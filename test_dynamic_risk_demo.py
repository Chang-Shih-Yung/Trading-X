#!/usr/bin/env python3
"""
🎯 動態風險參數系統演示
專門展示短中長線、不同幣種的動態止盈止損計算
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime
from sniper_unified_data_layer import SnipeDataUnifiedLayer, TradingTimeframe

async def demo_dynamic_risk_parameters():
    """演示動態風險參數計算"""
    print("🎯 狙擊手動態風險參數系統演示")
    print("=" * 80)
    
    sniper = SnipeDataUnifiedLayer()
    
    # 測試不同場景
    scenarios = [
        {
            'symbol': 'BTCUSDT',
            'current_price': 50000.0,
            'atr_value': 800.0,  # 1.6%的ATR
            'signal_quality': 'high',
            'timeframe': TradingTimeframe.SHORT_TERM,
            'market_volatility': 0.025
        },
        {
            'symbol': 'BTCUSDT', 
            'current_price': 50000.0,
            'atr_value': 800.0,
            'signal_quality': 'medium',
            'timeframe': TradingTimeframe.MEDIUM_TERM,
            'market_volatility': 0.025
        },
        {
            'symbol': 'BTCUSDT',
            'current_price': 50000.0,
            'atr_value': 800.0,
            'signal_quality': 'low',
            'timeframe': TradingTimeframe.LONG_TERM,
            'market_volatility': 0.025
        },
        {
            'symbol': 'ETHUSDT',
            'current_price': 3000.0,
            'atr_value': 80.0,  # 2.67%的ATR
            'signal_quality': 'high',
            'timeframe': TradingTimeframe.MEDIUM_TERM,
            'market_volatility': 0.04
        },
        {
            'symbol': 'ADAUSDT',
            'current_price': 0.5,
            'atr_value': 0.02,  # 4%的ATR
            'signal_quality': 'medium', 
            'timeframe': TradingTimeframe.LONG_TERM,
            'market_volatility': 0.06
        }
    ]
    
    print(f"📊 測試場景總數: {len(scenarios)}")
    print("\n" + "=" * 80)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🎯 場景 {i}: {scenario['symbol']} - {scenario['timeframe'].value}線策略")
        print(f"   當前價格: ${scenario['current_price']:,.2f}")
        print(f"   ATR值: ${scenario['atr_value']:,.2f} ({scenario['atr_value']/scenario['current_price']:.2%})")
        print(f"   信號品質: {scenario['signal_quality']}")
        print(f"   市場波動率: {scenario['market_volatility']:.1%}")
        
        # 計算動態風險參數
        risk_params = sniper.calculate_dynamic_risk_parameters(
            symbol=scenario['symbol'],
            current_price=scenario['current_price'],
            atr_value=scenario['atr_value'],
            signal_type='BUY',
            signal_quality=scenario['signal_quality'],
            timeframe=scenario['timeframe'],
            market_volatility=scenario['market_volatility']
        )
        
        # 顯示結果
        print(f"📈 動態風險參數:")
        print(f"   止損價格: ${risk_params.stop_loss_price:,.6f}")
        print(f"   止盈價格: ${risk_params.take_profit_price:,.6f}")
        print(f"   止損幅度: {((scenario['current_price'] - risk_params.stop_loss_price) / scenario['current_price']):.2%}")
        print(f"   止盈幅度: {((risk_params.take_profit_price - scenario['current_price']) / scenario['current_price']):.2%}")
        print(f"   風險回報比: {risk_params.risk_reward_ratio}")
        print(f"   過期時間: {risk_params.expiry_hours} 小時")
        print(f"   倉位乘數: {risk_params.position_size_multiplier}")
        
        # 計算預期盈虧
        risk_amount = (scenario['current_price'] - risk_params.stop_loss_price) / scenario['current_price']
        reward_amount = (risk_params.take_profit_price - scenario['current_price']) / scenario['current_price']
        
        print(f"💰 風險回報分析:")
        print(f"   最大風險: {risk_amount:.2%}")
        print(f"   預期回報: {reward_amount:.2%}")
        print(f"   實際RR比: {reward_amount/risk_amount:.2f}")
        
        # 根據時間框架顯示策略說明
        strategy_notes = {
            TradingTimeframe.SHORT_TERM: "短線策略：快進快出，較小止損，適合高頻交易",
            TradingTimeframe.MEDIUM_TERM: "中線策略：平衡風險回報，適合日內到隔夜持倉",
            TradingTimeframe.LONG_TERM: "長線策略：較大止損空間，追求更高回報"
        }
        
        print(f"📝 策略說明: {strategy_notes[scenario['timeframe']]}")
    
    print("\n" + "=" * 80)
    print("✅ 動態風險參數演示完成")
    print("\n🎯 系統特色:")
    print("   ✅ 根據不同幣種調整風險參數（BTC保守，小幣激進）")  
    print("   ✅ 基於ATR計算動態止損（避免固定百分比）")
    print("   ✅ 信號品質影響風險管理（高品質信號敢承擔更小止損）")
    print("   ✅ 時間框架決定持倉預期（短線快速，長線耐心）")
    print("   ✅ 市場波動影響倉位大小（高波動減倉，低波動加倉）")
    print("   ✅ 完全動態計算，無任何固定值依賴")
    
    print("\n📋 不同幣種策略差異:")
    print("   🪙 BTC: 相對穩定，止損1.5%-5%，止盈3%-12%")
    print("   🪙 ETH: 波動較大，止損2%-6%，止盈4%-15%")  
    print("   🪙 小幣: 波動最大，止損2.5%-8%，止盈5%-20%")
    
    print("\n⏰ 時間框架策略:")
    print("   📊 短線 (1-12小時): 追求快速盈利，較小止損空間")
    print("   📊 中線 (6-36小時): 平衡風險回報，適中持倉時間")
    print("   📊 長線 (12-96小時): 追求更高回報，給價格更多空間")

if __name__ == "__main__":
    asyncio.run(demo_dynamic_risk_parameters())
