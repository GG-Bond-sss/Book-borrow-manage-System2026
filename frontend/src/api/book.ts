/**
 * api/book.ts — 图书管理接口
 */
import { db as _db, now, paginate } from '@/mock/db'
import { mockRequest, BizError } from './request'
import type { Book, PageQuery, PageResult } from '@/types'

/** 图书列表（带分类名称、搜索筛选、分页） */
export function listBooks(q: PageQuery): Promise<PageResult<Book & { category_name: string }>> {
  return mockRequest(() => {
    const cats = _db.cats()
    let books = _db.books()
    if (q.keyword) {
      const kw = q.keyword.trim().toLowerCase()
      books = books.filter(b =>
        b.title.toLowerCase().includes(kw) ||
        b.author.toLowerCase().includes(kw) ||
        b.isbn.toLowerCase().includes(kw)
      )
    }
    if (q.category_id) {
      books = books.filter(b => b.category_id === q.category_id)
    }
    const list = books.map(b => ({
      ...b,
      category_name: cats.find(c => c.id === b.category_id)?.name ?? '未分类'
    }))
    return paginate(list, q)
  })
}

/** 图书详情 */
export function getBook(id: number) {
  return mockRequest(() => {
    const cats = _db.cats()
    const book = _db.books().find(b => b.id === id)
    if (!book) throw new BizError('图书不存在')
    return {
      ...book,
      category_name: cats.find(c => c.id === book.category_id)?.name ?? '未分类'
    }
  })
}

/** 图书表单载荷（分类、出版年份允许为 null，提交时校验） */
export type BookPayload = Omit<Partial<Book>, 'category_id'> & { category_id: number | null }

/** 新增图书 */
export function createBook(payload: BookPayload) {
  return mockRequest(() => {
    const books = _db.books()
    if (!payload.title?.trim()) throw new BizError('书名不能为空')
    if (!payload.author?.trim()) throw new BizError('作者不能为空')
    if (!payload.isbn?.trim()) throw new BizError('ISBN不能为空')
    if (books.some(b => b.isbn === payload.isbn)) throw new BizError('ISBN已存在，不可重复添加')
    if (!payload.category_id) throw new BizError('请选择分类')
    const total = Number(payload.total_count)
    if (!total || total < 1) throw new BizError('总馆藏数量必须≥1')
    const id = _db.nextId('books')
    const t = now()
    const book: Book = {
      id,
      title: payload.title.trim(),
      author: payload.author.trim(),
      isbn: payload.isbn.trim(),
      category_id: payload.category_id,
      publisher: payload.publisher?.trim() ?? '',
      publish_year: payload.publish_year ?? null,
      total_count: total,
      available_count: total, // 新增时可借数量=总馆藏数
      summary: payload.summary?.trim() ?? '',
      cover_url: payload.cover_url ?? '',
      created_at: t,
      updated_at: t
    }
    books.push(book)
    _db.setBooks(books)
    return book
  })
}

/** 编辑图书 */
export function updateBook(id: number, payload: BookPayload) {
  return mockRequest(() => {
    const books = _db.books()
    const idx = books.findIndex(b => b.id === id)
    if (idx < 0) throw new BizError('图书不存在')
    const cur = books[idx]
    if (!payload.title?.trim()) throw new BizError('书名不能为空')
    if (!payload.author?.trim()) throw new BizError('作者不能为空')
    if (!payload.isbn?.trim()) throw new BizError('ISBN不能为空')
    if (books.some(b => b.id !== id && b.isbn === payload.isbn)) throw new BizError('ISBN已存在，不可重复添加')
    if (!payload.category_id) throw new BizError('请选择分类')
    const newTotal = Number(payload.total_count)
    if (!newTotal || newTotal < 1) throw new BizError('总馆藏数量必须≥1')
    // BR-08：新总数 ≥ 已借出数量（总馆藏 - 可借）
    const borrowed = cur.total_count - cur.available_count
    if (newTotal < borrowed) throw new BizError(`总馆藏数不能小于已借出数量（${borrowed}册）`)
    books[idx] = {
      ...cur,
      title: payload.title.trim(),
      author: payload.author.trim(),
      isbn: payload.isbn.trim(),
      category_id: payload.category_id,
      publisher: payload.publisher?.trim() ?? '',
      publish_year: payload.publish_year ?? null,
      total_count: newTotal,
      available_count: cur.available_count + (newTotal - cur.total_count), // 联动
      summary: payload.summary?.trim() ?? '',
      cover_url: payload.cover_url ?? '',
      updated_at: now()
    }
    _db.setBooks(books)
    return books[idx]
  })
}

/** 删除图书（BR-05：有借阅中/逾期记录禁止删除） */
export function deleteBook(id: number) {
  return mockRequest(() => {
    const books = _db.books()
    const book = books.find(b => b.id === id)
    if (!book) throw new BizError('图书不存在')
    const records = _db.records()
    const active = records.filter(r => r.book_id === id && r.status !== 'returned')
    if (active.length > 0) {
      throw new BizError(`该图书尚有 ${active.length} 册未归还，无法删除`)
    }
    // BR-14：删除图书时级联删除收藏记录
    const favs = _db.favs().filter(f => f.book_id !== id)
    _db.setFavs(favs)
    _db.setBooks(books.filter(b => b.id !== id))
    return { message: '删除成功' }
  })
}

/** 封面上传（原型阶段：返回 dataURL 作为 cover_url） */
export function uploadCover(file: File): Promise<{ cover_url: string }> {
  return new Promise((resolve, reject) => {
    if (!['image/jpeg', 'image/png'].includes(file.type)) {
      return reject(new BizError('仅支持 jpg/png 格式'))
    }
    if (file.size > 2 * 1024 * 1024) {
      return reject(new BizError('图片大小不能超过2MB'))
    }
    const reader = new FileReader()
    reader.onload = () => resolve({ cover_url: reader.result as string })
    reader.onerror = () => reject(new BizError('图片读取失败'))
    reader.readAsDataURL(file)
  })
}
