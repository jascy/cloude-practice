<template>
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑问答' : '新增问答'"
    width="640px"
    :close-on-click-modal="false"
    @close="resetForm"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="80px"
      label-position="top"
    >
      <el-form-item label="问题" prop="question">
        <el-input
          v-model="form.question"
          placeholder="请输入问题"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="答案" prop="answer">
        <el-input
          v-model="form.answer"
          type="textarea"
          :rows="8"
          placeholder="请输入答案（支持 Markdown 格式）"
          maxlength="10000"
          show-word-limit
        />
      </el-form-item>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="分类">
            <el-select
              v-model="form.category_id"
              placeholder="选择分类"
              clearable
              style="width: 100%"
            >
              <el-option
                v-for="cat in categories"
                :key="cat.id"
                :label="cat.name"
                :value="cat.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="标签">
            <el-select
              v-model="form.tags"
              multiple
              filterable
              allow-create
              default-first-option
              placeholder="输入标签后回车添加"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="handleSubmit">
        {{ isEdit ? '保存修改' : '立即创建' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const props = defineProps({
  visible: { type: Boolean, default: false },
  editingItem: { type: Object, default: null },
  categories: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:visible', 'saved'])

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const isEdit = computed(() => !!props.editingItem)

const formRef = ref(null)
const saving = ref(false)

const form = ref({
  question: '',
  answer: '',
  category_id: null,
  tags: []
})

const rules = {
  question: [{ required: true, message: '请输入问题', trigger: 'blur' }],
  answer: [{ required: true, message: '请输入答案', trigger: 'blur' }]
}

// 编辑时回填数据
watch(() => props.editingItem, (item) => {
  if (item) {
    form.value = {
      question: item.question || '',
      answer: item.answer || '',
      category_id: item.category_id || null,
      tags: Array.isArray(item.tags) ? [...item.tags] : []
    }
  } else {
    resetForm()
  }
})

function resetForm() {
  form.value = { question: '', answer: '', category_id: null, tags: [] }
  formRef.value?.resetFields()
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    if (isEdit.value) {
      await api.updateQA(props.editingItem.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await api.createQA(form.value)
      ElMessage.success('创建成功')
    }
    emit('saved')
  } catch (e) { /* */ } finally {
    saving.value = false
  }
}
</script>
