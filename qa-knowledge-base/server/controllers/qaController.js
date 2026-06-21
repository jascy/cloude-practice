const QAService = require('../services/qaService');
const ImportService = require('../services/importService');

class QAController {
  // GET /api/qa
  static list(req, res) {
    try {
      const { search, category, page, limit } = req.query;
      const result = QAService.getList({ search, category, page, limit });
      res.json({ success: true, data: result });
    } catch (err) {
      res.status(500).json({ success: false, message: err.message });
    }
  }

  // GET /api/qa/:id
  static detail(req, res) {
    try {
      const item = QAService.getById(req.params.id);
      if (!item) {
        return res.status(404).json({ success: false, message: '未找到该问答' });
      }
      res.json({ success: true, data: item });
    } catch (err) {
      res.status(500).json({ success: false, message: err.message });
    }
  }

  // POST /api/qa
  static create(req, res) {
    try {
      const { question, answer, category_id, tags } = req.body;
      if (!question || !answer) {
        return res.status(400).json({ success: false, message: '问题和答案不能为空' });
      }
      const item = QAService.create({ question, answer, category_id, tags });
      res.status(201).json({ success: true, data: item });
    } catch (err) {
      res.status(500).json({ success: false, message: err.message });
    }
  }

  // PUT /api/qa/:id
  static update(req, res) {
    try {
      const { question, answer, category_id, tags } = req.body;
      if (!question || !answer) {
        return res.status(400).json({ success: false, message: '问题和答案不能为空' });
      }
      const existing = QAService.getById(req.params.id);
      if (!existing) {
        return res.status(404).json({ success: false, message: '未找到该问答' });
      }
      const item = QAService.update(req.params.id, { question, answer, category_id, tags });
      res.json({ success: true, data: item });
    } catch (err) {
      res.status(500).json({ success: false, message: err.message });
    }
  }

  // DELETE /api/qa/:id
  static delete(req, res) {
    try {
      const existing = QAService.getById(req.params.id);
      if (!existing) {
        return res.status(404).json({ success: false, message: '未找到该问答' });
      }
      QAService.delete(req.params.id);
      res.json({ success: true, message: '删除成功' });
    } catch (err) {
      res.status(500).json({ success: false, message: err.message });
    }
  }

  // GET /api/search
  static search(req, res) {
    try {
      const { q } = req.query;
      if (!q) {
        return res.json({ success: true, data: [] });
      }
      const items = QAService.search(q);
      res.json({ success: true, data: items });
    } catch (err) {
      res.status(500).json({ success: false, message: err.message });
    }
  }

  // GET /api/suggest
  static suggest(req, res) {
    try {
      const { q } = req.query;
      const suggestions = QAService.suggest(q || '');
      res.json({ success: true, data: suggestions });
    } catch (err) {
      res.status(500).json({ success: false, message: err.message });
    }
  }

  // GET /api/categories
  static categories(req, res) {
    try {
      const list = QAService.getCategories();
      res.json({ success: true, data: list });
    } catch (err) {
      res.status(500).json({ success: false, message: err.message });
    }
  }

  // POST /api/import (单文件)
  static importFile(req, res) {
    try {
      if (!req.file) {
        return res.status(400).json({ success: false, message: '请选择要导入的文件' });
      }
      const result = ImportService.importFile(req.file.path, req.file.originalname);
      ImportService.cleanupFile(req.file.path);
      res.json({ success: true, data: result });
    } catch (err) {
      if (req.file) ImportService.cleanupFile(req.file.path);
      res.status(400).json({ success: false, message: err.message });
    }
  }

  // POST /api/import/batch (批量多文件)
  static importBatch(req, res) {
    try {
      if (!req.files || req.files.length === 0) {
        return res.status(400).json({ success: false, message: '请选择要导入的文件' });
      }

      const results = [];
      let totalImported = 0;
      let totalErrors = 0;

      for (const file of req.files) {
        try {
          const result = ImportService.importFile(file.path, file.originalname);
          ImportService.cleanupFile(file.path);
          results.push({
            file: file.originalname,
            ...result
          });
          totalImported += result.imported;
          totalErrors += (result.errors?.length || 0);
        } catch (err) {
          results.push({
            file: file.originalname,
            total: 0,
            imported: 0,
            error: err.message
          });
          totalErrors++;
        }
      }

      res.json({
        success: true,
        data: {
          files: req.files.length,
          totalImported,
          totalErrors,
          results
        }
      });
    } catch (err) {
      // 清理残留文件
      if (req.files) {
        req.files.forEach(f => ImportService.cleanupFile(f.path));
      }
      res.status(400).json({ success: false, message: err.message });
    }
  }
}

module.exports = QAController;
