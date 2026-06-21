import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({
  baseURL: '/api',
  timeout: 60000
})

// 响应拦截器
http.interceptors.response.use(
  res => res.data,
  err => {
    const msg = err.response?.data?.message || err.message || '请求失败'
    ElMessage.error(msg)
    return Promise.reject(err)
  }
)

// API 方法
const api = {
  // 问答
  getQAList(params) {
    return http.get('/qa', { params })
  },
  getQADetail(id) {
    return http.get(`/qa/${id}`)
  },
  createQA(data) {
    return http.post('/qa', data)
  },
  updateQA(id, data) {
    return http.put(`/qa/${id}`, data)
  },
  deleteQA(id) {
    return http.delete(`/qa/${id}`)
  },

  // 搜索
  search(keyword) {
    return http.get('/search', { params: { q: keyword } })
  },

  // 搜索建议
  suggest(keyword) {
    return http.get('/suggest', { params: { q: keyword } })
  },

  // 分类
  getCategories() {
    return http.get('/categories')
  },

  // 单文件导入
  importFile(file) {
    const formData = new FormData()
    formData.append('file', file)
    return http.post('/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 批量导入
  importBatch(files) {
    const formData = new FormData()
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i])
    }
    return http.post('/import/batch', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

export default api
