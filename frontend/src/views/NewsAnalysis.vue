<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">新聞與數據分析</h1>
      <p class="text-gray-600">多維度數據整合：新聞、鏈上數據、宏觀經濟指標</p>
    </div>

    <!-- 數據統計卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-2 bg-blue-100 rounded-lg">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"></path>
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">今日新聞</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.todayNews }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-2 bg-green-100 rounded-lg">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">鏈上事件</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.onchainEvents }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-2 bg-yellow-100 rounded-lg">
            <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">經濟指標</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.economicIndicators }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-2 bg-purple-100 rounded-lg">
            <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">AI 情緒分析</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.sentimentScore }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- AI 新聞摘要 -->
    <div class="bg-white rounded-lg shadow mb-8">
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex justify-between items-center">
          <h2 class="text-lg font-semibold text-gray-900">📊 市場摘要分析</h2>
          <button @click="refreshAISummary" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
            重新分析
          </button>
        </div>
      </div>
      <div class="p-6">
        <div v-if="loading.aiSummary" class="flex justify-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <div v-else class="space-y-4">
          <div class="bg-blue-50 border-l-4 border-blue-400 p-4">
            <h3 class="text-lg font-medium text-blue-900 mb-2">市場關鍵摘要</h3>
            <p class="text-blue-700">{{ aiSummary.keyPoints || '正在分析最新市場動態...' }}</p>
          </div>
          <div class="bg-green-50 border-l-4 border-green-400 p-4">
            <h3 class="text-lg font-medium text-green-900 mb-2">正面影響因素</h3>
            <p class="text-green-700">{{ aiSummary.positiveFactors || '分析中...' }}</p>
          </div>
          <div class="bg-red-50 border-l-4 border-red-400 p-4">
            <h3 class="text-lg font-medium text-red-900 mb-2">風險警示</h3>
            <p class="text-red-700">{{ aiSummary.riskFactors || '分析中...' }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 重點數據區塊 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <!-- 鏈上數據分析 -->
      <div class="bg-white rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200">
          <h2 class="text-lg font-semibold text-gray-900">🔗 鏈上數據分析</h2>
        </div>
        <div class="p-6">
          <div v-if="loading.onchain" class="flex justify-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
          </div>
          <div v-else class="space-y-4">
            <div v-for="metric in onchainMetrics" :key="metric.name" class="flex justify-between items-center p-3 bg-gray-50 rounded">
              <span class="font-medium">{{ metric.name }}</span>
              <span class="text-lg font-bold" :class="metric.trend === 'up' ? 'text-green-600' : metric.trend === 'down' ? 'text-red-600' : 'text-gray-600'">
                {{ metric.value }}
                <svg v-if="metric.trend === 'up'" class="inline w-4 h-4 ml-1" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z"/>
                </svg>
                <svg v-else-if="metric.trend === 'down'" class="inline w-4 h-4 ml-1" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M16.707 10.293a1 1 0 010 1.414l-6 6a1 1 0 01-1.414 0l-6-6a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l4.293-4.293a1 1 0 011.414 0z"/>
                </svg>
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 宏觀經濟指標 -->
      <div class="bg-white rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200">
          <h2 class="text-lg font-semibold text-gray-900">📊 宏觀經濟指標</h2>
        </div>
        <div class="p-6">
          <div v-if="loading.economic" class="flex justify-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-yellow-600"></div>
          </div>
          <div v-else class="space-y-4">
            <div v-for="indicator in economicData" :key="indicator.name" class="flex justify-between items-center p-3 bg-gray-50 rounded">
              <span class="font-medium">{{ indicator.name }}</span>
              <span class="text-lg font-bold" :class="indicator.impact === 'positive' ? 'text-green-600' : indicator.impact === 'negative' ? 'text-red-600' : 'text-gray-600'">
                {{ indicator.value }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 新聞列表 -->
    <div class="bg-white rounded-lg shadow">
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex justify-between items-center">
          <h2 class="text-lg font-semibold text-gray-900">📰 最新市場新聞</h2>
          <select v-model="selectedCategory" @change="filterNews" class="px-3 py-1 border rounded-md">
            <option value="all">全部類別</option>
            <option value="crypto">加密貨幣</option>
            <option value="defi">DeFi</option>
            <option value="nft">NFT</option>
            <option value="regulation">監管</option>
            <option value="technology">科技</option>
          </select>
        </div>
      </div>
      <div class="p-6">
        <div v-if="loading.news" class="flex justify-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <div v-else class="space-y-6">
          <div v-for="article in filteredNews" :key="article.id" class="border-b pb-4 last:border-b-0">
            <div class="flex justify-between items-start mb-2">
              <h3 
                class="text-lg font-semibold flex-1 cursor-pointer hover:text-blue-600 transition-colors"
                :class="getUrlStatusClass(article.url)"
                @click="openArticle(article.url, article)"
                :title="getUrlStatusText(article.url)"
              >
                <span v-if="article.translated" class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded mr-2">中文</span>
                {{ article.title }}
                <span v-if="!isValidUrl(article.url)" class="text-xs text-gray-400 ml-2">📄</span>
                <span v-else class="text-xs text-green-500 ml-2">🔗</span>
              </h3>
              <div class="flex items-center space-x-2 ml-4">
                <span class="text-xs px-2 py-1 rounded-full" :class="getCategoryColor(article.category)">
                  {{ getCategoryText(article.category) }}
                </span>
                <img v-if="article.image" :src="article.image" alt="新聞圖片" class="w-12 h-12 rounded object-cover">
              </div>
            </div>
            <p class="text-gray-600 mb-3">{{ article.summary }}</p>
            <div class="flex justify-between items-center text-sm">
              <div class="flex items-center space-x-2 text-gray-500">
                <span class="font-medium">{{ article.source }}</span>
                <span>{{ formatDate(article.publishedAt) }}</span>
              </div>
              <div class="flex items-center space-x-2">
                <button 
                  @click="translateArticle(article)" 
                  :disabled="loading.translate === article.id"
                  class="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200 disabled:opacity-50 transition-colors"
                >
                  <span v-if="loading.translate === article.id">翻譯中...</span>
                  <span v-else-if="article.translated">還原</span>
                  <span v-else>🈚️ 中文</span>
                </button>
                <button 
                  @click="copyNewsLink(article)" 
                  class="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                >
                  📋 複製連結
                </button>
                <button 
                  v-if="isValidUrl(article.url)"
                  @click="openArticleSafely(article.url, article.title)"
                  class="px-3 py-1 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200 transition-colors"
                >
                  🔗 開啟
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import axios from 'axios'

interface NewsArticle {
  id: string
  title: string
  summary: string
  url: string
  source: string
  publishedAt: string
  category: string
  sentiment?: 'positive' | 'negative' | 'neutral'
  image?: string
  translated?: boolean
  original_title?: string
  original_summary?: string
}

interface OnchainMetric {
  name: string
  value: string
  trend: 'up' | 'down' | 'stable'
}

interface EconomicIndicator {
  name: string
  value: string
  impact: 'positive' | 'negative' | 'neutral'
}

const stats = reactive({
  todayNews: 0,
  onchainEvents: 0,
  economicIndicators: 0,
  sentimentScore: '中性'
})

const loading = reactive({
  news: false,
  aiSummary: false,
  onchain: false,
  economic: false,
  translate: ''
})

const aiSummary = reactive({
  keyPoints: '',
  positiveFactors: '',
  riskFactors: ''
})

const news = ref<NewsArticle[]>([])
const selectedCategory = ref('all')
const onchainMetrics = ref<OnchainMetric[]>([])
const economicData = ref<EconomicIndicator[]>([])

const filteredNews = computed(() => {
  if (selectedCategory.value === 'all') {
    return news.value
  }
  return news.value.filter(article => article.category === selectedCategory.value)
})

const fetchNews = async () => {
  loading.news = true
  try {
    const response = await axios.get('/api/v1/news/latest')
    news.value = response.data
    stats.todayNews = news.value.length
  } catch (error) {
    console.error('獲取新聞失敗:', error)
    // 模擬數據
    news.value = [
      {
        id: '1',
        title: 'Bitcoin 突破 45,000 美元關鍵阻力位',
        summary: 'BTC 在機構投資者持續流入的推動下，成功突破技術分析關鍵阻力位，市場情緒轉為樂觀...',
        url: '#',
        source: 'CoinDesk',
        publishedAt: new Date().toISOString(),
        category: 'crypto',
        sentiment: 'positive'
      },
      {
        id: '2',
        title: '美聯儲暗示可能暫停升息',
        summary: '聯準會主席鮑威爾在最新演講中表示，考慮到通脹數據的改善，未來升息步調可能放緩...',
        url: '#',
        source: 'Reuters',
        publishedAt: new Date().toISOString(),
        category: 'economy',
        sentiment: 'positive'
      }
    ]
    stats.todayNews = news.value.length
  } finally {
    loading.news = false
  }
}

const fetchAISummary = async () => {
  loading.aiSummary = true
  try {
    const response = await axios.get('/api/v1/news/ai-summary')
    Object.assign(aiSummary, response.data)
  } catch (error) {
    console.error('獲取AI摘要失敗:', error)
    // 模擬數據
    aiSummary.keyPoints = '市場呈現謹慎樂觀態勢，比特幣突破關鍵阻力位，機構資金持續流入。美聯儲政策立場軟化為風險資產提供支撐。'
    aiSummary.positiveFactors = '1. 機構投資者持續增持加密貨幣 2. 美聯儲升息步調放緩預期 3. 技術面突破關鍵阻力位'
    aiSummary.riskFactors = '1. 全球經濟衰退風險仍存 2. 監管政策不確定性 3. 市場流動性偏緊'
  } finally {
    loading.aiSummary = false
  }
}

const fetchOnchainData = async () => {
  loading.onchain = true
  try {
    const response = await axios.get('/api/v1/news/onchain-metrics')
    onchainMetrics.value = response.data
  } catch (error) {
    console.error('獲取鏈上數據失敗:', error)
    // 模擬數據
    onchainMetrics.value = [
      { name: '大額轉帳數量', value: '+15%', trend: 'up' },
      { name: '交易所流入量', value: '2,450 BTC', trend: 'down' },
      { name: '活躍地址數', value: '985,432', trend: 'up' },
      { name: 'MVRV 比率', value: '1.25', trend: 'stable' },
      { name: '持幣大戶數量', value: '2,156', trend: 'up' }
    ]
    stats.onchainEvents = 5
  } finally {
    loading.onchain = false
  }
}

const fetchEconomicData = async () => {
  loading.economic = true
  try {
    const response = await axios.get('/api/v1/news/economic-indicators')
    economicData.value = response.data
  } catch (error) {
    console.error('獲取經濟指標失敗:', error)
    // 模擬數據
    economicData.value = [
      { name: '美國 CPI', value: '3.2%', impact: 'neutral' },
      { name: 'DXY 美元指數', value: '103.45', impact: 'negative' },
      { name: '10年期美債收益率', value: '4.25%', impact: 'negative' },
      { name: 'VIX 恐慌指數', value: '16.8', impact: 'positive' },
      { name: 'NASDAQ 100', value: '+1.2%', impact: 'positive' }
    ]
    stats.economicIndicators = 5
  } finally {
    loading.economic = false
  }
}

const refreshAISummary = () => {
  fetchAISummary()
}

const filterNews = () => {
  // 篩選邏輯已在 computed 中處理
}

const openArticle = (url: string, article?: NewsArticle) => {
  // 檢查URL有效性
  if (!url || url === '#' || url === '' || url.includes('example.com')) {
    // 如果是無效URL，顯示提示並返回
    alert('此新聞暫時無法跳轉，請稍後再試')
    return
  }
  
  // 檢查是否為有效的HTTP/HTTPS URL
  try {
    const urlObj = new URL(url)
    if (urlObj.protocol === 'http:' || urlObj.protocol === 'https:') {
      // 在新標籤頁中安全地開啟連結
      const newWindow = window.open(url, '_blank', 'noopener,noreferrer')
      if (!newWindow) {
        // 如果彈出視窗被阻擋
        const shouldCopy = confirm(`彈出視窗被瀏覽器阻擋。\n\n是否要複製連結？\n${url}`)
        if (shouldCopy) {
          copyToClipboard(url, article?.title || '新聞連結')
        }
      }
    } else {
      alert('無效的網址格式')
    }
  } catch (error) {
    // URL格式錯誤
    console.error('URL解析錯誤:', error)
    alert('網址格式有誤，無法開啟')
  }
}

const openArticleSafely = (url: string, title: string) => {
  try {
    const newWindow = window.open(url, '_blank', 'noopener,noreferrer')
    if (!newWindow) {
      const shouldCopy = confirm(`彈出視窗被阻擋，是否複製連結？\n\n標題：${title}\n連結：${url}`)
      if (shouldCopy) {
        copyToClipboard(url, title)
      }
    }
  } catch (error) {
    console.error('開啟連結失敗:', error)
    copyToClipboard(url, title)
  }
}

const copyToClipboard = async (text: string, title?: string) => {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text)
      alert(`✅ 連結已複製到剪貼簿！\n\n${title || '新聞連結'}`)
    } else {
      // 降級方案：使用舊方法
      const textArea = document.createElement('textarea')
      textArea.value = text
      textArea.style.position = 'fixed'
      textArea.style.left = '-999999px'
      textArea.style.top = '-999999px'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      
      try {
        document.execCommand('copy')
        alert(`✅ 連結已複製到剪貼簿！\n\n${title || '新聞連結'}`)
      } catch (err) {
        console.error('複製失敗:', err)
        alert(`❌ 複製失敗，請手動複製：\n\n${text}`)
      } finally {
        document.body.removeChild(textArea)
      }
    }
  } catch (error) {
    console.error('複製到剪貼簿失敗:', error)
    alert(`❌ 複製失敗，請手動複製：\n\n${text}`)
  }
}

const copyNewsLink = async (article: NewsArticle) => {
  await copyToClipboard(article.url, article.title)
}

const translateArticle = async (article: NewsArticle) => {
  if (article.translated) {
    // 還原到原始內容
    article.title = article.original_title || article.title
    article.summary = article.original_summary || article.summary
    article.translated = false
    return
  }
  
  loading.translate = article.id
  
  try {
    const response = await axios.post(`/api/v1/news/translate`, null, {
      params: {
        news_id: article.id,
        target_language: 'zh-TW'
      }
    })
    
    // 保存原始內容
    if (!article.original_title) {
      article.original_title = article.title
      article.original_summary = article.summary
    }
    
    // 更新為翻譯內容
    article.title = response.data.title
    article.summary = response.data.summary
    article.translated = true
    
    // 在新聞列表中更新該文章
    const index = news.value.findIndex(n => n.id === article.id)
    if (index !== -1) {
      news.value[index] = { ...article }
    }
    
  } catch (error) {
    console.error('翻譯失敗:', error)
    alert('翻譯服務暫時不可用，請稍後再試')
  } finally {
    loading.translate = ''
  }
}

const getCategoryColor = (category: string) => {
  const colors = {
    crypto: 'bg-orange-100 text-orange-800',
    economy: 'bg-blue-100 text-blue-800',
    technology: 'bg-green-100 text-green-800',
    defi: 'bg-purple-100 text-purple-800',
    nft: 'bg-pink-100 text-pink-800',
    regulation: 'bg-red-100 text-red-800'
  }
  return colors[category as keyof typeof colors] || 'bg-gray-100 text-gray-800'
}

const getCategoryText = (category: string) => {
  const texts = {
    crypto: '加密貨幣',
    economy: '經濟',
    technology: '科技',
    defi: 'DeFi',
    nft: 'NFT',
    regulation: '監管'
  }
  return texts[category as keyof typeof texts] || category
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-TW')
}

const isValidUrl = (url: string) => {
  if (!url || url === '#' || url === '' || url.includes('example.com')) {
    return false
  }
  try {
    const urlObj = new URL(url)
    return urlObj.protocol === 'http:' || urlObj.protocol === 'https:'
  } catch {
    return false
  }
}

const getUrlStatusClass = (url: string) => {
  return isValidUrl(url) ? 'text-gray-900' : 'text-gray-500'
}

const getUrlStatusText = (url: string) => {
  return isValidUrl(url) ? '點擊查看完整新聞' : '預覽模式 - 暫無外部連結'
}

onMounted(() => {
  fetchNews()
  fetchAISummary()
  fetchOnchainData()
  fetchEconomicData()
  
  // 計算整體情緒分數
  setTimeout(() => {
    const positiveCount = news.value.filter(n => n.sentiment === 'positive').length
    const totalCount = news.value.length
    if (totalCount > 0) {
      const positiveRatio = positiveCount / totalCount
      if (positiveRatio > 0.6) stats.sentimentScore = '樂觀'
      else if (positiveRatio < 0.4) stats.sentimentScore = '悲觀'
      else stats.sentimentScore = '中性'
    }
  }, 1000)
})
</script>
