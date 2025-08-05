"""
🎯 Trading-X 後端策略系統整合器
=================================

四階段完整流水線系統
Phase 1: 信號生成與候選池 → Phase 2: 信號前處理層 → Phase 3: 執行決策層 → Phase 4: 分級輸出與監控
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import sys
from pathlib import Path

# 添加所有階段路徑
current_dir = Path(__file__).parent
sys.path.extend([
    str(current_dir / "shared_core"),
    str(current_dir / "phase1_signal_generation"),
    str(current_dir / "phase2_pre_evaluation"),
    str(current_dir / "phase3_execution_policy"),
    str(current_dir / "phase4_output_monitoring"),
    str(current_dir.parent.parent / "app" / "services")
])

# 導入各階段主要組件
from unified_signal_candidate_pool import unified_candidate_pool, SignalCandidate
from epl_pre_processing_system import pre_evaluation_layer, PreEvaluationResult
from epl_intelligent_decision_engine import execution_policy_layer, EPLDecisionResult
from multi_level_output_system import multi_level_output_system

logger = logging.getLogger(__name__)

@dataclass
class SystemPipelineResult:
    """系統流水線結果"""
    symbol: str
    phase1_candidates: List[SignalCandidate]
    phase2_evaluations: List[PreEvaluationResult]
    phase3_decisions: List[EPLDecisionResult]
    phase4_outputs: List[Dict[str, Any]]
    processing_time: float
    success_rate: float
    error_messages: List[str]
    timestamp: datetime

class TradingXBackendIntegrator:
    """Trading-X 後端策略系統整合器"""
    
    def __init__(self):
        # 四個階段的處理器
        self.phase1_generator = unified_candidate_pool
        self.phase2_preprocessor = pre_evaluation_layer
        self.phase3_decision_engine = execution_policy_layer
        self.phase4_output_system = multi_level_output_system
        
        # 系統狀態
        self.is_running = False
        self.processing_queue: List[str] = []
        self.system_stats = {
            "total_processed_symbols": 0,
            "successful_pipelines": 0,
            "failed_pipelines": 0,
            "average_processing_time": 0.0,
            "phase_success_rates": {
                "phase1": 0.0,
                "phase2": 0.0,
                "phase3": 0.0,
                "phase4": 0.0
            }
        }
        
        # 動態適應參數追蹤
        self.dynamic_adaptation_metrics = {
            "parameter_changes_per_hour": 0,
            "adaptation_success_rate": 0.0,
            "dynamic_feature_usage": {},
            "last_adaptation_check": datetime.now()
        }
    
    async def process_symbol_pipeline(self, symbol: str) -> SystemPipelineResult:
        """處理單一標的的完整流水線"""
        start_time = datetime.now()
        error_messages = []
        
        # 初始化結果容器
        phase1_candidates = []
        phase2_evaluations = []
        phase3_decisions = []
        phase4_outputs = []
        
        try:
            logger.info(f"🚀 開始處理完整流水線: {symbol}")
            
            # ═══════════════════════════════════════
            # Phase 1: 信號生成與候選池
            # ═══════════════════════════════════════
            try:
                logger.info(f"🎯 Phase 1: 信號生成 - {symbol}")
                phase1_candidates = await self.phase1_generator.generate_signal_candidates(symbol)
                
                if not phase1_candidates:
                    error_messages.append("Phase 1: 未生成任何信號候選者")
                    logger.warning(f"⚠️ Phase 1 無候選者: {symbol}")
                else:
                    logger.info(f"✅ Phase 1 完成: 生成 {len(phase1_candidates)} 個候選者")
                    
                    # 驗證動態特性
                    await self._verify_dynamic_characteristics(phase1_candidates)
                    
            except Exception as e:
                error_messages.append(f"Phase 1 錯誤: {e}")
                logger.error(f"❌ Phase 1 失敗: {symbol} - {e}")
            
            # ═══════════════════════════════════════
            # Phase 2: 信號前處理層 (EPL Pre-Processing)
            # ═══════════════════════════════════════
            if phase1_candidates:
                try:
                    logger.info(f"🧠 Phase 2: EPL前處理 - {symbol}")
                    
                    for candidate in phase1_candidates:
                        try:
                            pre_eval_result = await self.phase2_preprocessor.process_signal_candidate(candidate)
                            phase2_evaluations.append(pre_eval_result)
                            
                        except Exception as e:
                            error_messages.append(f"Phase 2 候選者處理錯誤: {e}")
                            logger.error(f"❌ Phase 2 候選者失敗: {candidate.id} - {e}")
                    
                    # 篩選通過EPL的候選者
                    passed_evaluations = [eval_result for eval_result in phase2_evaluations if eval_result.pass_to_epl]
                    
                    if passed_evaluations:
                        logger.info(f"✅ Phase 2 完成: {len(passed_evaluations)}/{len(phase2_evaluations)} 通過EPL")
                    else:
                        logger.warning(f"⚠️ Phase 2: 無候選者通過EPL篩選")
                        
                except Exception as e:
                    error_messages.append(f"Phase 2 整體錯誤: {e}")
                    logger.error(f"❌ Phase 2 整體失敗: {symbol} - {e}")
            
            # ═══════════════════════════════════════
            # Phase 3: 執行決策層 (EPL Decision Engine)
            # ═══════════════════════════════════════
            passed_evaluations = [eval_result for eval_result in phase2_evaluations if eval_result.pass_to_epl]
            
            if passed_evaluations:
                try:
                    logger.info(f"⚙️ Phase 3: EPL決策引擎 - {symbol}")
                    
                    for pre_eval_result in passed_evaluations:
                        try:
                            decision_result = await self.phase3_decision_engine.make_execution_decision(
                                pre_eval_result.candidate, pre_eval_result
                            )
                            phase3_decisions.append(decision_result)
                            
                        except Exception as e:
                            error_messages.append(f"Phase 3 決策錯誤: {e}")
                            logger.error(f"❌ Phase 3 決策失敗: {pre_eval_result.candidate.id} - {e}")
                    
                    if phase3_decisions:
                        logger.info(f"✅ Phase 3 完成: 生成 {len(phase3_decisions)} 個決策")
                        
                except Exception as e:
                    error_messages.append(f"Phase 3 整體錯誤: {e}")
                    logger.error(f"❌ Phase 3 整體失敗: {symbol} - {e}")
            
            # ═══════════════════════════════════════
            # Phase 4: 分級輸出與監控
            # ═══════════════════════════════════════
            if phase3_decisions:
                try:
                    logger.info(f"📊 Phase 4: 分級輸出監控 - {symbol}")
                    
                    for decision_result in phase3_decisions:
                        try:
                            output_result = await self.phase4_output_system.process_decision_output(decision_result)
                            phase4_outputs.append(output_result)
                            
                        except Exception as e:
                            error_messages.append(f"Phase 4 輸出錯誤: {e}")
                            logger.error(f"❌ Phase 4 輸出失敗: {decision_result.candidate.id} - {e}")
                    
                    if phase4_outputs:
                        logger.info(f"✅ Phase 4 完成: 處理 {len(phase4_outputs)} 個輸出")
                        
                except Exception as e:
                    error_messages.append(f"Phase 4 整體錯誤: {e}")
                    logger.error(f"❌ Phase 4 整體失敗: {symbol} - {e}")
            
            # 計算處理時間和成功率
            processing_time = (datetime.now() - start_time).total_seconds()
            success_rate = self._calculate_success_rate(phase1_candidates, phase2_evaluations, phase3_decisions, phase4_outputs)
            
            # 創建流水線結果
            pipeline_result = SystemPipelineResult(
                symbol=symbol,
                phase1_candidates=phase1_candidates,
                phase2_evaluations=phase2_evaluations,
                phase3_decisions=phase3_decisions,
                phase4_outputs=phase4_outputs,
                processing_time=processing_time,
                success_rate=success_rate,
                error_messages=error_messages,
                timestamp=datetime.now()
            )
            
            # 更新系統統計
            self._update_system_stats(pipeline_result)
            
            if success_rate > 0.5:  # 50%以上成功率視為成功
                logger.info(f"🎉 流水線處理成功: {symbol} (成功率: {success_rate:.1%}, 耗時: {processing_time:.2f}s)")
            else:
                logger.warning(f"⚠️ 流水線處理完成但成功率較低: {symbol} (成功率: {success_rate:.1%})")
            
            return pipeline_result
            
        except Exception as e:
            logger.error(f"💥 流水線處理嚴重失敗: {symbol} - {e}")
            error_messages.append(f"系統級錯誤: {e}")
            
            # 返回錯誤結果
            return SystemPipelineResult(
                symbol=symbol,
                phase1_candidates=[],
                phase2_evaluations=[],
                phase3_decisions=[],
                phase4_outputs=[],
                processing_time=(datetime.now() - start_time).total_seconds(),
                success_rate=0.0,
                error_messages=error_messages,
                timestamp=datetime.now()
            )
    
    async def _verify_dynamic_characteristics(self, candidates: List[SignalCandidate]):
        """驗證 Phase1+2 動態特性"""
        try:
            dynamic_features_found = []
            fixed_parameters_found = []
            
            for candidate in candidates:
                # 檢查動態參數
                dynamic_params = candidate.dynamic_params
                if dynamic_params:
                    for param_name, param_value in dynamic_params.items():
                        if "dynamic" in param_name.lower() or "adaptation" in param_name.lower():
                            dynamic_features_found.append(param_name)
                        
                        # 檢查是否有時間戳記 (動態特性指標)
                        if isinstance(param_value, dict) and "timestamp" in param_value:
                            dynamic_features_found.append(f"{param_name}_timestamped")
                        
                        # 檢查是否為固定值
                        if isinstance(param_value, (int, float)) and param_value in [10, 20, 14, 26]:  # 常見固定參數
                            fixed_parameters_found.append(f"{param_name}={param_value}")
            
            # 更新動態適應指標
            self.dynamic_adaptation_metrics["dynamic_feature_usage"] = {
                "features_found": list(set(dynamic_features_found)),
                "count": len(set(dynamic_features_found)),
                "fixed_parameters": fixed_parameters_found
            }
            
            # 驗證結果
            dynamic_score = len(set(dynamic_features_found)) / max(1, len(candidates))
            
            if dynamic_score > 0.8:
                logger.info(f"✅ 動態特性驗證通過: 動態分數 {dynamic_score:.2f}")
                self.dynamic_adaptation_metrics["adaptation_success_rate"] = dynamic_score
            elif dynamic_score > 0.5:
                logger.warning(f"⚠️ 動態特性部分符合: 動態分數 {dynamic_score:.2f}")
                self.dynamic_adaptation_metrics["adaptation_success_rate"] = dynamic_score
            else:
                logger.error(f"❌ 動態特性不足: 動態分數 {dynamic_score:.2f}, 發現固定參數: {fixed_parameters_found}")
                self.dynamic_adaptation_metrics["adaptation_success_rate"] = dynamic_score
            
        except Exception as e:
            logger.error(f"❌ 動態特性驗證失敗: {e}")
    
    def _calculate_success_rate(self, phase1_candidates: List, phase2_evaluations: List, 
                               phase3_decisions: List, phase4_outputs: List) -> float:
        """計算流水線成功率"""
        try:
            total_stages = 4
            successful_stages = 0
            
            if phase1_candidates:
                successful_stages += 1
            if phase2_evaluations and any(eval_result.pass_to_epl for eval_result in phase2_evaluations):
                successful_stages += 1
            if phase3_decisions:
                successful_stages += 1
            if phase4_outputs:
                successful_stages += 1
            
            return successful_stages / total_stages
            
        except Exception:
            return 0.0
    
    def _update_system_stats(self, pipeline_result: SystemPipelineResult):
        """更新系統統計"""
        try:
            self.system_stats["total_processed_symbols"] += 1
            
            if pipeline_result.success_rate > 0.5:
                self.system_stats["successful_pipelines"] += 1
            else:
                self.system_stats["failed_pipelines"] += 1
            
            # 更新平均處理時間
            total_processed = self.system_stats["total_processed_symbols"]
            current_avg = self.system_stats["average_processing_time"]
            new_avg = ((current_avg * (total_processed - 1)) + pipeline_result.processing_time) / total_processed
            self.system_stats["average_processing_time"] = new_avg
            
            # 更新各階段成功率
            if pipeline_result.phase1_candidates:
                self._update_phase_success_rate("phase1", True)
            else:
                self._update_phase_success_rate("phase1", False)
            
            if pipeline_result.phase2_evaluations:
                self._update_phase_success_rate("phase2", True)
            else:
                self._update_phase_success_rate("phase2", False)
            
            if pipeline_result.phase3_decisions:
                self._update_phase_success_rate("phase3", True)
            else:
                self._update_phase_success_rate("phase3", False)
            
            if pipeline_result.phase4_outputs:
                self._update_phase_success_rate("phase4", True)
            else:
                self._update_phase_success_rate("phase4", False)
            
        except Exception as e:
            logger.error(f"❌ 統計更新失敗: {e}")
    
    def _update_phase_success_rate(self, phase: str, success: bool):
        """更新階段成功率"""
        try:
            current_rate = self.system_stats["phase_success_rates"][phase]
            total_processed = self.system_stats["total_processed_symbols"]
            
            if total_processed == 1:
                new_rate = 1.0 if success else 0.0
            else:
                new_rate = ((current_rate * (total_processed - 1)) + (1.0 if success else 0.0)) / total_processed
            
            self.system_stats["phase_success_rates"][phase] = new_rate
            
        except Exception as e:
            logger.error(f"❌ 階段成功率更新失敗: {e}")
    
    async def process_multiple_symbols(self, symbols: List[str], concurrent_limit: int = 3) -> List[SystemPipelineResult]:
        """並行處理多個標的"""
        try:
            logger.info(f"🔄 開始並行處理 {len(symbols)} 個標的 (並行限制: {concurrent_limit})")
            
            semaphore = asyncio.Semaphore(concurrent_limit)
            
            async def process_with_semaphore(symbol: str) -> SystemPipelineResult:
                async with semaphore:
                    return await self.process_symbol_pipeline(symbol)
            
            # 並行執行
            tasks = [process_with_semaphore(symbol) for symbol in symbols]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 處理結果
            successful_results = []
            failed_count = 0
            
            for i, result in enumerate(results):
                if isinstance(result, SystemPipelineResult):
                    successful_results.append(result)
                else:
                    failed_count += 1
                    logger.error(f"❌ 標的 {symbols[i]} 處理異常: {result}")
            
            logger.info(f"✅ 並行處理完成: {len(successful_results)} 成功, {failed_count} 失敗")
            return successful_results
            
        except Exception as e:
            logger.error(f"❌ 並行處理失敗: {e}")
            return []
    
    async def start_continuous_monitoring(self, symbols: List[str], interval_minutes: int = 5):
        """啟動持續監控模式"""
        try:
            self.is_running = True
            logger.info(f"🔄 啟動持續監控: {len(symbols)} 個標的, 間隔 {interval_minutes} 分鐘")
            
            while self.is_running:
                try:
                    # 處理所有標的
                    results = await self.process_multiple_symbols(symbols)
                    
                    # 生成監控報告
                    monitoring_report = self._generate_monitoring_report(results)
                    logger.info(f"📊 監控週期完成: {monitoring_report['summary']}")
                    
                    # 等待下一個週期
                    await asyncio.sleep(interval_minutes * 60)
                    
                except Exception as e:
                    logger.error(f"❌ 監控週期錯誤: {e}")
                    await asyncio.sleep(60)  # 錯誤時等待1分鐘再重試
            
        except Exception as e:
            logger.error(f"❌ 持續監控啟動失敗: {e}")
    
    def stop_continuous_monitoring(self):
        """停止持續監控"""
        self.is_running = False
        logger.info("⏹️ 持續監控已停止")
    
    def _generate_monitoring_report(self, results: List[SystemPipelineResult]) -> Dict[str, Any]:
        """生成監控報告"""
        try:
            if not results:
                return {"summary": "無處理結果"}
            
            total_symbols = len(results)
            successful_symbols = sum(1 for r in results if r.success_rate > 0.5)
            
            # 統計各階段表現
            phase_stats = {
                "phase1_success": sum(1 for r in results if r.phase1_candidates),
                "phase2_success": sum(1 for r in results if r.phase2_evaluations),
                "phase3_success": sum(1 for r in results if r.phase3_decisions),
                "phase4_success": sum(1 for r in results if r.phase4_outputs)
            }
            
            # 平均處理時間
            avg_processing_time = sum(r.processing_time for r in results) / total_symbols
            
            # 錯誤統計
            total_errors = sum(len(r.error_messages) for r in results)
            
            report = {
                "summary": f"處理 {total_symbols} 標的, {successful_symbols} 成功, 平均耗時 {avg_processing_time:.2f}s",
                "total_symbols": total_symbols,
                "successful_symbols": successful_symbols,
                "success_rate": successful_symbols / total_symbols if total_symbols > 0 else 0,
                "phase_performance": phase_stats,
                "average_processing_time": avg_processing_time,
                "total_errors": total_errors,
                "timestamp": datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"❌ 監控報告生成失敗: {e}")
            return {"summary": f"報告生成錯誤: {e}"}
    
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        try:
            # 獲取各階段統計
            phase1_stats = self.phase1_generator.get_generation_stats()
            phase2_stats = self.phase2_preprocessor.get_processing_stats()
            phase3_stats = self.phase3_decision_engine.get_decision_stats()
            phase4_stats = self.phase4_output_system.get_system_statistics()
            
            status = {
                "system_info": {
                    "running": self.is_running,
                    "queue_size": len(self.processing_queue),
                    "last_update": datetime.now().isoformat()
                },
                "overall_stats": self.system_stats,
                "dynamic_adaptation": self.dynamic_adaptation_metrics,
                "phase_details": {
                    "phase1_signal_generation": phase1_stats,
                    "phase2_pre_evaluation": phase2_stats,
                    "phase3_execution_policy": phase3_stats,
                    "phase4_output_monitoring": phase4_stats
                },
                "performance_metrics": {
                    "total_pipeline_success_rate": (
                        self.system_stats["successful_pipelines"] / 
                        max(1, self.system_stats["total_processed_symbols"])
                    ),
                    "average_processing_time": self.system_stats["average_processing_time"],
                    "system_efficiency": self._calculate_system_efficiency()
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"❌ 系統狀態獲取失敗: {e}")
            return {"error": str(e), "status": "unavailable"}
    
    def _calculate_system_efficiency(self) -> float:
        """計算系統效率"""
        try:
            # 基於各階段成功率和處理時間計算效率
            phase_rates = list(self.system_stats["phase_success_rates"].values())
            avg_success_rate = sum(phase_rates) / len(phase_rates) if phase_rates else 0
            
            # 處理時間效率 (假設目標是30秒以內)
            time_efficiency = max(0, min(1, 30 / max(1, self.system_stats["average_processing_time"])))
            
            # 綜合效率
            system_efficiency = (avg_success_rate * 0.7) + (time_efficiency * 0.3)
            
            return system_efficiency
            
        except Exception:
            return 0.0
    
    async def run_system_diagnostics(self) -> Dict[str, Any]:
        """運行系統診斷"""
        try:
            logger.info("🔍 開始系統診斷...")
            
            diagnostic_results = {
                "phase1_test": await self._test_phase1(),
                "phase2_test": await self._test_phase2(),
                "phase3_test": await self._test_phase3(),
                "phase4_test": await self._test_phase4(),
                "integration_test": await self._test_integration(),
                "dynamic_characteristics_test": await self._test_dynamic_characteristics()
            }
            
            # 綜合診斷結果
            passed_tests = sum(1 for result in diagnostic_results.values() if result.get("status") == "passed")
            total_tests = len(diagnostic_results)
            
            overall_status = "healthy" if passed_tests == total_tests else "degraded" if passed_tests > total_tests // 2 else "critical"
            
            diagnostics = {
                "overall_status": overall_status,
                "passed_tests": passed_tests,
                "total_tests": total_tests,
                "test_results": diagnostic_results,
                "recommendations": self._generate_diagnostic_recommendations(diagnostic_results),
                "diagnostic_timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"🔍 系統診斷完成: {overall_status} ({passed_tests}/{total_tests} 通過)")
            return diagnostics
            
        except Exception as e:
            logger.error(f"❌ 系統診斷失敗: {e}")
            return {"overall_status": "error", "error": str(e)}
    
    async def _test_phase1(self) -> Dict[str, Any]:
        """測試 Phase1 信號生成"""
        try:
            test_symbol = "BTCUSDT"
            candidates = await self.phase1_generator.generate_signal_candidates(test_symbol)
            
            if candidates and len(candidates) > 0:
                return {"status": "passed", "candidates_generated": len(candidates)}
            else:
                return {"status": "failed", "reason": "未生成候選者"}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _test_phase2(self) -> Dict[str, Any]:
        """測試 Phase2 前處理"""
        try:
            # 創建測試候選者
            from unified_signal_candidate_pool import SignalCandidate, SignalSource, TechnicalIndicatorSnapshot, MarketEnvironmentSnapshot
            
            test_candidate = SignalCandidate(
                id="test_candidate",
                symbol="BTCUSDT",
                signal_strength=75.0,
                confidence=0.8,
                direction="BUY",
                source=SignalSource.PHASE1ABC_DYNAMIC,
                timestamp=datetime.now(),
                source_tag="test",
                priority_weight=1.0,
                technical_snapshot=TechnicalIndicatorSnapshot(
                    rsi=65.0, macd_signal=0.01, bollinger_position=0.6,
                    sma_20=50000, ema_12=50100, volume_sma_ratio=1.2,
                    atr=1500, stoch_k=60, williams_r=-35, timestamp=datetime.now()
                ),
                market_environment=MarketEnvironmentSnapshot(
                    volatility=0.02, volume_trend=0.1, momentum=0.05,
                    liquidity_score=0.8, funding_rate=0.001, order_book_imbalance=0.1,
                    timestamp=datetime.now()
                ),
                dynamic_params={"test_param": "dynamic_value"},
                adaptation_metrics={"test_metric": 0.9},
                data_completeness=1.0,
                signal_clarity=0.8
            )
            
            result = await self.phase2_preprocessor.process_signal_candidate(test_candidate)
            
            if result:
                return {"status": "passed", "epl_passed": result.pass_to_epl}
            else:
                return {"status": "failed", "reason": "前處理失敗"}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _test_phase3(self) -> Dict[str, Any]:
        """測試 Phase3 決策引擎"""
        try:
            # 簡化測試 - 檢查決策引擎統計
            stats = self.phase3_decision_engine.get_decision_stats()
            return {"status": "passed", "decision_engine_active": True, "stats": stats}
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _test_phase4(self) -> Dict[str, Any]:
        """測試 Phase4 輸出監控"""
        try:
            stats = self.phase4_output_system.get_system_statistics()
            notification_status = self.phase4_output_system.get_notification_status()
            
            return {
                "status": "passed",
                "output_system_active": True,
                "stats": stats,
                "notifications": notification_status
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _test_integration(self) -> Dict[str, Any]:
        """測試系統整合"""
        try:
            # 運行簡化的端到端測試
            test_result = await self.process_symbol_pipeline("BTCUSDT")
            
            if test_result.success_rate > 0:
                return {"status": "passed", "success_rate": test_result.success_rate}
            else:
                return {"status": "failed", "errors": test_result.error_messages}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _test_dynamic_characteristics(self) -> Dict[str, Any]:
        """測試動態特性"""
        try:
            adaptation_rate = self.dynamic_adaptation_metrics["adaptation_success_rate"]
            feature_count = len(self.dynamic_adaptation_metrics["dynamic_feature_usage"].get("features_found", []))
            
            if adaptation_rate > 0.5 and feature_count > 0:
                return {
                    "status": "passed",
                    "adaptation_rate": adaptation_rate,
                    "dynamic_features": feature_count
                }
            else:
                return {
                    "status": "failed",
                    "adaptation_rate": adaptation_rate,
                    "feature_count": feature_count
                }
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _generate_diagnostic_recommendations(self, test_results: Dict[str, Any]) -> List[str]:
        """生成診斷建議"""
        recommendations = []
        
        for test_name, result in test_results.items():
            if result.get("status") == "failed":
                if "phase1" in test_name:
                    recommendations.append("🔧 檢查 Phase1 信號生成器和數據連接")
                elif "phase2" in test_name:
                    recommendations.append("🔧 檢查 Phase2 前處理邏輯和閾值設定")
                elif "phase3" in test_name:
                    recommendations.append("🔧 檢查 Phase3 決策引擎和持倉管理")
                elif "phase4" in test_name:
                    recommendations.append("🔧 檢查 Phase4 通知系統和輸出配置")
                elif "integration" in test_name:
                    recommendations.append("🔧 檢查系統整合和數據流")
                elif "dynamic" in test_name:
                    recommendations.append("🔧 增強動態適應特性和參數調整機制")
            elif result.get("status") == "error":
                recommendations.append(f"❌ 修復 {test_name} 的系統錯誤")
        
        if not recommendations:
            recommendations.append("✅ 系統運行正常，無需特別維護")
        
        return recommendations

# 全局後端系統整合器實例
backend_integrator = TradingXBackendIntegrator()
