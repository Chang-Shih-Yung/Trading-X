#!/usr/bin/env python3
"""
Phase1A Basic Signal Generation with Dynamic Parameters
整合動態參數系統到 Phase1A 基礎信號生成
嚴格匹配 phase1a_basic_signal_generation.json 配置
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
import sys
import os

# 添加動態參數系統路徑
current_dir = Path(__file__).parent
dynamic_system_path = current_dir.parent / "dynamic_parameter_system"
sys.path.append(str(dynamic_system_path))

from dynamic_parameter_engine import DynamicParameterEngine

@dataclass
class SignalGenerationParams:
    """信號生成參數數據類"""
    price_change_threshold: float
    volume_change_threshold: float
    signal_strength_range: Tuple[float, float]
    confidence_calculation: str
    confidence_threshold: float
    
@dataclass
class ExtremeMarketParams:
    """極端市場模式參數數據類"""
    price_change_threshold: float
    volume_change_threshold: float
    signal_strength_boost: float
    priority_escalation: bool
    confidence_threshold: float
    extreme_mode_multiplier: float

@dataclass
class BasicSignal:
    """基礎信號數據結構"""
    timestamp: datetime
    symbol: str
    signal_type: str
    confidence: float
    price_change: float
    volume_change: float
    signal_strength: float
    market_regime: str
    trading_session: str
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

class Phase1ABasicSignalGenerator:
    """
    Phase1A 基礎信號生成器 - 動態參數整合版本
    嚴格匹配 phase1a_basic_signal_generation.json 配置
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = self._setup_logging()
        self.config_path = config_path or (Path(__file__).parent / "phase1a_basic_signal_generation.json")
        self.config = self._load_configuration()
        
        # 初始化動態參數引擎
        self.dynamic_engine = None
        self._init_dynamic_parameter_system()
        
        # 緩存當前參數
        self._cached_params = {}
        self._cache_timestamp = 0
        self._cache_ttl = 300  # 5分鐘緩存
        
        # 性能監控
        self.performance_metrics = {
            'processing_latency': [],
            'signal_generation_rate': 0,
            'error_rate': 0,
            'total_signals': 0,
            'total_errors': 0
        }
        
        self.logger.info("Phase1A 基礎信號生成器已初始化（動態參數整合版本）")
    
    def _setup_logging(self) -> logging.Logger:
        """設置日誌記錄"""
        logger = logging.getLogger("Phase1A_SignalGenerator")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _load_configuration(self) -> Dict[str, Any]:
        """載入配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.logger.info(f"配置文件載入成功: {self.config_path}")
            return config
        except Exception as e:
            self.logger.error(f"配置文件載入失敗: {e}")
            raise
    
    def _init_dynamic_parameter_system(self):
        """初始化動態參數系統"""
        try:
            # 檢查動態參數整合是否啟用
            integration_config = self.config["phase1a_basic_signal_generation_dependency"]["configuration"]["dynamic_parameter_integration"]
            
            if not integration_config.get("enabled", False):
                self.logger.warning("動態參數系統未啟用，使用靜態參數")
                return
                
            # 初始化動態參數適配器
            config_file = integration_config["config_file"]
            
            # 修復路徑解析
            if config_file.startswith("../"):
                # 相對路徑，從當前文件位置解析
                config_file_path = Path(__file__).parent / config_file
            else:
                # 絕對路徑或當前目錄
                config_file_path = Path(config_file)
            
            # 確保路徑存在
            if not config_file_path.exists():
                self.logger.error(f"動態參數配置文件不存在: {config_file_path}")
                return
                
            self.dynamic_engine = DynamicParameterEngine(str(config_file_path))
            self.logger.info("動態參數系統初始化成功")
            
        except Exception as e:
            self.logger.error(f"動態參數系統初始化失敗: {e}")
            self.logger.warning("將使用靜態參數繼續運行")
    
    async def _get_current_parameters(self, mode: str = "basic_mode") -> Dict[str, Any]:
        """獲取當前動態調整後的參數"""
        current_time = time.time()
        
        # 檢查緩存是否有效
        if (current_time - self._cache_timestamp < self._cache_ttl and 
            mode in self._cached_params):
            return self._cached_params[mode]
        
        # 獲取基礎配置
        signal_params = self.config["phase1a_basic_signal_generation_dependency"]["configuration"]["signal_generation_params"]
        base_params = signal_params[mode].copy()
        
        # 如果動態參數系統可用，進行參數調整
        if self.dynamic_engine:
            try:
                # 獲取動態調整後的參數
                dynamic_result = await self.dynamic_engine.get_dynamic_parameters(
                    phase="phase1_signal_generation"
                )
                
                # 提取 confidence_threshold
                for param_name, param_result in dynamic_result.adapted_parameters.items():
                    if param_name == "confidence_threshold":
                        base_params["confidence_threshold"] = param_result.adapted_value
                        break
                    
                self.logger.debug(f"動態參數調整完成 - {mode}: confidence_threshold = {base_params.get('confidence_threshold', 'N/A')}")
                
            except Exception as e:
                self.logger.error(f"動態參數獲取失敗，使用靜態參數: {e}")
                # 從配置中提取靜態默認值
                confidence_config = base_params.get("confidence_threshold", {})
                if isinstance(confidence_config, dict) and "base_value" in confidence_config:
                    base_params["confidence_threshold"] = confidence_config["base_value"]
                else:
                    base_params["confidence_threshold"] = 0.75  # 默認值
        else:
            # 沒有動態參數系統，使用靜態值
            confidence_config = base_params.get("confidence_threshold", {})
            if isinstance(confidence_config, dict) and "base_value" in confidence_config:
                base_params["confidence_threshold"] = confidence_config["base_value"]
            else:
                base_params["confidence_threshold"] = 0.75  # 默認值
        
        # 更新緩存
        self._cached_params[mode] = base_params
        self._cache_timestamp = current_time
        
        return base_params
    
    async def _create_signal_params(self, mode: str = "basic_mode") -> SignalGenerationParams:
        """創建信號生成參數對象"""
        params = await self._get_current_parameters(mode)
        
        return SignalGenerationParams(
            price_change_threshold=params["price_change_threshold"],
            volume_change_threshold=params["volume_change_threshold"],
            signal_strength_range=tuple(params["signal_strength_range"]),
            confidence_calculation=params["confidence_calculation"],
            confidence_threshold=params["confidence_threshold"]
        )
    
    async def _create_extreme_market_params(self) -> ExtremeMarketParams:
        """創建極端市場模式參數對象"""
        params = await self._get_current_parameters("extreme_market_mode")
        
        return ExtremeMarketParams(
            price_change_threshold=params["price_change_threshold"],
            volume_change_threshold=params["volume_change_threshold"],
            signal_strength_boost=params["signal_strength_boost"],
            priority_escalation=params["priority_escalation"],
            confidence_threshold=params["confidence_threshold"],
            extreme_mode_multiplier=params.get("extreme_mode_multiplier", 1.067)
        )
    
    def _calculate_signal_confidence(self, 
                                   price_change: float, 
                                   volume_change: float,
                                   calculation_method: str) -> float:
        """計算信號信心度"""
        if calculation_method == "basic_statistical_model":
            # 基礎統計模型：價格變化和成交量變化的加權組合
            price_weight = 0.6
            volume_weight = 0.4
            
            # 正規化價格變化（假設最大變化為10%）
            normalized_price = min(abs(price_change) / 0.1, 1.0)
            
            # 正規化成交量變化（假設最大倍數為5）
            normalized_volume = min(volume_change / 5.0, 1.0)
            
            confidence = (normalized_price * price_weight + 
                         normalized_volume * volume_weight)
            
            return min(confidence, 1.0)
        
        else:
            # 未知計算方法，返回默認值
            return 0.5
    
    def _calculate_signal_strength(self, 
                                 confidence: float,
                                 strength_range: Tuple[float, float],
                                 boost: float = 1.0) -> float:
        """計算信號強度"""
        min_strength, max_strength = strength_range
        
        # 基於信心度計算強度
        raw_strength = min_strength + (max_strength - min_strength) * confidence
        
        # 應用增強倍數
        boosted_strength = raw_strength * boost
        
        # 確保在範圍內
        return max(min_strength, min(boosted_strength, max_strength))
    
    async def _get_market_context(self) -> Tuple[str, str]:
        """獲取市場上下文信息"""
        market_regime = "UNKNOWN"
        trading_session = "UNKNOWN"
        
        if self.dynamic_engine:
            try:
                regime_detector = self.dynamic_engine.regime_detector
                session_detector = self.dynamic_engine.session_detector
                
                # 這裡在實際實現中需要真實的價格和成交量數據
                # 目前使用模擬數據
                market_regime = await regime_detector.detect_regime(
                    price_data=[100, 101, 102],  # 模擬價格數據
                    volume_data=[1000, 1100, 1200]  # 模擬成交量數據
                )
                
                trading_session = session_detector.get_current_session()
                
            except Exception as e:
                self.logger.error(f"市場上下文獲取失敗: {e}")
        
        return market_regime, trading_session
    
    async def generate_basic_signal(self, 
                                  symbol: str,
                                  current_price: float,
                                  previous_price: float,
                                  current_volume: float,
                                  previous_volume: float,
                                  is_extreme_market: bool = False) -> Optional[BasicSignal]:
        """
        生成基礎信號
        
        Args:
            symbol: 交易標的
            current_price: 當前價格
            previous_price: 前一個價格
            current_volume: 當前成交量
            previous_volume: 前一個成交量
            is_extreme_market: 是否為極端市場條件
            
        Returns:
            生成的基礎信號或 None
        """
        start_time = time.time()
        
        try:
            # 選擇參數模式
            if is_extreme_market:
                params = await self._create_extreme_market_params()
                mode = "extreme_market_mode"
            else:
                params = await self._create_signal_params("basic_mode")
                mode = "basic_mode"
            
            # 計算價格變化
            price_change = (current_price - previous_price) / previous_price
            
            # 計算成交量變化倍數
            volume_change = current_volume / previous_volume if previous_volume > 0 else 1.0
            
            # 檢查是否滿足基礎門檻
            if (abs(price_change) < params.price_change_threshold or
                volume_change < params.volume_change_threshold):
                return None
            
            # 計算信號信心度
            if is_extreme_market:
                confidence = self._calculate_signal_confidence(
                    price_change, volume_change, "basic_statistical_model"
                )
            else:
                confidence = self._calculate_signal_confidence(
                    price_change, volume_change, params.confidence_calculation
                )
            
            # 檢查信心度門檻
            confidence_threshold = params.confidence_threshold
            if confidence < confidence_threshold:
                return None
            
            # 計算信號強度
            if is_extreme_market:
                signal_strength = self._calculate_signal_strength(
                    confidence, (0.0, 1.0), params.signal_strength_boost
                )
            else:
                signal_strength = self._calculate_signal_strength(
                    confidence, params.signal_strength_range
                )
            
            # 確定信號類型
            signal_type = "BUY" if price_change > 0 else "SELL"
            
            # 獲取市場上下文
            market_regime, trading_session = await self._get_market_context()
            
            # 創建信號
            signal = BasicSignal(
                timestamp=datetime.now(),
                symbol=symbol,
                signal_type=signal_type,
                confidence=confidence,
                price_change=price_change,
                volume_change=volume_change,
                signal_strength=signal_strength,
                market_regime=market_regime,
                trading_session=trading_session
            )
            
            # 記錄性能指標
            processing_time = (time.time() - start_time) * 1000  # 轉換為毫秒
            self.performance_metrics['processing_latency'].append(processing_time)
            self.performance_metrics['total_signals'] += 1
            
            self.logger.debug(f"信號生成成功 - {symbol}: {signal_type}, 信心度: {confidence:.3f}, 強度: {signal_strength:.3f}, 模式: {mode}")
            
            return signal
            
        except Exception as e:
            self.performance_metrics['total_errors'] += 1
            self.logger.error(f"信號生成錯誤 - {symbol}: {e}")
            return None
    
    async def process_websocket_data(self, data: Dict[str, Any]) -> Optional[List[BasicSignal]]:
        """
        處理 WebSocket 數據流
        
        Args:
            data: WebSocket 接收到的數據
            
        Returns:
            生成的信號列表
        """
        try:
            # 解析數據格式（假設標準格式）
            symbol = data.get('symbol')
            price_data = data.get('price_data', [])
            volume_data = data.get('volume_data', [])
            
            if not symbol or len(price_data) < 2 or len(volume_data) < 2:
                return None
            
            # 檢測是否為極端市場條件
            is_extreme_market = self._detect_extreme_market_conditions(price_data, volume_data)
            
            signals = []
            
            # 生成信號（可能有多個時間點的數據）
            for i in range(1, len(price_data)):
                signal = await self.generate_basic_signal(
                    symbol=symbol,
                    current_price=price_data[i],
                    previous_price=price_data[i-1],
                    current_volume=volume_data[i],
                    previous_volume=volume_data[i-1],
                    is_extreme_market=is_extreme_market
                )
                
                if signal:
                    signals.append(signal)
            
            return signals if signals else None
            
        except Exception as e:
            self.logger.error(f"WebSocket 數據處理錯誤: {e}")
            return None
    
    def _detect_extreme_market_conditions(self, price_data: List[float], volume_data: List[float]) -> bool:
        """檢測是否為極端市場條件"""
        if len(price_data) < 2 or len(volume_data) < 2:
            return False
        
        # 檢查價格劇烈波動
        price_changes = []
        for i in range(1, len(price_data)):
            change = abs((price_data[i] - price_data[i-1]) / price_data[i-1])
            price_changes.append(change)
        
        # 檢查成交量大幅增加
        volume_changes = []
        for i in range(1, len(volume_data)):
            if volume_data[i-1] > 0:
                change = volume_data[i] / volume_data[i-1]
                volume_changes.append(change)
        
        # 極端市場條件：價格變化超過1%或成交量增加超過2倍
        extreme_price = any(change > 0.01 for change in price_changes)
        extreme_volume = any(change > 2.0 for change in volume_changes)
        
        return extreme_price or extreme_volume
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """獲取性能指標"""
        latencies = self.performance_metrics['processing_latency']
        
        if latencies:
            # 計算 P99 延遲
            sorted_latencies = sorted(latencies)
            p99_index = int(len(sorted_latencies) * 0.99)
            p99_latency = sorted_latencies[p99_index] if p99_index < len(sorted_latencies) else sorted_latencies[-1]
            
            avg_latency = sum(latencies) / len(latencies)
        else:
            p99_latency = 0
            avg_latency = 0
        
        # 計算錯誤率
        total_operations = self.performance_metrics['total_signals'] + self.performance_metrics['total_errors']
        error_rate = (self.performance_metrics['total_errors'] / total_operations * 100) if total_operations > 0 else 0
        
        return {
            'processing_latency_p99_ms': p99_latency,
            'avg_processing_latency_ms': avg_latency,
            'total_signals_generated': self.performance_metrics['total_signals'],
            'error_rate_percent': error_rate,
            'cache_hit_info': f"TTL: {self._cache_ttl}s, Last Update: {self._cache_timestamp}"
        }
    
    async def cleanup(self):
        """清理資源"""
        if self.dynamic_engine:
            # 動態引擎的清理（如果有的話）
            pass
        
        self.logger.info("Phase1A 基礎信號生成器已清理")

# 示例使用和測試函數
async def example_usage():
    """示例使用"""
    # 初始化生成器
    generator = Phase1ABasicSignalGenerator()
    
    # 模擬 WebSocket 數據 - 使用更大的變化觸發信號
    test_data = {
        'symbol': 'BTCUSDT',
        'price_data': [50000, 50200, 50500, 49500],  # 更大的價格變化
        'volume_data': [1000, 2000, 3000, 2500]     # 更大的成交量變化
    }
    
    print("🚀 Phase1A 基礎信號生成器測試")
    print("=" * 50)
    
    # 顯示當前參數（動態調整後）
    basic_params = await generator._get_current_parameters("basic_mode")
    print(f"📊 當前基礎模式參數:")
    print(f"  價格變化門檻: {basic_params['price_change_threshold']}")
    print(f"  成交量變化門檻: {basic_params['volume_change_threshold']}")
    print(f"  信心度門檻: {basic_params['confidence_threshold']}")
    
    # 檢查動態引擎狀態
    if generator.dynamic_engine:
        dynamic_result = await generator.dynamic_engine.get_dynamic_parameters("phase1_signal_generation")
        print(f"🎯 動態參數結果:")
        print(f"  市場制度: {dynamic_result.market_regime}")
        print(f"  交易時段: {dynamic_result.trading_session}")
        print(f"  適配參數數量: {len(dynamic_result.adapted_parameters)}")
        for param_name, param_result in dynamic_result.adapted_parameters.items():
            print(f"    {param_name}: {param_result.original_value} → {param_result.adapted_value} (因子: {param_result.adaptation_factor:.3f})")
    print()
    
    # 處理數據
    signals = await generator.process_websocket_data(test_data)
    
    if signals:
        print(f"✅ 生成了 {len(signals)} 個信號:")
        for i, signal in enumerate(signals, 1):
            print(f"  信號 {i}: {signal.signal_type} {signal.symbol}")
            print(f"    信心度: {signal.confidence:.3f}")
            print(f"    強度: {signal.signal_strength:.3f}")
            print(f"    價格變化: {signal.price_change:.3%}")
            print(f"    成交量變化: {signal.volume_change:.2f}x")
            print(f"    市場制度: {signal.market_regime}")
            print(f"    交易時段: {signal.trading_session}")
            print()
    else:
        print("❌ 未生成任何信號")
        print("詳細檢查:")
        
        # 檢查每個數據點
        for i in range(1, len(test_data['price_data'])):
            current_price = test_data['price_data'][i]
            previous_price = test_data['price_data'][i-1]
            current_volume = test_data['volume_data'][i]
            previous_volume = test_data['volume_data'][i-1]
            
            price_change = (current_price - previous_price) / previous_price
            volume_change = current_volume / previous_volume
            
            confidence = generator._calculate_signal_confidence(
                price_change, volume_change, "basic_statistical_model"
            )
            
            print(f"  數據點 {i}:")
            print(f"    價格變化: {price_change:.3%} (門檻: {basic_params['price_change_threshold']:.3%})")
            print(f"    成交量變化: {volume_change:.2f}x (門檻: {basic_params['volume_change_threshold']:.2f}x)")
            print(f"    計算信心度: {confidence:.3f} (門檻: {basic_params['confidence_threshold']:.3f})")
            print(f"    通過價格門檻: {abs(price_change) >= basic_params['price_change_threshold']}")
            print(f"    通過成交量門檻: {volume_change >= basic_params['volume_change_threshold']}")
            print(f"    通過信心度門檻: {confidence >= basic_params['confidence_threshold']}")
            print()
    
    # 顯示性能指標
    metrics = generator.get_performance_metrics()
    print("📊 性能指標:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    
    # 測試單個信號生成（更明確的參數）
    print("\n🔬 單個信號測試:")
    single_signal = await generator.generate_basic_signal(
        symbol="BTCUSDT",
        current_price=50500,   # +1% 變化
        previous_price=50000,
        current_volume=3000,   # 3x 成交量增加
        previous_volume=1000,
        is_extreme_market=False
    )
    
    if single_signal:
        print(f"✅ 單個信號生成成功:")
        print(f"  類型: {single_signal.signal_type}")
        print(f"  信心度: {single_signal.confidence:.3f}")
        print(f"  強度: {single_signal.signal_strength:.3f}")
    else:
        print("❌ 單個信號生成失敗")
    
    # 清理
    await generator.cleanup()

if __name__ == "__main__":
    asyncio.run(example_usage())
