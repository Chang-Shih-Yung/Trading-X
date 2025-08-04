#!/usr/bin/env python3
"""
🎯 狙擊手信號篩選詳細調試腳本
顯示所有潛在信號點的詳細篩選過程
"""

import pandas as pd
import numpy as np
import pandas_ta as ta
from datetime import datetime
import logging
from sniper_unified_data_layer import SnipeDataUnifiedLayer, TradingTimeframe, MarketRegime

# 設置詳細日誌
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class DetailedSignalDebugger(SnipeDataUnifiedLayer):
    """增強版信號調試器，顯示每個信號的詳細篩選過程"""
    
    async def layer_two_dynamic_filter_debug(self, indicators, df):
        """第二層：動態過濾和信號品質控制 - 調試版本"""
        print(f"\n🔍 開始詳細信號篩選調試...")
        print(f"=" * 80)
        
        try:
            # 計算指標統計數據
            indicator_stats = await self._calculate_indicator_statistics(indicators)
            
            # 根據統計結果調整過濾參數
            dynamic_filter = self.layer_two_filter.adapt_to_results(indicator_stats)
            
            print(f"📊 動態篩選參數:")
            print(f"   RSI 超賣閾值: {dynamic_filter.rsi_oversold:.1f}")
            print(f"   MACD 直方圖閾值: {dynamic_filter.macd_histogram_threshold:.6f}")
            print(f"   成交量倍數閾值: {dynamic_filter.volume_spike_ratio:.2f}")
            print(f"   最低信號強度: {dynamic_filter.signal_strength_min:.1f}")
            print(f"   最低匯流數量: {dynamic_filter.confluence_min_count}")
            print(f"-" * 80)
            
            # 計算ATR和市場波動率
            atr_value = self.calculate_atr(df)
            current_price = df['close'].iloc[-1]
            returns = df['close'].pct_change().dropna()
            market_volatility = returns.std() * np.sqrt(24)
            
            signals = {
                'buy_signals': [],
                'signal_strength': [],
                'confluence_count': [],
                'filter_reasons': [],
                'dynamic_risk_params': []
            }
            
            # 統計計數器
            total_checked = 0
            passed_confluence = 0
            passed_strength = 0
            passed_volume = 0
            signal_details = []
            
            # 遍歷每個時間點進行信號檢測和過濾
            valid_length = min(len(df), min(len(series) for series in indicators.values() if isinstance(series, pd.Series)))
            start_idx = max(50, max(series.first_valid_index() or 0 for series in indicators.values() if isinstance(series, pd.Series)))
            
            print(f"📈 開始檢查 {valid_length - start_idx} 個時間點的信號...")
            print(f"   起始索引: {start_idx}, 結束索引: {valid_length-1}")
            print(f"-" * 80)
            
            for i in range(start_idx, valid_length):
                # 檢查所有關鍵指標是否有效
                if (pd.isna(indicators['rsi'].iloc[i]) or 
                    pd.isna(indicators['macd'].iloc[i]) or
                    pd.isna(indicators['bb_lower'].iloc[i])):
                    continue
                
                total_checked += 1
                current_signals = []
                filter_reasons = []
                
                # === 買入信號檢測 ===
                buy_confluence = 0
                confluence_details = []
                
                # 1. RSI 超賣
                rsi_val = indicators['rsi'].iloc[i]
                if rsi_val < dynamic_filter.rsi_oversold:
                    current_signals.append('rsi_oversold')
                    confluence_details.append(f"RSI超賣({rsi_val:.1f}<{dynamic_filter.rsi_oversold:.1f})")
                    buy_confluence += 1
                
                # 2. MACD 金叉
                if (i > start_idx and 
                    indicators['macd'].iloc[i] > indicators['macd_signal'].iloc[i] and 
                    indicators['macd'].iloc[i-1] <= indicators['macd_signal'].iloc[i-1] and
                    abs(indicators['macd_histogram'].iloc[i]) > dynamic_filter.macd_histogram_threshold):
                    current_signals.append('macd_bullish_cross')
                    confluence_details.append("MACD金叉")
                    buy_confluence += 1
                
                # 3. 布林帶下軌反彈
                if (i > start_idx and
                    df['close'].iloc[i] <= indicators['bb_lower'].iloc[i] and
                    df['close'].iloc[i-1] < indicators['bb_lower'].iloc[i-1] and
                    df['close'].iloc[i] > df['close'].iloc[i-1]):
                    current_signals.append('bb_bounce')
                    confluence_details.append("布林帶反彈")
                    buy_confluence += 1
                
                # 4. 隨機指標超賣反轉
                if (i > start_idx and
                    not pd.isna(indicators['stoch_k'].iloc[i]) and
                    indicators['stoch_k'].iloc[i] < 20 and 
                    indicators['stoch_k'].iloc[i] > indicators['stoch_k'].iloc[i-1]):
                    current_signals.append('stoch_oversold_reversal')
                    confluence_details.append("隨機指標反轉")
                    buy_confluence += 1
                
                # 5. EMA 金叉
                if (i > start_idx and
                    indicators['ema_fast'].iloc[i] > indicators['ema_slow'].iloc[i] and
                    indicators['ema_fast'].iloc[i-1] <= indicators['ema_slow'].iloc[i-1]):
                    current_signals.append('ema_bullish_cross')
                    confluence_details.append("EMA金叉")
                    buy_confluence += 1
                
                # 成交量確認
                volume_ratio = indicators['volume_ratio'].iloc[i] if not pd.isna(indicators['volume_ratio'].iloc[i]) else 0
                volume_confirmed = volume_ratio > dynamic_filter.volume_spike_ratio
                
                # 計算信號強度
                signal_strength = buy_confluence / 5.0
                
                # 記錄信號詳情
                signal_detail = {
                    'index': i,
                    'price': df['close'].iloc[i],
                    'rsi': rsi_val,
                    'confluence_count': buy_confluence,
                    'confluence_details': confluence_details,
                    'signal_strength': signal_strength,
                    'volume_ratio': volume_ratio,
                    'volume_confirmed': volume_confirmed,
                    'passed_confluence': False,
                    'passed_strength': False,
                    'passed_volume': False,
                    'final_result': False,
                    'filter_reason': ''
                }
                
                # 第一關：匯流檢查
                if buy_confluence >= dynamic_filter.confluence_min_count:
                    signal_detail['passed_confluence'] = True
                    passed_confluence += 1
                    
                    # 第二關：信號強度檢查
                    if signal_strength >= dynamic_filter.signal_strength_min:
                        signal_detail['passed_strength'] = True
                        passed_strength += 1
                        
                        # 第三關：成交量確認或強度豁免
                        if volume_confirmed or signal_strength > 0.2:
                            signal_detail['passed_volume'] = True
                            signal_detail['final_result'] = True
                            signal_detail['filter_reason'] = '✅ 通過所有篩選'
                            passed_volume += 1
                            
                            signals['buy_signals'].append(True)
                            signals['signal_strength'].append(signal_strength)
                            signals['confluence_count'].append(buy_confluence)
                            signals['filter_reasons'].append('passed_all_filters')
                        else:
                            signal_detail['filter_reason'] = f'❌ 成交量不足 (比率:{volume_ratio:.2f}<{dynamic_filter.volume_spike_ratio:.2f}, 強度:{signal_strength:.2f}≤0.2)'
                            signals['buy_signals'].append(False)
                            signals['signal_strength'].append(signal_strength)
                            signals['confluence_count'].append(buy_confluence)
                            signals['filter_reasons'].append('volume_insufficient')
                    else:
                        signal_detail['filter_reason'] = f'❌ 信號強度不足 ({signal_strength:.2f}<{dynamic_filter.signal_strength_min:.1f})'
                        signals['buy_signals'].append(False)
                        signals['signal_strength'].append(signal_strength)
                        signals['confluence_count'].append(buy_confluence)
                        signals['filter_reasons'].append('signal_strength_too_low')
                else:
                    signal_detail['filter_reason'] = f'❌ 匯流不足 ({buy_confluence}<{dynamic_filter.confluence_min_count})'
                    signals['buy_signals'].append(False)
                    signals['signal_strength'].append(signal_strength)
                    signals['confluence_count'].append(buy_confluence)
                    signals['filter_reasons'].append('insufficient_confluence')
                
                signal_details.append(signal_detail)
            
            # 顯示統計總結
            print(f"\n📊 篩選統計總結:")
            print(f"   總檢查點數: {total_checked}")
            print(f"   通過匯流關: {passed_confluence} ({passed_confluence/max(total_checked,1)*100:.1f}%)")
            print(f"   通過強度關: {passed_strength} ({passed_strength/max(total_checked,1)*100:.1f}%)")
            print(f"   通過成交量關: {passed_volume} ({passed_volume/max(total_checked,1)*100:.1f}%)")
            print(f"-" * 80)
            
            # 顯示所有信號詳情（前20個和最後10個）
            print(f"\n🔍 信號詳細分析 (顯示前20個 + 最後10個):")
            print(f"=" * 120)
            
            # 顯示前20個
            for i, detail in enumerate(signal_details[:20]):
                confluence_str = ", ".join(detail['confluence_details']) if detail['confluence_details'] else "無匯流"
                print(f"#{i+1:2d} | 索引:{detail['index']:2d} | 價格:{detail['price']:8.2f} | RSI:{detail['rsi']:5.1f} | "
                      f"匯流:{detail['confluence_count']}/5 ({confluence_str[:30]:<30}) | "
                      f"強度:{detail['signal_strength']:.2f} | 成交量:{detail['volume_ratio']:.2f} | {detail['filter_reason']}")
            
            if len(signal_details) > 30:
                print(f"... (省略中間 {len(signal_details)-30} 個信號)")
                # 顯示最後10個
                for i, detail in enumerate(signal_details[-10:], len(signal_details)-10):
                    confluence_str = ", ".join(detail['confluence_details']) if detail['confluence_details'] else "無匯流"
                    print(f"#{i+1:2d} | 索引:{detail['index']:2d} | 價格:{detail['price']:8.2f} | RSI:{detail['rsi']:5.1f} | "
                          f"匯流:{detail['confluence_count']}/5 ({confluence_str[:30]:<30}) | "
                          f"強度:{detail['signal_strength']:.2f} | 成交量:{detail['volume_ratio']:.2f} | {detail['filter_reason']}")
            
            print(f"=" * 120)
            
            # 按篩選原因分組統計
            filter_stats = {}
            for detail in signal_details:
                reason = detail['filter_reason'].split('(')[0].strip()  # 取主要原因
                filter_stats[reason] = filter_stats.get(reason, 0) + 1
            
            print(f"\n📈 篩選原因統計:")
            for reason, count in sorted(filter_stats.items(), key=lambda x: x[1], reverse=True):
                print(f"   {reason}: {count} 個 ({count/len(signal_details)*100:.1f}%)")
            
            return {
                'signals': signals,
                'dynamic_filter_config': dynamic_filter,
                'indicator_stats': indicator_stats,
                'signal_details': signal_details,
                'stats': {
                    'total_checked': total_checked,
                    'passed_confluence': passed_confluence,
                    'passed_strength': passed_strength,
                    'passed_volume': passed_volume,
                    'filter_stats': filter_stats
                },
                'market_metrics': {
                    'atr_value': atr_value,
                    'market_volatility': market_volatility,
                    'current_price': current_price
                }
            }
            
        except Exception as e:
            logger.error(f"❌ 詳細篩選調試失敗: {e}")
            return {}

async def debug_signal_filtering():
    """執行詳細信號篩選調試"""
    print("🎯 狙擊手信號篩選詳細調試")
    print("=" * 80)
    
    # 初始化調試器
    debugger = DetailedSignalDebugger()
    
    # 測試 BTCUSDT (這個有37個被篩掉的信號)
    symbol = 'BTCUSDT'
    timeframe = 'short'
    
    print(f"📊 調試 {symbol} ({timeframe}線策略)...")
    
    # 創建測試數據
    dates = pd.date_range(start='2024-12-01', periods=100, freq='1H')
    base_price = 50000
    volatility = 0.02
    
    prices = []
    current_price = base_price
    for i in range(100):
        change = np.random.normal(0, volatility) * current_price
        current_price += change
        prices.append(max(current_price, base_price * 0.5))
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': [p * (1 + np.random.uniform(0, 0.01)) for p in prices],
        'low': [p * (1 - np.random.uniform(0, 0.01)) for p in prices],
        'close': prices,
        'volume': [1000 + np.random.uniform(-200, 500) for _ in range(100)]
    })
    
    # 設置交易時間框架
    debugger.set_trading_timeframe(timeframe)
    
    # 分析市場狀態
    debugger.market_regime = await debugger.analyze_market_regime(df)
    
    # 第一層指標計算
    indicators = await debugger.layer_one_calculate_indicators(df)
    
    if not indicators:
        print("❌ 指標計算失敗")
        return
    
    # 第二層詳細篩選調試
    debug_results = await debugger.layer_two_dynamic_filter_debug(indicators, df)
    
    if debug_results:
        print(f"\n✅ 調試完成！")
        print(f"   總共檢查了 {debug_results['stats']['total_checked']} 個潛在信號點")
        print(f"   最終通過: {debug_results['stats']['passed_volume']} 個")
        print(f"   篩選成功率: {debug_results['stats']['passed_volume']/max(debug_results['stats']['total_checked'],1)*100:.2f}%")

if __name__ == "__main__":
    import asyncio
    asyncio.run(debug_signal_filtering())
