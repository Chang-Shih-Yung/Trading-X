# quantum_decision_optimizer.py
# 量子決策系統的精密優化策略實現
# 基於 regime_hmm_quantum.py 的高級決策引擎

import asyncio
import logging
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.special import logsumexp
from scipy.stats import t as student_t

from .regime_hmm_quantum import EmissionParams, TimeVaryingHMM

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class QuantumDecisionConfig:
    """量子決策系統配置"""
    # SPRT 參數
    alpha: float = 0.05  # Type-I 錯誤率
    beta: float = 0.2    # Type-II 錯誤率
    
    # 信念更新參數
    forgetting_factor: float = 0.96  # 遺忘因子 γ
    regime_update_freq: int = 1      # regime 更新頻率（分鐘）
    
    # Kelly 資金管理
    kelly_multiplier: float = 0.25   # Kelly 倍數
    max_position_cap: float = 0.1    # 最大倉位比例
    min_er_threshold: float = 0.001  # 最小期望收益閾值
    
    # 風險控制
    max_drawdown: float = 0.05       # 最大回撤
    volatility_lookback: int = 20    # 波動率回望期
    
    # 市場制度參數
    n_regimes: int = 6               # 制度數量
    regime_features: List[str] = field(default_factory=lambda: ['slope', 'volatility', 'orderbook'])

@dataclass
class MarketObservation:
    """市場觀測數據結構"""
    timestamp: pd.Timestamp
    returns: float
    log_volatility: float
    slope_d1: float
    orderbook_imbalance: float
    funding_rate: float
    rsi: float
    volume: float
    additional_features: Dict[str, float] = field(default_factory=dict)

@dataclass
class TradingHypothesis:
    """交易假設結構"""
    name: str
    direction: int  # 1: long, -1: short, 0: neutral
    expected_return: float
    expected_risk: float
    confidence: float
    time_horizon: int  # 預期持有期（分鐘）

class QuantumDecisionEngine:
    """量子決策引擎 - 精密實現"""
    
    def __init__(self, config: QuantumDecisionConfig):
        self.config = config
        self.hmm_model = TimeVaryingHMM(
            n_states=config.n_regimes,
            z_dim=len(config.regime_features),
            reg_lambda=1e-3
        )
        
        # 信念狀態
        self.belief_state: Dict[str, float] = {}
        self.log_odds_history: List[Dict[str, float]] = []
        
        # SPRT 閾值計算
        self.sprt_upper = math.log((1 - config.beta) / config.alpha)
        self.sprt_lower = math.log(config.beta / (1 - config.alpha))
        
        # 歷史數據緩存
        self.observation_buffer: List[MarketObservation] = []
        self.regime_probabilities: np.ndarray = np.ones(config.n_regimes) / config.n_regimes
        
        # 性能監控
        self.decision_stats = {
            'total_decisions': 0,
            'correct_decisions': 0,
            'average_confidence': 0.0,
            'average_holding_time': 0.0
        }

    def _extract_features(self, obs: MarketObservation) -> np.ndarray:
        """從市場觀測中提取制度特徵"""
        features = []
        for feature_name in self.config.regime_features:
            if feature_name == 'slope':
                features.append(obs.slope_d1)
            elif feature_name == 'volatility':
                features.append(obs.log_volatility)
            elif feature_name == 'orderbook':
                features.append(obs.orderbook_imbalance)
            else:
                features.append(obs.additional_features.get(feature_name, 0.0))
        return np.array(features)

    def _update_regime_probabilities(self, obs: MarketObservation):
        """更新市場制度概率 - 精密版本"""
        if len(self.observation_buffer) < 2:
            return
            
        # 構建觀測序列
        recent_obs = self.observation_buffer[-50:]  # 使用最近50個觀測
        
        x_seq = {
            'ret': np.array([o.returns for o in recent_obs]),
            'logvol': np.array([o.log_volatility for o in recent_obs]),
            'slope': np.array([o.slope_d1 for o in recent_obs]),
            'ob': np.array([o.orderbook_imbalance for o in recent_obs])
        }
        
        z_seq = np.array([self._extract_features(o) for o in recent_obs])
        
        # 執行 forward 算法獲取濾波概率
        try:
            log_alpha, _ = self.hmm_model.forward_log(x_seq, z_seq)
            self.regime_probabilities = np.exp(log_alpha[-1])  # 最新時刻的制度概率
        except Exception as e:
            print(f"Regime update failed: {e}")

    def _compute_hypothesis_likelihoods(self, 
                                      obs: MarketObservation,
                                      hypotheses: List[TradingHypothesis]) -> Dict[str, float]:
        """計算假設似然 - 多制度加權版本"""
        likelihoods = {}
        
        for hyp in hypotheses:
            # 對每個制度計算條件似然
            regime_weighted_likelihood = 0.0
            
            for regime_idx in range(self.config.n_regimes):
                regime_prob = self.regime_probabilities[regime_idx]
                
                # 基於制度的條件似然計算
                conditional_likelihood = self._compute_conditional_likelihood(
                    obs, hyp, regime_idx
                )
                
                regime_weighted_likelihood += regime_prob * conditional_likelihood
            
            likelihoods[hyp.name] = regime_weighted_likelihood
            
        return likelihoods

    def _compute_conditional_likelihood(self, 
                                      obs: MarketObservation,
                                      hypothesis: TradingHypothesis,
                                      regime_idx: int) -> float:
        """計算給定制度下的條件似然"""
        emission_params = self.hmm_model.emissions[regime_idx]
        
        # 1. 收益率似然 (Student-t 分布)
        returns_likelihood = self._student_t_likelihood(
            obs.returns, 
            emission_params.mu_ret,
            emission_params.sigma_ret,
            emission_params.nu_ret
        )
        
        # 2. 波動率似然 (對數正態)
        vol_likelihood = self._gaussian_likelihood(
            obs.log_volatility,
            emission_params.mu_logvol,
            emission_params.sigma_logvol
        )
        
        # 3. 斜率似然 (高斯)
        slope_likelihood = self._gaussian_likelihood(
            obs.slope_d1,
            emission_params.mu_slope,
            emission_params.sigma_slope
        )
        
        # 4. 訂單簿似然 (調整後高斯)
        ob_likelihood = self._adjusted_gaussian_likelihood(
            obs.orderbook_imbalance,
            emission_params.ob_loc,
            emission_params.ob_scale,
            hypothesis.direction
        )
        
        # 5. 方向一致性獎勵
        direction_bonus = self._compute_direction_consistency(
            obs, hypothesis, regime_idx
        )
        
        # 組合似然 (log 空間)
        total_log_likelihood = (
            returns_likelihood + vol_likelihood + 
            slope_likelihood + ob_likelihood + direction_bonus
        )
        
        return math.exp(total_log_likelihood)

    def _student_t_likelihood(self, x: float, mu: float, sigma: float, nu: float) -> float:
        """Student-t 分布對數似然"""
        sigma = max(sigma, 1e-9)
        nu = max(nu, 2.1)
        z = (x - mu) / sigma
        
        a = math.lgamma((nu + 1.0) / 2.0) - math.lgamma(nu / 2.0)
        b = -0.5 * math.log(nu * math.pi) - math.log(sigma)
        c = -(nu + 1.0) / 2.0 * math.log1p((z * z) / nu)
        
        return a + b + c

    def _gaussian_likelihood(self, x: float, mu: float, sigma: float) -> float:
        """高斯分布對數似然"""
        sigma = max(sigma, 1e-9)
        return -0.5 * math.log(2 * math.pi) - math.log(sigma) - 0.5 * ((x - mu) ** 2) / (sigma ** 2)

    def _adjusted_gaussian_likelihood(self, x: float, mu: float, sigma: float, direction: int) -> float:
        """根據方向調整的高斯似然"""
        base_likelihood = self._gaussian_likelihood(x, mu, sigma)
        
        # 如果訂單簿不平衡與假設方向一致，給予獎勵
        if (x > 0 and direction > 0) or (x < 0 and direction < 0):
            return base_likelihood + 0.1  # 小幅獎勵
        else:
            return base_likelihood - 0.05  # 小幅懲罰

    def _compute_direction_consistency(self, 
                                    obs: MarketObservation,
                                    hypothesis: TradingHypothesis,
                                    regime_idx: int) -> float:
        """計算方向一致性獎勵"""
        consistency_score = 0.0
        
        # RSI 一致性
        if hypothesis.direction > 0 and obs.rsi < 30:  # 超賣做多
            consistency_score += 0.2
        elif hypothesis.direction < 0 and obs.rsi > 70:  # 超買做空
            consistency_score += 0.2
        
        # 斜率一致性
        if (obs.slope_d1 > 0 and hypothesis.direction > 0) or \
           (obs.slope_d1 < 0 and hypothesis.direction < 0):
            consistency_score += 0.1
        
        # 資金費率一致性
        if (obs.funding_rate < 0 and hypothesis.direction > 0) or \
           (obs.funding_rate > 0 and hypothesis.direction < 0):
            consistency_score += 0.05
        
        return consistency_score

    def _update_belief_state(self, likelihoods: Dict[str, float]):
        """更新信念狀態 - 對數機率比方法"""
        if not self.belief_state:
            # 初始化均勻信念
            total_hyp = len(likelihoods)
            for hyp_name in likelihoods:
                self.belief_state[hyp_name] = 1.0 / total_hyp
        
        # 轉換為對數機率比
        log_odds = {}
        for hyp_name, likelihood in likelihoods.items():
            if hyp_name in self.belief_state:
                # 更新公式：log(P_t(k)/P_t(k̄)) = log(P_{t-1}(k)/P_{t-1}(k̄)) + log(L_k/L_k̄)
                prior_odds = self.belief_state[hyp_name] / (1 - self.belief_state[hyp_name] + 1e-10)
                likelihood_ratio = likelihood / (sum(likelihoods.values()) - likelihood + 1e-10)
                
                new_log_odds = math.log(max(prior_odds, 1e-10)) + math.log(max(likelihood_ratio, 1e-10))
                
                # 應用遺忘因子
                new_log_odds *= self.config.forgetting_factor
                
                log_odds[hyp_name] = new_log_odds
        
        # 轉換回概率
        self._normalize_belief_state(log_odds)
        
        # 記錄歷史
        self.log_odds_history.append(log_odds.copy())
        if len(self.log_odds_history) > 1000:  # 保持記錄大小
            self.log_odds_history.pop(0)

    def _normalize_belief_state(self, log_odds: Dict[str, float]):
        """正規化信念狀態"""
        # 從對數機率比轉換為概率
        total_odds = sum(math.exp(lo) for lo in log_odds.values())
        
        for hyp_name, log_odd in log_odds.items():
            odds = math.exp(log_odd)
            self.belief_state[hyp_name] = odds / (total_odds + 1e-10)

    def _apply_sprt_decision(self, 
                           hypotheses: List[TradingHypothesis]) -> Optional[TradingHypothesis]:
        """應用 SPRT 決策規則"""
        if len(self.belief_state) < 2:
            return None
        
        # 找到最高和次高信念
        sorted_beliefs = sorted(self.belief_state.items(), key=lambda x: x[1], reverse=True)
        top_hyp_name, top_prob = sorted_beliefs[0]
        second_prob = sorted_beliefs[1][1] if len(sorted_beliefs) > 1 else 0.0
        
        # 計算對數勝算比
        if second_prob > 1e-10:
            log_odds_ratio = math.log(top_prob / second_prob)
        else:
            log_odds_ratio = self.sprt_upper + 1  # 強制觸發
        
        # SPRT 決策
        if log_odds_ratio >= self.sprt_upper:
            # 找到對應的假設
            selected_hyp = next((h for h in hypotheses if h.name == top_hyp_name), None)
            if selected_hyp:
                # 檢查期望收益
                expected_return = self._compute_expected_return(selected_hyp)
                if expected_return > self.config.min_er_threshold:
                    return selected_hyp
        elif log_odds_ratio <= self.sprt_lower:
            # 放棄當前假設集合
            return None
        
        # 繼續觀望
        return None

    def _compute_expected_return(self, hypothesis: TradingHypothesis) -> float:
        """計算期望收益 - Kelly 調整版本"""
        if len(self.observation_buffer) < self.config.volatility_lookback:
            return 0.0
        
        # 計算近期波動率
        recent_returns = [obs.returns for obs in self.observation_buffer[-self.config.volatility_lookback:]]
        volatility = np.std(recent_returns)
        
        # 基礎期望收益
        base_er = hypothesis.expected_return * hypothesis.confidence
        
        # 風險調整
        risk_adjusted_er = base_er - 0.5 * volatility ** 2
        
        # 考慮交易成本 (簡化)
        transaction_cost = 0.0005  # 0.05%
        
        return risk_adjusted_er - transaction_cost

    def _compute_kelly_size(self, hypothesis: TradingHypothesis) -> float:
        """計算 Kelly 倉位大小"""
        er = self._compute_expected_return(hypothesis)
        if er <= 0:
            return 0.0
        
        # 估計方差
        if len(self.observation_buffer) < self.config.volatility_lookback:
            return 0.0
        
        recent_returns = [obs.returns for obs in self.observation_buffer[-self.config.volatility_lookback:]]
        variance = np.var(recent_returns)
        
        if variance <= 0:
            return 0.0
        
        # Kelly 公式
        kelly_fraction = er / variance
        
        # 應用倍數和上限
        adjusted_size = kelly_fraction * self.config.kelly_multiplier
        return min(adjusted_size, self.config.max_position_cap)

    async def process_observation(self, 
                                obs: MarketObservation,
                                hypotheses: List[TradingHypothesis]) -> Optional[Dict[str, Any]]:
        """處理市場觀測並做出決策"""
        # 添加到緩存
        self.observation_buffer.append(obs)
        if len(self.observation_buffer) > 200:  # 保持緩存大小
            self.observation_buffer.pop(0)
        
        # 更新制度概率
        self._update_regime_probabilities(obs)
        
        # 計算假設似然
        likelihoods = self._compute_hypothesis_likelihoods(obs, hypotheses)
        
        # 更新信念狀態
        self._update_belief_state(likelihoods)
        
        # 應用 SPRT 決策
        selected_hypothesis = self._apply_sprt_decision(hypotheses)
        
        if selected_hypothesis:
            # 計算倉位大小
            position_size = self._compute_kelly_size(selected_hypothesis)
            
            # 構建決策結果
            decision = {
                'timestamp': obs.timestamp,
                'hypothesis': selected_hypothesis,
                'position_size': position_size,
                'confidence': self.belief_state.get(selected_hypothesis.name, 0.0),
                'regime_probabilities': self.regime_probabilities.copy(),
                'expected_return': self._compute_expected_return(selected_hypothesis),
                'belief_state': self.belief_state.copy()
            }
            
            # 更新統計
            self.decision_stats['total_decisions'] += 1
            
            return decision
        
        return None

    def get_current_state(self) -> Dict[str, Any]:
        """獲取當前量子決策狀態"""
        return {
            'belief_state': self.belief_state.copy(),
            'regime_probabilities': self.regime_probabilities.copy(),
            'decision_stats': self.decision_stats.copy(),
            'sprt_thresholds': {
                'upper': self.sprt_upper,
                'lower': self.sprt_lower
            },
            'buffer_size': len(self.observation_buffer)
        }

# 生產級量子決策處理器
class ProductionQuantumProcessor:
    """生產級量子決策處理器 - 整合 Trading X 區塊鏈數據流"""
    
    def __init__(self, config: QuantumDecisionConfig):
        self.config = config
        self.quantum_engine = QuantumDecisionEngine(config)
        self.market_data_service = None  # 延遲初始化
        self.active_symbols = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 
            'DOTUSDT', 'LINKUSDT', 'SOLUSDT'  # Trading X 主池七種幣
        ]
        self.data_processors = {}
        self.technical_calculators = {}
        self.decision_history = {}
        
        # 初始化各幣種的技術指標計算器
        for symbol in self.active_symbols:
            self.technical_calculators[symbol] = TechnicalIndicatorCalculator()
            self.decision_history[symbol] = []

    async def initialize(self):
        """初始化生產環境組件"""
        try:
            # 動態導入 Trading X 服務
            from app.services.binance_websocket import BinanceDataCollector
            from app.services.market_data import MarketDataService
            from app.services.technical_indicators import TechnicalIndicatorCalculator
            
            self.market_data_service = MarketDataService()
            
            # 設置實時數據回調
            if self.market_data_service.binance_collector:
                self.market_data_service.binance_collector.on_ticker = self._process_ticker_update
                self.market_data_service.binance_collector.on_kline = self._process_kline_update
                self.market_data_service.binance_collector.on_depth = self._process_depth_update
            
            logger.info("量子決策處理器初始化完成")
            
        except ImportError as e:
            logger.error(f"無法導入 Trading X 服務: {e}")
            raise
        except Exception as e:
            logger.error(f"初始化失敗: {e}")
            raise

    async def _process_ticker_update(self, ticker_data):
        """處理即時價格更新"""
        try:
            if ticker_data.symbol not in self.active_symbols:
                return
            
            # 計算收益率
            if hasattr(self, '_last_prices') and ticker_data.symbol in self._last_prices:
                last_price = self._last_prices[ticker_data.symbol]
                returns = math.log(ticker_data.price / last_price) if last_price > 0 else 0.0
            else:
                returns = 0.0
                
            # 更新最後價格
            if not hasattr(self, '_last_prices'):
                self._last_prices = {}
            self._last_prices[ticker_data.symbol] = ticker_data.price
            
            # 計算技術指標 (需要歷史數據)
            technical_data = await self._compute_technical_indicators(ticker_data.symbol)
            
            # 構建市場觀測
            observation = MarketObservation(
                timestamp=ticker_data.timestamp,
                returns=returns,
                log_volatility=technical_data.get('log_volatility', -2.0),
                slope_d1=technical_data.get('slope_d1', 0.0),
                orderbook_imbalance=await self._get_orderbook_imbalance(ticker_data.symbol),
                funding_rate=await self._get_funding_rate(ticker_data.symbol),
                rsi=technical_data.get('rsi', 50.0),
                volume=ticker_data.volume_24h,
                additional_features={
                    'price': ticker_data.price,
                    'change_percent': ticker_data.price_change_percent,
                    'high_24h': ticker_data.high_24h,
                    'low_24h': ticker_data.low_24h
                }
            )
            
            # 生成交易假設
            hypotheses = await self._generate_hypotheses(ticker_data.symbol, observation)
            
            # 量子決策處理
            decision = await self.quantum_engine.process_observation(observation, hypotheses)
            
            if decision:
                await self._handle_decision(ticker_data.symbol, decision)
                
        except Exception as e:
            logger.error(f"處理價格更新失敗 {ticker_data.symbol}: {e}")

    async def _compute_technical_indicators(self, symbol: str) -> Dict[str, float]:
        """計算技術指標"""
        try:
            # 獲取歷史 K線數據
            klines = await self.market_data_service.get_klines(
                symbol=symbol,
                interval='1m',
                limit=100
            )
            
            if not klines or len(klines) < 20:
                return {'log_volatility': -2.0, 'slope_d1': 0.0, 'rsi': 50.0}
            
            # 轉換為 DataFrame
            df = pd.DataFrame([{
                'timestamp': k.timestamp,
                'open': k.open_price,
                'high': k.high_price,
                'low': k.low_price,
                'close': k.close_price,
                'volume': k.volume
            } for k in klines])
            
            # 計算收益率
            df['returns'] = np.log(df['close'] / df['close'].shift(1))
            
            # 計算對數波動率 (20期滾動)
            volatility = df['returns'].rolling(20).std().iloc[-1]
            log_volatility = math.log(max(volatility, 1e-9)) if not pd.isna(volatility) else -2.0
            
            # 計算價格斜率 (線性回歸斜率)
            if len(df) >= 5:
                x = np.arange(5)
                y = df['close'].iloc[-5:].values
                slope = np.polyfit(x, y, 1)[0] / y[-1]  # 正規化斜率
            else:
                slope = 0.0
            
            # 計算 RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            rsi = rsi if not pd.isna(rsi) else 50.0
            
            return {
                'log_volatility': log_volatility,
                'slope_d1': slope,
                'rsi': rsi,
                'volatility': volatility if not pd.isna(volatility) else 0.01
            }
            
        except Exception as e:
            logger.error(f"計算技術指標失敗 {symbol}: {e}")
            return {'log_volatility': -2.0, 'slope_d1': 0.0, 'rsi': 50.0}

    async def _get_orderbook_imbalance(self, symbol: str) -> float:
        """獲取訂單簿不平衡"""
        try:
            depth_data = self.market_data_service.realtime_data['depths'].get(symbol)
            if not depth_data:
                return 0.0
            
            # 計算前5檔買賣壓比
            bid_volume = sum(float(bid[1]) for bid in depth_data.get('bids', [])[:5])
            ask_volume = sum(float(ask[1]) for ask in depth_data.get('asks', [])[:5])
            
            if bid_volume + ask_volume == 0:
                return 0.0
            
            return (bid_volume - ask_volume) / (bid_volume + ask_volume)
            
        except Exception as e:
            logger.error(f"獲取訂單簿不平衡失敗 {symbol}: {e}")
            return 0.0

    async def _get_funding_rate(self, symbol: str) -> float:
        """獲取資金費率"""
        try:
            if symbol.endswith('USDT'):
                # 從交易所 API 獲取資金費率
                funding_info = await self.market_data_service.exchanges['binance'].fetch_funding_rate(symbol)
                return float(funding_info.get('fundingRate', 0.0))
            return 0.0
        except Exception as e:
            logger.error(f"獲取資金費率失敗 {symbol}: {e}")
            return 0.0

    async def _generate_hypotheses(self, symbol: str, observation: MarketObservation) -> List[TradingHypothesis]:
        """基於市場條件生成交易假設"""
        hypotheses = []
        
        # 多頭突破假設
        if observation.slope_d1 > 0.001 and observation.rsi < 70:
            hypotheses.append(TradingHypothesis(
                name=f"BULL_BREAKOUT_{symbol}",
                direction=1,
                expected_return=abs(observation.slope_d1) * 10,  # 基於斜率動態調整
                expected_risk=math.exp(observation.log_volatility),
                confidence=min(0.9, 0.5 + abs(observation.slope_d1) * 100),
                time_horizon=15
            ))
        
        # 空頭下破假設  
        if observation.slope_d1 < -0.001 and observation.rsi > 30:
            hypotheses.append(TradingHypothesis(
                name=f"BEAR_BREAKDOWN_{symbol}",
                direction=-1,
                expected_return=abs(observation.slope_d1) * 10,
                expected_risk=math.exp(observation.log_volatility),
                confidence=min(0.9, 0.5 + abs(observation.slope_d1) * 100),
                time_horizon=12
            ))
        
        # 區間震盪假設
        if abs(observation.slope_d1) < 0.0005:
            hypotheses.append(TradingHypothesis(
                name=f"RANGE_BOUND_{symbol}",
                direction=0,
                expected_return=0.002,  # 小幅套利
                expected_risk=math.exp(observation.log_volatility) * 0.5,
                confidence=0.8,
                time_horizon=5
            ))
        
        # 資金費率套利假設
        if abs(observation.funding_rate) > 0.0001:
            direction = -1 if observation.funding_rate > 0 else 1
            hypotheses.append(TradingHypothesis(
                name=f"FUNDING_ARBITRAGE_{symbol}",
                direction=direction,
                expected_return=abs(observation.funding_rate) * 24 * 3,  # 3天資金費率
                expected_risk=math.exp(observation.log_volatility) * 0.3,
                confidence=0.7,
                time_horizon=480  # 8小時
            ))
        
        return hypotheses

    async def _handle_decision(self, symbol: str, decision: Dict[str, Any]):
        """處理量子決策結果"""
        try:
            # 記錄決策
            self.decision_history[symbol].append(decision)
            if len(self.decision_history[symbol]) > 1000:
                self.decision_history[symbol].pop(0)
            
            # 日誌記錄
            logger.info(f"量子決策觸發 [{symbol}]: "
                       f"假設={decision['hypothesis'].name}, "
                       f"方向={decision['hypothesis'].direction}, "
                       f"倉位={decision['position_size']:.4f}, "
                       f"信心度={decision['confidence']:.3f}, "
                       f"期望收益={decision['expected_return']:.4f}")
            
            # 風險檢查
            if decision['position_size'] > self.config.max_position_cap:
                logger.warning(f"倉位超限 {symbol}: {decision['position_size']}")
                return
            
            # 制度概率檢查
            dominant_regime_prob = max(decision['regime_probabilities'])
            if dominant_regime_prob < 0.6:
                logger.warning(f"市場制度不明確 {symbol}: {dominant_regime_prob:.3f}")
            
            # 發送到執行引擎 (需要實現)
            await self._send_to_execution_engine(symbol, decision)
            
        except Exception as e:
            logger.error(f"處理決策失敗 {symbol}: {e}")

    async def _send_to_execution_engine(self, symbol: str, decision: Dict[str, Any]):
        """發送到交易執行引擎"""
        # TODO: 整合 Trading X 的交易執行模組
        pass

    async def start_processing(self):
        """啟動量子決策處理"""
        try:
            await self.initialize()
            
            # 啟動市場數據流
            if self.market_data_service:
                await self.market_data_service.start_streams(self.active_symbols)
            
            logger.info("量子決策處理器已啟動，監控七種主要加密貨幣")
            
        except Exception as e:
            logger.error(f"啟動處理器失敗: {e}")
            raise

# 技術指標計算器類 (需要實現)
class TechnicalIndicatorCalculator:
    """技術指標計算器"""
    def __init__(self):
        pass
