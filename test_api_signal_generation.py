#!/usr/bin/env python3
"""
🚀 通過後端服務直接測試信號生成
使用與API相同的服務實例
"""

import asyncio
import aiohttp
import json

async def trigger_signal_via_api():
    """通過API觸發信號生成"""
    print("🚀 通過API觸發信號生成測試")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # 測試幣種列表
    symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT', 'SOLUSDT']
    
    async with aiohttp.ClientSession() as session:
        for symbol in symbols:
            try:
                print(f"\n🎯 測試 {symbol}...")
                
                # 嘗試通過API觸發 (如果有觸發端點)
                # 這裡我們直接檢查現有信號
                
                # 檢查智能分層信號
                async with session.get(f"{base_url}/api/v1/scalping/smart-layer-signals?symbols={symbol}") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        signal_count = len(data.get('signals', []))
                        print(f"  📊 {symbol} 當前信號數: {signal_count}")
                        
                        if signal_count > 0:
                            for signal in data['signals']:
                                print(f"    ✅ {signal.get('symbol')} - {signal.get('action')} @ ${signal.get('current_price', 0):.4f}")
                                print(f"       信心度: {signal.get('confidence', 0):.2f}, 品質: {signal.get('quality_score', 0):.2f}")
                    else:
                        print(f"  ❌ API請求失敗: {resp.status}")
                        
            except Exception as e:
                print(f"  ❌ {symbol} 測試失敗: {e}")
        
        # 檢查整體狀態
        print(f"\n📊 整體系統狀態檢查:")
        try:
            async with session.get(f"{base_url}/api/v1/scalping/smart-layer-signals") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    total_signals = data.get('total_count', 0)
                    print(f"  🎯 總信號數: {total_signals}")
                    
                    if total_signals > 0:
                        print(f"  📈 信號列表:")
                        for signal in data.get('signals', []):
                            print(f"    • {signal.get('symbol')} - {signal.get('action')} (品質: {signal.get('quality_score', 0):.2f})")
                    else:
                        print(f"  ⚠️ 沒有活躍信號")
                        
                    print(f"  🕐 生成時間: {data.get('generated_at')}")
                else:
                    print(f"  ❌ 系統狀態檢查失敗: {resp.status}")
        except Exception as e:
            print(f"  ❌ 系統狀態檢查異常: {e}")

async def main():
    await trigger_signal_via_api()

if __name__ == "__main__":
    asyncio.run(main())
