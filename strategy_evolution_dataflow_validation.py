"""
🔍 Strategy Evolution Learning 數據流驗證
=========================================

驗證第4組件 JSON 配置與其他 Phase 數據流的匹配度
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

class StrategyEvolutionDataFlowValidator:
    """策略演化學習數據流驗證器"""
    
    def __init__(self):
        self.config_path = Path("/Users/henrychang/Desktop/Trading-X/X/backend/phase4_output_monitoring/4_strategy_evolution_learning/strategy_evolution_learning_config.json")
        
    def load_config(self) -> Dict[str, Any]:
        """載入策略演化學習配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 載入配置失敗: {e}")
            return {}
    
    def validate_phase1_integration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """驗證 Phase1 信號生成整合"""
        phase1_score = 0
        details = {}
        
        # 檢查信號候選數據擷取
        signal_capture = config.get('strategy_learning', {}).get('signal_pattern_analysis', {})
        if signal_capture:
            details['signal_candidate_capture'] = "✅ 完整的 SignalCandidate 物件擷取"
            phase1_score += 25
        else:
            details['signal_candidate_capture'] = "❌ 缺少信號候選數據擷取"
        
        # 檢查技術指標整合
        technical_analysis = signal_capture.get('technical_patterns', {})
        if technical_analysis:
            details['technical_indicator_integration'] = "✅ 技術指標模式分析"
            phase1_score += 20
        else:
            details['technical_indicator_integration'] = "⚠️  技術指標整合有限"
        
        # 檢查市場上下文
        market_context = signal_capture.get('market_condition_correlation', {})
        if market_context:
            details['market_context_tracking'] = "✅ 市場條件關聯分析"
            phase1_score += 20
        else:
            details['market_context_tracking'] = "⚠️  市場上下文追蹤有限"
        
        # 檢查信號品質追蹤
        quality_metrics = signal_capture.get('signal_quality_evolution', {})
        if quality_metrics:
            details['signal_quality_tracking'] = "✅ 信號品質演化追蹤"
            phase1_score += 25
        else:
            details['signal_quality_tracking'] = "❌ 信號品質追蹤缺失"
        
        # 檢查實時數據支援
        realtime_support = config.get('data_collection', {}).get('real_time_learning', {})
        if realtime_support:
            details['realtime_data_support'] = "✅ 實時學習數據支援"
            phase1_score += 10
        else:
            details['realtime_data_support'] = "⚠️  實時數據支援有限"
        
        return {
            "score": phase1_score,
            "grade": "優秀" if phase1_score >= 80 else "良好" if phase1_score >= 60 else "需改進",
            "details": details
        }
    
    def validate_phase2_integration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """驗證 Phase2 預評估整合"""
        phase2_score = 0
        details = {}
        
        # 檢查預評估結果整合
        pre_evaluation = config.get('strategy_learning', {}).get('evaluation_effectiveness_analysis', {})
        if pre_evaluation:
            details['pre_evaluation_integration'] = "✅ 預評估效果分析"
            phase2_score += 30
        else:
            details['pre_evaluation_integration'] = "❌ 預評估整合缺失"
        
        # 檢查相關性分析學習
        correlation_learning = pre_evaluation.get('correlation_learning', {})
        if correlation_learning:
            details['correlation_analysis_learning'] = "✅ 相關性分析學習"
            phase2_score += 25
        else:
            details['correlation_analysis_learning'] = "⚠️  相關性學習有限"
        
        # 檢查評分系統演化
        scoring_evolution = pre_evaluation.get('scoring_system_optimization', {})
        if scoring_evolution:
            details['scoring_system_evolution'] = "✅ 評分系統優化"
            phase2_score += 25
        else:
            details['scoring_system_evolution'] = "❌ 評分系統演化缺失"
        
        # 檢查投資組合狀態學習
        portfolio_learning = config.get('strategy_learning', {}).get('portfolio_state_learning', {})
        if portfolio_learning:
            details['portfolio_state_learning'] = "✅ 投資組合狀態學習"
            phase2_score += 20
        else:
            details['portfolio_state_learning'] = "❌ 投資組合學習缺失"
        
        return {
            "score": phase2_score,
            "grade": "優秀" if phase2_score >= 80 else "良好" if phase2_score >= 60 else "需改進", 
            "details": details
        }
    
    def validate_phase3_integration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """驗證 Phase3 執行追蹤整合"""
        phase3_score = 0
        details = {}
        
        # 檢查執行結果學習
        execution_learning = config.get('strategy_learning', {}).get('execution_learning', {})
        if execution_learning:
            details['execution_result_learning'] = "✅ 執行結果學習機制"
            phase3_score += 35
        else:
            details['execution_result_learning'] = "❌ 執行學習缺失"
        
        # 檢查策略效果追蹤
        strategy_effectiveness = execution_learning.get('strategy_effectiveness_tracking', {})
        if strategy_effectiveness:
            details['strategy_effectiveness_tracking'] = "✅ 策略效果追蹤"
            phase3_score += 30
        else:
            details['strategy_effectiveness_tracking'] = "❌ 策略效果追蹤缺失"
        
        # 檢查適應性調整
        adaptive_adjustment = execution_learning.get('adaptive_parameter_adjustment', {})
        if adaptive_adjustment:
            details['adaptive_adjustment'] = "✅ 適應性參數調整"
            phase3_score += 25
        else:
            details['adaptive_adjustment'] = "❌ 適應性調整缺失"
        
        # 檢查風險管理學習
        risk_learning = config.get('strategy_learning', {}).get('risk_management_evolution', {})
        if risk_learning:
            details['risk_management_learning'] = "✅ 風險管理演化"
            phase3_score += 10
        else:
            details['risk_management_learning'] = "⚠️  風險管理學習有限"
        
        return {
            "score": phase3_score,
            "grade": "優秀" if phase3_score >= 80 else "良好" if phase3_score >= 60 else "需改進",
            "details": details
        }
    
    def validate_phase4_consistency(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """驗證 Phase4 內部一致性"""
        phase4_score = 0
        details = {}
        
        # 檢查策略學習架構
        strategy_learning = config.get('strategy_learning', {})
        if strategy_learning:
            details['strategy_learning_framework'] = "✅ 完整的策略學習框架"
            phase4_score += 25
        else:
            details['strategy_learning_framework'] = "❌ 策略學習框架缺失"
        
        # 檢查學習演算法
        learning_algorithms = config.get('learning_algorithms', {})
        if learning_algorithms:
            details['learning_algorithms'] = "✅ 多種學習演算法支援"
            phase4_score += 25
        else:
            details['learning_algorithms'] = "❌ 學習演算法缺失"
        
        # 檢查模型管理
        model_management = config.get('model_management', {})
        if model_management:
            details['model_management'] = "✅ 完整的模型管理系統"
            phase4_score += 25
        else:
            details['model_management'] = "❌ 模型管理缺失"
        
        # 檢查回測驗證
        backtesting = config.get('backtesting_integration', {})
        if backtesting:
            details['backtesting_integration'] = "✅ 回測驗證整合"
            phase4_score += 15
        else:
            details['backtesting_integration'] = "⚠️  回測驗證有限"
        
        # 檢查API接口
        api_interfaces = config.get('api_interfaces', {})
        if api_interfaces:
            details['api_interfaces'] = "✅ 完整的API接口"
            phase4_score += 10
        else:
            details['api_interfaces'] = "❌ API接口缺失"
        
        return {
            "score": phase4_score,
            "grade": "優秀" if phase4_score >= 80 else "良好" if phase4_score >= 60 else "需改進",
            "details": details
        }
    
    def validate_data_completeness(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """驗證數據完整性"""
        completeness_score = 0
        details = {}
        
        # 檢查數據存儲
        data_storage = config.get('data_storage', {})
        if data_storage:
            details['data_storage'] = "✅ 完整的數據存儲配置"
            completeness_score += 30
        else:
            details['data_storage'] = "❌ 數據存儲配置缺失"
        
        # 檢查數據收集
        data_collection = config.get('data_collection', {})
        if data_collection:
            details['data_collection'] = "✅ 全面的數據收集機制"
            completeness_score += 25
        else:
            details['data_collection'] = "❌ 數據收集機制缺失"
        
        # 檢查數據處理
        data_processing = config.get('data_processing', {})
        if data_processing:
            details['data_processing'] = "✅ 數據處理流程完整"
            completeness_score += 25
        else:
            details['data_processing'] = "❌ 數據處理流程缺失"
        
        # 檢查實時監控
        monitoring = config.get('real_time_monitoring', {})
        if monitoring:
            details['real_time_monitoring'] = "✅ 實時監控系統"
            completeness_score += 20
        else:
            details['real_time_monitoring'] = "❌ 實時監控缺失"
        
        return {
            "score": completeness_score,
            "grade": "優秀" if completeness_score >= 80 else "良好" if completeness_score >= 60 else "需改進",
            "details": details
        }
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """生成完整的驗證報告"""
        print("🔍 Strategy Evolution Learning 數據流驗證開始")
        print("=" * 60)
        
        # 載入配置
        config = self.load_config()
        if not config:
            return {"error": "無法載入配置文件"}
        
        # 執行各階段驗證
        print("📊 執行 Phase1 整合驗證...")
        phase1_result = self.validate_phase1_integration(config)
        print(f"  Phase1 整合: {phase1_result['score']}/100 ({phase1_result['grade']})")
        
        print("📊 執行 Phase2 整合驗證...")
        phase2_result = self.validate_phase2_integration(config)
        print(f"  Phase2 整合: {phase2_result['score']}/100 ({phase2_result['grade']})")
        
        print("📊 執行 Phase3 整合驗證...")
        phase3_result = self.validate_phase3_integration(config)
        print(f"  Phase3 整合: {phase3_result['score']}/100 ({phase3_result['grade']})")
        
        print("📊 執行 Phase4 一致性驗證...")
        phase4_result = self.validate_phase4_consistency(config)
        print(f"  Phase4 一致性: {phase4_result['score']}/100 ({phase4_result['grade']})")
        
        print("📊 執行數據完整性驗證...")
        completeness_result = self.validate_data_completeness(config)
        print(f"  數據完整性: {completeness_result['score']}/100 ({completeness_result['grade']})")
        
        # 計算總體分數
        total_score = (
            phase1_result['score'] + 
            phase2_result['score'] + 
            phase3_result['score'] + 
            phase4_result['score'] + 
            completeness_result['score']
        ) / 5
        
        overall_grade = "優秀" if total_score >= 85 else "良好" if total_score >= 70 else "需改進"
        
        print(f"\n📈 整體驗證結果:")
        print(f"  總體分數: {total_score:.1f}/100")
        print(f"  整體等級: {overall_grade}")
        
        if total_score >= 85:
            print("✅ 數據流匹配優秀，可以繼續 Python 實現優化")
        elif total_score >= 70:
            print("⚠️  數據流匹配良好，建議小幅改進後繼續")
        else:
            print("❌ 數據流匹配需要改進，建議先修正 JSON 配置")
        
        return {
            "validation_timestamp": datetime.now().isoformat(),
            "overall_score": total_score,
            "overall_grade": overall_grade,
            "phase_results": {
                "phase1_integration": phase1_result,
                "phase2_integration": phase2_result,
                "phase3_integration": phase3_result,
                "phase4_consistency": phase4_result,
                "data_completeness": completeness_result
            },
            "recommendation": "proceed_to_python_optimization" if total_score >= 70 else "improve_json_config"
        }

def main():
    """主函數"""
    validator = StrategyEvolutionDataFlowValidator()
    report = validator.generate_validation_report()
    
    if "error" in report:
        print(f"❌ 驗證過程出錯: {report['error']}")
        return False
    
    return report['overall_score'] >= 70

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 準備進行 Strategy Evolution Learning Python 實現優化...")
    else:
        print("\n⚠️  建議先改進 JSON 配置再進行 Python 優化")
