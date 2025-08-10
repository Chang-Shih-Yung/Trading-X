#!/usr/bin/env python3
"""
Component 5 數據流集成測試
檢查與其他組件的數據格式一致性和集成完整性
"""

import json
import sys
from pathlib import Path

def load_config(config_path):
    """載入配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"載入配置失敗 {config_path}: {e}")
        return None

def test_data_format_consistency():
    """測試數據格式一致性"""
    print("🔍 測試數據格式一致性...")
    
    # 載入所有組件配置
    base_path = Path("/Users/henrychang/Desktop/Trading-X/X/backend/phase4_output_monitoring")
    
    configs = {
        'component1': load_config(base_path / "1_unified_monitoring_dashboard/unified_monitoring_dashboard_config.json"),
        'component2': load_config(base_path / "2_signal_processing_statistics/signal_processing_statistics_config.json"),
        'component3': load_config(base_path / "3_epl_decision_history_tracking/epl_decision_history_tracking_config.json"),
        'component4': load_config(base_path / "4_notification_success_rate_monitoring/notification_success_rate_monitoring_config.json"),
        'component5_original': load_config(base_path / "5_system_performance_metrics_monitoring/system_performance_metrics_monitoring_config.json"),
        'component5_corrected': load_config(base_path / "5_system_performance_metrics_monitoring/system_performance_metrics_monitoring_config_corrected.json")
    }
    
    # 檢查關鍵數據格式標準
    standard_formats = {
        'signal_strength_range': '0.0-1.0',
        'confidence_range': '0.0-1.0',
        'priority_levels': ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
        'timestamp_format': 'ISO_8601_UTC'
    }
    
    print("\n📊 數據格式標準檢查:")
    consistency_issues = []
    
    for component_name, config in configs.items():
        if not config:
            print(f"❌ {component_name}: 配置文件無法載入")
            continue
        
        # 檢查Component 1的標準格式
        if component_name == 'component1':
            integration_standards = config.get('PHASE4_UNIFIED_MONITORING_DASHBOARD', {}).get('integration_standards', {}).get('data_format_consistency', {})
            for key, expected_value in standard_formats.items():
                actual_value = integration_standards.get(key)
                if actual_value == expected_value:
                    print(f"✅ {component_name} - {key}: {actual_value}")
                else:
                    print(f"❌ {component_name} - {key}: 期望 {expected_value}, 實際 {actual_value}")
                    consistency_issues.append(f"{component_name}-{key}")
        
        # 檢查Component 5修正版本是否包含數據格式標準
        if component_name == 'component5_corrected':
            data_format = config.get('PHASE4_SYSTEM_PERFORMANCE_METRICS_MONITORING', {}).get('data_format_consistency', {})
            for key, expected_value in standard_formats.items():
                actual_value = data_format.get(key)
                if actual_value == expected_value:
                    print(f"✅ {component_name} - {key}: {actual_value}")
                else:
                    print(f"❌ {component_name} - {key}: 期望 {expected_value}, 實際 {actual_value}")
                    consistency_issues.append(f"{component_name}-{key}")
    
    return len(consistency_issues) == 0

def test_cross_component_integration():
    """測試跨組件集成"""
    print("\n🔗 測試跨組件集成...")
    
    base_path = Path("/Users/henrychang/Desktop/Trading-X/X/backend/phase4_output_monitoring")
    component5_config = load_config(base_path / "5_system_performance_metrics_monitoring/system_performance_metrics_monitoring_config_corrected.json")
    
    if not component5_config:
        print("❌ Component 5 配置文件載入失敗")
        return False
    
    component5_data = component5_config.get('PHASE4_SYSTEM_PERFORMANCE_METRICS_MONITORING', {})
    
    # 檢查跨組件集成監控
    cross_component = component5_data.get('cross_component_integration_monitoring', {})
    required_integrations = [
        'component1_dashboard_integration',
        'component2_statistics_correlation', 
        'component3_decision_performance_tracking',
        'component4_notification_performance'
    ]
    
    integration_complete = True
    for integration in required_integrations:
        if integration in cross_component.get('component_interaction_performance', {}):
            print(f"✅ 跨組件集成: {integration}")
        else:
            print(f"❌ 缺少跨組件集成: {integration}")
            integration_complete = False
    
    # 檢查CPU負載分佈是否包含所有組件
    cpu_distribution = component5_data.get('infrastructure_performance_monitoring', {}).get('server_resource_monitoring', {}).get('cpu_performance_tracking', {}).get('cpu_load_distribution', {})
    
    required_cpu_tracking = [
        'phase1_cpu_usage', 'phase2_cpu_usage', 'phase3_cpu_usage', 'phase4_cpu_usage',
        'component1_dashboard_cpu', 'component2_statistics_cpu', 'component3_epl_tracking_cpu', 'component4_notification_cpu'
    ]
    
    for cpu_metric in required_cpu_tracking:
        if cpu_metric in cpu_distribution:
            print(f"✅ CPU追蹤: {cpu_metric}")
        else:
            print(f"❌ 缺少CPU追蹤: {cpu_metric}")
            integration_complete = False
    
    return integration_complete

def test_api_integration():
    """測試API集成"""
    print("\n🔌 測試API集成...")
    
    base_path = Path("/Users/henrychang/Desktop/Trading-X/X/backend/phase4_output_monitoring")
    component5_config = load_config(base_path / "5_system_performance_metrics_monitoring/system_performance_metrics_monitoring_config_corrected.json")
    
    if not component5_config:
        return False
    
    integration_apis = component5_config.get('PHASE4_SYSTEM_PERFORMANCE_METRICS_MONITORING', {}).get('integration_apis', {})
    
    # 檢查是否有跨組件API集成
    performance_api = integration_apis.get('performance_monitoring_api', {})
    integration_endpoints = performance_api.get('integration_endpoints', {})
    
    required_endpoints = [
        'dashboard_integration',
        'statistics_correlation',
        'decision_performance',
        'notification_performance'
    ]
    
    api_complete = True
    for endpoint in required_endpoints:
        if endpoint in integration_endpoints:
            print(f"✅ API端點: {endpoint} -> {integration_endpoints[endpoint]}")
        else:
            print(f"❌ 缺少API端點: {endpoint}")
            api_complete = False
    
    # 檢查跨組件API
    if 'cross_component_integration_api' in integration_apis:
        print("✅ 跨組件集成API: 已配置")
    else:
        print("❌ 缺少跨組件集成API")
        api_complete = False
    
    return api_complete

def test_performance_monitoring_coverage():
    """測試性能監控覆蓋度"""
    print("\n📈 測試性能監控覆蓋度...")
    
    base_path = Path("/Users/henrychang/Desktop/Trading-X/X/backend/phase4_output_monitoring")
    component5_config = load_config(base_path / "5_system_performance_metrics_monitoring/system_performance_metrics_monitoring_config_corrected.json")
    
    if not component5_config:
        return False
    
    component5_data = component5_config.get('PHASE4_SYSTEM_PERFORMANCE_METRICS_MONITORING', {})
    
    # 檢查Phase 4特定性能監控
    phase4_performance = component5_data.get('infrastructure_performance_monitoring', {}).get('application_performance_monitoring', {}).get('phase_specific_performance', {}).get('phase4_monitoring_performance', {})
    
    required_phase4_metrics = [
        'dashboard_data_aggregation_time',
        'notification_preparation_time',
        'statistics_computation_time',
        'performance_analysis_time'
    ]
    
    coverage_complete = True
    for metric in required_phase4_metrics:
        if metric in phase4_performance:
            print(f"✅ Phase4 性能指標: {metric}")
        else:
            print(f"❌ 缺少Phase4 性能指標: {metric}")
            coverage_complete = False
    
    # 檢查警報系統集成
    cross_component_alerts = component5_data.get('reporting_and_alerting', {}).get('automated_alerting', {}).get('cross_component_alerts', {})
    
    required_alerts = [
        'dashboard_performance_alerts',
        'statistics_computation_alerts',
        'decision_tracking_alerts',
        'notification_delivery_alerts'
    ]
    
    for alert in required_alerts:
        if alert in cross_component_alerts:
            print(f"✅ 跨組件警報: {alert}")
        else:
            print(f"❌ 缺少跨組件警報: {alert}")
            coverage_complete = False
    
    return coverage_complete

def main():
    """主測試函數"""
    print("🚀 開始 Component 5 數據流集成測試")
    print("=" * 60)
    
    tests = [
        ("數據格式一致性", test_data_format_consistency),
        ("跨組件集成", test_cross_component_integration),
        ("API集成", test_api_integration),
        ("性能監控覆蓋度", test_performance_monitoring_coverage)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 執行測試: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ 通過" if result else "❌ 失敗"
            print(f"📊 測試結果: {status}")
        except Exception as e:
            print(f"❌ 測試執行錯誤: {e}")
            results.append((test_name, False))
    
    # 總結報告
    print("\n" + "=" * 60)
    print("📋 測試總結報告")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{status} {test_name}")
    
    print(f"\n📊 總體測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！Component 5 數據流集成完整")
        return True
    else:
        print("⚠️ 部分測試失敗，需要修正配置")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
