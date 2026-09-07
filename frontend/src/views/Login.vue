<template>
  <div class="login-root">
    <div class="login-box">
      <div class="login-header">
        <div class="brand">
          <el-icon :size="36"><Reading /></el-icon>
          <span>图书借阅管理系统</span>
        </div>
        <p class="subtitle">欢迎登录</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @submit.prevent="onSubmit"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" :prefix-icon="User" size="large" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" :prefix-icon="Lock" size="large" show-password @keyup.enter="onSubmit" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" class="submit-btn" :loading="loading" @click="onSubmit">
            登 录
          </el-button>
        </el-form-item>
        <div class="form-footer">
          <span>还没有账号？</span>
          <router-link to="/register" class="register-link">读者注册</router-link>
        </div>
        <div class="hint">
          管理员预置账号：admin / 123456；读者：reader1 / 123456
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock, Reading } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const form = reactive({ username: '', password: '' })

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function onSubmit() {
  if (!formRef.value) return
  if (!form.username || !form.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await userStore.login(form.username, form.password)
      ElMessage.success('登录成功')
      const home = userStore.role === 'admin' ? '/admin/books' : '/reader/books'
      router.replace(home)
    } catch (e: any) {
      ElMessage.error(e.message || '登录失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-root {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #001529 0%, #0d2640 50%, #1a3a5c 100%);
  padding: 20px;
}
.login-box {
  width: 420px;
  background: #fff;
  border-radius: 12px;
  padding: 40px 36px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
}
.login-header { text-align: center; margin-bottom: 28px; }
.brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 22px;
  font-weight: 700;
  color: #001529;
}
.subtitle { color: #909399; margin: 8px 0 0; font-size: 14px; }
.submit-btn { width: 100%; }
.form-footer { text-align: center; margin-top: 8px; color: #606266; font-size: 14px; }
.register-link { color: #409eff; margin-left: 6px; }
.register-link:hover { text-decoration: underline; }
.hint {
  margin-top: 18px;
  padding: 10px 12px;
  background: #f4f4f5;
  border-radius: 6px;
  font-size: 12px;
  color: #909399;
  text-align: center;
}
</style>
