<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
    <!-- 頁面標題 -->
    <div class="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
              實時交易策略
            </h1>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
              WebSocket + pandas-ta 自動化分析結果
            </p>
          </div>
          <div class="flex items-center space-x-4">
            <!-- 連接狀態指示器 -->
            <div class="flex items-center space-x-2">
              <div class="relative">
                <div class="w-3 h-3 rounded-full" :class="connectionStatus.color"></div>
                <div v-if="connectionStatus.active" class="absolute inset-0 w-3 h-3 rounded-full animate-ping"
                  :class="connectionStatus.color">
                </div>
              </div>
              <span class="text-sm font-medium" :class="connectionStatus.textColor">
                {{ connectionStatus.text }}
              </span>
            </div>
            <!-- 最後更新時間 -->
            <div class="text-sm text-gray-500 dark:text-gray-400">
              更新: {{ lastUpdateTime }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要內容區域 -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 統計卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <div class="flex items-center">
            <div class="p-3 rounded-full bg-blue-100 dark:bg-blue-900">
              <svg class="w-6 h-6 text-blue-600 dark:text-blue-300" fill="none" stroke="currentColor"
                viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400">活躍策略</p>
              <p class="text-2xl font-semibold text-gray-900 dark:text-white">{{ stats.activeStrategies }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <div class="flex items-center">
            <div class="p-3 rounded-full bg-green-100 dark:bg-green-900">
              <svg class="w-6 h-6 text-green-600 dark:text-green-300" fill="none" stroke="currentColor"
                viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400">成功信號</p>
              <p class="text-2xl font-semibold text-gray-900 dark:text-white">{{ stats.successfulSignals }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <div class="flex items-center">
            <div class="p-3 rounded-full bg-purple-100 dark:bg-purple-900">
              <svg class="w-6 h-6 text-purple-600 dark:text-purple-300" fill="none" stroke="currentColor"
                viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400">平均信心度</p>
              <p class="text-2xl font-semibold text-gray-900 dark:text-white">{{ stats.avgConfidence }}%</p>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <div class="flex items-center">
            <div class="p-3 rounded-full bg-orange-100 dark:bg-orange-900">
              <svg class="w-6 h-6 text-orange-600 dark:text-orange-300" fill="none" stroke="currentColor"
                viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400">即時分析</p>
              <p class="text-2xl font-semibold text-gray-900 dark:text-white">{{ stats.realTimeAnalysis }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 策略列表 -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white">實時交易策略</h2>
            <div class="flex items-center space-x-3">
              <!-- 篩選按鈕 -->
              <select v-model="selectedFilter"
                class="text-sm border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-1 bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                <option value="all">全部策略</option>
                <option value="buy">買入信號</option>
                <option value="sell">賣出信號</option>
                <option value="high-confidence">高信心度</option>
              </select>
              <button @click="refreshStrategies"
                class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors duration-200">
                <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                刷新
              </button>
            </div>
          </div>
        </div>

        <!-- 策略卡片列表 -->
        <div class="p-6">
          <div v-if="loading" class="flex items-center justify-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span class="ml-3 text-gray-500 dark:text-gray-400">載入策略中...</span>
          </div>

          <div v-else-if="filteredStrategies.length === 0" class="text-center py-12">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">暫無策略</h3>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">等待 pandas-ta 分析產生新的交易策略</p>
          </div>

          <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div v-for="strategy in filteredStrategies" :key="strategy.id"
              class="bg-gradient-to-r from-white to-gray-50 dark:from-gray-700 dark:to-gray-800 rounded-xl border border-gray-200 dark:border-gray-600 p-6 hover:shadow-lg transition-all duration-200">

              <!-- 策略標題 -->
              <div class="flex items-center justify-between mb-4">
                <div class="flex items-center space-x-3">
                  <div class="p-2 rounded-full" :class="getSignalTypeStyle(strategy.signal_type).bg">
                    <svg class="w-5 h-5" :class="getSignalTypeStyle(strategy.signal_type).text" fill="currentColor"
                      viewBox="0 0 20 20">
                      <path v-if="strategy.signal_type === 'BUY'" fill-rule="evenodd"
                        d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z"
                        clip-rule="evenodd" />
                      <path v-else fill-rule="evenodd"
                        d="M16.707 10.293a1 1 0 010 1.414l-6 6a1 1 0 01-1.414 0l-6-6a1 1 0 111.414-1.414L9 14.586V3a1 1 0 112 0v11.586l4.293-4.293a1 1 0 011.414 0z"
                        clip-rule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-white">{{ strategy.symbol }}</h3>
                    <p class="text-sm text-gray-500 dark:text-gray-400">{{ strategy.timeframe }} · {{
                      strategy.strategy_name }}</p>
                  </div>
                </div>
                <div class="text-right">
                  <div class="text-sm font-medium" :class="getSignalTypeStyle(strategy.signal_type).text">
                    {{ strategy.signal_type }}
                  </div>
                  <div class="text-xs text-gray-500 dark:text-gray-400">
                    {{ formatTime(strategy.created_at) }}
                  </div>
                </div>
              </div>

              <!-- 價格信息 -->
              <div class="grid grid-cols-3 gap-4 mb-4">
                <div class="text-center">
                  <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">進場價</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">${{ strategy.entry_price.toFixed(4) }}
                  </p>
                </div>
                <div class="text-center">
                  <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">止損價</p>
                  <p class="text-sm font-semibold text-red-600">${{ strategy.stop_loss.toFixed(4) }}</p>
                </div>
                <div class="text-center">
                  <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">止盈價</p>
                  <p class="text-sm font-semibold text-green-600">${{ strategy.take_profit.toFixed(4) }}</p>
                </div>
              </div>

              <!-- 信心度和風險回報比 -->
              <div class="flex items-center justify-between mb-4">
                <div class="flex items-center space-x-2">
                  <span class="text-sm text-gray-500 dark:text-gray-400">信心度:</span>
                  <div class="flex items-center">
                    <div class="w-16 bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                      <div class="h-2 rounded-full transition-all duration-300"
                        :class="getConfidenceColor(strategy.confidence)"
                        :style="{ width: `${strategy.confidence * 100}%` }">
                      </div>
                    </div>
                    <span class="ml-2 text-sm font-medium text-gray-900 dark:text-white">
                      {{ Math.round(strategy.confidence * 100) }}%
                    </span>
                  </div>
                </div>
                <div class="text-right">
                  <span class="text-sm text-gray-500 dark:text-gray-400">R:R </span>
                  <span class="text-sm font-medium text-gray-900 dark:text-white">
                    1:{{ strategy.risk_reward_ratio.toFixed(1) }}
                  </span>
                </div>
              </div>

              <!-- 技術指標 -->
              <div class="mb-4">
                <p class="text-xs text-gray-500 dark:text-gray-400 mb-2">技術指標</p>
                <div class="flex flex-wrap gap-2">
                  <span v-for="indicator in strategy.technical_indicators" :key="indicator"
                    class="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded-full">
                    {{ indicator }}
                  </span>
                </div>
              </div>

              <!-- 策略描述 -->
              <div class="mb-4">
                <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">分析結果</p>
                <p class="text-sm text-gray-700 dark:text-gray-300">{{ strategy.reasoning }}</p>
              </div>

              <!-- 操作按鈕 -->
              <div class="flex space-x-2">
                <button @click="viewDetails(strategy)"
                  class="flex-1 px-4 py-2 bg-gray-100 dark:bg-gray-600 hover:bg-gray-200 dark:hover:bg-gray-500 text-gray-700 dark:text-gray-200 text-sm font-medium rounded-lg transition-colors duration-200">
                  查看詳情
                </button>
                <button @click="copyStrategy(strategy)"
                  class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors duration-200">
                  複製策略
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 策略詳情模態框 -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">策略詳情</h3>
            <button @click="showModal = false" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        <div class="p-6">
          <div v-if="selectedStrategy" class="space-y-4">
            <!-- 詳細技術分析 -->
            <div>
              <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-2">技術分析詳情</h4>
              <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <pre
                  class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ selectedStrategy.detailed_analysis || '暫無詳細分析' }}</pre>
              </div>
            </div>
            <!-- 市場條件 -->
            <div>
              <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-2">市場條件</h4>
              <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <p class="text-sm text-gray-700 dark:text-gray-300">{{ selectedStrategy.market_context || '正常市場條件' }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

// 響應式數據
const strategies = ref<any[]>([])
const loading = ref(false)
const selectedFilter = ref('all')
const showModal = ref(false)
const selectedStrategy = ref<any>(null)
const lastUpdateTime = ref('')

// 統計數據
const stats = ref({
  activeStrategies: 0,
  successfulSignals: 0,
  avgConfidence: 0,
  realTimeAnalysis: 0
})

// 連接狀態
const connectionStatus = ref({
  active: true,
  color: 'bg-green-500',
  textColor: 'text-green-600 dark:text-green-400',
  text: 'WebSocket 已連接'
})

// 定時器
let updateInterval: NodeJS.Timeout | null = null

// 計算屬性
const filteredStrategies = computed(() => {
  let filtered = strategies.value

  switch (selectedFilter.value) {
    case 'buy':
      filtered = filtered.filter(s => s.signal_type === 'BUY')
      break
    case 'sell':
      filtered = filtered.filter(s => s.signal_type === 'SELL')
      break
    case 'high-confidence':
      filtered = filtered.filter(s => s.confidence >= 0.8)
      break
  }

  return filtered.sort((a, b) => b.confidence - a.confidence)
})

// 方法
const fetchStrategies = async () => {
  try {
    loading.value = true

    // 優先獲取真實的 pandas-ta 直接分析結果
    const [directResponse, scalpingResponse, signalsResponse] = await Promise.all([
      axios.get('/api/v1/scalping/pandas-ta-direct'),  // 新的 pandas-ta 直接分析端點
      axios.get('/api/v1/scalping/signals'),  // 精準篩選後的信號
      axios.get('/api/v1/signals/latest?hours=24')  // 備用模板數據
    ])

    let allStrategies = []

    // 首先添加真實的 pandas-ta 直接分析結果
    const directSignals = directResponse.data?.signals || []
    if (directSignals.length > 0) {
      allStrategies = directSignals.map((signal: any) => ({
        ...signal,
        strategy_name: signal.strategy_name || 'Pandas-TA Direct',
        technical_indicators: signal.technical_indicators || ['RSI', 'MACD', 'EMA', 'ATR', 'Volume'],
        source: 'pandas-ta-direct',
        is_real_analysis: true,
        priority: 1  // 最高優先級
      }))

      console.log(`✅ 載入 ${directSignals.length} 個 pandas-ta 直接分析信號`)
    }

    // 如果沒有直接分析信號，嘗試精準篩選信號
    if (allStrategies.length === 0) {
      const precisionSignals = scalpingResponse.data?.signals || []
      if (precisionSignals.length > 0) {
        allStrategies = precisionSignals.map((signal: any) => ({
          ...signal,
          strategy_name: signal.strategy_name || 'Pandas-TA Precision',
          technical_indicators: ['RSI', 'MACD', 'EMA', 'ATR', 'Volume'],
          source: 'pandas-ta-precision',
          is_real_analysis: true,
          priority: 2  // 次高優先級
        }))

        console.log(`✅ 載入 ${precisionSignals.length} 個精準篩選 pandas-ta 信號`)
      }
    }

    // // 如果仍然沒有真實信號，才使用模板數據作為展示
    // if (allStrategies.length === 0) {
    //   const templateSignals = signalsResponse.data || []
    //   allStrategies = templateSignals.map((signal: any) => ({
    //     ...signal,
    //     strategy_name: 'Multi-Timeframe Template',
    //     technical_indicators: ['RSI', 'MACD', 'EMA', '布林帶'],
    //     source: 'template',
    //     is_real_analysis: false,
    //     priority: 3  // 最低優先級
    //   }))

    //   console.warn(`⚠️ 使用 ${templateSignals.length} 個模板信號 - 等待真實分析`)
    // }

    strategies.value = allStrategies
    updateStats()
    lastUpdateTime.value = new Date().toLocaleTimeString('zh-TW')

  } catch (error) {
    console.error('獲取策略失敗:', error)
    connectionStatus.value = {
      active: false,
      color: 'bg-red-500',
      textColor: 'text-red-600 dark:text-red-400',
      text: '連接失敗'
    }
  } finally {
    loading.value = false
  }
}

const updateStats = () => {
  stats.value.activeStrategies = strategies.value.length
  stats.value.successfulSignals = strategies.value.filter(s => s.confidence >= 0.7).length
  stats.value.avgConfidence = strategies.value.length > 0
    ? Math.round(strategies.value.reduce((sum, s) => sum + s.confidence, 0) / strategies.value.length * 100)
    : 0
  stats.value.realTimeAnalysis = strategies.value.filter(s =>
    new Date(s.created_at).getTime() > Date.now() - 15 * 60 * 1000
  ).length
}

const refreshStrategies = async () => {
  await fetchStrategies()
}

const getSignalTypeStyle = (signalType: string) => {
  if (signalType === 'BUY' || signalType === 'LONG') {
    return {
      bg: 'bg-green-100 dark:bg-green-900',
      text: 'text-green-600 dark:text-green-300'
    }
  } else if (signalType === 'SELL' || signalType === 'SHORT') {
    return {
      bg: 'bg-red-100 dark:bg-red-900',
      text: 'text-red-600 dark:text-red-300'
    }
  }
  return {
    bg: 'bg-gray-100 dark:bg-gray-700',
    text: 'text-gray-600 dark:text-gray-300'
  }
}

const getConfidenceColor = (confidence: number) => {
  if (confidence >= 0.8) return 'bg-green-500'
  if (confidence >= 0.6) return 'bg-yellow-500'
  return 'bg-red-500'
}

const formatTime = (dateString: string) => {
  return new Date(dateString).toLocaleTimeString('zh-TW', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const viewDetails = (strategy: any) => {
  selectedStrategy.value = strategy
  showModal.value = true
}

const copyStrategy = async (strategy: any) => {
  const strategyText = `
交易策略: ${strategy.symbol}
信號類型: ${strategy.signal_type}
進場價: $${strategy.entry_price.toFixed(4)}
止損價: $${strategy.stop_loss.toFixed(4)}
止盈價: $${strategy.take_profit.toFixed(4)}
信心度: ${Math.round(strategy.confidence * 100)}%
風險回報比: 1:${strategy.risk_reward_ratio.toFixed(1)}
分析結果: ${strategy.reasoning}
  `.trim()

  try {
    await navigator.clipboard.writeText(strategyText)
    // 簡單的提示（可以改為 toast 通知）
    alert('策略已複製到剪貼板')
  } catch (error) {
    console.error('複製失敗:', error)
  }
}

// 生命週期
onMounted(() => {
  fetchStrategies()

  // 每30秒自動更新
  updateInterval = setInterval(() => {
    fetchStrategies()
  }, 30000)
})

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
})
</script>

<style scoped>
/* 自定義樣式 */
.animate-pulse-slow {
  animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
