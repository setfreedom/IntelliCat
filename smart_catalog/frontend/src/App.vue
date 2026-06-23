<template>
  <el-container style="min-height: 100vh;">
    <el-aside :width="sidebarWidth" class="app-sidebar">
      <div class="app-logo">
        <div class="app-logo-icon">
          <svg viewBox="0 0 28 28" width="26" height="26" fill="none">
            <rect x="3" y="5" width="22" height="18" rx="3" stroke="#7B8CFF" stroke-width="1.8"/>
            <path d="M9 11h10M9 15h7M9 19h4" stroke="#7B8CFF" stroke-width="1.8" stroke-linecap="round"/>
            <circle cx="21" cy="21" r="5" fill="#4F6EF7" stroke="#1B1B3A" stroke-width="1.5"/>
            <path d="M19.5 21h3M21 19.5v3" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </div>
        <span class="app-logo-text">智能编目</span>
      </div>
      <el-menu
        :default-active="currentRoute"
        mode="vertical"
        router
        class="app-nav"
        text-color="rgba(255,255,255,0.65)"
        active-text-color="#fff"
      >
        <el-menu-item index="/catalogs">
          <el-icon><FolderOpened /></el-icon>
          <span>目录梳理</span>
        </el-menu-item>
        <el-menu-item index="/duties">
          <el-icon><UserFilled /></el-icon>
          <span>职能管理</span>
        </el-menu-item>
        <el-menu-item index="/results">
          <el-icon><DataBoard /></el-icon>
          <span>匹配结果</span>
        </el-menu-item>
        <el-menu-item index="/lines">
          <el-icon><Connection /></el-icon>
          <span>条线管理</span>
        </el-menu-item>
      </el-menu>
      <div class="app-sidebar-footer">
        <span>v1.0</span>
      </div>
    </el-aside>

    <el-main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>
  </el-container>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentRoute = computed(() => route.path)
const sidebarWidth = ref('var(--sidebar-width)')
</script>

<style>
:root {
  --el-font-size-base: 16px;
  --el-font-size-small: 14px;
  --el-font-size-large: 20px;
  --el-font-size-extra-large: 24px;
  --sidebar-width: 240px;
  --color-bg: #f0f4f8;
  --color-card-bg: #ffffff;
  --color-primary: #4F6EF7;
  --color-primary-light: #EEF1FF;
}
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* ===== Sidebar ===== */
.app-sidebar {
  background: linear-gradient(180deg, #1B1B3A 0%, #1a1a2e 100%);
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 10;
  box-shadow: 2px 0 12px rgba(0,0,0,0.08);
}
.app-logo {
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.app-logo-icon {
  font-size: 26px;
}
.app-logo-text {
  font-size: 22px;
  font-weight: 700;
  color: #e8e8f0;
  letter-spacing: 2px;
  user-select: none;
}
.app-nav {
  flex: 1;
  border: none !important;
  background: transparent !important;
  padding: 12px 0;
}
.app-nav .el-menu-item {
  height: 48px;
  line-height: 48px;
  margin: 2px 10px;
  border-radius: 8px;
  padding: 0 14px !important;
  transition: all 0.2s;
  position: relative;
}
.app-nav .el-menu-item .el-icon {
  font-size: 20px;
  margin-right: 10px;
}
.app-nav .el-menu-item.is-active {
  background: rgba(79, 110, 247, 0.25) !important;
  color: #fff !important;
}
.app-nav .el-menu-item.is-active::before {
  content: '';
  position: absolute;
  left: -10px;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  border-radius: 0 3px 3px 0;
  background: #4F6EF7;
}
.app-nav .el-menu-item:hover {
  background: rgba(255,255,255,0.08) !important;
}
.app-sidebar-footer {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  color: rgba(255,255,255,0.25);
  border-top: 1px solid rgba(255,255,255,0.06);
}

/* ===== Main area ===== */
.app-main {
  background: linear-gradient(135deg, #f0f4f8 0%, #e8ecf4 100%);
  padding: 28px 32px;
  min-height: 100vh;
}

@media (max-width: 1200px) {
  .app-main { padding: 20px 16px; }
}

/* ===== Card refinements ===== */
.app-main .el-card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}
.app-main .el-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #4F6EF7, #7B8CFF);
  opacity: 0;
  transition: opacity 0.3s ease;
}
.app-main .el-card.page-header::before {
  opacity: 1;
}
.app-main .el-card:hover {
  box-shadow: 0 8px 28px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.04);
}
.app-main .el-card__body {
  padding: 20px 24px;
}
.app-main .page-header {
  margin-bottom: 20px;
}
.app-main .page-table {
  margin-top: 0;
}
.app-main .card-stack > .el-card + .el-card {
  margin-top: 20px;
}
.app-main .page-header::before {
  opacity: 1;
}
.app-main .page-table {
  border-radius: 12px;
}

/* ===== Table refinements ===== */
.app-main .el-table {
  border-radius: 8px;
  overflow: hidden;
}
.app-main .el-table::before {
  display: none;
}
.app-main .el-table th.el-table__cell {
  background: linear-gradient(135deg, #f5f7fa, #eef1f5);
  font-weight: 600;
  color: #303133;
  padding: 12px 0;
}
.app-main .el-table th.el-table__cell .cell {
  font-weight: 600;
  color: #303133;
}
.app-main .el-table--striped .el-table__body tr.el-table__row--striped td {
  background: #fafbfc;
}
.app-main .el-table__body tr {
  transition: background 0.2s ease;
}
.app-main .el-table__body tr:hover td {
  background: #f0f4ff !important;
}
.app-main .el-table__body tr.el-table__row--striped:hover td {
  background: #eef2fb !important;
}
.app-main .el-table--enable-row-hover .el-table__body tr:hover > td.el-table__cell {
  background: #f0f4ff !important;
}
.el-table .cell {
  white-space: nowrap;
  font-size: var(--el-font-size-base);
  padding: 0 12px;
}
.el-table .el-input__wrapper,
.el-table .el-select__wrapper {
  font-size: var(--el-font-size-base);
}
.el-table--border td, .el-table--border th {
  border-color: #ebeef5;
}

/* ===== Table column selection (DutyManagement) ===== */
.el-table__body .el-checkbox__input.is-checked .el-checkbox__inner {
  background-color: var(--el-color-primary);
  border-color: var(--el-color-primary);
}

/* ===== Tag refinements ===== */
.app-main .el-tag {
  border-radius: 6px;
  padding: 0 10px;
  font-weight: 500;
  border: none;
}
.app-main .el-tag--plain {
  border: 1px solid;
}

/* ===== Steps vertical ===== */
.app-main .el-step.is-vertical .el-step__head {
  width: 28px;
  height: 28px;
}
.app-main .el-step.is-vertical .el-step__line {
  left: 13px;
}

/* ===== Button refinements ===== */
.app-main .el-button {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.app-main .el-button:active {
  transform: scale(0.97);
}
.app-main .el-button--primary {
  background: var(--color-primary);
  border-color: var(--color-primary);
}
.app-main .el-button--primary:hover {
  background: #3d5bd9;
  border-color: #3d5bd9;
  box-shadow: 0 4px 12px rgba(79, 110, 247, 0.3);
}
.app-main .el-button--success:hover {
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.3);
}
.app-main .el-button--danger:hover {
  box-shadow: 0 4px 12px rgba(245, 108, 108, 0.3);
}
.app-main .el-button--primary.is-disabled {
  box-shadow: none;
}
.app-main .el-button.is-link {
  border-radius: 4px;
}

/* ===== Dialog refinements ===== */
.app-main .el-dialog {
  border-radius: 12px;
}
.app-main .el-dialog__header {
  padding: 20px 24px 0;
}
.app-main .el-dialog__body {
  padding: 20px 24px;
}
.app-main .el-dialog__footer {
  padding: 0 24px 20px;
}

/* ===== Input refinements ===== */
.app-main .el-input__wrapper {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #dcdfe6 inset;
  transition: box-shadow 0.2s;
}
.app-main .el-input__wrapper:hover {
  box-shadow: 0 0 0 1px #c0c4cc inset;
}
.app-main .el-input__wrapper.is-focus {
  box-shadow: 0 0 0 1px var(--color-primary) inset !important;
}
.app-main .el-select .el-select__wrapper {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #dcdfe6 inset;
}
.app-main .el-select .el-select__wrapper:hover {
  box-shadow: 0 0 0 1px #c0c4cc inset;
}

/* ===== Alert refinements ===== */
.app-main .el-alert {
  border-radius: 10px;
}

/* ===== Steps refinements (match dialog) ===== */
.app-main .el-step.is-vertical .el-step__title {
  font-size: 15px;
  font-weight: 500;
}
.app-main .el-step.is-vertical .el-step__description {
  font-size: 13px;
  color: #a0a4b0;
  padding-bottom: 8px;
}
.app-main .el-step.is-vertical.is-process .el-step__title {
  color: var(--el-color-primary);
}
.app-main .el-step.is-vertical.is-finish .el-step__title {
  font-weight: 500;
}

/* ===== Menu horizontal overrides for dialogs ===== */
.app-main .el-tabs--border-card {
  border-radius: 8px;
  overflow: hidden;
}

/* ===== Custom scrollbar ===== */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* ===== Page title with accent bar ===== */
.page-title {
  font-size: var(--el-font-size-large);
  font-weight: 700;
  color: #1d1d2e;
  display: inline-flex;
  align-items: center;
  gap: 12px;
}
.page-title::before {
  content: '';
  display: inline-block;
  width: 4px;
  height: 24px;
  border-radius: 2px;
  background: linear-gradient(180deg, #4F6EF7, #7B8CFF);
  flex-shrink: 0;
}

/* ===== Empty state ===== */
.empty-state {
  text-align: center;
  padding: 80px 20px 60px;
  transition: all 0.3s;
}
.empty-state .empty-icon {
  font-size: 52px;
  color: #d0d4e0;
  display: inline-block;
  margin-bottom: 4px;
}
.empty-state .empty-title {
  font-size: 16px;
  font-weight: 500;
  color: #909399;
  margin: 10px 0 4px;
}
.empty-state .empty-hint {
  font-size: 14px;
  color: #c0c4cc;
  margin: 0;
}

/* ===== Stat cards ===== */
.stat-cards {
  display: flex;
  gap: 24px;
  justify-content: center;
  padding: 12px 0;
}
.stat-card {
  text-align: center;
  padding: 20px 36px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f8f9fc 0%, #f0f2f8 100%);
  min-width: 130px;
  transition: all 0.3s;
  border: 1px solid rgba(0,0,0,0.04);
  flex: 1;
  max-width: 220px;
}
.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}
.stat-card .stat-number {
  font-size: 34px;
  font-weight: 700;
  line-height: 1.2;
}
.stat-card .stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 6px;
}


</style>
