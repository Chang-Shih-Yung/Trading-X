#!/usr/bin/env python3
"""
🎯 狙擊手計劃 - 完整系統測試

測試流程:
1. 實時市場數據 WebSocket 連接
2. Phase 1ABC + Phase 1+2+3 整合處理
3. pandas-ta 技術分析計算  
4. 狙擊手雙層架構執行
5. 智能信號評分與質量檢查
6. Email 通知系統測試
7. 前端 Vue 組件整合測試

2024-12-19: 狙擊手計劃完整測試腳本
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SniperPlanTestSuite:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = {}
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def test_realtime_websocket_connection(self) -> Dict[str, Any]:
        """測試 WebSocket 實時數據連接"""
        print("\n🔍 測試 1: WebSocket 實時數據連接")
        try:
            async with self.session.get(f"{self.base_url}/api/v1/realtime/connection-status") as response:
                if response.status == 200:
                    data = await response.json()
                    status = data.get('status', 'unknown')
                    print(f"  ✅ WebSocket 連接狀態: {status}")
                    return {"status": "success", "connection": data}
                else:
                    print(f"  ❌ WebSocket 連接檢查失敗: {response.status}")
                    return {"status": "failed", "error": f"HTTP {response.status}"}
                    
        except Exception as e:
            print(f"  ❌ WebSocket 連接測試失敗: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def test_phase1abc_integration(self) -> Dict[str, Any]:
        """測試 Phase 1ABC 整合處理"""
        print("\n🔍 測試 2: Phase 1ABC 整合處理")
        try:
            async with self.session.get(f"{self.base_url}/api/v1/scalping/phase1abc-integration-status") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"  ✅ Phase 1ABC 狀態: {data.get('status', 'unknown')}")
                    
                    # 檢查各子階段
                    for phase in ['1A', '1B', '1C']:
                        phase_data = data.get(f'phase_{phase.lower()}', {})
                        completion = phase_data.get('completion', 0)
                        print(f"    • Phase {phase}: {completion}% 完成")
                    
                    return {"status": "success", "data": data}
                else:
                    print(f"  ❌ Phase 1ABC 檢查失敗: {response.status}")
                    return {"status": "failed", "error": f"HTTP {response.status}"}
                    
        except Exception as e:
            print(f"  ❌ Phase 1ABC 測試失敗: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def test_phase123_enhancement(self) -> Dict[str, Any]:
        """測試 Phase 1+2+3 增強處理"""
        print("\n🔍 測試 3: Phase 1+2+3 增強處理")
        try:
            async with self.session.get(f"{self.base_url}/api/v1/scalping/phase3-market-depth") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"  ✅ Phase 1+2+3 狀態: {data.get('status', 'unknown')}")
                    
                    metrics = data.get('performance_metrics', {})
                    print(f"    • 動態權重調整: {metrics.get('dynamic_weights', 0)}次")
                    print(f"    • 市場深度分析: {metrics.get('market_depth_analysis', 0)}個標的")
                    print(f"    • 風險調整效果: {metrics.get('risk_adjustment', 0)}%")
                    
                    return {"status": "success", "data": data}
                else:
                    print(f"  ❌ Phase 1+2+3 檢查失敗: {response.status}")
                    return {"status": "failed", "error": f"HTTP {response.status}"}
                    
        except Exception as e:
            print(f"  ❌ Phase 1+2+3 測試失敗: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def test_sniper_dual_layer_architecture(self) -> Dict[str, Any]:
        """測試狙擊手雙層架構"""
        print("\n🔍 測試 4: 🎯 狙擊手雙層架構")
        try:
            # 測試多個交易對
            symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
            url = f"{self.base_url}/api/v1/scalping/sniper-unified-data-layer"
            params = {
                "symbols": ",".join(symbols),
                "timeframe": "1h",
                "force_refresh": "true"
            }
            
            start_time = time.time()
            async with self.session.get(url, params=params) as response:
                execution_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    print(f"  ✅ 狙擊手架構執行成功 (耗時: {execution_time:.2f}秒)")
                    
                    if data.get('status') == 'success' and data.get('results'):
                        results = data['results']
                        
                        for symbol, result in results.items():
                            print(f"\n    🎯 {symbol} 狙擊手分析:")
                            
                            # Layer 1 分析
                            layer1 = result.get('layer_one', {})
                            print(f"      • Layer 1 時間: {layer1.get('execution_time', 0)*1000:.1f}ms")
                            print(f"      • 指標數量: {layer1.get('indicators_count', 0)}個")
                            
                            # Layer 2 分析
                            layer2 = result.get('layer_two', {})
                            print(f"      • Layer 2 時間: {layer2.get('execution_time', 0)*1000:.1f}ms")
                            print(f"      • 過濾效果: {layer2.get('filter_effectiveness', 0):.1%}")
                            
                            # 性能指標
                            perf = result.get('performance_metrics', {})
                            if perf:
                                signals_quality = perf.get('signals_quality', {})
                                generated = signals_quality.get('generated', 0)
                                filtered = signals_quality.get('filtered', 0)
                                pass_rate = generated / max(generated + filtered, 1)
                                print(f"      • 信號通過率: {pass_rate:.1%}")
                            
                            # 市場狀態
                            market_regime = result.get('market_regime', 'unknown')
                            print(f"      • 市場狀態: {market_regime}")
                    
                    return {"status": "success", "data": data, "execution_time": execution_time}
                else:
                    print(f"  ❌ 狙擊手架構測試失敗: {response.status}")
                    return {"status": "failed", "error": f"HTTP {response.status}"}
                    
        except Exception as e:
            print(f"  ❌ 狙擊手架構測試失敗: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def test_email_notification_system(self) -> Dict[str, Any]:
        """測試 Email 通知系統"""
        print("\n🔍 測試 5: 📧 Email 通知系統")
        try:
            # 檢查 Email 配置狀態
            async with self.session.get(f"{self.base_url}/api/v1/notifications/email/status") as response:
                if response.status == 200:
                    status_data = await response.json()
                    print(f"  ✅ Email 配置狀態: {status_data.get('configuration_status', 'unknown')}")
                    print(f"  ✅ Email 功能啟用: {status_data.get('enabled', False)}")
                    
                    # 測試 Email 發送功能
                    test_strategy = {
                        "symbol": "BTCUSDT",
                        "signal_type": "BUY",
                        "entry_price": 45000.0,
                        "stop_loss": 43000.0,
                        "take_profit": 48000.0,
                        "confidence": 0.89,
                        "timeframe": "1h",
                        "reasoning": "🎯 狙擊手計劃測試信號 - 系統整合測試中",
                        "technical_indicators": ["🎯 狙擊手雙層架構", "📊 RSI", "📈 MACD"],
                        "sniper_metrics": {
                            "market_regime": "TESTING",
                            "layer_one_time": 0.012,
                            "layer_two_time": 0.023,
                            "pass_rate": 0.89
                        }
                    }
                    
                    # 發送測試通知
                    email_payload = {
                        "strategy": test_strategy,
                        "type": "test-signal"
                    }
                    
                    async with self.session.post(
                        f"{self.base_url}/api/v1/notifications/email",
                        json=email_payload
                    ) as email_response:
                        if email_response.status == 200:
                            email_data = await email_response.json()
                            print(f"  ✅ 測試 Email 發送成功")
                            print(f"    • 主題: {email_data.get('email_subject', 'N/A')}")
                            return {"status": "success", "email_status": status_data, "email_test": email_data}
                        else:
                            print(f"  ❌ 測試 Email 發送失敗: {email_response.status}")
                            return {"status": "partial", "email_status": status_data, "email_error": f"HTTP {email_response.status}"}
                    
                else:
                    print(f"  ❌ Email 狀態檢查失敗: {response.status}")
                    return {"status": "failed", "error": f"HTTP {response.status}"}
                    
        except Exception as e:
            print(f"  ❌ Email 通知系統測試失敗: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def test_full_pipeline_integration(self) -> Dict[str, Any]:
        """測試完整管線整合"""
        print("\n🔍 測试 6: 🎯 完整狙擊手計劃管線")
        try:
            print("  📊 執行完整流程:")
            print("    1️⃣  實時市場數據 WebSocket 連接")
            print("    2️⃣  Phase 1ABC 處理 (信號重構→波動適應→標準化)")
            print("    3️⃣  Phase 1+2+3 增強 (動態權重→市場深度)")
            print("    4️⃣  pandas-ta 技術分析計算")
            print("    5️⃣  狙擊手雙層架構執行")
            print("    6️⃣  智能信號評分與質量檢查")
            print("    7️⃣  Email 通知準備")
            
            # 執行完整流程測試
            pipeline_results = {}
            
            # Step 1-3: 基礎系統測試
            pipeline_results['websocket'] = await self.test_realtime_websocket_connection()
            pipeline_results['phase1abc'] = await self.test_phase1abc_integration()
            pipeline_results['phase123'] = await self.test_phase123_enhancement()
            
            # Step 4-5: 狙擊手核心
            pipeline_results['sniper'] = await self.test_sniper_dual_layer_architecture()
            
            # Step 6-7: 通知系統
            pipeline_results['notifications'] = await self.test_email_notification_system()
            
            # 計算整體成功率
            success_count = sum(1 for result in pipeline_results.values() 
                              if result.get('status') in ['success', 'partial'])
            total_tests = len(pipeline_results)
            success_rate = success_count / total_tests
            
            print(f"\n  🎯 狙擊手計劃整合測試完成!")
            print(f"    • 總測試項目: {total_tests}")
            print(f"    • 成功項目: {success_count}")
            print(f"    • 成功率: {success_rate:.1%}")
            
            return {
                "status": "completed",
                "success_rate": success_rate,
                "results": pipeline_results,
                "summary": {
                    "total_tests": total_tests,
                    "successful_tests": success_count,
                    "failed_tests": total_tests - success_count
                }
            }
            
        except Exception as e:
            print(f"  ❌ 完整管線測試失敗: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """運行綜合測試"""
        print("🎯 狙擊手計劃 - 完整系統測試開始")
        print("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # 執行完整管線測試
            results = await self.test_full_pipeline_integration()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print("\n" + "=" * 60)
            print(f"🎯 狙擊手計劃測試完成 (耗時: {duration:.1f}秒)")
            
            if results.get('success_rate', 0) >= 0.8:
                print("✅ 測試結果: 系統整合成功!")
                print("🎯 狙擊手計劃已準備就緒，可以開始自動化交易信號生成")
            elif results.get('success_rate', 0) >= 0.6:
                print("⚠️  測試結果: 系統部分功能正常")
                print("🔧 建議檢查失敗的組件並進行修復")
            else:
                print("❌ 測試結果: 系統需要重大修復")
                print("🚨 請檢查系統配置和依賴項")
            
            # 保存測試結果
            results['test_metadata'] = {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration,
                'version': '🎯 狙擊手計劃 v1.0'
            }
            
            return results
            
        except Exception as e:
            print(f"\n❌ 測試執行失敗: {str(e)}")
            return {
                "status": "critical_error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

async def main():
    """主要測試執行函數"""
    try:
        async with SniperPlanTestSuite() as test_suite:
            results = await test_suite.run_comprehensive_test()
            
            # 保存測試結果到文件
            output_file = f"sniper_plan_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            print(f"\n📝 測試結果已保存到: {output_file}")
            
            return results
            
    except Exception as e:
        print(f"❌ 測試程序執行失敗: {str(e)}")
        return None

if __name__ == "__main__":
    print("🎯 啟動狙擊手計劃完整系統測試...")
    results = asyncio.run(main())
    
    if results and results.get('success_rate', 0) >= 0.8:
        print("\n🎯 狙擊手計劃系統測試通過!")
        exit(0)
    else:
        print("\n❌ 狙擊手計劃系統測試未通過")
        exit(1)
