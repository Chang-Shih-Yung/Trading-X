"""
Trading-X 市場條件配置使用示例
展示如何在實際交易系統中集成和使用市場條件配置
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import logging

from market_config_loader import (
    MarketConditionConfig, MarketCondition, StrategyType, 
    ConfidenceLevel, create_config_manager
)

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MarketAnalyzer:
    """市場分析器 - 使用配置系統進行市場條件判斷"""
    
    def __init__(self, config_manager: MarketConditionConfig):
        self.config = config_manager
        self.current_market_condition = None
        self.current_confidence = None
        self.last_analysis_time = None
    
    async def analyze_market_condition(self, market_data: Dict[str, float]) -> tuple:
        """
        分析當前市場條件
        
        Args:
            market_data: 包含各種指標數據的字典
            
        Returns:
            (market_condition, confidence_level, score)
        """
        logger.info("開始分析市場條件...")
        
        # 計算各個市場條件的評分
        condition_scores = {}
        condition_confidences = {}
        
        for condition in MarketCondition:
            try:
                score, confidence = self.config.calculate_market_score(
                    condition, market_data
                )
                condition_scores[condition] = score
                condition_confidences[condition] = confidence
                
                logger.info(f"{condition.value} 市場評分: {score:.2f} ({confidence.value})")
                
            except Exception as e:
                logger.error(f"計算 {condition.value} 評分時出錯: {e}")
                condition_scores[condition] = 0.0
                condition_confidences[condition] = ConfidenceLevel.LOW
        
        # 確定主導市場條件
        best_condition = max(condition_scores.items(), key=lambda x: x[1])
        self.current_market_condition = best_condition[0]
        self.current_confidence = condition_confidences[best_condition[0]]
        self.last_analysis_time = datetime.now()
        
        logger.info(f"當前市場條件: {self.current_market_condition.value} "
                   f"(評分: {best_condition[1]:.2f}, 信心度: {self.current_confidence.value})")
        
        return self.current_market_condition, self.current_confidence, best_condition[1]
    
    def get_recommended_strategies(self, 
                                 market_condition: Optional[MarketCondition] = None) -> List[Dict]:
        """獲取推薦策略"""
        if market_condition is None:
            market_condition = self.current_market_condition
        
        if market_condition is None:
            logger.warning("未進行市場分析，無法提供策略建議")
            return []
        
        strategies = []
        market_config = self.config.get_market_condition_config(market_condition)
        strategy_configs = market_config.get("strategies", {})
        
        for strategy_name, strategy_data in strategy_configs.items():
            strategy_info = {
                "name": strategy_data.get("name", strategy_name),
                "type": strategy_name,
                "timeframe": strategy_data.get("timeframe", "1h"),
                "entry_conditions": strategy_data.get("entry", {}),
                "exit_conditions": strategy_data.get("exit", {}),
                "indicators": strategy_data.get("indicators", []),
                "market_condition": market_condition.value
            }
            strategies.append(strategy_info)
        
        return strategies


class PortfolioManager:
    """投資組合管理器 - 基於市場條件調整持倉"""
    
    def __init__(self, config_manager: MarketConditionConfig, initial_capital: float = 10000):
        self.config = config_manager
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}
        self.risk_config = config_manager.get_risk_management_config()
    
    def calculate_position_size(self, 
                              symbol: str, 
                              market_condition: MarketCondition,
                              confidence: ConfidenceLevel,
                              current_price: float) -> float:
        """
        計算合適的倉位大小
        
        Args:
            symbol: 交易對
            market_condition: 市場條件
            confidence: 信心度
            current_price: 當前價格
            
        Returns:
            建議倉位大小 (USD)
        """
        # 獲取資產參數
        asset_params = self.config.get_asset_parameters(symbol.replace("USDT", ""))
        if not asset_params:
            logger.warning(f"未找到 {symbol} 的資產參數，使用默認值")
            volatility_factor = 1.0
        else:
            volatility_factor = asset_params.volatility_factor
        
        # 基礎風險管理
        risk_settings = self.risk_config.get("position_sizing", {})
        
        # 根據信心度調整風險偏好
        if confidence == ConfidenceLevel.HIGH:
            risk_profile = risk_settings.get("aggressive", {"max_per_trade": 0.1})
        elif confidence == ConfidenceLevel.MEDIUM:
            risk_profile = risk_settings.get("moderate", {"max_per_trade": 0.05})
        else:
            risk_profile = risk_settings.get("conservative", {"max_per_trade": 0.02})
        
        # 計算基礎倉位
        max_per_trade = risk_profile.get("max_per_trade", 0.05)
        base_position = self.current_capital * max_per_trade
        
        # 根據波動率調整
        adjusted_position = base_position / volatility_factor
        
        # 確保不超過風險限制
        max_total_exposure = self.current_capital * risk_settings.get("moderate", {}).get("max_total", 0.5)
        current_exposure = sum(abs(pos["value"]) for pos in self.positions.values())
        
        available_exposure = max_total_exposure - current_exposure
        final_position = min(adjusted_position, available_exposure)
        
        logger.info(f"{symbol} 建議倉位: ${final_position:.2f} "
                   f"(信心度: {confidence.value}, 波動因子: {volatility_factor})")
        
        return max(0, final_position)
    
    def update_position(self, symbol: str, quantity: float, price: float, action: str):
        """更新持倉信息"""
        if symbol not in self.positions:
            self.positions[symbol] = {"quantity": 0, "avg_price": 0, "value": 0}
        
        if action == "buy":
            old_quantity = self.positions[symbol]["quantity"]
            old_value = self.positions[symbol]["value"]
            
            new_quantity = old_quantity + quantity
            new_value = old_value + (quantity * price)
            
            self.positions[symbol]["quantity"] = new_quantity
            self.positions[symbol]["avg_price"] = new_value / new_quantity if new_quantity > 0 else 0
            self.positions[symbol]["value"] = new_value
            
            self.current_capital -= quantity * price
            
        elif action == "sell":
            if self.positions[symbol]["quantity"] >= quantity:
                self.positions[symbol]["quantity"] -= quantity
                self.positions[symbol]["value"] -= quantity * self.positions[symbol]["avg_price"]
                
                self.current_capital += quantity * price
                
                if self.positions[symbol]["quantity"] == 0:
                    del self.positions[symbol]
        
        logger.info(f"更新持倉 {symbol}: {action} {quantity} @ ${price}")


class TradingBot:
    """自動化交易機器人 - 整合市場分析和投資組合管理"""
    
    def __init__(self, config_path: str = None):
        self.config_manager = create_config_manager(config_path)
        self.market_analyzer = MarketAnalyzer(self.config_manager)
        self.portfolio_manager = PortfolioManager(self.config_manager)
        self.running = False
    
    async def start(self):
        """啟動交易機器人"""
        self.running = True
        logger.info("交易機器人已啟動")
        
        while self.running:
            try:
                # 模擬獲取市場數據
                market_data = await self.fetch_market_data()
                
                # 分析市場條件
                market_condition, confidence, score = await self.market_analyzer.analyze_market_condition(market_data)
                
                # 獲取策略建議
                strategies = self.market_analyzer.get_recommended_strategies(market_condition)
                
                # 執行交易邏輯
                await self.execute_trading_logic(market_condition, confidence, strategies)
                
                # 等待下一個分析週期
                await asyncio.sleep(300)  # 5分鐘間隔
                
            except Exception as e:
                logger.error(f"交易循環出錯: {e}")
                await asyncio.sleep(60)  # 出錯時等待1分鐘
    
    async def fetch_market_data(self) -> Dict[str, float]:
        """
        模擬獲取市場數據
        在實際應用中，這裡會連接到真實的數據源
        """
        # 模擬數據 - 實際應用中應該連接到Binance API等
        import random
        
        market_data = {
            "MA200_slope": random.uniform(-0.05, 0.05),
            "RSI_14": random.uniform(20, 80),
            "MACD_histogram": random.uniform(-1, 1),
            "MVRV": random.uniform(0.5, 3.0),
            "FearGreed": random.uniform(10, 90),
            "FundingRate": random.uniform(-0.02, 0.02),
            "Volume_MA": random.uniform(0.5, 3.0),
            "BB_position": random.uniform(0, 1),
            "OI_growth": random.uniform(-0.1, 0.1)
        }
        
        return market_data
    
    async def execute_trading_logic(self, 
                                  market_condition: MarketCondition,
                                  confidence: ConfidenceLevel,
                                  strategies: List[Dict]):
        """執行交易邏輯"""
        logger.info(f"執行交易邏輯 - 市場條件: {market_condition.value}, 信心度: {confidence.value}")
        
        # 獲取交易資產
        assets = self.config_manager.get_assets("all")
        
        for asset in assets:
            symbol = f"{asset}USDT"
            
            # 模擬當前價格
            mock_price = 100.0  # 實際應該從API獲取
            
            # 計算建議倉位
            position_size = self.portfolio_manager.calculate_position_size(
                symbol, market_condition, confidence, mock_price
            )
            
            # 基於策略和市場條件決定是否交易
            if position_size > 0 and self._should_trade(market_condition, confidence, strategies):
                logger.info(f"建議開倉 {symbol}: ${position_size:.2f}")
                # 在實際應用中，這裡會執行真實的交易
    
    def _should_trade(self, 
                     market_condition: MarketCondition,
                     confidence: ConfidenceLevel,
                     strategies: List[Dict]) -> bool:
        """判斷是否應該交易"""
        # 簡單的交易決策邏輯
        if confidence == ConfidenceLevel.LOW:
            return False
        
        if market_condition == MarketCondition.BEAR and confidence != ConfidenceLevel.HIGH:
            return False
        
        return len(strategies) > 0
    
    def stop(self):
        """停止交易機器人"""
        self.running = False
        logger.info("交易機器人已停止")


async def main():
    """主程序入口"""
    # 創建並啟動交易機器人
    bot = TradingBot()
    
    try:
        # 運行10個週期後自動停止（示例）
        task = asyncio.create_task(bot.start())
        await asyncio.sleep(60)  # 運行1分鐘
        bot.stop()
        await task
        
    except KeyboardInterrupt:
        logger.info("接收到中斷信號，正在停止...")
        bot.stop()


if __name__ == "__main__":
    # 運行示例
    asyncio.run(main())
