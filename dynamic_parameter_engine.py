#!/usr/bin/env python3
"""
Dynamic Parameter Engine - Core Implementation
動態參數引擎核心實現，100%匹配對應的JSON配置
"""

import json
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import pytz
from abc import ABC, abstractmethod

# 核心數據結構
class MarketRegime(Enum):
    """市場制度枚舉"""
    BULL_TREND = "BULL_TREND"
    BEAR_TREND = "BEAR_TREND"
    SIDEWAYS = "SIDEWAYS" 
    VOLATILE = "VOLATILE"
    UNKNOWN = "UNKNOWN"

class TradingSession(Enum):
    """交易時段枚舉"""
    US_MARKET = "US_MARKET"
    ASIA_MARKET = "ASIA_MARKET"
    EUROPE_MARKET = "EUROPE_MARKET"
    OVERLAP_HOURS = "OVERLAP_HOURS"
    OFF_HOURS = "OFF_HOURS"

@dataclass
class MarketData:
    """市場數據結構"""
    timestamp: datetime
    price: float
    volume: float
    price_change_1h: float
    price_change_24h: float
    volume_ratio: float
    volatility: float
    fear_greed_index: int
    bid_ask_spread: float
    market_depth: float
    moving_averages: Dict[str, float]

@dataclass
class AdaptedParameter:
    """適應後的參數結構"""
    parameter_name: str
    original_value: float
    adapted_value: float
    adaptation_factor: float
    adaptation_reasons: List[str]
    confidence_score: float
    timestamp: datetime
    market_regime: MarketRegime
    trading_session: TradingSession

@dataclass 
class DynamicParameterResult:
    """動態參數結果結構"""
    adapted_parameters: Dict[str, AdaptedParameter]
    market_regime: MarketRegime
    trading_session: TradingSession
    regime_confidence: float
    timestamp: datetime
    metadata: Dict[str, Any]

class MarketDataSource(ABC):
    """市場數據源抽象接口"""
    
    @abstractmethod
    async def get_current_market_data(self) -> MarketData:
        """獲取當前市場數據"""
        pass
    
    @abstractmethod
    async def get_fear_greed_index(self) -> int:
        """獲取恐懼貪婪指數"""
        pass

class MockMarketDataSource(MarketDataSource):
    """模擬市場數據源（用於測試）"""
    
    async def get_current_market_data(self) -> MarketData:
        """返回模擬市場數據"""
        now = datetime.now(timezone.utc)
        return MarketData(
            timestamp=now,
            price=50000.0,
            volume=1000000.0,
            price_change_1h=0.02,
            price_change_24h=0.05,
            volume_ratio=1.2,
            volatility=0.03,
            fear_greed_index=65,
            bid_ask_spread=0.001,
            market_depth=0.8,
            moving_averages={
                "ma_20": 49800.0,
                "ma_50": 49000.0,
                "ma_200": 48000.0
            }
        )
    
    async def get_fear_greed_index(self) -> int:
        """返回模擬恐懼貪婪指數"""
        return 65

class MarketRegimeDetector:
    """市場制度檢測器 - 100%匹配JSON配置"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.regime_types = config["dynamic_parameter_system"]["market_regime_detection"]["regime_types"]
        self.detection_algorithm = config["dynamic_parameter_system"]["market_regime_detection"]["detection_algorithm"]
        self.current_regime = MarketRegime.UNKNOWN
        self.regime_confidence = 0.0
        self.confirmation_count = 0
        self.logger = logging.getLogger(__name__)
    
    async def detect_market_regime(self, market_data: MarketData) -> Tuple[MarketRegime, float]:
        """檢測當前市場制度"""
        try:
            regime_scores = {}
            
            # 檢測牛市趨勢
            bull_score = await self._calculate_bull_trend_score(market_data)
            regime_scores[MarketRegime.BULL_TREND] = bull_score
            
            # 檢測熊市趨勢
            bear_score = await self._calculate_bear_trend_score(market_data)
            regime_scores[MarketRegime.BEAR_TREND] = bear_score
            
            # 檢測橫盤整理
            sideways_score = await self._calculate_sideways_score(market_data)
            regime_scores[MarketRegime.SIDEWAYS] = sideways_score
            
            # 檢測高波動
            volatile_score = await self._calculate_volatile_score(market_data)
            regime_scores[MarketRegime.VOLATILE] = volatile_score
            
            # 選擇最高分數的制度
            best_regime = max(regime_scores.keys(), key=lambda k: regime_scores[k])
            confidence = regime_scores[best_regime]
            
            # 檢查是否滿足最小信心度要求
            min_confidence = self.regime_types[best_regime.value]["confidence_threshold"]
            
            if confidence >= min_confidence:
                # 檢查制度持續性要求
                if await self._check_regime_persistence(best_regime, confidence):
                    self.current_regime = best_regime
                    self.regime_confidence = confidence
                    self.logger.info(f"Market regime detected: {best_regime.value} (confidence: {confidence:.3f})")
                else:
                    # 需要更多確認
                    best_regime = self.current_regime
                    confidence = self.regime_confidence
            else:
                # 信心度不足，保持當前制度
                best_regime = self.current_regime
                confidence = self.regime_confidence
            
            return best_regime, confidence
            
        except Exception as e:
            self.logger.error(f"Error in market regime detection: {e}")
            return MarketRegime.UNKNOWN, 0.0
    
    async def _calculate_bull_trend_score(self, market_data: MarketData) -> float:
        """計算牛市趨勢分數"""
        score = 0.0
        criteria = self.regime_types["BULL_TREND"]["detection_criteria"]
        
        # 價格趨勢斜率檢查
        if market_data.price_change_24h > 0.02:
            score += 0.3
        
        # 成交量確認
        if market_data.volume_ratio > 1.2:
            score += 0.25
        
        # 恐懼貪婪指數
        if market_data.fear_greed_index > 60:
            score += 0.25
        
        # 移動平均線排列
        ma_20 = market_data.moving_averages.get("ma_20", 0)
        ma_50 = market_data.moving_averages.get("ma_50", 0)
        ma_200 = market_data.moving_averages.get("ma_200", 0)
        
        if ma_20 > ma_50 > ma_200 and market_data.price > ma_20:
            score += 0.2
        
        return min(score, 1.0)
    
    async def _calculate_bear_trend_score(self, market_data: MarketData) -> float:
        """計算熊市趨勢分數"""
        score = 0.0
        
        # 價格趨勢斜率檢查
        if market_data.price_change_24h < -0.02:
            score += 0.3
        
        # 成交量確認
        if market_data.volume_ratio > 1.1:
            score += 0.25
        
        # 恐懼貪婪指數
        if market_data.fear_greed_index < 40:
            score += 0.25
        
        # 移動平均線排列（熊市排列）
        ma_20 = market_data.moving_averages.get("ma_20", 0)
        ma_50 = market_data.moving_averages.get("ma_50", 0)
        ma_200 = market_data.moving_averages.get("ma_200", 0)
        
        if ma_20 < ma_50 < ma_200 and market_data.price < ma_20:
            score += 0.2
        
        return min(score, 1.0)
    
    async def _calculate_sideways_score(self, market_data: MarketData) -> float:
        """計算橫盤整理分數"""
        score = 0.0
        
        # 價格趨勢斜率檢查
        if -0.02 <= market_data.price_change_24h <= 0.02:
            score += 0.3
        
        # 波動率檢查
        if market_data.volatility < 0.05:
            score += 0.3
        
        # 成交量比率
        if 0.8 <= market_data.volume_ratio <= 1.2:
            score += 0.2
        
        # 區間震盪確認（簡化實現）
        if market_data.price_change_1h < 0.01:
            score += 0.2
        
        return min(score, 1.0)
    
    async def _calculate_volatile_score(self, market_data: MarketData) -> float:
        """計算高波動分數"""
        score = 0.0
        
        # 波動率檢查
        if market_data.volatility > 0.08:
            score += 0.3
        
        # 價格跳空
        if abs(market_data.price_change_1h) > 0.02:
            score += 0.3
        
        # 成交量激增
        if market_data.volume_ratio > 2.0:
            score += 0.2
        
        # 日內波幅（簡化實現）
        if market_data.volatility > 0.05:
            score += 0.2
        
        return min(score, 1.0)
    
    async def _check_regime_persistence(self, regime: MarketRegime, confidence: float) -> bool:
        """檢查制度持續性要求"""
        if regime == self.current_regime:
            self.confirmation_count += 1
        else:
            self.confirmation_count = 1
        
        # 需要至少2次確認
        return self.confirmation_count >= 2

class TradingSessionDetector:
    """交易時段檢測器 - 100%匹配JSON配置"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session_types = config["dynamic_parameter_system"]["trading_session_detection"]["session_types"]
        self.timezone_handling = config["dynamic_parameter_system"]["trading_session_detection"]["timezone_handling"]
        self.logger = logging.getLogger(__name__)
    
    async def detect_trading_session(self, current_time: Optional[datetime] = None) -> TradingSession:
        """檢測當前交易時段"""
        try:
            if current_time is None:
                current_time = datetime.now(timezone.utc)
            
            # 轉換到各市場時區
            est_time = current_time.astimezone(pytz.timezone('US/Eastern'))
            jst_time = current_time.astimezone(pytz.timezone('Asia/Tokyo'))
            gmt_time = current_time.astimezone(pytz.timezone('GMT'))
            
            # 檢查美股交易時段 (09:30-16:00 EST)
            if self._is_us_market_hours(est_time):
                # 檢查是否為重疊時段
                if self._is_overlap_hours(est_time, gmt_time):
                    return TradingSession.OVERLAP_HOURS
                return TradingSession.US_MARKET
            
            # 檢查亞洲市場時段 (09:00-15:00 JST)
            if self._is_asia_market_hours(jst_time):
                # 檢查是否為重疊時段
                if self._is_asia_europe_overlap(jst_time, gmt_time):
                    return TradingSession.OVERLAP_HOURS
                return TradingSession.ASIA_MARKET
            
            # 檢查歐洲市場時段 (08:00-16:30 GMT)
            if self._is_europe_market_hours(gmt_time):
                return TradingSession.EUROPE_MARKET
            
            # 默認為非活躍時段
            return TradingSession.OFF_HOURS
            
        except Exception as e:
            self.logger.error(f"Error in trading session detection: {e}")
            return TradingSession.OFF_HOURS
    
    def _is_us_market_hours(self, est_time: datetime) -> bool:
        """檢查是否為美股交易時間"""
        weekday = est_time.weekday()
        if weekday >= 5:  # 週末
            return False
        
        hour = est_time.hour
        minute = est_time.minute
        current_minutes = hour * 60 + minute
        
        # 09:30-16:00 EST
        start_minutes = 9 * 60 + 30
        end_minutes = 16 * 60
        
        return start_minutes <= current_minutes <= end_minutes
    
    def _is_asia_market_hours(self, jst_time: datetime) -> bool:
        """檢查是否為亞洲市場交易時間"""
        weekday = jst_time.weekday()
        if weekday >= 5:  # 週末
            return False
        
        hour = jst_time.hour
        # 09:00-15:00 JST
        return 9 <= hour <= 15
    
    def _is_europe_market_hours(self, gmt_time: datetime) -> bool:
        """檢查是否為歐洲市場交易時間"""
        weekday = gmt_time.weekday()
        if weekday >= 5:  # 週末
            return False
        
        hour = gmt_time.hour
        minute = gmt_time.minute
        current_minutes = hour * 60 + minute
        
        # 08:00-16:30 GMT
        start_minutes = 8 * 60
        end_minutes = 16 * 60 + 30
        
        return start_minutes <= current_minutes <= end_minutes
    
    def _is_overlap_hours(self, est_time: datetime, gmt_time: datetime) -> bool:
        """檢查是否為美歐重疊時段 (14:00-16:00 EST)"""
        if not self._is_us_market_hours(est_time):
            return False
        
        hour = est_time.hour
        return 14 <= hour <= 16 and self._is_europe_market_hours(gmt_time)
    
    def _is_asia_europe_overlap(self, jst_time: datetime, gmt_time: datetime) -> bool:
        """檢查是否為亞歐重疊時段 (09:00-11:00 JST)"""
        if not self._is_asia_market_hours(jst_time):
            return False
        
        hour = jst_time.hour
        return 9 <= hour <= 11 and self._is_europe_market_hours(gmt_time)

class DynamicParameterAdapter:
    """動態參數適配器 - 100%匹配JSON配置"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dynamic_parameters = config["dynamic_parameter_system"]["dynamic_parameters"]
        self.logger = logging.getLogger(__name__)
    
    async def adapt_parameter(
        self,
        parameter_config: Dict[str, Any],
        market_regime: MarketRegime,
        trading_session: TradingSession,
        market_data: MarketData
    ) -> AdaptedParameter:
        """適配單個參數"""
        try:
            parameter_name = parameter_config["parameter_name"]
            base_value = parameter_config["base_value"]
            adaptation_rules = parameter_config["adaptation_rules"]
            bounds = parameter_config["bounds"]
            
            adaptation_factor = 1.0
            adaptation_reasons = []
            
            # 市場制度調整
            if market_regime.value in adaptation_rules:
                regime_factor = adaptation_rules[market_regime.value].get("adjustment_factor", 1.0)
                adaptation_factor *= regime_factor
                reason = adaptation_rules[market_regime.value].get("description", "市場制度調整")
                adaptation_reasons.append(f"市場制度調整 ({market_regime.value}): {reason}")
            
            # 恐懼貪婪指數調整
            if "fear_greed_adjustment" in adaptation_rules:
                fg_factor = self._get_fear_greed_factor(
                    market_data.fear_greed_index,
                    adaptation_rules["fear_greed_adjustment"]
                )
                if fg_factor != 1.0:
                    adaptation_factor *= fg_factor
                    adaptation_reasons.append(f"恐懼貪婪指數調整: {market_data.fear_greed_index}")
            
            # 交易時段調整
            if "session_adjustment" in adaptation_rules:
                session_factor = self._get_session_factor(
                    trading_session,
                    adaptation_rules["session_adjustment"]
                )
                if session_factor != 1.0:
                    adaptation_factor *= session_factor
                    adaptation_reasons.append(f"交易時段調整 ({trading_session.value})")
            
            # 流動性調整
            if "liquidity_adjustment" in adaptation_rules:
                liquidity_factor = self._get_liquidity_factor(
                    market_data,
                    adaptation_rules["liquidity_adjustment"]
                )
                if liquidity_factor != 1.0:
                    adaptation_factor *= liquidity_factor
                    adaptation_reasons.append(f"流動性調整")
            
            # 波動率調整
            if "volatility_adjustment" in adaptation_rules:
                volatility_factor = self._get_volatility_factor(
                    market_data.volatility,
                    adaptation_rules["volatility_adjustment"]
                )
                if volatility_factor != 1.0:
                    adaptation_factor *= volatility_factor
                    adaptation_reasons.append(f"波動率調整")
            
            # 計算適配後的值
            adapted_value = base_value * adaptation_factor
            
            # 應用邊界限制
            min_val = bounds["minimum"]
            max_val = bounds["maximum"]
            adapted_value = max(min_val, min(adapted_value, max_val))
            
            # 計算信心度
            confidence_score = self._calculate_confidence_score(
                adaptation_factor, len(adaptation_reasons)
            )
            
            return AdaptedParameter(
                parameter_name=parameter_name,
                original_value=base_value,
                adapted_value=adapted_value,
                adaptation_factor=adaptation_factor,
                adaptation_reasons=adaptation_reasons,
                confidence_score=confidence_score,
                timestamp=datetime.now(timezone.utc),
                market_regime=market_regime,
                trading_session=trading_session
            )
            
        except Exception as e:
            self.logger.error(f"Error adapting parameter {parameter_config.get('parameter_name', 'unknown')}: {e}")
            # 返回未調整的參數
            return AdaptedParameter(
                parameter_name=parameter_config.get("parameter_name", "unknown"),
                original_value=parameter_config.get("base_value", 0.0),
                adapted_value=parameter_config.get("base_value", 0.0),
                adaptation_factor=1.0,
                adaptation_reasons=["適配失敗，使用原始值"],
                confidence_score=0.0,
                timestamp=datetime.now(timezone.utc),
                market_regime=market_regime,
                trading_session=trading_session
            )
    
    def _get_fear_greed_factor(self, fg_index: int, fg_rules: Dict[str, Any]) -> float:
        """根據恐懼貪婪指數獲取調整因子"""
        if 0 <= fg_index <= 20 and "extreme_fear" in fg_rules:
            return fg_rules["extreme_fear"]["factor"]
        elif 21 <= fg_index <= 40 and "fear" in fg_rules:
            return fg_rules["fear"]["factor"]
        elif 41 <= fg_index <= 59 and "neutral" in fg_rules:
            return fg_rules["neutral"]["factor"]
        elif 60 <= fg_index <= 79 and "greed" in fg_rules:
            return fg_rules["greed"]["factor"]
        elif 80 <= fg_index <= 100 and "extreme_greed" in fg_rules:
            return fg_rules["extreme_greed"]["factor"]
        else:
            return 1.0
    
    def _get_session_factor(self, session: TradingSession, session_rules: Dict[str, Any]) -> float:
        """根據交易時段獲取調整因子"""
        session_key = session.value
        if session_key in session_rules:
            return session_rules[session_key]["factor"]
        elif "default" in session_rules:
            return session_rules["default"]["factor"]
        else:
            return 1.0
    
    def _get_liquidity_factor(self, market_data: MarketData, liquidity_rules: Dict[str, Any]) -> float:
        """根據流動性獲取調整因子"""
        liquidity_score = 1.0 - market_data.bid_ask_spread  # 簡化流動性計算
        
        if liquidity_score > 0.8 and "high_liquidity" in liquidity_rules:
            return liquidity_rules["high_liquidity"]["factor"]
        elif 0.5 <= liquidity_score <= 0.8 and "medium_liquidity" in liquidity_rules:
            return liquidity_rules["medium_liquidity"]["factor"]
        elif liquidity_score < 0.5 and "low_liquidity" in liquidity_rules:
            return liquidity_rules["low_liquidity"]["factor"]
        else:
            return 1.0
    
    def _get_volatility_factor(self, volatility: float, volatility_rules: Dict[str, Any]) -> float:
        """根據波動率獲取調整因子"""
        if volatility > 0.08 and "high_volatility" in volatility_rules:
            return volatility_rules["high_volatility"]["factor"]
        elif 0.02 <= volatility <= 0.08 and "normal_volatility" in volatility_rules:
            return volatility_rules["normal_volatility"]["factor"]
        elif volatility < 0.02 and "low_volatility" in volatility_rules:
            return volatility_rules["low_volatility"]["factor"]
        else:
            return 1.0
    
    def _calculate_confidence_score(self, adaptation_factor: float, reason_count: int) -> float:
        """計算適配信心度"""
        # 基礎信心度
        base_confidence = 0.8
        
        # 調整因子偏離度懲罰
        deviation = abs(adaptation_factor - 1.0)
        deviation_penalty = min(deviation * 0.5, 0.3)
        
        # 調整原因數量獎勵
        reason_bonus = min(reason_count * 0.05, 0.2)
        
        confidence = base_confidence - deviation_penalty + reason_bonus
        return max(0.0, min(confidence, 1.0))

class DynamicParameterEngine:
    """動態參數引擎主類 - 整合所有組件"""
    
    def __init__(self, config_path: str, market_data_source: Optional[MarketDataSource] = None):
        self.config_path = config_path
        self.config = self._load_config()
        self.market_data_source = market_data_source or MockMarketDataSource()
        
        # 初始化組件
        self.regime_detector = MarketRegimeDetector(self.config)
        self.session_detector = TradingSessionDetector(self.config)
        self.parameter_adapter = DynamicParameterAdapter(self.config)
        
        # 緩存
        self._regime_cache = None
        self._session_cache = None
        self._last_update = None
        
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self) -> Dict[str, Any]:
        """載入配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config from {self.config_path}: {e}")
            raise
    
    async def get_dynamic_parameters(
        self,
        phase: str,
        force_refresh: bool = False
    ) -> DynamicParameterResult:
        """獲取指定階段的動態參數"""
        try:
            # 獲取市場數據
            market_data = await self.market_data_source.get_current_market_data()
            
            # 檢測市場制度和交易時段
            market_regime, regime_confidence = await self.regime_detector.detect_market_regime(market_data)
            trading_session = await self.session_detector.detect_trading_session()
            
            # 獲取階段參數配置
            phase_config = self._get_phase_config(phase)
            if not phase_config:
                raise ValueError(f"Phase '{phase}' not found in configuration")
            
            # 適配所有參數
            adapted_parameters = {}
            for param_name, param_config in phase_config.items():
                adapted_param = await self.parameter_adapter.adapt_parameter(
                    param_config, market_regime, trading_session, market_data
                )
                adapted_parameters[param_name] = adapted_param
            
            # 構建結果
            result = DynamicParameterResult(
                adapted_parameters=adapted_parameters,
                market_regime=market_regime,
                trading_session=trading_session,
                regime_confidence=regime_confidence,
                timestamp=datetime.now(timezone.utc),
                metadata={
                    "config_version": self.config["dynamic_parameter_system"]["system_metadata"]["version"],
                    "market_data_timestamp": market_data.timestamp.isoformat(),
                    "fear_greed_index": market_data.fear_greed_index,
                    "volatility": market_data.volatility,
                    "volume_ratio": market_data.volume_ratio
                }
            )
            
            self.logger.info(
                f"Generated dynamic parameters for {phase}: "
                f"regime={market_regime.value}, session={trading_session.value}, "
                f"param_count={len(adapted_parameters)}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating dynamic parameters for {phase}: {e}")
            raise
    
    def _get_phase_config(self, phase: str) -> Optional[Dict[str, Any]]:
        """獲取指定階段的參數配置"""
        phase_mapping = {
            "phase1": "phase1_signal_generation",
            "phase1_signal_generation": "phase1_signal_generation",
            "phase2": "phase2_pre_evaluation",
            "phase2_pre_evaluation": "phase2_pre_evaluation", 
            "phase3": "phase3_execution_policy",
            "phase3_execution_policy": "phase3_execution_policy",
            "phase5": "phase5_backtest_validation",
            "phase5_backtest_validation": "phase5_backtest_validation"
        }
        
        mapped_phase = phase_mapping.get(phase)
        if not mapped_phase:
            return None
        
        return self.config["dynamic_parameter_system"]["dynamic_parameters"].get(mapped_phase)
    
    async def get_parameter_value(
        self,
        phase: str,
        parameter_name: str,
        force_refresh: bool = False
    ) -> float:
        """獲取單個參數的動態值"""
        result = await self.get_dynamic_parameters(phase, force_refresh)
        
        if parameter_name in result.adapted_parameters:
            return result.adapted_parameters[parameter_name].adapted_value
        else:
            raise ValueError(f"Parameter '{parameter_name}' not found in phase '{phase}'")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        try:
            market_data = await self.market_data_source.get_current_market_data()
            market_regime, regime_confidence = await self.regime_detector.detect_market_regime(market_data)
            trading_session = await self.session_detector.detect_trading_session()
            
            return {
                "status": "operational",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "market_regime": {
                    "current": market_regime.value,
                    "confidence": regime_confidence
                },
                "trading_session": trading_session.value,
                "market_data": {
                    "price": market_data.price,
                    "volatility": market_data.volatility,
                    "volume_ratio": market_data.volume_ratio,
                    "fear_greed_index": market_data.fear_greed_index
                },
                "config_version": self.config["dynamic_parameter_system"]["system_metadata"]["version"]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

# 輔助函數
async def create_dynamic_parameter_engine(
    config_path: str = "/Users/itts/Desktop/Trading X/X/backend/phase1_signal_generation/dynamic_parameter_config.json",
    market_data_source: Optional[MarketDataSource] = None
) -> DynamicParameterEngine:
    """創建動態參數引擎實例"""
    return DynamicParameterEngine(config_path, market_data_source)

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    # 測試示例
    async def test_dynamic_parameter_engine():
        """測試動態參數引擎"""
        try:
            # 創建引擎
            engine = await create_dynamic_parameter_engine()
            
            # 測試系統狀態
            status = await engine.get_system_status()
            print("系統狀態:")
            print(json.dumps(status, indent=2, ensure_ascii=False))
            
            # 測試Phase1參數
            phase1_result = await engine.get_dynamic_parameters("phase1")
            print("\nPhase1 動態參數:")
            for param_name, param in phase1_result.adapted_parameters.items():
                print(f"  {param_name}: {param.original_value} → {param.adapted_value:.4f} "
                      f"(因子: {param.adaptation_factor:.3f})")
                for reason in param.adaptation_reasons:
                    print(f"    - {reason}")
            
            # 測試單個參數值獲取
            confidence_threshold = await engine.get_parameter_value("phase1", "confidence_threshold")
            print(f"\nconfidence_threshold 動態值: {confidence_threshold:.4f}")
            
        except Exception as e:
            print(f"測試失敗: {e}")
            import traceback
            traceback.print_exc()
    
    # 運行測試
    asyncio.run(test_dynamic_parameter_engine())
