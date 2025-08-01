#!/usr/bin/env python3
"""
🎯 WebSocket 信號廣播測試
測試系統是否能正確廣播交易信號到 WebSocket 客戶端
"""

import asyncio
import websockets
import json
from datetime import datetime
import sys

async def test_websocket_signal_broadcast():
    """測試 WebSocket 信號廣播功能"""
    
    websocket_url = "ws://localhost:8000/api/v1/realtime/ws"
    
    print("🎯 開始測試 WebSocket 信號廣播...")
    print(f"連接到: {websocket_url}")
    
    try:
        async with websockets.connect(websocket_url) as websocket:
            print("✅ WebSocket 連接建立成功")
            
            # 1. 等待連接確認消息
            try:
                welcome_message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                welcome_data = json.loads(welcome_message)
                print(f"📨 收到歡迎消息: {welcome_data.get('message', '無消息')}")
                
                if welcome_data.get('type') == 'connection_established':
                    print("✅ 連接確認消息正確")
                else:
                    print(f"⚠️  非預期的消息類型: {welcome_data.get('type')}")
                    
            except asyncio.TimeoutError:
                print("❌ 等待歡迎消息超時")
                return
            except Exception as e:
                print(f"❌ 處理歡迎消息時出錯: {e}")
                return
            
            # 2. 發送訂閱消息 (可選)
            subscribe_message = {
                "action": "subscribe",
                "symbols": ["BTCUSDT", "ETHUSDT"],
                "data_types": ["trading_signals", "prices"]
            }
            
            await websocket.send(json.dumps(subscribe_message))
            print("📡 已發送訂閱消息")
            
            # 3. 等待訂閱確認
            try:
                sub_confirm = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                sub_data = json.loads(sub_confirm)
                print(f"📨 訂閱確認: {sub_data}")
            except asyncio.TimeoutError:
                print("⚠️  未收到訂閱確認 (可能是正常的)")
            except Exception as e:
                print(f"⚠️  處理訂閱確認時出錯: {e}")
            
            # 4. 持續監聽消息
            print("\n🎧 開始監聽 WebSocket 消息...")
            print("⏰ 將監聽 30 秒，等待信號廣播...")
            print("💡 提示：可以在另一個終端觸發信號生成來測試廣播")
            
            message_count = 0
            signal_count = 0
            
            try:
                while True:
                    try:
                        # 等待消息，設置超時
                        message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                        message_count += 1
                        
                        try:
                            data = json.loads(message)
                            message_type = data.get('type', 'unknown')
                            timestamp = data.get('timestamp', 'no_timestamp')
                            
                            print(f"\n📨 消息 #{message_count} [{datetime.now().strftime('%H:%M:%S')}]")
                            print(f"   類型: {message_type}")
                            
                            if message_type == 'trading_signal':
                                signal_count += 1
                                signal_data = data.get('data', {})
                                print(f"🎯 交易信號 #{signal_count}:")
                                print(f"   交易對: {signal_data.get('symbol', 'N/A')}")
                                print(f"   信號類型: {signal_data.get('signal_type', 'N/A')}")
                                print(f"   信心度: {signal_data.get('confidence', 'N/A')}")
                                print(f"   進場價: {signal_data.get('entry_price', 'N/A')}")
                                print(f"   止損價: {signal_data.get('stop_loss', 'N/A')}")
                                print(f"   止盈價: {signal_data.get('take_profit', 'N/A')}")
                                print(f"   風險回報比: {signal_data.get('risk_reward_ratio', 'N/A')}")
                                print(f"   使用指標: {', '.join(signal_data.get('indicators_used', []))}")
                                print(f"   推理: {signal_data.get('reasoning', 'N/A')}")
                                print(f"   時間框架: {signal_data.get('timeframe', 'N/A')}")
                                print(f"   緊急程度: {signal_data.get('urgency', 'N/A')}")
                                
                            elif message_type == 'price_update':
                                symbol = data.get('symbol', 'N/A')
                                price_data = data.get('data', {})
                                price = price_data.get('price', 'N/A')
                                print(f"💰 價格更新: {symbol} = {price}")
                                
                            elif message_type == 'price_batch_update':
                                prices = data.get('data', {}).get('prices', {})
                                print(f"💰 批量價格更新: {len(prices)} 個交易對")
                                
                            elif message_type == 'heartbeat':
                                print(f"💓 心跳包")
                                
                            else:
                                print(f"   內容: {data}")
                                
                        except json.JSONDecodeError:
                            print(f"   原始消息: {message}")
                            
                    except asyncio.TimeoutError:
                        print(f"\n⏰ 30秒內未收到新消息，測試結束")
                        break
                        
            except Exception as e:
                print(f"\n❌ 監聽過程中出錯: {e}")
            
            # 5. 總結結果
            print(f"\n📊 測試總結:")
            print(f"   總消息數: {message_count}")
            print(f"   交易信號數: {signal_count}")
            
            if signal_count > 0:
                print("✅ WebSocket 信號廣播測試成功！")
                return True
            else:
                print("⚠️  未收到交易信號廣播")
                print("💡 可能原因：")
                print("   1. 沒有新信號生成")
                print("   2. 信號廣播功能未啟用")
                print("   3. 系統正在處理中")
                return False
                
    except websockets.exceptions.ConnectionClosed:
        print("❌ WebSocket 連接被服務器關閉")
        return False
    except ConnectionRefusedError:
        print("❌ 無法連接到 WebSocket 服務器，請確認後端是否運行")
        return False
    except Exception as e:
        print(f"❌ WebSocket 測試失敗: {e}")
        return False

async def trigger_signal_generation():
    """觸發信號生成，用於測試廣播"""
    import aiohttp
    
    print("\n🚀 同時觸發信號生成...")
    
    try:
        async with aiohttp.ClientSession() as session:
            url = "http://localhost:8000/api/v1/scalping/sniper-unified-data-layer"
            params = {
                "symbols": "BTCUSDT,ETHUSDT",
                "timeframe": "1h",
                "force_refresh": "true"
            }
            
            print(f"📡 調用 API: {url}")
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    total_signals = data.get('total_signals_generated', 0)
                    print(f"✅ 信號生成成功，總計 {total_signals} 個信號")
                    return True
                else:
                    print(f"❌ 信號生成失敗，HTTP {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ 觸發信號生成時出錯: {e}")
        return False

async def main():
    """主函數"""
    print("🎯 WebSocket 信號廣播完整測試")
    print("=" * 50)
    
    # 選項：是否同時觸發信號生成
    if len(sys.argv) > 1 and sys.argv[1] == "--generate":
        print("📢 模式：同時測試信號生成和廣播")
        
        # 創建並發任務
        websocket_task = asyncio.create_task(test_websocket_signal_broadcast())
        
        # 等待5秒讓WebSocket建立連接
        await asyncio.sleep(5)
        
        # 觸發信號生成
        await trigger_signal_generation()
        
        # 等待WebSocket測試完成
        result = await websocket_task
        
    else:
        print("📢 模式：僅測試 WebSocket 連接和監聽")
        print("💡 要同時測試信號生成，請使用: python test_websocket_signal_broadcast.py --generate")
        result = await test_websocket_signal_broadcast()
    
    if result:
        print("\n🎉 測試完成：WebSocket 信號廣播功能正常！")
        sys.exit(0)
    else:
        print("\n⚠️  測試完成：需要進一步檢查 WebSocket 廣播功能")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  測試被用戶中斷")
        sys.exit(130)
