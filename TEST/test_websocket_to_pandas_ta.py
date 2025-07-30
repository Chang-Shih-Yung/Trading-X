#!/usr/bin/env python3
"""
WebSocket → pandas-ta 分析流程驗證測試
測試從WebSocket抓取即時幣價到pandas-ta處理分析的完整流程
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
import json

# 添加項目根目錄到路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.binance_websocket import BinanceWebSocketClient, TickerData, KlineData
from app.services.market_data import MarketDataService
from app.services.pandas_ta_indicators import PandasTAIndicators
from app.services.pandas_ta_trading_signal_parser import PandasTATradingSignals
from app.services.realtime_signal_engine import RealtimeSignalEngine, MarketDataUpdate

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebSocketToTAValidator:
    """WebSocket到TA分析流程驗證器"""
    
    def __init__(self):
        self.websocket_client = BinanceWebSocketClient()
        self.market_service = MarketDataService()
        self.ta_indicators = PandasTAIndicators()
        self.signal_parser = PandasTATradingSignals()
        self.realtime_engine = RealtimeSignalEngine()
        
        # 接收數據統計
        self.ticker_count = 0
        self.kline_count = 0
        self.analysis_count = 0
        self.signal_count = 0
        
        # 測試幣種
        self.test_symbols = ["BTCUSDT", "ETHUSDT"]
        
    async def ticker_callback(self, ticker_data: TickerData):
        """處理即時價格數據"""
        self.ticker_count += 1
        logger.info(f"📊 Ticker #{self.ticker_count}: {ticker_data.symbol} = ${ticker_data.price:.2f} ({ticker_data.price_change_percent:+.2f}%)")
        
        # 模擬將價格數據傳送給實時引擎
        update = MarketDataUpdate(
            symbol=ticker_data.symbol,
            price=ticker_data.price,
            volume=ticker_data.volume_24h,
            timestamp=ticker_data.timestamp,
            data_type='ticker'
        )
        
        # 觸發pandas-ta分析
        await self.trigger_pandas_ta_analysis(ticker_data.symbol)
        
    async def kline_callback(self, kline_data: KlineData):
        """處理K線數據"""
        self.kline_count += 1
        logger.info(f"📈 K-Line #{self.kline_count}: {kline_data.symbol} [{kline_data.interval}] 收盤價: ${kline_data.close_price:.2f}")
        
        # 觸發pandas-ta分析
        await self.trigger_pandas_ta_analysis(kline_data.symbol)
        
    async def trigger_pandas_ta_analysis(self, symbol: str):
        """觸發pandas-ta技術分析"""
        try:
            self.analysis_count += 1
            
            # 獲取歷史數據進行分析
            df = await self.market_service.get_historical_data(
                symbol=symbol,
                timeframe="5m",
                limit=100,
                exchange='binance'
            )
            
            if df is None or len(df) < 50:
                logger.warning(f"⚠️ {symbol} 數據不足，跳過分析")
                return
                
            # 計算技術指標
            indicators = self.ta_indicators.calculate_all_indicators(df)
            
            # 解析交易信號
            analysis_result = self.signal_parser.analyze_signals(df, strategy="realtime")
            
            if analysis_result and analysis_result.get('signals'):
                self.signal_count += 1
                best_signal = max(analysis_result['signals'], key=lambda x: x.get('confidence', 0))
                
                logger.info(f"✅ 分析 #{self.analysis_count}: {symbol} -> {best_signal.get('signal_type', 'NEUTRAL')} (信心度: {best_signal.get('confidence', 0):.2%})")
                
                # 如果信號夠強，顯示詳細信息
                if best_signal.get('confidence', 0) > 0.3:
                    logger.info(f"🎯 強信號 #{self.signal_count}: {symbol}")
                    logger.info(f"   信號類型: {best_signal.get('signal_type', 'UNKNOWN')}")
                    logger.info(f"   信心度: {best_signal.get('confidence', 0):.2%}")
                    logger.info(f"   指標: {best_signal.get('indicator', 'Unknown')}")
                    logger.info(f"   原因: {best_signal.get('reason', '無詳細說明')}")
            else:
                logger.info(f"⚠️ 分析 #{self.analysis_count}: {symbol} -> 無有效信號")
                
        except Exception as e:
            logger.error(f"❌ pandas-ta 分析失敗 {symbol}: {e}")
    
    async def start_validation(self, duration_minutes: int = 5):
        """開始驗證流程"""
        logger.info("🚀 開始 WebSocket → pandas-ta 流程驗證")
        logger.info(f"📊 測試幣種: {self.test_symbols}")
        logger.info(f"⏱️ 測試時長: {duration_minutes} 分鐘")
        logger.info("=" * 60)
        
        # 註冊回調函數
        self.websocket_client.add_ticker_callback(self.ticker_callback)
        self.websocket_client.add_kline_callback(self.kline_callback)
        
        # 啟動WebSocket
        await self.websocket_client.start()
        
        # 訂閱即時價格
        await self.websocket_client.subscribe_ticker(self.test_symbols)
        logger.info("✅ 已訂閱即時價格數據")
        
        # 訂閱K線數據
        await self.websocket_client.subscribe_klines(self.test_symbols, ["1m", "5m"])
        logger.info("✅ 已訂閱K線數據")
        
        # 運行指定時間
        start_time = datetime.now()
        while (datetime.now() - start_time).total_seconds() < duration_minutes * 60:
            await asyncio.sleep(10)
            
            # 每10秒顯示統計
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"📊 統計 ({elapsed:.0f}s): Ticker: {self.ticker_count}, K-Line: {self.kline_count}, 分析: {self.analysis_count}, 信號: {self.signal_count}")
        
        # 停止WebSocket
        await self.websocket_client.stop()
        
        # 最終統計
        logger.info("=" * 60)
        logger.info("📋 最終統計報告:")
        logger.info(f"   ✅ 接收到Ticker數據: {self.ticker_count} 筆")
        logger.info(f"   ✅ 接收到K線數據: {self.kline_count} 筆")
        logger.info(f"   ✅ 執行pandas-ta分析: {self.analysis_count} 次")
        logger.info(f"   ✅ 生成交易信號: {self.signal_count} 個")
        
        # 效能分析
        if self.ticker_count > 0:
            analysis_rate = (self.analysis_count / self.ticker_count) * 100
            signal_rate = (self.signal_count / self.analysis_count) * 100 if self.analysis_count > 0 else 0
            
            logger.info(f"   📊 分析觸發率: {analysis_rate:.1f}% (每個ticker觸發分析的比例)")
            logger.info(f"   📊 信號生成率: {signal_rate:.1f}% (分析產生有效信號的比例)")
        
        # 流程驗證結果
        logger.info("=" * 60)
        if self.ticker_count > 0 and self.analysis_count > 0:
            logger.info("✅ WebSocket → pandas-ta 流程驗證成功！")
            logger.info("   ✅ WebSocket 正常接收即時數據")
            logger.info("   ✅ pandas-ta 正常執行技術分析")
            if self.signal_count > 0:
                logger.info("   ✅ 成功生成交易信號")
            else:
                logger.info("   ⚠️ 未生成交易信號 (可能市場條件不符合)")
        else:
            logger.error("❌ WebSocket → pandas-ta 流程驗證失敗！")
            if self.ticker_count == 0:
                logger.error("   ❌ WebSocket 未接收到即時數據")
            if self.analysis_count == 0:
                logger.error("   ❌ pandas-ta 未執行分析")

async def main():
    """主程序"""
    validator = WebSocketToTAValidator()
    
    try:
        # 運行5分鐘的驗證測試
        await validator.start_validation(duration_minutes=5)
        
    except KeyboardInterrupt:
        logger.info("⚠️ 用戶中斷測試")
    except Exception as e:
        logger.error(f"❌ 測試過程中發生錯誤: {e}")
    finally:
        logger.info("🏁 測試結束")

if __name__ == "__main__":
    asyncio.run(main())
