<template>
  <div class="search-bar">
    <el-autocomplete
      ref="autocompleteRef"
      v-model="localKeyword"
      :fetch-suggestions="fetchSuggestions"
      :trigger-on-focus="false"
      :highlight-first-item="true"
      placeholder="输入关键词搜索问答..."
      clearable
      size="large"
      class="search-input"
      @clear="handleClear"
      @keyup.enter="handleSearch"
      @select="handleSelect"
    >
      <template #prefix>
        <el-icon><Search /></el-icon>
      </template>
      <template #append>
        <el-button type="primary" @click="handleSearch" :icon="Search">
          搜索
        </el-button>
      </template>
    </el-autocomplete>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import api from '../api'

const props = defineProps({
  modelValue: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue', 'search'])

const localKeyword = ref(props.modelValue)
const autocompleteRef = ref(null)
let debounceTimer = null

// 同步 v-model
watch(() => props.modelValue, (val) => {
  localKeyword.value = val
})

watch(localKeyword, (val) => {
  emit('update:modelValue', val)
})

// 搜索建议（带防抖）
function fetchSuggestions(queryString, cb) {
  if (!queryString || queryString.trim().length < 1) {
    cb([])
    return
  }
  // 防抖 250ms
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(async () => {
    try {
      const res = await api.suggest(queryString)
      const suggestions = (res.data || []).map(q => ({ value: q }))
      cb(suggestions)
    } catch {
      cb([])
    }
  }, 250)
}

function handleSearch() {
  if (autocompleteRef.value) {
    autocompleteRef.value.close()
  }
  emit('search', localKeyword.value)
}

function handleSelect(item) {
  localKeyword.value = item.value
  emit('search', item.value)
}

function handleClear() {
  emit('search', '')
}
</script>

<style scoped>
.search-bar {
  max-width: 640px;
  margin: 0 auto 20px;
}

.search-input {
  width: 100%;
}
</style>
