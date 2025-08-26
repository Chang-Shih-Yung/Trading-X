#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔮 Trading X Quantum Ultimate Launcher v3.0
統一量子交易系統啟動器
═══════════════════════════════════════════════

系統架構整合：
- 主要系統：regime_hmm_quantum.py（包含DynamicWeightFusion）
- 啟動器：quantum_ultimate_launcher.py（本文件）
- 已移除：redundant integrated files（避免混淆）

核心功能：
- 🧠 動態權重融合器（自適應學習）
- 🔮 量子終極融合引擎（七幣種同步）
- 📊 實時市場微觀結構分析
- ⚖️ 智能風險管理系統
- 🎯 機器學習權重預測

技術規格：
- 無簡化、無模擬數據
- 完整實時數據集成
- 動態性能調整
"""

import asyncio
import logging
import sys
import signal
import numpy as np
from typing import Dict, Any
from datetime import datetime

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'quantum_ultimate_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

# 量子系統依賴檢查
try:
    from regime_hmm_quantum import (
        即時幣安數據收集器,
        TradingX信號,
        QUANTUM_SYMBOLS
    )
    QUANTUM_AVAILABLE = True
    logger.info("✅ 量子系統模組載入成功")
except ImportError as e:
    QUANTUM_AVAILABLE = False
    logger.error(f"❌ 量子系統模組載入失敗: {e}")

# 導入設置
QUANTUM_SYMBOLS = [
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT',
    'XRPUSDT', 'DOGEUSDT', 'ADAUSDT'
]

class QuantumUltimateLauncher:
    """🚀 量子終極系統啟動器 v3.0"""
    
    def __init__(self):
        self.運行中 = False
        self.數據收集器 = None
        self.信號歷史 = []
        
        # 設置優雅退出
        signal.signal(signal.SIGINT, self._優雅退出)
        signal.signal(signal.SIGTERM, self._優雅退出)
        
    def _優雅退出(self, signum, frame):
        """優雅退出處理"""
        logger.info(f"📴 收到關閉信號 {signum}，正在優雅關閉...")
        self.運行中 = False
        
        if self.數據收集器:
            logger.info("🛑 正在停止量子終極引擎...")
            # 設置強制停止標誌
            self.數據收集器.force_stop = True
            
        # 快速退出（1秒超時）
        try:
            import time
            time.sleep(1)
        except:
            pass
        
        logger.info("⚡ 強制終止程序...")
        sys.exit(0)
    
    async def 初始化量子終極系統(self):
        """初始化量子終極交易系統"""
        
        if not QUANTUM_AVAILABLE:
            logger.error("❌ 量子系統不可用，請檢查依賴安裝")
            return False
        
        try:
            logger.info("🔮 初始化量子終極交易系統...")
            
            # 初始化數據收集器（包含量子終極融合引擎）
            self.數據收集器 = 即時幣安數據收集器(QUANTUM_SYMBOLS)
            
            logger.info("✅ 量子終極系統初始化完成")
            logger.info(f"🎯 監控交易對: {', '.join(QUANTUM_SYMBOLS)}")
            logger.info("🧠 動態權重融合器: 已啟動")
            logger.info("🔮 量子終極引擎: 已就緒")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 量子系統初始化失敗: {e}")
            return False
    
    async def 啟動量子終極分析(self):
        """啟動量子終極分析循環"""
        
        logger.info("🚀 啟動量子終極分析循環...")
        
        分析週期 = 0
        
        while self.運行中:
            try:
                分析週期 += 1
                logger.info(f"📊 執行量子終極分析週期 #{分析週期}")
                
                # 檢查數據收集器狀態
                if self.數據收集器 and self.數據收集器.運行中:
                    logger.info("🔗 量子數據流: 活躍中")
                    
                    # 生成所有交易對的量子終極信號
                    全部信號 = self.數據收集器.獲取所有交易對信號()
                    
                    if 全部信號:
                        await self.顯示量子終極信號(全部信號)
                        
                        # 獲取動態權重狀態
                        權重狀態 = self.數據收集器.獲取動態權重狀態()
                        if 權重狀態.get('status') != 'insufficient_data':
                            await self.顯示動態權重狀態(權重狀態)
                        
                        # 每10個週期訓練一次權重預測模型
                        if 分析週期 % 10 == 0:
                            logger.info("🤖 訓練動態權重預測模型...")
                            self.數據收集器.訓練權重預測模型()
                        
                        # 每20個週期訓練一次量子模型  
                        if 分析週期 % 20 == 0:
                            logger.info("🔮 訓練量子變分模型...")
                            self.數據收集器.訓練量子模型(max_iterations=30)
                    
                    else:
                        logger.info("⏳ 量子數據累積中...")
                        
                else:
                    logger.warning("⚠️ 量子數據流中斷")
                
                # 等待下一個分析週期（30秒）
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                logger.info("📴 量子分析循環被取消")
                break
            except Exception as e:
                logger.error(f"❌ 量子分析週期失敗: {e}")
                await asyncio.sleep(5)  # 錯誤後短暫暫停
    
    async def 顯示量子終極信號(self, 信號字典: Dict[str, TradingX信號]):
        """顯示量子終極交易信號"""
        
        logger.info("🎯 量子終極交易信號生成:")
        logger.info("=" * 90)
        
        for 交易對, 信號 in 信號字典.items():
            # 信號圖標
            if 信號.信號類型 == 'LONG':
                圖標 = "🟢"
                動作 = "做多"
            elif 信號.信號類型 == 'SHORT':
                圖標 = "🔴" 
                動作 = "做空"
            else:
                圖標 = "⚪"
                動作 = "觀望"
            
            # 信心度條
            信心條 = "█" * int(信號.信心度 * 10) + "░" * (10 - int(信號.信心度 * 10))
            
            # 風險等級
            風險等級 = self._獲取風險等級(信號.風險評估)
            
            logger.info(f"💎 {交易對}")
            logger.info(f"   {圖標} 信號: {動作} | 信心度: {信號.信心度:.2%} [{信心條}]")
            logger.info(f"   🔮 制度: {信號.市場制度名稱} | 量子評分: {信號.量子評分:.3f}")
            logger.info(f"   💰 進場: ${信號.進場價格:.4f} | 期望收益: {信號.期望收益:.2%}")
            
            if 信號.止損價格 and 信號.止盈價格:
                logger.info(f"   🛡️ 止損: ${信號.止損價格:.4f} | 🎯 止盈: ${信號.止盈價格:.4f}")
            
            logger.info(f"   ⚖️ 風險回報比: {信號.風險報酬比:.2f} | 風險等級: {風險等級}")
            logger.info(f"   📊 建議倉位: {信號.持倉建議:.1%}")
            
            # 顯示權重信息
            微觀結構 = 信號.市場微觀結構 or {}
            制度權重 = 微觀結構.get('制度權重', 0.5)
            量子權重 = 微觀結構.get('量子權重', 0.5)
            logger.info(f"   🧠 動態權重融合: 制度{制度權重:.1%} | 量子{量子權重:.1%}")
            
            # 顯示市場微觀結構
            logger.info(f"   📈 微觀結構: 買賣差{微觀結構.get('買賣價差', 0):.4f} | "
                       f"資金費率{微觀結構.get('資金費率', 0):.4f} | "
                       f"主動買入{微觀結構.get('主動買入比率', 0.5):.1%}")
            
            logger.info("-" * 70)
    
    def _獲取風險等級(self, 風險值: float) -> str:
        """獲取風險等級描述"""
        if 風險值 < 0.01:
            return "🟢 低風險"
        elif 風險值 < 0.03:
            return "🟡 中風險"
        elif 風險值 < 0.05:
            return "🟠 高風險"
        else:
            return "🔴 極高風險"
    
    async def 顯示動態權重狀態(self, 權重狀態: Dict[str, Any]):
        """顯示動態權重融合狀態"""
        
        logger.info("🧠 動態權重融合狀態:")
        logger.info("=" * 70)
        
        # 性能表現
        制度性能 = 權重狀態.get('regime_performance', {})
        量子性能 = 權重狀態.get('quantum_performance', {})
        
        logger.info(f"📈 制度模型性能:")
        logger.info(f"   近期準確率: {制度性能.get('recent_avg', 0):.2%} | "
                   f"整體準確率: {制度性能.get('overall_avg', 0):.2%}")
        logger.info(f"   性能趨勢: {制度性能.get('trend', 0):+.4f} | "
                   f"穩定性: {1/(制度性能.get('volatility', 1)+0.01):.2f}")
        
        logger.info(f"🔮 量子模型性能:")
        logger.info(f"   近期準確率: {量子性能.get('recent_avg', 0):.2%} | "
                   f"整體準確率: {量子性能.get('overall_avg', 0):.2%}")
        logger.info(f"   性能趨勢: {量子性能.get('trend', 0):+.4f} | "
                   f"穩定性: {1/(量子性能.get('volatility', 1)+0.01):.2f}")
        
        # 當前權重
        當前權重 = 權重狀態.get('current_weights', {})
        制度權重 = 當前權重.get('regime', 0.5)
        量子權重 = 當前權重.get('quantum', 0.5)
        
        logger.info(f"⚖️ 當前權重分配:")
        制度條 = "█" * int(制度權重 * 20) + "░" * (20 - int(制度權重 * 20))
        量子條 = "█" * int(量子權重 * 20) + "░" * (20 - int(量子權重 * 20))
        logger.info(f"   制度權重: {制度權重:.1%} [{制度條}]")
        logger.info(f"   量子權重: {量子權重:.1%} [{量子條}]")
        
        # 市場狀態
        市場狀態 = 權重狀態.get('market_state', {})
        波動率 = 市場狀態.get('volatility', 0)
        趨勢強度 = 市場狀態.get('trend_strength', 0)
        
        波動狀態 = self._獲取波動狀態(波動率)
        趨勢狀態 = self._獲取趨勢狀態(趨勢強度)
        
        logger.info(f"📊 市場狀態:")
        logger.info(f"   波動率: {波動率:.2%} {波動狀態}")
        logger.info(f"   趨勢強度: {趨勢強度:.2f} {趨勢狀態}")
        
        logger.info("=" * 70)
    
    def _獲取波動狀態(self, 波動率: float) -> str:
        """獲取波動狀態描述"""
        if 波動率 < 0.01:
            return "🟢 極低波動"
        elif 波動率 < 0.02:
            return "🟡 低波動"
        elif 波動率 < 0.04:
            return "🟠 中等波動"
        else:
            return "🔴 高波動"
    
    def _獲取趨勢狀態(self, 趨勢強度: float) -> str:
        """獲取趨勢狀態描述"""
        if 趨勢強度 < 0.5:
            return "⚪ 無明顯趨勢"
        elif 趨勢強度 < 1.0:
            return "🟡 弱趨勢"
        elif 趨勢強度 < 2.0:
            return "🟠 中等趨勢"
        else:
            return "🔴 強趨勢"
    
    async def 運行(self):
        """運行量子終極交易系統"""
        
        try:
            logger.info("=" * 90)
            logger.info("🔮 Trading X 量子終極交易系統 v3.0")
            logger.info("=" * 90)
            logger.info("🧠 動態權重融合 + 制度識別 + 量子變分預測")
            logger.info("⚡ 七大幣種同步分析 + 實時信號生成")
            logger.info("🎯 自適應權重調整 + 機器學習優化")
            logger.info("📁 架構清理完成 - 統一量子系統")
            logger.info("=" * 90)
            
            # 初始化系統
            if not await self.初始化量子終極系統():
                return
            
            self.運行中 = True
            
            # 啟動數據收集
            數據收集任務 = asyncio.create_task(
                self.數據收集器.啟動數據收集()
            )
            
            # 等待數據收集建立
            logger.info("⏳ 等待量子數據流建立...")
            await asyncio.sleep(5)
            
            # 啟動量子分析循環
            分析任務 = asyncio.create_task(
                self.啟動量子終極分析()
            )
            
            # 等待任務完成
            await asyncio.gather(數據收集任務, 分析任務, return_exceptions=True)
            
        except KeyboardInterrupt:
            logger.info("📴 收到中斷信號")
        except Exception as e:
            logger.error(f"❌ 系統運行錯誤: {e}")
        finally:
            await self.清理資源()
    
    async def 清理資源(self):
        """清理系統資源"""
        
        logger.info("🧹 清理系統資源...")
        
        if self.數據收集器:
            try:
                await asyncio.wait_for(
                    self.數據收集器.停止數據收集(),
                    timeout=2.0
                )
            except asyncio.TimeoutError:
                logger.warning("⚠️ 數據收集器停止超時")
            except Exception as e:
                logger.error(f"❌ 停止數據收集器失敗: {e}")
        
        logger.info("✅ 資源清理完成")

async def main():
    """主函數"""
    
    啟動器 = QuantumUltimateLauncher()
    await 啟動器.運行()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 用戶中斷程序")
    except Exception as e:
        print(f"❌ 程序執行失敗: {e}")
    finally:
        print("👋 Trading X 量子終極系統已退出")
