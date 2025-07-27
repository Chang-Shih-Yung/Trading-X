"""
Trading-X 市場條件配置加載器
提供統一的配置管理和市場條件分析功能
"""

import json
import os
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketCondition(Enum):
    """市場條件枚舉"""
    BULL = "bull"
    BEAR = "bear"
    SIDEWAY = "sideway"


class StrategyType(Enum):
    """策略類型枚舉"""
    SCALPING = "scalping"
    SHORT_TERM = "short_term"
    MID_TERM = "mid_term"
    LONG_TERM = "long_term"
    RANGE_TRADING = "range_trading"
    DEFENSIVE = "defensive"


class ConfidenceLevel(Enum):
    """信心度等級"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class IndicatorCondition:
    """技術指標條件"""
    name: str
    threshold: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    weight: float = 1.0
    description: str = ""
    timeframe: str = "1h"
    applicable_assets: List[str] = field(default_factory=list)


@dataclass
class StrategyConfig:
    """策略配置"""
    name: str
    timeframe: str
    entry_conditions: Dict[str, Any]
    exit_conditions: Dict[str, Any]
    stop_loss: str
    indicators: List[str]
    position_sizing: Optional[str] = None
    risk_reward: Optional[str] = None


@dataclass
class AssetParameters:
    """資產特定參數"""
    symbol: str
    volatility_factor: float
    entry_padding: float
    stop_loss_multiplier: float
    min_volume_24h: Optional[float] = None
    market_cap_rank: Optional[int] = None
    special_attributes: Dict[str, Any] = field(default_factory=dict)


class MarketConditionConfig:
    """市場條件配置管理器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路徑，默認為相對路徑
        """
        if config_path is None:
            # 默認配置文件路徑
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, "market_conditions_config.json")
        
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config()
        
        logger.info(f"配置已載入: {self.config.get('description', 'Trading-X Config')}")
        logger.info(f"配置版本: {self.config.get('version', 'Unknown')}")
    
    def _load_config(self) -> Dict[str, Any]:
        """載入JSON配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            logger.error(f"配置文件未找到: {self.config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"配置文件JSON格式錯誤: {e}")
            raise
    
    def _validate_config(self) -> None:
        """驗證配置文件的完整性"""
        required_keys = ["market_conditions", "custom_parameters", "assets"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"配置文件缺少必要鍵值: {key}")
        
        # 驗證市場條件
        for condition in MarketCondition:
            if condition.value not in self.config["market_conditions"]:
                logger.warning(f"配置中缺少市場條件: {condition.value}")
    
    def get_market_conditions(self) -> List[str]:
        """獲取所有可用的市場條件"""
        return list(self.config["market_conditions"].keys())
    
    def get_assets(self, category: str = "all") -> List[str]:
        """
        獲取資產列表
        
        Args:
            category: 資產類別 (all, major, altcoins)
        """
        assets_config = self.config.get("assets", {})
        if isinstance(assets_config, list):
            # 兼容舊格式
            return assets_config
        
        return assets_config.get(category, assets_config.get("all", []))
    
    def get_timeframes(self, strategy_type: str = "all") -> List[str]:
        """
        獲取時間框架列表
        
        Args:
            strategy_type: 策略類型 (short_term, mid_term, long_term, all)
        """
        timeframes = self.config.get("timeframes", {})
        if strategy_type == "all":
            all_timeframes = []
            for tf_list in timeframes.values():
                all_timeframes.extend(tf_list)
            return list(set(all_timeframes))
        
        return timeframes.get(strategy_type, [])
    
    def get_market_condition_config(self, condition: Union[MarketCondition, str]) -> Dict[str, Any]:
        """
        獲取特定市場條件的配置
        
        Args:
            condition: 市場條件
        """
        if isinstance(condition, MarketCondition):
            condition = condition.value
        
        return self.config["market_conditions"].get(condition, {})
    
    def get_indicator_conditions(self, 
                               market_condition: Union[MarketCondition, str],
                               indicator_type: str = "technical_indicators") -> List[IndicatorCondition]:
        """
        獲取指標條件列表
        
        Args:
            market_condition: 市場條件
            indicator_type: 指標類型 (technical_indicators, on_chain_metrics, etc.)
        """
        market_config = self.get_market_condition_config(market_condition)
        conditions_config = market_config.get("conditions", {}).get(indicator_type, {})
        
        indicator_conditions = []
        for name, config in conditions_config.items():
            condition = IndicatorCondition(
                name=name,
                threshold=config.get("threshold"),
                min_value=config.get("min", config.get("min_value")),
                max_value=config.get("max", config.get("max_value")),
                weight=config.get("weight", 1.0),
                description=config.get("description", ""),
                timeframe=config.get("timeframe", "1h"),
                applicable_assets=config.get("applicable_assets", [])
            )
            indicator_conditions.append(condition)
        
        return indicator_conditions
    
    def get_strategy_config(self, 
                          market_condition: Union[MarketCondition, str],
                          strategy_type: Union[StrategyType, str]) -> Optional[StrategyConfig]:
        """
        獲取策略配置
        
        Args:
            market_condition: 市場條件
            strategy_type: 策略類型
        """
        if isinstance(market_condition, MarketCondition):
            market_condition = market_condition.value
        if isinstance(strategy_type, StrategyType):
            strategy_type = strategy_type.value
        
        market_config = self.get_market_condition_config(market_condition)
        strategies = market_config.get("strategies", {})
        
        if strategy_type not in strategies:
            return None
        
        strategy_data = strategies[strategy_type]
        
        return StrategyConfig(
            name=strategy_data.get("name", f"{market_condition}_{strategy_type}"),
            timeframe=strategy_data.get("timeframe", "1h"),
            entry_conditions=strategy_data.get("entry", {}),
            exit_conditions=strategy_data.get("exit", {}),
            stop_loss=strategy_data.get("stop_loss", "-5%"),
            indicators=strategy_data.get("indicators", []),
            position_sizing=strategy_data.get("position_sizing"),
            risk_reward=strategy_data.get("risk_reward")
        )
    
    def get_asset_parameters(self, symbol: str) -> Optional[AssetParameters]:
        """
        獲取資產特定參數
        
        Args:
            symbol: 資產符號 (例如: BTC, ETH)
        """
        custom_params = self.config.get("custom_parameters", {})
        
        if symbol not in custom_params:
            return None
        
        params = custom_params[symbol]
        special_attrs = {}
        
        # 提取特殊屬性
        for key, value in params.items():
            if key not in ["volatility_factor", "entry_padding", "stop_loss_multiplier", 
                          "min_volume_24h", "market_cap_rank"]:
                special_attrs[key] = value
        
        return AssetParameters(
            symbol=symbol,
            volatility_factor=params.get("volatility_factor", 1.0),
            entry_padding=params.get("entry_padding", 1.0),
            stop_loss_multiplier=params.get("stop_loss_multiplier", 1.0),
            min_volume_24h=params.get("min_volume_24h"),
            market_cap_rank=params.get("market_cap_rank"),
            special_attributes=special_attrs
        )
    
    def calculate_market_score(self, 
                             market_condition: Union[MarketCondition, str],
                             indicator_values: Dict[str, float]) -> Tuple[float, ConfidenceLevel]:
        """
        計算市場條件評分
        
        Args:
            market_condition: 市場條件
            indicator_values: 指標數值字典
            
        Returns:
            (總分, 信心度等級)
        """
        market_config = self.get_market_condition_config(market_condition)
        conditions = market_config.get("conditions", {})
        
        total_score = 0.0
        max_possible_score = 0.0
        
        # 計算各類指標評分
        for indicator_type, indicators in conditions.items():
            for indicator_name, config in indicators.items():
                weight = config.get("weight", 1.0)
                max_possible_score += weight
                
                if indicator_name in indicator_values:
                    value = indicator_values[indicator_name]
                    score = self._evaluate_indicator(value, config)
                    total_score += score * weight
        
        # 標準化評分
        normalized_score = (total_score / max_possible_score * 10) if max_possible_score > 0 else 0
        
        # 確定信心度等級
        threshold = market_config.get("total_score_threshold", 5.0)
        confidence_levels = market_config.get("confidence_levels", {})
        
        if normalized_score >= confidence_levels.get("high", {}).get("min_score", 8.0):
            confidence = ConfidenceLevel.HIGH
        elif normalized_score >= confidence_levels.get("medium", {}).get("min_score", threshold):
            confidence = ConfidenceLevel.MEDIUM
        else:
            confidence = ConfidenceLevel.LOW
        
        return normalized_score, confidence
    
    def _evaluate_indicator(self, value: float, config: Dict[str, Any]) -> float:
        """
        評估單個指標是否符合條件
        
        Args:
            value: 指標數值
            config: 指標配置
            
        Returns:
            評分 (0-1)
        """
        # 閾值檢查
        if "threshold" in config:
            threshold = config["threshold"]
            if "min" in str(config.get("description", "")).lower():
                return 1.0 if value >= threshold else 0.0
            elif "max" in str(config.get("description", "")).lower():
                return 1.0 if value <= threshold else 0.0
            else:
                # 默認為最小閾值
                return 1.0 if value >= threshold else 0.0
        
        # 範圍檢查
        min_val = config.get("min", config.get("min_value"))
        max_val = config.get("max", config.get("max_value"))
        
        if min_val is not None and max_val is not None:
            if min_val <= value <= max_val:
                return 1.0
            else:
                # 計算距離最近邊界的程度
                if value < min_val:
                    distance = (min_val - value) / min_val
                else:
                    distance = (value - max_val) / max_val
                return max(0.0, 1.0 - distance)
        
        elif min_val is not None:
            return 1.0 if value >= min_val else max(0.0, value / min_val)
        
        elif max_val is not None:
            return 1.0 if value <= max_val else max(0.0, max_val / value)
        
        # 特殊條件處理
        if config.get("growth_near_zero"):
            return 1.0 if abs(value) < config.get("threshold", 0.02) else 0.0
        
        if config.get("stable"):
            change_threshold = config.get("change_threshold", 0.05)
            return 1.0 if abs(value) < change_threshold else 0.0
        
        return 0.5  # 默認中性評分
    
    def get_risk_management_config(self) -> Dict[str, Any]:
        """獲取風險管理配置"""
        return self.config.get("risk_management", {})
    
    def get_data_sources(self) -> Dict[str, List[str]]:
        """獲取數據源配置"""
        return self.config.get("data_sources", {})
    
    def get_update_intervals(self) -> Dict[str, List[str]]:
        """獲取更新間隔配置"""
        return self.config.get("update_intervals", {})
    
    def reload_config(self) -> None:
        """重新載入配置文件"""
        logger.info("重新載入配置文件...")
        self.config = self._load_config()
        self._validate_config()
        logger.info("配置重新載入完成")


# 便捷函數
def create_config_manager(config_path: str = None) -> MarketConditionConfig:
    """創建配置管理器實例"""
    return MarketConditionConfig(config_path)


def get_default_config() -> MarketConditionConfig:
    """獲取默認配置管理器"""
    return MarketConditionConfig()


# 使用示例
if __name__ == "__main__":
    # 創建配置管理器
    config_manager = get_default_config()
    
    # 獲取資產列表
    all_assets = config_manager.get_assets("all")
    major_assets = config_manager.get_assets("major")
    print(f"所有資產: {all_assets}")
    print(f"主要資產: {major_assets}")
    
    # 獲取牛市策略配置
    bull_scalping = config_manager.get_strategy_config("bull", "scalping")
    if bull_scalping:
        print(f"牛市剝頭皮策略: {bull_scalping.name}")
        print(f"時間框架: {bull_scalping.timeframe}")
    
    # 獲取BTC參數
    btc_params = config_manager.get_asset_parameters("BTC")
    if btc_params:
        print(f"BTC 波動因子: {btc_params.volatility_factor}")
    
    # 計算市場評分示例
    sample_indicators = {
        "MA200_slope": 0.025,
        "RSI_14": 65,
        "MACD_histogram": 0.5,
        "MVRV": 1.5,
        "FearGreed": 70
    }
    
    score, confidence = config_manager.calculate_market_score("bull", sample_indicators)
    print(f"牛市評分: {score:.2f}, 信心度: {confidence.value}")
