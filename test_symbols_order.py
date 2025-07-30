#!/usr/bin/env python3
"""
🎯 交易對順序驗證測試
驗證所有 API 都返回正確的交易對順序：BTC/ETH/ADA/BNB/SOL/XRP/DOGE
"""

import asyncio
import aiohttp
import json

EXPECTED_ORDER = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT"]

async def test_api_endpoints():
    """測試各個 API 端點的交易對順序"""
    
    print("🎯 交易對順序驗證測試")
    print("=" * 60)
    print(f"預期順序: {' -> '.join(EXPECTED_ORDER)}")
    print()
    
    base_url = "http://localhost:8000"
    endpoints = [
        "/api/v1/scalping/phase3-market-depth",
        "/api/v1/scalping/dynamic-parameters",
        "/api/v1/scalping/prices"
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            try:
                print(f"📊 測試 {endpoint}")
                async with session.get(f"{base_url}{endpoint}") as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # 檢查不同端點的數據結構
                        if "symbol_analyses" in data:
                            # Phase 3 端點
                            symbols = [analysis["symbol"] for analysis in data["symbol_analyses"]]
                        elif "dynamic_parameters" in data:
                            # 動態參數端點
                            symbols = [param["symbol"] for param in data["dynamic_parameters"]]
                        elif "prices" in data:
                            # 價格端點
                            symbols = list(data["prices"].keys())
                        else:
                            print(f"   ❌ 未知數據結構")
                            continue
                        
                        print(f"   回傳順序: {' -> '.join(symbols)}")
                        
                        if symbols == EXPECTED_ORDER:
                            print(f"   ✅ 順序正確！")
                        else:
                            print(f"   ❌ 順序錯誤！")
                            print(f"      預期: {EXPECTED_ORDER}")
                            print(f"      實際: {symbols}")
                    else:
                        print(f"   ❌ API 錯誤: {response.status}")
                        
            except Exception as e:
                print(f"   ❌ 測試失敗: {e}")
            
            print()
    
    print("🎯 驗證完成")

if __name__ == "__main__":
    asyncio.run(test_api_endpoints())
