#!/usr/bin/env python3
"""
檢查智能分層系統狀態
"""

import asyncio
import sys
sys.path.append('.')

from app.services.sniper_smart_layer import sniper_smart_layer

async def check_system_status():
    """檢查系統狀態"""
    print("🔍 檢查智能分層系統狀態...")
    
    # 檢查活躍信號
    print(f"\n📊 活躍信號數量: {len(sniper_smart_layer.active_signals)}")
    
    for symbol, signal in sniper_smart_layer.active_signals.items():
        print(f"• {symbol}: 品質評分 {signal.quality_score:.1f}, 過期時間 {signal.expires_at}")
    
    # 獲取所有活躍信號 (API方法)
    api_signals = await sniper_smart_layer.get_all_active_signals()
    print(f"\n📡 API返回信號數量: {len(api_signals)}")
    
    for signal in api_signals:
        print(f"• {signal['symbol']}: 品質評分 {signal['quality_score']}")

if __name__ == "__main__":
    asyncio.run(check_system_status())
