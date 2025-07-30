"""
精準信號篩選服務 - 零備選模式 (Phase 1+2 動態適應版本)
Phase 1: 基於動態市場適應的多維度評分系統，移除雙重信心度過濾，實現ATR動態止損止盈
Phase 2: 整合市場機制識別和Fear & Greed Index，實現機制適應性交易策略
只保留最精準的單一信號，備選信號直接銷毀
集成 AI 混合決策系統與智能共振濾波器
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import numpy as np

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.services.market_data import MarketDataService
from app.services.technical_indicators import TechnicalIndicatorsService
from app.services.market_analysis import MarketAnalysisService
from app.services.dynamic_market_adapter import dynamic_adapter, MarketState, DynamicThresholds
from app.core.database import AsyncSessionLocal
from app.models.models import TradingSignal

def get_taiwan_now_naive():
    """獲取台灣時間（無時區信息）"""
    return datetime.now()
from app.utils.time_utils import get_taiwan_now_naive
from sqlalchemy import delete, update, select
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)

@dataclass
class PrecisionSignal:
    """精準篩選信號"""
    symbol: str
    signal_type: str  # LONG, SHORT
    strategy_name: str
    confidence: float
    precision_score: float
    entry_price: float
    stop_loss: float
    take_profit: float
    timeframe: str
    created_at: datetime
    expires_at: datetime
    
    # 市場條件評分
    market_condition_score: float
    indicator_consistency: float
    timing_score: float
    risk_adjustment: float
    
    # 原始數據
    market_data: Dict[str, Any]
    technical_indicators: Dict[str, Any]
    
    def dict(self):
        """轉換為字典格式"""
        return {
            'symbol': self.symbol,
            'signal_type': self.signal_type,
            'strategy_name': self.strategy_name,
            'confidence': self.confidence,
            'precision_score': self.precision_score,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'timeframe': self.timeframe,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'market_condition_score': self.market_condition_score,
            'indicator_consistency': self.indicator_consistency,
            'timing_score': self.timing_score,
            'risk_adjustment': self.risk_adjustment
        }

@dataclass
class ConsensusSignal:
    """智能共振信號"""
    symbol: str
    signal_type: str
    consensus_score: float
    contributing_indicators: List[str]
    indicator_weights: Dict[str, float]
    sentiment_status: str
    confidence: float
    created_at: datetime

class IntelligentConsensusFilter:
    """智能共振濾波器 - AI混合決策系統"""
    
    def __init__(self):
        self.config = self._load_consensus_config()
        self.performance_history = {}
        self.adaptive_parameters = self.config.get('adaptive_parameters', {})
        
    def _load_consensus_config(self) -> Dict:
        """載入智能共振配置"""
        try:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                'config', 
                'intelligent_consensus_config.json'
            )
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"載入智能共振配置失敗: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """默認配置"""
        return {
            "consensus_filter": {
                "required_consensus": 5,
                "indicators": {
                    "RSI": {"weight": 0.2, "enabled": True},
                    "MACD": {"weight": 0.25, "enabled": True},
                    "Stochastic": {"weight": 0.15, "enabled": True},
                    "OBV": {"weight": 0.2, "enabled": True},
                    "BollingerBands": {"weight": 0.2, "enabled": True}
                }
            },
            "sentiment_guard": {"enabled": True}
        }
    
    async def analyze_consensus(self, symbol: str, market_data: Dict[str, Any]) -> Optional[ConsensusSignal]:
        """執行智能共振分析"""
        try:
            # 1. 計算各指標信號
            indicator_signals = await self._calculate_indicator_signals(symbol, market_data)
            
            # 2. 執行共振分析
            consensus_result = self._evaluate_consensus(indicator_signals)
            
            # 3. 情緒防護檢查
            sentiment_status = self._check_sentiment_guard(market_data)
            
            # 4. 自適應參數調整
            adjusted_consensus = self._apply_adaptive_adjustments(consensus_result, sentiment_status)
            
            # 5. 生成最終共振信號
            if adjusted_consensus['meets_threshold']:
                return ConsensusSignal(
                    symbol=symbol,
                    signal_type=adjusted_consensus['signal_type'],
                    consensus_score=adjusted_consensus['score'],
                    contributing_indicators=adjusted_consensus['contributors'],
                    indicator_weights=adjusted_consensus['weights'],
                    sentiment_status=sentiment_status,
                    confidence=adjusted_consensus['confidence'],
                    created_at=get_taiwan_now_naive()
                )
            
            return None
            
        except Exception as e:
            logger.error(f"智能共振分析失敗 {symbol}: {e}")
            return None
    
    async def _calculate_indicator_signals(self, symbol: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """計算各指標信號"""
        signals = {}
        
        try:
            indicators_config = self.config['consensus_filter']['indicators']
            
            # RSI 信號
            if indicators_config.get('RSI', {}).get('enabled', False):
                rsi = market_data.get('rsi', 50)
                rsi_config = indicators_config['RSI']['thresholds']
                
                if rsi < rsi_config['long_entry']:
                    signals['RSI'] = {'signal': 'BUY', 'strength': (rsi_config['long_entry'] - rsi) / rsi_config['long_entry']}
                elif rsi > rsi_config['short_entry']:
                    signals['RSI'] = {'signal': 'SELL', 'strength': (rsi - rsi_config['short_entry']) / (100 - rsi_config['short_entry'])}
                else:
                    signals['RSI'] = {'signal': 'NEUTRAL', 'strength': 0}
            
            # MACD 信號 (簡化版本)
            if indicators_config.get('MACD', {}).get('enabled', False):
                signals['MACD'] = {'signal': 'NEUTRAL', 'strength': 0}
            
            # Stochastic 信號 (簡化版本)
            if indicators_config.get('Stochastic', {}).get('enabled', False):
                signals['Stochastic'] = {'signal': 'NEUTRAL', 'strength': 0}
            
            # OBV 信號 (簡化版本)
            if indicators_config.get('OBV', {}).get('enabled', False):
                signals['OBV'] = {'signal': 'NEUTRAL', 'strength': 0}
            
            # Bollinger Bands 信號 (簡化版本)
            if indicators_config.get('BollingerBands', {}).get('enabled', False):
                signals['BollingerBands'] = {'signal': 'NEUTRAL', 'strength': 0}
            
            return signals
            
        except Exception as e:
            logger.error(f"計算指標信號失敗: {e}")
            return {}
    
    def _evaluate_consensus(self, indicator_signals: Dict[str, Any]) -> Dict[str, Any]:
        """評估指標共振"""
        try:
            buy_signals = []
            sell_signals = []
            weights_config = self.config['consensus_filter']['indicators']
            required_consensus = self.config['consensus_filter']['required_consensus']
            
            for indicator, signal_data in indicator_signals.items():
                if signal_data['signal'] == 'BUY':
                    weight = weights_config.get(indicator, {}).get('weight', 0.1)
                    buy_signals.append({
                        'indicator': indicator,
                        'weight': weight,
                        'strength': signal_data['strength']
                    })
                elif signal_data['signal'] == 'SELL':
                    weight = weights_config.get(indicator, {}).get('weight', 0.1)
                    sell_signals.append({
                        'indicator': indicator,
                        'weight': weight,
                        'strength': signal_data['strength']
                    })
            
            # 計算加權共振分數
            buy_score = sum(s['weight'] * s['strength'] for s in buy_signals)
            sell_score = sum(s['weight'] * s['strength'] for s in sell_signals)
            
            # 檢查是否達到共振閾值
            buy_count = len(buy_signals)
            sell_count = len(sell_signals)
            
            result = {
                'meets_threshold': False,
                'signal_type': 'NEUTRAL',
                'score': 0,
                'contributors': [],
                'weights': {},
                'confidence': 0
            }
            
            if buy_count >= required_consensus and buy_score > sell_score:
                result.update({
                    'meets_threshold': True,
                    'signal_type': 'BUY',
                    'score': buy_score,
                    'contributors': [s['indicator'] for s in buy_signals],
                    'weights': {s['indicator']: s['weight'] for s in buy_signals},
                    'confidence': min(buy_score, 1.0)
                })
            elif sell_count >= required_consensus and sell_score > buy_score:
                result.update({
                    'meets_threshold': True,
                    'signal_type': 'SELL',
                    'score': sell_score,
                    'contributors': [s['indicator'] for s in sell_signals],
                    'weights': {s['indicator']: s['weight'] for s in sell_signals},
                    'confidence': min(sell_score, 1.0)
                })
            
            return result
            
        except Exception as e:
            logger.error(f"評估共振失敗: {e}")
            return {'meets_threshold': False, 'signal_type': 'NEUTRAL', 'score': 0}
    
    def _check_sentiment_guard(self, market_data: Dict[str, Any]) -> str:
        """檢查情緒防護狀態"""
        try:
            guard_config = self.config.get('sentiment_guard', {})
            if not guard_config.get('enabled', False):
                return 'normal'
            
            extreme_conditions = guard_config.get('extreme_conditions', {})
            
            # RSI過熱檢查
            rsi = market_data.get('rsi', 50)
            if rsi > extreme_conditions.get('rsi_overheat', {}).get('threshold', 90):
                return 'overheat_block_long'
            
            if rsi < extreme_conditions.get('rsi_oversold_extreme', {}).get('threshold', 10):
                return 'oversold_block_short'
            
            # 成交量激增檢查
            volume_ratio = market_data.get('volume_ratio', 1)
            volume_threshold = extreme_conditions.get('volume_spike', {}).get('threshold_multiplier', 2.0)
            if volume_ratio > volume_threshold:
                return 'volume_spike_cautious'
            
            # 波動率極端檢查
            volatility = market_data.get('volatility', 0.02)
            vol_threshold = extreme_conditions.get('price_volatility_extreme', {}).get('threshold_multiplier', 3.0)
            if volatility > vol_threshold * 0.02:  # 假設基準波動率為2%
                return 'volatility_extreme_block_all'
            
            return 'normal'
            
        except Exception as e:
            logger.error(f"情緒防護檢查失敗: {e}")
            return 'normal'
    
    def _apply_adaptive_adjustments(self, consensus_result: Dict[str, Any], sentiment_status: str) -> Dict[str, Any]:
        """應用自適應調整"""
        adjusted_result = consensus_result.copy()
        
        # 根據情緒狀態調整
        if sentiment_status == 'overheat_block_long' and consensus_result['signal_type'] == 'BUY':
            adjusted_result['meets_threshold'] = False
            adjusted_result['signal_type'] = 'BLOCKED'
        elif sentiment_status == 'oversold_block_short' and consensus_result['signal_type'] == 'SELL':
            adjusted_result['meets_threshold'] = False
            adjusted_result['signal_type'] = 'BLOCKED'
        elif sentiment_status == 'volatility_extreme_block_all':
            adjusted_result['meets_threshold'] = False
            adjusted_result['signal_type'] = 'BLOCKED'
        
        return adjusted_result

class MarketConditionsConfig:
    """市場條件配置 - 精準篩選標準"""
    
    def __init__(self):
        self.precision_thresholds = {
            # 基礎精準度要求 (降低閾值以便生成更多信號)
            "min_confidence": 0.35,        # 最低信心度 (從0.75降至0.35)
            "min_volume_ratio": 0.8,       # 最低成交量比率 (從1.2降至0.8)
            "max_spread": 0.01,            # 最大價差 (從0.002提升至0.01, 1%)
            
            # 技術指標精準度 (放寬限制)
            "rsi_precision": {
                "oversold_max": 35,        # 超賣上限 (從25放寬至35)
                "overbought_min": 65,      # 超買下限 (從75放寬至65)
                "neutral_exclude": False   # 允許中性區間信號
            },
            
            # 趨勢強度要求 (降低門檻)
            "trend_strength_min": 0.3,     # 最小趨勢強度 (從0.6降至0.3)
            "momentum_threshold": 0.4,      # 動量閾值 (從0.7降至0.4)
            
            # 波動率篩選 (放寬範圍)
            "volatility_range": {
                "min": 0.005,              # 最小波動率 (從1.5%降至0.5%)
                "max": 0.08,               # 最大波動率 (從5%提升至8%)
                "optimal": 0.025           # 最佳波動率 (2.5%)
            },
            
            # 時機精準度 (更靈活的時間限制)
            "time_precision": {
                "market_hours_only": False,  # 允許全天候交易
                "exclude_news_time": False,  # 允許新聞時段
                "optimal_hours": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]  # 全天候最佳時段
            }
        }
    
    def is_market_condition_optimal(self, market_data: dict) -> bool:
        """檢查市場條件是否達到最佳狀態"""
        
        current_hour = datetime.now().hour
        
        # 時機檢查
        if current_hour not in self.precision_thresholds["time_precision"]["optimal_hours"]:
            return False
        
        # 成交量檢查
        volume_ratio = market_data.get("volume_ratio", 0)
        if volume_ratio < self.precision_thresholds["min_volume_ratio"]:
            return False
        
        # 價差檢查
        spread = market_data.get("spread", 0)
        if spread > self.precision_thresholds["max_spread"]:
            return False
        
        # 波動率檢查
        volatility = market_data.get("volatility", 0)
        vol_range = self.precision_thresholds["volatility_range"]
        if not (vol_range["min"] <= volatility <= vol_range["max"]):
            return False
        
        return True

class PrecisionSignalFilter:
    """精準信號篩選器 - Phase 1 動態適應版本"""
    
    def __init__(self):
        self.market_config = MarketConditionsConfig()
        self.market_service = MarketDataService()
        self.technical_service = TechnicalIndicatorsService()
        self.market_analyzer = MarketAnalysisService()
        
        # Phase 1: 整合動態市場適應器
        self.dynamic_adapter = dynamic_adapter
        
        # 初始化智能共振濾波器
        self.intelligent_consensus = IntelligentConsensusFilter()
        
        self.strategy_weights = {
            # 策略可靠性權重 (基於歷史表現)
            "momentum_scalp": 0.85,
            "breakout_scalp": 0.90,     # 突破策略較可靠
            "reversal_scalp": 0.75,     # 反轉策略風險較高
            "volume_scalp": 0.80,
            "enhanced_momentum": 0.88
        }
    
    async def execute_precision_selection(self, symbol: str) -> Optional[PrecisionSignal]:
        """🎯 Phase 1 核心：執行動態適應精準篩選"""
        
        try:
            # 1. 獲取動態市場狀態
            market_state = await self.dynamic_adapter.get_market_state(symbol)
            
            # 2. 計算動態閾值
            dynamic_thresholds = self.dynamic_adapter.get_dynamic_indicator_params(market_state)
            
            # 3. 獲取市場數據
            market_data = await self.get_comprehensive_market_data(symbol)
            
            # 4. 🔥 使用動態閾值檢查市場條件（移除固定限制）
            if not self._is_dynamic_market_condition_optimal(market_data, dynamic_thresholds):
                logger.info(f"{symbol} 動態市場條件評估：不符合當前閾值標準")
                return None
            
            # 5. 智能共振分析 - AI混合決策系統
            consensus_signal = await self.intelligent_consensus.analyze_consensus(symbol, market_data)
            
            # 6. 🎯 執行動態策略（使用動態參數）
            strategy_results = await self.execute_dynamic_strategies(symbol, market_data, dynamic_thresholds)
            
            # 7. 集成共振分析結果
            if consensus_signal and strategy_results:
                strategy_results = self._integrate_consensus_results(strategy_results, consensus_signal)
            
            # 8. 🔧 使用動態信心度閾值進行精準篩選
            best_signal = await self.select_precision_signal_dynamic(
                strategy_results, market_data, dynamic_thresholds
            )
            
            if best_signal:
                # 9. 🎯 應用ATR動態止損止盈
                best_signal = self._apply_dynamic_risk_management(best_signal, market_state)
                
                # 10. 最終驗證
                if await self.final_precision_check_dynamic(best_signal, market_data, dynamic_thresholds):
                    logger.info(f"✅ Phase 1 動態精準信號: {symbol} - {best_signal.strategy_name} "
                               f"(信心度: {best_signal.confidence:.3f}, "
                               f"精準度: {best_signal.precision_score:.3f}, "
                               f"動態閾值: {dynamic_thresholds.confidence_threshold:.3f})")
                    return best_signal
                else:
                    logger.info(f"❌ 信號未通過動態最終驗證: {symbol}")
            
            return None
            
        except Exception as e:
            logger.error(f"Phase 1 動態精準篩選執行失敗 {symbol}: {e}")
            return None
    
    def _is_dynamic_market_condition_optimal(self, market_data: dict, dynamic_thresholds: DynamicThresholds) -> bool:
        """🔥 Phase 1: 使用動態閾值檢查市場條件"""
        
        # 🌊 動態成交量檢查
        volume_ratio = market_data.get("volume_ratio", 0)
        min_volume_ratio = max(0.5, 0.8 - (dynamic_thresholds.confidence_threshold - 0.25) * 2)
        
        if volume_ratio < min_volume_ratio:
            logger.info(f"動態成交量檢查未通過: {volume_ratio:.2f} < {min_volume_ratio:.2f}")
            return False
        
        # 📊 動態波動率檢查（基於ATR）
        volatility = market_data.get("volatility", 0)
        min_volatility = 0.005 * (2.0 - dynamic_thresholds.confidence_threshold * 4)  # 動態最小波動率
        max_volatility = min(0.08, dynamic_thresholds.stop_loss_percent * 4)  # 基於動態止損的最大波動率
        
        if not (min_volatility <= volatility <= max_volatility):
            logger.info(f"動態波動率檢查未通過: {volatility:.4f} 不在 [{min_volatility:.4f}, {max_volatility:.4f}] 範圍")
            return False
        
        # 🔧 動態RSI檢查
        rsi = market_data.get("rsi", 50)
        if not (dynamic_thresholds.rsi_oversold <= rsi <= dynamic_thresholds.rsi_overbought):
            logger.info(f"動態RSI檢查未通過: {rsi:.1f} 不在 [{dynamic_thresholds.rsi_oversold}, {dynamic_thresholds.rsi_overbought}] 範圍")
            return False
        
        logger.info(f"✅ 動態市場條件檢查通過: 成交量比 {volume_ratio:.2f}, 波動率 {volatility:.4f}, RSI {rsi:.1f}")
        return True
    
    async def execute_dynamic_strategies(self, symbol: str, market_data: dict, dynamic_thresholds: DynamicThresholds) -> List[PrecisionSignal]:
        """🎯 Phase 1: 執行使用動態參數的策略"""
        
        strategies = [
            ('enhanced_momentum_dynamic', self.enhanced_momentum_strategy_dynamic),
            ('breakout_scalp_dynamic', self.enhanced_breakout_strategy_dynamic),
            ('reversal_scalp_dynamic', self.enhanced_reversal_strategy_dynamic),
            ('volume_scalp_dynamic', self.enhanced_volume_strategy_dynamic)
        ]
        
        valid_signals = []
        
        for strategy_name, strategy_func in strategies:
            try:
                signal = await strategy_func(symbol, market_data, dynamic_thresholds)
                
                # 🔥 使用動態信心度閾值（移除固定0.2限制）
                if signal and signal.confidence >= dynamic_thresholds.confidence_threshold:
                    # 應用策略權重
                    signal.confidence *= self.strategy_weights.get(strategy_name, 0.8)
                    valid_signals.append(signal)
                    logger.info(f"✅ 策略 {strategy_name} 通過動態閾值: {signal.confidence:.3f} >= {dynamic_thresholds.confidence_threshold:.3f}")
                elif signal:
                    logger.info(f"❌ 策略 {strategy_name} 未達動態閾值: {signal.confidence:.3f} < {dynamic_thresholds.confidence_threshold:.3f}")
                    
            except Exception as e:
                logger.error(f"動態策略 {strategy_name} 執行失敗: {e}")
        
        return valid_signals
    
    async def select_precision_signal_dynamic(self, signals: List[PrecisionSignal], market_data: dict, dynamic_thresholds: DynamicThresholds) -> Optional[PrecisionSignal]:
        """🎯 Phase 1: 使用動態閾值進行精準篩選"""
        
        if not signals:
            return None
        
        # 🔥 第一輪：動態信心度篩選（移除雙重過濾）
        qualified_signals = [
            s for s in signals 
            if s.confidence >= dynamic_thresholds.confidence_threshold
        ]
        
        if not qualified_signals:
            logger.info(f"無信號通過動態信心度閾值 {dynamic_thresholds.confidence_threshold:.3f}")
            return None
        
        logger.info(f"🎯 {len(qualified_signals)}/{len(signals)} 信號通過動態信心度篩選")
        
        # 第二輪：計算動態精準度評分
        for signal in qualified_signals:
            signal.precision_score = self._calculate_dynamic_precision_score(signal, market_data, dynamic_thresholds)
        
        # 選擇精準度最高的信號
        best_signal = max(qualified_signals, key=lambda s: s.precision_score)
        
        logger.info(f"🏆 最佳動態信號: {best_signal.strategy_name} "
                   f"(信心度: {best_signal.confidence:.3f}, 精準度: {best_signal.precision_score:.3f})")
        
        return best_signal
    
    def _calculate_dynamic_precision_score(self, signal: PrecisionSignal, market_data: dict, dynamic_thresholds: DynamicThresholds) -> float:
        """🔧 Phase 1: 計算動態精準度評分"""
        
        base_score = signal.confidence
        
        # 🌊 動態波動率加分
        volatility = market_data.get("volatility", 0.02)
        optimal_volatility = 0.025  # 最佳波動率2.5%
        volatility_score = 1.0 - abs(volatility - optimal_volatility) / optimal_volatility
        volatility_score = max(0.5, volatility_score)
        
        # 📊 動態成交量加分
        volume_ratio = market_data.get("volume_ratio", 1.0)
        volume_score = min(1.5, volume_ratio / 2.0)  # 成交量越高評分越高，上限1.5
        
        # 🎯 ATR適應性加分
        atr = market_data.get("atr", 0)
        current_price = market_data.get("current_price", 1)
        atr_percent = atr / current_price if current_price > 0 else 0.02
        
        # ATR與動態止損的匹配度
        atr_match_score = 1.0 - abs(atr_percent - dynamic_thresholds.stop_loss_percent) / dynamic_thresholds.stop_loss_percent
        atr_match_score = max(0.5, atr_match_score)
        
        # 🔥 RSI動態位置加分
        rsi = market_data.get("rsi", 50)
        if signal.signal_type == "BUY":
            # 做多信號：RSI越接近動態超賣線越好
            rsi_score = max(0.5, 1.0 - (rsi - dynamic_thresholds.rsi_oversold) / (50 - dynamic_thresholds.rsi_oversold))
        else:
            # 做空信號：RSI越接近動態超買線越好
            rsi_score = max(0.5, 1.0 - (dynamic_thresholds.rsi_overbought - rsi) / (dynamic_thresholds.rsi_overbought - 50))
        
        # 綜合評分
        precision_score = (
            base_score * 0.4 +           # 基礎信心度權重40%
            volatility_score * 0.25 +    # 波動率適應性25%
            volume_score * 0.15 +        # 成交量強度15%
            atr_match_score * 0.15 +     # ATR匹配度15%
            rsi_score * 0.05             # RSI動態位置5%
        )
        
        return min(1.0, precision_score)
    
    def _apply_dynamic_risk_management(self, signal: PrecisionSignal, market_state: MarketState) -> PrecisionSignal:
        """🎯 Phase 1 核心：應用ATR動態止損止盈"""
        
        entry_price = signal.entry_price
        
        # 🔧 ATR動態止損
        dynamic_stop_percent = market_state.atr_value / market_state.current_price
        
        # 應用流動性和波動率調整
        liquidity_multiplier = 2.0 / market_state.liquidity_score
        volatility_multiplier = 1.0 + (market_state.volatility_score - 1.0) * 0.5
        
        final_stop_percent = dynamic_stop_percent * liquidity_multiplier * volatility_multiplier
        final_stop_percent = max(0.01, min(0.05, final_stop_percent))  # 1%-5%範圍
        
        # 🎯 動態止盈（基於成交量和情緒）
        base_take_profit = 0.04  # 基礎4%
        volume_multiplier = 1.0 + (market_state.volume_strength - 1.0) * 0.3
        sentiment_multiplier = market_state.sentiment_multiplier
        
        final_take_profit_percent = base_take_profit * volume_multiplier * sentiment_multiplier
        final_take_profit_percent = max(0.02, min(0.08, final_take_profit_percent))  # 2%-8%範圍
        
        # 🔄 應用到信號
        if signal.signal_type in ["BUY", "LONG"]:
            signal.stop_loss = entry_price * (1 - final_stop_percent)
            signal.take_profit = entry_price * (1 + final_take_profit_percent)
        else:  # SELL, SHORT
            signal.stop_loss = entry_price * (1 + final_stop_percent)
            signal.take_profit = entry_price * (1 - final_take_profit_percent)
        
        logger.info(f"🎯 {signal.symbol} ATR動態風險管理: "
                   f"止損 {final_stop_percent:.3f}%, 止盈 {final_take_profit_percent:.3f}%, "
                   f"價格 ${entry_price:.6f} → 止損 ${signal.stop_loss:.6f}, 止盈 ${signal.take_profit:.6f}")
        
        return signal
    
    async def final_precision_check_dynamic(self, signal: PrecisionSignal, market_data: dict, dynamic_thresholds: DynamicThresholds) -> bool:
        """🔧 Phase 1: 動態最終驗證"""
        
        # 動態風險回報比檢查
        entry_price = signal.entry_price
        stop_loss = signal.stop_loss
        take_profit = signal.take_profit
        
        if signal.signal_type in ["BUY", "LONG"]:
            risk = abs(entry_price - stop_loss) / entry_price
            reward = abs(take_profit - entry_price) / entry_price
        else:
            risk = abs(stop_loss - entry_price) / entry_price
            reward = abs(entry_price - take_profit) / entry_price
        
        risk_reward_ratio = reward / risk if risk > 0 else 0
        
        # 🎯 動態風險回報比要求（基於市場條件調整）
        min_risk_reward = max(1.5, 3.0 - (dynamic_thresholds.confidence_threshold * 5))  # 信心度越高要求越低
        
        if risk_reward_ratio < min_risk_reward:
            logger.warning(f"動態風險回報比不足: {risk_reward_ratio:.2f} < {min_risk_reward:.2f}")
            return False
        
        # 精準度評分檢查
        if signal.precision_score < 0.4:  # 動態精準度最低要求
            logger.warning(f"動態精準度評分不足: {signal.precision_score:.3f} < 0.4")
            return False
        
        logger.info(f"✅ 動態最終驗證通過: 風險回報比 {risk_reward_ratio:.2f}, 精準度 {signal.precision_score:.3f}")
        return True
    
    def _integrate_consensus_results(self, strategy_results: List[Any], consensus_signal: ConsensusSignal) -> List[Any]:
        """集成智能共振分析結果"""
        try:
            consensus_boost = 0.2  # 共振增強係數
            
            for signal in strategy_results:
                if hasattr(signal, 'signal_type') and hasattr(signal, 'confidence'):
                    # 如果策略信號與共振信號一致，增強信心度
                    if signal.signal_type == consensus_signal.signal_type:
                        original_confidence = signal.confidence
                        signal.confidence = min(1.0, signal.confidence + (consensus_boost * consensus_signal.confidence))
                        logger.info(f"共振增強: {signal.strategy_name if hasattr(signal, 'strategy_name') else 'Unknown'} "
                                   f"信心度 {original_confidence:.3f} → {signal.confidence:.3f}")
                        
                        # 添加共振標記
                        if hasattr(signal, 'metadata'):
                            signal.metadata['consensus_enhanced'] = True
                            signal.metadata['consensus_score'] = consensus_signal.consensus_score
                            signal.metadata['contributing_indicators'] = consensus_signal.contributing_indicators
                    
                    # 如果信號方向衝突，降低信心度
                    elif signal.signal_type != consensus_signal.signal_type and consensus_signal.signal_type != 'NEUTRAL':
                        original_confidence = signal.confidence
                        signal.confidence = max(0.1, signal.confidence - (consensus_boost * consensus_signal.confidence))
                        logger.warning(f"共振衝突: {signal.strategy_name if hasattr(signal, 'strategy_name') else 'Unknown'} "
                                      f"信心度 {original_confidence:.3f} → {signal.confidence:.3f}")
            
            return strategy_results
            
        except Exception as e:
            logger.error(f"集成共振結果失敗: {e}")
            return strategy_results
    
    async def get_comprehensive_market_data(self, symbol: str) -> Dict[str, Any]:
        """獲取綜合市場數據"""
        
        try:
            # 獲取歷史數據
            df = await self.market_service.get_historical_data(
                symbol=symbol,
                timeframe="5m",
                limit=100,
                exchange='binance'
            )
            
            if df is None or df.empty or len(df) < 20:
                return {}
            
            # 計算市場指標
            closes = df['close'].tolist()
            volumes = df['volume'].tolist()
            highs = df['high'].tolist()
            lows = df['low'].tolist()
            
            # 當前價格
            current_price = closes[-1]
            
            # 計算波動率 (20期ATR)
            true_ranges = []
            for i in range(1, len(closes)):
                tr = max(
                    highs[i] - lows[i],
                    abs(highs[i] - closes[i-1]),
                    abs(lows[i] - closes[i-1])
                )
                true_ranges.append(tr)
            
            atr = np.mean(true_ranges[-20:]) if len(true_ranges) >= 20 else 0
            volatility = atr / current_price if current_price > 0 else 0
            
            # 計算成交量比率
            avg_volume = np.mean(volumes[-20:])
            current_volume = volumes[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            
            # 計算價差 (模擬)
            spread = (highs[-1] - lows[-1]) / current_price if current_price > 0 else 0
            
            # 計算趨勢強度
            sma_20 = np.mean(closes[-20:])
            trend_strength = abs(current_price - sma_20) / sma_20 if sma_20 > 0 else 0
            
            # 計算RSI (14期)
            rsi = 0.0
            if len(closes) >= 15:  # 需要至少15個數據點
                price_changes = [closes[i] - closes[i-1] for i in range(1, len(closes))]
                gains = [max(0, change) for change in price_changes]
                losses = [max(0, -change) for change in price_changes]
                
                if len(gains) >= 14:
                    avg_gain = np.mean(gains[-14:])
                    avg_loss = np.mean(losses[-14:])
                    
                    if avg_loss == 0:
                        rsi = 100.0
                    else:
                        rs = avg_gain / avg_loss
                        rsi = 100 - (100 / (1 + rs))
            
            return {
                "current_price": current_price,
                "volatility": volatility,
                "volume_ratio": volume_ratio,
                "spread": spread,
                "trend_strength": trend_strength,
                "rsi": rsi,
                "atr": atr,
                "avg_volume": avg_volume,
                "sma_20": sma_20,
                "closes": closes,
                "volumes": volumes,
                "highs": highs,
                "lows": lows
            }
            
        except Exception as e:
            logger.error(f"獲取市場數據失敗 {symbol}: {e}")
            return {}
    
    async def execute_all_strategies(self, symbol: str, market_data: dict) -> List[PrecisionSignal]:
        """執行所有策略並收集結果"""
        
        strategies = [
            ('enhanced_momentum', self.enhanced_momentum_strategy),
            ('breakout_scalp', self.enhanced_breakout_strategy),
            ('reversal_scalp', self.enhanced_reversal_strategy),
            ('volume_scalp', self.enhanced_volume_strategy)
        ]
        
        valid_signals = []
        
        for strategy_name, strategy_func in strategies:
            try:
                signal = await strategy_func(symbol, market_data)
                if signal and signal.confidence >= 0.2:  # 降低最低信心度要求 (從0.75降至0.2)
                    # 應用策略權重
                    signal.confidence *= self.strategy_weights.get(strategy_name, 0.8)
                    valid_signals.append(signal)
                    
            except Exception as e:
                logger.error(f"策略 {strategy_name} 執行失敗: {e}")
        
        return valid_signals
    
    async def enhanced_momentum_strategy_dynamic(self, symbol: str, market_data: dict, dynamic_thresholds: DynamicThresholds) -> Optional[PrecisionSignal]:
        """🔥 Phase 1: 增強動量策略（使用動態RSI閾值）"""
        
        try:
            closes = market_data.get("closes", [])
            if len(closes) < 20:
                return None
            
            # 🎯 使用動態RSI閾值
            rsi = market_data.get("rsi", 50)
            
            current_price = market_data.get("current_price", 0)
            if current_price <= 0:
                return None
            
            # 計算動量指標
            short_ma = np.mean(closes[-5:])  # 5期均線
            long_ma = np.mean(closes[-20:])  # 20期均線
            
            # 🔧 動態RSI信號判斷
            signal_type = None
            confidence = 0.0
            
            if rsi <= dynamic_thresholds.rsi_oversold and short_ma > long_ma * 0.995:
                signal_type = "BUY"
                # 🌊 動態信心度計算：RSI越低信心度越高
                rsi_confidence = (dynamic_thresholds.rsi_oversold - rsi) / dynamic_thresholds.rsi_oversold
                ma_confidence = (short_ma - long_ma) / long_ma * 100
                confidence = min(1.0, 0.5 + rsi_confidence * 0.3 + ma_confidence * 0.2)
                
            elif rsi >= dynamic_thresholds.rsi_overbought and short_ma < long_ma * 1.005:
                signal_type = "SELL"
                # 🌊 動態信心度計算：RSI越高信心度越高
                rsi_confidence = (rsi - dynamic_thresholds.rsi_overbought) / (100 - dynamic_thresholds.rsi_overbought)
                ma_confidence = (long_ma - short_ma) / long_ma * 100
                confidence = min(1.0, 0.5 + rsi_confidence * 0.3 + ma_confidence * 0.2)
            
            if not signal_type or confidence < 0.1:
                return None
            
            # 📊 成交量確認
            volume_ratio = market_data.get("volume_ratio", 1.0)
            if volume_ratio > 1.2:  # 成交量放大
                confidence *= 1.1
            
            # 🎯 計算進場價格（當前價格）
            entry_price = current_price
            
            # 🔧 暫時設置基礎止損止盈（稍後會被動態風險管理覆蓋）
            if signal_type == "BUY":
                stop_loss = entry_price * 0.98
                take_profit = entry_price * 1.04
            else:
                stop_loss = entry_price * 1.02
                take_profit = entry_price * 0.96
            
            signal = PrecisionSignal(
                symbol=symbol,
                signal_type=signal_type,
                strategy_name="Enhanced Momentum Dynamic",
                confidence=confidence,
                precision_score=0.0,  # 將在後續計算
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                timeframe="5m",
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=2),
                market_condition_score=0.8,
                indicator_consistency=confidence,
                timing_score=0.7,
                risk_adjustment=1.0,
                market_data=market_data,
                technical_indicators={"rsi": rsi, "short_ma": short_ma, "long_ma": long_ma}
            )
            
            logger.info(f"🔥 動態動量策略: {symbol} {signal_type} "
                       f"(RSI: {rsi:.1f}, 動態閾值: {dynamic_thresholds.rsi_oversold}/{dynamic_thresholds.rsi_overbought}, "
                       f"信心度: {confidence:.3f})")
            
            return signal
            
        except Exception as e:
            logger.error(f"動態動量策略失敗 {symbol}: {e}")
            return None
    
    async def enhanced_breakout_strategy_dynamic(self, symbol: str, market_data: dict, dynamic_thresholds: DynamicThresholds) -> Optional[PrecisionSignal]:
        """🚀 Phase 1: 增強突破策略（使用動態布林帶）"""
        
        try:
            closes = market_data.get("closes", [])
            highs = market_data.get("highs", [])
            lows = market_data.get("lows", [])
            
            if len(closes) < 20:
                return None
            
            current_price = market_data.get("current_price", 0)
            if current_price <= 0:
                return None
            
            # 🌊 動態布林帶計算
            sma_20 = np.mean(closes[-20:])
            std_20 = np.std(closes[-20:])
            
            bb_upper = sma_20 + (std_20 * dynamic_thresholds.bollinger_multiplier)
            bb_lower = sma_20 - (std_20 * dynamic_thresholds.bollinger_multiplier)
            
            # 計算布林帶位置
            bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) if bb_upper != bb_lower else 0.5
            
            # 📊 成交量確認
            volume_ratio = market_data.get("volume_ratio", 1.0)
            volatility = market_data.get("volatility", 0.02)
            
            signal_type = None
            confidence = 0.0
            
            # 🚀 上軌突破（做多）
            if current_price > bb_upper and volume_ratio > 1.5:
                signal_type = "BUY"
                # 突破幅度越大，成交量越大，信心度越高
                breakout_strength = (current_price - bb_upper) / bb_upper
                volume_strength = min(2.0, volume_ratio / 1.5)
                confidence = min(1.0, 0.6 + breakout_strength * 100 + (volume_strength - 1.0) * 0.2)
                
            # 🔻 下軌突破（做空）
            elif current_price < bb_lower and volume_ratio > 1.5:
                signal_type = "SELL"
                # 跌破幅度越大，成交量越大，信心度越高
                breakout_strength = (bb_lower - current_price) / bb_lower
                volume_strength = min(2.0, volume_ratio / 1.5)
                confidence = min(1.0, 0.6 + breakout_strength * 100 + (volume_strength - 1.0) * 0.2)
            
            if not signal_type or confidence < 0.1:
                return None
            
            # 🎯 波動率調整
            if volatility > 0.04:  # 高波動環境
                confidence *= 1.15  # 提高信心度
            elif volatility < 0.01:  # 低波動環境
                confidence *= 0.9   # 降低信心度
            
            entry_price = current_price
            
            # 暫時設置基礎止損止盈
            if signal_type == "BUY":
                stop_loss = max(bb_lower, entry_price * 0.97)  # 止損設在布林帶下軌或3%
                take_profit = entry_price * 1.05
            else:
                stop_loss = min(bb_upper, entry_price * 1.03)  # 止損設在布林帶上軌或3%
                take_profit = entry_price * 0.95
            
            signal = PrecisionSignal(
                symbol=symbol,
                signal_type=signal_type,
                strategy_name="Enhanced Breakout Dynamic",
                confidence=confidence,
                precision_score=0.0,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                timeframe="5m",
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=1),
                market_condition_score=0.9,
                indicator_consistency=confidence,
                timing_score=0.8,
                risk_adjustment=1.0,
                market_data=market_data,
                technical_indicators={
                    "bb_upper": bb_upper, "bb_lower": bb_lower, "bb_position": bb_position,
                    "bollinger_multiplier": dynamic_thresholds.bollinger_multiplier
                }
            )
            
            logger.info(f"🚀 動態突破策略: {symbol} {signal_type} "
                       f"(價格: ${current_price:.6f}, BB: ${bb_lower:.6f}-${bb_upper:.6f}, "
                       f"倍數: {dynamic_thresholds.bollinger_multiplier:.2f}, 信心度: {confidence:.3f})")
            
            return signal
            
        except Exception as e:
            logger.error(f"動態突破策略失敗 {symbol}: {e}")
            return None
    
    async def enhanced_reversal_strategy_dynamic(self, symbol: str, market_data: dict, dynamic_thresholds: DynamicThresholds) -> Optional[PrecisionSignal]:
        """🔄 Phase 1: 增強反轉策略（使用動態MACD參數）"""
        
        try:
            closes = market_data.get("closes", [])
            if len(closes) < 30:
                return None
            
            current_price = market_data.get("current_price", 0)
            if current_price <= 0:
                return None
            
            # 🎯 動態MACD計算
            fast_period = dynamic_thresholds.macd_fast
            slow_period = dynamic_thresholds.macd_slow
            signal_period = 9
            
            # 計算EMA
            def calculate_ema(data, period):
                alpha = 2 / (period + 1)
                ema = [data[0]]
                for price in data[1:]:
                    ema.append(alpha * price + (1 - alpha) * ema[-1])
                return ema
            
            ema_fast = calculate_ema(closes, fast_period)
            ema_slow = calculate_ema(closes, slow_period)
            
            if len(ema_fast) < 2 or len(ema_slow) < 2:
                return None
            
            # MACD線和信號線
            macd_line = [fast - slow for fast, slow in zip(ema_fast, ema_slow)]
            macd_signal = calculate_ema(macd_line, signal_period)
            
            if len(macd_line) < 2 or len(macd_signal) < 2:
                return None
            
            # 當前MACD值
            current_macd = macd_line[-1]
            current_signal = macd_signal[-1]
            prev_macd = macd_line[-2]
            prev_signal = macd_signal[-2]
            
            # RSI反轉確認
            rsi = market_data.get("rsi", 50)
            
            signal_type = None
            confidence = 0.0
            
            # 🔄 金叉反轉（做多）
            if (prev_macd <= prev_signal and current_macd > current_signal and 
                rsi < dynamic_thresholds.rsi_oversold + 10):  # RSI在超賣區域附近
                signal_type = "BUY"
                
                # 🌊 動態信心度：MACD差值越大，RSI越低，信心度越高
                macd_strength = abs(current_macd - current_signal) / abs(ema_slow[-1] - ema_fast[-1]) if abs(ema_slow[-1] - ema_fast[-1]) > 0 else 0
                rsi_strength = max(0, (dynamic_thresholds.rsi_oversold + 10 - rsi) / 20)
                confidence = min(1.0, 0.5 + macd_strength * 0.3 + rsi_strength * 0.2)
                
            # 🔻 死叉反轉（做空）
            elif (prev_macd >= prev_signal and current_macd < current_signal and 
                  rsi > dynamic_thresholds.rsi_overbought - 10):  # RSI在超買區域附近
                signal_type = "SELL"
                
                # 🌊 動態信心度：MACD差值越大，RSI越高，信心度越高
                macd_strength = abs(current_macd - current_signal) / abs(ema_slow[-1] - ema_fast[-1]) if abs(ema_slow[-1] - ema_fast[-1]) > 0 else 0
                rsi_strength = max(0, (rsi - (dynamic_thresholds.rsi_overbought - 10)) / 20)
                confidence = min(1.0, 0.5 + macd_strength * 0.3 + rsi_strength * 0.2)
            
            if not signal_type or confidence < 0.1:
                return None
            
            # 📊 成交量確認
            volume_ratio = market_data.get("volume_ratio", 1.0)
            if volume_ratio > 1.3:
                confidence *= 1.1
            
            entry_price = current_price
            
            # 暫時設置基礎止損止盈
            if signal_type == "BUY":
                stop_loss = entry_price * 0.975
                take_profit = entry_price * 1.035
            else:
                stop_loss = entry_price * 1.025
                take_profit = entry_price * 0.965
            
            signal = PrecisionSignal(
                symbol=symbol,
                signal_type=signal_type,
                strategy_name="Enhanced Reversal Dynamic",
                confidence=confidence,
                precision_score=0.0,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                timeframe="5m",
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=1.5),
                market_condition_score=0.75,
                indicator_consistency=confidence,
                timing_score=0.8,
                risk_adjustment=1.0,
                market_data=market_data,
                technical_indicators={
                    "macd": current_macd, "macd_signal": current_signal,
                    "macd_fast": fast_period, "macd_slow": slow_period, "rsi": rsi
                }
            )
            
            logger.info(f"🔄 動態反轉策略: {symbol} {signal_type} "
                       f"(MACD: {current_macd:.6f}, 信號: {current_signal:.6f}, "
                       f"參數: {fast_period}/{slow_period}, 信心度: {confidence:.3f})")
            
            return signal
            
        except Exception as e:
            logger.error(f"動態反轉策略失敗 {symbol}: {e}")
            return None
    
    async def enhanced_volume_strategy_dynamic(self, symbol: str, market_data: dict, dynamic_thresholds: DynamicThresholds) -> Optional[PrecisionSignal]:
        """📊 Phase 1: 增強成交量策略（動態成交量閾值）"""
        
        try:
            closes = market_data.get("closes", [])
            volumes = market_data.get("volumes", [])
            
            if len(closes) < 20 or len(volumes) < 20:
                return None
            
            current_price = market_data.get("current_price", 0)
            if current_price <= 0:
                return None
            
            # 📊 成交量分析
            current_volume = volumes[-1]
            avg_volume_20 = np.mean(volumes[-20:])
            volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 1.0
            
            # 🎯 動態成交量閾值（基於動態信心度調整）
            base_volume_threshold = 2.0
            dynamic_volume_threshold = base_volume_threshold * (2.0 - dynamic_thresholds.confidence_threshold)
            
            if volume_ratio < dynamic_volume_threshold:
                return None
            
            # 價格趨勢確認
            price_change = (closes[-1] - closes[-5]) / closes[-5] if closes[-5] > 0 else 0
            short_trend = (closes[-1] - closes[-10]) / closes[-10] if closes[-10] > 0 else 0
            
            # 🔍 成交量價格背離檢查
            volume_trend = (current_volume - np.mean(volumes[-10:-5])) / np.mean(volumes[-10:-5]) if np.mean(volumes[-10:-5]) > 0 else 0
            
            signal_type = None
            confidence = 0.0
            
            # 📈 成交量突增配合價格上漲
            if volume_ratio >= dynamic_volume_threshold and price_change > 0.005:  # 價格上漲0.5%以上
                signal_type = "BUY"
                
                # 🌊 動態信心度：成交量倍數越高，價格漲幅越大，信心度越高
                volume_strength = min(3.0, volume_ratio / dynamic_volume_threshold)
                price_strength = min(2.0, price_change * 100)
                trend_strength = max(0.5, min(2.0, 1.0 + short_trend * 50))
                
                confidence = min(1.0, 0.4 + 
                               volume_strength * 0.2 + 
                               price_strength * 0.2 + 
                               (trend_strength - 0.5) * 0.2)
            
            # 📉 成交量突增配合價格下跌
            elif volume_ratio >= dynamic_volume_threshold and price_change < -0.005:  # 價格下跌0.5%以上
                signal_type = "SELL"
                
                # 🌊 動態信心度：成交量倍數越高，價格跌幅越大，信心度越高
                volume_strength = min(3.0, volume_ratio / dynamic_volume_threshold)
                price_strength = min(2.0, abs(price_change) * 100)
                trend_strength = max(0.5, min(2.0, 1.0 - short_trend * 50))
                
                confidence = min(1.0, 0.4 + 
                               volume_strength * 0.2 + 
                               price_strength * 0.2 + 
                               (trend_strength - 0.5) * 0.2)
            
            if not signal_type or confidence < 0.1:
                return None
            
            # 🎯 RSI確認（使用動態閾值）
            rsi = market_data.get("rsi", 50)
            if signal_type == "BUY" and rsi > dynamic_thresholds.rsi_overbought:
                confidence *= 0.8  # 降低信心度
            elif signal_type == "SELL" and rsi < dynamic_thresholds.rsi_oversold:
                confidence *= 0.8  # 降低信心度
            
            entry_price = current_price
            
            # 暫時設置基礎止損止盈
            if signal_type == "BUY":
                stop_loss = entry_price * 0.98
                take_profit = entry_price * 1.04
            else:
                stop_loss = entry_price * 1.02
                take_profit = entry_price * 0.96
            
            signal = PrecisionSignal(
                symbol=symbol,
                signal_type=signal_type,
                strategy_name="Enhanced Volume Dynamic",
                confidence=confidence,
                precision_score=0.0,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                timeframe="5m",
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=1),
                market_condition_score=0.85,
                indicator_consistency=confidence,
                timing_score=0.9,
                risk_adjustment=1.0,
                market_data=market_data,
                technical_indicators={
                    "volume_ratio": volume_ratio, "dynamic_threshold": dynamic_volume_threshold,
                    "price_change": price_change, "volume_trend": volume_trend
                }
            )
            
            logger.info(f"📊 動態成交量策略: {symbol} {signal_type} "
                       f"(成交量比: {volume_ratio:.2f}, 動態閾值: {dynamic_volume_threshold:.2f}, "
                       f"價格變化: {price_change:.4f}, 信心度: {confidence:.3f})")
            
            return signal
            
        except Exception as e:
            logger.error(f"動態成交量策略失敗 {symbol}: {e}")
            return None
            price_changes = [closes[i] - closes[i-1] for i in range(1, len(closes))]
            gains = [max(0, change) for change in price_changes]
            losses = [max(0, -change) for change in price_changes]
            
            if len(gains) < 14:
                return None
            
            avg_gain = sum(gains[-14:]) / 14
            avg_loss = sum(losses[-14:]) / 14
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            # 計算MACD
            ema_12 = self._calculate_ema(closes, 12)
            ema_26 = self._calculate_ema(closes, 26)
            macd_line = ema_12 - ema_26
            
            # 動量評分
            momentum_score = 0.0
            signal_type = None
            
            if rsi > 75 and macd_line < 0:  # 超買且MACD看空
                signal_type = "SHORT"
                momentum_score = (rsi - 75) / 25  # 0-1標準化
            elif rsi < 25 and macd_line > 0:  # 超賣且MACD看多
                signal_type = "LONG"
                momentum_score = (25 - rsi) / 25  # 0-1標準化
            
            if not signal_type:
                return None
            
            # 計算入場價格和止損止盈
            current_price = market_data["current_price"]
            atr = market_data.get("atr", current_price * 0.02)
            
            if signal_type == "LONG":
                entry_price = current_price
                stop_loss = current_price - (atr * 1.5)
                take_profit = current_price + (atr * 3.0)
            else:
                entry_price = current_price
                stop_loss = current_price + (atr * 1.5)
                take_profit = current_price - (atr * 3.0)
            
            # 基礎信心度
            base_confidence = momentum_score * 0.8 + (market_data.get("trend_strength", 0) * 0.2)
            
            signal = PrecisionSignal(
                symbol=symbol,
                signal_type=signal_type,
                strategy_name="enhanced_momentum",
                confidence=float(base_confidence),
                precision_score=0.0,  # 稍後計算
                entry_price=float(entry_price),
                stop_loss=float(stop_loss),
                take_profit=float(take_profit),
                timeframe="5m",
                created_at=get_taiwan_now_naive(),
                expires_at=get_taiwan_now_naive() + timedelta(hours=4),
                market_condition_score=0.0,  # 稍後計算
                indicator_consistency=0.0,   # 稍後計算
                timing_score=0.0,           # 稍後計算
                risk_adjustment=0.0,        # 稍後計算
                market_data=market_data,
                technical_indicators={"rsi": rsi, "macd": macd_line}
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"增強動量策略執行失敗: {e}")
            return None
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """計算指數移動平均"""
        if len(prices) < period:
            return np.mean(prices)
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    async def enhanced_breakout_strategy(self, symbol: str, market_data: dict) -> Optional[PrecisionSignal]:
        """增強突破策略"""
        
        try:
            closes = market_data.get("closes", [])
            highs = market_data.get("highs", [])
            lows = market_data.get("lows", [])
            
            if len(closes) < 20:
                return None
            
            # 計算布林帶
            sma_20 = np.mean(closes[-20:])
            std_20 = np.std(closes[-20:])
            upper_band = sma_20 + (std_20 * 2)
            lower_band = sma_20 - (std_20 * 2)
            
            current_price = closes[-1]
            
            # 檢查突破
            signal_type = None
            breakout_strength = 0.0
            
            if current_price > upper_band:
                signal_type = "LONG"
                breakout_strength = (current_price - upper_band) / upper_band
            elif current_price < lower_band:
                signal_type = "SHORT"
                breakout_strength = (lower_band - current_price) / lower_band
            
            if not signal_type or breakout_strength < 0.005:  # 至少0.5%的突破
                return None
            
            # 計算止損止盈
            atr = market_data.get("atr", current_price * 0.02)
            
            if signal_type == "LONG":
                entry_price = current_price
                stop_loss = lower_band
                take_profit = current_price + (atr * 4.0)
            else:
                entry_price = current_price
                stop_loss = upper_band
                take_profit = current_price - (atr * 4.0)
            
            # 信心度計算
            volume_confirmation = min(market_data.get("volume_ratio", 1), 3) / 3
            confidence = (breakout_strength * 0.6) + (volume_confirmation * 0.4)
            
            signal = PrecisionSignal(
                symbol=symbol,
                signal_type=signal_type,
                strategy_name="breakout_scalp",
                confidence=float(confidence),
                precision_score=0.0,
                entry_price=float(entry_price),
                stop_loss=float(stop_loss),
                take_profit=float(take_profit),
                timeframe="5m",
                created_at=get_taiwan_now_naive(),
                expires_at=get_taiwan_now_naive() + timedelta(hours=4),
                market_condition_score=0.0,
                indicator_consistency=0.0,
                timing_score=0.0,
                risk_adjustment=0.0,
                market_data=market_data,
                technical_indicators={"upper_band": upper_band, "lower_band": lower_band, "breakout_strength": breakout_strength}
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"增強突破策略執行失敗: {e}")
            return None
    
    async def enhanced_reversal_strategy(self, symbol: str, market_data: dict) -> Optional[PrecisionSignal]:
        """增強反轉策略"""
        
        try:
            closes = market_data.get("closes", [])
            if len(closes) < 14:
                return None
            
            # 計算Stochastic RSI
            rsi_values = []
            for i in range(14, len(closes)):
                period_closes = closes[i-13:i+1]
                price_changes = [period_closes[j] - period_closes[j-1] for j in range(1, len(period_closes))]
                gains = [max(0, change) for change in price_changes]
                losses = [max(0, -change) for change in price_changes]
                
                avg_gain = sum(gains) / len(gains) if gains else 0
                avg_loss = sum(losses) / len(losses) if losses else 0
                
                if avg_loss == 0:
                    rsi = 100
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                
                rsi_values.append(rsi)
            
            if len(rsi_values) < 14:
                return None
            
            # 計算Stochastic RSI
            rsi_high = max(rsi_values[-14:])
            rsi_low = min(rsi_values[-14:])
            current_rsi = rsi_values[-1]
            
            if rsi_high == rsi_low:
                stoch_rsi = 50
            else:
                stoch_rsi = (current_rsi - rsi_low) / (rsi_high - rsi_low) * 100
            
            # 反轉信號判斷
            signal_type = None
            reversal_strength = 0.0
            
            if stoch_rsi > 80:  # 超買反轉
                signal_type = "SHORT"
                reversal_strength = (stoch_rsi - 80) / 20
            elif stoch_rsi < 20:  # 超賣反轉
                signal_type = "LONG"
                reversal_strength = (20 - stoch_rsi) / 20
            
            if not signal_type:
                return None
            
            # 計算止損止盈
            current_price = market_data["current_price"]
            atr = market_data.get("atr", current_price * 0.015)
            
            if signal_type == "LONG":
                entry_price = current_price
                stop_loss = current_price - (atr * 2.0)
                take_profit = current_price + (atr * 2.5)
            else:
                entry_price = current_price
                stop_loss = current_price + (atr * 2.0)
                take_profit = current_price - (atr * 2.5)
            
            confidence = reversal_strength * 0.7  # 反轉策略相對保守
            
            signal = PrecisionSignal(
                symbol=symbol,
                signal_type=signal_type,
                strategy_name="reversal_scalp",
                confidence=float(confidence),
                precision_score=0.0,
                entry_price=float(entry_price),
                stop_loss=float(stop_loss),
                take_profit=float(take_profit),
                timeframe="5m",
                created_at=get_taiwan_now_naive(),
                expires_at=get_taiwan_now_naive() + timedelta(hours=4),
                market_condition_score=0.0,
                indicator_consistency=0.0,
                timing_score=0.0,
                risk_adjustment=0.0,
                market_data=market_data,
                technical_indicators={"stoch_rsi": stoch_rsi, "current_rsi": current_rsi}
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"增強反轉策略執行失敗: {e}")
            return None
    
    async def enhanced_volume_strategy(self, symbol: str, market_data: dict) -> Optional[PrecisionSignal]:
        """增強成交量策略"""
        
        try:
            volumes = market_data.get("volumes", [])
            closes = market_data.get("closes", [])
            
            if len(volumes) < 20 or len(closes) < 20:
                return None
            
            # 計算成交量指標
            avg_volume = np.mean(volumes[-20:])
            current_volume = volumes[-1]
            volume_spike = current_volume / avg_volume if avg_volume > 0 else 0
            
            # 計算價格變化
            price_change = (closes[-1] - closes[-2]) / closes[-2] if closes[-2] > 0 else 0
            
            # 成交量確認信號
            signal_type = None
            volume_strength = 0.0
            
            if volume_spike > 2.0:  # 成交量激增
                if price_change > 0.002:  # 價格上漲
                    signal_type = "LONG"
                    volume_strength = min(volume_spike / 5, 1.0)
                elif price_change < -0.002:  # 價格下跌
                    signal_type = "SHORT"
                    volume_strength = min(volume_spike / 5, 1.0)
            
            if not signal_type:
                return None
            
            # 計算止損止盈
            current_price = market_data["current_price"]
            atr = market_data.get("atr", current_price * 0.02)
            
            if signal_type == "LONG":
                entry_price = current_price
                stop_loss = current_price - (atr * 1.0)
                take_profit = current_price + (atr * 2.0)
            else:
                entry_price = current_price
                stop_loss = current_price + (atr * 1.0)
                take_profit = current_price - (atr * 2.0)
            
            confidence = volume_strength * abs(price_change) * 50  # 成交量 × 價格變化幅度
            
            signal = PrecisionSignal(
                symbol=symbol,
                signal_type=signal_type,
                strategy_name="volume_scalp",
                confidence=float(confidence),
                precision_score=0.0,
                entry_price=float(entry_price),
                stop_loss=float(stop_loss),
                take_profit=float(take_profit),
                timeframe="5m",
                created_at=get_taiwan_now_naive(),
                expires_at=get_taiwan_now_naive() + timedelta(hours=4),
                market_condition_score=0.0,
                indicator_consistency=0.0,
                timing_score=0.0,
                risk_adjustment=0.0,
                market_data=market_data,
                technical_indicators={"volume_spike": volume_spike, "price_change": price_change}
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"增強成交量策略執行失敗: {e}")
            return None
    
    async def select_precision_signal(self, signals: List[PrecisionSignal], 
                                    market_data: dict) -> Optional[PrecisionSignal]:
        """從信號中選擇最精準的一個"""
        
        if not signals:
            return None
        
        # 計算精準度評分
        for signal in signals:
            precision_score = await self.calculate_precision_score(signal, market_data)
            signal.precision_score = precision_score
        
        # 按精準度排序
        signals.sort(key=lambda x: x.precision_score, reverse=True)
        
        # 只有當最高分超過閾值才返回
        best_signal = signals[0]
        if best_signal.precision_score >= 0.4:  # 精準度閾值 (從0.8降至0.4)
            logger.info(f"精準信號評分: {best_signal.strategy_name} = {best_signal.precision_score:.3f}")
            return best_signal
        
        logger.info(f"所有信號精準度不足 (最高: {best_signal.precision_score:.3f})")
        return None
    
    async def calculate_precision_score(self, signal: PrecisionSignal, 
                                      market_data: dict) -> float:
        """計算信號精準度評分"""
        
        score = 0.0
        
        # 1. 基礎信心度 (40%)
        score += signal.confidence * 0.4
        
        # 2. 市場條件匹配度 (25%)
        market_match = self.calculate_market_match_score(signal, market_data)
        signal.market_condition_score = market_match
        score += market_match * 0.25
        
        # 3. 技術指標一致性 (20%)
        indicator_consistency = await self.check_indicator_consistency(signal, market_data)
        signal.indicator_consistency = indicator_consistency
        score += indicator_consistency * 0.2
        
        # 4. 時機精準度 (10%)
        timing_score = self.calculate_timing_score(signal, market_data)
        signal.timing_score = timing_score
        score += timing_score * 0.1
        
        # 5. 風險調整 (5%)
        risk_adjustment = self.calculate_risk_adjustment(signal, market_data)
        signal.risk_adjustment = risk_adjustment
        score += risk_adjustment * 0.05
        
        return min(score, 1.0)
    
    def calculate_market_match_score(self, signal: PrecisionSignal, market_data: dict) -> float:
        """計算市場條件匹配度"""
        
        match_score = 0.0
        
        # 波動率匹配
        volatility = market_data.get("volatility", 0)
        optimal_vol = self.market_config.precision_thresholds["volatility_range"]["optimal"]
        vol_deviation = abs(volatility - optimal_vol) / optimal_vol if optimal_vol > 0 else 1
        vol_score = max(0, 1.0 - vol_deviation)
        match_score += vol_score * 0.4
        
        # 成交量匹配
        volume_ratio = market_data.get("volume_ratio", 0)
        min_volume = self.market_config.precision_thresholds["min_volume_ratio"]
        vol_score = min(volume_ratio / min_volume, 2.0) / 2.0 if min_volume > 0 else 0
        match_score += vol_score * 0.3
        
        # 趨勢強度匹配
        trend_strength = market_data.get("trend_strength", 0)
        min_trend = self.market_config.precision_thresholds["trend_strength_min"]
        trend_score = max(0, min(trend_strength / min_trend, 1.0)) if min_trend > 0 else 0
        match_score += trend_score * 0.3
        
        return match_score
    
    async def check_indicator_consistency(self, signal: PrecisionSignal, market_data: dict) -> float:
        """檢查技術指標一致性"""
        
        try:
            consistency_score = 0.0
            
            # 獲取技術指標
            tech_indicators = signal.technical_indicators
            
            # RSI一致性檢查
            if "rsi" in tech_indicators:
                rsi = tech_indicators["rsi"]
                if signal.signal_type == "LONG" and rsi < 30:
                    consistency_score += 0.4
                elif signal.signal_type == "SHORT" and rsi > 70:
                    consistency_score += 0.4
            
            # MACD一致性檢查
            if "macd" in tech_indicators:
                macd = tech_indicators["macd"]
                if signal.signal_type == "LONG" and macd > 0:
                    consistency_score += 0.3
                elif signal.signal_type == "SHORT" and macd < 0:
                    consistency_score += 0.3
            
            # 成交量一致性檢查
            volume_ratio = market_data.get("volume_ratio", 1)
            if volume_ratio > 1.5:  # 成交量放大
                consistency_score += 0.3
            
            return min(consistency_score, 1.0)
            
        except Exception as e:
            logger.error(f"指標一致性檢查失敗: {e}")
            return 0.0
    
    def calculate_timing_score(self, signal: PrecisionSignal, market_data: dict) -> float:
        """計算時機精準度"""
        
        current_hour = datetime.now().hour
        optimal_hours = self.market_config.precision_thresholds["time_precision"]["optimal_hours"]
        
        # 最佳時間段評分
        if current_hour in optimal_hours:
            timing_score = 1.0
        else:
            # 次佳時間段
            secondary_hours = [8, 11, 13, 16, 19, 22]
            if current_hour in secondary_hours:
                timing_score = 0.7
            else:
                timing_score = 0.3
        
        return timing_score
    
    def calculate_risk_adjustment(self, signal: PrecisionSignal, market_data: dict) -> float:
        """計算風險調整評分"""
        
        try:
            # 計算風險回報比
            entry_price = signal.entry_price
            stop_loss = signal.stop_loss
            take_profit = signal.take_profit
            
            risk = abs(entry_price - stop_loss) / entry_price
            reward = abs(take_profit - entry_price) / entry_price
            
            if risk <= 0:
                return 0.0
            
            risk_reward_ratio = reward / risk
            
            # 風險回報比評分 (1:2以上較好)
            if risk_reward_ratio >= 2.0:
                rr_score = 1.0
            elif risk_reward_ratio >= 1.5:
                rr_score = 0.8
            elif risk_reward_ratio >= 1.0:
                rr_score = 0.6
            else:
                rr_score = 0.3
            
            # 波動率風險調整
            volatility = market_data.get("volatility", 0.02)
            if volatility > 0.04:  # 高波動率
                vol_adjustment = 0.7
            elif volatility < 0.01:  # 低波動率
                vol_adjustment = 0.8
            else:  # 適中波動率
                vol_adjustment = 1.0
            
            return rr_score * vol_adjustment
            
        except Exception as e:
            logger.error(f"風險調整計算失敗: {e}")
            return 0.5
    
    async def final_precision_check(self, signal: PrecisionSignal, market_data: dict) -> bool:
        """最終精準度檢查"""
        
        try:
            # 1. 檢查信號與當前市場價格的偏差
            current_price = market_data.get("current_price", 0)
            if current_price <= 0:
                return False
            
            price_deviation = abs(current_price - signal.entry_price) / signal.entry_price
            if price_deviation > 0.001:  # 0.1% 價格偏差容忍度
                logger.warning(f"信號價格偏差過大: {price_deviation:.4f}")
                return False
            
            # 2. 檢查風險回報比
            risk = abs(signal.entry_price - signal.stop_loss) / signal.entry_price
            reward = abs(signal.take_profit - signal.entry_price) / signal.entry_price
            
            if risk <= 0 or reward / risk < 1.0:  # 至少1:1的風險回報比
                logger.warning(f"風險回報比不佳: {reward/risk if risk > 0 else 0:.2f}")
                return False
            
            # 3. 檢查市場流動性 (通過成交量)
            volume_ratio = market_data.get("volume_ratio", 0)
            if volume_ratio < 0.5:  # 成交量過低
                logger.warning(f"市場流動性不足: {volume_ratio:.2f}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"最終精準度檢查失敗: {e}")
            return False

# 全局精準篩選器實例
precision_filter = PrecisionSignalFilter()
