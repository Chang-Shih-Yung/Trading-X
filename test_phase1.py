#!/usr/bin/env python3
"""
Phase 1 動態市場適應測試腳本
"""

import asyncio
import sys
import os
sys.path.append('.')

async def test_phase1():
    from app.services.dynamic_market_adapter import dynamic_adapter
    from app.services.precision_signal_filter import PrecisionSignalFilter
    
    print('🎯 Phase 1 動態市場適應測試')
    print('=' * 50)
    
    # 測試動態市場狀態計算
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
    
    for symbol in symbols:
        try:
            print(f'\n📊 測試 {symbol} 動態市場狀態:')
            
            # 獲取市場狀態
            market_state = await dynamic_adapter.get_market_state(symbol)
            
            print(f'  • 波動率評分: {market_state.volatility_score:.2f}/3.0')
            print(f'  • 成交量強度: {market_state.volume_strength:.2f}/3.0') 
            print(f'  • 流動性評分: {market_state.liquidity_score:.2f}/2.0')
            print(f'  • 情緒倍數: {market_state.sentiment_multiplier:.2f}')
            print(f'  • ATR 價值: {market_state.atr_value:.6f}')
            
            # 計算動態閾值
            dynamic_thresholds = dynamic_adapter.get_dynamic_indicator_params(market_state)
            
            print(f'\n🔧 動態參數配置:')
            print(f'  • 信心度閾值: {dynamic_thresholds.confidence_threshold:.3f}')
            print(f'  • RSI 閾值: {dynamic_thresholds.rsi_oversold}/{dynamic_thresholds.rsi_overbought}')
            print(f'  • 止損百分比: {dynamic_thresholds.stop_loss_percent*100:.2f}%')
            print(f'  • 止盈百分比: {dynamic_thresholds.take_profit_percent*100:.2f}%')
            print(f'  • 布林帶倍數: {dynamic_thresholds.bollinger_multiplier:.2f}')
            
            # 測試精準篩選
            print(f'\n🎯 測試 {symbol} 動態精準篩選:')
            precision_filter = PrecisionSignalFilter()
            signal = await precision_filter.execute_precision_selection(symbol)
            
            if signal:
                print(f'  ✅ 生成信號: {signal.signal_type}')
                print(f'     策略: {signal.strategy_name}')
                print(f'     信心度: {signal.confidence:.3f}')
                print(f'     精準度: {signal.precision_score:.3f}')
                print(f'     進場價: ${signal.entry_price:.6f}')
                print(f'     止損價: ${signal.stop_loss:.6f}')
                print(f'     止盈價: ${signal.take_profit:.6f}')
            else:
                print(f'  ❌ 未生成信號（市場條件不符合動態標準）')
                
        except Exception as e:
            print(f'  ❌ {symbol} 測試失敗: {e}')
    
    print(f'\n🏆 Phase 1 測試完成!')
    print(f'主要改進:')
    print(f'  1. ✅ 移除雙重信心度過濾 (15% + 35% → 動態25-35%)')
    print(f'  2. ✅ 實現 ATR 動態止損止盈')
    print(f'  3. ✅ 基於成交量動態調整 RSI 閾值')
    print(f'  4. ✅ 整合動態市場狀態評估')

if __name__ == "__main__":
    asyncio.run(test_phase1())
