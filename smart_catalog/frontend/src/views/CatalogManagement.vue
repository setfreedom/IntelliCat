<template>
  <div>
    <!-- 操作栏 -->
    <el-card class="page-header">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span style="font-weight: 600; color: #303133; white-space: nowrap;">目录梳理</span>
        <div style="display: flex; gap: 8px; flex-shrink: 0;">
          <el-button :icon="Download" @click="downloadTemplate">下载模板</el-button>
          <el-upload
            :show-file-list="false"
            :before-upload="handleUpload"
            accept=".xlsx,.xls,.csv"
          >
            <el-button type="primary" :icon="Upload" :loading="uploading">
              {{ uploading ? '解析中...' : '上传Excel/CSV' }}
            </el-button>
          </el-upload>
          <el-button type="success" :icon="Check" :disabled="!hasData" @click="handleSave" :loading="saving">
            保存数据
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="page-table">
      <el-table :data="rows" v-loading="loading" stripe border max-height="600" style="width: 100%">
        <el-table-column type="index" label="序号" width="70" fixed />
        <el-table-column label="目录名称" min-width="240">
          <template #default="{ row }">
            <el-input v-model="row.name" size="small" placeholder="目录名称" disabled />
          </template>
        </el-table-column>
        <el-table-column label="来源部门" width="180">
          <template #default="{ row }">
            <el-input v-model="row.department" size="small" disabled />
          </template>
        </el-table-column>
        <el-table-column label="条线" width="240" fixed="right">
          <template #default="{ row }">
            <div style="display: flex; align-items: center; gap: 4px;">
              <el-select
                v-model="row.line_id"
                placeholder="请选择条线"
                size="small"
                filterable
                style="flex:1"
                :class="{ 'line-selected': row.line_id }"
                @change="(val) => handleLineSelect(row, val)"
              >
                <el-option
                  v-for="l in allLines"
                  :key="l.id"
                  :label="l.name"
                  :value="l.id"
                />
                <template #footer>
                  <div style="padding: 8px; border-top: 1px solid #eee;">
                    <el-button size="small" type="primary" link @click="showAddLineFromCatalog(row)">
                      新增条线
                    </el-button>
                  </div>
                </template>
              </el-select>
              <el-tooltip v-if="row._line_message" :content="row._line_message" placement="top">
                <el-icon style="color: var(--el-color-warning); cursor: pointer;"><WarningFilled /></el-icon>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="主要字段项" min-width="250">
          <template #default="{ row }">
            <div style="display: flex; flex-wrap: wrap; gap: 4px;">
              <el-tag
                v-for="(f, fi) in row.fields"
                :key="fi"
                size="small"
                type="info"
                effect="plain"
              >{{ f }}</el-tag>
              <span v-if="!row.fields || row.fields.length === 0" style="color:#909399;">无字段项</span>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <div v-if="rows.length === 0" style="text-align:center;padding:60px 0;color:#909399;">
        <el-icon :size="48"><FolderOpened /></el-icon>
        <p style="margin-top:12px;">暂无数据，请上传 Excel/CSV 文件</p>
      </div>
    </el-card>

    <!-- 新增条线对话框（快捷入口） -->
    <el-dialog v-model="addLineVisible" title="新增条线" width="400px" :close-on-click-modal="false">
      <el-form :model="addLineForm" label-width="80px">
        <el-form-item label="条线名称">
          <el-input v-model="addLineForm.name" placeholder="输入新条线名称" maxlength="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addLineVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAddLine" :loading="addLineLoading">创建并选择</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Check, WarningFilled, FolderOpened, Download } from '@element-plus/icons-vue'
import { getLines, createLine, addCatalogDept, parseCatalog, saveCatalogs, getCatalogs, lookupCatalogLine } from '../api/index.js'

const loading = ref(false)
const uploading = ref(false)
const saving = ref(false)
const rows = ref([])
const allLines = ref([])
const hasData = computed(() => rows.value.length > 0)

const addLineVisible = ref(false)
const addLineForm = ref({ name: '' })
const addLineLoading = ref(false)
const targetRow = ref(null)

async function loadLines() {
  try {
    const res = await getLines()
    allLines.value = res.data
  } catch {}
}

async function loadSavedCatalogs() {
  try {
    const res = await getCatalogs()
    if (res.data.length > 0) {
      rows.value = res.data.map(c => ({
        ...c,
        fields: c.fields || [],
        _line_message: '',
        _line_suggestion: null,
        _matched_lines: c.line_id ? [{ id: c.line_id, name: c.line_name }] : []
      }))
    }
  } catch {}
}

function downloadTemplate() {
  window.open('/api/catalogs/template')
}

async function handleUpload(file) {
  uploading.value = true
  try {
    const res = await parseCatalog(file)
    rows.value = res.data.rows
    ElMessage.success(`解析成功，共 ${res.data.total} 条记录`)
    for (const row of rows.value) {
      if (row.department) {
        try {
          const lr = await lookupCatalogLine(row.department)
          const ld = lr.data
          row._line_message = ld.message
          row._line_suggestion = ld.suggestion
          row._matched_lines = ld.lines
          if (ld.count === 1 && ld.suggestion) {
            row.line_id = ld.suggestion.id
            row._line_message = ''
          }
        } catch {}
      }
    }
  } catch (e) {
    // 错误已在拦截器中处理
  } finally {
    uploading.value = false
  }
  return false
}

async function handleSave() {
  const invalid = rows.value.filter(r => !r.line_id)
  if (invalid.length > 0) {
    const names = invalid.slice(0, 5).map(r => `「${r.name || '未命名'}」`).join('、')
    ElMessageBox.alert(`以下目录未选择条线：${names}`, '保存失败', { type: 'warning', confirmButtonText: '知道了' })
    return
  }
  for (const r of rows.value) {
    if (!allLines.value.find(l => l.id === r.line_id)) {
      ElMessageBox.alert(`目录「${r.name}」选择的条线无效`, '保存失败', { type: 'error' })
      return
    }
  }

  saving.value = true
  try {
    // 保存前去除前端临时字段
    const data = rows.value.map(r => ({
      sequence: r.sequence,
      name: r.name,
      department: r.department,
      line_id: r.line_id,
      fields: r.fields || []
    }))
    await saveCatalogs(data)
    ElMessage.success('保存成功')
    await loadSavedCatalogs()
  } finally {
    saving.value = false
  }
}

async function handleLineSelect(row, lineId) {
  if (!lineId) return
  row._line_message = ''
  const dept = row.department
  if (!dept) return
  if (row._matched_lines && row._matched_lines.length > 0) return
  const line = allLines.value.find(l => l.id === lineId)
  try {
    await addCatalogDept(lineId, dept)
    row._matched_lines = [{ id: lineId, name: line?.name || '' }]
  } catch {
    // 映射建立失败不影响选中
  }
}

function showAddLineFromCatalog(row) {
  targetRow.value = row
  addLineForm.value = { name: '' }
  addLineVisible.value = true
}

async function handleAddLine() {
  const name = addLineForm.value.name.trim()
  if (!name) {
    ElMessage.warning('请输入条线名称')
    return
  }
  addLineLoading.value = true
  try {
    const res = await createLine(name)
    const line = res.data
    allLines.value.push(line)
    if (targetRow.value) {
      targetRow.value.line_id = line.id
      targetRow.value._line_message = ''
      // 自动建立映射
      const dept = targetRow.value.department
      if (dept && (!targetRow.value._matched_lines || targetRow.value._matched_lines.length === 0)) {
        try {
          await addCatalogDept(line.id, dept)
          targetRow.value._matched_lines = [{ id: line.id, name: line.name }]
        } catch {}
      }
    }
    addLineVisible.value = false
    ElMessage.success(`已创建条线「${name}」并选中`)
  } finally {
    addLineLoading.value = false
  }
}

onMounted(() => { loadLines(); loadSavedCatalogs() })
</script>

<style scoped>
.line-selected :deep(.el-select__wrapper) {
  border-color: var(--el-color-success);
}
</style>
