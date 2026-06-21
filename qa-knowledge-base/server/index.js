const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { initDB } = require('./db');

const app = express();
const PORT = process.env.PORT || 3000;

// 中间件
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 配置文件上传
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, uploadsDir),
  filename: (req, file, cb) => {
    // 保留中文文件名（multer 默认不处理中文，需要手动 decode）
    const uniqueName = Date.now() + '-' + Math.round(Math.random() * 1E9) + path.extname(file.originalname);
    cb(null, uniqueName);
  }
});

const upload = multer({
  storage,
  fileFilter: (req, file, cb) => {
    const ext = path.extname(file.originalname).toLowerCase();
    if (['.md', '.markdown', '.json'].includes(ext)) {
      cb(null, true);
    } else {
      cb(new Error('仅支持 .md、.markdown 和 .json 格式的文件'));
    }
  },
  limits: { fileSize: 10 * 1024 * 1024 }
});

const qaController = require('./controllers/qaController');

// 单文件导入
app.post('/api/import', upload.single('file'), qaController.importFile);

// 批量多文件导入
app.post('/api/import/batch', upload.array('files', 50), qaController.importBatch);

// 其他路由
const qaRoutes = require('./routes/qa');
app.use('/api', qaRoutes);

// 健康检查
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// 全局错误处理
app.use((err, req, res, next) => {
  if (err instanceof multer.MulterError) {
    if (err.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({ success: false, message: '文件大小不能超过 10MB' });
    }
    if (err.code === 'LIMIT_FILE_COUNT') {
      return res.status(400).json({ success: false, message: '单次最多上传 50 个文件' });
    }
    return res.status(400).json({ success: false, message: err.message });
  }
  console.error('服务器错误:', err);
  res.status(500).json({ success: false, message: err.message || '服务器内部错误' });
});

// 初始化数据库后启动服务
async function start() {
  try {
    await initDB();
    app.listen(PORT, () => {
      console.log(`问答知识库后端服务启动成功: http://localhost:${PORT}`);
      console.log(`API 地址: http://localhost:${PORT}/api`);
    });
  } catch (err) {
    console.error('启动失败:', err);
    process.exit(1);
  }
}

start();
