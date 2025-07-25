<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <!-- Loading 覆蓋層 -->
    <LoadingOverlay :show="isLoading" :title="loadingMessage" message="請稍候..." />

    <div class="mx-auto max-w-7xl">
      <!-- 標題 -->
      <div class="mb-8 flex justify-between items-center">
        <div>
          <h1 class="text-3xl font-bold text-orange-900">⚡ 短線信號歷史管理</h1>
          <p class="mt-2 text-gray-600">短線交易信號的完整歷史記錄、勝率分析與統計</p>
        </div>
        <div class="flex items-center space-x-3">
          <button @click="goBack"
            class="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white text-sm font-medium rounded-md transition-colors flex items-center space-x-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
            </svg>
            <span>返回儀表板</span>
          </button>
          <div class="text-sm text-gray-500">
            總記錄: {{ savedShortTermHistory.length }} 筆
          </div>
        </div>
      </div>

      <!-- 統計概覽 -->
      <div class="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-5">
        <!-- 總體統計 -->
        <div class="bg-white shadow rounded-lg p-6 border-l-4 border-orange-500">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-lg font-semibold text-gray-900">總體統計</h3>
              <p class="text-sm text-gray-500">ALL</p>
            </div>
            <div class="text-right">
              <div class="text-2xl font-bold text-orange-600">{{ savedShortTermHistory.length }}</div>
              <div class="text-xs text-gray-500">歷史信號</div>
            </div>
          </div>
          <div class="mt-4 pt-4 border-t border-gray-200">
            <div class="grid grid-cols-2 gap-2 text-xs">
              <div class="flex justify-between">
                <span class="text-gray-600">勝率</span>
                <span class="font-medium" :class="getOverallWinRate() > 0 ? 'text-green-600' : 'text-red-600'">
                  {{ getOverallWinRate() }}%
                </span>
              </div>
              <div class="flex justify-between">
                <span class="text-green-600">成功</span>
                <span class="font-medium text-green-600">{{ getOverallSuccessCount() }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-red-600">失敗</span>
                <span class="font-medium text-red-600">{{ getOverallFailureCount() }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">攤平</span>
                <span class="font-medium text-gray-600">{{ getOverallBreakevenCount() }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-orange-600">🚀 突破</span>
                <span class="font-medium text-orange-600">{{ getOverallBreakoutCount() }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-purple-600">突破勝率</span>
                <span class="font-medium text-purple-600">{{ getBreakoutWinRate() }}%</span>
              </div>
              <div class="flex justify-between col-span-2 pt-1 border-t border-gray-100">
                <span class="text-blue-600 font-medium">💰 本週盈利</span>
                <span class="font-bold" :class="getWeeklyProfitStats().currentWeek >= 0 ? 'text-green-600' : 'text-red-600'">
                  {{ getWeeklyProfitStats().currentWeek >= 0 ? '+' : '' }}{{ getWeeklyProfitStats().currentWeek.toFixed(2) }}%
                </span>
              </div>
              <div class="flex justify-between col-span-2">
                <span class="text-gray-600 font-medium">📈 上週盈利</span>
                <span class="font-bold" :class="getWeeklyProfitStats().lastWeek >= 0 ? 'text-green-600' : 'text-red-600'">
                  {{ getWeeklyProfitStats().lastWeek >= 0 ? '+' : '' }}{{ getWeeklyProfitStats().lastWeek.toFixed(2) }}%
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 各幣種分類統計 -->
        <div v-for="(category, symbol) in shortTermCategories" :key="symbol"
          class="bg-white shadow rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer"
          @click="selectCategory(symbol)" :class="selectedCategory === symbol ? 'ring-2 ring-orange-500 bg-orange-50' : ''">
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
                <span class="text-gray-600">攤平</span>
                <span class="font-medium text-gray-600">{{ getBreakevenCount(symbol) }}</span>
              </div>
              <div class="flex justify-between col-span-2 pt-1 border-t border-gray-100">
                <span class="text-blue-600 font-medium">💰 本週</span>
                <span class="font-bold text-xs" :class="getSymbolWeeklyProfitStats(symbol).currentWeek >= 0 ? 'text-green-600' : 'text-red-600'">
                  {{ getSymbolWeeklyProfitStats(symbol).currentWeek >= 0 ? '+' : '' }}{{ getSymbolWeeklyProfitStats(symbol).currentWeek.toFixed(2) }}%
                </span>
              </div>
              <div class="flex justify-between col-span-2">
                <span class="text-gray-600 font-medium">📈 上週</span>
                <span class="font-bold text-xs" :class="getSymbolWeeklyProfitStats(symbol).lastWeek >= 0 ? 'text-green-600' : 'text-red-600'">
                  {{ getSymbolWeeklyProfitStats(symbol).lastWeek >= 0 ? '+' : '' }}{{ getSymbolWeeklyProfitStats(symbol).lastWeek.toFixed(2) }}%
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
                class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500">
                <option value="ALL">所有幣種</option>
                <option v-for="(category, symbol) in shortTermCategories" :key="symbol" :value="symbol">
                  {{ category.name }} ({{ category.count }})
                </option>
              </select>
            </div>

            <!-- 交易方向篩選 -->
            <div class="flex items-center space-x-2">
              <label class="text-sm font-medium text-gray-700">方向:</label>
              <select v-model="selectedDirection"
                class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500">
                <option value="ALL">所有方向</option>
                <option value="LONG">做多</option>
                <option value="SHORT">做空</option>
              </select>
            </div>

            <!-- 結果篩選 -->
            <div class="flex items-center space-x-2">
              <label class="text-sm font-medium text-gray-700">結果:</label>
              <select v-model="selectedResult"
                class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500">
                <option value="ALL">所有結果</option>
                <option value="success">成功</option>
                <option value="failure">失敗</option>
                <option value="breakeven">攤平</option>
              </select>
            </div>

            <!-- 🚀 突破信號篩選 -->
            <div class="flex items-center space-x-2">
              <label class="text-sm font-medium text-gray-700">類型:</label>
              <select v-model="selectedBreakout"
                class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500">
                <option value="ALL">所有信號</option>
                <option value="BREAKOUT">🚀 突破信號</option>
                <option value="NORMAL">常規信號</option>
              </select>
            </div>
          </div>

          <div class="flex items-center space-x-3">
            <!-- 排序選項 -->
            <div class="flex items-center space-x-2">
              <label class="text-sm font-medium text-gray-700">排序:</label>
              <select v-model="sortBy"
                class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500">
                <option value="date_desc">最新時間</option>
                <option value="date_asc">最舊時間</option>
                <option value="profit_desc">利潤高→低</option>
                <option value="profit_asc">利潤低→高</option>
                <option value="confidence_desc">信心度高→低</option>
                <option value="confidence_asc">信心度低→高</option>
              </select>
            </div>

            <!-- 匯出功能 -->
            <button @click="exportHistory"
              class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-md transition-colors">
              📊 匯出 CSV
            </button>

            <!-- 🔄 重新計算按鈕 -->
                        <button @click="recalculateResults" :disabled="isLoading"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md transition-colors flex items-center space-x-2"
              title="根據新的攤平邏輯(0% < 利潤 < 0.5%)重新計算歷史記錄">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              <span>重算結果</span>
            </button>
            <button @click="fixProfitDirections" :disabled="isLoading"
              class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-md transition-colors flex items-center space-x-2"
              title="修正做空信號的利潤方向性(將正利潤改為負利潤)">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <span>修正利潤方向</span>
            </button>

            <!-- 清除功能 -->
            <button @click="showClearConfirm = true"
              class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-md transition-colors">
              🗑️ 清除歷史
            </button>
          </div>
        </div>
      </div>

      <!-- 短線信號歷史列表 -->
      <div class="bg-white shadow rounded-lg overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">
            短線信號歷史記錄
            <span class="text-sm text-gray-500">({{ filteredHistory.length }} 筆記錄)</span>
          </h3>
        </div>

        <div class="overflow-x-auto max-h-96 overflow-y-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50 sticky top-0 z-10">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">幣種/時間</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">方向/結果</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">價格信息</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">利潤</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">信心度</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">策略類型</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">歸檔原因</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="signal in paginatedHistory" :key="`history-${signal.id}`" 
                class="hover:bg-gray-50 transition-colors">
                <!-- 幣種/時間 -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex flex-col">
                    <div class="text-sm font-medium text-gray-900">{{ signal.symbol }}</div>
                    <div class="text-xs text-gray-500">{{ formatTime(signal.archived_at || '') }}</div>
                  </div>
                </td>

                <!-- 方向/結果 -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex flex-col space-y-1">
                    <div class="flex items-center space-x-1">
                      <span class="text-sm text-gray-700">
                        {{ getSignalDirection(signal.signal_type) === 'LONG' ? '做多' : '做空' }}
                      </span>
                      <!-- 🚀 突破信號歷史標記 -->
                      <span v-if="isHistoricalBreakoutSignal(signal)"
                        class="px-1.5 py-0.5 text-xs font-bold bg-gradient-to-r from-yellow-400 to-orange-500 text-white rounded-full">
                        🚀
                      </span>
                    </div>
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="getResultBadgeClass(signal.trade_result)">
                      {{ getResultText(signal.trade_result) }}
                    </span>
                  </div>
                </td>

                <!-- 價格信息 -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex flex-col text-xs">
                    <div class="text-gray-600">開倉: ${{ signal.entry_price?.toFixed(4) || 'N/A' }}</div>
                    <div class="text-gray-600">結算: ${{ signal.current_price?.toFixed(4) || 'N/A' }}</div>
                  </div>
                </td>

                <!-- 利潤 -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium"
                    :class="getProfitClass(signal.profit_percent)">
                    {{ getProfitDisplay(signal.trade_result, signal.profit_percent) }}
                  </div>
                </td>

                <!-- 信心度 -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="w-16 bg-gray-200 rounded-full h-2">
                      <div class="h-2 rounded-full" 
                        :class="getConfidenceBarClass(signal.confidence)"
                        :style="{ width: `${signal.confidence * 100}%` }"></div>
                    </div>
                    <span class="ml-2 text-sm text-gray-600">{{ Math.round(signal.confidence * 100) }}%</span>
                  </div>
                </td>

                <!-- 策略 -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-700">
                    {{ signal.strategy_name || (signal.is_scalping ? '短線專用' : '中長線篩選') }}
                  </div>
                </td>

                <!-- 歸檔原因 -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="getArchiveReasonClass(signal.archive_reason)">
                    {{ getArchiveReasonText(signal.archive_reason) }}
                  </span>
                </td>
              </tr>

              <tr v-if="filteredHistory.length === 0">
                <td colspan="7" class="px-6 py-12 text-center text-gray-500">
                  <div class="flex flex-col items-center">
                    <svg class="w-12 h-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z">
                      </path>
                    </svg>
                    <p class="text-lg font-medium">暫無歷史記錄</p>
                    <p class="text-sm">短線信號到期後會自動出現在這裡</p>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 分頁 -->
        <div v-if="filteredHistory.length > itemsPerPage" class="px-6 py-4 border-t border-gray-200">
          <div class="flex items-center justify-between">
            <div class="text-sm text-gray-700">
              顯示 {{ (currentPage - 1) * itemsPerPage + 1 }} 到 {{ Math.min(currentPage * itemsPerPage, filteredHistory.length) }} 
              筆，共 {{ filteredHistory.length }} 筆記錄
            </div>
            <div class="flex items-center space-x-2">
              <button @click="currentPage = Math.max(1, currentPage - 1)" :disabled="currentPage === 1"
                class="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50">
                上一頁
              </button>
              <span class="px-3 py-1 text-sm">第 {{ currentPage }} 頁，共 {{ totalPages }} 頁</span>
              <button @click="currentPage = Math.min(totalPages, currentPage + 1)" :disabled="currentPage === totalPages"
                class="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50">
                下一頁
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 清除確認彈窗 -->
    <ConfirmDialog
      v-model:show="showClearConfirm"
      title="確認清除歷史記錄"
      message="您確定要清除選定的短線信號歷史記錄嗎？"
      :details="clearConfirmDetails"
      confirm-text="確認清除"
      cancel-text="取消"
      type="danger"
      @confirm="confirmClearHistory"
      @cancel="showClearConfirm = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import LoadingOverlay from '@/components/LoadingOverlay.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const router = useRouter()

// 介面定義
interface Signal {
  id: number | string
  symbol: string
  signal_type: string
  entry_price?: number
  current_price?: number
  confidence: number
  archived_at?: string
  archive_reason?: 'completed' | 'expired' | 'stopped' | 'archived'
  trade_result?: 'success' | 'failure' | 'breakeven'
  profit_percent?: number
  strategy_name?: string
  is_scalping?: boolean
}

// 數據狀態
const savedShortTermHistory = ref<Signal[]>([])
const shortTermCategories = ref<Record<string, { name: string; signals: Signal[]; count: number }>>({})
const isLoading = ref(false)
const loadingMessage = ref('')

// 篩選和排序
const selectedCategory = ref('ALL')
const selectedDirection = ref('ALL')
const selectedResult = ref('ALL')
const selectedBreakout = ref('ALL')  // 🚀 突破信號篩選
const sortBy = ref('date_desc')

// 分頁
const currentPage = ref(1)
const itemsPerPage = 20

// 清除確認
const showClearConfirm = ref(false)

// 載入短線歷史記錄
const loadShortTermHistory = () => {
  try {
    const savedHistory = localStorage.getItem('tradingx_shortterm_history')
    const savedCategories = localStorage.getItem('tradingx_shortterm_categories')

    if (savedHistory) {
      savedShortTermHistory.value = JSON.parse(savedHistory)
      // 🔄 重新計算交易結果（應用新的攤平邏輯）
      recalculateTradeResults()
    }

    if (savedCategories) {
      const loadedCategories = JSON.parse(savedCategories)
      Object.assign(shortTermCategories.value, loadedCategories)
    }
  } catch (error) {
    console.error('無法載入短線信號歷史:', error)
  }
}

// 🔄 重新計算交易結果（根據新的攤平邏輯）
const recalculateTradeResults = () => {
  let updated = false
  
  savedShortTermHistory.value.forEach(signal => {
    if (signal.entry_price && signal.current_price && signal.profit_percent !== undefined) {
      const newResult = calculateUpdatedTradeResult(signal)
      if (newResult !== signal.trade_result) {
        signal.trade_result = newResult
        updated = true
        console.log(`🔄 更新交易結果: ${signal.symbol} ${signal.profit_percent.toFixed(2)}% -> ${newResult}`)
      }
    }
  })
  
  if (updated) {
    // 保存更新後的數據
    localStorage.setItem('tradingx_shortterm_history', JSON.stringify(savedShortTermHistory.value))
    console.log('✅ 交易結果重新計算完成')
  }
}

// 📊 根據新邏輯計算交易結果
const calculateUpdatedTradeResult = (signal: Signal): 'success' | 'failure' | 'breakeven' => {
  const profitPercent = signal.profit_percent || 0
  const direction = getSignalDirection(signal.signal_type)
  
  // 攤平閾值：0% < 利潤 < 0.5% 才算攤平
  const breakevenThreshold = 0.5
  const stopLossThreshold = 1.0
  
  // 簡化的動態止盈計算（基於時間框架和信心度）
  let successThreshold = 2.0 // 基礎閾值
  
  // 根據信心度調整
  if (signal.confidence > 0.8) successThreshold *= 1.2
  else if (signal.confidence < 0.6) successThreshold *= 0.8
  
  // 🐛 詳細調試信息
  console.log(`🔍 計算交易結果 ${signal.symbol}:`, {
    signal_type: signal.signal_type,  // 📊 查看原始信號類型
    profitPercent: profitPercent.toFixed(3),
    direction,
    successThreshold: successThreshold.toFixed(3),
    confidence: signal.confidence,
    breakevenThreshold,
    stopLossThreshold
  })
  
  // 判斷邏輯
  if (direction === 'LONG') {
    if (profitPercent >= successThreshold) {
      console.log(`✅ 做多大成功: ${profitPercent.toFixed(3)}% >= ${successThreshold.toFixed(3)}%`)
      return 'success'
    } else if (profitPercent <= -stopLossThreshold) {
      console.log(`❌ 做多失敗: ${profitPercent.toFixed(3)}% <= -${stopLossThreshold}%`)
      return 'failure'
    } else if (profitPercent > 0 && profitPercent < breakevenThreshold) {
      console.log(`⚖️ 做多攤平: 0% < ${profitPercent.toFixed(3)}% < ${breakevenThreshold}%`)
      return 'breakeven'
    } else {
      console.log(`✅ 做多中等成功: ${profitPercent.toFixed(3)}% (>= ${breakevenThreshold}% 且 < ${successThreshold.toFixed(3)}%)`)
      return 'success'
    }
  } else if (direction === 'SHORT') {
    // 🔧 修正做空邏輯：處理負利潤
    const actualShortProfit = Math.abs(profitPercent) // 做空利潤的絕對值
    
    if (profitPercent < 0 && actualShortProfit >= successThreshold) {
      console.log(`✅ 做空大成功: ${profitPercent.toFixed(3)}% (實際利潤 ${actualShortProfit.toFixed(3)}% >= ${successThreshold.toFixed(3)}%)`)
      return 'success'
    } else if (profitPercent > 0 && profitPercent >= stopLossThreshold) {
      console.log(`❌ 做空失敗: ${profitPercent.toFixed(3)}% >= ${stopLossThreshold}%`)
      return 'failure'
    } else if (profitPercent < 0 && actualShortProfit > 0 && actualShortProfit < breakevenThreshold) {
      console.log(`⚖️ 做空攤平: 0% < ${actualShortProfit.toFixed(3)}% < ${breakevenThreshold}%`)
      return 'breakeven'
    } else if (profitPercent < 0 && actualShortProfit >= breakevenThreshold && actualShortProfit < successThreshold) {
      console.log(`✅ 做空中等成功: ${profitPercent.toFixed(3)}% (實際利潤 ${actualShortProfit.toFixed(3)}% >= ${breakevenThreshold}% 且 < ${successThreshold.toFixed(3)}%)`)
      return 'success'
    } else if (profitPercent > 0 && profitPercent < stopLossThreshold) {
      console.log(`⚖️ 做空小虧損視為攤平: ${profitPercent.toFixed(3)}% < ${stopLossThreshold}%`)
      return 'breakeven'
    } else {
      console.log(`✅ 做空預設成功: ${profitPercent.toFixed(3)}%`)
      return 'success'
    }
  }
  
  console.log(`⚖️ 未知方向，默認攤平: ${direction}`)
  return 'breakeven'
}

// 獲取信號方向
const getSignalDirection = (signalType: string): 'LONG' | 'SHORT' | 'UNKNOWN' => {
  if (!signalType) return 'UNKNOWN'
  
  const normalizedType = signalType.toString().toUpperCase()
  
  // 📊 增強的信號類型識別
  const longTypes = [
    'BUY', 'LONG', 'BULL', 'CALL', '買入', '做多', '看多',
    'buy', 'long', 'bull', 'call',
    // 技術指標相關
    'GOLDEN_CROSS', 'BULLISH', 'UPTREND', 'BREAKOUT_UP',
    // 可能的數值類型
    '1', 1, true
  ]
  
  const shortTypes = [
    'SELL', 'SHORT', 'BEAR', 'PUT', '賣出', '做空', '看空',
    'sell', 'short', 'bear', 'put',
    // 技術指標相關
    'DEATH_CROSS', 'BEARISH', 'DOWNTREND', 'BREAKOUT_DOWN',
    // 可能的數值類型
    '0', 0, false, '-1', -1
  ]
  
  // 🔍 調試信號類型識別
  console.log(`🔍 信號類型識別: "${signalType}" -> "${normalizedType}"`)
  
  if (longTypes.some(type => normalizedType.includes(type.toString().toUpperCase()))) {
    console.log(`✅ 識別為做多信號`)
    return 'LONG'
  }
  
  if (shortTypes.some(type => normalizedType.includes(type.toString().toUpperCase()))) {
    console.log(`✅ 識別為做空信號`)
    return 'SHORT'
  }
  
  // 模糊匹配：包含關鍵字
  if (normalizedType.includes('UP') || normalizedType.includes('HIGH') || normalizedType.includes('RISE')) {
    console.log(`✅ 模糊匹配做多信號 (UP/HIGH/RISE)`)
    return 'LONG'
  }
  
  if (normalizedType.includes('DOWN') || normalizedType.includes('LOW') || normalizedType.includes('FALL')) {
    console.log(`✅ 模糊匹配做空信號 (DOWN/LOW/FALL)`)
    return 'SHORT'
  }
  
  console.log(`❌ 無法識別信號方向: "${signalType}"`)
  return 'UNKNOWN'
}

// 格式化時間
const formatTime = (timestamp: string): string => {
  try {
    if (!timestamp) return '無效'
    const date = new Date(timestamp)
    if (isNaN(date.getTime())) return '無效'
    
    return date.toLocaleString('zh-TW', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return '錯誤'
  }
}

// 計算篩選後的歷史記錄
const filteredHistory = computed(() => {
  let filtered = savedShortTermHistory.value

  // 幣種篩選
  if (selectedCategory.value !== 'ALL') {
    filtered = filtered.filter(signal => signal.symbol === selectedCategory.value)
  }

  // 方向篩選
  if (selectedDirection.value !== 'ALL') {
    filtered = filtered.filter(signal => getSignalDirection(signal.signal_type) === selectedDirection.value)
  }

  // 結果篩選
  if (selectedResult.value !== 'ALL') {
    filtered = filtered.filter(signal => signal.trade_result === selectedResult.value)
  }

  // 🚀 突破信號篩選
  if (selectedBreakout.value !== 'ALL') {
    if (selectedBreakout.value === 'BREAKOUT') {
      filtered = filtered.filter(signal => isHistoricalBreakoutSignal(signal))
    } else if (selectedBreakout.value === 'NORMAL') {
      filtered = filtered.filter(signal => !isHistoricalBreakoutSignal(signal))
    }
  }

  // 排序
  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'date_desc':
        return new Date(b.archived_at || 0).getTime() - new Date(a.archived_at || 0).getTime()
      case 'date_asc':
        return new Date(a.archived_at || 0).getTime() - new Date(b.archived_at || 0).getTime()
      case 'profit_desc':
        return (b.profit_percent || 0) - (a.profit_percent || 0)
      case 'profit_asc':
        return (a.profit_percent || 0) - (b.profit_percent || 0)
      case 'confidence_desc':
        return b.confidence - a.confidence
      case 'confidence_asc':
        return a.confidence - b.confidence
      default:
        return 0
    }
  })

  return filtered
})

// 分頁計算
const totalPages = computed(() => Math.ceil(filteredHistory.value.length / itemsPerPage))
const paginatedHistory = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredHistory.value.slice(start, end)
})

// 統計計算函數
const getOverallSuccessCount = () => savedShortTermHistory.value.filter(s => s.trade_result === 'success').length
const getOverallFailureCount = () => savedShortTermHistory.value.filter(s => s.trade_result === 'failure').length
const getOverallBreakevenCount = () => savedShortTermHistory.value.filter(s => s.trade_result === 'breakeven').length

const getOverallWinRate = () => {
  const total = getOverallSuccessCount() + getOverallFailureCount() // 攤平不計入勝率
  return total > 0 ? Math.round((getOverallSuccessCount() / total) * 100) : 0
}

//  計算7天週期的累積盈利統計
const getWeeklyProfitStats = () => {
  if (savedShortTermHistory.value.length === 0) {
    return { currentWeek: 0, lastWeek: 0 }
  }

  const now = new Date()
  
  // 找到第一筆交易的時間作為起始點
  const firstTradeDate = new Date(Math.min(...savedShortTermHistory.value.map(s => 
    new Date(s.archived_at || 0).getTime()
  )))
  
  // 計算從第一筆交易開始的完整週數
  const daysSinceFirstTrade = Math.floor((now.getTime() - firstTradeDate.getTime()) / (1000 * 60 * 60 * 24))
  const weeksSinceStart = Math.floor(daysSinceFirstTrade / 7)
  
  // 計算當前週期的開始時間（從第一筆交易開始的第N個7天週期）
  const currentWeekStart = new Date(firstTradeDate.getTime() + (weeksSinceStart * 7 * 24 * 60 * 60 * 1000))
  const lastWeekStart = new Date(currentWeekStart.getTime() - (7 * 24 * 60 * 60 * 1000))
  const lastWeekEnd = new Date(currentWeekStart.getTime() - 1)

  // 篩選當前7天週期的交易
  const currentWeekTrades = savedShortTermHistory.value.filter(signal => {
    const tradeDate = new Date(signal.archived_at || 0)
    return tradeDate >= currentWeekStart && tradeDate <= now
  })

  // 篩選上一個7天週期的交易
  const lastWeekTrades = savedShortTermHistory.value.filter(signal => {
    const tradeDate = new Date(signal.archived_at || 0)
    return tradeDate >= lastWeekStart && tradeDate <= lastWeekEnd
  })

  // 計算累積盈利
  const currentWeekProfit = currentWeekTrades.reduce((sum, signal) => {
    return sum + (signal.profit_percent || 0)
  }, 0)

  const lastWeekProfit = lastWeekTrades.reduce((sum, signal) => {
    return sum + (signal.profit_percent || 0)
  }, 0)

  return {
    currentWeek: currentWeekProfit,
    lastWeek: lastWeekProfit,
    currentWeekStart,
    currentWeekTrades: currentWeekTrades.length,
    lastWeekTrades: lastWeekTrades.length
  }
}

// 🚀 突破信號統計函數
const getOverallBreakoutCount = () => savedShortTermHistory.value.filter(s => isHistoricalBreakoutSignal(s)).length

const getBreakoutWinRate = () => {
  const breakoutSignals = savedShortTermHistory.value.filter(s => isHistoricalBreakoutSignal(s))
  const successfulBreakouts = breakoutSignals.filter(s => s.trade_result === 'success')
  const totalBreakouts = breakoutSignals.filter(s => s.trade_result === 'success' || s.trade_result === 'failure')
  return totalBreakouts.length > 0 ? Math.round((successfulBreakouts.length / totalBreakouts.length) * 100) : 0
}

const getSuccessCount = (symbol: string) => {
  return savedShortTermHistory.value.filter(s => s.symbol === symbol && s.trade_result === 'success').length
}

const getFailureCount = (symbol: string) => {
  return savedShortTermHistory.value.filter(s => s.symbol === symbol && s.trade_result === 'failure').length
}

const getBreakevenCount = (symbol: string) => {
  return savedShortTermHistory.value.filter(s => s.symbol === symbol && s.trade_result === 'breakeven').length
}

const calculateWinRate = (symbol: string) => {
  const success = getSuccessCount(symbol)
  const failure = getFailureCount(symbol)
  const total = success + failure // 攤平不計入勝率
  return total > 0 ? Math.round((success / total) * 100) : 0
}

//  計算特定幣種的7天週期盈利統計
const getSymbolWeeklyProfitStats = (symbol: string) => {
  const symbolSignals = savedShortTermHistory.value.filter(s => s.symbol === symbol)
  
  if (symbolSignals.length === 0) {
    return { currentWeek: 0, lastWeek: 0 }
  }

  const now = new Date()
  
  // 找到該幣種第一筆交易的時間
  const firstTradeDate = new Date(Math.min(...symbolSignals.map(s => 
    new Date(s.archived_at || 0).getTime()
  )))
  
  // 計算週期
  const daysSinceFirstTrade = Math.floor((now.getTime() - firstTradeDate.getTime()) / (1000 * 60 * 60 * 24))
  const weeksSinceStart = Math.floor(daysSinceFirstTrade / 7)
  
  const currentWeekStart = new Date(firstTradeDate.getTime() + (weeksSinceStart * 7 * 24 * 60 * 60 * 1000))
  const lastWeekStart = new Date(currentWeekStart.getTime() - (7 * 24 * 60 * 60 * 1000))
  const lastWeekEnd = new Date(currentWeekStart.getTime() - 1)

  // 篩選當前週期和上週期的交易
  const currentWeekTrades = symbolSignals.filter(signal => {
    const tradeDate = new Date(signal.archived_at || 0)
    return tradeDate >= currentWeekStart && tradeDate <= now
  })

  const lastWeekTrades = symbolSignals.filter(signal => {
    const tradeDate = new Date(signal.archived_at || 0)
    return tradeDate >= lastWeekStart && tradeDate <= lastWeekEnd
  })

  const currentWeekProfit = currentWeekTrades.reduce((sum, signal) => {
    return sum + (signal.profit_percent || 0)
  }, 0)

  const lastWeekProfit = lastWeekTrades.reduce((sum, signal) => {
    return sum + (signal.profit_percent || 0)
  }, 0)

  return {
    currentWeek: currentWeekProfit,
    lastWeek: lastWeekProfit
  }
}

// 樣式相關函數
const getResultBadgeClass = (result?: string) => {
  switch (result) {
    case 'success': return 'bg-green-100 text-green-800'
    case 'failure': return 'bg-red-100 text-red-800'
    case 'breakeven': return 'bg-gray-100 text-gray-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const getResultText = (result?: string) => {
  switch (result) {
    case 'success': return '成功'
    case 'failure': return '失敗'
    case 'breakeven': return '攤平'
    default: return '未知'
  }
}

const getProfitClass = (profit?: number) => {
  if (!profit) return 'text-gray-600'
  return profit > 0 ? 'text-green-600' : profit < 0 ? 'text-red-600' : 'text-gray-600'
}

const getProfitDisplay = (result?: string, profit?: number) => {
  if (!profit) return '0.00%'
  const sign = result === 'success' ? '+' : result === 'failure' ? '-' : ''
  return `${sign}${profit.toFixed(2)}%`
}

const getConfidenceBarClass = (confidence: number) => {
  if (confidence >= 0.8) return 'bg-green-500'
  if (confidence >= 0.6) return 'bg-yellow-500'
  return 'bg-red-500'
}

const getArchiveReasonClass = (reason?: string) => {
  switch (reason) {
    case 'expired': return 'bg-orange-100 text-orange-800'
    case 'completed': return 'bg-green-100 text-green-800'
    case 'stopped': return 'bg-red-100 text-red-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const getArchiveReasonText = (reason?: string) => {
  switch (reason) {
    case 'expired': return '時效結束'
    case 'completed': return '已完成'
    case 'stopped': return '已停止'
    default: return '其他'
  }
}

// 操作函數
const selectCategory = (symbol: string) => {
  selectedCategory.value = symbol
  currentPage.value = 1
}

const goBack = () => {
  router.push({ name: 'Dashboard' })
}

// 🔄 手動重新計算交易結果
const manualRecalculate = () => {
  isLoading.value = true
  loadingMessage.value = '正在根據新的攤平邏輯重新計算交易結果...'
  
  try {
    // 獲取原始統計
    const originalCounts = {
      success: savedShortTermHistory.value.filter(s => s.result === 'success').length,
      failure: savedShortTermHistory.value.filter(s => s.result === 'failure').length,
      breakeven: savedShortTermHistory.value.filter(s => s.result === 'breakeven').length
    }
    
    // 重新計算每個信號的結果
    savedShortTermHistory.value.forEach(signal => {
      const newResult = calculateUpdatedTradeResult(signal)
      const oldResult = signal.result
      
      if (oldResult !== newResult) {
        signal.result = newResult
        console.log(`📊 ${signal.symbol} 結果變更: ${oldResult} → ${newResult} (利潤: ${signal.profit_percent}%)`)
      }
    })
    
    // 更新 localStorage
    localStorage.setItem('tradingx_shortterm_history', JSON.stringify(savedShortTermHistory.value))
    
    // 獲取新統計
    const newCounts = {
      success: savedShortTermHistory.value.filter(s => s.result === 'success').length,
      failure: savedShortTermHistory.value.filter(s => s.result === 'failure').length,
      breakeven: savedShortTermHistory.value.filter(s => s.result === 'breakeven').length
    }
    
    // 顯示變更統計
    const changes = []
    if (originalCounts.success !== newCounts.success) {
      changes.push(`成功: ${originalCounts.success} → ${newCounts.success}`)
    }
    if (originalCounts.failure !== newCounts.failure) {
      changes.push(`失敗: ${originalCounts.failure} → ${newCounts.failure}`)
    }
    if (originalCounts.breakeven !== newCounts.breakeven) {
      changes.push(`攤平: ${originalCounts.breakeven} → ${newCounts.breakeven}`)
    }
    
    if (changes.length > 0) {
      alert(`✅ 重算完成！\n\n變更統計:\n${changes.join('\n')}\n\n新攤平標準: 0% < 利潤 < 0.5%`)
    } else {
      alert('✅ 重算完成！沒有需要變更的記錄。')
    }
    
  } catch (error) {
    console.error('重算失敗:', error)
    alert('❌ 重算失敗，請檢查控制台獲取詳細信息')
  } finally {
    isLoading.value = false
  }
}

// 修正做空信號的利潤方向性
const fixProfitDirections = () => {
  if (!confirm('⚠️ 此操作會修正所有做空信號的利潤方向性，確定要繼續嗎？\n\n修正邏輯：做空信號的正利潤會被轉換為負利潤')) {
    return
  }
  
isLoading.value = true
  loadingMessage.value = '正在修正做空信號的利潤方向性...'
  
  try {
    let fixedCount = 0
    
    savedShortTermHistory.value.forEach(signal => {
      const direction = getSignalDirection(signal.signal_type)
      
      // 只處理做空信號且利潤為正數的情況
      if (direction === 'SHORT' && signal.profit_percent && signal.profit_percent > 0) {
        const oldProfit = signal.profit_percent
        signal.profit_percent = -signal.profit_percent // 轉為負數
        
        // 重新計算結果
        const newResult = calculateUpdatedTradeResult(signal)
        ;(signal as any).result = newResult
        
        console.log(`🔧 修正 ${signal.symbol} 做空利潤: ${oldProfit}% -> ${signal.profit_percent}%，結果: ${newResult}`)
        fixedCount++
      }
    })
    
    if (fixedCount > 0) {
      // 更新 localStorage
      localStorage.setItem('tradingx_shortterm_history', JSON.stringify(savedShortTermHistory.value))
      alert(`✅ 修正完成！\n\n共修正了 ${fixedCount} 個做空信號的利潤方向`)
    } else {
      alert('ℹ️ 沒有需要修正的做空信號')
    }
    
  } catch (error) {
    console.error('修正失敗:', error)
    alert('❌ 修正失敗，請檢查控制台獲取詳細信息')
  } finally {
    isLoading.value = false
  }
}

// 手動重算（舊函數，保持兼容性）
const recalculateResults = manualRecalculate

const exportHistory = () => {
  try {
    const csv = convertToCSV(filteredHistory.value)
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `短線信號歷史_${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('匯出失敗:', error)
  }
}

const convertToCSV = (data: Signal[]) => {
  const headers = ['幣種', '信號方向', '開倉價', '結算價', '利潤(%)', '結果', '信心度(%)', '策略', '歸檔時間', '歸檔原因']
  
  const rows = data.map(signal => [
    signal.symbol,
    getSignalDirection(signal.signal_type) === 'LONG' ? '做多' : '做空',
    signal.entry_price?.toFixed(4) || 'N/A',
    signal.current_price?.toFixed(4) || 'N/A',
    signal.profit_percent?.toFixed(2) || '0.00',
    getResultText(signal.trade_result),
    Math.round(signal.confidence * 100),
    signal.strategy_name || (signal.is_scalping ? '短線專用' : '中長線篩選'),
    formatTime(signal.archived_at || ''),
    getArchiveReasonText(signal.archive_reason)
  ])

  return [headers, ...rows].map(row => row.map(cell => `"${cell}"`).join(',')).join('\n')
}

const clearConfirmDetails = computed(() => {
  if (selectedCategory.value === 'ALL') {
    return ['將清除所有短線信號歷史記錄', '此操作無法撤銷', '請謹慎操作']
  } else {
    return [`將清除 ${selectedCategory.value} 的歷史記錄`, '此操作無法撤銷', '請謹慎操作']
  }
})

// 🚀 判斷歷史信號是否為突破信號
const isHistoricalBreakoutSignal = (signal: Signal): boolean => {
  // 基於歷史數據判斷是否為突破信號
  // 條件：高信心度 + 成功結果 + 高利潤
  return signal.confidence > 0.8 && 
         signal.trade_result === 'success' && 
         (signal.profit_percent || 0) > 3.0
}

const confirmClearHistory = () => {
  try {
    if (selectedCategory.value === 'ALL') {
      savedShortTermHistory.value = []
      Object.keys(shortTermCategories.value).forEach(key => {
        shortTermCategories.value[key].signals = []
        shortTermCategories.value[key].count = 0
      })
    } else {
      savedShortTermHistory.value = savedShortTermHistory.value.filter(signal => 
        signal.symbol !== selectedCategory.value
      )
      if (shortTermCategories.value[selectedCategory.value]) {
        shortTermCategories.value[selectedCategory.value].signals = []
        shortTermCategories.value[selectedCategory.value].count = 0
      }
    }

    // 更新 localStorage
    localStorage.setItem('tradingx_shortterm_history', JSON.stringify(savedShortTermHistory.value))
    localStorage.setItem('tradingx_shortterm_categories', JSON.stringify(shortTermCategories.value))
    
    showClearConfirm.value = false
    currentPage.value = 1
  } catch (error) {
    console.error('清除歷史記錄失敗:', error)
  }
}

// 組件掛載
onMounted(() => {
  loadShortTermHistory()
})
</script>
