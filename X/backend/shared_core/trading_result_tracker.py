"""
🎯 Trading X - 真實交易結果追蹤系統
用於 Phase2 學習機制的反饋數據收集和分析
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
from pathlib import Path
from collections import defaultdict, deque
import uuid

logger = logging.getLogger(__name__)

class TradeStatus(Enum):
    """交易狀態"""
    PENDING = "pending"           # 待執行
    EXECUTED = "executed"         # 已執行
    PARTIALLY_FILLED = "partial"  # 部分成交
    CANCELLED = "cancelled"       # 已取消
    FAILED = "failed"            # 執行失敗

class TradeOutcome(Enum):
    """交易結果"""
    PROFIT = "profit"      # 盈利
    LOSS = "loss"          # 虧損
    BREAKEVEN = "breakeven" # 持平
    PENDING = "pending"     # 待確定

@dataclass
class SignalTrackingRecord:
    """信號追蹤記錄"""
    signal_id: str
    symbol: str
    timestamp: datetime
    signal_type: str              # BUY/SELL
    signal_strength: float        # 信號強度 0-1
    tier: str                     # CRITICAL/HIGH/MEDIUM/LOW
    
    # Phase2 學習相關
    market_regime: str            # 市場狀態
    confidence: float             # 信心度
    adaptive_parameters: Dict[str, Any]  # 自適應參數
    
    # Phase3 決策相關
    decision_action: Optional[str] = None
    decision_confidence: Optional[float] = None
    
    # 執行追蹤
    execution_time: Optional[datetime] = None
    execution_price: Optional[float] = None
    execution_quantity: Optional[float] = None
    trade_status: TradeStatus = TradeStatus.PENDING
    
    # 結果追蹤
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    realized_pnl: Optional[float] = None
    trade_outcome: TradeOutcome = TradeOutcome.PENDING
    
    # 性能指標
    accuracy_score: Optional[float] = None  # 預測準確性 0-1
    timing_score: Optional[float] = None    # 時機準確性 0-1
    risk_score: Optional[float] = None      # 風險控制評分 0-1

@dataclass
class LearningFeedback:
    """學習反饋數據"""
    symbol: str
    time_period: Tuple[datetime, datetime]
    
    # 整體統計
    total_signals: int
    executed_trades: int
    successful_trades: int
    win_rate: float
    average_return: float
    sharpe_ratio: float
    max_drawdown: float
    
    # 分層統計
    tier_performance: Dict[str, Dict[str, float]]  # 各層級表現
    regime_performance: Dict[str, Dict[str, float]]  # 各市場狀態表現
    
    # 參數效果分析
    parameter_effectiveness: Dict[str, float]  # 參數有效性評分
    
    # 改進建議
    recommendations: List[str]

class TradingResultTracker:
    """交易結果追蹤器"""
    
    def __init__(self):
        """初始化追蹤器"""
        self.tracking_records: Dict[str, SignalTrackingRecord] = {}
        self.feedback_history: deque = deque(maxlen=100)  # 保留最近100條反饋
        
        # 配置
        self.tracking_window_hours = 24  # 信號追蹤窗口：24小時
        self.min_tracking_samples = 10   # 最少樣本數用於學習
        
        # 數據存儲
        self.data_dir = Path(__file__).parent / "tracking_data"
        self.data_dir.mkdir(exist_ok=True)
        
        # 性能統計
        self.performance_cache = {}
        self.last_analysis_time = None
        
        logger.info("✅ 交易結果追蹤器初始化完成")
    
    async def track_signal(self, 
                          signal_id: str,
                          symbol: str,
                          signal_data: Dict[str, Any],
                          market_regime: str = "unknown",
                          adaptive_params: Dict[str, Any] = None) -> str:
        """開始追蹤信號"""
        
        record = SignalTrackingRecord(
            signal_id=signal_id,
            symbol=symbol,
            timestamp=datetime.now(),
            signal_type=signal_data.get('signal_type', 'UNKNOWN'),
            signal_strength=signal_data.get('signal_strength', 0.0),
            tier=signal_data.get('tier', 'LOW'),
            market_regime=market_regime,
            confidence=signal_data.get('confidence', 0.0),
            adaptive_parameters=adaptive_params or {}
        )
        
        self.tracking_records[signal_id] = record
        
        logger.info(f"📋 開始追蹤信號: {signal_id} ({symbol})")
        return signal_id
    
    async def update_phase3_decision(self, 
                                   signal_id: str,
                                   decision_action: str,
                                   decision_confidence: float):
        """更新 Phase3 決策結果"""
        if signal_id in self.tracking_records:
            record = self.tracking_records[signal_id]
            record.decision_action = decision_action
            record.decision_confidence = decision_confidence
            
            logger.debug(f"🎯 更新決策: {signal_id} -> {decision_action}")
    
    async def update_execution(self,
                             signal_id: str,
                             execution_price: float,
                             execution_quantity: float,
                             trade_status: TradeStatus = TradeStatus.EXECUTED):
        """更新執行結果"""
        if signal_id in self.tracking_records:
            record = self.tracking_records[signal_id]
            record.execution_time = datetime.now()
            record.execution_price = execution_price
            record.execution_quantity = execution_quantity
            record.trade_status = trade_status
            
            logger.info(f"✅ 更新執行: {signal_id} -> {execution_price} @ {execution_quantity}")
    
    async def update_trade_result(self,
                                signal_id: str,
                                exit_price: float,
                                realized_pnl: float):
        """更新交易結果"""
        if signal_id in self.tracking_records:
            record = self.tracking_records[signal_id]
            record.exit_time = datetime.now()
            record.exit_price = exit_price
            record.realized_pnl = realized_pnl
            
            # 計算交易結果
            if realized_pnl > 0:
                record.trade_outcome = TradeOutcome.PROFIT
            elif realized_pnl < 0:
                record.trade_outcome = TradeOutcome.LOSS
            else:
                record.trade_outcome = TradeOutcome.BREAKEVEN
            
            # 計算性能評分
            await self._calculate_performance_scores(record)
            
            logger.info(f"💰 更新結果: {signal_id} -> PnL: {realized_pnl:.4f}")
    
    async def _calculate_performance_scores(self, record: SignalTrackingRecord):
        """計算性能評分"""
        if not record.execution_price or not record.exit_price:
            return
        
        # 準確性評分：基於價格預測準確性
        if record.signal_type == "BUY":
            price_movement = (record.exit_price - record.execution_price) / record.execution_price
        else:  # SELL
            price_movement = (record.execution_price - record.exit_price) / record.execution_price
        
        # 準確性：正向移動得高分，負向移動得低分
        record.accuracy_score = max(0.0, min(1.0, (price_movement + 0.1) / 0.2))
        
        # 時機評分：基於執行延遲
        if record.execution_time:
            execution_delay = (record.execution_time - record.timestamp).total_seconds()
            # 執行越快得分越高（5分鐘內得滿分，超過1小時得0分）
            record.timing_score = max(0.0, min(1.0, (3600 - execution_delay) / 3600))
        
        # 風險評分：基於實際盈虧與信號強度的匹配度
        expected_return = record.signal_strength * 0.05  # 預期收益率
        actual_return = abs(record.realized_pnl) / (record.execution_price * record.execution_quantity) if record.execution_quantity else 0
        
        risk_match = 1.0 - abs(expected_return - actual_return) / max(expected_return, 0.01)
        record.risk_score = max(0.0, min(1.0, risk_match))
    
    async def generate_learning_feedback(self, 
                                       symbol: str,
                                       hours_back: int = 24) -> Optional[LearningFeedback]:
        """生成學習反饋數據"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours_back)
        
        # 篩選符合時間範圍的已完成記錄
        completed_records = [
            record for record in self.tracking_records.values()
            if (record.symbol == symbol and 
                start_time <= record.timestamp <= end_time and
                record.trade_outcome != TradeOutcome.PENDING)
        ]
        
        if len(completed_records) < self.min_tracking_samples:
            logger.warning(f"⚠️ {symbol} 樣本數不足 ({len(completed_records)}<{self.min_tracking_samples})，無法生成反饋")
            return None
        
        # 計算整體統計
        total_signals = len(completed_records)
        executed_trades = len([r for r in completed_records if r.trade_status == TradeStatus.EXECUTED])
        successful_trades = len([r for r in completed_records if r.trade_outcome == TradeOutcome.PROFIT])
        
        win_rate = successful_trades / max(executed_trades, 1)
        
        # 計算收益統計
        returns = [r.realized_pnl for r in completed_records if r.realized_pnl is not None]
        average_return = sum(returns) / len(returns) if returns else 0.0
        
        # 計算 Sharpe 比率（簡化版）
        if returns:
            return_std = (sum((r - average_return) ** 2 for r in returns) / len(returns)) ** 0.5
            sharpe_ratio = average_return / max(return_std, 0.001)
        else:
            sharpe_ratio = 0.0
        
        # 計算最大回撤
        cumulative_returns = []
        cumsum = 0
        for r in returns:
            cumsum += r
            cumulative_returns.append(cumsum)
        
        if cumulative_returns:
            peak = cumulative_returns[0]
            max_drawdown = 0
            for value in cumulative_returns:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / max(abs(peak), 0.001)
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
        else:
            max_drawdown = 0.0
        
        # 分層性能分析
        tier_performance = self._analyze_tier_performance(completed_records)
        regime_performance = self._analyze_regime_performance(completed_records)
        parameter_effectiveness = self._analyze_parameter_effectiveness(completed_records)
        
        # 生成改進建議
        recommendations = self._generate_recommendations(
            win_rate, average_return, sharpe_ratio, max_drawdown,
            tier_performance, regime_performance
        )
        
        feedback = LearningFeedback(
            symbol=symbol,
            time_period=(start_time, end_time),
            total_signals=total_signals,
            executed_trades=executed_trades,
            successful_trades=successful_trades,
            win_rate=win_rate,
            average_return=average_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            tier_performance=tier_performance,
            regime_performance=regime_performance,
            parameter_effectiveness=parameter_effectiveness,
            recommendations=recommendations
        )
        
        self.feedback_history.append(feedback)
        await self._save_feedback(feedback)
        
        logger.info(f"📊 生成學習反饋: {symbol}, 勝率: {win_rate:.2%}, 平均收益: {average_return:.4f}")
        return feedback
    
    def _analyze_tier_performance(self, records: List[SignalTrackingRecord]) -> Dict[str, Dict[str, float]]:
        """分析分層性能"""
        tier_stats = defaultdict(lambda: {"count": 0, "wins": 0, "total_return": 0.0})
        
        for record in records:
            tier = record.tier
            tier_stats[tier]["count"] += 1
            if record.trade_outcome == TradeOutcome.PROFIT:
                tier_stats[tier]["wins"] += 1
            if record.realized_pnl is not None:
                tier_stats[tier]["total_return"] += record.realized_pnl
        
        result = {}
        for tier, stats in tier_stats.items():
            if stats["count"] > 0:
                result[tier] = {
                    "win_rate": stats["wins"] / stats["count"],
                    "average_return": stats["total_return"] / stats["count"],
                    "sample_count": stats["count"]
                }
        
        return result
    
    def _analyze_regime_performance(self, records: List[SignalTrackingRecord]) -> Dict[str, Dict[str, float]]:
        """分析市場狀態性能"""
        regime_stats = defaultdict(lambda: {"count": 0, "wins": 0, "total_return": 0.0})
        
        for record in records:
            regime = record.market_regime
            regime_stats[regime]["count"] += 1
            if record.trade_outcome == TradeOutcome.PROFIT:
                regime_stats[regime]["wins"] += 1
            if record.realized_pnl is not None:
                regime_stats[regime]["total_return"] += record.realized_pnl
        
        result = {}
        for regime, stats in regime_stats.items():
            if stats["count"] > 0:
                result[regime] = {
                    "win_rate": stats["wins"] / stats["count"],
                    "average_return": stats["total_return"] / stats["count"],
                    "sample_count": stats["count"]
                }
        
        return result
    
    def _analyze_parameter_effectiveness(self, records: List[SignalTrackingRecord]) -> Dict[str, float]:
        """分析參數有效性"""
        # 分析自適應參數與交易結果的相關性
        param_effectiveness = {}
        
        # 分析信號強度的有效性
        strong_signals = [r for r in records if r.signal_strength > 0.7]
        if strong_signals:
            strong_win_rate = len([r for r in strong_signals if r.trade_outcome == TradeOutcome.PROFIT]) / len(strong_signals)
            param_effectiveness["signal_strength_high"] = strong_win_rate
        
        # 分析信心度的有效性
        confident_signals = [r for r in records if r.confidence > 0.8]
        if confident_signals:
            confident_win_rate = len([r for r in confident_signals if r.trade_outcome == TradeOutcome.PROFIT]) / len(confident_signals)
            param_effectiveness["confidence_high"] = confident_win_rate
        
        return param_effectiveness
    
    def _generate_recommendations(self, 
                                win_rate: float,
                                average_return: float,
                                sharpe_ratio: float,
                                max_drawdown: float,
                                tier_performance: Dict,
                                regime_performance: Dict) -> List[str]:
        """生成改進建議"""
        recommendations = []
        
        # 勝率分析
        if win_rate < 0.4:
            recommendations.append("勝率偏低，建議提高信號篩選標準")
        elif win_rate > 0.8:
            recommendations.append("勝率很高，可考慮適度降低篩選標準以增加交易頻率")
        
        # Sharpe 比率分析
        if sharpe_ratio < 0.5:
            recommendations.append("風險調整收益偏低，建議優化風險控制策略")
        
        # 回撤分析
        if max_drawdown > 0.2:
            recommendations.append("最大回撤過大，建議加強止損機制")
        
        # 分層表現分析
        if tier_performance:
            best_tier = max(tier_performance.keys(), key=lambda t: tier_performance[t]["win_rate"])
            worst_tier = min(tier_performance.keys(), key=lambda t: tier_performance[t]["win_rate"])
            
            if tier_performance[best_tier]["win_rate"] - tier_performance[worst_tier]["win_rate"] > 0.3:
                recommendations.append(f"建議重點使用 {best_tier} 層級信號，減少 {worst_tier} 層級")
        
        return recommendations
    
    async def _save_feedback(self, feedback: LearningFeedback):
        """保存反饋數據"""
        try:
            filename = f"feedback_{feedback.symbol}_{feedback.time_period[1].strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.data_dir / filename
            
            # 轉換為可序列化的格式
            data = asdict(feedback)
            data["time_period"] = [t.isoformat() for t in feedback.time_period]
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            logger.debug(f"💾 反饋數據已保存: {filename}")
            
        except Exception as e:
            logger.error(f"❌ 保存反饋數據失敗: {e}")
    
    def get_performance_summary(self, symbol: str = None) -> Dict[str, Any]:
        """獲取性能摘要"""
        if symbol:
            records = [r for r in self.tracking_records.values() if r.symbol == symbol]
        else:
            records = list(self.tracking_records.values())
        
        completed_records = [r for r in records if r.trade_outcome != TradeOutcome.PENDING]
        
        if not completed_records:
            return {"message": "暫無完成的交易記錄"}
        
        total_trades = len(completed_records)
        successful_trades = len([r for r in completed_records if r.trade_outcome == TradeOutcome.PROFIT])
        
        return {
            "total_signals_tracked": len(self.tracking_records),
            "completed_trades": total_trades,
            "successful_trades": successful_trades,
            "win_rate": successful_trades / total_trades if total_trades > 0 else 0,
            "average_accuracy_score": sum(r.accuracy_score for r in completed_records if r.accuracy_score) / len([r for r in completed_records if r.accuracy_score]),
            "average_timing_score": sum(r.timing_score for r in completed_records if r.timing_score) / len([r for r in completed_records if r.timing_score]),
            "recent_feedback_count": len(self.feedback_history)
        }

# 全局實例
trading_result_tracker = TradingResultTracker()

# 便捷函數
async def track_signal_for_learning(signal_id: str, symbol: str, signal_data: Dict, market_regime: str = "unknown", adaptive_params: Dict = None) -> str:
    """追蹤信號用於學習"""
    return await trading_result_tracker.track_signal(signal_id, symbol, signal_data, market_regime, adaptive_params)

async def update_trade_execution(signal_id: str, execution_price: float, quantity: float):
    """更新交易執行"""
    await trading_result_tracker.update_execution(signal_id, execution_price, quantity)

async def update_trade_outcome(signal_id: str, exit_price: float, pnl: float):
    """更新交易結果"""
    await trading_result_tracker.update_trade_result(signal_id, exit_price, pnl)

async def generate_feedback_for_symbol(symbol: str, hours_back: int = 24) -> Optional[LearningFeedback]:
    """為特定符號生成學習反饋"""
    return await trading_result_tracker.generate_learning_feedback(symbol, hours_back)
