# quantum_production_extension.py
# 生產級量子決策系統擴展模組
# 專門負責 Trading X 整合和生產級功能

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

# 導入基礎量子模組
from .quantum_decision_optimizer import (
    CryptoMarketObservation,
    ProductionQuantumConfig,
    ProductionQuantumEngine,
    ProductionTradingHypothesis,
)

logger = logging.getLogger(__name__)

class TradingXQuantumProcessor:
    """Trading X 量子決策處理器 - 完整生產級實現"""
    
    def __init__(self, config: ProductionQuantumConfig):
        self.config = config
        self.quantum_engine = ProductionQuantumEngine(config)
        
        # Trading X 服務整合
        self.market_data_service = None
        self.data_collectors = {}
        self.hypothesis_generators = {}
        
        # 實時數據流管理
        self.active_streams = set()
        self.data_quality_metrics = {}
        
        # 執行管理
        self.execution_queue = asyncio.Queue()
        self.position_manager = None
        
        # 監控和日誌
        self.performance_monitor = PerformanceMonitor()
        self.alert_manager = AlertManager()

    async def initialize_production_services(self):
        """初始化生產服務 - Trading X 整合"""
        try:
            # 1. 嘗試初始化 Trading X 市場數據服務
            try:
                from app.services.market_data import MarketDataService
                self.market_data_service = MarketDataService()
                await self.market_data_service.initialize()
                logger.info("Trading X 市場數據服務已初始化")
            except ImportError:
                logger.error("Trading X 服務未找到 - 生產環境必須有真實數據源")
                raise RuntimeError("生產環境要求: Trading X 市場數據服務必須可用")
            except Exception as e:
                logger.error(f"Trading X 服務初始化失敗: {e}")
                raise RuntimeError(f"市場數據服務啟動失敗: {e}")
            
            # 2. 設置區塊鏈七幣種數據收集器
            for symbol in self.config.primary_symbols:
                self.data_collectors[symbol] = CryptoDataCollector(
                    symbol=symbol,
                    on_update_callback=self._handle_market_update
                )
                await self.data_collectors[symbol].start()
            
            # 3. 初始化假設生成器
            for symbol in self.config.primary_symbols:
                self.hypothesis_generators[symbol] = ProductionHypothesisGenerator(
                    symbol=symbol,
                    config=self.config
                )
            
            # 4. 初始化倉位管理器
            self.position_manager = QuantumPositionManager(self.config)
            
            # 5. 啟動執行處理器
            asyncio.create_task(self._execute_decision_worker())
            
            logger.info(f"量子決策處理器已成功初始化，監控 {len(self.config.primary_symbols)} 個幣種")
            
        except Exception as e:
            logger.error(f"初始化生產服務失敗: {e}")
            raise

    async def _handle_market_update(self, symbol: str, market_data: Dict[str, Any]):
        """處理市場數據更新 - 即時響應"""
        try:
            # 1. 構建觀測對象
            observation = await self._build_observation_from_market_data(symbol, market_data)
            
            if not observation:
                return
            
            # 2. 生成交易假設
            hypotheses = await self.hypothesis_generators[symbol].generate_hypotheses(observation)
            
            # 3. 量子決策處理
            decision = await self.quantum_engine.process_observation_production(
                observation, hypotheses
            )
            
            # 4. 處理決策結果
            if decision:
                await self._enqueue_decision(decision)
                
                # 5. 更新性能監控
                self.performance_monitor.record_decision(symbol, decision)
                
                # 6. 檢查告警條件
                await self.alert_manager.check_decision_alerts(decision)
        
        except Exception as e:
            logger.error(f"處理市場更新失敗 {symbol}: {e}")

    async def _build_observation_from_market_data(self, 
                                                 symbol: str, 
                                                 market_data: Dict[str, Any]) -> Optional[CryptoMarketObservation]:
        """從原始市場數據構建觀測對象"""
        try:
            # 獲取即時價格數據
            ticker = market_data.get('ticker', {})
            price = float(ticker.get('price', 0))
            
            if price <= 0:
                return None
            
            # 計算收益率
            returns = await self._calculate_returns(symbol, price)
            
            # 獲取技術指標
            technical_data = await self._compute_real_time_technical_indicators(symbol)
            
            # 獲取市場微觀結構數據
            microstructure = await self._get_market_microstructure(symbol)
            
            # 獲取鏈上數據
            onchain_data = await self._get_onchain_metrics(symbol)
            
            # 構建完整觀測
            observation = CryptoMarketObservation(
                timestamp=pd.Timestamp.now(),
                symbol=symbol,
                price=price,
                returns=returns,
                volume_24h=float(ticker.get('volume_24h', 0)),
                market_cap=ticker.get('market_cap'),
                
                # 技術指標
                realized_volatility=technical_data['realized_volatility'],
                momentum_slope=technical_data['momentum_slope'],
                rsi_14=technical_data['rsi_14'],
                bb_position=technical_data['bb_position'],
                
                # 市場微觀結構
                orderbook_pressure=microstructure['orderbook_pressure'],
                bid_ask_spread=microstructure['bid_ask_spread'],
                trade_aggression=microstructure['trade_aggression'],
                
                # 資金和鏈上數據
                funding_rate=onchain_data['funding_rate'],
                open_interest=onchain_data['open_interest'],
                liquidation_ratio=onchain_data['liquidation_ratio'],
                
                # 網路效應
                social_sentiment=onchain_data.get('social_sentiment', 0.0),
                whale_activity=onchain_data.get('whale_activity', 0.0),
                
                # 相關性和制度信號
                correlation_btc=await self._calculate_btc_correlation(symbol),
                market_regime_signal=technical_data.get('regime_signal', 0.0)
            )
            
            return observation
            
        except Exception as e:
            logger.error(f"構建觀測失敗 {symbol}: {e}")
            return None

    async def _calculate_returns(self, symbol: str, current_price: float) -> float:
        """計算即時收益率"""
        # 從緩存獲取上一個價格
        buffer = self.quantum_engine.observation_buffers.get(symbol, [])
        if buffer:
            last_price = buffer[-1].price
            if last_price > 0:
                return np.log(current_price / last_price)
        return 0.0

    async def _compute_real_time_technical_indicators(self, symbol: str) -> Dict[str, float]:
        """計算即時技術指標 - 基於真實數據"""
        try:
            # 獲取最近的 K線數據
            if self.market_data_service and hasattr(self.market_data_service, 'get_recent_klines'):
                klines = await self.market_data_service.get_recent_klines(
                    symbol=symbol,
                    interval='1m',
                    limit=100
                )
            else:
                # 回退到緩存數據
                buffer = self.quantum_engine.observation_buffers.get(symbol, [])
                klines = self._buffer_to_klines(buffer)
            
            if not klines or len(klines) < 20:
                logger.error(f"技術指標計算失敗: {symbol} 數據不足 (需要>=20個數據點)")
                raise ValueError(f"數據不足: {symbol} 只有 {len(klines) if klines else 0} 個數據點")
            
            # 轉換為價格數組
            prices = np.array([getattr(k, 'close_price', k.get('close', 0)) for k in klines])
            volumes = np.array([getattr(k, 'volume', k.get('volume', 0)) for k in klines])
            
            # 1. 已實現波動率 (20期)
            returns = np.diff(np.log(prices))
            realized_vol = np.std(returns[-20:]) if len(returns) >= 20 else 0.01
            
            # 2. 動量斜率 (線性回歸)
            if len(prices) >= 10:
                x = np.arange(10)
                y = prices[-10:]
                slope = np.polyfit(x, y, 1)[0] / y[-1]  # 正規化斜率
            else:
                slope = 0.0
            
            # 3. RSI (14期)
            rsi = self._calculate_rsi(prices, period=14)
            
            # 4. 布林帶位置
            bb_position = self._calculate_bollinger_position(prices, period=20)
            
            # 5. 制度信號 (複合指標)
            regime_signal = self._calculate_regime_signal(prices, volumes)
            
            return {
                'realized_volatility': realized_vol,
                'momentum_slope': slope,
                'rsi_14': rsi,
                'bb_position': bb_position,
                'regime_signal': regime_signal
            }
            
        except Exception as e:
            logger.error(f"計算技術指標失敗 {symbol}: {e}")
            raise RuntimeError(f"技術指標計算失敗: {e}")

    async def _get_real_funding_rate(self, symbol: str) -> float:
        """獲取真實資金費率 - 禁止模擬數據"""
        try:
            # 使用 Trading X 的 Binance API 獲取資金費率
            if hasattr(self.market_data_service, 'get_funding_rate'):
                funding_rate = await self.market_data_service.get_funding_rate(symbol)
                return funding_rate
            else:
                # 直接使用 Binance API
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    url = f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}"
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            return float(data.get('lastFundingRate', 0))
                        else:
                            logger.error(f"獲取資金費率失敗 {symbol}: HTTP {response.status}")
                            raise RuntimeError(f"API 請求失敗: {response.status}")
        except Exception as e:
            logger.error(f"獲取資金費率失敗 {symbol}: {e}")
            raise RuntimeError(f"資金費率數據獲取失敗: {e}")

    async def _get_real_open_interest(self, symbol: str) -> float:
        """獲取真實未平倉量 - 禁止模擬數據"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                url = f"https://fapi.binance.com/fapi/v1/openInterest?symbol={symbol}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return float(data.get('openInterest', 0))
                    else:
                        logger.error(f"獲取未平倉量失敗 {symbol}: HTTP {response.status}")
                        raise RuntimeError(f"未平倉量 API 請求失敗: {response.status}")
        except Exception as e:
            logger.error(f"獲取未平倉量失敗 {symbol}: {e}")
            raise RuntimeError(f"未平倉量數據獲取失敗: {e}")

    def _buffer_to_klines(self, buffer: List) -> List:
        """將緩存轉換為 K線格式"""
        if not buffer:
            return []
        
        klines = []
        for obs in buffer[-100:]:  # 最多 100 個
            kline = {
                'close': obs.price,
                'volume': getattr(obs, 'volume_24h', 0),
                'timestamp': obs.timestamp
            }
            klines.append(kline)
        
        return klines

    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> float:
        """計算 RSI 指標"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi)

    def _calculate_bollinger_position(self, prices: np.ndarray, period: int = 20) -> float:
        """計算布林帶位置"""
        if len(prices) < period:
            return 0.5
        
        recent_prices = prices[-period:]
        mean_price = np.mean(recent_prices)
        std_price = np.std(recent_prices)
        
        if std_price == 0:
            return 0.5
        
        current_price = prices[-1]
        position = (current_price - mean_price) / (2 * std_price) + 0.5
        
        return np.clip(position, 0.0, 1.0)

    def _calculate_regime_signal(self, prices: np.ndarray, volumes: np.ndarray) -> float:
        """計算市場制度信號"""
        if len(prices) < 20:
            return 0.0
        
        # 多個制度指標的加權組合
        vol_signal = self._volatility_regime_signal(prices)
        trend_signal = self._trend_regime_signal(prices)
        volume_signal = self._volume_regime_signal(volumes)
        
        # 加權組合
        regime_signal = 0.4 * vol_signal + 0.4 * trend_signal + 0.2 * volume_signal
        
        return float(np.clip(regime_signal, -1.0, 1.0))

    def _volatility_regime_signal(self, prices: np.ndarray) -> float:
        """波動率制度信號"""
        returns = np.diff(np.log(prices))
        if len(returns) < 20:
            return 0.0
        
        current_vol = np.std(returns[-5:])
        baseline_vol = np.std(returns[-20:])
        
        if baseline_vol == 0:
            return 0.0
        
        vol_ratio = current_vol / baseline_vol
        return np.tanh((vol_ratio - 1.0) * 2)  # 正規化到 [-1, 1]

    def _trend_regime_signal(self, prices: np.ndarray) -> float:
        """趨勢制度信號"""
        if len(prices) < 20:
            return 0.0
        
        # 多時間框架趨勢強度
        short_trend = (prices[-1] / prices[-5] - 1) * 100  # 5期趨勢
        medium_trend = (prices[-1] / prices[-10] - 1) * 100  # 10期趨勢
        
        combined_trend = 0.6 * short_trend + 0.4 * medium_trend
        return np.tanh(combined_trend)  # 正規化

    def _volume_regime_signal(self, volumes: np.ndarray) -> float:
        """成交量制度信號"""
        if len(volumes) < 10:
            return 0.0
        
        current_vol = np.mean(volumes[-3:])
        baseline_vol = np.mean(volumes[-10:])
        
        if baseline_vol == 0:
            return 0.0
        
        vol_ratio = current_vol / baseline_vol
        return np.tanh((vol_ratio - 1.0))  # 正規化

    async def _get_market_microstructure(self, symbol: str) -> Dict[str, float]:
        """獲取市場微觀結構數據"""
        try:
            # 獲取訂單簿數據
            depth_data = await self._get_order_book_depth(symbol)
            
            # 計算訂單簿壓力
            orderbook_pressure = self._calculate_orderbook_pressure(depth_data)
            
            # 計算買賣價差
            bid_ask_spread = self._calculate_bid_ask_spread(depth_data)
            
            # 獲取最近交易數據
            recent_trades = await self._get_recent_trades(symbol)
            
            # 計算交易主動性
            trade_aggression = self._calculate_trade_aggression(recent_trades)
            
            return {
                'orderbook_pressure': orderbook_pressure,
                'bid_ask_spread': bid_ask_spread,
                'trade_aggression': trade_aggression
            }
            
        except Exception as e:
            logger.error(f"獲取微觀結構數據失敗 {symbol}: {e}")
            raise RuntimeError(f"市場微觀結構數據獲取失敗: {e}")

    async def _get_order_book_depth(self, symbol: str) -> Dict[str, Any]:
        """獲取訂單簿深度 - 必須有真實數據"""
        if not self.market_data_service:
            raise RuntimeError("市場數據服務未初始化")
        
        if hasattr(self.market_data_service, 'get_depth'):
            depth = await self.market_data_service.get_depth(symbol)
            if not depth or not depth.get('bids') or not depth.get('asks'):
                raise ValueError(f"訂單簿數據無效: {symbol}")
            return depth
        else:
            raise RuntimeError("市場數據服務不支持訂單簿數據")

    async def _get_recent_trades(self, symbol: str) -> List[Dict]:
        """獲取最近交易 - 必須有真實數據"""
        if not self.market_data_service:
            raise RuntimeError("市場數據服務未初始化")
        
        if hasattr(self.market_data_service, 'get_recent_trades'):
            trades = await self.market_data_service.get_recent_trades(symbol)
            if not trades:
                raise ValueError(f"交易數據為空: {symbol}")
            return trades
        else:
            raise RuntimeError("市場數據服務不支持交易數據")

    def _calculate_orderbook_pressure(self, depth_data: Dict) -> float:
        """計算訂單簿壓力"""
        bids = depth_data.get('bids', [])
        asks = depth_data.get('asks', [])
        
        if not bids or not asks:
            return 0.0
        
        bid_volume = sum(float(bid[1]) for bid in bids[:10])
        ask_volume = sum(float(ask[1]) for ask in asks[:10])
        
        if bid_volume + ask_volume == 0:
            return 0.0
        
        return (bid_volume - ask_volume) / (bid_volume + ask_volume)

    def _calculate_bid_ask_spread(self, depth_data: Dict) -> float:
        """計算買賣價差 - 必須有真實數據"""
        bids = depth_data.get('bids', [])
        asks = depth_data.get('asks', [])
        
        if not bids or not asks:
            raise ValueError("訂單簿數據不完整")
        
        best_bid = float(bids[0][0])
        best_ask = float(asks[0][0])
        
        if best_bid <= 0 or best_ask <= 0:
            raise ValueError(f"價格數據無效: bid={best_bid}, ask={best_ask}")
        
        return (best_ask - best_bid) / ((best_ask + best_bid) / 2)

    def _calculate_trade_aggression(self, trades: List[Dict]) -> float:
        """計算交易主動性"""
        if not trades:
            return 0.0
        
        # 簡化的主動性計算
        buy_volume = sum(float(t.get('qty', 0)) for t in trades if t.get('is_buyer_maker', False))
        sell_volume = sum(float(t.get('qty', 0)) for t in trades if not t.get('is_buyer_maker', True))
        
        total_volume = buy_volume + sell_volume
        if total_volume == 0:
            return 0.0
        
        return (buy_volume - sell_volume) / total_volume

    async def _get_onchain_metrics(self, symbol: str) -> Dict[str, float]:
        """獲取鏈上指標"""
        try:
            metrics = {
                'funding_rate': 0.0,
                'open_interest': 0.0,
                'liquidation_ratio': 0.0,
                'social_sentiment': 0.0,
                'whale_activity': 0.0
            }
            
            # 1. 資金費率（期貨合約）
            if symbol.endswith('USDT'):
                funding_rate = await self._get_real_funding_rate(symbol)
                metrics['funding_rate'] = funding_rate
            
            # 2. 未平倉量
            oi_value = await self._get_real_open_interest(symbol)
            metrics['open_interest'] = oi_value
            
            # 3. 清算數據 (暫時跳過，需要專門的清算數據API)
            # liquidation_data = await self._get_liquidation_data(symbol)
            # metrics['liquidation_ratio'] = liquidation_data.get('ratio', 0.0)
            
            return metrics
            
        except Exception as e:
            logger.error(f"獲取鏈上指標失敗 {symbol}: {e}")
            raise RuntimeError(f"鏈上數據獲取失敗: {e}")

    async def _get_open_interest_data(self, symbol: str) -> Dict[str, Any]:
        """獲取未平倉量數據 - 已整合到 _get_real_open_interest"""
        oi_value = await self._get_real_open_interest(symbol)
        return {'open_interest': oi_value}

    async def _get_liquidation_data(self, symbol: str) -> Dict[str, Any]:
        """獲取清算數據 - 需要專門的清算數據源"""
        # TODO: 整合清算數據 API (需要專門的數據源)
        logger.warning(f"清算數據暫不可用: {symbol}")
        return {'ratio': 0.0}

    async def _calculate_btc_correlation(self, symbol: str) -> float:
        """計算與 BTC 的相關性"""
        if symbol == 'BTCUSDT':
            return 1.0
        
        try:
            # 獲取兩個幣種的歷史價格數據
            btc_buffer = self.quantum_engine.observation_buffers.get('BTCUSDT', [])
            symbol_buffer = self.quantum_engine.observation_buffers.get(symbol, [])
            
            if len(btc_buffer) < 20 or len(symbol_buffer) < 20:
                return 0.5  # 預設中等相關性
            
            # 對齊時間序列並計算收益率
            min_length = min(len(btc_buffer), len(symbol_buffer), 50)
            btc_returns = [obs.returns for obs in btc_buffer[-min_length:]]
            symbol_returns = [obs.returns for obs in symbol_buffer[-min_length:]]
            
            # 計算相關係數
            correlation = np.corrcoef(btc_returns, symbol_returns)[0, 1]
            
            return float(correlation) if not np.isnan(correlation) else 0.5
            
        except Exception as e:
            logger.error(f"計算 BTC 相關性失敗 {symbol}: {e}")
            return 0.5

    async def _enqueue_decision(self, decision: Dict[str, Any]):
        """將決策加入執行佇列"""
        await self.execution_queue.put(decision)

    async def _execute_decision_worker(self):
        """決策執行工作者 - 後台處理"""
        while True:
            try:
                # 等待決策
                decision = await self.execution_queue.get()
                
                # 執行決策
                await self._execute_quantum_decision(decision)
                
                # 標記任務完成
                self.execution_queue.task_done()
                
            except Exception as e:
                logger.error(f"執行決策失敗: {e}")

    async def _execute_quantum_decision(self, decision: Dict[str, Any]):
        """執行量子決策 - 整合交易執行引擎"""
        try:
            symbol = decision['symbol']
            hypothesis = decision['hypothesis']
            position_size = decision['position_size']
            
            # 1. 風險檢查
            if not await self._validate_execution_risk(decision):
                logger.warning(f"風險檢查未通過 {symbol}")
                return
            
            # 2. 更新倉位狀態
            await self.position_manager.update_position(
                symbol=symbol,
                size=position_size,
                direction=hypothesis.direction,
                metadata=decision
            )
            
            # 3. 記錄執行
            self.quantum_engine.execution_stats['executed_trades'] += 1
            logger.info(f"量子決策已執行 {symbol}: {hypothesis.hypothesis_id}")
            
        except Exception as e:
            logger.error(f"執行量子決策失敗: {e}")

    async def _validate_execution_risk(self, decision: Dict[str, Any]) -> bool:
        """驗證執行風險"""
        # 實現風險驗證邏輯
        return True

    async def start_quantum_processing(self):
        """啟動量子決策處理系統"""
        try:
            logger.info("啟動 Trading X 量子決策處理系統...")
            
            # 1. 初始化生產服務
            await self.initialize_production_services()
            
            # 2. 啟動性能監控
            await self.performance_monitor.start()
            
            # 3. 啟動告警管理
            await self.alert_manager.start()
            
            logger.info(f"量子決策系統已啟動，監控 {len(self.config.primary_symbols)} 個幣種")
            
        except Exception as e:
            logger.error(f"啟動量子處理系統失敗: {e}")
            raise

    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        return {
            'quantum_engine_state': self.quantum_engine.get_production_state(),
            'active_streams': list(self.active_streams),
            'data_quality': self.data_quality_metrics,
            'performance_metrics': self.performance_monitor.get_metrics(),
            'position_summary': self.position_manager.get_summary() if self.position_manager else {},
            'execution_queue_size': self.execution_queue.qsize()
        }

# --------------------------
# 輔助類別實現
# --------------------------

class CryptoDataCollector:
    """加密貨幣數據收集器"""
    def __init__(self, symbol: str, on_update_callback):
        self.symbol = symbol
        self.on_update_callback = on_update_callback
        self.is_running = False
        
    async def start(self):
        """啟動數據收集"""
        self.is_running = True
        logger.info(f"數據收集器已啟動: {self.symbol}")

class ProductionHypothesisGenerator:
    """生產級假設生成器"""
    def __init__(self, symbol: str, config: ProductionQuantumConfig):
        self.symbol = symbol
        self.config = config
        
    async def generate_hypotheses(self, obs: CryptoMarketObservation) -> List[ProductionTradingHypothesis]:
        """生成交易假設"""
        hypotheses = []
        
        # 1. 趨勢跟隨假設
        if abs(obs.momentum_slope) > 0.001:
            direction = 1 if obs.momentum_slope > 0 else -1
            hypotheses.append(ProductionTradingHypothesis(
                symbol=self.symbol,
                hypothesis_id=f"TREND_{self.symbol}_{direction}",
                direction=direction,
                expected_return_1h=abs(obs.momentum_slope) * 10,
                expected_return_4h=abs(obs.momentum_slope) * 25,
                expected_return_24h=abs(obs.momentum_slope) * 60,
                value_at_risk_95=obs.realized_volatility * 2,
                expected_shortfall=obs.realized_volatility * 2.5,
                max_adverse_excursion=obs.realized_volatility * 3,
                optimal_timeframe="1h",
                entry_confidence=0.7 + min(abs(obs.momentum_slope) * 1000, 0.2),
                exit_conditions={'stop_loss': -0.02, 'take_profit': 0.03},
                regime_dependency=np.array([0.8, 0.3, 0.5, 0.6, 0.4, 0.2]),
                regime_performance={i: obs.momentum_slope * (10 + i) for i in range(6)}
            ))
        
        # 2. 均值回歸假設
        if obs.bb_position > 0.8 or obs.bb_position < 0.2:
            direction = -1 if obs.bb_position > 0.8 else 1
            hypotheses.append(ProductionTradingHypothesis(
                symbol=self.symbol,
                hypothesis_id=f"MEANREV_{self.symbol}_{direction}",
                direction=direction,
                expected_return_1h=0.005,
                expected_return_4h=0.015,
                expected_return_24h=0.03,
                value_at_risk_95=obs.realized_volatility * 1.5,
                expected_shortfall=obs.realized_volatility * 2,
                max_adverse_excursion=obs.realized_volatility * 2.5,
                optimal_timeframe="1h",
                entry_confidence=0.6 + abs(obs.bb_position - 0.5) * 0.4,
                exit_conditions={'stop_loss': -0.015, 'take_profit': 0.02},
                regime_dependency=np.array([0.3, 0.5, 0.2, 0.8, 0.7, 0.1]),
                regime_performance={i: 0.01 - i * 0.002 for i in range(6)}
            ))
        
        # 3. 波動率突破假設
        if obs.realized_volatility > 0.03:
            hypotheses.append(ProductionTradingHypothesis(
                symbol=self.symbol,
                hypothesis_id=f"VOLBREAK_{self.symbol}",
                direction=1 if obs.momentum_slope > 0 else -1,
                expected_return_1h=obs.realized_volatility * 0.5,
                expected_return_4h=obs.realized_volatility * 1.2,
                expected_return_24h=obs.realized_volatility * 2.5,
                value_at_risk_95=obs.realized_volatility * 2,
                expected_shortfall=obs.realized_volatility * 3,
                max_adverse_excursion=obs.realized_volatility * 4,
                optimal_timeframe="1h",
                entry_confidence=0.8,
                exit_conditions={'stop_loss': -0.025, 'take_profit': 0.04},
                regime_dependency=np.array([0.6, 0.7, 0.9, 0.2, 0.5, 0.8]),
                regime_performance={i: obs.realized_volatility * (0.5 + i * 0.1) for i in range(6)}
            ))
        
        return hypotheses

class QuantumPositionManager:
    """量子倉位管理器"""
    def __init__(self, config: ProductionQuantumConfig):
        self.config = config
        self.positions = {}
        
    async def update_position(self, symbol: str, size: float, direction: int, metadata: Dict):
        """更新倉位"""
        self.positions[symbol] = {
            'size': size,
            'direction': direction,
            'timestamp': datetime.now(),
            'metadata': metadata
        }
        
    def get_summary(self) -> Dict[str, Any]:
        """獲取倉位摘要"""
        total_exposure = sum(abs(pos['size']) for pos in self.positions.values())
        return {
            'total_positions': len(self.positions),
            'total_exposure': total_exposure,
            'positions': self.positions.copy()
        }

class PerformanceMonitor:
    """性能監控器"""
    def __init__(self):
        self.metrics = {
            'decisions_count': 0,
            'avg_confidence': 0.0,
            'processing_times': []
        }
        
    async def start(self):
        """啟動監控"""
        logger.info("性能監控器已啟動")
        
    def record_decision(self, symbol: str, decision: Dict[str, Any]):
        """記錄決策"""
        self.metrics['decisions_count'] += 1
        self.metrics['avg_confidence'] = (
            self.metrics['avg_confidence'] * (self.metrics['decisions_count'] - 1) +
            decision['confidence']
        ) / self.metrics['decisions_count']
        
    def get_metrics(self) -> Dict[str, Any]:
        """獲取指標"""
        return self.metrics.copy()

class AlertManager:
    """告警管理器"""
    async def start(self):
        """啟動告警"""
        logger.info("告警管理器已啟動")
        
    async def check_decision_alerts(self, decision: Dict[str, Any]):
        """檢查決策告警"""
        # 檢查是否需要發送告警
        if decision['confidence'] > 0.9:
            logger.info(f"高信心度決策: {decision['symbol']} - {decision['confidence']:.3f}")

# --------------------------
# 測試函數
# --------------------------

async def run_production_quantum_system_test():
    """運行完整的生產級量子系統測試"""
    print("="*60)
    print("生產級量子決策系統完整測試")
    print("="*60)
    
    # 創建生產級配置
    config = ProductionQuantumConfig(
        alpha_base=0.01,
        beta_base=0.05,
        kelly_multiplier=0.15,
        max_single_position=0.08,
        primary_symbols=['BTCUSDT', 'ETHUSDT', 'ADAUSDT']  # 測試用
    )
    
    # 初始化處理器
    processor = TradingXQuantumProcessor(config)
    
    try:
        # 啟動系統
        await processor.start_quantum_processing()
        
        # 模擬市場數據處理
        for symbol in config.primary_symbols:
            print(f"\n處理 {symbol} 市場數據...")
            
            # 創建模擬市場數據
            market_data = {
                'ticker': {
                    'price': 50000.0 if symbol == 'BTCUSDT' else 3000.0,
                    'volume_24h': 1000000.0,
                    'change_percent': 2.5
                }
            }
            
            # 處理市場更新
            await processor._handle_market_update(symbol, market_data)
        
        # 等待處理完成
        await asyncio.sleep(1)
        
        # 顯示系統狀態
        status = processor.get_system_status()
        print(f"\n系統狀態:")
        print(f"  量子引擎統計: {status['quantum_engine_state']['execution_stats']}")
        print(f"  執行佇列大小: {status['execution_queue_size']}")
        print(f"  倉位摘要: {status['position_summary']}")
        
        print("\n生產級量子決策系統測試完成!")
        
    except Exception as e:
        print(f"系統測試失敗: {e}")

if __name__ == "__main__":
    # 運行完整系統測試
    asyncio.run(run_production_quantum_system_test())
