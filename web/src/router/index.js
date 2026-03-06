import { createRouter, createWebHistory } from 'vue-router'

// 导入页面组件（后续可补充具体组件代码）
const Home = () => import('../views/Home.vue')
const TaskManage = () => import('../views/TaskManage.vue')
const AgentManage = () => import('../views/AgentManage.vue')
const PluginManage = () => import('../views/PluginManage.vue')
const AuditLog = () => import('../views/AuditLog.vue')

// 路由规则
const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: '首页 - 赛博合众国AI' }
  },
  {
    path: '/task',
    name: 'TaskManage',
    component: TaskManage,
    meta: { title: '任务管理' }
  },
  {
    path: '/agent',
    name: 'AgentManage',
    component: AgentManage,
    meta: { title: 'Agent管理' }
  },
  {
    path: '/plugin',
    name: 'PluginManage',
    component: PluginManage,
    meta: { title: '插件管理' }
  },
  {
    path: '/audit',
    name: 'AuditLog',
    component: AuditLog,
    meta: { title: '审计日志' }
  },
  // 404路由
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫：设置页面标题
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title
  }
  next()
})

export default router