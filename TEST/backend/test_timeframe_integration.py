#!/usr/bin/env python3
"""
測試短線信號交易策略整合性
驗證：
1. 短線信號是否依據 market_conditions_config.json 生成策略
2. 有效時間計算邏輯是否符合短線/極短線策略實現
3. 智能判斷而非固定測試數字
4. 確保產出格式不變，避免API錯誤
"""

import requests
import json
import time
import sqlite3
import os
import sys
from datetime import datetime, timedelta
import pytz
import pandas as pd
from typing import Dict, List, Any, Optional

# 添加項目根目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app.services.smart_timing_service import SmartTimingService
from app.services.market_analysis import MarketAnalysisService, MarketTrend, SignalDirection
from app.config.market_config_loader import MarketConditionConfig

# 台灣時區
TAIWAN_TZ = pytz.timezone('Asia/Taipei')

class TimeframeIntegrationTester:
    """時間框架整合測試器"""
    
    def __init__(self):
        self.config_loader = MarketConditionConfig()
        self.smart_timing = SmartTimingService()
        self.market_analysis = MarketAnalysisService()
        
        # 測試結果記錄
        self.test_results = {
            "config_validation": {},
            "timing_logic_validation": {},
            "signal_generation_tests": {},
            "api_format_validation": {},
            "smart_logic_tests": {}
        }
        
    def test_market_config_dependency(self) -> Dict[str, Any]:
        """測試1：驗證短線信號是否依據 market_conditions_config.json"""
        print("🔍 測試1：驗證市場配置依賴性")
        print("=" * 60)
        
        results = {}
        
        try:
            # 1. 檢查配置文件是否正確加載
            config = self.config_loader.config
            
            if not config:
                results["config_loading"] = {
                    "status": "FAILED",
                    "error": "market_conditions_config.json 未能正確加載"
                }
                return results
            
            # 2. 驗證策略配置是否包含短線策略
            bull_strategies = config.get('market_conditions', {}).get('bull', {}).get('strategies', {})
            sideway_strategies = config.get('market_conditions', {}).get('sideway', {}).get('strategies', {})
            bear_strategies = config.get('market_conditions', {}).get('bear', {}).get('strategies', {})
            
            short_term_strategies = []
            ultra_short_strategies = []
            
            # 檢查牛市策略
            for strategy_key, strategy_config in bull_strategies.items():
                classification = strategy_config.get('classification', '')
                if '短線' in classification:
                    short_term_strategies.append({
                        "market": "bull",
                        "strategy": strategy_key,
                        "classification": classification,
                        "timeframe": strategy_config.get('timeframe', ''),
                        "profit_target": strategy_config.get('exit', {}).get('profit_target', ''),
                        "time_limit": strategy_config.get('exit', {}).get('time_limit', '')
                    })
                elif '極短線' in classification:
                    ultra_short_strategies.append({
                        "market": "bull",
                        "strategy": strategy_key,
                        "classification": classification,
                        "timeframe": strategy_config.get('timeframe', ''),
                        "profit_target": strategy_config.get('exit', {}).get('profit_target', ''),
                        "time_limit": strategy_config.get('exit', {}).get('time_limit', '')
                    })
            
            # 檢查震盪市策略
            for strategy_key, strategy_config in sideway_strategies.items():
                classification = strategy_config.get('classification', '')
                if '短線' in classification:
                    short_term_strategies.append({
                        "market": "sideway",
                        "strategy": strategy_key,
                        "classification": classification,
                        "timeframe": strategy_config.get('timeframe', ''),
                        "profit_target": strategy_config.get('exit', {}).get('profit_target', ''),
                        "time_limit": strategy_config.get('exit', {}).get('time_limit', '')
                    })
                elif '極短線' in classification:
                    ultra_short_strategies.append({
                        "market": "sideway",
                        "strategy": strategy_key,
                        "classification": classification,
                        "timeframe": strategy_config.get('timeframe', ''),
                        "profit_target": strategy_config.get('exit', {}).get('profit_target', ''),
                        "time_limit": strategy_config.get('exit', {}).get('time_limit', '')
                    })
            
            # 檢查熊市策略
            for strategy_key, strategy_config in bear_strategies.items():
                classification = strategy_config.get('classification', '')
                if '短線' in classification:
                    short_term_strategies.append({
                        "market": "bear",
                        "strategy": strategy_key,
                        "classification": classification,
                        "timeframe": strategy_config.get('timeframe', ''),
                        "profit_target": strategy_config.get('exit', {}).get('profit_target', ''),
                        "time_limit": strategy_config.get('exit', {}).get('time_limit', '')
                    })
                elif '極短線' in classification:
                    ultra_short_strategies.append({
                        "market": "bear",
                        "strategy": strategy_key,
                        "classification": classification,
                        "timeframe": strategy_config.get('timeframe', ''),
                        "profit_target": strategy_config.get('exit', {}).get('profit_target', ''),
                        "time_limit": strategy_config.get('exit', {}).get('time_limit', '')
                    })
            
            # 3. 驗證風險管理配置
            risk_config = config.get('risk_management', {}).get('timeframe_based_sizing', {})
            ultra_short_risk = risk_config.get('ultra_short', {})
            short_term_risk = risk_config.get('short_term', {})
            
            results["config_loading"] = {
                "status": "SUCCESS",
                "total_strategies": len(bull_strategies) + len(sideway_strategies) + len(bear_strategies),
                "short_term_strategies_count": len(short_term_strategies),
                "ultra_short_strategies_count": len(ultra_short_strategies),
                "short_term_strategies": short_term_strategies,
                "ultra_short_strategies": ultra_short_strategies,
                "risk_management": {
                    "ultra_short": ultra_short_risk,
                    "short_term": short_term_risk
                }
            }
            
            # 4. 顯示配置驗證結果
            print(f"✅ 配置文件加載成功")
            print(f"📊 策略統計：")
            print(f"   - 短線策略: {len(short_term_strategies)} 個")
            print(f"   - 極短線策略: {len(ultra_short_strategies)} 個")
            
            for strategy in short_term_strategies:
                print(f"   🎯 短線策略: {strategy['strategy']} ({strategy['market']}市)")
                print(f"      時間框架: {strategy['timeframe']}")
                print(f"      時間限制: {strategy['time_limit']}")
            
            for strategy in ultra_short_strategies:
                print(f"   ⚡ 極短線策略: {strategy['strategy']} ({strategy['market']}市)")
                print(f"      時間框架: {strategy['timeframe']}")
                print(f"      時間限制: {strategy['time_limit']}")
            
        except Exception as e:
            results["config_loading"] = {
                "status": "ERROR",
                "error": str(e)
            }
            print(f"❌ 配置驗證失敗: {e}")
        
        return results
    
    def test_smart_timing_logic(self) -> Dict[str, Any]:
        """測試2：驗證有效時間計算邏輯是否符合策略實現"""
        print(f"\n🔍 測試2：驗證智能時間計算邏輯")
        print("=" * 60)
        
        results = {}
        test_cases = [
            # 極短線測試案例
            {"timeframe": "5m", "signal_strength": 0.95, "signal_type": "MOMENTUM_BREAKOUT", "expected_category": "極短線"},
            {"timeframe": "15m", "signal_strength": 0.88, "signal_type": "SCALPING", "expected_category": "極短線"},
            
            # 短線測試案例
            {"timeframe": "1h", "signal_strength": 0.82, "signal_type": "MOMENTUM_FOLLOW", "expected_category": "短線"},
            {"timeframe": "4h", "signal_strength": 0.75, "signal_type": "SWING_TRADE", "expected_category": "短線"},
        ]
        
        try:
            for i, case in enumerate(test_cases, 1):
                print(f"\n📊 測試案例 {i}: {case['expected_category']} - {case['timeframe']}")
                
                # 調用智能時間計算
                timing_result = self.smart_timing.calculate_smart_expiry_minutes(
                    base_timeframe=case['timeframe'],
                    signal_strength=case['signal_strength'],
                    signal_type=case['signal_type']
                )
                
                expiry_minutes = timing_result.get('expiry_minutes', 0)
                reasoning = timing_result.get('reasoning', '')
                calculation_details = timing_result.get('calculation_details', {})
                
                # 驗證時間邏輯
                if case['expected_category'] == '極短線':
                    # 極短線應該 5-60 分鐘
                    is_valid_timing = 5 <= expiry_minutes <= 60
                    expected_range = "5-60 分鐘"
                elif case['expected_category'] == '短線':
                    # 短線應該 30 分鐘 - 3 天 (4320 分鐘)
                    is_valid_timing = 30 <= expiry_minutes <= 4320
                    expected_range = "30-4320 分鐘"
                else:
                    is_valid_timing = False
                    expected_range = "未知"
                
                results[f"case_{i}"] = {
                    "test_case": case,
                    "result": timing_result,
                    "is_valid_timing": is_valid_timing,
                    "expected_range": expected_range,
                    "actual_minutes": expiry_minutes
                }
                
                print(f"   時間框架: {case['timeframe']}")
                print(f"   信號強度: {case['signal_strength']}")
                print(f"   計算結果: {expiry_minutes} 分鐘")
                print(f"   期望範圍: {expected_range}")
                print(f"   邏輯驗證: {'✅ 通過' if is_valid_timing else '❌ 失敗'}")
                print(f"   推理說明: {reasoning}")
                
                # 顯示計算細節
                if calculation_details:
                    print(f"   計算細節:")
                    for key, value in calculation_details.items():
                        if isinstance(value, float):
                            print(f"     {key}: {value:.3f}")
                        else:
                            print(f"     {key}: {value}")
            
        except Exception as e:
            results["error"] = str(e)
            print(f"❌ 智能時間測試失敗: {e}")
        
        return results
    
    def test_signal_generation_intelligence(self) -> Dict[str, Any]:
        """測試3：驗證信號生成的智能判斷邏輯"""
        print(f"\n🔍 測試3：驗證信號生成智能判斷")
        print("=" * 60)
        
        results = {}
        
        try:
            # 獲取當前活躍信號
            response = requests.get("http://localhost:8000/api/v1/scalping/signals", timeout=10)
            
            if response.status_code != 200:
                results["api_connection"] = {
                    "status": "FAILED",
                    "error": f"API 響應錯誤: {response.status_code}"
                }
                return results
            
            data = response.json()
            signals = data.get('signals', []) if isinstance(data, dict) else data if isinstance(data, list) else []
            
            print(f"📊 獲取到 {len(signals)} 個活躍信號")
            
            # 分析每個信號的智能程度
            signal_analysis = []
            
            for signal in signals:
                symbol = signal.get('symbol', '')
                timeframe = signal.get('timeframe', '')
                confidence = signal.get('confidence', 0)
                precision_score = signal.get('precision_score', 0)
                strategy_name = signal.get('strategy_name', '')
                
                # 檢查有效時間計算
                created_at = signal.get('created_at', '')
                expires_at = signal.get('expires_at', '')
                
                if created_at and expires_at:
                    try:
                        created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        expire_time = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                        duration_minutes = (expire_time - created_time).total_seconds() / 60
                    except:
                        duration_minutes = 0
                else:
                    duration_minutes = 0
                
                # 判斷智能化程度
                intelligence_score = 0
                intelligence_factors = []
                
                # 1. 信心度是否在合理範圍且有變化
                if 0.7 <= confidence <= 0.95:
                    intelligence_score += 25
                    intelligence_factors.append("信心度合理")
                elif confidence == 0.8 or confidence == 0.85:
                    # 固定值可能是測試數據
                    intelligence_factors.append("信心度可能為固定值")
                else:
                    intelligence_score += 10
                    intelligence_factors.append("信心度範圍異常")
                
                # 2. 精準度評分是否有細微差異
                if precision_score > 0 and precision_score != 0.9:
                    intelligence_score += 25
                    intelligence_factors.append("精準度有變化")
                else:
                    intelligence_factors.append("精準度可能為固定值")
                
                # 3. 策略名稱是否反映具體策略
                if '測試' not in strategy_name and strategy_name != '精準篩選':
                    intelligence_score += 20
                    intelligence_factors.append("策略名稱具體")
                else:
                    intelligence_factors.append("策略名稱通用")
                
                # 4. 時間框架與有效時間的匹配度
                timeframe_expected = {
                    '1m': (3, 15), '5m': (8, 30), '15m': (15, 60), '30m': (30, 120), '1h': (60, 240)
                }
                
                if timeframe in timeframe_expected:
                    min_expected, max_expected = timeframe_expected[timeframe]
                    if min_expected <= duration_minutes <= max_expected:
                        intelligence_score += 30
                        intelligence_factors.append("有效時間匹配")
                    else:
                        intelligence_factors.append(f"有效時間不匹配({duration_minutes:.1f}分鐘)")
                
                signal_analysis.append({
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "confidence": confidence,
                    "precision_score": precision_score,
                    "strategy_name": strategy_name,
                    "duration_minutes": duration_minutes,
                    "intelligence_score": intelligence_score,
                    "intelligence_factors": intelligence_factors,
                    "is_intelligent": intelligence_score >= 70
                })
                
                print(f"\n🎯 {symbol} ({timeframe}):")
                print(f"   信心度: {confidence:.3f}")
                print(f"   精準度: {precision_score:.3f}")
                print(f"   策略: {strategy_name}")
                print(f"   有效時間: {duration_minutes:.1f} 分鐘")
                print(f"   智能評分: {intelligence_score}/100")
                print(f"   智能判斷: {'✅ 是' if intelligence_score >= 70 else '❌ 否'}")
                
                for factor in intelligence_factors:
                    print(f"     - {factor}")
            
            # 統計智能化程度
            intelligent_signals = [s for s in signal_analysis if s['is_intelligent']]
            intelligence_rate = len(intelligent_signals) / len(signal_analysis) if signal_analysis else 0
            
            results = {
                "total_signals": len(signals),
                "signal_analysis": signal_analysis,
                "intelligent_signals_count": len(intelligent_signals),
                "intelligence_rate": intelligence_rate,
                "overall_assessment": "INTELLIGENT" if intelligence_rate >= 0.7 else "MIXED" if intelligence_rate >= 0.3 else "BASIC"
            }
            
            print(f"\n📊 智能化評估:")
            print(f"   總信號數: {len(signals)}")
            print(f"   智能信號: {len(intelligent_signals)}")
            print(f"   智能化率: {intelligence_rate:.1%}")
            print(f"   整體評估: {results['overall_assessment']}")
            
        except Exception as e:
            results["error"] = str(e)
            print(f"❌ 信號智能判斷測試失敗: {e}")
        
        return results
    
    def test_api_format_consistency(self) -> Dict[str, Any]:
        """測試4：驗證API格式一致性"""
        print(f"\n🔍 測試4：驗證API格式一致性")
        print("=" * 60)
        
        results = {}
        
        try:
            # 測試主要API端點
            endpoints = [
                {"url": "http://localhost:8000/api/v1/scalping/signals", "name": "活躍信號"},
                {"url": "http://localhost:8000/api/v1/scalping/dashboard-precision-signals", "name": "儀表板信號"},
                {"url": "http://localhost:8000/api/v1/scalping/expired", "name": "歷史信號"}
            ]
            
            expected_fields = [
                'id', 'symbol', 'timeframe', 'signal_type', 'confidence',
                'entry_price', 'strategy_name', 'created_at'
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint['url'], timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        signals = data.get('signals', []) if isinstance(data, dict) else data if isinstance(data, list) else []
                        
                        # 檢查格式一致性
                        format_issues = []
                        
                        for i, signal in enumerate(signals[:3]):  # 檢查前3個信號
                            missing_fields = []
                            for field in expected_fields:
                                if field not in signal:
                                    missing_fields.append(field)
                            
                            if missing_fields:
                                format_issues.append({
                                    "signal_index": i,
                                    "missing_fields": missing_fields
                                })
                        
                        results[endpoint['name']] = {
                            "status": "SUCCESS",
                            "response_code": response.status_code,
                            "signals_count": len(signals),
                            "format_issues": format_issues,
                            "is_format_consistent": len(format_issues) == 0
                        }
                        
                        print(f"✅ {endpoint['name']}: {len(signals)} 個信號")
                        if format_issues:
                            print(f"   ⚠️ 格式問題: {len(format_issues)} 處")
                            for issue in format_issues:
                                print(f"     信號 {issue['signal_index']}: 缺少 {issue['missing_fields']}")
                        else:
                            print(f"   ✅ 格式一致")
                        
                    else:
                        results[endpoint['name']] = {
                            "status": "FAILED",
                            "response_code": response.status_code,
                            "error": f"HTTP {response.status_code}"
                        }
                        print(f"❌ {endpoint['name']}: HTTP {response.status_code}")
                
                except Exception as e:
                    results[endpoint['name']] = {
                        "status": "ERROR",
                        "error": str(e)
                    }
                    print(f"❌ {endpoint['name']}: {e}")
            
        except Exception as e:
            results["error"] = str(e)
            print(f"❌ API格式測試失敗: {e}")
        
        return results
    
    def run_comprehensive_test(self):
        """運行完整的綜合測試"""
        print("🚀 短線信號交易策略整合測試")
        print("=" * 80)
        print("📋 測試目標:")
        print("   1. 驗證短線信號是否依據 market_conditions_config.json")
        print("   2. 檢查有效時間計算邏輯是否符合短線/極短線策略")
        print("   3. 確認系統使用智能判斷而非固定測試數字")
        print("   4. 驗證API格式一致性，確保無破壞性變更")
        print("=" * 80)
        
        # 運行各項測試
        self.test_results["config_validation"] = self.test_market_config_dependency()
        self.test_results["timing_logic_validation"] = self.test_smart_timing_logic()
        self.test_results["signal_generation_tests"] = self.test_signal_generation_intelligence()
        self.test_results["api_format_validation"] = self.test_api_format_consistency()
        
        # 生成綜合報告
        self.generate_comprehensive_report()
    
    def generate_comprehensive_report(self):
        """生成綜合測試報告"""
        print(f"\n" + "=" * 80)
        print("📊 綜合測試報告")
        print("=" * 80)
        
        # 測試1：配置依賴性
        config_test = self.test_results.get("config_validation", {})
        if config_test.get("config_loading", {}).get("status") == "SUCCESS":
            short_count = config_test["config_loading"]["short_term_strategies_count"]
            ultra_count = config_test["config_loading"]["ultra_short_strategies_count"]
            print(f"✅ 測試1 - 配置依賴性: 通過")
            print(f"   📊 短線策略: {short_count} 個, 極短線策略: {ultra_count} 個")
        else:
            print(f"❌ 測試1 - 配置依賴性: 失敗")
        
        # 測試2：時間邏輯
        timing_test = self.test_results.get("timing_logic_validation", {})
        valid_cases = 0
        total_cases = 0
        for key, value in timing_test.items():
            if key.startswith("case_") and isinstance(value, dict):
                total_cases += 1
                if value.get("is_valid_timing", False):
                    valid_cases += 1
        
        if total_cases > 0:
            timing_rate = valid_cases / total_cases
            print(f"{'✅' if timing_rate >= 0.8 else '⚠️'} 測試2 - 時間邏輯: {valid_cases}/{total_cases} 通過 ({timing_rate:.1%})")
        else:
            print(f"❌ 測試2 - 時間邏輯: 測試失敗")
        
        # 測試3：智能判斷
        intelligence_test = self.test_results.get("signal_generation_tests", {})
        if "intelligence_rate" in intelligence_test:
            intel_rate = intelligence_test["intelligence_rate"]
            assessment = intelligence_test["overall_assessment"]
            print(f"{'✅' if intel_rate >= 0.7 else '⚠️'} 測試3 - 智能判斷: {intel_rate:.1%} 智能化率 ({assessment})")
        else:
            print(f"❌ 測試3 - 智能判斷: 測試失敗")
        
        # 測試4：API格式
        format_test = self.test_results.get("api_format_validation", {})
        format_success = 0
        format_total = 0
        for endpoint_name, endpoint_result in format_test.items():
            if endpoint_name != "error" and isinstance(endpoint_result, dict):
                format_total += 1
                if endpoint_result.get("is_format_consistent", False):
                    format_success += 1
        
        if format_total > 0:
            format_rate = format_success / format_total
            print(f"{'✅' if format_rate == 1.0 else '⚠️'} 測試4 - API格式: {format_success}/{format_total} 一致 ({format_rate:.1%})")
        else:
            print(f"❌ 測試4 - API格式: 測試失敗")
        
        # 總結建議
        print(f"\n📋 總結建議:")
        
        if config_test.get("config_loading", {}).get("status") == "SUCCESS":
            print(f"✅ 系統正確依賴 market_conditions_config.json")
        else:
            print(f"🔧 建議檢查配置文件加載邏輯")
        
        if timing_rate >= 0.8 if 'timing_rate' in locals() else False:
            print(f"✅ 時間計算邏輯符合短線策略要求")
        else:
            print(f"🔧 建議調整智能時間計算參數")
        
        if intel_rate >= 0.7 if 'intel_rate' in locals() else False:
            print(f"✅ 信號生成具備智能判斷能力")
        else:
            print(f"🔧 建議增強信號生成的動態性")
        
        if format_rate == 1.0 if 'format_rate' in locals() else False:
            print(f"✅ API格式保持一致，無破壞性變更")
        else:
            print(f"🔧 建議檢查API響應格式")
        
        print("=" * 80)

def main():
    """主函數"""
    print("🧪 短線信號交易策略整合測試啟動")
    
    try:
        tester = TimeframeIntegrationTester()
        tester.run_comprehensive_test()
        
    except KeyboardInterrupt:
        print(f"\n\n🛑 測試被用戶中止")
    except Exception as e:
        print(f"\n\n❌ 測試過程中出現錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
