<template>
  <div ref="chartRef" style="width: 100%; height: 400px;"></div>
  <div v-if="selectedNode" class="node-detail">
    <h4>节点详情</h4>
    <pre>{{ selectedNode }}</pre>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  nodes: { type: Array, default: () => [] },
  edges: { type: Array, default: () => [] }
})

const chartRef = ref(null)
const selectedNode = ref(null)
let chart = null

const initChart = () => {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value)
  updateChart()
  chart.on('click', (params) => {
    if (params.componentType === 'series' && params.dataType === 'node') {
      const node = props.nodes.find(n => n.id === params.data.name)
      selectedNode.value = node
    }
  })
}

const updateChart = () => {
  if (!chart) return
  const option = {
    title: { text: '任务执行流程图', left: 'center' },
    tooltip: {},
    series: [{
      type: 'graph',
      layout: 'none',
      symbolSize: 50,
      roam: true,
      label: { show: true, position: 'bottom', formatter: '{b}' },
      edgeSymbol: ['circle', 'arrow'],
      edgeLabel: { fontSize: 12 },
      data: props.nodes.map(node => ({
        name: node.id,
        label: node.label,
        category: node.status === 'success' ? 0 : node.status === 'failed' ? 1 : node.status === 'running' ? 2 : 3,
        itemStyle: {
          color: node.status === 'success' ? '#67C23A' : node.status === 'failed' ? '#F56C6C' : node.status === 'running' ? '#409EFF' : '#909399'
        }
      })),
      links: props.edges.map(edge => ({
        source: edge.from,
        target: edge.to
      })),
      categories: [
        { name: '成功', itemStyle: { color: '#67C23A' } },
        { name: '失败', itemStyle: { color: '#F56C6C' } },
        { name: '运行中', itemStyle: { color: '#409EFF' } },
        { name: '默认', itemStyle: { color: '#909399' } }
      ],
      lineStyle: { color: '#aaa', curveness: 0.2, width: 2 }
    }]
  }
  chart.setOption(option)
}

watch(() => props.nodes, updateChart, { deep: true })
watch(() => props.edges, updateChart, { deep: true })

onMounted(() => {
  initChart()
  window.addEventListener('resize', () => chart?.resize())
})
</script>

<style scoped>
.node-detail {
  margin-top: 16px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  max-height: 200px;
  overflow: auto;
}
pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>