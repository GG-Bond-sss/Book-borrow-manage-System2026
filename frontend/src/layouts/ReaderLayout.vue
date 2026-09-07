<template>
  <el-container class="layout-root">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <span>图书借阅系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :router="true"
        background-color="#001529"
        text-color="#ffffff"
        active-text-color="#ffd666"
      >
        <el-menu-item index="/reader/books">
          <el-icon><Reading /></el-icon>
          <span>图书浏览</span>
        </el-menu-item>
        <el-menu-item index="/reader/borrows">
          <el-icon><List /></el-icon>
          <span>我的借阅</span>
        </el-menu-item>
        <el-menu-item index="/reader/favorites">
          <el-icon><Star /></el-icon>
          <span>我的收藏</span>
        </el-menu-item>
        <el-menu-item index="/reader/profile">
          <el-icon><User /></el-icon>
          <span>个人资料</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="topbar" height="60px">
        <div class="topbar-title">读者中心</div>
        <el-dropdown @command="onCommand">
          <span class="user-chip">
            <el-avatar :size="32" class="avatar">{{ avatarChar }}</el-avatar>
            <span class="user-name">{{ user?.real_name }}</span>
            <el-tag size="small" type="success" effect="dark">读者</el-tag>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人资料</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>

      <el-main class="content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessageBox, ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const user = computed(() => userStore.user)

const activeMenu = computed(() => {
  // 详情页高亮图书浏览
  if (route.path.startsWith('/reader/books')) return '/reader/books'
  return route.path
})
const avatarChar = computed(() => user.value?.real_name?.charAt(0) || 'R')

async function onCommand(cmd: string) {
  if (cmd === 'profile') {
    router.push('/reader/profile')
  } else if (cmd === 'logout') {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', { type: 'warning' })
    await userStore.logout()
    ElMessage.success('已退出登录')
    router.replace('/login')
  }
}
</script>

<style scoped>
.layout-root { height: 100vh; }
.sidebar {
  background: #001529;
  position: fixed;
  left: 0; top: 0; bottom: 0;
  width: 220px;
  overflow-y: auto;
}
.layout-root > .el-container { margin-left: 220px; }
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 1px;
  border-bottom: 1px solid #0d2640;
}
.sidebar :deep(.el-menu) { border-right: none; }
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  padding: 0 24px;
}
.topbar-title { font-size: 16px; font-weight: 600; color: #303133; }
.user-chip { display: flex; align-items: center; gap: 8px; cursor: pointer; outline: none; }
.avatar { background: #001529; color: #ffd666; }
.user-name { font-size: 14px; color: #303133; }
.content { background: #f0f2f5; padding: 20px; overflow-y: auto; }
</style>
