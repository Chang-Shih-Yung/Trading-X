#!/usr/bin/env python3
"""直接測試API錯誤"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.sniper_smart_layer import sniper_smart_layer

async def test_api():
    print("🔧 直接測試狙擊手API")
    try:
        # 強制生成信號
        success = await sniper_smart_layer.force_generate_signal('BTCUSDT')
        print(f"生成結果: {success}")
        
        # 檢查內存
        print(f"活躍信號數: {len(sniper_smart_layer.active_signals)}")
        
        # 測試API方法
        active_signals = await sniper_smart_layer.get_all_active_signals()
        print(f"API返回: {len(active_signals)}")
        
    except Exception as e:
        print(f"錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_api())
