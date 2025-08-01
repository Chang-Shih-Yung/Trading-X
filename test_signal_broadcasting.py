#!/usr/bin/env python3
"""
WebSocket 信號廣播即時測試
"""
import asyncio
import aiohttp
import websockets
import json
from datetime import datetime

async def test_real_time_signal_broadcast():
    """測試實時信號廣播"""
    print("🎯 WebSocket 實時信號廣播測試")
    print("=" * 50)
    
    signal_count = 0
    messages_received = 0
    
    async def websocket_listener():
        """WebSocket 監聽器"""
        nonlocal signal_count, messages_received
        
        try:
            uri = "ws://localhost:8000/api/v1/realtime/ws"
            async with websockets.connect(uri) as websocket:
                print("✅ WebSocket 連接建立")
                
                # 發送訂閱消息
                subscribe_msg = {
                    "type": "subscribe",
                    "symbols": ["BTCUSDT", "ETHUSDT"]
                }
                await websocket.send(json.dumps(subscribe_msg))
                print("📡 已訂閱信號")
                
                # 監聽消息
                while True:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(message)
                        messages_received += 1
                        
                        if data.get('type') == 'trading_signal':
                            signal_count += 1
                            signal_data = data.get('data', {})
                            print(f"🎯 收到交易信號 #{signal_count}:")
                            print(f"   符號: {signal_data.get('symbol')}")
                            print(f"   類型: {signal_data.get('signal_type')}")
                            print(f"   價格: {signal_data.get('price')}")
                            print(f"   信心度: {signal_data.get('confidence'):.3f}")
                            print(f"   匯合數: {signal_data.get('confluence_count')}")
                        elif data.get('type') in ['price_update', 'heartbeat']:
                            # 靜默處理價格更新和心跳包
                            pass
                        else:
                            print(f"📨 其他消息: {data.get('type')}")
                            
                    except asyncio.TimeoutError:
                        continue
                    except websockets.exceptions.ConnectionClosed:
                        print("🔌 WebSocket 連接關閉")
                        break
                        
        except Exception as e:
            print(f"❌ WebSocket 錯誤: {e}")
    
    async def trigger_signals():
        """觸發信號生成"""
        await asyncio.sleep(2)  # 等待WebSocket連接建立
        
        print("🚀 觸發信號生成...")
        
        try:
            async with aiohttp.ClientSession() as session:
                url = "http://localhost:8000/api/v1/scalping/sniper-unified-data-layer"
                params = {
                    "symbols": "BTCUSDT,ETHUSDT",
                    "timeframe": "15m", 
                    "limit": 100,
                    "broadcast_signals": "true"
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        total_signals = data.get('total_signals_generated', 0)
                        broadcasts = data.get('websocket_broadcasts', 0)
                        print(f"✅ API 調用成功")
                        print(f"   生成信號: {total_signals}")
                        print(f"   廣播信號: {broadcasts}")
                    else:
                        print(f"❌ API 調用失敗: {response.status}")
                        
        except Exception as e:
            print(f"❌ API 調用錯誤: {e}")
    
    # 同時執行WebSocket監聽和信號觸發
    try:
        await asyncio.gather(
            websocket_listener(),
            trigger_signals(),
            return_exceptions=True
        )
    except KeyboardInterrupt:
        print("\n⏹️ 測試中斷")
    
    # 等待一段時間讓所有信號處理完成
    await asyncio.sleep(3)
    
    print(f"\n📊 測試總結:")
    print(f"   收到總消息數: {messages_received}")
    print(f"   收到交易信號數: {signal_count}")
    
    if signal_count > 0:
        print("✅ WebSocket 信號廣播測試成功！")
    else:
        print("⚠️ 未收到交易信號，可能需要檢查廣播邏輯")

if __name__ == "__main__":
    try:
        asyncio.run(test_real_time_signal_broadcast())
    except KeyboardInterrupt:
        print("\n👋 測試結束")
