<template>
  <el-card class="qa-card" shadow="hover" @click="$emit('click')">
    <div class="card-body">
      <!-- 匹配度和类别 -->
      <div class="card-top">
        <div class="card-category" v-if="item.category_name">
          <el-tag size="small" type="success">{{ item.category_name }}</el-tag>
        </div>
        <div class="card-score" v-if="item._score > 0">
          <el-tag size="small" type="warning" effect="plain">
            匹配度 {{ Math.round((item._matchedTokens / item._totalTokens) * 100) }}%
          </el-tag>
        </div>
      </div>

      <!-- 问题（高亮关键词） -->
      <h3 class="card-question" v-html="highlightText(item.question)"></h3>

      <!-- 答案摘要（高亮） -->
      <p class="card-answer" v-html="highlightText(item._snippet || truncateAnswer)"></p>

      <!-- 底部信息 -->
      <div class="card-footer">
        <div class="card-tags" v-if="item.tags && item.tags.length > 0">
          <el-tag
            v-for="tag in item.tags.slice(0, 3)"
            :key="tag"
            size="small"
            type="info"
            class="mini-tag"
          >
            {{ tag }}
          </el-tag>
          <span v-if="item.tags.length > 3" class="more-tag">+{{ item.tags.length - 3 }}</span>
        </div>
        <span class="card-time">{{ formatTime(item.updated_at) }}</span>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  item: { type: Object, required: true },
  keyword: { type: String, default: '' }
})

defineEmits(['click'])

const truncateAnswer = computed(() => {
  const text = props.item.answer || ''
  if (text.length > 120) {
    return text.slice(0, 120) + '...'
  }
  return text
})

// 高亮搜索关键词
function highlightText(text) {
  if (!text) return ''
  let result = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

  if (props.keyword && props.keyword.trim()) {
    // 拆分关键词为独立的匹配词
    const terms = getSearchTerms(props.keyword)
    // 按长度降序排列，避免短词覆盖长词的高亮
    const sorted = [...terms].sort((a, b) => b.length - a.length)

    for (const term of sorted) {
      if (term.length === 0) continue
      const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
      const regex = new RegExp(`(${escaped})`, 'gi')
      result = result.replace(regex, '<mark class="highlight">$1</mark>')
    }
  }

  return result
}

// 从搜索词中提取有意义的分词
function getSearchTerms(keyword) {
  const terms = new Set()
  const k = keyword.trim().toLowerCase()

  // 英文单词
  const enWords = k.match(/[a-z0-9]+/g) || []
  enWords.forEach(w => { if (w.length >= 1) terms.add(w) })

  // 中文字符
  const zhChars = k.match(/[一-鿿]+/g) || []
  zhChars.forEach(seg => {
    // 双字
    for (let i = 0; i < seg.length - 1; i++) terms.add(seg[i] + seg[i + 1])
    // 单字
    for (let i = 0; i < seg.length; i++) terms.add(seg[i])
    // 完整
    terms.add(seg)
  })

  // 原始整体
  terms.add(k)

  return terms
}

function formatTime(t) {
  if (!t) return ''
  return new Date(t).toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.qa-card {
  cursor: pointer;
  margin-bottom: 16px;
  height: 100%;
}

.card-body {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.card-question {
  font-size: 16px;
  color: #303133;
  line-height: 1.5;
  margin-bottom: 10px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-answer {
  font-size: 14px;
  color: #909399;
  line-height: 1.6;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.card-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.mini-tag {
  font-size: 11px;
}

.more-tag {
  font-size: 12px;
  color: #909399;
}

.card-time {
  font-size: 12px;
  color: #c0c4cc;
  white-space: nowrap;
}

/* 关键词高亮 */
:deep(.highlight) {
  background: #fff3cd;
  color: #e6a23c;
  padding: 1px 2px;
  border-radius: 2px;
  font-weight: 600;
}
</style>
