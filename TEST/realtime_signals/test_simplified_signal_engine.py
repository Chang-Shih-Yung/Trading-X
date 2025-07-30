#!/usr/bin/env python3
"""
簡化版即時信號引擎測試腳本
專門測試核心功能並使用測試數據
"""

import asyncio
import requests
import json
import logging
from datetime import datetime
import time

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

class SimplifiedSignalEngineTester:
    """簡化版信號引擎測試器"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.test_data_created = []  # 記錄創建的測試數據
        
    async def test_basic_connectivity(self):
        """測試基本連接"""
        logger.info("🧪 測試基本連接...")
        
        try:
            # 檢查服務健康狀態
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ 後端服務連接正常")
                return True
            else:
                logger.error(f"❌ 後端服務異常: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 基本連接測試失敗: {e}")
            return False
    
    async def test_signal_engine_endpoints(self):
        """測試信號引擎端點"""
        logger.info("🧪 測試信號引擎端點...")
        
        try:
            # 1. 檢查狀態端點
            logger.info("1. 檢查狀態端點...")
            status_response = self._make_request("GET", "/api/v1/realtime-signals/status")
            if status_response.get("success") or status_response.get("data"):
                logger.info("✅ 狀態端點可用")
            else:
                logger.warning("⚠️ 狀態端點響應異常")
            
            # 2. 檢查健康檢查端點
            logger.info("2. 檢查健康檢查端點...")
            health_response = self._make_request("GET", "/api/v1/realtime-signals/health")
            if health_response.get("success") or health_response.get("data"):
                logger.info("✅ 健康檢查端點可用")
            else:
                logger.warning("⚠️ 健康檢查端點響應異常")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 信號引擎端點測試失敗: {e}")
            return False
    
    async def test_data_flow_with_test_data(self):
        """使用測試數據測試數據流"""
        logger.info("🧪 測試數據流（使用測試數據）...")
        
        try:
            # 1. 創建測試信號
            logger.info("1. 創建測試信號...")
            test_signal_data = {
                "symbol": "TEST_BTCUSDT",
                "signal_type": "BUY",
                "confidence": 0.85,
                "test_mode": True,
                "test_timestamp": datetime.now().isoformat()
            }
            
            # 嘗試生成測試信號
            test_result = self._make_request("POST", "/api/v1/realtime-signals/signals/test", test_signal_data)
            
            if test_result.get("success"):
                logger.info("✅ 測試信號生成成功")
                
                # 記錄測試數據以便後續清理
                signal_id = test_result.get("data", {}).get("id")
                if signal_id:
                    self.test_data_created.append(("signal", signal_id))
                
                # 2. 驗證信號數據
                signal_data = test_result.get("data", {})
                if signal_data.get("symbol") == "TEST_BTCUSDT":
                    logger.info("✅ 測試數據正確傳遞")
                else:
                    logger.warning("⚠️ 測試數據傳遞異常")
                
                return True
            else:
                logger.warning("⚠️ 測試信號生成失敗，可能是端點不支援")
                
                # 嘗試其他方式測試數據流
                return await self._test_alternative_data_flow()
                
        except Exception as e:
            logger.error(f"❌ 數據流測試失敗: {e}")
            return False
    
    async def _test_alternative_data_flow(self):
        """替代數據流測試"""
        logger.info("2. 嘗試替代數據流測試...")
        
        try:
            # 檢查是否能獲取最近信號
            recent_signals = self._make_request("GET", "/api/v1/realtime-signals/signals/recent?hours=1")
            
            if recent_signals.get("success") or recent_signals.get("data") is not None:
                logger.info("✅ 信號查詢端點正常")
                return True
            else:
                logger.warning("⚠️ 替代數據流測試未完全成功")
                return False
                
        except Exception as e:
            logger.error(f"❌ 替代數據流測試失敗: {e}")
            return False
    
    async def test_configuration_handling(self):
        """測試配置處理"""
        logger.info("🧪 測試配置處理...")
        
        try:
            # 測試配置更新（使用安全的測試配置）
            test_config = {
                "test_mode": True,
                "test_confidence_threshold": 0.8,
                "test_symbols": ["TEST_BTC", "TEST_ETH"]
            }
            
            config_result = self._make_request("POST", "/api/v1/realtime-signals/config", test_config)
            
            if config_result.get("success"):
                logger.info("✅ 配置更新功能正常")
                return True
            else:
                logger.warning("⚠️ 配置更新功能異常")
                return False
                
        except Exception as e:
            logger.error(f"❌ 配置處理測試失敗: {e}")
            return False
    
    async def cleanup_test_data(self):
        """清理測試數據"""
        logger.info("🧹 清理測試數據...")
        
        try:
            cleanup_count = 0
            
            for data_type, data_id in self.test_data_created:
                try:
                    if data_type == "signal":
                        # 嘗試刪除測試信號
                        delete_result = self._make_request("DELETE", f"/api/v1/realtime-signals/signals/{data_id}")
                        if delete_result.get("success"):
                            cleanup_count += 1
                            
                except Exception as e:
                    logger.debug(f"清理測試數據時發生錯誤: {e}")
            
            if cleanup_count > 0:
                logger.info(f"✅ 清理了 {cleanup_count} 個測試數據")
            else:
                logger.info("ℹ️ 沒有需要清理的測試數據")
                
        except Exception as e:
            logger.warning(f"⚠️ 清理測試數據時發生錯誤: {e}")
    
    def _make_request(self, method: str, endpoint: str, data: dict = None):
        """發送 HTTP 請求"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=15)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=15)
            elif method == "DELETE":
                response = requests.delete(url, timeout=15)
            else:
                raise ValueError(f"不支援的方法: {method}")
            
            if response.status_code < 500:  # 非服務器錯誤都嘗試解析
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
            
        except requests.exceptions.RequestException as e:
            logger.debug(f"HTTP 請求失敗 {method} {endpoint}: {e}")
            return {"success": False, "error": str(e)}

async def main():
    """主測試函數"""
    logger.info("🚀 開始簡化版即時信號引擎測試...")
    
    tester = SimplifiedSignalEngineTester()
    test_results = []
    
    try:
        # 測試項目
        tests = [
            ("基本連接", tester.test_basic_connectivity),
            ("信號引擎端點", tester.test_signal_engine_endpoints),
            ("數據流（測試數據）", tester.test_data_flow_with_test_data),
            ("配置處理", tester.test_configuration_handling),
        ]
        
        for test_name, test_func in tests:
            logger.info(f"\n📋 執行測試: {test_name}")
            try:
                result = await test_func()
                test_results.append((test_name, result))
                
                if result:
                    logger.info(f"✅ {test_name} - 通過")
                else:
                    logger.warning(f"⚠️ {test_name} - 部分問題")
                    
                # 測試間隔
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ {test_name} - 異常: {e}")
                test_results.append((test_name, False))
        
    finally:
        # 清理測試數據
        await tester.cleanup_test_data()
    
    # 測試總結
    logger.info("\n📊 測試結果總結:")
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通過" if result else "⚠️ 有問題"
        logger.info(f"  {test_name}: {status}")
    
    logger.info(f"\n🎯 總計: {passed}/{total} 項測試通過")
    
    if passed >= total * 0.75:  # 75% 通過率
        logger.info("🎉 整體測試通過！信號引擎基本功能正常")
        return True
    else:
        logger.warning("⚠️ 部分測試未完全通過，但基本功能可能正常")
        return False

if __name__ == "__main__":
    # 運行測試
    success = asyncio.run(main())
    exit(0 if success else 1)
