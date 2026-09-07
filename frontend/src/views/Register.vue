<template>
  <div class="register-root">
    <div class="register-box">
      <div class="register-header">
        <div class="brand">
          <el-icon :size="32"><Reading /></el-icon>
          <span>读者注册</span>
        </div>
        <p class="subtitle">仅可注册读者账号</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="90px"
        label-position="left"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="登录用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="6-20位" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm">
          <el-input v-model="form.confirm" type="password" placeholder="再次输入密码" show-password />
        </el-form-item>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="真实姓名" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="11位手机号" maxlength="11" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="邮箱（含@）" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="submit-btn" :loading="loading" @click="onSubmit">注 册</el-button>
        </el-form-item>
        <div class="form-footer">
          已有账号？
          <router-link to="/login" class="link">返回登录</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Reading } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  confirm: '',
  real_name: '',
  phone: '',
  email: ''
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度为6-20位', trigger: 'blur' }
  ],
  confirm: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: (_r, v, cb) => v === form.password ? cb() : cb(new Error('两次输入的密码不一致')), trigger: 'blur' }
  ],
  real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1\d{10}$/, message: '手机号为11位', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { validator: (_r, v, cb) => v.includes('@') ? cb() : cb(new Error('邮箱格式不正确')), trigger: 'blur' }
  ]
}

async function onSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await userStore.register({ ...form })
      ElMessage.success('注册成功，请登录')
      setTimeout(() => router.push('/login'), 1500)
    } catch (e: any) {
      ElMessage.error(e.message || '注册失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.register-root {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #001529 0%, #0d2640 50%, #1a3a5c 100%);
  padding: 30px 20px;
}
.register-box {
  width: 460px;
  background: #fff;
  border-radius: 12px;
  padding: 36px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
}
.register-header { text-align: center; margin-bottom: 24px; }
.brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 22px;
  font-weight: 700;
  color: #001529;
}
.subtitle { color: #909399; margin: 8px 0 0; font-size: 13px; }
.submit-btn { width: 100%; }
.form-footer { text-align: center; margin-top: 4px; color: #606266; font-size: 14px; }
.link { color: #409eff; margin-left: 6px; }
.link:hover { text-decoration: underline; }
</style>
