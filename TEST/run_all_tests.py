#!/usr/bin/env python3
"""
Trading X 測試套件主運行腳本
一次性運行所有後端測試
"""

import subprocess
import sys
import os
import time
from datetime import datetime

def run_test(test_script, description):
    """運行單個測試腳本"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"▶️  正在運行: {test_script}")
    print(f"⏰ 開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 運行測試腳本
        result = subprocess.run([
            sys.executable, test_script
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ {description} - 測試通過")
            if result.stdout:
                print("📊 輸出:")
                print(result.stdout)
        else:
            print(f"❌ {description} - 測試失敗")
            if result.stderr:
                print("🚨 錯誤信息:")
                print(result.stderr)
            if result.stdout:
                print("📊 輸出:")
                print(result.stdout)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - 測試超時 (5分鐘)")
        return False
    except Exception as e:
        print(f"💥 {description} - 運行異常: {e}")
        return False

def check_backend_status():
    """檢查後端服務狀態"""
    print("🔍 檢查後端服務狀態...")
    try:
        import requests
        response = requests.get('http://localhost:8000/api/v1/scalping/signals', timeout=5)
        if response.status_code == 200:
            print("✅ 後端服務運行正常")
            return True
        else:
            print(f"⚠️ 後端服務響應異常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 無法連接後端服務: {e}")
        print("💡 請確保後端服務已啟動:")
        print("   uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        return False

def main():
    """主測試流程"""
    print("🚀 Trading X 測試套件")
    print("=" * 60)
    print(f"📅 測試開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 檢查當前工作目錄
    current_dir = os.getcwd()
    if not current_dir.endswith('Trading-X'):
        print("⚠️ 請從 Trading-X 項目根目錄運行此腳本")
        print(f"📁 當前目錄: {current_dir}")
        return
    
    # 檢查後端服務
    if not check_backend_status():
        user_continue = input("🤔 是否繼續運行測試? (y/N): ").strip().lower()
        if user_continue not in ['y', 'yes']:
            print("🛑 測試終止")
            return
    
    # 定義測試列表
    tests = [
        ("TEST/config/test_config.py", "配置文件測試"),
        ("TEST/backend/test_real_price.py", "實時價格數據測試"),
        ("TEST/backend/verify_signals.py", "信號驗證測試"),
        ("TEST/backend/test_timeframe_integration.py", "時間框架整合測試"),
        ("TEST/backend/test_precision_signal.py", "精準信號時間顯示測試"),
    ]
    
    # 運行測試
    passed = 0
    failed = 0
    
    for test_script, description in tests:
        if os.path.exists(test_script):
            if run_test(test_script, description):
                passed += 1
            else:
                failed += 1
            
            # 測試間隔
            time.sleep(2)
        else:
            print(f"⚠️ 測試文件不存在: {test_script}")
            failed += 1
    
    # 總結報告
    print(f"\n{'='*60}")
    print("📊 測試總結報告")
    print(f"{'='*60}")
    print(f"✅ 通過測試: {passed}")
    print(f"❌ 失敗測試: {failed}")
    print(f"📈 成功率: {(passed/(passed+failed)*100):.1f}%" if (passed+failed) > 0 else "N/A")
    print(f"⏰ 測試結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if failed == 0:
        print("🎉 所有測試通過！系統運行正常")
    else:
        print("🚨 部分測試失敗，請檢查相關功能")

if __name__ == "__main__":
    main()
