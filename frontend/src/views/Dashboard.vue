<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">交易儀表板</h1>
      <p class="text-gray-600">監控您的交易策略和市場表現</p>
    </div>

    <!-- 概覽卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-2 bg-green-100 rounded-lg">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">活躍信號</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.activeSignals }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-2 bg-blue-100 rounded-lg">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">今日信號</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.todaySignals }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-2 bg-yellow-100 rounded-lg">
            <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">平均置信度</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.avgConfidence }}%</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-2 bg-purple-100 rounded-lg">
            <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">風險回報比</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.avgRiskReward }}:1</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 最新信號 -->
    <div class="bg-white rounded-lg shadow mb-8">
      <div class="px-6 py-4 border-b border-gray-200">
        <h2 class="text-lg font-semibold text-gray-900">最新交易信號</h2>
      </div>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">交易對</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">方向</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">進場價格</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">止損</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">止盈</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">風險回報比</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">置信度</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="signal in latestSignals" :key="signal.id">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ signal.symbol }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                      :class="signal.signal_type === 'LONG' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                  {{ signal.signal_type }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${{ signal.entry_price?.toFixed(2) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${{ signal.stop_loss?.toFixed(2) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${{ signal.take_profit?.toFixed(2) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ signal.risk_reward_ratio?.toFixed(1) }}:1</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ (signal.confidence * 100).toFixed(0) }}%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">快速分析</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">交易對</label>
            <select v-model="quickAnalysis.symbol" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="BTC/USDT">BTC/USDT</option>
              <option value="ETH/USDT">ETH/USDT</option>
              <option value="BNB/USDT">BNB/USDT</option>
                <option value="XRP/USDT">XRP/USDT</option>
                <option value="ADA/USDT">ADA/USDT</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">時間框架</label>
            <select v-model="quickAnalysis.timeframe" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="5m">5分鐘</option>
              <option value="15m">15分鐘</option>
              <option value="1h">1小時</option>
              <option value="4h">4小時</option>
              <option value="1d">1天</option>
            </select>
          </div>
          <button @click="analyzeSymbol" class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500">
            立即分析
          </button>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">系統狀態</h3>
        <div class="space-y-3">
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">市場數據服務</span>
            <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">運行中</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">策略引擎</span>
            <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">運行中</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">回測服務</span>
            <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">運行中</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">資料庫連接</span>
            <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">正常</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'

interface Signal {
  id: number
  symbol: string
  signal_type: string
  entry_price?: number
  stop_loss?: number
  take_profit?: number
  risk_reward_ratio?: number
  confidence: number
}

const stats = reactive({
  activeSignals: 0,
  todaySignals: 0,
  avgConfidence: 0,
  avgRiskReward: 0
})

const latestSignals = ref<Signal[]>([])

const quickAnalysis = reactive({
  symbol: 'BTC/USDT',
  timeframe: '1h'
})

const fetchDashboardData = async () => {
  try {
    // 獲取最新信號
    const signalsResponse = await axios.get('/api/v1/signals/latest?hours=24')
    latestSignals.value = signalsResponse.data.slice(0, 10)
    
    // 計算統計數據
    stats.activeSignals = latestSignals.value.length
    stats.todaySignals = latestSignals.value.length
    
    if (latestSignals.value.length > 0) {
      stats.avgConfidence = Math.round(
        latestSignals.value.reduce((sum, signal) => sum + signal.confidence * 100, 0) / latestSignals.value.length
      )
      
      const validRRSignals = latestSignals.value.filter(s => s.risk_reward_ratio)
      if (validRRSignals.length > 0) {
        stats.avgRiskReward = Number(
          (validRRSignals.reduce((sum, signal) => sum + (signal.risk_reward_ratio || 0), 0) / validRRSignals.length).toFixed(1)
        )
      }
    }
  } catch (error) {
    console.error('獲取儀表板數據失敗:', error)
  }
}

const analyzeSymbol = async () => {
  try {
    const response = await axios.post('/api/v1/signals/analyze', {
      symbol: quickAnalysis.symbol,
      timeframe: quickAnalysis.timeframe
    })
    
    if (response.data.success) {
      alert(`分析完成：${response.data.message}`)
      // 重新獲取數據
      await fetchDashboardData()
    }
  } catch (error) {
    console.error('分析失敗:', error)
    alert('分析失敗，請檢查服務狀態')
  }
}

onMounted(() => {
  fetchDashboardData()
})
</script>
