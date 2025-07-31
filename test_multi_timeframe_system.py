#!/usr/bin/env python3
"""
🎯 多時間框架權重管理系統測試
驗證三週期權重模板、動態權重引擎和信號可用性監控
"""

import asyncio
import json
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_timeframe_templates():
    """測試三週期權重模板"""
    print("🎯 測試三週期權重模板系統")
    print("=" * 60)
    
    try:
        from app.services.timeframe_weight_templates import (
            timeframe_templates, TradingTimeframe
        )
        
        # 測試短線模板
        short_template = timeframe_templates.get_template(TradingTimeframe.SHORT_TERM)
        print(f"📊 短線模板:")
        print(f"   名稱: {short_template.template_name}")
        print(f"   描述: {short_template.description}")
        print(f"   信心閾值: {short_template.confidence_threshold}")
        print(f"   風險容忍度: {short_template.risk_tolerance}")
        print(f"   持倉週期: {short_template.holding_period_hours}小時")
        
        # 測試中線模板
        medium_template = timeframe_templates.get_template(TradingTimeframe.MEDIUM_TERM)
        print(f"\n📊 中線模板:")
        print(f"   名稱: {medium_template.template_name}")
        print(f"   描述: {medium_template.description}")
        print(f"   信心閾值: {medium_template.confidence_threshold}")
        print(f"   風險容忍度: {medium_template.risk_tolerance}")
        print(f"   持倉週期: {medium_template.holding_period_hours}小時")
        
        # 測試長線模板
        long_template = timeframe_templates.get_template(TradingTimeframe.LONG_TERM)
        print(f"\n📊 長線模板:")
        print(f"   名稱: {long_template.template_name}")
        print(f"   描述: {long_template.description}")
        print(f"   信心閾值: {long_template.confidence_threshold}")
        print(f"   風險容忍度: {long_template.risk_tolerance}")
        print(f"   持倉週期: {long_template.holding_period_hours}小時")
        
        # 測試權重值
        print(f"\n🎯 短線權重配置:")
        weights = short_template.signal_weights
        print(f"   精準過濾: {weights.precision_filter_weight:.3f}")
        print(f"   技術分析: {weights.technical_analysis_weight:.3f}")
        print(f"   市場深度: {weights.market_depth_weight:.3f}")
        print(f"   資金費率: {weights.funding_rate_weight:.3f}")
        
        print("✅ 三週期權重模板測試成功!")
        return True
        
    except Exception as e:
        print(f"❌ 三週期權重模板測試失敗: {e}")
        return False

def test_signal_monitor():
    """測試信號可用性監控"""
    print("\n🎯 測試信號可用性監控系統")
    print("=" * 60)
    
    try:
        from app.services.signal_availability_monitor import (
            signal_availability_monitor, SignalStatus
        )
        
        # 初始化監控系統
        print("🚀 初始化信號監控系統...")
        
        # 獲取系統狀態
        status = signal_availability_monitor.get_system_status()
        print(f"📊 系統狀態:")
        print(f"   運行狀態: {'運行中' if status['is_running'] else '未運行'}")
        print(f"   信號總數: {status['total_signals']}")
        print(f"   可用信號: {status['available_signals']}")
        print(f"   系統健康率: {status['system_health_rate']:.3f}")
        
        # 模擬信號健康數據
        print(f"\n🔍 模擬信號健康檢查...")
        test_signal = "precision_filter"
        
        # 模擬成功的檢查
        monitor_result = signal_availability_monitor.record_signal_check(
            test_signal, True, 45.5, datetime.now()
        )
        print(f"   {test_signal}: {monitor_result}")
        
        # 獲取信號健康數據
        health_data = signal_availability_monitor.get_signal_health(test_signal)
        if health_data:
            print(f"📈 {test_signal} 健康數據:")
            print(f"   狀態: {health_data.status.value}")
            print(f"   可用率: {health_data.availability_rate:.3f}")
            print(f"   成功率: {health_data.success_rate:.3f}")
            print(f"   平均延遲: {health_data.average_latency_ms:.1f}ms")
            print(f"   品質評分: {health_data.quality_score:.3f}")
        
        print("✅ 信號可用性監控測試成功!")
        return True
        
    except Exception as e:
        print(f"❌ 信號可用性監控測試失敗: {e}")
        return False

async def test_dynamic_weight_engine():
    """測試動態權重引擎"""
    print("\n🎯 測試動態權重引擎")
    print("=" * 60)
    
    try:
        from app.services.dynamic_weight_engine import (
            dynamic_weight_engine, MarketConditions, SignalBlockData, TradingTimeframe
        )
        
        # 創建模擬市場條件
        market_conditions = MarketConditions(
            symbol="BTCUSDT",
            current_price=43500.0,
            volatility_score=0.65,
            trend_strength=0.75,
            volume_strength=0.80,
            liquidity_score=0.90,
            sentiment_score=0.60,
            fear_greed_index=55,
            market_regime="uptrend",
            regime_confidence=0.78,
            timestamp=datetime.now()
        )
        
        # 創建模擬信號可用性數據
        signal_data = {
            "precision_filter": SignalBlockData(
                block_name="precision_filter",
                availability=True,
                quality_score=0.85,
                confidence=0.90,
                latency_ms=25.5,
                last_update=datetime.now(),
                error_count=0,
                success_rate=0.95
            ),
            "technical_analysis": SignalBlockData(
                block_name="technical_analysis", 
                availability=True,
                quality_score=0.78,
                confidence=0.82,
                latency_ms=45.2,
                last_update=datetime.now(),
                error_count=1,
                success_rate=0.88
            )
        }
        
        print("📊 市場條件:")
        print(f"   交易對: {market_conditions.symbol}")
        print(f"   當前價格: ${market_conditions.current_price:,.2f}")
        print(f"   波動率: {market_conditions.volatility_score:.3f}")
        print(f"   趨勢強度: {market_conditions.trend_strength:.3f}")
        print(f"   市場制度: {market_conditions.market_regime}")
        print(f"   制度信心: {market_conditions.regime_confidence:.3f}")
        
        # 計算短線權重
        print(f"\n🎯 計算短線動態權重...")
        weight_result = await dynamic_weight_engine.calculate_dynamic_weights(
            symbol="BTCUSDT",
            timeframe=TradingTimeframe.SHORT_TERM,
            market_conditions=market_conditions,
            signal_availabilities=signal_data
        )
        
        print(f"💡 權重計算結果:")
        weights = weight_result.calculated_weights
        print(f"   精準過濾: {weights.precision_filter_weight:.4f}")
        print(f"   市場條件: {weights.market_condition_weight:.4f}")
        print(f"   技術分析: {weights.technical_analysis_weight:.4f}")
        print(f"   制度分析: {weights.regime_analysis_weight:.4f}")
        print(f"   恐懼貪婪: {weights.fear_greed_weight:.4f}")
        print(f"   趨勢對齊: {weights.trend_alignment_weight:.4f}")
        print(f"   市場深度: {weights.market_depth_weight:.4f}")
        print(f"   資金費率: {weights.funding_rate_weight:.4f}")
        print(f"   聰明資金: {weights.smart_money_weight:.4f}")
        
        print(f"\n📈 綜合評估:")
        print(f"   總體信心: {weight_result.total_confidence:.3f}")
        print(f"   推薦評分: {weight_result.recommendation_score:.3f}")
        print(f"   風險等級: {weight_result.risk_level}")
        
        print("✅ 動態權重引擎測試成功!")
        return True
        
    except Exception as e:
        print(f"❌ 動態權重引擎測試失敗: {e}")
        return False

def test_integration():
    """測試系統整合"""
    print("\n🎯 測試系統整合功能")
    print("=" * 60)
    
    try:
        from app.services.timeframe_weight_templates import timeframe_templates
        from app.services.dynamic_weight_engine import dynamic_weight_engine
        from app.services.signal_availability_monitor import signal_availability_monitor
        
        # 測試模板匯出
        template_summary = timeframe_templates.export_template_summary()
        print(f"📊 模板系統摘要:")
        print(f"   模板數量: {template_summary['template_count']}")
        print(f"   驗證狀態: {template_summary['validation_status']}")
        
        # 測試引擎狀態
        engine_status = dynamic_weight_engine.export_engine_status()
        print(f"\n⚙️ 權重引擎狀態:")
        print(f"   計算次數: {engine_status['total_calculations']}")
        print(f"   緩存條目: {engine_status['cache_entries']}")
        
        # 測試監控系統狀態
        monitor_status = signal_availability_monitor.get_system_status()
        print(f"\n📡 監控系統狀態:")
        print(f"   運行狀態: {'運行中' if monitor_status['is_running'] else '未運行'}")
        print(f"   系統健康率: {monitor_status['system_health_rate']:.3f}")
        
        print("✅ 系統整合測試成功!")
        return True
        
    except Exception as e:
        print(f"❌ 系統整合測試失敗: {e}")
        return False

async def main():
    """主測試函數"""
    print("🚀 多時間框架權重管理系統 - 完整測試")
    print("=" * 80)
    
    results = []
    
    # 1. 測試三週期權重模板
    results.append(test_timeframe_templates())
    
    # 2. 測試信號可用性監控
    results.append(test_signal_monitor())
    
    # 3. 測試動態權重引擎
    results.append(await test_dynamic_weight_engine())
    
    # 4. 測試系統整合
    results.append(test_integration())
    
    # 總結
    print("\n" + "=" * 80)
    print("🎯 測試結果總結:")
    test_names = [
        "三週期權重模板",
        "信號可用性監控", 
        "動態權重引擎",
        "系統整合"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results), 1):
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"   {i}. {name}: {status}")
    
    success_rate = sum(results) / len(results)
    print(f"\n📊 測試通過率: {success_rate:.1%} ({sum(results)}/{len(results)})")
    
    if success_rate == 1.0:
        print("🎉 所有測試通過！多時間框架權重管理系統已就緒!")
    else:
        print("⚠️  部分測試失敗，請檢查相關模組。")

if __name__ == "__main__":
    asyncio.run(main())
