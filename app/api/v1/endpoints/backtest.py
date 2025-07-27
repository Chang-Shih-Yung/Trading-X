from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from app.core.database import get_db
from app.utils.time_utils import get_taiwan_now_naive, taiwan_now_minus
from app.services.market_data import MarketDataService
from app.services.technical_indicators import TechnicalIndicatorsService
from app.services.strategy_engine import StrategyEngine
from app.models.models import BacktestResult
from app.schemas.backtest import BacktestRequest, BacktestResponse

router = APIRouter()

@router.post("/run", response_model=BacktestResponse)
async def run_backtest(
    request: BacktestRequest,
    db: AsyncSession = Depends(get_db)
):
    """執行策略回測"""
    try:
        backtester = StrategyBacktester()
        result = await backtester.run_backtest(
            symbol=request.symbol,
            timeframe=request.timeframe,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            strategy_config=request.strategy_config
        )
        
        # 儲存回測結果
        backtest_record = BacktestResult(
            strategy_id=request.strategy_id or 0,
            symbol=request.symbol,
            timeframe=request.timeframe,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            final_capital=result['final_capital'],
            total_return=result['total_return'],
            total_trades=result['total_trades'],
            winning_trades=result['winning_trades'],
            losing_trades=result['losing_trades'],
            win_rate=result['win_rate'],
            max_drawdown=result['max_drawdown'],
            sharpe_ratio=result.get('sharpe_ratio'),
            profit_factor=result.get('profit_factor'),
            avg_trade_return=result.get('avg_trade_return'),
            detailed_results=result
        )
        
        db.add(backtest_record)
        await db.commit()
        
        return BacktestResponse(**result, backtest_id=backtest_record.id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"回測執行失敗: {str(e)}")

@router.get("/results/{backtest_id}")
async def get_backtest_result(
    backtest_id: int,
    db: AsyncSession = Depends(get_db)
):
    """獲取回測結果"""
    try:
        query = db.query(BacktestResult).filter(BacktestResult.id == backtest_id)
        result = await db.execute(query)
        backtest = result.scalar_one_or_none()
        
        if not backtest:
            raise HTTPException(status_code=404, detail="回測結果不存在")
        
        return {
            "id": backtest.id,
            "symbol": backtest.symbol,
            "timeframe": backtest.timeframe,
            "date_range": {
                "start": backtest.start_date,
                "end": backtest.end_date
            },
            "performance": {
                "initial_capital": backtest.initial_capital,
                "final_capital": backtest.final_capital,
                "total_return": backtest.total_return,
                "total_trades": backtest.total_trades,
                "winning_trades": backtest.winning_trades,
                "losing_trades": backtest.losing_trades,
                "win_rate": backtest.win_rate,
                "max_drawdown": backtest.max_drawdown,
                "sharpe_ratio": backtest.sharpe_ratio,
                "profit_factor": backtest.profit_factor,
                "avg_trade_return": backtest.avg_trade_return
            },
            "detailed_results": backtest.detailed_results,
            "created_at": backtest.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取回測結果失敗: {str(e)}")

@router.get("/compare")
async def compare_strategies(
    symbol: str,
    timeframe: str,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """比較不同策略的回測表現"""
    try:
        end_date = get_taiwan_now_naive()
        start_date = taiwan_now_minus(days=days)
        
        query = db.query(BacktestResult).filter(
            BacktestResult.symbol == symbol,
            BacktestResult.timeframe == timeframe,
            BacktestResult.start_date >= start_date
        )
        result = await db.execute(query)
        backtests = result.scalars().all()
        
        if not backtests:
            return {"message": "未找到符合條件的回測結果", "strategies": []}
        
        # 整理比較數據
        strategies = []
        for bt in backtests:
            strategies.append({
                "backtest_id": bt.id,
                "strategy_id": bt.strategy_id,
                "total_return": bt.total_return,
                "win_rate": bt.win_rate,
                "max_drawdown": bt.max_drawdown,
                "sharpe_ratio": bt.sharpe_ratio,
                "profit_factor": bt.profit_factor,
                "total_trades": bt.total_trades,
                "created_at": bt.created_at
            })
        
        # 排序：按總回報率排序
        strategies.sort(key=lambda x: x['total_return'], reverse=True)
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "comparison_period": f"{days} days",
            "total_strategies": len(strategies),
            "best_performer": strategies[0] if strategies else None,
            "strategies": strategies
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"策略比較失敗: {str(e)}")

class StrategyBacktester:
    """策略回測器"""
    
    def __init__(self):
        self.market_service = MarketDataService()
        self.strategy_engine = StrategyEngine()
    
    async def run_backtest(
        self,
        symbol: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime,
        initial_capital: float,
        strategy_config: Optional[Dict] = None
    ) -> Dict:
        """執行回測"""
        
        # 獲取歷史數據
        df = await self._get_backtest_data(symbol, timeframe, start_date, end_date)
        
        if df.empty:
            raise ValueError(f"無法獲取 {symbol} {timeframe} 的歷史數據")
        
        # 執行回測邏輯
        trades = await self._simulate_trades(df, strategy_config)
        
        # 計算績效指標
        performance = self._calculate_performance(trades, initial_capital, df)
        
        return performance
    
    async def _get_backtest_data(
        self,
        symbol: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """獲取回測數據"""
        
        # 計算需要的K線數量
        time_diff = end_date - start_date
        
        timeframe_minutes = {
            "1m": 1, "5m": 5, "15m": 15, "1h": 60, "4h": 240, "1d": 1440
        }
        
        total_minutes = int(time_diff.total_seconds() / 60)
        limit = int(total_minutes / timeframe_minutes.get(timeframe, 60))
        limit = min(limit, 1000)  # API限制
        
        # 先嘗試從資料庫獲取
        df = await self.market_service.get_market_data_from_db(symbol, timeframe, limit)
        
        if df.empty:
            # 從交易所獲取
            df = await self.market_service.get_historical_data(symbol, timeframe, limit)
        
        # 篩選時間範圍
        if not df.empty:
            df = df[
                (df['timestamp'] >= start_date) & 
                (df['timestamp'] <= end_date)
            ].copy()
        
        return df
    
    async def _simulate_trades(self, df: pd.DataFrame, strategy_config: Optional[Dict]) -> List[Dict]:
        """模擬交易"""
        trades = []
        position = None
        
        # 逐根K線分析
        for i in range(50, len(df)):  # 從第50根開始，確保有足夠數據計算指標
            current_data = df.iloc[:i+1].copy()
            
            # 計算技術指標
            indicators = TechnicalIndicatorsService.calculate_all_indicators(current_data)
            
            # 生成信號
            signal = await self._generate_backtest_signal(current_data, indicators)
            
            current_price = float(current_data['close'].iloc[-1])
            current_time = current_data['timestamp'].iloc[-1]
            
            # 處理信號
            if signal and not position:
                # 開倉
                if signal['signal_type'] in ['LONG', 'SHORT']:
                    position = {
                        'type': signal['signal_type'],
                        'entry_price': current_price,
                        'entry_time': current_time,
                        'stop_loss': signal['stop_loss'],
                        'take_profit': signal['take_profit'],
                        'quantity': 1.0  # 簡化，假設固定數量
                    }
            
            elif position:
                # 檢查平倉條件
                should_close, reason = self._check_exit_conditions(position, current_price)
                
                if should_close:
                    # 平倉
                    trade = self._close_position(position, current_price, current_time, reason)
                    trades.append(trade)
                    position = None
        
        return trades
    
    async def _generate_backtest_signal(self, df: pd.DataFrame, indicators: Dict) -> Optional[Dict]:
        """為回測生成信號"""
        
        if len(df) < 50:
            return None
        
        current_price = float(df['close'].iloc[-1])
        
        # 簡化的信號邏輯
        long_signals = 0
        short_signals = 0
        
        # 趨勢確認
        if 'EMA' in indicators and indicators['EMA'].signal == 'BUY':
            long_signals += 1
        elif 'EMA' in indicators and indicators['EMA'].signal == 'SELL':
            short_signals += 1
        
        # MACD確認
        if 'MACD' in indicators and indicators['MACD'].signal == 'BUY':
            long_signals += 1
        elif 'MACD' in indicators and indicators['MACD'].signal == 'SELL':
            short_signals += 1
        
        # RSI確認
        if 'RSI' in indicators:
            if indicators['RSI'].value < 30:
                long_signals += 1
            elif indicators['RSI'].value > 70:
                short_signals += 1
        
        # 生成信號
        if long_signals >= 2:
            return {
                'signal_type': 'LONG',
                'entry_price': current_price,
                'stop_loss': current_price * 0.98,
                'take_profit': current_price * 1.06
            }
        elif short_signals >= 2:
            return {
                'signal_type': 'SHORT',
                'entry_price': current_price,
                'stop_loss': current_price * 1.02,
                'take_profit': current_price * 0.94
            }
        
        return None
    
    def _check_exit_conditions(self, position: Dict, current_price: float) -> tuple:
        """檢查平倉條件"""
        
        if position['type'] == 'LONG':
            if current_price <= position['stop_loss']:
                return True, 'stop_loss'
            elif current_price >= position['take_profit']:
                return True, 'take_profit'
        
        elif position['type'] == 'SHORT':
            if current_price >= position['stop_loss']:
                return True, 'stop_loss'
            elif current_price <= position['take_profit']:
                return True, 'take_profit'
        
        return False, None
    
    def _close_position(self, position: Dict, exit_price: float, exit_time: datetime, reason: str) -> Dict:
        """平倉並記錄交易"""
        
        if position['type'] == 'LONG':
            pnl = (exit_price - position['entry_price']) * position['quantity']
        else:  # SHORT
            pnl = (position['entry_price'] - exit_price) * position['quantity']
        
        pnl_percentage = (pnl / position['entry_price']) * 100
        
        return {
            'type': position['type'],
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'entry_time': position['entry_time'],
            'exit_time': exit_time,
            'quantity': position['quantity'],
            'pnl': pnl,
            'pnl_percentage': pnl_percentage,
            'exit_reason': reason,
            'duration': (exit_time - position['entry_time']).total_seconds() / 3600  # 小時
        }
    
    def _calculate_performance(self, trades: List[Dict], initial_capital: float, df: pd.DataFrame) -> Dict:
        """計算績效指標"""
        
        if not trades:
            return {
                'initial_capital': initial_capital,
                'final_capital': initial_capital,
                'total_return': 0.0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'max_drawdown': 0.0,
                'sharpe_ratio': 0.0,
                'profit_factor': 0.0,
                'avg_trade_return': 0.0,
                'trades': []
            }
        
        # 基本統計
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t['pnl'] > 0])
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        # 計算總收益
        total_pnl = sum(t['pnl'] for t in trades)
        final_capital = initial_capital + total_pnl
        total_return = (total_pnl / initial_capital) * 100
        
        # 計算最大回撤
        equity_curve = [initial_capital]
        running_capital = initial_capital
        
        for trade in trades:
            running_capital += trade['pnl']
            equity_curve.append(running_capital)
        
        peak = equity_curve[0]
        max_drawdown = 0
        
        for equity in equity_curve:
            if equity > peak:
                peak = equity
            drawdown = ((peak - equity) / peak) * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # 計算Sharpe比率 (簡化版)
        returns = [t['pnl_percentage'] for t in trades]
        if len(returns) > 1:
            avg_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe_ratio = avg_return / std_return if std_return > 0 else 0
        else:
            sharpe_ratio = 0
        
        # 盈利因子
        gross_profit = sum(t['pnl'] for t in trades if t['pnl'] > 0)
        gross_loss = abs(sum(t['pnl'] for t in trades if t['pnl'] < 0))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # 平均交易回報
        avg_trade_return = np.mean([t['pnl_percentage'] for t in trades])
        
        return {
            'initial_capital': initial_capital,
            'final_capital': final_capital,
            'total_return': round(total_return, 2),
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': round(win_rate, 2),
            'max_drawdown': round(max_drawdown, 2),
            'sharpe_ratio': round(sharpe_ratio, 3),
            'profit_factor': round(profit_factor, 2),
            'avg_trade_return': round(avg_trade_return, 2),
            'gross_profit': round(gross_profit, 2),
            'gross_loss': round(gross_loss, 2),
            'avg_win': round(gross_profit / winning_trades, 2) if winning_trades > 0 else 0,
            'avg_loss': round(gross_loss / losing_trades, 2) if losing_trades > 0 else 0,
            'trades': trades
        }
