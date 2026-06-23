import { createRouter, createWebHistory } from 'vue-router'
import LineManagement from '../views/LineManagement.vue'
import CatalogManagement from '../views/CatalogManagement.vue'
import DutyManagement from '../views/DutyManagement.vue'
import MatchResults from '../views/MatchResults.vue'

const routes = [
  { path: '/', redirect: '/catalogs' },
  { path: '/catalogs', name: 'catalogs', component: CatalogManagement, meta: { title: '目录梳理' } },
  { path: '/duties', name: 'duties', component: DutyManagement, meta: { title: '职能管理' } },
  { path: '/results', name: 'results', component: MatchResults, meta: { title: '匹配结果' } },
  { path: '/lines', name: 'lines', component: LineManagement, meta: { title: '条线管理' } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
