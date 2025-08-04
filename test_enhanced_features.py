#!/usr/bin/env python3
"""
測試增強統計功能（簡化版）
"""

import asyncio
import sys
sys.path.append('.')

async def test_enhanced_features():
    print("🧪 測試增強統計功能...")
    
    try:
        # 方法1: 測試價格獲取和PnL計算
        print("\n📊 測試價格和PnL計算...")
        
        # 直接導入並使用方法
        from app.services.sniper_smart_layer import SniperSmartLayerSystem
        
        # 創建實例但不完全初始化
        system = SniperSmartLayerSystem()
        
        # 測試價格獲取
        test_symbol = "BTCUSDT"
        price = await system._get_api_fallback_price(test_symbol)
        print(f"   {test_symbol} API價格: ${price:,.2f}")
        
        # 測試PnL計算
        test_signals = [
            {'symbol': test_symbol, 'entry_price': 50000.0, 'signal_type': 'BUY'},
            {'symbol': test_symbol, 'entry_price': 120000.0, 'signal_type': 'SELL'}
        ]
        
        for signal in test_signals:
            pnl = await system._calculate_current_pnl(signal, price)
            entry = signal['entry_price']
            sig_type = signal['signal_type']
            print(f"   {sig_type}信號: 入場 ${entry:,.0f} -> 當前 ${price:,.0f} = {pnl:.2f}%")
        
        # 方法2: 測試統計計算
        print("\n📈 測試統計計算...")
        
        # 測試風險指標計算
        risk_metrics = await system._calculate_risk_metrics()
        print(f"   風險指標: {len(risk_metrics)} 項")
        for key, value in risk_metrics.items():
            if isinstance(value, (int, float)):
                print(f"     {key}: {value}")
        
        # 測試盈虧比計算
        test_stats = {
            'profitable_signals': 30,
            'unprofitable_signals': 20,
            'total_pnl': 150.5,
            'average_pnl': 3.01
        }
        profit_factor = system._calculate_profit_factor(test_stats)
        print(f"   盈虧比: {profit_factor:.2f}")
        
        # 測試夏普比率
        sharpe_ratio = await system._calculate_sharpe_ratio()
        print(f"   夏普比率: {sharpe_ratio:.2f}")
        
        print("\n✅ 增強功能測試完成")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_enhanced_features())
