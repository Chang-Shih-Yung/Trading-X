#!/usr/bin/env python3
"""
修正版本：解決數據格式問題的 pandas-ta 測試
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 添加項目路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def generate_proper_crypto_data(periods=200):
    """生成格式正確的加密貨幣數據"""
    np.random.seed(42)
    
    # 創建正確的時間索引
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=periods)
    timestamps = pd.date_range(start=start_time, end=end_time, periods=periods)
    
    base_price = 50000.0
    prices = []
    volumes = []
    
    for i in range(periods):
        if i == 0:
            price = base_price
        else:
            # 添加一些趨勢和波動
            trend = 0.0001 * np.sin(i / 50)  # 長期趨勢
            noise = np.random.normal(0, 0.02)  # 隨機波動
            price = prices[-1] * (1 + trend + noise)
            price = max(price, 10000)  # 避免負價格
        
        prices.append(price)
        
        # 成交量與價格變動相關
        if i == 0:
            volume = 1000000000
        else:
            price_change = abs((price - prices[-2]) / prices[-2])
            volume_multiplier = 1 + price_change * 10
            volume = 800000000 * volume_multiplier * np.random.normal(1, 0.2)
            volume = max(volume, 100000000)
        
        volumes.append(volume)
    
    # 生成 OHLC 數據
    data = []
    for i in range(periods):
        close_price = prices[i]
        volatility = np.random.normal(0, 0.005)
        
        high = close_price * (1 + abs(volatility) + 0.001)
        low = close_price * (1 - abs(volatility) - 0.001)
        open_price = close_price * (1 + volatility * 0.5)
        
        data.append({
            'open': open_price,
            'high': high,
            'low': low,
            'close': close_price,
            'volume': volumes[i]
        })
    
    # 創建 DataFrame 並設置正確的索引
    df = pd.DataFrame(data, index=timestamps)
    
    # 確保數據類型正確
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 確保數據按時間排序
    df = df.sort_index()
    
    return df

def test_fixed_signal_generation():
    """測試修正後的信號生成"""
    print("=" * 80)
    print("🔧 修正版本信號生成測試")
    print("=" * 80)
    
    # 生成正確格式的數據
    print("📊 生成格式正確的市場數據...")
    df = generate_proper_crypto_data(200)
    print(f"✅ 生成了 {len(df)} 筆數據")
    print(f"📅 時間範圍: {df.index[0]} 到 {df.index[-1]}")
    print(f"📈 價格範圍: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
    print(f"📊 數據格式檢查:")
    print(f"  • 索引類型: {type(df.index)}")
    print(f"  • 是否已排序: {df.index.is_monotonic_increasing}")
    print(f"  • 空值檢查: {df.isnull().sum().sum()}")
    
    try:
        # 導入信號生成器
        from app.services.pandas_ta_trading_signal_parser import PandasTATradingSignals
        
        print("\n🔧 初始化信號解析器...")
        parser = PandasTATradingSignals()
        
        # 測試指標計算
        print("\n📊 測試指標計算...")
        df_with_indicators = parser.calculate_all_indicators(df, "swing")
        print(f"✅ 指標計算成功！數據維度: {df_with_indicators.shape}")
        
        # 檢查主要指標
        indicator_columns = [col for col in df_with_indicators.columns if col not in ['open', 'high', 'low', 'close', 'volume']]
        print(f"📈 計算出的指標數量: {len(indicator_columns)}")
        print("主要指標:")
        for col in indicator_columns[:10]:  # 顯示前10個指標
            non_null_count = df_with_indicators[col].count()
            if non_null_count > 0:
                min_val = df_with_indicators[col].min()
                max_val = df_with_indicators[col].max()
                print(f"  ✅ {col}: {non_null_count} 個值，範圍 [{min_val:.3f}, {max_val:.3f}]")
        
        # 測試信號生成
        print("\n🎯 測試信號生成...")
        signals = parser.generate_signals(df_with_indicators, strategy="swing")
        
        if signals and len(signals) > 0:
            print(f"🎉 成功生成 {len(signals)} 個信號！")
            
            # 分析信號
            buy_count = sum(1 for s in signals if hasattr(s, 'signal_type') and 'BUY' in str(s.signal_type))
            sell_count = sum(1 for s in signals if hasattr(s, 'signal_type') and 'SELL' in str(s.signal_type))
            
            print(f"  • 買入信號: {buy_count}")
            print(f"  • 賣出信號: {sell_count}")
            print(f"  • 信號密度: {len(signals)/len(df)*100:.1f}%")
            
            # 顯示最近的信號
            print("\n📋 最近信號詳情:")
            for i, signal in enumerate(signals[-5:]):
                timestamp = signal.timestamp if hasattr(signal, 'timestamp') else 'N/A'
                print(f"  {i+1}. [{timestamp}] {signal.indicator}: {signal.signal_type}")
                print(f"     強度: {signal.strength:.3f}, 信心度: {signal.confidence:.3f}")
            
            # 測試優化過濾 (簡化版本)
            print("\n🎯 測試優化過濾...")
            high_quality_signals = [s for s in signals if s.confidence > 0.7 and s.strength > 0.6]
            print(f"  • 高質量信號 (信心度>0.7, 強度>0.6): {len(high_quality_signals)}")
            print(f"  • 過濾率: {(1-len(high_quality_signals)/len(signals))*100:.1f}%")
            
            if high_quality_signals:
                hq_buy = sum(1 for s in high_quality_signals if 'BUY' in str(s.signal_type))
                hq_sell = sum(1 for s in high_quality_signals if 'SELL' in str(s.signal_type))
                print(f"  • 優化後 - 買入: {hq_buy}, 賣出: {hq_sell}")
        
        else:
            print("❌ 仍然沒有生成信號")
            
            # 進一步調試
            print("\n🔍 進一步調試信號生成邏輯...")
            
            # 檢查最後幾個數據點的指標值
            last_rows = df_with_indicators.tail(10)
            print("最後10個數據點的關鍵指標:")
            key_indicators = ['close', 'rsi_14', 'macd', 'ema_20']
            for indicator in key_indicators:
                matching_cols = [col for col in last_rows.columns if indicator in col.lower()]
                if matching_cols:
                    col = matching_cols[0]
                    values = last_rows[col].dropna()
                    if len(values) > 0:
                        print(f"  {col}: 最新值 {values.iloc[-1]:.3f}")
        
    except Exception as e:
        print(f"❌ 測試過程出錯: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("🎯 修正版本測試完成")
    print("=" * 80)

if __name__ == "__main__":
    test_fixed_signal_generation()
