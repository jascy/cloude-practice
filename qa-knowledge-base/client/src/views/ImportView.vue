<template>
  <div class="import-view">
    <div class="page-header">
      <h2>📥 批量导入问答</h2>
      <p class="subtitle">一次上传多个 Markdown 或 JSON 文件，自动批量导入问答内容</p>
    </div>

    <!-- 上传区域 -->
    <ImportUpload @batchResult="handleBatchResult" />

    <!-- 批量导入结果 -->
    <el-card v-if="result" class="result-card">
      <template #header>
        <span>📊 批量导入结果</span>
      </template>

      <!-- 汇总统计 -->
      <div class="result-stats">
        <el-statistic title="处理文件" :value="result.files" />
        <el-statistic title="成功导入" :value="result.totalImported">
          <template #suffix>
            <el-icon v-if="result.totalImported > 0" style="color: #67c23a;">
              <SuccessFilled />
            </el-icon>
          </template>
        </el-statistic>
        <el-statistic
          v-if="result.totalErrors > 0"
          title="失败文件"
          :value="result.totalErrors"
        >
          <template #suffix>
            <el-icon style="color: #f56c6c;"><WarningFilled /></el-icon>
          </template>
        </el-statistic>
      </div>

      <!-- 每个文件详情 -->
      <el-divider />
      <h4 style="margin-bottom: 12px;">文件详情：</h4>
      <div class="result-detail" v-for="(r, i) in result.results" :key="i">
        <div class="detail-header">
          <el-icon :color="r.error ? '#f56c6c' : '#67c23a'">
            <SuccessFilled v-if="!r.error" />
            <WarningFilled v-else />
          </el-icon>
          <span class="detail-filename">{{ r.file }}</span>
          <el-tag v-if="r.error" type="danger" size="small">失败</el-tag>
          <el-tag v-else type="success" size="small">成功 {{ r.imported }}/{{ r.total }} 条</el-tag>
        </div>
        <p v-if="r.error" class="detail-error">{{ r.error }}</p>

        <!-- 单文件内的错误条目 -->
        <div v-if="r.errors && r.errors.length > 0" class="error-list">
          <div v-for="(err, j) in r.errors" :key="j" class="error-item">
            <p><strong>条目：</strong>{{ err.entry?.question || err.entry || '(无)' }}</p>
            <p><strong>原因：</strong>{{ err.error }}</p>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 格式说明 -->
    <el-card class="help-card">
      <template #header>
        <span>📋 支持的文件格式说明</span>
      </template>

      <el-tabs>
        <el-tab-pane label="Markdown 格式">
          <pre class="format-demo"># 分类名称（可选）

## 这是第一个问题？
这是第一个问题的答案。
可以有多行内容。

## 这是第二个问题？
这是第二个问题的答案。
支持 **加粗** 等 Markdown 格式。</pre>
          <ul class="tips">
            <li><code>#</code> 一级标题作为分类名（可选，放在最前面）</li>
            <li><code>##</code> 二级标题作为问题</li>
            <li>问题下方的段落作为答案内容</li>
          </ul>
        </el-tab-pane>
        <el-tab-pane label="JSON 格式">
          <pre class="format-demo">[
  {
    "question": "第一个问题？",
    "answer": "第一个问题的答案。",
    "category": "技术",
    "tags": ["前端", "Vue"]
  },
  {
    "question": "第二个问题？",
    "answer": "第二个问题的答案。",
    "category": "生活"
  }
]</pre>
          <ul class="tips">
            <li>必须是 JSON 数组格式</li>
            <li><code>question</code> 和 <code>answer</code> 为必填字段</li>
            <li><code>category</code> 和 <code>tags</code> 为可选字段</li>
          </ul>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ImportUpload from '../components/ImportUpload.vue'

const result = ref(null)

function handleBatchResult(data) {
  result.value = data
}
</script>

<style scoped>
.subtitle {
  color: #909399;
  margin-top: 4px;
}

.result-card {
  margin-top: 20px;
}

.result-stats {
  display: flex;
  gap: 40px;
  justify-content: center;
}

.result-detail {
  padding: 10px 0;
  border-bottom: 1px solid #f2f3f5;
}
.result-detail:last-child {
  border-bottom: none;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.detail-filename {
  font-weight: 500;
  color: #303133;
}

.detail-error {
  margin-top: 6px;
  color: #f56c6c;
  font-size: 13px;
  padding-left: 28px;
}

.error-list {
  margin-top: 10px;
  padding: 10px;
  margin-left: 28px;
  background: #fef0f0;
  border-radius: 6px;
}

.error-item {
  padding: 6px 0;
  border-bottom: 1px solid #fde2e2;
  font-size: 13px;
}
.error-item:last-child {
  border-bottom: none;
}

.help-card {
  margin-top: 20px;
}

.format-demo {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 6px;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
}

.tips {
  margin-top: 12px;
  padding-left: 20px;
  color: #606266;
  font-size: 14px;
}
.tips li {
  margin: 6px 0;
}
.tips code {
  background: #f0f2f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 13px;
}
</style>
