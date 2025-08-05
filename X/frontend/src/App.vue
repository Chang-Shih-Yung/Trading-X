<template>
  <div id="app" class="min-h-screen bg-trading-primary text-white">
    <!-- 頂部導航 -->
    <nav class="bg-trading-secondary border-b border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <!-- Logo -->
            <div class="flex-shrink-0 flex items-center">
              <Target class="h-8 w-8 text-blue-400 mr-3" />
              <h1 class="text-xl font-bold">Trading X</h1>
              <span class="ml-2 text-sm text-gray-400">專業信號品質控制監控</span>
            </div>
          </div>
          
          <!-- 系統狀態指示器 -->
          <div class="flex items-center space-x-4">
            <div class="flex items-center">
              <div 
                :class="[
                  'status-indicator',
                  systemStore.isSystemHealthy ? 'bg-green-500' : 'bg-red-500'
                ]"
              ></div>
              <span class="text-sm">{{ systemStore.systemHealth }}</span>
            </div>
            
            <div class="flex items-center">
              <Wifi 
                :class="[
                  'h-4 w-4 mr-1',
                  systemStore.isConnected ? 'text-green-500' : 'text-red-500'
                ]" 
              />
              <span class="text-sm">
                {{ systemStore.isConnected ? '已連接' : '未連接' }}
              </span>
            </div>
            
            <div class="text-sm text-gray-400">
              運行時間: {{ systemStore.uptimeFormatted }}
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主要內容區域 -->
    <div class="flex">
      <!-- 側邊導航 -->
      <aside class="w-64 bg-trading-secondary h-screen sticky top-0">
        <nav class="mt-8 px-4">
          <ul class="space-y-2">
            <li v-for="route in navigation" :key="route.name">
              <router-link
                :to="{ name: route.name }"
                :class="[
                  'group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-200',
                  $route.name === route.name
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                ]"
              >
                <component 
                  :is="route.meta.icon" 
                  class="mr-3 h-5 w-5 flex-shrink-0" 
                />
                {{ route.meta.title }}
              </router-link>
            </li>
          </ul>
        </nav>
      </aside>

      <!-- 主要內容 -->
      <main class="flex-1 overflow-y-auto">
        <router-view />
      </main>
    </div>

    <!-- 全域通知 -->
    <div 
      v-if="showNotification"
      class="fixed top-4 right-4 z-50 max-w-sm w-full bg-red-600 border border-red-500 rounded-lg shadow-lg"
    >
      <div class="p-4">
        <div class="flex items-start">
          <AlertTriangle class="h-6 w-6 text-white mr-3 flex-shrink-0 mt-0.5" />
          <div class="flex-1">
            <h3 class="text-sm font-medium text-white">系統通知</h3>
            <p class="mt-1 text-sm text-red-100">{{ notificationMessage }}</p>
          </div>
          <button 
            @click="showNotification = false"
            class="ml-4 inline-flex text-red-200 hover:text-white"
          >
            <X class="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useSystemStore } from '@/stores/system'
import { useSignalStore } from '@/stores/signals'
import { 
  Target, 
  Wifi, 
  AlertTriangle, 
  X, 
  BarChart3,
  Activity,
  Settings
} from 'lucide-vue-next'

const router = useRouter()
const systemStore = useSystemStore()
const signalStore = useSignalStore()

// 通知狀態
const showNotification = ref(false)
const notificationMessage = ref('')

// 導航選項
const navigation = computed(() => router.getRoutes().filter(route => route.meta?.title))

// 組件掛載時初始化
onMounted(() => {
  // 初始化系統監控
  systemStore.initialize()
  
  // 獲取初始信號數據
  signalStore.fetchSignals()
  
  // 監聽 WebSocket 事件
  if (systemStore.socket) {
    systemStore.socket.on('critical_signal', handleCriticalSignal)
    systemStore.socket.on('system_alert', handleSystemAlert)
  }
})

// 組件卸載時清理
onBeforeUnmount(() => {
  systemStore.cleanup()
})

// 處理緊急信號通知
function handleCriticalSignal(signal) {
  showNotification.value = true
  notificationMessage.value = `🚨 緊急信號: ${signal.symbol} ${signal.signal_type}`
  
  // 自動隱藏通知
  setTimeout(() => {
    showNotification.value = false
  }, 10000)
  
  // 添加到信號列表
  signalStore.addSignal(signal)
}

// 處理系統警報
function handleSystemAlert(alert) {
  showNotification.value = true
  notificationMessage.value = alert.message
  
  setTimeout(() => {
    showNotification.value = false
  }, 8000)
}
</script>
