<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <!-- Loading 覆蓋層 -->
    <LoadingOverlay :show="isLoading" :title="loadingMessage" message="請稍候..." />

    <!-- 自定義通知 -->
    <CustomNotification v-if="notification.show" :type="notification.type" :title="notification.title"
      :message="notification.message" @close="hideNotification" />

    <div class="mx-auto max-w-7xl">
      <!-- 標題 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">TradingX 量化交易儀表板</h1>
        <p class="mt-2 text-gray-600">實時市場監控與交易信號分析</p>
      </div>

      <!-- 系統狀態 - 實時 API 服務狀態 -->
      <div class="mb-6 bg-white shadow rounded-lg p-6">
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
            <div :class="serviceStatus.strategy_engine ? 'bg-green-500' : 'bg-red-500'" class="w-3 h-3 rounded-full">
            </div>
            <span class="text-sm">策略引擎</span>
            <span :class="serviceStatus.strategy_engine ? 'text-green-600' : 'text-red-600'"
              class="text-xs font-medium">
              {{ serviceStatus.strategy_engine ? '正常' : '異常' }}
            </span>
          </div>
          <div class="flex items-center space-x-2">
            <div :class="serviceStatus.backtest_service ? 'bg-green-500' : 'bg-red-500'" class="w-3 h-3 rounded-full">
            </div>
            <span class="text-sm">回測服務</span>
            <span :class="serviceStatus.backtest_service ? 'text-green-600' : 'text-red-600'"
              class="text-xs font-medium">
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
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
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
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
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
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
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
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">平均風險報酬</p>
              <p class="text-2xl font-semibold text-gray-900">{{ stats.avgRiskReward }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 短線交易信號分析區塊 -->
      <div class="mb-8 bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200 rounded-lg p-6">
        <div class="flex justify-between items-center mb-6">
          <div>
            <h2 class="text-xl font-bold text-orange-800">⚡ 短線信號分析中心 (激進模式)</h2>
            <p class="text-sm text-orange-600 mt-1">
              激進交易模式：30分鐘內快速交易機會 | 每3分鐘更新 | 85%高信心度 | 牛市優化 | 每幣種保留最佳信號
            </p>
            <div class="flex items-center mt-2 space-x-4">
              <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                🔥 激進模式
              </span>
              <span
                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                ⏱️ 3分鐘刷新
              </span>
              <span
                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                📈 85%高信心度
              </span>
              <span
                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                � 牛市優化
              </span>
              <span v-if="priceUpdateTime"
                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                💰 幣安價格: {{ priceUpdateTime }}
              </span>
              <span
                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                🎯 智能去重
              </span>
              <span v-if="scalpingSignalsCache.data.length > 0"
                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                💾 暫存: {{ Math.round((Date.now() - scalpingSignalsCache.timestamp) / 1000) }}秒前
              </span>
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <!-- 短線信號統計 -->
            <div class="text-center">
              <div class="text-2xl font-bold text-orange-600">{{ shortTermStats.totalSignals }}</div>
              <div class="text-xs text-orange-500">短線信號</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-green-600">{{ shortTermStats.avgConfidence }}%</div>
              <div class="text-xs text-orange-500">平均信心度</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-purple-600">{{ shortTermStats.urgentCount }}</div>
              <div class="text-xs text-orange-500">緊急信號</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-blue-600">{{ shortTermStats.strategiesUsed }}</div>
              <div class="text-xs text-orange-500">策略種類</div>
            </div>
            <button @click="refreshShortTermSignals"
              class="px-3 py-1 bg-orange-500 text-white rounded hover:bg-orange-600 text-sm">
              刷新短線
            </button>
          </div>
        </div>

        <!-- 短線信號篩選器 -->
        <div class="mb-4 flex items-center space-x-4 p-3 bg-white rounded-lg border">
          <div class="flex items-center space-x-2">
            <label class="text-sm font-medium text-gray-700">時間框架:</label>
            <select v-model="shortTermFilter.timeframe"
              class="border border-gray-300 rounded px-2 py-1 text-sm focus:ring-2 focus:ring-orange-500">
              <option value="all">全部短線</option>
              <option value="1m">1分鐘</option>
              <option value="5m">5分鐘</option>
              <option value="15m">15分鐘</option>
            </select>
          </div>
          <div class="flex items-center space-x-2">
            <label class="text-sm font-medium text-gray-700">緊急度:</label>
            <select v-model="shortTermFilter.urgency"
              class="border border-gray-300 rounded px-2 py-1 text-sm focus:ring-2 focus:ring-orange-500">
              <option value="all">全部</option>
              <option value="urgent">緊急</option>
              <option value="high">高</option>
              <option value="medium">中等</option>
            </select>
          </div>
          <div class="flex items-center space-x-2">
            <label class="text-sm font-medium text-gray-700">信心度:</label>
            <select v-model="shortTermFilter.confidence"
              class="border border-gray-300 rounded px-2 py-1 text-sm focus:ring-2 focus:ring-orange-500">
              <option value="all">全部</option>
              <option value="high">高(>80%)</option>
              <option value="medium">中(60-80%)</option>
              <option value="low">低(<60%)</option>
            </select>
          </div>
          <button @click="refreshShortTermSignals"
            class="px-3 py-1 bg-orange-600 hover:bg-orange-700 text-white text-sm rounded transition-colors">
            刷新
          </button>
        </div>

        <!-- 短線信號卡片網格 -->
        <div v-if="filteredShortTermSignals.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="signal in filteredShortTermSignals" :key="`short-${signal.id}`"
            class="bg-white rounded-lg border-l-4 border-orange-400 p-4 shadow-sm hover:shadow-md transition-shadow">

            <!-- 信號標題行 -->
            <div class="flex justify-between items-center mb-3">
              <div class="flex items-center space-x-2">
                <h4 class="font-bold text-lg text-gray-900">{{ signal.symbol }}</h4>
                <!-- 做多/做空標示 -->
                <span :class="{
                  'bg-green-100 text-green-800': getSignalDirection(signal.signal_type) === 'LONG',
                  'bg-red-100 text-red-800': getSignalDirection(signal.signal_type) === 'SHORT'
                }" class="px-2 py-1 text-xs font-bold rounded-full">
                  {{ getSignalDirectionText(signal.signal_type) }}
                </span>
                <!-- 詳細信號類型 -->
                <span class="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-full">
                  {{ getSignalTypeText(signal.signal_type) }}
                </span>
              </div>
              <div class="flex items-center space-x-1">
                <!-- 緊急度標示 -->
                <span v-if="signal.urgency_level === 'urgent'"
                  class="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                <span v-else-if="signal.urgency_level === 'high'" class="w-2 h-2 bg-orange-500 rounded-full"></span>
                <span v-else class="w-2 h-2 bg-yellow-500 rounded-full"></span>
                <!-- 時間框架 -->
                <span class="text-xs text-gray-500 font-medium">{{ signal.primary_timeframe }}</span>
              </div>
            </div>

            <!-- 價格信息 -->
            <div class="grid grid-cols-2 gap-2 mb-3 text-sm">
              <div class="bg-blue-50 p-2 rounded">
                <div class="text-xs text-gray-500">進場價</div>
                <div class="font-bold text-blue-600">${{ signal.entry_price?.toFixed(4) || 'N/A' }}</div>
              </div>
              <div class="bg-gray-50 p-2 rounded">
                <div class="text-xs text-gray-500">當前價
                  <span v-if="priceUpdateTime" class="text-green-600">({{ priceUpdateTime }})</span>
                </div>
                <div class="font-bold" :class="{
                  'text-green-600': signal.price_change_percent && signal.price_change_percent > 0,
                  'text-red-600': signal.price_change_percent && signal.price_change_percent < 0,
                  'text-gray-800': !signal.price_change_percent
                }">
                  ${{ signal.current_price?.toFixed(4) || 'N/A' }}
                  <span v-if="signal.price_change_percent" class="text-xs ml-1">
                    ({{ signal.price_change_percent > 0 ? '+' : '' }}{{ signal.price_change_percent.toFixed(2) }}%)
                  </span>
                </div>
              </div>
            </div>

            <!-- 信心度條 -->
            <div class="mb-3">
              <div class="flex justify-between items-center mb-1">
                <span class="text-xs text-gray-500">信心度</span>
                <span class="text-xs font-bold">{{ Math.round(signal.confidence * 100) }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div :style="{ width: (signal.confidence * 100) + '%' }" :class="{
                  'bg-green-500': signal.confidence >= 0.8,
                  'bg-yellow-500': signal.confidence >= 0.6,
                  'bg-red-500': signal.confidence < 0.6
                }" class="h-2 rounded-full transition-all duration-500"></div>
              </div>
            </div>

            <!-- 信號來源和策略 -->
            <div class="mb-3 flex items-center justify-between">
              <span v-if="signal.is_scalping"
                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                🔥 專用短線
              </span>
              <span v-else
                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                📊 中長線篩選
              </span>
              <span v-if="signal.strategy_name" class="text-xs text-gray-600 font-medium">
                {{ signal.strategy_name }}
              </span>
            </div>

            <!-- 技術指標詳情 -->
            <div v-if="signal.key_indicators || signal.is_scalping" class="mb-3 p-2 bg-gray-50 rounded">
              <div class="text-xs font-medium text-gray-700 mb-2">📊 技術指標</div>

              <!-- 短線專用指標 -->
              <div v-if="signal.is_scalping" class="grid grid-cols-2 gap-2 text-xs">
                <div class="bg-white p-2 rounded border">
                  <div class="text-gray-500">策略類型</div>
                  <div class="font-medium text-blue-600">{{ getSignalTypeText(signal.signal_type) }}</div>
                </div>
                <div class="bg-white p-2 rounded border">
                  <div class="text-gray-500">風險回報</div>
                  <div class="font-medium" :class="{
                    'text-green-600': (signal.risk_reward_ratio || 0) >= 2,
                    'text-yellow-600': (signal.risk_reward_ratio || 0) >= 1.5,
                    'text-red-600': (signal.risk_reward_ratio || 0) < 1.5
                  }">1:{{ signal.risk_reward_ratio?.toFixed(1) || 'N/A' }}</div>
                </div>

                <!-- 真實技術指標 -->
                <div class="bg-white p-2 rounded border">
                  <div class="text-gray-500">RSI (7)</div>
                  <div class="font-medium" :class="{
                    'text-red-600': (signal.key_indicators?.rsi_7 || 50) > 70,
                    'text-green-600': (signal.key_indicators?.rsi_7 || 50) < 30,
                    'text-gray-600': (signal.key_indicators?.rsi_7 || 50) >= 30 && (signal.key_indicators?.rsi_7 || 50) <= 70
                  }">{{ signal.key_indicators?.rsi_7?.toFixed(1) || '50.0' }}</div>
                </div>
                <div class="bg-white p-2 rounded border">
                  <div class="text-gray-500">EMA偏離</div>
                  <div class="font-medium" :class="{
                    'text-green-600': (signal.key_indicators?.ema_deviation || 0) > 0,
                    'text-red-600': (signal.key_indicators?.ema_deviation || 0) < 0
                  }">{{ (signal.key_indicators?.ema_deviation || 0) > 0 ? '+' : '' }}{{
                    signal.key_indicators?.ema_deviation?.toFixed(2) || '0.00' }}%</div>
                </div>
                <div class="bg-white p-2 rounded border">
                  <div class="text-gray-500">成交量比</div>
                  <div class="font-medium" :class="{
                    'text-orange-600': (signal.key_indicators?.volume_ratio || 1) > 2,
                    'text-blue-600': (signal.key_indicators?.volume_ratio || 1) > 1.5,
                    'text-gray-600': (signal.key_indicators?.volume_ratio || 1) <= 1.5
                  }">{{ signal.key_indicators?.volume_ratio?.toFixed(1) || '1.0' }}x</div>
                </div>
                <div class="bg-white p-2 rounded border">
                  <div class="text-gray-500">ATR %</div>
                  <div class="font-medium text-purple-600">{{ signal.key_indicators?.atr_percent?.toFixed(2) || '0.00'
                  }}%</div>
                </div>

                <!-- 擴展顯示更多指標 -->
                <div v-if="signal.key_indicators?.vwap_deviation !== undefined" class="bg-white p-2 rounded border">
                  <div class="text-gray-500">VWAP偏離</div>
                  <div class="font-medium" :class="{
                    'text-blue-600': Math.abs(signal.key_indicators.vwap_deviation) > 0.5,
                    'text-gray-600': Math.abs(signal.key_indicators.vwap_deviation) <= 0.5
                  }">{{ signal.key_indicators.vwap_deviation > 0 ? '+' : '' }}{{
                    signal.key_indicators.vwap_deviation.toFixed(2) }}%</div>
                </div>
                <div v-if="signal.key_indicators?.stoch_k !== undefined" class="bg-white p-2 rounded border">
                  <div class="text-gray-500">Stoch %K</div>
                  <div class="font-medium" :class="{
                    'text-red-600': signal.key_indicators.stoch_k > 80,
                    'text-green-600': signal.key_indicators.stoch_k < 20,
                    'text-gray-600': signal.key_indicators.stoch_k >= 20 && signal.key_indicators.stoch_k <= 80
                  }">{{ signal.key_indicators.stoch_k.toFixed(1) }}</div>
                </div>
              </div>

              <!-- 常規指標 -->
              <div v-else-if="signal.key_indicators" class="text-xs">
                <div v-for="(value, key) in signal.key_indicators" :key="key" class="flex justify-between py-1">
                  <span class="text-gray-500">{{ key }}:</span>
                  <span class="font-medium">{{ value }}</span>
                </div>
              </div>
            </div>

            <!-- 時效性倒計時 -->
            <div class="mb-3">
              <div class="flex justify-between items-center">
                <span class="text-xs text-gray-500">剩餘時效</span>
                <span :class="{
                  'text-red-600': getShortTermValidity(signal).percentage <= 30,
                  'text-orange-600': getShortTermValidity(signal).percentage <= 60,
                  'text-green-600': getShortTermValidity(signal).percentage > 60
                }" class="text-xs font-bold">
                  {{ getShortTermValidity(signal).text }}
                </span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-1 mt-1">
                <div :style="{ width: getShortTermValidity(signal).percentage + '%' }" :class="{
                  'bg-red-500': getShortTermValidity(signal).percentage <= 30,
                  'bg-orange-500': getShortTermValidity(signal).percentage <= 60,
                  'bg-green-500': getShortTermValidity(signal).percentage > 60
                }" class="h-1 rounded-full transition-all duration-300"></div>
              </div>
            </div>

            <!-- 快速操作按鈕 -->
            <div class="flex space-x-2">
              <button @click="executeQuickTrade(signal)" :disabled="getShortTermValidity(signal).percentage <= 10"
                class="flex-1 px-3 py-1 bg-orange-600 hover:bg-orange-700 disabled:bg-gray-300 text-white text-xs font-medium rounded transition-colors">
                快速執行
              </button>
              <button @click="viewShortTermDetail(signal)"
                class="px-3 py-1 border border-orange-600 text-orange-600 hover:bg-orange-50 text-xs font-medium rounded transition-colors">
                詳情
              </button>
            </div>
          </div>
        </div>

        <!-- 無短線信號時的提示 -->
        <div v-else class="text-center py-8">
          <div class="text-gray-400 mb-2">
            <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <p class="text-gray-500">目前沒有短線交易信號</p>
          <p class="text-xs text-gray-400 mt-1">系統正在掃描15分鐘內的交易機會</p>
        </div>
      </div>



      <!-- 最新交易信號 - 增強版本 -->
      <div class="mb-8 bg-white shadow rounded-lg p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-semibold text-gray-900">🎯 中長線交易信號分析</h2>

          <!-- 信號設置和狀態 -->
          <div class="flex items-center space-x-4">
            <!-- 新信號計數 -->
            <div v-if="newSignalIds.size > 0"
              class="flex items-center space-x-2 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
              <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              <span class="font-medium">{{ newSignalIds.size }} 個新信號</span>
            </div>

            <!-- 信號歷史按鈕 -->
            <button @click="navigateToSignalHistory"
              class="flex items-center space-x-2 px-3 py-1 text-sm bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-md transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <span>信號歷史 ({{ savedSignalsHistory.length }})</span>
            </button>

            <!-- 音效通知切換 -->
            <div class="flex items-center space-x-2">
              <label class="text-sm text-gray-600">音效通知</label>
              <input v-model="soundNotificationEnabled" type="checkbox"
                class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500">
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
              <select v-model="selectedCategory"
                class="text-sm border border-gray-300 rounded px-3 py-1 focus:ring-2 focus:ring-blue-500">
                <option value="ALL">所有幣種</option>
                <option v-for="(category, symbol) in signalCategories" :key="symbol" :value="symbol">
                  {{ category.name }} ({{ category.count }})
                </option>
              </select>

              <!-- 清除歷史按鈕 -->
              <button @click="clearSignalHistory(selectedCategory)"
                class="text-sm px-3 py-1 bg-red-100 hover:bg-red-200 text-red-700 rounded transition-colors">
                清除歷史
              </button>

              <!-- 關閉按鈕 -->
              <button @click="showSignalHistory = false" class="text-gray-500 hover:text-gray-700">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
          </div>

          <!-- 歷史信號列表 -->
          <div class="max-h-96 overflow-y-auto space-y-3">
            <div v-for="signal in getFilteredSignalHistory().slice(0, 20)" :key="`history-${signal.id}`"
              class="bg-white p-4 rounded border-l-4" :class="{
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
                      'bg-green-100 text-green-800': getSignalDirection(signal.signal_type) === 'LONG',
                      'bg-red-100 text-red-800': getSignalDirection(signal.signal_type) === 'SHORT'
                    }" class="px-2 py-1 text-xs rounded-full">
                      {{ getSignalDirectionText(signal.signal_type) }}
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
          <div v-for="signal in latestSignals" :key="signal.id" :class="[
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
            <div class="flex items-center justify-between p-6 cursor-pointer" @click="toggleSignalExpansion(signal.id)">
              <div class="flex items-center space-x-3">
                <h3 :class="[
                  'text-xl font-bold',
                  newSignalIds.has(signal.id) ? 'text-green-700' : 'text-gray-900'
                ]">{{ signal.symbol }}</h3>
                <span :class="{
                  'bg-green-100 text-green-800 border-green-200': getSignalDirection(signal.signal_type) === 'LONG',
                  'bg-red-100 text-red-800 border-red-200': getSignalDirection(signal.signal_type) === 'SHORT',
                  'bg-gray-100 text-gray-800 border-gray-200': getSignalDirection(signal.signal_type) === 'UNKNOWN'
                }" class="inline-flex px-3 py-1 text-sm font-semibold rounded-full border">
                  {{ getSignalDirectionText(signal.signal_type) }}
                </span>

                <!-- 置信度顯示 -->
                <div class="flex items-center space-x-2">
                  <div class="w-20 bg-gray-200 rounded-full h-2">
                    <div :style="{ width: (signal.confidence * 100) + '%' }" :class="{
                      'bg-green-500': signal.confidence >= 0.8,
                      'bg-yellow-500': signal.confidence >= 0.6,
                      'bg-red-500': signal.confidence < 0.6
                    }" class="h-2 rounded-full"></div>
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
                <svg :class="expandedSignals.has(signal.id) ? 'rotate-180' : ''"
                  class="w-5 h-5 text-gray-400 transition-transform duration-200" fill="none" stroke="currentColor"
                  viewBox="0 0 24 24">
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

                <div class="text-center p-2 rounded text-sm" :class="getTimeValidityStyle(signal)">
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
            <div :style="{ color: calculateMarketSentiment().color }" class="font-semibold text-lg">
              {{ calculateMarketSentiment().text }}
            </div>
            <div class="text-sm text-gray-500">
              (平均漲跌: {{realtimeUpdates.length > 0 ?
                (realtimeUpdates.reduce((sum, update) => sum + update.change_24h, 0) / realtimeUpdates.length).toFixed(2)
                + '%' :
                '0.00%'}})
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
                <span :style="{ color: update.color }" class="text-sm font-semibold">
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
            <button @click="isLogExpanded = !isLogExpanded"
              class="flex items-center space-x-2 px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-md transition-colors">
              <svg :class="isLogExpanded ? 'rotate-180' : ''" class="w-4 h-4 transition-transform duration-300"
                fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
              </svg>
              <span>{{ isLogExpanded ? '收縮' : '展開' }}({{ databaseLogs.length }}筆)</span>
            </button>

            <!-- 狀態指示器 -->
            <div class="flex items-center space-x-2">
              <div :class="isLogRefreshing ? 'animate-pulse bg-green-400 shadow-lg' : 'bg-green-500'"
                class="w-2 h-2 rounded-full transition-all duration-300"></div>
              <span :class="isLogRefreshing ? 'text-blue-600 font-medium' : 'text-gray-500'"
                class="text-sm transition-all duration-300">
                {{ isLogRefreshing ? '正在更新...' : '每5秒更新' }}
              </span>
              <div v-if="isLogRefreshing" class="inline-flex items-center text-xs text-blue-500 animate-pulse">
                <svg class="w-3 h-3 mr-1 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15">
                  </path>
                </svg>
                更新中
              </div>
            </div>
          </div>
        </div>

        <!-- 日誌區域 - 可展開至20筆記錄 -->
        <div :class="[
          isLogRefreshing ? 'animate-pulse bg-blue-50' : 'bg-gray-50',
          isLogExpanded ? 'max-h-96' : 'max-h-64'
        ]" class="space-y-2 overflow-y-auto rounded-md p-4 transition-all duration-300">
          <div v-for="log in databaseLogs" :key="log.timestamp + log.message" :class="[
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
              <div :class="isLogRefreshing ? 'text-blue-600 font-semibold' : 'text-gray-400'"
                class="text-xs mb-1 transition-all duration-200">
                🕒 {{ formatFullTime(log.timestamp) }}
              </div>
              <!-- 日誌訊息 -->
              <div :style="{ color: log.color }" :class="isLogRefreshing ? 'font-semibold' : ''"
                class="text-sm transition-all duration-200">
                {{ log.message }}
              </div>
            </div>
            <div :class="[
              'text-xs px-2 py-1 rounded-full text-center min-w-12 transition-all duration-200',
              isLogRefreshing ? 'font-semibold' : '',
              {
                'bg-green-100 text-green-700': log.type === 'success',
                'bg-blue-100 text-blue-700': log.type === 'info',
                'bg-yellow-100 text-yellow-700': log.type === 'warning',
                'bg-red-100 text-red-700': log.type === 'error',
                'bg-gray-100 text-gray-700': log.type === 'debug'
              }
            ]">
              {{ log.type.toUpperCase() }}
            </div>
          </div>

          <div v-if="databaseLogs.length === 0" class="text-center text-gray-500 py-8">
            <div :class="isLogRefreshing ? 'animate-spin' : ''" class="inline-block w-6 h-6 mb-2">
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
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
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
  // 短線信號專用字段
  is_scalping?: boolean
  strategy_name?: string
  scalping_type?: string
  signal_strength?: number
  key_indicators?: Record<string, any>
  expires_at?: string
  price_change_percent?: number
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
const previousSignalsMap = ref<Map<string, Signal>>(new Map())

// 使用者設置
const soundNotificationEnabled = ref(true)

// 短線信號分析相關數據
const shortTermStats = reactive({
  totalSignals: 0,
  avgConfidence: 0,
  urgentCount: 0,
  strategiesUsed: 0
})

const shortTermFilter = reactive({
  timeframe: 'all',
  urgency: 'all',
  confidence: 'all'
})

// 短線信號列表（包含原始短線專用信號）
const shortTermSignals = ref<Signal[]>([])
const rawScalpingSignals = ref<any[]>([]) // 原始短線專用信號

// 短線信號暫存機制
const scalpingSignalsCache = ref({
  data: [] as any[],
  timestamp: 0,
  expireTime: 3 * 60 * 1000 // 3分鐘過期時間
})

// 從localStorage載入短線信號暫存
const loadScalpingSignalsCache = () => {
  try {
    const saved = localStorage.getItem('tradingx_scalping_signals_cache')
    if (saved) {
      const parsed = JSON.parse(saved)
      const now = Date.now()
      const cacheAge = now - parsed.timestamp

      // 如果暫存未過期，則載入
      if (cacheAge < parsed.expireTime) {
        scalpingSignalsCache.value = parsed
        console.log(`載入短線信號暫存 (${Math.round(cacheAge / 1000)}秒前)`)
      } else {
        console.log('短線信號暫存已過期，清除localStorage')
        localStorage.removeItem('tradingx_scalping_signals_cache')
      }
    }
  } catch (error) {
    console.error('載入短線信號暫存失敗:', error)
    localStorage.removeItem('tradingx_scalping_signals_cache')
  }
}

// 保存短線信號暫存到localStorage
const saveScalpingSignalsCache = () => {
  try {
    localStorage.setItem('tradingx_scalping_signals_cache', JSON.stringify(scalpingSignalsCache.value))
  } catch (error) {
    console.error('保存短線信號暫存失敗:', error)
  }
}

// 即時價格數據
const realtimePrices = ref<Record<string, any>>({})
const priceUpdateTime = ref<string>('')

// 計算過濾後的短線信號
const filteredShortTermSignals = computed(() => {
  let filtered = shortTermSignals.value

  // 時間框架篩選
  if (shortTermFilter.timeframe !== 'all') {
    filtered = filtered.filter(signal => signal.primary_timeframe === shortTermFilter.timeframe)
  }

  // 緊急度篩選
  if (shortTermFilter.urgency !== 'all') {
    filtered = filtered.filter(signal => signal.urgency_level === shortTermFilter.urgency)
  }

  // 信心度篩選 (激進模式：調整門檻)
  if (shortTermFilter.confidence !== 'all') {
    filtered = filtered.filter(signal => {
      if (shortTermFilter.confidence === 'high') return signal.confidence >= 0.7   // 從0.8降到0.7
      if (shortTermFilter.confidence === 'medium') return signal.confidence >= 0.5 && signal.confidence < 0.7  // 從0.6降到0.5
      if (shortTermFilter.confidence === 'low') return signal.confidence < 0.5     // 從0.6降到0.5
      return true
    })
  }

  // 強化同幣種去重：不論方向，每個幣種只保留信心度最高的一個信號
  const deduplicatedSignals = new Map<string, Signal>()
  const duplicateCount = new Map<string, number>()

  filtered.forEach(signal => {
    // 創建去重鍵：只用幣種，不分方向
    const deduplicationKey = signal.symbol

    // 計數重複信號
    duplicateCount.set(deduplicationKey, (duplicateCount.get(deduplicationKey) || 0) + 1)

    // 如果該鍵不存在，或當前信號信心度更高，則保留當前信號
    const existingSignal = deduplicatedSignals.get(deduplicationKey)
    if (!existingSignal || signal.confidence > existingSignal.confidence) {
      deduplicatedSignals.set(deduplicationKey, signal)
    }
  })

  // 記錄去重統計
  const totalDuplicates = Array.from(duplicateCount.values()).reduce((sum, count) => sum + Math.max(0, count - 1), 0)
  if (totalDuplicates > 0) {
    console.log(`短線信號去重: 移除了 ${totalDuplicates} 個重複信號`)
    duplicateCount.forEach((count, key) => {
      if (count > 1) {
        const selectedSignal = deduplicatedSignals.get(key)
        console.log(`  ${key}: ${count} 個信號 → 保留 1 個最高信心度 (${selectedSignal ? (selectedSignal.confidence * 100).toFixed(1) : '未知'}% ${selectedSignal?.signal_type || '未知'})`)
      }
    })
  }  // 將去重後的信號轉回陣列
  const uniqueSignals = Array.from(deduplicatedSignals.values())

  // 激進模式排序：優先級 > 時效性 > 信心度
  const sorted = uniqueSignals.sort((a, b) => {
    // 1. 優先級排序 (urgent > high > medium > 無)
    const urgencyPriority: Record<string, number> = { 'urgent': 4, 'high': 3, 'medium': 2 }
    const aPriority = urgencyPriority[a.urgency_level || ''] || 1
    const bPriority = urgencyPriority[b.urgency_level || ''] || 1
    if (aPriority !== bPriority) return bPriority - aPriority

    // 2. 時效性排序 (較新的信號優先)
    if (a.created_at && b.created_at) {
      const aTime = new Date(a.created_at).getTime()
      const bTime = new Date(b.created_at).getTime()
      if (aTime !== bTime) return bTime - aTime
    }

    // 3. 信心度排序
    return b.confidence - a.confidence
  })

  return sorted.slice(0, 12) // 激進模式：增加到12個短線信號 (原來9個)
})

// 路由
const router = useRouter()

// 跳轉到信號歷史頁面
const navigateToSignalHistory = () => {
  router.push({ name: 'SignalHistory' })
}

// 獲取即時幣安價格
const fetchRealtimePrices = async () => {
  try {
    const symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT'] // 只包含指定的5個幣種
    const response = await axios.get('/api/v1/scalping/prices', {
      params: { symbols },
      timeout: 5000
    })

    if (response.data && response.data.prices) {
      realtimePrices.value = response.data.prices
      priceUpdateTime.value = new Date().toLocaleTimeString()

      // 更新短線信號中的當前價格
      updateCurrentPricesInSignals()

      console.log(`更新即時價格: ${Object.keys(realtimePrices.value).length} 個交易對`)
    }

  } catch (error) {
    console.error('獲取即時價格失敗:', error)
  }
}

// 更新短線信號中的當前價格（包括暫存）
const updateCurrentPricesInSignals = () => {
  // 更新展示中的信號
  shortTermSignals.value.forEach(signal => {
    const priceData = realtimePrices.value[signal.symbol]
    if (priceData && priceData.price) {
      signal.current_price = priceData.price

      // 計算價格變動百分比
      if (signal.entry_price) {
        const changePercent = ((priceData.price - signal.entry_price) / signal.entry_price * 100)
        signal.price_change_percent = changePercent
      }
    }
  })

  // 同時更新暫存中的價格信息
  if (scalpingSignalsCache.value.data.length > 0) {
    scalpingSignalsCache.value.data.forEach(signal => {
      const priceData = realtimePrices.value[signal.symbol]
      if (priceData && priceData.price) {
        signal.current_price = priceData.price

        // 計算價格變動百分比
        if (signal.entry_price) {
          const changePercent = ((priceData.price - signal.entry_price) / signal.entry_price * 100)
          signal.price_change_percent = changePercent
        }
      }
    })

    // 更新暫存時間戳，但不改變過期時間
    scalpingSignalsCache.value.timestamp = Date.now()

    // 重新保存到localStorage
    saveScalpingSignalsCache()
  }
}
const fetchScalpingSignals = async (): Promise<any[]> => {
  try {
    // 檢查暫存是否有效
    const now = Date.now()
    const cacheAge = now - scalpingSignalsCache.value.timestamp

    // 如果暫存存在且未過期，直接返回暫存數據
    if (scalpingSignalsCache.value.data.length > 0 && cacheAge < scalpingSignalsCache.value.expireTime) {
      console.log(`使用暫存的短線信號 (${Math.round(cacheAge / 1000)}秒前)，剩餘 ${Math.round((scalpingSignalsCache.value.expireTime - cacheAge) / 1000)}秒過期`)
      return scalpingSignalsCache.value.data
    }

    console.log('暫存已過期或無效，重新獲取短線信號...')

    const response = await axios.get('/api/v1/scalping/signals', {
      params: {
        symbols: ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT'], // 只包含指定的5個幣種
        timeframes: ['1m', '3m', '5m', '15m', '30m'],
        min_confidence: 0.85, // 提升至85%信心度 (牛市精選)
        urgency_levels: ['urgent', 'high', 'medium'],
        market_condition: 'bull', // 牛市環境
        risk_level: 'conservative' // 縮小止盈止損區間
      },
      timeout: 8000
    })

    rawScalpingSignals.value = response.data || []
    console.log(`獲取到 ${rawScalpingSignals.value.length} 個專用短線信號`)

    // 轉換為通用Signal格式以便在UI中顯示
    const convertedSignals = rawScalpingSignals.value.map(signal => {
      const convertedSignal: Signal = {
        id: signal.id,
        symbol: signal.symbol,
        primary_timeframe: signal.primary_timeframe,
        confirmed_timeframes: signal.confirmed_timeframes || [signal.primary_timeframe],
        signal_type: signal.signal_type,
        confidence: signal.confidence,
        signal_strength: signal.signal_strength || signal.confidence,
        urgency_level: signal.urgency_level,
        entry_price: signal.entry_price,
        stop_loss: signal.stop_loss,
        take_profit: signal.take_profit,
        risk_reward_ratio: signal.risk_reward_ratio,
        reasoning: signal.reasoning || `${signal.strategy_name} - ${signal.scalping_type}`,
        created_at: signal.created_at,
        expires_at: signal.expires_at,
        key_indicators: signal.key_indicators || {},
        strategy_name: signal.strategy_name,
        is_scalping: true
      }

      // 從即時價格中獲取當前價格
      const priceData = realtimePrices.value[signal.symbol]
      if (priceData && priceData.price) {
        convertedSignal.current_price = priceData.price

        // 計算價格變動百分比
        if (signal.entry_price) {
          const changePercent = ((priceData.price - signal.entry_price) / signal.entry_price * 100)
          convertedSignal.price_change_percent = changePercent
        }
      }

      return convertedSignal
    })

    // 更新暫存（包含當前價格信息）
    scalpingSignalsCache.value = {
      data: convertedSignals,
      timestamp: now,
      expireTime: 3 * 60 * 1000 // 3分鐘過期
    }

    // 保存到localStorage
    saveScalpingSignalsCache()

    console.log(`短線信號已暫存，3分鐘後過期`)
    return convertedSignals

  } catch (error) {
    console.error('獲取短線信號失敗:', error)
    rawScalpingSignals.value = []

    // 如果API失敗但有暫存數據，則返回暫存數據
    if (scalpingSignalsCache.value.data.length > 0) {
      console.log('API失敗，使用暫存的短線信號數據')
      return scalpingSignalsCache.value.data
    }

    return []
  }
}

// 清除短線信號暫存（強制刷新）
const clearScalpingSignalsCache = () => {
  scalpingSignalsCache.value = {
    data: [],
    timestamp: 0,
    expireTime: 3 * 60 * 1000
  }

  // 同時清除localStorage
  localStorage.removeItem('tradingx_scalping_signals_cache')
  console.log('短線信號暫存已清除')
}

// 短線信號相關函數 - 激進模式（混合中長線篩選和專用短線信號）
const updateShortTermSignals = async () => {
  try {
    // 1. 從中長線信號中篩選短線適用的信號
    const aggressiveTimeframes = ['1m', '3m', '5m', '15m', '30m']
    const filteredFromGeneral = latestSignals.value.filter(signal => {
      const hasShortTimeframe = aggressiveTimeframes.includes(signal.primary_timeframe || '') ||
        (signal.confirmed_timeframes && signal.confirmed_timeframes.some(tf => aggressiveTimeframes.includes(tf)))

      const hasDecentConfidence = signal.confidence >= 0.5
      const isRecentEnough = isSignalRecentEnough(signal, 120) // 2小時

      const isHighPriority = signal.urgency_level && ['urgent', 'high'].includes(signal.urgency_level)
      const isMediumPriority = signal.urgency_level === 'medium'

      return hasShortTimeframe && isRecentEnough && (
        (isHighPriority && hasDecentConfidence) ||
        (isMediumPriority && signal.confidence >= 0.65) ||
        (!signal.urgency_level && signal.confidence >= 0.7)
      )
    })

    // 2. 獲取專用短線信號
    const scalpingSignals = await fetchScalpingSignals()

    // 2.1 同時獲取即時價格
    await fetchRealtimePrices()

    // 3. 合併兩種信號，基於幣種去重（不分方向），保留信心度最高的信號
    const allShortSignals = [...scalpingSignals, ...filteredFromGeneral]
    const uniqueSignals = new Map()

    // 基於幣種去重，每個幣種只保留信心度最高的一個信號
    allShortSignals.forEach(signal => {
      const key = signal.symbol
      const existingSignal = uniqueSignals.get(key)

      // 如果該鍵不存在，或當前信號信心度更高，或當前信號是專用短線信號且信心度相近，則保留當前信號
      if (!existingSignal ||
        signal.confidence > existingSignal.confidence ||
        (signal.is_scalping && !existingSignal.is_scalping && Math.abs(signal.confidence - existingSignal.confidence) < 0.1)) {
        uniqueSignals.set(key, signal)
      }
    })

    shortTermSignals.value = Array.from(uniqueSignals.values())

    // 更新統計數據
    const scalpingCount = shortTermSignals.value.filter(s => s.is_scalping).length
    const strategiesSet = new Set(shortTermSignals.value.map(s => s.strategy_name || 'Unknown'))

    shortTermStats.totalSignals = shortTermSignals.value.length
    shortTermStats.avgConfidence = shortTermSignals.value.length > 0
      ? Math.round(shortTermSignals.value.reduce((sum, signal) => sum + signal.confidence * 100, 0) / shortTermSignals.value.length)
      : 0
    shortTermStats.urgentCount = shortTermSignals.value.filter(signal =>
      ['urgent', 'high'].includes(signal.urgency_level || '')).length
    shortTermStats.strategiesUsed = strategiesSet.size

    console.log(`短線信號更新完成: 總計${shortTermStats.totalSignals}個 (專用短線${scalpingCount}個, 中長線篩選${shortTermStats.totalSignals - scalpingCount}個, ${shortTermStats.strategiesUsed}種策略)`)

  } catch (error) {
    console.error('短線信號更新失敗:', error)
    // 如果專用短線信號獲取失敗，至少保留中長線篩選的結果
    const aggressiveTimeframes = ['1m', '3m', '5m', '15m', '30m']
    shortTermSignals.value = latestSignals.value.filter(signal => {
      const hasShortTimeframe = aggressiveTimeframes.includes(signal.primary_timeframe || '')
      const hasDecentConfidence = signal.confidence >= 0.5
      return hasShortTimeframe && hasDecentConfidence
    })

    shortTermStats.totalSignals = shortTermSignals.value.length
    shortTermStats.avgConfidence = shortTermSignals.value.length > 0
      ? Math.round(shortTermSignals.value.reduce((sum, signal) => sum + signal.confidence * 100, 0) / shortTermSignals.value.length)
      : 0
  }
}// 檢查信號是否在指定時間內
const isSignalRecentEnough = (signal: Signal, maxMinutes: number): boolean => {
  if (!signal.created_at) return true // 如果沒有時間戳，假設是新信號

  try {
    const createdTime = new Date(signal.created_at)
    const now = new Date()
    const minutesElapsed = (now.getTime() - createdTime.getTime()) / (1000 * 60)
    return minutesElapsed <= maxMinutes
  } catch {
    return true
  }
}

const refreshShortTermSignals = async () => {
  // 清除短線信號暫存，強制重新獲取
  clearScalpingSignalsCache()

  await updateShortTermSignals()
  showNotification('success', '激進短線信號已刷新',
    `強制刷新完成！發現 ${shortTermStats.totalSignals} 個短線交易機會 (包含${shortTermStats.strategiesUsed}種策略)`)
}// 計算短線信號時效性 - 激進模式
const getShortTermValidity = (signal: Signal): { percentage: number; text: string } => {
  if (!signal.created_at) return { percentage: 100, text: '即時' }

  try {
    const createdTime = new Date(signal.created_at)
    const now = new Date()
    const minutesElapsed = (now.getTime() - createdTime.getTime()) / (1000 * 60)

    // 激進模式：大幅縮短有效期，更快速的交易決策
    let validityMinutes = 30 // 預設30分鐘（比原來的15分鐘長）
    if (signal.primary_timeframe === '1m') validityMinutes = 10  // 原來5分鐘 -> 10分鐘
    else if (signal.primary_timeframe === '3m') validityMinutes = 15  // 新增3分鐘框架
    else if (signal.primary_timeframe === '5m') validityMinutes = 20  // 原來10分鐘 -> 20分鐘
    else if (signal.primary_timeframe === '15m') validityMinutes = 45 // 原來15分鐘 -> 45分鐘
    else if (signal.primary_timeframe === '30m') validityMinutes = 90 // 新增30分鐘框架

    const remainingMinutes = Math.max(0, validityMinutes - minutesElapsed)
    const percentage = (remainingMinutes / validityMinutes) * 100

    let text = ''
    if (remainingMinutes > 30) {
      text = `${Math.round(remainingMinutes)}分鐘 (充裕)`
    } else if (remainingMinutes > 10) {
      text = `${Math.round(remainingMinutes)}分鐘 (適中)`
    } else if (remainingMinutes > 2) {
      text = `${Math.round(remainingMinutes)}分鐘 (緊急)`
    } else if (remainingMinutes > 0) {
      text = '即將過期'
    } else {
      text = '已過期'
    }

    return { percentage: Math.round(percentage), text }
  } catch (error) {
    return { percentage: 50, text: '計算錯誤' }
  }
}// 快速執行交易
const executeQuickTrade = (signal: Signal) => {
  const validity = getShortTermValidity(signal)
  if (validity.percentage <= 10) {
    showNotification('warning', '信號已過期', '此短線信號已過期，無法執行')
    return
  }

  // 這裡可以集成實際的交易執行邏輯
  showNotification('info', '快速交易', `正在執行 ${signal.symbol} ${signal.signal_type} 信號`)

  // 模擬交易執行
  console.log(`執行快速交易: ${signal.symbol} ${signal.signal_type} at ${signal.entry_price}`)
}

// 查看短線信號詳情
const viewShortTermDetail = (signal: Signal) => {
  // 暫時使用 alert，後續可以開發詳細的模態框
  const details = `
短線信號詳情:
幣種: ${signal.symbol}
類型: ${signal.signal_type}
時間框架: ${signal.primary_timeframe}
進場價格: $${signal.entry_price?.toFixed(4)}
止損價格: $${signal.stop_loss?.toFixed(4)}
止盈價格: $${signal.take_profit?.toFixed(4)}
信心度: ${Math.round(signal.confidence * 100)}%
緊急度: ${signal.urgency_level}
剩餘時效: ${getShortTermValidity(signal).text}
  `
  alert(details)
}

// 檢測新信號
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
}

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

  // 重要：立即從儀表板中移除已歷史化的信號
  latestSignals.value = latestSignals.value.filter(s => s.id !== signal.id)

  // 更新統計
  stats.activeSignals = latestSignals.value.length

  console.log(`信號 ${signal.symbol} 已保存到歷史記錄並從儀表板移除，原因: ${action}`)
}

// 計算信號結果
const calculateSignalResult = (signal: Signal): string => {
  if (!signal.current_price || !signal.entry_price) return '無法計算'

  const priceChange = signal.current_price - signal.entry_price
  const percentageChange = (priceChange / signal.entry_price) * 100
  const direction = getSignalDirection(signal.signal_type)

  if (direction === 'LONG') {
    return percentageChange > 0 ? `+${percentageChange.toFixed(2)}%` : `${percentageChange.toFixed(2)}%`
  } else if (direction === 'SHORT') {
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

// 智能信號刪除機制 - 增強版，包含成功失敗判定
const shouldDeleteSignal = (signal: Signal): { shouldDelete: boolean; reason: string; isSuccess: boolean } => {
  const now = new Date()

  // 1. 檢查時效性 - 超過24小時自動刪除
  if (signal.created_at) {
    const createdTime = new Date(signal.created_at)
    const hoursElapsed = (now.getTime() - createdTime.getTime()) / (1000 * 60 * 60)

    if (hoursElapsed > 24) {
      // 時效到期，根據收益判定成功失敗
      const currentProfit = calculateCurrentProfit(signal)
      return {
        shouldDelete: true,
        reason: '時效過期',
        isSuccess: currentProfit > 0
      }
    }
  }

  // 2. 檢查止損觸發
  if (signal.stop_loss && signal.current_price) {
    const direction = getSignalDirection(signal.signal_type)
    if ((direction === 'LONG' && signal.current_price <= signal.stop_loss) ||
      (direction === 'SHORT' && signal.current_price >= signal.stop_loss)) {
      return {
        shouldDelete: true,
        reason: '止損觸發',
        isSuccess: false
      }
    }
  }

  // 3. 檢查止盈觸發
  if (signal.take_profit && signal.current_price) {
    const direction = getSignalDirection(signal.signal_type)
    if ((direction === 'LONG' && signal.current_price >= signal.take_profit) ||
      (direction === 'SHORT' && signal.current_price <= signal.take_profit)) {
      return {
        shouldDelete: true,
        reason: '止盈觸發',
        isSuccess: true
      }
    }
  }

  // 4. 檢查價格偏離度 - 如果當前價格與進場價格偏離超過15%且是不利方向
  if (signal.current_price && signal.entry_price) {
    const priceDeviation = Math.abs(signal.current_price - signal.entry_price) / signal.entry_price
    const direction = getSignalDirection(signal.signal_type)

    if (priceDeviation > 0.15) {
      // 做多信號但價格大幅下跌，做空信號但價格大幅上漲
      if ((direction === 'LONG' && signal.current_price < signal.entry_price * 0.85) ||
        (direction === 'SHORT' && signal.current_price > signal.entry_price * 1.15)) {
        return {
          shouldDelete: true,
          reason: '價格超出區間',
          isSuccess: false
        }
      }
    }
  }

  // 5. 檢查信心度 - 低於20%的信號刪除
  if (signal.confidence < 0.2) {
    return {
      shouldDelete: true,
      reason: '信心度過低',
      isSuccess: false
    }
  }

  // 6. 檢查黑天鵝事件標記
  if (signal.market_context && signal.market_context.includes('黑天鵝')) {
    return {
      shouldDelete: true,
      reason: '黑天鵝事件影響',
      isSuccess: false
    }
  }

  // 7. 檢查突發變盤因素
  if (signal.market_context && signal.market_context.includes('突發變盤')) {
    return {
      shouldDelete: true,
      reason: '市場突發變盤',
      isSuccess: false
    }
  }

  // 8. 檢查技術指標失效
  if (signal.technical_confluence && signal.technical_confluence.length === 0) {
    return {
      shouldDelete: true,
      reason: '技術指標失效',
      isSuccess: false
    }
  }

  return { shouldDelete: false, reason: '', isSuccess: false }
}

// 確保信號分離：歷史記錄中的信號不會出現在儀表板
const ensureSignalSeparation = () => {
  // 載入最新的歷史記錄
  loadSignalHistory()

  // 獲取所有已歷史化的信號 ID
  const historicalSignalIds = new Set(savedSignalsHistory.value.map(s => s.id))

  // 從當前儀表板信號中移除已歷史化的信號
  const originalCount = latestSignals.value.length
  latestSignals.value = latestSignals.value.filter(signal => !historicalSignalIds.has(signal.id))

  const removedCount = originalCount - latestSignals.value.length
  if (removedCount > 0) {
    console.log(`信號分離完成: 從儀表板移除了 ${removedCount} 個已歷史化的信號`)
    // 更新統計
    stats.activeSignals = latestSignals.value.length
  }
}

// 模擬技術指標函數 (基於信號數據計算)
const getMockRSI = (signal: Signal): number => {
  // 基於信號類型和信心度模擬RSI值
  const direction = getSignalDirection(signal.signal_type)
  const base = direction === 'LONG' ? 35 : 65
  const variance = (signal.confidence - 0.5) * 40
  return Math.round(Math.max(10, Math.min(90, base + variance)))
}

const getMockEMADeviation = (signal: Signal): number => {
  // 基於當前價格和入場價格計算EMA偏離度
  if (!signal.current_price || !signal.entry_price) return 0
  const deviation = ((signal.current_price - signal.entry_price) / signal.entry_price * 100)
  return Number(deviation.toFixed(2))
}

const getMockVolumeRatio = (signal: Signal): number => {
  // 基於緊急程度模擬成交量比率
  const urgencyMultiplier = {
    'urgent': 3.5,
    'high': 2.2,
    'medium': 1.6
  }
  const base = urgencyMultiplier[signal.urgency_level as keyof typeof urgencyMultiplier] || 1.2
  const variance = (signal.confidence - 0.5) * 2
  return Number((base + variance).toFixed(1))
}

const getMockATR = (signal: Signal): number => {
  // 基於時間框架和信號強度模擬ATR
  const timeframeATR = {
    '1m': 0.15,
    '3m': 0.25,
    '5m': 0.35,
    '15m': 0.55,
    '30m': 0.85
  }
  const base = timeframeATR[signal.primary_timeframe as keyof typeof timeframeATR] || 0.4
  const variance = signal.confidence * 0.3
  return Number((base + variance).toFixed(2))
}

// 解析信號方向 (LONG/SHORT)
const getSignalDirection = (signalType: string): string => {
  if (!signalType) return 'UNKNOWN'

  const longTypes = ['SCALP_LONG', 'MOMENTUM_BREAKOUT', 'BUY', 'LONG']
  const shortTypes = ['SCALP_SHORT', 'MEAN_REVERSION', 'SELL', 'SHORT']

  if (longTypes.includes(signalType)) return 'LONG'
  if (shortTypes.includes(signalType)) return 'SHORT'

  return 'UNKNOWN'
}

// 獲取信號方向中文文字
const getSignalDirectionText = (signalType: string): string => {
  const direction = getSignalDirection(signalType)

  switch (direction) {
    case 'LONG':
      return '🚀 做多'
    case 'SHORT':
      return '📉 做空'
    default:
      return '❓ 未知'
  }
}

// 獲取詳細信號類型中文文字
const getSignalTypeText = (signalType: string): string => {
  const typeMap: { [key: string]: string } = {
    'SCALP_LONG': '短線多頭',
    'SCALP_SHORT': '短線空頭',
    'MOMENTUM_BREAKOUT': '動量突破',
    'MEAN_REVERSION': '均值回歸',
    'BUY': '買入',
    'SELL': '賣出',
    'LONG': '做多',
    'SHORT': '做空'
  }

  return typeMap[signalType] || signalType
}

// 計算當前收益
const calculateCurrentProfit = (signal: Signal): number => {
  if (!signal.current_price || !signal.entry_price) return 0

  const priceChange = signal.current_price - signal.entry_price
  const percentageChange = (priceChange / signal.entry_price) * 100

  const direction = getSignalDirection(signal.signal_type)

  if (direction === 'LONG') {
    return percentageChange  // 做多：價格上漲為正收益
  } else if (direction === 'SHORT') {
    return -percentageChange // 做空：價格下跌為正收益
  }

  return 0
}

// 過濾和管理信號 - 增強版
const filterValidSignals = (signals: Signal[]): Signal[] => {
  const validSignals: Signal[] = []
  const deletedSignals: Array<{ signal: Signal; reason: string; isSuccess: boolean }> = []

  signals.forEach(signal => {
    const deleteCheck = shouldDeleteSignal(signal)

    if (deleteCheck.shouldDelete) {
      deletedSignals.push({ signal, reason: deleteCheck.reason, isSuccess: deleteCheck.isSuccess })

      // 將銷毀的信號保存到歷史記錄，並標記是否成功
      const archiveReason = deleteCheck.reason === '時效過期' ? 'expired' :
        deleteCheck.reason === '止損觸發' ? 'stopped' :
          deleteCheck.reason === '止盈觸發' ? 'completed' :
            'archived'

      saveSignalToHistory(signal, archiveReason as 'completed' | 'expired' | 'stopped' | 'archived')

      // 可選：發送刪除通知
      if (deletedSignals.length <= 3) { // 避免過多通知
        const successText = deleteCheck.isSuccess ? '✅ 成功' : '❌ 失敗'
        showNotification('info', '信號已自動銷毀', `${signal.symbol} ${deleteCheck.reason} - ${successText}`)
      }
    } else {
      validSignals.push(signal)
    }
  })

  // 記錄刪除統計
  if (deletedSignals.length > 0) {
    const successCount = deletedSignals.filter(d => d.isSuccess).length
    const failureCount = deletedSignals.length - successCount
    console.log(`已銷毀 ${deletedSignals.length} 個信號: ${successCount} 成功, ${failureCount} 失敗`)
    console.log('銷毀詳情:', deletedSignals)
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

    // 並行獲取中長線信號和短線信號
    const [signalsResponse, scalpingResponse] = await Promise.all([
      axios.get('/api/v1/signals/latest?hours=24', { timeout: 10000 }),
      fetchScalpingSignals() // 獨立的短線信號調用
    ])

    // 處理中長線信號
    const rawSignals = signalsResponse.data || []
    let filteredSignals = filterValidSignals(rawSignals)

    // 重要：確保已進入歷史記錄的信號不會出現在儀表板
    // 載入歷史記錄以獲取已銷毀的信號 ID
    loadSignalHistory()
    const historicalSignalIds = new Set(savedSignalsHistory.value.map(s => s.id))

    // 過濾掉已經在歷史記錄中的信號
    filteredSignals = filteredSignals.filter(signal => !historicalSignalIds.has(signal.id))

    console.log(`中長線信號 - 原始: ${rawSignals.length}, 過濾後: ${filteredSignals.length}`)
    console.log(`短線信號數量: ${scalpingResponse ? scalpingResponse.length : 0}`)

    // 簡化的新信號檢測：檢查是否有新的信號 ID
    if (latestSignals.value.length > 0) {
      const existingIds = new Set(latestSignals.value.map(s => s.id))
      const newSignals = filteredSignals.filter(signal => !existingIds.has(signal.id))

      // 檢查已移除的信號並儲存到歷史
      const currentIds = new Set(filteredSignals.map(s => s.id))
      const removedSignals = latestSignals.value.filter(signal => !currentIds.has(signal.id))

      removedSignals.forEach(signal => {
        const deleteReason = shouldDeleteSignal(signal)
        const archiveReason = deleteReason.shouldDelete ?
          (deleteReason.reason === '時效過期' ? 'expired' :
            deleteReason.reason === '止損觸發' ? 'stopped' :
              deleteReason.reason === '止盈觸發' ? 'completed' : 'archived') : 'archived'

        saveSignalToHistory(signal, archiveReason as 'completed' | 'expired' | 'stopped' | 'archived')

        if (deleteReason.shouldDelete) {
          const successText = deleteReason.isSuccess ? '✅ 成功' : '❌ 失敗'
          console.log(`信號 ${signal.symbol} 已銷毀: ${deleteReason.reason} - ${successText}`)
        }
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

    // 更新短線信號
    updateShortTermSignals()

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
  // 載入短線信號暫存
  loadScalpingSignalsCache()

  // 初始載入
  checkServiceStatus()
  fetchDashboardData()
  fetchRealtimeUpdates()

  // 確保信號分離
  ensureSignalSeparation()

  // 設置定時更新信號數據 (激進模式：每15秒檢查新信號)
  updateInterval = setInterval(() => {
    fetchDashboardData()  // 改為載入信號數據來檢測新信號
  }, 15000) // 從30秒改為15秒，更激進的數據獲取

  // 設置系統日誌更新 (每3秒更新一次，原為5秒)
  logUpdateInterval = setInterval(() => {
    fetchRealtimeUpdates()
  }, 3000)

  // 每30秒檢查一次服務狀態 (原為60秒)
  setInterval(() => {
    checkServiceStatus()
  }, 30000)

  // 激進模式：每5秒檢查一次信號銷毀條件和信號分離 (原為10秒)
  setInterval(() => {
    if (latestSignals.value.length > 0) {
      const beforeCount = latestSignals.value.length

      // 首先應用銷毀邏輯
      let processedSignals = filterValidSignals(latestSignals.value)

      // 然後確保已在歷史記錄中的信號不會出現在儀表板
      const historicalSignalIds = new Set(savedSignalsHistory.value.map(s => s.id))
      processedSignals = processedSignals.filter(signal => !historicalSignalIds.has(signal.id))

      latestSignals.value = processedSignals
      const afterCount = latestSignals.value.length

      if (beforeCount !== afterCount) {
        // 更新統計數據
        stats.activeSignals = latestSignals.value.length
        // 異步更新短線信號
        updateShortTermSignals().catch(error => {
          console.error('短線信號更新失敗:', error)
        })
        console.log(`激進模式信號檢查完成: ${beforeCount} -> ${afterCount} (移除了 ${beforeCount - afterCount} 個信號)`)
      }
    }

    // 確保信號分離
    ensureSignalSeparation()
  }, 5000) // 激進模式：從10秒改為5秒

  // 激進模式：額外的短線信號專用更新間隔
  setInterval(async () => {
    try {
      await updateShortTermSignals()
      console.log('激進模式：短線信號更新完成（3分鐘間隔）')
    } catch (error) {
      console.error('短線信號更新失敗:', error)
    }
  }, 180000) // 每3分鐘更新短線信號 (180秒)

  // 牛市優化：價格更新（每30秒，減少不必要的頻繁更新）
  setInterval(async () => {
    try {
      await fetchRealtimePrices()
      console.log('牛市優化：價格更新完成')
    } catch (error) {
      console.error('價格更新失敗:', error)
    }
  }, 30000) // 每30秒更新價格 (牛市環境下降低更新頻率)
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
