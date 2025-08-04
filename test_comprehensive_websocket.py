#!/usr/bin/env python3
"""
🎯 Trading X - 綜合 WebSocket 信號廣播測試
測試實時信號接收和API觸發廣播功能
"""

import asyncio
import websockets
import json
import requests
import time
from datetime import datetime

class WebSocketSignalTester:
    def __init__(self):
        self.websocket_url = "ws://localhost:8000/api/v1/realtime/ws"
        self.api_url = "http://localhost:8000/api/v1/scalping/sniper-unified-data-layer"
        self.received_signals = []
        self.connection_active = False
        
    async def listen_for_signals(self, duration=10):
        """監聽 WebSocket 信號"""
        print(f"🔊 開始監聽 WebSocket 信號 ({duration}秒)...")
        
        try:
            async with websockets.connect(self.websocket_url) as websocket:
                self.connection_active = True
                print("✅ WebSocket 連接建立成功")
                
                # 設置監聽超時
                end_time = time.time() + duration
                
                while time.time() < end_time and self.connection_active:
                    try:
                        # 等待消息，設置短超時避免阻塞
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        
                        try:
                            data = json.loads(message)
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            
                            # 檢查消息類型
                            if data.get('type') == 'trading_signal':
                                signal_data = data.get('data', {})
                                symbol = signal_data.get('symbol', 'Unknown')
                                confidence = signal_data.get('confidence', 0)
                                action = signal_data.get('signal_type', 'Unknown')  # 修復：使用 signal_type 而不是 action
                                
                                print(f"📡 [{timestamp}] 收到交易信號:")
                                print(f"   符號: {symbol}")
                                print(f"   動作: {action}")
                                print(f"   信心度: {confidence:.3f}")
                                
                                self.received_signals.append({
                                    'timestamp': timestamp,
                                    'symbol': symbol,
                                    'confidence': confidence,
                                    'action': action
                                })
                                
                            elif data.get('type') == 'price_update':
                                # 價格更新消息（較常見）
                                price_data = data.get('data', {})
                                symbol = price_data.get('symbol', 'Unknown')
                                price = price_data.get('price', 0)
                                print(f"💱 [{timestamp}] 價格更新: {symbol} = ${price}")
                                
                            else:
                                print(f"📨 [{timestamp}] 收到消息: {data.get('type', 'unknown')}")
                                
                        except json.JSONDecodeError:
                            print(f"⚠️  收到非JSON消息: {message[:100]}...")
                            
                    except asyncio.TimeoutError:
                        # 超時是正常的，繼續監聽
                        continue
                    except websockets.exceptions.ConnectionClosed:
                        print("❌ WebSocket 連接已關閉")
                        break
                        
        except Exception as e:
            print(f"❌ WebSocket 連接失敗: {e}")
            
        finally:
            self.connection_active = False
            
    def trigger_signal_generation(self):
        """觸發信號生成和廣播"""
        print("🚀 觸發信號生成...")
        
        try:
            params = {
                'symbols': 'BTCUSDT,ETHUSDT',
                'timeframe': '15m',
                'limit': 100,
                'broadcast_signals': 'true',
                'force_refresh': 'true'
            }
            
            response = requests.get(self.api_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                broadcasts = data.get('websocket_broadcasts', 0)
                print(f"✅ API 調用成功，廣播信號數: {broadcasts}")
                
                # 顯示信號摘要
                for symbol, result in data.get('results', {}).items():
                    if 'layer_two' in result and 'filter_results' in result['layer_two']:
                        signals = result['layer_two']['filter_results']['signals']
                        buy_signals = signals.get('buy_signals', [])
                        passed_count = sum(buy_signals)
                        print(f"📊 {symbol}: {passed_count} 個有效信號")
                        
                return broadcasts
            else:
                print(f"❌ API 調用失敗: {response.status_code}")
                return 0
                
        except Exception as e:
            print(f"❌ 觸發信號生成失敗: {e}")
            return 0
    
    async def run_comprehensive_test(self):
        """運行綜合測試"""
        print("🎯 Trading X - WebSocket 信號廣播綜合測試")
        print("=" * 50)
        
        # 第一階段：先監聽背景信號
        print("\n📍 階段 1: 監聽背景信號 (5秒)")
        listen_task = asyncio.create_task(self.listen_for_signals(5))
        await listen_task
        
        background_signals = len(self.received_signals)
        print(f"📊 背景信號數量: {background_signals}")
        
        # 第二階段：觸發信號並同時監聽
        print("\n📍 階段 2: 觸發信號生成並監聽 (10秒)")
        
        # 重置信號計數
        self.received_signals = []
        
        # 同時啟動監聽和觸發
        listen_task = asyncio.create_task(self.listen_for_signals(10))
        
        # 等待2秒讓WebSocket建立連接
        await asyncio.sleep(2)
        
        # 觸發信號生成
        broadcast_count = self.trigger_signal_generation()
        
        # 等待監聽完成
        await listen_task
        
        triggered_signals = len(self.received_signals)
        
        # 測試結果分析
        print("\n📈 測試結果分析:")
        print("=" * 30)
        print(f"API 廣播信號數: {broadcast_count}")
        print(f"WebSocket 接收信號數: {triggered_signals}")
        
        if triggered_signals > 0:
            print("✅ WebSocket 信號接收成功!")
            print("\n收到的信號詳情:")
            for i, signal in enumerate(self.received_signals, 1):
                print(f"  {i}. [{signal['timestamp']}] {signal['symbol']} - {signal['action']} (信心度: {signal['confidence']:.3f})")
        else:
            print("⚠️  未收到 WebSocket 信號")
            if broadcast_count > 0:
                print("   - API 顯示有廣播信號，但 WebSocket 未收到")
                print("   - 可能是廣播延遲或信號格式問題")
            else:
                print("   - API 也未產生廣播信號")
        
        # 連接測試
        if self.connection_active or triggered_signals > 0:
            print("✅ WebSocket 連接功能正常")
        else:
            print("❌ WebSocket 連接可能有問題")
            
        print("\n🎯 測試完成!")
        return broadcast_count, triggered_signals

async def main():
    tester = WebSocketSignalTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())
