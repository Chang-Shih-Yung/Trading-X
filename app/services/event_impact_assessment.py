#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Impact Assessment System
事件影響評估系統 - Phase 3 Week 2

這個模組提供精確的市場事件影響評估功能，包括：
- 量化事件對價格的影響
- 評估事件持續時間和衰減模式
- 計算不同資產的敏感度
- 提供影響預測和風險評估
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

# 設置日誌
logger = logging.getLogger(__name__)

class ImpactSeverity(Enum):
    """影響嚴重程度"""
    MINIMAL = "minimal"          # 最小影響 (<1%)
    LOW = "low"                  # 低影響 (1-3%)
    MODERATE = "moderate"        # 中等影響 (3-7%)
    HIGH = "high"               # 高影響 (7-15%)
    EXTREME = "extreme"         # 極端影響 (>15%)

class ImpactDirection(Enum):
    """影響方向"""
    BULLISH = "bullish"         # 利多
    BEARISH = "bearish"         # 利空  
    NEUTRAL = "neutral"         # 中性
    VOLATILE = "volatile"       # 增加波動

class ImpactTimeframe(Enum):
    """影響時間框架"""
    IMMEDIATE = "immediate"      # 即時 (0-1小時)
    SHORT_TERM = "short_term"   # 短期 (1-24小時)
    MEDIUM_TERM = "medium_term" # 中期 (1-7天)
    LONG_TERM = "long_term"     # 長期 (7-30天)

@dataclass
class ImpactMetrics:
    """影響指標"""
    price_impact_percent: float          # 價格影響百分比
    volatility_impact: float             # 波動率影響
    volume_impact: float                 # 成交量影響  
    duration_hours: float               # 影響持續時間
    confidence_score: float             # 預測信心分數
    
    # 詳細指標
    max_drawdown: float = 0.0           # 最大回撤
    recovery_time_hours: float = 0.0    # 恢復時間
    correlation_impact: float = 0.0     # 相關性影響
    liquidity_impact: float = 0.0       # 流動性影響

@dataclass
class AssetSensitivity:
    """資產敏感度分析"""
    symbol: str
    sensitivity_score: float            # 敏感度分數 (0-1)
    historical_beta: float              # 歷史貝塔值
    correlation_coefficient: float      # 相關係數
    volatility_multiplier: float        # 波動率乘數
    liquidity_adjustment: float         # 流動性調整
    
    # 時間框架敏感度
    immediate_sensitivity: float = 0.0
    short_term_sensitivity: float = 0.0
    medium_term_sensitivity: float = 0.0
    long_term_sensitivity: float = 0.0

@dataclass
class ImpactAssessment:
    """完整的影響評估結果"""
    event_id: str
    assessment_id: str
    timestamp: datetime
    
    # 基本評估
    overall_severity: ImpactSeverity
    primary_direction: ImpactDirection
    primary_timeframe: ImpactTimeframe
    
    # 定量指標
    impact_metrics: ImpactMetrics
    
    # 資產特定評估
    asset_assessments: Dict[str, ImpactMetrics] = field(default_factory=dict)
    asset_sensitivities: Dict[str, AssetSensitivity] = field(default_factory=dict)
    
    # 預測和建議
    risk_factors: List[str] = field(default_factory=list)
    mitigation_strategies: List[str] = field(default_factory=list)
    confidence_intervals: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    
    # 元數據
    model_version: str = "v1.0"
    data_quality_score: float = 1.0
    computation_time_ms: float = 0.0

class EventImpactAssessment:
    """事件影響評估引擎"""
    
    def __init__(self):
        self.assessment_history: Dict[str, ImpactAssessment] = {}
        self.sensitivity_cache: Dict[str, AssetSensitivity] = {}
        self.model_cache: Dict[str, Any] = {}
        self.computation_stats = {
            "total_assessments": 0,
            "successful_assessments": 0,
            "avg_computation_time_ms": 0.0,
            "last_assessment_time": None
        }
        
        # 初始化機器學習模型
        self._initialize_models()
        
        logger.info("EventImpactAssessment 引擎初始化完成")
    
    def _initialize_models(self):
        """初始化預測模型"""
        try:
            # 價格影響預測模型
            self.price_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            # 波動率影響預測模型
            self.volatility_model = RandomForestRegressor(
                n_estimators=50,
                max_depth=8,
                random_state=42
            )
            
            # 持續時間預測模型
            self.duration_model = LinearRegression()
            
            # 數據標準化器
            self.feature_scaler = StandardScaler()
            
            logger.info("機器學習模型初始化完成")
            
        except Exception as e:
            logger.error(f"模型初始化失敗: {e}")
    
    async def assess_event_impact(
        self,
        event_id: str,
        event_data: Dict[str, Any],
        target_symbols: List[str] = None,
        assessment_timeframe: ImpactTimeframe = ImpactTimeframe.MEDIUM_TERM
    ) -> Optional[ImpactAssessment]:
        """
        評估事件影響
        
        Args:
            event_id: 事件ID
            event_data: 事件數據
            target_symbols: 目標交易對列表
            assessment_timeframe: 評估時間框架
            
        Returns:
            ImpactAssessment: 影響評估結果
        """
        start_time = datetime.now()
        
        try:
            # 生成評估ID
            assessment_id = f"impact_{event_id}_{int(datetime.now().timestamp())}"
            
            # 默認目標資產
            if target_symbols is None:
                target_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT"]
            
            # 提取事件特徵
            event_features = await self._extract_event_features(event_data)
            
            # 獲取歷史相似事件
            similar_events = await self._find_similar_events(event_features)
            
            # 計算整體影響指標
            overall_metrics = await self._calculate_overall_impact(
                event_features, similar_events, assessment_timeframe
            )
            
            # 評估資產特定影響
            asset_assessments = {}
            asset_sensitivities = {}
            
            for symbol in target_symbols:
                # 計算資產敏感度
                sensitivity = await self._calculate_asset_sensitivity(
                    symbol, event_features, similar_events
                )
                asset_sensitivities[symbol] = sensitivity
                
                # 計算資產特定影響
                asset_impact = await self._calculate_asset_impact(
                    symbol, event_features, sensitivity, overall_metrics
                )
                asset_assessments[symbol] = asset_impact
            
            # 分析風險因子
            risk_factors = await self._analyze_risk_factors(
                event_features, asset_sensitivities
            )
            
            # 生成緩解策略
            mitigation_strategies = await self._generate_mitigation_strategies(
                overall_metrics, asset_assessments, risk_factors
            )
            
            # 計算信心區間
            confidence_intervals = await self._calculate_confidence_intervals(
                overall_metrics, asset_assessments
            )
            
            # 確定嚴重程度和方向
            severity = self._determine_impact_severity(overall_metrics.price_impact_percent)
            direction = self._determine_impact_direction(event_features, overall_metrics)
            
            # 計算執行時間
            computation_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # 創建評估結果
            assessment = ImpactAssessment(
                event_id=event_id,
                assessment_id=assessment_id,
                timestamp=start_time,
                overall_severity=severity,
                primary_direction=direction,
                primary_timeframe=assessment_timeframe,
                impact_metrics=overall_metrics,
                asset_assessments=asset_assessments,
                asset_sensitivities=asset_sensitivities,
                risk_factors=risk_factors,
                mitigation_strategies=mitigation_strategies,
                confidence_intervals=confidence_intervals,
                data_quality_score=await self._calculate_data_quality_score(event_features),
                computation_time_ms=computation_time
            )
            
            # 儲存評估結果
            self.assessment_history[assessment_id] = assessment
            
            # 更新統計信息
            self._update_stats(computation_time, True)
            
            logger.info(f"事件影響評估完成: {assessment_id}")
            return assessment
            
        except Exception as e:
            logger.error(f"事件影響評估失敗: {e}")
            self._update_stats(0, False)
            return None
    
    async def _extract_event_features(self, event_data: Dict[str, Any]) -> Dict[str, float]:
        """提取事件特徵向量"""
        try:
            features = {}
            
            # 基本特徵
            features['event_type_numeric'] = self._encode_event_type(event_data.get('event_type', ''))
            features['severity_score'] = self._encode_severity(event_data.get('severity', 'MEDIUM'))
            features['confidence'] = float(event_data.get('confidence', 0.5))
            
            # 時間特徵
            event_time = event_data.get('event_time')
            if isinstance(event_time, datetime):
                time_to_event = (event_time - datetime.now()).total_seconds() / 3600  # 小時
                features['time_to_event_hours'] = time_to_event
                features['is_immediate'] = 1.0 if abs(time_to_event) < 1 else 0.0
                features['is_future'] = 1.0 if time_to_event > 0 else 0.0
            
            # 市場條件特徵
            features['market_volatility'] = await self._get_current_market_volatility()
            features['market_sentiment'] = await self._get_market_sentiment_score()
            features['liquidity_condition'] = await self._get_liquidity_condition()
            
            # 影響範圍特徵
            affected_symbols = event_data.get('affected_symbols', [])
            features['affected_count'] = float(len(affected_symbols))
            features['includes_btc'] = 1.0 if 'BTCUSDT' in affected_symbols else 0.0
            features['includes_eth'] = 1.0 if 'ETHUSDT' in affected_symbols else 0.0
            
            return features
            
        except Exception as e:
            logger.error(f"特徵提取失敗: {e}")
            return {}
    
    def _encode_event_type(self, event_type: str) -> float:
        """編碼事件類型"""
        type_mapping = {
            'FOMC_MEETING': 0.9,
            'NFP_RELEASE': 0.8,
            'CPI_DATA': 0.7,
            'HALVING_EVENT': 0.95,
            'REGULATION_NEWS': 0.6,
            'FLASH_CRASH': 0.85,
            'WHALE_MOVEMENT': 0.5,
            'EXCHANGE_LISTING': 0.4,
            'PARTNERSHIP_NEWS': 0.3,
            'TECHNICAL_UPGRADE': 0.35
        }
        return type_mapping.get(event_type, 0.5)
    
    def _encode_severity(self, severity: str) -> float:
        """編碼嚴重程度"""
        severity_mapping = {
            'LOW': 0.2,
            'MEDIUM': 0.5,
            'HIGH': 0.8,
            'CRITICAL': 1.0
        }
        return severity_mapping.get(severity, 0.5)
    
    async def _get_current_market_volatility(self) -> float:
        """獲取當前市場波動率"""
        try:
            # 這裡應該連接到實時數據源
            # 暫時返回模擬值
            return np.random.normal(0.5, 0.2)
        except:
            return 0.5
    
    async def _get_market_sentiment_score(self) -> float:
        """獲取市場情緒分數"""
        try:
            # 這裡應該整合恐慌貪婪指數等指標
            return np.random.normal(0.5, 0.2)
        except:
            return 0.5
    
    async def _get_liquidity_condition(self) -> float:
        """獲取流動性條件"""
        try:
            # 這裡應該分析市場深度和交易量
            return np.random.normal(0.7, 0.15)
        except:
            return 0.7
    
    async def _find_similar_events(self, event_features: Dict[str, float]) -> List[Dict[str, Any]]:
        """尋找歷史相似事件"""
        try:
            # 這是一個簡化的實現
            # 在生產環境中，這應該查詢歷史數據庫
            similar_events = []
            
            # 模擬相似事件
            for i in range(3):
                similar_event = {
                    'event_id': f'historical_{i}',
                    'similarity_score': np.random.uniform(0.6, 0.9),
                    'price_impact': np.random.uniform(-0.15, 0.15),
                    'volatility_impact': np.random.uniform(0.1, 0.5),
                    'duration_hours': np.random.uniform(2, 48)
                }
                similar_events.append(similar_event)
            
            return similar_events
            
        except Exception as e:
            logger.error(f"相似事件搜尋失敗: {e}")
            return []
    
    async def _calculate_overall_impact(
        self,
        event_features: Dict[str, float],
        similar_events: List[Dict[str, Any]],
        timeframe: ImpactTimeframe
    ) -> ImpactMetrics:
        """計算整體影響指標"""
        try:
            # 基於歷史相似事件計算影響
            if similar_events:
                avg_price_impact = np.mean([e['price_impact'] for e in similar_events])
                avg_volatility_impact = np.mean([e['volatility_impact'] for e in similar_events])
                avg_duration = np.mean([e['duration_hours'] for e in similar_events])
            else:
                # 如果沒有相似事件，使用基於特徵的估算
                severity = event_features.get('severity_score', 0.5)
                confidence = event_features.get('confidence', 0.5)
                
                avg_price_impact = severity * 0.1 * (1 + confidence)
                avg_volatility_impact = severity * 0.3
                avg_duration = severity * 24  # 小時
            
            # 時間框架調整
            timeframe_multipliers = {
                ImpactTimeframe.IMMEDIATE: (1.2, 0.8, 0.5),    # (價格, 波動, 持續)
                ImpactTimeframe.SHORT_TERM: (1.0, 1.0, 1.0),
                ImpactTimeframe.MEDIUM_TERM: (0.8, 1.2, 2.0),
                ImpactTimeframe.LONG_TERM: (0.6, 0.9, 4.0)
            }
            
            price_mult, vol_mult, dur_mult = timeframe_multipliers[timeframe]
            
            # 創建影響指標
            metrics = ImpactMetrics(
                price_impact_percent=avg_price_impact * price_mult * 100,
                volatility_impact=avg_volatility_impact * vol_mult,
                volume_impact=np.random.uniform(0.2, 0.8),  # 簡化實現
                duration_hours=avg_duration * dur_mult,
                confidence_score=event_features.get('confidence', 0.5),
                max_drawdown=abs(avg_price_impact) * 1.5 * price_mult,
                recovery_time_hours=avg_duration * dur_mult * 0.7,
                correlation_impact=np.random.uniform(0.1, 0.4),
                liquidity_impact=event_features.get('liquidity_condition', 0.7)
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"整體影響計算失敗: {e}")
            # 返回默認指標
            return ImpactMetrics(
                price_impact_percent=0.0,
                volatility_impact=0.0,
                volume_impact=0.0,
                duration_hours=0.0,
                confidence_score=0.0
            )
    
    async def _calculate_asset_sensitivity(
        self,
        symbol: str,
        event_features: Dict[str, float],
        similar_events: List[Dict[str, Any]]
    ) -> AssetSensitivity:
        """計算資產敏感度"""
        try:
            # 檢查快取
            cache_key = f"{symbol}_{hash(str(event_features))}"
            if cache_key in self.sensitivity_cache:
                return self.sensitivity_cache[cache_key]
            
            # 資產特定因子
            asset_factors = {
                'BTCUSDT': {'beta': 1.0, 'base_sensitivity': 0.9},
                'ETHUSDT': {'beta': 1.2, 'base_sensitivity': 0.8},
                'ADAUSDT': {'beta': 1.5, 'base_sensitivity': 0.6},
                'SOLUSDT': {'beta': 1.8, 'base_sensitivity': 0.7},
                'BNBUSDT': {'beta': 1.1, 'base_sensitivity': 0.7}
            }
            
            factors = asset_factors.get(symbol, {'beta': 1.0, 'base_sensitivity': 0.5})
            
            # 計算敏感度分數
            base_sensitivity = factors['base_sensitivity']
            event_severity = event_features.get('severity_score', 0.5)
            includes_asset = 1.0 if symbol in event_features.get('affected_symbols', []) else 0.5
            
            sensitivity_score = min(base_sensitivity * event_severity * includes_asset, 1.0)
            
            # 計算相關係數
            correlation_coeff = np.random.uniform(0.6, 0.9) if symbol == 'BTCUSDT' else np.random.uniform(0.4, 0.8)
            
            # 時間框架敏感度
            immediate_sens = sensitivity_score * 1.2
            short_term_sens = sensitivity_score * 1.0
            medium_term_sens = sensitivity_score * 0.8
            long_term_sens = sensitivity_score * 0.6
            
            sensitivity = AssetSensitivity(
                symbol=symbol,
                sensitivity_score=sensitivity_score,
                historical_beta=factors['beta'],
                correlation_coefficient=correlation_coeff,
                volatility_multiplier=1.0 + sensitivity_score * 0.5,
                liquidity_adjustment=np.random.uniform(0.8, 1.2),
                immediate_sensitivity=min(immediate_sens, 1.0),
                short_term_sensitivity=min(short_term_sens, 1.0),
                medium_term_sensitivity=min(medium_term_sens, 1.0),
                long_term_sensitivity=min(long_term_sens, 1.0)
            )
            
            # 快取結果
            self.sensitivity_cache[cache_key] = sensitivity
            
            return sensitivity
            
        except Exception as e:
            logger.error(f"資產敏感度計算失敗 {symbol}: {e}")
            return AssetSensitivity(
                symbol=symbol,
                sensitivity_score=0.5,
                historical_beta=1.0,
                correlation_coefficient=0.5,
                volatility_multiplier=1.0,
                liquidity_adjustment=1.0
            )
    
    async def _calculate_asset_impact(
        self,
        symbol: str,
        event_features: Dict[str, float],
        sensitivity: AssetSensitivity,
        overall_metrics: ImpactMetrics
    ) -> ImpactMetrics:
        """計算資產特定影響"""
        try:
            # 基於敏感度調整整體影響
            sensitivity_mult = sensitivity.sensitivity_score
            
            asset_metrics = ImpactMetrics(
                price_impact_percent=overall_metrics.price_impact_percent * sensitivity_mult,
                volatility_impact=overall_metrics.volatility_impact * sensitivity.volatility_multiplier,
                volume_impact=overall_metrics.volume_impact * sensitivity.liquidity_adjustment,
                duration_hours=overall_metrics.duration_hours,
                confidence_score=overall_metrics.confidence_score * sensitivity.correlation_coefficient,
                max_drawdown=overall_metrics.max_drawdown * sensitivity_mult,
                recovery_time_hours=overall_metrics.recovery_time_hours / sensitivity.liquidity_adjustment,
                correlation_impact=overall_metrics.correlation_impact * sensitivity.correlation_coefficient,
                liquidity_impact=overall_metrics.liquidity_impact * sensitivity.liquidity_adjustment
            )
            
            return asset_metrics
            
        except Exception as e:
            logger.error(f"資產影響計算失敗 {symbol}: {e}")
            return overall_metrics  # 回退到整體指標
    
    async def _analyze_risk_factors(
        self,
        event_features: Dict[str, float],
        asset_sensitivities: Dict[str, AssetSensitivity]
    ) -> List[str]:
        """分析風險因子"""
        risk_factors = []
        
        try:
            # 市場風險
            if event_features.get('market_volatility', 0.5) > 0.7:
                risk_factors.append("高市場波動率環境")
            
            # 流動性風險
            if event_features.get('liquidity_condition', 0.7) < 0.4:
                risk_factors.append("流動性不足風險")
            
            # 相關性風險
            high_corr_assets = [s for s in asset_sensitivities.values() 
                              if s.correlation_coefficient > 0.8]
            if len(high_corr_assets) > 2:
                risk_factors.append("高相關性集中風險")
            
            # 時間風險
            if event_features.get('time_to_event_hours', 24) < 2:
                risk_factors.append("即時事件反應風險")
            
            # 信心風險
            if event_features.get('confidence', 0.5) < 0.6:
                risk_factors.append("事件預測不確定性")
            
            # 敏感度風險
            high_sens_count = sum(1 for s in asset_sensitivities.values() 
                                if s.sensitivity_score > 0.8)
            if high_sens_count > len(asset_sensitivities) * 0.5:
                risk_factors.append("高敏感度資產集中")
            
        except Exception as e:
            logger.error(f"風險因子分析失敗: {e}")
            risk_factors.append("風險分析異常")
        
        return risk_factors
    
    async def _generate_mitigation_strategies(
        self,
        overall_metrics: ImpactMetrics,
        asset_assessments: Dict[str, ImpactMetrics],
        risk_factors: List[str]
    ) -> List[str]:
        """生成緩解策略"""
        strategies = []
        
        try:
            # 基於整體影響的策略
            if abs(overall_metrics.price_impact_percent) > 5:
                strategies.append("考慮減少倉位規模以降低風險暴露")
            
            if overall_metrics.volatility_impact > 0.5:
                strategies.append("增加止損設置以管理波動風險")
            
            if overall_metrics.duration_hours > 24:
                strategies.append("準備長期持倉管理策略")
            
            # 基於資產特定影響的策略
            high_impact_assets = [symbol for symbol, metrics in asset_assessments.items()
                                if abs(metrics.price_impact_percent) > 7]
            if high_impact_assets:
                strategies.append(f"重點監控高影響資產: {', '.join(high_impact_assets)}")
            
            # 基於風險因子的策略
            if "高市場波動率環境" in risk_factors:
                strategies.append("在高波動環境中使用較小的倉位")
            
            if "流動性不足風險" in risk_factors:
                strategies.append("避免在流動性低的時段進行大額交易")
            
            if "即時事件反應風險" in risk_factors:
                strategies.append("準備快速反應機制以應對即時事件")
            
            # 通用策略
            if overall_metrics.confidence_score < 0.7:
                strategies.append("由於預測不確定性，採用保守交易策略")
            
            strategies.append("持續監控事件發展並準備調整策略")
            
        except Exception as e:
            logger.error(f"緩解策略生成失敗: {e}")
            strategies.append("建議諮詢風險管理專家")
        
        return strategies
    
    async def _calculate_confidence_intervals(
        self,
        overall_metrics: ImpactMetrics,
        asset_assessments: Dict[str, ImpactMetrics]
    ) -> Dict[str, Tuple[float, float]]:
        """計算信心區間"""
        intervals = {}
        
        try:
            # 整體價格影響信心區間
            price_impact = overall_metrics.price_impact_percent
            confidence = overall_metrics.confidence_score
            
            # 基於信心分數計算區間寬度
            interval_width = (1 - confidence) * abs(price_impact) * 2
            
            intervals['overall_price_impact'] = (
                price_impact - interval_width,
                price_impact + interval_width
            )
            
            # 資產特定信心區間
            for symbol, metrics in asset_assessments.items():
                asset_price_impact = metrics.price_impact_percent
                asset_confidence = metrics.confidence_score
                
                asset_interval_width = (1 - asset_confidence) * abs(asset_price_impact) * 2
                
                intervals[f'{symbol}_price_impact'] = (
                    asset_price_impact - asset_interval_width,
                    asset_price_impact + asset_interval_width
                )
            
            # 持續時間信心區間
            duration = overall_metrics.duration_hours
            duration_interval = duration * (1 - confidence) * 0.5
            intervals['duration_hours'] = (
                max(0, duration - duration_interval),
                duration + duration_interval
            )
            
        except Exception as e:
            logger.error(f"信心區間計算失敗: {e}")
            intervals['error'] = (0.0, 0.0)
        
        return intervals
    
    def _determine_impact_severity(self, price_impact_percent: float) -> ImpactSeverity:
        """確定影響嚴重程度"""
        abs_impact = abs(price_impact_percent)
        
        if abs_impact < 1:
            return ImpactSeverity.MINIMAL
        elif abs_impact < 3:
            return ImpactSeverity.LOW
        elif abs_impact < 7:
            return ImpactSeverity.MODERATE
        elif abs_impact < 15:
            return ImpactSeverity.HIGH
        else:
            return ImpactSeverity.EXTREME
    
    def _determine_impact_direction(
        self,
        event_features: Dict[str, float],
        metrics: ImpactMetrics
    ) -> ImpactDirection:
        """確定影響方向"""
        price_impact = metrics.price_impact_percent
        volatility_impact = metrics.volatility_impact
        
        if volatility_impact > 0.6 and abs(price_impact) < 2:
            return ImpactDirection.VOLATILE
        elif price_impact > 2:
            return ImpactDirection.BULLISH
        elif price_impact < -2:
            return ImpactDirection.BEARISH
        else:
            return ImpactDirection.NEUTRAL
    
    async def _calculate_data_quality_score(self, event_features: Dict[str, float]) -> float:
        """計算數據質量分數"""
        try:
            # 檢查特徵完整性
            required_features = ['event_type_numeric', 'severity_score', 'confidence']
            completeness = sum(1 for f in required_features if f in event_features) / len(required_features)
            
            # 檢查數據合理性
            confidence = event_features.get('confidence', 0.5)
            severity = event_features.get('severity_score', 0.5)
            
            reasonableness = 1.0
            if confidence < 0 or confidence > 1:
                reasonableness *= 0.8
            if severity < 0 or severity > 1:
                reasonableness *= 0.8
            
            # 綜合評分
            quality_score = (completeness * 0.6 + reasonableness * 0.4)
            return min(max(quality_score, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"數據質量評估失敗: {e}")
            return 0.5
    
    def _update_stats(self, computation_time_ms: float, success: bool):
        """更新統計信息"""
        self.computation_stats["total_assessments"] += 1
        if success:
            self.computation_stats["successful_assessments"] += 1
        
        # 更新平均計算時間
        current_avg = self.computation_stats["avg_computation_time_ms"]
        total = self.computation_stats["total_assessments"]
        new_avg = ((current_avg * (total - 1)) + computation_time_ms) / total
        self.computation_stats["avg_computation_time_ms"] = new_avg
        
        self.computation_stats["last_assessment_time"] = datetime.now()
    
    def get_assessment_by_id(self, assessment_id: str) -> Optional[ImpactAssessment]:
        """根據ID獲取評估結果"""
        return self.assessment_history.get(assessment_id)
    
    def get_recent_assessments(self, limit: int = 10) -> List[ImpactAssessment]:
        """獲取最近的評估結果"""
        assessments = list(self.assessment_history.values())
        assessments.sort(key=lambda x: x.timestamp, reverse=True)
        return assessments[:limit]
    
    def export_assessment_summary(self) -> Dict[str, Any]:
        """導出評估摘要"""
        return {
            "system_info": {
                "total_assessments": self.computation_stats["total_assessments"],
                "successful_assessments": self.computation_stats["successful_assessments"],
                "success_rate": (
                    self.computation_stats["successful_assessments"] / 
                    max(self.computation_stats["total_assessments"], 1)
                ),
                "avg_computation_time_ms": self.computation_stats["avg_computation_time_ms"],
                "last_assessment_time": self.computation_stats["last_assessment_time"]
            },
            "recent_assessments": [
                {
                    "assessment_id": assessment.assessment_id,
                    "event_id": assessment.event_id,
                    "timestamp": assessment.timestamp,
                    "severity": assessment.overall_severity.value,
                    "direction": assessment.primary_direction.value,
                    "price_impact": assessment.impact_metrics.price_impact_percent,
                    "confidence": assessment.impact_metrics.confidence_score
                }
                for assessment in self.get_recent_assessments(5)
            ],
            "sensitivity_cache_size": len(self.sensitivity_cache),
            "assessment_history_size": len(self.assessment_history)
        }

# 全局實例
event_impact_assessment = EventImpactAssessment()
