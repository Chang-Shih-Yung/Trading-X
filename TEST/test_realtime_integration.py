"""
測試即時市場數據API整合
包括WebSocket和RESTful API測試
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

async def test_realtime_apis():
    """測試即時數據RESTful API"""
    print("🔄 測試即時市場數據API...")
    
    async with aiohttp.ClientSession() as session:
        try:
            # 1. 測試啟動即時數據服務
            print("\n1️⃣ 測試啟動即時數據服務...")
            async with session.post(f"{BASE_URL}/realtime/start") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 即時數據服務啟動成功")
                    print(f"   WebSocket模式: {result['data']['websocket_enabled']}")
                    print(f"   監控代號: {result['data']['symbols']}")
                else:
                    print(f"❌ 啟動失敗: {response.status}")
            
            # 等待數據初始化
            print("\n⏳ 等待5秒讓數據初始化...")
            await asyncio.sleep(5)
            
            # 2. 測試獲取服務狀態
            print("\n2️⃣ 測試服務狀態...")
            async with session.get(f"{BASE_URL}/realtime/status") as response:
                if response.status == 200:
                    result = await response.json()
                    status = result['data']
                    print(f"✅ 服務狀態查詢成功")
                    print(f"   運行中: {status['service_running']}")
                    print(f"   WebSocket啟用: {status['websocket_enabled']}")
                    print(f"   活躍連接: {status['active_websocket_connections']}")
                    print(f"   監控代號數: {status['total_symbols']}")
                else:
                    print(f"❌ 狀態查詢失敗: {response.status}")
            
            # 3. 測試獲取即時價格
            print("\n3️⃣ 測試即時價格...")
            async with session.get(f"{BASE_URL}/realtime/prices?symbols=BTCUSDT,ETHUSDT") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 即時價格獲取成功，數量: {result['count']}")
                    for symbol, data in result['data'].items():
                        print(f"   {symbol}: ${data['price']:.2f} ({data['change_percent']:+.2f}%)")
                else:
                    print(f"❌ 價格獲取失敗: {response.status}")
            
            # 4. 測試獲取深度數據
            print("\n4️⃣ 測試深度數據...")
            async with session.get(f"{BASE_URL}/realtime/depth/BTCUSDT") as response:
                if response.status == 200:
                    result = await response.json()
                    depth = result['data']
                    print(f"✅ 深度數據獲取成功")
                    if depth.get('bids') and depth.get('asks'):
                        best_bid = depth['bids'][0][0]
                        best_ask = depth['asks'][0][0]
                        spread = best_ask - best_bid
                        print(f"   最佳買價: ${best_bid:.2f}")
                        print(f"   最佳賣價: ${best_ask:.2f}")
                        print(f"   價差: ${spread:.2f}")
                else:
                    print(f"❌ 深度數據獲取失敗: {response.status}")
            
            # 5. 測試K線數據
            print("\n5️⃣ 測試K線數據...")
            async with session.get(f"{BASE_URL}/realtime/klines/BTCUSDT?interval=1m") as response:
                if response.status == 200:
                    result = await response.json()
                    kline = result['data']
                    print(f"✅ K線數據獲取成功")
                    print(f"   開盤: ${kline['open']:.2f}")
                    print(f"   最高: ${kline['high']:.2f}")
                    print(f"   最低: ${kline['low']:.2f}")
                    print(f"   收盤: ${kline['close']:.2f}")
                    print(f"   成交量: {kline['volume']:.2f}")
                else:
                    print(f"❌ K線數據獲取失敗: {response.status}")
            
            # 6. 測試市場總覽
            print("\n6️⃣ 測試市場總覽...")
            async with session.get(f"{BASE_URL}/realtime/summary") as response:
                if response.status == 200:
                    result = await response.json()
                    summary = result['data']
                    print(f"✅ 市場總覽獲取成功")
                    print(f"   總代號數: {summary['total_symbols']}")
                    print(f"   活躍代號: {summary['active_symbols']}")
                    print(f"   平均漲跌幅: {summary['avg_change_percent']}%")
                    print(f"   總成交量: {summary['total_volume']:.2f}")
                    
                    if summary['top_gainers']:
                        top_gainer = summary['top_gainers'][0]
                        print(f"   最大漲幅: {top_gainer['symbol']} (+{top_gainer['change_percent']:.2f}%)")
                else:
                    print(f"❌ 市場總覽獲取失敗: {response.status}")
            
            # 7. 測試獲取所有數據
            print("\n7️⃣ 測試獲取所有數據...")
            async with session.get(f"{BASE_URL}/realtime/all") as response:
                if response.status == 200:
                    result = await response.json()
                    all_data = result['data']
                    print(f"✅ 所有數據獲取成功")
                    print(f"   價格數據: {len(all_data.get('prices', {}))} 個")
                    print(f"   深度數據: {len(all_data.get('depths', {}))} 個")
                    print(f"   K線數據: {len(all_data.get('klines', {}))} 個")
                    print(f"   WebSocket狀態: {all_data.get('websocket_enabled', False)}")
                else:
                    print(f"❌ 所有數據獲取失敗: {response.status}")
                    
        except Exception as e:
            print(f"❌ API測試過程中發生錯誤: {e}")

async def test_websocket():
    """測試WebSocket連接"""
    print("\n🔄 測試WebSocket連接...")
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ WebSocket連接建立成功")
            
            # 發送訂閱消息
            subscribe_message = {
                "action": "subscribe",
                "symbols": ["BTCUSDT", "ETHUSDT"],
                "data_types": ["prices", "depths", "klines"]
            }
            
            await websocket.send(json.dumps(subscribe_message))
            print("📤 已發送訂閱消息")
            
            # 接收並處理消息
            message_count = 0
            start_time = time.time()
            
            while message_count < 10 and (time.time() - start_time) < 30:  # 最多接收10條消息或30秒
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    message_count += 1
                    
                    msg_type = data.get('type', 'unknown')
                    print(f"📨 收到消息 #{message_count}: {msg_type}")
                    
                    if msg_type == 'subscription_confirmed':
                        print(f"   ✅ 訂閱確認: {data.get('symbols', [])}")
                    elif msg_type == 'price_update':
                        price_data = data.get('data', {})
                        symbol = price_data.get('symbol', 'Unknown')
                        price = price_data.get('price', 0)
                        change = price_data.get('change_percent', 0)
                        print(f"   💰 {symbol}: ${price:.2f} ({change:+.2f}%)")
                    elif msg_type == 'price_batch_update':
                        batch_data = data.get('data', {})
                        prices = batch_data.get('prices', {})
                        print(f"   📊 批量更新: {len(prices)} 個價格")
                    
                except asyncio.TimeoutError:
                    print("⏰ WebSocket接收超時，繼續等待...")
                    continue
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析錯誤: {e}")
                    continue
            
            # 發送ping測試
            ping_message = {"action": "ping"}
            await websocket.send(json.dumps(ping_message))
            
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                if response_data.get('type') == 'pong':
                    print("🏓 Ping-Pong測試成功")
            except:
                print("❌ Ping-Pong測試失敗")
            
            # 取消訂閱
            unsubscribe_message = {"action": "unsubscribe"}
            await websocket.send(json.dumps(unsubscribe_message))
            print("📤 已發送取消訂閱消息")
            
            print(f"✅ WebSocket測試完成，共接收 {message_count} 條消息")
            
    except ConnectionRefusedError:
        print("❌ WebSocket連接被拒絕，請確保服務器正在運行")
    except Exception as e:
        print(f"❌ WebSocket測試錯誤: {e}")

async def test_performance():
    """測試API性能"""
    print("\n🔄 測試API性能...")
    
    async with aiohttp.ClientSession() as session:
        # 測試並發請求
        start_time = time.time()
        
        tasks = []
        for i in range(10):  # 10個並發請求
            task = session.get(f"{BASE_URL}/realtime/prices?symbols=BTCUSDT,ETHUSDT")
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        duration = end_time - start_time
        
        successful_requests = sum(1 for r in responses if hasattr(r, 'status') and r.status == 200)
        
        print(f"⚡ 性能測試結果:")
        print(f"   並發請求數: 10")
        print(f"   成功請求數: {successful_requests}")
        print(f"   總耗時: {duration:.2f}秒")
        print(f"   平均響應時間: {duration/10:.3f}秒")
        print(f"   每秒請求數: {10/duration:.1f} RPS")
        
        # 關閉所有響應
        for response in responses:
            if hasattr(response, 'close'):
                response.close()

async def main():
    """主測試流程"""
    print("🚀 開始測試即時市場數據API整合")
    print("=" * 50)
    
    try:
        # 測試RESTful API
        await test_realtime_apis()
        
        # 等待一下
        await asyncio.sleep(2)
        
        # 測試WebSocket
        await test_websocket()
        
        # 測試性能
        await test_performance()
        
        print("\n" + "=" * 50)
        print("🎉 測試完成！")
        
    except Exception as e:
        print(f"\n❌ 測試過程中發生嚴重錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("請先確保後端服務運行在 localhost:8000")
    print("運行命令: uvicorn main:app --reload")
    print("\n按Enter開始測試...")
    input()
    
    asyncio.run(main())
