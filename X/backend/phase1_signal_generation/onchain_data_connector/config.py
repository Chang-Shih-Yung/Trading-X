"""
🎯 產品級鏈上價格抓取系統 - 配置模塊
Production-Grade Onchain Price Fetcher Configuration
"""

from typing import Dict, List, Tuple

class ProductionConfig:
    """產品級配置"""
    
    # 🔗 固定合約地址
    USDT_ADDRESS = "0x55d398326f99059fF775485246999027B3197955"
    
    # 🏭 PancakeSwap Factory 合約
    PANCAKE_V2_FACTORY = "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73"
    PANCAKE_V3_FACTORY = "0x1097053Fd2ea711dad45caCcc45EfF7548fCB362"
    
    # 🪙 七大幣種代幣地址 (固定)
    TOKEN_ADDRESSES = {
        'BTCB': '0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c',    # Bitcoin BEP20
        'ETH': '0x2170Ed0880ac9A755fd29B2688956BD959F933F8',     # Ethereum Token
        'WBNB': '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',   # Wrapped BNB
        'ADA': '0x3EE2200Efb3400fAbB9AacF31297cBdD1d435D47',     # Cardano Token
        'DOGE': '0xbA2aE424d960c26247Dd6c32edC70B295c744C43',    # Dogecoin Token
        'XRP': '0x1D2F0da169ceB9fC7B3144628dB156f3F6c60dBE',     # XRP Token
        'SOL': '0x570A5D26f7765Ecb712C0924E4De545B89fD43dF'      # Solana Token
    }
    
    # 🔢 代幣小數位數配置 (關鍵：DOGE 是 8 位，其他大多是 18 位)
    TOKEN_DECIMALS = {
        'BTCB': 18,    # Bitcoin BEP20 是 18 位
        'ETH': 18,     # Ethereum Token 是 18 位
        'WBNB': 18,    # Wrapped BNB 是 18 位
        'ADA': 18,     # Cardano Token 是 18 位
        'DOGE': 8,     # ⚠️ Dogecoin Token 是 8 位小數！
        'XRP': 18,     # XRP Token 是 18 位
        'SOL': 18,     # Solana Token 是 18 位
        'USDT': 18     # USDT 是 18 位
    }
    
    # 📊 V3 Fee Tiers (從高流動性到低流動性順序)
    V3_FEE_TIERS = [500, 3000, 10000, 100]  # 0.05%, 0.3%, 1%, 0.01%
    
    # 💰 動態流動性評估配置
    MIN_LIQUIDITY_THRESHOLD = 1000  # 最低1000 USDT即可接受
    PREFERRED_LIQUIDITY_THRESHOLD = 50000  # 優先選擇5萬USDT以上
    
    # 🌐 產品級 BSC RPC 節點池 (按優先級排序)
    BSC_RPC_NODES = [
        "https://bsc-dataseed.binance.org",
        "https://bsc-dataseed1.binance.org", 
        "https://bsc-dataseed2.binance.org",
        "https://bsc.publicnode.com",
        "https://rpc.ankr.com/bsc",
        "https://bsc-rpc.publicnode.com",
        "https://bsc.nodereal.io",
        "https://bsc-dataseed3.binance.org"
    ]
    
    # ⏱️ 時間配置
    PRICE_UPDATE_INTERVAL = 500  # 500ms 更新間隔
    POOL_DISCOVERY_INTERVAL = 3600  # 1小時重新發現主池
    RPC_TIMEOUT = 10  # RPC 請求超時
    
    # 🔄 重試配置
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    
    # 📈 動態價格異常檢測配置
    PRICE_VOLATILITY_THRESHOLD = 0.5  # 50% 變動視為異常
    PRICE_CACHE_DURATION = 300  # 5分鐘價格快取用於異常檢測
    
    # 🎯 Phase1 Schema 兼容性
    SUPPORTED_SYMBOLS = ['BTC', 'ETH', 'BNB', 'ADA', 'DOGE', 'XRP', 'SOL']
    
    @classmethod
    def get_token_address(cls, symbol: str) -> str:
        """獲取代幣地址"""
        if symbol == 'BTC':
            return cls.TOKEN_ADDRESSES['BTCB']
        elif symbol == 'BNB':
            return cls.TOKEN_ADDRESSES['WBNB']
        else:
            return cls.TOKEN_ADDRESSES.get(symbol)
    
    @classmethod
    def get_token_decimals(cls, symbol: str) -> int:
        """獲取代幣小數位數"""
        if symbol == 'BTC':
            return cls.TOKEN_DECIMALS['BTCB']
        elif symbol == 'BNB':
            return cls.TOKEN_DECIMALS['WBNB']
        else:
            return cls.TOKEN_DECIMALS.get(symbol, 18)  # 默認 18 位
    
    @classmethod
    def get_usdt_decimals(cls) -> int:
        """獲取 USDT 小數位數"""
        return cls.TOKEN_DECIMALS['USDT']
    
    @classmethod
    def is_liquidity_acceptable(cls, liquidity_usdt: float, symbol: str = None) -> bool:
        """動態判斷流動性是否可接受"""
        # 基本門檻：至少1000 USDT
        if liquidity_usdt < cls.MIN_LIQUIDITY_THRESHOLD:
            return False
        
        # 對於主流幣種，可接受較低流動性
        mainstream_coins = ['BTCB', 'ETH', 'WBNB']
        if symbol in mainstream_coins:
            return liquidity_usdt >= cls.MIN_LIQUIDITY_THRESHOLD
        
        # 其他幣種需要更高流動性
        return liquidity_usdt >= cls.MIN_LIQUIDITY_THRESHOLD * 5  # 5000 USDT
    
    @classmethod
    def get_liquidity_score(cls, liquidity_usdt: float) -> float:
        """計算流動性評分 (0-1)"""
        if liquidity_usdt <= cls.MIN_LIQUIDITY_THRESHOLD:
            return 0.0
        elif liquidity_usdt >= cls.PREFERRED_LIQUIDITY_THRESHOLD:
            return 1.0
        else:
            # 線性插值
            ratio = (liquidity_usdt - cls.MIN_LIQUIDITY_THRESHOLD) / (cls.PREFERRED_LIQUIDITY_THRESHOLD - cls.MIN_LIQUIDITY_THRESHOLD)
            return min(1.0, max(0.0, ratio))
    
    @classmethod
    def get_symbol_pairs(cls) -> List[str]:
        """獲取所有交易對"""
        return [f"{symbol}USDT" for symbol in cls.SUPPORTED_SYMBOLS]
