#!/usr/bin/env python3
"""
Trading X 量子決策系統 - 生產啟動器
整合區塊鏈即時數據流的量子決策引擎
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from pathlib import Path

# 確保正確的路徑
sys.path.append(str(Path(__file__).parent))

from .quantum_config_manager import get_config_manager
from .quantum_decision_optimizer import ProductionQuantumProcessor

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/quantum_decision_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class QuantumDecisionLauncher:
    """量子決策系統啟動器"""
    
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

    async def initialize_processor(self):
        """初始化量子決策處理器"""
        try:
            # 加載生產級配置
            config_manager = get_config_manager()
            
            if not config_manager.validate_config():
                raise ValueError("配置文件驗證失敗")
            
            config = config_manager.get_quantum_decision_config()
            
            self.processor = ProductionQuantumProcessor(config)
            await self.processor.initialize()
            
            logger.info("量子決策處理器初始化完成")
            logger.info(f"SPRT 參數: α={config.alpha}, β={config.beta}")
            logger.info(f"Kelly 倍數: {config.kelly_multiplier}")
            logger.info(f"最大倉位: {config.max_position_cap}")
            
        except Exception as e:
            logger.error(f"初始化處理器失敗: {e}")
            raise

    async def run_monitoring_loop(self):
        """運行監控循環"""
        monitor_interval = 60  # 每分鐘監控一次
        
        while self.running:
            try:
                # 監控系統狀態
                await self.monitor_system_health()
                
                # 等待下一次監控
                await asyncio.sleep(monitor_interval)
                
            except Exception as e:
                logger.error(f"監控循環錯誤: {e}")
                await asyncio.sleep(5)  # 短暫延遲後重試

    async def monitor_system_health(self):
        """監控系統健康狀態"""
        try:
            if not self.processor:
                return
            
            # 獲取量子引擎狀態
            state = self.processor.quantum_engine.get_current_state()
            
            # 檢查各項指標
            total_decisions = state['decision_stats']['total_decisions']
            buffer_size = state['buffer_size']
            
            # 監控信念狀態
            belief_entropy = self._calculate_entropy(state['belief_state'])
            
            # 監控制度識別
            regime_confidence = max(state['regime_probabilities']) if len(state['regime_probabilities']) > 0 else 0
            
            logger.info(f"系統健康檢查 - "
                       f"總決策數: {total_decisions}, "
                       f"緩衝區大小: {buffer_size}, "
                       f"信念熵: {belief_entropy:.3f}, "
                       f"制度信心: {regime_confidence:.3f}")
            
            # 警報檢查
            if belief_entropy > 2.0:
                logger.warning("信念狀態過於分散")
            
            if regime_confidence < 0.5:
                logger.warning("市場制度識別不明確")
                
            if buffer_size < 10:
                logger.warning("數據緩衝區過小，可能影響決策品質")
            
        except Exception as e:
            logger.error(f"健康監控失敗: {e}")

    def _calculate_entropy(self, belief_state: Dict[str, float]) -> float:
        """計算信念狀態熵值"""
        if not belief_state:
            return 0.0
        
        entropy = 0.0
        for prob in belief_state.values():
            if prob > 1e-10:
                entropy -= prob * math.log(prob)
        
        return entropy

    async def start(self):
        """啟動量子決策系統"""
        try:
            logger.info("=" * 80)
            logger.info("Trading X 量子決策系統啟動")
            logger.info("=" * 80)
            
            # 初始化處理器
            await self.initialize_processor()
            
            # 啟動處理器
            self.running = True
            await self.processor.start_processing()
            
            # 啟動監控任務
            monitoring_task = asyncio.create_task(self.run_monitoring_loop())
            
            logger.info("量子決策系統已完全啟動，開始處理區塊鏈數據流")
            
            # 等待關閉信號
            while self.running:
                await asyncio.sleep(1)
            
            # 優雅關閉
            logger.info("正在關閉量子決策系統...")
            monitoring_task.cancel()
            
            try:
                await monitoring_task
            except asyncio.CancelledError:
                pass
            
            logger.info("量子決策系統已安全關閉")
            
        except KeyboardInterrupt:
            logger.info("收到中斷信號，正在關閉...")
        except Exception as e:
            logger.error(f"系統運行錯誤: {e}")
            raise
        finally:
            self.running = False

async def main():
    """主函數"""
    try:
        # 創建日誌目錄
        Path("logs").mkdir(exist_ok=True)
        
        # 啟動量子決策系統
        launcher = QuantumDecisionLauncher()
        await launcher.start()
        
    except Exception as e:
        logger.error(f"系統啟動失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # 確保使用 asyncio.run() 運行
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("程序被用戶中斷")
    except Exception as e:
        logger.error(f"未處理的錯誤: {e}")
        sys.exit(1)
