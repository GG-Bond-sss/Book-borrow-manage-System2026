/**
 * api/favorite.ts — 收藏接口（BR-13：同一读者同一图书仅一条，点击切换）
 */
import { db as _db, now, paginate } from '@/mock/db'
import { mockRequest, BizError, getCurrentUser } from './request'
import type { PageQuery, PageResult } from '@/types'
import type { Book } from '@/types'

/** 我的收藏列表 */
export function listMyFavorites(q: PageQuery): Promise<PageResult<Book & { favorite_time: string }>> {
  return mockRequest(() => {
    const cur = getCurrentUser()
    if (!cur) throw new BizError('未登录')
    const favs = _db.favs().filter(f => f.user_id === cur.id)
    const books = _db.books()
    const cats = _db.cats()
    let list = favs.map(f => {
      const b = books.find(b => b.id === f.book_id)
      if (!b) return null
      return {
        ...b,
        category_name: cats.find(c => c.id === b.category_id)?.name ?? '未分类',
        favorite_time: f.created_at
      }
    }).filter(Boolean) as (Book & { category_name: string; favorite_time: string })[]
    if (q.keyword) {
      const kw = q.keyword.trim().toLowerCase()
      list = list.filter(b => b.title.toLowerCase().includes(kw) || b.author.toLowerCase().includes(kw))
    }
    list.sort((a, b) => b.favorite_time.localeCompare(a.favorite_time))
    return paginate(list, q)
  })
}

/** 是否已收藏 */
export function isFavorited(bookId: number): Promise<boolean> {
  return mockRequest(() => {
    const cur = getCurrentUser()
    if (!cur) return false
    return _db.favs().some(f => f.user_id === cur.id && f.book_id === bookId)
  }, 60)
}

/** 切换收藏状态（BR-13） */
export function toggleFavorite(bookId: number): Promise<{ favorited: boolean }> {
  return mockRequest(() => {
    const cur = getCurrentUser()
    if (!cur) throw new BizError('未登录')
    if (cur.role !== 'reader') throw new BizError('仅读者可收藏')
    const favs = _db.favs()
    const idx = favs.findIndex(f => f.user_id === cur.id && f.book_id === bookId)
    if (idx >= 0) {
      favs.splice(idx, 1)
      _db.setFavs(favs)
      return { favorited: false }
    }
    const id = _db.nextId('favs')
    favs.push({ id, user_id: cur.id, book_id: bookId, created_at: now() })
    _db.setFavs(favs)
    return { favorited: true }
  })
}
