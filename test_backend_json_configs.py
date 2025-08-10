#!/usr/bin/env python3
"""
JSON配置數據流測試器 (X/backend版本)
測試WebSocket實時價格源、智能觸發引擎和自動回測驗證器的JSON配置
專為X/backend架構優化
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
import traceback

class BackendJSONConfigTester:
    def __init__(self):
        # 使用X/backend中的正確路徑
        self.config_files = {
            'websocket': '/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/websocket_realtime_driver/websocket_realtime_config.json',
            'trigger': '/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/intelligent_trigger_engine/intelligent_trigger_config.json', 
            'backtest': '/Users/henrychang/Desktop/Trading-X/X/backend/phase5_backtest_validation/auto_backtest_validator/auto_backtest_config.json'
        }
        self.test_results = {}
        
    def load_and_validate_json(self, config_name: str, file_path: str) -> bool:
        """載入並驗證JSON配置文件"""
        try:
            print(f"\n📋 測試配置: {config_name}")
            print(f"📁 文件路径: {file_path}")
            
            # 檢查文件存在
            if not Path(file_path).exists():
                print(f"❌ 文件不存在: {file_path}")
                return False
                
            # 載入JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            print(f"✅ JSON載入成功")
            
            # 驗證基本結構
            required_fields = ['version', 'config_name', 'description', 'last_updated']
            for field in required_fields:
                if field not in config:
                    print(f"❌ 缺少必要字段: {field}")
                    return False
                    
            print(f"✅ 基本結構驗證通過")
            print(f"📊 配置版本: {config['version']}")
            print(f"📝 配置名稱: {config['config_name']}")
            
            # 存儲配置用於數據流測試
            self.test_results[config_name] = {
                'config': config,
                'status': 'loaded',
                'file_path': file_path
            }
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析錯誤: {e}")
            return False
        except Exception as e:
            print(f"❌ 載入錯誤: {e}")
            traceback.print_exc()
            return False
    
    def test_websocket_config_flow(self) -> bool:
        """測試WebSocket配置數據流 - Phase1整合"""
        print(f"\n🔄 測試WebSocket配置數據流 (Phase1 Integration)...")
        
        try:
            config = self.test_results['websocket']['config']
            
            # 測試WebSocket驅動器配置
            websocket_driver = config['websocket_driver']
            print(f"📡 WebSocket驅動器類: {websocket_driver['class_name']}")
            
            # 測試與現有websocket_realtime_driver.py的兼容性
            binance_config = websocket_driver['binance_config']
            symbols = binance_config['symbols']
            print(f"💱 支援交易對: {', '.join(symbols)}")
            print(f"🔗 WebSocket URL: {binance_config['base_url']}")
            
            # 測試性能目標 (符合現有< 112ms需求)
            performance = websocket_driver['performance_targets']
            latency_target = performance['latency_ms']
            if latency_target <= 50:  # 比現有112ms更優
                print(f"✅ 延遲目標: {latency_target}ms (優於現有112ms)")
            else:
                print(f"⚠️ 延遲目標: {latency_target}ms (需要優化)")
            
            # 測試與Phase1 main_coordinator的整合
            integration = config['integration_points']
            phase1_integration = integration['phase1_main_coordinator']
            print(f"🎯 Phase1整合格式: {phase1_integration['data_format']}")
            print(f"🔄 觸發方法: {phase1_integration['trigger_method']}")
            
            # 測試與統一監控儀表板的整合
            dashboard_integration = integration['unified_monitoring_dashboard']
            print(f"📊 監控儀表板整合: {dashboard_integration['metrics_reporting']}")
            
            print(f"✅ WebSocket配置數據流測試通過")
            return True
            
        except Exception as e:
            print(f"❌ WebSocket配置數據流測試失敗: {e}")
            traceback.print_exc()
            return False
    
    def test_trigger_config_flow(self) -> bool:
        """測試智能觸發引擎配置數據流 - Phase1整合"""
        print(f"\n🎯 測試智能觸發引擎配置數據流 (Phase1 Integration)...")
        
        try:
            config = self.test_results['trigger']['config']
            
            # 測試觸發引擎配置
            trigger_engine = config['trigger_engine']
            print(f"🔧 觸發引擎類: {trigger_engine['class_name']}")
            print(f"⏱️ 掃描間隔: {trigger_engine['scan_interval_seconds']}秒")
            print(f"🔄 並行處理: {trigger_engine['parallel_processing']}")
            
            # 測試信號分類 (與勝率要求對齊)
            signal_classification = config['signal_classification']
            high_priority = signal_classification['high_priority']
            observation = signal_classification['observation']
            
            print(f"🔥 高優先級閾值: {high_priority['win_rate_threshold']*100}% (≥75%)")
            print(f"👀 觀察範圍: {observation['win_rate_range'][0]*100}%-{observation['win_rate_range'][1]*100}% (40%-75%)")
            
            # 驗證勝率分類邏輯
            if high_priority['win_rate_threshold'] >= 0.75:
                print(f"✅ 高勝率閾值符合要求 (≥75%)")
            else:
                print(f"❌ 高勝率閾值不符合要求 (<75%)")
                return False
            
            # 測試技術指標配置
            indicators = config['technical_indicators']
            total_weight = sum(indicators[ind]['weight'] for ind in indicators)
            print(f"📈 技術指標權重總和: {total_weight} (應為1.0)")
            
            if abs(total_weight - 1.0) < 0.01:
                print(f"✅ 技術指標權重配置正確")
            else:
                print(f"⚠️ 技術指標權重配置需要調整")
            
            # 測試與WebSocket數據源的整合
            data_sources = config['data_sources']
            realtime_source = data_sources['realtime_prices']
            if realtime_source == "WebSocketRealtimeDriver":
                print(f"✅ WebSocket數據源整合: {realtime_source}")
            else:
                print(f"❌ WebSocket數據源配置錯誤: {realtime_source}")
                return False
            
            # 測試輸出格式 (與unified_signal_candidate_pool_v3對齊)
            output_config = config['output_configuration']
            signal_format = output_config['signal_format']
            if signal_format == "unified_signal_candidate_pool_v3":
                print(f"✅ 信號格式對齊: {signal_format}")
            else:
                print(f"❌ 信號格式不匹配: {signal_format}")
                return False
            
            print(f"✅ 智能觸發引擎配置數據流測試通過")
            return True
            
        except Exception as e:
            print(f"❌ 智能觸發引擎配置數據流測試失敗: {e}")
            traceback.print_exc()
            return False
    
    def test_backtest_config_flow(self) -> bool:
        """測試自動回測驗證器配置數據流 - Phase5獨立"""
        print(f"\n📊 測試自動回測驗證器配置數據流 (Phase5 Independent)...")
        
        try:
            config = self.test_results['backtest']['config']
            
            # 測試回測驗證器配置
            validator = config['backtest_validator']
            print(f"🔍 驗證器類: {validator['class_name']}")
            print(f"⏰ 驗證窗口: {validator['validation_window_hours']}小時 (48小時需求)")
            
            # 驗證48小時窗口需求
            if validator['validation_window_hours'] == 48:
                print(f"✅ 驗證窗口符合48小時需求")
            else:
                print(f"⚠️ 驗證窗口與48小時需求不匹配")
            
            # 測試驗證方法論
            methodology = config['validation_methodology']
            performance_metrics = methodology['performance_metrics']
            
            # 檢查關鍵性能指標
            win_rate = performance_metrics['win_rate']
            profit_loss = performance_metrics['profit_loss_ratio']
            sharpe_ratio = performance_metrics['sharpe_ratio']
            max_drawdown = performance_metrics['maximum_drawdown']
            
            print(f"🎯 關鍵指標:")
            print(f"  - 勝率目標: {win_rate['target_threshold']*100}%")
            print(f"  - 盈虧比目標: {profit_loss['target_threshold']}")
            print(f"  - Sharpe比率目標: {sharpe_ratio['target_threshold']}")
            print(f"  - 最大回撤限制: {max_drawdown['target_threshold']*100}%")
            
            # 測試動態閾值調整
            dynamic_threshold = config['dynamic_threshold_system']
            adjustment_freq = dynamic_threshold['adjustment_frequency_hours']
            bounds = dynamic_threshold['threshold_bounds']
            
            print(f"⚙️ 動態調整:")
            print(f"  - 調整頻率: {adjustment_freq}小時")
            print(f"  - 勝率範圍: {bounds['win_rate_min']*100}%-{bounds['win_rate_max']*100}%")
            
            # 測試與智能觸發引擎的整合
            integration = config['integration_points']
            trigger_integration = integration['intelligent_trigger_engine']
            dashboard_integration = integration['unified_monitoring_dashboard']
            
            print(f"🔗 整合測試:")
            print(f"  - 觸發引擎反饋: {trigger_integration['feedback_mechanism']}")
            print(f"  - 儀表板整合: {dashboard_integration['validation_metrics']}")
            
            # 測試機器學習整合
            ml_integration = config['machine_learning_integration']
            if ml_integration['predictive_modeling']['enabled']:
                model_type = ml_integration['predictive_modeling']['model_type']
                print(f"🤖 機器學習: {model_type} (已啟用)")
            else:
                print(f"🤖 機器學習: 已停用")
            
            print(f"✅ 自動回測驗證器配置數據流測試通過")
            return True
            
        except Exception as e:
            print(f"❌ 自動回測驗證器配置數據流測試失敗: {e}")
            traceback.print_exc()
            return False
    
    def test_phase_integration_flow(self) -> bool:
        """測試跨Phase整合流程"""
        print(f"\n🔗 測試跨Phase整合流程...")
        
        try:
            websocket_config = self.test_results['websocket']['config']
            trigger_config = self.test_results['trigger']['config']
            backtest_config = self.test_results['backtest']['config']
            
            print(f"📋 Phase架構驗證:")
            print(f"  - Phase1: WebSocket實時價格源 + 智能觸發引擎")
            print(f"  - Phase5: 自動回測驗證器")
            
            # 測試數據流向
            print(f"\n🔄 數據流向測試:")
            
            # 1. WebSocket → Trigger Engine 數據流
            websocket_output = websocket_config['data_flow']['output_destinations']['phase1_coordinator']
            trigger_input_format = trigger_config['output_configuration']['signal_format']
            
            if websocket_output == trigger_input_format:
                print(f"✅ Phase1 內部數據流: WebSocket → Trigger Engine")
                print(f"   格式: {websocket_output}")
            else:
                print(f"❌ Phase1 內部數據流格式不匹配")
                return False
            
            # 2. Trigger Engine → Backtest Validator 整合
            trigger_monitoring = trigger_config['monitoring_integration']
            backtest_integration = backtest_config['integration_points']['intelligent_trigger_engine']
            
            print(f"✅ Phase1 → Phase5 整合:")
            print(f"   觸發引擎監控: {trigger_monitoring['unified_dashboard_metrics']}")
            print(f"   回測整合方式: {backtest_integration['feedback_mechanism']}")
            
            # 3. 統一監控儀表板整合
            websocket_dashboard = websocket_config['integration_points']['unified_monitoring_dashboard']
            trigger_dashboard = trigger_config['monitoring_integration']['unified_dashboard_metrics']
            backtest_dashboard = backtest_config['integration_points']['unified_monitoring_dashboard']
            
            print(f"✅ 統一監控儀表板整合:")
            print(f"   WebSocket監控: {websocket_dashboard['metrics_reporting']}")
            print(f"   觸發引擎監控: {list(trigger_dashboard.keys())}")
            print(f"   回測監控: {backtest_dashboard['validation_metrics']}")
            
            # 4. 性能目標一致性
            websocket_latency = websocket_config['websocket_driver']['performance_targets']['latency_ms']
            trigger_latency = trigger_config['monitoring_integration']['alerting']['latency_threshold_ms']
            
            print(f"\n⚡ 性能目標一致性:")
            print(f"   WebSocket延遲目標: {websocket_latency}ms")
            print(f"   觸發引擎延遲閾值: {trigger_latency}ms")
            
            if websocket_latency <= trigger_latency:
                print(f"✅ 性能目標一致且合理")
            else:
                print(f"⚠️ 性能目標需要重新評估")
            
            print(f"✅ 跨Phase整合流程測試通過")
            return True
            
        except Exception as e:
            print(f"❌ 跨Phase整合流程測試失敗: {e}")
            traceback.print_exc()
            return False
    
    def run_all_tests(self) -> bool:
        """執行所有測試"""
        print("🚀 開始X/backend JSON配置數據流完整測試...")
        print("=" * 80)
        
        all_passed = True
        
        # 1. 載入所有JSON配置
        for config_name, file_path in self.config_files.items():
            if not self.load_and_validate_json(config_name, file_path):
                all_passed = False
        
        if not all_passed:
            print(f"\n❌ JSON載入階段失敗，停止測試")
            return False
        
        # 2. 測試各配置數據流
        test_methods = [
            self.test_websocket_config_flow,
            self.test_trigger_config_flow,
            self.test_backtest_config_flow,
            self.test_phase_integration_flow
        ]
        
        for test_method in test_methods:
            if not test_method():
                all_passed = False
        
        # 3. 總結測試結果
        print("\n" + "=" * 80)
        if all_passed:
            print("🎉 所有X/backend JSON配置數據流測試通過！")
            print("✅ Phase1 - WebSocket實時價格源配置 - 正常")
            print("✅ Phase1 - 智能觸發引擎配置 - 正常") 
            print("✅ Phase5 - 自動回測驗證器配置 - 正常")
            print("✅ 跨Phase整合流程 - 正常")
            print("\n📁 配置檔案位置:")
            for config_name, file_path in self.config_files.items():
                print(f"   {config_name}: {file_path}")
            print("\n🚀 準備進行Python實現階段...")
        else:
            print("❌ X/backend JSON配置數據流測試失敗")
            print("🔧 請修正配置錯誤後重新測試")
        
        return all_passed

def main():
    """主函數"""
    tester = BackendJSONConfigTester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n📋 測試完成 - 可以刪除此測試文件並進行下一步")
        sys.exit(0)
    else:
        print(f"\n❌ 測試失敗 - 需要修正配置")
        sys.exit(1)

if __name__ == "__main__":
    main()
