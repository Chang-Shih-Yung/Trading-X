"""
🎯 Trading X - 性能測試：系統性能基準測試
測試系統在不同負載下的性能表現
"""

import unittest
import asyncio
import time
import statistics
from datetime import datetime
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import json

class PerformanceMetrics:
    """性能指標收集器"""
    
    def __init__(self):
        self.metrics = {
            "response_times": [],
            "throughput": 0,
            "error_rate": 0,
            "memory_usage": [],
            "concurrent_users": 0
        }
    
    def add_response_time(self, response_time: float):
        """添加響應時間"""
        self.metrics["response_times"].append(response_time)
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """計算統計指標"""
        response_times = self.metrics["response_times"]
        
        if not response_times:
            return self.metrics
        
        return {
            **self.metrics,
            "avg_response_time": statistics.mean(response_times),
            "median_response_time": statistics.median(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "p95_response_time": self._percentile(response_times, 95),
            "p99_response_time": self._percentile(response_times, 99)
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """計算百分位數"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]

class MockHighPerformanceEngine:
    """模擬高性能處理引擎"""
    
    def __init__(self):
        self.processed_count = 0
        self.error_count = 0
        self.processing_delay = 0.01  # 10ms 基準延遲
    
    async def process_signal(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理信號（模擬計算密集操作）"""
        start_time = time.time()
        
        try:
            # 模擬技術指標計算
            await asyncio.sleep(self.processing_delay)
            
            # 模擬複雜計算
            result = {
                "signal_id": signal_data.get("id", "unknown"),
                "symbol": signal_data.get("symbol", "BTCUSDT"),
                "processed_at": datetime.now().isoformat(),
                "computation_result": sum(range(100)),  # 簡單計算
                "status": "success"
            }
            
            self.processed_count += 1
            
        except Exception as e:
            self.error_count += 1
            result = {
                "signal_id": signal_data.get("id", "unknown"),
                "status": "error",
                "error": str(e)
            }
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        return {
            **result,
            "processing_time": processing_time
        }
    
    async def batch_process(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批次處理信號"""
        tasks = [self.process_signal(signal) for signal in signals]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 處理異常
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                self.error_count += 1
                processed_results.append({
                    "status": "error",
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results

class TestSystemPerformance(unittest.TestCase):
    """測試系統性能"""
    
    def setUp(self):
        """設置性能測試環境"""
        self.engine = MockHighPerformanceEngine()
        self.metrics = PerformanceMetrics()
    
    def test_single_signal_latency(self):
        """測試單信號處理延遲"""
        signal = {"id": "test_001", "symbol": "BTCUSDT", "data": "test_data"}
        
        async def run_latency_test():
            results = []
            
            # 執行多次測試
            for i in range(100):
                start_time = time.time()
                result = await self.engine.process_signal(signal)
                end_time = time.time()
                
                response_time = end_time - start_time
                self.metrics.add_response_time(response_time)
                results.append(result)
            
            return results
        
        results = asyncio.run(run_latency_test())
        stats = self.metrics.calculate_statistics()
        
        # 性能斷言
        self.assertEqual(len(results), 100)
        self.assertLess(stats["avg_response_time"], 0.1)  # 平均響應時間 < 100ms
        self.assertLess(stats["p95_response_time"], 0.2)  # 95%響應時間 < 200ms
        
        print(f"📊 單信號處理性能:")
        print(f"   平均響應時間: {stats['avg_response_time']:.3f}s")
        print(f"   P95響應時間: {stats['p95_response_time']:.3f}s")
        print(f"   P99響應時間: {stats['p99_response_time']:.3f}s")
    
    def test_batch_processing_throughput(self):
        """測試批次處理吞吐量"""
        batch_sizes = [10, 50, 100, 500]
        
        async def run_throughput_test():
            throughput_results = {}
            
            for batch_size in batch_sizes:
                signals = [
                    {"id": f"batch_{i}", "symbol": "BTCUSDT", "data": f"data_{i}"}
                    for i in range(batch_size)
                ]
                
                start_time = time.time()
                results = await self.engine.batch_process(signals)
                end_time = time.time()
                
                processing_time = end_time - start_time
                throughput = batch_size / processing_time
                
                throughput_results[batch_size] = {
                    "processing_time": processing_time,
                    "throughput": throughput,
                    "success_count": sum(1 for r in results if r.get("status") == "success")
                }
                
                # 性能斷言
                self.assertEqual(len(results), batch_size)
                self.assertGreater(throughput, 10)  # 至少 10 信號/秒
            
            return throughput_results
        
        throughput_results = asyncio.run(run_throughput_test())
        
        print(f"📊 批次處理吞吐量測試:")
        for batch_size, result in throughput_results.items():
            print(f"   批次大小 {batch_size}: {result['throughput']:.1f} 信號/秒")
    
    def test_concurrent_processing_stress(self):
        """測試並發處理壓力"""
        concurrent_levels = [1, 5, 10, 20]
        
        async def run_stress_test():
            stress_results = {}
            
            for concurrent_level in concurrent_levels:
                signals = [
                    {"id": f"stress_{i}", "symbol": "BTCUSDT"}
                    for i in range(concurrent_level * 10)
                ]
                
                start_time = time.time()
                
                # 分批並發處理
                batch_size = 10
                tasks = []
                for i in range(0, len(signals), batch_size):
                    batch = signals[i:i + batch_size]
                    task = self.engine.batch_process(batch)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks)
                end_time = time.time()
                
                # 計算結果
                total_processed = sum(len(batch_result) for batch_result in results)
                processing_time = end_time - start_time
                throughput = total_processed / processing_time
                
                stress_results[concurrent_level] = {
                    "total_processed": total_processed,
                    "processing_time": processing_time,
                    "throughput": throughput,
                    "error_rate": self.engine.error_count / total_processed if total_processed > 0 else 0
                }
                
                # 性能斷言
                self.assertGreater(throughput, 5)  # 壓力下至少 5 信號/秒
                self.assertLess(stress_results[concurrent_level]["error_rate"], 0.1)  # 錯誤率 < 10%
            
            return stress_results
        
        stress_results = asyncio.run(run_stress_test())
        
        print(f"📊 並發壓力測試:")
        for level, result in stress_results.items():
            print(f"   並發級別 {level}: {result['throughput']:.1f} 信號/秒, 錯誤率: {result['error_rate']:.2%}")
    
    def test_memory_usage_monitoring(self):
        """測試記憶體使用監控"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        async def run_memory_test():
            memory_readings = []
            
            # 基準記憶體
            baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_readings.append(baseline_memory)
            
            # 處理大量數據
            for batch_num in range(10):
                signals = [
                    {"id": f"mem_test_{i}", "symbol": "BTCUSDT", "large_data": "x" * 1000}
                    for i in range(100)
                ]
                
                await self.engine.batch_process(signals)
                
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_readings.append(current_memory)
            
            return memory_readings
        
        memory_readings = asyncio.run(run_memory_test())
        
        memory_increase = max(memory_readings) - min(memory_readings)
        
        # 記憶體使用斷言
        self.assertLess(memory_increase, 100)  # 記憶體增長 < 100MB
        
        print(f"📊 記憶體使用測試:")
        print(f"   基準記憶體: {memory_readings[0]:.1f} MB")
        print(f"   最大記憶體: {max(memory_readings):.1f} MB")
        print(f"   記憶體增長: {memory_increase:.1f} MB")
    
    def test_sustained_load_endurance(self):
        """測試持續負載耐力"""
        async def run_endurance_test():
            start_time = time.time()
            test_duration = 10  # 10秒耐力測試
            
            total_processed = 0
            error_count = 0
            
            while time.time() - start_time < test_duration:
                signals = [
                    {"id": f"endurance_{i}", "symbol": "BTCUSDT"}
                    for i in range(20)
                ]
                
                try:
                    results = await self.engine.batch_process(signals)
                    total_processed += len(results)
                    error_count += sum(1 for r in results if r.get("status") == "error")
                except Exception as e:
                    error_count += len(signals)
                
                # 短暫休息避免過載
                await asyncio.sleep(0.1)
            
            actual_duration = time.time() - start_time
            throughput = total_processed / actual_duration
            error_rate = error_count / total_processed if total_processed > 0 else 1
            
            return {
                "duration": actual_duration,
                "total_processed": total_processed,
                "throughput": throughput,
                "error_rate": error_rate
            }
        
        result = asyncio.run(run_endurance_test())
        
        # 耐力測試斷言
        self.assertGreater(result["throughput"], 50)  # 持續吞吐量 > 50 信號/秒
        self.assertLess(result["error_rate"], 0.05)   # 錯誤率 < 5%
        
        print(f"📊 持續負載耐力測試 ({result['duration']:.1f}s):")
        print(f"   總處理數量: {result['total_processed']}")
        print(f"   持續吞吐量: {result['throughput']:.1f} 信號/秒")
        print(f"   錯誤率: {result['error_rate']:.2%}")

if __name__ == "__main__":
    print("🧪 執行系統性能基準測試...")
    print("⚠️  注意：性能測試可能需要較長時間")
    unittest.main(verbosity=2)
