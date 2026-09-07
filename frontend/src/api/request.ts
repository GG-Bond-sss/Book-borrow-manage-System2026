/**
 * api/request.ts — 请求封装
 * 原型阶段：直接对接 mock db，模拟网络延迟与 Token 鉴权。
 * 切换真实后端时，将各 api/*.ts 中的 mockRequest 调用替换为 axios 请求即可。
 */
import { initSeed } from '@/mock/db'

const TOKEN_KEY = 'lib_token'
const USER_KEY = 'lib_current_user'

initSeed()

export function setToken(token: string) { localStorage.setItem(TOKEN_KEY, token) }
export function getToken(): string | null { return localStorage.getItem(TOKEN_KEY) }
export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export function setCurrentUser(user: any) {
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}
export function getCurrentUser(): any | null {
  try {
    const v = localStorage.getItem(USER_KEY)
    return v ? JSON.parse(v) : null
  } catch {
    return null
  }
}

/** 模拟网络延迟 */
export function delay<T>(data: T, ms = 120): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(data), ms))
}

/** 模拟请求：执行业务函数并返回 Promise，统一延迟 */
export async function mockRequest<T>(fn: () => T, ms = 120): Promise<T> {
  await new Promise((r) => setTimeout(r, ms))
  return fn()
}

/** 模拟请求失败 */
export function mockError(message: string): Promise<never> {
  return new Promise((_, reject) => {
    setTimeout(() => reject(new Error(message)), 120)
  })
}

/** 业务异常 */
export class BizError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'BizError'
  }
}
