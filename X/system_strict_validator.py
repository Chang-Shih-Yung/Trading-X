#!/usr/bin/env python3
"""
🔒 Trading X 嚴格系統驗證器
==============================    # 2. MarketRegime 嚴格驗證 - 必須使用正確的模組
    try:
        # 只允許從正確的模組導入 MarketRegime
        from backend.phase2_adaptive_learning.market_regime_detection.advanced_market_detector import MarketRegime
        logger.info("✅ MarketRegime 導入成功（來自 advanced_market_detector）")
        validation_result["market_regime"] = True
    except ImportError as e:
        logger.error(f"❌ MarketRegime 嚴格驗證失敗: {e}")
        logger.error("💥 系統要求：必須有正確的 MarketRegime 模組才能運行")
        raise SystemValidationError(f"MarketRegime 驗證失敗: {e}")有組件都正確安裝和導入，否則終止系統
- 強制檢查 TA-Lib
- 強制檢查 MarketRegime
- 強制檢查 EPLPreProcessingSystem
- 強制檢查所有關鍵組件

如果任何組件缺失，系統將立即終止
"""

import sys
import logging
import traceback
from typing import Dict, List, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class SystemValidationError(Exception):
    """系統驗證錯誤"""
    pass

class StrictSystemValidator:
    """嚴格系統驗證器"""
    
    def __init__(self):
        self.validation_results = {
            "talib": False,
            "market_regime": False,
            "epl_preprocessing": False,
            "phase1_integration": False,
            "phase3_decision": False,
            "signal_database": False
        }
        self.errors = []
    
    def validate_all_components(self) -> Dict[str, Any]:
        """驗證所有組件，任何失敗都終止系統"""
        logger.info("🔒 開始嚴格系統驗證...")
        
        # 1. TA-Lib 檢查
        self._validate_talib()
        
        # 2. MarketRegime 檢查
        self._validate_market_regime()
        
        # 3. EPLPreProcessingSystem 檢查
        self._validate_epl_preprocessing()
        
        # 4. Phase1 整合檢查
        self._validate_phase1_integration()
        
        # 5. Phase3 決策引擎檢查
        self._validate_phase3_decision()
        
        # 6. 信號資料庫檢查
        self._validate_signal_database()
        
        # 檢查結果
        return self._evaluate_results()
    
    def _validate_talib(self):
        """驗證 TA-Lib 庫"""
        try:
            import talib
            logger.info("✅ TA-Lib 庫驗證通過")
            self.validation_results["talib"] = True
        except ImportError as e:
            error_msg = f"❌ TA-Lib 庫缺失 - 系統無法運行: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            raise SystemValidationError(error_msg)
    
    def _validate_market_regime(self):
        """驗證 MarketRegime 組件"""
        try:
            # 只允許從正確的模組導入 MarketRegime
            from backend.phase2_adaptive_learning.market_regime_detection.advanced_market_detector import MarketRegime
            logger.info("✅ MarketRegime 導入成功（來自 advanced_market_detector）")
            self.validation_results["market_regime"] = True
        except ImportError as e:
            error_msg = f"❌ MarketRegime 嚴格驗證失敗 - 系統無法運行: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            raise SystemValidationError(error_msg)
    
    def _validate_epl_preprocessing(self):
        """驗證 EPLPreProcessingSystem 導入"""
        try:
            sys.path.append(str(Path(__file__).parent / "backend" / "phase2_pre_evaluation" / "epl_pre_processing_system"))
            from epl_pre_processing_system import EnhancedPreEvaluationLayer
            logger.info("✅ EnhancedPreEvaluationLayer 導入驗證通過")
            self.validation_results["epl_preprocessing"] = True
        except ImportError as e:
            error_msg = f"❌ EnhancedPreEvaluationLayer 導入失敗 - 系統無法運行: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            raise SystemValidationError(error_msg)
    
    def _validate_phase1_integration(self):
        """驗證 Phase1 整合"""
        try:
            sys.path.append(str(Path(__file__).parent / "backend" / "phase1_signal_generation" / "unified_signal_pool"))
            from unified_signal_candidate_pool import UnifiedSignalCandidatePoolV3
            logger.info("✅ Phase1 整合驗證通過")
            self.validation_results["phase1_integration"] = True
        except ImportError as e:
            error_msg = f"❌ Phase1 整合失敗 - 系統無法運行: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            raise SystemValidationError(error_msg)
    
    def _validate_phase3_decision(self):
        """驗證 Phase3 決策引擎"""
        try:
            sys.path.append(str(Path(__file__).parent / "backend" / "phase3_execution_policy"))
            from epl_intelligent_decision_engine import EPLDecision
            
            # 檢查是否有 SIGNAL_IGNORE
            if not hasattr(EPLDecision, 'SIGNAL_IGNORE'):
                raise AttributeError("SIGNAL_IGNORE 枚舉值缺失")
            
            logger.info("✅ Phase3 決策引擎驗證通過")
            self.validation_results["phase3_decision"] = True
        except (ImportError, AttributeError) as e:
            error_msg = f"❌ Phase3 決策引擎失敗 - 系統無法運行: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            raise SystemValidationError(error_msg)
    
    def _validate_signal_database(self):
        """驗證信號資料庫"""
        try:
            from backend.phase2_adaptive_learning.storage.signal_database import SignalDatabase
            
            # 檢查是否有 delete_signal 方法
            if not hasattr(SignalDatabase, 'delete_signal'):
                raise AttributeError("delete_signal 方法缺失")
            
            logger.info("✅ 信號資料庫驗證通過")
            self.validation_results["signal_database"] = True
        except (ImportError, AttributeError) as e:
            error_msg = f"❌ 信號資料庫失敗 - 系統無法運行: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            raise SystemValidationError(error_msg)
    
    def _evaluate_results(self) -> Dict[str, Any]:
        """評估驗證結果"""
        all_passed = all(self.validation_results.values())
        
        result = {
            "all_components_valid": all_passed,
            "validation_details": self.validation_results,
            "errors": self.errors,
            "can_proceed": all_passed
        }
        
        if all_passed:
            logger.info("🎉 所有組件驗證通過！系統可以安全啟動")
        else:
            failed_components = [k for k, v in self.validation_results.items() if not v]
            error_msg = f"❌ 系統驗證失敗！缺失組件: {failed_components}"
            logger.error(error_msg)
            raise SystemValidationError(error_msg)
        
        return result

def validate_system_strict() -> Dict[str, Any]:
    """執行嚴格系統驗證"""
    validator = StrictSystemValidator()
    return validator.validate_all_components()

if __name__ == "__main__":
    try:
        result = validate_system_strict()
        print("✅ 系統驗證完成")
        print(f"驗證結果: {result}")
    except SystemValidationError as e:
        print(f"❌ 系統驗證失敗: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 驗證過程出錯: {e}")
        traceback.print_exc()
        sys.exit(1)
