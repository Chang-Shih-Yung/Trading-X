"""
增強數據存儲服務
提供自動數據入庫、數據驗證、重複檢查等功能
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, desc, select
import logging
from dataclasses import dataclass

from app.core.database import AsyncSessionLocal
from app.models.models import MarketData
from app.utils.time_utils import get_taiwan_now_naive

logger = logging.getLogger(__name__)

@dataclass
class DataValidationResult:
    """數據驗證結果"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    cleaned_data: Optional[pd.DataFrame] = None

@dataclass
class StorageStats:
    """存儲統計信息"""
    total_records: int
    new_records: int
    duplicate_records: int
    invalid_records: int
    storage_time: float

class EnhancedDataStorage:
    """增強數據存儲服務"""
    
    def __init__(self):
        self.batch_size = 1000  # 批量處理大小
        self.validation_enabled = True
        self.auto_cleanup = True
        self.max_retention_days = 365  # 數據保留天數
        self.duplicate_check_window = timedelta(minutes=5)  # 重複檢查窗口
        
    async def store_market_data_batch(
        self, 
        data_batch: List[Dict], 
        validate: bool = True
    ) -> StorageStats:
        """批量存儲市場數據"""
        start_time = datetime.now()
        
        try:
            # 轉換為 DataFrame
            df = pd.DataFrame(data_batch)
            
            if df.empty:
                return StorageStats(0, 0, 0, 0, 0)
            
            # 數據驗證
            if validate and self.validation_enabled:
                validation_result = await self._validate_market_data(df)
                if not validation_result.is_valid:
                    logger.error(f"數據驗證失敗: {validation_result.errors}")
                    return StorageStats(
                        len(df), 0, 0, len(df), 
                        (datetime.now() - start_time).total_seconds()
                    )
                df = validation_result.cleaned_data or df
            
            # 去重處理
            deduplicated_df = await self._remove_duplicates(df)
            
            # 存儲到數據庫
            new_records = await self._bulk_insert_market_data(deduplicated_df)
            
            # 自動清理舊數據
            if self.auto_cleanup:
                asyncio.create_task(self._cleanup_old_data())
            
            storage_time = (datetime.now() - start_time).total_seconds()
            
            return StorageStats(
                total_records=len(df),
                new_records=new_records,
                duplicate_records=len(df) - len(deduplicated_df),
                invalid_records=0,
                storage_time=storage_time
            )
            
        except Exception as e:
            logger.error(f"批量存儲數據失敗: {e}")
            return StorageStats(0, 0, 0, 0, 0)
    
    async def _validate_market_data(self, df: pd.DataFrame) -> DataValidationResult:
        """驗證市場數據"""
        errors = []
        warnings = []
        cleaned_df = df.copy()
        
        # 必要字段檢查
        required_fields = ['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume']
        missing_fields = [field for field in required_fields if field not in df.columns]
        
        if missing_fields:
            errors.append(f"缺少必要字段: {missing_fields}")
            return DataValidationResult(False, errors, warnings)
        
        # 數據類型檢查
        numeric_fields = ['open', 'high', 'low', 'close', 'volume']
        for field in numeric_fields:
            if field in df.columns:
                # 嘗試轉換為數值類型
                try:
                    cleaned_df[field] = pd.to_numeric(cleaned_df[field], errors='coerce')
                    # 檢查 NaN 值
                    nan_count = cleaned_df[field].isna().sum()
                    if nan_count > 0:
                        warnings.append(f"{field} 字段有 {nan_count} 個無效值")
                        # 移除包含 NaN 的行
                        cleaned_df = cleaned_df.dropna(subset=[field])
                except Exception as e:
                    errors.append(f"{field} 字段類型轉換失敗: {e}")
        
        # 時間戳檢查
        try:
            if 'timestamp' in df.columns:
                cleaned_df['timestamp'] = pd.to_datetime(cleaned_df['timestamp'])
                # 檢查未來時間
                future_count = (cleaned_df['timestamp'] > datetime.now()).sum()
                if future_count > 0:
                    warnings.append(f"發現 {future_count} 個未來時間戳")
        except Exception as e:
            errors.append(f"時間戳處理失敗: {e}")
        
        # 價格邏輯檢查
        try:
            # 檢查 OHLC 邏輯: low <= open,close <= high
            invalid_ohlc = (
                (cleaned_df['low'] > cleaned_df['open']) | 
                (cleaned_df['low'] > cleaned_df['close']) |
                (cleaned_df['high'] < cleaned_df['open']) |
                (cleaned_df['high'] < cleaned_df['close'])
            ).sum()
            
            if invalid_ohlc > 0:
                warnings.append(f"發現 {invalid_ohlc} 個 OHLC 邏輯錯誤")
                # 移除邏輯錯誤的行
                valid_ohlc_mask = (
                    (cleaned_df['low'] <= cleaned_df['open']) & 
                    (cleaned_df['low'] <= cleaned_df['close']) &
                    (cleaned_df['high'] >= cleaned_df['open']) &
                    (cleaned_df['high'] >= cleaned_df['close'])
                )
                cleaned_df = cleaned_df[valid_ohlc_mask]
        
        except Exception as e:
            warnings.append(f"OHLC 邏輯檢查失敗: {e}")
        
        # 價格範圍檢查
        try:
            for field in ['open', 'high', 'low', 'close']:
                if field in cleaned_df.columns:
                    # 檢查負價格
                    negative_count = (cleaned_df[field] <= 0).sum()
                    if negative_count > 0:
                        warnings.append(f"{field} 有 {negative_count} 個非正值")
                        cleaned_df = cleaned_df[cleaned_df[field] > 0]
                    
                    # 檢查異常高價格 (可能是數據錯誤)
                    median_price = cleaned_df[field].median()
                    if median_price > 0:
                        extreme_high = (cleaned_df[field] > median_price * 100).sum()
                        if extreme_high > 0:
                            warnings.append(f"{field} 有 {extreme_high} 個異常高價格")
        
        except Exception as e:
            warnings.append(f"價格範圍檢查失敗: {e}")
        
        # 成交量檢查
        try:
            if 'volume' in cleaned_df.columns:
                negative_volume = (cleaned_df['volume'] < 0).sum()
                if negative_volume > 0:
                    warnings.append(f"發現 {negative_volume} 個負成交量")
                    cleaned_df = cleaned_df[cleaned_df['volume'] >= 0]
        
        except Exception as e:
            warnings.append(f"成交量檢查失敗: {e}")
        
        is_valid = len(errors) == 0
        
        return DataValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            cleaned_data=cleaned_df if is_valid else None
        )
    
    async def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """移除重複數據"""
        try:
            # 基於 symbol, timestamp, timeframe 去重
            key_columns = ['symbol', 'timestamp']
            if 'timeframe' in df.columns:
                key_columns.append('timeframe')
            
            # 內部去重
            df_deduplicated = df.drop_duplicates(subset=key_columns, keep='last')
            
            # 與數據庫中的數據對比去重
            if len(df_deduplicated) > 0:
                df_deduplicated = await self._check_database_duplicates(df_deduplicated)
            
            logger.info(f"去重處理: {len(df)} -> {len(df_deduplicated)} 記錄")
            return df_deduplicated
            
        except Exception as e:
            logger.error(f"去重處理失敗: {e}")
            return df
    
    async def _check_database_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """檢查數據庫中的重複數據"""
        try:
            async with AsyncSessionLocal() as session:
                unique_records = []
                
                for _, row in df.iterrows():
                    # 檢查窗口內是否存在相同記錄
                    start_time = row['timestamp'] - self.duplicate_check_window
                    end_time = row['timestamp'] + self.duplicate_check_window
                    
                    stmt = select(MarketData).where(
                        and_(
                            MarketData.symbol == row['symbol'],
                            MarketData.timestamp >= start_time,
                            MarketData.timestamp <= end_time
                        )
                    )
                    
                    if 'timeframe' in row:
                        stmt = stmt.where(MarketData.timeframe == row['timeframe'])
                    
                    result = await session.execute(stmt)
                    existing = result.first()
                    
                    if not existing:
                        unique_records.append(row)
                
                return pd.DataFrame(unique_records) if unique_records else pd.DataFrame()
                
        except Exception as e:
            logger.error(f"數據庫重複檢查失敗: {e}")
            return df
    
    async def _bulk_insert_market_data(self, df: pd.DataFrame) -> int:
        """批量插入市場數據"""
        if df.empty:
            return 0
            
        try:
            async with AsyncSessionLocal() as session:
                market_data_objects = []
                
                for _, row in df.iterrows():
                    market_data = MarketData(
                        symbol=row['symbol'],
                        timeframe=row.get('timeframe', '1m'),
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
                
                logger.info(f"成功存儲 {len(market_data_objects)} 筆市場數據")
                return len(market_data_objects)
                
        except Exception as e:
            logger.error(f"批量插入數據失敗: {e}")
            return 0
    
    async def _cleanup_old_data(self):
        """清理舊數據"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.max_retention_days)
            
            async with AsyncSessionLocal() as session:
                # 刪除舊數據
                stmt = select(MarketData).where(MarketData.timestamp < cutoff_date)
                result = await session.execute(stmt)
                old_records = result.scalars().all()
                
                if old_records:
                    for record in old_records:
                        await session.delete(record)
                    
                    await session.commit()
                    logger.info(f"清理了 {len(old_records)} 筆舊數據 (超過 {self.max_retention_days} 天)")
                    
        except Exception as e:
            logger.error(f"清理舊數據失敗: {e}")
    
    async def get_storage_statistics(self) -> Dict[str, Any]:
        """獲取存儲統計信息"""
        try:
            async with AsyncSessionLocal() as session:
                # 總記錄數
                total_stmt = select(MarketData)
                total_result = await session.execute(total_stmt)
                total_count = len(total_result.scalars().all())
                
                # 今日新增記錄
                today = datetime.now().date()
                today_stmt = select(MarketData).where(
                    MarketData.timestamp >= today
                )
                today_result = await session.execute(today_stmt)
                today_count = len(today_result.scalars().all())
                
                # 最新記錄時間
                latest_stmt = select(MarketData).order_by(desc(MarketData.timestamp)).limit(1)
                latest_result = await session.execute(latest_stmt)
                latest_record = latest_result.scalar_one_or_none()
                
                # 統計不同交易對
                symbols_stmt = select(MarketData.symbol).distinct()
                symbols_result = await session.execute(symbols_stmt)
                unique_symbols = len(symbols_result.scalars().all())
                
                return {
                    "total_records": total_count,
                    "today_new_records": today_count,
                    "unique_symbols": unique_symbols,
                    "latest_timestamp": latest_record.timestamp.isoformat() if latest_record else None,
                    "retention_days": self.max_retention_days,
                    "validation_enabled": self.validation_enabled,
                    "auto_cleanup": self.auto_cleanup
                }
                
        except Exception as e:
            logger.error(f"獲取存儲統計失敗: {e}")
            return {"error": str(e)}
