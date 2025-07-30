#!/usr/bin/env python3
"""
調試 WebSocket 連接問題
"""

import asyncio
import json
import logging
from app.services.binance_websocket import BinanceDataCollector

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def debug_websocket():
    """調試 WebSocket 連接"""
    
    def on_ticker_debug(ticker):
        logger.info(f"🎯 收到價格數據: {ticker.symbol} = ${ticker.price:.4f}")
        
    def on_kline_debug(kline):
        logger.info(f"📊 收到K線數據: {kline.symbol} {kline.interval}")
        
    def on_depth_debug(depth):
        logger.info(f"📈 收到深度數據: {depth.symbol}")
    
    try:
        # 創建收集器
        collector = BinanceDataCollector(
            on_ticker=on_ticker_debug,
            on_kline=on_kline_debug,
            on_depth=on_depth_debug
        )
        
        # 啟動收集器
        logger.info("🚀 啟動數據收集器...")
        await collector.start_collecting(
            symbols=['BTCUSDT', 'ETHUSDT'],
            intervals=['1m']
        )
        
        # 等待一段時間觀察數據
        logger.info("⏰ 等待 60 秒收集數據...")
        await asyncio.sleep(60)
        
        # 停止收集器
        await collector.ws_client.stop()
        logger.info("🛑 數據收集器已停止")
        
    except Exception as e:
        logger.error(f"❌ 調試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_websocket())
