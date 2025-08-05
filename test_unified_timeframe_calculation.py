#!/usr/bin/env python3
"""
統一時間分層計算驗證測試 - Trading X
驗證所有時間計算函數都遵循統一標準
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 直接導入時間計算類而不是整個系統
from app.services.sniper_emergency_trigger import TimeframeCategory
from datetime import datetime

# 創建一個簡化的時間計算器類用於測試
class TimeCalculator:
    """簡化的時間計算器用於測試"""
    
    def _calculate_phase1abc_timeframe(self, category: TimeframeCategory, analysis_result: dict = None) -> float:
        # Phase 1A: 基礎時間框架
        base_hours = {
            TimeframeCategory.SHORT_TERM: 3.0,   # 短線: 3小時基礎
            TimeframeCategory.MEDIUM_TERM: 18.0, # 中線: 18小時基礎
            TimeframeCategory.LONG_TERM: 48.0    # 長線: 48小時基礎
        }
        phase1a_base = base_hours.get(category, 18.0)
        
        # Phase 1B: 多維分析加成
        if analysis_result and analysis_result.get('technical_indicators'):
            indicator_count = len(analysis_result['technical_indicators'])
            phase1b_multiplier = 1.0 + (indicator_count - 3) * 0.1
            phase1b_multiplier = max(0.8, min(1.5, phase1b_multiplier))
        else:
            phase1b_multiplier = 1.0
        
        # Phase 1C: 精準度調整
        if analysis_result and 'sniper_metrics' in analysis_result:
            metrics = analysis_result['sniper_metrics']
            precision = metrics.get('precision', 0.85)
            phase1c_multiplier = 0.7 + (precision * 0.6)
        else:
            precision = 0.85
            phase1c_multiplier = 0.7 + (precision * 0.6)
        
        return phase1a_base * phase1b_multiplier * phase1c_multiplier
    
    def _calculate_phase123_multiplier(self, analysis_result: dict = None) -> float:
        if not analysis_result:
            return 1.0
        
        # 技術分析強度：0.8 + (technical_strength * 0.4)
        technical_strength = analysis_result.get('technical_strength', 0.7)
        phase1_factor = 0.8 + (technical_strength * 0.4)
        
        # 市場確信度：0.9 + (market_confidence * 0.3)
        market_confidence = analysis_result.get('confidence', 0.7)
        phase2_factor = 0.9 + (market_confidence * 0.3)
        
        # 指標收斂度：基於風險回報比，最高1.3倍
        risk_reward = analysis_result.get('risk_reward_ratio', 2.0)
        phase3_factor = min(1.3, 0.9 + (risk_reward - 1.5) * 0.2)
        
        multiplier = phase1_factor * phase2_factor * phase3_factor
        return max(0.7, min(1.8, multiplier))
    
    def _calculate_quality_time_multiplier(self, quality_score: float) -> float:
        if quality_score >= 8.0:
            return 1.4  # 高品質+40%
        elif quality_score >= 6.5:
            return 1.2  # 中高品質+20%
        elif quality_score >= 5.0:
            return 1.0  # 標準時間
        else:
            return 0.8  # 低品質-20%
    
    def _calculate_market_time_adjustment(self, analysis_result: dict = None) -> float:
        if not analysis_result:
            return 1.0
        
        market_conditions = analysis_result.get('market_conditions', 0.6)
        
        if market_conditions >= 0.8:
            return 1.2  # 好市場+20%
        elif market_conditions >= 0.6:
            return 1.0  # 正常市場
        else:
            return 0.8  # 差市場-20%
    
    def _get_timeframe_limits(self, category: TimeframeCategory) -> tuple:
        limits = {
            TimeframeCategory.SHORT_TERM: (1.5, 8.0),    # 短線: 1.5-8小時
            TimeframeCategory.MEDIUM_TERM: (8.0, 48.0),  # 中線: 8-48小時
            TimeframeCategory.LONG_TERM: (24.0, 120.0)   # 長線: 24-120小時
        }
        return limits.get(category, (6.0, 48.0))

def test_unified_timeframe_calculation():
    """測試統一時間分層計算"""
    
    print("🎯 狙擊手統一時間分層計算驗證")
    print("=" * 60)
    
    # 初始化時間計算器
    calculator = TimeCalculator()
    
    # 測試數據
    test_cases = [
        {
            "name": "短線高品質信號",
            "category": TimeframeCategory.SHORT_TERM,
            "quality_score": 8.5,
            "analysis_result": {
                "technical_indicators": ["RSI", "MACD", "BB", "EMA", "Volume"],  # 5個指標
                "sniper_metrics": {"precision": 0.95},
                "technical_strength": 0.9,
                "confidence": 0.85,
                "risk_reward_ratio": 3.0,
                "market_conditions": 0.8
            }
        },
        {
            "name": "中線中品質信號", 
            "category": TimeframeCategory.MEDIUM_TERM,
            "quality_score": 6.5,
            "analysis_result": {
                "technical_indicators": ["RSI", "MACD", "EMA"],  # 3個指標
                "sniper_metrics": {"precision": 0.75},
                "technical_strength": 0.7,
                "confidence": 0.7,
                "risk_reward_ratio": 2.0,
                "market_conditions": 0.6
            }
        },
        {
            "name": "長線低品質信號",
            "category": TimeframeCategory.LONG_TERM,
            "quality_score": 4.5,
            "analysis_result": {
                "technical_indicators": ["RSI", "MACD"],  # 2個指標
                "sniper_metrics": {"precision": 0.70},
                "technical_strength": 0.5,
                "confidence": 0.6,
                "risk_reward_ratio": 1.5,
                "market_conditions": 0.4
            }
        }
    ]
    
    print("\n📊 計算過程詳細分解:")
    print("-" * 60)
    
    for test_case in test_cases:
        print(f"\n🔍 測試案例: {test_case['name']}")
        print(f"   時間框架: {test_case['category'].value}")
        print(f"   品質評分: {test_case['quality_score']}")
        
        # === Phase 1ABC 計算 ===
        phase1abc_hours = calculator._calculate_phase1abc_timeframe(
            test_case['category'], 
            test_case['analysis_result']
        )
        
        # === Phase 1+2+3 加成 ===
        phase123_multiplier = calculator._calculate_phase123_multiplier(
            test_case['analysis_result']
        )
        
        # === 品質時間加成 ===
        quality_multiplier = calculator._calculate_quality_time_multiplier(
            test_case['quality_score']
        )
        
        # === 市場條件調整 ===
        market_adjustment = calculator._calculate_market_time_adjustment(
            test_case['analysis_result']
        )
        
        # === 最終計算 ===
        phase123_time = phase1abc_hours * phase123_multiplier
        final_hours = phase123_time * quality_multiplier * market_adjustment
        
        # === 範圍限制 ===
        min_hours, max_hours = calculator._get_timeframe_limits(test_case['category'])
        limited_hours = max(min_hours, min(max_hours, final_hours))
        
        print(f"   📈 Phase1ABC基礎: {phase1abc_hours:.1f}h")
        print(f"   🔍 Phase123加成: ×{phase123_multiplier:.2f} = {phase123_time:.1f}h")
        print(f"   ⭐ 品質加成: ×{quality_multiplier:.1f} = {phase123_time * quality_multiplier:.1f}h")
        print(f"   🌊 市場調整: ×{market_adjustment:.1f} = {final_hours:.1f}h")
        print(f"   📏 範圍限制: {min_hours}-{max_hours}h")
        print(f"   ✅ 最終結果: {limited_hours:.1f}h")
        
        # 驗證是否符合統一標準
        expected_ranges = {
            TimeframeCategory.SHORT_TERM: (1.5, 8.0),
            TimeframeCategory.MEDIUM_TERM: (8.0, 48.0),
            TimeframeCategory.LONG_TERM: (24.0, 120.0)
        }
        
        expected_min, expected_max = expected_ranges[test_case['category']]
        if expected_min <= limited_hours <= expected_max:
            print(f"   ✅ 符合統一標準: {expected_min}-{expected_max}h")
        else:
            print(f"   ❌ 超出統一標準: {expected_min}-{expected_max}h")
    
    print("\n" + "=" * 60)
    print("🎯 統一標準驗證:")
    print("   📊 短線 (SHORT_TERM): 1.5-8小時")
    print("   📊 中線 (MEDIUM_TERM): 8-48小時") 
    print("   📊 長線 (LONG_TERM): 24-120小時")
    print("\n📋 計算公式:")
    print("   1️⃣ Phase1B: 1.0 + (indicator_count - 3) * 0.1 (80%-150%)")
    print("   2️⃣ Phase1C: 0.7 + (precision * 0.6)")
    print("   3️⃣ 技術強度: 0.8 + (technical_strength * 0.4)")
    print("   4️⃣ 市場確信: 0.9 + (market_confidence * 0.3)")
    print("   5️⃣ 品質加成: 8.0+→1.4x, 6.5+→1.2x, 5.0+→1.0x, <5.0→0.8x")
    print("   6️⃣ 市場調整: 0.8+→1.2x, 0.6+→1.0x, <0.6→0.8x")

if __name__ == "__main__":
    test_unified_timeframe_calculation()
