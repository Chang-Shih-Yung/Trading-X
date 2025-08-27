#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔮 量子驅動交易系統示例
展示如何使用量子自適應信號引擎
══════════════════════════════════════

這個示例展示了如何從固定30秒週期
轉換到真正的量子狀態驅動系統
"""

import asyncio
import logging
from datetime import datetime

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 導入量子自適應引擎
from quantum_adaptive_signal_engine import QuantumAdaptiveSignalEngine

class QuantumDrivenTradingSystem:
    """🔮 量子驅動交易系統"""
    
    def __init__(self):
        self.quantum_engine = QuantumAdaptiveSignalEngine()
        self.traditional_mode = False  # 設為True使用傳統30秒模式
        
    async def run_traditional_mode(self):
        """🕰️ 傳統固定30秒模式 (舊方法)"""
        
        logger.info("🕰️ 運行傳統固定週期模式...")
        
        cycle = 0
        while True:
            cycle += 1
            logger.info(f"📊 傳統分析週期 #{cycle} - 固定30秒間隔")
            
            # 傳統的固定分析邏輯
            await self._traditional_analysis()
            
            # 固定等待30秒
            logger.info("⏳ 等待30秒...")
            await asyncio.sleep(30)
    
    async def run_quantum_driven_mode(self):
        """🔮 量子驅動模式 (新方法)"""
        
        logger.info("🔮 啟動量子驅動交易模式...")
        logger.info("⚡ 告別固定週期，擁抱量子狀態觸發！")
        
        # 模擬數據收集器和信號處理器
        class MockDataCollector:
            async def get_market_data(self, symbol):
                return {'price': 50000, 'volume': 1000000}
        
        class MockSignalProcessor:
            async def generate_signal(self, symbol, market_data):
                return {
                    'symbol': symbol,
                    'signal': 'LONG',
                    'confidence': 0.85,
                    'trigger_reason': '量子狀態觸發'
                }
        
        data_collector = MockDataCollector()
        signal_processor = MockSignalProcessor()
        
        # 啟動量子驅動分析循環
        await self.quantum_engine.quantum_driven_analysis_loop(
            data_collector, 
            signal_processor
        )
    
    async def _traditional_analysis(self):
        """傳統的固定分析邏輯"""
        
        symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        
        for symbol in symbols:
            logger.info(f"📈 分析 {symbol}...")
            # 模擬分析時間
            await asyncio.sleep(0.5)
        
        logger.info("✅ 傳統分析完成")
    
    async def compare_modes(self):
        """🔬 對比兩種模式的差異"""
        
        logger.info("🔬 量子驅動 vs 傳統模式對比")
        logger.info("=" * 80)
        
        logger.info("📊 傳統固定週期模式:")
        logger.info("   ❌ 固定30秒間隔，無視市場狀態")
        logger.info("   ❌ 可能錯過快速市場變化")
        logger.info("   ❌ 在平靜市場時浪費計算資源")
        logger.info("   ❌ 無法適應不同幣種的特性")
        
        logger.info("")
        logger.info("🔮 量子驅動自適應模式:")
        logger.info("   ✅ 疊加態坍縮觸發，捕捉關鍵時刻")
        logger.info("   ✅ 量子糾纏檢測，跨幣聯動分析")
        logger.info("   ✅ 自適應間隔 (5-120秒)，最佳資源利用")
        logger.info("   ✅ 量子相干管理，避免過度交易")
        logger.info("   ✅ 不確定性突破檢測，精確時機把握")
        
        logger.info("=" * 80)
    
    async def demonstrate_quantum_triggers(self):
        """🎯 演示量子觸發機制"""
        
        logger.info("🎯 量子觸發機制演示")
        logger.info("=" * 60)
        
        # 初始化量子狀態
        symbols = ['BTCUSDT', 'ETHUSDT']
        self.quantum_engine.initialize_quantum_states(symbols)
        
        # 模擬不同的市場情況
        scenarios = [
            {
                'name': '疊加態坍縮事件',
                'data': {
                    'price_change_percent': 3.5,
                    'volume_change_percent': 45,
                    'volatility': 0.08,
                    'momentum': 0.8,
                    'rsi': 75
                }
            },
            {
                'name': '量子糾纏強化',
                'data': {
                    'price_change_percent': 0.5,
                    'volume_change_percent': 5,
                    'volatility': 0.01,
                    'momentum': 0.9,
                    'rsi': 65
                }
            },
            {
                'name': '不確定性突破',
                'data': {
                    'price_change_percent': 0.1,
                    'volume_change_percent': 2,
                    'volatility': 0.005,
                    'momentum': 0.3,
                    'rsi': 55
                }
            }
        ]
        
        for scenario in scenarios:
            logger.info(f"📋 場景: {scenario['name']}")
            
            for symbol in symbols:
                # 更新量子狀態
                event_detected = self.quantum_engine.update_quantum_state(
                    symbol, 
                    scenario['data']
                )
                
                # 檢查觸發條件
                should_signal, reason = self.quantum_engine.should_generate_signal_now(symbol)
                
                # 計算自適應間隔
                adaptive_interval = self.quantum_engine.calculate_adaptive_interval(symbol)
                
                logger.info(f"   {symbol}:")
                logger.info(f"     量子事件檢測: {'✅ 是' if event_detected else '❌ 否'}")
                logger.info(f"     信號觸發: {'✅ 是' if should_signal else '❌ 否'}")
                logger.info(f"     觸發原因: {reason}")
                logger.info(f"     自適應間隔: {adaptive_interval:.1f}秒")
                logger.info(f"     量子狀態: {self.quantum_engine._get_quantum_state_summary(symbol)}")
            
            logger.info("")
        
        logger.info("=" * 60)
    
    async def run(self):
        """運行示例"""
        
        logger.info("🚀 量子驅動交易系統啟動")
        logger.info("=" * 80)
        
        # 1. 對比兩種模式
        await self.compare_modes()
        
        # 2. 演示量子觸發機制
        await self.demonstrate_quantum_triggers()
        
        # 3. 詢問用戶選擇運行模式
        logger.info("🔧 選擇運行模式:")
        logger.info("   1. 量子驅動模式 (推薦)")
        logger.info("   2. 傳統固定週期模式")
        
        # 預設使用量子驅動模式
        mode = 1
        
        if mode == 1:
            logger.info("🔮 啟動量子驅動模式...")
            await self.run_quantum_driven_mode()
        else:
            logger.info("🕰️ 啟動傳統模式...")
            await self.run_traditional_mode()

async def main():
    """主函數"""
    
    system = QuantumDrivenTradingSystem()
    await system.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 用戶中斷")
    except Exception as e:
        print(f"❌ 錯誤: {e}")
