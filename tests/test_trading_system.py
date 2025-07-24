import pytest
import asyncio
from datetime import datetime, timedelta
from app.services.technical_indicators import TechnicalIndicatorsService
from app.services.strategy_engine import StrategyEngine
import pandas as pd
import numpy as np

class TestTechnicalIndicators:
    """技術指標測試"""
    
    def setup_method(self):
        """測試設置"""
        # 創建模擬數據
        dates = pd.date_range(start='2023-01-01', periods=100, freq='H')
        
        # 生成模擬價格數據
        np.random.seed(42)
        prices = []
        price = 100.0
        
        for _ in range(100):
            change = np.random.normal(0, 0.02)  # 2%標準差
            price *= (1 + change)
            prices.append(price)
        
        self.df = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'close': prices,
            'volume': [np.random.randint(1000, 10000) for _ in range(100)],
            'symbol': 'BTC/USDT',
            'timeframe': '1h'
        })
    
    def test_calculate_all_indicators(self):
        """測試計算所有指標"""
        indicators = TechnicalIndicatorsService.calculate_all_indicators(self.df)
        
        # 檢查基本指標是否存在
        expected_indicators = ['EMA', 'MACD', 'RSI', 'BBANDS', 'ATR']
        for indicator in expected_indicators:
            assert indicator in indicators
            assert indicators[indicator].value is not None
            assert indicators[indicator].signal in ['BUY', 'SELL', 'NEUTRAL']
            assert 0 <= indicators[indicator].strength <= 100
    
    def test_rsi_calculation(self):
        """測試RSI計算"""
        indicators = TechnicalIndicatorsService.calculate_momentum_indicators(self.df)
        rsi = indicators['RSI']
        
        assert 0 <= rsi.value <= 100
        
        # 測試超買超賣信號
        if rsi.value > 70:
            assert rsi.signal == 'SELL'
        elif rsi.value < 30:
            assert rsi.signal == 'BUY'
        else:
            assert rsi.signal == 'NEUTRAL'
    
    def test_macd_calculation(self):
        """測試MACD計算"""
        indicators = TechnicalIndicatorsService.calculate_trend_indicators(self.df)
        macd = indicators['MACD']
        
        assert 'macd' in macd.metadata
        assert 'signal' in macd.metadata
        assert 'histogram' in macd.metadata
    
    def test_bollinger_bands(self):
        """測試布林通道"""
        indicators = TechnicalIndicatorsService.calculate_volatility_indicators(self.df)
        bb = indicators['BBANDS']
        
        assert 'upper' in bb.metadata
        assert 'middle' in bb.metadata
        assert 'lower' in bb.metadata
        assert 'position' in bb.metadata
        
        # 檢查通道關係
        assert bb.metadata['upper'] > bb.metadata['middle'] > bb.metadata['lower']

class TestStrategyEngine:
    """策略引擎測試"""
    
    def setup_method(self):
        """測試設置"""
        self.strategy_engine = StrategyEngine()
    
    @pytest.mark.asyncio
    async def test_signal_generation(self):
        """測試信號生成"""
        # 創建測試數據
        dates = pd.date_range(start='2023-01-01', periods=100, freq='H')
        prices = [100 + i * 0.5 for i in range(100)]  # 上升趨勢
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': [p * 1.02 for p in prices],
            'low': [p * 0.98 for p in prices],
            'close': prices,
            'volume': [1000] * 100,
            'symbol': 'BTC/USDT',
            'timeframe': '1h'
        })
        
        indicators = TechnicalIndicatorsService.calculate_all_indicators(df)
        signal = await self.strategy_engine.generate_signal(
            df, indicators, 'BTC/USDT', '1h'
        )
        
        # 在上升趨勢中應該生成做多信號或無信號
        if signal:
            assert signal.symbol == 'BTC/USDT'
            assert signal.timeframe == '1h'
            assert signal.entry_price > 0
            assert signal.stop_loss > 0
            assert signal.take_profit > 0
            assert 0 <= signal.confidence <= 1

class TestMarketData:
    """市場數據測試"""
    
    def test_data_validation(self):
        """測試數據驗證"""
        # 測試有效數據
        valid_df = pd.DataFrame({
            'timestamp': pd.date_range(start='2023-01-01', periods=10, freq='H'),
            'open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            'high': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
            'low': [99, 100, 101, 102, 103, 104, 105, 106, 107, 108],
            'close': [100.5, 101.5, 102.5, 103.5, 104.5, 105.5, 106.5, 107.5, 108.5, 109.5],
            'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900],
            'symbol': 'BTC/USDT',
            'timeframe': '1h'
        })
        
        # 檢查數據完整性
        assert len(valid_df) == 10
        assert all(valid_df['high'] >= valid_df['low'])
        assert all(valid_df['high'] >= valid_df['open'])
        assert all(valid_df['high'] >= valid_df['close'])
        assert all(valid_df['low'] <= valid_df['open'])
        assert all(valid_df['low'] <= valid_df['close'])

def test_risk_reward_calculation():
    """測試風險回報比計算"""
    entry_price = 100
    stop_loss = 98
    take_profit = 106
    
    risk = entry_price - stop_loss  # 2
    reward = take_profit - entry_price  # 6
    risk_reward_ratio = reward / risk  # 3:1
    
    assert risk_reward_ratio == 3.0
    assert risk > 0
    assert reward > 0

def test_position_sizing():
    """測試倉位大小計算"""
    account_balance = 10000
    risk_percentage = 2.0  # 2%
    entry_price = 100
    stop_loss = 98
    
    risk_amount = account_balance * (risk_percentage / 100)  # $200
    risk_per_unit = entry_price - stop_loss  # $2
    position_size = risk_amount / risk_per_unit  # 100 units
    
    assert risk_amount == 200
    assert risk_per_unit == 2
    assert position_size == 100

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
