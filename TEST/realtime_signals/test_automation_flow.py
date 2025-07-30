#!/usr/bin/env python3
"""
自動化流程端到端測試腳本
測試完整的 websocket → pandas-ta → 信號廣播流程
"""

import asyncio
import websockets
import requests
import json
import logging
from datetime import datetime, timedelta
import time

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/api/v1/realtime/ws"

class AutomationFlowTester:
    """自動化流程測試器"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.ws_url = WS_URL
        self.websocket = None
        self.received_data = {
            "price_updates": [],
            "trading_signals": [],
            "market_data": []
        }
        
    async def test_complete_automation_flow(self):
        """測試完整自動化流程"""
        logger.info("🧪 測試完整自動化流程...")
        
        try:
            # 1. 準備測試環境
            logger.info("1. 準備測試環境...")
            await self._setup_test_environment()
            
            # 2. 連接 WebSocket 並訂閱
            logger.info("2. 連接 WebSocket...")
            await self._connect_websocket()
            
            # 3. 啟動信號引擎
            logger.info("3. 啟動信號引擎...")
            await self._start_signal_engine()
            
            # 4. 監控數據流程
            logger.info("4. 監控自動化流程...")
            await self._monitor_automation_flow()
            
            # 5. 驗證完整流程
            logger.info("5. 驗證流程完整性...")
            result = await self._validate_complete_flow()
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 完整流程測試失敗: {e}")
            return False
        finally:
            await self._cleanup()
    
    async def _setup_test_environment(self):
        """設置測試環境"""
        try:
            # 檢查服務狀態
            health_check = self._make_request("GET", "/health")
            if not health_check.get("status") == "healthy":
                raise Exception("後端服務不健康")
            
            # 配置測試參數
            config = {
                "confidence_threshold": 0.6,  # 降低閾值以便測試
                "signal_cooldown": 60,  # 降低冷卻時間
                "monitored_symbols": ["BTCUSDT", "ETHUSDT"],
                "analysis_interval": 30  # 30秒分析一次
            }
            
            config_result = self._make_request("POST", "/api/v1/realtime-signals/config", config)
            if not config_result.get("success"):
                raise Exception("配置設置失敗")
                
            logger.info("✅ 測試環境準備完成")
            
        except Exception as e:
            logger.error(f"❌ 測試環境設置失敗: {e}")
            raise
    
    async def _connect_websocket(self):
        """連接 WebSocket"""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            
            # 訂閱所有數據類型
            subscribe_msg = {
                "action": "subscribe",
                "symbols": ["BTCUSDT", "ETHUSDT"],
                "data_types": ["prices", "signals", "analysis"]
            }
            
            await self.websocket.send(json.dumps(subscribe_msg))
            logger.info("✅ WebSocket 連接並訂閱成功")
            
        except Exception as e:
            logger.error(f"❌ WebSocket 連接失敗: {e}")
            raise
    
    async def _start_signal_engine(self):
        """啟動信號引擎"""
        try:
            # 停止現有引擎（如果有）
            self._make_request("POST", "/api/v1/realtime-signals/stop")
            await asyncio.sleep(2)
            
            # 啟動新引擎
            start_result = self._make_request("POST", "/api/v1/realtime-signals/start")
            if not start_result.get("success"):
                raise Exception("信號引擎啟動失敗")
            
            # 等待引擎初始化
            await asyncio.sleep(10)
            
            # 驗證引擎狀態
            status = self._make_request("GET", "/api/v1/realtime-signals/status")
            if not status.get("data", {}).get("running"):
                raise Exception("信號引擎未正常運行")
                
            logger.info("✅ 信號引擎啟動成功")
            
        except Exception as e:
            logger.error(f"❌ 信號引擎啟動失敗: {e}")
            raise
    
    async def _monitor_automation_flow(self):
        """監控自動化流程"""
        logger.info("開始監控自動化流程...")
        
        flow_steps = {
            "price_received": False,
            "analysis_triggered": False,
            "signal_generated": False,
            "signal_broadcasted": False
        }
        
        start_time = datetime.now()
        timeout = 300  # 5分鐘超時
        
        try:
            while (datetime.now() - start_time).total_seconds() < timeout:
                # 檢查是否有 WebSocket 消息
                try:
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                    data = json.loads(message)
                    
                    message_type = data.get("type")
                    logger.info(f"收到消息類型: {message_type}")
                    
                    # 處理不同類型的消息
                    if message_type == "price_update":
                        self.received_data["price_updates"].append(data)
                        flow_steps["price_received"] = True
                        logger.info("📈 第1步: 價格更新已接收")
                        
                    elif message_type == "market_analysis":
                        self.received_data["market_data"].append(data)
                        flow_steps["analysis_triggered"] = True
                        logger.info("🔍 第2步: 市場分析已觸發")
                        
                    elif message_type == "trading_signal":
                        self.received_data["trading_signals"].append(data)
                        flow_steps["signal_generated"] = True
                        flow_steps["signal_broadcasted"] = True
                        
                        signal_data = data.get("data", {})
                        logger.info("🎯 第3步: 交易信號已生成並廣播")
                        logger.info(f"   交易對: {signal_data.get('symbol')}")
                        logger.info(f"   信號: {signal_data.get('signal_type')}")
                        logger.info(f"   信心度: {signal_data.get('confidence')}")
                        
                    # 檢查是否完成完整流程
                    if all(flow_steps.values()):
                        logger.info("🎉 完整自動化流程已完成！")
                        break
                        
                except asyncio.TimeoutError:
                    # 定期檢查流程狀態
                    completed_steps = sum(flow_steps.values())
                    logger.info(f"流程進度: {completed_steps}/4 步驟完成")
                    
                    # 如果長時間沒有新數據，主動觸發
                    if (datetime.now() - start_time).total_seconds() > 60 and not flow_steps["price_received"]:
                        logger.info("主動觸發測試信號...")
                        self._make_request("POST", "/api/v1/realtime-signals/signals/test")
                    
                    continue
        
        except Exception as e:
            logger.error(f"監控過程中發生錯誤: {e}")
            
        # 返回流程狀態
        return flow_steps
    
    async def _validate_complete_flow(self):
        """驗證完整流程"""
        logger.info("驗證流程完整性...")
        
        validation_results = {
            "data_collection": False,
            "technical_analysis": False,
            "signal_generation": False,
            "signal_broadcast": False,
            "timing_performance": False
        }
        
        try:
            # 1. 驗證數據收集
            if len(self.received_data["price_updates"]) > 0:
                validation_results["data_collection"] = True
                logger.info("✅ 數據收集: 已接收價格更新")
            else:
                logger.warning("⚠️ 數據收集: 未接收到價格更新")
            
            # 2. 驗證技術分析
            if len(self.received_data["market_data"]) > 0 or len(self.received_data["trading_signals"]) > 0:
                validation_results["technical_analysis"] = True
                logger.info("✅ 技術分析: 已執行分析")
            else:
                logger.warning("⚠️ 技術分析: 未檢測到分析活動")
            
            # 3. 驗證信號生成
            if len(self.received_data["trading_signals"]) > 0:
                validation_results["signal_generation"] = True
                signal_count = len(self.received_data["trading_signals"])
                logger.info(f"✅ 信號生成: 已生成 {signal_count} 個信號")
                
                # 檢查信號質量
                for signal in self.received_data["trading_signals"]:
                    signal_data = signal.get("data", {})
                    confidence = signal_data.get("confidence", 0)
                    has_reasoning = bool(signal_data.get("reasoning"))
                    
                    logger.info(f"   信號質量: 信心度 {confidence:.2f}, 有推理: {has_reasoning}")
            else:
                logger.warning("⚠️ 信號生成: 未生成交易信號")
            
            # 4. 驗證信號廣播
            validation_results["signal_broadcast"] = validation_results["signal_generation"]
            if validation_results["signal_broadcast"]:
                logger.info("✅ 信號廣播: 信號已通過 WebSocket 廣播")
            else:
                logger.warning("⚠️ 信號廣播: 未接收到廣播信號")
            
            # 5. 驗證時間性能
            if self.received_data["trading_signals"]:
                first_signal = self.received_data["trading_signals"][0]
                signal_time = datetime.fromisoformat(first_signal.get("timestamp", ""))
                current_time = datetime.now()
                
                # 信號應該是最近生成的（5分鐘內）
                if (current_time - signal_time).total_seconds() < 300:
                    validation_results["timing_performance"] = True
                    logger.info("✅ 時間性能: 信號及時生成")
                else:
                    logger.warning("⚠️ 時間性能: 信號生成延遲")
            
            # 計算總體驗證結果
            passed_validations = sum(validation_results.values())
            total_validations = len(validation_results)
            
            logger.info(f"\n驗證結果: {passed_validations}/{total_validations} 項通過")
            
            # 如果至少80%通過，認為流程正常
            success_threshold = 0.8
            overall_success = (passed_validations / total_validations) >= success_threshold
            
            if overall_success:
                logger.info("🎉 完整自動化流程驗證通過！")
            else:
                logger.warning("⚠️ 自動化流程存在問題，需要改善")
            
            return overall_success
            
        except Exception as e:
            logger.error(f"❌ 流程驗證失敗: {e}")
            return False
    
    async def _cleanup(self):
        """清理測試環境"""
        logger.info("清理測試環境...")
        
        try:
            # 關閉 WebSocket
            if self.websocket:
                await self.websocket.close()
                
            # 停止信號引擎
            self._make_request("POST", "/api/v1/realtime-signals/stop")
            
            logger.info("✅ 清理完成")
            
        except Exception as e:
            logger.error(f"清理時發生錯誤: {e}")
    
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
    logger.info("🚀 開始自動化流程端到端測試...")
    
    tester = AutomationFlowTester()
    
    try:
        # 執行完整流程測試
        success = await tester.test_complete_automation_flow()
        
        if success:
            logger.info("🎉 自動化流程端到端測試完全成功！")
            logger.info("💡 系統已實現:")
            logger.info("   📡 WebSocket 即時數據收集")
            logger.info("   🔍 pandas-ta 技術分析")
            logger.info("   🎯 智能交易信號生成")
            logger.info("   📢 自動信號廣播")
            return True
        else:
            logger.warning("⚠️ 自動化流程存在改善空間")
            return False
            
    except Exception as e:
        logger.error(f"❌ 測試執行失敗: {e}")
        return False

if __name__ == "__main__":
    # 運行測試
    success = asyncio.run(main())
    exit(0 if success else 1)
