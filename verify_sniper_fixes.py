#!/usr/bin/env python3
"""
狙擊手策略修復驗證測試
檢查是否還有模擬數據、固定價格計算等問題
"""

import asyncio
import aiohttp
import json
from datetime import datetime

class SniperFixVerificationTest:
    def __init__(self):
        self.base_url = "http://localhost:8000/api/v1/scalping"
        
    async def test_dashboard_signals(self):
        """測試儀表板信號是否使用真實數據"""
        print("🎯 測試 1: 檢查儀表板精準信號...")
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/dashboard-precision-signals") as response:
                    if response.status == 200:
                        data = await response.json()
                        signals = data.get('signals', [])
                        
                        print(f"✅ 獲取到 {len(signals)} 個信號")
                        
                        for signal in signals[:3]:  # 檢查前3個信號
                            symbol = signal.get('symbol')
                            entry_price = signal.get('entry_price', 0)
                            stop_loss = signal.get('stop_loss', 0)
                            take_profit = signal.get('take_profit', 0)
                            
                            # 檢查價格是否合理
                            if entry_price > 0:
                                risk_pct = abs(entry_price - stop_loss) / entry_price * 100
                                reward_pct = abs(take_profit - entry_price) / entry_price * 100
                                rr_ratio = reward_pct / risk_pct if risk_pct > 0 else 0
                                
                                print(f"📊 {symbol}:")
                                print(f"   進場價: ${entry_price:.6f}")
                                print(f"   止損價: ${stop_loss:.6f} (風險: {risk_pct:.2f}%)")
                                print(f"   止盈價: ${take_profit:.6f} (回報: {reward_pct:.2f}%)")
                                print(f"   風險回報比: {rr_ratio:.2f}:1")
                                
                                # 檢查是否為固定百分比
                                if abs(risk_pct - 3.0) < 0.1 and abs(reward_pct - 6.0) < 0.1:
                                    print(f"   ⚠️ 警告: {symbol} 可能仍使用固定 3%/6% 計算")
                                else:
                                    print(f"   ✅ {symbol} 使用動態價格計算")
                            
                            # 檢查處理時間
                            layer_one_time = signal.get('layer_one_time')
                            layer_two_time = signal.get('layer_two_time')
                            
                            if layer_one_time is not None and layer_two_time is not None:
                                print(f"   處理時間: Layer1={layer_one_time}ms, Layer2={layer_two_time}ms")
                                if layer_one_time == 0.0 and layer_two_time == 0.0:
                                    print(f"   ⚠️ 警告: {symbol} 處理時間為 0，可能有問題")
                                else:
                                    print(f"   ✅ {symbol} 處理時間正常")
                            
                            print()
                    else:
                        print(f"❌ API 請求失敗: {response.status}")
                        
            except Exception as e:
                print(f"❌ 測試失敗: {e}")
    
    async def test_price_reasonableness(self):
        """測試價格合理性"""
        print("🎯 測試 2: 檢查價格合理性...")
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/dashboard-precision-signals") as response:
                    if response.status == 200:
                        data = await response.json()
                        signals = data.get('signals', [])
                        
                        suspicious_count = 0
                        total_count = len(signals)
                        
                        for signal in signals:
                            symbol = signal.get('symbol')
                            entry_price = signal.get('entry_price', 0)
                            confidence = signal.get('confidence', 0)
                            
                            # 檢查價格範圍是否合理
                            price_ranges = {
                                'BTCUSDT': (25000, 80000),
                                'ETHUSDT': (1200, 5000),
                                'BNBUSDT': (200, 800),
                                'ADAUSDT': (0.2, 2.0),
                                'SOLUSDT': (10, 300),
                                'XRPUSDT': (0.3, 3.0),
                                'DOGEUSDT': (0.05, 1.0)
                            }
                            
                            if symbol in price_ranges:
                                min_price, max_price = price_ranges[symbol]
                                if not (min_price <= entry_price <= max_price):
                                    print(f"⚠️ {symbol} 價格異常: ${entry_price:.6f} (合理範圍: ${min_price}-${max_price})")
                                    suspicious_count += 1
                                else:
                                    print(f"✅ {symbol} 價格合理: ${entry_price:.6f}")
                            
                            # 檢查信心度是否為明顯的隨機值
                            if confidence in [0.6, 0.7, 0.8, 0.9]:
                                print(f"⚠️ {symbol} 信心度可能為固定值: {confidence}")
                                suspicious_count += 1
                        
                        print(f"\n📊 價格合理性檢查: {total_count - suspicious_count}/{total_count} 個信號正常")
                        
            except Exception as e:
                print(f"❌ 測試失敗: {e}")
    
    async def test_dynamic_parameters(self):
        """測試動態參數API"""
        print("🎯 測試 3: 檢查動態參數...")
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/dynamic-parameters") as response:
                    if response.status == 200:
                        data = await response.json()
                        dynamic_params = data.get('dynamic_parameters', [])
                        
                        print(f"✅ 獲取到 {len(dynamic_params)} 個動態參數集")
                        
                        for params in dynamic_params[:2]:  # 檢查前2個
                            symbol = params.get('symbol')
                            regime_info = params.get('regime_info', {})
                            
                            print(f"📊 {symbol}:")
                            print(f"   市場機制: {regime_info.get('primary_regime')}")
                            print(f"   恐懼貪婪指數: {regime_info.get('fear_greed_index')}")
                            print(f"   趨勢一致性: {regime_info.get('trend_alignment_score')}")
                            print()
                            
                    else:
                        print(f"❌ 動態參數 API 請求失敗: {response.status}")
                        
            except Exception as e:
                print(f"❌ 測試失敗: {e}")
    
    async def run_all_tests(self):
        """運行所有測試"""
        print("🔧 狙擊手策略修復驗證測試")
        print("=" * 50)
        print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        await self.test_dashboard_signals()
        print()
        await self.test_price_reasonableness() 
        print()
        await self.test_dynamic_parameters()
        
        print("\n" + "=" * 50)
        print("✅ 狙擊手策略修復驗證測試完成")

async def main():
    tester = SniperFixVerificationTest()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
