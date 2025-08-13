#!/usr/bin/env python3
"""
深度分析 Phase1A 信號生成門檻問題
目標：找出為何價格變化超過門檻仍不生成信號
"""

import asyncio
import logging
import sys
from pathlib import Path

# 設置專案路徑
project_root = Path(__file__).parent
sys.path.append(str(project_root / "X" / "backend"))

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def deep_signal_analysis():
    """深度分析信號生成失敗原因"""
    try:
        from phase1_signal_generation.phase1a_basic_signal_generation.phase1a_basic_signal_generation import Phase1ABasicSignalGeneration
        
        # 創建 Phase1A 實例
        phase1a = Phase1ABasicSignalGeneration()
        
        # 手動設置運行狀態
        phase1a.is_running = True
        
        # 模擬歷史數據（10個價格點）
        test_symbol = "BTCUSDT"
        phase1a.price_buffer[test_symbol] = []
        
        # 添加歷史價格數據
        base_price = 119420.0
        for i in range(10):
            price_data = {
                'price': base_price + (i * 0.1),  # 逐漸增加價格
                'timestamp': f'2025-08-13T15:22:{20+i:02d}',
                'volume': 1000.0
            }
            phase1a.price_buffer[test_symbol].append(price_data)
        
        logger.info(f"✅ 設置了 {len(phase1a.price_buffer[test_symbol])} 個歷史價格點")
        
        # 創建市場數據，價格變化 0.15%
        current_price = base_price + (base_price * 0.0015)  # 0.15% 上漲
        market_data = {
            'symbol': test_symbol,
            'price': current_price,
            'volume': 1200.0,
            'timestamp': '2025-08-13T15:22:30'
        }
        
        price_change_pct = (current_price - base_price) / base_price
        logger.info(f"💰 基準價格: ${base_price:.2f}")
        logger.info(f"💰 當前價格: ${current_price:.2f}")
        logger.info(f"📈 價格變化: {price_change_pct:.6f} ({price_change_pct*100:.3f}%)")
        
        # 獲取動態參數
        dynamic_params = await phase1a._get_dynamic_parameters()
        logger.info(f"🎯 價格變化門檻: {dynamic_params.price_change_threshold:.6f} ({dynamic_params.price_change_threshold*100:.3f}%)")
        logger.info(f"🔍 信心度門檻: {dynamic_params.confidence_threshold:.3f}")
        
        # 檢查是否滿足基本條件
        logger.info("🔍 檢查信號生成條件:")
        logger.info(f"   ✅ is_running: {phase1a.is_running}")
        logger.info(f"   ✅ 歷史數據點: {len(phase1a.price_buffer.get(test_symbol, []))}")
        logger.info(f"   {'✅' if abs(price_change_pct) > dynamic_params.price_change_threshold else '❌'} 價格變化超過門檻: {abs(price_change_pct):.6f} > {dynamic_params.price_change_threshold:.6f}")
        
        # 嘗試手動調用信號生成
        logger.info("🎯 嘗試手動生成信號...")
        signals = await phase1a.generate_signals(test_symbol, market_data)
        
        if signals:
            logger.info(f"🎉 成功生成 {len(signals)} 個信號!")
            for signal in signals:
                logger.info(f"   📊 {signal.symbol}: {signal.direction} | 強度: {signal.strength:.3f} | 信心度: {signal.confidence:.3f}")
        else:
            logger.warning("⚠️ 仍然沒有生成信號")
            
            # 進一步診斷
            logger.info("🔍 深度診斷:")
            
            # 檢查各層信號生成
            try:
                layer_0_signals = await phase1a._layer_0_instant_signals_enhanced(test_symbol, market_data, dynamic_params)
                logger.info(f"   Layer 0 (即時): {len(layer_0_signals) if layer_0_signals else 0} 個信號")
                
                # 如果 Layer 0 沒有信號，檢查原因
                if not layer_0_signals:
                    logger.info("   🔍 Layer 0 失敗原因分析:")
                    recent_prices = list(phase1a.price_buffer[test_symbol])[-10:]
                    if len(recent_prices) < 2:
                        logger.warning(f"      ❌ 價格數據不足: {len(recent_prices)} < 2")
                    else:
                        current_p = recent_prices[-1]['price']
                        previous_p = recent_prices[-2]['price']
                        actual_change = (current_p - previous_p) / previous_p if previous_p > 0 else 0
                        logger.info(f"      📊 實際最近變化: {actual_change:.6f} ({actual_change*100:.3f}%)")
                        logger.info(f"      🎯 需要變化: {dynamic_params.price_change_threshold:.6f} ({dynamic_params.price_change_threshold*100:.3f}%)")
                        
                        if abs(actual_change) <= dynamic_params.price_change_threshold:
                            logger.warning(f"      ❌ 最近價格變化太小: {abs(actual_change):.6f} <= {dynamic_params.price_change_threshold:.6f}")
                        else:
                            logger.info(f"      ✅ 價格變化足夠: {abs(actual_change):.6f} > {dynamic_params.price_change_threshold:.6f}")
                            
                            # 檢查信心度計算
                            import numpy as np
                            price_values = [p['price'] for p in recent_prices]
                            volatility = np.std(price_values) / np.mean(price_values) if len(price_values) > 1 else 0
                            confidence = min(0.95, dynamic_params.confidence_threshold + (1 - volatility) * 0.2)
                            logger.info(f"      📊 波動性: {volatility:.6f}")
                            logger.info(f"      🔍 計算信心度: {confidence:.3f}")
                            logger.info(f"      🎯 信心度門檻: {dynamic_params.confidence_threshold:.3f}")
                            
                            if confidence < dynamic_params.confidence_threshold:
                                logger.warning(f"      ❌ 信心度不足: {confidence:.3f} < {dynamic_params.confidence_threshold:.3f}")
                            else:
                                logger.info(f"      ✅ 信心度足夠: {confidence:.3f} >= {dynamic_params.confidence_threshold:.3f}")
                
            except Exception as e:
                logger.error(f"   ❌ Layer 診斷失敗: {e}")
        
        return len(signals) > 0 if signals else False
        
    except Exception as e:
        logger.error(f"❌ 分析失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await deep_signal_analysis()
    
    if success:
        print("\n🎉 信號生成成功！")
    else:
        print("\n⚠️ 信號生成失敗，已完成深度分析")

if __name__ == "__main__":
    asyncio.run(main())
