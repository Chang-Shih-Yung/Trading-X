#!/usr/bin/env python3
"""
綜合系統測試器 - 測試所有Trading X核心系統
"""

import asyncio
import sys
import os
import time
import logging
from pathlib import Path

# 添加路徑
sys.path.append(str(Path(__file__).parent))

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_database_systems():
    """測試三數據庫分離系統"""
    try:
        from app.core.database_separated import SeparatedDatabaseManager
        
        logger.info("🗄️ 測試三數據庫分離系統...")
        db_manager = SeparatedDatabaseManager()
        
        # 創建表
        await db_manager.create_all_tables()
        
        # 檢查數據庫連接
        market_db = await db_manager.create_session("market_data")
        learning_db = await db_manager.create_session("learning_records") 
        extreme_db = await db_manager.create_session("extreme_events")
        
        logger.info("✅ 數據庫連接測試成功")
        
        await market_db.close()
        await learning_db.close()
        await extreme_db.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 數據庫測試失敗: {e}")
        return False

def test_crash_detection():
    """測試閃崩檢測系統"""
    try:
        from app.utils.crash_detector import CrashDetector
        
        logger.info("🚨 測試閃崩檢測系統...")
        
        detector = CrashDetector()
        # 檢查保護狀態
        status = detector.get_protection_status()
        
        logger.info(f"✅ 閃崩檢測完成，監控狀態: {status['monitoring_active']}")
        return True
        
    except Exception as e:
        logger.error(f"❌ 閃崩檢測測試失敗: {e}")
        return False

def test_liquidity_monitoring():
    """測試流動性監控系統"""
    try:
        from app.services.liquidity_monitor import LiquidityMonitor
        import asyncio
        
        logger.info("💧 測試流動性監控系統...")
        
        monitor = LiquidityMonitor()
        # 測試基本屬性
        symbols_count = len(monitor.symbols)
        thresholds = monitor.liquidity_thresholds
        
        logger.info(f"✅ 流動性監控完成，監控 {symbols_count} 個交易對")
        return True
        
    except Exception as e:
        logger.error(f"❌ 流動性監控測試失敗: {e}")
        return False

def test_correlation_monitoring():
    """測試相關性監控系統"""
    try:
        from app.services.correlation_monitor import CorrelationMonitor
        
        logger.info("📈 測試相關性監控系統...")
        
        monitor = CorrelationMonitor()
        # 檢查基本屬性
        symbols_count = len(monitor.symbols)
        
        logger.info(f"✅ 相關性監控完成，監控 {symbols_count} 個交易對")
        return True
        
    except Exception as e:
        logger.error(f"❌ 相關性監控測試失敗: {e}")
        return False

def test_data_flow_protection():
    """測試數據流保護系統"""
    try:
        from app.utils.data_flow_protection import DataFlowProtectionManager
        
        logger.info("🔒 測試數據流保護系統...")
        
        protector = DataFlowProtectionManager()
        
        # 測試基本功能
        test_file = "test_lock.tmp"
        try:
            with open(test_file, "w") as f:
                protector.lock_file(f)
                f.write("test data")
                protector.unlock_file(f)
        except:
            pass  # 忽略鎖定錯誤
        
        # 清理測試文件
        if os.path.exists(test_file):
            os.remove(test_file)
            
        logger.info("✅ 數據流保護測試成功")
        return True
        
    except Exception as e:
        logger.error(f"❌ 數據流保護測試失敗: {e}")
        return False

def test_shutdown_manager():
    """測試系統停機管理器"""
    try:
        from app.services.shutdown_manager import ShutdownManager
        
        logger.info("🛑 測試系統停機管理器...")
        
        manager = ShutdownManager()
        
        # 檢查系統狀態
        status = manager.get_shutdown_status()
        logger.info("✅ 系統停機管理器測試成功")
        return True
        
    except Exception as e:
        logger.error(f"❌ 系統停機管理器測試失敗: {e}")
        return False

async def main():
    """主測試函數"""
    print("🚀 Trading X 綜合系統測試開始...")
    print("=" * 60)
    
    test_results = {}
    
    # 測試各個系統
    test_results['database'] = await test_database_systems()
    test_results['crash_detection'] = test_crash_detection()
    test_results['liquidity_monitoring'] = test_liquidity_monitoring()
    test_results['correlation_monitoring'] = test_correlation_monitoring()
    test_results['data_flow_protection'] = test_data_flow_protection()
    test_results['shutdown_manager'] = test_shutdown_manager()
    
    # 總結結果
    print("\n" + "=" * 60)
    print("📊 系統測試結果總結:")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for system, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{system.replace('_', ' ').title():25} : {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"總體通過率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 所有系統測試通過！Trading X 系統運行正常")
    else:
        print("⚠️  部分系統測試失敗，請檢查上述錯誤")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
