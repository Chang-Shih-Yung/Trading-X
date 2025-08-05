<template>
  <div class="p-6 space-y-6">
    <!-- 頁面標題 -->
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-3xl font-bold text-white">實時監控</h2>
        <p class="text-gray-400 mt-1">實時追蹤系統性能與信號流動</p>
      </div>
      
      <div class="flex items-center space-x-3">
        <div 
          :class="[
            'px-3 py-1 rounded-full text-sm font-medium flex items-center',
            systemStore.isConnected ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
          ]"
        >
          <div 
            :class="[
              'w-2 h-2 rounded-full mr-2',
              systemStore.isConnected ? 'bg-green-300 animate-pulse' : 'bg-red-300'
            ]"
          ></div>
          {{ systemStore.isConnected ? 'LIVE' : 'OFFLINE' }}
        </div>
        
        <button 
          @click="toggleConnection"
          :class="[
            'btn-secondary',
            systemStore.isConnected ? 'hover:bg-red-600' : 'hover:bg-green-600'
          ]"
        >
          {{ systemStore.isConnected ? '斷開連接' : '重新連接' }}
        </button>
      </div>
    </div>

    <!-- 實時系統指標 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="metric-card text-center">
        <div class="text-2xl font-bold text-green-500">{{ realtimeMetrics.cpu_usage }}%</div>
        <div class="text-gray-300 text-sm">CPU 使用率</div>
        <div class="w-full bg-gray-700 rounded-full h-2 mt-2">
          <div 
            class="bg-green-500 h-2 rounded-full transition-all duration-300"
            :style="{ width: realtimeMetrics.cpu_usage + '%' }"
          ></div>
        </div>
      </div>
      
      <div class="metric-card text-center">
        <div class="text-2xl font-bold text-blue-500">{{ realtimeMetrics.memory_usage }}%</div>
        <div class="text-gray-300 text-sm">記憶體使用</div>
        <div class="w-full bg-gray-700 rounded-full h-2 mt-2">
          <div 
            class="bg-blue-500 h-2 rounded-full transition-all duration-300"
            :style="{ width: realtimeMetrics.memory_usage + '%' }"
          ></div>
        </div>
      </div>
      
      <div class="metric-card text-center">
        <div class="text-2xl font-bold text-yellow-500">{{ realtimeMetrics.active_connections }}</div>
        <div class="text-gray-300 text-sm">活躍連接</div>
      </div>
      
      <div class="metric-card text-center">
        <div class="text-2xl font-bold text-purple-500">{{ realtimeMetrics.requests_per_second }}/s</div>
        <div class="text-gray-300 text-sm">請求/秒</div>
      </div>
    </div>

    <!-- 實時信號流 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 信號處理流水線 -->
      <div class="bg-trading-secondary rounded-lg border border-gray-700 p-6">
        <h3 class="text-xl font-semibold mb-4 flex items-center">
          <Activity class="h-6 w-6 mr-2 text-green-500" />
          信號處理流水線
        </h3>
        
        <div class="space-y-4">
          <!-- 候選池階段 -->
          <div class="flex items-center justify-between p-3 bg-blue-600 bg-opacity-20 rounded-lg">
            <div>
              <div class="font-semibold">信號候選池</div>
              <div class="text-sm text-gray-400">Signal Candidate Pool</div>
            </div>
            <div class="text-right">
              <div class="text-2xl font-bold text-blue-400">{{ pipeline.candidate_pool }}</div>
              <div class="text-xs text-gray-400">待處理</div>
            </div>
          </div>
          
          <!-- EPL處理階段 -->
          <div class="flex items-center justify-between p-3 bg-yellow-600 bg-opacity-20 rounded-lg">
            <div>
              <div class="font-semibold">EPL 處理中</div>
              <div class="text-sm text-gray-400">Execution Policy Layer</div>
            </div>
            <div class="text-right">
              <div class="text-2xl font-bold text-yellow-400">{{ pipeline.epl_processing }}</div>
              <div class="text-xs text-gray-400">分析中</div>
            </div>
          </div>
          
          <!-- 品質控制階段 -->
          <div class="flex items-center justify-between p-3 bg-green-600 bg-opacity-20 rounded-lg">
            <div>
              <div class="font-semibold">品質控制</div>
              <div class="text-sm text-gray-400">Quality Control</div>
            </div>
            <div class="text-right">
              <div class="text-2xl font-bold text-green-400">{{ pipeline.quality_control }}</div>
              <div class="text-xs text-gray-400">通過率</div>
            </div>
          </div>
          
          <!-- 最終輸出階段 -->
          <div class="flex items-center justify-between p-3 bg-purple-600 bg-opacity-20 rounded-lg">
            <div>
              <div class="font-semibold">最終輸出</div>
              <div class="text-sm text-gray-400">Final Output</div>
            </div>
            <div class="text-right">
              <div class="text-2xl font-bold text-purple-400">{{ pipeline.final_output }}</div>
              <div class="text-xs text-gray-400">已發送</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 實時活動日誌 -->
      <div class="bg-trading-secondary rounded-lg border border-gray-700">
        <div class="p-6 border-b border-gray-700">
          <h3 class="text-xl font-semibold flex items-center">
            <ScrollText class="h-6 w-6 mr-2 text-blue-500" />
            實時活動日誌
          </h3>
        </div>
        
        <div class="h-80 overflow-y-auto p-4 space-y-2">
          <div 
            v-for="log in activityLogs" 
            :key="log.id"
            class="flex items-start space-x-3 p-2 hover:bg-trading-accent hover:bg-opacity-30 rounded text-sm slide-in"
          >
            <div 
              :class="[
                'w-2 h-2 rounded-full mt-2 flex-shrink-0',
                getLogLevelColor(log.level)
              ]"
            ></div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between">
                <span class="font-medium text-white">{{ log.message }}</span>
                <span class="text-xs text-gray-400">{{ formatLogTime(log.timestamp) }}</span>
              </div>
              <div v-if="log.details" class="text-gray-400 text-xs mt-1">{{ log.details }}</div>
            </div>
          </div>
          
          <div v-if="activityLogs.length === 0" class="text-center text-gray-400 py-8">
            <FileText class="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>暫無活動記錄</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 性能趨勢圖表 -->
    <div class="bg-trading-secondary rounded-lg border border-gray-700 p-6">
      <h3 class="text-xl font-semibold mb-4 flex items-center">
        <TrendingUp class="h-6 w-6 mr-2 text-green-500" />
        性能趨勢監控
      </h3>
      
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- 信號處理速度 -->
        <div class="text-center">
          <div class="text-3xl font-bold text-blue-500 mb-2">{{ performanceTrends.processing_speed }}ms</div>
          <div class="text-gray-300 text-sm mb-4">平均處理時間</div>
          <div class="h-20 bg-trading-accent rounded-lg flex items-end justify-center space-x-1 p-2">
            <div 
              v-for="(value, index) in performanceTrends.speed_history" 
              :key="index"
              class="bg-blue-500 rounded-t"
              :style="{ 
                width: '8px', 
                height: Math.max(4, (value / 200) * 100) + '%' 
              }"
            ></div>
          </div>
        </div>
        
        <!-- 通過率趨勢 -->
        <div class="text-center">
          <div class="text-3xl font-bold text-green-500 mb-2">{{ performanceTrends.success_rate }}%</div>
          <div class="text-gray-300 text-sm mb-4">信號通過率</div>
          <div class="h-20 bg-trading-accent rounded-lg flex items-end justify-center space-x-1 p-2">
            <div 
              v-for="(value, index) in performanceTrends.success_history" 
              :key="index"
              class="bg-green-500 rounded-t"
              :style="{ 
                width: '8px', 
                height: Math.max(4, value) + '%' 
              }"
            ></div>
          </div>
        </div>
        
        <!-- 錯誤率監控 -->
        <div class="text-center">
          <div class="text-3xl font-bold text-red-500 mb-2">{{ performanceTrends.error_rate }}%</div>
          <div class="text-gray-300 text-sm mb-4">錯誤率</div>
          <div class="h-20 bg-trading-accent rounded-lg flex items-end justify-center space-x-1 p-2">
            <div 
              v-for="(value, index) in performanceTrends.error_history" 
              :key="index"
              class="bg-red-500 rounded-t"
              :style="{ 
                width: '8px', 
                height: Math.max(4, value * 10) + '%' 
              }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="bg-trading-secondary rounded-lg border border-gray-700 p-6">
      <h3 class="text-xl font-semibold mb-4 flex items-center">
        <Zap class="h-6 w-6 mr-2 text-yellow-500" />
        快速操作
      </h3>
      
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <button @click="testSystemHealth" class="btn-secondary flex items-center justify-center">
          <Heart class="h-4 w-4 mr-2" />
          健康檢查
        </button>
        
        <button @click="clearLogs" class="btn-secondary flex items-center justify-center">
          <Trash2 class="h-4 w-4 mr-2" />
          清除日誌
        </button>
        
        <button @click="sendTestNotification" class="btn-secondary flex items-center justify-center">
          <Bell class="h-4 w-4 mr-2" />
          測試通知
        </button>
        
        <button @click="exportLogs" class="btn-secondary flex items-center justify-center">
          <Download class="h-4 w-4 mr-2" />
          導出日誌
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { useSystemStore } from '@/stores/system'
import { 
  Activity, 
  ScrollText, 
  TrendingUp, 
  Zap, 
  Heart, 
  Trash2, 
  Bell, 
  Download,
  FileText
} from 'lucide-vue-next'

const systemStore = useSystemStore()

// 實時指標
const realtimeMetrics = reactive({
  cpu_usage: 45,
  memory_usage: 62,
  active_connections: 7,
  requests_per_second: 23
})

// 信號處理流水線
const pipeline = reactive({
  candidate_pool: 12,
  epl_processing: 3,
  quality_control: 89,
  final_output: 156
})

// 性能趨勢
const performanceTrends = reactive({
  processing_speed: 156,
  success_rate: 89,
  error_rate: 1.2,
  speed_history: [120, 145, 156, 143, 167, 134, 156, 142, 158, 156],
  success_history: [92, 88, 91, 89, 94, 87, 89, 90, 88, 89],
  error_history: [0.8, 1.2, 0.9, 1.1, 0.7, 1.5, 1.2, 1.0, 1.3, 1.2]
})

// 活動日誌
const activityLogs = ref([])
let logId = 1

// 監控間隔
let metricsInterval = null
let logsInterval = null

onMounted(() => {
  startRealtimeMonitoring()
  generateInitialLogs()
})

onBeforeUnmount(() => {
  stopRealtimeMonitoring()
})

// 開始實時監控
function startRealtimeMonitoring() {
  // 更新實時指標
  metricsInterval = setInterval(() => {
    realtimeMetrics.cpu_usage = Math.max(20, Math.min(90, realtimeMetrics.cpu_usage + (Math.random() - 0.5) * 10))
    realtimeMetrics.memory_usage = Math.max(30, Math.min(85, realtimeMetrics.memory_usage + (Math.random() - 0.5) * 8))
    realtimeMetrics.active_connections = Math.max(3, Math.min(15, realtimeMetrics.active_connections + Math.floor((Math.random() - 0.5) * 3)))
    realtimeMetrics.requests_per_second = Math.max(10, Math.min(50, realtimeMetrics.requests_per_second + Math.floor((Math.random() - 0.5) * 8)))
    
    // 更新流水線數據
    pipeline.candidate_pool = Math.max(0, Math.min(25, pipeline.candidate_pool + Math.floor((Math.random() - 0.5) * 6)))
    pipeline.epl_processing = Math.max(0, Math.min(8, pipeline.epl_processing + Math.floor((Math.random() - 0.5) * 2)))
  }, 2000)
  
  // 生成活動日誌
  logsInterval = setInterval(generateRandomLog, 3000)
}

// 停止實時監控
function stopRealtimeMonitoring() {
  if (metricsInterval) {
    clearInterval(metricsInterval)
    metricsInterval = null
  }
  if (logsInterval) {
    clearInterval(logsInterval)
    logsInterval = null
  }
}

// 生成隨機日誌
function generateRandomLog() {
  const logTypes = [
    { level: 'info', message: '信號處理完成', details: 'BTCUSDT BUY 信號已通過 EPL 評估' },
    { level: 'success', message: 'Gmail 通知發送成功', details: '高品質信號通知已發送' },
    { level: 'warning', message: 'CPU 使用率偏高', details: `當前 CPU 使用率: ${realtimeMetrics.cpu_usage}%` },
    { level: 'info', message: 'WebSocket 連接正常', details: `活躍連接數: ${realtimeMetrics.active_connections}` },
    { level: 'success', message: '信號品質檢查通過', details: 'Phase1ABC 動態系統評分: 85分' },
    { level: 'info', message: 'EPL 決策執行', details: '替單決策：ETHUSDT 信號優先級提升' }
  ]
  
  const randomLog = logTypes[Math.floor(Math.random() * logTypes.length)]
  
  addLog(randomLog.level, randomLog.message, randomLog.details)
}

// 添加日誌條目
function addLog(level, message, details = null) {
  activityLogs.value.unshift({
    id: logId++,
    level,
    message,
    details,
    timestamp: new Date()
  })
  
  // 保持日誌數量在合理範圍
  if (activityLogs.value.length > 50) {
    activityLogs.value = activityLogs.value.slice(0, 50)
  }
}

// 生成初始日誌
function generateInitialLogs() {
  addLog('success', '系統啟動完成', 'Trading X 監控系統已成功啟動')
  addLog('info', 'WebSocket 連接建立', '實時監控連接已建立')
  addLog('success', '狙擊手雙層架構載入', 'Layer 1 & 2 已就緒')
  addLog('info', 'Phase1ABC 系統初始化', '動態適應系統已啟動')
}

// 獲取日誌級別顏色
function getLogLevelColor(level) {
  const colors = {
    info: 'bg-blue-500',
    success: 'bg-green-500',
    warning: 'bg-yellow-500',
    error: 'bg-red-500'
  }
  return colors[level] || 'bg-gray-500'
}

// 格式化日誌時間
function formatLogTime(timestamp) {
  return timestamp.toLocaleTimeString('zh-TW', { 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit' 
  })
}

// 切換連接狀態
function toggleConnection() {
  if (systemStore.isConnected) {
    systemStore.disconnectWebSocket()
    stopRealtimeMonitoring()
    addLog('warning', 'WebSocket 連接已斷開', '實時監控已停止')
  } else {
    systemStore.initializeWebSocket()
    startRealtimeMonitoring()
    addLog('success', 'WebSocket 重新連接', '實時監控已恢復')
  }
}

// 測試系統健康
async function testSystemHealth() {
  addLog('info', '執行系統健康檢查', '正在檢查所有組件狀態...')
  
  try {
    await systemStore.checkSystemHealth()
    addLog('success', '系統健康檢查完成', `系統狀態: ${systemStore.systemHealth}`)
  } catch (error) {
    addLog('error', '系統健康檢查失敗', error.message)
  }
}

// 清除日誌
function clearLogs() {
  activityLogs.value = []
  addLog('info', '活動日誌已清除', '日誌歷史記錄已重置')
}

// 發送測試通知
async function sendTestNotification() {
  addLog('info', '發送測試通知', '正在測試 Gmail 通知系統...')
  
  try {
    await systemStore.testNotificationSystem()
    addLog('success', '測試通知發送成功', 'Gmail 通知系統運作正常')
  } catch (error) {
    addLog('error', '測試通知發送失敗', error.message)
  }
}

// 導出日誌
function exportLogs() {
  const logsData = activityLogs.value.map(log => ({
    timestamp: log.timestamp.toISOString(),
    level: log.level,
    message: log.message,
    details: log.details
  }))
  
  const blob = new Blob([JSON.stringify(logsData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `trading-x-logs-${new Date().toISOString().split('T')[0]}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  
  addLog('success', '日誌導出完成', `已導出 ${logsData.length} 條日誌記錄`)
}
</script>
