#!/usr/bin/env python3
"""
直接測試動態時間計算功能
不依賴完整的數據庫session，直接調用計算方法
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from app.services.sniper_smart_layer import SniperSmartLayerSystem
from app.models.sniper_signal_history import TimeframeCategory
from app.utils.timezone_utils import get_taiwan_now
import logging

# 設置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

async def test_dynamic_calculation_direct():
    """直接測試動態時間計算方法"""
    
    print("🧪 直接測試動態時間計算方法...")
    
    # 創建 sniper_smart_layer 系統
    sniper_system = SniperSmartLayerSystem()
    
    # 測試案例
    test_cases = [
        {
            "name": "高品質短期信號",
            "category": TimeframeCategory.SHORT_TERM,
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
            "category": TimeframeCategory.MEDIUM_TERM,
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
            "category": TimeframeCategory.LONG_TERM,
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
    print("=" * 80)
    
    for test_case in test_cases:
        print(f"\n🎯 {test_case['name']}")
        print(f"   類別: {test_case['category'].value}")
        print(f"   品質評分: {test_case['quality_score']}")
        
        try:
            # 調用動態時間計算方法
            expires_at = sniper_system._calculate_dynamic_expiry(
                category=test_case['category'],
                quality_score=test_case['quality_score'],
                analysis_result=test_case['analysis_result']
            )
            
            # 計算小時數
            current_time = get_taiwan_now()
            time_diff = expires_at - current_time
            hours = time_diff.total_seconds() / 3600
            
            print(f"   計算結果: {hours:.1f}小時")
            print(f"   當前時間: {current_time}")
            print(f"   過期時間: {expires_at}")
            
            if hours != 24.0:
                print(f"   ✅ 動態計算成功！")
            else:
                print(f"   ⚠️  返回固定24小時")
                
        except Exception as e:
            print(f"   ❌ 計算失敗: {e}")
            import traceback
            print(f"   錯誤詳情: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_dynamic_calculation_direct())
