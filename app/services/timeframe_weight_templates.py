"""
三週期權重模板系統 - Trading X Phase 3
為短線/中線/長線不同持倉週期提供動態權重配置模板
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class TradingTimeframe(Enum):
    """交易時間框架枚舉 - 統一標準"""
    SHORT_TERM = "short"    # 短線: 1.5-8小時持倉
    MEDIUM_TERM = "medium"  # 中線: 8-48小時持倉
    LONG_TERM = "long"      # 長線: 24-120小時持倉

@dataclass
class SignalBlockWeights:
    """信號區塊權重配置"""
    # Phase 1 核心信號區塊
    precision_filter_weight: float      # 精準篩選器權重
    market_condition_weight: float      # 市場條件權重
    technical_analysis_weight: float    # 技術分析權重
    
    # Phase 2 機制適應區塊
    regime_analysis_weight: float       # 市場機制分析權重
    fear_greed_weight: float           # Fear & Greed 指標權重
    trend_alignment_weight: float      # 趨勢一致性權重
    
    # Phase 3 高階區塊 (預留)
    market_depth_weight: float         # 市場深度分析權重
    funding_rate_weight: float         # 資金費率情緒權重
    smart_money_weight: float          # 聰明錢流向權重
    
    def validate_weights(self) -> bool:
        """驗證權重總和是否接近1.0"""
        total = (
            self.precision_filter_weight + self.market_condition_weight + 
            self.technical_analysis_weight + self.regime_analysis_weight +
            self.fear_greed_weight + self.trend_alignment_weight +
            self.market_depth_weight + self.funding_rate_weight + 
            self.smart_money_weight
        )
        return 0.98 <= total <= 1.02  # 允許2%的誤差

    def get_total_weight(self) -> float:
        """計算總權重"""
        return (
            self.precision_filter_weight + self.market_condition_weight + 
            self.technical_analysis_weight + self.regime_analysis_weight +
            self.fear_greed_weight + self.trend_alignment_weight +
            self.market_depth_weight + self.funding_rate_weight + 
            self.smart_money_weight
        )

@dataclass
class TimeframeWeightTemplate:
    """時間框架權重模板"""
    timeframe: TradingTimeframe
    template_name: str
    description: str
    signal_weights: SignalBlockWeights
    
    # 時間框架特定參數
    confidence_threshold: float         # 信心度閾值
    risk_tolerance: float              # 風險容忍度 (0.1-1.0)
    position_size_multiplier: float    # 倉位大小倍數
    holding_period_hours: int          # 預期持倉時間(小時)
    
    # 動態調整參數
    volatility_sensitivity: float      # 波動敏感度
    trend_sensitivity: float          # 趨勢敏感度
    volume_sensitivity: float         # 成交量敏感度

class TimeframeWeightTemplates:
    """三週期權重模板管理器"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
        logger.info("✅ 三週期權重模板系統初始化完成")
    
    def _initialize_templates(self) -> Dict[TradingTimeframe, TimeframeWeightTemplate]:
        """初始化三種時間框架的權重模板"""
        templates = {}
        
        # ========== 短線權重模板 ==========
        short_term_weights = SignalBlockWeights(
            # 短線重視即時性和精準度
            precision_filter_weight=0.30,      # 最高權重：精準篩選
            market_condition_weight=0.20,      # 重視即時市場條件
            technical_analysis_weight=0.25,    # 重視技術信號
            
            # Phase 2: 機制適應 (中等權重)
            regime_analysis_weight=0.10,       # 短線較少考慮長期機制
            fear_greed_weight=0.08,            # 情緒指標作為輔助
            trend_alignment_weight=0.05,       # 趨勢確認權重較低
            
            # Phase 3: 高階指標 (較低權重)
            market_depth_weight=0.02,          # 市場深度輔助參考
            funding_rate_weight=0.00,          # 短線不考慮資金費率
            smart_money_weight=0.00            # 短線不考慮資金流向
        )
        
        templates[TradingTimeframe.SHORT_TERM] = TimeframeWeightTemplate(
            timeframe=TradingTimeframe.SHORT_TERM,
            template_name="短線快進快出模板",
            description="5分鐘-1小時持倉，重視精準度和即時性",
            signal_weights=short_term_weights,
            confidence_threshold=0.70,         # 高信心度要求
            risk_tolerance=0.8,               # 高風險容忍度
            position_size_multiplier=1.5,     # 較大倉位
            holding_period_hours=1,           # 1小時內平倉
            volatility_sensitivity=0.9,       # 高波動敏感度
            trend_sensitivity=0.6,            # 中等趨勢敏感度
            volume_sensitivity=0.8            # 高成交量敏感度
        )
        
        # ========== 中線權重模板 ==========
        medium_term_weights = SignalBlockWeights(
            # 中線平衡各項指標
            precision_filter_weight=0.22,      # 精準篩選仍重要
            market_condition_weight=0.18,      # 市場條件重要性
            technical_analysis_weight=0.20,    # 技術分析權重
            
            # Phase 2: 機制適應 (提高權重)
            regime_analysis_weight=0.15,       # 中線開始重視機制
            fear_greed_weight=0.12,            # 情緒指標更重要
            trend_alignment_weight=0.08,       # 趨勢確認增加
            
            # Phase 3: 高階指標 (適中權重)
            market_depth_weight=0.03,          # 開始考慮市場深度
            funding_rate_weight=0.01,          # 輕微考慮資金費率
            smart_money_weight=0.01           # 輕微考慮資金流向
        )
        
        templates[TradingTimeframe.MEDIUM_TERM] = TimeframeWeightTemplate(
            timeframe=TradingTimeframe.MEDIUM_TERM,
            template_name="中線平衡策略模板", 
            description="2-8小時持倉，平衡精準度與趨勢分析",
            signal_weights=medium_term_weights,
            confidence_threshold=0.60,         # 中等信心度要求
            risk_tolerance=0.6,               # 中等風險容忍度
            position_size_multiplier=1.2,     # 適中倉位
            holding_period_hours=4,           # 4小時平均持倉
            volatility_sensitivity=0.7,       # 中等波動敏感度
            trend_sensitivity=0.8,            # 高趨勢敏感度
            volume_sensitivity=0.6            # 中等成交量敏感度
        )
        
        # ========== 長線權重模板 ==========
        long_term_weights = SignalBlockWeights(
            # 長線重視趨勢和機制分析
            precision_filter_weight=0.15,      # 精準篩選權重降低
            market_condition_weight=0.12,      # 即時條件權重較低
            technical_analysis_weight=0.18,    # 技術分析依然重要
            
            # Phase 2: 機制適應 (最高權重)
            regime_analysis_weight=0.25,       # 長線最重視機制分析
            fear_greed_weight=0.15,            # 情緒指標高權重
            trend_alignment_weight=0.10,       # 趨勢確認很重要
            
            # Phase 3: 高階指標 (更高權重)
            market_depth_weight=0.03,          # 市場深度重要性增加
            funding_rate_weight=0.01,          # 資金費率考慮增加
            smart_money_weight=0.01           # 資金流向考慮增加
        )
        
        templates[TradingTimeframe.LONG_TERM] = TimeframeWeightTemplate(
            timeframe=TradingTimeframe.LONG_TERM,
            template_name="長線趨勢追蹤模板",
            description="1-3天持倉，重視趨勢分析和市場機制",
            signal_weights=long_term_weights,
            confidence_threshold=0.50,         # 較低信心度要求
            risk_tolerance=0.4,               # 較低風險容忍度
            position_size_multiplier=0.8,     # 較小倉位
            holding_period_hours=24,          # 24小時平均持倉
            volatility_sensitivity=0.5,       # 較低波動敏感度
            trend_sensitivity=0.9,            # 最高趨勢敏感度
            volume_sensitivity=0.4            # 較低成交量敏感度
        )
        
        return templates
    
    def get_template(self, timeframe: TradingTimeframe) -> Optional[TimeframeWeightTemplate]:
        """獲取指定時間框架的權重模板"""
        return self.templates.get(timeframe)
    
    def get_all_templates(self) -> Dict[TradingTimeframe, TimeframeWeightTemplate]:
        """獲取所有權重模板"""
        return self.templates.copy()
    
    def validate_all_templates(self) -> Dict[TradingTimeframe, bool]:
        """驗證所有模板的權重配置"""
        validation_results = {}
        
        for timeframe, template in self.templates.items():
            is_valid = template.signal_weights.validate_weights()
            total_weight = template.signal_weights.get_total_weight()
            
            validation_results[timeframe] = {
                "is_valid": is_valid,
                "total_weight": round(total_weight, 3),
                "template_name": template.template_name
            }
            
            if is_valid:
                logger.info(f"✅ {template.template_name} 權重驗證通過 (總權重: {total_weight:.3f})")
            else:
                logger.warning(f"⚠️ {template.template_name} 權重驗證失敗 (總權重: {total_weight:.3f})")
        
        return validation_results
    
    def get_adaptive_template(self, 
                            timeframe: TradingTimeframe, 
                            market_volatility: float,
                            trend_strength: float,
                            volume_strength: float) -> TimeframeWeightTemplate:
        """
        獲取市場條件自適應的權重模板
        
        Args:
            timeframe: 交易時間框架
            market_volatility: 市場波動率 (0.0-1.0)
            trend_strength: 趨勢強度 (0.0-1.0)  
            volume_strength: 成交量強度 (0.0-1.0)
        """
        base_template = self.get_template(timeframe)
        if not base_template:
            logger.error(f"❌ 找不到時間框架 {timeframe} 的基礎模板")
            return None
        
        # 創建自適應模板副本
        adaptive_template = TimeframeWeightTemplate(
            timeframe=base_template.timeframe,
            template_name=f"{base_template.template_name} (自適應)",
            description=f"{base_template.description} - 市場自適應調整",
            signal_weights=SignalBlockWeights(
                precision_filter_weight=base_template.signal_weights.precision_filter_weight,
                market_condition_weight=base_template.signal_weights.market_condition_weight,
                technical_analysis_weight=base_template.signal_weights.technical_analysis_weight,
                regime_analysis_weight=base_template.signal_weights.regime_analysis_weight,
                fear_greed_weight=base_template.signal_weights.fear_greed_weight,
                trend_alignment_weight=base_template.signal_weights.trend_alignment_weight,
                market_depth_weight=base_template.signal_weights.market_depth_weight,
                funding_rate_weight=base_template.signal_weights.funding_rate_weight,
                smart_money_weight=base_template.signal_weights.smart_money_weight
            ),
            confidence_threshold=base_template.confidence_threshold,
            risk_tolerance=base_template.risk_tolerance,
            position_size_multiplier=base_template.position_size_multiplier,
            holding_period_hours=base_template.holding_period_hours,
            volatility_sensitivity=base_template.volatility_sensitivity,
            trend_sensitivity=base_template.trend_sensitivity,
            volume_sensitivity=base_template.volume_sensitivity
        )
        
        # 🎯 市場條件自適應調整
        weights = adaptive_template.signal_weights
        
        # 高波動市場調整
        if market_volatility > 0.7:
            # 高波動時增加精準篩選和市場條件權重
            weights.precision_filter_weight *= 1.2
            weights.market_condition_weight *= 1.1
            weights.technical_analysis_weight *= 0.9
            logger.info(f"🌊 高波動調整: 精準篩選權重提升至 {weights.precision_filter_weight:.3f}")
        
        # 強趨勢市場調整
        if trend_strength > 0.8:
            # 強趨勢時增加趨勢相關權重
            weights.trend_alignment_weight *= 1.3
            weights.regime_analysis_weight *= 1.1
            weights.precision_filter_weight *= 0.95
            logger.info(f"📈 強趨勢調整: 趨勢權重提升至 {weights.trend_alignment_weight:.3f}")
        
        # 高成交量調整
        if volume_strength > 0.8:
            # 高成交量時增加技術分析權重
            weights.technical_analysis_weight *= 1.1
            weights.market_condition_weight *= 1.05
            logger.info(f"📊 高成交量調整: 技術分析權重提升至 {weights.technical_analysis_weight:.3f}")
        
        # 重新標準化權重 (確保總和為1.0)
        total_weight = weights.get_total_weight()
        if total_weight > 0:
            normalization_factor = 1.0 / total_weight
            
            weights.precision_filter_weight *= normalization_factor
            weights.market_condition_weight *= normalization_factor
            weights.technical_analysis_weight *= normalization_factor
            weights.regime_analysis_weight *= normalization_factor
            weights.fear_greed_weight *= normalization_factor
            weights.trend_alignment_weight *= normalization_factor
            weights.market_depth_weight *= normalization_factor
            weights.funding_rate_weight *= normalization_factor
            weights.smart_money_weight *= normalization_factor
            
            logger.info(f"⚖️ 權重標準化完成: {total_weight:.3f} → 1.000")
        
        return adaptive_template
    
    def export_template_summary(self) -> Dict:
        """導出模板配置摘要"""
        summary = {
            "template_count": len(self.templates),
            "templates": {},
            "validation_status": self.validate_all_templates()
        }
        
        for timeframe, template in self.templates.items():
            summary["templates"][timeframe.value] = {
                "name": template.template_name,
                "description": template.description,
                "confidence_threshold": template.confidence_threshold,
                "risk_tolerance": template.risk_tolerance,
                "position_size_multiplier": template.position_size_multiplier,
                "holding_period_hours": template.holding_period_hours,
                "weight_distribution": {
                    "precision_filter": template.signal_weights.precision_filter_weight,
                    "market_condition": template.signal_weights.market_condition_weight,
                    "technical_analysis": template.signal_weights.technical_analysis_weight,
                    "regime_analysis": template.signal_weights.regime_analysis_weight,
                    "fear_greed": template.signal_weights.fear_greed_weight,
                    "trend_alignment": template.signal_weights.trend_alignment_weight,
                    "market_depth": template.signal_weights.market_depth_weight,
                    "funding_rate": template.signal_weights.funding_rate_weight,
                    "smart_money": template.signal_weights.smart_money_weight
                }
            }
        
        return summary

# 全局實例
timeframe_templates = TimeframeWeightTemplates()
