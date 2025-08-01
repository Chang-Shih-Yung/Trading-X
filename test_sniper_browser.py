#!/usr/bin/env python3
"""
🎯 狙擊手監控台瀏覽器測試腳本
快速驗證 strategies.vue 中的 Phase 1ABC 整合功能
"""

import webbrowser
import time
import subprocess
import os

def open_sniper_dashboard():
    """打開狙擊手監控台"""
    print("🎯 狙擊手監控台瀏覽器測試")
    print("=" * 50)
    
    # 檢查服務狀態
    print("📡 檢查服務狀態...")
    
    # 檢查前端服務 (port 3001)
    try:
        import requests
        frontend_response = requests.get("http://localhost:3001", timeout=3)
        if frontend_response.status_code == 200:
            print("✅ 前端服務 (3001): 正常運行")
        else:
            print("❌ 前端服務 (3001): 響應異常")
    except:
        print("❌ 前端服務 (3001): 無法連接")
    
    # 檢查後端服務 (port 8000)
    try:
        backend_response = requests.get("http://localhost:8000/health", timeout=3)
        if backend_response.status_code == 200:
            print("✅ 後端服務 (8000): 正常運行")
        else:
            print("❌ 後端服務 (8000): 響應異常")
    except:
        print("❌ 後端服務 (8000): 無法連接")
    
    print("\n🚀 正在打開狙擊手監控台...")
    
    # 打開 strategies 頁面
    strategies_url = "http://localhost:3001/strategies"
    
    try:
        webbrowser.open(strategies_url)
        print(f"✅ 已在瀏覽器中打開: {strategies_url}")
        
        print("\n📋 瀏覽器測試清單:")
        print("□ 1. 檢查 Phase 1ABC 狙擊手監控台卡片是否顯示")
        print("□ 2. 點擊展開 Phase 1ABC 卡片")
        print("□ 3. 確認三個核心功能顯示:")
        print("    - 1A: 信號重構引擎")
        print("    - 1B: 波動適應引擎") 
        print("    - 1C: 極端信號狙擊")
        print("□ 4. 檢查實時數據自動刷新")
        print("□ 5. 驗證整合分數顯示")
        
        print(f"\n🎯 狙擊手監控台已啟動!")
        print(f"📊 前端頁面: {strategies_url}")
        print(f"⚡ 後端API: http://localhost:8000/api/v1/scalping/phase1abc-integration-status")
        
        # 可選：自動刷新測試
        print(f"\n🔄 自動刷新測試...")
        for i in range(3):
            time.sleep(2)
            try:
                test_response = requests.get("http://localhost:8000/api/v1/scalping/phase1abc-integration-status", timeout=5)
                if test_response.status_code == 200:
                    data = test_response.json()
                    integration_status = data.get('integration_status', 'Unknown')
                    print(f"   測試 {i+1}/3: ✅ API響應正常 - {integration_status}")
                else:
                    print(f"   測試 {i+1}/3: ❌ API響應異常")
            except:
                print(f"   測試 {i+1}/3: ❌ API連接失敗")
        
    except Exception as e:
        print(f"❌ 無法打開瀏覽器: {e}")
        print(f"請手動打開: {strategies_url}")

if __name__ == "__main__":
    open_sniper_dashboard()
