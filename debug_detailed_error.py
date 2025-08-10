#!/usr/bin/env python3
"""詳細錯誤調試工具"""

import sys
import os
import asyncio
import traceback
import pandas as pd
import numpy as np

# 添加路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'X', 'backend', 'phase1_signal_generation', 'indicator_dependency'))

def setup_test_data():
    """設置測試數據"""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=200, freq='1min')
    
    # 生成價格數據
    base_price = 50000
    price_changes = np.random.randn(200) * 100
    close_prices = [base_price]
    
    for change in price_changes[1:]:
        close_prices.append(close_prices[-1] + change)
    
    close_prices = np.array(close_prices)
    
    # 確保所有價格為正數
    close_prices = np.abs(close_prices)
    
    data = pd.DataFrame({
        'timestamp': dates,
        'open': close_prices * (1 + np.random.randn(200) * 0.001),
        'high': close_prices * (1 + np.abs(np.random.randn(200) * 0.002)),
        'low': close_prices * (1 - np.abs(np.random.randn(200) * 0.002)),
        'close': close_prices,
        'volume': np.abs(np.random.randn(200) * 1000000) + 100000,
    })
    
    # 確保 high >= low 且 close 在合理範圍內
    data['high'] = np.maximum(data['high'], np.maximum(data['open'], data['close']))
    data['low'] = np.minimum(data['low'], np.minimum(data['open'], data['close']))
    
    return data

async def test_individual_layers():
    """測試每個層級"""
    try:
        from indicator_dependency_graph import IndicatorDependencyGraph
        
        engine = IndicatorDependencyGraph()
        test_data = setup_test_data()
        
        print("🧪 測試每個層級...")
        
        # 測試 Layer -1
        print("\n📊 測試 Layer -1 (數據同步)...")
        try:
            result = await engine._layer_minus1_data_sync("BTCUSDT", "1m")
            print(f"✅ Layer -1 成功: {type(result)}")
        except Exception as e:
            print(f"❌ Layer -1 失敗: {e}")
            traceback.print_exc()
            
        # 測試 Layer 0
        print("\n📊 測試 Layer 0 (原始數據)...")
        try:
            result = await engine._layer_0_raw_data(test_data, "BTCUSDT", "1m")
            print(f"✅ Layer 0 成功: 數據鍵: {list(result.keys())}")
        except Exception as e:
            print(f"❌ Layer 0 失敗: {e}")
            traceback.print_exc()
            
        # 測試後續層級
        print("\n📊 測試後續層級...")
        raw_data = {
            'BTCUSDT_1m_open': test_data['open'],
            'BTCUSDT_1m_high': test_data['high'],
            'BTCUSDT_1m_low': test_data['low'],
            'BTCUSDT_1m_close': test_data['close'],
            'BTCUSDT_1m_volume': test_data['volume']
        }
        
        try:
            layer_124 = await engine._parallel_layers_124(raw_data, "BTCUSDT", "1m")
            print(f"✅ Layers 1-2-4 成功")
        except Exception as e:
            print(f"❌ Layers 1-2-4 失敗: {e}")
            traceback.print_exc()
            return
            
        try:
            layer_3 = await engine._layer_3_standard_deviations(raw_data, layer_124, "BTCUSDT", "1m")
            print(f"✅ Layer 3 成功")
        except Exception as e:
            print(f"❌ Layer 3 失敗: {e}")
            traceback.print_exc()
            return
            
        try:
            layer_5 = await engine._layer_5_intermediate_calculations(layer_124, "BTCUSDT", "1m")
            print(f"✅ Layer 5 成功")
        except Exception as e:
            print(f"❌ Layer 5 失敗: {e}")
            traceback.print_exc()
            return
            
        try:
            final_indicators = await engine._layer_6_final_indicators(
                raw_data, layer_124, layer_3, layer_5, "BTCUSDT", "1m"
            )
            print(f"✅ Layer 6 成功: {len(final_indicators)} 個指標")
            print(f"📋 指標名稱: {list(final_indicators.keys())}")
        except Exception as e:
            print(f"❌ Layer 6 失敗: {e}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ 整體測試失敗: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_individual_layers())
