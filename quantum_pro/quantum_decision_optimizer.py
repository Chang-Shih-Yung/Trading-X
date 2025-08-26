# quantum_decision_optimizer.py
# 生產級量子決策系統 - Trading X 區塊鏈整合版本
#
# 核心優化特性:
# - 真實區塊鏈七幣種數據整合 (BTC/ETH/ADA/SOL/XRP/DOGE/BNB)
# - 生產級 SPRT 決策閾值動態調整
# - Kelly 資金管理 + 多制度風險評估
# - 向量化假設似然計算 
# - 實時制度切換偵測與響應
# - 無模擬數據，純數學計算

import asyncio
import logging
import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import digamma, logsumexp
from scipy.stats import t as student_t

# Trading X 整合導入
try:
    from app.core.config import settings
    from app.services.binance_websocket import BinanceDataCollector
    from app.services.market_data import MarketDataService
except ImportError:
    # 開發環境回退
    BinanceDataCollector = None
    MarketDataService = None
    settings = None

# 修正導入路徑 - 導入新的類別
try:
    from .regime_hmm_quantum import (
        EmissionParams, 
        TimeVaryingHMM,
        即時幣安數據收集器,
        TradingX信號輸出器,
        即時市場觀測,
        TradingX信號,
        QuantumSignalSelector
    )
except ImportError:
    from regime_hmm_quantum import (
        EmissionParams, 
        TimeVaryingHMM,
        即時幣安數據收集器,
        TradingX信號輸出器,
        即時市場觀測,
        TradingX信號,
        QuantumSignalSelector
    )

# 配置專業級日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ProductionQuantumConfig:
    """生產級量子決策配置 - 針對加密貨幣優化"""
    # SPRT 動態參數
    alpha_base: float = 0.01          # 基礎 Type-I 錯誤率  
    beta_base: float = 0.05           # 基礎 Type-II 錯誤率
    alpha_volatility_adj: float = 2.0 # 波動率調整係數
    beta_confidence_adj: float = 1.5  # 信心度調整係數
    
    # 信念更新優化
    forgetting_factor: float = 0.995  # 高保真遺忘因子
    regime_update_freq: int = 30      # 制度更新頻率（秒）
    belief_update_threshold: float = 0.001  # 信念更新閾值
    
    # Kelly 位置管理進階參數
    kelly_multiplier: float = 0.15    # 保守 Kelly 倍數
    max_single_position: float = 0.08 # 單幣種最大倉位
    portfolio_heat: float = 0.25      # 組合總熱度上限
    drawdown_protection: float = 0.03 # 回撤保護閾值
    
    # 風險管理矩陣
    volatility_regime_threshold: float = 0.04  # 高波動制度閾值
    correlation_decay_factor: float = 0.98     # 相關性衰減因子
    regime_confidence_min: float = 0.6         # 最低制度信心度
    
    # 區塊鏈七幣種配置
    primary_symbols: List[str] = field(default_factory=lambda: [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 
        'XRPUSDT', 'DOGEUSDT', 'ADAUSDT'
    ])
    
    # 特徵工程參數
    feature_lookback: int = 50        # 特徵計算回望期
    regime_features: List[str] = field(default_factory=lambda: [
        'momentum_slope', 'realized_volatility', 'orderbook_pressure'
    ])
    
    # 執行配置
    min_trade_interval: int = 120     # 最小交易間隔（秒）
    position_update_freq: int = 10    # 倉位更新頻率（秒）
    emergency_stop_threshold: float = -0.15  # 緊急停損閾值

@dataclass
class CryptoMarketObservation:
    """加密貨幣市場觀測結構 - 純真實數據"""
    timestamp: pd.Timestamp
    symbol: str
    # 核心市場數據
    price: float
    returns: float
    volume_24h: float
    market_cap: Optional[float]
    
    # 技術指標（基於真實計算）
    realized_volatility: float    # 已實現波動率
    momentum_slope: float         # 動量斜率
    rsi_14: float                # 14期 RSI
    bb_position: float           # 布林帶位置
    
    # 市場微觀結構
    orderbook_pressure: float    # 訂單簿壓力
    bid_ask_spread: float        # 買賣價差
    trade_aggression: float      # 交易主動性
    
    # 鏈上與資金數據  
    funding_rate: float          # 資金費率
    open_interest: float         # 未平倉量
    liquidation_ratio: float     # 清算比率
    
    # 網路效應指標
    social_sentiment: float      # 社交情緒（如果可獲得）
    whale_activity: float        # 大戶活動指標
    
    # 輔助數據
    correlation_btc: float       # 與 BTC 相關性
    market_regime_signal: float  # 市場制度信號

@dataclass  
class ProductionTradingHypothesis:
    """生產級交易假設 - 數學精確定義"""
    symbol: str
    hypothesis_id: str           # 唯一識別符
    direction: int               # 1: long, -1: short, 0: neutral
    
    # 收益預期（基於數學模型）
    expected_return_1h: float    # 1小時期望收益
    expected_return_4h: float    # 4小時期望收益  
    expected_return_24h: float   # 24小時期望收益
    
    # 風險評估
    value_at_risk_95: float      # 95% VaR
    expected_shortfall: float    # 期望缺口
    max_adverse_excursion: float # 最大不利偏移
    
    # 執行參數
    optimal_timeframe: str       # 最佳時間框架
    entry_confidence: float      # 入場信心度
    exit_conditions: Dict[str, float]  # 出場條件
    
    # 制度依賴性
    regime_dependency: np.ndarray  # 對各制度的依賴程度 (M,)
    regime_performance: Dict[int, float]  # 各制度下的歷史表現

class ProductionQuantumEngine:
    """生產級量子決策引擎 - 零模擬數據版本"""
    
    def __init__(self, config: ProductionQuantumConfig):
        self.config = config
        
        # 初始化時變 HMM（每個幣種獨立）
        self.hmm_models = {}
        for symbol in config.primary_symbols:
            self.hmm_models[symbol] = TimeVaryingHMM(
                n_states=6,  # 6種市場制度
                z_dim=len(config.regime_features),
                reg_lambda=1e-4,  # 較強正則化
                rng_seed=hash(symbol) % 2**31  # 每個幣種不同的種子
            )
        
        # 信念狀態管理（每個幣種獨立）
        self.belief_states = {symbol: {} for symbol in config.primary_symbols}
        self.log_odds_histories = {symbol: [] for symbol in config.primary_symbols}
        
        # 動態 SPRT 閾值  
        self.dynamic_sprt_thresholds = {}
        self._update_sprt_thresholds()
        
        # 市場數據緩存
        self.observation_buffers = {symbol: [] for symbol in config.primary_symbols}
        self.regime_probabilities = {symbol: np.ones(6) / 6 for symbol in config.primary_symbols}
        
        # 相關性矩陣管理
        self.correlation_matrix = np.eye(len(config.primary_symbols))
        self.correlation_history = []
        
        # 執行狀態追蹤
        self.active_positions = {}  # {symbol: {size, entry_time, hypothesis_id}}
        self.execution_stats = {
            'total_signals': 0,
            'executed_trades': 0,
            'avg_hold_time': 0.0,
            'success_rate': 0.0,
            'total_return': 0.0
        }
        
        # 性能監控
        self.processing_times = {'observation': [], 'decision': [], 'execution': []}
        
    def _update_sprt_thresholds(self):
        """動態更新 SPRT 閾值基於市場條件"""
        for symbol in self.config.primary_symbols:
            # 基於歷史波動率調整 alpha
            if symbol in self.observation_buffers and len(self.observation_buffers[symbol]) > 20:
                recent_returns = [obs.returns for obs in self.observation_buffers[symbol][-20:]]
                volatility = np.std(recent_returns)
                
                # 波動率越高，決策越保守
                adjusted_alpha = self.config.alpha_base * (1 + volatility * self.config.alpha_volatility_adj)
                adjusted_beta = self.config.beta_base * (1 + volatility * self.config.beta_confidence_adj)
            else:
                adjusted_alpha = self.config.alpha_base
                adjusted_beta = self.config.beta_base
            
            # 限制在合理範圍內
            adjusted_alpha = np.clip(adjusted_alpha, 0.001, 0.1)
            adjusted_beta = np.clip(adjusted_beta, 0.01, 0.3)
            
            self.dynamic_sprt_thresholds[symbol] = {
                'upper': math.log((1 - adjusted_beta) / adjusted_alpha),
                'lower': math.log(adjusted_beta / (1 - adjusted_alpha)),
                'alpha': adjusted_alpha,
                'beta': adjusted_beta
            }

    def _extract_advanced_features(self, obs: CryptoMarketObservation) -> np.ndarray:
        """提取進階特徵向量 - 純數學計算"""
        features = []
        
        # 特徵 1: 正規化動量斜率
        momentum_feature = np.tanh(obs.momentum_slope * 1000)  # 縮放到 [-1, 1]
        features.append(momentum_feature)
        
        # 特徵 2: 波動率制度指標
        vol_feature = np.log(max(obs.realized_volatility, 1e-6)) 
        features.append(vol_feature)
        
        # 特徵 3: 訂單簿壓力（正規化）
        pressure_feature = np.tanh(obs.orderbook_pressure)
        features.append(pressure_feature)
        
        return np.array(features)

    def _update_regime_probabilities_vectorized(self, symbol: str, obs: CryptoMarketObservation):
        """向量化制度概率更新 - 優化版本"""
        if len(self.observation_buffers[symbol]) < 10:
            return
        
        # 構建最近觀測的序列
        recent_obs = self.observation_buffers[symbol][-min(100, len(self.observation_buffers[symbol])):]
        
        # 向量化構建觀測矩陣
        x_seq = {
            'ret': np.array([o.returns for o in recent_obs]),
            'logvol': np.array([math.log(max(o.realized_volatility, 1e-6)) for o in recent_obs]),
            'slope': np.array([o.momentum_slope for o in recent_obs]),
            'ob': np.array([o.orderbook_pressure for o in recent_obs])
        }
        
        z_seq = np.array([self._extract_advanced_features(o) for o in recent_obs])
        
        try:
            # 使用優化的 forward 算法
            start_time = time.time()
            log_alpha, _ = self.hmm_models[symbol].forward_log(x_seq, z_seq)
            
            # 更新制度概率（濾波）
            self.regime_probabilities[symbol] = np.exp(log_alpha[-1])
            
            # 記錄處理時間
            processing_time = time.time() - start_time
            self.processing_times['observation'].append(processing_time)
            
        except Exception as e:
            logger.warning(f"制度更新失敗 {symbol}: {e}")

    def _compute_vectorized_hypothesis_likelihoods(self, 
                                                   symbol: str,
                                                   obs: CryptoMarketObservation,
                                                   hypotheses: List[ProductionTradingHypothesis]) -> np.ndarray:
        """向量化假設似然計算 - 高性能版本"""
        n_hypotheses = len(hypotheses)
        n_regimes = 6
        
        # 預分配結果矩陣
        regime_likelihoods = np.zeros((n_hypotheses, n_regimes))
        
        # 獲取 HMM 發射參數
        emissions = self.hmm_models[symbol].emissions
        
        for h_idx, hypothesis in enumerate(hypotheses):
            for r_idx in range(n_regimes):
                ep = emissions[r_idx]
                
                # 向量化 likelihood 計算
                # 1. 收益率 likelihood (Student-t)
                ret_ll = self._vectorized_student_t_logpdf(
                    obs.returns, ep.mu_ret, ep.sigma_ret, ep.nu_ret
                )
                
                # 2. 波動率 likelihood
                vol_ll = self._vectorized_gaussian_logpdf(
                    math.log(max(obs.realized_volatility, 1e-6)),
                    ep.mu_logvol, ep.sigma_logvol
                )
                
                # 3. 動量 likelihood
                slope_ll = self._vectorized_gaussian_logpdf(
                    obs.momentum_slope, ep.mu_slope, ep.sigma_slope
                )
                
                # 4. 訂單簿 likelihood（方向調整）
                ob_ll = self._direction_adjusted_likelihood(
                    obs.orderbook_pressure, ep.ob_loc, ep.ob_scale, hypothesis.direction
                )
                
                # 5. 制度一致性獎勵
                regime_bonus = self._compute_regime_consistency_bonus(
                    obs, hypothesis, r_idx
                )
                
                # 組合 log-likelihood
                total_ll = ret_ll + vol_ll + slope_ll + ob_ll + regime_bonus
                regime_likelihoods[h_idx, r_idx] = total_ll
        
        # 加權組合（使用制度概率）
        regime_probs = self.regime_probabilities[symbol]
        
        # 計算加權似然: L_k = sum_r P(regime=r) * exp(log_likelihood_kr)
        weighted_likelihoods = np.zeros(n_hypotheses)
        for h_idx in range(n_hypotheses):
            # 數值穩定的 log-sum-exp
            max_ll = np.max(regime_likelihoods[h_idx])
            exp_lls = np.exp(regime_likelihoods[h_idx] - max_ll)
            weighted_likelihoods[h_idx] = max_ll + math.log(np.dot(regime_probs, exp_lls) + 1e-300)
        
        return weighted_likelihoods

    def _vectorized_student_t_logpdf(self, x: float, mu: float, sigma: float, nu: float) -> float:
        """向量化 Student-t 對數概率密度"""
        sigma = max(sigma, 1e-9)
        nu = max(nu, 2.1)
        z = (x - mu) / sigma
        
        # 使用 math.lgamma 計算
        a = math.lgamma((nu + 1.0) / 2.0) - math.lgamma(nu / 2.0)
        b = -0.5 * math.log(nu * math.pi) - math.log(sigma)
        c = -(nu + 1.0) / 2.0 * math.log1p((z * z) / nu)
        
        return a + b + c

    def _vectorized_gaussian_logpdf(self, x: float, mu: float, sigma: float) -> float:
        """向量化高斯對數概率密度"""
        sigma = max(sigma, 1e-9)
        return -0.5 * math.log(2 * math.pi) - math.log(sigma) - 0.5 * ((x - mu) ** 2) / (sigma ** 2)

    def _direction_adjusted_likelihood(self, x: float, mu: float, sigma: float, direction: int) -> float:
        """方向調整的似然函數"""
        base_ll = self._vectorized_gaussian_logpdf(x, mu, sigma)
        
        # 方向一致性獎勵/懲罰
        if direction != 0:
            consistency = (x > 0 and direction > 0) or (x < 0 and direction < 0)
            adjustment = 0.2 if consistency else -0.1
            return base_ll + adjustment
        
        return base_ll

    def _compute_regime_consistency_bonus(self, 
                                        obs: CryptoMarketObservation,
                                        hypothesis: ProductionTradingHypothesis,
                                        regime_idx: int) -> float:
        """計算制度一致性獎勵 - 基於數學特徵"""
        bonus = 0.0
        
        # RSI 制度一致性
        if regime_idx in [0, 3]:  # 牛市/低波動制度
            if hypothesis.direction > 0 and obs.rsi_14 < 70:
                bonus += 0.1 * (70 - obs.rsi_14) / 70  # RSI 越低獎勵越高
        elif regime_idx in [1, 5]:  # 熊市/高波動制度
            if hypothesis.direction < 0 and obs.rsi_14 > 30:
                bonus += 0.1 * (obs.rsi_14 - 30) / 70  # RSI 越高獎勵越高
        
        # 波動率制度一致性
        if regime_idx == 2:  # 高波動制度
            if obs.realized_volatility > self.config.volatility_regime_threshold:
                bonus += 0.05
        elif regime_idx == 3:  # 低波動制度
            if obs.realized_volatility < self.config.volatility_regime_threshold:
                bonus += 0.05
        
        # 動量制度一致性
        if abs(obs.momentum_slope) > 0.001:
            if (obs.momentum_slope > 0 and hypothesis.direction > 0) or \
               (obs.momentum_slope < 0 and hypothesis.direction < 0):
                bonus += 0.08 * min(abs(obs.momentum_slope) * 1000, 1.0)
        
        return bonus

    def _update_belief_state_optimized(self, 
                                     symbol: str,
                                     log_likelihoods: np.ndarray,
                                     hypotheses: List[ProductionTradingHypothesis]):
        """優化的信念狀態更新 - 向量化實現"""
        if symbol not in self.belief_states:
            self.belief_states[symbol] = {}
        
        # 初始化信念（如果需要）
        belief_state = self.belief_states[symbol]
        hypothesis_names = [h.hypothesis_id for h in hypotheses]
        
        if not belief_state:
            # 均勻初始化
            for name in hypothesis_names:
                belief_state[name] = 1.0 / len(hypothesis_names)
        
        # 向量化信念更新
        n_hyp = len(hypotheses)
        if n_hyp == 0:
            return
        
        # 獲取先驗信念
        prior_beliefs = np.array([belief_state.get(name, 1.0/n_hyp) for name in hypothesis_names])
        
        # 似然正規化
        max_ll = np.max(log_likelihoods)
        normalized_likelihoods = np.exp(log_likelihoods - max_ll)
        normalized_likelihoods /= (np.sum(normalized_likelihoods) + 1e-300)
        
        # 貝葉斯更新
        posterior_unnormalized = prior_beliefs * normalized_likelihoods
        posterior_beliefs = posterior_unnormalized / (np.sum(posterior_unnormalized) + 1e-300)
        
        # 應用遺忘因子
        forgetting = self.config.forgetting_factor
        updated_beliefs = forgetting * posterior_beliefs + (1 - forgetting) * prior_beliefs
        
        # 更新信念狀態
        for i, name in enumerate(hypothesis_names):
            if updated_beliefs[i] > self.config.belief_update_threshold:
                belief_state[name] = float(updated_beliefs[i])
        
        # 清理過小的信念
        to_remove = [name for name, belief in belief_state.items() 
                    if belief < self.config.belief_update_threshold]
        for name in to_remove:
            del belief_state[name]
        
        # 重新正規化
        total_belief = sum(belief_state.values())
        if total_belief > 0:
            for name in belief_state:
                belief_state[name] /= total_belief

    def _apply_dynamic_sprt_decision(self, 
                                    symbol: str,
                                    hypotheses: List[ProductionTradingHypothesis]) -> Optional[ProductionTradingHypothesis]:
        """應用動態 SPRT 決策規則"""
        belief_state = self.belief_states.get(symbol, {})
        if len(belief_state) < 2:
            return None
        
        # 獲取動態閾值
        thresholds = self.dynamic_sprt_thresholds.get(symbol, {
            'upper': math.log(19), 'lower': math.log(1/19)
        })
        
        # 排序信念
        sorted_beliefs = sorted(belief_state.items(), key=lambda x: x[1], reverse=True)
        top_name, top_belief = sorted_beliefs[0]
        second_belief = sorted_beliefs[1][1] if len(sorted_beliefs) > 1 else 0.01
        
        # 計算對數勝算比
        if second_belief > 1e-10:
            log_odds_ratio = math.log(top_belief / second_belief)
        else:
            log_odds_ratio = thresholds['upper'] + 1  # 強制觸發
        
        # SPRT 決策邏輯
        if log_odds_ratio >= thresholds['upper']:
            # 找到對應假設
            selected_hypothesis = next(
                (h for h in hypotheses if h.hypothesis_id == top_name), None
            )
            
            if selected_hypothesis:
                # 額外檢查：制度信心度
                regime_confidence = np.max(self.regime_probabilities[symbol])
                if regime_confidence >= self.config.regime_confidence_min:
                    return selected_hypothesis
                else:
                    logger.info(f"制度信心度不足 {symbol}: {regime_confidence:.3f}")
        
        elif log_odds_ratio <= thresholds['lower']:
            # 重置信念狀態
            logger.info(f"SPRT 下閾值觸發，重置信念 {symbol}")
            self.belief_states[symbol] = {}
        
        return None

    def _compute_kelly_position_advanced(self, 
                                       symbol: str,
                                       hypothesis: ProductionTradingHypothesis) -> float:
        """進階 Kelly 倉位計算 - 考慮制度和相關性"""
        if len(self.observation_buffers[symbol]) < 20:
            return 0.0
        
        # 計算期望收益（制度加權）
        regime_probs = self.regime_probabilities[symbol]
        expected_returns = []
        
        for regime_idx in range(6):
            regime_er = hypothesis.regime_performance.get(regime_idx, hypothesis.expected_return_1h)
            expected_returns.append(regime_er)
        
        weighted_er = np.dot(regime_probs, expected_returns)
        
        if weighted_er <= 0:
            return 0.0
        
        # 計算制度加權方差
        recent_returns = [obs.returns for obs in self.observation_buffers[symbol][-20:]]
        historical_variance = np.var(recent_returns)
        
        # VaR 調整
        var_adjustment = max(1.0 - hypothesis.value_at_risk_95 / abs(weighted_er), 0.1)
        
        # Kelly 公式
        kelly_fraction = (weighted_er * var_adjustment) / (historical_variance + 1e-9)
        
        # 應用倍數和限制
        position_size = kelly_fraction * self.config.kelly_multiplier
        position_size = min(position_size, self.config.max_single_position)
        
        # 組合熱度檢查
        current_heat = sum(abs(pos['size']) for pos in self.active_positions.values())
        if current_heat + abs(position_size) > self.config.portfolio_heat:
            position_size *= max(0.1, (self.config.portfolio_heat - current_heat) / abs(position_size))
        
        return max(0.0, position_size)

    async def process_observation_production(self, 
                                           obs: CryptoMarketObservation,
                                           hypotheses: List[ProductionTradingHypothesis]) -> Optional[Dict[str, Any]]:
        """生產級觀測處理 - 完整優化流程"""
        symbol = obs.symbol
        start_time = time.time()
        
        try:
            # 1. 數據驗證
            if not self._validate_observation(obs):
                return None
            
            # 2. 添加到緩存
            self.observation_buffers[symbol].append(obs)
            if len(self.observation_buffers[symbol]) > 500:  # 控制記憶體
                self.observation_buffers[symbol].pop(0)
            
            # 3. 更新制度概率（向量化）
            self._update_regime_probabilities_vectorized(symbol, obs)
            
            # 4. 計算假設似然（向量化）
            log_likelihoods = self._compute_vectorized_hypothesis_likelihoods(
                symbol, obs, hypotheses
            )
            
            # 5. 更新信念狀態（優化版本）
            self._update_belief_state_optimized(symbol, log_likelihoods, hypotheses)
            
            # 6. 應用動態 SPRT 決策
            selected_hypothesis = self._apply_dynamic_sprt_decision(symbol, hypotheses)
            
            if selected_hypothesis:
                # 7. 計算進階 Kelly 倉位
                position_size = self._compute_kelly_position_advanced(symbol, selected_hypothesis)
                
                if position_size > 0.001:  # 最小倉位過濾
                    # 8. 構建決策結果
                    decision = self._build_production_decision(
                        obs, selected_hypothesis, position_size
                    )
                    
                    # 9. 更新執行統計
                    self.execution_stats['total_signals'] += 1
                    
                    # 10. 記錄處理時間
                    processing_time = time.time() - start_time
                    self.processing_times['decision'].append(processing_time)
                    
                    return decision
            
        except Exception as e:
            logger.error(f"處理觀測失敗 {symbol}: {e}")
            return None
        
        return None

    def _validate_observation(self, obs: CryptoMarketObservation) -> bool:
        """數據驗證 - 確保數據品質"""
        # 基本數值檢查
        if not all(np.isfinite([obs.price, obs.returns, obs.realized_volatility])):
            logger.warning(f"無效數值在觀測 {obs.symbol}")
            return False
        
        # 價格合理性檢查
        if obs.price <= 0:
            logger.warning(f"無效價格 {obs.symbol}: {obs.price}")
            return False
        
        # 收益率異常檢查
        if abs(obs.returns) > 0.5:  # 50% 日內變動視為異常
            logger.warning(f"異常收益率 {obs.symbol}: {obs.returns}")
            return False
        
        # 波動率合理性檢查  
        if obs.realized_volatility < 0 or obs.realized_volatility > 5.0:
            logger.warning(f"異常波動率 {obs.symbol}: {obs.realized_volatility}")
            return False
        
        return True

    def _build_production_decision(self, 
                                 obs: CryptoMarketObservation,
                                 hypothesis: ProductionTradingHypothesis,
                                 position_size: float) -> Dict[str, Any]:
        """構建生產級決策結果"""
        belief_state = self.belief_states.get(obs.symbol, {})
        
        return {
            'timestamp': obs.timestamp,
            'symbol': obs.symbol,
            'hypothesis': hypothesis,
            'position_size': position_size,
            'confidence': belief_state.get(hypothesis.hypothesis_id, 0.0),
            'regime_probabilities': self.regime_probabilities[obs.symbol].copy(),
            'dominant_regime': int(np.argmax(self.regime_probabilities[obs.symbol])),
            'regime_confidence': float(np.max(self.regime_probabilities[obs.symbol])),
            'expected_return_1h': hypothesis.expected_return_1h,
            'value_at_risk_95': hypothesis.value_at_risk_95,
            'sprt_thresholds': self.dynamic_sprt_thresholds.get(obs.symbol, {}),
            'market_conditions': {
                'volatility': obs.realized_volatility,
                'momentum': obs.momentum_slope,
                'orderbook_pressure': obs.orderbook_pressure,
                'rsi': obs.rsi_14,
                'funding_rate': obs.funding_rate
            },
            'execution_metadata': {
                'belief_state_size': len(belief_state),
                'buffer_size': len(self.observation_buffers[obs.symbol]),
                'portfolio_heat': sum(abs(pos['size']) for pos in self.active_positions.values())
            }
        }

    def get_production_state(self) -> Dict[str, Any]:
        """獲取完整的生產狀態快照"""
        return {
            'belief_states': {k: v.copy() for k, v in self.belief_states.items()},
            'regime_probabilities': {k: v.copy() for k, v in self.regime_probabilities.items()},
            'active_positions': self.active_positions.copy(),
            'execution_stats': self.execution_stats.copy(),
            'sprt_thresholds': self.dynamic_sprt_thresholds.copy(),
            'buffer_sizes': {k: len(v) for k, v in self.observation_buffers.items()},
            'correlation_matrix': self.correlation_matrix.copy(),
            'processing_performance': {
                'avg_observation_time': np.mean(self.processing_times['observation']) if self.processing_times['observation'] else 0.0,
                'avg_decision_time': np.mean(self.processing_times['decision']) if self.processing_times['decision'] else 0.0,
                'total_observations': sum(len(buf) for buf in self.observation_buffers.values())
            }
        }


# 生產級量子決策處理器 - 已遷移到 quantum_production_extension.py
# 此類已被 TradingXQuantumProcessor 取代，請使用 quantum_production_extension 模組
