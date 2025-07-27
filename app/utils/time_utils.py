"""
統一時間處理工具模組
確保全系統使用台灣時區 (UTC+8)
"""

import pytz
from datetime import datetime, timedelta
from typing import Optional, Union

# 台灣時區定義
TAIWAN_TZ = pytz.timezone('Asia/Taipei')
UTC_TZ = pytz.UTC

def get_taiwan_now() -> datetime:
    """獲取當前台灣時間（帶時區信息）"""
    return datetime.now(TAIWAN_TZ)

def get_taiwan_now_naive() -> datetime:
    """獲取當前台灣時間（無時區信息）"""
    return get_taiwan_now().replace(tzinfo=None)

def utc_to_taiwan(utc_dt: datetime) -> datetime:
    """將UTC時間轉換為台灣時間"""
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=UTC_TZ)
    return utc_dt.astimezone(TAIWAN_TZ)

def taiwan_to_utc(taiwan_dt: datetime) -> datetime:
    """將台灣時間轉換為UTC時間"""
    if taiwan_dt.tzinfo is None:
        taiwan_dt = TAIWAN_TZ.localize(taiwan_dt)
    return taiwan_dt.astimezone(UTC_TZ)

def to_taiwan_naive(dt: Union[datetime, str]) -> datetime:
    """將任何時間轉換為台灣時間的naive datetime"""
    if isinstance(dt, str):
        # 解析字符串時間
        try:
            if 'Z' in dt or '+' in dt or '-' in dt.split('T')[-1]:
                # 包含時區信息
                dt_clean = dt.replace('Z', '+00:00')
                parsed_dt = datetime.fromisoformat(dt_clean)
                taiwan_dt = parsed_dt.astimezone(TAIWAN_TZ)
                return taiwan_dt.replace(tzinfo=None)
            else:
                # 無時區信息，假設為本地時間
                return datetime.fromisoformat(dt)
        except:
            # 解析失敗，返回當前台灣時間
            return get_taiwan_now_naive()
    
    elif isinstance(dt, datetime):
        if dt.tzinfo is None:
            # 無時區信息，假設為台灣時間
            return dt
        else:
            # 有時區信息，轉換為台灣時間
            taiwan_dt = dt.astimezone(TAIWAN_TZ)
            return taiwan_dt.replace(tzinfo=None)
    
    return get_taiwan_now_naive()

def taiwan_now_plus(hours: int = 0, minutes: int = 0, days: int = 0) -> datetime:
    """獲取台灣時間加上指定時間間隔（無時區信息）"""
    base_time = get_taiwan_now_naive()
    return base_time + timedelta(hours=hours, minutes=minutes, days=days)

def taiwan_now_minus(hours: int = 0, minutes: int = 0, days: int = 0) -> datetime:
    """獲取台灣時間減去指定時間間隔（無時區信息）"""
    base_time = get_taiwan_now_naive()
    return base_time - timedelta(hours=hours, minutes=minutes, days=days)

def format_taiwan_time(dt: datetime, format_str: str = "%Y/%m/%d %H:%M:%S") -> str:
    """格式化台灣時間為字符串"""
    taiwan_dt = to_taiwan_naive(dt)
    return taiwan_dt.strftime(format_str)

def is_expired(expires_at: Union[datetime, str], base_time: Optional[datetime] = None) -> bool:
    """檢查是否已過期（使用台灣時間）"""
    if base_time is None:
        base_time = get_taiwan_now_naive()
    
    expires_taiwan = to_taiwan_naive(expires_at)
    base_taiwan = to_taiwan_naive(base_time)
    
    return base_taiwan > expires_taiwan

def time_until_expiry(expires_at: Union[datetime, str], base_time: Optional[datetime] = None) -> timedelta:
    """計算距離過期的時間差（使用台灣時間）"""
    if base_time is None:
        base_time = get_taiwan_now_naive()
    
    expires_taiwan = to_taiwan_naive(expires_at)
    base_taiwan = to_taiwan_naive(base_time)
    
    return expires_taiwan - base_taiwan

# 向後兼容的函數別名
now = get_taiwan_now_naive
utcnow = get_taiwan_now_naive  # 重定向到台灣時間
