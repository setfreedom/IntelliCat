<template>
  <div>
    <!-- 操作栏 -->
    <el-card class="page-header">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
        <span style="font-weight: 600; color: #303133; white-space: nowrap;">匹配结果</span>
        <div style="display: flex; gap: 8px; align-items: center; flex-shrink: 0;">
          <el-input
            v-model="searchQuery"
            placeholder="搜索部门/职能/目录/条线..."
            clearable
            style="width: 260px;"
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button @click="handleSearch" :icon="Search">搜索</el-button>
          <el-button @click="handleExport" :icon="Download" :loading="exporting">导出</el-button>
        </div>
      </div>
    </el-card>

    <!-- 结果表格 -->
    <el-card class="page-table">
      <el-table :data="results" v-loading="loading" stripe border style="width: 100%">
        <el-table-column type="index" label="序号" width="70" fixed />
        <el-table-column prop="department" label="部门" width="180" />
        <el-table-column prop="_inner_org" label="内设机构" min-width="160" />
        <el-table-column label="职能" min-width="200">
          <template #default="{ row }">
            <el-input v-model="row.duty_name" size="small" @blur="handleEdit(row)" />
          </template>
        </el-table-column>
        <el-table-column label="目录名称" min-width="200">
          <template #default="{ row }">
            <el-input v-model="row.catalog_name" size="small" @blur="handleEdit(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="line_name" label="条线" width="130">
          <template #default="{ row }">
            <el-tag size="small">{{ row.line_name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <div v-if="results.length === 0 && !loading" style="text-align:center;padding:60px 0;color:#909399;">
        <el-icon :size="48"><DataBoard /></el-icon>
        <p style="margin-top:12px;">暂无匹配结果，请先在职能管理中执行智能匹配</p>
      </div>
    </el-card>

    <!-- 统计信息 -->
    <el-card v-if="results.length > 0" class="page-table" style="margin-top: 16px;">
      <div style="display: flex; gap: 32px; justify-content: center; padding: 8px 0;">
        <div style="text-align: center;">
          <div style="font-size: 32px; font-weight: 700; color: var(--el-color-primary);">{{ results.length }}</div>
          <div style="color: #909399;">匹配结果总数</div>
        </div>
        <div style="text-align: center;">
          <div style="font-size: 32px; font-weight: 700; color: var(--el-color-success);">{{ uniqueLines }}</div>
          <div style="color: #909399;">涉及条线数</div>
        </div>
        <div style="text-align: center;">
          <div style="font-size: 32px; font-weight: 700; color: var(--el-color-warning);">{{ uniqueDepts }}</div>
          <div style="color: #909399;">涉及部门数</div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Download, DataBoard } from '@element-plus/icons-vue'
import { getResults, updateResult, deleteResult, getDuties } from '../api/index.js'
import { saveAs } from 'file-saver'
import * as XLSX from 'xlsx'

const loading = ref(false)
const results = ref([])
const searchQuery = ref('')
const exporting = ref(false)
const dutyMap = ref({})  // duty_id → inner_org

const uniqueLines = computed(() => {
  const s = new Set(results.value.map(r => r.line_name).filter(Boolean))
  return s.size
})
const uniqueDepts = computed(() => {
  const s = new Set(results.value.map(r => r.department).filter(Boolean))
  return s.size
})

async function loadDutyMap() {
  try {
    const res = await getDuties()
    const map = {}
    for (const d of res.data) {
      if (d.id && d.inner_org) map[d.id] = d.inner_org
    }
    dutyMap.value = map
  } catch {}
}

async function loadResults() {
  loading.value = true
  try {
    const res = await getResults(searchQuery.value)
    results.value = res.data.map(r => ({
      ...r,
      _inner_org: dutyMap.value[r.duty_id] || ''
    }))
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  loadResults()
}

async function handleEdit(row) {
  try {
    await updateResult(row.id, {
      catalog_name: row.catalog_name,
      duty_name: row.duty_name
    })
  } catch {}
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除此匹配结果吗？`, '确认删除', { type: 'warning' })
    await deleteResult(row.id)
    results.value = results.value.filter(r => r.id !== row.id)
    ElMessage.success('删除成功')
  } catch {}
}

async function handleExport() {
  exporting.value = true
  try {
    const data = results.value.map(r => ({
      '部门': r.department,
      '内设机构': r._inner_org,
      '职能名称': r.duty_name,
      '目录名称': r.catalog_name,
      '条线': r.line_name,
    }))
    const ws = XLSX.utils.json_to_sheet(data)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '匹配结果')
    const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
    saveAs(new Blob([wbout], { type: 'application/octet-stream' }), '匹配结果.xlsx')
    ElMessage.success('导出成功')
  } catch {
    // handled by interceptor
  } finally {
    exporting.value = false
  }
}

onMounted(async () => {
  await loadDutyMap()
  await loadResults()
})
</script>
