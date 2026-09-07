<template>
  <div class="book-cover" :style="{ width: width + 'px', height: height + 'px' }">
    <img
      v-if="coverUrl && !loadError"
      :src="coverUrl"
      :alt="title"
      class="cover-img"
      @error="loadError = true"
    />
    <div
      v-else
      class="default-cover"
      :style="{ background: bgColor }"
    >
      {{ firstChar }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

const props = withDefaults(defineProps<{
  coverUrl?: string
  title: string
  width?: number
  height?: number
}>(), {
  coverUrl: '',
  width: 60,
  height: 80
})

const loadError = ref(false)
watch(() => props.coverUrl, () => { loadError.value = false })

const firstChar = computed(() => props.title?.trim()?.charAt(0) || '书')
const bgColor = computed(() => {
  // 根据书名 hash 取稳定颜色
  const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#fc8452', '#9a60b4']
  let sum = 0
  for (const ch of props.title || '书') sum += ch.charCodeAt(0)
  return colors[sum % colors.length]
})
</script>

<style scoped>
.book-cover { border-radius: 4px; overflow: hidden; flex-shrink: 0; background: #f5f5f5; }
.cover-img { width: 100%; height: 100%; object-fit: cover; display: block; }
.default-cover { width: 100%; height: 100%; }
</style>
