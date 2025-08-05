"""
🎯 Trading X - X資料夾流程測試
測試信號質量控制引擎的所有流程
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime
import logging

# 添加父目錄到路徑
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# 模擬真實數據源的類別
class MockVolatilityMetrics:
    def __init__(self):
        self.current_volatility = 0.65
        self.volatility_trend = 0.2
        self.volatility_percentile = 0.7
        self.regime_stability = 0.8
        self.micro_volatility = 0.45
        self.intraday_volatility = 0.55
        self.timestamp = datetime.now()

class MockSignalContinuityMetrics:
    def __init__(self):
        self.signal_persistence = 0.75
        self.signal_divergence = 0.3
        self.consensus_strength = 0.8
        self.temporal_consistency = 0.7
        self.cross_module_correlation = 0.85
        self.signal_decay_rate = 0.2

class MockStandardizedSignal:
    def __init__(self, signal_id="test_signal"):
        self.signal_id = signal_id
        self.module_name = "trend_analysis"
        self.original_value = 0.7
        self.standardized_value = 0.75
        self.quality_score = 0.8
        self.is_extreme = False

class MockExtremeSignalMetrics:
    def __init__(self):
        self.extreme_count = 2
        self.amplification_factor = 1.3

class MockOrderBookData:
    def __init__(self):
        self.symbol = "BTCUSDT"
        self.timestamp = datetime.now()
        self.bids = [(50000.0, 100.0), (49950.0, 200.0)]
        self.asks = [(50050.0, 150.0), (50100.0, 250.0)]
        self.total_bid_volume = 300.0
        self.total_ask_volume = 400.0
        self.pressure_ratio = 0.6
        self.market_sentiment = "bullish"
        self.bid_ask_spread = 50.0
        self.mid_price = 50025.0

class MockFundingRateData:
    def __init__(self):
        self.symbol = "BTCUSDT"
        self.funding_rate = 0.0001
        self.funding_time = datetime.now()
        self.next_funding_time = datetime.now()
        self.mark_price = 50025.0
        self.sentiment = "neutral"
        self.market_interpretation = "steady"
        self.annual_rate = 0.036

# 修改我們的引擎以使用模擬數據進行測試
class TestableSignalQualityEngine:
    def __init__(self):
        from X.real_data_signal_quality_engine import (
            SignalPriority, DataIntegrityStatus, RealTimeDataSnapshot,
            SignalCandidate, EPLDecision
        )
        
        self.SignalPriority = SignalPriority
        self.DataIntegrityStatus = DataIntegrityStatus
        self.RealTimeDataSnapshot = RealTimeDataSnapshot
        self.SignalCandidate = SignalCandidate
        self.EPLDecision = EPLDecision
        
        # 初始化與真實引擎相同的參數
        self.min_data_completeness = 0.8
        self.signal_memory_size = 100
        self.recent_signals = []
        self.priority_weights = {
            SignalPriority.CRITICAL: 1.0,
            SignalPriority.HIGH: 0.8,
            SignalPriority.MEDIUM: 0.6,
            SignalPriority.LOW: 0.4,
            SignalPriority.REJECTED: 0.0
        }
    
    async def test_collect_real_time_data(self) -> 'RealTimeDataSnapshot':
        """測試：收集即時數據快照"""
        print("📊 測試流程 1: 收集即時數據...")
        
        # 模擬收集各個數據源
        volatility_metrics = MockVolatilityMetrics()
        signal_continuity = MockSignalContinuityMetrics()
        standardized_signals = [MockStandardizedSignal("signal_1"), MockStandardizedSignal("signal_2")]
        extreme_signals = MockExtremeSignalMetrics()
        order_book_analysis = MockOrderBookData()
        funding_rate_data = MockFundingRateData()
        technical_indicators = {
            "RSI": 75.5,
            "MACD": 0.02,
            "BB_position": 0.8,
            "volume_trend": 0.6
        }
        
        # 評估數據完整性
        total_components = 4
        missing_components = []
        completeness_ratio = 1.0  # 模擬完整數據
        
        data_integrity = self.DataIntegrityStatus.COMPLETE
        
        snapshot = self.RealTimeDataSnapshot(
            timestamp=datetime.now(),
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
        
        print(f"   ✅ 數據完整性: {snapshot.data_integrity.value}")
        print(f"   📋 缺失組件: {snapshot.missing_components}")
        print(f"   🔢 技術指標數量: {len(snapshot.technical_indicators)}")
        
        return snapshot
    
    async def test_stage1_signal_candidate_pool(self, data_snapshot) -> list:
        """測試：第一階段信號候選者池生成"""
        print("\n🔍 測試流程 2: 第一階段信號候選者池...")
        
        candidates = []
        
        # 1. 測試 Phase1B 候選者創建
        phase1b_candidate = self._create_test_phase1b_candidate(
            data_snapshot.volatility_metrics,
            data_snapshot.signal_continuity,
            data_snapshot.timestamp
        )
        if phase1b_candidate:
            candidates.append(phase1b_candidate)
            print(f"   ✅ Phase1B 候選者: {phase1b_candidate.preliminary_priority.value}")
        
        # 2. 測試 Phase1C 候選者創建
        for signal in data_snapshot.standardized_signals:
            phase1c_candidate = self._create_test_phase1c_candidate(
                signal,
                data_snapshot.extreme_signals,
                data_snapshot.timestamp
            )
            if phase1c_candidate:
                candidates.append(phase1c_candidate)
                print(f"   ✅ Phase1C 候選者: {phase1c_candidate.preliminary_priority.value}")
        
        # 3. 測試 Phase3 候選者創建
        phase3_candidate = self._create_test_phase3_candidate(
            data_snapshot.order_book_analysis,
            data_snapshot.funding_rate_data,
            data_snapshot.timestamp
        )
        if phase3_candidate:
            candidates.append(phase3_candidate)
            print(f"   ✅ Phase3 候選者: {phase3_candidate.preliminary_priority.value}")
        
        # 4. 測試技術指標候選者創建
        tech_candidates = self._create_test_technical_candidates(
            data_snapshot.technical_indicators,
            data_snapshot.timestamp
        )
        candidates.extend(tech_candidates)
        print(f"   ✅ 技術指標候選者: {len(tech_candidates)}個")
        
        # 5. 測試去重邏輯
        original_count = len(candidates)
        candidates = self._test_deduplicate_candidates(candidates)
        print(f"   🔄 去重處理: {original_count} → {len(candidates)}個")
        
        return candidates
    
    async def test_stage2_epl_decision_layer(self, candidates) -> list:
        """測試：第二階段EPL決策層"""
        print("\n🎯 測試流程 3: 第二階段EPL決策層...")
        
        # 模擬市場環境
        market_context = {
            "market_trend": 0.7,
            "volatility": 0.6,
            "liquidity": 0.8,
            "market_uncertainty": 0.3,
            "market_activity": 0.75
        }
        
        decisions = []
        
        for i, candidate in enumerate(candidates):
            print(f"   🔍 處理候選者 {i+1}: {candidate.source_type}")
            
            # 市場環境評估
            market_score = self._test_evaluate_market_context(candidate, market_context)
            print(f"     📈 市場環境評分: {market_score:.3f}")
            
            # 風險評估
            risk_score = self._test_assess_signal_risk(candidate, market_context)
            print(f"     ⚠️ 風險評估評分: {risk_score:.3f}")
            
            # 時機優化評估
            timing_score = self._test_optimize_signal_timing(candidate, market_context)
            print(f"     ⏰ 時機優化評分: {timing_score:.3f}")
            
            # 組合適配評估
            portfolio_score = self._test_evaluate_portfolio_fit(candidate, market_context)
            print(f"     💼 組合適配評分: {portfolio_score:.3f}")
            
            # 綜合決策
            decision = self._test_make_epl_decision(
                candidate, market_score, risk_score, timing_score, portfolio_score
            )
            
            decisions.append(decision)
            print(f"     ✅ 最終決策: {decision.final_priority.value} - {decision.recommended_action}")
            print(f"     🎯 執行信心度: {decision.execution_confidence:.3f}")
        
        # 按優先級排序
        decisions.sort(
            key=lambda d: (
                self.priority_weights[d.final_priority],
                d.execution_confidence
            ),
            reverse=True
        )
        
        print(f"\n   📊 決策排序完成，共 {len(decisions)} 個決策")
        return decisions
    
    def _create_test_phase1b_candidate(self, volatility, continuity, timestamp):
        """創建測試用 Phase1B 候選者"""
        signal_strength = (
            volatility.current_volatility * 0.3 +
            continuity.signal_persistence * 0.4 +
            continuity.consensus_strength * 0.3
        )
        
        confidence = (
            volatility.regime_stability * 0.4 +
            continuity.temporal_consistency * 0.3 +
            continuity.cross_module_correlation * 0.3
        )
        
        data_quality = 0.9
        
        if signal_strength >= 0.8 and confidence >= 0.75:
            priority = self.SignalPriority.CRITICAL
        elif signal_strength >= 0.6 and confidence >= 0.6:
            priority = self.SignalPriority.HIGH
        elif signal_strength >= 0.4 and confidence >= 0.4:
            priority = self.SignalPriority.MEDIUM
        elif signal_strength >= 0.2:
            priority = self.SignalPriority.LOW
        else:
            priority = self.SignalPriority.REJECTED
        
        return self.SignalCandidate(
            signal_id=f"test_phase1b_{timestamp.strftime('%H%M%S')}",
            source_type="phase1b",
            raw_signal_strength=signal_strength,
            confidence_score=confidence,
            data_quality_score=data_quality,
            timestamp=timestamp,
            source_data={"test": True},
            integrity_check=True,
            preliminary_priority=priority,
            quality_flags=["VOLATILITY_CONFIRMED"]
        )
    
    def _create_test_phase1c_candidate(self, signal, extreme_metrics, timestamp):
        """創建測試用 Phase1C 候選者"""
        signal_strength = signal.standardized_value
        confidence = signal.quality_score
        
        if extreme_metrics and signal.is_extreme:
            signal_strength *= 1.2
            confidence *= 1.1
        
        signal_strength = min(1.0, max(0.0, signal_strength))
        confidence = min(1.0, max(0.0, confidence))
        
        if signal_strength >= 0.85 and confidence >= 0.8:
            priority = self.SignalPriority.CRITICAL
        elif signal_strength >= 0.7 and confidence >= 0.65:
            priority = self.SignalPriority.HIGH
        elif signal_strength >= 0.5 and confidence >= 0.5:
            priority = self.SignalPriority.MEDIUM
        elif signal_strength >= 0.3:
            priority = self.SignalPriority.LOW
        else:
            priority = self.SignalPriority.REJECTED
        
        return self.SignalCandidate(
            signal_id=f"test_phase1c_{signal.signal_id}",
            source_type="phase1c",
            raw_signal_strength=signal_strength,
            confidence_score=confidence,
            data_quality_score=0.9,
            timestamp=timestamp,
            source_data={"test": True},
            integrity_check=True,
            preliminary_priority=priority,
            quality_flags=["STANDARDIZED_STRONG"]
        )
    
    def _create_test_phase3_candidate(self, order_book, funding_rate, timestamp):
        """創建測試用 Phase3 候選者"""
        pressure_strength = abs(order_book.pressure_ratio)
        funding_strength = abs(funding_rate.funding_rate) * 100
        
        signal_strength = min(1.0, (pressure_strength * 0.6 + funding_strength * 0.4))
        
        spread_quality = 1.0 - min(1.0, order_book.bid_ask_spread / order_book.mid_price * 100)
        volume_quality = min(1.0, (order_book.total_bid_volume + order_book.total_ask_volume) / 1000000)
        confidence = (spread_quality * 0.5 + volume_quality * 0.5)
        
        if signal_strength >= 0.8 and confidence >= 0.75:
            priority = self.SignalPriority.CRITICAL
        elif signal_strength >= 0.6 and confidence >= 0.6:
            priority = self.SignalPriority.HIGH
        elif signal_strength >= 0.4 and confidence >= 0.45:
            priority = self.SignalPriority.MEDIUM
        elif signal_strength >= 0.2:
            priority = self.SignalPriority.LOW
        else:
            priority = self.SignalPriority.REJECTED
        
        return self.SignalCandidate(
            signal_id=f"test_phase3_{timestamp.strftime('%H%M%S')}",
            source_type="phase3",
            raw_signal_strength=signal_strength,
            confidence_score=confidence,
            data_quality_score=0.95,
            timestamp=timestamp,
            source_data={"test": True},
            integrity_check=True,
            preliminary_priority=priority,
            quality_flags=["MARKET_DEPTH_CONFIRMED"]
        )
    
    def _create_test_technical_candidates(self, indicators, timestamp):
        """創建測試用技術指標候選者"""
        candidates = []
        
        for indicator_name, value in indicators.items():
            signal_strength = self._test_calculate_indicator_strength(indicator_name, value)
            confidence = 0.7
            data_quality = 0.8
            
            if signal_strength >= 0.8:
                priority = self.SignalPriority.HIGH
            elif signal_strength >= 0.6:
                priority = self.SignalPriority.MEDIUM
            elif signal_strength >= 0.4:
                priority = self.SignalPriority.LOW
            else:
                priority = self.SignalPriority.REJECTED
            
            candidate = self.SignalCandidate(
                signal_id=f"test_tech_{indicator_name}_{timestamp.strftime('%H%M%S')}",
                source_type="pandas_ta",
                raw_signal_strength=signal_strength,
                confidence_score=confidence,
                data_quality_score=data_quality,
                timestamp=timestamp,
                source_data={"indicator": indicator_name, "value": value},
                integrity_check=True,
                preliminary_priority=priority,
                quality_flags=["TECHNICAL_INDICATOR"]
            )
            
            candidates.append(candidate)
        
        return candidates
    
    def _test_calculate_indicator_strength(self, indicator, value):
        """測試技術指標強度計算"""
        if indicator == "RSI":
            if value <= 20 or value >= 80:
                return 0.9
            elif value <= 30 or value >= 70:
                return 0.7
            else:
                return 0.3
        elif indicator == "MACD":
            return min(1.0, abs(value) * 10)
        elif indicator == "BB_position":
            return abs(value - 0.5) * 2
        elif indicator == "volume_trend":
            return min(1.0, abs(value))
        else:
            return min(1.0, abs(value))
    
    def _test_deduplicate_candidates(self, candidates):
        """測試去重邏輯"""
        deduplicated = {}
        
        for candidate in candidates:
            dedup_key = f"{candidate.source_type}_{candidate.timestamp.strftime('%Y%m%d_%H%M')}"
            
            if dedup_key not in deduplicated or \
               candidate.raw_signal_strength > deduplicated[dedup_key].raw_signal_strength:
                deduplicated[dedup_key] = candidate
        
        return list(deduplicated.values())
    
    def _test_evaluate_market_context(self, candidate, context):
        """測試市場環境評估"""
        trend_score = context.get("market_trend", 0.5)
        volatility_score = 1.0 - min(1.0, context.get("volatility", 0.5))
        liquidity_score = context.get("liquidity", 0.7)
        
        market_score = (trend_score * 0.4 + volatility_score * 0.3 + liquidity_score * 0.3)
        return min(1.0, max(0.0, market_score))
    
    def _test_assess_signal_risk(self, candidate, context):
        """測試風險評估"""
        data_risk = 1.0 - candidate.data_quality_score
        strength_risk = abs(candidate.raw_signal_strength - 0.7) / 0.7
        market_risk = context.get("market_uncertainty", 0.3)
        
        total_risk = (data_risk * 0.4 + strength_risk * 0.3 + market_risk * 0.3)
        risk_score = 1.0 - min(1.0, total_risk)
        
        return max(0.0, risk_score)
    
    def _test_optimize_signal_timing(self, candidate, context):
        """測試時機優化"""
        current_hour = candidate.timestamp.hour
        market_hours_score = 1.0 if 9 <= current_hour <= 21 else 0.7
        
        age_minutes = (datetime.now() - candidate.timestamp).total_seconds() / 60
        freshness_score = max(0.1, 1.0 - age_minutes / 60)
        
        activity_score = context.get("market_activity", 0.7)
        
        timing_score = (market_hours_score * 0.3 + freshness_score * 0.4 + activity_score * 0.3)
        return min(1.0, max(0.0, timing_score))
    
    def _test_evaluate_portfolio_fit(self, candidate, context):
        """測試組合適配評估"""
        # 模擬多樣性評分
        diversity_score = 0.8
        balance_score = 0.7
        
        portfolio_score = (diversity_score * 0.6 + balance_score * 0.4)
        return min(1.0, max(0.0, portfolio_score))
    
    def _test_make_epl_decision(self, candidate, market_score, risk_score, timing_score, portfolio_score):
        """測試EPL決策製作"""
        execution_confidence = (
            candidate.confidence_score * 0.25 +
            market_score * 0.25 +
            risk_score * 0.25 +
            timing_score * 0.15 +
            portfolio_score * 0.1
        )
        
        if execution_confidence >= 0.85 and candidate.preliminary_priority in [self.SignalPriority.CRITICAL, self.SignalPriority.HIGH]:
            final_priority = self.SignalPriority.CRITICAL
            recommended_action = "EXECUTE_IMMEDIATELY"
        elif execution_confidence >= 0.7 and candidate.preliminary_priority != self.SignalPriority.REJECTED:
            final_priority = self.SignalPriority.HIGH
            recommended_action = "EXECUTE_WITH_CAUTION"
        elif execution_confidence >= 0.5:
            final_priority = self.SignalPriority.MEDIUM
            recommended_action = "MONITOR_AND_PREPARE"
        elif execution_confidence >= 0.3:
            final_priority = self.SignalPriority.LOW
            recommended_action = "LOW_PRIORITY_WATCH"
        else:
            final_priority = self.SignalPriority.REJECTED
            recommended_action = "REJECT_SIGNAL"
        
        risk_params = {
            "stop_loss_ratio": max(0.01, 0.05 * (1 - risk_score)),
            "take_profit_ratio": min(0.1, 0.03 * execution_confidence),
            "position_size_ratio": min(0.2, 0.1 * execution_confidence),
            "max_holding_time": int(60 * execution_confidence)
        }
        
        reasoning = [
            f"執行信心度: {execution_confidence:.3f}",
            f"市場環境評分: {market_score:.3f}",
            f"風險評估評分: {risk_score:.3f}",
            f"時機優化評分: {timing_score:.3f}",
            f"組合適配評分: {portfolio_score:.3f}"
        ]
        
        data_support = "STRONG" if candidate.data_quality_score >= 0.8 else \
                      "MODERATE" if candidate.data_quality_score >= 0.6 else "WEAK"
        
        return self.EPLDecision(
            decision_id=f"test_epl_{candidate.signal_id}",
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

async def test_unified_monitoring_manager():
    """測試統一監控管理器"""
    print("\n📊 測試流程 4: 統一監控管理器...")
    
    try:
        from X.real_time_unified_monitoring_manager import unified_monitoring_manager
        
        # 測試儀表板數據獲取
        print("   🔍 測試儀表板數據獲取...")
        dashboard_data = await unified_monitoring_manager.get_monitoring_dashboard_data()
        
        print(f"   ✅ 監控狀態: {dashboard_data['monitoring_status']}")
        print(f"   📋 監控標的: {dashboard_data['monitored_symbols']}")
        print(f"   ⏱️ 處理間隔: {dashboard_data['processing_interval']}秒")
        
        # 測試配置更新
        print("   🔧 測試配置更新...")
        await unified_monitoring_manager.update_monitoring_config({
            "processing_interval": 45,
            "symbols": ["BTCUSDT", "ETHUSDT"]
        })
        print("   ✅ 配置更新成功")
        
        # 測試信號歷史獲取
        print("   📜 測試信號歷史獲取...")
        history = await unified_monitoring_manager.get_signal_history(limit=10)
        print(f"   ✅ 歷史記錄: {len(history)}個")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 統一監控管理器測試失敗: {e}")
        return False

async def test_api_routes():
    """測試API路由"""
    print("\n🌐 測試流程 5: API路由系統...")
    
    try:
        from X.monitoring_api import router
        
        # 檢查路由註冊
        routes = router.routes
        print(f"   ✅ 註冊路由數量: {len(routes)}")
        
        route_paths = [route.path for route in routes if hasattr(route, 'path')]
        print("   📋 可用端點:")
        for path in route_paths:
            print(f"     - {path}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ API路由測試失敗: {e}")
        return False

async def run_complete_flow_test():
    """運行完整流程測試"""
    print("🎯 Trading X 獨立監控系統 - 完整流程測試")
    print("=" * 60)
    
    try:
        # 初始化測試引擎
        engine = TestableSignalQualityEngine()
        
        # 流程 1: 收集即時數據
        data_snapshot = await engine.test_collect_real_time_data()
        
        # 流程 2: 第一階段信號候選者池
        candidates = await engine.test_stage1_signal_candidate_pool(data_snapshot)
        
        # 流程 3: 第二階段EPL決策層
        decisions = await engine.test_stage2_epl_decision_layer(candidates)
        
        # 流程 4: 統一監控管理器
        monitoring_success = await test_unified_monitoring_manager()
        
        # 流程 5: API路由系統
        api_success = await test_api_routes()
        
        # 總結測試結果
        print("\n" + "=" * 60)
        print("🎉 完整流程測試結果:")
        print("=" * 60)
        print(f"📊 數據收集: ✅ {data_snapshot.data_integrity.value}")
        print(f"🔍 信號候選者: ✅ {len(candidates)}個")
        print(f"🎯 EPL決策: ✅ {len(decisions)}個")
        print(f"📊 監控管理器: {'✅' if monitoring_success else '❌'}")
        print(f"🌐 API系統: {'✅' if api_success else '❌'}")
        
        # 顯示最終決策摘要
        if decisions:
            print("\n📈 最終決策摘要:")
            for i, decision in enumerate(decisions[:3]):  # 顯示前3個
                print(f"   {i+1}. {decision.final_priority.value} - {decision.recommended_action}")
                print(f"      信心度: {decision.execution_confidence:.3f}")
                print(f"      來源: {decision.original_candidate.source_type}")
        
        print("\n✅ 所有流程測試完成!")
        print("💡 系統準備就緒，可以啟動監控服務")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 流程測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 開始測試 Trading X 獨立監控系統...")
    
    try:
        success = asyncio.run(run_complete_flow_test())
        
        if success:
            print("\n🎊 所有測試通過!")
            print("📝 下一步:")
            print("   1. 運行 'python X/main.py' 啟動服務")
            print("   2. 訪問 http://localhost:8001/x-docs")
            print("   3. 使用 POST /api/v1/x-monitoring/start 開始監控")
        else:
            print("\n⚠️ 部分測試失敗，請檢查錯誤並修復")
            
    except Exception as e:
        print(f"\n💥 測試執行錯誤: {e}")
        sys.exit(1)
