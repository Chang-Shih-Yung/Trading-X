<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <LoadingOverlay :show="isLoading" :title="loadingMessage" message="請稍候..." />
    <div class="max-w-7xl mx-auto">
      <!-- 頁面標題 -->
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900">短線歷史數據</h1>
        <div class="flex items-center space-x-3">
          <button @click="goBack"
            class="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white text-sm font-medium rounded-md transition-colors flex items-center space-x-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18">
              </path>
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
              <div class="text-sm text-gray-500">總計</div>
            </div>
          </div>
          <div class="mt-4 grid grid-cols-2 gap-2 text-xs">
            <div class="text-center">
              <div class="text-lg font-semibold">
                <span class="font-medium" :class="getOverallWinRate() > 0 ? 'text-green-600' : 'text-red-600'">
                  {{ getOverallWinRate() }}%
                </span>
              </div>
              <div class="text-gray-500">勝率</div>
            </div>
            <div class="text-center">
              <div class="text-lg font-semibold">
                <span class="font-medium text-green-600">{{ getOverallSuccessCount() }}</span> /
                <span class="font-medium text-red-600">{{ getOverallFailureCount() }}</span> /
                <span class="font-medium text-gray-600">{{ getOverallBreakevenCount() }}</span>
              </div>
              <div class="text-gray-500">賺錢/虧損/平手</div>
            </div>
            <div class="text-center">
              <div class="text-lg font-semibold">
                <span class="font-medium text-orange-600">{{ getOverallBreakoutCount() }}</span>
              </div>
              <div class="text-gray-500">突破信號</div>
            </div>
            <div class="text-center">
              <div class="text-lg font-semibold">
                <span class="font-medium text-purple-600">{{ getBreakoutWinRate() }}%</span>
              </div>
              <div class="text-gray-500">突破勝率</div>
            </div>
          </div>
        </div>

        <!-- 週盈虧 -->
        <div class="bg-white shadow rounded-lg p-6 border-l-4 border-blue-500">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-lg font-semibold text-gray-900">本週盈虧</h3>
              <p class="text-sm text-gray-500">Current Week</p>
            </div>
            <div class="text-right">
              <div class="text-2xl font-bold"
                :class="typeof getWeeklyProfitStats().currentWeek === 'number' && getWeeklyProfitStats().currentWeek >= 0 ? 'text-green-600' : 'text-red-600'">
                <span v-if="typeof getWeeklyProfitStats().currentWeek === 'number'">
                  {{ getWeeklyProfitStats().currentWeek >= 0 ? '+' : '' }}{{
                    getWeeklyProfitStats().currentWeek.toFixed(2) }}%
                </span>
                <span v-else class="text-gray-500">
                  無數據
                </span>
              </div>
              <div class="text-sm text-gray-500">本週累計</div>
            </div>
          </div>
          <div class="mt-2 text-xs text-gray-500">
            上週:
            <span v-if="typeof getWeeklyProfitStats().lastWeek === 'number'" class="font-medium"
              :class="getWeeklyProfitStats().lastWeek >= 0 ? 'text-green-600' : 'text-red-600'">
              {{ getWeeklyProfitStats().lastWeek >= 0 ? '+' : '' }}{{ getWeeklyProfitStats().lastWeek.toFixed(2) }}%
            </span>
            <span v-else class="font-medium text-gray-500">
              無數據
            </span>
          </div>
        </div>

        <!-- 分類統計卡片 -->
        <div v-for="(category, symbol) in shortTermCategories" :key="symbol"
          class="bg-white shadow rounded-lg p-6 border-l-4 border-purple-500 cursor-pointer hover:shadow-lg transition-shadow"
          @click="selectCategory(symbol)"
          :class="{ 'ring-2 ring-purple-500 ring-opacity-50': selectedCategory === symbol }">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-lg font-semibold text-gray-900">{{ category.name }}</h3>
              <p class="text-sm text-gray-500">幣種統計</p>
            </div>
            <div class="text-right">
              <div class="text-2xl font-bold text-purple-600">{{ category.count }}</div>
              <div class="text-sm text-gray-500">筆數</div>
            </div>
          </div>
          <div class="mt-4 grid grid-cols-2 gap-2 text-xs">
            <div class="text-center">
              <div class="text-lg font-semibold">
                <span class="font-medium" :class="getCategoryWinRate(symbol) > 0 ? 'text-green-600' : 'text-red-600'">
                  {{ getCategoryWinRate(symbol) }}%
                </span>
              </div>
              <div class="text-gray-500">勝率</div>
            </div>
            <div class="text-center">
              <div class="text-lg font-semibold">
                <span v-if="typeof getCategoryProfitSum(symbol) === 'number'" class="font-medium"
                  :class="getCategoryProfitSum(symbol) >= 0 ? 'text-green-600' : 'text-red-600'">
                  {{ getCategoryProfitSum(symbol) >= 0 ? '+' : '' }}{{ getCategoryProfitSum(symbol).toFixed(2) }}%
                </span>
                <span v-else class="font-medium text-gray-500">
                  無數據
                </span>
              </div>
              <div class="text-gray-500">累計盈虧</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 控制面板 -->
      <div class="mb-6 bg-white shadow rounded-lg p-6">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div class="flex items-center space-x-4">
            <div class="flex items-center space-x-2">
              <label class="text-sm font-medium text-gray-700">分類篩選:</label>
              <select v-model="selectedCategory"
                class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent">
                <option value="">全部</option>
                <option v-for="(category, symbol) in shortTermCategories" :key="symbol" :value="symbol">
                  {{ category.name }} ({{ category.count }} 筆)
                </option>
              </select>
            </div>

            <div class="flex items-center space-x-2">
              <label class="text-sm font-medium text-gray-700">結果篩選:</label>
              <select v-model="selectedResult"
                class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent">
                <option value="">全部結果</option>
                <option value="success">賺錢</option>
                <option value="failure">虧損</option>
                <option value="breakeven">平手</option>
              </select>
            </div>

            <div class="flex items-center space-x-2">
              <label class="text-sm font-medium text-gray-700">方向篩選:</label>
              <select v-model="selectedDirection"
                class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent">
                <option value="">全部方向</option>
                <option value="LONG">做多</option>
                <option value="SHORT">做空</option>
              </select>
            </div>

            <div class="flex items-center space-x-2">
              <label class="text-sm font-medium text-gray-700">排序方式:</label>
              <select v-model="sortOption"
                class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent">
                <option value="profit">盈利表現（預設）</option>
                <option value="time">時間（最新優先）</option>
              </select>
            </div>
          </div>

          <div class="flex items-center space-x-3">
            <button @click="clearSelectedHistory"
              class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-md transition-colors">
              清除選定歷史
            </button>
            <button @click="refreshHistory"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md transition-colors">
              重新載入
            </button>
          </div>
        </div>
      </div>

      <!-- 歷史記錄表格 -->
      <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg leading-6 font-medium text-gray-900">短線信號歷史記錄</h3>
          <p class="mt-1 text-sm text-gray-500">
            顯示 {{ filteredHistory.length }} 筆過期短線信號，
            <span v-if="sortOption === 'time'">按時間排序（最新的在前）</span>
            <span v-else>按盈利表現排序（🥇最佳表現在前）</span>
          </p>
          <div v-if="sortOption === 'profit'" class="mt-2 flex items-center space-x-4 text-xs text-gray-400">
            <span class="flex items-center">
              <span class="w-3 h-3 bg-yellow-500 rounded-full mr-1"></span>
              第1名：金牌
            </span>
            <span class="flex items-center">
              <span class="w-3 h-3 bg-gray-400 rounded-full mr-1"></span>
              第2名：銀牌
            </span>
            <span class="flex items-center">
              <span class="w-3 h-3 bg-yellow-600 rounded-full mr-1"></span>
              第3名：銅牌
            </span>
            <span class="flex items-center">
              <span class="w-3 h-3 bg-blue-500 rounded-full mr-1"></span>
              前10名
            </span>
            <span class="flex items-center">
              <span class="w-3 h-3 bg-green-500 rounded-full mr-1"></span>
              前50名
            </span>
          </div>
          <div v-else class="mt-2 flex items-center space-x-4 text-xs text-gray-400">
            <span>按歸檔時間排序，較新的記錄顯示在前面</span>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  排名
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  信號資訊
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  價格資訊
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  交易結果
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  時間資訊
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  策略
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  歸檔原因
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(signal, index) in paginatedHistory" :key="signal.id" class="hover:bg-gray-50">
                <!-- 排名編號 -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center justify-center">
                    <span v-if="sortOption === 'profit'"
                      class="inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold"
                      :class="getRankBadgeClass(getGlobalRank(signal, index))">
                      {{ getGlobalRank(signal, index) }}
                    </span>
                    <span v-else
                      class="inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold bg-blue-100 text-blue-800">
                      {{ getGlobalRank(signal, index) }}
                    </span>
                  </div>
                </td>
                <!-- 信號資訊 -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="flex-shrink-0">
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                        :class="getDirectionClass(signal)">
                        {{ getDirectionText(signal) }}
                      </span>
                    </div>
                    <div class="ml-3">
                      <div class="text-sm font-medium text-gray-900">{{ signal.symbol }}</div>
                      <div class="text-sm text-gray-500">信心度: {{ (signal.confidence * 100).toFixed(1) }}%</div>
                    </div>
                  </div>
                </td>

                <!-- 價格資訊 -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">
                    <div>進場: ${{ signal.entry_price?.toFixed(4) || 'N/A' }}</div>
                    <div>當前: ${{ signal.current_price?.toFixed(4) || 'N/A' }}</div>
                    <div v-if="signal.stop_loss">止損: ${{ signal.stop_loss.toFixed(4) }}</div>
                    <div v-if="signal.take_profit">止盈: ${{ signal.take_profit.toFixed(4) }}</div>
                  </div>
                </td>

                <!-- 交易結果 -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center space-x-2">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="getTradeResultClass(signal.tradeResult)">
                      {{ getTradeResultText(signal.tradeResult) }}
                    </span>
                    <!-- 特殊表現標記 (只在盈利排序時顯示) -->
                    <span v-if="sortOption === 'profit' && getGlobalRank(signal, index) <= 3"
                      class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-bold"
                      :class="getPerformanceBadgeClass(getGlobalRank(signal, index))">
                      {{ getPerformanceText(getGlobalRank(signal, index)) }}
                    </span>
                  </div>
                  <div class="mt-1 text-sm font-medium" :class="typeof signal.profitPercent === 'number'
                    ? (signal.profitPercent >= 0 ? 'text-green-600' : 'text-red-600')
                    : 'text-gray-500'">
                    <span v-if="typeof signal.profitPercent === 'number'">
                      {{ signal.profitPercent >= 0 ? '+' : '' }}{{ signal.profitPercent.toFixed(2) }}%
                    </span>
                    <span v-else>
                      {{ signal.profitPercent }}
                    </span>
                  </div>
                </td>

                <!-- 時間資訊 -->
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <div>生成: {{ formatDateTime(signal.timestamp) }}</div>
                  <div>歸檔: {{ formatDateTime(signal.archiveTime) }}</div>
                </td>

                <!-- 策略 -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">
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
              顯示 {{ (currentPage - 1) * itemsPerPage + 1 }} 到 {{ Math.min(currentPage * itemsPerPage,
                filteredHistory.length) }}
              筆，共 {{ filteredHistory.length }} 筆記錄
            </div>
            <div class="flex items-center space-x-2">
              <button @click="currentPage = Math.max(1, currentPage - 1)" :disabled="currentPage === 1"
                class="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50">
                上一頁
              </button>
              <span class="px-3 py-1 text-sm">第 {{ currentPage }} 頁，共 {{ totalPages }} 頁</span>
              <button @click="currentPage = Math.min(totalPages, currentPage + 1)"
                :disabled="currentPage === totalPages"
                class="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50">
                下一頁
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 清除確認彈窗 -->
    <ConfirmDialog v-model:show="showClearConfirm" title="確認清除歷史記錄" message="您確定要清除選定的短線信號歷史記錄嗎？"
      :details="[clearConfirmDetails]" confirm-text="確認清除" cancel-text="取消" type="danger" @confirm="confirmClearHistory"
      @cancel="showClearConfirm = false" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import LoadingOverlay from '@/components/LoadingOverlay.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

// 路由
const router = useRouter()

// 響應式數據
const isLoading = ref(false)
const loadingMessage = ref('載入中...')
const savedShortTermHistory = ref<any[]>([])
const shortTermCategories = ref<Record<string, { name: string; signals: any[]; count: number }>>({})

// 篩選和分頁
const selectedCategory = ref('')
const selectedResult = ref('')
const selectedDirection = ref('')
const sortOption = ref('profit') // 預設按盈利排序
const currentPage = ref(1)
const itemsPerPage = 10

// 清除確認
const showClearConfirm = ref(false)
const clearConfirmDetails = ref('')

// 計算交易結果 - 優先使用真實數據，無真實數據時返回 LOSE PRICE
const calculateTradeResult = (signal: any) => {
  // 🔥 優先使用資料庫中的真實結果
  if (signal.trade_result && ['success', 'failure', 'breakeven'].includes(signal.trade_result)) {
    console.log(`✅ 使用真實交易結果: ${signal.symbol} -> ${signal.trade_result}`)
    return signal.trade_result
  }

  // 如果沒有真實數據，返回"LOSE PRICE"字串
  console.log(`❌ ${signal.symbol} 缺少真實交易結果，返回 LOSE PRICE`)
  return "LOSE PRICE"
}

// 計算盈虧百分比 - 優先使用真實數據，無真實數據時返回 LOSE PRICE
const calculateProfitPercent = (signal: any) => {
  // 🔥 優先使用資料庫中的真實盈虧數據
  if (signal.profit_loss_pct !== undefined && signal.profit_loss_pct !== null) {
    console.log(`✅ 使用真實盈虧數據: ${signal.symbol} -> ${signal.profit_loss_pct.toFixed(2)}%`)
    return signal.profit_loss_pct
  }

  // 如果沒有真實數據，返回"LOSE PRICE"字串
  console.log(`❌ ${signal.symbol} 缺少真實盈虧數據，返回 LOSE PRICE`)
  return "LOSE PRICE"
}

// 更新分類統計
const updateCategories = () => {
  const categories: Record<string, { name: string; signals: any[]; count: number }> = {}

  savedShortTermHistory.value.forEach(signal => {
    if (!categories[signal.symbol]) {
      categories[signal.symbol] = {
        name: signal.symbol,
        signals: [],
        count: 0
      }
    }
    categories[signal.symbol].signals.push(signal)
    categories[signal.symbol].count += 1
  })

  shortTermCategories.value = categories
  console.log(`📂 更新分類統計: ${Object.keys(categories).length} 個幣種`)
}

// 載入主要的短線歷史數據（優先從後端API載入）
const loadShortTermHistory = async () => {
  try {
    isLoading.value = true
    loadingMessage.value = '正在從後端載入過期信號...'

    // 1. 先嘗試從後端 API 載入過期信號
    console.log('🔄 正在從後端API載入過期短線信號...')

    const response = await fetch('/api/v1/scalping/expired', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })

    console.log(`📡 API 響應狀態: ${response.status}`)
    console.log(`📡 API 響應狀態文本: ${response.statusText}`)

    if (response.ok) {
      const expiredSignals = await response.json()
      console.log('✅ API 響應成功，返回數據:', expiredSignals)

      if (expiredSignals && expiredSignals.length > 0) {
        // 轉換後端數據格式以匹配前端格式
        savedShortTermHistory.value = expiredSignals.map((signal: any) => {
          const processedSignal = {
            ...signal,
            timestamp: signal.created_at,
            archiveTime: signal.archived_at || signal.updated_at || signal.created_at,
            currentPrice: signal.current_price || signal.entry_price,
          }

          // 🔥 優先使用資料庫中的真實交易結果和盈虧數據
          let profitPercent = signal.profit_loss_pct
          let tradeResult = signal.trade_result

          // 如果資料庫沒有真實結果，計算一次並保存結果，避免重複計算
          if (profitPercent === undefined || profitPercent === null) {
            profitPercent = calculateProfitPercent(processedSignal)
            console.log(`📊 ${signal.symbol}: 使用計算的盈虧=${profitPercent}`)
          } else {
            console.log(`✅ ${signal.symbol}: 使用真實盈虧=${typeof profitPercent === 'number' ? profitPercent.toFixed(2) + '%' : profitPercent}`)
          }

          if (!tradeResult || !['success', 'failure', 'breakeven'].includes(tradeResult)) {
            tradeResult = calculateTradeResult(processedSignal)
            console.log(`📊 ${signal.symbol}: 使用計算的結果=${tradeResult}`)
          } else {
            console.log(`✅ ${signal.symbol}: 使用真實結果=${tradeResult}`)
          }

          processedSignal.profitPercent = profitPercent
          processedSignal.tradeResult = tradeResult

          // 🔧 調試：檢查關鍵欄位
          if (!processedSignal.id || !processedSignal.symbol || !processedSignal.entry_price) {
            console.warn(`⚠️ 信號資料不完整: ID=${processedSignal.id}, Symbol=${processedSignal.symbol}, Entry=${processedSignal.entry_price}`)
          }

          // 檢查 tradeResult 是否有效
          if (!['success', 'failure', 'breakeven'].includes(tradeResult)) {
            console.warn(`⚠️ 無效的交易結果: ${signal.symbol} -> ${tradeResult}`)
          }

          return processedSignal
        })

        console.log(`✅ 從API載入 ${savedShortTermHistory.value.length} 筆過期短線信號`)
        updateCategories()
        return // 成功載入，直接返回
      } else {
        console.log('⚠️ 後端API返回空數據')
        savedShortTermHistory.value = []
        updateCategories()
        return
      }
    } else {
      // 獲取錯誤響應內容
      const errorText = await response.text()
      console.error('❌ 後端API請求失敗:')
      console.error(`狀態碼: ${response.status}`)
      console.error(`狀態文本: ${response.statusText}`)
      console.error(`錯誤內容: ${errorText}`)

      // 顯示錯誤信息給用戶
      savedShortTermHistory.value = []
      updateCategories()

      // 可以選擇在這裡顯示錯誤通知
      alert(`API 錯誤 ${response.status}: ${response.statusText}\n詳細信息: ${errorText}`)
      return
    }
  } catch (error) {
    console.error('❌ 請求過程中發生錯誤:', error)
    savedShortTermHistory.value = []
    updateCategories()

    // 顯示網絡錯誤
    alert(`網絡錯誤: ${(error as Error).message || error}`)
  } finally {
    isLoading.value = false
  }
}

// 計算屬性
const filteredHistory = computed(() => {
  let filtered = savedShortTermHistory.value

  // 🔧 調試：記錄初始狀態
  console.log(`🔍 過濾邏輯開始 - 原始數據: ${filtered.length} 筆`)

  if (selectedCategory.value) {
    const beforeFilter = filtered.length
    filtered = filtered.filter(signal => signal.symbol === selectedCategory.value)
    console.log(`🔍 分類過濾 (${selectedCategory.value}): ${beforeFilter} -> ${filtered.length}`)
  }

  if (selectedResult.value) {
    const beforeFilter = filtered.length
    filtered = filtered.filter(signal => signal.tradeResult === selectedResult.value)
    console.log(`🔍 結果過濾 (${selectedResult.value}): ${beforeFilter} -> ${filtered.length}`)
  }

  if (selectedDirection.value) {
    const beforeFilter = filtered.length
    filtered = filtered.filter(signal => {
      const direction = signal.direction || signal.signal_type || ''
      if (selectedDirection.value === 'LONG') {
        return direction.includes('LONG') || direction.includes('UP') ||
          direction.includes('MOMENTUM_BREAKOUT') ||
          (!direction.includes('SHORT') && !direction.includes('DOWN'))
      } else if (selectedDirection.value === 'SHORT') {
        return direction.includes('SHORT') || direction.includes('DOWN') ||
          direction.includes('SCALP_SHORT')
      }
      return true
    })
    console.log(`🔍 方向過濾 (${selectedDirection.value}): ${beforeFilter} -> ${filtered.length}`)
  }

  // 按照選定的排序方式排序
  if (sortOption.value === 'time') {
    // 按時間排序：最新的在前
    const sorted = filtered.sort((a, b) => {
      const timeA = new Date(a.archiveTime || a.timestamp || 0).getTime()
      const timeB = new Date(b.archiveTime || b.timestamp || 0).getTime()

      // 優先按歸檔時間排序（較新的在前）
      if (timeB !== timeA) {
        return timeB - timeA // 降序：較新的在前
      }

      // 如果時間相同，按盈利排序作為次要排序（只對有效數據排序）
      const profitA = typeof a.profitPercent === 'number' ? a.profitPercent : -999999
      const profitB = typeof b.profitPercent === 'number' ? b.profitPercent : -999999
      return profitB - profitA // 降序：高盈利在前
    })
    console.log(`🔍 時間排序完成: ${sorted.length} 筆信號`)
    return sorted
  } else {
    // 按照盈利百分比排序：從高到低（最好的數據在前）
    // 🔥 排除 LOSE PRICE 信號，這些信號排在最後
    const validSignals = filtered.filter(signal => {
      const profitPercent = signal.profitPercent
      return profitPercent !== "LOSE PRICE" && typeof profitPercent === 'number'
    })

    const losePriceSignals = filtered.filter(signal => {
      const profitPercent = signal.profitPercent
      return profitPercent === "LOSE PRICE" || typeof profitPercent !== 'number'
    })

    // 對有效信號進行排序
    const sortedValidSignals = validSignals.sort((a, b) => {
      const profitA = a.profitPercent || 0
      const profitB = b.profitPercent || 0

      // 優先按盈利排序
      if (profitB !== profitA) {
        return profitB - profitA // 降序：高盈利在前
      }

      // 如果盈利相同，按信心度排序
      const confidenceA = a.confidence || 0
      const confidenceB = b.confidence || 0
      if (confidenceB !== confidenceA) {
        return confidenceB - confidenceA // 降序：高信心度在前
      }

      // 如果信心度也相同，按時間排序（較新的在前）
      const timeA = new Date(a.archiveTime || a.timestamp || 0).getTime()
      const timeB = new Date(b.archiveTime || b.timestamp || 0).getTime()
      return timeB - timeA // 降序：較新的在前
    })

    // 對 LOSE PRICE 信號按時間排序（較新的在前）
    const sortedLosePriceSignals = losePriceSignals.sort((a, b) => {
      const timeA = new Date(a.archiveTime || a.timestamp || 0).getTime()
      const timeB = new Date(b.archiveTime || b.timestamp || 0).getTime()
      return timeB - timeA // 降序：較新的在前
    })

    // 將有效信號排在前面，LOSE PRICE 信號排在後面
    const sorted = [...sortedValidSignals, ...sortedLosePriceSignals]

    console.log(`🔍 盈利排序完成: ${sortedValidSignals.length} 筆有效信號 + ${sortedLosePriceSignals.length} 筆 LOSE PRICE 信號`)
    return sorted
  }
})

const paginatedHistory = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredHistory.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredHistory.value.length / itemsPerPage)
})

// 統計計算函數 - 排除 LOSE PRICE 信號
const getOverallWinRate = () => {
  // 只計算有真實結果的信號
  const validSignals = savedShortTermHistory.value.filter(s => s.tradeResult !== 'LOSE PRICE')
  const successful = validSignals.filter(s => s.tradeResult === 'success').length
  const failed = validSignals.filter(s => s.tradeResult === 'failure').length
  const total = successful + failed // 平手不計入勝率計算
  if (total === 0) return 0
  return Math.round((successful / total) * 100)
}

const getOverallSuccessCount = () => {
  return savedShortTermHistory.value.filter(s => s.tradeResult === 'success').length
}

const getOverallFailureCount = () => {
  return savedShortTermHistory.value.filter(s => s.tradeResult === 'failure').length
}

const getOverallBreakevenCount = () => {
  return savedShortTermHistory.value.filter(s => s.tradeResult === 'breakeven').length
}

const getOverallBreakoutCount = () => {
  return savedShortTermHistory.value.filter(s => s.is_breakout || s.strategy_name?.includes('突破')).length
}

const getBreakoutWinRate = () => {
  const breakouts = savedShortTermHistory.value.filter(s => s.is_breakout || s.strategy_name?.includes('突破'))
  // 只計算有真實結果的突破信號
  const validBreakouts = breakouts.filter(s => s.tradeResult !== 'LOSE PRICE')
  const successful = validBreakouts.filter(s => s.tradeResult === 'success').length
  const failed = validBreakouts.filter(s => s.tradeResult === 'failure').length
  const total = successful + failed // 平手不計入勝率計算
  if (total === 0) return 0
  return Math.round((successful / total) * 100)
}

const getWeeklyProfitStats = () => {
  const now = new Date()
  const currentWeekStart = new Date(now.setDate(now.getDate() - now.getDay()))
  const lastWeekStart = new Date(currentWeekStart.getTime() - 7 * 24 * 60 * 60 * 1000)
  const lastWeekEnd = new Date(currentWeekStart.getTime() - 1)

  // 只計算有真實盈虧數據的信號
  const currentWeekSignals = savedShortTermHistory.value.filter(s => {
    const signalDate = new Date(s.archiveTime)
    return signalDate >= currentWeekStart && typeof s.profitPercent === 'number'
  })

  const lastWeekSignals = savedShortTermHistory.value.filter(s => {
    const signalDate = new Date(s.archiveTime)
    return signalDate >= lastWeekStart && signalDate <= lastWeekEnd && typeof s.profitPercent === 'number'
  })

  const currentWeekProfit = currentWeekSignals.reduce((sum, s) => sum + (s.profitPercent || 0), 0)
  const lastWeekProfit = lastWeekSignals.reduce((sum, s) => sum + (s.profitPercent || 0), 0)

  return {
    currentWeek: currentWeekProfit,
    lastWeek: lastWeekProfit
  }
}

const getCategoryWinRate = (symbol: string) => {
  const categorySignals = savedShortTermHistory.value.filter(s => s.symbol === symbol)
  // 只計算有真實結果的信號
  const validSignals = categorySignals.filter(s => s.tradeResult !== 'LOSE PRICE')
  const successful = validSignals.filter(s => s.tradeResult === 'success').length
  const failed = validSignals.filter(s => s.tradeResult === 'failure').length
  const total = successful + failed // 平手不計入勝率計算
  if (total === 0) return 0
  return Math.round((successful / total) * 100)
}

const getCategoryProfitSum = (symbol: string) => {
  const categorySignals = savedShortTermHistory.value.filter(s => s.symbol === symbol)
  // 只計算有真實盈虧數據的信號
  const validSignals = categorySignals.filter(s => typeof s.profitPercent === 'number')
  return validSignals.reduce((sum, s) => sum + (s.profitPercent || 0), 0)
}

// 格式化函數
const formatDateTime = (dateString: string) => {
  if (!dateString) return 'N/A'

  try {
    // 🔧 修復時間格式化問題
    // 確保正確處理 ISO 格式的日期字符串並使用台灣時區
    const date = new Date(dateString)

    // 檢查日期是否有效
    if (isNaN(date.getTime())) {
      console.warn(`無效的日期格式: ${dateString}`)
      return dateString // 返回原始字符串
    }

    // 使用台灣時區格式化，並強制使用24小時制
    const formatted = date.toLocaleString('zh-TW', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'Asia/Taipei', // 明確指定台灣時區
      hour12: false // 使用 24 小時制
    })

    // 🔍 調試：記錄格式化過程（特別是測試信號）
    if (dateString.includes('15:28') || dateString.includes('TESTUSDT')) {
      console.log(`🕐 時間格式化調試:`)
      console.log(`原始: ${dateString}`)
      console.log(`Date對象: ${date.toISOString()}`)
      console.log(`格式化結果: ${formatted}`)
    }

    return formatted
  } catch (error) {
    console.error(`時間格式化錯誤: ${dateString}`, error)
    return dateString // 出錯時返回原始字符串
  }
}

// 判斷信號方向並返回對應的CSS類別
const getDirectionClass = (signal: any) => {
  const direction = signal.direction || signal.signal_type || ''
  const isLong = direction.includes('LONG') || direction.includes('UP') ||
    direction.includes('MOMENTUM_BREAKOUT') ||
    (!direction.includes('SHORT') && !direction.includes('DOWN'))

  return isLong ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
}

// 判斷信號方向並返回對應的文字
const getDirectionText = (signal: any) => {
  const direction = signal.direction || signal.signal_type || ''
  const isLong = direction.includes('LONG') || direction.includes('UP') ||
    direction.includes('MOMENTUM_BREAKOUT') ||
    (!direction.includes('SHORT') && !direction.includes('DOWN'))

  return isLong ? '做多' : '做空'
}

// 獲取全局排名（在所有篩選結果中的位置）
const getGlobalRank = (_signal: any, localIndex: number) => {
  // 計算在當前頁面中的全局排名
  const startIndex = (currentPage.value - 1) * itemsPerPage
  return startIndex + localIndex + 1
}

// 獲取排名徽章樣式
const getRankBadgeClass = (rank: number) => {
  if (rank === 1) {
    return 'bg-yellow-500 text-white' // 金牌
  } else if (rank === 2) {
    return 'bg-gray-400 text-white' // 銀牌
  } else if (rank === 3) {
    return 'bg-yellow-600 text-white' // 銅牌
  } else if (rank <= 10) {
    return 'bg-blue-500 text-white' // 前十名
  } else if (rank <= 50) {
    return 'bg-green-500 text-white' // 前五十名
  } else {
    return 'bg-gray-300 text-gray-700' // 其他
  }
}

// 獲取表現徽章樣式
const getPerformanceBadgeClass = (rank: number) => {
  if (rank === 1) {
    return 'bg-yellow-500 text-white' // 金牌
  } else if (rank === 2) {
    return 'bg-gray-400 text-white' // 銀牌
  } else if (rank === 3) {
    return 'bg-yellow-600 text-white' // 銅牌
  } else {
    return 'bg-blue-500 text-white' // 其他優秀表現
  }
}

// 獲取表現文字
const getPerformanceText = (rank: number) => {
  if (rank === 1) {
    return '🥇'
  } else if (rank === 2) {
    return '🥈'
  } else if (rank === 3) {
    return '🥉'
  } else {
    return '⭐'
  }
}

const getTradeResultClass = (result: string) => {
  switch (result) {
    case 'success': return 'bg-green-100 text-green-800'  // 賺錢 (>+0.5%)
    case 'failure': return 'bg-red-100 text-red-800'      // 虧損 (負值)
    case 'breakeven': return 'bg-gray-100 text-gray-800'  // 平手 (0 到 +0.5%)
    default: return 'bg-yellow-100 text-yellow-800'
  }
}

const getTradeResultText = (result: string) => {
  switch (result) {
    case 'success': return '賺錢'   // 更改為更直觀的文字
    case 'failure': return '虧損'   // 更改為更直觀的文字
    case 'breakeven': return '平手'
    default: return '未知'
  }
}

const getArchiveReasonClass = (reason: string) => {
  switch (reason) {
    case 'expired': return 'bg-orange-100 text-orange-800'
    case 'stopped': return 'bg-red-100 text-red-800'
    case 'profit_taken': return 'bg-green-100 text-green-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const getArchiveReasonText = (reason: string) => {
  switch (reason) {
    case 'expired': return '時間到期'
    case 'stopped': return '止損觸發'
    case 'profit_taken': return '止盈觸發'
    default: return '其他'
  }
}

// 事件處理函數
const selectCategory = (symbol: string) => {
  selectedCategory.value = selectedCategory.value === symbol ? '' : symbol
  currentPage.value = 1
}

const clearSelectedHistory = () => {
  if (selectedCategory.value) {
    clearConfirmDetails.value = `將清除 ${selectedCategory.value} 的歷史記錄`
  } else {
    clearConfirmDetails.value = '將清除全部歷史記錄'
  }
  showClearConfirm.value = true
}

const confirmClearHistory = () => {
  if (selectedCategory.value) {
    // 清除特定分類
    savedShortTermHistory.value = savedShortTermHistory.value.filter(s => s.symbol !== selectedCategory.value)
    selectedCategory.value = ''
  } else {
    // 清除全部
    savedShortTermHistory.value = []
  }

  updateCategories()
  localStorage.setItem('savedShortTermHistory', JSON.stringify(savedShortTermHistory.value))
  localStorage.setItem('shortTermCategories', JSON.stringify(shortTermCategories.value))

  showClearConfirm.value = false
  console.log('🗑️ 歷史記錄已清除')
}

const refreshHistory = () => {
  loadShortTermHistory()
}

const goBack = () => {
  router.push('/')
}

// 載入頁面時執行
onMounted(() => {
  loadShortTermHistory()
})

// 監聽排序選項變更，重置頁面
watch(sortOption, () => {
  currentPage.value = 1
})
</script>
