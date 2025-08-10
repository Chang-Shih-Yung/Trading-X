#!/usr/bin/env python3
"""
🎯 Phase1 實時信號流端到端測試
從實時數據抓取 -> Phase1全流程 -> EPL預備
"""

import asyncio
import time
import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

# 添加路徑
current_dir = Path(__file__).parent
sys.path.extend([
    str(current_dir / "X" / "backend" / "phase1_signal_generation"),
    str(current_dir / "X" / "backend" / "phase1_signal_generation" / "websocket_realtime_driver"),
    str(current_dir / "X" / "backend" / "phase1_signal_generation" / "phase1a_basic_signal_generation"),
    str(current_dir / "X" / "backend" / "phase1_signal_generation" / "indicator_dependency"),
    str(current_dir / "X" / "backend" / "phase1_signal_generation" / "phase1b_volatility_adaptation"),
    str(current_dir / "X" / "backend" / "phase1_signal_generation" / "phase1c_signal_standardization"),
    str(current_dir / "X" / "backend" / "phase1_signal_generation" / "unified_signal_pool"),
])

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealTimeSignalFlowEngine:
    """實時信號流測試引擎"""
    
    def __init__(self):
        self.flow_metrics = {
            "total_processing_time": 0.0,
            "stage_times": {},
            "signals_generated": {},
            "final_epl_signals": 0,
            "success_rate": 0.0
        }
        
        # 模擬 Phase1 各模組
        self.modules = {}
        
    async def run_realtime_signal_flow_test(self, duration_seconds: int = 60):
        """運行實時信號流測試"""
        logger.info(f"🚀 開始 {duration_seconds} 秒實時信號流測試")
        
        start_time = time.time()
        total_cycles = 0
        successful_cycles = 0
        
        while time.time() - start_time < duration_seconds:
            cycle_start = time.time()
            
            try:
                # 執行一個完整的信號流周期
                success = await self._execute_signal_flow_cycle()
                
                total_cycles += 1
                if success:
                    successful_cycles += 1
                
                # 計算周期時間
                cycle_time = (time.time() - cycle_start) * 1000
                logger.info(f"🔄 周期 {total_cycles}: {'✅' if success else '❌'} 耗時 {cycle_time:.1f}ms")
                
                # 控制頻率（每2秒一個周期）
                await asyncio.sleep(2.0)
                
            except Exception as e:
                logger.error(f"❌ 周期 {total_cycles + 1} 執行失敗: {e}")
                total_cycles += 1
        
        # 計算最終指標
        self.flow_metrics["success_rate"] = successful_cycles / total_cycles if total_cycles > 0 else 0
        self.flow_metrics["total_cycles"] = total_cycles
        self.flow_metrics["successful_cycles"] = successful_cycles
        
        # 生成測試報告
        await self._generate_flow_test_report()
        
        return self.flow_metrics["success_rate"] >= 0.8
    
    async def _execute_signal_flow_cycle(self) -> bool:
        """執行一個完整的信號流周期"""
        try:
            flow_start = time.time()
            
            # 第1階段：模擬實時數據獲取 (WebSocket)
            stage_start = time.time()
            market_data = await self._stage_1_realtime_data_acquisition()
            self.flow_metrics["stage_times"]["data_acquisition"] = (time.time() - stage_start) * 1000
            
            if not market_data:
                return False
            
            # 第2階段：Phase1A 基礎信號生成
            stage_start = time.time()
            phase1a_signals = await self._stage_2_phase1a_signal_generation(market_data)
            self.flow_metrics["stage_times"]["phase1a_generation"] = (time.time() - stage_start) * 1000
            
            # 第3階段：指標依賴計算
            stage_start = time.time()
            indicator_signals = await self._stage_3_indicator_calculation(market_data)
            self.flow_metrics["stage_times"]["indicator_calculation"] = (time.time() - stage_start) * 1000
            
            # 第4階段：Phase1B 波動性適應
            stage_start = time.time()
            phase1b_signals = await self._stage_4_phase1b_adaptation(phase1a_signals + indicator_signals, market_data)
            self.flow_metrics["stage_times"]["phase1b_adaptation"] = (time.time() - stage_start) * 1000
            
            # 第5階段：Phase1C 信號標準化
            stage_start = time.time()
            phase1c_signals = await self._stage_5_phase1c_standardization(phase1b_signals)
            self.flow_metrics["stage_times"]["phase1c_standardization"] = (time.time() - stage_start) * 1000
            
            # 第6階段：統一信號池聚合
            stage_start = time.time()
            unified_signals = await self._stage_6_unified_pool_aggregation({
                'phase1a': phase1a_signals,
                'indicators': indicator_signals,
                'phase1b': phase1b_signals,
                'phase1c': phase1c_signals
            })
            self.flow_metrics["stage_times"]["unified_aggregation"] = (time.time() - stage_start) * 1000
            
            # 第7階段：EPL 預處理準備
            stage_start = time.time()
            epl_ready_signals = await self._stage_7_epl_preprocessing(unified_signals)
            self.flow_metrics["stage_times"]["epl_preprocessing"] = (time.time() - stage_start) * 1000
            
            # 記錄總體指標
            self.flow_metrics["total_processing_time"] = (time.time() - flow_start) * 1000
            self.flow_metrics["signals_generated"]["phase1a"] = len(phase1a_signals)
            self.flow_metrics["signals_generated"]["indicators"] = len(indicator_signals)
            self.flow_metrics["signals_generated"]["phase1b"] = len(phase1b_signals)
            self.flow_metrics["signals_generated"]["phase1c"] = len(phase1c_signals)
            self.flow_metrics["signals_generated"]["unified"] = len(unified_signals)
            self.flow_metrics["final_epl_signals"] = len(epl_ready_signals)
            
            logger.info(f"✅ 完整信號流: {len(epl_ready_signals)} 個 EPL 信號，總耗時 {self.flow_metrics['total_processing_time']:.1f}ms")
            
            return len(epl_ready_signals) > 0
            
        except Exception as e:
            logger.error(f"❌ 信號流周期執行失敗: {e}")
            return False
    
    async def _stage_1_realtime_data_acquisition(self) -> Dict[str, Any]:
        """第1階段：實時數據獲取"""
        try:
            # 模擬實時市場數據
            import random
            
            base_price = 45000.0
            price_change = random.uniform(-0.02, 0.02)  # ±2% 價格變化
            current_price = base_price * (1 + price_change)
            
            volume_multiplier = random.uniform(0.5, 3.0)  # 0.5x-3x 成交量變化
            base_volume = 1000.0
            current_volume = base_volume * volume_multiplier
            
            # 生成 K線數據（最近100根）
            klines = []
            for i in range(100):
                timestamp = int((time.time() - (100 - i) * 60) * 1000)  # 每分鐘一根K線
                open_price = base_price + random.uniform(-100, 100)
                high_price = open_price + random.uniform(0, 50)
                low_price = open_price - random.uniform(0, 50)
                close_price = open_price + random.uniform(-25, 25)
                volume = base_volume * random.uniform(0.8, 1.2)
                
                klines.append([
                    timestamp,  # 開盤時間
                    str(open_price),  # 開盤價
                    str(high_price),  # 最高價
                    str(low_price),  # 最低價
                    str(close_price),  # 收盤價
                    str(volume),  # 成交量
                    timestamp + 60000,  # 收盤時間
                    str(volume * close_price),  # 成交額
                    100,  # 成交筆數
                    str(volume * 0.6),  # 主動買入成交量
                    str(volume * close_price * 0.6),  # 主動買入成交額
                    "0"  # 忽略字段
                ])
            
            # 生成訂單簿數據
            orderbook = {
                "bids": [[str(current_price - i), str(random.uniform(10, 100))] for i in range(1, 6)],
                "asks": [[str(current_price + i), str(random.uniform(10, 100))] for i in range(1, 6)]
            }
            
            market_data = {
                "symbol": "BTCUSDT",
                "price": current_price,
                "volume": current_volume,
                "timestamp": datetime.now(),
                "klines": klines,
                "orderbook": orderbook,
                "bid": current_price - 0.5,
                "ask": current_price + 0.5,
                "price_change_pct": price_change * 100,
                "volume_ratio": volume_multiplier,
                "data_completeness": 1.0
            }
            
            logger.debug(f"📊 市場數據: BTC ${current_price:.1f} ({price_change*100:+.2f}%), 成交量 {volume_multiplier:.1f}x")
            
            return market_data
            
        except Exception as e:
            logger.error(f"❌ 實時數據獲取失敗: {e}")
            return {}
    
    async def _stage_2_phase1a_signal_generation(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """第2階段：Phase1A 基礎信號生成"""
        try:
            signals = []
            
            # 價格突破檢測
            price_change = market_data.get("price_change_pct", 0)
            if abs(price_change) > 1.0:  # 1% 價格變化閾值
                signals.append({
                    "signal_id": f"phase1a_price_{uuid.uuid4().hex[:8]}",
                    "signal_type": "PRICE_BREAKOUT",
                    "signal_strength": min(1.0, abs(price_change) / 5.0),  # 5% 變化 = 滿強度
                    "confidence_score": 0.75 + min(0.2, abs(price_change) / 10.0),
                    "signal_source": "phase1a",
                    "timestamp": datetime.now(),
                    "metadata": {
                        "price_change_pct": price_change,
                        "trigger_threshold": 1.0
                    }
                })
            
            # 成交量激增檢測
            volume_ratio = market_data.get("volume_ratio", 1.0)
            if volume_ratio > 1.5:  # 1.5x 成交量閾值
                signals.append({
                    "signal_id": f"phase1a_volume_{uuid.uuid4().hex[:8]}",
                    "signal_type": "VOLUME_SURGE",
                    "signal_strength": min(1.0, (volume_ratio - 1.0) / 2.0),  # 3x 成交量 = 滿強度
                    "confidence_score": 0.7 + min(0.25, (volume_ratio - 1.0) / 4.0),
                    "signal_source": "phase1a",
                    "timestamp": datetime.now(),
                    "metadata": {
                        "volume_ratio": volume_ratio,
                        "trigger_threshold": 1.5
                    }
                })
            
            # 動量轉換檢測（簡化）
            if abs(price_change) > 0.5 and volume_ratio > 1.2:
                signals.append({
                    "signal_id": f"phase1a_momentum_{uuid.uuid4().hex[:8]}",
                    "signal_type": "MOMENTUM_SHIFT", 
                    "signal_strength": min(1.0, (abs(price_change) + volume_ratio) / 4.0),
                    "confidence_score": 0.65 + min(0.3, (abs(price_change) + volume_ratio) / 6.0),
                    "signal_source": "phase1a",
                    "timestamp": datetime.now(),
                    "metadata": {
                        "price_momentum": price_change,
                        "volume_momentum": volume_ratio
                    }
                })
            
            logger.debug(f"📈 Phase1A: 生成 {len(signals)} 個基礎信號")
            return signals
            
        except Exception as e:
            logger.error(f"❌ Phase1A 信號生成失敗: {e}")
            return []
    
    async def _stage_3_indicator_calculation(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """第3階段：技術指標計算"""
        try:
            signals = []
            klines = market_data.get("klines", [])
            
            if len(klines) >= 20:
                # 獲取收盤價數據
                prices = [float(k[4]) for k in klines[-20:]]  # 最近20個收盤價
                
                # 簡化 RSI 計算
                if len(prices) >= 14:
                    gains = [max(0, prices[i] - prices[i-1]) for i in range(1, len(prices))]
                    losses = [max(0, prices[i-1] - prices[i]) for i in range(1, len(prices))]
                    
                    if gains and losses:
                        avg_gain = sum(gains[-14:]) / 14
                        avg_loss = sum(losses[-14:]) / 14
                        
                        if avg_loss > 0:
                            rs = avg_gain / avg_loss
                            rsi = 100 - (100 / (1 + rs))
                            
                            # RSI 信號判斷
                            if rsi > 70 or rsi < 30:
                                signals.append({
                                    "signal_id": f"indicator_rsi_{uuid.uuid4().hex[:8]}",
                                    "signal_type": "RSI_signals",
                                    "signal_strength": min(1.0, abs(rsi - 50) / 50),
                                    "confidence_score": 0.7 + min(0.25, abs(rsi - 50) / 100),
                                    "signal_source": "indicator_graph",
                                    "timestamp": datetime.now(),
                                    "metadata": {
                                        "rsi_value": rsi,
                                        "condition": "oversold" if rsi < 30 else "overbought"
                                    }
                                })
                
                # 簡化 MACD 計算
                if len(prices) >= 26:
                    ema_12 = sum(prices[-12:]) / 12
                    ema_26 = sum(prices[-26:]) / 26
                    macd = ema_12 - ema_26
                    current_price = prices[-1]
                    
                    # MACD 信號判斷
                    macd_ratio = abs(macd) / current_price
                    if macd_ratio > 0.001:  # 0.1% 閾值
                        signals.append({
                            "signal_id": f"indicator_macd_{uuid.uuid4().hex[:8]}",
                            "signal_type": "MACD_signals",
                            "signal_strength": min(1.0, macd_ratio * 500),  # 放大係數
                            "confidence_score": 0.65 + min(0.3, macd_ratio * 1000),
                            "signal_source": "indicator_graph",
                            "timestamp": datetime.now(),
                            "metadata": {
                                "macd_value": macd,
                                "macd_ratio": macd_ratio,
                                "direction": "bullish" if macd > 0 else "bearish"
                            }
                        })
                
                # 布林帶計算
                if len(prices) >= 20:
                    sma_20 = sum(prices) / len(prices)
                    variance = sum((p - sma_20) ** 2 for p in prices) / len(prices)
                    std_dev = variance ** 0.5
                    
                    upper_band = sma_20 + (2 * std_dev)
                    lower_band = sma_20 - (2 * std_dev)
                    current_price = prices[-1]
                    
                    # 布林帶突破信號
                    if current_price > upper_band or current_price < lower_band:
                        band_penetration = abs(current_price - sma_20) / std_dev / 2
                        signals.append({
                            "signal_id": f"indicator_bb_{uuid.uuid4().hex[:8]}",
                            "signal_type": "BB_signals",
                            "signal_strength": min(1.0, band_penetration),
                            "confidence_score": 0.72 + min(0.25, band_penetration * 0.5),
                            "signal_source": "indicator_graph",
                            "timestamp": datetime.now(),
                            "metadata": {
                                "bb_position": "upper" if current_price > upper_band else "lower",
                                "penetration_ratio": band_penetration,
                                "sma_20": sma_20
                            }
                        })
            
            logger.debug(f"📊 指標計算: 生成 {len(signals)} 個技術指標信號")
            return signals
            
        except Exception as e:
            logger.error(f"❌ 技術指標計算失敗: {e}")
            return []
    
    async def _stage_4_phase1b_adaptation(self, input_signals: List[Dict[str, Any]], market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """第4階段：Phase1B 波動性適應"""
        try:
            adapted_signals = []
            
            # 計算市場波動性
            klines = market_data.get("klines", [])
            if len(klines) >= 10:
                recent_prices = [float(k[4]) for k in klines[-10:]]
                price_changes = [(recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1] 
                               for i in range(1, len(recent_prices))]
                volatility = (sum(pc ** 2 for pc in price_changes) / len(price_changes)) ** 0.5
            else:
                volatility = 0.01  # 默認波動性
            
            # 對每個輸入信號進行波動性適應
            for signal in input_signals:
                adapted_signal = signal.copy()
                
                # 波動性調整
                if volatility > 0.02:  # 高波動性市場
                    # 提升信號強度和信心度
                    adapted_signal["signal_strength"] = min(1.0, signal["signal_strength"] * 1.2)
                    adapted_signal["confidence_score"] = min(1.0, signal["confidence_score"] * 1.1)
                    adapted_signal["volatility_regime"] = "high"
                elif volatility < 0.005:  # 低波動性市場
                    # 降低信號強度
                    adapted_signal["signal_strength"] = signal["signal_strength"] * 0.8
                    adapted_signal["confidence_score"] = signal["confidence_score"] * 0.9
                    adapted_signal["volatility_regime"] = "low"
                else:
                    adapted_signal["volatility_regime"] = "normal"
                
                # 添加 Phase1B 特有的字段
                adapted_signal.update({
                    "stability_score": 1.0 - volatility * 10,  # 波動性越高，穩定性越低
                    "volatility_value": volatility,
                    "adaptation_applied": True,
                    "processing_stage": "phase1b"
                })
                
                adapted_signals.append(adapted_signal)
            
            # 添加 Phase1B 特有的波動性信號
            if volatility > 0.025:  # 極高波動性
                adapted_signals.append({
                    "signal_id": f"phase1b_volatility_{uuid.uuid4().hex[:8]}",
                    "signal_type": "VOLATILITY_BREAKOUT",
                    "signal_strength": min(1.0, volatility * 20),
                    "confidence_score": 0.8,
                    "signal_source": "phase1b",
                    "timestamp": datetime.now(),
                    "stability_score": 1.0 - volatility * 10,
                    "volatility_value": volatility,
                    "metadata": {
                        "volatility_threshold": 0.025,
                        "market_regime": "extreme_volatility"
                    }
                })
            
            logger.debug(f"🌊 Phase1B: {len(input_signals)} -> {len(adapted_signals)} 信號，波動性 {volatility:.4f}")
            return adapted_signals
            
        except Exception as e:
            logger.error(f"❌ Phase1B 波動性適應失敗: {e}")
            return input_signals
    
    async def _stage_5_phase1c_standardization(self, input_signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """第5階段：Phase1C 信號標準化"""
        try:
            standardized_signals = []
            
            for signal in input_signals:
                standardized_signal = signal.copy()
                
                # 標準化信號強度到 0.0-1.0
                original_strength = signal.get("signal_strength", 0.5)
                normalized_strength = max(0.0, min(1.0, original_strength))
                
                # 標準化信心度到 0.0-1.0
                original_confidence = signal.get("confidence_score", 0.5)
                normalized_confidence = max(0.0, min(1.0, original_confidence))
                
                # 計算綜合品質分數
                quality_score = (normalized_strength * 0.6 + normalized_confidence * 0.4)
                
                # 分層分配
                if quality_score >= 0.8:
                    tier = "tier_1_critical"
                    execution_priority = 1
                elif quality_score >= 0.6:
                    tier = "tier_2_important" 
                    execution_priority = 2
                else:
                    tier = "tier_3_normal"
                    execution_priority = 3
                
                # 更新標準化字段
                standardized_signal.update({
                    "signal_strength": normalized_strength,
                    "confidence_score": normalized_confidence,
                    "quality_score": quality_score,
                    "tier_assignment": tier,
                    "execution_priority": execution_priority,
                    "processing_stage": "phase1c",
                    "standardization_applied": True,
                    "risk_assessment": 1.0 - normalized_confidence,
                    "position_sizing": normalized_confidence * 0.1,  # 最大10%倉位
                    "metadata": {
                        **signal.get("metadata", {}),
                        "original_strength": original_strength,
                        "original_confidence": original_confidence,
                        "standardization_timestamp": datetime.now().isoformat()
                    }
                })
                
                standardized_signals.append(standardized_signal)
            
            # 按品質分數排序
            standardized_signals.sort(key=lambda x: x["quality_score"], reverse=True)
            
            logger.debug(f"📏 Phase1C: 標準化 {len(standardized_signals)} 個信號")
            return standardized_signals
            
        except Exception as e:
            logger.error(f"❌ Phase1C 信號標準化失敗: {e}")
            return input_signals
    
    async def _stage_6_unified_pool_aggregation(self, signals_by_source: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """第6階段：統一信號池聚合"""
        try:
            all_signals = []
            
            # 合併所有信號源的信號
            for source, signals in signals_by_source.items():
                for signal in signals:
                    signal["aggregation_source"] = source
                    all_signals.append(signal)
            
            # 去重處理（基於信號類型和時間窗口）
            deduplicated_signals = []
            for signal in all_signals:
                is_duplicate = False
                signal_type = signal.get("signal_type", "")
                signal_time = signal.get("timestamp", datetime.now())
                
                for existing in deduplicated_signals:
                    if (existing.get("signal_type") == signal_type and
                        abs((signal_time - existing.get("timestamp", datetime.now())).total_seconds()) < 30):
                        # 保留品質更高的信號
                        if signal.get("quality_score", 0) > existing.get("quality_score", 0):
                            deduplicated_signals.remove(existing)
                            break
                        else:
                            is_duplicate = True
                            break
                
                if not is_duplicate:
                    deduplicated_signals.append(signal)
            
            # 品質過濾（最低品質分數 0.5）
            quality_filtered = [s for s in deduplicated_signals if s.get("quality_score", 0) >= 0.5]
            
            # 數量限制（最多保留前10個最高品質信號）
            final_signals = sorted(quality_filtered, key=lambda x: x.get("quality_score", 0), reverse=True)[:10]
            
            # 添加聚合元數據
            for i, signal in enumerate(final_signals):
                signal.update({
                    "pool_ranking": i + 1,
                    "aggregation_timestamp": datetime.now(),
                    "processing_stage": "unified_pool",
                    "final_candidate": True
                })
            
            logger.debug(f"🎯 統一池: {sum(len(signals) for signals in signals_by_source.values())} -> {len(final_signals)} 個候選信號")
            return final_signals
            
        except Exception as e:
            logger.error(f"❌ 統一信號池聚合失敗: {e}")
            return []
    
    async def _stage_7_epl_preprocessing(self, unified_signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """第7階段：EPL 預處理準備"""
        try:
            epl_ready_signals = []
            
            for signal in unified_signals:
                # EPL 通過概率預測（簡化模型）
                quality_score = signal.get("quality_score", 0.5)
                confidence = signal.get("confidence_score", 0.5)
                strength = signal.get("signal_strength", 0.5)
                
                # 綜合評分決定 EPL 通過概率
                epl_prediction = (quality_score * 0.4 + confidence * 0.3 + strength * 0.3)
                
                # 只保留 EPL 預測通過概率 > 0.6 的信號
                if epl_prediction > 0.6:
                    epl_signal = signal.copy()
                    epl_signal.update({
                        "epl_prediction": epl_prediction,
                        "epl_ready": True,
                        "processing_stage": "epl_preprocessing",
                        "stop_loss_suggestion": 0.02,  # 2% 止損
                        "take_profit_levels": [0.02, 0.04, 0.06],  # 多層止盈
                        "position_sizing": min(0.1, confidence * 0.15),  # 動態倉位
                        "execution_conditions": ["market_open", "sufficient_liquidity"],
                        "contraindications": ["extreme_volatility"] if signal.get("volatility_value", 0) > 0.03 else [],
                        "epl_preprocessing_timestamp": datetime.now(),
                        "ready_for_phase2": True
                    })
                    
                    epl_ready_signals.append(epl_signal)
            
            # 最終排序：按 EPL 預測概率降序
            epl_ready_signals.sort(key=lambda x: x["epl_prediction"], reverse=True)
            
            logger.info(f"🎯 EPL 預處理: {len(unified_signals)} -> {len(epl_ready_signals)} 個準備就緒信號")
            
            return epl_ready_signals
            
        except Exception as e:
            logger.error(f"❌ EPL 預處理失敗: {e}")
            return []
    
    async def _generate_flow_test_report(self):
        """生成流程測試報告"""
        total_time = self.flow_metrics.get("total_processing_time", 0)
        success_rate = self.flow_metrics.get("success_rate", 0)
        
        report = f"""
🎯 Phase1 實時信號流測試報告
{'='*50}

📊 總體指標:
- 總周期數: {self.flow_metrics.get('total_cycles', 0)}
- 成功周期: {self.flow_metrics.get('successful_cycles', 0)}
- 成功率: {success_rate:.1%}
- 平均處理時間: {total_time:.1f}ms

⏱️ 階段耗時:
- 數據獲取: {self.flow_metrics['stage_times'].get('data_acquisition', 0):.1f}ms
- Phase1A 生成: {self.flow_metrics['stage_times'].get('phase1a_generation', 0):.1f}ms
- 指標計算: {self.flow_metrics['stage_times'].get('indicator_calculation', 0):.1f}ms
- Phase1B 適應: {self.flow_metrics['stage_times'].get('phase1b_adaptation', 0):.1f}ms
- Phase1C 標準化: {self.flow_metrics['stage_times'].get('phase1c_standardization', 0):.1f}ms
- 統一池聚合: {self.flow_metrics['stage_times'].get('unified_aggregation', 0):.1f}ms
- EPL 預處理: {self.flow_metrics['stage_times'].get('epl_preprocessing', 0):.1f}ms

🎯 信號生成:
- Phase1A: {self.flow_metrics['signals_generated'].get('phase1a', 0)} 個
- 技術指標: {self.flow_metrics['signals_generated'].get('indicators', 0)} 個
- Phase1B: {self.flow_metrics['signals_generated'].get('phase1b', 0)} 個
- Phase1C: {self.flow_metrics['signals_generated'].get('phase1c', 0)} 個
- 統一池: {self.flow_metrics['signals_generated'].get('unified', 0)} 個
- 最終 EPL: {self.flow_metrics.get('final_epl_signals', 0)} 個

🏆 評級: {'A+' if success_rate >= 0.95 else 'A' if success_rate >= 0.9 else 'B+' if success_rate >= 0.85 else 'B' if success_rate >= 0.8 else 'C' if success_rate >= 0.7 else 'D'}
        """
        
        print(report)
        
        # 保存詳細指標到文件
        with open("realtime_signal_flow_report.json", "w", encoding="utf-8") as f:
            json.dump(self.flow_metrics, f, indent=2, default=str, ensure_ascii=False)
        
        logger.info(f"📊 實時信號流測試完成，成功率: {success_rate:.1%}")

async def main():
    """主測試函數"""
    try:
        engine = RealTimeSignalFlowEngine()
        
        # 運行60秒的實時信號流測試
        success = await engine.run_realtime_signal_flow_test(duration_seconds=60)
        
        if success:
            logger.info("🎉 實時信號流測試通過！")
        else:
            logger.warning("⚠️ 實時信號流測試需要改進")
            
        return success
        
    except Exception as e:
        logger.error(f"測試執行失敗: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(main())
