"""
🔄 智能回退機制配置
Smart Fallback Configuration
"""

class FallbackConfig:
    """回退機制配置"""
    
    # 🚨 失敗檢測配置
    MAX_CONSECUTIVE_FAILURES = 3  # 連續失敗3次後啟用回退
    FAILURE_WINDOW_SECONDS = 30   # 30秒內的失敗計數
    PRICE_STALENESS_THRESHOLD = 10  # 10秒內的價格視為新鮮
    
    # ⏰ 回退恢復配置
    FALLBACK_RETRY_INTERVAL = 60  # 60秒後嘗試恢復鏈上數據
    SUCCESS_RECOVERY_COUNT = 5    # 連續成功5次後完全恢復
    
    # 🔍 健康檢查配置
    HEALTH_CHECK_INTERVAL = 30    # 30秒檢查一次系統健康
    RPC_TIMEOUT_THRESHOLD = 5     # RPC超時5秒視為不健康
    
    # 📊 性能監控
    PERFORMANCE_WINDOW = 300      # 5分鐘性能監控窗口
    TARGET_LATENCY_MS = 1000      # 目標延遲1秒以內
