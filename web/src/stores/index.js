import { defineStore } from 'pinia'

// 全局任务Store：管理所有任务相关状态
export const useTaskStore = defineStore('task', {
  state: () => ({
    // 任务列表
    taskList: [],
    // 当前选中的任务ID
    currentTaskId: '',
    // 加载状态
    loading: false,
    // 错误信息
    errorMsg: ''
  }),
  actions: {
    // 模拟获取任务列表（后续对接API）
    async fetchTaskList() {
      this.loading = true
      try {
        // 这里后续替换为真实API请求
        setTimeout(() => {
          this.taskList = [
            { id: 'demo_task_energy_policy', name: '新能源政策制定', status: 'completed', createTime: '2026-03-06' }
          ]
          this.errorMsg = ''
        }, 500)
      } catch (err) {
        this.errorMsg = '获取任务列表失败：' + err.message
      } finally {
        this.loading = false
      }
    },
    // 选中任务
    selectTask(taskId) {
      this.currentTaskId = taskId
    },
    // 清空错误信息
    clearError() {
      this.errorMsg = ''
    }
  }
})

// 全局用户Store：管理用户登录、权限等状态
export const useUserStore = defineStore('user', {
  state: () => ({
    // 用户信息
    userInfo: null,
    // 登录状态
    isLogin: false
  }),
  actions: {
    // 模拟登录（后续对接API）
    login(username, password) {
      // 简单模拟：用户名密码不为空即登录成功
      if (username && password) {
        this.userInfo = { username, role: 'admin' }
        this.isLogin = true
        return true
      }
      return false
    },
    // 退出登录
    logout() {
      this.userInfo = null
      this.isLogin = false
    }
  }
})