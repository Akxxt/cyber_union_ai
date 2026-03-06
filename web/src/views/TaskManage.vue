<template>
  <div class="task-manage-container">
    <!-- 页面标题 + 新建任务按钮 -->
    <div class="page-header">
      <h1>任务管理</h1>
      <button @click="showCreateTask = true" class="create-btn">新建任务</button>
    </div>

    <!-- 加载状态 -->
    <div v-if="taskStore.loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载任务列表中...</p>
    </div>

    <!-- 错误提示 -->
    <div v-if="taskStore.errorMsg" class="error-alert">
      {{ taskStore.errorMsg }}
      <button @click="taskStore.clearError()" class="close-btn">×</button>
    </div>

    <!-- 任务列表 -->
    <div v-else class="task-list-container">
      <!-- 任务筛选栏 -->
      <div class="task-filter">
        <select v-model="statusFilter" class="filter-select">
          <option value="">全部状态</option>
          <option value="pending">待处理</option>
          <option value="running">运行中</option>
          <option value="completed">已完成</option>
          <option value="failed">失败</option>
          <option value="paused">已暂停</option>
          <option value="cancelled">已终止</option>
        </select>
        <input 
          v-model="searchKeyword" 
          type="text" 
          placeholder="搜索任务ID/名称..." 
          class="search-input"
          @input="debouncedSearch"
        >
      </div>

      <!-- 任务列表 -->
      <div class="task-list">
        <div v-if="filteredTasks.length === 0" class="empty-tip">
          暂无符合条件的任务
        </div>
        <div 
          v-for="task in filteredTasks" 
          :key="task.id" 
          class="task-item"
          :class="{ active: task.id === taskStore.currentTaskId }"
          @click="taskStore.selectTask(task.id)"
        >
          <!-- 任务基本信息 -->
          <div class="task-basic">
            <div class="task-id">{{ task.id }}</div>
            <div class="task-name">{{ task.name }}</div>
            <div 
              class="task-status" 
              :class="formatTaskStatus(task.status).class"
            >
              {{ formatTaskStatus(task.status).text }}
            </div>
            <div class="task-time">{{ formatTime(task.createTime) }}</div>
          </div>

          <!-- 任务操作按钮 -->
          <div class="task-actions">
            <button 
              v-if="task.status === 'running'"
              @click.stop="handlePauseTask(task.id)"
              class="action-btn pause-btn"
            >
              暂停
            </button>
            <button 
              v-if="task.status === 'pending' || task.status === 'paused'"
              @click.stop="handleResumeTask(task.id)"
              class="action-btn resume-btn"
            >
              继续
            </button>
            <button 
              v-if="task.status !== 'cancelled' && task.status !== 'completed'"
              @click.stop="handleStopTask(task.id)"
              class="action-btn stop-btn"
            >
              终止
            </button>
            <button 
              v-if="task.status === 'failed'"
              @click.stop="handleRetryTask(task.id)"
              class="action-btn retry-btn"
            >
              重试
            </button>
          </div>

          <!-- 任务详情（展开/折叠） -->
          <div 
            v-if="task.id === taskStore.currentTaskId" 
            class="task-detail"
          >
            <div class="detail-section">
              <div class="detail-title">任务详情</div>
              <div class="detail-content">
                <div class="detail-row">
                  <span class="label">任务ID：</span>
                  <span class="value">{{ task.id }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">任务名称：</span>
                  <span class="value">{{ task.name }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">创建时间：</span>
                  <span class="value">{{ formatTime(task.createTime) }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">状态：</span>
                  <span class="value" :class="formatTaskStatus(task.status).class">
                    {{ formatTaskStatus(task.status).text }}
                  </span>
                </div>
                <div v-if="task.output" class="detail-row">
                  <span class="label">执行结果：</span>
                  <span class="value">{{ task.output }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建任务弹窗（隐藏状态） -->
    <div v-if="showCreateTask" class="modal-mask">
      <div class="modal-container">
        <div class="modal-header">
          <h3>新建任务</h3>
          <button @click="showCreateTask = false" class="modal-close">×</button>
        </div>
        <div class="modal-body">
          <div class="form-item">
            <label class="form-label">任务名称：</label>
            <input 
              v-model="newTask.name" 
              type="text" 
              placeholder="请输入任务名称" 
              class="form-input"
            >
          </div>
          <div class="form-item">
            <label class="form-label">任务描述：</label>
            <textarea 
              v-model="newTask.desc" 
              placeholder="请输入任务具体需求（如：制定新能源政策）" 
              class="form-textarea"
              rows="4"
            ></textarea>
          </div>
          <div class="form-item">
            <label class="form-label">优先级：</label>
            <select v-model="newTask.priority" class="form-select">
              <option value="low">低</option>
              <option value="medium">中</option>
              <option value="high">高</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showCreateTask = false" class="modal-cancel">取消</button>
          <button @click="handleCreateTask" class="modal-confirm">提交</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTaskStore } from '../stores/index'
import { formatTime, formatTaskStatus, debounce } from '../utils/index'
// 后续对接API时引入
// import { taskApi } from '../api/index'

// 路由实例
const router = useRouter()

// 任务Store
const taskStore = useTaskStore()

// 弹窗状态
const showCreateTask = ref(false)

// 新建任务表单数据
const newTask = ref({
  name: '',
  desc: '',
  priority: 'medium'
})

// 筛选条件
const statusFilter = ref('')
const searchKeyword = ref('')

// 防抖搜索（300ms延迟）
const debouncedSearch = debounce(() => {
  console.log('搜索关键词：', searchKeyword.value)
}, 300)

// 筛选后的任务列表
const filteredTasks = computed(() => {
  let tasks = taskStore.taskList
  // 状态筛选
  if (statusFilter.value) {
    tasks = tasks.filter(task => task.status === statusFilter.value)
  }
  // 关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    tasks = tasks.filter(task => 
      task.id.toLowerCase().includes(keyword) || 
      task.name.toLowerCase().includes(keyword)
    )
  }
  return tasks
})

// 页面挂载时加载任务列表
onMounted(() => {
  // 从URL参数获取演示任务ID并选中
  const taskId = router.currentRoute.query.taskId
  if (taskId) {
    taskStore.selectTask(taskId)
  }
  // 加载任务列表
  taskStore.fetchTaskList()
})

// 操作函数：暂停任务
const handlePauseTask = (taskId) => {
  if (confirm(`确定要暂停任务 ${taskId} 吗？`)) {
    console.log('暂停任务：', taskId)
    // 后续对接API：await taskApi.pauseTask(taskId)
    // 重新加载任务列表
    taskStore.fetchTaskList()
  }
}

// 操作函数：继续任务
const handleResumeTask = (taskId) => {
  if (confirm(`确定要继续任务 ${taskId} 吗？`)) {
    console.log('继续任务：', taskId)
    // 后续对接API：await taskApi.resumeTask(taskId)
    taskStore.fetchTaskList()
  }
}

// 操作函数：终止任务
const handleStopTask = (taskId) => {
  if (confirm(`确定要终止任务 ${taskId} 吗？此操作不可恢复！`)) {
    console.log('终止任务：', taskId)
    // 后续对接API：await taskApi.stopTask(taskId)
    taskStore.fetchTaskList()
  }
}

// 操作函数：重试任务
const handleRetryTask = (taskId) => {
  if (confirm(`确定要重试任务 ${taskId} 吗？`)) {
    console.log('重试任务：', taskId)
    // 后续对接API：await taskApi.retryTask(taskId)
    taskStore.fetchTaskList()
  }
}

// 操作函数：创建任务
const handleCreateTask = () => {
  // 表单验证
  if (!newTask.value.name.trim()) {
    alert('请输入任务名称！')
    return
  }
  if (!newTask.value.desc.trim()) {
    alert('请输入任务描述！')
    return
  }

  console.log('创建新任务：', newTask.value)
  // 后续对接API：
  // try {
  //   await taskApi.createTask(newTask.value)
  //   alert('任务创建成功！')
  //   showCreateTask.value = false
  //   // 重置表单
  //   newTask.value = { name: '', desc: '', priority: 'medium' }
  //   // 重新加载任务列表
  //   taskStore.fetchTaskList()
  // } catch (err) {
  //   alert('任务创建失败：' + err.message)
  // }

  // 模拟创建成功
  alert('任务创建成功（演示模式）！')
  showCreateTask.value = false
  newTask.value = { name: '', desc: '', priority: 'medium' }
  taskStore.fetchTaskList()
}
</script>

<style scoped>
/* 页面整体样式 */
.task-manage-container {
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
.create-btn {
  background-color: #10b981;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
.create-btn:hover {
  background-color: #059669;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: #6b7280;
}
.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 错误提示 */
.error-alert {
  background-color: #fee2e2;
  color: #dc2626;
  padding: 12px 16px;
  border-radius: 4px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.close-btn {
  background: none;
  border: none;
  color: #dc2626;
  font-size: 18px;
  cursor: pointer;
  padding: 0 4px;
}

/* 任务筛选栏 */
.task-filter {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.filter-select, .search-input {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
}
.search-input {
  flex: 1;
  min-width: 200px;
}

/* 任务列表 */
.task-list-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  overflow: hidden;
}
.task-list {
  width: 100%;
}
.empty-tip {
  padding: 40px;
  text-align: center;
  color: #9ca3af;
  font-size: 14px;
}
.task-item {
  border-bottom: 1px solid #e5e7eb;
  cursor: pointer;
}
.task-item:last-child {
  border-bottom: none;
}
.task-item.active {
  background-color: #f9fafb;
}

/* 任务基本信息 */
.task-basic {
  display: grid;
  grid-template-columns: 2fr 3fr 1fr 1.5fr;
  padding: 16px 20px;
  align-items: center;
  font-size: 14px;
}
.task-id {
  color: #4b5563;
  font-family: monospace;
}
.task-name {
  color: #1f2937;
  font-weight: 500;
}
.task-status {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  text-align: center;
}
/* 状态样式 */
.status-pending { background: #fef3c7; color: #d97706; }
.status-running { background: #dbeafe; color: #2563eb; }
.status-completed { background: #d1fae5; color: #059669; }
.status-failed { background: #fee2e2; color: #dc2626; }
.status-paused { background: #e5e7eb; color: #4b5563; }
.status-cancelled { background: #f3f4f6; color: #6b7280; }
.status-unknown { background: #f9fafb; color: #9ca3af; }

/* 任务操作按钮 */
.task-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  padding: 0 20px 8px 0;
}
.action-btn {
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
}
.pause-btn { background: #f59e0b; color: white; }
.resume-btn { background: #10b981; color: white; }
.stop-btn { background: #ef4444; color: white; }
.retry-btn { background: #3b82f6; color: white; }

/* 任务详情 */
.task-detail {
  padding: 0 20px 16px;
  border-top: 1px solid #e5e7eb;
  margin-top: 8px;
}
.detail-section {
  margin-top: 12px;
}
.detail-title {
  font-size: 16px;
  color: #1f2937;
  margin-bottom: 12px;
  font-weight: 600;
}
.detail-content {
  font-size: 14px;
  color: #4b5563;
}
.detail-row {
  margin-bottom: 8px;
  display: flex;
  flex-wrap: wrap;
}
.label {
  color: #6b7280;
  min-width: 80px;
}
.value {
  flex: 1;
  word-break: break-all;
}

/* 弹窗遮罩 */
.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

/* 弹窗容器 */
.modal-container {
  background: white;
  width: 500px;
  max-width: 90%;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.modal-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #1f2937;
}
.modal-close {
  background: none;
  border: none;
  font-size: 20px;
  color: #6b7280;
  cursor: pointer;
  padding: 0 4px;
}
.modal-body {
  padding: 20px;
}
.modal-footer {
  padding: 16px 20px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
.modal-cancel {
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: white;
  color: #4b5563;
  cursor: pointer;
}
.modal-confirm {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  background: #3b82f6;
  color: white;
  cursor: pointer;
}
.modal-confirm:hover {
  background: #2563eb;
}

/* 表单样式 */
.form-item {
  margin-bottom: 16px;
}
.form-label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #1f2937;
  font-weight: 500;
}
.form-input, .form-select, .form-textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}
.form-textarea {
  resize: vertical;
}
</style>