#!/usr/bin/env python3
"""簡潔的指標測試，使用直接數據"""

import sys
import pandas as pd
import numpy as np
import asyncio
import logging

# 路徑設置
sys.path.append("/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/indicator_dependency")

logging.basicConfig(level=logging.INFO)

def create_test_data():
    """創建標準測試數據"""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100, freq='1min')
    
    # 生成價格數據
    base_price = 50000
    close_prices = []
    current = base_price
    
    for i in range(100):
        change = np.random.normal(0, 50)
        current = max(current + change, 10000)  # 避免負價格
        close_prices.append(current)
    
    close_prices = np.array(close_prices)
    
    data = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices * (1 + np.random.normal(0, 0.001, 100)),
        'high': close_prices * (1 + np.abs(np.random.normal(0, 0.002, 100))),
        'low': close_prices * (1 - np.abs(np.random.normal(0, 0.002, 100))),
        'close': close_prices,
        'volume': np.abs(np.random.normal(1000000, 200000, 100)),
    })
    
    # 確保 OHLC 關係
    data['high'] = np.maximum(data['high'], np.maximum(data['open'], data['close']))
    data['low'] = np.minimum(data['low'], np.minimum(data['open'], data['close']))
    
    return data

async def test_direct_calculation():
    """直接測試計算邏輯"""
    from indicator_dependency_graph import IndicatorDependencyGraph
    
    print("🧪 直接測試指標計算...")
    
    # 使用自定義數據
    engine = IndicatorDependencyGraph()
    test_data = create_test_data()
    
    # 構造原始數據字典
    raw_data = {
        'BTCUSDT_1m_open': test_data['open'],
        'BTCUSDT_1m_high': test_data['high'],
        'BTCUSDT_1m_low': test_data['low'], 
        'BTCUSDT_1m_close': test_data['close'],
        'BTCUSDT_1m_volume': test_data['volume']
    }
    
    try:
        print("📊 執行完整計算流程...")
        
        # 測試各層級
        layer_124 = await engine._parallel_layers_124(raw_data, "BTCUSDT", "1m")
        print(f"✅ Layers 1-2-4: {len(layer_124)} 組")
        
        layer_3 = await engine._layer_3_standard_deviations(raw_data, layer_124, "BTCUSDT", "1m")
        print(f"✅ Layer 3: {len(layer_3)} 項")
        
        layer_5 = await engine._layer_5_intermediate_calculations(layer_124, "BTCUSDT", "1m")
        print(f"✅ Layer 5: {len(layer_5)} 項")
        
        final_indicators = await engine._layer_6_final_indicators(
            raw_data, layer_124, layer_3, layer_5, "BTCUSDT", "1m"
        )
        print(f"✅ Layer 6: {len(final_indicators)} 個指標")
        
        print("\n📋 成功計算的指標:")
        for name, indicator in final_indicators.items():
            print(f"  • {indicator.indicator_name}: {indicator.value:.4f}")
            
        return True
            
    except Exception as e:
        print(f"❌ 計算失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_direct_calculation())
    if success:
        print("\n🏆 直接測試成功！所有指標正常計算")
    else:
        print("\n💥 直接測試失敗")
