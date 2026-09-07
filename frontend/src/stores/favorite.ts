/**
 * stores/favorite.ts — 当前用户的收藏状态（集中管理，跨页同步）
 * 跟踪当前用户所有已收藏的图书 ID，用于在图书浏览/详情/我的收藏页
 * 实时反映收藏按钮的高亮切换状态。
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { favoriteApi } from '@/api'

export const useFavoriteStore = defineStore('favorite', () => {
  /** 当前用户已收藏的图书 ID 集合 */
  const favoriteBookIds = ref<Set<number>>(new Set())
  const loaded = ref(false)

  /** 是否已收藏 */
  function isFavorited(bookId: number): boolean {
    return favoriteBookIds.value.has(bookId)
  }

  /** 从后端拉取本人收藏列表，刷新本地缓存 */
  async function load(force = false) {
    if (loaded.value && !force) return
    const res = await favoriteApi.listMyFavorites({ page: 1, page_size: 1000 })
    const favs = new Set<number>()
    for (const b of res.list) favs.add(b.id)
    favoriteBookIds.value = favs
    loaded.value = true
  }

  /** 切换收藏状态（调用 API 后同步本地） */
  async function toggle(bookId: number): Promise<boolean> {
    const res = await favoriteApi.toggleFavorite(bookId)
    const set = new Set(favoriteBookIds.value)
    if (res.favorited) set.add(bookId)
    else set.delete(bookId)
    favoriteBookIds.value = set
    return res.favorited
  }

  /** 直接设置某书收藏状态（详情页单独查询后同步） */
  function setFavorited(bookId: number, favorited: boolean) {
    const set = new Set(favoriteBookIds.value)
    if (favorited) set.add(bookId)
    else set.delete(bookId)
    favoriteBookIds.value = set
  }

  /** 重置（退出登录时） */
  function reset() {
    favoriteBookIds.value = new Set()
    loaded.value = false
  }

  return {
    favoriteBookIds, loaded,
    isFavorited, load, toggle, setFavorited, reset
  }
})
