<template>
  <div class="home-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>赛博合众国AI协作架构 - 监控大屏</h1>
    </div>

    <!-- 核心统计卡片 -->
    <div class="stats-card-group">
      <div class="stat-card">
        <div class="stat-title">总任务数</div>
        <div class="stat-value">{{ stats.totalTasks }}</div>
        <div class="stat-desc">已完成 {{ stats.completedTasks }} | 运行中 {{ stats.runningTasks }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">Token总消耗</div>
        <div class="stat-value">{{ formatNumber(stats.totalTokens) }}</div>
        <div class="stat-desc">今日新增 {{ formatNumber(stats.todayTokens) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">Agent调用次数</div>
        <div class="stat-value">{{ formatNumber(stats.agentCalls) }}</div>
        <div class="stat-desc">总统 {{ stats.presidentCalls }} | 国会 {{ stats.congressCalls }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">插件启用数</div>
        <div class="stat-value">{{ stats.enabledPlugins }} / {{ stats.totalPlugins }}</div>
        <div class="stat-desc">内置 {{ stats.builtinPlugins }} | 第三方 {{ stats.thirdPlugins }}</div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="chart-group">
      <!-- 任务状态分布 -->
      <div class="chart-card">
        <div class="chart-title">任务状态分布</div>
        <div id="taskStatusChart" class="chart-container"></div>
      </div>
      <!-- Token消耗趋势 -->
      <div class="chart-card">
        <div class="chart-title">Token消耗趋势（近7天）</div>
        <div id="tokenTrendChart" class="chart-container"></div>
      </div>
    </div>

    <!-- 演示任务快捷入口 -->
    <div class="demo-task-card">
      <div class="demo-title">演示任务</div>
      <div class="demo-content">
        <p>已预置「新能源政策制定」演示任务，点击查看完整执行轨迹：</p>
        <button @click="goToTaskDetail" class="demo-btn">查看演示任务</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { formatNumber } from '../utils/index'

// 路由实例
const router = useRouter()

// 模拟统计数据
const stats = ref({
  totalTasks: 128,
  completedTasks: 115,
  runningTasks: 8,
  totalTokens: 385600,
  todayTokens: 12500,
  agentCalls: 2560,
  presidentCalls: 480,
  congressCalls: 620,
  enabledPlugins: 12,
  totalPlugins: 15,
  builtinPlugins: 8,
  thirdPlugins: 7
})

// 工具函数：数字格式化
const formatNum = (num) => formatNumber(num)

// 跳转到演示任务详情
const goToTaskDetail = () => {
  router.push({
    name: 'TaskManage',
    query: { taskId: 'demo_task_energy_policy' }
  })
}

// 挂载后初始化图表（ECharts占位，后续可补充完整配置）
onMounted(() => {
  // 这里后续引入ECharts并初始化图表
  // 示例：
  // import * as echarts from 'echarts'
  // const taskStatusChart = echarts.init(document.getElementById('taskStatusChart'))
  // taskStatusChart.setOption({...})
  console.log('监控大屏初始化完成')
})
</script>

<style scoped>
/* 页面整体样式 */
.home-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

/* 页面标题 */
.page-header {
  margin-bottom: 20px;
}
.page-header h1 {
  font-size: 24px;
  color: #1f2937;
  margin: 0;
}

/* 统计卡片组 */
.stats-card-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

/* 单个统计卡片 */
.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.stat-title {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 8px;
}
.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 4px;
}
.stat-desc {
  font-size: 12px;
  color: #9ca3af;
}

/* 图表区域 */
.chart-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}
.chart-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.chart-title {
  font-size: 16px;
  color: #1f2937;
  margin-bottom: 16px;
}
.chart-container {
  width: 100%;
  height: 300px;
  background-color: #f9fafb;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  font-size: 14px;
}

/* 演示任务卡片 */
.demo-task-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.demo-title {
  font-size: 16px;
  color: #1f2937;
  margin-bottom: 12px;
  font-weight: 600;
}
.demo-content p {
  font-size: 14px;
  color: #4b5563;
  margin: 0 0 12px 0;
}
.demo-btn {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
.demo-btn:hover {
  background-color: #2563eb;
}
</style>