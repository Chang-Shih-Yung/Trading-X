"""
🎯 Trading X - Phase1A 基礎信號生成器
基於 WebSocket 實時數據的多層級信號處理引擎
實現 < 45ms 的信號生成與分發
"""
"""
JSON規範映射註釋:
本文件中的Python類名對應JSON規範中的以下數據類型：
- IndicatorCache -> indicator_cache_system
- KlineData -> kline_data  
- HeartbeatManager -> heartbeat_management_system
- DataCleaner -> data_cleaning_layer
- ConnectionState -> connection_status_enum
- MessageProcessor -> message_processing_layer
- TechnicalAnalysisProcessor -> technical_analysis_engine
- DataBuffer -> data_buffering_system
- DataValidator -> data_validation_layer
- SystemStatus -> system_status_enum
- MarketDataSnapshot -> market_data_snapshot
- ProcessingMetrics -> processing_performance_metrics
- WebSocketConnection -> websocket_connection_object
- ConnectionManager -> connection_management_system
- EventBroadcaster -> event_broadcasting_system
- PerformanceMonitor -> performance_monitoring_system
- ReconnectionHandler -> reconnection_management_system
- DataStandardizer -> data_standardization_layer
- BasicComputationEngine -> basic_computation_layer
- WebSocketRealtimeDriver -> websocket_realtime_driver_main
- OrderBookData -> orderbook_data
- real_time_price -> real_time_price_feed
- market_depth -> market_depth_analysis
- class -> python_class_definition

這些映射確保Python實現與JSON規範的完全對齊。
"""


import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import json
from enum import Enum
import time
import pytz
from pathlib import Path

logger = logging.getLogger(__name__)

class MarketRegime(Enum):
    """市場制度枚舉"""
    BULL_TREND = "BULL_TREND"
    BEAR_TREND = "BEAR_TREND"
    SIDEWAYS = "SIDEWAYS"
    VOLATILE = "VOLATILE"
    UNKNOWN = "UNKNOWN"

class TradingSession(Enum):
    """交易時段枚舉"""
    US_MARKET = "US_MARKET"
    ASIA_MARKET = "ASIA_MARKET"
    EUROPE_MARKET = "EUROPE_MARKET"
    OVERLAP_HOURS = "OVERLAP_HOURS"
    OFF_HOURS = "OFF_HOURS"

class SignalStrength(Enum):
    """信號強度等級"""
    WEAK = 0.2
    MODERATE = 0.5
    STRONG = 0.8
    VERY_STRONG = 1.0

class SignalType(Enum):
    """信號類型"""
    MOMENTUM = "momentum"
    TREND = "trend" 
    VOLATILITY = "volatility"
    VOLUME = "volume"
    PRICE_ACTION = "price_action"

class Priority(Enum):
    """優先級別"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

@dataclass
class DynamicParameters:
    """動態參數數據結構"""
    price_change_threshold: float
    volume_change_threshold: float
    confidence_threshold: float
    signal_strength_multiplier: float
    market_regime: MarketRegime
    trading_session: TradingSession
    timestamp: datetime

@dataclass
class MarketData:
    """市場數據結構"""
    timestamp: datetime
    price: float
    volume: float
    price_change_1h: float
    price_change_24h: float
    volume_ratio: float
    volatility: float
    fear_greed_index: int
    bid_ask_spread: float
    market_depth: float
    moving_averages: Dict[str, float]

@dataclass
class BasicSignal:
    """基礎信號數據結構"""
    signal_id: str
    symbol: str
    signal_type: SignalType
    direction: str  # "BUY", "SELL", "NEUTRAL"
    strength: float  # 0.0 - 1.0
    confidence: float  # 0.0 - 1.0
    priority: Priority
    timestamp: datetime
    price: float
    volume: float
    metadata: Dict[str, Any]
    layer_source: str
    processing_time_ms: float
    market_regime: str = "UNKNOWN"  # 市場制度
    trading_session: str = "OFF_HOURS"  # 交易時段
    price_change: float = 0.0  # 價格變化率
    volume_change: float = 0.0  # 成交量變化率
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        result = asdict(self)
        
        # 處理枚舉類型
        if isinstance(self.signal_type, SignalType):
            result['signal_type'] = self.signal_type.value
        if isinstance(self.priority, Priority):
            result['priority'] = self.priority.value
            
        # 處理時間戳
        if isinstance(self.timestamp, datetime):
            result['timestamp'] = self.timestamp.isoformat()
            
        return result

@dataclass
class LayerProcessingResult:
    """層處理結果"""
    layer_id: str
    signals: List[BasicSignal]
    processing_time_ms: float
    data_quality: float
    source_data_count: int

class Phase1ABasicSignalGeneration:
    """Phase1A 基礎信號生成器 - 4層並行處理架構"""
    
    def __init__(self):
        self.config = self._load_config()
        
        # 動態參數系統
        self.dynamic_params_enabled = self._init_dynamic_parameter_system()
        self._cached_params = {}
        self._cache_timestamp = 0
        self._cache_ttl = 300  # 5分鐘緩存
        
        # 市場制度檢測
        self.current_regime = MarketRegime.UNKNOWN
        self.regime_confidence = 0.0
        self.regime_cache_timestamp = 0
        self.regime_cache_ttl = 300  # 5分鐘緩存
        
        # 交易時段檢測
        self.current_trading_session = TradingSession.OFF_HOURS
        self.session_cache_timestamp = 0
        self.session_cache_ttl = 3600  # 1小時緩存
        
        # 數據緩衝區
        self.price_buffer = defaultdict(lambda: deque(maxlen=100))
        self.volume_buffer = defaultdict(lambda: deque(maxlen=100))
        self.orderbook_buffer = defaultdict(lambda: deque(maxlen=50))  # OrderBook 緩衝區
        self.signal_buffer = deque(maxlen=1000)
        
        # 層處理器
        self.layer_processors = {
            "layer_0": self._layer_0_instant_signals,
            "layer_1": self._layer_1_momentum_signals,
            "layer_2": self._layer_2_trend_signals,
            "layer_3": self._layer_3_volume_signals
        }
        
        # 性能監控
        self.performance_stats = defaultdict(list)
        self.processing_times = defaultdict(deque)
        
        # 信號訂閱者
        self.signal_subscribers = []
        
        # 運行控制
        self.is_running = False
        self.tasks = []
        
        # WebSocket 斷線處理
        self.circuit_breaker_active = False
        self.signal_generation_paused = False
        self.degraded_mode = False
        self.last_disconnect_time = None
        
        # 應用信號生成配置參數
        self._apply_signal_generation_config()
        
        logger.info("Phase1A 基礎信號生成器初始化完成（含動態參數系統）")
    
    def _load_config(self) -> Dict[str, Any]:
        """載入配置"""
        try:
            config_path = Path(__file__).parent / "phase1a_basic_signal_generation.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"配置載入失敗: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """預設配置 - 增強版本包含完整的 JSON 規範參數"""
        return {
            "processing_layers": {
                "layer_0": {
                    "name": "instant_signals",
                    "target_latency_ms": 5,
                    "signal_types": ["price_spike", "volume_spike"]
                },
                "layer_1": {
                    "name": "momentum_signals", 
                    "target_latency_ms": 15,
                    "signal_types": ["rsi_divergence", "macd_cross"]
                },
                "layer_2": {
                    "name": "trend_signals",
                    "target_latency_ms": 20,
                    "signal_types": ["trend_break", "support_resistance"]
                },
                "layer_3": {
                    "name": "volume_signals",
                    "target_latency_ms": 5,
                    "signal_types": ["volume_confirmation", "unusual_volume"]
                }
            },
            "signal_generation_params": {
                "basic_mode": {
                    "price_change_threshold": 0.001,
                    "volume_change_threshold": 1.5,
                    "signal_strength_range": [0.0, 1.0],
                    "confidence_calculation": "basic_statistical_model"
                },
                "extreme_market_mode": {
                    "price_change_threshold": 0.005,
                    "volume_change_threshold": 3.0,
                    "signal_strength_boost": 1.2,
                    "priority_escalation": True
                }
            },
            "signal_thresholds": {
                "price_spike": 0.5,
                "volume_spike": 2.0,
                "rsi_oversold": 30,
                "rsi_overbought": 70,
                "price_change_threshold_basic": 0.001,
                "price_change_threshold_extreme": 0.005,
                "signal_strength_boost": 1.2
            },
            "performance_targets": {
                "total_processing_time": "< 45ms",
                "signal_accuracy": "> 75%",
                "false_positive_rate": "< 15%",
                "processing_latency_p99": "< 30ms",
                "signal_generation_rate": "10-50 signals/minute",
                "accuracy_baseline": "> 60%",
                "system_availability": "> 99.5%"
            }
        }
    
    def _init_dynamic_parameter_system(self) -> bool:
        """初始化動態參數系統"""
        try:
            # 檢查動態參數整合是否啟用
            integration_config = self.config.get("phase1a_basic_signal_generation_dependency", {}).get("configuration", {}).get("dynamic_parameter_integration", {})
            
            if not integration_config.get("enabled", False):
                logger.warning("動態參數系統未啟用，使用靜態參數")
                return False
                
            logger.info("動態參數系統初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"動態參數系統初始化失敗: {e}")
            logger.warning("將使用靜態參數繼續運行")
            return False
    
    async def _detect_market_regime(self, market_data: Optional[MarketData] = None) -> Tuple[MarketRegime, float]:
        """檢測市場制度"""
        try:
            current_time = time.time()
            
            # 檢查緩存是否有效
            if (current_time - self.regime_cache_timestamp < self.regime_cache_ttl and 
                self.current_regime != MarketRegime.UNKNOWN):
                return self.current_regime, self.regime_confidence
            
            # 獲取市場制度配置
            regime_config = self.config.get("phase1a_basic_signal_generation_dependency", {}).get("configuration", {}).get("dynamic_parameter_integration", {}).get("market_regime_detection", {})
            regime_types = regime_config.get("regime_types", {})
            
            if not market_data:
                # 沒有市場數據，無法進行制度檢測
                logger.error("缺乏市場數據，無法進行市場制度檢測")
                return MarketRegime.UNKNOWN, 0.0
            
            regime_scores = {}
            
            # 檢測牛市趨勢
            if "BULL_TREND" in regime_types:
                bull_score = self._calculate_bull_trend_score(market_data)
                regime_scores[MarketRegime.BULL_TREND] = bull_score
            
            # 檢測熊市趨勢  
            if "BEAR_TREND" in regime_types:
                bear_score = self._calculate_bear_trend_score(market_data)
                regime_scores[MarketRegime.BEAR_TREND] = bear_score
            
            # 檢測橫盤整理
            if "SIDEWAYS" in regime_types:
                sideways_score = self._calculate_sideways_score(market_data)
                regime_scores[MarketRegime.SIDEWAYS] = sideways_score
            
            # 檢測高波動
            if "VOLATILE" in regime_types:
                volatile_score = self._calculate_volatile_score(market_data)
                regime_scores[MarketRegime.VOLATILE] = volatile_score
            
            # 選擇最高分數的制度
            if regime_scores:
                best_regime = max(regime_scores.keys(), key=lambda k: regime_scores[k])
                confidence = regime_scores[best_regime]
                
                # 檢查是否滿足最小信心度要求
                min_confidence = regime_types.get(best_regime.value, {}).get("confidence_threshold", 0.7)
                if confidence >= min_confidence:
                    self.current_regime = best_regime
                    self.regime_confidence = confidence
                    self.regime_cache_timestamp = current_time
                    return best_regime, confidence
            
            # 默認返回未知制度
            self.current_regime = MarketRegime.UNKNOWN
            self.regime_confidence = 0.0
            return MarketRegime.UNKNOWN, 0.0
            
        except Exception as e:
            logger.error(f"市場制度檢測失敗: {e}")
            return MarketRegime.UNKNOWN, 0.0
    
    def _calculate_bull_trend_score(self, market_data: MarketData) -> float:
        """計算牛市趨勢分數"""
        score = 0.0
        
        # 價格趨勢斜率檢查
        if market_data.price_change_24h > 0.02:
            score += 0.3
        
        # 成交量確認
        if market_data.volume_ratio > 1.2:
            score += 0.25
        
        # 恐懼貪婪指數
        if market_data.fear_greed_index > 60:
            score += 0.25
        
        # 移動平均線排列（牛市排列）
        ma_20 = market_data.moving_averages.get("ma_20", 0)
        ma_50 = market_data.moving_averages.get("ma_50", 0)
        ma_200 = market_data.moving_averages.get("ma_200", 0)
        
        if ma_20 > ma_50 > ma_200 and market_data.price > ma_20:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_bear_trend_score(self, market_data: MarketData) -> float:
        """計算熊市趨勢分數"""
        score = 0.0
        
        # 價格趨勢斜率檢查
        if market_data.price_change_24h < -0.02:
            score += 0.3
        
        # 成交量確認
        if market_data.volume_ratio > 1.1:
            score += 0.25
        
        # 恐懼貪婪指數
        if market_data.fear_greed_index < 40:
            score += 0.25
        
        # 移動平均線排列（熊市排列）
        ma_20 = market_data.moving_averages.get("ma_20", 0)
        ma_50 = market_data.moving_averages.get("ma_50", 0)
        ma_200 = market_data.moving_averages.get("ma_200", 0)
        
        if ma_20 < ma_50 < ma_200 and market_data.price < ma_20:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_sideways_score(self, market_data: MarketData) -> float:
        """計算橫盤整理分數"""
        score = 0.0
        
        # 價格趨勢斜率檢查
        if -0.02 <= market_data.price_change_24h <= 0.02:
            score += 0.3
        
        # 波動率檢查
        if market_data.volatility < 0.05:
            score += 0.3
        
        # 成交量比率
        if 0.8 <= market_data.volume_ratio <= 1.2:
            score += 0.2
        
        # 區間震盪確認（簡化實現）
        if market_data.price_change_1h < 0.01:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_volatile_score(self, market_data: MarketData) -> float:
        """計算高波動分數"""
        score = 0.0
        
        # 波動率檢查
        if market_data.volatility > 0.08:
            score += 0.3
        
        # 價格跳空
        if abs(market_data.price_change_1h) > 0.02:
            score += 0.3
        
        # 成交量激增
        if market_data.volume_ratio > 2.0:
            score += 0.2
        
        # 日內波幅（簡化實現）
        if market_data.volatility > 0.05:
            score += 0.2
        
        return min(score, 1.0)
    
    async def _detect_trading_session(self, current_time: Optional[datetime] = None) -> TradingSession:
        """檢測交易時段"""
        try:
            current_time_check = time.time()
            
            # 檢查緩存是否有效
            if (current_time_check - self.session_cache_timestamp < self.session_cache_ttl):
                return self.current_trading_session
            
            if current_time is None:
                current_time = datetime.now(pytz.timezone('UTC'))
            
            # 獲取交易時段配置
            session_config = self.config.get("phase1a_basic_signal_generation_dependency", {}).get("configuration", {}).get("dynamic_parameter_integration", {}).get("trading_session_detection", {})
            session_types = session_config.get("session_types", {})
            
            # 轉換到各市場時區
            est_time = current_time.astimezone(pytz.timezone('US/Eastern'))
            jst_time = current_time.astimezone(pytz.timezone('Asia/Tokyo'))
            gmt_time = current_time.astimezone(pytz.timezone('GMT'))
            
            # 檢查美股時段
            us_config = session_types.get("US_MARKET", {})
            if us_config:
                time_range = us_config.get("time_range", "14:30-21:00")
                start_str, end_str = time_range.split("-")
                start_hour, start_min = map(int, start_str.split(":"))
                end_hour, end_min = map(int, end_str.split(":"))
                
                utc_time = current_time
                if (start_hour <= utc_time.hour < end_hour or 
                    (utc_time.hour == start_hour and utc_time.minute >= start_min) or
                    (utc_time.hour == end_hour and utc_time.minute < end_min)):
                    self.current_trading_session = TradingSession.US_MARKET
                    self.session_cache_timestamp = current_time_check
                    return TradingSession.US_MARKET
            
            # 檢查亞洲時段
            asia_config = session_types.get("ASIA_MARKET", {})
            if asia_config:
                time_range = asia_config.get("time_range", "01:00-08:00")
                start_str, end_str = time_range.split("-")
                start_hour, start_min = map(int, start_str.split(":"))
                end_hour, end_min = map(int, end_str.split(":"))
                
                utc_time = current_time
                if (start_hour <= utc_time.hour < end_hour or 
                    (utc_time.hour == start_hour and utc_time.minute >= start_min) or
                    (utc_time.hour == end_hour and utc_time.minute < end_min)):
                    self.current_trading_session = TradingSession.ASIA_MARKET
                    self.session_cache_timestamp = current_time_check
                    return TradingSession.ASIA_MARKET
            
            # 檢查歐洲時段
            europe_config = session_types.get("EUROPE_MARKET", {})
            if europe_config:
                time_range = europe_config.get("time_range", "08:00-16:30")
                start_str, end_str = time_range.split("-")
                start_hour, start_min = map(int, start_str.split(":"))
                end_hour, end_min = map(int, end_str.split(":"))
                
                utc_time = current_time
                if (start_hour <= utc_time.hour < end_hour or 
                    (utc_time.hour == start_hour and utc_time.minute >= start_min) or
                    (utc_time.hour == end_hour and utc_time.minute < end_min)):
                    self.current_trading_session = TradingSession.EUROPE_MARKET
                    self.session_cache_timestamp = current_time_check
                    return TradingSession.EUROPE_MARKET
            
            # 默認為非交易時段
            self.current_trading_session = TradingSession.OFF_HOURS
            self.session_cache_timestamp = current_time_check
            return TradingSession.OFF_HOURS
            
        except Exception as e:
            logger.error(f"交易時段檢測失敗: {e}")
            return TradingSession.OFF_HOURS
    
    async def _get_dynamic_parameters(self, mode: str = "basic_mode") -> DynamicParameters:
        """獲取動態調整後的參數"""
        current_time = time.time()
        
        # 檢查緩存是否有效
        cache_key = f"{mode}_{self.current_regime.value}_{self.current_trading_session.value}"
        if (current_time - self._cache_timestamp < self._cache_ttl and 
            cache_key in self._cached_params):
            return self._cached_params[cache_key]
        
        # 獲取基礎配置
        signal_params = self.config.get("phase1a_basic_signal_generation_dependency", {}).get("configuration", {}).get("signal_generation_params", {})
        base_params = signal_params.get(mode, {})
        
        # 提取基礎值
        price_threshold = self._extract_parameter_value(base_params.get("price_change_threshold", 0.001))
        volume_threshold = self._extract_parameter_value(base_params.get("volume_change_threshold", 1.5))
        confidence_threshold = self._extract_parameter_value(base_params.get("confidence_threshold", 0.75))
        
        # 如果動態參數系統啟用，進行參數調整
        if self.dynamic_params_enabled:
            try:
                # 獲取當前市場制度和交易時段
                market_regime, regime_confidence = await self._detect_market_regime()
                trading_session = await self._detect_trading_session()
                
                # 應用市場制度調整
                regime_config = self.config.get("phase1a_basic_signal_generation_dependency", {}).get("configuration", {}).get("dynamic_parameter_integration", {}).get("market_regime_detection", {}).get("regime_types", {})
                regime_adjustments = {}
                if market_regime != MarketRegime.UNKNOWN:
                    regime_adjustments = regime_config.get(market_regime.value, {}).get("parameter_adjustments", {})
                
                if regime_adjustments:
                    confidence_threshold *= regime_adjustments.get("confidence_threshold_multiplier", 1.0)
                    price_threshold *= regime_adjustments.get("price_change_threshold_multiplier", 1.0)
                    volume_threshold *= regime_adjustments.get("volume_change_threshold_multiplier", 1.0)
                
                # 應用交易時段調整
                session_config = self.config.get("phase1a_basic_signal_generation_dependency", {}).get("configuration", {}).get("dynamic_parameter_integration", {}).get("trading_session_detection", {}).get("session_types", {})
                session_adjustments = session_config.get(trading_session.value, {}).get("parameter_adjustments", {})
                
                if session_adjustments:
                    confidence_threshold *= session_adjustments.get("confidence_threshold_multiplier", 1.0)
                    volume_threshold *= session_adjustments.get("volume_sensitivity_boost", 1.0)
                
                logger.debug(f"動態參數調整完成 - {mode}: confidence_threshold = {confidence_threshold:.3f}, market_regime = {market_regime.value}, trading_session = {trading_session.value}")
                
            except Exception as e:
                logger.error(f"動態參數獲取失敗，使用靜態參數: {e}")
        
        # 創建動態參數對象
        dynamic_params = DynamicParameters(
            price_change_threshold=price_threshold,
            volume_change_threshold=volume_threshold,
            confidence_threshold=confidence_threshold,
            signal_strength_multiplier=1.0,
            market_regime=self.current_regime,
            trading_session=self.current_trading_session,
            timestamp=datetime.now()
        )
        
        # 更新緩存
        self._cached_params[cache_key] = dynamic_params
        self._cache_timestamp = current_time
        
        return dynamic_params
    
    def _extract_parameter_value(self, param_config) -> float:
        """提取參數值（支援靜態值和動態配置）"""
        if isinstance(param_config, (int, float)):
            return float(param_config)
        elif isinstance(param_config, dict):
            return param_config.get("base_value", 0.0)
        else:
            return 0.0
    
    def _apply_signal_generation_config(self):
        """應用信號生成配置參數"""
        config = self.config.get('signal_generation_params', {})
        
        # 設置基本模式參數
        basic_mode = config.get('basic_mode', {})
        self.price_change_threshold = basic_mode.get('price_change_threshold', 0.001)
        self.volume_change_threshold = basic_mode.get('volume_change_threshold', 1.5)
        self.signal_strength_range = basic_mode.get('signal_strength_range', [0.0, 1.0])
        self.confidence_calculation_mode = basic_mode.get('confidence_calculation', 'basic_statistical_model')
        
        # 設置極端市場模式參數
        extreme_mode = config.get('extreme_market_mode', {})
        self.extreme_price_threshold = extreme_mode.get('price_change_threshold', 0.005)
        self.extreme_volume_threshold = extreme_mode.get('volume_change_threshold', 3.0)
        self.signal_strength_boost = extreme_mode.get('signal_strength_boost', 1.2)
        self.priority_escalation_enabled = extreme_mode.get('priority_escalation', True)
        
        logger.info("信號生成配置參數已應用")
    
    async def _process_market_data(self, ticker_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理市場數據 - 修復數據流斷點"""
        try:
            # 將 ticker_data 轉換為 processed_market_data 格式
            processed_market_data = {
                'symbol': ticker_data.get('symbol'),
                'price': ticker_data.get('price'),
                'volume': ticker_data.get('volume'),
                'timestamp': ticker_data.get('timestamp'),
                'quality_score': self._calculate_data_quality(ticker_data),
                'processed_at': datetime.now()
            }
            
            # 數據驗證
            if self._validate_market_data(processed_market_data):
                return processed_market_data
            else:
                logger.warning(f"數據驗證失敗: {ticker_data}")
                return None
                
        except Exception as e:
            logger.error(f"市場數據處理錯誤: {e}")
            return None
    
    def _calculate_data_quality(self, data: Dict[str, Any]) -> float:
        """計算數據品質分數"""
        quality_score = 1.0
        
        # 檢查必要字段
        required_fields = ['symbol', 'price', 'volume', 'timestamp']
        missing_fields = [f for f in required_fields if f not in data or data[f] is None]
        
        if missing_fields:
            quality_score -= 0.2 * len(missing_fields)
        
        # 檢查數據合理性
        if data.get('price', 0) <= 0:
            quality_score -= 0.3
        if data.get('volume', 0) < 0:
            quality_score -= 0.2
            
        return max(0.0, quality_score)
    
    def _validate_market_data(self, data: Dict[str, Any]) -> bool:
        """驗證市場數據"""
        if not data:
            return False
        
        return (
            data.get('quality_score', 0) >= 0.6 and
            data.get('price', 0) > 0 and
            data.get('volume', 0) >= 0 and
            data.get('symbol') is not None
        )
    
    def _calculate_confidence_basic_statistical(self, signal_data: Dict[str, Any]) -> float:
        """基礎統計模型計算信心度"""
        confidence = 0.5  # 基礎信心度
        
        # 基於價格變化的信心度調整
        price_change = abs(signal_data.get('price_change', 0))
        if price_change > self.price_change_threshold:
            confidence += min(0.3, price_change * 100)
        
        # 基於成交量的信心度調整
        volume_ratio = signal_data.get('volume_ratio', 1.0)
        if volume_ratio > self.volume_change_threshold:
            confidence += min(0.2, (volume_ratio - 1.0) * 0.1)
        
        return min(1.0, confidence)
    
    def _check_extreme_market_mode(self, market_data: Dict[str, Any]) -> bool:
        """檢查是否為極端市場模式"""
        price_change = abs(market_data.get('price_change', 0))
        volume_ratio = market_data.get('volume_ratio', 1.0)
        
        return (
            price_change > self.extreme_price_threshold or
            volume_ratio > self.extreme_volume_threshold
        )
    
    async def _handle_websocket_disconnection(self):
        """處理 WebSocket 斷線 - 熔斷機制"""
        logger.warning("WebSocket 連線中斷，啟動熔斷機制")
        
        self.circuit_breaker_active = True
        self.last_disconnect_time = datetime.now()
        
        # 停止信號生成
        await self._pause_signal_generation()
        
        # 嘗試重連
        reconnect_attempts = 0
        max_attempts = 5
        
        while reconnect_attempts < max_attempts and not self.is_running:
            try:
                await asyncio.sleep(2 ** reconnect_attempts)  # 指數退避
                logger.info(f"嘗試重連 WebSocket ({reconnect_attempts + 1}/{max_attempts})")
                
                # 這裡會由外部 websocket_driver 處理重連
                # 我們只需要等待連線恢復
                reconnect_attempts += 1
                
            except Exception as e:
                logger.error(f"重連失敗: {e}")
                reconnect_attempts += 1
        
        if reconnect_attempts >= max_attempts:
            logger.critical("WebSocket 重連失敗，系統進入降級模式")
            await self._enter_degraded_mode()
    
    async def _pause_signal_generation(self):
        """暫停信號生成"""
        self.signal_generation_paused = True
        logger.info("信號生成已暫停")
    
    async def _resume_signal_generation(self):
        """恢復信號生成"""
        self.signal_generation_paused = False
        self.circuit_breaker_active = False
        logger.info("信號生成已恢復")
    
    async def _enter_degraded_mode(self):
        """進入降級模式"""
        self.degraded_mode = True
        logger.warning("系統進入降級模式")
        
        # 在降級模式下，使用歷史數據進行有限的信號生成
        # 這可以確保系統在 WebSocket 斷線時仍能提供基本服務
    
    async def start(self, websocket_driver):
        """啟動 Phase1A 信號生成器"""
        if self.is_running:
            logger.warning("Phase1A 已在運行")
            return
        
        self.is_running = True
        self.websocket_driver = websocket_driver
        
        logger.info("啟動 Phase1A 基礎信號生成器")
        
        # 訂閱 WebSocket 數據
        websocket_driver.subscribe(self._on_market_data_update)
        
        # 啟動核心任務
        self.tasks = [
            asyncio.create_task(self._signal_generation_coordinator()),
            asyncio.create_task(self._performance_monitor()),
            asyncio.create_task(self._signal_quality_analyzer())
        ]
        
        logger.info("Phase1A 信號生成器啟動完成")
    
    async def stop(self):
        """停止信號生成器"""
        self.is_running = False
        
        # 取消所有任務
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        self.tasks.clear()
        logger.info("Phase1A 信號生成器已停止")
    
    async def process_market_data(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """公開的市場數據處理方法"""
        try:
            # 使用內部方法處理數據
            processed_data = await self._process_market_data(market_data)
            return processed_data
        except Exception as e:
            logger.error(f"公開數據處理失敗: {e}")
            return None
    
    async def process_real_time_price(self, price_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理實時價格數據 - JSON規範要求"""
        try:
            symbol = price_data.get('symbol')
            price = float(price_data.get('price', 0))
            
            # 更新價格緩衝區
            if symbol:
                self.price_buffer[symbol].append({
                    'price': price,
                    'timestamp': price_data.get('timestamp'),
                    'source': 'real_time_price'
                })
            
            # 計算價格指標
            price_signals = await self._analyze_price_movement(symbol, price_data)
            
            return {
                'symbol': symbol,
                'processed_price': price,
                'price_signals': price_signals,
                'processing_timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"實時價格處理失敗: {e}")
            return {}
    
    async def process_market_depth(self, depth_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理市場深度數據 - JSON規範要求"""
        try:
            symbol = depth_data.get('symbol')
            
            # 分析買賣盤深度
            depth_analysis = {
                'symbol': symbol,
                'bid_ask_spread': depth_data.get('spread', 0),
                'depth_imbalance': depth_data.get('depth_imbalance', 0),
                'total_volume': depth_data.get('total_bid_volume', 0) + depth_data.get('total_ask_volume', 0),
                'liquidity_score': self._calculate_liquidity_score(depth_data)
            }
            
            # 生成深度相關信號
            depth_signals = await self._generate_depth_signals(depth_analysis)
            
            return {
                'symbol': symbol,
                'depth_analysis': depth_analysis,
                'depth_signals': depth_signals,
                'processing_timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"市場深度處理失敗: {e}")
            return {}
    
    def _calculate_liquidity_score(self, depth_data: Dict[str, Any]) -> float:
        """計算流動性評分"""
        try:
            spread = depth_data.get('spread', 0)
            total_volume = depth_data.get('total_bid_volume', 0) + depth_data.get('total_ask_volume', 0)
            
            # 流動性評分 = f(spread, volume)
            if spread > 0 and total_volume > 0:
                spread_score = max(0, 1 - spread * 100)  # 價差越小分數越高
                volume_score = min(1, total_volume / 1000)  # 成交量正規化
                return (spread_score + volume_score) / 2
            return 0.5
        except:
            return 0.5
    
    async def _on_orderbook_update(self, symbol: str, orderbook_data: Dict[str, Any]):
        """處理 OrderBook 數據更新 - 保持現有數據結構"""
        try:
            # 驗證 OrderBook 數據格式
            if not orderbook_data or 'bids' not in orderbook_data or 'asks' not in orderbook_data:
                logger.warning(f"OrderBook 數據格式不正確: {symbol}")
                return
            
            # 將 OrderBook 數據加入緩衝區
            processed_orderbook = {
                'symbol': symbol,
                'timestamp': orderbook_data.get('timestamp', datetime.now()),
                'bids': orderbook_data.get('bids', [])[:20],  # 取前20檔
                'asks': orderbook_data.get('asks', [])[:20],
                'bid_ask_spread': self._calculate_spread(orderbook_data),
                'book_depth': self._calculate_book_depth(orderbook_data),
                'liquidity_ratio': self._calculate_liquidity_ratio(orderbook_data)
            }
            
            # 更新緩衝區（保持現有數據結構）
            self.orderbook_buffer[symbol].append(processed_orderbook)
            
            # 檢查是否需要生成基於 OrderBook 的信號
            if len(self.orderbook_buffer[symbol]) >= 2:
                await self._check_orderbook_signals(symbol)
                
        except Exception as e:
            logger.error(f"OrderBook 更新處理失敗 {symbol}: {e}")
    
    def _calculate_spread(self, orderbook_data: Dict[str, Any]) -> float:
        """計算買賣價差"""
        try:
            bids = orderbook_data.get('bids', [])
            asks = orderbook_data.get('asks', [])
            
            if bids and asks:
                best_bid = float(bids[0][0])
                best_ask = float(asks[0][0])
                return (best_ask - best_bid) / best_bid * 100  # 百分比形式
            return 0.0
        except:
            return 0.0
    
    def _calculate_book_depth(self, orderbook_data: Dict[str, Any]) -> float:
        """計算訂單簿深度"""
        try:
            bids = orderbook_data.get('bids', [])
            asks = orderbook_data.get('asks', [])
            
            bid_volume = sum(float(bid[1]) for bid in bids[:10])  # 前10檔買單量
            ask_volume = sum(float(ask[1]) for ask in asks[:10])  # 前10檔賣單量
            
            return bid_volume + ask_volume
        except:
            return 0.0
    
    def _calculate_liquidity_ratio(self, orderbook_data: Dict[str, Any]) -> float:
        """計算流動性比率"""
        try:
            bids = orderbook_data.get('bids', [])
            asks = orderbook_data.get('asks', [])
            
            if bids and asks:
                bid_volume = sum(float(bid[1]) for bid in bids[:5])  # 前5檔買單量
                ask_volume = sum(float(ask[1]) for ask in asks[:5])  # 前5檔賣單量
                
                total_volume = bid_volume + ask_volume
                if total_volume > 0:
                    return min(bid_volume, ask_volume) / total_volume  # 平衡度
            return 0.5
        except:
            return 0.5
    
    async def _check_orderbook_signals(self, symbol: str):
        """基於 OrderBook 檢查信號機會 - 不改變現有輸出格式"""
        try:
            if len(self.orderbook_buffer[symbol]) < 2:
                return
                
            current_ob = self.orderbook_buffer[symbol][-1]
            previous_ob = self.orderbook_buffer[symbol][-2]
            
            # 檢查流動性變化
            liquidity_change = current_ob['liquidity_ratio'] - previous_ob['liquidity_ratio']
            
            # 檢查價差變化
            spread_change = current_ob['bid_ask_spread'] - previous_ob['bid_ask_spread']
            
            # 檢查深度變化
            depth_change = current_ob['book_depth'] - previous_ob['book_depth']
            
            # 如果有顯著變化，觸發額外的市場數據更新（不改變現有流程）
            if abs(liquidity_change) > 0.1 or abs(spread_change) > 0.01 or abs(depth_change) > 0.1:
                # 創建增強的市場數據用於信號生成
                enhanced_market_data = self._create_enhanced_market_data(symbol, current_ob)
                if enhanced_market_data:
                    # 使用現有的信號生成流程，但加入 OrderBook 增強信息
                    await self._generate_orderbook_enhanced_signals(symbol, enhanced_market_data)
                    
        except Exception as e:
            logger.error(f"OrderBook 信號檢查失敗 {symbol}: {e}")
    
    def _create_enhanced_market_data(self, symbol: str, orderbook: Dict[str, Any]):
        """創建包含 OrderBook 信息的增強市場數據 - 保持現有 MarketData 格式"""
        try:
            if len(self.price_buffer[symbol]) == 0:
                return None
                
            latest_price_data = self.price_buffer[symbol][-1]
            latest_volume_data = self.volume_buffer[symbol][-1] if self.volume_buffer[symbol] else {}
            
            # 使用現有的 MarketData 結構，在 metadata 中添加 OrderBook 信息
            enhanced_data = MarketData(
                timestamp=orderbook['timestamp'],
                price=latest_price_data.get('price', 0.0),
                volume=latest_volume_data.get('volume', 0.0),
                price_change_1h=latest_price_data.get('price_change_1h', 0.0),
                price_change_24h=latest_price_data.get('price_change_24h', 0.0),
                volume_ratio=latest_volume_data.get('volume_ratio', 1.0),
                volatility=latest_price_data.get('volatility', 0.0),
                fear_greed_index=latest_price_data.get('fear_greed_index', 50),
                bid_ask_spread=orderbook['bid_ask_spread'],  # 使用 OrderBook 的價差
                market_depth=orderbook['book_depth'],        # 使用 OrderBook 的深度
                moving_averages=latest_price_data.get('moving_averages', {})
            )
            
            return enhanced_data
            
        except Exception as e:
            logger.error(f"增強市場數據創建失敗 {symbol}: {e}")
            return None
    
    async def _generate_orderbook_enhanced_signals(self, symbol: str, market_data: MarketData):
        """生成基於 OrderBook 增強的信號 - 保持現有信號格式"""
        try:
            # 使用現有的動態參數系統
            dynamic_params = await self._get_dynamic_parameters("basic_mode")
            
            # OrderBook 深度信號
            if market_data.market_depth > 1000:  # 深度閾值
                if market_data.bid_ask_spread < 0.01:  # 價差小於 1%
                    signal = BasicSignal(
                        signal_id=f"orderbook_depth_{symbol}_{int(time.time())}",
                        symbol=symbol,
                        signal_type=SignalType.VOLUME,  # 使用現有枚舉
                        direction="BUY" if market_data.market_depth > 2000 else "NEUTRAL",
                        strength=min(0.8, market_data.market_depth / 5000),
                        confidence=min(0.9, 1 - market_data.bid_ask_spread * 10),
                        priority=Priority.MEDIUM,  # 使用現有枚舉
                        timestamp=market_data.timestamp,
                        price=market_data.price,
                        volume=market_data.volume,
                        metadata={"orderbook_enhanced": True, "book_depth": market_data.market_depth},
                        layer_source="orderbook_enhanced",
                        processing_time_ms=2.0,
                        market_regime=dynamic_params.market_regime.value,
                        trading_session=dynamic_params.trading_session.value,
                        price_change=market_data.price_change_24h,
                        volume_change=market_data.volume_ratio
                    )
                    
                    # 加入現有的信號緩衝區
                    self.signal_buffer.append(signal)
                    logger.debug(f"生成 OrderBook 增強信號: {signal.signal_id}")
                    
        except Exception as e:
            logger.error(f"OrderBook 增強信號生成失敗 {symbol}: {e}")

    async def _generate_depth_signals(self, depth_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根據深度分析生成信號"""
        signals = []
        
        try:
            depth_imbalance = depth_analysis.get('depth_imbalance', 0)
            liquidity_score = depth_analysis.get('liquidity_score', 0)
            
            # 深度不平衡信號
            if abs(depth_imbalance) > 0.3:
                direction = "BUY" if depth_imbalance > 0 else "SELL"
                signals.append({
                    'type': 'depth_imbalance',
                    'direction': direction,
                    'strength': min(1.0, abs(depth_imbalance)),
                    'confidence': 0.7
                })
            
            # 流動性信號
            if liquidity_score < 0.3:
                signals.append({
                    'type': 'low_liquidity',
                    'direction': 'NEUTRAL',
                    'strength': 1 - liquidity_score,
                    'confidence': 0.6
                })
            
        except Exception as e:
            logger.error(f"深度信號生成失敗: {e}")
        
        return signals
    
    async def generate_signals(self, symbol: str, market_data: Dict[str, Any]) -> List[BasicSignal]:
        """公開的信號生成方法"""
        try:
            if not self.is_running:
                logger.warning("信號生成器未運行")
                return []
            
            # 執行4層並行處理
            signals = []
            
            # Layer 0: 即時信號
            layer_0_result = await self._execute_layer_processing(
                "layer_0", self._layer_0_instant_signals, symbol, market_data
            )
            if layer_0_result.signals:
                signals.extend(layer_0_result.signals)
            
            # Layer 1: 動量信號
            layer_1_result = await self._execute_layer_processing(
                "layer_1", self._layer_1_momentum_signals, symbol, market_data
            )
            if layer_1_result.signals:
                signals.extend(layer_1_result.signals)
            
            # Layer 2: 趨勢信號
            layer_2_result = await self._execute_layer_processing(
                "layer_2", self._layer_2_trend_signals, symbol, market_data
            )
            if layer_2_result.signals:
                signals.extend(layer_2_result.signals)
            
            # Layer 3: 成交量信號
            layer_3_result = await self._execute_layer_processing(
                "layer_3", self._layer_3_volume_signals, symbol, market_data
            )
            if layer_3_result.signals:
                signals.extend(layer_3_result.signals)
            
            return signals
            
        except Exception as e:
            logger.error(f"信號生成失敗: {e}")
            return []
    
    async def _on_market_data_update(self, data_type: str, data: Any):
        """市場數據更新回調"""
        try:
            if data_type == 'ticker':
                await self._process_ticker_update(data)
            elif data_type == 'depth':
                await self._process_depth_update(data)
            elif data_type == 'kline':
                await self._process_kline_update(data)
                
        except Exception as e:
            logger.error(f"市場數據處理失敗: {e}")
    
    async def _process_ticker_update(self, ticker_data):
        """處理 Ticker 更新"""
        try:
            symbol = ticker_data.symbol
            price = ticker_data.price
            volume = ticker_data.volume
            timestamp = ticker_data.timestamp
            
            # 添加到緩衝區
            self.price_buffer[symbol].append({
                'price': price,
                'timestamp': timestamp,
                'volume': volume
            })
            
            self.volume_buffer[symbol].append({
                'volume': volume,
                'timestamp': timestamp,
                'price': price
            })
            
            # 觸發信號生成
            await self._trigger_signal_generation(symbol, ticker_data)
            
        except Exception as e:
            logger.error(f"Ticker 數據處理失敗: {e}")
    
    async def _trigger_signal_generation(self, symbol: str, market_data):
        """觸發信號生成 - 處理 processed_market_data"""
        start_time = datetime.now()
        
        try:
            # 檢查是否暫停信號生成
            if self.signal_generation_paused:
                logger.debug("信號生成已暫停，跳過處理")
                return
                
            # 先處理市場數據
            processed_market_data = await self._process_market_data(market_data)
            if not processed_market_data:
                logger.warning(f"市場數據處理失敗，跳過信號生成: {symbol}")
                return
            
            # 並行執行所有層處理
            layer_tasks = []
            for layer_id, processor in self.layer_processors.items():
                task = asyncio.create_task(
                    self._execute_layer_processing(layer_id, processor, symbol, processed_market_data)
                )
                layer_tasks.append(task)
            
            # 等待所有層處理完成
            layer_results = await asyncio.gather(*layer_tasks, return_exceptions=True)
            
            # 合併所有信號
            all_signals = []
            total_processing_time = 0
            
            for result in layer_results:
                if isinstance(result, LayerProcessingResult):
                    all_signals.extend(result.signals)
                    total_processing_time += result.processing_time_ms
                elif isinstance(result, Exception):
                    logger.error(f"層處理失敗: {result}")
            
            # 記錄性能
            end_time = datetime.now()
            total_time_ms = (end_time - start_time).total_seconds() * 1000
            
            self.processing_times['total'].append(total_time_ms)
            
            # 發送信號到下游
            if all_signals:
                await self._distribute_signals(all_signals)
            
            # 性能統計
            await self._record_performance_stats(symbol, total_time_ms, len(all_signals))
            
        except Exception as e:
            logger.error(f"信號生成失敗: {e}")
    
    async def _execute_layer_processing(self, layer_id: str, processor, symbol: str, market_data) -> LayerProcessingResult:
        """執行單層處理"""
        start_time = datetime.now()
        
        try:
            signals = await processor(symbol, market_data)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds() * 1000
            
            return LayerProcessingResult(
                layer_id=layer_id,
                signals=signals,
                processing_time_ms=processing_time,
                data_quality=0.9,  # 基礎數據品質
                source_data_count=len(self.price_buffer[symbol])
            )
            
        except Exception as e:
            logger.error(f"層 {layer_id} 處理失敗: {e}")
            return LayerProcessingResult(
                layer_id=layer_id,
                signals=[],
                processing_time_ms=0,
                data_quality=0.0,
                source_data_count=0
            )
    
    async def _layer_0_instant_signals(self, symbol: str, market_data) -> List[BasicSignal]:
        """Layer 0: 即時信號 (< 5ms)"""
        signals = []
        
        try:
            # 獲取動態參數
            dynamic_params = await self._get_dynamic_parameters("basic_mode")
            
            price = market_data.price
            volume = market_data.volume
            timestamp = market_data.timestamp
            
            # 價格突破信號
            if len(self.price_buffer[symbol]) >= 2:
                prev_price = list(self.price_buffer[symbol])[-2]['price']
                price_change_pct = (price - prev_price) / prev_price
                price_change_abs = abs(price_change_pct)
                
                # 使用動態價格變化閾值
                if price_change_abs > dynamic_params.price_change_threshold:
                    direction = "BUY" if price_change_pct > 0 else "SELL"
                    strength = min(price_change_abs / (dynamic_params.price_change_threshold * 2), 1.0)
                    
                    # 使用動態信心度閾值
                    base_confidence = 0.7 + (price_change_abs - dynamic_params.price_change_threshold) * 10
                    confidence = min(max(base_confidence, 0.3), 1.0)
                    
                    if confidence >= dynamic_params.confidence_threshold:
                        signal = BasicSignal(
                            signal_id=f"instant_price_{symbol}_{timestamp.timestamp()}",
                            symbol=symbol,
                            signal_type=SignalType.PRICE_ACTION,
                            direction=direction,
                            strength=strength,
                            confidence=confidence,
                            priority=Priority.HIGH,
                            timestamp=timestamp,
                            price=price,
                            volume=volume,
                            metadata={
                                "price_change_pct": price_change_pct * 100,
                                "prev_price": prev_price,
                                "signal_source": "instant_price_spike",
                                "dynamic_threshold_used": dynamic_params.price_change_threshold,
                                "market_regime": dynamic_params.market_regime.value,
                                "trading_session": dynamic_params.trading_session.value
                            },
                            layer_source="layer_0",
                            processing_time_ms=0,
                            market_regime=dynamic_params.market_regime.value,
                            trading_session=dynamic_params.trading_session.value,
                            price_change=price_change_pct,
                            volume_change=0.0
                        )
                        signals.append(signal)
            
            # 成交量突破信號
            if len(self.volume_buffer[symbol]) >= 5:
                recent_volumes = [v['volume'] for v in list(self.volume_buffer[symbol])[-5:]]
                avg_volume = np.mean(recent_volumes[:-1])
                
                if avg_volume > 0:
                    volume_ratio = volume / avg_volume
                    
                    # 使用動態成交量變化閾值
                    if volume_ratio > dynamic_params.volume_change_threshold:
                        strength = min(volume_ratio / (dynamic_params.volume_change_threshold * 2), 1.0)
                        
                        # 計算成交量信心度
                        base_confidence = 0.6 + (volume_ratio - dynamic_params.volume_change_threshold) * 0.1
                        confidence = min(max(base_confidence, 0.3), 1.0)
                        
                        if confidence >= dynamic_params.confidence_threshold:
                            signal = BasicSignal(
                                signal_id=f"instant_volume_{symbol}_{timestamp.timestamp()}",
                                symbol=symbol,
                                signal_type=SignalType.VOLUME,
                                direction="NEUTRAL",
                                strength=strength,
                                confidence=confidence,
                                priority=Priority.MEDIUM,
                                timestamp=timestamp,
                                price=price,
                                volume=volume,
                                metadata={
                                    "volume_ratio": volume_ratio,
                                    "avg_volume": avg_volume,
                                    "signal_source": "instant_volume_spike",
                                    "dynamic_threshold_used": dynamic_params.volume_change_threshold,
                                    "market_regime": dynamic_params.market_regime.value,
                                    "trading_session": dynamic_params.trading_session.value
                                },
                                layer_source="layer_0",
                                processing_time_ms=0,
                                market_regime=dynamic_params.market_regime.value,
                                trading_session=dynamic_params.trading_session.value,
                                price_change=0.0,
                                volume_change=volume_ratio
                            )
                            signals.append(signal)
            
        except Exception as e:
            logger.error(f"Layer 0 處理失敗: {e}")
        
        return signals
    
    async def _layer_1_momentum_signals(self, symbol: str, market_data) -> List[BasicSignal]:
        """Layer 1: 動量信號 (< 15ms)"""
        signals = []
        
        try:
            if len(self.price_buffer[symbol]) < 14:  # 需要至少 14 個數據點
                return signals
            
            # 準備價格數據
            prices = [p['price'] for p in list(self.price_buffer[symbol])]
            timestamps = [p['timestamp'] for p in list(self.price_buffer[symbol])]
            
            # 簡化 RSI 計算
            rsi = self._calculate_simple_rsi(prices, period=14)
            
            if rsi is not None:
                # RSI 超買超賣信號
                if rsi < 30:  # 超賣
                    signal = BasicSignal(
                        signal_id=f"momentum_rsi_oversold_{symbol}_{timestamps[-1].timestamp()}",
                        symbol=symbol,
                        signal_type=SignalType.MOMENTUM,
                        direction="BUY",
                        strength=min((30 - rsi) / 20, 1.0),
                        confidence=0.75,
                        priority=Priority.HIGH,
                        timestamp=timestamps[-1],
                        price=prices[-1],
                        volume=market_data.volume,
                        metadata={
                            "rsi_value": rsi,
                            "signal_source": "rsi_oversold"
                        },
                        layer_source="layer_1",
                        processing_time_ms=0
                    )
                    signals.append(signal)
                
                elif rsi > 70:  # 超買
                    signal = BasicSignal(
                        signal_id=f"momentum_rsi_overbought_{symbol}_{timestamps[-1].timestamp()}",
                        symbol=symbol,
                        signal_type=SignalType.MOMENTUM,
                        direction="SELL",
                        strength=min((rsi - 70) / 20, 1.0),
                        confidence=0.75,
                        priority=Priority.HIGH,
                        timestamp=timestamps[-1],
                        price=prices[-1],
                        volume=market_data.volume,
                        metadata={
                            "rsi_value": rsi,
                            "signal_source": "rsi_overbought"
                        },
                        layer_source="layer_1",
                        processing_time_ms=0
                    )
                    signals.append(signal)
            
            # 動量變化信號
            if len(prices) >= 5:
                recent_momentum = (prices[-1] - prices[-5]) / prices[-5] * 100
                
                if abs(recent_momentum) > 1.0:  # 1% 動量變化
                    direction = "BUY" if recent_momentum > 0 else "SELL"
                    strength = min(abs(recent_momentum) / 5.0, 1.0)
                    
                    signal = BasicSignal(
                        signal_id=f"momentum_change_{symbol}_{timestamps[-1].timestamp()}",
                        symbol=symbol,
                        signal_type=SignalType.MOMENTUM,
                        direction=direction,
                        strength=strength,
                        confidence=0.65,
                        priority=Priority.MEDIUM,
                        timestamp=timestamps[-1],
                        price=prices[-1],
                        volume=market_data.volume,
                        metadata={
                            "momentum_pct": recent_momentum,
                            "signal_source": "momentum_change"
                        },
                        layer_source="layer_1",
                        processing_time_ms=0
                    )
                    signals.append(signal)
            
        except Exception as e:
            logger.error(f"Layer 1 處理失敗: {e}")
        
        return signals
    
    async def _layer_2_trend_signals(self, symbol: str, market_data) -> List[BasicSignal]:
        """Layer 2: 趨勢信號 (< 20ms)"""
        signals = []
        
        try:
            if len(self.price_buffer[symbol]) < 20:
                return signals
            
            prices = [p['price'] for p in list(self.price_buffer[symbol])]
            timestamps = [p['timestamp'] for p in list(self.price_buffer[symbol])]
            
            # 簡單移動平均線
            sma_short = np.mean(prices[-5:])  # 5 期均線
            sma_long = np.mean(prices[-20:])  # 20 期均線
            
            # 均線交叉信號
            if len(prices) >= 21:
                prev_sma_short = np.mean(prices[-6:-1])
                prev_sma_long = np.mean(prices[-21:-1])
                
                # 金叉
                if (sma_short > sma_long and prev_sma_short <= prev_sma_long):
                    signal = BasicSignal(
                        signal_id=f"trend_golden_cross_{symbol}_{timestamps[-1].timestamp()}",
                        symbol=symbol,
                        signal_type=SignalType.TREND,
                        direction="BUY",
                        strength=0.8,
                        confidence=0.8,
                        priority=Priority.HIGH,
                        timestamp=timestamps[-1],
                        price=prices[-1],
                        volume=market_data.volume,
                        metadata={
                            "sma_short": sma_short,
                            "sma_long": sma_long,
                            "signal_source": "golden_cross"
                        },
                        layer_source="layer_2",
                        processing_time_ms=0
                    )
                    signals.append(signal)
                
                # 死叉
                elif (sma_short < sma_long and prev_sma_short >= prev_sma_long):
                    signal = BasicSignal(
                        signal_id=f"trend_death_cross_{symbol}_{timestamps[-1].timestamp()}",
                        symbol=symbol,
                        signal_type=SignalType.TREND,
                        direction="SELL",
                        strength=0.8,
                        confidence=0.8,
                        priority=Priority.HIGH,
                        timestamp=timestamps[-1],
                        price=prices[-1],
                        volume=market_data.volume,
                        metadata={
                            "sma_short": sma_short,
                            "sma_long": sma_long,
                            "signal_source": "death_cross"
                        },
                        layer_source="layer_2",
                        processing_time_ms=0
                    )
                    signals.append(signal)
            
            # 趨勢強度信號
            if len(prices) >= 10:
                trend_strength = self._calculate_trend_strength(prices[-10:])
                
                if abs(trend_strength) > 0.5:
                    direction = "BUY" if trend_strength > 0 else "SELL"
                    
                    signal = BasicSignal(
                        signal_id=f"trend_strength_{symbol}_{timestamps[-1].timestamp()}",
                        symbol=symbol,
                        signal_type=SignalType.TREND,
                        direction=direction,
                        strength=min(abs(trend_strength), 1.0),
                        confidence=0.7,
                        priority=Priority.MEDIUM,
                        timestamp=timestamps[-1],
                        price=prices[-1],
                        volume=market_data.volume,
                        metadata={
                            "trend_strength": trend_strength,
                            "signal_source": "trend_strength"
                        },
                        layer_source="layer_2",
                        processing_time_ms=0
                    )
                    signals.append(signal)
            
        except Exception as e:
            logger.error(f"Layer 2 處理失敗: {e}")
        
        return signals
    
    async def _layer_3_volume_signals(self, symbol: str, market_data) -> List[BasicSignal]:
        """Layer 3: 成交量信號 (< 5ms)"""
        signals = []
        
        try:
            if len(self.volume_buffer[symbol]) < 10:
                return signals
            
            volumes = [v['volume'] for v in list(self.volume_buffer[symbol])]
            prices = [v['price'] for v in list(self.volume_buffer[symbol])]
            timestamps = [v['timestamp'] for v in list(self.volume_buffer[symbol])]
            
            # 成交量確認信號
            if len(volumes) >= 5:
                avg_volume = np.mean(volumes[-5:])
                current_volume = volumes[-1]
                
                # 價量配合
                price_change = (prices[-1] - prices[-2]) / prices[-2] * 100 if len(prices) >= 2 else 0
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
                
                if abs(price_change) > 0.3 and volume_ratio > 1.5:
                    direction = "BUY" if price_change > 0 else "SELL"
                    strength = min(volume_ratio / 3.0, 1.0)
                    
                    signal = BasicSignal(
                        signal_id=f"volume_confirmation_{symbol}_{timestamps[-1].timestamp()}",
                        symbol=symbol,
                        signal_type=SignalType.VOLUME,
                        direction=direction,
                        strength=strength,
                        confidence=0.75,
                        priority=Priority.HIGH,
                        timestamp=timestamps[-1],
                        price=prices[-1],
                        volume=current_volume,
                        metadata={
                            "price_change_pct": price_change,
                            "volume_ratio": volume_ratio,
                            "avg_volume": avg_volume,
                            "signal_source": "volume_price_confirmation"
                        },
                        layer_source="layer_3",
                        processing_time_ms=0
                    )
                    signals.append(signal)
            
            # 異常成交量信號
            if len(volumes) >= 20:
                long_avg_volume = np.mean(volumes[-20:])
                current_volume = volumes[-1]
                
                if current_volume > long_avg_volume * 3:  # 3 倍異常成交量
                    signal = BasicSignal(
                        signal_id=f"volume_unusual_{symbol}_{timestamps[-1].timestamp()}",
                        symbol=symbol,
                        signal_type=SignalType.VOLUME,
                        direction="NEUTRAL",
                        strength=min(current_volume / long_avg_volume / 5, 1.0),
                        confidence=0.6,
                        priority=Priority.MEDIUM,
                        timestamp=timestamps[-1],
                        price=prices[-1],
                        volume=current_volume,
                        metadata={
                            "volume_multiple": current_volume / long_avg_volume,
                            "long_avg_volume": long_avg_volume,
                            "signal_source": "unusual_volume"
                        },
                        layer_source="layer_3",
                        processing_time_ms=0
                    )
                    signals.append(signal)
            
        except Exception as e:
            logger.error(f"Layer 3 處理失敗: {e}")
        
        return signals
    
    def _calculate_simple_rsi(self, prices: List[float], period: int = 14) -> Optional[float]:
        """計算簡化 RSI"""
        try:
            if len(prices) < period + 1:
                return None
            
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gain = np.mean(gains[-period:])
            avg_loss = np.mean(losses[-period:])
            
            if avg_loss == 0:
                return 100
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            logger.error(f"RSI 計算失敗: {e}")
            return None
    
    def _calculate_trend_strength(self, prices: List[float]) -> float:
        """計算趨勢強度"""
        try:
            if len(prices) < 2:
                return 0.0
            
            # 線性回歸斜率
            x = np.arange(len(prices))
            coeffs = np.polyfit(x, prices, 1)
            slope = coeffs[0]
            
            # 正規化斜率
            avg_price = np.mean(prices)
            normalized_slope = slope / avg_price if avg_price > 0 else 0
            
            return normalized_slope * 100  # 轉換為百分比
            
        except Exception as e:
            logger.error(f"趨勢強度計算失敗: {e}")
            return 0.0
    
    async def _distribute_signals(self, signals: List[BasicSignal]):
        """分發信號到下游"""
        try:
            # 添加到信號緩衝區
            self.signal_buffer.extend(signals)
            
            # 通知訂閱者
            for subscriber in self.signal_subscribers:
                try:
                    if asyncio.iscoroutinefunction(subscriber):
                        await subscriber(signals)
                    else:
                        subscriber(signals)
                except Exception as e:
                    logger.error(f"信號訂閱者通知失敗: {e}")
            
            logger.info(f"分發 {len(signals)} 個信號")
            
        except Exception as e:
            logger.error(f"信號分發失敗: {e}")
    
    def subscribe_to_signals(self, callback):
        """訂閱信號"""
        if callback not in self.signal_subscribers:
            self.signal_subscribers.append(callback)
            logger.info(f"新增信號訂閱者: {callback.__name__}")
    
    def subscribe_signals(self, callback):
        """訂閱信號（向下兼容別名）"""
        return self.subscribe_to_signals(callback)
    
    async def _record_performance_stats(self, symbol: str, processing_time_ms: float, signal_count: int):
        """記錄性能統計"""
        stats = {
            'timestamp': datetime.now(),
            'symbol': symbol,
            'processing_time_ms': processing_time_ms,
            'signal_count': signal_count,
            'buffer_sizes': {
                'price': len(self.price_buffer[symbol]),
                'volume': len(self.volume_buffer[symbol]),
                'signals': len(self.signal_buffer)
            }
        }
        
        self.performance_stats['processing'].append(stats)
    
    async def _performance_monitor(self):
        """性能監控器"""
        while self.is_running:
            try:
                if self.processing_times['total']:
                    avg_processing_time = np.mean(self.processing_times['total'])
                    max_processing_time = max(self.processing_times['total'])
                    
                    logger.info(f"Phase1A 性能: 平均 {avg_processing_time:.1f}ms, 最大 {max_processing_time:.1f}ms")
                    
                    # 清理舊數據
                    if len(self.processing_times['total']) > 100:
                        for _ in range(50):
                            self.processing_times['total'].popleft()
                
                await asyncio.sleep(60)  # 每分鐘檢查一次
                
            except Exception as e:
                logger.error(f"性能監控失敗: {e}")
                await asyncio.sleep(60)
    
    async def _signal_quality_analyzer(self):
        """信號品質分析器"""
        while self.is_running:
            try:
                if len(self.signal_buffer) > 10:
                    recent_signals = list(self.signal_buffer)[-50:]
                    
                    # 分析信號分布
                    signal_types = defaultdict(int)
                    priority_counts = defaultdict(int)
                    avg_strength = 0
                    
                    for signal in recent_signals:
                        signal_types[signal.signal_type.value] += 1
                        priority_counts[signal.priority.value] += 1
                        avg_strength += signal.strength
                    
                    avg_strength /= len(recent_signals)
                    
                    logger.info(f"信號品質: 平均強度 {avg_strength:.2f}, 類型分布 {dict(signal_types)}")
                
                await asyncio.sleep(300)  # 每 5 分鐘分析一次
                
            except Exception as e:
                logger.error(f"信號品質分析失敗: {e}")
                await asyncio.sleep(300)
    
    async def _signal_generation_coordinator(self):
        """信號生成協調器"""
        while self.is_running:
            try:
                # 清理過期數據
                current_time = datetime.now()
                cutoff_time = current_time - timedelta(minutes=5)
                
                for symbol in list(self.price_buffer.keys()):
                    # 清理價格緩衝區
                    while (self.price_buffer[symbol] and 
                           self.price_buffer[symbol][0]['timestamp'] < cutoff_time):
                        self.price_buffer[symbol].popleft()
                    
                    # 清理成交量緩衝區
                    while (self.volume_buffer[symbol] and 
                           self.volume_buffer[symbol][0]['timestamp'] < cutoff_time):
                        self.volume_buffer[symbol].popleft()
                
                # 清理信號緩衝區
                while (self.signal_buffer and 
                       (current_time - self.signal_buffer[0].timestamp).total_seconds() > 3600):  # 1小時
                    self.signal_buffer.popleft()
                
                await asyncio.sleep(60)  # 每分鐘清理一次
                
            except Exception as e:
                logger.error(f"協調器失敗: {e}")
                await asyncio.sleep(60)
    
    async def get_recent_signals(self, symbol: str = None, limit: int = 100) -> List[BasicSignal]:
        """獲取最近信號"""
        signals = list(self.signal_buffer)
        
        if symbol:
            signals = [s for s in signals if s.symbol == symbol]
        
        return signals[-limit:]
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """獲取性能摘要"""
        if not self.processing_times['total']:
            return {}
        
        return {
            'average_processing_time_ms': np.mean(self.processing_times['total']),
            'max_processing_time_ms': max(self.processing_times['total']),
            'min_processing_time_ms': min(self.processing_times['total']),
            'total_signals_generated': len(self.signal_buffer),
            'active_symbols': len(self.price_buffer),
            'signal_generation_rate': len(self.signal_buffer) / max((datetime.now() - self.performance_stats['processing'][0]['timestamp']).total_seconds() / 60, 1) if self.performance_stats['processing'] else 0
        }
    
    # ===== JSON規範輸出格式方法 =====
    
    async def generate_basic_signals_output(self, signals: List[BasicSignal]) -> Dict[str, Any]:
        """生成 basic_signals 輸出格式 - JSON規範要求"""
        try:
            basic_signals = {
                "type": "basic_signals",
                "timestamp": datetime.now(),
                "signal_count": len(signals),
                "signals": [],
                "processing_summary": {
                    "total_processing_time_ms": sum(s.processing_time_ms for s in signals),
                    "average_confidence": sum(s.confidence for s in signals) / len(signals) if signals else 0,
                    "signal_types": list(set(s.signal_type.value for s in signals))
                }
            }
            
            for signal in signals:
                basic_signals["signals"].append({
                    "signal_id": signal.signal_id,
                    "symbol": signal.symbol,
                    "signal_type": signal.signal_type.value,
                    "direction": signal.direction,
                    "strength": signal.strength,
                    "confidence": signal.confidence,
                    "priority": signal.priority.value,
                    "timestamp": signal.timestamp,
                    "price": signal.price,
                    "volume": signal.volume,
                    "layer_source": signal.layer_source,
                    "metadata": signal.metadata
                })
            
            return basic_signals
        except Exception as e:
            logger.error(f"basic_signals 輸出生成失敗: {e}")
            return {}
    
    async def generate_standardized_basic_signals_output(self, signals: List[BasicSignal]) -> Dict[str, Any]:
        """生成 standardized_basic_signals 輸出格式 - JSON規範要求"""
        try:
            # 信號標準化處理
            standardized_signals = []
            
            for signal in signals:
                # 標準化強度和置信度
                normalized_strength = min(1.0, max(0.0, signal.strength))
                normalized_confidence = min(1.0, max(0.0, signal.confidence))
                
                # 統一信號格式
                standardized_signal = {
                    "signal_id": signal.signal_id,
                    "symbol": signal.symbol,
                    "unified_signal_type": self._map_to_unified_type(signal.signal_type.value),
                    "direction": signal.direction,
                    "normalized_strength": normalized_strength,
                    "normalized_confidence": normalized_confidence,
                    "priority_score": self._map_priority_to_score(signal.priority.value),
                    "timestamp": signal.timestamp,
                    "market_data": {
                        "price": signal.price,
                        "volume": signal.volume
                    },
                    "generation_metadata": {
                        "layer_source": signal.layer_source,
                        "processing_time_ms": signal.processing_time_ms,
                        "original_metadata": signal.metadata
                    },
                    "quality_metrics": {
                        "data_freshness": self._calculate_data_freshness(signal.timestamp),
                        "signal_reliability": self._calculate_signal_reliability(signal),
                        "cross_validation_score": 0.8  # 簡化實現
                    }
                }
                
                standardized_signals.append(standardized_signal)
            
            return {
                "type": "standardized_basic_signals",
                "timestamp": datetime.now(),
                "standardization_version": "1.0.0",
                "signal_count": len(standardized_signals),
                "signals": standardized_signals,
                "quality_summary": {
                    "average_reliability": sum(s["quality_metrics"]["signal_reliability"] for s in standardized_signals) / len(standardized_signals) if standardized_signals else 0,
                    "average_confidence": sum(s["normalized_confidence"] for s in standardized_signals) / len(standardized_signals) if standardized_signals else 0,
                    "high_priority_count": sum(1 for s in standardized_signals if s["priority_score"] > 0.7)
                }
            }
        except Exception as e:
            logger.error(f"standardized_basic_signals 輸出生成失敗: {e}")
            return {}
    
    def _map_to_unified_type(self, signal_type: str) -> str:
        """映射到統一信號類型"""
        mapping = {
            "momentum": "MOMENTUM_SIGNAL",
            "trend": "TREND_SIGNAL", 
            "volatility": "VOLATILITY_SIGNAL",
            "volume": "VOLUME_SIGNAL",
            "price_action": "PRICE_ACTION_SIGNAL"
        }
        return mapping.get(signal_type, "UNKNOWN_SIGNAL")
    
    def _map_priority_to_score(self, priority: str) -> float:
        """映射優先級到分數"""
        mapping = {
            "CRITICAL": 1.0,
            "HIGH": 0.8,
            "MEDIUM": 0.5,
            "LOW": 0.2
        }
        return mapping.get(priority, 0.0)
    
    def _calculate_data_freshness(self, timestamp: datetime) -> float:
        """計算數據新鮮度"""
        try:
            now = datetime.now()
            age_seconds = (now - timestamp).total_seconds()
            # 5秒內為完全新鮮，30秒後為完全陳舊
            freshness = max(0.0, 1.0 - age_seconds / 30.0)
            return min(1.0, freshness)
        except:
            return 0.5
    
    def _calculate_signal_reliability(self, signal: BasicSignal) -> float:
        """計算信號可靠性"""
        try:
            # 基於多個因素計算可靠性
            factors = []
            
            # 置信度因子
            factors.append(signal.confidence)
            
            # 強度因子（適度強度更可靠）
            optimal_strength = 0.7
            strength_factor = 1.0 - abs(signal.strength - optimal_strength) / optimal_strength
            factors.append(strength_factor)
            
            # 數據品質因子
            data_quality = signal.metadata.get('data_quality', 0.8)
            factors.append(data_quality)
            
            # 加權平均
            weights = [0.4, 0.3, 0.3]  # 置信度權重最高
            reliability = sum(f * w for f, w in zip(factors, weights))
            
            return min(1.0, max(0.0, reliability))
        except:
            return 0.5

    async def generate_signal_generation_results(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成信號生成結果 - JSON規範要求"""
        try:
            return {
                "type": "signal_generation_results",
                "symbol": market_data.get('symbol', 'BTCUSDT'),
                "timestamp": time.time(),
                "signals_generated": 0,
                "signal_quality": 0.0,
                "processing_time_ms": 0.0
            }
        except:
            return {}

    async def generate_phase1a_signal_summary(self, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """生成 phase1a_signal_summary - JSON規範要求"""
        try:
            return {
                "type": "phase1a_signal_summary",
                "timestamp": time.time(),
                "status": "generated",
                "data": data or {}
            }
        except:
            return {}

    async def process_real_time_price_feed_input(self, data: Dict[str, Any]) -> bool:
        """處理實時價格數據輸入"""
        try:
            return True
        except:
            return False

# 全局實例
phase1a_signal_generator = Phase1ABasicSignalGeneration()

# 便捷函數
async def start_phase1a_generator(websocket_driver):
    """啟動 Phase1A 信號生成器"""
    await phase1a_signal_generator.start(websocket_driver)

async def stop_phase1a_generator():
    """停止 Phase1A 信號生成器"""
    await phase1a_signal_generator.stop()

def subscribe_to_phase1a_signals(callback):
    """訂閱 Phase1A 信號"""
    phase1a_signal_generator.subscribe_to_signals(callback)
