<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">交易信號</h1>
      <p class="text-gray-600">實時監控和管理交易信號</p>
    </div>

    <!-- 篩選器 -->
    <div class="bg-white rounded-lg shadow mb-6 p-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">交易對</label>
          <select v-model="filters.symbol" class="w-full px-3 py-2 border border-gray-300 rounded-md">
            <option value="">全部</option>
            <option value="BTC/USDT">BTC/USDT</option>
            <option value="ETH/USDT">ETH/USDT</option>
            <option value="BNB/USDT">BNB/USDT</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">信號類型</label>
          <select v-model="filters.signalType" class="w-full px-3 py-2 border border-gray-300 rounded-md">
            <option value="">全部</option>
            <option value="LONG">做多</option>
            <option value="SHORT">做空</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">最低置信度</label>
          <input v-model="filters.minConfidence" type="number" min="0" max="1" step="0.1" 
                 class="w-full px-3 py-2 border border-gray-300 rounded-md">
        </div>
        <div class="flex items-end">
          <button @click="fetchSignals" class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700">
            篩選
          </button>
        </div>
      </div>
    </div>

    <!-- 信號列表 -->
    <div class="bg-white rounded-lg shadow">
      <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
        <h2 class="text-lg font-semibold text-gray-900">交易信號列表</h2>
        <button @click="fetchSignals" class="bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700">
          刷新
        </button>
      </div>
      
      <div v-if="loading" class="p-8 text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-2 text-gray-600">載入中...</p>
      </div>

      <div v-else-if="signals.length === 0" class="p-8 text-center text-gray-500">
        暫無信號數據
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">交易對</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">時間框架</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">方向</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">進場價格</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">止損</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">止盈</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">風險回報比</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">置信度</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">信號強度</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">創建時間</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="signal in signals" :key="signal.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ signal.symbol }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ signal.timeframe }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                      :class="getSignalTypeClass(signal.signal_type)">
                  {{ signal.signal_type }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${{ signal.entry_price?.toFixed(2) || 'N/A' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${{ signal.stop_loss?.toFixed(2) || 'N/A' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${{ signal.take_profit?.toFixed(2) || 'N/A' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ signal.risk_reward_ratio?.toFixed(1) || 'N/A' }}:1
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                    <div class="bg-blue-600 h-2 rounded-full" 
                         :style="`width: ${signal.confidence * 100}%`"></div>
                  </div>
                  <span class="text-sm text-gray-900">{{ (signal.confidence * 100).toFixed(0) }}%</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                    <div class="bg-green-600 h-2 rounded-full" 
                         :style="`width: ${signal.signal_strength}%`"></div>
                  </div>
                  <span class="text-sm text-gray-900">{{ signal.signal_strength.toFixed(0) }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(signal.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button @click="viewSignalDetails(signal)" 
                        class="text-blue-600 hover:text-blue-900 mr-2">
                  詳情
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 信號詳情彈窗 -->
    <div v-if="selectedSignal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-900">信號詳情</h3>
          <button @click="selectedSignal = null" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <div class="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">交易對</label>
            <p class="text-lg font-semibold">{{ selectedSignal.symbol }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">信號方向</label>
            <span class="inline-flex px-2 py-1 text-sm font-semibold rounded-full"
                  :class="getSignalTypeClass(selectedSignal.signal_type)">
              {{ selectedSignal.signal_type }}
            </span>
          </div>
        </div>

        <div v-if="selectedSignal.reasoning" class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">信號理由</label>
          <p class="text-sm text-gray-900 bg-gray-50 p-3 rounded">{{ selectedSignal.reasoning }}</p>
        </div>

        <div v-if="selectedSignal.indicators_used" class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">使用的指標</label>
          <div class="flex flex-wrap gap-2">
            <span v-for="(signal, indicator) in selectedSignal.indicators_used" 
                  :key="indicator"
                  class="px-2 py-1 text-xs rounded-full"
                  :class="getIndicatorClass(signal)">
              {{ indicator }}: {{ signal }}
            </span>
          </div>
        </div>

        <div class="flex justify-end">
          <button @click="selectedSignal = null" 
                  class="bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400">
            關閉
          </button>
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
  timeframe: string
  signal_type: string
  entry_price?: number
  stop_loss?: number
  take_profit?: number
  risk_reward_ratio?: number
  confidence: number
  signal_strength: number
  reasoning?: string
  indicators_used?: Record<string, string>
  created_at: string
}

const signals = ref<Signal[]>([])
const loading = ref(false)
const selectedSignal = ref<Signal | null>(null)

const filters = reactive({
  symbol: '',
  signalType: '',
  minConfidence: 0.7
})

const fetchSignals = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (filters.symbol) params.append('symbol', filters.symbol)
    if (filters.signalType) params.append('signal_type', filters.signalType)
    if (filters.minConfidence) params.append('min_confidence', filters.minConfidence.toString())
    
    const response = await axios.get(`/api/v1/signals?${params.toString()}`)
    signals.value = response.data
  } catch (error) {
    console.error('獲取信號失敗:', error)
  } finally {
    loading.value = false
  }
}

const getSignalTypeClass = (signalType: string) => {
  return signalType === 'LONG' 
    ? 'bg-green-100 text-green-800' 
    : 'bg-red-100 text-red-800'
}

const getIndicatorClass = (signal: string) => {
  switch (signal) {
    case 'BUY':
      return 'bg-green-100 text-green-800'
    case 'SELL':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-TW')
}

const viewSignalDetails = (signal: Signal) => {
  selectedSignal.value = signal
}

onMounted(() => {
  fetchSignals()
})
</script>
