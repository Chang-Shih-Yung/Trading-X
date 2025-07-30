#!/usr/bin/env python3
"""
🎯 Phase 3 快速驗證測試
驗證 Order Book 和資金費率完整功能
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_phase3_quick():
    """快速測試 Phase 3 功能"""
    print("🎯 Phase 3 快速驗證測試")
    print("=" * 60)
    
    from app.services.phase3_market_analyzer import Phase3MarketAnalyzer
    
    analyzer = Phase3MarketAnalyzer()
    
    async with analyzer as a:
        # 測試 BTCUSDT
        analysis = await a.get_phase3_analysis("BTCUSDT")
        
        print(f"📊 {analysis.symbol} Phase 3 分析結果:")
        print(f"   時間戳: {analysis.timestamp}")
        
        print(f"\n📖 Order Book 分析:")
        print(f"   總買單量: {analysis.order_book.total_bid_volume:.4f}")
        print(f"   總賣單量: {analysis.order_book.total_ask_volume:.4f}")  
        print(f"   壓力比: {analysis.order_book.pressure_ratio:.3f}")
        print(f"   市場情緒: {analysis.order_book.market_sentiment}")
        print(f"   中間價: ${analysis.order_book.mid_price:,.2f}")
        
        print(f"\n💰 資金費率分析:")
        print(f"   費率: {analysis.funding_rate.funding_rate:.6f} ({analysis.funding_rate.funding_rate*100:.4f}%)")
        print(f"   年化費率: {analysis.funding_rate.annual_rate*100:.2f}%")
        print(f"   情緒: {analysis.funding_rate.sentiment}")
        print(f"   標記價格: ${analysis.funding_rate.mark_price:,.2f}")
        
        print(f"\n🎯 綜合評估:")
        print(f"   綜合情緒: {analysis.combined_sentiment}")
        print(f"   市場壓力評分: {analysis.market_pressure_score:.1f}/100")
        print(f"   交易建議: {analysis.trading_recommendation}")
        print(f"   風險等級: {analysis.risk_level}")
        
        print(f"\n🔵 Top 5 買單:")
        for i, (price, qty) in enumerate(analysis.order_book.bids[:5], 1):
            print(f"   {i}. ${price:,.2f} - {qty:.4f}")
            
        print(f"\n🔴 Top 5 賣單:")
        for i, (price, qty) in enumerate(analysis.order_book.asks[:5], 1):
            print(f"   {i}. ${price:,.2f} - {qty:.4f}")

async def test_api_functionality():
    """測試 API 功能"""
    print(f"\n🌐 API 功能測試")
    print("=" * 60)
    
    try:
        import requests
        
        response = requests.get("http://localhost:8000/api/v1/scalping/phase3-market-depth", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ API 成功回應")
            print(f"階段: {data.get('phase')}")
            print(f"狀態: {data.get('status')}")
            
            overview = data.get('market_overview', {})
            print(f"\n📊 市場概況:")
            print(f"   分析符號數: {overview.get('total_symbols_analyzed')}")
            print(f"   平均壓力: {overview.get('average_market_pressure')}")
            print(f"   主導情緒: {overview.get('dominant_market_sentiment')}")
            print(f"   壓力等級: {overview.get('market_stress_level')}")
            
            symbols = data.get('symbol_analyses', [])
            print(f"\n📈 符號分析數量: {len(symbols)}")
            
            if symbols:
                btc_analysis = symbols[0]
                print(f"\n🔍 {btc_analysis.get('symbol')} 詳細:")
                
                ob = btc_analysis.get('order_book_analysis', {})
                print(f"   壓力比: {ob.get('pressure_ratio'):.3f}")
                print(f"   市場情緒: {ob.get('market_sentiment')}")
                
                fr = btc_analysis.get('funding_rate_analysis', {})
                print(f"   資金費率: {fr.get('funding_rate_percentage'):.4f}%")
                print(f"   年化費率: {fr.get('annual_rate'):.2f}%")
                
                p3 = btc_analysis.get('phase3_assessment', {})
                print(f"   綜合情緒: {p3.get('combined_sentiment')}")
                print(f"   壓力評分: {p3.get('market_pressure_score')}/100")
                print(f"   交易建議: {p3.get('trading_recommendation')}")
                
        else:
            print(f"❌ API 錯誤: {response.status_code}")
            
    except Exception as e:
        print(f"❌ API 測試失敗: {e}")

if __name__ == "__main__":
    async def main():
        await test_phase3_quick()
        await test_api_functionality()
        
    asyncio.run(main())
