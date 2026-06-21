<template>
  <div class="upload-wrapper">
    <!-- 拖拽上传区 -->
    <el-upload
      ref="uploadRef"
      class="upload-area"
      drag
      multiple
      :auto-upload="false"
      :show-file-list="false"
      :on-change="handleFileChange"
      :accept="'.md,.markdown,.json'"
    >
      <div class="upload-content">
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <div class="upload-text">
          <p class="upload-title">将文件拖到此处，或<em>点击选择</em></p>
          <p class="upload-hint">支持 .md、.markdown、.json 格式，单文件不超过 10MB，一次最多 50 个文件</p>
        </div>
      </div>
    </el-upload>

    <!-- 文件列表 -->
    <div v-if="fileList.length > 0" class="file-list">
      <div class="file-list-header">
        <span>已选择 <strong>{{ fileList.length }}</strong> 个文件</span>
        <el-button type="danger" size="small" link @click="clearAll">清空</el-button>
      </div>
      <div class="file-items">
        <div v-for="(f, i) in fileList" :key="i" class="file-item">
          <div class="file-info">
            <el-icon :size="18" color="#409eff"><Document /></el-icon>
            <span class="file-name">{{ f.name }}</span>
            <span class="file-size">{{ formatSize(f.size) }}</span>
          </div>
          <!-- 导入状态标记 -->
          <el-tag v-if="f.status === 'success'" type="success" size="small">
            {{ f.imported }} 条
          </el-tag>
          <el-tag v-else-if="f.status === 'error'" type="danger" size="small">失败</el-tag>
          <el-tag v-else-if="f.status === 'importing'" type="warning" size="small">导入中...</el-tag>
          <el-button
            v-else
            size="small"
            type="danger"
            :icon="Delete"
            circle
            @click="removeFile(i)"
          />
        </div>
      </div>

      <!-- 导入按钮 + 进度 -->
      <div class="import-actions">
        <el-button
          type="primary"
          size="large"
          :loading="loading"
          :disabled="fileList.length === 0"
          @click="handleBatchImport"
          style="width: 200px;"
        >
          <el-icon><Upload /></el-icon>
          {{ loading ? `导入中 (${progress.current}/${progress.total})` : `批量导入 (${fileList.length} 个文件)` }}
        </el-button>
      </div>
    </div>

    <!-- 进度条 -->
    <el-progress
      v-if="loading && fileList.length > 0"
      :percentage="Math.round((progress.current / progress.total) * 100)"
      :status="progress.status"
      style="margin-top: 12px;"
    />
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Delete, Document } from '@element-plus/icons-vue'
import api from '../api'

const props = defineProps({
  loading: { type: Boolean, default: false }
})

const emit = defineEmits(['import', 'batchResult'])

const uploadRef = ref(null)
const fileList = ref([])
const progress = reactive({ current: 0, total: 0, status: '' })

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(1) + ' MB'
}

function handleFileChange(file) {
  const raw = file.raw
  // 去重
  if (fileList.value.some(f => f.name === raw.name && f.size === raw.size)) {
    ElMessage.warning(`文件 "${raw.name}" 已存在`)
    return
  }
  fileList.value.push({
    name: raw.name,
    size: raw.size,
    raw,
    status: 'pending'
  })
}

function removeFile(index) {
  fileList.value.splice(index, 1)
}

function clearAll() {
  fileList.value = []
  progress.current = 0
  progress.total = 0
  progress.status = ''
}

async function handleBatchImport() {
  if (fileList.value.length === 0) return

  const files = fileList.value.map(f => f.raw)
  progress.total = files.length
  progress.current = 0
  progress.status = ''

  // 标记所有文件为 pending
  fileList.value.forEach(f => { f.status = 'pending' })

  // 使用批量 API 一次发送所有文件
  try {
    const res = await api.importBatch(files)

    // 根据返回结果更新每个文件的状态
    for (const r of res.data.results) {
      const found = fileList.value.find(f => f.name === r.file)
      if (found) {
        if (r.error) {
          found.status = 'error'
        } else {
          found.status = 'success'
          found.imported = r.imported
        }
      }
      progress.current++
    }

    progress.status = res.data.totalErrors > 0 ? 'warning' : 'success'

    // 汇总通知
    const successFiles = res.data.results.filter(r => !r.error).length
    const failFiles = res.data.results.filter(r => r.error).length

    if (failFiles > 0) {
      ElMessage.warning(`导入完成：${res.data.totalImported} 条成功，${failFiles} 个文件失败`)
    } else {
      ElMessage.success(`批量导入完成！共导入 ${res.data.totalImported} 条问答`)
    }

    emit('batchResult', res.data)
  } catch (e) {
    progress.status = 'exception'
    fileList.value.forEach(f => {
      if (f.status === 'pending') f.status = 'error'
    })
  }
}
</script>

<style scoped>
.upload-wrapper {
  width: 100%;
}

.upload-area {
  width: 100%;
}

.upload-content {
  padding: 20px;
}

.upload-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 12px;
}

.upload-title {
  font-size: 16px;
  color: #606266;
  margin-bottom: 8px;
}
.upload-title em {
  color: #409eff;
  font-style: normal;
}

.upload-hint {
  font-size: 13px;
  color: #c0c4cc;
}

/* 文件列表 */
.file-list {
  margin-top: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #fff;
  overflow: hidden;
}

.file-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: #fafafa;
  border-bottom: 1px solid #ebeef5;
  font-size: 14px;
}

.file-items {
  max-height: 260px;
  overflow-y: auto;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  border-bottom: 1px solid #f2f3f5;
  transition: background 0.2s;
}
.file-item:last-child {
  border-bottom: none;
}
.file-item:hover {
  background: #fafafa;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.file-name {
  font-size: 14px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: 12px;
  color: #c0c4cc;
  white-space: nowrap;
}

.import-actions {
  display: flex;
  justify-content: center;
  padding: 14px 16px;
  border-top: 1px solid #ebeef5;
}
</style>
