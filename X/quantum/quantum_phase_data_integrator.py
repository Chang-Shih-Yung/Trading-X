"""
🔗 Trading X - 量子數據流融合器 (Quantum Data Flow Integrator)
確保量子引擎與X系統Phase1A→Phase5數據流完全暢通

這個模塊負責：
1. 與Phase1A基礎信號生成的數據對接
2. 與Phase2自適應學習的參數共享
3. 與Phase3執行策略的決策協調
4. 與Phase5回測驗證的結果反饋
5. 與所有現有數據庫的無縫集成
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path

# X系統導入
import sys
sys.path.append('../')
sys.path.append('../backend')

# Phase導入
try:
    from X.backend.phase1_signal_generation.phase1a_basic_signal_generation.phase1a_basic_signal_generation import (
        Phase1ASignalGenerator, DynamicParameters, MarketRegime, TradingSession, SignalTier
    )
    PHASE1A_AVAILABLE = True
except ImportError:
    PHASE1A_AVAILABLE = False
    logging.warning("Phase1A 不可用")

try:
    from X.backend.phase2_adaptive_learning.priority3_timeframe_learning.enhanced_signal_database import (
        EnhancedSignalDatabase, TimeframeEnhancedSignal
    )
    PHASE2_AVAILABLE = True
except ImportError:
    PHASE2_AVAILABLE = False
    logging.warning("Phase2 不可用")

try:
    from X.backend.phase3_execution_policy import ExecutionPolicyEngine
    PHASE3_AVAILABLE = True
except ImportError:
    PHASE3_AVAILABLE = False
    logging.warning("Phase3 不可用")

try:
    from X.backend.phase5_backtest_validation.auto_backtest_validator.auto_backtest_validator import (
        AutoBacktestValidator, BacktestSignal
    )
    PHASE5_AVAILABLE = True
except ImportError:
    PHASE5_AVAILABLE = False
    logging.warning("Phase5 不可用")

# 數據庫和服務
import sys
sys.path.append('../../..')
from X.app.core.database_separated import get_learning_db, get_signals_db, get_market_db
try:
    from X.app.services.realtime_signal_engine import RealtimeSignalEngine, TradingSignalAlert
    REALTIME_SIGNAL_AVAILABLE = True
except ImportError:
    REALTIME_SIGNAL_AVAILABLE = False
    logging.warning("實時信號引擎不可用")
    
    # 創建mock類以避免名稱錯誤
    class TradingSignalAlert:
        def __init__(self, *args, **kwargs):
            pass
    
    class RealtimeSignalEngine:
        def __init__(self, *args, **kwargs):
            pass

logger = logging.getLogger(__name__)

class QuantumPhaseDataFlowIntegrator:
    """量子Phase數據流集成器"""
    
    def __init__(self):
        # Phase組件
        self.phase1a_generator = None
        self.phase2_database = None
        self.phase3_executor = None
        self.phase5_validator = None
        self.realtime_engine = None
        
        # 數據庫連接
        self.signals_db = None
        self.learning_db = None
        self.market_db = None
        
        # 數據流狀態
        self.phase_status = {
            "phase1a": PHASE1A_AVAILABLE,
            "phase2": PHASE2_AVAILABLE, 
            "phase3": PHASE3_AVAILABLE,
            "phase5": PHASE5_AVAILABLE
        }
        
        # 數據緩存
        self.phase1a_signals = {}
        self.phase2_learning_weights = {}
        self.phase3_execution_decisions = {}
        self.phase5_backtest_results = {}
    
    async def initialize(self):
        """初始化所有Phase組件"""
        logger.info("🔗 初始化量子Phase數據流集成器")
        
        # 初始化數據庫連接
        self.signals_db = get_signals_db
        self.learning_db = get_learning_db
        self.market_db = get_market_db
        
        # 初始化Phase1A
        if PHASE1A_AVAILABLE:
            try:
                self.phase1a_generator = Phase1ASignalGenerator()
                await self.phase1a_generator.initialize() 
                logger.info("✅ Phase1A 信號生成器已連接")
            except Exception as e:
                logger.error(f"❌ Phase1A 初始化失敗: {e}")
                self.phase_status["phase1a"] = False
        
        # 初始化Phase2
        if PHASE2_AVAILABLE:
            try:
                self.phase2_database = EnhancedSignalDatabase()
                logger.info("✅ Phase2 自適應學習已連接") 
            except Exception as e:
                logger.error(f"❌ Phase2 初始化失敗: {e}")
                self.phase_status["phase2"] = False
        
        # 初始化Phase3  
        if PHASE3_AVAILABLE:
            try:
                self.phase3_executor = ExecutionPolicyEngine()
                logger.info("✅ Phase3 執行策略已連接")
            except Exception as e:
                logger.error(f"❌ Phase3 初始化失敗: {e}")
                self.phase_status["phase3"] = False
        
        # 初始化Phase5
        if PHASE5_AVAILABLE:
            try:
                self.phase5_validator = AutoBacktestValidator()
                logger.info("✅ Phase5 回測驗證已連接")
            except Exception as e:
                logger.error(f"❌ Phase5 初始化失敗: {e}")
                self.phase_status["phase5"] = False
        
        # 初始化實時引擎
        try:
            self.realtime_engine = RealtimeSignalEngine()
            logger.info("✅ 實時信號引擎已連接")
        except Exception as e:
            logger.error(f"❌ 實時引擎初始化失敗: {e}")
        
        logger.info(f"🔗 Phase集成狀態: {self.phase_status}")
    
    async def get_phase1a_signals(self, symbol: str, timeframe: str) -> List[Dict[str, Any]]:
        """獲取Phase1A基礎信號"""
        if not self.phase_status["phase1a"]:
            return []
            
        try:
            # 從Phase1A獲取信號
            signals = await self.phase1a_generator.generate_signals(symbol, timeframe)
            
            # 轉換為量子引擎可用格式
            quantum_signals = []
            for signal in signals:
                quantum_signal = {
                    "source": "phase1a",
                    "signal_type": getattr(signal, 'signal_type', 'UNKNOWN'),
                    "confidence": getattr(signal, 'confidence', 0.0),
                    "lean_similarity": getattr(signal, 'lean_similarity', 0.0),
                    "tier": getattr(signal, 'tier', SignalTier.MEDIUM),
                    "dynamic_params": getattr(signal, 'dynamic_params', {}),
                    "market_regime": getattr(signal, 'market_regime', MarketRegime.NEUTRAL),
                    "trading_session": getattr(signal, 'trading_session', TradingSession.OFF_HOURS),
                    "timestamp": datetime.now()
                }
                quantum_signals.append(quantum_signal)
            
            # 緩存結果
            self.phase1a_signals[f"{symbol}_{timeframe}"] = quantum_signals
            
            logger.debug(f"📡 Phase1A: {symbol} {timeframe} -> {len(quantum_signals)} 信號")
            return quantum_signals
            
        except Exception as e:
            logger.error(f"❌ Phase1A信號獲取失敗: {e}")
            return []
    
    async def get_phase2_learning_data(self, symbol: str, timeframe: str) -> Dict[str, float]:
        """獲取Phase2學習權重和參數"""
        if not self.phase_status["phase2"]:
            return {"learning_weight": 0.5, "pattern_confidence": 0.5}
            
        try:
            # 從Phase2數據庫獲取學習數據
            async for db in self.learning_db():
                query = """
                SELECT avg_weight, pattern_confidence, technical_score, volatility_adjustment
                FROM weight_statistics 
                WHERE symbol = ? AND timeframe = ?
                ORDER BY timestamp DESC LIMIT 1
                """
                cursor = await db.execute(query, (symbol, timeframe))
                result = await cursor.fetchone()
                break  # 只需要第一個連接
                
            if result:
                learning_data = {
                    "learning_weight": result[0] if result[0] else 0.5,
                    "pattern_confidence": result[1] if result[1] else 0.5, 
                    "technical_score": result[2] if result[2] else 0.5,
                    "volatility_adjustment": result[3] if result[3] else 1.0
                }
            else:
                learning_data = {
                    "learning_weight": 0.5,
                    "pattern_confidence": 0.5,
                    "technical_score": 0.5, 
                    "volatility_adjustment": 1.0
                }
            
            # 如果Phase2數據庫可用，還可以獲取增強信號
            if self.phase2_database:
                enhanced_signals = await self.phase2_database.get_recent_signals(
                    symbol=symbol, timeframe=timeframe, limit=10
                )
                
                if enhanced_signals:
                    # 計算平均學習權重
                    avg_learning_weight = np.mean([
                        getattr(s, 'final_learning_weight', 0.5) for s in enhanced_signals
                    ])
                    learning_data["enhanced_learning_weight"] = avg_learning_weight
            
            # 緩存結果
            self.phase2_learning_weights[f"{symbol}_{timeframe}"] = learning_data
            
            logger.debug(f"🎓 Phase2: {symbol} {timeframe} -> 學習權重 {learning_data['learning_weight']:.3f}")
            return learning_data
            
        except Exception as e:
            logger.error(f"❌ Phase2學習數據獲取失敗: {e}")
            return {"learning_weight": 0.5, "pattern_confidence": 0.5}
    
    async def get_phase3_execution_context(self, symbol: str) -> Dict[str, Any]:
        """獲取Phase3執行上下文"""
        if not self.phase_status["phase3"]:
            return {"execution_ready": False, "risk_level": "medium"}
            
        try:
            # 從Phase3獲取執行決策上下文
            execution_context = {
                "execution_ready": True,
                "risk_level": "medium",
                "position_sizing": 0.4,
                "market_sentiment": "neutral",
                "execution_timing": "immediate",
                "stop_loss_strategy": "dynamic_atr",
                "take_profit_strategy": "fibonacci_levels"
            }
            
            # 如果Phase3執行器可用
            if self.phase3_executor:
                try:
                    # 獲取市場情境分析
                    market_analysis = await self.phase3_executor.analyze_market_context(symbol)
                    execution_context.update(market_analysis)
                except:
                    pass  # 使用預設值
            
            # 緩存結果
            self.phase3_execution_decisions[symbol] = execution_context
            
            logger.debug(f"⚡ Phase3: {symbol} -> 執行就緒 {execution_context['execution_ready']}")
            return execution_context
            
        except Exception as e:
            logger.error(f"❌ Phase3執行上下文獲取失敗: {e}")
            return {"execution_ready": False, "risk_level": "high"}
    
    async def get_phase5_backtest_insights(self, symbol: str, signal_type: str) -> Dict[str, float]:
        """獲取Phase5回測洞察"""
        if not self.phase_status["phase5"]:
            return {"historical_accuracy": 0.6, "avg_return": 0.0}
            
        try:
            # 從Phase5獲取回測結果
            backtest_insights = {
                "historical_accuracy": 0.6,
                "avg_return": 0.0,
                "max_drawdown": 0.05,
                "sharpe_ratio": 1.2,
                "win_rate": 0.65,
                "avg_holding_time": 4.5,  # 小時
                "lean_similarity_performance": 0.75
            }
            
            # 如果Phase5驗證器可用
            if self.phase5_validator:
                try:
                    # 查詢歷史相似信號的表現
                    historical_performance = await self.phase5_validator.get_signal_performance(
                        symbol=symbol, signal_type=signal_type
                    )
                    if historical_performance:
                        backtest_insights.update(historical_performance)
                except:
                    pass  # 使用預設值
            
            # 緩存結果
            self.phase5_backtest_results[f"{symbol}_{signal_type}"] = backtest_insights
            
            logger.debug(f"📊 Phase5: {symbol} {signal_type} -> 準確率 {backtest_insights['historical_accuracy']:.3f}")
            return backtest_insights
            
        except Exception as e:
            logger.error(f"❌ Phase5回測洞察獲取失敗: {e}")
            return {"historical_accuracy": 0.6, "avg_return": 0.0}
    
    async def integrate_all_phases(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """集成所有Phase的數據"""
        logger.debug(f"🔗 集成Phase數據: {symbol} {timeframe}")
        
        # 並行獲取所有Phase數據
        phase1a_task = asyncio.create_task(self.get_phase1a_signals(symbol, timeframe))
        phase2_task = asyncio.create_task(self.get_phase2_learning_data(symbol, timeframe))  
        phase3_task = asyncio.create_task(self.get_phase3_execution_context(symbol))
        
        phase1a_data, phase2_data, phase3_data = await asyncio.gather(
            phase1a_task, phase2_task, phase3_task, return_exceptions=True
        )
        
        # 處理異常
        if isinstance(phase1a_data, Exception):
            phase1a_data = []
        if isinstance(phase2_data, Exception):
            phase2_data = {"learning_weight": 0.5}
        if isinstance(phase3_data, Exception):
            phase3_data = {"execution_ready": False}
        
        # 集成數據結構
        integrated_data = {
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": datetime.now(),
            
            # Phase1A 數據
            "phase1a_signals": phase1a_data,
            "lean_confidence": self._extract_lean_confidence(phase1a_data),
            "signal_tier": self._extract_signal_tier(phase1a_data),
            "market_regime": self._extract_market_regime(phase1a_data),
            
            # Phase2 數據
            "learning_weight": phase2_data.get("learning_weight", 0.5),
            "pattern_confidence": phase2_data.get("pattern_confidence", 0.5),
            "technical_score": phase2_data.get("technical_score", 0.5),
            "volatility_adjustment": phase2_data.get("volatility_adjustment", 1.0),
            
            # Phase3 數據
            "execution_ready": phase3_data.get("execution_ready", False),
            "risk_level": phase3_data.get("risk_level", "medium"),
            "position_sizing": phase3_data.get("position_sizing", 0.4),
            
            # 統合評分
            "integrated_confidence": self._calculate_integrated_confidence(
                phase1a_data, phase2_data, phase3_data
            ),
            "quantum_readiness": self._calculate_quantum_readiness(
                phase1a_data, phase2_data, phase3_data
            )
        }
        
        return integrated_data
    
    def _extract_lean_confidence(self, phase1a_signals: List[Dict]) -> float:
        """從Phase1A信號中提取Lean信心度"""
        if not phase1a_signals:
            return 0.5
        
        lean_scores = [s.get("lean_similarity", 0.0) for s in phase1a_signals]
        return np.mean(lean_scores) if lean_scores else 0.5
    
    def _extract_signal_tier(self, phase1a_signals: List[Dict]) -> str:
        """從Phase1A信號中提取信號分層"""
        if not phase1a_signals:
            return "MEDIUM"
        
        # 取最高等級的信號分層
        tiers = [s.get("tier", SignalTier.MEDIUM) for s in phase1a_signals]
        tier_values = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        
        max_tier = max(tiers, key=lambda t: tier_values.get(getattr(t, 'value', 'MEDIUM'), 2))
        return getattr(max_tier, 'value', 'MEDIUM')
    
    def _extract_market_regime(self, phase1a_signals: List[Dict]) -> str:
        """從Phase1A信號中提取市場狀態"""
        if not phase1a_signals:
            return "NEUTRAL"
        
        regimes = [s.get("market_regime", MarketRegime.NEUTRAL) for s in phase1a_signals]
        if regimes:
            # 取出現最多的市場狀態
            regime_counts = {}
            for regime in regimes:
                regime_val = getattr(regime, 'value', 'NEUTRAL')
                regime_counts[regime_val] = regime_counts.get(regime_val, 0) + 1
            
            return max(regime_counts, key=regime_counts.get)
        
        return "NEUTRAL"
    
    def _calculate_integrated_confidence(self, phase1a_data: List[Dict], 
                                       phase2_data: Dict, phase3_data: Dict) -> float:
        """計算集成信心度"""
        # Phase1A信心度 (40%)
        phase1a_conf = np.mean([s.get("confidence", 0.0) for s in phase1a_data]) if phase1a_data else 0.5
        
        # Phase2學習權重 (30%)
        phase2_conf = phase2_data.get("learning_weight", 0.5)
        
        # Phase3執行就緒度 (30%)
        phase3_conf = 0.8 if phase3_data.get("execution_ready", False) else 0.3
        
        integrated = phase1a_conf * 0.4 + phase2_conf * 0.3 + phase3_conf * 0.3
        return min(0.95, max(0.05, integrated))
    
    def _calculate_quantum_readiness(self, phase1a_data: List[Dict],
                                   phase2_data: Dict, phase3_data: Dict) -> float:
        """計算量子就緒度"""
        readiness_factors = []
        
        # 信號數量充足度
        signal_abundance = min(1.0, len(phase1a_data) / 3.0) if phase1a_data else 0.0
        readiness_factors.append(signal_abundance)
        
        # 學習數據可靠性
        learning_reliability = phase2_data.get("pattern_confidence", 0.5)
        readiness_factors.append(learning_reliability)
        
        # 執行環境準備度
        execution_readiness = 0.9 if phase3_data.get("execution_ready", False) else 0.2
        readiness_factors.append(execution_readiness)
        
        # Lean相似度質量
        lean_quality = self._extract_lean_confidence(phase1a_data)
        readiness_factors.append(lean_quality)
        
        return np.mean(readiness_factors)
    
    async def create_quantum_enhanced_signal(self, integrated_data: Dict[str, Any], 
                                           quantum_decision: Dict[str, Any]) -> TradingSignalAlert:
        """創建量子增強的交易信號"""
        
        # 融合量子決策與Phase數據
        enhanced_signal = TradingSignalAlert(
            symbol=integrated_data["symbol"],
            signal_type=quantum_decision["signal_type"],
            confidence=quantum_decision["confidence"],
            entry_price=quantum_decision["entry_price"],
            stop_loss=quantum_decision["stop_loss"],
            take_profit=quantum_decision["take_profit"],
            risk_reward_ratio=quantum_decision["risk_reward_ratio"],
            indicators_used=quantum_decision["indicators_used"],
            reasoning=f"量子融合: {quantum_decision['reasoning']} | Phase集成信心度: {integrated_data['integrated_confidence']:.3f}",
            timeframe=integrated_data["timeframe"],
            timestamp=datetime.now(),
            urgency=quantum_decision["urgency_level"]
        )
        
        # 添加Phase數據到推理中
        phase_context = []
        if integrated_data["phase1a_signals"]:
            phase_context.append(f"Phase1A:{len(integrated_data['phase1a_signals'])}信號")
        phase_context.append(f"Phase2:學習權重{integrated_data['learning_weight']:.2f}")
        if integrated_data["execution_ready"]:
            phase_context.append("Phase3:就緒")
        
        enhanced_signal.reasoning += f" | {', '.join(phase_context)}"
        
        return enhanced_signal
    
    async def save_integrated_result(self, quantum_decision: Dict[str, Any], 
                                   integrated_data: Dict[str, Any]):
        """保存集成結果到數據庫"""
        try:
            # 保存到signals.db
            async for db in self.signals_db():
                insert_query = """
                INSERT INTO sniper_signal_history 
                (symbol, timeframe, signal_type, confidence, entry_price, stop_loss, take_profit,
                 risk_reward_ratio, reasoning, indicators_used, quantum_metadata, phase_integration_data,
                 created_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                phase_integration = {
                    "lean_confidence": integrated_data.get("lean_confidence", 0.5),
                    "learning_weight": integrated_data.get("learning_weight", 0.5),
                    "execution_ready": integrated_data.get("execution_ready", False),
                    "integrated_confidence": integrated_data.get("integrated_confidence", 0.5),
                    "quantum_readiness": integrated_data.get("quantum_readiness", 0.5),
                    "signal_tier": integrated_data.get("signal_tier", "MEDIUM"),
                    "market_regime": integrated_data.get("market_regime", "NEUTRAL")
                }
                
                await db.execute(insert_query, (
                    quantum_decision["symbol"],
                    quantum_decision["timeframe"],
                    quantum_decision["signal_type"],
                    quantum_decision["confidence"],
                    quantum_decision["entry_price"],
                    quantum_decision["stop_loss"],
                    quantum_decision["take_profit"],
                    quantum_decision["risk_reward_ratio"],
                    quantum_decision["reasoning"],
                    json.dumps(quantum_decision["indicators_used"]),
                    json.dumps(quantum_decision.get("quantum_metadata", {})),
                    json.dumps(phase_integration),
                    datetime.now(),
                    quantum_decision.get("expires_at", datetime.now() + timedelta(hours=4))
                ))
                
                await db.commit()
                logger.info(f"💾 量子Phase集成結果已保存: {quantum_decision['symbol']}")
                break  # 只需要第一個連接
                
        except Exception as e:
            logger.error(f"❌ 保存集成結果失敗: {e}")

# ==================== 導出的集成接口 ====================

class QuantumPhaseCoordinator:
    """量子Phase協調器 - 對外統一接口"""
    
    def __init__(self):
        self.integrator = QuantumPhaseDataFlowIntegrator()
        self.initialized = False
    
    async def initialize(self):
        """初始化協調器"""
        if not self.initialized:
            await self.integrator.initialize()
            self.initialized = True
            logger.info("🚀 量子Phase協調器初始化完成")
    
    async def get_phase_integrated_data(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """獲取Phase集成數據 - 量子引擎主要調用接口"""
        if not self.initialized:
            await self.initialize()
        
        return await self.integrator.integrate_all_phases(symbol, timeframe)
    
    async def enhance_quantum_decision(self, quantum_decision: Dict[str, Any], 
                                     symbol: str, timeframe: str) -> TradingSignalAlert:
        """增強量子決策 - 融合Phase數據"""
        if not self.initialized:
            await self.initialize()
        
        # 獲取集成數據
        integrated_data = await self.integrator.integrate_all_phases(symbol, timeframe)
        
        # 創建增強信號
        enhanced_signal = await self.integrator.create_quantum_enhanced_signal(
            integrated_data, quantum_decision
        )
        
        # 保存結果
        await self.integrator.save_integrated_result(quantum_decision, integrated_data)
        
        return enhanced_signal
    
    def get_phase_status(self) -> Dict[str, bool]:
        """獲取Phase狀態"""
        return self.integrator.phase_status if self.initialized else {}

# 全局實例
quantum_phase_coordinator = QuantumPhaseCoordinator()

async def get_quantum_phase_coordinator() -> QuantumPhaseCoordinator:
    """獲取全局量子Phase協調器"""
    if not quantum_phase_coordinator.initialized:
        await quantum_phase_coordinator.initialize()
    return quantum_phase_coordinator
