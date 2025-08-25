# regime_hmm_quantum.py
# Time-varying HMM - Production Optimized Version for Trading X
# 
# 核心優化特性:
# - 向量化 forward/backward 計算
# - Transition matrix 快取 (A_cache, logA_cache)
# - Per-row 加權 multinomial-logit M-step (L-BFGS)
# - 加權 Student-t nu 數值估計
# - Viterbi & smoothed posterior 輸出  
# - 系統化重採樣粒子濾波
# - 生產級數值穩定性
#
# Trading X 區塊鏈主池七幣種: BTC/ETH/ADA/SOL/XRP/DOGE/BNB
# Dependencies: numpy, scipy

import math
import time
import warnings
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy.optimize import minimize
from scipy.special import digamma, logsumexp

warnings.filterwarnings("ignore", category=RuntimeWarning)

# --------------------------
# 核心 PDF 計算函數 (向量化)
# --------------------------

def student_t_logpdf(x: np.ndarray, mu: float, sigma: float, nu: float) -> np.ndarray:
    """向量化 Student-t 對數 PDF - 處理加密貨幣厚尾分布"""
    sigma = max(sigma, 1e-9)
    nu = max(nu, 2.1)
    z = (x - mu) / sigma
    a = math.lgamma((nu + 1.0) / 2.0) - math.lgamma(nu / 2.0)
    b = -0.5 * math.log(nu * math.pi) - math.log(sigma)
    c = -(nu + 1.0) / 2.0 * np.log1p((z * z) / nu)
    return a + b + c

def gaussian_logpdf(x: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    """向量化高斯對數 PDF"""
    sigma = max(sigma, 1e-9)
    return -0.5 * np.log(2 * math.pi) - np.log(sigma) - 0.5 * ((x - mu) ** 2) / (sigma ** 2)

# --------------------------
# 發射參數結構
# --------------------------

@dataclass
class EmissionParams:
    """市場制度發射參數 - 對應不同市場狀態的統計特徵"""
    mu_ret: float      # 收益率均值
    sigma_ret: float   # 收益率標準差
    nu_ret: float      # Student-t 自由度 (厚尾參數)
    mu_logvol: float   # 對數波動率均值
    sigma_logvol: float # 對數波動率標準差  
    mu_slope: float    # 價格斜率均值
    sigma_slope: float # 價格斜率標準差
    ob_loc: float      # 訂單簿不平衡位置參數
    ob_scale: float    # 訂單簿不平衡尺度參數

# --------------------------
# 生產級時變隱馬可夫模型
# --------------------------

class TimeVaryingHMM:
    """
    生產級時變 HMM 引擎
    
    特性:
    - 時變轉移矩陣: A_t[i,j] = softmax(b_{ij} + w_{ij}^T z_t)
    - Student-t 厚尾發射分布
    - 向量化 forward/backward 算法
    - 快取優化的轉移矩陣計算
    - 數值穩定的 EM 訓練
    """
    
    def __init__(self, 
                 n_states: int = 6, 
                 z_dim: int = 3, 
                 reg_lambda: float = 1e-3, 
                 rng_seed: int = 42):
        """
        初始化時變 HMM
        
        Args:
            n_states: 市場制度數量 (對應 6 種狀態)
            z_dim: 協變量維度 (slope, volatility, orderbook)
            reg_lambda: L2 正則化係數
            rng_seed: 隨機種子
        """
        self.M = n_states
        self.z_dim = z_dim
        self.reg_lambda = reg_lambda
        rng = np.random.RandomState(rng_seed)
        
        # 轉移參數: b (M x M), w (M x M x z_dim)
        self.b = rng.normal(scale=0.01, size=(self.M, self.M))
        self.w = rng.normal(scale=0.01, size=(self.M, self.M, self.z_dim))
        
        # 初始狀態分布 (對數空間)
        self.log_pi = np.log(np.ones(self.M) / self.M)
        
        # 發射參數初始化
        self.emissions: List[EmissionParams] = []
        for i in range(self.M):
            ep = EmissionParams(
                mu_ret=rng.normal(scale=1e-3),
                sigma_ret=0.01 + rng.uniform() * 0.05,
                nu_ret=5.0 + rng.uniform() * 5.0,
                mu_logvol=-2.0 + rng.normal(scale=0.2),
                sigma_logvol=0.5 + rng.uniform() * 0.5,
                mu_slope=rng.normal(scale=1e-3),
                sigma_slope=0.005 + rng.uniform() * 0.02,
                ob_loc=rng.normal(scale=0.1),
                ob_scale=0.5 + rng.uniform() * 0.5
            )
            self.emissions.append(ep)
        
        # 性能優化快取
        self.A_cache = None
        self.logA_cache = None
        self.last_z_seq_hash = None

    # --------------------------
    # 轉移矩陣計算 (向量化 + 快取)
    # --------------------------
    
    def _compute_z_seq_hash(self, z_seq: np.ndarray) -> int:
        """計算 z_seq 的雜湊值用於快取驗證"""
        return hash(z_seq.tobytes())
    
    def compute_A_cache(self, z_seq: np.ndarray):
        """
        計算並快取整個序列的轉移矩陣
        
        公式: A_t[i,j] = softmax_j(b_{ij} + w_{ij}^T z_t)
        """
        T = z_seq.shape[0]
        z_hash = self._compute_z_seq_hash(z_seq)
        
        # 檢查快取是否有效
        if (self.A_cache is not None and 
            self.last_z_seq_hash == z_hash and 
            self.A_cache.shape[0] == T):
            return
        
        # 重新計算快取
        A_cache = np.zeros((T, self.M, self.M))
        logA_cache = np.zeros((T, self.M, self.M))
        
        # 向量化計算所有時間點的轉移矩陣
        for t in range(T):
            zt = z_seq[t]  # shape: (z_dim,)
            # 使用 tensordot 進行高效矩陣乘法
            logits = self.b + np.tensordot(self.w, zt, axes=([2], [0]))  # shape: (M, M)
            
            # 數值穩定的 softmax (按行)
            row_max = logits.max(axis=1, keepdims=True)
            exp_logits = np.exp(logits - row_max)
            A = exp_logits / (exp_logits.sum(axis=1, keepdims=True) + 1e-300)
            
            A_cache[t] = A
            logA_cache[t] = np.log(A + 1e-300)
        
        self.A_cache = A_cache
        self.logA_cache = logA_cache
        self.last_z_seq_hash = z_hash

    def get_transition_matrix(self, z_t: np.ndarray, t_idx: int = None) -> np.ndarray:
        """獲取指定時間點的轉移矩陣"""
        if self.A_cache is not None and t_idx is not None and t_idx < self.A_cache.shape[0]:
            return self.A_cache[t_idx]
        
        # 實時計算單個轉移矩陣
        logits = self.b + np.tensordot(self.w, z_t, axes=([2], [0]))
        row_max = logits.max(axis=1, keepdims=True)
        exp_logits = np.exp(logits - row_max)
        return exp_logits / (exp_logits.sum(axis=1, keepdims=True) + 1e-300)

    # --------------------------
    # 發射概率計算 (向量化)
    # --------------------------
    
    def log_emission_matrix(self, x_seq: Dict[str, np.ndarray]) -> np.ndarray:
        """
        計算所有狀態和時間點的發射對數概率
        
        Args:
            x_seq: 觀測序列字典，包含 'ret', 'logvol', 'slope', 'ob'
            
        Returns:
            log_em: 形狀 (M, T) 的發射對數概率矩陣
        """
        T = x_seq['ret'].shape[0]
        log_em = np.zeros((self.M, T))
        
        for h in range(self.M):
            ep = self.emissions[h]
            
            # Student-t 分布用於收益率 (處理厚尾)
            l_ret = student_t_logpdf(x_seq['ret'], ep.mu_ret, ep.sigma_ret, ep.nu_ret)
            
            # 高斯分布用於其他觀測變量
            l_vol = gaussian_logpdf(x_seq['logvol'], ep.mu_logvol, ep.sigma_logvol)
            l_slope = gaussian_logpdf(x_seq['slope'], ep.mu_slope, ep.sigma_slope)
            
            # 訂單簿不平衡的特殊處理
            ob_diff = x_seq['ob'] - ep.ob_loc
            l_ob = (-0.5 * (ob_diff ** 2) / (max(ep.ob_scale, 1e-9) ** 2) - 
                    math.log(max(ep.ob_scale, 1e-9)) - 
                    0.5 * math.log(2 * math.pi))
            
            # 組合所有觀測的對數概率
            log_em[h, :] = l_ret + l_vol + l_slope + l_ob
            
        return log_em

    # --------------------------
    # Forward 算法 (向量化 + 數值穩定)
    # --------------------------
    
    def forward_log(self, x_seq: Dict[str, np.ndarray], z_seq: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        向量化 Forward 算法 (對數空間)
        
        Returns:
            log_alpha: 正規化的前向概率 (T x M)
            log_c: 正規化常數序列 (T,)
        """
        T = x_seq['ret'].shape[0]
        
        # 預計算發射概率矩陣
        log_em = self.log_emission_matrix(x_seq)  # (M, T)
        
        # 確保轉移矩陣快取
        self.compute_A_cache(z_seq)
        logA_cache = self.logA_cache  # (T, M, M)
        
        # 初始化
        log_alpha = np.full((T, self.M), -np.inf)
        log_c = []
        
        # t=0: 初始化
        log_alpha[0, :] = self.log_pi + log_em[:, 0]
        c0 = logsumexp(log_alpha[0, :])
        log_alpha[0, :] -= c0
        log_c.append(c0)
        
        # t=1...T-1: 遞推計算
        for t in range(1, T):
            # 向量化計算: log_alpha[t-1, i] + log(A[t, i, j]) for all i,j
            # 形狀: (M, 1) + (M, M) -> (M, M), 然後沿 axis=0 求 logsumexp
            prev_alpha = log_alpha[t-1, :][:, None]  # (M, 1)
            transition_logits = prev_alpha + logA_cache[t]  # (M, M)
            
            # 沿來源狀態維度求 logsumexp
            forward_probs = logsumexp(transition_logits, axis=0)  # (M,)
            
            # 加上發射概率
            log_alpha[t, :] = log_em[:, t] + forward_probs
            
            # 正規化
            ct = logsumexp(log_alpha[t, :])
            log_alpha[t, :] -= ct
            log_c.append(ct)
        
        return log_alpha, np.array(log_c)

    # --------------------------
    # Backward 算法 (向量化)
    # --------------------------
    
    def backward_log(self, x_seq: Dict[str, np.ndarray], z_seq: np.ndarray) -> np.ndarray:
        """
        向量化 Backward 算法 (對數空間)
        
        Returns:
            log_beta: 後向概率 (T x M)
        """
        T = x_seq['ret'].shape[0]
        
        # 預計算發射概率矩陣
        log_em = self.log_emission_matrix(x_seq)
        
        # 確保轉移矩陣快取
        if self.logA_cache is None or self.logA_cache.shape[0] != T:
            self.compute_A_cache(z_seq)
        logA_cache = self.logA_cache
        
        # 初始化
        log_beta = np.full((T, self.M), -np.inf)
        log_beta[-1, :] = 0.0  # log(1)
        
        # 反向遞推
        for t in range(T - 2, -1, -1):
            # 使用 t+1 時刻的轉移矩陣
            logA_next = logA_cache[t + 1]  # (M, M) i->j
            
            # 向量化計算: log(A[i,j]) + log_em[j,t+1] + log_beta[t+1,j]
            emission_beta = log_em[:, t + 1] + log_beta[t + 1, :]  # (M,)
            transition_emission = logA_next + emission_beta[None, :]  # (M, M)
            
            # 沿目標狀態維度求 logsumexp
            log_beta[t, :] = logsumexp(transition_emission, axis=1)
        
        return log_beta

    # --------------------------
    # 後驗計算 (完整 xi 矩陣)
    # --------------------------
    
    def compute_posteriors_full_xi(self, 
                                   log_alpha: np.ndarray, 
                                   log_beta: np.ndarray, 
                                   z_seq: np.ndarray, 
                                   x_seq: Dict[str, np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
        """
        計算完整的後驗概率
        
        Returns:
            gamma: 單點後驗 P(H_t=h|x_{1:T}) (T x M)
            xi_t: 配對後驗 P(H_t=i, H_{t+1}=j|x_{1:T}) (T-1 x M x M)
        """
        T = log_alpha.shape[0]
        
        # 計算 gamma (單點後驗)
        log_gamma = log_alpha + log_beta
        for t in range(T):
            log_gamma[t, :] -= logsumexp(log_gamma[t, :])
        gamma = np.exp(log_gamma)
        
        # 計算 xi (配對後驗)
        if self.logA_cache is None or self.logA_cache.shape[0] != T:
            self.compute_A_cache(z_seq)
        logA_cache = self.logA_cache
        log_em = self.log_emission_matrix(x_seq)
        
        xi_t = np.zeros((T - 1, self.M, self.M))
        
        for t in range(T - 1):
            # log xi_t(i,j) ∝ log_alpha[t,i] + log(A[t+1,i,j]) + log_em[j,t+1] + log_beta[t+1,j]
            alpha_i = log_alpha[t, :][:, None]  # (M, 1)
            transition_ij = logA_cache[t + 1]   # (M, M)
            emission_beta_j = log_em[:, t + 1] + log_beta[t + 1, :]  # (M,)
            
            log_xi = alpha_i + transition_ij + emission_beta_j[None, :]
            log_xi -= logsumexp(log_xi)  # 正規化
            xi_t[t] = np.exp(log_xi)
        
        return gamma, xi_t

    # --------------------------
    # M-step: 發射參數更新 (加權 MLE + 數值 nu 估計)
    # --------------------------
    
    def m_step_emissions(self, 
                        x_seq: Dict[str, np.ndarray], 
                        gamma: np.ndarray, 
                        update_nu: bool = True):
        """
        發射參數的加權最大似然估計
        
        Args:
            x_seq: 觀測序列
            gamma: 後驗責任度 (T x M)
            update_nu: 是否數值更新 Student-t 自由度
        """
        for h in range(self.M):
            w = gamma[:, h]  # 權重
            W = w.sum() + 1e-12
            
            # 收益率參數 (Student-t)
            mu_ret = float(np.sum(w * x_seq['ret']) / W)
            var_ret = float(np.sum(w * (x_seq['ret'] - mu_ret) ** 2) / W)
            sigma_ret = math.sqrt(max(var_ret, 1e-12))
            
            # nu 參數的數值估計
            nu = self.emissions[h].nu_ret
            if update_nu and W > 10:  # 只有足夠樣本時才更新
                try:
                    nu = self._estimate_nu_weighted(x_seq['ret'], mu_ret, sigma_ret, w, nu)
                except Exception:
                    pass  # 保持原值
            
            # 其他參數的加權估計
            mu_logvol = float(np.sum(w * x_seq['logvol']) / W)
            var_logvol = float(np.sum(w * (x_seq['logvol'] - mu_logvol) ** 2) / W)
            sigma_logvol = math.sqrt(max(var_logvol, 1e-12))
            
            mu_slope = float(np.sum(w * x_seq['slope']) / W)
            var_slope = float(np.sum(w * (x_seq['slope'] - mu_slope) ** 2) / W)
            sigma_slope = math.sqrt(max(var_slope, 1e-12))
            
            mu_ob = float(np.sum(w * x_seq['ob']) / W)
            var_ob = float(np.sum(w * (x_seq['ob'] - mu_ob) ** 2) / W)
            sigma_ob = math.sqrt(max(var_ob, 1e-9))
            
            # 更新參數 (確保數值穩定性)
            self.emissions[h].mu_ret = mu_ret
            self.emissions[h].sigma_ret = max(sigma_ret, 1e-9)
            self.emissions[h].nu_ret = max(nu, 2.1)
            self.emissions[h].mu_logvol = mu_logvol
            self.emissions[h].sigma_logvol = max(sigma_logvol, 1e-9)
            self.emissions[h].mu_slope = mu_slope
            self.emissions[h].sigma_slope = max(sigma_slope, 1e-9)
            self.emissions[h].ob_loc = mu_ob
            self.emissions[h].ob_scale = max(sigma_ob, 1e-9)

    def _estimate_nu_weighted(self, 
                             x: np.ndarray, 
                             mu: float, 
                             sigma: float, 
                             weights: np.ndarray, 
                             init_nu: float = 6.0) -> float:
        """
        加權 Student-t 自由度的數值最大似然估計
        
        優化目標: 最大化加權對數似然函數
        """
        z2 = ((x - mu) / sigma) ** 2
        w = weights / (weights.sum() + 1e-12)
        
        def neg_log_likelihood(nu_arr):
            nu = float(nu_arr[0])
            if nu <= 2.1:
                return 1e12
            
            try:
                # 加權對數似然的各項
                term1 = (np.sum(w) * 
                        (math.lgamma((nu + 1) / 2.0) - math.lgamma(nu / 2.0) - 
                         0.5 * math.log(nu * math.pi)))
                
                term2 = -(nu + 1) / 2.0 * np.sum(w * np.log1p(z2 / nu))
                
                return -(term1 + term2)
            except (OverflowError, ValueError):
                return 1e12
        
        # 數值優化
        result = minimize(
            neg_log_likelihood, 
            x0=np.array([init_nu]), 
            bounds=[(2.1, 100.0)], 
            method='L-BFGS-B',
            options={'maxiter': 50}
        )
        
        if result.success and 2.1 <= result.x[0] <= 100.0:
            return float(result.x[0])
        return init_nu

    # --------------------------
    # M-step: 轉移參數更新 (Per-row 加權 multinomial logistic)
    # --------------------------
    
    def m_step_transition(self, xi_t: np.ndarray, z_seq: np.ndarray):
        """
        轉移參數的 per-row 加權 multinomial logistic 回歸
        
        對每個來源狀態 i 獨立優化轉移參數，支援並行化
        """
        T_minus_1 = xi_t.shape[0]
        
        # 構建特徵矩陣: X = [1, z_{t+1}] for t=0..T-2
        X = np.hstack([np.ones((T_minus_1, 1)), z_seq[1:T_minus_1+1]])  # (T-1, 1+z_dim)
        d = X.shape[1]  # 特徵維度
        
        # 對每個來源狀態 i 優化參數
        for i in range(self.M):
            self._optimize_row_parameters(i, xi_t, X, d)

    def _optimize_row_parameters(self, i: int, xi_t: np.ndarray, X: np.ndarray, d: int):
        """
        優化第 i 行的轉移參數
        
        使用加權 multinomial logistic 回歸 + L2 正則化
        """
        def _build_logits_from_theta(theta):
            """從參數向量重構 logits 矩陣"""
            return theta.reshape((self.M, d))  # (M, d)
        
        def objective(theta_flat):
            """目標函數: 負加權對數似然 + L2 正則化"""
            try:
                W = _build_logits_from_theta(theta_flat)  # (M, d)
                
                # 計算 logits: X @ W.T -> (T-1, M)
                logits = X @ W.T
                
                # 計算 log-sum-exp (沿目標狀態維度)
                lse = logsumexp(logits, axis=1)  # (T-1,)
                
                # 加權對數似然: sum_t sum_j xi_t[t,i,j] * (logits[t,j] - lse[t])
                weighted_logits = xi_t[:, i, :] * (logits - lse[:, None])
                log_likelihood = np.sum(weighted_logits)
                
                # L2 正則化
                regularization = 0.5 * self.reg_lambda * np.sum(theta_flat ** 2)
                
                return -log_likelihood + regularization
                
            except (OverflowError, ValueError, RuntimeWarning):
                return 1e12
        
        # 初始化參數 (從當前 b, w 提取)
        theta0 = np.zeros(self.M * d)
        for j in range(self.M):
            theta0[j * d] = self.b[i, j]  # 截距項
            if d > 1:  # 有協變量
                theta0[j * d + 1:j * d + d] = self.w[i, j, :]
        
        # L-BFGS-B 優化
        try:
            result = minimize(
                objective, 
                theta0, 
                method='L-BFGS-B', 
                options={'maxiter': 100, 'disp': False}
            )
            
            if result.success:
                # 更新參數
                optimized_W = _build_logits_from_theta(result.x)
                for j in range(self.M):
                    self.b[i, j] = float(optimized_W[j, 0])
                    if d > 1:
                        self.w[i, j, :] = optimized_W[j, 1:]
                        
        except Exception:
            # 優化失敗時保持原參數
            pass

    # --------------------------
    # EM 算法 (Baum-Welch 訓練)
    # --------------------------
    
    def fit_EM(self, 
               x_seq: Dict[str, np.ndarray], 
               z_seq: np.ndarray, 
               n_iter: int = 10, 
               tol: float = 1e-4, 
               verbose: bool = True):
        """
        EM 算法訓練時變 HMM
        
        Args:
            x_seq: 觀測序列字典
            z_seq: 協變量序列 (T x z_dim)
            n_iter: 最大迭代次數
            tol: 收斂容忍度
            verbose: 是否輸出訓練進度
        """
        T = x_seq['ret'].shape[0]
        last_loglik = -np.inf
        
        for iteration in range(n_iter):
            start_time = time.time()
            
            # E-step: 計算後驗概率
            log_alpha, log_c = self.forward_log(x_seq, z_seq)
            log_beta = self.backward_log(x_seq, z_seq)
            gamma, xi_t = self.compute_posteriors_full_xi(log_alpha, log_beta, z_seq, x_seq)
            
            # 計算對數似然
            current_loglik = float(np.sum(log_c))
            
            if verbose:
                elapsed = time.time() - start_time
                print(f"[EM] Iter {iteration}: LogLik = {current_loglik:.6f}, "
                      f"Time = {elapsed:.3f}s, T = {T}")
            
            # M-step: 更新參數
            self.m_step_emissions(x_seq, gamma, update_nu=True)
            self.m_step_transition(xi_t, z_seq)
            
            # 清除快取以使用新參數
            self.A_cache = None
            self.logA_cache = None
            self.last_z_seq_hash = None
            
            # 檢查收斂
            if abs(current_loglik - last_loglik) < tol:
                if verbose:
                    print(f"[EM] Converged at iteration {iteration}")
                break
                
            last_loglik = current_loglik

    # --------------------------
    # Viterbi 算法 (最優路徑解碼)
    # --------------------------
    
    def viterbi(self, x_seq: Dict[str, np.ndarray], z_seq: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Viterbi 算法求解最優狀態序列
        
        Returns:
            path: 最優狀態路徑 (T,)
            max_logprob: 最大對數概率
        """
        T = x_seq['ret'].shape[0]
        
        # 預計算矩陣
        log_em = self.log_emission_matrix(x_seq)
        self.compute_A_cache(z_seq)
        logA_cache = self.logA_cache
        
        # 初始化
        delta = np.full((T, self.M), -np.inf)
        psi = np.zeros((T, self.M), dtype=int)
        
        # t=0
        delta[0, :] = self.log_pi + log_em[:, 0]
        
        # 前向遞推
        for t in range(1, T):
            # 計算所有可能的轉移: delta[t-1, i] + log(A[t, i, j])
            transition_scores = delta[t-1, :][:, None] + logA_cache[t]  # (M, M)
            
            # 找到每個目標狀態的最優前驅
            psi[t, :] = np.argmax(transition_scores, axis=0)
            delta[t, :] = np.max(transition_scores, axis=0) + log_em[:, t]
        
        # 回溯最優路徑
        path = np.zeros(T, dtype=int)
        path[-1] = int(np.argmax(delta[-1, :]))
        
        for t in range(T-2, -1, -1):
            path[t] = psi[t+1, path[t+1]]
        
        max_logprob = float(np.max(delta[-1, :]))
        return path, max_logprob

    # --------------------------
    # 粒子濾波 (系統化重採樣)
    # --------------------------
    
    def particle_filter(self, 
                       x_seq: Dict[str, np.ndarray], 
                       z_seq: np.ndarray, 
                       N: int = 500, 
                       resample_thresh: float = 0.5) -> np.ndarray:
        """
        粒子濾波 with 系統化重採樣
        
        Args:
            x_seq: 觀測序列
            z_seq: 協變量序列
            N: 粒子數量
            resample_thresh: 重採樣閾值 (基於有效樣本大小)
            
        Returns:
            posterior: 近似後驗概率 (T x M)
        """
        T = x_seq['ret'].shape[0]
        
        # 初始化粒子
        particles = np.random.choice(self.M, size=N, p=np.ones(self.M) / self.M)
        weights = np.ones(N) / N
        posterior = np.zeros((T, self.M))
        
        for t in range(T):
            # 狀態傳播
            if t > 0:
                A = self.get_transition_matrix(z_seq[t], t)
                new_particles = np.zeros_like(particles)
                
                for i in range(N):
                    current_state = particles[i]
                    new_particles[i] = np.random.choice(self.M, p=A[current_state])
                
                particles = new_particles
            
            # 權重更新 (基於發射概率)
            log_weights = np.zeros(N)
            for i in range(N):
                h = particles[i]
                ep = self.emissions[h]
                
                # 計算發射對數概率
                log_weights[i] = (
                    student_t_logpdf(np.array([x_seq['ret'][t]]), ep.mu_ret, ep.sigma_ret, ep.nu_ret)[0] +
                    gaussian_logpdf(np.array([x_seq['logvol'][t]]), ep.mu_logvol, ep.sigma_logvol)[0] +
                    gaussian_logpdf(np.array([x_seq['slope'][t]]), ep.mu_slope, ep.sigma_slope)[0] +
                    (-0.5 * math.log(2 * math.pi) - math.log(max(ep.ob_scale, 1e-9)) - 
                     0.5 * ((x_seq['ob'][t] - ep.ob_loc) ** 2) / (max(ep.ob_scale, 1e-9) ** 2))
                )
            
            # 數值穩定的權重正規化
            max_log_weight = log_weights.max()
            unnormalized_weights = np.exp(log_weights - max_log_weight) * weights
            weight_sum = unnormalized_weights.sum() + 1e-300
            weights = unnormalized_weights / weight_sum
            
            # 計算近似後驗
            for h in range(self.M):
                posterior[t, h] = weights[particles == h].sum()
            
            # 有效樣本大小檢查
            ess = 1.0 / np.sum(weights ** 2)
            if ess < resample_thresh * N:
                # 系統化重採樣
                positions = (np.arange(N) + np.random.random()) / N
                cumulative_weights = np.cumsum(weights)
                indices = np.searchsorted(cumulative_weights, positions)
                
                particles = particles[indices]
                weights.fill(1.0 / N)
        
        return posterior

    # --------------------------
    # 輔助方法
    # --------------------------
    
    def get_filtered_probabilities(self, log_alpha: np.ndarray) -> np.ndarray:
        """獲取濾波概率 P(H_t | x_{1:t})"""
        return np.exp(log_alpha)
    
    def get_smoothed_probabilities(self, log_alpha: np.ndarray, log_beta: np.ndarray) -> np.ndarray:
        """獲取平滑概率 P(H_t | x_{1:T})"""
        log_gamma = log_alpha + log_beta
        for t in range(log_gamma.shape[0]):
            log_gamma[t, :] -= logsumexp(log_gamma[t, :])
        return np.exp(log_gamma)
    
    def get_model_summary(self) -> Dict[str, Any]:
        """獲取模型摘要資訊"""
        return {
            'n_states': self.M,
            'z_dim': self.z_dim,
            'regularization': self.reg_lambda,
            'emission_types': {
                'returns': 'Student-t',
                'log_volatility': 'Gaussian',
                'slope': 'Gaussian', 
                'orderbook': 'Gaussian'
            },
            'cache_status': {
                'A_cache_size': self.A_cache.shape if self.A_cache is not None else None,
                'last_z_hash': self.last_z_seq_hash
            }
        }
# --------------------------
# 生產級演示與測試函數
# --------------------------

def generate_synthetic_crypto_data(T: int = 500, seed: int = 42) -> Tuple[Dict[str, np.ndarray], np.ndarray, np.ndarray]:
    """
    生成合成的加密貨幣數據，模擬真實的市場狀態切換
    
    Returns:
        x_seq: 觀測序列字典 
        z_seq: 協變量序列 (T x z_dim)
        true_states: 真實狀態序列 (用於評估)
    """
    rng = np.random.RandomState(seed)
    
    # 定義 6 種市場制度 (對應加密貨幣市場的典型狀態)
    regime_params = {
        0: {"name": "Bull Market", "mu_ret": 0.002, "sigma_ret": 0.015, "vol_base": 0.02},
        1: {"name": "Bear Market", "mu_ret": -0.001, "sigma_ret": 0.025, "vol_base": 0.035},
        2: {"name": "High Volatility", "mu_ret": 0.0, "sigma_ret": 0.04, "vol_base": 0.05},
        3: {"name": "Low Volatility", "mu_ret": 0.0005, "sigma_ret": 0.008, "vol_base": 0.015},
        4: {"name": "Sideways", "mu_ret": 0.0, "sigma_ret": 0.018, "vol_base": 0.025},
        5: {"name": "Crash", "mu_ret": -0.008, "sigma_ret": 0.06, "vol_base": 0.08}
    }
    
    # 生成狀態序列 (持久性較高的制度切換)
    true_states = np.zeros(T, dtype=int)
    current_state = 0
    
    for t in range(T):
        # 制度切換概率 (依賴當前狀態)
        if current_state == 5:  # Crash 狀態更容易結束
            switch_prob = 0.1
        elif current_state in [0, 1]:  # Bull/Bear 更持久
            switch_prob = 0.02
        else:
            switch_prob = 0.05
            
        if rng.random() < switch_prob:
            current_state = rng.choice(6)
            
        true_states[t] = current_state
    
    # 生成觀測數據
    x_seq = {'ret': np.zeros(T), 'logvol': np.zeros(T), 'slope': np.zeros(T), 'ob': np.zeros(T)}
    z_seq = np.zeros((T, 3))  # [slope, volatility, orderbook]
    
    for t in range(T):
        state = true_states[t]
        params = regime_params[state]
        
        # 生成收益率 (Student-t 分布)
        nu = 5.0 if state == 5 else 8.0  # Crash 狀態更厚尾
        ret = rng.standard_t(nu) * params["sigma_ret"] + params["mu_ret"]
        
        # 生成波動率
        vol = params["vol_base"] * (1 + 0.3 * rng.standard_t(6))
        vol = max(vol, 0.005)  # 最小波動率
        
        # 生成價格斜率 (價格趨勢)
        if state == 0:  # Bull
            slope = 0.01 + 0.005 * rng.randn()
        elif state == 1:  # Bear
            slope = -0.008 + 0.004 * rng.randn()
        elif state == 5:  # Crash
            slope = -0.03 + 0.01 * rng.randn()
        else:
            slope = 0.001 * rng.randn()
            
        # 生成訂單簿不平衡
        if state in [0, 3]:  # Bull/Low vol 傾向買盤
            ob = 0.2 + 0.3 * rng.randn()
        elif state in [1, 5]:  # Bear/Crash 傾向賣盤  
            ob = -0.15 + 0.25 * rng.randn()
        else:
            ob = 0.05 * rng.randn()
        
        # 存儲數據
        x_seq['ret'][t] = ret
        x_seq['logvol'][t] = np.log(vol)
        x_seq['slope'][t] = slope
        x_seq['ob'][t] = ob
        
        # 協變量 (用於轉移矩陣)
        z_seq[t, 0] = slope
        z_seq[t, 1] = vol
        z_seq[t, 2] = ob
    
    return x_seq, z_seq, true_states

def benchmark_optimized_hmm():
    """
    生產級性能基準測試
    
    測試優化版本的性能改進:
    - 向量化計算速度
    - 快取機制效果
    - 數值穩定性
    """
    print("="*60)
    print("生產級量子 HMM 性能基準測試")
    print("="*60)
    
    # 生成測試數據 (模擬實際交易數據規模)
    T_sizes = [500, 1000, 2000]
    
    for T in T_sizes:
        print(f"\n【測試序列長度: {T}】")
        
        # 生成數據
        x_seq, z_seq, true_states = generate_synthetic_crypto_data(T=T, seed=42)
        
        # 初始化模型
        model = TimeVaryingHMM(n_states=6, z_dim=3, reg_lambda=1e-3, rng_seed=42)
        
        # 測試 Forward 算法
        start_time = time.time()
        log_alpha, log_c = model.forward_log(x_seq, z_seq)
        forward_time = time.time() - start_time
        loglik = np.sum(log_c)
        
        print(f"  Forward 算法: {forward_time:.4f}s | LogLik: {loglik:.2f}")
        
        # 測試 Backward 算法
        start_time = time.time()
        log_beta = model.backward_log(x_seq, z_seq)
        backward_time = time.time() - start_time
        
        print(f"  Backward 算法: {backward_time:.4f}s")
        
        # 測試完整 E-step (包含 xi 計算)
        start_time = time.time()
        gamma, xi_t = model.compute_posteriors_full_xi(log_alpha, log_beta, z_seq, x_seq)
        posterior_time = time.time() - start_time
        
        print(f"  後驗計算: {posterior_time:.4f}s")
        
        # 測試 Viterbi 解碼
        start_time = time.time()
        path, max_logprob = model.viterbi(x_seq, z_seq)
        viterbi_time = time.time() - start_time
        
        print(f"  Viterbi 解碼: {viterbi_time:.4f}s | Max LogProb: {max_logprob:.2f}")
        
        # 計算準確率 (與真實狀態比較)
        accuracy = np.mean(path == true_states)
        print(f"  狀態識別準確率: {accuracy:.3f}")
        
        # 測試快取效果 (重複 Forward 調用)
        start_time = time.time()
        for _ in range(3):
            log_alpha2, _ = model.forward_log(x_seq, z_seq)
        cached_time = (time.time() - start_time) / 3
        
        print(f"  快取加速比: {forward_time/cached_time:.2f}x")
        
        # 記憶體使用估計
        cache_memory = (model.A_cache.nbytes + model.logA_cache.nbytes) / 1024 / 1024
        print(f"  快取記憶體: {cache_memory:.2f} MB")

def run_production_em_test():
    """
    生產級 EM 訓練測試
    
    驗證:
    - 收斂性
    - 參數估計品質  
    - 訓練速度
    """
    print("\n" + "="*60)
    print("生產級 EM 訓練測試")
    print("="*60)
    
    # 生成訓練數據
    x_seq, z_seq, true_states = generate_synthetic_crypto_data(T=800, seed=123)
    
    # 初始化模型
    model = TimeVaryingHMM(n_states=6, z_dim=3, reg_lambda=1e-3, rng_seed=42)
    
    # 記錄初始對數似然
    log_alpha, log_c = model.forward_log(x_seq, z_seq)
    initial_loglik = np.sum(log_c)
    print(f"初始對數似然: {initial_loglik:.2f}")
    
    # 運行 EM 訓練
    print("\n開始 EM 訓練...")
    start_time = time.time()
    
    model.fit_EM(x_seq, z_seq, n_iter=15, tol=1e-5, verbose=True)
    
    total_time = time.time() - start_time
    print(f"\nEM 訓練完成! 總時間: {total_time:.2f}s")
    
    # 評估訓練後性能
    log_alpha_final, log_c_final = model.forward_log(x_seq, z_seq)
    final_loglik = np.sum(log_c_final)
    improvement = final_loglik - initial_loglik
    
    print(f"最終對數似然: {final_loglik:.2f}")
    print(f"似然改進: +{improvement:.2f}")
    
    # 狀態解碼準確率
    path_final, _ = model.viterbi(x_seq, z_seq)
    accuracy = np.mean(path_final == true_states)
    print(f"訓練後準確率: {accuracy:.3f}")
    
    # 顯示學習到的制度參數
    print("\n學習到的制度參數:")
    for i in range(model.M):
        ep = model.emissions[i]
        print(f"  狀態 {i}: μ_ret={ep.mu_ret:.4f}, σ_ret={ep.sigma_ret:.4f}, ν={ep.nu_ret:.2f}")

def quantum_integration_test():
    """
    量子決策引擎整合測試
    
    模擬與 quantum_decision_optimizer.py 的整合
    """
    print("\n" + "="*60)
    print("量子決策引擎整合測試")
    print("="*60)
    
    # 模擬即時數據流
    x_seq, z_seq, _ = generate_synthetic_crypto_data(T=100, seed=456)
    
    # 初始化並訓練模型
    model = TimeVaryingHMM(n_states=6, z_dim=3, reg_lambda=1e-3)
    model.fit_EM(x_seq, z_seq, n_iter=5, verbose=False)
    
    # 即時制度識別 (模擬線上推理)
    print("即時制度識別:")
    for t in range(95, 100):  # 最後5個時間點
        # 使用滑動窗口進行制度識別
        window_start = max(0, t-50)
        x_window = {k: v[window_start:t+1] for k, v in x_seq.items()}
        z_window = z_seq[window_start:t+1]
        
        # Forward 推理 (即時濾波)
        log_alpha, _ = model.forward_log(x_window, z_window)
        current_probs = np.exp(log_alpha[-1])  # 當前時刻的制度概率
        
        # 識別最可能的制度
        dominant_regime = np.argmax(current_probs)
        confidence = current_probs[dominant_regime]
        
        print(f"  t={t}: 制度={dominant_regime}, 信心度={confidence:.3f}, "
              f"概率分布={np.round(current_probs, 3)}")
        
        # 模擬決策邏輯 (基於制度狀態)
        if dominant_regime == 0 and confidence > 0.6:
            print(f"    → 量子決策: LONG 信號 (牛市制度)")
        elif dominant_regime in [1, 5] and confidence > 0.6:
            print(f"    → 量子決策: SHORT 信號 (熊市/崩盤制度)")
        else:
            print(f"    → 量子決策: HOLD (制度不確定)")

if __name__ == "__main__":
    # 運行所有生產級測試
    benchmark_optimized_hmm()
    run_production_em_test()
    quantum_integration_test()
    
    print("\n" + "="*60)
    print("生產級量子 HMM 優化完成!")
    print("✓ 向量化 forward/backward 算法")
    print("✓ 轉移矩陣快取機制")
    print("✓ Per-row multinomial logistic M-step")
    print("✓ 加權 Student-t 數值估計")
    print("✓ 系統化重採樣粒子濾波")
    print("✓ 數值穩定性優化")
    print("✓ Trading X 區塊鏈數據整合")
    print("="*60)
