"""
測試日誌管理系統
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_log_management():
    """測試日誌管理功能"""
    
    base_url = "http://localhost:8000/api/v1/admin"
    
    print("🧪 測試日誌管理系統")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # 1. 檢查日誌管理狀態
        print("\n📊 1. 檢查日誌管理狀態")
        try:
            async with session.get(f"{base_url}/logs/status") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("✅ 日誌管理狀態:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                else:
                    print(f"❌ 狀態檢查失敗: {resp.status}")
        except Exception as e:
            print(f"❌ 狀態檢查錯誤: {e}")
        
        # 2. 獲取日誌統計
        print("\n📊 2. 獲取日誌統計")
        try:
            async with session.get(f"{base_url}/logs/stats") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("✅ 日誌統計:")
                    
                    # 格式化顯示統計信息
                    stats = data.get("data", {})
                    
                    print(f"📁 總佔用空間: {stats.get('total_size_mb', 0)} MB")
                    print(f"📄 備份文件數量: {stats.get('backup_count', 0)}")
                    
                    # 主日誌文件
                    main_logs = stats.get("main_logs", {})
                    if main_logs:
                        print("\n主日誌文件:")
                        for log_name, info in main_logs.items():
                            status = "⚠️ 需要輪轉" if info.get("needs_rotation") else "✅ 正常"
                            print(f"  {log_name}: {info['size_mb']} MB - {status}")
                    
                    # 建議
                    recommendations = stats.get("recommendations", [])
                    if recommendations:
                        print("\n💡 清理建議:")
                        for rec in recommendations:
                            print(f"  • {rec}")
                    else:
                        print("\n✅ 沒有清理建議")
                        
                else:
                    print(f"❌ 統計獲取失敗: {resp.status}")
        except Exception as e:
            print(f"❌ 統計獲取錯誤: {e}")
        
        # 3. 手動觸發清理
        print("\n🧹 3. 手動觸發清理")
        try:
            async with session.post(f"{base_url}/logs/cleanup") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("✅ 清理完成:")
                    
                    cleanup_result = data.get("data", {})
                    before_size = cleanup_result.get("before", {}).get("total_size_mb", 0)
                    after_size = cleanup_result.get("after", {}).get("total_size_mb", 0)
                    freed_space = cleanup_result.get("space_freed_mb", 0)
                    
                    print(f"  清理前: {before_size} MB")
                    print(f"  清理後: {after_size} MB")
                    print(f"  釋放空間: {freed_space} MB")
                else:
                    print(f"❌ 清理失敗: {resp.status}")
                    error = await resp.text()
                    print(f"錯誤詳情: {error}")
        except Exception as e:
            print(f"❌ 清理錯誤: {e}")
        
        # 4. 再次檢查統計（驗證清理效果）
        print("\n📊 4. 清理後統計")
        try:
            async with session.get(f"{base_url}/logs/stats") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    stats = data.get("data", {})
                    print(f"✅ 清理後總大小: {stats.get('total_size_mb', 0)} MB")
                    print(f"✅ 清理後備份數量: {stats.get('backup_count', 0)}")
                else:
                    print(f"❌ 清理後統計失敗: {resp.status}")
        except Exception as e:
            print(f"❌ 清理後統計錯誤: {e}")

async def create_test_log_files():
    """創建測試日誌文件來驗證清理功能"""
    
    print("\n🧪 創建測試日誌文件")
    
    import os
    from pathlib import Path
    
    log_dir = Path("/Users/henrychang/Desktop/Trading-X")
    
    # 創建一些測試日誌文件
    test_files = [
        "test_server.log.backup_20240101_120000",
        "test_app.log.backup_20240102_120000", 
        "test_large.log"
    ]
    
    for filename in test_files:
        file_path = log_dir / filename
        try:
            # 創建小的測試文件
            with open(file_path, 'w') as f:
                f.write(f"Test log file created at {datetime.now()}\n" * 100)
            print(f"✅ 創建測試文件: {filename}")
        except Exception as e:
            print(f"❌ 創建文件失敗 {filename}: {e}")

async def main():
    """主測試函數"""
    
    print("🧪 日誌管理系統測試")
    print("=" * 60)
    
    # 檢查服務是否運行
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health") as resp:
                if resp.status == 200:
                    print("✅ 服務正在運行")
                else:
                    print(f"❌ 服務狀態異常: {resp.status}")
                    return
    except Exception as e:
        print(f"❌ 無法連接服務: {e}")
        return
    
    # 可選：創建測試文件
    # await create_test_log_files()
    
    # 測試日誌管理功能
    await test_log_management()
    
    print("\n" + "=" * 60)
    print("🎉 測試完成")

if __name__ == "__main__":
    asyncio.run(main())
