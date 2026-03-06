/**
 * 前端通用工具函数库
 * 包含时间格式化、状态转换、深拷贝、防抖节流等常用工具
 */

// 1. 时间格式化工具：timestamp → 友好格式（如 2026-03-06 12:30:00）
export function formatTime(timestamp, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  const second = String(date.getSeconds()).padStart(2, '0')

  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hour)
    .replace('mm', minute)
    .replace('ss', second)
}

// 2. 任务状态转换：英文状态 → 中文+样式类
export function formatTaskStatus(status) {
  const statusMap = {
    pending: { text: '待处理', class: 'status-pending' },
    running: { text: '运行中', class: 'status-running' },
    completed: { text: '已完成', class: 'status-completed' },
    failed: { text: '失败', class: 'status-failed' },
    paused: { text: '已暂停', class: 'status-paused' },
    cancelled: { text: '已终止', class: 'status-cancelled' }
  }
  return statusMap[status] || { text: '未知', class: 'status-unknown' }
}

// 3. 深拷贝工具（兼容对象/数组，简单版）
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj)
  if (obj instanceof Array) return obj.map(item => deepClone(item))
  if (obj instanceof Object) {
    const newObj = {}
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        newObj[key] = deepClone(obj[key])
      }
    }
    return newObj
  }
  return obj
}

// 4. 防抖函数（防止高频触发，如搜索框输入）
export function debounce(fn, delay = 300) {
  let timer = null
  return function (...args) {
    clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

// 5. 节流函数（限制触发频率，如滚动/resize）
export function throttle(fn, interval = 500) {
  let lastTime = 0
  return function (...args) {
    const now = Date.now()
    if (now - lastTime >= interval) {
      fn.apply(this, args)
      lastTime = now
    }
  }
}

// 6. 数字格式化：大数字加千分位（如 10000 → 10,000）
export function formatNumber(num) {
  if (isNaN(num)) return '0'
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

// 7. 空值判断：判断值是否为null/undefined/空字符串/空数组/空对象
export function isEmpty(value) {
  if (value === null || value === undefined) return true
  if (typeof value === 'string' && value.trim() === '') return true
  if (Array.isArray(value) && value.length === 0) return true
  if (typeof value === 'object' && Object.keys(value).length === 0) return true
  return false
}