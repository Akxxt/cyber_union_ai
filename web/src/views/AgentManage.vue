<template>
  <div class="agent-manage-container">
    <div class="page-header">
      <h1>Agent 管理</h1>
    </div>

    <div class="agent-list">
      <div class="agent-item" v-for="agent in agentList" :key="agent.id">
        <div class="agent-info">
          <div class="agent-name">{{ agent.name }}</div>
          <div class="agent-role">{{ agent.role }}</div>
          <div class="agent-status" :class="agent.status === 'enabled' ? 'status-enabled' : 'status-disabled'">
            {{ agent.status === 'enabled' ? '已启用' : '已禁用' }}
          </div>
        </div>
        <div class="agent-stats">
          <div>调用次数：{{ agent.callCount }}</div>
          <div>Token消耗：{{ agent.tokenUsed }}</div>
        </div>
        <button 
          @click="toggleAgent(agent.id, agent.status)" 
          class="toggle-btn"
          :class="agent.status === 'enabled' ? 'disable-btn' : 'enable-btn'"
        >
          {{ agent.status === 'enabled' ? '禁用' : '启用' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const agentList = ref([
  { id: 'president', name: '总统', role: 'PRESIDENT', status: 'enabled', callCount: 480, tokenUsed: 125000 },
  { id: 'congress', name: '国会', role: 'CONGRESS', status: 'enabled', callCount: 620, tokenUsed: 186000 },
  { id: 'supreme_court', name: '最高法院', role: 'SUPREME_COURT', status: 'enabled', callCount: 310, tokenUsed: 93000 },
  { id: 'energy_dept', name: '能源部', role: 'CABINET', status: 'enabled', callCount: 240, tokenUsed: 72000 },
  { id: 'treasury_dept', name: '财政部', role: 'CABINET', status: 'enabled', callCount: 210, tokenUsed: 63000 }
])

const toggleAgent = (id, currentStatus) => {
  const agent = agentList.value.find(item => item.id === id)
  if (agent) {
    agent.status = currentStatus === 'enabled' ? 'disabled' : 'enabled'
  }
}
</script>

<style scoped>
.agent-manage-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}
.page-header h1 {
  font-size: 24px;
  color: #1f2937;
  margin: 0 0 20px 0;
}
.agent-list {
  display: grid;
  gap: 16px;
}
.agent-item {
  background: white;
  padding: 16px 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.agent-info {
  display: flex;
  align-items: center;
  gap: 16px;
}
.agent-name {
  font-size: 16px;
  font-weight: 500;
  color: #1f2937;
}
.agent-role {
  color: #6b7280;
  font-size: 14px;
}
.agent-status {
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
.agent-stats {
  color: #6b7280;
  font-size: 14px;
  display: flex;
  gap: 16px;
}
.toggle-btn {
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
.enable-btn {
  background: #10b981;
  color: white;
}
.disable-btn {
  background: #ef4444;
  color: white;
}
</style>