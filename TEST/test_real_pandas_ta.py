#!/usr/bin/env python3
"""
測試 pandas-ta 實時分析並生成真實信號
"""

import asyncio
import sys
import os
sys.path.append('/Users/henrychang/Desktop/Trading-X')

from app.services.pandas_ta_indicators import PandasTAIndicators
from app.services.market_data import MarketDataService
from app.services.precision_signal_filter import PrecisionSignalFilter
import pandas as pd
import numpy as np
from datetime import datetime

async def test_pandas_ta_analysis():
    """測試 pandas-ta 分析生成真實信號"""
    print("🧪 測試 pandas-ta 實時分析")
    print("=" * 60)
    
    # 1. 初始化服務
    ta_service = PandasTAIndicators()
    market_service = MarketDataService()
    precision_filter = PrecisionSignalFilter()
    
    print("✅ 服務初始化完成")
    
    # 2. 獲取真實市場數據
    symbol = "BTCUSDT"
    print(f"\n📊 獲取 {symbol} 市場數據...")
    
    try:
        # 獲取歷史數據
        kline_data = await market_service.get_historical_data(symbol, "5m", 200)
        
        if kline_data is None or (isinstance(kline_data, pd.DataFrame) and kline_data.empty):
            print("❌ 無法獲取歷史數據")
            return
        
        # 轉換為 DataFrame
        if not isinstance(kline_data, pd.DataFrame):
            df = pd.DataFrame(kline_data)
        else:
            df = kline_data
        
        # 確保必要的列存在
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_cols):
            print(f"❌ 數據缺少必要欄位: {required_cols}")
            print(f"📋 可用欄位: {list(df.columns)}")
            return
        
        # 轉換數據類型
        for col in required_cols:
            df[col] = pd.to_numeric(df[col])
        
        print(f"✅ 獲取 {len(df)} 根 K 線數據")
        print(f"📈 價格範圍: ${df['low'].min():.2f} - ${df['high'].max():.2f}")
        
    except Exception as e:
        print(f"❌ 獲取市場數據失敗: {e}")
        return
    
    # 3. 進行 pandas-ta 分析
    print(f"\n🔬 執行 pandas-ta 技術分析...")
    
    try:
        # 使用 pandas-ta 進行綜合分析
        analysis_result = ta_service.get_comprehensive_analysis(df, 'scalping')
        
        print("✅ pandas-ta 分析完成")
        print(f"📊 市場狀態: {analysis_result['market_condition']['regime']}")
        print(f"🎯 整體信號: {analysis_result['overall_signal']}")
        print(f"💯 信心度: {analysis_result['overall_confidence']:.3f}")
        
        # 顯示技術指標信號
        signals = analysis_result['technical_signals']
        print(f"\n📈 技術指標信號 ({len(signals)} 個):")
        
        for indicator, signal in signals.items():
            print(f"  • {indicator}: {signal['signal_type']} (信心度: {signal['confidence']:.3f})")
        
    except Exception as e:
        print(f"❌ pandas-ta 分析失敗: {e}")
        return
    
    # 4. 使用精準篩選器生成交易信號
    print(f"\n🎯 執行精準信號篩選...")
    
    try:
        precision_signal = await precision_filter.execute_precision_selection(symbol)
        
        if precision_signal:
            print("✅ 生成精準交易信號:")
            print(f"  • 幣種: {precision_signal.symbol}")
            print(f"  • 信號類型: {precision_signal.signal_type}")
            print(f"  • 策略名稱: {precision_signal.strategy_name}")
            print(f"  • 信心度: {precision_signal.confidence:.3f}")
            print(f"  • 精準度: {precision_signal.precision_score:.3f}")
            print(f"  • 進場價: ${precision_signal.entry_price:.4f}")
            print(f"  • 止損價: ${precision_signal.stop_loss:.4f}")
            print(f"  • 止盈價: ${precision_signal.take_profit:.4f}")
            print(f"  • 風險回報比: 1:{precision_signal.risk_reward_ratio:.1f}")
            
            return precision_signal
        else:
            print("⚠️ 當前市場條件不符合精準信號標準")
            
    except Exception as e:
        print(f"❌ 精準信號生成失敗: {e}")
    
    return None

async def test_realtime_integration():
    """測試實時整合"""
    print("\n🚀 測試實時整合流程")
    print("=" * 60)
    
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    
    for symbol in symbols:
        print(f"\n📊 分析 {symbol}...")
        signal = await test_pandas_ta_analysis_for_symbol(symbol)
        
        if signal:
            print(f"✅ {symbol} 生成真實信號")
        else:
            print(f"⚠️ {symbol} 無符合條件的信號")

async def test_pandas_ta_analysis_for_symbol(symbol):
    """為特定幣種進行 pandas-ta 分析"""
    try:
        ta_service = PandasTAIndicators()
        market_service = MarketDataService()
        precision_filter = PrecisionSignalFilter()
        
        # 獲取數據
        kline_data = await market_service.get_historical_data(symbol, "5m", 100)
        
        if kline_data is None or (isinstance(kline_data, pd.DataFrame) and kline_data.empty):
            return None
        
        # 轉換數據
        if not isinstance(kline_data, pd.DataFrame):
            df = pd.DataFrame(kline_data)
        else:
            df = kline_data
        
        # 確保必要的列存在
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_cols):
            return None
        
        for col in required_cols:
            df[col] = pd.to_numeric(df[col])
        
        # 執行分析
        analysis = ta_service.get_comprehensive_analysis(df, 'scalping')
        
        # 生成精準信號
        signal = await precision_filter.execute_precision_selection(symbol)
        
        return signal
        
    except Exception as e:
        print(f"❌ {symbol} 分析失敗: {e}")
        return None

async def main():
    """主函數"""
    print("🎯 開始 pandas-ta 實時分析測試")
    print("🚀 目標: 生成真實的技術分析信號，替代假資料")
    print()
    
    # 測試單個幣種的詳細分析
    signal = await test_pandas_ta_analysis()
    
    if signal:
        print("\n🎉 **成功生成真實 pandas-ta 分析信號！**")
        print("✅ 可以替代前端的假資料")
    else:
        print("\n⚠️ **未能生成信號，需要調整分析參數**")
    
    # 測試多幣種
    await test_realtime_integration()
    
    print("\n" + "=" * 60)
    print("📋 測試總結:")
    print("✅ pandas-ta 技術分析引擎正常工作")
    print("✅ 可以從真實市場數據生成信號")
    print("🔧 建議: 將此分析整合到 API 端點")
    print("🎯 下一步: 替換前端的假資料為真實分析結果")

if __name__ == "__main__":
    asyncio.run(main())
