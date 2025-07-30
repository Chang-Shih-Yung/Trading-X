#!/usr/bin/env python3
"""
系統性能與負載測試腳本
測試即時信號引擎在高負載下的性能表現
"""

import asyncio
import aiohttp
import websockets
import json
import time
import statistics
import logging
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import psutil
import threading

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/api/v1/realtime/ws"

class PerformanceLoadTester:
    """性能與負載測試器"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.ws_url = WS_URL
        self.test_metrics = {
            "response_times": [],
            "error_count": 0,
            "success_count": 0,
            "websocket_latency": [],
            "memory_usage": [],
            "cpu_usage": []
        }
        self.is_monitoring = False
        
    async def test_concurrent_requests(self, concurrent_users=10, duration_seconds=60):
        """測試並發請求性能"""
        logger.info(f"🧪 測試並發請求性能 ({concurrent_users} 用戶, {duration_seconds} 秒)...")
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        # 啟動系統監控
        self._start_system_monitoring()
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            # 創建並發任務
            for i in range(concurrent_users):
                task = asyncio.create_task(
                    self._concurrent_user_simulation(session, i, end_time)
                )
                tasks.append(task)
            
            # 等待所有任務完成
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # 停止系統監控
        self._stop_system_monitoring()
        
        # 分析結果
        await self._analyze_performance_results(concurrent_users, duration_seconds)
        
        return self._calculate_performance_score()
    
    async def _concurrent_user_simulation(self, session, user_id, end_time):
        """模擬併發用戶行為"""
        try:
            while time.time() < end_time:
                # 隨機選擇 API 調用
                api_calls = [
                    ("GET", "/api/v1/realtime-signals/status"),
                    ("POST", "/api/v1/realtime-signals/signals/test"),
                    ("GET", "/api/v1/realtime-signals/health"),
                    ("GET", "/api/v1/realtime-signals/signals/recent?hours=1")
                ]
                
                method, endpoint = api_calls[user_id % len(api_calls)]
                
                request_start = time.time()
                try:
                    if method == "GET":
                        async with session.get(f"{self.base_url}{endpoint}") as response:
                            await response.json()
                    elif method == "POST":
                        data = {"symbol": "BTCUSDT"} if "test" in endpoint else {}
                        async with session.post(f"{self.base_url}{endpoint}", json=data) as response:
                            await response.json()
                    
                    request_time = time.time() - request_start
                    self.test_metrics["response_times"].append(request_time)
                    self.test_metrics["success_count"] += 1
                    
                except Exception as e:
                    self.test_metrics["error_count"] += 1
                    logger.debug(f"用戶 {user_id} 請求失敗: {e}")
                
                # 模擬用戶思考時間
                await asyncio.sleep(0.1 + (user_id % 3) * 0.1)
                
        except Exception as e:
            logger.error(f"用戶 {user_id} 模擬失敗: {e}")
    
    async def test_websocket_load(self, concurrent_connections=20, duration_seconds=60):
        """測試 WebSocket 負載"""
        logger.info(f"🧪 測試 WebSocket 負載 ({concurrent_connections} 連接, {duration_seconds} 秒)...")
        
        tasks = []
        for i in range(concurrent_connections):
            task = asyncio.create_task(
                self._websocket_connection_test(i, duration_seconds)
            )
            tasks.append(task)
        
        # 等待所有連接測試完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 統計 WebSocket 性能
        successful_connections = sum(1 for r in results if r is True)
        connection_success_rate = (successful_connections / concurrent_connections) * 100
        
        logger.info(f"WebSocket 連接成功率: {connection_success_rate:.1f}%")
        
        if len(self.test_metrics["websocket_latency"]) > 0:
            avg_latency = statistics.mean(self.test_metrics["websocket_latency"])
            max_latency = max(self.test_metrics["websocket_latency"])
            logger.info(f"WebSocket 平均延遲: {avg_latency:.3f}秒")
            logger.info(f"WebSocket 最大延遲: {max_latency:.3f}秒")
        
        return connection_success_rate >= 80
    
    async def _websocket_connection_test(self, connection_id, duration_seconds):
        """單個 WebSocket 連接測試"""
        try:
            async with websockets.connect(self.ws_url) as websocket:
                # 發送訂閱消息
                subscribe_msg = {
                    "action": "subscribe",
                    "symbols": ["BTCUSDT"],
                    "data_types": ["prices", "signals"]
                }
                
                send_time = time.time()
                await websocket.send(json.dumps(subscribe_msg))
                
                # 等待響應並測量延遲
                start_time = time.time()
                end_time = start_time + duration_seconds
                
                while time.time() < end_time:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        receive_time = time.time()
                        latency = receive_time - send_time
                        self.test_metrics["websocket_latency"].append(latency)
                        send_time = receive_time  # 更新發送時間基準
                        
                    except asyncio.TimeoutError:
                        continue
                
                return True
                
        except Exception as e:
            logger.debug(f"WebSocket 連接 {connection_id} 失敗: {e}")
            return False
    
    async def test_memory_leak(self, iterations=100):
        """測試記憶體洩漏"""
        logger.info(f"🧪 測試記憶體洩漏 ({iterations} 次迭代)...")
        
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        logger.info(f"初始記憶體使用: {initial_memory:.2f} MB")
        
        memory_readings = [initial_memory]
        
        for i in range(iterations):
            # 執行各種操作
            async with aiohttp.ClientSession() as session:
                # API 調用
                async with session.post(f"{self.base_url}/api/v1/realtime-signals/signals/test") as response:
                    await response.json()
                
                # WebSocket 連接
                try:
                    async with websockets.connect(self.ws_url) as websocket:
                        await websocket.send(json.dumps({"action": "subscribe", "symbols": ["BTCUSDT"]}))
                        await asyncio.wait_for(websocket.recv(), timeout=1.0)
                except:
                    pass
            
            # 每10次迭代記錄記憶體使用
            if (i + 1) % 10 == 0:
                current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                memory_readings.append(current_memory)
                logger.info(f"迭代 {i+1}: 記憶體使用 {current_memory:.2f} MB")
                
                # 強制垃圾收集
                import gc
                gc.collect()
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        logger.info(f"最終記憶體使用: {final_memory:.2f} MB")
        logger.info(f"記憶體增長: {memory_increase:.2f} MB")
        
        # 檢查是否有明顯的記憶體洩漏（增長超過50MB認為異常）
        if memory_increase > 50:
            logger.warning("⚠️ 檢測到可能的記憶體洩漏")
            return False
        else:
            logger.info("✅ 未檢測到明顯記憶體洩漏")
            return True
    
    async def test_sustained_load(self, duration_minutes=10):
        """測試持續負載"""
        logger.info(f"🧪 測試持續負載 ({duration_minutes} 分鐘)...")
        
        duration_seconds = duration_minutes * 60
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        # 啟動系統監控
        self._start_system_monitoring()
        
        error_count = 0
        request_count = 0
        
        try:
            async with aiohttp.ClientSession() as session:
                while time.time() < end_time:
                    try:
                        # 定期執行各種操作
                        async with session.get(f"{self.base_url}/api/v1/realtime-signals/status") as response:
                            await response.json()
                            request_count += 1
                        
                        # 每分鐘生成一次測試信號
                        if request_count % 60 == 0:
                            async with session.post(f"{self.base_url}/api/v1/realtime-signals/signals/test") as response:
                                await response.json()
                        
                        await asyncio.sleep(1)  # 1秒間隔
                        
                    except Exception as e:
                        error_count += 1
                        logger.debug(f"持續負載測試請求失敗: {e}")
                        
                        if error_count > 10:  # 如果錯誤太多，提前結束
                            logger.error("錯誤過多，提前結束持續負載測試")
                            break
        
        finally:
            self._stop_system_monitoring()
        
        error_rate = (error_count / request_count) * 100 if request_count > 0 else 100
        logger.info(f"持續負載測試結果:")
        logger.info(f"  總請求數: {request_count}")
        logger.info(f"  錯誤數: {error_count}")
        logger.info(f"  錯誤率: {error_rate:.2f}%")
        
        return error_rate < 5  # 錯誤率低於5%認為通過
    
    def _start_system_monitoring(self):
        """開始系統監控"""
        self.is_monitoring = True
        
        def monitor():
            while self.is_monitoring:
                try:
                    # CPU 使用率
                    cpu_percent = psutil.cpu_percent(interval=1)
                    self.test_metrics["cpu_usage"].append(cpu_percent)
                    
                    # 記憶體使用率
                    memory_info = psutil.virtual_memory()
                    self.test_metrics["memory_usage"].append(memory_info.percent)
                    
                except Exception as e:
                    logger.debug(f"系統監控錯誤: {e}")
                
                time.sleep(1)
        
        # 在背景線程中運行監控
        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()
    
    def _stop_system_monitoring(self):
        """停止系統監控"""
        self.is_monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=2)
    
    async def _analyze_performance_results(self, concurrent_users, duration_seconds):
        """分析性能結果"""
        logger.info("\n📊 性能分析結果:")
        
        # 響應時間統計
        if self.test_metrics["response_times"]:
            avg_response = statistics.mean(self.test_metrics["response_times"])
            max_response = max(self.test_metrics["response_times"])
            min_response = min(self.test_metrics["response_times"])
            p95_response = statistics.quantiles(self.test_metrics["response_times"], n=20)[18]  # 95th percentile
            
            logger.info(f"  響應時間統計:")
            logger.info(f"    平均: {avg_response:.3f}秒")
            logger.info(f"    最大: {max_response:.3f}秒")
            logger.info(f"    最小: {min_response:.3f}秒")
            logger.info(f"    95th: {p95_response:.3f}秒")
        
        # 吞吐量統計
        total_requests = self.test_metrics["success_count"] + self.test_metrics["error_count"]
        throughput = total_requests / duration_seconds
        error_rate = (self.test_metrics["error_count"] / total_requests) * 100 if total_requests > 0 else 0
        
        logger.info(f"  吞吐量統計:")
        logger.info(f"    總請求數: {total_requests}")
        logger.info(f"    成功請求: {self.test_metrics['success_count']}")
        logger.info(f"    失敗請求: {self.test_metrics['error_count']}")
        logger.info(f"    吞吐量: {throughput:.2f} 請求/秒")
        logger.info(f"    錯誤率: {error_rate:.2f}%")
        
        # 系統資源統計
        if self.test_metrics["cpu_usage"]:
            avg_cpu = statistics.mean(self.test_metrics["cpu_usage"])
            max_cpu = max(self.test_metrics["cpu_usage"])
            logger.info(f"  CPU 使用率:")
            logger.info(f"    平均: {avg_cpu:.1f}%")
            logger.info(f"    最大: {max_cpu:.1f}%")
        
        if self.test_metrics["memory_usage"]:
            avg_memory = statistics.mean(self.test_metrics["memory_usage"])
            max_memory = max(self.test_metrics["memory_usage"])
            logger.info(f"  記憶體使用率:")
            logger.info(f"    平均: {avg_memory:.1f}%")
            logger.info(f"    最大: {max_memory:.1f}%")
    
    def _calculate_performance_score(self):
        """計算性能分數"""
        score = 100
        
        # 響應時間評分 (40分)
        if self.test_metrics["response_times"]:
            avg_response = statistics.mean(self.test_metrics["response_times"])
            if avg_response > 2.0:
                score -= 30
            elif avg_response > 1.0:
                score -= 20
            elif avg_response > 0.5:
                score -= 10
        
        # 錯誤率評分 (30分)
        total_requests = self.test_metrics["success_count"] + self.test_metrics["error_count"]
        if total_requests > 0:
            error_rate = (self.test_metrics["error_count"] / total_requests) * 100
            if error_rate > 10:
                score -= 30
            elif error_rate > 5:
                score -= 20
            elif error_rate > 1:
                score -= 10
        
        # 系統資源評分 (30分)
        if self.test_metrics["cpu_usage"]:
            max_cpu = max(self.test_metrics["cpu_usage"])
            if max_cpu > 90:
                score -= 20
            elif max_cpu > 80:
                score -= 10
        
        if self.test_metrics["memory_usage"]:
            max_memory = max(self.test_metrics["memory_usage"])
            if max_memory > 90:
                score -= 10
            elif max_memory > 80:
                score -= 5
        
        logger.info(f"\n🎯 性能評分: {score}/100")
        
        if score >= 80:
            logger.info("✅ 性能優秀")
        elif score >= 60:
            logger.info("⚠️ 性能良好")
        else:
            logger.warning("❌ 性能需要改善")
        
        return score >= 60

async def main():
    """主測試函數"""
    logger.info("🚀 開始性能與負載測試...")
    
    tester = PerformanceLoadTester()
    test_results = []
    
    # 測試項目
    tests = [
        ("並發請求性能 (10用戶/60秒)", lambda: tester.test_concurrent_requests(10, 60)),
        ("WebSocket負載測試 (10連接/30秒)", lambda: tester.test_websocket_load(10, 30)),
        ("記憶體洩漏測試 (50次迭代)", lambda: tester.test_memory_leak(50)),
        ("持續負載測試 (3分鐘)", lambda: tester.test_sustained_load(3)),
    ]
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 執行測試: {test_name}")
        try:
            result = await test_func()
            test_results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name} - 通過")
            else:
                logger.error(f"❌ {test_name} - 失敗")
                
            # 測試間隔
            await asyncio.sleep(5)
            
        except Exception as e:
            logger.error(f"❌ {test_name} - 異常: {e}")
            test_results.append((test_name, False))
    
    # 測試總結
    logger.info("\n📊 性能測試結果總結:")
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通過" if result else "❌ 失敗"
        logger.info(f"  {test_name}: {status}")
    
    logger.info(f"\n🎯 總計: {passed}/{total} 項測試通過")
    
    if passed == total:
        logger.info("🎉 所有性能測試通過！系統性能表現優秀")
        return True
    elif passed >= total * 0.75:
        logger.warning("⚠️ 大部分性能測試通過，系統性能可接受")
        return True
    else:
        logger.warning("❌ 多項性能測試失敗，系統性能需要改善")
        return False

if __name__ == "__main__":
    # 運行測試
    success = asyncio.run(main())
    exit(0 if success else 1)
