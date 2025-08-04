#!/usr/bin/env python3
"""
測試WebSocket價格集成和增強統計
"""

import asyncio
import sys
sys.path.append('.')

async def test_price_integration():
    print("🧪 測試價格集成...")
    
    try:
        # 測試實時價格獲取
        from app.services.sniper_smart_layer import sniper_smart_layer
        
        # 測試單個價格獲取
        test_symbol = "BTCUSDT"
        print(f"📊 測試 {test_symbol} 實時價格...")
        
        price = await sniper_smart_layer._get_realtime_price(test_symbol)
        print(f"   {test_symbol} 價格: {price}")
        
        # 測試PnL計算
        test_signal = {
            'symbol': test_symbol,
            'entry_price': 50000.0,  # 假設入場價格
            'signal_type': 'BUY'
        }
        
        if price and price > 0:
            pnl = await sniper_smart_layer._calculate_current_pnl(test_signal, price)
            print(f"   模擬PnL計算: 入場 $50,000 -> 當前 ${price} = {pnl:.2f}%")
        
        # 測試統計功能（簡化版）
        print("\n📈 測試基礎統計...")
        stats = await sniper_smart_layer._get_performance_statistics()
        
        print(f"   總信號: {stats.get('total_signals', 0)}")
        print(f"   活躍信號: {stats.get('active_signals', 0)}")
        print(f"   傳統勝率: {stats.get('traditional_win_rate', 0):.1f}%")
        print(f"   真實成功率: {stats.get('real_success_rate', 0):.1f}%")
        
        # 檢查最近時間段統計
        recent_30 = stats.get('recent_30days', {})
        if recent_30:
            print(f"   近30天信號: {recent_30.get('signals', 0)}")
            print(f"   近30天平均PnL: {recent_30.get('avg_pnl', 0):.2f}%")
        
        print("✅ 價格集成測試完成")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_price_integration())
