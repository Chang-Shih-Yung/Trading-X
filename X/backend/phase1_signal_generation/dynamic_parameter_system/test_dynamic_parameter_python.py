#!/usr/bin/env python3
"""
Dynamic Parameter Engine Testing Suite for Phase1
Phase1 動態參數引擎測試套件 - 驗證Python邏輯流程無錯誤或衝突
"""

import asyncio
import json
import sys
import os
import traceback
from datetime import datetime, timezone
from typing import Dict, Any, List
import unittest
from unittest.mock import AsyncMock, Mock

# 確保可以導入動態參數引擎
sys.path.append('/Users/itts/Desktop/Trading X/X/backend/phase1_signal_generation/dynamic_parameter_system')
from dynamic_parameter_engine import (
    DynamicParameterEngine,
    MarketRegimeDetector,
    TradingSessionDetector, 
    DynamicParameterAdapter,
    MockMarketDataSource,
    MarketData,
    MarketRegime,
    TradingSession,
    create_dynamic_parameter_engine
)

class AsyncTestRunner:
    """異步測試運行器"""
    
    def __init__(self):
        self.config_path = "/Users/itts/Desktop/Trading X/X/backend/phase1_signal_generation/dynamic_parameter_system/dynamic_parameter_config.json"
        self.test_results = {
            "engine_creation": False,
            "market_regime_detection": False,
            "trading_session_detection": False,
            "parameter_adaptation": False,
            "phase1_integration": False,
            "phase2_integration": False,
            "phase3_integration": False,
            "phase5_integration": False,
            "error_handling": False,
            "boundary_validation": False,
            "data_flow_integrity": False
        }
        self.errors = []
        self.warnings = []
    
    async def test_engine_creation(self) -> bool:
        """測試引擎創建"""
        print("🔍 測試動態參數引擎創建...")
        
        try:
            engine = await create_dynamic_parameter_engine(self.config_path)
            
            # 檢查引擎組件
            if engine.regime_detector is None:
                raise AssertionError("市場制度檢測器未初始化")
            if engine.session_detector is None:
                raise AssertionError("交易時段檢測器未初始化")
            if engine.parameter_adapter is None:
                raise AssertionError("參數適配器未初始化")
            if engine.config is None:
                raise AssertionError("配置未載入")
            
            print("✅ 引擎創建測試通過")
            return True
            
        except Exception as e:
            self.errors.append(f"引擎創建失敗: {e}")
            print(f"❌ 引擎創建測試失敗: {e}")
            return False
    
    async def test_market_regime_detection(self) -> bool:
        """測試市場制度檢測"""
        print("🔍 測試市場制度檢測...")
        
        try:
            engine = await create_dynamic_parameter_engine(self.config_path)
            
            # 創建測試市場數據
            test_cases = [
                # 牛市數據
                MarketData(
                    timestamp=datetime.now(timezone.utc),
                    price=50000.0,
                    volume=1000000.0,
                    price_change_1h=0.01,
                    price_change_24h=0.05,  # 5% 上漲
                    volume_ratio=1.3,
                    volatility=0.03,
                    fear_greed_index=75,  # 貪婪
                    bid_ask_spread=0.001,
                    market_depth=0.8,
                    moving_averages={"ma_20": 49800.0, "ma_50": 49000.0, "ma_200": 48000.0}
                ),
                # 熊市數據
                MarketData(
                    timestamp=datetime.now(timezone.utc),
                    price=45000.0,
                    volume=800000.0,
                    price_change_1h=-0.01,
                    price_change_24h=-0.08,  # 8% 下跌
                    volume_ratio=1.2,
                    volatility=0.06,
                    fear_greed_index=25,  # 恐懼
                    bid_ask_spread=0.002,
                    market_depth=0.6,
                    moving_averages={"ma_20": 45200.0, "ma_50": 46000.0, "ma_200": 47000.0}
                ),
                # 橫盤數據
                MarketData(
                    timestamp=datetime.now(timezone.utc),
                    price=48000.0,
                    volume=900000.0,
                    price_change_1h=0.005,
                    price_change_24h=0.01,  # 1% 變化
                    volume_ratio=1.0,
                    volatility=0.02,
                    fear_greed_index=50,  # 中性
                    bid_ask_spread=0.001,
                    market_depth=0.7,
                    moving_averages={"ma_20": 48000.0, "ma_50": 48000.0, "ma_200": 48000.0}
                )
            ]
            
            for i, market_data in enumerate(test_cases):
                regime, confidence = await engine.regime_detector.detect_market_regime(market_data)
                if not isinstance(regime, MarketRegime):
                    raise AssertionError(f"測試案例 {i+1}: 制度類型錯誤")
                if not isinstance(confidence, float):
                    raise AssertionError(f"測試案例 {i+1}: 信心度類型錯誤")
                if not (0 <= confidence <= 1):
                    raise AssertionError(f"測試案例 {i+1}: 信心度範圍錯誤")
                
                print(f"  測試案例 {i+1}: 制度={regime.value}, 信心度={confidence:.3f}")
            
            print("✅ 市場制度檢測測試通過")
            return True
            
        except Exception as e:
            self.errors.append(f"市場制度檢測失敗: {e}")
            print(f"❌ 市場制度檢測測試失敗: {e}")
            return False
    
    async def test_trading_session_detection(self) -> bool:
        """測試交易時段檢測"""
        print("🔍 測試交易時段檢測...")
        
        try:
            engine = await create_dynamic_parameter_engine(self.config_path)
            
            # 測試不同時間點
            test_times = [
                datetime(2024, 1, 15, 14, 30, tzinfo=timezone.utc),  # 美股時間
                datetime(2024, 1, 15, 2, 30, tzinfo=timezone.utc),   # 亞洲時間
                datetime(2024, 1, 15, 10, 30, tzinfo=timezone.utc),  # 歐洲時間
                datetime(2024, 1, 15, 22, 30, tzinfo=timezone.utc),  # 非活躍時間
            ]
            
            for i, test_time in enumerate(test_times):
                session = await engine.session_detector.detect_trading_session(test_time)
                if not isinstance(session, TradingSession):
                    raise AssertionError(f"測試時間 {i+1}: 時段類型錯誤")
                print(f"  測試時間 {i+1} ({test_time.strftime('%H:%M UTC')}): 時段={session.value}")
            
            print("✅ 交易時段檢測測試通過")
            return True
            
        except Exception as e:
            self.errors.append(f"交易時段檢測失敗: {e}")
            print(f"❌ 交易時段檢測測試失敗: {e}")
            return False
    
    async def test_parameter_adaptation(self) -> bool:
        """測試參數適配"""
        print("🔍 測試參數適配...")
        
        try:
            engine = await create_dynamic_parameter_engine(self.config_path)
            
            # 測試市場數據
            market_data = await engine.market_data_source.get_current_market_data()
            
            # 測試不同制度下的參數適配
            test_regimes = [MarketRegime.BULL_TREND, MarketRegime.BEAR_TREND, MarketRegime.VOLATILE]
            test_sessions = [TradingSession.US_MARKET, TradingSession.OFF_HOURS]
            
            # 獲取Phase1配置
            phase1_config = engine._get_phase_config("phase1")
            if phase1_config is None:
                raise AssertionError("Phase1配置獲取失敗")
            
            for regime in test_regimes:
                for session in test_sessions:
                    for param_name, param_config in phase1_config.items():
                        adapted_param = await engine.parameter_adapter.adapt_parameter(
                            param_config, regime, session, market_data
                        )
                        
                        # 驗證適配結果
                        if adapted_param.parameter_name != param_name:
                            raise AssertionError(f"參數名稱不匹配: {adapted_param.parameter_name} vs {param_name}")
                        if not isinstance(adapted_param.adapted_value, float):
                            raise AssertionError(f"適配值類型錯誤: {type(adapted_param.adapted_value)}")
                        if not isinstance(adapted_param.adaptation_factor, float):
                            raise AssertionError(f"適配因子類型錯誤: {type(adapted_param.adaptation_factor)}")
                        if not isinstance(adapted_param.adaptation_reasons, list):
                            raise AssertionError(f"適配原因類型錯誤: {type(adapted_param.adaptation_reasons)}")
                        if not (0 <= adapted_param.confidence_score <= 1):
                            raise AssertionError(f"信心度範圍錯誤: {adapted_param.confidence_score}")
                        
                        # 檢查邊界限制
                        bounds = param_config["bounds"]
                        if not (bounds["minimum"] <= adapted_param.adapted_value <= bounds["maximum"]):
                            raise AssertionError(f"參數 {param_name} 超出邊界: {adapted_param.adapted_value}")
            
            print("✅ 參數適配測試通過")
            return True
            
        except Exception as e:
            self.errors.append(f"參數適配失敗: {e}")
            print(f"❌ 參數適配測試失敗: {e}")
            return False
    
    async def test_phase_integration(self, phase: str) -> bool:
        """測試階段整合"""
        print(f"🔍 測試 {phase} 階段整合...")
        
        try:
            engine = await create_dynamic_parameter_engine(self.config_path)
            
            # 獲取階段動態參數
            result = await engine.get_dynamic_parameters(phase)
            
            # 驗證結果結構
            if result.adapted_parameters is None:
                raise AssertionError(f"{phase} 適配參數為空")
            if not isinstance(result.market_regime, MarketRegime):
                raise AssertionError(f"{phase} 市場制度類型錯誤")
            if not isinstance(result.trading_session, TradingSession):
                raise AssertionError(f"{phase} 交易時段類型錯誤")
            if not isinstance(result.regime_confidence, float):
                raise AssertionError(f"{phase} 制度信心度類型錯誤")
            if not isinstance(result.timestamp, datetime):
                raise AssertionError(f"{phase} 時間戳類型錯誤")
            if not isinstance(result.metadata, dict):
                raise AssertionError(f"{phase} 元數據類型錯誤")
            
            # 驗證參數數量
            phase_config = engine._get_phase_config(phase)
            expected_param_count = len(phase_config)
            actual_param_count = len(result.adapted_parameters)
            if expected_param_count != actual_param_count:
                raise AssertionError(f"{phase} 參數數量不匹配: 預期 {expected_param_count}, 實際 {actual_param_count}")
            
            # 測試單個參數值獲取
            for param_name in result.adapted_parameters.keys():
                param_value = await engine.get_parameter_value(phase, param_name)
                if not isinstance(param_value, float):
                    raise AssertionError(f"{phase} 參數值類型錯誤")
                if param_value != result.adapted_parameters[param_name].adapted_value:
                    raise AssertionError(f"{phase} 參數值不一致")
            
            print(f"✅ {phase} 階段整合測試通過")
            return True
            
        except Exception as e:
            self.errors.append(f"{phase} 階段整合失敗: {e}")
            print(f"❌ {phase} 階段整合測試失敗: {e}")
            return False
    
    async def test_error_handling(self) -> bool:
        """測試錯誤處理"""
        print("🔍 測試錯誤處理...")
        
        try:
            engine = await create_dynamic_parameter_engine(self.config_path)
            
            # 測試無效階段
            try:
                await engine.get_dynamic_parameters("invalid_phase")
                raise AssertionError("應該拋出無效階段異常")
            except ValueError:
                pass  # 預期的異常
            
            # 測試無效參數名
            try:
                await engine.get_parameter_value("phase1", "invalid_parameter")
                raise AssertionError("應該拋出無效參數異常")
            except ValueError:
                pass  # 預期的異常
            
            print("✅ 錯誤處理測試通過")
            return True
            
        except Exception as e:
            self.errors.append(f"錯誤處理測試失敗: {e}")
            print(f"❌ 錯誤處理測試失敗: {e}")
            return False
    
    async def test_boundary_validation(self) -> bool:
        """測試邊界值驗證"""
        print("🔍 測試邊界值驗證...")
        
        try:
            engine = await create_dynamic_parameter_engine(self.config_path)
            
            # 創建極端市場數據
            extreme_bull = MarketData(
                timestamp=datetime.now(timezone.utc),
                price=100000.0,
                volume=5000000.0,
                price_change_1h=0.05,
                price_change_24h=0.20,  # 極端上漲
                volume_ratio=3.0,
                volatility=0.15,
                fear_greed_index=100,  # 極度貪婪
                bid_ask_spread=0.0001,
                market_depth=1.0,
                moving_averages={"ma_20": 99000.0, "ma_50": 95000.0, "ma_200": 90000.0}
            )
            
            extreme_bear = MarketData(
                timestamp=datetime.now(timezone.utc),
                price=20000.0,
                volume=500000.0,
                price_change_1h=-0.05,
                price_change_24h=-0.25,  # 極端下跌
                volume_ratio=0.3,
                volatility=0.20,
                fear_greed_index=0,  # 極度恐懼
                bid_ask_spread=0.01,
                market_depth=0.2,
                moving_averages={"ma_20": 21000.0, "ma_50": 25000.0, "ma_200": 30000.0}
            )
            
            # 測試極端數據下的邊界保護
            for extreme_data in [extreme_bull, extreme_bear]:
                # 替換數據源
                engine.market_data_source.get_current_market_data = AsyncMock(return_value=extreme_data)
                
                result = await engine.get_dynamic_parameters("phase1")
                
                # 檢查所有參數都在安全邊界內
                for param_name, adapted_param in result.adapted_parameters.items():
                    phase_config = engine._get_phase_config("phase1")
                    bounds = phase_config[param_name]["bounds"]
                    
                    if not (bounds["minimum"] <= adapted_param.adapted_value <= bounds["maximum"]):
                        raise AssertionError(f"極端情況下參數 {param_name} 超出邊界: {adapted_param.adapted_value}")
            
            print("✅ 邊界值驗證測試通過")
            return True
            
        except Exception as e:
            self.errors.append(f"邊界值驗證失敗: {e}")
            print(f"❌ 邊界值驗證測試失敗: {e}")
            return False
    
    async def test_data_flow_integrity(self) -> bool:
        """測試數據流完整性"""
        print("🔍 測試數據流完整性...")
        
        try:
            engine = await create_dynamic_parameter_engine(self.config_path)
            
            # 測試系統狀態
            status = await engine.get_system_status()
            if "status" not in status:
                raise AssertionError("系統狀態缺少status字段")
            if "market_regime" not in status:
                raise AssertionError("系統狀態缺少market_regime字段")
            if "trading_session" not in status:
                raise AssertionError("系統狀態缺少trading_session字段")
            if "market_data" not in status:
                raise AssertionError("系統狀態缺少market_data字段")
            
            # 測試數據一致性
            phase1_result = await engine.get_dynamic_parameters("phase1")
            
            # 檢查時間戳一致性
            if not isinstance(phase1_result.timestamp, datetime):
                raise AssertionError("時間戳類型錯誤")
            
            # 檢查制度一致性
            if not isinstance(phase1_result.market_regime, MarketRegime):
                raise AssertionError("市場制度類型錯誤")
            if not isinstance(phase1_result.trading_session, TradingSession):
                raise AssertionError("交易時段類型錯誤")
            
            # 檢查元數據完整性
            required_metadata = ["config_version", "market_data_timestamp", "fear_greed_index", "volatility"]
            for key in required_metadata:
                if key not in phase1_result.metadata:
                    raise AssertionError(f"元數據缺少{key}字段")
            
            print("✅ 數據流完整性測試通過")
            return True
            
        except Exception as e:
            self.errors.append(f"數據流完整性測試失敗: {e}")
            print(f"❌ 數據流完整性測試失敗: {e}")
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """運行所有測試"""
        print("🚀 開始 Dynamic Parameter Engine Python 全面測試")
        print("=" * 70)
        
        # 執行所有測試
        self.test_results["engine_creation"] = await self.test_engine_creation()
        self.test_results["market_regime_detection"] = await self.test_market_regime_detection()
        self.test_results["trading_session_detection"] = await self.test_trading_session_detection()
        self.test_results["parameter_adaptation"] = await self.test_parameter_adaptation()
        self.test_results["phase1_integration"] = await self.test_phase_integration("phase1")
        self.test_results["phase2_integration"] = await self.test_phase_integration("phase2")
        self.test_results["phase3_integration"] = await self.test_phase_integration("phase3")
        self.test_results["phase5_integration"] = await self.test_phase_integration("phase5")
        self.test_results["error_handling"] = await self.test_error_handling()
        self.test_results["boundary_validation"] = await self.test_boundary_validation()
        self.test_results["data_flow_integrity"] = await self.test_data_flow_integrity()
        
        # 計算總體結果
        all_passed = all(self.test_results.values())
        
        print("\n" + "=" * 70)
        print("📊 Python 測試結果摘要")
        print("=" * 70)
        
        for test_name, result in self.test_results.items():
            status = "✅ 通過" if result else "❌ 失敗"
            print(f"{test_name:<30} {status}")
        
        print(f"\n總體結果: {'✅ 全部通過' if all_passed else '❌ 有錯誤需要修正'}")
        
        if self.errors:
            print(f"\n❌ 錯誤 ({len(self.errors)} 個):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        if self.warnings:
            print(f"\n⚠️  警告 ({len(self.warnings)} 個):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        # 生成詳細報告
        report = {
            "validation_timestamp": datetime.now().isoformat(),
            "overall_status": "PASS" if all_passed else "FAIL",
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for r in self.test_results.values() if r),
            "failed_tests": sum(1 for r in self.test_results.values() if not r),
            "test_results": self.test_results,
            "errors": self.errors,
            "warnings": self.warnings,
            "recommendations": self.generate_recommendations(all_passed)
        }
        
        return report
    
    def generate_recommendations(self, all_passed: bool) -> List[str]:
        """生成改進建議"""
        recommendations = []
        
        if not all_passed:
            recommendations.append("修正所有錯誤後再次運行測試")
            recommendations.append("檢查配置文件路徑和格式")
            recommendations.append("確保所有依賴項正確安裝")
        else:
            recommendations.extend([
                "Python 動態參數引擎實現完成並通過所有測試",
                "可以開始整合到現有的 Phase1-5 系統中",
                "建議添加更多的監控和日誌記錄功能",
                "考慮實現配置熱重載和實時參數調整",
                "添加更詳細的效能分析和優化建議"
            ])
        
        return recommendations

async def main():
    """主函數"""
    try:
        # 檢查依賴
        import pytz
        print("✅ 依賴檢查通過")
    except ImportError as e:
        print(f"❌ 缺少依賴: {e}")
        print("請運行: pip install pytz")
        return 1
    
    # 創建測試運行器
    test_runner = AsyncTestRunner()
    
    # 執行測試
    report = await test_runner.run_all_tests()
    
    # 保存測試報告
    report_path = "/Users/itts/Desktop/Trading X/X/backend/phase1_signal_generation/dynamic_parameter_system/test_report.json"
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n📄 詳細測試報告已保存到: {report_path}")
    except Exception as e:
        print(f"\n❌ 無法保存測試報告: {e}")
    
    # 返回適當的退出碼
    return 0 if report["overall_status"] == "PASS" else 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  測試被用戶中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 測試運行失敗: {e}")
        traceback.print_exc()
        sys.exit(1)
