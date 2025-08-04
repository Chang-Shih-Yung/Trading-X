#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試增強統計系統
"""

import asyncio
import sys
sys.path.append('.')

from app.services.sniper_smart_layer import sniper_smart_layer

async def test_enhanced_stats():
    print("🧪 測試增強統計系統...")
    
    try:
        # 測試增強統計
        stats = await sniper_smart_layer.get_enhanced_statistics()
        
        print("📊 增強統計結果:")
        print(f"   狀態: {stats.get('status')}")
        
        if stats.get('status') == 'success':
            perf = stats.get('performance_metrics', {})
            print(f"   總信號: {perf.get('total_signals', 0)}")
            print(f"   傳統勝率: {perf.get('traditional_win_rate', 0):.1f}%")
            print(f"   真實成功率: {perf.get('real_success_rate', 0):.1f}%")
            print(f"   平均收益: {perf.get('average_pnl', 0):.2f}%")
            print(f"   總收益: {perf.get('total_pnl', 0):.2f}%")
            print(f"   盈虧比: {perf.get('profit_factor', 0):.2f}")
            print(f"   夏普比率: {perf.get('sharpe_ratio', 0):.2f}")
            
            risk = stats.get('risk_analytics', {})
            if risk:
                print(f"   最大收益: {risk.get('max_gain', 0):.2f}%")
                print(f"   最大虧損: {risk.get('max_loss', 0):.2f}%")
                print(f"   波動率: {risk.get('volatility', 0):.2f}%")
            
            realtime = stats.get('realtime_monitoring', {})
            active_pos = realtime.get('active_positions', {})
            print(f"   實時監控: {len(active_pos)} 個活躍信號")
            
            for symbol, data in list(active_pos.items())[:3]:
                price = data.get('price', 0)
                pnl = data.get('current_pnl', 0)
                print(f"     {symbol}: 價格 {price:.4f}, PnL {pnl:.2f}%")
        
        else:
            print(f"   錯誤: {stats.get('error')}")
        
        print("✅ 增強統計測試完成")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_enhanced_stats())
