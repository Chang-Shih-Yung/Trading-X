#!/usr/bin/env python3
"""
🎯 Trading X - 第一階段回測整合測試
執行完整的基礎回測整合功能測試
測試完成後自動清理臨時檔案
"""

import asyncio
import logging
import sys
import json
from pathlib import Path
from datetime import datetime

# 設置項目路徑
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# 導入測試模組
from historical_data_extension import test_historical_data_extension
from multiframe_backtest_engine import test_multiframe_backtest
from phase5_integrated_validator import test_phase5_integration

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(project_root / 'phase1_backtest_integration_test.log')
    ]
)

logger = logging.getLogger(__name__)

class Phase1BacktestIntegrationTester:
    """第一階段回測整合測試器"""
    
    def __init__(self):
        self.test_results = {}
        self.temp_files = []
        self.start_time = datetime.now()
    
    async def run_complete_test_suite(self):
        """運行完整的測試套件"""
        logger.info("🚀 開始第一階段回測整合測試")
        logger.info("=" * 80)
        
        try:
            # 測試1: 歷史數據擴展功能
            logger.info("📊 測試1: 歷史數據擴展功能")
            await test_historical_data_extension()
            self.test_results['historical_data_extension'] = {
                'status': 'success',
                'message': '歷史數據擴展功能測試通過'
            }
            logger.info("✅ 測試1完成\n")
            
            # 測試2: 多時間框架回測引擎
            logger.info("📈 測試2: 多時間框架回測引擎")
            backtest_results = await test_multiframe_backtest()
            self.test_results['multiframe_backtest'] = {
                'status': 'success',
                'message': '多時間框架回測引擎測試通過',
                'data': backtest_results
            }
            
            # 記錄臨時檔案
            temp_file = project_root / "backtest_results_temp.json"
            if temp_file.exists():
                self.temp_files.append(temp_file)
            
            logger.info("✅ 測試2完成\n")
            
            # 測試3: Phase5整合驗證
            logger.info("🔍 測試3: Phase5整合驗證")
            phase5_results = await test_phase5_integration()
            self.test_results['phase5_integration'] = {
                'status': 'success',
                'message': 'Phase5整合驗證測試通過',
                'data': phase5_results
            }
            
            # 記錄臨時檔案
            temp_file = project_root / "phase5_integration_results_temp.json"
            if temp_file.exists():
                self.temp_files.append(temp_file)
            
            logger.info("✅ 測試3完成\n")
            
            # 生成最終報告
            await self._generate_final_report()
            
            # 清理臨時檔案
            await self._cleanup_temp_files()
            
            logger.info("🎉 第一階段回測整合測試全部完成")
            
        except Exception as e:
            logger.error(f"❌ 測試過程中發生錯誤: {e}")
            self.test_results['error'] = str(e)
            
            # 即使發生錯誤也要清理臨時檔案
            await self._cleanup_temp_files()
            raise
    
    async def _generate_final_report(self):
        """生成最終測試報告"""
        logger.info("📋 生成最終測試報告")
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        report = {
            "test_suite": "Phase1 回測整合測試",
            "version": "1.0.0",
            "test_time": {
                "start": self.start_time.isoformat(),
                "end": end_time.isoformat(),
                "duration_seconds": duration.total_seconds()
            },
            "test_results": self.test_results,
            "summary": self._generate_test_summary(),
            "next_steps": self._generate_next_steps()
        }
        
        # 保存最終報告
        report_file = project_root / f"Phase1_Backtest_Integration_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📁 最終報告已保存: {report_file}")
        
        # 輸出摘要到控制台
        self._print_test_summary(report)
    
    def _generate_test_summary(self):
        """生成測試摘要"""
        successful_tests = sum(1 for result in self.test_results.values() 
                             if isinstance(result, dict) and result.get('status') == 'success')
        total_tests = len([k for k in self.test_results.keys() if k != 'error'])
        
        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "overall_status": "PASS" if successful_tests == total_tests else "FAIL"
        }
        
        # 提取關鍵指標
        if 'multiframe_backtest' in self.test_results and self.test_results['multiframe_backtest'].get('data'):
            backtest_data = self.test_results['multiframe_backtest']['data']
            if 'backtest_summary' in backtest_data:
                backtest_summary = backtest_data['backtest_summary']
                summary['backtest_metrics'] = {
                    "total_backtests": backtest_summary.get('total_backtests', 0),
                    "successful_backtests": backtest_summary.get('successful_backtests', 0),
                    "overall_performance": backtest_summary.get('overall_performance', {})
                }
        
        if 'phase5_integration' in self.test_results and self.test_results['phase5_integration'].get('data'):
            phase5_data = self.test_results['phase5_integration']['data']
            if 'results' in phase5_data and 'phase5_validation' in phase5_data['results']:
                phase5_validation = phase5_data['results']['phase5_validation']
                excellent_count = sum(1 for p in phase5_validation.get('performance_classification', {}).values() 
                                    if p.get('classification') == 'excellent')
                total_count = len(phase5_validation.get('performance_classification', {}))
                summary['phase5_metrics'] = {
                    "total_validations": total_count,
                    "excellent_performances": excellent_count,
                    "excellence_rate": excellent_count / total_count if total_count > 0 else 0
                }
        
        return summary
    
    def _generate_next_steps(self):
        """生成下一步建議"""
        next_steps = []
        
        # 基於測試結果生成建議
        if self.test_results.get('historical_data_extension', {}).get('status') == 'success':
            next_steps.append("✅ 歷史數據擴展功能已就緒，可進入第二階段開發")
        
        if self.test_results.get('multiframe_backtest', {}).get('status') == 'success':
            next_steps.append("✅ 多時間框架回測引擎運行正常，可開始智能參數調整開發")
        
        if self.test_results.get('phase5_integration', {}).get('status') == 'success':
            next_steps.append("✅ Phase5整合成功，可開始TradingView風格報告開發")
        
        # 第二階段建議
        next_steps.extend([
            "🔧 第二階段: 實現智能參數調整",
            "📊 第二階段: 實現TradingView風格報告生成",
            "🎯 第二階段: 實現月度自動參數優化",
            "📈 第二階段: 實現市場制度自適應調整"
        ])
        
        return next_steps
    
    def _print_test_summary(self, report):
        """輸出測試摘要到控制台"""
        summary = report['summary']
        
        logger.info("=" * 80)
        logger.info("📋 第一階段回測整合測試總結")
        logger.info("=" * 80)
        logger.info(f"🕐 測試時間: {report['test_time']['duration_seconds']:.1f} 秒")
        logger.info(f"📊 測試結果: {summary['successful_tests']}/{summary['total_tests']} 通過")
        logger.info(f"🎯 成功率: {summary['success_rate']:.1%}")
        logger.info(f"🏆 整體狀態: {summary['overall_status']}")
        
        if 'backtest_metrics' in summary:
            metrics = summary['backtest_metrics']
            logger.info(f"📈 回測成功: {metrics['successful_backtests']}/{metrics['total_backtests']}")
            
            if 'overall_performance' in metrics and metrics['overall_performance']:
                perf = metrics['overall_performance']
                logger.info(f"📊 平均勝率: {perf.get('avg_win_rate', 0):.1%}")
                logger.info(f"💰 平均收益: {perf.get('avg_return', 0):.3%}")
        
        if 'phase5_metrics' in summary:
            metrics = summary['phase5_metrics']
            logger.info(f"🏆 優秀表現: {metrics['excellent_performances']}/{metrics['total_validations']}")
            logger.info(f"✨ 優秀率: {metrics['excellence_rate']:.1%}")
        
        logger.info("\n💡 下一步建議:")
        for i, step in enumerate(report['next_steps'][:5], 1):
            logger.info(f"   {i}. {step}")
        
        logger.info("=" * 80)
    
    async def _cleanup_temp_files(self):
        """清理臨時檔案"""
        logger.info("🧹 清理臨時檔案")
        
        cleaned_count = 0
        for temp_file in self.temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
                    cleaned_count += 1
                    logger.info(f"🗑️ 已刪除: {temp_file.name}")
            except Exception as e:
                logger.warning(f"⚠️ 無法刪除 {temp_file.name}: {e}")
        
        # 清理日誌檔案 (可選)
        log_file = project_root / 'phase1_backtest_integration_test.log'
        try:
            if log_file.exists():
                log_file.unlink()
                cleaned_count += 1
                logger.info(f"🗑️ 已刪除: {log_file.name}")
        except Exception as e:
            logger.warning(f"⚠️ 無法刪除日誌檔案: {e}")
        
        logger.info(f"✅ 清理完成，共刪除 {cleaned_count} 個臨時檔案")


async def main():
    """主測試函數"""
    tester = Phase1BacktestIntegrationTester()
    await tester.run_complete_test_suite()


if __name__ == "__main__":
    asyncio.run(main())
