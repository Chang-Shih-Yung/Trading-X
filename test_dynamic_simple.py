#!/usr/bin/env python3
"""
直接測試動態時間計算方法（不使用全域初始化）
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from app.services.intelligent_timeframe_classifier import TimeframeCategory
from app.utils.timezone_utils import get_taiwan_now
from datetime import timedelta
import logging

# 設置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

def calculate_dynamic_expiry_test(category: TimeframeCategory, quality_score: float, analysis_result: dict):
    """
    複製動態時間計算邏輯進行獨立測試
    """
    print(f"   🔧 計算動態過期時間...")
    print(f"   📊 時間框架類別: {category.value}")
    print(f"   ⭐ 品質評分: {quality_score}")
    
    # 基礎時間配置 (小時)
    base_times = {
        TimeframeCategory.SHORT: 8,    # 短線：8小時
        TimeframeCategory.MEDIUM: 18,  # 中線：18小時  
        TimeframeCategory.LONG: 36     # 長線：36小時
    }
    
    base_hours = base_times.get(category, 18)
    print(f"   🕐 基礎時間: {base_hours}小時")
    
    # 品質調整係數 (0.5-1.5倍)
    if quality_score >= 0.85:
        quality_multiplier = 1.4  # 高品質：+40%
    elif quality_score >= 0.70:
        quality_multiplier = 1.2  # 中高品質：+20%
    elif quality_score >= 0.50:
        quality_multiplier = 1.0  # 中等品質：基準
    else:
        quality_multiplier = 0.7  # 低品質：-30%
    
    print(f"   📈 品質調整係數: {quality_multiplier}x")
    
    # 技術強度調整
    technical_strength = analysis_result.get('technical_strength', 0.7)
    if technical_strength >= 0.9:
        tech_adjustment = 1.2
    elif technical_strength >= 0.8:
        tech_adjustment = 1.1
    elif technical_strength >= 0.6:
        tech_adjustment = 1.0
    else:
        tech_adjustment = 0.9
    
    print(f"   🔧 技術強度調整: {tech_adjustment}x (強度: {technical_strength})")
    
    # 市場條件調整
    market_conditions = analysis_result.get('market_conditions', 0.7)
    if market_conditions >= 0.8:
        market_adjustment = 1.15
    elif market_conditions >= 0.6:
        market_adjustment = 1.0
    else:
        market_adjustment = 0.85
    
    print(f"   🌊 市場條件調整: {market_adjustment}x (條件: {market_conditions})")
    
    # 風險報酬比調整
    risk_reward = analysis_result.get('risk_reward_ratio', 2.0)
    if risk_reward >= 3.0:
        rr_adjustment = 1.25
    elif risk_reward >= 2.5:
        rr_adjustment = 1.15
    elif risk_reward >= 2.0:
        rr_adjustment = 1.05
    else:
        rr_adjustment = 0.95
    
    print(f"   💰 風險報酬調整: {rr_adjustment}x (比率: {risk_reward})")
    
    # 計算最終小時數
    final_hours = base_hours * quality_multiplier * tech_adjustment * market_adjustment * rr_adjustment
    
    # 邊界限制
    min_hours = 2
    max_hours = 72
    final_hours = max(min_hours, min(final_hours, max_hours))
    
    print(f"   ⏰ 最終計算時間: {final_hours:.1f}小時")
    
    # 轉換為過期時間
    current_time = get_taiwan_now()
    expires_at = current_time + timedelta(hours=final_hours)
    
    return expires_at, final_hours

async def test_dynamic_calculation_simple():
    """簡化的動態時間計算測試"""
    
    print("🧪 簡化動態時間計算測試...")
    
    # 測試案例
    test_cases = [
        {
            "name": "高品質短期信號",
            "category": TimeframeCategory.SHORT,
            "quality_score": 0.95,
            "analysis_result": {
                'symbol': 'TESTUSDT',
                'confidence': 0.95,
                'technical_strength': 0.95,
                'market_conditions': 0.8,
                'indicator_count': 5,
                'precision': 0.95,
                'risk_reward_ratio': 3.0
            }
        },
        {
            "name": "中等品質中期信號",  
            "category": TimeframeCategory.MEDIUM,
            "quality_score": 0.70,
            "analysis_result": {
                'symbol': 'TEST2USDT',
                'confidence': 0.70,
                'technical_strength': 0.70,
                'market_conditions': 0.6,
                'indicator_count': 3,
                'precision': 0.70,
                'risk_reward_ratio': 2.0
            }
        },
        {
            "name": "低品質長期信號",
            "category": TimeframeCategory.LONG,
            "quality_score": 0.40,
            "analysis_result": {
                'symbol': 'TEST3USDT',
                'confidence': 0.40,
                'technical_strength': 0.40,
                'market_conditions': 0.5,
                'indicator_count': 2,
                'precision': 0.40,
                'risk_reward_ratio': 1.5
            }
        }
    ]
    
    print("\n📊 測試結果:")
    print("=" * 100)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🎯 測試 {i}: {test_case['name']}")
        print(f"   類別: {test_case['category'].value}")
        print(f"   品質評分: {test_case['quality_score']}")
        
        try:
            expires_at, hours = calculate_dynamic_expiry_test(
                category=test_case['category'],
                quality_score=test_case['quality_score'],
                analysis_result=test_case['analysis_result']
            )
            
            current_time = get_taiwan_now()
            
            print(f"   📅 當前時間: {current_time}")
            print(f"   📅 過期時間: {expires_at}")
            
            if hours != 24.0:
                print(f"   ✅ 動態計算成功！時間: {hours:.1f}小時")
            else:
                print(f"   ⚠️  返回固定24小時")
                
        except Exception as e:
            print(f"   ❌ 計算失敗: {e}")
            import traceback
            print(f"   錯誤詳情: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_dynamic_calculation_simple())
