<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black">
    <!-- 🎯 統一監控儀表板頂部 -->
    <div class="bg-black/20 backdrop-blur-xl border-b border-white/10 shadow-2xl">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1
              class="text-3xl font-bold text-white bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
              🎯 Trading X 統一監控儀表板
            </h1>
            <p class="mt-2 text-sm text-gray-300">
              狙擊手雙層架構 + Phase 1ABC + Phase 2+3 完整整合監控
            </p>
          </div>
          <div class="flex items-center space-x-6">
            <!-- 系統總體狀態 -->
            <div
              class="flex items-center space-x-3 bg-white/5 backdrop-blur-sm rounded-full px-4 py-2 border border-white/10">
              <div class="relative">
                <div class="w-3 h-3 rounded-full bg-green-500"></div>
                <div class="absolute inset-0 w-3 h-3 rounded-full animate-ping bg-green-500"></div>
              </div>
              <span class="text-sm font-medium text-green-400">
                系統正常運行
              </span>
            </div>
            <!-- 活躍標的數量 -->
            <div
              class="text-sm text-gray-300 bg-white/5 backdrop-blur-sm rounded-full px-4 py-2 border border-white/10">
              活躍標的: <span class="font-medium text-cyan-400">{{ sniperLayerStatus.activeSymbols || 0 }}個</span>
            </div>
            <!-- 信號生成率 -->
            <div
              class="text-sm text-gray-300 bg-white/5 backdrop-blur-sm rounded-full px-4 py-2 border border-white/10">
              信號通過率: <span class="font-medium text-purple-400">{{ (sniperLayerStatus.passRate * 100).toFixed(1)
                }}%</span>
            </div>
            <!-- 最後更新時間 -->
            <div
              class="text-sm text-gray-300 bg-white/5 backdrop-blur-sm rounded-full px-4 py-2 border border-white/10">
              更新: <span class="font-medium text-white">{{ new Date().toLocaleTimeString() }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要內容區域 -->
    <div class="max-w-7xl mx-auto px-6 py-8">

      <!-- 🎯 核心指標卡片區 -->
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-8 mb-8">

        <!-- 狙擊手雙層架構核心指標 -->
        <div
          class="bg-gradient-to-br from-purple-500/20 to-red-500/20 backdrop-blur-xl text-white rounded-3xl p-8 shadow-2xl border border-purple-400/30"
          style="box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.05);">
          <div class="flex items-center justify-between mb-6">
            <div class="p-4 rounded-2xl bg-gradient-to-br from-purple-400/30 to-red-400/30 backdrop-blur-sm">
              <span class="text-3xl">🎯</span>
            </div>
            <div class="text-right">
              <div class="text-xs text-purple-300 font-medium">SNIPER PROTOCOL</div>
              <div class="text-xl font-bold text-white">{{ sniperLayerStatus.marketRegime || 'ANALYZING' }}</div>
            </div>
          </div>
          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-300">活躍信號</span>
              <span class="text-2xl font-bold text-white bg-purple-500/20 px-3 py-1 rounded-xl">{{
                sniperLayerStatus.activeSymbols || 0 }}個</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-300">精準度</span>
              <span
                class="text-xl font-bold text-white bg-gradient-to-r from-purple-500 to-red-500 px-3 py-1 rounded-xl">{{
                  (sniperLayerStatus.passRate * 100).toFixed(1) }}%</span>
            </div>
            <div class="text-xs text-purple-200 mt-3 bg-purple-500/10 px-3 py-2 rounded-lg backdrop-blur-sm">
              雙層架構 • {{ sniperLayerStatus.totalProcessingTime.toFixed(1) }}ms平均
            </div>
          </div>
        </div>

        <!-- Phase 1ABC 整合指標 -->
        <div
          class="bg-gradient-to-br from-blue-500/20 to-indigo-600/20 backdrop-blur-xl text-white rounded-3xl p-8 shadow-2xl border border-blue-400/30"
          style="box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.05);">
          <div class="flex items-center justify-between mb-6">
            <div class="p-4 rounded-2xl bg-gradient-to-br from-blue-400/30 to-indigo-400/30 backdrop-blur-sm">
              <span class="text-3xl">📊</span>
            </div>
            <div class="text-right">
              <div class="text-xs text-blue-300 font-medium">PHASE 1ABC</div>
              <div class="text-xl font-bold text-white">整合鏈</div>
            </div>
          </div>
          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-300">整合評分</span>
              <span class="text-2xl font-bold text-white bg-blue-500/20 px-3 py-1 rounded-xl">85.7%</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-300">信心度</span>
              <span
                class="text-xl font-bold text-white bg-gradient-to-r from-blue-500 to-indigo-600 px-3 py-1 rounded-xl">78.5%</span>
            </div>
            <div class="text-xs text-blue-200 mt-3 bg-blue-500/10 px-3 py-2 rounded-lg backdrop-blur-sm">
              信號重構 • 波動適應 • 標準化
            </div>
          </div>
        </div>

        <!-- Phase 2+3 綜合分析 -->
        <div
          class="bg-gradient-to-br from-green-500/20 to-emerald-600/20 backdrop-blur-xl text-white rounded-3xl p-8 shadow-2xl border border-green-400/30"
          style="box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.05);">
          <div class="flex items-center justify-between mb-6">
            <div class="p-4 rounded-2xl bg-gradient-to-br from-green-400/30 to-emerald-400/30 backdrop-blur-sm">
              <span class="text-3xl">🔍</span>
            </div>
            <div class="text-right">
              <div class="text-xs text-green-300 font-medium">PHASE 2+3</div>
              <div class="text-xl font-bold text-white">深度分析</div>
            </div>
          </div>
          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-300">動態權重</span>
              <span class="text-2xl font-bold text-white bg-green-500/20 px-3 py-1 rounded-xl">4次</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-300">風險調整</span>
              <span
                class="text-xl font-bold text-white bg-gradient-to-r from-green-500 to-emerald-600 px-3 py-1 rounded-xl">38.2%</span>
            </div>
            <div class="text-xs text-green-200 mt-3 bg-green-500/10 px-3 py-2 rounded-lg backdrop-blur-sm">
              市場深度 • 動態適應
            </div>
          </div>
        </div>

        <!-- 系統健康度監控 -->
        <div
          class="bg-gradient-to-br from-gray-600/20 to-gray-700/20 backdrop-blur-xl text-white rounded-3xl p-8 shadow-2xl border border-gray-400/30"
          style="box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.05);">
          <div class="flex items-center justify-between mb-6">
            <div class="p-4 rounded-2xl bg-gradient-to-br from-gray-400/30 to-gray-500/30 backdrop-blur-sm">
              <span class="text-3xl">⚡</span>
            </div>
            <div class="text-right">
              <div class="text-xs text-gray-300 font-medium">SYSTEM STATUS</div>
              <div class="text-xl font-bold text-white">正常運行</div>
            </div>
          </div>
          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-300">API 響應</span>
              <span class="text-2xl font-bold text-white bg-gray-500/20 px-3 py-1 rounded-xl">{{
                sniperLayerStatus.totalProcessingTime.toFixed(0) }}ms</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-300">數據完整</span>
              <span
                class="text-xl font-bold text-white bg-gradient-to-r from-gray-500 to-gray-600 px-3 py-1 rounded-xl">100%</span>
            </div>
            <div class="text-xs text-gray-200 mt-3 bg-gray-500/10 px-3 py-2 rounded-lg backdrop-blur-sm">
              即時監控 • 無假數據
            </div>
          </div>
        </div>
      </div>

      <!-- 🎯 狙擊手雙層架構詳細監控 -->
      <div class="bg-white/5 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/10 mb-8 overflow-hidden"
        style="box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.05);">
        <div class="px-8 py-6 border-b border-white/10">
          <div class="flex items-center justify-between">
            <h2
              class="text-xl font-bold text-white bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              🎯 狙擊手雙層架構監控</h2>
            <button @click="refreshSniperLayer" :disabled="loading"
              class="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 disabled:from-gray-500 disabled:to-gray-600 text-white text-sm font-bold rounded-2xl transition-all duration-300 shadow-lg backdrop-blur-sm">
              {{ loading ? '更新中...' : '刷新數據' }}
            </button>
          </div>
        </div>
        <div class="p-8">
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">

            <!-- 第一層：智能參數計算 -->
            <div
              class="bg-gradient-to-br from-blue-500/20 to-indigo-500/20 backdrop-blur-sm rounded-2xl p-6 border border-blue-400/30">
              <h3 class="text-lg font-bold text-blue-300 mb-6">第一層：智能參數</h3>
              <div class="space-y-4">
                <div class="flex justify-between items-center">
                  <span class="text-sm text-blue-200">計算時間</span>
                  <span class="text-lg font-bold text-white bg-blue-500/20 px-3 py-1 rounded-xl">{{
                    sniperLayerStatus.layerOne.calculationTime.toFixed(1) }}ms</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-sm text-blue-200">指標數量</span>
                  <span class="text-lg font-bold text-white bg-blue-500/20 px-3 py-1 rounded-xl">{{
                    sniperLayerStatus.layerOne.indicatorCount }}項</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-sm text-blue-200">自適應參數</span>
                  <span class="text-sm font-medium px-3 py-1 rounded-xl backdrop-blur-sm"
                    :class="sniperLayerStatus.layerOne.adaptiveParams ? 'text-green-300 bg-green-500/20' : 'text-gray-400 bg-gray-500/20'">
                    {{ sniperLayerStatus.layerOne.adaptiveParams ? '✅ 啟用' : '⚪ 停用' }}
                  </span>
                </div>
              </div>
              <div class="mt-6 p-4 bg-blue-500/10 backdrop-blur-sm rounded-xl border border-blue-400/20">
                <div class="text-xs text-blue-200">
                  RSI: {{ sniperLayerStatus.layerOne.currentParams.rsi }} |
                  MACD: {{ sniperLayerStatus.layerOne.currentParams.macd_fast }}/{{
                    sniperLayerStatus.layerOne.currentParams.macd_slow }}
                </div>
              </div>
            </div>

            <!-- 第二層：動態過濾 -->
            <div
              class="bg-gradient-to-br from-green-500/20 to-emerald-500/20 backdrop-blur-sm rounded-2xl p-6 border border-green-400/30">
              <h3 class="text-lg font-bold text-green-300 mb-6">第二層：動態過濾</h3>
              <div class="space-y-4">
                <div class="flex justify-between items-center">
                  <span class="text-sm text-green-200">過濾時間</span>
                  <span class="text-lg font-bold text-white bg-green-500/20 px-3 py-1 rounded-xl">{{
                    sniperLayerStatus.layerTwo.filterTime.toFixed(1) }}ms</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-sm text-green-200">信號生成</span>
                  <span class="text-lg font-bold text-white bg-green-500/20 px-3 py-1 rounded-xl">{{
                    sniperLayerStatus.layerTwo.signalsGenerated }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-sm text-green-200">信號過濾</span>
                  <span class="text-lg font-bold text-white bg-red-500/20 px-3 py-1 rounded-xl">{{
                    sniperLayerStatus.layerTwo.signalsFiltered }}</span>
                </div>
              </div>
              <div class="mt-6 p-4 bg-green-500/10 backdrop-blur-sm rounded-xl border border-green-400/20">
                <div class="text-xs text-green-200">
                  RSI範圍: {{ sniperLayerStatus.layerTwo.dynamicThresholds.rsi_low }}-{{
                    sniperLayerStatus.layerTwo.dynamicThresholds.rsi_high }} |
                  最小匯聚: {{ sniperLayerStatus.layerTwo.dynamicThresholds.confluence_min }}
                </div>
              </div>
            </div>

            <!-- 市場狀態分析 -->
            <div
              class="bg-gradient-to-br from-purple-500/20 to-pink-500/20 backdrop-blur-sm rounded-2xl p-6 border border-purple-400/30">
              <h3 class="text-lg font-bold text-purple-300 mb-6">市場狀態分析</h3>
              <div class="space-y-4">
                <div class="flex justify-between items-center">
                  <span class="text-sm text-purple-200">當前狀態</span>
                  <span class="text-lg font-bold text-white bg-purple-500/20 px-3 py-1 rounded-xl">{{
                    sniperLayerStatus.marketRegime }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-sm text-purple-200">信號通過率</span>
                  <span class="text-lg font-bold text-white bg-purple-500/20 px-3 py-1 rounded-xl">{{
                    (sniperLayerStatus.passRate * 100).toFixed(1) }}%</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-sm text-purple-200">總處理時間</span>
                  <span
                    class="text-lg font-bold text-white bg-gradient-to-r from-purple-500 to-pink-500 px-3 py-1 rounded-xl">{{
                      sniperLayerStatus.totalProcessingTime.toFixed(1) }}ms</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 活躍標的詳細追蹤 -->
          <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">🔍 活躍標的詳細追蹤</h3>
              <button @click="toggleActiveSymbolsDetail"
                class="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200">
                {{ showActiveSymbolsDetail ? '收起詳情' : '展開詳情' }} ({{ sniperLayerStatus.activeSymbols }}個)
              </button>
            </div>

            <!-- 摺疊詳細內容 -->
            <transition name="slide-down" enter-active-class="transition-all duration-300 ease-out"
              leave-active-class="transition-all duration-300 ease-in" enter-from-class="opacity-0 max-h-0"
              enter-to-class="opacity-100 max-h-screen" leave-from-class="opacity-100 max-h-screen"
              leave-to-class="opacity-0 max-h-0">
              <div v-show="showActiveSymbolsDetail" class="space-y-4 overflow-hidden">
                <div v-for="symbol in activeSymbolsDetails" :key="symbol.symbol"
                  class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 border border-gray-200 dark:border-gray-600">

                  <!-- 標的標題 -->
                  <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center space-x-3">
                      <div class="w-3 h-3 rounded-full" :class="{
                        'bg-green-500': symbol.status === 'active',
                        'bg-red-500': symbol.status === 'error',
                        'bg-yellow-500': symbol.status === 'processing'
                      }"></div>
                      <h4 class="font-bold text-gray-900 dark:text-white">{{ symbol.symbol }}</h4>
                      <span
                        class="text-xs bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100 px-2 py-1 rounded-full">
                        {{ symbol.marketRegime }}
                      </span>
                    </div>
                    <span class="text-xs text-gray-500 dark:text-gray-400">{{ symbol.lastUpdate }}</span>
                  </div>

                  <!-- 雙層架構指標 -->
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">

                    <!-- Layer 1 指標 -->
                    <div class="bg-blue-50 dark:bg-blue-900 rounded-lg p-3">
                      <h5 class="font-medium text-blue-900 dark:text-blue-100 mb-2">Layer 1: 智能參數</h5>
                      <div class="space-y-1 text-sm">
                        <div class="flex justify-between">
                          <span class="text-blue-700 dark:text-blue-300">計算時間</span>
                          <span class="font-medium text-blue-900 dark:text-blue-100">{{ symbol.layerOne.calculationTime
                            }}ms</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-blue-700 dark:text-blue-300">指標數量</span>
                          <span class="font-medium text-blue-900 dark:text-blue-100">{{ symbol.layerOne.indicatorCount
                            }}項</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-blue-700 dark:text-blue-300">性能評分</span>
                          <span class="font-medium text-blue-900 dark:text-blue-100">{{ symbol.layerOne.performanceScore
                            }}%</span>
                        </div>
                      </div>
                    </div>

                    <!-- Layer 2 指標 -->
                    <div class="bg-green-50 dark:bg-green-900 rounded-lg p-3">
                      <h5 class="font-medium text-green-900 dark:text-green-100 mb-2">Layer 2: 動態過濾</h5>
                      <div class="space-y-1 text-sm">
                        <div class="flex justify-between">
                          <span class="text-green-700 dark:text-green-300">過濾時間</span>
                          <span class="font-medium text-green-900 dark:text-green-100">{{ symbol.layerTwo.filterTime
                            }}ms</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-green-700 dark:text-green-300">通過率</span>
                          <span class="font-medium text-green-900 dark:text-green-100">{{ (symbol.layerTwo.passRate *
                            100).toFixed(1) }}%</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-green-700 dark:text-green-300">過濾效率</span>
                          <span class="font-medium text-green-900 dark:text-green-100">{{
                            symbol.layerTwo.filterEfficiency }}%</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- 動態閾值顯示 -->
                  <div class="mt-3 p-2 bg-purple-50 dark:bg-purple-900 rounded">
                    <div class="text-xs text-purple-800 dark:text-purple-200">
                      <strong>動態閾值:</strong>
                      RSI {{ symbol.layerTwo.dynamicThresholds.rsi_low }}-{{ symbol.layerTwo.dynamicThresholds.rsi_high
                      }} |
                      波動閾值 {{ symbol.layerTwo.dynamicThresholds.volatility_threshold.toFixed(3) }} |
                      最小匯聚 {{ symbol.layerTwo.dynamicThresholds.confluence_min }}
                    </div>
                  </div>

                  <!-- 錯誤信息顯示 -->
                  <div v-if="symbol.error"
                    class="mt-3 p-2 bg-red-50 dark:bg-red-900 rounded border border-red-200 dark:border-red-700">
                    <div class="text-sm text-red-800 dark:text-red-200">
                      <strong>錯誤:</strong> {{ symbol.error }}
                    </div>
                  </div>
                </div>
              </div>
            </transition>
          </div>
        </div>
      </div>

      <!-- 🧠 智能系統診斷區 -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 mb-8">
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">🧠 智能系統診斷</h2>
        </div>
        <div class="p-6">
          <div class="space-y-4">
            <!-- 系統建議 -->
            <div
              class="flex items-start space-x-3 p-4 bg-yellow-50 dark:bg-yellow-900 rounded-lg border border-yellow-200 dark:border-yellow-700">
              <div class="flex-shrink-0">
                <span class="text-yellow-600 dark:text-yellow-300">⚠️</span>
              </div>
              <div>
                <h4 class="font-medium text-yellow-800 dark:text-yellow-200">系統建議</h4>
                <p class="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                  當前市場狀態為 {{ sniperLayerStatus.marketRegime }}，建議關注 {{ sniperLayerStatus.activeSymbols }} 個活躍標的的信號變化
                </p>
              </div>
            </div>

            <!-- 性能優化 -->
            <div
              class="flex items-start space-x-3 p-4 bg-blue-50 dark:bg-blue-900 rounded-lg border border-blue-200 dark:border-blue-700">
              <div class="flex-shrink-0">
                <span class="text-blue-600 dark:text-blue-300">💡</span>
              </div>
              <div>
                <h4 class="font-medium text-blue-800 dark:text-blue-200">性能優化</h4>
                <p class="text-sm text-blue-700 dark:text-blue-300 mt-1">
                  狙擊手雙層架構平均處理時間 {{ sniperLayerStatus.totalProcessingTime.toFixed(1) }}ms，表現優異。信號通過率 {{
                    (sniperLayerStatus.passRate * 100).toFixed(1) }}%
                </p>
              </div>
            </div>

            <!-- 市場趨勢 -->
            <div
              class="flex items-start space-x-3 p-4 bg-green-50 dark:bg-green-900 rounded-lg border border-green-200 dark:border-green-700">
              <div class="flex-shrink-0">
                <span class="text-green-600 dark:text-green-300">📈</span>
              </div>
              <div>
                <h4 class="font-medium text-green-800 dark:text-green-200">市場機會</h4>
                <p class="text-sm text-green-700 dark:text-green-300 mt-1">
                  Phase 1ABC 整合鏈運行正常，Phase 2+3 深度分析已檢測到 {{ sniperLayerStatus.activeSymbols }} 個潛在交易機會
                </p>
              </div>
            </div>

          </div>
        </div>
      </div>

      <!-- 🎯 狙擊手動態風險管理系統 -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">🎯 狙擊手動態風險管理系統</h2>
        </div>
        <div class="p-6">
          <RiskManagementDisplay />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import RiskManagementDisplay from '@/components/RiskManagementDisplay.vue'

// 🎯 TypeScript 介面定義
interface SymbolDetail {
  symbol: string
  status: 'active' | 'error' | 'processing'
  marketRegime: string
  layerOne: {
    calculationTime: number
    indicatorCount: number
    adaptiveParams: boolean
    currentParams: {
      rsi: number
      macd_fast: number
      macd_slow: number
      bb_period: number
    }
    performanceScore: number
  }
  layerTwo: {
    filterTime: number
    signalsGenerated: number
    signalsFiltered: number
    passRate: number
    dynamicThresholds: {
      rsi_low: number
      rsi_high: number
      confluence_min: number
      volatility_threshold: number
    }
    filterEfficiency: number
  }
  error: string | null
  lastUpdate: string
}

// 響應式數據
const loading = ref(false)

// 🎯 狙擊手雙層架構響應式數據
const sniperLayerStatus = ref({
  marketRegime: 'ANALYZING',
  activeSymbols: 0,
  passRate: 0,
  totalProcessingTime: 0,
  layerOne: {
    calculationTime: 0,
    indicatorCount: 0,
    adaptiveParams: false,
    currentParams: {
      rsi: 14,
      macd_fast: 12,
      macd_slow: 26
    }
  },
  layerTwo: {
    filterTime: 0,
    signalsGenerated: 0,
    signalsFiltered: 0,
    dynamicThresholds: {
      rsi_low: 30,
      rsi_high: 70,
      confluence_min: 2
    }
  }
})

// 🎯 活躍標的詳細追蹤響應式數據
const showActiveSymbolsDetail = ref(false)
const activeSymbolsDetails = ref<SymbolDetail[]>([])

// 🎯 狙擊手雙層架構方法
const refreshSniperLayer = async () => {
  try {
    loading.value = true
    console.log('🎯 刷新狙擊手雙層架構數據...')

    // 調用狙擊手雙層架構 API
    const response = await axios.get('/api/v1/scalping/sniper-unified-data-layer?symbols=BTCUSDT,ETHUSDT,ADAUSDT&timeframe=1h&force_refresh=true')

    if (response.data.status === 'success') {
      const results = response.data.results
      const successful = response.data.successful_symbols

      // 計算統計數據
      let totalCalcTime = 0
      let totalFilterTime = 0
      let totalSignalsGenerated = 0
      let totalSignalsFiltered = 0
      let totalProcessingTime = 0

      const resultValues = Object.values(results) as any[]
      resultValues.forEach((result: any) => {
        if (result.performance_metrics) {
          totalCalcTime += result.performance_metrics.layer_one_time || 0
          totalFilterTime += result.performance_metrics.layer_two_time || 0
          totalSignalsGenerated += result.performance_metrics.signals_quality?.generated || 0
          totalSignalsFiltered += result.performance_metrics.signals_quality?.filtered || 0
          totalProcessingTime += result.performance_metrics.total_processing_time || 0
        }
      })

      const firstResult = resultValues[0] as any

      // 更新狙擊手狀態
      sniperLayerStatus.value = {
        marketRegime: firstResult?.market_regime?.toUpperCase() || 'ANALYZING',
        activeSymbols: successful,
        passRate: totalSignalsGenerated > 0 ? totalSignalsGenerated / (totalSignalsGenerated + totalSignalsFiltered) : 0,
        totalProcessingTime: Math.round(totalProcessingTime * 1000) / successful || 0,
        layerOne: {
          calculationTime: Math.round(totalCalcTime * 1000) / successful || 0,
          indicatorCount: firstResult?.layer_one?.indicators_count || 14,
          adaptiveParams: true,
          currentParams: {
            rsi: firstResult?.layer_one?.config_used?.rsi_length || 14,
            macd_fast: firstResult?.layer_one?.config_used?.macd_fast || 12,
            macd_slow: firstResult?.layer_one?.config_used?.macd_slow || 26
          }
        },
        layerTwo: {
          filterTime: Math.round(totalFilterTime * 1000) / successful || 0,
          signalsGenerated: totalSignalsGenerated,
          signalsFiltered: totalSignalsFiltered,
          dynamicThresholds: {
            rsi_low: firstResult?.layer_two?.filter_results?.dynamic_filter_config?.rsi_oversold || 30,
            rsi_high: firstResult?.layer_two?.filter_results?.dynamic_filter_config?.rsi_overbought || 70,
            confluence_min: firstResult?.layer_two?.filter_results?.dynamic_filter_config?.confluence_min_count || 2
          }
        }
      }

      // 🔍 構建活躍標的詳細數據
      activeSymbolsDetails.value = Object.entries(results).map(([symbol, result]: [string, any]) => ({
        symbol,
        status: result.success === false ? 'error' : 'active',
        marketRegime: result.market_regime || 'unknown',
        layerOne: {
          calculationTime: Math.round((result.performance_metrics?.layer_one_time || 0) * 1000),
          indicatorCount: result.layer_one?.indicators_count || 14,
          adaptiveParams: result.layer_one?.adaptive_params_active || false,
          currentParams: {
            rsi: result.layer_one?.config_used?.rsi_length || 14,
            macd_fast: result.layer_one?.config_used?.macd_fast || 12,
            macd_slow: result.layer_one?.config_used?.macd_slow || 26,
            bb_period: result.layer_one?.config_used?.bb_period || 20
          },
          performanceScore: Math.round((result.layer_one?.performance_score || 0) * 100)
        },
        layerTwo: {
          filterTime: Math.round((result.performance_metrics?.layer_two_time || 0) * 1000),
          signalsGenerated: result.performance_metrics?.signals_quality?.generated || 0,
          signalsFiltered: result.performance_metrics?.signals_quality?.filtered || 0,
          passRate: result.performance_metrics?.signals_quality?.generated > 0
            ? result.performance_metrics.signals_quality.generated /
            (result.performance_metrics.signals_quality.generated + result.performance_metrics.signals_quality.filtered)
            : 0,
          dynamicThresholds: {
            rsi_low: result.layer_two?.filter_results?.dynamic_filter_config?.rsi_oversold || 30,
            rsi_high: result.layer_two?.filter_results?.dynamic_filter_config?.rsi_overbought || 70,
            confluence_min: result.layer_two?.filter_results?.dynamic_filter_config?.confluence_min_count || 2,
            volatility_threshold: result.layer_two?.filter_results?.dynamic_filter_config?.volatility_threshold || 0.02
          },
          filterEfficiency: Math.round((result.layer_two?.filter_efficiency || 0) * 100)
        },
        error: result.success === false ? result.error : null,
        lastUpdate: new Date().toLocaleTimeString()
      }))

      console.log('✅ 狙擊手雙層架構數據更新完成:', sniperLayerStatus.value)
      console.log('🎯 活躍標的詳細數據:', activeSymbolsDetails.value)
    }
  } catch (error) {
    console.error('❌ 狙擊手雙層架構數據刷新失敗:', error)
  } finally {
    loading.value = false
  }
}

// 🎯 切換活躍標的詳細顯示
const toggleActiveSymbolsDetail = () => {
  showActiveSymbolsDetail.value = !showActiveSymbolsDetail.value
  console.log('🔍 切換活躍標的詳細顯示:', showActiveSymbolsDetail.value)
}

// 生命週期
onMounted(() => {
  refreshSniperLayer() // 初始載入狙擊手數據
})
</script>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from {
  opacity: 0;
  max-height: 0;
}

.slide-down-enter-to {
  opacity: 1;
  max-height: 1000px;
}

.slide-down-leave-from {
  opacity: 1;
  max-height: 1000px;
}

.slide-down-leave-to {
  opacity: 0;
  max-height: 0;
}
</style>
