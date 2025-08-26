#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 動態權重融合系統測試器

測試新增的動態權重融合功能:
- 自適應權重調整
- 市場狀態驅動的風險調整  
- 貝葉斯更新的置信度校準
- 機器學習權重預測

用法: python test_dynamic_fusion.py
"""

import asyncio
import logging
import sys
from datetime import datetime

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

try:
    from regime_hmm_quantum import 即時幣安數據收集器, TradingX信號, DynamicWeightFusion
    SYSTEM_READY = True
except ImportError as e:
    logger.error(f"系統導入失敗: {e}")
    SYSTEM_READY = False

# 測試交易對
TEST_SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']

class DynamicFusionTester:
    """動態權重融合測試器"""
    
    def __init__(self):
        self.data_collector = None
        self.test_cycles = 0
        
    async def initialize_system(self):
        """初始化測試系統"""
        
        if not SYSTEM_READY:
            logger.error("❌ 系統未就緒")
            return False
        
        try:
            logger.info("🔮 初始化動態權重融合測試系統...")
            
            # 初始化數據收集器（包含動態權重融合器）
            self.data_collector = 即時幣安數據收集器(TEST_SYMBOLS)
            
            logger.info("✅ 測試系統初始化完成")
            logger.info(f"🎯 測試交易對: {', '.join(TEST_SYMBOLS)}")
            logger.info("🧠 動態權重融合器: 已啟動")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 初始化失敗: {e}")
            return False
    
    async def test_dynamic_fusion(self):
        """測試動態權重融合功能"""
        
        logger.info("🚀 開始動態權重融合測試...")
        
        # 運行5個測試週期
        for cycle in range(1, 6):
            try:
                logger.info(f"📊 測試週期 #{cycle}")
                
                # 測試信號生成
                for symbol in TEST_SYMBOLS:
                    signal = self.data_collector.生成量子終極信號(symbol)
                    
                    if signal:
                        await self.display_test_signal(signal, cycle)
                    else:
                        logger.info(f"⏳ {symbol} 數據累積中...")
                
                # 顯示權重狀態
                weight_status = self.data_collector.獲取動態權重狀態()
                if weight_status.get('status') != 'insufficient_data':
                    await self.display_weight_status(weight_status, cycle)
                else:
                    logger.info("📊 權重數據累積中...")
                
                # 每3個週期測試一次權重預測模型訓練
                if cycle % 3 == 0:
                    logger.info("🤖 測試權重預測模型訓練...")
                    self.data_collector.訓練權重預測模型()
                
                logger.info("-" * 60)
                
                # 等待下一個測試週期
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"❌ 測試週期 {cycle} 失敗: {e}")
    
    async def display_test_signal(self, signal: TradingX信號, cycle: int):
        """顯示測試信號"""
        
        # 信號圖標
        if signal.信號類型 == 'LONG':
            icon = "🟢 做多"
        elif signal.信號類型 == 'SHORT':
            icon = "🔴 做空"
        else:
            icon = "⚪ 觀望"
        
        logger.info(f"💎 {signal.交易對} 量子終極信號:")
        logger.info(f"   {icon} | 信心度: {signal.信心度:.2%}")
        logger.info(f"   🔮 制度: {signal.市場制度名稱} | 量子評分: {signal.量子評分:.3f}")
        logger.info(f"   💰 進場價格: ${signal.進場價格:.4f} | 期望收益: {signal.期望收益:.2%}")
        
        # 顯示動態權重
        微觀結構 = signal.市場微觀結構 or {}
        制度權重 = 微觀結構.get('制度權重', 0.5)
        量子權重 = 微觀結構.get('量子權重', 0.5)
        
        logger.info(f"   🧠 動態權重: 制度{制度權重:.1%} | 量子{量子權重:.1%}")
        logger.info(f"   ⚖️ 風險回報比: {signal.風險報酬比:.2f} | 建議倉位: {signal.持倉建議:.1%}")
    
    async def display_weight_status(self, status: dict, cycle: int):
        """顯示權重狀態"""
        
        logger.info(f"🧠 動態權重狀態 (週期 {cycle}):")
        
        # 當前權重
        current_weights = status.get('current_weights', {})
        regime_weight = current_weights.get('regime', 0.5)
        quantum_weight = current_weights.get('quantum', 0.5)
        
        logger.info(f"   ⚖️ 當前權重: 制度{regime_weight:.1%} | 量子{quantum_weight:.1%}")
        
        # 性能表現
        regime_perf = status.get('regime_performance', {})
        quantum_perf = status.get('quantum_performance', {})
        
        if regime_perf and quantum_perf:
            logger.info(f"   📈 制度模型: 準確率{regime_perf.get('recent_avg', 0):.1%}")
            logger.info(f"   🔮 量子模型: 準確率{quantum_perf.get('recent_avg', 0):.1%}")
        
        # 市場狀態
        market_state = status.get('market_state', {})
        if market_state:
            volatility = market_state.get('volatility', 0)
            trend_strength = market_state.get('trend_strength', 0)
            logger.info(f"   📊 市場狀態: 波動率{volatility:.2%} | 趨勢強度{trend_strength:.2f}")
    
    async def run_test(self):
        """運行完整測試"""
        
        try:
            logger.info("=" * 80)
            logger.info("🧠 Trading X 動態權重融合系統測試")
            logger.info("=" * 80)
            logger.info("🎯 測試項目:")
            logger.info("   1. 自適應權重調整")
            logger.info("   2. 市場狀態風險調整")
            logger.info("   3. 置信度校準")
            logger.info("   4. 機器學習權重預測")
            logger.info("=" * 80)
            
            # 初始化系統
            if not await self.initialize_system():
                return
            
            # 啟動數據收集
            data_task = asyncio.create_task(
                self.data_collector.啟動數據收集()
            )
            
            # 等待數據收集建立
            logger.info("⏳ 等待數據流建立...")
            await asyncio.sleep(5)
            
            # 運行融合測試
            test_task = asyncio.create_task(
                self.test_dynamic_fusion()
            )
            
            # 等待測試完成（限時1分鐘）
            try:
                await asyncio.wait_for(test_task, timeout=60)
            except asyncio.TimeoutError:
                logger.info("⏰ 測試時間結束")
            
            # 停止數據收集
            self.data_collector.force_stop = True
            
        except KeyboardInterrupt:
            logger.info("📴 測試被中斷")
        except Exception as e:
            logger.error(f"❌ 測試失敗: {e}")
        finally:
            logger.info("✅ 動態權重融合測試完成")

async def main():
    """主函數"""
    
    tester = DynamicFusionTester()
    await tester.run_test()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 測試被中斷")
    except Exception as e:
        print(f"❌ 測試執行失敗: {e}")
    finally:
        print("👋 動態權重融合測試器已退出")
