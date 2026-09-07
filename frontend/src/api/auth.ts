/**
 * api/auth.ts — 认证相关接口（登录/注册/个人资料/修改密码）
 */
import { db as _db, now } from '@/mock/db'
import { mockRequest, BizError, setToken, setCurrentUser, getCurrentUser, clearToken } from './request'
import type { User } from '@/types'

function genToken(userId: number): string {
  return 'mock-token-' + userId + '-' + Date.now()
}

function sanitize(u: User) {
  const { password, ...rest } = u
  return rest
}

/** 登录 */
export function login(username: string, password: string) {
  return mockRequest(() => {
    const users = _db.users()
    const user = users.find(u => u.username === username)
    if (!user) throw new BizError('用户名不存在')
    if (user.password !== password) throw new BizError('密码错误')
    const token = genToken(user.id)
    setToken(token)
    setCurrentUser(sanitize(user))
    return sanitize(user)
  })
}

/** 注册（仅读者） */
export function register(payload: {
  username: string
  password: string
  confirm: string
  real_name: string
  phone: string
  email: string
}) {
  return mockRequest(() => {
    const { username, password, confirm, real_name, phone, email } = payload
    if (!username) throw new BizError('用户名不能为空')
    if (!real_name) throw new BizError('姓名不能为空')
    if (password.length < 6 || password.length > 20) throw new BizError('密码长度为6-20位')
    if (password !== confirm) throw new BizError('两次输入的密码不一致')
    if (!/^1\d{10}$/.test(phone)) throw new BizError('手机号格式不正确（11位）')
    if (!email.includes('@')) throw new BizError('邮箱格式不正确')
    const users = _db.users()
    if (users.some(u => u.username === username)) throw new BizError('用户名已存在')
    const id = _db.nextId('users')
    const user: User = {
      id, username, password, role: 'reader',
      real_name, phone, email, created_at: now()
    }
    users.push(user)
    _db.setUsers(users)
    return { message: '注册成功' }
  })
}

/** 获取当前用户 */
export function getProfile() {
  return mockRequest(() => {
    const cur = getCurrentUser()
    if (!cur) throw new BizError('未登录')
    const user = _db.users().find(u => u.id === cur.id)
    if (!user) throw new BizError('用户不存在')
    return sanitize(user)
  })
}

/** 更新个人资料（手机号/邮箱） */
export function updateProfile(payload: { phone: string; email: string }) {
  return mockRequest(() => {
    const cur = getCurrentUser()
    if (!cur) throw new BizError('未登录')
    if (!/^1\d{10}$/.test(payload.phone)) throw new BizError('手机号格式不正确（11位）')
    if (!payload.email.includes('@')) throw new BizError('邮箱格式不正确')
    const users = _db.users()
    const idx = users.findIndex(u => u.id === cur.id)
    if (idx < 0) throw new BizError('用户不存在')
    users[idx].phone = payload.phone
    users[idx].email = payload.email
    _db.setUsers(users)
    setCurrentUser(sanitize(users[idx]))
    return sanitize(users[idx])
  })
}

/** 修改密码 */
export function changePassword(payload: { old_password: string; new_password: string; confirm: string }) {
  return mockRequest(() => {
    const cur = getCurrentUser()
    if (!cur) throw new BizError('未登录')
    const users = _db.users()
    const user = users.find(u => u.id === cur.id)
    if (!user) throw new BizError('用户不存在')
    if (user.password !== payload.old_password) throw new BizError('原密码不正确')
    if (payload.new_password.length < 6 || payload.new_password.length > 20) throw new BizError('新密码长度为6-20位')
    if (payload.new_password !== payload.confirm) throw new BizError('两次输入的密码不一致')
    if (payload.new_password === payload.old_password) throw new BizError('新密码不能与原密码相同')
    user.password = payload.new_password
    _db.setUsers(users)
    return { message: '密码修改成功' }
  })
}

/** 退出登录 */
export function logout() {
  return mockRequest(() => {
    clearToken()
    return { message: '已退出登录' }
  }, 50)
}
