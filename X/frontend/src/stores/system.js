import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { io } from 'socket.io-client'

export const useSystemStore = defineStore('system', () => {
  // 系統狀態
  const systemHealth = ref('HEALTHY')
  const connectionStatus = ref('disconnected')
  const lastHeartbeat = ref(null)
  const uptime = ref(0)
  const responseTime = ref(0)
  
  // WebSocket 連接
  const socket = ref(null)
  const wsConnected = ref(false)
  
  // 系統統計
  const systemStats = ref({
    // 狙擊手雙層架構
    sniper: {
      layer1_time: 12,
      layer2_filter_rate: 74.2,
      accuracy: 94.3,
      active_connections: 7,
      latest_signal: 'ETHUSDT BUY',
      confidence: 82.4
    },
    
    // Phase1ABC 動態系統
    phase1abc: {
      signal_rebuild: 85,
      volatility_adaptation: 78,
      standardization: 92,
      overall_score: 85
    },
    
    // Phase2+3 完整整合
    phase23: {
      dynamic_weights: 4,
      market_depth_levels: 8,
      risk_adjustment: 73,
      enhancement_score: 81
    },
    
    // EPL 決策引擎
    epl: {
      replacement_decisions: 12,
      position_additions: 8,
      new_positions: 27,
      ignored_signals: 249,
      active_positions: 5,
      decision_accuracy: 91.7
    },
    
    // 通知系統
    notifications: {
      gmail_sent: 23,
      success_rate: 100,
      critical_count: 3,
      high_count: 8,
      standard_count: 12,
      websocket_pushes: 47,
      last_notification: '5分鐘前',
      cooldown_status: '正常'
    }
  })
  
  // 性能指標
  const performanceMetrics = ref({
    today_signals: 1247,
    epl_pass_rate: 23.7,
    epl_passed_count: 296,
    final_output: 47,
    success_rate: 89.4,
    avg_processing_time: 156,
    duplicate_filtered: 412,
    filter_rate: 33
  })
  
  // 計算屬性
  const isSystemHealthy = computed(() => systemHealth.value === 'HEALTHY')
  const isConnected = computed(() => connectionStatus.value === 'connected' && wsConnected.value)
  const uptimeFormatted = computed(() => {
    const hours = Math.floor(uptime.value / 3600)
    const minutes = Math.floor((uptime.value % 3600) / 60)
    return `${hours}小時 ${minutes}分`
  })
  
  // WebSocket 連接管理
  function initializeWebSocket() {
    if (socket.value) {
      socket.value.disconnect()
    }
    
    socket.value = io('ws://localhost:8000', {
      transports: ['websocket'],
      autoConnect: true
    })
    
    socket.value.on('connect', () => {
      wsConnected.value = true
      connectionStatus.value = 'connected'
      console.log('✅ WebSocket 已連接')
    })
    
    socket.value.on('disconnect', () => {
      wsConnected.value = false
      connectionStatus.value = 'disconnected'
      console.log('❌ WebSocket 已斷線')
    })
    
    socket.value.on('system_health', (data) => {
      updateSystemHealth(data)
    })
    
    socket.value.on('performance_update', (data) => {
      updatePerformanceMetrics(data)
    })
    
    socket.value.on('stats_update', (data) => {
      updateSystemStats(data)
    })
    
    // 定期心跳檢測
    socket.value.on('heartbeat', (data) => {
      lastHeartbeat.value = new Date()
      responseTime.value = data.response_time || 0
    })
  }
  
  function disconnectWebSocket() {
    if (socket.value) {
      socket.value.disconnect()
      socket.value = null
    }
    wsConnected.value = false
    connectionStatus.value = 'disconnected'
  }
  
  // 系統健康檢查
  async function checkSystemHealth() {
    try {
      const response = await fetch('/api/v1/monitoring/health')
      const data = await response.json()
      
      systemHealth.value = data.status || 'UNKNOWN'
      uptime.value = data.uptime || 0
      lastHeartbeat.value = new Date()
      
      if (response.ok) {
        connectionStatus.value = 'connected'
      }
      
      return data
    } catch (error) {
      systemHealth.value = 'ERROR'
      connectionStatus.value = 'error'
      console.error('系統健康檢查失敗:', error)
    }
  }
  
  // 更新系統狀態
  function updateSystemHealth(data) {
    if (data.status) systemHealth.value = data.status
    if (data.uptime) uptime.value = data.uptime
    if (data.response_time) responseTime.value = data.response_time
    lastHeartbeat.value = new Date()
  }
  
  function updatePerformanceMetrics(data) {
    performanceMetrics.value = { ...performanceMetrics.value, ...data }
  }
  
  function updateSystemStats(data) {
    systemStats.value = { ...systemStats.value, ...data }
  }
  
  // 測試系統功能
  async function testNotificationSystem() {
    try {
      const response = await fetch('/api/v1/monitoring/notifications/test', {
        method: 'POST'
      })
      return await response.json()
    } catch (error) {
      console.error('測試通知系統失敗:', error)
      throw error
    }
  }
  
  async function restartService(serviceName) {
    try {
      const response = await fetch(`/api/v1/monitoring/services/${serviceName}/restart`, {
        method: 'POST'
      })
      return await response.json()
    } catch (error) {
      console.error(`重啟服務 ${serviceName} 失敗:`, error)
      throw error
    }
  }
  
  // 初始化系統監控
  function initialize() {
    initializeWebSocket()
    checkSystemHealth()
    
    // 定期健康檢查
    setInterval(checkSystemHealth, 30000) // 每30秒檢查一次
  }
  
  // 清理資源
  function cleanup() {
    disconnectWebSocket()
  }
  
  return {
    // 狀態
    systemHealth,
    connectionStatus,
    lastHeartbeat,
    uptime,
    responseTime,
    wsConnected,
    systemStats,
    performanceMetrics,
    
    // 計算屬性
    isSystemHealthy,
    isConnected,
    uptimeFormatted,
    
    // 動作
    initialize,
    cleanup,
    checkSystemHealth,
    updateSystemHealth,
    updatePerformanceMetrics,
    updateSystemStats,
    testNotificationSystem,
    restartService,
    
    // WebSocket 相關
    initializeWebSocket,
    disconnectWebSocket
  }
})
