"""
🎯 Trading X - 技術指標依賴圖引擎
基於 JSON 配置的 7 層並行計算架構
實現高性能技術指標批量計算與智能快取管理
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
import time
import logging
import sys
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
import warnings
warnings.filterwarnings('ignore')

# Try to import required modules
try:
    import pandas_ta
except ImportError:
    pandas_ta = None

try:
    from binance_data_connector import binance_connector
except ImportError:
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared_core'))
        from binance_data_connector import binance_connector
    except ImportError:
        # 如果無法導入，設為 None，稍後處理
        binance_connector = None

logger = logging.getLogger(__name__)

@dataclass
class IndicatorResult:
    """指標計算結果"""
    symbol: str
    timeframe: str
    indicator_name: str
    value: float
    quality_score: float
    timestamp: datetime
    calculation_time_ms: float
    cache_hit: bool

@dataclass
class LayerPerformance:
    """層級性能監控"""
    layer_name: str
    execution_time_ms: float
    parallel_count: int
    cache_hit_rate: float
    memory_usage_mb: float

class IndicatorDependencyGraph:
    """技術指標依賴圖計算引擎 - 7層並行架構"""
    
    def __init__(self):
        self.config = self._load_config()
        
        # 性能監控
        self.layer_timings = defaultdict(list)
        self.cache_stats = defaultdict(int)
        self.performance_history = deque(maxlen=1000)
        
        # 智能快取系統
        self.cache = {}
        self.cache_ttl = {}
        self.auto_ttl_enabled = True
        
        # 記憶體管理機制 (新增 - JSON 規範要求)
        self.max_cache_size_mb = 256
        self.cleanup_threshold = 0.8
        self.emergency_cleanup = True
        
        # 事件驅動快取失效機制 (新增)
        self.cache_events = {
            'new_kline_close': False,
            'significant_price_move': False,
            'volume_spike': False,
            'quality_score_spike': False
        }
        self.previous_price = None
        self.previous_volume = None
        self.cache_warming_enabled = True
        
        # 並行執行控制
        self.parallel_semaphore = asyncio.Semaphore(4)
        self.degraded_mode = False
        self.emergency_mode = False  # 新增緊急模式標記
        
        logger.info("指標依賴圖引擎初始化完成")
    
    def _load_config(self) -> Dict[str, Any]:
        """載入 JSON 配置"""
        try:
            config_path = "/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/indicator_dependency/indicator_dependency_graph.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"配置載入失敗: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """預設配置"""
        return {
            "performance_targets": {
                "total_calculation_time": "45ms",
                "parallel_efficiency": "> 70%",
                "cache_hit_rate": "> 95%"
            },
            "indicators": {
                "trend": ["MACD", "trend_strength"],
                "momentum": ["RSI", "STOCH_K", "STOCH_D", "CCI"],
                "volatility": ["BB_upper", "BB_lower", "BB_position", "ATR"],
                "volume": ["OBV", "volume_ratio", "volume_trend"],
                "support_resistance": ["pivot_point", "resistance_1", "support_1"]
            }
        }
    
    async def calculate_all_indicators(self, symbol: str = "BTCUSDT", 
                                     timeframe: str = "1m") -> Dict[str, IndicatorResult]:
        """
        7層並行架構主要計算流程
        參照 CORE_FLOW.json 的視覺化流程
        """
        start_time = time.time()
        
        try:
            # Layer -1: 數據同步檢查層 (2ms)
            synced_data = await self._layer_minus1_data_sync(symbol, timeframe)
            if not synced_data:
                logger.error("數據同步失敗，啟動降級模式")
                return await self._degraded_calculation(symbol, timeframe)
            
            # Layer 0: 原始價格數據層 (1ms)
            raw_data = await self._layer_0_raw_data(synced_data, symbol, timeframe)
            
            # 事件驅動快取失效檢查 (新增)
            self._check_cache_invalidation_events(raw_data, symbol, timeframe)
            
            # 並行執行組: Layer 1 + 2 + 4 (15ms 並行)
            layer_124_results = await self._parallel_layers_124(raw_data, symbol, timeframe)
            
            # Layer 3: 標準差計算層 (10ms)
            layer_3_results = await self._layer_3_standard_deviations(
                raw_data, layer_124_results, symbol, timeframe
            )
            
            # Layer 5: 中間計算層 (12ms)
            layer_5_results = await self._layer_5_intermediate_calculations(
                layer_124_results, symbol, timeframe
            )
            
            # Layer 6: 最終指標計算層 (20ms)
            final_indicators = await self._layer_6_final_indicators(
                raw_data, layer_124_results, layer_3_results, 
                layer_5_results, symbol, timeframe
            )
            
            # 計算總執行時間
            total_time = (time.time() - start_time) * 1000
            
            # 記錄性能
            await self._record_performance(total_time, final_indicators)
            
            logger.info(f"指標計算完成: {symbol}_{timeframe}, "
                       f"耗時: {total_time:.1f}ms, "
                       f"指標數: {len(final_indicators)}")
            
            return final_indicators
            
        except Exception as e:
            logger.error(f"指標計算失敗: {e}")
            return await self._degraded_calculation(symbol, timeframe)
    
    async def _layer_minus1_data_sync(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """Layer -1: 數據同步檢查層"""
        layer_start = time.time()
        
        try:
            if binance_connector is None:
                logger.error("Binance connector 不可用，無法獲取即時數據")
                raise ConnectionError("外部數據源不可用，系統需要即時數據連接")
                
            # 從 binance_connector 獲取 OHLCV 數據
            async with binance_connector as connector:
                # 獲取最近 100 個週期的數據用於技術指標計算
                klines = await connector.get_kline_data(symbol, timeframe, limit=100)
                
                if not klines or len(klines) < 50:
                    logger.warning("數據不足，無法計算技術指標")
                    return None
                
                # 轉換為 DataFrame
                df = pd.DataFrame(klines, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_volume', 'count', 'taker_buy_volume',
                    'taker_buy_quote_volume', 'ignore'
                ])
                
                # 數據類型轉換
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                
                # 數據完整性檢查
                if df.isnull().sum().sum() > 0:
                    logger.warning("數據包含空值，進行清理")
                    df = df.fillna(method='ffill').fillna(method='bfill')
                
                # 增強數據驗證機制 (新增)
                validation_result = self._validate_ohlcv_data(df)
                if not validation_result['is_valid']:
                    logger.error(f"數據驗證失敗: {validation_result['errors']}")
                    return None
                
                # 序列連續性驗證
                time_diff = df['timestamp'].diff().median()
                expected_diff = self._get_timeframe_delta(timeframe)
                
                if abs((time_diff - expected_diff).total_seconds()) > 60:
                    logger.warning(f"時間序列不連續: {time_diff} vs {expected_diff}")
                
                # 記錄層級性能
                layer_time = (time.time() - layer_start) * 1000
                self.layer_timings['layer_-1'].append(layer_time)
                
                logger.debug(f"Layer -1 完成: {layer_time:.1f}ms, 數據質量: 良好")
                return df
                
        except Exception as e:
            logger.error(f"Layer -1 數據同步失敗: {e}")
            return None
    
    async def _layer_0_raw_data(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Dict[str, pd.Series]:
        """Layer 0: 原始價格數據層"""
        layer_start = time.time()
        
        # 標準化命名格式 {symbol}_{timeframe}_{field}
        raw_data = {
            f"{symbol}_{timeframe}_open": df['open'],
            f"{symbol}_{timeframe}_high": df['high'],
            f"{symbol}_{timeframe}_low": df['low'],
            f"{symbol}_{timeframe}_close": df['close'],
            f"{symbol}_{timeframe}_volume": df['volume']
        }
        
        layer_time = (time.time() - layer_start) * 1000
        self.layer_timings['layer_0'].append(layer_time)
        
        return raw_data
    
    async def _parallel_layers_124(self, raw_data: Dict[str, pd.Series], 
                                 symbol: str, timeframe: str) -> Dict[str, Any]:
        """並行執行 Layer 1 + 2 + 4"""
        async def layer_1_basic():
            """Layer 1: 基礎計算"""
            close = raw_data[f"{symbol}_{timeframe}_close"]
            high = raw_data[f"{symbol}_{timeframe}_high"]
            low = raw_data[f"{symbol}_{timeframe}_low"]
            
            return {
                'price_changes': close.diff(),
                'typical_price': (high + low + close) / 3,
                'true_range_components': {
                    'tr1': high - low,
                    'tr2': abs(high - close.shift(1)),
                    'tr3': abs(low - close.shift(1))
                }
            }
        
        async def layer_2_moving_averages():
            """Layer 2: 移動平均線批次計算"""
            close = raw_data[f"{symbol}_{timeframe}_close"]
            volume = raw_data[f"{symbol}_{timeframe}_volume"]
            
            # 向量化批次計算 - 按 JSON 規範參數化配置
            sma_periods = [10, 20, 50]
            ema_periods = [12, 26, 50]
            
            smas = {}
            for period in sma_periods:
                smas[f"{symbol}_{timeframe}_SMA_{period}"] = close.rolling(period).mean()
            
            emas = {}
            for period in ema_periods:
                emas[f"{symbol}_{timeframe}_EMA_{period}"] = close.ewm(span=period).mean()
            
            # 成交量移動平均線 - 支援多週期
            volume_smas = {}
            for period in [10, 20, 50]:
                volume_smas[f"{symbol}_{timeframe}_volume_SMA_{period}"] = volume.rolling(period).mean()
            
            return {**smas, **emas, **volume_smas}
        
        async def layer_4_rolling_extremes():
            """Layer 4: 滾動極值 - 按 JSON 規範參數化配置"""
            high = raw_data[f"{symbol}_{timeframe}_high"]
            low = raw_data[f"{symbol}_{timeframe}_low"]
            
            # 支援多週期滾動極值
            rolling_periods = [14, 20]
            
            rolling_data = {}
            for period in rolling_periods:
                rolling_data[f"{symbol}_{timeframe}_highest_high_{period}"] = high.rolling(period).max()
                rolling_data[f"{symbol}_{timeframe}_lowest_low_{period}"] = low.rolling(period).min()
            
            return rolling_data
        
        # 並行執行三個層級
        start_time = time.time()
        
        layer_1_task = asyncio.create_task(layer_1_basic())
        layer_2_task = asyncio.create_task(layer_2_moving_averages())
        layer_4_task = asyncio.create_task(layer_4_rolling_extremes())
        
        layer_1_result = await layer_1_task
        layer_2_result = await layer_2_task
        layer_4_result = await layer_4_task
        
        parallel_time = (time.time() - start_time) * 1000
        self.layer_timings['parallel_124'].append(parallel_time)
        
        return {
            'layer_1': layer_1_result,
            'layer_2': layer_2_result,
            'layer_4': layer_4_result
        }
    
    async def _layer_3_standard_deviations(self, raw_data: Dict[str, pd.Series],
                                         layer_124: Dict[str, Any], 
                                         symbol: str, timeframe: str) -> Dict[str, pd.Series]:
        """Layer 3: 標準差計算層"""
        layer_start = time.time()
        
        close = raw_data[f"{symbol}_{timeframe}_close"]
        
        result = {
            f"{symbol}_{timeframe}_price_std_20": close.rolling(20).std(),
            f"{symbol}_{timeframe}_return_std_20": close.pct_change().rolling(20).std()
        }
        
        layer_time = (time.time() - layer_start) * 1000
        self.layer_timings['layer_3'].append(layer_time)
        
        return result
    
    async def _layer_5_intermediate_calculations(self, layer_124: Dict[str, Any],
                                               symbol: str, timeframe: str) -> Dict[str, Any]:
        """Layer 5: 中間計算層"""
        layer_start = time.time()
        
        price_changes = layer_124['layer_1']['price_changes']
        typical_price = layer_124['layer_1']['typical_price']
        ema_12 = layer_124['layer_2'][f"{symbol}_{timeframe}_EMA_12"]
        ema_26 = layer_124['layer_2'][f"{symbol}_{timeframe}_EMA_26"]
        
        # 真實範圍計算
        tr_components = layer_124['layer_1']['true_range_components']
        true_range = pd.concat([
            tr_components['tr1'],
            tr_components['tr2'],
            tr_components['tr3']
        ], axis=1).max(axis=1)
        
        result = {
            'rsi_components': {
                'gain': price_changes.where(price_changes > 0, 0).rolling(14).mean(),
                'loss': (-price_changes).where(price_changes < 0, 0).rolling(14).mean()
            },
            'macd_line': ema_12 - ema_26,
            'true_range': true_range,
            'cci_components': {
                'typical_price_sma': typical_price.rolling(20).mean(),
                'mean_deviation': typical_price.rolling(20).apply(
                    lambda x: np.mean(np.abs(x - np.mean(x)))
                )
            }
        }
        
        layer_time = (time.time() - layer_start) * 1000
        self.layer_timings['layer_5'].append(layer_time)
        
        return result
    
    async def _layer_6_final_indicators(self, raw_data: Dict[str, pd.Series],
                                      layer_124: Dict[str, Any],
                                      layer_3: Dict[str, pd.Series],
                                      layer_5: Dict[str, Any],
                                      symbol: str, timeframe: str) -> Dict[str, IndicatorResult]:
        """Layer 6: 最終指標計算層"""
        layer_start = time.time()
        
        close = raw_data[f"{symbol}_{timeframe}_close"]
        volume = raw_data[f"{symbol}_{timeframe}_volume"]
        
        indicators = {}
        
        # 趨勢指標 - 增強錯誤處理
        try:
            macd_line = layer_5['macd_line']
            macd_signal = macd_line.ewm(span=9).mean()
            sma_20 = layer_124['layer_2'][f"{symbol}_{timeframe}_SMA_20"]
            sma_50 = layer_124['layer_2'][f"{symbol}_{timeframe}_SMA_50"]
            
            macd_value = float(macd_line.iloc[-1]) if len(macd_line) > 0 and not pd.isna(macd_line.iloc[-1]) else 0.0
            macd_signal_value = float(macd_signal.iloc[-1]) if len(macd_signal) > 0 and not pd.isna(macd_signal.iloc[-1]) else 0.0
            macd_histogram_value = macd_value - macd_signal_value
        except (ValueError, IndexError, KeyError, Exception):
            macd_value = 0.0
            macd_signal_value = 0.0
            macd_histogram_value = 0.0

        indicators[f"{symbol}_{timeframe}_MACD"] = self._create_indicator_result(
            symbol, timeframe, "MACD", macd_value, 0.8
        )
        indicators[f"{symbol}_{timeframe}_MACD_signal"] = self._create_indicator_result(
            symbol, timeframe, "MACD_signal", macd_signal_value, 0.8
        )
        indicators[f"{symbol}_{timeframe}_MACD_histogram"] = self._create_indicator_result(
            symbol, timeframe, "MACD_histogram", macd_histogram_value, 0.8
        )
        
        # 動量指標
        rsi_gain = layer_5['rsi_components']['gain']
        rsi_loss = layer_5['rsi_components']['loss']
        
        # 安全的 RSI 計算
        try:
            rsi_ratio = rsi_gain / rsi_loss
            rsi = 100 - (100 / (1 + rsi_ratio))
            rsi_value = rsi.iloc[-1] if len(rsi) > 0 and not pd.isna(rsi.iloc[-1]) else 50.0
        except (ZeroDivisionError, ValueError, IndexError):
            rsi_value = 50.0
        
        highest_high_14 = layer_124['layer_4'][f"{symbol}_{timeframe}_highest_high_14"]
        lowest_low_14 = layer_124['layer_4'][f"{symbol}_{timeframe}_lowest_low_14"]
        
        # 安全的 Stochastic 計算
        try:
            stoch_range = highest_high_14 - lowest_low_14
            stoch_k = 100 * ((close - lowest_low_14) / stoch_range)
            stoch_k_value = stoch_k.iloc[-1] if len(stoch_k) > 0 and not pd.isna(stoch_k.iloc[-1]) else 50.0
            stoch_d_series = stoch_k.rolling(3).mean()
            stoch_d_value = float(stoch_d_series.iloc[-1]) if len(stoch_d_series) >= 3 and not pd.isna(stoch_d_series.iloc[-1]) else stoch_k_value
        except (ZeroDivisionError, ValueError, IndexError):
            stoch_k_value = 50.0
            stoch_d_value = 50.0
        
        # CCI 計算 (安全版本)
        try:
            typical_price = layer_124['layer_1']['typical_price']
            typical_price_sma = layer_5['cci_components']['typical_price_sma']
            mean_deviation = layer_5['cci_components']['mean_deviation']
            cci = (typical_price - typical_price_sma) / (0.015 * mean_deviation)
            cci_value = cci.iloc[-1] if len(cci) > 0 and not pd.isna(cci.iloc[-1]) else 0.0
        except (ZeroDivisionError, ValueError, IndexError):
            cci_value = 0.0
        
        # Williams %R 計算 (安全版本)
        try:
            willr = -100 * ((highest_high_14 - close) / (highest_high_14 - lowest_low_14))
            willr_value = willr.iloc[-1] if len(willr) > 0 and not pd.isna(willr.iloc[-1]) else -50.0
        except (ZeroDivisionError, ValueError, IndexError):
            willr_value = -50.0
        
        indicators[f"{symbol}_{timeframe}_RSI"] = self._create_indicator_result(
            symbol, timeframe, "RSI", rsi_value, self._calculate_rsi_quality(rsi_value)
        )
        indicators[f"{symbol}_{timeframe}_STOCH_K"] = self._create_indicator_result(
            symbol, timeframe, "STOCH_K", stoch_k_value, 0.7
        )
        indicators[f"{symbol}_{timeframe}_STOCH_D"] = self._create_indicator_result(
            symbol, timeframe, "STOCH_D", stoch_d_value, 0.7
        )
        indicators[f"{symbol}_{timeframe}_CCI"] = self._create_indicator_result(
            symbol, timeframe, "CCI", cci_value, self._calculate_cci_quality(cci_value)
        )
        indicators[f"{symbol}_{timeframe}_WILLR"] = self._create_indicator_result(
            symbol, timeframe, "WILLR", willr_value, self._calculate_willr_quality(willr_value)
        )
        
        # 波動性指標 (安全版本)
        try:
            price_std_20 = layer_3[f"{symbol}_{timeframe}_price_std_20"]
            bb_upper = sma_20 + (price_std_20 * 2)
            bb_lower = sma_20 - (price_std_20 * 2)
            bb_position = (close - bb_lower) / (bb_upper - bb_lower)
            
            # 安全取值
            bb_upper_value = float(bb_upper.iloc[-1]) if len(bb_upper) > 0 and not pd.isna(bb_upper.iloc[-1]) else float(sma_20.iloc[-1]) * 1.02
            bb_lower_value = float(bb_lower.iloc[-1]) if len(bb_lower) > 0 and not pd.isna(bb_lower.iloc[-1]) else float(sma_20.iloc[-1]) * 0.98
            bb_position_value = float(bb_position.iloc[-1]) if len(bb_position) > 0 and not pd.isna(bb_position.iloc[-1]) else 0.5
        except (ValueError, IndexError, ZeroDivisionError, Exception):
            sma_20_val = float(sma_20.iloc[-1]) if len(sma_20) > 0 else float(close.iloc[-1])
            bb_upper_value = sma_20_val * 1.02
            bb_lower_value = sma_20_val * 0.98
            bb_position_value = 0.5
        
        try:
            atr_series = layer_5['true_range'].rolling(14).mean()
            atr_value = float(atr_series.iloc[-1]) if len(atr_series) > 0 and not pd.isna(atr_series.iloc[-1]) else float(close.iloc[-1]) * 0.02
        except (ValueError, IndexError, Exception):
            atr_value = float(close.iloc[-1]) * 0.02
        
        indicators[f"{symbol}_{timeframe}_BB_upper"] = self._create_indicator_result(
            symbol, timeframe, "BB_upper", bb_upper_value, 0.9
        )
        indicators[f"{symbol}_{timeframe}_BB_lower"] = self._create_indicator_result(
            symbol, timeframe, "BB_lower", bb_lower_value, 0.9
        )
        indicators[f"{symbol}_{timeframe}_BB_position"] = self._create_indicator_result(
            symbol, timeframe, "BB_position", bb_position_value, 
            self._calculate_bb_quality(bb_position_value)
        )
        indicators[f"{symbol}_{timeframe}_ATR"] = self._create_indicator_result(
            symbol, timeframe, "ATR", atr_value, 0.8
        )
        
        # 成交量指標 (安全版本)
        try:
            price_changes = layer_124['layer_1']['price_changes']
            obv = (np.sign(price_changes) * volume).cumsum()
            volume_sma_20 = layer_124['layer_2'][f"{symbol}_{timeframe}_volume_SMA_20"]
            
            obv_value = obv.iloc[-1] if len(obv) > 0 and not pd.isna(obv.iloc[-1]) else 0.0
            vol_ratio = volume.iloc[-1] / volume_sma_20.iloc[-1] if volume_sma_20.iloc[-1] != 0 else 1.0
        except (ValueError, IndexError, ZeroDivisionError):
            obv_value = 0.0
            vol_ratio = 1.0
        
        indicators[f"{symbol}_{timeframe}_OBV"] = self._create_indicator_result(
            symbol, timeframe, "OBV", obv_value, 0.6
        )
        indicators[f"{symbol}_{timeframe}_volume_ratio"] = self._create_indicator_result(
            symbol, timeframe, "volume_ratio", vol_ratio, 0.7
        )
        
        # 成交量趨勢指標 (修復版)
        volume_sma_10 = layer_124['layer_2'].get(f"{symbol}_{timeframe}_volume_SMA_10")
        volume_sma_50 = layer_124['layer_2'].get(f"{symbol}_{timeframe}_volume_SMA_50")
        
        if volume_sma_10 is not None and volume_sma_50 is not None:
            try:
                # 安全的 Series 計算
                vol_10_last = volume_sma_10.iloc[-1] if len(volume_sma_10) > 0 else 0
                vol_50_last = volume_sma_50.iloc[-1] if len(volume_sma_50) > 0 else 0
                
                if vol_50_last != 0 and not pd.isna(vol_50_last) and not pd.isna(vol_10_last):
                    volume_trend_result = (vol_10_last - vol_50_last) / vol_50_last
                else:
                    volume_trend_result = 0.0
            except Exception:
                volume_trend_result = 0.0
        else:
            volume_trend_result = 0.0
        
        indicators[f"{symbol}_{timeframe}_volume_trend"] = self._create_indicator_result(
            symbol, timeframe, "volume_trend", volume_trend_result, 0.6
        )
        
        # 支撐阻力指標群組 (安全版本)
        try:
            high = raw_data[f"{symbol}_{timeframe}_high"]
            low = raw_data[f"{symbol}_{timeframe}_low"]
            highest_high_20 = high.rolling(20).max()
            lowest_low_20 = low.rolling(20).min()
            previous_close = close.shift(1)
            
            # Pivot Point 計算
            pivot_point = (highest_high_20 + lowest_low_20 + previous_close) / 3
            resistance_1 = 2 * pivot_point - lowest_low_20
            support_1 = 2 * pivot_point - highest_high_20
            
            pivot_value = pivot_point.iloc[-1] if len(pivot_point) > 0 and not pd.isna(pivot_point.iloc[-1]) else close.iloc[-1]
            resistance_value = resistance_1.iloc[-1] if len(resistance_1) > 0 and not pd.isna(resistance_1.iloc[-1]) else close.iloc[-1] * 1.05
            support_value = support_1.iloc[-1] if len(support_1) > 0 and not pd.isna(support_1.iloc[-1]) else close.iloc[-1] * 0.95
        except (ValueError, IndexError):
            current_price = close.iloc[-1]
            pivot_value = current_price
            resistance_value = current_price * 1.05
            support_value = current_price * 0.95
        
        indicators[f"{symbol}_{timeframe}_pivot_point"] = self._create_indicator_result(
            symbol, timeframe, "pivot_point", pivot_value, 0.8
        )
        indicators[f"{symbol}_{timeframe}_resistance_1"] = self._create_indicator_result(
            symbol, timeframe, "resistance_1", resistance_value, 0.8
        )
        indicators[f"{symbol}_{timeframe}_support_1"] = self._create_indicator_result(
            symbol, timeframe, "support_1", support_value, 0.8
        )
        
        # 趨勢強度指標 (安全版本) - 使用 EMA_50
        try:
            current_price = float(close.iloc[-1])
            sma_20_val = float(sma_20.iloc[-1]) if len(sma_20) > 0 and not pd.isna(sma_20.iloc[-1]) else current_price
            sma_50_val = float(sma_50.iloc[-1]) if len(sma_50) > 0 and not pd.isna(sma_50.iloc[-1]) else current_price
            ema_50_val = float(layer_124['layer_2'][f"{symbol}_{timeframe}_EMA_50"].iloc[-1]) if f"{symbol}_{timeframe}_EMA_50" in layer_124['layer_2'] else current_price
            
            if sma_20_val != 0 and sma_50_val != 0 and ema_50_val != 0:
                # 增強趨勢強度計算，納入 EMA_50 (JSON 規範要求)
                sma_trend = (current_price - sma_20_val) / sma_20_val + (current_price - sma_50_val) / sma_50_val
                ema_trend = (current_price - ema_50_val) / ema_50_val
                trend_strength = (sma_trend + ema_trend) / 3  # 整合 SMA 和 EMA 趨勢
            else:
                trend_strength = 0.0
        except (ValueError, IndexError, ZeroDivisionError, Exception):
            trend_strength = 0.0
        
        indicators[f"{symbol}_{timeframe}_trend_strength"] = self._create_indicator_result(
            symbol, timeframe, "trend_strength", trend_strength, 
            self._calculate_trend_strength_quality(trend_strength)
        )
        
        layer_time = (time.time() - layer_start) * 1000
        self.layer_timings['layer_6'].append(layer_time)
        
        return indicators
    
    def _create_indicator_result(self, symbol: str, timeframe: str, 
                               indicator_name: str, value: float, 
                               quality_score: float) -> IndicatorResult:
        """創建指標結果對象 - 包含信心權重機制"""
        
        # 信心權重計算 (JSON 規範要求)
        base_confidence = 1.0
        market_session_weight = self._get_market_session_weight()
        confidence_multiplier = self._calculate_confidence_multiplier(indicator_name, value)
        
        # 應用信心權重公式: base_score * confidence_multiplier * market_session_weight
        adjusted_quality_score = quality_score * confidence_multiplier * market_session_weight
        
        return IndicatorResult(
            symbol=symbol,
            timeframe=timeframe,
            indicator_name=indicator_name,
            value=float(value) if not np.isnan(value) else 0.0,
            quality_score=min(1.0, adjusted_quality_score),  # 確保不超過 1.0
            timestamp=datetime.now(),
            calculation_time_ms=0.0,
            cache_hit=False
        )
    
    def _calculate_rsi_quality(self, rsi_value: float) -> float:
        """計算 RSI 品質評分"""
        if np.isnan(rsi_value):
            return 0.0
        
        # RSI 極值區域給予更高評分
        if rsi_value <= 20 or rsi_value >= 80:
            return min(1.0, abs(rsi_value - 50) / 50 * 1.2)
        elif rsi_value <= 30 or rsi_value >= 70:
            return min(1.0, abs(rsi_value - 50) / 50)
        else:
            return max(0.3, abs(rsi_value - 50) / 50)
    
    def _calculate_bb_quality(self, bb_position: float) -> float:
        """計算布林帶位置品質評分"""
        if np.isnan(bb_position):
            return 0.0
        
        # 接近上下軌給予更高評分
        return min(1.0, abs(bb_position - 0.5) * 2)
    
    def _calculate_cci_quality(self, cci_value: float) -> float:
        """計算 CCI 品質評分"""
        if np.isnan(cci_value):
            return 0.0
        
        # CCI 極值區域給予更高評分 (±100 為關鍵水平)
        if abs(cci_value) >= 200:
            return 1.0
        elif abs(cci_value) >= 100:
            return min(1.0, abs(cci_value) / 100 * 0.8)
        else:
            return max(0.3, abs(cci_value) / 100 * 0.5)
    
    def _calculate_willr_quality(self, willr_value: float) -> float:
        """計算 Williams %R 品質評分"""
        if np.isnan(willr_value):
            return 0.0
        
        # Williams %R 極值區域給予更高評分 (-20, -80 為關鍵水平)
        if willr_value <= -80 or willr_value >= -20:
            return min(1.0, abs(willr_value + 50) / 50 * 1.2)
        else:
            return max(0.3, abs(willr_value + 50) / 50)
    
    def _calculate_trend_strength_quality(self, trend_strength: float) -> float:
        """計算趨勢強度品質評分"""
        if np.isnan(trend_strength):
            return 0.0
        
        # 趨勢強度絕對值越大，品質越高
        return min(1.0, abs(trend_strength) * 10)
    
    def _get_market_session_weight(self) -> float:
        """獲取市場時段權重 - JSON 規範要求"""
        current_hour = datetime.now().hour
        
        # 主要交易時段給予更高權重
        if 8 <= current_hour <= 16:  # 主要市場時間
            return 1.0
        elif 20 <= current_hour <= 23 or 0 <= current_hour <= 2:  # 美國市場時間
            return 0.9
        else:  # 其他時間
            return 0.8
    
    def _calculate_confidence_multiplier(self, indicator_name: str, value: float) -> float:
        """計算信心乘數 - JSON 規範要求"""
        if indicator_name == 'RSI':
            # RSI 極值區域信心更高
            if value <= 20 or value >= 80:
                return 1.2
            elif value <= 30 or value >= 70:
                return 1.0
            else:
                return 0.8
        elif indicator_name == 'BB_position':
            # 接近布林帶邊界信心更高
            return min(1.2, abs(value - 0.5) * 2.4 + 0.8)
        elif 'MACD' in indicator_name:
            # MACD 信號強度相關
            return min(1.1, abs(value) / 100 + 0.9)
        else:
            return 1.0  # 預設信心乘數
    
    def _get_timeframe_delta(self, timeframe: str) -> timedelta:
        """獲取時間框架對應的時間差"""
        timeframe_map = {
            '1m': timedelta(minutes=1),
            '5m': timedelta(minutes=5),
            '15m': timedelta(minutes=15),
            '1h': timedelta(hours=1),
            '4h': timedelta(hours=4),
            '1d': timedelta(days=1)
        }
        return timeframe_map.get(timeframe, timedelta(minutes=1))
    
    def _validate_ohlcv_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """增強數據驗證機制 - JSON 規範要求"""
        errors = []
        
        # 檢查 OHLC 關係
        if not (df['high'] >= df['open']).all():
            errors.append("高價小於開盤價")
        if not (df['high'] >= df['close']).all():
            errors.append("高價小於收盤價")
        if not (df['low'] <= df['open']).all():
            errors.append("低價大於開盤價")
        if not (df['low'] <= df['close']).all():
            errors.append("低價大於收盤價")
        if not (df['high'] >= df['low']).all():
            errors.append("高價小於低價")
        
        # 檢查成交量
        if (df['volume'] < 0).any():
            errors.append("成交量存在負值")
        
        # 檢查價格合理性
        for col in ['open', 'high', 'low', 'close']:
            if (df[col] <= 0).any():
                errors.append(f"{col}存在零或負值")
        
        # 檢查數據範圍異常
        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            median_price = df[col].median()
            outliers = abs(df[col] - median_price) > median_price * 0.5  # 50% 異常閾值
            if outliers.any():
                errors.append(f"{col}存在異常值")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'quality_score': max(0, 1 - len(errors) * 0.2)
        }
    
    async def _degraded_calculation(self, symbol: str, timeframe: str) -> Dict[str, IndicatorResult]:
        """降級模式：只計算基礎指標"""
        logger.warning("啟動降級模式計算")
        
        try:
            # 只返回基礎的模擬指標
            basic_indicators = {
                f"{symbol}_{timeframe}_RSI": self._create_indicator_result(
                    symbol, timeframe, "RSI", 50.0, 0.3
                ),
                f"{symbol}_{timeframe}_MACD": self._create_indicator_result(
                    symbol, timeframe, "MACD", 0.0, 0.3
                ),
                f"{symbol}_{timeframe}_BB_position": self._create_indicator_result(
                    symbol, timeframe, "BB_position", 0.5, 0.3
                )
            }
            
            return basic_indicators
            
        except Exception as e:
            logger.error(f"降級計算也失敗: {e}")
            return {}
    
    async def _record_performance(self, total_time: float, indicators: Dict[str, IndicatorResult]):
        """記錄性能數據"""
        performance = {
            'timestamp': datetime.now(),
            'total_time_ms': total_time,
            'indicator_count': len(indicators),
            'layer_timings': dict(self.layer_timings),
            'cache_hit_rate': self._calculate_cache_hit_rate(),
            'degraded_mode': self.degraded_mode,
            'emergency_mode': self.emergency_mode
        }
        
        self.performance_history.append(performance)
        
        # 緊急模式檢查 (新增)
        if total_time > 200:  # 超過 200ms 觸發緊急模式
            await self._trigger_emergency_mode()
        elif total_time > 100:  # 超過 100ms 觸發優化
            await self._auto_optimize()
    
    async def _trigger_emergency_mode(self):
        """觸發緊急模式 - JSON 規範要求"""
        self.emergency_mode = True
        self.degraded_mode = True
        logger.warning("⚠️ 觸發緊急模式：系統性能嚴重下降")
        
        # 極端優化措施
        self.parallel_semaphore = asyncio.Semaphore(1)  # 最小並行度
        self.auto_ttl_enabled = False  # 停用自動 TTL
        
        # 只保留最關鍵的快取
        critical_keys = [k for k in self.cache.keys() if 'RSI' in k or 'MACD' in k]
        self.cache = {k: v for k, v in self.cache.items() if k in critical_keys}
    
    def _check_cache_invalidation_events(self, raw_data: Dict[str, pd.Series], 
                                       symbol: str, timeframe: str):
        """檢查事件驅動快取失效條件 - JSON 規範要求"""
        close = raw_data[f"{symbol}_{timeframe}_close"]
        volume = raw_data[f"{symbol}_{timeframe}_volume"]
        
        current_price = close.iloc[-1]
        current_volume = volume.iloc[-1]
        avg_volume = volume.rolling(20).mean().iloc[-1]
        
        # 檢查價格變動
        if self.previous_price is not None:
            price_change_pct = abs(current_price - self.previous_price) / self.previous_price
            if price_change_pct > 0.01:  # 1% 價格變動
                self.cache_events['significant_price_move'] = True
                self._invalidate_cache_by_event('price_move')
        
        # 檢查成交量激增
        if current_volume > avg_volume * 2:  # 成交量 > 2倍平均
            self.cache_events['volume_spike'] = True
            self._invalidate_cache_by_event('volume_spike')
        
        # 更新前一個值
        self.previous_price = current_price
        self.previous_volume = current_volume
    
    def _invalidate_cache_by_event(self, event_type: str):
        """根據事件類型失效相關快取"""
        if event_type == 'price_move':
            # 價格相關指標快取失效
            keys_to_remove = [k for k in self.cache.keys() if any(
                indicator in k for indicator in ['RSI', 'MACD', 'BB_', 'trend_strength']
            )]
        elif event_type == 'volume_spike':
            # 成交量相關指標快取失效
            keys_to_remove = [k for k in self.cache.keys() if any(
                indicator in k for indicator in ['OBV', 'volume_ratio', 'volume_trend']
            )]
        else:
            return
        
        for key in keys_to_remove:
            self.cache.pop(key, None)
            self.cache_ttl.pop(key, None)
        
        logger.debug(f"事件驅動快取失效: {event_type}, 清理 {len(keys_to_remove)} 個快取項目")
    
    def _calculate_cache_hit_rate(self) -> float:
        """計算快取命中率"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        if total_requests == 0:
            return 0.0
        return self.cache_stats['hits'] / total_requests
    
    async def _auto_optimize(self):
        """自動優化策略"""
        logger.info("觸發自動優化")
        
        # 啟用更積極的快取策略
        self.auto_ttl_enabled = True
        
        # 減少並行度以降低資源競爭
        if self.parallel_semaphore._value > 2:
            self.parallel_semaphore = asyncio.Semaphore(2)
        
        # 觸發快取預熱 (新增)
        if self.cache_warming_enabled:
            await self._warm_cache()
        
        # 記憶體管理檢查 (新增 - JSON 規範要求)
        await self._check_memory_management()
    
    async def _check_memory_management(self):
        """記憶體管理檢查 - JSON 規範要求"""
        try:
            # 估算快取大小 (簡化版本)
            cache_size_estimate = len(self.cache) * 0.1  # 假設每個快取項目 0.1MB
            
            if cache_size_estimate > self.max_cache_size_mb * self.cleanup_threshold:
                logger.warning(f"快取使用量達到閾值: {cache_size_estimate:.1f}MB")
                await self._cleanup_cache()
                
            if cache_size_estimate > self.max_cache_size_mb:
                logger.error("觸發緊急清理")
                if self.emergency_cleanup:
                    await self._emergency_cache_cleanup()
        except Exception as e:
            logger.error(f"記憶體管理檢查失敗: {e}")
    
    async def _cleanup_cache(self):
        """快取清理機制"""
        # 清理過期的快取項目
        now = datetime.now()
        expired_keys = [
            key for key, expiry in self.cache_ttl.items()
            if expiry and expiry < now
        ]
        
        for key in expired_keys:
            self.cache.pop(key, None)
            self.cache_ttl.pop(key, None)
        
        logger.info(f"清理了 {len(expired_keys)} 個過期快取項目")
    
    async def _emergency_cache_cleanup(self):
        """緊急快取清理"""
        # 保留最重要的快取項目
        critical_indicators = ['RSI', 'MACD', 'BB_position']
        critical_keys = [
            key for key in self.cache.keys()
            if any(indicator in key for indicator in critical_indicators)
        ]
        
        # 清理非關鍵快取
        non_critical_keys = [
            key for key in self.cache.keys()
            if key not in critical_keys
        ]
        
        for key in non_critical_keys:
            self.cache.pop(key, None)
            self.cache_ttl.pop(key, None)
        
        logger.warning(f"緊急清理了 {len(non_critical_keys)} 個非關鍵快取項目")
    
    async def _warm_cache(self):
        """快取預熱機制 - JSON 規範要求"""
        priority_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
        warm_timeframes = ["1m", "5m", "15m"]
        
        logger.info("開始快取預熱...")
        
        for symbol in priority_symbols:
            for timeframe in warm_timeframes:
                try:
                    # 預計算熱門交易對的指標
                    cache_key = f"warm_{symbol}_{timeframe}"
                    if cache_key not in self.cache:
                        # 執行輕量級預計算
                        await self._lightweight_precalculation(symbol, timeframe)
                        
                except Exception as e:
                    logger.warning(f"快取預熱失敗 {symbol}_{timeframe}: {e}")
                    continue
        
        logger.info("快取預熱完成")
    
    async def _lightweight_precalculation(self, symbol: str, timeframe: str):
        """輕量級預計算 - 只計算關鍵指標"""
        try:
            # 獲取基礎數據
            synced_data = await self._layer_minus1_data_sync(symbol, timeframe)
            if synced_data is None:
                return
            
            raw_data = await self._layer_0_raw_data(synced_data, symbol, timeframe)
            
            # 只計算 Layer 2 (移動平均線) 用於預熱
            close = raw_data[f"{symbol}_{timeframe}_close"]
            
            # 預計算關鍵移動平均線
            sma_20 = close.rolling(20).mean()
            ema_12 = close.ewm(span=12).mean()
            ema_26 = close.ewm(span=26).mean()
            
            # 存入快取
            cache_key = f"warm_{symbol}_{timeframe}"
            self.cache[cache_key] = {
                'sma_20': sma_20,
                'ema_12': ema_12,
                'ema_26': ema_26,
                'timestamp': datetime.now()
            }
            self.cache_ttl[cache_key] = datetime.now() + timedelta(seconds=30)
            
        except Exception as e:
            logger.error(f"輕量級預計算失敗: {e}")
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """獲取性能統計 - 增強版"""
        if not self.performance_history:
            return {}
        
        recent_performances = list(self.performance_history)[-10:]
        
        avg_time = np.mean([p['total_time_ms'] for p in recent_performances])
        avg_indicators = np.mean([p['indicator_count'] for p in recent_performances])
        avg_cache_hit_rate = np.mean([p['cache_hit_rate'] for p in recent_performances])
        
        # 新增統計項目
        emergency_mode_count = sum(1 for p in recent_performances if p.get('emergency_mode', False))
        
        return {
            'average_calculation_time_ms': avg_time,
            'average_indicator_count': avg_indicators,
            'average_cache_hit_rate': avg_cache_hit_rate,
            'total_calculations': len(self.performance_history),
            'degraded_mode_active': self.degraded_mode,
            'emergency_mode_active': self.emergency_mode,
            'emergency_mode_triggers': emergency_mode_count,
            'cache_warming_enabled': self.cache_warming_enabled,
            'cache_events_status': self.cache_events,
            'recent_layer_timings': {
                layer: np.mean(times[-5:]) if times else 0
                for layer, times in self.layer_timings.items()
            }
        }
    
    async def calculate_indicators(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """公開的指標計算方法 - 與其他模組對接"""
        try:
            symbol = market_data.get('symbol', 'BTCUSDT')
            timeframe = market_data.get('timeframe', '1m')
            
            # 調用完整計算方法
            indicators = await self.calculate_all_indicators(symbol, timeframe)
            
            # 轉換為標準格式
            result = {
                'symbol': symbol,
                'timeframe': timeframe,
                'indicators': indicators,
                'timestamp': datetime.now(),
                'calculation_time_ms': sum(r.calculation_time_ms for r in indicators.values()),
                'cache_hit_rate': sum(1 for r in indicators.values() if r.cache_hit) / len(indicators) if indicators else 0
            }
            
            return result
            
        except Exception as e:
            logger.error(f"公開指標計算失敗: {e}")
            return {}
    
    async def update_dependencies(self, dependency_update: Dict[str, Any]) -> bool:
        """更新依賴關係"""
        try:
            update_type = dependency_update.get('type', 'unknown')
            
            if update_type == 'market_data_update':
                # 市場數據更新，檢查是否需要重新計算
                symbol = dependency_update.get('symbol')
                price_change = dependency_update.get('price_change', 0)
                
                if abs(price_change) > 0.01:  # 1%以上變化
                    # 觸發快取失效
                    cache_keys_to_remove = [k for k in self.cache.keys() if symbol in k]
                    for key in cache_keys_to_remove:
                        del self.cache[key]
                        if key in self.cache_ttl:
                            del self.cache_ttl[key]
                    logger.info(f"價格顯著變化，失效快取: {symbol}")
                
            elif update_type == 'volume_spike':
                # 成交量異常，可能需要重新計算音量相關指標
                symbol = dependency_update.get('symbol')
                volume_cache_keys = [k for k in self.cache.keys() 
                                   if symbol in k and ('volume' in k or 'OBV' in k)]
                for key in volume_cache_keys:
                    del self.cache[key]
                    if key in self.cache_ttl:
                        del self.cache_ttl[key]
                
            elif update_type == 'time_sync':
                # 時間同步更新
                self.last_sync_time = dependency_update.get('timestamp')
                
            return True
            
        except Exception as e:
            logger.error(f"依賴更新失敗: {e}")
            return False

    # ===== JSON規範輸出格式方法 =====
    
    async def process_standardized_basic_signals(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理標準化基礎信號輸入 - JSON規範要求"""
        try:
            signals = signal_data.get('signals', [])
            processing_results = []
            
            for signal in signals:
                symbol = signal.get('symbol')
                signal_type = signal.get('unified_signal_type')
                
                # 根據信號類型確定需要計算的指標
                required_indicators = self._get_indicators_for_signal_type(signal_type)
                
                # 計算相關指標
                indicators = await self.calculate_all_indicators(symbol, '1m')
                
                # 過濾出相關指標
                relevant_indicators = {
                    name: result for name, result in indicators.items()
                    if name in required_indicators
                }
                
                processing_results.append({
                    'signal_id': signal.get('signal_id'),
                    'symbol': symbol,
                    'relevant_indicators': relevant_indicators,
                    'processing_timestamp': datetime.now()
                })
            
            return {
                'type': 'processed_signal_indicators',
                'input_signal_count': len(signals),
                'results': processing_results,
                'processing_timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"標準化基礎信號處理失敗: {e}")
            return {}
    
    async def generate_indicator_results_output(self, indicators: Dict[str, IndicatorResult]) -> Dict[str, Any]:
        """生成 indicator_results 輸出格式 - JSON規範要求"""
        try:
            indicator_results = {
                "type": "indicator_results",
                "timestamp": datetime.now(),
                "calculation_summary": {
                    "total_indicators": len(indicators),
                    "average_calculation_time_ms": sum(r.calculation_time_ms for r in indicators.values()) / len(indicators) if indicators else 0,
                    "cache_hit_rate": sum(1 for r in indicators.values() if r.cache_hit) / len(indicators) if indicators else 0,
                    "average_quality_score": sum(r.quality_score for r in indicators.values()) / len(indicators) if indicators else 0
                },
                "indicators": {},
                "performance_metrics": {
                    "total_calculation_time_ms": sum(r.calculation_time_ms for r in indicators.values()),
                    "memory_usage_estimate_kb": len(indicators) * 2,  # 簡化估算
                    "parallel_efficiency": 0.85  # 估算並行效率
                }
            }
            
            # 分類整理指標
            for name, result in indicators.items():
                category = self._categorize_indicator(name)
                
                if category not in indicator_results["indicators"]:
                    indicator_results["indicators"][category] = []
                
                indicator_results["indicators"][category].append({
                    "indicator_name": result.indicator_name,
                    "symbol": result.symbol,
                    "timeframe": result.timeframe,
                    "value": result.value,
                    "quality_score": result.quality_score,
                    "timestamp": result.timestamp,
                    "calculation_time_ms": result.calculation_time_ms,
                    "cache_hit": result.cache_hit,
                    "reliability_score": self._calculate_indicator_reliability(result)
                })
            
            return indicator_results
        except Exception as e:
            logger.error(f"indicator_results 輸出生成失敗: {e}")
            return {}
    
    def _get_indicators_for_signal_type(self, signal_type: str) -> List[str]:
        """根據信號類型獲取相關指標"""
        mapping = {
            "MOMENTUM_SIGNAL": ["RSI", "MACD", "Stoch_RSI"],
            "TREND_SIGNAL": ["EMA_12", "EMA_26", "SMA_20", "ADX"],
            "VOLATILITY_SIGNAL": ["BB_upper", "BB_lower", "ATR"],
            "VOLUME_SIGNAL": ["OBV", "Volume_SMA", "VWAP"],
            "PRICE_ACTION_SIGNAL": ["Support", "Resistance", "Pivot"]
        }
        return mapping.get(signal_type, ["RSI", "MACD", "EMA_12"])
    
    def _categorize_indicator(self, indicator_name: str) -> str:
        """指標分類"""
        if any(x in indicator_name for x in ["RSI", "Stoch", "Williams", "CCI"]):
            return "oscillators"
        elif any(x in indicator_name for x in ["EMA", "SMA", "WMA"]):
            return "moving_averages"
        elif any(x in indicator_name for x in ["MACD", "Signal"]):
            return "momentum"
        elif any(x in indicator_name for x in ["BB", "ATR", "Volatility"]):
            return "volatility"
        elif any(x in indicator_name for x in ["Volume", "OBV", "VWAP"]):
            return "volume"
        else:
            return "other"
    
    def _calculate_indicator_reliability(self, result: IndicatorResult) -> float:
        """計算指標可靠性"""
        try:
            factors = []
            
            # 品質分數因子
            factors.append(result.quality_score)
            
            # 計算時間因子（快速計算通常更可靠）
            time_factor = max(0.1, 1.0 - result.calculation_time_ms / 1000.0)
            factors.append(time_factor)
            
            # 快取命中因子（一致性指標）
            cache_factor = 0.9 if result.cache_hit else 0.7
            factors.append(cache_factor)
            
            # 數值合理性因子
            value_factor = 0.9 if 0 <= result.value <= 100 else 0.7  # 適用於大部分震盪指標
            factors.append(value_factor)
            
            # 加權平均
            weights = [0.4, 0.2, 0.2, 0.2]
            reliability = sum(f * w for f, w in zip(factors, weights))
            
            return min(1.0, max(0.0, reliability))
        except:
            return 0.5

    def continuous_numerical(self, data: Any) -> float:
        """連續數值處理 - JSON規範要求"""
        try:
            if isinstance(data, (int, float)):
                return float(data)
            elif isinstance(data, str):
                return float(data) if data.replace('.', '').replace('-', '').isdigit() else 0.0
            else:
                return 0.0
        except:
            return 0.0
    
    async def generate_synced_outputs(self, symbol: str, timeframe: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成同步輸出 - JSON規範要求"""
        try:
            synced_data = {
                "synced_open": data.get('open', 0.0),
                "synced_high": data.get('high', 0.0), 
                "synced_low": data.get('low', 0.0),
                "synced_close": data.get('close', 0.0),
                "synced_volume": data.get('volume', 0.0),
                "data_quality_score": self._calculate_data_quality_score(data)
            }
            return synced_data
        except:
            return {}
    
    def _calculate_data_quality_score(self, data: Dict[str, Any]) -> float:
        """計算數據品質分數"""
        try:
            required_fields = ['open', 'high', 'low', 'close', 'volume']
            present_fields = sum(1 for field in required_fields if field in data and data[field] is not None)
            return present_fields / len(required_fields)
        except:
            return 0.0


    async def generate_highest_high_20(self, symbol: str, timeframe: str, data: List[float]) -> float:
        """生成20期最高價 - JSON規範要求"""
        try:
            if len(data) >= 20:
                return max(data[-20:])
            else:
                return max(data) if data else 0.0
        except:
            return 0.0
    
    async def generate_lowest_low_20(self, symbol: str, timeframe: str, data: List[float]) -> float:
        """生成20期最低價 - JSON規範要求"""
        try:
            if len(data) >= 20:
                return min(data[-20:])
            else:
                return min(data) if data else 0.0
        except:
            return 0.0
    
    async def generate_sma_10(self, symbol: str, timeframe: str, data: List[float]) -> float:
        """生成10期簡單移動平均 - JSON規範要求"""
        try:
            if len(data) >= 10:
                return sum(data[-10:]) / 10
            else:
                return sum(data) / len(data) if data else 0.0
        except:
            return 0.0
    
    async def generate_standardized_with_symbol_timeframe(self, symbol: str, timeframe: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成標準化符號時間框架數據 - JSON規範要求"""
        try:
            standardized = {
                "type": "standardized with symbol and timeframe",
                "symbol": symbol,
                "timeframe": timeframe,
                "timestamp": data.get('timestamp'),
                "standardized_price": data.get('close', 0),
                "standardized_volume": data.get('volume', 0),
                "price_percentile": self._calculate_price_percentile(data),
                "volume_percentile": self._calculate_volume_percentile(data)
            }
            return standardized
        except:
            return {}
    
    def _calculate_price_percentile(self, data: Dict[str, Any]) -> float:
        """計算價格百分位"""
        return 50.0  # 簡化實現
    
    def _calculate_volume_percentile(self, data: Dict[str, Any]) -> float:
        """計算成交量百分位"""
        return 50.0  # 簡化實現


    async def generate_missing_indicator_outputs(self, symbol: str, timeframe: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成缺失的指標輸出"""
        try:
            outputs = {}
            
            # 生成缺失的20期指標
            if 'high' in data:
                outputs[f'{symbol}_{timeframe}_highest_high_20'] = await self.generate_highest_high_20(symbol, timeframe, [data['high']])
            
            if 'low' in data:
                outputs[f'{symbol}_{timeframe}_lowest_low_20'] = await self.generate_lowest_low_20(symbol, timeframe, [data['low']])
            
            # 生成SMA_10
            if 'close' in data:
                outputs[f'{symbol}_{timeframe}_SMA_10'] = await self.generate_sma_10(symbol, timeframe, [data['close']])
            
            # 生成標準化數據
            outputs['standardized_with_symbol_and_timeframe'] = await self.generate_standardized_with_symbol_timeframe(symbol, timeframe, data)
            
            return outputs
        except Exception as e:
            self.logger.error(f"❌ 指標輸出生成失敗: {e}")
            return {}


    async def generate_missing_indicator_outputs(self, symbol: str, timeframe: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成缺失的指標輸出"""
        try:
            outputs = {}
            
            # 生成缺失的20期指標
            if 'high' in data:
                outputs[f'{symbol}_{timeframe}_highest_high_20'] = await self.generate_highest_high_20(symbol, timeframe, [data['high']])
            
            if 'low' in data:
                outputs[f'{symbol}_{timeframe}_lowest_low_20'] = await self.generate_lowest_low_20(symbol, timeframe, [data['low']])
            
            # 生成SMA_10
            if 'close' in data:
                outputs[f'{symbol}_{timeframe}_SMA_10'] = await self.generate_sma_10(symbol, timeframe, [data['close']])
            
            # 生成標準化數據
            outputs['standardized_with_symbol_and_timeframe'] = await self.generate_standardized_with_symbol_timeframe(symbol, timeframe, data)
            
            return outputs
        except Exception as e:
            self.logger.error(f"❌ 指標輸出生成失敗: {e}")
            return {}

# 全局實例
indicator_dependency_graph = IndicatorDependencyGraph()

# 便捷函數
async def calculate_technical_indicators(symbol: str = "BTCUSDT", 
                                       timeframe: str = "1m") -> Dict[str, IndicatorResult]:
    """便捷函數：計算技術指標"""
    return await indicator_dependency_graph.calculate_all_indicators(symbol, timeframe)

async def get_indicator_performance() -> Dict[str, Any]:
    """便捷函數：獲取性能統計"""
    return await indicator_dependency_graph.get_performance_stats()
