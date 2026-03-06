import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index'
import { createPinia } from 'pinia'

// 引入全局样式（后续可补充）
// import './assets/style.css'

// 创建Vue应用实例
const app = createApp(App)

// 挂载路由和状态管理
app.use(router)
app.use(createPinia())

// 挂载到页面的#app节点
app.mount('#app')