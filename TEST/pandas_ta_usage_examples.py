"""
pandas-ta 交易信號系統使用範例
展示如何在實際交易策略中使用技術指標信號
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from app.services.pandas_ta_trading_signal_parser import PandasTATradingSignals, SignalType

def create_realistic_crypto_data():
    """創建更真實的加密貨幣價格數據"""
    # 創建過去30天的小時數據
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    dates = pd.date_range(start=start_date, end=end_date, freq='1H')
    
    # 模擬比特幣價格走勢
    np.random.seed(123)
    price_base = 45000
    
    # 創建趨勢成分 + 隨機波動
    trend = np.linspace(0, 2000, len(dates))  # 上升趨勢
    noise = np.random.randn(len(dates)).cumsum() * 300
    volatility_spikes = np.random.choice([0, 1], len(dates), p=[0.95, 0.05]) * np.random.randn(len(dates)) * 1000
    
    price_series = price_base + trend + noise + volatility_spikes
    
    df = pd.DataFrame(index=dates)
    df['close'] = price_series
    
    # 生成 OHLC 數據
    df['open'] = df['close'].shift(1).fillna(df['close'].iloc[0])
    
    # 計算每小時的波動範圍
    hourly_volatility = np.random.gamma(2, 50, len(dates))  # Gamma 分佈產生正偏波動
    
    df['high'] = df[['open', 'close']].max(axis=1) + hourly_volatility * np.random.random(len(dates))
    df['low'] = df[['open', 'close']].min(axis=1) - hourly_volatility * np.random.random(len(dates))
    
    # 確保 OHLC 邏輯正確
    df['high'] = df[['open', 'high', 'low', 'close']].max(axis=1)
    df['low'] = df[['open', 'high', 'low', 'close']].min(axis=1)
    
    # 生成成交量 (與價格變動相關)
    price_change = df['close'].pct_change().abs().fillna(0)
    base_volume = 20000
    volume_multiplier = 1 + price_change * 10  # 價格變動大時成交量增加
    
    # 確保沒有 NaN 或 inf 值
    volume_multiplier = volume_multiplier.fillna(1).replace([np.inf, -np.inf], 1)
    volume_raw = base_volume * volume_multiplier * (0.5 + np.random.random(len(dates)))
    volume_raw = volume_raw.fillna(base_volume).replace([np.inf, -np.inf], base_volume)
    
    df['volume'] = volume_raw.astype(int)
    
    # 移除缺失值並確保數據完整性
    df = df.dropna()
    
    # 最終檢查確保所有值都是有限的
    for col in df.columns:
        df[col] = df[col].replace([np.inf, -np.inf], df[col].median())
        df[col] = df[col].fillna(df[col].median())
    
    return df

def example_scalping_strategy():
    """剝頭皮交易策略範例"""
    print("=== 剝頭皮交易策略範例 ===\n")
    
    # 創建數據
    df = create_realistic_crypto_data()
    print(f"數據範圍: {df.index[0]} 到 {df.index[-1]}")
    print(f"價格範圍: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
    print(f"總數據點: {len(df)}")
    
    # 初始化信號生成器
    signal_generator = PandasTATradingSignals()
    
    # 計算指標 (專為剝頭皮優化)
    df_with_indicators = signal_generator.calculate_all_indicators(df, strategy="scalping")
    
    # 生成信號
    signals = signal_generator.generate_signals(df_with_indicators, strategy="scalping", timeframe="1h")
    
    # 信號摘要
    summary = signal_generator.get_signal_summary(signals)
    
    print(f"\n信號統計:")
    print(f"  總信號數: {summary['total_signals']}")
    print(f"  買入信號: {summary['buy_signals']}")
    print(f"  賣出信號: {summary['sell_signals']}")
    print(f"  整體情緒: {summary['overall_sentiment']}")
    print(f"  平均信心度: {summary['average_confidence']:.3f}")
    
    # 找出高信心度的信號
    high_confidence_signals = [s for s in signals if s.confidence > 0.7]
    print(f"\n高信心度信號 (>0.7): {len(high_confidence_signals)} 個")
    
    for signal in high_confidence_signals[:5]:  # 顯示前 5 個
        print(f"  {signal.indicator:12s} | {signal.signal_type.value:4s} | "
              f"信心: {signal.confidence:.3f} | 強度: {signal.strength:.3f}")
        print(f"    條件: {signal.condition_met}")
    
    return df_with_indicators, signals, summary

def example_swing_strategy():
    """波段交易策略範例"""
    print("\n=== 波段交易策略範例 ===\n")
    
    # 創建數據
    df = create_realistic_crypto_data()
    
    # 初始化信號生成器
    signal_generator = PandasTATradingSignals()
    
    # 計算指標 (專為波段交易優化)
    df_with_indicators = signal_generator.calculate_all_indicators(df, strategy="swing")
    
    # 生成信號
    signals = signal_generator.generate_signals(df_with_indicators, strategy="swing", timeframe="4h")
    
    # 信號摘要
    summary = signal_generator.get_signal_summary(signals)
    
    print(f"信號統計:")
    print(f"  總信號數: {summary['total_signals']}")
    print(f"  買入信號: {summary['buy_signals']}")
    print(f"  賣出信號: {summary['sell_signals']}")
    print(f"  整體情緒: {summary['overall_sentiment']}")
    print(f"  買入強度總和: {summary['buy_strength_total']:.3f}")
    print(f"  賣出強度總和: {summary['sell_strength_total']:.3f}")
    
    # 按指標類型分析信號
    trend_signals = [s for s in signals if s.indicator in ['macd', 'adx', 'supertrend', 'aroon']]
    momentum_signals = [s for s in signals if s.indicator in ['rsi', 'stoch', 'willr', 'cci']]
    volatility_signals = [s for s in signals if s.indicator in ['bbands', 'atr', 'donchian']]
    
    print(f"\n按類型分類:")
    print(f"  趨勢信號: {len(trend_signals)} 個")
    print(f"  動量信號: {len(momentum_signals)} 個")
    print(f"  波動性信號: {len(volatility_signals)} 個")
    
    return df_with_indicators, signals, summary

def analyze_signal_consensus():
    """分析信號一致性"""
    print("\n=== 信號一致性分析 ===\n")
    
    # 創建數據
    df = create_realistic_crypto_data()
    signal_generator = PandasTATradingSignals()
    
    # 計算不同策略的信號
    strategies = ["scalping", "swing", "trend"]
    all_results = {}
    
    for strategy in strategies:
        df_indicators = signal_generator.calculate_all_indicators(df, strategy=strategy)
        signals = signal_generator.generate_signals(df_indicators, strategy=strategy, timeframe="1h")
        summary = signal_generator.get_signal_summary(signals)
        
        all_results[strategy] = {
            'signals': signals,
            'summary': summary
        }
        
        print(f"{strategy.upper()} 策略:")
        print(f"  信號數: {summary['total_signals']}")
        print(f"  情緒: {summary['overall_sentiment']}")
        print(f"  信心度: {summary['average_confidence']:.3f}")
    
    # 分析一致性
    print(f"\n策略一致性分析:")
    sentiments = [all_results[s]['summary']['overall_sentiment'] for s in strategies]
    
    if len(set(sentiments)) == 1:
        print(f"  ✅ 所有策略一致: {sentiments[0]}")
    else:
        print(f"  ⚠️  策略不一致: {', '.join(sentiments)}")
    
    # 找出共同的強信號
    common_indicators = set()
    for strategy in strategies:
        indicators = {s.indicator for s in all_results[strategy]['signals'] if s.confidence > 0.7}
        if not common_indicators:
            common_indicators = indicators
        else:
            common_indicators = common_indicators.intersection(indicators)
    
    print(f"  共同高信心指標: {', '.join(common_indicators) if common_indicators else '無'}")
    
    return all_results

def backtest_signal_performance():
    """回測信號性能"""
    print("\n=== 信號回測分析 ===\n")
    
    # 創建更長期的數據用於回測
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='4H')
    np.random.seed(456)
    
    # 創建有明確趨勢的測試數據
    price_base = 45000
    trend_changes = np.random.choice([-1, 0, 1], len(dates)//10, p=[0.3, 0.4, 0.3])
    trend_repeated = np.repeat(trend_changes, 10)
    
    # 確保陣列長度一致
    if len(trend_repeated) > len(dates):
        trend_repeated = trend_repeated[:len(dates)]
    elif len(trend_repeated) < len(dates):
        # 補齊到所需長度
        padding = np.tile(trend_repeated, (len(dates) // len(trend_repeated)) + 1)
        trend_repeated = padding[:len(dates)]
    
    price_changes = trend_repeated * 100 + np.random.randn(len(dates)) * 200
    price_series = price_base + np.cumsum(price_changes)
    
    df = pd.DataFrame(index=dates)
    df['close'] = price_series
    df['open'] = df['close'].shift(1).fillna(df['close'].iloc[0])
    df['high'] = df[['open', 'close']].max(axis=1) + np.abs(np.random.randn(len(dates))) * 100
    df['low'] = df[['open', 'close']].min(axis=1) - np.abs(np.random.randn(len(dates))) * 100
    df['volume'] = np.random.randint(10000, 100000, len(dates))
    
    # 初始化信號生成器
    signal_generator = PandasTATradingSignals()
    
    # 回測不同時間點的信號準確性
    correct_predictions = 0
    total_predictions = 0
    signal_history = []
    
    # 滑動窗口回測
    window_size = 50  # 使用 50 個數據點計算指標
    prediction_horizon = 5  # 預測未來 5 個時間點
    
    for i in range(window_size, len(df) - prediction_horizon, 5):
        # 獲取窗口數據
        window_df = df.iloc[i-window_size:i].copy()
        
        # 計算指標和信號
        df_indicators = signal_generator.calculate_all_indicators(window_df, strategy="swing")
        signals = signal_generator.generate_signals(df_indicators, strategy="swing", timeframe="4h")
        
        if not signals:
            continue
            
        # 獲取最強信號
        summary = signal_generator.get_signal_summary(signals)
        
        # 預測方向
        current_price = df.iloc[i]['close']
        future_price = df.iloc[i + prediction_horizon]['close']
        actual_direction = "BUY" if future_price > current_price else "SELL"
        
        predicted_direction = summary['overall_sentiment']
        if predicted_direction == "BULLISH":
            predicted_direction = "BUY"
        elif predicted_direction == "BEARISH":
            predicted_direction = "SELL"
        else:
            continue  # 跳過中性信號
        
        # 記錄預測結果
        is_correct = predicted_direction == actual_direction
        if is_correct:
            correct_predictions += 1
        total_predictions += 1
        
        signal_history.append({
            'timestamp': df.index[i],
            'current_price': current_price,
            'future_price': future_price,
            'predicted': predicted_direction,
            'actual': actual_direction,
            'correct': is_correct,
            'confidence': summary['average_confidence'],
            'signal_count': summary['total_signals']
        })
    
    # 計算準確率
    accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
    
    print(f"回測結果:")
    print(f"  預測總數: {total_predictions}")
    print(f"  正確預測: {correct_predictions}")
    print(f"  準確率: {accuracy:.3f} ({accuracy*100:.1f}%)")
    
    # 分析高信心度信號的表現
    high_conf_signals = [s for s in signal_history if s['confidence'] > 0.7]
    if high_conf_signals:
        high_conf_accuracy = sum(s['correct'] for s in high_conf_signals) / len(high_conf_signals)
        print(f"  高信心度信號準確率: {high_conf_accuracy:.3f} ({high_conf_accuracy*100:.1f}%)")
    
    return signal_history

def export_signal_config():
    """匯出完整的信號配置文件"""
    print("\n=== 匯出信號配置 ===\n")
    
    signal_generator = PandasTATradingSignals()
    
    # 創建完整的配置摘要
    config_summary = {
        "system_info": {
            "name": "pandas-ta 交易信號系統",
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "supported_strategies": ["scalping", "swing", "trend"],
            "supported_timeframes": ["5m", "15m", "1h", "4h", "1d"]
        },
        "indicators_count": {
            "trend_indicators": len(signal_generator.config["trend_indicators"]),
            "momentum_indicators": len(signal_generator.config["momentum_indicators"]),
            "volatility_indicators": len(signal_generator.config["volatility_indicators"]),
            "volume_indicators": len(signal_generator.config["volume_indicators"]),
            "candlestick_patterns": len(signal_generator.config["candlestick_patterns"])
        },
        "signal_types": {
            "BUY": "買入信號 - 價格預期上漲",
            "SELL": "賣出信號 - 價格預期下跌", 
            "NEUTRAL": "中性信號 - 無明確方向",
            "STRONG_BUY": "強烈買入 - 多重指標確認上漲",
            "STRONG_SELL": "強烈賣出 - 多重指標確認下跌"
        },
        "confidence_levels": {
            "0.9+": "極高信心 - 建議重倉操作",
            "0.7-0.9": "高信心 - 建議正常倉位",
            "0.5-0.7": "中等信心 - 建議輕倉試探",
            "0.3-0.5": "低信心 - 建議觀望",
            "0.0-0.3": "極低信心 - 不建議操作"
        }
    }
    
    # 保存配置摘要
    with open('/Users/henrychang/Desktop/Trading-X/app/config/pandas_ta_signal_summary.json', 'w', encoding='utf-8') as f:
        json.dump(config_summary, f, ensure_ascii=False, indent=2)
    
    print("✅ 配置摘要已匯出到 app/config/pandas_ta_signal_summary.json")
    
    return config_summary

if __name__ == "__main__":
    print("🚀 pandas-ta 交易信號系統完整示範\n")
    
    try:
        # 1. 剝頭皮策略示範
        scalping_df, scalping_signals, scalping_summary = example_scalping_strategy()
        
        # 2. 波段交易策略示範 
        swing_df, swing_signals, swing_summary = example_swing_strategy()
        
        # 3. 信號一致性分析
        consensus_results = analyze_signal_consensus()
        
        # 4. 回測分析
        backtest_history = backtest_signal_performance()
        
        # 5. 匯出配置
        config_summary = export_signal_config()
        
        print("\n" + "="*50)
        print("🎉 完整示範已完成！")
        print("="*50)
        
        print(f"\n📊 核心統計:")
        print(f"  支援指標數量: {sum(config_summary['indicators_count'].values())}")
        print(f"  剝頭皮信號數: {scalping_summary['total_signals']}")
        print(f"  波段交易信號數: {swing_summary['total_signals']}")
        print(f"  回測準確率: {len([h for h in backtest_history if h['correct']]) / len(backtest_history) * 100:.1f}%")
        
        print(f"\n💡 建議:")
        print(f"  1. 使用多策略確認提高信號準確性")
        print(f"  2. 重點關注信心度 > 0.7 的信號")
        print(f"  3. 結合止損止盈進行風險管理")
        print(f"  4. 定期回測驗證策略有效性")
        
    except Exception as e:
        print(f"❌ 示範過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
