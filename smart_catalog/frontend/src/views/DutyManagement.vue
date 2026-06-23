<template>
  <div>
    <!-- 操作栏 -->
    <el-card class="page-header">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span style="font-weight: 600; color: #303133; white-space: nowrap;">职能管理</span>
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
          <el-button type="success" :icon="Check" :disabled="selectedDepts.length === 0" @click="handleBatchMatch" :loading="matching">
            批量智能匹配（已选 {{ selectedDepts.length }} 个部门）
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 铁律一提示 -->
    <el-alert
      v-if="violations.length > 0"
      :title="`铁律一校验未通过：存在 ${violations.length} 个违规项，请先修正映射关系`"
      type="error"
      :closable="false"
      show-icon
      style="margin-bottom: 16px; border-radius: 8px;"
    >
      <template #default>
        <ul style="margin: 8px 0 0; padding-left: 20px;">
          <li v-for="(v, i) in violations" :key="i">{{ v }}</li>
        </ul>
      </template>
    </el-alert>

    <!-- 上传预览表格 -->
    <el-card v-if="previewRows.length > 0" class="page-table" style="margin-bottom: 16px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span style="font-weight: 600;">上传预览（共 {{ previewRows.length }} 条）</span>
        <div>
          <el-button size="small" @click="previewRows = []">取消</el-button>
          <el-button size="small" type="primary" :disabled="hasViolations" @click="handleSavePreview" :loading="saving">保存数据</el-button>
        </div>
      </div>
      <el-table :data="previewRows" stripe border max-height="400" size="small" style="width: 100%">
        <el-table-column type="index" label="序号" width="70" />
        <el-table-column prop="department" label="部门名称" width="180" />
        <el-table-column prop="inner_org" label="内设机构" width="180" />
        <el-table-column prop="duty_name" label="职能名称" min-width="240" />
        <el-table-column label="条线" width="220">
          <template #default="{ row }">
            <el-tag v-if="row.line_name" size="small" type="success">{{ row.line_name }}</el-tag>
            <div v-else-if="row._error && row._error.includes('0条映射')">
              <el-button size="small" type="warning" @click="showAddLineForDept(row)">新增条线</el-button>
            </div>
            <el-tag v-else size="small" type="danger">未映射</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="校验状态" width="180">
          <template #default="{ row }">
            <el-tag v-if="row._valid" size="small" type="success">通过</el-tag>
            <el-tag v-else size="small" type="danger">{{ row._error ? '违规' : '未校验' }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 已保存的职能列表（按部门分组） -->
    <el-card class="page-table">
      <div style="margin-bottom: 12px; font-weight: 600; color: #606266;">
        已保存职能数据（共 {{ savedDuties.length }} 条，{{ departmentGroups.length }} 个部门）
      </div>
      <el-table :data="departmentGroups" v-loading="loading" stripe border style="width: 100%" @selection-change="onDeptSelectionChange" row-key="department">
        <el-table-column type="selection" width="45" />
        <el-table-column type="expand">
          <template #default="{ row }">
            <div style="padding: 8px 16px;">
              <el-table :data="row.duties" size="small" stripe>
                <el-table-column type="index" label="序号" width="60" />
                <el-table-column prop="inner_org" label="内设机构" min-width="200" />
                <el-table-column prop="duty_name" label="职能名称" min-width="240" />
                <el-table-column label="条线" width="120">
                  <template #default="{ row: d }">
                    <el-tag v-if="d.line_name" size="small">{{ d.line_name }}</el-tag>
                    <el-tag v-else size="small" type="info">未映射</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="90">
                  <template #default="{ row: d }">
                    <el-button size="small" type="danger" link @click="handleDeleteDuty(d)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="department" label="部门名称" min-width="180" />
        <el-table-column label="条线" width="130">
          <template #default="{ row }">
            <el-tag v-if="row.line_name" size="small">{{ row.line_name }}</el-tag>
            <el-tag v-else size="small" type="info">未映射</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="职能数" width="100" align="center">
          <template #default="{ row }"> {{ row.duties.length }} </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="handleSingleMatch(row)">智能匹配</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="savedDuties.length === 0 && previewRows.length === 0" style="text-align:center;padding:60px 0;color:#909399;">
        <el-icon :size="48"><Document /></el-icon>
        <p style="margin-top:12px;">暂无数据，请上传职能清单文件</p>
      </div>
    </el-card>

    <!-- 匹配进度对话框 -->
    <el-dialog v-model="matchProgressVisible" title="智能匹配进度" width="500px" :close-on-click-modal="false" :close-on-press-escape="false">
      <div v-loading="matchLoading">
        <el-steps :active="matchStep" direction="vertical" space="60">
          <el-step title="铁律一校验" description="校验所有职能部门映射的唯一性" />
          <el-step title="按条线分组" description="按映射条线对职能进行分组" />
          <el-step title="执行匹配" :description="matchStatusText" />
        </el-steps>
        <div v-if="matchResult" style="margin-top: 16px;">
          <el-alert
            :title="matchResult.message"
            :type="matchResult.results_count > 0 ? 'success' : 'info'"
            :closable="false"
            show-icon
          />
          <div v-if="matchResult.progress" style="margin-top: 12px;">
            <div v-for="p in matchResult.progress" :key="p.line" style="display:flex;align-items:center;gap:8px;padding:4px 0;">
              <el-tag size="small" :type="p.status === '成功' ? 'success' : p.status === '跳过' ? 'info' : 'danger'">
                {{ p.status }}
              </el-tag>
              <span>{{ p.line }}</span>
              <span v-if="p.catalog_count" style="color:#909399;">(目录{{ p.catalog_count }}条 / 职能{{ p.duty_count }}条)</span>
              <span v-if="p.reason" style="color:#909399;">— {{ p.reason }}</span>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="matchProgressVisible = false" :disabled="matchLoading">关闭</el-button>
        <el-button v-if="matchResult" type="primary" @click="goToResults">查看匹配结果</el-button>
      </template>
    </el-dialog>
    <!-- 新增条线对话框 -->
    <el-dialog v-model="addLineVisible" title="新增条线并建立映射" width="420px" :close-on-click-modal="false">
      <el-form @submit.prevent="handleAddLineAndMap">
        <el-form-item label="部门名称">
          <el-input :model-value="pendingDept" disabled />
        </el-form-item>
        <el-form-item label="条线名称">
          <el-input v-model="newLineName" placeholder="输入新条线名称" maxlength="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addLineVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAddLineAndMap" :loading="addLineLoading">创建并映射</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Check, Document, Download } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { getLines, createLine, addDutyDept, parseDuties, saveDuties, getDuties, deleteDuty, matchDuties } from '../api/index.js'

const router = useRouter()
const loading = ref(false)
const uploading = ref(false)
const saving = ref(false)
const previewRows = ref([])
const violations = ref([])
const hasViolations = ref(false)
const savedDuties = ref([])
const selectedDepts = ref([])

const departmentGroups = computed(() => {
  const map = {}
  for (const d of savedDuties.value) {
    const key = d.department || '(空)'
    if (!map[key]) {
      map[key] = { department: d.department, line_id: d.line_id, line_name: d.line_name, duties: [] }
    }
    map[key].duties.push(d)
  }
  return Object.values(map)
})

const matching = ref(false)
const matchProgressVisible = ref(false)
const matchLoading = ref(false)
const matchStep = ref(0)
const matchStatusText = ref('')
const matchResult = ref(null)

const addLineVisible = ref(false)
const newLineName = ref('')
const addLineLoading = ref(false)
const pendingDept = ref('')

function showAddLineForDept(row) {
  pendingDept.value = row.department
  newLineName.value = ''
  addLineVisible.value = true
}

async function handleAddLineAndMap() {
  const name = newLineName.value.trim()
  if (!name) { ElMessage.warning('请输入条线名称'); return }
  addLineLoading.value = true
  try {
    const lineRes = await createLine(name)
    const line = lineRes.data
    await addDutyDept(line.id, pendingDept.value)
    // 更新预览行中该部门的映射
    for (const r of previewRows.value) {
      if (r.department === pendingDept.value) {
        r.line_id = line.id
        r.line_name = line.name
        r._valid = true
        r._error = null
      }
    }
    // 重新汇总违规项
    violations.value = previewRows.value.filter(r => !r._valid).map(r => r._error).filter(Boolean)
    hasViolations.value = violations.value.length > 0
    addLineVisible.value = false
    ElMessage.success(`已创建条线「${name}」并建立映射`)
  } catch {} finally {
    addLineLoading.value = false
  }
}

function downloadTemplate() {
  window.open('/api/duties/template')
}

async function handleUpload(file) {
  uploading.value = true
  try {
    const res = await parseDuties(file)
    const data = res.data
    previewRows.value = data.rows
    violations.value = data.violations || []
    hasViolations.value = data.has_violations

    if (data.has_violations) {
      ElMessage.warning(`铁律一校验未通过，存在 ${violations.value.length} 个违规项`)
    } else {
      ElMessage.success(`解析成功，共 ${data.total} 条，全部通过铁律一校验`)
    }
  } catch {
    // handled by interceptor
  } finally {
    uploading.value = false
  }
  return false
}

async function handleSavePreview() {
  if (hasViolations.value) {
    ElMessageBox.alert('存在铁律一违规项，无法保存。请先在条线管理中修正映射关系。', '保存失败', { type: 'error' })
    return
  }
  saving.value = true
  try {
    const res = await saveDuties(previewRows.value)
    ElMessage.success(res.data.message)
    previewRows.value = []
    violations.value = []
    hasViolations.value = false
    await loadSavedDuties()
  } finally {
    saving.value = false
  }
}

async function loadSavedDuties() {
  loading.value = true
  try {
    const res = await getDuties()
    savedDuties.value = res.data
  } finally {
    loading.value = false
  }
}

async function handleDeleteDuty(row) {
  try {
    await ElMessageBox.confirm(`确定删除该职能记录吗？`, '确认删除', { type: 'warning' })
    await deleteDuty(row.id)
    ElMessage.success('删除成功')
    await loadSavedDuties()
  } catch {}
}

function onDeptSelectionChange(rows) {
  selectedDepts.value = rows
}

async function handleSingleMatch(group) {
  if (!group.duties || group.duties.length === 0) {
    ElMessage.warning('该部门下无职能数据')
    return
  }
  matchProgressVisible.value = true
  matchLoading.value = true
  matchStep.value = 0
  matchStatusText.value = '准备中...'
  matchResult.value = null
  try {
    matchStep.value = 1
    await new Promise(r => setTimeout(r, 300))
    matchStep.value = 2
    await new Promise(r => setTimeout(r, 200))
    matchStep.value = 3
    matchStatusText.value = '正在匹配...'
    matching.value = true
    const dutyIds = group.duties.map(d => d.id)
    const res = await matchDuties(dutyIds)
    matchResult.value = res.data
    matchStatusText.value = `匹配完成，共生成 ${res.data.results_count} 条结果`
    ElMessage.success('匹配完成')
  } catch (e) {
    matchStatusText.value = '匹配失败'
    if (e.response?.data?.violations) {
      matchResult.value = { message: '铁律一校验未通过', progress: e.response.data.violations.map(v => ({ line: v, status: '失败', reason: v })), results_count: 0 }
    }
  } finally {
    matchLoading.value = false
    matching.value = false
  }
}

async function handleBatchMatch() {
  if (selectedDepts.value.length === 0) {
    ElMessage.warning('请先勾选要匹配的部门')
    return
  }
  const dutyIds = selectedDepts.value.flatMap(g => g.duties.map(d => d.id))
  if (dutyIds.length === 0) {
    ElMessage.warning('所选部门下无职能数据')
    return
  }
  matchProgressVisible.value = true
  matchLoading.value = true
  matchStep.value = 0
  matchStatusText.value = '准备中...'
  matchResult.value = null
  try {
    matchStep.value = 1
    await new Promise(r => setTimeout(r, 500))
    matchStep.value = 2
    await new Promise(r => setTimeout(r, 300))
    matchStep.value = 3
    matchStatusText.value = '正在调用外部接口进行匹配...'
    matching.value = true
    const res = await matchDuties(dutyIds)
    matchResult.value = res.data
    matchStatusText.value = `匹配完成，共生成 ${res.data.results_count} 条结果`
    matchStep.value = 3
    ElMessage.success('匹配完成')
  } catch (e) {
    matchStatusText.value = '匹配失败'
    if (e.response?.data?.violations) {
      matchResult.value = { message: '铁律一校验未通过', progress: e.response.data.violations.map(v => ({ line: v, status: '失败', reason: v })), results_count: 0 }
    }
  } finally {
    matchLoading.value = false
    matching.value = false
  }
}

function goToResults() {
  matchProgressVisible.value = false
  router.push('/results')
}

onMounted(loadSavedDuties)
</script>
