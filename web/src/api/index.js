import axios from 'axios'

// 创建Axios实例
const api = axios.create({
  // 基础URL：由Vite环境变量配置，Nginx会代理到后端
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 10000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json',
    // API密钥：从环境变量获取
    'X-API-Key': import.meta.env.VITE_API_KEY || 'default_secret'
  }
})

// 请求拦截器：添加通用配置（如token）
api.interceptors.request.use(
  (config) => {
    // 后续可添加登录token
    // const token = localStorage.getItem('token')
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：统一处理错误
api.interceptors.response.use(
  (response) => {
    // 后端统一返回格式：{ code: 200, data: ..., msg: '' }
    if (response.data.code !== 200) {
      return Promise.reject(new Error(response.data.msg || '请求失败'))
    }
    return response.data.data
  },
  (error) => {
    // 处理网络错误/404/500等
    let errMsg = '网络异常，请稍后重试'
    if (error.response) {
      const status = error.response.status
      if (status === 401) {
        errMsg = '未授权，请重新登录'
        // 清空登录状态
        // localStorage.removeItem('token')
        // window.location.href = '/login'
      } else if (status === 403) {
        errMsg = '权限不足，无法操作'
      } else if (status === 404) {
        errMsg = '接口不存在'
      } else if (status === 500) {
        errMsg = '服务器内部错误'
      }
    }
    return Promise.reject(new Error(errMsg))
  }
)

// -------------------------- 核心API封装 --------------------------
// 1. 任务相关API
export const taskApi = {
  // 获取任务列表
  getTaskList: () => api.get('/tasks'),
  // 获取任务详情
  getTaskDetail: (taskId) => api.get(`/tasks/${taskId}`),
  // 创建任务
  createTask: (data) => api.post('/tasks', data),
  // 暂停任务
  pauseTask: (taskId) => api.put(`/tasks/${taskId}/pause`),
  // 终止任务
  stopTask: (taskId) => api.put(`/tasks/${taskId}/stop`),
  // 重试任务
  retryTask: (taskId) => api.put(`/tasks/${taskId}/retry`)
}

// 2. Agent相关API
export const agentApi = {
  // 获取Agent列表
  getAgentList: () => api.get('/agents'),
  // 启用/禁用Agent
  toggleAgent: (agentId, status) => api.put(`/agents/${agentId}/status`, { status })
}

// 3. 插件相关API
export const pluginApi = {
  // 获取插件列表
  getPluginList: () => api.get('/plugins'),
  // 启用/禁用插件
  togglePlugin: (pluginId, status) => api.put(`/plugins/${pluginId}/status`, { status }),
  // 重载插件
  reloadPlugin: (pluginId) => api.put(`/plugins/${pluginId}/reload`)
}

// 4. 审计日志相关API
export const auditApi = {
  // 获取审计日志
  getAuditLogs: (params) => api.get('/audit/logs', { params }),
  // 导出日志
  exportLogs: (params) => api.get('/audit/export', { params, responseType: 'blob' })
}

// 5. 系统状态相关API
export const systemApi = {
  // 健康检查
  healthCheck: () => api.get('/health'),
  // 获取系统统计
  getStats: () => api.get('/stats')
}

// 默认导出axios实例（供特殊场景使用）
export default api