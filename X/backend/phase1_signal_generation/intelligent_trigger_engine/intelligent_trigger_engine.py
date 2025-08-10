"""
🎯 Trading X - 智能觸發引擎
高勝率信號檢測與智能觸發系統
符合 intelligent_trigger_config.json v1.0.0 規範
與 Phase1 主協調器深度整合
"""

import asyncio
import logging
import json
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from collections import deque, defaultdict
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# 技術指標庫
try:
    import pandas_ta as ta
except ImportError:
    ta = None
    logging.warning("pandas_ta 未安裝，部分技術指標功能將受限")

logger = logging.getLogger(__name__)

# ==================== 數據結構定義 ====================

class SignalPriority(Enum):
    """信號優先級枚舉"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class TriggerReason(Enum):
    """觸發原因枚舉"""
    PRICE_MOMENTUM_1MIN = "price_momentum_1min"
    PRICE_MOMENTUM_5MIN = "price_momentum_5min"
    PRICE_MOMENTUM_15MIN = "price_momentum_15min"
    INDICATOR_CONVERGENCE = "indicator_convergence"
    VOLUME_CONFIRMATION = "volume_confirmation"
    SUPPORT_RESISTANCE_EVENT = "support_resistance_event"
    PERIODIC_CHECK = "periodic_check"

class MarketCondition(Enum):
    """市場條件枚舉"""
    TREND_BULLISH = "trend_bullish"
    TREND_BEARISH = "trend_bearish"
    RANGING = "ranging"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"

@dataclass
class TechnicalIndicatorState:
    """技術指標狀態"""
    rsi: Optional[float] = None
    rsi_convergence: float = 0.0
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    macd_convergence: float = 0.0
    bollinger_upper: Optional[float] = None
    bollinger_lower: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_convergence: float = 0.0
    volume_sma: Optional[float] = None
    volume_spike_ratio: float = 0.0
    volume_convergence: float = 0.0
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None
    support_resistance_convergence: float = 0.0
    overall_convergence_score: float = 0.0

@dataclass
class PriceData:
    """價格數據"""
    symbol: str
    price: float
    volume: float
    timestamp: datetime
    price_change_1min: float = 0.0
    price_change_5min: float = 0.0
    price_change_15min: float = 0.0
    volume_change: float = 0.0

@dataclass
class TriggerCondition:
    """觸發條件"""
    reason: TriggerReason
    priority: SignalPriority
    confidence_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WinRatePrediction:
    """勝率預測"""
    predicted_win_rate: float
    confidence_interval: Tuple[float, float]
    sample_size: int
    historical_performance: Dict[str, float]
    ml_features: Dict[str, float] = field(default_factory=dict)

@dataclass
class IntelligentSignal:
    """智能信號"""
    symbol: str
    trigger_reason: TriggerReason
    priority: SignalPriority
    confidence_score: float
    win_rate_prediction: WinRatePrediction
    technical_indicators_state: TechnicalIndicatorState
    market_conditions: List[MarketCondition]
    risk_assessment: Dict[str, float]
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_unified_signal_format(self) -> Dict[str, Any]:
        """轉換為統一信號格式 (unified_signal_candidate_pool_v3)"""
        return {
            "signal_id": f"{self.symbol}_{self.trigger_reason.value}_{int(self.timestamp.timestamp())}",
            "symbol": self.symbol,
            "signal_type": "INTELLIGENT_TRIGGER",
            "priority": self.priority.value,
            "confidence": self.confidence_score,
            "win_rate_prediction": self.win_rate_prediction.predicted_win_rate,
            "technical_analysis": {
                "rsi": self.technical_indicators_state.rsi,
                "macd": self.technical_indicators_state.macd,
                "bollinger_position": self._calculate_bollinger_position(),
                "volume_spike": self.technical_indicators_state.volume_spike_ratio,
                "convergence_score": self.technical_indicators_state.overall_convergence_score
            },
            "market_conditions": [condition.value for condition in self.market_conditions],
            "risk_metrics": self.risk_assessment,
            "trigger_metadata": {
                "trigger_reason": self.trigger_reason.value,
                "timestamp": self.timestamp.isoformat(),
                **self.metadata
            }
        }
    
    def _calculate_bollinger_position(self) -> float:
        """計算布林帶位置"""
        if (self.technical_indicators_state.bollinger_upper is None or 
            self.technical_indicators_state.bollinger_lower is None):
            return 0.5
        
        try:
            current_price = self.metadata.get('current_price', 0)
            upper = self.technical_indicators_state.bollinger_upper
            lower = self.technical_indicators_state.bollinger_lower
            
            if upper <= lower:
                return 0.5
            
            position = (current_price - lower) / (upper - lower)
            return max(0, min(1, position))
        except:
            return 0.5

# ==================== 智能觸發引擎核心類 ====================

class IntelligentTriggerEngine:
    """智能觸發引擎"""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        
        # 運行狀態
        self.is_running = False
        self.scan_interval = self.config['trigger_engine']['scan_interval_seconds']
        
        # 數據快取
        self.price_cache = {}  # symbol -> deque of PriceData
        self.indicator_cache = {}  # symbol -> TechnicalIndicatorState
        self.trigger_history = deque(maxlen=1000)
        self.signal_rate_limiter = defaultdict(lambda: deque(maxlen=100))
        
        # 統計
        self.stats = {
            'total_triggers': 0,
            'high_priority_signals': 0,
            'observation_signals': 0,
            'low_priority_signals': 0,
            'convergence_detections': 0,
            'win_rate_predictions': 0
        }
        
        # 訂閱者
        self.signal_subscribers = []
        
        # 任務
        self.engine_tasks = []
        
        # 勝率預測模型 (簡化版)
        self.win_rate_model = None
        
        logger.info("智能觸發引擎初始化完成")
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """載入配置"""
        if config_path is None:
            config_path = "/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/intelligent_trigger_engine/intelligent_trigger_config.json"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"配置載入失敗: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """預設配置"""
        return {
            "trigger_engine": {
                "scan_interval_seconds": 1,
                "parallel_processing": True,
                "max_concurrent_triggers": 10
            },
            "signal_classification": {
                "high_priority": {
                    "win_rate_threshold": 0.75,
                    "minimum_confidence": 0.80,
                    "required_confirmations": 3,
                    "max_signals_per_hour": 5
                },
                "observation": {
                    "win_rate_range": [0.40, 0.75],
                    "minimum_confidence": 0.60,
                    "required_confirmations": 2,
                    "max_signals_per_hour": 15
                }
            },
            "technical_indicators": {
                "rsi": {"period": 14, "oversold": 30, "overbought": 70, "weight": 0.25},
                "macd": {"fast_period": 12, "slow_period": 26, "signal_period": 9, "weight": 0.25},
                "bollinger_bands": {"period": 20, "std_dev": 2, "weight": 0.20},
                "volume_analysis": {"sma_period": 20, "spike_multiplier": 2.0, "weight": 0.15},
                "support_resistance": {"lookback_periods": 50, "proximity_percent": 0.2, "weight": 0.15}
            },
            "trigger_conditions": {
                "price_momentum": {
                    "1min_threshold": 0.005,
                    "5min_threshold": 0.02,
                    "15min_threshold": 0.05
                },
                "indicator_convergence": {
                    "minimum_indicators": 3,
                    "convergence_score_threshold": 0.75
                }
            }
        }
    
    async def start_engine(self):
        """啟動智能觸發引擎"""
        if self.is_running:
            logger.warning("智能觸發引擎已在運行")
            return
        
        try:
            logger.info("啟動智能觸發引擎...")
            
            # 初始化數據結構
            self._initialize_data_structures()
            
            # 啟動核心任務
            self.engine_tasks = [
                asyncio.create_task(self._trigger_scan_loop()),
                asyncio.create_task(self._convergence_detector()),
                asyncio.create_task(self._win_rate_updater()),
                asyncio.create_task(self._performance_monitor())
            ]
            
            self.is_running = True
            logger.info("✅ 智能觸發引擎啟動成功")
            
        except Exception as e:
            logger.error(f"智能觸發引擎啟動失敗: {e}")
            await self.stop_engine()
    
    async def stop_engine(self):
        """停止智能觸發引擎"""
        logger.info("停止智能觸發引擎...")
        
        self.is_running = False
        
        # 取消所有任務
        for task in self.engine_tasks:
            if not task.done():
                task.cancel()
        
        self.engine_tasks.clear()
        logger.info("✅ 智能觸發引擎已停止")
    
    def _initialize_data_structures(self):
        """初始化數據結構"""
        symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT"]
        
        for symbol in symbols:
            self.price_cache[symbol] = deque(maxlen=1000)  # 保存最近1000個價格點
            self.indicator_cache[symbol] = TechnicalIndicatorState()
    
    async def process_price_update(self, symbol: str, price: float, volume: float):
        """處理價格更新"""
        try:
            timestamp = datetime.now()
            
            # 計算價格變化
            price_changes = self._calculate_price_changes(symbol, price)
            
            # 創建價格數據
            price_data = PriceData(
                symbol=symbol,
                price=price,
                volume=volume,
                timestamp=timestamp,
                price_change_1min=price_changes.get('1min', 0.0),
                price_change_5min=price_changes.get('5min', 0.0),
                price_change_15min=price_changes.get('15min', 0.0)
            )
            
            # 更新快取
            if symbol not in self.price_cache:
                self.price_cache[symbol] = deque(maxlen=1000)
            
            self.price_cache[symbol].append(price_data)
            
            # 更新技術指標
            await self._update_technical_indicators(symbol)
            
            # 檢查觸發條件
            await self._check_trigger_conditions(symbol, price_data)
            
        except Exception as e:
            logger.error(f"價格更新處理失敗 {symbol}: {e}")
    
    def _calculate_price_changes(self, symbol: str, current_price: float) -> Dict[str, float]:
        """計算價格變化"""
        changes = {}
        
        if symbol not in self.price_cache or len(self.price_cache[symbol]) == 0:
            return changes
        
        now = datetime.now()
        price_history = list(self.price_cache[symbol])
        
        # 計算不同時間框架的價格變化
        for timeframe, minutes in [('1min', 1), ('5min', 5), ('15min', 15)]:
            target_time = now - timedelta(minutes=minutes)
            
            # 找到最接近目標時間的價格
            closest_price = None
            min_diff = float('inf')
            
            for price_data in price_history:
                time_diff = abs((price_data.timestamp - target_time).total_seconds())
                if time_diff < min_diff:
                    min_diff = time_diff
                    closest_price = price_data.price
            
            if closest_price is not None:
                changes[timeframe] = (current_price - closest_price) / closest_price
        
        return changes
    
    async def _update_technical_indicators(self, symbol: str):
        """更新技術指標"""
        try:
            if symbol not in self.price_cache or len(self.price_cache[symbol]) < 50:
                return
            
            # 轉換為 DataFrame
            price_history = list(self.price_cache[symbol])
            df = pd.DataFrame([
                {
                    'close': p.price,
                    'volume': p.volume,
                    'timestamp': p.timestamp
                }
                for p in price_history[-100:]  # 使用最近100個數據點
            ])
            
            if len(df) < 20:
                return
            
            # 計算技術指標
            indicator_state = TechnicalIndicatorState()
            
            # RSI
            if ta is not None:
                rsi = ta.rsi(df['close'], length=14)
                if not rsi.empty:
                    indicator_state.rsi = float(rsi.iloc[-1])
                    indicator_state.rsi_convergence = self._calculate_rsi_convergence(indicator_state.rsi)
            
            # MACD
            if ta is not None:
                macd_data = ta.macd(df['close'])
                if macd_data is not None and len(macd_data.columns) >= 3:
                    indicator_state.macd = float(macd_data.iloc[-1, 0])
                    indicator_state.macd_signal = float(macd_data.iloc[-1, 1])
                    indicator_state.macd_histogram = float(macd_data.iloc[-1, 2])
                    indicator_state.macd_convergence = self._calculate_macd_convergence(
                        indicator_state.macd, indicator_state.macd_signal
                    )
            
            # 布林帶
            if ta is not None:
                bb = ta.bbands(df['close'], length=20)
                if bb is not None and len(bb.columns) >= 3:
                    indicator_state.bollinger_upper = float(bb.iloc[-1, 0])
                    indicator_state.bollinger_middle = float(bb.iloc[-1, 1])
                    indicator_state.bollinger_lower = float(bb.iloc[-1, 2])
                    indicator_state.bollinger_convergence = self._calculate_bollinger_convergence(
                        df['close'].iloc[-1], indicator_state
                    )
            
            # 成交量分析
            volume_sma = df['volume'].rolling(window=20).mean()
            if not volume_sma.empty:
                indicator_state.volume_sma = float(volume_sma.iloc[-1])
                current_volume = df['volume'].iloc[-1]
                indicator_state.volume_spike_ratio = current_volume / indicator_state.volume_sma
                indicator_state.volume_convergence = self._calculate_volume_convergence(
                    indicator_state.volume_spike_ratio
                )
            
            # 支撐阻力
            support_resistance = self._calculate_support_resistance(df['close'])
            indicator_state.support_level = support_resistance.get('support')
            indicator_state.resistance_level = support_resistance.get('resistance')
            indicator_state.support_resistance_convergence = self._calculate_support_resistance_convergence(
                df['close'].iloc[-1], support_resistance
            )
            
            # 計算整體收斂分數
            indicator_state.overall_convergence_score = self._calculate_overall_convergence(indicator_state)
            
            # 更新快取
            self.indicator_cache[symbol] = indicator_state
            
        except Exception as e:
            logger.error(f"技術指標更新失敗 {symbol}: {e}")
    
    def _calculate_rsi_convergence(self, rsi: float) -> float:
        """計算RSI收斂度"""
        if rsi is None:
            return 0.0
        
        # RSI極值區域給予更高收斂度
        if rsi <= 30:
            return min(1.0, (30 - rsi) / 20)  # 超賣區域
        elif rsi >= 70:
            return min(1.0, (rsi - 70) / 20)  # 超買區域
        else:
            return 0.0
    
    def _calculate_macd_convergence(self, macd: float, signal: float) -> float:
        """計算MACD收斂度"""
        if macd is None or signal is None:
            return 0.0
        
        # MACD穿越信號線給予收斂度
        diff = abs(macd - signal)
        if diff < 0.001:  # 非常接近
            return 0.8
        elif diff < 0.005:  # 較接近
            return 0.6
        elif diff < 0.01:  # 一般接近
            return 0.4
        else:
            return 0.0
    
    def _calculate_bollinger_convergence(self, price: float, indicator_state: TechnicalIndicatorState) -> float:
        """計算布林帶收斂度"""
        if (indicator_state.bollinger_upper is None or 
            indicator_state.bollinger_lower is None):
            return 0.0
        
        # 價格接近布林帶邊界給予收斂度
        upper = indicator_state.bollinger_upper
        lower = indicator_state.bollinger_lower
        
        upper_distance = abs(price - upper) / upper
        lower_distance = abs(price - lower) / lower
        
        min_distance = min(upper_distance, lower_distance)
        
        if min_distance < 0.005:  # 非常接近
            return 0.9
        elif min_distance < 0.01:  # 較接近
            return 0.7
        elif min_distance < 0.02:  # 一般接近
            return 0.5
        else:
            return 0.0
    
    def _calculate_volume_convergence(self, spike_ratio: float) -> float:
        """計算成交量收斂度"""
        # 成交量異常給予收斂度
        if spike_ratio >= 2.5:  # 高成交量
            return min(1.0, spike_ratio / 3.0)
        elif spike_ratio <= 0.5:  # 低成交量
            return min(1.0, (0.5 - spike_ratio) * 2)
        else:
            return 0.0
    
    def _calculate_support_resistance(self, prices: pd.Series) -> Dict[str, float]:
        """計算支撐阻力位"""
        try:
            recent_prices = prices.tail(50)
            
            # 簡化的支撐阻力計算
            support = recent_prices.min()
            resistance = recent_prices.max()
            
            return {
                'support': float(support),
                'resistance': float(resistance)
            }
        except:
            return {'support': None, 'resistance': None}
    
    def _calculate_support_resistance_convergence(self, current_price: float, sr_levels: Dict[str, float]) -> float:
        """計算支撐阻力收斂度"""
        support = sr_levels.get('support')
        resistance = sr_levels.get('resistance')
        
        if support is None or resistance is None:
            return 0.0
        
        # 價格接近支撐阻力位給予收斂度
        support_distance = abs(current_price - support) / support
        resistance_distance = abs(current_price - resistance) / resistance
        
        min_distance = min(support_distance, resistance_distance)
        
        if min_distance < 0.002:  # 非常接近
            return 0.9
        elif min_distance < 0.005:  # 較接近
            return 0.7
        elif min_distance < 0.01:  # 一般接近
            return 0.5
        else:
            return 0.0
    
    def _calculate_overall_convergence(self, indicator_state: TechnicalIndicatorState) -> float:
        """計算整體收斂分數"""
        weights = self.config['technical_indicators']
        
        total_score = 0.0
        total_weight = 0.0
        
        # 加權計算
        if indicator_state.rsi_convergence > 0:
            total_score += indicator_state.rsi_convergence * weights['rsi']['weight']
            total_weight += weights['rsi']['weight']
        
        if indicator_state.macd_convergence > 0:
            total_score += indicator_state.macd_convergence * weights['macd']['weight']
            total_weight += weights['macd']['weight']
        
        if indicator_state.bollinger_convergence > 0:
            total_score += indicator_state.bollinger_convergence * weights['bollinger_bands']['weight']
            total_weight += weights['bollinger_bands']['weight']
        
        if indicator_state.volume_convergence > 0:
            total_score += indicator_state.volume_convergence * weights['volume_analysis']['weight']
            total_weight += weights['volume_analysis']['weight']
        
        if indicator_state.support_resistance_convergence > 0:
            total_score += indicator_state.support_resistance_convergence * weights['support_resistance']['weight']
            total_weight += weights['support_resistance']['weight']
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    async def _check_trigger_conditions(self, symbol: str, price_data: PriceData):
        """檢查觸發條件"""
        try:
            trigger_conditions = []
            
            # 1. 價格動量觸發
            momentum_triggers = self._check_price_momentum(price_data)
            trigger_conditions.extend(momentum_triggers)
            
            # 2. 指標收斂觸發
            convergence_trigger = self._check_indicator_convergence(symbol)
            if convergence_trigger:
                trigger_conditions.append(convergence_trigger)
            
            # 3. 成交量確認觸發
            volume_trigger = self._check_volume_confirmation(price_data)
            if volume_trigger:
                trigger_conditions.append(volume_trigger)
            
            # 4. 支撐阻力事件觸發
            sr_trigger = self._check_support_resistance_events(symbol, price_data.price)
            if sr_trigger:
                trigger_conditions.append(sr_trigger)
            
            # 處理觸發條件
            for condition in trigger_conditions:
                await self._process_trigger_condition(symbol, condition, price_data)
                
        except Exception as e:
            logger.error(f"觸發條件檢查失敗 {symbol}: {e}")
    
    def _check_price_momentum(self, price_data: PriceData) -> List[TriggerCondition]:
        """檢查價格動量觸發"""
        conditions = []
        thresholds = self.config['trigger_conditions']['price_momentum']
        
        # 1分鐘動量
        if abs(price_data.price_change_1min) >= thresholds['1min_threshold']:
            conditions.append(TriggerCondition(
                reason=TriggerReason.PRICE_MOMENTUM_1MIN,
                priority=SignalPriority.HIGH,
                confidence_score=min(1.0, abs(price_data.price_change_1min) / thresholds['1min_threshold']),
                metadata={'price_change': price_data.price_change_1min}
            ))
        
        # 5分鐘動量
        if abs(price_data.price_change_5min) >= thresholds['5min_threshold']:
            conditions.append(TriggerCondition(
                reason=TriggerReason.PRICE_MOMENTUM_5MIN,
                priority=SignalPriority.CRITICAL,
                confidence_score=min(1.0, abs(price_data.price_change_5min) / thresholds['5min_threshold']),
                metadata={'price_change': price_data.price_change_5min}
            ))
        
        # 15分鐘動量
        if abs(price_data.price_change_15min) >= thresholds['15min_threshold']:
            conditions.append(TriggerCondition(
                reason=TriggerReason.PRICE_MOMENTUM_15MIN,
                priority=SignalPriority.MEDIUM,
                confidence_score=min(1.0, abs(price_data.price_change_15min) / thresholds['15min_threshold']),
                metadata={'price_change': price_data.price_change_15min}
            ))
        
        return conditions
    
    def _check_indicator_convergence(self, symbol: str) -> Optional[TriggerCondition]:
        """檢查指標收斂觸發"""
        if symbol not in self.indicator_cache:
            return None
        
        indicator_state = self.indicator_cache[symbol]
        convergence_config = self.config['trigger_conditions']['indicator_convergence']
        
        if indicator_state.overall_convergence_score >= convergence_config['convergence_score_threshold']:
            return TriggerCondition(
                reason=TriggerReason.INDICATOR_CONVERGENCE,
                priority=SignalPriority.HIGH,
                confidence_score=indicator_state.overall_convergence_score,
                metadata={
                    'rsi_convergence': indicator_state.rsi_convergence,
                    'macd_convergence': indicator_state.macd_convergence,
                    'bollinger_convergence': indicator_state.bollinger_convergence,
                    'volume_convergence': indicator_state.volume_convergence,
                    'sr_convergence': indicator_state.support_resistance_convergence
                }
            )
        
        return None
    
    def _check_volume_confirmation(self, price_data: PriceData) -> Optional[TriggerCondition]:
        """檢查成交量確認觸發"""
        if price_data.symbol not in self.indicator_cache:
            return None
        
        indicator_state = self.indicator_cache[price_data.symbol]
        
        if indicator_state.volume_spike_ratio >= 2.0:  # 成交量暴增
            return TriggerCondition(
                reason=TriggerReason.VOLUME_CONFIRMATION,
                priority=SignalPriority.MEDIUM,
                confidence_score=min(1.0, indicator_state.volume_spike_ratio / 3.0),
                metadata={'volume_spike_ratio': indicator_state.volume_spike_ratio}
            )
        
        return None
    
    def _check_support_resistance_events(self, symbol: str, current_price: float) -> Optional[TriggerCondition]:
        """檢查支撐阻力事件觸發"""
        if symbol not in self.indicator_cache:
            return None
        
        indicator_state = self.indicator_cache[symbol]
        
        if indicator_state.support_resistance_convergence >= 0.7:
            return TriggerCondition(
                reason=TriggerReason.SUPPORT_RESISTANCE_EVENT,
                priority=SignalPriority.HIGH,
                confidence_score=indicator_state.support_resistance_convergence,
                metadata={
                    'current_price': current_price,
                    'support_level': indicator_state.support_level,
                    'resistance_level': indicator_state.resistance_level
                }
            )
        
        return None
    
    async def _process_trigger_condition(self, symbol: str, condition: TriggerCondition, price_data: PriceData):
        """處理觸發條件"""
        try:
            # 檢查速率限制
            if not self._check_rate_limit(symbol, condition.priority):
                logger.debug(f"速率限制: {symbol} {condition.reason.value}")
                return
            
            # 預測勝率
            win_rate_prediction = self._predict_win_rate(symbol, condition, price_data)
            
            # 分類信號
            signal_class = self._classify_signal(win_rate_prediction.predicted_win_rate, condition.confidence_score)
            
            if signal_class is None:
                return
            
            # 評估市場條件
            market_conditions = self._assess_market_conditions(symbol, price_data)
            
            # 風險評估
            risk_assessment = self._assess_risk(symbol, condition, price_data)
            
            # 創建智能信號
            intelligent_signal = IntelligentSignal(
                symbol=symbol,
                trigger_reason=condition.reason,
                priority=condition.priority,
                confidence_score=condition.confidence_score,
                win_rate_prediction=win_rate_prediction,
                technical_indicators_state=self.indicator_cache.get(symbol, TechnicalIndicatorState()),
                market_conditions=market_conditions,
                risk_assessment=risk_assessment,
                timestamp=datetime.now(),
                metadata={
                    'current_price': price_data.price,
                    'signal_classification': signal_class,
                    **condition.metadata
                }
            )
            
            # 記錄觸發歷史
            self.trigger_history.append({
                'timestamp': datetime.now(),
                'symbol': symbol,
                'trigger_reason': condition.reason.value,
                'priority': condition.priority.value,
                'confidence': condition.confidence_score,
                'win_rate_prediction': win_rate_prediction.predicted_win_rate
            })
            
            # 更新統計
            self._update_trigger_stats(signal_class)
            
            # 通知訂閱者
            await self._notify_signal_subscribers(intelligent_signal)
            
            logger.info(f"🎯 智能觸發: {symbol} {condition.reason.value} | 勝率: {win_rate_prediction.predicted_win_rate:.2%} | 信心: {condition.confidence_score:.2f}")
            
        except Exception as e:
            logger.error(f"觸發條件處理失敗: {e}")
    
    def _check_rate_limit(self, symbol: str, priority: SignalPriority) -> bool:
        """檢查速率限制"""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        # 清理舊記錄
        key = f"{symbol}_{priority.value}"
        self.signal_rate_limiter[key] = deque([
            ts for ts in self.signal_rate_limiter[key] if ts > hour_ago
        ], maxlen=100)
        
        # 檢查限制
        config = self.config['signal_classification']
        
        if priority == SignalPriority.CRITICAL or priority == SignalPriority.HIGH:
            limit = config['high_priority']['max_signals_per_hour']
        else:
            limit = config['observation']['max_signals_per_hour']
        
        if len(self.signal_rate_limiter[key]) >= limit:
            return False
        
        # 記錄當前時間
        self.signal_rate_limiter[key].append(now)
        return True
    
    def _predict_win_rate(self, symbol: str, condition: TriggerCondition, price_data: PriceData) -> WinRatePrediction:
        """預測勝率 (簡化版)"""
        # 基礎勝率 (基於歷史經驗)
        base_win_rates = {
            TriggerReason.PRICE_MOMENTUM_1MIN: 0.65,
            TriggerReason.PRICE_MOMENTUM_5MIN: 0.72,
            TriggerReason.PRICE_MOMENTUM_15MIN: 0.58,
            TriggerReason.INDICATOR_CONVERGENCE: 0.78,
            TriggerReason.VOLUME_CONFIRMATION: 0.62,
            TriggerReason.SUPPORT_RESISTANCE_EVENT: 0.75,
            TriggerReason.PERIODIC_CHECK: 0.55
        }
        
        base_rate = base_win_rates.get(condition.reason, 0.60)
        
        # 根據信心分數調整
        confidence_adjustment = (condition.confidence_score - 0.5) * 0.2
        
        # 根據技術指標收斂度調整
        if symbol in self.indicator_cache:
            convergence_adjustment = self.indicator_cache[symbol].overall_convergence_score * 0.15
        else:
            convergence_adjustment = 0
        
        # 計算最終勝率
        predicted_rate = base_rate + confidence_adjustment + convergence_adjustment
        predicted_rate = max(0.3, min(0.95, predicted_rate))  # 限制在合理範圍
        
        # 簡化的信心區間
        confidence_width = 0.1 * (1 - condition.confidence_score)
        confidence_interval = (
            max(0, predicted_rate - confidence_width),
            min(1, predicted_rate + confidence_width)
        )
        
        return WinRatePrediction(
            predicted_win_rate=predicted_rate,
            confidence_interval=confidence_interval,
            sample_size=50,  # 模擬樣本大小
            historical_performance={
                'last_30_days': predicted_rate * 0.95,
                'last_7_days': predicted_rate * 1.02,
                'similar_conditions': predicted_rate * 0.98
            }
        )
    
    def _classify_signal(self, predicted_win_rate: float, confidence_score: float) -> Optional[str]:
        """分類信號"""
        high_priority_config = self.config['signal_classification']['high_priority']
        observation_config = self.config['signal_classification']['observation']
        
        # 高優先級信號
        if (predicted_win_rate >= high_priority_config['win_rate_threshold'] and 
            confidence_score >= high_priority_config['minimum_confidence']):
            return 'high_priority'
        
        # 觀察信號
        win_rate_range = observation_config['win_rate_range']
        if (win_rate_range[0] <= predicted_win_rate <= win_rate_range[1] and 
            confidence_score >= observation_config['minimum_confidence']):
            return 'observation'
        
        # 低優先級信號
        if predicted_win_rate >= 0.40:
            return 'low_priority'
        
        return None  # 不生成信號
    
    def _assess_market_conditions(self, symbol: str, price_data: PriceData) -> List[MarketCondition]:
        """評估市場條件"""
        conditions = []
        
        # 簡化的市場條件評估
        if abs(price_data.price_change_5min) > 0.03:
            conditions.append(MarketCondition.HIGH_VOLATILITY)
        elif abs(price_data.price_change_5min) < 0.005:
            conditions.append(MarketCondition.LOW_VOLATILITY)
        
        if price_data.price_change_15min > 0.02:
            conditions.append(MarketCondition.TREND_BULLISH)
        elif price_data.price_change_15min < -0.02:
            conditions.append(MarketCondition.TREND_BEARISH)
        else:
            conditions.append(MarketCondition.RANGING)
        
        return conditions
    
    def _assess_risk(self, symbol: str, condition: TriggerCondition, price_data: PriceData) -> Dict[str, float]:
        """風險評估"""
        risk_score = 0.5  # 基礎風險
        
        # 根據波動性調整風險
        if abs(price_data.price_change_5min) > 0.05:
            risk_score += 0.3  # 高波動性增加風險
        
        # 根據成交量調整風險
        if symbol in self.indicator_cache:
            volume_ratio = self.indicator_cache[symbol].volume_spike_ratio
            if volume_ratio < 0.5:
                risk_score += 0.2  # 低成交量增加風險
            elif volume_ratio > 3.0:
                risk_score += 0.1  # 極高成交量輕微增加風險
        
        # 根據觸發原因調整風險
        risk_adjustments = {
            TriggerReason.PRICE_MOMENTUM_1MIN: 0.1,
            TriggerReason.PRICE_MOMENTUM_5MIN: -0.1,
            TriggerReason.INDICATOR_CONVERGENCE: -0.2,
            TriggerReason.SUPPORT_RESISTANCE_EVENT: -0.15
        }
        
        risk_score += risk_adjustments.get(condition.reason, 0)
        risk_score = max(0.1, min(0.9, risk_score))
        
        return {
            'overall_risk_score': risk_score,
            'volatility_risk': min(0.9, abs(price_data.price_change_5min) * 10),
            'liquidity_risk': max(0.1, 1 - self.indicator_cache.get(symbol, TechnicalIndicatorState()).volume_spike_ratio / 2),
            'technical_risk': 1 - condition.confidence_score
        }
    
    def _update_trigger_stats(self, signal_class: str):
        """更新觸發統計"""
        self.stats['total_triggers'] += 1
        
        if signal_class == 'high_priority':
            self.stats['high_priority_signals'] += 1
        elif signal_class == 'observation':
            self.stats['observation_signals'] += 1
        elif signal_class == 'low_priority':
            self.stats['low_priority_signals'] += 1
    
    async def _notify_signal_subscribers(self, signal: IntelligentSignal):
        """通知信號訂閱者"""
        unified_signal = signal.to_unified_signal_format()
        
        for subscriber in self.signal_subscribers:
            try:
                if asyncio.iscoroutinefunction(subscriber):
                    await subscriber(unified_signal)
                else:
                    subscriber(unified_signal)
            except Exception as e:
                logger.error(f"信號訂閱者通知失敗: {e}")
    
    def subscribe_to_signals(self, callback: Callable):
        """訂閱智能信號"""
        if callback not in self.signal_subscribers:
            self.signal_subscribers.append(callback)
            logger.info(f"新增智能信號訂閱者: {callback.__name__}")
    
    async def _trigger_scan_loop(self):
        """觸發掃描循環"""
        while self.is_running:
            try:
                # 週期性檢查 (每5分鐘)
                for symbol in self.price_cache.keys():
                    if len(self.price_cache[symbol]) > 0:
                        latest_price = self.price_cache[symbol][-1]
                        
                        # 週期性觸發檢查
                        periodic_condition = TriggerCondition(
                            reason=TriggerReason.PERIODIC_CHECK,
                            priority=SignalPriority.LOW,
                            confidence_score=0.5,
                            metadata={'check_type': 'periodic'}
                        )
                        
                        # 只有在滿足基本條件時才處理週期性檢查
                        if symbol in self.indicator_cache:
                            convergence_score = self.indicator_cache[symbol].overall_convergence_score
                            if convergence_score > 0.3:  # 只有在有一定收斂度時才觸發
                                await self._process_trigger_condition(symbol, periodic_condition, latest_price)
                
                await asyncio.sleep(self.scan_interval)
                
            except Exception as e:
                logger.error(f"觸發掃描循環錯誤: {e}")
                await asyncio.sleep(5)
    
    async def _convergence_detector(self):
        """收斂檢測器"""
        while self.is_running:
            try:
                for symbol in self.indicator_cache.keys():
                    indicator_state = self.indicator_cache[symbol]
                    
                    if indicator_state.overall_convergence_score > 0.8:
                        self.stats['convergence_detections'] += 1
                        logger.debug(f"高收斂檢測: {symbol} 分數: {indicator_state.overall_convergence_score:.3f}")
                
                await asyncio.sleep(30)  # 每30秒檢查一次
                
            except Exception as e:
                logger.error(f"收斂檢測器錯誤: {e}")
                await asyncio.sleep(60)
    
    async def _win_rate_updater(self):
        """勝率更新器"""
        while self.is_running:
            try:
                # 這裡可以實現更複雜的勝率模型更新邏輯
                self.stats['win_rate_predictions'] += len(self.trigger_history)
                
                await asyncio.sleep(3600)  # 每小時更新一次
                
            except Exception as e:
                logger.error(f"勝率更新器錯誤: {e}")
                await asyncio.sleep(3600)
    
    async def _performance_monitor(self):
        """性能監控"""
        while self.is_running:
            try:
                logger.info(f"📊 智能觸發引擎統計: {self.stats}")
                
                await asyncio.sleep(300)  # 每5分鐘報告一次
                
            except Exception as e:
                logger.error(f"性能監控錯誤: {e}")
                await asyncio.sleep(300)
    
    async def get_engine_status(self) -> Dict[str, Any]:
        """獲取引擎狀態"""
        return {
            'is_running': self.is_running,
            'statistics': self.stats.copy(),
            'cached_symbols': list(self.price_cache.keys()),
            'recent_triggers': list(self.trigger_history)[-10:],
            'configuration': {
                'scan_interval': self.scan_interval,
                'signal_classification': self.config['signal_classification']
            }
        }

# ==================== 全局實例和便捷函數 ====================

# 全局智能觸發引擎實例
intelligent_trigger_engine = IntelligentTriggerEngine()

async def start_intelligent_trigger_engine():
    """啟動智能觸發引擎"""
    await intelligent_trigger_engine.start_engine()

async def stop_intelligent_trigger_engine():
    """停止智能觸發引擎"""
    await intelligent_trigger_engine.stop_engine()

def subscribe_to_intelligent_signals(callback: Callable):
    """訂閱智能信號"""
    intelligent_trigger_engine.subscribe_to_signals(callback)

async def process_realtime_price_update(symbol: str, price: float, volume: float):
    """處理實時價格更新"""
    await intelligent_trigger_engine.process_price_update(symbol, price, volume)

async def get_intelligent_trigger_status() -> Dict[str, Any]:
    """獲取智能觸發引擎狀態"""
    return await intelligent_trigger_engine.get_engine_status()
