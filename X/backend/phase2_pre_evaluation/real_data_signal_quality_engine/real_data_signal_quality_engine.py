"""
🎯 Trading X - 真實數據信號質量控制引擎
基於現有 Phase1ABC + Phase2+3 真實數據源的信號品質監控系統

真實數據源：
- Phase1B: app.services.phase1b_volatility_adaptation
- Phase1C: app.services.phase1c_signal_standardization  
- Phase3: app.services.phase3_market_analyzer
- pandas-ta 技術指標系統
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
import json

# 導入真實系統模組
from app.services.phase1b_volatility_adaptation import (
    VolatilityAdaptiveEngine, 
    VolatilityMetrics, 
    SignalContinuityMetrics
)
from app.services.phase1c_signal_standardization import (
    SignalStandardizationEngine,
    StandardizedSignal,
    ExtremeSignalMetrics
)
from app.services.phase3_market_analyzer import (
    Phase3MarketAnalyzer,
    OrderBookData,
    FundingRateData,
    Phase3Analysis
)
from app.services.pandas_ta_indicators import TechnicalIndicatorEngine
from app.services.signal_scoring_engine import signal_scoring_engine
from binance_data_connector import binance_connector

logger = logging.getLogger(__name__)

class SignalPriority(Enum):
    """信號優先級分類"""
    CRITICAL = "critical"        # 高質量確認信號
    HIGH = "high"               # 強信號
    MEDIUM = "medium"           # 中等信號
    LOW = "low"                 # 弱信號
    REJECTED = "rejected"       # 被拒絕信號

class DataIntegrityStatus(Enum):
    """數據完整性狀態"""
    COMPLETE = "complete"       # 數據完整
    PARTIAL = "partial"         # 數據部分缺失
    INCOMPLETE = "incomplete"   # 數據不完整
    INVALID = "invalid"         # 數據無效

@dataclass
class RealTimeDataSnapshot:
    """即時數據快照"""
    timestamp: datetime
    
    # Phase1B 波動適應數據
    volatility_metrics: Optional[VolatilityMetrics]
    signal_continuity: Optional[SignalContinuityMetrics]
    
    # Phase1C 標準化數據
    standardized_signals: List[StandardizedSignal]
    extreme_signals: Optional[ExtremeSignalMetrics]
    
    # Phase3 市場深度數據
    order_book_analysis: Optional[OrderBookData]
    funding_rate_data: Optional[FundingRateData]
    
    # pandas-ta 技術指標
    technical_indicators: Dict[str, float]
    
    # 數據完整性狀態
    data_integrity: DataIntegrityStatus
    missing_components: List[str]

@dataclass 
class SignalCandidate:
    """信號候選者 - 第一階段篩選"""
    signal_id: str
    source_type: str  # "phase1b", "phase1c", "phase3", "pandas_ta"
    raw_signal_strength: float
    confidence_score: float
    data_quality_score: float
    timestamp: datetime
    
    # 來源數據參考
    source_data: Dict[str, Any]
    integrity_check: bool
    
    # 初步評估
    preliminary_priority: SignalPriority
    quality_flags: List[str]

@dataclass
class EPLDecision:
    """執行策略層決定 - 第二階段決策"""
    decision_id: str
    original_candidate: SignalCandidate
    
    # EPL 決策參數
    market_context_score: float      # 市場環境評分
    risk_assessment_score: float     # 風險評估評分
    timing_optimization_score: float # 時機優化評分
    portfolio_fit_score: float       # 組合適配評分
    
    # 最終決策
    final_priority: SignalPriority
    execution_confidence: float
    recommended_action: str
    risk_management_params: Dict[str, Any]
    
    # 決策理由
    decision_reasoning: List[str]
    data_support_level: str

class RealDataSignalQualityEngine:
    """基於真實數據的信號質量控制引擎"""
    
    def __init__(self):
        # 初始化真實系統組件
        self.volatility_engine = VolatilityAdaptiveEngine()
        self.standardization_engine = SignalStandardizationEngine()
        self.phase3_analyzer = Phase3MarketAnalyzer()
        self.technical_engine = TechnicalIndicatorEngine()
        
        # 質量控制參數
        self.min_data_completeness = 0.8  # 最低數據完整性要求
        self.signal_memory_size = 100      # 信號記憶體大小
        self.recent_signals = []           # 近期信號記錄
        
        # 去重和優先級設定
        self.deduplication_window = timedelta(minutes=5)
        self.priority_weights = {
            SignalPriority.CRITICAL: 1.0,
            SignalPriority.HIGH: 0.8,
            SignalPriority.MEDIUM: 0.6,
            SignalPriority.LOW: 0.4,
            SignalPriority.REJECTED: 0.0
        }
        
    async def collect_real_time_data(self, symbol: str = "BTCUSDT") -> RealTimeDataSnapshot:
        """收集即時真實數據"""
        timestamp = datetime.now()
        missing_components = []
        
        try:
            # 1. 收集 Phase1B 波動適應數據
            volatility_metrics = None
            signal_continuity = None
            try:
                # 這裡應該呼叫真實的 Phase1B 數據
                price_data = await self._get_recent_price_data(symbol)
                volatility_metrics = self.volatility_engine.calculate_volatility_metrics(price_data)
                signal_continuity = self.volatility_engine.analyze_signal_continuity([])
            except Exception as e:
                logger.warning(f"Phase1B 數據收集失敗: {e}")
                missing_components.append("phase1b_data")
            
            # 2. 收集 Phase1C 標準化數據
            standardized_signals = []
            extreme_signals = None
            try:
                # 使用真實的標準化引擎
                raw_signals = await self._collect_raw_signals(symbol)
                standardized_signals = await self.standardization_engine.standardize_signals(raw_signals)
                extreme_signals = await self.standardization_engine.detect_extreme_signals(standardized_signals)
            except Exception as e:
                logger.warning(f"Phase1C 數據收集失敗: {e}")
                missing_components.append("phase1c_data")
            
            # 3. 收集 Phase3 市場深度數據
            order_book_analysis = None
            funding_rate_data = None
            try:
                phase3_data = await self.phase3_analyzer.analyze_market_depth(symbol)
                if phase3_data:
                    order_book_analysis = phase3_data.order_book
                    funding_rate_data = phase3_data.funding_rate
            except Exception as e:
                logger.warning(f"Phase3 數據收集失敗: {e}")
                missing_components.append("phase3_data")
            
            # 4. 收集 pandas-ta 技術指標 + 幣安實時數據增強
            technical_indicators = {}
            try:
                # 並行獲取技術指標和幣安市場數據
                async with binance_connector as connector:
                    market_data_task = connector.get_comprehensive_market_data(symbol)
                    technical_task = self.technical_engine.calculate_all_indicators(symbol)
                    
                    market_data, tech_indicators = await asyncio.gather(
                        market_data_task, technical_task, return_exceptions=True
                    )
                    
                    # 處理技術指標
                    if not isinstance(tech_indicators, Exception):
                        technical_indicators.update(tech_indicators)
                    
                    # 整合幣安實時數據到技術指標
                    if not isinstance(market_data, Exception) and market_data:
                        # 添加實時價格信息
                        technical_indicators["current_price"] = market_data.get("current_price", 0)
                        
                        # 添加24小時變動信息
                        ticker_24h = market_data.get("ticker_24h", {})
                        if ticker_24h:
                            technical_indicators["price_change_24h"] = float(ticker_24h.get("priceChangePercent", 0))
                            technical_indicators["volume_24h"] = float(ticker_24h.get("volume", 0))
                            technical_indicators["high_24h"] = float(ticker_24h.get("highPrice", 0))
                            technical_indicators["low_24h"] = float(ticker_24h.get("lowPrice", 0))
                        
                        # 添加波動性指標
                        volatility_metrics = market_data.get("volatility_metrics", {})
                        if volatility_metrics:
                            technical_indicators["volatility"] = volatility_metrics.get("current_volatility", 0)
                            technical_indicators["returns_std"] = volatility_metrics.get("returns_std", 0)
                        
                        # 添加成交量分析
                        volume_analysis = market_data.get("volume_analysis", {})
                        if volume_analysis:
                            technical_indicators["volume_trend"] = volume_analysis.get("volume_trend", 0)
                            technical_indicators["volume_ratio"] = volume_analysis.get("volume_ratio", 1)
                        
                        # 添加資金費率（期貨數據）
                        funding_rate = market_data.get("funding_rate", {})
                        if funding_rate:
                            technical_indicators["funding_rate"] = float(funding_rate.get("fundingRate", 0))
                        
                        # 添加訂單簿壓力
                        order_book = market_data.get("order_book", {})
                        if order_book and "bids" in order_book and "asks" in order_book:
                            bids = order_book["bids"][:5]
                            asks = order_book["asks"][:5]
                            bid_volume = sum(float(bid[1]) for bid in bids)
                            ask_volume = sum(float(ask[1]) for ask in asks)
                            
                            if bid_volume + ask_volume > 0:
                                technical_indicators["order_pressure"] = (bid_volume - ask_volume) / (bid_volume + ask_volume)
                                technical_indicators["total_book_volume"] = bid_volume + ask_volume
                        
                        logger.info(f"成功整合幣安實時數據到技術指標，總計 {len(technical_indicators)} 個指標")
                    
            except Exception as e:
                logger.warning(f"pandas-ta + 幣安數據收集失敗: {e}")
                missing_components.append("technical_indicators")
            
            # 判斷數據完整性
            total_components = 4
            missing_count = len(missing_components)
            completeness_ratio = (total_components - missing_count) / total_components
            
            if completeness_ratio >= 0.9:
                data_integrity = DataIntegrityStatus.COMPLETE
            elif completeness_ratio >= 0.7:
                data_integrity = DataIntegrityStatus.PARTIAL
            elif completeness_ratio >= 0.5:
                data_integrity = DataIntegrityStatus.INCOMPLETE
            else:
                data_integrity = DataIntegrityStatus.INVALID
            
            return RealTimeDataSnapshot(
                timestamp=timestamp,
                volatility_metrics=volatility_metrics,
                signal_continuity=signal_continuity,
                standardized_signals=standardized_signals,
                extreme_signals=extreme_signals,
                order_book_analysis=order_book_analysis,
                funding_rate_data=funding_rate_data,
                technical_indicators=technical_indicators,
                data_integrity=data_integrity,
                missing_components=missing_components
            )
            
        except Exception as e:
            logger.error(f"即時數據收集失敗: {e}")
            return RealTimeDataSnapshot(
                timestamp=timestamp,
                volatility_metrics=None,
                signal_continuity=None,
                standardized_signals=[],
                extreme_signals=None,
                order_book_analysis=None,
                funding_rate_data=None,
                technical_indicators={},
                data_integrity=DataIntegrityStatus.INVALID,
                missing_components=["all_components"]
            )
    
    async def stage1_signal_candidate_pool(self, data_snapshot: RealTimeDataSnapshot) -> List[SignalCandidate]:
        """第一階段：信號候選者池生成"""
        candidates = []
        
        # 檢查數據完整性
        if data_snapshot.data_integrity == DataIntegrityStatus.INVALID:
            logger.warning("數據完整性無效，跳過信號生成")
            return candidates
        
        # 1. Phase1B 波動適應信號
        if data_snapshot.volatility_metrics and data_snapshot.signal_continuity:
            candidate = self._create_phase1b_candidate(
                data_snapshot.volatility_metrics,
                data_snapshot.signal_continuity,
                data_snapshot.timestamp
            )
            if candidate:
                candidates.append(candidate)
        
        # 2. Phase1C 標準化信號
        for standardized_signal in data_snapshot.standardized_signals:
            candidate = self._create_phase1c_candidate(
                standardized_signal,
                data_snapshot.extreme_signals,
                data_snapshot.timestamp
            )
            if candidate:
                candidates.append(candidate)
        
        # 3. Phase3 市場深度信號
        if data_snapshot.order_book_analysis and data_snapshot.funding_rate_data:
            candidate = self._create_phase3_candidate(
                data_snapshot.order_book_analysis,
                data_snapshot.funding_rate_data,
                data_snapshot.timestamp
            )
            if candidate:
                candidates.append(candidate)
        
        # 4. pandas-ta 技術指標信號
        if data_snapshot.technical_indicators:
            tech_candidates = self._create_technical_candidates(
                data_snapshot.technical_indicators,
                data_snapshot.timestamp
            )
            candidates.extend(tech_candidates)
        
        # 去重處理
        candidates = self._deduplicate_candidates(candidates)
        
        logger.info(f"第一階段生成 {len(candidates)} 個信號候選者")
        return candidates
    
    async def stage2_epl_decision_layer(self, candidates: List[SignalCandidate], 
                                      market_context: Dict[str, Any]) -> List[EPLDecision]:
        """第二階段：執行策略層決策"""
        decisions = []
        
        for candidate in candidates:
            # 市場環境評估
            market_score = self._evaluate_market_context(candidate, market_context)
            
            # 風險評估
            risk_score = self._assess_signal_risk(candidate, market_context)
            
            # 時機優化評估
            timing_score = self._optimize_signal_timing(candidate, market_context)
            
            # 組合適配評估
            portfolio_score = self._evaluate_portfolio_fit(candidate, market_context)
            
            # 綜合決策計算
            decision = self._make_epl_decision(
                candidate, market_score, risk_score, timing_score, portfolio_score
            )
            
            decisions.append(decision)
        
        # 按優先級排序
        decisions.sort(
            key=lambda d: (
                self.priority_weights[d.final_priority],
                d.execution_confidence
            ),
            reverse=True
        )
        
        logger.info(f"第二階段產生 {len(decisions)} 個執行決策")
        return decisions
    
    def _create_phase1b_candidate(self, volatility: VolatilityMetrics, 
                                 continuity: SignalContinuityMetrics,
                                 timestamp: datetime) -> Optional[SignalCandidate]:
        """創建 Phase1B 信號候選者"""
        try:
            # 計算信號強度（基於波動性和連續性）
            signal_strength = (
                volatility.current_volatility * 0.3 +
                continuity.signal_persistence * 0.4 +
                continuity.consensus_strength * 0.3
            )
            
            # 信心評分
            confidence = (
                volatility.regime_stability * 0.4 +
                continuity.temporal_consistency * 0.3 +
                continuity.cross_module_correlation * 0.3
            )
            
            # 數據質量評分
            data_quality = min(1.0, (
                (1.0 if volatility.current_volatility > 0 else 0.0) +
                (1.0 if continuity.signal_persistence > 0 else 0.0) +
                (1.0 if continuity.consensus_strength > 0 else 0.0)
            ) / 3.0)
            
            # 初步優先級判斷
            if signal_strength >= 0.8 and confidence >= 0.75:
                priority = SignalPriority.CRITICAL
            elif signal_strength >= 0.6 and confidence >= 0.6:
                priority = SignalPriority.HIGH
            elif signal_strength >= 0.4 and confidence >= 0.4:
                priority = SignalPriority.MEDIUM
            elif signal_strength >= 0.2:
                priority = SignalPriority.LOW
            else:
                priority = SignalPriority.REJECTED
            
            return SignalCandidate(
                signal_id=f"phase1b_{timestamp.strftime('%Y%m%d_%H%M%S')}",
                source_type="phase1b",
                raw_signal_strength=signal_strength,
                confidence_score=confidence,
                data_quality_score=data_quality,
                timestamp=timestamp,
                source_data={
                    "volatility_metrics": asdict(volatility),
                    "continuity_metrics": asdict(continuity)
                },
                integrity_check=data_quality >= 0.7,
                preliminary_priority=priority,
                quality_flags=self._generate_quality_flags("phase1b", signal_strength, confidence)
            )
            
        except Exception as e:
            logger.error(f"Phase1B 候選者創建失敗: {e}")
            return None
    
    def _create_phase1c_candidate(self, signal: StandardizedSignal,
                                 extreme_metrics: Optional[ExtremeSignalMetrics],
                                 timestamp: datetime) -> Optional[SignalCandidate]:
        """創建 Phase1C 信號候選者"""
        try:
            # 使用標準化後的信號強度
            signal_strength = signal.standardized_value
            confidence = signal.quality_score
            
            # 考慮極端信號加成
            if extreme_metrics and signal.is_extreme:
                signal_strength *= 1.2  # 極端信號加成
                confidence *= 1.1
            
            # 限制在 0-1 範圍
            signal_strength = min(1.0, max(0.0, signal_strength))
            confidence = min(1.0, max(0.0, confidence))
            
            # 數據質量基於信號處理完整性
            data_quality = 0.9 if signal.standardized_value > 0 else 0.1
            
            # 優先級判斷
            if signal_strength >= 0.85 and confidence >= 0.8:
                priority = SignalPriority.CRITICAL
            elif signal_strength >= 0.7 and confidence >= 0.65:
                priority = SignalPriority.HIGH
            elif signal_strength >= 0.5 and confidence >= 0.5:
                priority = SignalPriority.MEDIUM
            elif signal_strength >= 0.3:
                priority = SignalPriority.LOW
            else:
                priority = SignalPriority.REJECTED
            
            return SignalCandidate(
                signal_id=f"phase1c_{signal.signal_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}",
                source_type="phase1c",
                raw_signal_strength=signal_strength,
                confidence_score=confidence,
                data_quality_score=data_quality,
                timestamp=timestamp,
                source_data={
                    "standardized_signal": asdict(signal),
                    "extreme_metrics": asdict(extreme_metrics) if extreme_metrics else None
                },
                integrity_check=data_quality >= 0.7,
                preliminary_priority=priority,
                quality_flags=self._generate_quality_flags("phase1c", signal_strength, confidence)
            )
            
        except Exception as e:
            logger.error(f"Phase1C 候選者創建失敗: {e}")
            return None
    
    def _create_phase3_candidate(self, order_book: OrderBookData,
                                funding_rate: FundingRateData,
                                timestamp: datetime) -> Optional[SignalCandidate]:
        """創建 Phase3 信號候選者"""
        try:
            # 基於市場深度和資金費率計算信號強度
            pressure_strength = abs(order_book.pressure_ratio)  # 市場壓力強度
            funding_strength = abs(funding_rate.funding_rate) * 100  # 資金費率強度
            
            # 綜合信號強度
            signal_strength = min(1.0, (pressure_strength * 0.6 + funding_strength * 0.4))
            
            # 信心評分基於數據可靠性
            spread_quality = 1.0 - min(1.0, order_book.bid_ask_spread / order_book.mid_price * 100)
            volume_quality = min(1.0, (order_book.total_bid_volume + order_book.total_ask_volume) / 1000000)
            confidence = (spread_quality * 0.5 + volume_quality * 0.5)
            
            # 數據質量
            data_quality = 0.95 if order_book.mid_price > 0 and funding_rate.mark_price > 0 else 0.1
            
            # 優先級判斷
            if signal_strength >= 0.8 and confidence >= 0.75:
                priority = SignalPriority.CRITICAL
            elif signal_strength >= 0.6 and confidence >= 0.6:
                priority = SignalPriority.HIGH
            elif signal_strength >= 0.4 and confidence >= 0.45:
                priority = SignalPriority.MEDIUM
            elif signal_strength >= 0.2:
                priority = SignalPriority.LOW
            else:
                priority = SignalPriority.REJECTED
            
            return SignalCandidate(
                signal_id=f"phase3_{timestamp.strftime('%Y%m%d_%H%M%S')}",
                source_type="phase3",
                raw_signal_strength=signal_strength,
                confidence_score=confidence,
                data_quality_score=data_quality,
                timestamp=timestamp,
                source_data={
                    "order_book": asdict(order_book),
                    "funding_rate": asdict(funding_rate)
                },
                integrity_check=data_quality >= 0.7,
                preliminary_priority=priority,
                quality_flags=self._generate_quality_flags("phase3", signal_strength, confidence)
            )
            
        except Exception as e:
            logger.error(f"Phase3 候選者創建失敗: {e}")
            return None
    
    def _create_technical_candidates(self, indicators: Dict[str, float],
                                   timestamp: datetime) -> List[SignalCandidate]:
        """創建 pandas-ta 技術指標候選者"""
        candidates = []
        
        # 主要技術指標信號
        key_indicators = {
            "RSI": indicators.get("RSI", 50),
            "MACD": indicators.get("MACD", 0),
            "BB_position": indicators.get("BB_position", 0.5),
            "volume_trend": indicators.get("volume_trend", 0)
        }
        
        for indicator_name, value in key_indicators.items():
            try:
                # 根據不同指標計算信號強度
                signal_strength = self._calculate_indicator_strength(indicator_name, value)
                confidence = 0.7  # 技術指標的基礎信心度
                data_quality = 0.8 if value != 0 else 0.2
                
                # 優先級判斷
                if signal_strength >= 0.8:
                    priority = SignalPriority.HIGH
                elif signal_strength >= 0.6:
                    priority = SignalPriority.MEDIUM
                elif signal_strength >= 0.4:
                    priority = SignalPriority.LOW
                else:
                    priority = SignalPriority.REJECTED
                
                candidate = SignalCandidate(
                    signal_id=f"tech_{indicator_name}_{timestamp.strftime('%Y%m%d_%H%M%S')}",
                    source_type="pandas_ta",
                    raw_signal_strength=signal_strength,
                    confidence_score=confidence,
                    data_quality_score=data_quality,
                    timestamp=timestamp,
                    source_data={
                        "indicator": indicator_name,
                        "value": value,
                        "all_indicators": indicators
                    },
                    integrity_check=data_quality >= 0.5,
                    preliminary_priority=priority,
                    quality_flags=self._generate_quality_flags("technical", signal_strength, confidence)
                )
                
                candidates.append(candidate)
                
            except Exception as e:
                logger.error(f"技術指標 {indicator_name} 候選者創建失敗: {e}")
                continue
        
        return candidates
    
    def _deduplicate_candidates(self, candidates: List[SignalCandidate]) -> List[SignalCandidate]:
        """去重信號候選者"""
        # 按來源類型和時間戳分組去重
        deduplicated = {}
        
        for candidate in candidates:
            # 創建去重鍵值
            dedup_key = f"{candidate.source_type}_{candidate.timestamp.strftime('%Y%m%d_%H%M')}"
            
            # 保留信號強度最高的候選者
            if dedup_key not in deduplicated or \
               candidate.raw_signal_strength > deduplicated[dedup_key].raw_signal_strength:
                deduplicated[dedup_key] = candidate
        
        return list(deduplicated.values())
    
    def _evaluate_market_context(self, candidate: SignalCandidate, context: Dict[str, Any]) -> float:
        """評估市場環境"""
        try:
            # 市場趨勢評分
            trend_score = context.get("market_trend", 0.5)
            
            # 波動性評分
            volatility_score = 1.0 - min(1.0, context.get("volatility", 0.5))
            
            # 流動性評分
            liquidity_score = context.get("liquidity", 0.7)
            
            # 綜合市場環境評分
            market_score = (trend_score * 0.4 + volatility_score * 0.3 + liquidity_score * 0.3)
            
            return min(1.0, max(0.0, market_score))
            
        except Exception as e:
            logger.error(f"市場環境評估失敗: {e}")
            return 0.5
    
    def _assess_signal_risk(self, candidate: SignalCandidate, context: Dict[str, Any]) -> float:
        """評估信號風險"""
        try:
            # 數據質量風險
            data_risk = 1.0 - candidate.data_quality_score
            
            # 信號強度風險（強度過低或過高都有風險）
            strength_risk = abs(candidate.raw_signal_strength - 0.7) / 0.7
            
            # 市場環境風險
            market_risk = context.get("market_uncertainty", 0.3)
            
            # 綜合風險評分（越低越好）
            total_risk = (data_risk * 0.4 + strength_risk * 0.3 + market_risk * 0.3)
            
            # 轉換為風險評分（越高越好）
            risk_score = 1.0 - min(1.0, total_risk)
            
            return max(0.0, risk_score)
            
        except Exception as e:
            logger.error(f"風險評估失敗: {e}")
            return 0.5
    
    def _optimize_signal_timing(self, candidate: SignalCandidate, context: Dict[str, Any]) -> float:
        """優化信號時機"""
        try:
            # 市場開放時間評分
            current_hour = candidate.timestamp.hour
            market_hours_score = 1.0 if 9 <= current_hour <= 21 else 0.7
            
            # 信號新鮮度評分
            age_minutes = (datetime.now() - candidate.timestamp).total_seconds() / 60
            freshness_score = max(0.1, 1.0 - age_minutes / 60)  # 1小時內有效
            
            # 市場活躍度評分
            activity_score = context.get("market_activity", 0.7)
            
            # 綜合時機評分
            timing_score = (market_hours_score * 0.3 + freshness_score * 0.4 + activity_score * 0.3)
            
            return min(1.0, max(0.0, timing_score))
            
        except Exception as e:
            logger.error(f"時機優化失敗: {e}")
            return 0.6
    
    def _evaluate_portfolio_fit(self, candidate: SignalCandidate, context: Dict[str, Any]) -> float:
        """評估組合適配度"""
        try:
            # 信號類型多樣性評分
            recent_types = [s.source_type for s in self.recent_signals[-10:]]
            diversity_score = 1.0 - (recent_types.count(candidate.source_type) / max(1, len(recent_types)))
            
            # 優先級平衡評分
            recent_priorities = [s.preliminary_priority for s in self.recent_signals[-10:]]
            balance_score = 0.8 if candidate.preliminary_priority not in recent_priorities[-3:] else 0.5
            
            # 組合適配評分
            portfolio_score = (diversity_score * 0.6 + balance_score * 0.4)
            
            return min(1.0, max(0.0, portfolio_score))
            
        except Exception as e:
            logger.error(f"組合適配評估失敗: {e}")
            return 0.7
    
    def _make_epl_decision(self, candidate: SignalCandidate, market_score: float,
                          risk_score: float, timing_score: float, 
                          portfolio_score: float) -> EPLDecision:
        """進行 EPL 最終決策"""
        
        # 綜合執行信心度計算
        execution_confidence = (
            candidate.confidence_score * 0.25 +
            market_score * 0.25 +
            risk_score * 0.25 +
            timing_score * 0.15 +
            portfolio_score * 0.1
        )
        
        # 最終優先級決策
        if execution_confidence >= 0.85 and candidate.preliminary_priority in [SignalPriority.CRITICAL, SignalPriority.HIGH]:
            final_priority = SignalPriority.CRITICAL
            recommended_action = "EXECUTE_IMMEDIATELY"
        elif execution_confidence >= 0.7 and candidate.preliminary_priority != SignalPriority.REJECTED:
            final_priority = SignalPriority.HIGH
            recommended_action = "EXECUTE_WITH_CAUTION"
        elif execution_confidence >= 0.5:
            final_priority = SignalPriority.MEDIUM
            recommended_action = "MONITOR_AND_PREPARE"
        elif execution_confidence >= 0.3:
            final_priority = SignalPriority.LOW
            recommended_action = "LOW_PRIORITY_WATCH"
        else:
            final_priority = SignalPriority.REJECTED
            recommended_action = "REJECT_SIGNAL"
        
        # 風險管理參數
        risk_params = {
            "stop_loss_ratio": max(0.01, 0.05 * (1 - risk_score)),
            "take_profit_ratio": min(0.1, 0.03 * execution_confidence),
            "position_size_ratio": min(0.2, 0.1 * execution_confidence),
            "max_holding_time": int(60 * execution_confidence)  # 分鐘
        }
        
        # 決策理由
        reasoning = [
            f"執行信心度: {execution_confidence:.3f}",
            f"市場環境評分: {market_score:.3f}",
            f"風險評估評分: {risk_score:.3f}",
            f"時機優化評分: {timing_score:.3f}",
            f"組合適配評分: {portfolio_score:.3f}"
        ]
        
        # 數據支撐水平
        data_support = "STRONG" if candidate.data_quality_score >= 0.8 else \
                      "MODERATE" if candidate.data_quality_score >= 0.6 else "WEAK"
        
        return EPLDecision(
            decision_id=f"epl_{candidate.signal_id}",
            original_candidate=candidate,
            market_context_score=market_score,
            risk_assessment_score=risk_score,
            timing_optimization_score=timing_score,
            portfolio_fit_score=portfolio_score,
            final_priority=final_priority,
            execution_confidence=execution_confidence,
            recommended_action=recommended_action,
            risk_management_params=risk_params,
            decision_reasoning=reasoning,
            data_support_level=data_support
        )
    
    def _generate_quality_flags(self, source_type: str, strength: float, confidence: float) -> List[str]:
        """生成質量標記"""
        flags = []
        
        if strength < 0.3:
            flags.append("WEAK_SIGNAL")
        elif strength > 0.9:
            flags.append("EXTREME_SIGNAL")
        
        if confidence < 0.4:
            flags.append("LOW_CONFIDENCE")
        elif confidence > 0.85:
            flags.append("HIGH_CONFIDENCE")
        
        if source_type == "phase1b" and strength > 0.7:
            flags.append("VOLATILITY_CONFIRMED")
        elif source_type == "phase1c" and strength > 0.8:
            flags.append("STANDARDIZED_STRONG")
        elif source_type == "phase3" and strength > 0.6:
            flags.append("MARKET_DEPTH_CONFIRMED")
        
        return flags
    
    def _calculate_indicator_strength(self, indicator: str, value: float) -> float:
        """計算技術指標強度"""
        try:
            if indicator == "RSI":
                if value <= 20 or value >= 80:
                    return 0.9  # 極端區域
                elif value <= 30 or value >= 70:
                    return 0.7  # 超買超賣
                else:
                    return 0.3  # 中性區域
            
            elif indicator == "MACD":
                return min(1.0, abs(value) * 10)  # MACD 絕對值越大信號越強
            
            elif indicator == "BB_position":
                return abs(value - 0.5) * 2  # 離中軸越遠信號越強
            
            elif indicator == "volume_trend":
                return min(1.0, abs(value))
            
            else:
                return min(1.0, abs(value))
                
        except Exception as e:
            logger.error(f"指標強度計算失敗 {indicator}: {e}")
            return 0.0
    
    async def _get_recent_price_data(self, symbol: str) -> List[float]:
        """獲取近期價格數據 - 僅使用真實幣安API"""
        try:
            async with binance_connector as connector:
                # 獲取最近100個1分鐘K線數據
                price_series = await connector.calculate_price_series(symbol, 100)
                
                if price_series and len(price_series) >= 5:
                    logger.info(f"成功獲取 {symbol} 真實價格數據: {len(price_series)} 個數據點")
                    return price_series
                else:
                    logger.error(f"價格數據不足或獲取失敗: {len(price_series) if price_series else 0}")
                    raise Exception("真實價格數據獲取失敗")
                        
        except Exception as e:
            logger.error(f"真實價格數據獲取失敗: {e}")
            raise Exception(f"無法獲取 {symbol} 的真實價格數據: {e}")
    
    async def _collect_raw_signals(self, symbol: str) -> List[Dict[str, Any]]:
        """收集原始信號 - 僅使用真實幣安市場數據"""
        try:
            async with binance_connector as connector:
                # 獲取綜合市場數據
                market_data = await connector.get_comprehensive_market_data(symbol)
                
                if not market_data or market_data.get("data_completeness", 0) < 0.5:
                    logger.error("市場數據不完整或獲取失敗")
                    raise Exception("真實市場數據獲取失敗")
                
                signals = []
                
                # 1. 基於24小時價格變動的趨勢信號
                ticker_24h = market_data.get("ticker_24h", {})
                if ticker_24h:
                    price_change_pct = float(ticker_24h.get("priceChangePercent", 0))
                    trend_strength = min(1.0, abs(price_change_pct) / 5.0)  # 5%變動為滿強度
                    trend_confidence = min(1.0, float(ticker_24h.get("volume", 0)) / 10000)  # 成交量信心度
                    
                    signals.append({
                        "module": "trend_24h",
                        "value": trend_strength * (1 if price_change_pct > 0 else -1),
                        "confidence": max(0.6, trend_confidence),
                        "source_data": {
                            "price_change_pct": price_change_pct,
                            "volume": ticker_24h.get("volume", 0)
                        }
                    })
                
                # 2. 基於波動性的動量信號
                volatility_metrics = market_data.get("volatility_metrics", {})
                if volatility_metrics:
                    volatility = volatility_metrics.get("current_volatility", 0)
                    momentum_strength = min(1.0, volatility * 20)  # 波動性轉換為動量強度
                    momentum_confidence = 0.8 if volatility > 0.005 else 0.6
                    
                    signals.append({
                        "module": "momentum_volatility",
                        "value": momentum_strength,
                        "confidence": momentum_confidence,
                        "source_data": volatility_metrics
                    })
                
                # 3. 基於訂單簿的壓力信號
                order_book = market_data.get("order_book", {})
                if order_book and "bids" in order_book and "asks" in order_book:
                    bids = order_book["bids"][:5]  # 前5檔買單
                    asks = order_book["asks"][:5]  # 前5檔賣單
                    
                    bid_volume = sum(float(bid[1]) for bid in bids)
                    ask_volume = sum(float(ask[1]) for ask in asks)
                    
                    if bid_volume + ask_volume > 0:
                        pressure_ratio = (bid_volume - ask_volume) / (bid_volume + ask_volume)
                        pressure_strength = abs(pressure_ratio)
                        pressure_confidence = min(1.0, (bid_volume + ask_volume) / 50)
                        
                        signals.append({
                            "module": "order_pressure",
                            "value": pressure_strength * (1 if pressure_ratio > 0 else -1),
                            "confidence": max(0.7, pressure_confidence),
                            "source_data": {
                                "bid_volume": bid_volume,
                                "ask_volume": ask_volume,
                                "pressure_ratio": pressure_ratio
                            }
                        })
                
                # 4. 基於資金費率的期貨信號
                funding_rate = market_data.get("funding_rate", {})
                if funding_rate and "fundingRate" in funding_rate:
                    funding_value = float(funding_rate["fundingRate"])
                    funding_strength = min(1.0, abs(funding_value) * 2000)  # 資金費率信號強度
                    funding_confidence = 0.9  # 資金費率數據通常很可靠
                    
                    signals.append({
                        "module": "funding_rate",
                        "value": funding_strength * (1 if funding_value > 0 else -1),
                        "confidence": funding_confidence,
                        "source_data": funding_rate
                    })
                
                # 5. 基於成交量趨勢的信號
                volume_analysis = market_data.get("volume_analysis", {})
                if volume_analysis:
                    volume_trend = volume_analysis.get("volume_trend", 0)
                    volume_strength = min(1.0, abs(volume_trend) * 2)
                    volume_confidence = 0.8
                    
                    signals.append({
                        "module": "volume_trend",
                        "value": volume_strength * (1 if volume_trend > 0 else -1),
                        "confidence": volume_confidence,
                        "source_data": volume_analysis
                    })
                
                if not signals:
                    logger.error("無法從真實市場數據生成有效信號")
                    raise Exception("信號生成失敗")
                
                logger.info(f"成功收集 {len(signals)} 個基於真實市場數據的信號")
                return signals
                    
        except Exception as e:
            logger.error(f"真實信號收集失敗: {e}")
            raise Exception(f"無法收集 {symbol} 的真實信號數據: {e}")

# 全局實例
real_data_engine = RealDataSignalQualityEngine()
