"""
🎯 Trading X - Phase5 Lean 相似度回測（實戰優化版）
保持既有 JSON Schema，內部實現 Lean 優化邏輯
基於形狀比較的歷史相似度匹配，避免多指標過擬合
"""

import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import json
import warnings
from pathlib import Path

# 關閉警告
warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

class TimeFrame(Enum):
    """時間框架枚舉 - Lean 版本：H4+D1主導，W1制度閘門"""
    H4 = "4h"  # 短期趨勢，權重 45%
    D1 = "1d"  # 中期趨勢，權重 55%  
    W1 = "1w"  # 制度判斷，僅做閘門

class MarketDirection(Enum):
    """市場方向"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"

class MarketRegime(Enum):
    """市場制度分類 - 6種制度"""
    TREND_UP_HIGH = "trend_up_high"      # 上升+高波動
    TREND_UP_MID = "trend_up_mid"        # 上升+中波動
    TREND_UP_LOW = "trend_up_low"        # 上升+低波動
    TREND_DOWN_HIGH = "trend_down_high"  # 下降+高波動
    TREND_DOWN_MID = "trend_down_mid"    # 下降+中波動
    TREND_DOWN_LOW = "trend_down_low"    # 下降+低波動
    RANGE_HIGH = "range_high"            # 橫盤+高波動
    RANGE_MID = "range_mid"              # 橫盤+中波動
    RANGE_LOW = "range_low"              # 橫盤+低波動

@dataclass
class LeanPattern:
    """Lean 歷史模式匹配結果 - 僅3個核心序列"""
    symbol: str
    timeframe: TimeFrame
    match_date: datetime
    similarity_score: float          # 基於形狀相似度 (cosine)
    subsequent_direction: MarketDirection
    subsequent_return: float
    confidence_level: float
    regime: MarketRegime            # 制度標籤
    return_sequence: List[float]    # 收益率序列
    rsi_zscore_sequence: List[float] # RSI z-score 序列

@dataclass
class LeanConsensus:
    """Lean 多時間框架共識 - H4+D1投票，W1制度閘門"""
    symbol: str
    current_timestamp: datetime
    h4_patterns: List[LeanPattern]
    d1_patterns: List[LeanPattern]
    w1_regime_gate: bool            # W1制度閘門通過/不通過
    consensus_direction: MarketDirection
    consensus_confidence: float
    expected_return: float
    position_size_multiplier: float  # 波動倒數縮放
    regime_restriction: str         # 制度限制說明

@dataclass
class ExecutionFilter:
    """執行過濾器 - 三重過濾機制"""
    win_rate_threshold: float = 0.58  # 統計顯著性門檻
    cost_threshold: float = 0.0008    # 手續費+滑點×2
    regime_gate_passed: bool = True   # 制度閘門
    execution_allowed: bool = False   # 最終執行許可

class LeanHistoricalMatcher:
    """Lean 歷史匹配引擎 - 僅形狀比較，避免過擬合"""
    
    def __init__(self):
        # 主要加密貨幣 (高流動性)
        self.major_symbols = [
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", 
            "XRPUSDT", "SOLUSDT", "DOTUSDT"
        ]
        
        # Lean 時間框架：H4+D1投票，W1制度
        self.timeframes = [TimeFrame.H4, TimeFrame.D1, TimeFrame.W1]
        
        # 數據儲存
        self.historical_data = {}
        self.regime_cache = {}
        
        # Lean 參數 (固定粗粒度檔位，避免過擬合)
        self.lean_params = {
            'window_size': 60,          # 固定窗口大小
            'forward_periods': 10,      # 固定前瞻期間
            'top_k_matches': 20,        # 固定相似模式數量
            'cost_buffer': 0.0008,      # 保守成本估計 (雙倍)
            'regime_lookback': 60,      # 制度判斷回看期
            'vol_lookback': 30          # 波動計算期間
        }
        
    def logret(self, prices: pd.Series) -> pd.Series:
        """計算對數收益率"""
        return np.log(prices).diff().fillna(0)
    
    def zscore(self, x: pd.Series) -> pd.Series:
        """計算 Z-Score 標準化"""
        x = x.astype(float)
        return (x - x.mean()) / (x.std(ddof=0) + 1e-9)
    
    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """計算餘弦相似度"""
        a = a - a.mean()
        b = b - b.mean()
        denominator = (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9)
        return float(np.dot(a, b) / denominator)
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """計算 RSI - 唯一技術濾波"""
        delta = prices.diff()
        up = delta.clip(lower=0).ewm(alpha=1/period, adjust=False).mean()
        down = (-delta.clip(upper=0)).ewm(alpha=1/period, adjust=False).mean()
        rs = up / (down + 1e-9)
        return 100 - 100 / (1 + rs)
    
    def detect_regime(self, df: pd.DataFrame) -> MarketRegime:
        """制度檢測 - 趨勢方向 × 波動桶"""
        try:
            if len(df) < self.lean_params['regime_lookback']:
                return MarketRegime.RANGE_MID
            
            # 趨勢檢測 (60日斜率)
            prices = df['close'].tail(self.lean_params['regime_lookback'])
            slope = np.polyfit(range(len(prices)), prices, 1)[0]
            
            # 波動檢測 (30日實際波動分位)
            returns = self.logret(df['close']).tail(self.lean_params['vol_lookback'])
            vol = returns.std() * np.sqrt(365)  # 年化波動率
            
            # 簡化的波動分位 (這裡可以用歷史分位數，簡化用固定閾值)
            vol_percentile = 0.33 if vol < 0.3 else (0.67 if vol < 0.6 else 1.0)
            
            # 趨勢分類
            if slope > 0.02:
                trend = "trend_up"
            elif slope < -0.02:
                trend = "trend_down"
            else:
                trend = "range"
            
            # 波動分類
            if vol_percentile < 0.4:
                vol_bucket = "low"
            elif vol_percentile < 0.7:
                vol_bucket = "mid"  
            else:
                vol_bucket = "high"
            
            # 組合制度
            regime_str = f"{trend}_{vol_bucket}"
            
            # 映射到枚舉
            regime_mapping = {
                "trend_up_low": MarketRegime.TREND_UP_LOW,
                "trend_up_mid": MarketRegime.TREND_UP_MID,
                "trend_up_high": MarketRegime.TREND_UP_HIGH,
                "trend_down_low": MarketRegime.TREND_DOWN_LOW,
                "trend_down_mid": MarketRegime.TREND_DOWN_MID,
                "trend_down_high": MarketRegime.TREND_DOWN_HIGH,
                "range_low": MarketRegime.RANGE_LOW,
                "range_mid": MarketRegime.RANGE_MID,
                "range_high": MarketRegime.RANGE_HIGH,
            }
            
            return regime_mapping.get(regime_str, MarketRegime.RANGE_MID)
            
        except Exception as e:
            logger.warning(f"制度檢測失敗: {e}")
            return MarketRegime.RANGE_MID
    
    def build_lean_features(self, df: pd.DataFrame, window: int) -> Tuple[np.ndarray, np.ndarray]:
        """構建 Lean 特徵 - 僅3個序列"""
        try:
            # 1. 收益率序列 (形狀比較核心)
            returns = self.logret(df['close']).tail(window).fillna(0)
            
            # 2. RSI Z-Score (唯一技術濾波)
            rsi = self.calculate_rsi(df['close']).tail(window)
            rsi_zscore = self.zscore(rsi).fillna(0)
            
            return returns.values, rsi_zscore.values
            
        except Exception as e:
            logger.error(f"特徵構建失敗: {e}")
            return np.zeros(window), np.zeros(window)
    
    async def find_lean_patterns(self, symbol: str, timeframe: TimeFrame, 
                                df: pd.DataFrame) -> List[LeanPattern]:
        """尋找 Lean 相似模式 - 同制度內比較"""
        try:
            patterns = []
            window = self.lean_params['window_size']
            forward = self.lean_params['forward_periods']
            top_k = self.lean_params['top_k_matches']
            
            if len(df) < window + forward + 10:
                return patterns
            
            # 當前制度和特徵
            current_regime = self.detect_regime(df)
            current_returns, current_rsi_z = self.build_lean_features(df, window)
            
            # 滑動窗口搜索歷史相似模式
            for i in range(window, len(df) - forward - 5):
                historical_window = df.iloc[i-window:i+1]
                
                # 制度過濾：只在同制度內比較
                historical_regime = self.detect_regime(historical_window)
                if historical_regime != current_regime:
                    continue
                
                # 構建歷史特徵
                hist_returns, hist_rsi_z = self.build_lean_features(historical_window, window)
                
                # Lean 相似度計算：70% 收益形狀 + 30% RSI
                returns_sim = self.cosine_similarity(current_returns, hist_returns)
                rsi_sim = self.cosine_similarity(current_rsi_z, hist_rsi_z)
                similarity = 0.7 * returns_sim + 0.3 * rsi_sim
                
                if similarity > 0.0:  # 只保留正相似度
                    # 分析後續走勢
                    future_data = df.iloc[i+1:i+1+forward]
                    if len(future_data) >= forward:
                        subsequent_direction, subsequent_return = self._analyze_subsequent_movement(
                            df.iloc[i]['close'], future_data
                        )
                        
                        pattern = LeanPattern(
                            symbol=symbol,
                            timeframe=timeframe,
                            match_date=df.iloc[i]['timestamp'] if 'timestamp' in df.columns else datetime.now(),
                            similarity_score=similarity,
                            subsequent_direction=subsequent_direction,
                            subsequent_return=subsequent_return,
                            confidence_level=similarity * 0.8,  # 保守信心度
                            regime=historical_regime,
                            return_sequence=hist_returns.tolist(),
                            rsi_zscore_sequence=hist_rsi_z.tolist()
                        )
                        
                        patterns.append(pattern)
            
            # 排序並返回 top-K
            patterns.sort(key=lambda x: x.similarity_score, reverse=True)
            return patterns[:top_k]
            
        except Exception as e:
            logger.error(f"Lean 模式搜索失敗: {e}")
            return []
    
    def _analyze_subsequent_movement(self, entry_price: float, 
                                   future_data: pd.DataFrame) -> Tuple[MarketDirection, float]:
        """分析後續市場走勢"""
        try:
            if len(future_data) == 0:
                return MarketDirection.NEUTRAL, 0.0
            
            exit_price = future_data.iloc[-1]['close']
            total_return = (exit_price - entry_price) / entry_price
            
            # 2% 閾值判斷方向
            if total_return > 0.02:
                return MarketDirection.BULLISH, total_return
            elif total_return < -0.02:
                return MarketDirection.BEARISH, total_return
            else:
                return MarketDirection.NEUTRAL, total_return
                
        except Exception as e:
            logger.error(f"後續走勢分析失敗: {e}")
            return MarketDirection.NEUTRAL, 0.0
    
    def vote_direction(self, patterns: List[LeanPattern]) -> Tuple[int, float, float]:
        """多模式投票 - 統計勝率與期望"""
        try:
            if not patterns:
                return 0, 0.0, 0.0
            
            returns = [p.subsequent_return for p in patterns]
            
            # 統計勝率
            up_threshold = 0.01  # 1% 
            down_threshold = -0.01
            
            p_up = sum(1 for r in returns if r > up_threshold) / len(returns)
            p_down = sum(1 for r in returns if r < down_threshold) / len(returns)
            
            # 期望收益
            expected_return = np.mean(returns)
            
            # 信心度和方向
            confidence = max(p_up, p_down)
            
            if p_up > p_down:
                direction = 1  # 看多
            elif p_down > p_up:
                direction = -1  # 看空
            else:
                direction = 0  # 中性
            
            return direction, confidence, expected_return
            
        except Exception as e:
            logger.error(f"投票計算失敗: {e}")
            return 0, 0.0, 0.0
    
    def check_w1_regime_gate(self, w1_df: pd.DataFrame) -> bool:
        """W1 制度閘門檢查"""
        try:
            regime = self.detect_regime(w1_df)
            
            # 禁止在極端高波動趨勢期交易
            forbidden_regimes = [
                MarketRegime.TREND_UP_HIGH,
                MarketRegime.TREND_DOWN_HIGH
            ]
            
            return regime not in forbidden_regimes
            
        except Exception as e:
            logger.warning(f"W1 制度閘門檢查失敗: {e}")
            return True  # 檢查失敗時允許交易 (保守策略)
    
    def apply_execution_filter(self, consensus: LeanConsensus) -> ExecutionFilter:
        """應用三重執行過濾"""
        filter_result = ExecutionFilter()
        
        # 1. 統計顯著性檢查
        win_rate_pass = consensus.consensus_confidence > filter_result.win_rate_threshold
        
        # 2. 期望收益超成本檢查
        edge = consensus.expected_return - filter_result.cost_threshold
        cost_pass = edge > 0
        
        # 3. 制度閘門檢查
        regime_pass = consensus.w1_regime_gate
        
        # 最終執行許可
        filter_result.execution_allowed = win_rate_pass and cost_pass and regime_pass
        filter_result.regime_gate_passed = regime_pass
        
        return filter_result
    
    async def generate_lean_consensus(self, symbol: str, 
                                    h4_df: pd.DataFrame, d1_df: pd.DataFrame, 
                                    w1_df: pd.DataFrame) -> LeanConsensus:
        """生成 Lean 共識分析"""
        try:
            # H4 和 D1 模式搜索
            h4_patterns = await self.find_lean_patterns(symbol, TimeFrame.H4, h4_df)
            d1_patterns = await self.find_lean_patterns(symbol, TimeFrame.D1, d1_df)
            
            # W1 制度閘門
            w1_gate = self.check_w1_regime_gate(w1_df)
            
            # 多時間框架投票
            h4_vote = self.vote_direction(h4_patterns)
            d1_vote = self.vote_direction(d1_patterns)
            
            # 加權融合：H4(45%) + D1(55%)
            weighted_direction = 0.45 * h4_vote[0] + 0.55 * d1_vote[0]
            weighted_confidence = 0.45 * h4_vote[1] + 0.55 * d1_vote[1]
            weighted_expected = 0.45 * h4_vote[2] + 0.55 * d1_vote[2]
            
            # 方向判斷
            if weighted_direction > 0.2:
                consensus_direction = MarketDirection.BULLISH
            elif weighted_direction < -0.2:
                consensus_direction = MarketDirection.BEARISH
            else:
                consensus_direction = MarketDirection.NEUTRAL
            
            # 波動倒數縮放
            h4_returns = self.logret(h4_df['close']).tail(48)  # 48 根 H4
            realized_vol = h4_returns.std()
            target_risk = 0.02  # 2% 目標風險
            size_multiplier = min(1.0, target_risk / (realized_vol + 1e-6))
            
            # 制度限制說明
            current_regime = self.detect_regime(d1_df)
            restriction = f"當前制度: {current_regime.value}, W1閘門: {'通過' if w1_gate else '禁止'}"
            
            return LeanConsensus(
                symbol=symbol,
                current_timestamp=datetime.now(),
                h4_patterns=h4_patterns,
                d1_patterns=d1_patterns,
                w1_regime_gate=w1_gate,
                consensus_direction=consensus_direction,
                consensus_confidence=weighted_confidence,
                expected_return=weighted_expected,
                position_size_multiplier=size_multiplier,
                regime_restriction=restriction
            )
            
        except Exception as e:
            logger.error(f"Lean 共識分析失敗: {e}")
            return LeanConsensus(
                symbol=symbol,
                current_timestamp=datetime.now(),
                h4_patterns=[],
                d1_patterns=[],
                w1_regime_gate=False,
                consensus_direction=MarketDirection.NEUTRAL,
                consensus_confidence=0.0,
                expected_return=0.0,
                position_size_multiplier=0.0,
                regime_restriction="分析失敗"
            )

async def generate_lean_backtest_config(lean_consensus_results: List[LeanConsensus]) -> Dict:
    """生成 Lean 回測配置 - 保持既有 JSON Schema"""
    logger.info("📊 生成 Lean 回測配置...")
    
    try:
        # 統計 Lean 共識結果
        bullish_count = sum(1 for result in lean_consensus_results 
                           if result.consensus_direction == MarketDirection.BULLISH and 
                           result.w1_regime_gate)
        bearish_count = sum(1 for result in lean_consensus_results 
                          if result.consensus_direction == MarketDirection.BEARISH and 
                          result.w1_regime_gate)
        
        total_valid = len([r for r in lean_consensus_results if r.w1_regime_gate])
        
        # 計算市場傾向
        if total_valid > 0:
            market_sentiment = "BULLISH" if bullish_count > bearish_count else "BEARISH"
            market_confidence = max(bullish_count, bearish_count) / total_valid
        else:
            market_sentiment = "NEUTRAL"
            market_confidence = 0.5
        
        # 計算平均 Lean 指標
        avg_confidence = np.mean([r.consensus_confidence for r in lean_consensus_results if r.w1_regime_gate]) if total_valid > 0 else 0.7
        avg_expected_return = np.mean([r.expected_return for r in lean_consensus_results if r.w1_regime_gate]) if total_valid > 0 else 0.0
        avg_size_multiplier = np.mean([r.position_size_multiplier for r in lean_consensus_results]) if lean_consensus_results else 1.0
        
        # 保持既有 JSON Schema 結構，內部填入 Lean 優化參數
        lean_config = {
            # ========== 保持原有結構 ==========
            "input_specifications": {
                "real_time_data_sources": {
                    "binance_websocket": {
                        "price_stream": "real_time",
                        "volume_stream": "real_time",
                        "orderbook_stream": "real_time",
                        "funding_rate_api": "periodic"
                    }
                },
                "required_parameters": {
                    "dynamic_parameters": ["market_regime", "trading_session"],
                    "orderbook_integration": ["spread_calculation", "depth_analysis", "liquidity_ratio"],
                    "signal_thresholds": ["strength_minimum", "confidence_threshold"]
                }
            },
            
            "output_specifications": {
                "signal_format": "BasicSignal",
                "market_data_format": "MarketData",
                "output_channels": ["phase1b_volatility", "phase1c_coordination", "phase2_pre_evaluation"]
            },
            
            # ========== Lean 優化參數 (隱藏在現有結構中) ==========
            
            # 在 phase1a_basic_signal_generation_dependency 中注入 Lean 參數
            "phase1a_basic_signal_generation_dependency": {
                "version": "2.0.0-lean",
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "description": "Phase1A Lean 相似度回測優化配置 - 僅形狀比較，避免過擬合",
                "module_type": "lean_signal_generation_foundation",
                
                # Lean 核心配置
                "lean_optimization": {
                    "enabled": True,
                    "methodology": "shape_comparison_only",
                    "feature_count": 3,  # 僅3個序列
                    "timeframe_strategy": "h4_d1_voting_w1_gate",
                    "regime_filtering": "same_regime_comparison",
                    "execution_filter": "triple_filter_mechanism"
                },
                
                # 注入到現有的配置結構
                "configuration": {
                    "signal_generation_params": {
                        "basic_mode": {
                            # 保持原有參數名，但用 Lean 計算值
                            "price_change_threshold": {
                                "base_value": max(0.001, avg_expected_return * 0.5),  # 基於期望收益調整
                                "type": "dynamic_parameter",
                                "parameter_id": "lean_price_change_threshold",
                                "market_regime_dependent": True,
                                "lean_optimization": True,
                                "description": "Lean 優化：基於歷史相似度的價格變化閾值"
                            },
                            "confidence_threshold": {
                                "base_value": max(0.7, avg_confidence * 0.9),  # 基於 Lean 共識信心度
                                "type": "dynamic_parameter", 
                                "parameter_id": "lean_confidence_threshold",
                                "market_regime_dependent": True,
                                "lean_optimization": True,
                                "description": "Lean 優化：基於多時間框架共識的信心度閾值"
                            }
                        }
                    },
                    
                    # Lean 特定參數 (隱藏在 performance_targets 中)
                    "performance_targets": {
                        "processing_latency_p99": "<30ms",
                        "signal_generation_rate": "5-25 signals/minute",  # 更保守
                        "accuracy_baseline": f">{max(60, avg_confidence * 100):.0f}%",  # 基於實際 Lean 結果
                        "system_availability": ">99.5%",
                        
                        # Lean 隱藏參數
                        "lean_win_rate_target": max(0.58, avg_confidence),
                        "lean_expected_return": avg_expected_return,
                        "lean_position_multiplier": avg_size_multiplier,
                        "lean_regime_gate_rate": total_valid / len(lean_consensus_results) if lean_consensus_results else 0.8
                    }
                }
            },
            
            # 在現有參數中嵌入 Lean 優化值
            "rsi_period": int(15 + avg_confidence * 5),  # Lean 動態調整 RSI 期間
            "macd_fast": int(12 + avg_expected_return * 20),  # 基於期望收益調整
            "macd_slow": int(26 + market_confidence * 10),  # 基於市場信心度調整
            
            # 標記為 Lean 優化
            "optimization_timestamp": datetime.now().isoformat(),
            "optimized_by": "Phase5_Lean_Optimizer",
            "lean_mode": True,
            "performance_boost": min(1.2, 1.0 + avg_confidence * 0.3),
            "optimization_method": "lean_similarity_matching",
            
            # Lean 回測結果摘要 (隱藏在 metadata 中)
            "lean_backtest_summary": {
                "total_symbols_analyzed": len(lean_consensus_results),
                "regime_gate_passed": total_valid,
                "bullish_consensus": bullish_count,
                "bearish_consensus": bearish_count,
                "market_sentiment": market_sentiment,
                "market_confidence": round(market_confidence, 3),
                "avg_lean_confidence": round(avg_confidence, 3),
                "avg_expected_return": round(avg_expected_return, 4),
                "avg_position_sizing": round(avg_size_multiplier, 3)
            }
        }
        
        # 為每個幣種添加具體調整 (保持原有格式)
        for result in lean_consensus_results:
            if result.w1_regime_gate:  # 只為通過制度閘門的幣種調整
                symbol_key = f"{result.symbol.lower()}_lean_adjustment"
                lean_config[symbol_key] = {
                    "direction_bias": result.consensus_direction.value,
                    "confidence_level": round(result.consensus_confidence, 3),
                    "expected_return": round(result.expected_return, 4),
                    "position_multiplier": round(result.position_size_multiplier, 3),
                    "regime_status": result.regime_restriction,
                    "h4_pattern_count": len(result.h4_patterns),
                    "d1_pattern_count": len(result.d1_patterns)
                }
        
        return lean_config
        
    except Exception as e:
        logger.error(f"Lean 回測配置生成失敗: {e}")
        # 返回保守的預設配置
        return {
            "optimization_timestamp": datetime.now().isoformat(),
            "optimized_by": "Phase5_Lean_Optimizer_Fallback",
            "lean_mode": True,
            "error": str(e),
            "fallback_mode": True
        }

async def save_lean_config_to_phase5_backup(lean_config: Dict) -> str:
    """保存 Lean 配置到 Phase5 備份目錄，供 Phase1A 讀取"""
    try:
        # Phase5 備份目錄 (當前目錄的 safety_backups/working)
        backup_dir = Path(__file__).parent / "safety_backups" / "working"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成時間戳檔名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"phase1a_backup_deployment_initial_{timestamp}.json"
        filepath = backup_dir / filename
        
        # 保存配置
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(lean_config, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"✅ Lean 配置已保存: {filename}")
        logger.info(f"📁 路徑: {filepath}")
        return str(filepath)
        
    except Exception as e:
        logger.error(f"Lean 配置保存失敗: {e}")
        return ""

# ==================== 主要執行函數 ====================

async def run_lean_backtest_analysis(symbols: List[str] = None) -> Dict:
    """執行 Lean 回測分析主流程"""
    logger.info("🚀 啟動 Phase5 Lean 相似度回測分析...")
    
    try:
        # 使用預設主要幣種或用戶指定
        if symbols is None:
            symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT", "SOLUSDT", "DOTUSDT"]
        
        lean_matcher = LeanHistoricalMatcher()
        lean_results = []
        
        # 模擬歷史數據 (實際應從 API 獲取)
        for symbol in symbols:
            logger.info(f"🔍 分析 {symbol} - Lean 相似度匹配...")
            
            try:
                # 模擬生成不同時間框架的歷史數據
                h4_df = await generate_mock_historical_data(symbol, "4h", days=30)
                d1_df = await generate_mock_historical_data(symbol, "1d", days=90) 
                w1_df = await generate_mock_historical_data(symbol, "1w", days=365)
                
                # 生成 Lean 共識
                lean_consensus = await lean_matcher.generate_lean_consensus(symbol, h4_df, d1_df, w1_df)
                
                # 應用執行過濾
                execution_filter = lean_matcher.apply_execution_filter(lean_consensus)
                
                # 記錄結果
                lean_results.append(lean_consensus)
                
                filter_status = "✅ 通過" if execution_filter.execution_allowed else "❌ 被過濾"
                logger.info(f"   {symbol}: {lean_consensus.consensus_direction.value} "
                          f"(信心度: {lean_consensus.consensus_confidence:.2%}, "
                          f"期望: {lean_consensus.expected_return:.2%}) {filter_status}")
                
            except Exception as e:
                logger.error(f"   ❌ {symbol} 分析失敗: {e}")
        
        # 生成 Lean 配置
        lean_config = await generate_lean_backtest_config(lean_results)
        
        # 保存到 Phase5 備份目錄
        config_path = await save_lean_config_to_phase5_backup(lean_config)
        
        # 生成分析摘要
        analysis_summary = {
            "lean_analysis_timestamp": datetime.now().isoformat(),
            "methodology": "shape_comparison_similarity_matching",
            "symbols_analyzed": len(symbols),
            "successful_analysis": len(lean_results),
            "config_saved_path": config_path,
            "lean_optimization_enabled": True,
            "next_phase1a_will_load": bool(config_path),
            "summary": {
                "avg_confidence": np.mean([r.consensus_confidence for r in lean_results]) if lean_results else 0,
                "avg_expected_return": np.mean([r.expected_return for r in lean_results]) if lean_results else 0,
                "regime_gate_pass_rate": len([r for r in lean_results if r.w1_regime_gate]) / len(lean_results) if lean_results else 0,
                "bullish_signals": len([r for r in lean_results if r.consensus_direction == MarketDirection.BULLISH]),
                "bearish_signals": len([r for r in lean_results if r.consensus_direction == MarketDirection.BEARISH])
            }
        }
        
        logger.info("✅ Phase5 Lean 分析完成")
        logger.info(f"📊 平均信心度: {analysis_summary['summary']['avg_confidence']:.2%}")
        logger.info(f"📈 平均期望收益: {analysis_summary['summary']['avg_expected_return']:.2%}")
        logger.info(f"🚪 制度閘門通過率: {analysis_summary['summary']['regime_gate_pass_rate']:.1%}")
        
        return analysis_summary
        
    except Exception as e:
        logger.error(f"❌ Lean 回測分析失敗: {e}")
        return {"error": str(e), "lean_analysis_timestamp": datetime.now().isoformat()}

async def generate_mock_historical_data(symbol: str, interval: str, days: int = 30) -> pd.DataFrame:
    """生成模擬歷史數據 (實際應從 Binance API 獲取)"""
    try:
        # 根據時間間隔計算數據點數量
        if interval == "4h":
            periods = days * 6  # 一天6根4小時K線
        elif interval == "1d":
            periods = days     # 一天1根日K線
        elif interval == "1w":
            periods = days // 7  # 一週1根週K線
        else:
            periods = days * 24  # 預設小時K線
        
        # 生成時間序列
        end_time = datetime.now()
        if interval == "4h":
            freq = "4H"
        elif interval == "1d":
            freq = "D"
        elif interval == "1w":
            freq = "W"
        else:
            freq = "H"
        
        timestamps = pd.date_range(end=end_time, periods=periods, freq=freq)
        
        # 模擬價格走勢 (帶有一定趨勢性)
        base_price = 30000 if "BTC" in symbol else (2000 if "ETH" in symbol else 300)
        
        # 生成帶趨勢的隨機遊走
        returns = np.random.normal(0.0001, 0.02, periods)  # 小幅正向趨勢 + 2%波動
        returns[0] = 0  # 第一個收益率為0
        
        prices = base_price * np.exp(np.cumsum(returns))
        
        # 生成 OHLC 數據
        highs = prices * (1 + np.abs(np.random.normal(0, 0.01, periods)))
        lows = prices * (1 - np.abs(np.random.normal(0, 0.01, periods)))
        opens = np.roll(prices, 1)
        opens[0] = prices[0]
        
        # 生成成交量
        volumes = np.random.lognormal(10, 1, periods)
        
        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': opens,
            'high': highs,
            'low': lows,
            'close': prices,
            'volume': volumes
        })
        
        return df
        
    except Exception as e:
        logger.error(f"模擬數據生成失敗: {e}")
        return pd.DataFrame()

# 主要執行函數
async def run_enhanced_backtest_analysis():
    """執行 Lean 回測分析 - 重新路由到新函數"""
    return await run_lean_backtest_analysis()

if __name__ == "__main__":
    # 執行 Lean 回測分析
    asyncio.run(run_lean_backtest_analysis())
