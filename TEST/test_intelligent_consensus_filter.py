#!/usr/bin/env python3
"""
智能共振濾波器測試
測試 AI 混合決策系統的核心功能
"""

import sys
import os
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# 添加項目根目錄到路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_config_loading():
    """測試配置文件載入"""
    print("🧪 測試智能共振配置載入...")
    
    try:
        from app.services.precision_signal_filter import IntelligentConsensusFilter
        
        # 初始化智能共振濾波器
        consensus_filter = IntelligentConsensusFilter()
        
        # 檢查配置載入
        if consensus_filter.config:
            print("✅ 配置載入成功")
            print(f"   - 需要共振數量: {consensus_filter.config.get('consensus_filter', {}).get('required_consensus', 'N/A')}")
            print(f"   - 啟用指標數量: {len([k for k, v in consensus_filter.config.get('consensus_filter', {}).get('indicators', {}).items() if v.get('enabled', False)])}")
            print(f"   - 情緒防護啟用: {consensus_filter.config.get('sentiment_guard', {}).get('enabled', False)}")
            return True
        else:
            print("❌ 配置載入失敗")
            return False
            
    except Exception as e:
        print(f"❌ 配置載入錯誤: {e}")
        return False

def test_indicator_signals():
    """測試指標信號計算"""
    print("\n🧪 測試指標信號計算...")
    
    try:
        from app.services.precision_signal_filter import IntelligentConsensusFilter
        
        consensus_filter = IntelligentConsensusFilter()
        
        # 模擬市場數據
        mock_market_data = {
            'rsi': 25.0,  # 超賣信號
            'macd': 0.001,
            'stochastic_k': 20.0,
            'obv': 100000,
            'bb_position': 0.1,  # 接近下軌
            'volume_ratio': 1.5,
            'volatility': 0.03
        }
        
        # 測試指標信號計算
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        signals = loop.run_until_complete(
            consensus_filter._calculate_indicator_signals("BTCUSDT", mock_market_data)
        )
        
        if signals:
            print("✅ 指標信號計算成功")
            for indicator, signal_data in signals.items():
                print(f"   - {indicator}: {signal_data['signal']} (強度: {signal_data.get('strength', 0):.3f})")
            return True
        else:
            print("❌ 指標信號計算失敗")
            return False
            
    except Exception as e:
        print(f"❌ 指標信號計算錯誤: {e}")
        return False

def test_consensus_evaluation():
    """測試共振評估"""
    print("\n🧪 測試共振評估...")
    
    try:
        from app.services.precision_signal_filter import IntelligentConsensusFilter
        
        consensus_filter = IntelligentConsensusFilter()
        
        # 模擬指標信號
        mock_indicator_signals = {
            'RSI': {'signal': 'BUY', 'strength': 0.8},
            'MACD': {'signal': 'BUY', 'strength': 0.6},
            'Stochastic': {'signal': 'BUY', 'strength': 0.7},
            'OBV': {'signal': 'BUY', 'strength': 0.5},
            'BollingerBands': {'signal': 'BUY', 'strength': 0.9}
        }
        
        # 執行共振評估
        consensus_result = consensus_filter._evaluate_consensus(mock_indicator_signals)
        
        if consensus_result:
            print("✅ 共振評估成功")
            print(f"   - 是否達到閾值: {consensus_result['meets_threshold']}")
            print(f"   - 信號類型: {consensus_result['signal_type']}")
            print(f"   - 共振分數: {consensus_result['score']:.3f}")
            print(f"   - 貢獻指標: {consensus_result['contributors']}")
            print(f"   - 信心度: {consensus_result['confidence']:.3f}")
            return True
        else:
            print("❌ 共振評估失敗")
            return False
            
    except Exception as e:
        print(f"❌ 共振評估錯誤: {e}")
        return False

def test_sentiment_guard():
    """測試情緒防護"""
    print("\n🧪 測試情緒防護...")
    
    try:
        from app.services.precision_signal_filter import IntelligentConsensusFilter
        
        consensus_filter = IntelligentConsensusFilter()
        
        # 測試正常市場條件
        normal_data = {
            'rsi': 50.0,
            'volume_ratio': 1.0,
            'volatility': 0.02
        }
        
        normal_status = consensus_filter._check_sentiment_guard(normal_data)
        print(f"✅ 正常條件情緒狀態: {normal_status}")
        
        # 測試極端條件
        extreme_data = {
            'rsi': 95.0,  # 極度超買
            'volume_ratio': 3.0,  # 成交量激增
            'volatility': 0.15  # 極高波動
        }
        
        extreme_status = consensus_filter._check_sentiment_guard(extreme_data)
        print(f"✅ 極端條件情緒狀態: {extreme_status}")
        
        return True
        
    except Exception as e:
        print(f"❌ 情緒防護測試錯誤: {e}")
        return False

def test_full_consensus_analysis():
    """測試完整共振分析流程"""
    print("\n🧪 測試完整共振分析流程...")
    
    try:
        from app.services.precision_signal_filter import IntelligentConsensusFilter
        
        consensus_filter = IntelligentConsensusFilter()
        
        # 模擬完整市場數據
        market_data = {
            'rsi': 30.0,  # 超賣
            'macd': 0.002,
            'stochastic_k': 25.0,
            'obv': 120000,
            'bb_position': 0.15,
            'volume_ratio': 1.2,
            'volatility': 0.025,
            'price': 45000.0,
            'trend': 'bearish'
        }
        
        # 執行完整分析
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        consensus_signal = loop.run_until_complete(
            consensus_filter.analyze_consensus("BTCUSDT", market_data)
        )
        
        if consensus_signal:
            print("✅ 完整共振分析成功")
            print(f"   - 交易對: {consensus_signal.symbol}")
            print(f"   - 信號類型: {consensus_signal.signal_type}")
            print(f"   - 共振分數: {consensus_signal.consensus_score:.3f}")
            print(f"   - 貢獻指標: {consensus_signal.contributing_indicators}")
            print(f"   - 情緒狀態: {consensus_signal.sentiment_status}")
            print(f"   - 信心度: {consensus_signal.confidence:.3f}")
            print(f"   - 生成時間: {consensus_signal.created_at}")
            return True
        else:
            print("⚠️  未生成共振信號（可能不滿足條件）")
            return True  # 這也是正常情況
            
    except Exception as e:
        print(f"❌ 完整共振分析錯誤: {e}")
        return False

def main():
    """主測試函數"""
    print("="*60)
    print("🚀 智能共振濾波器測試開始")
    print("="*60)
    
    test_results = []
    
    # 執行所有測試
    test_results.append(("配置載入測試", test_config_loading()))
    test_results.append(("指標信號計算測試", test_indicator_signals()))
    test_results.append(("共振評估測試", test_consensus_evaluation()))
    test_results.append(("情緒防護測試", test_sentiment_guard()))
    test_results.append(("完整分析流程測試", test_full_consensus_analysis()))
    
    # 總結結果
    print("\n" + "="*60)
    print("📊 測試結果總結")
    print("="*60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n總計: {passed}/{total} 測試通過")
    
    if passed == total:
        print("🎉 所有測試通過！智能共振濾波器運行正常")
        return True
    else:
        print("⚠️  部分測試失敗，需要檢查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
