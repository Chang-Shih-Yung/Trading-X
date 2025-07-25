<!--
Enhanced Dashboard Component
整合後端的牛熊市分析、動態止盈止損、短線歷史管理等功能
-->

<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <!-- Loading 覆蓋層 -->
    <LoadingOverlay :show="isLoading" :title="loadingMessage" message="請稍候..." />

    <!-- 自定義通知 -->
    <CustomNotification 
      v-if="notification.show" 
      :type="notification.type" 
      :title="notification.title"
      :message="notification.message" 
      @close="hideNotification" 
    />

    <div class="mx-auto max-w-7xl">
      <!-- 標題 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Service X - 高級交易分析</h1>
        <p class="mt-2 text-gray-600">整合牛熊市分析、動態止盈止損和智能短線信號</p>
      </div>

      <!-- 市場情緒總覽 -->
      <div class="mb-8 bg-white shadow rounded-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-900">🎯 市場情緒總覽</h2>
          <button 
            @click="refreshMarketSentiment"
            :disabled="isRefreshingMarket"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {{ isRefreshingMarket ? '分析中...' : '🔄 更新分析' }}
          </button>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
          <!-- 整體情緒 -->
          <div class="text-center">
            <div class="text-3xl mb-2">
              {{ getSentimentEmoji(marketSentiment.overall_sentiment) }}
            </div>
            <div class="text-lg font-semibold" :class="getSentimentColor(marketSentiment.overall_sentiment)">
              {{ getSentimentLabel(marketSentiment.overall_sentiment) }}
            </div>
            <div class="text-sm text-gray-600">
              情緒分數: {{ marketSentiment.sentiment_score || 0 }}
            </div>
          </div>

          <!-- 信號分布 -->
          <div class="text-center">
            <div class="text-2xl font-bold text-green-600">{{ marketSentiment.bull_signals || 0 }}</div>
            <div class="text-sm text-gray-600">多頭信號</div>
            <div class="text-2xl font-bold text-red-600">{{ marketSentiment.bear_signals || 0 }}</div>
            <div class="text-sm text-gray-600">空頭信號</div>
          </div>

          <!-- 市場分析 -->
          <div class="text-center">
            <div class="text-lg font-semibold text-blue-600">
              {{ marketSentiment.market_analysis?.avg_bull_score?.toFixed(1) || 0 }}
            </div>
            <div class="text-sm text-gray-600">平均牛市分數</div>
            <div class="text-lg font-semibold text-orange-600">
              {{ marketSentiment.market_analysis?.avg_bear_score?.toFixed(1) || 0 }}
            </div>
            <div class="text-sm text-gray-600">平均熊市分數</div>
          </div>

          <!-- 突破比例 -->
          <div class="text-center">
            <div class="text-lg font-semibold text-purple-600">
              {{ ((marketSentiment.market_analysis?.breakout_ratio || 0) * 100).toFixed(1) }}%
            </div>
            <div class="text-sm text-gray-600">突破信號比例</div>
            <div class="text-lg font-semibold text-indigo-600">
              {{ ((marketSentiment.market_analysis?.high_confidence_ratio || 0) * 100).toFixed(1) }}%
            </div>
            <div class="text-sm text-gray-600">高信心信號比例</div>
          </div>
        </div>
      </div>

      <!-- 增強短線信號 -->
      <div class="mb-8 bg-white shadow rounded-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-900">⚡ 增強短線信號</h2>
          <div class="flex gap-2">
            <select 
              v-model="signalFilters.market_condition" 
              @change="refreshEnhancedSignals"
              class="px-3 py-1 border border-gray-300 rounded-md text-sm"
            >
              <option value="">所有市場條件</option>
              <option value="bull">牛市</option>
              <option value="bear">熊市</option>
              <option value="neutral">中性</option>
            </select>
            <select 
              v-model="signalFilters.risk_level" 
              @change="refreshEnhancedSignals"
              class="px-3 py-1 border border-gray-300 rounded-md text-sm"
            >
              <option value="moderate">中等風險</option>
              <option value="conservative">保守</option>
              <option value="aggressive">激進</option>
            </select>
            <button 
              @click="refreshEnhancedSignals"
              :disabled="isRefreshingSignals"
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              {{ isRefreshingSignals ? '生成中...' : '🔄 重新生成' }}
            </button>
          </div>
        </div>

        <!-- 信號統計 -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div class="bg-blue-50 p-3 rounded-lg text-center">
            <div class="text-lg font-bold text-blue-600">{{ enhancedSignals.length }}</div>
            <div class="text-sm text-gray-600">總信號數</div>
          </div>
          <div class="bg-green-50 p-3 rounded-lg text-center">
            <div class="text-lg font-bold text-green-600">
              {{ enhancedSignals.filter(s => s.urgency_level === 'urgent' || s.urgency_level === 'high').length }}
            </div>
            <div class="text-sm text-gray-600">高優先級</div>
          </div>
          <div class="bg-purple-50 p-3 rounded-lg text-center">
            <div class="text-lg font-bold text-purple-600">
              {{ enhancedSignals.filter(s => s.is_breakout_signal).length }}
            </div>
            <div class="text-sm text-gray-600">突破信號</div>
          </div>
          <div class="bg-orange-50 p-3 rounded-lg text-center">
            <div class="text-lg font-bold text-orange-600">
              {{ enhancedSignals.length > 0 ? (enhancedSignals.reduce((sum, s) => sum + s.confidence, 0) / enhancedSignals.length * 100).toFixed(1) : 0 }}%
            </div>
            <div class="text-sm text-gray-600">平均信心度</div>
          </div>
        </div>

        <!-- 信號列表 -->
        <div class="space-y-4">
          <div 
            v-for="signal in enhancedSignals.slice(0, 10)" 
            :key="signal.id"
            class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-3">
                <span class="font-semibold text-lg">{{ signal.symbol }}</span>
                <span 
                  :class="signal.signal_type === 'LONG' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                  class="px-2 py-1 rounded-full text-xs font-medium"
                >
                  {{ signal.signal_type === 'LONG' ? '📈 做多' : '📉 做空' }}
                </span>
                <span 
                  :class="getUrgencyClass(signal.urgency_level)"
                  class="px-2 py-1 rounded-full text-xs font-medium"
                >
                  {{ getUrgencyLabel(signal.urgency_level) }}
                </span>
                <span 
                  v-if="signal.is_breakout_signal"
                  class="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium"
                >
                  🚀 突破
                </span>
              </div>
              <div class="text-right">
                <div class="text-lg font-bold">{{ (signal.confidence * 100).toFixed(1) }}%</div>
                <div class="text-sm text-gray-600">信心度</div>
              </div>
            </div>

            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
              <div>
                <div class="text-sm text-gray-600">進場價</div>
                <div class="font-semibold">${{ signal.entry_price?.toFixed(4) }}</div>
              </div>
              <div>
                <div class="text-sm text-gray-600">止損價</div>
                <div class="font-semibold text-red-600">${{ signal.stop_loss?.toFixed(4) }}</div>
              </div>
              <div>
                <div class="text-sm text-gray-600">止盈價</div>
                <div class="font-semibold text-green-600">${{ signal.take_profit?.toFixed(4) }}</div>
              </div>
              <div>
                <div class="text-sm text-gray-600">風險回報比</div>
                <div class="font-semibold">1:{{ signal.risk_reward_ratio?.toFixed(1) }}</div>
              </div>
            </div>

            <!-- 市場分析信息 -->
            <div class="bg-gray-50 p-3 rounded-lg mb-3">
              <div class="text-sm text-gray-700">
                <strong>市場分析：</strong>
                {{ signal.market_condition?.trend || 'Unknown' }}市場
                <span v-if="signal.market_phase">（{{ signal.market_phase }}）</span>
                | 牛市分數: {{ signal.bull_score?.toFixed(1) }}
                | 熊市分數: {{ signal.bear_score?.toFixed(1) }}
              </div>
              <div v-if="signal.breakout_analysis?.is_breakout" class="text-sm text-purple-700 mt-1">
                <strong>突破分析：</strong>
                {{ signal.breakout_analysis.breakout_type }} | 強度: {{ (signal.breakout_analysis.strength * 100).toFixed(1) }}%
              </div>
            </div>

            <div class="text-sm text-gray-600">
              <strong>推理：</strong>{{ signal.reasoning }}
            </div>

            <div class="flex items-center justify-between mt-3">
              <div class="text-xs text-gray-500">
                策略: {{ signal.strategy_name }} | 
                時間框架: {{ signal.primary_timeframe }} |
                過期時間: {{ formatTime(signal.expires_at) }}
              </div>
              <div class="flex gap-1">
                <span 
                  v-if="signal.atr_adjusted"
                  class="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full"
                  title="ATR調整"
                >
                  📊 ATR
                </span>
                <span 
                  v-if="signal.market_condition_adjusted"
                  class="px-2 py-1 bg-indigo-100 text-indigo-700 text-xs rounded-full"
                  title="市場條件調整"
                >
                  🎯 調整
                </span>
              </div>
            </div>
          </div>

          <div v-if="enhancedSignals.length === 0" class="text-center py-8 text-gray-500">
            暫無符合條件的增強短線信號
          </div>
        </div>
      </div>

      <!-- 歷史表現統計 -->
      <div class="mb-8 bg-white shadow rounded-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-900">📊 歷史表現統計</h2>
          <div class="flex gap-2">
            <select 
              v-model="statsFilters.days" 
              @change="refreshPerformanceStats"
              class="px-3 py-1 border border-gray-300 rounded-md text-sm"
            >
              <option value="7">過去7天</option>
              <option value="30">過去30天</option>
              <option value="90">過去90天</option>
            </select>
            <button 
              @click="refreshPerformanceStats"
              :disabled="isRefreshingStats"
              class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
            >
              {{ isRefreshingStats ? '統計中...' : '🔄 更新統計' }}
            </button>
          </div>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-5 gap-6">
          <div class="text-center">
            <div class="text-2xl font-bold text-blue-600">{{ performanceStats.overall_performance?.total_signals || 0 }}</div>
            <div class="text-sm text-gray-600">總信號數</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-green-600">
              {{ performanceStats.overall_performance?.win_rate?.toFixed(1) || 0 }}%
            </div>
            <div class="text-sm text-gray-600">勝率</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-emerald-600">
              +{{ performanceStats.overall_performance?.avg_profit_pct?.toFixed(2) || 0 }}%
            </div>
            <div class="text-sm text-gray-600">平均盈利</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-red-600">
              {{ performanceStats.overall_performance?.avg_loss_pct?.toFixed(2) || 0 }}%
            </div>
            <div class="text-sm text-gray-600">平均虧損</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-indigo-600">
              {{ performanceStats.overall_performance?.avg_hold_time_minutes?.toFixed(0) || 0 }}分鐘
            </div>
            <div class="text-sm text-gray-600">平均持有時間</div>
          </div>
        </div>

        <!-- 最佳/最差表現 -->
        <div v-if="performanceStats.best_performer || performanceStats.worst_performer" class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div v-if="performanceStats.best_performer" class="bg-green-50 p-4 rounded-lg">
            <h3 class="font-semibold text-green-800 mb-2">🏆 最佳表現</h3>
            <div class="text-sm">
              <div><strong>交易對:</strong> {{ performanceStats.best_performer.symbol }}</div>
              <div><strong>盈利:</strong> +{{ performanceStats.best_performer.profit_pct?.toFixed(2) }}%</div>
              <div><strong>策略:</strong> {{ performanceStats.best_performer.strategy }}</div>
              <div><strong>時間:</strong> {{ performanceStats.best_performer.date }}</div>
            </div>
          </div>
          <div v-if="performanceStats.worst_performer" class="bg-red-50 p-4 rounded-lg">
            <h3 class="font-semibold text-red-800 mb-2">📉 最差表現</h3>
            <div class="text-sm">
              <div><strong>交易對:</strong> {{ performanceStats.worst_performer.symbol }}</div>
              <div><strong>虧損:</strong> {{ performanceStats.worst_performer.loss_pct?.toFixed(2) }}%</div>
              <div><strong>策略:</strong> {{ performanceStats.worst_performer.strategy }}</div>
              <div><strong>時間:</strong> {{ performanceStats.worst_performer.date }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 快速操作 -->
      <div class="bg-white shadow rounded-lg p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">⚙️ 快速操作</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button 
            @click="processExpiredSignals"
            :disabled="isProcessingExpired"
            class="px-4 py-3 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50"
          >
            {{ isProcessingExpired ? '處理中...' : '🧹 處理過期信號' }}
          </button>
          <button 
            @click="recalculateHistoryResults"
            :disabled="isRecalculating"
            class="px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
          >
            {{ isRecalculating ? '重算中...' : '🔄 重算歷史結果' }}
          </button>
          <button 
            @click="navigateToHistoryAnalysis"
            class="px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            📈 歷史分析
          </button>
          <button 
            @click="exportPerformanceReport"
            :disabled="isExporting"
            class="px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            {{ isExporting ? '匯出中...' : '📄 匯出報告' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import LoadingOverlay from '@/components/LoadingOverlay.vue'
import CustomNotification from '@/components/CustomNotification.vue'

// 響應式數據
const isLoading = ref(false)
const loadingMessage = ref('')
const notification = reactive({
  show: false,
  type: 'info' as 'success' | 'error' | 'warning' | 'info',
  title: '',
  message: ''
})

// 市場情緒數據
const marketSentiment = ref<any>({})
const isRefreshingMarket = ref(false)

// 增強信號數據
const enhancedSignals = ref<any[]>([])
const isRefreshingSignals = ref(false)
const signalFilters = reactive({
  market_condition: '',
  risk_level: 'moderate'
})

// 表現統計數據
const performanceStats = ref<any>({})
const isRefreshingStats = ref(false)
const statsFilters = reactive({
  days: 7
})

// 操作狀態
const isProcessingExpired = ref(false)
const isRecalculating = ref(false)
const isExporting = ref(false)

const router = useRouter()

// 通知函數
const showNotification = (type: string, title: string, message: string = '') => {
  notification.type = type as any
  notification.title = title
  notification.message = message
  notification.show = true
}

const hideNotification = () => {
  notification.show = false
}

// 顯示載入狀態
const showLoading = (message: string) => {
  isLoading.value = true
  loadingMessage.value = message
}

const hideLoading = () => {
  isLoading.value = false
  loadingMessage.value = ''
}

// 刷新市場情緒
const refreshMarketSentiment = async () => {
  try {
    isRefreshingMarket.value = true
    const response = await axios.get('/api/v1/scalping/market-sentiment')
    marketSentiment.value = response.data
    showNotification('success', '市場情緒已更新')
  } catch (error) {
    console.error('刷新市場情緒失敗:', error)
    showNotification('error', '刷新市場情緒失敗')
  } finally {
    isRefreshingMarket.value = false
  }
}

// 刷新增強信號
const refreshEnhancedSignals = async () => {
  try {
    isRefreshingSignals.value = true
    const params = new URLSearchParams({
      min_confidence: '0.75',
      risk_level: signalFilters.risk_level
    })
    
    if (signalFilters.market_condition) {
      params.append('market_condition', signalFilters.market_condition)
    }
    
    const response = await axios.get(`/api/v1/scalping/signals?${params}`)
    enhancedSignals.value = response.data.signals || []
    showNotification('success', `已生成 ${enhancedSignals.value.length} 個增強信號`)
  } catch (error) {
    console.error('刷新增強信號失敗:', error)
    showNotification('error', '刷新增強信號失敗')
  } finally {
    isRefreshingSignals.value = false
  }
}

// 刷新表現統計
const refreshPerformanceStats = async () => {
  try {
    isRefreshingStats.value = true
    const response = await axios.get(`/api/v1/scalping/strategy-performance?days=${statsFilters.days}`)
    performanceStats.value = response.data
    showNotification('success', '表現統計已更新')
  } catch (error) {
    console.error('刷新表現統計失敗:', error)
    showNotification('error', '刷新表現統計失敗')
  } finally {
    isRefreshingStats.value = false
  }
}

// 處理過期信號
const processExpiredSignals = async () => {
  try {
    isProcessingExpired.value = true
    const response = await axios.post('/api/v1/scalping/process-expired')
    showNotification('success', '過期信號處理完成', response.data.message)
    await refreshPerformanceStats() // 更新統計
  } catch (error) {
    console.error('處理過期信號失敗:', error)
    showNotification('error', '處理過期信號失敗')
  } finally {
    isProcessingExpired.value = false
  }
}

// 重算歷史結果
const recalculateHistoryResults = async () => {
  try {
    isRecalculating.value = true
    const response = await axios.post('/api/v1/market-analysis/history/recalculate', {
      new_breakeven_threshold: 0.5
    })
    showNotification('success', '歷史結果重算完成', response.data.message)
    await refreshPerformanceStats() // 更新統計
  } catch (error) {
    console.error('重算歷史結果失敗:', error)
    showNotification('error', '重算歷史結果失敗')
  } finally {
    isRecalculating.value = false
  }
}

// 導航到歷史分析
const navigateToHistoryAnalysis = () => {
  router.push({ name: 'ShortTermHistory' })
}

// 匯出表現報告
const exportPerformanceReport = async () => {
  try {
    isExporting.value = true
    // 這裡可以實現匯出功能
    showNotification('info', '匯出功能開發中')
  } catch (error) {
    showNotification('error', '匯出失敗')
  } finally {
    isExporting.value = false
  }
}

// 輔助函數
const getSentimentEmoji = (sentiment: string) => {
  switch (sentiment) {
    case 'bullish': return '🚀'
    case 'bearish': return '📉'
    default: return '😐'
  }
}

const getSentimentLabel = (sentiment: string) => {
  switch (sentiment) {
    case 'bullish': return '看漲'
    case 'bearish': return '看跌'
    default: return '中性'
  }
}

const getSentimentColor = (sentiment: string) => {
  switch (sentiment) {
    case 'bullish': return 'text-green-600'
    case 'bearish': return 'text-red-600'
    default: return 'text-gray-600'
  }
}

const getUrgencyClass = (urgency: string) => {
  switch (urgency) {
    case 'urgent': return 'bg-red-100 text-red-800'
    case 'high': return 'bg-orange-100 text-orange-800'
    case 'medium': return 'bg-yellow-100 text-yellow-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const getUrgencyLabel = (urgency: string) => {
  switch (urgency) {
    case 'urgent': return '🔥 緊急'
    case 'high': return '⚡ 高'
    case 'medium': return '📊 中'
    default: return '💤 低'
  }
}

const formatTime = (timeStr: string) => {
  if (!timeStr) return ''
  return new Date(timeStr).toLocaleTimeString('zh-TW', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 生命週期
onMounted(async () => {
  showLoading('載入高級交易分析...')
  try {
    await Promise.all([
      refreshMarketSentiment(),
      refreshEnhancedSignals(),
      refreshPerformanceStats()
    ])
  } catch (error) {
    showNotification('error', '初始化失敗')
  } finally {
    hideLoading()
  }
})
</script>

<style scoped>
/* 自定義樣式 */
.transition-shadow {
  transition: box-shadow 0.2s ease;
}
</style>
