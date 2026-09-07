/**
 * api/index.ts — 统一导出所有 API 模块
 */
import * as auth from './auth'
import * as book from './book'
import * as category from './category'
import * as borrow from './borrow'
import * as favorite from './favorite'

export const authApi = auth
export const bookApi = book
export const categoryApi = category
export const borrowApi = borrow
export const favoriteApi = favorite

export { auth, book, category, borrow, favorite }
