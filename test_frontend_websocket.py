#!/usr/bin/env python3
"""
前端 WebSocket 連接測試
測試與前端相同的 WebSocket 連接邏輯
"""

import asyncio
import websockets
import json
from datetime import datetime

async def test_frontend_websocket():
    """模擬前端 WebSocket 連接並測試信號接收"""
    
    websocket_url = "ws://localhost:8000/api/v1/realtime/ws"
    
    print("🔌 測試前端 WebSocket 連接...")
    print(f"連接到: {websocket_url}")
    
    try:
        async with websockets.connect(websocket_url) as websocket:
            print("✅ WebSocket 連接成功")
            
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
            
            # 2. 發送訂閱消息（模擬前端邏輯）
            subscribe_message = {
                "action": "subscribe",
                "symbols": ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT"],
                "data_types": ["trading_signals", "prices", "market_updates"]
            }
            
            await websocket.send(json.dumps(subscribe_message))
            print("📡 已發送訂閱消息:", subscribe_message)
            
            # 3. 等待訂閱確認
            try:
                confirmation_message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                confirmation_data = json.loads(confirmation_message)
                print(f"📨 收到訂閱確認: {confirmation_data.get('type', 'unknown')}")
                
                if confirmation_data.get('type') == 'subscription_confirmed':
                    print("✅ 訂閱確認成功")
                    print(f"   訂閱的符號: {confirmation_data.get('symbols', [])}")
                else:
                    print(f"⚠️  非預期的確認消息: {confirmation_data}")
                    
            except asyncio.TimeoutError:
                print("❌ 等待訂閱確認超時")
                return
            except Exception as e:
                print(f"❌ 處理訂閱確認時出錯: {e}")
                return
            
            # 4. 監聽訊息
            print("\n🎧 開始監聽 WebSocket 訊息 (30秒)...")
            print("💡 提示：可以在另一個終端觸發信號生成來測試接收")
            
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
                print("✅ WebSocket 信號接收測試成功！")
                return True
            else:
                print("⚠️  未收到交易信號")
                print("💡 可能原因：")
                print("   1. 沒有新信號生成")
                print("   2. 信號廣播功能未啟用")
                print("   3. 訂閱設置不正確")
                return False
                
    except websockets.exceptions.ConnectionClosed:
        print("❌ WebSocket 連接被服務器關閉")
        return False
    except ConnectionRefusedError:
        print("❌ 無法連接到 WebSocket 服務器")
        print("💡 請確保後端服務正在運行")
        return False
    except Exception as e:
        print(f"❌ WebSocket 測試失敗: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_frontend_websocket())
