/**
 * api/category.ts — 分类管理接口
 */
import { db as _db, now, paginate } from '@/mock/db'
import { mockRequest, BizError } from './request'
import type { Category, PageQuery, PageResult } from '@/types'

/** 分类列表（含图书数量） */
export function listCategories(q?: PageQuery): Promise<PageResult<Category & { book_count: number }>> {
  return mockRequest(() => {
    const cats = _db.cats()
    const books = _db.books()
    const list = cats
      .map(c => ({
        ...c,
        book_count: books.filter(b => b.category_id === c.id).length
      }))
      .sort((a, b) => a.id - b.id)
    if (q && q.keyword) {
      const kw = q.keyword.trim().toLowerCase()
      return paginate(list.filter(c => c.name.toLowerCase().includes(kw)), q)
    }
    // 不分页时返回全部
    if (!q || !q.page) {
      return { list, total: list.length, page: 1, page_size: list.length || 1 }
    }
    return paginate(list, q)
  })
}

/** 全部分类（不分页，供下拉选择用） */
export function allCategories(): Promise<Category[]> {
  return mockRequest(() => _db.cats().sort((a, b) => a.id - b.id))
}

/** 新增分类 */
export function createCategory(name: string) {
  return mockRequest(() => {
    const cats = _db.cats()
    if (!name.trim()) throw new BizError('分类名称不能为空')
    if (cats.some(c => c.name === name.trim())) throw new BizError('分类名称已存在')
    const id = _db.nextId('cats')
    const t = now()
    const cat: Category = { id, name: name.trim(), created_at: t, updated_at: t }
    cats.push(cat)
    _db.setCats(cats)
    return cat
  })
}

/** 修改分类 */
export function updateCategory(id: number, name: string) {
  return mockRequest(() => {
    const cats = _db.cats()
    const idx = cats.findIndex(c => c.id === id)
    if (idx < 0) throw new BizError('分类不存在')
    if (!name.trim()) throw new BizError('分类名称不能为空')
    if (cats.some(c => c.id !== id && c.name === name.trim())) throw new BizError('分类名称已存在')
    cats[idx].name = name.trim()
    cats[idx].updated_at = now()
    _db.setCats(cats)
    return cats[idx]
  })
}

/** 删除分类（BR-11：分类下有图书时禁止删除） */
export function deleteCategory(id: number) {
  return mockRequest(() => {
    const cats = _db.cats()
    const cat = cats.find(c => c.id === id)
    if (!cat) throw new BizError('分类不存在')
    const count = _db.books().filter(b => b.category_id === id).length
    if (count > 0) throw new BizError(`该分类下有 ${count} 本图书，无法删除`)
    _db.setCats(cats.filter(c => c.id !== id))
    return { message: '删除成功' }
  })
}
