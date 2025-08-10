#!/usr/bin/env python3
"""
WebSocket Realtime Driver 精確深度分析工具
檢查 websocket_realtime_driver.py 與 JSON 規範的完全匹配情況
確保數據流與核心邏輯 100% 完整匹配
"""

import json
import re
import ast
import os
from typing import Dict, List, Any, Set, Tuple
from datetime import datetime
from pathlib import Path

class WebSocketRealtimeDriverPrecisionAnalyzer:
    """WebSocket Realtime Driver 精確深度分析器"""
    
    def __init__(self):
        self.python_file = "X/backend/phase1_signal_generation/websocket_realtime_driver/websocket_realtime_driver.py"
        self.json_spec = "X/backend/phase1_signal_generation/websocket_realtime_driver/websocket_realtime_driver_dependency_CORE_FLOW.json"
        
    def execute_precision_analysis(self) -> Dict[str, Any]:
        """執行精確深度分析"""
        print("🔍 WebSocket Realtime Driver 精確深度分析開始")
        print("=" * 80)
        
        try:
            # 讀取文件
            with open(self.python_file, 'r', encoding='utf-8') as f:
                python_code = f.read()
            
            with open(self.json_spec, 'r', encoding='utf-8') as f:
                json_spec = json.load(f)
            
            # 執行12個類別的深度分析
            analysis_results = {
                "timestamp": datetime.now().isoformat(),
                "precision_analysis": {
                    "1_websocket_architecture": self._analyze_websocket_architecture(python_code, json_spec),
                    "2_realtime_data_flow": self._analyze_realtime_data_flow(python_code, json_spec),
                    "3_connection_management": self._analyze_connection_management(python_code, json_spec),
                    "4_message_processing": self._analyze_message_processing(python_code, json_spec),
                    "5_error_handling": self._analyze_error_handling(python_code, json_spec),
                    "6_reconnection_logic": self._analyze_reconnection_logic(python_code, json_spec),
                    "7_performance_monitoring": self._analyze_performance_monitoring(python_code, json_spec),
                    "8_data_validation": self._analyze_data_validation(python_code, json_spec),
                    "9_event_broadcasting": self._analyze_event_broadcasting(python_code, json_spec),
                    "10_heartbeat_mechanism": self._analyze_heartbeat_mechanism(python_code, json_spec),
                    "11_buffer_management": self._analyze_buffer_management(python_code, json_spec),
                    "12_method_signatures": self._analyze_method_signatures(python_code, json_spec)
                }
            }
            
            # 計算總體匹配分數
            overall_score = self._calculate_overall_precision_score(analysis_results["precision_analysis"])
            analysis_results["overall_precision_score"] = overall_score
            
            self._print_detailed_analysis_results(analysis_results)
            
            return analysis_results
            
        except Exception as e:
            print(f"❌ 分析過程失敗: {e}")
            return {"error": str(e)}
    
    def _analyze_websocket_architecture(self, code: str, spec: Dict) -> Dict[str, Any]:
        """分析WebSocket架構完整性"""
        print("\n🌐 1. WebSocket架構分析...")
        
        # JSON規範要求的核心架構組件
        required_components = [
            "WebSocketRealtimeDriver",
            "ConnectionManager", 
            "MessageProcessor",
            "ReconnectionHandler",
            "DataBuffer",
            "EventBroadcaster",
            "PerformanceMonitor",
            "HeartbeatManager"
        ]
        
        found_components = []
        missing_components = []
        
        for component in required_components:
            pattern = rf"class\s+{component}|def\s+.*{component.lower()}"
            if re.search(pattern, code, re.IGNORECASE):
                found_components.append(component)
                print(f"  ✅ {component}")
            else:
                missing_components.append(component)
                print(f"  ❌ {component}")
        
        # 檢查WebSocket連接模式
        connection_modes = [
            "single_connection_mode",
            "multi_symbol_mode", 
            "failover_mode",
            "load_balancing_mode"
        ]
        
        modes_found = sum(1 for mode in connection_modes if mode in code)
        
        coverage = len(found_components) / len(required_components) * 100
        
        return {
            "required_components": required_components,
            "found_components": found_components,
            "missing_components": missing_components,
            "connection_modes_found": modes_found,
            "architecture_coverage": coverage,
            "status": "complete" if coverage >= 90 else "incomplete"
        }
    
    def _analyze_realtime_data_flow(self, code: str, spec: Dict) -> Dict[str, Any]:
        """分析實時數據流完整性"""
        print("\n⚡ 2. 實時數據流分析...")
        
        # JSON規範的數據流變數
        required_data_flows = [
            "websocket_connection",
            "incoming_message_stream",
            "parsed_market_data",
            "validated_data",
            "processed_ticker_data",
            "processed_kline_data", 
            "processed_depth_data",
            "processed_trade_data",
            "buffered_data_stream",
            "broadcast_events",
            "performance_metrics",
            "connection_status"
        ]
        
        found_flows = []
        missing_flows = []
        
        for flow in required_data_flows:
            patterns = [
                rf"\b{flow}\b\s*=",
                rf"[\"']{flow}[\"']",
                rf"\.{flow}\b",
                rf"\[\"?{flow}\"?\]"
            ]
            
            if any(re.search(pattern, code, re.IGNORECASE) for pattern in patterns):
                found_flows.append(flow)
                print(f"  ✅ {flow}")
            else:
                missing_flows.append(flow)
                print(f"  ❌ {flow}")
        
        coverage = len(found_flows) / len(required_data_flows) * 100
        
        return {
            "required_data_flows": required_data_flows,
            "found_flows": found_flows,
            "missing_flows": missing_flows,
            "data_flow_coverage": coverage,
            "status": "complete" if coverage >= 85 else "incomplete"
        }
    
    def _analyze_connection_management(self, code: str, spec: Dict) -> Dict[str, Any]:
        """分析連接管理邏輯"""
        print("\n🔗 3. 連接管理分析...")
        
        # 連接管理核心方法
        required_methods = [
            "establish_connection",
            "close_connection", 
            "validate_connection_health",
            "handle_connection_lost",
            "subscribe_to_streams",
            "unsubscribe_from_streams",
            "manage_subscription_list",
            "monitor_connection_quality"
        ]
        
        found_methods = []
        missing_methods = []
        
        for method in required_methods:
            pattern = rf"async def {method}|def {method}"
            if re.search(pattern, code):
                found_methods.append(method)
                print(f"  ✅ {method}")
            else:
                missing_methods.append(method)
                print(f"  ❌ {method}")
        
        # 檢查連接狀態管理
        connection_states = [
            "DISCONNECTED",
            "CONNECTING", 
            "CONNECTED",
            "RECONNECTING",
            "ERROR"
        ]
        
        states_found = sum(1 for state in connection_states if state in code)
        
        coverage = len(found_methods) / len(required_methods) * 100
        
        return {
            "required_methods": required_methods,
            "found_methods": found_methods,
            "missing_methods": missing_methods,
            "connection_states_found": states_found,
            "connection_coverage": coverage,
            "status": "complete" if coverage >= 90 else "incomplete"
        }
    
    def _analyze_message_processing(self, code: str, spec: Dict) -> Dict[str, Any]:
        """分析消息處理機制"""
        print("\n📨 4. 消息處理分析...")
        
        # 消息處理組件
        message_processors = [
            "process_ticker_message",
            "process_kline_message",
            "process_depth_message", 
            "process_trade_message",
            "validate_message_format",
            "parse_binary_message",
            "parse_json_message",
            "handle_error_message",
            "process_subscription_response"
        ]
        
        found_processors = []
        missing_processors = []
        
        for processor in message_processors:
            if processor in code:
                found_processors.append(processor)
                print(f"  ✅ {processor}")
            else:
                missing_processors.append(processor)
                print(f"  ❌ {processor}")
        
        # 消息類型處理
        message_types = [
            "24hrTicker",
            "kline",
            "depth",
            "trade", 
            "bookTicker",
            "error",
            "subscription_response"
        ]
        
        types_found = sum(1 for msg_type in message_types if msg_type in code)
        
        coverage = len(found_processors) / len(message_processors) * 100
        
        return {
            "message_processors": message_processors,
            "found_processors": found_processors,
            "missing_processors": missing_processors,
            "message_types_found": types_found,
            "processing_coverage": coverage,
            "status": "complete" if coverage >= 85 else "incomplete"
        }
    
    def _analyze_error_handling(self, code: str, spec: Dict) -> Dict[str, Any]:
        """分析錯誤處理機制"""
        print("\n🛡️ 5. 錯誤處理分析...")
        
        # 錯誤處理組件
        error_handlers = [
            "handle_websocket_error",
            "handle_connection_timeout",
            "handle_invalid_message",
            "handle_subscription_error", 
            "handle_rate_limit_error",
            "log_error_details",
            "trigger_error_recovery",
            "notify_error_listeners"
        ]
        
        found_handlers = []
        missing_handlers = []
        
        for handler in error_handlers:
            if handler in code:
                found_handlers.append(handler)
                print(f"  ✅ {handler}")
            else:
                missing_handlers.append(handler)
                print(f"  ❌ {handler}")
        
        # 錯誤類型檢查
        error_types = [
            "ConnectionError",
            "TimeoutError",
            "MessageParseError",
            "SubscriptionError",
            "RateLimitError"
        ]
        
        error_types_found = sum(1 for error in error_types if error in code)
        
        coverage = len(found_handlers) / len(error_handlers) * 100
        
        return {
            "error_handlers": error_handlers,
            "found_handlers": found_handlers,
            "missing_handlers": missing_handlers,
            "error_types_found": error_types_found,
            "error_coverage": coverage,
            "status": "complete" if coverage >= 85 else "incomplete"
        }
    
    def _analyze_reconnection_logic(self, code: str, spec: Dict) -> Dict[str, Any]:
        """分析重連邏輯"""
        print("\n🔄 6. 重連邏輯分析...")
        
        # 重連組件
        reconnection_components = [
            "initiate_reconnection",
            "exponential_backoff",
            "max_retry_attempts",
            "reconnection_delay",
            "restore_subscriptions", 
            "validate_reconnection_success",
            "handle_reconnection_failure",
            "reset_connection_state"
        ]
        
        found_reconnection = []
        missing_reconnection = []
        
        for component in reconnection_components:
            if component in code:
                found_reconnection.append(component)
                print(f"  ✅ {component}")
            else:
                missing_reconnection.append(component)
                print(f"  ❌ {component}")
        
        # 重連策略
        reconnection_strategies = [
            "immediate_retry",
            "exponential_backoff",
            "fixed_interval",
            "jittered_backoff"
        ]
        
        strategies_found = sum(1 for strategy in reconnection_strategies 
                              if strategy in code)
        
        coverage = len(found_reconnection) / len(reconnection_components) * 100
        
        return {
            "reconnection_components": reconnection_components,
            "found_reconnection": found_reconnection,
            "missing_reconnection": missing_reconnection,
            "strategies_found": strategies_found,
            "reconnection_coverage": coverage,
            "status": "complete" if coverage >= 85 else "incomplete"
        }
    
    def _analyze_performance_monitoring(self, code: str, spec: Dict) -> Dict[str, Any]:
        """分析性能監控實現"""
        print("\n📊 7. 性能監控分析...")
        
        # 性能監控組件
        performance_components = [
            "track_message_latency",
            "monitor_connection_uptime",
            "calculate_throughput_metrics",
            "measure_processing_time",
            "track_error_rates",
            "monitor_memory_usage",
            "log_performance_metrics",
            "generate_performance_report"
        ]
        
        found_performance = []
        missing_performance = []
        
        for component in performance_components:
            if component in code:
                found_performance.append(component)
                print(f"  ✅ {component}")
            else:
                missing_performance.append(component)
                print(f"  ❌ {component}")
        
        # 性能指標
        performance_metrics = [
            "message_count",
            "latency_ms",
            "throughput_msg_sec",
            "error_count",
            "uptime_percentage",
            "memory_usage_mb"
        ]
        
        metrics_found = sum(1 for metric in performance_metrics if metric in code)
        
        coverage = len(found_performance) / len(performance_components) * 100
        
        return {
            "performance_components": performance_components,
            "found_performance": found_performance,
            "missing_performance": missing_performance,
            "metrics_found": metrics_found,
            "performance_coverage": coverage,
            "status": "optimized" if coverage >= 80 else "needs_optimization"
        }
    
    def _analyze_data_validation(self, code: str, spec: Dict) -> Dict[str, Any]:
        """分析數據驗證實現"""
        print("\n✅ 8. 數據驗證分析...")
        
        # 數據驗證組件
        validation_components = [
            "validate_ticker_data",
            "validate_kline_data",
            "validate_depth_data",
            "validate_trade_data",
            "validate_timestamp_format",
            "validate_price_format",
            "validate_volume_format",
            "validate_symbol_format"
        ]
        
        found_validation = []
        missing_validation = []
        
        for component in validation_components:
            if component in code:
                found_validation.append(component)
                print(f"  ✅ {component}")
            else:
                missing_validation.append(component)
                print(f"  ❌ {component}")
        
        # 驗證規則
        validation_rules = [
            "price.*>.*0",
            "volume.*>=.*0",
            "timestamp.*is.*int",
            "symbol.*[A-Z]+USDT"
        ]
        
        rules_found = sum(1 for rule in validation_rules 
                         if re.search(rule, code, re.IGNORECASE))
        
        coverage = len(found_validation) / len(validation_components) * 100
        
        return {
            "validation_components": validation_components,
            "found_validation": found_validation,
            "missing_validation": missing_validation,
            "validation_rules_found": rules_found,
            "validation_coverage": coverage,
            "status": "complete" if coverage >= 85 else "incomplete"
        }
    
    def _analyze_event_broadcasting(self, code: str, spec: Dict) -> Dict[str, Any]:
        """分析事件廣播機制"""
        print("\n📡 9. 事件廣播分析...")
        
        # 事件廣播組件
        broadcast_components = [
            "EventBroadcaster",
            "register_listener",
            "unregister_listener",
            "broadcast_ticker_update",
            "broadcast_kline_update",
            "broadcast_depth_update",
            "broadcast_trade_update",
            "broadcast_connection_event",
            "broadcast_error_event"
        ]
        
        found_broadcast = []
        missing_broadcast = []
        
        for component in broadcast_components:
            if component in code:
                found_broadcast.append(component)
                print(f"  ✅ {component}")
            else:
                missing_broadcast.append(component)
                print(f"  ❌ {component}")
        
        # 事件類型
        event_types = [
            "ticker_update",
            "kline_update",
            "depth_update",
            "trade_update",
            "connection_established",
            "connection_lost",
            "error_occurred"
        ]
        
        events_found = sum(1 for event in event_types if event in code)
        
        coverage = len(found_broadcast) / len(broadcast_components) * 100
        
        return {
            "broadcast_components": broadcast_components,
            "found_broadcast": found_broadcast,
            "missing_broadcast": missing_broadcast,
            "event_types_found": events_found,
            "broadcast_coverage": coverage,
            "status": "complete" if coverage >= 85 else "incomplete"
        }
    
    def _analyze_heartbeat_mechanism(self, code: str, spec: Dict) -> Dict[str, Any]:
        """分析心跳機制"""
        print("\n💓 10. 心跳機制分析...")
        
        # 心跳組件
        heartbeat_components = [
            "HeartbeatManager",
            "send_ping",
            "handle_pong",
            "schedule_heartbeat",
            "monitor_heartbeat_response",
            "detect_connection_dead",
            "restart_heartbeat",
            "configure_heartbeat_interval"
        ]
        
        found_heartbeat = []
        missing_heartbeat = []
        
        for component in heartbeat_components:
            if component in code:
                found_heartbeat.append(component)
                print(f"  ✅ {component}")
            else:
                missing_heartbeat.append(component)
                print(f"  ❌ {component}")
        
        # 心跳配置
        heartbeat_config = [
            "heartbeat_interval",
            "ping_timeout",
            "max_missed_pongs",
            "heartbeat_enabled"
        ]
        
        config_found = sum(1 for config in heartbeat_config if config in code)
        
        coverage = len(found_heartbeat) / len(heartbeat_components) * 100
        
        return {
            "heartbeat_components": heartbeat_components,
            "found_heartbeat": found_heartbeat,
            "missing_heartbeat": missing_heartbeat,
            "config_found": config_found,
            "heartbeat_coverage": coverage,
            "status": "complete" if coverage >= 85 else "incomplete"
        }
    
    def _analyze_buffer_management(self, code: str, spec: Dict) -> Dict[str, Any]:
        """分析緩衝區管理"""
        print("\n🗄️ 11. 緩衝區管理分析...")
        
        # 緩衝區組件
        buffer_components = [
            "DataBuffer",
            "add_to_buffer",
            "get_from_buffer",
            "clear_buffer",
            "manage_buffer_size",
            "handle_buffer_overflow",
            "rotate_buffer_data",
            "monitor_buffer_usage"
        ]
        
        found_buffer = []
        missing_buffer = []
        
        for component in buffer_components:
            if component in code:
                found_buffer.append(component)
                print(f"  ✅ {component}")
            else:
                missing_buffer.append(component)
                print(f"  ❌ {component}")
        
        # 緩衝區配置
        buffer_config = [
            "buffer_size_limit",
            "buffer_overflow_strategy",
            "buffer_rotation_policy",
            "buffer_cleanup_interval"
        ]
        
        config_found = sum(1 for config in buffer_config if config in code)
        
        coverage = len(found_buffer) / len(buffer_components) * 100
        
        return {
            "buffer_components": buffer_components,
            "found_buffer": found_buffer,
            "missing_buffer": missing_buffer,
            "config_found": config_found,
            "buffer_coverage": coverage,
            "status": "complete" if coverage >= 85 else "incomplete"
        }
    
    def _analyze_method_signatures(self, code: str, spec: Dict) -> Dict[str, Any]:
        """分析方法簽名完整性"""
        print("\n📝 12. 方法簽名分析...")
        
        # 關鍵方法簽名
        required_signatures = [
            "async def start.*symbols.*List.*str",
            "async def stop.*cleanup.*bool.*True",
            "async def subscribe.*symbol.*str.*streams.*List",
            "async def unsubscribe.*symbol.*str.*streams.*List",
            "def register_listener.*event_type.*str.*callback",
            "def get_connection_status.*Dict.*str.*Any",
            "def get_performance_metrics.*Dict.*str.*Any",
            "async def handle_message.*message.*Dict.*Any"
        ]
        
        found_signatures = []
        missing_signatures = []
        
        for signature in required_signatures:
            if re.search(signature, code, re.DOTALL):
                found_signatures.append(signature.split(".*")[0] + "_" + signature.split(".*")[1])
                print(f"  ✅ {signature.split('.*')[0]}")
            else:
                missing_signatures.append(signature.split(".*")[0] + "_" + signature.split(".*")[1])
                print(f"  ❌ {signature.split('.*')[0]}")
        
        # 返回類型檢查
        return_types = [
            "Dict\\[str, Any\\]",
            "List\\[str\\]",
            "bool",
            "None",
            "Optional\\[.*\\]"
        ]
        
        types_found = sum(1 for rtype in return_types if re.search(rtype, code))
        
        coverage = len(found_signatures) / len(required_signatures) * 100
        
        return {
            "required_signatures": [s.split(".*")[0] for s in required_signatures],
            "found_signatures": [s.split("_")[0] for s in found_signatures],
            "missing_signatures": [s.split("_")[0] for s in missing_signatures],
            "return_types_found": types_found,
            "signature_coverage": coverage,
            "status": "complete" if coverage >= 90 else "incomplete"
        }
    
    def _calculate_overall_precision_score(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """計算總體精確匹配分數"""
        
        # 權重分配 (總和=1.0)
        weights = {
            "1_websocket_architecture": 0.12,
            "2_realtime_data_flow": 0.15,
            "3_connection_management": 0.12,
            "4_message_processing": 0.12,
            "5_error_handling": 0.10,
            "6_reconnection_logic": 0.10,
            "7_performance_monitoring": 0.08,
            "8_data_validation": 0.08,
            "9_event_broadcasting": 0.06,
            "10_heartbeat_mechanism": 0.04,
            "11_buffer_management": 0.02,
            "12_method_signatures": 0.01
        }
        
        scores = {}
        weighted_total = 0
        
        for category, weight in weights.items():
            if category in analysis:
                result = analysis[category]
                
                # 提取分數
                if "architecture_coverage" in result:
                    score = result["architecture_coverage"]
                elif "data_flow_coverage" in result:
                    score = result["data_flow_coverage"]
                elif "connection_coverage" in result:
                    score = result["connection_coverage"]
                elif "processing_coverage" in result:
                    score = result["processing_coverage"]
                elif "error_coverage" in result:
                    score = result["error_coverage"]
                elif "reconnection_coverage" in result:
                    score = result["reconnection_coverage"]
                elif "performance_coverage" in result:
                    score = result["performance_coverage"]
                elif "validation_coverage" in result:
                    score = result["validation_coverage"]
                elif "broadcast_coverage" in result:
                    score = result["broadcast_coverage"]
                elif "heartbeat_coverage" in result:
                    score = result["heartbeat_coverage"]
                elif "buffer_coverage" in result:
                    score = result["buffer_coverage"]
                elif "signature_coverage" in result:
                    score = result["signature_coverage"]
                else:
                    score = 50  # 默認分數
                
                scores[category] = score
                weighted_total += score * weight
        
        return {
            "category_scores": scores,
            "weighted_total_score": weighted_total,
            "precision_grade": self._get_precision_grade(weighted_total),
            "critical_gaps": self._identify_critical_gaps(analysis),
            "completion_status": "PERFECT_MATCH" if weighted_total >= 95 else "NEEDS_OPTIMIZATION"
        }
    
    def _get_precision_grade(self, score: float) -> str:
        """獲取精確度等級"""
        if score >= 95:
            return "🏆 完美匹配"
        elif score >= 90:
            return "🥇 優秀匹配"
        elif score >= 80:
            return "🥈 良好匹配"
        elif score >= 70:
            return "🥉 可接受匹配"
        else:
            return "❌ 需要大幅改進"
    
    def _identify_critical_gaps(self, analysis: Dict[str, Any]) -> List[str]:
        """識別關鍵缺口"""
        critical_gaps = []
        
        for category, result in analysis.items():
            if "missing_" in str(result):
                missing_items = (result.get("missing_components", []) + 
                               result.get("missing_flows", []) + 
                               result.get("missing_methods", []) +
                               result.get("missing_processors", []) +
                               result.get("missing_handlers", []) +
                               result.get("missing_reconnection", []) +
                               result.get("missing_performance", []) +
                               result.get("missing_validation", []) +
                               result.get("missing_broadcast", []) +
                               result.get("missing_heartbeat", []) +
                               result.get("missing_buffer", []) +
                               result.get("missing_signatures", []))
                
                if missing_items:
                    critical_gaps.append(f"{category}: {', '.join(missing_items[:3])}")
        
        return critical_gaps[:5]  # 返回最多5個關鍵缺口
    
    def _print_detailed_analysis_results(self, results: Dict):
        """列印詳細分析結果"""
        print("\n" + "=" * 80)
        print("📊 WEBSOCKET REALTIME DRIVER 精確深度分析結果")
        print("=" * 80)
        
        precision_score = results["overall_precision_score"]
        
        print(f"🎯 總體精確匹配分數: {precision_score['weighted_total_score']:.1f}/100")
        print(f"🏆 精確度等級: {precision_score['precision_grade']}")
        print(f"📋 完成狀態: {precision_score['completion_status']}")
        
        print(f"\n📊 詳細分類得分:")
        for category, score in precision_score["category_scores"].items():
            status = "✅" if score >= 90 else "⚠️" if score >= 70 else "❌"
            print(f"   {status} {category:35} {score:6.1f}%")
        
        if precision_score["critical_gaps"]:
            print(f"\n🔧 關鍵缺口:")
            for gap in precision_score["critical_gaps"]:
                print(f"   ❌ {gap}")
        
        # 具體分析結果
        analysis = results["precision_analysis"]
        
        print(f"\n📋 核心組件匹配情況:")
        
        # WebSocket架構
        arch_result = analysis["1_websocket_architecture"]
        print(f"   🌐 WebSocket架構: {len(arch_result['found_components'])}/{len(arch_result['required_components'])} ({arch_result['architecture_coverage']:.1f}%)")
        
        # 實時數據流
        flow_result = analysis["2_realtime_data_flow"] 
        print(f"   ⚡ 實時數據流: {len(flow_result['found_flows'])}/{len(flow_result['required_data_flows'])} ({flow_result['data_flow_coverage']:.1f}%)")
        
        # 連接管理
        conn_result = analysis["3_connection_management"]
        print(f"   🔗 連接管理: {len(conn_result['found_methods'])}/{len(conn_result['required_methods'])} ({conn_result['connection_coverage']:.1f}%)")
        
        # 消息處理
        msg_result = analysis["4_message_processing"]
        print(f"   📨 消息處理: {len(msg_result['found_processors'])}/{len(msg_result['message_processors'])} ({msg_result['processing_coverage']:.1f}%)")
        
        print(f"\n🎉 分析結論: {'🏆 完美匹配 - 可以進行生產部署' if precision_score['weighted_total_score'] >= 95 else '🔧 需要優化以達到完美匹配'}")

if __name__ == "__main__":
    analyzer = WebSocketRealtimeDriverPrecisionAnalyzer()
    results = analyzer.execute_precision_analysis()
