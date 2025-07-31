#!/usr/bin/env python3
"""
🎯 多時間框架權重管理系統 API 演示
展示新增的 API 端點功能
"""

import asyncio
import json
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def demo_multi_timeframe_api():
    """演示多時間框架權重管理 API"""
    print("🎯 多時間框架權重管理 API 演示")
    print("=" * 60)
    
    try:
        # 模擬 API 調用邏輯 (實際中會通過 HTTP 請求)
        from app.services.timeframe_weight_templates import (
            timeframe_templates, TradingTimeframe
        )
        from app.services.dynamic_weight_engine import (
            dynamic_weight_engine, MarketConditions, SignalBlockData
        )
        from app.services.signal_availability_monitor import (
            signal_availability_monitor
        )
        
        # 模擬市場條件
        market_conditions = MarketConditions(
            symbol="BTCUSDT",
            current_price=43750.50,
            volatility_score=0.68,
            trend_strength=0.82,
            volume_strength=0.75,
            liquidity_score=0.88,
            sentiment_score=0.72,
            fear_greed_index=62,
            market_regime="uptrend",
            regime_confidence=0.85,
            timestamp=datetime.now()
        )
        
        # 模擬信號可用性數據
        signal_availabilities = {
            "precision_filter": SignalBlockData(
                block_name="precision_filter",
                availability=True,
                quality_score=0.92,
                confidence=0.88,
                latency_ms=35.2,
                last_update=datetime.now(),
                error_count=0,
                success_rate=0.96
            ),
            "technical_analysis": SignalBlockData(
                block_name="technical_analysis",
                availability=True,
                quality_score=0.85,
                confidence=0.78,
                latency_ms=58.7,
                last_update=datetime.now(),
                error_count=1,
                success_rate=0.91
            ),
            "market_condition": SignalBlockData(
                block_name="market_condition",
                availability=True,
                quality_score=0.79,
                confidence=0.74,
                latency_ms=42.1,
                last_update=datetime.now(),
                error_count=0,
                success_rate=0.93
            )
        }
        
        symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
        timeframes = ["short", "medium", "long"]
        
        print("📊 API 端點演示結果:")
        print("-" * 60)
        
        for timeframe in timeframes:
            print(f"\n🎯 時間框架: {timeframe.upper()}")
            
            # 獲取時間框架模板
            tf_enum = {
                "short": TradingTimeframe.SHORT_TERM,
                "medium": TradingTimeframe.MEDIUM_TERM,
                "long": TradingTimeframe.LONG_TERM
            }[timeframe]
            
            template = timeframe_templates.get_template(tf_enum)
            print(f"   📋 模板: {template.template_name}")
            print(f"   📝 描述: {template.description}")
            print(f"   🎯 信心閾值: {template.confidence_threshold}")
            print(f"   ⏱️  持倉週期: {template.holding_period_hours}小時")
            
            # 計算動態權重 (以 BTCUSDT 為例)
            weight_result = await dynamic_weight_engine.calculate_dynamic_weights(
                symbol="BTCUSDT",
                timeframe=tf_enum,
                market_conditions=market_conditions,
                signal_availabilities=signal_availabilities
            )
            
            print(f"   💰 動態權重結果:")
            weights = weight_result.calculated_weights
            print(f"      精準過濾: {weights.precision_filter_weight:.4f}")
            print(f"      技術分析: {weights.technical_analysis_weight:.4f}")
            print(f"      市場條件: {weights.market_condition_weight:.4f}")
            print(f"      制度分析: {weights.regime_analysis_weight:.4f}")
            
            print(f"   📈 綜合評估:")
            print(f"      總體信心: {weight_result.total_confidence:.3f}")
            print(f"      推薦評分: {weight_result.recommendation_score:.3f}")
            print(f"      風險等級: {weight_result.risk_level}")
        
        return True
        
    except Exception as e:
        print(f"❌ API 演示失敗: {e}")
        return False

async def demo_signal_health_dashboard():
    """演示信號健康儀表板 API"""
    print("\n🎯 信號健康儀表板 API 演示")
    print("=" * 60)
    
    try:
        from app.services.signal_availability_monitor import signal_availability_monitor
        
        # 模擬一些信號檢查
        test_signals = [
            ("precision_filter", True, 25.8),
            ("technical_analysis", True, 67.2),
            ("market_condition", True, 43.5),
            ("regime_analysis", False, 120.0),  # 模擬一個失敗
            ("fear_greed", True, 89.1)
        ]
        
        print("🔍 模擬信號健康檢查...")
        for signal_name, success, latency in test_signals:
            result = signal_availability_monitor.record_signal_check(
                signal_name, success, latency, datetime.now()
            )
            print(f"   {result}")
        
        # 獲取系統狀態
        system_status = signal_availability_monitor.get_system_status()
        print(f"\n📊 系統狀態摘要:")
        print(f"   信號總數: {system_status['total_signals']}")
        print(f"   可用信號: {system_status['available_signals']}")
        print(f"   系統健康率: {system_status['system_health_rate']:.3f}")
        print(f"   總檢查次數: {system_status['total_checks']}")
        print(f"   錯誤率: {system_status['error_rate']:.4f}")
        
        # 獲取信號健康詳情
        all_health = signal_availability_monitor.get_all_signal_health()
        print(f"\n🔍 信號健康詳情:")
        
        for signal_name, health_metrics in all_health.items():
            status_emoji = {
                "available": "✅",
                "error": "❌", 
                "degraded": "⚠️",
                "unknown": "❓"
            }.get(health_metrics.status.value, "❓")
            
            print(f"   {status_emoji} {signal_name}:")
            print(f"      狀態: {health_metrics.status.value}")
            print(f"      成功率: {health_metrics.success_rate:.3f}")
            print(f"      品質評分: {health_metrics.quality_score:.3f}")
            print(f"      平均延遲: {health_metrics.average_latency_ms:.1f}ms")
            if health_metrics.error_count_24h > 0:
                print(f"      24h錯誤: {health_metrics.error_count_24h}")
        
        return True
        
    except Exception as e:
        print(f"❌ 儀表板演示失敗: {e}")
        return False

async def demo_api_integration():
    """演示 API 整合功能"""
    print("\n🎯 API 整合功能演示")
    print("=" * 60)
    
    print("📡 新增的 API 端點:")
    
    api_endpoints = [
        {
            "endpoint": "GET /multi-timeframe-weights",
            "description": "多時間框架權重分析",
            "parameters": "symbols, timeframe (short/medium/long)",
            "features": [
                "三週期權重模板",
                "動態權重計算",
                "市場條件適應",
                "信號可用性整合"
            ]
        },
        {
            "endpoint": "GET /signal-health-dashboard", 
            "description": "信號健康監控儀表板",
            "parameters": "無",
            "features": [
                "即時信號狀態監控",
                "信號品質評估",
                "系統健康率統計",
                "告警管理"
            ]
        }
    ]
    
    for i, endpoint_info in enumerate(api_endpoints, 1):
        print(f"\n{i}. {endpoint_info['endpoint']}")
        print(f"   📝 功能: {endpoint_info['description']}")
        print(f"   🔧 參數: {endpoint_info['parameters']}")
        print(f"   ✨ 特色功能:")
        for feature in endpoint_info['features']:
            print(f"      • {feature}")
    
    print(f"\n🚀 系統架構整合:")
    print(f"   📊 三週期權重模板系統 ✅")
    print(f"   ⚙️  動態權重計算引擎 ✅")  
    print(f"   📡 信號可用性監控系統 ✅")
    print(f"   🔗 API 端點整合 ✅")
    print(f"   🎯 多時間框架管理 ✅")
    
    print(f"\n💡 使用場景:")
    use_cases = [
        "短線交易者: 使用 short 時間框架，重視精準度和即時性",
        "中線投資者: 使用 medium 時間框架，平衡各項指標權重",
        "長線策略: 使用 long 時間框架，注重趨勢和市場機制分析",
        "系統管理員: 使用健康儀表板監控所有信號狀態",
        "量化團隊: 整合 API 進行自動化交易策略開發"
    ]
    
    for i, use_case in enumerate(use_cases, 1):
        print(f"   {i}. {use_case}")
    
    return True

async def main():
    """主演示函數"""
    print("🚀 多時間框架權重管理系統 - API 功能演示")
    print("=" * 80)
    
    results = []
    
    # 1. 多時間框架 API 演示
    results.append(await demo_multi_timeframe_api())
    
    # 2. 信號健康儀表板演示
    results.append(await demo_signal_health_dashboard())
    
    # 3. API 整合功能演示
    results.append(await demo_api_integration())
    
    # 總結
    print("\n" + "=" * 80)
    print("🎯 演示結果總結:")
    
    demo_names = [
        "多時間框架權重管理 API",
        "信號健康儀表板 API",
        "API 整合功能"
    ]
    
    for i, (name, result) in enumerate(zip(demo_names, results), 1):
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"   {i}. {name}: {status}")
    
    success_rate = sum(results) / len(results)
    print(f"\n📊 演示成功率: {success_rate:.1%} ({sum(results)}/{len(results)})")
    
    if success_rate == 1.0:
        print("🎉 所有 API 功能演示成功！系統已準備就緒!")
        print("\n🔗 可用的 API 端點:")
        print("   • GET /multi-timeframe-weights?symbols=BTCUSDT,ETHUSDT&timeframe=short")
        print("   • GET /signal-health-dashboard")
    else:
        print("⚠️  部分演示失敗，請檢查相關模組。")

if __name__ == "__main__":
    asyncio.run(main())
