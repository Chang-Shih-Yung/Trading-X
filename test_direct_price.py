#!/usr/bin/env python3
"""
直接測試價格獲取功能
"""

import asyncio
import aiohttp
import sys
sys.path.append('.')

async def test_direct_price():
    print("🧪 直接測試價格獲取...")
    
    try:
        # 直接測試Binance API
        symbol = "BTCUSDT"
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    price = float(data['price'])
                    print(f"📊 {symbol} 當前價格: ${price:,.2f}")
                    
                    # 測試PnL計算
                    entry_price = 50000.0
                    pnl_buy = ((price - entry_price) / entry_price) * 100
                    pnl_sell = ((entry_price - price) / entry_price) * 100
                    
                    print(f"   BUY信號PnL: {pnl_buy:.2f}%")
                    print(f"   SELL信號PnL: {pnl_sell:.2f}%")
                    
                else:
                    print(f"❌ API請求失敗: {response.status}")
        
        # 測試WebSocket連接（如果可用）
        try:
            from app.services.binance_websocket_service import binance_websocket_service
            print("🔌 測試WebSocket服務...")
            
            # 嘗試獲取WebSocket價格
            ws_price = await binance_websocket_service.get_current_price(symbol.lower())
            if ws_price:
                print(f"   WebSocket價格: ${ws_price:,.2f}")
            else:
                print("   WebSocket價格獲取失敗")
                
        except Exception as ws_e:
            print(f"   WebSocket測試跳過: {ws_e}")
        
        print("✅ 直接價格測試完成")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_direct_price())
