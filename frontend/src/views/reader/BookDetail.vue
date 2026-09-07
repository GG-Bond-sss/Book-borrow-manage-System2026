<template>
  <div class="page-card" v-loading="loading">
    <div class="back-row">
      <el-button :icon="ArrowLeft" @click="router.back()">返回</el-button>
    </div>

    <div v-if="book" class="detail-grid">
      <div class="detail-cover">
        <BookCover :cover-url="book.cover_url" :title="book.title" :width="200" :height="280" />
      </div>
      <div class="detail-info">
        <h1 class="detail-title">{{ book.title }}</h1>
        <div class="detail-author">作者：{{ book.author }}</div>
        <el-descriptions :column="2" border size="default" class="desc">
          <el-descriptions-item label="ISBN">{{ book.isbn }}</el-descriptions-item>
          <el-descriptions-item label="分类">{{ book.category_name }}</el-descriptions-item>
          <el-descriptions-item label="出版社">{{ book.publisher || '—' }}</el-descriptions-item>
          <el-descriptions-item label="出版年份">{{ book.publish_year || '—' }}</el-descriptions-item>
          <el-descriptions-item label="总馆藏">{{ book.total_count }} 册</el-descriptions-item>
          <el-descriptions-item label="可借数量">
            <span :class="book.available_count > 0 ? 'status-available' : 'status-returned'">
              {{ book.available_count > 0 ? `${book.available_count} 册` : '已借完' }}
            </span>
          </el-descriptions-item>
        </el-descriptions>
        <div class="summary">
          <h3>简介</h3>
          <p>{{ book.summary || '暂无简介' }}</p>
        </div>
        <div class="actions">
          <el-button
            :type="borrowBtnType"
            size="large"
            :disabled="borrowBtnDisabled"
            @click="onBorrow"
          >{{ borrowBtnText }}</el-button>
          <el-button
            :type="favStore.isFavorited(bookId) ? 'danger' : 'default'"
            size="large"
            :icon="favStore.isFavorited(bookId) ? StarFilled : Star"
            @click="onToggleFav"
          >{{ favStore.isFavorited(bookId) ? '已收藏' : '收藏' }}</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Star, StarFilled } from '@element-plus/icons-vue'
import BookCover from '@/components/BookCover.vue'
import { useBorrowStore } from '@/stores/borrow'
import { useFavoriteStore } from '@/stores/favorite'
import { bookApi, borrowApi } from '@/api'

const route = useRoute()
const router = useRouter()

const borrowStore = useBorrowStore()
const favStore = useFavoriteStore()

const loading = ref(false)
const book = ref<any>(null)
const bookId = computed(() => Number(route.params.id))

/** 借阅按钮文本 */
const borrowBtnText = computed(() => {
  if (!book.value) return '借阅'
  if (borrowStore.isBorrowed(bookId.value)) return '已借阅'
  if (book.value.available_count <= 0) return '已借完'
  return '借阅此书'
})
/** 借阅按钮类型 */
const borrowBtnType = computed<'primary' | 'info'>(() => {
  if (!book.value) return 'primary'
  if (borrowStore.isBorrowed(bookId.value) || book.value.available_count <= 0) return 'info'
  return 'primary'
})
/** 借阅按钮禁用 */
const borrowBtnDisabled = computed(() => {
  if (!book.value) return true
  return borrowStore.isBorrowed(bookId.value) || book.value.available_count <= 0
})

async function load() {
  loading.value = true
  try {
    book.value = await bookApi.getBook(bookId.value)
  } catch (e: any) {
    ElMessage.error(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

async function onBorrow() {
  if (!book.value) return
  try {
    await ElMessageBox.confirm(`确定借阅《${book.value.title}》吗？借期30天。`, '借阅确认', { type: 'info' })
  } catch { return }
  try {
    await borrowApi.borrowBook(book.value.id)
    // 本地立即更新
    book.value.available_count = Math.max(0, book.value.available_count - 1)
    borrowStore.markBorrowed(book.value.id)
    ElMessage.success('借阅成功')
  } catch (e: any) {
    ElMessage.error(e.message || '借阅失败')
  }
}

async function onToggleFav() {
  if (!book.value) return
  try {
    const favorited = await favStore.toggle(book.value.id)
    ElMessage.success(favorited ? '已加入收藏' : '已取消收藏')
  } catch (e: any) {
    ElMessage.error(e.message || '操作失败')
  }
}

onMounted(async () => {
  // 确保借阅/收藏状态已加载（从浏览页跳来时已加载，直接刷新详情页时需加载）
  await borrowStore.load()
  await favStore.load()
  load()
})
</script>

<style scoped>
.back-row { margin-bottom: 16px; }
.detail-grid { display: flex; gap: 36px; align-items: flex-start; }
.detail-cover { flex-shrink: 0; }
.detail-info { flex: 1; }
.detail-title { margin: 0 0 6px; font-size: 24px; color: #303133; }
.detail-author { color: #909399; margin-bottom: 18px; }
.desc { margin-bottom: 20px; }
.summary h3 { margin: 0 0 8px; font-size: 16px; color: #303133; }
.summary p { color: #606266; line-height: 1.8; margin: 0; }
.actions { margin-top: 24px; display: flex; gap: 12px; }
</style>
