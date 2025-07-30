#!/usr/bin/env python3
"""
pandas-ta 指標整合測試腳本
測試即時信號引擎中的 pandas-ta 指標計算和分析功能
"""

import asyncio
import requests
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

class PandasTAIntegrationTester:
    """pandas-ta 整合測試器"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.test_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
        
    async def test_technical_indicators(self):
        """測試技術指標計算"""
        logger.info("🧪 測試技術指標計算...")
        
        try:
            # 確保信號引擎正在運行
            status = self._make_request("GET", "/api/v1/realtime-signals/status")
            if not status.get("data", {}).get("running"):
                logger.info("啟動信號引擎...")
                self._make_request("POST", "/api/v1/realtime-signals/start")
                await asyncio.sleep(5)
            
            # 等待一些數據收集
            logger.info("等待市場數據收集...")
            await asyncio.sleep(15)
            
            # 測試每個交易對的指標
            for symbol in self.test_symbols:
                logger.info(f"測試 {symbol} 的技術指標...")
                await self._test_symbol_indicators(symbol)
                
            return True
            
        except Exception as e:
            logger.error(f"❌ 技術指標測試失敗: {e}")
            return False
    
    async def _test_symbol_indicators(self, symbol: str):
        """測試特定交易對的指標"""
        try:
            # 觸發測試信號生成，這會計算所有指標
            test_result = self._make_request("POST", "/api/v1/realtime-signals/signals/test", {
                "symbol": symbol,
                "include_analysis": True
            })
            
            if test_result.get("success"):
                signal_data = test_result.get("data", {})
                indicators = signal_data.get("technical_indicators", {})
                
                logger.info(f"  {symbol} 指標結果:")
                
                # 檢查 RSI
                rsi = indicators.get("rsi")
                if rsi is not None:
                    logger.info(f"    RSI: {rsi:.2f}")
                    if 0 <= rsi <= 100:
                        logger.info("    ✅ RSI 範圍正常")
                    else:
                        logger.warning(f"    ⚠️ RSI 範圍異常: {rsi}")
                
                # 檢查 MACD
                macd_data = indicators.get("macd", {})
                if macd_data:
                    macd = macd_data.get("macd")
                    signal = macd_data.get("signal")
                    histogram = macd_data.get("histogram")
                    logger.info(f"    MACD: {macd:.6f}, Signal: {signal:.6f}, Histogram: {histogram:.6f}")
                    logger.info("    ✅ MACD 計算完成")
                
                # 檢查 Bollinger Bands
                bb_data = indicators.get("bollinger_bands", {})
                if bb_data:
                    upper = bb_data.get("upper")
                    middle = bb_data.get("middle")
                    lower = bb_data.get("lower")
                    logger.info(f"    BB Upper: {upper:.2f}, Middle: {middle:.2f}, Lower: {lower:.2f}")
                    
                    if upper > middle > lower:
                        logger.info("    ✅ Bollinger Bands 順序正確")
                    else:
                        logger.warning("    ⚠️ Bollinger Bands 順序異常")
                
                # 檢查移動平均線
                sma_20 = indicators.get("sma_20")
                ema_20 = indicators.get("ema_20")
                if sma_20 and ema_20:
                    logger.info(f"    SMA(20): {sma_20:.2f}, EMA(20): {ema_20:.2f}")
                    logger.info("    ✅ 移動平均線計算完成")
                
                # 檢查成交量指標
                volume_sma = indicators.get("volume_sma")
                if volume_sma:
                    logger.info(f"    Volume SMA: {volume_sma:.2f}")
                    logger.info("    ✅ 成交量指標計算完成")
                
                # 檢查隨機指標
                stoch_data = indicators.get("stochastic", {})
                if stoch_data:
                    k = stoch_data.get("k")
                    d = stoch_data.get("d")
                    logger.info(f"    Stoch K: {k:.2f}, D: {d:.2f}")
                    if 0 <= k <= 100 and 0 <= d <= 100:
                        logger.info("    ✅ 隨機指標範圍正常")
                
                return True
                
            else:
                logger.error(f"    ❌ {symbol} 指標計算失敗")
                return False
                
        except Exception as e:
            logger.error(f"    ❌ {symbol} 指標測試異常: {e}")
            return False
    
    async def test_signal_generation_logic(self):
        """測試信號生成邏輯"""
        logger.info("🧪 測試信號生成邏輯...")
        
        try:
            # 生成測試信號並分析邏輯
            for symbol in self.test_symbols:
                logger.info(f"測試 {symbol} 信號生成邏輯...")
                
                test_result = self._make_request("POST", "/api/v1/realtime-signals/signals/test", {
                    "symbol": symbol,
                    "include_reasoning": True
                })
                
                if test_result.get("success"):
                    signal_data = test_result.get("data", {})
                    signal_type = signal_data.get("signal_type", "UNKNOWN")
                    confidence = signal_data.get("confidence", 0.0)
                    reasoning = signal_data.get("reasoning", [])
                    
                    logger.info(f"  {symbol} 信號結果:")
                    logger.info(f"    信號類型: {signal_type}")
                    logger.info(f"    信心度: {confidence:.2f}")
                    logger.info(f"    分析依據數量: {len(reasoning) if reasoning else 0}")
                    
                    # 檢查推理邏輯
                    if reasoning:
                        logger.info("    分析依據:")
                        for reason in reasoning[:3]:  # 顯示前3個
                            logger.info(f"      - {reason}")
                        
                        # 驗證信心度與依據的一致性
                        if signal_type in ["buy", "sell"] and confidence >= 0.6:
                            logger.info("    ✅ 強信號邏輯合理")
                        elif signal_type == "hold" and confidence < 0.6:
                            logger.info("    ✅ 觀望信號邏輯合理")
                        else:
                            logger.info(f"    ✅ 信號邏輯: {signal_type} (信心度: {confidence:.2f})")
                    
                    # 檢查風險管理
                    entry_price = signal_data.get("entry_price")
                    stop_loss = signal_data.get("stop_loss")
                    take_profit = signal_data.get("take_profit")
                    
                    if entry_price and stop_loss and take_profit:
                        if signal_type == "buy":
                            risk_reward = (take_profit - entry_price) / (entry_price - stop_loss)
                        elif signal_type == "sell":
                            risk_reward = (entry_price - take_profit) / (stop_loss - entry_price)
                        else:
                            risk_reward = None
                        
                        if risk_reward and risk_reward > 0:
                            logger.info(f"    風險報酬比: {risk_reward:.2f}")
                            if risk_reward >= 1.5:
                                logger.info("    ✅ 風險報酬比良好")
                            else:
                                logger.info("    ⚠️ 風險報酬比偏低")
                        
                else:
                    logger.error(f"  ❌ {symbol} 信號生成失敗")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 信號生成邏輯測試失敗: {e}")
            return False
    
    async def test_multi_timeframe_analysis(self):
        """測試多時間框架分析"""
        logger.info("🧪 測試多時間框架分析...")
        
        try:
            # 檢查是否支援多時間框架
            for symbol in ["BTCUSDT", "ETHUSDT"]:
                logger.info(f"測試 {symbol} 多時間框架分析...")
                
                # 請求包含多時間框架的分析
                test_result = self._make_request("POST", "/api/v1/realtime-signals/signals/test", {
                    "symbol": symbol,
                    "timeframes": ["1m", "5m", "15m", "1h"],
                    "include_analysis": True
                })
                
                if test_result.get("success"):
                    signal_data = test_result.get("data", {})
                    timeframe_analysis = signal_data.get("timeframe_analysis", {})
                    
                    if timeframe_analysis:
                        logger.info(f"  {symbol} 多時間框架分析:")
                        for tf, analysis in timeframe_analysis.items():
                            trend = analysis.get("trend", "unknown")
                            strength = analysis.get("strength", 0)
                            logger.info(f"    {tf}: 趨勢 {trend}, 強度 {strength:.2f}")
                        
                        logger.info("    ✅ 多時間框架分析完成")
                    else:
                        logger.info("    ℹ️ 使用單一時間框架分析")
                else:
                    logger.error(f"  ❌ {symbol} 多時間框架分析失敗")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 多時間框架分析測試失敗: {e}")
            return False
    
    async def test_performance_metrics(self):
        """測試性能指標"""
        logger.info("🧪 測試性能指標...")
        
        try:
            # 記錄開始時間
            start_time = datetime.now()
            
            # 連續生成多個信號測試性能
            test_count = 10
            successful_tests = 0
            total_time = 0
            
            for i in range(test_count):
                symbol = self.test_symbols[i % len(self.test_symbols)]
                
                test_start = datetime.now()
                test_result = self._make_request("POST", "/api/v1/realtime-signals/signals/test", {
                    "symbol": symbol
                })
                test_end = datetime.now()
                
                if test_result.get("success"):
                    successful_tests += 1
                    test_duration = (test_end - test_start).total_seconds()
                    total_time += test_duration
                    
                    if i == 0:  # 第一次測試顯示詳細信息
                        logger.info(f"  測試 {symbol}: {test_duration:.3f}秒")
                
                # 短暫延遲
                await asyncio.sleep(0.5)
            
            # 計算統計
            success_rate = (successful_tests / test_count) * 100
            avg_time = total_time / successful_tests if successful_tests > 0 else 0
            
            logger.info(f"  性能統計:")
            logger.info(f"    測試次數: {test_count}")
            logger.info(f"    成功率: {success_rate:.1f}%")
            logger.info(f"    平均響應時間: {avg_time:.3f}秒")
            
            if success_rate >= 90 and avg_time <= 5.0:
                logger.info("  ✅ 性能指標良好")
                return True
            elif success_rate >= 80:
                logger.info("  ⚠️ 性能指標可接受")
                return True
            else:
                logger.warning("  ❌ 性能指標需要改善")
                return False
                
        except Exception as e:
            logger.error(f"❌ 性能測試失敗: {e}")
            return False
    
    def _make_request(self, method: str, endpoint: str, data: dict = None):
        """發送 HTTP 請求"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=30)
            else:
                raise ValueError(f"不支援的方法: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP 請求失敗 {method} {endpoint}: {e}")
            return {"success": False, "error": str(e)}

async def main():
    """主測試函數"""
    logger.info("🚀 開始 pandas-ta 整合測試...")
    
    tester = PandasTAIntegrationTester()
    test_results = []
    
    # 測試項目
    tests = [
        ("技術指標計算", tester.test_technical_indicators),
        ("信號生成邏輯", tester.test_signal_generation_logic),
        ("多時間框架分析", tester.test_multi_timeframe_analysis),
        ("性能指標", tester.test_performance_metrics),
    ]
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 執行測試: {test_name}")
        try:
            result = await test_func()
            test_results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name} - 通過")
            else:
                logger.error(f"❌ {test_name} - 失敗")
                
            # 測試間隔
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"❌ {test_name} - 異常: {e}")
            test_results.append((test_name, False))
    
    # 測試總結
    logger.info("\n📊 測試結果總結:")
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通過" if result else "❌ 失敗"
        logger.info(f"  {test_name}: {status}")
    
    logger.info(f"\n🎯 總計: {passed}/{total} 項測試通過")
    
    if passed == total:
        logger.info("🎉 所有測試通過！pandas-ta 整合工作正常")
        return True
    else:
        logger.warning("⚠️ 部分測試失敗，請檢查 pandas-ta 整合")
        return False

if __name__ == "__main__":
    # 運行測試
    success = asyncio.run(main())
    exit(0 if success else 1)
