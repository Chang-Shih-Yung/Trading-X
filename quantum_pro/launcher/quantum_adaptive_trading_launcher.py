#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔮 Trading X 量子自適應交易系統啟動器
═══════════════════════════════════════════════

革命性量子驅動交易系統：
- 🌀 量子疊加態坍縮觸發
- 🔗 量子糾纏強度檢測  
- ⚛️ 海森堡不確定性管理
- 🕐 自適應間隔調整
- 🌌 量子場能量監控

完全替代固定週期系統，實現真正的量子物理驅動！
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from pathlib import Path

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'quantum_adaptive_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

# 導入量子系統
try:
    from quantum_adaptive_signal_engine import QuantumAdaptiveSignalEngine
    from regime_hmm_quantum import 即時幣安數據收集器, QUANTUM_ENTANGLED_COINS
    logger.info("✅ 量子自適應系統導入成功")
except ImportError as e:
    logger.error(f"❌ 量子系統導入失敗: {e}")
    sys.exit(1)

class QuantumAdaptiveTradingLauncher:
    """🔮 量子自適應交易系統啟動器"""
    
    def __init__(self):
        self.running = False
        self.quantum_engine = QuantumAdaptiveSignalEngine()
        self.data_collector = None
        
        # 量子糾纏幣種
        self.quantum_symbols = [f"{coin}USDT" for coin in QUANTUM_ENTANGLED_COINS]
        
        # 設置優雅退出
        signal.signal(signal.SIGINT, self._graceful_shutdown)
        signal.signal(signal.SIGTERM, self._graceful_shutdown)
        
    def _graceful_shutdown(self, signum, frame):
        """優雅退出"""
        logger.info(f"📴 收到關閉信號 {signum}，正在優雅關閉量子系統...")
        self.running = False
        sys.exit(0)
    
    async def initialize_quantum_systems(self):
        """初始化量子系統"""
        
        logger.info("🔮 初始化量子自適應交易系統...")
        logger.info("=" * 80)
        logger.info("🌌 突破性量子驅動架構：")
        logger.info("   ⚡ 量子狀態觸發 (替代固定30秒週期)")
        logger.info("   🔮 疊加態坍縮檢測")
        logger.info("   🌀 量子糾纏強度監控")
        logger.info("   ⚛️  海森堡不確定性管理")
        logger.info("   🕐 自適應間隔調整 (0.1-3600秒)")
        logger.info("=" * 80)
        
        try:
            # 1. 檢查量子模型
            await self._check_quantum_models()
            
            # 2. 初始化數據收集器
            self.data_collector = 即時幣安數據收集器(self.quantum_symbols)
            logger.info(f"✅ 數據收集器初始化完成 - 監控 {len(self.quantum_symbols)} 個量子糾纏幣種")
            
            # 3. 初始化量子自適應引擎
            self.quantum_engine.initialize_quantum_states(self.quantum_symbols)
            logger.info("✅ 量子自適應引擎初始化完成")
            
            logger.info("🚀 量子自適應系統初始化完成！")
            return True
            
        except Exception as e:
            logger.error(f"❌ 量子系統初始化失敗: {e}")
            return False
    
    async def _check_quantum_models(self):
        """檢查量子模型狀態"""
        
        models_dir = Path(__file__).parent.parent / "data" / "models"
        
        if not models_dir.exists():
            logger.warning("⚠️ 模型目錄不存在，將自動創建")
            models_dir.mkdir(parents=True, exist_ok=True)
        
        # 檢查已訓練的模型
        model_files = list(models_dir.glob("quantum_model_*.pkl"))
        
        logger.info(f"📊 量子模型狀態檢查:")
        logger.info(f"   已訓練模型: {len(model_files)}/7")
        
        if len(model_files) == 0:
            logger.warning("⚠️ 未發現任何已訓練的量子模型")
            logger.warning("💡 建議先運行 quantum_model_trainer.py 進行訓練")
        elif len(model_files) < 7:
            logger.warning(f"⚠️ 部分量子模型缺失 ({len(model_files)}/7)")
            logger.warning("💡 建議重新訓練所有模型以確保一致性")
        else:
            logger.info("✅ 所有量子模型已就緒！")
        
        for model_file in model_files:
            coin = model_file.stem.replace("quantum_model_", "").upper()
            logger.info(f"   ✅ {coin} 量子模型: {model_file.name}")
    
    async def run_quantum_adaptive_loop(self):
        """運行量子自適應分析循環"""
        
        logger.info("🚀 啟動量子自適應分析循環...")
        logger.info("⚡ 告別固定週期，擁抱量子狀態驅動！")
        
        # 模擬信號處理器
        class QuantumSignalProcessor:
            async def generate_signal(self, symbol, market_data):
                return {
                    'symbol': symbol,
                    'signal': 'QUANTUM_DRIVEN',
                    'confidence': 0.85,
                    'quantum_state': 'superposition_collapse'
                }
        
        signal_processor = QuantumSignalProcessor()
        
        # 啟動量子驅動循環
        await self.quantum_engine.quantum_driven_analysis_loop(
            self.data_collector,
            signal_processor
        )
    
    async def run(self):
        """運行量子自適應交易系統"""
        
        try:
            logger.info("🔮 Trading X 量子自適應交易系統 v2.0")
            logger.info("=" * 80)
            logger.info("🌌 革命性突破：量子狀態驅動的交易系統")
            logger.info("⚡ 核心特色：零固定週期，純物理定律觸發")
            logger.info("🎯 技術優勢：自適應間隔，量子事件驅動")
            logger.info("=" * 80)
            
            # 初始化系統
            if not await self.initialize_quantum_systems():
                logger.error("❌ 系統初始化失敗")
                return
            
            self.running = True
            
            # 啟動數據收集
            data_task = asyncio.create_task(
                self.data_collector.啟動數據收集()
            )
            
            # 等待數據收集建立
            logger.info("⏳ 等待量子數據流建立...")
            await asyncio.sleep(5)
            
            # 啟動量子自適應循環
            quantum_task = asyncio.create_task(
                self.run_quantum_adaptive_loop()
            )
            
            # 等待任務完成
            await asyncio.gather(data_task, quantum_task, return_exceptions=True)
            
        except KeyboardInterrupt:
            logger.info("📴 收到中斷信號")
        except Exception as e:
            logger.error(f"❌ 量子系統運行錯誤: {e}")
        finally:
            await self.cleanup_resources()
    
    async def cleanup_resources(self):
        """清理系統資源"""
        
        logger.info("🧹 清理量子系統資源...")
        
        if self.data_collector:
            try:
                await asyncio.wait_for(
                    self.data_collector.停止數據收集(),
                    timeout=2.0
                )
            except asyncio.TimeoutError:
                logger.warning("⚠️ 數據收集器停止超時")
            except Exception as e:
                logger.error(f"❌ 停止數據收集器失敗: {e}")
        
        logger.info("✅ 量子系統資源清理完成")

async def main():
    """主函數"""
    
    launcher = QuantumAdaptiveTradingLauncher()
    await launcher.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 用戶中斷程序")
    except Exception as e:
        print(f"❌ 程序執行失敗: {e}")
    finally:
        print("👋 Trading X 量子自適應系統已退出")
