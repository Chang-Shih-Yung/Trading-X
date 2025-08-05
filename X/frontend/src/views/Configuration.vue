<template>
  <div class="p-6 space-y-6">
    <!-- 頁面標題 -->
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-3xl font-bold text-white">系統設定</h2>
        <p class="text-gray-400 mt-1">配置 Trading X 監控系統參數</p>
      </div>
      
      <div class="flex items-center space-x-3">
        <button @click="saveAllConfiguration" :disabled="saving" class="btn-primary">
          <Save :class="['h-4 w-4 mr-2', saving && 'animate-pulse']" />
          {{ saving ? '保存中...' : '保存設定' }}
        </button>
        
        <button @click="resetToDefaults" class="btn-secondary">
          <RotateCcw class="h-4 w-4 mr-2" />
          重置預設
        </button>
      </div>
    </div>

    <!-- Gmail 通知設定 -->
    <div class="bg-trading-secondary rounded-lg border border-gray-700 p-6">
      <h3 class="text-xl font-semibold mb-4 flex items-center">
        <Mail class="h-6 w-6 mr-2 text-blue-500" />
        Gmail 通知設定
      </h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              Gmail 通知
              <span :class="gmailConfig.enabled ? 'text-green-500' : 'text-red-500'" class="ml-2">
                {{ gmailConfig.enabled ? '已啟用' : '已停用' }}
              </span>
            </label>
            <label class="flex items-center cursor-pointer">
              <input 
                v-model="gmailConfig.enabled" 
                type="checkbox" 
                class="sr-only"
              />
              <div 
                :class="[
                  'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none',
                  gmailConfig.enabled ? 'bg-blue-600' : 'bg-gray-600'
                ]"
              >
                <span 
                  :class="[
                    'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
                    gmailConfig.enabled ? 'translate-x-5' : 'translate-x-0'
                  ]"
                ></span>
              </div>
              <span class="ml-3 text-sm text-gray-300">啟用 Gmail 通知</span>
            </label>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">發送者郵箱</label>
            <input 
              v-model="gmailConfig.sender_email" 
              type="email" 
              class="w-full bg-trading-accent border border-gray-600 rounded-lg px-3 py-2 text-white"
              placeholder="your-email@gmail.com"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">應用密碼</label>
            <div class="relative">
              <input 
                v-model="gmailConfig.app_password" 
                :type="showPassword ? 'text' : 'password'"
                class="w-full bg-trading-accent border border-gray-600 rounded-lg px-3 py-2 pr-10 text-white"
                placeholder="Gmail 應用密碼"
              />
              <button 
                @click="showPassword = !showPassword"
                type="button"
                class="absolute inset-y-0 right-0 flex items-center pr-3"
              >
                <Eye v-if="!showPassword" class="h-4 w-4 text-gray-400" />
                <EyeOff v-else class="h-4 w-4 text-gray-400" />
              </button>
            </div>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">接收者郵箱</label>
            <input 
              v-model="gmailConfig.recipient_email" 
              type="email" 
              class="w-full bg-trading-accent border border-gray-600 rounded-lg px-3 py-2 text-white"
              placeholder="recipient@gmail.com"
            />
          </div>
        </div>
        
        <div class="space-y-4">
          <h4 class="text-lg font-semibold text-white">通知規則設定</h4>
          
          <div v-for="(rule, priority) in gmailConfig.notification_rules" :key="priority" class="p-4 bg-trading-accent rounded-lg">
            <div class="flex items-center justify-between mb-3">
              <span class="font-medium" :class="getPriorityTextColor(priority)">
                {{ getPriorityLabel(priority) }} 級別
              </span>
              <label class="flex items-center cursor-pointer">
                <input 
                  v-model="rule.enabled" 
                  type="checkbox" 
                  class="sr-only"
                />
                <div 
                  :class="[
                    'relative inline-flex h-5 w-9 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out',
                    rule.enabled ? 'bg-blue-600' : 'bg-gray-600'
                  ]"
                >
                  <span 
                    :class="[
                      'pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
                      rule.enabled ? 'translate-x-4' : 'translate-x-0'
                    ]"
                  ></span>
                </div>
              </label>
            </div>
            
            <div class="grid grid-cols-2 gap-3 text-sm">
              <div>
                <label class="block text-gray-300 mb-1">延遲時間 (秒)</label>
                <input 
                  v-model.number="rule.delay" 
                  type="number" 
                  min="0" 
                  class="w-full bg-trading-secondary border border-gray-600 rounded px-2 py-1 text-white text-sm"
                />
              </div>
              <div>
                <label class="block text-gray-300 mb-1">冷卻時間 (秒)</label>
                <input 
                  v-model.number="rule.cooldown" 
                  type="number" 
                  min="0" 
                  class="w-full bg-trading-secondary border border-gray-600 rounded px-2 py-1 text-white text-sm"
                />
              </div>
              <div>
                <label class="block text-gray-300 mb-1">每小時上限</label>
                <input 
                  v-model.number="rule.max_per_hour" 
                  type="number" 
                  min="1" 
                  class="w-full bg-trading-secondary border border-gray-600 rounded px-2 py-1 text-white text-sm"
                />
              </div>
              <div>
                <label class="block text-gray-300 mb-1">郵件優先級</label>
                <select 
                  v-model="rule.email_priority" 
                  class="w-full bg-trading-secondary border border-gray-600 rounded px-2 py-1 text-white text-sm"
                >
                  <option value="HIGH">高</option>
                  <option value="NORMAL">普通</option>
                  <option value="LOW">低</option>
                </select>
              </div>
            </div>
          </div>
          
          <button @click="testGmailNotification" :disabled="!gmailConfig.enabled || testing" class="btn-secondary w-full">
            <TestTube :class="['h-4 w-4 mr-2', testing && 'animate-pulse']" />
            {{ testing ? '測試中...' : '測試 Gmail 通知' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 信號品質控制設定 -->
    <div class="bg-trading-secondary rounded-lg border border-gray-700 p-6">
      <h3 class="text-xl font-semibold mb-4 flex items-center">
        <Target class="h-6 w-6 mr-2 text-green-500" />
        信號品質控制設定
      </h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="space-y-4">
          <h4 class="text-lg font-semibold text-white">EPL 決策閾值</h4>
          
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              替單決策閾值
              <span class="text-blue-400">{{ eplConfig.replacement_threshold }}%</span>
            </label>
            <input 
              v-model.number="eplConfig.replacement_threshold" 
              type="range" 
              min="5" 
              max="30" 
              step="1"
              class="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
            />
            <div class="flex justify-between text-xs text-gray-400 mt-1">
              <span>5%</span>
              <span>30%</span>
            </div>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              加倉決策閾值
              <span class="text-green-400">{{ eplConfig.addition_threshold }}%</span>
            </label>
            <input 
              v-model.number="eplConfig.addition_threshold" 
              type="range" 
              min="3" 
              max="20" 
              step="1"
              class="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
            />
            <div class="flex justify-between text-xs text-gray-400 mt-1">
              <span>3%</span>
              <span>20%</span>
            </div>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              品質門檻分數
              <span class="text-yellow-400">{{ eplConfig.quality_threshold }}分</span>
            </label>
            <input 
              v-model.number="eplConfig.quality_threshold" 
              type="range" 
              min="50" 
              max="90" 
              step="1"
              class="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
            />
            <div class="flex justify-between text-xs text-gray-400 mt-1">
              <span>50分</span>
              <span>90分</span>
            </div>
          </div>
        </div>
        
        <div class="space-y-4">
          <h4 class="text-lg font-semibold text-white">去重過濾設定</h4>
          
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              時間重疊窗口
              <span class="text-blue-400">{{ eplConfig.time_overlap_window }}分鐘</span>
            </label>
            <input 
              v-model.number="eplConfig.time_overlap_window" 
              type="range" 
              min="5" 
              max="60" 
              step="5"
              class="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
            />
            <div class="flex justify-between text-xs text-gray-400 mt-1">
              <span>5分鐘</span>
              <span>60分鐘</span>
            </div>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              相似度閾值
              <span class="text-green-400">{{ eplConfig.similarity_threshold }}%</span>
            </label>
            <input 
              v-model.number="eplConfig.similarity_threshold" 
              type="range" 
              min="70" 
              max="95" 
              step="1"
              class="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
            />
            <div class="flex justify-between text-xs text-gray-400 mt-1">
              <span>70%</span>
              <span>95%</span>
            </div>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              信心度差異閾值
              <span class="text-yellow-400">{{ eplConfig.confidence_diff_threshold }}%</span>
            </label>
            <input 
              v-model.number="eplConfig.confidence_diff_threshold" 
              type="range" 
              min="1" 
              max="10" 
              step="0.5"
              class="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
            />
            <div class="flex justify-between text-xs text-gray-400 mt-1">
              <span>1%</span>
              <span>10%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 系統性能設定 -->
    <div class="bg-trading-secondary rounded-lg border border-gray-700 p-6">
      <h3 class="text-xl font-semibold mb-4 flex items-center">
        <Settings class="h-6 w-6 mr-2 text-purple-500" />
        系統性能設定
      </h3>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="space-y-4">
          <h4 class="text-lg font-semibold text-white">處理優化</h4>
          
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              批次處理大小
              <span class="text-blue-400">{{ systemConfig.batch_size }}</span>
            </label>
            <input 
              v-model.number="systemConfig.batch_size" 
              type="range" 
              min="10" 
              max="100" 
              step="10"
              class="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              處理超時 (秒)
              <span class="text-yellow-400">{{ systemConfig.processing_timeout }}</span>
            </label>
            <input 
              v-model.number="systemConfig.processing_timeout" 
              type="range" 
              min="5" 
              max="60" 
              step="5"
              class="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
            />
          </div>
        </div>
        
        <div class="space-y-4">
          <h4 class="text-lg font-semibold text-white">緩存設定</h4>
          
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              信號緩存時間 (小時)
              <span class="text-green-400">{{ systemConfig.signal_cache_hours }}</span>
            </label>
            <input 
              v-model.number="systemConfig.signal_cache_hours" 
              type="range" 
              min="1" 
              max="48" 
              step="1"
              class="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              最大緩存條目
              <span class="text-purple-400">{{ systemConfig.max_cache_entries }}</span>
            </label>
            <input 
              v-model.number="systemConfig.max_cache_entries" 
              type="range" 
              min="500" 
              max="5000" 
              step="500"
              class="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
            />
          </div>
        </div>
        
        <div class="space-y-4">
          <h4 class="text-lg font-semibold text-white">監控設定</h4>
          
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              心跳間隔 (秒)
              <span class="text-red-400">{{ systemConfig.heartbeat_interval }}</span>
            </label>
            <input 
              v-model.number="systemConfig.heartbeat_interval" 
              type="range" 
              min="10" 
              max="120" 
              step="10"
              class="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
            />
          </div>
          
          <div>
            <label class="flex items-center cursor-pointer">
              <input 
                v-model="systemConfig.debug_mode" 
                type="checkbox" 
                class="sr-only"
              />
              <div 
                :class="[
                  'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out',
                  systemConfig.debug_mode ? 'bg-red-600' : 'bg-gray-600'
                ]"
              >
                <span 
                  :class="[
                    'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
                    systemConfig.debug_mode ? 'translate-x-5' : 'translate-x-0'
                  ]"
                ></span>
              </div>
              <span class="ml-3 text-sm text-gray-300">除錯模式</span>
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作按鈕 -->
    <div class="flex justify-center space-x-4">
      <button @click="exportConfiguration" class="btn-secondary">
        <Download class="h-4 w-4 mr-2" />
        導出設定
      </button>
      
      <button @click="importConfiguration" class="btn-secondary">
        <Upload class="h-4 w-4 mr-2" />
        導入設定
      </button>
      
      <input 
        ref="fileInput" 
        type="file" 
        accept=".json" 
        @change="handleConfigurationImport" 
        class="hidden"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { 
  Mail, 
  Target, 
  Settings, 
  Save, 
  RotateCcw, 
  Eye, 
  EyeOff, 
  TestTube, 
  Download, 
  Upload 
} from 'lucide-vue-next'

// 組件狀態
const saving = ref(false)
const testing = ref(false)
const showPassword = ref(false)
const fileInput = ref(null)

// Gmail 設定
const gmailConfig = reactive({
  enabled: true,
  sender_email: '',
  app_password: '',
  recipient_email: '',
  notification_rules: {
    CRITICAL: {
      enabled: true,
      delay: 0,
      cooldown: 60,
      max_per_hour: 10,
      email_priority: 'HIGH'
    },
    HIGH: {
      enabled: true,
      delay: 300,
      cooldown: 900,
      max_per_hour: 6,
      email_priority: 'NORMAL'
    },
    MEDIUM: {
      enabled: true,
      delay: 1800,
      cooldown: 3600,
      max_per_hour: 3,
      email_priority: 'LOW'
    }
  }
})

// EPL 設定
const eplConfig = reactive({
  replacement_threshold: 15,
  addition_threshold: 8,
  quality_threshold: 70,
  time_overlap_window: 15,
  similarity_threshold: 85,
  confidence_diff_threshold: 3
})

// 系統設定
const systemConfig = reactive({
  batch_size: 50,
  processing_timeout: 30,
  signal_cache_hours: 24,
  max_cache_entries: 2000,
  heartbeat_interval: 30,
  debug_mode: false
})

// 獲取優先級標籤
function getPriorityLabel(priority) {
  const labels = {
    CRITICAL: '🚨 緊急',
    HIGH: '🎯 高品質',
    MEDIUM: '📊 標準'
  }
  return labels[priority] || priority
}

// 獲取優先級文字顏色
function getPriorityTextColor(priority) {
  const colors = {
    CRITICAL: 'text-red-400',
    HIGH: 'text-orange-400',
    MEDIUM: 'text-blue-400'
  }
  return colors[priority] || 'text-gray-400'
}

// 保存所有設定
async function saveAllConfiguration() {
  saving.value = true
  
  try {
    const configuration = {
      gmail: gmailConfig,
      epl: eplConfig,
      system: systemConfig,
      timestamp: new Date().toISOString()
    }
    
    // 模擬 API 調用
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 這裡應該調用實際的 API
    // await fetch('/api/v1/monitoring/configuration', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(configuration)
    // })
    
    console.log('設定已保存:', configuration)
    alert('設定保存成功！')
    
  } catch (error) {
    console.error('保存設定失敗:', error)
    alert('設定保存失敗，請重試。')
  } finally {
    saving.value = false
  }
}

// 重置為預設值
function resetToDefaults() {
  if (confirm('確定要重置所有設定為預設值嗎？')) {
    // 重置 Gmail 設定
    Object.assign(gmailConfig, {
      enabled: true,
      sender_email: '',
      app_password: '',
      recipient_email: '',
      notification_rules: {
        CRITICAL: { enabled: true, delay: 0, cooldown: 60, max_per_hour: 10, email_priority: 'HIGH' },
        HIGH: { enabled: true, delay: 300, cooldown: 900, max_per_hour: 6, email_priority: 'NORMAL' },
        MEDIUM: { enabled: true, delay: 1800, cooldown: 3600, max_per_hour: 3, email_priority: 'LOW' }
      }
    })
    
    // 重置 EPL 設定
    Object.assign(eplConfig, {
      replacement_threshold: 15,
      addition_threshold: 8,
      quality_threshold: 70,
      time_overlap_window: 15,
      similarity_threshold: 85,
      confidence_diff_threshold: 3
    })
    
    // 重置系統設定
    Object.assign(systemConfig, {
      batch_size: 50,
      processing_timeout: 30,
      signal_cache_hours: 24,
      max_cache_entries: 2000,
      heartbeat_interval: 30,
      debug_mode: false
    })
    
    alert('設定已重置為預設值！')
  }
}

// 測試 Gmail 通知
async function testGmailNotification() {
  if (!gmailConfig.enabled) {
    alert('請先啟用 Gmail 通知功能')
    return
  }
  
  if (!gmailConfig.sender_email || !gmailConfig.app_password || !gmailConfig.recipient_email) {
    alert('請完整填寫 Gmail 設定資訊')
    return
  }
  
  testing.value = true
  
  try {
    // 模擬 API 調用
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 這裡應該調用實際的測試 API
    // await fetch('/api/v1/monitoring/notifications/test', { method: 'POST' })
    
    alert('測試郵件發送成功！請檢查收件箱。')
    
  } catch (error) {
    console.error('測試通知失敗:', error)
    alert('測試郵件發送失敗，請檢查設定。')
  } finally {
    testing.value = false
  }
}

// 導出設定
function exportConfiguration() {
  const configuration = {
    gmail: gmailConfig,
    epl: eplConfig,
    system: systemConfig,
    exported_at: new Date().toISOString(),
    version: '1.0.0'
  }
  
  const blob = new Blob([JSON.stringify(configuration, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `trading-x-config-${new Date().toISOString().split('T')[0]}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

// 導入設定
function importConfiguration() {
  fileInput.value?.click()
}

// 處理設定檔案導入
function handleConfigurationImport(event) {
  const file = event.target.files[0]
  if (!file) return
  
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const configuration = JSON.parse(e.target.result)
      
      // 驗證設定格式
      if (configuration.gmail) Object.assign(gmailConfig, configuration.gmail)
      if (configuration.epl) Object.assign(eplConfig, configuration.epl)
      if (configuration.system) Object.assign(systemConfig, configuration.system)
      
      alert('設定導入成功！')
      
    } catch (error) {
      console.error('導入設定失敗:', error)
      alert('設定檔案格式錯誤，請檢查檔案內容。')
    }
  }
  
  reader.readAsText(file)
  
  // 清空文件選擇器
  event.target.value = ''
}
</script>

<style scoped>
/* 自定義滑桿樣式 */
.slider::-webkit-slider-thumb {
  appearance: none;
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid #1e293b;
  box-shadow: 0 0 0 1px #3b82f6;
}

.slider::-webkit-slider-thumb:hover {
  background: #2563eb;
  box-shadow: 0 0 0 2px #2563eb;
}

.slider::-moz-range-thumb {
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid #1e293b;
  box-shadow: 0 0 0 1px #3b82f6;
}
</style>
