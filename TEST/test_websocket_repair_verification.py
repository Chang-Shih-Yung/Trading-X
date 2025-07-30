"""
測試 WebSocket 修復效果 - 觸發連接斷開場景
"""

import asyncio
import websockets
import json
import time
from datetime import datetime

async def test_websocket_disconnect_scenario():
    """測試 WebSocket 斷開場景以驗證修復效果"""
    
    print(f"🚀 測試 WebSocket 斷開場景 - {datetime.now()}")
    
    # 測試1：正常連接後立即斷開（模擬網絡問題）
    print("\n📡 測試1：快速連接斷開")
    connections = []
    
    try:
        # 建立多個連接
        for i in range(3):
            try:
                uri = "ws://localhost:8000/api/v1/ws"
                websocket = await websockets.connect(uri)
                print(f"✅ 連接 {i+1} 建立成功")
                
                # 發送訂閱消息
                subscribe_msg = {
                    "action": "subscribe",
                    "symbols": ["BTCUSDT", "ETHUSDT"]
                }
                await websocket.send(json.dumps(subscribe_msg))
                
                connections.append(websocket)
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"❌ 連接 {i+1} 失敗: {e}")
        
        print(f"✅ 建立了 {len(connections)} 個連接")
        
        # 等待一會讓服務器開始廣播
        await asyncio.sleep(3)
        
        # 突然關閉所有連接（模擬客戶端斷開）
        print("\n🔌 強制斷開所有連接...")
        for i, conn in enumerate(connections):
            try:
                await conn.close()
                print(f"✅ 連接 {i+1} 已關閉")
            except Exception as e:
                print(f"⚠️ 關閉連接 {i+1} 時出錯: {e}")
        
        # 等待服務器嘗試向已斷開的連接發送數據
        print("\n⏰ 等待服務器處理斷開的連接...")
        await asyncio.sleep(10)
        
        print("✅ 測試完成")
        
    except Exception as e:
        print(f"❌ 測試過程出錯: {e}")

async def check_server_logs():
    """檢查服務器日誌"""
    import aiohttp
    import subprocess
    
    print("\n📋 檢查最新的服務器日誌...")
    
    try:
        # 檢查新的 server.log
        result = subprocess.run(
            ["tail", "-20", "server.log"], 
            capture_output=True, 
            text=True,
            cwd="/Users/henrychang/Desktop/Trading-X"
        )
        
        if result.returncode == 0:
            print("最新日誌內容:")
            print("-" * 50)
            print(result.stdout)
            print("-" * 50)
        else:
            print("❌ 無法讀取日誌文件")
            
    except Exception as e:
        print(f"❌ 檢查日誌時出錯: {e}")

async def monitor_error_pattern():
    """監控錯誤模式"""
    import subprocess
    
    print("\n🔍 監控 WebSocket 錯誤...")
    
    try:
        # 檢查是否還有舊的錯誤模式
        result = subprocess.run(
            ["grep", "-c", "Unexpected ASGI message", "server.log"], 
            capture_output=True, 
            text=True,
            cwd="/Users/henrychang/Desktop/Trading-X"
        )
        
        if result.returncode == 0:
            count = int(result.stdout.strip())
            if count > 0:
                print(f"⚠️ 發現 {count} 個 ASGI 錯誤")
            else:
                print("✅ 沒有發現 ASGI 錯誤")
        else:
            print("✅ 沒有發現 ASGI 錯誤（grep 沒找到匹配）")
            
    except Exception as e:
        print(f"❌ 監控錯誤時出錯: {e}")

async def main():
    """主測試函數"""
    print("=" * 60)
    print("🔧 WebSocket 修復效果驗證測試")
    print("=" * 60)
    
    # 等待服務完全啟動
    await asyncio.sleep(5)
    
    await test_websocket_disconnect_scenario()
    await asyncio.sleep(3)
    await check_server_logs()
    await monitor_error_pattern()
    
    print("\n" + "=" * 60)
    print("📋 測試完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
