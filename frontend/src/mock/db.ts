/**
 * mock/db.ts — 基于 localStorage 的内存数据库
 * 所有 API 模块共享此实例。模拟后端业务逻辑与全部业务规则校验。
 */
import type {
  User, Category, Book, BorrowRecord, Favorite,
  BorrowStatus, PageQuery, PageResult
} from '@/types'

const KEYS = {
  users: 'lib_users',
  cats: 'lib_cats',
  books: 'lib_books',
  records: 'lib_records',
  favs: 'lib_favs',
  seq: 'lib_seq',
  ver: 'lib_seed_ver'
}

export const LOAN_DAYS = 30
export const BORROW_LIMIT = 5
/** 种子数据版本：升级后自动重置 localStorage 中的脏数据 */
export const SEED_VERSION = 2

/* ---------- 基础读写 ---------- */
function read<T>(key: string, def: T): T {
  try {
    const v = localStorage.getItem(key)
    return v ? JSON.parse(v) as T : def
  } catch {
    return def
  }
}
function write<T>(key: string, val: T) {
  localStorage.setItem(key, JSON.stringify(val))
}

/* ---------- 序号生成 ---------- */
function nextId(name: keyof typeof KEYS): number {
  const seq = read<Record<string, number>>(KEYS.seq, {})
  const cur = (seq[name] ?? 0) + 1
  seq[name] = cur
  write(KEYS.seq, seq)
  return cur
}

/* ---------- 时间工具 ---------- */
export function now(): string { return new Date().toISOString() }
export function addDays(date: Date, days: number): string {
  const d = new Date(date)
  d.setDate(d.getDate() + days)
  return d.toISOString()
}
export function isOverdue(r: BorrowRecord): boolean {
  if (r.status === 'returned') return false
  return new Date(r.due_time).getTime() < Date.now()
}

/* ---------- 初始化种子数据 ---------- */
export function initSeed() {
  const storedVer = read<number>(KEYS.ver, 0)
  if (storedVer === SEED_VERSION && read<User[] | null>(KEYS.users, null) !== null) return
  // 版本不匹配或首次初始化：重置全部种子数据，清除脏数据（如"自然"作者为0的错误记录）

  const t = now()
  // 用户：预置管理员 + 几个读者
  const users: User[] = [
    { id: 1, username: 'admin', password: '123456', role: 'admin', real_name: '系统管理员', phone: '13800000001', email: 'admin@library.com', created_at: t },
    { id: 2, username: 'reader1', password: '123456', role: 'reader', real_name: '张三', phone: '13800000002', email: 'zhangsan@library.com', created_at: t },
    { id: 3, username: 'reader2', password: '123456', role: 'reader', real_name: '李四', phone: '13800000003', email: 'lisi@library.com', created_at: t }
  ]
  // 分类
  const cats: Category[] = [
    { id: 1, name: '文学', created_at: t, updated_at: t },
    { id: 2, name: '科技', created_at: t, updated_at: t },
    { id: 3, name: '历史', created_at: t, updated_at: t },
    { id: 4, name: '哲学', created_at: t, updated_at: t },
    { id: 5, name: '自然', created_at: t, updated_at: t }
  ]
  // 图书
  const books: Book[] = [
    { id: 1, title: '红楼梦', author: '曹雪芹', isbn: '9787020002207', category_id: 1, publisher: '人民文学出版社', publish_year: 1996, total_count: 5, available_count: 3, summary: '中国古典四大名著之一，描写贾府兴衰。', cover_url: '', created_at: t, updated_at: t },
    { id: 2, title: '三体', author: '刘慈欣', isbn: '9787536692930', category_id: 2, publisher: '重庆出版社', publish_year: 2008, total_count: 4, available_count: 4, summary: '中国科幻里程碑，讲述人类文明与三体文明的故事。', cover_url: '', created_at: t, updated_at: t },
    { id: 3, title: '人类简史', author: '尤瓦尔·赫拉利', isbn: '9787508647357', category_id: 3, publisher: '中信出版社', publish_year: 2014, total_count: 3, available_count: 2, summary: '从认知革命到科学革命，重新审视人类历史。', cover_url: '', created_at: t, updated_at: t },
    { id: 4, title: '明朝那些事儿', author: '当年明月', isbn: '9787540461188', category_id: 3, publisher: '湖南人民出版社', publish_year: 2009, total_count: 6, available_count: 6, summary: '以通俗笔法讲述明朝三百年兴衰。', cover_url: '', created_at: t, updated_at: t },
    { id: 5, title: '苏菲的世界', author: '乔斯坦·贾德', isbn: '9787544263566', category_id: 4, publisher: '南海出版公司', publish_year: 2011, total_count: 2, available_count: 1, summary: '一本西方哲学史的入门小说。', cover_url: '', created_at: t, updated_at: t },
    { id: 6, title: '西游记', author: '吴承恩', isbn: '9787020008704', category_id: 1, publisher: '人民文学出版社', publish_year: 2004, total_count: 3, available_count: 3, summary: '四大名著之一，讲述唐僧师徒西天取经。', cover_url: '', created_at: t, updated_at: t },
    { id: 7, title: '时间简史', author: '史蒂芬·霍金', isbn: '9787535732309', category_id: 2, publisher: '湖南科学技术出版社', publish_year: 2010, total_count: 2, available_count: 0, summary: '探索宇宙起源与时间本质的科普经典。', cover_url: '', created_at: t, updated_at: t },
    { id: 8, title: '瓦尔登湖', author: '亨利·戴维·梭罗', isbn: '9787544291707', category_id: 5, publisher: '南海出版公司', publish_year: 2017, total_count: 3, available_count: 3, summary: '记录作者在瓦尔登湖畔自给自足的隐居生活，感悟自然与人生。', cover_url: '', created_at: t, updated_at: t }
  ]
  // 借阅记录：为 reader1 制造几条，其中一条逾期
  const borrowTime = new Date()
  borrowTime.setDate(borrowTime.getDate() - 40) // 40天前借出 → 已逾期
  const overdueBorrow = borrowTime.toISOString()
  const overdueDue = addDays(new Date(overdueBorrow), LOAN_DAYS)

  const normalBorrow = new Date()
  normalBorrow.setDate(normalBorrow.getDate() - 10)
  const normalBorrowIso = normalBorrow.toISOString()
  const normalDue = addDays(new Date(normalBorrowIso), LOAN_DAYS)

  const records: BorrowRecord[] = [
    { id: 1, user_id: 2, book_id: 1, borrow_time: overdueBorrow, due_time: overdueDue, return_time: null, status: 'borrowed', operator_id: 2 },
    { id: 2, user_id: 2, book_id: 3, borrow_time: normalBorrowIso, due_time: normalDue, return_time: null, status: 'borrowed', operator_id: 2 }
  ]
  // 收藏
  const favs: Favorite[] = [
    { id: 1, user_id: 2, book_id: 2, created_at: t },
    { id: 2, user_id: 2, book_id: 5, created_at: t }
  ]
  const seq: Record<string, number> = { users: 3, cats: 5, books: 8, records: 2, favs: 2 }

  write(KEYS.users, users)
  write(KEYS.cats, cats)
  write(KEYS.books, books)
  write(KEYS.records, records)
  write(KEYS.favs, favs)
  write(KEYS.seq, seq)
  write(KEYS.ver, SEED_VERSION)
}

/* ---------- 通用分页工具 ---------- */
export function paginate<T>(list: T[], q: PageQuery): PageResult<T> {
  const page = q.page ?? 1
  const page_size = q.page_size ?? 10
  const start = (page - 1) * page_size
  return {
    list: list.slice(start, start + page_size),
    total: list.length,
    page,
    page_size
  }
}

/* ---------- 导出存储访问器 ---------- */
export const db = {
  users: () => read<User[]>(KEYS.users, []),
  cats: () => read<Category[]>(KEYS.cats, []),
  books: () => read<Book[]>(KEYS.books, []),
  records: () => read<BorrowRecord[]>(KEYS.records, []),
  favs: () => read<Favorite[]>(KEYS.favs, []),
  setUsers: (v: User[]) => write(KEYS.users, v),
  setCats: (v: Category[]) => write(KEYS.cats, v),
  setBooks: (v: Book[]) => write(KEYS.books, v),
  setRecords: (v: BorrowRecord[]) => write(KEYS.records, v),
  setFavs: (v: Favorite[]) => write(KEYS.favs, v),
  nextId
}
