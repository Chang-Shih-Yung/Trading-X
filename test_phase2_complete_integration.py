#!/usr/bin/env python3
"""
🎯 Phase 2 牛熊動態權重完整測試
驗證前後端整合的完整性
"""

import asyncio
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.external_market_apis import ExternalMarketAPIs
from app.services.bull_bear_weight_manager import BullBearWeightManager

async def test_complete_phase2_integration():
    """測試 Phase 2 完整整合"""
    print("🎯 Phase 2 牛熊動態權重完整整合測試")
    print("=" * 80)
    
    external_api = ExternalMarketAPIs()
    weight_manager = BullBearWeightManager()
    
    # 測試符號
    test_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    
    for symbol in test_symbols:
        print(f"\n📊 測試 {symbol}")
        print("-" * 60)
        
        try:
            # 1. 獲取 Phase 2 分析
            analysis = await external_api.get_phase2_market_analysis(symbol)
            
            # 2. 顯示核心數據結構
            print("🎯 核心分析結果:")
            print(f"   階段: {analysis.get('phase', 'Unknown')}")
            print(f"   時間戳: {analysis.get('timestamp', 'N/A')}")
            
            # 3. 市場機制分析
            regime_analysis = analysis.get("market_regime_analysis", {})
            print(f"\n🔍 市場機制分析:")
            print(f"   機制: {regime_analysis.get('regime', 'UNKNOWN')}")
            print(f"   信心度: {regime_analysis.get('confidence', 0):.1f}%")
            print(f"   調整理由: {regime_analysis.get('justification', 'N/A')}")
            
            # 4. 動態權重分配
            data_weights = analysis.get("data_weights", {})
            print(f"\n⚖️ 動態權重分配:")
            print(f"   幣安即時: {data_weights.get('binance_realtime_weight', 0):.0%}")
            print(f"   技術分析: {data_weights.get('technical_analysis_weight', 0):.0%}")
            print(f"   Fear & Greed: {data_weights.get('fear_greed_weight', 0):.0%}")
            print(f"   總數據質量: {data_weights.get('total_data_quality', 0):.1f}%")
            
            # 5. 牛熊指標評分
            bull_bear_indicators = analysis.get("bull_bear_indicators", {})
            print(f"\n🐂🐻 牛熊指標評分:")
            print(f"   牛市信號: {bull_bear_indicators.get('bull_score', 0):.1f}")
            print(f"   熊市信號: {bull_bear_indicators.get('bear_score', 0):.1f}")
            print(f"   活躍指標: {bull_bear_indicators.get('active_indicators', [])}")
            
            # 6. 實時市場數據
            binance_data = analysis.get("binance_realtime", {})
            if binance_data:
                print(f"\n💰 實時市場數據:")
                print(f"   價格: ${binance_data.get('current_price', 0):,.2f}")
                print(f"   24h變動: {binance_data.get('price_change_percentage_24h', 0):+.2f}%")
                print(f"   成交量: {binance_data.get('volume_24h', 0):,.0f}")
                print(f"   活躍度: {binance_data.get('market_activity_score', 0):.2f}/3.0")
                print(f"   流動性: {binance_data.get('liquidity_score', 0):.2f}/2.0")
            
            # 7. Fear & Greed 分析
            fg_analysis = analysis.get("fear_greed_analysis", {})
            if fg_analysis:
                print(f"\n😨 Fear & Greed 分析:")
                print(f"   指數值: {fg_analysis.get('value', 0)}/100")
                print(f"   分類: {fg_analysis.get('classification', 'N/A')}")
                print(f"   等級: {fg_analysis.get('level', 'N/A')}")
                print(f"   權重: {fg_analysis.get('weight_in_decision', 0):.0%}")
                print(f"   市場解讀: {fg_analysis.get('market_interpretation', 'N/A')}")
            
            # 8. API 狀態
            print(f"\n🔧 API 狀態:")
            print(f"   狀態: {analysis.get('api_status', 'unknown')}")
            print(f"   數據來源: {analysis.get('data_sources', {})}")
            
        except Exception as e:
            print(f"❌ {symbol} 測試失敗: {e}")
    
    print("\n" + "=" * 80)
    print("🎯 Phase 2 完整整合測試完成")

async def test_frontend_data_structure():
    """測試前端數據結構兼容性"""
    print("\n🌐 前端數據結構兼容性測試")
    print("=" * 80)
    
    try:
        import requests
        
        # 測試 API 端點
        response = requests.get("http://localhost:8000/api/v1/scalping/dynamic-parameters", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ API 端點可訪問")
            print(f"階段: {data.get('phase', 'Unknown')}")
            print(f"狀態: {data.get('status', 'Unknown')}")
            print(f"參數數量: {len(data.get('dynamic_parameters', []))}")
            
            # 檢查第一個參數的數據結構
            if data.get('dynamic_parameters'):
                first_param = data['dynamic_parameters'][0]
                
                print(f"\n📊 {first_param.get('symbol', 'Unknown')} 數據結構檢查:")
                
                # 檢查必要欄位
                required_fields = [
                    "market_state", "dynamic_thresholds", "bull_bear_analysis", 
                    "dynamic_weights", "market_regime"
                ]
                
                for field in required_fields:
                    if field in first_param:
                        print(f"   ✅ {field}: {type(first_param[field]).__name__}")
                    else:
                        print(f"   ❌ {field}: 缺失")
                
                # 檢查 Phase 2 特定欄位
                if "bull_bear_analysis" in first_param:
                    bull_bear = first_param["bull_bear_analysis"]
                    print(f"\n🐂🐻 牛熊分析數據:")
                    print(f"   機制: {bull_bear.get('regime', 'N/A')}")
                    print(f"   信心度: {bull_bear.get('confidence', 0)}")
                    print(f"   牛市評分: {bull_bear.get('bull_score', 0)}")
                    print(f"   熊市評分: {bull_bear.get('bear_score', 0)}")
                
                if "dynamic_weights" in first_param:
                    weights = first_param["dynamic_weights"]
                    print(f"\n⚖️ 動態權重數據:")
                    print(f"   幣安權重: {weights.get('binance_realtime_weight', 0):.1%}")
                    print(f"   技術權重: {weights.get('technical_analysis_weight', 0):.1%}")
                    print(f"   F&G權重: {weights.get('fear_greed_weight', 0):.1%}")
                    print(f"   調整理由: {weights.get('adjustment_reason', 'N/A')}")
                
                if "market_state" in first_param:
                    market = first_param["market_state"]
                    print(f"\n💰 市場狀態數據:")
                    print(f"   價格: ${market.get('current_price', 0):,.2f}")
                    print(f"   F&G指數: {market.get('fear_greed_index', 'N/A')}")
                    print(f"   F&G等級: {market.get('fear_greed_level', 'N/A')}")
                    print(f"   波動率: {market.get('volatility_score', 0):.3f}")
                    print(f"   流動性: {market.get('liquidity_score', 0):.3f}")
                
        else:
            print(f"❌ API 端點不可訪問: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 網路連接失敗: {e}")
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

if __name__ == "__main__":
    # 執行完整測試
    asyncio.run(test_complete_phase2_integration())
    asyncio.run(test_frontend_data_structure())
