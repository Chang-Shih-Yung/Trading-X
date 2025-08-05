<template>
  <div class="p-6 space-y-6">
    <!-- 頁面標題與操作 -->
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-3xl font-bold text-white">信號管理</h2>
        <p class="text-gray-400 mt-1">管理和監控交易信號品質控制流程</p>
      </div>
      
      <div class="flex items-center space-x-3">
        <button 
          @click="signalStore.testSignal()"
          class="btn-secondary"
        >
          <TestTube class="h-4 w-4 mr-2" />
          測試信號
        </button>
        
        <button 
          @click="refreshSignals"
          :disabled="signalStore.loading"
          class="btn-primary"
        >
          <RefreshCw :class="['h-4 w-4 mr-2', signalStore.loading && 'animate-spin']" />
          刷新
        </button>
      </div>
    </div>

    <!-- 信號統計卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="metric-card text-center">
        <div class="text-3xl font-bold text-red-500">{{ signalStore.criticalSignals.length }}</div>
        <div class="text-gray-300 text-sm">🚨 緊急信號</div>
      </div>
      
      <div class="metric-card text-center">
        <div class="text-3xl font-bold text-orange-500">{{ signalStore.highSignals.length }}</div>
        <div class="text-gray-300 text-sm">🎯 高品質信號</div>
      </div>
      
      <div class="metric-card text-center">
        <div class="text-3xl font-bold text-blue-500">{{ signalStore.activeSignals.length }}</div>
        <div class="text-gray-300 text-sm">✅ 活躍信號</div>
      </div>
      
      <div class="metric-card text-center">
        <div class="text-3xl font-bold text-green-500">{{ signalStore.statistics.success_rate }}%</div>
        <div class="text-gray-300 text-sm">📈 成功率</div>
      </div>
    </div>

    <!-- 信號處理器 -->
    <div class="bg-trading-secondary rounded-lg border border-gray-700 p-6">
      <h3 class="text-xl font-semibold mb-4 flex items-center">
        <Plus class="h-6 w-6 mr-2 text-green-500" />
        新增信號處理
      </h3>
      
      <form @submit.prevent="processNewSignal" class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">交易對</label>
          <select v-model="newSignal.symbol" class="w-full bg-trading-accent border border-gray-600 rounded-lg px-3 py-2 text-white">
            <option value="BTCUSDT">BTCUSDT</option>
            <option value="ETHUSDT">ETHUSDT</option>
            <option value="ADAUSDT">ADAUSDT</option>
            <option value="DOTUSDT">DOTUSDT</option>
            <option value="LINKUSDT">LINKUSDT</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">信號方向</label>
          <select v-model="newSignal.signal_type" class="w-full bg-trading-accent border border-gray-600 rounded-lg px-3 py-2 text-white">
            <option value="BUY">📈 做多 (BUY)</option>
            <option value="SELL">📉 做空 (SELL)</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">信心度 (%)</label>
          <input 
            v-model.number="newSignal.confidence" 
            type="number" 
            min="0" 
            max="100" 
            step="0.1"
            class="w-full bg-trading-accent border border-gray-600 rounded-lg px-3 py-2 text-white"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">進場價格</label>
          <input 
            v-model.number="newSignal.entry_price" 
            type="number" 
            step="0.01"
            class="w-full bg-trading-accent border border-gray-600 rounded-lg px-3 py-2 text-white"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">止損價格</label>
          <input 
            v-model.number="newSignal.stop_loss" 
            type="number" 
            step="0.01"
            class="w-full bg-trading-accent border border-gray-600 rounded-lg px-3 py-2 text-white"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">止盈價格</label>
          <input 
            v-model.number="newSignal.take_profit" 
            type="number" 
            step="0.01"
            class="w-full bg-trading-accent border border-gray-600 rounded-lg px-3 py-2 text-white"
          />
        </div>
        
        <div class="md:col-span-3">
          <label class="block text-sm font-medium text-gray-300 mb-2">分析原因</label>
          <textarea 
            v-model="newSignal.reasoning" 
            rows="2"
            class="w-full bg-trading-accent border border-gray-600 rounded-lg px-3 py-2 text-white"
            placeholder="例如：狙擊手雙層架構確認 + RSI黃金交叉"
          ></textarea>
        </div>
        
        <div class="md:col-span-3">
          <button 
            type="submit" 
            :disabled="processing"
            class="btn-primary w-full"
          >
            <Send :class="['h-4 w-4 mr-2', processing && 'animate-pulse']" />
            {{ processing ? '處理中...' : '提交信號處理' }}
          </button>
        </div>
      </form>
    </div>

    <!-- 信號列表 -->
    <div class="bg-trading-secondary rounded-lg border border-gray-700">
      <div class="p-6 border-b border-gray-700">
        <div class="flex justify-between items-center">
          <h3 class="text-xl font-semibold flex items-center">
            <List class="h-6 w-6 mr-2 text-blue-500" />
            信號列表
          </h3>
          
          <div class="flex items-center space-x-4">
            <!-- 優先級篩選 -->
            <select v-model="priorityFilter" class="bg-trading-accent border border-gray-600 rounded-lg px-3 py-1 text-sm text-white">
              <option value="">全部優先級</option>
              <option value="CRITICAL">🚨 緊急</option>
              <option value="HIGH">🎯 高品質</option>
              <option value="MEDIUM">📊 標準</option>
              <option value="LOW">📈 參考</option>
            </select>
            
            <!-- 清除按鈕 -->
            <button 
              @click="signalStore.clearSignals()"
              class="btn-danger text-sm"
            >
              <Trash2 class="h-4 w-4 mr-1" />
              清除全部
            </button>
          </div>
        </div>
      </div>
      
      <div class="max-h-96 overflow-y-auto">
        <div v-if="signalStore.loading" class="p-8 text-center text-gray-400">
          <RefreshCw class="h-8 w-8 animate-spin mx-auto mb-4" />
          載入信號數據...
        </div>
        
        <div v-else-if="filteredSignals.length === 0" class="p-8 text-center text-gray-400">
          <Target class="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>暫無信號數據</p>
          <button @click="signalStore.testSignal()" class="btn-secondary mt-4 text-sm">
            生成測試信號
          </button>
        </div>
        
        <div v-else class="divide-y divide-gray-700">
          <div 
            v-for="signal in filteredSignals" 
            :key="signal.id"
            class="p-4 hover:bg-trading-accent hover:bg-opacity-50 transition-colors duration-200"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center mb-2">
                  <div 
                    :class="[
                      'status-indicator',
                      getPriorityColor(signal.priority)
                    ]"
                  ></div>
                  
                  <span class="font-semibold text-lg mr-3">{{ signal.symbol }}</span>
                  
                  <span 
                    :class="[
                      'px-2 py-1 rounded-full text-xs font-medium',
                      signal.signal_type === 'BUY' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
                    ]"
                  >
                    {{ signal.signal_type === 'BUY' ? '📈 做多' : '📉 做空' }}
                  </span>
                  
                  <span 
                    :class="[
                      'ml-2 px-2 py-1 rounded-full text-xs font-medium',
                      getPriorityBadgeClass(signal.priority)
                    ]"
                  >
                    {{ getPriorityLabel(signal.priority) }}
                  </span>
                </div>
                
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span class="text-gray-400">信心度:</span>
                    <span class="ml-1 font-semibold">{{ (signal.confidence * 100).toFixed(1) }}%</span>
                  </div>
                  <div>
                    <span class="text-gray-400">進場:</span>
                    <span class="ml-1 font-semibold">${{ signal.entry_price?.toLocaleString() }}</span>
                  </div>
                  <div>
                    <span class="text-gray-400">止損:</span>
                    <span class="ml-1 font-semibold text-red-400">${{ signal.stop_loss?.toLocaleString() }}</span>
                  </div>
                  <div>
                    <span class="text-gray-400">止盈:</span>
                    <span class="ml-1 font-semibold text-green-400">${{ signal.take_profit?.toLocaleString() }}</span>
                  </div>
                </div>
                
                <div v-if="signal.reasoning" class="mt-2 text-sm text-gray-300">
                  <span class="text-gray-400">分析:</span> {{ signal.reasoning }}
                </div>
              </div>
              
              <div class="text-right text-xs text-gray-400 ml-4">
                <div>{{ formatTime(signal.timestamp) }}</div>
                <div v-if="signal.epl_decision" class="mt-1">
                  EPL: {{ signal.epl_decision }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { useSignalStore } from '@/stores/signals'
import { 
  Plus, 
  RefreshCw, 
  Send, 
  List, 
  Target, 
  TestTube, 
  Trash2
} from 'lucide-vue-next'

const signalStore = useSignalStore()

// 新信號表單
const newSignal = reactive({
  symbol: 'BTCUSDT',
  signal_type: 'BUY',
  confidence: 85.0,
  entry_price: 95847.23,
  stop_loss: 92450.00,
  take_profit: 102339.00,
  reasoning: '狙擊手雙層架構確認 + RSI黃金交叉'
})

const processing = ref(false)
const priorityFilter = ref('')

// 篩選後的信號
const filteredSignals = computed(() => {
  let signals = [...signalStore.signals]
  
  if (priorityFilter.value) {
    signals = signals.filter(signal => signal.priority === priorityFilter.value)
  }
  
  return signals.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
})

// 處理新信號
async function processNewSignal() {
  if (processing.value) return
  
  processing.value = true
  try {
    // 計算品質分數和風險報酬比
    const qualityScore = newSignal.confidence
    const riskRewardRatio = Math.abs((newSignal.take_profit - newSignal.entry_price) / (newSignal.entry_price - newSignal.stop_loss))
    
    const signalData = {
      ...newSignal,
      confidence: newSignal.confidence / 100, // 轉換為小數
      quality_score: qualityScore,
      risk_reward_ratio: riskRewardRatio,
      source: 'manual',
      timeframe: '15m',
      indicators_used: ['Manual Input']
    }
    
    await signalStore.processSignal(signalData)
    
    // 重置表單（保留一些預設值）
    Object.assign(newSignal, {
      confidence: 85.0,
      entry_price: 0,
      stop_loss: 0,
      take_profit: 0,
      reasoning: ''
    })
    
  } catch (error) {
    console.error('處理信號失敗:', error)
  } finally {
    processing.value = false
  }
}

// 刷新信號列表
async function refreshSignals() {
  await signalStore.fetchSignals()
}

// 格式化時間
function formatTime(timestamp) {
  return new Date(timestamp).toLocaleString('zh-TW', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 獲取優先級標籤
function getPriorityLabel(priority) {
  const labels = {
    CRITICAL: '緊急',
    HIGH: '高品質',
    MEDIUM: '標準',
    LOW: '參考',
    REJECTED: '已拒絕'
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

// 獲取優先級徽章樣式
function getPriorityBadgeClass(priority) {
  const classes = {
    CRITICAL: 'bg-red-600 text-white',
    HIGH: 'bg-orange-600 text-white',
    MEDIUM: 'bg-blue-600 text-white',
    LOW: 'bg-gray-600 text-white',
    REJECTED: 'bg-gray-800 text-gray-400'
  }
  return classes[priority] || 'bg-gray-600 text-white'
}
</script>
