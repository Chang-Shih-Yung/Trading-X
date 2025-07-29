<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <!-- Loading 覆蓋層 -->
    <LoadingOverlay :show="isLoading" :title="loadingMessage" message="請稍候..." />

    <!-- 自定義通知 -->
    <CustomNotification v-if="notification.show" :type="notification.type" :title="notification.title"
      :message="notification.message" @close="hideNotification" />

    <!-- 短線刷新確認彈窗 -->
    <ConfirmDialog v-model:show="showRefreshConfirm" title="確認刷新短線信號" message="您確定要強制刷新短線信號嗎？"
      :details="refreshConfirmDetails" confirm-text="確認刷新" cancel-text="取消" type="warning"
      @confirm="confirmRefreshShortTermSignals" @cancel="showRefreshConfirm = false" />

    <div class="mx-auto max-w-7xl">
      <!-- 標題 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Service X</h1>
        <p class="mt-2 text-gray-600">Trading Signals and Market Analysis</p>
      </div>

      <!-- 系統狀態 - 實時 API 服務狀態 -->
      <div class="mb-6 bg-white shadow rounded-lg p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">🚀 系統服務狀態</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <ServiceStatus :status="serviceStatus.market_data" label="市場數據服務" />
          <ServiceStatus :status="serviceStatus.strategy_engine" label="策略引擎" />
          <ServiceStatus :status="serviceStatus.backtest_service" label="回測服務" />
          <ServiceStatus :status="serviceStatus.database" label="資料庫" />
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
            <button @click="showRefreshConfirm = true"
              class="px-3 py-1 bg-orange-500 text-white rounded hover:bg-orange-600 text-sm">
              刷新短線
            </button>
            <button @click="printExpiredSignals"
              class="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-sm">
              打印過往累積過期信號
            </button>
            <button @click="navigateToShortTermHistory"
              class="flex items-center px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm">
              <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                  clip-rule="evenodd"></path>
              </svg>
              <span>短線歷史</span>
            </button>
          </div>
        </div>

        <!-- 短線信號卡片網格 -->
        <div v-if="filteredShortTermSignals.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="signal in filteredShortTermSignals" :key="`short-${signal.id}`"
            class="bg-white rounded-lg border-l-4 border-orange-400 p-4 shadow-sm hover:shadow-md transition-shadow">

            <!-- 信號標題行 -->
            <div class="flex justify-between items-center mb-3">
              <div class="flex items-center space-x-2">
                <h4 class="font-bold text-lg text-gray-900">{{ signal.symbol }}</h4>
                <!-- 💎 突破信號特殊標記 -->
                <span v-if="isBreakoutSignal(signal)"
                  class="px-2 py-1 text-xs font-bold bg-gradient-to-r from-yellow-400 to-orange-500 text-white rounded-full animate-pulse shadow-lg">
                  🚀 突破
                </span>
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
                <!-- 💎 動態止盈顯示 -->
                <span class="text-xs text-orange-600 font-bold bg-orange-50 px-2 py-1 rounded">
                  目標: {{ calculateDynamicStopProfit(signal).toFixed(1) }}%
                </span>
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
                <!-- 價格偏離風險警示 -->
                <div v-if="signal.current_price && signal.entry_price" class="mt-1">
                  <span v-if="signal.price_deviation_risk"
                    :class="getPriceDeviationBadgeClass(signal.price_deviation_risk.level)"
                    class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium">
                    {{ signal.price_deviation_risk.warning }}
                  </span>
                  <span v-else :class="getPriceDeviationBadgeClass(calculatePriceDeviationRisk(signal).level)"
                    class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium">
                    {{ calculatePriceDeviationRisk(signal).warning }}
                  </span>
                </div>

                <!-- 市場條件影響評級 -->
                <div v-if="signal.market_condition_impact" class="mt-1">
                  <StatusBadge type="status" :value="signal.market_condition_impact.overall_rating"
                    :text="`${signal.market_condition_impact.rating_text} - ${signal.market_condition_impact.condition_text}`" />
                </div>
              </div>
            </div>

            <!-- 信心度數字顯示 - 替代長條圖 -->
            <div class="mb-3 flex justify-between items-center">
              <span class="text-xs text-gray-500">信心度</span>
              <StatusBadge type="confidence" :value="Math.round(signal.confidence * 100)"
                :text="`${Math.round(signal.confidence * 100)}%`" />
            </div>

            <!-- 信號來源和策略 -->
            <div class="mb-3 flex items-center justify-between">
              <StatusBadge v-if="signal.is_scalping" type="strategy" value="scalping" text="🔥 專用短線" icon="🔥" />
              <StatusBadge v-else type="strategy" value="swing" text="📊 中長線篩選" icon="📊" />
              <span v-if="signal.strategy_name" class="text-xs text-gray-600 font-medium">
                {{ signal.strategy_name }}
              </span>
            </div>

            <!-- 技術指標詳情 - 可收合 -->
            <div v-if="signal.key_indicators || signal.is_scalping" class="mb-3">
              <button @click="toggleIndicatorExpansion(signal.id)"
                class="w-full flex items-center justify-between p-2 bg-gray-50 rounded hover:bg-gray-100 transition-colors">
                <div class="text-xs font-medium text-gray-700">📊 技術指標</div>
                <svg :class="expandedIndicators.has(signal.id) ? 'rotate-180' : ''"
                  class="w-4 h-4 text-gray-400 transition-transform duration-200" fill="none" stroke="currentColor"
                  viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </button>

              <!-- 收合的技術指標內容 -->
              <div v-if="expandedIndicators.has(signal.id)" class="mt-2 p-2 bg-gray-50 rounded">
                <!-- 短線專用指標 -->
                <div v-if="signal.is_scalping" class="grid grid-cols-2 gap-2 text-xs">
                  <div class="bg-white p-2 rounded border">
                    <div class="text-gray-500">策略類型</div>
                    <div class="font-medium text-blue-600">{{ getSignalTypeText(signal.signal_type) }}</div>
                  </div>
                  <div class="bg-white p-2 rounded border">
                    <div class="text-gray-500">風險回報</div>
                    <StatusBadge type="risk" :value="signal.risk_reward_ratio || 0"
                      :text="`1:${signal.risk_reward_ratio?.toFixed(1) || 'N/A'}`" />
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
            </div>

            <!-- 信號狀態與剩餘時間 -->
            <div class="mb-3">
              <div class="flex justify-between items-center">
                <span class="text-xs text-gray-500">信號狀態</span>
                <span :class="{
                  'text-red-600': signal.validity_info?.status === 'expired',
                  'text-orange-600': signal.validity_info?.status === 'expiring',
                  'text-yellow-600': signal.validity_info?.status === 'valid',
                  'text-green-600': signal.validity_info?.status === 'fresh'
                }" class="text-xs font-bold">
                  {{ getSignalStatusText(signal) }}
                </span>
              </div>

              <!-- 剩餘時間顯示 -->
              <div class="flex justify-between items-center mt-1">
                <span class="text-xs text-gray-500">剩餘時間</span>
                <span :class="{
                  'text-red-600': (signal.remaining_time_minutes || 0) <= 2,
                  'text-orange-600': (signal.remaining_time_minutes || 0) <= 5,
                  'text-yellow-600': (signal.remaining_time_minutes || 0) <= 10,
                  'text-green-600': (signal.remaining_time_minutes || 0) > 10
                }" class="text-xs font-medium">
                  {{ formatRemainingTime(signal) }}
                </span>
              </div>

              <div class="w-full bg-gray-200 rounded-full h-1 mt-1">
                <div :style="{ width: getSignalStatusPercentage(signal) + '%' }" :class="{
                  'bg-red-500': signal.validity_info?.status === 'expired',
                  'bg-orange-500': signal.validity_info?.status === 'expiring',
                  'bg-yellow-500': signal.validity_info?.status === 'valid',
                  'bg-green-500': signal.validity_info?.status === 'fresh'
                }" class="h-1 rounded-full"></div>
              </div>
            </div>

            <!-- 快速操作按鈕 -->
            <div class="flex space-x-2">
              <button @click="executeQuickTrade(signal)" :disabled="!canExecuteSignal(signal)"
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

        <!-- 中長線即時建議卡片 -->
        <div class="bg-gradient-to-r from-blue-50 to-indigo-50 shadow rounded-lg p-6 border-l-4 border-blue-500">
          <div class="flex items-center justify-between mb-6">
            <div class="flex items-center">
              <div class="p-3 rounded-full bg-blue-100">
                <svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div class="ml-4">
                <h2 class="text-xl font-bold text-blue-800">📊 中長線即時建議 (牛熊市導向)</h2>
                <p class="text-sm text-blue-600">基於當下即時點位的牛熊市判斷，提供中長線策略建議</p>
              </div>
            </div>
            <div class="flex items-center space-x-4">
              <!-- 即時建議統計 -->
              <div class="text-center">
                <div class="text-2xl font-bold text-blue-600">{{ adviceStats.totalAdvice }}</div>
                <div class="text-xs text-blue-500">建議總數</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-green-600">{{ adviceStats.bullishAdvice }}</div>
                <div class="text-xs text-blue-500">做多建議</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-red-600">{{ adviceStats.bearishAdvice }}</div>
                <div class="text-xs text-blue-500">做空建議</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-purple-600">{{ adviceStats.avgConfidence }}%</div>
                <div class="text-xs text-blue-500">平均信心度</div>
              </div>
            </div>
          </div>

          <!-- 操作按鈕區 -->
          <div class="flex items-center justify-between mb-6">
            <div class="flex items-center space-x-3">
              <button @click="generateInstantAdvice" :disabled="isGeneratingAdvice"
                class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white font-medium rounded-lg transition-colors flex items-center">
                <span v-if="isGeneratingAdvice" class="animate-spin mr-2">⏳</span>
                <span v-else class="mr-2">🚀</span>
                {{ isGeneratingAdvice ? '生成中...' : '生成即時建議' }}
              </button>
              <button @click="clearAllInstantAdvice" :disabled="instantAdviceSignals.length === 0"
                class="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-300 text-white font-medium rounded-lg transition-colors">
                🗑️ 清除所有建議
              </button>
            </div>
            <div class="text-sm text-gray-600">
              💡 提示：建議基於牛市看日週期以上，熊市看3日週期以上的K線分析
            </div>
          </div>

          <!-- 即時建議信號列表 -->
          <div v-if="instantAdviceSignals.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="advice in instantAdviceSignals" :key="advice.id"
              class="bg-white border border-blue-200 rounded-lg p-4 hover:shadow-md transition-shadow">

              <!-- 頭部信息 -->
              <div class="flex items-center justify-between mb-3">
                <div class="flex items-center">
                  <span class="font-bold text-gray-800">{{ advice.symbol }}</span>
                  <span :class="{
                    'bg-green-100 text-green-800 border-green-200': advice.signal_type === 'LONG',
                    'bg-red-100 text-red-800 border-red-200': advice.signal_type === 'SHORT'
                  }" class="ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full border">
                    {{ advice.signal_type === 'LONG' ? '做多' : advice.signal_type === 'SHORT' ? '做空' : '未知' }}
                  </span>
                </div>
                <button @click="removeInstantAdvice(advice.id)"
                  class="text-red-500 hover:text-red-700 transition-colors">
                  ❌
                </button>
              </div>

              <!-- 價格信息 -->
              <div class="grid grid-cols-2 gap-2 mb-3 text-sm">
                <div class="bg-gray-50 p-2 rounded">
                  <div class="text-xs text-gray-500">當前價</div>
                  <div class="font-bold">${{ advice.current_price?.toFixed(4) || 'N/A' }}</div>
                </div>
                <div class="bg-blue-50 p-2 rounded">
                  <div class="text-xs text-gray-500">建議進場</div>
                  <div class="font-bold text-blue-600">${{ advice.entry_price?.toFixed(4) || 'N/A' }}</div>
                </div>
              </div>

              <!-- 風險管理 -->
              <div class="grid grid-cols-2 gap-2 mb-3 text-xs">
                <div class="bg-red-50 p-2 rounded">
                  <div class="text-gray-500">止損</div>
                  <div class="font-bold text-red-600">${{ advice.stop_loss?.toFixed(4) }}</div>
                </div>
                <div class="bg-green-50 p-2 rounded">
                  <div class="text-gray-500">止盈</div>
                  <div class="font-bold text-green-600">${{ advice.take_profit?.toFixed(4) }}</div>
                </div>
              </div>

              <!-- 信心度和時間框架 -->
              <div class="flex justify-between items-center mb-3">
                <div class="flex items-center space-x-2">
                  <span class="text-xs text-gray-500">信心度:</span>
                  <span :class="{
                    'bg-green-100 text-green-800': advice.confidence >= 0.8,
                    'bg-yellow-100 text-yellow-800': advice.confidence >= 0.6 && advice.confidence < 0.8,
                    'bg-red-100 text-red-800': advice.confidence < 0.6
                  }" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                    {{ Math.round(advice.confidence * 100) }}%
                  </span>
                </div>
                <span class="text-xs text-gray-600">{{ advice.time_horizon || '中長線' }}</span>
              </div>

              <!-- 時效性顯示 -->
              <div class="mb-3 p-2 rounded" :class="{
                'bg-green-50 border border-green-200': calculateAdviceValidity(advice).percentage > 50,
                'bg-yellow-50 border border-yellow-200': calculateAdviceValidity(advice).percentage <= 50 && calculateAdviceValidity(advice).percentage > 20,
                'bg-red-50 border border-red-200': calculateAdviceValidity(advice).percentage <= 20
              }">
                <div class="flex items-center justify-between text-xs">
                  <span class="text-gray-600">剩餘時效:</span>
                  <span :class="{
                    'text-green-700 font-medium': calculateAdviceValidity(advice).percentage > 50,
                    'text-yellow-700 font-medium': calculateAdviceValidity(advice).percentage <= 50 && calculateAdviceValidity(advice).percentage > 20,
                    'text-red-700 font-bold': calculateAdviceValidity(advice).percentage <= 20
                  }">
                    {{ calculateAdviceValidity(advice).text }}
                  </span>
                </div>
                <div class="mt-1 w-full bg-gray-200 rounded-full h-1">
                  <div :style="{ width: calculateAdviceValidity(advice).percentage + '%' }" :class="{
                    'bg-green-500': calculateAdviceValidity(advice).percentage > 50,
                    'bg-yellow-500': calculateAdviceValidity(advice).percentage <= 50 && calculateAdviceValidity(advice).percentage > 20,
                    'bg-red-500': calculateAdviceValidity(advice).percentage <= 20
                  }" class="h-1 rounded-full transition-all duration-300">
                  </div>
                </div>
              </div>

              <!-- 市場分析信息 -->
              <div v-if="advice.market_analysis" class="bg-gray-50 p-3 rounded text-xs mb-3">
                <div class="font-medium text-gray-700 mb-2">📊 市場分析</div>
                <div class="grid grid-cols-2 gap-2 mb-2">
                  <div class="flex items-center justify-between">
                    <span class="text-gray-600">趨勢:</span>
                    <span :class="{
                      'text-green-600 font-medium': advice.market_analysis.trend === 'BULL',
                      'text-red-600 font-medium': advice.market_analysis.trend === 'BEAR',
                      'text-gray-600': advice.market_analysis.trend === 'NEUTRAL'
                    }">
                      {{ advice.market_analysis.trend === 'BULL' ? '牛市' :
                        advice.market_analysis.trend === 'BEAR' ? '熊市' : '中性' }}
                    </span>
                  </div>
                  <div class="flex items-center justify-between">
                    <span class="text-gray-600">強度:</span>
                    <span class="font-medium text-blue-600">{{ Math.round(advice.market_analysis.strength * 100)
                      }}%</span>
                  </div>
                </div>
                <div class="grid grid-cols-2 gap-2 mb-2">
                  <div class="flex items-center justify-between">
                    <span class="text-gray-600">信心度:</span>
                    <span class="font-medium text-purple-600">{{ Math.round(advice.market_analysis.confidence * 100)
                      }}%</span>
                  </div>
                  <div class="flex items-center justify-between">
                    <span class="text-gray-600">動量:</span>
                    <span class="font-medium text-orange-600">{{ advice.market_analysis.momentum }}</span>
                  </div>
                </div>
                <div class="text-gray-600 mt-2 p-2 bg-blue-50 rounded">
                  <div class="text-xs text-blue-700 mb-1">💡 強度說明:</div>
                  <div class="text-xs text-blue-600">
                    {{ advice.market_analysis.strength >= 0.8 ? '🟢 強勢 (>80%): 趨勢非常明確，建議積極操作' :
                      advice.market_analysis.strength >= 0.6 ? '🟡 中等 (60-80%): 趨勢較為明確，可謹慎操作' :
                        advice.market_analysis.strength >= 0.4 ? '🟠 偏弱 (40-60%): 趨勢不夠明確，建議觀望' :
                          '🔴 弱勢 (<40%): 趨勢不明，風險較高' }} </div>
                  </div>
                  <div class="text-gray-700 mt-2 font-medium">{{ translateReasoningText(advice.reasoning) }}</div>
                </div>

                <!-- 策略名稱 -->
                <div class="text-xs text-blue-600 font-medium">
                  📈 {{ advice.strategy_name }}
                </div>
              </div>
            </div>

            <!-- 無建議時的提示 -->
            <div v-else class="text-center py-12">
              <div class="text-gray-400 mb-4">
                <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 class="text-lg font-medium text-gray-900 mb-2">暫無即時建議</h3>
              <p class="text-gray-600 mb-4">點擊上方按鈕生成基於牛熊市判斷的中長線策略建議</p>
              <div class="text-sm text-gray-500">
                <p>• 牛市環境：分析日線、3日線、週線走勢</p>
                <p>• 熊市環境：分析3日線、週線、月線走勢</p>
                <p>• 建議可手動刪除，24小時後自動過期</p>
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
              <div class="flex items-center justify-between p-6 cursor-pointer"
                @click="toggleSignalExpansion(signal.id)">
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
                  (realtimeUpdates.reduce((sum, update) => sum + update.change_24h, 0) /
                    realtimeUpdates.length).toFixed(2)
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
            <h2 class="text-lg font-semibold text-gray-900">📋 即時數據更新日誌</h2>
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
                  {{ isLogRefreshing ? '正在更新...' : '每3秒更新' }}
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
import api, { checkHealth, waitForService } from '@/utils/api'
import CustomNotification from '../components/CustomNotification.vue'
import LoadingOverlay from '../components/LoadingOverlay.vue'
import StatusBadge from '../components/StatusBadge.vue'
import ServiceStatus from '../components/ServiceStatus.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

interface Signal {
  id: number | string
  symbol: string
  signal_type: string
  status?: string // 後端信號狀態：active, expired, executed, cancelled
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
  // 短線信號歷史專用字段
  trade_result?: 'success' | 'failure' | 'breakeven'
  profit_percent?: number
  // 短線信號專用字段
  is_scalping?: boolean
  // 🔥 牛市短線交易優化：新增技術指標字段
  technical_summary?: {
    volume_analysis?: {
      relative_volume?: number
      volume_trend?: string
    }
  }
  price_action?: {
    breakout_potential?: number
    support_resistance?: number
  }
  bollinger_bands?: {
    upper?: number
    lower?: number
    middle?: number
  }
  strategy_name?: string
  scalping_type?: string
  signal_strength?: number
  key_indicators?: Record<string, any>
  expires_at?: string
  price_change_percent?: number
  // 新增：後端計算的時效性和風險信息
  remaining_time_minutes?: number  // 剩餘時間（分鐘）
  validity_info?: {
    percentage: number
    remaining_minutes: number
    remaining_seconds: number
    status: string
    text: string
    color: string
    can_execute: boolean
  }
  execution_status?: string  // active, expired, executed, cancelled
  price_deviation_risk?: {
    level: string
    percentage: number
    warning: string
    color: string
  }
  market_condition_impact?: {
    impact_score: number
    condition_text: string
    risk_text: string
    overall_rating: string
    rating_text: string
    rating_color: string
  }
  // 新增：手動即時建議專用字段
  is_manual_advice?: boolean
  advice_type?: string
  time_horizon?: string
  market_analysis?: {
    trend: string
    strength: number
    confidence: number
    duration_days: number
    volatility: string
    momentum: string
  }
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
const expandedIndicators = ref<Set<number | string>>(new Set()) // 新增：技術指標展開狀態

// 新信號追蹤狀態
const newSignalIds = ref<Set<number | string>>(new Set())

// 使用者設置
const soundNotificationEnabled = ref(true)

// ===== 短線信號管理系統 (簡化版) =====
// 目標幣種列表
const TARGET_COINS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT']

// 短線信號分析相關數據
const shortTermStats = reactive({
  totalSignals: 0,
  avgConfidence: 0,
  urgentCount: 0,
  strategiesUsed: 0
})

// 更新短線信號統計數據 - 基於實際顯示的篩選後信號
const updateShortTermStats = () => {
  // 使用 filteredShortTermSignals 計算統計，反映真實顯示的數據
  const displayedSignals = filteredShortTermSignals.value
  const strategiesSet = new Set(displayedSignals.map(s => s.strategy_name || 'Unknown'))

  shortTermStats.totalSignals = displayedSignals.length
  shortTermStats.avgConfidence = displayedSignals.length > 0
    ? Math.round(displayedSignals.reduce((sum, signal) => sum + signal.confidence * 100, 0) / displayedSignals.length)
    : 0
  shortTermStats.urgentCount = displayedSignals.filter(signal =>
    ['urgent', 'high'].includes(signal.urgency_level || '')).length
  shortTermStats.strategiesUsed = strategiesSet.size

  // 短線統計更新 (已移除調試日誌)
}

const shortTermFilter = reactive({
  timeframe: 'all',
  urgency: 'all',
  confidence: 'all'
})

// 短線信號列表（包含原始短線專用信號）
const shortTermSignals = ref<Signal[]>([])
const rawScalpingSignals = ref<any[]>([]) // 原始短線專用信號

// 新增：手動即時建議相關數據
const instantAdviceSignals = ref<Signal[]>([])
const isGeneratingAdvice = ref(false)
const adviceStats = reactive({
  totalAdvice: 0,
  bullishAdvice: 0,
  bearishAdvice: 0,
  avgConfidence: 0
})

// 短線信號刷新確認彈窗
const showRefreshConfirm = ref(false)
const refreshConfirmDetails = ref([
  '將重新獲取最新信號',
  '建議在市場突發波動較大時才執行此操作',
  '策略邏輯測試功能'
])

// 即時價格數據
const realtimePrices = ref<Record<string, any>>({})
const priceUpdateTime = ref<string>('')

// 計算顯示的短線信號 (簡化版 - 直接顯示有效信號)
const filteredShortTermSignals = computed(() => {
  // 🔥 關鍵修復：過濾掉過期信號，確保UI立即更新
  const validSignals = shortTermSignals.value.filter(signal => {
    const validityCheck = checkShortTermSignalValidity(signal)
    const isValid = !validityCheck.isExpired

    if (!isValid) {
      // 過期信號被過濾 (已移除調試日誌)
    }

    return isValid
  })

  // 有效信號統計 (已移除調試日誌)

  // 按目標幣種順序排序
  return validSignals
    .slice()
    .sort((a, b) => {
      const aIndex = TARGET_COINS.indexOf(a.symbol)
      const bIndex = TARGET_COINS.indexOf(b.symbol)
      // 如果幣種在目標列表中，按列表順序排序；如果不在，放在後面
      if (aIndex !== -1 && bIndex !== -1) return aIndex - bIndex
      if (aIndex !== -1) return -1
      if (bIndex !== -1) return 1
      return a.symbol.localeCompare(b.symbol)
    })
    .slice(0, 5) // 確保最多5個信號
})

// 路由
const router = useRouter()

// 跳轉到信號歷史頁面
const navigateToSignalHistory = () => {
  router.push({ name: 'SignalHistory' })
}

// 跳轉到短線歷史頁面
const navigateToShortTermHistory = () => {
  // 防止在跳轉期間觸發額外的歸檔操作
  // 準備跳轉到短線歷史頁面 (已移除調試日誌)
  router.push({ name: 'ShortTermHistory' })
}

// 打印短線信號分析中心的過期信號
const printExpiredSignals = async () => {
  try {
    // 從後端API載入所有歸檔的過期信號
    const response = await fetch('/api/v1/scalping/expired', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('❌ 載入過期信號失敗:', errorText)
      showNotification('error', '載入失敗', `無法載入過期信號: ${response.status} ${response.statusText}`)
      return
    }

    const allExpiredSignals = await response.json()

    if (allExpiredSignals.length === 0) {
      showNotification('info', '過期信號檢查', '沒有發現任何過往累積的過期信號。')
      return
    }

    // 按幣種分組統計
    const symbolGroups: Record<string, any[]> = {}
    allExpiredSignals.forEach((signal: any) => {
      if (!symbolGroups[signal.symbol]) {
        symbolGroups[signal.symbol] = []
      }
      symbolGroups[signal.symbol].push(signal)
    })

    // 計算統計信息
    const typeStats: Record<string, number> = {}
    allExpiredSignals.forEach((signal: any) => {
      const type = signal.signal_type || signal.direction || 'Unknown'
      typeStats[type] = (typeStats[type] || 0) + 1
    })

    // 僅在開發環境顯示詳細日誌
    if (process.env.NODE_ENV === 'development') {

    }

    // 顯示通知
    showNotification('info', '過往累積過期信號檢查',
      `檢查完成！發現 ${allExpiredSignals.length} 個過往累積的過期信號，涉及 ${Object.keys(symbolGroups).length} 個幣種。詳細信息請查看控制台。`)

  } catch (error) {
    console.error('❌ 載入過期信號時發生錯誤:', error)
    showNotification('error', '載入錯誤', `載入過期信號時發生錯誤: ${(error as Error).message}`)
  }
}

// 獲取即時幣安價格
const fetchRealtimePrices = async () => {
  try {
    const symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT'] // 只包含指定的5個幣種
    const response = await api.get('/api/v1/scalping/prices', {
      params: { symbols }
    })

    if (response.data && response.data.prices) {
      realtimePrices.value = response.data.prices
      priceUpdateTime.value = new Date().toLocaleTimeString()

      // 更新短線信號中的當前價格
      updateCurrentPricesInSignals()

      // 更新即時價格 (已移除調試日誌)
    }

  } catch (error: any) {
    // 只在開發模式下輸出錯誤，避免生產環境的噪音
    if (process.env.NODE_ENV === 'development') {
      console.warn('獲取即時價格失敗 (非關鍵錯誤):', error?.message || error)
    }
    // 不顯示錯誤通知，因為這不是關鍵功能
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
  if (rawScalpingSignals.value.length > 0) {
    rawScalpingSignals.value.forEach((signal: any) => {
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
  }
}
const fetchScalpingSignals = async (): Promise<any[]> => {
  try {
    // 獲取短線信號 (已移除調試日誌)

    const response = await api.get('/api/v1/scalping/signals', {
      params: {
        symbols: ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT'],
        timeframes: ['1m', '3m', '5m', '15m', '30m'],
        min_confidence: 0.85,
        urgency_levels: ['urgent', 'high', 'medium'],
        market_condition: 'bull',
        risk_level: 'conservative'
      }
    })

    // 修復：處理精準篩選API的響應格式
    const responseData = response.data
    rawScalpingSignals.value = responseData.signals || []

    // 記錄精準篩選模式信息
    if (responseData.precision_mode) {
      console.log(`🎯 精準篩選模式: ${responseData.count} 個信號`, responseData.market_conditions)
    }

    // 載入存儲的信號時間戳
    const savedTimestamps = JSON.parse(localStorage.getItem('tradingx_signal_timestamps') || '{}')

    // 轉換為通用Signal格式以便在UI中顯示
    const convertedSignals = rawScalpingSignals.value.map(signal => {
      // 🔧 修正信號標識符：加入時間戳哈希避免不同時期的相同策略信號被混淆
      const timeHash = Math.floor(new Date(signal.created_at).getTime() / (1000 * 60 * 30)) // 30分鐘為一個時間片段
      const signalKey = `${signal.symbol}_${signal.signal_type}_${signal.primary_timeframe}_${signal.strategy_name}_${timeHash}`

      // 檢查是否為已知信號（在時間窗口內）
      let preservedCreatedAt = signal.created_at
      let preservedExpiresAt = signal.expires_at
      let isExistingSignal = false

      if (savedTimestamps[signalKey]) {
        const saved = savedTimestamps[signalKey]
        const savedTime = new Date(saved.created_at)
        const currentTime = new Date()
        const hoursDiff = (currentTime.getTime() - savedTime.getTime()) / (1000 * 60 * 60)

        // 只有在4小時內的信號才視為同一信號，超過則視為新信號
        if (hoursDiff < 4) {
          preservedCreatedAt = saved.created_at
          preservedExpiresAt = saved.expires_at
          isExistingSignal = true
          // 信號使用保存的時間戳 (已移除調試日誌)
        } else {
          // 清理過期的時間戳記錄
          delete savedTimestamps[signalKey]
          // 信號時間戳過期，使用新時間戳 (已移除調試日誌)
        }
      }

      if (!isExistingSignal) {
        // 新信號，保存其時間戳
        savedTimestamps[signalKey] = {
          created_at: signal.created_at,
          expires_at: signal.expires_at,
          symbol: signal.symbol,
          signal_type: signal.signal_type,
          entry_price: signal.entry_price
        }
        localStorage.setItem('tradingx_signal_timestamps', JSON.stringify(savedTimestamps))
        // 新信號保存時間戳 (已移除調試日誌)
      }

      const convertedSignal: Signal = {
        id: signalKey, // 使用穩定的標識符作為 ID
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
        created_at: preservedCreatedAt, // 使用保存的時間戳
        expires_at: preservedExpiresAt, // 使用保存的過期時間
        key_indicators: signal.key_indicators || {},
        strategy_name: signal.strategy_name,
        is_scalping: true,
        // 🔧 修復：確保 validity_info 被正確傳遞
        validity_info: signal.validity_info
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

    // 清理過期的時間戳（超過24小時的記錄）
    cleanupExpiredTimestamps()

    return convertedSignals

  } catch (error) {
    console.error('獲取短線信號失敗:', error)
    rawScalpingSignals.value = []
    return []
  }
}

// 清理過期的信號時間戳
const cleanupExpiredTimestamps = () => {
  try {
    const savedTimestamps = JSON.parse(localStorage.getItem('tradingx_signal_timestamps') || '{}')
    const now = new Date()
    const expiredKeys: string[] = []

    // 檢查每個時間戳，移除超過4小時的記錄（與信號重用邏輯一致）
    Object.keys(savedTimestamps).forEach(key => {
      const saved = savedTimestamps[key]
      // 處理新的數據結構
      const timestamp = typeof saved === 'string' ? saved : saved.created_at
      const timestampDate = new Date(timestamp)
      const hoursElapsed = (now.getTime() - timestampDate.getTime()) / (1000 * 60 * 60)

      if (hoursElapsed > 4) { // 改為4小時，與主邏輯一致
        expiredKeys.push(key)
      }
    })

    // 移除過期的記錄
    if (expiredKeys.length > 0) {
      expiredKeys.forEach(key => delete savedTimestamps[key])
      localStorage.setItem('tradingx_signal_timestamps', JSON.stringify(savedTimestamps))
      // 清理過期的信號時間戳記錄 (已移除調試日誌)
    }
  } catch (error) {
    console.error('清理時間戳記錄失敗:', error)
  }
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

    // 2. 獲取專用短線信號（後端已包含完整的時效性和風險計算）
    const scalpingSignals = await fetchScalpingSignals()

    // 2.1 同時獲取即時價格
    await fetchRealtimePrices()

    // 3. 合併兩種信號，基於幣種去重（不分方向），保留信心度最高的信號
    const allShortSignals = [...scalpingSignals, ...filteredFromGeneral]
    const uniqueSignals = new Map()

    // 首先檢查現有的短線信號，避免同幣種重複
    const existingCoins = new Set(shortTermSignals.value
      .filter(signal => {
        const validityCheck = checkShortTermSignalValidity(signal)
        return !validityCheck.isExpired // 只考慮未過期的信號
      })
      .map(signal => signal.symbol)
    )

    // 基於幣種去重，每個幣種只保留信心度最高的一個信號
    allShortSignals.forEach(signal => {
      const key = signal.symbol

      // 如果該幣種在儀表板中已有未過期信號，跳過
      if (existingCoins.has(key)) {
        // 跳過已存在的信號 (已移除調試日誌)
        return
      }

      const existingSignal = uniqueSignals.get(key)

      // 如果該鍵不存在，或當前信號信心度更高，或當前信號是專用短線信號且信心度相近，則保留當前信號
      if (!existingSignal ||
        signal.confidence > existingSignal.confidence ||
        (signal.is_scalping && !existingSignal.is_scalping && Math.abs(signal.confidence - existingSignal.confidence) < 0.1)) {
        uniqueSignals.set(key, signal)
      }
    })

    // 將新信號添加到現有短線信號中，而不是完全替換
    const newSignals = Array.from(uniqueSignals.values())
    shortTermSignals.value = [...shortTermSignals.value, ...newSignals]

    // 首先檢查並歸檔過期信號（無論手動還是自動刷新）
    const expiredCount = await processExpiredShortTermSignals()

    // 確保至少保持5個主要幣種的信號
    await ensureMinimumCoinCoverage()

    // 更新統計數據 - 基於實際顯示的篩選後信號
    updateShortTermStats()

    // 短線信號更新完成 (已移除調試日誌)

    if (expiredCount > 0) {
      // 處理過期短線信號 (已移除調試日誌)
    }

  } catch (error) {
    console.error('短線信號更新失敗:', error)
    // 如果專用短線信號獲取失敗，至少保留中長線篩選的結果
    const aggressiveTimeframes = ['1m', '3m', '5m', '15m', '30m']
    shortTermSignals.value = latestSignals.value.filter(signal => {
      const hasShortTimeframe = aggressiveTimeframes.includes(signal.primary_timeframe || '')
      const hasDecentConfidence = signal.confidence >= 0.5
      return hasShortTimeframe && hasDecentConfidence
    })

    // 更新統計數據
    updateShortTermStats()
  }
}

// 生成即時中長線建議
const generateInstantAdvice = async () => {
  try {
    isGeneratingAdvice.value = true
    showLoading('正在生成即時中長線建議...')

    const response = await api.post('/api/v1/signals/generate-instant-advice', {
      symbols: ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT'],
      analysis_depth: 'comprehensive'
    })

    const adviceData = response.data
    instantAdviceSignals.value = adviceData.advice_signals || []

    // 為每個建議添加時效性檢查（根據建議類型設定不同有效期）
    instantAdviceSignals.value.forEach(advice => {
      if (!advice.expires_at) {
        // 根據市場分析的時間跨度設定不同的有效期
        let hoursToExpire = 24 // 預設24小時

        if (advice.time_horizon) {
          if (advice.time_horizon.includes('短線')) {
            hoursToExpire = 4 // 短線4小時
          } else if (advice.time_horizon.includes('中線')) {
            hoursToExpire = 12 // 中線12小時
          } else if (advice.time_horizon.includes('中長線')) {
            hoursToExpire = 48 // 中長線48小時
          } else if (advice.time_horizon.includes('長線')) {
            hoursToExpire = 72 // 長線72小時
          }
        } else if (advice.market_analysis?.trend === 'BULL') {
          // 牛市環境：延長有效期
          hoursToExpire = 36
        } else if (advice.market_analysis?.trend === 'BEAR') {
          // 熊市環境：縮短有效期
          hoursToExpire = 18
        }

        const expireTime = new Date()
        expireTime.setHours(expireTime.getHours() + hoursToExpire)
        advice.expires_at = expireTime.toISOString()

        // 設定建議有效期 (已移除調試日誌)
      }
    })

    // 保存到 localStorage
    saveInstantAdviceToStorage()

    // 更新統計
    updateAdviceStats()

    // 生成即時中長線建議 (已移除調試日誌)
    showNotification('success', '即時建議生成成功',
      `基於牛熊市分析，生成 ${adviceStats.totalAdvice} 個中長線策略建議`)

  } catch (error) {
    console.error('生成即時建議失敗:', error)
    showNotification('error', '生成建議失敗', '無法獲取即時中長線建議，請稍後重試')
  } finally {
    isGeneratingAdvice.value = false
    hideLoading()
  }
}

// 手動刪除即時建議
const removeInstantAdvice = (adviceId: string | number) => {
  const index = instantAdviceSignals.value.findIndex(advice => advice.id === adviceId)
  if (index !== -1) {
    const removedAdvice = instantAdviceSignals.value.splice(index, 1)[0]

    // 更新統計和儲存
    updateAdviceStats()
    saveInstantAdviceToStorage()

    showNotification('info', '建議已移除', `已移除 ${removedAdvice.symbol} 的中長線建議`)
  }
}

// 清除所有即時建議
const clearAllInstantAdvice = () => {
  const count = instantAdviceSignals.value.length
  instantAdviceSignals.value = []

  // 重置統計和清除儲存
  updateAdviceStats()
  clearInstantAdviceFromStorage()

  showNotification('info', '已清除所有建議', `清除了 ${count} 個即時中長線建議`)
}

// 更新即時建議統計
const updateAdviceStats = () => {
  adviceStats.totalAdvice = instantAdviceSignals.value.length
  adviceStats.bullishAdvice = instantAdviceSignals.value.filter(s => s.signal_type === 'LONG').length
  adviceStats.bearishAdvice = instantAdviceSignals.value.filter(s => s.signal_type === 'SHORT').length
  adviceStats.avgConfidence = instantAdviceSignals.value.length > 0
    ? Math.round(instantAdviceSignals.value.reduce((sum, signal) => sum + signal.confidence * 100, 0) / instantAdviceSignals.value.length)
    : 0
}

// 保存即時建議到 localStorage
const saveInstantAdviceToStorage = () => {
  try {
    const adviceData = {
      signals: instantAdviceSignals.value,
      timestamp: Date.now()
    }
    localStorage.setItem('tradingx_instant_advice', JSON.stringify(adviceData))
    // 保存即時建議到 localStorage (已移除調試日誌)
  } catch (error) {
    console.error('保存即時建議失敗:', error)
  }
}

// 從 localStorage 載入即時建議
const loadInstantAdviceFromStorage = () => {
  try {
    const saved = localStorage.getItem('tradingx_instant_advice')
    if (saved) {
      const adviceData = JSON.parse(saved)
      const validAdvice = adviceData.signals.filter((advice: Signal) => {
        // 檢查是否過期
        if (advice.expires_at) {
          const expireTime = new Date(advice.expires_at)
          const now = new Date()
          return now < expireTime
        }
        return true
      })

      instantAdviceSignals.value = validAdvice
      updateAdviceStats()

      // 如果有過期的建議被移除，更新儲存
      if (validAdvice.length !== adviceData.signals.length) {
        const expiredCount = adviceData.signals.length - validAdvice.length
        // 移除過期的即時建議 (已移除調試日誌)
        saveInstantAdviceToStorage()
      }

      // 從 localStorage 載入有效即時建議 (已移除調試日誌)
    }
  } catch (error) {
    console.error('載入即時建議失敗:', error)
    // 如果載入失敗，清除可能損壞的數據
    localStorage.removeItem('tradingx_instant_advice')
  }
}

// 清除 localStorage 中的即時建議
const clearInstantAdviceFromStorage = () => {
  try {
    localStorage.removeItem('tradingx_instant_advice')
    // 已清除 localStorage 中的即時建議 (已移除調試日誌)
  } catch (error) {
    // console.error('清除即時建議儲存失敗:', error)
  }
}

// 檢查並清理過期的即時建議
const cleanupExpiredAdvice = () => {
  const originalCount = instantAdviceSignals.value.length
  const now = new Date()

  instantAdviceSignals.value = instantAdviceSignals.value.filter(advice => {
    if (advice.expires_at) {
      const expireTime = new Date(advice.expires_at)
      return now < expireTime
    }
    return true
  })

  const expiredCount = originalCount - instantAdviceSignals.value.length
  if (expiredCount > 0) {
    updateAdviceStats()
    saveInstantAdviceToStorage()
    // 自動清理過期的即時建議 (已移除調試日誌)
    showNotification('info', '建議已過期', `已自動移除 ${expiredCount} 個過期的中長線建議`)
  }
}

// 翻譯reasoning中的英文術語
const translateReasoningText = (text?: string): string => {
  if (!text) return ''

  return text
    .replace(/LONG操作/g, '做多操作')
    .replace(/SHORT操作/g, '做空操作')
    .replace(/建議LONG/g, '建議做多')
    .replace(/建議SHORT/g, '建議做空')
    .replace(/LONG建議/g, '做多建議')
    .replace(/SHORT建議/g, '做空建議')
    .replace(/\bLONG\b/g, '做多')
    .replace(/\bSHORT\b/g, '做空')
}

// 計算即時建議剩餘時效
const calculateAdviceValidity = (advice: Signal): { percentage: number; text: string; isExpiring: boolean } => {
  if (!advice.expires_at) {
    return { percentage: 100, text: '永久有效', isExpiring: false }
  }

  try {
    const expireTime = new Date(advice.expires_at)
    const now = new Date()
    const remainingMs = expireTime.getTime() - now.getTime()

    if (remainingMs <= 0) {
      return { percentage: 0, text: '已過期', isExpiring: true }
    }

    // 動態計算總有效期（從創建時間到過期時間）
    let totalMs = 24 * 60 * 60 * 1000 // 預設24小時
    if (advice.created_at) {
      const createdTime = new Date(advice.created_at)
      totalMs = expireTime.getTime() - createdTime.getTime()
    }

    const percentage = Math.max(0, (remainingMs / totalMs) * 100)

    const remainingHours = Math.floor(remainingMs / (1000 * 60 * 60))
    const remainingMinutes = Math.floor((remainingMs % (1000 * 60 * 60)) / (1000 * 60))

    let text = ''
    let isExpiring = false

    if (remainingHours > 24) {
      const days = Math.floor(remainingHours / 24)
      const hours = remainingHours % 24
      text = days > 0 ? `${days}天${hours}小時` : `${remainingHours}小時`
    } else if (remainingHours > 6) {
      text = `${remainingHours}小時`
    } else if (remainingHours > 0) {
      text = `${remainingHours}小時${remainingMinutes}分`
      isExpiring = remainingHours <= 2
    } else if (remainingMinutes > 0) {
      text = `${remainingMinutes}分鐘`
      isExpiring = true
    } else {
      text = '即將過期'
      isExpiring = true
    }

    return { percentage: Math.round(percentage), text, isExpiring }
  } catch (error) {
    return { percentage: 50, text: '計算錯誤', isExpiring: false }
  }
}

// 檢查信號是否在指定時間內
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
  // 直接重新獲取數據，不再使用快取
  await updateShortTermSignals()
  showNotification('success', '激進短線信號已刷新',
    `強制刷新完成！發現 ${shortTermStats.totalSignals} 個短線交易機會 (包含${shortTermStats.strategiesUsed}種策略)`)
}

// 確認刷新短線信號
const confirmRefreshShortTermSignals = async () => {
  showRefreshConfirm.value = false

  // 在刷新之前，先檢查並歸檔過期的信號
  const expiredCount = await processExpiredShortTermSignals()

  if (expiredCount > 0) {
    // 手動刷新處理過期信號 (已移除調試日誌)
    showNotification('info', '信號歸檔完成', `已將 ${expiredCount} 個過期信號移至歷史紀錄`)
  }

  // 然後執行刷新
  await refreshShortTermSignals()
}

// 格式化剩餘時間顯示
const formatRemainingTime = (signal: Signal): string => {
  const remainingMinutes = signal.validity_info?.remaining_minutes || 0
  const remainingSeconds = signal.validity_info?.remaining_seconds || 0

  if (remainingMinutes >= 60) {
    const hours = Math.floor(remainingMinutes / 60)
    const mins = Math.floor(remainingMinutes % 60)
    return mins > 0 ? `${hours}小時${mins}分鐘` : `${hours}小時`
  } else if (remainingMinutes >= 1) {
    return `${Math.floor(remainingMinutes)}分鐘`
  } else if (remainingSeconds > 0) {
    return `${Math.floor(remainingSeconds)}秒`
  } else {
    return '已過期'
  }
}

// 檢查信號是否可執行
const canExecuteSignal = (signal: Signal): boolean => {
  const status = signal.validity_info?.status || 'unknown'
  return status === 'fresh' || status === 'valid'
}

// 獲取信號狀態文字
const getSignalStatusText = (signal: Signal): string => {
  const status = signal.validity_info?.status || 'unknown'
  switch (status) {
    case 'fresh':
      return '新鮮'
    case 'valid':
      return '有效'
    case 'expiring':
      return '即將過期'
    case 'expired':
      return '已過期'
    default:
      return '未知'
  }
}

// 獲取信號狀態百分比（用於進度條）
const getSignalStatusPercentage = (signal: Signal): number => {
  const status = signal.validity_info?.status || 'unknown'
  switch (status) {
    case 'fresh':
      return 100
    case 'valid':
      return 70
    case 'expiring':
      return 30
    case 'expired':
      return 0
    default:
      return 0
  }
}

// 快速執行交易
const executeQuickTrade = (signal: Signal) => {
  if (!canExecuteSignal(signal)) {
    showNotification('warning', '信號無法執行', '此短線信號已過期或不符合執行條件')
    return
  }

  // 檢查價格偏離風險
  if (signal.price_deviation_risk && signal.price_deviation_risk.level === 'critical') {
    showNotification('warning', '價格偏離風險', signal.price_deviation_risk.warning)
    return
  }

  // 這裡可以集成實際的交易執行邏輯
  showNotification('info', '快速交易', `正在執行 ${signal.symbol} ${signal.signal_type} 信號`)

  // 模擬交易執行
  // 執行快速交易 (已移除調試日誌)
}

// 查看短線信號詳情
const viewShortTermDetail = (signal: Signal) => {
  const statusText = getSignalStatusText(signal)
  const priceRisk = signal.price_deviation_risk || { level: 'unknown', warning: '無數據' }
  const marketImpact = signal.market_condition_impact || { rating_text: '無數據', condition_text: '無數據' }

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
信號狀態: ${statusText}
價格偏離風險: ${priceRisk.warning}
市場條件評級: ${marketImpact.rating_text} (${marketImpact.condition_text})
執行狀態: ${signal.execution_status || 'active'}
  `
  alert(details)
}

// 移除未使用的函數警告
// const detectNewSignals = (newSignals: Signal[]) => { ... }
// const getSortedSignals = (signals: Signal[]): Signal[] => { ... }
// const getMockRSI = (signal: Signal): number => { ... }
// const getMockEMADeviation = (signal: Signal): number => { ... }
// const getMockVolumeRatio = (signal: Signal): number => { ... }
// const getMockATR = (signal: Signal): number => { ... }

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

// ===== 短線信號歷史紀錄系統 =====

// 檢查短線信號時效性並計算結果（優化版本 - 牛市短線交易）
const checkShortTermSignalValidity = (signal: Signal): { isExpired: boolean; result: 'success' | 'failure' | 'breakeven'; profitPercent: number } => {
  let isExpired = false

  // 🔧 新增：驗證後端時間邏輯的一致性，並使用實際時間差
  if (signal.created_at && signal.expires_at) {
    const createdTime = new Date(signal.created_at)
    const expiresTime = new Date(signal.expires_at)
    const now = new Date()

    // 使用實際的過期時間判斷是否過期
    isExpired = now >= expiresTime

    if (signal.validity_info) {
      const actualDiffMinutes = (expiresTime.getTime() - createdTime.getTime()) / (1000 * 60)
      const backendMinutes = signal.validity_info.remaining_minutes || 0

      // 如果實際時間差與後端數據差異超過1分鐘，記錄警告
      if (Math.abs(actualDiffMinutes - backendMinutes) > 1) {
        console.warn(`⚠️ 時間邏輯不一致 ${signal.symbol}: 實際有效期 ${actualDiffMinutes.toFixed(2)}分鐘 vs 後端計算 ${backendMinutes}分鐘`)
      }
    }

    if (isExpired) {
      return { isExpired: true, result: 'breakeven', profitPercent: 0 }
    }
  }

  // 優先檢查後端的 status 字段
  if (signal.status === 'expired') {
    isExpired = true

  }
  // 使用後端提供的 validity_info 數據
  else if (signal.validity_info) {
    // 只有當 validity_info.status 為 "expired" 或剩餘時間 <= 0 時才算過期
    isExpired = signal.validity_info.status === 'expired' ||
      (signal.validity_info.remaining_seconds !== undefined && signal.validity_info.remaining_seconds <= 0)

  } else {
    // 如果沒有後端數據，保守處理為未過期，避免錯誤判斷
    console.warn(`⚠️ 缺少後端時效性數據: ${signal.symbol}，預設為有效`)
    isExpired = false
  }

  if (!isExpired || !signal.current_price || !signal.entry_price) {
    return { isExpired, result: 'breakeven', profitPercent: 0 }
  }

  const direction = getSignalDirection(signal.signal_type)
  const priceChange = signal.current_price - signal.entry_price
  const profitPercent = (priceChange / signal.entry_price) * 100

  // 🔧 牛市短線交易優化：動態止盈策略
  let successThreshold = calculateDynamicStopProfit(signal)

  // 動態止損計算（基於 JSON 配置邏輯）
  const stopLossThreshold = calculateDynamicStopLoss(signal)
  const breakevenThreshold = 0.5 // 攤平閾值：0% < 利潤 < 0.5% 才算攤平



  let result: 'success' | 'failure' | 'breakeven'

  // 根據方向判斷勝敗
  if (direction === 'LONG') {
    // 做多：需要達到動態閾值才算成功
    if (profitPercent >= successThreshold) {
      result = 'success'

    } else if (profitPercent <= -stopLossThreshold) {
      result = 'failure' // 虧損超過1%算失敗

    } else if (profitPercent > 0 && profitPercent < breakevenThreshold) {
      result = 'breakeven' // 0% < 利潤 < 0.5% 才算攤平

    } else {
      result = 'success' // 0.5% <= 利潤 < successThreshold 也算成功

    }
  } else if (direction === 'SHORT') {
    // 做空：價格下跌需要達到動態閾值才算成功
    if (-profitPercent >= successThreshold) { // 做空時使用負值進行比較
      result = 'success'

    } else if (profitPercent >= stopLossThreshold) {
      result = 'failure' // 虧損超過1%算失敗（做空時價格上漲）

    } else if (profitPercent < 0 && -profitPercent < breakevenThreshold) {
      result = 'breakeven' // 做空：0% < 利潤 < 0.5% 才算攤平

    } else {
      result = 'success' // 做空：0.5% <= 利潤 < successThreshold 也算成功

    }
  } else {
    result = 'breakeven'

  }

  // 🔧 修正：返回帶方向性的利潤百分比
  const displayProfitPercent = direction === 'SHORT' ? -profitPercent : profitPercent

  return { isExpired, result, profitPercent: displayProfitPercent }
}

// 動態止損計算（基於 JSON 配置邏輯）
const calculateDynamicStopLoss = (signal: Signal): number => {
  // 基於資產類型的波動性因子
  const assetVolatilityMap: Record<string, number> = {
    'BTCUSDT': 1.0,
    'ETHUSDT': 1.2,
    'SOLUSDT': 1.8,
    'BNBUSDT': 1.1,
    'XRPUSDT': 1.4,
    'ADAUSDT': 1.6
  }

  // 基於時間框架的止損範圍
  const timeframeStopLossMap: Record<string, [number, number]> = {
    '1m': [0.01, 0.03],   // 極短線: 1-3%
    '3m': [0.01, 0.03],
    '5m': [0.01, 0.03],
    '15m': [0.01, 0.03],
    '30m': [0.01, 0.03],
    '1h': [0.01, 0.03],
    '4h': [0.02, 0.05],   // 短線: 2-5%
    '1d': [0.02, 0.05]
  }

  // 獲取基礎止損範圍
  const baseRange = timeframeStopLossMap[signal.primary_timeframe || '1h'] || [0.02, 0.03]
  const volatilityFactor = assetVolatilityMap[signal.symbol] || 1.0

  // 計算平均止損百分比
  const baseStopLoss = (baseRange[0] + baseRange[1]) / 2
  const adjustedStopLoss = baseStopLoss * volatilityFactor

  // 根據信號緊急程度調整
  let urgencyMultiplier = 1.0
  if (signal.urgency_level === 'urgent') urgencyMultiplier = 0.8  // 緊急信號收緊止損
  else if (signal.urgency_level === 'high') urgencyMultiplier = 0.9
  else if (signal.urgency_level === 'medium') urgencyMultiplier = 1.1

  // 最終止損百分比
  const finalStopLoss = adjustedStopLoss * urgencyMultiplier

  // 限制在合理範圍內 (0.5% - 5%)
  return Math.max(0.5, Math.min(5.0, finalStopLoss * 100))
}

// � 牛市短線交易：動態止盈計算（ATR + ADX 趨勢判斷）
const calculateDynamicStopProfit = (signal: Signal): number => {
  // 基礎閾值設定
  let baseThreshold = 2.0 // 基礎閾值2%

  // 根據時間框架調整基礎閾值
  if (signal.primary_timeframe === '1m') baseThreshold = 1.5  // 1分鐘: 1.5%
  else if (signal.primary_timeframe === '3m') baseThreshold = 2.0  // 3分鐘: 2%
  else if (signal.primary_timeframe === '5m') baseThreshold = 2.5  // 5分鐘: 2.5%
  else if (signal.primary_timeframe === '15m') baseThreshold = 3.0 // 15分鐘: 3%
  else if (signal.primary_timeframe === '30m') baseThreshold = 4.0 // 30分鐘: 4%

  // 🔥 ATR 波動率調整（模擬 ATR 計算）
  let atrMultiplier = 1.0
  const priceLevel = signal.entry_price || 1

  // 根據價格區間估算波動率調整
  if (priceLevel > 50000) atrMultiplier = 1.3      // 高價位（如BTC）：高波動
  else if (priceLevel > 3000) atrMultiplier = 1.2   // 中高價位（如ETH）：中高波動
  else if (priceLevel > 300) atrMultiplier = 1.1    // 中價位（如BNB）：中等波動
  else if (priceLevel > 1) atrMultiplier = 1.0      // 低價位：標準波動
  else atrMultiplier = 0.8                          // 極低價位：低波動

  // 🎯 ADX 趨勢強度判斷（基於技術指標模擬）
  let trendMultiplier = 1.0

  // 基於現有信號數據估算趨勢強度
  if (signal.key_indicators) {
    const rsi = signal.key_indicators.rsi || 50
    const macdSignal = signal.key_indicators.macd_signal || 0
    const stochK = signal.key_indicators.stoch_k || 50

    // 趨勢強度評估
    let trendScore = 0

    // RSI 趨勢判斷
    if (rsi > 70 || rsi < 30) trendScore += 1  // 強趨勢
    else if (rsi > 60 || rsi < 40) trendScore += 0.5  // 中等趨勢

    // MACD 趨勢判斷
    if (Math.abs(macdSignal) > 0.5) trendScore += 1  // 強信號
    else if (Math.abs(macdSignal) > 0.2) trendScore += 0.5  // 中等信號

    // Stochastic 趨勢判斷
    if (stochK > 80 || stochK < 20) trendScore += 1  // 強勢區間
    else if (stochK > 70 || stochK < 30) trendScore += 0.5  // 中等區間

    // 趨勢倍數調整
    if (trendScore >= 2.5) trendMultiplier = 1.4      // 強趨勢：開放到4.8%
    else if (trendScore >= 1.5) trendMultiplier = 1.2  // 中等趨勢：適度放寬
    else if (trendScore >= 0.5) trendMultiplier = 1.0  // 弱趨勢：標準設定
    else trendMultiplier = 0.8                         // 震盪盤：控制在1.5-2%
  }

  // 🎖️ 信心度調整（高信心度要求更高收益）
  let confidenceMultiplier = 1.0
  if (signal.confidence > 0.9) confidenceMultiplier = 1.3      // 極高信心度
  else if (signal.confidence > 0.8) confidenceMultiplier = 1.2  // 高信心度+20%
  else if (signal.confidence > 0.6) confidenceMultiplier = 1.0  // 中等信心度
  else confidenceMultiplier = 0.8                              // 低信心度-20%

  // 💎 追單條件檢測（突破條件額外加成）
  let breakoutBonus = checkBreakoutConditions(signal)

  // 計算最終動態止盈點
  let finalThreshold = baseThreshold * atrMultiplier * trendMultiplier * confidenceMultiplier + breakoutBonus

  // 限制在合理範圍內：1.2% ~ 6.0%
  finalThreshold = Math.max(1.2, Math.min(6.0, finalThreshold))



  return finalThreshold
}

// 🚀 追單條件檢測（突破信號識別）
const checkBreakoutConditions = (signal: Signal): number => {
  let breakoutScore = 0

  // 檢查成交量突破（Volume Spike）
  if (signal.technical_summary?.volume_analysis) {
    const volumeRatio = signal.technical_summary.volume_analysis.relative_volume || 1
    if (volumeRatio > 2.0) breakoutScore += 0.8  // 成交量暴增
    else if (volumeRatio > 1.5) breakoutScore += 0.4  // 成交量增加
  }

  // 檢查價格突破（Price Breakout）
  if (signal.price_action) {
    if (signal.price_action.breakout_potential && signal.price_action.breakout_potential > 0.7) {
      breakoutScore += 0.6  // 高突破潛力
    }
  }

  // 檢查 MACD 雙金叉
  if (signal.key_indicators) {
    const macdLine = signal.key_indicators.macd_line || 0
    const macdSignal = signal.key_indicators.macd_signal || 0
    const macdHist = signal.key_indicators.macd_histogram || 0

    // MACD 金叉 + 柱狀圖向上
    if (macdLine > macdSignal && macdHist > 0) {
      breakoutScore += 0.5  // MACD 雙金叉
    }
  }

  // 檢查 RSI 突破關鍵位
  if (signal.key_indicators?.rsi) {
    const rsi = signal.key_indicators.rsi
    if ((rsi > 50 && rsi < 70) || (rsi < 50 && rsi > 30)) {
      breakoutScore += 0.3  // RSI 在動能區間
    }
  }

  // 檢查布林帶突破
  if (signal.bollinger_bands) {
    const currentPrice = signal.current_price || signal.entry_price || 0
    const upperBand = signal.bollinger_bands.upper || 0
    const lowerBand = signal.bollinger_bands.lower || 0

    if (currentPrice > upperBand || currentPrice < lowerBand) {
      breakoutScore += 0.7  // 布林帶突破
    }
  }


  return breakoutScore
}

// 🎯 判斷是否為突破信號（前端顯示用）
const isBreakoutSignal = (signal: Signal): boolean => {
  const breakoutScore = checkBreakoutConditions(signal)
  const dynamicThreshold = calculateDynamicStopProfit(signal)

  // 突破信號條件：
  // 1. 追單評分 > 1.5
  // 2. 動態止盈目標 > 3.5%
  // 3. 信心度 > 80%
  const isBreakout = breakoutScore > 1.5 && dynamicThreshold > 3.5 && signal.confidence > 0.8

  if (isBreakout) {

  }

  return isBreakout
}

// 注意：短線信號歷史記錄現在由後端處理，前端不再需要本地存儲

// 節流變數：防止過度頻繁的過期信號檢查
let lastExpiredCheckTime = 0
const EXPIRED_CHECK_THROTTLE = 25000 // 25秒節流

// 防重複歸檔鎖定
let isArchivingInProgress = false

// 專門處理過期短線信號的函數（簡化版 - 僅移除過期信號）
const processExpiredShortTermSignals = async (forceCheck = false) => {
  // 節流檢查：避免過度頻繁的檢查（手動觸發時可繞過）
  const now = Date.now()
  if (!forceCheck && now - lastExpiredCheckTime < EXPIRED_CHECK_THROTTLE) {

    return 0
  }

  lastExpiredCheckTime = now


  // 獲取已歸檔的歷史記錄 ID，避免重複歸檔
  const existingHistory = localStorage.getItem('tradingx_shortterm_history')
  const archivedSignalIds = new Set()
  if (existingHistory) {
    const historyData = JSON.parse(existingHistory)
    historyData.forEach((entry: any) => archivedSignalIds.add(entry.id))
  }


  const expiredSignals = shortTermSignals.value.filter(signal => {
    // 檢查是否已經歸檔過
    if (archivedSignalIds.has(signal.id)) {

      return false
    }

    const validityCheck = checkShortTermSignalValidity(signal)
    console.log(`信號檢查: ${signal.symbol} ${signal.signal_type} (ID: ${signal.id}) - ${validityCheck.isExpired ? '已過期' : '有效'}`)
    return validityCheck.isExpired
  })

  console.log(`找到 ${expiredSignals.length} 個待歸檔的過期信號:`, expiredSignals.map(s => `${s.symbol}(${s.id})`).join(', '))

  // 🔄 將過期信號歸檔到短線歷史記錄
  if (expiredSignals.length > 0) {
    // 歸檔過期信號到歷史記錄
    await archiveExpiredShortTermSignals(expiredSignals)

    // 移除過期信號
    const beforeCount = shortTermSignals.value.length
    shortTermSignals.value = shortTermSignals.value.filter(signal => {
      const validityCheck = checkShortTermSignalValidity(signal)
      return !validityCheck.isExpired
    })
    const afterCount = shortTermSignals.value.length

    // 🔥 更新統計數據，確保UI反映正確狀態
    updateShortTermStats()

    console.log(`🗑️ UI更新: ${beforeCount} → ${afterCount} 個信號，已移除 ${beforeCount - afterCount} 個過期信號`)
  }

  console.log(`✅ 清理完成，剩餘 ${shortTermSignals.value.length} 個有效信號`)
  return expiredSignals.length
}

// 🗂️ 將過期短線信號歸檔到後端數據庫
const archiveExpiredShortTermSignals = async (expiredSignals: Signal[]) => {
  // 防重複歸檔檢查
  if (isArchivingInProgress) {
    console.log(`⏸️ 歸檔進行中，跳過本次歸檔請求`)
    return
  }

  isArchivingInProgress = true
  console.log(`🔒 開始歸檔操作 - 鎖定中`)

  try {
    console.log(`🗂️ 開始歸檔 ${expiredSignals.length} 個過期短線信號到後端數據庫`)

    const signalsToBackend: any[] = []

    expiredSignals.forEach(signal => {
      const validityCheck = checkShortTermSignalValidity(signal)

      // 創建歷史記錄條目
      const historyEntry = {
        id: signal.id,
        symbol: signal.symbol,
        signal_type: signal.signal_type,
        entry_price: signal.entry_price,
        current_price: signal.current_price,
        confidence: signal.confidence,
        archived_at: new Date().toISOString(),
        archive_reason: 'expired',
        trade_result: validityCheck.result,
        profit_percent: validityCheck.profitPercent,
        strategy_name: signal.strategy_name || '短線專用',
        is_scalping: true,
        timestamp: signal.created_at || new Date().toISOString(),
        primary_timeframe: signal.primary_timeframe,
        signal_strength: signal.signal_strength,
        stop_loss: signal.stop_loss,
        take_profit: signal.take_profit,
        risk_reward_ratio: signal.risk_reward_ratio,
        reasoning: signal.reasoning,
        key_indicators: signal.key_indicators
      }

      // 準備發送到後端的數據
      signalsToBackend.push(historyEntry)
      console.log(`✅ 準備歸檔: ${signal.symbol} ${signal.signal_type} -> ${validityCheck.result} (${validityCheck.profitPercent.toFixed(2)}%)`)
    })

    // 🚀 同步到後端數據庫
    if (signalsToBackend.length > 0) {
      try {
        console.log(`🔄 正在同步 ${signalsToBackend.length} 個過期信號到後端數據庫...`)

        const response = await fetch('/api/v1/signals/archive-expired', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            signals: signalsToBackend
          })
        })

        if (response.ok) {
          const result = await response.json()
          console.log(`✅ 成功同步到後端: ${result.archived_count} 個信號`)
        } else {
          const errorText = await response.text()
          console.error(`❌ 後端同步失敗 (${response.status}): ${errorText}`)
          throw new Error(`後端同步失敗: ${response.status}`)
        }
      } catch (backendError) {
        console.error('❌ 後端同步請求失敗:', backendError)
        throw backendError // 拋出錯誤，因為沒有本地備份
      }
    } else {
      console.log(`ℹ️ 沒有新的信號需要歸檔`)
    }

    console.log(`🎯 歸檔總結: 預計歸檔 ${expiredSignals.length} 個過期信號`)

  } catch (error) {
    console.error('❌ 歸檔短線信號到後端數據庫失敗:', error)
    // 沒有本地備份，需要拋出錯誤以便重試機制處理
    throw error
  } finally {
    // 釋放歸檔鎖定
    isArchivingInProgress = false
    console.log(`🔓 歸檔操作完成 - 鎖定已釋放`)
  }
}

// 確保最少5個主要幣種的信號覆蓋
const ensureMinimumCoinCoverage = async () => {
  const targetCoins = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT']
  const currentCoins = new Set(shortTermSignals.value.map(s => s.symbol))
  const missingCoins = targetCoins.filter(coin => !currentCoins.has(coin))

  if (missingCoins.length > 0) {
    console.log(`缺少 ${missingCoins.length} 個主要幣種信號: ${missingCoins.join(', ')}`)

    // 獲取已歸檔的歷史記錄 ID，避免重新添加已處理過的信號
    const existingHistory = localStorage.getItem('tradingx_shortterm_history')
    const archivedSignalIds = new Set()
    if (existingHistory) {
      try {
        const historyData = JSON.parse(existingHistory)
        historyData.forEach((entry: any) => {
          if (entry.id) archivedSignalIds.add(entry.id)
        })
      } catch (error) {
        console.warn('無法解析歷史記錄:', error)
      }
    }

    // 嘗試從中長線信號中為缺失的幣種生成信號
    const aggressiveTimeframes = ['1m', '3m', '5m', '15m', '30m']

    missingCoins.forEach(coinSymbol => {
      const candidateSignals = latestSignals.value.filter(signal => {
        const hasShortTimeframe = aggressiveTimeframes.includes(signal.primary_timeframe || '') ||
          (signal.confirmed_timeframes && signal.confirmed_timeframes.some(tf => aggressiveTimeframes.includes(tf)))
        const hasDecentConfidence = signal.confidence >= 0.5
        const isTargetCoin = signal.symbol === coinSymbol

        // 重要：檢查信號是否已經被歸檔過
        const notAlreadyArchived = !archivedSignalIds.has(signal.id)

        // 重要：檢查信號是否會立即過期
        const validityCheck = checkShortTermSignalValidity(signal)
        const notExpired = !validityCheck.isExpired

        return hasShortTimeframe && hasDecentConfidence && isTargetCoin && notAlreadyArchived && notExpired
      })

      if (candidateSignals.length > 0) {
        // 選擇信心度最高的信號
        const bestSignal = candidateSignals.reduce((best, current) =>
          current.confidence > best.confidence ? current : best
        )

        // 檢查是否已經在短線信號中
        const alreadyExists = shortTermSignals.value.some(s => s.id === bestSignal.id)
        if (!alreadyExists) {
          shortTermSignals.value.push(bestSignal)
          console.log(`為 ${coinSymbol} 補充短線信號 (ID: ${bestSignal.id}, 信心度: ${Math.round(bestSignal.confidence * 100)}%)`)
        } else {
          console.log(`⚠️ 跳過 ${coinSymbol}：信號已存在 (ID: ${bestSignal.id})`)
        }
      } else {
        // console.log(`⚠️ 無法為 ${coinSymbol} 找到合適的信號 (可能已被歸檔或已過期)`)
      }
    })
  }
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
let countdownUpdateInterval: NodeJS.Timeout | null = null

// 即時倒數計時狀態
const currentTime = ref(new Date())

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

// 技術指標展開/收縮切換
const toggleIndicatorExpansion = (signalId: number | string) => {
  if (expandedIndicators.value.has(signalId)) {
    expandedIndicators.value.delete(signalId)
  } else {
    expandedIndicators.value.add(signalId)
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

  // 4. 檢查價格偏離度 - 分級警告和刪除機制
  if (signal.current_price && signal.entry_price) {
    const priceDeviation = Math.abs(signal.current_price - signal.entry_price) / signal.entry_price
    const direction = getSignalDirection(signal.signal_type)

    // 5% 偏離：警告但不刪除，可以在 UI 中顯示警告標識
    if (priceDeviation > 0.05) {
      // 不利方向的偏離檢查
      const isUnfavorableDirection =
        (direction === 'LONG' && signal.current_price < signal.entry_price) ||
        (direction === 'SHORT' && signal.current_price > signal.entry_price)

      if (isUnfavorableDirection) {
        // 8% 偏離：中等風險，考慮提醒用戶
        if (priceDeviation > 0.08) {
          // 12% 偏離：高風險，自動刪除信號
          if (priceDeviation > 0.12) {
            return {
              shouldDelete: true,
              reason: '價格嚴重偏離',
              isSuccess: false
            }
          }

          // 8-12% 偏離：暫時保留但標記高風險
          console.warn(`信號 ${signal.symbol} 價格偏離 ${(priceDeviation * 100).toFixed(1)}% (高風險)`)
        }

        // 5-8% 偏離：標記中風險
        if (priceDeviation > 0.05) {
          console.warn(`信號 ${signal.symbol} 價格偏離 ${(priceDeviation * 100).toFixed(1)}% (中風險)`)
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

// 移除未使用的模擬技術指標函數 (改用實際數據)
// 這些函數已被實際的技術指標數據取代

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
      return '做多'
    case 'SHORT':
      return '做空'
    default:
      return '未知'
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

// 分析信號來源和策略分佈
const analyzeSignalSources = (totalSignals: Signal[], shortTermSignals: Signal[]) => {
  // 策略名稱中文對照表 - 支援 strategy_name 和 pattern_detected
  const strategyMap: { [key: string]: string } = {
    // 短線策略名稱
    'enhanced_momentum': '增強動量',
    'breakout_scalp': '突破短線',
    'reversal_scalp': '反轉短線',
    'volume_scalp': '成交量短線',
    'momentum_scalp': '動量短線',
    'scalping_precision': '精準短線',

    // 圖表形態 (pattern_detected)
    '三重頂形態': '反轉形態',
    '頭肩底反轉': '反轉形態',
    '雙重底確認': '反轉形態',
    '看漲旗形整理': '整理形態',
    '楔形收斂突破': '突破形態',
    '頭肩頂': '反轉形態',
    '上升三角形': '突破形態',
    '下降楔形': '反轉形態',

    // 其他策略
    'trend_following': '趨勢跟隨',
    'mean_reversion': '均值回歸',
    'volume_breakout': '成交量突破',
    'advanced_scalping': '進階短線'
  }

  // 策略類型分類
  const getStrategyCategory = (signal: Signal): string => {
    const strategyName = signal.strategy_name || ''
    const patternName = (signal as any).pattern_detected || ''

    // 優先檢查 strategy_name
    if (strategyName) {
      if (strategyName.includes('scalp') || strategyName.includes('precision')) {
        return '精準短線'
      } else if (strategyName.includes('trend') || strategyName.includes('momentum')) {
        return '趨勢策略'
      } else if (strategyName.includes('reversal') || strategyName.includes('reversion')) {
        return '反轉策略'
      } else if (strategyName.includes('volume')) {
        return '成交量策略'
      } else if (strategyName.includes('breakout')) {
        return '突破策略'
      }
    }

    // 如果沒有 strategy_name，檢查 pattern_detected
    if (patternName) {
      if (patternName.includes('頂') || patternName.includes('底') || patternName.includes('反轉')) {
        return '反轉形態'
      } else if (patternName.includes('突破') || patternName.includes('三角') || patternName.includes('楔形')) {
        return '突破形態'
      } else if (patternName.includes('旗形') || patternName.includes('整理')) {
        return '整理形態'
      }
    }

    return '技術分析'
  }

  // 獲取信號顯示名稱
  const getSignalDisplayName = (signal: Signal): string => {
    const strategyName = signal.strategy_name || ''
    const patternName = (signal as any).pattern_detected || ''

    if (strategyName && strategyMap[strategyName]) {
      return strategyMap[strategyName]
    } else if (patternName && strategyMap[patternName]) {
      return strategyMap[patternName]
    } else if (patternName) {
      return patternName
    } else if (strategyName) {
      return strategyName
    }

    return '未知策略'
  }

  // 分析總信號
  const totalStrategies = new Set()
  const totalCategories = new Set()
  totalSignals.forEach(signal => {
    const displayName = getSignalDisplayName(signal)
    const category = getStrategyCategory(signal)
    totalStrategies.add(displayName)
    totalCategories.add(category)
  })

  // 分析短線信號
  const shortTermStrategies = new Set()
  const shortTermCategories = new Set()
  shortTermSignals.forEach(signal => {
    const displayName = getSignalDisplayName(signal)
    const category = getStrategyCategory(signal)
    shortTermStrategies.add(displayName)
    shortTermCategories.add(category)
  })

  return {
    totalStrategies: Array.from(totalCategories).join('、'),
    shortTermStrategies: Array.from(shortTermCategories).join('、'),
    totalStrategyDetails: Array.from(totalStrategies).join('、'),
    shortTermStrategyDetails: Array.from(shortTermStrategies).join('、')
  }
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

// 計算價格偏離風險等級
const calculatePriceDeviationRisk = (signal: Signal): { level: string; percentage: number; color: string; warning: string } => {
  if (!signal.current_price || !signal.entry_price) {
    return { level: 'unknown', percentage: 0, color: 'gray', warning: '' }
  }

  const priceDeviation = Math.abs(signal.current_price - signal.entry_price) / signal.entry_price
  const direction = getSignalDirection(signal.signal_type)

  // 檢查是否為不利方向
  const isUnfavorableDirection =
    (direction === 'LONG' && signal.current_price < signal.entry_price) ||
    (direction === 'SHORT' && signal.current_price > signal.entry_price)

  if (!isUnfavorableDirection) {
    // 有利方向：顯示盈利狀態
    return {
      level: 'profit',
      percentage: priceDeviation * 100,
      color: 'green',
      warning: `${direction === 'LONG' ? '上漲' : '下跌'} ${(priceDeviation * 100).toFixed(1)}%`
    }
  }

  // 不利方向：按風險等級分類
  if (priceDeviation > 0.12) {
    return {
      level: 'critical',
      percentage: priceDeviation * 100,
      color: 'red',
      warning: `嚴重偏離 -${(priceDeviation * 100).toFixed(1)}%`
    }
  } else if (priceDeviation > 0.08) {
    return {
      level: 'high',
      percentage: priceDeviation * 100,
      color: 'orange',
      warning: `高風險 -${(priceDeviation * 100).toFixed(1)}%`
    }
  } else if (priceDeviation > 0.05) {
    return {
      level: 'medium',
      percentage: priceDeviation * 100,
      color: 'yellow',
      warning: `中風險 -${(priceDeviation * 100).toFixed(1)}%`
    }
  } else {
    return {
      level: 'low',
      percentage: priceDeviation * 100,
      color: 'green',
      warning: '正常範圍'
    }
  }
}

// 獲取價格偏離風險標章樣式
const getPriceDeviationBadgeClass = (level: string): string => {
  const baseClasses = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium'

  switch (level) {
    case 'profit':
      return `${baseClasses} bg-green-100 text-green-800`
    case 'low':
      return `${baseClasses} bg-green-100 text-green-800`
    case 'medium':
      return `${baseClasses} bg-yellow-100 text-yellow-800`
    case 'high':
      return `${baseClasses} bg-orange-100 text-orange-800`
    case 'critical':
      return `${baseClasses} bg-red-100 text-red-800`
    default:
      return `${baseClasses} bg-gray-100 text-gray-800`
  }
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
    // 等待服務可用
    const serviceReady = await waitForService(5, 1000)
    if (!serviceReady) {
      console.warn('服務不可用，使用離線模式')
      serviceStatus.value.market_data = false
      serviceStatus.value.strategy_engine = false
      serviceStatus.value.backtest_service = false
      serviceStatus.value.database = false
      return
    }

    // 檢查市場數據服務
    try {
      await api.get('/api/v1/market/symbols')
      serviceStatus.value.market_data = true
    } catch {
      serviceStatus.value.market_data = false
    }

    // 檢查後端健康狀態
    const isHealthy = await checkHealth()
    serviceStatus.value.strategy_engine = isHealthy
    serviceStatus.value.backtest_service = isHealthy
    serviceStatus.value.database = isHealthy
  } catch (error) {
    console.error('檢查服務狀態失敗:', error)
    serviceStatus.value.market_data = false
    serviceStatus.value.strategy_engine = false
    serviceStatus.value.backtest_service = false
    serviceStatus.value.database = false
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

  } catch (error: any) {
    isLogRefreshing.value = false
    // 只在開發模式下輸出錯誤，避免生產環境的噪音
    if (process.env.NODE_ENV === 'development') {
      console.warn('獲取實時更新失敗 (非關鍵錯誤):', error?.message || error)
    }
    // 不顯示錯誤通知，因為這不是關鍵功能
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

    // 顯示載入結果通知，明確顯示信號來源和類型
    const shortTermCount = shortTermSignals.value.length
    const totalCount = latestSignals.value.length

    if (totalCount > 0) {
      // 分析信號來源和策略分佈
      const signalAnalysis = analyzeSignalSources(latestSignals.value, shortTermSignals.value)

      if (shortTermCount > 0) {
        showNotification('success', '儀表板數據載入成功',
          `已載入 ${shortTermCount} 個精準短線信號 (${signalAnalysis.shortTermStrategies})，總計 ${totalCount} 個交易信號 (${signalAnalysis.totalStrategies})`)
      } else {
        showNotification('info', '儀表板數據載入成功',
          `已載入 ${totalCount} 個交易信號 (${signalAnalysis.totalStrategies})，當前無符合條件的精準短線信號`)
      }
    } else {
      showNotification('info', '儀表板數據載入完成', '當前無活躍交易信號')
    }

  } catch (error) {
    hideLoading()
    console.error('獲取儀表板數據失敗:', error)
    showNotification('error', '儀表板數據載入失敗', '無法獲取交易信號數據，請稍後重試')
  }
}

onMounted(() => {
  // 載入即時建議
  loadInstantAdviceFromStorage()

  // 載入歷史紀錄
  loadSignalHistory()

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

  // 短線信號時效性檢查器：每30秒檢查一次過期信號
  setInterval(async () => {
    try {
      console.log(`⏰ 定時器觸發 - 開始檢查過期短線信號 (${new Date().toLocaleTimeString()})`)
      const expiredCount = await processExpiredShortTermSignals()
      if (expiredCount > 0) {
        console.log(`✅ 自動檢查：處理了 ${expiredCount} 個過期短線信號`)
        // 確保幣種覆蓋
        await ensureMinimumCoinCoverage()
      } else {
        console.log(`ℹ️ 自動檢查：沒有發現過期信號`)
      }
    } catch (error) {
      console.error('❌ 短線信號時效性檢查失敗:', error)
    }
  }, 30000) // 每30秒檢查一次

  // 設置系統日誌更新 (每3秒更新一次，原為5秒)
  logUpdateInterval = setInterval(() => {
    fetchRealtimeUpdates()
  }, 3000)

  // 即時倒數計時更新器：每秒更新當前時間
  countdownUpdateInterval = setInterval(() => {
    currentTime.value = new Date()
  }, 1000)

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

    // 檢查即時建議過期情況
    cleanupExpiredAdvice()
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

  // 即時建議專用定時器：每分鐘檢查一次過期情況
  setInterval(() => {
    cleanupExpiredAdvice()
  }, 60000) // 每分鐘檢查一次即時建議過期情況
})

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
  if (logUpdateInterval) {
    clearInterval(logUpdateInterval)
  }
  if (countdownUpdateInterval) {
    clearInterval(countdownUpdateInterval)
  }
})
</script>
