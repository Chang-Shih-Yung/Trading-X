#!/usr/bin/env python3
"""
WebSocket 修復驗證測試
測試 ConnectionManager 修復後的穩定性
"""

import asyncio
import json
import time
import logging
import websockets
import requests
from datetime import datetime
import sys

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

class WebSocketStabilityTester:
    """WebSocket 穩定性測試器"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.websocket_url = "ws://localhost:8000/api/v1/realtime/ws"  # 修正路由
        self.test_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
        self.connections = []
        
    async def test_multiple_connections(self):
        """測試多個 WebSocket 連接的穩定性"""
        print("🔗 測試多個 WebSocket 連接...")
        
        try:
            # 建立3個同時連接
            for i in range(3):
                try:
                    ws = await websockets.connect(
                        self.websocket_url,
                        ping_interval=20,
                        ping_timeout=10
                    )
                    self.connections.append(ws)
                    print(f"✅ 連接 {i+1} 建立成功")
                    
                    # 等待歡迎消息
                    welcome_msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    welcome_data = json.loads(welcome_msg)
                    
                    if welcome_data.get("type") == "connection_established":
                        print(f"📡 連接 {i+1} 確認: {welcome_data.get('message')}")
                    
                except Exception as e:
                    print(f"❌ 連接 {i+1} 建立失敗: {e}")
            
            print(f"🎯 成功建立 {len(self.connections)} 個連接")
            
        except Exception as e:
            print(f"❌ 多連接測試失敗: {e}")
    
    async def test_concurrent_operations(self):
        """測試併發操作的穩定性"""
        print("⚡ 測試併發操作...")
        
        if not self.connections:
            print("❌ 沒有可用的連接")
            return
        
        try:
            # 同時向所有連接發送訂閱請求
            subscribe_tasks = []
            for i, ws in enumerate(self.connections):
                subscribe_msg = {
                    "action": "subscribe",
                    "symbols": self.test_symbols[i:i+2],  # 每個連接訂閱不同的符號
                    "data_types": ["prices", "signals"]
                }
                
                task = asyncio.create_task(
                    ws.send(json.dumps(subscribe_msg))
                )
                subscribe_tasks.append(task)
            
            # 等待所有訂閱完成
            await asyncio.gather(*subscribe_tasks, return_exceptions=True)
            print("✅ 所有訂閱請求已發送")
            
            # 接收訂閱確認
            for i, ws in enumerate(self.connections):
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    data = json.loads(response)
                    if data.get("type") == "subscription_confirmed":
                        print(f"✅ 連接 {i+1} 訂閱確認: {data.get('symbols')}")
                    else:
                        print(f"⚠️ 連接 {i+1} 意外響應: {data.get('type')}")
                except Exception as e:
                    print(f"❌ 連接 {i+1} 訂閱確認失敗: {e}")
            
        except Exception as e:
            print(f"❌ 併發操作測試失敗: {e}")
    
    async def test_data_streaming(self, duration=30):
        """測試數據流的穩定性"""
        print(f"📊 測試 {duration} 秒數據流...")
        
        if not self.connections:
            print("❌ 沒有可用的連接")
            return
        
        start_time = time.time()
        message_counts = [0] * len(self.connections)
        error_counts = [0] * len(self.connections)
        
        try:
            # 為每個連接創建數據接收任務
            async def receive_data(ws, connection_id):
                while time.time() - start_time < duration:
                    try:
                        message = await asyncio.wait_for(ws.recv(), timeout=2.0)
                        data = json.loads(message)
                        message_counts[connection_id] += 1
                        
                        if message_counts[connection_id] % 10 == 0:
                            print(f"📡 連接 {connection_id+1}: 已接收 {message_counts[connection_id]} 條消息")
                            
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        error_counts[connection_id] += 1
                        if error_counts[connection_id] <= 3:  # 只記錄前3個錯誤
                            print(f"⚠️ 連接 {connection_id+1} 錯誤: {e}")
            
            # 啟動所有接收任務
            receive_tasks = [
                asyncio.create_task(receive_data(ws, i)) 
                for i, ws in enumerate(self.connections)
            ]
            
            # 等待測試完成
            await asyncio.gather(*receive_tasks, return_exceptions=True)
            
            # 報告結果
            total_messages = sum(message_counts)
            total_errors = sum(error_counts)
            
            print(f"\n📊 數據流測試結果:")
            print(f"   ⏱️ 測試時間: {duration} 秒")
            print(f"   📈 總消息數: {total_messages}")
            print(f"   ❌ 總錯誤數: {total_errors}")
            print(f"   📊 平均頻率: {total_messages/duration:.1f} 消息/秒")
            
            for i, (msg_count, err_count) in enumerate(zip(message_counts, error_counts)):
                print(f"   🔗 連接 {i+1}: {msg_count} 消息, {err_count} 錯誤")
            
        except Exception as e:
            print(f"❌ 數據流測試失敗: {e}")
    
    async def test_connection_recovery(self):
        """測試連接恢復能力"""
        print("🔄 測試連接恢復能力...")
        
        if not self.connections:
            print("❌ 沒有可用的連接")
            return
        
        try:
            # 故意關閉一個連接
            test_ws = self.connections[0]
            await test_ws.close()
            print("🔌 故意關閉了一個連接")
            
            # 等待一段時間
            await asyncio.sleep(5)
            
            # 嘗試重新建立連接
            new_ws = await websockets.connect(
                self.websocket_url,
                ping_interval=20,
                ping_timeout=10
            )
            
            # 替換舊連接
            self.connections[0] = new_ws
            print("✅ 成功重新建立連接")
            
            # 驗證新連接工作正常
            welcome_msg = await asyncio.wait_for(new_ws.recv(), timeout=5.0)
            welcome_data = json.loads(welcome_msg)
            
            if welcome_data.get("type") == "connection_established":
                print("✅ 新連接工作正常")
            else:
                print("⚠️ 新連接響應異常")
            
        except Exception as e:
            print(f"❌ 連接恢復測試失敗: {e}")
    
    async def cleanup_connections(self):
        """清理所有連接"""
        print("🧹 清理連接...")
        
        cleanup_tasks = []
        for i, ws in enumerate(self.connections):
            if ws and not ws.closed:
                task = asyncio.create_task(ws.close())
                cleanup_tasks.append(task)
        
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        print(f"✅ 已清理 {len(cleanup_tasks)} 個連接")
    
    async def run_stability_test(self):
        """運行完整的穩定性測試"""
        print("🎯 開始 WebSocket 穩定性測試")
        print("=" * 50)
        
        try:
            # 檢查後端服務
            try:
                response = requests.get(f"{self.backend_url}/health", timeout=5)
                if response.status_code == 200:
                    print("✅ 後端服務正常")
                else:
                    print(f"⚠️ 後端服務狀態: {response.status_code}")
            except Exception as e:
                print(f"❌ 無法連接後端服務: {e}")
                return
            
            # 測試步驟
            await self.test_multiple_connections()
            await asyncio.sleep(2)
            
            await self.test_concurrent_operations()
            await asyncio.sleep(2)
            
            await self.test_data_streaming(duration=20)
            await asyncio.sleep(2)
            
            await self.test_connection_recovery()
            
            print("\n🎉 WebSocket 穩定性測試完成！")
            
        except Exception as e:
            print(f"❌ 測試過程中發生錯誤: {e}")
            
        finally:
            await self.cleanup_connections()

async def main():
    tester = WebSocketStabilityTester()
    await tester.run_stability_test()

if __name__ == "__main__":
    asyncio.run(main())
