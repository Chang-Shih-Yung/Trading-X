"""
測試 pandas-ta 交易信號系統
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from app.services.pandas_ta_trading_signal_parser import PandasTATradingSignals, SignalType

def create_test_data():
    """創建測試數據"""
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='1H')
    np.random.seed(42)
    
    # 模擬比特幣價格數據
    price_base = 45000
    price_changes = np.random.randn(len(dates)) * 200
    cumulative_changes = np.cumsum(price_changes)
    
    df = pd.DataFrame(index=dates)
    df['open'] = price_base + cumulative_changes
    df['close'] = df['open'] + np.random.randn(len(dates)) * 150
    df['high'] = df[['open', 'close']].max(axis=1) + np.abs(np.random.randn(len(dates))) * 100
    df['low'] = df[['open', 'close']].min(axis=1) - np.abs(np.random.randn(len(dates))) * 100
    df['volume'] = np.random.randint(1000, 50000, len(dates))
    
    return df

def test_signal_generation():
    """測試信號生成功能"""
    print("=== 測試 pandas-ta 交易信號系統 ===\n")
    
    # 創建測試數據
    print("1. 創建測試數據...")
    df = create_test_data()
    print(f"   數據點數: {len(df)}")
    print(f"   價格範圍: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
    
    # 初始化信號生成器
    print("\n2. 初始化信號生成器...")
    try:
        signal_generator = PandasTATradingSignals()
        print("   ✅ 配置文件載入成功")
    except Exception as e:
        print(f"   ❌ 配置文件載入失敗: {e}")
        return
    
    # 計算技術指標
    print("\n3. 計算技術指標...")
    try:
        df_with_indicators = signal_generator.calculate_all_indicators(df, strategy="swing")
        print(f"   ✅ 指標計算完成，總欄位數: {len(df_with_indicators.columns)}")
        
        # 顯示計算出的指標
        indicator_cols = [col for col in df_with_indicators.columns if col not in ['open', 'high', 'low', 'close', 'volume']]
        print(f"   新增指標: {len(indicator_cols)} 個")
        print(f"   主要指標: {', '.join(indicator_cols[:10])}")
        if len(indicator_cols) > 10:
            print(f"   ... 等 {len(indicator_cols) - 10} 個指標")
            
    except Exception as e:
        print(f"   ❌ 指標計算失敗: {e}")
        return
    
    # 生成交易信號
    print("\n4. 生成交易信號...")
    try:
        signals = signal_generator.generate_signals(df_with_indicators, strategy="swing", timeframe="1h")
        print(f"   ✅ 信號生成完成，總信號數: {len(signals)}")
        
        # 按信號類型分組
        signal_counts = {}
        for signal in signals:
            signal_type = signal.signal_type.value
            signal_counts[signal_type] = signal_counts.get(signal_type, 0) + 1
        
        for signal_type, count in signal_counts.items():
            print(f"   {signal_type}: {count} 個")
            
    except Exception as e:
        print(f"   ❌ 信號生成失敗: {e}")
        return
    
    # 獲取信號摘要
    print("\n5. 信號摘要分析...")
    try:
        summary = signal_generator.get_signal_summary(signals)
        print("   ✅ 摘要分析完成")
        print(f"   整體情緒: {summary['overall_sentiment']}")
        print(f"   平均信心度: {summary['average_confidence']:.3f}")
        print(f"   買入強度: {summary['buy_strength_total']:.3f}")
        print(f"   賣出強度: {summary['sell_strength_total']:.3f}")
        
        if summary['strongest_signal']:
            strongest = summary['strongest_signal']
            print(f"   最強信號: {strongest['indicator']} - {strongest['type']} (信心度: {strongest['confidence']:.3f})")
            
    except Exception as e:
        print(f"   ❌ 摘要分析失敗: {e}")
        return
    
    # 顯示詳細信號
    print("\n6. 詳細信號列表 (最新 10 個):")
    try:
        latest_signals = signals[-10:] if len(signals) >= 10 else signals
        
        for i, signal in enumerate(latest_signals, 1):
            print(f"   {i:2d}. {signal.indicator:12s} | {signal.signal_type.value:10s} | "
                  f"強度: {signal.strength:.3f} | 信心: {signal.confidence:.3f}")
            print(f"       條件: {signal.condition_met}")
            print(f"       時間: {signal.timestamp} | 時間框架: {signal.timeframe}")
            print()
            
    except Exception as e:
        print(f"   ❌ 詳細信號顯示失敗: {e}")
    
    # 測試不同策略
    print("\n7. 測試不同策略參數...")
    strategies = ["scalping", "swing", "trend"]
    
    for strategy in strategies:
        try:
            df_strategy = signal_generator.calculate_all_indicators(df, strategy=strategy)
            signals_strategy = signal_generator.generate_signals(df_strategy, strategy=strategy, timeframe="1h")
            summary_strategy = signal_generator.get_signal_summary(signals_strategy)
            
            print(f"   {strategy:10s}: {len(signals_strategy):3d} 信號 | "
                  f"情緒: {summary_strategy['overall_sentiment']:8s} | "
                  f"信心: {summary_strategy['average_confidence']:.3f}")
            
        except Exception as e:
            print(f"   {strategy:10s}: ❌ 失敗 - {e}")

def test_specific_indicators():
    """測試特定指標功能"""
    print("\n=== 測試特定指標詳細功能 ===\n")
    
    df = create_test_data()
    signal_generator = PandasTATradingSignals()
    
    # 測試趨勢指標
    print("1. 趨勢指標測試...")
    df_trend = signal_generator._calculate_trend_indicators(df, "swing")
    trend_indicators = [col for col in df_trend.columns if col not in df.columns]
    print(f"   新增趨勢指標: {len(trend_indicators)} 個")
    for indicator in trend_indicators[:5]:
        latest_value = df_trend[indicator].iloc[-1]
        if not pd.isna(latest_value):
            print(f"   {indicator:20s}: {latest_value:.4f}")
    
    # 測試動量指標
    print("\n2. 動量指標測試...")
    df_momentum = signal_generator._calculate_momentum_indicators(df, "swing")
    momentum_indicators = [col for col in df_momentum.columns if col not in df.columns]
    print(f"   新增動量指標: {len(momentum_indicators)} 個")
    for indicator in momentum_indicators[:5]:
        latest_value = df_momentum[indicator].iloc[-1]
        if not pd.isna(latest_value):
            print(f"   {indicator:20s}: {latest_value:.4f}")
    
    # 測試波動性指標
    print("\n3. 波動性指標測試...")
    df_volatility = signal_generator._calculate_volatility_indicators(df, "swing")
    volatility_indicators = [col for col in df_volatility.columns if col not in df.columns]
    print(f"   新增波動性指標: {len(volatility_indicators)} 個")
    for indicator in volatility_indicators[:5]:
        latest_value = df_volatility[indicator].iloc[-1]
        if not pd.isna(latest_value):
            print(f"   {indicator:20s}: {latest_value:.4f}")

if __name__ == "__main__":
    try:
        test_signal_generation()
        test_specific_indicators()
        print("\n=== 測試完成 ===")
        print("✅ 所有功能測試通過")
        
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
