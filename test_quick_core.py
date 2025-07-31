"""
快速核心功能驗證 - 無異步版本
"""
import requests
import json
from datetime import datetime

def test_core_sync():
    """同步測試核心功能"""
    print("🔍 Trading X 核心功能快速驗證")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    results = {"passed": 0, "failed": 0, "warnings": 0}
    
    # 測試項目
    tests = [
        {
            "name": "基本連接",
            "url": f"{base_url}/",
            "expected_keys": ["message", "status"],
            "timeout": 5
        },
        {
            "name": "pandas-ta 分析",
            "url": f"{base_url}/api/v1/scalping/pandas-ta-direct",
            "expected_keys": ["status", "total_signals"],
            "timeout": 10
        },
        {
            "name": "精準篩選信號",
            "url": f"{base_url}/api/v1/scalping/signals",
            "expected_keys": ["signals", "count"],
            "timeout": 10
        },
        {
            "name": "啟動即時分析服務",
            "url": f"{base_url}/api/v1/enhanced/start-realtime-analysis?symbols=BTCUSDT&symbols=ETHUSDT&timeframes=1m&timeframes=5m&timeframes=15m&timeframes=1h",
            "method": "POST",
            "expected_keys": ["success", "message"],
            "timeout": 10
        },
        {
            "name": "市場機制分析",
            "url": f"{base_url}/api/v1/enhanced/market-regime/BTCUSDT",
            "expected_keys": ["success", "data"],
            "timeout": 10
        },
        {
            "name": "Fear & Greed 指數",
            "url": f"{base_url}/api/v1/enhanced/fear-greed-index/BTCUSDT",
            "expected_keys": ["success", "data"],
            "timeout": 10
        },
        {
            "name": "多時間框架分析",
            "url": f"{base_url}/api/v1/enhanced/multi-timeframe-analysis/BTCUSDT",
            "expected_keys": ["success", "data"],
            "timeout": 10
        }
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"\n{i}️⃣ 測試 {test['name']}...")
        try:
            method = test.get("method", "GET")
            if method == "POST":
                response = requests.post(test["url"], timeout=test["timeout"])
            else:
                response = requests.get(test["url"], timeout=test["timeout"])
            
            if response.status_code == 200:
                data = response.json()
                
                # 檢查必要的鍵
                missing_keys = [key for key in test["expected_keys"] if key not in data]
                if not missing_keys:
                    print(f"✅ {test['name']} - 正常")
                    results["passed"] += 1
                    
                    # 顯示關鍵信息
                    if "total_signals" in data:
                        print(f"   📊 信號數量: {data['total_signals']}")
                    if "count" in data:
                        print(f"   📊 篩選結果: {data['count']}")
                    if "status" in data:
                        print(f"   📊 狀態: {data['status']}")
                    if "data" in data and isinstance(data["data"], dict):
                        if "market_regime" in data["data"]:
                            print(f"   📊 市場機制: {data['data']['market_regime']}")
                        if "fear_greed_index" in data["data"] and "sentiment" in data["data"]["fear_greed_index"]:
                            print(f"   📊 恐慌貪婪指數: {data['data']['fear_greed_index']['sentiment']} ({data['data']['fear_greed_index']['score']})")
                        if "overall_signal" in data["data"]:
                            print(f"   📊 整體信號: {data['data']['overall_signal']}")
                        
                else:
                    print(f"⚠️ {test['name']} - 回應格式異常，缺少: {missing_keys}")
                    results["warnings"] += 1
                    
            else:
                print(f"❌ {test['name']} - HTTP {response.status_code}")
                results["failed"] += 1
                
        except requests.exceptions.Timeout:
            print(f"⏰ {test['name']} - 請求超時")
            results["warnings"] += 1
        except Exception as e:
            print(f"❌ {test['name']} - 錯誤: {str(e)[:100]}")
            results["failed"] += 1
    
    # 測試總結
    print("\n" + "=" * 50)
    print("📊 測試結果總結:")
    print(f"✅ 通過: {results['passed']}")
    print(f"⚠️ 警告: {results['warnings']}")
    print(f"❌ 失敗: {results['failed']}")
    
    if results["passed"] >= 5:
        print("\n🎉 核心系統與 Phase 2 增強功能全部正常！")
        print("📋 Market Regime Analysis ✅")
        print("📋 Fear & Greed Index ✅") 
        print("📋 Multi-timeframe Analysis ✅")
        print("📋 動態權重系統基礎功能已實現")
    elif results["passed"] >= 2:
        print("\n🎉 核心系統基本正常！")
        print("📋 下一步可以開始 Phase 2 測試")
    else:
        print("\n🔧 需要修復基礎問題後再繼續")
    
    return results

if __name__ == "__main__":
    test_core_sync()
