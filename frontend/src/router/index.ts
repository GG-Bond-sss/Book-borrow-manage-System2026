/**
 * router/index.ts — 路由配置 + 角色守卫
 */
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'login', component: () => import('@/views/Login.vue'), meta: { title: '登录' } },
  { path: '/register', name: 'register', component: () => import('@/views/Register.vue'), meta: { title: '读者注册' } },

  // 管理员路由
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, role: 'admin' },
    redirect: '/admin/books',
    children: [
      { path: 'books', name: 'admin-books', component: () => import('@/views/admin/Books.vue'), meta: { title: '图书管理' } },
      { path: 'categories', name: 'admin-categories', component: () => import('@/views/admin/Categories.vue'), meta: { title: '分类管理' } },
      { path: 'records', name: 'admin-records', component: () => import('@/views/admin/Records.vue'), meta: { title: '借阅记录' } },
      { path: 'profile', name: 'admin-profile', component: () => import('@/views/Profile.vue'), meta: { title: '个人资料' } }
    ]
  },

  // 读者路由
  {
    path: '/reader',
    component: () => import('@/layouts/ReaderLayout.vue'),
    meta: { requiresAuth: true, role: 'reader' },
    redirect: '/reader/books',
    children: [
      { path: 'books', name: 'reader-books', component: () => import('@/views/reader/Books.vue'), meta: { title: '图书浏览' } },
      { path: 'books/:id', name: 'reader-book-detail', component: () => import('@/views/reader/BookDetail.vue'), meta: { title: '图书详情' } },
      { path: 'borrows', name: 'reader-borrows', component: () => import('@/views/reader/MyBorrows.vue'), meta: { title: '我的借阅' } },
      { path: 'favorites', name: 'reader-favorites', component: () => import('@/views/reader/Favorites.vue'), meta: { title: '我的收藏' } },
      { path: 'profile', name: 'reader-profile', component: () => import('@/views/Profile.vue'), meta: { title: '个人资料' } }
    ]
  },

  { path: '/:pathMatch(.*)*', redirect: '/login' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const HOME: Record<string, string> = {
  admin: '/admin/books',
  reader: '/reader/books'
}

router.beforeEach(async (to) => {
  const userStore = useUserStore()
  // 首次进入时初始化用户态
  if (userStore.token && !userStore.user) {
    await userStore.init()
  }

  const requiresAuth = to.meta.requiresAuth
  const needRole = to.meta.role as string | undefined

  if (requiresAuth && !userStore.isLoggedIn) {
    return { name: 'login' }
  }

  // 已登录访问登录/注册页 → 跳首页
  if (userStore.isLoggedIn && (to.name === 'login' || to.name === 'register')) {
    return HOME[userStore.role!] ?? '/login'
  }

  // 角色隔离：读者访问管理员页面、管理员访问读者页面
  if (needRole && userStore.role && userStore.role !== needRole) {
    ElMessage?.error('无权限访问')
    return HOME[userStore.role] ?? '/login'
  }

  if (to.meta.title) {
    document.title = `${to.meta.title} - 图书借阅管理系统`
  }
})

export default router
