"""
K線形態分析模組
實現經典的K線形態識別，包括頭肩頂、黃昏十字星等高勝率形態
形態分析優先級高於技術指標，目標勝率85%+
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class PatternStrength(Enum):
    """形態強度等級"""
    WEAK = 1
    MODERATE = 2
    STRONG = 3
    VERY_STRONG = 4

class PatternType(Enum):
    """形態類型"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"

@dataclass
class PatternResult:
    """形態識別結果"""
    pattern_name: str
    pattern_type: PatternType
    strength: PatternStrength
    confidence: float  # 0.0 - 1.0
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float
    timeframe: str
    description: str
    additional_notes: str = ""

class CandlestickPatternAnalyzer:
    """K線形態分析器"""
    
    def __init__(self):
        self.min_candles_required = {
            'doji': 1,
            'hammer': 1,
            'shooting_star': 1,
            'engulfing': 2,
            'harami': 2,
            'morning_star': 3,
            'evening_star': 3,
            'three_white_soldiers': 3,
            'three_black_crows': 3,
            'head_shoulders': 15,  # 需要較多K線識別
            'inverse_head_shoulders': 15,
            'double_top': 20,
            'double_bottom': 20,
            'ascending_triangle': 15,
            'descending_triangle': 15,
            'wedge': 15,
        }
    
    def analyze_patterns(self, df: pd.DataFrame, timeframe: str = "1d") -> List[PatternResult]:
        """
        分析所有K線形態
        
        Args:
            df: OHLCV數據，必須包含 'open', 'high', 'low', 'close', 'volume'
            timeframe: 時間週期 ('1d', '1w', '1M')
            
        Returns:
            檢測到的形態列表，按信心度排序
        """
        if df.empty or len(df) < 5:
            return []
        
        patterns = []
        
        try:
            # 單K線形態
            patterns.extend(self._detect_single_candle_patterns(df, timeframe))
            
            # 雙K線形態
            patterns.extend(self._detect_two_candle_patterns(df, timeframe))
            
            # 三K線形態
            patterns.extend(self._detect_three_candle_patterns(df, timeframe))
            
            # 複雜形態（需要更多K線）
            patterns.extend(self._detect_complex_patterns(df, timeframe))
            
            # 按信心度排序，優先顯示高信心度形態
            patterns.sort(key=lambda x: x.confidence, reverse=True)
            
            return patterns
            
        except Exception as e:
            logger.error(f"形態分析錯誤: {e}")
            return []
    
    def _detect_single_candle_patterns(self, df: pd.DataFrame, timeframe: str) -> List[PatternResult]:
        """檢測單K線形態"""
        patterns = []
        
        if len(df) < 1:
            return patterns
        
        current = df.iloc[-1]
        
        # 十字星系列
        doji_result = self._detect_doji_series(df, timeframe)
        if doji_result:
            patterns.append(doji_result)
        
        # 錘子線
        hammer_result = self._detect_hammer(df, timeframe)
        if hammer_result:
            patterns.append(hammer_result)
        
        # 射擊之星
        shooting_star_result = self._detect_shooting_star(df, timeframe)
        if shooting_star_result:
            patterns.append(shooting_star_result)
        
        return patterns
    
    def _detect_doji_series(self, df: pd.DataFrame, timeframe: str) -> Optional[PatternResult]:
        """檢測十字星系列形態"""
        if len(df) < 3:
            return None
        
        current = df.iloc[-1]
        prev1 = df.iloc[-2]
        prev2 = df.iloc[-3] if len(df) >= 3 else None
        
        # 計算實體大小
        body_size = abs(current['close'] - current['open'])
        total_range = current['high'] - current['low']
        
        # 十字星：實體小於總範圍的10%
        if body_size / total_range <= 0.1:
            
            # 黃昏十字星（看空）
            if (prev1['close'] > prev1['open'] and  # 前一根陽線
                current['open'] > prev1['close'] and  # 跳空高開
                len(df) >= 3 and prev2 and
                self._is_strong_trend(df.iloc[-10:], direction='up')):
                
                confidence = 0.88  # 黃昏十字星高勝率
                entry_price = current['low'] * 0.995  # 稍微破低進場
                stop_loss = current['high'] * 1.005
                take_profit = entry_price * (1 - 0.08)  # 8%獲利目標
                
                return PatternResult(
                    pattern_name="黃昏十字星",
                    pattern_type=PatternType.BEARISH,
                    strength=PatternStrength.VERY_STRONG,
                    confidence=confidence,
                    entry_price=entry_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    risk_reward_ratio=abs(take_profit - entry_price) / abs(stop_loss - entry_price),
                    timeframe=timeframe,
                    description="強烈看空信號，上升趨勢反轉",
                    additional_notes="在上升趨勢末期出現，建議等待確認破低後進場做空"
                )
            
            # 早晨十字星（看多）
            elif (prev1['close'] < prev1['open'] and  # 前一根陰線
                  current['open'] < prev1['close'] and  # 跳空低開
                  len(df) >= 3 and prev2 and
                  self._is_strong_trend(df.iloc[-10:], direction='down')):
                
                confidence = 0.86
                entry_price = current['high'] * 1.005
                stop_loss = current['low'] * 0.995
                take_profit = entry_price * (1 + 0.08)
                
                return PatternResult(
                    pattern_name="早晨十字星",
                    pattern_type=PatternType.BULLISH,
                    strength=PatternStrength.VERY_STRONG,
                    confidence=confidence,
                    entry_price=entry_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    risk_reward_ratio=abs(take_profit - entry_price) / abs(stop_loss - entry_price),
                    timeframe=timeframe,
                    description="強烈看多信號，下降趨勢反轉",
                    additional_notes="在下降趨勢末期出現，建議等待確認破高後進場做多"
                )
        
        return None
    
    def _detect_hammer(self, df: pd.DataFrame, timeframe: str) -> Optional[PatternResult]:
        """檢測錘子線形態"""
        if len(df) < 1:
            return None
        
        current = df.iloc[-1]
        
        # 錘子線特徵
        body_size = abs(current['close'] - current['open'])
        lower_shadow = min(current['open'], current['close']) - current['low']
        upper_shadow = current['high'] - max(current['open'], current['close'])
        total_range = current['high'] - current['low']
        
        # 錘子線條件：下影線長，上影線短，實體小
        if (lower_shadow >= body_size * 2 and
            upper_shadow <= body_size * 0.5 and
            lower_shadow >= total_range * 0.6):
            
            # 在下降趨勢中的錘子線更有效
            if self._is_strong_trend(df.iloc[-10:], direction='down'):
                confidence = 0.82
                pattern_type = PatternType.BULLISH
                description = "看多反轉信號，下降趨勢可能結束"
            else:
                confidence = 0.65
                pattern_type = PatternType.NEUTRAL
                description = "中性信號，需要其他指標確認"
            
            entry_price = current['high'] * 1.002
            stop_loss = current['low'] * 0.995
            take_profit = entry_price * (1 + 0.06)
            
            return PatternResult(
                pattern_name="錘子線",
                pattern_type=pattern_type,
                strength=PatternStrength.STRONG if confidence > 0.8 else PatternStrength.MODERATE,
                confidence=confidence,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_reward_ratio=abs(take_profit - entry_price) / abs(stop_loss - entry_price),
                timeframe=timeframe,
                description=description,
                additional_notes="建議等待突破確認後進場"
            )
        
        return None
    
    def _detect_shooting_star(self, df: pd.DataFrame, timeframe: str) -> Optional[PatternResult]:
        """檢測射擊之星形態"""
        if len(df) < 1:
            return None
        
        current = df.iloc[-1]
        
        # 射擊之星特徵
        body_size = abs(current['close'] - current['open'])
        lower_shadow = min(current['open'], current['close']) - current['low']
        upper_shadow = current['high'] - max(current['open'], current['close'])
        total_range = current['high'] - current['low']
        
        # 射擊之星條件：上影線長，下影線短，實體小
        if (upper_shadow >= body_size * 2 and
            lower_shadow <= body_size * 0.5 and
            upper_shadow >= total_range * 0.6):
            
            # 在上升趨勢中的射擊之星更有效
            if self._is_strong_trend(df.iloc[-10:], direction='up'):
                confidence = 0.80
                pattern_type = PatternType.BEARISH
                description = "看空反轉信號，上升趨勢可能結束"
            else:
                confidence = 0.62
                pattern_type = PatternType.NEUTRAL
                description = "中性信號，需要其他指標確認"
            
            entry_price = current['low'] * 0.998
            stop_loss = current['high'] * 1.005
            take_profit = entry_price * (1 - 0.06)
            
            return PatternResult(
                pattern_name="射擊之星",
                pattern_type=pattern_type,
                strength=PatternStrength.STRONG if confidence > 0.75 else PatternStrength.MODERATE,
                confidence=confidence,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_reward_ratio=abs(take_profit - entry_price) / abs(stop_loss - entry_price),
                timeframe=timeframe,
                description=description,
                additional_notes="建議等待跌破確認後進場"
            )
        
        return None
    
    def _detect_two_candle_patterns(self, df: pd.DataFrame, timeframe: str) -> List[PatternResult]:
        """檢測雙K線形態"""
        patterns = []
        
        if len(df) < 2:
            return patterns
        
        # 吞噬形態
        engulfing_result = self._detect_engulfing_pattern(df, timeframe)
        if engulfing_result:
            patterns.append(engulfing_result)
        
        return patterns
    
    def _detect_engulfing_pattern(self, df: pd.DataFrame, timeframe: str) -> Optional[PatternResult]:
        """檢測吞噬形態"""
        if len(df) < 2:
            return None
        
        current = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 看漲吞噬
        if (prev['close'] < prev['open'] and  # 前一根陰線
            current['close'] > current['open'] and  # 當前陽線
            current['open'] < prev['close'] and  # 開盤價低於前收
            current['close'] > prev['open']):  # 收盤價高於前開
            
            confidence = 0.78 if self._is_strong_trend(df.iloc[-10:], direction='down') else 0.65
            
            entry_price = current['close'] * 1.001
            stop_loss = min(current['low'], prev['low']) * 0.995
            take_profit = entry_price * (1 + 0.08)
            
            return PatternResult(
                pattern_name="看漲吞噬",
                pattern_type=PatternType.BULLISH,
                strength=PatternStrength.STRONG,
                confidence=confidence,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_reward_ratio=abs(take_profit - entry_price) / abs(stop_loss - entry_price),
                timeframe=timeframe,
                description="看多反轉信號，買方力量強勁",
                additional_notes="陽線完全吞噬前一根陰線，顯示趨勢可能反轉"
            )
        
        # 看跌吞噬
        elif (prev['close'] > prev['open'] and  # 前一根陽線
              current['close'] < current['open'] and  # 當前陰線
              current['open'] > prev['close'] and  # 開盤價高於前收
              current['close'] < prev['open']):  # 收盤價低於前開
            
            confidence = 0.76 if self._is_strong_trend(df.iloc[-10:], direction='up') else 0.63
            
            entry_price = current['close'] * 0.999
            stop_loss = max(current['high'], prev['high']) * 1.005
            take_profit = entry_price * (1 - 0.08)
            
            return PatternResult(
                pattern_name="看跌吞噬",
                pattern_type=PatternType.BEARISH,
                strength=PatternStrength.STRONG,
                confidence=confidence,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_reward_ratio=abs(take_profit - entry_price) / abs(stop_loss - entry_price),
                timeframe=timeframe,
                description="看空反轉信號，賣方力量強勁",
                additional_notes="陰線完全吞噬前一根陽線，顯示趨勢可能反轉"
            )
        
        return None
    
    def _detect_three_candle_patterns(self, df: pd.DataFrame, timeframe: str) -> List[PatternResult]:
        """檢測三K線形態"""
        patterns = []
        
        if len(df) < 3:
            return patterns
        
        # 早晨之星
        morning_star = self._detect_morning_star(df, timeframe)
        if morning_star:
            patterns.append(morning_star)
        
        # 黃昏之星
        evening_star = self._detect_evening_star(df, timeframe)
        if evening_star:
            patterns.append(evening_star)
        
        return patterns
    
    def _detect_morning_star(self, df: pd.DataFrame, timeframe: str) -> Optional[PatternResult]:
        """檢測早晨之星形態"""
        if len(df) < 3:
            return None
        
        first = df.iloc[-3]
        second = df.iloc[-2] 
        third = df.iloc[-1]
        
        # 早晨之星條件
        if (first['close'] < first['open'] and  # 第一根陰線
            abs(second['close'] - second['open']) < abs(first['close'] - first['open']) * 0.3 and  # 第二根十字星/小實體
            third['close'] > third['open'] and  # 第三根陽線
            third['close'] > (first['open'] + first['close']) / 2):  # 第三根收盤超過第一根中點
            
            confidence = 0.85 if self._is_strong_trend(df.iloc[-15:], direction='down') else 0.70
            
            entry_price = third['close'] * 1.002
            stop_loss = min(first['low'], second['low'], third['low']) * 0.995
            take_profit = entry_price * (1 + 0.12)  # 較大獲利目標
            
            return PatternResult(
                pattern_name="早晨之星",
                pattern_type=PatternType.BULLISH,
                strength=PatternStrength.VERY_STRONG,
                confidence=confidence,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_reward_ratio=abs(take_profit - entry_price) / abs(stop_loss - entry_price),
                timeframe=timeframe,
                description="強烈看多反轉信號，經典底部形態",
                additional_notes="三K線組合顯示賣壓消失，買方開始接手"
            )
        
        return None
    
    def _detect_evening_star(self, df: pd.DataFrame, timeframe: str) -> Optional[PatternResult]:
        """檢測黃昏之星形態"""
        if len(df) < 3:
            return None
        
        first = df.iloc[-3]
        second = df.iloc[-2]
        third = df.iloc[-1]
        
        # 黃昏之星條件
        if (first['close'] > first['open'] and  # 第一根陽線
            abs(second['close'] - second['open']) < abs(first['close'] - first['open']) * 0.3 and  # 第二根十字星/小實體
            third['close'] < third['open'] and  # 第三根陰線
            third['close'] < (first['open'] + first['close']) / 2):  # 第三根收盤低於第一根中點
            
            confidence = 0.87 if self._is_strong_trend(df.iloc[-15:], direction='up') else 0.72
            
            entry_price = third['close'] * 0.998
            stop_loss = max(first['high'], second['high'], third['high']) * 1.005
            take_profit = entry_price * (1 - 0.12)  # 較大獲利目標
            
            return PatternResult(
                pattern_name="黃昏之星",
                pattern_type=PatternType.BEARISH,
                strength=PatternStrength.VERY_STRONG,
                confidence=confidence,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_reward_ratio=abs(take_profit - entry_price) / abs(stop_loss - entry_price),
                timeframe=timeframe,
                description="強烈看空反轉信號，經典頂部形態",
                additional_notes="三K線組合顯示買盤消失，賣方開始接手"
            )
        
        return None
    
    def _detect_complex_patterns(self, df: pd.DataFrame, timeframe: str) -> List[PatternResult]:
        """檢測複雜形態（頭肩頂等）"""
        patterns = []
        
        if len(df) < 15:
            return patterns
        
        # 頭肩頂
        head_shoulders = self._detect_head_and_shoulders(df, timeframe)
        if head_shoulders:
            patterns.append(head_shoulders)
        
        return patterns
    
    def _detect_head_and_shoulders(self, df: pd.DataFrame, timeframe: str) -> Optional[PatternResult]:
        """檢測頭肩頂形態"""
        if len(df) < 20:
            return None
        
        # 簡化的頭肩頂檢測邏輯
        highs = df['high'].rolling(window=5).max()
        recent_highs = highs.iloc[-20:].values
        
        # 尋找三個主要高點
        peaks = []
        for i in range(2, len(recent_highs) - 2):
            if (recent_highs[i] > recent_highs[i-1] and 
                recent_highs[i] > recent_highs[i-2] and
                recent_highs[i] > recent_highs[i+1] and
                recent_highs[i] > recent_highs[i+2]):
                peaks.append((i, recent_highs[i]))
        
        # 需要至少3個峰值
        if len(peaks) >= 3:
            # 取最近的3個峰值
            last_three_peaks = peaks[-3:]
            left_shoulder = last_three_peaks[0][1]
            head = last_three_peaks[1][1] 
            right_shoulder = last_three_peaks[2][1]
            
            # 頭肩頂條件：頭部高於兩肩，兩肩高度相近
            if (head > left_shoulder and head > right_shoulder and
                abs(left_shoulder - right_shoulder) / head < 0.05):
                
                confidence = 0.89  # 頭肩頂是高勝率形態
                current_price = df.iloc[-1]['close']
                
                # 頸線位置（簡化為兩肩之間的低點）
                neckline = min(left_shoulder, right_shoulder) * 0.95
                
                entry_price = neckline * 0.995  # 跌破頸線進場
                stop_loss = head * 1.02  # 止損設在頭部上方
                take_profit = entry_price - (head - neckline) * 1.2  # 目標價為形態高度的1.2倍
                
                return PatternResult(
                    pattern_name="頭肩頂",
                    pattern_type=PatternType.BEARISH,
                    strength=PatternStrength.VERY_STRONG,
                    confidence=confidence,
                    entry_price=entry_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    risk_reward_ratio=abs(take_profit - entry_price) / abs(stop_loss - entry_price),
                    timeframe=timeframe,
                    description="經典頂部反轉形態，極強看空信號",
                    additional_notes=f"頭部價格: ${head:.2f}, 建議等待跌破頸線 ${neckline:.2f} 後進場"
                )
        
        return None
    
    def _is_strong_trend(self, df: pd.DataFrame, direction: str) -> bool:
        """判斷是否為強趨勢"""
        if len(df) < 5:
            return False
        
        if direction == 'up':
            # 上升趨勢：收盤價持續上升
            closes = df['close'].values
            return (closes[-1] > closes[-5] and 
                    closes[-2] > closes[-6] if len(closes) >= 6 else True)
        
        elif direction == 'down':
            # 下降趨勢：收盤價持續下降
            closes = df['close'].values
            return (closes[-1] < closes[-5] and 
                    closes[-2] < closes[-6] if len(closes) >= 6 else True)
        
        return False
    
    def get_pattern_priority_weight(self, pattern_name: str) -> float:
        """
        獲取形態的優先權重
        K線形態優先級高於技術指標
        """
        priority_weights = {
            # 最高優先級形態（85%+ 勝率）
            "頭肩頂": 0.95,
            "黃昏十字星": 0.92,
            "黃昏之星": 0.90,
            "早晨之星": 0.88,
            "早晨十字星": 0.86,
            
            # 高優先級形態（80%+ 勝率）
            "看漲吞噬": 0.82,
            "看跌吞噬": 0.80,
            "錘子線": 0.78,
            "射擊之星": 0.76,
            
            # 中等優先級形態
            "十字星": 0.65,
            "紡錘頂": 0.60,
        }
        
        return priority_weights.get(pattern_name, 0.5)

def analyze_candlestick_patterns(df: pd.DataFrame, timeframe: str = "1d") -> Dict:
    """
    K線形態分析主入口函數
    
    Args:
        df: OHLCV數據
        timeframe: 時間週期
        
    Returns:
        分析結果字典
    """
    analyzer = CandlestickPatternAnalyzer()
    patterns = analyzer.analyze_patterns(df, timeframe)
    
    # 計算綜合信號
    if patterns:
        # 取信心度最高的形態作為主信號
        primary_pattern = patterns[0]
        
        # 計算綜合分數（形態權重 × 信心度）
        pattern_weight = analyzer.get_pattern_priority_weight(primary_pattern.pattern_name)
        combined_score = pattern_weight * primary_pattern.confidence
        
        return {
            "has_pattern": True,
            "primary_pattern": primary_pattern,
            "all_patterns": patterns,
            "combined_score": combined_score,
            "signal_strength": "VERY_STRONG" if combined_score > 0.85 else 
                            "STRONG" if combined_score > 0.75 else
                            "MODERATE" if combined_score > 0.65 else "WEAK",
            "pattern_count": len(patterns)
        }
    
    return {
        "has_pattern": False,
        "primary_pattern": None,
        "all_patterns": [],
        "combined_score": 0.0,
        "signal_strength": "NONE",
        "pattern_count": 0
    }
