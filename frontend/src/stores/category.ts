/**
 * stores/category.ts — 分类缓存（供下拉选择与筛选使用）
 * 增删改操作后会主动 refresh，确保所有引用此 store 的下拉框/筛选器同步更新。
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as catApi from '@/api/category'
import type { Category } from '@/types'

export const useCategoryStore = defineStore('category', () => {
  const list = ref<Category[]>([])
  const loaded = ref(false)

  /** 加载分类列表（默认带缓存，force=true 强制刷新） */
  async function load(force = false) {
    if (loaded.value && !force) return
    list.value = await catApi.allCategories()
    loaded.value = true
  }

  /** 新增分类后同步到本地列表（避免重新请求） */
  function addLocal(cat: Category) {
    const idx = list.value.findIndex(c => c.id === cat.id)
    if (idx < 0) list.value.push(cat)
    else list.value[idx] = cat
  }

  /** 修改分类后同步到本地列表 */
  function updateLocal(cat: Category) {
    const idx = list.value.findIndex(c => c.id === cat.id)
    if (idx >= 0) list.value[idx] = cat
  }

  /** 删除分类后从本地列表移除 */
  function removeLocal(id: number) {
    list.value = list.value.filter(c => c.id !== id)
  }

  /** 新增分类（调用 API + 本地同步） */
  async function create(name: string): Promise<Category> {
    const cat = await catApi.createCategory(name)
    addLocal(cat)
    return cat
  }

  /** 修改分类（调用 API + 本地同步） */
  async function update(id: number, name: string): Promise<Category> {
    const cat = await catApi.updateCategory(id, name)
    updateLocal(cat)
    return cat
  }

  /** 删除分类（调用 API + 本地同步） */
  async function remove(id: number): Promise<void> {
    await catApi.deleteCategory(id)
    removeLocal(id)
  }

  /** 强制重新拉取最新分类列表（兜底策略） */
  async function refresh() {
    list.value = await catApi.allCategories()
    loaded.value = true
  }

  function nameOf(id?: number | null): string {
    if (!id) return '未分类'
    return list.value.find(c => c.id === id)?.name ?? '未分类'
  }

  /** 重置（退出登录时） */
  function reset() {
    list.value = []
    loaded.value = false
  }

  return {
    list, loaded,
    load, refresh, create, update, remove,
    addLocal, updateLocal, removeLocal, nameOf, reset
  }
})
