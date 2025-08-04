<template>
  <div class="signal-history-page">
    <!-- 頁面標題與標籤切換 -->
    <div class="page-header">
      <h3 class="page-title">
        <i class="fas fa-history"></i>
        狙擊手策略分析系統
      </h3>

      <!-- 🎯 新增：標籤頁切換 -->
      <div class="tab-navigation">
        <button @click="activeTab = 'history'" :class="['tab-btn', { active: activeTab === 'history' }]">
          <i class="fas fa-history"></i>
          信號歷史
        </button>
        <button @click="activeTab = 'backtest'" :class="['tab-btn', { active: activeTab === 'backtest' }]">
          <i class="fas fa-chart-bar"></i>
          策略回測
        </button>
      </div>

      <div class="control-panel" v-show="activeTab === 'history'">
        <select v-model="selectedTimeRange" @change="fetchHistoryData" class="time-selector">
          <option value="24">過去24小時</option>
          <option value="72">過去3天</option>
          <option value="168">過去7天</option>
          <option value="720">過去30天</option>
        </select>
        <select v-model="selectedPrecisionLevel" @change="fetchHistoryData" class="precision-selector">
          <option value="high">高精準度信號</option>
          <option value="other">其他精準度信號</option>
          <option value="all">全部信號</option>
        </select>
        <button @click="refreshData" class="refresh-btn" :disabled="isLoading">
          <i class="fas fa-sync-alt" :class="{ spinning: isLoading }"></i>
          刷新數據
        </button>
      </div>
    </div>

    <!-- 🎯 新增：策略回測區塊 -->
    <div v-show="activeTab === 'backtest'" class="backtest-section">
      <!-- 回測控制面板 -->
      <div class="backtest-controls">
        <h2 class="section-title">
          <i class="fas fa-cogs"></i>
          回測參數設定
        </h2>

        <div class="controls-grid">
          <div class="control-group">
            <label>回測週期</label>
            <select v-model="backtestPeriod" class="period-selector">
              <option value="7d">過去 7 天</option>
              <option value="30d">過去 30 天</option>
              <option value="90d">過去 90 天</option>
              <option value="180d">過去 180 天</option>
              <option value="365d">過去 1 年</option>
              <option value="all">全部歷史</option>
            </select>
          </div>

          <div class="control-group">
            <label>包含優化建議</label>
            <input type="checkbox" v-model="includeOptimization" id="optimization-checkbox">
            <label for="optimization-checkbox" class="checkbox-label">啟用</label>
          </div>

          <button @click="runBacktest" class="run-backtest-btn" :disabled="backtestLoading">
            <i class="fas fa-play" v-if="!backtestLoading"></i>
            <i class="fas fa-spinner fa-spin" v-else></i>
            {{ backtestLoading ? '回測執行中...' : '執行回測' }}
          </button>
        </div>
      </div>

      <!-- 快速統計 -->
      <div v-if="quickStats" class="quick-stats">
        <h2 class="section-title">
          <i class="fas fa-tachometer-alt"></i>
          快速統計 ({{ quickStats.period }})
        </h2>

        <div class="quick-stats-grid">
          <div class="quick-stat-card">
            <div class="stat-icon">
              <i class="fas fa-signal"></i>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ quickStats.total_signals }}</div>
              <div class="stat-label">總信號數</div>
            </div>
          </div>

          <div class="quick-stat-card">
            <div class="stat-icon">
              <i class="fas fa-bullseye"></i>
            </div>
            <div class="stat-content">
              <div class="stat-number" :class="getSuccessRateClass(quickStats.win_rate)">
                {{ quickStats.win_rate }}%
              </div>
              <div class="stat-label">勝率</div>
            </div>
          </div>

          <div class="quick-stat-card">
            <div class="stat-icon">
              <i class="fas fa-chart-line"></i>
            </div>
            <div class="stat-content">
              <div class="stat-number" :class="getProfitClass(quickStats.total_pnl)">
                {{ quickStats.total_pnl > 0 ? '+' : '' }}{{ quickStats.total_pnl }}%
              </div>
              <div class="stat-label">總收益</div>
            </div>
          </div>

          <div class="quick-stat-card">
            <div class="stat-icon">
              <i class="fas fa-balance-scale"></i>
            </div>
            <div class="stat-content">
              <div class="stat-number" :class="getProfitFactorClass(quickStats.profit_factor)">
                {{ quickStats.profit_factor }}x
              </div>
              <div class="stat-label">盈虧因子</div>
            </div>
          </div>

          <div class="quick-stat-card">
            <div class="stat-icon">
              <i class="fas fa-trophy"></i>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ quickStats.best_performing_symbol || 'N/A' }}</div>
              <div class="stat-label">最佳幣種</div>
            </div>
          </div>

          <div class="quick-stat-card performance-grade"
            :class="getPerformanceGradeClass(quickStats.performance_grade)">
            <div class="stat-icon">
              <i class="fas fa-medal"></i>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ quickStats.performance_grade || 'N/A' }}</div>
              <div class="stat-label">策略評級</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 詳細回測結果 -->
      <div v-if="backtestResults" class="backtest-results">
        <h2 class="section-title">
          <i class="fas fa-chart-area"></i>
          詳細回測結果
        </h2>

        <!-- 核心指標 -->
        <div class="core-metrics">
          <div class="metrics-grid">
            <div class="metric-card">
              <h4>基礎統計</h4>
              <div class="metric-list">
                <div class="metric-item">
                  <span>總信號數</span>
                  <span>{{ backtestResults.summary.total_signals }}</span>
                </div>
                <div class="metric-item">
                  <span>獲利信號</span>
                  <span class="positive">{{ backtestResults.summary.winning_signals }}</span>
                </div>
                <div class="metric-item">
                  <span>虧損信號</span>
                  <span class="negative">{{ backtestResults.summary.losing_signals }}</span>
                </div>
                <div class="metric-item">
                  <span>勝率</span>
                  <span :class="getSuccessRateClass(backtestResults.summary.win_rate)">
                    {{ backtestResults.summary.win_rate }}%
                  </span>
                </div>
              </div>
            </div>

            <div class="metric-card">
              <h4>盈虧分析</h4>
              <div class="metric-list">
                <div class="metric-item">
                  <span>總收益</span>
                  <span :class="getProfitClass(backtestResults.summary.total_pnl)">
                    {{ backtestResults.summary.total_pnl > 0 ? '+' : '' }}{{ backtestResults.summary.total_pnl }}%
                  </span>
                </div>
                <div class="metric-item">
                  <span>平均收益</span>
                  <span :class="getProfitClass(backtestResults.summary.average_pnl)">
                    {{ backtestResults.summary.average_pnl > 0 ? '+' : '' }}{{ backtestResults.summary.average_pnl }}%
                  </span>
                </div>
                <div class="metric-item">
                  <span>最大獲利</span>
                  <span class="positive">+{{ backtestResults.summary.max_profit }}%</span>
                </div>
                <div class="metric-item">
                  <span>最大虧損</span>
                  <span class="negative">{{ backtestResults.summary.max_loss }}%</span>
                </div>
              </div>
            </div>

            <div class="metric-card">
              <h4>風險指標</h4>
              <div class="metric-list">
                <div class="metric-item">
                  <span>盈虧因子</span>
                  <span :class="getProfitFactorClass(backtestResults.summary.profit_factor)">
                    {{ backtestResults.summary.profit_factor }}x
                  </span>
                </div>
                <div class="metric-item">
                  <span>夏普比率</span>
                  <span :class="getSharpeClass(backtestResults.summary.sharpe_ratio)">
                    {{ backtestResults.summary.sharpe_ratio }}
                  </span>
                </div>
                <div class="metric-item">
                  <span>最大回撤</span>
                  <span class="negative">{{ backtestResults.summary.max_drawdown }}%</span>
                </div>
                <div class="metric-item">
                  <span>平均持倉時間</span>
                  <span>{{ backtestResults.summary.average_hold_time }}小時</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 各交易對表現 -->
        <div v-if="backtestResults.detailed_analysis.symbol_performance" class="symbol-performance">
          <h3>各交易對表現</h3>
          <div class="symbol-performance-grid">
            <div v-for="(perf, symbol) in backtestResults.detailed_analysis.symbol_performance" :key="symbol"
              class="symbol-perf-card">
              <div class="symbol-name">{{ symbol }}</div>
              <div class="symbol-metrics-mini">
                <div class="mini-metric">
                  <span>信號數</span>
                  <span>{{ perf.total_signals }}</span>
                </div>
                <div class="mini-metric">
                  <span>勝率</span>
                  <span :class="getSuccessRateClass(perf.win_rate)">{{ perf.win_rate }}%</span>
                </div>
                <div class="mini-metric">
                  <span>總收益</span>
                  <span :class="getProfitClass(perf.total_pnl)">
                    {{ perf.total_pnl > 0 ? '+' : '' }}{{ perf.total_pnl }}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 優化建議 -->
        <div v-if="backtestResults.optimization_suggestions" class="optimization-suggestions">
          <h3>策略優化建議</h3>
          <div class="suggestions-card">
            <div class="overall-assessment"
              :class="getAssessmentClass(backtestResults.optimization_suggestions.overall_assessment)">
              <i class="fas fa-clipboard-check"></i>
              <span>{{ backtestResults.optimization_suggestions.overall_assessment }}</span>
            </div>

            <div class="suggestions-grid">
              <div class="suggestion-section" v-if="backtestResults.optimization_suggestions.strengths.length > 0">
                <h4><i class="fas fa-thumbs-up"></i> 策略優勢</h4>
                <ul>
                  <li v-for="strength in backtestResults.optimization_suggestions.strengths" :key="strength">
                    {{ strength }}
                  </li>
                </ul>
              </div>

              <div class="suggestion-section" v-if="backtestResults.optimization_suggestions.weaknesses.length > 0">
                <h4><i class="fas fa-exclamation-triangle"></i> 需要改進</h4>
                <ul>
                  <li v-for="weakness in backtestResults.optimization_suggestions.weaknesses" :key="weakness">
                    {{ weakness }}
                  </li>
                </ul>
              </div>

              <div class="suggestion-section"
                v-if="backtestResults.optimization_suggestions.optimization_recommendations.length > 0">
                <h4><i class="fas fa-lightbulb"></i> 優化建議</h4>
                <ul>
                  <li v-for="rec in backtestResults.optimization_suggestions.optimization_recommendations" :key="rec">
                    {{ rec }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 原有的歷史記錄區塊 -->
    <div v-show="activeTab === 'history'">
      <!-- 總體統計概覽 -->
      <div class="stats-overview">
        <div class="stat-card total-signals">
          <div class="stat-icon">
            <i class="fas fa-signal"></i>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ overallStats.totalSignals }}</div>
            <div class="stat-label">總信號數</div>
          </div>
        </div>

        <div class="stat-card success-rate">
          <div class="stat-icon">
            <i class="fas fa-bullseye"></i>
          </div>
          <div class="stat-content">
            <div class="stat-number" :class="getSuccessRateClass(overallStats.successRate)">
              {{ overallStats.successRate }}%
            </div>
            <div class="stat-label">整體勝率</div>
          </div>
        </div>

        <div class="stat-card total-profit">
          <div class="stat-icon">
            <i class="fas fa-chart-line"></i>
          </div>
          <div class="stat-content">
            <div class="stat-number" :class="getProfitClass(overallStats.totalProfitPercent)">
              {{ overallStats.totalProfitPercent > 0 ? '+' : '' }}{{ overallStats.totalProfitPercent }}%
            </div>
            <div class="stat-label">累計收益</div>
          </div>
        </div>

        <div class="stat-card avg-profit">
          <div class="stat-icon">
            <i class="fas fa-percentage"></i>
          </div>
          <div class="stat-content">
            <div class="stat-number" :class="getProfitClass(overallStats.avgProfitPercent)">
              {{ overallStats.avgProfitPercent > 0 ? '+' : '' }}{{ overallStats.avgProfitPercent }}%
            </div>
            <div class="stat-label">平均收益</div>
          </div>
        </div>
      </div>

      <!-- 按幣種分組的詳細統計 -->
      <div class="symbol-analysis">
        <h2 class="section-title">
          <i class="fas fa-coins"></i>
          各幣種表現分析
        </h2>

        <div class="symbol-grid">
          <div v-for="symbolData in symbolStats" :key="symbolData.symbol" class="symbol-card">
            <div class="symbol-header">
              <div class="symbol-name">{{ symbolData.symbol }}</div>
              <div class="symbol-badge" :class="getPerformanceBadge(symbolData.successRate)">
                {{ getPerformanceText(symbolData.successRate) }}
              </div>
            </div>

            <div class="symbol-metrics">
              <div class="metric">
                <span class="metric-label">信號數</span>
                <span class="metric-value">{{ symbolData.totalSignals }}</span>
              </div>
              <div class="metric">
                <span class="metric-label">勝率</span>
                <span class="metric-value" :class="getSuccessRateClass(symbolData.successRate)">
                  {{ symbolData.successRate }}%
                </span>
              </div>
              <div class="metric">
                <span class="metric-label">累計收益</span>
                <span class="metric-value" :class="getProfitClass(symbolData.totalProfit)">
                  {{ symbolData.totalProfit > 0 ? '+' : '' }}{{ symbolData.totalProfit }}%
                </span>
              </div>
              <div class="metric">
                <span class="metric-label">平均收益</span>
                <span class="metric-value" :class="getProfitClass(symbolData.avgProfit)">
                  {{ symbolData.avgProfit > 0 ? '+' : '' }}{{ symbolData.avgProfit }}%
                </span>
              </div>
            </div>

            <div class="symbol-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: symbolData.successRate + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 詳細信號歷史表格 -->
      <div class="history-table-section">
        <h2 class="section-title">
          <i class="fas fa-table"></i>
          詳細信號記錄
        </h2>

        <div class="table-controls">
          <div class="filter-group">
            <select v-model="selectedSymbol" @change="filterSignals" class="symbol-filter">
              <option value="">所有幣種</option>
              <option v-for="symbol in availableSymbols" :key="symbol" :value="symbol">
                {{ symbol }}
              </option>
            </select>

            <select v-model="selectedStatus" @change="filterSignals" class="status-filter">
              <option value="">所有狀態</option>
              <option value="executed">已執行</option>
              <option value="expired">已過期</option>
              <option value="pending">待執行</option>
            </select>
          </div>

          <div class="pagination-info">
            顯示 {{ (currentPage - 1) * pageSize + 1 }}-{{ Math.min(currentPage * pageSize, filteredSignals.length) }} / 共
            {{ filteredSignals.length }} 條
          </div>
        </div>

        <div class="history-table">
          <table>
            <thead>
              <tr>
                <th>時間</th>
                <th>幣種</th>
                <th>策略</th>
                <th>類型</th>
                <th>入場價</th>
                <th>信心度</th>
                <th>狀態</th>
                <th>收益%</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="signal in paginatedSignals" :key="signal.signal_id" class="signal-row">
                <td class="time-cell">
                  <div class="time-main">{{ formatTime(signal.created_at) }}</div>
                  <div class="time-sub">{{ formatDate(signal.created_at) }}</div>
                </td>
                <td class="symbol-cell">
                  <div class="symbol-badge">{{ signal.symbol }}</div>
                </td>
                <td class="strategy-cell">{{ signal.strategy_name }}</td>
                <td class="type-cell">
                  <span class="type-badge" :class="signal.signal_type.toLowerCase()">
                    {{ signal.signal_type }}
                  </span>
                </td>
                <td class="price-cell">${{ signal.entry_price.toFixed(2) }}</td>
                <td class="confidence-cell">
                  <div class="confidence-bar">
                    <div class="confidence-fill" :style="{ width: (signal.confidence * 100) + '%' }"></div>
                    <span class="confidence-text">{{ (signal.confidence * 100).toFixed(0) }}%</span>
                  </div>
                </td>
                <td class="status-cell">
                  <span class="status-badge" :class="signal.status">
                    {{ getStatusText(signal.status) }}
                  </span>
                </td>
                <td class="profit-cell">
                  <span class="profit-value" :class="getProfitClass(signal.pnl_percentage)">
                    {{ signal.pnl_percentage > 0 ? '+' : '' }}{{ signal.pnl_percentage }}%
                  </span>
                </td>
                <td class="action-cell">
                  <button @click="viewSignalDetails(signal)" class="detail-btn">
                    <i class="fas fa-eye"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 分頁控制 -->
        <div class="pagination">
          <button @click="changePage(-1)" :disabled="currentPage <= 1" class="page-btn">
            <i class="fas fa-chevron-left"></i>
          </button>
          <span class="page-info">第 {{ currentPage }} / {{ totalPages }} 頁</span>
          <button @click="changePage(1)" :disabled="currentPage >= totalPages" class="page-btn">
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </div>

      <!-- 載入指示器 -->
      <div v-if="isLoading" class="loading-overlay">
        <div class="loading-spinner">
          <i class="fas fa-spinner fa-spin"></i>
          <span>載入歷史數據中...</span>
        </div>
      </div>

    </div> <!-- 關閉歷史記錄區塊 -->
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'

// 響應式數據
const isLoading = ref(false)
const selectedTimeRange = ref('24')
const selectedPrecisionLevel = ref('high')
const selectedSymbol = ref('')
const selectedStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

// 🎯 新增：回測相關數據
const activeTab = ref('history')
const backtestPeriod = ref('30d')
const includeOptimization = ref(true)
const backtestLoading = ref(false)
const quickStats = ref(null)
const backtestResults = ref(null)

// 統計數據
const overallStats = ref({
  totalSignals: 0,
  successRate: 0,
  totalProfitPercent: 0,
  avgProfitPercent: 0
})

const symbolStats = ref([])
const allSignals = ref([])

// 計算屬性
const availableSymbols = computed(() => {
  const symbols = new Set(allSignals.value.map(s => s.symbol))
  return Array.from(symbols).sort()
})

const filteredSignals = computed(() => {
  let filtered = allSignals.value

  if (selectedSymbol.value) {
    filtered = filtered.filter(s => s.symbol === selectedSymbol.value)
  }

  if (selectedStatus.value) {
    filtered = filtered.filter(s => s.status === selectedStatus.value)
  }

  return filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
})

const totalPages = computed(() => {
  return Math.ceil(filteredSignals.value.length / pageSize.value)
})

const paginatedSignals = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredSignals.value.slice(start, end)
})

// 生命週期
onMounted(() => {
  fetchHistoryData()
})

// 方法
async function fetchHistoryData() {
  isLoading.value = true
  try {
    const symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT', 'XRPUSDT', 'DOGEUSDT']
    const hours = parseInt(selectedTimeRange.value)

    const promises = symbols.map(symbol =>
      fetch(`/api/v1/sniper/history/signals?symbol=${symbol}&limit=100&skip=0`)
        .then(res => res.json())
    )

    const results = await Promise.all(promises)

    // 彙總所有信號
    let allHistorySignals = []
    let symbolStatsTemp = []

    results.forEach(result => {
      if (result.status === 'success') {
        const symbolData = result.data
        allHistorySignals.push(...symbolData.signals)

        symbolStatsTemp.push({
          symbol: symbolData.symbol,
          totalSignals: symbolData.statistics.total_signals,
          successRate: symbolData.statistics.success_rate,
          totalProfit: parseFloat((symbolData.statistics.average_pnl * symbolData.statistics.executed_signals).toFixed(2)),
          avgProfit: symbolData.statistics.average_pnl
        })
      }
    })

    allSignals.value = allHistorySignals
    symbolStats.value = symbolStatsTemp.sort((a, b) => b.successRate - a.successRate)

    // 計算總體統計
    const totalSignals = allHistorySignals.length
    const executedSignals = allHistorySignals.filter(s => s.status === 'executed')
    const profitSignals = executedSignals.filter(s => s.result === 'profit')

    overallStats.value = {
      totalSignals,
      successRate: executedSignals.length > 0 ? parseFloat((profitSignals.length / executedSignals.length * 100).toFixed(1)) : 0,
      totalProfitPercent: parseFloat(executedSignals.reduce((sum, s) => sum + s.pnl_percentage, 0).toFixed(2)),
      avgProfitPercent: executedSignals.length > 0 ? parseFloat((executedSignals.reduce((sum, s) => sum + s.pnl_percentage, 0) / executedSignals.length).toFixed(2)) : 0
    }

  } catch (error) {
    console.error('獲取歷史數據失敗:', error)
  } finally {
    isLoading.value = false
  }
}

function refreshData() {
  fetchHistoryData()
}

function filterSignals() {
  currentPage.value = 1
}

function changePage(direction) {
  const newPage = currentPage.value + direction
  if (newPage >= 1 && newPage <= totalPages.value) {
    currentPage.value = newPage
  }
}

function viewSignalDetails(signal) {
  alert(`信號詳情:\n\n` +
    `幣種: ${signal.symbol}\n` +
    `策略: ${signal.strategy_name}\n` +
    `類型: ${signal.signal_type}\n` +
    `入場價: $${signal.entry_price}\n` +
    `信心度: ${(signal.confidence * 100).toFixed(0)}%\n` +
    `狀態: ${getStatusText(signal.status)}\n` +
    `收益: ${signal.pnl_percentage}%\n` +
    `時間: ${formatTime(signal.created_at)} ${formatDate(signal.created_at)}`)
}

// 輔助方法
function getSuccessRateClass(rate) {
  if (rate >= 70) return 'excellent'
  if (rate >= 50) return 'good'
  if (rate >= 30) return 'fair'
  return 'poor'
}

function getProfitClass(profit) {
  if (profit > 0) return 'profit'
  if (profit < 0) return 'loss'
  return 'neutral'
}

function getPerformanceBadge(rate) {
  if (rate >= 70) return 'excellent'
  if (rate >= 50) return 'good'
  return 'poor'
}

function getPerformanceText(rate) {
  if (rate >= 70) return '優秀'
  if (rate >= 50) return '良好'
  return '需改進'
}

function getStatusText(status) {
  const statusMap = {
    'executed': '已執行',
    'expired': '已過期',
    'pending': '待執行'
  }
  return statusMap[status] || status
}

function formatTime(timeStr) {
  // 處理時區問題 - 確保顯示台灣時間
  const date = new Date(timeStr)
  return date.toLocaleTimeString('zh-TW', {
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'Asia/Taipei'
  })
}

function formatDate(timeStr) {
  // 處理時區問題 - 確保顯示台灣時間  
  const date = new Date(timeStr)
  return date.toLocaleDateString('zh-TW', {
    month: '2-digit',
    day: '2-digit',
    timeZone: 'Asia/Taipei'
  })
}

// 🎯 新增：回測相關方法
async function runBacktest() {
  backtestLoading.value = true
  backtestResults.value = null
  quickStats.value = null

  try {
    // 1. 先獲取快速統計
    const quickStatsResponse = await fetch(`/api/v1/sniper/backtest/stats?period=${backtestPeriod.value}`)
    if (quickStatsResponse.ok) {
      const quickStatsData = await quickStatsResponse.json()
      if (quickStatsData.status === 'success') {
        quickStats.value = quickStatsData.data
      }
    }

    // 2. 執行詳細回測
    const backtestResponse = await fetch('/api/v1/sniper/backtest/run', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        period: backtestPeriod.value,
        include_optimization: includeOptimization.value
      })
    })

    if (!backtestResponse.ok) {
      throw new Error(`HTTP error! status: ${backtestResponse.status}`)
    }

    const backtestData = await backtestResponse.json()
    if (backtestData.status === 'success') {
      backtestResults.value = backtestData.data
    } else {
      throw new Error(backtestData.message || '回測執行失敗')
    }

  } catch (error) {
    console.error('回測執行錯誤:', error)
    alert(`回測執行失敗: ${error.message}`)
  } finally {
    backtestLoading.value = false
  }
}

function getProfitFactorClass(factor) {
  if (factor >= 2.0) return 'excellent'
  if (factor >= 1.5) return 'good'
  if (factor >= 1.0) return 'fair'
  return 'poor'
}

function getSharpeClass(ratio) {
  if (ratio >= 2.0) return 'excellent'
  if (ratio >= 1.0) return 'good'
  if (ratio >= 0.5) return 'fair'
  return 'poor'
}

function getPerformanceGradeClass(grade) {
  const gradeMap = {
    'A+': 'grade-aplus',
    'A': 'grade-a',
    'B+': 'grade-bplus',
    'B': 'grade-b',
    'C+': 'grade-cplus',
    'C': 'grade-c',
    'D': 'grade-d',
    'F': 'grade-f'
  }
  return gradeMap[grade] || 'grade-unknown'
}

function getAssessmentClass(assessment) {
  if (!assessment) return 'assessment-unknown'

  const lowerAssessment = assessment.toLowerCase()
  if (lowerAssessment.includes('優秀') || lowerAssessment.includes('excellent')) return 'assessment-excellent'
  if (lowerAssessment.includes('良好') || lowerAssessment.includes('good')) return 'assessment-good'
  if (lowerAssessment.includes('普通') || lowerAssessment.includes('fair')) return 'assessment-fair'
  if (lowerAssessment.includes('需要改進') || lowerAssessment.includes('poor')) return 'assessment-poor'
  return 'assessment-neutral'
}
</script>

<style scoped>
.signal-history-page {
  padding: 24px;
  background: linear-gradient(135deg, #000000 0%, #191919 50%, #000000 100%);
  min-height: 100vh;
  color: white;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.page-title {
  font-size: 2rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 16px;
  color: white;
}

.control-panel {
  display: flex;
  gap: 16px;
  align-items: center;
}

.time-selector,
.precision-selector {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-weight: 500;
}

.refresh-btn {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.spinning {
  animation: spin 1s linear infinite;
}

/* 統計概覽 */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-icon {
  width: 60px;
  height: 60px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.8;
}

.excellent {
  color: #00ff88;
}

.good {
  color: #ffd700;
}

.fair {
  color: #ff9500;
}

.poor {
  color: #ff453a;
}

.profit {
  color: #00ff88;
}

.loss {
  color: #ff453a;
}

.neutral {
  color: #888;
}

/* 幣種分析 */
.symbol-analysis {
  margin-bottom: 32px;
}

.section-title {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.symbol-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.symbol-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.symbol-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.symbol-name {
  font-size: 1.2rem;
  font-weight: bold;
}

.symbol-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.symbol-badge.excellent {
  background: rgba(0, 255, 136, 0.2);
  color: #00ff88;
}

.symbol-badge.good {
  background: rgba(255, 215, 0, 0.2);
  color: #ffd700;
}

.symbol-badge.poor {
  background: rgba(255, 69, 58, 0.2);
  color: #ff453a;
}

.symbol-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
}

.metric {
  display: flex;
  justify-content: space-between;
}

.metric-label {
  font-size: 14px;
  opacity: 0.8;
}

.metric-value {
  font-weight: 600;
}

.symbol-progress {
  margin-top: 12px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #ff453a 0%, #ffd700 50%, #00ff88 100%);
  border-radius: 3px;
  transition: width 0.5s ease;
}

/* 歷史表格 */
.history-table-section {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 24px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.table-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-group {
  display: flex;
  gap: 12px;
}

.symbol-filter,
.status-filter {
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.pagination-info {
  font-size: 14px;
  opacity: 0.8;
}

.history-table {
  overflow-x: auto;
  margin-bottom: 20px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  padding: 12px;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
}

td {
  padding: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.signal-row:hover {
  background: rgba(255, 255, 255, 0.05);
}

.time-cell .time-main {
  font-weight: 600;
}

.time-cell .time-sub {
  font-size: 12px;
  opacity: 0.7;
}

.symbol-badge {
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.type-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.type-badge.buy {
  background: rgba(0, 255, 136, 0.2);
  color: #00ff88;
}

.type-badge.sell {
  background: rgba(255, 69, 58, 0.2);
  color: #ff453a;
}

.confidence-bar {
  position: relative;
  width: 60px;
  height: 16px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(90deg, #ff453a 0%, #ffd700 50%, #00ff88 100%);
  border-radius: 8px;
}

.confidence-text {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 500;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.executed {
  background: rgba(0, 255, 136, 0.2);
  color: #00ff88;
}

.status-badge.expired {
  background: rgba(255, 152, 0, 0.2);
  color: #ff9500;
}

.status-badge.pending {
  background: rgba(255, 215, 0, 0.2);
  color: #ffd700;
}

.detail-btn {
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.detail-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* 分頁 */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.page-btn {
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-weight: 500;
}

/* 載入動畫 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: white;
  font-size: 18px;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

/* 響應式設計 */
@media (max-width: 768px) {
  .signal-history-page {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .stats-overview {
    grid-template-columns: 1fr;
  }

  .symbol-grid {
    grid-template-columns: 1fr;
  }

  .table-controls {
    flex-direction: column;
    gap: 12px;
  }

  .history-table {
    font-size: 14px;
  }
}

/* 🎯 新增：回測相關樣式 */
.tab-navigation {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.tab-btn {
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.tab-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.tab-btn.active {
  background: linear-gradient(135deg, #00d4aa 0%, #00a885 100%);
  box-shadow: 0 4px 15px rgba(0, 212, 170, 0.3);
}

.backtest-section {
  animation: fadeIn 0.3s ease-in-out;
}

.backtest-controls {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.controls-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  align-items: end;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.control-group label {
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.period-selector {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-weight: 500;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  margin-left: 8px;
}

.run-backtest-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
}

.run-backtest-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 123, 255, 0.4);
}

.run-backtest-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.quick-stats {
  margin-bottom: 32px;
}

.quick-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.quick-stat-card {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.quick-stat-card:hover {
  background: rgba(255, 255, 255, 0.12);
  transform: translateY(-2px);
}

.quick-stat-card .stat-icon {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.quick-stat-card .stat-content {
  flex: 1;
}

.quick-stat-card .stat-number {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 4px;
}

.quick-stat-card .stat-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.performance-grade.grade-aplus,
.performance-grade.grade-a {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
}

.performance-grade.grade-bplus,
.performance-grade.grade-b {
  background: linear-gradient(135deg, #17a2b8 0%, #007bff 100%);
}

.performance-grade.grade-cplus,
.performance-grade.grade-c {
  background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);
}

.performance-grade.grade-d,
.performance-grade.grade-f {
  background: linear-gradient(135deg, #dc3545 0%, #e83e8c 100%);
}

.backtest-results {
  animation: slideInUp 0.5s ease-out;
}

.core-metrics {
  margin-bottom: 32px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.metric-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.metric-card h4 {
  margin-bottom: 16px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.1rem;
}

.metric-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.metric-item:last-child {
  border-bottom: none;
}

.symbol-performance {
  margin-bottom: 32px;
}

.symbol-performance-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.symbol-perf-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.symbol-name {
  font-weight: bold;
  font-size: 1.1rem;
  margin-bottom: 12px;
  color: #00d4aa;
}

.symbol-metrics-mini {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.mini-metric {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mini-metric span:first-child {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.mini-metric span:last-child {
  font-weight: 600;
}

.optimization-suggestions {
  margin-top: 32px;
}

.suggestions-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.overall-assessment {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 24px;
  font-weight: 600;
  font-size: 1.1rem;
}

.assessment-excellent {
  background: linear-gradient(135deg, rgba(40, 167, 69, 0.2) 0%, rgba(32, 201, 151, 0.2) 100%);
  border: 1px solid rgba(40, 167, 69, 0.3);
  color: #28a745;
}

.assessment-good {
  background: linear-gradient(135deg, rgba(23, 162, 184, 0.2) 0%, rgba(0, 123, 255, 0.2) 100%);
  border: 1px solid rgba(23, 162, 184, 0.3);
  color: #17a2b8;
}

.assessment-fair {
  background: linear-gradient(135deg, rgba(255, 193, 7, 0.2) 0%, rgba(253, 126, 20, 0.2) 100%);
  border: 1px solid rgba(255, 193, 7, 0.3);
  color: #ffc107;
}

.assessment-poor {
  background: linear-gradient(135deg, rgba(220, 53, 69, 0.2) 0%, rgba(232, 62, 140, 0.2) 100%);
  border: 1px solid rgba(220, 53, 69, 0.3);
  color: #dc3545;
}

.suggestions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.suggestion-section {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.suggestion-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  color: rgba(255, 255, 255, 0.9);
}

.suggestion-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.suggestion-section li {
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.5;
}

.suggestion-section li:last-child {
  border-bottom: none;
}

/* 動畫效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 響應式調整 - 回測部分 */
@media (max-width: 768px) {
  .tab-navigation {
    flex-direction: column;
  }

  .controls-grid {
    grid-template-columns: 1fr;
  }

  .quick-stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .symbol-performance-grid {
    grid-template-columns: 1fr;
  }

  .suggestions-grid {
    grid-template-columns: 1fr;
  }
}
</style>
