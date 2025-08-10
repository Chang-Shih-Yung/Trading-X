#!/usr/bin/env python3
"""
WebSocket 實時數據驅動器 JSON 規範匹配性檢查
檢查 websocket_realtime_driver.py 是否完全符合 websocket_realtime_driver_dependency.json v1.0.0
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# 添加項目路徑
sys.path.append('/Users/henrychang/Desktop/Trading-X')
sys.path.append('/Users/henrychang/Desktop/Trading-X/X/backend')

from X.backend.phase1_signal_generation.websocket_realtime_driver.websocket_realtime_driver import (
    WebSocketRealTimeDriver,
    websocket_realtime_driver
)

class JSONMatchingVerification:
    """JSON 規範匹配性驗證"""
    
    def __init__(self):
        self.json_config_path = "/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/websocket_realtime_driver/websocket_realtime_driver_dependency.json"
        self.json_spec = None
        self.verification_results = {
            "timestamp": datetime.now().isoformat(),
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "detailed_results": {},
            "compliance_score": 0.0
        }
    
    async def run_complete_verification(self):
        """運行完整驗證"""
        print("🔍 開始 JSON 規範匹配性驗證")
        print("=" * 80)
        
        # 載入 JSON 規範
        await self.load_json_specification()
        
        # 驗證架構設計
        await self.verify_architecture_design()
        
        # 驗證數據流
        await self.verify_realtime_data_flow()
        
        # 驗證性能要求
        await self.verify_performance_requirements()
        
        # 驗證技術架構
        await self.verify_technical_architecture()
        
        # 驗證集成接口
        await self.verify_integration_interfaces()
        
        # 生成最終報告
        self.generate_final_report()
    
    async def load_json_specification(self):
        """載入 JSON 規範"""
        try:
            with open(self.json_config_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                
            if "WEBSOCKET_REALTIME_DRIVER_DEPENDENCY" in json_data:
                self.json_spec = json_data["WEBSOCKET_REALTIME_DRIVER_DEPENDENCY"]
            else:
                self.json_spec = json_data
                
            print(f"✅ JSON 規範載入成功 (版本: {self.json_spec.get('version', 'unknown')})")
            
        except Exception as e:
            print(f"❌ JSON 規範載入失敗: {e}")
            raise
    
    async def verify_architecture_design(self):
        """驗證架構設計"""
        print("\n🏗️ 驗證架構設計")
        print("-" * 50)
        
        driver = websocket_realtime_driver
        arch_design = self.json_spec["🌐 architecture_design"]
        
        # 檢查連接架構
        connection_arch = arch_design["connection_architecture"]
        
        # 多交易所支持
        expected_exchanges = connection_arch["multi_exchange_support"]
        actual_exchanges = driver.active_exchanges
        
        self._check_feature("多交易所支持", 
                          set(expected_exchanges).issubset(set(actual_exchanges)),
                          f"期望: {expected_exchanges}, 實際: {actual_exchanges}")
        
        # 連接模式
        expected_mode = connection_arch["connection_mode"]
        has_async_websocket = hasattr(driver, 'connections') and isinstance(driver.connections, dict)
        self._check_feature("異步WebSocket連接池", 
                          has_async_websocket,
                          f"期望: {expected_mode}, 實際: {'有連接池' if has_async_websocket else '無連接池'}")
        
        # 故障容錯
        fault_tolerance = connection_arch["fault_tolerance"]
        has_auto_reconnect = hasattr(driver, '_auto_reconnection_mechanism')
        self._check_feature("自動重連機制", 
                          has_auto_reconnect,
                          f"期望: {fault_tolerance}, 實際: {'已實現' if has_auto_reconnect else '未實現'}")
        
        # 檢查數據管道
        data_pipeline = arch_design["data_pipeline"]
        
        # 接收緩衝區
        expected_buffer = data_pipeline["receive_buffer"]
        has_ring_buffer = hasattr(driver, 'market_data_buffer') and hasattr(driver.market_data_buffer, 'maxlen')
        self._check_feature("環形緩衝區", 
                          has_ring_buffer,
                          f"期望: {expected_buffer}, 實際: {'已實現' if has_ring_buffer else '未實現'}")
        
        # 處理隊列
        expected_queue = data_pipeline["processing_queue"]
        has_priority_queue = hasattr(driver, 'processing_queue')
        self._check_feature("優先級隊列", 
                          has_priority_queue,
                          f"期望: {expected_queue}, 實際: {'已實現' if has_priority_queue else '未實現'}")
        
        # 分發機制
        expected_distribution = data_pipeline["distribution_mechanism"]
        has_pub_sub = hasattr(driver, 'subscribers') and len(driver.subscribers) > 0
        self._check_feature("發布訂閱模式", 
                          has_pub_sub,
                          f"期望: {expected_distribution}, 實際: {'已實現' if has_pub_sub else '未實現'}")
    
    async def verify_realtime_data_flow(self):
        """驗證實時數據流"""
        print("\n⚡ 驗證實時數據流")
        print("-" * 50)
        
        driver = websocket_realtime_driver
        data_flow = self.json_spec["⚡ realtime_data_flow"]
        
        # Layer 0 驗證
        layer_0 = data_flow["Layer_0_connection_management"]
        has_layer_0 = hasattr(driver, '_layer_0_connection_management')
        target_time_0 = layer_0["time"]
        self._check_feature("Layer 0 連接管理", 
                          has_layer_0,
                          f"期望時間: {target_time_0}, 方法: {'已實現' if has_layer_0 else '未實現'}")
        
        # Layer 1 驗證
        layer_1 = data_flow["Layer_1_data_ingestion"]
        has_layer_1 = hasattr(driver, '_layer_1_data_ingestion')
        has_validation = hasattr(driver, '_data_validation')
        target_time_1 = layer_1["time"]
        self._check_feature("Layer 1 數據接收", 
                          has_layer_1 and has_validation,
                          f"期望時間: {target_time_1}, 數據驗證: {'已實現' if has_validation else '未實現'}")
        
        # 檢查數據驗證子方法
        validation_methods = ['_validate_ticker_data', '_validate_kline_data', '_validate_orderbook_data']
        all_validation_methods = all(hasattr(driver, method) for method in validation_methods)
        self._check_feature("數據驗證子方法", 
                          all_validation_methods,
                          f"驗證方法: {[method for method in validation_methods if hasattr(driver, method)]}")
        
        # Layer 2 驗證
        layer_2 = data_flow["Layer_2_data_processing"]
        has_layer_2 = hasattr(driver, '_layer_2_data_processing')
        has_cleaning = hasattr(driver, '_data_cleaning')
        has_standardization = hasattr(driver, '_standardization_processing')
        has_computation = hasattr(driver, '_basic_computation')
        target_time_2 = layer_2["time"]
        
        layer_2_complete = has_layer_2 and has_cleaning and has_standardization and has_computation
        self._check_feature("Layer 2 數據處理", 
                          layer_2_complete,
                          f"期望時間: {target_time_2}, 完整度: {'完整' if layer_2_complete else '不完整'}")
        
        # Layer 3 驗證
        layer_3 = data_flow["Layer_3_signal_distribution"]
        has_layer_3 = hasattr(driver, '_layer_3_signal_distribution')
        has_routing = hasattr(driver, '_intelligent_routing')
        has_pub_sub_method = hasattr(driver, '_publish_subscribe')
        has_monitoring = hasattr(driver, '_update_monitoring_statistics')
        target_time_3 = layer_3["time"]
        
        layer_3_complete = has_layer_3 and has_routing and has_pub_sub_method and has_monitoring
        self._check_feature("Layer 3 信號分發", 
                          layer_3_complete,
                          f"期望時間: {target_time_3}, 完整度: {'完整' if layer_3_complete else '不完整'}")
        
        # 檢查智能路由目標
        routing_rules = layer_3["operations"]["🎯 intelligent_routing"]["routing_rules"]
        expected_targets = list(routing_rules.keys())
        config_targets = driver.config.get("data_outputs", [])
        
        targets_match = set(expected_targets).issubset(set(config_targets))
        self._check_feature("智能路由目標", 
                          targets_match,
                          f"期望: {expected_targets}, 配置: {config_targets}")
    
    async def verify_performance_requirements(self):
        """驗證性能要求"""
        print("\n🎯 驗證性能要求")
        print("-" * 50)
        
        driver = websocket_realtime_driver
        perf_req = self.json_spec["🎯 performance_requirements_and_optimization"]
        
        # 延遲目標
        latency_targets = perf_req["latency_targets"]
        has_metrics = hasattr(driver, 'processing_metrics')
        has_monitoring = hasattr(driver, '_performance_monitoring')
        
        self._check_feature("延遲監控", 
                          has_metrics and has_monitoring,
                          f"內部處理目標: {latency_targets['internal_processing']}, 總延遲目標: {latency_targets['total_latency']}")
        
        # 吞吐量目標
        throughput_targets = perf_req["throughput_targets"]
        has_throughput_stats = 'data_throughput' in driver.performance_stats
        
        self._check_feature("吞吐量監控", 
                          has_throughput_stats,
                          f"消息處理目標: {throughput_targets['message_processing']}")
        
        # 可靠性目標
        reliability_targets = perf_req["reliability_targets"]
        has_health_monitor = hasattr(driver, '_connection_health_monitor')
        has_data_quality = 'data_quality' in driver.performance_stats
        
        self._check_feature("可靠性監控", 
                          has_health_monitor and has_data_quality,
                          f"連接穩定性目標: {reliability_targets['connection_stability']}")
    
    async def verify_technical_architecture(self):
        """驗證技術架構"""
        print("\n🔧 驗證技術架構")
        print("-" * 50)
        
        driver = websocket_realtime_driver
        tech_arch = self.json_spec["🔧 technical_architecture"]
        
        # 技術棧
        tech_stack = tech_arch["technology_stack"]
        
        # WebSocket 客戶端
        has_websockets = hasattr(driver, 'connections')
        self._check_feature("WebSocket 客戶端", 
                          has_websockets,
                          f"期望: {tech_stack['websocket_client']}")
        
        # 數據處理
        has_data_processing = hasattr(driver, 'data_validator') and hasattr(driver, 'standardizer')
        self._check_feature("數據處理組件", 
                          has_data_processing,
                          f"期望: {tech_stack['data_processing']}")
        
        # 消息隊列
        has_message_queue = hasattr(driver, 'processing_queue') and hasattr(driver, '_layer_2_queue')
        self._check_feature("消息隊列", 
                          has_message_queue,
                          f"期望: {tech_stack['message_queue']}")
    
    async def verify_integration_interfaces(self):
        """驗證集成接口"""
        print("\n🔗 驗證集成接口")
        print("-" * 50)
        
        driver = websocket_realtime_driver
        integration = self.json_spec["🔗 integration_interfaces"]
        
        # 提供的服務
        provided_services = integration["provided_services"]
        has_realtime_feed = hasattr(driver, 'market_data_buffer')
        has_event_notification = hasattr(driver, 'subscribers')
        has_health_status = hasattr(driver, '_connection_health_monitor')
        
        services_implemented = has_realtime_feed and has_event_notification and has_health_status
        self._check_feature("提供的服務", 
                          services_implemented,
                          f"期望服務: {len(provided_services)}, 實現: {'完整' if services_implemented else '部分'}")
        
        # 數據輸出
        data_outputs = integration["data_outputs"]
        config_outputs = driver.config.get("data_outputs", [])
        
        outputs_match = set(data_outputs) == set(config_outputs)
        self._check_feature("數據輸出目標", 
                          outputs_match,
                          f"期望: {data_outputs}, 配置: {config_outputs}")
    
    def _check_feature(self, feature_name: str, is_passed: bool, details: str):
        """檢查功能並記錄結果"""
        self.verification_results["total_checks"] += 1
        
        if is_passed:
            self.verification_results["passed_checks"] += 1
            status = "✅ 通過"
        else:
            self.verification_results["failed_checks"] += 1
            status = "❌ 失敗"
        
        self.verification_results["detailed_results"][feature_name] = {
            "status": "PASSED" if is_passed else "FAILED",
            "details": details
        }
        
        print(f"  {status} {feature_name}: {details}")
    
    def generate_final_report(self):
        """生成最終報告"""
        print("\n" + "=" * 80)
        print("📋 JSON 規範匹配性驗證報告")
        print("=" * 80)
        
        total = self.verification_results["total_checks"]
        passed = self.verification_results["passed_checks"]
        failed = self.verification_results["failed_checks"]
        
        if total > 0:
            compliance_score = (passed / total) * 100
            self.verification_results["compliance_score"] = compliance_score
        else:
            compliance_score = 0
        
        print(f"\n📊 驗證總結:")
        print(f"  總檢查項: {total}")
        print(f"  通過項目: {passed}")
        print(f"  失敗項目: {failed}")
        print(f"  合規分數: {compliance_score:.1f}%")
        
        # 合規性評級
        if compliance_score >= 95:
            grade = "🟢 優秀 (Excellent)"
            recommendation = "完全符合 JSON v1.0.0 規範，可以投入生產使用"
        elif compliance_score >= 85:
            grade = "🟡 良好 (Good)"
            recommendation = "基本符合 JSON 規範，建議修復少數問題"
        elif compliance_score >= 70:
            grade = "🟠 一般 (Fair)"
            recommendation = "部分符合 JSON 規範，需要重要改進"
        else:
            grade = "🔴 差 (Poor)"
            recommendation = "不符合 JSON 規範，需要重大修改"
        
        print(f"\n🎯 合規性評級: {grade}")
        print(f"📝 建議: {recommendation}")
        
        # 詳細失敗項目
        if failed > 0:
            print(f"\n❌ 需要修復的項目:")
            for feature, result in self.verification_results["detailed_results"].items():
                if result["status"] == "FAILED":
                    print(f"  • {feature}: {result['details']}")
        
        print(f"\n📅 驗證完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

async def main():
    """主函數"""
    try:
        verifier = JSONMatchingVerification()
        await verifier.run_complete_verification()
        
        # 自動刪除測試文件
        test_file = "/Users/henrychang/Desktop/Trading-X/json_matching_verification.py"
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\n🗑️ 測試文件已自動刪除: {test_file}")
        
    except Exception as e:
        print(f"❌ 驗證執行失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
