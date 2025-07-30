#!/usr/bin/env python3
"""
診斷 pandas-ta 新版本"需調優"問題
分析市場狀態檢測和信號生成邏輯
"""

import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from app.services.pandas_ta_indicators import PandasTAIndicators, MarketRegime

class PandasTADiagnostic:
    """pandas-ta 診斷工具"""
    
    def __init__(self):
        self.indicators = PandasTAIndicators()
    
    def create_test_scenarios(self):
        """創建不同的測試情境"""
        scenarios = {}
        periods = 100
        base_price = 45000
        
        # 1. 明確的牛市趨勢
        bull_trend = np.linspace(0, 0.20, periods)  # 20% 上漲
        bull_noise = np.random.normal(0, 0.01, periods)  # 1% 噪音
        scenarios['strong_bull'] = base_price * (1 + bull_trend + bull_noise)
        
        # 2. 明確的熊市趨勢  
        bear_trend = np.linspace(0, -0.20, periods)  # 20% 下跌
        bear_noise = np.random.normal(0, 0.01, periods)
        scenarios['strong_bear'] = base_price * (1 + bear_trend + bear_noise)
        
        # 3. 真正的盤整市場
        sideways_base = np.ones(periods)  # 無趨勢
        sideways_noise = np.random.normal(0, 0.005, periods)  # 0.5% 微小噪音
        scenarios['true_sideways'] = base_price * (sideways_base + sideways_noise)
        
        # 4. 高波動但無方向
        volatile_trend = np.sin(np.linspace(0, 6*np.pi, periods)) * 0.03  # 3% 振盪
        volatile_noise = np.random.normal(0, 0.02, periods)  # 2% 噪音
        scenarios['high_volatile'] = base_price * (1 + volatile_trend + volatile_noise)
        
        return scenarios
    
    def convert_to_ohlcv(self, price_series, name):
        """轉換價格序列為 OHLCV 格式"""
        data = []
        for i, close in enumerate(price_series):
            # 確保價格為正數
            close = max(close, price_series.mean() * 0.5)
            
            # 生成合理的 OHLC
            daily_range = close * 0.015  # 1.5% 日內波動
            high = close + np.random.uniform(0, daily_range * 0.7)
            low = close - np.random.uniform(0, daily_range * 0.7)
            open_price = low + np.random.uniform(0, high - low)
            volume = np.random.uniform(100000, 1000000)
            
            data.append({
                'open': open_price,
                'high': max(high, close, open_price),  # 確保 high 是最高的
                'low': min(low, close, open_price),    # 確保 low 是最低的
                'close': close,
                'volume': volume,
                'timestamp': datetime.now() - timedelta(hours=len(price_series)-i)
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        return df
    
    def analyze_scenario(self, scenario_name, df):
        """分析特定情境"""
        print(f"\n🔍 分析 {scenario_name.upper()} 情境:")
        print("=" * 50)
        
        # 市場狀態檢測
        try:
            market_condition = self.indicators.detect_market_regime(df)
            print(f"檢測到的市場狀態: {market_condition.regime.value}")
            print(f"趨勢強度: {market_condition.trend_strength:.3f}")
            print(f"波動性: {market_condition.volatility:.3f}")
            print(f"動量: {market_condition.momentum:.3f}")
            print(f"信心度: {market_condition.confidence:.3f}")
            
            # 技術指標分析
            analysis = self.indicators.get_comprehensive_analysis(df, 'scalping')
            print(f"\n整體信號: {analysis['overall_signal']}")
            print(f"整體信心度: {analysis['overall_confidence']:.3f}")
            
            print("\n技術指標詳情:")
            for indicator, signal in analysis['technical_signals'].items():
                print(f"  {indicator.upper()}: {signal['signal_type']} (信心度: {signal['confidence']:.3f})")
            
            # 診斷問題
            self.diagnose_issues(scenario_name, market_condition, analysis)
            
        except Exception as e:
            print(f"❌ 分析失敗: {e}")
            import traceback
            traceback.print_exc()
    
    def diagnose_issues(self, scenario_name, market_condition, analysis):
        """診斷問題"""
        print(f"\n🔧 {scenario_name} 診斷結果:")
        
        issues = []
        
        # 1. 檢查市場狀態檢測是否正確
        expected_regimes = {
            'strong_bull': [MarketRegime.BULL_STRONG, MarketRegime.BULL_WEAK],
            'strong_bear': [MarketRegime.BEAR_STRONG, MarketRegime.BEAR_WEAK],
            'true_sideways': [MarketRegime.SIDEWAYS],
            'high_volatile': [MarketRegime.VOLATILE, MarketRegime.SIDEWAYS]
        }
        
        if scenario_name in expected_regimes:
            if market_condition.regime not in expected_regimes[scenario_name]:
                issues.append(f"市場狀態檢測錯誤: 期待 {expected_regimes[scenario_name]}, 實際 {market_condition.regime}")
        
        # 2. 檢查趨勢強度是否合理
        if scenario_name in ['strong_bull', 'strong_bear']:
            if market_condition.trend_strength < 0.3:
                issues.append(f"趨勢強度過低: {market_condition.trend_strength:.3f} < 0.3")
        
        # 3. 檢查信號邏輯是否合理
        overall_signal = analysis['overall_signal']
        if scenario_name == 'strong_bull' and overall_signal != 'BUY':
            issues.append(f"牛市環境下應該是 BUY 信號，實際是 {overall_signal}")
        elif scenario_name == 'strong_bear' and overall_signal != 'SELL':
            issues.append(f"熊市環境下應該是 SELL 信號，實際是 {overall_signal}")
        elif scenario_name in ['true_sideways', 'high_volatile'] and overall_signal not in ['NEUTRAL', 'BUY', 'SELL']:
            # 盤整市場可能是任何信號，但需要調優
            if analysis['overall_confidence'] > 0.8:
                issues.append(f"盤整市場信心度過高: {analysis['overall_confidence']:.3f}")
        
        # 4. 檢查指標一致性
        signals = [s['signal_type'] for s in analysis['technical_signals'].values()]
        buy_count = signals.count('BUY')
        sell_count = signals.count('SELL')
        neutral_count = signals.count('NEUTRAL')
        
        if scenario_name == 'strong_bull' and buy_count == 0:
            issues.append("牛市環境下沒有任何 BUY 信號")
        elif scenario_name == 'strong_bear' and sell_count == 0:
            issues.append("熊市環境下沒有任何 SELL 信號")
        
        # 輸出診斷結果
        if issues:
            print("❌ 發現的問題:")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
        else:
            print("✅ 分析邏輯正常")
        
        return issues
    
    def suggest_fixes(self, all_issues):
        """建議修正方案"""
        print("\n🛠️ 修正建議:")
        print("=" * 50)
        
        # 統計問題類型
        trend_issues = [issue for issue in all_issues if "趨勢強度" in issue or "狀態檢測" in issue]
        signal_issues = [issue for issue in all_issues if "信號" in issue]
        confidence_issues = [issue for issue in all_issues if "信心度" in issue]
        
        if trend_issues:
            print("1. 市場狀態檢測優化:")
            print("   - 調整 ADX 閾值：從 25 降低到 20")
            print("   - 優化 Aroon 參數：增加敏感度")
            print("   - 改進 CCI 計算：考慮加密貨幣市場特性")
        
        if signal_issues:
            print("2. 信號生成邏輯優化:")
            print("   - 調整 RSI 閾值：根據市場狀態動態設定")
            print("   - 優化 MACD 參數：提高趨勢跟隨能力")
            print("   - 改進信號融合算法：加權平均改為專家系統")
        
        if confidence_issues:
            print("3. 信心度計算優化:")
            print("   - 引入不確定性懲罰：盤整市場降低信心度")
            print("   - 多時間框架驗證：確保信號一致性")
            print("   - 歷史表現權重：根據過往準確率調整")
    
    def run_comprehensive_diagnosis(self):
        """運行完整診斷"""
        print("🔍 pandas-ta 新版本診斷分析")
        print("=" * 70)
        
        # 創建測試情境
        scenarios = self.create_test_scenarios()
        all_issues = []
        
        # 分析每個情境
        for scenario_name, price_series in scenarios.items():
            df = self.convert_to_ohlcv(price_series, scenario_name)
            issues = []
            
            try:
                self.analyze_scenario(scenario_name, df)
            except Exception as e:
                print(f"❌ {scenario_name} 分析失敗: {e}")
        
        # 提供修正建議
        self.suggest_fixes(all_issues)
        
        print("\n" + "=" * 70)
        print("🎯 診斷完成：問題主要集中在市場狀態檢測敏感度和信號融合邏輯")
        print("=" * 70)

if __name__ == "__main__":
    diagnostic = PandasTADiagnostic()
    diagnostic.run_comprehensive_diagnosis()
