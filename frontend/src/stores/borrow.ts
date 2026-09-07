/**
 * stores/borrow.ts — 当前用户的借阅状态（集中管理，跨页同步）
 * 跟踪当前用户所有「借阅中/逾期」的图书 ID，用于在图书浏览/详情页
 * 实时反映借阅按钮的"已借阅"置灰状态。
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { borrowApi } from '@/api'
import type { BorrowStatus } from '@/types'

export const useBorrowStore = defineStore('borrow', () => {
  /** 当前用户处于「借阅中/逾期」状态的图书 ID 集合（按 book_id 去重） */
  const borrowedBookIds = ref<Set<number>>(new Set())
  /** 当前用户处于「逾期」状态的图书 ID 集合 */
  const overdueBookIds = ref<Set<number>>(new Set())
  const loaded = ref(false)

  /** 是否已借阅某书（借阅中/逾期） */
  function isBorrowed(bookId: number): boolean {
    return borrowedBookIds.value.has(bookId)
  }
  /** 是否逾期（用于禁用所有借阅） */
  function hasOverdue(): boolean {
    return overdueBookIds.value.size > 0
  }

  /** 从后端拉取本人借阅记录，刷新本地缓存 */
  async function load(force = false) {
    if (loaded.value && !force) return
    const res = await borrowApi.listMyRecords({ page: 1, page_size: 1000 })
    const borrowed = new Set<number>()
    const overdue = new Set<number>()
    for (const r of res.list) {
      if (r.status === 'returned') continue
      borrowed.add(r.book_id)
      if (r.status === 'overdue') overdue.add(r.book_id)
    }
    borrowedBookIds.value = borrowed
    overdueBookIds.value = overdue
    loaded.value = true
  }

  /** 借阅成功后本地立即更新状态（无需等待重新拉取） */
  function markBorrowed(bookId: number) {
    borrowedBookIds.value.add(bookId)
    // 触发响应式：Set 需重新赋值
    borrowedBookIds.value = new Set(borrowedBookIds.value)
  }

  /** 归还成功后本地立即更新状态 */
  function markReturned(bookId: number) {
    borrowedBookIds.value.delete(bookId)
    overdueBookIds.value.delete(bookId)
    borrowedBookIds.value = new Set(borrowedBookIds.value)
    overdueBookIds.value = new Set(overdueBookIds.value)
  }

  /** 重置（退出登录时） */
  function reset() {
    borrowedBookIds.value = new Set()
    overdueBookIds.value = new Set()
    loaded.value = false
  }

  return {
    borrowedBookIds, overdueBookIds, loaded,
    isBorrowed, hasOverdue, load, markBorrowed, markReturned, reset
  }
})
