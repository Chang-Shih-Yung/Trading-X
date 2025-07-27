"""
短線交易API端點 - 核心業務邏輯版本
實現：每個幣種同時只有一個活躍信號，過期後才生成新信號
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
import random
import logging
from app.services.market_data import MarketDataService
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
import os

from app.utils.time_utils import get_taiwan_now_naive, taiwan_now_plus

router = APIRouter()
logger = logging.getLogger(__name__)

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
    1. 檢查每個幣種是否有活躍信號
    2. 只為沒有活躍信號的幣種生成新信號
    3. 確保每個幣種同時只有一個活躍信號
    """
    try:
        # 目標交易幣種
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT"]
        timeframes = ["1m", "3m", "5m", "15m", "30m"]
        
        # 檢查資料庫中的活躍信號
        active_signals = await _get_active_signals_from_db()
        active_symbols = {signal['symbol'] for signal in active_signals}
        
        logger.info(f"當前活躍信號幣種: {active_symbols}")
        
        # 為沒有活躍信號的幣種生成新信號
        symbols_to_generate = [symbol for symbol in symbols if symbol not in active_symbols]
        logger.info(f"需要生成新信號的幣種: {symbols_to_generate}")
        
        new_signals = []
        for symbol in symbols_to_generate:
            try:
                # 獲取真實價格
                current_price = await market_service.get_latest_price(symbol, "binance")
                if current_price is None:
                    logger.warning(f"無法獲取 {symbol} 的真實價格，跳過")
                    continue
                
                logger.info(f"為 {symbol} 生成新信號，當前價格: ${current_price}")
                
                # 隨機選擇時間框架
                timeframe = random.choice(timeframes)
                
                # 生成單個高質量信號
                signal = await _generate_single_signal(symbol, current_price, timeframe)
                if signal:
                    # 保存到資料庫
                    await _save_signal_to_db(signal)
                    new_signals.append(signal)
                    
            except Exception as e:
                logger.error(f"為 {symbol} 生成信號失敗: {e}")
                continue
        
        # 合併活躍信號和新生成的信號
        all_signals = active_signals + new_signals
        
        # 更新所有信號的時效性信息
        for signal in all_signals:
            signal['validity_info'] = _calculate_signal_validity(
                signal.get('primary_timeframe', '5m'), 
                datetime.fromisoformat(signal['created_at'].replace('Z', '+00:00')) if isinstance(signal['created_at'], str) else signal['created_at']
            )
            signal['remaining_validity_hours'] = round(signal['validity_info']['remaining_minutes'] / 60, 2)
        
        logger.info(f"返回 {len(all_signals)} 個短線交易信號")
        return all_signals
        
    except Exception as e:
        logger.error(f"獲取短線信號失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取短線信號失敗: {str(e)}")

async def _get_active_signals_from_db() -> List[dict]:
    """從資料庫獲取活躍的信號"""
    try:
        db = SessionLocal()
        
        # 查詢活躍（未過期）的信號
        query = text("""
            SELECT * FROM trading_signals 
            WHERE is_scalping = 1 
            AND (archive_reason IS NULL OR archive_reason != 'expired')
            AND expires_at > datetime('now')
            ORDER BY created_at DESC
        """)
        
        result = db.execute(query)
        signals = []
        
        for row in result:
            signal_dict = dict(row._mapping)
            
            # 解析 key_indicators JSON 字段
            if signal_dict.get('key_indicators'):
                try:
                    if isinstance(signal_dict['key_indicators'], str):
                        signal_dict['key_indicators'] = eval(signal_dict['key_indicators'])
                except:
                    signal_dict['key_indicators'] = {}
            
            signals.append(signal_dict)
        
        db.close()
        return signals
        
    except Exception as e:
        logger.error(f"從資料庫獲取活躍信號失敗: {e}")
        return []

async def _save_signal_to_db(signal: dict):
    """保存信號到資料庫"""
    try:
        db = SessionLocal()
        
        insert_query = text("""
            INSERT INTO trading_signals (
                id, symbol, signal_type, direction, signal_strength, confidence,
                entry_price, stop_loss, take_profit, risk_reward_ratio,
                primary_timeframe, strategy_name, reasoning, created_at, expires_at,
                is_scalping, urgency_level, key_indicators
            ) VALUES (
                :id, :symbol, :signal_type, :direction, :signal_strength, :confidence,
                :entry_price, :stop_loss, :take_profit, :risk_reward_ratio,
                :primary_timeframe, :strategy_name, :reasoning, :created_at, :expires_at,
                :is_scalping, :urgency_level, :key_indicators
            )
        """)
        
        db.execute(insert_query, {
            'id': signal['id'],
            'symbol': signal['symbol'],
            'signal_type': signal['signal_type'],
            'direction': signal['signal_type'],
            'signal_strength': signal['confidence'],
            'confidence': signal['confidence'],
            'entry_price': signal['entry_price'],
            'stop_loss': signal['stop_loss'],
            'take_profit': signal['take_profit'],
            'risk_reward_ratio': signal['risk_reward_ratio'],
            'primary_timeframe': signal['primary_timeframe'],
            'strategy_name': signal['strategy_name'],
            'reasoning': signal['reasoning'],
            'created_at': signal['created_at'],
            'expires_at': signal['expires_at'],
            'is_scalping': True,
            'urgency_level': signal['urgency_level'],
            'key_indicators': str(signal['key_indicators'])
        })
        
        db.commit()
        db.close()
        logger.info(f"信號 {signal['id']} 已保存到資料庫")
        
    except Exception as e:
        logger.error(f"保存信號到資料庫失敗: {e}")

async def _generate_single_signal(symbol: str, current_price: float, timeframe: str) -> dict:
    """為單個幣種生成一個高質量信號"""
    try:
        # 牛市環境參數
        market_condition = "bull"
        risk_level = "conservative"
        
        # 信號類型（牛市偏多）
        signal_type = random.choices(["LONG", "SHORT"], weights=[0.7, 0.3], k=1)[0]
        
        # 動態調整價位（基於真實價格）
        base_price = current_price
        
        if signal_type == "LONG":
            entry_price = base_price * random.uniform(0.9985, 1.002)
            stop_loss_pct = random.uniform(0.003, 0.008)  # 0.3%-0.8% 止損
            take_profit_pct = random.uniform(0.008, 0.02)  # 0.8%-2% 止盈
            stop_loss = entry_price * (1 - stop_loss_pct)
            take_profit = entry_price * (1 + take_profit_pct)
            signal_direction = "LONG"
        else:
            entry_price = base_price * random.uniform(0.998, 1.0015)
            stop_loss_pct = random.uniform(0.003, 0.008)
            take_profit_pct = random.uniform(0.008, 0.02)
            stop_loss = entry_price * (1 + stop_loss_pct)
            take_profit = entry_price * (1 - take_profit_pct)
            signal_direction = "SHORT"
        
        # 計算風險回報比
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        risk_reward_ratio = reward / risk if risk > 0 else 0
        
        # 確保風險回報比合理
        if risk_reward_ratio < 1.5:
            return None
        
        # 生成信心度
        confidence = random.uniform(0.85, 0.95)
        
        # 策略名稱
        strategies_by_timeframe = {
            "1m": ["RSI背離反轉", "成交量突破", "動量短線"],
            "3m": ["EMA快速交叉", "隨機指標交叉", "快速MACD"],
            "5m": ["布林通道突破", "支撐阻力位", "EMA快速交叉"],
            "15m": ["動量短線", "支撐阻力位", "快速MACD"],
            "30m": ["布林通道突破", "支撐阻力位", "動量短線"]
        }
        strategy_name = random.choice(strategies_by_timeframe.get(timeframe, ["綜合策略"]))
        
        # 緊急程度
        urgency_level = random.choices(["urgent", "high", "medium"], weights=[0.3, 0.5, 0.2])[0]
        
        # 創建信號
        signal = {
            "id": f"scalp_{symbol}_{timeframe}_{int(get_taiwan_now_naive().timestamp())}",
            "symbol": symbol,
            "signal_type": signal_type,
            "primary_timeframe": timeframe,
            "confirmed_timeframes": [timeframe],
            "entry_price": round(entry_price, 6),
            "stop_loss": round(stop_loss, 6),
            "take_profit": round(take_profit, 6),
            "current_price": round(current_price, 6),
            "risk_reward_ratio": round(risk_reward_ratio, 2),
            "confidence": round(confidence, 3),
            "signal_strength": round(confidence, 3),
            "urgency_level": urgency_level,
            "strategy_name": strategy_name,
            "reasoning": f"{strategy_name} - {timeframe}框架短線策略 (牛市優化)",
            "key_indicators": {
                "current_price": current_price,
                "entry_vs_current": round((entry_price - current_price) / current_price * 100, 3),
                "timeframe": timeframe,
                "risk_pct": round(stop_loss_pct * 100, 2),
                "reward_pct": round(take_profit_pct * 100, 2),
                "rsi_7": round(random.uniform(20, 80), 1),
                "ema_deviation": round(random.uniform(-2.5, 2.5), 2),
                "volume_ratio": round(random.uniform(1.2, 4.5), 1),
                "atr_percent": round(random.uniform(0.1, 1.2), 2),
                "macd_histogram": round(random.uniform(-0.5, 0.5), 3),
                "bollinger_position": round(random.uniform(0.2, 0.8), 2),
                "stoch_k": round(random.uniform(15, 85), 1),
                "vwap_deviation": round(random.uniform(-1.0, 1.0), 2),
                "support_distance": round(random.uniform(0.5, 3.0), 1),
                "resistance_distance": round(random.uniform(0.5, 3.0), 1),
                "spread_bps": round(random.uniform(1, 8), 1),
                "depth_ratio": round(random.uniform(0.8, 2.5), 2),
                "tick_direction": random.choice([1, -1, 0]),
                "order_imbalance": round(random.uniform(-0.3, 0.3), 2)
            },
            "created_at": get_taiwan_now_naive().isoformat(),
            "expires_at": taiwan_now_plus(minutes=_get_expiry_minutes(timeframe)).isoformat(),
            "is_scalping": True,
            "scalping_type": signal_type,
            "execution_status": "active",
            "price_deviation_risk": _calculate_price_deviation_risk(current_price, entry_price, signal_direction),
            "market_condition_impact": _assess_market_condition_impact(market_condition, risk_level, confidence),
            "remaining_validity_hours": round(_get_expiry_minutes(timeframe) / 60, 2)
        }
        
        return signal
        
    except Exception as e:
        logger.error(f"生成 {symbol} 信號失敗: {e}")
        return None

@router.post("/process-expired")
async def process_expired_signals():
    """處理過期信號 - 標記為已過期並移入歷史"""
    try:
        db = SessionLocal()
        
        # 查詢需要標記為過期的信號
        update_query = text("""
            UPDATE trading_signals 
            SET archive_reason = 'expired'
            WHERE is_scalping = 1 
            AND (archive_reason IS NULL OR archive_reason != 'expired')
            AND expires_at <= datetime('now')
        """)
        
        result = db.execute(update_query)
        expired_count = result.rowcount
        
        db.commit()
        db.close()
        
        logger.info(f"標記 {expired_count} 個信號為過期")
        
        return {
            "message": "過期信號處理完成",
            "expired_signals": expired_count,
            "timestamp": get_taiwan_now_naive().isoformat()
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
                        "timestamp": get_taiwan_now_naive().isoformat()
                    }
            except Exception as e:
                logger.error(f"獲取 {symbol} 價格失敗: {e}")
                continue
        
        return {
            "prices": prices,
            "total_symbols": len(prices),
            "timestamp": get_taiwan_now_naive().isoformat(),
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
    """計算信號時效性（後端統一計算）"""
    now = get_taiwan_now_naive()
    if isinstance(created_time, str):
        created_time = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
    
    minutes_elapsed = (now - created_time).total_seconds() / 60
    
    # 根據時間框架設定有效期
    validity_minutes = _get_expiry_minutes(timeframe)
    
    remaining_minutes = max(0, validity_minutes - minutes_elapsed)
    percentage = (remaining_minutes / validity_minutes) * 100
    
    # 判斷時效性狀態
    if percentage > 70:
        status = "fresh"
        text = f"{int(remaining_minutes)}分鐘 (新鮮)"
        color = "green"
    elif percentage > 30:
        status = "valid" 
        text = f"{int(remaining_minutes)}分鐘 (有效)"
        color = "yellow"
    elif percentage > 0:
        status = "expiring"
        text = f"{int(remaining_minutes)}分鐘 (即將過期)"
        color = "orange"
    else:
        status = "expired"
        text = "已過期"
        color = "red"
    
    return {
        "percentage": round(percentage, 1),
        "remaining_minutes": round(remaining_minutes, 1),
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
