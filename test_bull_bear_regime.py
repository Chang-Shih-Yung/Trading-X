#!/usr/bin/env python3
"""
🎯 Phase 2 牛熊市場動態權重測試
測試不同市場條件下的動態權重分配
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.external_market_apis import ExternalMarketAPIs

async def test_bull_bear_scenarios():
    """測試不同牛熊市場情境"""
    print("🎯 牛熊市場動態權重測試")
    print("=" * 60)
    
    api = ExternalMarketAPIs()
    
    # 測試不同幣種在當前市場條件下的表現
    test_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "ADAUSDT"]
    
    for symbol in test_symbols:
        print(f"\n📊 測試 {symbol}")
        print("-" * 40)
        
        try:
            analysis = await api.get_phase2_market_analysis(symbol)
            
            # 顯示市場機制分析
            regime_analysis = analysis.get("market_regime_analysis", {})
            data_weights = analysis.get("data_weights", {})
            bull_bear_indicators = analysis.get("bull_bear_indicators", {})
            
            print(f"🎯 市場機制: {regime_analysis.get('regime', 'UNKNOWN')}")
            print(f"   信心度: {regime_analysis.get('confidence', 0):.1f}%")
            print(f"   調整理由: {data_weights.get('weight_adjustment_reason', 'N/A')}")
            
            print(f"\n📊 動態權重分配:")
            print(f"   幣安即時: {data_weights.get('binance_realtime_weight', 0):.0%}")
            print(f"   技術分析: {data_weights.get('technical_analysis_weight', 0):.0%}")
            print(f"   Fear & Greed: {data_weights.get('fear_greed_weight', 0):.0%}")
            
            print(f"\n🐂🐻 指標評分:")
            print(f"   牛市信號: {bull_bear_indicators.get('bull_score', 0):.1f}")
            print(f"   熊市信號: {bull_bear_indicators.get('bear_score', 0):.1f}")
            print(f"   活躍指標: {len(bull_bear_indicators.get('active_indicators', []))}")
            
            # 價格數據
            binance_data = analysis.get("binance_realtime", {})
            if binance_data:
                price_change = binance_data.get("price_change_percentage_24h", 0)
                activity = binance_data.get("market_activity_score", 0)
                liquidity = binance_data.get("liquidity_score", 0)
                
                print(f"\n💰 市場數據:")
                print(f"   價格: ${binance_data.get('current_price', 0):,.2f}")
                print(f"   24h變動: {price_change:+.2f}%")
                print(f"   活躍度: {activity:.2f}/3.0")
                print(f"   流動性: {liquidity:.2f}/2.0")
                
        except Exception as e:
            print(f"❌ {symbol} 分析失敗: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 牛熊動態權重測試完成")

async def test_scenario_simulation():
    """模擬不同市場情境"""
    print("\n🧪 市場情境模擬測試")
    print("=" * 60)
    
    from app.services.bull_bear_weight_manager import BullBearWeightManager
    
    manager = BullBearWeightManager()
    
    # 測試情境
    scenarios = [
        {
            "name": "強勢牛市",
            "data": {
                "price_change_percentage_24h": 5.2,
                "volume_24h": 50000,
                "trade_count": 3000000,
                "fear_greed_value": 85,
                "atr_percentage": 0.015,
                "market_activity_score": 2.8,
                "liquidity_score": 1.8
            }
        },
        {
            "name": "溫和牛市", 
            "data": {
                "price_change_percentage_24h": 2.1,
                "volume_24h": 25000,
                "trade_count": 1500000,
                "fear_greed_value": 68,
                "atr_percentage": 0.025,
                "market_activity_score": 2.2,
                "liquidity_score": 1.3
            }
        },
        {
            "name": "橫盤震盪",
            "data": {
                "price_change_percentage_24h": -0.3,
                "volume_24h": 15000,
                "trade_count": 800000,
                "fear_greed_value": 50,
                "atr_percentage": 0.03,
                "market_activity_score": 1.8,
                "liquidity_score": 1.1
            }
        },
        {
            "name": "溫和熊市",
            "data": {
                "price_change_percentage_24h": -3.2,
                "volume_24h": 30000,
                "trade_count": 2200000,
                "fear_greed_value": 25,
                "atr_percentage": 0.055,
                "market_activity_score": 2.8,
                "liquidity_score": 0.8
            }
        },
        {
            "name": "恐慌熊市",
            "data": {
                "price_change_percentage_24h": -8.5,
                "volume_24h": 80000,
                "trade_count": 4500000,
                "fear_greed_value": 15,
                "atr_percentage": 0.085,
                "market_activity_score": 3.0,
                "liquidity_score": 0.6
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📊 {scenario['name']} 情境")
        print("-" * 40)
        
        # 分析市場機制
        regime, confidence, indicators = manager.analyze_market_regime(scenario["data"])
        weights = manager.calculate_dynamic_weights(regime, confidence, scenario["data"])
        
        print(f"🎯 市場機制: {regime} (信心度: {confidence:.1f}%)")
        print(f"📊 權重分配:")
        print(f"   幣安即時: {weights.binance_realtime_weight:.0%}")
        print(f"   技術分析: {weights.technical_analysis_weight:.0%}")
        print(f"   Fear & Greed: {weights.fear_greed_weight:.0%}")
        print(f"🔍 調整理由: {weights.justification}")
        
        print(f"📈 市場指標:")
        print(f"   價格變動: {scenario['data']['price_change_percentage_24h']:+.1f}%")
        print(f"   Fear & Greed: {scenario['data']['fear_greed_value']}")
        print(f"   波動率: {scenario['data']['atr_percentage']:.3f}")
        print(f"   活躍度: {scenario['data']['market_activity_score']:.1f}")

if __name__ == "__main__":
    asyncio.run(test_bull_bear_scenarios())
    asyncio.run(test_scenario_simulation())
