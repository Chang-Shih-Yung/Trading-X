"""
即時市場數據 API 端點
提供 WebSocket 支援的即時價格、深度、K線數據
"""

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from typing import List, Optional, Dict, Any
import asyncio
import json
import logging
from datetime import datetime

from app.services.market_data import MarketDataService
from app.services.realtime_signal_engine import realtime_signal_engine, TradingSignalAlert
from app.schemas.market import MarketDataResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# WebSocket 連接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.symbol_subscriptions: Dict[WebSocket, List[str]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.symbol_subscriptions[websocket] = []
        logger.info(f"WebSocket 連接建立，當前連接數: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.symbol_subscriptions:
            del self.symbol_subscriptions[websocket]
        logger.info(f"WebSocket 連接斷開，當前連接數: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            # 簡化狀態檢查，直接嘗試發送
            await websocket.send_text(message)
        except Exception as e:
            # 只有在發送失敗時才移除連接
            logger.debug(f"發送個人消息失敗，移除連接: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        """廣播消息到所有連接的客戶端，自動清理斷開的連接"""
        disconnected = []
        
        # 使用 copy() 避免在迭代時修改列表
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.debug(f"廣播消息失敗，標記連接移除: {e}")
                disconnected.append(connection)
        
        # 批量清理斷開的連接
        for conn in disconnected:
            self.disconnect(conn)
            
    async def broadcast_trading_signal(self, signal: TradingSignalAlert):
        """廣播交易信號到所有連接的客戶端"""
        disconnected = []
        
        signal_message = json.dumps({
            "type": "trading_signal",
            "data": {
                "symbol": signal.symbol,
                "signal_type": signal.signal_type,
                "confidence": round(signal.confidence, 3),
                "entry_price": round(signal.entry_price, 6),
                "stop_loss": round(signal.stop_loss, 6),
                "take_profit": round(signal.take_profit, 6),
                "risk_reward_ratio": round(signal.risk_reward_ratio, 2),
                "indicators_used": signal.indicators_used,
                "reasoning": signal.reasoning,
                "timeframe": signal.timeframe,
                "urgency": signal.urgency,
                "timestamp": signal.timestamp.isoformat()
            },
            "timestamp": datetime.now().isoformat()
        })
        
        for connection in self.active_connections.copy():
            try:
                # 檢查連接狀態
                if connection.client_state.name != "CONNECTED":
                    logger.debug(f"跳過已斷開的連接，狀態: {connection.client_state.name}")
                    disconnected.append(connection)
                    continue
                    
                await connection.send_text(signal_message)
                logger.debug(f"廣播交易信號到客戶端: {signal.symbol} {signal.signal_type}")
                
            except Exception as e:
                logger.error(f"廣播交易信號失敗: {e}")
                disconnected.append(connection)
        
        # 清理斷開的連接
        for conn in disconnected:
            self.disconnect(conn)
            
        logger.info(f"📡 廣播交易信號完成: {signal.symbol} {signal.signal_type} (發送給 {len(self.active_connections)} 個客戶端)")

    async def broadcast_to_subscribers(self, symbol: str, message: str):
        """只向訂閱了特定交易對的客戶端廣播消息"""
        disconnected = []
        
        for connection, symbols in self.symbol_subscriptions.items():
            if symbol in symbols:
                try:
                    # 檢查連接狀態
                    if connection.client_state.name != "CONNECTED":
                        logger.debug(f"跳過已斷開的訂閱連接，狀態: {connection.client_state.name}")
                        disconnected.append(connection)
                        continue
                        
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"向訂閱者廣播失敗: {e}")
                    disconnected.append(connection)
        
        # 清理斷開的連接
        for conn in disconnected:
            self.disconnect(conn)
            
    async def cleanup_invalid_connections(self):
        """清理無效的WebSocket連接"""
        disconnected = []
        
        for connection in self.active_connections.copy():
            try:
                # 簡化連接驗證，只嘗試ping
                await asyncio.wait_for(connection.ping(), timeout=2.0)
            except Exception:
                # ping失敗表示連接無效
                disconnected.append(connection)
        
        # 清理無效連接
        for conn in disconnected:
            self.disconnect(conn)
                
        if disconnected:
            logger.info(f"清理了 {len(disconnected)} 個無效連接，當前有效連接數: {len(self.active_connections)}")
        
    def get_connection_stats(self):
        """獲取連接統計信息"""
        return {
            "total_connections": len(self.active_connections),
            "subscriptions": {
                id(conn): symbols for conn, symbols in self.symbol_subscriptions.items()
            }
        }

manager = ConnectionManager()

@router.get("/prices")
async def get_realtime_prices(
    symbols: Optional[str] = Query(None, description="逗號分隔的交易對列表，如: BTCUSDT,ETHUSDT")
):
    """
    獲取即時價格數據
    
    如果不指定 symbols，返回所有可用的價格數據
    """
    try:
        # 獲取市場數據服務實例
        from main import app
        market_service: MarketDataService = app.state.market_service
        
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(',')]
            result = await market_service.get_multiple_realtime_prices(symbol_list)
        else:
            # 返回所有價格數據
            all_data = await market_service.get_all_realtime_data()
            result = all_data.get('prices', {})
        
        return {
            "success": True,
            "data": {
                "prices": result,
                "websocket_enabled": market_service.websocket_enabled,
                "count": len(result)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取即時價格失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取即時價格失敗: {str(e)}")

@router.get("/depth/{symbol}")
async def get_realtime_depth(symbol: str):
    """獲取指定交易對的即時深度數據"""
    try:
        from main import app
        market_service: MarketDataService = app.state.market_service
        
        depth_data = await market_service.get_realtime_depth(symbol.upper())
        
        if not depth_data:
            raise HTTPException(status_code=404, detail=f"找不到 {symbol} 的深度數據")
        
        return {
            "success": True,
            "data": depth_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取即時深度失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取即時深度失敗: {str(e)}")

@router.get("/klines/{symbol}")
async def get_realtime_klines(
    symbol: str,
    interval: str = Query("1m", description="時間間隔: 1m, 5m, 15m, 1h, 4h, 1d")
):
    """獲取指定交易對的即時K線數據"""
    try:
        from main import app
        market_service: MarketDataService = app.state.market_service
        
        kline_data = await market_service.get_realtime_klines(symbol.upper(), interval)
        
        if not kline_data:
            raise HTTPException(status_code=404, detail=f"找不到 {symbol} {interval} 的K線數據")
        
        return {
            "success": True,
            "data": kline_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取即時K線失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取即時K線失敗: {str(e)}")

@router.get("/summary")
async def get_market_summary():
    """獲取市場總覽數據"""
    try:
        from main import app
        market_service: MarketDataService = app.state.market_service
        
        summary = await market_service.get_market_summary()
        
        return {
            "success": True,
            "data": summary,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取市場總覽失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取市場總覽失敗: {str(e)}")

@router.get("/all")
async def get_all_realtime_data():
    """獲取所有即時數據（價格、深度、K線）"""
    try:
        from main import app
        market_service: MarketDataService = app.state.market_service
        
        all_data = await market_service.get_all_realtime_data()
        
        return {
            "success": True,
            "data": all_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取所有即時數據失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取所有即時數據失敗: {str(e)}")

@router.post("/start")
async def start_realtime_service(
    symbols: Optional[List[str]] = None,
    intervals: Optional[List[str]] = None
):
    """
    啟動即時數據服務
    
    symbols: 要監控的交易對列表，默認為主要交易對
    intervals: 要監控的時間間隔，默認為 ['1m', '5m', '1h']
    """
    try:
        from main import app
        market_service: MarketDataService = app.state.market_service
        
        if symbols is None:
            symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 'DOGEUSDT']
        
        if intervals is None:
            intervals = ['1m', '5m', '1h']
        
        # 在背景啟動即時數據服務
        asyncio.create_task(market_service.start_real_time_data(symbols, intervals))
        
        return {
            "success": True,
            "data": {
                "message": "即時數據服務啟動成功",
                "symbols": symbols,
                "intervals": intervals,
                "websocket_enabled": market_service.websocket_enabled,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"啟動即時數據服務失敗: {e}")
        raise HTTPException(status_code=500, detail=f"啟動即時數據服務失敗: {str(e)}")

@router.post("/stop")
async def stop_realtime_service():
    """停止即時數據服務"""
    try:
        from main import app
        market_service: MarketDataService = app.state.market_service
        
        await market_service.stop()
        
        return {
            "success": True,
            "message": "即時數據服務已停止",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"停止即時數據服務失敗: {e}")
        raise HTTPException(status_code=500, detail=f"停止即時數據服務失敗: {str(e)}")

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket 端點，提供即時數據推送
    
    客戶端可以發送以下格式的消息來訂閱數據：
    {
        "action": "subscribe",
        "symbols": ["BTCUSDT", "ETHUSDT"],
        "data_types": ["prices", "depths", "klines"]
    }
    """
    await manager.connect(websocket)
    
    try:
        from main import app
        market_service: MarketDataService = app.state.market_service
        
        # 發送連接確認
        await manager.send_personal_message(
            json.dumps({
                "type": "connection_established",
                "message": "WebSocket連接已建立",
                "timestamp": datetime.now().isoformat()
            }),
            websocket
        )
        
        # 主要的消息接收循環
        while True:
            try:
                # 接收客戶端消息，設置合理超時
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
                # 解析JSON消息
                try:
                    message = json.loads(data)
                except json.JSONDecodeError:
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "error",
                            "message": "無效的JSON格式",
                            "timestamp": datetime.now().isoformat()
                        }),
                        websocket
                    )
                    continue
                
                # 處理不同類型的消息
                if message.get("action") == "subscribe":
                    symbols = message.get("symbols", [])
                    manager.symbol_subscriptions[websocket] = symbols
                    
                    # 發送訂閱確認
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "subscription_confirmed", 
                            "symbols": symbols,
                            "timestamp": datetime.now().isoformat()
                        }),
                        websocket
                    )
                    
                    # 立即發送當前數據
                    for symbol in symbols:
                        try:
                            price_data = await market_service.get_realtime_price(symbol)
                            if price_data:
                                await manager.send_personal_message(
                                    json.dumps({
                                        "type": "price_update",
                                        "symbol": symbol,
                                        "data": price_data,
                                        "timestamp": datetime.now().isoformat()
                                    }),
                                    websocket
                                )
                        except Exception as e:
                            logger.warning(f"發送 {symbol} 數據失敗: {e}")
                
                elif message.get("action") == "unsubscribe":
                    manager.symbol_subscriptions[websocket] = []
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "unsubscribed",
                            "timestamp": datetime.now().isoformat()
                        }),
                        websocket
                    )
                
                elif message.get("action") == "ping":
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "pong",
                            "timestamp": datetime.now().isoformat()
                        }),
                        websocket
                    )
                    
            except asyncio.TimeoutError:
                # 超時，發送心跳包
                try:
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "heartbeat",
                            "timestamp": datetime.now().isoformat()
                        }),
                        websocket
                    )
                except Exception:
                    # 心跳失敗說明連接已斷開
                    break
                    
            except WebSocketDisconnect:
                # 客戶端主動斷開連接
                break
                
            except Exception as e:
                # 檢查是否是連接斷開相關的錯誤
                error_msg = str(e).lower()
                if any(keyword in error_msg for keyword in ['disconnect', 'closed', 'cannot call', 'connection']):
                    logger.debug(f"WebSocket連接斷開: {e}")
                    break
                else:
                    # 其他錯誤，記錄但繼續處理
                    logger.error(f"處理WebSocket消息錯誤: {e}")
                    try:
                        await manager.send_personal_message(
                            json.dumps({
                                "type": "error",
                                "message": f"處理消息時發生錯誤: {str(e)}",
                                "timestamp": datetime.now().isoformat()
                            }),
                            websocket
                        )
                    except Exception:
                        # 發送錯誤消息失敗，說明連接已斷開
                        break
                
    except WebSocketDisconnect:
        logger.info("WebSocket 客戶端正常斷開連接")
    except Exception as e:
        logger.error(f"WebSocket 處理錯誤: {e}")
    finally:
        # 確保連接被正確清理
        manager.disconnect(websocket)

@router.get("/status")
async def get_realtime_status():
    """獲取即時數據服務狀態"""
    try:
        from main import app
        market_service: MarketDataService = app.state.market_service
        
        return {
            "success": True,
            "data": {
                "service_running": market_service.running,
                "websocket_enabled": market_service.websocket_enabled,
                "active_websocket_connections": len(manager.active_connections),
                "total_symbols": len(market_service.realtime_data['prices']),
                "total_klines": len(market_service.realtime_data['klines']),
                "total_depths": len(market_service.realtime_data['depths']),
                "last_updates": {
                    symbol: timestamp.isoformat() 
                    for symbol, timestamp in market_service.realtime_data['last_updated'].items()
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取服務狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取服務狀態失敗: {str(e)}")

# 背景任務：定期向 WebSocket 客戶端推送數據
async def broadcast_price_updates():
    """定期廣播價格更新到 WebSocket 客戶端"""
    cleanup_counter = 0
    
    while True:
        try:
            # 每6次廣播（1分鐘）執行一次連接清理
            cleanup_counter += 1
            if cleanup_counter >= 6:
                await manager.cleanup_invalid_connections()
                cleanup_counter = 0
            
            if manager.active_connections:
                from main import app
                market_service: MarketDataService = app.state.market_service
                
                # 獲取所有價格數據
                all_data = await market_service.get_all_realtime_data()
                
                if all_data.get('prices'):
                    message = json.dumps({
                        "type": "price_batch_update",
                        "data": all_data,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    await manager.broadcast(message)
            
            await asyncio.sleep(10)  # 每10秒廣播一次，降低頻率
            
        except Exception as e:
            logger.error(f"廣播價格更新錯誤: {e}")
            await asyncio.sleep(15)  # 錯誤時延長等待時間

# 啟動背景廣播任務（在應用啟動時調用）
def start_broadcast_task():
    """啟動廣播任務"""
    asyncio.create_task(broadcast_price_updates())
