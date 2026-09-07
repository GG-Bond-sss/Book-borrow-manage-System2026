/**
 * stores/category.ts — 分类缓存（供下拉选择与筛选使用）
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as catApi from '@/api/category'
import type { Category } from '@/types'

export const useCategoryStore = defineStore('category', () => {
  const list = ref<Category[]>([])
  const loaded = ref(false)

  async function load(force = false) {
    if (loaded.value && !force) return
    list.value = await catApi.allCategories()
    loaded.value = true
  }

  function nameOf(id?: number | null): string {
    if (!id) return '未分类'
    return list.value.find(c => c.id === id)?.name ?? '未分类'
  }

  return { list, loaded, load, nameOf }
})
