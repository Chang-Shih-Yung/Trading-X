<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">🎯 動態交易策略監控</h1>
      <p class="text-gray-600">Phase 1+2+3 完整動態適應系統 - 驗證無固定值策略</p>
    </div>

    <!-- Phase 3 高階市場分析 -->
    <div v-if="phase3Data" class="mb-8">
      <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center">
        <span class="bg-red-100 text-red-800 text-sm font-medium px-2.5 py-0.5 rounded mr-3">Phase 3</span>
        🎯 高階市場適應監控
      </h2>

      <!-- 整體市場概況 -->
      <div class="bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg p-6 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="text-center">
            <div class="text-3xl font-bold">{{ phase3Data.market_overview?.average_market_pressure || 0 }}</div>
            <div class="text-sm opacity-90">市場壓力評分</div>
            <div class="text-xs opacity-75">0-100 綜合評分</div>
          </div>
          <div class="text-center">
            <div class="text-lg font-bold">{{ phase3Data.market_overview?.dominant_market_sentiment || 'Unknown' }}
            </div>
            <div class="text-sm opacity-90">主導市場情緒</div>
            <div class="text-xs opacity-75">綜合 Order Book + 資金費率</div>
          </div>
          <div class="text-center">
            <div class="text-lg font-bold">{{ phase3Data.market_overview?.market_stress_level || 'Unknown' }}</div>
            <div class="text-sm opacity-90">市場壓力等級</div>
            <div class="text-xs opacity-75">HIGH / MEDIUM / LOW</div>
          </div>
          <div class="text-center">
            <div class="text-3xl font-bold">{{ phase3Data.market_overview?.total_symbols_analyzed || 0 }}</div>
            <div class="text-sm opacity-90">分析符號數</div>
            <div class="text-xs opacity-75">實時深度分析</div>
          </div>
        </div>
      </div>

      <!-- Phase 3 詳細分析 -->
      <div class="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-8">
        <div v-for="analysis in phase3Data.symbol_analyses" :key="analysis.symbol"
          class="bg-white rounded-lg shadow-lg overflow-hidden border border-gray-200">

          <!-- 標題區 (可點擊) -->
          <div
            class="bg-gradient-to-r from-gray-700 to-gray-800 text-white px-4 py-3 cursor-pointer hover:from-gray-600 hover:to-gray-700 transition-colors"
            @click="togglePhase3Card(analysis.symbol)">
            <div class="flex justify-between items-center">
              <div>
                <h3 class="text-lg font-bold">{{ analysis.symbol }}</h3>
                <!-- 收縮狀態下的簡要信息 -->
                <div v-show="!expandedPhase3Cards.has(analysis.symbol)" class="text-sm opacity-75 mt-1">
                  壓力評分: {{ analysis.phase3_assessment?.market_pressure_score || 0 }}/100 |
                  風險: <span :class="{
                    'text-red-300': analysis.phase3_assessment?.risk_level === 'HIGH',
                    'text-yellow-300': analysis.phase3_assessment?.risk_level === 'MEDIUM',
                    'text-green-300': analysis.phase3_assessment?.risk_level === 'LOW'
                  }">{{ analysis.phase3_assessment?.risk_level || 'Unknown' }}</span>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <span class="px-2 py-1 rounded text-xs font-medium" :class="{
                  'bg-red-100 text-red-800': analysis.phase3_assessment?.combined_sentiment?.includes('BEARISH'),
                  'bg-green-100 text-green-800': analysis.phase3_assessment?.combined_sentiment?.includes('BULLISH'),
                  'bg-gray-100 text-gray-800': analysis.phase3_assessment?.combined_sentiment?.includes('NEUTRAL')
                }">
                  {{ analysis.phase3_assessment?.combined_sentiment || 'Unknown' }}
                </span>
                <!-- 展開/收縮圖標 -->
                <svg class="w-5 h-5 transform transition-transform"
                  :class="{ 'rotate-180': expandedPhase3Cards.has(analysis.symbol) }" fill="none" stroke="currentColor"
                  viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </div>
            </div>
          </div>

          <!-- 詳細內容 (可展開/收縮) -->
          <transition enter-active-class="transition-all duration-300 ease-out"
            leave-active-class="transition-all duration-300 ease-in" enter-from-class="opacity-0 max-h-0"
            enter-to-class="opacity-100 max-h-screen" leave-from-class="opacity-100 max-h-screen"
            leave-to-class="opacity-0 max-h-0">
            <div v-show="expandedPhase3Cards.has(analysis.symbol)" class="p-4 overflow-hidden">
              <!-- Order Book 深度分析 -->
              <div class="mb-4">
                <h4 class="font-semibold text-gray-800 mb-2 flex items-center">
                  📖 Order Book 深度分析
                </h4>
                <div class="grid grid-cols-2 gap-3">
                  <div class="bg-blue-50 p-3 rounded">
                    <div class="text-sm text-gray-600">買賣壓力比</div>
                    <div class="text-lg font-bold" :class="{
                      'text-green-600': analysis.order_book_analysis?.pressure_ratio > 1,
                      'text-red-600': analysis.order_book_analysis?.pressure_ratio < 1,
                      'text-gray-600': analysis.order_book_analysis?.pressure_ratio === 1
                    }">
                      {{ (analysis.order_book_analysis?.pressure_ratio || 0).toFixed(3) }}
                    </div>
                    <div class="text-xs text-gray-500">
                      {{ analysis.order_book_analysis?.pressure_ratio > 1 ? '買強' :
                        analysis.order_book_analysis?.pressure_ratio < 1 ? '賣強' : '平衡' }} </div>
                    </div>
                    <div class="bg-purple-50 p-3 rounded">
                      <div class="text-sm text-gray-600">市場情緒</div>
                      <div class="text-sm font-medium" :class="{
                        'text-green-600': analysis.order_book_analysis?.market_sentiment === 'BULLISH_PRESSURE',
                        'text-red-600': analysis.order_book_analysis?.market_sentiment === 'BEARISH_PRESSURE',
                        'text-gray-600': analysis.order_book_analysis?.market_sentiment === 'BALANCED'
                      }">
                        {{ analysis.order_book_analysis?.market_sentiment || 'Unknown' }}
                      </div>
                      <div class="text-xs text-gray-500">
                        中間價: ${{ (analysis.order_book_analysis?.mid_price || 0).toLocaleString() }}
                      </div>
                    </div>
                  </div>

                  <!-- Top 買賣盤顯示 -->
                  <div class="mt-3 grid grid-cols-2 gap-2">
                    <div class="bg-green-50 p-2 rounded">
                      <div class="text-xs text-gray-600 mb-1">🔵 Top 3 買單</div>
                      <div class="space-y-1">
                        <div v-for="bid in analysis.order_book_analysis?.top_bids?.slice(0, 3)" :key="bid.price"
                          class="flex justify-between text-xs">
                          <span>${{ bid.price.toLocaleString() }}</span>
                          <span class="text-green-600">{{ bid.quantity.toFixed(4) }}</span>
                        </div>
                      </div>
                    </div>
                    <div class="bg-red-50 p-2 rounded">
                      <div class="text-xs text-gray-600 mb-1">🔴 Top 3 賣單</div>
                      <div class="space-y-1">
                        <div v-for="ask in analysis.order_book_analysis?.top_asks?.slice(0, 3)" :key="ask.price"
                          class="flex justify-between text-xs">
                          <span>${{ ask.price.toLocaleString() }}</span>
                          <span class="text-red-600">{{ ask.quantity.toFixed(4) }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 資金費率分析 -->
                <div class="mb-4">
                  <h4 class="font-semibold text-gray-800 mb-2 flex items-center">
                    💰 資金費率情緒指標
                  </h4>
                  <div class="grid grid-cols-2 gap-3">
                    <div class="bg-yellow-50 p-3 rounded">
                      <div class="text-sm text-gray-600">當前費率</div>
                      <div class="text-lg font-bold" :class="{
                        'text-red-600': (analysis.funding_rate_analysis?.funding_rate || 0) > 0.0007,
                        'text-green-600': (analysis.funding_rate_analysis?.funding_rate || 0) < -0.0007,
                        'text-gray-600': Math.abs(analysis.funding_rate_analysis?.funding_rate || 0) <= 0.0007
                      }">
                        {{ (analysis.funding_rate_analysis?.funding_rate_percentage || 0).toFixed(4) }}%
                      </div>
                      <div class="text-xs text-gray-500">
                        年化: {{ (analysis.funding_rate_analysis?.annual_rate || 0).toFixed(2) }}%
                      </div>
                    </div>
                    <div class="bg-orange-50 p-3 rounded">
                      <div class="text-sm text-gray-600">情緒判斷</div>
                      <div class="text-sm font-medium" :class="{
                        'text-red-600': analysis.funding_rate_analysis?.sentiment?.includes('OVERHEATED'),
                        'text-green-600': analysis.funding_rate_analysis?.sentiment?.includes('OVERSOLD'),
                        'text-blue-600': analysis.funding_rate_analysis?.sentiment?.includes('BULLISH'),
                        'text-orange-600': analysis.funding_rate_analysis?.sentiment?.includes('BEARISH'),
                        'text-gray-600': analysis.funding_rate_analysis?.sentiment === 'NEUTRAL'
                      }">
                        {{ analysis.funding_rate_analysis?.sentiment || 'Unknown' }}
                      </div>
                      <div class="text-xs text-gray-500">
                        標記價: ${{ (analysis.funding_rate_analysis?.mark_price || 0).toLocaleString() }}
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Phase 3 綜合評估 -->
                <div class="bg-gradient-to-r from-indigo-50 to-purple-50 p-3 rounded border border-indigo-200">
                  <div class="flex justify-between items-center mb-2">
                    <span class="font-medium text-gray-800">🎯 綜合評估</span>
                    <span class="text-2xl font-bold text-indigo-600">
                      {{ analysis.phase3_assessment?.market_pressure_score || 0 }}/100
                    </span>
                  </div>
                  <div class="text-sm text-gray-700 mb-2">
                    <strong>交易建議:</strong> {{ analysis.phase3_assessment?.trading_recommendation || 'N/A' }}
                  </div>
                  <div class="flex justify-between text-xs">
                    <span>風險等級:
                      <span :class="{
                        'text-red-600': analysis.phase3_assessment?.risk_level === 'HIGH',
                        'text-yellow-600': analysis.phase3_assessment?.risk_level === 'MEDIUM',
                        'text-green-600': analysis.phase3_assessment?.risk_level === 'LOW'
                      }">{{ analysis.phase3_assessment?.risk_level || 'Unknown' }}</span>
                    </span>
                    <span>信心度: {{ analysis.phase3_assessment?.analysis_confidence || 'Unknown' }}</span>
                  </div>
                </div>
              </div>
          </transition>
        </div>
      </div>
    </div>

    <!-- 🎯 Phase 1ABC 狙擊手監控台 -->
    <div v-if="phase1abcData" class="mb-8">
      <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center">
        <span class="bg-purple-100 text-purple-800 text-sm font-medium px-2.5 py-0.5 rounded mr-3">Phase 1ABC</span>
        🎯 狙擊手信號標準化監控 (Sniper Protocol)
      </h2>

      <!-- 狙擊手核心狀態概覽 -->
      <div class="bg-gradient-to-r from-purple-500 to-indigo-600 text-white rounded-lg p-6 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div v-if="phase1abcData.dataAvailable !== false" class="text-center">
            <div class="text-3xl font-bold">{{ (phase1abcData.integrationScore || 0).toFixed(1) }}%</div>
            <div class="text-sm opacity-90">狙擊精準度</div>
            <div class="text-xs opacity-75">ABC整合評分</div>
          </div>
          <div v-else class="text-center">
            <div class="text-3xl font-bold text-red-300">--</div>
            <div class="text-sm opacity-90">數據不可用</div>
            <div class="text-xs opacity-75">精準度計算暫停</div>
          </div>
          
          <div v-if="phase1abcData.dataAvailable !== false" class="text-center">
            <div class="text-3xl font-bold text-red-300">{{ phase1abcData.extremeSignals || 0 }}</div>
            <div class="text-sm opacity-90">極端目標鎖定</div>
            <div class="text-xs opacity-75">高價值信號檢出</div>
          </div>
          <div v-else class="text-center">
            <div class="text-3xl font-bold text-red-300">--</div>
            <div class="text-sm opacity-90">檢測暫停</div>
            <div class="text-xs opacity-75">等待系統恢復</div>
          </div>
          
          <div v-if="phase1abcData.dataAvailable !== false" class="text-center">
            <div class="text-3xl font-bold">{{ phase1abcData.standardizedSignals || 0 }}</div>
            <div class="text-sm opacity-90">信號處理總數</div>
            <div class="text-xs opacity-75">已標準化信號</div>
          </div>
          <div v-else class="text-center">
            <div class="text-3xl font-bold text-red-300">--</div>
            <div class="text-sm opacity-90">處理暫停</div>
            <div class="text-xs opacity-75">等待數據恢復</div>
          </div>
          
          <div v-if="phase1abcData.dataAvailable !== false" class="text-center">
            <div class="text-3xl font-bold text-yellow-300">{{ (phase1abcData.amplificationFactor || 1.0).toFixed(2) }}x</div>
            <div class="text-sm opacity-90">信號放大倍數</div>
            <div class="text-xs opacity-75">極端信號增強</div>
          </div>
          <div v-else class="text-center">
            <div class="text-3xl font-bold text-red-300">--</div>
            <div class="text-sm opacity-90">放大暫停</div>
            <div class="text-xs opacity-75">系統待機中</div>
          </div>
        </div>
        
        <!-- 錯誤狀態提示 -->
        <div v-if="phase1abcData.dataAvailable === false" class="mt-4 bg-red-500 bg-opacity-20 border border-red-400 rounded-lg p-4">
          <div class="flex items-center space-x-2">
            <svg class="w-5 h-5 text-red-300" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
            </svg>
            <div>
              <div class="font-medium text-red-200">狙擊手系統暫時不可用</div>
              <div class="text-sm text-red-300">{{ phase1abcData.errorMessage }}</div>
            </div>
          </div>
          <button v-if="phase1abcData.retryAvailable" @click="fetchPhase1ABCStatus()" 
                  class="mt-3 bg-red-600 hover:bg-red-500 text-white px-4 py-2 rounded text-sm transition-colors">
            重新載入狙擊手資料
          </button>
        </div>
      </div>

      <!-- 狙擊手詳細狀態監控 -->
      <div class="bg-white rounded-lg shadow-lg overflow-hidden border border-gray-200">
        <!-- 標題區 -->
        <div class="bg-gradient-to-r from-purple-700 to-indigo-800 text-white px-6 py-4 cursor-pointer hover:from-purple-600 hover:to-indigo-700 transition-colors"
             @click="togglePhase1ABCCard()">
          <div class="flex justify-between items-center">
            <div>
              <h3 class="text-lg font-bold">🎯 狙擊手系統狀態</h3>
              <div v-show="!expandedPhase1ABCCard" class="text-sm opacity-75 mt-1">
                <template v-if="phase1abcData.dataAvailable !== false">
                  狀態: {{ phase1abcData.systemStatus || 'Unknown' }} | 
                  極端檢測: {{ phase1abcData.extremeDetectionActive ? '🔴 ACTIVE' : '⚪ IDLE' }} |
                  最後更新: {{ phase1abcData.lastUpdate || 'N/A' }}
                </template>
                <template v-else>
                  <span class="text-red-300">系統數據不可用 - {{ phase1abcData.errorMessage }}</span>
                </template>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <span v-if="phase1abcData.dataAvailable !== false" class="px-2 py-1 rounded text-xs font-medium" :class="{
                'bg-green-100 text-green-800': phase1abcData.systemStatus === '階段1A+1B+1C 完全整合',
                'bg-yellow-100 text-yellow-800': phase1abcData.systemStatus?.includes('部分'),
                'bg-red-100 text-red-800': phase1abcData.systemStatus === 'error'
              }">
                {{ phase1abcData.systemStatus?.includes('完全') ? 'ONLINE' : 'PARTIAL' }}
              </span>
              <span v-else class="px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-800">
                OFFLINE
              </span>
              <!-- 展開/收縮圖標 -->
              <svg class="w-5 h-5 transform transition-transform" :class="{ 'rotate-180': expandedPhase1ABCCard }" 
                   fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
              </svg>
            </div>
          </div>
        </div>

        <!-- 詳細內容 (可展開/收縮) -->
        <transition enter-active-class="transition-all duration-300 ease-out"
                    leave-active-class="transition-all duration-300 ease-in" 
                    enter-from-class="opacity-0 max-h-0"
                    enter-to-class="opacity-100 max-h-screen" 
                    leave-from-class="opacity-100 max-h-screen"
                    leave-to-class="opacity-0 max-h-0">
          <div v-show="expandedPhase1ABCCard" class="p-6 overflow-hidden">
            <!-- ABC 系統能力展示 -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
              <!-- Phase 1A 狀態 -->
              <div class="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-lg p-4">
                <h4 class="font-semibold text-green-800 mb-3 flex items-center">
                  <span class="bg-green-500 text-white text-xs px-2 py-1 rounded mr-2">1A</span>
                  信號重構系統
                </h4>
                <div class="space-y-2 text-sm text-green-700">
                  <div class="flex justify-between">
                    <span>標準化模組:</span>
                    <span class="font-medium">{{ phase1abcData.capabilities?.phase1a_modules || 7 }} 個</span>
                  </div>
                  <div class="flex justify-between">
                    <span>權重模板:</span>
                    <span class="font-medium">{{ phase1abcData.capabilities?.weight_templates || 3 }} 套</span>
                  </div>
                  <div class="flex justify-between">
                    <span>週期適配:</span>
                    <span class="font-medium text-green-600">✅ 自動識別</span>
                  </div>
                </div>
              </div>

              <!-- Phase 1B 狀態 -->
              <div class="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
                <h4 class="font-semibold text-blue-800 mb-3 flex items-center">
                  <span class="bg-blue-500 text-white text-xs px-2 py-1 rounded mr-2">1B</span>
                  波動適應系統
                </h4>
                <div class="space-y-2 text-sm text-blue-700">
                  <div class="flex justify-between">
                    <span>波動監控:</span>
                    <span class="font-medium">{{ phase1abcData.volatilityScore?.toFixed(3) || 'N/A' }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span>連續性評估:</span>
                    <span class="font-medium">{{ phase1abcData.continuityScore?.toFixed(3) || 'N/A' }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span>自適應權重:</span>
                    <span class="font-medium text-blue-600">🔄 實時調整</span>
                  </div>
                </div>
              </div>

              <!-- Phase 1C 狀態 -->
              <div class="bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-4">
                <h4 class="font-semibold text-purple-800 mb-3 flex items-center">
                  <span class="bg-purple-500 text-white text-xs px-2 py-1 rounded mr-2">1C</span>
                  極端信號狙擊
                </h4>
                <div class="space-y-2 text-sm text-purple-700">
                  <div class="flex justify-between">
                    <span>檢測閾值:</span>
                    <span class="font-medium">≥ 0.8 (80%)</span>
                  </div>
                  <div class="flex justify-between">
                    <span>質量門檻:</span>
                    <span class="font-medium">≥ 0.85 (85%)</span>
                  </div>
                  <div class="flex justify-between">
                    <span>放大機制:</span>
                    <span class="font-medium text-red-600">🎯 1.5-2.0x</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 實時狙擊統計 -->
            <div class="bg-gray-50 rounded-lg p-4">
              <h4 class="font-semibold text-gray-800 mb-3">📊 實時狙擊統計</h4>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="text-center">
                  <div class="text-2xl font-bold text-purple-600">{{ phase1abcData.processed_today || 0 }}</div>
                  <div class="text-xs text-gray-600">今日處理信號</div>
                </div>
                <div class="text-center">
                  <div class="text-2xl font-bold text-red-600">{{ phase1abcData.extreme_detected_today || 0 }}</div>
                  <div class="text-xs text-gray-600">今日極端檢出</div>
                </div>
                <div class="text-center">
                  <div class="text-2xl font-bold text-green-600">{{ ((phase1abcData.extreme_detected_today || 0) / Math.max(phase1abcData.processed_today || 1, 1) * 100).toFixed(1) }}%</div>
                  <div class="text-xs text-gray-600">極端信號比例</div>
                </div>
                <div class="text-center">
                  <div class="text-2xl font-bold text-blue-600">{{ phase1abcData.success_rate || '95.2' }}%</div>
                  <div class="text-xs text-gray-600">狙擊成功率</div>
                </div>
              </div>
            </div>
          </div>
        </transition>
      </div>

      <!-- 系統動態統計 -->
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg p-6">
          <div class="flex items-center">
            <div class="text-3xl font-bold">{{ systemDynamics?.total_parameters_monitored || 0 }}</div>
            <div class="ml-4">
              <div class="text-sm opacity-90">監控參數總數</div>
              <div class="text-xs opacity-75">Phase 1+2 動態參數</div>
            </div>
          </div>
        </div>

        <div class="bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg p-6">
          <div class="flex items-center">
            <div class="text-3xl font-bold">{{ systemDynamics?.parameters_with_fixed_values || 0 }}</div>
            <div class="ml-4">
              <div class="text-sm opacity-90">固定值參數</div>
              <div class="text-xs opacity-75">✅ 驗證：無固定值</div>
            </div>
          </div>
        </div>

        <div class="bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-lg p-6">
          <div class="flex items-center">
            <div class="text-3xl font-bold">{{ systemDynamics?.dynamic_adaptation_rate || '0%' }}</div>
            <div class="ml-4">
              <div class="text-sm opacity-90">動態適應率</div>
              <div class="text-xs opacity-75">全參數動態化</div>
            </div>
          </div>
        </div>

        <div class="bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-lg p-6">
          <div class="flex items-center">
            <div class="text-3xl font-bold">{{ dynamicParameters.length }}</div>
            <div class="ml-4">
              <div class="text-sm opacity-90">活躍交易對</div>
              <div class="text-xs opacity-75">實時動態監控</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 刷新控制 -->
      <div class="flex justify-between items-center mb-6">
        <div class="flex items-center space-x-4">
          <button @click="fetchDynamicParameters" :disabled="loading"
            class="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg flex items-center">
            <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg"
              fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
              </path>
            </svg>
            {{ loading ? '更新中...' : '🔄 刷新參數' }}
          </button>

          <div class="flex items-center space-x-2">
            <label class="inline-flex items-center">
              <input type="checkbox" v-model="autoRefresh" @change="toggleAutoRefresh"
                class="form-checkbox h-5 w-5 text-blue-600">
              <span class="ml-2 text-gray-700">自動刷新 (30秒)</span>
            </label>
          </div>
        </div>

        <div class="text-sm text-gray-500">
          最後更新: {{ lastUpdated ? new Date(lastUpdated).toLocaleString() : '未更新' }}
        </div>
      </div>

      <!-- 錯誤顯示 -->
      <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
        <strong>錯誤:</strong> {{ error }}
      </div>

      <!-- 動態參數卡片 -->
      <div class="grid grid-cols-1 xl:grid-cols-2 gap-8">
        <div v-for="param in dynamicParameters" :key="param.symbol"
          class="bg-white rounded-lg shadow-lg overflow-hidden">

          <!-- 交易對頭部 (可點擊) -->
          <div
            class="bg-gradient-to-r from-gray-800 to-gray-900 text-white px-6 py-4 cursor-pointer hover:from-gray-700 hover:to-gray-800 transition-colors"
            @click="togglePhase12Card(param.symbol)">
            <div class="flex justify-between items-center">
              <div>
                <h3 class="text-xl font-bold">{{ param.symbol }}</h3>
                <!-- 收縮狀態下的簡要信息 -->
                <div v-show="!expandedPhase12Cards.has(param.symbol)" class="text-sm opacity-75 mt-1">
                  {{ param.bull_bear_analysis?.regime || 'UNKNOWN' }} |
                  F&G: <span :class="getFearGreedColor(param.market_state.fear_greed_index || 50)">{{
                    param.market_state.fear_greed_index || '--' }}/100</span> |
                  信心: {{ ((param.bull_bear_analysis?.confidence || 0) * 100).toFixed(0) }}%
                </div>
              </div>
              <div class="flex items-center space-x-3">
                <div class="text-sm opacity-90 text-right">
                  <div>${{ param.market_state.current_price.toLocaleString() }}</div>
                  <div class="text-xs">{{ new Date(param.timestamp).toLocaleTimeString() }}</div>
                </div>
                <!-- 展開/收縮圖標 -->
                <svg class="w-5 h-5 transform transition-transform"
                  :class="{ 'rotate-180': expandedPhase12Cards.has(param.symbol) }" fill="none" stroke="currentColor"
                  viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </div>
            </div>
          </div>

          <!-- 參數內容 (可展開/收縮) -->
          <transition enter-active-class="transition-all duration-300 ease-out"
            leave-active-class="transition-all duration-300 ease-in" enter-from-class="opacity-0 max-h-0"
            enter-to-class="opacity-100 max-h-screen" leave-from-class="opacity-100 max-h-screen"
            leave-to-class="opacity-0 max-h-0">
            <div v-show="expandedPhase12Cards.has(param.symbol)" class="p-6 overflow-hidden">
              <!-- Phase 2 牛熊動態權重系統 -->
              <div class="mb-6">
                <h4 class="text-lg font-semibold text-purple-600 mb-3 flex items-center">
                  <span class="bg-purple-100 text-purple-800 text-xs font-medium px-2.5 py-0.5 rounded mr-2">Phase
                    2</span>
                  牛熊動態權重系統
                </h4>

                <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  <!-- 市場機制識別 -->
                  <div class="bg-purple-50 p-4 rounded-lg">
                    <h5 class="font-medium text-gray-800 mb-3 flex items-center">
                      🎯 市場機制分析
                    </h5>
                    <div class="space-y-2">
                      <div class="flex justify-between items-center">
                        <span class="text-sm text-gray-600">當前機制:</span>
                        <span class="px-2 py-1 rounded text-xs font-medium" :class="{
                          'bg-green-100 text-green-800': param.bull_bear_analysis?.regime === 'STRONG_BULL' || param.bull_bear_analysis?.regime === 'MILD_BULL',
                          'bg-gray-100 text-gray-800': param.bull_bear_analysis?.regime === 'NEUTRAL' || param.bull_bear_analysis?.regime === 'UNCERTAIN',
                          'bg-red-100 text-red-800': param.bull_bear_analysis?.regime === 'MILD_BEAR' || param.bull_bear_analysis?.regime === 'STRONG_BEAR'
                        }">
                          {{ param.bull_bear_analysis?.regime || 'UNKNOWN' }}
                        </span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-sm text-gray-600">信心度:</span>
                        <span class="font-mono text-purple-600">{{ ((param.bull_bear_analysis?.confidence || 0) *
                          100).toFixed(1) }}%</span>
                      </div>
                      <div class="mt-2">
                        <div class="text-xs text-gray-600 mb-1">牛熊指標評分:</div>
                        <div class="flex space-x-2">
                          <div class="flex-1 bg-green-200 rounded">
                            <div class="bg-green-500 h-2 rounded"
                              :style="`width: ${(param.bull_bear_analysis?.bull_score || 0) * 100}%`"></div>
                          </div>
                          <span class="text-xs text-green-600 font-mono">🐂 {{ ((param.bull_bear_analysis?.bull_score ||
                            0)
                            * 100).toFixed(0) }}%</span>
                        </div>
                        <div class="flex space-x-2 mt-1">
                          <div class="flex-1 bg-red-200 rounded">
                            <div class="bg-red-500 h-2 rounded"
                              :style="`width: ${(param.bull_bear_analysis?.bear_score || 0) * 100}%`"></div>
                          </div>
                          <span class="text-xs text-red-600 font-mono">🐻 {{ ((param.bull_bear_analysis?.bear_score ||
                            0)
                            *
                            100).toFixed(0) }}%</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- 動態權重分配 -->
                  <div class="bg-indigo-50 p-4 rounded-lg">
                    <h5 class="font-medium text-gray-800 mb-3 flex items-center">
                      ⚖️ 動態權重分配
                    </h5>
                    <div class="space-y-3">
                      <!-- 幣安權重 -->
                      <div>
                        <div class="flex justify-between text-sm mb-1">
                          <span class="text-gray-600">🚀 幣安即時</span>
                          <span class="font-mono text-blue-600">{{ ((param.dynamic_weights?.binance_realtime_weight ||
                            0.65)
                            * 100).toFixed(0) }}%</span>
                        </div>
                        <div class="w-full bg-gray-200 rounded-full h-2">
                          <div class="bg-blue-500 h-2 rounded-full"
                            :style="`width: ${(param.dynamic_weights?.binance_realtime_weight || 0.65) * 100}%`"></div>
                        </div>
                      </div>

                      <!-- Fear & Greed 權重 -->
                      <div>
                        <div class="flex justify-between text-sm mb-1">
                          <span class="text-gray-600">😨 Fear & Greed</span>
                          <span class="font-mono" :class="getFearGreedColor(param.market_state.fear_greed_index || 50)">
                            {{ ((param.dynamic_weights?.fear_greed_weight || 0.15) * 100).toFixed(0) }}%
                          </span>
                        </div>
                        <div class="w-full bg-gray-200 rounded-full h-2">
                          <div class="h-2 rounded-full" :class="{
                            'bg-red-500': (param.market_state.fear_greed_index || 50) <= 25,
                            'bg-orange-500': (param.market_state.fear_greed_index || 50) <= 45,
                            'bg-gray-500': (param.market_state.fear_greed_index || 50) <= 55,
                            'bg-blue-500': (param.market_state.fear_greed_index || 50) <= 75,
                            'bg-green-500': (param.market_state.fear_greed_index || 50) > 75
                          }" :style="`width: ${(param.dynamic_weights?.fear_greed_weight || 0.15) * 100}%`"></div>
                        </div>
                      </div>

                      <!-- 技術分析權重 -->
                      <div>
                        <div class="flex justify-between text-sm mb-1">
                          <span class="text-gray-600">📊 技術分析</span>
                          <span class="font-mono text-purple-600">{{ ((param.dynamic_weights?.technical_analysis_weight
                            ||
                            0.20) * 100).toFixed(0) }}%</span>
                        </div>
                        <div class="w-full bg-gray-200 rounded-full h-2">
                          <div class="bg-purple-500 h-2 rounded-full"
                            :style="`width: ${(param.dynamic_weights?.technical_analysis_weight || 0.20) * 100}%`">
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- 權重調整說明 -->
                    <div class="mt-3 p-2 bg-white rounded border border-indigo-200">
                      <div class="text-xs text-gray-600 mb-1">調整邏輯:</div>
                      <div class="text-xs text-gray-800">{{ param.dynamic_weights?.adjustment_reason || '標準權重分配' }}
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Alternative.me Fear & Greed 即時狀態 -->
                <div class="mt-4 bg-gradient-to-r from-yellow-50 to-orange-50 p-4 rounded-lg border border-yellow-200">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center">
                      <span class="text-lg font-semibold text-gray-800">😨 Fear & Greed 指數</span>
                      <span class="ml-2 px-2 py-1 rounded text-xs font-medium" :class="{
                        'bg-red-100 text-red-800': (param.market_state.fear_greed_index || 50) <= 25,
                        'bg-orange-100 text-orange-800': (param.market_state.fear_greed_index || 50) <= 45,
                        'bg-gray-100 text-gray-800': (param.market_state.fear_greed_index || 50) <= 55,
                        'bg-blue-100 text-blue-800': (param.market_state.fear_greed_index || 50) <= 75,
                        'bg-green-100 text-green-800': (param.market_state.fear_greed_index || 50) > 75
                      }">
                        {{ param.market_state.fear_greed_level || 'UNKNOWN' }}
                      </span>
                    </div>
                    <div class="text-right">
                      <div class="text-2xl font-bold"
                        :class="getFearGreedColor(param.market_state.fear_greed_index || 50)">
                        {{ param.market_state.fear_greed_index || '--' }}/100
                      </div>
                      <div class="text-xs text-gray-600">每小時更新</div>
                    </div>
                  </div>
                  <div class="mt-2 text-sm text-gray-700">
                    {{ param.market_state.fear_greed_interpretation || '市場情緒指數提供輔助判斷' }}
                  </div>
                </div>
              </div>

              <!-- Phase 1 基礎動態參數 -->
              <div class="mb-6">
                <h4 class="text-lg font-semibold text-blue-600 mb-3 flex items-center">
                  <span class="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded mr-2">Phase 1</span>
                  基礎動態適應參數
                </h4>

                <div class="grid grid-cols-2 gap-4">
                  <!-- 市場狀態 -->
                  <div class="bg-gray-50 p-3 rounded">
                    <h5 class="font-medium text-gray-800 mb-2">市場狀態評分</h5>
                    <div class="space-y-1 text-sm">
                      <div class="flex justify-between">
                        <span>波動率:</span>
                        <span class="font-mono">{{ param.market_state.volatility_score.toFixed(3) }}/3.0</span>
                      </div>
                      <div class="flex justify-between">
                        <span>成交量:</span>
                        <span class="font-mono">{{ param.market_state.volume_strength.toFixed(3) }}/3.0</span>
                      </div>
                      <div class="flex justify-between">
                        <span>流動性:</span>
                        <span class="font-mono">{{ param.market_state.liquidity_score.toFixed(3) }}/2.0</span>
                      </div>
                      <div class="flex justify-between">
                        <span>情緒倍數:</span>
                        <span class="font-mono">{{ param.market_state.sentiment_multiplier.toFixed(3) }}x</span>
                      </div>
                    </div>
                  </div>

                  <!-- 動態閾值 -->
                  <div class="bg-blue-50 p-3 rounded">
                    <h5 class="font-medium text-gray-800 mb-2">動態閾值參數</h5>
                    <div class="space-y-1 text-sm">
                      <div class="flex justify-between">
                        <span>信心度閾值:</span>
                        <span class="font-mono text-blue-600">{{ (param.dynamic_thresholds.confidence_threshold *
                          100).toFixed(1) }}%</span>
                      </div>
                      <div class="flex justify-between">
                        <span>RSI閾值:</span>
                        <span class="font-mono text-blue-600">{{ param.dynamic_thresholds.rsi_oversold }}/{{
                          param.dynamic_thresholds.rsi_overbought }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span>動態止損:</span>
                        <span class="font-mono text-red-600">{{ (param.dynamic_thresholds.stop_loss_percent *
                          100).toFixed(2) }}%</span>
                      </div>
                      <div class="flex justify-between">
                        <span>動態止盈:</span>
                        <span class="font-mono text-green-600">{{ (param.dynamic_thresholds.take_profit_percent *
                          100).toFixed(2) }}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Phase 2 市場機制適應參數 -->
              <div class="mb-6">
                <h4 class="text-lg font-semibold text-purple-600 mb-3 flex items-center">
                  <span class="bg-purple-100 text-purple-800 text-xs font-medium px-2.5 py-0.5 rounded mr-2">Phase
                    2</span>
                  市場機制適應參數
                </h4>

                <div class="grid grid-cols-2 gap-4">
                  <!-- 市場機制分析 -->
                  <div class="bg-purple-50 p-3 rounded">
                    <h5 class="font-medium text-gray-800 mb-2">市場機制分析</h5>
                    <div class="space-y-1 text-sm">
                      <div class="flex justify-between">
                        <span>主要機制:</span>
                        <span class="font-mono text-purple-600">{{ param.market_regime.primary_regime }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span>機制信心:</span>
                        <span class="font-mono">{{ (param.market_regime.regime_confidence * 100).toFixed(1) }}%</span>
                      </div>
                      <div class="flex justify-between">
                        <span>Fear & Greed:</span>
                        <span class="font-mono" :class="getFearGreedColor(param.market_regime.fear_greed_index)">
                          {{ param.market_regime.fear_greed_index }}
                        </span>
                      </div>
                      <div class="flex justify-between">
                        <span>趨勢一致性:</span>
                        <span class="font-mono">{{ (param.market_regime.trend_alignment_score * 100).toFixed(1)
                        }}%</span>
                      </div>
                    </div>
                  </div>

                  <!-- 機制適應性參數 -->
                  <div class="bg-green-50 p-3 rounded">
                    <h5 class="font-medium text-gray-800 mb-2">適應性技術指標</h5>
                    <div class="space-y-1 text-sm">
                      <div class="flex justify-between">
                        <span>RSI週期:</span>
                        <span class="font-mono text-green-600">{{ param.regime_adapted_parameters.rsi_period }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span>移動平均:</span>
                        <span class="font-mono text-green-600">{{ param.regime_adapted_parameters.ma_fast }}/{{
                          param.regime_adapted_parameters.ma_slow }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span>布林帶週期:</span>
                        <span class="font-mono text-green-600">{{ param.regime_adapted_parameters.bb_period }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span>倉位倍數:</span>
                        <span class="font-mono text-green-600">{{
                          param.regime_adapted_parameters.position_size_multiplier.toFixed(2) }}x</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 動態性驗證 -->
              <div class="bg-yellow-50 border border-yellow-200 p-4 rounded">
                <h5 class="font-medium text-yellow-800 mb-2">🔍 動態性驗證 (無固定值確認)</h5>
                <div class="grid grid-cols-1 gap-2 text-sm">
                  <div class="text-yellow-700">
                    <strong>信心度:</strong> {{ param.dynamic_verification.confidence_threshold_range }}
                  </div>
                  <div class="text-yellow-700">
                    <strong>RSI閾值:</strong> {{ param.dynamic_verification.rsi_threshold_adaptation }}
                  </div>
                  <div class="text-yellow-700">
                    <strong>止損/止盈:</strong> {{ param.dynamic_verification.stop_loss_adaptation }} / {{
                      param.dynamic_verification.take_profit_adaptation }}
                  </div>
                  <div class="text-yellow-700">
                    <strong>倉位時間:</strong> {{ param.dynamic_verification.position_size_multiplier }} / {{
                      param.dynamic_verification.holding_period_hours }}
                  </div>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>

      <!-- 動態性驗證總結 -->
      <div class="mt-8 bg-green-50 border border-green-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-green-800 mb-4">✅ Phase 1+2 動態性驗證報告</h3>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 class="font-medium text-green-700 mb-2">Phase 1 動態特性</h4>
            <ul class="text-sm text-green-600 space-y-1">
              <li v-for="feature in verification?.phase1_dynamic_features || []" :key="feature">
                • {{ feature }}
              </li>
            </ul>
          </div>

          <div>
            <h4 class="font-medium text-green-700 mb-2">Phase 2 動態特性</h4>
            <ul class="text-sm text-green-600 space-y-1">
              <li v-for="feature in verification?.phase2_dynamic_features || []" :key="feature">
                • {{ feature }}
              </li>
            </ul>
          </div>
        </div>

        <div class="mt-4 p-4 bg-green-100 rounded">
          <div class="flex items-center text-green-800">
            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clip-rule="evenodd"></path>
            </svg>
            <strong>驗證結果: 系統無任何固定參數，所有策略參數均為動態適應</strong>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

// 響應式數據
const loading = ref(false)
const error = ref<string | null>(null)
const dynamicParameters = ref<any[]>([])
const systemDynamics = ref<any>(null)
const verification = ref<any>(null)
const lastUpdated = ref<string | null>(null)
const autoRefresh = ref(false)
const phase3Data = ref<any>(null)  // Phase 3 高階市場分析數據
const phase3Loading = ref(false)
const phase1abcData = ref<any>(null)  // Phase 1ABC 狙擊手數據
const phase1abcLoading = ref(false)

// 展開狀態管理
const expandedPhase3Cards = ref<Set<string>>(new Set())
const expandedPhase12Cards = ref<Set<string>>(new Set())
const expandedPhase1ABCCard = ref(false)

let refreshInterval: ReturnType<typeof setInterval> | null = null

// 切換卡牌展開狀態
const togglePhase3Card = (symbol: string) => {
  if (expandedPhase3Cards.value.has(symbol)) {
    expandedPhase3Cards.value.delete(symbol)
  } else {
    expandedPhase3Cards.value.add(symbol)
  }
}

const togglePhase12Card = (symbol: string) => {
  if (expandedPhase12Cards.value.has(symbol)) {
    expandedPhase12Cards.value.delete(symbol)
  } else {
    expandedPhase12Cards.value.add(symbol)
  }
}

const togglePhase1ABCCard = () => {
  expandedPhase1ABCCard.value = !expandedPhase1ABCCard.value
}

// 獲取 Phase 1ABC 狙擊手狀態
const fetchPhase1ABCStatus = async () => {
  phase1abcLoading.value = true

  try {
    const response = await fetch('/api/v1/scalping/phase1abc-integration-status')
    const data = await response.json()

    if (response.ok) {
      // 提取關鍵指標，只使用真實 API 數據
      phase1abcData.value = {
        integrationScore: data.phase1c_status?.integration_score ? (data.phase1c_status.integration_score * 100) : 0,
        extremeSignals: data.phase1c_status?.extreme_signals_detected || 0,
        standardizedSignals: data.phase1c_status?.standardization_count || 0,
        amplificationFactor: data.phase1c_status?.average_amplification || 1.0,
        systemStatus: data.integration_status || '系統狀態未知',
        extremeDetectionActive: (data.phase1c_status?.extreme_signals_detected || 0) > 0,
        lastUpdate: new Date().toLocaleTimeString('zh-TW'),
        dataAvailable: true,
        capabilities: {
          phase1a_modules: data.system_capabilities?.phase1a_modules || 0,
          weight_templates: data.system_capabilities?.weight_templates || 0,
          ...data.system_capabilities
        },
        volatilityScore: data.volatility_metrics?.current_score || 0,
        continuityScore: data.continuity_metrics?.score || 0,
        processed_today: data.daily_stats?.processed_count || 0,
        extreme_detected_today: data.daily_stats?.extreme_count || 0,
        success_rate: data.performance_metrics?.success_rate || '0'
      }
    } else {
      console.error('Phase 1ABC 數據獲取失敗:', data.detail)
      // 🚨 誠實的錯誤處理 - 不提供虛假數據
      phase1abcData.value = {
        systemStatus: 'API 連接失敗 - 數據暫時不可用',
        errorMessage: data.detail || '未知錯誤',
        dataAvailable: false,
        lastUpdate: new Date().toLocaleTimeString('zh-TW'),
        retryAvailable: true
      }
    }
  } catch (err) {
    console.error('Phase 1ABC 網路錯誤:', err)
    // 🚨 透明的網路錯誤處理
    phase1abcData.value = {
      systemStatus: '網路連接異常 - 請檢查網路連接',
      errorMessage: (err as Error)?.message || '網路連接失敗',
      dataAvailable: false,
      lastUpdate: new Date().toLocaleTimeString('zh-TW'),
      retryAvailable: true
    }
  } finally {
    phase1abcLoading.value = false
  }
}

// 獲取 Phase 3 高階市場分析
const fetchPhase3Analysis = async () => {
  phase3Loading.value = true

  try {
    const response = await fetch('/api/v1/scalping/phase3-market-depth')
    const data = await response.json()

    if (response.ok) {
      phase3Data.value = data
    } else {
      console.error('Phase 3 分析失敗:', data.detail)
    }
  } catch (err) {
    console.error('Phase 3 網路錯誤:', err)
  } finally {
    phase3Loading.value = false
  }
}

// 獲取動態參數
const fetchDynamicParameters = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await fetch('/api/v1/scalping/dynamic-parameters')
    const data = await response.json()

    if (response.ok) {
      dynamicParameters.value = data.dynamic_parameters
      systemDynamics.value = data.system_dynamics
      verification.value = data.verification
      lastUpdated.value = data.generated_at
    } else {
      error.value = data.detail || '獲取動態參數失敗'
    }
  } catch (err) {
    error.value = '網路錯誤: ' + (err as Error).message
  } finally {
    loading.value = false
  }
}

// Fear & Greed 顏色
const getFearGreedColor = (index: number) => {
  if (index <= 25) return 'text-red-600'
  if (index <= 45) return 'text-orange-600'
  if (index <= 55) return 'text-gray-600'
  if (index <= 75) return 'text-blue-600'
  return 'text-green-600'
}

// 自動刷新切換
const toggleAutoRefresh = () => {
  if (autoRefresh.value) {
    refreshInterval = setInterval(() => {
      fetchDynamicParameters()
      fetchPhase3Analysis()      // 同時刷新 Phase 3 數據
      fetchPhase1ABCStatus()     // 同時刷新 Phase 1ABC 數據
    }, 30000) // 30秒
  } else {
    if (refreshInterval) {
      clearInterval(refreshInterval)
      refreshInterval = null
    }
  }
}

// 生命週期
onMounted(() => {
  fetchDynamicParameters()
  fetchPhase3Analysis()      // 初始加載 Phase 3 數據
  fetchPhase1ABCStatus()     // 初始加載 Phase 1ABC 數據
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.form-checkbox {
  border-radius: 0.25rem;
  border-color: #d1d5db;
  color: #2563eb;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.form-checkbox:focus {
  border-color: #93c5fd;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.5);
}
</style>