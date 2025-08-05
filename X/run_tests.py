"""
🎯 Trading X - 測試執行器
統一管理和執行所有測試腳本
"""

import unittest
import asyncio
import sys
import os
from typing import List, Dict, Any
from datetime import datetime
import importlib.util

class TestRunner:
    """測試運行器"""
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.test_results = {}
        self.categories = ["unit", "integration", "flow", "performance"]
    
    def discover_tests(self, category: str) -> List[str]:
        """發現測試文件"""
        category_path = os.path.join(self.base_path, "tests", category)
        test_files = []
        
        if os.path.exists(category_path):
            for file in os.listdir(category_path):
                if file.startswith("test_") and file.endswith(".py"):
                    test_files.append(os.path.join(category_path, file))
        
        return test_files
    
    def run_category_tests(self, category: str, verbose: bool = True) -> Dict[str, Any]:
        """運行特定類別的測試"""
        print(f"\n🧪 開始執行 {category.upper()} 測試...")
        print("=" * 60)
        
        test_files = self.discover_tests(category)
        category_results = {
            "category": category,
            "total_files": len(test_files),
            "test_results": [],
            "summary": {"passed": 0, "failed": 0, "errors": 0}
        }
        
        for test_file in test_files:
            print(f"\n📄 執行測試文件: {os.path.basename(test_file)}")
            result = self._run_single_test_file(test_file, verbose)
            category_results["test_results"].append(result)
            
            # 更新摘要
            if result["success"]:
                category_results["summary"]["passed"] += 1
            else:
                category_results["summary"]["failed"] += 1
                if result.get("has_errors", False):
                    category_results["summary"]["errors"] += 1
        
        self._print_category_summary(category_results)
        return category_results
    
    def _run_single_test_file(self, test_file: str, verbose: bool) -> Dict[str, Any]:
        """運行單個測試文件"""
        try:
            # 動態載入測試模組
            spec = importlib.util.spec_from_file_location("test_module", test_file)
            test_module = importlib.util.module_from_spec(spec)
            
            # 添加到 sys.modules 以支持相對導入
            sys.modules["test_module"] = test_module
            spec.loader.exec_module(test_module)
            
            # 創建測試套件
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(test_module)
            
            # 運行測試
            runner = unittest.TextTestRunner(
                verbosity=2 if verbose else 1,
                stream=sys.stdout
            )
            
            result = runner.run(suite)
            
            return {
                "file": os.path.basename(test_file),
                "tests_run": result.testsRun,
                "failures": len(result.failures),
                "errors": len(result.errors),
                "success": result.wasSuccessful(),
                "has_errors": len(result.errors) > 0
            }
            
        except Exception as e:
            print(f"❌ 執行測試文件 {os.path.basename(test_file)} 時發生錯誤: {str(e)}")
            return {
                "file": os.path.basename(test_file),
                "tests_run": 0,
                "failures": 0,
                "errors": 1,
                "success": False,
                "has_errors": True,
                "error_message": str(e)
            }
    
    def _print_category_summary(self, results: Dict[str, Any]):
        """打印類別摘要"""
        print(f"\n📊 {results['category'].upper()} 測試摘要:")
        print(f"   測試文件數量: {results['total_files']}")
        print(f"   通過文件: {results['summary']['passed']}")
        print(f"   失敗文件: {results['summary']['failed']}")
        print(f"   錯誤文件: {results['summary']['errors']}")
        
        # 詳細結果
        for test_result in results["test_results"]:
            status = "✅" if test_result["success"] else "❌"
            print(f"   {status} {test_result['file']}: {test_result['tests_run']} tests")
    
    def run_all_tests(self, include_performance: bool = False) -> Dict[str, Any]:
        """運行所有測試"""
        print("\n🚀 Trading X 完整測試套件")
        print("=" * 60)
        print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        categories_to_run = ["unit", "integration", "flow"]
        if include_performance:
            categories_to_run.append("performance")
        
        all_results = {
            "start_time": datetime.now().isoformat(),
            "categories": {},
            "overall_summary": {"total_passed": 0, "total_failed": 0, "total_errors": 0}
        }
        
        for category in categories_to_run:
            category_result = self.run_category_tests(category)
            all_results["categories"][category] = category_result
            
            # 更新總體摘要
            all_results["overall_summary"]["total_passed"] += category_result["summary"]["passed"]
            all_results["overall_summary"]["total_failed"] += category_result["summary"]["failed"]
            all_results["overall_summary"]["total_errors"] += category_result["summary"]["errors"]
        
        all_results["end_time"] = datetime.now().isoformat()
        self._print_overall_summary(all_results)
        
        return all_results
    
    def _print_overall_summary(self, results: Dict[str, Any]):
        """打印總體摘要"""
        print("\n" + "=" * 60)
        print("🎯 Trading X 測試總體摘要")
        print("=" * 60)
        
        summary = results["overall_summary"]
        total_files = summary["total_passed"] + summary["total_failed"]
        
        print(f"總測試文件: {total_files}")
        print(f"✅ 通過: {summary['total_passed']}")
        print(f"❌ 失敗: {summary['total_failed']}")
        print(f"⚠️  錯誤: {summary['total_errors']}")
        
        success_rate = (summary["total_passed"] / total_files * 100) if total_files > 0 else 0
        print(f"📈 成功率: {success_rate:.1f}%")
        
        print(f"\n完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 給出建議
        if summary["total_failed"] == 0 and summary["total_errors"] == 0:
            print("\n🎉 所有測試通過！系統狀態良好。")
        else:
            print(f"\n⚠️  發現 {summary['total_failed']} 個失敗和 {summary['total_errors']} 個錯誤。")
            print("建議檢查失敗的測試並修復相關問題。")
    
    def run_quick_test(self) -> Dict[str, Any]:
        """快速測試（只運行核心測試）"""
        print("\n⚡ Trading X 快速測試模式")
        print("=" * 60)
        
        # 只運行單元測試和整合測試
        quick_results = {
            "mode": "quick",
            "start_time": datetime.now().isoformat(),
            "categories": {}
        }
        
        for category in ["unit", "integration"]:
            quick_results["categories"][category] = self.run_category_tests(category)
        
        quick_results["end_time"] = datetime.now().isoformat()
        return quick_results

def main():
    """主函數"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.dirname(current_dir)  # 回到 X 目錄
    
    runner = TestRunner(base_path)
    
    # 檢查命令行參數
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "quick":
            results = runner.run_quick_test()
        elif mode == "performance":
            results = runner.run_category_tests("performance")
        elif mode in ["unit", "integration", "flow"]:
            results = runner.run_category_tests(mode)
        elif mode == "all":
            include_perf = "--include-performance" in sys.argv
            results = runner.run_all_tests(include_performance=include_perf)
        else:
            print("❌ 未知的測試模式。可用模式: quick, unit, integration, flow, performance, all")
            return
    else:
        # 默認運行快速測試
        results = runner.run_quick_test()
    
    # 保存結果到文件
    import json
    result_file = os.path.join(base_path, "test_results.json")
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 測試結果已保存到: {result_file}")

if __name__ == "__main__":
    main()
