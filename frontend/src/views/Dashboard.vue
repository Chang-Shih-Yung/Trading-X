<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <!-- Loading 覆蓋層 -->
    <LoadingOverlay 
      :show="isLoading" 
      :title="loadingMessage"
      message="請稍候..."
    />
    
    <!-- 自定義通知 -->
    <CustomNotification
      v-if="notification.show"
      :type="notification.type"
      :title="notification.title"
      :message="notification.message"
      @close="hideNotification"
    />
    
    <div class="mx-auto max-w-7xl">
      <!-- 標題 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">TradingX 量化交易儀表板</h1>
        <p class="mt-2 text-gray-600">實時市場監控與交易信號分析</p>
      </div>

      <!-- 系統狀態 - 實時 API 服務狀態 -->
      <div class="mb-6 bg-whit// 檢測新信號
const detectNewSignals = (newSignals: Signal[]) => {
  const currentTime = new Date()
  const newDetectedSignals: Signal[] = []
  
  newSignals.forEach(signal => {
    const signalKey = `${signal.symbol}_${signal.signal_type}`
    const previousSignal = previousSignalsMap.value.get(signalKey)
    
    // 檢查是否為新信號（5分鐘內的信號視為新信號）
    if (signal.created_at) {
      const signalTime = new Date(signal.created_at)
      const timeDiffMinutes = (currentTime.getTime() - signalTime.getTime()) / (1000 * 60)
      
      if (timeDiffMinutes <= 5 && (!previousSignal || previousSignal.id !== signal.id)) {
        newDetectedSignals.push(signal)
        newSignalIds.value.add(signal.id)
        
        // 自動展開新信號
        expandedSignals.value.add(signal.id)
      }
    }
    
    // 更新信號映射
    previousSignalsMap.value.set(signalKey, signal)
  })
  
  // 發送新信號通知
  if (newDetectedSignals.length > 0) {
    showNewSignalNotification(newDetectedSignals)
    playNotificationSound()
  }
  
  // 10秒後移除新信號標記
  setTimeout(() => {
    newDetectedSignals.forEach(signal => {
      newSignalIds.value.delete(signal.id)
    })
  }, 10000)
}

// 顯示新信號通知
const showNewSignalNotification = (signals: Signal[]) => {
  const symbolsList = signals.map(s => s.symbol).join(', ')
  const signalTypes = signals.map(s => s.signal_type).join(', ')
  
  showNotification(
    'success', 
    `🎯 新交易信號出現！`,
    `${symbolsList} 產生 ${signalTypes} 信號，共 ${signals.length} 個新信號`
  )
}

// 播放通知音效
const playNotificationSound = () => {
  if (!soundNotificationEnabled.value) return
  
  try {
    // 創建簡單的提示音
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
    const oscillator = audioContext.createOscillator()
    const gainNode = audioContext.createGain()
    
    oscillator.connect(gainNode)
    gainNode.connect(audioContext.destination)
    
    oscillator.frequency.setValueAtTime(800, audioContext.currentTime)
    oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1)
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3)
    
    oscillator.start(audioContext.currentTime)
    oscillator.stop(audioContext.currentTime + 0.3)
  } catch (error) {
    console.log('無法播放通知音效:', error)
  }
}

// 檢查信號是否為新信號
const isNewSignal = (signalId: number | string): boolean => {
  return newSignalIds.value.has(signalId)
}

// 獲取信號排序（新信號優先，然後按置信度排序）
const getSortedSignals = (signals: Signal[]): Signal[] => {
  return signals.sort((a, b) => {
    // 新信號優先
    const aIsNew = isNewSignal(a.id)
    const bIsNew = isNewSignal(b.id)
    
    if (aIsNew && !bIsNew) return -1
    if (!aIsNew && bIsNew) return 1
    
    // 然後按置信度排序
    return (b.confidence - a.confidence)
  })
}d-lg p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">🚀 系統服務狀態</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="flex items-center space-x-2">
            <div :class="serviceStatus.market_data ? 'bg-green-500' : 'bg-red-500'" class="w-3 h-3 rounded-full"></div>
            <span class="text-sm">市場數據服務</span>
            <span :class="serviceStatus.market_data ? 'text-green-600' : 'text-red-600'" class="text-xs font-medium">
              {{ serviceStatus.market_data ? '正常' : '異常' }}
            </span>
          </div>
          <div class="flex items-center space-x-2">
            <div :class="serviceStatus.strategy_engine ? 'bg-green-500' : 'bg-red-500'" class="w-3 h-3 rounded-full"></div>
            <span class="text-sm">策略引擎</span>
            <span :class="serviceStatus.strategy_engine ? 'text-green-600' : 'text-red-600'" class="text-xs font-medium">
              {{ serviceStatus.strategy_engine ? '正常' : '異常' }}
            </span>
          </div>
          <div class="flex items-center space-x-2">
            <div :class="serviceStatus.backtest_service ? 'bg-green-500' : 'bg-red-500'" class="w-3 h-3 rounded-full"></div>
            <span class="text-sm">回測服務</span>
            <span :class="serviceStatus.backtest_service ? 'text-green-600' : 'text-red-600'" class="text-xs font-medium">
              {{ serviceStatus.backtest_service ? '正常' : '異常' }}
            </span>
          </div>
          <div class="flex items-center space-x-2">
            <div :class="serviceStatus.database ? 'bg-green-500' : 'bg-red-500'" class="w-3 h-3 rounded-full"></div>
            <span class="text-sm">資料庫</span>
            <span :class="serviceStatus.database ? 'text-green-600' : 'text-red-600'" class="text-xs font-medium">
              {{ serviceStatus.database ? '正常' : '異常' }}
            </span>
          </div>
        </div>
      </div>

      <!-- 統計卡片 -->
      <div class="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div class="bg-white shadow rounded-lg p-6">
          <div class="flex items-center">
            <div class="p-3 rounded-full bg-blue-100">
              <svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">活躍信號</p>
              <p class="text-2xl font-semibold text-gray-900">{{ stats.activeSignals }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white shadow rounded-lg p-6">
          <div class="flex items-center">
            <div class="p-3 rounded-full bg-green-100">
              <svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">今日信號</p>
              <p class="text-2xl font-semibold text-gray-900">{{ stats.todaySignals }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white shadow rounded-lg p-6">
          <div class="flex items-center">
            <div class="p-3 rounded-full bg-yellow-100">
              <svg class="h-6 w-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">平均信心度</p>
              <p class="text-2xl font-semibold text-gray-900">{{ stats.avgConfidence }}%</p>
            </div>
          </div>
        </div>

        <div class="bg-white shadow rounded-lg p-6">
          <div class="flex items-center">
            <div class="p-3 rounded-full bg-purple-100">
              <svg class="h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">平均風險報酬</p>
              <p class="text-2xl font-semibold text-gray-900">{{ stats.avgRiskReward }}</p>
            </div>
          </div>
        </div>
      </div>



      <!-- 最新交易信號 - 增強版本 -->
      <div class="mb-8 bg-white shadow rounded-lg p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-semibold text-gray-900">🎯 最新交易信號分析</h2>
          
          <!-- 信號設置和狀態 -->
          <div class="flex items-center space-x-4">
            <!-- 新信號計數 -->
            <div v-if="newSignalIds.size > 0" 
                 class="flex items-center space-x-2 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
              <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              <span class="font-medium">{{ newSignalIds.size }} 個新信號</span>
            </div>
            
            <!-- 信號歷史按鈕 -->
            <button
              @click="showSignalHistory = !showSignalHistory"
              class="flex items-center space-x-2 px-3 py-1 text-sm bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-md transition-colors"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <span>信號歷史 ({{ savedSignalsHistory.length }})</span>
            </button>
            
            <!-- 音效通知切換 -->
            <div class="flex items-center space-x-2">
              <label class="text-sm text-gray-600">音效通知</label>
              <input 
                v-model="soundNotificationEnabled" 
                type="checkbox" 
                class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              >
            </div>
            
            <!-- 信號總數顯示 -->
            <div class="text-sm text-gray-500">
              共 {{ latestSignals.length }} 個信號
            </div>
          </div>
        </div>
        
        <!-- 信號歷史面板 -->
        <div v-if="showSignalHistory" class="mb-6 p-4 bg-gray-50 rounded-lg border-l-4 border-blue-500">
          <div class="flex justify-between items-center mb-4">
            <h3 class="font-semibold text-gray-800">📊 信號歷史記錄</h3>
            <div class="flex items-center space-x-3">
              <!-- 分類選擇 -->
              <select 
                v-model="selectedCategory" 
                class="text-sm border border-gray-300 rounded px-3 py-1 focus:ring-2 focus:ring-blue-500"
              >
                <option value="ALL">所有幣種</option>
                <option v-for="(category, symbol) in signalCategories" :key="symbol" :value="symbol">
                  {{ category.name }} ({{ category.count }})
                </option>
              </select>
              
              <!-- 清除歷史按鈕 -->
              <button
                @click="clearSignalHistory(selectedCategory)"
                class="text-sm px-3 py-1 bg-red-100 hover:bg-red-200 text-red-700 rounded transition-colors"
              >
                清除歷史
              </button>
              
              <!-- 關閉按鈕 -->
              <button
                @click="showSignalHistory = false"
                class="text-gray-500 hover:text-gray-700"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
          </div>
          
          <!-- 歷史信號列表 -->
          <div class="max-h-96 overflow-y-auto space-y-3">
            <div v-for="signal in getFilteredSignalHistory().slice(0, 20)" :key="`history-${signal.id}`"
                 class="bg-white p-4 rounded border-l-4"
                 :class="{
                   'border-green-400': signal.archive_reason === 'completed',
                   'border-yellow-400': signal.archive_reason === 'expired',
                   'border-red-400': signal.archive_reason === 'stopped',
                   'border-gray-400': signal.archive_reason === 'archived'
                 }">
              <div class="flex justify-between items-start">
                <div class="flex-1">
                  <div class="flex items-center space-x-3 mb-2">
                    <h4 class="font-semibold text-gray-900">{{ signal.symbol }}</h4>
                    <span :class="{
                      'bg-green-100 text-green-800': signal.signal_type === 'BUY',
                      'bg-red-100 text-red-800': signal.signal_type === 'SELL'
                    }" class="px-2 py-1 text-xs rounded-full">
                      {{ signal.signal_type }}
                    </span>
                    <span class="text-xs text-gray-500">
                      {{ signal.archived_at ? formatTime(signal.archived_at) : '' }}
                    </span>
                  </div>
                  
                  <div class="grid grid-cols-3 gap-3 text-sm">
                    <div>
                      <span class="text-gray-500">進場: </span>
                      <span class="font-medium">${{ signal.entry_price?.toFixed(4) || 'N/A' }}</span>
                    </div>
                    <div>
                      <span class="text-gray-500">信心度: </span>
                      <span class="font-medium">{{ Math.round(signal.confidence * 100) }}%</span>
                    </div>
                    <div>
                      <span class="text-gray-500">結果: </span>
                      <span class="font-medium" :class="{
                        'text-green-600': signal.final_result?.startsWith('+'),
                        'text-red-600': signal.final_result?.startsWith('-'),
                        'text-gray-600': !signal.final_result?.startsWith('+') && !signal.final_result?.startsWith('-')
                      }">
                        {{ signal.final_result || 'N/A' }}
                      </span>
                    </div>
                  </div>
                  
                  <div class="mt-2 text-xs text-gray-600">
                    移除原因: {{ 
                      signal.archive_reason === 'completed' ? '✅ 完成' :
                      signal.archive_reason === 'expired' ? '⏰ 過期' :
                      signal.archive_reason === 'stopped' ? '🛑 止損' :
                      '📁 歸檔'
                    }}
                  </div>
                </div>
              </div>
            </div>
            
            <div v-if="getFilteredSignalHistory().length === 0" class="text-center text-gray-500 py-8">
              <div class="text-2xl mb-2">📭</div>
              <p>暫無歷史記錄</p>
            </div>
          </div>
        </div>
        
        <div v-if="latestSignals.length > 0" class="space-y-6">
          <!-- 信號卡片展示 -->
          <div v-for="signal in latestSignals" :key="signal.id" 
               :class="[
                 'border rounded-lg hover:shadow-md transition-all duration-300',
                 newSignalIds.has(signal.id) ? 
                   'border-green-400 bg-green-50 shadow-lg animate-pulse' : 
                   'border-gray-200'
               ]">
            
            <!-- 新信號標記 -->
            <div v-if="newSignalIds.has(signal.id)" 
                 class="bg-gradient-to-r from-green-500 to-emerald-500 text-white text-xs font-bold py-1 px-3 rounded-t-lg flex items-center justify-center">
              <span class="animate-bounce mr-1">🎯</span>
              新信號出現！
              <span class="animate-bounce ml-1">🎯</span>
            </div>
            
            <!-- 信號標題行 - 永遠顯示 -->
            <div class="flex items-center justify-between p-6 cursor-pointer" 
                 @click="toggleSignalExpansion(signal.id)">
              <div class="flex items-center space-x-3">
                <h3 :class="[
                  'text-xl font-bold',
                  newSignalIds.has(signal.id) ? 'text-green-700' : 'text-gray-900'
                ]">{{ signal.symbol }}</h3>
                <span :class="{
                  'bg-green-100 text-green-800 border-green-200': signal.signal_type === 'BUY',
                  'bg-red-100 text-red-800 border-red-200': signal.signal_type === 'SELL',
                  'bg-gray-100 text-gray-800 border-gray-200': signal.signal_type === 'HOLD'
                }" class="inline-flex px-3 py-1 text-sm font-semibold rounded-full border">
                  {{ signal.signal_type }}
                </span>
                
                <!-- 置信度顯示 -->
                <div class="flex items-center space-x-2">
                  <div class="w-20 bg-gray-200 rounded-full h-2">
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
                  <span class="text-sm font-medium text-gray-700">{{ Math.round(signal.confidence * 100) }}%</span>
                </div>
              </div>
              
              <!-- 展開/收縮按鈕 -->
              <div class="flex items-center space-x-4">
                <div v-if="signal.historical_win_rate" class="text-right">
                  <div class="text-sm text-gray-500">歷史勝率</div>
                  <div class="text-lg font-bold text-green-600">{{ signal.historical_win_rate }}</div>
                </div>
                <svg 
                  :class="expandedSignals.has(signal.id) ? 'rotate-180' : ''"
                  class="w-5 h-5 text-gray-400 transition-transform duration-200"
                  fill="none" stroke="currentColor" viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </div>
            </div>
            
            <!-- 重要信息摘要 - 永遠顯示 -->
            <div class="px-6 pb-4">
              <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
                <div class="text-center p-2 bg-blue-50 rounded text-sm">
                  <div class="text-xs text-gray-500">進場價格</div>
                  <div class="font-bold text-blue-600">
                    ${{ signal.entry_price ? signal.entry_price.toFixed(4) : 'N/A' }}
                  </div>
                </div>
                
                <div class="text-center p-2 bg-red-50 rounded text-sm">
                  <div class="text-xs text-gray-500">止損價格</div>
                  <div class="font-bold text-red-600">
                    ${{ signal.stop_loss ? signal.stop_loss.toFixed(4) : 'N/A' }}
                  </div>
                </div>
                
                <div class="text-center p-2 bg-green-50 rounded text-sm">
                  <div class="text-xs text-gray-500">止盈價格</div>
                  <div class="font-bold text-green-600">
                    ${{ signal.take_profit ? signal.take_profit.toFixed(4) : 'N/A' }}
                  </div>
                </div>
                
                <div class="text-center p-2 bg-gray-50 rounded text-sm">
                  <div class="text-xs text-gray-500">發佈時間</div>
                  <div class="font-bold text-gray-700 text-xs">
                    {{ signal.created_at ? formatTime(signal.created_at) : '未知' }}
                  </div>
                </div>
                
                <div class="text-center p-2 rounded text-sm"
                     :class="getTimeValidityStyle(signal)">
                  <div class="text-xs text-gray-500">時效性</div>
                  <div class="font-bold text-xs">
                    {{ calculateSignalValidity(signal) }}
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 詳細信息 - 可展開 -->
            <div v-if="expandedSignals.has(signal.id)" class="px-6 pb-6 border-t border-gray-100">
              <!-- K線形態信息 -->
              <div v-if="signal.pattern_detected" class="mt-4 p-3 bg-blue-50 rounded-lg">
                <div class="flex items-center space-x-2 mb-2">
                  <span class="text-blue-600 font-semibold">📊 檢測形態:</span>
                  <span class="text-blue-800 font-bold">{{ signal.pattern_detected }}</span>
                </div>
                
                <!-- 多時間軸確認 -->
                <div v-if="signal.confirmed_timeframes" class="mb-2">
                  <span class="text-sm text-gray-600">時間軸確認: </span>
                  <span v-for="tf in signal.confirmed_timeframes" :key="tf" 
                        class="inline-block px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded mr-1">
                    {{ tf }}
                  </span>
                </div>
                
                <!-- 時間軸分析詳情 -->
                <div v-if="signal.timeframe_analysis" class="text-sm text-gray-700">
                  <div v-for="analysis in signal.timeframe_analysis" :key="analysis" class="mb-1">
                    • {{ analysis }}
                  </div>
                </div>
              </div>
              
              <!-- 當前價格信息 -->
              <div v-if="signal.current_price" class="mt-4 p-3 bg-gray-50 rounded">
                <div class="text-center">
                  <div class="text-sm text-gray-500">當前價格</div>
                  <div class="text-lg font-bold text-gray-900">
                    ${{ signal.current_price.toLocaleString() }}
                  </div>
                </div>
              </div>
              
              <!-- 技術分析理由 -->
              <div v-if="signal.reasoning" class="mt-4 p-4 bg-yellow-50 border-l-4 border-yellow-400">
                <h4 class="font-semibold text-yellow-800 mb-2">💡 分析理由</h4>
                <p class="text-yellow-700">{{ signal.reasoning }}</p>
              </div>
              
              <!-- 技術指標匯聚 -->
              <div v-if="signal.technical_confluence" class="mt-4">
                <h4 class="font-semibold text-gray-700 mb-2">📈 技術指標匯聚</h4>
                <div class="flex flex-wrap gap-2">
                  <span v-for="indicator in signal.technical_confluence" :key="indicator"
                        class="px-3 py-1 text-sm bg-purple-100 text-purple-700 rounded-full">
                    {{ indicator }}
                  </span>
                </div>
              </div>
              
              <!-- 策略執行信息 -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                <div v-if="signal.entry_strategy" class="p-3 bg-green-50 rounded">
                  <h5 class="font-semibold text-green-700 mb-1">🎯 進場策略</h5>
                  <p class="text-sm text-green-600">{{ signal.entry_strategy }}</p>
                </div>
                
                <div v-if="signal.risk_management" class="p-3 bg-red-50 rounded">
                  <h5 class="font-semibold text-red-700 mb-1">🛡️ 風險管理</h5>
                  <p class="text-sm text-red-600">{{ signal.risk_management }}</p>
                </div>
              </div>
              
              <!-- 風險報酬比 -->
              <div class="mt-4 p-3 bg-gray-50 rounded-lg">
                <div class="flex items-center justify-between">
                  <div>
                    <span class="text-sm text-gray-500">風險回報比</span>
                    <span class="ml-2 font-bold text-gray-900">
                      1:{{ signal.risk_reward_ratio ? signal.risk_reward_ratio.toFixed(1) : 'N/A' }}
                    </span>
                  </div>
                  
                  <div v-if="signal.remaining_validity_hours" class="flex items-center space-x-2">
                    <span class="text-sm text-gray-500">剩餘時效</span>
                    <span class="font-medium" :style="{ color: signal.urgency_color }">
                      {{ signal.remaining_validity_hours }}小時
                    </span>
                    <span class="text-xs px-2 py-1 rounded" 
                          :style="{ backgroundColor: signal.urgency_color + '20', color: signal.urgency_color }">
                      {{ signal.urgency_level }}急迫性
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 無信號時的顯示 -->
        <div v-if="latestSignals.length === 0" class="text-center text-gray-500 py-12">
          <div class="text-4xl mb-4">📊</div>
          <p class="text-lg">暫無交易信號</p>
          <p class="text-sm mt-2">系統正在分析市場形態，請稍候...</p>
        </div>
      </div>

      <!-- 市場總體情緒與實時更新 -->
      <div class="mb-8 bg-white shadow rounded-lg p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-semibold text-gray-900">📊 市場實時動態</h2>
          <div class="flex items-center space-x-2">
            <div 
              :style="{ color: calculateMarketSentiment().color }"
              class="font-semibold text-lg"
            >
              {{ calculateMarketSentiment().text }}
            </div>
            <div class="text-sm text-gray-500">
              (平均漲跌: {{ realtimeUpdates.length > 0 ? 
                (realtimeUpdates.reduce((sum, update) => sum + update.change_24h, 0) / realtimeUpdates.length).toFixed(2) + '%' : 
                '0.00%' }})
            </div>
          </div>
        </div>
        
        <!-- 市場統計 -->
        <div v-if="marketStats" class="grid grid-cols-3 gap-4 mb-4 p-4 bg-gray-50 rounded-md">
          <div class="text-center">
            <div class="text-2xl font-bold text-green-600">{{ marketStats.bullish_count }}</div>
            <div class="text-sm text-gray-600">看多</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-red-600">{{ marketStats.bearish_count }}</div>
            <div class="text-sm text-gray-600">看空</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-gray-600">{{ marketStats.neutral_count }}</div>
            <div class="text-sm text-gray-600">中性</div>
          </div>
        </div>
        
        <!-- 實時更新列表 -->
        <div class="space-y-3 max-h-64 overflow-y-auto">
          <div v-for="update in realtimeUpdates" :key="update.symbol + update.timestamp" 
               class="flex justify-between items-center p-3 bg-gray-50 rounded-md">
            <div class="flex-1">
              <div class="flex items-center space-x-2">
                <span class="font-medium">{{ update.symbol }}</span>
                <span 
                  :style="{ color: update.color }"
                  class="text-sm font-semibold"
                >
                  {{ update.sentiment === 'bullish' ? '🟢 看多' : 
                     update.sentiment === 'bearish' ? '🔴 看空' : 
                     '⚫ 中性' }}
                </span>
              </div>
              <div class="text-sm text-gray-600 mt-1">{{ update.message }}</div>
            </div>
            <div class="text-right text-sm">
              <div class="font-medium">${{ update.price.toFixed(2) }}</div>
              <div class="text-gray-500">{{ formatTime(update.timestamp) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 系統更新日誌 - 增強版（可展開顯示20筆記錄） -->
      <div class="mb-8 bg-white shadow rounded-lg p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-semibold text-gray-900">📋 系統更新日誌</h2>
          <div class="flex items-center space-x-4">
            <!-- 展開/收縮按鈕 -->
            <button
              @click="isLogExpanded = !isLogExpanded"
              class="flex items-center space-x-2 px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
            >
              <svg 
                :class="isLogExpanded ? 'rotate-180' : ''"
                class="w-4 h-4 transition-transform duration-300"
                fill="none" stroke="currentColor" viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
              </svg>
              <span>{{ isLogExpanded ? '收縮' : '展開' }}({{ databaseLogs.length }}筆)</span>
            </button>
            
            <!-- 狀態指示器 -->
            <div class="flex items-center space-x-2">
              <div 
                :class="isLogRefreshing ? 'animate-pulse bg-green-400 shadow-lg' : 'bg-green-500'"
                class="w-2 h-2 rounded-full transition-all duration-300"
              ></div>
              <span 
                :class="isLogRefreshing ? 'text-blue-600 font-medium' : 'text-gray-500'"
                class="text-sm transition-all duration-300"
              >
                {{ isLogRefreshing ? '正在更新...' : '每5秒更新' }}
              </span>
              <div 
                v-if="isLogRefreshing"
                class="inline-flex items-center text-xs text-blue-500 animate-pulse"
              >
                <svg class="w-3 h-3 mr-1 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                更新中
              </div>
            </div>
          </div>
        </div>
        
        <!-- 日誌區域 - 可展開至20筆記錄 -->
        <div 
          :class="[
            isLogRefreshing ? 'animate-pulse bg-blue-50' : 'bg-gray-50',
            isLogExpanded ? 'max-h-96' : 'max-h-64'
          ]"
          class="space-y-2 overflow-y-auto rounded-md p-4 transition-all duration-300"
        >
          <div v-for="log in databaseLogs" :key="log.timestamp + log.message"
               :class="[
                 'flex justify-between items-start p-3 bg-white rounded border-l-4 transition-all duration-200',
                 isLogRefreshing ? 'shadow-md border-l-8' : '',
                 {
                   'border-green-500': log.type === 'success',
                   'border-blue-500': log.type === 'info',
                   'border-yellow-500': log.type === 'warning',
                   'border-red-500': log.type === 'error',
                   'border-gray-500': log.type === 'debug'
                 }
               ]">
            <div class="flex-1">
              <!-- 時間戳顯示 -->
              <div 
                :class="isLogRefreshing ? 'text-blue-600 font-semibold' : 'text-gray-400'"
                class="text-xs mb-1 transition-all duration-200"
              >
                🕒 {{ formatFullTime(log.timestamp) }}
              </div>
              <!-- 日誌訊息 -->
              <div 
                :style="{ color: log.color }"
                :class="isLogRefreshing ? 'font-semibold' : ''"
                class="text-sm transition-all duration-200"
              >
                {{ log.message }}
              </div>
            </div>
            <div 
              :class="[
                'text-xs px-2 py-1 rounded-full text-center min-w-12 transition-all duration-200',
                isLogRefreshing ? 'font-semibold' : '',
                {
                  'bg-green-100 text-green-700': log.type === 'success',
                  'bg-blue-100 text-blue-700': log.type === 'info',
                  'bg-yellow-100 text-yellow-700': log.type === 'warning',
                  'bg-red-100 text-red-700': log.type === 'error',
                  'bg-gray-100 text-gray-700': log.type === 'debug'
                }
              ]"
            >
              {{ log.type.toUpperCase() }}
            </div>
          </div>
          
          <div v-if="databaseLogs.length === 0" class="text-center text-gray-500 py-8">
            <div 
              :class="isLogRefreshing ? 'animate-spin' : ''"
              class="inline-block w-6 h-6 mb-2"
            >
              ⚙️
            </div>
            <p>{{ isLogRefreshing ? '正在更新系統日誌...' : '暫無系統日誌' }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import CustomNotification from '../components/CustomNotification.vue'
import LoadingOverlay from '../components/LoadingOverlay.vue'

interface Signal {
  id: number | string
  symbol: string
  signal_type: string
  entry_price?: number
  stop_loss?: number
  take_profit?: number
  risk_reward_ratio?: number
  confidence: number
  // 新增的精準分析字段
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
  // 歷史信號專用字段
  archived_at?: string
  archive_reason?: 'completed' | 'expired' | 'stopped' | 'archived'
  final_result?: string
}

interface RealtimeUpdate {
  symbol: string
  message: string
  price: number
  change_24h: number
  short_term_change: number
  sentiment: string
  color: string
  timestamp: string
  volume: number
}

interface MarketStats {
  bullish_count: number
  bearish_count: number
  neutral_count: number
}

interface DatabaseLog {
  timestamp: string
  message: string
  type: string
  color: string
}

interface ServiceStatus {
  market_data: boolean
  strategy_engine: boolean
  backtest_service: boolean
  database: boolean
}

interface NotificationData {
  show: boolean
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
}

const stats = reactive({
  activeSignals: 0,
  todaySignals: 0,
  avgConfidence: 0,
  avgRiskReward: 0
})

const latestSignals = ref<Signal[]>([])
const realtimeUpdates = ref<RealtimeUpdate[]>([])
const databaseLogs = ref<DatabaseLog[]>([])
const marketOverallSentiment = ref<string>('market_neutral')
const marketOverallColor = ref<string>('black')
const marketStats = ref<MarketStats | null>(null)
const serviceStatus = ref<ServiceStatus>({
  market_data: false,
  strategy_engine: false,
  backtest_service: false,
  database: false
})

// 信號儲存和分類管理
const signalCategories = ref<Record<string, { name: string; signals: Signal[]; count: number }>>({
  'BTC/USDT': { name: 'Bitcoin', signals: [], count: 0 },
  'ETH/USDT': { name: 'Ethereum', signals: [], count: 0 },
  'BNB/USDT': { name: 'Binance Coin', signals: [], count: 0 },
  'ADA/USDT': { name: 'Cardano', signals: [], count: 0 },
  'SOL/USDT': { name: 'Solana', signals: [], count: 0 }
})

const savedSignalsHistory = ref<Signal[]>([])
const showSignalHistory = ref(false)
const selectedCategory = ref<string>('ALL')

// 信號展開狀態管理
const expandedSignals = ref<Set<number | string>>(new Set())

// 新信號追蹤狀態
const newSignalIds = ref<Set<number | string>>(new Set())

// 使用者設置
const soundNotificationEnabled = ref(true)

// 儲存信號到歷史記錄
const saveSignalToHistory = (signal: Signal, action: 'completed' | 'expired' | 'stopped' | 'archived') => {
  const historicalSignal = {
    ...signal,
    archived_at: new Date().toISOString(),
    archive_reason: action,
    final_result: calculateSignalResult(signal)
  }
  
  // 添加到歷史記錄
  savedSignalsHistory.value.unshift(historicalSignal)
  
  // 更新分類統計
  if (signalCategories.value[signal.symbol]) {
    signalCategories.value[signal.symbol].signals.push(historicalSignal)
    signalCategories.value[signal.symbol].count++
  }
  
  // 限制歷史記錄數量（最多保存1000條）
  if (savedSignalsHistory.value.length > 1000) {
    savedSignalsHistory.value = savedSignalsHistory.value.slice(0, 1000)
  }
  
  // 保存到 localStorage
  try {
    localStorage.setItem('tradingx_signal_history', JSON.stringify(savedSignalsHistory.value))
    localStorage.setItem('tradingx_signal_categories', JSON.stringify(signalCategories.value))
  } catch (error) {
    console.error('無法保存信號歷史:', error)
  }
}

// 計算信號結果
const calculateSignalResult = (signal: Signal): string => {
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

// 從 localStorage 載入歷史記錄
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

// 獲取分類後的信號
const getFilteredSignalHistory = (): Signal[] => {
  if (selectedCategory.value === 'ALL') {
    return savedSignalsHistory.value
  }
  
  return savedSignalsHistory.value.filter(signal => signal.symbol === selectedCategory.value)
}

// 清理歷史記錄
const clearSignalHistory = (category?: string) => {
  if (category && category !== 'ALL') {
    savedSignalsHistory.value = savedSignalsHistory.value.filter(signal => signal.symbol !== category)
    if (signalCategories.value[category]) {
      signalCategories.value[category].signals = []
      signalCategories.value[category].count = 0
    }
  } else {
    savedSignalsHistory.value = []
    Object.keys(signalCategories.value).forEach(key => {
      signalCategories.value[key].signals = []
      signalCategories.value[key].count = 0
    })
  }
  
  // 更新 localStorage
  try {
    localStorage.setItem('tradingx_signal_history', JSON.stringify(savedSignalsHistory.value))
    localStorage.setItem('tradingx_signal_categories', JSON.stringify(signalCategories.value))
  } catch (error) {
    console.error('無法更新信號歷史:', error)
  }
}

// Loading 和通知狀態
const isLoading = ref(false)
const loadingMessage = ref('')
const notification = ref<NotificationData>({
  show: false,
  type: 'info',
  title: '',
  message: ''
})

// 系統更新日誌閃爍效果和展開狀態
const isLogRefreshing = ref(false)
const isLogExpanded = ref(false)  // 新增：日誌展開狀態

let updateInterval: NodeJS.Timeout | null = null
let logUpdateInterval: NodeJS.Timeout | null = null

const formatTime = (timestamp: string): string => {
  try {
    let date: Date
    
    if (timestamp.includes('T') || timestamp.includes('Z')) {
      date = new Date(timestamp)
    } else if (timestamp.match(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/)) {
      date = new Date(timestamp.replace(' ', 'T'))
    } else if (!isNaN(Number(timestamp))) {
      const num = Number(timestamp)
      date = new Date(num > 1e10 ? num : num * 1000)
    } else {
      date = new Date(timestamp)
    }
    
    if (isNaN(date.getTime())) {
      return '無效'
    }
    
    return date.toLocaleTimeString('zh-TW', {
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return '錯誤'
  }
}

const formatFullTime = (timestamp: string): string => {
  try {
    // 處理各種時間戳格式
    let date: Date
    
    if (timestamp.includes('T') || timestamp.includes('Z')) {
      // ISO 格式
      date = new Date(timestamp)
    } else if (timestamp.match(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/)) {
      // SQL 格式 YYYY-MM-DD HH:MM:SS
      date = new Date(timestamp.replace(' ', 'T'))
    } else if (!isNaN(Number(timestamp))) {
      // Unix timestamp (秒或毫秒)
      const num = Number(timestamp)
      date = new Date(num > 1e10 ? num : num * 1000)
    } else {
      // 直接嘗試解析
      date = new Date(timestamp)
    }
    
    // 檢查日期是否有效
    if (isNaN(date.getTime())) {
      console.warn('Invalid timestamp:', timestamp)
      return '無效時間'
    }
    
    return date.toLocaleString('zh-TW', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch (error) {
    console.error('時間格式化錯誤:', error, 'timestamp:', timestamp)
    return '時間錯誤'
  }
}

const showNotification = (type: 'success' | 'error' | 'warning' | 'info', title: string, message?: string) => {
  notification.value = {
    show: true,
    type,
    title,
    message
  }
}

const hideNotification = () => {
  notification.value.show = false
}

const showLoading = (message: string) => {
  isLoading.value = true
  loadingMessage.value = message
}

const hideLoading = () => {
  isLoading.value = false
  loadingMessage.value = ''
}

// 信號展開/收縮切換
const toggleSignalExpansion = (signalId: number | string) => {
  if (expandedSignals.value.has(signalId)) {
    expandedSignals.value.delete(signalId)
  } else {
    expandedSignals.value.add(signalId)
  }
}

// 計算信號時效性
const calculateSignalValidity = (signal: Signal): string => {
  if (!signal.created_at) return '未知'
  
  try {
    const createdTime = new Date(signal.created_at)
    const now = new Date()
    const hoursElapsed = (now.getTime() - createdTime.getTime()) / (1000 * 60 * 60)
    
    // 假設信號有效期為 24 小時
    const totalValidityHours = 24
    const remainingHours = Math.max(0, totalValidityHours - hoursElapsed)
    const validityPercentage = (remainingHours / totalValidityHours) * 100
    
    if (validityPercentage > 70) {
      return `${Math.round(remainingHours)}h (新鮮)`
    } else if (validityPercentage > 30) {
      return `${Math.round(remainingHours)}h (有效)`
    } else if (validityPercentage > 0) {
      return `${Math.round(remainingHours)}h (即將過期)`
    } else {
      return '已過期'
    }
  } catch (error) {
    return '計算錯誤'
  }
}

// 獲取時效性樣式
const getTimeValidityStyle = (signal: Signal): string => {
  if (!signal.created_at) return 'bg-gray-50'
  
  try {
    const createdTime = new Date(signal.created_at)
    const now = new Date()
    const hoursElapsed = (now.getTime() - createdTime.getTime()) / (1000 * 60 * 60)
    
    const totalValidityHours = 24
    const remainingHours = Math.max(0, totalValidityHours - hoursElapsed)
    const validityPercentage = (remainingHours / totalValidityHours) * 100
    
    if (validityPercentage > 70) {
      return 'bg-green-50' // 新鮮
    } else if (validityPercentage > 30) {
      return 'bg-yellow-50' // 有效但需注意
    } else if (validityPercentage > 0) {
      return 'bg-orange-50' // 即將過期
    } else {
      return 'bg-red-50' // 已過期
    }
  } catch (error) {
    return 'bg-gray-50'
  }
}

// 智能信號刪除機制
const shouldDeleteSignal = (signal: Signal): { shouldDelete: boolean; reason: string } => {
  const now = new Date()
  
  // 1. 檢查時效性 - 超過24小時自動刪除
  if (signal.created_at) {
    const createdTime = new Date(signal.created_at)
    const hoursElapsed = (now.getTime() - createdTime.getTime()) / (1000 * 60 * 60)
    
    if (hoursElapsed > 24) {
      return { shouldDelete: true, reason: '時效過期' }
    }
  }
  
  // 2. 檢查信心度 - 低於15%的信號刪除
  if (signal.confidence < 0.15) {
    return { shouldDelete: true, reason: '信心度過低' }
  }
  
  // 3. 檢查黑天鵝事件標記
  if (signal.market_context && signal.market_context.includes('黑天鵝')) {
    return { shouldDelete: true, reason: '黑天鵝事件影響' }
  }
  
  // 4. 檢查突發變盤因素
  if (signal.market_context && signal.market_context.includes('突發變盤')) {
    return { shouldDelete: true, reason: '市場突發變盤' }
  }
  
  // 5. 檢查價格偏離度 - 如果當前價格與進場價格偏離超過10%且是不利方向
  if (signal.current_price && signal.entry_price) {
    const priceDeviation = Math.abs(signal.current_price - signal.entry_price) / signal.entry_price
    
    if (priceDeviation > 0.1) {
      // 買入信號但價格大幅下跌，賣出信號但價格大幅上漲
      if ((signal.signal_type === 'BUY' && signal.current_price < signal.entry_price * 0.9) ||
          (signal.signal_type === 'SELL' && signal.current_price > signal.entry_price * 1.1)) {
        return { shouldDelete: true, reason: '價格偏離過大' }
      }
    }
  }
  
  // 6. 檢查止損觸發
  if (signal.stop_loss && signal.current_price) {
    if ((signal.signal_type === 'BUY' && signal.current_price <= signal.stop_loss) ||
        (signal.signal_type === 'SELL' && signal.current_price >= signal.stop_loss)) {
      return { shouldDelete: true, reason: '止損觸發' }
    }
  }
  
  // 7. 檢查技術指標失效
  if (signal.technical_confluence && signal.technical_confluence.length === 0) {
    return { shouldDelete: true, reason: '技術指標失效' }
  }
  
  return { shouldDelete: false, reason: '' }
}

// 過濾和管理信號 - 增強版
const filterValidSignals = (signals: Signal[]): Signal[] => {
  const validSignals: Signal[] = []
  const deletedSignals: Array<{ signal: Signal; reason: string }> = []
  
  signals.forEach(signal => {
    const deleteCheck = shouldDeleteSignal(signal)
    
    if (deleteCheck.shouldDelete) {
      deletedSignals.push({ signal, reason: deleteCheck.reason })
      // 可選：發送刪除通知
      if (deletedSignals.length <= 3) { // 避免過多通知
        showNotification('info', '信號已自動移除', `${signal.symbol} ${deleteCheck.reason}`)
      }
    } else {
      validSignals.push(signal)
    }
  })
  
  // 記錄刪除統計
  if (deletedSignals.length > 0) {
    console.log(`已移除 ${deletedSignals.length} 個信號:`, deletedSignals)
  }
  
  return validSignals
}

// 計算市場整體情緒（基於漲跌幅大於5%的邏輯）
const calculateMarketSentiment = () => {
  if (realtimeUpdates.value.length === 0) {
    return { sentiment: 'market_neutral', color: 'black', text: '⚫ 中性市場' }
  }
  
  // 計算平均漲跌幅
  const totalChange = realtimeUpdates.value.reduce((sum, update) => sum + update.change_24h, 0)
  const avgChange = totalChange / realtimeUpdates.value.length
  
  // 基於平均漲跌幅判斷市場情緒
  if (avgChange > 5) {
    return { sentiment: 'bullish', color: 'green', text: '🟢 多頭市場' }
  } else if (avgChange < -5) {
    return { sentiment: 'bearish', color: 'red', text: '🔴 空頭市場' }
  } else {
    return { sentiment: 'neutral', color: 'black', text: '⚫ 中性市場' }
  }
}

// 檢查服務狀態
const checkServiceStatus = async () => {
  try {
    // 檢查市場數據服務
    try {
      await axios.get('/api/v1/market/symbols', { timeout: 3000 })
      serviceStatus.value.market_data = true
    } catch {
      serviceStatus.value.market_data = false
    }

    // 檢查後端健康狀態
    try {
      await axios.get('/health', { timeout: 3000 })
      serviceStatus.value.strategy_engine = true
      serviceStatus.value.backtest_service = true
      serviceStatus.value.database = true
    } catch {
      serviceStatus.value.strategy_engine = false
      serviceStatus.value.backtest_service = false
      serviceStatus.value.database = false
    }
  } catch (error) {
    console.error('檢查服務狀態失敗:', error)
  }
}

const fetchRealtimeUpdates = async () => {
  try {
    isLogRefreshing.value = true
    const response = await axios.get('/api/v1/market/realtime-updates', { timeout: 10000 })
    const data = response.data
    
    realtimeUpdates.value = data.updates || []
    databaseLogs.value = data.database_logs || []
    marketOverallSentiment.value = data.overall_sentiment || 'market_neutral'
    marketOverallColor.value = data.overall_color || 'black'
    marketStats.value = data.market_stats || null
    
    // 3秒後移除閃爍效果（3秒閃爍 + 2秒正常 = 5秒週期）
    setTimeout(() => {
      isLogRefreshing.value = false
    }, 3000)
    
  } catch (error) {
    isLogRefreshing.value = false
    console.error('獲取實時更新失敗:', error)
    showNotification('error', '獲取市場數據失敗', '無法連接到市場數據服務，請檢查網路連接')
  }
}

const fetchDashboardData = async () => {
  try {
    showLoading('載入儀表板數據...')
    
    // 獲取最新信號
    const signalsResponse = await axios.get('/api/v1/signals/latest?hours=24', { timeout: 10000 })
    
    // 應用智能過濾邏輯
    const rawSignals = signalsResponse.data || []
    const filteredSignals = filterValidSignals(rawSignals)
    
    // 簡化的新信號檢測：檢查是否有新的信號 ID
    if (latestSignals.value.length > 0) {
      const existingIds = new Set(latestSignals.value.map(s => s.id))
      const newSignals = filteredSignals.filter(signal => !existingIds.has(signal.id))
      
      // 檢查已移除的信號並儲存到歷史
      const currentIds = new Set(filteredSignals.map(s => s.id))
      const removedSignals = latestSignals.value.filter(signal => !currentIds.has(signal.id))
      
      removedSignals.forEach(signal => {
        const deleteReason = shouldDeleteSignal(signal)
        saveSignalToHistory(signal, deleteReason.shouldDelete ? 'expired' : 'archived')
      })
      
      if (newSignals.length > 0) {
        // 標記新信號
        newSignals.forEach(signal => {
          newSignalIds.value.add(signal.id)
          expandedSignals.value.add(signal.id)
        })
        
        // 顯示通知
        const symbolsList = newSignals.map(s => s.symbol).join(', ')
        const signalTypes = newSignals.map(s => s.signal_type).join(', ')
        
        showNotification(
          'success', 
          `🎯 新交易信號出現！`,
          `${symbolsList} 產生 ${signalTypes} 信號，共 ${newSignals.length} 個新信號`
        )
        
        // 播放音效
        if (soundNotificationEnabled.value) {
          try {
            const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
            const oscillator = audioContext.createOscillator()
            const gainNode = audioContext.createGain()
            
            oscillator.connect(gainNode)
            gainNode.connect(audioContext.destination)
            
            oscillator.frequency.setValueAtTime(800, audioContext.currentTime)
            oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1)
            
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime)
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3)
            
            oscillator.start(audioContext.currentTime)
            oscillator.stop(audioContext.currentTime + 0.3)
          } catch (error) {
            console.log('無法播放通知音效:', error)
          }
        }
        
        // 10秒後移除新信號標記
        setTimeout(() => {
          newSignals.forEach(signal => {
            newSignalIds.value.delete(signal.id)
          })
        }, 10000)
      }
    } else {
      // 首次載入，初始化歷史記錄
      loadSignalHistory()
    }
    
    latestSignals.value = filteredSignals
    
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
    
    hideLoading()
    
    if (latestSignals.value.length > 0) {
      showNotification('success', '儀表板數據載入成功', `已載入 ${latestSignals.value.length} 個交易信號`)
    }
    
  } catch (error) {
    hideLoading()
    console.error('獲取儀表板數據失敗:', error)
    showNotification('error', '儀表板數據載入失敗', '無法獲取交易信號數據，請稍後重試')
  }
}

onMounted(() => {
  // 初始載入
  checkServiceStatus()
  fetchDashboardData()
  fetchRealtimeUpdates()
  
  // 設置定時更新信號數據 (每30秒檢查新信號)
  updateInterval = setInterval(() => {
    fetchDashboardData()  // 改為載入信號數據來檢測新信號
  }, 30000)
  
  // 設置系統日誌更新 (每5秒更新一次)
  logUpdateInterval = setInterval(() => {
    fetchRealtimeUpdates()
  }, 5000)
  
  // 每分鐘檢查一次服務狀態
  setInterval(() => {
    checkServiceStatus()
  }, 60000)
})

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
  if (logUpdateInterval) {
    clearInterval(logUpdateInterval)
  }
})
</script>
