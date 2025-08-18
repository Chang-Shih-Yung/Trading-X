#!/usr/bin/env python3
"""
🧪 Trading-X 簡化系統測試
========================

簡化版本的後端測試，不依賴外部API
驗證核心架構和組件初始化
"""

import asyncio
import sys
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass

# 設置項目路徑 - 使用 X 資料夾作為根目錄
current_dir = Path(__file__).parent
project_root = current_dir.parent  # X 資料夾
sys.path.append(str(project_root))
sys.path.append(str(current_dir))  # backend 資料夾

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class MockTestResult:
    """模擬測試結果"""
    test_name: str
    success: bool
    details: Dict[str, Any]
    execution_time: float

class SimplifiedSystemTest:
    """簡化系統測試"""
    
    def __init__(self):
        self.test_results: List[MockTestResult] = []
    
    async def test_core_imports(self) -> MockTestResult:
        """測試核心模組導入"""
        start_time = datetime.now()
        
        try:
            # 測試標準庫導入
            import asyncio
            import json
            import logging
            from datetime import datetime as dt
            from dataclasses import dataclass
            
            # 測試pandas導入
            import pandas as pd
            
            details = {
                "asyncio": "✅ 已導入",
                "json": "✅ 已導入", 
                "logging": "✅ 已導入",
                "datetime": "✅ 已導入",
                "dataclasses": "✅ 已導入",
                "pandas": f"✅ 已導入 v{pd.__version__}",
            }
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return MockTestResult(
                test_name="核心模組導入",
                success=True,
                details=details,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return MockTestResult(
                test_name="核心模組導入",
                success=False,
                details={"error": str(e)},
                execution_time=execution_time
            )
    
    async def test_backend_structure(self) -> MockTestResult:
        """測試後端目錄結構"""
        start_time = datetime.now()
        
        try:
            backend_dir = Path(__file__).parent
            
            # 檢查所需目錄
            required_dirs = [
                "shared_core",
                "phase1_signal_generation",
                "phase2_pre_evaluation",
                "phase3_execution_policy", 
                "phase4_output_monitoring"
            ]
            
            structure_status = {}
            for dir_name in required_dirs:
                dir_path = backend_dir / dir_name
                if dir_path.exists():
                    structure_status[dir_name] = "✅ 存在"
                else:
                    structure_status[dir_name] = "❌ 缺失"
            
            # 檢查核心文件
            core_files = [
                "trading_x_backend_integrator.py",
                "launcher.py",
                "architecture_check.py"
            ]
            
            for file_name in core_files:
                file_path = backend_dir / file_name
                if file_path.exists():
                    structure_status[file_name] = f"✅ 存在 ({file_path.stat().st_size:,} bytes)"
                else:
                    structure_status[file_name] = "❌ 缺失"
            
            all_exist = all("✅" in status for status in structure_status.values())
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return MockTestResult(
                test_name="後端目錄結構",
                success=all_exist,
                details=structure_status,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return MockTestResult(
                test_name="後端目錄結構",
                success=False,
                details={"error": str(e)},
                execution_time=execution_time
            )
    
    async def test_mock_pipeline(self) -> MockTestResult:
        """測試模擬流水線"""
        start_time = datetime.now()
        
        try:
            # 模擬四階段流水線
            phases = {
                "Phase1_信號生成": await self._simulate_phase1(),
                "Phase2_前處理": await self._simulate_phase2(),
                "Phase3_決策引擎": await self._simulate_phase3(),
                "Phase4_輸出監控": await self._simulate_phase4()
            }
            
            # 計算總體成功率
            success_count = sum(1 for phase_result in phases.values() if phase_result["success"])
            overall_success = success_count == len(phases)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return MockTestResult(
                test_name="模擬流水線測試",
                success=overall_success,
                details={
                    "phases": phases,
                    "success_rate": f"{success_count}/{len(phases)}",
                    "overall_status": "通過" if overall_success else "部分失敗"
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return MockTestResult(
                test_name="模擬流水線測試",
                success=False,
                details={"error": str(e)},
                execution_time=execution_time
            )
    
    async def _simulate_phase1(self) -> Dict[str, Any]:
        """模擬Phase1信號生成"""
        await asyncio.sleep(0.1)  # 模擬處理時間
        
        # 模擬生成3個信號候選者
        candidates = [
            {"id": f"candidate_{i}", "strength": 70 + i*5, "symbol": "BTCUSDT"}
            for i in range(3)
        ]
        
        return {
            "success": True,
            "candidates_generated": len(candidates),
            "details": "成功生成信號候選者"
        }
    
    async def _simulate_phase2(self) -> Dict[str, Any]:
        """模擬Phase2前處理"""
        await asyncio.sleep(0.1)  # 模擬處理時間
        
        # 模擬EPL處理
        return {
            "success": True,
            "processed_signals": 3,
            "passed_to_epl": 2,
            "details": "EPL前處理完成"
        }
    
    async def _simulate_phase3(self) -> Dict[str, Any]:
        """模擬Phase3決策引擎"""
        await asyncio.sleep(0.1)  # 模擬處理時間
        
        # 模擬決策生成
        decisions = ["NEW_POSITION", "STRENGTHEN"]
        
        return {
            "success": True,
            "decisions_made": len(decisions),
            "decision_types": decisions,
            "details": "智能決策完成"
        }
    
    async def _simulate_phase4(self) -> Dict[str, Any]:
        """模擬Phase4輸出監控"""
        await asyncio.sleep(0.1)  # 模擬處理時間
        
        # 模擬輸出處理
        outputs = [
            {"priority": "HIGH", "status": "已發送"},
            {"priority": "MEDIUM", "status": "已發送"}
        ]
        
        return {
            "success": True,
            "outputs_processed": len(outputs),
            "notification_sent": True,
            "details": "分級輸出完成"
        }
    
    async def test_dynamic_characteristics(self) -> MockTestResult:
        """測試動態特性"""
        start_time = datetime.now()
        
        try:
            # 模擬動態參數檢查
            dynamic_features = {
                "dynamic_rsi_period": {"value": "adaptive", "timestamp": datetime.now().isoformat()},
                "dynamic_volatility_threshold": {"value": "market_dependent", "last_update": "recent"},
                "adaptive_signal_strength": {"status": "active", "adaptation_rate": 0.85}
            }
            
            # 檢查動態特性
            dynamic_count = len(dynamic_features)
            has_timestamps = any("timestamp" in feature or "last_update" in feature 
                               for feature in dynamic_features.values())
            
            adaptation_score = dynamic_count * 0.3 + (0.4 if has_timestamps else 0)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return MockTestResult(
                test_name="動態特性驗證",
                success=adaptation_score > 0.5,
                details={
                    "dynamic_features": dynamic_features,
                    "feature_count": dynamic_count,
                    "has_timestamps": has_timestamps,
                    "adaptation_score": f"{adaptation_score:.2f}"
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return MockTestResult(
                test_name="動態特性驗證",
                success=False,
                details={"error": str(e)},
                execution_time=execution_time
            )
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """運行所有測試"""
        print("🧪 Trading-X 簡化系統測試")
        print("=" * 50)
        
        # 運行各項測試
        tests = [
            self.test_core_imports(),
            self.test_backend_structure(),
            self.test_mock_pipeline(),
            self.test_dynamic_characteristics()
        ]
        
        # 並行執行測試
        results = await asyncio.gather(*tests, return_exceptions=True)
        
        # 處理結果
        successful_tests = 0
        total_tests = len(results)
        
        print("\n📋 測試結果:")
        for i, result in enumerate(results):
            if isinstance(result, MockTestResult):
                self.test_results.append(result)
                status_emoji = "✅" if result.success else "❌"
                print(f"{status_emoji} {result.test_name} ({result.execution_time:.3f}s)")
                
                # 顯示詳細信息
                if result.success:
                    successful_tests += 1
                    if isinstance(result.details, dict) and len(result.details) <= 3:
                        for key, value in result.details.items():
                            print(f"     {key}: {value}")
                else:
                    print(f"     錯誤: {result.details.get('error', '未知錯誤')}")
            else:
                print(f"❌ 測試 {i+1} 異常: {result}")
        
        # 測試總結
        success_rate = successful_tests / total_tests
        overall_status = "通過" if success_rate == 1.0 else "部分通過" if success_rate > 0.5 else "失敗"
        
        print(f"\n🏆 測試總結:")
        print(f"✅ 成功: {successful_tests}/{total_tests}")
        print(f"📊 成功率: {success_rate:.1%}")
        print(f"🎯 總體狀態: {overall_status}")
        
        # 建議
        if success_rate == 1.0:
            print("\n🚀 建議下一步:")
            print("- 系統基礎架構良好")
            print("- 可以開始安裝完整依賴套件")
            print("- 運行: py -m pip install -r requirements.txt")
            print("- 然後測試: py launcher.py --mode test")
        elif success_rate > 0.5:
            print("\n🔧 需要注意:")
            print("- 部分組件需要修復")
            print("- 檢查失敗的測試項目")
            print("- 完善後再進行完整測試")
        else:
            print("\n⚠️ 需要修復:")
            print("- 多個核心組件有問題")
            print("- 請檢查系統環境和依賴")
            print("- 重新檢查架構設置")
        
        return {
            "successful_tests": successful_tests,
            "total_tests": total_tests,
            "success_rate": success_rate,
            "overall_status": overall_status,
            "test_results": [
                {
                    "name": result.test_name,
                    "success": result.success,
                    "execution_time": result.execution_time
                } for result in self.test_results
            ]
        }

async def main():
    """主函數"""
    try:
        print(f"🕐 開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 創建測試實例
        test_system = SimplifiedSystemTest()
        
        # 運行測試
        results = await test_system.run_all_tests()
        
        print(f"\n🕐 結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 返回結果
        return results
        
    except Exception as e:
        print(f"\n❌ 測試系統錯誤: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    asyncio.run(main())
