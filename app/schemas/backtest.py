from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

class BacktestRequest(BaseModel):
    symbol: str = Field(..., description="交易對")
    timeframe: str = Field(..., description="時間框架")
    start_date: datetime = Field(..., description="開始日期")
    end_date: datetime = Field(..., description="結束日期")
    initial_capital: float = Field(10000.0, gt=0, description="初始資金")
    strategy_id: Optional[int] = Field(None, description="策略ID")
    strategy_config: Optional[Dict[str, Any]] = Field(None, description="策略配置")

class TradeResult(BaseModel):
    type: str  # LONG or SHORT
    entry_price: float
    exit_price: float
    entry_time: datetime
    exit_time: datetime
    quantity: float
    pnl: float
    pnl_percentage: float
    exit_reason: str
    duration: float  # hours

class BacktestResponse(BaseModel):
    backtest_id: Optional[int] = None
    initial_capital: float
    final_capital: float
    total_return: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    max_drawdown: float
    sharpe_ratio: float
    profit_factor: float
    avg_trade_return: float
    gross_profit: Optional[float] = None
    gross_loss: Optional[float] = None
    avg_win: Optional[float] = None
    avg_loss: Optional[float] = None
    trades: List[TradeResult]

class PerformanceMetrics(BaseModel):
    initial_capital: float
    final_capital: float
    total_return: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    max_drawdown: float
    sharpe_ratio: Optional[float] = None
    profit_factor: Optional[float] = None
    avg_trade_return: Optional[float] = None

class BacktestResultResponse(BaseModel):
    id: int
    symbol: str
    timeframe: str
    date_range: Dict[str, datetime]
    performance: PerformanceMetrics
    detailed_results: Optional[Dict[str, Any]] = None
    created_at: datetime

class StrategyComparison(BaseModel):
    backtest_id: int
    strategy_id: int
    total_return: float
    win_rate: float
    max_drawdown: float
    sharpe_ratio: Optional[float] = None
    profit_factor: Optional[float] = None
    total_trades: int
    created_at: datetime

class ComparisonResponse(BaseModel):
    symbol: str
    timeframe: str
    comparison_period: str
    total_strategies: int
    best_performer: Optional[StrategyComparison] = None
    strategies: List[StrategyComparison]
