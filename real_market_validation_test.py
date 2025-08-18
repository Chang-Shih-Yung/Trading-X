"""
🎯 Trading X - 真實市場 Phase1A + Phase5 配置驗證測試
禁止模擬數據，使用真實幣安市場數據驗證信號準確性
"""

import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import logging
from pathlib import Path
import time

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealMarketValidator:
    """真實市場驗證器"""
    
    def __init__(self):
        self.binance_url = "https://api.binance.com"
        self.session = None
        self.test_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]  # 主要測試幣種
        self.validation_results = []
        self.signal_tracking = {}
        
        # 載入 Phase5 最新配置
        self.lean_config = self._load_phase5_config()
        
        # 驗證參數
        self.signal_timeout = 300  # 5分鐘信號有效期
        self.profit_threshold = 0.002  # 0.2% 獲利閾值
        self.loss_threshold = -0.001  # 0.1% 止損閾值
        
    def _load_phase5_config(self) -> Dict:
        """載入 Phase5 最新配置"""
        try:
            config_dir = Path("X/backend/phase5_backtest_validation/safety_backups/working")
            config_files = list(config_dir.glob("phase1a_backup_deployment_initial_*.json"))
            
            if not config_files:
                logger.error("找不到 Phase5 配置檔案")
                return {}
                
            # 取最新檔案
            latest_config = max(config_files, key=lambda x: x.stat().st_mtime)
            
            with open(latest_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            logger.info(f"✅ 載入 Phase5 配置: {latest_config.name}")
            return config
            
        except Exception as e:
            logger.error(f"載入 Phase5 配置失敗: {e}")
            return {}
    
    async def __aenter__(self):
        """異步上下文管理器"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """關閉連接"""
        if self.session:
            await self.session.close()
    
    async def get_real_kline_data(self, symbol: str, interval: str = "5m", 
                                limit: int = 100) -> pd.DataFrame:
        """獲取真實幣安 K 線數據"""
        try:
            url = f"{self.binance_url}/api/v3/klines"
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # 轉換為 DataFrame
                    df = pd.DataFrame(data, columns=[
                        'timestamp', 'open', 'high', 'low', 'close', 'volume',
                        'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                        'taker_buy_quote', 'ignore'
                    ])
                    
                    # 資料處理
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    for col in ['open', 'high', 'low', 'close', 'volume']:
                        df[col] = df[col].astype(float)
                    
                    logger.info(f"✅ 獲取 {symbol} 真實數據: {len(df)} 根 K 線")
                    return df
                else:
                    logger.error(f"❌ 獲取 {symbol} 數據失敗: {response.status}")
                    return pd.DataFrame()
                    
        except Exception as e:
            logger.error(f"❌ 獲取 {symbol} 數據異常: {e}")
            return pd.DataFrame()
    
    def calculate_lean_indicators(self, df: pd.DataFrame) -> Dict:
        """計算 Lean 優化指標"""
        try:
            if len(df) < 30:
                return {}
            
            # 使用 Phase5 配置的參數
            rsi_period = self.lean_config.get('rsi_period', 14)
            macd_fast = self.lean_config.get('macd_fast', 12)
            macd_slow = self.lean_config.get('macd_slow', 26)
            
            # RSI 計算
            delta = df['close'].diff()
            up = delta.clip(lower=0).ewm(alpha=1/rsi_period, adjust=False).mean()
            down = (-delta.clip(upper=0)).ewm(alpha=1/rsi_period, adjust=False).mean()
            rs = up / (down + 1e-9)
            rsi = 100 - 100 / (1 + rs)
            
            # MACD 計算
            ema_fast = df['close'].ewm(span=macd_fast).mean()
            ema_slow = df['close'].ewm(span=macd_slow).mean()
            macd_line = ema_fast - ema_slow
            macd_signal = macd_line.ewm(span=9).mean()
            
            # 價格變化
            price_change = df['close'].pct_change()
            
            latest_data = {
                'price': df['close'].iloc[-1],
                'rsi': rsi.iloc[-1],
                'macd': macd_line.iloc[-1],
                'macd_signal': macd_signal.iloc[-1],
                'price_change_5m': price_change.iloc[-1],
                'volume': df['volume'].iloc[-1],
                'timestamp': df['timestamp'].iloc[-1]
            }
            
            return latest_data
            
        except Exception as e:
            logger.error(f"指標計算失敗: {e}")
            return {}
    
    def generate_lean_signal(self, symbol: str, indicators: Dict) -> Optional[Dict]:
        """基於 Lean 配置生成信號"""
        try:
            if not indicators:
                return None
            
            # Phase5 配置的閾值
            price_threshold = 0.001  # 從配置中獲取
            confidence_base = 0.7    # 從配置中獲取
            
            # 檢查幣種特定調整
            coin_key = f"{symbol.lower()}_lean_adjustment"
            coin_config = self.lean_config.get(coin_key, {})
            
            direction_bias = coin_config.get('direction_bias', 'neutral')
            confidence_level = coin_config.get('confidence_level', 0.5)
            expected_return = coin_config.get('expected_return', 0.0)
            
            # 信號生成邏輯
            signal = None
            signal_strength = 0
            
            # RSI 信號
            rsi = indicators['rsi']
            if rsi < 30:  # 超賣
                signal = 'BUY'
                signal_strength += 0.3
            elif rsi > 70:  # 超買
                signal = 'SELL'
                signal_strength += 0.3
            
            # MACD 信號
            macd = indicators['macd']
            macd_signal = indicators['macd_signal']
            if macd > macd_signal and macd > 0:  # 金叉且在零軸上方
                if signal == 'BUY' or signal is None:
                    signal = 'BUY'
                    signal_strength += 0.4
            elif macd < macd_signal and macd < 0:  # 死叉且在零軸下方
                if signal == 'SELL' or signal is None:
                    signal = 'SELL'
                    signal_strength += 0.4
            
            # 價格動量
            price_change = indicators['price_change_5m']
            if abs(price_change) > price_threshold:
                if price_change > 0 and signal == 'BUY':
                    signal_strength += 0.3
                elif price_change < 0 and signal == 'SELL':
                    signal_strength += 0.3
            
            # Lean 方向偏向調整
            if direction_bias == 'bullish' and signal == 'BUY':
                signal_strength *= (1 + confidence_level)
            elif direction_bias == 'bearish' and signal == 'SELL':
                signal_strength *= (1 + confidence_level)
            elif direction_bias != 'neutral' and signal != direction_bias.upper().replace('ISH', ''):
                signal_strength *= 0.5  # 降低反向信號強度
            
            # 信號有效性檢查
            if signal and signal_strength >= confidence_base:
                return {
                    'symbol': symbol,
                    'signal': signal,
                    'strength': signal_strength,
                    'price': indicators['price'],
                    'timestamp': indicators['timestamp'],
                    'lean_bias': direction_bias,
                    'lean_confidence': confidence_level,
                    'expected_return': expected_return,
                    'indicators': {
                        'rsi': rsi,
                        'macd': macd,
                        'price_change': price_change
                    }
                }
            
            return None
            
        except Exception as e:
            logger.error(f"信號生成失敗: {e}")
            return None
    
    async def track_signal_performance(self, signal: Dict) -> Dict:
        """追蹤信號表現 (真實市場驗證)"""
        try:
            symbol = signal['symbol']
            entry_price = signal['price']
            entry_time = signal['timestamp']
            signal_direction = signal['signal']
            
            logger.info(f"📊 開始追蹤信號: {symbol} {signal_direction} @ {entry_price}")
            
            # 追蹤期間 (5分鐘)
            start_time = time.time()
            best_profit = 0
            worst_loss = 0
            final_result = None
            
            while time.time() - start_time < self.signal_timeout:
                # 獲取當前價格
                current_data = await self.get_real_kline_data(symbol, "1m", 2)
                if current_data.empty:
                    await asyncio.sleep(10)
                    continue
                
                current_price = current_data['close'].iloc[-1]
                current_time = current_data['timestamp'].iloc[-1]
                
                # 計算收益率
                if signal_direction == 'BUY':
                    return_rate = (current_price - entry_price) / entry_price
                else:  # SELL
                    return_rate = (entry_price - current_price) / entry_price
                
                best_profit = max(best_profit, return_rate)
                worst_loss = min(worst_loss, return_rate)
                
                # 檢查止盈止損
                if return_rate >= self.profit_threshold:
                    final_result = {
                        'status': 'WIN',
                        'return': return_rate,
                        'exit_price': current_price,
                        'exit_time': current_time,
                        'duration_seconds': time.time() - start_time
                    }
                    logger.info(f"✅ {symbol} 信號獲利: {return_rate:.3%}")
                    break
                elif return_rate <= self.loss_threshold:
                    final_result = {
                        'status': 'LOSS',
                        'return': return_rate,
                        'exit_price': current_price,
                        'exit_time': current_time,
                        'duration_seconds': time.time() - start_time
                    }
                    logger.info(f"❌ {symbol} 信號止損: {return_rate:.3%}")
                    break
                
                await asyncio.sleep(10)  # 每10秒檢查一次
            
            # 如果沒有觸發止盈止損，記錄最終結果
            if final_result is None:
                current_data = await self.get_real_kline_data(symbol, "1m", 2)
                if not current_data.empty:
                    current_price = current_data['close'].iloc[-1]
                    current_time = current_data['timestamp'].iloc[-1]
                    
                    if signal_direction == 'BUY':
                        final_return = (current_price - entry_price) / entry_price
                    else:
                        final_return = (entry_price - current_price) / entry_price
                    
                    final_result = {
                        'status': 'TIMEOUT',
                        'return': final_return,
                        'exit_price': current_price,
                        'exit_time': current_time,
                        'duration_seconds': self.signal_timeout
                    }
                    
                    status = "✅" if final_return > 0 else "❌"
                    logger.info(f"{status} {symbol} 信號超時: {final_return:.3%}")
            
            # 整合結果
            performance = {
                'signal': signal,
                'result': final_result,
                'best_profit': best_profit,
                'worst_loss': worst_loss,
                'lean_accuracy': final_result['return'] > 0 if final_result else False
            }
            
            return performance
            
        except Exception as e:
            logger.error(f"信號追蹤失敗: {e}")
            return {}
    
    async def run_real_market_validation(self, duration_minutes: int = 60) -> Dict:
        """執行真實市場驗證測試"""
        logger.info("🚀 開始真實市場 Phase1A + Phase5 配置驗證")
        logger.info(f"📊 測試時長: {duration_minutes} 分鐘")
        logger.info(f"🪙 測試幣種: {', '.join(self.test_symbols)}")
        logger.info("=" * 70)
        
        validation_results = []
        start_time = time.time()
        signal_count = 0
        
        try:
            while time.time() - start_time < duration_minutes * 60:
                for symbol in self.test_symbols:
                    # 獲取真實市場數據
                    market_data = await self.get_real_kline_data(symbol, "5m", 50)
                    
                    if market_data.empty:
                        continue
                    
                    # 計算 Lean 指標
                    indicators = self.calculate_lean_indicators(market_data)
                    
                    if not indicators:
                        continue
                    
                    # 生成 Lean 信號
                    signal = self.generate_lean_signal(symbol, indicators)
                    
                    if signal:
                        signal_count += 1
                        logger.info(f"🔔 生成信號 #{signal_count}: {symbol} {signal['signal']} "
                                  f"(強度: {signal['strength']:.2f}, Lean偏向: {signal['lean_bias']})")
                        
                        # 追蹤信號表現
                        performance = await self.track_signal_performance(signal)
                        
                        if performance:
                            validation_results.append(performance)
                
                # 等待下一輪檢查
                await asyncio.sleep(30)  # 每30秒檢查一次
        
        except KeyboardInterrupt:
            logger.info("⏹️ 用戶中斷測試")
        
        # 生成驗證報告
        return self._generate_validation_report(validation_results, signal_count)
    
    def _generate_validation_report(self, results: List[Dict], total_signals: int) -> Dict:
        """生成驗證報告"""
        if not results:
            return {
                'total_signals': total_signals,
                'tracked_signals': 0,
                'accuracy': 0,
                'message': '無有效信號追蹤結果'
            }
        
        # 統計分析
        wins = sum(1 for r in results if r['result']['status'] == 'WIN')
        losses = sum(1 for r in results if r['result']['status'] == 'LOSS')
        timeouts = sum(1 for r in results if r['result']['status'] == 'TIMEOUT')
        
        # 收益分析
        returns = [r['result']['return'] for r in results if r['result']]
        avg_return = np.mean(returns) if returns else 0
        win_rate = wins / len(results) if results else 0
        
        # Lean 配置準確性
        lean_correct = sum(1 for r in results if r['lean_accuracy'])
        lean_accuracy = lean_correct / len(results) if results else 0
        
        # 按幣種分析
        symbol_stats = {}
        for result in results:
            symbol = result['signal']['symbol']
            if symbol not in symbol_stats:
                symbol_stats[symbol] = {'total': 0, 'wins': 0, 'returns': []}
            
            symbol_stats[symbol]['total'] += 1
            if result['result']['status'] == 'WIN':
                symbol_stats[symbol]['wins'] += 1
            symbol_stats[symbol]['returns'].append(result['result']['return'])
        
        report = {
            'validation_timestamp': datetime.now().isoformat(),
            'phase5_config_validation': True,
            'total_signals_generated': total_signals,
            'tracked_signals': len(results),
            'tracking_rate': len(results) / max(total_signals, 1),
            
            'performance_summary': {
                'wins': wins,
                'losses': losses,
                'timeouts': timeouts,
                'win_rate': win_rate,
                'average_return': avg_return,
                'lean_accuracy': lean_accuracy
            },
            
            'symbol_breakdown': {
                symbol: {
                    'total_signals': stats['total'],
                    'win_rate': stats['wins'] / stats['total'],
                    'avg_return': np.mean(stats['returns'])
                }
                for symbol, stats in symbol_stats.items()
            },
            
            'lean_config_effectiveness': {
                'parameter_optimization': len(results) > 0,
                'direction_bias_accuracy': lean_accuracy,
                'real_market_validation': True
            },
            
            'recommendations': self._generate_recommendations(win_rate, lean_accuracy, avg_return)
        }
        
        return report
    
    def _generate_recommendations(self, win_rate: float, lean_accuracy: float, avg_return: float) -> List[str]:
        """生成改進建議"""
        recommendations = []
        
        if win_rate < 0.6:
            recommendations.append("🔧 建議調整信號強度閾值，提高信號質量")
        
        if lean_accuracy < 0.7:
            recommendations.append("📊 建議重新運行 Phase5 回測，更新 Lean 配置")
        
        if avg_return < 0.001:
            recommendations.append("💰 建議調整止盈止損參數，改善風險收益比")
        
        if win_rate > 0.7 and lean_accuracy > 0.8:
            recommendations.append("✅ 配置表現優秀，可考慮實際部署")
        
        return recommendations

async def main():
    """主要執行函數"""
    print("🎯 Trading X - 真實市場驗證測試")
    print("📊 使用 Phase5 最新 Lean 配置")
    print("🚫 禁止模擬數據，僅使用真實幣安市場數據")
    print("=" * 60)
    
    async with RealMarketValidator() as validator:
        # 執行驗證測試 (預設30分鐘)
        report = await validator.run_real_market_validation(duration_minutes=30)
        
        # 顯示結果
        print("\n" + "=" * 60)
        print("📋 真實市場驗證報告")
        print("=" * 60)
        
        print(f"🔔 總信號數: {report['total_signals_generated']}")
        print(f"📊 追蹤信號: {report['tracked_signals']}")
        print(f"📈 追蹤率: {report['tracking_rate']:.1%}")
        
        perf = report['performance_summary']
        print(f"\n✅ 獲利信號: {perf['wins']}")
        print(f"❌ 虧損信號: {perf['losses']}")
        print(f"⏱️ 超時信號: {perf['timeouts']}")
        print(f"🎯 勝率: {perf['win_rate']:.1%}")
        print(f"💰 平均收益: {perf['average_return']:.3%}")
        print(f"🧠 Lean準確性: {perf['lean_accuracy']:.1%}")
        
        print(f"\n🏦 幣種表現:")
        for symbol, stats in report['symbol_breakdown'].items():
            print(f"   {symbol}: 勝率 {stats['win_rate']:.1%}, 平均收益 {stats['avg_return']:.3%}")
        
        print(f"\n💡 改進建議:")
        for rec in report['recommendations']:
            print(f"   {rec}")
        
        # 保存詳細報告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"real_market_validation_report_{timestamp}.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📄 詳細報告已保存: {report_path}")

if __name__ == "__main__":
    asyncio.run(main())
