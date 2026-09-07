<template>
  <div class="page-card">
    <div class="toolbar">
      <h2 class="page-title">我的收藏</h2>
      <div class="toolbar-spacer"></div>
      <el-input v-model="query.keyword" placeholder="书名/作者" clearable style="width: 220px" @keyup.enter="onSearch" @clear="onSearch" />
      <el-button type="primary" @click="onSearch">搜索</el-button>
    </div>

    <div v-loading="loading" class="fav-grid">
      <div v-for="b in list" :key="b.id" class="fav-card">
        <div class="cover-wrap" @click="goDetail(b.id)">
          <BookCover :cover-url="b.cover_url" :title="b.title" :width="100" :height="140" />
        </div>
        <div class="fav-info">
          <div class="fav-title" @click="goDetail(b.id)">{{ b.title }}</div>
          <div class="fav-author">{{ b.author }}</div>
          <div class="fav-meta">
            <el-tag size="small">{{ b.category_name }}</el-tag>
            <span :class="b.available_count > 0 ? 'status-available' : 'status-returned'">
              {{ b.available_count > 0 ? `可借 ${b.available_count}` : '已借完' }}
            </span>
          </div>
          <div class="fav-time">收藏时间：{{ formatTime(b.favorite_time) }}</div>
          <div class="fav-actions">
            <el-button size="small" @click="goDetail(b.id)">详情</el-button>
            <el-button type="danger" size="small" :icon="Delete" @click="onUnfav(b)">取消收藏</el-button>
          </div>
        </div>
      </div>
      <div v-if="!loading && list.length === 0" class="empty">
        <el-empty description="暂无收藏" />
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
import { Delete } from '@element-plus/icons-vue'
import BookCover from '@/components/BookCover.vue'
import { favoriteApi } from '@/api'
import type { PageQuery } from '@/types'

const router = useRouter()
const loading = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const query = reactive<PageQuery>({ page: 1, page_size: 10, keyword: '' })

function formatTime(iso: string) {
  if (!iso) return '-'
  return new Date(iso).toLocaleString('zh-CN', { hour12: false })
}

async function load() {
  loading.value = true
  try {
    const res = await favoriteApi.listMyFavorites(query)
    list.value = res.list
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function onSearch() { query.page = 1; load() }
function goDetail(id: number) { router.push(`/reader/books/${id}`) }

async function onUnfav(b: any) {
  try {
    await ElMessageBox.confirm(`确定取消收藏《${b.title}》吗？`, '取消收藏', { type: 'warning' })
  } catch { return }
  try {
    await favoriteApi.toggleFavorite(b.id)
    ElMessage.success('已取消收藏')
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
.fav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 14px;
  min-height: 200px;
}
.fav-card {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 12px;
  display: flex;
  gap: 12px;
  transition: box-shadow 0.2s;
}
.fav-card:hover { box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08); }
.cover-wrap { cursor: pointer; flex-shrink: 0; }
.fav-info { flex: 1; display: flex; flex-direction: column; gap: 5px; }
.fav-title {
  font-size: 15px; font-weight: 600; color: #303133; cursor: pointer;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.fav-title:hover { color: #409eff; }
.fav-author { font-size: 13px; color: #909399; }
.fav-meta { display: flex; align-items: center; gap: 10px; font-size: 13px; }
.fav-time { font-size: 12px; color: #c0c4cc; }
.fav-actions { margin-top: auto; display: flex; gap: 8px; }
.empty { grid-column: 1 / -1; }
</style>
