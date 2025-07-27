"""
短線交易API端點 - 核心業務邏輯版本
實現：每個幣種同時只有一個活躍信號，過期後才生成新信號
整合 market_conditions_config.json 配置
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
import random
import logging
from app.services.market_data import MarketDataService
from app.services.scalping_strategy import ScalpingStrategyEngine, ScalpingSignal  # 添加ScalpingSignal
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
import os
import pytz

router = APIRouter()
logger = logging.getLogger(__name__)

# 台灣時區設定
TAIWAN_TZ = pytz.timezone('Asia/Taipei')

# 初始化服務
market_service = MarketDataService()
scalping_engine = ScalpingStrategyEngine()  # 使用新的策略引擎

# 台灣時區設定
TAIWAN_TZ = pytz.timezone('Asia/Taipei')

def get_taiwan_now():
    """獲取台灣當前時間"""
    return datetime.now(TAIWAN_TZ)

def taiwan_to_naive(dt):
    """將台灣時區的時間轉換為naive datetime（移除時區信息但保持台灣時間）"""
    if dt.tzinfo is None:
        return dt
    taiwan_dt = dt.astimezone(TAIWAN_TZ)
    return taiwan_dt.replace(tzinfo=None)

def parse_time_to_taiwan(time_str):
    """解析時間字符串並轉換為台灣時間的naive datetime"""
    if isinstance(time_str, str):
        try:
            # 如果字符串包含時區信息
            if 'Z' in time_str or '+' in time_str or '-' in time_str.split('T')[-1]:
                time_str_clean = time_str.replace('Z', '+00:00')
                dt = datetime.fromisoformat(time_str_clean)
                return taiwan_to_naive(dt)
            else:
                # 沒有時區信息，假設已經是台灣時間
                dt = datetime.fromisoformat(time_str)
                return dt
        except:
            # 如果解析失敗，返回當前台灣時間減去5分鐘
            return get_taiwan_now().replace(tzinfo=None) - timedelta(minutes=5)
    return time_str

# 資料庫連接
DATABASE_URL = "sqlite:///./tradingx.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 全域市場數據服務
market_service = MarketDataService()

@router.get("/signals")
async def get_scalping_signals():
    """
    獲取短線交易信號 (核心業務邏輯版本)
    
    核心邏輯：
    1. 檢查數據庫中每個幣種的活躍信號
    2. 如果信號未過期，返回並更新剩餘時間
    3. 如果信號已過期或不存在，生成新信號
    4. 確保每個幣種同時只有一個活躍信號
    """
    try:
        # 目標交易幣種
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT"]
        timeframes = ["5m"]  # 專注於5分鐘短線
        
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
                    # 有活躍信號，計算剩餘時間並返回
                    taiwan_now = get_taiwan_now().replace(tzinfo=None)
                    expires_at = parse_time_to_taiwan(existing_signal['expires_at'])
                    
                    if expires_at > taiwan_now:
                        # 信號仍然有效，計算剩餘時間
                        remaining_seconds = (expires_at - taiwan_now).total_seconds()
                        remaining_minutes = remaining_seconds / 60
                        
                        # 更新時效性信息
                        validity_info = _calculate_signal_validity(
                            existing_signal['timeframe'], 
                            parse_time_to_taiwan(existing_signal['created_at'])
                        )
                        
                        signal = {
                            'id': existing_signal['id'],
                            'symbol': existing_signal['symbol'],
                            'timeframe': existing_signal['timeframe'],
                            'primary_timeframe': existing_signal['timeframe'],
                            'signal_type': existing_signal['signal_type'],
                            'strategy_name': existing_signal['strategy_name'],
                            'entry_price': existing_signal['entry_price'],
                            'stop_loss': existing_signal['stop_loss'],
                            'take_profit': existing_signal['take_profit'],
                            'confidence': existing_signal['confidence'],
                            'urgency_level': existing_signal['urgency_level'],
                            'risk_reward_ratio': existing_signal['risk_reward_ratio'],
                            'created_at': existing_signal['created_at'],
                            'expires_at': existing_signal['expires_at'],
                            'indicators_used': existing_signal['indicators_used'],
                            'key_indicators': existing_signal['key_indicators'] if existing_signal['key_indicators'] else {},
                            'reasoning': existing_signal['reasoning'],
                            'status': 'active',
                            'is_scalping': True,
                            'current_price': existing_signal['entry_price'],  # 可以更新為最新價格
                            'signal_strength': existing_signal['confidence'],
                            'remaining_time_minutes': remaining_minutes,
                            'updated_at': existing_signal['created_at'],
                            'validity_info': validity_info
                        }
                        
                        all_signals.append(signal)
                        logger.info(f"✅ 返回現有信號 {symbol}: {remaining_minutes:.1f}分鐘剩餘")
                        continue
                
                # 沒有活躍信號或已過期，生成新信號
                logger.info(f"🔥 為 {symbol} 生成新信號（沒有活躍信號）")
                
                # 獲取真實價格
                current_price = await market_service.get_latest_price(symbol, "binance")
                if current_price is None:
                    logger.warning(f"無法獲取 {symbol} 的真實價格，跳過")
                    continue
                
                # 為5分鐘時間框架生成新信號
                for timeframe in timeframes:
                    try:
                        # 使用策略引擎生成信號
                        engine_signals = await scalping_engine.generate_scalping_signals(
                            symbol, [timeframe], real_price=current_price
                        )
                        
                        if engine_signals:
                            # 取最佳信號
                            engine_signal = engine_signals[0]
                            
                            # 保存到數據庫
                            await _save_signal_to_db(engine_signal, current_price)
                            
                            # 轉換為 API 響應格式
                            signal = {
                                'id': f"{symbol}_{timeframe}_{int(taiwan_to_naive(get_taiwan_now()).timestamp())}",
                                'symbol': engine_signal.symbol,
                                'timeframe': engine_signal.timeframe,
                                'primary_timeframe': engine_signal.timeframe,
                                'signal_type': engine_signal.signal_type.value,
                                'strategy_name': engine_signal.strategy_name,
                                'entry_price': engine_signal.entry_price,
                                'stop_loss': engine_signal.stop_loss,
                                'take_profit': engine_signal.take_profit,
                                'confidence': engine_signal.confidence,
                                'urgency_level': engine_signal.urgency_level,
                                'risk_reward_ratio': engine_signal.risk_reward_ratio,
                                'created_at': engine_signal.created_at.isoformat(),
                                'expires_at': (engine_signal.created_at + timedelta(minutes=engine_signal.expires_in_minutes)).isoformat(),
                                'indicators_used': str(engine_signal.indicators),
                                'key_indicators': engine_signal.indicators,
                                'reasoning': f"{engine_signal.strategy_name} ({engine_signal.urgency_level}) - 基於真實市場價格 (${current_price:.4f}) 和智能時間計算",
                                'status': 'active',
                                'is_scalping': True,
                                'current_price': current_price,
                                'signal_strength': engine_signal.confidence,
                                'smart_timing': engine_signal.timing_details  # 添加智能時間計算詳情
                            }
                            
                            # 計算時效性信息
                            validity_info = _calculate_signal_validity(
                                timeframe, engine_signal.created_at
                            )
                            signal['validity_info'] = validity_info
                            signal['remaining_validity_hours'] = round(validity_info['remaining_minutes'] / 60, 2)
                            signal['remaining_time_minutes'] = validity_info['remaining_minutes']
                            signal['updated_at'] = engine_signal.created_at.isoformat()
                            
                            all_signals.append(signal)
                            logger.info(f"✅ 生成新信號 {symbol}-{timeframe}: {engine_signal.strategy_name} (置信度: {engine_signal.confidence:.2f})")
                            
                            # 只取每個幣種的第一個好信號
                            break
                            
                    except Exception as e:
                        logger.error(f"為 {symbol}-{timeframe} 生成信號失敗: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"為 {symbol} 處理信號失敗: {e}")
                continue
        
        logger.info(f"🚀 返回 {len(all_signals)} 個短線交易信號")
        return all_signals
        
    except Exception as e:
        logger.error(f"獲取短線信號失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取短線信號失敗: {str(e)}")

async def _auto_process_expired_signals():
    """自動處理過期信號（內部函數）- 獲取真實市場價格"""
    try:
        db = SessionLocal()
        
        # 使用台灣時區進行過期判斷
        taiwan_now = get_taiwan_now().replace(tzinfo=None)
        
        # 🔥 首先查詢即將過期但尚未處理的信號
        expired_signals_query = text("""
            SELECT id, symbol, entry_price, signal_type, confidence
            FROM trading_signals 
            WHERE datetime(expires_at) <= datetime(:taiwan_now)
            AND (status IS NULL OR status != 'expired')
        """)
        
        expired_signals_result = db.execute(expired_signals_query, {"taiwan_now": taiwan_now.isoformat()})
        expired_signals = list(expired_signals_result)
        
        # 🔥 為每個過期信號獲取真實的當前市場價格
        for signal_row in expired_signals:
            signal_id = signal_row.id
            symbol = signal_row.symbol
            entry_price = signal_row.entry_price
            signal_type = signal_row.signal_type  # 修改為使用 signal_type
            confidence = signal_row.confidence
            
            try:
                # 獲取真實的當前市場價格
                current_price = await market_service.get_latest_price(symbol, "binance")
                
                if current_price and entry_price:
                    # 計算真實的盈虧百分比
                    is_long = not (signal_type and ('SHORT' in signal_type.upper() or 'DOWN' in signal_type.upper()))
                    price_change = current_price - entry_price
                    profit_percent = (price_change / entry_price) * 100 if is_long else -(price_change / entry_price) * 100
                    
                    # 判斷交易結果
                    if profit_percent > 0.5:
                        trade_result = 'success'
                    elif profit_percent < 0:
                        trade_result = 'failure'
                    else:
                        trade_result = 'breakeven'
                    
                    # 更新信號：設置狀態為過期，並保存真實價格和交易結果
                    update_with_price_query = text("""
                        UPDATE trading_signals 
                        SET status = 'expired', 
                            current_price = :current_price,
                            profit_loss_pct = :profit_loss_pct,
                            trade_result = :trade_result,
                            archived_at = :archived_at
                        WHERE id = :signal_id
                    """)
                    
                    db.execute(update_with_price_query, {
                        "signal_id": signal_id,
                        "current_price": current_price,
                        "profit_loss_pct": profit_percent,
                        "trade_result": trade_result,
                        "archived_at": taiwan_now.isoformat()
                    })
                    
                    logger.info(f"✅ {symbol} 過期信號處理完成: 進場=${entry_price:.4f}, 出場=${current_price:.4f}, 盈虧={profit_percent:.2f}%, 結果={trade_result}")
                    
                else:
                    # 如果無法獲取價格，僅標記為過期
                    simple_update_query = text("""
                        UPDATE trading_signals 
                        SET status = 'expired', archived_at = :archived_at
                        WHERE id = :signal_id
                    """)
                    
                    db.execute(simple_update_query, {
                        "signal_id": signal_id,
                        "archived_at": taiwan_now.isoformat()
                    })
                    
                    logger.warning(f"⚠️ {symbol} 無法獲取真實價格，僅標記為過期")
                    
            except Exception as price_error:
                logger.error(f"❌ 處理 {symbol} 過期信號時獲取價格失敗: {price_error}")
                
                # 如果獲取價格失敗，僅標記為過期
                simple_update_query = text("""
                    UPDATE trading_signals 
                    SET status = 'expired', archived_at = :archived_at
                    WHERE id = :signal_id
                """)
                
                db.execute(simple_update_query, {
                    "signal_id": signal_id,
                    "archived_at": taiwan_now.isoformat()
                })
        
        db.commit()
        expired_count = len(expired_signals)
        
        if expired_count > 0:
            logger.info(f"🎯 自動處理 {expired_count} 個過期信號（含真實價格計算）")
        
        db.close()
        
    except Exception as e:
        logger.error(f"自動處理過期信號失敗: {e}")

async def _get_active_signals_from_db() -> List[dict]:
    """從資料庫獲取活躍的信號"""
    try:
        db = SessionLocal()
        
        # 查詢活躍（未過期）的信號，使用台灣時區
        taiwan_now = get_taiwan_now().replace(tzinfo=None)
        query = text("""
            SELECT * FROM trading_signals 
            WHERE datetime(expires_at) > datetime(:taiwan_now)
            AND (status IS NULL OR status != 'expired')
            ORDER BY created_at DESC
        """)
        
        result = db.execute(query, {"taiwan_now": taiwan_now.isoformat()})
        signals = []
        
        for row in result:
            signal_dict = dict(row._mapping)
            
            # 🔥 動態獲取當前真實價格
            try:
                current_price = await market_service.get_latest_price(signal_dict['symbol'], "binance")
                signal_dict['current_price'] = current_price
            except Exception as e:
                logger.warning(f"無法獲取 {signal_dict['symbol']} 的當前價格: {e}")
                signal_dict['current_price'] = None
            
            # 設置預設值以相容前端
            signal_dict['primary_timeframe'] = signal_dict.get('timeframe', '5m')
            signal_dict['is_scalping'] = True
            signal_dict['urgency_level'] = signal_dict.get('urgency_level', 'medium')
            # 保留原始策略名稱（來自新策略引擎的信號）
            signal_dict['strategy_name'] = signal_dict.get('strategy_name', '技術分析')
            signal_dict['reasoning'] = signal_dict.get('reasoning', '短線交易策略')
            
            # 解析 indicators_used JSON 字段作為 key_indicators
            if signal_dict.get('indicators_used'):
                try:
                    if isinstance(signal_dict['indicators_used'], str):
                        signal_dict['key_indicators'] = eval(signal_dict['indicators_used'])
                    else:
                        signal_dict['key_indicators'] = signal_dict['indicators_used']
                except:
                    signal_dict['key_indicators'] = {}
            else:
                signal_dict['key_indicators'] = {}
            
            signals.append(signal_dict)
        
        db.close()
        return signals
        
    except Exception as e:
        logger.error(f"從資料庫獲取活躍信號失敗: {e}")
        return []

async def _save_signal_to_db(signal: ScalpingSignal, current_price: float):
    """保存信號到資料庫"""
    try:
        db = SessionLocal()
        
        # 先刪除該幣種的舊信號
        delete_query = text("""
            DELETE FROM trading_signals 
            WHERE symbol = :symbol AND (status IS NULL OR status = 'active')
        """)
        db.execute(delete_query, {"symbol": signal.symbol})
        
        # 使用現有表結構
        insert_query = text("""
            INSERT INTO trading_signals (
                symbol, timeframe, signal_type, signal_strength, confidence,
                entry_price, stop_loss, take_profit, risk_reward_ratio,
                primary_timeframe, reasoning, created_at, expires_at,
                status, indicators_used, key_indicators, strategy_name, 
                urgency_level, is_scalping, is_active
            ) VALUES (
                :symbol, :timeframe, :signal_type, :signal_strength, :confidence,
                :entry_price, :stop_loss, :take_profit, :risk_reward_ratio,
                :primary_timeframe, :reasoning, :created_at, :expires_at,
                :status, :indicators_used, :key_indicators, :strategy_name,
                :urgency_level, :is_scalping, :is_active
            )
        """)
        
        # 將策略名稱和緊急度合併到 reasoning 欄位中
        combined_reasoning = f"{signal.strategy_name} ({signal.urgency_level}) - 基於真實市場價格 (${current_price:.4f}) 和 JSON 配置"
        
        signal_id = f"{signal.symbol}_{signal.timeframe}_{int(taiwan_to_naive(get_taiwan_now()).timestamp())}"
        expires_at = signal.created_at + timedelta(minutes=signal.expires_in_minutes)
        
        db.execute(insert_query, {
            'symbol': signal.symbol,
            'timeframe': signal.timeframe,
            'signal_type': signal.signal_type.value,
            'signal_strength': signal.confidence,
            'confidence': signal.confidence,
            'entry_price': signal.entry_price,
            'stop_loss': signal.stop_loss,
            'take_profit': signal.take_profit,
            'risk_reward_ratio': signal.risk_reward_ratio,
            'primary_timeframe': signal.timeframe,
            'reasoning': combined_reasoning,
            'created_at': taiwan_to_naive(signal.created_at).isoformat(),
            'expires_at': taiwan_to_naive(expires_at).isoformat(),
            'status': 'active',
            'indicators_used': str(signal.indicators),
            'key_indicators': str(signal.indicators) if signal.indicators else '{}',
            'strategy_name': signal.strategy_name,
            'urgency_level': signal.urgency_level,
            'is_scalping': True,
            'is_active': True
        })
        
        db.commit()
        db.close()
        logger.info(f"信號 {signal['id']} 已保存到資料庫")
        
    except Exception as e:
        logger.error(f"保存信號到資料庫失敗: {e}")

async def _generate_single_signal(symbol: str, current_price: float, timeframe: str) -> dict:
    """使用新的 ScalpingStrategyEngine 為單個幣種生成信號"""
    try:
        # 使用新的策略引擎生成信號
        signals = await scalping_engine.generate_scalping_signals(symbol, [timeframe])
        
        if not signals:
            logger.info(f"策略引擎未生成 {symbol} {timeframe} 的信號")
            return None
        
        # 選擇第一個信號
        scalping_signal = signals[0]
        
        # 獲取資產配置和止損範圍
        asset_config = scalping_engine.get_asset_config(symbol)
        stop_loss_range = scalping_engine.get_stop_loss_range(symbol)
        
        # 創建信號ID
        taiwan_now = get_taiwan_now().replace(tzinfo=None)
        signal_id = f"scalp_{symbol}_{timeframe}_{taiwan_now.strftime('%Y%m%d_%H%M%S')}"
        
        # 轉換為 API 響應格式
        signal_data = {
            "id": signal_id,
            "symbol": scalping_signal.symbol,
            "signal_type": scalping_signal.signal_type.value,
            "primary_timeframe": scalping_signal.timeframe,
            "confirmed_timeframes": [scalping_signal.timeframe],
            "entry_price": round(scalping_signal.entry_price, 6),
            "stop_loss": round(scalping_signal.stop_loss, 6),
            "take_profit": round(scalping_signal.take_profit, 6),
            "current_price": round(current_price, 6),
            "risk_reward_ratio": round(scalping_signal.risk_reward_ratio, 2),
            "confidence": round(scalping_signal.confidence, 3),
            "signal_strength": round(scalping_signal.confidence, 3),
            "urgency_level": scalping_signal.urgency_level,
            "strategy_name": scalping_signal.strategy_name,
            "reasoning": f"{scalping_signal.strategy_name} - 基於 JSON 配置的動態參數",
            "key_indicators": {
                **scalping_signal.indicators,
                "current_price": current_price,
                "asset_volatility_factor": asset_config.get('volatility_factor', 1.0),
                "stop_loss_range_min": stop_loss_range[0] * 100,
                "stop_loss_range_max": stop_loss_range[1] * 100,
                "timeframe_classification": "ultra_short",
                "max_holding_time": scalping_engine.ultra_short_config['risk_management']['position_hold_limit'],
                "monitoring_frequency": scalping_engine.ultra_short_config['risk_management']['monitoring_frequency']
            },
            "created_at": scalping_signal.created_at.isoformat(),
            "expires_at": (scalping_signal.created_at + timedelta(minutes=scalping_signal.expires_in_minutes)).isoformat(),
            "is_scalping": True,
            "scalping_type": scalping_signal.signal_type.value,
            "execution_status": "active",
            "price_change_percent": round(((current_price - scalping_signal.entry_price) / scalping_signal.entry_price) * 100, 3),
            
            # JSON 配置相關信息
            "timeframe_classification": "ultra_short",
            "asset_config_applied": {
                "volatility_factor": asset_config.get('volatility_factor', 1.0),
                "entry_padding": asset_config.get('entry_padding', 1.0),
                "stop_loss_multiplier": asset_config.get('stop_loss_multiplier', 1.0)
            },
            "risk_management_config": {
                "stop_loss_range": f"{stop_loss_range[0]*100:.1f}%-{stop_loss_range[1]*100:.1f}%",
                "max_holding_time": scalping_engine.ultra_short_config['risk_management']['position_hold_limit'],
                "monitoring_frequency": scalping_engine.ultra_short_config['risk_management']['monitoring_frequency']
            },
            
            "price_deviation_risk": _calculate_price_deviation_risk(current_price, scalping_signal.entry_price, scalping_signal.signal_type.value),
            "market_condition_impact": _assess_market_condition_impact("bull", "conservative", scalping_signal.confidence),
            "remaining_validity_hours": round(scalping_signal.expires_in_minutes / 60, 2)
        }
        
        logger.info(f"✅ 策略引擎生成 {symbol} 信號: {scalping_signal.strategy_name}")
        logger.info(f"   止損範圍: {stop_loss_range[0]*100:.1f}%-{stop_loss_range[1]*100:.1f}%")
        logger.info(f"   波動性因子: {asset_config.get('volatility_factor', 1.0)}")
        
        return signal_data
        
    except Exception as e:
        logger.error(f"策略引擎生成信號失敗 {symbol}: {e}")
        return None
        return None

@router.post("/process-expired")
async def process_expired_signals():
    """處理過期信號 - 標記為已過期並移入歷史"""
    try:
        db = SessionLocal()
        
        # 使用台灣時區進行過期判斷
        taiwan_now = get_taiwan_now().replace(tzinfo=None)
        
        # 查詢需要標記為過期的信號（使用現有的status欄位）
        update_query = text("""
            UPDATE trading_signals 
            SET status = 'expired'
            WHERE datetime(expires_at) <= datetime(:taiwan_now)
            AND (status IS NULL OR status != 'expired')
        """)
        
        result = db.execute(update_query, {"taiwan_now": taiwan_now.isoformat()})
        expired_count = result.rowcount
        
        db.commit()
        db.close()
        
        logger.info(f"標記 {expired_count} 個信號為過期")
        
        return {
            "message": "過期信號處理完成",
            "expired_signals": expired_count,
            "timestamp": get_taiwan_now().isoformat(),
            "timezone": "Asia/Taipei"
        }
        
    except Exception as e:
        logger.error(f"處理過期信號失敗: {e}")
        raise HTTPException(status_code=500, detail=f"處理過期信號失敗: {str(e)}")

@router.get("/prices")
async def get_realtime_prices(symbols: Optional[List[str]] = None):
    """獲取即時幣安價格"""
    try:
        if symbols is None:
            symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT"]
        
        prices = {}
        for symbol in symbols:
            try:
                current_price = await market_service.get_latest_price(symbol, "binance")
                if current_price is not None:
                    prices[symbol] = {
                        "symbol": symbol,
                        "price": round(current_price, 6),
                        "timestamp": get_taiwan_now().isoformat()
                    }
            except Exception as e:
                logger.error(f"獲取 {symbol} 價格失敗: {e}")
                continue
        
        return {
            "prices": prices,
            "total_symbols": len(prices),
            "timestamp": get_taiwan_now().isoformat(),
            "timezone": "Asia/Taipei",
            "source": "Binance API"
        }
        
    except Exception as e:
        logger.error(f"獲取即時價格失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取即時價格失敗: {str(e)}")

def _get_expiry_minutes(timeframe: str) -> int:
    """根據時間框架計算信號有效期（分鐘）"""
    expiry_map = {
        "1m": 5,    # 1分鐘框架：5分鐘有效期
        "3m": 10,   # 3分鐘框架：10分鐘有效期
        "5m": 15,   # 5分鐘框架：15分鐘有效期
        "15m": 30,  # 15分鐘框架：30分鐘有效期
        "30m": 60   # 30分鐘框架：60分鐘有效期
    }
    return expiry_map.get(timeframe, 15)

def _calculate_signal_validity(timeframe: str, created_time: datetime) -> dict:
    """計算信號時效性（後端統一計算，使用台灣時區）"""
    # 使用台灣時間進行計算
    now = get_taiwan_now().replace(tzinfo=None)
    
    # 統一處理時間對象，確保都是台灣時間的 naive datetime
    if isinstance(created_time, str):
        created_time = parse_time_to_taiwan(created_time)
    elif hasattr(created_time, 'tzinfo') and created_time.tzinfo is not None:
        # 如果是 offset-aware datetime，轉換為台灣時間
        created_time = taiwan_to_naive(created_time)
    
    minutes_elapsed = (now - created_time).total_seconds() / 60
    
    # 根據時間框架設定有效期
    validity_minutes = _get_expiry_minutes(timeframe)
    
    remaining_minutes = max(0, validity_minutes - minutes_elapsed)
    remaining_seconds = max(0, (validity_minutes * 60) - (now - created_time).total_seconds())
    percentage = (remaining_minutes / validity_minutes) * 100
    
    # 判斷時效性狀態
    if percentage > 70:
        status = "fresh"
        if remaining_minutes >= 1:
            text = f"{int(remaining_minutes)}分鐘 (新鮮)"
        else:
            text = f"{int(remaining_seconds)}秒 (新鮮)"
        color = "green"
    elif percentage > 30:
        status = "valid"
        if remaining_minutes >= 1:
            text = f"{int(remaining_minutes)}分鐘 (有效)"
        else:
            text = f"{int(remaining_seconds)}秒 (有效)"
        color = "yellow"
    elif percentage > 0:
        status = "expiring"
        if remaining_minutes >= 1:
            text = f"{int(remaining_minutes)}分鐘 (即將過期)"
        else:
            text = f"{int(remaining_seconds)}秒 (即將過期)"
        color = "orange"
    else:
        status = "expired"
        text = "已過期"
        color = "red"
    
    return {
        "percentage": round(percentage, 1),
        "remaining_minutes": round(remaining_minutes, 1),
        "remaining_seconds": round(remaining_seconds, 1),
        "status": status,
        "text": text,
        "color": color,
        "can_execute": percentage > 10  # 只有剩餘時效>10%才能執行
    }

def _calculate_price_deviation_risk(current_price: float, entry_price: float, signal_direction: str) -> dict:
    """計算價格偏離風險（後端統一計算）"""
    if not current_price or not entry_price:
        return {"level": "unknown", "percentage": 0, "warning": "", "color": "gray"}
    
    deviation = abs(current_price - entry_price) / entry_price * 100
    
    # 判斷是否為不利方向
    is_unfavorable = (
        (signal_direction == "LONG" and current_price < entry_price) or
        (signal_direction == "SHORT" and current_price > entry_price)
    )
    
    if not is_unfavorable:
        # 有利方向
        return {
            "level": "profit",
            "percentage": round(deviation, 2),
            "warning": f"{'上漲' if signal_direction == 'LONG' else '下跌'} {deviation:.1f}%",
            "color": "green"
        }
    
    # 不利方向，按風險等級分類
    if deviation > 12:
        return {"level": "critical", "percentage": round(deviation, 2), 
                "warning": f"嚴重偏離 -{deviation:.1f}%", "color": "red"}
    elif deviation > 8:
        return {"level": "high", "percentage": round(deviation, 2),
                "warning": f"高風險 -{deviation:.1f}%", "color": "orange"}
    elif deviation > 5:
        return {"level": "medium", "percentage": round(deviation, 2),
                "warning": f"中風險 -{deviation:.1f}%", "color": "yellow"}
    else:
        return {"level": "low", "percentage": round(deviation, 2),
                "warning": "正常範圍", "color": "green"}

def _assess_market_condition_impact(market_condition: str, risk_level: str, confidence: float) -> dict:
    """評估市場條件對信號的影響（後端統一計算）"""
    impact_score = confidence
    
    # 根據市場條件調整
    if market_condition == "bull":
        impact_score *= 1.1  # 牛市加成10%
        condition_text = "牛市利好"
    elif market_condition == "bear":
        impact_score *= 0.9  # 熊市折扣10%
        condition_text = "熊市謹慎"
    else:
        condition_text = "中性市場"
    
    # 根據風險等級調整
    if risk_level == "aggressive":
        impact_score *= 1.05
        risk_text = "激進策略"
    else:
        risk_text = "保守策略"
    
    # 最終評級
    if impact_score > 0.9:
        overall_rating = "excellent"
        rating_text = "極佳"
        rating_color = "green"
    elif impact_score > 0.8:
        overall_rating = "good"
        rating_text = "良好" 
        rating_color = "blue"
    elif impact_score > 0.7:
        overall_rating = "fair"
        rating_text = "一般"
        rating_color = "yellow"
    else:
        overall_rating = "poor"
        rating_text = "較差"
        rating_color = "red"
    
        return {
            "impact_score": round(impact_score, 3),
            "condition_text": condition_text,
            "risk_text": risk_text,
            "overall_rating": overall_rating,
            "rating_text": rating_text,
            "rating_color": rating_color
        }

@router.get("/expired")
async def get_expired_scalping_signals():
    """獲取過期的短線信號（供歷史頁面使用）"""
    try:
        db = SessionLocal()
        
        # 查詢所有過期的短線信號
        query = text("""
            SELECT * FROM trading_signals 
            WHERE status = 'expired'
            ORDER BY created_at DESC
        """)
        
        result = db.execute(query)
        expired_signals = []
        
        for row in result:
            signal_dict = dict(row._mapping)
            
            # 設置預設值以相容前端
            signal_dict['primary_timeframe'] = signal_dict.get('timeframe', '5m')
            signal_dict['is_scalping'] = True
            signal_dict['urgency_level'] = signal_dict.get('urgency_level', 'medium')
            # 保留原始策略名稱（來自新策略引擎的信號）
            signal_dict['strategy_name'] = signal_dict.get('strategy_name', '技術分析')
            signal_dict['reasoning'] = signal_dict.get('reasoning', '短線交易策略')
            
            # 解析 indicators_used JSON 字段作為 key_indicators
            if signal_dict.get('indicators_used'):
                try:
                    if isinstance(signal_dict['indicators_used'], str):
                        signal_dict['key_indicators'] = eval(signal_dict['indicators_used'])
                    else:
                        signal_dict['key_indicators'] = signal_dict['indicators_used']
                except:
                    signal_dict['key_indicators'] = {}
            else:
                signal_dict['key_indicators'] = {}
            
            # 添加過期時的時效性信息
            signal_dict['validity_info'] = {
                "percentage": 0,
                "remaining_minutes": 0,
                "remaining_seconds": 0,
                "status": "expired",
                "text": "已過期",
                "color": "red",
                "can_execute": False
            }
            
            expired_signals.append(signal_dict)
        
        db.close()
        
        logger.info(f"返回 {len(expired_signals)} 個過期短線信號")
        return expired_signals
        
    except Exception as e:
        logger.error(f"獲取過期短線信號失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取過期短線信號失敗: {str(e)}")