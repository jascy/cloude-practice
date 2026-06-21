<template>
  <div class="home-view">
    <div class="page-header">
      <h2>探索知识</h2>
      <p class="subtitle">搜索或浏览分类，发现你需要的答案</p>
    </div>

    <!-- 搜索栏 -->
    <SearchBar v-model="keyword" @search="handleSearch" />

    <!-- 分类导航 -->
    <CategoryNav
      :categories="categories"
      :active="activeCategory"
      @select="handleCategoryChange"
    />

    <!-- 问答列表 -->
    <el-row :gutter="16" v-loading="loading">
      <el-col
        v-for="item in list"
        :key="item.id"
        :xs="24"
        :sm="12"
        :md="8"
        :lg="6"
      >
        <QACard :item="item" :keyword="keyword" @click="goDetail(item.id)" />
      </el-col>
    </el-row>

    <!-- 空状态 -->
    <div v-if="!loading && list.length === 0" class="empty-state">
      <div class="icon">🔍</div>
      <p>暂无内容，试试其他关键词或分类</p>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrap" v-if="pagination.totalPages > 1">
      <el-pagination
        background
        layout="prev, pager, next"
        :total="pagination.total"
        :page-size="pagination.limit"
        v-model:current-page="currentPage"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import SearchBar from '../components/SearchBar.vue'
import CategoryNav from '../components/CategoryNav.vue'
import QACard from '../components/QACard.vue'

const router = useRouter()

const keyword = ref('')
const activeCategory = ref(null)
const list = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pagination = ref({ total: 0, limit: 20, page: 1, totalPages: 0 })
const categories = ref([])

onMounted(() => {
  fetchData()
  fetchCategories()
})

async function fetchData() {
  loading.value = true
  try {
    const res = await api.getQAList({
      search: keyword.value,
      category: activeCategory.value,
      page: currentPage.value,
      limit: 20
    })
    list.value = res.data.list
    pagination.value = res.data.pagination
  } catch (e) {
    // 错误已在拦截器中处理
  } finally {
    loading.value = false
  }
}

async function fetchCategories() {
  try {
    const res = await api.getCategories()
    categories.value = res.data
  } catch (e) { /* */ }
}

function handleSearch() {
  currentPage.value = 1
  fetchData()
}

function handleCategoryChange(catId) {
  activeCategory.value = catId
  currentPage.value = 1
  fetchData()
}

function handlePageChange(page) {
  currentPage.value = page
  fetchData()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goDetail(id) {
  router.push(`/qa/${id}`)
}
</script>

<style scoped>
.subtitle {
  color: #909399;
  margin-top: 4px;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}
</style>
