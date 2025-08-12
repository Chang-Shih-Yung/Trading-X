import asyncio
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Callable
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.models import MarketData
import asyncio
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import threading

# 導入 WebSocket 數據結構
from X.app.services.binance_websocket import BinanceDataCollector, TickerData, KlineData, DepthData
from sqlalchemy import desc, select
import logging
import json

logger = logging.getLogger(__name__)

class MarketDataService:
    """增強版市場數據服務 - 整合 WebSocket 即時數據和增強存儲"""
    
    def __init__(self):
        """初始化市場數據服務"""
        self.exchanges = {}
        self.running = False
        self.stream_tasks = []
        self.binance_collector = None
        self.realtime_data = {
            'prices': {},
            'depths': {},
            'klines': {},
            'last_updated': {}
        }
        self.websocket_enabled = True
        self.enhanced_storage = None  # 將在需要時初始化
        self.data_buffer = []  # 數據緩衝區
        self.buffer_size = 100  # 緩衝區大小
        self.auto_storage = True  # 自動存儲開關
        self._setup_exchanges()
        self._setup_websocket_callbacks()
    
    def _setup_exchanges(self):
        """設置交易所連接（演示模式）"""
        # 幣安 - 使用公共 API (沒有認證)
        try:
            self.exchanges['binance'] = ccxt.binance({
                'sandbox': False,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot'
                }
            })
        except Exception as e:
            logger.error(f"幣安交易所初始化失敗: {e}")
        
        # OKX - 使用公共 API
        try:
            self.exchanges['okx'] = ccxt.okx({
                'sandbox': False,
                'enableRateLimit': True
            })
        except Exception as e:
            logger.error(f"OKX交易所初始化失敗: {e}")
    
    def _setup_websocket_callbacks(self):
        """設置 WebSocket 回調函數"""
        try:
            self.binance_collector = BinanceDataCollector(
                on_ticker=self._on_ticker_update,
                on_kline=self._on_kline_update,
                on_depth=self._on_depth_update
            )
            logger.info("WebSocket 回調函數設置成功")
        except Exception as e:
            logger.error(f"WebSocket 回調函數設置失敗: {e}")
            self.websocket_enabled = False
    
    def _on_ticker_update(self, ticker: TickerData):
        """處理價格更新"""
        try:
            self.realtime_data['prices'][ticker.symbol] = {
                'symbol': ticker.symbol,
                'price': ticker.price,
                'change': ticker.price_change,
                'change_percent': ticker.price_change_percent,
                'high_24h': ticker.high_24h,
                'low_24h': ticker.low_24h,
                'volume_24h': ticker.volume_24h,
                'timestamp': ticker.timestamp.isoformat()
            }
            self.realtime_data['last_updated'][ticker.symbol] = datetime.now()
            logger.debug(f"價格更新: {ticker.symbol} = ${ticker.price:.4f}")
        except Exception as e:
            logger.error(f"處理價格更新錯誤: {e}")
    
    def _on_kline_update(self, kline: KlineData):
        """處理 K線更新 - 使用增強存儲"""
        try:
            key = f"{kline.symbol}_{kline.interval}"
            self.realtime_data['klines'][key] = {
                'symbol': kline.symbol,
                'interval': kline.interval,
                'open_time': kline.open_time,
                'close_time': kline.close_time,
                'open': kline.open_price,
                'high': kline.high_price,
                'low': kline.low_price,
                'close': kline.close_price,
                'volume': kline.volume,
                'trade_count': kline.trade_count,
                'timestamp': kline.timestamp.isoformat()
            }
            
            # 添加到數據緩衝區
            if self.auto_storage:
                kline_data = {
                    'timestamp': kline.timestamp,
                    'open': kline.open_price,
                    'high': kline.high_price,
                    'low': kline.low_price,
                    'close': kline.close_price,
                    'volume': kline.volume,
                    'symbol': kline.symbol,
                    'timeframe': kline.interval
                }
                self.data_buffer.append(kline_data)
                
                # 當緩衝區滿時，批量存儲
                if len(self.data_buffer) >= self.buffer_size:
                    asyncio.create_task(self._flush_data_buffer())
            
            logger.debug(f"K線更新: {kline.symbol} {kline.interval} 收盤: ${kline.close_price:.4f}")
        except Exception as e:
            logger.error(f"處理K線更新錯誤: {e}")
    
    async def _flush_data_buffer(self):
        """清空數據緩衝區並存儲"""
        if not self.data_buffer:
            return
            
        try:
            # 初始化增強存儲（如果尚未初始化）
            if self.enhanced_storage is None:
                from app.services.enhanced_data_storage import EnhancedDataStorage
                self.enhanced_storage = EnhancedDataStorage()
            
            # 複製緩衝區數據並清空
            buffer_copy = self.data_buffer.copy()
            self.data_buffer.clear()
            
            # 使用增強存儲批量處理
            stats = await self.enhanced_storage.store_market_data_batch(buffer_copy, validate=True)
            
            if stats.new_records > 0:
                logger.info(f"批量存儲成功: {stats.new_records} 新記錄, "
                          f"{stats.duplicate_records} 重複, "
                          f"耗時 {stats.storage_time:.2f}秒")
        
        except Exception as e:
            logger.error(f"清空數據緩衝區失敗: {e}")
    
    def _on_depth_update(self, depth: DepthData):
        """處理深度更新"""
        try:
            self.realtime_data['depths'][depth.symbol] = {
                'symbol': depth.symbol,
                'bids': depth.bids[:10],  # 保留前10檔
                'asks': depth.asks[:10],  # 保留前10檔
                'timestamp': depth.timestamp.isoformat()
            }
            logger.debug(f"深度更新: {depth.symbol}")
        except Exception as e:
            logger.error(f"處理深度更新錯誤: {e}")
    
    async def _save_kline_to_db(self, kline: KlineData):
        """將 K線數據保存到資料庫 - 已棄用，使用緩衝區機制"""
        # 這個方法現在由 _flush_data_buffer 替代
        pass
    
    async def get_historical_data(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 1000,
        exchange: str = "binance"
    ) -> pd.DataFrame:
        """獲取歷史K線數據"""
        try:
            if exchange not in self.exchanges:
                raise ValueError(f"不支援的交易所: {exchange}")
            
            exchange_obj = self.exchanges[exchange]
            ohlcv = exchange_obj.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['symbol'] = symbol
            df['timeframe'] = timeframe
            
            return df
            
        except Exception as e:
            logger.error(f"獲取歷史數據失敗: {e}")
            return pd.DataFrame()
    
    async def save_market_data(self, df: pd.DataFrame):
        """儲存市場數據到資料庫"""
        if df.empty:
            return
        
        try:
            async with AsyncSessionLocal() as session:
                # 批量插入以提高性能
                market_data_objects = []
                for _, row in df.iterrows():
                    market_data = MarketData(
                        symbol=row['symbol'],
                        timeframe=row['timeframe'],
                        timestamp=row['timestamp'],
                        open=float(row['open']),
                        high=float(row['high']),
                        low=float(row['low']),
                        close=float(row['close']),
                        volume=float(row['volume'])
                    )
                    market_data_objects.append(market_data)
                
                # 批量添加
                session.add_all(market_data_objects)
                await session.commit()
                logger.info(f"成功儲存 {len(df)} 筆市場數據")
                
        except Exception as e:
            logger.error(f"儲存市場數據失敗: {e}")
            # 不要重新拋出異常，避免中斷主流程
    
    async def get_latest_price(self, symbol: str, exchange: str = "binance") -> Optional[float]:
        """獲取最新價格 - API 兼容性方法"""
        try:
            # 僅從 WebSocket 數據獲取
            if symbol in self.realtime_data['prices']:
                price_data = self.realtime_data['prices'][symbol]
                return price_data.get('price') if price_data else None
            
            # 沒有即時數據時拋出錯誤
            raise ValueError(f"無法獲取 {symbol} 的即時價格數據")
            
        except Exception as e:
            logger.error(f"獲取最新價格失敗: {e}")
            return None

    async def get_realtime_price(self, symbol: str) -> Optional[Dict]:
        """獲取即時價格數據"""
        try:
            # 僅從 WebSocket 數據獲取
            if symbol in self.realtime_data['prices']:
                return self.realtime_data['prices'][symbol]
            
            # 沒有即時數據時拋出錯誤
            raise ValueError(f"無法獲取 {symbol} 的即時價格數據")
            
        except Exception as e:
            logger.error(f"獲取即時價格失敗: {e}")
            return None
    
    async def get_realtime_prices(self, symbols: List[str]) -> Dict[str, float]:
        """批量獲取多個交易對的即時價格"""
        try:
            prices = {}
            for symbol in symbols:
                try:
                    price_data = await self.get_realtime_price(symbol)
                    if price_data and 'price' in price_data:
                        prices[symbol] = price_data['price']
                    else:
                        # 嘗試直接從WebSocket數據獲取
                        if symbol in self.realtime_data['prices']:
                            prices[symbol] = self.realtime_data['prices'][symbol].get('price', 0)
                except Exception as e:
                    logger.debug(f"獲取 {symbol} 價格失敗: {e}")
                    continue
            
            logger.debug(f"批量獲取價格: {len(prices)}/{len(symbols)} 個交易對")
            return prices
            
        except Exception as e:
            logger.error(f"批量獲取即時價格失敗: {e}")
            return {}
    
    async def get_realtime_depth(self, symbol: str) -> Optional[Dict]:
        """獲取即時深度數據"""
        try:
            # 僅從 WebSocket 數據獲取
            if symbol in self.realtime_data['depths']:
                return self.realtime_data['depths'][symbol]
            
            # 沒有即時數據時拋出錯誤
            raise ValueError(f"無法獲取 {symbol} 的即時深度數據")
            
        except Exception as e:
            logger.error(f"獲取即時深度失敗: {e}")
            return None
    
    async def get_realtime_klines(self, symbol: str, interval: str = '1m') -> Optional[Dict]:
        """獲取即時 K線數據"""
        try:
            key = f"{symbol}_{interval}"
            
            # 優先從 WebSocket 數據獲取
            if key in self.realtime_data['klines']:
                return self.realtime_data['klines'][key]
            
            # 備用：從資料庫或API獲取
            df = await self.get_historical_data(symbol, interval, limit=1)
            if not df.empty:
                latest = df.iloc[-1]
                return {
                    'symbol': symbol,
                    'interval': interval,
                    'open': float(latest['open']),
                    'high': float(latest['high']),
                    'low': float(latest['low']),
                    'close': float(latest['close']),
                    'volume': float(latest['volume']),
                    'timestamp': latest['timestamp'].isoformat()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"獲取即時K線失敗: {e}")
            return None
    
    async def get_all_realtime_data(self) -> Dict:
        """獲取所有即時數據"""
        try:
            return {
                'prices': dict(self.realtime_data['prices']),
                'depths': dict(self.realtime_data['depths']),
                'klines': dict(self.realtime_data['klines']),
                'websocket_enabled': self.websocket_enabled,
                'total_symbols': len(self.realtime_data['prices']),
                'last_update': max(
                    self.realtime_data['last_updated'].values(),
                    default=datetime.now()
                ).isoformat(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"獲取即時數據失敗: {e}")
            return {
                'prices': {},
                'depths': {},
                'klines': {},
                'websocket_enabled': False,
                'error': str(e)
            }
    
    async def _get_price_from_api(self, symbol: str, exchange: str = "binance") -> Optional[Dict]:
        """從交易所 API 獲取價格（備用方法）"""
        try:
            if exchange not in self.exchanges:
                return None
            
            ticker = self.exchanges[exchange].fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'price': float(ticker['last']),
                'change': float(ticker['change']) if ticker['change'] else 0,
                'change_percent': float(ticker['percentage']) if ticker['percentage'] else 0,
                'high_24h': float(ticker['high']) if ticker['high'] else 0,
                'low_24h': float(ticker['low']) if ticker['low'] else 0,
                'volume_24h': float(ticker['baseVolume']) if ticker['baseVolume'] else 0,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"從API獲取價格失敗: {e}")
            return None
    
    async def get_multiple_realtime_prices(self, symbols: List[str]) -> Dict[str, Dict]:
        """批量獲取多個代號的即時價格"""
        result = {}
        
        for symbol in symbols:
            price_data = await self.get_realtime_price(symbol)
            if price_data:
                result[symbol] = price_data
                
        return result
    
    async def get_market_summary(self) -> Dict:
        """獲取市場總覽"""
        try:
            summary = {
                'total_symbols': 0,
                'active_symbols': 0,
                'avg_change_percent': 0,
                'top_gainers': [],
                'top_losers': [],
                'total_volume': 0,
                'websocket_status': 'enabled' if self.websocket_enabled else 'disabled',
                'last_update': datetime.now().isoformat()
            }
            
            prices = self.realtime_data['prices']
            if not prices:
                return summary
            
            summary['total_symbols'] = len(prices)
            summary['active_symbols'] = len([p for p in prices.values() if p.get('price', 0) > 0])
            
            # 計算平均漲跌幅
            changes = [p.get('change_percent', 0) for p in prices.values()]
            if changes:
                summary['avg_change_percent'] = round(sum(changes) / len(changes), 2)
            
            # 總成交量
            volumes = [p.get('volume_24h', 0) for p in prices.values()]
            summary['total_volume'] = round(sum(volumes), 2)
            
            # 漲跌幅排序
            sorted_by_change = sorted(
                prices.values(), 
                key=lambda x: x.get('change_percent', 0), 
                reverse=True
            )
            
            summary['top_gainers'] = sorted_by_change[:5]
            summary['top_losers'] = sorted_by_change[-5:]
            
            return summary
            
        except Exception as e:
            logger.error(f"獲取市場總覽失敗: {e}")
            return {'error': str(e)}
    
    async def get_orderbook(self, symbol: str, exchange: str = "binance") -> Optional[Dict]:
        """獲取訂單簿"""
        try:
            if exchange not in self.exchanges:
                return None
            
            orderbook = self.exchanges[exchange].fetch_order_book(symbol)
            return {
                'bids': orderbook['bids'][:10],  # 前10檔買單
                'asks': orderbook['asks'][:10],  # 前10檔賣單
                'timestamp': orderbook['timestamp']
            }
            
        except Exception as e:
            logger.error(f"獲取訂單簿失敗: {e}")
            return None
    
    async def start_real_time_data(self, symbols: List[str] = None, intervals: List[str] = None):
        """啟動即時數據串流 - 支援 WebSocket 和輪詢兩種模式"""
        self.running = True
        
        if symbols is None:
            symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 'DOGEUSDT']
        
        if intervals is None:
            intervals = ['1m', '5m', '1h']
        
        # 嘗試啟動 WebSocket 模式
        if self.websocket_enabled and self.binance_collector:
            try:
                await self.binance_collector.start_collecting(symbols, intervals)
                logger.info(f"WebSocket 即時數據服務已啟動: {symbols}")
                
                # WebSocket 模式下仍然需要一個保持運行的任務
                task = asyncio.create_task(self._websocket_health_check())
                self.stream_tasks.append(task)
                
            except Exception as e:
                logger.error(f"WebSocket 啟動失敗，切換到輪詢模式: {e}")
                self.websocket_enabled = False
        
        # 備用輪詢模式
        if not self.websocket_enabled:
            logger.info("使用輪詢模式獲取市場數據")
            tasks = []
            for symbol in symbols:
                for timeframe in intervals:
                    task = asyncio.create_task(
                        self._stream_kline_data(symbol, timeframe)
                    )
                    tasks.append(task)
            
            self.stream_tasks = tasks
        
        try:
            # 等待所有任務完成
            await asyncio.gather(*self.stream_tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"啟動串流數據時發生錯誤: {e}")
    
    async def _websocket_health_check(self):
        """WebSocket 健康檢查任務"""
        while self.running:
            try:
                await asyncio.sleep(30)  # 每30秒檢查一次
                
                # 檢查數據更新狀態
                current_time = datetime.now()
                stale_symbols = []
                
                for symbol, last_update in self.realtime_data['last_updated'].items():
                    if (current_time - last_update).seconds > 300:  # 5分鐘無更新
                        stale_symbols.append(symbol)
                
                if stale_symbols:
                    logger.warning(f"以下代號數據可能過時: {stale_symbols}")
                
            except Exception as e:
                logger.error(f"WebSocket 健康檢查錯誤: {e}")
                await asyncio.sleep(10)
    
    async def _stream_kline_data(self, symbol: str, timeframe: str):
        """串流K線數據"""
        exchange_name = 'binance'
        if exchange_name not in self.exchanges:
            return
        
        exchange = self.exchanges[exchange_name]
        
        while self.running:
            try:
                # 獲取最新的K線數據
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=1)
                if ohlcv:
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    df['symbol'] = symbol
                    df['timeframe'] = timeframe
                    
                    # 儲存到資料庫
                    await self.save_market_data(df)
                
                # 根據時間框架設定更新頻率
                sleep_time = self._get_sleep_time(timeframe)
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"串流數據錯誤 {symbol} {timeframe}: {e}")
                await asyncio.sleep(10)  # 錯誤時等待10秒
    
    def _get_sleep_time(self, timeframe: str) -> int:
        """根據時間框架獲取睡眠時間"""
        time_map = {
            '1m': 30,   # 30秒更新一次
            '5m': 5,    # 5秒更新一次
            '15m': 60,  # 1分鐘更新一次
            '1h': 600,  # 10分鐘更新一次
            '4h': 1800, # 30分鐘更新一次
            '1d': 3600  # 1小時更新一次
        }
        return time_map.get(timeframe, 60)
    
    async def get_market_data_from_db(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 1000
    ) -> pd.DataFrame:
        """從資料庫獲取市場數據"""
        async with AsyncSessionLocal() as session:
            try:
                stmt = select(MarketData).filter(
                    MarketData.symbol == symbol,
                    MarketData.timeframe == timeframe
                ).order_by(desc(MarketData.timestamp)).limit(limit)
                
                result = await session.execute(stmt)
                data = result.scalars().all()
                
                if not data:
                    return pd.DataFrame()
                
                # 轉換為DataFrame
                df_data = []
                for item in data:
                    df_data.append({
                        'timestamp': item.timestamp,
                        'open': item.open,
                        'high': item.high,
                        'low': item.low,
                        'close': item.close,
                        'volume': item.volume,
                        'symbol': item.symbol,
                        'timeframe': item.timeframe
                    })
                
                df = pd.DataFrame(df_data)
                df = df.sort_values('timestamp').reset_index(drop=True)
                return df
                
            except Exception as e:
                logger.error(f"從資料庫獲取數據失敗: {e}")
                return pd.DataFrame()
    
    async def stop(self):
        """停止服務"""
        self.running = False
        
        # 停止 WebSocket 收集器
        if self.binance_collector:
            try:
                await self.binance_collector.stop_collecting()
                logger.info("WebSocket 數據收集器已停止")
            except Exception as e:
                logger.error(f"停止 WebSocket 收集器時錯誤: {e}")
        
        # 取消所有串流任務
        if hasattr(self, 'stream_tasks'):
            for task in self.stream_tasks:
                if not task.done():
                    task.cancel()
        
        # 安全地關閉交易所連接
        for exchange in self.exchanges.values():
            try:
                if hasattr(exchange, 'close'):
                    await exchange.close()
                else:
                    logger.warning(f"交易所 {exchange.id} 不支援 close() 方法")
            except Exception as e:
                logger.warning(f"關閉交易所 {exchange.id} 時發生錯誤: {e}")
        
        # 清理即時數據
        self.realtime_data = {
            'prices': {},
            'depths': {},
            'klines': {},
            'last_updated': {}
        }
        
        logger.info("市場數據服務已停止")
