<template>
  <div class="page-card">
    <div class="toolbar">
      <h2 class="page-title">借阅记录</h2>
      <div class="toolbar-spacer"></div>
      <el-select v-model="query.status" placeholder="全部状态" clearable style="width: 130px" @change="onSearch">
        <el-option label="借阅中" value="borrowed" />
        <el-option label="已归还" value="returned" />
        <el-option label="逾期" value="overdue" />
      </el-select>
      <el-input v-model="query.reader_keyword" placeholder="读者用户名/姓名" clearable style="width: 180px" @keyup.enter="onSearch" @clear="onSearch" />
      <el-input v-model="query.book_keyword" placeholder="书名/ISBN" clearable style="width: 180px" @keyup.enter="onSearch" @clear="onSearch" />
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="-"
        start-placeholder="借出起"
        end-placeholder="借出止"
        value-format="YYYY-MM-DD"
        style="width: 240px"
        @change="onDateChange"
      />
      <el-button type="primary" @click="onSearch">搜索</el-button>
      <el-button @click="onReset">重置</el-button>
    </div>

    <el-table :data="list" v-loading="loading" border stripe style="width: 100%" :row-class-name="rowClass">
      <el-table-column prop="id" label="编号" width="70" align="center" />
      <el-table-column prop="reader_name" label="读者" min-width="100" />
      <el-table-column prop="reader_username" label="用户名" min-width="120" show-overflow-tooltip />
      <el-table-column prop="book_title" label="图书" min-width="180" show-overflow-tooltip />
      <el-table-column prop="book_isbn" label="ISBN" min-width="150" show-overflow-tooltip />
      <el-table-column label="借出时间" min-width="160">
        <template #default="{ row }">{{ formatTime(row.borrow_time) }}</template>
      </el-table-column>
      <el-table-column label="应还时间" min-width="160">
        <template #default="{ row }">
          <span :class="isOverdueRow(row) ? 'status-overdue' : ''">{{ formatTime(row.due_time) }}</span>
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
          >办理归还</el-button>
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
import { borrowApi } from '@/api'
import type { PageQuery, BorrowStatus } from '@/types'

const loading = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const dateRange = ref<[string, string] | null>(null)
const query = reactive<PageQuery>({
  page: 1, page_size: 10,
  status: null, reader_keyword: '', book_keyword: '',
  start_time: null, end_time: null
})

function formatTime(iso: string) {
  if (!iso) return '-'
  return new Date(iso).toLocaleString('zh-CN', { hour12: false })
}

function statusText(s: BorrowStatus) {
  return { borrowed: '借阅中', returned: '已归还', overdue: '逾期' }[s]
}
function statusType(s: BorrowStatus): 'success' | 'info' | 'warning' | 'danger' {
  return { borrowed: 'warning', returned: 'info', overdue: 'danger' }[s] as any
}
function isOverdueRow(row: any) {
  return row.status === 'overdue'
}
function rowClass({ row }: any) {
  return row.status === 'overdue' ? 'row-overdue' : ''
}

function onDateChange(val: [string, string] | null) {
  if (val) {
    query.start_time = val[0] + 'T00:00:00'
    query.end_time = val[1] + 'T23:59:59'
  } else {
    query.start_time = null
    query.end_time = null
  }
  onSearch()
}

async function load() {
  loading.value = true
  try {
    const res = await borrowApi.listAllRecords(query)
    list.value = res.list
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function onSearch() { query.page = 1; load() }
function onReset() {
  query.status = null
  query.reader_keyword = ''
  query.book_keyword = ''
  dateRange.value = null
  query.start_time = null
  query.end_time = null
  onSearch()
}

async function onReturn(row: any) {
  try {
    await ElMessageBox.confirm(`确定为「${row.reader_name}」办理《${row.book_title}》归还吗？`, '办理归还', { type: 'warning' })
  } catch {
    return
  }
  try {
    await borrowApi.returnBook(row.id)
    ElMessage.success('归还成功')
    load()
  } catch (e: any) {
    ElMessage.error(e.message || '操作失败')
  }
}

onMounted(load)
</script>

<style scoped>
.page-title { margin: 0; font-size: 18px; color: #303133; }
.toolbar-spacer { flex: 1; }
</style>
