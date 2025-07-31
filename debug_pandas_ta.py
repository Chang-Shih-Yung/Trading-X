#!/usr/bin/env python3
"""
調試 pandas-ta 信號生成問題
"""
import asyncio
import requests
import json
from datetime import datetime

async def debug_pandas_ta():
    """調試 pandas-ta 信號生成"""
    
    print("🔍 調試 pandas-ta 信號生成問題")
    print("=" * 60)
    
    # 1. 檢查市場狀態
    print("\n1️⃣ 檢查市場狀態...")
    try:
        market_regime = requests.get("http://localhost:8000/api/v1/enhanced/market-regime/BTCUSDT")
        if market_regime.status_code == 200:
            data = market_regime.json()
            print(f"✅ 市場機制: {data['data']['market_regime']}")
            print(f"✅ 當前價格: ${data['data']['price_data']['price']}")
            print(f"✅ 24小時變化: {data['data']['price_data']['change_percent']}%")
        
        fear_greed = requests.get("http://localhost:8000/api/v1/enhanced/fear-greed-index/BTCUSDT")
        if fear_greed.status_code == 200:
            data = fear_greed.json()
            print(f"✅ Fear & Greed: {data['data']['fear_greed_index']['sentiment']} ({data['data']['fear_greed_index']['score']})")
    except Exception as e:
        print(f"❌ 市場狀態檢查失敗: {e}")
    
    # 2. 檢查 pandas-ta 詳細分析
    print("\n2️⃣ 檢查 pandas-ta 詳細分析...")
    try:
        response = requests.get("http://localhost:8000/api/v1/scalping/pandas-ta-direct")
        if response.status_code == 200:
            data = response.json()
            print(f"📊 總信號數: {data['total_signals']}")
            print(f"📊 數據源: {data['data_source']}")
            print(f"📊 階段: {data['phase']}")
            
            if data['total_signals'] == 0:
                print("❌ 問題：沒有生成任何信號！")
                print("🔍 可能原因：")
                print("   - 動態閾值過於嚴格")
                print("   - 市場數據不足")
                print("   - 技術指標計算問題")
                print("   - 信心度計算問題")
            else:
                print("✅ 信號生成正常")
                for i, signal in enumerate(data['signals'][:3], 1):
                    print(f"   {i}. {signal.get('symbol')} - {signal.get('signal_type')} (信心度: {signal.get('confidence', 0):.3f})")
                    
        else:
            print(f"❌ pandas-ta 端點失敗: HTTP {response.status_code}")
            print(f"   錯誤: {response.text}")
            
    except Exception as e:
        print(f"❌ pandas-ta 檢查失敗: {e}")
    
    # 3. 檢查歷史數據可用性
    print("\n3️⃣ 檢查歷史數據...")
    try:
        # 這裡我們需要直接檢查 MarketDataService 的數據
        print("📊 檢查主要交易對的數據可用性...")
        symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT"]
        
        for symbol in symbols:
            # 通過 scalping signals 端點間接檢查數據
            try:
                resp = requests.get(f"http://localhost:8000/api/v1/signals/latest?symbol={symbol}&hours=1")
                if resp.status_code == 200:
                    sig_data = resp.json()
                    print(f"   ✅ {symbol}: 數據正常 (信號數: {len(sig_data.get('signals', []))})")
                else:
                    print(f"   ⚠️ {symbol}: 數據可能有問題")
            except:
                print(f"   ❌ {symbol}: 無法獲取數據")
                
    except Exception as e:
        print(f"❌ 歷史數據檢查失敗: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 調試總結:")
    print("   如果市場狀態正常但 pandas-ta 信號為0，")
    print("   問題可能在於動態閾值過於嚴格或數據處理邏輯。")
    
if __name__ == "__main__":
    asyncio.run(debug_pandas_ta())
