#!/usr/bin/env python3
"""
🎯 Trading X - 自動參數優化排程器
每週自動執行參數優化，無人值守運行
"""

import asyncio
import schedule
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AutomaticOptimizationScheduler:
    """自動優化排程器"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.last_optimization = None
        self.optimization_results = []
        
    def _setup_logging(self):
        """設置日誌"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('weekly_optimization.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def start_scheduler(self):
        """啟動排程器"""
        self.logger.info("🚀 啟動每週自動參數優化排程器...")
        
        # 每週日凌晨 2:00 執行優化
        schedule.every().sunday.at("02:00").do(self._run_optimization_job)
        
        # 每天檢查系統狀態
        schedule.every().day.at("08:00").do(self._daily_health_check)
        
        self.logger.info("📅 排程設置完成:")
        self.logger.info("   • 每週日 02:00 - 參數優化")
        self.logger.info("   • 每天 08:00 - 系統健康檢查")
        
        # 主循環
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分鐘檢查一次
    
    def _run_optimization_job(self):
        """執行優化任務"""
        self.logger.info("⏰ 觸發每週參數優化任務...")
        
        try:
            # 異步執行優化
            result = asyncio.run(self._execute_weekly_optimization())
            
            # 記錄結果
            self.last_optimization = datetime.now()
            self.optimization_results.append(result)
            
            # 發送報告
            self._send_optimization_report(result)
            
            self.logger.info("✅ 週週參數優化完成")
            
        except Exception as e:
            self.logger.error(f"❌ 優化任務失敗: {e}")
            self._send_error_alert(str(e))
    
    async def _execute_weekly_optimization(self) -> Dict[str, Any]:
        """執行實際的優化邏輯"""
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent))
        from weekly_parameter_optimizer import run_weekly_optimization  # type: ignore
        
        self.logger.info("🔧 開始執行參數優化...")
        result = await run_weekly_optimization()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'optimization_result': result,
            'execution_time_minutes': result.get('optimization_time', 0) / 60
        }
    
    def _daily_health_check(self):
        """每日健康檢查"""
        self.logger.info("🏥 執行每日系統健康檢查...")
        
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'scheduler_running': True,
            'last_optimization': self.last_optimization.isoformat() if self.last_optimization else None,
            'total_optimizations': len(self.optimization_results)
        }
        
        # 檢查是否超過 7 天沒有優化
        if self.last_optimization:
            days_since_last = (datetime.now() - self.last_optimization).days
            if days_since_last > 7:
                self.logger.warning(f"⚠️  超過 {days_since_last} 天未執行優化")
                health_status['warning'] = f'超過 {days_since_last} 天未執行優化'
        
        self.logger.info(f"✅ 健康檢查完成: {json.dumps(health_status, indent=2)}")
    
    def _send_optimization_report(self, result: Dict[str, Any]):
        """發送優化報告"""
        try:
            report = self._generate_report(result)
            self.logger.info("📧 優化報告:")
            self.logger.info(report)
            
            # 這裡可以添加郵件發送邏輯
            # self._send_email("每週參數優化報告", report)
            
        except Exception as e:
            self.logger.error(f"❌ 報告生成失敗: {e}")
    
    def _generate_report(self, result: Dict[str, Any]) -> str:
        """生成優化報告"""
        optimization_result = result.get('optimization_result', {})
        status = optimization_result.get('status', 'unknown')
        
        if status == 'success':
            old_perf = optimization_result.get('old_performance', {})
            new_perf = optimization_result.get('new_performance', {})
            
            report = f"""
📊 Trading X 每週參數優化報告
====================================

⏰ 執行時間: {result.get('timestamp')}
🕐 優化耗時: {result.get('execution_time_minutes', 0):.1f} 分鐘

✅ 優化狀態: 成功

📈 性能改善:
   勝率: {old_perf.get('win_rate', 0):.2%} → {new_perf.get('win_rate', 0):.2%}
   盈虧比: {old_perf.get('avg_pnl_ratio', 0):.3f} → {new_perf.get('avg_pnl_ratio', 0):.3f}
   夏普比率: {old_perf.get('sharpe_ratio', 0):.3f} → {new_perf.get('sharpe_ratio', 0):.3f}

🔧 參數調整:
   信心度閾值: {optimization_result.get('old_parameters', {}).get('confidence_threshold', 0):.3f} → {optimization_result.get('new_parameters', {}).get('confidence_threshold', 0):.3f}
   價格變化閾值: {optimization_result.get('old_parameters', {}).get('price_change_threshold', 0):.4f} → {optimization_result.get('new_parameters', {}).get('price_change_threshold', 0):.4f}
   成交量變化閾值: {optimization_result.get('old_parameters', {}).get('volume_change_threshold', 0):.1f} → {optimization_result.get('new_parameters', {}).get('volume_change_threshold', 0):.1f}

🎯 目標達成度:
   勝率目標 (70%): {'✅' if new_perf.get('win_rate', 0) >= 0.70 else '❌'}
   盈虧比目標 (1.5): {'✅' if new_perf.get('avg_pnl_ratio', 0) >= 1.5 else '❌'}
   夏普比率目標 (1.0): {'✅' if new_perf.get('sharpe_ratio', 0) >= 1.0 else '❌'}
"""
        elif status == 'skip':
            report = f"""
📊 Trading X 每週參數優化報告
====================================

⏰ 執行時間: {result.get('timestamp')}

✅ 優化狀態: 跳過優化
💡 原因: {optimization_result.get('reason', '未知')}

當前性能已達標，無需調整參數。
"""
        else:
            report = f"""
📊 Trading X 每週參數優化報告
====================================

⏰ 執行時間: {result.get('timestamp')}

❌ 優化狀態: {status}
💡 詳情: {optimization_result.get('reason', optimization_result.get('error', '未知錯誤'))}
"""
        
        return report
    
    def _send_error_alert(self, error_message: str):
        """發送錯誤警報"""
        self.logger.error(f"🚨 系統錯誤警報: {error_message}")
        
        # 這裡可以添加郵件/Slack/Discord 通知
        alert = f"""
🚨 Trading X 參數優化系統錯誤

時間: {datetime.now().isoformat()}
錯誤: {error_message}

請檢查系統狀態並手動介入。
"""
        
        self.logger.error(alert)

def main():
    """主函數"""
    print("🎯 Trading X - 自動參數優化排程器")
    print("=" * 50)
    
    scheduler = AutomaticOptimizationScheduler()
    
    try:
        scheduler.start_scheduler()
    except KeyboardInterrupt:
        print("\n⏹️  用戶終止排程器")
    except Exception as e:
        print(f"\n💥 排程器錯誤: {e}")

if __name__ == "__main__":
    main()
