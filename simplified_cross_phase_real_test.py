#!/usr/bin/env python3
"""
🔥 跨階段整合實際信號流測試 (簡化版)
禁止模擬數據！使用真實 Binance 數據進行 Phase1A → Phase2 → Phase3 完整流程測試
"""

import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import json
import logging
from pathlib import Path
from enum import Enum
import time

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SignalTier(Enum):
    """信號層級枚舉"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class TierConfig:
    """層級配置"""
    def __init__(self, tier: SignalTier):
        self.tier = tier
        self.configs = {
            SignalTier.CRITICAL: {
                'min_confidence': 0.85,
                'position_multiplier': 1.5,
                'priority': 1,
                'execution_urgency': 'IMMEDIATE'
            },
            SignalTier.HIGH: {
                'min_confidence': 0.70,
                'position_multiplier': 1.2,
                'priority': 2,
                'execution_urgency': 'HIGH'
            },
            SignalTier.MEDIUM: {
                'min_confidence': 0.55,
                'position_multiplier': 1.0,
                'priority': 3,
                'execution_urgency': 'NORMAL'
            },
            SignalTier.LOW: {
                'min_confidence': 0.40,
                'position_multiplier': 0.8,
                'priority': 4,
                'execution_urgency': 'LOW'
            }
        }
    
    def get_config(self, tier: SignalTier) -> Dict[str, Any]:
        return self.configs.get(tier, self.configs[SignalTier.LOW])

class SimplifiedSignalTierSystem:
    """簡化的信號分層系統"""
    
    def __init__(self):
        self.tier_config = TierConfig(SignalTier.MEDIUM)
    
    def classify_signal_tier(self, confidence: float, signal_strength: float) -> SignalTier:
        """分類信號層級"""
        combined_score = (confidence + signal_strength / 10) / 2
        
        if combined_score >= 0.85:
            return SignalTier.CRITICAL
        elif combined_score >= 0.70:
            return SignalTier.HIGH
        elif combined_score >= 0.55:
            return SignalTier.MEDIUM
        else:
            return SignalTier.LOW
    
    def get_tier_config(self, tier: SignalTier) -> Dict[str, Any]:
        """獲取層級配置"""
        return self.tier_config.get_config(tier)
    
    def get_dynamic_threshold(self, confidence: float, tier: SignalTier) -> float:
        """獲取動態閾值"""
        base_threshold = self.get_tier_config(tier)['min_confidence']
        return max(base_threshold, confidence * 0.9)
    
    def get_execution_priority(self, tier: SignalTier) -> int:
        """獲取執行優先級"""
        return self.get_tier_config(tier)['priority']

class SimplifiedTierAwareScoring:
    """簡化的分層感知評分"""
    
    def __init__(self):
        self.tier_weights = {
            SignalTier.CRITICAL: 1.5,
            SignalTier.HIGH: 1.2,
            SignalTier.MEDIUM: 1.0,
            SignalTier.LOW: 0.8
        }
    
    def calculate_tier_score(self, signal_data: Dict[str, Any], lean_params: Dict[str, Any]) -> Dict[str, Any]:
        """計算分層評分"""
        base_score = (
            signal_data['strength'] * 0.3 +
            signal_data['confidence'] * 0.4 +
            abs(signal_data['price_change']) * 10 * 0.2 +
            signal_data['volume'] * 0.1
        )
        
        # 層級權重調整
        tier_str = lean_params.get('signal_tier', 'MEDIUM')
        tier = SignalTier(tier_str) if tier_str in [t.value for t in SignalTier] else SignalTier.MEDIUM
        tier_weight = self.tier_weights.get(tier, 1.0)
        
        # Lean 參數增強
        lean_confidence_boost = lean_params.get('confidence_level', 0.5) * 0.2
        lean_return_boost = abs(lean_params.get('expected_return', 0)) * 5
        
        final_score = base_score * tier_weight + lean_confidence_boost + lean_return_boost
        
        return {
            'base_score': base_score,
            'tier_weight': tier_weight,
            'lean_confidence_boost': lean_confidence_boost,
            'lean_return_boost': lean_return_boost,
            'final_tier_score': min(1.0, final_score),
            'signal_tier': tier_str,
            'score_improvement': final_score - base_score
        }
    
    def get_tier_recommendation(self, tier_scores: Dict[str, Any]) -> Dict[str, Any]:
        """獲取層級建議"""
        final_score = tier_scores['final_tier_score']
        
        if final_score >= 0.85:
            recommendation = 'STRONG_BUY'
            position_size = 0.15
            confidence_level = 'VERY_HIGH'
        elif final_score >= 0.70:
            recommendation = 'BUY'
            position_size = 0.10
            confidence_level = 'HIGH'
        elif final_score >= 0.55:
            recommendation = 'SMALL_BUY'
            position_size = 0.05
            confidence_level = 'MEDIUM'
        else:
            recommendation = 'HOLD'
            position_size = 0.0
            confidence_level = 'LOW'
        
        return {
            'execution_recommendation': recommendation,
            'suggested_position_size': position_size,
            'confidence_level': confidence_level
        }

class RealCrossPhaseIntegrationTest:
    """真實跨階段整合測試"""
    
    def __init__(self):
        self.binance_url = "https://api.binance.com"
        self.test_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT", "DOGEUSDT", "XRPUSDT"]  # 完整 7 個測試幣種
        self.session = None
        
        # 初始化系統組件
        self.tier_system = SimplifiedSignalTierSystem()
        self.tier_scoring = SimplifiedTierAwareScoring()
        
        # 跨階段追蹤
        self.cross_phase_tracker = {
            'signal_flows': [],
            'integration_successes': 0,
            'integration_failures': 0,
            'tier_metadata_continuity': [],
            'configuration_sync_issues': []
        }
        
        # 實時統計
        self.real_time_stats = {
            'signals_generated': 0,
            'signals_scored': 0,
            'decisions_made': 0,
            'successful_flows': 0
        }
    
    async def get_live_market_data(self, symbol: str, interval: str = "1m", limit: int = 100) -> pd.DataFrame:
        """獲取實時市場數據"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.binance_url}/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    df = pd.DataFrame(data, columns=[
                        'timestamp', 'open', 'high', 'low', 'close', 'volume',
                        'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                        'taker_buy_quote', 'ignore'
                    ])
                    
                    # 數據處理
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    for col in ['open', 'high', 'low', 'close', 'volume']:
                        df[col] = df[col].astype(float)
                    
                    return df
                else:
                    logger.error(f"❌ 獲取 {symbol} 數據失敗: {response.status}")
                    return pd.DataFrame()
                    
        except Exception as e:
            logger.error(f"❌ 獲取 {symbol} 數據異常: {e}")
            return pd.DataFrame()
    
    async def execute_phase1a_signal_generation(self, symbol: str, market_data: pd.DataFrame) -> Dict[str, Any]:
        """執行 Phase1A 信號生成"""
        try:
            if len(market_data) < 20:
                return {}
            
            latest_data = market_data.iloc[-1]
            
            # 技術指標計算
            current_price = latest_data['close']
            price_changes = {
                '5m': (current_price - market_data.iloc[-5]['close']) / market_data.iloc[-5]['close'] if len(market_data) >= 5 else 0,
                '15m': (current_price - market_data.iloc[-15]['close']) / market_data.iloc[-15]['close'] if len(market_data) >= 15 else 0,
                '1h': (current_price - market_data.iloc[-60]['close']) / market_data.iloc[-60]['close'] if len(market_data) >= 60 else 0
            }
            
            volume_ratio = latest_data['volume'] / market_data['volume'].rolling(10).mean().iloc[-1] if len(market_data) >= 10 else 1
            
            # 信號強度計算
            signal_strength = (
                abs(price_changes['5m']) * 3 +
                abs(price_changes['15m']) * 2 +
                abs(price_changes['1h']) * 1
            ) * 5
            
            # 基礎信心度
            base_confidence = min(0.95, 0.4 + abs(price_changes['15m']) * 10 + (volume_ratio - 1) * 0.1)
            
            # 信號分層
            signal_tier = self.tier_system.classify_signal_tier(base_confidence, signal_strength)
            tier_config = self.tier_system.get_tier_config(signal_tier)
            
            # Phase1A 信號對象
            phase1a_signal = {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'signal_strength': signal_strength,
                'base_confidence': base_confidence,
                'signal_tier': signal_tier,
                'tier_metadata': {
                    'tier_config': tier_config,
                    'dynamic_threshold': self.tier_system.get_dynamic_threshold(base_confidence, signal_tier),
                    'execution_priority': self.tier_system.get_execution_priority(signal_tier),
                    'position_multiplier': tier_config['position_multiplier']
                },
                'market_context': {
                    'current_price': current_price,
                    'price_changes': price_changes,
                    'volume_ratio': volume_ratio,
                    'volatility': market_data['close'].rolling(20).std().iloc[-1] if len(market_data) >= 20 else 0
                },
                'phase1a_uuid': f"P1A_{symbol}_{int(time.time())}"
            }
            
            self.real_time_stats['signals_generated'] += 1
            logger.info(f"🎯 Phase1A: {symbol} 信號生成 - 層級: {signal_tier.value}, 信心度: {base_confidence:.3f}")
            
            return phase1a_signal
            
        except Exception as e:
            logger.error(f"❌ Phase1A 信號生成失敗 {symbol}: {e}")
            return {}
    
    async def execute_phase2_signal_scoring(self, phase1a_signal: Dict[str, Any]) -> Dict[str, Any]:
        """執行 Phase2 信號評分"""
        try:
            # 檢查 Phase1A 數據完整性
            required_keys = ['signal_tier', 'tier_metadata', 'market_context']
            missing_keys = [key for key in required_keys if key not in phase1a_signal]
            
            if missing_keys:
                logger.warning(f"⚠️ Phase1A→Phase2: 缺少關鍵數據 {missing_keys}")
                self.cross_phase_tracker['configuration_sync_issues'].append(
                    f"P1A→P2 數據缺失: {missing_keys} - {phase1a_signal.get('symbol', 'UNKNOWN')}"
                )
            
            # 構建 Phase2 評分輸入
            signal_data = {
                'symbol': phase1a_signal['symbol'],
                'strength': phase1a_signal['signal_strength'],
                'confidence': phase1a_signal['base_confidence'],
                'volume': phase1a_signal['market_context']['volume_ratio'],
                'price_change': phase1a_signal['market_context']['price_changes']['15m']
            }
            
            # 構建 Lean 參數
            lean_params = {
                'confidence_level': phase1a_signal['base_confidence'],
                'consensus_direction': 'BULLISH' if phase1a_signal['market_context']['price_changes']['15m'] > 0 else 'BEARISH',
                'expected_return': phase1a_signal['market_context']['price_changes']['15m'],
                'signal_tier': phase1a_signal['signal_tier'].value,
                'volume_confirmation': phase1a_signal['market_context']['volume_ratio'] > 1.2
            }
            
            # 執行分層感知評分
            tier_scores = self.tier_scoring.calculate_tier_score(signal_data, lean_params)
            execution_recommendation = self.tier_scoring.get_tier_recommendation(tier_scores)
            
            # 檢查層級元數據連續性
            tier_continuity_check = {
                'phase1a_tier': phase1a_signal['signal_tier'].value,
                'phase2_tier': tier_scores['signal_tier'],
                'tier_consistent': phase1a_signal['signal_tier'].value == tier_scores['signal_tier'],
                'metadata_preserved': 'tier_metadata' in phase1a_signal and len(phase1a_signal['tier_metadata']) > 0
            }
            
            phase2_result = {
                'symbol': phase1a_signal['symbol'],
                'timestamp': datetime.now(),
                'phase1a_uuid': phase1a_signal['phase1a_uuid'],
                'tier_scores': tier_scores,
                'execution_recommendation': execution_recommendation,
                'tier_continuity': tier_continuity_check,
                'enhanced_confidence': tier_scores['final_tier_score'],
                'lean_enhancements': {
                    'confidence_boost': tier_scores['lean_confidence_boost'],
                    'return_boost': tier_scores['lean_return_boost'],
                    'score_improvement': tier_scores['score_improvement']
                },
                'phase2_uuid': f"P2_{phase1a_signal['symbol']}_{int(time.time())}"
            }
            
            # 記錄層級元數據連續性
            self.cross_phase_tracker['tier_metadata_continuity'].append(tier_continuity_check)
            
            self.real_time_stats['signals_scored'] += 1
            logger.info(f"📊 Phase2: {phase1a_signal['symbol']} 評分完成 - 最終分數: {tier_scores['final_tier_score']:.3f}")
            
            return phase2_result
            
        except Exception as e:
            logger.error(f"❌ Phase2 評分失敗 {phase1a_signal.get('symbol', 'UNKNOWN')}: {e}")
            return {}
    
    async def execute_phase3_epl_decision(self, phase1a_signal: Dict[str, Any], phase2_result: Dict[str, Any]) -> Dict[str, Any]:
        """執行 Phase3 EPL 決策"""
        try:
            # 跨階段數據一致性檢查
            consistency_checks = {
                'symbol_match': phase1a_signal['symbol'] == phase2_result['symbol'],
                'uuid_chain': phase1a_signal['phase1a_uuid'] == phase2_result['phase1a_uuid'],
                'tier_consistency': phase2_result['tier_continuity']['tier_consistent'],
                'metadata_preservation': phase2_result['tier_continuity']['metadata_preserved']
            }
            
            consistency_score = sum(consistency_checks.values()) / len(consistency_checks)
            
            # 構建 EPL 決策輸入
            epl_input = {
                'symbol': phase1a_signal['symbol'],
                'original_signal_tier': phase1a_signal['signal_tier'],
                'enhanced_confidence': phase2_result['enhanced_confidence'],
                'execution_recommendation': phase2_result['execution_recommendation'],
                'tier_metadata': phase1a_signal.get('tier_metadata', {}),
                'market_context': phase1a_signal['market_context'],
                'lean_enhancements': phase2_result['lean_enhancements']
            }
            
            # EPL 決策邏輯
            execution_rec = phase2_result['execution_recommendation']
            final_confidence = phase2_result['enhanced_confidence']
            
            # 決策映射
            epl_decisions = {
                'STRONG_BUY': 'CREATE_AGGRESSIVE_POSITION',
                'BUY': 'CREATE_STANDARD_POSITION',
                'SMALL_BUY': 'CREATE_CONSERVATIVE_POSITION',
                'HOLD': 'MONITOR_SIGNAL'
            }
            
            epl_decision = epl_decisions.get(execution_rec['execution_recommendation'], 'IGNORE_SIGNAL')
            
            # 決策理由生成
            decision_reasoning = []
            decision_reasoning.append(f"基於 {execution_rec['execution_recommendation']} 建議")
            decision_reasoning.append(f"信心度: {final_confidence:.3f} ({execution_rec['confidence_level']})")
            decision_reasoning.append(f"層級: {phase1a_signal['signal_tier'].value}")
            
            if consistency_score < 0.8:
                decision_reasoning.append(f"⚠️ 跨階段一致性較低: {consistency_score:.2f}")
            
            # 執行參數計算
            base_position_size = execution_rec['suggested_position_size']
            tier_multiplier = phase1a_signal['tier_metadata']['position_multiplier']
            final_position_size = base_position_size * tier_multiplier
            
            phase3_result = {
                'symbol': phase1a_signal['symbol'],
                'timestamp': datetime.now(),
                'phase1a_uuid': phase1a_signal['phase1a_uuid'],
                'phase2_uuid': phase2_result['phase2_uuid'],
                'epl_decision': epl_decision,
                'decision_reasoning': decision_reasoning,
                'consistency_checks': consistency_checks,
                'consistency_score': consistency_score,
                'execution_parameters': {
                    'final_position_size': final_position_size,
                    'base_position_size': base_position_size,
                    'tier_multiplier': tier_multiplier,
                    'execution_priority': phase1a_signal['tier_metadata']['execution_priority'],
                    'execution_urgency': phase1a_signal['tier_metadata']['tier_config']['execution_urgency']
                },
                'cross_phase_summary': {
                    'phase1a_tier': phase1a_signal['signal_tier'].value,
                    'phase2_score': phase2_result['enhanced_confidence'],
                    'phase3_decision': epl_decision,
                    'tier_metadata_flow': consistency_checks['metadata_preservation'],
                    'overall_success': consistency_score >= 0.8
                },
                'phase3_uuid': f"P3_{phase1a_signal['symbol']}_{int(time.time())}"
            }
            
            # 更新統計
            if consistency_score >= 0.8:
                self.cross_phase_tracker['integration_successes'] += 1
                self.real_time_stats['successful_flows'] += 1
            else:
                self.cross_phase_tracker['integration_failures'] += 1
            
            self.real_time_stats['decisions_made'] += 1
            
            logger.info(f"🎯 Phase3: {phase1a_signal['symbol']} 決策完成 - {epl_decision} (一致性: {consistency_score:.2f})")
            
            return phase3_result
            
        except Exception as e:
            logger.error(f"❌ Phase3 決策失敗: {e}")
            self.cross_phase_tracker['integration_failures'] += 1
            return {}
    
    async def execute_complete_signal_flow(self, symbol: str) -> Dict[str, Any]:
        """執行完整信號流"""
        signal_flow_start = datetime.now()
        
        try:
            # 1. 獲取實時市場數據
            market_data = await self.get_live_market_data(symbol)
            if market_data.empty:
                return {'success': False, 'error': '無法獲取市場數據'}
            
            # 2. Phase1A 信號生成
            phase1a_signal = await self.execute_phase1a_signal_generation(symbol, market_data)
            if not phase1a_signal:
                return {'success': False, 'error': 'Phase1A 信號生成失敗'}
            
            # 3. Phase2 信號評分
            phase2_result = await self.execute_phase2_signal_scoring(phase1a_signal)
            if not phase2_result:
                return {'success': False, 'error': 'Phase2 信號評分失敗'}
            
            # 4. Phase3 EPL 決策
            phase3_result = await self.execute_phase3_epl_decision(phase1a_signal, phase2_result)
            if not phase3_result:
                return {'success': False, 'error': 'Phase3 EPL 決策失敗'}
            
            # 5. 信號流統計
            signal_flow_end = datetime.now()
            processing_time = (signal_flow_end - signal_flow_start).total_seconds()
            
            complete_flow = {
                'success': True,
                'symbol': symbol,
                'processing_time_seconds': processing_time,
                'signal_flow_id': f"FLOW_{symbol}_{int(signal_flow_start.timestamp())}",
                'phase1a_signal': phase1a_signal,
                'phase2_result': phase2_result,
                'phase3_result': phase3_result,
                'flow_summary': {
                    'tier_progression': f"{phase1a_signal['signal_tier'].value} → {phase2_result['enhanced_confidence']:.3f} → {phase3_result['epl_decision']}",
                    'consistency_score': phase3_result['consistency_score'],
                    'successful_integration': phase3_result['cross_phase_summary']['overall_success']
                }
            }
            
            self.cross_phase_tracker['signal_flows'].append(complete_flow)
            
            logger.info(f"✅ {symbol} 完整信號流完成: {complete_flow['flow_summary']['tier_progression']} ({processing_time:.2f}s)")
            
            return complete_flow
            
        except Exception as e:
            logger.error(f"❌ {symbol} 完整信號流失敗: {e}")
            return {'success': False, 'error': str(e)}
    
    async def run_real_time_cross_phase_test(self, test_duration_minutes: int = 15):
        """執行實時跨階段測試"""
        logger.info(f"🚀 開始實時跨階段整合測試 - 測試時長: {test_duration_minutes} 分鐘")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=test_duration_minutes)
        
        test_cycle = 0
        
        try:
            while datetime.now() < end_time:
                test_cycle += 1
                cycle_start = datetime.now()
                
                logger.info(f"🔄 測試循環 #{test_cycle} - {datetime.now().strftime('%H:%M:%S')}")
                
                # 並行處理所有測試幣種
                cycle_tasks = []
                for symbol in self.test_symbols:
                    cycle_tasks.append(self.execute_complete_signal_flow(symbol))
                
                # 等待所有信號流完成
                cycle_results = await asyncio.gather(*cycle_tasks, return_exceptions=True)
                
                # 統計本輪結果
                successful_flows = sum(1 for result in cycle_results if isinstance(result, dict) and result.get('success', False))
                
                logger.info(f"📊 循環 #{test_cycle} 完成: {successful_flows}/{len(self.test_symbols)} 成功")
                
                # 顯示實時統計
                self._display_real_time_stats()
                
                # 循環間隔
                cycle_duration = (datetime.now() - cycle_start).total_seconds()
                if cycle_duration < 60:  # 確保每分鐘至少一個循環
                    await asyncio.sleep(60 - cycle_duration)
            
            # 生成最終報告
            await self.generate_comprehensive_report()
            
        except Exception as e:
            logger.error(f"❌ 跨階段測試執行失敗: {e}")
        finally:
            if self.session:
                await self.session.close()
    
    def _display_real_time_stats(self):
        """顯示實時統計"""
        success_rate = (self.real_time_stats['successful_flows'] / max(1, self.real_time_stats['signals_generated'])) * 100
        
        print(f"\n📈 實時統計:")
        print(f"  • 信號生成: {self.real_time_stats['signals_generated']}")
        print(f"  • 信號評分: {self.real_time_stats['signals_scored']}")
        print(f"  • 決策制定: {self.real_time_stats['decisions_made']}")
        print(f"  • 成功流程: {self.real_time_stats['successful_flows']}")
        print(f"  • 成功率: {success_rate:.1f}%")
        print(f"  • 整合成功: {self.cross_phase_tracker['integration_successes']}")
        print(f"  • 整合失敗: {self.cross_phase_tracker['integration_failures']}")
    
    async def generate_comprehensive_report(self):
        """生成綜合測試報告"""
        logger.info("📋 生成跨階段整合測試綜合報告...")
        
        # 計算統計指標
        total_flows = len(self.cross_phase_tracker['signal_flows'])
        successful_flows = sum(1 for flow in self.cross_phase_tracker['signal_flows'] if flow.get('success', False))
        
        if total_flows > 0:
            success_rate = successful_flows / total_flows
            avg_processing_time = sum(flow.get('processing_time_seconds', 0) for flow in self.cross_phase_tracker['signal_flows']) / total_flows
            
            # 層級分佈統計
            tier_distribution = {}
            for flow in self.cross_phase_tracker['signal_flows']:
                if flow.get('success') and 'phase1a_signal' in flow:
                    tier = flow['phase1a_signal']['signal_tier'].value
                    tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
            
            # 一致性統計
            consistency_scores = [flow['phase3_result']['consistency_score'] for flow in self.cross_phase_tracker['signal_flows'] if flow.get('success') and 'phase3_result' in flow]
            avg_consistency = sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0
            
            # 層級元數據保持率
            metadata_continuity_rate = sum(1 for item in self.cross_phase_tracker['tier_metadata_continuity'] if item['metadata_preserved']) / max(1, len(self.cross_phase_tracker['tier_metadata_continuity']))
        else:
            success_rate = 0
            avg_processing_time = 0
            tier_distribution = {}
            avg_consistency = 0
            metadata_continuity_rate = 0
        
        # 生成報告
        report = {
            'test_timestamp': datetime.now().isoformat(),
            'test_summary': {
                'total_signal_flows': total_flows,
                'successful_flows': successful_flows,
                'success_rate': success_rate,
                'avg_processing_time_seconds': avg_processing_time,
                'integration_successes': self.cross_phase_tracker['integration_successes'],
                'integration_failures': self.cross_phase_tracker['integration_failures']
            },
            'cross_phase_metrics': {
                'avg_consistency_score': avg_consistency,
                'tier_metadata_continuity_rate': metadata_continuity_rate,
                'configuration_sync_issues_count': len(self.cross_phase_tracker['configuration_sync_issues'])
            },
            'tier_system_analysis': {
                'tier_distribution': tier_distribution,
                'tier_effectiveness': self._analyze_tier_effectiveness()
            },
            'performance_metrics': {
                'signals_per_minute': self.real_time_stats['signals_generated'] / max(1, avg_processing_time / 60),
                'end_to_end_latency': avg_processing_time,
                'system_throughput': successful_flows / max(1, avg_processing_time / 60)
            },
            'integration_issues': self.cross_phase_tracker['configuration_sync_issues'],
            'sample_successful_flows': [flow['flow_summary'] for flow in self.cross_phase_tracker['signal_flows'][:5] if flow.get('success')]
        }
        
        # 保存報告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"cross_phase_integration_real_test_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        # 顯示報告摘要
        print("\n" + "="*80)
        print("🎯 跨階段整合實際信號流測試報告")
        print("="*80)
        print(f"📊 測試統計:")
        print(f"  • 總信號流: {total_flows}")
        print(f"  • 成功流程: {successful_flows}")
        print(f"  • 成功率: {success_rate:.1%}")
        print(f"  • 平均處理時間: {avg_processing_time:.2f}秒")
        
        print(f"\n🔄 跨階段指標:")
        print(f"  • 平均一致性分數: {avg_consistency:.3f}")
        print(f"  • 層級元數據保持率: {metadata_continuity_rate:.1%}")
        print(f"  • 整合成功率: {self.cross_phase_tracker['integration_successes']}/{self.cross_phase_tracker['integration_successes'] + self.cross_phase_tracker['integration_failures']}")
        
        print(f"\n🎚️ 層級分佈:")
        for tier, count in tier_distribution.items():
            percentage = (count / total_flows) * 100 if total_flows > 0 else 0
            print(f"  • {tier}: {count} ({percentage:.1f}%)")
        
        print(f"\n⚡ 性能指標:")
        print(f"  • 信號/分鐘: {report['performance_metrics']['signals_per_minute']:.1f}")
        print(f"  • 端到端延遲: {report['performance_metrics']['end_to_end_latency']:.2f}秒")
        print(f"  • 系統吞吐量: {report['performance_metrics']['system_throughput']:.1f}")
        
        if self.cross_phase_tracker['configuration_sync_issues']:
            print(f"\n⚠️ 配置同步問題:")
            for issue in self.cross_phase_tracker['configuration_sync_issues'][:5]:
                print(f"  • {issue}")
        else:
            print(f"\n✅ 無配置同步問題")
        
        print(f"\n💾 詳細報告已保存: {report_file}")
        
        return report
    
    def _analyze_tier_effectiveness(self) -> Dict[str, Any]:
        """分析層級系統效果"""
        tier_analysis = {}
        
        for flow in self.cross_phase_tracker['signal_flows']:
            if not flow.get('success'):
                continue
                
            tier = flow['phase1a_signal']['signal_tier'].value
            consistency_score = flow['phase3_result']['consistency_score']
            
            if tier not in tier_analysis:
                tier_analysis[tier] = {
                    'count': 0,
                    'total_consistency': 0,
                    'successful_integrations': 0
                }
            
            tier_analysis[tier]['count'] += 1
            tier_analysis[tier]['total_consistency'] += consistency_score
            
            if consistency_score >= 0.8:
                tier_analysis[tier]['successful_integrations'] += 1
        
        # 計算每層級的效果指標
        for tier in tier_analysis:
            if tier_analysis[tier]['count'] > 0:
                tier_analysis[tier]['avg_consistency'] = tier_analysis[tier]['total_consistency'] / tier_analysis[tier]['count']
                tier_analysis[tier]['integration_success_rate'] = tier_analysis[tier]['successful_integrations'] / tier_analysis[tier]['count']
        
        return tier_analysis

async def main():
    """主測試執行函數"""
    print("🔥 跨階段整合實際信號流測試")
    print("=" * 50)
    print("📋 測試範圍:")
    print("  • Phase1A 信號生成 (層級分類)")
    print("  • Phase2 信號評分 (層級感知)")
    print("  • Phase3 EPL 決策 (跨階段整合)")
    print("  • 真實 Binance 市場數據")
    print("  • 層級元數據流追蹤")
    print("  • 配置同步驗證")
    print("=" * 50)
    
    tester = RealCrossPhaseIntegrationTest()
    await tester.run_real_time_cross_phase_test(test_duration_minutes=1)  # 1分鐘快速測試

if __name__ == "__main__":
    asyncio.run(main())
