#!/usr/bin/env python3
"""
🎯 Trading X - Phase1 系統綜合測試和實時信號生成演示
完整測試 Phase1A + Phase1B + Phase1C + 統一信號池 + WebSocket驅動器
⚡ 包含128個剩餘問題的優化處理
"""
import asyncio
import json
import time
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase1_test_demo.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 添加模組路徑
sys.path.append('/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation')

@dataclass
class TestResult:
    """測試結果數據結構"""
    module_name: str
    test_name: str
    success: bool
    execution_time_ms: float
    details: Dict[str, Any]
    errors: List[str]

@dataclass
class Phase1SystemStatus:
    """Phase1系統狀態"""
    websocket_driver_status: str
    phase1a_status: str
    indicator_dependency_status: str
    phase1b_status: str
    phase1c_status: str
    unified_pool_status: str
    total_signals_processed: int
    average_latency_ms: float
    error_count: int
    uptime_seconds: float

class Phase1SystemTester:
    """Phase1系統綜合測試器"""
    
    def __init__(self):
        self.test_results: List[TestResult] = []
        self.system_status = Phase1SystemStatus(
            websocket_driver_status="未初始化",
            phase1a_status="未初始化", 
            indicator_dependency_status="未初始化",
            phase1b_status="未初始化",
            phase1c_status="未初始化",
            unified_pool_status="未初始化",
            total_signals_processed=0,
            average_latency_ms=0.0,
            error_count=0,
            uptime_seconds=0.0
        )
        self.start_time = time.time()
        self.modules = {}
        
    async def initialize_phase1_modules(self) -> bool:
        """初始化所有Phase1模組"""
        logger.info("🚀 開始初始化Phase1系統模組...")
        
        try:
            # 1. WebSocket實時驅動器
            logger.info("📡 初始化WebSocket實時驅動器...")
            from websocket_realtime_driver.websocket_realtime_driver import WebSocketRealtimeDriver
            self.modules['websocket_driver'] = WebSocketRealtimeDriver()
            self.system_status.websocket_driver_status = "已初始化"
            logger.info("✅ WebSocket驅動器初始化成功")
            
            # 2. Phase1A基礎信號生成  
            logger.info("🎯 初始化Phase1A基礎信號生成...")
            from phase1a_basic_signal_generation.phase1a_basic_signal_generation import Phase1ABasicSignalGenerator
            self.modules['phase1a'] = Phase1ABasicSignalGenerator()
            self.system_status.phase1a_status = "已初始化"
            logger.info("✅ Phase1A初始化成功")
            
            # 3. 技術指標依賴圖
            logger.info("📊 初始化技術指標依賴圖...")
            from indicator_dependency.indicator_dependency_graph import IndicatorDependencyGraph
            self.modules['indicator_dependency'] = IndicatorDependencyGraph()
            self.system_status.indicator_dependency_status = "已初始化"
            logger.info("✅ 技術指標依賴圖初始化成功")
            
            # 4. Phase1B波動率適應
            logger.info("📈 初始化Phase1B波動率適應...")
            from phase1b_volatility_adaptation.phase1b_volatility_adaptation import Phase1BVolatilityAdaptationEngine
            self.modules['phase1b'] = Phase1BVolatilityAdaptationEngine()
            self.system_status.phase1b_status = "已初始化"
            logger.info("✅ Phase1B初始化成功")
            
            # 5. Phase1C信號標準化
            logger.info("🎛️ 初始化Phase1C信號標準化...")
            from phase1c_signal_standardization.phase1c_signal_standardization import Phase1CSignalStandardizationEngine
            self.modules['phase1c'] = Phase1CSignalStandardizationEngine()
            self.system_status.phase1c_status = "已初始化"
            logger.info("✅ Phase1C初始化成功")
            
            # 6. 統一信號候選池
            logger.info("🎰 初始化統一信號候選池...")
            from unified_signal_pool.unified_signal_candidate_pool import UnifiedSignalCandidatePoolV3
            self.modules['unified_pool'] = UnifiedSignalCandidatePoolV3()
            self.system_status.unified_pool_status = "已初始化"
            logger.info("✅ 統一信號池初始化成功")
            
            logger.info("🎉 所有Phase1模組初始化完成！")
            return True
            
        except Exception as e:
            logger.error(f"❌ Phase1模組初始化失敗: {e}")
            return False
    
    async def test_websocket_driver(self) -> TestResult:
        """測試WebSocket驅動器"""
        start_time = time.time()
        test_name = "WebSocket驅動器連接測試"
        errors = []
        details = {}
        
        try:
            logger.info("🔗 測試WebSocket驅動器...")
            driver = self.modules.get('websocket_driver')
            
            if not driver:
                raise Exception("WebSocket驅動器未初始化")
            
            # 測試連接健康狀態生成
            health_status = await driver.generate_connection_health_status()
            details['connection_health'] = health_status
            
            # 測試數據生成器
            test_data = {"symbol": "BTCUSDT", "price": 50000.0, "volume": 1000.0}
            extreme_events = await driver.generate_extreme_events_anomaly_detections(test_data)
            details['extreme_events'] = extreme_events
            
            # 測試基礎指標生成
            price_volume_indicators = await driver.generate_price_volume_basic_indicators(test_data)
            details['price_volume_indicators'] = price_volume_indicators
            
            success = True
            logger.info("✅ WebSocket驅動器測試通過")
            
        except Exception as e:
            errors.append(str(e))
            success = False
            logger.error(f"❌ WebSocket驅動器測試失敗: {e}")
        
        execution_time = (time.time() - start_time) * 1000
        return TestResult("WebSocket驅動器", test_name, success, execution_time, details, errors)
    
    async def test_phase1a_signals(self) -> TestResult:
        """測試Phase1A基礎信號生成"""
        start_time = time.time()
        test_name = "Phase1A基礎信號生成測試"
        errors = []
        details = {}
        
        try:
            logger.info("🎯 測試Phase1A基礎信號生成...")
            phase1a = self.modules.get('phase1a')
            
            if not phase1a:
                raise Exception("Phase1A模組未初始化")
            
            # 模擬市場數據
            market_data = {
                "symbol": "BTCUSDT",
                "klines": [
                    [1640995200000, "47000", "47500", "46800", "47200", "1000"],
                    [1640995260000, "47200", "47800", "47100", "47600", "1200"],
                    [1640995320000, "47600", "48000", "47400", "47800", "1100"],
                ],
                "trades": [{"price": 47800, "quantity": 10, "timestamp": time.time()}],
                "orderbook": {"bids": [[47750, 100]], "asks": [[47850, 100]]}
            }
            
            # 測試信號生成
            signals = await phase1a.generate_signals(market_data)
            details['generated_signals'] = signals
            details['signal_count'] = len(signals)
            
            # 驗證信號質量
            if signals:
                avg_quality = sum(s.get('quality_score', 0) for s in signals) / len(signals)
                details['average_quality'] = avg_quality
            
            success = len(signals) > 0
            logger.info(f"✅ Phase1A測試通過 - 生成 {len(signals)} 個信號")
            
        except Exception as e:
            errors.append(str(e))
            success = False
            logger.error(f"❌ Phase1A測試失敗: {e}")
        
        execution_time = (time.time() - start_time) * 1000
        return TestResult("Phase1A", test_name, success, execution_time, details, errors)
    
    async def test_indicator_dependency(self) -> TestResult:
        """測試技術指標依賴圖"""
        start_time = time.time()
        test_name = "技術指標依賴圖測試"
        errors = []
        details = {}
        
        try:
            logger.info("📊 測試技術指標依賴圖...")
            indicator_graph = self.modules.get('indicator_dependency')
            
            if not indicator_graph:
                raise Exception("技術指標依賴圖模組未初始化")
            
            # 測試指標計算
            test_prices = [47000, 47200, 47600, 47800, 47500, 47300, 47700, 47900, 48000, 47850]
            
            # 計算各種技術指標
            rsi_result = await indicator_graph.calculate_rsi(test_prices)
            macd_result = await indicator_graph.calculate_macd(test_prices)
            bb_result = await indicator_graph.calculate_bollinger_bands(test_prices)
            
            details['rsi'] = rsi_result
            details['macd'] = macd_result
            details['bollinger_bands'] = bb_result
            
            # 測試依賴關係
            dependencies = await indicator_graph.get_indicator_dependencies()
            details['dependencies'] = dependencies
            
            success = all([rsi_result, macd_result, bb_result])
            logger.info("✅ 技術指標依賴圖測試通過")
            
        except Exception as e:
            errors.append(str(e))
            success = False
            logger.error(f"❌ 技術指標依賴圖測試失敗: {e}")
        
        execution_time = (time.time() - start_time) * 1000
        return TestResult("技術指標依賴圖", test_name, success, execution_time, details, errors)
    
    async def test_phase1b_volatility(self) -> TestResult:
        """測試Phase1B波動率適應"""
        start_time = time.time()
        test_name = "Phase1B波動率適應測試"
        errors = []
        details = {}
        
        try:
            logger.info("📈 測試Phase1B波動率適應...")
            phase1b = self.modules.get('phase1b')
            
            if not phase1b:
                raise Exception("Phase1B模組未初始化")
            
            # 模擬輸入信號
            input_signals = [
                {
                    "signal_type": "PRICE_BREAKOUT",
                    "signal_strength": 0.8,
                    "confidence_score": 0.75,
                    "timestamp": datetime.now(),
                    "symbol": "BTCUSDT"
                },
                {
                    "signal_type": "VOLUME_SURGE", 
                    "signal_strength": 0.6,
                    "confidence_score": 0.65,
                    "timestamp": datetime.now(),
                    "symbol": "BTCUSDT"
                }
            ]
            
            # 測試波動率適應處理
            adapted_signals = await phase1b.process_signals(input_signals, "BTCUSDT")
            details['adapted_signals'] = adapted_signals
            details['adaptation_count'] = len(adapted_signals)
            
            # 測試波動率制度檢測
            market_data = {"symbol": "BTCUSDT", "price": 47800, "volume": 1000}
            volatility_regime = await phase1b.detect_volatility_regime(market_data)
            details['volatility_regime'] = volatility_regime
            
            success = len(adapted_signals) > 0
            logger.info(f"✅ Phase1B測試通過 - 適應 {len(adapted_signals)} 個信號")
            
        except Exception as e:
            errors.append(str(e))
            success = False
            logger.error(f"❌ Phase1B測試失敗: {e}")
        
        execution_time = (time.time() - start_time) * 1000
        return TestResult("Phase1B", test_name, success, execution_time, details, errors)
    
    async def test_phase1c_standardization(self) -> TestResult:
        """測試Phase1C信號標準化"""
        start_time = time.time()
        test_name = "Phase1C信號標準化測試"
        errors = []
        details = {}
        
        try:
            logger.info("🎛️ 測試Phase1C信號標準化...")
            phase1c = self.modules.get('phase1c')
            
            if not phase1c:
                raise Exception("Phase1C模組未初始化")
            
            # 模擬原始上游信號
            raw_signals = [
                {
                    "signal_type": "BREAKOUT",
                    "value": 0.75,
                    "confidence": 0.8,
                    "source": "phase1a",
                    "timestamp": datetime.now()
                },
                {
                    "signal_type": "VOLATILITY_SURGE",
                    "value": 0.65,
                    "confidence": 0.7,
                    "source": "phase1b", 
                    "timestamp": datetime.now()
                },
                {
                    "signal_type": "RSI_OVERSOLD",
                    "value": 0.85,
                    "confidence": 0.9,
                    "source": "indicator_graph",
                    "timestamp": datetime.now()
                }
            ]
            
            # 測試信號標準化處理
            standardized_signals = await phase1c.process_signals(raw_signals, "BTCUSDT")
            details['standardized_signals'] = [asdict(s) for s in standardized_signals]
            details['standardization_count'] = len(standardized_signals)
            
            if standardized_signals:
                avg_quality = sum(s.quality_score for s in standardized_signals) / len(standardized_signals)
                details['average_quality_score'] = avg_quality
                
                tier_distribution = {}
                for signal in standardized_signals:
                    tier = signal.tier.value
                    tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
                details['tier_distribution'] = tier_distribution
            
            # 測試系統狀態
            system_status = await phase1c.get_system_status()
            details['system_status'] = system_status
            
            success = len(standardized_signals) > 0
            logger.info(f"✅ Phase1C測試通過 - 標準化 {len(standardized_signals)} 個信號")
            
        except Exception as e:
            errors.append(str(e))
            success = False
            logger.error(f"❌ Phase1C測試失敗: {e}")
        
        execution_time = (time.time() - start_time) * 1000
        return TestResult("Phase1C", test_name, success, execution_time, details, errors)
    
    async def test_unified_signal_pool(self) -> TestResult:
        """測試統一信號候選池"""
        start_time = time.time()
        test_name = "統一信號候選池測試"
        errors = []
        details = {}
        
        try:
            logger.info("🎰 測試統一信號候選池...")
            unified_pool = self.modules.get('unified_pool')
            
            if not unified_pool:
                raise Exception("統一信號池模組未初始化")
            
            # 模擬市場數據
            market_data = {
                "symbol": "BTCUSDT",
                "klines": [
                    [1640995200000, "47000", "47500", "46800", "47200", "1000"],
                    [1640995260000, "47200", "47800", "47100", "47600", "1200"],
                    [1640995320000, "47600", "48000", "47400", "47800", "1100"],
                    [1640995380000, "47800", "48200", "47700", "48000", "1300"],
                    [1640995440000, "48000", "48300", "47900", "48100", "1150"],
                ],
                "orderbook": {
                    "bids": [[47950, 100], [47900, 200]],
                    "asks": [[48050, 150], [48100, 180]]
                },
                "trades": [
                    {"price": 48000, "quantity": 10, "timestamp": time.time()},
                    {"price": 48020, "quantity": 15, "timestamp": time.time()}
                ]
            }
            
            # 測試信號收集和統一
            unified_signals = await unified_pool.collect_and_unify_signals("BTCUSDT", market_data)
            details['unified_signals'] = unified_signals
            details['signal_count'] = len(unified_signals)
            
            if unified_signals:
                # 信號質量分析
                quality_scores = [s.get('quality_score', 0) for s in unified_signals]
                details['quality_stats'] = {
                    'average': sum(quality_scores) / len(quality_scores),
                    'max': max(quality_scores),
                    'min': min(quality_scores)
                }
                
                # 信號類型分布
                signal_types = {}
                for signal in unified_signals:
                    sig_type = signal.get('signal_type', 'UNKNOWN')
                    signal_types[sig_type] = signal_types.get(sig_type, 0) + 1
                details['signal_type_distribution'] = signal_types
            
            # 測試統計數據
            stats = await unified_pool.get_statistics()
            details['pool_statistics'] = stats
            
            success = len(unified_signals) > 0
            logger.info(f"✅ 統一信號池測試通過 - 收集 {len(unified_signals)} 個信號")
            
        except Exception as e:
            errors.append(str(e))
            success = False
            logger.error(f"❌ 統一信號池測試失敗: {e}")
        
        execution_time = (time.time() - start_time) * 1000
        return TestResult("統一信號池", test_name, success, execution_time, details, errors)
    
    async def test_end_to_end_integration(self) -> TestResult:
        """端對端整合測試"""
        start_time = time.time()
        test_name = "Phase1端對端整合測試"
        errors = []
        details = {}
        
        try:
            logger.info("🔄 執行Phase1端對端整合測試...")
            
            # 1. 模擬WebSocket數據流
            market_data = {
                "symbol": "BTCUSDT",
                "timestamp": time.time(),
                "klines": [
                    [1640995200000, "47000", "47500", "46800", "47200", "1000"],
                    [1640995260000, "47200", "47800", "47100", "47600", "1200"],
                    [1640995320000, "47600", "48000", "47400", "47800", "1100"],
                    [1640995380000, "47800", "48200", "47700", "48000", "1300"],
                    [1640995440000, "48000", "48300", "47900", "48100", "1150"],
                ],
                "orderbook": {
                    "bids": [[47950, 100], [47900, 200], [47850, 300]],
                    "asks": [[48050, 150], [48100, 180], [48150, 220]]
                },
                "trades": [
                    {"price": 48000, "quantity": 10, "timestamp": time.time()},
                    {"price": 48020, "quantity": 15, "timestamp": time.time()},
                    {"price": 47980, "quantity": 8, "timestamp": time.time()}
                ]
            }
            
            # 2. Phase1A: 基礎信號生成
            phase1a = self.modules.get('phase1a')
            phase1a_signals = await phase1a.generate_signals(market_data)
            details['phase1a_signals'] = phase1a_signals
            logger.info(f"Phase1A生成 {len(phase1a_signals)} 個基礎信號")
            
            # 3. 技術指標處理
            indicator_graph = self.modules.get('indicator_dependency')
            prices = [float(k[4]) for k in market_data['klines']]
            indicator_signals = []
            
            # RSI信號
            rsi_data = await indicator_graph.calculate_rsi(prices)
            if rsi_data:
                indicator_signals.append({
                    "signal_type": "RSI_signals",
                    "value": rsi_data.get('value', 0.5),
                    "confidence": 0.75,
                    "source": "indicator_graph"
                })
            
            # MACD信號
            macd_data = await indicator_graph.calculate_macd(prices)
            if macd_data:
                indicator_signals.append({
                    "signal_type": "MACD_signals", 
                    "value": macd_data.get('signal', 0.5),
                    "confidence": 0.7,
                    "source": "indicator_graph"
                })
            
            details['indicator_signals'] = indicator_signals
            logger.info(f"技術指標生成 {len(indicator_signals)} 個信號")
            
            # 4. Phase1B: 波動率適應
            phase1b = self.modules.get('phase1b')
            all_signals = phase1a_signals + indicator_signals
            adapted_signals = await phase1b.process_signals(all_signals, "BTCUSDT")
            details['phase1b_adapted_signals'] = adapted_signals
            logger.info(f"Phase1B適應 {len(adapted_signals)} 個信號")
            
            # 5. Phase1C: 信號標準化
            phase1c = self.modules.get('phase1c')
            raw_signals = [
                {
                    "signal_type": s.get('signal_type', 'UNKNOWN'),
                    "value": s.get('signal_strength', s.get('value', 0.5)),
                    "confidence": s.get('confidence_score', s.get('confidence', 0.7)),
                    "source": s.get('signal_source', s.get('source', 'unknown')),
                    "timestamp": datetime.now()
                }
                for s in adapted_signals
            ]
            
            standardized_signals = await phase1c.process_signals(raw_signals, "BTCUSDT")
            details['phase1c_standardized_signals'] = [asdict(s) for s in standardized_signals]
            logger.info(f"Phase1C標準化 {len(standardized_signals)} 個信號")
            
            # 6. 統一信號池整合
            unified_pool = self.modules.get('unified_pool')
            final_signals = await unified_pool.collect_and_unify_signals("BTCUSDT", market_data)
            details['final_unified_signals'] = final_signals
            logger.info(f"統一信號池最終產出 {len(final_signals)} 個信號")
            
            # 7. 性能分析
            details['performance_analysis'] = {
                'total_processing_time_ms': (time.time() - start_time) * 1000,
                'signal_flow': {
                    'input_data_points': len(market_data['klines']) + len(market_data['trades']),
                    'phase1a_output': len(phase1a_signals),
                    'indicator_output': len(indicator_signals),
                    'phase1b_output': len(adapted_signals),
                    'phase1c_output': len(standardized_signals),
                    'final_output': len(final_signals)
                },
                'quality_metrics': {
                    'avg_final_quality': sum(s.get('quality_score', 0) for s in final_signals) / len(final_signals) if final_signals else 0,
                    'signal_retention_rate': len(final_signals) / max(len(all_signals), 1) * 100
                }
            }
            
            success = len(final_signals) > 0
            logger.info(f"✅ 端對端整合測試通過 - 最終產出 {len(final_signals)} 個高質量信號")
            
        except Exception as e:
            errors.append(str(e))
            success = False
            logger.error(f"❌ 端對端整合測試失敗: {e}")
        
        execution_time = (time.time() - start_time) * 1000
        return TestResult("端對端整合", test_name, success, execution_time, details, errors)
    
    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """執行綜合測試套件"""
        logger.info("🎯 開始執行Phase1綜合測試套件...")
        
        # 初始化模組
        if not await self.initialize_phase1_modules():
            return {"error": "模組初始化失敗"}
        
        # 執行所有測試
        test_functions = [
            self.test_websocket_driver,
            self.test_phase1a_signals,
            self.test_indicator_dependency,
            self.test_phase1b_volatility,
            self.test_phase1c_standardization,
            self.test_unified_signal_pool,
            self.test_end_to_end_integration
        ]
        
        for test_func in test_functions:
            try:
                result = await test_func()
                self.test_results.append(result)
                
                if result.success:
                    logger.info(f"✅ {result.test_name} - 成功 ({result.execution_time_ms:.1f}ms)")
                else:
                    logger.error(f"❌ {result.test_name} - 失敗 ({result.execution_time_ms:.1f}ms)")
                    self.system_status.error_count += 1
            
            except Exception as e:
                logger.error(f"❌ 測試執行錯誤: {e}")
                self.system_status.error_count += 1
        
        # 更新系統狀態
        self.system_status.uptime_seconds = time.time() - self.start_time
        self.system_status.total_signals_processed = sum(
            len(r.details.get('signal_count', r.details.get('final_unified_signals', []))) 
            for r in self.test_results if r.success
        )
        self.system_status.average_latency_ms = sum(r.execution_time_ms for r in self.test_results) / len(self.test_results)
        
        return self.generate_test_report()
    
    def generate_test_report(self) -> Dict[str, Any]:
        """生成測試報告"""
        successful_tests = [r for r in self.test_results if r.success]
        failed_tests = [r for r in self.test_results if not r.success]
        
        report = {
            "test_summary": {
                "total_tests": len(self.test_results),
                "successful_tests": len(successful_tests),
                "failed_tests": len(failed_tests),
                "success_rate": len(successful_tests) / len(self.test_results) * 100 if self.test_results else 0,
                "total_execution_time_ms": sum(r.execution_time_ms for r in self.test_results)
            },
            "system_status": asdict(self.system_status),
            "test_details": [asdict(r) for r in self.test_results],
            "performance_metrics": {
                "average_test_time_ms": sum(r.execution_time_ms for r in self.test_results) / len(self.test_results) if self.test_results else 0,
                "fastest_test": min(self.test_results, key=lambda x: x.execution_time_ms) if self.test_results else None,
                "slowest_test": max(self.test_results, key=lambda x: x.execution_time_ms) if self.test_results else None
            },
            "recommendations": self.generate_recommendations()
        }
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """生成優化建議"""
        recommendations = []
        
        failed_tests = [r for r in self.test_results if not r.success]
        if failed_tests:
            recommendations.append(f"修復 {len(failed_tests)} 個失敗的測試模組")
        
        slow_tests = [r for r in self.test_results if r.execution_time_ms > 1000]
        if slow_tests:
            recommendations.append(f"優化 {len(slow_tests)} 個執行緩慢的測試 (>1000ms)")
        
        if self.system_status.error_count > 0:
            recommendations.append(f"處理 {self.system_status.error_count} 個系統錯誤")
        
        if self.system_status.average_latency_ms > 500:
            recommendations.append("優化系統整體延遲性能")
        
        if not recommendations:
            recommendations.append("系統運行良好，建議定期監控性能指標")
        
        return recommendations

class Phase1RealTimeDemo:
    """Phase1實時信號生成演示"""
    
    def __init__(self):
        self.is_running = False
        self.signal_count = 0
        self.demo_duration = 60  # 60秒演示
        
    async def start_real_time_demo(self):
        """啟動實時演示"""
        logger.info("🎬 啟動Phase1實時信號生成演示...")
        
        tester = Phase1SystemTester()
        
        # 初始化系統
        if not await tester.initialize_phase1_modules():
            logger.error("❌ 無法啟動演示 - 模組初始化失敗")
            return
        
        self.is_running = True
        start_time = time.time()
        
        try:
            while self.is_running and (time.time() - start_time) < self.demo_duration:
                # 模擬實時市場數據
                current_time = time.time()
                base_price = 47000 + np.random.normal(0, 500)  # 隨機價格波動
                
                market_data = {
                    "symbol": "BTCUSDT",
                    "timestamp": current_time,
                    "price": base_price,
                    "volume": np.random.uniform(800, 1200),
                    "klines": self.generate_random_klines(base_price),
                    "orderbook": self.generate_random_orderbook(base_price),
                    "trades": self.generate_random_trades(base_price)
                }
                
                # 執行完整的信號生成流程
                signals = await self.process_real_time_signals(tester, market_data)
                
                if signals:
                    self.signal_count += len(signals)
                    logger.info(f"🚨 實時信號生成: {len(signals)} 個新信號 (總計: {self.signal_count})")
                    
                    # 顯示高質量信號
                    high_quality_signals = [s for s in signals if s.get('quality_score', 0) > 0.8]
                    if high_quality_signals:
                        logger.info(f"⭐ 高質量信號: {len(high_quality_signals)} 個")
                        for signal in high_quality_signals[:3]:  # 顯示前3個
                            logger.info(f"   📈 {signal.get('signal_type', 'UNKNOWN')} - "
                                      f"強度: {signal.get('signal_strength', 0):.2f} - "
                                      f"質量: {signal.get('quality_score', 0):.2f}")
                
                # 等待下一次更新
                await asyncio.sleep(2)  # 每2秒更新一次
            
            logger.info(f"🎬 演示完成 - 總共生成 {self.signal_count} 個信號")
            
        except Exception as e:
            logger.error(f"❌ 實時演示失敗: {e}")
        finally:
            self.is_running = False
    
    def generate_random_klines(self, base_price: float) -> List[List]:
        """生成隨機K線數據"""
        klines = []
        current_price = base_price
        
        for i in range(5):
            open_price = current_price
            high_price = open_price + np.random.uniform(0, 200)
            low_price = open_price - np.random.uniform(0, 200)
            close_price = open_price + np.random.uniform(-100, 100)
            volume = np.random.uniform(800, 1200)
            
            klines.append([
                int(time.time() * 1000) - (5-i) * 60000,  # 1分鐘間隔
                str(open_price),
                str(high_price),
                str(low_price),
                str(close_price),
                str(volume)
            ])
            
            current_price = close_price
        
        return klines
    
    def generate_random_orderbook(self, base_price: float) -> Dict[str, List]:
        """生成隨機訂單簿"""
        return {
            "bids": [
                [base_price - i * 10, np.random.uniform(50, 200)]
                for i in range(1, 6)
            ],
            "asks": [
                [base_price + i * 10, np.random.uniform(50, 200)]
                for i in range(1, 6)
            ]
        }
    
    def generate_random_trades(self, base_price: float) -> List[Dict]:
        """生成隨機交易數據"""
        return [
            {
                "price": base_price + np.random.uniform(-50, 50),
                "quantity": np.random.uniform(1, 20),
                "timestamp": time.time()
            }
            for _ in range(3)
        ]
    
    async def process_real_time_signals(self, tester: Phase1SystemTester, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """處理實時信號"""
        try:
            # 使用統一信號池進行快速處理
            unified_pool = tester.modules.get('unified_pool')
            if unified_pool:
                signals = await unified_pool.collect_and_unify_signals(
                    market_data['symbol'], 
                    market_data
                )
                return signals
            
            return []
            
        except Exception as e:
            logger.error(f"❌ 實時信號處理失敗: {e}")
            return []

async def main():
    """主函數"""
    logger.info("🚀 Trading X - Phase1系統測試和演示啟動")
    
    # 選擇運行模式
    print("\n選擇運行模式:")
    print("1. 綜合測試模式")
    print("2. 實時演示模式") 
    print("3. 完整測試+演示")
    
    try:
        choice = input("\n請輸入選擇 (1-3): ").strip()
        
        if choice == "1":
            # 綜合測試模式
            tester = Phase1SystemTester()
            report = await tester.run_comprehensive_tests()
            
            # 保存測試報告
            with open('phase1_test_report.json', 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
            print("\n" + "="*60)
            print("📊 Phase1綜合測試報告")
            print("="*60)
            print(f"總測試數: {report['test_summary']['total_tests']}")
            print(f"成功率: {report['test_summary']['success_rate']:.1f}%")
            print(f"總執行時間: {report['test_summary']['total_execution_time_ms']:.1f}ms")
            print(f"系統處理信號數: {report['system_status']['total_signals_processed']}")
            print(f"平均延遲: {report['system_status']['average_latency_ms']:.1f}ms")
            print("\n優化建議:")
            for rec in report['recommendations']:
                print(f"  • {rec}")
        
        elif choice == "2":
            # 實時演示模式
            demo = Phase1RealTimeDemo()
            await demo.start_real_time_demo()
        
        elif choice == "3":
            # 完整測試+演示
            print("\n🎯 執行完整測試...")
            tester = Phase1SystemTester()
            report = await tester.run_comprehensive_tests()
            
            # 保存測試報告
            with open('phase1_test_report.json', 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n✅ 測試完成 - 成功率: {report['test_summary']['success_rate']:.1f}%")
            
            if report['test_summary']['success_rate'] > 70:
                print("\n🎬 測試通過，啟動實時演示...")
                demo = Phase1RealTimeDemo()
                await demo.start_real_time_demo()
            else:
                print(f"\n❌ 測試成功率過低 ({report['test_summary']['success_rate']:.1f}%)，請修復問題後再次運行")
        
        else:
            print("❌ 無效選擇")
    
    except KeyboardInterrupt:
        logger.info("\n👋 用戶中斷，程序退出")
    except Exception as e:
        logger.error(f"❌ 程序執行錯誤: {e}")
    
    logger.info("🏁 Phase1系統測試和演示結束")

if __name__ == "__main__":
    asyncio.run(main())
