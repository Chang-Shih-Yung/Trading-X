"""
pandas-ta 優化信號篩選器
基於 market_conditions_config 的多重確認機制
提升信號準確率和風險管理
"""

import pandas as pd
import numpy as np
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import logging
from app.services.pandas_ta_trading_signal_parser import PandasTATradingSignals, SignalType

logger = logging.getLogger(__name__)

@dataclass
class EnhancedSignal:
    """增強信號類別"""
    indicator: str
    signal_type: str
    confidence: float
    strength: float
    timeframe: str
    timestamp: datetime
    
    # 多重確認指標
    primary_confirmation: bool = False
    secondary_confirmation: bool = False
    volume_confirmation: bool = False
    trend_confirmation: bool = False
    
    # 風險評估
    risk_score: float = 0.0
    reward_potential: float = 0.0
    risk_reward_ratio: float = 0.0
    
    # 市場環境評分
    market_condition_score: float = 0.0
    
    def is_high_quality(self) -> bool:
        """判斷是否為高質量信號"""
        confirmations = sum([
            self.primary_confirmation,
            self.secondary_confirmation, 
            self.volume_confirmation,
            self.trend_confirmation
        ])
        
        return (confirmations >= 3 and 
                self.confidence > 0.75 and 
                self.risk_reward_ratio > 1.5 and
                self.market_condition_score > 0.6)

class OptimizedSignalFilter:
    """優化信號篩選器 - 基於 market_conditions_config 思路"""
    
    def __init__(self):
        self.signal_generator = PandasTATradingSignals()
        
        # 基於 market_conditions_config 的優化配置
        self.optimization_config = {
            "multi_confirmation": {
                "required_confirmations": 3,  # 至少需要3個確認
                "primary_weight": 0.4,
                "secondary_weight": 0.3,
                "volume_weight": 0.2,
                "trend_weight": 0.1
            },
            "market_filters": {
                "min_volume_ratio": 1.2,      # 成交量需高於平均20%
                "max_volatility": 0.08,       # 最大波動率8%
                "min_trend_strength": 0.3,    # 最小趨勢強度
                "rsi_range": [25, 75]         # RSI有效範圍
            },
            "risk_management": {
                "min_risk_reward": 1.5,       # 最小風險回報比
                "max_position_risk": 0.03,    # 最大倉位風險3%
                "stop_loss_atr_multiplier": 2.0,
                "take_profit_atr_multiplier": 4.0
            },
            "signal_quality": {
                "min_confidence": 0.75,       # 最低信心度
                "min_strength": 0.6,          # 最低信號強度
                "max_signal_age": 300,        # 信號最大有效期(秒)
            }
        }
    
    def generate_optimized_signals(self, df: pd.DataFrame, 
                                 strategy: str = "swing", 
                                 timeframe: str = "1h") -> List[EnhancedSignal]:
        """生成優化的高質量信號"""
        
        # 1. 計算所有技術指標
        df_with_indicators = self.signal_generator.calculate_all_indicators(df, strategy=strategy)
        
        # 2. 進行市場環境評估
        market_score = self._evaluate_market_conditions(df_with_indicators)
        
        if market_score < 0.4:  # 市場環境不佳，不生成信號
            logger.info(f"市場環境評分過低 ({market_score:.2f})，跳過信號生成")
            return []
        
        # 3. 生成基礎信號
        base_signals = self.signal_generator.generate_signals(df_with_indicators, strategy=strategy, timeframe=timeframe)
        
        # 4. 應用多重確認機制
        enhanced_signals = []
        for signal in base_signals:
            enhanced_signal = self._apply_multi_confirmation(signal, df_with_indicators, market_score)
            if enhanced_signal and enhanced_signal.confidence > self.optimization_config["signal_quality"]["min_confidence"]:
                enhanced_signals.append(enhanced_signal)
        
        # 5. 按質量排序並返回最佳信號
        enhanced_signals.sort(key=lambda x: (x.confidence * x.market_condition_score), reverse=True)
        
        # 6. 只保留高質量信號
        high_quality_signals = [s for s in enhanced_signals if s.is_high_quality()]
        
        logger.info(f"生成 {len(base_signals)} 個基礎信號，篩選出 {len(high_quality_signals)} 個高質量信號")
        
        return high_quality_signals[:5]  # 最多返回5個最佳信號
    
    def _evaluate_market_conditions(self, df: pd.DataFrame) -> float:
        """評估市場環境質量 - 參考 market_conditions_config 邏輯"""
        
        if len(df) < 20:
            return 0.0
        
        score = 0.0
        max_score = 0.0
        
        try:
            # 1. 成交量條件 (權重: 25%)
            if 'volume' in df.columns:
                recent_volume = df['volume'].iloc[-5:].mean()
                avg_volume = df['volume'].iloc[-20:].mean()
                volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 0
                
                volume_score = min(volume_ratio / 1.5, 1.0) if volume_ratio >= 1.2 else 0
                score += volume_score * 0.25
            max_score += 0.25
            
            # 2. 波動率條件 (權重: 20%)
            price_changes = df['close'].pct_change().dropna()
            volatility = price_changes.std() * np.sqrt(24)  # 日化波動率
            
            if 0.02 <= volatility <= 0.08:  # 適中波動率
                volatility_score = 1.0 - abs(volatility - 0.04) / 0.04
            else:
                volatility_score = 0.0
            
            score += volatility_score * 0.20
            max_score += 0.20
            
            # 3. 趨勢清晰度 (權重: 30%)
            if len(df) >= 20:
                sma_5 = df['close'].rolling(5).mean().iloc[-1]
                sma_20 = df['close'].rolling(20).mean().iloc[-1]
                current_price = df['close'].iloc[-1]
                
                # 檢查趨勢方向一致性
                trend_consistency = 0.0
                if sma_5 > sma_20 and current_price > sma_5:  # 上升趨勢
                    trend_consistency = min((sma_5 - sma_20) / sma_20, 0.1) / 0.1
                elif sma_5 < sma_20 and current_price < sma_5:  # 下降趨勢
                    trend_consistency = min((sma_20 - sma_5) / sma_20, 0.1) / 0.1
                
                score += trend_consistency * 0.30
            max_score += 0.30
            
            # 4. RSI 狀態 (權重: 15%)
            if f'rsi_14' in df.columns:
                rsi = df[f'rsi_14'].iloc[-1]
                if 25 <= rsi <= 75:  # RSI在正常範圍
                    rsi_score = 1.0 - abs(rsi - 50) / 25  # 越接近50越好
                else:
                    rsi_score = 0.0
                
                score += rsi_score * 0.15
            max_score += 0.15
            
            # 5. MACD 信號質量 (權重: 10%)
            if f'macd_12_26_9' in df.columns and f'macdh_12_26_9' in df.columns:
                macd = df[f'macd_12_26_9'].iloc[-1]
                macd_hist = df[f'macdh_12_26_9'].iloc[-1]
                
                # MACD與柱狀圖同向為好信號
                if (macd > 0 and macd_hist > 0) or (macd < 0 and macd_hist < 0):
                    macd_score = min(abs(macd_hist) / abs(macd) if abs(macd) > 0 else 0, 1.0)
                else:
                    macd_score = 0.0
                
                score += macd_score * 0.10
            max_score += 0.10
            
        except Exception as e:
            logger.error(f"市場條件評估錯誤: {e}")
            return 0.0
        
        return score / max_score if max_score > 0 else 0.0
    
    def _apply_multi_confirmation(self, signal, df: pd.DataFrame, market_score: float) -> Optional[EnhancedSignal]:
        """應用多重確認機制"""
        
        try:
            enhanced_signal = EnhancedSignal(
                indicator=signal.indicator,
                signal_type=signal.signal_type.value if hasattr(signal.signal_type, 'value') else str(signal.signal_type),
                confidence=signal.confidence,
                strength=signal.strength,
                timeframe=getattr(signal, 'timeframe', '1h'),
                timestamp=datetime.now(),
                market_condition_score=market_score
            )
            
            # 1. 主要確認 - 檢查指標本身的信號強度
            enhanced_signal.primary_confirmation = (
                signal.confidence > 0.7 and 
                signal.strength > 0.6
            )
            
            # 2. 次要確認 - 檢查相關指標
            enhanced_signal.secondary_confirmation = self._check_secondary_indicators(signal, df)
            
            # 3. 成交量確認
            enhanced_signal.volume_confirmation = self._check_volume_confirmation(signal, df)
            
            # 4. 趨勢確認
            enhanced_signal.trend_confirmation = self._check_trend_confirmation(signal, df)
            
            # 5. 計算風險回報比
            risk_reward = self._calculate_risk_reward(signal, df)
            enhanced_signal.risk_score = risk_reward.get('risk', 0.03)
            enhanced_signal.reward_potential = risk_reward.get('reward', 0.06)
            enhanced_signal.risk_reward_ratio = risk_reward.get('ratio', 2.0)
            
            # 6. 調整最終信心度
            confirmation_boost = sum([
                enhanced_signal.primary_confirmation * 0.4,
                enhanced_signal.secondary_confirmation * 0.3,
                enhanced_signal.volume_confirmation * 0.2,
                enhanced_signal.trend_confirmation * 0.1
            ])
            
            enhanced_signal.confidence = min(
                enhanced_signal.confidence * (1 + confirmation_boost) * market_score,
                1.0
            )
            
            return enhanced_signal
            
        except Exception as e:
            logger.error(f"多重確認處理錯誤: {e}")
            return None
    
    def _check_secondary_indicators(self, signal, df: pd.DataFrame) -> bool:
        """檢查次要指標確認"""
        
        try:
            confirmations = 0
            total_checks = 0
            
            # RSI 確認
            if f'rsi_14' in df.columns:
                rsi = df[f'rsi_14'].iloc[-1]
                if signal.signal_type in ['BUY', 'LONG'] and rsi < 60:
                    confirmations += 1
                elif signal.signal_type in ['SELL', 'SHORT'] and rsi > 40:
                    confirmations += 1
                total_checks += 1
            
            # MACD 確認
            if f'macd_12_26_9' in df.columns:
                macd = df[f'macd_12_26_9'].iloc[-1]
                macd_signal = df[f'macds_12_26_9'].iloc[-1] if f'macds_12_26_9' in df.columns else 0
                
                if signal.signal_type in ['BUY', 'LONG'] and macd > macd_signal:
                    confirmations += 1
                elif signal.signal_type in ['SELL', 'SHORT'] and macd < macd_signal:
                    confirmations += 1
                total_checks += 1
            
            # 移動平均確認
            if 'close' in df.columns and len(df) >= 20:
                current_price = df['close'].iloc[-1]
                sma_10 = df['close'].rolling(10).mean().iloc[-1]
                sma_20 = df['close'].rolling(20).mean().iloc[-1]
                
                if signal.signal_type in ['BUY', 'LONG'] and current_price > sma_10 > sma_20:
                    confirmations += 1
                elif signal.signal_type in ['SELL', 'SHORT'] and current_price < sma_10 < sma_20:
                    confirmations += 1
                total_checks += 1
            
            return confirmations >= (total_checks * 0.6) if total_checks > 0 else False
            
        except Exception as e:
            logger.error(f"次要指標確認錯誤: {e}")
            return False
    
    def _check_volume_confirmation(self, signal, df: pd.DataFrame) -> bool:
        """檢查成交量確認"""
        
        try:
            if 'volume' not in df.columns or len(df) < 10:
                return False
            
            recent_volume = df['volume'].iloc[-3:].mean()
            avg_volume = df['volume'].iloc[-20:].mean()
            volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 0
            
            # 強信號需要成交量配合
            if signal.strength > 0.7:
                return volume_ratio > 1.2
            else:
                return volume_ratio > 1.0
                
        except Exception as e:
            logger.error(f"成交量確認錯誤: {e}")
            return False
    
    def _check_trend_confirmation(self, signal, df: pd.DataFrame) -> bool:
        """檢查趨勢確認"""
        
        try:
            if len(df) < 20:
                return False
            
            # 計算不同週期的移動平均
            sma_5 = df['close'].rolling(5).mean().iloc[-1]
            sma_10 = df['close'].rolling(10).mean().iloc[-1]
            sma_20 = df['close'].rolling(20).mean().iloc[-1]
            current_price = df['close'].iloc[-1]
            
            if signal.signal_type in ['BUY', 'LONG']:
                # 買入信號：價格在均線之上且均線呈多頭排列
                return (current_price > sma_5 > sma_10 and sma_10 > sma_20)
            elif signal.signal_type in ['SELL', 'SHORT']:
                # 賣出信號：價格在均線之下且均線呈空頭排列
                return (current_price < sma_5 < sma_10 and sma_10 < sma_20)
            
            return False
            
        except Exception as e:
            logger.error(f"趨勢確認錯誤: {e}")
            return False
    
    def _calculate_risk_reward(self, signal, df: pd.DataFrame) -> Dict[str, float]:
        """計算風險回報比"""
        
        try:
            current_price = df['close'].iloc[-1]
            
            # 計算 ATR 作為波動率參考
            if len(df) >= 14:
                high_low = df['high'] - df['low']
                high_close = abs(df['high'] - df['close'].shift(1))
                low_close = abs(df['low'] - df['close'].shift(1))
                true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                atr = true_range.rolling(14).mean().iloc[-1]
            else:
                atr = current_price * 0.02  # 預設2%波動
            
            # 根據信號類型計算止損止盈
            atr_multiplier = self.optimization_config["risk_management"]["stop_loss_atr_multiplier"]
            profit_multiplier = self.optimization_config["risk_management"]["take_profit_atr_multiplier"]
            
            if signal.signal_type in ['BUY', 'LONG']:
                stop_loss = current_price - (atr * atr_multiplier)
                take_profit = current_price + (atr * profit_multiplier)
            else:
                stop_loss = current_price + (atr * atr_multiplier)
                take_profit = current_price - (atr * profit_multiplier)
            
            risk = abs(current_price - stop_loss) / current_price
            reward = abs(take_profit - current_price) / current_price
            ratio = reward / risk if risk > 0 else 0
            
            return {
                'risk': risk,
                'reward': reward,
                'ratio': ratio,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'atr': atr
            }
            
        except Exception as e:
            logger.error(f"風險回報計算錯誤: {e}")
            return {'risk': 0.03, 'reward': 0.06, 'ratio': 2.0}
    
    def generate_signal_report(self, signals: List[EnhancedSignal]) -> Dict[str, Any]:
        """生成詳細的信號報告"""
        
        if not signals:
            return {
                'total_signals': 0,
                'high_quality_signals': 0,
                'average_confidence': 0.0,
                'average_risk_reward': 0.0,
                'market_conditions': 'POOR',
                'recommendation': 'WAIT'
            }
        
        high_quality = [s for s in signals if s.is_high_quality()]
        
        avg_confidence = np.mean([s.confidence for s in signals])
        avg_risk_reward = np.mean([s.risk_reward_ratio for s in signals if s.risk_reward_ratio > 0])
        avg_market_score = np.mean([s.market_condition_score for s in signals])
        
        # 市場狀態評估
        if avg_market_score > 0.7:
            market_condition = 'EXCELLENT'
            recommendation = 'AGGRESSIVE'
        elif avg_market_score > 0.5:
            market_condition = 'GOOD'
            recommendation = 'MODERATE'
        elif avg_market_score > 0.3:
            market_condition = 'FAIR'
            recommendation = 'CONSERVATIVE'
        else:
            market_condition = 'POOR'
            recommendation = 'WAIT'
        
        return {
            'total_signals': len(signals),
            'high_quality_signals': len(high_quality),
            'average_confidence': avg_confidence,
            'average_risk_reward': avg_risk_reward,
            'average_market_score': avg_market_score,
            'market_conditions': market_condition,
            'recommendation': recommendation,
            'best_signal': high_quality[0].__dict__ if high_quality else None,
            'signal_distribution': {
                'BUY': len([s for s in signals if s.signal_type in ['BUY', 'LONG']]),
                'SELL': len([s for s in signals if s.signal_type in ['SELL', 'SHORT']]),
                'NEUTRAL': len([s for s in signals if s.signal_type == 'NEUTRAL'])
            }
        }

# 全局優化信號篩選器實例
optimized_filter = OptimizedSignalFilter()
