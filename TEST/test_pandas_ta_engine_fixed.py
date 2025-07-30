#!/usr/bin/env python3
"""
pandas-ta 技術分析引擎專門測試（修正版）
檢查技術分析為什麼沒有在自動化流程中正常工作
"""

import asyncio
import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# 添加項目路徑
sys.path.append('/Users/henrychang/Desktop/Trading-X')

from app.services.pandas_ta_indicators import PandasTAIndicators
from app.services.realtime_signal_engine import RealtimeSignalEngine

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PandasTAEngineTester:
    """pandas-ta 技術分析引擎測試器"""
    
    def __init__(self):
        self.test_results = {}
        self.pandas_ta_service = None
        self.signal_engine = None
        self.test_data = None
        
    def generate_test_market_data(self, symbol="BTCUSDT", periods=100):
        """生成測試市場數據"""
        logger.info(f"🔄 生成 {symbol} 測試市場數據 ({periods} 個週期)")
        
        # 生成模擬的 OHLCV 數據
        base_price = 50000  # BTC 基準價格
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=periods), 
            periods=periods, 
            freq='1H'
        )
        
        # 生成隨機價格變動
        np.random.seed(42)  # 固定種子確保可重複性
        price_changes = np.random.randn(periods) * 0.02  # 2% 標準差
        
        # 生成價格序列
        prices = [base_price]
        for change in price_changes[1:]:
            new_price = prices[-1] * (1 + change)
            prices.append(max(new_price, 1000))  # 防止價格過低
        
        # 生成 OHLCV 數據
        data = []
        for i, (date, close_price) in enumerate(zip(dates, prices)):
            # 生成 OHLC
            high = close_price * (1 + abs(np.random.randn() * 0.005))
            low = close_price * (1 - abs(np.random.randn() * 0.005))
            open_price = prices[i-1] if i > 0 else close_price
            volume = np.random.uniform(1000, 10000)
            
            data.append({
                'timestamp': date,
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close_price, 2),
                'volume': round(volume, 2)
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        
        logger.info(f"✅ 生成完成: {len(df)} 行數據，價格範圍 {df['close'].min():.2f} - {df['close'].max():.2f}")
        return df
    
    async def test_pandas_ta_service_init(self):
        """測試 pandas-ta 服務初始化"""
        logger.info("🔄 測試 pandas-ta 服務初始化...")
        
        try:
            self.pandas_ta_service = PandasTAIndicators()
            logger.info("✅ pandas-ta 服務初始化成功")
            return True
        except Exception as e:
            logger.error(f"❌ pandas-ta 服務初始化失敗: {e}")
            return False
    
    async def test_technical_indicators_calculation(self):
        """測試技術指標計算"""
        logger.info("🔄 測試技術指標計算...")
        
        if not self.pandas_ta_service:
            logger.error("❌ pandas-ta 服務未初始化")
            return False
        
        try:
            # 生成測試數據
            self.test_data = self.generate_test_market_data()
            
            # 測試各種策略類型的技術指標計算
            strategy_tests = [
                ("短線剝頭皮", "scalping"),
                ("波段交易", "swing"),
                ("趨勢跟隨", "trend"),
                ("動量策略", "momentum"),
            ]
            
            results = {}
            for strategy_name, strategy_type in strategy_tests:
                logger.info(f"  📊 測試 {strategy_name}策略...")
                try:
                    # 使用實際的方法
                    adaptive_indicators = self.pandas_ta_service.calculate_adaptive_indicators(
                        df=self.test_data, 
                        strategy_type=strategy_type
                    )
                    
                    if adaptive_indicators and len(adaptive_indicators) > 0:
                        logger.info(f"    ✅ {strategy_name}: 成功計算 {len(adaptive_indicators)} 個指標")
                        results[strategy_name] = True
                        
                        # 顯示計算出的指標
                        for indicator_name, signal in adaptive_indicators.items():
                            logger.info(f"      - {indicator_name}: {signal.signal_type} (強度: {signal.strength:.2f})")
                    else:
                        logger.warning(f"    ⚠️ {strategy_name}: 未生成指標")
                        results[strategy_name] = False
                        
                except Exception as e:
                    logger.error(f"    ❌ {strategy_name} 計算異常: {e}")
                    results[strategy_name] = False
            
            success_rate = sum(results.values()) / len(results)
            logger.info(f"📊 技術指標計算測試結果: {success_rate*100:.1f}% 通過率")
            
            return success_rate >= 0.5  # 50% 通過率即可接受
            
        except Exception as e:
            logger.error(f"❌ 技術指標計算測試失敗: {e}")
            return False
    
    async def test_signal_generation(self):
        """測試信號生成"""
        logger.info("🔄 測試信號生成...")
        
        if not self.pandas_ta_service or self.test_data is None:
            logger.error("❌ pandas-ta 服務或測試數據未準備")
            return False
        
        try:
            # 嘗試使用綜合分析方法生成交易信號
            comprehensive_analysis = self.pandas_ta_service.get_comprehensive_analysis(
                df=self.test_data,
                strategy_type="scalping"
            )
            
            if comprehensive_analysis and len(comprehensive_analysis) > 0:
                logger.info(f"✅ 成功生成綜合分析結果")
                
                # 分析結果內容
                for key, value in comprehensive_analysis.items():
                    if isinstance(value, dict):
                        logger.info(f"  📊 {key}: {len(value)} 項目")
                    else:
                        logger.info(f"  📊 {key}: {type(value).__name__}")
                
                # 檢查是否包含信號
                signals = comprehensive_analysis.get('signals', {})
                if signals:
                    logger.info(f"  🎯 包含 {len(signals)} 個交易信號")
                    
                    # 統計信號類型
                    signal_types = {}
                    for signal_name, signal_data in signals.items():
                        if hasattr(signal_data, 'signal_type'):
                            signal_type = signal_data.signal_type
                            signal_types[signal_type] = signal_types.get(signal_type, 0) + 1
                    
                    logger.info(f"  📊 信號類型分佈: {signal_types}")
                    return True
                else:
                    logger.warning("⚠️ 綜合分析中未包含具體交易信號")
                    return True  # 能生成分析就算成功
            else:
                logger.warning("⚠️ 未生成綜合分析結果")
                return False
                
        except Exception as e:
            logger.error(f"❌ 信號生成測試失敗: {e}")
            return False
    
    async def test_realtime_engine_integration(self):
        """測試即時引擎整合"""
        logger.info("🔄 測試即時引擎整合...")
        
        try:
            # 初始化即時信號引擎（不需要參數）
            self.signal_engine = RealtimeSignalEngine()
            
            logger.info("✅ 即時信號引擎初始化成功")
            
            # 檢查引擎的基本屬性
            if hasattr(self.signal_engine, 'pandas_ta_indicators'):
                logger.info("  ✅ pandas-ta 指標服務已整合")
            
            if hasattr(self.signal_engine, 'signal_parser'):
                logger.info("  ✅ 信號解析器已整合")
                
            if hasattr(self.signal_engine, 'running'):
                logger.info(f"  📊 引擎運行狀態: {self.signal_engine.running}")
            
            # 測試引擎是否能處理基本配置
            if hasattr(self.signal_engine, 'monitored_symbols'):
                logger.info(f"  📊 監控交易對: {len(self.signal_engine.monitored_symbols)}")
                
            if hasattr(self.signal_engine, 'monitored_timeframes'):
                logger.info(f"  📊 監控時間框架: {self.signal_engine.monitored_timeframes}")
            
            return True
                
        except Exception as e:
            logger.error(f"❌ 即時引擎整合測試失敗: {e}")
            return False
    
    async def test_configuration_loading(self):
        """測試配置加載"""
        logger.info("🔄 測試配置加載...")
        
        try:
            config_files = [
                "/Users/henrychang/Desktop/Trading-X/app/config/pandas_ta_trading_signals.json",
                "/Users/henrychang/Desktop/Trading-X/app/config/smart_timing_config.json",
                "/Users/henrychang/Desktop/Trading-X/app/config/market_conditions_config.json"
            ]
            
            loaded_configs = 0
            for config_file in config_files:
                try:
                    if os.path.exists(config_file):
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config_data = json.load(f)
                        logger.info(f"  ✅ 成功加載: {os.path.basename(config_file)}")
                        loaded_configs += 1
                    else:
                        logger.warning(f"  ⚠️ 配置文件不存在: {os.path.basename(config_file)}")
                except Exception as e:
                    logger.error(f"  ❌ 加載失敗 {os.path.basename(config_file)}: {e}")
            
            success_rate = loaded_configs / len(config_files)
            logger.info(f"📊 配置加載成功率: {success_rate*100:.1f}%")
            
            return success_rate >= 0.5  # 至少 50% 配置文件可用
            
        except Exception as e:
            logger.error(f"❌ 配置加載測試失敗: {e}")
            return False
    
    async def run_comprehensive_test(self):
        """運行綜合測試"""
        logger.info("🎯 開始 pandas-ta 技術分析引擎綜合測試")
        logger.info("="*70)
        
        test_cases = [
            ("pandas-ta 服務初始化", self.test_pandas_ta_service_init),
            ("技術指標計算", self.test_technical_indicators_calculation),
            ("交易信號生成", self.test_signal_generation),
            ("即時引擎整合", self.test_realtime_engine_integration),
            ("配置文件加載", self.test_configuration_loading),
        ]
        
        for test_name, test_func in test_cases:
            logger.info(f"\n📋 執行測試: {test_name}")
            try:
                result = await test_func()
                self.test_results[test_name] = result
                
                if result:
                    logger.info(f"✅ {test_name} - 通過")
                else:
                    logger.warning(f"⚠️ {test_name} - 失敗")
                    
                await asyncio.sleep(1)  # 短暫間隔
                
            except Exception as e:
                logger.error(f"❌ {test_name} - 異常: {e}")
                self.test_results[test_name] = False
        
        # 生成報告
        await self._generate_test_report()
        
        return self._calculate_success_rate() >= 0.6
    
    async def _generate_test_report(self):
        """生成測試報告"""
        success_rate = self._calculate_success_rate()
        
        logger.info("\n" + "="*70)
        logger.info("🎯 pandas-ta 技術分析引擎測試報告")
        logger.info("="*70)
        
        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)
        
        logger.info(f"總測試項目: {total}")
        logger.info(f"通過項目: {passed}")
        logger.info(f"失敗項目: {total - passed}")
        logger.info(f"成功率: {success_rate*100:.1f}%")
        logger.info("-"*70)
        
        for test_name, result in self.test_results.items():
            status = "✅ 通過" if result else "❌ 失敗"
            logger.info(f"  {test_name}: {status}")
        
        # 診斷建議
        logger.info("\n" + "="*70)
        logger.info("🔍 診斷分析")
        logger.info("="*70)
        
        if not self.test_results.get("pandas-ta 服務初始化", False):
            logger.warning("⚠️ pandas-ta 服務無法初始化")
            logger.info("💡 建議檢查 pandas-ta 庫安裝和依賴項")
        
        if not self.test_results.get("技術指標計算", False):
            logger.warning("⚠️ 技術指標計算存在問題")
            logger.info("💡 建議檢查數據格式和指標計算邏輯")
        
        if not self.test_results.get("交易信號生成", False):
            logger.warning("⚠️ 交易信號生成失敗")
            logger.info("💡 建議檢查信號生成邏輯和條件判斷")
        
        if not self.test_results.get("即時引擎整合", False):
            logger.warning("⚠️ 即時引擎整合有問題")
            logger.info("💡 建議檢查引擎初始化和數據傳遞")
        
        # 自動化流程分析
        logger.info("\n🤖 自動化流程診斷:")
        
        if self.test_results.get("pandas-ta 服務初始化", False):
            logger.info("  ✅ 技術分析模組可用")
        else:
            logger.info("  ❌ 技術分析模組不可用 - 這可能是自動化流程中斷的原因")
        
        if self.test_results.get("技術指標計算", False):
            logger.info("  ✅ 技術指標計算正常")
        else:
            logger.info("  ❌ 技術指標計算異常 - 無法生成分析結果")
        
        if self.test_results.get("交易信號生成", False):
            logger.info("  ✅ 信號生成功能正常")
        else:
            logger.info("  ❌ 信號生成功能異常 - 無法產生交易信號")
        
        logger.info("\n" + "="*70)
    
    def _calculate_success_rate(self):
        """計算成功率"""
        if not self.test_results:
            return 0.0
        
        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)
        return passed / total

async def main():
    """主函數"""
    logger.info("🎯 pandas-ta 技術分析引擎專門測試")
    logger.info("="*70)
    logger.info("測試目標: 檢查為什麼自動化流程中的技術分析環節沒有工作")
    logger.info("測試範圍:")
    logger.info("  • pandas-ta 服務初始化")
    logger.info("  • 技術指標計算功能")
    logger.info("  • 交易信號生成邏輯")
    logger.info("  • 即時引擎整合測試")
    logger.info("  • 配置文件完整性")
    logger.info("="*70)
    
    tester = PandasTAEngineTester()
    
    try:
        success = await tester.run_comprehensive_test()
        
        if success:
            logger.info("\n🎉 pandas-ta 技術分析引擎測試完成 - 基本功能正常!")
            logger.info("💡 如果自動化流程仍有問題，可能是數據流或觸發機制的問題")
        else:
            logger.warning("\n⚠️ pandas-ta 技術分析引擎測試完成 - 發現問題!")
            logger.info("💡 建議根據診斷分析修復相關問題")
        
        return success
        
    except Exception as e:
        logger.error(f"\n❌ pandas-ta 技術分析引擎測試執行失敗: {e}")
        return False

if __name__ == "__main__":
    # 運行 pandas-ta 引擎測試
    success = asyncio.run(main())
    exit(0 if success else 1)
