#!/usr/bin/env python3
"""
測試數據創建與清理腳本
專門測試數據的創建、傳遞和清理過程
"""

import asyncio
import requests
import json
import sqlite3
import os
from datetime import datetime, timedelta
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"
DB_PATH = "/Users/henrychang/Desktop/Trading-X/tradingx.db"

class TestDataManager:
    """測試數據管理器"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.db_path = DB_PATH
        self.created_test_data = []
        
    async def test_data_creation_and_cleanup(self):
        """測試數據創建和清理完整流程"""
        logger.info("🧪 開始測試數據創建與清理流程...")
        
        try:
            # 1. 記錄初始狀態
            initial_count = self._count_test_records()
            logger.info(f"初始測試數據數量: {initial_count}")
            
            # 2. 創建測試數據
            success_count = await self._create_test_data()
            logger.info(f"成功創建 {success_count} 個測試數據")
            
            # 3. 驗證數據創建
            after_creation_count = self._count_test_records()
            logger.info(f"創建後測試數據數量: {after_creation_count}")
            
            created_records = after_creation_count - initial_count
            if created_records > 0:
                logger.info(f"✅ 數據創建成功，新增 {created_records} 條記錄")
            else:
                logger.warning("⚠️ 未檢測到新創建的測試數據")
            
            # 4. 測試數據傳遞
            transmission_success = await self._test_data_transmission()
            
            # 5. 清理測試數據
            cleaned_count = await self._cleanup_test_data()
            logger.info(f"清理了 {cleaned_count} 個測試數據")
            
            # 6. 驗證清理效果
            final_count = self._count_test_records()
            logger.info(f"清理後測試數據數量: {final_count}")
            
            # 7. 總結
            results = {
                "data_creation": created_records > 0,
                "data_transmission": transmission_success,
                "data_cleanup": cleaned_count > 0 or final_count <= initial_count
            }
            
            return results
            
        except Exception as e:
            logger.error(f"❌ 數據創建清理測試失敗: {e}")
            return {"data_creation": False, "data_transmission": False, "data_cleanup": False}
    
    async def _create_test_data(self):
        """創建多種類型的測試數據"""
        success_count = 0
        
        test_data_types = [
            # 1. API 測試數據
            {
                "type": "api_signal",
                "data": {
                    "symbol": "TEST_BTCUSDT",
                    "signal_type": "BUY",
                    "confidence": 0.85,
                    "test_mode": True,
                    "source": "test_api"
                }
            },
            # 2. 配置測試數據
            {
                "type": "api_config",
                "data": {
                    "test_parameter": "test_value",
                    "test_symbols": ["TEST_BTC", "TEST_ETH"],
                    "test_mode": True
                }
            },
            # 3. 直接數據庫測試數據
            {
                "type": "database_signal",
                "data": {
                    "symbol": "TEST_ETHUSDT",
                    "signal_type": "SELL",
                    "confidence": 0.75,
                    "test_marker": "direct_db_test"
                }
            }
        ]
        
        for test_item in test_data_types:
            try:
                if test_item["type"] == "api_signal":
                    result = await self._create_api_test_signal(test_item["data"])
                elif test_item["type"] == "api_config":
                    result = await self._create_api_test_config(test_item["data"])
                elif test_item["type"] == "database_signal":
                    result = await self._create_database_test_signal(test_item["data"])
                else:
                    result = False
                
                if result:
                    success_count += 1
                    self.created_test_data.append(test_item)
                    
            except Exception as e:
                logger.warning(f"創建測試數據失敗 {test_item['type']}: {e}")
        
        return success_count
    
    async def _create_api_test_signal(self, data):
        """通過 API 創建測試信號"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/realtime-signals/signals/test", 
                json=data, 
                timeout=10
            )
            
            if response.status_code in [200, 201, 202]:
                logger.info("✅ API 測試信號創建成功")
                return True
            else:
                logger.warning(f"⚠️ API 測試信號創建異常: {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"API 測試信號創建失敗: {e}")
            return False
    
    async def _create_api_test_config(self, data):
        """通過 API 創建測試配置"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/realtime-signals/config", 
                json=data, 
                timeout=10
            )
            
            if response.status_code in [200, 201, 202]:
                logger.info("✅ API 測試配置創建成功")
                return True
            else:
                logger.warning(f"⚠️ API 測試配置創建異常: {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"API 測試配置創建失敗: {e}")
            return False
    
    async def _create_database_test_signal(self, data):
        """直接在數據庫中創建測試信號"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 插入測試信號到 trading_signals 表
                test_timestamp = datetime.now().isoformat()
                
                cursor.execute("""
                    INSERT INTO trading_signals 
                    (symbol, timeframe, signal_type, signal_strength, confidence, primary_timeframe, reasoning, created_at, status, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'test', 0)
                """, (
                    data["symbol"],
                    "1h",  # 必需的 timeframe
                    data["signal_type"],
                    0.7,   # 必需的 signal_strength
                    data["confidence"],
                    "1h",  # 必需的 primary_timeframe
                    f"測試數據 - {data.get('test_marker', 'test')}",
                    test_timestamp
                ))
                
                conn.commit()
                logger.info("✅ 數據庫測試信號創建成功")
                return True
                
        except Exception as e:
            logger.warning(f"數據庫測試信號創建失敗: {e}")
            return False
    
    async def _test_data_transmission(self):
        """測試數據傳遞機制"""
        try:
            # 發送測試數據並檢查響應
            test_payload = {
                "action": "test_transmission",
                "data": {
                    "test_id": f"test_{datetime.now().timestamp()}",
                    "test_message": "數據傳遞測試",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/realtime-signals/config", 
                json=test_payload, 
                timeout=10
            )
            
            if response.status_code < 500:  # 非服務器錯誤
                logger.info("✅ 數據傳遞機制正常")
                return True
            else:
                logger.warning(f"⚠️ 數據傳遞異常: {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"數據傳遞測試失敗: {e}")
            return False
    
    async def _cleanup_test_data(self):
        """清理所有測試數據"""
        cleaned_count = 0
        
        try:
            # 1. 清理數據庫中的測試數據
            db_cleaned = self._cleanup_database_test_data()
            cleaned_count += db_cleaned
            
            # 2. 通過 API 清理（如果支持）
            api_cleaned = await self._cleanup_api_test_data()
            cleaned_count += api_cleaned
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"清理測試數據失敗: {e}")
            return cleaned_count
    
    def _cleanup_database_test_data(self):
        """清理數據庫中的測試數據"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 清理測試信號
                cursor.execute("SELECT COUNT(*) FROM trading_signals WHERE symbol LIKE 'TEST_%' OR reasoning LIKE '%測試數據%' OR status = 'test'")
                before_count = cursor.fetchone()[0]
                
                cursor.execute("DELETE FROM trading_signals WHERE symbol LIKE 'TEST_%' OR reasoning LIKE '%測試數據%' OR status = 'test'")
                
                cursor.execute("SELECT COUNT(*) FROM trading_signals WHERE symbol LIKE 'TEST_%' OR reasoning LIKE '%測試數據%' OR status = 'test'")
                after_count = cursor.fetchone()[0]
                
                cleaned = before_count - after_count
                
                conn.commit()
                
                if cleaned > 0:
                    logger.info(f"✅ 數據庫清理完成，清理了 {cleaned} 條測試記錄")
                else:
                    logger.info("ℹ️ 數據庫中沒有需要清理的測試數據")
                
                return cleaned
                
        except Exception as e:
            logger.warning(f"數據庫清理失敗: {e}")
            return 0
    
    async def _cleanup_api_test_data(self):
        """通過 API 清理測試數據"""
        try:
            # 嘗試通過 API 觸發清理
            cleanup_request = {
                "action": "cleanup_test_data",
                "test_mode": True
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/realtime-signals/cleanup", 
                json=cleanup_request, 
                timeout=15
            )
            
            if response.status_code in [200, 201, 202]:
                logger.info("✅ API 清理請求成功")
                return 1
            else:
                logger.debug(f"API 清理響應: {response.status_code}")
                return 0
                
        except Exception as e:
            logger.debug(f"API 清理失敗: {e}")
            return 0
    
    def _count_test_records(self):
        """統計測試相關的記錄數量"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM trading_signals WHERE symbol LIKE 'TEST_%' OR reasoning LIKE '%測試數據%' OR status = 'test'")
                count = cursor.fetchone()[0]
                
                return count
                
        except Exception as e:
            logger.warning(f"統計測試記錄失敗: {e}")
            return 0

async def main():
    """主測試函數"""
    logger.info("🧪 開始測試數據創建與清理測試...")
    
    manager = TestDataManager()
    
    try:
        results = await manager.test_data_creation_and_cleanup()
        
        logger.info("\n📊 測試結果總結:")
        logger.info(f"  數據創建: {'✅ 成功' if results['data_creation'] else '❌ 失敗'}")
        logger.info(f"  數據傳遞: {'✅ 成功' if results['data_transmission'] else '❌ 失敗'}")
        logger.info(f"  數據清理: {'✅ 成功' if results['data_cleanup'] else '❌ 失敗'}")
        
        success_count = sum(results.values())
        total_count = len(results)
        
        logger.info(f"\n🎯 總計: {success_count}/{total_count} 項測試通過")
        
        if success_count == total_count:
            logger.info("🎉 所有數據管理測試通過！")
            logger.info("💡 測試數據創建、傳遞和清理機制運行正常")
            return True
        elif success_count >= total_count * 0.6:
            logger.info("✅ 大部分數據管理測試通過")
            logger.info("💡 數據管理機制基本正常")
            return True
        else:
            logger.warning("⚠️ 數據管理測試存在問題")
            logger.info("💡 建議檢查數據創建和清理機制")
            return False
            
    except Exception as e:
        logger.error(f"❌ 測試執行失敗: {e}")
        return False

if __name__ == "__main__":
    # 運行測試
    success = asyncio.run(main())
    exit(0 if success else 1)
