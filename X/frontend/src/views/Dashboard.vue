<template>
  <div class="p-6 space-y-6">
    <!-- 頁面標題 -->
    <div class="flex justify-between items-center">
      <h2 class="text-3xl font-bold text-white">監控儀表板</h2>
      <div class="flex items-center space-x-2 text-sm text-gray-400">
        <Clock class="h-4 w-4" />
        <span>最後更新: {{ lastUpdateFormatted }}</span>
        <button 
          @click="refreshData"
          :disabled="loading"
          class="ml-2 btn-secondary text-xs"
        >
          <RefreshCw :class="['h-3 w-3 mr-1', loading && 'animate-spin']" />
          刷新
        </button>
      </div>
    </div>

    <!-- 系統狀態總覽 -->
    <div class="bg-trading-secondary rounded-lg border border-gray-700 p-6">
      <h3 class="text-xl font-semibold mb-4 flex items-center">
        <Activity class="h-6 w-6 mr-2 text-green-500" />
        系統狀態總覽
      </h3>
      
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="text-center">
          <div class="text-2xl font-bold" :class="systemStore.isSystemHealthy ? 'text-green-500' : 'text-red-500'">
            {{ systemStore.systemHealth }}
          </div>
          <div class="text-sm text-gray-400">監控狀態</div>
        </div>
        
        <div class="text-center">
          <div class="text-2xl font-bold" :class="systemStore.isConnected ? 'text-green-500' : 'text-red-500'">
            {{ systemStore.isConnected ? '已啟用' : '未連接' }}
          </div>
          <div class="text-sm text-gray-400">Gmail通知</div>
        </div>
        
        <div class="text-center">
          <div class="text-2xl font-bold text-blue-500">
            {{ systemStore.uptimeFormatted }}
          </div>
          <div class="text-sm text-gray-400">運行時間</div>
        </div>
        
        <div class="text-center">
          <div class="text-2xl font-bold text-yellow-500">
            &lt;{{ systemStore.responseTime }}ms
          </div>
          <div class="text-sm text-gray-400">響應時間</div>
        </div>
      </div>
    </div>

    <!-- 今日信號處理統計 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="metric-card">
        <h3 class="text-xl font-semibold mb-4 flex items-center">
          <BarChart3 class="h-6 w-6 mr-2 text-blue-500" />
          今日信號處理統計
        </h3>
        
        <div class="space-y-4">
          <div class="flex justify-between items-center">
            <span class="text-gray-300">總接收信號</span>
            <span class="text-2xl font-bold text-white">
              {{ systemStore.performanceMetrics.today_signals.toLocaleString() }}個
            </span>
          </div>
          
          <div class="flex justify-between items-center">
            <span class="text-gray-300">EPL通過率</span>
            <div class="text-right">
              <span class="text-xl font-bold text-green-500">
                {{ systemStore.performanceMetrics.epl_pass_rate }}%
              </span>
              <span class="text-sm text-gray-400 ml-2">
                ({{ systemStore.performanceMetrics.epl_passed_count }}個)
              </span>
            </div>
          </div>
          
          <div class="flex justify-between items-center">
            <span class="text-gray-300">去重過濾</span>
            <div class="text-right">
              <span class="text-xl font-bold text-orange-500">
                {{ systemStore.performanceMetrics.duplicate_filtered }}個
              </span>
              <span class="text-sm text-gray-400 ml-2">
                ({{ systemStore.performanceMetrics.filter_rate }}%)
              </span>
            </div>
          </div>
          
          <div class="flex justify-between items-center">
            <span class="text-gray-300">最終輸出</span>
            <span class="text-2xl font-bold text-blue-500">
              {{ systemStore.performanceMetrics.final_output }}個高品質信號
            </span>
          </div>
          
          <div class="flex justify-between items-center">
            <span class="text-gray-300">成功率</span>
            <span class="text-xl font-bold text-green-500">
              {{ systemStore.performanceMetrics.success_rate }}%
            </span>
          </div>
          
          <div class="flex justify-between items-center">
            <span class="text-gray-300">平均處理時間</span>
            <span class="text-lg font-semibold text-blue-400">
              {{ systemStore.performanceMetrics.avg_processing_time }}ms
            </span>
          </div>
        </div>
      </div>

      <!-- 信號品質分布 -->
      <div class="metric-card">
        <h3 class="text-xl font-semibold mb-4 flex items-center">
          <Target class="h-6 w-6 mr-2 text-red-500" />
          信號優先級分布
        </h3>
        
        <div class="space-y-3">
          <div 
            v-for="(count, priority) in signalStore.signalsByPriority" 
            :key="priority"
            class="flex items-center justify-between p-3 rounded-lg"
            :class="getPriorityCardClass(priority)"
          >
            <div class="flex items-center">
              <div 
                class="w-4 h-4 rounded-full mr-3"
                :class="getPriorityColor(priority)"
              ></div>
              <span class="font-medium">{{ getPriorityLabel(priority) }}</span>
            </div>
            <div class="text-right">
              <div class="text-xl font-bold">{{ count }}</div>
              <div class="text-xs opacity-75">
                {{ ((count / signalStore.signals.length) * 100).toFixed(1) }}%
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 狙擊手雙層架構與系統組件狀態 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 狙擊手雙層架構 -->
      <div class="metric-card">
        <h3 class="text-lg font-semibold mb-4 flex items-center">
          <Crosshair class="h-5 w-5 mr-2 text-red-500" />
          狙擊手雙層架構
        </h3>
        
        <div class="space-y-3 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-300">Layer 1 處理時間</span>
            <span class="font-semibold">平均 {{ systemStore.systemStats.sniper.layer1_time }}ms</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-300">Layer 2 篩選率</span>
            <span class="font-semibold text-green-500">{{ systemStore.systemStats.sniper.layer2_filter_rate }}%</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-300">通過率</span>
            <span class="font-semibold text-blue-500">{{ systemStore.systemStats.sniper.accuracy }}%</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-300">實時連接狀態</span>
            <span class="font-semibold text-green-500">✅ 正常</span>
          </div>
        </div>
      </div>

      <!-- Phase 1ABC 動態系統 -->
      <div class="metric-card">
        <h3 class="text-lg font-semibold mb-4 flex items-center">
          <Zap class="h-5 w-5 mr-2 text-yellow-500" />
          Phase 1ABC 動態系統
        </h3>
        
        <div class="space-y-3 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-300">信號重建</span>
            <span class="font-semibold">{{ systemStore.systemStats.phase1abc.signal_rebuild }}%</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-300">波動適應</span>
            <span class="font-semibold">{{ systemStore.systemStats.phase1abc.volatility_adaptation }}%</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-300">標準化</span>
            <span class="font-semibold text-green-500">{{ systemStore.systemStats.phase1abc.standardization }}%</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-300">整體評分</span>
            <span class="font-semibold text-blue-500">{{ systemStore.systemStats.phase1abc.overall_score }}分</span>
          </div>
        </div>
      </div>

      <!-- Phase 2+3 完整整合 -->
      <div class="metric-card">
        <h3 class="text-lg font-semibold mb-4 flex items-center">
          <Layers class="h-5 w-5 mr-2 text-purple-500" />
          Phase 2+3 完整整合
        </h3>
        
        <div class="space-y-3 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-300">動態權重</span>
            <span class="font-semibold">{{ systemStore.systemStats.phase23.dynamic_weights }}個活躍</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-300">市場深度</span>
            <span class="font-semibold">{{ systemStore.systemStats.phase23.market_depth_levels }}級數據</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-300">風險調整</span>
            <span class="font-semibold">{{ systemStore.systemStats.phase23.risk_adjustment }}%</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-300">強化評分</span>
            <span class="font-semibold text-blue-500">{{ systemStore.systemStats.phase23.enhancement_score }}分</span>
          </div>
        </div>
      </div>
    </div>

    <!-- EPL 決策引擎與通知統計 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- EPL 決策引擎 -->
      <div class="metric-card">
        <h3 class="text-lg font-semibold mb-4 flex items-center">
          <Cpu class="h-5 w-5 mr-2 text-green-500" />
          EPL 決策引擎統計
        </h3>
        
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div class="text-center p-3 bg-blue-600 bg-opacity-20 rounded-lg">
            <div class="text-2xl font-bold text-blue-400">{{ systemStore.systemStats.epl.replacement_decisions }}</div>
            <div class="text-gray-300">🔁 替單</div>
          </div>
          <div class="text-center p-3 bg-green-600 bg-opacity-20 rounded-lg">
            <div class="text-2xl font-bold text-green-400">{{ systemStore.systemStats.epl.position_additions }}</div>
            <div class="text-gray-300">➕ 加倉</div>
          </div>
          <div class="text-center p-3 bg-purple-600 bg-opacity-20 rounded-lg">
            <div class="text-2xl font-bold text-purple-400">{{ systemStore.systemStats.epl.new_positions }}</div>
            <div class="text-gray-300">✅ 新單</div>
          </div>
          <div class="text-center p-3 bg-red-600 bg-opacity-20 rounded-lg">
            <div class="text-2xl font-bold text-red-400">{{ systemStore.systemStats.epl.ignored_signals }}</div>
            <div class="text-gray-300">❌ 忽略</div>
          </div>
        </div>
        
        <div class="mt-4 pt-4 border-t border-gray-600">
          <div class="flex justify-between">
            <span class="text-gray-300">活躍持倉</span>
            <span class="font-semibold text-yellow-500">{{ systemStore.systemStats.epl.active_positions }}個</span>
          </div>
          <div class="flex justify-between mt-2">
            <span class="text-gray-300">決策準確率</span>
            <span class="font-semibold text-green-500">{{ systemStore.systemStats.epl.decision_accuracy }}%</span>
          </div>
        </div>
      </div>

      <!-- 通知系統統計 -->
      <div class="metric-card">
        <h3 class="text-lg font-semibold mb-4 flex items-center">
          <Mail class="h-5 w-5 mr-2 text-blue-500" />
          通知系統統計
        </h3>
        
        <div class="space-y-3 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-300">Gmail發送</span>
            <div class="text-right">
              <span class="font-semibold">{{ systemStore.systemStats.notifications.gmail_sent }}封</span>
              <span class="text-green-500 ml-2">成功率: {{ systemStore.systemStats.notifications.success_rate }}%</span>
            </div>
          </div>
          
          <div class="grid grid-cols-3 gap-2 text-xs">
            <div class="text-center p-2 bg-red-600 bg-opacity-20 rounded">
              <div class="font-bold text-red-400">{{ systemStore.systemStats.notifications.critical_count }}</div>
              <div class="text-gray-400">🚨 緊急</div>
            </div>
            <div class="text-center p-2 bg-orange-600 bg-opacity-20 rounded">
              <div class="font-bold text-orange-400">{{ systemStore.systemStats.notifications.high_count }}</div>
              <div class="text-gray-400">🎯 高品質</div>
            </div>
            <div class="text-center p-2 bg-blue-600 bg-opacity-20 rounded">
              <div class="font-bold text-blue-400">{{ systemStore.systemStats.notifications.standard_count }}</div>
              <div class="text-gray-400">📊 標準</div>
            </div>
          </div>
          
          <div class="flex justify-between">
            <span class="text-gray-300">WebSocket推送</span>
            <span class="font-semibold">{{ systemStore.systemStats.notifications.websocket_pushes }}次</span>
          </div>
          
          <div class="flex justify-between">
            <span class="text-gray-300">最近通知</span>
            <span class="font-semibold">{{ systemStore.systemStats.notifications.last_notification }}</span>
          </div>
          
          <div class="flex justify-between">
            <span class="text-gray-300">冷卻狀態</span>
            <span class="font-semibold text-green-500">{{ systemStore.systemStats.notifications.cooldown_status }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSystemStore } from '@/stores/system'
import { useSignalStore } from '@/stores/signals'
import { 
  Activity, 
  BarChart3, 
  Target, 
  Clock, 
  RefreshCw,
  Crosshair,
  Zap,
  Layers,
  Cpu,
  Mail
} from 'lucide-vue-next'

const systemStore = useSystemStore()
const signalStore = useSignalStore()
const loading = ref(false)

const lastUpdateFormatted = computed(() => {
  if (!signalStore.lastUpdate) return '從未'
  return new Date(signalStore.lastUpdate).toLocaleString('zh-TW')
})

// 獲取優先級標籤
function getPriorityLabel(priority) {
  const labels = {
    CRITICAL: '🚨 緊急信號',
    HIGH: '🎯 高品質',
    MEDIUM: '📊 標準',
    LOW: '📈 參考',
    REJECTED: '❌ 已拒絕'
  }
  return labels[priority] || priority
}

// 獲取優先級顏色
function getPriorityColor(priority) {
  const colors = {
    CRITICAL: 'bg-red-500',
    HIGH: 'bg-orange-500',
    MEDIUM: 'bg-blue-500',
    LOW: 'bg-gray-500',
    REJECTED: 'bg-gray-700'
  }
  return colors[priority] || 'bg-gray-500'
}

// 獲取優先級卡片樣式
function getPriorityCardClass(priority) {
  const classes = {
    CRITICAL: 'bg-red-600 bg-opacity-10 border border-red-600 border-opacity-30',
    HIGH: 'bg-orange-600 bg-opacity-10 border border-orange-600 border-opacity-30',
    MEDIUM: 'bg-blue-600 bg-opacity-10 border border-blue-600 border-opacity-30',
    LOW: 'bg-gray-600 bg-opacity-10 border border-gray-600 border-opacity-30',
    REJECTED: 'bg-gray-800 bg-opacity-50 border border-gray-700'
  }
  return classes[priority] || 'bg-gray-600 bg-opacity-10'
}

// 刷新數據
async function refreshData() {
  loading.value = true
  try {
    await Promise.all([
      systemStore.checkSystemHealth(),
      signalStore.fetchSignals()
    ])
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  refreshData()
})
</script>
