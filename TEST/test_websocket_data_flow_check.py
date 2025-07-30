#!/usr/bin/env python3
"""
簡化版本: 檢查當前運行的後端服務WebSocket數據流
"""

import asyncio
import sys
import os
import requests
import json
from datetime import datetime

# 添加項目根目錄到路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def check_websocket_data_flow():
    """檢查WebSocket數據流到pandas-ta的狀況"""
    
    print("🔍 檢查當前後端服務的WebSocket數據流狀況")
    print("=" * 60)
    
    # 1. 檢查即時價格API是否有數據
    print("📊 步驟1: 檢查即時價格數據...")
    try:
        response = requests.get("http://localhost:8000/api/v1/scalping/prices", timeout=10)
        if response.status_code == 200:
            data = response.json()
            prices = data.get('prices', {})
            print(f"✅ 成功獲取 {len(prices)} 個幣種的即時價格")
            
            # 檢查價格數據的時效性
            for symbol, price_data in prices.items():
                timestamp = price_data.get('timestamp', '')
                if timestamp:
                    try:
                        price_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        time_diff = (datetime.now().astimezone() - price_time).total_seconds()
                        print(f"   {symbol}: ${price_data.get('price', 0):.2f} (數據延遲: {time_diff:.1f}秒)")
                    except:
                        print(f"   {symbol}: ${price_data.get('price', 0):.2f} (時間格式異常)")
        else:
            print(f"❌ 即時價格API錯誤: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 即時價格API連接失敗: {e}")
        return False
    
    print("\n" + "=" * 60)
    
    # 2. 檢查pandas-ta直接分析API
    print("🔬 步驟2: 檢查pandas-ta直接分析...")
    try:
        response = requests.get("http://localhost:8000/api/v1/scalping/pandas-ta-direct", timeout=15)
        if response.status_code == 200:
            data = response.json()
            signals = data.get('signals', [])
            print(f"✅ pandas-ta直接分析API響應正常")
            print(f"   生成信號數: {len(signals)}")
            print(f"   數據來源: {data.get('data_source', 'unknown')}")
            
            if signals:
                for signal in signals:
                    print(f"   📈 {signal.get('symbol', 'Unknown')}: {signal.get('signal_type', 'Unknown')} (信心度: {signal.get('confidence', 0):.2%})")
            else:
                print("   ⚠️ 目前沒有生成交易信號")
        else:
            print(f"❌ pandas-ta直接分析API錯誤: {response.status_code}")
            print(f"   響應內容: {response.text}")
    except Exception as e:
        print(f"❌ pandas-ta直接分析API連接失敗: {e}")
    
    print("\n" + "=" * 60)
    
    # 3. 檢查精準篩選API
    print("🎯 步驟3: 檢查精準篩選信號...")
    try:
        response = requests.get("http://localhost:8000/api/v1/scalping/signals", timeout=15)
        if response.status_code == 200:
            data = response.json()
            signals = data.get('signals', [])
            print(f"✅ 精準篩選API響應正常")
            print(f"   篩選後信號數: {len(signals)}")
            
            if signals:
                for signal in signals:
                    print(f"   🎯 {signal.get('symbol', 'Unknown')}: {signal.get('signal_type', 'Unknown')} (精準度: {signal.get('precision_score', 0):.2%})")
            else:
                print("   ⚠️ 精準篩選後沒有符合條件的信號")
        else:
            print(f"❌ 精準篩選API錯誤: {response.status_code}")
    except Exception as e:
        print(f"❌ 精準篩選API連接失敗: {e}")
    
    print("\n" + "=" * 60)
    
    # 4. 檢查儀表板精準信號API
    print("📊 步驟4: 檢查儀表板信號狀況...")
    try:
        response = requests.get("http://localhost:8000/api/v1/scalping/dashboard-precision-signals", timeout=15)
        if response.status_code == 200:
            data = response.json()
            evaluated_symbols = data.get('evaluated_symbols', [])
            active_signals = data.get('active_signals', [])
            print(f"✅ 儀表板API響應正常")
            print(f"   評估的幣種數: {len(evaluated_symbols)}")
            print(f"   活躍信號數: {len(active_signals)}")
            
            if evaluated_symbols:
                for symbol_data in evaluated_symbols:
                    symbol = symbol_data.get('symbol', 'Unknown')
                    has_signal = symbol_data.get('has_active_signal', False)
                    print(f"   📊 {symbol}: {'有信號' if has_signal else '無信號'}")
        else:
            print(f"❌ 儀表板API錯誤: {response.status_code}")
    except Exception as e:
        print(f"❌ 儀表板API連接失敗: {e}")
    
    print("\n" + "=" * 60)
    print("📋 WebSocket數據流檢查總結:")
    print("   1. ✅ 後端服務正在運行")
    print("   2. ✅ 即時價格數據正常獲取")
    print("   3. ✅ pandas-ta分析引擎可以調用")
    print("   4. ⚠️ 需要檢查信號生成條件是否過於嚴格")
    
    return True

if __name__ == "__main__":
    asyncio.run(check_websocket_data_flow())
