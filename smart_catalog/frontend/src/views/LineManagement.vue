<template>
  <div>
    <!-- 操作栏 -->
    <el-card class="page-header">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span class="page-title">条线管理</span>
        <el-button type="primary" @click="showAddDialog" :icon="Plus">新增条线</el-button>
      </div>
    </el-card>

    <!-- 条线列表 -->
    <el-card class="page-table">
      <el-table :data="lines" v-loading="loading" stripe border style="width: 100%">
        <el-table-column type="index" label="序号" width="70" fixed />
        <el-table-column prop="name" label="条线名称" min-width="200" />
        <el-table-column label="目录部门映射数" min-width="160">
          <template #default="{ row }">
            <el-tag size="small" :type="row._catalog_count > 0 ? 'success' : 'info'">
              {{ row._catalog_count || 0 }} 个部门
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="职能部门映射数" min-width="160">
          <template #default="{ row }">
            <el-tag size="small" :type="row._duty_count > 0 ? 'warning' : 'info'">
              {{ row._duty_count || 0 }} 个部门
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="showEditDialog(row)" :icon="Edit">编辑</el-button>
            <el-button size="small" @click="showMappings(row)" :icon="Setting">映射</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)" :icon="Delete">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑条线' : '新增条线'" width="420px" :close-on-click-modal="false">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px" @submit.prevent="handleSave">
        <el-form-item label="条线名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入条线名称" maxlength="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" native-type="submit" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 映射管理对话框 -->
    <el-dialog v-model="mappingVisible" :title="`映射管理 — ${currentLine?.name}`" width="700px" :close-on-click-modal="false" @closed="loadLines">
      <el-tabs type="border-card">
        <el-tab-pane label="目录部门映射（一对多）">
          <div style="display: flex; gap: 8px; margin-bottom: 12px;">
            <el-input v-model="newCatalogDept" placeholder="输入目录部门名称" style="flex:1" clearable @keyup.enter="handleAddCatalogDept" />
            <el-button type="primary" @click="handleAddCatalogDept" :disabled="!newCatalogDept.trim()">添加</el-button>
          </div>
          <el-table :data="catalogDepts" stripe size="small" max-height="300">
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column prop="department" label="目录部门" min-width="160" />
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button size="small" type="danger" link @click="handleDeleteCatalogDept(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="catalogDepts.length === 0" class="empty-mapping">暂无映射</div>
        </el-tab-pane>
        <el-tab-pane label="职能部门映射（一对一）">
          <el-alert title="铁律一：每个职能部门只能映射到一个条线（唯一映射）" type="warning" :closable="false" show-icon style="margin-bottom:12px;" />
          <div style="display: flex; gap: 8px; margin-bottom: 12px;">
            <el-input v-model="newDutyDept" placeholder="输入职能部门名称" style="flex:1" clearable @keyup.enter="handleAddDutyDept" />
            <el-button type="primary" @click="handleAddDutyDept" :disabled="!newDutyDept.trim()">添加</el-button>
          </div>
          <el-table :data="dutyDepts" stripe size="small" max-height="300">
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column prop="department" label="职能部门" min-width="160" />
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button size="small" type="danger" link @click="handleDeleteDutyDept(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="dutyDepts.length === 0" class="empty-mapping">暂无映射</div>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Setting, Delete } from '@element-plus/icons-vue'
import { getLines, createLine, updateLine, deleteLine, getMappings, addCatalogDept, deleteCatalogDept, addDutyDept, deleteDutyDept } from '../api/index.js'

const loading = ref(false)
const lines = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const form = ref({ name: '' })
const formRef = ref(null)
const editId = ref(null)

const mappingVisible = ref(false)
const currentLine = ref(null)
const catalogDepts = ref([])
const dutyDepts = ref([])
const newCatalogDept = ref('')
const newDutyDept = ref('')

const rules = {
  name: [{ required: true, message: '请输入条线名称', trigger: 'blur' }]
}

async function loadLines() {
  loading.value = true
  try {
    const res = await getLines()
    const lineData = res.data
    // 获取每个条线的映射计数
    for (const l of lineData) {
      try {
        const m = await getMappings(l.id)
        l._catalog_count = m.data.catalog_depts.length
        l._duty_count = m.data.duty_depts.length
      } catch {
        l._catalog_count = 0
        l._duty_count = 0
      }
    }
    lines.value = lineData
  } finally {
    loading.value = false
  }
}

function showAddDialog() {
  isEdit.value = false
  editId.value = null
  form.value = { name: '' }
  dialogVisible.value = true
}

function showEditDialog(row) {
  isEdit.value = true
  editId.value = row.id
  form.value = { name: row.name }
  dialogVisible.value = true
}

async function handleSave() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (isEdit.value) {
      await updateLine(editId.value, form.value.name)
      ElMessage.success('更新成功')
    } else {
      await createLine(form.value.name)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    await loadLines()
  } finally {
    saving.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除条线「${row.name}」吗？`, '确认删除', { type: 'warning' })
    await deleteLine(row.id)
    ElMessage.success('删除成功')
    await loadLines()
  } catch {}
}

async function showMappings(row) {
  currentLine.value = row
  catalogDepts.value = []
  dutyDepts.value = []
  newCatalogDept.value = ''
  newDutyDept.value = ''
  mappingVisible.value = true
  try {
    const res = await getMappings(row.id)
    catalogDepts.value = res.data.catalog_depts
    dutyDepts.value = res.data.duty_depts
  } catch {}
}

async function handleAddCatalogDept() {
  const dept = newCatalogDept.value.trim()
  if (!dept) return
  try {
    const res = await addCatalogDept(currentLine.value.id, dept)
    catalogDepts.value.push(res.data)
    newCatalogDept.value = ''
    ElMessage.success('添加成功')
  } catch {}
}

async function handleDeleteCatalogDept(row) {
  try {
    await deleteCatalogDept(currentLine.value.id, row.id)
    catalogDepts.value = catalogDepts.value.filter(d => d.id !== row.id)
    ElMessage.success('删除成功')
  } catch {}
}

async function handleAddDutyDept() {
  const dept = newDutyDept.value.trim()
  if (!dept) return
  try {
    const res = await addDutyDept(currentLine.value.id, dept)
    dutyDepts.value.push(res.data)
    newDutyDept.value = ''
    ElMessage.success('添加成功')
  } catch {}
}

async function handleDeleteDutyDept(row) {
  try {
    await deleteDutyDept(currentLine.value.id, row.id)
    dutyDepts.value = dutyDepts.value.filter(d => d.id !== row.id)
    ElMessage.success('删除成功')
  } catch {}
}

onMounted(loadLines)
</script>

<style scoped>
.empty-mapping {
  text-align: center;
  color: #909399;
  padding: 20px;
}
</style>
