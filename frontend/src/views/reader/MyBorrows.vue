<template>
  <div class="page-card">
    <div class="toolbar">
      <h2 class="page-title">我的借阅</h2>
      <div class="toolbar-spacer"></div>
      <el-select v-model="query.status" placeholder="全部状态" clearable style="width: 130px" @change="onSearch">
        <el-option label="借阅中" value="borrowed" />
        <el-option label="已归还" value="returned" />
        <el-option label="逾期" value="overdue" />
      </el-select>
      <el-button type="primary" @click="onSearch">查询</el-button>
    </div>

    <el-table :data="list" v-loading="loading" border stripe style="width: 100%" :row-class-name="rowClass">
      <el-table-column prop="id" label="编号" width="70" align="center" />
      <el-table-column label="图书" min-width="220" show-overflow-tooltip>
        <template #default="{ row }">
          <div class="book-cell">
            <BookCover :cover-url="row.book_cover" :title="row.book_title" :width="36" :height="48" />
            <div class="book-cell-info">
              <div class="book-cell-title">{{ row.book_title }}</div>
              <div class="book-cell-isbn">{{ row.book_isbn }}</div>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="借出时间" min-width="160">
        <template #default="{ row }">{{ formatTime(row.borrow_time) }}</template>
      </el-table-column>
      <el-table-column label="应还时间" min-width="160">
        <template #default="{ row }">
          <span :class="row.status === 'overdue' ? 'status-overdue' : ''">{{ formatTime(row.due_time) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="实际归还时间" min-width="160">
        <template #default="{ row }">{{ row.return_time ? formatTime(row.return_time) : '—' }}</template>
      </el-table-column>
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)" effect="dark">
            {{ statusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="110" fixed="right">
        <template #default="{ row }">
          <el-button
            v-if="row.status !== 'returned'"
            link type="success" size="small"
            @click="onReturn(row)"
          >归还</el-button>
          <span v-else class="status-returned">已归还</span>
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import BookCover from '@/components/BookCover.vue'
import { borrowApi } from '@/api'
import type { PageQuery, BorrowStatus } from '@/types'

const loading = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const query = reactive<PageQuery>({ page: 1, page_size: 10, status: null })

function formatTime(iso: string) {
  if (!iso) return '-'
  return new Date(iso).toLocaleString('zh-CN', { hour12: false })
}
function statusText(s: BorrowStatus) {
  return { borrowed: '借阅中', returned: '已归还', overdue: '逾期' }[s]
}
function statusType(s: BorrowStatus): any {
  return { borrowed: 'warning', returned: 'info', overdue: 'danger' }[s]
}
function rowClass({ row }: any) {
  return row.status === 'overdue' ? 'row-overdue' : ''
}

async function load() {
  loading.value = true
  try {
    const res = await borrowApi.listMyRecords(query)
    list.value = res.list
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function onSearch() { query.page = 1; load() }

async function onReturn(row: any) {
  try {
    await ElMessageBox.confirm(`确定归还《${row.book_title}》吗？`, '归还确认', { type: 'warning' })
  } catch { return }
  try {
    await borrowApi.returnBook(row.id)
    ElMessage.success('归还成功')
    load()
  } catch (e: any) {
    ElMessage.error(e.message || '归还失败')
  }
}

onMounted(load)
</script>

<style scoped>
.page-title { margin: 0; font-size: 18px; color: #303133; }
.toolbar-spacer { flex: 1; }
.book-cell { display: flex; align-items: center; gap: 10px; }
.book-cell-info { display: flex; flex-direction: column; }
.book-cell-title { font-size: 14px; color: #303133; }
.book-cell-isbn { font-size: 12px; color: #909399; }
</style>
