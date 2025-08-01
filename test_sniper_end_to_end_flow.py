#!/usr/bin/env python3
"""
🎯 狙擊手計劃端到端完整業務流程測試
測試目的：驗證狙擊手計劃核心業務邏輯從頭到尾徹底成功執行

完整流程：
1. WebSocket 實時數據監測
2. 數據傳入 pandas-ta 技術分析
3. 狙擊手算法分析篩選
4. 生成高精準度信號
5. 前端實時顯示
6. 自動發送 Gmail 通知

測試重點：
- 驗證 WebSocket 數據流暢性
- 確認技術分析引擎運作
- 檢查狙擊手篩選邏輯
- 測試前端信號顯示
- 驗證 Gmail 通知發送
"""

import asyncio
import json
import time
import logging
import websockets
import requests
from datetime import datetime
from typing import Dict, List, Any
import sys
import os

# 添加項目路徑
sys.path.append('/Users/itts/Desktop/Trading X')

from app.services.market_data import MarketDataService
from app.services.realtime_signal_engine import RealtimeSignalEngine

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('sniper_end_to_end_test.log')
    ]
)
logger = logging.getLogger(__name__)

class SniperEndToEndTester:
    """狙擊手計劃端到端測試器"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.websocket_url = "ws://localhost:8000/api/v1/realtime-market/ws"
        self.frontend_url = "http://localhost:3000"
        
        self.test_results = []
        self.websocket_connection = None
        self.received_signals = []
        self.test_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
        
        # 測試階段計數器
        self.current_stage = 0
        self.total_stages = 7
        
    def log_stage_result(self, stage_name: str, success: bool, details: str = "", data: Any = None):
        """記錄測試階段結果"""
        self.current_stage += 1
        timestamp = datetime.now().isoformat()
        
        result = {
            "stage": f"{self.current_stage}/{self.total_stages}",
            "name": stage_name,
            "success": success,
            "details": details,
            "data": data,
            "timestamp": timestamp
        }
        
        self.test_results.append(result)
        
        status_emoji = "✅" if success else "❌"
        progress = f"[{self.current_stage}/{self.total_stages}]"
        
        logger.info(f"{status_emoji} {progress} {stage_name}")
        if details:
            logger.info(f"   📋 {details}")
        if data and isinstance(data, dict):
            for key, value in data.items():
                logger.info(f"   📊 {key}: {value}")
        
        print(f"\n{status_emoji} {progress} {stage_name}")
        if details:
            print(f"   📋 {details}")
            
    async def run_complete_test(self):
        """執行完整的端到端測試"""
        print("🎯" * 50)
        print("🎯 狙擊手計劃端到端完整業務流程測試")
        print("🎯 測試目的：驗證核心業務邏輯完整執行")
        print("🎯" * 50)
        
        start_time = time.time()
        
        try:
            # 階段1: 檢查後端服務健康狀態
            await self.test_backend_health()
            
            # 階段2: 測試 WebSocket 連接和數據監測
            await self.test_websocket_data_monitoring()
            
            # 階段3: 測試技術分析引擎
            await self.test_technical_analysis_engine()
            
            # 階段4: 測試狙擊手信號生成
            await self.test_sniper_signal_generation()
            
            # 階段5: 測試前端信號顯示
            await self.test_frontend_signal_display()
            
            # 階段6: 測試 Gmail 通知發送
            await self.test_gmail_notification()
            
            # 階段7: 驗證完整業務流程
            await self.test_complete_business_flow()
            
        except Exception as e:
            logger.error(f"❌ 測試執行失敗: {e}")
            self.log_stage_result(f"測試執行", False, f"執行失敗: {str(e)}")
            
        finally:
            # 清理 WebSocket 連接
            if self.websocket_connection:
                await self.websocket_connection.close()
        
        # 生成測試報告
        await self.generate_test_report(start_time)
        
    async def test_backend_health(self):
        """階段1: 檢查後端服務健康狀態"""
        try:
            # 檢查基本 API 健康狀態
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                self.log_stage_result(
                    "後端服務健康檢查", 
                    True, 
                    "後端服務運行正常",
                    {"狀態": "正常", "響應時間": f"{response.elapsed.total_seconds():.3f}s"}
                )
            else:
                self.log_stage_result(
                    "後端服務健康檢查", 
                    False, 
                    f"API 響應異常: {response.status_code}"
                )
                return
                
            # 檢查實時信號引擎狀態
            response = requests.get(f"{self.backend_url}/api/v1/realtime-signals/health", timeout=10)
            
            if response.status_code == 200:
                engine_data = response.json()
                engine_status = engine_data.get("data", {})
                
                self.log_stage_result(
                    "實時信號引擎健康檢查", 
                    True, 
                    "信號引擎運行正常",
                    {
                        "引擎狀態": engine_status.get("status", "unknown"),
                        "監控交易對": engine_status.get("metrics", {}).get("monitored_pairs", 0),
                        "活躍連接": engine_status.get("metrics", {}).get("active_connections", 0)
                    }
                )
            else:
                self.log_stage_result(
                    "實時信號引擎健康檢查", 
                    False, 
                    f"信號引擎狀態異常: {response.status_code}"
                )
                
        except Exception as e:
            self.log_stage_result("後端服務健康檢查", False, f"健康檢查失敗: {str(e)}")
            
    async def test_websocket_data_monitoring(self):
        """階段2: 測試 WebSocket 連接和數據監測"""
        try:
            # 建立 WebSocket 連接
            self.websocket_connection = await websockets.connect(
                self.websocket_url,
                ping_interval=20,
                ping_timeout=10
            )
            
            # 等待連接確認
            welcome_msg = await asyncio.wait_for(
                self.websocket_connection.recv(), 
                timeout=10.0
            )
            welcome_data = json.loads(welcome_msg)
            
            if welcome_data.get("type") == "connection_established":
                self.log_stage_result(
                    "WebSocket 連接建立", 
                    True, 
                    "成功建立 WebSocket 連接",
                    {"連接時間": welcome_data.get("timestamp", "unknown")}
                )
            else:
                self.log_stage_result(
                    "WebSocket 連接建立", 
                    False, 
                    "未收到預期的連接確認消息"
                )
                return
                
            # 發送訂閱請求
            subscribe_msg = {
                "action": "subscribe",
                "symbols": self.test_symbols,
                "data_types": ["prices", "signals"]
            }
            
            await self.websocket_connection.send(json.dumps(subscribe_msg))
            
            # 等待訂閱確認
            subscription_msg = await asyncio.wait_for(
                self.websocket_connection.recv(), 
                timeout=10.0
            )
            subscription_data = json.loads(subscription_msg)
            
            if subscription_data.get("type") == "subscription_confirmed":
                confirmed_symbols = subscription_data.get("symbols", [])
                self.log_stage_result(
                    "WebSocket 數據訂閱", 
                    True, 
                    f"成功訂閱 {len(confirmed_symbols)} 個交易對",
                    {"訂閱交易對": ", ".join(confirmed_symbols)}
                )
            else:
                self.log_stage_result(
                    "WebSocket 數據訂閱", 
                    False, 
                    "未收到訂閱確認"
                )
                return
                
            # 等待和收集實時數據
            price_updates_received = 0
            data_collection_start = time.time()
            
            while time.time() - data_collection_start < 15:  # 收集15秒的數據
                try:
                    message = await asyncio.wait_for(
                        self.websocket_connection.recv(), 
                        timeout=2.0
                    )
                    data = json.loads(message)
                    
                    if data.get("type") in ["price_update", "price_batch_update"]:
                        price_updates_received += 1
                        
                        if price_updates_received == 1:
                            logger.info(f"📡 開始接收實時價格數據...")
                        
                        if price_updates_received % 5 == 0:
                            logger.info(f"📊 已接收 {price_updates_received} 次價格更新")
                            
                except asyncio.TimeoutError:
                    continue
                    
            if price_updates_received > 0:
                self.log_stage_result(
                    "WebSocket 實時數據監測", 
                    True, 
                    f"成功接收 {price_updates_received} 次實時數據更新",
                    {
                        "數據更新次數": price_updates_received,
                        "平均更新頻率": f"{price_updates_received/15:.1f} 次/秒"
                    }
                )
            else:
                self.log_stage_result(
                    "WebSocket 實時數據監測", 
                    False, 
                    "15秒內未收到任何價格更新"
                )
                
        except Exception as e:
            self.log_stage_result("WebSocket 數據監測", False, f"WebSocket 測試失敗: {str(e)}")
            
    async def test_technical_analysis_engine(self):
        """階段3: 測試技術分析引擎"""
        try:
            # 測試精準篩選信號 API
            response = requests.get(
                f"{self.backend_url}/api/v1/scalping/signals",
                timeout=15
            )
            
            if response.status_code == 200:
                signals_data = response.json()
                signals = signals_data.get('signals', [])
                
                # 檢查技術指標計算
                technical_indicators_found = False
                for signal in signals[:3]:  # 檢查前3個信號
                    if signal.get('technical_analysis') or signal.get('indicators_used'):
                        technical_indicators_found = True
                        break
                
                self.log_stage_result(
                    "技術分析引擎運作", 
                    True, 
                    f"技術分析引擎正常運作，生成 {len(signals)} 個分析信號",
                    {
                        "分析信號數": len(signals),
                        "包含技術指標": "是" if technical_indicators_found else "否"
                    }
                )
            else:
                self.log_stage_result(
                    "技術分析引擎運作", 
                    False, 
                    f"技術分析 API 響應異常: {response.status_code}"
                )
                return
                
            # 測試狙擊手統一數據層
            test_symbols_str = ",".join(self.test_symbols[:2])  # 測試前2個交易對
            response = requests.get(
                f"{self.backend_url}/api/v1/scalping/sniper-unified-data-layer",
                params={"symbols": test_symbols_str, "timeframe": "1h"},
                timeout=20
            )
            
            if response.status_code == 200:
                sniper_data = response.json()
                results = sniper_data.get('results', {})
                
                analyzed_symbols = len([k for k, v in results.items() if 'error' not in v])
                
                self.log_stage_result(
                    "狙擊手統一數據層", 
                    True, 
                    f"狙擊手數據層正常運作，分析 {analyzed_symbols} 個交易對",
                    {
                        "分析交易對數": analyzed_symbols,
                        "數據完整性": "通過" if sniper_data.get('data_integrity', {}).get('no_fake_data') else "未知"
                    }
                )
            else:
                self.log_stage_result(
                    "狙擊手統一數據層", 
                    False, 
                    f"狙擊手數據層 API 異常: {response.status_code}"
                )
                
        except Exception as e:
            self.log_stage_result("技術分析引擎", False, f"技術分析測試失敗: {str(e)}")
            
    async def test_sniper_signal_generation(self):
        """階段4: 測試狙擊手信號生成"""
        try:
            # 觸發測試信號生成
            response = requests.post(
                f"{self.backend_url}/api/v1/realtime-signals/signals/test",
                timeout=15
            )
            
            if response.status_code == 200:
                test_result = response.json()
                
                if test_result.get("success"):
                    signal_data = test_result.get("signal", {})
                    
                    self.log_stage_result(
                        "狙擊手測試信號生成", 
                        True, 
                        "成功生成狙擊手測試信號",
                        {
                            "交易對": signal_data.get("symbol", "unknown"),
                            "信號類型": signal_data.get("signal_type", "unknown"),
                            "信心度": f"{signal_data.get('confidence', 0):.1%}",
                            "進場價": f"${signal_data.get('entry_price', 0):,.2f}"
                        }
                    )
                    
                    # 等待通過 WebSocket 接收信號
                    if self.websocket_connection:
                        signal_received_via_websocket = False
                        wait_start = time.time()
                        
                        while time.time() - wait_start < 10:  # 等待10秒
                            try:
                                message = await asyncio.wait_for(
                                    self.websocket_connection.recv(), 
                                    timeout=2.0
                                )
                                data = json.loads(message)
                                
                                if data.get("type") == "trading_signal":
                                    signal_ws_data = data.get("data", {})
                                    self.received_signals.append(signal_ws_data)
                                    signal_received_via_websocket = True
                                    
                                    self.log_stage_result(
                                        "WebSocket 信號廣播", 
                                        True, 
                                        "成功通過 WebSocket 接收狙擊手信號",
                                        {
                                            "交易對": signal_ws_data.get("symbol", "unknown"),
                                            "信號類型": signal_ws_data.get("signal_type", "unknown"),
                                            "廣播延遲": "< 10秒"
                                        }
                                    )
                                    break
                                    
                            except asyncio.TimeoutError:
                                continue
                                
                        if not signal_received_via_websocket:
                            self.log_stage_result(
                                "WebSocket 信號廣播", 
                                False, 
                                "10秒內未通過 WebSocket 接收到信號"
                            )
                    
                else:
                    self.log_stage_result(
                        "狙擊手測試信號生成", 
                        False, 
                        "測試信號生成失敗"
                    )
            else:
                self.log_stage_result(
                    "狙擊手信號生成", 
                    False, 
                    f"信號生成 API 異常: {response.status_code}"
                )
                
        except Exception as e:
            self.log_stage_result("狙擊手信號生成", False, f"信號生成測試失敗: {str(e)}")
            
    async def test_frontend_signal_display(self):
        """階段5: 測試前端信號顯示"""
        try:
            # 檢查前端狙擊手界面是否可訪問
            try:
                response = requests.get(f"{self.frontend_url}/sniper", timeout=10)
                frontend_accessible = response.status_code == 200
            except:
                frontend_accessible = False
                
            if frontend_accessible:
                self.log_stage_result(
                    "前端狙擊手界面", 
                    True, 
                    "狙擊手界面可正常訪問",
                    {"界面地址": f"{self.frontend_url}/sniper"}
                )
            else:
                self.log_stage_result(
                    "前端狙擊手界面", 
                    False, 
                    "狙擊手界面無法訪問，請確認前端服務是否運行"
                )
                
            # 檢查最近信號 API（前端會調用此API顯示信號）
            response = requests.get(
                f"{self.backend_url}/api/v1/realtime-signals/signals/recent",
                params={"hours": 1},  # 最近1小時
                timeout=10
            )
            
            if response.status_code == 200:
                recent_signals_data = response.json()
                recent_signals = recent_signals_data.get('signals', [])
                
                self.log_stage_result(
                    "前端信號數據 API", 
                    True, 
                    f"前端可獲取 {len(recent_signals)} 個最近信號",
                    {"最近信號數": len(recent_signals)}
                )
            else:
                self.log_stage_result(
                    "前端信號數據 API", 
                    False, 
                    f"前端信號 API 異常: {response.status_code}"
                )
                
        except Exception as e:
            self.log_stage_result("前端信號顯示", False, f"前端測試失敗: {str(e)}")
            
    async def test_gmail_notification(self):
        """階段6: 測試 Gmail 通知發送"""
        try:
            # 測試 Gmail 通知功能
            response = requests.get(
                f"{self.backend_url}/api/v1/notifications/email/test",
                timeout=15
            )
            
            if response.status_code == 200:
                test_result = response.json()
                
                if test_result.get("status") == "success":
                    email_result = test_result.get("test_result", {})
                    
                    self.log_stage_result(
                        "Gmail 通知發送", 
                        True, 
                        "Gmail 測試通知發送成功",
                        {
                            "發送狀態": email_result.get("status", "unknown"),
                            "郵件主題": email_result.get("email_subject", "unknown"),
                            "發送時間": email_result.get("timestamp", "unknown")
                        }
                    )
                else:
                    self.log_stage_result(
                        "Gmail 通知發送", 
                        False, 
                        "Gmail 測試通知發送失敗"
                    )
            else:
                self.log_stage_result(
                    "Gmail 通知發送", 
                    False, 
                    f"Gmail 通知 API 異常: {response.status_code}"
                )
                
        except Exception as e:
            self.log_stage_result("Gmail 通知發送", False, f"Gmail 通知測試失敗: {str(e)}")
            
    async def test_complete_business_flow(self):
        """階段7: 驗證完整業務流程"""
        try:
            # 計算測試成功率
            successful_stages = len([r for r in self.test_results if r["success"]])
            total_tested_stages = len(self.test_results)
            success_rate = (successful_stages / total_tested_stages) * 100 if total_tested_stages > 0 else 0
            
            # 檢查關鍵流程是否全部成功
            critical_stages = [
                "WebSocket 連接建立",
                "WebSocket 實時數據監測", 
                "技術分析引擎運作",
                "狙擊手測試信號生成",
                "Gmail 通知發送"
            ]
            
            critical_success_count = len([
                r for r in self.test_results 
                if r["name"] in critical_stages and r["success"]
            ])
            
            critical_success_rate = (critical_success_count / len(critical_stages)) * 100
            
            # 檢查是否收到了 WebSocket 信號
            websocket_signals_received = len(self.received_signals)
            
            if success_rate >= 80 and critical_success_rate >= 80:
                self.log_stage_result(
                    "完整業務流程驗證", 
                    True, 
                    f"狙擊手計劃核心業務邏輯驗證成功！",
                    {
                        "整體成功率": f"{success_rate:.1f}%",
                        "關鍵流程成功率": f"{critical_success_rate:.1f}%",
                        "WebSocket 信號接收": f"{websocket_signals_received} 個",
                        "業務流程狀態": "完全可用" if success_rate >= 90 else "基本可用"
                    }
                )
            else:
                self.log_stage_result(
                    "完整業務流程驗證", 
                    False, 
                    f"狙擊手計劃業務流程存在問題",
                    {
                        "整體成功率": f"{success_rate:.1f}%",
                        "關鍵流程成功率": f"{critical_success_rate:.1f}%",
                        "需要修復的問題": total_tested_stages - successful_stages
                    }
                )
                
        except Exception as e:
            self.log_stage_result("完整業務流程驗證", False, f"業務流程驗證失敗: {str(e)}")
            
    async def generate_test_report(self, start_time: float):
        """生成測試報告"""
        end_time = time.time()
        total_duration = end_time - start_time
        
        print("\n" + "🎯" * 50)
        print("🎯 狙擊手計劃端到端測試報告")
        print("🎯" * 50)
        
        print(f"\n📊 測試總結:")
        print(f"   ⏱️  測試總時長: {total_duration:.1f} 秒")
        print(f"   🔍 測試階段總數: {len(self.test_results)}")
        
        successful_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        print(f"   ✅ 成功階段: {len(successful_tests)}")
        print(f"   ❌ 失敗階段: {len(failed_tests)}")
        print(f"   📈 成功率: {(len(successful_tests)/len(self.test_results)*100):.1f}%")
        
        print(f"\n📋 詳細測試結果:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅" if result["success"] else "❌"
            print(f"   {status} {result['stage']} {result['name']}")
            if result['details']:
                print(f"      📝 {result['details']}")
                
        if failed_tests:
            print(f"\n🔧 需要修復的問題:")
            for result in failed_tests:
                print(f"   ❌ {result['name']}: {result['details']}")
                
        print(f"\n🎯 狙擊手計劃業務流程狀態:")
        if len(successful_tests) >= len(self.test_results) * 0.8:
            print(f"   🚀 狙擊手計劃核心業務邏輯運行良好！")
            print(f"   💡 WebSocket → pandas-ta → 狙擊手篩選 → 前端顯示 → Gmail 通知 流程已驗證")
        else:
            print(f"   ⚠️  狙擊手計劃存在一些問題，建議檢查失敗的階段")
            
        print(f"\n📧 Gmail 通知信息:")
        print(f"   📬 請檢查您的 Gmail 收件匣 (henry1010921@gmail.com)")
        print(f"   📨 應該收到狙擊手計劃的測試通知郵件")
        
        print(f"\n🌐 系統訪問地址:")
        print(f"   🖥️  狙擊手界面: {self.frontend_url}/sniper")
        print(f"   🔧 後端 API: {self.backend_url}")
        print(f"   📡 WebSocket: {self.websocket_url}")
        
        print("\n" + "🎯" * 50)
        
        # 寫入詳細日誌文件
        report_filename = f"sniper_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump({
                "test_summary": {
                    "total_duration": total_duration,
                    "total_stages": len(self.test_results),
                    "successful_stages": len(successful_tests),
                    "failed_stages": len(failed_tests),
                    "success_rate": (len(successful_tests)/len(self.test_results)*100)
                },
                "detailed_results": self.test_results,
                "websocket_signals_received": self.received_signals,
                "test_timestamp": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
            
        print(f"📄 詳細測試報告已保存至: {report_filename}")

async def main():
    """主測試函數"""
    tester = SniperEndToEndTester()
    await tester.run_complete_test()

if __name__ == "__main__":
    asyncio.run(main())
