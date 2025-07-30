#!/usr/bin/env python3
"""
使用真實市場數據的 pandas-ta 優化測試
解決信號生成問題並驗證優化效果
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

def generate_realistic_crypto_data(periods=500):
    """生成更真實的加密貨幣市場數據"""
    np.random.seed(42)
    
    # 從實際 BTC 價格範圍開始
    base_price = 50000.0
    price = base_price
    
    data = []
    trend_phase = 0  # 0: 盤整, 1: 上漲, -1: 下跌
    trend_duration = 0
    
    for i in range(periods):
        # 模擬趨勢變化
        if trend_duration <= 0:
            trend_phase = np.random.choice([-1, 0, 1], p=[0.3, 0.4, 0.3])
            trend_duration = np.random.randint(20, 80)
        
        # 根據趨勢調整價格變動
        if trend_phase == 1:  # 上漲趨勢
            change = np.random.normal(0.005, 0.02)  # 平均上漲0.5%
        elif trend_phase == -1:  # 下跌趨勢
            change = np.random.normal(-0.005, 0.02)  # 平均下跌0.5%
        else:  # 盤整
            change = np.random.normal(0, 0.015)  # 橫盤波動
        
        price = max(price * (1 + change), 10000)  # 防止價格過低
        
        # 生成 OHLC
        volatility = abs(np.random.normal(0, 0.008))
        high = price * (1 + volatility)
        low = price * (1 - volatility)
        open_price = price * (1 + np.random.normal(0, 0.003))
        
        # 生成更真實的成交量 (與價格變動相關)
        volume_base = 1000000000
        volume_multiplier = 1 + abs(change) * 5  # 波動大時成交量增加
        volume = volume_base * volume_multiplier * np.random.normal(1, 0.3)
        volume = max(volume, 100000000)
        
        data.append({
            'timestamp': datetime.now() - timedelta(hours=periods-i),
            'open': open_price,
            'high': high,
            'low': low,
            'close': price,
            'volume': volume
        })
        
        trend_duration -= 1
    
    return pd.DataFrame(data)

def test_signal_generation_debug():
    """調試信號生成問題"""
    print("=" * 80)
    print("🔍 真實數據信號生成調試測試")
    print("=" * 80)
    
    # 生成更真實的數據
    print("📊 生成真實市場數據...")
    df = generate_realistic_crypto_data(500)
    print(f"✅ 生成了 {len(df)} 筆數據")
    print(f"📈 價格範圍: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
    print(f"📊 平均成交量: {df['volume'].mean():.0f}")
    
    # 檢查數據質量
    price_change = (df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0] * 100
    volatility = df['close'].pct_change().std() * 100
    print(f"📈 總價格變動: {price_change:.2f}%")
    print(f"🌊 波動率: {volatility:.2f}%")
    
    try:
        # 導入並測試原始信號生成器
        from app.services.pandas_ta_trading_signal_parser import PandasTATradingSignals
        
        print("\n🔧 初始化信號解析器...")
        parser = PandasTATradingSignals()
        
        # 嘗試生成信號
        print("\n📈 生成原始信號...")
        signals = parser.generate_signals(df, strategy="swing")
        
        if signals:
            print(f"✅ 成功生成 {len(signals)} 個信號")
            
            # 分析信號類型
            buy_signals = [s for s in signals if hasattr(s, 'signal_type') and 'BUY' in str(s.signal_type)]
            sell_signals = [s for s in signals if hasattr(s, 'signal_type') and 'SELL' in str(s.signal_type)]
            
            print(f"  • 買入信號: {len(buy_signals)}")
            print(f"  • 賣出信號: {len(sell_signals)}")
            
            # 顯示最近的幾個信號詳情
            print("\n🔍 最近信號詳情:")
            for i, signal in enumerate(signals[-3:]):
                print(f"  {i+1}. {signal.indicator}: {signal.signal_type} (強度: {signal.strength:.3f})")
        else:
            print("❌ 沒有生成任何信號")
            print("\n🔍 調試信息:")
            
            # 檢查指標計算
            print("📊 檢查基礎指標計算...")
            try:
                df_with_indicators = parser.calculate_all_indicators(df, "swing")
                print(f"✅ 指標計算成功，數據形狀: {df_with_indicators.shape}")
                
                # 檢查關鍵指標
                key_indicators = ['close', 'rsi_14', 'macd', 'ema_20']
                for indicator in key_indicators:
                    if f'{indicator}' in df_with_indicators.columns or indicator in df_with_indicators.columns:
                        col_name = indicator if indicator in df_with_indicators.columns else f'{indicator}'
                        values = df_with_indicators[col_name].dropna()
                        if len(values) > 0:
                            print(f"  ✅ {indicator}: {len(values)} 個有效值，範圍 {values.min():.3f} - {values.max():.3f}")
                        else:
                            print(f"  ❌ {indicator}: 無有效值")
                    else:
                        print(f"  ⚠️ {indicator}: 欄位不存在")
                        
            except Exception as e:
                print(f"❌ 指標計算失敗: {e}")
        
        # 測試市場狀態評估
        print("\n🌡️ 測試市場狀態評估...")
        try:
            # 簡單的市場健康度計算
            price_volatility = df['close'].pct_change().std()
            volume_stability = df['volume'].std() / df['volume'].mean()
            trend_direction = (df['close'].iloc[-1] - df['close'].iloc[-20]) / df['close'].iloc[-20]
            
            volatility_score = max(0, 1 - price_volatility * 20)
            volume_score = max(0, 1 - volume_stability)
            trend_score = min(abs(trend_direction) * 5, 1.0)
            
            market_health = (volatility_score + volume_score + trend_score) / 3
            market_status = "GOOD" if market_health > 0.6 else "FAIR" if market_health > 0.4 else "POOR"
            
            print(f"  • 市場健康度: {market_health:.3f}")
            print(f"  • 市場狀態: {market_status}")
            print(f"  • 波動性評分: {volatility_score:.3f}")
            print(f"  • 成交量評分: {volume_score:.3f}")
            print(f"  • 趨勢評分: {trend_score:.3f}")
            
        except Exception as e:
            print(f"❌ 市場狀態評估失敗: {e}")
        
    except ImportError as e:
        print(f"❌ 導入錯誤: {e}")
    except Exception as e:
        print(f"❌ 測試過程出錯: {e}")
    
    print("\n" + "=" * 80)
    print("🎯 調試測試完成")
    print("=" * 80)
    
    # 提供改進建議
    print("\n💡 改進建議:")
    print("1. 檢查 pandas_ta_trading_signals.json 配置文件")
    print("2. 驗證指標計算的閾值設定")
    print("3. 調整信號生成的敏感度參數")
    print("4. 確保數據格式符合指標要求")

if __name__ == "__main__":
    test_signal_generation_debug()
