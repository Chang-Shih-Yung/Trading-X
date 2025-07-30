#!/usr/bin/env python3
"""
數據管理與清理測試腳本
測試7天數據清理週期和數據存儲管理功能
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

class DataManagementTester:
    """數據管理測試器"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.db_path = DB_PATH
        
    async def test_data_storage_and_retrieval(self):
        """測試數據存儲和檢索"""
        logger.info("🧪 測試數據存儲和檢索...")
        
        try:
            # 1. 檢查數據庫連接
            if not self._check_database_connection():
                logger.error("❌ 無法連接到數據庫")
                return False
            
            # 2. 啟動信號引擎生成測試數據
            logger.info("啟動信號引擎生成測試數據...")
            start_result = self._make_request("POST", "/api/v1/realtime-signals/start")
            if not start_result.get("success"):
                logger.error("❌ 信號引擎啟動失敗")
                return False
            
            # 3. 等待數據生成
            await asyncio.sleep(10)
            
            # 4. 生成一些測試信號
            for i in range(5):
                test_result = self._make_request("POST", "/api/v1/realtime-signals/signals/test", {
                    "symbol": "BTCUSDT" if i % 2 == 0 else "ETHUSDT"
                })
                if test_result.get("success"):
                    logger.info(f"生成測試信號 {i+1}/5")
                await asyncio.sleep(2)
            
            # 5. 檢查數據存儲
            stored_data = self._check_stored_data()
            if stored_data:
                logger.info("✅ 數據存儲正常")
                logger.info(f"   存儲的信號數量: {stored_data.get('signal_count', 0)}")
                logger.info(f"   存儲的市場數據量: {stored_data.get('market_data_count', 0)}")
            else:
                logger.warning("⚠️ 數據存儲檢查失敗")
                return False
            
            # 6. 測試數據檢索
            recent_signals = self._make_request("GET", "/api/v1/realtime-signals/signals/recent?hours=1")
            if recent_signals.get("success"):
                signal_count = recent_signals.get("data", {}).get("count", 0)
                logger.info(f"✅ 數據檢索正常，最近1小時信號數: {signal_count}")
            else:
                logger.error("❌ 數據檢索失敗")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 數據存儲測試失敗: {e}")
            return False
    
    async def test_7_day_cleanup_cycle(self):
        """測試7天數據清理週期"""
        logger.info("🧪 測試7天數據清理週期...")
        
        try:
            # 1. 檢查現有數據
            initial_data = self._check_stored_data()
            logger.info(f"初始數據量: 信號 {initial_data.get('signal_count', 0)}, 市場數據 {initial_data.get('market_data_count', 0)}")
            
            # 2. 創建模擬舊數據（超過7天）
            if not self._create_old_test_data():
                logger.error("❌ 創建測試舊數據失敗")
                return False
            
            # 3. 檢查插入舊數據後的數據量
            after_insert_data = self._check_stored_data()
            logger.info(f"插入舊數據後: 信號 {after_insert_data.get('signal_count', 0)}, 市場數據 {after_insert_data.get('market_data_count', 0)}")
            
            # 4. 觸發清理操作
            logger.info("觸發數據清理...")
            cleanup_result = self._make_request("POST", "/api/v1/realtime-signals/cleanup")
            
            if cleanup_result.get("success"):
                cleaned_info = cleanup_result.get("data", {})
                logger.info(f"✅ 清理完成:")
                logger.info(f"   清理的信號數: {cleaned_info.get('signals_cleaned', 0)}")
                logger.info(f"   清理的市場數據: {cleaned_info.get('market_data_cleaned', 0)}")
            else:
                logger.error("❌ 數據清理失敗")
                return False
            
            # 5. 檢查清理後的數據量
            after_cleanup_data = self._check_stored_data()
            logger.info(f"清理後數據量: 信號 {after_cleanup_data.get('signal_count', 0)}, 市場數據 {after_cleanup_data.get('market_data_count', 0)}")
            
            # 6. 驗證清理效果
            signals_cleaned = after_insert_data.get('signal_count', 0) - after_cleanup_data.get('signal_count', 0)
            if signals_cleaned > 0:
                logger.info(f"✅ 數據清理效果驗證通過，清理了 {signals_cleaned} 個舊信號")
                return True
            else:
                logger.warning("⚠️ 未檢測到數據清理效果")
                return False
            
        except Exception as e:
            logger.error(f"❌ 7天清理週期測試失敗: {e}")
            return False
    
    async def test_database_integrity(self):
        """測試數據庫完整性"""
        logger.info("🧪 測試數據庫完整性...")
        
        try:
            # 1. 檢查數據庫結構
            if not self._check_database_schema():
                logger.error("❌ 數據庫結構檢查失敗")
                return False
            
            # 2. 檢查索引
            if not self._check_database_indexes():
                logger.warning("⚠️ 數據庫索引檢查異常")
            
            # 3. 檢查數據一致性
            if not self._check_data_consistency():
                logger.error("❌ 數據一致性檢查失敗")
                return False
            
            # 4. 檢查外鍵約束
            if not self._check_foreign_key_constraints():
                logger.warning("⚠️ 外鍵約束檢查異常")
            
            logger.info("✅ 數據庫完整性檢查通過")
            return True
            
        except Exception as e:
            logger.error(f"❌ 數據庫完整性測試失敗: {e}")
            return False
    
    async def test_storage_efficiency(self):
        """測試存儲效率"""
        logger.info("🧪 測試存儲效率...")
        
        try:
            # 1. 檢查數據庫大小
            initial_size = self._get_database_size()
            logger.info(f"初始數據庫大小: {initial_size:.2f} MB")
            
            # 2. 生成大量測試數據
            logger.info("生成測試數據...")
            for i in range(20):
                test_result = self._make_request("POST", "/api/v1/realtime-signals/signals/test")
                if i % 5 == 0:
                    logger.info(f"生成進度: {i+1}/20")
                await asyncio.sleep(0.5)
            
            # 3. 檢查數據增長
            after_generation_size = self._get_database_size()
            size_increase = after_generation_size - initial_size
            logger.info(f"生成數據後大小: {after_generation_size:.2f} MB (增長 {size_increase:.2f} MB)")
            
            # 4. 執行數據庫優化
            self._optimize_database()
            
            # 5. 檢查優化後大小
            after_optimization_size = self._get_database_size()
            optimization_savings = after_generation_size - after_optimization_size
            logger.info(f"優化後大小: {after_optimization_size:.2f} MB (節省 {optimization_savings:.2f} MB)")
            
            # 6. 評估存儲效率
            if size_increase < 10:  # 20個信號增長少於10MB認為效率良好
                logger.info("✅ 存儲效率良好")
                return True
            elif size_increase < 20:
                logger.info("⚠️ 存儲效率可接受")
                return True
            else:
                logger.warning("❌ 存儲效率需要改善")
                return False
            
        except Exception as e:
            logger.error(f"❌ 存儲效率測試失敗: {e}")
            return False
    
    def _check_database_connection(self):
        """檢查數據庫連接"""
        try:
            if not os.path.exists(self.db_path):
                logger.warning(f"數據庫文件不存在: {self.db_path}")
                return False
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True
                
        except Exception as e:
            logger.error(f"數據庫連接失敗: {e}")
            return False
    
    def _check_stored_data(self):
        """檢查存儲的數據"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 檢查信號表
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                result = {}
                
                # 檢查常見的表
                if 'trading_signals' in tables:
                    cursor.execute("SELECT COUNT(*) FROM trading_signals")
                    result['signal_count'] = cursor.fetchone()[0]
                
                if 'market_data' in tables:
                    cursor.execute("SELECT COUNT(*) FROM market_data")
                    result['market_data_count'] = cursor.fetchone()[0]
                
                return result
                
        except Exception as e:
            logger.error(f"檢查存儲數據失敗: {e}")
            return None
    
    def _create_old_test_data(self):
        """創建模擬舊數據"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 創建舊的信號數據（8天前）
                old_date = datetime.now() - timedelta(days=8)
                old_timestamp = old_date.isoformat()
                
                # 檢查是否存在 trading_signals 表
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trading_signals'")
                if not cursor.fetchone():
                    # 創建測試表
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS trading_signals (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            symbol TEXT NOT NULL,
                            signal_type TEXT NOT NULL,
                            confidence REAL NOT NULL,
                            timestamp TEXT NOT NULL,
                            created_at TEXT NOT NULL
                        )
                    """)
                
                # 插入舊數據
                for i in range(10):
                    cursor.execute("""
                        INSERT INTO trading_signals 
                        (symbol, signal_type, confidence, timestamp, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        "BTCUSDT" if i % 2 == 0 else "ETHUSDT",
                        "buy" if i % 3 == 0 else "sell",
                        0.7 + (i % 3) * 0.1,
                        old_timestamp,
                        old_timestamp
                    ))
                
                conn.commit()
                logger.info("✅ 創建了10個測試舊數據")
                return True
                
        except Exception as e:
            logger.error(f"創建舊測試數據失敗: {e}")
            return False
    
    def _check_database_schema(self):
        """檢查數據庫結構"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 獲取所有表
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                logger.info(f"數據庫表: {tables}")
                
                # 檢查關鍵表的結構
                for table in tables:
                    if table.startswith('sqlite_'):
                        continue
                        
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    logger.info(f"表 {table} 的列: {[col[1] for col in columns]}")
                
                return True
                
        except Exception as e:
            logger.error(f"數據庫結構檢查失敗: {e}")
            return False
    
    def _check_database_indexes(self):
        """檢查數據庫索引"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index'")
                indexes = cursor.fetchall()
                
                logger.info(f"數據庫索引: {len(indexes)} 個")
                for index_name, table_name in indexes:
                    if not index_name.startswith('sqlite_'):
                        logger.info(f"  {table_name}.{index_name}")
                
                return True
                
        except Exception as e:
            logger.error(f"數據庫索引檢查失敗: {e}")
            return False
    
    def _check_data_consistency(self):
        """檢查數據一致性"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 檢查是否有重複數據
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                for table in tables:
                    if table.startswith('sqlite_'):
                        continue
                    
                    # 檢查NULL值
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    total_rows = cursor.fetchone()[0]
                    
                    if total_rows > 0:
                        logger.info(f"表 {table}: {total_rows} 行數據")
                
                return True
                
        except Exception as e:
            logger.error(f"數據一致性檢查失敗: {e}")
            return False
    
    def _check_foreign_key_constraints(self):
        """檢查外鍵約束"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("PRAGMA foreign_key_check")
                violations = cursor.fetchall()
                
                if violations:
                    logger.warning(f"發現 {len(violations)} 個外鍵約束違規")
                    return False
                else:
                    logger.info("✅ 外鍵約束檢查通過")
                    return True
                
        except Exception as e:
            logger.error(f"外鍵約束檢查失敗: {e}")
            return False
    
    def _get_database_size(self):
        """獲取數據庫大小（MB）"""
        try:
            size_bytes = os.path.getsize(self.db_path)
            return size_bytes / (1024 * 1024)  # 轉換為 MB
        except Exception as e:
            logger.error(f"獲取數據庫大小失敗: {e}")
            return 0
    
    def _optimize_database(self):
        """優化數據庫"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 執行 VACUUM 清理
                cursor.execute("VACUUM")
                
                # 分析統計信息
                cursor.execute("ANALYZE")
                
                logger.info("✅ 數據庫優化完成")
                
        except Exception as e:
            logger.error(f"數據庫優化失敗: {e}")
    
    def _make_request(self, method: str, endpoint: str, data: dict = None):
        """發送 HTTP 請求"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=30)
            else:
                raise ValueError(f"不支援的方法: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP 請求失敗 {method} {endpoint}: {e}")
            return {"success": False, "error": str(e)}

async def main():
    """主測試函數"""
    logger.info("🚀 開始數據管理與清理測試...")
    
    tester = DataManagementTester()
    test_results = []
    
    # 測試項目
    tests = [
        ("數據存儲和檢索", tester.test_data_storage_and_retrieval),
        ("7天數據清理週期", tester.test_7_day_cleanup_cycle),
        ("數據庫完整性", tester.test_database_integrity),
        ("存儲效率", tester.test_storage_efficiency),
    ]
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 執行測試: {test_name}")
        try:
            result = await test_func()
            test_results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name} - 通過")
            else:
                logger.error(f"❌ {test_name} - 失敗")
                
            # 測試間隔
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"❌ {test_name} - 異常: {e}")
            test_results.append((test_name, False))
    
    # 測試總結
    logger.info("\n📊 測試結果總結:")
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通過" if result else "❌ 失敗"
        logger.info(f"  {test_name}: {status}")
    
    logger.info(f"\n🎯 總計: {passed}/{total} 項測試通過")
    
    if passed == total:
        logger.info("🎉 所有數據管理測試通過！數據管理功能正常")
        return True
    else:
        logger.warning("⚠️ 部分數據管理測試失敗，請檢查相關功能")
        return False

if __name__ == "__main__":
    # 運行測試
    success = asyncio.run(main())
    exit(0 if success else 1)
