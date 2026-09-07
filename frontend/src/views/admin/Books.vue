<template>
  <div class="page-card">
    <div class="toolbar">
      <h2 class="page-title">图书管理</h2>
      <div class="toolbar-spacer"></div>
      <el-input
        v-model="query.keyword"
        placeholder="书名 / 作者 / ISBN"
        clearable
        style="width: 240px"
        @keyup.enter="onSearch"
        @clear="onSearch"
      />
      <el-select v-model="query.category_id" placeholder="全部分类" clearable style="width: 140px" @change="onSearch">
        <el-option v-for="c in catStore.list" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
      <el-button type="primary" @click="onSearch">搜索</el-button>
      <el-button @click="onReset">重置</el-button>
      <el-button type="success" :icon="Plus" @click="onAdd">新增图书</el-button>
    </div>

    <el-table :data="list" v-loading="loading" border stripe style="width: 100%">
      <el-table-column label="封面" width="80" align="center">
        <template #default="{ row }">
          <BookCover :cover-url="row.cover_url" :title="row.title" :width="48" :height="64" />
        </template>
      </el-table-column>
      <el-table-column prop="title" label="书名" min-width="160" show-overflow-tooltip />
      <el-table-column prop="author" label="作者" min-width="120" show-overflow-tooltip />
      <el-table-column prop="isbn" label="ISBN" min-width="160" show-overflow-tooltip />
      <el-table-column prop="category_name" label="分类" width="90" />
      <el-table-column prop="publisher" label="出版社" min-width="140" show-overflow-tooltip />
      <el-table-column prop="publish_year" label="出版年份" width="100" />
      <el-table-column label="总馆藏" width="80" align="center">
        <template #default="{ row }">{{ row.total_count }}</template>
      </el-table-column>
      <el-table-column label="可借" width="80" align="center">
        <template #default="{ row }">
          <span :class="row.available_count > 0 ? 'status-available' : 'status-returned'">
            {{ row.available_count }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click="onEdit(row)">编辑</el-button>
          <el-button link type="danger" size="small" @click="onDelete(row)">删除</el-button>
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

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑图书' : '新增图书'"
      width="640px"
      :close-on-click-modal="false"
      @closed="onDialogClosed"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="书名" prop="title">
          <el-input v-model="form.title" placeholder="必填" />
        </el-form-item>
        <el-form-item label="作者" prop="author">
          <el-input v-model="form.author" placeholder="必填" />
        </el-form-item>
        <el-form-item label="ISBN" prop="isbn">
          <el-input v-model="form.isbn" placeholder="必填，唯一" />
        </el-form-item>
        <el-form-item label="分类" prop="category_id">
          <el-select v-model="form.category_id" placeholder="请选择分类" style="width: 100%">
            <el-option v-for="c in catStore.list" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="出版社" prop="publisher">
          <el-input v-model="form.publisher" />
        </el-form-item>
        <el-form-item label="出版年份" prop="publish_year">
          <el-input-number v-model="form.publish_year" :min="1000" :max="new Date().getFullYear()" controls-position="right" style="width: 100%" />
        </el-form-item>
        <el-form-item label="总馆藏数量" prop="total_count">
          <el-input-number v-model="form.total_count" :min="1" controls-position="right" style="width: 100%" />
        </el-form-item>
        <el-form-item label="封面图片">
          <div class="cover-row">
            <div class="cover-upload">
              <el-upload
                :show-file-list="false"
                :before-upload="onBeforeUpload"
                :disabled="!!form.cover_url"
                accept="image/jpeg,image/png"
              >
                <el-button :disabled="!!form.cover_url">本地上传</el-button>
                <span class="cover-tip">jpg/png ≤2MB</span>
              </el-upload>
            </div>
            <div class="cover-divider">或</div>
            <el-input
              v-model="coverUrlInput"
              placeholder="请输入图片URL"
              :disabled="!!form.cover_url"
              style="flex: 1"
              @input="onUrlInput"
            />
            <el-button v-if="form.cover_url" link type="danger" @click="clearCover">清除</el-button>
          </div>
          <div v-if="form.cover_url" class="cover-preview">
            <img :src="form.cover_url" alt="封面预览" @error="onPreviewError" />
            <span class="cover-label">封面预览</span>
          </div>
        </el-form-item>
        <el-form-item label="简介" prop="summary">
          <el-input v-model="form.summary" type="textarea" :rows="3" />
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
import BookCover from '@/components/BookCover.vue'
import { useCategoryStore } from '@/stores/category'
import { bookApi } from '@/api'
import type { Book, PageQuery } from '@/types'

const catStore = useCategoryStore()
const loading = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const query = reactive<PageQuery>({
  page: 1,
  page_size: 10,
  keyword: '',
  category_id: null
})

const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const coverUrlInput = ref('')

type BookForm = Omit<Partial<Book>, 'category_id' | 'publish_year'> & {
  category_id: number | null
  publish_year: number | null
}

const form = reactive<BookForm>({
  title: '', author: '', isbn: '', category_id: null,
  publisher: '', publish_year: new Date().getFullYear(),
  total_count: 1, summary: '', cover_url: ''
})

const rules: FormRules = {
  title: [{ required: true, message: '请输入书名', trigger: 'blur' }],
  author: [{ required: true, message: '请输入作者', trigger: 'blur' }],
  isbn: [{ required: true, message: '请输入ISBN', trigger: 'blur' }],
  category_id: [{ required: true, message: '请选择分类', trigger: 'change' }],
  total_count: [{ required: true, message: '请输入总馆藏数量', trigger: 'blur' }]
}

async function load() {
  loading.value = true
  try {
    const res = await bookApi.listBooks(query)
    list.value = res.list
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function onSearch() { query.page = 1; load() }
function onReset() {
  query.keyword = ''
  query.category_id = null
  onSearch()
}

function resetForm() {
  Object.assign(form, {
    title: '', author: '', isbn: '', category_id: null,
    publisher: '', publish_year: new Date().getFullYear(),
    total_count: 1, summary: '', cover_url: ''
  })
  coverUrlInput.value = ''
}

function onAdd() {
  resetForm()
  isEdit.value = false
  dialogVisible.value = true
}

function onEdit(row: any) {
  resetForm()
  Object.assign(form, {
    id: row.id, title: row.title, author: row.author, isbn: row.isbn,
    category_id: row.category_id, publisher: row.publisher,
    publish_year: row.publish_year, total_count: row.total_count,
    summary: row.summary, cover_url: row.cover_url
  })
  coverUrlInput.value = row.cover_url || ''
  isEdit.value = true
  dialogVisible.value = true
}

function onDialogClosed() {
  resetForm()
  formRef.value?.clearValidate()
}

async function onBeforeUpload(file: File) {
  try {
    const { cover_url } = await bookApi.uploadCover(file)
    form.cover_url = cover_url
    coverUrlInput.value = ''
    ElMessage.success('封面上传成功')
  } catch (e: any) {
    ElMessage.error(e.message || '上传失败')
  }
  return false // 阻止真实上传
}

function onUrlInput(val: string) {
  if (val && !form.cover_url) {
    form.cover_url = val
  }
}

function clearCover() {
  form.cover_url = ''
  coverUrlInput.value = ''
}

function onPreviewError(e: Event) {
  ElMessage.warning('封面URL无法加载')
  ;(e.target as HTMLImageElement).style.display = 'none'
}

async function onSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      if (isEdit.value) {
        await bookApi.updateBook(form.id!, form)
        ElMessage.success('修改成功')
      } else {
        await bookApi.createBook(form)
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
  try {
    await ElMessageBox.confirm(`确定要删除《${row.title}》吗？`, '删除确认', { type: 'warning' })
  } catch {
    return
  }
  try {
    await bookApi.deleteBook(row.id)
    ElMessage.success('删除成功')
    load()
  } catch (e: any) {
    ElMessage.error(e.message || '删除失败')
  }
}

onMounted(async () => {
  await catStore.load()
  load()
})
</script>

<style scoped>
.page-title { margin: 0; font-size: 18px; color: #303133; }
.toolbar-spacer { flex: 1; }
.cover-row {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}
.cover-divider { color: #909399; }
.cover-tip { margin-left: 8px; color: #909399; font-size: 12px; }
.cover-preview {
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.cover-preview img {
  width: 80px;
  height: 110px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #ebeef5;
}
.cover-label { color: #909399; font-size: 12px; }
</style>
