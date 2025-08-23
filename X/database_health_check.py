#!/usr/bin/env python3
"""
🔧 Trading X 資料庫健康檢查與修復工具
用於驗證和修復 enhanced_signals 表結構問題
"""

import asyncio
import sys
import os
import logging

# 添加項目路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.phase2_adaptive_learning.priority3_timeframe_learning.enhanced_signal_database import enhanced_signal_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def check_database_health():
    """檢查資料庫健康狀態"""
    try:
        logger.info("🔧 開始資料庫健康檢查...")
        
        # 初始化資料庫
        await enhanced_signal_db.initialize()
        logger.info("✅ 資料庫連接成功")
        
        # 檢查表結構
        cursor = await enhanced_signal_db.connection.execute("PRAGMA table_info(enhanced_signals)")
        columns = await cursor.fetchall()
        await cursor.close()
        
        column_names = [col[1] for col in columns]
        logger.info(f"📊 當前表結構欄位數量: {len(column_names)}")
        
        # 必需欄位列表
        required_columns = [
            'signal_id', 'symbol', 'signal_type', 'signal_strength', 'timestamp',
            'features', 'market_conditions', 'tier',
            'time_decay_weight', 'hours_since_generation',
            'coin_category', 'category_weight', 'category_risk_multiplier',
            'primary_timeframe', 'timeframe_consensus', 'cross_timeframe_weight',
            'final_learning_weight', 'status', 'actual_outcome', 'performance_score', 'execution_time'
        ]
        
        # 檢查缺失欄位
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            logger.warning(f"⚠️ 發現 {len(missing_columns)} 個缺失欄位: {missing_columns}")
            
            # 執行修復
            logger.info("🔧 開始執行修復...")
            await enhanced_signal_db._validate_and_fix_table_structure()
            logger.info("✅ 修復完成")
            
            # 重新檢查
            cursor = await enhanced_signal_db.connection.execute("PRAGMA table_info(enhanced_signals)")
            columns = await cursor.fetchall()
            await cursor.close()
            
            new_column_names = [col[1] for col in columns]
            still_missing = [col for col in required_columns if col not in new_column_names]
            
            if still_missing:
                logger.error(f"❌ 修復後仍缺失欄位: {still_missing}")
                return False
            else:
                logger.info("✅ 所有欄位修復成功")
        else:
            logger.info("✅ 表結構完整，無需修復")
        
        # 檢查版本
        cursor = await enhanced_signal_db.connection.execute("SELECT MAX(version) FROM database_version")
        current_version = (await cursor.fetchone())[0]
        await cursor.close()
        
        logger.info(f"📊 當前資料庫版本: {current_version}")
        
        # 測試寫入
        logger.info("🧪 測試信號寫入...")
        
        # 創建測試信號對象
        class TestSignal:
            def __init__(self):
                self.signal_id = "test_health_check_001"
                self.symbol = "BTCUSDT"
                self.signal_type = "TEST"
                self.signal_strength = 0.75
                self.timestamp = asyncio.get_event_loop().time()
                self.features = {"test": True}
                self.market_conditions = {"test_mode": True}
                self.tier = "HIGH"
                self.status = "PENDING"
                self.actual_outcome = None
                self.performance_score = None
                self.execution_time = None
        
        from datetime import datetime
        test_signal = TestSignal()
        test_signal.timestamp = datetime.now()
        
        # 嘗試存儲測試信號
        success = await enhanced_signal_db.store_enhanced_signal(test_signal)
        
        if success:
            logger.info("✅ 測試信號寫入成功")
            
            # 清理測試數據
            await enhanced_signal_db.connection.execute(
                "DELETE FROM enhanced_signals WHERE signal_id = ?", 
                (test_signal.signal_id,)
            )
            await enhanced_signal_db.connection.commit()
            logger.info("✅ 測試數據清理完成")
        else:
            logger.error("❌ 測試信號寫入失敗")
            return False
        
        logger.info("🎉 資料庫健康檢查完成 - 所有測試通過！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 健康檢查失敗: {e}")
        return False
    
    finally:
        if enhanced_signal_db.connection:
            await enhanced_signal_db.connection.close()

async def main():
    """主函數"""
    print("🔧 Trading X 資料庫健康檢查工具")
    print("=" * 50)
    
    success = await check_database_health()
    
    if success:
        print("\n✅ 資料庫健康檢查通過！系統可以正常運行。")
        sys.exit(0)
    else:
        print("\n❌ 資料庫健康檢查失敗！請檢查錯誤訊息。")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
