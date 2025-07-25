import axios, { AxiosRequestConfig, InternalAxiosRequestConfig } from 'axios'

// 擴展 axios 類型定義
interface CustomAxiosRequestConfig extends AxiosRequestConfig {
    retry?: number
    retryDelay?: number
    __retryCount?: number
    metadata?: {
        startTime: Date
    }
}

interface CustomInternalAxiosRequestConfig extends InternalAxiosRequestConfig {
    retry?: number
    retryDelay?: number
    __retryCount?: number
    metadata?: {
        startTime: Date
    }
}

// 建立 axios 實例
const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    timeout: 15000, // 增加到 15 秒超時
} as CustomAxiosRequestConfig)

// 請求攔截器
api.interceptors.request.use(
    (config: CustomInternalAxiosRequestConfig) => {
        // 添加請求時間戳
        config.metadata = { startTime: new Date() }
        // 設置默認重試配置
        config.retry = config.retry || 3
        config.retryDelay = config.retryDelay || 1000
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// 響應攔截器
api.interceptors.response.use(
    (response) => {
        // 記錄請求時間
        const endTime = new Date()
        const config = response.config as CustomInternalAxiosRequestConfig
        if (config.metadata) {
            const duration = endTime.getTime() - config.metadata.startTime.getTime()
            console.log(`API請求: ${response.config.url} - ${duration}ms`)
        }
        return response
    },
    async (error) => {
        const config = error.config as CustomInternalAxiosRequestConfig

        // 如果沒有配置重試，則直接拋出錯誤
        if (!config || !config.retry) {
            return Promise.reject(error)
        }

        // 設置重試計數器
        config.__retryCount = config.__retryCount || 0

        // 檢查是否應該重試
        if (config.__retryCount >= config.retry) {
            return Promise.reject(error)
        }

        // 增加重試計數
        config.__retryCount += 1

        // 如果是網絡錯誤或超時錯誤，嘗試重試
        if (
            error.code === 'ERR_NETWORK' ||
            error.code === 'ERR_CONNECTION_TIMED_OUT' ||
            error.code === 'ECONNABORTED' ||
            (error.response && error.response.status >= 500)
        ) {
            console.log(`重試請求: ${config.url} (第${config.__retryCount}次)`)

            // 延遲重試
            await new Promise(resolve => setTimeout(resolve, config.retryDelay || 1000))

            // 重新發送請求
            return api(config)
        }

        return Promise.reject(error)
    }
)

export default api

// 便利方法
export const get = (url: string, config = {}) => api.get(url, config)
export const post = (url: string, data?: any, config = {}) => api.post(url, data, config)
export const put = (url: string, data?: any, config = {}) => api.put(url, data, config)
export const del = (url: string, config = {}) => api.delete(url, config)

// 健康檢查方法
export const checkHealth = async (): Promise<boolean> => {
    try {
        await api.get('/health', { timeout: 5000 })
        return true
    } catch (error) {
        console.error('健康檢查失敗:', error)
        return false
    }
}

// 等待服務可用
export const waitForService = async (maxAttempts = 10, delay = 2000): Promise<boolean> => {
    for (let i = 0; i < maxAttempts; i++) {
        const isHealthy = await checkHealth()
        if (isHealthy) {
            console.log('服務已就緒')
            return true
        }

        console.log(`等待服務啟動... (${i + 1}/${maxAttempts})`)
        await new Promise(resolve => setTimeout(resolve, delay))
    }

    console.error('服務啟動超時')
    return false
}
