"""
階段1A測試：三週期信號打分模組重構測試
測試標準化週期權重模板與自動週期識別機制
"""

import asyncio
import pytest
from datetime import datetime, timedelta
from typing import Dict, Any

# 導入我們的新模組
from app.services.signal_scoring_engine import (
    SignalScoringEngine,
    StandardizedCycleTemplates,
    SignalModuleType,
    SignalModuleScore,
    TradingCycle,
    CycleSwitchConditions
)

class TestPhase1ASignalScoring:
    """階段1A測試套件"""
    
    def setup_method(self):
        """測試初始化"""
        self.scoring_engine = SignalScoringEngine()
        self.templates = StandardizedCycleTemplates()
        print("\n🧪 階段1A測試初始化完成")
    
    def test_cycle_weight_templates_validation(self):
        """測試1：週期權重模板驗證"""
        print("\n📋 測試1: 週期權重模板驗證")
        
        # 測試所有週期模板
        for cycle in TradingCycle:
            template = self.templates.get_template(cycle)
            assert template is not None, f"週期 {cycle.value} 模板不存在"
            
            # 驗證權重總和
            total_weight = template.get_total_weight()
            assert template.validate_weights(), f"週期 {cycle.value} 權重總和異常: {total_weight}"
            
            print(f"   ✅ {cycle.value} 模板: {template.template_name}")
            print(f"      權重總和: {total_weight:.3f}")
            print(f"      持倉預期: {template.holding_expectation_hours}小時")
            print(f"      核心權重: 技術{template.technical_structure_weight:.2f} | "
                  f"微結構{template.volume_microstructure_weight:.2f} | "
                  f"機構{template.smart_money_detection_weight:.2f}")
    
    def test_short_term_template_specifics(self):
        """測試2：短線模式特定配置"""
        print("\n🔥 測試2: 短線模式權重配置")
        
        short_template = self.templates.get_template(TradingCycle.SHORT_TERM)
        
        # 驗證短線模式的核心權重分配
        assert short_template.volume_microstructure_weight == 0.40, "短線微結構權重應為40%"
        assert short_template.smart_money_detection_weight == 0.25, "短線機構參與度權重應為25%"
        assert short_template.macro_environment_weight == 0.00, "短線不應考慮宏觀環境"
        assert short_template.holding_expectation_hours <= 2, "短線持倉預期應小於2小時"
        
        print(f"   ✅ 短線核心權重驗證通過:")
        print(f"      成交量微結構: {short_template.volume_microstructure_weight:.1%} (核心)")
        print(f"      機構參與度: {short_template.smart_money_detection_weight:.1%} (Smart Money)")
        print(f"      宏觀環境: {short_template.macro_environment_weight:.1%} (不適用)")
    
    def test_medium_term_template_specifics(self):
        """測試3：中線模式特定配置"""
        print("\n⚖️ 測試3: 中線模式權重配置")
        
        medium_template = self.templates.get_template(TradingCycle.MEDIUM_TERM)
        
        # 驗證中線模式的平衡權重分配  
        assert medium_template.smart_money_detection_weight == 0.30, "中線機構參與度權重應為30%"
        assert medium_template.macro_environment_weight == 0.10, "中線宏觀環境權重應為10%"
        assert 4 <= medium_template.holding_expectation_hours <= 24, "中線持倉預期應在4-24小時"
        assert medium_template.trend_confirmation_required == True, "中線應需要趨勢確認"
        
        print(f"   ✅ 中線平衡權重驗證通過:")
        print(f"      機構參與度: {medium_template.smart_money_detection_weight:.1%} (資金流向)")
        print(f"      技術結構: {medium_template.technical_structure_weight:.1%}")
        print(f"      宏觀環境: {medium_template.macro_environment_weight:.1%}")
    
    def test_long_term_template_specifics(self):
        """測試4：長線模式特定配置"""
        print("\n📈 測試4: 長線模式權重配置")
        
        long_template = self.templates.get_template(TradingCycle.LONG_TERM)
        
        # 驗證長線模式的宏觀主導配置
        assert long_template.macro_environment_weight == 0.35, "長線宏觀環境權重應為35%"
        assert long_template.volume_microstructure_weight == 0.05, "長線微結構權重應為5%"
        assert long_template.holding_expectation_hours >= 168, "長線持倉預期應≥168小時(1週)"
        assert long_template.macro_factor_importance >= 0.3, "長線宏觀因子重要性應≥0.3"
        
        print(f"   ✅ 長線宏觀主導驗證通過:")
        print(f"      宏觀環境: {long_template.macro_environment_weight:.1%} (核心)")
        print(f"      跨市場聯動: {long_template.cross_market_correlation_weight:.1%}")
        print(f"      成交量微結構: {long_template.volume_microstructure_weight:.1%} (最低)")
    
    def test_cycle_switch_conditions(self):
        """測試5：週期切換觸發條件"""
        print("\n🔄 測試5: 自動週期識別條件")
        
        # 測試短線觸發條件
        short_trigger = CycleSwitchConditions.evaluate_short_term_trigger(
            holding_expectation_hours=1.5,
            signal_density=0.8,
            current_volatility=0.7
        )
        assert short_trigger == True, "短線觸發條件測試失敗"
        print("   ✅ 短線觸發條件: 持倉1.5h + 信號密度0.8 + 波動0.7 → 觸發成功")
        
        # 測試中線觸發條件
        medium_trigger = CycleSwitchConditions.evaluate_medium_term_trigger(
            holding_expectation_hours=12.0,
            trend_confirmation=True,
            trend_strength=0.7
        )
        assert medium_trigger == True, "中線觸發條件測試失敗"
        print("   ✅ 中線觸發條件: 持倉12h + 趨勢確認 + 趨勢強度0.7 → 觸發成功")
        
        # 測試長線觸發條件
        long_trigger = CycleSwitchConditions.evaluate_long_term_trigger(
            holding_expectation_hours=200.0,
            macro_factor_weight=0.3,
            market_regime_stability=0.8
        )
        assert long_trigger == True, "長線觸發條件測試失敗"
        print("   ✅ 長線觸發條件: 持倉200h + 宏觀權重0.3 + 制度穩定0.8 → 觸發成功")
    
    async def test_auto_cycle_identification(self):
        """測試6：自動週期識別邏輯"""
        print("\n🎯 測試6: 自動週期識別邏輯")
        
        # 測試短線識別
        short_conditions = {
            'holding_expectation_hours': 1.0,
            'current_volatility': 0.8,
            'trend_strength': 0.4,
            'regime_stability': 0.5
        }
        short_signals = {
            'signal_density': 0.85,
            'trend_confirmed': False,
            'macro_factor_weight': 0.05
        }
        
        identified_cycle = self.templates.auto_cycle_identification(short_conditions, short_signals)
        assert identified_cycle == TradingCycle.SHORT_TERM, f"短線識別失敗，得到: {identified_cycle}"
        print("   ✅ 短線自動識別: 高波動 + 高信號密度 → SHORT_TERM")
        
        # 測試長線識別
        long_conditions = {
            'holding_expectation_hours': 240.0,
            'current_volatility': 0.3,
            'trend_strength': 0.8,
            'regime_stability': 0.9
        }
        long_signals = {
            'signal_density': 0.3,
            'trend_confirmed': True,
            'macro_factor_weight': 0.4
        }
        
        identified_cycle = self.templates.auto_cycle_identification(long_conditions, long_signals)
        assert identified_cycle == TradingCycle.LONG_TERM, f"長線識別失敗，得到: {identified_cycle}"
        print("   ✅ 長線自動識別: 長持倉 + 高宏觀權重 → LONG_TERM")
    
    async def test_signal_weighted_scoring(self):
        """測試7：信號加權評分系統"""
        print("\n📊 測試7: 信號加權評分系統")
        
        # 模擬各模組信號分數
        mock_signal_scores = {
            SignalModuleType.TECHNICAL_STRUCTURE: SignalModuleScore(
                module_type=SignalModuleType.TECHNICAL_STRUCTURE,
                raw_score=0.75,
                confidence=0.85,
                strength=0.8,
                timestamp=datetime.now(),
                source_data={'RSI': 65, 'MACD': 'bullish'},
                reliability=0.9
            ),
            SignalModuleType.VOLUME_MICROSTRUCTURE: SignalModuleScore(
                module_type=SignalModuleType.VOLUME_MICROSTRUCTURE,
                raw_score=0.82,
                confidence=0.78,
                strength=0.85,
                timestamp=datetime.now(),
                source_data={'volume_surge': True, 'smart_money_flow': 'inflow'},
                reliability=0.85
            ),
            SignalModuleType.SENTIMENT_INDICATORS: SignalModuleScore(
                module_type=SignalModuleType.SENTIMENT_INDICATORS,
                raw_score=0.68,
                confidence=0.72,
                strength=0.7,
                timestamp=datetime.now(),
                source_data={'fear_greed': 45, 'funding_rate': -0.01},
                reliability=0.8
            ),
            SignalModuleType.SMART_MONEY_DETECTION: SignalModuleScore(
                module_type=SignalModuleType.SMART_MONEY_DETECTION,
                raw_score=0.78,
                confidence=0.88,
                strength=0.82,
                timestamp=datetime.now(),
                source_data={'institutional_flow': 'accumulating', 'whale_activity': 'high'},
                reliability=0.92
            )
        }
        
        # 測試市場條件
        market_conditions = {
            'holding_expectation_hours': 2.0,
            'current_volatility': 0.75,
            'trend_strength': 0.6,
            'regime_stability': 0.7,
            'macro_importance': 0.1
        }
        
        # 執行加權評分
        result = await self.scoring_engine.calculate_weighted_score(
            signal_scores=mock_signal_scores,
            market_conditions=market_conditions
        )
        
        # 驗證結果結構
        assert 'active_cycle' in result, "結果缺少活躍週期信息"
        assert 'total_weighted_score' in result, "結果缺少總加權分數"
        assert 'signal_coverage' in result, "結果缺少信號覆蓋率"
        assert 'module_scores' in result, "結果缺少模組分數詳情"
        
        print(f"   ✅ 加權評分計算成功:")
        print(f"      活躍週期: {result['active_cycle']}")
        print(f"      總加權分數: {result['total_weighted_score']:.3f}")
        print(f"      信號覆蓋率: {result['signal_coverage']:.2%}")
        print(f"      平均信心度: {result['average_confidence']:.3f}")
        
        # 驗證信號覆蓋率計算
        expected_coverage = len(mock_signal_scores) / 7  # 4個模組 / 7個總模組
        assert abs(result['signal_coverage'] - expected_coverage) < 0.01, "信號覆蓋率計算錯誤"
    
    def test_cycle_switch_execution(self):
        """測試8：週期切換執行"""
        print("\n🔄 測試8: 週期切換執行")
        
        # 記錄初始週期
        initial_cycle = self.templates.active_cycle
        print(f"   初始週期: {initial_cycle.value}")
        
        # 執行週期切換
        switch_success = self.templates.execute_cycle_switch(
            target_cycle=TradingCycle.SHORT_TERM,
            trigger_reason="測試觸發",
            market_conditions={'volatility': 0.8, 'signal_density': 0.9},
            confidence_score=0.85
        )
        
        assert switch_success == True, "週期切換執行失敗"
        assert self.templates.active_cycle == TradingCycle.SHORT_TERM, "週期切換後狀態錯誤"
        
        # 檢查切換歷史
        history = self.templates.get_switch_history(limit=1)
        assert len(history) >= 1, "切換歷史記錄失敗"
        
        last_switch = history[-1]
        assert last_switch.target_cycle == TradingCycle.SHORT_TERM, "歷史記錄週期錯誤"
        assert last_switch.confidence_score == 0.85, "歷史記錄信心度錯誤"
        
        print(f"   ✅ 週期切換成功: {initial_cycle.value} → {TradingCycle.SHORT_TERM.value}")
        print(f"      觸發原因: {last_switch.trigger_reason}")
        print(f"      信心度: {last_switch.confidence_score:.2f}")

async def run_phase1a_tests():
    """運行階段1A完整測試套件"""
    print("🚀 階段1A：三週期信號打分模組重構 - 完整測試")
    print("=" * 80)
    
    test_suite = TestPhase1ASignalScoring()
    test_suite.setup_method()
    
    try:
        # 基礎模板測試
        test_suite.test_cycle_weight_templates_validation()
        test_suite.test_short_term_template_specifics()
        test_suite.test_medium_term_template_specifics()
        test_suite.test_long_term_template_specifics()
        
        # 週期切換機制測試
        test_suite.test_cycle_switch_conditions()
        await test_suite.test_auto_cycle_identification()
        
        # 信號評分系統測試
        await test_suite.test_signal_weighted_scoring()
        test_suite.test_cycle_switch_execution()
        
        print("\n" + "=" * 80)
        print("✅ 階段1A測試全部通過！")
        print("\n📋 實施成果總結:")
        print("   ✅ 標準化信號模組分類 (7個核心模組)")
        print("   ✅ 三週期權重模板 (短線/中線/長線)")
        print("   ✅ 自動週期識別機制")
        print("   ✅ 週期切換觸發邏輯")
        print("   ✅ 信號加權評分引擎")
        print("   ✅ 權重標準化驗證")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 階段1A測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 運行測試
    import asyncio
    success = asyncio.run(run_phase1a_tests())
    
    if success:
        print("\n🎯 階段1A實施完成，可以繼續階段1B開發")
    else:
        print("\n⚠️ 階段1A存在問題，需要修正後再繼續")
