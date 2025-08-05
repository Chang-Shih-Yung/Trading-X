"""
Trading-X 系統配置檔案
====================

配置整個 Trading-X 系統的路徑、參數和設定
"""

import os
from pathlib import Path

# === 系統路徑配置 ===
PROJECT_ROOT = Path(__file__).parent
STRATEGIES_PATH = PROJECT_ROOT / "strategies"
CORE_PATH = PROJECT_ROOT / "core"
INDICATORS_PATH = PROJECT_ROOT / "indicators"
MONITORING_PATH = PROJECT_ROOT / "monitoring"
UTILS_PATH = PROJECT_ROOT / "utils"
FRONTEND_PATH = PROJECT_ROOT / "frontend"

# === API 配置 ===
BINANCE_API_BASE = "https://api.binance.com"
BINANCE_FUTURES_API_BASE = "https://fapi.binance.com"

# === 交易配置 ===
DEFAULT_SYMBOLS = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "SOLUSDT"]
DEFAULT_INTERVALS = ["1m", "5m", "15m", "1h", "4h", "1d"]

# === 監控配置 ===
MONITORING_PORT = 8001
MONITORING_HOST = "0.0.0.0"
LOG_LEVEL = "INFO"

# === 信號配置 ===
SIGNAL_QUALITY_THRESHOLD = 0.7
EXTREME_SIGNAL_THRESHOLD = 0.8
MAX_SIGNALS_PER_HOUR = 10

# === 通知配置 ===
GMAIL_ENABLED = True
TELEGRAM_ENABLED = False  # 未來擴展

# === 安全配置 ===
API_RATE_LIMIT = 100  # 每分鐘請求數
MAX_CONCURRENT_REQUESTS = 10

# === 系統元數據 ===
SYSTEM_VERSION = "1.0.0"
SYSTEM_NAME = "Trading-X"
LAST_UPDATED = "2024-12-28"
