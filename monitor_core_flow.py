#!/usr/bin/env python3
"""
實時監控核心 pandas+websocket 流程
"""

import asyncio
import logging
import sys
sys.path.append('/Users/henrychang/Desktop/Trading-X')

from app.services.market_data import MarketDataService
from app.services.realtime_signal_engine import RealtimeSignalEngine

# 設置簡潔的日誌格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)

async def monitor_core_flow():
    """監控核心 pandas+websocket 流程"""
    
    print("🔍 開始監控核心 pandas+websocket 流程...")
    
    try:
        # 創建服務實例
        market_service = MarketDataService()
        signal_engine = RealtimeSignalEngine()
        
        # 初始化
        await signal_engine.initialize(market_service)
        print("✅ 核心服務初始化完成")
        
        # 監控循環
        for i in range(10):  # 監控10次
            print(f"\n--- 第 {i+1} 次檢查 ---")
            
            # 檢查價格獲取
            symbols = ['BTCUSDT', 'ETHUSDT']
            prices = await market_service.get_realtime_prices(symbols)
            
            if prices:
                print(f"📊 價格數據: {len(prices)} 個交易對")
                for symbol, price in prices.items():
                    print(f"   💰 {symbol}: ${price:,.2f}")
            else:
                print("⚠️ 未獲取到價格數據")
            
            # 檢查 WebSocket 數據
            websocket_data = market_service.realtime_data['prices']
            if websocket_data:
                print(f"📡 WebSocket 數據: {len(websocket_data)} 個交易對有數據")
            else:
                print("📡 WebSocket 數據: 暫無數據")
            
            # 檢查信號引擎狀態
            if hasattr(signal_engine, 'latest_prices') and signal_engine.latest_prices:
                print(f"🎯 信號引擎: {len(signal_engine.latest_prices)} 個交易對在追蹤")
            else:
                print("🎯 信號引擎: 暫無追蹤數據")
            
            await asyncio.sleep(3)  # 每3秒檢查一次
            
        print("\n✅ 監控完成，核心流程運行正常")
        
    except Exception as e:
        print(f"❌ 監控失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(monitor_core_flow())
