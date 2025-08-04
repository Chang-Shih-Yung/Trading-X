// 🎯 狙擊手信號持久化系統 - 前端

class SniperSignalPersistence {
    constructor() {
        this.STORAGE_KEY = 'sniper_signals_cache'
        this.HISTORY_KEY = 'sniper_signals_history'
        this.MAX_CACHE_SIZE = 100
        this.MAX_HISTORY_SIZE = 500
        this.CACHE_EXPIRE_HOURS = 24
        
        // 初始化
        this.initializeStorage()
    }
    
    initializeStorage() {
        // 檢查並初始化 localStorage
        if (!localStorage.getItem(this.STORAGE_KEY)) {
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify({
                version: '1.0',
                lastUpdate: new Date().toISOString(),
                signals: {},
                metadata: {}
            }))
        }
        
        if (!localStorage.getItem(this.HISTORY_KEY)) {
            localStorage.setItem(this.HISTORY_KEY, JSON.stringify({
                version: '1.0',
                signals: [],
                index: {}
            }))
        }
    }
    
    // ==================== 信號緩存管理 ====================
    
    /**
     * 保存活躍信號到本地緩存
     * @param {Array} signals - 信號列表
     */
    saveActiveSignals(signals) {
        try {
            const cache = this.getCache()
            const now = new Date().toISOString()
            
            // 更新活躍信號
            cache.signals = {}
            cache.lastUpdate = now
            
            signals.forEach(signal => {
                cache.signals[signal.symbol] = {
                    ...signal,
                    cachedAt: now,
                    expiresAt: this.calculateExpiryTime(signal)
                }
            })
            
            // 更新元數據
            cache.metadata = {
                totalSignals: signals.length,
                highQualityCount: signals.filter(s => s.confidence >= 0.8).length,
                lastSyncTime: now,
                version: cache.version
            }
            
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(cache))
            console.log(`💾 已緩存 ${signals.length} 個狙擊手信號`)
            
            return true
        } catch (error) {
            console.error('❌ 保存活躍信號失敗:', error)
            return false
        }
    }
    
    /**
     * 從本地緩存獲取活躍信號
     * @returns {Array} 緩存的信號列表
     */
    getActiveSignals() {
        try {
            const cache = this.getCache()
            const now = new Date()
            
            // 檢查緩存是否過期
            if (this.isCacheExpired(cache.lastUpdate)) {
                console.warn('⚠️ 信號緩存已過期')
                return []
            }
            
            // 過濾有效信號
            const validSignals = Object.values(cache.signals).filter(signal => {
                const expiryTime = new Date(signal.expiresAt)
                return now < expiryTime
            })
            
            console.log(`📦 從緩存加載 ${validSignals.length} 個有效信號`)
            return validSignals
            
        } catch (error) {
            console.error('❌ 獲取活躍信號失敗:', error)
            return []
        }
    }
    
    /**
     * 更新單個信號
     * @param {Object} signal - 更新的信號
     */
    updateSignal(signal) {
        try {
            const cache = this.getCache()
            const now = new Date().toISOString()
            
            cache.signals[signal.symbol] = {
                ...signal,
                cachedAt: now,
                expiresAt: this.calculateExpiryTime(signal)
            }
            
            cache.lastUpdate = now
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(cache))
            
            console.log(`🔄 已更新 ${signal.symbol} 信號`)
            return true
            
        } catch (error) {
            console.error(`❌ 更新 ${signal.symbol} 信號失敗:`, error)
            return false
        }
    }
    
    // ==================== 歷史數據管理 ====================
    
    /**
     * 添加信號到歷史記錄
     * @param {Object} signal - 要歷史化的信號
     */
    addToHistory(signal) {
        try {
            const history = this.getHistory()
            const now = new Date().toISOString()
            
            const historyRecord = {
                ...signal,
                archivedAt: now,
                status: this.determineSignalStatus(signal),
                performance: this.calculateSignalPerformance(signal)
            }
            
            // 添加到歷史列表
            history.signals.unshift(historyRecord)
            
            // 更新索引
            if (!history.index[signal.symbol]) {
                history.index[signal.symbol] = []
            }
            history.index[signal.symbol].unshift(historyRecord.signal_id)
            
            // 限制歷史記錄大小
            if (history.signals.length > this.MAX_HISTORY_SIZE) {
                const removed = history.signals.splice(this.MAX_HISTORY_SIZE)
                this.cleanupIndexes(removed, history.index)
            }
            
            localStorage.setItem(this.HISTORY_KEY, JSON.stringify(history))
            console.log(`📚 已添加 ${signal.symbol} 到歷史記錄`)
            
            return true
            
        } catch (error) {
            console.error(`❌ 添加 ${signal.symbol} 到歷史失敗:`, error)
            return false
        }
    }
    
    /**
     * 獲取歷史信號
     * @param {Object} filters - 過濾條件
     * @returns {Array} 歷史信號列表
     */
    getHistorySignals(filters = {}) {
        try {
            const history = this.getHistory()
            let signals = [...history.signals]
            
            // 應用過濾器
            if (filters.symbol) {
                signals = signals.filter(s => s.symbol === filters.symbol)
            }
            
            if (filters.signal_type) {
                signals = signals.filter(s => s.signal_type === filters.signal_type)
            }
            
            if (filters.status) {
                signals = signals.filter(s => s.status === filters.status)
            }
            
            if (filters.days) {
                const cutoffDate = new Date()
                cutoffDate.setDate(cutoffDate.getDate() - filters.days)
                signals = signals.filter(s => new Date(s.created_at) >= cutoffDate)
            }
            
            // 限制返回數量
            if (filters.limit) {
                signals = signals.slice(0, filters.limit)
            }
            
            console.log(`📊 獲取歷史信號: ${signals.length} 條記錄`)
            return signals
            
        } catch (error) {
            console.error('❌ 獲取歷史信號失敗:', error)
            return []
        }
    }
    
    /**
     * 獲取特定幣種的最後一個策略
     * @param {string} symbol - 幣種符號
     * @returns {Object|null} 最後的策略信號
     */
    getLastStrategy(symbol) {
        try {
            // 先檢查活躍信號
            const cache = this.getCache()
            if (cache.signals[symbol]) {
                const signal = cache.signals[symbol]
                return {
                    ...signal,
                    source: 'active',
                    recommendation: this.analyzeSignalRecommendation(signal)
                }
            }
            
            // 檢查歷史記錄
            const history = this.getHistory()
            const symbolHistory = history.signals.filter(s => s.symbol === symbol)
            
            if (symbolHistory.length > 0) {
                const lastSignal = symbolHistory[0]  // 最新的歷史記錄
                return {
                    ...lastSignal,
                    source: 'history',
                    recommendation: this.analyzeHistoryRecommendation(lastSignal)
                }
            }
            
            return null
            
        } catch (error) {
            console.error(`❌ 獲取 ${symbol} 最後策略失敗:`, error)
            return null
        }
    }
    
    // ==================== 智能分析功能 ====================
    
    /**
     * 分析活躍信號的建議
     * @param {Object} signal - 活躍信號
     * @returns {Object} 分析建議
     */
    analyzeSignalRecommendation(signal) {
        const now = new Date()
        const expiryTime = new Date(signal.expiresAt)
        const timeRemaining = (expiryTime - now) / (1000 * 60)  // 分鐘
        
        let action, reason, priority
        
        if (timeRemaining <= 0) {
            action = '信號過期'
            reason = '信號已過期，需要重新分析市場'
            priority = 'HIGH'
        } else if (signal.confidence >= 0.9) {
            action = '堅持持有'
            reason = `超高信心度信號(${(signal.confidence * 100).toFixed(1)}%)，建議堅持策略`
            priority = 'LOW'
        } else if (signal.confidence >= 0.75) {
            action = '謹慎持有'
            reason = `高信心度信號(${(signal.confidence * 100).toFixed(1)}%)，密切觀察市場變化`
            priority = 'MEDIUM'
        } else if (signal.confidence >= 0.6) {
            action = '考慮調整'
            reason = `中等信心度信號(${(signal.confidence * 100).toFixed(1)}%)，考慮調整策略`
            priority = 'MEDIUM'
        } else {
            action = '考慮止損'
            reason = `低信心度信號(${(signal.confidence * 100).toFixed(1)}%)，優先考慮風險控制`
            priority = 'HIGH'
        }
        
        return {
            action,
            reason,
            priority,
            timeRemaining: Math.max(0, timeRemaining),
            riskLevel: this.calculateRiskLevel(signal)
        }
    }
    
    /**
     * 分析歷史信號的建議
     * @param {Object} historySignal - 歷史信號
     * @returns {Object} 分析建議
     */
    analyzeHistoryRecommendation(historySignal) {
        const performance = historySignal.performance || {}
        
        let action, reason, priority
        
        if (historySignal.status === 'HIT_TP') {
            action = '重新分析'
            reason = '上次信號成功止盈，可以尋找新的機會'
            priority = 'MEDIUM'
        } else if (historySignal.status === 'HIT_SL') {
            action = '謹慎觀望'
            reason = '上次信號觸發止損，建議等待更好的進場點'
            priority = 'LOW'
        } else if (historySignal.status === 'EXPIRED') {
            action = '市場分析'
            reason = '上次信號自然過期，需要重新分析市場趨勢'
            priority = 'MEDIUM'
        } else {
            action = '等待信號'
            reason = '暫無明確的歷史參考，等待新的高品質信號'
            priority = 'LOW'
        }
        
        return {
            action,
            reason,
            priority,
            lastPerformance: performance,
            suggestion: this.generateStrategySuggestion(historySignal)
        }
    }
    
    /**
     * 生成策略建議
     * @param {Object} signal - 信號對象
     * @returns {string} 策略建議
     */
    generateStrategySuggestion(signal) {
        const riskReward = Math.abs(signal.take_profit - signal.entry_price) / 
                           Math.abs(signal.entry_price - signal.stop_loss)
        
        if (riskReward >= 2.5) {
            return '風險回報比優秀，適合積極交易者'
        } else if (riskReward >= 1.8) {
            return '風險回報比良好，適合穩健交易者'
        } else {
            return '風險回報比一般，建議謹慎考慮'
        }
    }
    
    // ==================== 數據同步功能 ====================
    
    /**
     * 與後端同步數據
     * @param {Function} apiCall - API 調用函數
     */
    async syncWithBackend(apiCall) {
        try {
            console.log('🔄 開始與後端同步數據...')
            
            // 獲取後端最新數據
            const backendData = await apiCall()
            
            if (backendData && backendData.length > 0) {
                // 保存到本地緩存
                this.saveActiveSignals(backendData)
                
                // 檢查是否有新的歷史信號需要歸檔
                await this.archiveExpiredSignals()
                
                console.log('✅ 數據同步完成')
                return backendData
            } else {
                console.warn('⚠️ 後端返回空數據，使用本地緩存')
                return this.getActiveSignals()
            }
            
        } catch (error) {
            console.error('❌ 數據同步失敗，使用本地緩存:', error)
            return this.getActiveSignals()
        }
    }
    
    /**
     * 歸檔過期信號
     */
    async archiveExpiredSignals() {
        try {
            const cache = this.getCache()
            const now = new Date()
            
            Object.values(cache.signals).forEach(signal => {
                const expiryTime = new Date(signal.expiresAt)
                if (now >= expiryTime) {
                    // 信號過期，添加到歷史
                    this.addToHistory(signal)
                    delete cache.signals[signal.symbol]
                }
            })
            
            // 更新緩存
            cache.lastUpdate = now.toISOString()
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(cache))
            
        } catch (error) {
            console.error('❌ 歸檔過期信號失敗:', error)
        }
    }
    
    // ==================== 工具函數 ====================
    
    getCache() {
        try {
            const cache = JSON.parse(localStorage.getItem(this.STORAGE_KEY))
            return cache || { version: '1.0', lastUpdate: new Date().toISOString(), signals: {}, metadata: {} }
        } catch (error) {
            console.error('❌ 讀取緩存失敗:', error)
            return { version: '1.0', lastUpdate: new Date().toISOString(), signals: {}, metadata: {} }
        }
    }
    
    getHistory() {
        try {
            const history = JSON.parse(localStorage.getItem(this.HISTORY_KEY))
            return history || { version: '1.0', signals: [], index: {} }
        } catch (error) {
            console.error('❌ 讀取歷史失敗:', error)
            return { version: '1.0', signals: [], index: {} }
        }
    }
    
    isCacheExpired(lastUpdate) {
        if (!lastUpdate) return true
        
        const cacheTime = new Date(lastUpdate)
        const now = new Date()
        const hoursDiff = (now - cacheTime) / (1000 * 60 * 60)
        
        return hoursDiff > this.CACHE_EXPIRE_HOURS
    }
    
    calculateExpiryTime(signal) {
        // 根據信號的時間框架計算過期時間
        const timeframes = {
            'SHORT_TERM': 5 * 60,      // 5分鐘
            'MEDIUM_TERM': 30 * 60,    // 30分鐘  
            'LONG_TERM': 120 * 60      // 2小時
        }
        
        const expiryMinutes = timeframes[signal.timeframe] || 60
        const expiryTime = new Date()
        expiryTime.setMinutes(expiryTime.getMinutes() + expiryMinutes)
        
        return expiryTime.toISOString()
    }
    
    determineSignalStatus(signal) {
        // 根據信號狀態判斷結果
        // 實際應用中可能需要從交易記錄中獲取
        const statuses = ['EXPIRED', 'HIT_TP', 'HIT_SL', 'CANCELLED']
        return statuses[Math.floor(Math.random() * statuses.length)]
    }
    
    calculateSignalPerformance(signal) {
        // 計算信號表現
        return {
            duration: this.calculateSignalDuration(signal),
            maxDrawdown: Math.random() * 0.05,  // 模擬最大回撤
            finalReturn: (Math.random() - 0.5) * 0.1  // 模擬最終收益
        }
    }
    
    calculateSignalDuration(signal) {
        const created = new Date(signal.created_at)
        const now = new Date()
        return Math.floor((now - created) / (1000 * 60))  // 分鐘
    }
    
    calculateRiskLevel(signal) {
        const stopLossDistance = Math.abs(signal.entry_price - signal.stop_loss) / signal.entry_price
        
        if (stopLossDistance <= 0.03) return 'LOW'      // 3%以內
        if (stopLossDistance <= 0.07) return 'MEDIUM'   // 7%以內
        return 'HIGH'  // 超過7%
    }
    
    cleanupIndexes(removedSignals, index) {
        // 清理索引中已被移除的信號
        removedSignals.forEach(signal => {
            if (index[signal.symbol]) {
                const signalIndex = index[signal.symbol].indexOf(signal.signal_id)
                if (signalIndex > -1) {
                    index[signal.symbol].splice(signalIndex, 1)
                }
            }
        })
    }
    
    // ==================== 統計分析功能 ====================
    
    /**
     * 獲取信號統計數據
     * @returns {Object} 統計數據
     */
    getStatistics() {
        try {
            const cache = this.getCache()
            const history = this.getHistory()
            
            const activeSignals = Object.values(cache.signals)
            const historySignals = history.signals
            
            return {
                active: {
                    total: activeSignals.length,
                    highQuality: activeSignals.filter(s => s.confidence >= 0.8).length,
                    symbols: [...new Set(activeSignals.map(s => s.symbol))],
                    averageConfidence: activeSignals.length > 0 
                        ? activeSignals.reduce((sum, s) => sum + s.confidence, 0) / activeSignals.length 
                        : 0
                },
                history: {
                    total: historySignals.length,
                    successful: historySignals.filter(s => s.status === 'HIT_TP').length,
                    failed: historySignals.filter(s => s.status === 'HIT_SL').length,
                    expired: historySignals.filter(s => s.status === 'EXPIRED').length
                },
                performance: {
                    winRate: this.calculateWinRate(historySignals),
                    averageReturn: this.calculateAverageReturn(historySignals)
                }
            }
        } catch (error) {
            console.error('❌ 獲取統計數據失敗:', error)
            return null
        }
    }
    
    calculateWinRate(signals) {
        if (signals.length === 0) return 0
        const successful = signals.filter(s => s.status === 'HIT_TP').length
        return successful / signals.length
    }
    
    calculateAverageReturn(signals) {
        if (signals.length === 0) return 0
        const validSignals = signals.filter(s => s.performance && s.performance.finalReturn)
        if (validSignals.length === 0) return 0
        
        const totalReturn = validSignals.reduce((sum, s) => sum + s.performance.finalReturn, 0)
        return totalReturn / validSignals.length
    }
    
    /**
     * 清理存儲數據
     */
    clearStorage() {
        try {
            localStorage.removeItem(this.STORAGE_KEY)
            localStorage.removeItem(this.HISTORY_KEY)
            this.initializeStorage()
            console.log('🗑️ 已清理所有存儲數據')
            return true
        } catch (error) {
            console.error('❌ 清理存儲數據失敗:', error)
            return false
        }
    }
    
    /**
     * 導出數據
     * @returns {Object} 導出的數據
     */
    exportData() {
        try {
            const cache = this.getCache()
            const history = this.getHistory()
            
            return {
                timestamp: new Date().toISOString(),
                cache,
                history,
                statistics: this.getStatistics()
            }
        } catch (error) {
            console.error('❌ 導出數據失敗:', error)
            return null
        }
    }
}

// 導出持久化系統
export default SniperSignalPersistence
