#!/usr/bin/env python3
"""
全面測試狙擊手策略時間轉換
"""

import asyncio
import sys
import os
sys.path.append('/Users/henrychang/Desktop/Trading-X')

import requests
from datetime import datetime
import json

def test_all_precision_levels():
    """測試所有精準度等級的時間轉換"""
    print("🎯 測試所有精準度等級的時間轉換")
    print("=" * 50)
    
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
    precision_levels = ['high', 'other', 'all']
    
    for symbol in symbols:
        print(f"\n📊 測試 {symbol}:")
        
        for level in precision_levels:
            try:
                response = requests.get(
                    f"http://localhost:8000/api/v1/scalping/signal-history/{symbol}",
                    params={
                        'hours': 24,
                        'precision_level': level
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    signals = data.get('data', {}).get('signals', [])
                    start_time = data.get('data', {}).get('start_time', '')
                    end_time = data.get('data', {}).get('end_time', '')
                    
                    print(f"  {level:>5} 精準度: {len(signals):>2} 個信號")
                    
                    if signals:
                        latest_signal = signals[0]
                        created_at = latest_signal.get('created_at', '')
                        print(f"        最新信號時間: {created_at}")
                        
                        # 驗證時間格式
                        if '+08:00' in created_at:
                            print(f"        ✅ 包含台灣時區標記")
                        else:
                            print(f"        ⚠️  未包含時區標記")
                    
                    # 檢查時間範圍
                    if '+08:00' in start_time and '+08:00' in end_time:
                        print(f"        ✅ 時間範圍使用台灣時區")
                    else:
                        print(f"        ⚠️  時間範圍未使用台灣時區")
                
                else:
                    print(f"  {level:>5} 精準度: API錯誤 {response.status_code}")
                    
            except Exception as e:
                print(f"  {level:>5} 精準度: 請求失敗 - {e}")

def test_smart_layer_signals():
    """測試智能分層信號的時間轉換"""
    print("\n🎯 測試智能分層信號時間")
    print("=" * 50)
    
    try:
        response = requests.get(
            "http://localhost:8000/api/v1/scalping/smart-layer-signals",
            params={
                'symbols': 'BTCUSDT,ETHUSDT',
                'strategy_mode': 'precision'
            },
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            signals = data.get('data', {}).get('signals', [])
            
            print(f"獲取到 {len(signals)} 個智能分層信號")
            
            for signal in signals[:3]:  # 只顯示前3個
                symbol = signal.get('symbol', 'Unknown')
                created_at = signal.get('created_at', '')
                expires_at = signal.get('expires_at', '')
                
                print(f"\n  {symbol}:")
                print(f"    創建時間: {created_at}")
                print(f"    過期時間: {expires_at}")
                
                # 檢查時區標記
                if '+08:00' in created_at:
                    print(f"    ✅ 創建時間包含台灣時區")
                else:
                    print(f"    ⚠️  創建時間未包含時區標記")
                    
                if '+08:00' in expires_at:
                    print(f"    ✅ 過期時間包含台灣時區")
                else:
                    print(f"    ⚠️  過期時間未包含時區標記")
        else:
            print(f"❌ API錯誤: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 請求失敗: {e}")

def test_frontend_compatibility():
    """測試前端兼容性"""
    print("\n🖥️  測試前端時間解析兼容性")
    print("=" * 50)
    
    # 模擬API返回的時間格式
    test_times = [
        "2025-08-02T05:09:09+08:00",     # 完整的台灣時間
        "2025-08-02T05:09:09",          # 無時區信息
        "2025-08-01T21:09:09Z",         # UTC時間
        "2025-08-02T05:09:09.325332+08:00",  # 帶毫秒的台灣時間
    ]
    
    for i, time_str in enumerate(test_times, 1):
        print(f"\n測試 {i}: {time_str}")
        
        try:
            # JavaScript new Date() 行為模擬
            date = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            
            # 模擬前端的formatTime和formatDate函數
            time_display = date.strftime('%H:%M')
            date_display = date.strftime('%m/%d')
            
            print(f"  前端顯示 - 時間: {time_display}, 日期: {date_display}")
            print(f"  ✅ 解析成功")
            
        except Exception as e:
            print(f"  ❌ 解析失敗: {e}")

def main():
    print("🎯 狙擊手策略完整時間轉換測試")
    print("=" * 60)
    
    # 測試所有精準度等級
    test_all_precision_levels()
    
    # 測試智能分層信號
    test_smart_layer_signals()
    
    # 測試前端兼容性
    test_frontend_compatibility()
    
    print("\n" + "=" * 60)
    print("✅ 完整時間轉換測試完成")
    print("\n💡 確認事項:")
    print("   1. 所有時間都應該包含 +08:00 時區標記")
    print("   2. 前端應該能正確解析並顯示台灣時間")
    print("   3. 高精準度、其他精準度、全部信號都應該正確處理時間")

if __name__ == "__main__":
    main()
