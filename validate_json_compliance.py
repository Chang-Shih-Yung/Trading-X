#!/usr/bin/env python3
"""
🔍 Trading X - JSON規範合規性驗證工具
驗證所有Phase1組件是否符合JSON規範的輸入/輸出要求
"""

import asyncio
import sys
import os
import inspect
from datetime import datetime
from typing import Dict, List, Any, Set

# 添加路徑
sys.path.append('/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation')

class JSONComplianceValidator:
    """JSON規範合規性驗證器"""
    
    def __init__(self):
        self.validation_results = {}
        self.warnings = []
        self.critical_issues = []
        
        # JSON規範要求的輸入/輸出映射
        self.required_data_flows = {
            "websocket_realtime_driver": {
                "required_outputs": ["real_time_price", "market_depth", "kline_data", "real_time_trades", "orderbook_data"],
                "output_methods": ["generate_market_depth_output", "_handle_phase1a_signal_generation"]
            },
            "phase1a_basic_signal_generation": {
                "required_inputs": ["real_time_price", "market_depth", "volume"],
                "required_outputs": ["basic_signals", "standardized_basic_signals"],
                "input_methods": ["process_real_time_price", "process_market_depth"],
                "output_methods": ["generate_basic_signals_output", "generate_standardized_basic_signals_output"]
            },
            "indicator_dependency_graph": {
                "required_inputs": ["standardized_basic_signals"],
                "required_outputs": ["indicator_results"],
                "input_methods": ["process_standardized_basic_signals"],
                "output_methods": ["generate_indicator_results_output"]
            },
            "phase1b_volatility_adaptation": {
                "required_inputs": ["basic_signal_foundation", "technical_indicators"],
                "required_outputs": ["adaptive_adjustments"],
                "input_methods": ["analyze_volatility"],
                "output_methods": ["adapt_signals"]
            },
            "phase1c_signal_standardization": {
                "required_inputs": ["preprocessed_signals"],
                "required_outputs": ["standardized_signals"],
                "input_methods": ["standardize_signals"],
                "output_methods": ["calculate_quality"]
            },
            "unified_signal_candidate_pool": {
                "required_inputs": ["all_standardized_signals"],
                "required_outputs": ["unified_signal_pool", "epl_ready_signals"],
                "input_methods": ["aggregate_signals"],
                "output_methods": ["ai_learning", "prepare_epl"]
            }
        }
    
    async def validate_all_components(self):
        """驗證所有組件"""
        print("🔍 開始JSON規範合規性驗證...")
        print("=" * 60)
        
        components = [
            ("websocket_realtime_driver", "websocket_realtime_driver/websocket_realtime_driver.py"),
            ("phase1a_basic_signal_generation", "phase1a_basic_signal_generation/phase1a_basic_signal_generation.py"),
            ("indicator_dependency_graph", "indicator_dependency/indicator_dependency_graph.py"),
            ("phase1b_volatility_adaptation", "phase1b_volatility_adaptation/phase1b_volatility_adaptation.py"),
            ("phase1c_signal_standardization", "phase1c_signal_standardization/phase1c_signal_standardization.py"),
            ("unified_signal_candidate_pool", "unified_signal_pool/unified_signal_candidate_pool.py")
        ]
        
        for component_name, module_path in components:
            await self.validate_component(component_name, module_path)
        
        await self.generate_summary_report()
    
    async def validate_component(self, component_name: str, module_path: str):
        """驗證單個組件"""
        print(f"\n📊 驗證組件: {component_name}")
        print("-" * 40)
        
        try:
            # 動態導入模組
            module = await self.import_module(module_path)
            if not module:
                self.critical_issues.append(f"❌ {component_name}: 模組導入失敗")
                return
            
            # 檢查必要的方法
            await self.check_required_methods(component_name, module)
            
            # 檢查數據流輸入處理
            await self.check_input_processing(component_name, module)
            
            # 檢查數據流輸出生成
            await self.check_output_generation(component_name, module)
            
            print(f"✅ {component_name} 驗證完成")
            
        except Exception as e:
            error_msg = f"❌ {component_name}: 驗證失敗 - {e}"
            self.critical_issues.append(error_msg)
            print(error_msg)
    
    async def import_module(self, module_path: str):
        """動態導入模組"""
        try:
            # 構建完整路徑
            full_path = f"/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/{module_path}"
            
            # 讀取模組內容並檢查基本語法
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 檢查是否包含基本類定義
            if "class " not in content:
                self.warnings.append(f"⚠️ {module_path}: 未發現類定義")
                return None
            
            return content  # 返回內容而不是實際導入
            
        except Exception as e:
            self.critical_issues.append(f"❌ {module_path}: 無法讀取模組 - {e}")
            return None
    
    async def check_required_methods(self, component_name: str, module_content: str):
        """檢查必要方法"""
        requirements = self.required_data_flows.get(component_name, {})
        
        # 檢查輸入處理方法
        input_methods = requirements.get("input_methods", [])
        for method in input_methods:
            if f"def {method}" in module_content or f"async def {method}" in module_content:
                print(f"  ✅ 發現輸入方法: {method}")
            else:
                warning = f"⚠️ {component_name}: 缺少輸入處理方法 {method}"
                self.warnings.append(warning)
                print(f"  {warning}")
        
        # 檢查輸出處理方法
        output_methods = requirements.get("output_methods", [])
        for method in output_methods:
            if f"def {method}" in module_content or f"async def {method}" in module_content:
                print(f"  ✅ 發現輸出方法: {method}")
            else:
                warning = f"⚠️ {component_name}: 缺少輸出生成方法 {method}"
                self.warnings.append(warning)
                print(f"  {warning}")
    
    async def check_input_processing(self, component_name: str, module_content: str):
        """檢查輸入處理"""
        requirements = self.required_data_flows.get(component_name, {})
        required_inputs = requirements.get("required_inputs", [])
        
        for input_type in required_inputs:
            if input_type in module_content or input_type.replace("_", "-") in module_content:
                print(f"  ✅ 發現輸入處理: {input_type}")
            else:
                warning = f"⚠️ {component_name}: 未發現 {input_type} 輸入處理"
                self.warnings.append(warning)
                print(f"  {warning}")
    
    async def check_output_generation(self, component_name: str, module_content: str):
        """檢查輸出生成"""
        requirements = self.required_data_flows.get(component_name, {})
        required_outputs = requirements.get("required_outputs", [])
        
        for output_type in required_outputs:
            if output_type in module_content or output_type.replace("_", "-") in module_content:
                print(f"  ✅ 發現輸出生成: {output_type}")
            else:
                warning = f"⚠️ {component_name}: 未發現 {output_type} 輸出生成"
                self.warnings.append(warning)
                print(f"  {warning}")
    
    async def generate_summary_report(self):
        """生成總結報告"""
        print("\n" + "=" * 60)
        print("📊 JSON規範合規性驗證報告")
        print("=" * 60)
        
        total_issues = len(self.critical_issues)
        total_warnings = len(self.warnings)
        
        # 計算合規性評分
        if total_issues == 0:
            if total_warnings == 0:
                score = 100
                grade = "完全合規 🎉"
            elif total_warnings <= 10:
                score = 85
                grade = "高度合規 ✅"
            elif total_warnings <= 20:
                score = 70
                grade = "基本合規 ⚠️"
            else:
                score = 50
                grade = "需要改善 ⚠️"
        else:
            score = max(0, 50 - total_issues * 10)
            grade = "不合規 ❌"
        
        print(f"📊 總體評分: {score}/100 - {grade}")
        print()
        
        if total_issues > 0:
            print(f"❌ 嚴重問題 ({total_issues} 項):")
            for issue in self.critical_issues:
                print(f"   {issue}")
            print()
        
        if total_warnings > 0:
            print(f"⚠️ 警告項目 ({total_warnings} 項):")
            for i, warning in enumerate(self.warnings[:10]):  # 只顯示前10個
                print(f"   {warning}")
            if total_warnings > 10:
                print(f"   ... 還有 {total_warnings - 10} 項")
            print()
        
        print("💡 修復建議:")
        if total_issues > 0:
            print("   🔥 優先修復critical issues，這些會阻止系統運行")
        if total_warnings > 0:
            print("   ⚠️ 按批次解決warnings，建議分組處理")
        if total_issues == 0 and total_warnings == 0:
            print("   🎉 所有組件完全符合JSON規範！")
        print()
        
        # 性能建議
        if "process_" in str(self.warnings):
            print("   ⚡ 建議優化異步處理方法以提升性能")
        if "generate_" in str(self.warnings):
            print("   📤 建議標準化輸出格式以提升兼容性")

async def main():
    """主函數"""
    validator = JSONComplianceValidator()
    await validator.validate_all_components()

if __name__ == "__main__":
    asyncio.run(main())
