#!/usr/bin/env python3
"""
改進版即時市場數據測試腳本
測試修復後的API響應格式和WebSocket連接穩定性
"""

import asyncio
import aiohttp
import websockets
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

# 配置
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/api/v1/realtime/ws"

class RealtimeDataTester:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws_connection: Optional[websockets.WebSocketServerProtocol] = None
        self.test_results: Dict = {
            "api_tests": {},
            "websocket_tests": {},
            "start_time": datetime.now().isoformat(),
            "errors": []
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        if self.ws_connection:
            await self.ws_connection.close()
    
    def log_result(self, test_name: str, success: bool, message: str, data: any = None):
        """記錄測試結果"""
        result = {
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        if "api" in test_name.lower():
            self.test_results["api_tests"][test_name] = result
        else:
            self.test_results["websocket_tests"][test_name] = result
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        
        if not success:
            self.test_results["errors"].append(f"{test_name}: {message}")
    
    async def test_api_response_format(self):
        """測試API響應格式是否正確"""
        print("\n=== API響應格式測試 ===")
        
        test_endpoints = [
            ("/api/v1/realtime/prices", "實時價格"),
            ("/api/v1/realtime/all", "所有實時數據"),
            ("/api/v1/realtime/status", "服務狀態"),
        ]
        
        for endpoint, description in test_endpoints:
            try:
                async with self.session.get(f"{BASE_URL}{endpoint}") as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # 檢查必要的響應字段
                        required_fields = ["success", "data", "timestamp"]
                        missing_fields = [field for field in required_fields if field not in data]
                        
                        if missing_fields:
                            self.log_result(
                                f"API格式_{description}", 
                                False, 
                                f"響應缺少必要字段: {missing_fields}",
                                data
                            )
                        else:
                            # 檢查data字段的內容
                            if isinstance(data.get("data"), dict) and data["data"]:
                                self.log_result(
                                    f"API格式_{description}", 
                                    True, 
                                    "響應格式正確",
                                    {"status": response.status, "fields": list(data.keys())}
                                )
                            else:
                                self.log_result(
                                    f"API格式_{description}", 
                                    False, 
                                    "data字段為空或格式不正確",
                                    data
                                )
                    else:
                        self.log_result(
                            f"API格式_{description}", 
                            False, 
                            f"HTTP狀態碼錯誤: {response.status}"
                        )
                        
            except Exception as e:
                self.log_result(
                    f"API格式_{description}", 
                    False, 
                    f"請求失敗: {str(e)}"
                )
    
    async def test_price_data_content(self):
        """測試價格數據內容"""
        print("\n=== 價格數據內容測試 ===")
        
        try:
            async with self.session.get(f"{BASE_URL}/api/v1/realtime/prices?symbols=BTCUSDT,ETHUSDT") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success") and data.get("data", {}).get("prices"):
                        prices = data["data"]["prices"]
                        
                        for symbol, price_info in prices.items():
                            if isinstance(price_info, dict) and "price" in price_info:
                                price = price_info["price"]
                                if isinstance(price, (int, float)) and price > 0:
                                    self.log_result(
                                        f"價格數據_{symbol}", 
                                        True, 
                                        f"價格: ${price:,.2f}",
                                        price_info
                                    )
                                else:
                                    self.log_result(
                                        f"價格數據_{symbol}", 
                                        False, 
                                        f"價格格式錯誤: {price}"
                                    )
                            else:
                                self.log_result(
                                    f"價格數據_{symbol}", 
                                    False, 
                                    "價格信息格式錯誤",
                                    price_info
                                )
                    else:
                        self.log_result(
                            "價格數據_整體", 
                            False, 
                            "響應中沒有prices數據",
                            data
                        )
                else:
                    self.log_result(
                        "價格數據_請求", 
                        False, 
                        f"HTTP狀態碼: {response.status}"
                    )
                    
        except Exception as e:
            self.log_result(
                "價格數據_請求", 
                False, 
                f"請求異常: {str(e)}"
            )
    
    async def test_websocket_connection(self):
        """測試WebSocket連接和消息處理"""
        print("\n=== WebSocket連接測試 ===")
        
        try:
            # 建立WebSocket連接
            self.ws_connection = await websockets.connect(WS_URL)
            self.log_result("WebSocket連接", True, "連接建立成功")
            
            # 等待連接確認消息
            try:
                welcome_msg = await asyncio.wait_for(self.ws_connection.recv(), timeout=5.0)
                welcome_data = json.loads(welcome_msg)
                
                if welcome_data.get("type") == "connection_established":
                    self.log_result("WebSocket歡迎消息", True, "收到連接確認", welcome_data)
                else:
                    self.log_result("WebSocket歡迎消息", False, "未收到預期的連接確認", welcome_data)
                    
            except asyncio.TimeoutError:
                self.log_result("WebSocket歡迎消息", False, "5秒內未收到歡迎消息")
            
            # 測試訂閱功能
            await self.test_websocket_subscription()
            
            # 測試心跳
            await self.test_websocket_heartbeat()
            
        except Exception as e:
            self.log_result("WebSocket連接", False, f"連接失敗: {str(e)}")
    
    async def test_websocket_subscription(self):
        """測試WebSocket訂閱功能"""
        if not self.ws_connection:
            return
        
        try:
            # 發送訂閱請求
            subscribe_msg = {
                "action": "subscribe",
                "symbols": ["BTCUSDT", "ETHUSDT"]
            }
            
            await self.ws_connection.send(json.dumps(subscribe_msg))
            self.log_result("WebSocket訂閱發送", True, "訂閱請求已發送", subscribe_msg)
            
            # 等待訂閱確認
            try:
                response = await asyncio.wait_for(self.ws_connection.recv(), timeout=10.0)
                response_data = json.loads(response)
                
                if response_data.get("type") == "subscription_confirmed":
                    symbols = response_data.get("symbols", [])
                    self.log_result("WebSocket訂閱確認", True, f"訂閱確認: {symbols}", response_data)
                    
                    # 等待價格更新消息
                    await self.wait_for_price_updates()
                    
                else:
                    self.log_result("WebSocket訂閱確認", False, "未收到訂閱確認", response_data)
                    
            except asyncio.TimeoutError:
                self.log_result("WebSocket訂閱確認", False, "10秒內未收到訂閱確認")
                
        except Exception as e:
            self.log_result("WebSocket訂閱", False, f"訂閱測試失敗: {str(e)}")
    
    async def wait_for_price_updates(self):
        """等待價格更新消息"""
        received_updates = 0
        max_wait_time = 15  # 最多等待15秒
        start_time = time.time()
        
        try:
            while received_updates < 3 and (time.time() - start_time) < max_wait_time:
                try:
                    message = await asyncio.wait_for(self.ws_connection.recv(), timeout=5.0)
                    data = json.loads(message)
                    
                    if data.get("type") in ["price_update", "price_batch_update"]:
                        received_updates += 1
                        symbol = data.get("symbol", "批量更新")
                        self.log_result(
                            f"WebSocket價格更新_{received_updates}", 
                            True, 
                            f"收到{symbol}價格更新",
                            {"type": data.get("type"), "symbol": symbol}
                        )
                    elif data.get("type") == "heartbeat":
                        self.log_result("WebSocket心跳", True, "收到心跳包")
                    
                except asyncio.TimeoutError:
                    # 發送ping測試連接
                    await self.ws_connection.send(json.dumps({"action": "ping"}))
                    
        except Exception as e:
            self.log_result("WebSocket價格更新", False, f"等待更新時出錯: {str(e)}")
        
        if received_updates == 0:
            self.log_result("WebSocket價格更新", False, f"在{max_wait_time}秒內未收到任何價格更新")
    
    async def test_websocket_heartbeat(self):
        """測試WebSocket心跳機制"""
        if not self.ws_connection:
            return
        
        try:
            # 發送ping
            ping_msg = {"action": "ping"}
            await self.ws_connection.send(json.dumps(ping_msg))
            
            # 等待pong
            try:
                response = await asyncio.wait_for(self.ws_connection.recv(), timeout=5.0)
                response_data = json.loads(response)
                
                if response_data.get("type") == "pong":
                    self.log_result("WebSocket心跳", True, "ping-pong測試成功", response_data)
                else:
                    self.log_result("WebSocket心跳", False, "收到非pong響應", response_data)
                    
            except asyncio.TimeoutError:
                self.log_result("WebSocket心跳", False, "pong響應超時")
                
        except Exception as e:
            self.log_result("WebSocket心跳", False, f"心跳測試失敗: {str(e)}")
    
    async def test_service_status(self):
        """測試服務狀態"""
        print("\n=== 服務狀態測試 ===")
        
        try:
            async with self.session.get(f"{BASE_URL}/api/v1/realtime/status") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success") and data.get("data"):
                        status_data = data["data"]
                        
                        # 檢查關鍵狀態指標
                        checks = [
                            ("service_running", "服務運行狀態"),
                            ("websocket_enabled", "WebSocket啟用狀態"),
                            ("active_websocket_connections", "活躍WebSocket連接數"),
                        ]
                        
                        for field, description in checks:
                            if field in status_data:
                                value = status_data[field]
                                self.log_result(
                                    f"服務狀態_{description}", 
                                    True, 
                                    f"{description}: {value}",
                                    {field: value}
                                )
                            else:
                                self.log_result(
                                    f"服務狀態_{description}", 
                                    False, 
                                    f"狀態數據中缺少{field}字段"
                                )
                    else:
                        self.log_result("服務狀態_響應", False, "狀態響應格式錯誤", data)
                else:
                    self.log_result("服務狀態_請求", False, f"HTTP狀態碼: {response.status}")
                    
        except Exception as e:
            self.log_result("服務狀態_請求", False, f"請求失敗: {str(e)}")
    
    def print_summary(self):
        """打印測試總結"""
        print("\n" + "="*60)
        print("測試總結報告")
        print("="*60)
        
        total_tests = len(self.test_results["api_tests"]) + len(self.test_results["websocket_tests"])
        
        api_success = sum(1 for result in self.test_results["api_tests"].values() if result["success"])
        api_total = len(self.test_results["api_tests"])
        
        ws_success = sum(1 for result in self.test_results["websocket_tests"].values() if result["success"])
        ws_total = len(self.test_results["websocket_tests"])
        
        total_success = api_success + ws_success
        
        print(f"總測試數: {total_tests}")
        print(f"成功: {total_success} | 失敗: {total_tests - total_success}")
        print(f"API測試: {api_success}/{api_total} 成功")
        print(f"WebSocket測試: {ws_success}/{ws_total} 成功")
        print(f"成功率: {(total_success/total_tests*100):.1f}%" if total_tests > 0 else "無測試數據")
        
        if self.test_results["errors"]:
            print(f"\n錯誤列表 ({len(self.test_results['errors'])}):")
            for i, error in enumerate(self.test_results["errors"], 1):
                print(f"{i}. {error}")
        else:
            print("\n🎉 所有測試都通過了！")
        
        print(f"\n測試開始時間: {self.test_results['start_time']}")
        print(f"測試結束時間: {datetime.now().isoformat()}")

async def main():
    """主測試函數"""
    print("開始改進版即時市場數據測試...")
    print(f"測試目標: {BASE_URL}")
    
    async with RealtimeDataTester() as tester:
        # 執行所有測試
        await tester.test_service_status()
        await tester.test_api_response_format()
        await tester.test_price_data_content()
        await tester.test_websocket_connection()
        
        # 打印總結
        tester.print_summary()
        
        # 保存詳細結果
        with open("test_realtime_fixed_results.json", "w", encoding="utf-8") as f:
            json.dump(tester.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n詳細測試結果已保存到: test_realtime_fixed_results.json")

if __name__ == "__main__":
    asyncio.run(main())
