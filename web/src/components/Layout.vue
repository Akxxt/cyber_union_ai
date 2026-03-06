<template>
  <el-container class="layout-container">
    <el-aside width="200px" class="aside">
      <div class="logo">
        <img src="@/assets/logo.svg" alt="Logo" height="40" />
      </div>
      <el-menu
        :default-active="$route.path"
        router
        background-color="#304156"
        text-color="#fff"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Monitor /></el-icon>
          <span>监控大屏</span>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <el-icon><List /></el-icon>
          <span>任务管理</span>
        </el-menu-item>
        <el-menu-item index="/agents">
          <el-icon><User /></el-icon>
          <span>Agent管理</span>
        </el-menu-item>
        <el-menu-item index="/plugins">
          <el-icon><Connection /></el-icon>
          <span>插件管理</span>
        </el-menu-item>
        <el-menu-item index="/audit">
          <el-icon><Document /></el-icon>
          <span>审计日志</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ $route.meta.title || $route.name }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-input
            v-model="apiKey"
            placeholder="API Key"
            size="small"
            style="width: 200px; margin-right: 10px;"
            show-password
          />
          <el-button type="primary" size="small" @click="saveApiKey">保存</el-button>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Monitor, List, User, Connection, Document } from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'

const route = useRoute()
const appStore = useAppStore()
const apiKey = ref(appStore.apiKey)

const saveApiKey = () => {
  appStore.setApiKey(apiKey.value)
  ElMessage.success('API Key已保存')
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}
.aside {
  background-color: #304156;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #1f2d3d;
}
.header {
  background-color: #fff;
  border-bottom: 1px solid #e6e9f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}
.header-left {
  flex: 1;
}
.header-right {
  display: flex;
  align-items: center;
}
.el-menu {
  border-right: none;
}
.el-menu-item {
  display: flex;
  align-items: center;
}
.el-menu-item .el-icon {
  margin-right: 8px;
}
</style>