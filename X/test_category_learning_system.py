#!/usr/bin/env python3
"""
優先級2：幣種分群學習系統完整測試
測試時間權重 + 分群權重的組合學習機制
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import numpy as np

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.phase2_adaptive_learning.learning_core.adaptive_learning_engine import AdaptiveLearningCore, SignalPerformance

async def test_category_learning_system():
    """測試完整的分群學習系統"""
    print("🚀 優先級2：幣種分群學習系統完整測試")
    print("=" * 60)
    
    try:
        # 初始化學習引擎
        engine = AdaptiveLearningCore()
        
        # 1. 測試分群配置
        print("📊 第一階段：分群配置驗證")
        print("-" * 40)
        
        categories = ['major', 'alt', 'meme', 'payment']
        for category in categories:
            params = engine.category_optimized_params[category]
            print(f"🏷️ {category}類別策略:")
            print(f"   信號門檻: {params['signal_threshold']} (越高越保守)")
            print(f"   風險倍數: {params['risk_multiplier']} (越低越保守)")
            print(f"   動量權重: {params['momentum_weight']} (越高越激進)")
            print(f"   波動調整: {params['volatility_adjustment']} (調節敏感度)")
        
        print("\n" + "=" * 60)
        
        # 2. 模擬不同幣種的信號數據
        print("📈 第二階段：模擬分群信號數據")
        print("-" * 40)
        
        test_signals = [
            # 主流幣 - 穩定表現
            ('BTCUSDT', 0.75, 0.08, 1),   # 高信號強度，低收益，成功
            ('ETHUSDT', 0.70, 0.06, 1),   # 中高信號強度，低收益，成功
            ('BTCUSDT', 0.68, -0.02, 0),  # 中信號強度，小虧損，失敗
            
            # Meme幣 - 高波動表現
            ('DOGEUSDT', 0.60, 0.25, 1),  # 中信號強度，高收益，成功
            ('DOGEUSDT', 0.58, -0.15, 0), # 中信號強度，大虧損，失敗
            ('DOGEUSDT', 0.62, 0.30, 1),  # 中信號強度，高收益，成功
            
            # 支付幣 - 穩健表現
            ('XRPUSDT', 0.65, 0.12, 1),   # 中高信號強度，穩定收益，成功
            ('XRPUSDT', 0.63, 0.08, 1),   # 中信號強度，穩定收益，成功
            
            # 替代幣 - 平衡表現
            ('BNBUSDT', 0.62, 0.10, 1),   # 中信號強度，穩定收益，成功
            ('BNBUSDT', 0.59, -0.05, 0),  # 中信號強度，小虧損，失敗
        ]
        
        # 創建模擬信號並加入學習系統
        current_time = datetime.now()
        
        for i, (symbol, strength, outcome, success) in enumerate(test_signals):
            # 創建時間序列信號（最近的信號權重更高）
            signal_time = current_time - timedelta(hours=i*2)  # 每2小時一個信號
            
            performance = SignalPerformance(
                signal_id=f"test_{symbol}_{i}",
                symbol=symbol,
                signal_strength=strength,
                direction="LONG" if outcome > 0 else "SHORT",
                timestamp=signal_time,
                performance_score=0.8 if success else 0.2,
                actual_outcome=outcome
            )
            
            # 記錄到學習系統
            await engine.add_signal_performance(performance)
            
            # 分群學習記錄
            category = engine._get_symbol_category(symbol)
            engine.record_category_learning(symbol, {
                'success_rate': 0.8 if success else 0.2,
                'return_rate': outcome,
                'signal_strength': strength
            })
            
            print(f"📝 記錄信號: {symbol}({category}) - 強度:{strength:.2f}, 收益:{outcome:+.2f}, 成功:{bool(success)}")
        
        print("\n" + "=" * 60)
        
        # 3. 測試分群學習洞察
        print("🧠 第三階段：分群學習洞察分析")
        print("-" * 40)
        
        all_insights = engine.get_category_learning_insights()
        for category, insight in all_insights.items():
            if isinstance(insight, dict) and 'total_signals' in insight:
                print(f"🎯 {category}類別分析:")
                print(f"   總信號數: {insight['total_signals']}")
                print(f"   平均表現: {insight['recent_avg_performance']:.2%}")
                
                optimized = insight['optimized_params']
                print(f"   優化策略: 門檻{optimized['signal_threshold']}, 風險{optimized['risk_multiplier']}")
                print(f"   涵蓋幣種: {', '.join(insight.get('symbols', []))}")
                print()
        
        # 4. 測試時間權重 + 分群權重的組合效果
        print("⚖️ 第四階段：組合權重效果測試")
        print("-" * 40)
        
        performance_score = engine._evaluate_current_performance()
        print(f"📊 當前綜合表現分數: {performance_score:.4f}")
        
        # 測試不同幣種的權重效果
        test_weights = [
            ('BTCUSDT', 'major'),    # 1.2權重
            ('DOGEUSDT', 'meme'),    # 0.8權重  
            ('XRPUSDT', 'payment'),  # 1.1權重
            ('UNKNOWN', 'alt')       # 1.0權重（默認）
        ]
        
        print("\n🏋️ 權重效果對比:")
        for symbol, expected_category in test_weights:
            actual_category = engine._get_symbol_category(symbol)
            weight = engine._get_category_weight(symbol)
            params = engine.get_category_optimized_params(symbol)
            
            print(f"  💰 {symbol}:")
            print(f"     預期分類: {expected_category} -> 實際: {actual_category}")
            print(f"     學習權重: {weight}x")
            print(f"     策略參數: 門檻{params['signal_threshold']}, 風險{params['risk_multiplier']}")
        
        print("\n" + "=" * 60)
        
        # 5. 解釋UNKNOWN分類邏輯
        print("❓ 第五階段：UNKNOWN分類邏輯解釋")
        print("-" * 40)
        
        print("🎯 為什麼UNKNOWN歸類為alt？")
        print("   1. 🛡️ 產品級安全設計：未知=風險，採用中性策略")
        print("   2. ⚖️ 風險控制：alt類別權重1.0，不放大也不縮小")
        print("   3. 📊 參數平衡：使用標準參數組合，避免過度激進")
        print("   4. 🔄 學習機制：隨著數據累積，可動態調整分類")
        
        print("\n✅ 分群學習系統測試完成！")
        print("🎉 已實現：時間衰減 + 幣種分群的智能學習機制")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_category_learning_system())
