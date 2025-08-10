#!/usr/bin/env python3
"""
🔬 詳細實戰分析工具 - Phase1 真實問題檢測
檢測實際的數據流、邏輯一致性和實現完整性問題
"""

import os
import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Set
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DetailedPhase1AnalysisTool:
    """詳細Phase1分析工具"""
    
    def __init__(self):
        self.base_path = Path("/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation")
        self.issues = []
        self.warnings = []
        self.fixes_needed = []
        
        # 核心流程組件
        self.components = {
            "websocket_realtime_driver": "websocket_realtime_driver/websocket_realtime_driver.py",
            "phase1a_basic_signal_generation": "phase1a_basic_signal_generation/phase1a_basic_signal_generation.py",
            "indicator_dependency_graph": "indicator_dependency/indicator_dependency_graph.py",
            "phase1b_volatility_adaptation": "phase1b_volatility_adaptation/phase1b_volatility_adaptation.py",
            "phase1c_signal_standardization": "phase1c_signal_standardization/phase1c_signal_standardization.py",
            "unified_signal_candidate_pool": "unified_signal_pool/unified_signal_candidate_pool.py"
        }
        
        # 期望的數據流接口
        self.expected_interfaces = {
            "websocket_realtime_driver": {
                "outputs": ["real_time_price", "volume", "market_depth", "kline_data"],
                "methods": ["start", "stop", "subscribe", "get_latest_data"]
            },
            "phase1a_basic_signal_generation": {
                "inputs": ["real_time_price", "volume", "market_depth"],
                "outputs": ["basic_signals", "standardized_basic_signals"],
                "methods": ["process_market_data", "generate_signals"]
            },
            "indicator_dependency_graph": {
                "inputs": ["standardized_basic_signals", "market_data"],
                "outputs": ["technical_indicators", "indicator_results"],
                "methods": ["calculate_indicators", "update_dependencies"]
            },
            "phase1b_volatility_adaptation": {
                "inputs": ["basic_signal_foundation", "technical_indicators"],
                "outputs": ["volatility_metrics", "adaptive_adjustments"],
                "methods": ["analyze_volatility", "adapt_signals"]
            },
            "phase1c_signal_standardization": {
                "inputs": ["preprocessed_signals", "adaptive_adjustments"],
                "outputs": ["standardized_signals", "quality_scores"],
                "methods": ["standardize_signals", "calculate_quality"]
            },
            "unified_signal_candidate_pool": {
                "inputs": ["standardized_signals", "quality_scores"],
                "outputs": ["epl_ready_signals", "ai_enhanced_signals"],
                "methods": ["aggregate_signals", "ai_learning", "prepare_epl"]
            }
        }
    
    def run_detailed_analysis(self) -> Dict[str, Any]:
        """執行詳細分析"""
        logger.info("🔬 開始詳細實戰分析...")
        
        # 1. 檢查文件存在性
        self._check_file_existence()
        
        # 2. 分析數據流一致性
        self._analyze_data_flow_consistency()
        
        # 3. 檢查方法實現完整性
        self._check_method_implementations()
        
        # 4. 驗證異步實現
        self._verify_async_implementations()
        
        # 5. 檢查導入依賴
        self._check_import_dependencies()
        
        # 6. 分析配置一致性
        self._analyze_config_consistency()
        
        # 7. 檢查錯誤處理
        self._check_error_handling()
        
        return self._generate_detailed_report()
    
    def _check_file_existence(self):
        """檢查文件存在性"""
        logger.info("📁 檢查文件存在性...")
        
        missing_files = []
        for component, path in self.components.items():
            full_path = self.base_path / path
            if not full_path.exists():
                missing_files.append(f"{component}: {path}")
                self.issues.append(f"❌ 缺失文件: {component} - {path}")
        
        if missing_files:
            self.issues.append(f"❌ 共有 {len(missing_files)} 個文件缺失")
        else:
            logger.info("✅ 所有核心文件都存在")
    
    def _analyze_data_flow_consistency(self):
        """分析數據流一致性"""
        logger.info("🔄 分析數據流一致性...")
        
        for component, path in self.components.items():
            full_path = self.base_path / path
            if full_path.exists():
                self._check_component_data_flow(component, full_path)
    
    def _check_component_data_flow(self, component: str, file_path: Path):
        """檢查組件數據流"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            expected = self.expected_interfaces.get(component, {})
            
            # 檢查輸入數據處理
            if 'inputs' in expected:
                for input_type in expected['inputs']:
                    if input_type not in content:
                        self.warnings.append(f"⚠️ {component}: 未發現 {input_type} 輸入處理")
            
            # 檢查輸出數據生成
            if 'outputs' in expected:
                for output_type in expected['outputs']:
                    if output_type not in content:
                        self.warnings.append(f"⚠️ {component}: 未發現 {output_type} 輸出生成")
            
            # 檢查方法存在性
            if 'methods' in expected:
                for method in expected['methods']:
                    method_pattern = f"(def|async def)\\s+{method}"
                    if not re.search(method_pattern, content):
                        self.issues.append(f"❌ {component}: 缺失核心方法 {method}")
            
        except Exception as e:
            self.issues.append(f"❌ {component}: 文件讀取失敗 - {str(e)}")
    
    def _check_method_implementations(self):
        """檢查方法實現完整性"""
        logger.info("⚙️ 檢查方法實現完整性...")
        
        for component, path in self.components.items():
            full_path = self.base_path / path
            if full_path.exists():
                self._analyze_component_methods(component, full_path)
    
    def _analyze_component_methods(self, component: str, file_path: Path):
        """分析組件方法"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析AST
            tree = ast.parse(content)
            
            # 查找類和方法
            classes = []
            methods = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.append(node.name)
            
            # 檢查是否有主要類
            main_class_patterns = [
                f"Phase1A.*",
                f".*DependencyGraph",
                f"Phase1B.*",
                f"Phase1C.*",
                f".*SignalPool.*",
                f"UnifiedSignalCandidatePoolV3",
                f"WebSocket.*Driver"
            ]
            
            has_main_class = False
            for pattern in main_class_patterns:
                if any(re.match(pattern, cls) for cls in classes):
                    has_main_class = True
                    break
            
            if not has_main_class:
                self.issues.append(f"❌ {component}: 未發現主要處理類")
            
            # 檢查異步方法比例
            async_methods = len([m for m in methods if content.find(f"async def {m}") != -1])
            total_methods = len(methods)
            
            if total_methods > 0:
                async_ratio = async_methods / total_methods
                if async_ratio < 0.3:  # 至少30%應該是異步方法
                    self.warnings.append(f"⚠️ {component}: 異步方法比例過低 ({async_ratio:.1%})")
            
        except SyntaxError as e:
            self.issues.append(f"❌ {component}: 語法錯誤 - {str(e)}")
        except Exception as e:
            self.issues.append(f"❌ {component}: 分析失敗 - {str(e)}")
    
    def _verify_async_implementations(self):
        """驗證異步實現"""
        logger.info("🔄 驗證異步實現...")
        
        for component, path in self.components.items():
            full_path = self.base_path / path
            if full_path.exists():
                self._check_async_patterns(component, full_path)
    
    def _check_async_patterns(self, component: str, file_path: Path):
        """檢查異步模式"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 檢查異步關鍵字
            has_async_def = "async def" in content
            has_await = "await" in content
            has_asyncio = "asyncio" in content
            
            if not has_async_def:
                self.warnings.append(f"⚠️ {component}: 未使用異步函數")
            
            if has_async_def and not has_await:
                self.issues.append(f"❌ {component}: 有async函數但未使用await")
            
            if not has_asyncio:
                self.warnings.append(f"⚠️ {component}: 未導入asyncio模組")
            
            # 檢查常見的阻塞呼叫
            blocking_patterns = [
                r"time\.sleep\(",
                r"requests\.get\(",
                r"requests\.post\(",
                r"\.join\(\)"
            ]
            
            for pattern in blocking_patterns:
                if re.search(pattern, content):
                    self.warnings.append(f"⚠️ {component}: 可能包含阻塞呼叫: {pattern}")
            
        except Exception as e:
            self.issues.append(f"❌ {component}: 異步分析失敗 - {str(e)}")
    
    def _check_import_dependencies(self):
        """檢查導入依賴"""
        logger.info("📦 檢查導入依賴...")
        
        for component, path in self.components.items():
            full_path = self.base_path / path
            if full_path.exists():
                self._analyze_imports(component, full_path)
    
    def _analyze_imports(self, component: str, file_path: Path):
        """分析導入"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 檢查必要的導入
            required_imports = {
                "websocket_realtime_driver": ["asyncio", "websockets", "json"],
                "phase1a_basic_signal_generation": ["asyncio", "numpy", "pandas"],
                "indicator_dependency_graph": ["pandas", "numpy", "asyncio"],
                "phase1b_volatility_adaptation": ["asyncio", "numpy", "pandas"],
                "phase1c_signal_standardization": ["asyncio", "pandas", "numpy"],
                "unified_signal_candidate_pool": ["asyncio", "pandas", "numpy", "json"]
            }
            
            component_requirements = required_imports.get(component, [])
            
            for requirement in component_requirements:
                import_patterns = [
                    f"import {requirement}",
                    f"from {requirement} import",
                    f"import {requirement} as"
                ]
                
                if not any(pattern in content for pattern in import_patterns):
                    self.warnings.append(f"⚠️ {component}: 可能缺失必要導入 {requirement}")
            
            # 檢查循環導入風險
            phase_imports = re.findall(r"from.*phase\d[abc]?.*import", content)
            if len(phase_imports) > 2:
                self.warnings.append(f"⚠️ {component}: 可能存在循環導入風險")
            
        except Exception as e:
            self.issues.append(f"❌ {component}: 導入分析失敗 - {str(e)}")
    
    def _analyze_config_consistency(self):
        """分析配置一致性"""
        logger.info("⚙️ 分析配置一致性...")
        
        for component in self.components.keys():
            json_files = [
                f"{component}/{component}.json",
                f"{component}/{component}_dependency.json"
            ]
            
            for json_file in json_files:
                json_path = self.base_path / json_file
                if json_path.exists():
                    self._check_json_config(component, json_path)
    
    def _check_json_config(self, component: str, json_path: Path):
        """檢查JSON配置"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 檢查必要的配置段落
            required_sections = [
                "dependencies",
                "performance_targets",
                "input_format",
                "output_format"
            ]
            
            for section in required_sections:
                if section not in config:
                    self.warnings.append(f"⚠️ {component}: JSON配置缺失 {section} 段落")
            
            # 檢查延遲目標
            if "performance_targets" in config:
                targets = config["performance_targets"]
                if "latency" in targets or "processing_time" in targets:
                    # 延遲目標存在，這是好的
                    pass
                else:
                    self.warnings.append(f"⚠️ {component}: 缺失延遲性能目標")
            
        except json.JSONDecodeError as e:
            self.issues.append(f"❌ {component}: JSON格式錯誤 - {str(e)}")
        except Exception as e:
            self.issues.append(f"❌ {component}: 配置分析失敗 - {str(e)}")
    
    def _check_error_handling(self):
        """檢查錯誤處理"""
        logger.info("🛡️ 檢查錯誤處理...")
        
        for component, path in self.components.items():
            full_path = self.base_path / path
            if full_path.exists():
                self._analyze_error_handling(component, full_path)
    
    def _analyze_error_handling(self, component: str, file_path: Path):
        """分析錯誤處理"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 檢查try-except覆蓋
            try_count = content.count("try:")
            except_count = content.count("except")
            
            if try_count == 0:
                self.issues.append(f"❌ {component}: 完全缺失錯誤處理")
            elif try_count < 3:
                self.warnings.append(f"⚠️ {component}: 錯誤處理覆蓋可能不足")
            
            # 檢查裸except
            if "except:" in content:
                self.warnings.append(f"⚠️ {component}: 使用裸except，應該指定異常類型")
            
            # 檢查日誌記錄
            if "logger" not in content and "logging" not in content:
                self.warnings.append(f"⚠️ {component}: 未使用日誌記錄")
            
        except Exception as e:
            self.issues.append(f"❌ {component}: 錯誤處理分析失敗 - {str(e)}")
    
    def _generate_detailed_report(self) -> Dict[str, Any]:
        """生成詳細報告"""
        
        # 計算總體評分
        total_checks = len(self.issues) + len(self.warnings) + len(self.fixes_needed)
        critical_issues = len(self.issues)
        
        if total_checks == 0:
            score = 100
        else:
            # 嚴重問題 -20分，警告 -5分，需要修復 -10分
            penalty = critical_issues * 20 + len(self.warnings) * 5 + len(self.fixes_needed) * 10
            score = max(0, 100 - penalty)
        
        report = {
            "overall_score": score,
            "critical_issues": self.issues,
            "warnings": self.warnings,
            "fixes_needed": self.fixes_needed,
            "components_analyzed": len(self.components),
            "analysis_timestamp": datetime.now().isoformat(),
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """生成修復建議"""
        recommendations = []
        
        if self.issues:
            recommendations.append("🔧 立即修復所有critical issues以確保系統正常運行")
        
        if len(self.warnings) > 10:
            recommendations.append("⚠️ 大量warnings需要關注，建議分批次解決")
        
        if self.fixes_needed:
            recommendations.append("🔨 處理所有fixes_needed項目以提升系統品質")
        
        # 基於具體問題類型的建議
        import_issues = [w for w in self.warnings if "導入" in w or "import" in w]
        if import_issues:
            recommendations.append("📦 檢查並修復導入依賴問題")
        
        async_issues = [w for w in self.warnings if "異步" in w or "async" in w]
        if async_issues:
            recommendations.append("⚡ 改善異步實現以提升性能")
        
        error_issues = [i for i in self.issues if "錯誤處理" in i]
        if error_issues:
            recommendations.append("🛡️ 加強錯誤處理和異常管理")
        
        return recommendations
    
    def print_detailed_report(self, report: Dict[str, Any]):
        """打印詳細報告"""
        print("\n" + "="*80)
        print("🔬 PHASE1 SIGNAL GENERATION - 詳細實戰分析報告")
        print("="*80)
        
        print(f"\n📊 總體評分: {report['overall_score']}/100")
        
        if report['critical_issues']:
            print(f"\n❌ 嚴重問題 ({len(report['critical_issues'])} 項):")
            for issue in report['critical_issues'][:10]:  # 顯示前10項
                print(f"   {issue}")
            if len(report['critical_issues']) > 10:
                print(f"   ... 還有 {len(report['critical_issues']) - 10} 項")
        
        if report['warnings']:
            print(f"\n⚠️ 警告項目 ({len(report['warnings'])} 項):")
            for warning in report['warnings'][:10]:  # 顯示前10項
                print(f"   {warning}")
            if len(report['warnings']) > 10:
                print(f"   ... 還有 {len(report['warnings']) - 10} 項")
        
        if report['fixes_needed']:
            print(f"\n🔧 需要修復 ({len(report['fixes_needed'])} 項):")
            for fix in report['fixes_needed'][:10]:
                print(f"   {fix}")
        
        if report['recommendations']:
            print(f"\n💡 修復建議:")
            for rec in report['recommendations']:
                print(f"   {rec}")
        
        print(f"\n📈 分析統計:")
        print(f"   分析組件數: {report['components_analyzed']}")
        print(f"   分析時間: {report['analysis_timestamp']}")
        
        print("\n" + "="*80)

def main():
    """主函數"""
    from datetime import datetime
    
    tool = DetailedPhase1AnalysisTool()
    report = tool.run_detailed_analysis()
    tool.print_detailed_report(report)
    
    return report

if __name__ == "__main__":
    main()
