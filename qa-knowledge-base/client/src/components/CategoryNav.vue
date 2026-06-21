<template>
  <div class="category-nav">
    <el-radio-group
      v-model="localActive"
      size="small"
      @change="handleSelect"
    >
      <el-radio-button :value="null">
        全部
      </el-radio-button>
      <el-radio-button
        v-for="cat in categories"
        :key="cat.id"
        :value="cat.id"
      >
        {{ cat.name }}
        <span class="cat-count">({{ cat.count }})</span>
      </el-radio-button>
    </el-radio-group>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  categories: { type: Array, default: () => [] },
  active: { default: null }
})

const emit = defineEmits(['select'])

const localActive = ref(props.active)

watch(() => props.active, (val) => {
  localActive.value = val
})

function handleSelect(val) {
  emit('select', val)
}
</script>

<style scoped>
.category-nav {
  text-align: center;
  margin-bottom: 24px;
}

.cat-count {
  font-size: 11px;
  opacity: 0.7;
}
</style>
