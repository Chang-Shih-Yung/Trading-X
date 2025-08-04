#!/usr/bin/env python3
"""
🔧 直接測試API錯誤
"""

import asyncio
import sys
import os

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.sniper_smart_layer import sniper_smart_layer

async def test_api_directly():
    """直接測試API調用"""
    print("🔧 直接測試狙擊手API調用")
    print("=" * 50)
    
    try:
        # 強制生成一個信號
        print("🚀 強制生成BTCUSDT信號...")
        success = await sniper_smart_layer.force_generate_signal('BTCUSDT')
        print(f"   結果: {'成功' if success else '失敗'}")
        
        # 檢查內存狀態
        print(f"📊 內存中活躍信號數量: {len(sniper_smart_layer.active_signals)}")
        
        if sniper_smart_layer.active_signals:
            print("📈 活躍信號:")
            for symbol, signal in sniper_smart_layer.active_signals.items():
                print(f"  💰 {symbol}: {signal.signal_type} @ ${signal.entry_price:.4f}")
        
        # 測試API方法
        print("\n🌐 測試get_all_active_signals()方法...")
        active_signals = await sniper_smart_layer.get_all_active_signals()
        print(f"   返回信號數量: {len(active_signals)}")
        
        if active_signals:
            print("   信號詳情:")
            for signal in active_signals:
                print(f"     • {signal.get('symbol')} - {signal.get('action')} @ ${signal.get('current_price', 0):.4f}")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_api_directly())

import asyncio
import sys
sys.path.append('.')

from app.api.v1.endpoints.sniper_smart_layer import get_smart_layer_signals

async def test_api_directly():
    """直接測試API端點"""
    print("🔧 直接測試智能分層API端點...")
    
    try:
        result = await get_smart_layer_signals(
            symbols=None,
            include_analysis=True,
            quality_threshold=6.0,
            max_signals_per_symbol=1
        )
        
        print(f"✅ API返回結果:")
        print(f"• 狀態: {result['status']}")
        print(f"• 信號數量: {result['total_count']}")
        print(f"• 品質分佈: {result['quality_distribution']}")
        
        if result['signals']:
            for signal in result['signals']:
                print(f"• {signal['symbol']}: 品質評分 {signal['quality_score']}")
        
    except Exception as e:
        print(f"❌ API測試失敗: {e}")

if __name__ == "__main__":
    asyncio.run(test_api_directly())
