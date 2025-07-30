#!/usr/bin/env python3
"""
即時信號引擎測試腳本
測試自動化交易信號生成和 WebSocket 廣播功能
"""

import asyncio
import requests
import json
import websockets
import logging
from datetime import datetime
import time

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/api/v1/realtime/ws"

class RealtimeSignalTester:
    """即時信號引擎測試器"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.ws_url = WS_URL
        self.websocket = None
        self.received_signals = []
        
    async def test_engine_lifecycle(self):
        """測試引擎生命週期（啟動、狀態檢查、停止）"""
        logger.info("🧪 測試引擎生命週期...")
        
        try:
            # 1. 檢查初始狀態
            logger.info("1. 檢查初始狀態...")
            status = self._make_request("GET", "/api/v1/realtime-signals/status")
            logger.info(f"初始狀態: {status.get('data', {}).get('running', False)}")
            
            # 2. 啟動引擎
            logger.info("2. 啟動信號引擎...")
            start_result = self._make_request("POST", "/api/v1/realtime-signals/start")
            if start_result.get("success"):
                logger.info("✅ 引擎啟動成功")
            else:
                logger.error(f"❌ 引擎啟動失敗: {start_result}")
                return False
            
            # 3. 等待一段時間讓引擎初始化
            logger.info("3. 等待引擎初始化...")
            await asyncio.sleep(10)
            
            # 4. 檢查運行狀態
            logger.info("4. 檢查運行狀態...")
            status = self._make_request("GET", "/api/v1/realtime-signals/status")
            if status.get("data", {}).get("running"):
                logger.info("✅ 引擎運行正常")
                logger.info(f"監控交易對: {status.get('data', {}).get('monitored_symbols', [])}")
                logger.info(f"24小時信號數: {status.get('data', {}).get('signals_24h', 0)}")
            else:
                logger.error("❌ 引擎未正常運行")
                return False
            
            # 5. 健康檢查
            logger.info("5. 健康檢查...")
            health = self._make_request("GET", "/api/v1/realtime-signals/health")
            if health.get("data", {}).get("status") == "healthy":
                logger.info("✅ 健康檢查通過")
            else:
                logger.warning("⚠️ 健康檢查異常")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 生命週期測試失敗: {e}")
            return False
    
    async def test_websocket_signals(self):
        """測試 WebSocket 信號接收"""
        logger.info("🧪 測試 WebSocket 信號接收...")
        
        try:
            # 連接 WebSocket
            logger.info("連接 WebSocket...")
            self.websocket = await websockets.connect(self.ws_url)
            
            # 發送訂閱消息
            subscribe_msg = {
                "action": "subscribe",
                "symbols": ["BTCUSDT", "ETHUSDT", "BNBUSDT"],
                "data_types": ["prices", "signals"]
            }
            await self.websocket.send(json.dumps(subscribe_msg))
            logger.info("✅ WebSocket 連接成功，已發送訂閱消息")
            
            # 生成測試信號
            logger.info("生成測試信號...")
            test_result = self._make_request("POST", "/api/v1/realtime-signals/signals/test")
            if test_result.get("success"):
                logger.info("✅ 測試信號生成成功")
            else:
                logger.error("❌ 測試信號生成失敗")
                return False
            
            # 等待接收信號
            logger.info("等待接收信號...")
            signal_received = False
            
            try:
                # 等待最多30秒接收信號
                for _ in range(30):
                    try:
                        message = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                        data = json.loads(message)
                        
                        logger.info(f"收到消息: {data.get('type', 'unknown')}")
                        
                        if data.get("type") == "trading_signal":
                            signal_data = data.get("data", {})
                            logger.info(f"🎯 收到交易信號:")
                            logger.info(f"   交易對: {signal_data.get('symbol')}")
                            logger.info(f"   信號類型: {signal_data.get('signal_type')}")
                            logger.info(f"   信心度: {signal_data.get('confidence')}")
                            logger.info(f"   進場價: {signal_data.get('entry_price')}")
                            logger.info(f"   理由: {signal_data.get('reasoning')}")
                            
                            self.received_signals.append(signal_data)
                            signal_received = True
                            break
                            
                    except asyncio.TimeoutError:
                        continue
                        
            except Exception as e:
                logger.error(f"接收信號時發生錯誤: {e}")
            
            if signal_received:
                logger.info("✅ WebSocket 信號接收測試成功")
                return True
            else:
                logger.warning("⚠️ 未收到預期的交易信號")
                return False
                
        except Exception as e:
            logger.error(f"❌ WebSocket 測試失敗: {e}")
            return False
        finally:
            if self.websocket:
                await self.websocket.close()
    
    async def test_configuration(self):
        """測試配置更新"""
        logger.info("🧪 測試配置更新...")
        
        try:
            # 獲取當前配置
            status = self._make_request("GET", "/api/v1/realtime-signals/status")
            original_config = status.get("data", {})
            
            # 更新配置
            new_config = {
                "confidence_threshold": 0.75,
                "signal_cooldown": 600,
                "monitored_symbols": ["BTCUSDT", "ETHUSDT"]
            }
            
            logger.info(f"更新配置: {new_config}")
            update_result = self._make_request("POST", "/api/v1/realtime-signals/config", new_config)
            
            if update_result.get("success"):
                logger.info("✅ 配置更新成功")
                updated_fields = update_result.get("updated_fields", [])
                logger.info(f"更新的欄位: {updated_fields}")
                
                # 驗證配置是否生效
                status = self._make_request("GET", "/api/v1/realtime-signals/status")
                current_config = status.get("data", {})
                
                # 簡單驗證
                if len(current_config.get("monitored_symbols", [])) == 2:
                    logger.info("✅ 配置驗證成功")
                    return True
                else:
                    logger.error("❌ 配置驗證失敗")
                    return False
            else:
                logger.error(f"❌ 配置更新失敗: {update_result}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 配置測試失敗: {e}")
            return False
    
    async def test_signal_history(self):
        """測試信號歷史查詢"""
        logger.info("🧪 測試信號歷史查詢...")
        
        try:
            # 查詢最近24小時的信號
            signals = self._make_request("GET", "/api/v1/realtime-signals/signals/recent?hours=24")
            
            if signals.get("success"):
                signal_count = signals.get("data", {}).get("count", 0)
                logger.info(f"✅ 查詢到 {signal_count} 個最近信號")
                
                if signal_count > 0:
                    recent_signal = signals.get("data", {}).get("signals", [])[0]
                    logger.info(f"最新信號: {recent_signal.get('symbol')} {recent_signal.get('signal_type')}")
                
                return True
            else:
                logger.error(f"❌ 信號歷史查詢失敗: {signals}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 信號歷史測試失敗: {e}")
            return False
    
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
    
    async def cleanup(self):
        """清理測試環境"""
        logger.info("🧹 清理測試環境...")
        
        try:
            # 停止引擎
            stop_result = self._make_request("POST", "/api/v1/realtime-signals/stop")
            if stop_result.get("success"):
                logger.info("✅ 引擎已停止")
            else:
                logger.warning("⚠️ 停止引擎時出現問題")
                
        except Exception as e:
            logger.error(f"清理時發生錯誤: {e}")

async def main():
    """主測試函數"""
    logger.info("🚀 開始即時信號引擎測試...")
    
    tester = RealtimeSignalTester()
    test_results = []
    
    try:
        # 測試項目
        tests = [
            ("引擎生命週期", tester.test_engine_lifecycle),
            ("WebSocket 信號接收", tester.test_websocket_signals),
            ("配置更新", tester.test_configuration),
            ("信號歷史查詢", tester.test_signal_history),
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
        
    finally:
        # 清理
        await tester.cleanup()
    
    # 測試總結
    logger.info("\n📊 測試結果總結:")
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通過" if result else "❌ 失敗"
        logger.info(f"  {test_name}: {status}")
    
    logger.info(f"\n🎯 總計: {passed}/{total} 項測試通過")
    
    if passed == total:
        logger.info("🎉 所有測試通過！即時信號引擎工作正常")
        return True
    else:
        logger.warning("⚠️ 部分測試失敗，請檢查系統狀態")
        return False

if __name__ == "__main__":
    # 運行測試
    success = asyncio.run(main())
    exit(0 if success else 1)
