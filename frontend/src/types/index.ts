// 核心类型定义

export type Role = 'admin' | 'reader'

export interface User {
  id: number
  username: string
  password: string // 原型阶段明文存储，真实场景应为哈希
  role: Role
  real_name: string
  phone: string
  email: string
  created_at: string
}

export interface Category {
  id: number
  name: string
  created_at: string
  updated_at: string
}

export interface Book {
  id: number
  title: string
  author: string
  isbn: string
  category_id: number
  publisher: string
  publish_year: number | null
  total_count: number
  available_count: number
  summary: string
  cover_url: string
  created_at: string
  updated_at: string
}

export type BorrowStatus = 'borrowed' | 'returned' | 'overdue'

export interface BorrowRecord {
  id: number
  user_id: number
  book_id: number
  borrow_time: string
  due_time: string
  return_time: string | null
  status: BorrowStatus
  operator_id: number
}

export interface Favorite {
  id: number
  user_id: number
  book_id: number
  created_at: string
}

// API 响应统一格式
export interface ApiResult<T = any> {
  code: number
  message: string
  data: T
}

export interface PageResult<T = any> {
  list: T[]
  total: number
  page: number
  page_size: number
}

export interface PageQuery {
  page?: number
  page_size?: number
  keyword?: string
  category_id?: number | null
  status?: BorrowStatus | null
  reader_keyword?: string
  book_keyword?: string
  start_time?: string | null
  end_time?: string | null
}
