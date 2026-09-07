<template>
  <div class="page-card">
    <div class="toolbar">
      <h2 class="page-title">图书浏览</h2>
      <div class="toolbar-spacer"></div>
      <el-input v-model="query.keyword" placeholder="书名 / 作者 / ISBN" clearable style="width: 240px" @keyup.enter="onSearch" @clear="onSearch" />
      <el-select v-model="query.category_id" placeholder="全部分类" clearable style="width: 140px" @change="onSearch">
        <el-option v-for="c in catStore.list" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
      <el-button type="primary" @click="onSearch">搜索</el-button>
      <el-button @click="onReset">重置</el-button>
    </div>

    <div v-loading="loading" class="book-grid">
      <div v-for="b in list" :key="b.id" class="book-card">
        <div class="cover-wrap" @click="goDetail(b.id)">
          <BookCover :cover-url="b.cover_url" :title="b.title" :width="120" :height="160" />
        </div>
        <div class="book-info">
          <div class="book-title" @click="goDetail(b.id)">{{ b.title }}</div>
          <div class="book-author">{{ b.author }}</div>
          <div class="book-meta">
            <el-tag size="small" :type="b.available_count > 0 ? 'success' : 'info'">
              {{ b.category_name }}
            </el-tag>
            <span :class="b.available_count > 0 ? 'status-available' : 'status-returned'">
              {{ b.available_count > 0 ? `可借 ${b.available_count}` : '已借完' }}
            </span>
          </div>
          <div class="book-actions">
            <el-button size="small" @click="goDetail(b.id)">查看详情</el-button>
            <el-button
              type="primary"
              size="small"
              :disabled="b.available_count <= 0"
              @click="onBorrow(b)"
            >借阅</el-button>
          </div>
        </div>
      </div>
      <div v-if="!loading && list.length === 0" class="empty">
        <el-empty description="暂无图书" />
      </div>
    </div>

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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import BookCover from '@/components/BookCover.vue'
import { useCategoryStore } from '@/stores/category'
import { bookApi, borrowApi } from '@/api'
import type { PageQuery } from '@/types'

const router = useRouter()
const catStore = useCategoryStore()
const loading = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const query = reactive<PageQuery>({
  page: 1, page_size: 10, keyword: '', category_id: null
})

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

function goDetail(id: number) {
  router.push(`/reader/books/${id}`)
}

async function onBorrow(b: any) {
  try {
    await ElMessageBox.confirm(`确定借阅《${b.title}》吗？借期30天。`, '借阅确认', { type: 'info' })
  } catch {
    return
  }
  try {
    await borrowApi.borrowBook(b.id)
    ElMessage.success('借阅成功')
    load()
  } catch (e: any) {
    ElMessage.error(e.message || '借阅失败')
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
.book-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  min-height: 200px;
}
.book-card {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 14px;
  display: flex;
  gap: 14px;
  transition: box-shadow 0.2s;
}
.book-card:hover { box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08); }
.cover-wrap { cursor: pointer; flex-shrink: 0; }
.book-info { flex: 1; display: flex; flex-direction: column; gap: 6px; }
.book-title {
  font-size: 15px; font-weight: 600; color: #303133;
  cursor: pointer; overflow: hidden; text-overflow: ellipsis;
  white-space: nowrap;
}
.book-title:hover { color: #409eff; }
.book-author { font-size: 13px; color: #909399; }
.book-meta { display: flex; align-items: center; gap: 10px; font-size: 13px; }
.book-actions { margin-top: auto; display: flex; gap: 8px; }
.empty { grid-column: 1 / -1; }
</style>
