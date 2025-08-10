#!/usr/bin/env python3
"""
Phase1信號生成系統綜合測試
測試目標：
1. Phase1A基礎信號生成算法
2. 技術指標計算準確性
3. Phase1B波動率適應機制
4. Phase1C信號標準化流程
5. 統一信號池聚合邏輯
"""

import asyncio
import time
import pytest
import json
import logging
import numpy as np
from datetime import datetime
from typing import Dict, List, Any
from unittest.mock import Mock, patch

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Phase1ComprehensiveTest:
    """Phase1各組件綜合測試"""
    
    def __init__(self):
        self.test_results = {}
        self.performance_metrics = {
            'phase1a_latency': [],
            'phase1b_latency': [],
            'phase1c_latency': [],
            'unified_pool_latency': [],
            'indicator_calculation_latency': []
        }
        
    async def test_phase1a_signal_generation(self) -> Dict[str, Any]:
        """測試Phase1A基礎信號生成算法"""
        logger.info("🔄 測試Phase1A基礎信號生成...")
        
        try:
            # 模擬市場數據
            market_data = {
                "symbol": "BTCUSDT",
                "timestamp": time.time(),
                "klines": [
                    {"open": 45000, "high": 45500, "low": 44800, "close": 45200, "volume": 1500},
                    {"open": 45200, "high": 45800, "low": 45100, "close": 45600, "volume": 1800},
                    {"open": 45600, "high": 46000, "low": 45400, "close": 45800, "volume": 2100}
                ],
                "orderbook": {
                    "bids": [[45750, 100], [45700, 200], [45650, 300]],
                    "asks": [[45850, 150], [45900, 180], [45950, 220]]
                }
            }
            
            start_time = time.time()
            
            # 模擬Phase1A信號生成
            phase1a_signals = await self._simulate_phase1a_generation(market_data)
            
            processing_time = (time.time() - start_time) * 1000
            self.performance_metrics['phase1a_latency'].append(processing_time)
            
            # 驗證信號質量
            signal_quality_checks = await self._validate_phase1a_signals(phase1a_signals)
            
            # 性能檢查
            performance_target = 25.0  # 目標<25ms
            performance_pass = processing_time < performance_target
            
            overall_success = (
                len(phase1a_signals) > 0 and
                signal_quality_checks["all_valid"] and
                performance_pass
            )
            
            result = {
                "test_name": "Phase1A基礎信號生成測試",
                "success": overall_success,
                "processing_time_ms": processing_time,
                "performance_target_ms": performance_target,
                "performance_pass": performance_pass,
                "signals_generated": len(phase1a_signals),
                "signal_quality": signal_quality_checks,
                "generated_signals": phase1a_signals[:3],  # 只保存前3個作為示例
                "status": "✅ PASSED" if overall_success else "❌ FAILED"
            }
            
            logger.info(f"{'✅' if overall_success else '❌'} Phase1A: {len(phase1a_signals)}個信號, {processing_time:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"❌ Phase1A測試失敗: {e}")
            return {
                "test_name": "Phase1A基礎信號生成測試",
                "success": False,
                "error": str(e),
                "status": "❌ ERROR"
            }
    
    async def test_technical_indicator_calculation(self) -> Dict[str, Any]:
        """測試技術指標計算準確性"""
        logger.info("🔄 測試技術指標計算...")
        
        try:
            # 準備測試價格數據
            price_data = [45000, 45200, 45600, 45800, 46000, 45700, 45500, 45900, 46200, 46100]
            volume_data = [1500, 1800, 2100, 1900, 2200, 1700, 1600, 2000, 2300, 2100]
            
            start_time = time.time()
            
            # 計算各種技術指標
            indicators_result = await self._calculate_technical_indicators(price_data, volume_data)
            
            processing_time = (time.time() - start_time) * 1000
            self.performance_metrics['indicator_calculation_latency'].append(processing_time)
            
            # 驗證指標計算結果
            validation_results = await self._validate_technical_indicators(indicators_result)
            
            # 檢查計算準確性
            accuracy_checks = {
                "rsi_range_valid": 0 <= indicators_result.get("rsi", -1) <= 100,
                "macd_exists": "macd" in indicators_result,
                "ema_exists": "ema_12" in indicators_result and "ema_26" in indicators_result,
                "volume_indicators_exist": "volume_trend" in indicators_result
            }
            
            all_indicators_valid = all(accuracy_checks.values())
            performance_target = 45.0  # 目標<45ms
            performance_pass = processing_time < performance_target
            
            overall_success = (
                all_indicators_valid and
                validation_results["validation_pass"] and
                performance_pass
            )
            
            result = {
                "test_name": "技術指標計算測試",
                "success": overall_success,
                "processing_time_ms": processing_time,
                "performance_target_ms": performance_target,
                "performance_pass": performance_pass,
                "calculated_indicators": indicators_result,
                "accuracy_checks": accuracy_checks,
                "validation_results": validation_results,
                "all_indicators_valid": all_indicators_valid,
                "status": "✅ PASSED" if overall_success else "❌ FAILED"
            }
            
            logger.info(f"{'✅' if overall_success else '❌'} 技術指標: {len(indicators_result)}個指標, {processing_time:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"❌ 技術指標計算測試失敗: {e}")
            return {
                "test_name": "技術指標計算測試",
                "success": False,
                "error": str(e),
                "status": "❌ ERROR"
            }
    
    async def test_phase1b_volatility_adaptation(self) -> Dict[str, Any]:
        """測試Phase1B波動率適應機制"""
        logger.info("🔄 測試Phase1B波動率適應...")
        
        try:
            # 模擬不同波動率情況
            volatility_scenarios = [
                {
                    "name": "高波動率",
                    "volatility_level": 0.08,  # 8%
                    "expected_adaptation": "increased_sensitivity"
                },
                {
                    "name": "中等波動率",
                    "volatility_level": 0.04,  # 4%
                    "expected_adaptation": "normal_sensitivity"
                },
                {
                    "name": "低波動率",
                    "volatility_level": 0.015,  # 1.5%
                    "expected_adaptation": "decreased_sensitivity"
                }
            ]
            
            # 模擬基礎信號
            base_signals = [
                {
                    "signal_type": "PRICE_BREAKOUT",
                    "signal_strength": 0.7,
                    "confidence_score": 0.8,
                    "timestamp": time.time()
                },
                {
                    "signal_type": "VOLUME_SURGE",
                    "signal_strength": 0.6,
                    "confidence_score": 0.75,
                    "timestamp": time.time()
                }
            ]
            
            adaptation_results = []
            
            for scenario in volatility_scenarios:
                start_time = time.time()
                
                # 模擬波動率適應
                adapted_signals = await self._simulate_volatility_adaptation(
                    base_signals, 
                    scenario["volatility_level"]
                )
                
                processing_time = (time.time() - start_time) * 1000
                self.performance_metrics['phase1b_latency'].append(processing_time)
                
                # 驗證適應效果
                adaptation_effective = await self._validate_adaptation_effectiveness(
                    adapted_signals, 
                    scenario["expected_adaptation"]
                )
                
                scenario_result = {
                    "scenario_name": scenario["name"],
                    "volatility_level": scenario["volatility_level"],
                    "processing_time_ms": processing_time,
                    "signals_adapted": len(adapted_signals),
                    "adaptation_effective": adaptation_effective,
                    "adapted_signals": adapted_signals
                }
                
                adaptation_results.append(scenario_result)
            
            # 評估整體適應性能
            avg_processing_time = np.mean([r["processing_time_ms"] for r in adaptation_results])
            all_adaptations_effective = all(r["adaptation_effective"] for r in adaptation_results)
            performance_target = 45.0  # 目標<45ms
            performance_pass = avg_processing_time < performance_target
            
            overall_success = all_adaptations_effective and performance_pass
            
            result = {
                "test_name": "Phase1B波動率適應測試",
                "success": overall_success,
                "avg_processing_time_ms": avg_processing_time,
                "performance_target_ms": performance_target,
                "performance_pass": performance_pass,
                "scenarios_tested": len(volatility_scenarios),
                "adaptation_results": adaptation_results,
                "all_adaptations_effective": all_adaptations_effective,
                "status": "✅ PASSED" if overall_success else "❌ FAILED"
            }
            
            logger.info(f"{'✅' if overall_success else '❌'} Phase1B: {len(volatility_scenarios)}個場景, {avg_processing_time:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"❌ Phase1B測試失敗: {e}")
            return {
                "test_name": "Phase1B波動率適應測試",
                "success": False,
                "error": str(e),
                "status": "❌ ERROR"
            }
    
    async def test_phase1c_signal_standardization(self) -> Dict[str, Any]:
        """測試Phase1C信號標準化流程"""
        logger.info("🔄 測試Phase1C信號標準化...")
        
        try:
            # 模擬未標準化的信號
            raw_signals = [
                {
                    "signal_type": "BREAKOUT",
                    "value": 0.85,
                    "confidence": 0.7,
                    "source": "phase1a",
                    "timestamp": time.time(),
                    "symbol": "BTCUSDT"
                },
                {
                    "signal_type": "MOMENTUM",
                    "value": 0.65,
                    "confidence": 0.8,
                    "source": "phase1b",
                    "timestamp": time.time(),
                    "symbol": "BTCUSDT"
                },
                {
                    "signal_type": "VOLUME_ANOMALY",
                    "value": 0.9,
                    "confidence": 0.75,
                    "source": "indicator_graph",
                    "timestamp": time.time(),
                    "symbol": "BTCUSDT"
                }
            ]
            
            start_time = time.time()
            
            # 模擬標準化處理
            standardized_signals = await self._simulate_signal_standardization(raw_signals)
            
            processing_time = (time.time() - start_time) * 1000
            self.performance_metrics['phase1c_latency'].append(processing_time)
            
            # 驗證標準化效果
            standardization_checks = await self._validate_signal_standardization(
                raw_signals, 
                standardized_signals
            )
            
            # 檢查標準化完整性
            completeness_checks = {
                "all_signals_processed": len(standardized_signals) == len(raw_signals),
                "tier_assignment_complete": all(
                    hasattr(signal, 'tier_assignment') or 'tier_assignment' in signal 
                    for signal in standardized_signals
                ),
                "priority_assignment_complete": all(
                    hasattr(signal, 'execution_priority') or 'execution_priority' in signal 
                    for signal in standardized_signals
                ),
                "standardization_applied": all(
                    hasattr(signal, 'standardized') or 'standardized' in signal 
                    for signal in standardized_signals
                )
            }
            
            all_checks_pass = all(completeness_checks.values())
            performance_target = 25.0  # 目標<25ms
            performance_pass = processing_time < performance_target
            
            overall_success = (
                all_checks_pass and
                standardization_checks["validation_pass"] and
                performance_pass
            )
            
            result = {
                "test_name": "Phase1C信號標準化測試",
                "success": overall_success,
                "processing_time_ms": processing_time,
                "performance_target_ms": performance_target,
                "performance_pass": performance_pass,
                "raw_signals_count": len(raw_signals),
                "standardized_signals_count": len(standardized_signals),
                "completeness_checks": completeness_checks,
                "standardization_checks": standardization_checks,
                "all_checks_pass": all_checks_pass,
                "sample_standardized_signals": standardized_signals[:2],  # 前2個作為示例
                "status": "✅ PASSED" if overall_success else "❌ FAILED"
            }
            
            logger.info(f"{'✅' if overall_success else '❌'} Phase1C: {len(standardized_signals)}個標準化信號, {processing_time:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"❌ Phase1C測試失敗: {e}")
            return {
                "test_name": "Phase1C信號標準化測試",
                "success": False,
                "error": str(e),
                "status": "❌ ERROR"
            }
    
    async def test_unified_signal_pool_aggregation(self) -> Dict[str, Any]:
        """測試統一信號池聚合邏輯"""
        logger.info("🔄 測試統一信號池聚合...")
        
        try:
            # 模擬來自不同來源的信號
            signals_from_sources = {
                "phase1a": [
                    {"signal_type": "BREAKOUT", "strength": 0.8, "confidence": 0.75},
                    {"signal_type": "REVERSAL", "strength": 0.7, "confidence": 0.7}
                ],
                "phase1b": [
                    {"signal_type": "VOLATILITY_ADAPTED", "strength": 0.85, "confidence": 0.8}
                ],
                "phase1c": [
                    {"signal_type": "STANDARDIZED_MOMENTUM", "strength": 0.9, "confidence": 0.85}
                ],
                "indicator_graph": [
                    {"signal_type": "RSI_OVERSOLD", "strength": 0.75, "confidence": 0.8},
                    {"signal_type": "MACD_BULLISH", "strength": 0.8, "confidence": 0.75}
                ]
            }
            
            start_time = time.time()
            
            # 模擬統一池聚合
            aggregated_signals = await self._simulate_unified_pool_aggregation(signals_from_sources)
            
            processing_time = (time.time() - start_time) * 1000
            self.performance_metrics['unified_pool_latency'].append(processing_time)
            
            # 驗證聚合效果
            aggregation_checks = await self._validate_signal_aggregation(
                signals_from_sources, 
                aggregated_signals
            )
            
            # 檢查聚合完整性
            total_input_signals = sum(len(signals) for signals in signals_from_sources.values())
            
            aggregation_metrics = {
                "input_signals_total": total_input_signals,
                "output_signals_count": len(aggregated_signals),
                "deduplication_effective": aggregation_checks.get("duplicates_removed", False),
                "quality_filtering_applied": aggregation_checks.get("quality_filtered", False),
                "source_diversity_maintained": len(set(
                    signal.get("source", "unknown") for signal in aggregated_signals
                )) > 1
            }
            
            performance_target = 28.0  # 目標<28ms
            performance_pass = processing_time < performance_target
            
            overall_success = (
                len(aggregated_signals) > 0 and
                aggregation_checks["validation_pass"] and
                aggregation_metrics["source_diversity_maintained"] and
                performance_pass
            )
            
            result = {
                "test_name": "統一信號池聚合測試",
                "success": overall_success,
                "processing_time_ms": processing_time,
                "performance_target_ms": performance_target,
                "performance_pass": performance_pass,
                "aggregation_metrics": aggregation_metrics,
                "aggregation_checks": aggregation_checks,
                "sample_aggregated_signals": aggregated_signals[:3],  # 前3個作為示例
                "status": "✅ PASSED" if overall_success else "❌ FAILED"
            }
            
            logger.info(f"{'✅' if overall_success else '❌'} 統一池: {len(aggregated_signals)}個聚合信號, {processing_time:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"❌ 統一信號池測試失敗: {e}")
            return {
                "test_name": "統一信號池聚合測試",
                "success": False,
                "error": str(e),
                "status": "❌ ERROR"
            }
    
    # === 模擬方法 ===
    
    async def _simulate_phase1a_generation(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """模擬Phase1A信號生成"""
        await asyncio.sleep(0.02)  # 模擬處理時間
        
        signals = []
        
        # 基於K線數據生成信號
        klines = market_data.get("klines", [])
        if klines:
            last_kline = klines[-1]
            price_change = (last_kline["close"] - last_kline["open"]) / last_kline["open"]
            
            if abs(price_change) > 0.01:  # 1%以上價格變化
                signals.append({
                    "signal_type": "PRICE_BREAKOUT" if price_change > 0 else "PRICE_BREAKDOWN",
                    "signal_strength": min(0.9, abs(price_change) * 50),
                    "confidence_score": 0.7 + min(0.2, abs(price_change) * 10),
                    "source": "phase1a",
                    "timestamp": time.time(),
                    "price_change": price_change
                })
        
        # 基於訂單簿生成信號
        orderbook = market_data.get("orderbook", {})
        if orderbook:
            bids = orderbook.get("bids", [])
            asks = orderbook.get("asks", [])
            
            if bids and asks:
                spread = (asks[0][0] - bids[0][0]) / bids[0][0]
                if spread < 0.001:  # 緊密價差
                    signals.append({
                        "signal_type": "TIGHT_SPREAD",
                        "signal_strength": 0.6,
                        "confidence_score": 0.8,
                        "source": "phase1a",
                        "timestamp": time.time(),
                        "spread": spread
                    })
        
        return signals
    
    async def _validate_phase1a_signals(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """驗證Phase1A信號質量"""
        await asyncio.sleep(0.001)
        
        if not signals:
            return {"all_valid": False, "error": "no_signals_generated"}
        
        validation_checks = []
        
        for signal in signals:
            checks = {
                "has_signal_type": "signal_type" in signal,
                "has_strength": "signal_strength" in signal and 0 <= signal.get("signal_strength", -1) <= 1,
                "has_confidence": "confidence_score" in signal and 0 <= signal.get("confidence_score", -1) <= 1,
                "has_source": "source" in signal,
                "has_timestamp": "timestamp" in signal
            }
            validation_checks.append(all(checks.values()))
        
        return {
            "all_valid": all(validation_checks),
            "valid_signals": sum(validation_checks),
            "total_signals": len(signals),
            "validation_rate": sum(validation_checks) / len(signals) * 100
        }
    
    async def _calculate_technical_indicators(self, price_data: List[float], volume_data: List[float]) -> Dict[str, Any]:
        """計算技術指標"""
        await asyncio.sleep(0.04)  # 模擬指標計算時間
        
        # 簡化的技術指標計算
        prices = np.array(price_data)
        volumes = np.array(volume_data)
        
        # RSI計算 (簡化版)
        price_changes = np.diff(prices)
        gains = np.where(price_changes > 0, price_changes, 0)
        losses = np.where(price_changes < 0, -price_changes, 0)
        
        avg_gain = np.mean(gains) if len(gains) > 0 else 0
        avg_loss = np.mean(losses) if len(losses) > 0 else 0
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        # EMA計算 (簡化版)
        ema_12 = np.mean(prices[-12:]) if len(prices) >= 12 else np.mean(prices)
        ema_26 = np.mean(prices[-26:]) if len(prices) >= 26 else np.mean(prices)
        
        # MACD計算
        macd = ema_12 - ema_26
        
        # 成交量指標
        volume_trend = np.mean(volumes[-5:]) / np.mean(volumes[:-5]) if len(volumes) > 5 else 1.0
        
        return {
            "rsi": float(rsi),
            "ema_12": float(ema_12),
            "ema_26": float(ema_26),
            "macd": float(macd),
            "volume_trend": float(volume_trend),
            "calculation_timestamp": time.time()
        }
    
    async def _validate_technical_indicators(self, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """驗證技術指標計算結果"""
        await asyncio.sleep(0.001)
        
        required_indicators = ["rsi", "ema_12", "ema_26", "macd", "volume_trend"]
        
        validation_results = {
            "required_indicators_present": all(ind in indicators for ind in required_indicators),
            "rsi_in_valid_range": 0 <= indicators.get("rsi", -1) <= 100,
            "ema_values_positive": indicators.get("ema_12", 0) > 0 and indicators.get("ema_26", 0) > 0,
            "volume_trend_reasonable": 0.1 <= indicators.get("volume_trend", 0) <= 10.0
        }
        
        return {
            "validation_pass": all(validation_results.values()),
            "validation_details": validation_results,
            "indicators_count": len(indicators)
        }
    
    async def _simulate_volatility_adaptation(self, base_signals: List[Dict[str, Any]], volatility_level: float) -> List[Dict[str, Any]]:
        """模擬波動率適應"""
        await asyncio.sleep(0.03)  # 模擬適應處理時間
        
        adapted_signals = []
        
        for signal in base_signals:
            adapted_signal = signal.copy()
            
            # 根據波動率調整信號強度
            if volatility_level > 0.06:  # 高波動率
                adapted_signal["signal_strength"] *= 1.2  # 增強信號
                adapted_signal["adaptation_type"] = "high_volatility_boost"
            elif volatility_level < 0.02:  # 低波動率
                adapted_signal["signal_strength"] *= 0.8  # 減弱信號
                adapted_signal["adaptation_type"] = "low_volatility_dampening"
            else:  # 中等波動率
                adapted_signal["adaptation_type"] = "normal_volatility"
            
            # 確保信號強度在有效範圍內
            adapted_signal["signal_strength"] = min(1.0, max(0.0, adapted_signal["signal_strength"]))
            
            # 添加適應元數據
            adapted_signal["volatility_adapted"] = True
            adapted_signal["original_strength"] = signal["signal_strength"]
            adapted_signal["volatility_level"] = volatility_level
            adapted_signal["adaptation_timestamp"] = time.time()
            
            adapted_signals.append(adapted_signal)
        
        return adapted_signals
    
    async def _validate_adaptation_effectiveness(self, adapted_signals: List[Dict[str, Any]], expected_adaptation: str) -> bool:
        """驗證適應效果"""
        await asyncio.sleep(0.001)
        
        if not adapted_signals:
            return False
        
        # 檢查適應標記
        all_adapted = all(signal.get("volatility_adapted", False) for signal in adapted_signals)
        
        # 檢查適應類型
        adaptation_types = [signal.get("adaptation_type", "") for signal in adapted_signals]
        
        if expected_adaptation == "increased_sensitivity":
            return all_adapted and any("high_volatility" in atype for atype in adaptation_types)
        elif expected_adaptation == "decreased_sensitivity":
            return all_adapted and any("low_volatility" in atype for atype in adaptation_types)
        else:  # normal_sensitivity
            return all_adapted and any("normal_volatility" in atype for atype in adaptation_types)
    
    async def _simulate_signal_standardization(self, raw_signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """模擬信號標準化"""
        await asyncio.sleep(0.02)  # 模擬標準化處理時間
        
        standardized_signals = []
        
        for i, signal in enumerate(raw_signals):
            standardized_signal = signal.copy()
            
            # 分配層級
            signal_strength = signal.get("value", signal.get("signal_strength", 0.5))
            
            if signal_strength >= 0.8:
                tier = "tier_1_critical"
                priority = 1
            elif signal_strength >= 0.6:
                tier = "tier_2_important"
                priority = 2
            else:
                tier = "tier_3_standard"
                priority = 3
            
            # 標準化字段
            standardized_signal.update({
                "standardized": True,
                "tier_assignment": tier,
                "execution_priority": priority,
                "normalized_strength": min(1.0, max(0.0, signal_strength)),
                "quality_score": signal.get("confidence", 0.7),
                "standardization_timestamp": time.time(),
                "processing_order": i + 1
            })
            
            standardized_signals.append(standardized_signal)
        
        return standardized_signals
    
    async def _validate_signal_standardization(self, raw_signals: List[Dict[str, Any]], standardized_signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """驗證信號標準化"""
        await asyncio.sleep(0.001)
        
        if len(raw_signals) != len(standardized_signals):
            return {"validation_pass": False, "error": "signal_count_mismatch"}
        
        validation_checks = []
        
        for std_signal in standardized_signals:
            checks = {
                "has_standardized_flag": std_signal.get("standardized", False),
                "has_tier_assignment": "tier_assignment" in std_signal,
                "has_execution_priority": "execution_priority" in std_signal,
                "has_normalized_strength": "normalized_strength" in std_signal,
                "normalized_strength_valid": 0 <= std_signal.get("normalized_strength", -1) <= 1
            }
            validation_checks.append(all(checks.values()))
        
        return {
            "validation_pass": all(validation_checks),
            "standardized_count": sum(validation_checks),
            "total_count": len(standardized_signals),
            "standardization_rate": sum(validation_checks) / len(standardized_signals) * 100
        }
    
    async def _simulate_unified_pool_aggregation(self, signals_from_sources: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """模擬統一池聚合"""
        await asyncio.sleep(0.025)  # 模擬聚合處理時間
        
        aggregated_signals = []
        signal_id = 1
        
        # 聚合所有來源的信號
        for source, signals in signals_from_sources.items():
            for signal in signals:
                aggregated_signal = signal.copy()
                aggregated_signal.update({
                    "signal_id": f"unified_{signal_id:04d}",
                    "source": source,
                    "aggregation_timestamp": time.time(),
                    "unified_pool_processed": True,
                    "quality_score": signal.get("confidence", 0.7),
                    "source_weight": self._get_source_weight(source)
                })
                
                aggregated_signals.append(aggregated_signal)
                signal_id += 1
        
        # 模擬去重和質量過濾
        filtered_signals = []
        seen_types = set()
        
        # 按質量分數排序
        aggregated_signals.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
        
        for signal in aggregated_signals:
            signal_type = signal.get("signal_type", "unknown")
            
            # 簡單去重：每種信號類型只保留最高質量的
            if signal_type not in seen_types and signal.get("quality_score", 0) >= 0.6:
                seen_types.add(signal_type)
                signal["deduplication_applied"] = True
                signal["quality_filtering_applied"] = True
                filtered_signals.append(signal)
        
        return filtered_signals
    
    def _get_source_weight(self, source: str) -> float:
        """獲取來源權重"""
        weights = {
            "phase1a": 0.3,
            "phase1b": 0.25,
            "phase1c": 0.25,
            "indicator_graph": 0.2
        }
        return weights.get(source, 0.1)
    
    async def _validate_signal_aggregation(self, input_sources: Dict[str, List], aggregated_signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """驗證信號聚合"""
        await asyncio.sleep(0.001)
        
        total_input = sum(len(signals) for signals in input_sources.values())
        
        # 檢查聚合質量
        aggregation_checks = {
            "signals_aggregated": len(aggregated_signals) > 0,
            "duplicates_removed": len(aggregated_signals) <= total_input,
            "quality_filtered": all(signal.get("quality_score", 0) >= 0.6 for signal in aggregated_signals),
            "source_attribution_maintained": all("source" in signal for signal in aggregated_signals),
            "unified_processing_applied": all(signal.get("unified_pool_processed", False) for signal in aggregated_signals)
        }
        
        return {
            "validation_pass": all(aggregation_checks.values()),
            "aggregation_details": aggregation_checks,
            "input_signals_total": total_input,
            "output_signals_count": len(aggregated_signals),
            "reduction_ratio": (total_input - len(aggregated_signals)) / total_input * 100 if total_input > 0 else 0
        }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """運行所有Phase1組件測試"""
        logger.info("🚀 開始Phase1信號生成系統綜合測試...")
        
        test_methods = [
            self.test_phase1a_signal_generation,
            self.test_technical_indicator_calculation,
            self.test_phase1b_volatility_adaptation,
            self.test_phase1c_signal_standardization,
            self.test_unified_signal_pool_aggregation
        ]
        
        all_results = {}
        start_time = time.time()
        
        for test_method in test_methods:
            test_name = test_method.__name__
            logger.info(f"\n📋 執行測試: {test_name}")
            
            try:
                result = await test_method()
                all_results[test_name] = result
                
                status = "✅" if result.get("success", False) else "❌"
                logger.info(f"{status} {test_name}: {result.get('status', 'UNKNOWN')}")
                
            except Exception as e:
                logger.error(f"❌ {test_name} 執行失敗: {e}")
                all_results[test_name] = {
                    "success": False,
                    "error": str(e),
                    "status": "❌ EXCEPTION"
                }
        
        # 計算總體結果
        total_tests = len(test_methods)
        passed_tests = sum(1 for result in all_results.values() if result.get("success", False))
        overall_success_rate = (passed_tests / total_tests) * 100
        
        # 計算性能統計
        performance_stats = {}
        for metric_name, latencies in self.performance_metrics.items():
            if latencies:
                performance_stats[metric_name] = {
                    "avg_ms": np.mean(latencies),
                    "max_ms": np.max(latencies),
                    "min_ms": np.min(latencies)
                }
        
        total_time = time.time() - start_time
        
        summary = {
            "test_type": "Phase1信號生成系統綜合測試",
            "start_time": datetime.fromtimestamp(start_time).isoformat(),
            "total_duration_s": total_time,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "overall_success_rate": overall_success_rate,
            "performance_statistics": performance_stats,
            "status": "✅ PASSED" if overall_success_rate >= 80.0 else "❌ FAILED",
            "detailed_results": all_results
        }
        
        logger.info(f"\n🎯 Phase1綜合測試完成:")
        logger.info(f"   總測試數: {total_tests}")
        logger.info(f"   通過測試: {passed_tests}")
        logger.info(f"   成功率: {overall_success_rate:.1f}%")
        logger.info(f"   總耗時: {total_time:.2f}秒")
        logger.info(f"   狀態: {summary['status']}")
        
        return summary

# 主執行函數
async def main():
    """主測試執行函數"""
    tester = Phase1ComprehensiveTest()
    results = await tester.run_all_tests()
    
    # 輸出測試報告
    print("\n" + "="*80)
    print("📊 Phase1信號生成系統綜合測試報告")
    print("="*80)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    return results

if __name__ == "__main__":
    # 運行測試
    results = asyncio.run(main())
    
    # 根據結果決定退出代碼
    exit_code = 0 if results.get("overall_success_rate", 0) >= 80.0 else 1
    exit(exit_code)
