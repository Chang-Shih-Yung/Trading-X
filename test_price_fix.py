#!/usr/bin/env python3
"""
測試修復後的 realtime_signal_engine 價格監控功能
"""

import asyncio
import logging
import sys
sys.path.append('/Users/henrychang/Desktop/Trading-X')

from app.services.market_data import MarketDataService
from app.services.realtime_signal_engine import RealtimeSignalEngine

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%H:%M:%S'
)

async def test_fixed_price_monitoring():
    """測試修復後的價格監控功能"""
    
    print("🧪 開始測試修復後的價格監控功能...")
    
    try:
        # 創建服務實例
        market_service = MarketDataService()
        signal_engine = RealtimeSignalEngine()
        
        print("✅ 服務實例創建成功")
        
        # 初始化信號引擎
        await signal_engine.initialize(market_service)
        print("✅ 信號引擎初始化成功")
        
        # 測試批量價格獲取
        test_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        print(f"🔍 測試獲取 {test_symbols} 的價格...")
        
        prices = await market_service.get_realtime_prices(test_symbols)
        print(f"📊 獲取到價格數據: {prices}")
        
        if prices:
            print("✅ 批量價格獲取測試通過")
            for symbol, price in prices.items():
                print(f"   💰 {symbol}: {price}")
        else:
            print("⚠️ 未獲取到價格數據，但沒有崩潰")
        
        # 測試單個價格獲取
        print("🔍 測試單個價格獲取...")
        single_price = await market_service.get_realtime_price('BTCUSDT')
        if single_price:
            print(f"✅ 單個價格獲取成功: {single_price}")
        else:
            print("⚠️ 單個價格獲取返回空值")
        
        print("🎉 所有測試完成，沒有發生 'unhashable type: list' 錯誤")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fixed_price_monitoring())
