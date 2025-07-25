<template>
  <div class="flex items-center space-x-2">
    <div 
      :class="statusClasses" 
      class="w-3 h-3 rounded-full"
    ></div>
    <span class="text-sm">{{ label }}</span>
    <StatusBadge 
      type="status" 
      :value="normalizedStatus" 
      :text="statusText" 
      class="text-xs font-medium"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import StatusBadge from './StatusBadge.vue'

interface Props {
  status: 'active' | 'warning' | 'error' | 'inactive' | boolean
  label: string
  statusText?: string
}

const props = withDefaults(defineProps<Props>(), {
  statusText: ''
})

const normalizedStatus = computed(() => {
  return typeof props.status === 'boolean' ? (props.status ? 'active' : 'error') : props.status
})

const statusClasses = computed(() => {
  const status = normalizedStatus.value
  
  switch (status) {
    case 'active':
      return 'bg-green-500'
    case 'warning':
      return 'bg-yellow-500'
    case 'error':
      return 'bg-red-500'
    case 'inactive':
      return 'bg-gray-400'
    default:
      return 'bg-gray-400'
  }
})

const statusText = computed(() => {
  if (props.statusText) return props.statusText
  
  const status = normalizedStatus.value
  
  switch (status) {
    case 'active':
      return '正常'
    case 'warning':
      return '警告'
    case 'error':
      return '異常'
    case 'inactive':
      return '停用'
    default:
      return '未知'
  }
})
</script>
