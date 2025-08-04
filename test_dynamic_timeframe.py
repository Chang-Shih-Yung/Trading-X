#!/usr/bin/env python3
"""
測試動態時間計算系統
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.intelligent_timeframe_classifier import IntelligentTimeframeClassifier
from datetime import datetime

async def test_dynamic_timeframe_calculation():
    """測試動態時間計算"""
    print("🎯 動態時間計算系統測試")
    print("=" * 60)
    
    # 初始化分類器
    classifier = IntelligentTimeframeClassifier()
    
    # 測試不同情境
    test_cases = [
        {
            'name': '高品質短線信號',
            'timeframe_category': 'short',
            'quality_score': 8.5,
            'analysis_result': {
                'indicator_count': 5,
                'precision': 0.85,
                'technical_strength': 0.8,
                'market_conditions': 0.9,
                'risk_reward_ratio': 2.5
            }
        },
        {
            'name': '中等品質中線信號', 
            'timeframe_category': 'medium',
            'quality_score': 6.0,
            'analysis_result': {
                'indicator_count': 3,
                'precision': 0.6,
                'technical_strength': 0.6,
                'market_conditions': 0.7,
                'risk_reward_ratio': 2.0
            }
        },
        {
            'name': '低品質長線信號',
            'timeframe_category': 'long', 
            'quality_score': 4.5,
            'analysis_result': {
                'indicator_count': 2,
                'precision': 0.5,
                'technical_strength': 0.4,
                'market_conditions': 0.5,
                'risk_reward_ratio': 1.5
            }
        }
    ]
    
    for case in test_cases:
        print(f"\n📊 測試案例: {case['name']}")
        print(f"   類別: {case['timeframe_category']}")
        print(f"   品質評分: {case['quality_score']}")
        
        try:
            # 計算動態時間
            dynamic_minutes = classifier.calculate_dynamic_timeframe(
                timeframe_category=case['timeframe_category'],
                quality_score=case['quality_score'],
                analysis_result=case['analysis_result']
            )
            
            dynamic_hours = dynamic_minutes / 60.0
            
            print(f"   ✅ 動態時間: {dynamic_minutes:.1f}分鐘 ({dynamic_hours:.1f}小時)")
            
            # 檢查是否在合理範圍內
            limits = {
                'short': (1.5, 8.0),
                'medium': (8.0, 48.0), 
                'long': (24.0, 120.0)
            }
            
            min_hours, max_hours = limits[case['timeframe_category']]
            if min_hours <= dynamic_hours <= max_hours:
                print(f"   ✅ 時間範圍合理: {min_hours}-{max_hours}小時")
            else:
                print(f"   ⚠️ 時間範圍異常: {dynamic_hours:.1f}小時 (預期: {min_hours}-{max_hours}小時)")
                
        except Exception as e:
            print(f"   ❌ 計算失敗: {e}")
    
    print(f"\n🎯 測試完成 - {datetime.now()}")

if __name__ == "__main__":
    asyncio.run(test_dynamic_timeframe_calculation())
