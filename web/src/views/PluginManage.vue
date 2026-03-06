<template>
  <div class="plugin-manage-container">
    <div class="page-header">
      <h1>插件管理</h1>
    </div>

    <!-- 插件列表 -->
    <div class="plugin-list">
      <div class="plugin-item" v-for="plugin in pluginList" :key="plugin.id">
        <!-- 插件基础信息 -->
        <div class="plugin-basic">
          <div class="plugin-name">{{ plugin.name }}</div>
          <div class="plugin-id">{{ plugin.id }}</div>
          <div class="plugin-version">v{{ plugin.version }}</div>
          <div class="plugin-status" :class="plugin.status === 'enabled' ? 'status-enabled' : 'status-disabled'">
            {{ plugin.status === 'enabled' ? '已启用' : '已禁用' }}
          </div>
        </div>

        <!-- 插件描述 -->
        <div class="plugin-desc">{{ plugin.description }}</div>

        <!-- 插件操作 -->
        <div class="plugin-actions">
          <button 
            @click="togglePlugin(plugin.id, plugin.status)"
            class="action-btn toggle-btn"
            :class="plugin.status === 'enabled' ? 'disable-btn' : 'enable-btn'"
          >
            {{ plugin.status === 'enabled' ? '禁用' : '启用' }}
          </button>
          <button @click="reloadPlugin(plugin.id)" class="action-btn reload-btn">
            重载
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 模拟插件列表数据
const pluginList = ref([
  {
    id: 'file_io',
    name: '文件IO插件',
    version: '1.0.0',
    status: 'enabled',
    description: '提供文件读取/写入功能，支持txt、json格式'
  },
  {
    id: 'web_request',
    name: '网络请求插件',
    version: '1.0.0',
    status: 'enabled',
    description: '发送HTTP/HTTPS请求，支持GET/POST方法'
  },
  {
    id: 'data_analysis',
    name: '数据分析插件',
    version: '1.0.0',
    status: 'enabled',
    description: '提供数据统计、图表生成等分析功能'
  },
  {
    id: 'llm_function',
    name: 'LLM函数调用',
    version: '1.0.0',
    status: 'enabled',
    description: '封装大模型函数调用逻辑，统一参数格式'
  },
  {
    id: 'audit_log',
    name: '审计日志插件',
    version: '1.0.0',
    status: 'enabled',
    description: '记录插件调用日志，支持审计追踪'
  }
])

// 启用/禁用插件
const togglePlugin = (pluginId, currentStatus) => {
  const plugin = pluginList.value.find(item => item.id === pluginId)
  if (plugin) {
    plugin.status = currentStatus === 'enabled' ? 'disabled' : 'enabled'
    alert(`插件 ${plugin.name} 已${plugin.status === 'enabled' ? '启用' : '禁用'}`)
  }
}

// 重载插件
const reloadPlugin = (pluginId) => {
  const plugin = pluginList.value.find(item => item.id === pluginId)
  if (plugin) {
    alert(`插件 ${plugin.name} 重载成功！`)
  }
}
</script>

<style scoped>
/* 页面基础样式 */
.plugin-manage-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

/* 页面标题 */
.page-header h1 {
  font-size: 24px;
  color: #1f2937;
  margin: 0 0 20px 0;
}

/* 插件列表 */
.plugin-list {
  display: grid;
  gap: 16px;
}

/* 单个插件项 */
.plugin-item {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 插件基础信息 */
.plugin-basic {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}
.plugin-name {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}
.plugin-id {
  font-size: 12px;
  color: #6b7280;
  font-family: monospace;
}
.plugin-version {
  font-size: 12px;
  color: #9ca3af;
}
.plugin-status {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
}
.status-enabled {
  background: #d1fae5;
  color: #059669;
}
.status-disabled {
  background: #e5e7eb;
  color: #4b5563;
}

/* 插件描述 */
.plugin-desc {
  font-size: 14px;
  color: #4b5563;
  line-height: 1.5;
}

/* 插件操作按钮 */
.plugin-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}
.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
.toggle-btn {
  color: white;
}
.enable-btn {
  background-color: #10b981;
}
.disable-btn {
  background-color: #ef4444;
}
.reload-btn {
  background-color: #3b82f6;
  color: white;
}
</style>