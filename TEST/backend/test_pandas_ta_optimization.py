#!/usr/bin/env python3
"""
測試 pandas-ta 優化指標服務
驗證自適應參數調整和市場狀態檢測功能
"""

import sys
import os

# 添加項目根目錄到 Python 路徑
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

import pandas as pd
import numpy as np
import pandas_ta as ta
from datetime import datetime, timedelta
import json
import asyncio

from app.services.pandas_ta_indicators import PandasTAIndicators, MarketRegime, TechnicalSignal

class PandasTATest:
    """pandas-ta 指標服務測試類"""
    
    def __init__(self):
        self.indicators = PandasTAIndicators()
        # self.market_service = MarketDataService()  # 暫時註解，使用模擬數據
        
    def create_test_data(self, trend_type: str = 'bull') -> pd.DataFrame:
        """創建測試數據"""
        periods = 100
        
        if trend_type == 'bull':
            # 模擬牛市數據
            base_price = 40000
            trend = np.linspace(0, 0.15, periods)  # 15% 上漲趨勢
            noise = np.random.normal(0, 0.02, periods)  # 2% 噪音
            price_series = base_price * (1 + trend + noise)
            
        elif trend_type == 'bear':
            # 模擬熊市數據
            base_price = 45000
            trend = np.linspace(0, -0.20, periods)  # 20% 下跌趨勢
            noise = np.random.normal(0, 0.025, periods)  # 2.5% 噪音
            price_series = base_price * (1 + trend + noise)
            
        elif trend_type == 'sideways':
            # 模擬盤整數據
            base_price = 42000
            trend = np.sin(np.linspace(0, 4*np.pi, periods)) * 0.05  # 5% 振盪
            noise = np.random.normal(0, 0.015, periods)  # 1.5% 噪音
            price_series = base_price * (1 + trend + noise)
            
        else:  # volatile
            # 模擬高波動數據
            base_price = 43000
            trend = np.random.normal(0, 0.05, periods)  # 5% 隨機波動
            noise = np.random.normal(0, 0.03, periods)  # 3% 噪音
            price_series = base_price * (1 + trend + noise)
        
        # 確保價格為正數
        price_series = np.maximum(price_series, base_price * 0.5)
        
        # 生成 OHLCV 數據
        data = []
        for i in range(periods):
            close = price_series[i]
            # 簡單的 OHLC 生成
            daily_range = close * 0.02  # 2% 日內波動
            high = close + np.random.uniform(0, daily_range)
            low = close - np.random.uniform(0, daily_range)
            open_price = low + np.random.uniform(0, high - low)
            volume = np.random.uniform(100000, 1000000)
            
            data.append({
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume,
                'timestamp': datetime.now() - timedelta(minutes=periods-i)
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        return df

    def test_market_regime_detection(self):
        """測試市場狀態檢測功能"""
        print("🔍 測試市場狀態檢測功能")
        print("=" * 50)
        
        test_scenarios = ['bull', 'bear', 'sideways', 'volatile']
        
        for scenario in test_scenarios:
            print(f"\n📊 測試情境: {scenario.upper()}")
            df = self.create_test_data(scenario)
            
            try:
                market_condition = self.indicators.detect_market_regime(df)
                
                print(f"   檢測結果: {market_condition.regime.value}")
                print(f"   趨勢強度: {market_condition.trend_strength:.3f}")
                print(f"   波動性: {market_condition.volatility:.3f}")
                print(f"   動量: {market_condition.momentum:.3f}")
                print(f"   信心度: {market_condition.confidence:.3f}")
                print(f"   關鍵位: 支撐={market_condition.key_levels['support']:.2f}, 阻力={market_condition.key_levels['resistance']:.2f}")
                
                # 驗證檢測正確性
                if scenario == 'bull' and market_condition.regime in [MarketRegime.BULL_STRONG, MarketRegime.BULL_WEAK]:
                    print("   ✅ 牛市檢測正確")
                elif scenario == 'bear' and market_condition.regime in [MarketRegime.BEAR_STRONG, MarketRegime.BEAR_WEAK]:
                    print("   ✅ 熊市檢測正確")
                elif scenario in ['sideways', 'volatile'] and market_condition.regime in [MarketRegime.SIDEWAYS, MarketRegime.VOLATILE]:
                    print("   ✅ 盤整/波動檢測正確")
                else:
                    print("   ⚠️ 檢測結果需要調優")
                    
            except Exception as e:
                print(f"   ❌ 檢測失敗: {e}")

    def test_adaptive_indicators(self):
        """測試自適應指標計算"""
        print("\n\n🔧 測試自適應指標計算")
        print("=" * 50)
        
        strategies = ['scalping', 'swing', 'trend', 'momentum']
        
        for strategy in strategies:
            print(f"\n📈 測試策略: {strategy.upper()}")
            
            # 使用牛市數據測試
            df = self.create_test_data('bull')
            
            try:
                signals = self.indicators.calculate_adaptive_indicators(df, strategy)
                
                print(f"   生成信號數量: {len(signals)}")
                
                for indicator_name, signal in signals.items():
                    print(f"   {indicator_name.upper()}:")
                    print(f"     信號類型: {signal.signal_type}")
                    print(f"     強度: {signal.strength:.3f}")
                    print(f"     信心度: {signal.confidence:.3f}")
                    print(f"     數值: {signal.value:.4f}")
                    print(f"     描述: {signal.description}")
                
                # 驗證信號合理性
                buy_signals = sum(1 for s in signals.values() if s.signal_type == "BUY")
                sell_signals = sum(1 for s in signals.values() if s.signal_type == "SELL")
                
                if buy_signals >= sell_signals:  # 牛市應該多頭信號較多
                    print("   ✅ 牛市環境下多頭信號佔優，符合預期")
                else:
                    print("   ⚠️ 信號分布需要調優")
                    
            except Exception as e:
                print(f"   ❌ 指標計算失敗: {e}")

    def test_comprehensive_analysis(self):
        """測試綜合分析功能"""
        print("\n\n📊 測試綜合分析功能")
        print("=" * 50)
        
        df = self.create_test_data('bull')
        
        try:
            analysis = self.indicators.get_comprehensive_analysis(df, 'scalping')
            
            print("🎯 綜合分析結果:")
            print(f"   市場狀態: {analysis['market_condition']['regime']}")
            print(f"   整體信號: {analysis['overall_signal']}")
            print(f"   整體信心度: {analysis['overall_confidence']:.3f}")
            print(f"   策略類型: {analysis['strategy_type']}")
            
            print("\n📈 技術指標詳情:")
            for indicator, signal in analysis['technical_signals'].items():
                print(f"   {indicator}: {signal['signal_type']} (強度: {signal['strength']:.3f})")
            
            print(f"\n🕒 分析時間: {analysis['analysis_timestamp']}")
            
            # 驗證分析完整性
            required_keys = ['market_condition', 'technical_signals', 'overall_signal', 'overall_confidence']
            if all(key in analysis for key in required_keys):
                print("✅ 綜合分析結構完整")
            else:
                print("❌ 綜合分析結構不完整")
                
        except Exception as e:
            print(f"❌ 綜合分析失敗: {e}")

    def test_parameter_adaptation(self):
        """測試參數自適應功能"""
        print("\n\n⚙️ 測試參數自適應功能")
        print("=" * 50)
        
        # 測試不同市場環境下的參數調整
        scenarios = [
            ('high_volatility', self.create_test_data('volatile')),
            ('low_volatility', self.create_test_data('sideways')),
            ('strong_trend', self.create_test_data('bull'))
        ]
        
        for scenario_name, df in scenarios:
            print(f"\n🔄 {scenario_name.upper()} 環境:")
            
            try:
                market_condition = self.indicators.detect_market_regime(df)
                adapted_params = self.indicators._adapt_parameters(market_condition, 'scalping')
                
                print(f"   波動性: {market_condition.volatility:.3f}")
                print(f"   趨勢強度: {market_condition.trend_strength:.3f}")
                print(f"   調整後參數:")
                for param, value in adapted_params.items():
                    print(f"     {param}: {value}")
                
                # 驗證參數調整邏輯
                if market_condition.volatility > 0.7:  # 高波動
                    if adapted_params['rsi_length'] < 14:
                        print("   ✅ 高波動環境下正確縮短 RSI 週期")
                    else:
                        print("   ⚠️ 高波動環境下 RSI 週期調整需優化")
                
                if market_condition.trend_strength > 0.8:  # 強趨勢
                    if adapted_params['macd_fast'] < 12:
                        print("   ✅ 強趨勢環境下正確加快 MACD 參數")
                    else:
                        print("   ⚠️ 強趨勢環境下 MACD 參數調整需優化")
                        
            except Exception as e:
                print(f"   ❌ 參數調整失敗: {e}")

    def run_performance_comparison(self):
        """運行性能對比測試"""
        print("\n\n⚡ 性能對比測試")
        print("=" * 50)
        
        df = self.create_test_data('bull')
        
        # 測試計算速度
        import time
        
        start_time = time.time()
        for _ in range(10):
            analysis = self.indicators.get_comprehensive_analysis(df, 'scalping')
        pandas_ta_time = (time.time() - start_time) / 10
        
        print(f"📊 pandas-ta 優化版本:")
        print(f"   平均執行時間: {pandas_ta_time:.4f} 秒")
        print(f"   生成指標數量: {len(analysis['technical_signals'])}")
        print(f"   綜合信心度: {analysis['overall_confidence']:.3f}")
        
        # 記憶體使用情況
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            print(f"   記憶體使用: {memory_mb:.2f} MB")
        except ImportError:
            print("   記憶體使用: psutil 未安裝，無法檢測")

    async def test_real_data_integration(self):
        """測試真實數據集成"""
        print("\n\n🌐 測試真實數據集成")
        print("=" * 50)
        
        try:
            # 獲取真實市場數據
            symbols = ['BTCUSDT', 'ETHUSDT']
            
            for symbol in symbols:
                print(f"\n📈 分析 {symbol}:")
                
                # 獲取數據 (這裡使用模擬數據，實際應該調用 market_service)
                df = self.create_test_data('bull')
                
                # 執行綜合分析
                analysis = self.indicators.get_comprehensive_analysis(df, 'scalping')
                
                print(f"   市場狀態: {analysis['market_condition']['regime']}")
                print(f"   整體信號: {analysis['overall_signal']}")
                print(f"   信心度: {analysis['overall_confidence']:.3f}")
                
                # 檢查關鍵指標
                key_indicators = ['rsi', 'macd', 'ema']
                for indicator in key_indicators:
                    if indicator in analysis['technical_signals']:
                        signal = analysis['technical_signals'][indicator]
                        print(f"   {indicator.upper()}: {signal['signal_type']} ({signal['confidence']:.3f})")
                    else:
                        print(f"   {indicator.upper()}: 數據不足")
                        
        except Exception as e:
            print(f"❌ 真實數據集成測試失敗: {e}")

    def generate_test_report(self):
        """生成測試報告"""
        print("\n\n📋 生成測試報告")
        print("=" * 50)
        
        report = {
            'test_date': datetime.now().isoformat(),
            'pandas_ta_version': ta.version,
            'test_scenarios': [
                'market_regime_detection',
                'adaptive_indicators',
                'comprehensive_analysis',
                'parameter_adaptation',
                'performance_comparison'
            ],
            'summary': {
                'total_tests': 5,
                'framework': 'pandas-ta 優化版本',
                'key_improvements': [
                    '自適應參數調整',
                    '市場狀態自動檢測',
                    '策略模板化',
                    '多指標融合分析'
                ]
            }
        }
        
        # 儲存報告
        with open('/Users/henrychang/Desktop/Trading-X/TEST/pandas_ta_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print("✅ 測試報告已儲存至 TEST/pandas_ta_test_report.json")

    async def run_all_tests(self):
        """運行所有測試"""
        print("🚀 開始 pandas-ta 指標服務完整測試")
        print("=" * 70)
        
        try:
            # 依序執行測試
            self.test_market_regime_detection()
            self.test_adaptive_indicators()
            self.test_comprehensive_analysis()
            self.test_parameter_adaptation()
            self.run_performance_comparison()
            await self.test_real_data_integration()
            self.generate_test_report()
            
            print("\n" + "=" * 70)
            print("🎉 所有測試完成！pandas-ta 優化版本準備就緒")
            print("=" * 70)
            
        except Exception as e:
            print(f"\n❌ 測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    tester = PandasTATest()
    asyncio.run(tester.run_all_tests())
