#!/usr/bin/env python3
"""
🌐 Trading-X 真實幣安數據流測試
=================================

功能：
1. 連接幣安WebSocket API獲取真實價格數據
2. 測試完整系統在真實數據下的性能
3. 驗證延遲、錯誤處理和穩定性
4. 生成真實環境測試報告
"""

import asyncio
import websockets
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import numpy as np
from dataclasses import dataclass
import ssl

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RealDataTestResult:
    """真實數據測試結果"""
    test_name: str
    success: bool
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    data_points_processed: int
    avg_latency_ms: float
    max_latency_ms: float
    error_count: int
    details: Dict[str, Any]

class BinanceRealDataFlowTest:
    """幣安真實數據流測試"""
    
    def __init__(self):
        self.test_results: List[RealDataTestResult] = []
        self.websocket_url = "wss://stream.binance.com:9443/ws"
        self.test_symbols = ["btcusdt", "ethusdt", "bnbusdt"]
        self.data_buffer = []
        self.processing_metrics = {
            'latencies': [],
            'processing_times': [],
            'error_events': [],
            'data_integrity_checks': []
        }
        
        # 載入測試配置
        self.config = self._load_real_data_config()
        
    def _load_real_data_config(self) -> Dict[str, Any]:
        """載入真實數據測試配置"""
        return {
            "real_data_test_configuration": {
                "description": "真實幣安數據流測試配置",
                "version": "1.0",
                "test_duration_seconds": 10,
                "expected_performance": {
                    "max_acceptable_latency_ms": 500,
                    "min_data_points": 30,
                    "max_error_rate": 5.0,
                    "min_success_rate": 90.0
                },
                "symbols_to_test": ["BTCUSDT", "ETHUSDT", "BNBUSDT"],
                "websocket_config": {
                    "connection_timeout": 10,
                    "ping_interval": 20,
                    "ping_timeout": 10,
                    "close_timeout": 10
                },
                "performance_thresholds": {
                    "excellent": {"latency_ms": 100, "success_rate": 98.0},
                    "good": {"latency_ms": 300, "success_rate": 95.0},
                    "acceptable": {"latency_ms": 500, "success_rate": 90.0}
                }
            }
        }
    
    async def test_real_binance_websocket_connection(self) -> RealDataTestResult:
        """測試真實幣安WebSocket連接"""
        logger.info("🔄 測試真實幣安WebSocket連接...")
        
        start_time = datetime.now()
        success = False
        error_count = 0
        data_points = 0
        latencies = []
        
        try:
            # 創建WebSocket連接
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # 構建訂閱消息
            subscribe_msg = {
                "method": "SUBSCRIBE",
                "params": [f"{symbol}@ticker" for symbol in self.test_symbols],
                "id": 1
            }
            
            async with websockets.connect(
                self.websocket_url,
                ssl=ssl_context,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=10
            ) as websocket:
                
                # 發送訂閱請求
                await websocket.send(json.dumps(subscribe_msg))
                logger.info(f"✅ 已訂閱符號: {', '.join(self.test_symbols)}")
                
                # 接收數據測試
                test_duration = self.config["real_data_test_configuration"]["test_duration_seconds"]
                end_time = time.time() + test_duration
                
                while time.time() < end_time:
                    try:
                        # 接收數據並測量延遲
                        receive_start = time.time()
                        
                        # 設置超時
                        message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        
                        receive_end = time.time()
                        latency_ms = (receive_end - receive_start) * 1000
                        latencies.append(latency_ms)
                        
                        # 解析數據
                        data = json.loads(message)
                        
                        # 處理價格數據
                        if 'c' in data:  # 'c' 是當前價格
                            await self._process_real_price_data(data, receive_end)
                            data_points += 1
                            
                            if data_points % 10 == 0:
                                logger.info(f"  已處理 {data_points} 個數據點，平均延遲: {np.mean(latencies[-10:]):.2f}ms")
                        
                    except asyncio.TimeoutError:
                        error_count += 1
                        logger.warning("⚠️ WebSocket接收超時")
                        if error_count > 5:
                            break
                    except json.JSONDecodeError:
                        error_count += 1
                        logger.warning("⚠️ 數據解析錯誤")
                    except Exception as e:
                        error_count += 1
                        logger.error(f"❌ 數據處理錯誤: {e}")
                
                success = data_points >= self.config["real_data_test_configuration"]["expected_performance"]["min_data_points"]
                
        except Exception as e:
            logger.error(f"❌ WebSocket連接失敗: {e}")
            error_count += 1
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        result = RealDataTestResult(
            test_name="真實幣安WebSocket連接測試",
            success=success,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            data_points_processed=data_points,
            avg_latency_ms=np.mean(latencies) if latencies else 0,
            max_latency_ms=np.max(latencies) if latencies else 0,
            error_count=error_count,
            details={
                "symbols_tested": self.test_symbols,
                "latency_distribution": {
                    "min": np.min(latencies) if latencies else 0,
                    "max": np.max(latencies) if latencies else 0,
                    "mean": np.mean(latencies) if latencies else 0,
                    "std": np.std(latencies) if latencies else 0
                },
                "error_rate": (error_count / max(data_points, 1)) * 100,
                "data_rate_per_second": data_points / duration if duration > 0 else 0
            }
        )
        
        logger.info(f"{'✅' if success else '❌'} 真實數據測試: {data_points}個數據點, {np.mean(latencies) if latencies else 0:.2f}ms平均延遲")
        return result
    
    async def _process_real_price_data(self, price_data: Dict[str, Any], timestamp: float) -> None:
        """處理真實價格數據通過完整系統流程"""
        try:
            # 模擬完整系統處理流程
            processing_start = time.time()
            
            # Phase1: 信號生成
            phase1_result = await self._simulate_phase1_with_real_data(price_data)
            
            # Phase2: 策略處理 
            if phase1_result.get("signals"):
                phase2_result = await self._simulate_phase2_with_real_data(
                    phase1_result["signals"], price_data
                )
                
                # Phase3: 整合決策
                if phase2_result.get("strategy_decision"):
                    phase3_result = await self._simulate_phase3_integration(phase2_result)
            
            processing_end = time.time()
            processing_time = (processing_end - processing_start) * 1000
            
            self.processing_metrics['processing_times'].append(processing_time)
            
        except Exception as e:
            self.processing_metrics['error_events'].append({
                "timestamp": timestamp,
                "error": str(e),
                "data": price_data
            })
    
    async def _simulate_phase1_with_real_data(self, price_data: Dict[str, Any]) -> Dict[str, Any]:
        """使用真實數據模擬Phase1處理"""
        await asyncio.sleep(0.01)  # 模擬實際處理時間
        
        signals = []
        
        # 基於真實價格變化生成信號
        if 'c' in price_data and 'o' in price_data:
            current_price = float(price_data['c'])
            open_price = float(price_data['o'])
            price_change = (current_price - open_price) / open_price
            
            if abs(price_change) > 0.001:  # 0.1%變化
                signals.append({
                    "type": "PRICE_MOVEMENT",
                    "strength": min(1.0, abs(price_change) * 100),
                    "direction": "LONG" if price_change > 0 else "SHORT",
                    "confidence": 0.7 + min(0.3, abs(price_change) * 50)
                })
        
        return {"signals": signals, "processing_time_ms": 10}
    
    async def _simulate_phase2_with_real_data(self, signals: List[Dict], price_data: Dict[str, Any]) -> Dict[str, Any]:
        """使用真實數據模擬Phase2處理"""
        await asyncio.sleep(0.015)  # 模擬策略計算時間
        
        if not signals:
            return {"strategy_decision": "WAIT"}
        
        # 基於信號強度做決策
        strongest_signal = max(signals, key=lambda s: s.get("strength", 0))
        
        if strongest_signal["strength"] > 0.5:
            decision = strongest_signal["direction"]
        else:
            decision = "WAIT"
        
        return {
            "strategy_decision": decision,
            "confidence": strongest_signal.get("confidence", 0.5),
            "processing_time_ms": 15
        }
    
    async def _simulate_phase3_integration(self, phase2_result: Dict[str, Any]) -> Dict[str, Any]:
        """模擬Phase3整合處理"""
        await asyncio.sleep(0.005)  # 模擬整合時間
        
        return {
            "final_decision": phase2_result["strategy_decision"],
            "risk_assessment": "LOW" if phase2_result.get("confidence", 0) > 0.7 else "MEDIUM",
            "processing_time_ms": 5
        }
    
    async def test_system_performance_under_real_load(self) -> RealDataTestResult:
        """測試系統在真實負載下的性能"""
        logger.info("🔄 測試系統在真實負載下的性能...")
        
        start_time = datetime.now()
        
        # 運行真實數據測試
        websocket_result = await self.test_real_binance_websocket_connection()
        
        # 分析性能指標
        processing_times = self.processing_metrics['processing_times']
        error_events = self.processing_metrics['error_events']
        
        # 計算性能評分
        avg_processing_time = np.mean(processing_times) if processing_times else 0
        max_processing_time = np.max(processing_times) if processing_times else 0
        error_rate = len(error_events) / max(len(processing_times), 1) * 100
        
        # 性能評級
        performance_config = self.config["real_data_test_configuration"]["performance_thresholds"]
        
        if avg_processing_time <= performance_config["excellent"]["latency_ms"] and error_rate <= 2.0:
            performance_grade = "優秀"
        elif avg_processing_time <= performance_config["good"]["latency_ms"] and error_rate <= 5.0:
            performance_grade = "良好"
        elif avg_processing_time <= performance_config["acceptable"]["latency_ms"] and error_rate <= 10.0:
            performance_grade = "可接受"
        else:
            performance_grade = "需改進"
        
        success = websocket_result.success and error_rate <= 10.0
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        result = RealDataTestResult(
            test_name="真實負載下系統性能測試",
            success=success,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            data_points_processed=websocket_result.data_points_processed,
            avg_latency_ms=avg_processing_time,
            max_latency_ms=max_processing_time,
            error_count=len(error_events),
            details={
                "performance_grade": performance_grade,
                "websocket_performance": {
                    "avg_latency_ms": websocket_result.avg_latency_ms,
                    "max_latency_ms": websocket_result.max_latency_ms,
                    "data_points": websocket_result.data_points_processed
                },
                "processing_performance": {
                    "avg_processing_time_ms": avg_processing_time,
                    "max_processing_time_ms": max_processing_time,
                    "total_processed": len(processing_times)
                },
                "error_analysis": {
                    "error_rate": error_rate,
                    "error_count": len(error_events),
                    "error_types": list(set(e.get("error", "unknown") for e in error_events))
                },
                "recommendations": self._generate_performance_recommendations(
                    avg_processing_time, error_rate, performance_grade
                )
            }
        )
        
        logger.info(f"{'✅' if success else '❌'} 真實負載測試: {performance_grade}, {error_rate:.1f}% 錯誤率")
        return result
    
    def _generate_performance_recommendations(self, avg_latency: float, error_rate: float, grade: str) -> List[str]:
        """生成性能改進建議"""
        recommendations = []
        
        if avg_latency > 300:
            recommendations.append("優化數據處理算法以減少延遲")
        if avg_latency > 500:
            recommendations.append("考慮使用更快的硬件或分散式處理")
        
        if error_rate > 5:
            recommendations.append("增強錯誤處理和重試機制")
        if error_rate > 10:
            recommendations.append("檢查網絡連接穩定性和API配額")
        
        if grade == "需改進":
            recommendations.append("進行全面的系統性能調優")
        elif grade == "可接受":
            recommendations.append("可考慮進一步優化以提升用戶體驗")
        
        return recommendations
    
    async def run_comprehensive_real_data_test(self) -> Dict[str, Any]:
        """運行綜合真實數據測試"""
        logger.info("🚀 開始綜合真實數據測試...")
        
        start_time = datetime.now()
        
        # 執行性能測試
        performance_result = await self.test_system_performance_under_real_load()
        
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        # 生成綜合報告
        report = {
            "execution_summary": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "total_duration_s": total_duration,
                "test_type": "真實幣安數據流綜合測試",
                "overall_status": "✅ PASSED" if performance_result.success else "❌ FAILED"
            },
            "real_data_performance": {
                "data_points_processed": performance_result.data_points_processed,
                "avg_latency_ms": performance_result.avg_latency_ms,
                "max_latency_ms": performance_result.max_latency_ms,
                "error_count": performance_result.error_count,
                "performance_grade": performance_result.details["performance_grade"],
                "success": performance_result.success
            },
            "detailed_analysis": performance_result.details,
            "test_environment": {
                "symbols_tested": self.test_symbols,
                "test_duration": self.config["real_data_test_configuration"]["test_duration_seconds"],
                "websocket_url": self.websocket_url
            }
        }
        
        # 保存測試報告
        report_filename = f"real_data_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(f"test_reports/{report_filename}", 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 真實數據測試報告已保存: {report_filename}")
        
        return report

async def main():
    """主函數"""
    logger.info("🌐 Trading-X 真實幣安數據流測試啟動")
    
    # 創建測試報告目錄
    import os
    os.makedirs("test_reports", exist_ok=True)
    
    tester = BinanceRealDataFlowTest()
    
    try:
        report = await tester.run_comprehensive_real_data_test()
        
        print("\n" + "="*80)
        print("🏆 真實數據流測試完成")
        print("="*80)
        print(f"📊 整體狀態: {report['execution_summary']['overall_status']}")
        print(f"⏱️  總耗時: {report['execution_summary']['total_duration_s']:.2f} 秒")
        print(f"📈 性能評級: {report['real_data_performance']['performance_grade']}")
        print(f"🎯 數據點處理: {report['real_data_performance']['data_points_processed']}")
        print(f"⚡ 平均延遲: {report['real_data_performance']['avg_latency_ms']:.2f}ms")
        print(f"❌ 錯誤數量: {report['real_data_performance']['error_count']}")
        
        if report['detailed_analysis'].get('recommendations'):
            print(f"\n💡 改進建議:")
            for i, rec in enumerate(report['detailed_analysis']['recommendations'], 1):
                print(f"   {i}. {rec}")
        
        return 0 if report['real_data_performance']['success'] else 1
        
    except Exception as e:
        logger.error(f"💥 真實數據測試嚴重失敗: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
