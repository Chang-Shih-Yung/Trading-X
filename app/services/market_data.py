import asyncio
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.models import MarketData
from sqlalchemy import desc, select
import logging

logger = logging.getLogger(__name__)

class MarketDataService:
    """市場數據服務"""
    
    def __init__(self):
        """初始化市場數據服務"""
        self.exchanges = {}
        self.running = False
        self.stream_tasks = []
        self._setup_exchanges()
    
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
            print(f"幣安交易所初始化失敗: {e}")
        
        # OKX - 使用公共 API
        try:
            self.exchanges['okx'] = ccxt.okx({
                'sandbox': False,
                'enableRateLimit': True
            })
        except Exception as e:
            print(f"OKX交易所初始化失敗: {e}")
    
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
        
        async with AsyncSessionLocal() as session:
            try:
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
                    session.add(market_data)
                
                await session.commit()
                logger.info(f"儲存 {len(df)} 筆市場數據")
                
            except Exception as e:
                await session.rollback()
                logger.error(f"儲存市場數據失敗: {e}")
    
    async def get_latest_price(self, symbol: str, exchange: str = "binance") -> Optional[float]:
        """獲取最新價格"""
        try:
            if exchange not in self.exchanges:
                return None
            
            ticker = self.exchanges[exchange].fetch_ticker(symbol)
            return float(ticker['last'])
            
        except Exception as e:
            logger.error(f"獲取最新價格失敗: {e}")
            return None
    
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
    
    async def start_real_time_data(self):
        """啟動即時數據串流"""
        self.running = True
        symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'XRP/USDT']
        
        tasks = []
        for symbol in symbols:
            for timeframe in ['1m', '5m', '1h']:
                task = asyncio.create_task(
                    self._stream_kline_data(symbol, timeframe)
                )
                tasks.append(task)
        
        # 儲存任務列表以便後續管理
        self.stream_tasks = tasks
        
        try:
            # 等待所有任務完成
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"啟動串流數據時發生錯誤: {e}")
            # 繼續運行，不要停止服務
    
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
        
        # 取消所有串流任務
        if hasattr(self, 'stream_tasks'):
            for task in self.stream_tasks:
                if not task.done():
                    task.cancel()
        
        for exchange in self.exchanges.values():
            await exchange.close()
        logger.info("市場數據服務已停止")
