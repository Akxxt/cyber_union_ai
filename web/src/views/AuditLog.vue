<template>
  <div class="audit-log-container">
    <!-- 页面标题 + 导出按钮 -->
    <div class="page-header">
      <h1>审计日志</h1>
      <button @click="exportLogs" class="export-btn">导出日志</button>
    </div>

    <!-- 筛选栏 -->
    <div class="log-filter">
      <select v-model="logTypeFilter" class="filter-select">
        <option value="">全部日志类型</option>
        <option value="operation">操作日志</option>
        <option value="execution">执行日志</option>
        <option value="compliance">合规日志</option>
        <option value="token">Token日志</option>
      </select>
      <input 
        v-model="taskIdFilter" 
        type="text" 
        placeholder="输入任务ID筛选..." 
        class="filter-input"
      >
      <button @click="filterLogs" class="filter-btn">筛选</button>
      <button @click="resetFilter" class="reset-btn">重置</button>
    </div>

    <!-- 日志列表 -->
    <div class="log-list">
      <div v-if="filteredLogs.length === 0" class="empty-tip">
        暂无符合条件的日志
      </div>
      <div class="log-item" v-for="log in filteredLogs" :key="log.id">
        <div class="log-header">
          <div class="log-type" :class="`type-${log.type}`">
            {{ getLogTypeName(log.type) }}
          </div>
          <div class="log-task-id">任务ID：{{ log.taskId }}</div>
          <div class="log-time">{{ log.time }}</div>
        </div>
        <div class="log-content">
          {{ log.content }}
        </div>
        <div v-if="log.extra" class="log-extra">
          扩展信息：{{ JSON.stringify(log.extra) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// 模拟日志数据
const logList = ref([
  {
    id: 1,
    type: 'operation',
    taskId: 'demo_task_energy_policy',
    time: '2026-03-06 10:00:00',
    content: '系统创建演示任务',
    extra: { operator: 'system', action: 'create' }
  },
  {
    id: 2,
    type: 'token',
    taskId: 'demo_task_energy_policy',
    time: '2026-03-06 10:05:00',
    content: '总统Agent调用消耗Token 5000',
    extra: { agent: 'PRESIDENT', tokens: 5000, node: 'president_plan' }
  },
  {
    id: 3,
    type: 'execution',
    taskId: 'demo_task_energy_policy',
    time: '2026-03-06 10:10:00',
    content: '国会完成新能源法案立法',
    extra: { node: 'congress_legislate', result: 'success' }
  },
  {
    id: 4,
    type: 'compliance',
    taskId: 'demo_task_energy_policy',
    time: '2026-03-06 10:15:00',
    content: '最高法院审查通过，无敏感内容',
    extra: { check_type: 'sensitive_content', risk_level: 'low', result: 'pass' }
  },
  {
    id: 5,
    type: 'token',
    taskId: 'demo_task_energy_policy',
    time: '2026-03-06 10:20:00',
    content: '国会Agent调用消耗Token 8000',
    extra: { agent: 'CONGRESS', tokens: 8000, node: 'congress_legislate' }
  }
])

// 筛选条件
const logTypeFilter = ref('')
const taskIdFilter = ref('')

// 筛选后的日志列表
const filteredLogs = computed(() => {
  let logs = [...logList.value]
  
  // 按日志类型筛选
  if (logTypeFilter.value) {
    logs = logs.filter(log => log.type === logTypeFilter.value)
  }
  
  // 按任务ID筛选
  if (taskIdFilter.value) {
    const keyword = taskIdFilter.value.toLowerCase()
    logs = logs.filter(log => log.taskId.toLowerCase().includes(keyword))
  }
  
  return logs
})

// 获取日志类型中文名称
const getLogTypeName = (type) => {
  const typeMap = {
    operation: '操作日志',
    execution: '执行日志',
    compliance: '合规日志',
    token: 'Token日志'
  }
  return typeMap[type] || '未知日志'
}

// 筛选日志
const filterLogs = () => {
  console.log('筛选条件：', { type: logTypeFilter.value, taskId: taskIdFilter.value })
}

// 重置筛选条件
const resetFilter = () => {
  logTypeFilter.value = ''
  taskIdFilter.value = ''
}

// 导出日志
const exportLogs = () => {
  alert('日志导出成功（演示模式），文件格式为JSON')
  // 后续对接API：await auditApi.exportLogs({ type: logTypeFilter.value, taskId: taskIdFilter.value })
}
</script>

<style scoped>
/* 页面基础样式 */
.audit-log-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

/* 页面标题 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.page-header h1 {
  font-size: 24px;
  color: #1f2937;
  margin: 0;
}
.export-btn {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
.export-btn:hover {
  background-color: #2563eb;
}

/* 筛选栏 */
.log-filter {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  align-items: center;
}
.filter-select, .filter-input {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
}
.filter-input {
  min-width: 200px;
}
.filter-btn {
  background-color: #10b981;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}
.reset-btn {
  background-color: #6b7280;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

/* 日志列表 */
.log-list {
  display: grid;
  gap: 12px;
}
.empty-tip {
  padding: 40px;
  text-align: center;
  color: #9ca3af;
  font-size: 14px;
  background: white;
  border-radius: 8px;
}
.log-item {
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.log-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}
.log-type {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  color: white;
}
.type-operation { background: #3b82f6; }
.type-execution { background: #10b981; }
.type-compliance { background: #f59e0b; }
.type-token { background: #8b5cf6; }
.log-task-id {
  font-size: 14px;
  color: #4b5563;
  font-family: monospace;
}
.log-time {
  font-size: 12px;
  color: #9ca3af;
  margin-left: auto;
}
.log-content {
  font-size: 14px;
  color: #1f2937;
  line-height: 1.5;
  margin-bottom: 8px;
}
.log-extra {
  font-size: 12px;
  color: #6b7280;
  background: #f9fafb;
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
}
</style>