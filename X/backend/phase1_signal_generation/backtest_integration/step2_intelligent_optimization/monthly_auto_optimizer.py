#!/usr/bin/env python3
"""
🎯 Trading X - 月度自動優化排程器
第二階段：自動化月度回測與參數優化
支援市場制度自適應調整
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
from enum import Enum
from dataclasses import dataclass, asdict
import sys

# 添加項目路徑
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from intelligent_parameter_optimizer import IntelligentParameterOptimizer
from tradingview_style_reporter import TradingViewStyleReportGenerator
from phase5_integrated_validator import Phase5IntegratedBacktestValidator

logger = logging.getLogger(__name__)

class MarketRegime(Enum):
    """市場制度"""
    BULL_MARKET = "bull_market"      # 牛市
    BEAR_MARKET = "bear_market"      # 熊市
    SIDEWAYS = "sideways"            # 震盪市
    HIGH_VOLATILITY = "high_volatility"  # 高波動
    LOW_VOLATILITY = "low_volatility"    # 低波動

@dataclass
class MarketCondition:
    """市場條件分析結果"""
    regime: MarketRegime
    volatility_level: float
    trend_strength: float
    volume_pattern: str
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "regime": self.regime.value,
            "volatility_level": self.volatility_level,
            "trend_strength": self.trend_strength,
            "volume_pattern": self.volume_pattern,
            "confidence": self.confidence
        }

@dataclass
class OptimizationSchedule:
    """優化排程配置"""
    frequency: str  # 'weekly', 'monthly', 'quarterly'
    target_symbols: List[str]
    target_timeframes: List[str]
    optimization_depth: str  # 'quick', 'standard', 'deep'
    auto_apply: bool
    notification_enabled: bool

class MonthlyAutoOptimizer:
    """月度自動優化排程器"""
    
    def __init__(self):
        self.optimizer = None
        self.reporter = None
        self.validator = None
        
        # 默認排程配置
        self.schedule_config = OptimizationSchedule(
            frequency="monthly",
            target_symbols=["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT"],
            target_timeframes=["1m", "5m", "15m", "1h"],
            optimization_depth="standard",
            auto_apply=False,  # 安全起見，默認不自動應用
            notification_enabled=True
        )
        
        self.optimization_history = []
        
    async def __aenter__(self):
        """異步初始化"""
        self.optimizer = await IntelligentParameterOptimizer().__aenter__()
        self.reporter = await TradingViewStyleReportGenerator().__aenter__()
        self.validator = await Phase5IntegratedBacktestValidator().__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """清理資源"""
        if self.optimizer:
            await self.optimizer.__aexit__(exc_type, exc_val, exc_tb)
        if self.reporter:
            await self.reporter.__aexit__(exc_type, exc_val, exc_tb)
        if self.validator:
            await self.validator.__aexit__(exc_type, exc_val, exc_tb)
    
    async def analyze_market_conditions(self, symbol: str = "BTCUSDT", 
                                      timeframe: str = "1h", 
                                      days_back: int = 30) -> MarketCondition:
        """分析當前市場條件"""
        logger.info(f"📊 分析 {symbol} 市場條件")
        
        try:
            # 獲取歷史數據進行市場分析
            historical_data = await self.optimizer.data_extension.fetch_extended_historical_data(
                symbol=symbol, interval=timeframe, days_back=days_back
            )
            
            if not historical_data:
                return MarketCondition(
                    regime=MarketRegime.SIDEWAYS,
                    volatility_level=0.5,
                    trend_strength=0.0,
                    volume_pattern="normal",
                    confidence=0.3
                )
            
            df = self.optimizer.data_extension.convert_to_dataframe(historical_data)
            
            # 計算趨勢強度
            price_change = (df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0]
            
            # 計算波動率 (20期標準差)
            returns = df['close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(len(returns))
            
            # 計算移動平均趨勢
            df['sma_20'] = df['close'].rolling(20).mean()
            df['sma_50'] = df['close'].rolling(50).mean()
            
            # 趨勢強度評估
            recent_data = df.tail(20)
            trend_up_count = sum(recent_data['close'] > recent_data['sma_20'])
            trend_strength = abs(trend_up_count - 10) / 10  # 標準化到0-1
            
            # 成交量模式分析
            df['volume_ma'] = df['volume'].rolling(20).mean()
            recent_volume_ratio = df['volume'].tail(10).mean() / df['volume_ma'].tail(10).mean()
            
            if recent_volume_ratio > 1.5:
                volume_pattern = "high"
            elif recent_volume_ratio < 0.7:
                volume_pattern = "low"
            else:
                volume_pattern = "normal"
            
            # 市場制度判斷
            if price_change > 0.1 and trend_strength > 0.6:
                regime = MarketRegime.BULL_MARKET
            elif price_change < -0.1 and trend_strength > 0.6:
                regime = MarketRegime.BEAR_MARKET
            elif volatility > 0.05:
                regime = MarketRegime.HIGH_VOLATILITY
            elif volatility < 0.02:
                regime = MarketRegime.LOW_VOLATILITY
            else:
                regime = MarketRegime.SIDEWAYS
            
            # 信心度評估
            confidence = min(1.0, (trend_strength + min(1.0, volatility * 10)) / 2)
            
            market_condition = MarketCondition(
                regime=regime,
                volatility_level=volatility,
                trend_strength=trend_strength,
                volume_pattern=volume_pattern,
                confidence=confidence
            )
            
            logger.info(f"📈 市場分析結果: {regime.value}, "
                       f"波動率: {volatility:.3f}, "
                       f"趨勢強度: {trend_strength:.2f}")
            
            return market_condition
            
        except Exception as e:
            logger.error(f"❌ 市場分析失敗: {e}")
            return MarketCondition(
                regime=MarketRegime.SIDEWAYS,
                volatility_level=0.5,
                trend_strength=0.0,
                volume_pattern="normal",
                confidence=0.1
            )
    
    def adapt_parameters_for_market_regime(self, market_condition: MarketCondition) -> Dict[str, float]:
        """根據市場制度調整參數"""
        logger.info(f"⚙️ 為 {market_condition.regime.value} 調整參數")
        
        # 基礎參數
        adapted_params = {
            "rsi_oversold": 30,
            "rsi_overbought": 70,
            "macd_fast": 12,
            "macd_slow": 26,
            "volume_threshold": 1.5,
            "confidence_threshold": 0.7
        }
        
        # 根據市場制度調整
        if market_condition.regime == MarketRegime.BULL_MARKET:
            # 牛市：更積極的參數
            adapted_params.update({
                "rsi_oversold": 35,      # 較寬鬆的超賣
                "rsi_overbought": 75,    # 較嚴格的超買
                "confidence_threshold": 0.6,  # 降低門檻增加信號
                "volume_threshold": 1.3
            })
            
        elif market_condition.regime == MarketRegime.BEAR_MARKET:
            # 熊市：更保守的參數
            adapted_params.update({
                "rsi_oversold": 25,      # 更嚴格的超賣
                "rsi_overbought": 65,    # 更寬鬆的超買
                "confidence_threshold": 0.8,  # 提高門檻減少信號
                "volume_threshold": 1.8
            })
            
        elif market_condition.regime == MarketRegime.HIGH_VOLATILITY:
            # 高波動：更謹慎的參數
            adapted_params.update({
                "macd_fast": 8,          # 更敏感的MACD
                "macd_slow": 21,
                "confidence_threshold": 0.85,  # 高門檻
                "volume_threshold": 2.0
            })
            
        elif market_condition.regime == MarketRegime.LOW_VOLATILITY:
            # 低波動：更敏感的參數
            adapted_params.update({
                "rsi_oversold": 35,      # 更寬鬆的RSI
                "rsi_overbought": 65,
                "macd_fast": 16,         # 較慢的MACD
                "macd_slow": 32,
                "confidence_threshold": 0.6,  # 降低門檻
                "volume_threshold": 1.2
            })
        
        # 根據趨勢強度微調
        if market_condition.trend_strength > 0.8:
            adapted_params["confidence_threshold"] *= 0.9  # 強趨勢時稍微降低門檻
        elif market_condition.trend_strength < 0.3:
            adapted_params["confidence_threshold"] *= 1.1  # 弱趨勢時稍微提高門檻
        
        logger.info(f"🎯 適應性參數: {adapted_params}")
        return adapted_params
    
    async def run_monthly_optimization(self) -> Dict[str, Any]:
        """執行月度優化流程"""
        logger.info("🚀 開始月度自動優化流程")
        
        optimization_report = {
            "optimization_date": datetime.now().isoformat(),
            "market_analysis": {},
            "optimization_results": {},
            "performance_reports": {},
            "recommendations": [],
            "implementation_status": "pending"
        }
        
        try:
            # 第一步：市場條件分析
            logger.info("📊 步驟1: 分析市場條件")
            market_conditions = {}
            
            for symbol in self.schedule_config.target_symbols[:2]:  # 限制分析數量以節省時間
                market_condition = await self.analyze_market_conditions(symbol)
                market_conditions[symbol] = market_condition.to_dict()
            
            optimization_report["market_analysis"] = market_conditions
            
            # 第二步：智能參數優化
            logger.info("🔧 步驟2: 運行智能參數優化")
            optimization_results = await self.optimizer.run_comprehensive_optimization(
                target_symbols=self.schedule_config.target_symbols[:2],
                target_timeframes=self.schedule_config.target_timeframes[:2],
                days_back=14
            )
            
            optimization_report["optimization_results"] = optimization_results
            
            # 第三步：生成TradingView風格報告
            logger.info("📊 步驟3: 生成性能報告")
            performance_reports = {}
            
            for symbol in self.schedule_config.target_symbols[:1]:  # 生成主要標的報告
                for timeframe in ["5m", "1h"]:  # 關鍵時間框架
                    try:
                        report = await self.reporter.generate_comprehensive_report(
                            symbol=symbol,
                            timeframe=timeframe,
                            days_back=14
                        )
                        
                        if "error" not in report:
                            performance_reports[f"{symbol}_{timeframe}"] = report
                    except Exception as e:
                        logger.warning(f"⚠️ 生成 {symbol} {timeframe} 報告失敗: {e}")
            
            optimization_report["performance_reports"] = performance_reports
            
            # 第四步：生成實施建議
            logger.info("💡 步驟4: 生成實施建議")
            recommendations = self._generate_implementation_recommendations(
                market_conditions, optimization_results, performance_reports
            )
            
            optimization_report["recommendations"] = recommendations
            
            # 第五步：記錄優化歷史
            self.optimization_history.append({
                "date": datetime.now().isoformat(),
                "summary": optimization_results.get("summary", {}),
                "market_regime": list(market_conditions.values())[0]["regime"] if market_conditions else "unknown"
            })
            
            logger.info("🎉 月度優化流程完成")
            return optimization_report
            
        except Exception as e:
            logger.error(f"❌ 月度優化失敗: {e}")
            optimization_report["error"] = str(e)
            optimization_report["implementation_status"] = "failed"
            return optimization_report
    
    def _generate_implementation_recommendations(self, 
                                               market_conditions: Dict[str, Any],
                                               optimization_results: Dict[str, Any],
                                               performance_reports: Dict[str, Any]) -> List[str]:
        """生成實施建議"""
        recommendations = []
        
        # 基於市場條件的建議
        if market_conditions:
            main_regime = list(market_conditions.values())[0]["regime"]
            
            if main_regime == "bull_market":
                recommendations.append("🐂 檢測到牛市環境，建議採用更積極的參數設定")
            elif main_regime == "bear_market":
                recommendations.append("🐻 檢測到熊市環境，建議採用更保守的參數設定")
            elif main_regime == "high_volatility":
                recommendations.append("⚡ 高波動環境，建議提高信號品質門檻")
        
        # 基於優化結果的建議
        if optimization_results and "summary" in optimization_results:
            summary = optimization_results["summary"]
            
            if summary.get("significant_improvements_count", 0) >= 3:
                recommendations.append("🎯 發現多個顯著改進機會，建議分階段實施")
            elif summary.get("significant_improvements_count", 0) >= 1:
                recommendations.append("⚙️ 發現部分優化機會，建議謹慎測試後實施")
            else:
                recommendations.append("📊 當前參數表現穩定，建議維持現狀")
        
        # 基於性能報告的建議
        if performance_reports:
            poor_performance_count = 0
            excellent_performance_count = 0
            
            for report in performance_reports.values():
                if "strategy_overview" in report:
                    rating = report["strategy_overview"]["performance_rating"]
                    if "Poor" in rating or "Below Average" in rating:
                        poor_performance_count += 1
                    elif "Excellent" in rating:
                        excellent_performance_count += 1
            
            if poor_performance_count > 0:
                recommendations.append("⚠️ 部分策略表現不佳，建議重新評估參數設定")
            
            if excellent_performance_count > 0:
                recommendations.append("🏆 部分策略表現優秀，可考慮增加權重或頻率")
        
        # 通用建議
        recommendations.extend([
            "📅 建議在下次交易日早上實施參數調整",
            "👀 實施後請密切監控48小時，如有異常立即回滾",
            "📊 建議設定30天後的下次優化提醒"
        ])
        
        return recommendations
    
    def schedule_optimization(self):
        """設定優化排程（簡化版本）"""
        logger.info(f"📅 優化排程配置: {self.schedule_config.frequency}")
        logger.info("� 提示: 實際部署時可集成cron或APScheduler進行定時執行")
    
    def _run_scheduled_optimization(self):
        """執行排程的優化（同步包裝器）"""
        try:
            # 簡化版本：直接調用異步函數
            logger.info("🔄 執行排程優化任務")
            return asyncio.create_task(self._async_scheduled_optimization())
        except Exception as e:
            logger.error(f"❌ 排程優化執行失敗: {e}")
    
    async def _async_scheduled_optimization(self):
        """異步執行排程的優化"""
        async with MonthlyAutoOptimizer() as optimizer:
            result = await optimizer.run_monthly_optimization()
            
            # 保存結果
            output_file = Path(__file__).parent / f"monthly_optimization_{datetime.now().strftime('%Y%m%d')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"📁 月度優化結果已保存: {output_file}")
    
    def get_next_optimization_schedule(self) -> str:
        """獲取下次優化排程時間"""
        if self.schedule_config.frequency == "monthly":
            next_month = datetime.now().replace(day=1, hour=2, minute=0, second=0, microsecond=0)
            if next_month <= datetime.now():
                if next_month.month == 12:
                    next_month = next_month.replace(year=next_month.year + 1, month=1)
                else:
                    next_month = next_month.replace(month=next_month.month + 1)
            return next_month.strftime("%Y-%m-%d %H:%M:%S")
        elif self.schedule_config.frequency == "weekly":
            days_ahead = 0 - datetime.now().weekday()  # 下週一
            if days_ahead <= 0:
                days_ahead += 7
            next_week = datetime.now() + timedelta(days=days_ahead)
            next_week = next_week.replace(hour=2, minute=0, second=0, microsecond=0)
            return next_week.strftime("%Y-%m-%d %H:%M:%S")
        
        return "排程未設定"


async def test_monthly_optimizer():
    """測試月度自動優化器"""
    logger.info("🧪 開始測試月度自動優化器")
    
    async with MonthlyAutoOptimizer() as optimizer:
        # 分析市場條件
        market_condition = await optimizer.analyze_market_conditions("BTCUSDT", "1h", 7)
        logger.info(f"📊 市場條件: {market_condition.regime.value}")
        
        # 執行簡化的月度優化
        result = await optimizer.run_monthly_optimization()
        
        # 輸出結果摘要
        if "error" not in result:
            logger.info(f"✅ 月度優化完成")
            logger.info(f"📊 建議數量: {len(result['recommendations'])}")
            
            for i, rec in enumerate(result['recommendations'][:3], 1):
                logger.info(f"   {i}. {rec}")
        else:
            logger.error(f"❌ 月度優化失敗: {result['error']}")
        
        # 保存結果到臨時檔案
        output_file = Path(__file__).parent / "monthly_optimization_test_temp.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📁 結果已保存到: {output_file}")
        return result


if __name__ == "__main__":
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 運行測試
    asyncio.run(test_monthly_optimizer())
