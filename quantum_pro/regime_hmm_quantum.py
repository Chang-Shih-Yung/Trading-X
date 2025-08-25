# regime_hmm_quantum.py
# Time-varying HMM with Student-t emissions, EM (Baum-Welch) training, transition logistic param,
# and optional particle filter. Engine for Regime Estimation and likelihood export for decision engine.
#
# Dependencies: numpy, scipy, pandas
# Save as: regime_hmm_quantum.py

import numpy as np
import math
from typing import List, Dict, Tuple, Any, Optional
from dataclasses import dataclass
from scipy.special import logsumexp
from scipy.optimize import minimize
import time

# --------------------------
# Utility / PDF functions
# --------------------------

def student_t_logpdf(x: np.ndarray, mu: float, sigma: float, nu: float) -> np.ndarray:
    """Vectorized Student-t log pdf for x array."""
    sigma = max(sigma, 1e-9)
    nu = max(nu, 2.1)
    z = (x - mu) / sigma
    # log normalization constant
    a = math.lgamma((nu + 1.0) / 2.0) - math.lgamma(nu / 2.0)
    b = -0.5 * math.log(nu * math.pi) - math.log(sigma)
    c = - (nu + 1.0) / 2.0 * np.log1p((z * z) / nu)
    return a + b + c

def gaussian_logpdf(x: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    sigma = max(sigma, 1e-9)
    return -0.5 * np.log(2 * math.pi) - np.log(sigma) - 0.5 * ((x - mu) ** 2) / (sigma ** 2)

# --------------------------
# Dataclasses for emission params
# --------------------------
@dataclass
class EmissionParams:
    mu_ret: float
    sigma_ret: float
    nu_ret: float
    mu_logvol: float
    sigma_logvol: float
    mu_slope: float
    sigma_slope: float
    ob_loc: float
    ob_scale: float

# --------------------------
# Main HMM Class
# --------------------------
class TimeVaryingHMM:
    def __init__(self,
                 n_states: int = 6,
                 z_dim: int = 3,
                 reg_lambda: float = 1e-3,
                 rng_seed: int = 42):
        """
        n_states: number of regimes (M)
        z_dim: dimension of covariates z_t used for transition logits
        reg_lambda: L2 regularization for logistic update
        """
        self.M = n_states
        self.z_dim = z_dim
        self.reg_lambda = reg_lambda
        rng = np.random.RandomState(rng_seed)

        # Transition base logits b (M x M) and weights w (M x M x z_dim)
        self.b = rng.normal(scale=0.01, size=(self.M, self.M))
        self.w = rng.normal(scale=0.01, size=(self.M, self.M, self.z_dim))

        # Initial log pi
        self.log_pi = np.log(np.ones(self.M) / self.M)

        # Emission params initial
        self.emissions: List[EmissionParams] = []
        for i in range(self.M):
            ep = EmissionParams(
                mu_ret=0.0 + rng.normal(scale=1e-3),
                sigma_ret=0.01 + rng.uniform() * 0.05,
                nu_ret=5.0 + rng.uniform() * 5.0,
                mu_logvol=-2.0 + rng.normal(scale=0.2),
                sigma_logvol=0.5 + rng.uniform() * 0.5,
                mu_slope=0.0 + rng.normal(scale=1e-3),
                sigma_slope=0.005 + rng.uniform() * 0.02,
                ob_loc=0.0 + rng.normal(scale=0.1),
                ob_scale=0.5 + rng.uniform() * 0.5
            )
            self.emissions.append(ep)

    # --------------------------
    # Transition matrix from z_t
    # --------------------------
    def transition_matrix(self, z_t: np.ndarray) -> np.ndarray:
        """
        Compute A_t (M x M), rows sum to 1: a_{i->j}(t) = softmax_j(b_i + w_i . z_t)
        """
        logits = np.zeros((self.M, self.M), dtype=float)
        for i in range(self.M):
            logits[i, :] = self.b[i, :] + (self.w[i, :, :] @ z_t)
            # numerically stable row-wise softmax
        # row softmax:
        row_max = logits.max(axis=1, keepdims=True)
        ex = np.exp(logits - row_max)
        A = ex / (ex.sum(axis=1, keepdims=True) + 1e-300)
        return A

    # --------------------------
    # Emission log-likelihood p(x_t | h)
    # x components: ret, logvol, slope, ob
    # --------------------------
    def log_emission(self, x_seq: Dict[str, np.ndarray], h: int) -> np.ndarray:
        """
        x_seq: dict of arrays length T: 'ret', 'logvol', 'slope', 'ob'
        returns vector length T of log p(x_t | H_t = h)
        """
        ep = self.emissions[h]
        # student-t on returns
        l_ret = student_t_logpdf(x_seq['ret'], ep.mu_ret, ep.sigma_ret, ep.nu_ret)
        l_vol = gaussian_logpdf(x_seq['logvol'], ep.mu_logvol, ep.sigma_logvol)
        l_slope = gaussian_logpdf(x_seq['slope'], ep.mu_slope, ep.sigma_slope)
        # treat OB as gaussian-like proxy (flexible)
        ob_diff = (x_seq['ob'] - ep.ob_loc)
        l_ob = -0.5 * (ob_diff ** 2) / (max(ep.ob_scale, 1e-9) ** 2) - math.log(max(ep.ob_scale, 1e-9)) - 0.5 * math.log(2 * math.pi)
        return l_ret + l_vol + l_slope + l_ob

    # --------------------------
    # Forward (log-space) -> returns log_alpha (T x M) and log_likelihoods per time
    # --------------------------
    def forward_log(self, x_seq: Dict[str, np.ndarray], z_seq: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        T = x_seq['ret'].shape[0]
        log_alpha = np.full((T, self.M), -np.inf)
        # precompute log emission per state
        log_em = np.zeros((self.M, T))
        for h in range(self.M):
            log_em[h, :] = self.log_emission(x_seq, h)

        # t=0
        log_alpha[0, :] = self.log_pi + log_em[:, 0]
        # normalize
        c0 = logsumexp(log_alpha[0, :])
        log_alpha[0, :] -= c0
        log_c = [c0]  # scaling log factors

        # iterate
        for t in range(1, T):
            A = self.transition_matrix(z_seq[t])  # (M,M), rows i->j
            # compute logsum over i for each j: logsum_i ( log_alpha[t-1,i] + log a_ij )
            # note a_ij = A[i,j]
            logA = np.log(A + 1e-300)
            for j in range(self.M):
                tmp = log_alpha[t-1, :] + logA[:, j]
                log_alpha[t, j] = logsumexp(tmp) + log_em[j, t]
            # normalize
            ct = logsumexp(log_alpha[t, :])
            log_alpha[t, :] -= ct
            log_c.append(ct)
        # total log-likelihood = sum(log_c)
        loglik = sum(log_c)
        return log_alpha, np.array(log_c)

    # --------------------------
    # Backward (log-space) -> returns log_beta (T x M)
    # --------------------------
    def backward_log(self, x_seq: Dict[str, np.ndarray], z_seq: np.ndarray) -> np.ndarray:
        T = x_seq['ret'].shape[0]
        log_em = np.zeros((self.M, T))
        for h in range(self.M):
            log_em[h, :] = self.log_emission(x_seq, h)
        log_beta = np.full((T, self.M), -np.inf)
        log_beta[-1, :] = 0.0  # log(1)
        # iterate backwards
        for t in range(T - 2, -1, -1):
            A = self.transition_matrix(z_seq[t + 1])  # transition used at next step
            logA = np.log(A + 1e-300)
            for i in range(self.M):
                # sum_j a_ij * p(x_{t+1}|j) * beta_{t+1}(j)
                tmp = logA[i, :] + log_em[:, t + 1] + log_beta[t + 1, :]
                log_beta[t, i] = logsumexp(tmp)
        return log_beta

    # --------------------------
    # Compute gamma, xi from forward/backward
    # --------------------------
    def compute_posteriors(self, log_alpha: np.ndarray, log_beta: np.ndarray, z_seq: np.ndarray, x_seq: Dict[str, np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Returns:
          gamma: (T, M) P(H_t = h | x_{1:T})
          xi_sum: (M, M) sum over t of expected transitions (for M-step)
        """
        T = log_alpha.shape[0]
        # compute unnormalized log gamma = log_alpha + log_beta
        log_gamma = log_alpha + log_beta
        # normalize
        for t in range(T):
            s = logsumexp(log_gamma[t, :])
            log_gamma[t, :] -= s
        gamma = np.exp(log_gamma)

        # xi (pairwise) expected counts sum over t
        xi_sum = np.zeros((self.M, self.M))
        log_em = np.zeros((self.M, T))
        for h in range(self.M):
            log_em[h, :] = self.log_emission(x_seq, h)

        for t in range(T - 1):
            A = self.transition_matrix(z_seq[t + 1])  # a_{i->j} at t+1
            logA = np.log(A + 1e-300)
            # compute log xi_t(i,j) ∝ log_alpha[t,i] + log a_ij + log_em[j,t+1] + log_beta[t+1,j]
            tmp = np.zeros((self.M, self.M))
            for i in range(self.M):
                for j in range(self.M):
                    tmp[i, j] = log_alpha[t, i] + logA[i, j] + log_em[j, t + 1] + log_beta[t + 1, j]
            # normalize tmp
            norm = logsumexp(tmp.ravel())
            tmp -= norm
            xi = np.exp(tmp)  # normalized pairwise at time t
            xi_sum += xi
        return gamma, xi_sum

    # --------------------------
    # M-step: update emission params (weighted MLE) and transition logits via weighted multinomial logistic
    # --------------------------
    def m_step_emissions(self, x_seq: Dict[str, np.ndarray], gamma: np.ndarray):
        """
        Weighted updates for emission parameters using responsibilities gamma (T x M)
        Student-t nu is updated via simple heuristic (can be improved with numeric root find)
        """
        T = x_seq['ret'].shape[0]
        # for each state h:
        for h in range(self.M):
            w = gamma[:, h]  # length T
            W = w.sum() + 1e-12
            # weighted mean for returns
            mu_ret = np.sum(w * x_seq['ret']) / W
            # weighted variance
            var_ret = np.sum(w * (x_seq['ret'] - mu_ret) ** 2) / W
            sigma_ret = math.sqrt(max(var_ret, 1e-12))
            # nu: heuristic shrink toward 6 based on W
            nu = max(2.5, 6.0 - 3.0 * math.exp(-W / 50.0))
            # logvol
            mu_logvol = np.sum(w * x_seq['logvol']) / W
            var_logvol = np.sum(w * (x_seq['logvol'] - mu_logvol) ** 2) / W
            sigma_logvol = math.sqrt(max(var_logvol, 1e-12))
            # slope
            mu_slope = np.sum(w * x_seq['slope']) / W
            var_slope = np.sum(w * (x_seq['slope'] - mu_slope) ** 2) / W
            sigma_slope = math.sqrt(max(var_slope, 1e-12))
            # ob
            mu_ob = np.sum(w * x_seq['ob']) / W
            var_ob = np.sum(w * (x_seq['ob'] - mu_ob) ** 2) / W
            sigma_ob = math.sqrt(max(var_ob, 1e-9))
            # update
            self.emissions[h].mu_ret = float(mu_ret)
            self.emissions[h].sigma_ret = float(sigma_ret)
            self.emissions[h].nu_ret = float(nu)
            self.emissions[h].mu_logvol = float(mu_logvol)
            self.emissions[h].sigma_logvol = float(sigma_logvol)
            self.emissions[h].mu_slope = float(mu_slope)
            self.emissions[h].sigma_slope = float(sigma_slope)
            self.emissions[h].ob_loc = float(mu_ob)
            self.emissions[h].ob_scale = float(sigma_ob)

    def _flatten_transition_params(self) -> np.ndarray:
        """pack b and w into flat vector for optimization"""
        return np.concatenate([self.b.ravel(), self.w.ravel()])

    def _unflatten_transition_params(self, theta: np.ndarray):
        """unpack flat vector into b and w"""
        b_size = self.M * self.M
        w_size = self.M * self.M * self.z_dim
        b_flat = theta[:b_size]
        w_flat = theta[b_size:b_size + w_size]
        self.b = b_flat.reshape((self.M, self.M))
        self.w = w_flat.reshape((self.M, self.M, self.z_dim))

    def m_step_transition(self, xi_sum: np.ndarray, z_seq: np.ndarray):
        """
        Update transition parameters (b, w) by maximizing expected complete log-likelihood:
        Σ_t Σ_i Σ_j ξ_t(i,j) * log a_{ij}(t)
        where logit_{i->j}(t) = b_{ij} + w_{ij}^T z_t
        This becomes a weighted multinomial logistic regression per i row.
        We'll do joint optimization with L2 regularization.
        """
        T = z_seq.shape[0]
        # flatten current params
        theta0 = self._flatten_transition_params()

        # Build target weights per (t, i, j): but to speed up we aggregate per (i,j) with "pseudo-samples" weighted by xi_t
        # We'll define objective and gradient using vectorized operations.

        # Vectorized objective implementation
        def obj_vec(theta_flat: np.ndarray) -> float:
            b_size = self.M * self.M
            w_size = self.M * self.M * self.z_dim
            b_flat = theta_flat[:b_size]
            w_flat = theta_flat[b_size:b_size + w_size]
            b = b_flat.reshape((self.M, self.M))
            w = w_flat.reshape((self.M, self.M, self.z_dim))
            total = 0.0
            # For t = 1..T-1 corresponding xi_t
            for t in range(0, T - 1):
                zt = z_seq[t + 1]  # because xi_t corresponds to transition used with z_{t+1}
                # compute logits for each i (M x M)
                logits = b + np.tensordot(w, zt, axes=([2], [0]))  # shape M x M
                # row-wise logsumexp
                row_lse = logsumexp(logits, axis=1)
                # sum over i,j xi_t(i,j) * (logit_ij - row_lse_i)
                total += np.sum(xi_sum * (logits - row_lse[:, None]))
            # negative loglik (we'll minimize)
            # regularization
            reg = 0.5 * self.reg_lambda * (np.sum(b ** 2) + np.sum(w ** 2))
            return -float(total) + reg

        # gradient for optimizer (optional). To keep code compact, we'll use scipy minimize (L-BFGS-B) without explicit gradient.
        res = minimize(obj_vec, theta0, method='L-BFGS-B', options={'maxiter': 100, 'disp': False})
        if res.success:
            self._unflatten_transition_params(res.x)
        else:
            # fallback: keep existing params
            print("Transition optimization failed:", res.message)

    # --------------------------
    # Full Baum-Welch EM iterations (offline)
    # --------------------------
    def fit_EM(self, x_seq: Dict[str, np.ndarray], z_seq: np.ndarray, n_iter: int = 10, tol: float = 1e-4, verbose: bool = True):
        """
        Run Baum-Welch EM to estimate emission and (optionally) transition parameters.
        """
        T = x_seq['ret'].shape[0]
        last_loglik = -np.inf
        for k in range(n_iter):
            # E-step
            log_alpha, log_c = self.forward_log(x_seq, z_seq)
            log_beta = self.backward_log(x_seq, z_seq)
            gamma, xi_sum = self.compute_posteriors(log_alpha, log_beta, z_seq, x_seq)
            loglik = np.sum(log_c)
            if verbose:
                print(f"EM iter {k} loglik = {loglik:.6f}")
            # M-step
            self.m_step_emissions(x_seq, gamma)
            # update transition params (expensive)
            self.m_step_transition(xi_sum, z_seq)
            # convergence
            if abs(loglik - last_loglik) < tol:
                if verbose:
                    print("EM converged")
                break
            last_loglik = loglik

    # --------------------------
    # Particle Filter (optional alternative)
    # --------------------------
    def particle_filter(self, x_seq: Dict[str, np.ndarray], z_seq: np.ndarray, N: int = 1000, resample_thresh: float = 0.5) -> np.ndarray:
        """
        Simple discrete-state particle filter. Returns approx posterior probs (T x M).
        Particles carry discrete hidden state h only (discrete HMM); transitions drawn from A_t.
        """
        T = x_seq['ret'].shape[0]
        # initialize
        particles = np.random.choice(self.M, size=N, p=np.ones(self.M) / self.M)
        weights = np.ones(N) / N
        posterior = np.zeros((T, self.M))
        for t in range(T):
            # propagate
            if t > 0:
                A = self.transition_matrix(z_seq[t])
                # for each particle, sample next state by row distribution
                new_particles = np.zeros_like(particles)
                for i in range(N):
                    cur = particles[i]
                    new_particles[i] = np.random.choice(self.M, p=A[cur, :])
                particles = new_particles
            # weight by emission likelihood
            log_em = np.array([self.log_emission({'ret': np.array([x_seq['ret'][t]]),
                                                  'logvol': np.array([x_seq['logvol'][t]]),
                                                  'slope': np.array([x_seq['slope'][t]]),
                                                  'ob': np.array([x_seq['ob'][t]])}, h=particles[i])[0]
                               for i in range(N)])
            # numerically stable exponentiation
            max_log = np.max(log_em)
            w_unnorm = np.exp(log_em - max_log) * weights
            w_sum = np.sum(w_unnorm) + 1e-300
            weights = w_unnorm / w_sum
            # posterior approx
            for h in range(self.M):
                posterior[t, h] = np.sum(weights[particles == h])
            # resample if ESS low
            ess = 1.0 / np.sum(weights ** 2)
            if ess < resample_thresh * N:
                idx = np.random.choice(N, size=N, p=weights)
                particles = particles[idx]
                weights.fill(1.0 / N)
        return posterior

    # --------------------------
    # Export likelihood for a hypothesis set K: you provide a mapping
    # p(obs | hypo=k, regime=h) implementer must supply or use defaults
    # --------------------------
    def export_mixed_likelihoods(self, x_seq: Dict[str, np.ndarray], z_seq: np.ndarray,
                                 hypothesis_likelihood_fn) -> np.ndarray:
        """
        Given a user-provided hypothesis_likelihood_fn(hypo_k, regime_h, t) -> log p(obs_t | hypo,k, regime,h),
        produce L_k(t) = sum_h P(H_t = h | x_1:t) * p(obs | hypo,k, regime=h)
        returns array of shape (K, T) with L_k(t) in log-space (log-likelihood)
        """
        # first get filtered P(H_t|x_1:t)
        log_alpha, _ = self.forward_log(x_seq, z_seq)  # log_alpha normalized per time
        filt_probs = np.exp(log_alpha)  # (T, M)
        T = x_seq['ret'].shape[0]
        # detect number of hypotheses K by calling hypothesis_likelihood_fn with sample
        # assume it can tell K
        # We'll call for each k,h,t and sum
        # For efficiency, caller can vectorize; here simple loop
        K = hypothesis_likelihood_fn('__count__', None, None)  # should return K
        Lk = np.full((K, T), -np.inf)
        for t in range(T):
            for k in range(K):
                # compute logsum_h filt_probs[t,h] * p(obs|k,h) -> in logspace: logsumexp(log(filt) + log p)
                log_terms = []
                for h in range(self.M):
                    log_pfilt = math.log(max(filt_probs[t, h], 1e-300))
                    log_pobs = hypothesis_likelihood_fn(k, h, t)  # should be scalar log p
                    log_terms.append(log_pfilt + log_pobs)
                Lk[k, t] = logsumexp(np.array(log_terms))
        return Lk

# --------------------------
# Quick usage example (synthetic)
# --------------------------
def synthetic_demo(T: int = 400, seed: int = 1):
    rng = np.random.RandomState(seed)
    # generate covariates z_seq and observations under toy regime switching
    true_states = []
    obs = {'ret': [], 'logvol': [], 'slope': [], 'ob': []}
    z_seq = []
    state = 0
    for t in range(T):
        if rng.rand() < 0.02:
            state = rng.randint(0, 6)
        true_states.append(state)
        # covariate vector: slope_proxy, vol_proxy, funding_proxy
        slope = rng.normal(scale=0.002) + (0.01 if state % 3 == 0 else -0.005 if state % 3 == 1 else 0.0)
        vol = 0.02 + 0.01 * (state % 3)
        ob = rng.normal(loc=0.1 if state % 2 == 0 else -0.1, scale=0.2)
        ret = rng.standard_t(df=5) * vol + (0.001 if state % 3 == 0 else -0.001 if state % 3 == 1 else 0.0)
        logvol = math.log(max(1e-9, vol))
        obs['ret'].append(float(ret))
        obs['logvol'].append(float(logvol))
        obs['slope'].append(float(slope))
        obs['ob'].append(float(ob))
        z_seq.append(np.array([slope, vol, ob]))
    # convert to numpy arrays
    for k in obs:
        obs[k] = np.array(obs[k], dtype=float)
    z_seq = np.stack(z_seq, axis=0)
    return obs, z_seq, true_states

def quick_run_demo():
    obs, z_seq, true_states = synthetic_demo(T=300, seed=42)
    model = TimeVaryingHMM(n_states=6, z_dim=3, reg_lambda=1e-3)
    # run one forward
    start = time.time()
    log_alpha, log_c = model.forward_log(obs, z_seq)
    elapsed = time.time() - start
    print(f"Forward completed in {elapsed:.3f}s")
    filt_probs = np.exp(log_alpha)
    print("Last filtered probs:", np.round(filt_probs[-1], 4))
    # run EM (caution: may be slow)
    print("Running short EM (2 iters)...")
    model.fit_EM(obs, z_seq, n_iter=2, tol=1e-5, verbose=True)
    log_alpha2, _ = model.forward_log(obs, z_seq)
    print("After EM last probs:", np.round(np.exp(log_alpha2[-1]), 4))

if __name__ == "__main__":
    quick_run_demo()
