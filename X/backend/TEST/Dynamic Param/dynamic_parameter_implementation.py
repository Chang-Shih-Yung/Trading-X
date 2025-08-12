#!/usr/bin/env python3
"""
🚀 Trading X - 動態參數實施方案
===============================

基於靜態參數分析結果，針對 Phase1-5 中發現的 2099 個靜態參數，
特別是 80 個高優化潛力參數，提供具體的動態化實施方案。

重點聚焦：
1. 牛熊市自動調整機制
2. 美股開盤時間適應性
3. 波動性實時調整
4. 流動性條件優化
"""

from datetime import datetime, time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import pytz

class MarketRegime(Enum):
    """市場制度分類"""
    BULL_TREND = "bull"          # 牛市趨勢
    BEAR_TREND = "bear"          # 熊市趨勢
    SIDEWAYS = "sideways"        # 橫盤整理
    VOLATILE = "volatile"        # 高波動期
    ACCUMULATION = "accumulation" # 吸籌階段
    DISTRIBUTION = "distribution" # 派發階段

class TradingSession(Enum):
    """交易時段分類"""
    US_MARKET = "us_market"      # 美股交易時間
    ASIA_MARKET = "asia_market"  # 亞洲市場時間
    EUROPE_MARKET = "europe_market" # 歐洲市場時間
    OFF_HOURS = "off_hours"      # 非活躍時段
    OVERLAP_HOURS = "overlap"    # 重疊時段

@dataclass
class MarketConditions:
    """市場條件數據結構"""
    regime: MarketRegime
    volatility: float           # 當前波動率 (0.0-1.0)
    liquidity_score: float      # 流動性評分 (0.0-1.0)
    volume_ratio: float         # 成交量比率 (相對平均)
    fear_greed_index: int       # 恐懼貪婪指數 (0-100)
    trading_session: TradingSession
    timestamp: datetime

class DynamicParameterEngine:
    """動態參數引擎 - 核心實施類別"""
    
    def __init__(self):
        self.timezone_us = pytz.timezone('US/Eastern')
        self.timezone_asia = pytz.timezone('Asia/Tokyo')
        self.timezone_europe = pytz.timezone('Europe/London')
        
        # 基準參數配置
        self.base_parameters = self._initialize_base_parameters()
        
        # 適應性調整係數
        self.adaptation_factors = self._initialize_adaptation_factors()
    
    def _initialize_base_parameters(self) -> Dict[str, Any]:
        """初始化基準參數"""
        return {
            # Phase1 - 信號生成參數
            "phase1": {
                "confidence_threshold": 0.75,        # 信心度閾值
                "volume_surge_multiplier": 1.0,      # 成交量激增倍數
                "volatility_percentile": 0.5,        # 波動性百分位
                "signal_strength_threshold": 0.6,    # 信號強度閾值
                "noise_filter_sensitivity": 0.3,     # 噪音過濾敏感度
            },
            
            # Phase2 - 預處理參數
            "phase2": {
                "similarity_threshold": 0.85,        # 相似度閾值
                "time_overlap_minutes": 15,          # 時間重疊分鐘
                "source_consensus_threshold": 0.72,  # 源共識閾值
                "model_diversity_threshold": 0.8,    # 模型多樣性閾值
                "quality_control_threshold": 0.7,    # 品質控制閾值
            },
            
            # Phase3 - 執行策略參數
            "phase3": {
                "replacement_score_threshold": 0.75, # 替換評分閾值
                "strengthening_score_threshold": 0.70, # 加強評分閾值
                "new_position_threshold": 0.70,      # 新倉位閾值
                "risk_tolerance": 0.05,              # 風險容忍度
                "position_concentration_limit": 0.30, # 倉位集中度限制
            },
            
            # Phase4 - 監控參數
            "phase4": {
                "alert_threshold": 0.8,              # 預警閾值
                "performance_tracking_interval": 300, # 性能追蹤間隔(秒)
                "notification_urgency_threshold": 0.9, # 通知緊急度閾值
                "system_health_threshold": 0.95,     # 系統健康度閾值
            },
            
            # Phase5 - 回測參數
            "phase5": {
                "backtest_confidence_threshold": 0.8, # 回測信心度閾值
                "performance_benchmark": 0.15,        # 性能基準
                "risk_adjusted_return_threshold": 1.5, # 風險調整收益閾值
                "sharpe_ratio_minimum": 1.0,          # 夏普比率最低要求
            }
        }
    
    def _initialize_adaptation_factors(self) -> Dict[str, Dict[str, float]]:
        """初始化適應性調整係數"""
        return {
            # 市場制度調整係數
            "market_regime": {
                MarketRegime.BULL_TREND: {
                    "confidence_factor": 0.85,       # 牛市降低信心度要求
                    "risk_factor": 1.2,              # 牛市提高風險容忍
                    "position_size_factor": 1.3,     # 牛市增加倉位
                    "alert_sensitivity": 0.9,        # 牛市降低預警敏感度
                },
                MarketRegime.BEAR_TREND: {
                    "confidence_factor": 1.15,       # 熊市提高信心度要求
                    "risk_factor": 0.8,              # 熊市降低風險容忍
                    "position_size_factor": 0.7,     # 熊市減少倉位
                    "alert_sensitivity": 1.2,        # 熊市提高預警敏感度
                },
                MarketRegime.VOLATILE: {
                    "confidence_factor": 1.1,        # 高波動提高要求
                    "risk_factor": 0.7,              # 高波動降低風險
                    "position_size_factor": 0.8,     # 高波動減少倉位
                    "alert_sensitivity": 1.3,        # 高波動提高預警
                },
                MarketRegime.SIDEWAYS: {
                    "confidence_factor": 1.0,        # 橫盤標準要求
                    "risk_factor": 1.0,              # 橫盤標準風險
                    "position_size_factor": 1.0,     # 橫盤標準倉位
                    "alert_sensitivity": 1.0,        # 橫盤標準預警
                }
            },
            
            # 交易時段調整係數
            "trading_session": {
                TradingSession.US_MARKET: {
                    "update_frequency": 0.7,         # 美股時段提高頻率
                    "signal_sensitivity": 1.1,       # 提高信號敏感度
                    "liquidity_weight": 1.2,         # 增加流動性權重
                    "execution_speed": 0.8,          # 加快執行速度
                },
                TradingSession.ASIA_MARKET: {
                    "update_frequency": 1.0,         # 亞洲時段標準頻率
                    "signal_sensitivity": 1.0,       # 標準信號敏感度
                    "liquidity_weight": 1.0,         # 標準流動性權重
                    "execution_speed": 1.0,          # 標準執行速度
                },
                TradingSession.OFF_HOURS: {
                    "update_frequency": 1.5,         # 非活躍時段降低頻率
                    "signal_sensitivity": 0.9,       # 降低信號敏感度
                    "liquidity_weight": 0.8,         # 降低流動性權重
                    "execution_speed": 1.2,          # 放慢執行速度
                },
                TradingSession.OVERLAP_HOURS: {
                    "update_frequency": 0.6,         # 重疊時段最高頻率
                    "signal_sensitivity": 1.2,       # 最高信號敏感度
                    "liquidity_weight": 1.3,         # 最高流動性權重
                    "execution_speed": 0.7,          # 最快執行速度
                }
            }
        }
    
    def get_dynamic_parameters(self, phase: str, market_conditions: MarketConditions) -> Dict[str, Any]:
        """獲取動態調整後的參數"""
        if phase not in self.base_parameters:
            raise ValueError(f"不支援的 Phase: {phase}")
        
        base_params = self.base_parameters[phase].copy()
        
        # 應用市場制度調整
        regime_factors = self.adaptation_factors["market_regime"].get(
            market_conditions.regime, {}
        )
        
        # 應用交易時段調整
        session_factors = self.adaptation_factors["trading_session"].get(
            market_conditions.trading_session, {}
        )
        
        # 執行動態調整
        adjusted_params = self._apply_dynamic_adjustments(
            base_params, market_conditions, regime_factors, session_factors
        )
        
        return adjusted_params
    
    def _apply_dynamic_adjustments(self, base_params: Dict[str, Any], 
                                 market_conditions: MarketConditions,
                                 regime_factors: Dict[str, float],
                                 session_factors: Dict[str, float]) -> Dict[str, Any]:
        """應用動態調整邏輯"""
        adjusted = base_params.copy()
        
        # 1. 信心度相關參數調整
        confidence_params = [k for k in adjusted.keys() if "confidence" in k or "threshold" in k]
        for param in confidence_params:
            original_value = adjusted[param]
            
            # 市場制度調整
            regime_factor = regime_factors.get("confidence_factor", 1.0)
            
            # 恐懼貪婪指數調整
            fear_greed_factor = self._calculate_fear_greed_factor(market_conditions.fear_greed_index)
            
            # 波動性調整
            volatility_factor = self._calculate_volatility_factor(market_conditions.volatility)
            
            # 綜合調整
            adjusted[param] = original_value * regime_factor * fear_greed_factor * volatility_factor
            adjusted[param] = max(0.1, min(0.95, adjusted[param]))  # 限制在合理範圍
        
        # 2. 倉位相關參數調整
        position_params = [k for k in adjusted.keys() if "position" in k or "size" in k]
        for param in position_params:
            original_value = adjusted[param]
            
            # 市場制度調整
            regime_factor = regime_factors.get("position_size_factor", 1.0)
            
            # 流動性調整
            liquidity_factor = self._calculate_liquidity_factor(market_conditions.liquidity_score)
            
            # 成交量調整
            volume_factor = self._calculate_volume_factor(market_conditions.volume_ratio)
            
            # 綜合調整
            adjusted[param] = original_value * regime_factor * liquidity_factor * volume_factor
            adjusted[param] = max(0.1, min(2.0, adjusted[param]))  # 限制倉位倍數
        
        # 3. 風險相關參數調整
        risk_params = [k for k in adjusted.keys() if "risk" in k or "tolerance" in k]
        for param in risk_params:
            original_value = adjusted[param]
            
            # 市場制度調整
            regime_factor = regime_factors.get("risk_factor", 1.0)
            
            # 波動性風險調整
            volatility_risk_factor = 1.0 - (market_conditions.volatility - 0.05) * 2
            volatility_risk_factor = max(0.5, min(1.5, volatility_risk_factor))
            
            # 綜合調整
            adjusted[param] = original_value * regime_factor * volatility_risk_factor
            adjusted[param] = max(0.01, min(0.15, adjusted[param]))  # 限制風險範圍
        
        # 4. 時間相關參數調整
        time_params = [k for k in adjusted.keys() if "time" in k or "interval" in k or "minutes" in k]
        for param in time_params:
            original_value = adjusted[param]
            
            # 交易時段調整
            session_factor = session_factors.get("update_frequency", 1.0)
            
            # 市場活躍度調整
            activity_factor = self._calculate_activity_factor(market_conditions)
            
            # 綜合調整
            adjusted[param] = original_value * session_factor * activity_factor
            adjusted[param] = max(1, min(300, adjusted[param]))  # 限制時間範圍
        
        return adjusted
    
    def _calculate_fear_greed_factor(self, fear_greed_index: int) -> float:
        """計算恐懼貪婪指數調整係數"""
        if fear_greed_index < 20:  # 極度恐懼
            return 0.8  # 降低閾值，抓住抄底機會
        elif fear_greed_index > 80:  # 極度貪婪
            return 1.2  # 提高閾值，風險控制
        elif 20 <= fear_greed_index <= 40:  # 恐懼
            return 0.9
        elif 60 <= fear_greed_index <= 80:  # 貪婪
            return 1.1
        else:  # 中性
            return 1.0
    
    def _calculate_volatility_factor(self, volatility: float) -> float:
        """計算波動性調整係數"""
        if volatility > 0.08:  # 高波動
            return 1.1  # 提高閾值
        elif volatility < 0.02:  # 低波動
            return 0.9  # 降低閾值
        else:
            return 1.0
    
    def _calculate_liquidity_factor(self, liquidity_score: float) -> float:
        """計算流動性調整係數"""
        if liquidity_score > 0.8:  # 高流動性
            return 1.2  # 可以增加倉位
        elif liquidity_score < 0.3:  # 低流動性
            return 0.7  # 減少倉位
        else:
            return 1.0
    
    def _calculate_volume_factor(self, volume_ratio: float) -> float:
        """計算成交量調整係數"""
        if volume_ratio > 1.5:  # 放量
            return 1.1  # 增加信心
        elif volume_ratio < 0.5:  # 縮量
            return 0.9  # 降低信心
        else:
            return 1.0
    
    def _calculate_activity_factor(self, market_conditions: MarketConditions) -> float:
        """計算市場活躍度調整係數"""
        # 綜合考慮成交量和波動性
        volume_component = min(1.5, max(0.5, market_conditions.volume_ratio))
        volatility_component = min(1.3, max(0.7, 1.0 + market_conditions.volatility * 5))
        
        return (volume_component + volatility_component) / 2
    
    def get_current_trading_session(self, current_time: datetime = None) -> TradingSession:
        """獲取當前交易時段"""
        if current_time is None:
            current_time = datetime.now(pytz.UTC)
        
        # 轉換到各時區
        us_time = current_time.astimezone(self.timezone_us).time()
        asia_time = current_time.astimezone(self.timezone_asia).time()
        europe_time = current_time.astimezone(self.timezone_europe).time()
        
        # 美股交易時間 (9:30-16:00 ET)
        if time(9, 30) <= us_time <= time(16, 0):
            # 檢查是否有重疊
            if time(14, 0) <= us_time <= time(16, 0):  # 與歐洲重疊
                return TradingSession.OVERLAP_HOURS
            return TradingSession.US_MARKET
        
        # 亞洲交易時間 (9:00-15:00 JST)
        elif time(9, 0) <= asia_time <= time(15, 0):
            return TradingSession.ASIA_MARKET
        
        # 歐洲交易時間 (8:00-16:30 GMT)
        elif time(8, 0) <= europe_time <= time(16, 30):
            return TradingSession.EUROPE_MARKET
        
        else:
            return TradingSession.OFF_HOURS

# 使用示例和測試
def demonstrate_dynamic_parameters():
    """演示動態參數調整"""
    engine = DynamicParameterEngine()
    
    # 模擬不同市場條件
    scenarios = [
        {
            "name": "牛市高活躍時段",
            "conditions": MarketConditions(
                regime=MarketRegime.BULL_TREND,
                volatility=0.03,
                liquidity_score=0.9,
                volume_ratio=1.8,
                fear_greed_index=75,
                trading_session=TradingSession.US_MARKET,
                timestamp=datetime.now()
            )
        },
        {
            "name": "熊市低流動性時段",
            "conditions": MarketConditions(
                regime=MarketRegime.BEAR_TREND,
                volatility=0.12,
                liquidity_score=0.4,
                volume_ratio=0.6,
                fear_greed_index=25,
                trading_session=TradingSession.OFF_HOURS,
                timestamp=datetime.now()
            )
        },
        {
            "name": "高波動橫盤整理",
            "conditions": MarketConditions(
                regime=MarketRegime.VOLATILE,
                volatility=0.15,
                liquidity_score=0.7,
                volume_ratio=1.2,
                fear_greed_index=50,
                trading_session=TradingSession.OVERLAP_HOURS,
                timestamp=datetime.now()
            )
        }
    ]
    
    print("🚀 Trading X 動態參數調整演示")
    print("=" * 60)
    
    for scenario in scenarios:
        print(f"\n📊 情境: {scenario['name']}")
        print("-" * 40)
        
        conditions = scenario["conditions"]
        print(f"市場制度: {conditions.regime.value}")
        print(f"波動率: {conditions.volatility:.3f}")
        print(f"流動性: {conditions.liquidity_score:.3f}")
        print(f"成交量比: {conditions.volume_ratio:.3f}")
        print(f"恐懼貪婪: {conditions.fear_greed_index}")
        print(f"交易時段: {conditions.trading_session.value}")
        
        # 獲取各Phase的動態參數
        for phase in ["phase1", "phase2", "phase3"]:
            params = engine.get_dynamic_parameters(phase, conditions)
            print(f"\n{phase.upper()} 動態參數:")
            for key, value in list(params.items())[:3]:  # 只顯示前3個
                print(f"  {key}: {value:.4f}")
    
    print("\n✅ 動態參數調整演示完成")

if __name__ == "__main__":
    demonstrate_dynamic_parameters()
