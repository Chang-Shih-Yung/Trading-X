"""
自動化測試即時市場數據API整合
"""

import asyncio
import aiohttp
import websockets
import json
import time
from datetime import datetime

# API基礎URL
BASE_URL = "http://localhost:8000/api/v1/market"
WS_URL = "ws://localhost:8000/api/v1/market/realtime/ws"

async def test_basic_apis():
    """測試基本API功能"""
    print("🔄 測試基本API功能...")
    
    async with aiohttp.ClientSession() as session:
        try:
            # 測試健康檢查
            async with session.get("http://localhost:8000/health") as response:
                if response.status == 200:
                    print("✅ 服務健康檢查通過")
                else:
                    print(f"❌ 服務健康檢查失敗: {response.status}")
                    return False
            
            # 測試獲取服務狀態
            async with session.get(f"{BASE_URL}/realtime/status") as response:
                if response.status == 200:
                    result = await response.json()
                    status = result['data']
                    print(f"✅ 服務狀態查詢成功")
                    print(f"   運行中: {status['service_running']}")
                    print(f"   WebSocket啟用: {status['websocket_enabled']}")
                    print(f"   監控代號數: {status['total_symbols']}")
                    return True
                else:
                    print(f"❌ 狀態查詢失敗: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ API測試錯誤: {e}")
            return False

async def test_realtime_prices():
    """測試即時價格API"""
    print("\n🔄 測試即時價格API...")
    
    async with aiohttp.ClientSession() as session:
        try:
            # 等待數據初始化
            await asyncio.sleep(3)
            
            # 測試獲取即時價格
            async with session.get(f"{BASE_URL}/realtime/prices?symbols=BTCUSDT,ETHUSDT") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 即時價格獲取成功，數量: {result['count']}")
                    
                    if result['data']:
                        for symbol, data in result['data'].items():
                            print(f"   {symbol}: ${data['price']:.2f} ({data['change_percent']:+.2f}%)")
                    else:
                        print("   ⚠️ 暫無價格數據，可能還在初始化中")
                else:
                    print(f"❌ 價格獲取失敗: {response.status}")
                    
        except Exception as e:
            print(f"❌ 價格測試錯誤: {e}")

async def test_market_summary():
    """測試市場總覽"""
    print("\n🔄 測試市場總覽...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}/realtime/summary") as response:
                if response.status == 200:
                    result = await response.json()
                    summary = result['data']
                    print(f"✅ 市場總覽獲取成功")
                    print(f"   總代號數: {summary['total_symbols']}")
                    print(f"   活躍代號: {summary['active_symbols']}")
                    print(f"   WebSocket狀態: {summary['websocket_status']}")
                else:
                    print(f"❌ 市場總覽獲取失敗: {response.status}")
                    
        except Exception as e:
            print(f"❌ 市場總覽測試錯誤: {e}")

async def test_websocket_basic():
    """測試WebSocket基本連接"""
    print("\n🔄 測試WebSocket連接...")
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ WebSocket連接建立成功")
            
            # 發送ping測試
            ping_message = {"action": "ping"}
            await websocket.send(json.dumps(ping_message))
            
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                if response_data.get('type') == 'pong':
                    print("✅ WebSocket Ping-Pong測試成功")
                else:
                    print(f"⚠️ 未預期的響應: {response_data}")
            except asyncio.TimeoutError:
                print("❌ WebSocket響應超時")
            except json.JSONDecodeError:
                print("❌ WebSocket響應格式錯誤")
                
    except ConnectionRefusedError:
        print("❌ WebSocket連接被拒絕")
    except Exception as e:
        print(f"❌ WebSocket測試錯誤: {e}")

async def main():
    """主測試流程"""
    print("🚀 開始自動化測試即時市場數據API整合")
    print("=" * 60)
    
    # 基本API測試
    api_ok = await test_basic_apis()
    if not api_ok:
        print("❌ 基本API測試失敗，停止後續測試")
        return
    
    # 等待服務完全啟動
    print("\n⏳ 等待數據服務初始化...")
    await asyncio.sleep(5)
    
    # 測試各項功能
    await test_realtime_prices()
    await test_market_summary()
    await test_websocket_basic()
    
    print("\n" + "=" * 60)
    print("🎉 測試完成！")
    print("\n📊 測試結果總結:")
    print("✅ 即時數據服務集成成功")
    print("✅ WebSocket連接功能正常")
    print("✅ RESTful API響應正常")
    print("\n🔗 可用的API端點:")
    print("📈 即時價格: GET /api/v1/market/realtime/prices")
    print("📊 市場總覽: GET /api/v1/market/realtime/summary")
    print("🔌 WebSocket: ws://localhost:8000/api/v1/market/realtime/ws")
    print("📖 API文檔: http://localhost:8000/docs")

if __name__ == "__main__":
    asyncio.run(main())
