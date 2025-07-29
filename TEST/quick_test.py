#!/usr/bin/env python3
"""
Trading X 快速測試腳本
運行核心功能的基本測試
"""

import requests
import time
from datetime import datetime

def test_backend_connection():
    """測試後端連接"""
    print("🔍 測試後端連接...")
    try:
        response = requests.get('http://localhost:8000/api/v1/scalping/signals', timeout=5)
        if response.status_code == 200:
            print("✅ 後端服務連接正常")
            return True
        else:
            print(f"❌ 後端響應異常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 無法連接後端: {e}")
        return False

def test_price_api():
    """測試價格API"""
    print("📊 測試價格數據API...")
    try:
        response = requests.get(
            'http://localhost:8000/api/v1/scalping/prices?symbols=BTCUSDT,ETHUSDT', 
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if 'prices' in data and len(data['prices']) > 0:
                print("✅ 價格數據API正常")
                print(f"📈 獲取到 {len(data['prices'])} 個幣種的價格數據")
                return True
            else:
                print("⚠️ 價格數據為空")
                return False
        else:
            print(f"❌ 價格API響應異常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 價格API測試失敗: {e}")
        return False

def test_signals_api():
    """測試信號API"""
    print("🎯 測試信號數據API...")
    try:
        response = requests.get('http://localhost:8000/api/v1/scalping/signals', timeout=15)
        if response.status_code == 200:
            data = response.json()
            if 'signals' in data:
                signal_count = len(data['signals'])
                print(f"✅ 信號API正常 - 獲取到 {signal_count} 個信號")
                
                # 檢查信號質量
                precision_signals = [s for s in data['signals'] if s.get('is_precision_verified')]
                print(f"🎯 精準信號數量: {len(precision_signals)}")
                
                return True
            else:
                print("⚠️ 信號數據格式異常")
                return False
        else:
            print(f"❌ 信號API響應異常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 信號API測試失敗: {e}")
        return False

def test_expired_signals():
    """測試過期信號API"""
    print("📜 測試過期信號API...")
    try:
        response = requests.get('http://localhost:8000/api/v1/scalping/expired', timeout=10)
        if response.status_code == 200:
            expired_signals = response.json()
            print(f"✅ 過期信號API正常 - 獲取到 {len(expired_signals)} 個過期信號")
            return True
        else:
            print(f"❌ 過期信號API響應異常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 過期信號API測試失敗: {e}")
        return False

def main():
    """快速測試主流程"""
    print("⚡ Trading X 快速功能測試")
    print("=" * 50)
    print(f"🕐 開始時間: {datetime.now().strftime('%H:%M:%S')}")
    
    tests = [
        ("後端連接", test_backend_connection),
        ("價格數據API", test_price_api),
        ("信號數據API", test_signals_api),
        ("過期信號API", test_expired_signals),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        time.sleep(1)  # 避免API請求過快
    
    print(f"\n{'='*50}")
    print("📊 快速測試結果")
    print(f"{'='*50}")
    print(f"✅ 通過: {passed}/{total}")
    print(f"📈 成功率: {(passed/total*100):.1f}%")
    print(f"🕐 結束時間: {datetime.now().strftime('%H:%M:%S')}")
    
    if passed == total:
        print("🎉 系統核心功能正常！")
    else:
        print("⚠️ 部分功能異常，建議運行完整測試")

if __name__ == "__main__":
    main()
