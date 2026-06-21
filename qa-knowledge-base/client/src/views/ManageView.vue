<template>
  <div class="manage-view">
    <div class="page-header">
      <h2>⚙️ 管理问答</h2>
      <el-button type="primary" @click="showCreateDialog">
        <el-icon><Plus /></el-icon>
        新增问答
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="toolbar">
      <el-input
        v-model="keyword"
        placeholder="搜索问答..."
        clearable
        @clear="fetchData"
        @keyup.enter="fetchData"
        style="width: 300px;"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-select
        v-model="filterCategory"
        placeholder="按分类筛选"
        clearable
        @change="fetchData"
        style="width: 160px;"
      >
        <el-option
          v-for="cat in categories"
          :key="cat.id"
          :label="`${cat.name} (${cat.count})`"
          :value="cat.id"
        />
      </el-select>
    </div>

    <!-- 列表 -->
    <el-table
      :data="list"
      v-loading="loading"
      stripe
      style="width: 100%; margin-top: 16px;"
    >
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="question" label="问题" min-width="200" show-overflow-tooltip />
      <el-table-column prop="category_name" label="分类" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.category_name" size="small">{{ row.category_name }}</el-tag>
          <span v-else style="color:#c0c4cc;">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="source_file" label="来源" width="120" show-overflow-tooltip />
      <el-table-column prop="updated_at" label="更新时间" width="170">
        <template #default="{ row }">
          {{ formatTime(row.updated_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" link @click="showEditDialog(row)">
            <el-icon><Edit /></el-icon>
          </el-button>
          <el-button size="small" type="primary" link @click="goDetail(row.id)">
            <el-icon><View /></el-icon>
          </el-button>
          <el-popconfirm
            title="确定删除这条问答吗？"
            @confirm="handleDelete(row.id)"
          >
            <template #reference>
              <el-button size="small" type="danger" link>
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

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

    <!-- 新增/编辑对话框 -->
    <QAForm
      v-model:visible="dialogVisible"
      :editing-item="editingItem"
      :categories="categories"
      @saved="handleSaved"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'
import QAForm from '../components/QAForm.vue'

const router = useRouter()

const keyword = ref('')
const filterCategory = ref(null)
const list = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pagination = ref({ total: 0, limit: 20, page: 1, totalPages: 0 })
const categories = ref([])

const dialogVisible = ref(false)
const editingItem = ref(null)

onMounted(() => {
  fetchData()
  fetchCategories()
})

async function fetchData() {
  loading.value = true
  try {
    const res = await api.getQAList({
      search: keyword.value,
      category: filterCategory.value,
      page: currentPage.value,
      limit: 20
    })
    list.value = res.data.list
    pagination.value = res.data.pagination
  } catch (e) { /* */ } finally {
    loading.value = false
  }
}

async function fetchCategories() {
  try {
    const res = await api.getCategories()
    categories.value = res.data
  } catch (e) { /* */ }
}

function handlePageChange(page) {
  currentPage.value = page
  fetchData()
}

function showCreateDialog() {
  editingItem.value = null
  dialogVisible.value = true
}

function showEditDialog(row) {
  editingItem.value = { ...row }
  dialogVisible.value = true
}

async function handleDelete(id) {
  try {
    await api.deleteQA(id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (e) { /* */ }
}

function handleSaved() {
  dialogVisible.value = false
  fetchData()
  fetchCategories()
}

function goDetail(id) {
  router.push(`/qa/${id}`)
}

function formatTime(t) {
  if (!t) return ''
  return new Date(t).toLocaleString('zh-CN')
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
