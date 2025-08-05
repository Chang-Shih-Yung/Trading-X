"""
🎯 Trading X - 真實幣安API數據測試
驗證 Binance API 連接和數據獲取功能
"""

import asyncio
import logging
import json
from datetime import datetime
from binance_data_connector import binance_connector
from real_data_signal_quality_engine import real_data_engine

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_binance_data_connection():
    """測試幣安數據連接"""
    print("🚀 開始測試幣安API數據連接...")
    
    symbol = "BTCUSDT"
    
    try:
        async with binance_connector as connector:
            print(f"\n📊 測試 {symbol} 的各項數據源...")
            
            # 1. 測試基礎價格數據
            print("\n1. 獲取當前價格...")
            current_price = await connector.get_ticker_price(symbol)
            print(f"   當前價格: ${current_price:,.2f}" if current_price else "   價格獲取失敗")
            
            # 2. 測試24小時數據
            print("\n2. 獲取24小時數據...")
            ticker_24h = await connector.get_24hr_ticker(symbol)
            if ticker_24h:
                print(f"   24h價格變動: {ticker_24h.get('priceChangePercent', 'N/A')}%")
                print(f"   24h成交量: {float(ticker_24h.get('volume', 0)):,.2f}")
                print(f"   24h最高價: ${float(ticker_24h.get('highPrice', 0)):,.2f}")
                print(f"   24h最低價: ${float(ticker_24h.get('lowPrice', 0)):,.2f}")
            else:
                print("   24小時數據獲取失敗")
            
            # 3. 測試K線數據
            print("\n3. 獲取K線價格序列...")
            price_series = await connector.calculate_price_series(symbol, 10)
            if price_series:
                print(f"   獲取了 {len(price_series)} 個價格點")
                print(f"   最近5個價格: {[f'${p:,.2f}' for p in price_series[-5:]]}")
            else:
                print("   K線數據獲取失敗")
            
            # 4. 測試訂單簿
            print("\n4. 獲取訂單簿數據...")
            order_book = await connector.get_order_book(symbol, 5)
            if order_book:
                bids = order_book.get("bids", [])[:3]
                asks = order_book.get("asks", [])[:3]
                print(f"   前3檔買單: {[[f'${float(b[0]):,.2f}', f'{float(b[1]):.4f}'] for b in bids]}")
                print(f"   前3檔賣單: {[[f'${float(a[0]):,.2f}', f'{float(a[1]):.4f}'] for a in asks]}")
            else:
                print("   訂單簿數據獲取失敗")
            
            # 5. 測試資金費率
            print("\n5. 獲取資金費率...")
            funding_rate = await connector.get_funding_rate(symbol)
            if funding_rate:
                rate = float(funding_rate.get("fundingRate", 0))
                print(f"   當前資金費率: {rate * 100:.6f}%")
                print(f"   下次結算時間: {funding_rate.get('fundingTime', 'N/A')}")
            else:
                print("   資金費率獲取失敗")
            
            # 6. 測試波動性分析
            print("\n6. 計算波動性指標...")
            volatility_metrics = await connector.calculate_volatility_metrics(symbol)
            if volatility_metrics:
                print(f"   當前波動率: {volatility_metrics.get('current_volatility', 0) * 100:.4f}%")
                print(f"   24h價格變動: {volatility_metrics.get('price_change_24h', 0) * 100:.4f}%")
                print(f"   收益率標準差: {volatility_metrics.get('returns_std', 0) * 100:.6f}%")
            else:
                print("   波動性指標計算失敗")
            
            # 7. 測試成交量分析
            print("\n7. 計算成交量分析...")
            volume_analysis = await connector.calculate_volume_analysis(symbol)
            if volume_analysis:
                print(f"   當前成交量: {volume_analysis.get('current_volume', 0):,.2f}")
                print(f"   平均成交量: {volume_analysis.get('average_volume', 0):,.2f}")
                print(f"   成交量趨勢: {volume_analysis.get('volume_trend', 0) * 100:.2f}%")
                print(f"   成交量比率: {volume_analysis.get('volume_ratio', 0):.2f}")
            else:
                print("   成交量分析失敗")
            
            # 8. 測試綜合市場數據
            print("\n8. 獲取綜合市場數據...")
            comprehensive_data = await connector.get_comprehensive_market_data(symbol)
            if comprehensive_data:
                completeness = comprehensive_data.get("data_completeness", 0)
                quality = comprehensive_data.get("data_quality", "unknown")
                print(f"   數據完整性: {completeness * 100:.1f}%")
                print(f"   數據質量: {quality}")
                
                if "error" in comprehensive_data:
                    print(f"   錯誤信息: {comprehensive_data['error']}")
            else:
                print("   綜合市場數據獲取失敗")
            
            print(f"\n✅ 幣安API數據連接測試完成！")
            return True
            
    except Exception as e:
        print(f"\n❌ 幣安API連接測試失敗: {e}")
        return False

async def test_real_signal_quality_engine():
    """測試真實數據信號質量引擎"""
    print("\n🎯 開始測試真實數據信號質量引擎...")
    
    symbol = "BTCUSDT"
    
    try:
        # 1. 測試即時數據收集
        print("\n1. 收集即時真實數據...")
        data_snapshot = await real_data_engine.collect_real_time_data(symbol)
        
        print(f"   數據時間戳: {data_snapshot.timestamp}")
        print(f"   數據完整性: {data_snapshot.data_integrity.value}")
        print(f"   缺失組件: {data_snapshot.missing_components}")
        print(f"   技術指標數量: {len(data_snapshot.technical_indicators)}")
        
        # 顯示一些關鍵技術指標
        key_indicators = ["current_price", "price_change_24h", "volume_24h", "volatility", "funding_rate"]
        for indicator in key_indicators:
            value = data_snapshot.technical_indicators.get(indicator)
            if value is not None:
                print(f"   {indicator}: {value}")
        
        # 2. 測試第一階段信號候選者生成
        print("\n2. 生成信號候選者...")
        candidates = await real_data_engine.stage1_signal_candidate_pool(data_snapshot)
        
        print(f"   生成了 {len(candidates)} 個信號候選者")
        for i, candidate in enumerate(candidates[:3]):  # 顯示前3個
            print(f"   候選者 {i+1}:")
            print(f"     來源: {candidate.source_type}")
            print(f"     信號強度: {candidate.raw_signal_strength:.3f}")
            print(f"     信心度: {candidate.confidence_score:.3f}")
            print(f"     優先級: {candidate.preliminary_priority.value}")
        
        # 3. 測試第二階段EPL決策
        print("\n3. 執行EPL決策層...")
        market_context = {
            "market_trend": 0.7,
            "volatility": 0.5,
            "liquidity": 0.8,
            "market_uncertainty": 0.3,
            "market_activity": 0.9
        }
        
        decisions = await real_data_engine.stage2_epl_decision_layer(candidates, market_context)
        
        print(f"   產生了 {len(decisions)} 個執行決策")
        for i, decision in enumerate(decisions[:3]):  # 顯示前3個
            print(f"   決策 {i+1}:")
            print(f"     最終優先級: {decision.final_priority.value}")
            print(f"     執行信心度: {decision.execution_confidence:.3f}")
            print(f"     建議動作: {decision.recommended_action}")
            print(f"     數據支撐水平: {decision.data_support_level}")
        
        print(f"\n✅ 真實數據信號質量引擎測試完成！")
        return True
        
    except Exception as e:
        print(f"\n❌ 信號質量引擎測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主測試流程"""
    print("=" * 60)
    print("🎯 Trading X - 真實幣安API數據驗證測試")
    print("=" * 60)
    
    # 測試幣安API連接
    api_test_result = await test_binance_data_connection()
    
    # 測試信號質量引擎
    engine_test_result = await test_real_signal_quality_engine()
    
    print("\n" + "=" * 60)
    print("📊 測試結果總結:")
    print(f"   幣安API連接: {'✅ 成功' if api_test_result else '❌ 失敗'}")
    print(f"   信號質量引擎: {'✅ 成功' if engine_test_result else '❌ 失敗'}")
    
    if api_test_result and engine_test_result:
        print("\n🎉 所有測試通過！系統已成功連接真實幣安API數據")
    else:
        print("\n⚠️  部分測試失敗，請檢查網路連接和API配置")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
