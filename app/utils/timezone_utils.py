"""
時區處理工具
專門處理UTC和台灣時間(CST/UTC+8)的轉換
"""
from datetime import datetime, timezone, timedelta
from typing import Optional

# 台灣時區 (UTC+8)
TAIWAN_TZ = timezone(timedelta(hours=8))

def get_taiwan_now() -> datetime:
    """獲取當前台灣時間 (UTC+8)"""
    return datetime.now(TAIWAN_TZ)

def get_utc_now() -> datetime:
    """獲取當前UTC時間"""
    return datetime.now(timezone.utc)

def taiwan_to_utc(taiwan_dt: datetime) -> datetime:
    """將台灣時間轉換為UTC時間"""
    if taiwan_dt.tzinfo is None:
        # 如果沒有時區信息，假設是台灣時間
        taiwan_dt = taiwan_dt.replace(tzinfo=TAIWAN_TZ)
    return taiwan_dt.astimezone(timezone.utc)

def utc_to_taiwan(utc_dt: datetime) -> datetime:
    """將UTC時間轉換為台灣時間"""
    if utc_dt.tzinfo is None:
        # 如果沒有時區信息，假設是UTC時間
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    return utc_dt.astimezone(TAIWAN_TZ)

def ensure_taiwan_timezone(dt: datetime) -> datetime:
    """確保datetime對象有台灣時區信息"""
    if dt.tzinfo is None:
        # 如果沒有時區信息，假設是UTC時間，然後轉換為台灣時間
        utc_dt = dt.replace(tzinfo=timezone.utc)
        return utc_dt.astimezone(TAIWAN_TZ)
    return dt.astimezone(TAIWAN_TZ)

def ensure_utc_timezone(dt: datetime) -> datetime:
    """確保datetime對象有UTC時區信息"""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def format_taiwan_time(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化台灣時間為字符串"""
    taiwan_dt = ensure_taiwan_timezone(dt)
    return taiwan_dt.strftime(format_str)

def parse_iso_to_taiwan(iso_string: str) -> datetime:
    """解析ISO格式字符串並轉換為台灣時間"""
    dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    return ensure_taiwan_timezone(dt)

# 常用的時間增量
MINUTES_15 = timedelta(minutes=15)
MINUTES_30 = timedelta(minutes=30)
HOURS_1 = timedelta(hours=1)
HOURS_2 = timedelta(hours=2)
HOURS_24 = timedelta(hours=24)
DAYS_7 = timedelta(days=7)
