"""
量子決策系統配置管理器
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .quantum_decision_optimizer import QuantumDecisionConfig

logger = logging.getLogger(__name__)

@dataclass
class SymbolConfig:
    """交易對配置"""
    symbol: str
    weight: float
    max_position: float
    min_volume_24h: float

@dataclass 
class RegimeDefinition:
    """市場制度定義"""
    name: str
    description: str
    characteristics: Dict[str, Any]

@dataclass
class HypothesisTemplate:
    """假設模板"""
    direction: int
    base_expected_return: float
    base_risk: float
    time_horizon_minutes: int
    confidence_factors: Dict[str, float]

class QuantumConfigManager:
    """量子決策系統配置管理器"""
    
    def __init__(self, config_path: str = "config/quantum_config.json"):
        self.config_path = Path(config_path)
        self.config_data: Optional[Dict[str, Any]] = None
        self.load_config()
    
    def load_config(self):
        """加載配置文件"""
        try:
            if not self.config_path.exists():
                logger.error(f"配置文件不存在: {self.config_path}")
                raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
            
            logger.info(f"配置文件加載成功: {self.config_path}")
            
        except json.JSONDecodeError as e:
            logger.error(f"配置文件JSON格式錯誤: {e}")
            raise
        except Exception as e:
            logger.error(f"加載配置文件失敗: {e}")
            raise
    
    def get_quantum_decision_config(self) -> QuantumDecisionConfig:
        """獲取量子決策配置"""
        if not self.config_data:
            raise ValueError("配置數據未加載")
        
        config = self.config_data["quantum_decision_config"]
        
        return QuantumDecisionConfig(
            # SPRT 參數
            alpha=config["sprt_parameters"]["alpha"],
            beta=config["sprt_parameters"]["beta"],
            
            # 信念更新參數
            forgetting_factor=config["belief_update"]["forgetting_factor"],
            regime_update_freq=config["belief_update"]["regime_update_frequency_minutes"],
            
            # Kelly 資金管理
            kelly_multiplier=config["kelly_management"]["kelly_multiplier"],
            max_position_cap=config["kelly_management"]["max_position_cap"],
            min_er_threshold=config["kelly_management"]["min_expected_return_threshold"],
            
            # 風險控制
            max_drawdown=config["risk_control"]["max_drawdown"],
            volatility_lookback=config["risk_control"]["volatility_lookback_minutes"],
            
            # 市場制度參數
            n_regimes=config["market_regime"]["n_regimes"],
            regime_features=config["market_regime"]["regime_features"]
        )
    
    def get_active_symbols(self) -> List[SymbolConfig]:
        """獲取活躍交易對配置"""
        if not self.config_data:
            raise ValueError("配置數據未加載")
        
        symbols = []
        for symbol_data in self.config_data["active_symbols"]:
            symbols.append(SymbolConfig(
                symbol=symbol_data["symbol"],
                weight=symbol_data["weight"],
                max_position=symbol_data["max_position"],
                min_volume_24h=symbol_data["min_volume_24h"]
            ))
        
        return symbols
    
    def get_regime_definitions(self) -> Dict[int, RegimeDefinition]:
        """獲取市場制度定義"""
        if not self.config_data:
            raise ValueError("配置數據未加載")
        
        regimes = {}
        for regime_id, regime_data in self.config_data["regime_definitions"].items():
            regimes[int(regime_id)] = RegimeDefinition(
                name=regime_data["name"],
                description=regime_data["description"],
                characteristics=regime_data["characteristics"]
            )
        
        return regimes
    
    def get_hypothesis_templates(self) -> Dict[str, HypothesisTemplate]:
        """獲取假設模板"""
        if not self.config_data:
            raise ValueError("配置數據未加載")
        
        templates = {}
        for template_name, template_data in self.config_data["hypothesis_templates"].items():
            templates[template_name] = HypothesisTemplate(
                direction=template_data["direction"],
                base_expected_return=template_data["base_expected_return"],
                base_risk=template_data["base_risk"],
                time_horizon_minutes=template_data["time_horizon_minutes"],
                confidence_factors=template_data["confidence_factors"]
            )
        
        return templates
    
    def get_technical_indicator_config(self) -> Dict[str, Any]:
        """獲取技術指標配置"""
        if not self.config_data:
            raise ValueError("配置數據未加載")
        
        return self.config_data["quantum_decision_config"]["data_processing"]["technical_indicator_periods"]
    
    def get_execution_config(self) -> Dict[str, Any]:
        """獲取執行配置"""
        if not self.config_data:
            raise ValueError("配置數據未加載")
        
        return self.config_data["quantum_decision_config"]["execution"]
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """獲取監控配置"""
        if not self.config_data:
            raise ValueError("配置數據未加載")
        
        return self.config_data["quantum_decision_config"]["monitoring"]
    
    def update_config(self, section: str, key: str, value: Any):
        """動態更新配置"""
        if not self.config_data:
            raise ValueError("配置數據未加載")
        
        try:
            # 支持嵌套鍵，例如 "sprt_parameters.alpha"
            keys = key.split('.')
            current = self.config_data["quantum_decision_config"]
            
            for k in keys[:-1]:
                current = current[k]
            
            current[keys[-1]] = value
            
            logger.info(f"配置更新: {section}.{key} = {value}")
            
        except KeyError as e:
            logger.error(f"配置鍵不存在: {section}.{key}")
            raise
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置已保存到: {self.config_path}")
            
        except Exception as e:
            logger.error(f"保存配置失敗: {e}")
            raise
    
    def validate_config(self) -> bool:
        """驗證配置完整性"""
        try:
            if not self.config_data:
                return False
            
            required_sections = [
                "quantum_decision_config",
                "active_symbols", 
                "regime_definitions",
                "hypothesis_templates"
            ]
            
            for section in required_sections:
                if section not in self.config_data:
                    logger.error(f"缺少配置節: {section}")
                    return False
            
            # 驗證量子決策配置
            qdc = self.config_data["quantum_decision_config"]
            required_qdc_sections = [
                "sprt_parameters",
                "belief_update", 
                "kelly_management",
                "risk_control",
                "market_regime"
            ]
            
            for section in required_qdc_sections:
                if section not in qdc:
                    logger.error(f"缺少量子決策配置節: {section}")
                    return False
            
            # 驗證 SPRT 參數範圍
            sprt = qdc["sprt_parameters"]
            if not (0 < sprt["alpha"] < 1):
                logger.error(f"SPRT alpha 參數無效: {sprt['alpha']}")
                return False
            
            if not (0 < sprt["beta"] < 1):
                logger.error(f"SPRT beta 參數無效: {sprt['beta']}")
                return False
            
            logger.info("配置驗證通過")
            return True
            
        except Exception as e:
            logger.error(f"配置驗證失敗: {e}")
            return False

# 全局配置管理器實例
_config_manager = None

def get_config_manager(config_path: str = "config/quantum_config.json") -> QuantumConfigManager:
    """獲取配置管理器單例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = QuantumConfigManager(config_path)
    return _config_manager

def reload_config():
    """重新加載配置"""
    global _config_manager
    if _config_manager:
        _config_manager.load_config()
    else:
        _config_manager = QuantumConfigManager()

if __name__ == "__main__":
    # 測試配置管理器
    manager = QuantumConfigManager()
    
    if manager.validate_config():
        config = manager.get_quantum_decision_config()
        symbols = manager.get_active_symbols()
        regimes = manager.get_regime_definitions()
        
        print(f"量子決策配置: {config}")
        print(f"活躍交易對數量: {len(symbols)}")
        print(f"市場制度數量: {len(regimes)}")
    else:
        print("配置驗證失敗")
