"""
🎯 Trading-X 系統啟動器
==================

重新組織後的 Trading-X 系統統一啟動入口
支援分模組啟動和完整系統啟動
"""

import asyncio
import logging
import sys
import argparse
from pathlib import Path
from datetime import datetime

# 添加所有模組路徑
current_dir = Path(__file__).parent
sys.path.extend([
    str(current_dir / "core"),
    str(current_dir / "strategies"),
    str(current_dir / "indicators"), 
    str(current_dir / "monitoring"),
    str(current_dir / "utils"),
    str(current_dir.parent / "app" / "services")
])

from config import *
from monitoring.real_time_unified_monitoring_manager import unified_monitoring_manager
from monitoring.monitoring_api import create_monitoring_app
import uvicorn

# 設定日誌
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(current_dir / 'trading_x.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TradingXLauncher:
    """Trading-X 系統啟動器"""
    
    def __init__(self):
        self.monitoring_manager = None
        self.monitoring_app = None
        
    async def start_monitoring_system(self):
        """啟動監控系統"""
        try:
            logger.info("🚀 啟動 Trading-X 監控系統...")
            
            # 初始化監控管理器
            self.monitoring_manager = unified_monitoring_manager
            await self.monitoring_manager.start()
            
            logger.info("✅ 監控系統啟動成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 監控系統啟動失敗: {e}")
            return False
    
    async def start_api_server(self):
        """啟動 API 服務器"""
        try:
            logger.info("🌐 啟動 Trading-X API 服務器...")
            
            # 創建監控 API 應用
            self.monitoring_app = create_monitoring_app()
            
            # 配置 uvicorn
            config = uvicorn.Config(
                self.monitoring_app,
                host=MONITORING_HOST,
                port=MONITORING_PORT,
                log_level=LOG_LEVEL.lower(),
                reload=False
            )
            
            server = uvicorn.Server(config)
            
            logger.info(f"✅ API 服務器啟動在 http://{MONITORING_HOST}:{MONITORING_PORT}")
            await server.serve()
            
        except Exception as e:
            logger.error(f"❌ API 服務器啟動失敗: {e}")
    
    async def run_full_system(self):
        """運行完整系統"""
        logger.info(f"🎯 啟動 {SYSTEM_NAME} v{SYSTEM_VERSION}")
        logger.info(f"📅 最後更新: {LAST_UPDATED}")
        logger.info("=" * 50)
        
        # 啟動監控系統
        monitoring_success = await self.start_monitoring_system()
        if not monitoring_success:
            logger.error("無法啟動監控系統，停止執行")
            return
        
        # 啟動 API 服務器
        await self.start_api_server()
    
    async def run_monitoring_only(self):
        """僅運行監控系統"""
        logger.info("🔍 啟動純監控模式...")
        
        monitoring_success = await self.start_monitoring_system()
        if monitoring_success:
            logger.info("監控系統運行中...")
            # 保持運行
            try:
                while True:
                    await asyncio.sleep(60)
                    if self.monitoring_manager:
                        stats = await self.monitoring_manager.get_system_stats()
                        logger.info(f"系統狀態: {stats}")
            except KeyboardInterrupt:
                logger.info("收到停止信號，關閉監控系統...")
                if self.monitoring_manager:
                    await self.monitoring_manager.stop()
    
    async def run_api_only(self):
        """僅運行 API 服務器"""
        logger.info("🌐 啟動純 API 模式...")
        await self.start_api_server()
    
    async def test_system(self):
        """測試系統各組件"""
        logger.info("🧪 開始系統測試...")
        
        test_results = {}
        
        # 測試核心組件
        try:
            from core.binance_data_connector import binance_connector
            async with binance_connector as connector:
                test_data = await connector.get_comprehensive_market_data("BTCUSDT")
                test_results["binance_connector"] = "✅ 正常" if test_data else "❌ 失敗"
        except Exception as e:
            test_results["binance_connector"] = f"❌ 錯誤: {e}"
        
        # 測試策略組件
        try:
            from strategies.phase1.phase1b_volatility_adaptation import VolatilityAdaptationEngine
            engine = VolatilityAdaptationEngine()
            test_results["phase1b_volatility"] = "✅ 正常"
        except Exception as e:
            test_results["phase1b_volatility"] = f"❌ 錯誤: {e}"
        
        # 測試指標組件
        try:
            from indicators.pandas_ta_indicators import TechnicalIndicatorEngine
            indicator_engine = TechnicalIndicatorEngine()
            test_results["technical_indicators"] = "✅ 正常"
        except Exception as e:
            test_results["technical_indicators"] = f"❌ 錯誤: {e}"
        
        # 顯示測試結果
        logger.info("🧪 系統測試結果:")
        for component, status in test_results.items():
            logger.info(f"  {component}: {status}")
        
        return test_results

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="Trading-X 系統啟動器")
    parser.add_argument("--mode", choices=["full", "monitoring", "api", "test"], 
                       default="full", help="啟動模式")
    
    args = parser.parse_args()
    
    launcher = TradingXLauncher()
    
    try:
        if args.mode == "full":
            asyncio.run(launcher.run_full_system())
        elif args.mode == "monitoring":
            asyncio.run(launcher.run_monitoring_only())
        elif args.mode == "api":
            asyncio.run(launcher.run_api_only())
        elif args.mode == "test":
            asyncio.run(launcher.test_system())
    except KeyboardInterrupt:
        logger.info("👋 Trading-X 系統已停止")
    except Exception as e:
        logger.error(f"💥 系統錯誤: {e}")

if __name__ == "__main__":
    main()
