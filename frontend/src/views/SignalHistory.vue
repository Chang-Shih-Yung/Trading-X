<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <!-- Loading 覆蓋層 -->
    <LoadingOverlay :show="isLoading" :title="loadingMessage" message="請稍候..." />

    <div class="mx-auto max-w-7xl">
      <!-- 標題 -->
      <div class="mb-8 flex justify-between items-center">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">📊 交易信號歷史管理</h1>
          <p class="mt-2 text-gray-600">完整的信號歷史記錄、分析與統計</p>
        </div>
        <div class="flex items-center space-x-3">
          <button @click="fetchLatestSignals" :disabled="isLoading"
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white text-sm font-medium rounded-md transition-colors flex items-center space-x-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15">
              </path>
            </svg>
            <span>{{ isLoading ? '同步中...' : '同步最新信號' }}</span>
          </button>
          <div class="text-sm text-gray-500">
            總記錄: {{ savedSignalsHistory.length }} 筆
          </div>
        </div>
      </div>

      <!-- 統計概覽 -->
      <!-- 統計概覽 -->
      <div class="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-5">
        <div v-for="(category, symbol) in signalCategories" :key="symbol"
          class="bg-white shadow rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer"
          @click="selectCategory(symbol)" :class="selectedCategory === symbol ? 'ring-2 ring-blue-500 bg-blue-50' : ''">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-lg font-semibold text-gray-900">{{ category.name }}</h3>
              <p class="text-sm text-gray-500">{{ symbol }}</p>
            </div>
            <div class="text-right">
              <div class="text-2xl font-bold text-blue-600">{{ category.count }}</div>
              <div class="text-xs text-gray-500">歷史信號</div>
            </div>
          </div>

          <!-- 勝率統計 -->
          <div class="mt-4 pt-4 border-t border-gray-200">
            <div class="grid grid-cols-2 gap-2 text-xs">
              <div class="flex justify-between">
                <span class="text-gray-600">勝率</span>
                <span class="font-medium" :class="calculateWinRate(symbol) > 0 ? 'text-green-600' : 'text-red-600'">
                  {{ calculateWinRate(symbol) }}%
                </span>
              </div>
              <div class="flex justify-between">
                <span class="text-green-600">成功</span>
                <span class="font-medium text-green-600">{{ getSuccessCount(symbol) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-red-600">失敗</span>
                <span class="font-medium text-red-600">{{ getFailureCount(symbol) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">平均收益</span>
                <span class="font-medium" :class="getAverageReturn(symbol) >= 0 ? 'text-green-600' : 'text-red-600'">
                  {{ getAverageReturn(symbol).toFixed(2) }}%
                </span>
              </div>
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
              <select v-model="selectedCategory"
                class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                <option value="ALL">所有幣種</option>
                <option v-for="(category, symbol) in signalCategories" :key="symbol" :value="symbol">
                  {{ category.name }} ({{ category.count }})
                </option>
              </select>
            </div>

            <!-- 信號類型篩選 -->
            <div class="flex items-center space-x-2">
              <label class="text-sm font-medium text-gray-700">類型:</label>
              <select v-model="selectedSignalType"
                class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                <option value="ALL">所有類型</option>
                <option value="BUY">買入信號</option>
                <option value="SELL">賣出信號</option>
                <option value="HOLD">持有信號</option>
              </select>
            </div>

            <!-- 結果篩選 -->
            <div class="flex items-center space-x-2">
              <label class="text-sm font-medium text-gray-700">結果:</label>
              <select v-model="selectedResult"
                class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
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
              <select v-model="sortBy"
                class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                <option value="date_desc">最新時間</option>
                <option value="date_asc">最舊時間</option>
                <option value="confidence_desc">信心度高→低</option>
                <option value="confidence_asc">信心度低→高</option>
                <option value="result_desc">盈利優先</option>
                <option value="result_asc">虧損優先</option>
              </select>
            </div>

            <!-- 匯出功能 -->
            <button @click="exportSignalHistory"
              class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-md transition-colors">
              📊 匯出 CSV
            </button>

            <!-- 清除功能 -->
            <button @click="showClearConfirm = true"
              class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-md transition-colors">
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
                  成功/失敗
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
                      <div :style="{ width: (signal.confidence * 100) + '%' }" :class="{
                        'bg-green-500': signal.confidence >= 0.8,
                        'bg-yellow-500': signal.confidence >= 0.6,
                        'bg-red-500': signal.confidence < 0.6
                      }" class="h-2 rounded-full"></div>
                    </div>
                    <span class="text-sm font-medium text-gray-700">
                      {{ Math.round(signal.confidence * 100) }}%
                    </span>
                  </div>
                </td>

                <!-- 成功/失敗狀態 -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="{
                    'bg-green-100 text-green-800': isSignalSuccessful(signal),
                    'bg-red-100 text-red-800': !isSignalSuccessful(signal)
                  }" class="inline-flex px-2 py-1 text-xs rounded-full font-medium">
                    {{ isSignalSuccessful(signal) ? '✅ 成功' : '❌ 失敗' }}
                  </span>
                  <div class="text-xs text-gray-500 mt-1">
                    {{ getFailureReason(signal) }}
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
                  <button @click="viewSignalDetail(signal)" class="text-blue-600 hover:text-blue-900 mr-3">
                    查看詳情
                  </button>
                  <button @click="deleteSignalRecord(signal.id)" class="text-red-600 hover:text-red-900">
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
            <button @click="currentPage > 1 && currentPage--" :disabled="currentPage <= 1"
              class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50">
              上一頁
            </button>
            <button @click="currentPage < totalPages && currentPage++" :disabled="currentPage >= totalPages"
              class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50">
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
                <button v-for="page in visiblePages" :key="page"
                  @click="typeof page === 'number' && (currentPage = page)" :class="[
                    page === currentPage
                      ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                      : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50',
                    'relative inline-flex items-center px-4 py-2 border text-sm font-medium'
                  ]" :disabled="typeof page === 'string'">
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
            <button @click="confirmClearHistory"
              class="px-4 py-2 bg-red-500 text-white text-base font-medium rounded-md w-24 mr-2 hover:bg-red-600">
              確認
            </button>
            <button @click="showClearConfirm = false"
              class="px-4 py-2 bg-gray-300 text-gray-800 text-base font-medium rounded-md w-24 hover:bg-gray-400">
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
import axios from 'axios'
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

// 數據 - 支援兩種格式的幣種符號
const signalCategories = ref<Record<string, { name: string; signals: Signal[]; count: number }>>({
  'BTCUSDT': { name: 'Bitcoin', signals: [], count: 0 },
  'ETHUSDT': { name: 'Ethereum', signals: [], count: 0 },
  'BNBUSDT': { name: 'Binance Coin', signals: [], count: 0 },
  'ADAUSDT': { name: 'Cardano', signals: [], count: 0 },
  'XRPUSDT': { name: 'Ripple', signals: [], count: 0 }
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

    // 更新統計數據
    updateCategoryStats()
  } catch (error) {
    console.error('無法載入信號歷史:', error)
  }
}

// 更新分類統計
const updateCategoryStats = () => {
  // 首先重置所有統計
  Object.keys(signalCategories.value).forEach(symbol => {
    signalCategories.value[symbol].signals = []
    signalCategories.value[symbol].count = 0
  })

  // 重新計算統計
  savedSignalsHistory.value.forEach(signal => {
    if (signalCategories.value[signal.symbol]) {
      signalCategories.value[signal.symbol].signals.push(signal)
      signalCategories.value[signal.symbol].count++
    } else {
      // 嘗試標準化符號（BTCUSDT -> BTC/USDT）
      const normalizedSymbol = normalizeSymbol(signal.symbol)
      if (signalCategories.value[normalizedSymbol]) {
        // 更新信號的符號為標準格式
        signal.symbol = normalizedSymbol
        signalCategories.value[normalizedSymbol].signals.push(signal)
        signalCategories.value[normalizedSymbol].count++
      } else {
        console.warn(`未知的幣種符號: ${signal.symbol}`)
      }
    }
  })

  console.log('更新統計數據:', signalCategories.value)
  console.log('歷史記錄總數:', savedSignalsHistory.value.length)
}

// 符號標準化函數
const normalizeSymbol = (symbol: string): string => {
  // 將 BTCUSDT 格式轉換為 BTC/USDT
  if (symbol.endsWith('USDT') && !symbol.includes('/')) {
    const base = symbol.replace('USDT', '')
    return `${base}/USDT`
  }
  return symbol
}

// 改進的勝率計算邏輯
const calculateWinRate = (symbol: string): number => {
  const signals = savedSignalsHistory.value.filter(signal => signal.symbol === symbol)
  if (signals.length === 0) return 0

  const successCount = signals.filter(signal => isSignalSuccessful(signal)).length
  return Math.round((successCount / signals.length) * 100)
}

// 選擇分類
const selectCategory = (symbol: string) => {
  console.log('選擇分類:', symbol)
  selectedCategory.value = symbol
  currentPage.value = 1 // 重置到第一頁
  console.log('當前選擇的分類:', selectedCategory.value)
  console.log('篩選後的歷史記錄:', filteredHistory.value.length)
}

// 獲取最新交易信號（從 API 同步）
const fetchLatestSignals = async () => {
  try {
    isLoading.value = true
    loadingMessage.value = '同步最新信號數據...'

    // 1. 首先處理現有信號的銷毀邏輯
    processSignalDestruction()

    // 2. 從 API 獲取最新信號
    const response = await axios.get('/api/v1/signals/latest?hours=168', { timeout: 10000 }) // 獲取一週內的信號
    const latestSignals = response.data || []

    // 3. 合併新信號到歷史記錄（避免重複）
    const existingIds = new Set(savedSignalsHistory.value.map(s => s.id))
    const newSignals = latestSignals.filter((signal: Signal) => !existingIds.has(signal.id))

    if (newSignals.length > 0) {
      // 將新信號標記為已歸檔
      const archivedNewSignals = newSignals.map((signal: Signal) => ({
        ...signal,
        archived_at: new Date().toISOString(),
        archive_reason: 'archived' as const,
        final_result: calculateSignalFinalResult(signal)
      }))

      savedSignalsHistory.value.unshift(...archivedNewSignals)

      // 保存到 localStorage
      localStorage.setItem('tradingx_signal_history', JSON.stringify(savedSignalsHistory.value))

      // 更新統計
      updateCategoryStats()

      console.log(`同步了 ${newSignals.length} 個新信號`)
    } else {
      console.log('沒有新信號需要同步')
    }

    // 4. 再次處理銷毀邏輯（針對新同步的信號）
    processSignalDestruction()

  } catch (error) {
    console.error('獲取最新信號失敗:', error)
  } finally {
    isLoading.value = false
    loadingMessage.value = ''
  }
}

// 計算信號最終結果
const calculateSignalFinalResult = (signal: Signal): string => {
  if (!signal.current_price || !signal.entry_price) return '無法計算'

  const priceChange = signal.current_price - signal.entry_price
  const percentageChange = (priceChange / signal.entry_price) * 100

  if (signal.signal_type === 'BUY') {
    return percentageChange > 0 ? `+${percentageChange.toFixed(2)}%` : `${percentageChange.toFixed(2)}%`
  } else if (signal.signal_type === 'SELL') {
    return percentageChange < 0 ? `+${Math.abs(percentageChange).toFixed(2)}%` : `-${percentageChange.toFixed(2)}%`
  }

  return '0.00%'
}

// 判斷信號是否成功 - 增強版銷毀邏輯
const isSignalSuccessful = (signal: Signal): boolean => {
  // 1. 如果信號是因為完成而歸檔，視為成功
  if (signal.archive_reason === 'completed') {
    return true
  }

  // 2. 如果信號是因為以下原因被銷毀，視為失敗
  if (signal.archive_reason === 'expired' ||
    signal.archive_reason === 'stopped') {
    return false
  }

  // 3. 基於最終結果和時效性判斷
  if (signal.final_result) {
    const resultValue = parseFloat(signal.final_result.replace('%', ''))

    // 負收益視為失敗
    if (resultValue < 0) {
      return false
    }

    // 檢查時效性：如果時效結束，只有收益>0才算成功
    if (isSignalExpired(signal)) {
      return resultValue > 0
    }

    // 利潤低於10%視為失敗（僅適用於未過期信號）
    if (resultValue > 0 && resultValue < 10) {
      return false
    }

    // 正收益且大於等於10%視為成功
    return resultValue >= 10
  }

  // 4. 檢查是否因為價格超出區間而銷毀
  if (isPriceOutOfRange(signal)) {
    return false
  }

  // 默認視為失敗（未確定的情況）
  return false
}

// 檢查信號是否已過期
const isSignalExpired = (signal: Signal): boolean => {
  if (!signal.created_at) return false

  const createdTime = new Date(signal.created_at)
  const now = new Date()
  const hoursElapsed = (now.getTime() - createdTime.getTime()) / (1000 * 60 * 60)

  return hoursElapsed > 24 // 24小時後視為過期
}

// 檢查價格是否超出區間
const isPriceOutOfRange = (signal: Signal): boolean => {
  if (!signal.current_price || !signal.entry_price) return false

  const priceDeviation = Math.abs(signal.current_price - signal.entry_price) / signal.entry_price

  // 如果價格偏離超過15%，視為超出區間
  if (priceDeviation > 0.15) {
    // 進一步檢查是否是不利方向的偏離
    if ((signal.signal_type === 'BUY' && signal.current_price < signal.entry_price * 0.85) ||
      (signal.signal_type === 'SELL' && signal.current_price > signal.entry_price * 1.15)) {
      return true
    }
  }

  return false
}

// 信號銷毀判定和處理
const shouldDestroySignal = (signal: Signal): { shouldDestroy: boolean; reason: string; isSuccess: boolean } => {
  const now = new Date()

  // 1. 檢查時效性 - 超過24小時自動銷毀
  if (signal.created_at) {
    const createdTime = new Date(signal.created_at)
    const hoursElapsed = (now.getTime() - createdTime.getTime()) / (1000 * 60 * 60)

    if (hoursElapsed > 24) {
      // 時效到期，根據收益判定成功失敗
      const currentProfit = calculateCurrentProfit(signal)
      return {
        shouldDestroy: true,
        reason: '時效到期',
        isSuccess: currentProfit > 0
      }
    }
  }

  // 2. 檢查價格是否超出點位區間
  if (isPriceOutOfRange(signal)) {
    return {
      shouldDestroy: true,
      reason: '價格超出區間',
      isSuccess: false
    }
  }

  // 3. 檢查止損觸發
  if (signal.stop_loss && signal.current_price) {
    if ((signal.signal_type === 'BUY' && signal.current_price <= signal.stop_loss) ||
      (signal.signal_type === 'SELL' && signal.current_price >= signal.stop_loss)) {
      return {
        shouldDestroy: true,
        reason: '止損觸發',
        isSuccess: false
      }
    }
  }

  // 4. 檢查止盈觸發
  if (signal.take_profit && signal.current_price) {
    if ((signal.signal_type === 'BUY' && signal.current_price >= signal.take_profit) ||
      (signal.signal_type === 'SELL' && signal.current_price <= signal.take_profit)) {
      return {
        shouldDestroy: true,
        reason: '止盈觸發',
        isSuccess: true
      }
    }
  }

  // 5. 檢查信心度 - 低於20%的信號銷毀
  if (signal.confidence < 0.2) {
    return {
      shouldDestroy: true,
      reason: '信心度過低',
      isSuccess: false
    }
  }

  return { shouldDestroy: false, reason: '', isSuccess: false }
}

// 計算當前收益
const calculateCurrentProfit = (signal: Signal): number => {
  if (!signal.current_price || !signal.entry_price) return 0

  const priceChange = signal.current_price - signal.entry_price
  const percentageChange = (priceChange / signal.entry_price) * 100

  if (signal.signal_type === 'BUY') {
    return percentageChange
  } else if (signal.signal_type === 'SELL') {
    return -percentageChange
  }

  return 0
}

// 獲取成功信號數量
const getSuccessCount = (symbol: string): number => {
  const signals = savedSignalsHistory.value.filter(signal => signal.symbol === symbol)
  return signals.filter(signal => isSignalSuccessful(signal)).length
}

// 獲取失敗信號數量
const getFailureCount = (symbol: string): number => {
  const signals = savedSignalsHistory.value.filter(signal => signal.symbol === symbol)
  return signals.filter(signal => !isSignalSuccessful(signal)).length
}

// 獲取平均收益率
const getAverageReturn = (symbol: string): number => {
  const signals = savedSignalsHistory.value.filter(signal => signal.symbol === symbol && signal.final_result)
  if (signals.length === 0) return 0

  const totalReturn = signals.reduce((sum, signal) => {
    const result = parseFloat(signal.final_result?.replace('%', '') || '0')
    return sum + result
  }, 0)

  return totalReturn / signals.length
}// 獲取失敗原因 - 增強版
const getFailureReason = (signal: Signal): string => {
  if (isSignalSuccessful(signal)) {
    return '達成目標'
  }

  // 檢查銷毀原因
  const destroyCheck = shouldDestroySignal(signal)
  if (destroyCheck.shouldDestroy) {
    return destroyCheck.reason
  }

  // 檢查歸檔原因
  if (signal.archive_reason === 'expired') {
    return '時效過期'
  }
  if (signal.archive_reason === 'stopped') {
    return '止損觸發'
  }

  // 檢查收益率
  if (signal.final_result) {
    const resultValue = parseFloat(signal.final_result.replace('%', ''))
    if (Math.abs(resultValue) < 10) {
      return '收益低於10%'
    }
    if (resultValue < 0) {
      return '虧損'
    }
  }

  // 檢查價格偏離
  if (isPriceOutOfRange(signal)) {
    return '價格超出區間'
  }

  // 檢查時效性
  if (isSignalExpired(signal)) {
    return '時效過期'
  }

  return '待確認'
}

// 處理信號銷毀（在同步時調用）
const processSignalDestruction = () => {
  let destroyedCount = 0
  const updatedSignals: Signal[] = []

  savedSignalsHistory.value.forEach(signal => {
    const destroyCheck = shouldDestroySignal(signal)

    if (destroyCheck.shouldDestroy && !signal.archived_at) {
      // 銷毀信號並標記結果
      const destroyedSignal = {
        ...signal,
        archived_at: new Date().toISOString(),
        archive_reason: destroyCheck.reason === '時效過期' ? 'expired' as const :
          destroyCheck.reason === '止損觸發' ? 'stopped' as const :
            destroyCheck.reason === '止盈觸發' ? 'completed' as const :
              'archived' as const,
        final_result: calculateSignalFinalResult(signal)
      }

      updatedSignals.push(destroyedSignal)
      destroyedCount++

      console.log(`信號 ${signal.symbol} 已銷毀: ${destroyCheck.reason}, 結果: ${destroyCheck.isSuccess ? '成功' : '失敗'}`)
    } else {
      updatedSignals.push(signal)
    }
  })

  if (destroyedCount > 0) {
    savedSignalsHistory.value = updatedSignals
    localStorage.setItem('tradingx_signal_history', JSON.stringify(savedSignalsHistory.value))
    updateCategoryStats()
    console.log(`已銷毀 ${destroyedCount} 個信號`)
  }
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

onMounted(async () => {
  // 載入現有的歷史數據
  loadSignalHistory()

  // 同步最新信號（這將從 API 獲取數據）
  await fetchLatestSignals()

  // 設置定時器，每5分鐘檢查一次信號銷毀條件
  setInterval(() => {
    processSignalDestruction()
  }, 300000) // 5分鐘 = 300000毫秒
})
</script>
