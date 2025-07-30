#!/usr/bin/env python3
"""
🎯 Phase 3 高階市場適應測試
測試 Order Book 深度分析和資金費率情緒指標
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.phase3_market_analyzer import Phase3MarketAnalyzer

async def test_order_book_analysis():
    """測試 Order Book 深度分析"""
    print("🎯 Phase 3 - Order Book 深度分析測試")
    print("=" * 60)
    
    analyzer = Phase3MarketAnalyzer()
    
    async with analyzer as a:
        try:
            # 測試 BTCUSDT Order Book
            order_book = await a.get_order_book_depth("BTCUSDT", limit=20)
            
            print(f"📊 {order_book.symbol} Order Book 深度分析")
            print(f"   時間戳: {order_book.timestamp}")
            print(f"   總買單量: {order_book.total_bid_volume:.4f}")
            print(f"   總賣單量: {order_book.total_ask_volume:.4f}")
            print(f"   壓力比: {order_book.pressure_ratio:.3f}")
            print(f"   市場情緒: {order_book.market_sentiment}")
            print(f"   買賣價差: ${order_book.bid_ask_spread:.2f}")
            print(f"   中間價: ${order_book.mid_price:,.2f}")
            
            print(f"\n🔵 Top 5 買單 (Bids):")
            print(f"{'價格':>12} | {'數量':>10}")
            print("-" * 26)
            for price, qty in order_book.bids[:5]:
                print(f"{price:>12.2f} | {qty:>10.4f}")
            
            print(f"\n🔴 Top 5 賣單 (Asks):")
            print(f"{'價格':>12} | {'數量':>10}")
            print("-" * 26)
            for price, qty in order_book.asks[:5]:
                print(f"{price:>12.2f} | {qty:>10.4f}")
            
        except Exception as e:
            print(f"❌ Order Book 分析失敗: {e}")

async def test_funding_rate_analysis():
    """測試資金費率分析"""
    print("\n🎯 Phase 3 - 資金費率情緒指標測試")
    print("=" * 60)
    
    analyzer = Phase3MarketAnalyzer()
    
    async with analyzer as a:
        try:
            # 測試 BTCUSDT 資金費率
            funding_rate = await a.get_funding_rate("BTCUSDT")
            
            print(f"📊 {funding_rate.symbol} 資金費率分析")
            print(f"   當前費率: {funding_rate.funding_rate:.6f} ({funding_rate.funding_rate*100:.4f}%)")
            print(f"   年化費率: {funding_rate.annual_rate*100:.2f}%")
            print(f"   標記價格: ${funding_rate.mark_price:,.2f}")
            print(f"   情緒判斷: {funding_rate.sentiment}")
            print(f"   市場解讀: {funding_rate.market_interpretation}")
            print(f"   費率時間: {funding_rate.funding_time}")
            print(f"   下次費率: {funding_rate.next_funding_time}")
            
        except Exception as e:
            print(f"❌ 資金費率分析失敗: {e}")

async def test_phase3_comprehensive_analysis():
    """測試 Phase 3 綜合分析"""
    print("\n🎯 Phase 3 - 綜合高階市場分析測試")
    print("=" * 60)
    
    analyzer = Phase3MarketAnalyzer()
    test_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    
    async with analyzer as a:
        for symbol in test_symbols:
            print(f"\n📊 測試 {symbol}")
            print("-" * 40)
            
            try:
                # 獲取 Phase 3 綜合分析
                analysis = await a.get_phase3_analysis(symbol)
                
                print(f"🎯 Phase 3 綜合分析結果:")
                print(f"   符號: {analysis.symbol}")
                print(f"   時間戳: {analysis.timestamp}")
                
                print(f"\n📖 Order Book 分析:")
                print(f"   壓力比: {analysis.order_book.pressure_ratio:.3f}")
                print(f"   市場情緒: {analysis.order_book.market_sentiment}")
                print(f"   買單量: {analysis.order_book.total_bid_volume:.4f}")
                print(f"   賣單量: {analysis.order_book.total_ask_volume:.4f}")
                
                print(f"\n💰 資金費率分析:")
                print(f"   費率: {analysis.funding_rate.funding_rate:.6f}")
                print(f"   情緒: {analysis.funding_rate.sentiment}")
                print(f"   年化: {analysis.funding_rate.annual_rate*100:.2f}%")
                
                print(f"\n🎯 Phase 3 綜合評估:")
                print(f"   綜合情緒: {analysis.combined_sentiment}")
                print(f"   市場壓力評分: {analysis.market_pressure_score:.1f}/100")
                print(f"   交易建議: {analysis.trading_recommendation}")
                print(f"   風險等級: {analysis.risk_level}")
                
            except Exception as e:
                print(f"❌ {symbol} Phase 3 分析失敗: {e}")

async def test_api_endpoint():
    """測試 API 端點"""
    print("\n🌐 Phase 3 API 端點測試")
    print("=" * 60)
    
    try:
        import requests
        
        # 測試 Phase 3 API 端點
        response = requests.get("http://localhost:8000/api/v1/scalping/phase3-market-depth", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Phase 3 API 端點可訪問")
            print(f"階段: {data.get('phase', 'Unknown')}")
            print(f"狀態: {data.get('status', 'Unknown')}")
            print(f"分析數量: {len(data.get('symbol_analyses', []))}")
            
            # 檢查市場概況
            overview = data.get('market_overview', {})
            print(f"\n📊 市場概況:")
            print(f"   分析符號數: {overview.get('total_symbols_analyzed', 0)}")
            print(f"   平均市場壓力: {overview.get('average_market_pressure', 0)}")
            print(f"   主導情緒: {overview.get('dominant_market_sentiment', 'Unknown')}")
            print(f"   市場壓力等級: {overview.get('market_stress_level', 'Unknown')}")
            
            # 檢查第一個符號的詳細數據
            if data.get('symbol_analyses'):
                first_analysis = data['symbol_analyses'][0]
                symbol = first_analysis.get('symbol', 'Unknown')
                
                print(f"\n📈 {symbol} 詳細分析:")
                
                # Order Book 數據
                ob = first_analysis.get('order_book_analysis', {})
                print(f"   壓力比: {ob.get('pressure_ratio', 0):.3f}")
                print(f"   市場情緒: {ob.get('market_sentiment', 'Unknown')}")
                print(f"   中間價: ${ob.get('mid_price', 0):,.2f}")
                
                # 資金費率數據
                fr = first_analysis.get('funding_rate_analysis', {})
                print(f"   資金費率: {fr.get('funding_rate_percentage', 0):.4f}%")
                print(f"   年化費率: {fr.get('annual_rate', 0):.2f}%")
                print(f"   情緒: {fr.get('sentiment', 'Unknown')}")
                
                # Phase 3 評估
                p3 = first_analysis.get('phase3_assessment', {})
                print(f"   綜合情緒: {p3.get('combined_sentiment', 'Unknown')}")
                print(f"   壓力評分: {p3.get('market_pressure_score', 0)}/100")
                print(f"   交易建議: {p3.get('trading_recommendation', 'Unknown')}")
                print(f"   風險等級: {p3.get('risk_level', 'Unknown')}")
        else:
            print(f"❌ API 端點不可訪問: {response.status_code}")
            print(f"回應: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 網路連接失敗: {e}")
    except Exception as e:
        print(f"❌ API 測試失敗: {e}")

if __name__ == "__main__":
    async def main():
        await test_order_book_analysis()
        await test_funding_rate_analysis()
        await test_phase3_comprehensive_analysis()
        await test_api_endpoint()
        
    asyncio.run(main())
