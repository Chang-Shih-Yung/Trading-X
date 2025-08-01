#!/usr/bin/env python3
"""
🎯 狙擊手計劃 (Sniper Protocol) 測試腳本
測試 Phase 1ABC + strategies.vue 整合狀態
"""

import asyncio
import requests
import json
from datetime import datetime

def test_sniper_protocol():
    """測試狙擊手監控台的各項功能"""
    print("\n🎯 狙擊手計劃 (Sniper Protocol) 測試開始")
    print("=" * 60)
    
    # 測試項目清單
    test_items = [
        {
            "name": "Phase 1ABC API 端點",
            "endpoint": "http://localhost:8000/api/v1/scalping/phase1abc-integration-status",
            "expected": "階段1A+1B+1C整合狀態"
        },
        {
            "name": "前端 strategies.vue 頁面",
            "endpoint": "http://localhost:3001/strategies",
            "expected": "狙擊手監控台頁面"
        },
        {
            "name": "Phase 3 數據支援",
            "endpoint": "http://localhost:8000/api/v1/scalping/phase3-market-depth",
            "expected": "高階市場分析數據"
        },
        {
            "name": "動態參數支援",
            "endpoint": "http://localhost:8000/api/v1/scalping/dynamic-parameters",
            "expected": "Phase 1+2動態參數"
        }
    ]
    
    results = {}
    
    for item in test_items:
        print(f"\n📡 測試 {item['name']}...")
        
        try:
            if item['endpoint'].startswith('http://localhost:3001'):
                # 前端頁面測試
                response = requests.get(item['endpoint'], timeout=5)
                if response.status_code == 200:
                    print(f"✅ {item['name']} - 頁面可訪問")
                    results[item['name']] = "SUCCESS"
                else:
                    print(f"❌ {item['name']} - 頁面無法訪問 ({response.status_code})")
                    results[item['name']] = "FAILED"
            else:
                # API 端點測試
                response = requests.get(item['endpoint'], timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {item['name']} - API 正常響應")
                    
                    # 檢查具體數據
                    if 'phase1abc' in item['endpoint']:
                        if 'integration_status' in data:
                            print(f"   • 整合狀態: {data.get('integration_status', 'Unknown')}")
                        if 'system_capabilities' in data:
                            print(f"   • 系統能力: {len(data.get('system_capabilities', {}))} 項")
                        results[item['name']] = "SUCCESS"
                    elif 'phase3' in item['endpoint']:
                        if 'symbol_analyses' in data:
                            print(f"   • 分析符號數: {len(data.get('symbol_analyses', []))}")
                        results[item['name']] = "SUCCESS"
                    elif 'dynamic-parameters' in item['endpoint']:
                        if 'dynamic_parameters' in data:
                            print(f"   • 動態參數數: {len(data.get('dynamic_parameters', []))}")
                        results[item['name']] = "SUCCESS"
                    else:
                        results[item['name']] = "SUCCESS"
                        
                else:
                    print(f"❌ {item['name']} - API 錯誤 ({response.status_code})")
                    if response.text:
                        try:
                            error_data = response.json()
                            print(f"   • 錯誤詳情: {error_data.get('detail', 'Unknown error')}")
                        except:
                            pass
                    results[item['name']] = "FAILED"
                    
        except requests.exceptions.ConnectionError:
            print(f"❌ {item['name']} - 服務未啟動")
            results[item['name']] = "CONNECTION_ERROR"
        except requests.exceptions.Timeout:
            print(f"❌ {item['name']} - 請求超時")
            results[item['name']] = "TIMEOUT"
        except Exception as e:
            print(f"❌ {item['name']} - 未知錯誤: {e}")
            results[item['name']] = "ERROR"
    
    # 測試結果總結
    print(f"\n🎯 狙擊手計劃測試總結")
    print("=" * 60)
    
    success_count = len([r for r in results.values() if r == "SUCCESS"])
    total_count = len(results)
    
    print(f"📊 測試結果: {success_count}/{total_count} 項目通過")
    
    for name, result in results.items():
        status_icon = "✅" if result == "SUCCESS" else "❌"
        print(f"{status_icon} {name}: {result}")
    
    # 狙擊手系統狀態評估
    if success_count == total_count:
        print(f"\n🎯 狙擊手系統狀態: 🟢 FULLY OPERATIONAL")
        print("   所有系統正常，狙擊手監控台已就緒！")
    elif success_count >= total_count * 0.75:
        print(f"\n🎯 狙擊手系統狀態: 🟡 MOSTLY OPERATIONAL")
        print("   大部分系統正常，可以進行基本監控。")
    elif success_count >= total_count * 0.5:
        print(f"\n🎯 狙擊手系統狀態: 🟠 PARTIALLY OPERATIONAL")
        print("   部分系統正常，建議檢查失敗項目。")
    else:
        print(f"\n🎯 狙擊手系統狀態: 🔴 SYSTEM ISSUES")
        print("   多個系統異常，需要排查問題。")
    
    # 下一步建議
    print(f"\n📋 下一步建議:")
    if success_count == total_count:
        print("• 🎯 開始第二階段：建立統一數據層")
        print("• 🔄 測試自動刷新功能")
        print("• 📊 驗證實時數據同步")
    else:
        failed_items = [name for name, result in results.items() if result != "SUCCESS"]
        print(f"• 🔧 修復失敗項目: {', '.join(failed_items)}")
        print("• 🔄 重新運行測試")
    
    print(f"\n⏰ 測試完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return results

if __name__ == "__main__":
    test_sniper_protocol()
