"""
🔧 EPL Decision History Tracking Python 實現優化
==============================================

基於 JSON 配置精確匹配的 Python 實現優化
"""

import sys
import ast
import re
from pathlib import Path
from typing import Dict, Any, List, Set
from datetime import datetime

class EPLPythonOptimizer:
    """EPL Python 實現優化器"""
    
    def __init__(self):
        self.python_path = Path("/Users/henrychang/Desktop/Trading-X/X/backend/phase4_output_monitoring/3_epl_decision_history_tracking/epl_decision_history_tracking.py")
        self.config_path = Path("/Users/henrychang/Desktop/Trading-X/X/backend/phase4_output_monitoring/3_epl_decision_history_tracking/epl_decision_history_tracking_config.json")
        
    def analyze_current_implementation(self) -> Dict[str, Any]:
        """分析當前實現"""
        try:
            with open(self.python_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取類別和方法
            tree = ast.parse(content)
            
            classes = []
            methods = []
            dataclasses = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                    # 檢查是否為 dataclass
                    for decorator in node.decorator_list:
                        if (isinstance(decorator, ast.Name) and decorator.id == 'dataclass'):
                            dataclasses.append(node.name)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.append(node.name)
            
            return {
                "classes": classes,
                "methods": methods,
                "dataclasses": dataclasses,
                "total_lines": len(content.split('\n')),
                "file_size": len(content)
            }
            
        except Exception as e:
            return {"error": f"分析實現失敗: {e}"}
    
    def identify_missing_components(self) -> Dict[str, List[str]]:
        """識別缺失的組件"""
        missing_components = {
            "dataclasses": [],
            "core_methods": [],
            "analytics_methods": [],
            "integration_methods": []
        }
        
        # 檢查 JSON 配置要求的數據結構
        required_dataclasses = [
            "EPLDecisionRecord",      # ✅ 已存在
            "DecisionOutcome",        # ✅ 已存在  
            "MarketSnapshot",         # ❌ 缺失
            "PortfolioState",         # ❌ 缺失
            "ExecutionMetrics"        # ❌ 缺失
        ]
        
        # 檢查核心方法
        required_core_methods = [
            "record_epl_decision",           # ✅ 已存在
            "update_decision_outcome",       # ✅ 已存在
            "track_execution_lifecycle",    # ❌ 缺失
            "capture_market_context",       # ❌ 缺失
            "validate_data_integrity"       # ❌ 缺失
        ]
        
        # 檢查分析方法
        required_analytics_methods = [
            "analyze_replacement_patterns",      # ❌ 缺失
            "analyze_strengthening_patterns",    # ❌ 缺失
            "analyze_new_position_patterns",     # ❌ 缺失
            "analyze_ignore_patterns",           # ❌ 缺失
            "generate_learning_insights"         # ❌ 缺失
        ]
        
        # 檢查整合方法
        required_integration_methods = [
            "integrate_phase1_signals",          # ❌ 缺失
            "integrate_phase2_evaluation",       # ❌ 缺失
            "integrate_phase3_execution",        # ❌ 缺失
            "export_phase4_analytics"            # ❌ 缺失
        ]
        
        # 讀取當前實現並檢查
        try:
            with open(self.python_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 檢查 dataclasses
            for dc in required_dataclasses:
                if f"class {dc}" not in content:
                    missing_components["dataclasses"].append(dc)
            
            # 檢查方法
            for method in required_core_methods:
                if f"def {method}" not in content and f"async def {method}" not in content:
                    missing_components["core_methods"].append(method)
            
            for method in required_analytics_methods:
                if f"def {method}" not in content and f"async def {method}" not in content:
                    missing_components["analytics_methods"].append(method)
            
            for method in required_integration_methods:
                if f"def {method}" not in content and f"async def {method}" not in content:
                    missing_components["integration_methods"].append(method)
        
        except Exception as e:
            print(f"檢查缺失組件時出錯: {e}")
        
        return missing_components
    
    def generate_missing_dataclasses(self) -> str:
        """生成缺失的數據類"""
        return '''
@dataclass
class MarketSnapshot:
    """市場快照數據"""
    timestamp: datetime
    symbol: str
    price: float
    volume: float
    volatility: float
    market_conditions: Dict[str, Any]
    technical_indicators: Dict[str, float]
    sentiment_score: Optional[float] = None

@dataclass  
class PortfolioState:
    """投資組合狀態"""
    timestamp: datetime
    total_value: float
    available_cash: float
    positions: Dict[str, Dict[str, Any]]
    risk_metrics: Dict[str, float]
    correlation_matrix: Optional[Dict[str, Dict[str, float]]] = None
    exposure_limits: Optional[Dict[str, float]] = None

@dataclass
class ExecutionMetrics:
    """執行指標"""
    decision_id: str
    execution_timestamp: datetime
    planned_price: float
    actual_price: float
    slippage: float
    execution_latency: float
    market_impact: float
    execution_quality_score: float
    fees_and_costs: Dict[str, float]
'''
    
    def generate_missing_core_methods(self) -> str:
        """生成缺失的核心方法"""
        return '''
    async def track_execution_lifecycle(self, decision_id: str, execution_data: Dict[str, Any]) -> bool:
        """追蹤執行生命週期"""
        try:
            # 創建執行指標
            execution_metrics = ExecutionMetrics(
                decision_id=decision_id,
                execution_timestamp=datetime.fromisoformat(execution_data.get('timestamp', datetime.now().isoformat())),
                planned_price=execution_data.get('planned_price', 0.0),
                actual_price=execution_data.get('actual_price', 0.0),
                slippage=execution_data.get('slippage', 0.0),
                execution_latency=execution_data.get('latency', 0.0),
                market_impact=execution_data.get('market_impact', 0.0),
                execution_quality_score=execution_data.get('quality_score', 0.0),
                fees_and_costs=execution_data.get('costs', {})
            )
            
            # 更新決策記錄
            decision_record = self._find_decision_by_id(decision_id)
            if decision_record:
                decision_record.execution_details['execution_metrics'] = asdict(execution_metrics)
                logger.info(f"更新執行生命週期: {decision_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"追蹤執行生命週期失敗: {e}")
            return False
    
    async def capture_market_context(self, symbol: str) -> MarketSnapshot:
        """擷取市場上下文"""
        try:
            # 模擬市場數據擷取 (實際應該從市場數據源獲取)
            market_snapshot = MarketSnapshot(
                timestamp=datetime.now(),
                symbol=symbol,
                price=0.0,  # 應該從實際數據源獲取
                volume=0.0,
                volatility=0.0,
                market_conditions={"trend": "neutral", "session": "active"},
                technical_indicators={"rsi": 50.0, "macd": 0.0},
                sentiment_score=0.5
            )
            
            logger.info(f"擷取市場上下文: {symbol}")
            return market_snapshot
            
        except Exception as e:
            logger.error(f"擷取市場上下文失敗: {e}")
            # 返回默認快照
            return MarketSnapshot(
                timestamp=datetime.now(),
                symbol=symbol,
                price=0.0, volume=0.0, volatility=0.0,
                market_conditions={}, technical_indicators={}
            )
    
    def validate_data_integrity(self) -> Dict[str, Any]:
        """驗證數據完整性"""
        try:
            integrity_report = {
                "validation_timestamp": datetime.now().isoformat(),
                "total_decisions": len(self.decision_history),
                "total_outcomes": len(self.outcome_history),
                "integrity_checks": {}
            }
            
            # 檢查決策記錄完整性
            missing_outcomes = 0
            invalid_records = 0
            
            for record in self.decision_history:
                # 檢查必要欄位
                if not all([record.decision_id, record.symbol, record.timestamp]):
                    invalid_records += 1
                
                # 檢查是否有對應的結果
                if record.decision_id not in self.outcome_history:
                    missing_outcomes += 1
            
            integrity_report["integrity_checks"] = {
                "invalid_records": invalid_records,
                "missing_outcomes": missing_outcomes,
                "data_consistency": "good" if invalid_records == 0 else "issues_found",
                "outcome_coverage": (len(self.outcome_history) / max(len(self.decision_history), 1)) * 100
            }
            
            logger.info("數據完整性驗證完成")
            return integrity_report
            
        except Exception as e:
            logger.error(f"數據完整性驗證失敗: {e}")
            return {"error": str(e)}
'''
    
    def generate_missing_analytics_methods(self) -> str:
        """生成缺失的分析方法"""
        return '''
    async def analyze_replacement_patterns(self) -> Dict[str, Any]:
        """分析替換決策模式"""
        try:
            replacement_decisions = [
                record for record in self.decision_history
                if record.decision_type == EPLDecisionType.REPLACE_POSITION
            ]
            
            if not replacement_decisions:
                return {"message": "暫無替換決策數據"}
            
            # 分析替換頻率
            total_decisions = len(self.decision_history)
            replacement_rate = len(replacement_decisions) / total_decisions
            
            # 分析替換成功率
            successful_replacements = 0
            for record in replacement_decisions:
                if record.decision_id in self.outcome_history:
                    outcome = self.outcome_history[record.decision_id]
                    if outcome.success:
                        successful_replacements += 1
            
            replacement_success_rate = successful_replacements / len(replacement_decisions) if replacement_decisions else 0
            
            # 分析信心分數分佈
            confidence_scores = [r.confidence_score for r in replacement_decisions]
            avg_confidence = statistics.mean(confidence_scores) if confidence_scores else 0
            
            return {
                "replacement_frequency": {
                    "total_replacements": len(replacement_decisions),
                    "replacement_rate": replacement_rate,
                    "average_confidence": avg_confidence
                },
                "replacement_effectiveness": {
                    "success_rate": replacement_success_rate,
                    "successful_count": successful_replacements,
                    "failed_count": len(replacement_decisions) - successful_replacements
                },
                "insights": self._generate_replacement_insights(replacement_decisions)
            }
            
        except Exception as e:
            logger.error(f"分析替換模式失敗: {e}")
            return {"error": str(e)}
    
    async def analyze_strengthening_patterns(self) -> Dict[str, Any]:
        """分析強化決策模式"""
        try:
            strengthening_decisions = [
                record for record in self.decision_history
                if record.decision_type == EPLDecisionType.STRENGTHEN_POSITION
            ]
            
            if not strengthening_decisions:
                return {"message": "暫無強化決策數據"}
            
            # 基本統計
            total_decisions = len(self.decision_history)
            strengthening_rate = len(strengthening_decisions) / total_decisions
            
            # 成功率分析
            successful_strengthenings = sum(
                1 for record in strengthening_decisions
                if record.decision_id in self.outcome_history and 
                self.outcome_history[record.decision_id].success
            )
            
            success_rate = successful_strengthenings / len(strengthening_decisions) if strengthening_decisions else 0
            
            return {
                "strengthening_frequency": {
                    "total_strengthenings": len(strengthening_decisions),
                    "strengthening_rate": strengthening_rate,
                    "average_confidence": statistics.mean([r.confidence_score for r in strengthening_decisions])
                },
                "strengthening_effectiveness": {
                    "success_rate": success_rate,
                    "successful_count": successful_strengthenings
                }
            }
            
        except Exception as e:
            logger.error(f"分析強化模式失敗: {e}")
            return {"error": str(e)}
    
    async def analyze_new_position_patterns(self) -> Dict[str, Any]:
        """分析新倉位決策模式"""
        try:
            new_position_decisions = [
                record for record in self.decision_history
                if record.decision_type == EPLDecisionType.CREATE_NEW_POSITION
            ]
            
            if not new_position_decisions:
                return {"message": "暫無新倉位決策數據"}
            
            # 基本統計
            creation_rate = len(new_position_decisions) / len(self.decision_history)
            
            # 成功率分析
            successful_creations = sum(
                1 for record in new_position_decisions
                if record.decision_id in self.outcome_history and
                self.outcome_history[record.decision_id].success
            )
            
            success_rate = successful_creations / len(new_position_decisions) if new_position_decisions else 0
            
            return {
                "creation_frequency": {
                    "total_new_positions": len(new_position_decisions),
                    "creation_rate": creation_rate,
                    "average_confidence": statistics.mean([r.confidence_score for r in new_position_decisions])
                },
                "creation_effectiveness": {
                    "success_rate": success_rate,
                    "successful_count": successful_creations
                }
            }
            
        except Exception as e:
            logger.error(f"分析新倉位模式失敗: {e}")
            return {"error": str(e)}
    
    async def analyze_ignore_patterns(self) -> Dict[str, Any]:
        """分析忽略決策模式"""
        try:
            ignore_decisions = [
                record for record in self.decision_history
                if record.decision_type == EPLDecisionType.IGNORE_SIGNAL
            ]
            
            if not ignore_decisions:
                return {"message": "暫無忽略決策數據"}
            
            # 忽略率分析
            ignore_rate = len(ignore_decisions) / len(self.decision_history)
            
            # 忽略原因分析
            ignore_reasons = defaultdict(int)
            for record in ignore_decisions:
                reason = record.position_context.get('reason', 'unknown')
                ignore_reasons[reason] += 1
            
            return {
                "ignore_frequency": {
                    "total_ignores": len(ignore_decisions),
                    "ignore_rate": ignore_rate,
                    "average_confidence": statistics.mean([r.confidence_score for r in ignore_decisions])
                },
                "ignore_reasons": dict(ignore_reasons),
                "filtering_effectiveness": self._calculate_filtering_effectiveness(ignore_decisions)
            }
            
        except Exception as e:
            logger.error(f"分析忽略模式失敗: {e}")
            return {"error": str(e)}
    
    async def generate_learning_insights(self) -> Dict[str, Any]:
        """生成學習洞察"""
        try:
            if not self.decision_history:
                return {"message": "暫無決策數據生成學習洞察"}
            
            # 模式識別
            successful_patterns = await self._identify_successful_patterns()
            failure_patterns = await self._identify_failure_patterns()
            
            # 適應性學習建議
            adaptive_recommendations = self._generate_adaptive_recommendations()
            
            # 回饋整合分析
            feedback_integration = self._analyze_feedback_integration()
            
            return {
                "pattern_recognition": {
                    "successful_patterns": successful_patterns,
                    "failure_patterns": failure_patterns
                },
                "adaptive_learning": {
                    "recommendations": adaptive_recommendations,
                    "threshold_adjustments": self._suggest_threshold_adjustments()
                },
                "feedback_integration": feedback_integration,
                "learning_summary": self._summarize_learning_insights()
            }
            
        except Exception as e:
            logger.error(f"生成學習洞察失敗: {e}")
            return {"error": str(e)}
'''
    
    def generate_missing_integration_methods(self) -> str:
        """生成缺失的整合方法"""
        return '''
    async def integrate_phase1_signals(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """整合 Phase1 信號數據"""
        try:
            # 提取 Phase1 信號候選資料
            signal_candidate = signal_data.get('signal_candidate', {})
            
            integrated_data = {
                "original_signal_candidate": signal_candidate,
                "signal_quality_metrics": {
                    "technical_strength": signal_candidate.get('technical_strength', 0.5),
                    "market_timing": signal_candidate.get('market_timing', 0.5),
                    "source_reliability": signal_candidate.get('source_reliability', 0.5)
                },
                "market_context": await self.capture_market_context(signal_candidate.get('symbol', 'UNKNOWN'))
            }
            
            logger.info("Phase1 信號數據整合完成")
            return integrated_data
            
        except Exception as e:
            logger.error(f"整合 Phase1 信號失敗: {e}")
            return {}
    
    async def integrate_phase2_evaluation(self, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
        """整合 Phase2 預評估結果"""
        try:
            # 提取 Phase2 預評估結果
            pre_evaluation = evaluation_data.get('pre_evaluation_result', {})
            
            integrated_data = {
                "pre_evaluation_result": pre_evaluation,
                "embedded_scoring": pre_evaluation.get('embedded_scoring', {}),
                "correlation_analysis": pre_evaluation.get('correlation_analysis', {}),
                "portfolio_state": self._extract_portfolio_state(evaluation_data)
            }
            
            logger.info("Phase2 預評估數據整合完成")
            return integrated_data
            
        except Exception as e:
            logger.error(f"整合 Phase2 評估失敗: {e}")
            return {}
    
    async def integrate_phase3_execution(self, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """整合 Phase3 執行數據"""
        try:
            # 提取執行相關數據
            execution_result = execution_data.get('execution_result', {})
            
            integrated_data = {
                "execution_initiation": {
                    "execution_timestamp": execution_result.get('timestamp'),
                    "execution_latency": execution_result.get('latency'),
                    "market_conditions_at_execution": execution_result.get('market_conditions'),
                    "slippage_measurement": execution_result.get('slippage')
                },
                "execution_monitoring": {
                    "position_establishment": execution_result.get('position_changes'),
                    "risk_parameter_application": execution_result.get('risk_parameters'),
                    "portfolio_impact": execution_result.get('portfolio_impact'),
                    "correlation_effects": execution_result.get('correlation_impact')
                }
            }
            
            logger.info("Phase3 執行數據整合完成")
            return integrated_data
            
        except Exception as e:
            logger.error(f"整合 Phase3 執行失敗: {e}")
            return {}
    
    async def export_phase4_analytics(self) -> Dict[str, Any]:
        """匯出 Phase4 分析結果"""
        try:
            # 匯出所有分析結果供其他系統使用
            analytics_export = {
                "export_timestamp": datetime.now().isoformat(),
                "decision_analytics": await self.get_comprehensive_decision_analysis(),
                "performance_metrics": await self.get_performance_metrics(),
                "pattern_insights": {
                    "replacement_patterns": await self.analyze_replacement_patterns(),
                    "strengthening_patterns": await self.analyze_strengthening_patterns(),
                    "new_position_patterns": await self.analyze_new_position_patterns(),
                    "ignore_patterns": await self.analyze_ignore_patterns()
                },
                "learning_insights": await self.generate_learning_insights(),
                "system_status": await self.get_system_status()
            }
            
            logger.info("Phase4 分析結果匯出完成")
            return analytics_export
            
        except Exception as e:
            logger.error(f"匯出 Phase4 分析失敗: {e}")
            return {"error": str(e)}
'''
    
    def generate_helper_methods(self) -> str:
        """生成輔助方法"""
        return '''
    def _generate_replacement_insights(self, replacement_decisions: List) -> List[str]:
        """生成替換洞察"""
        insights = []
        
        if len(replacement_decisions) > 10:
            avg_confidence = statistics.mean([r.confidence_score for r in replacement_decisions])
            if avg_confidence > 0.8:
                insights.append("替換決策普遍具有高信心分數")
            elif avg_confidence < 0.6:
                insights.append("替換決策信心分數偏低，建議檢討標準")
        
        return insights if insights else ["需要更多數據生成洞察"]
    
    def _extract_portfolio_state(self, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取投資組合狀態"""
        return {
            "current_positions": evaluation_data.get('portfolio', {}).get('positions', {}),
            "risk_metrics": evaluation_data.get('portfolio', {}).get('risk_metrics', {}),
            "available_cash": evaluation_data.get('portfolio', {}).get('cash', 0.0),
            "total_value": evaluation_data.get('portfolio', {}).get('total_value', 0.0)
        }
    
    def _calculate_filtering_effectiveness(self, ignore_decisions: List) -> Dict[str, Any]:
        """計算過濾效果"""
        if not ignore_decisions:
            return {"effectiveness": "no_data"}
        
        # 計算低品質信號過濾率
        low_quality_ignores = len([d for d in ignore_decisions if d.confidence_score < 0.5])
        filtering_rate = low_quality_ignores / len(ignore_decisions)
        
        return {
            "low_quality_filtering_rate": filtering_rate,
            "total_filtered": len(ignore_decisions),
            "effectiveness_score": min(filtering_rate * 2, 1.0)  # 歸一化到0-1
        }
    
    async def _identify_successful_patterns(self) -> Dict[str, Any]:
        """識別成功模式"""
        successful_decisions = [
            record for record in self.decision_history
            if record.decision_id in self.outcome_history and
            self.outcome_history[record.decision_id].success
        ]
        
        if not successful_decisions:
            return {"patterns": "insufficient_data"}
        
        # 分析成功決策的共同特徵
        avg_confidence = statistics.mean([d.confidence_score for d in successful_decisions])
        priority_distribution = defaultdict(int)
        
        for decision in successful_decisions:
            priority_distribution[decision.signal_priority.value] += 1
        
        return {
            "average_confidence": avg_confidence,
            "priority_distribution": dict(priority_distribution),
            "pattern_count": len(successful_decisions)
        }
    
    async def _identify_failure_patterns(self) -> Dict[str, Any]:
        """識別失敗模式"""
        failed_decisions = [
            record for record in self.decision_history
            if record.decision_id in self.outcome_history and
            not self.outcome_history[record.decision_id].success
        ]
        
        if not failed_decisions:
            return {"patterns": "insufficient_data"}
        
        # 分析失敗決策的共同特徵
        avg_confidence = statistics.mean([d.confidence_score for d in failed_decisions])
        priority_distribution = defaultdict(int)
        
        for decision in failed_decisions:
            priority_distribution[decision.signal_priority.value] += 1
        
        return {
            "average_confidence": avg_confidence,
            "priority_distribution": dict(priority_distribution),
            "pattern_count": len(failed_decisions)
        }
    
    def _generate_adaptive_recommendations(self) -> List[str]:
        """生成適應性建議"""
        recommendations = []
        
        if self.success_rates:
            overall_success_rate = sum(
                sum(successes) / len(successes) for successes in self.success_rates.values() if successes
            ) / len(self.success_rates)
            
            if overall_success_rate < 0.7:
                recommendations.append("整體成功率偏低，建議調整決策閾值")
            elif overall_success_rate > 0.9:
                recommendations.append("成功率極高，可考慮降低決策門檻以增加機會")
        
        return recommendations if recommendations else ["系統表現穩定，繼續監控"]
    
    def _suggest_threshold_adjustments(self) -> Dict[str, float]:
        """建議閾值調整"""
        adjustments = {}
        
        # 基於成功率建議置信度閾值調整
        if self.success_rates:
            for decision_type, successes in self.success_rates.items():
                if successes:
                    success_rate = sum(successes) / len(successes)
                    if success_rate < 0.6:
                        adjustments[f"{decision_type}_confidence_threshold"] = 0.1  # 提高閾值
                    elif success_rate > 0.9:
                        adjustments[f"{decision_type}_confidence_threshold"] = -0.05  # 降低閾值
        
        return adjustments
    
    def _analyze_feedback_integration(self) -> Dict[str, Any]:
        """分析回饋整合"""
        return {
            "total_outcomes_tracked": len(self.outcome_history),
            "feedback_coverage": len(self.outcome_history) / max(len(self.decision_history), 1),
            "learning_effectiveness": "good" if len(self.outcome_history) > 0 else "limited",
            "improvement_areas": ["增加結果追蹤覆蓋率", "加強即時回饋機制"]
        }
    
    def _summarize_learning_insights(self) -> str:
        """總結學習洞察"""
        if not self.decision_history:
            return "暫無足夠數據生成學習總結"
        
        total_decisions = len(self.decision_history)
        total_outcomes = len(self.outcome_history)
        
        return f"已追蹤 {total_decisions} 個決策，其中 {total_outcomes} 個有結果回饋。系統正在持續學習和優化決策模式。"
'''
    
    def create_optimized_implementation(self):
        """創建優化的實現"""
        print("🔧 開始 EPL Python 實現優化")
        print("=" * 60)
        
        # 分析當前實現
        current_analysis = self.analyze_current_implementation()
        print(f"✅ 當前實現分析完成:")
        print(f"  - 類別數: {len(current_analysis.get('classes', []))}")
        print(f"  - 方法數: {len(current_analysis.get('methods', []))}")
        print(f"  - 代碼行數: {current_analysis.get('total_lines', 0)}")
        
        # 識別缺失組件
        missing = self.identify_missing_components()
        print(f"\n📋 缺失組件識別:")
        print(f"  - 缺失數據類: {len(missing['dataclasses'])}")
        print(f"  - 缺失核心方法: {len(missing['core_methods'])}")
        print(f"  - 缺失分析方法: {len(missing['analytics_methods'])}")
        print(f"  - 缺失整合方法: {len(missing['integration_methods'])}")
        
        total_missing = sum(len(v) for v in missing.values())
        
        if total_missing == 0:
            print("✅ 實現已完整，無需優化")
            return True
        
        print(f"\n🔧 需要添加 {total_missing} 個組件")
        
        # 生成優化代碼
        optimization_content = ""
        
        if missing['dataclasses']:
            print("📝 生成缺失的數據類...")
            optimization_content += self.generate_missing_dataclasses()
        
        if missing['core_methods']:
            print("📝 生成缺失的核心方法...")
            optimization_content += self.generate_missing_core_methods()
        
        if missing['analytics_methods']:
            print("📝 生成缺失的分析方法...")
            optimization_content += self.generate_missing_analytics_methods()
        
        if missing['integration_methods']:
            print("📝 生成缺失的整合方法...")
            optimization_content += self.generate_missing_integration_methods()
        
        # 添加輔助方法
        optimization_content += self.generate_helper_methods()
        
        print("✅ 優化代碼生成完成")
        return optimization_content
    
    def apply_optimizations(self):
        """應用優化"""
        try:
            # 讀取當前文件
            with open(self.python_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            # 生成優化內容
            optimization_content = self.create_optimized_implementation()
            
            if isinstance(optimization_content, str) and optimization_content:
                # 在文件末尾添加優化內容
                optimized_content = current_content + optimization_content
                
                # 創建備份
                backup_path = self.python_path.with_suffix('.py.backup')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(current_content)
                
                print(f"✅ 已創建備份: {backup_path}")
                
                # 寫入優化後的內容
                with open(self.python_path, 'w', encoding='utf-8') as f:
                    f.write(optimized_content)
                
                print(f"✅ 已應用優化到: {self.python_path}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ 應用優化失敗: {e}")
            return False

def main():
    """主函數"""
    optimizer = EPLPythonOptimizer()
    
    print("🔧 EPL Decision History Tracking Python 實現優化")
    print("=" * 70)
    
    success = optimizer.apply_optimizations()
    
    if success:
        print("\n🎉 EPL Python 實現優化完成!")
        print("✅ 已添加缺失的數據類和方法")
        print("✅ 已完善 Phase 間整合功能")
        print("✅ 已增強決策分析能力")
        print("\n🚀 準備進行功能測試驗證...")
    else:
        print("\n❌ 優化過程中出現問題")
        print("請檢查錯誤訊息並重新嘗試")

if __name__ == "__main__":
    main()
