"""
即時信號引擎
監聽 WebSocket 數據更新，自動觸發 pandas-ta 分析並廣播結果
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np

from app.services.market_data import MarketDataService
from app.services.pandas_ta_indicators import PandasTAIndicators
from app.services.pandas_ta_trading_signal_parser import PandasTATradingSignals
from app.services.realtime_technical_analysis import RealTimeTechnicalAnalysis
from app.services.candlestick_patterns import analyze_candlestick_patterns
from app.services.gmail_notification import GmailNotificationService
from app.utils.time_utils import get_taiwan_now_naive

logger = logging.getLogger(__name__)

@dataclass
class TradingSignalAlert:
    """交易信號警報"""
    symbol: str
    signal_type: str  # BUY, SELL, STRONG_BUY, STRONG_SELL
    confidence: float  # 0.0 - 1.0
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float
    indicators_used: List[str]
    reasoning: str
    timeframe: str
    timestamp: datetime
    urgency: str  # low, medium, high, critical
    
@dataclass
class MarketDataUpdate:
    """市場數據更新"""
    symbol: str
    price: float
    volume: float
    timestamp: datetime
    data_type: str  # ticker, kline, depth

class RealtimeSignalEngine:
    """即時信號引擎 - 自動化交易信號生成與廣播"""
    
    def __init__(self):
        self.market_service: Optional[MarketDataService] = None
        self.pandas_ta_indicators = PandasTAIndicators()
        self.signal_parser = PandasTATradingSignals()
        self.technical_analysis: Optional[RealTimeTechnicalAnalysis] = None
        
        # 配置參數
        self.min_history_points = 200  # 最少歷史數據點
        self.signal_cooldown = 300  # 信號冷卻時間(秒)
        self.confidence_threshold = 0.65  # 信號信心度閾值
        
        # 運行狀態
        self.running = False
        self.monitored_symbols = []
        self.tracked_symbols = []  # 當前追蹤的交易對
        self.monitored_timeframes = ['1m', '5m', '15m', '1h']
        
        # 快取和狀態
        self.last_signals = {}  # 最後信號快取
        self.price_buffers = {}  # 價格緩衝區
        self.signal_history = []  # 信號歷史
        self.latest_prices = {}  # 最新價格
        
        # 事件和同步
        self.data_initialized_event = asyncio.Event()
        
        # 回調函數
        self.signal_callbacks: List[Callable] = []
        self.notification_callbacks: List[Callable] = []
        
        # Gmail 通知服務
        self.gmail_service: Optional[GmailNotificationService] = None
        self.gmail_enabled = False
        
    async def initialize(self, market_service: MarketDataService):
        """初始化引擎"""
        try:
            self.market_service = market_service
            self.technical_analysis = RealTimeTechnicalAnalysis(market_service)
            
            # 設置默認監控的交易對
            self.monitored_symbols = [
                'BTCUSDT', 'ETHUSDT', 'ADAUSDT', 
                'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 'DOGEUSDT'
            ]
            
            # 初始化追蹤的交易對（與監控的交易對相同）
            self.tracked_symbols = self.monitored_symbols.copy()
            
            logger.info(f"🚀 實時信號引擎初始化完成")
            logger.info(f"📊 監控交易對: {self.monitored_symbols}")
            logger.info(f"🎯 追蹤交易對: {self.tracked_symbols}")
            logger.info(f"⏰ 監控時間框架: {self.monitored_timeframes}")
            logger.info(f"🎯 信心度閾值: {self.confidence_threshold}")
            logger.info(f"❄️ 信號冷卻時間: {self.signal_cooldown}秒")
            
        except Exception as e:
            logger.error(f"❌ 初始化實時信號引擎失敗: {e}")
            raise
    
    def setup_gmail_notification(self, sender_email: str, sender_password: str, recipient_email: str):
        """設置Gmail通知服務"""
        try:
            self.gmail_service = GmailNotificationService(
                sender_email=sender_email,
                sender_password=sender_password, 
                recipient_email=recipient_email
            )
            self.gmail_enabled = True
            logger.info("📧 Gmail通知服務設置完成")
            
        except Exception as e:
            logger.error(f"❌ 設置Gmail通知服務失敗: {e}")
            self.gmail_enabled = False
    
    async def test_gmail_notification(self) -> bool:
        """測試Gmail通知功能"""
        if not self.gmail_service:
            logger.warning("📧 Gmail服務未設置")
            return False
            
        return await self.gmail_service.test_notification()
    
    async def start(self):
        """啟動即時信號引擎"""
        if self.running:
            logger.warning("即時信號引擎已在運行中")
            return
            
        self.running = True
        logger.info("🚀 啟動即時信號引擎...")
        
        # 啟動各種監控任務
        tasks = [
            asyncio.create_task(self._price_monitor_loop()),
            asyncio.create_task(self._signal_generation_loop()),
            asyncio.create_task(self._data_cleanup_loop()),
            asyncio.create_task(self._health_check_loop())
        ]
        
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"即時信號引擎運行錯誤: {e}")
        finally:
            self.running = False
    
    async def stop(self):
        """停止即時信號引擎"""
        logger.info("⏹️ 正在停止實時信號引擎...")
        self.running = False
        
        # 等待所有任務完成
        if hasattr(self, 'tasks'):
            for task in self.tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        logger.info("✅ 實時信號引擎已停止")
    
    async def handle_market_data_update(self, update):
        """處理市場數據更新 - WebSocket事件處理"""
        try:
            # 記錄WebSocket數據接收
            logger.info(f"📡 WebSocket數據: {update.get('symbol', 'UNKNOWN')} - 價格: {update.get('price', 0):.6f}, 成交量: {update.get('volume', 0):.2f}")
            
            symbol = update.get('symbol')
            price = update.get('price', 0)
            volume = update.get('volume', 0)
            
            if not symbol or price <= 0:
                logger.warning(f"⚠️ 無效的WebSocket數據: {update}")
                return
            
            # 更新價格緩衝區
            await self._update_price_buffer_from_websocket(symbol, price, volume)
            
            # 更新最新價格
            old_price = self.latest_prices.get(symbol, 0)
            self.latest_prices[symbol] = price
            
            # 計算價格變化並記錄
            if old_price > 0:
                price_change = ((price - old_price) / old_price) * 100
                if abs(price_change) > 0.05:  # 變化超過0.05%才記錄
                    logger.info(f"📈 {symbol} 價格變化: {price_change:+.3f}% (WebSocket更新)")
            
            # 檢查是否觸發新信號
            await self._handle_new_signal_trigger_from_websocket(symbol, price)
            
        except Exception as e:
            logger.error(f"❌ 處理WebSocket數據更新失敗: {e}")
        
    def add_signal_callback(self, callback: Callable):
        """添加信號回調函數"""
        self.signal_callbacks.append(callback)
        
    def add_notification_callback(self, callback: Callable):
        """添加通知回調函數"""
        self.notification_callbacks.append(callback)
    
    async def _price_monitor_loop(self):
        """價格監控循環"""
        logger.info("💰 價格監控循環已啟動 - 開始實時價格追蹤")
        
        while self.running:
            try:
                if self.market_service is None:
                    logger.warning("⏳ 價格監控等待中: market_service 尚未初始化")
                    await asyncio.sleep(5)
                    continue
                
                # 獲取實時價格 - 使用批量方法
                prices = await self.market_service.get_realtime_prices(self.tracked_symbols)
                
                if prices:
                    # 批量更新價格
                    updated_count = 0
                    for symbol, price in prices.items():
                        if symbol in self.latest_prices:
                            old_price = self.latest_prices[symbol]
                            price_change = ((price - old_price) / old_price) * 100 if old_price > 0 else 0
                            
                            if abs(price_change) > 0.1:  # 變化超過0.1%才記錄
                                logger.info(f"💱 {symbol}: {old_price:.6f} → {price:.6f} ({price_change:+.2f}%)")
                                updated_count += 1
                        
                        self.latest_prices[symbol] = price
                    
                    if updated_count > 0:
                        logger.info(f"📊 價格更新完成: {updated_count}/{len(prices)} 個交易對有顯著變化")
                else:
                    logger.warning("⚠️ 未獲取到實時價格數據")
                
                await asyncio.sleep(2)  # 每2秒檢查一次
                
            except Exception as e:
                if self.market_service is None:
                    logger.warning("⏳ 價格監控等待中: market_service 尚未初始化")
                    await asyncio.sleep(5)
                    continue
                else:
                    logger.error(f"❌ 價格監控錯誤: {e}")
                    await asyncio.sleep(5)
        """價格監控循環"""
        logger.info("📊 啟動價格監控循環...")
        
        while self.running:
            try:
                # 檢查服務是否已初始化
                if not self.market_service:
                    logger.warning("market_service 未初始化，跳過價格監控")
                    await asyncio.sleep(10)
                    continue
                
                for symbol in self.monitored_symbols:
                    # 獲取最新價格數據
                    price_data = await self.market_service.get_realtime_price(symbol)
                    
                    if price_data:
                        update = MarketDataUpdate(
                            symbol=symbol,
                            price=price_data.get('price', 0),
                            volume=price_data.get('volume_24h', 0),
                            timestamp=datetime.now(),
                            data_type='ticker'
                        )
                        
                        # 更新價格緩衝區
                        await self._update_price_buffer(update)
                
                await asyncio.sleep(5)  # 每5秒檢查一次
                
            except Exception as e:
                logger.error(f"價格監控錯誤: {e}")
                await asyncio.sleep(10)
    
    async def _signal_generation_loop(self):
        """信號生成主循環"""
        await self.data_initialized_event.wait()
        
        logger.info("📊 信號生成循環已啟動 - 開始監控交易信號")
        
        while self.running:
            try:
                # 等待最新價格數據
                if not self.latest_prices:
                    await asyncio.sleep(1)
                    continue
                
                # 獲取需要檢查的交易對
                symbols_to_check = list(self.latest_prices.keys())
                logger.info(f"🔄 正在檢查 {len(symbols_to_check)} 個交易對的信號")
                
                # 批量檢查信號
                signal_count = 0
                for symbol in symbols_to_check:
                    for timeframe in ["1m", "5m", "15m", "1h"]:
                        signal_generated = await self._check_single_symbol_signal(symbol, timeframe)
                        if signal_generated:
                            signal_count += 1
                        await asyncio.sleep(0.1)  # 避免過度頻繁
                
                if signal_count > 0:
                    logger.info(f"✅ 本輪檢查完成，生成 {signal_count} 個交易信號")
                else:
                    logger.info("🔍 本輪檢查完成，暫無新信號")
                
                # 每30秒檢查一次新信號
                await asyncio.sleep(30)
                
            except Exception as e:
                if self.market_service is None:
                    logger.warning("⏳ 信號生成循環等待中: market_service 尚未初始化")
                    await asyncio.sleep(5)
                    continue
                else:
                    logger.error(f"❌ 信號生成錯誤: {e}")
                    await asyncio.sleep(5)
    
    async def _check_single_symbol_signal(self, symbol: str, timeframe: str) -> bool:
        """檢查單個交易對的信號"""
        try:
            if self.market_service is None:
                logger.warning(f"⏳ 市場服務未初始化，跳過 {symbol} {timeframe} 檢查")
                return False
                
            should_generate = await self._should_generate_signal(symbol, timeframe)
            if not should_generate:
                return False
                
            logger.info(f"🎯 開始生成 {symbol} {timeframe} 交易信號")
            signal = await self._generate_comprehensive_signal(symbol, timeframe)
            
            if signal:
                logger.info(f"📈 生成信號: {symbol} {timeframe} - {signal.signal_type} (信心度: {signal.confidence:.2f})")
                await self._save_signal(signal)
                return True
            else:
                logger.debug(f"📊 {symbol} {timeframe} 無有效信號")
                return False
                
        except Exception as e:
            logger.error(f"❌ 檢查 {symbol} {timeframe} 信號時發生錯誤: {e}")
            return False
    
    async def _update_price_buffer(self, update: MarketDataUpdate):
        """更新價格緩衝區"""
        symbol = update.symbol
        
        if symbol not in self.price_buffers:
            self.price_buffers[symbol] = []
        
        # 添加新數據點
        self.price_buffers[symbol].append({
            'timestamp': update.timestamp,
            'price': update.price,
            'volume': update.volume
        })
        
        # 保持緩衝區大小（保留最近1000個數據點）
        if len(self.price_buffers[symbol]) > 1000:
            self.price_buffers[symbol] = self.price_buffers[symbol][-1000:]
    
    async def _update_price_buffer_from_websocket(self, symbol: str, price: float, volume: float):
        """從WebSocket更新價格緩衝區"""
        if symbol not in self.price_buffers:
            self.price_buffers[symbol] = []
        
        # 添加新數據點
        self.price_buffers[symbol].append({
            'timestamp': datetime.now(),
            'price': price,
            'volume': volume,
            'source': 'websocket'
        })
        
        # 保持緩衝區大小
        if len(self.price_buffers[symbol]) > 1000:
            self.price_buffers[symbol] = self.price_buffers[symbol][-1000:]
            
        logger.debug(f"📊 {symbol} 價格緩衝區更新: {len(self.price_buffers[symbol])} 個數據點")
    
    async def _handle_new_signal_trigger_from_websocket(self, symbol: str, price: float):
        """處理WebSocket觸發的新信號檢查"""
        try:
            # 只對監控的交易對進行信號檢查
            if symbol not in self.monitored_symbols:
                return
            
            # 檢查各個時間框架的信號
            for timeframe in self.monitored_timeframes:
                should_check = await self._should_generate_signal(symbol, timeframe)
                if should_check:
                    logger.info(f"🎯 WebSocket觸發信號檢查: {symbol} {timeframe}")
                    
                    # 異步生成信號，避免阻塞WebSocket處理
                    asyncio.create_task(self._generate_and_save_signal(symbol, timeframe))
                    
        except Exception as e:
            logger.error(f"❌ WebSocket信號觸發處理失敗: {e}")
    
    async def _generate_and_save_signal(self, symbol: str, timeframe: str):
        """生成並保存信號（異步任務）"""
        try:
            signal = await self._generate_comprehensive_signal(symbol, timeframe)
            if signal:
                logger.info(f"🚨 WebSocket觸發信號: {symbol} {timeframe} - {signal.signal_type} (信心度: {signal.confidence:.2f})")
                await self._save_signal(signal)
        except Exception as e:
            logger.error(f"❌ 生成WebSocket信號失敗: {e}")
    
    async def _save_signal(self, signal):
        """保存交易信號"""
        try:
            logger.info(f"💾 保存交易信號: {signal.symbol} {signal.timeframe} - {signal.signal_type}")
            logger.info(f"📊 信號詳情: 信心度={signal.confidence:.3f}, 緊急度={signal.urgency}")
            logger.info(f"💰 價格資訊: 入場={signal.entry_price:.6f}, 止損={signal.stop_loss:.6f}, 止盈={signal.take_profit:.6f}")
            logger.info(f"⚖️ 風險回報比: {signal.risk_reward_ratio:.2f}")
            
            # 處理新信號
            await self._process_new_signal(signal)
            
            # 發送Gmail通知
            await self._send_gmail_notification(signal)
            
            # 更新統計
            self._update_signal_statistics(signal)
            
            logger.info(f"✅ 信號保存完成: {signal.symbol} {signal.signal_type}")
            
        except Exception as e:
            logger.error(f"❌ 保存信號失敗: {e}")
    
    async def _send_gmail_notification(self, signal):
        """發送Gmail通知"""
        try:
            if not self.gmail_enabled or not self.gmail_service:
                logger.debug("📧 Gmail通知未啟用，跳過發送")
                return
            
            logger.info(f"📧 準備發送Gmail通知: {signal.symbol} {signal.signal_type}")
            
            # 異步發送通知，避免阻塞主流程
            success = await self.gmail_service.send_signal_notification(signal)
            
            if success:
                logger.info(f"✅ Gmail通知發送成功: {signal.symbol} {signal.signal_type}")
            else:
                logger.warning(f"⚠️ Gmail通知發送失敗: {signal.symbol} {signal.signal_type}")
                
        except Exception as e:
            logger.error(f"❌ 發送Gmail通知時發生錯誤: {e}")
            # 不重新拋出異常，避免影響主流程
    
    def _update_signal_statistics(self, signal):
        """更新信號統計"""
        try:
            # 簡單的統計記錄
            stats_key = f"{signal.symbol}_{signal.timeframe}"
            if not hasattr(self, 'signal_stats'):
                self.signal_stats = {}
            
            if stats_key not in self.signal_stats:
                self.signal_stats[stats_key] = {
                    'total_signals': 0,
                    'by_type': {},
                    'avg_confidence': 0,
                    'last_signal_time': None
                }
            
            stats = self.signal_stats[stats_key]
            stats['total_signals'] += 1
            stats['by_type'][signal.signal_type] = stats['by_type'].get(signal.signal_type, 0) + 1
            stats['avg_confidence'] = (stats['avg_confidence'] * (stats['total_signals'] - 1) + signal.confidence) / stats['total_signals']
            stats['last_signal_time'] = signal.timestamp
            
            logger.debug(f"📈 {stats_key} 統計更新: 總信號={stats['total_signals']}, 平均信心度={stats['avg_confidence']:.3f}")
            
        except Exception as e:
            logger.error(f"❌ 更新信號統計失敗: {e}")
    
    async def _should_generate_signal(self, symbol: str, timeframe: str) -> bool:
        """判斷是否應該生成新信號"""
        key = f"{symbol}_{timeframe}"
        
        # 檢查服務是否已初始化
        if not self.market_service:
            return False
        
        # 檢查冷卻時間
        if key in self.last_signals:
            last_time = self.last_signals[key].get('timestamp')
            if last_time:
                time_diff = (datetime.now() - last_time).total_seconds()
                if time_diff < self.signal_cooldown:
                    logger.debug(f"📧 信號冷卻中: {symbol} {timeframe} ({time_diff:.1f}/{self.signal_cooldown}秒)")
                    return False
        
        # 檢查數據充足性
        try:
            df = await self.market_service.get_historical_data(
                symbol=symbol, 
                timeframe=timeframe, 
                limit=self.min_history_points
            )
            
            return df is not None and len(df) >= self.min_history_points
            
        except Exception as e:
            logger.warning(f"檢查數據充足性失敗 {symbol} {timeframe}: {e}")
            return False
    
    async def _generate_comprehensive_signal(self, symbol: str, timeframe: str) -> Optional[TradingSignalAlert]:
        """生成綜合交易信號"""
        try:
            # 檢查服務是否已初始化
            if not self.market_service:
                logger.warning(f"market_service 未初始化，無法生成信號 {symbol} {timeframe}")
                return None
            
            # 1. 獲取歷史數據
            df = await self.market_service.get_historical_data(
                symbol=symbol, 
                timeframe=timeframe, 
                limit=self.min_history_points
            )
            
            if df is None or len(df) < self.min_history_points:
                logger.warning(f"數據不足 {symbol} {timeframe}: {len(df) if df is not None else 0} < {self.min_history_points}")
                return None
            
            # 2. K線形態分析（最高優先級）
            pattern_analysis = analyze_candlestick_patterns(df, timeframe)
            
            # 3. 技術指標分析
            indicators = self.pandas_ta_indicators.calculate_all_indicators(df)
            
            # 4. 信號解析
            signals = self.signal_parser.analyze_signals(df, strategy="realtime")
            
            # 5. 綜合判斷
            return await self._synthesize_signal(
                symbol, timeframe, pattern_analysis, indicators, signals, df
            )
            
        except Exception as e:
            logger.error(f"生成綜合信號失敗 {symbol} {timeframe}: {e}")
            return None
    
    async def _synthesize_signal(
        self, 
        symbol: str, 
        timeframe: str, 
        pattern_analysis: dict,
        indicators: dict,
        signals: list,
        df: pd.DataFrame
    ) -> Optional[TradingSignalAlert]:
        """綜合分析結果生成最終信號"""
        
        current_price = float(df['close'].iloc[-1])
        indicators_used = []
        total_confidence = 0.0
        signal_count = 0
        signal_type = "HOLD"
        reasoning_parts = []
        
        # 1. K線形態權重（40%）
        pattern_weight = 0.0
        if pattern_analysis.get('has_pattern') and pattern_analysis.get('primary_pattern'):
            pattern = pattern_analysis['primary_pattern']
            pattern_weight = pattern.confidence * 0.4
            indicators_used.append(f"K線形態: {pattern.pattern_name}")
            reasoning_parts.append(f"檢測到{pattern.pattern_name}形態(信心度:{pattern.confidence:.2f})")
            
            if pattern.pattern_type.value == "bullish":
                signal_type = "BUY"
            elif pattern.pattern_type.value == "bearish":
                signal_type = "SELL"
        
        # 2. 技術指標權重（40%）
        technical_weight = 0.0
        buy_signals = 0
        sell_signals = 0
        
        for signal in signals:
            if hasattr(signal, 'signal_type') and hasattr(signal, 'confidence'):
                signal_count += 1
                if signal.signal_type.value in ["BUY", "STRONG_BUY"]:
                    buy_signals += 1
                    technical_weight += signal.confidence * 0.1
                elif signal.signal_type.value in ["SELL", "STRONG_SELL"]:
                    sell_signals += 1
                    technical_weight += signal.confidence * 0.1
                
                indicators_used.append(f"{signal.indicator}")
                reasoning_parts.append(f"{signal.indicator}:{signal.signal_type.value}")
        
        # 3. 趨勢一致性權重（20%）
        trend_weight = 0.0
        if buy_signals > sell_signals:
            trend_weight = 0.2
            if signal_type != "SELL":  # 不與K線形態衝突
                signal_type = "BUY"
        elif sell_signals > buy_signals:
            trend_weight = 0.2
            if signal_type != "BUY":  # 不與K線形態衝突  
                signal_type = "SELL"
        
        # 計算總信心度
        total_confidence = min(pattern_weight + technical_weight + trend_weight, 1.0)
        
        # 信心度太低則不生成信號
        if total_confidence < self.confidence_threshold:
            return None
        
        # 計算進出場點位
        entry_price, stop_loss, take_profit = self._calculate_entry_exit(
            current_price, signal_type, df
        )
        
        # 計算風險回報比
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        risk_reward_ratio = reward / risk if risk > 0 else 0
        
        # 判斷緊急程度
        urgency = self._determine_urgency(total_confidence, pattern_analysis)
        
        return TradingSignalAlert(
            symbol=symbol,
            signal_type=signal_type,
            confidence=total_confidence,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward_ratio=risk_reward_ratio,
            indicators_used=indicators_used,
            reasoning=" | ".join(reasoning_parts) if reasoning_parts else "技術指標綜合分析",
            timeframe=timeframe,
            timestamp=get_taiwan_now_naive(),
            urgency=urgency
        )
    
    def _calculate_entry_exit(self, current_price: float, signal_type: str, df: pd.DataFrame) -> tuple:
        """計算進出場點位"""
        atr = df['high'].rolling(14).max() - df['low'].rolling(14).min()
        avg_atr = atr.mean()
        
        if signal_type in ["BUY", "STRONG_BUY"]:
            entry_price = current_price * 1.001  # 略高於當前價格
            stop_loss = current_price * 0.97     # 3% 止損
            take_profit = current_price * 1.06   # 6% 止盈
        elif signal_type in ["SELL", "STRONG_SELL"]:
            entry_price = current_price * 0.999  # 略低於當前價格
            stop_loss = current_price * 1.03     # 3% 止損
            take_profit = current_price * 0.94   # 6% 止盈
        else:
            entry_price = current_price
            stop_loss = current_price * 0.95
            take_profit = current_price * 1.05
        
        return entry_price, stop_loss, take_profit
    
    def _determine_urgency(self, confidence: float, pattern_analysis: dict) -> str:
        """判斷信號緊急程度"""
        if confidence >= 0.9:
            return "critical"
        elif confidence >= 0.8:
            return "high"
        elif confidence >= 0.7:
            return "medium"
        else:
            return "low"
    
    async def _process_new_signal(self, signal: TradingSignalAlert):
        """處理新生成的信號"""
        try:
            # 1. 更新快取
            key = f"{signal.symbol}_{signal.timeframe}"
            self.last_signals[key] = asdict(signal)
            
            # 2. 添加到歷史記錄
            self.signal_history.append(signal)
            
            # 3. 執行回調函數
            for callback in self.signal_callbacks:
                try:
                    await callback(signal)
                except Exception as e:
                    logger.error(f"信號回調執行失敗: {e}")
            
            # 4. 發送通知
            if signal.urgency in ["high", "critical"]:
                for callback in self.notification_callbacks:
                    try:
                        await callback(signal)
                    except Exception as e:
                        logger.error(f"通知回調執行失敗: {e}")
            
            logger.info(f"📢 新信號生成: {signal.symbol} {signal.signal_type} (信心度:{signal.confidence:.2f})")
            
        except Exception as e:
            logger.error(f"處理新信號失敗: {e}")
    
    async def _data_cleanup_loop(self):
        """數據清理循環 - 每7天清除一次舊數據"""
        logger.info("🧹 啟動數據清理循環...")
        
        while self.running:
            try:
                # 每7天執行一次清理
                await asyncio.sleep(7 * 24 * 3600)  # 7天
                
                if not self.running:
                    break
                
                await self._cleanup_old_data()
                
            except Exception as e:
                logger.error(f"數據清理錯誤: {e}")
                await asyncio.sleep(3600)  # 錯誤時1小時後重試
    
    async def _cleanup_old_data(self):
        """清理7天以上的舊數據"""
        try:
            cutoff_date = datetime.now() - timedelta(days=7)
            
            # 清理信號歷史
            original_count = len(self.signal_history)
            self.signal_history = [
                s for s in self.signal_history 
                if s.timestamp > cutoff_date
            ]
            cleaned_signals = original_count - len(self.signal_history)
            
            # 清理價格緩衝區（保留最近3天的數據）
            buffer_cutoff = datetime.now() - timedelta(days=3)
            cleaned_buffers = 0
            
            for symbol in self.price_buffers:
                original_buffer_size = len(self.price_buffers[symbol])
                self.price_buffers[symbol] = [
                    p for p in self.price_buffers[symbol]
                    if p['timestamp'] > buffer_cutoff
                ]
                cleaned_buffers += original_buffer_size - len(self.price_buffers[symbol])
            
            logger.info(f"🧹 數據清理完成: 清理{cleaned_signals}個舊信號, {cleaned_buffers}個舊價格數據點")
            
        except Exception as e:
            logger.error(f"清理舊數據失敗: {e}")
    
    async def _health_check_loop(self):
        """健康檢查循環"""
        logger.info("💓 啟動健康檢查循環...")
        
        while self.running:
            try:
                await asyncio.sleep(300)  # 每5分鐘檢查一次
                
                # 檢查各組件狀態
                health_status = {
                    'engine_running': self.running,
                    'monitored_symbols': len(self.monitored_symbols),
                    'signal_count_24h': len([
                        s for s in self.signal_history 
                        if (datetime.now() - s.timestamp).total_seconds() < 86400
                    ]),
                    'price_buffer_status': {
                        symbol: len(buffer) 
                        for symbol, buffer in self.price_buffers.items()
                    },
                    'last_check': datetime.now().isoformat()
                }
                
                logger.debug(f"健康檢查: {health_status}")
                
            except Exception as e:
                logger.error(f"健康檢查錯誤: {e}")
                await asyncio.sleep(600)  # 錯誤時10分鐘後重試
    
    def get_statistics(self) -> dict:
        """獲取引擎統計信息"""
        return {
            'running': self.running,
            'monitored_symbols': self.monitored_symbols,
            'monitored_timeframes': self.monitored_timeframes,
            'total_signals_generated': len(self.signal_history),
            'signals_last_24h': len([
                s for s in self.signal_history 
                if (datetime.now() - s.timestamp).total_seconds() < 86400
            ]),
            'average_confidence': np.mean([s.confidence for s in self.signal_history]) if self.signal_history else 0,
            'price_buffers_status': {
                symbol: len(buffer) 
                for symbol, buffer in self.price_buffers.items()
            },
            'last_signals': {
                key: {
                    'symbol': data.get('symbol'),
                    'signal_type': data.get('signal_type'),
                    'confidence': data.get('confidence'),
                    'timestamp': data.get('timestamp')
                }
                for key, data in self.last_signals.items()
            }
        }

# 全局實例
realtime_signal_engine = RealtimeSignalEngine()
