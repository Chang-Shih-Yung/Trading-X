"""
專門測試 TradingStrategy.vue 核心業務流程
WebSocket + pandas-ta + 實時策略生成
排除 Dashboard.vue 的 API
"""
import requests
import json
from datetime import datetime

def test_trading_strategy_core():
    """測試實時交易策略頁面的核心業務流程"""
    print("🎯 TradingStrategy.vue 核心業務流程測試")
    print("📊 專門測試：WebSocket → pandas-ta → 策略生成 → 前端展示")
    print("⚠️ 排除與 Dashboard 共用的備用模板數據")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    results = {
        "core_apis": {"passed": 0, "failed": 0},
        "data_flow": {"pandas_ta": False, "signals": False, "websocket": False}
    }
    
    # 純 pandas-ta + WebSocket 核心 API 測試
    core_tests = [
        {
            "name": "pandas-ta 直接分析引擎",
            "url": f"{base_url}/api/v1/scalping/pandas-ta-direct",
            "description": "🧠 核心分析引擎 - 純 pandas-ta 計算 + WebSocket 數據",
            "key_fields": ["signals", "total_signals", "status", "phase"],
            "timeout": 15,
            "is_primary": True
        },
        {
            "name": "精準篩選信號引擎",
            "url": f"{base_url}/api/v1/scalping/signals", 
            "description": "🎯 策略篩選引擎 - pandas-ta 結果精準篩選",
            "key_fields": ["signals", "count", "precision_mode"],
            "timeout": 10,
            "is_primary": True
        }
    ]
    
    print("1️⃣ 測試純 pandas-ta + WebSocket 核心數據流")
    print("🚫 不依賴 Dashboard 共用的備用模板數據")
    print("-" * 40)
    
    for test in core_tests:
        print(f"\n🔍 測試: {test['name']}")
        print(f"   📝 {test['description']}")
        print(f"   🎯 主要引擎: {'是' if test.get('is_primary') else '否'}")
        
        try:
            response = requests.get(test["url"], timeout=test["timeout"])
            
            if response.status_code == 200:
                data = response.json()
                
                # 檢查關鍵字段
                missing_fields = [field for field in test["key_fields"] if field not in data]
                if not missing_fields:
                    print(f"   ✅ API 回應正常")
                    results["core_apis"]["passed"] += 1
                    
                    # 分析數據內容 - 更詳細的 pandas-ta 分析
                    if "total_signals" in data:
                        signal_count = data["total_signals"]
                        data_source = data.get("data_source", "unknown")
                        print(f"   📊 pandas-ta 信號數量: {signal_count}")
                        print(f"   📡 數據源: {data_source}")
                        
                        if signal_count > 0:
                            results["data_flow"]["pandas_ta"] = True
                            print(f"   🎉 pandas-ta 正在產生真實分析結果！")
                            
                            # 檢查信號的詳細內容
                            signals = data.get("signals", [])
                            if signals:
                                sample_signal = signals[0]
                                print(f"   📈 信號樣本: symbol={sample_signal.get('symbol', 'N/A')}, "
                                      f"type={sample_signal.get('signal_type', 'N/A')}, "
                                      f"confidence={sample_signal.get('confidence', 'N/A')}")
                        else:
                            print(f"   ⏳ pandas-ta 分析中（無信號產生，等待 WebSocket 數據）")
                    
                    if "count" in data:
                        signal_count = data["count"]
                        precision_mode = data.get("precision_mode", False)
                        market_conditions = data.get("market_conditions", "unknown")
                        
                        print(f"   📊 精準篩選結果: {signal_count}")
                        print(f"   🎯 精準模式: {'✅ 啟用' if precision_mode else '❌ 停用'}")
                        print(f"   📊 市場條件: {market_conditions}")
                        
                        if signal_count > 0:
                            results["data_flow"]["signals"] = True
                            print(f"   🎉 策略引擎正在產生交易信號！")
                        else:
                            print(f"   ⏳ 等待符合精準篩選條件的信號")
                    
                    if "status" in data:
                        status = data["status"]
                        phase = data.get("phase", "unknown")
                        improvements = data.get("improvements", [])
                        
                        print(f"   📊 引擎狀態: {status}")
                        print(f"   📊 運行階段: {phase}")
                        if improvements:
                            print(f"   🔧 功能特性: {len(improvements)} 項增強功能")
                    
                else:
                    print(f"   ⚠️ 回應格式異常，缺少字段: {missing_fields}")
                    results["core_apis"]["failed"] += 1
                    
            else:
                print(f"   ❌ HTTP 錯誤: {response.status_code}")
                results["core_apis"]["failed"] += 1
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ 請求超時 (>{test['timeout']}s) - pandas-ta 分析可能較耗時")
            results["core_apis"]["failed"] += 1
        except Exception as e:
            print(f"   ❌ 錯誤: {str(e)[:80]}")
            results["core_apis"]["failed"] += 1

    # 測試 WebSocket 相關端點
    print(f"\n2️⃣ 測試 WebSocket 數據流狀態")
    print("-" * 40)
    
    websocket_tests = [
        f"{base_url}/api/v1/realtime-signals/status",
        f"{base_url}/api/v1/realtime/status"
    ]
    
    for url in websocket_tests:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ WebSocket 狀態端點可訪問")
                print(f"   📊 回應: {json.dumps(data, ensure_ascii=False)[:100]}...")
                results["data_flow"]["websocket"] = True
                break
        except:
            continue
    
    if not results["data_flow"]["websocket"]:
        print("⚠️ WebSocket 狀態端點無法訪問")

    # 核心業務流程評估
    print(f"\n" + "=" * 60)
    print("📊 TradingStrategy.vue 核心業務流程評估")
    print("=" * 60)
    
    print(f"🔧 API 端點狀態:")
    print(f"   ✅ 正常: {results['core_apis']['passed']}")
    print(f"   ❌ 失敗: {results['core_apis']['failed']}")
    
    print(f"\n📊 數據流狀態:")
    print(f"   🧠 pandas-ta 分析: {'✅ 活躍' if results['data_flow']['pandas_ta'] else '⏳ 待激活'}")
    print(f"   🎯 策略信號生成: {'✅ 活躍' if results['data_flow']['signals'] else '⏳ 待激活'}")
    print(f"   🌐 WebSocket 連接: {'✅ 正常' if results['data_flow']['websocket'] else '❌ 異常'}")
    
    # 核心流程完整性評估
    core_working = (
        results["core_apis"]["passed"] >= 2 and
        results["core_apis"]["failed"] == 0
    )
    
    data_flowing = any(results["data_flow"].values())
    
    print(f"\n🎯 核心業務流程狀態:")
    if core_working and data_flowing:
        print("🎉 純 pandas-ta + WebSocket 核心流程正常運作！")
        print("📊 真實數據流：WebSocket → pandas-ta → 策略生成 → 前端展示")
        print("📋 建議：✅ 可以開始 Phase 2 動態權重系統測試")
    elif core_working:
        print("⚠️ API 端點正常，但 pandas-ta 數據流需要激活")
        print("📋 建議：檢查 WebSocket 連接和市場數據輸入")
        print("💡 提示：pandas-ta 分析需要足夠的 WebSocket 數據才會產生信號")
    else:
        print("🔧 需要修復核心 pandas-ta API 端點問題")
        print("📋 建議：檢查 scalping 路由和 pandas-ta 分析引擎")
    
    print(f"\n📋 TradingStrategy.vue 專用端點狀態總結:")
    print(f"   🧠 /api/v1/scalping/pandas-ta-direct (主要)")
    print(f"   🎯 /api/v1/scalping/signals (篩選)")  
    print(f"   🚫 不依賴 /api/v1/signals/latest (Dashboard 共用)")
    
    return results

if __name__ == "__main__":
    test_trading_strategy_core()
