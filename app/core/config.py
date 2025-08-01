from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """應用程式設定"""
    
    # 基本設定
    PROJECT_NAME: str = "Trading X"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 資料庫設定
    DATABASE_URL: str = "sqlite:///./tradingx.db"
    ASYNC_DATABASE_URL: str = "sqlite+aiosqlite:///./tradingx.db"
    
    # Redis 設定
    REDIS_URL: str = "redis://localhost:6379"
    
    # InfluxDB 設定
    INFLUXDB_URL: str = "http://localhost:8086"
    INFLUXDB_TOKEN: str = ""
    INFLUXDB_ORG: str = "tradingx"
    INFLUXDB_BUCKET: str = "market_data"
    
    # API 金鑰
    BINANCE_API_KEY: str = ""
    BINANCE_SECRET_KEY: str = ""
    OKX_API_KEY: str = ""
    OKX_SECRET_KEY: str = ""
    OKX_PASSPHRASE: str = ""
    
    # OpenAI API
    OPENAI_API_KEY: str = ""
    OPENAI_ORG_ID: str = ""
    
    # GitHub Copilot API
    GITHUB_COPILOT_TOKEN: str = ""
    GITHUB_ACCESS_TOKEN: str = ""
    
    # Gmail 通知設定
    GMAIL_SENDER: Optional[str] = None
    GMAIL_APP_PASSWORD: Optional[str] = None  
    GMAIL_RECIPIENT: Optional[str] = None
    
    # 安全設定
    SECRET_KEY: str = "your-secret-key-here"
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # 交易設定
    DEFAULT_RISK_PERCENTAGE: float = 2.0  # 每筆交易風險百分比
    MIN_RISK_REWARD_RATIO: float = 2.0    # 最小風險回報比
    MAX_POSITIONS: int = 5                # 最大同時持倉數
    
    # 技術指標預設參數
    RSI_PERIOD: int = 14
    MACD_FAST: int = 12
    MACD_SLOW: int = 26
    MACD_SIGNAL: int = 9
    BB_PERIOD: int = 20
    BB_STD: float = 2.0
    ATR_PERIOD: int = 14
    
    # 時間框架設定
    TIMEFRAMES: List[str] = ["1m", "5m", "15m", "1h", "4h", "1d"]
    PRIMARY_TIMEFRAME: str = "1h"
    
    # 通知設定
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    LINE_NOTIFY_TOKEN: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # 忽略額外的環境變數

# 創建設定實例
settings = Settings()
