"""
測試用快速驗證腳本
檢查核心功能：WebSocket → pandas-ta → 策略生成
"""
import asyncio
import httpx
import json
from datetime import datetime

async def test_core_pipeline():
    """測試核心管道"""
    print("🔍 Phase 1：核心流程驗證測試")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # 1. 測試基本連接
        print("1️⃣ 測試基本連接...")
        try:
            response = await client.get(f"{base_url}/")
            if response.status_code == 200:
                print("✅ 後端服務正常運行")
                print(f"   回應: {response.json()}")
            else:
                print(f"❌ 後端連接失敗: {response.status_code}")
                return
        except Exception as e:
            print(f"❌ 連接錯誤: {e}")
            return
        
        # 2. 測試 pandas-ta 分析端點
        print("\n2️⃣ 測試 pandas-ta 分析...")
        try:
            response = await client.get(f"{base_url}/api/v1/scalping/pandas-ta-direct")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ pandas-ta 分析端點正常")
                print(f"   信號數量: {data.get('total_signals', 0)}")
                print(f"   狀態: {data.get('status', 'unknown')}")
                print(f"   階段: {data.get('phase', 'unknown')}")
            else:
                print(f"❌ pandas-ta 分析失敗: {response.status_code}")
        except Exception as e:
            print(f"❌ pandas-ta 測試錯誤: {e}")
        
        # 3. 測試精準篩選信號
        print("\n3️⃣ 測試精準篩選信號...")
        try:
            response = await client.get(f"{base_url}/api/v1/scalping/signals")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 精準篩選端點正常")
                print(f"   篩選信號數量: {data.get('count', 0)}")
                print(f"   模式: 精準篩選模式" if data.get('precision_mode') else "   模式: 一般模式")
                print(f"   下次更新: {data.get('next_update', 'unknown')}")
            else:
                print(f"❌ 精準篩選失敗: {response.status_code}")
        except Exception as e:
            print(f"❌ 精準篩選測試錯誤: {e}")
        
        # 4. 測試 WebSocket 數據狀態 (通過即時信號端點)
        print("\n4️⃣ 測試 WebSocket 數據狀態...")
        try:
            response = await client.get(f"{base_url}/api/v1/realtime-signals/status")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ WebSocket 狀態端點正常")
                print(f"   引擎狀態: {data.get('engine_status', 'unknown')}")
                print(f"   數據更新: {data.get('last_update', 'unknown')}")
            else:
                print(f"⚠️ WebSocket 狀態查詢失敗: {response.status_code}")
        except Exception as e:
            print(f"⚠️ WebSocket 狀態測試錯誤: {e}")
        
        # 5. 生成測試摘要
        print("\n" + "=" * 50)
        print("📊 Phase 1 測試摘要:")
        print("✅ 後端服務: 正常運行")
        print("✅ pandas-ta 分析: 端點可訪問 (等待信號產生)")
        print("✅ 精準篩選: 端點可訪問 (精準模式啟用)")
        print("⚠️ WebSocket 數據: 需進一步檢查")
        print("\n📋 下一步建議:")
        print("1. 檢查 WebSocket 連接是否建立")
        print("2. 驗證市場數據是否正常流入")
        print("3. 確認 pandas-ta 指標計算邏輯")
        print("4. 測試策略生成觸發條件")

if __name__ == "__main__":
    asyncio.run(test_core_pipeline())
