<template>
  <div class="app-container">
    <!-- 路由出口：所有页面组件都会渲染到这里 -->
    <router-view></router-view>
  </div>
</template>

<script setup>
// 根组件无需额外逻辑，仅作为路由容器
</script>

<style scoped>
.app-container {
  width: 100%;
  min-height: 100vh;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
</style>