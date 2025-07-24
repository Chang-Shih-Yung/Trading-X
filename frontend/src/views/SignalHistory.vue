<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <!-- Loading 覆蓋層 -->
    <LoadingOverlay 
      :show="isLoading" 
      :title="loadingMessage"
      message="請稍候..."
    />
    
    <div class="mx-auto max-w-7xl">
      <!-- 標題 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">📊 交易信號歷史管理</h1>
        <p class="mt-2 text-gray-600">完整的信號歷史記錄、分析與統計</p>
      </div>

      <!-- 統計概覽 -->
      <div class="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-5">
        <div v-for="(category, symbol) in signalCategories" :key="symbol" 
             class="bg-white shadow rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer"
             @click="selectedCategory = symbol"
             :class="selectedCategory === symbol ? 'ring-2 ring-blue-500 bg-blue-50' : ''">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-lg font-semibold text-gray-900">{{ category.name }}</h3>
              <p class="text-sm text-gray-500">{{ symbol }}</p>
            </div>
            <div class="text-right">
              <div class="text-2xl font-bold text-blue-600">{{ category.count }}</div>
              <div class="text-sm text-gray-500">歷史信號</div>
            </div>
          </div>
          
          <!-- 勝率統計 -->
          <div class="mt-4 pt-4 border-t border-gray-200">
            <div class="flex justify-between text-sm">
              <span class="text-gray-600">平均勝率</span>
              <span class="font-medium text-green-600">{{ calculateWinRate(symbol) }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 篩選和控制面板 -->
      <div class="mb-6 bg-white shadow rounded-lg p-6">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div class="flex items-center space-x-4">
            <!-- 幣種篩選 -->
            <div class="flex items-center space-x-2">
              <label class="text-sm font-medium text-gray-700">幣種:</label>
              <select 
                v-model="selectedCategory" 
                class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="ALL">所有幣種</option>
                <option v-for="(category, symbol) in signalCategories" :key="symbol" :value="symbol">
                  {{ category.name }} ({{ category.count }})
                </option>
              </select>
            </div>
            
            <!-- 信號類型篩選 -->
            <div class="flex items-center space-x-2">
              <label class="text-sm font-medium text-gray-700">類型:</label>
              <select 
                v-model="selectedSignalType" 
                class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="ALL">所有類型</option>
                <option value="BUY">買入信號</option>
                <option value="SELL">賣出信號</option>
                <option value="HOLD">持有信號</option>
              </select>
            </div>
            
            <!-- 結果篩選 -->
            <div class="flex items-center space-x-2">
              <label class="text-sm font-medium text-gray-700">結果:</label>
              <select 
                v-model="selectedResult" 
                class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="ALL">所有結果</option>
                <option value="PROFIT">盈利</option>
                <option value="LOSS">虧損</option>
                <option value="NEUTRAL">中性</option>
              </select>
            </div>
          </div>
          
          <div class="flex items-center space-x-3">
            <!-- 排序選項 -->
            <div class="flex items-center space-x-2">
              <label class="text-sm font-medium text-gray-700">排序:</label>
              <select 
                v-model="sortBy" 
                class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="date_desc">最新時間</option>
                <option value="date_asc">最舊時間</option>
                <option value="confidence_desc">信心度高→低</option>
                <option value="confidence_asc">信心度低→高</option>
                <option value="result_desc">盈利優先</option>
                <option value="result_asc">虧損優先</option>
              </select>
            </div>
            
            <!-- 匯出功能 -->
            <button
              @click="exportSignalHistory"
              class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-md transition-colors"
            >
              📊 匯出 CSV
            </button>
            
            <!-- 清除功能 -->
            <button
              @click="showClearConfirm = true"
              class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-md transition-colors"
            >
              🗑️ 清除歷史
            </button>
          </div>
        </div>
      </div>

      <!-- 信號歷史列表 -->
      <div class="bg-white shadow rounded-lg overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">
            歷史信號記錄 
            <span class="text-sm text-gray-500">({{ filteredHistory.length }} 筆記錄)</span>
          </h3>
        </div>
        
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  幣種 / 類型
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  進場資訊
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  風險管理
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  信心度
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  最終結果
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  時間 / 狀態
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  操作
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="signal in paginatedHistory" :key="`table-${signal.id}`" 
                  class="hover:bg-gray-50 transition-colors">
                <!-- 幣種 / 類型 -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div>
                      <div class="text-sm font-medium text-gray-900">{{ signal.symbol }}</div>
                      <span :class="{
                        'bg-green-100 text-green-800': signal.signal_type === 'BUY',
                        'bg-red-100 text-red-800': signal.signal_type === 'SELL',
                        'bg-gray-100 text-gray-800': signal.signal_type === 'HOLD'
                      }" class="inline-flex px-2 py-1 text-xs rounded-full">
                        {{ signal.signal_type }}
                      </span>
                    </div>
                  </div>
                </td>
                
                <!-- 進場資訊 -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">
                    <div>進場: ${{ signal.entry_price?.toFixed(4) || 'N/A' }}</div>
                    <div class="text-gray-500">
                      當前: ${{ signal.current_price?.toFixed(4) || 'N/A' }}
                    </div>
                  </div>
                </td>
                
                <!-- 風險管理 -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">
                    <div class="text-red-600">
                      止損: ${{ signal.stop_loss?.toFixed(4) || 'N/A' }}
                    </div>
                    <div class="text-green-600">
                      止盈: ${{ signal.take_profit?.toFixed(4) || 'N/A' }}
                    </div>
                  </div>
                </td>
                
                <!-- 信心度 -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                      <div 
                        :style="{ width: (signal.confidence * 100) + '%' }"
                        :class="{
                          'bg-green-500': signal.confidence >= 0.8,
                          'bg-yellow-500': signal.confidence >= 0.6,
                          'bg-red-500': signal.confidence < 0.6
                        }"
                        class="h-2 rounded-full"
                      ></div>
                    </div>
                    <span class="text-sm font-medium text-gray-700">
                      {{ Math.round(signal.confidence * 100) }}%
                    </span>
                  </div>
                </td>
                
                <!-- 最終結果 -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="text-sm font-medium" :class="{
                    'text-green-600': signal.final_result?.startsWith('+'),
                    'text-red-600': signal.final_result?.startsWith('-'),
                    'text-gray-600': !signal.final_result?.startsWith('+') && !signal.final_result?.startsWith('-')
                  }">
                    {{ signal.final_result || 'N/A' }}
                  </span>
                </td>
                
                <!-- 時間 / 狀態 -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">
                    <div>{{ signal.created_at ? formatDate(signal.created_at) : 'N/A' }}</div>
                    <span class="text-xs" :class="{
                      'text-green-600': signal.archive_reason === 'completed',
                      'text-yellow-600': signal.archive_reason === 'expired',
                      'text-red-600': signal.archive_reason === 'stopped',
                      'text-gray-600': signal.archive_reason === 'archived'
                    }">
                      {{ getArchiveReasonText(signal.archive_reason) }}
                    </span>
                  </div>
                </td>
                
                <!-- 操作 -->
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    @click="viewSignalDetail(signal)"
                    class="text-blue-600 hover:text-blue-900 mr-3"
                  >
                    查看詳情
                  </button>
                  <button
                    @click="deleteSignalRecord(signal.id)"
                    class="text-red-600 hover:text-red-900"
                  >
                    刪除
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- 分頁 -->
        <div class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200">
          <div class="flex-1 flex justify-between sm:hidden">
            <button
              @click="currentPage > 1 && currentPage--"
              :disabled="currentPage <= 1"
              class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              上一頁
            </button>
            <button
              @click="currentPage < totalPages && currentPage++"
              :disabled="currentPage >= totalPages"
              class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              下一頁
            </button>
          </div>
          <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p class="text-sm text-gray-700">
                顯示 
                <span class="font-medium">{{ (currentPage - 1) * pageSize + 1 }}</span>
                到 
                <span class="font-medium">{{ Math.min(currentPage * pageSize, filteredHistory.length) }}</span>
                筆，共 
                <span class="font-medium">{{ filteredHistory.length }}</span> 
                筆記錄
              </p>
            </div>
            <div>
              <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                <button
                  v-for="page in visiblePages"
                  :key="page"
                  @click="typeof page === 'number' && (currentPage = page)"
                  :class="[
                    page === currentPage 
                      ? 'z-10 bg-blue-50 border-blue-500 text-blue-600' 
                      : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50',
                    'relative inline-flex items-center px-4 py-2 border text-sm font-medium'
                  ]"
                  :disabled="typeof page === 'string'"
                >
                  {{ page }}
                </button>
              </nav>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 清除確認對話框 -->
    <div v-if="showClearConfirm" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3 text-center">
          <h3 class="text-lg font-medium text-gray-900">確認清除歷史記錄</h3>
          <div class="mt-2 px-7 py-3">
            <p class="text-sm text-gray-500">
              確定要清除{{ selectedCategory === 'ALL' ? '所有' : signalCategories[selectedCategory]?.name }}的歷史記錄嗎？
              此操作無法撤銷。
            </p>
          </div>
          <div class="items-center px-4 py-3">
            <button
              @click="confirmClearHistory"
              class="px-4 py-2 bg-red-500 text-white text-base font-medium rounded-md w-24 mr-2 hover:bg-red-600"
            >
              確認
            </button>
            <button
              @click="showClearConfirm = false"
              class="px-4 py-2 bg-gray-300 text-gray-800 text-base font-medium rounded-md w-24 hover:bg-gray-400"
            >
              取消
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import LoadingOverlay from '../components/LoadingOverlay.vue'

// 重用 Dashboard 中的 Signal 介面
interface Signal {
  id: number | string
  symbol: string
  signal_type: string
  entry_price?: number
  stop_loss?: number
  take_profit?: number
  risk_reward_ratio?: number
  confidence: number
  current_price?: number
  historical_win_rate?: string
  pattern_detected?: string
  confirmed_timeframes?: string[]
  timeframe_analysis?: string[]
  reasoning?: string
  technical_confluence?: string[]
  entry_strategy?: string
  risk_management?: string
  remaining_validity_hours?: number
  urgency_level?: string
  urgency_color?: string
  created_at?: string
  primary_timeframe?: string
  market_context?: string
  execution_notes?: string
  archived_at?: string
  archive_reason?: 'completed' | 'expired' | 'stopped' | 'archived'
  final_result?: string
}

// 狀態管理
const isLoading = ref(false)
const loadingMessage = ref('')
const selectedCategory = ref<string>('ALL')
const selectedSignalType = ref<string>('ALL')
const selectedResult = ref<string>('ALL')
const sortBy = ref<string>('date_desc')
const currentPage = ref(1)
const pageSize = ref(20)
const showClearConfirm = ref(false)

// 數據
const signalCategories = ref<Record<string, { name: string; signals: Signal[]; count: number }>>({
  'BTC/USDT': { name: 'Bitcoin', signals: [], count: 0 },
  'ETH/USDT': { name: 'Ethereum', signals: [], count: 0 },
  'BNB/USDT': { name: 'Binance Coin', signals: [], count: 0 },
  'ADA/USDT': { name: 'Cardano', signals: [], count: 0 },
  'SOL/USDT': { name: 'Solana', signals: [], count: 0 }
})

const savedSignalsHistory = ref<Signal[]>([])

// 計算屬性
const filteredHistory = computed(() => {
  let filtered = savedSignalsHistory.value

  // 按幣種篩選
  if (selectedCategory.value !== 'ALL') {
    filtered = filtered.filter(signal => signal.symbol === selectedCategory.value)
  }

  // 按信號類型篩選
  if (selectedSignalType.value !== 'ALL') {
    filtered = filtered.filter(signal => signal.signal_type === selectedSignalType.value)
  }

  // 按結果篩選
  if (selectedResult.value !== 'ALL') {
    filtered = filtered.filter(signal => {
      const result = signal.final_result || ''
      if (selectedResult.value === 'PROFIT') return result.startsWith('+')
      if (selectedResult.value === 'LOSS') return result.startsWith('-')
      if (selectedResult.value === 'NEUTRAL') return !result.startsWith('+') && !result.startsWith('-')
      return true
    })
  }

  // 排序
  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'date_desc':
        return new Date(b.archived_at || b.created_at || '').getTime() - new Date(a.archived_at || a.created_at || '').getTime()
      case 'date_asc':
        return new Date(a.archived_at || a.created_at || '').getTime() - new Date(b.archived_at || b.created_at || '').getTime()
      case 'confidence_desc':
        return b.confidence - a.confidence
      case 'confidence_asc':
        return a.confidence - b.confidence
      case 'result_desc':
        const aResult = parseFloat(a.final_result?.replace('%', '') || '0')
        const bResult = parseFloat(b.final_result?.replace('%', '') || '0')
        return bResult - aResult
      case 'result_asc':
        const aResult2 = parseFloat(a.final_result?.replace('%', '') || '0')
        const bResult2 = parseFloat(b.final_result?.replace('%', '') || '0')
        return aResult2 - bResult2
      default:
        return 0
    }
  })

  return filtered
})

const totalPages = computed(() => Math.ceil(filteredHistory.value.length / pageSize.value))

const paginatedHistory = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredHistory.value.slice(start, end)
})

const visiblePages = computed(() => {
  const total = totalPages.value
  const current = currentPage.value
  const delta = 2
  const range: (number | string)[] = []

  for (let i = Math.max(2, current - delta); i <= Math.min(total - 1, current + delta); i++) {
    range.push(i)
  }

  if (current - delta > 2) {
    range.unshift('...')
  }
  if (current + delta < total - 1) {
    range.push('...')
  }

  range.unshift(1)
  if (total > 1) {
    range.push(total)
  }

  return range.filter((item, index) => range.indexOf(item) === index)
})

// 方法
const loadSignalHistory = () => {
  try {
    const savedHistory = localStorage.getItem('tradingx_signal_history')
    const savedCategories = localStorage.getItem('tradingx_signal_categories')
    
    if (savedHistory) {
      savedSignalsHistory.value = JSON.parse(savedHistory)
    }
    
    if (savedCategories) {
      const loadedCategories = JSON.parse(savedCategories)
      Object.assign(signalCategories.value, loadedCategories)
    }
  } catch (error) {
    console.error('無法載入信號歷史:', error)
  }
}

const calculateWinRate = (symbol: string): number => {
  const signals = signalCategories.value[symbol]?.signals || []
  if (signals.length === 0) return 0
  
  const winCount = signals.filter(signal => {
    const result = signal.final_result || ''
    return result.startsWith('+')
  }).length
  
  return Math.round((winCount / signals.length) * 100)
}

const formatDate = (dateString: string): string => {
  try {
    return new Date(dateString).toLocaleString('zh-TW', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return 'N/A'
  }
}

const getArchiveReasonText = (reason?: string): string => {
  switch (reason) {
    case 'completed': return '✅ 完成'
    case 'expired': return '⏰ 過期'
    case 'stopped': return '🛑 止損'
    case 'archived': return '📁 歸檔'
    default: return '❓ 未知'
  }
}

const viewSignalDetail = (signal: Signal) => {
  // TODO: 實現信號詳情查看
  alert(`查看信號詳情: ${signal.symbol} - ${signal.signal_type}`)
}

const deleteSignalRecord = (signalId: number | string) => {
  if (confirm('確定要刪除這筆記錄嗎？')) {
    savedSignalsHistory.value = savedSignalsHistory.value.filter(s => s.id !== signalId)
    
    // 更新分類統計
    Object.keys(signalCategories.value).forEach(symbol => {
      signalCategories.value[symbol].signals = signalCategories.value[symbol].signals.filter(s => s.id !== signalId)
      signalCategories.value[symbol].count = signalCategories.value[symbol].signals.length
    })
    
    // 保存到 localStorage
    try {
      localStorage.setItem('tradingx_signal_history', JSON.stringify(savedSignalsHistory.value))
      localStorage.setItem('tradingx_signal_categories', JSON.stringify(signalCategories.value))
    } catch (error) {
      console.error('無法保存更新:', error)
    }
  }
}

const exportSignalHistory = () => {
  const data = filteredHistory.value
  const csvContent = [
    // CSV 標題行
    'Symbol,Type,Entry Price,Stop Loss,Take Profit,Confidence,Current Price,Final Result,Created At,Archived At,Archive Reason',
    // 數據行
    ...data.map(signal => [
      signal.symbol,
      signal.signal_type,
      signal.entry_price || '',
      signal.stop_loss || '',
      signal.take_profit || '',
      Math.round(signal.confidence * 100) + '%',
      signal.current_price || '',
      signal.final_result || '',
      signal.created_at || '',
      signal.archived_at || '',
      signal.archive_reason || ''
    ].join(','))
  ].join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `trading_signals_${new Date().toISOString().split('T')[0]}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const confirmClearHistory = () => {
  if (selectedCategory.value === 'ALL') {
    savedSignalsHistory.value = []
    Object.keys(signalCategories.value).forEach(key => {
      signalCategories.value[key].signals = []
      signalCategories.value[key].count = 0
    })
  } else {
    savedSignalsHistory.value = savedSignalsHistory.value.filter(signal => signal.symbol !== selectedCategory.value)
    if (signalCategories.value[selectedCategory.value]) {
      signalCategories.value[selectedCategory.value].signals = []
      signalCategories.value[selectedCategory.value].count = 0
    }
  }
  
  // 保存到 localStorage
  try {
    localStorage.setItem('tradingx_signal_history', JSON.stringify(savedSignalsHistory.value))
    localStorage.setItem('tradingx_signal_categories', JSON.stringify(signalCategories.value))
  } catch (error) {
    console.error('無法保存更新:', error)
  }
  
  showClearConfirm.value = false
}

onMounted(() => {
  loadSignalHistory()
})
</script>
