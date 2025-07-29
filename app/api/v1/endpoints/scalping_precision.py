"""
短線交易API端點 - 精準篩選版本
實現：零備選模式，每個幣種只保留最精準的單一信號
整合 market_conditions_config.json 配置，多策略競爭篩選
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import asyncio
import os

# 導入服務
from app.services.market_data import MarketDataService
from app.services.precision_signal_filter import precision_filter, PrecisionSignal
from app.core.database import AsyncSessionLocal
from app.utils.time_utils import get_taiwan_now_naive
import pytz

# SQLite 相關
import sqlite3
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker

router = APIRouter()
logger = logging.getLogger(__name__)

# 台灣時區設定
TAIWAN_TZ = pytz.timezone('Asia/Taipei')

# 數據庫配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///tradingx.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 初始化服務
market_service = MarketDataService()

def get_taiwan_now():
    """獲取台灣當前時間"""
    return datetime.now(TAIWAN_TZ)

def taiwan_to_naive(dt):
    """將台灣時區的時間轉換為naive datetime"""
    if dt.tzinfo is None:
        return dt
    taiwan_dt = dt.astimezone(TAIWAN_TZ)
    return taiwan_dt.replace(tzinfo=None)

def parse_time_to_taiwan(time_str):
    """解析時間字符串並轉換為台灣時間的naive datetime"""
    if isinstance(time_str, str):
        try:
            if 'Z' in time_str or '+' in time_str or '-' in time_str.split('T')[-1]:
                time_str_clean = time_str.replace('Z', '+00:00')
                dt = datetime.fromisoformat(time_str_clean)
                return taiwan_to_naive(dt)
            else:
                return datetime.fromisoformat(time_str)
        except:
            return datetime.now()
    return time_str

# ==================== 主要端點 ====================

@router.get("/prices")
async def get_current_prices(symbols: List[str] = None):
    """獲取當前價格數據"""
    try:
        if not symbols:
            symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT"]
        
        prices = {}
        
        for symbol in symbols:
            try:
                # 獲取最新價格數據
                data = await market_service.get_historical_data(
                    symbol=symbol,
                    timeframe="1m",
                    limit=1,
                    exchange='binance'
                )
                
                if data is not None and len(data) > 0:
                    latest = data.iloc[-1]
                    prices[symbol] = {
                        "symbol": symbol,
                        "price": float(latest['close']),
                        "change_24h": 0.0,  # 暫時設為0，可以後續優化
                        "change_percent": 0.0,
                        "volume": float(latest['volume']),
                        "timestamp": latest.name.isoformat() if hasattr(latest.name, 'isoformat') else get_taiwan_now().isoformat()
                    }
                else:
                    # 如果無法獲取數據，提供默認值
                    prices[symbol] = {
                        "symbol": symbol,
                        "price": 0.0,
                        "change_24h": 0.0,
                        "change_percent": 0.0,
                        "volume": 0.0,
                        "timestamp": get_taiwan_now().isoformat()
                    }
                    
            except Exception as e:
                logger.error(f"獲取 {symbol} 價格失敗: {e}")
                prices[symbol] = {
                    "symbol": symbol,
                    "price": 0.0,
                    "change_24h": 0.0,
                    "change_percent": 0.0,
                    "volume": 0.0,
                    "timestamp": get_taiwan_now().isoformat(),
                    "error": str(e)
                }
        
        return {
            "prices": prices,
            "updated_at": get_taiwan_now().isoformat(),
            "data_source": "binance",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"獲取價格數據失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取價格數據失敗: {str(e)}")

@router.get("/signals")
async def get_scalping_signals():
    """
    獲取短線交易信號 (精準篩選版本)
    
    核心邏輯：
    1. 使用精準篩選器為每個幣種生成最優信號
    2. 備選信號直接銷毀，只保留最精準的信號
    3. 基於 market_conditions_config 的多維度評分
    4. 確保每個幣種同時只有一個最精準信號
    """
    try:
        # 目標交易幣種
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT"]
        
        # 先處理過期信號
        await _auto_process_expired_signals()
        
        # 獲取當前活躍信號
        current_signals = await _get_active_signals_from_db()
        signal_map = {signal['symbol']: signal for signal in current_signals}
        
        all_signals = []
        
        # 為每個幣種處理信號
        for symbol in symbols:
            try:
                existing_signal = signal_map.get(symbol)
                
                if existing_signal:
                    # 有活躍信號，檢查是否仍然有效
                    taiwan_now = get_taiwan_now().replace(tzinfo=None)
                    expires_at = parse_time_to_taiwan(existing_signal['expires_at'])
                    
                    if expires_at > taiwan_now:
                        # 信號仍然有效，計算剩餘時間
                        remaining_seconds = (expires_at - taiwan_now).total_seconds()
                        remaining_minutes = remaining_seconds / 60
                        
                        # 檢查是否為精準信號
                        is_precision_signal = existing_signal.get('is_precision_selected', 0) == 1
                        precision_score = existing_signal.get('precision_score', 0.0)
                        
                        # 構建響應信號
                        signal = {
                            'id': existing_signal['id'],
                            'symbol': existing_signal['symbol'],
                            'timeframe': existing_signal.get('timeframe', '5m'),
                            'primary_timeframe': existing_signal.get('timeframe', '5m'),
                            'signal_type': existing_signal['signal_type'],
                            'strategy_name': existing_signal.get('strategy_name', '精準篩選'),
                            'entry_price': existing_signal.get('entry_price', 0),
                            'stop_loss': existing_signal.get('stop_loss', 0),
                            'take_profit': existing_signal.get('take_profit', 0),
                            'confidence': existing_signal.get('confidence', 0),
                            'precision_score': precision_score,
                            'urgency_level': 'high',
                            'risk_reward_ratio': existing_signal.get('risk_reward_ratio', 0),
                            'created_at': existing_signal['created_at'],
                            'expires_at': existing_signal['expires_at'],
                            'reasoning': f"精準篩選 - {existing_signal.get('strategy_name', '未知策略')} (評分: {precision_score:.3f})",
                            'status': 'active',
                            'is_scalping': True,
                            'is_precision_verified': is_precision_signal,
                            'remaining_time_minutes': remaining_minutes,
                            'validity_info': _calculate_signal_validity(
                                existing_signal.get('timeframe', '5m'), 
                                parse_time_to_taiwan(existing_signal['created_at'])
                            )
                        }
                        
                        all_signals.append(signal)
                        logger.info(f"✅ 返回現有精準信號 {symbol}: {remaining_minutes:.1f}分鐘剩餘 (精準度: {precision_score:.3f})")
                        continue
                
                # 沒有活躍信號或已過期，使用精準篩選生成新信號
                logger.info(f"🎯 為 {symbol} 執行精準篩選...")
                
                # 使用精準篩選器
                precision_signal = await precision_filter.execute_precision_selection(symbol)
                
                if precision_signal:
                    # 保存精準信號到數據庫（移除舊信號清理，讓信號自然過期）
                    await _save_precision_signal_to_db(precision_signal)
                    
                    # 轉換為 API 響應格式
                    signal = {
                        'id': f"precision_{symbol}_{int(precision_signal.created_at.timestamp())}",
                        'symbol': precision_signal.symbol,
                        'timeframe': precision_signal.timeframe,
                        'primary_timeframe': precision_signal.timeframe,
                        'signal_type': precision_signal.signal_type,
                        'strategy_name': precision_signal.strategy_name,
                        'entry_price': precision_signal.entry_price,
                        'stop_loss': precision_signal.stop_loss,
                        'take_profit': precision_signal.take_profit,
                        'confidence': precision_signal.confidence,
                        'precision_score': precision_signal.precision_score,
                        'urgency_level': 'high',
                        'risk_reward_ratio': abs(precision_signal.take_profit - precision_signal.entry_price) / abs(precision_signal.entry_price - precision_signal.stop_loss) if abs(precision_signal.entry_price - precision_signal.stop_loss) > 0 else 0,
                        'created_at': precision_signal.created_at.isoformat(),
                        'expires_at': precision_signal.expires_at.isoformat(),
                        'reasoning': f"精準篩選 - {precision_signal.strategy_name} (評分: {precision_signal.precision_score:.3f})",
                        'status': 'active',
                        'is_scalping': True,
                        'is_precision_verified': True,
                        'market_condition_score': precision_signal.market_condition_score,
                        'indicator_consistency': precision_signal.indicator_consistency,
                        'timing_score': precision_signal.timing_score,
                        'remaining_time_minutes': (precision_signal.expires_at - get_taiwan_now().replace(tzinfo=None)).total_seconds() / 60,
                        'validity_info': _calculate_signal_validity(
                            precision_signal.timeframe, precision_signal.created_at
                        )
                    }
                    
                    all_signals.append(signal)
                    logger.info(f"🎯 生成精準信號 {symbol}: {precision_signal.strategy_name} (評分: {precision_signal.precision_score:.3f})")
                    
                else:
                    # 未能生成精準信號
                    logger.info(f"⚠️ {symbol} 當前市場條件不符合精準篩選標準")
                    
            except Exception as e:
                logger.error(f"處理 {symbol} 信號時出錯: {str(e)}")
                continue
        
        # 返回結果
        response = {
            "signals": all_signals,
            "count": len(all_signals),
            "precision_mode": True,
            "updated_at": get_taiwan_now().isoformat(),
            "next_update": (get_taiwan_now() + timedelta(minutes=15)).isoformat(),
            "market_conditions": "精準篩選模式 - 只顯示最優信號"
        }
        
        logger.info(f"📊 精準篩選完成: 返回 {len(all_signals)} 個精準信號")
        return response
        
    except Exception as e:
        logger.error(f"獲取精準信號失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取精準信號失敗: {str(e)}")

@router.get("/precision-signal/{symbol}")
async def get_precision_signal(symbol: str):
    """獲取指定交易對的精準信號"""
    
    try:
        # 執行精準篩選
        precision_signal = await precision_filter.execute_precision_selection(symbol)
        
        if not precision_signal:
            return {
                "status": "no_signal",
                "message": f"{symbol} 當前市場條件不符合精準篩選標準",
                "next_check": (get_taiwan_now() + timedelta(minutes=15)).isoformat()
            }
        
        # 保存精準信號（移除舊信號清理，讓信號自然過期）
        await _save_precision_signal_to_db(precision_signal)
        
        return {
            "status": "success",
            "signal": precision_signal.dict(),
            "precision_metadata": {
                "precision_score": precision_signal.precision_score,
                "market_conditions": "optimal",
                "strategy_count_evaluated": 4,
                "selection_timestamp": get_taiwan_now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"獲取精準信號失敗: {e}")
        return {"status": "error", "message": str(e)}

@router.get("/dashboard-precision-signals")
async def get_dashboard_precision_signals():
    """為儀表板提供精準篩選的信號 (每幣種最多一個)"""
    
    target_symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'XRPUSDT', 'BNBUSDT']
    precision_signals = []
    
    # 並行獲取各幣種的精準信號
    tasks = [
        precision_filter.execute_precision_selection(symbol) 
        for symbol in target_symbols
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for symbol, result in zip(target_symbols, results):
        if isinstance(result, PrecisionSignal):
            precision_signals.append({
                "symbol": symbol,
                "signal": result.dict(),
                "precision_score": result.precision_score,
                "is_precision_verified": True
            })
        elif isinstance(result, Exception):
            logger.error(f"獲取 {symbol} 精準信號失敗: {result}")
    
    return {
        "signals": precision_signals,
        "total_evaluated_symbols": len(target_symbols),
        "precision_signals_found": len(precision_signals),
        "updated_at": get_taiwan_now().isoformat(),
        "next_update": (get_taiwan_now() + timedelta(minutes=15)).isoformat()
    }

# ==================== 輔助函數 ====================

async def _auto_process_expired_signals():
    """自動處理過期信號"""
    try:
        db = SessionLocal()
        taiwan_now = get_taiwan_now().replace(tzinfo=None)
        
        # 查詢過期信號
        expired_query = text("""
            SELECT id, symbol, entry_price, signal_type, confidence
            FROM trading_signals 
            WHERE datetime(expires_at) <= datetime(:taiwan_now)
            AND (status IS NULL OR status != 'expired')
        """)
        
        expired_result = db.execute(expired_query, {"taiwan_now": taiwan_now.isoformat()})
        expired_signals = list(expired_result)
        
        for signal_row in expired_signals:
            signal_id = signal_row.id
            symbol = signal_row.symbol
            
            try:
                # 更新信號狀態為過期
                update_query = text("""
                    UPDATE trading_signals 
                    SET status = 'expired', archived_at = :archived_at
                    WHERE id = :signal_id
                """)
                
                db.execute(update_query, {
                    "signal_id": signal_id,
                    "archived_at": taiwan_now.isoformat()
                })
                
            except Exception as e:
                logger.error(f"處理過期信號 {signal_id} 失敗: {e}")
        
        db.commit()
        db.close()
        
        if expired_signals:
            logger.info(f"✅ 處理了 {len(expired_signals)} 個過期信號")
        
    except Exception as e:
        logger.error(f"自動處理過期信號失敗: {e}")

async def _get_active_signals_from_db() -> List[dict]:
    """從數據庫獲取活躍信號"""
    try:
        db = SessionLocal()
        
        query = text("""
            SELECT * FROM trading_signals 
            WHERE (status IS NULL OR status = 'active')
            ORDER BY created_at DESC
        """)
        
        result = db.execute(query)
        signals = []
        
        for row in result:
            signal_dict = dict(row._mapping)
            signals.append(signal_dict)
        
        db.close()
        return signals
        
    except Exception as e:
        logger.error(f"獲取活躍信號失敗: {e}")
        return []

async def _cleanup_old_signals_for_symbol(symbol: str):
    """
    🚫 已棄用：不再清理同交易對的舊信號
    
    原因：這會破壞歷史信號保存機制
    新機制：讓信號自然過期，保存7天後再清理
    """
    logger.warning(f"⚠️  _cleanup_old_signals_for_symbol() 已棄用，信號將自然過期")
    pass

async def _cleanup_signals_older_than_7_days():
    """清理7天前的過期信號 - 真正的清理機制"""
    try:
        db = SessionLocal()
        seven_days_ago = get_taiwan_now().replace(tzinfo=None) - timedelta(days=7)
        
        # 刪除7天前的過期信號
        delete_query = text("""
            DELETE FROM trading_signals 
            WHERE status IN ('expired', 'replaced', 'archived') 
            AND (archived_at IS NOT NULL AND datetime(archived_at) <= datetime(:seven_days_ago))
            OR (expires_at IS NOT NULL AND datetime(expires_at) <= datetime(:seven_days_ago))
        """)
        
        result = db.execute(delete_query, {"seven_days_ago": seven_days_ago.isoformat()})
        deleted_count = result.rowcount
        
        db.commit()
        db.close()
        
        if deleted_count > 0:
            logger.info(f"✅ 清理了 {deleted_count} 個7天前的過期信號")
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"清理7天前信號失敗: {e}")
        return 0

async def _save_precision_signal_to_db(signal: PrecisionSignal):
    """保存精準信號到數據庫"""
    try:
        db = SessionLocal()
        
        # 計算風險回報比
        risk = abs(signal.entry_price - signal.stop_loss) / signal.entry_price if signal.entry_price > 0 else 0
        reward = abs(signal.take_profit - signal.entry_price) / signal.entry_price if signal.entry_price > 0 else 0
        risk_reward_ratio = reward / risk if risk > 0 else 0
        
        insert_query = text("""
            INSERT INTO trading_signals (
                symbol, timeframe, signal_type, confidence, precision_score,
                entry_price, stop_loss, take_profit, strategy_name,
                status, is_scalping, is_precision_selected,
                market_condition_score, indicator_consistency, timing_score, risk_adjustment,
                created_at, expires_at, reasoning, urgency_level, risk_reward_ratio
            ) VALUES (
                :symbol, :timeframe, :signal_type, :confidence, :precision_score,
                :entry_price, :stop_loss, :take_profit, :strategy_name,
                'active', 1, 1,
                :market_condition_score, :indicator_consistency, :timing_score, :risk_adjustment,
                :created_at, :expires_at, :reasoning, 'high', :risk_reward_ratio
            )
        """)
        
        db.execute(insert_query, {
            "symbol": signal.symbol,
            "timeframe": signal.timeframe,
            "signal_type": signal.signal_type,
            "confidence": signal.confidence,
            "precision_score": signal.precision_score,
            "entry_price": signal.entry_price,
            "stop_loss": signal.stop_loss,
            "take_profit": signal.take_profit,
            "strategy_name": signal.strategy_name,
            "market_condition_score": signal.market_condition_score,
            "indicator_consistency": signal.indicator_consistency,
            "timing_score": signal.timing_score,
            "risk_adjustment": signal.risk_adjustment,
            "created_at": signal.created_at.isoformat(),
            "expires_at": signal.expires_at.isoformat(),
            "reasoning": f"精準篩選 - {signal.strategy_name} (評分: {signal.precision_score:.3f})",
            "risk_reward_ratio": risk_reward_ratio
        })
        
        db.commit()
        db.close()
        
        logger.info(f"✅ 精準信號已保存: {signal.symbol} - {signal.strategy_name}")
        
    except Exception as e:
        logger.error(f"保存精準信號失敗: {e}")
        raise e

def _calculate_signal_validity(timeframe: str, created_time: datetime) -> dict:
    """計算信號時效性"""
    try:
        now = get_taiwan_now().replace(tzinfo=None)
        
        if isinstance(created_time, str):
            created_time = parse_time_to_taiwan(created_time)
        
        # 根據時間框架確定有效期
        validity_hours = {
            "1m": 1,
            "3m": 2,
            "5m": 4,
            "15m": 8,
            "30m": 12,
            "1h": 24
        }.get(timeframe, 4)
        
        total_seconds = validity_hours * 3600
        elapsed_seconds = (now - created_time).total_seconds()
        remaining_seconds = max(0, total_seconds - elapsed_seconds)
        remaining_minutes = remaining_seconds / 60
        
        percentage = (remaining_seconds / total_seconds) * 100 if total_seconds > 0 else 0
        
        if percentage > 70:
            status, color = "excellent", "green"
        elif percentage > 40:
            status, color = "good", "yellow"
        elif percentage > 0:
            status, color = "expiring", "orange"
        else:
            status, color = "expired", "red"
        
        return {
            "percentage": round(percentage, 2),
            "remaining_minutes": round(remaining_minutes, 2),
            "remaining_seconds": round(remaining_seconds),
            "status": status,
            "text": f"{remaining_minutes:.1f}分鐘" if remaining_minutes > 0 else "已過期",
            "color": color,
            "can_execute": remaining_minutes > 0
        }
        
    except Exception as e:
        logger.error(f"計算信號時效性失敗: {e}")
        return {
            "percentage": 0,
            "remaining_minutes": 0,
            "remaining_seconds": 0,
            "status": "error",
            "text": "計算錯誤",
            "color": "red",
            "can_execute": False
        }

# ==================== 統計端點 ====================

@router.get("/precision-signal-stats")
async def get_precision_signal_stats():
    """獲取精準信號統計"""
    try:
        db = SessionLocal()
        
        stats_query = text("""
            SELECT 
                COUNT(*) as total_precision,
                AVG(precision_score) as avg_precision,
                COUNT(CASE WHEN trade_result = 'success' THEN 1 END) as success_count,
                COUNT(CASE WHEN trade_result = 'failure' THEN 1 END) as failure_count,
                COUNT(CASE WHEN trade_result = 'breakeven' THEN 1 END) as breakeven_count
            FROM trading_signals 
            WHERE is_precision_selected = 1
        """)
        
        result = db.execute(stats_query)
        stats = result.fetchone()
        
        if stats and stats.total_precision > 0:
            success_rate = (stats.success_count / stats.total_precision * 100) if stats.total_precision > 0 else 0
            
            response = {
                "precision_signal_stats": {
                    "total_precision_signals": stats.total_precision,
                    "average_precision_score": round(stats.avg_precision or 0, 3),
                    "success_rate": round(success_rate, 2),
                    "success_count": stats.success_count,
                    "failure_count": stats.failure_count,
                    "breakeven_count": stats.breakeven_count,
                    "quality_grade": "A" if success_rate > 80 else "B" if success_rate > 60 else "C"
                },
                "updated_at": get_taiwan_now().isoformat()
            }
        else:
            response = {
                "precision_signal_stats": {
                    "total_precision_signals": 0,
                    "average_precision_score": 0,
                    "success_rate": 0,
                    "quality_grade": "未評級"
                },
                "updated_at": get_taiwan_now().isoformat()
            }
        
        db.close()
        return response
        
    except Exception as e:
        logger.error(f"獲取精準信號統計失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取統計失敗: {str(e)}")

@router.post("/force-precision-refresh/{symbol}")
async def force_precision_refresh(symbol: str):
    """強制刷新指定交易對的精準信號"""
    try:
        # 移除舊信號清理，讓信號自然過期
        precision_signal = await precision_filter.execute_precision_selection(symbol)
        
        if precision_signal:
            await _save_precision_signal_to_db(precision_signal)
            return {
                "status": "success",
                "message": f"已為 {symbol} 生成新的精準信號",
                "signal": precision_signal.dict(),
                "precision_score": precision_signal.precision_score
            }
        else:
            return {
                "status": "no_signal",
                "message": f"{symbol} 當前市場條件不符合精準篩選標準"
            }
            
    except Exception as e:
        logger.error(f"強制刷新精準信號失敗: {e}")
        return {"status": "error", "message": str(e)}

# ==================== 過期信號處理 ====================

@router.post("/process-expired")
async def process_expired_signals():
    """手動處理過期信號"""
    try:
        await _auto_process_expired_signals()
        return {"status": "success", "message": "過期信號處理完成"}
    except Exception as e:
        logger.error(f"處理過期信號失敗: {e}")
        raise HTTPException(status_code=500, detail=f"處理失敗: {str(e)}")

@router.post("/cleanup-expired")
async def cleanup_expired_signals():
    """手動清理7天前的過期信號"""
    try:
        deleted_count = await _cleanup_signals_older_than_7_days()
        
        return {
            "status": "success",
            "message": f"清理完成，共刪除 {deleted_count} 個過期信號",
            "deleted_count": deleted_count,
            "cleanup_date": get_taiwan_now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"手動清理過期信號失敗: {e}")
        raise HTTPException(status_code=500, detail=f"清理失敗: {str(e)}")

@router.get("/expired")
async def get_expired_signals():
    """獲取過期信號列表"""
    try:
        db = SessionLocal()
        
        query = text("""
            SELECT * FROM trading_signals 
            WHERE status = 'expired'
            ORDER BY created_at DESC
            LIMIT 100
        """)
        
        result = db.execute(query)
        expired_signals = []
        
        for row in result:
            signal_dict = dict(row._mapping)
            signal_dict['primary_timeframe'] = signal_dict.get('timeframe', '5m')
            signal_dict['is_scalping'] = True
            signal_dict['urgency_level'] = signal_dict.get('urgency_level', 'medium')
            signal_dict['strategy_name'] = signal_dict.get('strategy_name', '技術分析')
            signal_dict['reasoning'] = signal_dict.get('reasoning', '短線交易策略')
            expired_signals.append(signal_dict)
        
        db.close()
        
        logger.info(f"返回 {len(expired_signals)} 個過期短線信號")
        return expired_signals
        
    except Exception as e:
        logger.error(f"獲取過期短線信號失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取過期短線信號失敗: {str(e)}")
