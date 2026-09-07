<template>
  <div class="page-card">
    <div class="toolbar">
      <h2 class="page-title">分类管理</h2>
      <div class="toolbar-spacer"></div>
      <el-input v-model="query.keyword" placeholder="分类名称" clearable style="width: 200px" @keyup.enter="load" @clear="load" />
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" :icon="Plus" @click="onAdd">新增分类</el-button>
    </div>

    <el-table :data="list" v-loading="loading" border stripe style="width: 100%">
      <el-table-column prop="id" label="编号" width="80" align="center" />
      <el-table-column prop="name" label="分类名称" min-width="180" />
      <el-table-column label="图书数量" width="120" align="center">
        <template #default="{ row }">
          <el-tag :type="row.book_count > 0 ? 'warning' : 'info'">{{ row.book_count }} 本</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" min-width="180">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column prop="updated_at" label="更新时间" min-width="180">
        <template #default="{ row }">{{ formatTime(row.updated_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click="onEdit(row)">编辑</el-button>
          <el-tooltip :content="row.book_count > 0 ? `该分类下有 ${row.book_count} 本图书，无法删除` : ''" :disabled="row.book_count === 0" placement="top">
            <el-button
              link
              :type="row.book_count > 0 ? 'info' : 'danger'"
              size="small"
              @click="onDelete(row)"
            >删除</el-button>
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-wrap">
      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="load"
        @size-change="load"
      />
    </div>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑分类' : '新增分类'" width="420px" @closed="onDialogClosed">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name" placeholder="必填，唯一" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="onSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { categoryApi } from '@/api'
import { useCategoryStore } from '@/stores/category'
import type { PageQuery } from '@/types'

const catStore = useCategoryStore()

const loading = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const query = reactive<PageQuery>({ page: 1, page_size: 10, keyword: '' })

const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const form = reactive({ id: 0, name: '' })

const rules: FormRules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }]
}

function formatTime(iso: string) {
  if (!iso) return '-'
  return new Date(iso).toLocaleString('zh-CN', { hour12: false })
}

async function load() {
  loading.value = true
  try {
    const res = await categoryApi.listCategories(query)
    list.value = res.list
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function onDialogClosed() {
  form.id = 0
  form.name = ''
  formRef.value?.clearValidate()
}

function onAdd() {
  onDialogClosed()
  isEdit.value = false
  dialogVisible.value = true
}

function onEdit(row: any) {
  onDialogClosed()
  form.id = row.id
  form.name = row.name
  isEdit.value = true
  dialogVisible.value = true
}

async function onSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      if (isEdit.value) {
        // 通过 store 修改，自动同步到所有下拉框
        await catStore.update(form.id, form.name)
        ElMessage.success('修改成功')
      } else {
        await catStore.create(form.name)
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      load()
    } catch (e: any) {
      ElMessage.error(e.message || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

async function onDelete(row: any) {
  if (row.book_count > 0) {
    ElMessage.warning(`该分类下有 ${row.book_count} 本图书，无法删除`)
    return
  }
  try {
    await ElMessageBox.confirm(`确定要删除分类「${row.name}」吗？`, '删除确认', { type: 'warning' })
  } catch {
    return
  }
  try {
    // 通过 store 删除，自动从所有下拉框移除
    await catStore.remove(row.id)
    ElMessage.success('删除成功')
    load()
  } catch (e: any) {
    ElMessage.error(e.message || '删除失败')
  }
}

onMounted(load)
</script>

<style scoped>
.page-title { margin: 0; font-size: 18px; color: #303133; }
.toolbar-spacer { flex: 1; }
</style>
