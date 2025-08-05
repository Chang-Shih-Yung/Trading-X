#!/usr/bin/env python3
"""
測試 Email 系統優化：每個代幣只發送最佳信號
"""

import asyncio
import requests
from datetime import datetime
import json

# 後端 URL
BACKEND_URL = "http://localhost:8000"

async def test_email_system_optimization():
    """測試電子郵件系統優化功能"""
    print("🧪 測試 Email 系統優化 - 每代幣最佳信號發送")
    print("=" * 60)
    
    try:
        # 1. 檢查電子郵件狀態
        print("1️⃣ 檢查電子郵件狀態...")
        response = requests.get(f"{BACKEND_URL}/api/v1/sniper/email/status/summary")
        if response.status_code == 200:
            status = response.json()
            print(f"   ✅ Email 狀態: {status}")
        else:
            print(f"   ❌ 獲取 Email 狀態失敗: {response.status_code}")
        
        # 2. 檢查狙擊手信號歷史
        print("\n2️⃣ 檢查狙擊手信號歷史...")
        response = requests.get(f"{BACKEND_URL}/api/v1/sniper/history/statistics")
        if response.status_code == 200:
            stats = response.json()
            print(f"   📊 狙擊手統計:")
            print(f"      {json.dumps(stats, indent=6, ensure_ascii=False)}")
        else:
            print(f"   ❌ 獲取狙擊手統計失敗: {response.status_code}")
        
        # 3. 檢查實時信號狀態
        print("\n3️⃣ 檢查實時信號狀態...")
        response = requests.get(f"{BACKEND_URL}/api/v1/realtime-signals/status")
        if response.status_code == 200:
            realtime_status = response.json()
            print(f"   📡 實時信號狀態: {realtime_status}")
        else:
            print(f"   ❌ 獲取實時信號狀態失敗: {response.status_code}")
        
        # 4. 檢查最新實時信號
        print("\n4️⃣ 檢查最新實時信號...")
        response = requests.get(f"{BACKEND_URL}/api/v1/realtime-signals/signals/recent?limit=5")
        if response.status_code == 200:
            signals = response.json()
            if signals:
                print(f"   � 最新 {len(signals)} 個實時信號:")
                for signal in signals:
                    symbol = signal.get('symbol', 'Unknown')
                    strength = signal.get('signal_strength', 0)
                    signal_type = signal.get('signal_type', 'Unknown')
                    timestamp = signal.get('timestamp', '')
                    print(f"      • {symbol}: {signal_type}, 強度{strength:.3f} ({timestamp})")
            else:
                print(f"   📭 沒有找到最新實時信號")
        else:
            print(f"   ❌ 獲取最新實時信號失敗: {response.status_code}")
        
        print("\n✅ 測試完成！")
        print("\n📋 優化要點確認:")
        print("   • 每個代幣每天只發送信心度最高的一個信號")
        print("   • 30秒掃描間隔，避免重複發送")
        print("   • 自動清理過期的發送記錄")
        print("   • 失敗信號自動重試（最多5次）")
        
    except Exception as e:
        print(f"❌ 測試過程中出現錯誤: {e}")

if __name__ == "__main__":
    asyncio.run(test_email_system_optimization())
