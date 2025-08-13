#!/usr/bin/env python3
"""
🎯 Trading X - 歷史數據擴展模組
擴展Phase1A歷史數據獲取能力，支援多時間框架回測
保持原有JSON Schema不變，純數據擴展
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

class HistoricalDataExtension:
    """歷史數據擴展器 - 支援回測用歷史數據獲取"""
    
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3/klines"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _interval_to_minutes(self, interval: str) -> int:
        """時間間隔轉換為分鐘數"""
        interval_map = {
            "1m": 1, "3m": 3, "5m": 5, "15m": 15, "30m": 30,
            "1h": 60, "2h": 120, "4h": 240, "6h": 360, "8h": 480, "12h": 720,
            "1d": 1440, "3d": 4320, "1w": 10080, "1M": 43200
        }
        return interval_map.get(interval, 1)
    
    async def fetch_extended_historical_data(self, 
                                           symbol: str, 
                                           interval: str = "1m", 
                                           days_back: int = 30) -> List[Dict[str, Any]]:
        """
        擴展歷史數據獲取 - 支援多天回測數據
        
        Args:
            symbol: 交易對
            interval: 時間間隔
            days_back: 回溯天數
            
        Returns:
            歷史K線數據列表
        """
        try:
            if not self.session:
                raise RuntimeError("Session not initialized. Use async context manager.")
            
            # 計算需要的K線數量
            minutes_per_day = 1440
            interval_minutes = self._interval_to_minutes(interval)
            klines_per_day = minutes_per_day // interval_minutes
            total_limit = min(1000, days_back * klines_per_day)  # Binance限制1000根
            
            logger.info(f"🔄 獲取 {symbol} {interval} 歷史數據: {days_back}天 ({total_limit}根K線)")
            
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': total_limit
            }
            
            async with self.session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    raw_data = await response.json()
                    
                    # 轉換為標準格式 (保持與原有格式一致)
                    formatted_data = []
                    for kline in raw_data:
                        formatted_kline = {
                            'open_time': int(kline[0]),
                            'open': float(kline[1]),
                            'high': float(kline[2]),
                            'low': float(kline[3]),
                            'close': float(kline[4]),
                            'volume': float(kline[5]),
                            'close_time': int(kline[6]),
                            'quote_asset_volume': float(kline[7]),
                            'number_of_trades': int(kline[8]),
                            'taker_buy_base_volume': float(kline[9]),
                            'taker_buy_quote_volume': float(kline[10]),
                            'symbol': symbol,
                            'interval': interval,
                            'timestamp': datetime.fromtimestamp(kline[0] / 1000)
                        }
                        formatted_data.append(formatted_kline)
                    
                    logger.info(f"✅ 成功獲取 {len(formatted_data)} 根 {symbol} K線數據")
                    return formatted_data
                    
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Binance API錯誤: {response.status} - {error_text}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ 獲取歷史數據失敗: {e}")
            return []
    
    async def fetch_multiple_symbols_data(self, 
                                        symbols: List[str], 
                                        interval: str = "1m", 
                                        days_back: int = 30) -> Dict[str, List[Dict[str, Any]]]:
        """
        批量獲取多個交易對的歷史數據
        
        Args:
            symbols: 交易對列表
            interval: 時間間隔
            days_back: 回溯天數
            
        Returns:
            {symbol: 歷史數據} 的字典
        """
        logger.info(f"🔄 批量獲取 {len(symbols)} 個交易對的歷史數據")
        
        results = {}
        
        # 並行獲取數據 (限制並發數避免API限制)
        semaphore = asyncio.Semaphore(5)  # 限制並發數為5
        
        async def fetch_single_symbol(symbol):
            async with semaphore:
                data = await self.fetch_extended_historical_data(symbol, interval, days_back)
                return symbol, data
        
        # 創建任務
        tasks = [fetch_single_symbol(symbol) for symbol in symbols]
        
        # 等待所有任務完成
        completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 處理結果
        for result in completed_tasks:
            if isinstance(result, Exception):
                logger.error(f"❌ 獲取數據時發生錯誤: {result}")
                continue
                
            symbol, data = result
            results[symbol] = data
        
        logger.info(f"✅ 成功獲取 {len(results)} 個交易對的歷史數據")
        return results
    
    def convert_to_dataframe(self, kline_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        轉換K線數據為DataFrame格式 (用於技術分析)
        
        Args:
            kline_data: K線數據列表
            
        Returns:
            pandas DataFrame
        """
        if not kline_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(kline_data)
        
        # 設置時間索引
        df['datetime'] = pd.to_datetime(df['open_time'], unit='ms')
        df.set_index('datetime', inplace=True)
        
        # 確保數值列為float類型
        numeric_columns = ['open', 'high', 'low', 'close', 'volume', 
                          'quote_asset_volume', 'taker_buy_base_volume', 'taker_buy_quote_volume']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 按時間排序
        df.sort_index(inplace=True)
        
        logger.info(f"✅ 轉換為DataFrame: {len(df)} 行數據")
        return df
    
    async def validate_data_quality(self, kline_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        驗證歷史數據品質
        
        Args:
            kline_data: K線數據列表
            
        Returns:
            數據品質報告
        """
        if not kline_data:
            return {"status": "empty", "message": "無數據"}
        
        df = self.convert_to_dataframe(kline_data)
        
        # 數據品質檢查
        quality_report = {
            "total_records": len(df),
            "time_range": {
                "start": df.index.min().isoformat() if len(df) > 0 else None,
                "end": df.index.max().isoformat() if len(df) > 0 else None
            },
            "missing_values": {
                "open": int(df['open'].isna().sum()),
                "high": int(df['high'].isna().sum()), 
                "low": int(df['low'].isna().sum()),
                "close": int(df['close'].isna().sum()),
                "volume": int(df['volume'].isna().sum())
            },
            "data_gaps": [],
            "anomalies": {
                "zero_volume_count": int((df['volume'] == 0).sum()),
                "extreme_price_changes": []
            }
        }
        
        # 檢查時間間隔是否連續
        if len(df) > 1:
            time_diffs = df.index.to_series().diff()
            expected_interval = time_diffs.mode()[0] if len(time_diffs.mode()) > 0 else None
            
            if expected_interval:
                gaps = time_diffs[time_diffs > expected_interval * 1.5]
                quality_report["data_gaps"] = [
                    {
                        "timestamp": gap_time.isoformat(),
                        "duration_minutes": float(gap_duration.total_seconds() / 60)
                    }
                    for gap_time, gap_duration in gaps.items()
                ]
        
        # 檢查極端價格變化
        if len(df) > 1:
            price_changes = df['close'].pct_change()
            extreme_changes = price_changes[abs(price_changes) > 0.1]  # 10%以上變化
            
            quality_report["anomalies"]["extreme_price_changes"] = [
                {
                    "timestamp": change_time.isoformat(),
                    "change_percent": float(change_value * 100)
                }
                for change_time, change_value in extreme_changes.items()
            ]
        
        # 整體品質評分
        issues_count = (
            sum(quality_report["missing_values"].values()) +
            len(quality_report["data_gaps"]) +
            quality_report["anomalies"]["zero_volume_count"] +
            len(quality_report["anomalies"]["extreme_price_changes"])
        )
        
        if issues_count == 0:
            quality_report["quality_score"] = "excellent"
        elif issues_count < 5:
            quality_report["quality_score"] = "good"
        elif issues_count < 20:
            quality_report["quality_score"] = "fair"
        else:
            quality_report["quality_score"] = "poor"
        
        logger.info(f"✅ 數據品質評分: {quality_report['quality_score']}")
        return quality_report


# 測試函數
async def test_historical_data_extension():
    """測試歷史數據擴展功能"""
    logger.info("🧪 開始測試歷史數據擴展功能")
    
    async with HistoricalDataExtension() as data_ext:
        # 測試單一交易對
        test_symbol = "BTCUSDT"
        logger.info(f"📊 測試獲取 {test_symbol} 7天1分鐘數據")
        
        data = await data_ext.fetch_extended_historical_data(
            symbol=test_symbol,
            interval="1m", 
            days_back=7
        )
        
        if data:
            logger.info(f"✅ 獲取到 {len(data)} 根K線")
            
            # 驗證數據品質
            quality_report = await data_ext.validate_data_quality(data)
            # 轉換numpy類型為Python原生類型以便JSON序列化
            quality_report_json = json.loads(json.dumps(quality_report, default=str))
            logger.info(f"📋 數據品質報告: {json.dumps(quality_report_json, indent=2, ensure_ascii=False)}")
            
            # 測試DataFrame轉換
            df = data_ext.convert_to_dataframe(data)
            logger.info(f"📈 DataFrame形狀: {df.shape}")
            logger.info(f"📈 最新價格: {df['close'].iloc[-1]:.2f}")
            
        else:
            logger.error("❌ 未獲取到數據")
    
    logger.info("🎉 歷史數據擴展功能測試完成")


if __name__ == "__main__":
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 運行測試
    asyncio.run(test_historical_data_extension())
