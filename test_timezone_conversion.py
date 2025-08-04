#!/usr/bin/env python3
"""
測試狙擊手策略時間轉換
"""

import asyncio
import sys
import os
sys.path.append('/Users/henrychang/Desktop/Trading-X')

from app.utils.timezone_utils import get_taiwan_now, ensure_taiwan_timezone
from datetime import datetime, timezone
import requests

async def test_timezone_conversion():
    """測試時區轉換功能"""
    print("🕐 測試時區轉換功能")
    print("=" * 40)
    
    # 測試台灣時間獲取
    taiwan_now = get_taiwan_now()
    print(f"台灣時間: {taiwan_now}")
    print(f"ISO格式: {taiwan_now.isoformat()}")
    
    # 測試時區確保
    utc_now = datetime.now(timezone.utc)
    taiwan_converted = ensure_taiwan_timezone(utc_now)
    print(f"UTC時間: {utc_now}")
    print(f"轉換後台灣時間: {taiwan_converted}")
    
    print()

def test_api_time_format():
    """測試API返回的時間格式"""
    print("🌐 測試API時間格式")
    print("=" * 40)
    
    # 測試信號歷史API
    symbols = ['BTCUSDT', 'ETHUSDT']
    
    for symbol in symbols:
        try:
            print(f"\n📊 測試 {symbol} 信號歷史...")
            
            # 測試高精準度信號
            response = requests.get(
                f"http://localhost:8000/api/v1/scalping/signal-history/{symbol}?hours=24&precision_level=high",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                signals = data.get('data', {}).get('signals', [])
                
                if signals:
                    signal = signals[0]
                    created_at = signal.get('created_at')
                    print(f"✅ {symbol} 高精準度信號時間: {created_at}")
                    
                    # 嘗試解析時間
                    if created_at:
                        try:
                            parsed_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            print(f"   解析結果: {parsed_time}")
                            print(f"   時區信息: {parsed_time.tzinfo}")
                        except Exception as e:
                            print(f"   時間解析失敗: {e}")
                else:
                    print(f"ℹ️  {symbol} 高精準度無歷史信號")
            else:
                print(f"❌ {symbol} API請求失敗: {response.status_code}")
                
            # 測試其他精準度信號
            response = requests.get(
                f"http://localhost:8000/api/v1/scalping/signal-history/{symbol}?hours=24&precision_level=other",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                signals = data.get('data', {}).get('signals', [])
                
                if signals:
                    signal = signals[0]
                    created_at = signal.get('created_at')
                    print(f"✅ {symbol} 其他精準度信號時間: {created_at}")
                else:
                    print(f"ℹ️  {symbol} 其他精準度無歷史信號")
                    
        except requests.exceptions.RequestException as e:
            print(f"❌ {symbol} 網絡請求失敗: {e}")
        except Exception as e:
            print(f"❌ {symbol} 測試失敗: {e}")

def test_frontend_time_display():
    """測試前端時間顯示"""
    print("\n🖥️  測試前端時間顯示格式")
    print("=" * 40)
    
    # 模擬前端收到的時間字符串
    test_times = [
        "2024-08-02T14:30:45+08:00",  # 帶時區的ISO格式
        "2024-08-02T14:30:45",       # 不帶時區的ISO格式
        "2024-08-02T06:30:45Z",      # UTC時間
    ]
    
    for time_str in test_times:
        print(f"\n測試時間字符串: {time_str}")
        
        try:
            # 模擬前端的formatTime函數
            if 'Z' in time_str:
                # UTC時間
                date = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            else:
                date = datetime.fromisoformat(time_str)
            
            # 轉換為台灣時間顯示
            taiwan_time = date.strftime('%H:%M')
            taiwan_date = date.strftime('%m/%d')
            
            print(f"  時間顯示: {taiwan_time}")
            print(f"  日期顯示: {taiwan_date}")
            
        except Exception as e:
            print(f"  解析失敗: {e}")

async def main():
    print("🎯 狙擊手策略時間轉換測試")
    print("=" * 50)
    
    # 測試時區轉換
    await test_timezone_conversion()
    
    # 測試API時間格式
    test_api_time_format()
    
    # 測試前端時間顯示
    test_frontend_time_display()
    
    print("\n" + "=" * 50)
    print("✅ 時間轉換測試完成")

if __name__ == "__main__":
    asyncio.run(main())
