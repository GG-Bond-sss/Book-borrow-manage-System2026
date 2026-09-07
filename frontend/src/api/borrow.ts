/**
 * api/borrow.ts — 借阅记录接口（借书/还书/查询）
 */
import { db as _db, now, addDays, LOAN_DAYS, BORROW_LIMIT, isOverdue, paginate } from '@/mock/db'
import { mockRequest, BizError, getCurrentUser } from './request'
import type { BorrowRecord, BorrowStatus, PageQuery, PageResult } from '@/types'

/** 刷新逾期状态（查询时实时判定 BR-07） */
function refreshStatus(r: BorrowRecord): BorrowRecord {
  if (r.status === 'returned') return r
  if (isOverdue(r)) r.status = 'overdue'
  else r.status = 'borrowed'
  return r
}

/** 全部借阅记录（管理员） */
export function listAllRecords(q: PageQuery): Promise<PageResult<BorrowRecord & {
  reader_name: string; reader_username: string; book_title: string; book_isbn: string
}>> {
  return mockRequest(() => {
    const users = _db.users()
    const books = _db.books()
    let records = _db.records().map(refreshStatus)
    // 状态筛选
    if (q.status) records = records.filter(r => r.status === q.status)
    // 读者关键词
    if (q.reader_keyword) {
      const kw = q.reader_keyword.trim().toLowerCase()
      records = records.filter(r => {
        const u = users.find(u => u.id === r.user_id)
        return u && (u.username.toLowerCase().includes(kw) || u.real_name.toLowerCase().includes(kw))
      })
    }
    // 图书关键词
    if (q.book_keyword) {
      const kw = q.book_keyword.trim().toLowerCase()
      records = records.filter(r => {
        const b = books.find(b => b.id === r.book_id)
        return b && (b.title.toLowerCase().includes(kw) || b.isbn.toLowerCase().includes(kw))
      })
    }
    // 借出时间范围
    if (q.start_time) records = records.filter(r => r.borrow_time >= q.start_time!)
    if (q.end_time) records = records.filter(r => r.borrow_time <= q.end_time!)
    // 按借出时间倒序
    records.sort((a, b) => b.borrow_time.localeCompare(a.borrow_time))
    const list = records.map(r => {
      const u = users.find(u => u.id === r.user_id)
      const b = books.find(b => b.id === r.book_id)
      return {
        ...r,
        reader_name: u?.real_name ?? '未知读者',
        reader_username: u?.username ?? '',
        book_title: b?.title ?? '未知图书',
        book_isbn: b?.isbn ?? ''
      }
    })
    return paginate(list, q)
  })
}

/** 我的借阅记录（读者） */
export function listMyRecords(q: PageQuery): Promise<PageResult<BorrowRecord & {
  book_title: string; book_isbn: string; book_cover: string
}>> {
  return mockRequest(() => {
    const cur = getCurrentUser()
    if (!cur) throw new BizError('未登录')
    const books = _db.books()
    let records = _db.records()
      .filter(r => r.user_id === cur.id)
      .map(refreshStatus)
    if (q.status) records = records.filter(r => r.status === q.status)
    records.sort((a, b) => b.borrow_time.localeCompare(a.borrow_time))
    const list = records.map(r => {
      const b = books.find(b => b.id === r.book_id)
      return {
        ...r,
        book_title: b?.title ?? '未知图书',
        book_isbn: b?.isbn ?? '',
        book_cover: b?.cover_url ?? ''
      }
    })
    return paginate(list, q)
  })
}

/** 借书（含全部业务规则校验） */
export function borrowBook(bookId: number) {
  return mockRequest(() => {
    const cur = getCurrentUser()
    if (!cur) throw new BizError('未登录')
    if (cur.role !== 'reader') throw new BizError('仅读者可借书')
    const books = _db.books()
    const book = books.find(b => b.id === bookId)
    if (!book) throw new BizError('图书不存在')
    // BR-03：可借数量为0
    if (book.available_count <= 0) throw new BizError('该书已借完')
    const records = _db.records().map(refreshStatus)
    // BR-01：借阅上限5册
    const active = records.filter(r => r.user_id === cur.id && r.status !== 'returned')
    if (active.length >= BORROW_LIMIT) throw new BizError(`借阅已达上限（${BORROW_LIMIT}册）`)
    // BR-04：存在逾期未还
    if (active.some(r => r.status === 'overdue')) throw new BizError('您有逾期未还图书，暂不可借阅')
    const t = now()
    const id = _db.nextId('records')
    const record: BorrowRecord = {
      id,
      user_id: cur.id,
      book_id: bookId,
      borrow_time: t,
      due_time: addDays(new Date(t), LOAN_DAYS),
      return_time: null,
      status: 'borrowed',
      operator_id: cur.id
    }
    records.push(record)
    _db.setRecords(records)
    // 库存 -1
    book.available_count -= 1
    _db.setBooks(books)
    return record
  })
}

/** 还书（读者自助 / 管理员办理，BR-10：逾期不拦截还书） */
export function returnBook(recordId: number) {
  return mockRequest(() => {
    const cur = getCurrentUser()
    if (!cur) throw new BizError('未登录')
    const records = _db.records().map(refreshStatus)
    const idx = records.findIndex(r => r.id === recordId)
    if (idx < 0) throw new BizError('借阅记录不存在')
    const r = records[idx]
    if (r.status === 'returned') throw new BizError('该记录已归还')
    // 读者只能归还本人记录；管理员可代归还
    if (cur.role !== 'admin' && r.user_id !== cur.id) throw new BizError('无权操作他人借阅记录')
    const t = now()
    r.return_time = t
    r.status = 'returned'
    r.operator_id = cur.id
    records[idx] = r
    _db.setRecords(records)
    // 库存 +1
    const books = _db.books()
    const book = books.find(b => b.id === r.book_id)
    if (book) {
      book.available_count = Math.min(book.total_count, book.available_count + 1)
      _db.setBooks(books)
    }
    return r
  })
}
