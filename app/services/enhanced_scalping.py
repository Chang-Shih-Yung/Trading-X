"""
增強短線信號生成服務
整合牛熊市分析、動態止盈止損和突破檢測
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np

from ..utils.time_utils import get_taiwan_now_naive, taiwan_now_plus
from dataclasses import dataclass, asdict
import logging
import json
import hashlib

from app.services.market_analysis import (
    MarketAnalysisService,
    MarketCondition,
    DynamicStopLoss,
    BreakoutSignal,
    SignalDirection,
    MarketTrend,
    MarketPhase
)
from app.services.technical_indicators import TechnicalIndicatorsService
from app.services.market_data import MarketDataService

logger = logging.getLogger(__name__)

@dataclass
class EnhancedSignal:
    """增強型短線信號"""
    id: str
    symbol: str
    signal_type: str  # LONG, SHORT
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    urgency_level: str
    timeframe: str
    expires_at: datetime
    created_at: datetime
    
    # 市場分析相關
    market_condition: Dict[str, Any]
    bull_score: float
    bear_score: float
    market_phase: Optional[str]
    
    # 技術分析相關
    breakout_analysis: Dict[str, Any]
    technical_indicators: Dict[str, Any]
    risk_reward_ratio: float
    
    # 增強信息
    reasoning: str
    strategy_name: str
    key_factors: List[str]
    
    # 動態調整信息
    atr_adjusted: bool
    market_condition_adjusted: bool
    volatility_level: str

class EnhancedScalpingService:
    """增強短線交易服務"""
    
    def __init__(self):
        self.market_analyzer = MarketAnalysisService()
        self.technical_service = TechnicalIndicatorsService()
        self.market_data_service = MarketDataService()
        
        # 配置參數
        self.min_confidence = 0.75
        self.max_signals_per_symbol = 3
        self.timeframes = ['1m', '3m', '5m', '15m', '30m']
        self.target_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT']
        
        # 信號緩存 - 用於保持信號的持久性
        self.signal_cache: Dict[str, EnhancedSignal] = {}
        self.cache_expiry_hours = 2  # 緩存2小時後過期
        
    def _generate_signal_key(self, symbol: str, signal_type: str, timeframe: str, 
                           strategy_name: str, urgency_level: str) -> str:
        """生成信號的唯一鍵值"""
        key_data = f"{symbol}_{signal_type}_{timeframe}_{strategy_name}_{urgency_level}"
        return hashlib.md5(key_data.encode()).hexdigest()[:16]
    
    def _is_signal_expired(self, signal: EnhancedSignal) -> bool:
        """檢查信號是否過期"""
        return get_taiwan_now_naive() > signal.expires_at
    
    def _cleanup_expired_signals(self):
        """清理過期的緩存信號"""
        expired_keys = [
            key for key, signal in self.signal_cache.items()
            if self._is_signal_expired(signal)
        ]
        
        for key in expired_keys:
            del self.signal_cache[key]
            
        if expired_keys:
            logger.info(f"清理了 {len(expired_keys)} 個過期信號")
    
    async def generate_enhanced_signals(self, 
                                      symbols: Optional[List[str]] = None,
                                      market_condition_filter: Optional[str] = None) -> List[EnhancedSignal]:
        """
        生成增強型短線信號
        
        Args:
            symbols: 目標交易對列表
            market_condition_filter: 市場條件篩選 ('bull', 'bear', 'neutral')
            
        Returns:
            List[EnhancedSignal]: 增強型信號列表
        """
        try:
            # 清理過期信號
            self._cleanup_expired_signals()
            
            symbols = symbols or self.target_symbols
            all_signals = []
            
            for symbol in symbols:
                try:
                    symbol_signals = await self._generate_symbol_signals(symbol, market_condition_filter)
                    all_signals.extend(symbol_signals)
                except Exception as e:
                    logger.error(f"生成 {symbol} 信號失敗: {e}")
                    continue
            
            # 排序和去重
            final_signals = self._rank_and_filter_signals(all_signals)
            
            logger.info(f"成功生成 {len(final_signals)} 個增強型短線信號")
            return final_signals
            
        except Exception as e:
            logger.error(f"生成增強信號失敗: {e}")
            return []
    
    async def _generate_symbol_signals(self, 
                                     symbol: str, 
                                     market_condition_filter: Optional[str] = None) -> List[EnhancedSignal]:
        """為單個交易對生成信號"""
        signals = []
        
        for timeframe in self.timeframes:
            try:
                # 獲取價格數據
                price_data = await self.market_data_service.get_kline_data(
                    symbol=symbol,
                    interval=timeframe,
                    limit=200
                )
                
                if price_data is None or price_data.empty:
                    continue
                
                # 市場分析
                market_condition = self.market_analyzer.analyze_market_condition(price_data)
                
                # 市場條件篩選
                if market_condition_filter:
                    if market_condition_filter.lower() != market_condition.trend.value.lower():
                        continue
                
                # 突破分析
                breakout_signal = self.market_analyzer.detect_breakout_signals(price_data)
                
                # 技術指標分析
                technical_analysis = await self._analyze_technical_indicators(price_data, timeframe)
                
                # 生成信號
                symbol_signals = await self._create_signals_from_analysis(
                    symbol=symbol,
                    timeframe=timeframe,
                    price_data=price_data,
                    market_condition=market_condition,
                    breakout_signal=breakout_signal,
                    technical_analysis=technical_analysis
                )
                
                signals.extend(symbol_signals)
                
            except Exception as e:
                logger.error(f"分析 {symbol} {timeframe} 失敗: {e}")
                continue
        
        return signals
    
    async def _analyze_technical_indicators(self, 
                                          price_data: pd.DataFrame, 
                                          timeframe: str) -> Dict[str, Any]:
        """分析技術指標"""
        try:
            # 計算各類技術指標
            trend_indicators = self.technical_service.calculate_trend_indicators(price_data)
            momentum_indicators = self.technical_service.calculate_momentum_indicators(price_data)
            volatility_indicators = self.technical_service.calculate_volatility_indicators(price_data)
            volume_indicators = self.technical_service.calculate_volume_indicators(price_data)
            
            # 綜合評分
            trend_score = sum(ind.strength for ind in trend_indicators.values()) / len(trend_indicators)
            momentum_score = sum(ind.strength for ind in momentum_indicators.values()) / len(momentum_indicators)
            
            # 計算總體技術分數
            technical_score = (trend_score * 0.4 + momentum_score * 0.3 + 
                             (volatility_indicators.get('atr', type('obj', (object,), {'strength': 0.5})).strength) * 0.2 +
                             (volume_indicators.get('volume_sma', type('obj', (object,), {'strength': 0.5})).strength) * 0.1)
            
            return {
                'trend_indicators': {k: {'value': v.value, 'signal': v.signal, 'strength': v.strength} 
                                   for k, v in trend_indicators.items()},
                'momentum_indicators': {k: {'value': v.value, 'signal': v.signal, 'strength': v.strength} 
                                      for k, v in momentum_indicators.items()},
                'volatility_indicators': {k: {'value': v.value, 'signal': v.signal, 'strength': v.strength} 
                                        for k, v in volatility_indicators.items()},
                'volume_indicators': {k: {'value': v.value, 'signal': v.signal, 'strength': v.strength} 
                                    for k, v in volume_indicators.items()},
                'technical_score': technical_score,
                'trend_score': trend_score,
                'momentum_score': momentum_score
            }
            
        except Exception as e:
            logger.error(f"技術指標分析失敗: {e}")
            return {
                'technical_score': 0.5,
                'trend_score': 0.5,
                'momentum_score': 0.5,
                'trend_indicators': {},
                'momentum_indicators': {},
                'volatility_indicators': {},
                'volume_indicators': {}
            }
    
    async def _create_signals_from_analysis(self,
                                          symbol: str,
                                          timeframe: str,
                                          price_data: pd.DataFrame,
                                          market_condition: MarketCondition,
                                          breakout_signal: BreakoutSignal,
                                          technical_analysis: Dict[str, Any]) -> List[EnhancedSignal]:
        """根據分析結果創建信號"""
        signals = []
        current_price = price_data['close'].iloc[-1]
        
        # 判斷信號方向
        signal_directions = self._determine_signal_directions(
            market_condition, breakout_signal, technical_analysis
        )
        
        for direction, confidence in signal_directions:
            if confidence < self.min_confidence:
                continue
            
            try:
                # 計算動態止盈止損
                stop_loss = self.market_analyzer.calculate_dynamic_stop_loss(
                    entry_price=current_price,
                    signal_direction=direction,
                    price_data=price_data,
                    market_condition=market_condition,
                    timeframe=timeframe
                )
                
                # 計算過期時間
                expires_at = self._calculate_expiry_time(timeframe, market_condition)
                
                # 確定緊急程度
                urgency_level = self._determine_urgency_level(
                    confidence, breakout_signal, market_condition
                )
                
                # 確定策略名稱
                strategy_name = self._determine_strategy_name(
                    market_condition, breakout_signal, timeframe
                )
                
                # 生成信號鍵值
                signal_key = self._generate_signal_key(
                    symbol, direction.value, timeframe, strategy_name, urgency_level
                )
                
                # 檢查緩存中是否已有此信號
                if signal_key in self.signal_cache:
                    cached_signal = self.signal_cache[signal_key]
                    if not self._is_signal_expired(cached_signal):
                        # 更新價格信息但保持時間戳
                        cached_signal.entry_price = current_price
                        cached_signal.stop_loss = stop_loss.stop_loss_price
                        cached_signal.take_profit = stop_loss.take_profit_price
                        cached_signal.confidence = confidence
                        signals.append(cached_signal)
                        logger.info(f"使用緩存信號: {signal_key}")
                        continue
                
                # 生成新信號
                signal_id = f"scalp_{symbol}_{timeframe}_{int(get_taiwan_now_naive().timestamp())}"
                
                # 生成推理說明
                reasoning = self._generate_reasoning(
                    symbol, direction, market_condition, breakout_signal, technical_analysis
                )
                
                # 生成關鍵因素
                key_factors = self._extract_key_factors(
                    market_condition, breakout_signal, technical_analysis
                )
                
                # 確定波動率級別
                volatility_level = self._determine_volatility_level(price_data)
                
                signal = EnhancedSignal(
                    id=signal_id,
                    symbol=symbol,
                    signal_type=direction.value,
                    entry_price=current_price,
                    stop_loss=stop_loss.stop_loss_price,
                    take_profit=stop_loss.take_profit_price,
                    confidence=confidence,
                    urgency_level=urgency_level,
                    timeframe=timeframe,
                    expires_at=expires_at,
                    created_at=get_taiwan_now_naive(),
                    market_condition={
                        'trend': market_condition.trend.value,
                        'phase': market_condition.phase.value if market_condition.phase else None,
                        'confidence': market_condition.confidence
                    },
                    bull_score=market_condition.bull_score,
                    bear_score=market_condition.bear_score,
                    market_phase=market_condition.phase.value if market_condition.phase else None,
                    breakout_analysis={
                        'is_breakout': breakout_signal.is_breakout,
                        'breakout_type': breakout_signal.breakout_type,
                        'strength': breakout_signal.strength,
                        'volume_ratio': breakout_signal.volume_ratio,
                        'indicators_confirmation': breakout_signal.indicators_confirmation
                    },
                    technical_indicators=technical_analysis,
                    risk_reward_ratio=stop_loss.risk_reward_ratio,
                    reasoning=reasoning,
                    strategy_name=strategy_name,
                    key_factors=key_factors,
                    atr_adjusted=stop_loss.atr_adjusted,
                    market_condition_adjusted=stop_loss.market_condition_adjusted,
                    volatility_level=volatility_level
                )
                
                # 添加到信號列表
                signals.append(signal)
                
                # 添加到緩存
                self.signal_cache[signal_key] = signal
                logger.info(f"新信號添加到緩存: {signal_key}")
                
            except Exception as e:
                logger.error(f"創建信號失敗 {symbol} {direction.value}: {e}")
                continue
        
        return signals
    
    def _determine_signal_directions(self,
                                   market_condition: MarketCondition,
                                   breakout_signal: BreakoutSignal,
                                   technical_analysis: Dict[str, Any]) -> List[Tuple[SignalDirection, float]]:
        """確定信號方向和信心度"""
        directions = []
        
        # 基礎信心度來自技術分析
        base_confidence = technical_analysis.get('technical_score', 0.5)
        
        # 牛市邏輯
        if market_condition.trend == MarketTrend.BULL:
            # 牛市優先做多
            long_confidence = base_confidence + market_condition.confidence * 0.2
            
            # 突破信號加成
            if breakout_signal.is_breakout and breakout_signal.strength > 0.6:
                long_confidence += 0.1
            
            # 牛市階段調整
            if market_condition.phase == MarketPhase.MAIN_BULL:
                long_confidence += 0.1
            elif market_condition.phase == MarketPhase.HIGH_VOLATILITY:
                long_confidence -= 0.05  # 高位震盪降低信心
            elif market_condition.phase == MarketPhase.LATE_BULL:
                long_confidence -= 0.1   # 牛尾降低信心
            
            directions.append((SignalDirection.LONG, min(long_confidence, 0.95)))
            
            # 牛市中的短線空單（逆勢）
            if technical_analysis.get('momentum_score', 0.5) < 0.3:  # 動能疲軟
                short_confidence = base_confidence * 0.6  # 逆勢信心較低
                if short_confidence >= self.min_confidence:
                    directions.append((SignalDirection.SHORT, short_confidence))
        
        # 熊市邏輯
        elif market_condition.trend == MarketTrend.BEAR:
            # 熊市優先做空
            short_confidence = base_confidence + market_condition.confidence * 0.2
            
            # 突破信號加成
            if breakout_signal.is_breakout and breakout_signal.strength > 0.6:
                short_confidence += 0.1
            
            directions.append((SignalDirection.SHORT, min(short_confidence, 0.95)))
            
            # 熊市中的反彈多單
            if technical_analysis.get('momentum_score', 0.5) > 0.7:  # 強勢反彈
                long_confidence = base_confidence * 0.7
                if long_confidence >= self.min_confidence:
                    directions.append((SignalDirection.LONG, long_confidence))
        
        # 中性市場
        else:
            # 根據技術指標決定
            if technical_analysis.get('trend_score', 0.5) > 0.6:
                directions.append((SignalDirection.LONG, base_confidence))
            elif technical_analysis.get('trend_score', 0.5) < 0.4:
                directions.append((SignalDirection.SHORT, base_confidence))
        
        return directions
    
    def _calculate_expiry_time(self, timeframe: str, market_condition: MarketCondition) -> datetime:
        """計算信號過期時間"""
        base_hours = {
            '1m': 0.5,   # 30分鐘
            '3m': 1,     # 1小時
            '5m': 2,     # 2小時
            '15m': 4,    # 4小時
            '30m': 8     # 8小時
        }
        
        hours = base_hours.get(timeframe, 2)
        
        # 市場條件調整
        if market_condition.trend == MarketTrend.BULL and market_condition.phase == MarketPhase.MAIN_BULL:
            hours *= 1.5  # 牛市主升段延長有效期
        elif market_condition.trend == MarketTrend.BEAR:
            hours *= 0.8  # 熊市縮短有效期
        
        return taiwan_now_plus(hours=hours)
    
    def _determine_urgency_level(self,
                               confidence: float,
                               breakout_signal: BreakoutSignal,
                               market_condition: MarketCondition) -> str:
        """確定緊急程度"""
        if (confidence > 0.9 and 
            breakout_signal.is_breakout and 
            breakout_signal.strength > 0.8):
            return "urgent"
        elif (confidence > 0.85 and 
              (breakout_signal.is_breakout or market_condition.confidence > 0.8)):
            return "high"
        elif confidence > 0.75:
            return "medium"
        else:
            return "low"
    
    def _generate_reasoning(self,
                          symbol: str,
                          direction: SignalDirection,
                          market_condition: MarketCondition,
                          breakout_signal: BreakoutSignal,
                          technical_analysis: Dict[str, Any]) -> str:
        """生成推理說明"""
        reasons = []
        
        # 市場環境
        if market_condition.trend == MarketTrend.BULL:
            reasons.append(f"牛市環境(牛市分數{market_condition.bull_score:.1f})")
            if market_condition.phase:
                phase_desc = {
                    MarketPhase.EARLY_BULL: "初升段",
                    MarketPhase.MAIN_BULL: "主升段", 
                    MarketPhase.HIGH_VOLATILITY: "高位震盪",
                    MarketPhase.LATE_BULL: "牛尾期"
                }
                reasons.append(f"當前處於{phase_desc.get(market_condition.phase, '未知階段')}")
        
        # 突破信號
        if breakout_signal.is_breakout:
            reasons.append(f"檢測到{breakout_signal.breakout_type}突破(強度{breakout_signal.strength:.2f})")
        
        # 技術指標
        tech_score = technical_analysis.get('technical_score', 0.5)
        if tech_score > 0.7:
            reasons.append(f"技術指標強勢({tech_score:.2f})")
        elif tech_score < 0.3:
            reasons.append(f"技術指標疲軟({tech_score:.2f})")
        
        # 信號方向邏輯
        if direction == SignalDirection.LONG:
            reasons.append("建議做多")
        else:
            reasons.append("建議做空")
        
        return " | ".join(reasons)
    
    def _determine_strategy_name(self,
                               market_condition: MarketCondition,
                               breakout_signal: BreakoutSignal,
                               timeframe: str) -> str:
        """確定策略名稱"""
        if breakout_signal.is_breakout:
            if breakout_signal.breakout_type == "volume_price_breakout":
                return f"量價突破-{timeframe}"
            elif breakout_signal.breakout_type == "momentum_breakout":
                return f"動量突破-{timeframe}"
            else:
                return f"技術突破-{timeframe}"
        
        if market_condition.trend == MarketTrend.BULL:
            if market_condition.phase == MarketPhase.MAIN_BULL:
                return f"牛市主升-{timeframe}"
            else:
                return f"牛市順勢-{timeframe}"
        elif market_condition.trend == MarketTrend.BEAR:
            return f"熊市空頭-{timeframe}"
        else:
            return f"震盪交易-{timeframe}"
    
    def _extract_key_factors(self,
                           market_condition: MarketCondition,
                           breakout_signal: BreakoutSignal,
                           technical_analysis: Dict[str, Any]) -> List[str]:
        """提取關鍵因素"""
        factors = []
        
        # 市場條件因素
        factors.extend(market_condition.key_factors[:2])  # 取前2個
        
        # 突破因素
        if breakout_signal.is_breakout:
            confirmed = [k for k, v in breakout_signal.indicators_confirmation.items() if v]
            if confirmed:
                factors.append(f"突破確認: {', '.join(confirmed[:2])}")
        
        # 技術指標因素
        if technical_analysis.get('trend_score', 0) > 0.7:
            factors.append("趨勢指標強勢")
        if technical_analysis.get('momentum_score', 0) > 0.7:
            factors.append("動量指標強勢")
        
        return factors[:5]  # 最多5個因素
    
    def _determine_volatility_level(self, price_data: pd.DataFrame) -> str:
        """確定波動率級別"""
        returns = price_data['close'].pct_change().dropna()
        if len(returns) < 10:
            return "medium"
        
        volatility = returns.std() * np.sqrt(365)  # 年化波動率
        
        if volatility > 0.5:
            return "high"
        elif volatility > 0.3:
            return "medium"
        else:
            return "low"
    
    def _rank_and_filter_signals(self, signals: List[EnhancedSignal]) -> List[EnhancedSignal]:
        """排序和篩選信號"""
        if not signals:
            return []
        
        # 按交易對分組
        symbol_groups = {}
        for signal in signals:
            if signal.symbol not in symbol_groups:
                symbol_groups[signal.symbol] = []
            symbol_groups[signal.symbol].append(signal)
        
        final_signals = []
        
        # 每個交易對選取最佳信號
        for symbol, symbol_signals in symbol_groups.items():
            # 排序：緊急程度 > 信心度 > 突破強度
            sorted_signals = sorted(symbol_signals, key=lambda s: (
                {'urgent': 4, 'high': 3, 'medium': 2, 'low': 1}.get(s.urgency_level, 1),
                s.confidence,
                s.breakout_analysis.get('strength', 0)
            ), reverse=True)
            
            # 每個交易對最多保留指定數量的信號
            final_signals.extend(sorted_signals[:self.max_signals_per_symbol])
        
        # 全域排序
        final_signals.sort(key=lambda s: (
            {'urgent': 4, 'high': 3, 'medium': 2, 'low': 1}.get(s.urgency_level, 1),
            s.confidence,
            s.breakout_analysis.get('strength', 0)
        ), reverse=True)
        
        return final_signals[:20]  # 最多返回20個信號
