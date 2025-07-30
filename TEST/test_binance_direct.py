#!/usr/bin/env python3
"""
測試幣安 WebSocket 直接連接
"""

import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_binance_websocket():
    """直接測試幣安 WebSocket 連接"""
    
    # 幣安 WebSocket 端點
    uri = "wss://stream.binance.com:9443/ws/btcusdt@ticker"
    
    try:
        logger.info(f"嘗試連接到: {uri}")
        
        async with websockets.connect(uri, ping_interval=20, ping_timeout=10) as websocket:
            logger.info("✅ 成功連接到幣安 WebSocket")
            
            # 接收一些消息
            for i in range(5):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10)
                    data = json.loads(message)
                    
                    logger.info(f"接收消息 {i+1}:")
                    logger.info(f"  Symbol: {data.get('s', 'N/A')}")
                    logger.info(f"  Price: {data.get('c', 'N/A')}")
                    logger.info(f"  Change: {data.get('P', 'N/A')}%")
                    
                except asyncio.TimeoutError:
                    logger.warning("等待消息超時")
                    break
                except Exception as e:
                    logger.error(f"處理消息錯誤: {e}")
                    break
                    
    except Exception as e:
        logger.error(f"❌ 連接失敗: {e}")
        logger.error(f"錯誤類型: {type(e)}")

if __name__ == "__main__":
    asyncio.run(test_binance_websocket())
