<template>
  <div class="profile-root">
    <div class="page-card">
      <h2 class="section-title">基本信息</h2>
      <el-form :model="profile" label-width="100px" class="profile-form" v-loading="loading">
        <el-form-item label="用户名">
          <el-input v-model="profile.username" disabled />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="profile.real_name" disabled />
        </el-form-item>
        <el-form-item label="角色">
          <el-tag :type="user?.role === 'admin' ? 'danger' : 'success'" effect="dark">
            {{ user?.role === 'admin' ? '管理员' : '读者' }}
          </el-tag>
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="profile.phone" maxlength="11" placeholder="11位手机号" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="profile.email" placeholder="邮箱（含@）" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="onSaveProfile">保存资料</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="page-card" style="margin-top: 20px;">
      <h2 class="section-title">修改密码</h2>
      <el-form
        ref="pwdFormRef"
        :model="pwdForm"
        :rules="pwdRules"
        label-width="100px"
        class="profile-form"
      >
        <el-form-item label="原密码" prop="old_password">
          <el-input v-model="pwdForm.old_password" type="password" show-password placeholder="请输入原密码" />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="pwdForm.new_password" type="password" show-password placeholder="6-20位" />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirm">
          <el-input v-model="pwdForm.confirm" type="password" show-password placeholder="再次输入新密码" />
        </el-form-item>
        <el-form-item>
          <el-button type="warning" :loading="changing" @click="onChangePwd">确认修改</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { authApi } from '@/api'

const router = useRouter()
const userStore = useUserStore()
const user = userStore.user

const loading = ref(false)
const saving = ref(false)
const changing = ref(false)

const profile = reactive({
  username: '',
  real_name: '',
  phone: '',
  email: ''
})

const pwdFormRef = ref<FormInstance>()
const pwdForm = reactive({ old_password: '', new_password: '', confirm: '' })

const pwdRules: FormRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度为6-20位', trigger: 'blur' }
  ],
  confirm: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: (_r, v, cb) => v === pwdForm.new_password ? cb() : cb(new Error('两次输入的密码不一致')), trigger: 'blur' }
  ]
}

async function loadProfile() {
  loading.value = true
  try {
    const u = await authApi.getProfile()
    profile.username = u.username
    profile.real_name = u.real_name
    profile.phone = u.phone
    profile.email = u.email
  } catch (e: any) {
    ElMessage.error(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

async function onSaveProfile() {
  if (!/^1\d{10}$/.test(profile.phone)) {
    ElMessage.error('手机号格式不正确（11位）')
    return
  }
  if (!profile.email.includes('@')) {
    ElMessage.error('邮箱格式不正确')
    return
  }
  saving.value = true
  try {
    await userStore.updateProfile({ phone: profile.phone, email: profile.email })
    ElMessage.success('资料保存成功')
  } catch (e: any) {
    ElMessage.error(e.message || '保存失败')
  } finally {
    saving.value = false
  }
}

async function onChangePwd() {
  if (!pwdFormRef.value) return
  await pwdFormRef.value.validate(async (valid) => {
    if (!valid) return
    if (pwdForm.new_password === pwdForm.old_password) {
      ElMessage.error('新密码不能与原密码相同')
      return
    }
    changing.value = true
    try {
      await userStore.changePassword({ ...pwdForm })
      ElMessage.success('密码修改成功，请重新登录')
      setTimeout(() => {
        userStore.logout()
        router.replace('/login')
      }, 1500)
    } catch (e: any) {
      ElMessage.error(e.message || '修改失败')
    } finally {
      changing.value = false
    }
  })
}

onMounted(loadProfile)
</script>

<style scoped>
.profile-root { max-width: 720px; margin: 0 auto; }
.section-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 18px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
  color: #303133;
}
.profile-form { max-width: 520px; }
</style>
