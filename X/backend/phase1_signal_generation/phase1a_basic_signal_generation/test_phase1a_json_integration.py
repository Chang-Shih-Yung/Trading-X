#!/usr/bin/env python3
"""
Phase1A JSON Configuration Integration Test
測試 phase1a_basic_signal_generation.json 的動態參數整合
確保與前後Phase數據流無衝突或缺失
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

class Phase1AJsonIntegrationTester:
    """Phase1A JSON 配置整合測試器"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.dynamic_system_path = self.base_path.parent / "dynamic_parameter_system"
        self.test_results = []
        
    def load_phase1a_config(self) -> Dict[str, Any]:
        """載入 Phase1A 配置"""
        config_path = self.base_path / "phase1a_basic_signal_generation.json"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.test_results.append(f"❌ Phase1A 配置載入失敗: {e}")
            return {}
            
    def load_dynamic_parameter_config(self) -> Dict[str, Any]:
        """載入動態參數系統配置"""
        config_path = self.dynamic_system_path / "dynamic_parameter_config.json"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.test_results.append(f"❌ 動態參數配置載入失敗: {e}")
            return {}
    
    def test_json_syntax_validity(self, config: Dict[str, Any]) -> bool:
        """測試 JSON 語法有效性"""
        try:
            # 重新序列化測試
            json.dumps(config, indent=2)
            self.test_results.append("✅ JSON 語法有效性: 通過")
            return True
        except Exception as e:
            self.test_results.append(f"❌ JSON 語法錯誤: {e}")
            return False
    
    def test_confidence_threshold_structure(self, config: Dict[str, Any]) -> bool:
        """測試 confidence_threshold 結構完整性"""
        success = True
        
        # 檢查基礎模式
        try:
            basic_mode = config["phase1a_basic_signal_generation_dependency"]["configuration"]["signal_generation_params"]["basic_mode"]
            confidence_threshold = basic_mode["confidence_threshold"]
            
            required_fields = ["type", "base_value", "parameter_id", "adaptation_source", "market_regime_dependent"]
            for field in required_fields:
                if field not in confidence_threshold:
                    self.test_results.append(f"❌ 基礎模式缺少必要欄位: {field}")
                    success = False
                    
            # 檢查數值合理性
            base_value = confidence_threshold.get("base_value", 0)
            if not isinstance(base_value, (int, float)) or not 0 <= base_value <= 1:
                self.test_results.append(f"❌ 基礎模式 base_value 值不合理: {base_value}")
                success = False
                
        except KeyError as e:
            self.test_results.append(f"❌ 基礎模式配置結構錯誤: {e}")
            success = False
            
        # 檢查極端市場模式
        try:
            extreme_mode = config["phase1a_basic_signal_generation_dependency"]["configuration"]["signal_generation_params"]["extreme_market_mode"]
            confidence_threshold = extreme_mode["confidence_threshold"]
            
            required_fields = ["type", "base_value", "parameter_id", "adaptation_source", "market_regime_dependent"]
            for field in required_fields:
                if field not in confidence_threshold:
                    self.test_results.append(f"❌ 極端模式缺少必要欄位: {field}")
                    success = False
                    
            # 檢查極端模式特有欄位
            if "extreme_mode_multiplier" not in confidence_threshold:
                self.test_results.append("❌ 極端模式缺少 extreme_mode_multiplier")
                success = False
                
        except KeyError as e:
            self.test_results.append(f"❌ 極端模式配置結構錯誤: {e}")
            success = False
            
        if success:
            self.test_results.append("✅ confidence_threshold 結構完整性: 通過")
            
        return success
    
    def test_dynamic_parameter_integration(self, config: Dict[str, Any]) -> bool:
        """測試動態參數系統整合配置"""
        success = True
        
        try:
            integration_config = config["phase1a_basic_signal_generation_dependency"]["configuration"]["dynamic_parameter_integration"]
            
            # 檢查必要配置
            required_fields = [
                "enabled", "parameter_system_path", "config_file", 
                "update_frequency", "supported_parameters"
            ]
            for field in required_fields:
                if field not in integration_config:
                    self.test_results.append(f"❌ 動態參數整合缺少必要配置: {field}")
                    success = False
                    
            # 檢查支援的參數列表
            supported_params = integration_config.get("supported_parameters", [])
            if "confidence_threshold" not in supported_params:
                self.test_results.append("❌ supported_parameters 中缺少 confidence_threshold")
                success = False
                
            # 檢查路徑有效性
            system_path = integration_config.get("parameter_system_path", "")
            if not system_path or not system_path.endswith(".py"):
                self.test_results.append(f"❌ parameter_system_path 路徑無效: {system_path}")
                success = False
                
        except KeyError as e:
            self.test_results.append(f"❌ 動態參數整合配置結構錯誤: {e}")
            success = False
            
        if success:
            self.test_results.append("✅ 動態參數系統整合配置: 通過")
            
        return success
    
    def test_parameter_id_consistency(self, phase1a_config: Dict[str, Any], dynamic_config: Dict[str, Any]) -> bool:
        """測試參數ID一致性"""
        success = True
        
        try:
            # 從 Phase1A 配置中提取參數ID
            basic_mode = phase1a_config["phase1a_basic_signal_generation_dependency"]["configuration"]["signal_generation_params"]["basic_mode"]
            phase1a_param_id = basic_mode["confidence_threshold"]["parameter_id"]
            
            # 檢查動態配置中是否存在相應的適配規則
            # 修正完整路徑：dynamic_parameter_system -> dynamic_parameters -> phase1_signal_generation -> confidence_threshold
            dynamic_system = dynamic_config.get("dynamic_parameter_system", {})
            dynamic_params = dynamic_system.get("dynamic_parameters", {})
            phase1_params = dynamic_params.get("phase1_signal_generation", {})
            confidence_rules = phase1_params.get("confidence_threshold", {})
            
            if not confidence_rules:
                self.test_results.append("❌ 動態配置中缺少 confidence_threshold 適配規則")
                success = False
            else:
                # 檢查適配規則結構
                adaptation_rules = confidence_rules.get("adaptation_rules", {})
                required_regimes = ["BULL_TREND", "BEAR_TREND", "SIDEWAYS", "VOLATILE"]
                
                missing_regimes = []
                for regime in required_regimes:
                    if regime not in adaptation_rules:
                        missing_regimes.append(regime)
                    else:
                        # 檢查調整係數
                        regime_rule = adaptation_rules[regime]
                        if "adjustment_factor" not in regime_rule:
                            self.test_results.append(f"❌ {regime} 缺少 adjustment_factor")
                            success = False
                        else:
                            factor = regime_rule["adjustment_factor"]
                            if not isinstance(factor, (int, float)) or factor <= 0:
                                self.test_results.append(f"❌ {regime} adjustment_factor 值不合理: {factor}")
                                success = False
                
                if missing_regimes:
                    self.test_results.append(f"❌ 動態配置中缺少市場制度規則: {missing_regimes}")
                    success = False
                
                # 檢查基本值是否合理
                base_value = confidence_rules.get("base_value", 0)
                if not isinstance(base_value, (int, float)) or not 0 <= base_value <= 1:
                    self.test_results.append(f"❌ 動態配置中 base_value 值不合理: {base_value}")
                    success = False
                    
                # 檢查參數名稱一致性
                param_name = confidence_rules.get("parameter_name", "")
                if param_name != "confidence_threshold":
                    self.test_results.append(f"❌ 動態配置中參數名稱不一致: {param_name}")
                    success = False
                        
        except KeyError as e:
            self.test_results.append(f"❌ 參數ID一致性檢查錯誤: {e}")
            success = False
            
        if success:
            self.test_results.append("✅ 參數ID一致性: 通過")
            
        return success
    
    def test_data_flow_compatibility(self, config: Dict[str, Any]) -> bool:
        """測試數據流兼容性"""
        success = True
        
        try:
            # 檢查輸出目標配置
            dependency_graph = config["phase1a_basic_signal_generation_dependency"]["strategy_dependency_graph"]
            output_targets = dependency_graph["core_dependencies"]["output_targets"]
            
            # 確保輸出格式仍然標準化
            required_outputs = ["indicator_dependency_graph", "phase1b_volatility_adaptation"]
            for output in required_outputs:
                if output not in output_targets:
                    self.test_results.append(f"❌ 缺少必要的輸出目標: {output}")
                    success = False
                else:
                    output_config = output_targets[output]
                    if output_config.get("data_format") not in ["standardized_basic_signals", "basic_signal_foundation"]:
                        self.test_results.append(f"❌ {output} 數據格式不標準")
                        success = False
                        
            # 檢查整合點配置
            integration_points = config["phase1a_basic_signal_generation_dependency"]["integration_points"]
            
            # 確保保持現有的入口點
            entry_points = integration_points.get("entry_points", {})
            if "websocket_data_feed" not in entry_points:
                self.test_results.append("❌ 缺少 websocket_data_feed 入口點")
                success = False
                
            # 確保保持現有的出口點
            exit_points = integration_points.get("exit_points", {})
            if "parallel_distribution" not in exit_points:
                self.test_results.append("❌ 缺少 parallel_distribution 出口點")
                success = False
                
        except KeyError as e:
            self.test_results.append(f"❌ 數據流兼容性檢查錯誤: {e}")
            success = False
            
        if success:
            self.test_results.append("✅ 數據流兼容性: 通過")
            
        return success
    
    def test_backwards_compatibility(self, config: Dict[str, Any]) -> bool:
        """測試向後兼容性"""
        success = True
        
        try:
            signal_params = config["phase1a_basic_signal_generation_dependency"]["configuration"]["signal_generation_params"]
            
            # 確保原有參數仍然存在
            basic_mode = signal_params["basic_mode"]
            required_legacy_params = [
                "price_change_threshold", "volume_change_threshold", 
                "signal_strength_range", "confidence_calculation"
            ]
            
            for param in required_legacy_params:
                if param not in basic_mode:
                    self.test_results.append(f"❌ 基礎模式缺少原有參數: {param}")
                    success = False
                    
            # 確保極端市場模式原有參數存在
            extreme_mode = signal_params["extreme_market_mode"]
            required_extreme_params = [
                "price_change_threshold", "volume_change_threshold",
                "signal_strength_boost", "priority_escalation"
            ]
            
            for param in required_extreme_params:
                if param not in extreme_mode:
                    self.test_results.append(f"❌ 極端模式缺少原有參數: {param}")
                    success = False
                    
        except KeyError as e:
            self.test_results.append(f"❌ 向後兼容性檢查錯誤: {e}")
            success = False
            
        if success:
            self.test_results.append("✅ 向後兼容性: 通過")
            
        return success
    
    def test_performance_impact(self, config: Dict[str, Any]) -> bool:
        """測試性能影響評估"""
        success = True
        
        try:
            # 檢查性能目標是否保持
            performance_targets = config["phase1a_basic_signal_generation_dependency"]["configuration"]["performance_targets"]
            
            latency_target = performance_targets.get("processing_latency_p99", "")
            if not latency_target or "30ms" not in latency_target:
                self.test_results.append("❌ 處理延遲目標可能受影響")
                success = False
                
            # 檢查動態參數更新頻率
            dynamic_integration = config["phase1a_basic_signal_generation_dependency"]["configuration"]["dynamic_parameter_integration"]
            update_frequency = dynamic_integration.get("update_frequency", "")
            
            if update_frequency == "real_time":
                # 實時更新可能影響性能，但應該有緩存機制
                regime_detection = dynamic_integration.get("market_regime_detection", {})
                cache_ttl = regime_detection.get("regime_cache_ttl", "")
                
                if not cache_ttl or "300_seconds" not in cache_ttl:
                    self.test_results.append("⚠️ 實時更新可能影響性能，建議檢查緩存策略")
                    # 不設為失敗，只是警告
                    
        except KeyError as e:
            self.test_results.append(f"❌ 性能影響評估錯誤: {e}")
            success = False
            
        if success:
            self.test_results.append("✅ 性能影響評估: 通過")
            
        return success
    
    def run_all_tests(self) -> bool:
        """執行所有測試"""
        print("🧪 開始執行 Phase1A JSON 整合測試...")
        print("=" * 60)
        
        # 載入配置
        phase1a_config = self.load_phase1a_config()
        dynamic_config = self.load_dynamic_parameter_config()
        
        if not phase1a_config or not dynamic_config:
            print("❌ 配置載入失敗，測試中止")
            return False
            
        # 執行測試
        tests = [
            self.test_json_syntax_validity(phase1a_config),
            self.test_confidence_threshold_structure(phase1a_config),
            self.test_dynamic_parameter_integration(phase1a_config),
            self.test_parameter_id_consistency(phase1a_config, dynamic_config),
            self.test_data_flow_compatibility(phase1a_config),
            self.test_backwards_compatibility(phase1a_config),
            self.test_performance_impact(phase1a_config)
        ]
        
        # 輸出結果
        print("\n📊 測試結果:")
        print("-" * 40)
        for result in self.test_results:
            print(result)
            
        total_tests = len(tests)
        passed_tests = sum(tests)
        
        print(f"\n📈 測試總結: {passed_tests}/{total_tests} 通過")
        
        if passed_tests == total_tests:
            print("🎉 所有測試通過！JSON 整合完成，可以進行下一步")
            return True
        else:
            print("⚠️ 部分測試失敗，需要修復後再繼續")
            return False

def main():
    """主函數"""
    tester = Phase1AJsonIntegrationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Phase1A JSON 整合測試完成，準備開始 Python 實施")
        sys.exit(0)
    else:
        print("\n❌ Phase1A JSON 整合測試失敗，需要修復配置")
        sys.exit(1)

if __name__ == "__main__":
    main()
