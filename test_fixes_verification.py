#!/usr/bin/env python3
"""
觸發新信號並驗證修復效果
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta

async def trigger_and_verify_fixes():
    """觸發新信號並驗證修復效果"""
    print("🎯 狙擊手策略修復驗證")
    print("=" * 60)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    base_url = "http://localhost:8000/api/v1/scalping"
    
    async with aiohttp.ClientSession() as session:
        try:
            # 觸發信號生成
            print("📡 觸發狙擊手雙層數據分析...")
            trigger_url = f"{base_url}/sniper-unified-data-layer"
            params = {
                'symbols': 'BTCUSDT,ETHUSDT,BNBUSDT',
                'timeframe': '1h',
                'force_refresh': 'true',
                'broadcast_signals': 'true'
            }
            
            async with session.get(trigger_url, params=params) as response:
                if response.status == 200:
                    print("✅ 信號生成觸發成功")
                else:
                    print(f"❌ 信號生成觸發失敗: {response.status}")
                    return
            
            # 等待信號處理
            print("⏳ 等待信號處理...")
            await asyncio.sleep(5)
            
            # 檢查新信號
            print("\n📊 檢查新生成的信號...")
            async with session.get(f"{base_url}/dashboard-precision-signals") as response:
                if response.status == 200:
                    data = await response.json()
                    signals = data.get('signals', [])
                    
                    if signals:
                        print(f"✅ 獲取到 {len(signals)} 個信號")
                        
                        # 檢查最新的3個信號
                        for i, signal in enumerate(signals[:3]):
                            print(f"\n🎯 信號 {i+1}: {signal.get('symbol')} {signal.get('signal_type')}")
                            
                            # 檢查動態時間
                            created_at = signal.get('created_at')
                            expires_at = signal.get('expires_at')
                            if created_at and expires_at:
                                from datetime import datetime as dt
                                created = dt.fromisoformat(created_at.replace('Z', '+00:00'))
                                expires = dt.fromisoformat(expires_at.replace('Z', '+00:00'))
                                duration_hours = (expires - created).total_seconds() / 3600
                                
                                print(f"   ⏰ 動態持續時間: {duration_hours:.1f}小時")
                                
                                if duration_hours == 24.0:
                                    print(f"   ⚠️  可能仍使用固定24小時")
                                else:
                                    print(f"   ✅ 使用動態時間計算")
                            
                            # 檢查價格合理性
                            entry_price = signal.get('entry_price', 0)
                            stop_loss = signal.get('stop_loss', 0)
                            take_profit = signal.get('take_profit', 0)
                            
                            if entry_price > 0:
                                risk_pct = abs(entry_price - stop_loss) / entry_price * 100
                                reward_pct = abs(take_profit - entry_price) / entry_price * 100
                                
                                print(f"   💰 進場價: ${entry_price:.6f}")
                                print(f"   📉 風險: {risk_pct:.2f}%")
                                print(f"   📈 回報: {reward_pct:.2f}%")
                                
                                if abs(risk_pct - 3.0) < 0.1 and abs(reward_pct - 6.0) < 0.1:
                                    print(f"   ⚠️  可能仍使用固定3%/6%計算")
                                else:
                                    print(f"   ✅ 使用動態價格計算")
                            
                            # 檢查處理時間
                            layer_one_time = signal.get('layer_one_time')
                            layer_two_time = signal.get('layer_two_time')
                            
                            if layer_one_time is not None and layer_two_time is not None:
                                print(f"   ⚡ 處理時間: Layer1={layer_one_time}ms, Layer2={layer_two_time}ms")
                                if layer_one_time == 0.0 and layer_two_time == 0.0:
                                    print(f"   ⚠️  處理時間可能為模擬值")
                                else:
                                    print(f"   ✅ 處理時間正常")
                    else:
                        print("⚠️  暫無新信號生成")
                else:
                    print(f"❌ 獲取信號失敗: {response.status}")
            
            # 檢查Email發送狀態
            print(f"\n📧 檢查Email發送狀態...")
            async with session.get("http://localhost:8000/api/v1/notifications/email/status") as response:
                if response.status == 200:
                    email_data = await response.json()
                    print(f"   Gmail服務狀態: {email_data.get('gmail_status', 'unknown')}")
                    print(f"   最後發送時間: {email_data.get('last_sent_at', 'N/A')}")
                    print(f"   冷卻時間: {email_data.get('cooldown_minutes', 'N/A')}分鐘")
                else:
                    print(f"   ❌ 無法獲取Email狀態")
                    
        except Exception as e:
            print(f"❌ 測試失敗: {e}")
    
    print(f"\n🎯 修復驗證完成 - {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(trigger_and_verify_fixes())
