"""
增強技術分析 API 端點
提供即時技術指標、多時間框架分析、數據存儲狀態等功能
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
import asyncio
import logging
from datetime import datetime

from app.services.realtime_technical_analysis import RealTimeTechnicalAnalysis
from app.services.enhanced_data_storage import EnhancedDataStorage
from app.services.market_data import MarketDataService

router = APIRouter()
logger = logging.getLogger(__name__)

# 全局服務實例
enhanced_storage = EnhancedDataStorage()
realtime_analysis = None  # 將在 startup 時初始化

@router.post("/start-realtime-analysis")
async def start_realtime_analysis(
    symbols: List[str] = Query(..., description="交易對列表"),
    timeframes: List[str] = Query(default=["1m", "5m", "15m", "1h"], description="時間框架列表")
):
    """啟動即時技術分析"""
    try:
        global realtime_analysis
        
        if realtime_analysis is None:
            from main import app
            market_service: MarketDataService = app.state.market_service
            realtime_analysis = RealTimeTechnicalAnalysis(market_service)
        
        await realtime_analysis.start_realtime_analysis(symbols, timeframes)
        
        return {
            "success": True,
            "message": "即時技術分析已啟動",
            "symbols": symbols,
            "timeframes": timeframes,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"啟動即時技術分析失敗: {e}")
        raise HTTPException(status_code=500, detail=f"啟動即時技術分析失敗: {str(e)}")

@router.post("/stop-realtime-analysis")
async def stop_realtime_analysis():
    """停止即時技術分析"""
    try:
        global realtime_analysis
        
        if realtime_analysis:
            await realtime_analysis.stop_realtime_analysis()
        
        return {
            "success": True,
            "message": "即時技術分析已停止",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"停止即時技術分析失敗: {e}")
        raise HTTPException(status_code=500, detail=f"停止即時技術分析失敗: {str(e)}")

@router.get("/indicators/{symbol}")
async def get_current_indicators(
    symbol: str,
    timeframe: str = Query(default="1h", description="時間框架")
):
    """獲取當前技術指標"""
    try:
        global realtime_analysis
        
        if realtime_analysis is None:
            raise HTTPException(status_code=503, detail="即時分析服務未啟動")
        
        indicators = await realtime_analysis.get_current_indicators(symbol.upper(), timeframe)
        
        if not indicators:
            raise HTTPException(status_code=404, detail=f"找不到 {symbol} {timeframe} 的指標數據")
        
        # 轉換為可序列化的格式
        serializable_indicators = {}
        for name, indicator in indicators.items():
            serializable_indicators[name] = {
                "indicator_name": indicator.indicator_name,
                "current_value": indicator.current_value,
                "previous_value": indicator.previous_value,
                "signal": indicator.signal,
                "strength": indicator.strength.value,
                "confidence": indicator.confidence,
                "additional_data": indicator.additional_data,
                "timestamp": indicator.timestamp.isoformat()
            }
        
        return {
            "success": True,
            "data": {
                "symbol": symbol.upper(),
                "timeframe": timeframe,
                "indicators": serializable_indicators,
                "indicator_count": len(serializable_indicators)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取技術指標失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取技術指標失敗: {str(e)}")

@router.get("/multi-timeframe-analysis/{symbol}")
async def get_multi_timeframe_analysis(
    symbol: str,
    timeframes: Optional[str] = Query(None, description="時間框架列表，逗號分隔")
):
    """獲取多時間框架分析"""
    try:
        global realtime_analysis
        
        if realtime_analysis is None:
            raise HTTPException(status_code=503, detail="即時分析服務未啟動")
        
        tf_list = None
        if timeframes:
            tf_list = [tf.strip() for tf in timeframes.split(',')]
        
        analysis = await realtime_analysis.get_multi_timeframe_analysis(symbol.upper(), tf_list)
        
        # 轉換為可序列化的格式
        serializable_timeframes = {}
        for tf, data in analysis.timeframes.items():
            serializable_timeframes[tf] = {
                **data,
                "last_update": data["last_update"].isoformat() if data["last_update"] else None
            }
        
        return {
            "success": True,
            "data": {
                "symbol": analysis.symbol,
                "timeframes": serializable_timeframes,
                "overall_signal": analysis.overall_signal,
                "overall_confidence": analysis.overall_confidence,
                "consensus_indicators": analysis.consensus_indicators,
                "divergent_indicators": analysis.divergent_indicators,
                "timestamp": analysis.timestamp.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取多時間框架分析失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取多時間框架分析失敗: {str(e)}")

@router.get("/analysis-status")
async def get_analysis_status():
    """獲取技術分析服務狀態"""
    try:
        global realtime_analysis
        
        if realtime_analysis is None:
            return {
                "success": True,
                "data": {
                    "service_running": False,
                    "message": "即時分析服務未啟動"
                }
            }
        
        status = realtime_analysis.get_analysis_status()
        
        # 轉換時間戳為字符串
        if "last_updates" in status:
            status["last_updates"] = {
                key: timestamp.isoformat() if hasattr(timestamp, 'isoformat') else str(timestamp)
                for key, timestamp in status["last_updates"].items()
            }
        
        return {
            "success": True,
            "data": {
                "service_running": True,
                **status
            }
        }
        
    except Exception as e:
        logger.error(f"獲取分析狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取分析狀態失敗: {str(e)}")

@router.get("/storage-stats")
async def get_storage_statistics():
    """獲取數據存儲統計信息"""
    try:
        global enhanced_storage
        
        stats = await enhanced_storage.get_storage_statistics()
        
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取存儲統計失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取存儲統計失敗: {str(e)}")

@router.post("/validate-and-store-data")
async def validate_and_store_data(
    data: List[Dict[str, Any]],
    validate: bool = Query(default=True, description="是否啟用數據驗證")
):
    """驗證並存儲市場數據"""
    try:
        global enhanced_storage
        
        storage_stats = await enhanced_storage.store_market_data_batch(data, validate)
        
        return {
            "success": True,
            "data": {
                "total_records": storage_stats.total_records,
                "new_records": storage_stats.new_records,
                "duplicate_records": storage_stats.duplicate_records,
                "invalid_records": storage_stats.invalid_records,
                "storage_time": storage_stats.storage_time
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"數據驗證存儲失敗: {e}")
        raise HTTPException(status_code=500, detail=f"數據驗證存儲失敗: {str(e)}")

@router.get("/signal-summary/{symbol}")
async def get_signal_summary(
    symbol: str,
    timeframe: str = Query(default="1h", description="時間框架")
):
    """獲取信號摘要"""
    try:
        global realtime_analysis
        
        if realtime_analysis is None:
            raise HTTPException(status_code=503, detail="即時分析服務未啟動")
        
        indicators = await realtime_analysis.get_current_indicators(symbol.upper(), timeframe)
        
        if not indicators:
            raise HTTPException(status_code=404, detail=f"找不到 {symbol} {timeframe} 的指標數據")
        
        # 統計信號
        signal_counts = {"buy": 0, "sell": 0, "hold": 0}
        strong_signals = []
        total_confidence = 0
        
        for name, indicator in indicators.items():
            signal_counts[indicator.signal] += 1
            total_confidence += indicator.confidence
            
            if indicator.strength.value in ["strong", "very_strong"]:
                strong_signals.append({
                    "indicator": name,
                    "signal": indicator.signal,
                    "strength": indicator.strength.value,
                    "confidence": indicator.confidence
                })
        
        avg_confidence = total_confidence / len(indicators) if indicators else 0
        dominant_signal = max(signal_counts, key=signal_counts.get)
        
        return {
            "success": True,
            "data": {
                "symbol": symbol.upper(),
                "timeframe": timeframe,
                "signal_summary": {
                    "dominant_signal": dominant_signal,
                    "signal_counts": signal_counts,
                    "average_confidence": round(avg_confidence, 3),
                    "strong_signals": strong_signals,
                    "total_indicators": len(indicators)
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取信號摘要失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取信號摘要失敗: {str(e)}")

@router.get("/websocket-health")
async def get_websocket_health():
    """獲取 WebSocket 連接健康狀態"""
    try:
        from main import app
        market_service: MarketDataService = app.state.market_service
        
        # 檢查 WebSocket 服務狀態
        if hasattr(market_service, 'binance_collector') and market_service.binance_collector:
            connection_status = market_service.binance_collector.get_connection_status()
            
            return {
                "success": True,
                "data": {
                    "websocket_service": "active",
                    **connection_status
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": True,
                "data": {
                    "websocket_service": "inactive",
                    "message": "WebSocket 數據收集器未啟動"
                },
                "timestamp": datetime.now().isoformat()
            }
        
    except Exception as e:
        logger.error(f"獲取 WebSocket 健康狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取 WebSocket 健康狀態失敗: {str(e)}")

# 背景任務：定期數據清理和健康檢查
async def background_maintenance():
    """背景維護任務"""
    while True:
        try:
            # 每小時執行一次維護
            await asyncio.sleep(3600)
            
            # 清理過期快取
            if realtime_analysis:
                # 清理超過1小時的快取
                current_time = datetime.now()
                expired_keys = []
                
                for key, data in realtime_analysis.indicator_cache.items():
                    if 'timestamp' in data:
                        age = (current_time - data['timestamp']).total_seconds()
                        if age > 3600:  # 1小時
                            expired_keys.append(key)
                
                for key in expired_keys:
                    del realtime_analysis.indicator_cache[key]
                
                if expired_keys:
                    logger.info(f"清理了 {len(expired_keys)} 個過期快取")
            
            # 數據庫清理
            if enhanced_storage.auto_cleanup:
                await enhanced_storage._cleanup_old_data()
            
        except Exception as e:
            logger.error(f"背景維護任務錯誤: {e}")

# 啟動背景任務
def start_background_tasks():
    """啟動背景任務"""
    asyncio.create_task(background_maintenance())
