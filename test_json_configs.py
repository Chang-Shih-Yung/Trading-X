#!/usr/bin/env python3
"""
JSON配置數據流測試器
測試WebSocket實時價格源、智能觸發引擎和自動回測驗證器的JSON配置
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
import traceback

class JSONConfigTester:
    def __init__(self):
        self.config_files = {
            'websocket': '/Users/henrychang/Desktop/Trading-X/websocket_realtime_config.json',
            'trigger': '/Users/henrychang/Desktop/Trading-X/intelligent_trigger_config.json', 
            'backtest': '/Users/henrychang/Desktop/Trading-X/auto_backtest_config.json'
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
        """測試WebSocket配置數據流"""
        print(f"\n🔄 測試WebSocket配置數據流...")
        
        try:
            config = self.test_results['websocket']['config']
            
            # 測試WebSocket驅動器配置
            websocket_driver = config['websocket_driver']
            print(f"📡 WebSocket驅動器類: {websocket_driver['class_name']}")
            
            # 測試Binance配置
            binance_config = websocket_driver['binance_config']
            symbols = binance_config['symbols']
            print(f"💱 支援交易對: {', '.join(symbols)}")
            print(f"🔗 WebSocket URL: {binance_config['base_url']}")
            
            # 測試性能目標
            performance = websocket_driver['performance_targets']
            print(f"⚡ 延遲目標: {performance['latency_ms']}ms")
            print(f"📊 吞吐量目標: {performance['throughput_per_second']}/秒")
            
            # 測試數據流配置
            data_flow = config['data_flow']
            pipeline = data_flow['processing_pipeline']
            print(f"🔄 處理管道: {' → '.join(pipeline)}")
            
            # 測試整合點
            integration = config['integration_points']
            phase1_integration = integration['phase1_main_coordinator']
            print(f"🎯 Phase1整合: {phase1_integration['data_format']}")
            
            print(f"✅ WebSocket配置數據流測試通過")
            return True
            
        except Exception as e:
            print(f"❌ WebSocket配置數據流測試失敗: {e}")
            return False
    
    def test_trigger_config_flow(self) -> bool:
        """測試智能觸發引擎配置數據流"""
        print(f"\n🎯 測試智能觸發引擎配置數據流...")
        
        try:
            config = self.test_results['trigger']['config']
            
            # 測試觸發引擎配置
            trigger_engine = config['trigger_engine']
            print(f"🔧 觸發引擎類: {trigger_engine['class_name']}")
            print(f"⏱️ 掃描間隔: {trigger_engine['scan_interval_seconds']}秒")
            
            # 測試信號分類
            signal_classification = config['signal_classification']
            high_priority = signal_classification['high_priority']
            print(f"🔥 高優先級閾值: {high_priority['win_rate_threshold']*100}%")
            print(f"👀 觀察範圍: {signal_classification['observation']['win_rate_range']}")
            
            # 測試技術指標
            indicators = config['technical_indicators']
            print(f"📈 技術指標權重:")
            for indicator, settings in indicators.items():
                print(f"  - {indicator}: {settings['weight']*100}%")
            
            # 測試觸發條件
            trigger_conditions = config['trigger_conditions']
            price_momentum = trigger_conditions['price_momentum']
            print(f"💨 價格動量閾值:")
            print(f"  - 1分鐘: {price_momentum['1min_threshold']*100}%")
            print(f"  - 5分鐘: {price_momentum['5min_threshold']*100}%")
            
            # 測試勝率計算
            win_rate_calc = config['win_rate_calculation']
            print(f"🏆 勝率計算:")
            print(f"  - 歷史窗口: {win_rate_calc['historical_window_days']}天")
            print(f"  - 最小樣本: {win_rate_calc['minimum_sample_size']}個")
            
            print(f"✅ 智能觸發引擎配置數據流測試通過")
            return True
            
        except Exception as e:
            print(f"❌ 智能觸發引擎配置數據流測試失敗: {e}")
            return False
    
    def test_backtest_config_flow(self) -> bool:
        """測試自動回測驗證器配置數據流"""
        print(f"\n📊 測試自動回測驗證器配置數據流...")
        
        try:
            config = self.test_results['backtest']['config']
            
            # 測試回測驗證器配置
            validator = config['backtest_validator']
            print(f"🔍 驗證器類: {validator['class_name']}")
            print(f"⏰ 驗證窗口: {validator['validation_window_hours']}小時")
            
            # 測試驗證方法論
            methodology = config['validation_methodology']
            performance_metrics = methodology['performance_metrics']
            win_rate = performance_metrics['win_rate']
            print(f"🎯 勝率目標: {win_rate['target_threshold']*100}%")
            print(f"📊 最小樣本: {win_rate['minimum_sample_size']}個")
            
            # 測試動態閾值系統
            dynamic_threshold = config['dynamic_threshold_system']
            adjustment_freq = dynamic_threshold['adjustment_frequency_hours']
            print(f"⚙️ 閾值調整頻率: {adjustment_freq}小時")
            
            bounds = dynamic_threshold['threshold_bounds']
            print(f"📏 閾值範圍:")
            print(f"  - 勝率: {bounds['win_rate_min']*100}% - {bounds['win_rate_max']*100}%")
            print(f"  - 盈虧比: {bounds['profit_loss_min']} - {bounds['profit_loss_max']}")
            
            # 測試信號分類
            signal_categorization = config['signal_categorization']
            excellent = signal_categorization['excellent_signals']
            print(f"⭐ 優秀信號標準:")
            print(f"  - 勝率: ≥{excellent['win_rate_threshold']*100}%")
            print(f"  - 盈虧比: ≥{excellent['profit_loss_threshold']}")
            
            # 測試整合點
            integration = config['integration_points']
            trigger_integration = integration['intelligent_trigger_engine']
            print(f"🔗 與觸發引擎整合: {trigger_integration['feedback_mechanism']}")
            
            print(f"✅ 自動回測驗證器配置數據流測試通過")
            return True
            
        except Exception as e:
            print(f"❌ 自動回測驗證器配置數據流測試失敗: {e}")
            return False
    
    def test_cross_config_integration(self) -> bool:
        """測試跨配置整合"""
        print(f"\n🔗 測試跨配置整合...")
        
        try:
            websocket_config = self.test_results['websocket']['config']
            trigger_config = self.test_results['trigger']['config']
            backtest_config = self.test_results['backtest']['config']
            
            # 測試類名一致性
            websocket_class = websocket_config['websocket_driver']['class_name']
            trigger_class = trigger_config['trigger_engine']['class_name']
            backtest_class = backtest_config['backtest_validator']['class_name']
            
            print(f"🏗️ 類名檢查:")
            print(f"  - WebSocket驅動器: {websocket_class}")
            print(f"  - 智能觸發引擎: {trigger_class}")
            print(f"  - 自動回測驗證器: {backtest_class}")
            
            # 測試數據格式一致性
            websocket_output = websocket_config['data_flow']['output_destinations']['phase1_coordinator']
            trigger_output = trigger_config['output_configuration']['signal_format']
            
            if websocket_output == trigger_output:
                print(f"✅ 數據格式一致: {websocket_output}")
            else:
                print(f"❌ 數據格式不一致: {websocket_output} vs {trigger_output}")
                return False
            
            # 測試觸發條件一致性
            websocket_triggers = websocket_config['intelligent_trigger']['trigger_conditions']
            trigger_conditions = trigger_config['trigger_conditions']
            
            print(f"🎯 觸發條件檢查:")
            for condition in ['price_change_1min', 'rsi_extremes', 'volume_spike']:
                if condition.replace('_change_', '_momentum').replace('change', 'momentum') in str(trigger_conditions):
                    print(f"  ✅ {condition}: 配置一致")
                else:
                    print(f"  ℹ️ {condition}: 需要映射檢查")
            
            # 測試整合點
            print(f"🔄 整合點檢查:")
            integration_points = [
                ('WebSocket → Trigger', websocket_config['integration_points']['phase1_main_coordinator']),
                ('Trigger → Backtest', trigger_config['monitoring_integration']),
                ('Backtest → Dashboard', backtest_config['integration_points']['unified_monitoring_dashboard'])
            ]
            
            for name, config_section in integration_points:
                print(f"  ✅ {name}: 配置完整")
            
            print(f"✅ 跨配置整合測試通過")
            return True
            
        except Exception as e:
            print(f"❌ 跨配置整合測試失敗: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """執行所有測試"""
        print("🚀 開始JSON配置數據流完整測試...")
        print("=" * 60)
        
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
            self.test_cross_config_integration
        ]
        
        for test_method in test_methods:
            if not test_method():
                all_passed = False
        
        # 3. 總結測試結果
        print("\n" + "=" * 60)
        if all_passed:
            print("🎉 所有JSON配置數據流測試通過！")
            print("✅ WebSocket實時價格源配置 - 正常")
            print("✅ 智能觸發引擎配置 - 正常") 
            print("✅ 自動回測驗證器配置 - 正常")
            print("✅ 跨配置整合 - 正常")
            print("\n🚀 準備進行Python實現階段...")
        else:
            print("❌ JSON配置數據流測試失敗")
            print("🔧 請修正配置錯誤後重新測試")
        
        return all_passed

def main():
    """主函數"""
    tester = JSONConfigTester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n📋 測試完成 - 可以刪除此測試文件並進行下一步")
        sys.exit(0)
    else:
        print(f"\n❌ 測試失敗 - 需要修正配置")
        sys.exit(1)

if __name__ == "__main__":
    main()
