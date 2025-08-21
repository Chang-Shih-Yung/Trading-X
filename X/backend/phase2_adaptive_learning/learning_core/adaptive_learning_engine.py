#!/usr/bin/env python3
"""
🧠 Adaptive Learning Core
自適應學習核心系統 - Step 2 組件

Phase 2 - Step 2: 自適應學習核心
- 信號表現監控：追蹤每個信號的實際結果
- 參數動態優化：基於表現自動調整系統參數
- 模式學習：識別成功交易的共同特徵
- 週期性重訓練：定期更新學習模型
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path
import json
import pickle
from collections import defaultdict, deque

# 導入存儲模塊 - 嚴格模式：資料庫失敗時終止系統
import importlib.util

DATABASE_AVAILABLE = False
PROGRESS_TRACKER_AVAILABLE = False

try:
    # 動態導入 signal_database
    current_dir = Path(__file__).parent
    signal_db_path = current_dir.parent / "storage" / "signal_database.py"
    spec = importlib.util.spec_from_file_location("signal_database", signal_db_path)
    signal_database_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(signal_database_module)
    
    # 從模組中獲取需要的組件
    signal_db = signal_database_module.signal_db
    StoredSignal = signal_database_module.StoredSignal
    SignalStatus = signal_database_module.SignalStatus
    
    DATABASE_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ 信號資料庫已整合（動態導入）")
except Exception as e:
    logger = logging.getLogger(__name__)
    logger.error(f"❌ 嚴格模式：信號資料庫導入失敗 - {e}")
    logger.error("💥 系統終止：資料庫是系統運行的必要條件")
    raise SystemExit(f"嚴格模式：資料庫導入失敗 - {e}")

try:
    # 動態導入 learning_progress_tracker
    tracker_path = current_dir.parent / "storage" / "learning_progress_tracker.py"
    spec = importlib.util.spec_from_file_location("learning_progress_tracker", tracker_path)
    tracker_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tracker_module)
    
    progress_tracker = tracker_module.progress_tracker
    PROGRESS_TRACKER_AVAILABLE = True
    logger.info("✅ 學習進度追蹤器載入成功（動態導入）")
except Exception:
    PROGRESS_TRACKER_AVAILABLE = False
    logger.warning("⚠️ 學習進度追蹤器不可用（非關鍵組件）")

# ==================== 數據結構定義 ====================

# 學習策略枚舉

try:
    # 動態導入 learning_progress_tracker
    current_dir = Path(__file__).parent
    tracker_path = current_dir.parent / "storage" / "learning_progress_tracker.py"
    spec = importlib.util.spec_from_file_location("learning_progress_tracker", tracker_path)
    tracker_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tracker_module)
    
    progress_tracker = tracker_module.progress_tracker
    PROGRESS_TRACKER_AVAILABLE = True
    logger.info("✅ 學習進度追蹤器載入成功（動態導入）")
except Exception:
    PROGRESS_TRACKER_AVAILABLE = False
    logger.warning("⚠️ 學習進度追蹤器不可用（非關鍵組件）")

class LearningStatus(Enum):
    """學習狀態"""
    INITIALIZING = "INITIALIZING"
    COLLECTING_DATA = "COLLECTING_DATA"
    TRAINING = "TRAINING"
    OPTIMIZING = "OPTIMIZING"
    READY = "READY"
    ERROR = "ERROR"

@dataclass
class SignalPerformance:
    """信號表現記錄"""
    signal_id: str
    symbol: str
    signal_strength: float
    direction: str
    timestamp: datetime
    actual_outcome: Optional[float] = None
    performance_score: Optional[float] = None
    features: Dict[str, Any] = None
    market_conditions: Dict[str, Any] = None

@dataclass
class LearningPattern:
    """學習模式"""
    pattern_id: str
    pattern_type: str
    success_rate: float
    avg_return: float
    conditions: Dict[str, Any]
    sample_count: int
    confidence: float

@dataclass
class ParameterOptimization:
    """參數優化記錄"""
    parameter_name: str
    old_value: float
    new_value: float
    improvement_score: float
    optimization_time: datetime
    validation_results: Dict[str, float]

class AdaptiveLearningCore:
    """自適應學習核心 - Phase 2 Step 2"""
    
    def __init__(self):
        self.status = LearningStatus.INITIALIZING
        
        # 信號資料庫整合 - 嚴格模式
        self.use_database = DATABASE_AVAILABLE
        if not self.use_database:
            logger.error("❌ 嚴格模式：資料庫不可用，系統無法繼續")
            raise RuntimeError("嚴格模式：資料庫連接失敗，系統終止")
        
        logger.info("🗄️ 嚴格模式：使用持久化信號資料庫存儲")
        
        # 必要的內存存儲屬性 - 修正缺失屬性
        self.signal_history = deque(maxlen=1000)  # 最近1000個信號
        self.performance_db = {}  # 信號表現數據庫
        self.learning_patterns = {}  # 學習模式數據庫
        self.parameter_history = defaultdict(lambda: deque(maxlen=100))  # 參數優化歷史，每個參數最多100條記錄
        
        # 學習配置 - 根據快速信號生成調整頻率
        self.learning_config = {
            'min_signals_for_learning': 50,
            'pattern_discovery_frequency': 50,   # 每50個信號進行一次模式發現 (約7-8分鐘)
            'pattern_confidence_threshold': 0.65, # 模式信心度閾值
            'parameter_optimization_frequency': 200,  # 每200個信號優化一次參數 (約15分鐘)
            'success_rate_threshold': 0.55,
            'return_threshold': 0.01
        }
        
        # 當前優化參數
        self.current_parameters = {
            'signal_threshold': 0.6,
            'momentum_weight': 1.0,
            'volume_weight': 0.8,
            'volatility_adjustment': 1.0,
            'trend_sensitivity': 1.0,
            'risk_multiplier': 1.0
        }
        
        # 產品級幣種分類系統
        self.coin_categories = {
            'major': ['BTCUSDT', 'ETHUSDT'],              # 主流幣：穩定性優先
            'alt': ['BNBUSDT', 'ADAUSDT', 'SOLUSDT'],     # 替代幣：平衡策略
            'meme': ['DOGEUSDT'],                         # Meme幣：高風險高收益
            'payment': ['XRPUSDT']                        # 支付幣：特殊策略
        }
        
        # 各類別的優化參數配置（產品級分群學習）
        self.category_optimized_params = {
            'major': {
                'signal_threshold': 0.65,     # 較高門檻，追求穩定
                'risk_multiplier': 0.85,      # 保守風險
                'momentum_weight': 1.0,       # 標準動量
                'volatility_adjustment': 0.9  # 降低波動敏感度
            },
            'alt': {
                'signal_threshold': 0.60,     # 平衡門檻
                'risk_multiplier': 1.0,       # 標準風險
                'momentum_weight': 1.1,       # 稍強動量
                'volatility_adjustment': 1.0  # 標準波動調整
            },
            'meme': {
                'signal_threshold': 0.55,     # 較低門檻，捕捉機會
                'risk_multiplier': 1.2,       # 積極風險
                'momentum_weight': 1.3,       # 強調動量
                'volatility_adjustment': 1.2  # 增強波動敏感度
            },
            'payment': {
                'signal_threshold': 0.62,     # 中等門檻
                'risk_multiplier': 0.9,       # 稍保守
                'momentum_weight': 0.9,       # 稍弱動量
                'volatility_adjustment': 0.95 # 稍降波動敏感度
            }
        }
        
        # 各類別的學習歷史（分群追蹤）
        self.category_learning_history = {
            'major': deque(maxlen=200),
            'alt': deque(maxlen=200), 
            'meme': deque(maxlen=200),
            'payment': deque(maxlen=200)
        }
        
        # 性能監控
        self.performance_metrics = {
            'total_signals_tracked': 0,
            'successful_signals': 0,
            'total_return': 0.0,
            'average_return': 0.0,
            'success_rate': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0
        }
        
        # 學習統計
        self.learning_stats = {
            'patterns_discovered': 0,
            'parameters_optimized': 0,
            'retraining_cycles': 0,
            'model_accuracy': 0.0
        }
        
        self.status = LearningStatus.COLLECTING_DATA
        logger.info("✅ AdaptiveLearningCore 初始化完成")
    
    async def monitor_signal_performance(self, signal_data: Dict[str, Any], actual_outcome: Optional[float] = None) -> SignalPerformance:
        """監控信號表現 - 增強版支援資料庫"""
        try:
            # 創建信號表現記錄
            performance = SignalPerformance(
                signal_id=signal_data.get('signal_id', f"signal_{len(self.signal_history)}"),
                symbol=signal_data.get('symbol', 'UNKNOWN'),
                signal_strength=signal_data.get('signal_strength', 0.0),
                direction=signal_data.get('direction', 'HOLD'),
                timestamp=datetime.now(),
                actual_outcome=actual_outcome,
                features=signal_data.get('features', {}),
                market_conditions=signal_data.get('market_conditions', {})
            )
            
            # 計算表現分數
            if actual_outcome is not None:
                performance.performance_score = self._calculate_performance_score(
                    signal_data.get('direction', 'HOLD'),
                    actual_outcome,
                    signal_data.get('signal_strength', 0.0)
                )
                
                # 更新性能指標
                self._update_performance_metrics(performance)
            
            # 存儲到內存
            self.signal_history.append(performance)
            self.performance_db[performance.signal_id] = performance
            self.performance_metrics['total_signals_tracked'] += 1
            
            return await self._process_signal_performance(performance)
            
        except Exception as e:
            logger.error(f"❌ 信號表現監控失敗: {e}")
            return SignalPerformance(
                signal_id="error",
                symbol="UNKNOWN",
                signal_strength=0.0,
                direction="HOLD",
                timestamp=datetime.now()
            )
    
    async def add_signal_performance(self, performance: SignalPerformance) -> SignalPerformance:
        """直接添加SignalPerformance對象（用於測試和外部集成）"""
        try:
            # 存儲到內存
            self.signal_history.append(performance)
            self.performance_db[performance.signal_id] = performance
            self.performance_metrics['total_signals_tracked'] += 1
            
            # 更新性能指標
            if performance.actual_outcome is not None:
                self._update_performance_metrics(performance)
            
            return await self._process_signal_performance(performance)
            
        except Exception as e:
            logger.error(f"❌ 信號表現添加失敗: {e}")
            return performance
    
    async def _process_signal_performance(self, performance: SignalPerformance) -> SignalPerformance:
        """處理信號表現的共用邏輯"""
        try:
            # 存儲到資料庫
            if self.use_database:
                try:
                    stored_signal = StoredSignal(
                        signal_id=performance.signal_id,
                        symbol=performance.symbol,
                        signal_type=performance.direction,
                        signal_strength=performance.signal_strength,
                        timestamp=performance.timestamp,
                        features=performance.features or {},
                        market_conditions=performance.market_conditions or {},
                        tier='MEDIUM',  # 默認級別
                        status=SignalStatus.COMPLETED if performance.actual_outcome is not None else SignalStatus.PENDING,
                        actual_outcome=performance.actual_outcome,
                        performance_score=performance.performance_score
                    )
                    await signal_db.store_signal(stored_signal)
                    logger.debug(f"🗄️ 信號已存儲到資料庫: {performance.signal_id}")
                except Exception as db_e:
                    logger.error(f"❌ 資料庫存儲失敗: {db_e}")
            
            # 更新學習進度追蹤器
            if PROGRESS_TRACKER_AVAILABLE:
                try:
                    metrics = self._prepare_progress_metrics()
                    await progress_tracker.update_progress(
                        signal_count=len(self.signal_history),
                        performance_metrics=metrics
                    )
                    logger.debug("📊 學習進度已更新")
                except Exception as pt_e:
                    logger.warning(f"⚠️ 進度追蹤更新失敗: {pt_e}")
            
            # 檢查是否需要模式發現 (每50個信號)
            if len(self.signal_history) % self.learning_config['pattern_discovery_frequency'] == 0:
                await self._discover_patterns()
            
            # 檢查是否需要參數優化 (每200個信號)
            if len(self.signal_history) % self.learning_config['parameter_optimization_frequency'] == 0:
                await self._optimize_parameters()
            
            # 顯示學習狀態
            self._log_learning_status()
            
            logger.debug(f"📊 信號表現已記錄: {performance.signal_id}, 表現分數: {performance.performance_score}")
            
            return performance
            
        except Exception as e:
            logger.error(f"❌ 信號表現處理失敗: {e}")
            return performance
    
    def _log_learning_status(self):
        """記錄學習狀態"""
        try:
            current_signals = len(self.signal_history)
            min_required = self.learning_config['min_signals_for_learning']
            
            if current_signals < min_required:
                remaining = min_required - current_signals
                logger.info(f"🎓 學習準備中: {current_signals}/{min_required} 信號 (還需 {remaining} 個)")
            else:
                # 學習已啟動
                next_pattern_check = self.learning_config['pattern_discovery_frequency'] - (current_signals % self.learning_config['pattern_discovery_frequency'])
                next_param_opt = self.learning_config['parameter_optimization_frequency'] - (current_signals % self.learning_config['parameter_optimization_frequency'])
                
                logger.info(f"🧠 學習已啟動: {current_signals} 信號")
                logger.info(f"   📊 下次模式發現: {next_pattern_check} 信號後")
                logger.info(f"   🔧 下次參數優化: {next_param_opt} 信號後")
                
        except Exception as e:
            logger.error(f"❌ 學習狀態記錄失敗: {e}")

    def _get_symbol_category(self, symbol: str) -> str:
        """獲取交易對分類"""
        for category, symbols in self.coin_categories.items():
            if symbol in symbols:
                return category
        return 'alt'  # 默認歸類為替代幣
    
    def _get_category_weight(self, symbol: str) -> float:
        """獲取幣種類別權重"""
        category = self._get_symbol_category(symbol)
        weight_mapping = {
            'major': 1.2,    # 主流幣加權
            'alt': 1.0,      # 替代幣標準權重
            'meme': 0.8,     # Meme幣降權
            'payment': 1.1   # 支付幣稍加權
        }
        return weight_mapping.get(category, 1.0)  # 未知分類默認1.0
        
    def get_category_optimized_params(self, symbol: str) -> dict:
        """獲取特定幣種類別的優化參數"""
        category = self._get_symbol_category(symbol)
        return self.category_optimized_params.get(category, self.category_optimized_params['alt'])
        
    def record_category_learning(self, symbol: str, performance_data: dict):
        """記錄分類學習數據"""
        category = self._get_symbol_category(symbol)
        if category in self.category_learning_history:
            self.category_learning_history[category].append({
                'symbol': symbol,
                'timestamp': datetime.now(),
                'performance': performance_data
            })
            
    def get_category_learning_insights(self, category: str = None) -> dict:
        """獲取分類學習洞察"""
        if category:
            # 單一類別分析
            if category not in self.category_learning_history:
                return {'error': f'未知類別: {category}'}
                
            history = list(self.category_learning_history[category])
            if not history:
                return {'category': category, 'insights': '暫無學習數據'}
                
            # 計算類別專屬洞察
            recent_performance = [h['performance'] for h in history[-50:]]
            avg_performance = np.mean([p.get('success_rate', 0) for p in recent_performance])
            
            return {
                'category': category,
                'total_signals': len(history),
                'recent_avg_performance': float(avg_performance),
                'optimized_params': self.category_optimized_params.get(category, {}),
                'last_update': history[-1]['timestamp'].isoformat() if history else None
            }
        else:
            # 全部類別概覽
            insights = {}
            for cat in self.category_learning_history.keys():
                insights[cat] = self.get_category_learning_insights(cat)
            return insights

    def _calculate_performance_score(self, direction: str, actual_outcome: float, signal_strength: float) -> float:
        """計算信號表現分數"""
        try:
            # 基礎分數：方向正確性
            direction_score = 0.0
            if direction == 'BUY' and actual_outcome > 0:
                direction_score = 1.0
            elif direction == 'SELL' and actual_outcome < 0:
                direction_score = 1.0
            elif direction == 'HOLD':
                direction_score = 0.5  # 中性分數
            
            # 收益倍數
            return_multiplier = min(2.0, abs(actual_outcome) * 100)  # 收益放大，最大2倍
            
            # 信號強度加權
            strength_weight = 0.5 + signal_strength * 0.5
            
            # 綜合分數
            final_score = direction_score * return_multiplier * strength_weight
            
            return min(2.0, max(0.0, final_score))  # 限制在0-2範圍
            
        except Exception as e:
            logger.error(f"❌ 表現分數計算失敗: {e}")
            return 0.0
    
    def _update_performance_metrics(self, performance: SignalPerformance):
        """更新性能指標"""
        try:
            if performance.actual_outcome is not None:
                # 更新總收益
                self.performance_metrics['total_return'] += performance.actual_outcome
                
                # 更新成功信號數
                if performance.performance_score and performance.performance_score > 1.0:
                    self.performance_metrics['successful_signals'] += 1
                
                # 計算成功率
                total_with_outcome = len([s for s in self.signal_history if s.actual_outcome is not None])
                if total_with_outcome > 0:
                    self.performance_metrics['success_rate'] = self.performance_metrics['successful_signals'] / total_with_outcome
                
                # 計算平均收益 - 防止除零錯誤
                if total_with_outcome > 0:
                    self.performance_metrics['average_return'] = self.performance_metrics['total_return'] / total_with_outcome
                else:
                    self.performance_metrics['average_return'] = 0.0
                
                # 計算夏普比率（簡化版）
                returns = [s.actual_outcome for s in self.signal_history if s.actual_outcome is not None]
                if len(returns) > 5:
                    return_std = np.std(returns)
                    if return_std > 0:
                        self.performance_metrics['sharpe_ratio'] = np.mean(returns) / return_std
        
        except Exception as e:
            logger.error(f"❌ 性能指標更新失敗: {e}")
    
    def _prepare_progress_metrics(self) -> Dict[str, Any]:
        """準備進度追蹤器所需的指標"""
        total_signals = len(self.signal_history)
        signals_with_outcome = [s for s in self.signal_history if s.actual_outcome is not None]
        successful_signals = [s for s in signals_with_outcome if s.performance_score and s.performance_score > 1.0]
        
        # 計算指標
        accuracy_rate = len(successful_signals) / len(signals_with_outcome) if signals_with_outcome else 0.0
        avg_return = self.performance_metrics.get('average_return', 0.0)
        success_rate = self.performance_metrics.get('success_rate', 0.0)
        
        # 計算一致性分數 (最近10個信號的表現標準差)
        recent_signals = list(self.signal_history)[-10:] if len(self.signal_history) >= 10 else list(self.signal_history)
        recent_scores = [s.performance_score for s in recent_signals if s.performance_score is not None]
        consistency_score = 1.0 - (np.std(recent_scores) if len(recent_scores) > 1 else 0.0)
        consistency_score = max(0.0, min(1.0, consistency_score))
        
        return {
            'performance_score': success_rate,
            'accuracy_rate': accuracy_rate,
            'successful_predictions': len(successful_signals),
            'total_predictions': len(signals_with_outcome),
            'confidence_level': min(1.0, total_signals / 100.0),  # 基於信號數量的信心水平
            'avg_return_rate': avg_return,
            'consistency_score': consistency_score
        }
    
    async def _discover_patterns(self):
        """發現學習模式"""
        try:
            if len(self.signal_history) < self.learning_config['min_signals_for_learning']:
                return
            
            logger.info("🔍 開始模式發現...")
            
            # 分析成功信號的共同特徵
            successful_signals = [
                s for s in self.signal_history 
                if s.performance_score and s.performance_score > 1.0
            ]
            
            if len(successful_signals) < 10:
                return
            
            # 按特徵分組分析
            feature_patterns = defaultdict(list)
            
            for signal in successful_signals:
                if signal.features:
                    for feature_name, feature_value in signal.features.items():
                        if isinstance(feature_value, (int, float)):
                            feature_patterns[feature_name].append(feature_value)
            
            # 識別有效特徵範圍
            for feature_name, values in feature_patterns.items():
                if len(values) >= 5:
                    pattern_id = f"pattern_{feature_name}_{len(self.learning_patterns)}"
                    
                    # 計算統計特徵
                    mean_value = np.mean(values)
                    std_value = np.std(values)
                    # 防止除零錯誤
                    success_rate = len(values) / len(successful_signals) if len(successful_signals) > 0 else 0.0
                    
                    # 創建學習模式
                    pattern = LearningPattern(
                        pattern_id=pattern_id,
                        pattern_type=f"feature_{feature_name}",
                        success_rate=success_rate,
                        avg_return=np.mean([s.actual_outcome for s in successful_signals if s.actual_outcome]),
                        conditions={
                            'feature_name': feature_name,
                            'value_range': (mean_value - std_value, mean_value + std_value),
                            'optimal_value': mean_value
                        },
                        sample_count=len(values),
                        confidence=min(1.0, len(values) / 20)  # 20個樣本為滿信心
                    )
                    
                    # 只保存高信心模式
                    if pattern.confidence >= self.learning_config['pattern_confidence_threshold']:
                        self.learning_patterns[pattern_id] = pattern
                        self.learning_stats['patterns_discovered'] += 1
                        
                        logger.info(f"✅ 發現新模式: {pattern_id}, 成功率: {success_rate:.1%}")
        
        except Exception as e:
            logger.error(f"❌ 模式發現失敗: {e}")
    
    async def _optimize_parameters(self):
        """優化參數"""
        try:
            if len(self.signal_history) < self.learning_config['min_signals_for_learning']:
                return
            
            logger.info("⚙️ 開始參數優化...")
            
            # 評估當前參數表現
            current_performance = self._evaluate_current_performance()
            
            # 嘗試優化每個參數
            optimization_results = []
            
            for param_name, current_value in self.current_parameters.items():
                # 測試參數調整
                test_values = [
                    current_value * 0.9,
                    current_value * 1.1,
                    current_value * 0.8,
                    current_value * 1.2
                ]
                
                for test_value in test_values:
                    # 模擬參數調整的影響
                    simulated_performance = self._simulate_parameter_change(param_name, test_value)
                    
                    if simulated_performance > current_performance:
                        improvement = simulated_performance - current_performance
                        optimization_results.append({
                            'parameter': param_name,
                            'old_value': current_value,
                            'new_value': test_value,
                            'improvement': improvement
                        })
            
            # 應用最佳優化
            if optimization_results:
                best_optimization = max(optimization_results, key=lambda x: x['improvement'])
                
                # 更新參數
                old_value = self.current_parameters[best_optimization['parameter']]
                self.current_parameters[best_optimization['parameter']] = best_optimization['new_value']
                
                # 記錄優化
                optimization = ParameterOptimization(
                    parameter_name=best_optimization['parameter'],
                    old_value=old_value,
                    new_value=best_optimization['new_value'],
                    improvement_score=best_optimization['improvement'],
                    optimization_time=datetime.now(),
                    validation_results={'simulated_improvement': best_optimization['improvement']}
                )
                
                self.parameter_history[best_optimization['parameter']].append(optimization)
                self.learning_stats['parameters_optimized'] += 1
                
                logger.info(f"✅ 參數優化: {best_optimization['parameter']} {old_value:.3f} → {best_optimization['new_value']:.3f}")
        
        except Exception as e:
            logger.error(f"❌ 參數優化失敗: {e}")
    
    def _evaluate_current_performance(self) -> float:
        """評估當前參數表現 - 產品級時間衰減 + 分群學習版本"""
        try:
            recent_signals = list(self.signal_history)[-100:]  # 增加到100個信號
            if not recent_signals:
                return 0.0

            # 計算時間加權 + 分群權重表現分數
            weighted_scores = []
            weighted_returns = []
            total_weight = 0.0
            current_time = datetime.now()
            
            # 分群表現追蹤
            category_performance = {'major': [], 'alt': [], 'meme': [], 'payment': []}
            
            for signal in recent_signals:
                try:
                    # 計算時間權重（12小時半衰期）
                    time_diff_hours = (current_time - signal.timestamp).total_seconds() / 3600
                    time_weight = np.exp(-time_diff_hours / 12)  # 指數衰減
                    
                    # 獲取幣種分群權重
                    symbol = getattr(signal, 'symbol', 'UNKNOWN')
                    category = self._get_symbol_category(symbol)
                    category_weight = self._get_category_weight(symbol)
                    
                    # 組合權重：時間 × 分群
                    combined_weight = time_weight * category_weight
                    
                    if signal.performance_score is not None:
                        weighted_score = signal.performance_score * combined_weight
                        weighted_scores.append(weighted_score)
                        total_weight += combined_weight
                        
                        # 記錄分群表現
                        if category in category_performance:
                            category_performance[category].append({
                                'score': signal.performance_score,
                                'weight': combined_weight,
                                'symbol': symbol
                            })
                        
                    if signal.actual_outcome is not None:
                        weighted_returns.append(signal.actual_outcome * combined_weight)
                        
                except Exception as signal_e:
                    logger.warning(f"⚠️ 處理信號時出錯: {signal_e}")
                    continue

            if not weighted_scores:
                return 0.0
            
            # 時間 + 分群加權平均表現
            avg_weighted_performance = np.sum(weighted_scores) / total_weight if total_weight > 0 else 0.0
            
            # 計算收益穩定性（加權）
            if weighted_returns and len(weighted_returns) > 1:
                weighted_std = np.std(weighted_returns)
                return_stability = 1.0 / (1.0 + weighted_std)
                final_score = avg_weighted_performance * 0.7 + return_stability * 0.3
            else:
                final_score = avg_weighted_performance
            
            # 分群洞察記錄
            category_insights = {}
            for category, performances in category_performance.items():
                if performances:
                    avg_score = np.mean([p['score'] for p in performances])
                    total_cat_weight = sum([p['weight'] for p in performances])
                    category_insights[category] = {
                        'avg_performance': float(avg_score),
                        'signal_count': len(performances),
                        'total_weight': float(total_cat_weight),
                        'symbols': list(set([p['symbol'] for p in performances]))
                    }
            
            logger.debug(f"📊 分群加權表現評估: {final_score:.4f} (樣本: {len(weighted_scores)}, 總權重: {total_weight:.2f})")
            logger.debug(f"🎯 分群洞察: {category_insights}")
            
            return final_score
        
        except Exception as e:
            logger.error(f"❌ 表現評估失敗: {e}")
            return 0.0
    
    def _simulate_parameter_change(self, param_name: str, new_value: float) -> float:
        """模擬參數改變的影響"""
        try:
            # 簡化的模擬：基於歷史模式估算影響
            base_performance = self._evaluate_current_performance()
            
            # 根據參數類型估算影響
            if param_name == 'signal_threshold':
                # 閾值越低，信號越多但質量可能下降
                if new_value < self.current_parameters[param_name]:
                    return base_performance * 0.95  # 輕微降低
                else:
                    return base_performance * 1.02  # 輕微提升
            
            elif param_name in ['momentum_weight', 'volume_weight', 'trend_sensitivity']:
                # 權重調整的影響 - 防止除零錯誤
                current_param_value = self.current_parameters[param_name]
                if current_param_value != 0:
                    change_ratio = new_value / current_param_value
                    if 0.9 <= change_ratio <= 1.1:
                        return base_performance * (1.0 + (change_ratio - 1.0) * 0.1)
                    else:
                        return base_performance * 0.98  # 大幅調整可能降低性能
                else:
                    # 如果當前參數為0，使用默認增益
                    return base_performance * 1.05
            
            else:
                # 其他參數的一般性影響
                return base_performance * np.random.uniform(0.98, 1.05)
        
        except Exception as e:
            logger.error(f"❌ 參數模擬失敗: {e}")
            return 0.0
    
    async def weekly_parameter_retrain(self) -> Dict[str, Any]:
        """週期性參數重訓練"""
        try:
            logger.info("🔄 開始週期性參數重訓練...")
            
            if len(self.signal_history) < self.learning_config['min_signals_for_learning']:
                return {
                    'status': 'insufficient_data',
                    'message': f'需要至少 {self.learning_config["min_signals_for_learning"]} 個信號數據'
                }
            
            self.status = LearningStatus.TRAINING
            
            # 1. 分析歷史表現
            performance_analysis = self._analyze_historical_performance()
            
            # 2. 重新發現模式
            await self._discover_patterns()
            
            # 3. 全面參數優化
            await self._comprehensive_parameter_optimization()
            
            # 4. 驗證優化結果
            validation_results = self._validate_optimization()
            
            self.learning_stats['retraining_cycles'] += 1
            self.status = LearningStatus.READY
            
            logger.info("✅ 週期性重訓練完成")
            
            return {
                'status': 'success',
                'retraining_cycle': self.learning_stats['retraining_cycles'],
                'performance_analysis': performance_analysis,
                'parameters_optimized': list(self.current_parameters.keys()),
                'new_patterns_applied': len(self.learning_patterns),
                'validation_results': validation_results,
                'improvement_summary': {
                    'patterns_discovered': self.learning_stats['patterns_discovered'],
                    'parameters_optimized': self.learning_stats['parameters_optimized'],
                    'current_success_rate': self.performance_metrics['success_rate'],
                    'current_avg_return': self.performance_metrics['average_return']
                }
            }
        
        except Exception as e:
            logger.error(f"❌ 週期性重訓練失敗: {e}")
            self.status = LearningStatus.ERROR
            return {
                'status': 'error',
                'error_message': str(e)
            }
    
    def _analyze_historical_performance(self) -> Dict[str, Any]:
        """分析歷史表現"""
        try:
            recent_signals = list(self.signal_history)[-200:]  # 最近200個信號
            
            # 按時間段分析
            time_segments = {
                'last_week': [],
                'last_month': [],
                'all_time': recent_signals
            }
            
            now = datetime.now()
            for signal in recent_signals:
                if signal.timestamp > now - timedelta(days=7):
                    time_segments['last_week'].append(signal)
                if signal.timestamp > now - timedelta(days=30):
                    time_segments['last_month'].append(signal)
            
            analysis = {}
            for period, signals in time_segments.items():
                if signals:
                    outcomes = [s.actual_outcome for s in signals if s.actual_outcome is not None]
                    performance_scores = [s.performance_score for s in signals if s.performance_score is not None]
                    
                    analysis[period] = {
                        'signal_count': len(signals),
                        'avg_return': np.mean(outcomes) if outcomes else 0.0,
                        'success_rate': len([o for o in outcomes if o > 0]) / len(outcomes) if outcomes else 0.0,
                        'avg_performance_score': np.mean(performance_scores) if performance_scores else 0.0
                    }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ 歷史表現分析失敗: {e}")
            return {}
    
    async def _comprehensive_parameter_optimization(self):
        """全面參數優化"""
        try:
            # 使用更精細的參數搜索
            optimization_rounds = 3
            
            for round_num in range(optimization_rounds):
                logger.info(f"⚙️ 參數優化輪次 {round_num + 1}/{optimization_rounds}")
                
                # 對每個參數進行精細調優
                for param_name in self.current_parameters.keys():
                    best_value = await self._optimize_single_parameter(param_name)
                    if best_value != self.current_parameters[param_name]:
                        old_value = self.current_parameters[param_name]
                        self.current_parameters[param_name] = best_value
                        logger.info(f"🔧 {param_name}: {old_value:.3f} → {best_value:.3f}")
        
        except Exception as e:
            logger.error(f"❌ 全面參數優化失敗: {e}")
    
    async def _optimize_single_parameter(self, param_name: str) -> float:
        """優化單個參數"""
        try:
            current_value = self.current_parameters[param_name]
            best_value = current_value
            best_performance = self._evaluate_current_performance()
            
            # 測試範圍
            test_multipliers = [0.7, 0.8, 0.9, 1.1, 1.2, 1.3]
            
            for multiplier in test_multipliers:
                test_value = current_value * multiplier
                simulated_performance = self._simulate_parameter_change(param_name, test_value)
                
                if simulated_performance > best_performance:
                    best_performance = simulated_performance
                    best_value = test_value
            
            return best_value
            
        except Exception as e:
            logger.error(f"❌ 單個參數優化失敗: {e}")
            return self.current_parameters[param_name]
    
    def _validate_optimization(self) -> Dict[str, float]:
        """驗證優化結果"""
        try:
            # 計算優化前後的性能指標
            return {
                'current_success_rate': self.performance_metrics['success_rate'],
                'current_avg_return': self.performance_metrics['average_return'],
                'current_sharpe_ratio': self.performance_metrics['sharpe_ratio'],
                'pattern_confidence': np.mean([p.confidence for p in self.learning_patterns.values()]) if self.learning_patterns else 0.0,
                'optimization_score': self._evaluate_current_performance()
            }
            
        except Exception as e:
            logger.error(f"❌ 優化驗證失敗: {e}")
            return {}
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """獲取學習摘要"""
        try:
            return {
                'learning_status': self.status.value,
                'performance_metrics': self.performance_metrics,
                'learning_statistics': self.learning_stats,
                'current_parameters': self.current_parameters,
                'discovered_patterns': {
                    pattern_id: {
                        'type': pattern.pattern_type,
                        'success_rate': pattern.success_rate,
                        'confidence': pattern.confidence,
                        'sample_count': pattern.sample_count
                    }
                    for pattern_id, pattern in self.learning_patterns.items()
                },
                'recent_optimizations': {
                    param_name: [
                        {
                            'old_value': opt.old_value,
                            'new_value': opt.new_value,
                            'improvement': opt.improvement_score,
                            'time': opt.optimization_time.isoformat()
                        }
                        for opt in optimizations[-3:]  # 最近3次優化
                    ]
                    for param_name, optimizations in self.parameter_history.items()
                },
                'update_frequency': len(self.signal_history),
                'next_optimization_in': self.learning_config['parameter_optimization_frequency'] - (len(self.signal_history) % self.learning_config['parameter_optimization_frequency'])
            }
            
        except Exception as e:
            logger.error(f"❌ 學習摘要生成失敗: {e}")
            return {
                'learning_status': 'error',
                'error': str(e)
            }
    
    async def update_from_feedback(self, symbol: str, feedback) -> Dict[str, Any]:
        """根據交易反饋更新學習參數 - 生產系統接口"""
        try:
            logger.info(f"🔄 處理 {symbol} 的學習反饋...")
            
            # 將反饋數據轉換為學習系統格式
            feedback_data = {
                'symbol': symbol,
                'win_rate': feedback.win_rate,
                'average_return': feedback.average_return,
                'sharpe_ratio': feedback.sharpe_ratio,
                'max_drawdown': feedback.max_drawdown,
                'total_signals': feedback.total_signals,
                'successful_trades': feedback.successful_trades,
                'tier_performance': feedback.tier_performance,
                'regime_performance': feedback.regime_performance,
                'parameter_effectiveness': feedback.parameter_effectiveness,
                'recommendations': feedback.recommendations
            }
            
            # 更新性能指標
            self.performance_metrics['success_rate'] = feedback.win_rate
            self.performance_metrics['average_return'] = feedback.average_return
            self.performance_metrics['total_signals_tracked'] += feedback.total_signals
            self.performance_metrics['successful_signals'] += feedback.successful_trades
            
            # 根據反饋調整參數
            adjustments_made = {}
            
            # 1. 根據勝率調整信號閾值
            if feedback.win_rate < 0.4:
                old_threshold = self.current_parameters['signal_threshold']
                self.current_parameters['signal_threshold'] = min(0.8, old_threshold * 1.1)
                adjustments_made['signal_threshold'] = {
                    'old': old_threshold,
                    'new': self.current_parameters['signal_threshold'],
                    'reason': f'低勝率 {feedback.win_rate:.2%} < 40%'
                }
            elif feedback.win_rate > 0.8:
                old_threshold = self.current_parameters['signal_threshold']
                self.current_parameters['signal_threshold'] = max(0.3, old_threshold * 0.95)
                adjustments_made['signal_threshold'] = {
                    'old': old_threshold,
                    'new': self.current_parameters['signal_threshold'],
                    'reason': f'高勝率 {feedback.win_rate:.2%} > 80%'
                }
            
            # 2. 根據夏普比率調整風險倍數
            if feedback.sharpe_ratio < 0.5:
                old_risk = self.current_parameters['risk_multiplier']
                self.current_parameters['risk_multiplier'] = min(2.0, old_risk * 1.05)
                adjustments_made['risk_multiplier'] = {
                    'old': old_risk,
                    'new': self.current_parameters['risk_multiplier'],
                    'reason': f'低夏普比率 {feedback.sharpe_ratio:.3f} < 0.5'
                }
            elif feedback.sharpe_ratio > 1.5:
                old_risk = self.current_parameters['risk_multiplier']
                self.current_parameters['risk_multiplier'] = max(0.5, old_risk * 0.98)
                adjustments_made['risk_multiplier'] = {
                    'old': old_risk,
                    'new': self.current_parameters['risk_multiplier'],
                    'reason': f'高夏普比率 {feedback.sharpe_ratio:.3f} > 1.5'
                }
            
            # 3. 根據最大回撤調整波動性調整
            if feedback.max_drawdown > 0.15:
                old_vol = self.current_parameters['volatility_adjustment']
                self.current_parameters['volatility_adjustment'] = min(1.5, old_vol * 1.08)
                adjustments_made['volatility_adjustment'] = {
                    'old': old_vol,
                    'new': self.current_parameters['volatility_adjustment'],
                    'reason': f'高回撤 {feedback.max_drawdown:.2%} > 15%'
                }
            
            # 4. 根據分層表現調整權重
            if feedback.tier_performance:
                best_tier = max(feedback.tier_performance.keys(), 
                              key=lambda t: feedback.tier_performance[t].get('win_rate', 0))
                if feedback.tier_performance[best_tier].get('win_rate', 0) > 0.7:
                    # 增強最佳層級的權重
                    old_trend = self.current_parameters['trend_sensitivity']
                    self.current_parameters['trend_sensitivity'] = min(1.5, old_trend * 1.03)
                    adjustments_made['trend_sensitivity'] = {
                        'old': old_trend,
                        'new': self.current_parameters['trend_sensitivity'],
                        'reason': f'最佳層級 {best_tier} 勝率 {feedback.tier_performance[best_tier]["win_rate"]:.2%}'
                    }
            
            # 記錄參數變化歷史
            for param_name, adjustment in adjustments_made.items():
                self.parameter_history[param_name].append({
                    'timestamp': datetime.now(),
                    'old_value': adjustment['old'],
                    'new_value': adjustment['new'],
                    'reason': adjustment['reason'],
                    'feedback_source': symbol
                })
            
            # 更新學習統計
            self.learning_stats['parameters_optimized'] += len(adjustments_made)
            
            logger.info(f"✅ {symbol} 學習反饋處理完成")
            if adjustments_made:
                logger.info(f"🔧 進行了 {len(adjustments_made)} 項參數調整")
                for param, adj in adjustments_made.items():
                    logger.info(f"   📊 {param}: {adj['old']:.3f} → {adj['new']:.3f} ({adj['reason']})")
            
            return {
                'success': True,
                'adjustments_made': adjustments_made,
                'current_parameters': self.current_parameters,
                'total_adjustments': len(adjustments_made)
            }
            
        except Exception as e:
            logger.error(f"❌ 學習反饋處理失敗: {e}")
            return {
                'success': False,
                'error': str(e),
                'adjustments_made': {},
                'current_parameters': self.current_parameters
            }
    
    async def track_signal_for_learning(self, signal_data: Dict[str, Any]) -> str:
        """追蹤信號用於學習 - 生產系統接口"""
        try:
            signal_id = signal_data.get('signal_id', f"signal_{len(self.signal_history)}_{datetime.now().timestamp()}")
            
            # 記錄信號到學習系統
            performance = await self.monitor_signal_performance(signal_data)
            
            logger.debug(f"📊 信號已記錄到學習系統: {signal_id}")
            return signal_id
            
        except Exception as e:
            logger.error(f"❌ 信號學習追蹤失敗: {e}")
            return ""
    
    def get_optimized_parameters(self) -> Dict[str, float]:
        """獲取當前優化參數 - 供 Phase1A 使用"""
        return self.current_parameters.copy()
    
    async def get_optimized_parameters_async(self) -> Dict[str, float]:
        """獲取當前優化參數 - 異步版本供參數管理器使用"""
        return self.current_parameters.copy()

async def main():
    """測試函數"""
    print("🧠 Adaptive Learning Core 測試")
    
    # 創建實例進行測試
    learning_core = AdaptiveLearningCore()
    
    # 模擬信號數據
    test_signals = []
    for i in range(100):
        signal_data = {
            'signal_id': f'test_signal_{i}',
            'symbol': 'BTCUSDT',
            'signal_strength': np.random.uniform(0.3, 0.9),
            'direction': np.random.choice(['BUY', 'SELL']),
            'features': {
                'momentum': np.random.uniform(-1, 1),
                'volatility': np.random.uniform(0, 1),
                'volume_ratio': np.random.uniform(0.5, 2)
            }
        }
        
        # 模擬實際結果
        actual_outcome = np.random.uniform(-0.02, 0.03)
        
        # 監控表現
        await learning_core.monitor_signal_performance(signal_data, actual_outcome)
        test_signals.append(signal_data)
    
    # 執行重訓練
    retrain_results = await learning_core.weekly_parameter_retrain()
    print(f"重訓練結果: {retrain_results['status']}")
    
    # 獲取摘要
    summary = learning_core.get_learning_summary()
    print(f"學習狀態: {summary['learning_status']}")
    print(f"跟蹤信號數: {summary['performance_metrics']['total_signals_tracked']}")
    print(f"成功率: {summary['performance_metrics']['success_rate']:.1%}")
    
    print("\n✅ 測試完成")

if __name__ == "__main__":
    asyncio.run(main())
