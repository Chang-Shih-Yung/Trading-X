<template>
  <span 
    :class="badgeClasses"
    class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
  >
    <span v-if="icon" class="mr-1">{{ icon }}</span>
    {{ text }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type: 'signal' | 'confidence' | 'trend' | 'risk' | 'strategy' | 'status'
  value?: string | number
  text?: string
  icon?: string
}

const props = withDefaults(defineProps<Props>(), {
  text: '',
  icon: ''
})

const badgeClasses = computed(() => {
  const baseClasses = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium'
  
  switch (props.type) {
    case 'signal':
      if (props.value === 'LONG' || props.value === 'BUY') {
        return `${baseClasses} bg-green-100 text-green-800`
      } else if (props.value === 'SHORT' || props.value === 'SELL') {
        return `${baseClasses} bg-red-100 text-red-800`
      }
      return `${baseClasses} bg-gray-100 text-gray-800`
      
    case 'confidence':
      const confidence = typeof props.value === 'number' ? props.value : parseFloat(props.value as string || '0')
      if (confidence >= 85) {
        return `${baseClasses} bg-green-100 text-green-800`
      } else if (confidence >= 70) {
        return `${baseClasses} bg-yellow-100 text-yellow-800`
      } else if (confidence >= 50) {
        return `${baseClasses} bg-orange-100 text-orange-800`
      }
      return `${baseClasses} bg-red-100 text-red-800`
      
    case 'trend':
      if (props.value === 'bull' || props.value === '牛市') {
        return `${baseClasses} bg-emerald-100 text-emerald-800`
      } else if (props.value === 'bear' || props.value === '熊市') {
        return `${baseClasses} bg-red-100 text-red-800`
      }
      return `${baseClasses} bg-gray-100 text-gray-800`
      
    case 'risk':
      const riskRatio = typeof props.value === 'number' ? props.value : parseFloat(props.value as string || '0')
      if (riskRatio >= 2.5) {
        return `${baseClasses} bg-green-100 text-green-800`
      } else if (riskRatio >= 1.8) {
        return `${baseClasses} bg-blue-100 text-blue-800`
      } else if (riskRatio >= 1.2) {
        return `${baseClasses} bg-yellow-100 text-yellow-800`
      }
      return `${baseClasses} bg-red-100 text-red-800`
      
    case 'strategy':
      if (props.value === 'scalping' || props.text?.includes('短線')) {
        return `${baseClasses} bg-red-100 text-red-800`
      } else if (props.value === 'swing' || props.text?.includes('中長線')) {
        return `${baseClasses} bg-blue-100 text-blue-800`
      }
      return `${baseClasses} bg-purple-100 text-purple-800`
      
    case 'status':
      if (props.value === 'active' || props.value === '正常') {
        return `${baseClasses} bg-green-100 text-green-800`
      } else if (props.value === 'warning' || props.value === '警告') {
        return `${baseClasses} bg-yellow-100 text-yellow-800`
      } else if (props.value === 'error' || props.value === '異常') {
        return `${baseClasses} bg-red-100 text-red-800`
      }
      return `${baseClasses} bg-gray-100 text-gray-800`
      
    default:
      return `${baseClasses} bg-gray-100 text-gray-800`
  }
})
</script>
