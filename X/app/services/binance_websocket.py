"""
幣安 WebSocket 即時數據服務
提供即時價格、深度、交易數據串流
"""

import asyncio
import json
import logging
import websockets
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import pandas as pd
from decimal import Decimal

logger = logging.getLogger(__name__)

@dataclass
class TickerData:
    """股票代號數據"""
    symbol: str
    price: float
    price_change: float
    price_change_percent: float
    high_24h: float
    low_24h: float
    volume_24h: float
    timestamp: datetime

@dataclass
class KlineData:
    """K線數據"""
    symbol: str
    interval: str
    open_time: int
    close_time: int
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    trade_count: int
    quote_volume: float
    timestamp: datetime

@dataclass
class DepthData:
    """深度數據"""
    symbol: str
    bids: List[List[float]]  # [[price, quantity], ...]
    asks: List[List[float]]  # [[price, quantity], ...]
    timestamp: datetime

class BinanceWebSocketClient:
    """幣安 WebSocket 客戶端 - 增強版含重連機制"""
    
    def __init__(self):
        self.base_url = "wss://stream.binance.com:9443/ws/"
        self.connections = {}
        self.callbacks = {
            'ticker': [],
            'kline': [],
            'depth': [],
            'trade': []
        }
        self.running = False
        self.reconnect_delay = 5  # 重連延遲秒數
        self.max_reconnect_attempts = 10  # 最大重連次數
        self.connection_health = {}  # 連接健康狀態
        self.ping_interval = 20  # 心跳間隔
        self.subscriptions = {  # 保存訂閱信息用於重連
            'ticker': [],
            'klines': {},
            'depth': []
        }
        
    async def start(self):
        """啟動 WebSocket 服務"""
        self.running = True
        # 啟動健康檢查任務
        asyncio.create_task(self._health_check_loop())
        logger.info("幣安 WebSocket 服務已啟動，含健康檢查")
        
    async def stop(self):
        """停止 WebSocket 服務"""
        self.running = False
        
        # 關閉所有連接
        for key, connection in self.connections.items():
            if connection and not connection.closed:
                await connection.close()
                logger.info(f"已關閉 {key} WebSocket 連接")
        
        self.connections.clear()
        self.connection_health.clear()
        logger.info("幣安 WebSocket 服務已停止")
        
    def add_ticker_callback(self, callback: Callable[[TickerData], None]):
        """添加價格回調函數"""
        self.callbacks['ticker'].append(callback)
        
    def add_kline_callback(self, callback: Callable[[KlineData], None]):
        """添加 K線回調函數"""
        self.callbacks['kline'].append(callback)
        
    def add_depth_callback(self, callback: Callable[[DepthData], None]):
        """添加深度回調函數"""
        self.callbacks['depth'].append(callback)
        
    async def subscribe_ticker(self, symbols: List[str]):
        """訂閱股票代號即時價格 - 含重連機制"""
        self.subscriptions['ticker'] = symbols
        
        # 🔧 修復：分批訂閱避免連接問題
        batch_size = 3  # 每批最多3個symbols
        for i in range(0, len(symbols), batch_size):
            batch_symbols = symbols[i:i + batch_size]
            await self._subscribe_ticker_with_retry(batch_symbols)
            await asyncio.sleep(0.5)  # 短暫延遲避免連接過快
            
    async def _subscribe_ticker_with_retry(self, symbols: List[str], attempt: int = 1):
        """帶重試的價格訂閱"""
        streams = [f"{symbol.lower()}@ticker" for symbol in symbols]
        stream_name = "/".join(streams)
        connection_key = f"ticker_{'_'.join(symbols)}"
        
        try:
            uri = f"{self.base_url}{stream_name}"
            connection = await websockets.connect(
                uri,
                ping_interval=self.ping_interval,
                ping_timeout=10,
                close_timeout=10
            )
            
            self.connections[connection_key] = connection
            self.connection_health[connection_key] = {
                'last_ping': datetime.now(),
                'reconnect_count': attempt - 1,
                'status': 'connected'
            }
            
            asyncio.create_task(self._handle_ticker_stream_with_retry(connection, connection_key, symbols))
            logger.info(f"已訂閱價格數據: {symbols} (嘗試 {attempt})")
            
        except Exception as e:
            logger.error(f"訂閱價格數據失敗 (嘗試 {attempt}): {e}")
            if attempt < self.max_reconnect_attempts and self.running:
                await asyncio.sleep(self.reconnect_delay * attempt)
                await self._subscribe_ticker_with_retry(symbols, attempt + 1)
            
    async def subscribe_klines(self, symbols: List[str], intervals: List[str]):
        """訂閱 K線數據 - 含重連機制"""
        self.subscriptions['klines'][tuple(symbols)] = intervals
        
        # 🔧 修復：分批訂閱避免連接問題
        batch_size = 2  # K線數據更大，每批2個symbols
        for i in range(0, len(symbols), batch_size):
            batch_symbols = symbols[i:i + batch_size]
            await self._subscribe_klines_with_retry(batch_symbols, intervals)
            await asyncio.sleep(0.5)  # 短暫延遲避免連接過快
        
    async def _subscribe_klines_with_retry(self, symbols: List[str], intervals: List[str], attempt: int = 1):
        """帶重試的 K線訂閱"""
        streams = []
        for symbol in symbols:
            for interval in intervals:
                streams.append(f"{symbol.lower()}@kline_{interval}")
        
        stream_name = "/".join(streams)
        connection_key = f"klines_{'_'.join(symbols)}"
        
        try:
            uri = f"{self.base_url}{stream_name}"
            connection = await websockets.connect(
                uri,
                ping_interval=self.ping_interval,
                ping_timeout=10,
                close_timeout=10
            )
            
            self.connections[connection_key] = connection
            self.connection_health[connection_key] = {
                'last_ping': datetime.now(),
                'reconnect_count': attempt - 1,
                'status': 'connected'
            }
            
            asyncio.create_task(self._handle_kline_stream_with_retry(connection, connection_key, symbols, intervals))
            logger.info(f"已訂閱 K線數據: {symbols} - {intervals} (嘗試 {attempt})")
            
        except Exception as e:
            logger.error(f"訂閱 K線數據失敗 (嘗試 {attempt}): {e}")
            if attempt < self.max_reconnect_attempts and self.running:
                await asyncio.sleep(self.reconnect_delay * attempt)
                await self._subscribe_klines_with_retry(symbols, intervals, attempt + 1)
            
    async def subscribe_depth(self, symbols: List[str], speed: str = "100ms"):
        """訂閱深度數據"""
        streams = [f"{symbol.lower()}@depth@{speed}" for symbol in symbols]
        stream_name = "/".join(streams)
        
        try:
            uri = f"{self.base_url}{stream_name}"
            connection = await websockets.connect(uri)
            self.connections[f"depth_{'_'.join(symbols)}"] = connection
            
            asyncio.create_task(self._handle_depth_stream(connection))
            logger.info(f"已訂閱深度數據: {symbols}")
            
        except Exception as e:
            logger.error(f"訂閱深度數據失敗: {e}")
            
    async def _handle_ticker_stream_with_retry(self, connection, connection_key: str, symbols: List[str]):
        """處理價格數據串流 - 含重連機制"""
        try:
            async for message in connection:
                if not self.running:
                    break
                
                # 更新健康狀態
                self.connection_health[connection_key]['last_ping'] = datetime.now()
                self.connection_health[connection_key]['status'] = 'active'
                    
                data = json.loads(message)
                
                # 處理單一或多重數據流
                if isinstance(data, list):
                    for item in data:
                        await self._process_ticker_data(item)
                else:
                    await self._process_ticker_data(data)
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning(f"價格數據連接已關閉: {connection_key}")
            self.connection_health[connection_key]['status'] = 'disconnected'
            await self._handle_reconnection('ticker', symbols)
        except Exception as e:
            logger.error(f"處理價格數據錯誤: {e}")
            self.connection_health[connection_key]['status'] = 'error'
            await self._handle_reconnection('ticker', symbols)
            
    async def _handle_reconnection(self, stream_type: str, symbols: List[str]):
        """處理重連邏輯"""
        if not self.running:
            return
            
        logger.info(f"開始重連 {stream_type} 流: {symbols}")
        
        # 等待一段時間後重連
        await asyncio.sleep(self.reconnect_delay)
        
        if stream_type == 'ticker':
            await self._subscribe_ticker_with_retry(symbols)
        elif stream_type == 'klines':
            intervals = self.subscriptions['klines'].get(tuple(symbols), ['1m'])
            await self._subscribe_klines_with_retry(symbols, intervals)
        elif stream_type == 'depth':
            await self._subscribe_depth_with_retry(symbols)
            
    async def _health_check_loop(self):
        """健康檢查循環"""
        while self.running:
            try:
                await asyncio.sleep(30)  # 每30秒檢查一次
                
                current_time = datetime.now()
                for connection_key, health_info in self.connection_health.items():
                    last_ping = health_info.get('last_ping', current_time)
                    time_diff = (current_time - last_ping).total_seconds()
                    
                    # 如果超過60秒沒有活動，標記為不健康
                    if time_diff > 60:
                        logger.warning(f"連接 {connection_key} 可能不健康，上次活動: {time_diff:.1f}秒前")
                        health_info['status'] = 'unhealthy'
                        
                        # 觸發重連邏輯
                        if connection_key.startswith('ticker_') and 'ticker' in self.subscriptions:
                            await self._handle_reconnection('ticker', self.subscriptions['ticker'])
                            
            except Exception as e:
                logger.error(f"健康檢查錯誤: {e}")
                
    def get_connection_status(self) -> Dict[str, Any]:
        """獲取連接狀態信息"""
        return {
            'total_connections': len(self.connections),
            'health_status': dict(self.connection_health),
            'subscriptions': dict(self.subscriptions),
            'running': self.running
        }
            
    async def _handle_kline_stream_with_retry(self, connection, connection_key: str, symbols: List[str], intervals: List[str]):
        """處理 K線數據串流 - 含重連機制"""
        try:
            async for message in connection:
                if not self.running:
                    break
                
                # 更新健康狀態
                self.connection_health[connection_key]['last_ping'] = datetime.now()
                self.connection_health[connection_key]['status'] = 'active'
                    
                data = json.loads(message)
                
                # 處理單一或多重數據流
                if isinstance(data, list):
                    for item in data:
                        await self._process_kline_data(item)
                else:
                    await self._process_kline_data(data)
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning(f"K線數據連接已關閉: {connection_key}")
            self.connection_health[connection_key]['status'] = 'disconnected'
            await self._handle_reconnection('klines', symbols)
        except Exception as e:
            logger.error(f"處理K線數據錯誤: {e}")
            self.connection_health[connection_key]['status'] = 'error'
            await self._handle_reconnection('klines', symbols)
            
    async def _handle_depth_stream(self, connection):
        """處理深度數據串流"""
        try:
            async for message in connection:
                if not self.running:
                    break
                    
                data = json.loads(message)
                
                # 處理單一或多重數據流
                if isinstance(data, list):
                    for item in data:
                        await self._process_depth_data(item)
                else:
                    await self._process_depth_data(data)
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("深度數據連接已關閉")
        except Exception as e:
            logger.error(f"處理深度數據錯誤: {e}")
            
    async def _process_ticker_data(self, data: Dict):
        """處理單個價格數據"""
        try:
            # 處理直接的事件格式 (單一流)
            if data.get('e') == '24hrTicker':
                ticker_data = TickerData(
                    symbol=data['s'],
                    price=float(data['c']),
                    price_change=float(data['P']),
                    price_change_percent=float(data['P']),
                    high_24h=float(data['h']),
                    low_24h=float(data['l']),
                    volume_24h=float(data['v']),
                    timestamp=datetime.fromtimestamp(data['E'] / 1000)
                )
                
                # 呼叫所有回調函數
                for callback in self.callbacks['ticker']:
                    try:
                        callback(ticker_data)
                    except Exception as e:
                        logger.error(f"價格回調函數錯誤: {e}")
            
            # 處理多流格式 (帶有 stream 屬性)
            elif 'stream' in data and data['stream'].endswith('@ticker'):
                ticker_info = data['data']
                
                ticker_data = TickerData(
                    symbol=ticker_info['s'],
                    price=float(ticker_info['c']),
                    price_change=float(ticker_info['P']),
                    price_change_percent=float(ticker_info['P']),
                    high_24h=float(ticker_info['h']),
                    low_24h=float(ticker_info['l']),
                    volume_24h=float(ticker_info['v']),
                    timestamp=datetime.fromtimestamp(ticker_info['E'] / 1000)
                )
                
                # 呼叫所有回調函數
                for callback in self.callbacks['ticker']:
                    try:
                        callback(ticker_data)
                    except Exception as e:
                        logger.error(f"價格回調函數錯誤: {e}")
                        
        except Exception as e:
            logger.error(f"處理價格數據錯誤: {e}")
            
    async def _process_kline_data(self, data: Dict):
        """處理單個 K線數據"""
        try:
            # 處理直接的事件格式 (單一流)
            if data.get('e') == 'kline':
                kline_info = data['k']
                
                # 只處理已關閉的 K線
                if kline_info['x']:  # x = true 表示此K線已關閉
                    kline_data = KlineData(
                        symbol=kline_info['s'],
                        interval=kline_info['i'],
                        open_time=kline_info['t'],
                        close_time=kline_info['T'],
                        open_price=float(kline_info['o']),
                        high_price=float(kline_info['h']),
                        low_price=float(kline_info['l']),
                        close_price=float(kline_info['c']),
                        volume=float(kline_info['v']),
                        trade_count=kline_info['n'],
                        quote_volume=float(kline_info['q']),
                        timestamp=datetime.fromtimestamp(kline_info['T'] / 1000)
                    )
                    
                    # 呼叫所有回調函數
                    for callback in self.callbacks['kline']:
                        try:
                            callback(kline_data)
                        except Exception as e:
                            logger.error(f"K線回調函數錯誤: {e}")
            
            # 處理多流格式 (帶有 stream 屬性)
            elif 'stream' in data and '@kline_' in data['stream']:
                kline_info = data['data']['k']
                
                # 只處理已關閉的 K線
                if kline_info['x']:  # x = true 表示此K線已關閉
                    kline_data = KlineData(
                        symbol=kline_info['s'],
                        interval=kline_info['i'],
                        open_time=kline_info['t'],
                        close_time=kline_info['T'],
                        open_price=float(kline_info['o']),
                        high_price=float(kline_info['h']),
                        low_price=float(kline_info['l']),
                        close_price=float(kline_info['c']),
                        volume=float(kline_info['v']),
                        trade_count=kline_info['n'],
                        quote_volume=float(kline_info['q']),
                        timestamp=datetime.fromtimestamp(kline_info['T'] / 1000)
                    )
                    
                    # 呼叫所有回調函數
                    for callback in self.callbacks['kline']:
                        try:
                            callback(kline_data)
                        except Exception as e:
                            logger.error(f"K線回調函數錯誤: {e}")
                            
        except Exception as e:
            logger.error(f"處理K線數據錯誤: {e}")
            
    async def _process_depth_data(self, data: Dict):
        """處理單個深度數據"""
        try:
            # 處理直接的事件格式 (單一流)
            if data.get('e') == 'depthUpdate':
                depth_data = DepthData(
                    symbol=data['s'],
                    bids=[[float(price), float(qty)] for price, qty in data['b']],
                    asks=[[float(price), float(qty)] for price, qty in data['a']],
                    timestamp=datetime.fromtimestamp(data['E'] / 1000)
                )
                
                # 呼叫所有回調函數
                for callback in self.callbacks['depth']:
                    try:
                        callback(depth_data)
                    except Exception as e:
                        logger.error(f"深度回調函數錯誤: {e}")
            
            # 處理多流格式 (帶有 stream 屬性)
            elif 'stream' in data and '@depth' in data['stream']:
                depth_info = data['data']
                
                depth_data = DepthData(
                    symbol=depth_info['s'],
                    bids=[[float(price), float(qty)] for price, qty in depth_info['b']],
                    asks=[[float(price), float(qty)] for price, qty in depth_info['a']],
                    timestamp=datetime.fromtimestamp(depth_info['E'] / 1000)
                )
                
                # 呼叫所有回調函數
                for callback in self.callbacks['depth']:
                    try:
                        callback(depth_data)
                    except Exception as e:
                        logger.error(f"深度回調函數錯誤: {e}")
                        
        except Exception as e:
            logger.error(f"處理深度數據錯誤: {e}")

class BinanceDataCollector:
    """幣安數據收集器"""
    
    def __init__(self, on_ticker=None, on_kline=None, on_depth=None):
        self.ws_client = BinanceWebSocketClient()
        self.latest_data = {
            'tickers': {},
            'klines': {},
            'depths': {}
        }
        
        # 設置回調函數
        if on_ticker:
            self.ws_client.add_ticker_callback(on_ticker)
        if on_kline:
            self.ws_client.add_kline_callback(on_kline)
        if on_depth:
            self.ws_client.add_depth_callback(on_depth)
            
        # 添加內部數據更新回調
        self.ws_client.add_ticker_callback(self._update_ticker_data)
        self.ws_client.add_kline_callback(self._update_kline_data)
        self.ws_client.add_depth_callback(self._update_depth_data)
        
    def _update_ticker_data(self, ticker: TickerData):
        """更新價格數據"""
        self.latest_data['tickers'][ticker.symbol] = asdict(ticker)
        
    def _update_kline_data(self, kline: KlineData):
        """更新 K線數據"""
        key = f"{kline.symbol}_{kline.interval}"
        self.latest_data['klines'][key] = asdict(kline)
        
    def _update_depth_data(self, depth: DepthData):
        """更新深度數據"""
        self.latest_data['depths'][depth.symbol] = asdict(depth)
        
    async def start_collecting(self, 
                             symbols: List[str] = None,
                             intervals: List[str] = None):
        """開始收集數據"""
        if symbols is None:
            symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 'SOLUSDT', 'DOGEUSDT']
            
        if intervals is None:
            intervals = ['1m', '5m', '15m', '1h']
            
        await self.ws_client.start()
        
        # 訂閱不同類型的數據
        await self.ws_client.subscribe_ticker(symbols)
        await self.ws_client.subscribe_klines(symbols, intervals)
        await self.ws_client.subscribe_depth(symbols)
        
        logger.info(f"開始收集數據: {symbols}")
        
    async def stop_collecting(self):
        """停止收集數據"""
        await self.ws_client.stop()
        
    def get_latest_ticker(self, symbol: str) -> Optional[Dict]:
        """獲取最新價格數據"""
        return self.latest_data['tickers'].get(symbol)
        
    def get_latest_kline(self, symbol: str, interval: str) -> Optional[Dict]:
        """獲取最新 K線數據"""
        key = f"{symbol}_{interval}"
        return self.latest_data['klines'].get(key)
        
    def get_latest_depth(self, symbol: str) -> Optional[Dict]:
        """獲取最新深度數據"""
        return self.latest_data['depths'].get(symbol)
        
    def get_all_latest_data(self) -> Dict:
        """獲取所有最新數據"""
        return {
            'tickers': dict(self.latest_data['tickers']),
            'klines': dict(self.latest_data['klines']),
            'depths': dict(self.latest_data['depths']),
            'timestamp': datetime.now().isoformat()
        }

# 使用範例
if __name__ == "__main__":
    async def main():
        def on_ticker_update(ticker: TickerData):
            print(f"價格更新: {ticker.symbol} = ${ticker.price:.2f} ({ticker.price_change_percent:+.2f}%)")
            
        def on_kline_update(kline: KlineData):
            print(f"K線更新: {kline.symbol} {kline.interval} 收盤價: ${kline.close_price:.2f}")
            
        def on_depth_update(depth: DepthData):
            best_bid = depth.bids[0][0] if depth.bids else 0
            best_ask = depth.asks[0][0] if depth.asks else 0
            spread = best_ask - best_bid if best_bid and best_ask else 0
            print(f"深度更新: {depth.symbol} 買一: ${best_bid:.2f} 賣一: ${best_ask:.2f} 價差: ${spread:.2f}")
            
        collector = BinanceDataCollector(
            on_ticker=on_ticker_update,
            on_kline=on_kline_update,
            on_depth=on_depth_update
        )
        
        try:
            await collector.start_collecting(['BTCUSDT', 'ETHUSDT'], ['1m', '5m'])
            
            # 運行30秒然後停止
            await asyncio.sleep(30)
            
        finally:
            await collector.stop_collecting()
    
    asyncio.run(main())
