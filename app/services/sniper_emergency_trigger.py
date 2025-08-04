# 🎯 狙擊手緊急觸發系統

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from app.core.database import db_manager
from app.models.sniper_signal_history import (
    SniperSignalDetails, 
    SignalStatus, 
    TradingTimeframe
)
from app.services.sniper_signal_history_service import sniper_signal_tracker

logger = logging.getLogger(__name__)

class TriggerType(Enum):
    """緊急觸發類型"""
    VOLUME_SPIKE = "VOLUME_SPIKE"           # 成交量激增
    PRICE_CHANGE = "PRICE_CHANGE"           # 價格劇烈變動
    MARKET_SENTIMENT = "MARKET_SENTIMENT"   # 市場情緒變化
    TECHNICAL_BREAKOUT = "TECHNICAL_BREAKOUT" # 技術突破

class TimeframeCategory(Enum):
    """時間框架分類"""
    SHORT_TERM = "SHORT_TERM"   # 5分鐘更新 - BTCUSDT, ETHUSDT
    MEDIUM_TERM = "MEDIUM_TERM" # 30分鐘更新 - ADAUSDT, BNBUSDT, SOLUSDT  
    LONG_TERM = "LONG_TERM"     # 2小時更新 - XRPUSDT, DOGEUSDT

@dataclass
class EmergencyTrigger:
    """緊急觸發配置"""
    timeframe: TimeframeCategory
    symbols: List[str]
    volume_threshold: float  # 成交量激增閾值 (%)
    price_change_threshold: float  # 價格變動閾值 (%)
    time_window: int  # 檢測時間窗口 (分鐘)
    update_interval: int  # 正常更新間隔 (分鐘)
    priority: int  # 優先級 (1=最高, 3=最低)

class SniperEmergencyTrigger:
    """🎯 狙擊手緊急觸發系統"""
    
    def __init__(self):
        self.triggers = {
            TimeframeCategory.SHORT_TERM: EmergencyTrigger(
                timeframe=TimeframeCategory.SHORT_TERM,
                symbols=["BTCUSDT", "ETHUSDT"],
                volume_threshold=200.0,  # 成交量激增200%
                price_change_threshold=5.0,  # 1分鐘5%變動
                time_window=1,  # 1分鐘檢測窗口
                update_interval=5,  # 5分鐘正常更新
                priority=1  # 高優先級
            ),
            TimeframeCategory.MEDIUM_TERM: EmergencyTrigger(
                timeframe=TimeframeCategory.MEDIUM_TERM,
                symbols=["ADAUSDT", "BNBUSDT", "SOLUSDT"],
                volume_threshold=150.0,  # 成交量激增150%
                price_change_threshold=8.0,  # 5分鐘8%變動
                time_window=5,  # 5分鐘檢測窗口
                update_interval=30,  # 30分鐘正常更新
                priority=2  # 中優先級
            ),
            TimeframeCategory.LONG_TERM: EmergencyTrigger(
                timeframe=TimeframeCategory.LONG_TERM,
                symbols=["XRPUSDT", "DOGEUSDT"],
                volume_threshold=100.0,  # 成交量激增100%
                price_change_threshold=15.0,  # 1小時15%變動
                time_window=60,  # 1小時檢測窗口
                update_interval=120,  # 2小時正常更新
                priority=3  # 低優先級
            )
        }
        
        self.last_update_times: Dict[str, datetime] = {}
        self.emergency_callbacks: List = []
        self.is_monitoring = False
        
    async def start_monitoring(self):
        """開始緊急監控"""
        self.is_monitoring = True
        logger.info("🎯 狙擊手緊急觸發系統已啟動")
        
        # 為每個時間框架創建監控任務
        tasks = []
        for category, trigger in self.triggers.items():
            task = asyncio.create_task(
                self._monitor_timeframe(category, trigger)
            )
            tasks.append(task)
            
        await asyncio.gather(*tasks)
    
    async def stop_monitoring(self):
        """停止緊急監控"""
        self.is_monitoring = False
        logger.info("🎯 狙擊手緊急觸發系統已停止")
    
    async def _monitor_timeframe(self, category: TimeframeCategory, trigger: EmergencyTrigger):
        """監控特定時間框架"""
        while self.is_monitoring:
            try:
                for symbol in trigger.symbols:
                    # 檢查是否需要緊急觸發
                    emergency_detected = await self._check_emergency_conditions(
                        symbol, trigger
                    )
                    
                    if emergency_detected:
                        await self._trigger_emergency_update(symbol, category, trigger)
                    else:
                        # 檢查是否需要常規更新
                        await self._check_regular_update(symbol, category, trigger)
                
                # 等待下一次檢查 (根據時間框架調整檢查頻率)
                check_interval = min(30, trigger.time_window * 60 // 4)  # 至少30秒檢查一次
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"❌ 監控時間框架 {category.value} 時發生錯誤: {e}")
                await asyncio.sleep(60)  # 錯誤時等待1分鐘再重試
    
    async def _check_emergency_conditions(self, symbol: str, trigger: EmergencyTrigger) -> bool:
        """檢查緊急觸發條件"""
        try:
            # 這裡應該從實時數據源獲取市場數據
            # 現在先用模擬數據進行測試
            current_time = datetime.now()
            
            # 檢查成交量激增
            volume_spike = await self._check_volume_spike(symbol, trigger)
            
            # 檢查價格劇烈變動
            price_change = await self._check_price_change(symbol, trigger)
            
            # 檢查技術突破
            technical_breakout = await self._check_technical_breakout(symbol, trigger)
            
            emergency_detected = volume_spike or price_change or technical_breakout
            
            if emergency_detected:
                logger.warning(f"⚡ {symbol} 檢測到緊急條件: "
                             f"成交量激增={volume_spike}, "
                             f"價格劇變={price_change}, "
                             f"技術突破={technical_breakout}")
            
            return emergency_detected
            
        except Exception as e:
            logger.error(f"❌ 檢查 {symbol} 緊急條件時發生錯誤: {e}")
            return False
    
    async def _check_volume_spike(self, symbol: str, trigger: EmergencyTrigger) -> bool:
        """檢查成交量激增"""
        # TODO: 實現實際的成交量檢查邏輯
        # 這裡應該比較當前成交量與歷史平均成交量
        return False
    
    async def _check_price_change(self, symbol: str, trigger: EmergencyTrigger) -> bool:
        """檢查價格劇烈變動"""
        # TODO: 實現實際的價格變動檢查邏輯
        # 這裡應該比較指定時間窗口內的價格變動
        return False
    
    async def _check_technical_breakout(self, symbol: str, trigger: EmergencyTrigger) -> bool:
        """檢查技術突破"""
        # TODO: 實現技術突破檢查邏輯
        # 這裡應該檢查重要技術位的突破
        return False
    
    async def _trigger_emergency_update(self, symbol: str, category: TimeframeCategory, trigger: EmergencyTrigger):
        """觸發緊急更新"""
        logger.warning(f"⚡ 觸發 {symbol} 緊急更新 ({category.value})")
        
        # 立即執行狙擊手分析
        emergency_signal = await self._execute_emergency_analysis(symbol, category)
        
        # 更新最後更新時間
        self.last_update_times[f"{symbol}_{category.value}"] = datetime.now()
        
        # 觸發前端更新
        await self._notify_frontend_emergency(symbol, category, emergency_signal)
        
        # 記錄緊急觸發事件
        await self._log_emergency_event(symbol, category, trigger, emergency_signal)
    
    async def _check_regular_update(self, symbol: str, category: TimeframeCategory, trigger: EmergencyTrigger):
        """檢查常規更新"""
        current_time = datetime.now()
        last_update_key = f"{symbol}_{category.value}"
        
        last_update = self.last_update_times.get(last_update_key)
        if not last_update:
            # 首次更新
            await self._execute_regular_update(symbol, category, trigger)
            return
        
        # 檢查是否超過更新間隔
        time_diff = (current_time - last_update).total_seconds() / 60  # 轉換為分鐘
        if time_diff >= trigger.update_interval:
            await self._execute_regular_update(symbol, category, trigger)
    
    async def _execute_regular_update(self, symbol: str, category: TimeframeCategory, trigger: EmergencyTrigger):
        """執行常規更新"""
        logger.info(f"🔄 執行 {symbol} 常規更新 ({category.value})")
        
        # 執行狙擊手分析 (簡化版)
        regular_signal = await self._execute_regular_analysis(symbol, category)
        
        # 更新最後更新時間
        self.last_update_times[f"{symbol}_{category.value}"] = datetime.now()
        
        # 如果有有效信號，通知前端
        if regular_signal:
            await self._notify_frontend_regular(symbol, category, regular_signal)
    
    async def _execute_emergency_analysis(self, symbol: str, category: TimeframeCategory) -> Optional[Dict]:
        """執行緊急狙擊手分析 (完整流程)"""
        try:
            # 這裡應該調用完整的狙擊手分析流程
            # 包括 Phase 1ABC + Phase 1+2+3 + pandas-ta + 雙層架構
            
            logger.info(f"🎯 執行 {symbol} 緊急狙擊手分析...")
            
            # 模擬分析結果
            emergency_signal = {
                'signal_id': f"emergency_{symbol}_{int(datetime.now().timestamp())}",
                'symbol': symbol,
                'signal_type': 'BUY',  # 根據實際分析結果確定
                'entry_price': 0.0,    # 根據實際市場價格確定
                'stop_loss': 0.0,
                'take_profit': 0.0,
                'confidence': 0.95,    # 緊急信號通常有較高信心度
                'timeframe': category.value,
                'trigger_type': 'EMERGENCY',
                'analysis_type': 'FULL_PIPELINE',
                'created_at': datetime.now().isoformat(),
                'emergency_reason': '成交量激增+價格突破',
                'sniper_metrics': {
                    'layer_one_time': 0.008,  # 緊急模式更快
                    'layer_two_time': 0.015,
                    'pass_rate': 0.92,
                    'precision': 0.96
                }
            }
            
            return emergency_signal
            
        except Exception as e:
            logger.error(f"❌ 執行 {symbol} 緊急分析失敗: {e}")
            return None
    
    async def _execute_regular_analysis(self, symbol: str, category: TimeframeCategory) -> Optional[Dict]:
        """執行常規狙擊手分析 (輕量版)"""
        try:
            # 這裡應該調用輕量版的狙擊手分析
            # 只進行必要的檢查，避免過度計算
            
            logger.info(f"🔄 執行 {symbol} 常規狙擊手分析...")
            
            # 檢查是否有值得關注的信號
            # 如果沒有明顯機會，返回 None 避免無效信號
            
            # 模擬分析 - 只有30%機率產生常規信號
            import random
            if random.random() < 0.3:
                regular_signal = {
                    'signal_id': f"regular_{symbol}_{int(datetime.now().timestamp())}",
                    'symbol': symbol,
                    'signal_type': 'BUY',
                    'entry_price': 0.0,
                    'stop_loss': 0.0,
                    'take_profit': 0.0,
                    'confidence': 0.75,  # 常規信號信心度較低
                    'timeframe': category.value,
                    'trigger_type': 'REGULAR',
                    'analysis_type': 'LIGHTWEIGHT',
                    'created_at': datetime.now().isoformat(),
                    'sniper_metrics': {
                        'layer_one_time': 0.012,
                        'layer_two_time': 0.025,
                        'pass_rate': 0.68,
                        'precision': 0.82
                    }
                }
                return regular_signal
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 執行 {symbol} 常規分析失敗: {e}")
            return None
    
    async def _notify_frontend_emergency(self, symbol: str, category: TimeframeCategory, signal: Dict):
        """通知前端緊急信號"""
        notification = {
            'type': 'emergency_signal',
            'priority': 'HIGH',
            'symbol': symbol,
            'category': category.value,
            'signal': signal,
            'timestamp': datetime.now().isoformat()
        }
        
        # 這裡應該通過 WebSocket 發送給前端
        logger.info(f"📡 發送緊急信號通知: {symbol}")
        
        # 觸發註冊的回調函數
        for callback in self.emergency_callbacks:
            try:
                await callback(notification)
            except Exception as e:
                logger.error(f"❌ 緊急回調執行失敗: {e}")
    
    async def _notify_frontend_regular(self, symbol: str, category: TimeframeCategory, signal: Dict):
        """通知前端常規信號"""
        notification = {
            'type': 'regular_signal',
            'priority': 'NORMAL',
            'symbol': symbol,
            'category': category.value,
            'signal': signal,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"📡 發送常規信號通知: {symbol}")
        
        # 觸發註冊的回調函數
        for callback in self.emergency_callbacks:
            try:
                await callback(notification)
            except Exception as e:
                logger.error(f"❌ 常規回調執行失敗: {e}")
    
    async def _log_emergency_event(self, symbol: str, category: TimeframeCategory, trigger: EmergencyTrigger, signal: Dict):
        """記錄緊急觸發事件"""
        try:
            event_log = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'category': category.value,
                'trigger_type': 'EMERGENCY',
                'volume_threshold': trigger.volume_threshold,
                'price_threshold': trigger.price_change_threshold,
                'signal_generated': signal is not None,
                'signal_id': signal.get('signal_id') if signal else None
            }
            
            # 這裡可以存儲到數據庫或日誌文件
            logger.info(f"📝 記錄緊急事件: {json.dumps(event_log, ensure_ascii=False)}")
            
        except Exception as e:
            logger.error(f"❌ 記錄緊急事件失敗: {e}")
    
    def register_callback(self, callback):
        """註冊緊急觸發回調"""
        self.emergency_callbacks.append(callback)
    
    async def get_last_strategy_analysis(self, symbol: str) -> Optional[Dict]:
        """🎯 獲取上一單策略分析 - 用於判斷接下來是要止損還是觀望"""
        try:
            async with db_manager.create_session() as session:
                # 獲取最近的活躍信號
                latest_signal = await session.query(SniperSignalDetails).filter(
                    SniperSignalDetails.symbol == symbol,
                    SniperSignalDetails.status == SignalStatus.ACTIVE
                ).order_by(SniperSignalDetails.created_at.desc()).first()
                
                if not latest_signal:
                    return None
                
                # 分析當前市場狀況與信號的關係
                current_analysis = {
                    'signal_id': latest_signal.signal_id,
                    'symbol': latest_signal.symbol,
                    'signal_type': latest_signal.signal_type,
                    'entry_price': latest_signal.entry_price,
                    'stop_loss': latest_signal.stop_loss_price,
                    'take_profit': latest_signal.take_profit_price,
                    'created_at': latest_signal.created_at.isoformat(),
                    'signal_strength': latest_signal.signal_strength,
                    'timeframe': latest_signal.timeframe.value,
                    'current_status': latest_signal.status.value,
                    
                    # 決策建議
                    'recommendation': await self._analyze_current_position(latest_signal),
                    'risk_assessment': await self._assess_current_risk(latest_signal),
                    'market_condition': await self._get_current_market_condition(symbol)
                }
                
                return current_analysis
                
        except Exception as e:
            logger.error(f"❌ 獲取 {symbol} 上一單策略分析失敗: {e}")
            return None
    
    async def _analyze_current_position(self, signal: SniperSignalDetails) -> Dict:
        """分析當前持倉建議"""
        # TODO: 根據當前價格和信號狀態分析
        return {
            'action': 'HOLD',  # HOLD/STOP_LOSS/WATCH
            'reason': '信號仍在有效範圍內，建議持續觀察',
            'confidence': 0.75
        }
    
    async def _assess_current_risk(self, signal: SniperSignalDetails) -> Dict:
        """評估當前風險水平"""
        # TODO: 根據市場波動和信號表現評估風險
        return {
            'risk_level': 'MEDIUM',  # LOW/MEDIUM/HIGH
            'stop_loss_distance': abs(signal.entry_price - signal.stop_loss_price),
            'profit_potential': abs(signal.take_profit_price - signal.entry_price)
        }
    
    async def _get_current_market_condition(self, symbol: str) -> Dict:
        """獲取當前市場狀況"""
        # TODO: 分析當前市場趨勢和波動情況
        return {
            'trend': 'SIDEWAYS',  # UPTREND/DOWNTREND/SIDEWAYS
            'volatility': 'NORMAL',  # LOW/NORMAL/HIGH
            'volume': 'AVERAGE'  # LOW/AVERAGE/HIGH
        }

# 全局實例
sniper_emergency_trigger = SniperEmergencyTrigger()
