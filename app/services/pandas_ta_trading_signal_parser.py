"""
Pandas-TA 交易信號解析器
基於 pandas_ta_trading_signals.json 配置文件的交易信號生成與解析
"""

import json
import pandas as pd
import pandas_ta as ta
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    NEUTRAL = "NEUTRAL"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"

@dataclass
class TradingSignal:
    indicator: str
    signal_type: SignalType
    strength: float  # 0.0 - 1.0
    value: float
    condition_met: str
    timeframe: str
    timestamp: pd.Timestamp
    confidence: float = 0.0

class PandasTATradingSignals:
    """
    基於 pandas-ta 的交易信號生成器
    """
    
    def __init__(self, config_path: str = None):
        """
        初始化交易信號生成器
        
        Args:
            config_path: JSON 配置文件路徑
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "pandas_ta_trading_signals.json"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.signals_cache = {}
        
    def calculate_all_indicators(self, df: pd.DataFrame, strategy: str = "swing") -> pd.DataFrame:
        """
        計算所有支援的技術指標
        
        Args:
            df: OHLCV 數據框
            strategy: 策略類型 (scalping, swing, trend)
            
        Returns:
            包含所有指標的數據框
        """
        result_df = df.copy()
        
        # 趨勢指標
        result_df = self._calculate_trend_indicators(result_df, strategy)
        
        # 動量指標
        result_df = self._calculate_momentum_indicators(result_df, strategy)
        
        # 波動性指標
        result_df = self._calculate_volatility_indicators(result_df, strategy)
        
        # 成交量指標 (如果有 volume 數據)
        if 'volume' in df.columns:
            result_df = self._calculate_volume_indicators(result_df, strategy)
            
        # K線形態
        result_df = self._calculate_candlestick_patterns(result_df)
        
        return result_df
    
    def _calculate_trend_indicators(self, df: pd.DataFrame, strategy: str) -> pd.DataFrame:
        """計算趨勢指標"""
        trend_config = self.config["trend_indicators"]
        
        # EMA
        ema_params = trend_config["ema"]["parameters"]
        length = ema_params.get(strategy, ema_params["swing"])
        df[f'ema_{length}'] = ta.ema(df['close'], length=length)
        df[f'ema_{length}_slope'] = df[f'ema_{length}'].diff(3)
        
        # MACD
        macd_params = trend_config["macd"]["parameters"]
        if strategy in macd_params:
            params = macd_params[strategy]
        else:
            params = macd_params["swing"]
        
        macd_result = ta.macd(df['close'], 
                             fast=params["fast"], 
                             slow=params["slow"], 
                             signal=params["signal"])
        df = pd.concat([df, macd_result], axis=1)
        
        # ADX
        adx_length = trend_config["adx"]["parameters"]["length"][0]
        adx_result = ta.adx(df['high'], df['low'], df['close'], length=adx_length)
        df = pd.concat([df, adx_result], axis=1)
        
        # Aroon
        aroon_length = trend_config["aroon"]["parameters"]["length"][0]
        aroon_result = ta.aroon(df['high'], df['low'], length=aroon_length)
        df = pd.concat([df, aroon_result], axis=1)
        
        # SuperTrend
        st_params = trend_config["supertrend"]["parameters"]
        if strategy in st_params:
            st_config = st_params[strategy]
        else:
            st_config = st_params["swing"]
            
        supertrend_result = ta.supertrend(df['high'], df['low'], df['close'],
                                        length=st_config["length"],
                                        multiplier=st_config["multiplier"])
        df = pd.concat([df, supertrend_result], axis=1)
        
        # PSAR
        psar_result = ta.psar(df['high'], df['low'], df['close'])
        df = pd.concat([df, psar_result], axis=1)
        
        return df
    
    def _calculate_momentum_indicators(self, df: pd.DataFrame, strategy: str) -> pd.DataFrame:
        """計算動量指標"""
        momentum_config = self.config["momentum_indicators"]
        
        # RSI
        rsi_params = momentum_config["rsi"]["parameters"]
        if strategy in rsi_params:
            length = rsi_params[strategy]["length"]
        else:
            length = rsi_params["length"][0]
        df[f'rsi_{length}'] = ta.rsi(df['close'], length=length)
        
        # Stochastic
        stoch_params = momentum_config["stoch"]["parameters"]
        if strategy in stoch_params:
            k = stoch_params[strategy]["k"]
            d = stoch_params[strategy]["d"]
        else:
            k = stoch_params["k"][0]
            d = stoch_params["d"][0]
        stoch_result = ta.stoch(df['high'], df['low'], df['close'], k=k, d=d)
        df = pd.concat([df, stoch_result], axis=1)
        
        # Williams %R
        willr_length = momentum_config["willr"]["parameters"]["length"][0]
        df[f'willr_{willr_length}'] = ta.willr(df['high'], df['low'], df['close'], length=willr_length)
        
        # CCI
        cci_length = momentum_config["cci"]["parameters"]["length"][0]
        df[f'cci_{cci_length}'] = ta.cci(df['high'], df['low'], df['close'], length=cci_length)
        
        # ROC
        roc_length = momentum_config["roc"]["parameters"]["length"][0]
        df[f'roc_{roc_length}'] = ta.roc(df['close'], length=roc_length)
        
        return df
    
    def _calculate_volatility_indicators(self, df: pd.DataFrame, strategy: str) -> pd.DataFrame:
        """計算波動性指標"""
        volatility_config = self.config["volatility_indicators"]
        
        # Bollinger Bands
        bb_params = volatility_config["bbands"]["parameters"]
        if strategy in bb_params:
            length = bb_params[strategy]["length"]
            std = bb_params[strategy]["std"]
        else:
            length = bb_params["length"][1]  # 默認 20
            std = bb_params["std"][1]        # 默認 2.0
            
        bb_result = ta.bbands(df['close'], length=length, std=std)
        df = pd.concat([df, bb_result], axis=1)
        
        # ATR
        atr_length = volatility_config["atr"]["parameters"]["length"][1]  # 默認 14
        df[f'atr_{atr_length}'] = ta.atr(df['high'], df['low'], df['close'], length=atr_length)
        
        # Donchian Channel
        dc_length = volatility_config["donchian"]["parameters"]["length"][1]  # 默認 20
        dc_result = ta.donchian(df['high'], df['low'], length=dc_length)
        df = pd.concat([df, dc_result], axis=1)
        
        # Keltner Channel
        kc_params = volatility_config["kc"]["parameters"]
        kc_result = ta.kc(df['high'], df['low'], df['close'], 
                         length=kc_params["length"][1], 
                         scalar=kc_params["scalar"][1])
        df = pd.concat([df, kc_result], axis=1)
        
        return df
    
    def _calculate_volume_indicators(self, df: pd.DataFrame, strategy: str) -> pd.DataFrame:
        """計算成交量指標"""
        volume_config = self.config["volume_indicators"]
        
        # OBV
        df['obv'] = ta.obv(df['close'], df['volume'])
        
        # A/D Line
        df['ad'] = ta.ad(df['high'], df['low'], df['close'], df['volume'])
        
        # CMF
        cmf_length = volume_config["cmf"]["parameters"]["length"][1]  # 默認 20
        df[f'cmf_{cmf_length}'] = ta.cmf(df['high'], df['low'], df['close'], df['volume'], length=cmf_length)
        
        # MFI
        mfi_length = volume_config["mfi"]["parameters"]["length"][0]  # 默認 14
        # 確保 volume 欄位為正確的數據類型
        if 'volume' in df.columns:
            df['volume'] = df['volume'].astype('float64')  # 使用 float64 避免警告
        df[f'mfi_{mfi_length}'] = ta.mfi(df['high'], df['low'], df['close'], df['volume'], length=mfi_length)
        
        # VWAP
        df['vwap'] = ta.vwap(df['high'], df['low'], df['close'], df['volume'])
        
        return df
    
    def _calculate_candlestick_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算K線形態"""
        # 檢查是否有所需的 OHLC 數據
        if not all(col in df.columns for col in ['open', 'high', 'low', 'close']):
            return df
            
        # 使用 pandas-ta 的 CDL 策略計算 K線形態
        try:
            # 計算一些基本的 K線形態
            # Doji
            doji_df = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name="doji")
            if doji_df is not None:
                df = pd.concat([df, doji_df], axis=1)
            
            # Hammer (如果支援)
            try:
                hammer_df = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name="hammer")
                if hammer_df is not None:
                    df = pd.concat([df, hammer_df], axis=1)
            except:
                pass
                
            # Engulfing (如果支援)
            try:
                engulfing_df = ta.cdl_pattern(df['open'], df['high'], df['low'], df['close'], name="engulfing")
                if engulfing_df is not None:
                    df = pd.concat([df, engulfing_df], axis=1)
            except:
                pass
                
        except Exception as e:
            # 如果 K線形態計算失敗，添加空欄位以保持兼容性
            df['cdl_doji'] = 0
            df['cdl_hammer'] = 0
            df['cdl_engulfing'] = 0
        
        return df
    
    def generate_signals(self, df: pd.DataFrame, strategy: str = "swing", 
                        timeframe: str = "1h") -> List[TradingSignal]:
        """
        生成交易信號
        
        Args:
            df: 包含指標的數據框
            strategy: 交易策略類型
            timeframe: 時間框架
            
        Returns:
            交易信號列表
        """
        signals = []
        latest_idx = df.index[-1]
        current_time = df.index[-1] if hasattr(df.index[-1], 'to_pydatetime') else pd.Timestamp.now()
        
        # 趨勢信號
        signals.extend(self._generate_trend_signals(df, latest_idx, strategy, timeframe, current_time))
        
        # 動量信號
        signals.extend(self._generate_momentum_signals(df, latest_idx, strategy, timeframe, current_time))
        
        # 波動性信號
        signals.extend(self._generate_volatility_signals(df, latest_idx, strategy, timeframe, current_time))
        
        # 成交量信號
        if 'volume' in df.columns:
            signals.extend(self._generate_volume_signals(df, latest_idx, strategy, timeframe, current_time))
        
        # K線形態信號
        signals.extend(self._generate_candlestick_signals(df, latest_idx, strategy, timeframe, current_time))
        
        return signals
    
    def _generate_trend_signals(self, df: pd.DataFrame, idx: int, strategy: str, 
                               timeframe: str, current_time: pd.Timestamp) -> List[TradingSignal]:
        """生成趨勢信號"""
        signals = []
        trend_config = self.config["trend_indicators"]
        
        # MACD 信號
        if f'MACD_12_26_9' in df.columns and f'MACDs_12_26_9' in df.columns:
            macd = df.loc[idx, 'MACD_12_26_9']
            signal_line = df.loc[idx, 'MACDs_12_26_9']
            histogram = df.loc[idx, 'MACDh_12_26_9']
            
            if macd > signal_line and histogram > 0:
                signals.append(TradingSignal(
                    indicator="macd",
                    signal_type=SignalType.BUY,
                    strength=min(abs(histogram) * 10, 1.0),
                    value=macd,
                    condition_met="MACD 線上穿訊號線且柱狀圖 > 0",
                    timeframe=timeframe,
                    timestamp=current_time,
                    confidence=0.75
                ))
            elif macd < signal_line and histogram < 0:
                signals.append(TradingSignal(
                    indicator="macd",
                    signal_type=SignalType.SELL,
                    strength=min(abs(histogram) * 10, 1.0),
                    value=macd,
                    condition_met="MACD 線下穿訊號線且柱狀圖 < 0",
                    timeframe=timeframe,
                    timestamp=current_time,
                    confidence=0.75
                ))
        
        # ADX 信號
        if 'ADX_14' in df.columns and 'DMP_14' in df.columns and 'DMN_14' in df.columns:
            adx = df.loc[idx, 'ADX_14']
            di_plus = df.loc[idx, 'DMP_14']
            di_minus = df.loc[idx, 'DMN_14']
            
            if di_plus > di_minus and adx > 25:
                signals.append(TradingSignal(
                    indicator="adx",
                    signal_type=SignalType.BUY,
                    strength=min(adx / 50, 1.0),
                    value=adx,
                    condition_met="DI+ > DI- 且 ADX > 25",
                    timeframe=timeframe,
                    timestamp=current_time,
                    confidence=0.8
                ))
            elif di_minus > di_plus and adx > 25:
                signals.append(TradingSignal(
                    indicator="adx",
                    signal_type=SignalType.SELL,
                    strength=min(adx / 50, 1.0),
                    value=adx,
                    condition_met="DI- > DI+ 且 ADX > 25",
                    timeframe=timeframe,
                    timestamp=current_time,
                    confidence=0.8
                ))
        
        return signals
    
    def _generate_momentum_signals(self, df: pd.DataFrame, idx: int, strategy: str,
                                  timeframe: str, current_time: pd.Timestamp) -> List[TradingSignal]:
        """生成動量信號"""
        signals = []
        momentum_config = self.config["momentum_indicators"]
        
        # RSI 信號
        rsi_cols = [col for col in df.columns if col.startswith('rsi_')]
        if rsi_cols:
            rsi_col = rsi_cols[0]
            rsi = df.loc[idx, rsi_col]
            
            # 根據策略類型設置閾值
            rsi_params = momentum_config["rsi"]["parameters"]
            if strategy in rsi_params:
                oversold = rsi_params[strategy]["oversold"]
                overbought = rsi_params[strategy]["overbought"]
            else:
                oversold = 30
                overbought = 70
            
            if rsi < oversold:
                signals.append(TradingSignal(
                    indicator="rsi",
                    signal_type=SignalType.BUY,
                    strength=(oversold - rsi) / oversold,
                    value=rsi,
                    condition_met=f"RSI < {oversold} (超賣)",
                    timeframe=timeframe,
                    timestamp=current_time,
                    confidence=0.7
                ))
            elif rsi > overbought:
                signals.append(TradingSignal(
                    indicator="rsi",
                    signal_type=SignalType.SELL,
                    strength=(rsi - overbought) / (100 - overbought),
                    value=rsi,
                    condition_met=f"RSI > {overbought} (超買)",
                    timeframe=timeframe,
                    timestamp=current_time,
                    confidence=0.7
                ))
        
        # Stochastic 信號
        if 'STOCHk_14_3_3' in df.columns and 'STOCHd_14_3_3' in df.columns:
            k = df.loc[idx, 'STOCHk_14_3_3']
            d = df.loc[idx, 'STOCHd_14_3_3']
            
            if k < 20 and k > d:
                signals.append(TradingSignal(
                    indicator="stoch",
                    signal_type=SignalType.BUY,
                    strength=(20 - k) / 20,
                    value=k,
                    condition_met="%K < 20 且 %K 上穿 %D",
                    timeframe=timeframe,
                    timestamp=current_time,
                    confidence=0.65
                ))
            elif k > 80 and k < d:
                signals.append(TradingSignal(
                    indicator="stoch",
                    signal_type=SignalType.SELL,
                    strength=(k - 80) / 20,
                    value=k,
                    condition_met="%K > 80 且 %K 下穿 %D",
                    timeframe=timeframe,
                    timestamp=current_time,
                    confidence=0.65
                ))
        
        return signals
    
    def _generate_volatility_signals(self, df: pd.DataFrame, idx: int, strategy: str,
                                   timeframe: str, current_time: pd.Timestamp) -> List[TradingSignal]:
        """生成波動性信號"""
        signals = []
        
        # Bollinger Bands 信號
        bb_cols = [col for col in df.columns if 'BBL_' in col]
        if bb_cols and 'close' in df.columns:
            bb_lower = df.loc[idx, bb_cols[0]]
            bb_upper = df.loc[idx, bb_cols[0].replace('BBL_', 'BBU_')]
            close = df.loc[idx, 'close']
            
            if close < bb_lower:
                signals.append(TradingSignal(
                    indicator="bbands",
                    signal_type=SignalType.BUY,
                    strength=(bb_lower - close) / bb_lower,
                    value=close,
                    condition_met="價格觸及下軌",
                    timeframe=timeframe,
                    timestamp=current_time,
                    confidence=0.7
                ))
            elif close > bb_upper:
                signals.append(TradingSignal(
                    indicator="bbands",
                    signal_type=SignalType.SELL,
                    strength=(close - bb_upper) / bb_upper,
                    value=close,
                    condition_met="價格觸及上軌",
                    timeframe=timeframe,
                    timestamp=current_time,
                    confidence=0.7
                ))
        
        return signals
    
    def _generate_volume_signals(self, df: pd.DataFrame, idx: int, strategy: str,
                               timeframe: str, current_time: pd.Timestamp) -> List[TradingSignal]:
        """生成成交量信號"""
        signals = []
        
        # MFI 信號
        mfi_cols = [col for col in df.columns if col.startswith('mfi_')]
        if mfi_cols:
            mfi = df.loc[idx, mfi_cols[0]]
            
            if mfi < 20:
                signals.append(TradingSignal(
                    indicator="mfi",
                    signal_type=SignalType.BUY,
                    strength=(20 - mfi) / 20,
                    value=mfi,
                    condition_met="MFI < 20 (資金流入不足)",
                    timeframe=timeframe,
                    timestamp=current_time,
                    confidence=0.7
                ))
            elif mfi > 80:
                signals.append(TradingSignal(
                    indicator="mfi",
                    signal_type=SignalType.SELL,
                    strength=(mfi - 80) / 20,
                    value=mfi,
                    condition_met="MFI > 80 (資金流入過度)",
                    timeframe=timeframe,
                    timestamp=current_time,
                    confidence=0.7
                ))
        
        return signals
    
    def _generate_candlestick_signals(self, df: pd.DataFrame, idx: int, strategy: str,
                                    timeframe: str, current_time: pd.Timestamp) -> List[TradingSignal]:
        """生成K線形態信號"""
        signals = []
        
        # Hammer 信號
        if 'CDL_HAMMER' in df.columns:
            hammer = df.loc[idx, 'CDL_HAMMER']
            if hammer != 0:
                signal_type = SignalType.BUY if hammer > 0 else SignalType.SELL
                signals.append(TradingSignal(
                    indicator="hammer",
                    signal_type=signal_type,
                    strength=0.6,
                    value=hammer,
                    condition_met="錘子線形態",
                    timeframe=timeframe,
                    timestamp=current_time,
                    confidence=0.6
                ))
        
        # Engulfing 信號  
        if 'CDL_ENGULFING' in df.columns:
            engulfing = df.loc[idx, 'CDL_ENGULFING']
            if engulfing != 0:
                signal_type = SignalType.BUY if engulfing > 0 else SignalType.SELL
                signals.append(TradingSignal(
                    indicator="engulfing",
                    signal_type=signal_type,
                    strength=0.8,
                    value=engulfing,
                    condition_met="吞噬形態",
                    timeframe=timeframe,
                    timestamp=current_time,
                    confidence=0.75
                ))
        
        return signals
    
    def get_signal_summary(self, signals: List[TradingSignal]) -> Dict[str, Any]:
        """
        獲取信號摘要
        
        Args:
            signals: 交易信號列表
            
        Returns:
            信號摘要字典
        """
        if not signals:
            return {
                "total_signals": 0,
                "buy_signals": 0,
                "sell_signals": 0,
                "neutral_signals": 0,
                "average_confidence": 0.0,
                "strongest_signal": None,
                "overall_sentiment": "NEUTRAL"
            }
        
        buy_signals = [s for s in signals if s.signal_type in [SignalType.BUY, SignalType.STRONG_BUY]]
        sell_signals = [s for s in signals if s.signal_type in [SignalType.SELL, SignalType.STRONG_SELL]]
        neutral_signals = [s for s in signals if s.signal_type == SignalType.NEUTRAL]
        
        avg_confidence = np.mean([s.confidence for s in signals])
        strongest_signal = max(signals, key=lambda x: x.strength * x.confidence)
        
        # 計算整體情緒
        buy_strength = sum([s.strength * s.confidence for s in buy_signals])
        sell_strength = sum([s.strength * s.confidence for s in sell_signals])
        
        if buy_strength > sell_strength * 1.2:
            overall_sentiment = "BULLISH"
        elif sell_strength > buy_strength * 1.2:
            overall_sentiment = "BEARISH"
        else:
            overall_sentiment = "NEUTRAL"
        
        return {
            "total_signals": len(signals),
            "buy_signals": len(buy_signals),
            "sell_signals": len(sell_signals),
            "neutral_signals": len(neutral_signals),
            "average_confidence": round(avg_confidence, 3),
            "strongest_signal": {
                "indicator": strongest_signal.indicator,
                "type": strongest_signal.signal_type.value,
                "strength": round(strongest_signal.strength, 3),
                "confidence": round(strongest_signal.confidence, 3),
                "condition": strongest_signal.condition_met
            },
            "overall_sentiment": overall_sentiment,
            "buy_strength_total": round(buy_strength, 3),
            "sell_strength_total": round(sell_strength, 3)
        }

# 使用範例
if __name__ == "__main__":
    # 創建示例數據
    import yfinance as yf
    
    # 下載測試數據
    ticker = "BTCUSDT"  # 可以是任何交易對
    # df = yf.download(ticker, period="1mo", interval="1h")
    
    # 或使用模擬數據
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='1H')
    np.random.seed(42)
    price_base = 45000
    
    df = pd.DataFrame({
        'open': price_base + np.cumsum(np.random.randn(len(dates)) * 100),
        'high': None,
        'low': None,
        'close': None,
        'volume': np.random.randint(1000, 10000, len(dates))
    }, index=dates)
    
    df['close'] = df['open'] + np.random.randn(len(dates)) * 50
    df['high'] = df[['open', 'close']].max(axis=1) + np.random.rand(len(dates)) * 100
    df['low'] = df[['open', 'close']].min(axis=1) - np.random.rand(len(dates)) * 100
    
    # 初始化信號生成器
    signal_generator = PandasTATradingSignals()
    
    # 計算指標
    df_with_indicators = signal_generator.calculate_all_indicators(df, strategy="swing")
    
    # 生成信號
    signals = signal_generator.generate_signals(df_with_indicators, strategy="swing", timeframe="1h")
    
    # 獲取摘要
    summary = signal_generator.get_signal_summary(signals)
    
    print("=== 交易信號摘要 ===")
    print(f"總信號數: {summary['total_signals']}")
    print(f"買入信號: {summary['buy_signals']}")
    print(f"賣出信號: {summary['sell_signals']}")
    print(f"平均信心度: {summary['average_confidence']}")
    print(f"整體情緒: {summary['overall_sentiment']}")
    print(f"最強信號: {summary['strongest_signal']['indicator']} - {summary['strongest_signal']['type']}")
    
    print("\n=== 詳細信號 ===")
    for signal in signals[-5:]:  # 顯示最後 5 個信號
        print(f"{signal.indicator}: {signal.signal_type.value} "
              f"(強度: {signal.strength:.3f}, 信心: {signal.confidence:.3f}) "
              f"- {signal.condition_met}")
