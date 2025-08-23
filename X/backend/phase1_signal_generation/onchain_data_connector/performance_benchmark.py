"""
⚡ 智能混合系統效能基準測試
Performance Benchmark for Smart Hybrid System
測試 WebSocket + Multicall 優化效果
"""

import asyncio
import time
import statistics
from datetime import datetime
from typing import List, Dict

class PerformanceBenchmark:
    """智能混合系統效能基準測試"""
    
    def __init__(self):
        self.results = {}
        
    async def benchmark_price_fetching(self, connector, symbols: List[str], iterations: int = 10):
        """基準測試價格獲取性能"""
        print(f"⚡ 基準測試價格獲取性能 ({iterations} 次迭代)")
        
        latencies = []
        success_count = 0
        
        for i in range(iterations):
            start_time = time.time()
            
            try:
                # 隨機選擇測試符號
                test_symbol = symbols[i % len(symbols)]
                price = await connector.get_price(test_symbol)
                
                end_time = time.time()
                latency = (end_time - start_time) * 1000  # 轉換為毫秒
                
                if price:
                    latencies.append(latency)
                    success_count += 1
                    print(f"   第{i+1}次 {test_symbol}: {latency:.2f}ms -> ${price:.4f}")
                else:
                    print(f"   第{i+1}次 {test_symbol}: 失敗")
                    
            except Exception as e:
                print(f"   第{i+1}次: 錯誤 - {e}")
            
            # 避免過於頻繁的請求
            if i < iterations - 1:
                await asyncio.sleep(0.1)
        
        if latencies:
            avg_latency = statistics.mean(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            median_latency = statistics.median(latencies)
            
            print(f"\n📊 延遲統計:")
            print(f"   平均延遲: {avg_latency:.2f}ms")
            print(f"   最小延遲: {min_latency:.2f}ms")
            print(f"   最大延遲: {max_latency:.2f}ms") 
            print(f"   中位延遲: {median_latency:.2f}ms")
            print(f"   成功率: {success_count}/{iterations} ({success_count/iterations*100:.1f}%)")
            
            # 評估效能等級
            if avg_latency < 500:
                print("   🎯 效能等級: 優秀 (<500ms)")
            elif avg_latency < 1000:
                print("   ✅ 效能等級: 良好 (<1000ms)")
            elif avg_latency < 2000:
                print("   ⚠️ 效能等級: 可接受 (<2000ms)")
            else:
                print("   ❌ 效能等級: 需要優化 (>2000ms)")
                
            return {
                'avg_latency': avg_latency,
                'min_latency': min_latency,
                'max_latency': max_latency,
                'median_latency': median_latency,
                'success_rate': success_count/iterations,
                'total_iterations': iterations
            }
        else:
            print("   ❌ 沒有成功的測試")
            return None
    
    async def benchmark_batch_fetching(self, connector, iterations: int = 5):
        """基準測試批量獲取性能"""
        print(f"\n🔥 基準測試批量獲取性能 ({iterations} 次迭代)")
        
        batch_latencies = []
        
        for i in range(iterations):
            start_time = time.time()
            
            try:
                all_prices = await connector.get_all_prices()
                end_time = time.time()
                
                batch_latency = (end_time - start_time) * 1000
                batch_latencies.append(batch_latency)
                
                print(f"   第{i+1}次批量: {batch_latency:.2f}ms -> {len(all_prices)} 個價格")
                
            except Exception as e:
                print(f"   第{i+1}次批量: 錯誤 - {e}")
            
            if i < iterations - 1:
                await asyncio.sleep(0.5)
        
        if batch_latencies:
            avg_batch_latency = statistics.mean(batch_latencies)
            min_batch_latency = min(batch_latencies)
            max_batch_latency = max(batch_latencies)
            
            print(f"\n📊 批量延遲統計:")
            print(f"   平均批量延遲: {avg_batch_latency:.2f}ms")
            print(f"   最小批量延遲: {min_batch_latency:.2f}ms")
            print(f"   最大批量延遲: {max_batch_latency:.2f}ms")
            
            # WebSocket + Multicall 效能目標
            if avg_batch_latency < 1000:
                print("   🚀 批量效能: 優秀 (<1000ms)")
            elif avg_batch_latency < 2000:
                print("   ✅ 批量效能: 良好 (<2000ms)")
            else:
                print("   ⚠️ 批量效能: 需要優化 (>2000ms)")
                
            return {
                'avg_batch_latency': avg_batch_latency,
                'min_batch_latency': min_batch_latency,
                'max_batch_latency': max_batch_latency
            }
        else:
            return None
    
    async def benchmark_fallback_mechanism(self, connector, symbols: List[str]):
        """基準測試回退機制性能"""
        print(f"\n🔄 基準測試回退機制性能")
        
        fallback_count = 0
        fallback_latencies = []
        
        # 獲取系統狀態
        status = await connector.get_system_status()
        symbols_on_fallback = status.get('symbols_on_fallback', [])
        
        if symbols_on_fallback:
            print(f"   檢測到 {len(symbols_on_fallback)} 個幣種正在使用回退機制:")
            
            for symbol in symbols_on_fallback:
                start_time = time.time()
                try:
                    price = await connector.get_price(symbol)
                    end_time = time.time()
                    
                    if price:
                        fallback_latency = (end_time - start_time) * 1000
                        fallback_latencies.append(fallback_latency)
                        fallback_count += 1
                        print(f"      {symbol}: {fallback_latency:.2f}ms (回退)")
                        
                except Exception as e:
                    print(f"      {symbol}: 回退失敗 - {e}")
            
            if fallback_latencies:
                avg_fallback_latency = statistics.mean(fallback_latencies)
                print(f"\n   回退機制平均延遲: {avg_fallback_latency:.2f}ms")
                print(f"   回退機制成功率: {fallback_count}/{len(symbols_on_fallback)}")
                
                return {
                    'avg_fallback_latency': avg_fallback_latency,
                    'fallback_success_rate': fallback_count/len(symbols_on_fallback),
                    'symbols_on_fallback': len(symbols_on_fallback)
                }
        else:
            print("   ✅ 沒有幣種使用回退機制 - 鏈上數據運行良好")
            return {'all_onchain': True}

async def run_performance_benchmark():
    """運行完整的效能基準測試"""
    
    print("⚡ 智能混合系統效能基準測試")
    print("=" * 70)
    
    try:
        # 創建模擬幣安回退
        class MockBinanceFallback:
            async def get_price(self, symbol: str) -> float:
                mock_prices = {
                    'BTC': 43500.0, 'ETH': 2650.0, 'BNB': 310.0,
                    'ADA': 0.45, 'DOGE': 0.08, 'XRP': 0.52, 'SOL': 98.0
                }
                await asyncio.sleep(0.05)  # 模擬網路延遲
                return mock_prices.get(symbol, 100.0)
        
        # 導入智能混合連接器
        from smart_hybrid_connector import SmartHybridPriceConnector
        
        mock_binance = MockBinanceFallback()
        connector = SmartHybridPriceConnector(binance_fallback=mock_binance)
        
        print("🚀 初始化智能混合連接器...")
        await connector.initialize()
        
        print("⚡ 啟動價格流...")
        await connector.start_price_streaming()
        
        print("⏳ 系統穩定等待...")
        await asyncio.sleep(3)
        
        # 創建基準測試實例
        benchmark = PerformanceBenchmark()
        
        # 測試符號
        test_symbols = ['BTC', 'ETH', 'BNB', 'ADA', 'DOGE', 'XRP', 'SOL']
        
        # 1. 單次價格獲取效能測試
        print("\n" + "="*50)
        single_results = await benchmark.benchmark_price_fetching(
            connector, test_symbols, iterations=15
        )
        
        # 2. 批量獲取效能測試
        print("\n" + "="*50)
        batch_results = await benchmark.benchmark_batch_fetching(
            connector, iterations=5
        )
        
        # 3. 回退機制效能測試
        print("\n" + "="*50)
        fallback_results = await benchmark.benchmark_fallback_mechanism(
            connector, test_symbols
        )
        
        # 最終效能報告
        print("\n" + "="*70)
        print("🏆 最終效能報告")
        print("="*70)
        
        if single_results:
            print(f"📈 單次獲取平均延遲: {single_results['avg_latency']:.2f}ms")
            print(f"📈 單次獲取成功率: {single_results['success_rate']*100:.1f}%")
        
        if batch_results:
            print(f"🔥 批量獲取平均延遲: {batch_results['avg_batch_latency']:.2f}ms")
        
        if fallback_results and not fallback_results.get('all_onchain'):
            print(f"🔄 回退機制平均延遲: {fallback_results['avg_fallback_latency']:.2f}ms")
        
        # 系統整體評估
        print("\n🎯 系統整體評估:")
        
        performance_score = 0
        
        if single_results and single_results['avg_latency'] < 1000:
            performance_score += 30
            print("   ✅ 單次獲取效能: 優秀")
        elif single_results and single_results['avg_latency'] < 2000:
            performance_score += 20
            print("   ⚠️ 單次獲取效能: 良好")
        else:
            print("   ❌ 單次獲取效能: 需要優化")
        
        if batch_results and batch_results['avg_batch_latency'] < 2000:
            performance_score += 35
            print("   ✅ 批量獲取效能: 優秀")
        elif batch_results and batch_results['avg_batch_latency'] < 3000:
            performance_score += 25
            print("   ⚠️ 批量獲取效能: 良好")
        else:
            print("   ❌ 批量獲取效能: 需要優化")
        
        if fallback_results:
            if fallback_results.get('all_onchain'):
                performance_score += 35
                print("   ✅ 回退機制: 鏈上數據穩定，無需回退")
            elif fallback_results.get('fallback_success_rate', 0) > 0.8:
                performance_score += 30
                print("   ✅ 回退機制: 運行正常")
            else:
                performance_score += 15
                print("   ⚠️ 回退機制: 部分功能正常")
        
        print(f"\n🏆 總體效能評分: {performance_score}/100")
        
        if performance_score >= 80:
            print("🎉 系統效能優秀，生產環境就緒!")
        elif performance_score >= 60:
            print("✅ 系統效能良好，可用於生產環境")
        else:
            print("⚠️ 系統效能需要進一步優化")
        
        print("\n🧹 清理測試資源...")
        await connector.stop()
        
    except Exception as e:
        print(f"\n❌ 基準測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_performance_benchmark())
