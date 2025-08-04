#!/usr/bin/env python3
"""
狙擊手策略API清理腳本
根據分析結果移除未使用的API端點
"""

import os
import re
from pathlib import Path

class SniperAPICleanup:
    def __init__(self):
        self.cleanup_plan = {
            # 核心流程API - 保留
            'keep_core': [
                'dashboard-precision-signals',  # 前端主要使用
                'sniper-unified-data-layer',   # 前端使用
                'pandas-ta-direct',            # 前端使用 
                'signals',                     # 前端使用
                'phase1abc-integration-status', # 前端使用
                'phase3-market-depth',         # 前端使用
                'dynamic-parameters',          # 前端使用
                'expired',                     # 前端使用
                'history/signals',             # 前端使用
                'ws',                          # WebSocket
                'status',                      # 狀態檢查
            ],
            
            # 測試/調試API - 可安全移除
            'safe_remove': [
                'debug-active-signals',
                'test-email-notification', 
                'optimize-thresholds',
                'create-test-signal',
                'phase1a-templates-overview',
                'clear-all-signals',
                'active-signals-simple',
            ],
            
            # 實驗性/過時API - 建議移除
            'suggest_remove': [
                # Phase 1 舊版本API
                'force-precision-refresh',
                'process-expired',
                'cleanup-expired',
                'manual-expiration-trigger',
                'expiration-scheduler-status',
                'process-dynamic-expiration',
                
                # 複雜事件系統API (暫時不需要)
                'create-market-event',
                'event-multipliers',
                'execute-reallocation',
                'reallocation-status',
                'execute-timeframe-switch',
                'timeframe-status',
                'start-monitoring',
                'stop-monitoring',
                'event-predictions',
                'validate-predictions',
                'process-composite-events',
                'event-relations',
                'advanced-event-status',
                'assess-event-impact',
                'impact-assessment',
                'recent-impact-assessments',
                'asset-sensitivity-analysis',
                'impact-assessment-summary',
                
                # Phase 詳細分析API (前端未使用)
                'phase1a-signal-scoring',
                'phase1b-enhanced-signal-scoring',
                'phase1b-volatility-metrics',
                'phase1b-signal-continuity',
                'phase1ab-integration-status',
                'phase1c-enhanced-signal-scoring',
                'phase1c-standardization-metrics',
                'phase1c-extreme-signals',
                
                # 重複的歷史統計API
                'history/performance',
                'history/daily-summary',
                'history/generate-summary',
                'history/cleanup',
                
                # 低優先級監控API
                'realtime-sync-status',
                'performance-metrics',
                'signal-health-dashboard',
                'multi-timeframe-weights',
            ]
        }
    
    def create_streamlined_api(self):
        """創建精簡的API端點文件"""
        
        streamlined_api = '''from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ========================================
# 🎯 狙擊手策略核心API - 精簡版
# 只保留前端實際使用的端點
# ========================================

@router.get("/dashboard-precision-signals")
async def get_dashboard_precision_signals():
    """📊 核心API: 為儀表板提供精準篩選的信號"""
    try:
        from app.services.sniper_smart_layer import sniper_smart_layer
        
        current_signals = await sniper_smart_layer.get_all_active_signals()
        if not current_signals:
            return {
                "status": "success",
                "signals": [],
                "message": "當前無活躍信號",
                "timestamp": datetime.now().isoformat()
            }
        
        # 信號去重和篩選邏輯
        signal_map = {}
        for signal in current_signals:
            symbol = signal['symbol']
            if symbol not in signal_map:
                signal_map[symbol] = signal
            else:
                # 保留品質更高的信號
                existing_quality = signal_map[symbol].get('quality_score', 0)
                current_quality = signal.get('quality_score', 0)
                if current_quality > existing_quality:
                    signal_map[symbol] = signal
        
        return {
            "status": "success",
            "signals": list(signal_map.values()),
            "count": len(signal_map),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取精準信號失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sniper-unified-data-layer")
async def get_sniper_unified_data():
    """🎯 核心API: 狙擊手統一數據層"""
    try:
        from app.services.sniper_smart_layer import sniper_smart_layer
        
        # 獲取統一數據
        data = await sniper_smart_layer.get_unified_market_data()
        
        return {
            "status": "success",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取統一數據失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/signals")
async def get_signals():
    """📊 核心API: 獲取基礎信號列表"""
    try:
        from app.services.sniper_smart_layer import sniper_smart_layer
        
        signals = await sniper_smart_layer.get_all_active_signals()
        
        return {
            "status": "success",
            "signals": signals,
            "count": len(signals),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取信號失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pandas-ta-direct")
async def get_pandas_ta_analysis():
    """📈 核心API: 直接技術分析結果"""
    try:
        from app.services.technical_analysis import get_technical_analysis
        
        analysis = await get_technical_analysis()
        
        return {
            "status": "success", 
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"技術分析失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/expired")
async def get_expired_signals():
    """⏰ 核心API: 獲取過期信號"""
    try:
        from app.services.sniper_signal_history_service import get_expired_signals
        
        expired = await get_expired_signals()
        
        return {
            "status": "success",
            "expired_signals": expired,
            "count": len(expired),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取過期信號失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# 🎯 狙擊手歷史管理 - 精簡版
# ========================================

@router.get("/history/signals")
async def get_signal_history(
    days: int = 7,
    limit: int = 50,
    symbol: Optional[str] = None
):
    """📜 核心API: 獲取信號歷史"""
    try:
        from app.services.sniper_signal_history_service import get_signal_history
        
        history = await get_signal_history(
            days=days,
            limit=limit, 
            symbol=symbol
        )
        
        return {
            "status": "success",
            "signals": history,
            "count": len(history),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取歷史信號失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/statistics")
async def get_signal_statistics():
    """📊 核心API: 獲取信號統計"""
    try:
        from app.services.sniper_signal_history_service import get_statistics
        
        stats = await get_statistics()
        
        return {
            "status": "success",
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取統計失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# 🎯 狙擊手策略配置 - 精簡版  
# ========================================

@router.get("/dynamic-parameters")
async def get_dynamic_parameters():
    """⚙️ 核心API: 獲取動態參數"""
    try:
        from app.services.signal_scoring_engine import signal_scoring_engine
        
        params = await signal_scoring_engine.get_current_parameters()
        
        return {
            "status": "success",
            "parameters": params,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取參數失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/phase1abc-integration-status") 
async def get_phase_integration_status():
    """🔄 核心API: Phase 整合狀態"""
    try:
        from app.services.phase_integration import get_integration_status
        
        status = await get_integration_status()
        
        return {
            "status": "success",
            "integration": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取整合狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/phase3-market-depth")
async def get_phase3_market_depth():
    """📊 核心API: Phase 3 市場深度分析"""
    try:
        from app.services.phase3_analysis import get_market_depth_analysis
        
        analysis = await get_market_depth_analysis()
        
        return {
            "status": "success",
            "market_depth": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"市場深度分析失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# 🎯 系統狀態監控 - 精簡版
# ========================================

@router.get("/status")
async def get_system_status():
    """💓 核心API: 系統狀態檢查"""
    try:
        from app.services.system_monitor import get_system_health
        
        health = await get_system_health()
        
        return {
            "status": "success",
            "system_health": health,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"系統狀態檢查失敗: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
'''
        
        # 保存精簡API文件
        with open('app/api/v1/endpoints/sniper_core_streamlined.py', 'w', encoding='utf-8') as f:
            f.write(streamlined_api)
        
        print("✅ 已創建精簡版狙擊手API: app/api/v1/endpoints/sniper_core_streamlined.py")
    
    def generate_cleanup_script(self):
        """生成API清理腳本"""
        
        cleanup_script = '''#!/usr/bin/env python3
"""
狙擊手API清理建議報告
"""

print("🧹 狙擊手API清理建議")
print("=" * 60)

# 核心流程API - 必須保留
CORE_APIS = [
    "dashboard-precision-signals",  # 前端主要API
    "sniper-unified-data-layer",   # 前端數據源
    "pandas-ta-direct",            # 技術分析
    "signals",                     # 基礎信號
    "expired",                     # 過期信號
    "history/signals",             # 歷史記錄
    "status",                      # 系統狀態
]

# 測試/調試API - 可以移除
DEBUG_APIS = [
    "debug-active-signals",
    "test-email-notification", 
    "create-test-signal",
    "clear-all-signals",
    "active-signals-simple",
]

# 複雜功能API - 暫時可移除
COMPLEX_APIS = [
    "force-precision-refresh",
    "process-expired", 
    "cleanup-expired",
    "create-market-event",
    "execute-reallocation",
    "start-monitoring",
    "stop-monitoring",
    "event-predictions",
    "phase1a-signal-scoring",
    "phase1b-enhanced-signal-scoring",
    "impact-assessment",
]

print(f"✅ 保留核心API: {len(CORE_APIS)} 個")
for api in CORE_APIS:
    print(f"  - {api}")

print(f"\\n🗑️ 建議移除: {len(DEBUG_APIS + COMPLEX_APIS)} 個")
print("  調試API:")
for api in DEBUG_APIS:
    print(f"    - {api}")
    
print("  複雜功能API:")
for api in COMPLEX_APIS[:5]:
    print(f"    - {api}")
print(f"    ... 和其他 {len(COMPLEX_APIS) - 5} 個")

print("\\n📋 清理步驟:")
print("1. 先備份現有API文件")
print("2. 創建精簡版API文件")  
print("3. 測試前端功能正常")
print("4. 逐步移除未使用端點")
'''
        
        with open('sniper_api_cleanup_report.py', 'w', encoding='utf-8') as f:
            f.write(cleanup_script)
        
        print("✅ 已生成API清理報告: sniper_api_cleanup_report.py")
    
    def show_cleanup_summary(self):
        """顯示清理摘要"""
        print("\\n🎯 狙擊手API清理摘要")
        print("=" * 80)
        
        print(f"\\n✅ 保留核心API ({len(self.cleanup_plan['keep_core'])} 個):")
        for api in self.cleanup_plan['keep_core']:
            print(f"  - {api}")
        
        print(f"\\n🗑️ 建議移除API ({len(self.cleanup_plan['safe_remove']) + len(self.cleanup_plan['suggest_remove'])} 個):")
        print("  📄 安全移除 (測試/調試):")
        for api in self.cleanup_plan['safe_remove']:
            print(f"    - {api}")
        
        print("  ⚠️ 建議移除 (未使用):")
        for api in self.cleanup_plan['suggest_remove'][:10]:  # 只顯示前10個
            print(f"    - {api}")
        if len(self.cleanup_plan['suggest_remove']) > 10:
            print(f"    ... 和其他 {len(self.cleanup_plan['suggest_remove']) - 10} 個")
        
        print("\\n📊 清理效果:")
        total_remove = len(self.cleanup_plan['safe_remove']) + len(self.cleanup_plan['suggest_remove'])
        total_keep = len(self.cleanup_plan['keep_core'])
        print(f"  - 移除端點: {total_remove} 個")
        print(f"  - 保留端點: {total_keep} 個") 
        print(f"  - 精簡比例: {(total_remove / (total_remove + total_keep) * 100):.1f}%")

if __name__ == "__main__":
    cleanup = SniperAPICleanup()
    cleanup.show_cleanup_summary()
    cleanup.create_streamlined_api()
    cleanup.generate_cleanup_script()
