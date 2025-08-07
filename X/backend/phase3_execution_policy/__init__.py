"""
Phase3 Execution Policy Layer - 執行決策層
=======================================

## 系統概述
Phase3 Execution Policy Layer是Trading-X系統的智能執行決策層，負責將Phase2的
預評估候選信號轉化為精確的交易執行決策。採用四情境智能決策引擎，覆蓋所有交易場景。

## 核心模組
- **EPL Intelligent Decision Engine**: 四情境智能決策引擎
  - 🔁 替換決策引擎 (Replacement Decision Engine)
  - ➕ 加倉決策引擎 (Strengthening Decision Engine) 
  - ✅ 新倉決策引擎 (New Position Decision Engine)
  - ❌ 忽略決策引擎 (Ignore Decision Engine)
- **Priority Classification Engine**: 優先級分類引擎
- **Execution Policy Layer**: 主執行決策協調層

## 四情境決策邏輯
### 🔁 替換決策 (Replace Existing Position)
- 信心度差異評估 (≥15%提升)
- 市場時機分析與持倉表現評估
- 觸發條件: 相反方向 + 明顯優勢 + 持倉年齡>5分鐘

### ➕ 加倉決策 (Strengthen Position)  
- 信心度提升檢查 (≥8%提升)
- 風險集中度控制與倉位優化
- 觸發條件: 方向一致 + 持倉盈利 + 風險可控

### ✅ 新倉決策 (Create New Position)
- 品質門檻驗證 (≥80%品質要求)
- 組合相關性檢查與容量管理
- 觸發條件: 無現有持倉 + 高品質信號 + 組合空間

### ❌ 忽略決策 (Ignore Signal)
- 品質不足/重複性高/市場不利/風險超標
- 學習記錄與改進建議生成

## 優先級分類系統
- 🚨 **CRITICAL級**: ≥0.85評分 + 緊急市場機會 (全通道即時通知)
- 🎯 **HIGH級**: ≥0.75評分 + 強趨勢確認 (主通道5分鐘延遲)
- 📊 **MEDIUM級**: ≥0.60評分 + 正常市場條件 (標準30分鐘批量)
- 📈 **LOW級**: ≥0.40評分 + 研究性機會 (日終摘要)

## 風險管理架構
### 組合層級控制
- 最大持倉數: 8個同時持倉
- 組合相關性: ≤70%限制
- 行業集中度: ≤40%單一行業
- 每日風險預算: 5%組合風險

### 持倉層級控制
- 單一持倉: ≤15%組合限制
- 強制止損執行與動態調整
- 移動止損與止盈優化

## 性能指標
- 📥 數據驗證層: 50ms (格式+範圍+完整性)
- 🚦 情境路由層: 30ms (持倉檢查+路由分配)
- ⚡ 四情境並行: 150ms (最慢情境決定總時間)
  - 替換決策: 120ms | 加倉決策: 100ms
  - 新倉決策: 150ms | 忽略決策: 60ms
- 🛡️ 風險驗證層: 80ms (多層級風險控制)
- 🎯 優先分類層: 40ms (權重計算+分級)
- 📊 績效追蹤層: 30ms (追蹤設置+學習整合)
- 📡 通知分發層: 100ms (多通道分發)
- **總處理時間**: 450ms (完整EPL處理週期)

## 通知分發系統
### 多通道支援
- 📧 **Gmail通知**: OAuth2安全認證 + HTML圖表模板
- 🌐 **WebSocket廣播**: 即時更新 + 智能過濾 + 24小時持久化  
- 🖥️ **前端整合**: 儀表板更新 + 優先級高亮 + 聲音警報
- 📱 **緊急SMS**: 僅CRITICAL級 + 速率限制(3次/小時)

### 延遲管理策略
- 🚨 CRITICAL: 即時投遞 (0ms延遲)
- 🎯 HIGH: 5分鐘批量 (300s延遲)  
- 📊 MEDIUM: 30分鐘批量 (1800s延遲)
- 📈 LOW: 日終摘要 (批量處理)

## 高級特性
- 🌍 **市場制度適應**: 牛市/熊市/橫盤/波動制度動態調整
- 🤖 **機器學習整合**: 決策預測 + 時機預測 + 模式識別
- ⏰ **多時間框架驗證**: 1m-1d全時間框架技術確認
- 🔄 **自適應學習**: 決策結果反饋 + 閾值優化 + 參數自調整

## 系統彈性
- **故障轉移**: 決策引擎失效→保守默認 + 通知重試隊列
- **性能降級**: 高負載→優先CRITICAL + 簡化邏輯 + 本地快取
- **自我監控**: 延遲監控 + 準確率追蹤 + 異常檢測

版本: 2.1.0
最後更新: 2025-08-07
開發團隊: Trading-X Team
"""

# 核心模組導入
from .epl_intelligent_decision_engine import (
    # 決策枚舉
    EPLDecision,
    SignalPriority,
    
    # 數據結構
    PositionInfo,
    EPLDecisionResult,
    
    # 四情境決策引擎
    ReplacementDecisionEngine,
    StrengtheningDecisionEngine, 
    NewPositionDecisionEngine,
    IgnoreDecisionEngine,
    
    # 優先級分類引擎
    PriorityClassificationEngine,
    
    # 主執行決策層
    ExecutionPolicyLayer,
    
    # 全局實例
    execution_policy_layer
)

# 模組版本資訊
__version__ = "2.1.0"
__author__ = "Trading-X Team"
__description__ = "Phase3 Execution Policy Layer - 四情境智能決策引擎"

# 主要類別與枚舉匯出
__all__ = [
    # === 核心枚舉 ===
    "EPLDecision",           # 🔁➕✅❌ 四種決策類型
    "SignalPriority",        # 🚨🎯📊📈 四級優先級別
    
    # === 數據結構 ===  
    "PositionInfo",          # 持倉信息結構
    "EPLDecisionResult",     # 決策結果輸出結構
    
    # === 四情境決策引擎 ===
    "ReplacementDecisionEngine",    # 🔁 替換決策引擎
    "StrengtheningDecisionEngine",  # ➕ 加倉決策引擎
    "NewPositionDecisionEngine",    # ✅ 新倉決策引擎  
    "IgnoreDecisionEngine",         # ❌ 忽略決策引擎
    
    # === 分類與協調引擎 ===
    "PriorityClassificationEngine", # 🎯 優先級分類引擎
    "ExecutionPolicyLayer",         # 🏛️ 主執行決策協調層
    
    # === 全局實例 ===
    "execution_policy_layer"        # 🌟 即用型EPL實例
]

# 系統配置常數
SYSTEM_CONFIG = {
    "version": "2.1.0",
    "processing_timeout_ms": 800,
    "target_processing_ms": 450,
    "risk_management": {
        "max_concurrent_positions": 8,
        "max_portfolio_correlation": 0.70,
        "max_sector_concentration": 0.40,
        "daily_risk_budget": 0.05,
        "max_position_size": 0.15
    },
    "decision_thresholds": {
        "replacement_min_confidence_diff": 0.15,
        "strengthening_min_confidence_improvement": 0.08,
        "new_position_min_quality": 0.80,
        "ignore_max_quality": 0.40
    },
    "priority_thresholds": {
        "CRITICAL": {"score": 0.85, "confidence": 0.90},
        "HIGH": {"score": 0.75, "confidence": 0.80},
        "MEDIUM": {"score": 0.60, "confidence": 0.65},
        "LOW": {"score": 0.40, "confidence": 0.50}
    },
    "notification_delays": {
        "CRITICAL": 0,      # 即時投遞
        "HIGH": 300,        # 5分鐘批量
        "MEDIUM": 1800,     # 30分鐘批量  
        "LOW": 86400        # 日終摘要
    }
}

# 決策引擎配置
DECISION_ENGINE_CONFIG = {
    "replacement_engine": {
        "min_position_age_minutes": 5,
        "confidence_weight": 0.40,
        "market_timing_weight": 0.25,
        "position_performance_weight": 0.20,
        "risk_assessment_weight": 0.15,
        "min_replacement_score": 0.75
    },
    "strengthening_engine": {
        "confidence_improvement_weight": 0.35,
        "position_performance_weight": 0.25,
        "risk_concentration_weight": 0.25,
        "market_timing_weight": 0.15,
        "min_strengthening_score": 0.70,
        "max_additional_concentration": 0.30
    },
    "new_position_engine": {
        "signal_quality_weight": 0.40,
        "market_suitability_weight": 0.25,
        "portfolio_correlation_weight": 0.20,
        "timing_optimization_weight": 0.15,
        "min_creation_score": 0.70,
        "min_quality_threshold": 0.80
    },
    "ignore_engine": {
        "quality_check_weight": 0.30,
        "duplication_check_weight": 0.25,
        "market_timing_weight": 0.25,
        "risk_management_weight": 0.20
    }
}

# 性能監控配置
PERFORMANCE_CONFIG = {
    "target_times_ms": {
        "data_validation": 50,
        "scenario_routing": 30,
        "parallel_decisions": 150,
        "risk_validation": 80,
        "priority_classification": 40,
        "performance_tracking": 30,
        "notification_dispatch": 100
    },
    "monitoring_thresholds": {
        "decision_latency_alert_ms": 500,
        "accuracy_rate_min": 0.75,
        "system_health_check_interval_s": 60
    }
}

# 通知系統配置  
NOTIFICATION_CONFIG = {
    "channels": {
        "gmail": {
            "enabled": True,
            "templates": {
                "CRITICAL": "urgent_trading_alert",
                "HIGH": "important_signal_alert"
            },
            "auth_method": "OAuth2"
        },
        "websocket": {
            "enabled": True,
            "persistence_hours": 24,
            "auto_reconnect": True
        },
        "frontend": {
            "enabled": True,
            "dashboard_updates": True,
            "priority_highlights": True,
            "sound_alerts": True
        },
        "sms": {
            "enabled": True,
            "critical_only": True,
            "rate_limit_per_hour": 3,
            "message_length_limit": 160
        }
    }
}

# 模組初始化日誌
import logging
logger = logging.getLogger(__name__)
logger.info(f"📡 Phase3 Execution Policy Layer v{__version__} 初始化完成")
logger.info(f"🔁➕✅❌ 四情境決策引擎已載入")
logger.info(f"🎯 優先級分類系統: {list(SYSTEM_CONFIG['priority_thresholds'].keys())}")
logger.info(f"⚡ 目標處理時間: {SYSTEM_CONFIG['target_processing_ms']}ms")
