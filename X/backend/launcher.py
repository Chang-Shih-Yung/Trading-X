#!/usr/bin/env python3
"""
🚀 Trading-X 後端系統啟動器
=============================

統一啟動點 - 整合四階段完整流水線系統
支援多種運行模式：測試、監控、診斷、生產環境
"""

import asyncio
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import json

# 設置項目路徑 - 使用 X 資料夾作為根目錄
current_dir = Path(__file__).parent
project_root = current_dir.parent  # X 資料夾
sys.path.append(str(project_root))
sys.path.append(str(current_dir))  # backend 資料夾

from backend.trading_x_backend_integrator import backend_integrator

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/trading_x_backend_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TradingXLauncher:
    """Trading-X 後端系統啟動器"""
    
    def __init__(self):
        self.integrator = backend_integrator
        self.default_symbols = [
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "DOTUSDT",
            "XRPUSDT", "LINKUSDT", "LTCUSDT", "BCHUSDT", "UNIUSDT"
        ]
    
    async def test_mode(self, symbols: List[str] = None) -> Dict[str, Any]:
        """測試模式 - 驗證系統功能"""
        try:
            logger.info("🧪 ===== Trading-X 測試模式啟動 =====")
            
            # 使用預設或自訂標的
            test_symbols = symbols or self.default_symbols[:3]  # 測試模式使用前3個
            
            logger.info(f"🎯 測試標的: {test_symbols}")
            
            # 1. 系統診斷
            logger.info("🔍 步驟 1: 運行系統診斷...")
            diagnostic_results = await self.integrator.run_system_diagnostics()
            
            logger.info(f"🔍 診斷結果: {diagnostic_results['overall_status']}")
            if diagnostic_results.get('recommendations'):
                for rec in diagnostic_results['recommendations']:
                    logger.info(f"💡 建議: {rec}")
            
            # 2. 單一標的測試
            logger.info("🧪 步驟 2: 單一標的完整流水線測試...")
            single_symbol_result = await self.integrator.process_symbol_pipeline(test_symbols[0])
            
            logger.info(f"📊 單一標的測試結果:")
            logger.info(f"   - 標的: {single_symbol_result.symbol}")
            logger.info(f"   - 成功率: {single_symbol_result.success_rate:.1%}")
            logger.info(f"   - 處理時間: {single_symbol_result.processing_time:.2f}s")
            logger.info(f"   - Phase1 候選者: {len(single_symbol_result.phase1_candidates)}")
            logger.info(f"   - Phase2 評估: {len(single_symbol_result.phase2_evaluations)}")
            logger.info(f"   - Phase3 決策: {len(single_symbol_result.phase3_decisions)}")
            logger.info(f"   - Phase4 輸出: {len(single_symbol_result.phase4_outputs)}")
            
            if single_symbol_result.error_messages:
                logger.warning(f"⚠️ 錯誤訊息: {single_symbol_result.error_messages}")
            
            # 3. 多標的並行測試
            logger.info("🔄 步驟 3: 多標的並行處理測試...")
            multi_symbol_results = await self.integrator.process_multiple_symbols(test_symbols)
            
            successful_results = [r for r in multi_symbol_results if r.success_rate > 0.5]
            logger.info(f"📈 並行測試結果: {len(successful_results)}/{len(multi_symbol_results)} 成功")
            
            # 4. 系統狀態檢查
            logger.info("📊 步驟 4: 系統狀態檢查...")
            system_status = self.integrator.get_system_status()
            
            logger.info(f"⚙️ 系統效率: {system_status['performance_metrics']['system_efficiency']:.1%}")
            logger.info(f"🎯 各階段成功率:")
            for phase, rate in system_status['overall_stats']['phase_success_rates'].items():
                logger.info(f"   - {phase}: {rate:.1%}")
            
            # 5. 動態特性驗證
            dynamic_metrics = system_status.get('dynamic_adaptation', {})
            logger.info(f"🔄 動態適應率: {dynamic_metrics.get('adaptation_success_rate', 0):.1%}")
            
            dynamic_features = dynamic_metrics.get('dynamic_feature_usage', {})
            if dynamic_features.get('features_found'):
                logger.info(f"✅ 檢測到動態特性: {dynamic_features['features_found']}")
            else:
                logger.warning("⚠️ 未檢測到足夠的動態特性")
            
            # 測試總結
            test_summary = {
                "mode": "test",
                "start_time": datetime.now().isoformat(),
                "test_symbols": test_symbols,
                "diagnostic_status": diagnostic_results['overall_status'],
                "single_symbol_success": single_symbol_result.success_rate > 0.5,
                "multi_symbol_success_rate": len(successful_results) / len(multi_symbol_results) if multi_symbol_results else 0,
                "system_efficiency": system_status['performance_metrics']['system_efficiency'],
                "dynamic_adaptation_rate": dynamic_metrics.get('adaptation_success_rate', 0),
                "overall_test_status": "PASSED" if (
                    diagnostic_results['overall_status'] in ['healthy', 'degraded'] and
                    single_symbol_result.success_rate > 0.5 and
                    len(successful_results) > len(multi_symbol_results) // 2
                ) else "FAILED"
            }
            
            logger.info("✅ 測試完成")
            
            return test_summary
            
        except Exception as e:
            logger.error(f"❌ 測試模式失敗: {e}")
            return {"mode": "test", "status": "ERROR", "error": str(e)}
    
    async def monitoring_mode(self, symbols: List[str] = None, interval: int = 5) -> None:
        """監控模式 - 持續監控交易信號"""
        try:
            logger.info("📡 ===== Trading-X 監控模式啟動 =====")
            
            monitor_symbols = symbols or self.default_symbols
            logger.info(f"📊 監控標的: {monitor_symbols}")
            logger.info(f"⏰ 監控間隔: {interval} 分鐘")
            
            # 啟動持續監控
            await self.integrator.start_continuous_monitoring(monitor_symbols, interval)
            
        except KeyboardInterrupt:
            logger.info("⚡ 接收到中斷信號，正在停止監控...")
            self.integrator.stop_continuous_monitoring()
            logger.info("⏹️ 監控模式已停止")
        except Exception as e:
            logger.error(f"❌ 監控模式失敗: {e}")
    
    async def diagnostic_mode(self) -> Dict[str, Any]:
        """診斷模式 - 系統健康檢查"""
        try:
            logger.info("🔍 ===== Trading-X 診斷模式啟動 =====")
            
            # 執行完整診斷
            diagnostic_results = await self.integrator.run_system_diagnostics()
            
            # 輸出詳細診斷報告
            logger.info(f"🏥 系統整體狀態: {diagnostic_results['overall_status']}")
            logger.info(f"✅ 通過測試: {diagnostic_results['passed_tests']}/{diagnostic_results['total_tests']}")
            
            logger.info("📋 各項測試結果:")
            for test_name, result in diagnostic_results['test_results'].items():
                status_emoji = "✅" if result['status'] == 'passed' else "❌" if result['status'] == 'failed' else "⚠️"
                logger.info(f"   {status_emoji} {test_name}: {result['status']}")
                if result['status'] == 'error':
                    logger.error(f"      錯誤: {result.get('error', 'Unknown error')}")
            
            if diagnostic_results.get('recommendations'):
                logger.info("💡 系統建議:")
                for rec in diagnostic_results['recommendations']:
                    logger.info(f"   {rec}")
            
            # 系統狀態詳情
            system_status = self.integrator.get_system_status()
            logger.info("📊 系統性能指標:")
            logger.info(f"   - 總體成功率: {system_status['performance_metrics']['total_pipeline_success_rate']:.1%}")
            logger.info(f"   - 系統效率: {system_status['performance_metrics']['system_efficiency']:.1%}")
            logger.info(f"   - 平均處理時間: {system_status['performance_metrics']['average_processing_time']:.2f}s")
            
            logger.info("🎯 各階段表現:")
            for phase, rate in system_status['overall_stats']['phase_success_rates'].items():
                logger.info(f"   - {phase}: {rate:.1%}")
            
            logger.info("🔍 診斷完成")
            return diagnostic_results
            
        except Exception as e:
            logger.error(f"❌ 診斷模式失敗: {e}")
            return {"status": "ERROR", "error": str(e)}
    
    async def production_mode(self, symbols: List[str] = None) -> None:
        """生產模式 - 正式運行環境"""
        try:
            logger.info("🚀 ===== Trading-X 生產模式啟動 =====")
            
            # 生產環境預檢查
            logger.info("🔒 步驟 1: 生產環境預檢查...")
            diagnostic_results = await self.integrator.run_system_diagnostics()
            
            if diagnostic_results['overall_status'] not in ['healthy', 'degraded']:
                logger.error("❌ 系統診斷未通過，無法啟動生產模式")
                logger.error("🔧 請先修復系統問題後再嘗試啟動")
                return
            
            # 設置生產參數
            production_symbols = symbols or self.default_symbols
            monitoring_interval = 3  # 生產環境使用更短的間隔
            
            logger.info(f"📈 生產標的: {production_symbols}")
            logger.info(f"⚡ 生產監控間隔: {monitoring_interval} 分鐘")
            
            # 記錄啟動資訊
            startup_info = {
                "mode": "production",
                "start_time": datetime.now().isoformat(),
                "symbols": production_symbols,
                "interval": monitoring_interval,
                "system_status": diagnostic_results['overall_status']
            }
            
            # 保存啟動記錄
            with open("logs/production_startup.json", "w") as f:
                json.dump(startup_info, f, indent=2)
            
            logger.info("✅ 生產環境檢查通過，開始正式運行...")
            
            # 啟動生產監控
            await self.integrator.start_continuous_monitoring(production_symbols, monitoring_interval)
            
        except KeyboardInterrupt:
            logger.info("⚡ 接收到中斷信號，正在安全停止生產系統...")
            self.integrator.stop_continuous_monitoring()
            
            # 記錄停止資訊
            shutdown_info = {
                "shutdown_time": datetime.now().isoformat(),
                "reason": "user_interrupt",
                "status": "clean_shutdown"
            }
            
            with open("logs/production_shutdown.json", "w") as f:
                json.dump(shutdown_info, f, indent=2)
            
            logger.info("✅ 生產系統已安全停止")
            
        except Exception as e:
            logger.error(f"❌ 生產模式失敗: {e}")
            
            # 記錄錯誤
            error_info = {
                "error_time": datetime.now().isoformat(),
                "error": str(e),
                "status": "error_shutdown"
            }
            
            with open("logs/production_error.json", "w") as f:
                json.dump(error_info, f, indent=2)
    
    async def single_symbol_mode(self, symbol: str) -> Dict[str, Any]:
        """單一標的模式 - 測試特定標的"""
        try:
            logger.info(f"🎯 ===== 單一標的模式: {symbol} =====")
            
            # 處理單一標的
            result = await self.integrator.process_symbol_pipeline(symbol)
            
            # 詳細輸出結果
            logger.info(f"📊 處理結果:")
            logger.info(f"   標的: {result.symbol}")
            logger.info(f"   成功率: {result.success_rate:.1%}")
            logger.info(f"   處理時間: {result.processing_time:.2f}s")
            logger.info(f"   階段詳情:")
            logger.info(f"     - Phase1 (信號生成): {len(result.phase1_candidates)} 候選者")
            logger.info(f"     - Phase2 (前處理): {len(result.phase2_evaluations)} 評估")
            logger.info(f"     - Phase3 (決策): {len(result.phase3_decisions)} 決策")
            logger.info(f"     - Phase4 (輸出): {len(result.phase4_outputs)} 輸出")
            
            if result.error_messages:
                logger.warning("⚠️ 錯誤訊息:")
                for error in result.error_messages:
                    logger.warning(f"   - {error}")
            
            # 返回結構化結果
            return {
                "symbol": result.symbol,
                "success_rate": result.success_rate,
                "processing_time": result.processing_time,
                "phase_results": {
                    "phase1_candidates": len(result.phase1_candidates),
                    "phase2_evaluations": len(result.phase2_evaluations),
                    "phase3_decisions": len(result.phase3_decisions),
                    "phase4_outputs": len(result.phase4_outputs)
                },
                "errors": result.error_messages,
                "timestamp": result.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 單一標的模式失敗: {e}")
            return {"symbol": symbol, "status": "ERROR", "error": str(e)}

async def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="Trading-X 後端系統啟動器")
    parser.add_argument("--mode", choices=["test", "monitor", "diagnostic", "production", "single"], 
                       default="test", help="運行模式")
    parser.add_argument("--symbols", nargs="+", help="自訂交易標的")
    parser.add_argument("--symbol", help="單一標的模式的標的")
    parser.add_argument("--interval", type=int, default=5, help="監控間隔（分鐘）")
    parser.add_argument("--verbose", "-v", action="store_true", help="詳細輸出")
    
    args = parser.parse_args()
    
    # 設置日誌級別
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 創建啟動器
    launcher = TradingXLauncher()
    
    # 確保日誌目錄存在
    Path("logs").mkdir(exist_ok=True)
    
    try:
        if args.mode == "test":
            result = await launcher.test_mode(args.symbols)
            print(f"\n🏆 測試結果: {result['overall_test_status']}")
            
        elif args.mode == "monitor":
            await launcher.monitoring_mode(args.symbols, args.interval)
            
        elif args.mode == "diagnostic":
            result = await launcher.diagnostic_mode()
            print(f"\n🏥 診斷狀態: {result['overall_status']}")
            
        elif args.mode == "production":
            await launcher.production_mode(args.symbols)
            
        elif args.mode == "single":
            if not args.symbol:
                print("❌ 單一標的模式需要指定 --symbol 參數")
                return
            result = await launcher.single_symbol_mode(args.symbol)
            print(f"\n🎯 {args.symbol} 處理成功率: {result.get('success_rate', 0):.1%}")
            
    except KeyboardInterrupt:
        print("\n⚡ 接收到中斷信號，正在退出...")
    except Exception as e:
        print(f"\n❌ 系統錯誤: {e}")
        logger.error(f"系統錯誤: {e}")

if __name__ == "__main__":
    asyncio.run(main())
