<template>
  <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
       @click.self="handleCancel" @keydown.esc="handleCancel">
    <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4 shadow-xl">
      <!-- 標題區 -->
      <div class="flex items-center mb-4">
        <div class="flex-shrink-0">
          <svg :class="iconColorClass" class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="iconPath"></path>
          </svg>
        </div>
        <div class="ml-3">
          <h3 class="text-lg font-medium text-gray-900">{{ title }}</h3>
        </div>
        <div class="ml-auto">
          <button @click="handleCancel" class="text-gray-400 hover:text-gray-600">
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
      </div>

      <!-- 內容區 -->
      <div class="mb-6">
        <p v-if="message" class="text-sm text-gray-600 mb-2">
          {{ message }}
        </p>
        
        <!-- 詳細內容區 - 支援自定義內容 -->
        <div v-if="details && details.length > 0" :class="detailsContainerClass">
          <ul class="text-xs space-y-1" :class="detailsTextClass">
            <li v-for="(detail, index) in details" :key="index">
              {{ detail }}
            </li>
          </ul>
        </div>

        <!-- 插槽支援完全自定義內容 -->
        <slot name="content"></slot>
      </div>

      <!-- 按鈕區 -->
      <div class="flex justify-end space-x-3">
        <button @click="handleCancel" :class="cancelButtonClass">
          {{ cancelText }}
        </button>
        <button @click="handleConfirm" :class="confirmButtonClass" :disabled="loading">
          <span v-if="loading" class="animate-spin mr-2">⏳</span>
          {{ loading ? loadingText : confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  show: boolean
  title: string
  message?: string
  details?: string[]
  confirmText?: string
  cancelText?: string
  loadingText?: string
  loading?: boolean
  type?: 'warning' | 'danger' | 'info' | 'success'
}

interface Emits {
  (e: 'confirm'): void
  (e: 'cancel'): void
  (e: 'update:show', value: boolean): void
}

const props = withDefaults(defineProps<Props>(), {
  confirmText: '確認',
  cancelText: '取消',
  loadingText: '處理中...',
  loading: false,
  type: 'warning'
})

const emit = defineEmits<Emits>()

// 根據類型計算圖標和樣式
const iconPath = computed(() => {
  switch (props.type) {
    case 'warning':
      return 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 19.5c-.77.833.192 2.5 1.732 2.5z'
    case 'danger':
      return 'M12 9v2m0 4h.01M4.93 4.93l14.14 14.14'
    case 'info':
      return 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
    case 'success':
      return 'M5 13l4 4L19 7'
    default:
      return 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 19.5c-.77.833.192 2.5 1.732 2.5z'
  }
})

const iconColorClass = computed(() => {
  switch (props.type) {
    case 'warning':
      return 'text-orange-500'
    case 'danger':
      return 'text-red-500'
    case 'info':
      return 'text-blue-500'
    case 'success':
      return 'text-green-500'
    default:
      return 'text-orange-500'
  }
})

const detailsContainerClass = computed(() => {
  switch (props.type) {
    case 'warning':
      return 'bg-yellow-50 border border-yellow-200 rounded-md p-3'
    case 'danger':
      return 'bg-red-50 border border-red-200 rounded-md p-3'
    case 'info':
      return 'bg-blue-50 border border-blue-200 rounded-md p-3'
    case 'success':
      return 'bg-green-50 border border-green-200 rounded-md p-3'
    default:
      return 'bg-yellow-50 border border-yellow-200 rounded-md p-3'
  }
})

const detailsTextClass = computed(() => {
  switch (props.type) {
    case 'warning':
      return 'text-yellow-800'
    case 'danger':
      return 'text-red-800'
    case 'info':
      return 'text-blue-800'
    case 'success':
      return 'text-green-800'
    default:
      return 'text-yellow-800'
  }
})

const confirmButtonClass = computed(() => {
  const baseClass = 'px-4 py-2 text-sm font-medium rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed'
  switch (props.type) {
    case 'warning':
      return `${baseClass} text-white bg-orange-500 hover:bg-orange-600`
    case 'danger':
      return `${baseClass} text-white bg-red-500 hover:bg-red-600`
    case 'info':
      return `${baseClass} text-white bg-blue-500 hover:bg-blue-600`
    case 'success':
      return `${baseClass} text-white bg-green-500 hover:bg-green-600`
    default:
      return `${baseClass} text-white bg-orange-500 hover:bg-orange-600`
  }
})

const cancelButtonClass = 'px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md transition-colors'

const handleConfirm = () => {
  if (!props.loading) {
    emit('confirm')
  }
}

const handleCancel = () => {
  if (!props.loading) {
    emit('cancel')
    emit('update:show', false)
  }
}
</script>
