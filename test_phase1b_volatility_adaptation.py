#!/usr/bin/env python3
"""
階段1B：波動適應性優化測試
測試動態權重調整、信號連續性監控和波動適應機制
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.phase1b_volatility_adaptation import (
    enhanced_signal_scoring_engine,
    VolatilityAdaptiveEngine,
    AdaptiveWeightEngine,
    VolatilityMetrics,
    SignalContinuityMetrics
)
from app.services.signal_scoring_engine import TradingCycle
import random
from datetime import datetime

def generate_mock_price_data(base_price: float, volatility: float, periods: int = 100):
    """生成模擬價格數據"""
    prices = []
    current_price = base_price
    for _ in range(periods):
        change = random.uniform(-volatility, volatility)
        current_price *= (1 + change)
        prices.append(current_price)
    return prices

async def test_volatility_metrics():
    """測試波動性指標計算"""
    print("\n" + "="*60)
    print("🧪 測試1：波動性指標計算")
    print("="*60)
    
    volatility_engine = VolatilityAdaptiveEngine()
    
    # 測試不同波動環境
    test_scenarios = [
        ("低波動環境", 0.01),
        ("正常波動環境", 0.02),
        ("高波動環境", 0.04)
    ]
    
    for scenario_name, volatility in test_scenarios:
        print(f"\n📊 {scenario_name} (波動率: {volatility*100:.1f}%)")
        
        # 生成價格數據
        prices = generate_mock_price_data(50000, volatility, 100)
        
        # 計算波動指標
        vol_metrics = volatility_engine.calculate_volatility_metrics(prices)
        
        print(f"   當前波動率: {vol_metrics.current_volatility:.3f}")
        print(f"   波動趨勢: {vol_metrics.volatility_trend:.3f}")
        print(f"   制度穩定性: {vol_metrics.regime_stability:.3f}")
        print(f"   微觀波動: {vol_metrics.micro_volatility:.3f}")
        
        # 驗證指標合理性
        assert 0 <= vol_metrics.current_volatility <= 1, "波動率應在0-1範圍內"
        assert -1 <= vol_metrics.volatility_trend <= 1, "波動趨勢應在-1到1範圍內"
        
    print("✅ 波動性指標測試通過")

async def test_signal_continuity():
    """測試信號連續性指標"""
    print("\n" + "="*60)
    print("🧪 測試2：信號連續性指標")
    print("="*60)
    
    volatility_engine = VolatilityAdaptiveEngine()
    
    # 模擬一系列信號
    for i in range(10):
        current_signals = await enhanced_signal_scoring_engine._get_mock_signal_scores()
        
        # 添加一些隨機變化模擬信號演化
        for signal in current_signals.values():
            signal.raw_score += random.uniform(-0.1, 0.1)
            signal.raw_score = max(0, min(1, signal.raw_score))  # 限制在0-1範圍
    
    # 計算連續性指標
    continuity_metrics = volatility_engine.calculate_signal_continuity(current_signals)
    
    print(f"📈 信號持續性: {continuity_metrics.signal_persistence:.3f}")
    print(f"📊 信號分歧度: {continuity_metrics.signal_divergence:.3f}")
    print(f"🎯 共識強度: {continuity_metrics.consensus_strength:.3f}")
    print(f"⏰ 時間一致性: {continuity_metrics.temporal_consistency:.3f}")
    print(f"🔗 跨模組相關性: {continuity_metrics.cross_module_correlation:.3f}")
    print(f"📉 信號衰減率: {continuity_metrics.signal_decay_rate:.3f}")
    
    # 驗證指標合理性
    assert 0 <= continuity_metrics.signal_persistence <= 1, "信號持續性應在0-1範圍內"
    assert 0 <= continuity_metrics.consensus_strength <= 1, "共識強度應在0-1範圍內"
    
    print("✅ 信號連續性測試通過")

async def test_adaptive_weight_adjustment():
    """測試自適應權重調整"""
    print("\n" + "="*60)
    print("🧪 測試3：自適應權重調整")
    print("="*60)
    
    weight_engine = AdaptiveWeightEngine()
    
    # 獲取基礎模板
    base_template = weight_engine.base_templates.get_template(TradingCycle.MEDIUM_TERM)
    
    print(f"📋 基礎模板: {base_template.template_name}")
    print(f"   原始權重總和: {base_template.get_total_weight():.3f}")
    
    # 創建不同的市場條件場景
    scenarios = [
        ("高波動低穩定", VolatilityMetrics(0.8, 0.5, 0.9, 0.3, 0.7, 0.6, datetime.now()),
         SignalContinuityMetrics(0.4, 0.6, 0.5, 0.4, 0.3, 0.5)),
        ("低波動高穩定", VolatilityMetrics(0.2, -0.1, 0.1, 0.9, 0.3, 0.2, datetime.now()),
         SignalContinuityMetrics(0.8, 0.2, 0.9, 0.8, 0.7, 0.1)),
        ("正常市場條件", VolatilityMetrics(0.5, 0.0, 0.5, 0.7, 0.5, 0.4, datetime.now()),
         SignalContinuityMetrics(0.7, 0.3, 0.6, 0.7, 0.5, 0.2))
    ]
    
    for scenario_name, vol_metrics, cont_metrics in scenarios:
        print(f"\n🎯 {scenario_name}")
        
        # 調整權重
        adjusted_template = weight_engine.adjust_weights_for_volatility(
            base_template, vol_metrics, cont_metrics
        )
        
        print(f"   調整後權重總和: {adjusted_template.get_total_weight():.3f}")
        print(f"   成交量微結構權重變化: {base_template.volume_microstructure_weight:.3f} → {adjusted_template.volume_microstructure_weight:.3f}")
        print(f"   技術結構權重變化: {base_template.technical_structure_weight:.3f} → {adjusted_template.technical_structure_weight:.3f}")
        print(f"   宏觀環境權重變化: {base_template.macro_environment_weight:.3f} → {adjusted_template.macro_environment_weight:.3f}")
        
        # 驗證權重調整後仍然標準化
        assert 0.99 <= adjusted_template.get_total_weight() <= 1.01, "調整後權重總和應接近1.0"
        
    print("✅ 自適應權重調整測試通過")

async def test_enhanced_signal_scoring():
    """測試增強版信號打分系統"""
    print("\n" + "="*60)
    print("🧪 測試4：增強版信號打分系統")
    print("="*60)
    
    # 準備測試數據
    symbols = ['BTCUSDT', 'ETHUSDT']
    price_data = {
        'BTCUSDT': generate_mock_price_data(50000, 0.03, 100),
        'ETHUSDT': generate_mock_price_data(3000, 0.035, 100)
    }
    
    # 測試不同週期的增強評分
    cycles = [TradingCycle.SHORT_TERM, TradingCycle.MEDIUM_TERM, TradingCycle.LONG_TERM]
    
    for cycle in cycles:
        print(f"\n📊 測試週期: {cycle.value}")
        
        # 執行增強評分
        result = await enhanced_signal_scoring_engine.enhanced_signal_scoring(
            symbols=symbols,
            target_cycle=cycle,
            price_data=price_data,
            enable_adaptation=True
        )
        
        print(f"   適應性已應用: {result.get('enhancement_applied', False)}")
        print(f"   總加權分數: {result.get('total_weighted_score', 0):.3f}")
        print(f"   信號覆蓋率: {result.get('signal_coverage', 0):.2f}")
        
        # 檢查階段1B增強指標
        if 'phase_1b_metrics' in result:
            vol_metrics = result['phase_1b_metrics']['volatility_metrics']
            cont_metrics = result['phase_1b_metrics']['continuity_metrics']
            
            print(f"   當前波動率: {vol_metrics['current_volatility']:.3f}")
            print(f"   信號持續性: {cont_metrics['signal_persistence']:.3f}")
        
        # 驗證結果結構
        assert 'enhancement_applied' in result, "應包含增強應用狀態"
        assert 'total_weighted_score' in result, "應包含總加權分數"
        
    print("✅ 增強版信號打分測試通過")

async def test_performance_tracking():
    """測試性能追蹤"""
    print("\n" + "="*60)
    print("🧪 測試5：性能追蹤系統")
    print("="*60)
    
    # 執行幾次增強評分來累積性能數據
    symbols = ['BTCUSDT']
    price_data = {'BTCUSDT': generate_mock_price_data(50000, 0.04, 100)}  # 高波動
    
    for i in range(3):
        await enhanced_signal_scoring_engine.enhanced_signal_scoring(
            symbols=symbols,
            target_cycle=TradingCycle.SHORT_TERM,
            price_data=price_data,
            enable_adaptation=True
        )
    
    # 獲取性能總結
    performance = enhanced_signal_scoring_engine.get_performance_summary()
    
    print(f"📈 階段: {performance['phase']}")
    print(f"📊 總適應次數: {performance['metrics']['total_adaptations']}")
    print(f"🌊 波動調整次數: {performance['metrics']['volatility_adjustments']}")
    print(f"🔄 連續性改進次數: {performance['metrics']['continuity_improvements']}")
    
    print("\n🎯 系統能力:")
    for capability, description in performance['capabilities'].items():
        print(f"   {capability}: {description}")
    
    print("✅ 性能追蹤測試通過")

async def run_all_tests():
    """執行所有階段1B測試"""
    print("🚀 開始階段1B：波動適應性優化測試")
    print("=" * 80)
    
    try:
        await test_volatility_metrics()
        await test_signal_continuity()
        await test_adaptive_weight_adjustment()
        await test_enhanced_signal_scoring()
        await test_performance_tracking()
        
        print("\n" + "="*80)
        print("🎉 階段1B所有測試通過！")
        print("✅ 波動適應性優化功能完全正常")
        print("✅ 信號連續性監控運行良好")
        print("✅ 動態權重調整機制有效")
        print("✅ 增強版信號打分系統穩定")
        print("✅ 性能追蹤系統運行正常")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
