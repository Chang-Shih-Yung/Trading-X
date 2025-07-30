#!/usr/bin/env python3
"""
測試 WebSocket 連接狀態
"""

import asyncio
import json
import aiohttp

async def test_websocket_status():
    """測試 WebSocket 服務狀態"""
    
    try:
        # 測試服務狀態
        async with aiohttp.ClientSession() as session:
            # 基本健康檢查
            async with session.get('http://localhost:8000/health') as resp:
                health_data = await resp.json()
                print("🔍 服務健康狀態:")
                print(json.dumps(health_data, indent=2))
                
            # 實時數據狀態
            async with session.get('http://localhost:8000/api/v1/realtime/status') as resp:
                status_data = await resp.json()
                print("\n📊 實時數據狀態:")
                print(json.dumps(status_data, indent=2))
                
            # 市場數據統計
            async with session.get('http://localhost:8000/api/v1/market/data-stats') as resp:
                if resp.status == 200:
                    stats_data = await resp.json()
                    print("\n📈 數據統計:")
                    print(json.dumps(stats_data, indent=2))
                else:
                    print(f"\n❌ 無法獲取數據統計: {resp.status}")
                    
            # 測試實時價格
            async with session.get('http://localhost:8000/api/v1/realtime/prices') as resp:
                if resp.status == 200:
                    prices_data = await resp.json()
                    print("\n💰 實時價格:")
                    print(json.dumps(prices_data, indent=2)[:500] + "...")
                else:
                    print(f"\n❌ 無法獲取實時價格: {resp.status}")
                
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_status())
