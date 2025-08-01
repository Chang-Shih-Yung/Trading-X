#!/usr/bin/env python3
"""
🎯 狙擊手計劃 (Sniper Protocol) 第二階段測試
統一數據層 + 實時數據同步 + 性能監控測試
"""

import asyncio
import requests
import json
from datetime import datetime
import time

class SniperPhase2Tester:
    """狙擊手計劃第二階段測試器"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_results = {}
        
    def test_unified_data_layer(self):
        """測試統一數據層 API"""
        print("\n🎯 測試統一數據層...")
        
        url = f"{self.base_url}/api/v1/scalping/unified-data-layer"
        
        try:
            response = requests.get(url, params={
                "symbols": ["BTCUSDT", "ETHUSDT"],
                "include_cache_status": True,
                "force_refresh": False
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 統一數據層測試成功")
                print(f"   • 同步符號數: {data['system_metrics']['synchronized_symbols']}")
                print(f"   • 數據質量: {data['system_metrics']['average_data_quality']:.3f}")
                print(f"   • 同步成功率: {data['system_metrics']['sync_success_rate']:.1%}")
                
                self.test_results["unified_data_layer"] = {
                    "status": "success",
                    "response_time": response.elapsed.total_seconds(),
                    "data_quality": data['system_metrics']['average_data_quality']
                }
                return True
            else:
                print(f"❌ 統一數據層測試失敗: HTTP {response.status_code}")
                self.test_results["unified_data_layer"] = {"status": "failed", "error": response.status_code}
                return False
                
        except Exception as e:
            print(f"❌ 統一數據層測試錯誤: {e}")
            self.test_results["unified_data_layer"] = {"status": "error", "error": str(e)}
            return False
    
    def test_realtime_sync_status(self):
        """測試實時同步狀態監控"""
        print("\n🔄 測試實時同步狀態...")
        
        url = f"{self.base_url}/api/v1/scalping/realtime-sync-status"
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 實時同步測試成功")
                print(f"   • 整體健康度: {data['overall_health']:.3f}")
                print(f"   • 系統狀態: {data['overall_status']}")
                print(f"   • 活躍數據源: {data['system_metrics']['active_sources']}/{data['system_metrics']['total_sources']}")
                print(f"   • 24小時錯誤數: {data['system_metrics']['total_errors_24h']}")
                
                self.test_results["realtime_sync"] = {
                    "status": "success",
                    "response_time": response.elapsed.total_seconds(),
                    "health_score": data['overall_health']
                }
                return True
            else:
                print(f"❌ 實時同步測試失敗: HTTP {response.status_code}")
                self.test_results["realtime_sync"] = {"status": "failed", "error": response.status_code}
                return False
                
        except Exception as e:
            print(f"❌ 實時同步測試錯誤: {e}")
            self.test_results["realtime_sync"] = {"status": "error", "error": str(e)}
            return False
    
    def test_performance_metrics(self):
        """測試性能監控系統"""
        print("\n📊 測試性能監控...")
        
        url = f"{self.base_url}/api/v1/scalping/performance-metrics"
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 性能監控測試成功")
                print(f"   • 整體性能評分: {data['overall_performance_score']:.3f}")
                print(f"   • 性能等級: {data['performance_grade']}")
                print(f"   • 平均響應時間: {data['performance_metrics']['api_performance']['average_response_time_ms']}ms")
                print(f"   • 成功率: {data['performance_metrics']['api_performance']['success_rate']:.1%}")
                
                self.test_results["performance_metrics"] = {
                    "status": "success",
                    "response_time": response.elapsed.total_seconds(),
                    "performance_score": data['overall_performance_score']
                }
                return True
            else:
                print(f"❌ 性能監控測試失敗: HTTP {response.status_code}")
                self.test_results["performance_metrics"] = {"status": "failed", "error": response.status_code}
                return False
                
        except Exception as e:
            print(f"❌ 性能監控測試錯誤: {e}")
            self.test_results["performance_metrics"] = {"status": "error", "error": str(e)}
            return False
    
    def test_phase1abc_integration(self):
        """測試 Phase 1ABC 整合狀態"""
        print("\n🎯 測試 Phase 1ABC 整合...")
        
        url = f"{self.base_url}/api/v1/scalping/phase1abc-integration-status"
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Phase 1ABC 整合測試成功")
                print(f"   • 整合狀態: {data['integration_status']}")
                print(f"   • Phase 1A 完成度: {data['implementation_completeness']['phase1a_completion']}")
                print(f"   • Phase 1B 完成度: {data['implementation_completeness']['phase1b_completion']}")
                print(f"   • Phase 1C 完成度: {data['implementation_completeness']['phase1c_completion']}")
                
                self.test_results["phase1abc_integration"] = {
                    "status": "success",
                    "response_time": response.elapsed.total_seconds(),
                    "integration_complete": data['implementation_completeness']['total_progress']
                }
                return True
            else:
                print(f"❌ Phase 1ABC 整合測試失敗: HTTP {response.status_code}")
                self.test_results["phase1abc_integration"] = {"status": "failed", "error": response.status_code}
                return False
                
        except Exception as e:
            print(f"❌ Phase 1ABC 整合測試錯誤: {e}")
            self.test_results["phase1abc_integration"] = {"status": "error", "error": str(e)}
            return False
    
    def run_comprehensive_test(self):
        """執行完整的第二階段測試"""
        print("🎯 狙擊手計劃 (Sniper Protocol) 第二階段綜合測試")
        print("=" * 70)
        print(f"📅 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 測試目標: {self.base_url}")
        
        # 測試項目
        tests = [
            ("Phase 1ABC 整合狀態", self.test_phase1abc_integration),
            ("統一數據層", self.test_unified_data_layer),
            ("實時同步狀態", self.test_realtime_sync_status),
            ("性能監控系統", self.test_performance_metrics)
        ]
        
        # 執行測試
        successful_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    successful_tests += 1
            except Exception as e:
                print(f"❌ {test_name} 測試異常: {e}")
        
        # 生成測試報告
        print(f"\n🎯 狙擊手計劃第二階段測試結果")
        print("=" * 70)
        print(f"📊 測試總結: {successful_tests}/{total_tests} 項測試通過")
        
        # 詳細結果
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result["status"] == "success" else "❌"
            print(f"{status_icon} {test_name}: {result['status'].upper()}")
            
            if result["status"] == "success" and "response_time" in result:
                print(f"    響應時間: {result['response_time']:.3f}s")
                
                # 顯示特定指標
                if "data_quality" in result:
                    print(f"    數據質量: {result['data_quality']:.3f}")
                elif "health_score" in result:
                    print(f"    健康評分: {result['health_score']:.3f}")
                elif "performance_score" in result:
                    print(f"    性能評分: {result['performance_score']:.3f}")
        
        # 整體評估
        success_rate = successful_tests / total_tests
        if success_rate == 1.0:
            overall_status = "🟢 EXCELLENT - 所有系統正常運行"
        elif success_rate >= 0.75:
            overall_status = "🟡 GOOD - 大部分系統正常"
        elif success_rate >= 0.5:
            overall_status = "🟠 WARNING - 部分系統異常"
        else:
            overall_status = "🔴 CRITICAL - 多個系統故障"
        
        print(f"\n🎯 狙擊手計劃第二階段系統狀態: {overall_status}")
        print(f"📈 成功率: {success_rate:.1%}")
        
        # 下一步建議
        print(f"\n📋 下一步行動:")
        if success_rate == 1.0:
            print("• 🚀 開始第三階段：WebSocket 長連接實現")
            print("• 📊 開始前端實時數據同步優化")
            print("• ⚡ 實施自適應刷新頻率機制")
        else:
            failed_tests = [name for name, result in self.test_results.items() if result["status"] != "success"]
            print(f"• 🔧 修復失敗的測試項目: {', '.join(failed_tests)}")
            print("• 🔄 重新運行測試")
            print("• 📞 檢查後端服務狀態")
        
        print(f"\n⏰ 測試完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return success_rate

def main():
    """主程序"""
    tester = SniperPhase2Tester()
    success_rate = tester.run_comprehensive_test()
    
    # 返回適當的退出代碼
    exit_code = 0 if success_rate >= 0.75 else 1
    exit(exit_code)

if __name__ == "__main__":
    main()
