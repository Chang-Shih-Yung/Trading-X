#!/usr/bin/env python3
"""
綜合測試運行腳本
自動執行所有測試類別並生成綜合報告
"""

import asyncio
import subprocess
import sys
import os
import json
from datetime import datetime
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveTestRunner:
    """綜合測試運行器"""
    
    def __init__(self):
        self.test_base_dir = "/Users/henrychang/Desktop/Trading-X/TEST"
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
    async def run_all_tests(self):
        """運行所有測試"""
        logger.info("🚀 開始綜合測試...")
        self.start_time = datetime.now()
        
        # 測試套件定義
        test_suites = [
            {
                "category": "即時信號引擎",
                "tests": [
                    ("realtime_signals/test_realtime_signal_engine.py", "即時信號引擎基礎功能"),
                    ("realtime_signals/test_pandas_ta_integration.py", "pandas-ta 整合"),
                    ("realtime_signals/test_automation_flow.py", "端到端自動化流程"),
                ]
            },
            {
                "category": "性能測試",
                "tests": [
                    ("performance/test_performance_load.py", "性能與負載測試"),
                ]
            },
            {
                "category": "數據管理",
                "tests": [
                    ("data_management/test_data_cleanup.py", "數據管理與清理"),
                ]
            }
        ]
        
        # 執行測試套件
        for suite in test_suites:
            category = suite["category"]
            logger.info(f"\n📂 執行測試類別: {category}")
            
            category_results = []
            
            for test_file, test_description in suite["tests"]:
                logger.info(f"🧪 執行測試: {test_description}")
                result = await self._run_single_test(test_file, test_description)
                category_results.append(result)
                
                # 測試間隔
                await asyncio.sleep(2)
            
            self.test_results[category] = category_results
        
        self.end_time = datetime.now()
        
        # 生成測試報告
        await self._generate_test_report()
        
        return self._calculate_overall_success()
    
    async def _run_single_test(self, test_file, description):
        """運行單個測試"""
        test_path = os.path.join(self.test_base_dir, test_file)
        
        if not os.path.exists(test_path):
            logger.error(f"❌ 測試文件不存在: {test_path}")
            return {
                "file": test_file,
                "description": description,
                "success": False,
                "error": "測試文件不存在",
                "duration": 0,
                "output": ""
            }
        
        start_time = datetime.now()
        
        try:
            # 執行測試腳本
            process = await asyncio.create_subprocess_exec(
                sys.executable, test_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=self.test_base_dir
            )
            
            stdout, _ = await process.communicate()
            output = stdout.decode('utf-8', errors='ignore')
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            success = process.returncode == 0
            
            result = {
                "file": test_file,
                "description": description,
                "success": success,
                "error": None if success else f"退出代碼: {process.returncode}",
                "duration": duration,
                "output": output
            }
            
            if success:
                logger.info(f"✅ {description} - 通過 ({duration:.1f}秒)")
            else:
                logger.error(f"❌ {description} - 失敗 ({duration:.1f}秒)")
                
            return result
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.error(f"❌ {description} - 異常: {e}")
            
            return {
                "file": test_file,
                "description": description,
                "success": False,
                "error": str(e),
                "duration": duration,
                "output": ""
            }
    
    async def _generate_test_report(self):
        """生成測試報告"""
        logger.info("\n📊 生成測試報告...")
        
        total_duration = (self.end_time - self.start_time).total_seconds()
        
        # 統計數據
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for category, results in self.test_results.items():
            for result in results:
                total_tests += 1
                if result["success"]:
                    passed_tests += 1
                else:
                    failed_tests += 1
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # 生成控制台報告
        logger.info("="*80)
        logger.info("🎯 Trading-X 自動化系統綜合測試報告")
        logger.info("="*80)
        logger.info(f"測試開始時間: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"測試結束時間: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"總測試時間: {total_duration:.1f} 秒")
        logger.info("-"*80)
        logger.info(f"總測試數量: {total_tests}")
        logger.info(f"通過測試: {passed_tests}")
        logger.info(f"失敗測試: {failed_tests}")
        logger.info(f"成功率: {success_rate:.1f}%")
        logger.info("-"*80)
        
        # 詳細結果
        for category, results in self.test_results.items():
            category_passed = sum(1 for r in results if r["success"])
            category_total = len(results)
            category_rate = (category_passed / category_total) * 100 if category_total > 0 else 0
            
            logger.info(f"\n📂 {category} ({category_passed}/{category_total}, {category_rate:.1f}%)")
            
            for result in results:
                status = "✅" if result["success"] else "❌"
                duration_str = f"{result['duration']:.1f}s"
                logger.info(f"  {status} {result['description']} ({duration_str})")
                
                if not result["success"] and result["error"]:
                    logger.info(f"      錯誤: {result['error']}")
        
        # 系統健康評估
        logger.info("\n" + "="*80)
        logger.info("🏥 系統健康評估")
        logger.info("="*80)
        
        if success_rate >= 90:
            logger.info("🎉 系統狀態: 優秀")
            logger.info("💡 自動化交易系統運行完美，所有核心功能正常工作")
        elif success_rate >= 75:
            logger.info("✅ 系統狀態: 良好")
            logger.info("💡 自動化交易系統基本正常，少量功能需要關注")
        elif success_rate >= 50:
            logger.info("⚠️ 系統狀態: 需要改善")
            logger.info("💡 自動化交易系統部分功能異常，建議檢查和修復")
        else:
            logger.info("❌ 系統狀態: 嚴重問題")
            logger.info("💡 自動化交易系統存在重大問題，需要立即處理")
        
        # 核心功能檢查
        logger.info("\n🔍 核心功能檢查:")
        core_functions = {
            "WebSocket 數據收集": self._check_core_function("websocket"),
            "pandas-ta 技術分析": self._check_core_function("pandas_ta"),
            "交易信號生成": self._check_core_function("signal"),
            "自動化流程": self._check_core_function("automation"),
            "數據管理": self._check_core_function("data")
        }
        
        for function_name, status in core_functions.items():
            status_icon = "✅" if status else "❌"
            logger.info(f"  {status_icon} {function_name}")
        
        # 建議和改善方案
        logger.info("\n💡 系統改善建議:")
        if failed_tests > 0:
            logger.info("  • 檢查失敗的測試項目，修復相關功能")
            logger.info("  • 查看測試輸出日誌，分析失敗原因")
            logger.info("  • 確保所有依賴服務正常運行")
        
        if success_rate < 100:
            logger.info("  • 定期運行測試套件，監控系統健康狀態")
            logger.info("  • 建立持續集成流程，自動化測試執行")
        
        logger.info("  • 監控系統性能指標，確保穩定運行")
        logger.info("  • 定期更新技術指標參數，優化交易策略")
        
        logger.info("\n" + "="*80)
        
        # 生成 JSON 報告文件
        await self._save_json_report(total_duration, total_tests, passed_tests, failed_tests, success_rate)
    
    def _check_core_function(self, function_type):
        """檢查核心功能狀態"""
        for category, results in self.test_results.items():
            for result in results:
                if function_type in result["file"].lower() or function_type in result["description"].lower():
                    if result["success"]:
                        return True
        return False
    
    async def _save_json_report(self, total_duration, total_tests, passed_tests, failed_tests, success_rate):
        """保存 JSON 格式的測試報告"""
        try:
            report_data = {
                "test_summary": {
                    "start_time": self.start_time.isoformat(),
                    "end_time": self.end_time.isoformat(),
                    "total_duration_seconds": total_duration,
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": success_rate
                },
                "test_results": self.test_results,
                "system_health": {
                    "status": self._get_health_status(success_rate),
                    "core_functions": {
                        "websocket": self._check_core_function("websocket"),
                        "pandas_ta": self._check_core_function("pandas_ta"),
                        "signal_generation": self._check_core_function("signal"),
                        "automation": self._check_core_function("automation"),
                        "data_management": self._check_core_function("data")
                    }
                }
            }
            
            report_file = os.path.join(self.test_base_dir, "comprehensive_test_report.json")
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"📄 詳細測試報告已保存: {report_file}")
            
        except Exception as e:
            logger.error(f"保存 JSON 報告失敗: {e}")
    
    def _get_health_status(self, success_rate):
        """獲取健康狀態"""
        if success_rate >= 90:
            return "excellent"
        elif success_rate >= 75:
            return "good"
        elif success_rate >= 50:
            return "needs_improvement"
        else:
            return "critical"
    
    def _calculate_overall_success(self):
        """計算總體成功率"""
        total_tests = 0
        passed_tests = 0
        
        for category, results in self.test_results.items():
            for result in results:
                total_tests += 1
                if result["success"]:
                    passed_tests += 1
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        return success_rate >= 75  # 75% 以上認為總體成功

async def main():
    """主函數"""
    logger.info("🎯 Trading-X 自動化系統綜合測試")
    logger.info("="*60)
    logger.info("測試內容:")
    logger.info("  • 即時信號引擎功能")
    logger.info("  • pandas-ta 技術分析整合")
    logger.info("  • 端到端自動化流程")
    logger.info("  • 系統性能與負載能力")
    logger.info("  • 數據管理與清理機制")
    logger.info("="*60)
    
    runner = ComprehensiveTestRunner()
    
    try:
        success = await runner.run_all_tests()
        
        if success:
            logger.info("\n🎉 綜合測試完成 - 系統整體運行良好!")
            return True
        else:
            logger.warning("\n⚠️ 綜合測試完成 - 系統存在改善空間")
            return False
            
    except Exception as e:
        logger.error(f"\n❌ 綜合測試執行失敗: {e}")
        return False

if __name__ == "__main__":
    # 運行綜合測試
    success = asyncio.run(main())
    exit(0 if success else 1)
