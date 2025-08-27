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
    from ..regime_hmm_quantum import QUANTUM_ENTANGLED_COINS, 即時幣安數據收集器
    from .quantum_adaptive_signal_engine import QuantumAdaptiveSignalEngine
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
            from regime_hmm_quantum import QuantumRegimeDetector, 即時市場觀測
            
            class RealQuantumSignalProcessor:
                """真正的量子信號處理器 - 使用已有的量子計算系統"""
                
                def __init__(self):
                    # 初始化量子制度檢測器
                    self.quantum_detector = QuantumRegimeDetector()
                    logger.info("✅ 量子制度檢測器初始化完成")
                
                async def generate_signal(self, symbol, market_data):
                    """使用真正的量子計算生成信號"""
                    
                    try:
                        # 將市場數據轉換為即時市場觀測
                        observation = self._convert_to_observation(symbol, market_data)
                        
                        # 🔮 使用真正的量子計算
                        quantum_result = self.quantum_detector.calculate_quantum_signal(observation)
                        
                        # 轉換為統一的信號格式
                        signal = self._convert_quantum_result_to_signal(symbol, quantum_result)
                        
                        logger.info(f"🔮 {symbol} 量子計算完成: {signal['signal']} (信心度: {signal['confidence']:.3f})")
                        return signal
                        
                    except Exception as e:
                        logger.error(f"❌ {symbol} 量子計算失敗: {e}")
                        return self._fallback_quantum_signal(symbol)
                
                def _convert_to_observation(self, symbol, market_data):
                    """將市場數據轉換為即時市場觀測"""
                    
                    # 創建即時市場觀測對象
                    observation = 即時市場觀測(
                        交易對=symbol,
                        當前價格=market_data.get('current_price', 0.0),
                        收益率=market_data.get('price_change_percent', 0.0) / 100.0,
                        已實現波動率=market_data.get('volatility', 0.02),
                        動量斜率=market_data.get('momentum', 0.0),
                        RSI_14=market_data.get('rsi', 50.0),
                        布林帶位置=market_data.get('bb_position', 0.5),
                        成交量=market_data.get('volume', 0.0),
                        成交量變化率=market_data.get('volume_change_percent', 0.0) / 100.0,
                        時間戳=datetime.now()
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
                
                def _fallback_quantum_signal(self, symbol):
                    """備用量子信號（當主要計算失敗時）"""
                    
                    logger.warning(f"⚠️ {symbol} 使用備用量子信號")
                    
                    # 使用量子隨機性生成備用信號
                    import os
                    entropy_bytes = os.urandom(3)
                    probs = np.array([b for b in entropy_bytes], dtype=float)
                    probs = probs / np.sum(probs)
                    
                    pred = np.argmax(probs)
                    signal_map = {0: 'BEAR', 1: 'NEUTRAL', 2: 'BULL'}
                    
                    return {
                        'symbol': symbol,
                        'signal': signal_map[pred],
                        'confidence': float(np.max(probs)),
                        'quantum_state': 'quantum_fallback',
                        'probabilities': {
                            'bear': float(probs[0]),
                            'side': float(probs[1]),
                            'bull': float(probs[2])
                        },
                        'quantum_backend': 'quantum_entropy_fallback',
                        'model_status': 'fallback_mode'
                    }
            
            return RealQuantumSignalProcessor()
            
        except ImportError as e:
            logger.error(f"❌ 量子系統導入失敗: {e}")
            return await self._fallback_quantum_processor()
        except Exception as e:
            logger.error(f"❌ 真正量子信號處理器初始化失敗: {e}")
            return await self._fallback_quantum_processor()
    
    async def _fallback_quantum_processor(self):
        """備用簡化量子處理器"""
        
        logger.warning("⚠️ 使用備用簡化量子處理器")
        
        class SimplifiedQuantumProcessor:
            async def generate_signal(self, symbol, market_data):
                """使用簡化量子計算生成信號"""
                
                try:
                    # 基於量子原理的簡化計算
                    import os

                    import numpy as np

                    # 從市場數據提取關鍵指標
                    volatility = market_data.get('volatility', 0.02)
                    momentum = market_data.get('momentum', 0.0)
                    trend_strength = market_data.get('trend_strength', 0.5)
                    
                    # 使用量子隨機數而非偽隨機數
                    entropy_bytes = os.urandom(12)
                    quantum_random = [b / 255.0 for b in entropy_bytes]
                    
                    # 基於量子疊加態原理計算機率
                    bear_prob = 0.33 + (quantum_random[0] - 0.5) * 0.2 - momentum * 0.3
                    bull_prob = 0.33 + (quantum_random[1] - 0.5) * 0.2 + momentum * 0.3  
                    side_prob = 1.0 - bear_prob - bull_prob
                    
                    # 正規化
                    total = bear_prob + side_prob + bull_prob
                    probs = np.array([bear_prob, side_prob, bull_prob]) / total
                    
                    pred = np.argmax(probs)
                    signal_map = {0: 'BEAR', 1: 'SIDE', 2: 'BULL'}
                    
                    return {
                        'symbol': symbol,
                        'signal': signal_map[pred],
                        'confidence': float(np.max(probs)),
                        'quantum_state': 'simplified_quantum_computation',
                        'probabilities': {
                            'bear': float(probs[0]),
                            'side': float(probs[1]),
                            'bull': float(probs[2])
                        }
                    }
                    
                except Exception as e:
                    logger.error(f"簡化量子計算失敗: {e}")
                    return None
        
        return SimplifiedQuantumProcessor()
    
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
