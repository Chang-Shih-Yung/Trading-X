import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useSignalStore = defineStore('signals', () => {
  // 狀態
  const signals = ref([])
  const loading = ref(false)
  const error = ref(null)
  const lastUpdate = ref(null)
  
  // 信號統計
  const statistics = ref({
    total_signals: 0,
    epl_passed: 0,
    final_output: 0,
    success_rate: 0,
    processing_time: 0
  })
  
  // 計算屬性
  const criticalSignals = computed(() => 
    signals.value.filter(signal => signal.priority === 'CRITICAL')
  )
  
  const highSignals = computed(() => 
    signals.value.filter(signal => signal.priority === 'HIGH')
  )
  
  const activeSignals = computed(() => 
    signals.value.filter(signal => signal.status === 'active')
  )
  
  const signalsByPriority = computed(() => {
    const counts = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0, REJECTED: 0 }
    signals.value.forEach(signal => {
      counts[signal.priority] = (counts[signal.priority] || 0) + 1
    })
    return counts
  })
  
  // 動作函數
  async function fetchSignals() {
    loading.value = true
    error.value = null
    
    try {
      const response = await axios.get('/api/v1/monitoring/signals')
      signals.value = response.data.signals || []
      statistics.value = response.data.statistics || statistics.value
      lastUpdate.value = new Date()
    } catch (err) {
      error.value = err.message || '獲取信號失敗'
      console.error('獲取信號錯誤:', err)
    } finally {
      loading.value = false
    }
  }
  
  async function processSignal(signalData) {
    try {
      const response = await axios.post('/api/v1/monitoring/signals/process', signalData)
      
      // 如果處理成功，添加到信號列表
      if (response.data.success) {
        const newSignal = response.data.signal
        signals.value.unshift(newSignal)
        
        // 保持信號列表在合理範圍內
        if (signals.value.length > 1000) {
          signals.value = signals.value.slice(0, 1000)
        }
        
        // 更新統計數據
        statistics.value.total_signals += 1
        if (newSignal.epl_decision !== 'REJECTED') {
          statistics.value.epl_passed += 1
        }
        if (['CRITICAL', 'HIGH'].includes(newSignal.priority)) {
          statistics.value.final_output += 1
        }
      }
      
      return response.data
    } catch (err) {
      error.value = err.message || '處理信號失敗'
      throw err
    }
  }
  
  function addSignal(signal) {
    // 檢查重複信號
    const existing = signals.value.find(s => 
      s.symbol === signal.symbol && 
      s.signal_type === signal.signal_type &&
      Math.abs(new Date(s.timestamp) - new Date(signal.timestamp)) < 15 * 60 * 1000 // 15分鐘內
    )
    
    if (!existing) {
      signals.value.unshift({
        ...signal,
        id: Date.now() + Math.random(),
        timestamp: new Date().toISOString(),
        status: 'active'
      })
      
      // 觸發實時更新
      lastUpdate.value = new Date()
    }
  }
  
  function updateSignal(signalId, updates) {
    const index = signals.value.findIndex(s => s.id === signalId)
    if (index !== -1) {
      signals.value[index] = { ...signals.value[index], ...updates }
    }
  }
  
  function removeSignal(signalId) {
    const index = signals.value.findIndex(s => s.id === signalId)
    if (index !== -1) {
      signals.value.splice(index, 1)
    }
  }
  
  async function testSignal() {
    const testSignalData = {
      symbol: 'BTCUSDT',
      signal_type: 'BUY',
      confidence: 0.87,
      entry_price: 95847.23,
      stop_loss: 92450.00,
      take_profit: 102339.00,
      quality_score: 87.0,
      source: 'sniper',
      indicators_used: ['RSI', 'MACD', '狙擊手雙層'],
      reasoning: '狙擊手雙層架構確認 + RSI黃金交叉',
      timeframe: '15m',
      risk_reward_ratio: 1.91
    }
    
    return await processSignal(testSignalData)
  }
  
  function clearSignals() {
    signals.value = []
    statistics.value = {
      total_signals: 0,
      epl_passed: 0,
      final_output: 0,
      success_rate: 0,
      processing_time: 0
    }
    lastUpdate.value = new Date()
  }
  
  return {
    // 狀態
    signals,
    loading,
    error,
    lastUpdate,
    statistics,
    
    // 計算屬性
    criticalSignals,
    highSignals,
    activeSignals,
    signalsByPriority,
    
    // 動作
    fetchSignals,
    processSignal,
    addSignal,
    updateSignal,
    removeSignal,
    testSignal,
    clearSignals
  }
})
