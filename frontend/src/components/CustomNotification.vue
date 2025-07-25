<template>
  <div v-if="show" class="fixed top-4 right-4 z-50 max-w-sm">
    <div 
      :class="`rounded-lg shadow-lg p-4 transform transition-all duration-300 ${
        type === 'success' ? 'bg-green-100 border-l-4 border-green-500' :
        type === 'error' ? 'bg-red-100 border-l-4 border-red-500' :
        type === 'warning' ? 'bg-yellow-100 border-l-4 border-yellow-500' :
        'bg-blue-100 border-l-4 border-blue-500'
      }`"
    >
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <!-- Success Icon -->
          <svg v-if="type === 'success'" class="h-5 w-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
          </svg>
          <!-- Error Icon -->
          <svg v-else-if="type === 'error'" class="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
          </svg>
          <!-- Warning Icon -->
          <svg v-else-if="type === 'warning'" class="h-5 w-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
          </svg>
          <!-- Info Icon -->
          <svg v-else class="h-5 w-5 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
          </svg>
        </div>
        <div class="ml-3 flex-1">
          <h3 :class="`text-sm font-medium ${
            type === 'success' ? 'text-green-800' :
            type === 'error' ? 'text-red-800' :
            type === 'warning' ? 'text-yellow-800' :
            'text-blue-800'
          }`">
            {{ title }}
          </h3>
          <p v-if="message" :class="`mt-1 text-sm ${
            type === 'success' ? 'text-green-700' :
            type === 'error' ? 'text-red-700' :
            type === 'warning' ? 'text-yellow-700' :
            'text-blue-700'
          }`">
            {{ message }}
          </p>
        </div>
        <button 
          @click="close"
          :class="`ml-4 inline-flex text-sm ${
            type === 'success' ? 'text-green-500 hover:text-green-600' :
            type === 'error' ? 'text-red-500 hover:text-red-600' :
            type === 'warning' ? 'text-yellow-500 hover:text-yellow-600' :
            'text-blue-500 hover:text-blue-600'
          }`"
        >
          <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Props {
  type?: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
  duration?: number
  show?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'info',
  duration: 4000,
  show: false
})

const emit = defineEmits<{
  close: []
}>()

const show = ref(props.show)

const close = () => {
  show.value = false
  emit('close')
}

onMounted(() => {
  show.value = true
  if (props.duration > 0) {
    setTimeout(() => {
      close()
    }, props.duration)
  }
})
</script>
