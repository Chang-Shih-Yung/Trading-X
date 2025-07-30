"""
🎯 牛熊市場動態權重分配系統
根據市場狀態自動調整API數據權重
"""

import logging
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class MarketRegimeWeights:
    """市場機制權重配置"""
    binance_realtime_weight: float     # 幣安即時數據權重
    fear_greed_weight: float           # Fear & Greed 權重  
    technical_analysis_weight: float   # 技術分析權重
    regime_name: str                   # 機制名稱
    regime_confidence: float           # 機制信心度
    justification: str                 # 權重分配理由

class BullBearWeightManager:
    """牛熊市場權重管理器"""
    
    def __init__(self):
        # 🎯 牛熊市場指標定義
        self.bull_indicators = {
            "price_momentum": {
                "threshold": 2.0,           # 24h漲幅 >2%
                "weight_impact": 0.15       # 權重影響程度
            },
            "volume_surge": {
                "threshold": 2.0,           # 成交量暴增 >2倍
                "weight_impact": 0.10
            },
            "fear_greed_optimism": {
                "threshold": 65,            # F&G >65 貪婪
                "weight_impact": 0.10
            },
            "liquidity_strength": {
                "threshold": 1.5,           # 流動性 >1.5
                "weight_impact": 0.05
            },
            "market_activity": {
                "threshold": 2.2,           # 活躍度 >2.2
                "weight_impact": 0.10
            }
        }
        
        self.bear_indicators = {
            "price_decline": {
                "threshold": -2.0,          # 24h跌幅 <-2%
                "weight_impact": 0.15
            },
            "volume_panic": {
                "threshold": 2.5,           # 恐慌放量 >2.5倍
                "weight_impact": 0.12
            },
            "fear_greed_pessimism": {
                "threshold": 35,            # F&G <35 恐懼
                "weight_impact": 0.10
            },
            "liquidity_drying": {
                "threshold": 1.0,           # 流動性 <1.0
                "weight_impact": 0.08
            },
            "volatility_spike": {
                "threshold": 0.05,          # ATR >5%
                "weight_impact": 0.10
            }
        }
        
        # 🎯 預設權重配置
        self.default_weights = MarketRegimeWeights(
            binance_realtime_weight=0.65,
            fear_greed_weight=0.15,
            technical_analysis_weight=0.20,
            regime_name="NEUTRAL",
            regime_confidence=0.50,
            justification="中性市場，平衡權重分配"
        )
    
    def analyze_market_regime(self, market_data: Dict) -> Tuple[str, float, Dict[str, float]]:
        """
        🎯 分析市場機制和指標評分
        返回: (機制名稱, 信心度, 指標評分)
        """
        try:
            bull_score = 0.0
            bear_score = 0.0
            indicator_scores = {}
            
            # 📈 牛市指標評分
            if market_data.get("price_change_percentage_24h", 0) > self.bull_indicators["price_momentum"]["threshold"]:
                bull_score += self.bull_indicators["price_momentum"]["weight_impact"]
                indicator_scores["price_momentum_bull"] = True
                
            if market_data.get("market_activity_score", 0) > self.bull_indicators["market_activity"]["threshold"]:
                bull_score += self.bull_indicators["market_activity"]["weight_impact"]
                indicator_scores["activity_surge"] = True
                
            if market_data.get("fear_greed_value", 50) > self.bull_indicators["fear_greed_optimism"]["threshold"]:
                bull_score += self.bull_indicators["fear_greed_optimism"]["weight_impact"]
                indicator_scores["greed_sentiment"] = True
                
            if market_data.get("liquidity_score", 1.0) > self.bull_indicators["liquidity_strength"]["threshold"]:
                bull_score += self.bull_indicators["liquidity_strength"]["weight_impact"]
                indicator_scores["strong_liquidity"] = True
            
            # 📉 熊市指標評分
            if market_data.get("price_change_percentage_24h", 0) < self.bear_indicators["price_decline"]["threshold"]:
                bear_score += self.bear_indicators["price_decline"]["weight_impact"]
                indicator_scores["price_decline_bear"] = True
                
            if market_data.get("fear_greed_value", 50) < self.bear_indicators["fear_greed_pessimism"]["threshold"]:
                bear_score += self.bear_indicators["fear_greed_pessimism"]["weight_impact"]
                indicator_scores["fear_sentiment"] = True
                
            if market_data.get("liquidity_score", 1.0) < self.bear_indicators["liquidity_drying"]["threshold"]:
                bear_score += self.bear_indicators["liquidity_drying"]["weight_impact"]
                indicator_scores["weak_liquidity"] = True
                
            if market_data.get("atr_percentage", 0) > self.bear_indicators["volatility_spike"]["threshold"]:
                bear_score += self.bear_indicators["volatility_spike"]["weight_impact"]
                indicator_scores["high_volatility"] = True
            
            # 🎯 機制判斷邏輯
            if bull_score > bear_score and bull_score > 0.25:
                if bull_score > 0.40:
                    regime = "STRONG_BULL"
                    confidence = min(0.90, 0.60 + bull_score)
                else:
                    regime = "MILD_BULL"
                    confidence = min(0.80, 0.50 + bull_score)
            elif bear_score > bull_score and bear_score > 0.25:
                if bear_score > 0.40:
                    regime = "STRONG_BEAR"
                    confidence = min(0.90, 0.60 + bear_score)
                else:
                    regime = "MILD_BEAR"
                    confidence = min(0.80, 0.50 + bear_score)
            elif abs(bull_score - bear_score) < 0.10:
                regime = "NEUTRAL"
                confidence = 0.60
            else:
                regime = "UNCERTAIN"
                confidence = 0.40
            
            return regime, confidence, indicator_scores
            
        except Exception as e:
            logger.error(f"市場機制分析失敗: {e}")
            return "UNKNOWN", 0.30, {}
    
    def calculate_dynamic_weights(self, regime: str, confidence: float, 
                                market_data: Dict) -> MarketRegimeWeights:
        """
        🎯 根據市場機制動態計算權重
        """
        try:
            # 基礎權重
            base_binance = 0.65
            base_fear_greed = 0.15
            base_technical = 0.20
            
            if regime == "STRONG_BULL":
                # 強牛市：加重即時數據，減少恐懼指標
                weights = MarketRegimeWeights(
                    binance_realtime_weight=0.75,      # +10%
                    fear_greed_weight=0.10,            # -5%  
                    technical_analysis_weight=0.15,    # -5%
                    regime_name=regime,
                    regime_confidence=confidence,
                    justification="強牛市：優先即時動能數據，降低恐懼權重"
                )
                
            elif regime == "MILD_BULL":
                # 溫和牛市：略微加重即時數據
                weights = MarketRegimeWeights(
                    binance_realtime_weight=0.70,      # +5%
                    fear_greed_weight=0.12,            # -3%
                    technical_analysis_weight=0.18,    # -2%
                    regime_name=regime,
                    regime_confidence=confidence,
                    justification="溫和牛市：適度加重即時數據權重"
                )
                
            elif regime == "STRONG_BEAR":
                # 強熊市：加重技術分析和恐懼指標
                weights = MarketRegimeWeights(
                    binance_realtime_weight=0.55,      # -10%
                    fear_greed_weight=0.25,            # +10%
                    technical_analysis_weight=0.20,    # 維持
                    regime_name=regime,
                    regime_confidence=confidence,
                    justification="強熊市：加重恐懼指標，降低即時數據依賴"
                )
                
            elif regime == "MILD_BEAR":
                # 溫和熊市：增加恐懼權重
                weights = MarketRegimeWeights(
                    binance_realtime_weight=0.60,      # -5%
                    fear_greed_weight=0.20,            # +5%
                    technical_analysis_weight=0.20,    # 維持
                    regime_name=regime,
                    regime_confidence=confidence,
                    justification="溫和熊市：增加恐懼指標權重"
                )
                
            elif regime == "NEUTRAL":
                # 中性市場：標準權重
                weights = MarketRegimeWeights(
                    binance_realtime_weight=0.65,
                    fear_greed_weight=0.15,
                    technical_analysis_weight=0.20,
                    regime_name=regime,
                    regime_confidence=confidence,
                    justification="中性市場：標準權重平衡分配"
                )
                
            else:  # UNCERTAIN or UNKNOWN
                # 不確定市場：保守配置，加重技術分析
                weights = MarketRegimeWeights(
                    binance_realtime_weight=0.60,      # -5%
                    fear_greed_weight=0.15,            # 維持
                    technical_analysis_weight=0.25,    # +5%
                    regime_name=regime,
                    regime_confidence=confidence,
                    justification="不確定市場：加重技術分析，降低即時數據依賴"
                )
            
            # 🔍 極值調整
            fear_greed_value = market_data.get("fear_greed_value", 50)
            if fear_greed_value <= 20 or fear_greed_value >= 80:
                # 極值時額外提升F&G權重
                extra_fg_weight = 0.05
                weights.fear_greed_weight = min(0.30, weights.fear_greed_weight + extra_fg_weight)
                weights.binance_realtime_weight = max(0.50, weights.binance_realtime_weight - extra_fg_weight)
                weights.justification += f" | 極值F&G({fear_greed_value})額外+5%權重"
            
            return weights
            
        except Exception as e:
            logger.error(f"動態權重計算失敗: {e}")
            return self.default_weights
    
    def get_regime_indicators_explanation(self) -> Dict[str, Dict]:
        """獲取牛熊指標說明"""
        return {
            "bull_indicators": {
                "name": "牛市指標",
                "indicators": {
                    "價格動能": "24小時漲幅 > 2%",
                    "成交量暴增": "成交量 > 平均2倍",
                    "貪婪情緒": "Fear & Greed > 65",
                    "流動性充足": "流動性評分 > 1.5",
                    "市場活躍": "活躍度評分 > 2.2"
                }
            },
            "bear_indicators": {
                "name": "熊市指標", 
                "indicators": {
                    "價格下跌": "24小時跌幅 < -2%",
                    "恐慌拋售": "恐慌放量 > 2.5倍",
                    "恐懼情緒": "Fear & Greed < 35",
                    "流動性枯竭": "流動性評分 < 1.0",
                    "波動率飆升": "ATR > 5%"
                }
            },
            "weight_logic": {
                "強牛市": "即時數據75% | F&G 10% | 技術15%",
                "溫和牛市": "即時數據70% | F&G 12% | 技術18%", 
                "中性市場": "即時數據65% | F&G 15% | 技術20%",
                "溫和熊市": "即時數據60% | F&G 20% | 技術20%",
                "強熊市": "即時數據55% | F&G 25% | 技術20%"
            }
        }

# 全局實例
bull_bear_weight_manager = BullBearWeightManager()
