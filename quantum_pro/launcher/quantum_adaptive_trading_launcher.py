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

import numpy as np

# 設置日誌 - 只在直接運行時創建日誌檔案
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('quantum_adaptive_launcher.log', encoding='utf-8')
        ]
    )
else:
    # 當被導入時，只使用控制台輸出
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
logger = logging.getLogger(__name__)

# 導入量子系統
try:
    import sys
    from pathlib import Path

    # 添加項目根目錄到路徑
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    from quantum_pro.launcher.quantum_adaptive_signal_engine import (
        QuantumAdaptiveSignalEngine,
    )
    from quantum_pro.regime_hmm_quantum import QUANTUM_ENTANGLED_COINS, 即時幣安數據收集器
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
            logger.error("❌ 未發現任何已訓練的量子模型")
            logger.error("💡 必須先運行 quantum_model_trainer.py 進行訓練")
            logger.error("❌ 量子自適應系統禁止使用未訓練的模型")
            raise FileNotFoundError("缺少必要的量子模型檔案，請先執行模型訓練")
        elif len(model_files) < 7:
            logger.error(f"❌ 部分量子模型缺失 ({len(model_files)}/7)")
            logger.error("💡 必須重新訓練所有模型以確保一致性")
            logger.error("❌ 量子自適應系統要求完整的模型集合")
            raise FileNotFoundError(f"模型集合不完整，缺少 {7 - len(model_files)} 個模型")
        else:
            logger.info("✅ 所有量子模型已就緒！")
        
        for model_file in model_files:
            coin = model_file.stem.replace("quantum_model_", "").upper()
            logger.info(f"   ✅ {coin} 量子模型: {model_file.name}")
    
    async def run_quantum_adaptive_loop(self):
        """運行量子自適應分析循環"""
        
        logger.info("🚀 啟動量子自適應分析循環...")
        logger.info("⚡ 告別固定週期，擁抱量子狀態驅動！")
        
        # 🔮 真正的量子信號處理器 - 使用已訓練的量子模型
        signal_processor = await self._initialize_real_quantum_signal_processor()
        
        # 啟動量子驅動循環
        await self.quantum_engine.quantum_driven_analysis_loop(
            self.data_collector,
            signal_processor
        )
    
    async def _initialize_real_quantum_signal_processor(self):
        """初始化真正的量子信號處理器"""
        
        logger.info("🔮 初始化真正的量子信號處理器...")
        
        try:
            # 導入現有的量子計算系統
            from quantum_pro.regime_hmm_quantum import (
                QuantumUltimateFusionEngine,
                即時市場觀測,
            )
            
            class RealQuantumSignalProcessor:
                """真正的量子信號處理器 - 使用已有的量子計算系統"""
                
                def __init__(self):
                    # 初始化量子融合引擎
                    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 'DOGEUSDT', 'ADAUSDT']
                    self.quantum_fusion_engine = QuantumUltimateFusionEngine(symbols)
                    logger.info("✅ 量子融合引擎初始化完成")
                
                async def generate_signal(self, symbol, market_data):
                    """使用真正的量子計算生成信號"""
                    
                    try:
                        # 將市場數據轉換為即時市場觀測
                        observation = self._convert_to_observation(symbol, market_data)
                        
                        # 🔮 使用真正的量子計算
                        quantum_result = self.quantum_fusion_engine.calculate_quantum_signal(observation)
                        
                        # 轉換為統一的信號格式
                        signal = self._convert_quantum_result_to_signal(symbol, quantum_result)
                        
                        logger.info(f"🔮 {symbol} 量子計算完成: {signal['signal']} (信心度: {signal['confidence']:.3f})")
                        return signal
                        
                    except Exception as e:
                        logger.error(f"❌ {symbol} 量子計算失敗: {e}")
                        logger.error("❌ 量子自適應系統必須使用訓練好的模型，嚴格禁止任何降級模式")
                        raise RuntimeError(f"量子計算失敗，系統不允許降級運行: {e}")
                
                def _convert_to_observation(self, symbol, market_data):
                    """將市場數據轉換為即時市場觀測"""
                    
                    # 創建即時市場觀測對象 - 使用正確的中文參數名
                    observation = 即時市場觀測(
                        時間戳=datetime.now(),
                        交易對=symbol,
                        價格=market_data.get('current_price', 0.0),
                        成交量=market_data.get('volume', 0.0),
                        收益率=market_data.get('price_change_percent', 0.0) / 100.0,
                        已實現波動率=market_data.get('volatility', 0.02),
                        動量斜率=market_data.get('momentum', 0.0),
                        最佳買價=market_data.get('current_price', 0.0) * 0.9995,  # 模擬買價
                        最佳賣價=market_data.get('current_price', 0.0) * 1.0005,  # 模擬賣價
                        買賣價差=market_data.get('current_price', 0.0) * 0.001,  # 模擬價差
                        訂單簿壓力=0.0,  # 預設值
                        主動買入比率=0.5,  # 預設值
                        大單流入率=0.0,  # 預設值
                        RSI_14=market_data.get('rsi', 50.0),
                        布林帶位置=market_data.get('bb_position', 0.5)
                    )
                    
                    return observation
                
                def _convert_quantum_result_to_signal(self, symbol, quantum_result):
                    """將量子計算結果轉換為標準信號格式"""
                    
                    # 提取量子計算結果
                    predicted_action = quantum_result['predicted_action']
                    quantum_confidence = quantum_result['quantum_confidence']
                    quantum_fidelity = quantum_result['quantum_fidelity']
                    signal_strength = quantum_result['signal_strength']
                    probabilities = quantum_result['probabilities']
                    
                    # 計算最終信心度（結合量子信心度和保真度）
                    final_confidence = min(quantum_confidence * quantum_fidelity, 0.99)
                    
                    # 構建信號
                    signal = {
                        'symbol': symbol,
                        'signal': predicted_action,
                        'confidence': float(final_confidence),
                        'signal_strength': float(signal_strength),
                        'quantum_state': 'real_quantum_regime_detection',
                        'probabilities': {
                            'bear': float(probabilities[0]),
                            'side': float(probabilities[1]),
                            'bull': float(probabilities[2])
                        },
                        'quantum_metrics': {
                            'quantum_confidence': float(quantum_confidence),
                            'quantum_fidelity': float(quantum_fidelity),
                            'risk_reward_ratio': float(quantum_result['risk_reward_ratio'])
                        },
                        'quantum_backend': 'regime_quantum_detector',
                        'model_status': 'quantum_regime_hmm_trained'
                    }
                    
                    return signal
            
            return RealQuantumSignalProcessor()
            
        except ImportError as e:
            logger.error(f"❌ 量子系統導入失敗: {e}")
            logger.error("❌ 無法載入必要的量子計算模組，系統無法運行")
            raise ImportError("量子自適應系統需要完整的量子計算環境")
        except Exception as e:
            logger.error(f"❌ 真正量子信號處理器初始化失敗: {e}")
            logger.error("❌ 量子信號處理器必須使用訓練好的模型，嚴格禁止任何降級模式")
            raise RuntimeError("量子自適應系統必須使用經過訓練的模型")
    
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
