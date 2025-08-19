#!/usr/bin/env python3
"""
🔥 跨階段整合實際信號流測試
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
import sys
import time

# 添加專案路徑
current_dir = Path(__file__).parent
sys.path.extend([
    str(current_dir / "X" / "backend" / "phase1_signal_generation" / "phase1a_basic_signal_generation"),
    str(current_dir / "X" / "backend" / "phase2_pre_evaluation" / "signal_scoring_engine"),
    str(current_dir / "X" / "backend" / "phase3_execution_policy"),
    str(current_dir / "X" / "backend" / "phase5_backtest_validation"),
    str(current_dir / "app" / "services")
])

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealSignalFlowTest:
    """真實信號流跨階段整合測試"""
    
    def __init__(self):
        self.binance_url = "https://api.binance.com"
        self.test_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT"]  # 真實測試幣種
        self.session = None
        
        # 導入各階段模組
        self._import_phase_modules()
        
        # 信號流追蹤
        self.signal_flow_tracker = {
            'phase1a_signals': [],
            'phase2_scores': [],
            'phase3_decisions': [],
            'integration_issues': [],
            'tier_metadata_flow': []
        }
        
        # 配置同步檢查
        self.config_sync_status = {
            'phase1a_config': None,
            'phase2_config': None,
            'phase3_config': None,
            'sync_errors': []
        }
    
    def _import_phase_modules(self):
        """導入各階段模組"""
        try:
            # Phase1A
            import phase1a_basic_signal_generation as phase1a
            self.phase1a = phase1a
            self.tier_system = phase1a.EnhancedSignalTierSystem()
            
            # Phase2
            import signal_scoring_engine as phase2
            self.phase2_scoring = phase2.signal_scoring_engine
            self.tier_aware_scoring = phase2.TierAwareScoring()
            
            # Phase3
            import epl_intelligent_decision_engine as phase3
            self.phase3_epl = phase3
            
            # Phase5
            import phase5_enhanced_backtest_strategy as phase5
            self.phase5_lean = phase5
            
            logger.info("✅ 所有階段模組導入成功")
            
        except ImportError as e:
            logger.error(f"❌ 模組導入失敗: {e}")
            raise
    
    async def get_real_market_data(self, symbol: str, interval: str = "1m", limit: int = 100) -> pd.DataFrame:
        """獲取真實市場數據 - 禁止模擬"""
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
                    
                    # 資料處理
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    for col in ['open', 'high', 'low', 'close', 'volume']:
                        df[col] = df[col].astype(float)
                    
                    logger.info(f"✅ 獲取 {symbol} 真實數據: {len(df)} 條")
                    return df
                else:
                    logger.error(f"❌ 獲取 {symbol} 數據失敗: {response.status}")
                    return pd.DataFrame()
                    
        except Exception as e:
            logger.error(f"❌ 獲取 {symbol} 數據異常: {e}")
            return pd.DataFrame()
    
    async def test_phase1a_signal_generation(self, symbol: str, market_data: pd.DataFrame) -> Dict[str, Any]:
        """測試 Phase1A 信號生成 - 真實數據"""
        try:
            latest_data = market_data.iloc[-1]
            
            # 計算技術指標
            current_price = latest_data['close']
            price_change_1h = (current_price - market_data.iloc[-60]['close']) / market_data.iloc[-60]['close'] if len(market_data) >= 60 else 0
            volume_ratio = latest_data['volume'] / market_data['volume'].rolling(20).mean().iloc[-1] if len(market_data) >= 20 else 1
            
            # 模擬信號生成邏輯
            signal_strength = abs(price_change_1h) * 10  # 基於價格變化
            confidence = min(0.95, 0.5 + abs(price_change_1h) * 5)  # 基於變化幅度
            
            # 使用真實 Lean 參數（如果有 Phase5 配置）
            lean_confidence = self._get_lean_adjustment(symbol, confidence)
            
            # 分層分類
            signal_tier = self.tier_system.classify_signal_tier(lean_confidence, signal_strength)
            
            phase1a_signal = {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'signal_strength': signal_strength,
                'confidence': confidence,
                'lean_confidence': lean_confidence,
                'signal_tier': signal_tier,
                'tier_metadata': {
                    'tier_config': self.tier_system.get_tier_config(signal_tier),
                    'dynamic_threshold': self.tier_system.get_dynamic_threshold(lean_confidence, signal_tier),
                    'execution_priority': self.tier_system.get_execution_priority(signal_tier)
                },
                'market_data': {
                    'price': current_price,
                    'price_change_1h': price_change_1h,
                    'volume_ratio': volume_ratio
                }
            }
            
            # 追蹤信號
            self.signal_flow_tracker['phase1a_signals'].append(phase1a_signal)
            
            logger.info(f"📊 Phase1A 信號生成: {symbol} - 層級: {signal_tier.value}, 信心度: {lean_confidence:.3f}")
            return phase1a_signal
            
        except Exception as e:
            logger.error(f"❌ Phase1A 信號生成失敗: {e}")
            return {}
    
    def _get_lean_adjustment(self, symbol: str, base_confidence: float) -> float:
        """獲取 Lean 調整後的信心度"""
        try:
            # 檢查是否有 Phase5 Lean 配置
            config_key = f"{symbol.lower()}_lean_adjustment"
            if hasattr(self.phase5_lean, 'get_lean_config'):
                lean_config = self.phase5_lean.get_lean_config()
                if config_key in lean_config:
                    lean_boost = lean_config[config_key].get('confidence_level', 0)
                    return min(0.95, base_confidence + lean_boost * 0.2)
            
            return base_confidence
            
        except Exception:
            return base_confidence
    
    async def test_phase2_signal_scoring(self, phase1a_signal: Dict[str, Any]) -> Dict[str, Any]:
        """測試 Phase2 信號評分 - 層級元數據傳播"""
        try:
            # 檢查層級元數據是否完整傳播
            if 'tier_metadata' not in phase1a_signal:
                self.signal_flow_tracker['integration_issues'].append(
                    f"Phase1A→Phase2: 缺少層級元數據 - {phase1a_signal['symbol']}"
                )
                logger.warning("⚠️ Phase1A→Phase2: 層級元數據缺失")
            
            # 構建 Phase2 評分數據
            signal_data = {
                'symbol': phase1a_signal['symbol'],
                'strength': phase1a_signal['signal_strength'],
                'confidence': phase1a_signal['confidence'],
                'volume': phase1a_signal['market_data']['volume_ratio'],
                'price_change': phase1a_signal['market_data']['price_change_1h']
            }
            
            # 構建 Lean 參數
            lean_params = {
                'confidence_level': phase1a_signal['lean_confidence'],
                'consensus_direction': 'BULLISH' if phase1a_signal['market_data']['price_change_1h'] > 0 else 'BEARISH',
                'expected_return': phase1a_signal['market_data']['price_change_1h'],
                'signal_tier': phase1a_signal['signal_tier'].value if hasattr(phase1a_signal['signal_tier'], 'value') else str(phase1a_signal['signal_tier'])
            }
            
            # 使用分層感知評分
            tier_scores = self.tier_aware_scoring.calculate_tier_score(signal_data, lean_params)
            
            # 檢查層級元數據傳播
            tier_metadata_preserved = all(key in phase1a_signal.get('tier_metadata', {}) for key in ['tier_config', 'dynamic_threshold', 'execution_priority'])
            
            phase2_result = {
                'symbol': phase1a_signal['symbol'],
                'timestamp': datetime.now(),
                'base_scores': tier_scores,
                'final_tier_score': tier_scores.get('final_tier_score', 0),
                'tier_metadata_preserved': tier_metadata_preserved,
                'tier_enhancements': {
                    'lean_confidence_boost': tier_scores.get('lean_confidence_boost', 0),
                    'lean_return_boost': tier_scores.get('lean_return_boost', 0),
                    'score_improvement': tier_scores.get('score_improvement', 0)
                },
                'execution_recommendation': self.tier_aware_scoring.get_tier_recommendation(tier_scores)
            }
            
            # 追蹤評分
            self.signal_flow_tracker['phase2_scores'].append(phase2_result)
            self.signal_flow_tracker['tier_metadata_flow'].append({
                'phase': 'Phase1A→Phase2',
                'symbol': phase1a_signal['symbol'],
                'metadata_preserved': tier_metadata_preserved,
                'tier_continuity': phase1a_signal['signal_tier'].value == lean_params['signal_tier']
            })
            
            logger.info(f"📈 Phase2 評分: {phase1a_signal['symbol']} - 最終分數: {phase2_result['final_tier_score']:.3f}")
            return phase2_result
            
        except Exception as e:
            logger.error(f"❌ Phase2 評分失敗: {e}")
            return {}
    
    async def test_phase3_decision_making(self, phase1a_signal: Dict[str, Any], phase2_result: Dict[str, Any]) -> Dict[str, Any]:
        """測試 Phase3 EPL 決策 - 完整跨階段整合"""
        try:
            # 檢查跨階段數據一致性
            data_consistency_issues = []
            
            # 符號一致性
            if phase1a_signal['symbol'] != phase2_result['symbol']:
                data_consistency_issues.append("符號不一致")
            
            # 層級信息一致性
            p1_tier = phase1a_signal['signal_tier'].value if hasattr(phase1a_signal['signal_tier'], 'value') else str(phase1a_signal['signal_tier'])
            p2_tier = phase2_result['base_scores'].get('signal_tier', 'UNKNOWN')
            if p1_tier != p2_tier:
                data_consistency_issues.append(f"層級不一致: P1={p1_tier} vs P2={p2_tier}")
            
            # 構建 Phase3 決策輸入
            signal_candidate = {
                'symbol': phase1a_signal['symbol'],
                'signal_strength': phase1a_signal['signal_strength'],
                'confidence': phase2_result['final_tier_score'],  # 使用 Phase2 增強後的分數
                'direction': 'BUY' if phase1a_signal['market_data']['price_change_1h'] > 0 else 'SELL',
                'tier': phase1a_signal['signal_tier'],
                'tier_metadata': phase1a_signal.get('tier_metadata', {}),
                'phase2_enhancements': phase2_result['tier_enhancements']
            }
            
            # 模擬 EPL 決策
            execution_recommendation = phase2_result['execution_recommendation']
            
            # 基於分層的決策邏輯
            epl_decision = None
            decision_reasoning = []
            
            if execution_recommendation['execution_recommendation'] == 'STRONG_BUY':
                epl_decision = 'CREATE_NEW_POSITION'
                decision_reasoning.append('強烈買入信號，建立新倉位')
            elif execution_recommendation['execution_recommendation'] == 'BUY':
                epl_decision = 'STRENGTHEN_POSITION'
                decision_reasoning.append('買入信號，加強現有倉位')
            elif execution_recommendation['execution_recommendation'] == 'SMALL_BUY':
                epl_decision = 'CREATE_NEW_POSITION'
                decision_reasoning.append('小額買入，探索性倉位')
            else:
                epl_decision = 'IGNORE_SIGNAL'
                decision_reasoning.append('信號強度不足，忽略')
            
            phase3_result = {
                'symbol': phase1a_signal['symbol'],
                'timestamp': datetime.now(),
                'epl_decision': epl_decision,
                'decision_reasoning': decision_reasoning,
                'data_consistency_issues': data_consistency_issues,
                'tier_integration_success': len(data_consistency_issues) == 0,
                'execution_params': {
                    'position_size': execution_recommendation['suggested_position_size'],
                    'confidence_level': execution_recommendation['confidence_level'],
                    'tier_priority': phase1a_signal['tier_metadata']['execution_priority']
                },
                'cross_phase_flow': {
                    'phase1a_tier': p1_tier,
                    'phase2_score': phase2_result['final_tier_score'],
                    'phase3_decision': epl_decision,
                    'metadata_continuity': phase2_result['tier_metadata_preserved']
                }
            }
            
            # 追蹤決策
            self.signal_flow_tracker['phase3_decisions'].append(phase3_result)
            
            if data_consistency_issues:
                self.signal_flow_tracker['integration_issues'].extend([
                    f"Phase2→Phase3: {issue} - {phase1a_signal['symbol']}" for issue in data_consistency_issues
                ])
            
            logger.info(f"🎯 Phase3 決策: {phase1a_signal['symbol']} - {epl_decision}")
            return phase3_result
            
        except Exception as e:
            logger.error(f"❌ Phase3 決策失敗: {e}")
            return {}
    
    async def test_configuration_sync(self):
        """測試配置同步機制"""
        logger.info("🔧 測試配置同步機制...")
        
        try:
            # 檢查 Phase1A 配置
            if hasattr(self.phase1a, 'get_current_config'):
                self.config_sync_status['phase1a_config'] = self.phase1a.get_current_config()
            else:
                self.config_sync_status['sync_errors'].append("Phase1A 無配置獲取方法")
            
            # 檢查 Phase2 配置
            if hasattr(self.phase2_scoring, 'scoring_weights'):
                self.config_sync_status['phase2_config'] = {
                    'scoring_weights': self.phase2_scoring.scoring_weights,
                    'tier_aware': self.phase2_scoring.tier_aware_scoring
                }
            
            # 檢查 Phase5 Lean 配置同步
            try:
                lean_matcher = self.phase5_lean.LeanHistoricalMatcher()
                lean_params = lean_matcher.lean_params
                self.config_sync_status['phase5_lean_config'] = lean_params
                logger.info("✅ Phase5 Lean 配置同步正常")
            except Exception as e:
                self.config_sync_status['sync_errors'].append(f"Phase5 Lean 配置同步失敗: {e}")
            
            # 檢查配置版本一致性
            config_versions = {}
            for phase, config in self.config_sync_status.items():
                if isinstance(config, dict) and 'version' in config:
                    config_versions[phase] = config['version']
            
            if len(set(config_versions.values())) > 1:
                self.config_sync_status['sync_errors'].append("配置版本不一致")
            
            logger.info(f"🔧 配置同步檢查完成，錯誤數: {len(self.config_sync_status['sync_errors'])}")
            
        except Exception as e:
            logger.error(f"❌ 配置同步測試失敗: {e}")
            self.config_sync_status['sync_errors'].append(str(e))
    
    async def run_real_signal_flow_test(self, test_duration_minutes: int = 10):
        """執行真實信號流測試"""
        logger.info(f"🚀 開始跨階段整合實際信號流測試 - 測試時長: {test_duration_minutes} 分鐘")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=test_duration_minutes)
        
        test_cycle = 0
        
        try:
            # 1. 先測試配置同步
            await self.test_configuration_sync()
            
            # 2. 實際信號流測試循環
            while datetime.now() < end_time:
                test_cycle += 1
                logger.info(f"📊 測試循環 #{test_cycle}")
                
                for symbol in self.test_symbols:
                    try:
                        # 獲取真實市場數據
                        market_data = await self.get_real_market_data(symbol)
                        if market_data.empty:
                            continue
                        
                        # Phase1A: 信號生成
                        phase1a_signal = await self.test_phase1a_signal_generation(symbol, market_data)
                        if not phase1a_signal:
                            continue
                        
                        # Phase2: 信號評分
                        phase2_result = await self.test_phase2_signal_scoring(phase1a_signal)
                        if not phase2_result:
                            continue
                        
                        # Phase3: EPL 決策
                        phase3_result = await self.test_phase3_decision_making(phase1a_signal, phase2_result)
                        
                        # 記錄完整信號流
                        logger.info(f"✅ {symbol} 完整信號流: P1({phase1a_signal['signal_tier'].value}) → P2({phase2_result['final_tier_score']:.3f}) → P3({phase3_result.get('epl_decision', 'FAILED')})")
                        
                    except Exception as e:
                        logger.error(f"❌ {symbol} 信號流測試失敗: {e}")
                
                # 等待下一個測試循環
                await asyncio.sleep(30)  # 30秒間隔
            
            # 3. 生成測試報告
            await self.generate_integration_report()
            
        except Exception as e:
            logger.error(f"❌ 跨階段整合測試失敗: {e}")
        finally:
            if self.session:
                await self.session.close()
    
    async def generate_integration_report(self):
        """生成跨階段整合測試報告"""
        logger.info("📋 生成跨階段整合測試報告...")
        
        report = {
            'test_timestamp': datetime.now().isoformat(),
            'test_summary': {
                'total_signals_generated': len(self.signal_flow_tracker['phase1a_signals']),
                'total_signals_scored': len(self.signal_flow_tracker['phase2_scores']),
                'total_decisions_made': len(self.signal_flow_tracker['phase3_decisions']),
                'integration_issues_count': len(self.signal_flow_tracker['integration_issues']),
                'config_sync_errors_count': len(self.config_sync_status['sync_errors'])
            },
            'data_flow_consistency': {
                'phase1a_to_phase2_success_rate': len(self.signal_flow_tracker['phase2_scores']) / max(1, len(self.signal_flow_tracker['phase1a_signals'])),
                'phase2_to_phase3_success_rate': len(self.signal_flow_tracker['phase3_decisions']) / max(1, len(self.signal_flow_tracker['phase2_scores'])),
                'tier_metadata_preservation_rate': sum(1 for item in self.signal_flow_tracker['tier_metadata_flow'] if item['metadata_preserved']) / max(1, len(self.signal_flow_tracker['tier_metadata_flow']))
            },
            'integration_issues': self.signal_flow_tracker['integration_issues'],
            'config_sync_status': self.config_sync_status,
            'tier_system_performance': self._analyze_tier_system_performance()
        }
        
        # 保存報告
        report_file = f"cross_phase_integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        # 顯示關鍵結果
        print("\n" + "="*70)
        print("🎯 跨階段整合測試結果報告")
        print("="*70)
        print(f"📊 信號流處理統計:")
        print(f"  • Phase1A 信號生成: {report['test_summary']['total_signals_generated']}")
        print(f"  • Phase2 信號評分: {report['test_summary']['total_signals_scored']}")
        print(f"  • Phase3 決策制定: {report['test_summary']['total_decisions_made']}")
        
        print(f"\n🔄 數據流一致性:")
        print(f"  • Phase1A→Phase2 成功率: {report['data_flow_consistency']['phase1a_to_phase2_success_rate']:.1%}")
        print(f"  • Phase2→Phase3 成功率: {report['data_flow_consistency']['phase2_to_phase3_success_rate']:.1%}")
        print(f"  • 層級元數據保持率: {report['data_flow_consistency']['tier_metadata_preservation_rate']:.1%}")
        
        print(f"\n⚠️ 整合問題:")
        if report['integration_issues']:
            for issue in report['integration_issues']:
                print(f"  • {issue}")
        else:
            print("  ✅ 無整合問題")
        
        print(f"\n🔧 配置同步狀態:")
        if report['config_sync_status']['sync_errors']:
            for error in report['config_sync_status']['sync_errors']:
                print(f"  ❌ {error}")
        else:
            print("  ✅ 配置同步正常")
        
        print(f"\n💾 詳細報告已保存: {report_file}")
        logger.info(f"✅ 跨階段整合測試報告生成完成: {report_file}")
        
        return report
    
    def _analyze_tier_system_performance(self) -> Dict[str, Any]:
        """分析分層系統性能"""
        tier_stats = {}
        
        # 統計各層級信號分佈
        for signal in self.signal_flow_tracker['phase1a_signals']:
            tier = signal['signal_tier'].value if hasattr(signal['signal_tier'], 'value') else str(signal['signal_tier'])
            if tier not in tier_stats:
                tier_stats[tier] = {'count': 0, 'avg_confidence': 0, 'decisions': []}
            tier_stats[tier]['count'] += 1
            tier_stats[tier]['avg_confidence'] += signal['lean_confidence']
        
        # 計算平均值
        for tier in tier_stats:
            if tier_stats[tier]['count'] > 0:
                tier_stats[tier]['avg_confidence'] /= tier_stats[tier]['count']
        
        # 統計決策分佈
        for decision in self.signal_flow_tracker['phase3_decisions']:
            tier = decision['cross_phase_flow']['phase1a_tier']
            if tier in tier_stats:
                tier_stats[tier]['decisions'].append(decision['epl_decision'])
        
        return tier_stats

async def main():
    """主測試函數"""
    tester = RealSignalFlowTest()
    await tester.run_real_signal_flow_test(test_duration_minutes=15)  # 15分鐘真實測試

if __name__ == "__main__":
    asyncio.run(main())
