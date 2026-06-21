<template>
  <div class="detail-view" v-loading="loading">
    <template v-if="item">
      <el-page-header @back="goBack" :content="item.question">
        <template #title>
          <span style="color: #409eff; cursor: pointer;">← 返回首页</span>
        </template>
      </el-page-header>

      <el-card class="detail-card">
        <!-- 分类和标签 -->
        <div class="meta-row">
          <el-tag v-if="item.category_name" type="success" size="large">
            {{ item.category_name }}
          </el-tag>
          <el-tag
            v-for="tag in item.tags"
            :key="tag"
            size="large"
            class="tag-item"
          >
            {{ tag }}
          </el-tag>
          <span class="source" v-if="item.source_file">
            来源: {{ item.source_file }}
          </span>
        </div>

        <!-- 问题 -->
        <h1 class="question">{{ item.question }}</h1>

        <!-- 答案 -->
        <el-divider />
        <div class="answer-content" v-html="renderedAnswer"></div>

        <!-- 时间 -->
        <el-divider />
        <div class="time-info">
          <span>创建于: {{ formatTime(item.created_at) }}</span>
          <span v-if="item.updated_at !== item.created_at">
            更新于: {{ formatTime(item.updated_at) }}
          </span>
        </div>
      </el-card>
    </template>

    <div v-else-if="!loading" class="empty-state">
      <div class="icon">📄</div>
      <p>未找到该问答</p>
      <el-button type="primary" @click="goBack">返回首页</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'

const route = useRoute()
const router = useRouter()

const item = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await api.getQADetail(route.params.id)
    item.value = res.data
  } catch (e) {
    item.value = null
  } finally {
    loading.value = false
  }
})

// 简单 Markdown 渲染（将 **bold** 和换行转为 HTML）
const renderedAnswer = computed(() => {
  if (!item.value) return ''
  let html = item.value.answer
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
  return html
})

function formatTime(t) {
  if (!t) return ''
  return new Date(t).toLocaleString('zh-CN')
}

function goBack() {
  router.push('/')
}
</script>

<style scoped>
.detail-card {
  margin-top: 20px;
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.tag-item {
  margin-left: 0 !important;
}

.source {
  color: #909399;
  font-size: 13px;
  margin-left: auto;
}

.question {
  font-size: 22px;
  color: #303133;
  line-height: 1.6;
}

.time-info {
  display: flex;
  gap: 20px;
  color: #909399;
  font-size: 13px;
}
</style>
