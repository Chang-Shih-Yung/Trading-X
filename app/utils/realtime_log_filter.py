"""
日誌過濾器 - 只保留核心 pandas+websocket 流程日誌
"""

import logging
import re
from typing import Set

class RealtimeStrategyLogFilter(logging.Filter):
    """實時交易策略日誌過濾器"""
    
    def __init__(self):
        super().__init__()
        
        # 允許的模組
        self.allowed_modules = {
            'app.services.realtime_signal_engine',
            'app.services.market_data',
            'app.services.binance_websocket',
            'app.services.pandas_ta_indicators',
            'app.services.pandas_ta_trading_signal_parser',
            'app.services.precision_signal_filter',  # 智能共振濾波器
            'app.api.v1.endpoints.realtime_market'
        }
        
        # 關鍵詞過濾 - 只顯示核心流程
        self.core_keywords = {
            '實時信號引擎',
            'pandas-ta',
            'WebSocket',
            '信號生成',
            '智能共振',
            '精準篩選',
            '技術指標',
            '交易信號',
            '市場數據',
            'K線數據',
            '即時數據',
            '價格監控',
            'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT', 'XRPUSDT', 'DOGEUSDT'
        }
        
        # 忽略的錯誤類型
        self.ignored_errors = {
            'SQLite',
            'database',
            'session',
            'cleanup',
            'log_management'
        }
    
    def filter(self, record):
        """過濾日誌記錄"""
        
        # 檢查模組名稱
        if hasattr(record, 'name'):
            module_name = record.name
            
            # 只允許特定模組的日誌
            if not any(allowed in module_name for allowed in self.allowed_modules):
                return False
        
        # 檢查日誌消息內容
        message = record.getMessage()
        
        # 忽略特定錯誤
        if any(ignored in message for ignored in self.ignored_errors):
            return False
        
        # 只保留包含核心關鍵詞的日誌
        if record.levelno >= logging.WARNING:  # WARNING 和 ERROR 總是顯示
            return True
        
        # INFO 級別需要包含核心關鍵詞
        if any(keyword in message for keyword in self.core_keywords):
            return True
        
        return False

def setup_realtime_logging():
    """設置實時交易策略日誌"""
    
    # 獲取根日誌記录器
    root_logger = logging.getLogger()
    
    # 移除現有的處理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 創建新的處理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 設置格式
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # 添加過濾器
    realtime_filter = RealtimeStrategyLogFilter()
    console_handler.addFilter(realtime_filter)
    
    # 添加處理器
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.INFO)
    
    print("✅ 實時交易策略日誌過濾器已啟用 - 只顯示 pandas+WebSocket 核心流程")

def disable_noisy_loggers():
    """禁用吵雜的日誌記錄器"""
    noisy_loggers = [
        'sqlalchemy',
        'sqlite3',
        'asyncio',
        'websockets',
        'httpx',
        'urllib3',
        'requests'
    ]
    
    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.ERROR)
