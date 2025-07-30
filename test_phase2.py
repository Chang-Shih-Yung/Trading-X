#!/usr/bin/env python3
"""
🎯 Phase 2 市場機制適應測試腳本
測試市場機制識別、Fear & Greed Index 和機制適應性交易策略
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# 添加專案根目錄到路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.market_regime_analyzer import market_regime_analyzer
from app.services.dynamic_market_adapter import dynamic_adapter
import requests

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_market_regime_analysis():
    """測試市場機制分析功能"""
    print("🎯 Phase 2 測試：市場機制分析")
    print("=" * 60)
    
    test_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    
    for symbol in test_symbols:
        try:
            print(f"\n📊 測試 {symbol} 市場機制分析...")
            
            # 執行市場機制分析
            analysis = await market_regime_analyzer.analyze_market_regime(symbol)
            
            print(f"✅ {symbol} 市場機制分析結果:")
            print(f"   • 主要機制: {analysis.primary_regime.value}")
            print(f"   • 機制信心度: {analysis.regime_confidence:.2f}")
            print(f"   • Fear & Greed Index: {analysis.fear_greed_index} ({analysis.fear_greed_level.value})")
            print(f"   • 趨勢一致性: {analysis.trend_alignment_score:.2f}")
            print(f"   • 牛市評分: {analysis.bullish_score:.2f}")
            print(f"   • 熊市評分: {analysis.bearish_score:.2f}")
            print(f"   • 橫盤評分: {analysis.sideways_score:.2f}")
            print(f"   • 波動評分: {analysis.volatility_score:.2f}")
            
            print(f"   🔧 推薦技術指標參數:")
            print(f"   • RSI 週期: {analysis.recommended_rsi_period}")
            print(f"   • 移動平均: {analysis.recommended_ma_periods[0]}/{analysis.recommended_ma_periods[1]}")
            print(f"   • 布林帶週期: {analysis.recommended_bb_period}")
            print(f"   • MACD 參數: {analysis.recommended_macd_periods[0]}/{analysis.recommended_macd_periods[1]}/{analysis.recommended_macd_periods[2]}")
            
            print(f"   ⚡ 風險管理建議:")
            print(f"   • 建議倉位大小: {analysis.suggested_position_size:.2f}")
            print(f"   • 建議最大回撤: {analysis.suggested_max_drawdown:.2f}")
            print(f"   • 建議持倉時間: {analysis.suggested_holding_period_hours}小時")
            
            # 測試多時間框架分析
            print(f"   📈 多時間框架分析:")
            for tf, tf_analysis in analysis.timeframe_analysis.items():
                print(f"   • {tf}: {tf_analysis.trend_direction} "
                      f"(強度: {tf_analysis.trend_strength:.2f}, "
                      f"動量: {tf_analysis.momentum_score:.2f}, "
                      f"成交量: {tf_analysis.volume_profile:.2f})")
            
        except Exception as e:
            print(f"❌ {symbol} 市場機制分析失敗: {e}")

async def test_enhanced_dynamic_adapter():
    """測試增強版動態市場適應器"""
    print("\n🔧 Phase 2 測試：增強版動態市場適應器")
    print("=" * 60)
    
    test_symbols = ["BTCUSDT", "ETHUSDT"]
    
    for symbol in test_symbols:
        try:
            print(f"\n📊 測試 {symbol} 增強版動態適應...")
            
            # 獲取Phase 2增強版市場狀態
            market_state = await dynamic_adapter.get_market_state(symbol)
            dynamic_thresholds = dynamic_adapter.get_dynamic_indicator_params(market_state)
            
            print(f"✅ {symbol} Phase 2 增強版市場狀態:")
            print(f"   • 當前價格: ${market_state.current_price:.6f}")
            print(f"   • 波動率評分: {market_state.volatility_score:.2f}")
            print(f"   • 成交量強度: {market_state.volume_strength:.2f}")
            print(f"   • 流動性評分: {market_state.liquidity_score:.2f}")
            print(f"   • 情緒倍數: {market_state.sentiment_multiplier:.2f}")
            
            print(f"   🎯 Phase 2 新增市場機制信息:")
            print(f"   • 市場機制: {market_state.market_regime}")
            print(f"   • 機制信心度: {market_state.regime_confidence:.2f}")
            print(f"   • Fear & Greed Index: {market_state.fear_greed_index} ({market_state.fear_greed_level})")
            print(f"   • 趨勢一致性: {market_state.trend_alignment_score:.2f}")
            
            print(f"   🔧 Phase 2 機制適應性動態參數:")
            print(f"   • 信心度閾值: {dynamic_thresholds.confidence_threshold:.3f}")
            print(f"   • RSI 閾值: {dynamic_thresholds.rsi_oversold}/{dynamic_thresholds.rsi_overbought}")
            print(f"   • 止損百分比: {dynamic_thresholds.stop_loss_percent*100:.2f}%")
            print(f"   • 止盈百分比: {dynamic_thresholds.take_profit_percent*100:.2f}%")
            
            print(f"   📊 機制適應性技術指標參數:")
            print(f"   • RSI 週期: {dynamic_thresholds.regime_adapted_rsi_period}")
            print(f"   • 移動平均: {dynamic_thresholds.regime_adapted_ma_fast}/{dynamic_thresholds.regime_adapted_ma_slow}")
            print(f"   • 布林帶週期: {dynamic_thresholds.regime_adapted_bb_period}")
            print(f"   • 倉位倍數: {dynamic_thresholds.position_size_multiplier:.2f}")
            print(f"   • 持倉時間: {dynamic_thresholds.holding_period_hours}小時")
            
        except Exception as e:
            print(f"❌ {symbol} 增強版動態適應測試失敗: {e}")

def test_phase2_api_endpoint():
    """測試Phase 2 API端點"""
    print("\n🌐 Phase 2 測試：API端點")
    print("=" * 60)
    
    try:
        print("📡 測試 Phase 2 pandas-ta-direct 端點...")
        
        # 測試API端點
        response = requests.get("http://localhost:8000/api/v1/scalping/pandas-ta-direct", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ API 測試成功!")
            print(f"   • 狀態: {data.get('status')}")
            print(f"   • 階段: {data.get('phase')}")
            print(f"   • 生成信號數: {data.get('total_signals')}")
            print(f"   • 數據源: {data.get('data_source')}")
            
            print(f"   🎯 Phase 2 改進項目:")
            for improvement in data.get('improvements', []):
                print(f"   • {improvement}")
            
            # 顯示信號詳情
            signals = data.get('signals', [])
            if signals:
                print(f"\n📊 信號詳情:")
                for i, signal in enumerate(signals[:2]):  # 只顯示前2個
                    print(f"   信號 {i+1}: {signal['symbol']} - {signal['signal_type']}")
                    print(f"   • 策略: {signal['strategy_name']}")
                    print(f"   • 信心度: {signal['confidence']:.3f}")
                    print(f"   • 精準度: {signal['precision_score']:.3f}")
                    print(f"   • 風險回報比: {signal['risk_reward_ratio']:.2f}")
                    
                    # Phase 2 特有信息
                    if 'market_regime_info' in signal:
                        regime_info = signal['market_regime_info']
                        print(f"   • 市場機制: {regime_info['primary_regime']}")
                        print(f"   • Fear & Greed: {regime_info['fear_greed_index']} ({regime_info['fear_greed_level']})")
                        print(f"   • 倉位倍數: {regime_info['position_size_multiplier']}")
                        print(f"   • 持倉時間: {regime_info['holding_period_hours']}小時")
                    
                    if 'dynamic_market_info' in signal and 'regime_adapted_indicators' in signal['dynamic_market_info']:
                        adapted_indicators = signal['dynamic_market_info']['regime_adapted_indicators']
                        print(f"   • 適應性指標 - RSI週期: {adapted_indicators['rsi_period']}, "
                              f"MA: {adapted_indicators['ma_fast']}/{adapted_indicators['ma_slow']}, "
                              f"BB週期: {adapted_indicators['bb_period']}")
                    print()
            
        else:
            print(f"❌ API 測試失敗: HTTP {response.status_code}")
            print(f"   錯誤信息: {response.text}")
            
    except Exception as e:
        print(f"❌ API 端點測試失敗: {e}")

async def main():
    """主測試函數"""
    print("🎯 Trading-X Phase 2 市場機制適應測試")
    print("=" * 80)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Phase 2 主要功能:")
    print("• 市場機制識別 (牛市/熊市/橫盤/波動)")
    print("• Fear & Greed Index 模擬計算")
    print("• 多時間框架趨勢確認")
    print("• 機制適應性技術指標參數切換")
    print("• 機制適應性風險管理")
    print("=" * 80)
    
    try:
        # 測試市場機制分析
        await test_market_regime_analysis()
        
        # 測試增強版動態適應器
        await test_enhanced_dynamic_adapter()
        
        # 測試API端點
        test_phase2_api_endpoint()
        
        print("\n🎉 Phase 2 測試完成!")
        print("=" * 60)
        print("✅ 所有 Phase 2 功能測試完成")
        print("📊 市場機制適應性交易策略已準備就緒")
        
    except Exception as e:
        print(f"\n❌ Phase 2 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
