#!/usr/bin/env python3
"""
Trading X 量子決策系統 - 生產級啟動器
基於 ChatGPT 優化的向量化計算引擎
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from pathlib import Path

# 導入優化後的量子系統
from quantum_decision_optimizer import ProductionQuantumConfig, ProductionQuantumEngine
from quantum_production_extension import TradingXQuantumProcessor

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/quantum_production_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ProductionQuantumLauncher:
    """生產級量子決策系統啟動器"""
    
    def __init__(self):
        self.processor = None
        self.running = False
        self.setup_signal_handlers()

    def setup_signal_handlers(self):
        """設置信號處理器"""
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

    def handle_shutdown(self, signum, frame):
        """處理關閉信號"""
        logger.info(f"收到關閉信號 {signum}，正在優雅關閉...")
        self.running = False

    async def initialize_system(self):
        """初始化量子決策系統"""
        try:
            logger.info("初始化 Trading X 量子決策系統...")
            
            # 創建生產級配置
            config = ProductionQuantumConfig(
                # 基礎風險參數
                alpha_base=0.008,
                beta_base=0.045,
                kelly_multiplier=0.2,
                max_single_position=0.12,
                
                # SPRT 參數
                sprt_alpha=0.03,
                sprt_beta=0.15,
                min_confidence=0.7,
                
                # 系統參數
                max_observations=1000,
                forgetting_factor=0.95,
                volatility_lookback=20,
                
                # 正確的七幣種配置
                primary_symbols=[
                    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT',
                    'XRPUSDT', 'DOGEUSDT', 'ADAUSDT'
                ]
            )
            
            logger.info(f"配置加載完成: 監控 {len(config.primary_symbols)} 個幣種")
            
            # 初始化處理器
            self.processor = TradingXQuantumProcessor(config)
            await self.processor.start_quantum_processing()
            
            logger.info("量子決策系統啟動成功 ✓")
            return True
            
        except Exception as e:
            logger.error(f"系統初始化失敗: {e}")
            return False

    async def run_monitoring_loop(self):
        """運行監控循環"""
        logger.info("啟動系統監控循環...")
        
        while self.running:
            try:
                # 獲取系統狀態
                status = self.processor.get_system_status()
                
                # 記錄關鍵指標
                engine_stats = status.get('quantum_engine_state', {}).get('execution_stats', {})
                
                if engine_stats:
                    logger.info(
                        f"系統狀態 - 觀測: {engine_stats.get('total_observations', 0)}, "
                        f"決策: {engine_stats.get('successful_decisions', 0)}, "
                        f"執行: {engine_stats.get('executed_trades', 0)}, "
                        f"佇列: {status.get('execution_queue_size', 0)}"
                    )
                
                # 檢查系統健康
                await self.check_system_health(status)
                
                # 等待下一次檢查
                await asyncio.sleep(30)  # 30秒檢查一次
                
            except Exception as e:
                logger.error(f"監控循環錯誤: {e}")
                await asyncio.sleep(5)

    async def check_system_health(self, status: dict):
        """檢查系統健康狀態"""
        try:
            # 檢查執行佇列
            queue_size = status.get('execution_queue_size', 0)
            if queue_size > 100:
                logger.warning(f"執行佇列積壓: {queue_size} 項")
            
            # 檢查數據品質
            data_quality = status.get('data_quality', {})
            for symbol, quality in data_quality.items():
                if quality < 0.8:
                    logger.warning(f"數據品質警告 {symbol}: {quality:.3f}")
            
            # 檢查性能指標
            performance = status.get('performance_metrics', {})
            if performance.get('avg_confidence', 0) < 0.5:
                logger.warning(f"平均信心度偏低: {performance.get('avg_confidence', 0):.3f}")
            
        except Exception as e:
            logger.error(f"健康檢查失敗: {e}")

    async def start(self):
        """啟動系統"""
        logger.info("="*80)
        logger.info("Trading X 量子決策系統 - 生產級版本")
        logger.info("基於 ChatGPT 優化的向量化計算引擎")
        logger.info("="*80)
        
        try:
            # 初始化系統
            if not await self.initialize_system():
                logger.error("系統初始化失敗，退出")
                return False
            
            # 設置運行標誌
            self.running = True
            
            # 啟動監控循環
            await self.run_monitoring_loop()
            
            logger.info("系統正常關閉")
            return True
            
        except Exception as e:
            logger.error(f"系統運行錯誤: {e}")
            return False
        finally:
            await self.cleanup()

    async def cleanup(self):
        """清理資源"""
        logger.info("清理系統資源...")
        try:
            if self.processor:
                # 停止處理器 (如果有清理方法)
                pass
            logger.info("資源清理完成")
        except Exception as e:
            logger.error(f"清理資源失敗: {e}")

async def main():
    """主函數"""
    launcher = ProductionQuantumLauncher()
    
    try:
        success = await launcher.start()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("用戶中斷，正在關閉...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"未處理的錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # 運行生產級量子決策系統
    asyncio.run(main())
