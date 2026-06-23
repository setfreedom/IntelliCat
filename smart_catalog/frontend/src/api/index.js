import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000
})

api.interceptors.response.use(
  response => response,
  error => {
    const msg = error.response?.data?.error || error.message || '请求失败'
    ElMessage.error(msg)
    return Promise.reject(error)
  }
)

export function getLines() { return api.get('/lines') }
export function createLine(name) { return api.post('/lines', { name }) }
export function updateLine(id, name) { return api.put(`/lines/${id}`, { name }) }
export function deleteLine(id) { return api.delete(`/lines/${id}`) }

export function getMappings(lineId) { return api.get(`/lines/${lineId}/mappings`) }
export function addCatalogDept(lineId, department) { return api.post(`/lines/${lineId}/catalog-depts`, { department }) }
export function deleteCatalogDept(lineId, mappingId) { return api.delete(`/lines/${lineId}/catalog-depts/${mappingId}`) }
export function addDutyDept(lineId, department) { return api.post(`/lines/${lineId}/duty-depts`, { department }) }
export function deleteDutyDept(lineId, mappingId) { return api.delete(`/lines/${lineId}/duty-depts/${mappingId}`) }
export function lookupCatalogLine(department) { return api.post('/lines/lookup-catalog-line', { department }) }
export function lookupDutyLine(department) { return api.post('/lines/lookup-duty-line', { department }) }

export function parseCatalog(file) {
  const fd = new FormData()
  fd.append('file', file)
  return api.post('/catalogs/parse', fd)
}
export function saveCatalogs(rows) { return api.post('/catalogs/save', { rows }) }
export function getCatalogs() { return api.get('/catalogs') }
export function updateCatalog(id, data) { return api.put(`/catalogs/${id}`, data) }
export function deleteCatalog(id) { return api.delete(`/catalogs/${id}`) }

export function parseDuties(file) {
  const fd = new FormData()
  fd.append('file', file)
  return api.post('/duties/parse', fd)
}
export function saveDuties(rows) { return api.post('/duties/save', { rows }) }
export function getDuties() { return api.get('/duties') }
export function deleteDuty(id) { return api.delete(`/duties/${id}`) }
export function matchDuties(dutyIds) { return api.post('/duties/match', { duty_ids: dutyIds }) }

export function getResults(search) { return api.get('/results', { params: { search } }) }
export function updateResult(id, data) { return api.put(`/results/${id}`, data) }
export function deleteResult(id) { return api.delete(`/results/${id}`) }
export function exportResults(search) { return api.get('/results/export', { params: { search } }) }

export default api
