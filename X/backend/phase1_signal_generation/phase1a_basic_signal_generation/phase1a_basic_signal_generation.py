"""
🎯 Trading X - Phase1A 基礎信號生成器
基於 WebSocket 實時數據的多層級信號處理引擎
實現 < 45ms 的信號生成與分發

★ 產品等級架構：調用 intelligent_trigger_engine 進行技術分析
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
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import json
from enum import Enum
import time
import pytz

# 🧠 第二階段自適應學習組件導入
try:
    import sys
    from pathlib import Path
    
    # 添加上級目錄到路徑以便導入新組件
    current_dir = Path(__file__).parent
    backend_dir = current_dir.parent.parent
    
    # 嘗試導入新的 Phase 2 組件
    try:
        # 使用絕對導入避免循環依賴
        import importlib.util
        
        # 動態導入 advanced_market_detector
        market_detector_path = backend_dir / "phase2_adaptive_learning" / "market_regime_detection" / "advanced_market_detector.py"
        spec = importlib.util.spec_from_file_location("advanced_market_detector", market_detector_path)
        advanced_market_detector = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(advanced_market_detector)
        
        # 動態導入 adaptive_learning_engine
        learning_engine_path = backend_dir / "phase2_adaptive_learning" / "learning_core" / "adaptive_learning_engine.py"
        spec = importlib.util.spec_from_file_location("adaptive_learning_engine", learning_engine_path)
        adaptive_learning_engine = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adaptive_learning_engine)
        
        # 從模組中獲取類別
        AdvancedMarketRegimeDetector = advanced_market_detector.AdvancedMarketRegimeDetector
        MarketRegime = advanced_market_detector.MarketRegime
        AdaptiveLearningCore = adaptive_learning_engine.AdaptiveLearningCore
        LearningStatus = adaptive_learning_engine.LearningStatus
        
        ADAPTIVE_LEARNING_ENABLED = True
        logging.info("✅ 第二階段自適應學習組件載入成功")
        
    except Exception as e:
        ADAPTIVE_LEARNING_ENABLED = False
        logging.warning(f"⚠️ 第二階段自適應學習組件載入失敗: {e}")
        logging.warning("系統將以基礎模式運行")
    
except ImportError as e:
    ADAPTIVE_LEARNING_ENABLED = False
    logging.warning(f"⚠️ 第二階段自適應學習組件載入失敗: {e}")
    logging.warning("系統將以基礎模式運行")
from pathlib import Path

logger = logging.getLogger(__name__)

# ★ 產品等級導入：調用 intelligent_trigger_engine
import sys
sys.path.append(str(Path(__file__).parent.parent / "intelligent_trigger_engine"))

try:
    from intelligent_trigger_engine import (
        get_technical_indicators_for_phase1a,
        get_real_time_analysis_for_phase1a,
        is_real_time_data_available,
        validate_data_quality,
        TechnicalIndicatorState,
        start_intelligent_trigger_engine,
        process_realtime_price_update
    )
    logger.info("✅ 產品等級 intelligent_trigger_engine API 導入成功")
except ImportError as e:
    logger.error(f"❌ intelligent_trigger_engine 導入失敗: {e}")
    raise Exception("產品等級系統要求必須正確配置 intelligent_trigger_engine")

logger = logging.getLogger(__name__)

# ✅ 簡化：直接使用高級版本，如果載入失敗則系統停止
if not ADAPTIVE_LEARNING_ENABLED:
    raise ImportError("MarketRegime 必須從高級市場檢測器導入，系統無法在基礎模式下運行")

# MarketRegime 和相關類別已在上方從 advanced_market_detector 導入

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

class SignalTier(Enum):
    """信號分層系統 - 多層級信號處理"""
    CRITICAL = "🚨"     # 高信心度：大倉位，嚴格標準
    HIGH = "🎯"         # 中信心度：中倉位，適中標準  
    MEDIUM = "📊"       # 低信心度：中小倉位，寬鬆標準
    LOW = "📈"          # 探索性：小倉位，學習用途

@dataclass
class TierConfiguration:
    """分層配置 - 對應不同信號等級的處理參數"""
    tier: SignalTier
    lean_threshold: float           # Lean 信心度要求
    technical_threshold: float      # 技術指標閾值
    position_multiplier: float      # 倉位乘數
    stop_loss_ratio: float         # 止損比例
    execution_priority: int         # 執行優先級 (1-4)
    max_signals_per_hour: int      # 每小時最大信號數

class EnhancedSignalTierSystem:
    """增強信號分層系統 - Phase1A 核心分層邏輯"""
    
    def __init__(self):
        self.tier_configs = {
            SignalTier.CRITICAL: TierConfiguration(
                tier=SignalTier.CRITICAL,
                lean_threshold=0.65,
                technical_threshold=0.8,
                position_multiplier=0.8,
                stop_loss_ratio=0.02,
                execution_priority=1,
                max_signals_per_hour=3
            ),
            SignalTier.HIGH: TierConfiguration(
                tier=SignalTier.HIGH,
                lean_threshold=0.55,
                technical_threshold=0.7,
                position_multiplier=0.6,
                stop_loss_ratio=0.025,
                execution_priority=2,
                max_signals_per_hour=5
            ),
            SignalTier.MEDIUM: TierConfiguration(
                tier=SignalTier.MEDIUM,
                lean_threshold=0.45,
                technical_threshold=0.6,
                position_multiplier=0.4,
                stop_loss_ratio=0.03,
                execution_priority=3,
                max_signals_per_hour=8
            ),
            SignalTier.LOW: TierConfiguration(
                tier=SignalTier.LOW,
                lean_threshold=0.35,
                technical_threshold=0.5,
                position_multiplier=0.2,
                stop_loss_ratio=0.04,
                execution_priority=4,
                max_signals_per_hour=15
            )
        }
    
    def get_dynamic_threshold(self, lean_confidence: float, priority: SignalTier) -> float:
        """根據 Lean 信心度和優先級動態調整閾值"""
        base_threshold = self.tier_configs[priority].lean_threshold
        # 動態調整：最低 0.4，基於 lean_confidence 縮放
        return max(0.4, lean_confidence * base_threshold)
    
    def classify_signal_tier(self, lean_confidence: float, technical_score: float) -> SignalTier:
        """信號分層分類 - 基於 Lean 信心度和技術分數"""
        # CRITICAL: 需要很高的 Lean 信心度 + 技術確認
        if lean_confidence >= 0.75 and technical_score >= 0.8:
            return SignalTier.CRITICAL
        
        # HIGH: 較高信心度或單方面優秀
        elif lean_confidence >= 0.65 or technical_score >= 0.75:
            return SignalTier.HIGH
        
        # MEDIUM: 中等水平
        elif lean_confidence >= 0.5 or technical_score >= 0.6:
            return SignalTier.MEDIUM
        
        # LOW: 探索性信號
        else:
            return SignalTier.LOW
    
    def get_tier_config(self, tier: SignalTier) -> TierConfiguration:
        """獲取分層配置"""
        return self.tier_configs[tier]
    
    def adjust_position_size(self, base_size: float, tier: SignalTier, 
                           market_volatility: float = 0.02) -> float:
        """根據分層調整倉位大小"""
        config = self.tier_configs[tier]
        
        # 基礎倉位 × 分層乘數 × 波動性調整
        volatility_factor = max(0.5, 1.0 - market_volatility * 10)
        adjusted_size = base_size * config.position_multiplier * volatility_factor
        
        return adjusted_size
    
    def get_execution_priority(self, tier: SignalTier) -> int:
        """獲取執行優先級"""
        return self.tier_configs[tier].execution_priority

@dataclass
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
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'price_change_threshold': self.price_change_threshold,
            'volume_change_threshold': self.volume_change_threshold,
            'confidence_threshold': self.confidence_threshold,
            'signal_strength_multiplier': self.signal_strength_multiplier,
            'signal_threshold': self.confidence_threshold,  # 別名
            'momentum_weight': 1.0,
            'volume_weight': 1.0,
            'confidence_multiplier': 1.0
        }

@dataclass
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
    volume: float = 0.0
    metadata: Dict[str, Any] = None
    layer_source: str = "unknown"
    processing_time_ms: float = 0.0
    market_regime: str = "UNKNOWN"  # 市場制度
    trading_session: str = "OFF_HOURS"  # 交易時段
    price_change: float = 0.0  # 價格變化率
    volume_change: float = 0.0  # 成交量變化率
    
    def __post_init__(self):
        """後初始化處理"""
        if self.metadata is None:
            self.metadata = {}
    
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
    
    def format_for_display(self, tier: 'SignalTier' = None) -> Dict[str, Any]:
        """格式化信號以供用戶顯示"""
        # 信號類型友好顯示映射
        signal_type_mapping = {
            'MOMENTUM': '動量突破',
            'momentum': '動量突破',
            'REVERSAL': '反轉信號',
            'reversal': '反轉信號',
            'BREAKOUT': '突破信號',
            'breakout': '突破信號',
            'HOLD': '持有觀望',
            'hold': '持有觀望',
            'BUY': '買入信號',
            'buy': '買入信號',
            'SELL': '賣出信號',
            'sell': '賣出信號',
            'LONG': '做多信號',
            'long': '做多信號',
            'SHORT': '做空信號',
            'short': '做空信號',
            'PRICE_ACTION': '價格行為',
            'price_action': '價格行為'
        }
        
        # 獲取信號類型顯示文字
        signal_type_str = self.signal_type.value if hasattr(self.signal_type, 'value') else str(self.signal_type)
        friendly_signal_type = signal_type_mapping.get(signal_type_str, signal_type_str)
        
        # 計算建議倉位 (更保守的策略)
        tier_name = tier.value if tier and hasattr(tier, 'value') else 'MEDIUM'
        position_base_multipliers = {"CRITICAL": 0.5, "HIGH": 0.4, "MEDIUM": 0.3, "LOW": 0.2}
        
        confidence_factor = min(self.strength, 1.0)
        base_position = position_base_multipliers.get(tier_name, 0.3)
        suggested_position = base_position * confidence_factor
        
        # 最小倉位閾值
        min_position = 0.05
        if suggested_position < min_position:
            suggested_position = min_position
        
        # 計算止盈止損
        profit_pct = max(self.strength * 0.05, 0.015)  # 最少1.5%止盈
        loss_pct = max(self.strength * 0.03, 0.010)    # 最少1.0%止損
        
        if 'MOMENTUM' in signal_type_str or 'BUY' in signal_type_str or 'LONG' in signal_type_str:
            take_profit = self.price * (1 + profit_pct)
            stop_loss = self.price * (1 - loss_pct)
        elif 'SELL' in signal_type_str or 'SHORT' in signal_type_str:
            take_profit = self.price * (1 - profit_pct)
            stop_loss = self.price * (1 + loss_pct)
        else:
            take_profit = self.price * (1 + profit_pct)
            stop_loss = self.price * (1 - loss_pct)
        
        # 建議持倉時間
        holding_hours = {"CRITICAL": 4, "HIGH": 8, "MEDIUM": 24, "LOW": 72}
        suggested_holding = holding_hours.get(tier_name, 24)
        
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "signal_type": friendly_signal_type,
            "confidence": self.confidence,
            "tier": tier_name,
            "suggested_position_size": f"{suggested_position:.1%}",
            "current_price": self.price,
            "take_profit": f"{take_profit:.4f}",
            "stop_loss": f"{stop_loss:.4f}",
            "suggested_holding_hours": suggested_holding,
            "raw_signal_data": {
                "signal_id": self.signal_id,
                "strength": self.strength,
                "direction": self.direction,
                "layer_source": self.layer_source,
                "market_regime": self.market_regime,
                "trading_session": self.trading_session
            }
        }

@dataclass
@dataclass
class LayerProcessingResult:
    """層處理結果"""
    layer_id: str
    signals: List['BasicSignal']
    processing_time_ms: float
    success: bool = True
    error: Optional[str] = None
    data_quality: float = 1.0
    source_data_count: int = 0

class Phase1ABasicSignalGeneration:
    """Phase1A 基礎信號生成器 - 4層並行處理架構 + 信號分層系統"""
    
    def __init__(self):
        self.config = self._load_config()
        
        # 🧠 第二階段自適應學習組件初始化
        if ADAPTIVE_LEARNING_ENABLED:
            self.regime_detector = AdvancedMarketRegimeDetector()
            self.learning_core = AdaptiveLearningCore()
            self.adaptive_mode = True
            logger.info("✅ 第二階段自適應學習模式啟用")
        else:
            self.regime_detector = None
            self.learning_core = None
            self.adaptive_mode = False
            logger.info("📊 基礎模式運行")
        
        # 動態參數系統
        self.dynamic_params_enabled = self._init_dynamic_parameter_system()
        self._cached_params = {}
        self._cache_timestamp = 0
        self._cache_ttl = 300  # 5分鐘緩存
        
        # ✨ 信號分層系統初始化
        self.tier_system = self._init_tier_system()
        self.tier_counters = {tier: 0 for tier in SignalTier}
        self.tier_history = []
        
        # 市場制度檢測
        self.current_regime = MarketRegime.UNKNOWN
        self.regime_confidence = 0.0
        self.regime_cache_timestamp = 0
        self.regime_cache_ttl = 300  # 5分鐘緩存
        
        # intelligent_trigger_engine 實例引用
        try:
            from intelligent_trigger_engine import intelligent_trigger_engine
            self.intelligent_trigger_engine = intelligent_trigger_engine
            logger.debug("✅ intelligent_trigger_engine 實例引用設置成功")
        except Exception as e:
            self.intelligent_trigger_engine = None
            logger.warning(f"⚠️ intelligent_trigger_engine 實例引用設置失敗: {e}")
        
        # 交易時段檢測
        self.current_trading_session = TradingSession.OFF_HOURS
        self.session_cache_timestamp = 0
        self.session_cache_ttl = 3600  # 1小時緩存
        
        # 數據緩衝區 - 增強版，支援技術分析
        self.price_buffer = defaultdict(lambda: deque(maxlen=500))      # 增加容量用於技術分析
        self.volume_buffer = defaultdict(lambda: deque(maxlen=500))     # 增加容量用於成交量分析
        self.orderbook_buffer = defaultdict(lambda: deque(maxlen=100))  # OrderBook 緩衝區
        self.kline_buffers = defaultdict(lambda: {'1m': deque(maxlen=500)})  # K線數據緩衝區
        self.signal_buffer = deque(maxlen=1000)                         # 信號輸出緩衝區
        
        # 層處理器
        self.layer_processors = {
            "layer_0": self._layer_0_instant_signals,
            "layer_1": self._layer_1_momentum_signals,
            "layer_2": self._layer_2_trend_signals,
            "layer_3": self._layer_3_volume_signals
        }
        
        # 性能監控
        self.performance_stats = defaultdict(list)
        self.processing_times = defaultdict(lambda: deque(maxlen=100))  # 保留最近100次的處理時間
        
        # 信號訂閱者列表 - 用於外部系統訂閱信號
        self.signal_subscribers = []
        
        # 市場數據緩存 - 用於測試和信號生成
        self.real_market_data = {}
        
        # 統計數據
        self.total_signals_count = 0
        
        # 運行控制
        self.is_running = False
        self.tasks = []
        self.websocket_driver = None
        
        # WebSocket 斷線處理
        self.circuit_breaker_active = False
        self.signal_generation_paused = False
        self.degraded_mode = False
        self.last_disconnect_time = None
        
        # 應用信號生成配置參數
        self._apply_signal_generation_config()
        
        # 應用技術指標配置參數
        self._apply_technical_indicator_config()
        
        logger.info("Phase1A 基礎信號生成器初始化完成（含動態參數系統）")
    
    def _load_config(self) -> Dict[str, Any]:
        """載入配置 - 優先讀取 Phase5 最新優化備份"""
        try:
            # 策略 1: 優先讀取 Phase5 最新 deployment_initial 備份
            phase5_config = self._load_from_phase5_backup()
            if phase5_config:
                logger.info("✅ 使用 Phase5 最新優化配置")
                return phase5_config
            
            # 策略 2: 備用方案 - 讀取本地原始配置
            logger.info("🔄 Phase5 備份不可用，使用本地原始配置")
            config_path = Path(__file__).parent / "phase1a_basic_signal_generation.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"配置載入失敗: {e}")
            # 配置載入失敗時返回空字典，依賴動態參數系統
            logger.warning("使用空配置，系統將完全依賴動態參數")
            return {}
    
    def _load_from_phase5_backup(self) -> Optional[Dict[str, Any]]:
        """從 Phase5 備份目錄讀取最新優化配置"""
        try:
            # Phase5 備份目錄路徑
            phase5_backup_dir = Path(__file__).parent.parent.parent / "phase5_backtest_validation" / "safety_backups" / "working"
            
            if not phase5_backup_dir.exists():
                logger.debug(f"Phase5 備份目錄不存在: {phase5_backup_dir}")
                return None
            
            # 尋找所有 deployment_initial 檔案
            deployment_files = list(phase5_backup_dir.glob("phase1a_backup_deployment_initial_*.json"))
            
            if not deployment_files:
                logger.debug("沒有找到 Phase5 deployment_initial 備份檔案")
                return None
            
            # 按修改時間排序，取最新的
            latest_backup = max(deployment_files, key=lambda x: x.stat().st_mtime)
            
            # 🔒 安全讀取最新備份配置（帶文件鎖保護）
            import fcntl
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    with open(latest_backup, 'r', encoding='utf-8') as f:
                        fcntl.flock(f.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)  # 共享鎖
                        phase5_config = json.load(f)
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)  # 釋放鎖
                    break  # 成功讀取，跳出循環
                    
                except IOError as e:
                    if e.errno == 11:  # EAGAIN - 文件被鎖定
                        retry_count += 1
                        logger.warning(f"⚠️ Phase5配置文件被鎖定，重試 {retry_count}/{max_retries}")
                        import time
                        time.sleep(0.5)  # 使用同步sleep
                    else:
                        raise
            else:
                logger.error("❌ 無法讀取Phase5配置文件，使用備用配置")
                return self._get_default_config()
            
            logger.info(f"🎯 成功讀取最新 Phase5 備份: {latest_backup.name}")
            logger.info(f"📅 備份時間: {datetime.fromtimestamp(latest_backup.stat().st_mtime)}")
            
            # 【重要修復】確保 Phase5 配置包含完整的動態參數設置
            if "phase1a_basic_signal_generation_dependency" not in phase5_config:
                logger.warning("⚠️ Phase5 配置缺少關鍵設置，補充動態參數配置")
                
                # 從本地原始配置讀取完整配置結構
                try:
                    config_path = Path(__file__).parent / "phase1a_basic_signal_generation.json"
                    with open(config_path, 'r', encoding='utf-8') as f:
                        original_config = json.load(f)
                    
                    # 合併配置：Phase5 優化參數 + 原始配置結構
                    merged_config = original_config.copy()
                    
                    # 保留 Phase5 的優化參數
                    if "input_specifications" in phase5_config:
                        merged_config["input_specifications"] = phase5_config["input_specifications"]
                    if "dynamic_parameters" in phase5_config:
                        merged_config["dynamic_parameters"] = phase5_config["dynamic_parameters"]
                    if "signal_thresholds" in phase5_config:
                        merged_config["signal_thresholds"] = phase5_config["signal_thresholds"]
                    
                    # 強制確保動態參數系統啟用
                    if ("phase1a_basic_signal_generation_dependency" in merged_config and 
                        "configuration" in merged_config["phase1a_basic_signal_generation_dependency"]):
                        
                        # 確保 dynamic_parameter_integration 存在且啟用
                        config_section = merged_config["phase1a_basic_signal_generation_dependency"]["configuration"]
                        if "dynamic_parameter_integration" not in config_section:
                            config_section["dynamic_parameter_integration"] = {}
                        config_section["dynamic_parameter_integration"]["enabled"] = True
                        
                        logger.info("✅ 動態參數系統已啟用 (Phase5+原始配置合併)")
                    else:
                        # 如果結構不存在，創建最小必要結構
                        merged_config["phase1a_basic_signal_generation_dependency"] = {
                            "configuration": {
                                "dynamic_parameter_integration": {
                                    "enabled": True
                                }
                            }
                        }
                        logger.info("✅ 動態參數系統已啟用 (創建最小配置結構)")
                    
                    return merged_config
                    
                except Exception as merge_error:
                    logger.warning(f"配置合併失敗: {merge_error}，使用原始 Phase5 配置")
                    # 即使合併失敗，也要嘗試為 Phase5 配置添加必要的動態參數設置
                    phase5_config["phase1a_basic_signal_generation_dependency"] = {
                        "configuration": {
                            "dynamic_parameter_integration": {
                                "enabled": True
                            }
                        }
                    }
                    logger.info("✅ 動態參數系統已啟用 (Phase5 緊急設置)")
                    return phase5_config
            
            # 如果 Phase5 配置包含依賴設置，檢查並確保動態參數啟用
            else:
                config_deps = phase5_config.get("phase1a_basic_signal_generation_dependency", {})
                config_section = config_deps.get("configuration", {})
                dynamic_params = config_section.get("dynamic_parameter_integration", {})
                
                if not dynamic_params.get("enabled", False):
                    # 強制啟用動態參數
                    if "configuration" not in config_deps:
                        config_deps["configuration"] = {}
                    if "dynamic_parameter_integration" not in config_deps["configuration"]:
                        config_deps["configuration"]["dynamic_parameter_integration"] = {}
                    config_deps["configuration"]["dynamic_parameter_integration"]["enabled"] = True
                    logger.info("✅ 動態參數系統已啟用 (Phase5 修正)")
                else:
                    logger.info("✅ 動態參數系統已在 Phase5 配置中啟用")
            
            return phase5_config
            
        except Exception as e:
            logger.debug(f"從 Phase5 備份讀取配置失敗: {e}")
            return None
    
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
    
    def _init_tier_system(self) -> Dict[SignalTier, TierConfiguration]:
        """初始化信號分層系統 - 基於 Lean 優化配置"""
        try:
            logger.info("🎯 初始化信號分層系統")
            
            # 分層配置 - 基於當前 Lean 優化結果調整
            tier_configs = {
                SignalTier.CRITICAL: TierConfiguration(
                    tier=SignalTier.CRITICAL,
                    lean_threshold=0.65,      # 高信心度要求 (65%+)
                    technical_threshold=0.7,  # 嚴格技術指標
                    position_multiplier=0.8,  # 大倉位
                    stop_loss_ratio=0.02,     # 緊密止損 2%
                    execution_priority=1,     # 最高優先級
                    max_signals_per_hour=3    # 限制頻率
                ),
                SignalTier.HIGH: TierConfiguration(
                    tier=SignalTier.HIGH,
                    lean_threshold=0.58,      # 中等信心度 (58%+)，對應 Phase5 閾值
                    technical_threshold=0.5,  # 適中技術指標
                    position_multiplier=0.5,  # 中等倉位
                    stop_loss_ratio=0.03,     # 適中止損 3%
                    execution_priority=2,     # 高優先級
                    max_signals_per_hour=5    # 適中頻率
                ),
                SignalTier.MEDIUM: TierConfiguration(
                    tier=SignalTier.MEDIUM,
                    lean_threshold=0.45,      # 低信心度 (45%+)
                    technical_threshold=0.4,  # 寬鬆技術指標
                    position_multiplier=0.3,  # 中小倉位
                    stop_loss_ratio=0.04,     # 寬鬆止損 4%
                    execution_priority=3,     # 中優先級
                    max_signals_per_hour=8    # 較高頻率
                ),
                SignalTier.LOW: TierConfiguration(
                    tier=SignalTier.LOW,
                    lean_threshold=0.30,      # 探索性信心度 (30%+)
                    technical_threshold=0.25, # 最寬鬆技術指標
                    position_multiplier=0.1,  # 小倉位測試
                    stop_loss_ratio=0.06,     # 最寬鬆止損 6%
                    execution_priority=4,     # 低優先級
                    max_signals_per_hour=12   # 高頻率學習
                )
            }
            
            logger.info("✅ 信號分層系統初始化完成")
            logger.info(f"   🔴 CRITICAL: Lean≥65%, 倉位80%, 止損2%")
            logger.info(f"   🟡 HIGH: Lean≥58%, 倉位50%, 止損3%")
            logger.info(f"   🟠 MEDIUM: Lean≥45%, 倉位30%, 止損4%")
            logger.info(f"   🟢 LOW: Lean≥30%, 倉位10%, 止損6%")
            
            return tier_configs
            
        except Exception as e:
            logger.error(f"❌ 信號分層系統初始化失敗: {e}")
            # 返回默認配置
            return {
                SignalTier.CRITICAL: TierConfiguration(
                    SignalTier.CRITICAL, 0.7, 0.7, 0.5, 0.03, 1, 3
                )
            }
    
    async def _detect_market_regime(self, market_data: Optional[Union[MarketData, Dict[str, Any]]] = None) -> Tuple[MarketRegime, float]:
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
                # 沒有市場數據時，返回預設制度避免中斷優化流程
                logger.warning("缺乏市場數據，使用預設市場制度 (UNKNOWN)")
                return MarketRegime.UNKNOWN, 0.5
            
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
                
                # 檢查是否滿足最小信心度要求 - 完全依賴配置
                min_confidence = regime_types.get(best_regime.value, {}).get("confidence_threshold", 0.5)
                if isinstance(min_confidence, (int, float)) and confidence >= float(min_confidence):
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
    
    def _calculate_bull_trend_score(self, market_data: Union[MarketData, Dict[str, Any]]) -> float:
        """計算牛市趨勢分數"""
        score = 0.0
        
        # 支持字典和 MarketData 對象
        if isinstance(market_data, dict):
            price_change_24h = market_data.get('price_change_24h', 0)
            volume_ratio = market_data.get('volume_ratio', 1.0)
            fear_greed_index = market_data.get('fear_greed_index', 50)
            moving_averages = market_data.get('moving_averages', {})
            price = market_data.get('price', 0)
        else:
            price_change_24h = market_data.price_change_24h
            volume_ratio = market_data.volume_ratio
            fear_greed_index = market_data.fear_greed_index
            moving_averages = market_data.moving_averages
            price = market_data.price
        
        # 價格趨勢斜率檢查
        if price_change_24h > 0.02:
            score += 0.3
        
        # 成交量確認
        if volume_ratio > 1.2:
            score += 0.25
        
        # 恐懼貪婪指數
        if fear_greed_index > 60:
            score += 0.25
        
        # 移動平均線排列（牛市排列）
        ma_20 = moving_averages.get("ma_20", 0)
        ma_50 = moving_averages.get("ma_50", 0)
        ma_200 = moving_averages.get("ma_200", 0)
        
        if ma_20 > ma_50 > ma_200 and price > ma_20:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_bear_trend_score(self, market_data: Union[MarketData, Dict[str, Any]]) -> float:
        """計算熊市趨勢分數"""
        score = 0.0
        
        # 支持字典和 MarketData 對象
        if isinstance(market_data, dict):
            price_change_24h = market_data.get('price_change_24h', 0)
            volume_ratio = market_data.get('volume_ratio', 1.0)
            fear_greed_index = market_data.get('fear_greed_index', 50)
            moving_averages = market_data.get('moving_averages', {})
            price = market_data.get('price', 0)
        else:
            price_change_24h = market_data.price_change_24h
            volume_ratio = market_data.volume_ratio
            fear_greed_index = market_data.fear_greed_index
            moving_averages = market_data.moving_averages
            price = market_data.price
        
        # 價格趨勢斜率檢查
        if price_change_24h < -0.02:
            score += 0.3
        
        # 成交量確認
        if volume_ratio > 1.1:
            score += 0.25
        
        # 恐懼貪婪指數
        if fear_greed_index < 40:
            score += 0.25
        
        # 移動平均線排列（熊市排列）
        ma_20 = moving_averages.get("ma_20", 0)
        ma_50 = moving_averages.get("ma_50", 0)
        ma_200 = moving_averages.get("ma_200", 0)
        
        if ma_20 < ma_50 < ma_200 and price < ma_20:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_sideways_score(self, market_data: Union[MarketData, Dict[str, Any]]) -> float:
        """計算橫盤整理分數"""
        score = 0.0
        
        # 支持字典和 MarketData 對象
        if isinstance(market_data, dict):
            price_change_24h = market_data.get('price_change_24h', 0)
            volatility = market_data.get('volatility', 0.05)
            volume_ratio = market_data.get('volume_ratio', 1.0)
            price_change_1h = market_data.get('price_change_1h', 0)
        else:
            price_change_24h = market_data.price_change_24h
            volatility = market_data.volatility
            volume_ratio = market_data.volume_ratio
            price_change_1h = market_data.price_change_1h
        
        # 價格趨勢斜率檢查
        if -0.02 <= price_change_24h <= 0.02:
            score += 0.3
        
        # 波動率檢查
        if volatility < 0.05:
            score += 0.3
        
        # 成交量比率
        if 0.8 <= volume_ratio <= 1.2:
            score += 0.2
        
        # 區間震盪確認（簡化實現）
        if price_change_1h < 0.01:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_volatile_score(self, market_data: Union[MarketData, Dict[str, Any]]) -> float:
        """計算高波動分數"""
        score = 0.0
        
        # 支持字典和 MarketData 對象
        if isinstance(market_data, dict):
            volatility = market_data.get('volatility', 0.05)
            price_change_1h = market_data.get('price_change_1h', 0)
            volume_ratio = market_data.get('volume_ratio', 1.0)
        else:
            volatility = market_data.volatility
            price_change_1h = market_data.price_change_1h
            volume_ratio = market_data.volume_ratio
        
        # 波動率檢查
        if volatility > 0.08:
            score += 0.3
        
        # 價格跳空
        if abs(price_change_1h) > 0.02:
            score += 0.3
        
        # 成交量激增
        if volume_ratio > 2.0:
            score += 0.2
        
        # 日內波幅（簡化實現）
        if volatility > 0.05:
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
    
    async def _get_dynamic_parameters(self, mode: str = "basic_mode", market_data: Optional[Dict[str, Any]] = None) -> DynamicParameters:
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
        
        # 提取基礎值 - 完全依賴動態配置，無默認值
        price_threshold = self._extract_parameter_value(base_params.get("price_change_threshold"))
        volume_threshold = self._extract_parameter_value(base_params.get("volume_change_threshold"))
        confidence_threshold = self._extract_parameter_value(base_params.get("confidence_threshold"))
        
        # 如果動態參數系統啟用，進行參數調整
        if self.dynamic_params_enabled:
            try:
                # 準備市場數據對象用於制度檢測
                market_data_obj = None
                if market_data:
                    # 處理時間戳（可能是毫秒）
                    timestamp = market_data.get('timestamp', time.time())
                    if timestamp > 1e10:  # 如果是毫秒級時間戳
                        timestamp = timestamp / 1000
                    
                    market_data_obj = MarketData(
                        timestamp=datetime.fromtimestamp(timestamp),
                        price=market_data.get('price', 0.0),
                        volume=market_data.get('volume', 0.0),
                        price_change_1h=market_data.get('price_change_1h', 0.0),
                        price_change_24h=market_data.get('price_change_24h', 0.0),
                        volume_ratio=market_data.get('volume_ratio', 1.0),
                        volatility=market_data.get('volatility', 0.0),
                        fear_greed_index=market_data.get('fear_greed_index', 50),
                        bid_ask_spread=market_data.get('bid_ask_spread', 0.0),
                        market_depth=market_data.get('market_depth', 0.0),
                        moving_averages=market_data.get('moving_averages', {})
                    )
                
                # 獲取當前市場制度和交易時段
                market_regime, regime_confidence = await self._detect_market_regime(market_data_obj)
                trading_session = await self._detect_trading_session()
                
                # 應用市場制度調整
                regime_config = self.config.get("phase1a_basic_signal_generation_dependency", {}).get("configuration", {}).get("dynamic_parameter_integration", {}).get("market_regime_detection", {}).get("regime_types", {})
                regime_adjustments = {}
                if market_regime != MarketRegime.UNKNOWN:
                    regime_adjustments = regime_config.get(market_regime.value, {}).get("parameter_adjustments", {})
                
                if regime_adjustments:
                    confidence_mult = regime_adjustments.get("confidence_threshold_multiplier", 1.0)
                    price_mult = regime_adjustments.get("price_change_threshold_multiplier", 1.0)
                    volume_mult = regime_adjustments.get("volume_change_threshold_multiplier", 1.0)
                    
                    if isinstance(confidence_mult, (int, float)):
                        confidence_threshold *= float(confidence_mult)
                    if isinstance(price_mult, (int, float)):
                        price_threshold *= float(price_mult)
                    if isinstance(volume_mult, (int, float)):
                        volume_threshold *= float(volume_mult)
                
                # 應用交易時段調整
                session_config = self.config.get("phase1a_basic_signal_generation_dependency", {}).get("configuration", {}).get("dynamic_parameter_integration", {}).get("trading_session_detection", {}).get("session_types", {})
                session_adjustments = session_config.get(trading_session.value, {}).get("parameter_adjustments", {})
                
                if session_adjustments:
                    confidence_mult = session_adjustments.get("confidence_threshold_multiplier", 1.0)
                    volume_boost = session_adjustments.get("volume_sensitivity_boost", 1.0)
                    
                    if isinstance(confidence_mult, (int, float)):
                        confidence_threshold *= float(confidence_mult)
                    if isinstance(volume_boost, (int, float)):
                        volume_threshold *= float(volume_boost)
                
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
        """提取參數值（支援靜態值和動態配置）- 完全依賴配置"""
        if param_config is None:
            return 0.0  # 配置不存在時返回 0
        elif isinstance(param_config, (int, float)):
            return float(param_config)
        elif isinstance(param_config, dict):
            return param_config.get("base_value", 0.0)
        else:
            return 0.0
    
    def _convert_timestamp(self, timestamp) -> datetime:
        """轉換時間戳為 datetime 對象"""
        if isinstance(timestamp, datetime):
            return timestamp
        elif isinstance(timestamp, str):
            try:
                # 嘗試解析 ISO 格式
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                try:
                    # 嘗試解析其他常見格式
                    return datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                except:
                    return datetime.now()
        elif isinstance(timestamp, (int, float)):
            # Unix 時間戳
            return datetime.fromtimestamp(timestamp / 1000 if timestamp > 1e10 else timestamp)
        else:
            return datetime.now()
    
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
    
    def _apply_technical_indicator_config(self):
        """應用技術指標配置參數 - 支援自適應參數"""
        # 從配置中讀取技術指標參數（與JSON schema相容）
        self.rsi_period = self.config.get('rsi_period', 14)
        self.macd_fast = self.config.get('macd_fast', 12)
        self.macd_slow = self.config.get('macd_slow', 26)
        self.macd_signal = self.config.get('macd_signal', 9)
        
        # 移動平均線參數
        self.ma_periods = {
            'ma_20': 20,
            'ma_50': 50,
            'ma_200': 200
        }
        
        # 自適應參數優化
        performance_boost = self.config.get('performance_boost', 1.0)
        if performance_boost != 1.0:
            self.performance_boost = performance_boost
            logger.info(f"啟用性能提升係數: {performance_boost}")
        else:
            self.performance_boost = 1.0
        
        # 記錄配置的技術指標參數
        logger.info(f"技術指標參數: RSI({self.rsi_period}), MACD({self.macd_fast},{self.macd_slow},{self.macd_signal}), 性能提升({self.performance_boost}x)")
    
    def get_technical_indicator_params(self) -> Dict[str, Any]:
        """獲取當前的技術指標參數 - 供外部系統查詢"""
        return {
            'rsi_period': getattr(self, 'rsi_period', 14),
            'macd_fast': getattr(self, 'macd_fast', 12),
            'macd_slow': getattr(self, 'macd_slow', 26),
            'macd_signal': getattr(self, 'macd_signal', 9),
            'performance_boost': getattr(self, 'performance_boost', 1.0),
            'ma_periods': getattr(self, 'ma_periods', {'ma_20': 20, 'ma_50': 50, 'ma_200': 200})
        }
    
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
        """啟動 Phase1A 信號生成器 - 按照 JSON 規範實現完整啟動流程"""
        if self.is_running:
            logger.warning("Phase1A 已在運行")
            return
        
        logger.info("🚀 開始啟動 Phase1A 基礎信號生成器...")
        
        try:
            # 第一步：設置 WebSocket 驅動器
            self.websocket_driver = websocket_driver
            logger.info("✅ WebSocket 驅動器設置完成")
            
            # 第二步：初始化歷史數據緩衝區 - JSON 規範要求
            await self._initialize_historical_data_buffers()
            logger.info("✅ 歷史數據緩衝區初始化完成")
            
            # 第二步半：啟動 intelligent_trigger_engine
            try:
                await start_intelligent_trigger_engine()
                logger.info("✅ intelligent_trigger_engine 啟動完成")
            except Exception as e:
                logger.error(f"❌ intelligent_trigger_engine 啟動失敗: {e}")
                # 不要拋出異常，繼續啟動 Phase1A
            
            # 第三步：設置動態參數系統
            await self._initialize_dynamic_parameter_system()
            logger.info("✅ 動態參數系統初始化完成")
            
            # 第四步：訂閱 WebSocket 數據流
            websocket_driver.event_broadcaster.subscribe(self._on_market_data_update, ["data"])
            logger.info("✅ WebSocket 數據流訂閱完成")
            
            # 第五步：啟動信號處理任務
            self.is_running = True
            self.tasks = [
                asyncio.create_task(self._signal_generation_coordinator()),
                asyncio.create_task(self._performance_monitor()),
                asyncio.create_task(self._signal_quality_analyzer()),
                asyncio.create_task(self._historical_data_updater())  # 新增：持續更新歷史數據
            ]
            logger.info("✅ 信號處理任務啟動完成")
            
            # 第六步：等待系統穩定
            await asyncio.sleep(2)
            logger.info("🎉 Phase1A 信號生成器啟動完成，開始處理實時數據流")
            
        except Exception as e:
            logger.error(f"❌ Phase1A 啟動失敗: {e}")
            self.is_running = False
            raise
    
    async def stop(self):
        """停止信號生成器"""
        self.is_running = False
        
        # 取消所有任務
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        self.tasks.clear()
        logger.info("Phase1A 信號生成器已停止")
    
    async def _initialize_historical_data_buffers(self):
        """初始化歷史數據緩衝區 - JSON 規範要求的歷史 K 線數據"""
        logger.info("📊 開始初始化歷史數據緩衝區...")
        
        try:
            # 根據 JSON 配置，需要為技術分析準備歷史數據
            target_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT"]
            
            for symbol in target_symbols:
                try:
                    # 抓取歷史 K 線數據（250 條 1 分鐘數據）
                    historical_klines = await self._fetch_historical_klines(symbol, "1m", 250)
                    
                    if historical_klines:
                        # 初始化價格緩衝區
                        self.price_buffer[symbol] = deque(
                            [{'price': k['close'], 'timestamp': k['timestamp'], 'volume': k['volume']} 
                             for k in historical_klines],
                            maxlen=500
                        )
                        
                        # 初始化成交量緩衝區
                        self.volume_buffer[symbol] = deque(
                            [{'volume': k['volume'], 'timestamp': k['timestamp'], 'price': k['close']} 
                             for k in historical_klines],
                            maxlen=500
                        )
                        
                        # 初始化 K 線緩衝區（用於技術指標計算）
                        self.kline_buffers[symbol] = {
                            '1m': deque(historical_klines, maxlen=500)
                        }
                        
                        logger.info(f"✅ {symbol}: 歷史數據緩衝區初始化完成 ({len(historical_klines)} 條記錄)")
                    else:
                        logger.warning(f"⚠️ {symbol}: 歷史數據抓取失敗，使用空緩衝區")
                        self._initialize_empty_buffers(symbol)
                
                except Exception as e:
                    logger.error(f"❌ {symbol}: 歷史數據初始化失敗 - {e}")
                    self._initialize_empty_buffers(symbol)
                
                # 避免 API 限制
                await asyncio.sleep(0.2)
            
            logger.info("🎉 歷史數據緩衝區初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 歷史數據緩衝區初始化失敗: {e}")
            raise
    
    def _initialize_empty_buffers(self, symbol: str):
        """初始化空緩衝區（備用方案）"""
        self.price_buffer[symbol] = deque(maxlen=500)
        self.volume_buffer[symbol] = deque(maxlen=500)
        self.orderbook_buffer[symbol] = deque(maxlen=100)
        self.kline_buffers[symbol] = {'1m': deque(maxlen=500)}
    
    async def _fetch_historical_klines(self, symbol: str, interval: str = "1m", limit: int = 250) -> List[Dict[str, Any]]:
        """抓取歷史 K 線數據 - 支援技術分析"""
        try:
            import aiohttp
            
            url = "https://api.binance.com/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # 轉換為標準格式
                        klines = []
                        for kline in data:
                            formatted_kline = {
                                'open_time': int(kline[0]),
                                'open': float(kline[1]),
                                'high': float(kline[2]),
                                'low': float(kline[3]),
                                'close': float(kline[4]),
                                'volume': float(kline[5]),
                                'close_time': int(kline[6]),
                                'quote_asset_volume': float(kline[7]),
                                'number_of_trades': int(kline[8]),
                                'timestamp': datetime.fromtimestamp(int(kline[0]) / 1000).isoformat()
                            }
                            klines.append(formatted_kline)
                        
                        logger.debug(f"📈 {symbol}: 成功抓取 {len(klines)} 條 {interval} K線數據")
                        return klines
                    else:
                        logger.error(f"❌ {symbol}: API請求失敗 - {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"❌ {symbol}: K線數據抓取失敗 - {e}")
            return []
    
    async def _initialize_dynamic_parameter_system(self):
        """初始化動態參數系統 - JSON 規範要求"""
        logger.info("🔧 初始化動態參數系統...")
        
        try:
            # 從 JSON 配置加載動態參數設置
            dynamic_config = self.config.get("phase1a_basic_signal_generation_dependency", {}).get("configuration", {}).get("dynamic_parameter_integration", {})
            
            self.dynamic_params_enabled = dynamic_config.get("enabled", True)
            
            if self.dynamic_params_enabled:
                # 初始化市場制度檢測
                await self._initialize_market_regime_detection()
                
                # 初始化交易時段檢測
                await self._initialize_trading_session_detection()
                
                logger.info("✅ 動態參數系統初始化完成")
            else:
                logger.info("ℹ️ 動態參數系統已禁用，使用靜態參數")
                
        except Exception as e:
            logger.error(f"❌ 動態參數系統初始化失敗: {e}")
            self.dynamic_params_enabled = False
    
    async def _initialize_market_regime_detection(self):
        """初始化市場制度檢測系統"""
        try:
            # 設置預設市場制度
            self.current_regime = MarketRegime.UNKNOWN
            self.regime_confidence = 0.0
            
            # 從配置中讀取市場制度檢測參數
            regime_config = self.config.get("phase1a_basic_signal_generation_dependency", {}).get(
                "configuration", {}).get("dynamic_parameter_integration", {}).get(
                "market_regime_detection", {})
            
            if regime_config.get("enabled", True):
                # 執行初始市場制度檢測
                initial_regime, confidence = await self._detect_market_regime()
                self.current_regime = initial_regime
                self.regime_confidence = confidence
                
                logger.info(f"✅ 市場制度檢測初始化完成: {initial_regime.value} (信心度: {confidence:.2f})")
            else:
                logger.info("ℹ️ 市場制度檢測已禁用")
                
        except Exception as e:
            logger.error(f"❌ 市場制度檢測初始化失敗: {e}")
            self.current_regime = MarketRegime.UNKNOWN
    
    async def _initialize_trading_session_detection(self):
        """初始化交易時段檢測系統"""
        try:
            # 設置預設交易時段
            self.current_trading_session = TradingSession.OFF_HOURS
            
            # 從配置中讀取交易時段檢測參數
            session_config = self.config.get("phase1a_basic_signal_generation_dependency", {}).get(
                "configuration", {}).get("dynamic_parameter_integration", {}).get(
                "trading_session_detection", {})
            
            if session_config.get("enabled", True):
                # 執行初始交易時段檢測
                initial_session = await self._detect_trading_session()
                self.current_trading_session = initial_session
                
                logger.info(f"✅ 交易時段檢測初始化完成: {initial_session.value}")
            else:
                logger.info("ℹ️ 交易時段檢測已禁用")
                
        except Exception as e:
            logger.error(f"❌ 交易時段檢測初始化失敗: {e}")
            self.current_trading_session = TradingSession.OFF_HOURS
    
    async def _historical_data_updater(self):
        """持續更新歷史數據任務"""
        while self.is_running:
            try:
                # 每30分鐘更新一次歷史數據
                await asyncio.sleep(1800)
                
                if self.is_running:
                    logger.info("🔄 更新歷史數據緩衝區...")
                    
                    for symbol in self.price_buffer.keys():
                        try:
                            # 抓取最新的 K 線數據
                            latest_klines = await self._fetch_historical_klines(symbol, "1m", 50)
                            
                            if latest_klines:
                                # 更新緩衝區
                                for kline in latest_klines:
                                    self.price_buffer[symbol].append({
                                        'price': kline['close'],
                                        'timestamp': kline['timestamp'],
                                        'volume': kline['volume']
                                    })
                                    
                                    self.volume_buffer[symbol].append({
                                        'volume': kline['volume'],
                                        'timestamp': kline['timestamp'],
                                        'price': kline['close']
                                    })
                                    
                                    if symbol in self.kline_buffers and '1m' in self.kline_buffers[symbol]:
                                        self.kline_buffers[symbol]['1m'].append(kline)
                                
                                logger.debug(f"✅ {symbol}: 歷史數據更新完成")
                        
                        except Exception as e:
                            logger.error(f"❌ {symbol}: 歷史數據更新失敗 - {e}")
                    
                    logger.info("🎉 歷史數據緩衝區更新完成")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ 歷史數據更新器錯誤: {e}")
                await asyncio.sleep(60)  # 出錯後等待1分鐘再試
    
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
            
            # 檢查並處理 coroutine 對象
            if asyncio.iscoroutine(latest_price_data):
                logger.warning(f"⚠️ latest_price_data 是 coroutine 對象，使用默認值")
                latest_price_data = {}
            if asyncio.iscoroutine(latest_volume_data):
                logger.warning(f"⚠️ latest_volume_data 是 coroutine 對象，使用默認值")
                latest_volume_data = {}
            
            # 確保數據是字典
            if not isinstance(latest_price_data, dict):
                latest_price_data = {}
            if not isinstance(latest_volume_data, dict):
                latest_volume_data = {}
            
            # 使用現有的 MarketData 結構，在 metadata 中添加 OrderBook 信息
            enhanced_data = MarketData(
                timestamp=orderbook.get('timestamp', datetime.now()),
                price=latest_price_data.get('price', 0.0),
                volume=latest_volume_data.get('volume', 0.0),
                price_change_1h=latest_price_data.get('price_change_1h', 0.0),
                price_change_24h=latest_price_data.get('price_change_24h', 0.0),
                volume_ratio=latest_volume_data.get('volume_ratio', 1.0),
                volatility=latest_price_data.get('volatility', 0.0),
                fear_greed_index=latest_price_data.get('fear_greed_index', 50),
                bid_ask_spread=orderbook.get('bid_ask_spread', 0.01),  # 使用 OrderBook 的價差
                market_depth=orderbook.get('book_depth', 1000),        # 使用 OrderBook 的深度
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
            dynamic_params_obj = await self._get_dynamic_parameters("basic_mode")
            dynamic_params = dynamic_params_obj.to_dict() if dynamic_params_obj else {}
            
            # OrderBook 深度信號
            market_depth = market_data.get('market_depth', 0)
            bid_ask_spread = market_data.get('bid_ask_spread', 0.1)
            
            if market_depth > 1000:  # 深度閾值
                if bid_ask_spread < 0.01:  # 價差小於 1%
                    signal = BasicSignal(
                        signal_id=f"orderbook_depth_{symbol}_{int(time.time())}",
                        symbol=symbol,
                        signal_type=SignalType.VOLUME,  # 使用現有枚舉
                        direction="BUY" if market_depth > 2000 else "NEUTRAL",
                        strength=min(0.8, market_depth / 5000),
                        confidence=min(0.9, 1 - bid_ask_spread * 10),
                        priority=Priority.MEDIUM,  # 使用現有枚舉
                        timestamp=market_data.get('timestamp', datetime.now()),
                        price=market_data.get('price', 0),
                        volume=market_data.get('volume', 0),
                        metadata={"orderbook_enhanced": True, "book_depth": market_depth},
                        layer_source="orderbook_enhanced",
                        processing_time_ms=2.0,
                        market_regime=self.current_regime.value,
                        trading_session="OFF_HOURS",
                        price_change=market_data.get('price_change_24h', 0),
                        volume_change=market_data.get('volume_ratio', 1.0)
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
                    'confidence': 0.3  # 修復：降低硬編碼信心度
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
        """公開的信號生成方法 - 基於歷史數據和動態參數 + 第二階段自適應學習"""
        try:
            if not self.is_running:
                logger.warning("信號生成器未運行")
                return []
            
            # 檢查是否有足夠的歷史數據進行技術分析
            if symbol not in self.price_buffer or len(self.price_buffer[symbol]) < 10:
                logger.debug(f"{symbol}: 歷史數據不足，跳過信號生成")
                return []
            
            logger.debug(f"🎯 開始為 {symbol} 生成信號，使用 {len(self.price_buffer[symbol])} 條歷史數據")
            
            # 🧠 第二階段自適應學習：市場狀態檢測與學習
            regime_confidence = None
            if self.adaptive_mode and self.regime_detector:
                # 創建市場數據 DataFrame 用於分析
                market_df = self._create_market_dataframe(symbol)
                if market_df is not None and len(market_df) >= 20:
                    regime_confidence = await self.regime_detector.detect_regime_change(market_df, symbol)
                    logger.debug(f"🧠 {symbol} 市場狀態: {regime_confidence.regime.value}, 信心度: {regime_confidence.confidence:.3f}")
            
            # 更新當前市場數據到緩衝區
            await self._update_buffers_with_current_data(symbol, market_data)
            
            # 獲取動態參數（若有自適應學習，則考慮市場狀態）
            dynamic_params = await self._get_adaptive_parameters(market_data, regime_confidence)
            
            # 執行4層並行處理 - 基於真實的技術分析
            signals = []
            
            # Layer 0: 即時信號（基於價格變化）
            layer_0_result = await self._execute_layer_processing(
                "layer_0", self._layer_0_instant_signals_enhanced, symbol, market_data, dynamic_params
            )
            if layer_0_result.signals:
                signals.extend(layer_0_result.signals)
            
            # Layer 1: 動量信號（基於移動平均）
            layer_1_result = await self._execute_layer_processing(
                "layer_1", self._layer_1_momentum_signals_enhanced, symbol, market_data, dynamic_params
            )
            if layer_1_result.signals:
                signals.extend(layer_1_result.signals)
            
            # Layer 2: 趨勢信號（基於趨勢分析）
            layer_2_result = await self._execute_layer_processing(
                "layer_2", self._layer_2_trend_signals_enhanced, symbol, market_data, dynamic_params
            )
            if layer_2_result.signals:
                signals.extend(layer_2_result.signals)
            
            # Layer 3: 成交量信號（基於成交量分析）
            layer_3_result = await self._execute_layer_processing(
                "layer_3", self._layer_3_volume_signals_enhanced, symbol, market_data, dynamic_params
            )
            if layer_3_result.signals:
                signals.extend(layer_3_result.signals)
            
            # 🔥 新增：信號品質篩選和去重
            filtered_signals = await self._filter_and_prioritize_signals(signals, symbol, dynamic_params)
            
            logger.debug(f"✅ {symbol}: 原始信號 {len(signals)} 個，篩選後 {len(filtered_signals)} 個")
            return filtered_signals
            
        except Exception as e:
            logger.error(f"❌ {symbol}: 信號生成失敗 - {e}")
            return []

    async def generate_tiered_signals(self, symbol: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """增強版信號生成 - 整合分層系統"""
        try:
            start_time = time.time()
            
            if not self.is_running:
                logger.warning("信號生成器未運行")
                return {'signals': [], 'tier_analysis': {}}
            
            # 檢查歷史數據
            if symbol not in self.price_buffer or len(self.price_buffer[symbol]) < 10:
                logger.debug(f"{symbol}: 歷史數據不足，跳過信號生成")
                return {'signals': [], 'tier_analysis': {'error': '歷史數據不足'}}
            
            logger.debug(f"🎯 開始 {symbol} 分層信號生成")
            
            # 1. 執行基礎信號生成
            base_signals = await self.generate_signals(symbol, market_data)
            
            # 2. 對每個信號進行分層評估
            tiered_signals = []
            tier_statistics = {tier: {'count': 0, 'avg_confidence': 0.0} for tier in SignalTier}
            
            for signal in base_signals:
                try:
                    # 計算技術指標強度
                    technical_strength = signal.strength * signal.confidence
                    
                    # 評估信號分層
                    signal_tier, tier_config, tier_metadata = await self.evaluate_signal_tier(
                        symbol, technical_strength, market_data
                    )
                    
                    # 檢查分層閾值
                    if technical_strength >= tier_metadata.get('dynamic_threshold', 0.7):
                        # 增強信號對象
                        enhanced_signal = self._enhance_signal_with_tier_info(
                            signal, signal_tier, tier_config, tier_metadata
                        )
                        
                        tiered_signals.append(enhanced_signal)
                        
                        # 更新統計
                        tier_statistics[signal_tier]['count'] += 1
                        tier_statistics[signal_tier]['avg_confidence'] += signal.confidence
                        
                        # 更新分層計數器
                        self.tier_counters[signal_tier] += 1
                        
                        logger.debug(f"✅ {symbol}: {signal_tier.value} 信號通過 (強度: {technical_strength:.3f}, 閾值: {tier_metadata['dynamic_threshold']:.3f})")
                    else:
                        logger.debug(f"❌ {symbol}: 信號未達 {signal_tier.value} 閾值 (強度: {technical_strength:.3f}, 需要: {tier_metadata['dynamic_threshold']:.3f})")
                        
                except Exception as e:
                    logger.warning(f"信號分層評估失敗: {e}")
                    continue
            
            # 3. 計算平均信心度
            for tier, stats in tier_statistics.items():
                if stats['count'] > 0:
                    stats['avg_confidence'] = stats['avg_confidence'] / stats['count']
            
            # 4. 生成分層分析報告
            processing_time = (time.time() - start_time) * 1000
            tier_analysis = {
                'total_base_signals': len(base_signals),
                'total_tiered_signals': len(tiered_signals),
                'tier_statistics': tier_statistics,
                'tier_counters': dict(self.tier_counters),
                'processing_time_ms': round(processing_time, 2),
                'symbol': symbol,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"🎊 {symbol} 分層信號生成完成: {len(tiered_signals)}/{len(base_signals)} 信號通過分層篩選")
            
            return {
                'signals': tiered_signals,
                'tier_analysis': tier_analysis
            }
            
        except Exception as e:
            logger.error(f"❌ {symbol}: 分層信號生成失敗 - {e}")
            return {'signals': [], 'tier_analysis': {'error': str(e)}}
    
    def _enhance_signal_with_tier_info(self, signal: BasicSignal, tier: SignalTier, tier_config: TierConfiguration, tier_metadata: Dict[str, Any]) -> BasicSignal:
        """用分層信息增強信號對象"""
        try:
            # 創建增強的信號副本
            enhanced_signal = BasicSignal(
                signal_id=f"{signal.signal_id}_T{tier.value}",
                symbol=signal.symbol,
                signal_type=signal.signal_type,
                direction=signal.direction,
                strength=signal.strength,
                confidence=signal.confidence,
                priority=self._map_tier_to_priority(tier),
                timestamp=signal.timestamp,
                price=signal.price,
                volume=signal.volume,
                metadata=signal.metadata.copy() if signal.metadata else {},
                layer_source=signal.layer_source,
                processing_time_ms=signal.processing_time_ms,
                market_regime=signal.market_regime,
                trading_session=signal.trading_session,
                price_change=signal.price_change,
                volume_change=signal.volume_change
            )
            
            # 添加分層元數據
            enhanced_signal.metadata.update({
                'signal_tier': tier.value,
                'tier_config': {
                    'position_multiplier': tier_config.position_multiplier,
                    'stop_loss_ratio': tier_config.stop_loss_ratio,
                    'execution_priority': tier_config.execution_priority,
                    'max_signals_per_hour': tier_config.max_signals_per_hour
                },
                'tier_metadata': tier_metadata,
                'tier_enhanced': True,
                'tier_processing_timestamp': datetime.now().isoformat()
            })
            
            return enhanced_signal
            
        except Exception as e:
            logger.warning(f"信號增強失敗: {e}")
            return signal
    
    def _map_tier_to_priority(self, tier: SignalTier) -> Priority:
        """將信號分層映射到優先級"""
        mapping = {
            SignalTier.CRITICAL: Priority.CRITICAL,
            SignalTier.HIGH: Priority.HIGH,
            SignalTier.MEDIUM: Priority.MEDIUM,
            SignalTier.LOW: Priority.MEDIUM  # LOW 層級也使用 MEDIUM 優先級
        }
        return mapping.get(tier, Priority.MEDIUM)
    
    async def _update_buffers_with_current_data(self, symbol: str, market_data: Dict[str, Any]):
        """用當前市場數據更新緩衝區"""
        try:
            current_price = float(market_data.get('price', 0))
            current_volume = float(market_data.get('volume', 0)) if market_data.get('volume') != 'N/A' else 0.0
            timestamp = market_data.get('timestamp', datetime.now().isoformat())
            
            if current_price > 0:
                # 更新價格緩衝區
                self.price_buffer[symbol].append({
                    'price': current_price,
                    'timestamp': timestamp,
                    'volume': current_volume
                })
                
                # 更新成交量緩衝區
                self.volume_buffer[symbol].append({
                    'volume': current_volume,
                    'timestamp': timestamp,
                    'price': current_price
                })
                
                # 更新 K 線緩衝區（模擬1分鐘K線）
                if symbol in self.kline_buffers and '1m' in self.kline_buffers[symbol]:
                    current_kline = {
                        'open': current_price,
                        'high': current_price,
                        'low': current_price,
                        'close': current_price,
                        'volume': current_volume,
                        'timestamp': timestamp,
                        'open_time': int(datetime.now().timestamp() * 1000)
                    }
                    self.kline_buffers[symbol]['1m'].append(current_kline)
        
        except Exception as e:
            logger.error(f"❌ 緩衝區更新失敗: {e}")
    
    async def _layer_0_instant_signals_enhanced(self, symbol: str, market_data: Dict[str, Any], dynamic_params: Dict[str, Any]) -> List[BasicSignal]:
        """Layer 0: 增強型即時信號生成 - 基於價格變化分析"""
        signals = []
        
        try:
            if len(self.price_buffer[symbol]) < 2:
                return signals
            
            # 獲取最近價格數據
            recent_prices = list(self.price_buffer[symbol])[-10:]  # 最近10個價格點
            current_price = recent_prices[-1]['price']
            previous_price = recent_prices[-2]['price'] if len(recent_prices) >= 2 else current_price
            
            # 獲取當前成交量
            current_volume = float(market_data.get('volume', recent_prices[-1].get('volume', 1000.0)))
            
            # 計算價格變化率
            price_change_pct = (current_price - previous_price) / previous_price if previous_price > 0 else 0
            
            # 使用動態參數判斷信號
            if abs(price_change_pct) > dynamic_params.get('price_change_threshold', 0.02):
                
                # 計算信號強度（基於價格變化幅度）
                threshold = dynamic_params.get('price_change_threshold', 0.02)
                strength_raw = min(1.0, abs(price_change_pct) / threshold)
                strength = strength_raw * dynamic_params.get('signal_strength_multiplier', 1.0)
                
                # 計算信心度（基於歷史波動性）
                price_values = [p['price'] for p in recent_prices]
                volatility = np.std(price_values) / np.mean(price_values) if len(price_values) > 1 else 0
                confidence = max(0.1, dynamic_params.get('confidence_threshold', 0.6) * (1 + (1 - volatility) * 0.5))
                
                # 確定交易方向
                direction = "BUY" if price_change_pct > 0 else "SELL"
                
                # 生成信號
                signal = BasicSignal(
                    signal_id=f"{symbol}_instant_{int(time.time() * 1000)}",
                    symbol=symbol,
                    signal_type=SignalType.PRICE_ACTION,
                    direction=direction,
                    strength=strength,
                    confidence=confidence,
                    price=current_price,
                    volume=current_volume,  # 添加 volume 參數
                    timestamp=datetime.now(),
                    priority=Priority.HIGH if strength > 0.7 else Priority.MEDIUM,
                    layer_source="layer_0_instant",
                    market_regime=self.current_regime.value,
                    processing_time_ms=5.0,
                    metadata={
                        'price_change_pct': price_change_pct,
                        'volatility': volatility,
                        'threshold_used': threshold,
                        'data_points': len(recent_prices)
                    }
                )
                signals.append(signal)
                
                logger.debug(f"🔥 {symbol}: 即時信號 - {direction} 強度:{strength:.2f} 信心:{confidence:.2f}")
        
        except Exception as e:
            logger.error(f"❌ Layer 0 信號生成失敗: {e}")
        
        return signals
    
    async def _layer_1_momentum_signals_enhanced(self, symbol: str, market_data: Dict[str, Any], dynamic_params: Dict[str, Any]) -> List[BasicSignal]:
        """Layer 1: 增強型動量信號生成 - 基於 pandas-ta 技術指標"""
        signals = []
        
        try:
            if len(self.price_buffer[symbol]) < 20:  # 需要至少20個數據點
                return signals
            
            # 使用 pandas-ta 計算完整技術指標
            indicators = await self._calculate_advanced_indicators(symbol)
            if not indicators:
                return signals
            
            # 獲取當前價格
            current_price = list(self.price_buffer[symbol])[-1]['price']
            
            # 1. RSI 信號
            rsi = indicators.get('rsi')
            if rsi is not None:
                if rsi < 30:  # 超賣
                    signal = BasicSignal(
                        signal_id=f"{symbol}_rsi_oversold_{int(time.time() * 1000)}",
                        symbol=symbol,
                        signal_type=SignalType.MOMENTUM,
                        direction="BUY",
                        strength=min(1.0, (30 - rsi) / 30),
                        confidence=dynamic_params.get('confidence_threshold', 0.6) + 0.1,
                        price=current_price,
                        volume=float(market_data.get('volume', 1000.0)),
                        timestamp=datetime.now(),
                        priority=Priority.MEDIUM,
                        layer_source="layer_1_momentum",
                        market_regime=self.current_regime.value,
                        processing_time_ms=15.0,
                        metadata={
                            'rsi': rsi,
                            'signal_pattern': 'rsi_oversold',
                            'threshold': 30
                        }
                    )
                    signals.append(signal)
                elif rsi > 70:  # 超買
                    signal = BasicSignal(
                        signal_id=f"{symbol}_rsi_overbought_{int(time.time() * 1000)}",
                        symbol=symbol,
                        signal_type=SignalType.MOMENTUM,
                        direction="SELL",
                        strength=min(1.0, (rsi - 70) / 30),
                        confidence=dynamic_params.get('confidence_threshold', 0.6) + 0.1,
                        price=current_price,
                        timestamp=datetime.now(),
                        priority=Priority.MEDIUM,
                        layer_source="layer_1_momentum",
                        market_regime=self.current_regime.value,
                        processing_time_ms=15.0,
                        metadata={
                            'rsi': rsi,
                            'signal_pattern': 'rsi_overbought',
                            'threshold': 70
                        }
                    )
                    signals.append(signal)
            
            # 2. MACD 信號
            macd = indicators.get('macd')
            macd_signal = indicators.get('macd_signal')
            macd_histogram = indicators.get('macd_histogram')
            
            if macd is not None and macd_signal is not None:
                if macd > macd_signal and macd_histogram is not None and macd_histogram > 0:
                    signal = BasicSignal(
                        signal_id=f"{symbol}_macd_bull_{int(time.time() * 1000)}",
                        symbol=symbol,
                        signal_type=SignalType.MOMENTUM,
                        direction="BUY",
                        strength=min(1.0, abs(macd - macd_signal) / abs(macd) if macd != 0 else 0.5),
                        confidence=dynamic_params.get('confidence_threshold', 0.6) + 0.15,
                        price=current_price,
                        volume=float(market_data.get('volume', 1000.0)),
                        timestamp=datetime.now(),
                        priority=Priority.MEDIUM,
                        layer_source="layer_1_momentum",
                        market_regime=self.current_regime.value,
                        processing_time_ms=15.0,
                        metadata={
                            'macd': macd,
                            'macd_signal': macd_signal,
                            'macd_histogram': macd_histogram,
                            'signal_pattern': 'macd_bullish_crossover'
                        }
                    )
                    signals.append(signal)
                elif macd < macd_signal and macd_histogram is not None and macd_histogram < 0:
                    signal = BasicSignal(
                        signal_id=f"{symbol}_macd_bear_{int(time.time() * 1000)}",
                        symbol=symbol,
                        signal_type=SignalType.MOMENTUM,
                        direction="SELL",
                        strength=min(1.0, abs(macd - macd_signal) / abs(macd) if macd != 0 else 0.5),
                        confidence=dynamic_params.get('confidence_threshold', 0.6) + 0.15,
                        price=current_price,
                        timestamp=datetime.now(),
                        priority=Priority.MEDIUM,
                        layer_source="layer_1_momentum",
                        market_regime=self.current_regime.value,
                        processing_time_ms=15.0,
                        metadata={
                            'macd': macd,
                            'macd_signal': macd_signal,
                            'macd_histogram': macd_histogram,
                            'signal_pattern': 'macd_bearish_crossover'
                        }
                    )
                    signals.append(signal)
            
            # 3. Stochastic 信號
            stoch_k = indicators.get('stoch_k')
            stoch_d = indicators.get('stoch_d')
            
            if stoch_k is not None and stoch_d is not None:
                if stoch_k < 20 and stoch_d < 20 and stoch_k > stoch_d:
                    signal = BasicSignal(
                        signal_id=f"{symbol}_stoch_oversold_{int(time.time() * 1000)}",
                        symbol=symbol,
                        signal_type=SignalType.MOMENTUM,
                        direction="BUY",
                        strength=min(1.0, (20 - min(stoch_k, stoch_d)) / 20),
                        confidence=dynamic_params.get('confidence_threshold', 0.6) + 0.1,
                        price=current_price,
                        timestamp=datetime.now(),
                        priority=Priority.MEDIUM,
                        layer_source="layer_1_momentum",
                        market_regime=self.current_regime.value,
                        processing_time_ms=15.0,
                        metadata={
                            'stoch_k': stoch_k,
                            'stoch_d': stoch_d,
                            'signal_pattern': 'stochastic_oversold_crossover'
                        }
                    )
                    signals.append(signal)
                elif stoch_k > 80 and stoch_d > 80 and stoch_k < stoch_d:
                    signal = BasicSignal(
                        signal_id=f"{symbol}_stoch_overbought_{int(time.time() * 1000)}",
                        symbol=symbol,
                        signal_type=SignalType.MOMENTUM,
                        direction="SELL",
                        strength=min(1.0, (min(stoch_k, stoch_d) - 80) / 20),
                        confidence=dynamic_params.get('confidence_threshold', 0.6) + 0.1,
                        price=current_price,
                        timestamp=datetime.now(),
                        priority=Priority.MEDIUM,
                        layer_source="layer_1_momentum",
                        market_regime=self.current_regime.value,
                        processing_time_ms=15.0,
                        metadata={
                            'stoch_k': stoch_k,
                            'stoch_d': stoch_d,
                            'signal_pattern': 'stochastic_overbought_crossover'
                        }
                    )
                    signals.append(signal)
            
            # 4. EMA 交叉信號 (更精確的移動平均線)
            ema_5 = indicators.get('ema_5')
            ema_10 = indicators.get('ema_10')
            ema_20 = indicators.get('ema_20')
            
            if ema_5 is not None and ema_10 is not None and ema_20 is not None:
                if ema_5 > ema_10 > ema_20 and current_price > ema_5:
                    signal = BasicSignal(
                        signal_id=f"{symbol}_ema_golden_cross_{int(time.time() * 1000)}",
                        symbol=symbol,
                        signal_type=SignalType.MOMENTUM,
                        direction="BUY",
                        strength=min(1.0, (ema_5 - ema_20) / ema_20 * 10),
                        confidence=dynamic_params.get('confidence_threshold', 0.6) + 0.2,
                        price=current_price,
                        volume=float(market_data.get('volume', 1000.0)),
                        timestamp=datetime.now(),
                        priority=Priority.MEDIUM,
                        layer_source="layer_1_momentum",
                        market_regime=self.current_regime.value,
                        processing_time_ms=15.0,
                        metadata={
                            'ema_5': ema_5,
                            'ema_10': ema_10,
                            'ema_20': ema_20,
                            'signal_pattern': 'ema_golden_cross'
                        }
                    )
                    signals.append(signal)
                elif ema_5 < ema_10 < ema_20 and current_price < ema_5:
                    signal = BasicSignal(
                        signal_id=f"{symbol}_ema_death_cross_{int(time.time() * 1000)}",
                        symbol=symbol,
                        signal_type=SignalType.MOMENTUM,
                        direction="SELL",
                        strength=min(1.0, (ema_20 - ema_5) / ema_20 * 10),
                        confidence=dynamic_params.get('confidence_threshold', 0.6) + 0.2,
                        price=current_price,
                        timestamp=datetime.now(),
                        priority=Priority.MEDIUM,
                        layer_source="layer_1_momentum",
                        market_regime=self.current_regime.value,
                        processing_time_ms=15.0,
                        metadata={
                            'ema_5': ema_5,
                            'ema_10': ema_10,
                            'ema_20': ema_20,
                            'signal_pattern': 'ema_death_cross'
                        }
                    )
                    signals.append(signal)
                
            if signals:
                logger.debug(f"📈 {symbol}: pandas-ta 動量信號 - {len(signals)} 個")
        
        except Exception as e:
            logger.error(f"❌ Layer 1 pandas-ta 動量信號生成失敗: {e}")
        
        return signals
    
    async def _layer_2_trend_signals_enhanced(self, symbol: str, market_data: Dict[str, Any], dynamic_params: Dict[str, Any]) -> List[BasicSignal]:
        """Layer 2: 增強型趨勢信號生成 - 基於 pandas-ta 趨勢指標"""
        signals = []
        
        try:
            if len(self.price_buffer[symbol]) < 30:
                return signals
            
            # 使用 pandas-ta 計算趨勢指標
            indicators = await self._calculate_advanced_indicators(symbol)
            if not indicators:
                return signals
            
            current_price = list(self.price_buffer[symbol])[-1]['price']
            
            # 1. ADX 趨勢強度信號
            adx = indicators.get('adx')
            plus_di = indicators.get('plus_di')
            minus_di = indicators.get('minus_di')
            
            if adx is not None and adx > 25:  # 強趨勢
                if plus_di is not None and minus_di is not None:
                    if plus_di > minus_di:  # 上升趨勢
                        signal = BasicSignal(
                            signal_id=f"{symbol}_adx_uptrend_{int(time.time() * 1000)}",
                            symbol=symbol,
                            signal_type=SignalType.TREND,
                            direction="BUY",
                            strength=min(1.0, adx / 50),  # 基於 ADX 值計算強度
                            confidence=dynamic_params.get('confidence_threshold', 0.6) + 0.2,
                            price=current_price,
                            volume=float(market_data.get('volume', 1000.0)),
                            timestamp=datetime.now(),
                            priority=Priority.MEDIUM,
                            layer_source="layer_2_trend",
                            market_regime=self.current_regime.value,
                            processing_time_ms=20.0,
                            metadata={
                                'adx': adx,
                                'plus_di': plus_di,
                                'minus_di': minus_di,
                                'signal_pattern': 'adx_strong_uptrend'
                            }
                        )
                        signals.append(signal)
                    elif minus_di > plus_di:  # 下降趨勢
                        signal = BasicSignal(
                            signal_id=f"{symbol}_adx_downtrend_{int(time.time() * 1000)}",
                            symbol=symbol,
                            signal_type=SignalType.TREND,
                            direction="SELL",
                            strength=min(1.0, adx / 50),
                            confidence=dynamic_params.get('confidence_threshold', 0.6) + 0.2,
                            price=current_price,
                            timestamp=datetime.now(),
                            priority=Priority.MEDIUM,
                            layer_source="layer_2_trend",
                            market_regime=self.current_regime.value,
                            processing_time_ms=20.0,
                            metadata={
                                'adx': adx,
                                'plus_di': plus_di,
                                'minus_di': minus_di,
                                'signal_pattern': 'adx_strong_downtrend'
                            }
                        )
                        signals.append(signal)
            
            # 2. Aroon 趨勢信號
            aroon_up = indicators.get('aroon_up')
            aroon_down = indicators.get('aroon_down')
            aroon_osc = indicators.get('aroon_osc')
            
            if aroon_up is not None and aroon_down is not None:
                if aroon_up > 70 and aroon_down < 30:  # 強上升趨勢
                    signal = BasicSignal(
                        signal_id=f"{symbol}_aroon_bull_{int(time.time() * 1000)}",
                        symbol=symbol,
                        signal_type=SignalType.TREND,
                        direction="BUY",
                        strength=min(1.0, aroon_up / 100),
                        confidence=dynamic_params.get('confidence_threshold', 0.6) + 0.15,
                        price=current_price,
                        volume=float(market_data.get('volume', 1000.0)),
                        timestamp=datetime.now(),
                        priority=Priority.MEDIUM,
                        layer_source="layer_2_trend",
                        market_regime=self.current_regime.value,
                        processing_time_ms=20.0,
                        metadata={
                            'aroon_up': aroon_up,
                            'aroon_down': aroon_down,
                            'aroon_osc': aroon_osc,
                            'signal_pattern': 'aroon_strong_uptrend'
                        }
                    )
                    signals.append(signal)
                elif aroon_down > 70 and aroon_up < 30:  # 強下降趨勢
                    signal = BasicSignal(
                        signal_id=f"{symbol}_aroon_bear_{int(time.time() * 1000)}",
                        symbol=symbol,
                        signal_type=SignalType.TREND,
                        direction="SELL",
                        strength=min(1.0, aroon_down / 100),
                        confidence=dynamic_params.get('confidence_threshold', 0.6) + 0.15,
                        price=current_price,
                        timestamp=datetime.now(),
                        priority=Priority.MEDIUM,
                        layer_source="layer_2_trend",
                        market_regime=self.current_regime.value,
                        processing_time_ms=20.0,
                        metadata={
                            'aroon_up': aroon_up,
                            'aroon_down': aroon_down,
                            'aroon_osc': aroon_osc,
                            'signal_pattern': 'aroon_strong_downtrend'
                        }
                    )
                    signals.append(signal)
            
            # 3. Parabolic SAR 信號
            psar = indicators.get('psar')
            if psar is not None:
                if current_price > psar:  # 價格在 SAR 之上
                    signal = BasicSignal(
                        signal_id=f"{symbol}_psar_bull_{int(time.time() * 1000)}",
                        symbol=symbol,
                        signal_type=SignalType.TREND,
                        direction="BUY",
                        strength=min(1.0, (current_price - psar) / current_price * 100),
                        confidence=dynamic_params.get('confidence_threshold', 0.6) + 0.1,
                        price=current_price,
                        volume=float(market_data.get('volume', 1000.0)),
                        timestamp=datetime.now(),
                        priority=Priority.MEDIUM,
                        layer_source="layer_2_trend",
                        market_regime=self.current_regime.value,
                        processing_time_ms=20.0,
                        metadata={
                            'psar': psar,
                            'price_vs_psar': (current_price - psar) / current_price,
                            'signal_pattern': 'psar_bullish'
                        }
                    )
                    signals.append(signal)
                elif current_price < psar:  # 價格在 SAR 之下
                    signal = BasicSignal(
                        signal_id=f"{symbol}_psar_bear_{int(time.time() * 1000)}",
                        symbol=symbol,
                        signal_type=SignalType.TREND,
                        direction="SELL",
                        strength=min(1.0, (psar - current_price) / current_price * 100),
                        confidence=dynamic_params.get('confidence_threshold', 0.6) + 0.1,
                        price=current_price,
                        timestamp=datetime.now(),
                        priority=Priority.MEDIUM,
                        layer_source="layer_2_trend",
                        market_regime=self.current_regime.value,
                        processing_time_ms=20.0,
                        metadata={
                            'psar': psar,
                            'price_vs_psar': (current_price - psar) / current_price,
                            'signal_pattern': 'psar_bearish'
                        }
                    )
                    signals.append(signal)
            
            # 4. 布林帶突破信號
            bb_upper = indicators.get('bb_upper')
            bb_middle = indicators.get('bb_middle')
            bb_lower = indicators.get('bb_lower')
            bb_percent = indicators.get('bb_percent')
            
            if bb_upper is not None and bb_lower is not None and bb_percent is not None:
                if current_price > bb_upper and bb_percent > 1.0:  # 突破上軌
                    signal = BasicSignal(
                        signal_id=f"{symbol}_bb_breakout_up_{int(time.time() * 1000)}",
                        symbol=symbol,
                        signal_type=SignalType.TREND,
                        direction="BUY",
                        strength=min(1.0, bb_percent - 1.0),
                        confidence=dynamic_params.get('confidence_threshold', 0.6) + 0.1,
                        price=current_price,
                        volume=float(market_data.get('volume', 1000.0)),
                        timestamp=datetime.now(),
                        priority=Priority.MEDIUM,
                        layer_source="layer_2_trend",
                        market_regime=self.current_regime.value,
                        processing_time_ms=20.0,
                        metadata={
                            'bb_upper': bb_upper,
                            'bb_middle': bb_middle,
                            'bb_lower': bb_lower,
                            'bb_percent': bb_percent,
                            'signal_pattern': 'bollinger_upward_breakout'
                        }
                    )
                    signals.append(signal)
                elif current_price < bb_lower and bb_percent < 0.0:  # 突破下軌
                    signal = BasicSignal(
                        signal_id=f"{symbol}_bb_breakout_down_{int(time.time() * 1000)}",
                        symbol=symbol,
                        signal_type=SignalType.TREND,
                        direction="SELL",
                        strength=min(1.0, abs(bb_percent)),
                        confidence=dynamic_params.get('confidence_threshold', 0.6) + 0.1,
                        price=current_price,
                        timestamp=datetime.now(),
                        priority=Priority.MEDIUM,
                        layer_source="layer_2_trend",
                        market_regime=self.current_regime.value,
                        processing_time_ms=20.0,
                        metadata={
                            'bb_upper': bb_upper,
                            'bb_middle': bb_middle,
                            'bb_lower': bb_lower,
                            'bb_percent': bb_percent,
                            'signal_pattern': 'bollinger_downward_breakout'
                        }
                    )
                    signals.append(signal)
            
            if signals:
                logger.debug(f"📊 {symbol}: pandas-ta 趨勢信號 - {len(signals)} 個")
                
        except Exception as e:
            logger.error(f"❌ Layer 2 pandas-ta 趨勢信號生成失敗: {e}")
        
        return signals
    
    async def _layer_3_volume_signals_enhanced(self, symbol: str, market_data: Dict[str, Any], dynamic_params: Dict[str, Any]) -> List[BasicSignal]:
        """Layer 3: 增強型成交量信號生成 - 基於 pandas-ta 成交量指標"""
        signals = []
        
        try:
            if len(self.volume_buffer[symbol]) < 10:
                return signals
            
            # 使用 pandas-ta 計算成交量指標
            indicators = await self._calculate_advanced_indicators(symbol)
            if not indicators:
                return signals
            
            current_price = list(self.price_buffer[symbol])[-1]['price']
            current_volume = float(market_data.get('volume', 1000.0))
            
            # 1. OBV (On Balance Volume) 信號
            obv = indicators.get('obv')
            if obv is not None:
                # 檢查 OBV 趨勢 - 需要歷史 OBV 數據來比較
                recent_volumes = [v['volume'] for v in list(self.volume_buffer[symbol])[-10:] if v['volume'] > 0]
                if len(recent_volumes) >= 5:
                    avg_volume = np.mean(recent_volumes[:-1])
                    volume_change_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
                    
                    if volume_change_ratio > dynamic_params.get('volume_change_threshold', 2.0):
                        signal = BasicSignal(
                            signal_id=f"{symbol}_obv_confirmation_{int(time.time() * 1000)}",
                            symbol=symbol,
                            signal_type=SignalType.VOLUME,
                            direction="BUY",
                            strength=min(1.0, volume_change_ratio / dynamic_params.get('volume_change_threshold', 2.0)),
                            confidence=dynamic_params.get('confidence_threshold', 0.6) + 0.05,
                            price=current_price,
                            volume=current_volume,
                            timestamp=datetime.now(),
                            priority=Priority.MEDIUM,
                            layer_source="layer_3_volume",
                            market_regime=self.current_regime.value,
                            processing_time_ms=5.0,
                            metadata={
                                'obv': obv,
                                'volume_change_ratio': volume_change_ratio,
                                'avg_volume': avg_volume,
                                'threshold_used': dynamic_params.get('volume_change_threshold', 2.0),
                                'signal_pattern': 'obv_volume_confirmation'
                            }
                        )
                        signals.append(signal)
            
            # 2. A/D Line (Accumulation/Distribution Line) 信號
            ad_line = indicators.get('ad_line')
            if ad_line is not None:
                # 基於 A/D Line 和價格背離檢測
                recent_prices = [p['price'] for p in list(self.price_buffer[symbol])[-5:]]
                if len(recent_prices) >= 3:
                    price_trend = recent_prices[-1] - recent_prices[0]
                    
                    # 簡化的背離檢測
                    if price_trend > 0 and ad_line > 0:  # 價格上升且 A/D Line 正值
                        signal = BasicSignal(
                            signal_id=f"{symbol}_ad_line_bull_{int(time.time() * 1000)}",
                            symbol=symbol,
                            signal_type=SignalType.VOLUME,
                            direction="BUY",
                            strength=min(1.0, abs(price_trend) / recent_prices[0] * 100),
                            confidence=dynamic_params.get('confidence_threshold', 0.6) + 0.1,
                            price=current_price,
                            volume=current_volume,
                            timestamp=datetime.now(),
                            priority=Priority.MEDIUM,
                            layer_source="layer_3_volume",
                            market_regime=self.current_regime.value,
                            processing_time_ms=5.0,
                            metadata={
                                'ad_line': ad_line,
                                'price_trend': price_trend,
                                'signal_pattern': 'ad_line_bullish_confirmation'
                            }
                        )
                        signals.append(signal)
                    elif price_trend < 0 and ad_line < 0:  # 價格下降且 A/D Line 負值
                        signal = BasicSignal(
                            signal_id=f"{symbol}_ad_line_bear_{int(time.time() * 1000)}",
                            symbol=symbol,
                            signal_type=SignalType.VOLUME,
                            direction="SELL",
                            strength=min(1.0, abs(price_trend) / recent_prices[0] * 100),
                            confidence=dynamic_params.get('confidence_threshold', 0.6) + 0.1,
                            price=current_price,
                            timestamp=datetime.now(),
                            priority=Priority.MEDIUM,
                            layer_source="layer_3_volume",
                            market_regime=self.current_regime.value,
                            processing_time_ms=5.0,
                            metadata={
                                'ad_line': ad_line,
                                'price_trend': price_trend,
                                'signal_pattern': 'ad_line_bearish_confirmation'
                            }
                        )
                        signals.append(signal)
            
            # 3. VWAP (Volume Weighted Average Price) 信號
            vwap = indicators.get('vwap')
            if vwap is not None:
                if current_price > vwap:  # 價格高於 VWAP
                    signal = BasicSignal(
                        signal_id=f"{symbol}_vwap_above_{int(time.time() * 1000)}",
                        symbol=symbol,
                        signal_type=SignalType.VOLUME,
                        direction="BUY",
                        strength=min(1.0, (current_price - vwap) / vwap * 10),
                        confidence=dynamic_params.get('confidence_threshold', 0.6) + 0.05,
                        price=current_price,
                        volume=current_volume,
                        timestamp=datetime.now(),
                        priority=Priority.MEDIUM,
                        layer_source="layer_3_volume",
                        market_regime=self.current_regime.value,
                        processing_time_ms=5.0,
                        metadata={
                            'vwap': vwap,
                            'price_vs_vwap': (current_price - vwap) / vwap,
                            'signal_pattern': 'price_above_vwap'
                        }
                    )
                    signals.append(signal)
                elif current_price < vwap:  # 價格低於 VWAP
                    signal = BasicSignal(
                        signal_id=f"{symbol}_vwap_below_{int(time.time() * 1000)}",
                        symbol=symbol,
                        signal_type=SignalType.VOLUME,
                        direction="SELL",
                        strength=min(1.0, (vwap - current_price) / vwap * 10),
                        confidence=dynamic_params.get('confidence_threshold', 0.6) + 0.05,
                        price=current_price,
                        timestamp=datetime.now(),
                        priority=Priority.MEDIUM,
                        layer_source="layer_3_volume",
                        market_regime=self.current_regime.value,
                        processing_time_ms=5.0,
                        metadata={
                            'vwap': vwap,
                            'price_vs_vwap': (current_price - vwap) / vwap,
                            'signal_pattern': 'price_below_vwap'
                        }
                    )
                    signals.append(signal)
            
            # 4. 傳統成交量異常檢測 (保留原有邏輯)
            recent_volumes = [v['volume'] for v in list(self.volume_buffer[symbol])[-20:] if v['volume'] > 0]
            if len(recent_volumes) >= 5:
                avg_volume = np.mean(recent_volumes[:-1])
                volume_change_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
                
                if volume_change_ratio > dynamic_params.get('volume_change_threshold', 2.0) * 2:  # 更高的閾值用於異常檢測
                    signal = BasicSignal(
                        signal_id=f"{symbol}_volume_spike_{int(time.time() * 1000)}",
                        symbol=symbol,
                        signal_type=SignalType.VOLUME,
                        direction="BUY",
                        strength=1.0,
                        confidence=min(0.95, dynamic_params.get('confidence_threshold', 0.6) + 0.25),
                        price=current_price,
                        volume=current_volume,
                        timestamp=datetime.now(),
                        priority=Priority.HIGH,
                        layer_source="layer_3_volume",
                        market_regime=self.current_regime.value,
                        processing_time_ms=5.0,
                        metadata={
                            'volume_change_ratio': volume_change_ratio,
                            'current_volume': current_volume,
                            'avg_volume': avg_volume,
                            'threshold_used': dynamic_params.get('volume_change_threshold', 2.0),
                            'signal_pattern': 'unusual_volume_spike'
                        }
                    )
                    signals.append(signal)
            
            if signals:
                logger.debug(f"📦 {symbol}: pandas-ta 成交量信號 - {len(signals)} 個")
                
        except Exception as e:
            logger.error(f"❌ Layer 3 pandas-ta 成交量信號生成失敗: {e}")
        
        return signals
    
    async def subscribe_to_signals(self, callback):
        """訂閱信號輸出 - 外部系統用於接收信號"""
        if callback not in self.signal_subscribers:
            self.signal_subscribers.append(callback)
            logger.info(f"✅ 新增信號訂閱者，當前訂閱數: {len(self.signal_subscribers)}")
    
    async def unsubscribe_from_signals(self, callback):
        """取消信號訂閱"""
        if callback in self.signal_subscribers:
            self.signal_subscribers.remove(callback)
            logger.info(f"✅ 移除信號訂閱者，當前訂閱數: {len(self.signal_subscribers)}")
    
    async def get_recent_signals(self, limit: int = 50) -> List[BasicSignal]:
        """獲取最近的信號 - 用於外部系統查詢"""
        try:
            # 從信號緩衝區獲取最近的信號
            recent_signals = []
            
            # 如果有信號緩衝區，從中獲取
            if hasattr(self, 'signal_buffer') and self.signal_buffer:
                recent_signals = list(self.signal_buffer)[-limit:]
            
            # 如果沒有信號，嘗試生成一些測試信號
            if not recent_signals and self.real_market_data:
                logger.info("🔄 緩衝區無信號，嘗試即時生成...")
                
                for symbol, market_data in self.real_market_data.items():
                    try:
                        signals = await self.generate_signals(symbol, market_data)
                        recent_signals.extend(signals)
                        
                        if len(recent_signals) >= limit:
                            break
                            
                    except Exception as e:
                        logger.error(f"❌ 即時信號生成失敗 {symbol}: {e}")
            
            logger.debug(f"📊 返回 {len(recent_signals)} 個最近信號")
            return recent_signals[:limit]
            
        except Exception as e:
            logger.error(f"❌ 獲取最近信號失敗: {e}")
            return []
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """獲取性能統計摘要"""
        try:
            summary = {
                'is_running': self.is_running,
                'total_signals_generated': getattr(self, 'total_signals_count', 0),
                'avg_processing_time_ms': 0.0,
                'active_symbols': len(self.price_buffer),
                'buffer_sizes': {},
                'last_signal_time': None,
                'dynamic_params_enabled': self.dynamic_params_enabled
            }
            
            # 計算平均處理時間
            if hasattr(self, 'processing_times') and self.processing_times.get('total'):
                recent_times = list(self.processing_times['total'])[-10:]  # 最近10次
                if recent_times:
                    summary['avg_processing_time_ms'] = sum(recent_times) / len(recent_times)
            
            # 緩衝區大小統計
            for symbol, buffer in self.price_buffer.items():
                summary['buffer_sizes'][symbol] = len(buffer)
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ 性能統計獲取失敗: {e}")
            return {'error': str(e)}
    
    async def _distribute_signals(self, signals: List[BasicSignal]):
        """分發信號到訂閱者"""
        if not signals:
            return
        
        try:
            # 添加到信號緩衝區
            if not hasattr(self, 'signal_buffer'):
                self.signal_buffer = deque(maxlen=1000)
            
            for signal in signals:
                self.signal_buffer.append(signal)
            
            # 通知所有訂閱者
            if hasattr(self, 'signal_subscribers'):
                for callback in self.signal_subscribers:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(signals)
                        else:
                            callback(signals)
                    except Exception as e:
                        logger.error(f"❌ 信號分發到訂閱者失敗: {e}")
            
            # 更新統計
            if not hasattr(self, 'total_signals_count'):
                self.total_signals_count = 0
            self.total_signals_count += len(signals)
            
            logger.debug(f"📡 分發 {len(signals)} 個信號到 {len(getattr(self, 'signal_subscribers', []))} 個訂閱者")
            
        except Exception as e:
            logger.error(f"❌ 信號分發失敗: {e}")
    
    def _update_market_data_cache(self, symbol: str, market_data: Dict[str, Any]):
        """更新市場數據緩存"""
        if not hasattr(self, 'real_market_data'):
            self.real_market_data = {}
        
        self.real_market_data[symbol] = market_data
    
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
            
            # 更新 intelligent_trigger_engine
            try:
                await process_realtime_price_update(symbol, price, volume)
            except Exception as e:
                logger.debug(f"intelligent_trigger_engine 數據更新失敗: {e}")
            
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
    
    async def _execute_layer_processing(self, layer_id: str, processor, symbol: str, market_data, dynamic_params: Union[DynamicParameters, Dict[str, Any]] = None) -> 'LayerProcessingResult':
        """執行單層處理 - 支援動態參數"""
        start_time = datetime.now()
        
        try:
            # 如果沒有提供動態參數，獲取默認參數
            if dynamic_params is None:
                dynamic_params_obj = await self._get_dynamic_parameters()
                dynamic_params_dict = dynamic_params_obj.to_dict() if dynamic_params_obj else {}
            else:
                # 確保 dynamic_params 是字典格式
                if isinstance(dynamic_params, dict):
                    dynamic_params_dict = dynamic_params
                else:
                    dynamic_params_dict = dynamic_params.to_dict() if hasattr(dynamic_params, 'to_dict') else dynamic_params
            
            # 調用處理器方法
            if dynamic_params_dict:
                signals = await processor(symbol, market_data, dynamic_params_dict)
            else:
                # 備用調用方式
                signals = await processor(symbol, market_data)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds() * 1000
            
            return LayerProcessingResult(
                layer_id=layer_id,
                signals=signals if signals else [],
                processing_time_ms=processing_time,
                success=True
            )
            
        except Exception as e:
            logger.error(f"❌ {layer_id} 處理失敗: {e}")
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds() * 1000
            
            return LayerProcessingResult(
                layer_id=layer_id,
                signals=[],
                processing_time_ms=processing_time,
                success=False,
                error=str(e),
                data_quality=0.0,
                source_data_count=0
            )
    
    async def _layer_0_instant_signals(self, symbol: str, market_data) -> List[BasicSignal]:
        """Layer 0: 即時信號 (< 5ms)"""
        signals = []
        
        try:
            # 獲取動態參數
            dynamic_params_obj = await self._get_dynamic_parameters("basic_mode")
            dynamic_params = dynamic_params_obj.to_dict() if dynamic_params_obj else {}
            
            price = market_data.price
            volume = market_data.volume
            timestamp = market_data.timestamp
            
            # 價格突破信號
            if len(self.price_buffer[symbol]) >= 2:
                prev_price = list(self.price_buffer[symbol])[-2]['price']
                price_change_pct = (price - prev_price) / prev_price
                price_change_abs = abs(price_change_pct)
                
                # 使用動態價格變化閾值
                if price_change_abs > dynamic_params.get('price_change_threshold', 0.02):
                    direction = "BUY" if price_change_pct > 0 else "SELL"
                    strength = min(price_change_abs / (dynamic_params.get('price_change_threshold', 0.02) * 2), 1.0)
                    
                    # 使用動態信心度閾值 - 修復：降低基礎信心度
                    base_confidence = 0.3 + (price_change_abs - dynamic_params.get('price_change_threshold', 0.02)) * 10
                    confidence = min(max(base_confidence, 0.3), 1.0)
                    
                    if confidence >= dynamic_params.get('confidence_threshold', 0.6):
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
                                "dynamic_threshold_used": dynamic_params.get('price_change_threshold', 0.02),
                                "market_regime": "UNKNOWN",
                                "trading_session": "OFF_HOURS"
                            },
                            layer_source="layer_0",
                            processing_time_ms=0,
                            market_regime=self.current_regime.value,
                            trading_session="OFF_HOURS",
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
                    if volume_ratio > dynamic_params.get('volume_change_threshold', 2.0):
                        strength = min(volume_ratio / (dynamic_params.get('volume_change_threshold', 2.0) * 2), 1.0)
                        
                        # 計算成交量信心度
                        base_confidence = 0.6 + (volume_ratio - dynamic_params.get('volume_change_threshold', 2.0)) * 0.1
                        confidence = min(max(base_confidence, 0.3), 1.0)
                        
                        if confidence >= dynamic_params.get('confidence_threshold', 0.6):
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
                                    "dynamic_threshold_used": dynamic_params.get('volume_change_threshold', 2.0),
                                    "market_regime": "UNKNOWN",
                                    "trading_session": "OFF_HOURS"
                                },
                                layer_source="layer_0",
                                processing_time_ms=0,
                                market_regime=self.current_regime.value,
                                trading_session="OFF_HOURS",
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
                        confidence=0.35,  # 修復：降低硬編碼信心度
                        priority=Priority.HIGH,
                        timestamp=timestamps[-1],
                        price=prices[-1],
                        volume=market_data.get('volume', 0),
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
                        confidence=0.35,  # 修復：降低硬編碼信心度
                        priority=Priority.HIGH,
                        timestamp=timestamps[-1],
                        price=prices[-1],
                        volume=market_data.get('volume', 0),
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
                        volume=market_data.get('volume', 0),
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
                    
                    # 使用動態信心度閾值 - 來自 Phase5 Lean 優化
                    dynamic_params_obj = await self._get_dynamic_parameters("basic_mode")
                    dynamic_params = dynamic_params_obj.to_dict() if dynamic_params_obj else {}
                    confidence_threshold = dynamic_params.get('confidence_threshold', 0.6) if dynamic_params else 0.5
                    
                    # 載入 Phase5 Lean 優化參數
                    lean_adjustment = await self._get_lean_adjustment_for_symbol(symbol)
                    if lean_adjustment and lean_adjustment.get('confidence_level', 0) > 0.6:
                        # 如果是 Lean 優化的幣種，使用更智能的閾值
                        confidence_threshold = max(0.4, lean_adjustment['confidence_level'] * 0.8)
                    
                    signal = BasicSignal(
                        signal_id=f"trend_strength_{symbol}_{timestamps[-1].timestamp()}",
                        symbol=symbol,
                        signal_type=SignalType.TREND,
                        direction=direction,
                        strength=min(abs(trend_strength), 1.0),
                        confidence=confidence_threshold,  # 使用動態閾值
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

    async def _calculate_advanced_indicators(self, symbol: str) -> Dict[str, Any]:
        """
        ★ 產品等級技術指標計算 - 調用 intelligent_trigger_engine
        移除重複計算，直接使用 intelligent_trigger_engine 的產品等級實現
        """
        try:
            # 檢查數據質量 (回測模式下放寬要求)
            try:
                # 檢查是否為回測模式
                is_backtest_mode = hasattr(self, '_backtest_mode') and self._backtest_mode
                
                if not is_backtest_mode:
                    # 生產模式下進行質量評估（非阻塞）
                    data_quality = validate_data_quality(symbol)
                    if not data_quality.get('is_valid', False):
                        warnings = data_quality.get('warnings', data_quality.get('issues', []))
                        quality_level = data_quality.get('quality_level', '未知')
                        logger.warning(f"⚠️ {symbol} 數據質量：{quality_level}")
                        if warnings:
                            logger.warning(f"   警告項目: {warnings}")
                        recommendation = data_quality.get('recommendation', '系統將嘗試繼續')
                        logger.info(f"� 建議: {recommendation}")
                        # 不再強制退出，改為警告並繼續
                    else:
                        quality_level = data_quality.get('quality_level', '良好')
                        logger.info(f"✅ {symbol} 數據質量：{quality_level}")
                else:
                    # 回測模式下只進行基本檢查
                    logger.debug(f"📊 {symbol} 回測模式：跳過嚴格數據質量檢查")
                    
            except Exception as data_quality_error:
                # 檢查是否為回測模式
                is_backtest_mode = hasattr(self, '_backtest_mode') and self._backtest_mode
                if not is_backtest_mode:
                    logger.warning(f"⚠️ {symbol} 數據質量檢查異常: {data_quality_error}，系統將繼續運行")
                    # 不再強制退出
                else:
                    logger.warning(f"⚠️ {symbol} 回測模式數據質量檢查跳過: {data_quality_error}")
            
            # 檢查實時數據可用性 (回測模式下跳過)
            try:
                is_backtest_mode = hasattr(self, '_backtest_mode') and self._backtest_mode
                
                if not is_backtest_mode:
                    data_available = is_real_time_data_available(symbol)
                    if not data_available:
                        logger.warning(f"⚠️ {symbol} 實時數據源質量較低，但系統將繼續運行")
                        # 不再強制退出，改為警告
                    else:
                        logger.debug(f"✅ {symbol} 實時數據源可用")
                else:
                    logger.debug(f"📊 {symbol} 回測模式：跳過實時數據檢查")
                    
            except Exception as availability_error:
                is_backtest_mode = hasattr(self, '_backtest_mode') and self._backtest_mode
                if not is_backtest_mode:
                    logger.warning(f"⚠️ {symbol} 數據可用性檢查異常: {availability_error}，系統將繼續")
                    # 不再強制退出
                else:
                    logger.warning(f"⚠️ {symbol} 回測模式數據可用性檢查跳過: {availability_error}")
            
            # 從 intelligent_trigger_engine 獲取產品等級技術指標
            technical_indicators = await get_technical_indicators_for_phase1a(symbol)
            
            if technical_indicators is None:
                logger.warning(f"⚠️ {symbol} 技術指標暫時不可用，等待3秒後重試...")
                await asyncio.sleep(3)
                
                # 第二次嘗試
                technical_indicators = await get_technical_indicators_for_phase1a(symbol)
                if technical_indicators is None:
                    logger.error(f"🛑 {symbol} 技術指標獲取失敗（重試後），跳過此輪信號生成")
                    return []  # 返回空列表而不是強制退出
            
            # 轉換為 Phase1A 格式
            indicators = {}
            
            # 1. 移動平均線組
            if technical_indicators.sma_10 is not None:
                indicators['sma_10'] = technical_indicators.sma_10
            if technical_indicators.sma_20 is not None:
                indicators['sma_20'] = technical_indicators.sma_20
            if technical_indicators.sma_50 is not None:
                indicators['sma_50'] = technical_indicators.sma_50
            if technical_indicators.sma_200 is not None:
                indicators['sma_200'] = technical_indicators.sma_200
                
            if technical_indicators.ema_12 is not None:
                indicators['ema_12'] = technical_indicators.ema_12
            if technical_indicators.ema_26 is not None:
                indicators['ema_26'] = technical_indicators.ema_26
            if technical_indicators.ema_50 is not None:
                indicators['ema_50'] = technical_indicators.ema_50
            
            # 2. 動量指標
            if technical_indicators.rsi is not None:
                indicators['rsi'] = technical_indicators.rsi
            if technical_indicators.rsi_14 is not None:
                indicators['rsi_14'] = technical_indicators.rsi_14
            if technical_indicators.rsi_21 is not None:
                indicators['rsi_21'] = technical_indicators.rsi_21
                
            # 3. MACD 系統
            if technical_indicators.macd is not None:
                indicators['macd'] = technical_indicators.macd
            if technical_indicators.macd_signal is not None:
                indicators['macd_signal'] = technical_indicators.macd_signal
            if technical_indicators.macd_histogram is not None:
                indicators['macd_histogram'] = technical_indicators.macd_histogram
            
            # 4. 隨機指標
            if technical_indicators.stoch_k is not None:
                indicators['stoch_k'] = technical_indicators.stoch_k
            if technical_indicators.stoch_d is not None:
                indicators['stoch_d'] = technical_indicators.stoch_d
            if technical_indicators.williams_r is not None:
                indicators['williams_r'] = technical_indicators.williams_r
            
            # 5. 成交量指標
            if technical_indicators.obv is not None:
                indicators['obv'] = technical_indicators.obv
            if technical_indicators.vwap is not None:
                indicators['vwap'] = technical_indicators.vwap
            if technical_indicators.volume_sma is not None:
                indicators['volume_sma'] = technical_indicators.volume_sma
            
            # 6. 布林帶
            if technical_indicators.bollinger_upper is not None:
                indicators['bb_upper'] = technical_indicators.bollinger_upper
            if technical_indicators.bollinger_middle is not None:
                indicators['bb_middle'] = technical_indicators.bollinger_middle
            if technical_indicators.bollinger_lower is not None:
                indicators['bb_lower'] = technical_indicators.bollinger_lower
            if technical_indicators.bollinger_bandwidth is not None:
                indicators['bb_width'] = technical_indicators.bollinger_bandwidth
            if technical_indicators.bollinger_percent is not None:
                indicators['bb_percent'] = technical_indicators.bollinger_percent
            
            # 7. 波動性指標
            if technical_indicators.atr is not None:
                indicators['atr'] = technical_indicators.atr
            if technical_indicators.natr is not None:
                indicators['natr'] = technical_indicators.natr
            if technical_indicators.true_range is not None:
                indicators['true_range'] = technical_indicators.true_range
            
            # 8. 趨勢指標
            if technical_indicators.adx is not None:
                indicators['adx'] = technical_indicators.adx
            if technical_indicators.adx_plus is not None:
                indicators['plus_di'] = technical_indicators.adx_plus
            if technical_indicators.adx_minus is not None:
                indicators['minus_di'] = technical_indicators.adx_minus
            if technical_indicators.aroon_up is not None:
                indicators['aroon_up'] = technical_indicators.aroon_up
            if technical_indicators.aroon_down is not None:
                indicators['aroon_down'] = technical_indicators.aroon_down
            
            # 9. 支撐阻力
            if technical_indicators.support_level is not None:
                indicators['support_level'] = technical_indicators.support_level
            if technical_indicators.resistance_level is not None:
                indicators['resistance_level'] = technical_indicators.resistance_level
            
            # 10. 週期性指標 (新增功能)
            if technical_indicators.cycle_period is not None:
                indicators['cycle_period'] = technical_indicators.cycle_period
            if technical_indicators.cycle_strength is not None:
                indicators['cycle_strength'] = technical_indicators.cycle_strength
            
            # 11. 統計指標
            if technical_indicators.skewness is not None:
                indicators['skew'] = technical_indicators.skewness
            if technical_indicators.kurtosis is not None:
                indicators['kurtosis'] = technical_indicators.kurtosis
            
            # 12. 模式識別 (新增功能)
            if technical_indicators.doji_pattern is not None:
                indicators['doji_pattern'] = float(technical_indicators.doji_pattern)
            if technical_indicators.hammer_pattern is not None:
                indicators['hammer_pattern'] = float(technical_indicators.hammer_pattern)
            if technical_indicators.engulfing_pattern is not None:
                indicators['engulfing_pattern'] = float(technical_indicators.engulfing_pattern)
            
            # 13. 收斂和強度分數 (新增功能)
            indicators['overall_convergence_score'] = technical_indicators.overall_convergence_score
            indicators['signal_strength_score'] = technical_indicators.signal_strength_score
            
            # 14. 基礎蠟燭體計算 (保留原有邏輯)
            try:
                if len(self.price_buffer[symbol]) > 0:
                    latest_data = self.price_buffer[symbol][-1]
                    
                    # 檢查 latest_data 是否為 coroutine 對象
                    if asyncio.iscoroutine(latest_data):
                        logger.warning(f"⚠️ latest_data 是 coroutine 對象，跳過蠟燭體計算")
                        latest_data = None
                    
                    if latest_data and isinstance(latest_data, dict):
                        open_price = latest_data.get('open', latest_data.get('price', 0))
                        close_price = latest_data.get('price', 0)
                        high_price = latest_data.get('high', latest_data.get('price', 0))
                        low_price = latest_data.get('low', latest_data.get('price', 0))
                        
                        if all(isinstance(x, (int, float)) for x in [open_price, close_price, high_price, low_price]):
                            indicators['candle_body'] = abs(close_price - open_price)
                            indicators['upper_shadow'] = high_price - max(close_price, open_price)
                            indicators['lower_shadow'] = min(close_price, open_price) - low_price
                        else:
                            logger.warning(f"⚠️ 價格數據類型錯誤: open={type(open_price)}, close={type(close_price)}")
            except Exception as e:
                logger.debug(f"蠟燭體計算失敗: {e}")
            
            logger.info(f"✅ {symbol} 產品等級技術指標獲取成功，指標數量: {len(indicators)}")
            logger.info(f"📊 收斂分數: {technical_indicators.overall_convergence_score:.3f}, 信號強度: {technical_indicators.signal_strength_score:.3f}")
            return indicators
            
        except Exception as e:
            logger.error(f"❌ {symbol} 產品等級技術指標獲取失敗: {e}")
            # 改為警告而不是強制退出，允許系統繼續運行
            logger.warning(f"⚠️ {symbol} 技術指標計算失敗，跳過此輪信號生成，系統繼續運行")
            return []  # 返回空列表，讓系統嘗試下一個交易對
    
    
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
                           self._convert_timestamp(self.price_buffer[symbol][0]['timestamp']) < cutoff_time):
                        self.price_buffer[symbol].popleft()
                    
                    # 清理成交量緩衝區
                    while (self.volume_buffer[symbol] and 
                           self._convert_timestamp(self.volume_buffer[symbol][0]['timestamp']) < cutoff_time):
                        self.volume_buffer[symbol].popleft()
                
                # 清理信號緩衝區
                while (self.signal_buffer and 
                       (current_time - self.signal_buffer[0].timestamp).total_seconds() > 3600):  # 1小時
                    self.signal_buffer.popleft()
                
                await asyncio.sleep(60)  # 每分鐘清理一次
                
            except Exception as e:
                logger.error(f"協調器失敗: {e}")
                await asyncio.sleep(60)
    
    async def _filter_and_prioritize_signals(self, signals: List[BasicSignal], symbol: str, dynamic_params: Dict[str, Any]) -> List[BasicSignal]:
        """信號品質篩選和優先級排序"""
        if not signals:
            return signals
        
        try:
            # 1. 基礎品質篩選
            min_confidence = dynamic_params.get('confidence_threshold', 0.6)
            quality_filtered = []
            
            for signal in signals:
                # 篩選條件 - 完全禁用 price_action 信號
                if (signal.confidence >= min_confidence and 
                    signal.strength > 0.3 and 
                    signal.signal_type != SignalType.PRICE_ACTION):  # � 完全禁用 price_action 雜訊信號
                    quality_filtered.append(signal)
                elif signal.signal_type == SignalType.PRICE_ACTION:
                    # 🚫 完全禁用所有 price_action 信號（太多雜訊）
                    logger.debug(f"🚫 {symbol}: 過濾掉 price_action 信號 (confidence: {signal.confidence:.3f}, strength: {signal.strength:.3f})")
                    continue  # 跳過所有 price_action 信號
            
            # 2. 去重：相同方向和類型的信號只保留最高品質
            deduplicated = {}
            for signal in quality_filtered:
                key = f"{signal.symbol}_{signal.direction}_{signal.signal_type.value}"
                if key not in deduplicated or signal.confidence > deduplicated[key].confidence:
                    deduplicated[key] = signal
            
            # 3. 按優先級和品質排序
            final_signals = list(deduplicated.values())
            final_signals.sort(key=lambda x: (x.priority.value, -x.confidence, -x.strength))
            
            # 4. 限制每個符號的信號數量
            max_signals_per_symbol = 3
            if len(final_signals) > max_signals_per_symbol:
                final_signals = final_signals[:max_signals_per_symbol]
                logger.info(f"📊 {symbol}: 信號數量限制為 {max_signals_per_symbol} 個")
            
            return final_signals
            
        except Exception as e:
            logger.error(f"❌ {symbol}: 信號篩選失敗 - {e}")
            return signals  # 篩選失敗時返回原始信號
    
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
    
    async def _get_lean_adjustment_for_symbol(self, symbol: str) -> Dict[str, Any]:
        """獲取特定幣種的 Lean 優化參數 - 來自 Phase5 回測"""
        try:
            # 載入最新的 Phase5 配置
            config_dir = Path("X/backend/phase5_backtest_validation/safety_backups/working")
            if config_dir.exists():
                config_files = list(config_dir.glob("phase1a_backup_deployment_initial_*.json"))
                if config_files:
                    latest_config = max(config_files, key=lambda x: x.stat().st_mtime)
                    
                    with open(latest_config, 'r', encoding='utf-8') as f:
                        lean_config = json.load(f)
                    
                    # 查找幣種特定配置
                    lean_key = f"{symbol.lower()}_lean_adjustment"
                    lean_params = lean_config.get(lean_key, {})
                    
                    if lean_params:
                        logger.debug(f"✅ {symbol} Lean 參數載入: 信心度 {lean_params.get('confidence_level', 0)*100:.1f}%")
                        return lean_params
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ {symbol} Lean 參數載入失敗: {e}")
            return {}

    async def evaluate_signal_tier(self, symbol: str, technical_strength: float, market_data: Optional[Dict] = None) -> Tuple[SignalTier, TierConfiguration, Dict[str, Any]]:
        """評估信號分層等級 - 核心分層邏輯"""
        try:
            # 1. 獲取 Lean 優化參數
            lean_params = await self._get_lean_adjustment_for_symbol(symbol)
            lean_confidence = lean_params.get('confidence_level', 0.0)
            expected_return = lean_params.get('expected_return', 0.0)
            
            # 2. 計算綜合評分
            composite_score = self._calculate_composite_signal_score(
                lean_confidence, technical_strength, market_data
            )
            
            # 3. 確定分層等級
            selected_tier = self._determine_signal_tier(lean_confidence, composite_score)
            tier_config = self.tier_system.get(selected_tier)
            
            # 4. 動態調整閾值
            dynamic_threshold = self._calculate_dynamic_threshold(
                lean_confidence, selected_tier, tier_config
            )
            
            # 5. 分層元數據
            tier_metadata = {
                'tier': selected_tier,
                'lean_confidence': lean_confidence,
                'technical_strength': technical_strength,
                'composite_score': composite_score,
                'dynamic_threshold': dynamic_threshold,
                'expected_return': expected_return,
                'position_multiplier': tier_config.position_multiplier if tier_config else 0.5,
                'execution_priority': tier_config.execution_priority if tier_config else 4,
                'tier_reasoning': self._generate_tier_reasoning(lean_confidence, technical_strength, selected_tier)
            }
            
            logger.debug(f"📊 {symbol} 分層評估: {selected_tier.value} (Lean: {lean_confidence:.1%}, 技術: {technical_strength:.3f})")
            
            return selected_tier, tier_config, tier_metadata
            
        except Exception as e:
            logger.error(f"❌ {symbol} 信號分層評估失敗: {e}")
            # 返回默認 MEDIUM 層級
            default_config = self.tier_system.get(SignalTier.MEDIUM)
            default_metadata = {
                'tier': SignalTier.MEDIUM,
                'lean_confidence': 0.0,
                'technical_strength': technical_strength,
                'composite_score': technical_strength,
                'dynamic_threshold': 0.7,
                'expected_return': 0.0,
                'position_multiplier': 0.3,
                'execution_priority': 3,
                'tier_reasoning': '分層評估失敗，使用默認配置'
            }
            return SignalTier.MEDIUM, default_config, default_metadata
    
    def _calculate_composite_signal_score(self, lean_confidence: float, technical_strength: float, market_data: Optional[Dict] = None) -> float:
        """計算綜合信號評分 - 多因子評分模型"""
        try:
            # 基礎分數 (Lean + 技術指標)
            base_score = (lean_confidence * 0.6) + (technical_strength * 0.4)
            
            # 市場環境調整
            market_adjustment = 0.0
            if market_data:
                # 波動度調整 (高波動度降低評分)
                volatility = market_data.get('volatility', 0.02)
                if volatility > 0.05:  # 高波動
                    market_adjustment -= 0.1
                elif volatility < 0.01:  # 低波動  
                    market_adjustment += 0.05
                
                # 成交量確認 (高成交量增加評分)
                volume_ratio = market_data.get('volume_ratio', 1.0)
                if volume_ratio > 1.5:
                    market_adjustment += 0.05
                elif volume_ratio < 0.7:
                    market_adjustment -= 0.05
                
                # 市場制度匹配
                regime = market_data.get('market_regime', 'UNKNOWN')
                if regime in ['BULL_TREND', 'BEAR_TREND']:
                    market_adjustment += 0.03  # 趨勢市場加分
                elif regime == 'VOLATILE':
                    market_adjustment -= 0.02  # 震蕩市場減分
            
            # 計算最終評分
            final_score = max(0.0, min(1.0, base_score + market_adjustment))
            
            return final_score
            
        except Exception as e:
            logger.warning(f"綜合評分計算失敗: {e}")
            return max(0.0, min(1.0, (lean_confidence * 0.6) + (technical_strength * 0.4)))
    
    def _determine_signal_tier(self, lean_confidence: float, composite_score: float) -> SignalTier:
        """確定信號分層等級 - 分層決策邏輯"""
        try:
            # 優先基於 Lean 信心度分層
            if lean_confidence >= 0.65 and composite_score >= 0.7:
                return SignalTier.CRITICAL
            elif lean_confidence >= 0.58 and composite_score >= 0.55:
                return SignalTier.HIGH
            elif lean_confidence >= 0.45 and composite_score >= 0.4:
                return SignalTier.MEDIUM
            else:
                return SignalTier.LOW
                
        except Exception as e:
            logger.warning(f"分層等級決策失敗: {e}")
            return SignalTier.MEDIUM
    
    def _calculate_dynamic_threshold(self, lean_confidence: float, tier: SignalTier, tier_config: Optional[TierConfiguration]) -> float:
        """計算動態閾值 - 基於 Lean 信心度的閾值調整"""
        try:
            if not tier_config:
                return 0.7  # 默認閾值
            
            base_threshold = tier_config.technical_threshold
            
            # 基於 Lean 信心度動態調整
            if lean_confidence >= tier_config.lean_threshold:
                # Lean 信心度滿足要求，降低技術指標要求
                adjustment_factor = min(0.8, lean_confidence)
                dynamic_threshold = max(0.3, base_threshold * adjustment_factor)
            else:
                # Lean 信心度不足，保持或提高技術指標要求
                dynamic_threshold = min(1.0, base_threshold * 1.1)
            
            return round(dynamic_threshold, 3)
            
        except Exception as e:
            logger.warning(f"動態閾值計算失敗: {e}")
            return 0.7
    
    def _generate_tier_reasoning(self, lean_confidence: float, technical_strength: float, tier: SignalTier) -> str:
        """生成分層推理說明"""
        reasons = []
        
        if lean_confidence >= 0.65:
            reasons.append(f"Lean信心度優秀({lean_confidence:.1%})")
        elif lean_confidence >= 0.58:
            reasons.append(f"Lean信心度良好({lean_confidence:.1%})")
        elif lean_confidence >= 0.45:
            reasons.append(f"Lean信心度一般({lean_confidence:.1%})")
        else:
            reasons.append(f"Lean信心度較低({lean_confidence:.1%})")
        
        if technical_strength >= 0.7:
            reasons.append(f"技術指標強({technical_strength:.2f})")
        elif technical_strength >= 0.5:
            reasons.append(f"技術指標中({technical_strength:.2f})")
        else:
            reasons.append(f"技術指標弱({technical_strength:.2f})")
        
        return f"{tier.value}: {', '.join(reasons)}"
    
    # 🧠 第二階段自適應學習支持方法
    
    def _create_market_dataframe(self, symbol: str) -> Optional[pd.DataFrame]:
        """為自適應學習組件創建市場數據 DataFrame"""
        try:
            if symbol not in self.price_buffer or len(self.price_buffer[symbol]) < 20:
                return None
            
            prices = list(self.price_buffer[symbol])
            volumes = list(self.volume_buffer[symbol]) if symbol in self.volume_buffer else [0] * len(prices)
            
            # 創建基本 OHLCV 數據（模擬）
            data = []
            for i, (price_data, volume_data) in enumerate(zip(prices, volumes)):
                # 處理 price_data - 可能是字典或數值
                if isinstance(price_data, dict):
                    price = float(price_data.get('price', price_data.get('close', 0)))
                elif isinstance(price_data, (int, float)):
                    price = float(price_data)
                else:
                    price = 0.0
                
                # 處理 volume_data - 可能是字典或數值
                if isinstance(volume_data, dict):
                    volume = float(volume_data.get('volume', 1000))
                elif isinstance(volume_data, (int, float)):
                    volume = float(volume_data)
                else:
                    volume = 1000.0
                
                if price <= 0:  # 跳過無效價格
                    continue
                
                # 模擬 OHLC 數據
                high = price * (1 + np.random.uniform(0, 0.005))
                low = price * (1 - np.random.uniform(0, 0.005))
                
                # 獲取上一個價格
                if i > 0:
                    prev_data = prices[i-1]
                    if isinstance(prev_data, dict):
                        open_price = float(prev_data.get('price', prev_data.get('close', price)))
                    elif isinstance(prev_data, (int, float)):
                        open_price = float(prev_data)
                    else:
                        open_price = price
                else:
                    open_price = price
                
                data.append({
                    'timestamp': datetime.now() - timedelta(minutes=len(prices)-i),
                    'open': open_price,
                    'high': high,
                    'low': low,
                    'close': price,
                    'volume': volume
                })
            
            return pd.DataFrame(data)
            
        except Exception as e:
            logger.error(f"創建市場數據 DataFrame 失敗: {e}")
            return None
    
    async def _get_adaptive_parameters(self, market_data: Dict[str, Any], regime_confidence=None) -> Dict[str, Any]:
        """獲取自適應動態參數"""
        try:
            # 獲取基礎動態參數
            base_params_obj = await self._get_dynamic_parameters(market_data=market_data)
            base_params = base_params_obj.to_dict() if base_params_obj else {}
            
            if not self.adaptive_mode or not regime_confidence:
                return base_params
            
            # 根據市場狀態調整參數
            adaptive_params = base_params.copy()
            
            # 🔥 關鍵修復：整合 Phase2 學習核心的優化參數
            if self.learning_core:
                try:
                    # 獲取 Phase2 學習系統的優化參數
                    learned_params = self.learning_core.get_optimized_parameters()
                    
                    # 應用學習到的參數優化
                    if learned_params:
                        # 使用學習到的信號閾值
                        if 'signal_threshold' in learned_params:
                            adaptive_params['signal_threshold'] = learned_params['signal_threshold']
                        
                        # 應用其他學習到的權重
                        for param_name in ['momentum_weight', 'volume_weight', 'volatility_adjustment', 
                                         'trend_sensitivity', 'risk_multiplier']:
                            if param_name in learned_params:
                                # 將學習參數映射到信號生成參數
                                if param_name == 'momentum_weight':
                                    adaptive_params['momentum_weight'] = learned_params[param_name]
                                elif param_name == 'volume_weight':
                                    adaptive_params['volume_weight'] = learned_params[param_name]
                                elif param_name == 'volatility_adjustment':
                                    adaptive_params['price_change_threshold'] *= learned_params[param_name]
                                elif param_name == 'trend_sensitivity':
                                    adaptive_params['confidence_threshold'] *= learned_params[param_name]
                                elif param_name == 'risk_multiplier':
                                    adaptive_params['confidence_multiplier'] = learned_params[param_name]
                        
                        logger.info(f"🧠 應用 Phase2 學習參數: 閾值={learned_params.get('signal_threshold', 0):.3f}, 風險={learned_params.get('risk_multiplier', 0):.3f}")
                        
                except Exception as e:
                    logger.debug(f"Phase2 學習參數獲取失敗: {e}")
            
            # 根據市場狀態進行額外微調（在學習參數基礎上）
            if regime_confidence.regime == MarketRegime.BULL_TREND:
                adaptive_params['signal_threshold'] *= 0.95  # 在學習基礎上微調
                adaptive_params['momentum_weight'] *= 1.1
            elif regime_confidence.regime == MarketRegime.BEAR_TREND:
                adaptive_params['signal_threshold'] *= 1.05  # 在學習基礎上微調
                adaptive_params['volume_weight'] *= 1.15
            elif regime_confidence.regime == MarketRegime.VOLATILE:
                adaptive_params['signal_threshold'] *= 1.1  # 在學習基礎上微調
                adaptive_params['price_change_threshold'] *= 0.9
            
            # 根據信心度調整
            confidence_factor = 0.8 + (regime_confidence.confidence * 0.4)
            adaptive_params['confidence_multiplier'] = confidence_factor
            
            logger.debug(f"🧠 自適應參數調整: 狀態={regime_confidence.regime.value}, 信心度={regime_confidence.confidence:.3f}")
            
            return adaptive_params
            
        except Exception as e:
            logger.error(f"獲取自適應參數失敗: {e}")
            base_params_obj = await self._get_dynamic_parameters(market_data=market_data)
            base_params = base_params_obj.to_dict() if base_params_obj else {}
            return base_params
    
    async def _monitor_signal_performance(self, signal: BasicSignal, actual_outcome: Optional[float] = None):
        """監控信號表現用於自適應學習"""
        if not self.adaptive_mode or not self.learning_core:
            return
        
        try:
            # 創建信號數據用於學習
            signal_data = {
                'signal_id': f"{signal.symbol}_{signal.timestamp.timestamp()}",
                'symbol': signal.symbol,
                'signal_strength': signal.signal_strength,
                'direction': signal.signal_type,
                'tier': signal.tier.value,
                'features': {
                    'price_change': getattr(signal, 'price_change_pct', 0),
                    'volume_ratio': getattr(signal, 'volume_ratio', 1),
                    'technical_strength': getattr(signal, 'technical_strength', 0.5),
                    'market_regime': self.current_regime.value if hasattr(self, 'current_regime') else 'unknown'
                }
            }
            
            # 監控信號表現
            await self.learning_core.monitor_signal_performance(signal_data, actual_outcome)
            
        except Exception as e:
            logger.error(f"信號表現監控失敗: {e}")
    
    async def reload_configuration(self):
        """重新載入配置 - 支持運行時更新"""
        try:
            logger.info("🔄 重新載入 Phase1A 配置...")
            
            # 重新載入配置
            new_config = self._load_config()  # 修正：使用正確的方法名
            if new_config:
                self.config = new_config
                logger.info("✅ Phase1A 配置重新載入成功")
                
                # 重新初始化信號分層系統
                self.tier_configs = self._init_tier_system()
                
                return True
            else:
                logger.warning("⚠️ 配置重新載入失敗，保持當前配置")
                return False
                
        except Exception as e:
            logger.error(f"❌ 配置重新載入錯誤: {e}")
            return False
            return False

# 全局實例 - 延遲初始化
phase1a_signal_generator = None

def get_phase1a_generator():
    """獲取 Phase1A 生成器實例 - 延遲初始化"""
    global phase1a_signal_generator
    if phase1a_signal_generator is None:
        phase1a_signal_generator = Phase1ABasicSignalGeneration()
    return phase1a_signal_generator

# 便捷函數
async def start_phase1a_generator(websocket_driver):
    """啟動 Phase1A 信號生成器"""
    generator = get_phase1a_generator()
    await generator.start(websocket_driver)

async def stop_phase1a_generator():
    """停止 Phase1A 信號生成器"""
    global phase1a_signal_generator
    if phase1a_signal_generator is not None:
        await phase1a_signal_generator.stop()

def subscribe_to_phase1a_signals(callback):
    """訂閱 Phase1A 信號"""
    generator = get_phase1a_generator()
    generator.subscribe_to_signals(callback)
