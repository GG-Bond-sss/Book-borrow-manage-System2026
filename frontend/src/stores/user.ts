/**
 * stores/user.ts — 用户/会话状态
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as authApi from '@/api/auth'
import type { Role } from '@/types'

export interface CurrentUser {
  id: number
  username: string
  role: Role
  real_name: string
  phone: string
  email: string
  created_at: string
}

export const useUserStore = defineStore('user', () => {
  const user = ref<CurrentUser | null>(null)
  const token = ref<string | null>(localStorage.getItem('lib_token'))

  const isLoggedIn = computed(() => !!user.value)
  const role = computed<Role | null>(() => user.value?.role ?? null)
  const isAdmin = computed(() => role.value === 'admin')
  const isReader = computed(() => role.value === 'reader')

  /** 初始化：从 localStorage 恢复当前用户 */
  async function init() {
    if (!token.value) {
      user.value = null
      return
    }
    try {
      user.value = await authApi.getProfile()
    } catch {
      // token 失效
      token.value = null
      localStorage.removeItem('lib_token')
      localStorage.removeItem('lib_current_user')
    }
  }

  async function login(username: string, password: string) {
    user.value = await authApi.login(username, password)
    token.value = localStorage.getItem('lib_token')
  }

  async function register(payload: Parameters<typeof authApi.register>[0]) {
    return authApi.register(payload)
  }

  async function updateProfile(payload: { phone: string; email: string }) {
    user.value = await authApi.updateProfile(payload)
    return user.value
  }

  async function changePassword(payload: {
    old_password: string; new_password: string; confirm: string
  }) {
    const res = await authApi.changePassword(payload)
    // 密码修改成功后清除登录态
    await logout()
    return res
  }

  async function logout() {
    await authApi.logout()
    user.value = null
    token.value = null
  }

  return {
    user, token, isLoggedIn, role, isAdmin, isReader,
    init, login, register, updateProfile, changePassword, logout
  }
})
