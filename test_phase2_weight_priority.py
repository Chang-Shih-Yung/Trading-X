#!/usr/bin/env python3
"""
🎯 Phase 2 權重導向API測試
測試即時API數據權重分配和Alternative.me分類標準
"""

import asyncio
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.external_market_apis import ExternalMarketAPIs
from app.services.dynamic_market_adapter import DynamicMarketAdapter
from app.utils.time_utils import get_taiwan_now_naive

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_phase2_weight_priority():
    """測試 Phase 2 權重優先級API"""
    
    print("🎯 Phase 2 權重導向API測試開始")
    print("=" * 60)
    
    # 初始化服務
    external_apis = ExternalMarketAPIs()
    market_adapter = DynamicMarketAdapter()
    
    # 測試幣種
    test_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT"]
    
    for symbol in test_symbols:
        print(f"\n📊 測試 {symbol}")
        print("-" * 40)
        
        try:
            # 🎯 測試權重導向市場分析
            phase2_analysis = await external_apis.get_phase2_market_analysis(symbol)
            
            print(f"📈 Phase 2 分析結果:")
            print(f"   時間戳: {phase2_analysis.get('timestamp')}")
            print(f"   階段: {phase2_analysis.get('phase')}")
            
            # 權重分配
            weights = phase2_analysis.get("data_weights", {})
            print(f"\n🎯 數據權重分配:")
            print(f"   幣安即時數據: {weights.get('binance_realtime_weight', 0):.0%}")
            print(f"   技術分析: {weights.get('technical_analysis_weight', 0):.0%}")
            print(f"   Fear & Greed: {weights.get('fear_greed_weight', 0):.0%}")
            print(f"   總數據質量: {weights.get('total_data_quality', 0):.1%}")
            
            # 幣安即時數據
            binance_data = phase2_analysis.get("binance_realtime")
            if binance_data:
                print(f"\n🚀 幣安即時數據 (權重65%):")
                print(f"   當前價格: ${binance_data['current_price']:,.2f}")
                print(f"   24h變動: {binance_data['price_change_percentage_24h']:+.2f}%")
                print(f"   24h成交量: {binance_data['volume_24h']:,.0f}")
                print(f"   24h交易次數: {binance_data['trade_count_24h']:,}")
                print(f"   當前價差: ${binance_data['current_spread']:.4f}")
                print(f"   買賣盤比: {binance_data['bid_ask_ratio']:.2f}")
                print(f"   活躍度評分: {binance_data['market_activity_score']:.2f}/3.0")
                print(f"   流動性評分: {binance_data['liquidity_score']:.2f}/2.0")
            else:
                print("❌ 幣安即時數據不可用")
            
            # Fear & Greed 分析
            fg_data = phase2_analysis.get("fear_greed_analysis")
            if fg_data:
                print(f"\n😨 Fear & Greed 分析 (權重{fg_data['weight_in_decision']:.0%}):")
                print(f"   指數值: {fg_data['value']}/100")
                print(f"   API分類: {fg_data['classification']}")
                print(f"   標準等級: {fg_data['level']}")
                print(f"   市場解讀: {fg_data['market_interpretation']}")
                print(f"   上次更新: {fg_data['last_updated']}")
            else:
                print("❌ Fear & Greed 數據不可用")
            
            # 綜合評分
            market_score = phase2_analysis.get("market_score", 0)
            print(f"\n📊 綜合市場評分: {market_score:.1f}/100.0")
            
            # 🎯 測試動態市場狀態（整合權重分析）
            print(f"\n🔧 動態市場狀態分析:")
            market_state = await market_adapter.get_market_state(symbol)
            
            print(f"   市場機制: {market_state.market_regime} (信心度: {market_state.regime_confidence:.1%})")
            print(f"   F&G指數: {market_state.fear_greed_index} ({market_state.fear_greed_level})")
            print(f"   波動率評分: {market_state.volatility_score:.2f}/3.0")
            print(f"   成交量強度: {market_state.volume_strength:.2f}/3.0")
            print(f"   流動性評分: {market_state.liquidity_score:.2f}/2.0")
            print(f"   情緒倍數: {market_state.sentiment_multiplier:.3f}")
            print(f"   ATR百分比: {market_state.atr_percentage:.4f}")
            
        except Exception as e:
            print(f"❌ {symbol} 測試失敗: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Phase 2 權重導向API測試完成")

async def test_fear_greed_classifications():
    """測試 Alternative.me Fear & Greed 分類標準"""
    
    print("\n😨 Alternative.me Fear & Greed 分類測試")
    print("=" * 50)
    
    external_apis = ExternalMarketAPIs()
    
    # 測試分類邊界值
    test_values = [10, 25, 49, 50, 51, 74, 75, 90]
    
    print("數值\t分類\t\t權重\t市場解讀")
    print("-" * 50)
    
    for value in test_values:
        level = external_apis._get_alternative_fear_greed_level(value)
        weight = external_apis._calculate_fear_greed_weight(value)
        interpretation = external_apis._get_market_interpretation(value)
        
        print(f"{value}\t{level:15s}\t{weight:.0%}\t{interpretation[:30]}...")
    
    print("\n✅ 分類標準驗證完成")

async def test_real_api_calls():
    """測試真實API調用"""
    
    print("\n🌐 真實API調用測試")
    print("=" * 40)
    
    external_apis = ExternalMarketAPIs()
    
    # 測試即時Fear & Greed
    print("📞 調用 Alternative.me API...")
    fg_analysis = await external_apis.get_fear_greed_analysis()
    
    print(f"✅ Fear & Greed 結果:")
    print(f"   值: {fg_analysis.value}")
    print(f"   分類: {fg_analysis.value_classification}")
    print(f"   等級: {fg_analysis.fear_greed_level}")
    print(f"   權重: {fg_analysis.weight_in_decision:.1%}")
    print(f"   解讀: {fg_analysis.market_interpretation}")
    
    # 測試即時幣安數據
    print(f"\n📞 調用 Binance API (BTCUSDT)...")
    binance_data = await external_apis.get_binance_realtime_data("BTCUSDT")
    
    if binance_data:
        print(f"✅ Binance 即時數據:")
        print(f"   價格: ${binance_data.current_price:,.2f}")
        print(f"   24h變動: {binance_data.price_change_percentage_24h:+.2f}%")
        print(f"   交易次數: {binance_data.trade_count:,}")
        print(f"   買價: ${binance_data.bid_price:,.2f}")
        print(f"   賣價: ${binance_data.ask_price:,.2f}")
    else:
        print("❌ Binance 數據獲取失敗")

if __name__ == "__main__":
    async def main():
        await test_phase2_weight_priority()
        await test_fear_greed_classifications()
        await test_real_api_calls()
    
    asyncio.run(main())
