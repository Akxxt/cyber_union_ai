<template>
  <el-tag :type="type" size="small" effect="light">
    {{ status }}
  </el-tag>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, required: true }
})

const type = computed(() => {
  const map = {
    COMPLETED: 'success',
    SUCCESS: 'success',
    PASSED: 'success',
    FAILED: 'danger',
    REJECTED: 'danger',
    TERMINATED: 'info',
    PAUSED: 'warning',
    CREATED: 'info',
    PENDING_SORT: 'info',
    PENDING_LEGISLATION: 'info',
    PENDING_CONSTITUTIONAL_REVIEW: 'info',
    PENDING_PLANNING: 'info',
    PENDING_PLAN_APPROVAL: 'info',
    PENDING_PLAN_FINAL_REVIEW: 'info',
    PENDING_EXECUTION: 'info',
    PENDING_FINAL_INSPECTION: 'info',
    PENDING_FINAL_REVIEW: 'info',
    RUNNING: 'primary',
    ACTIVE: 'success',
    INACTIVE: 'info'
  }
  return map[props.status] || 'info'
})
</script>