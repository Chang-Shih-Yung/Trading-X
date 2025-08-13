"""
🎯 Trading X - WebSocket實時驅動器配置模組
處理所有配置相關功能
智能觸發引擎整合 & 回測驗證器整合配置
"""

import json
import logging
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path

logger = logging.getLogger(__name__)

class WebSocketRealtimeConfig:
    """WebSocket實時驅動器配置管理"""
    
    def __init__(self, config_path: str = None):
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
        
    def _get_default_config_path(self) -> str:
        """獲取預設配置路徑"""
        # 優先使用同目錄下的配置文件
        config_file = Path(__file__).parent / "websocket_realtime_config.json"
        if config_file.exists():
            return str(config_file)
        
        # 回退到父目錄
        fallback_path = Path(__file__).parent.parent / "websocket_realtime_config.json"
        return str(fallback_path)
    
    def _load_config(self) -> Dict[str, Any]:
        """載入配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.logger.info(f"✅ 配置載入成功: {self.config_path}")
            return config
        except FileNotFoundError:
            self.logger.warning(f"⚠️ 配置文件不存在，使用預設配置: {self.config_path}")
            return self._get_default_config()
        except Exception as e:
            self.logger.error(f"❌ 配置載入失敗: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """獲取默認配置"""
        return {
            "websocket_realtime_driver": {
                "target_latency_ms": 50,
                "throughput_target": 1000,
                "parallel_connections": True,
                "fallback_enabled": True,
                "intelligent_trigger_integration": True,
                "backtest_validator_integration": True
            },
            "exchanges": {
                "binance": {
                    "enabled": True,
                    "weight": 0.7,
                    "endpoints": {
                        "spot": "wss://stream.binance.com:9443/ws/",
                        "futures": "wss://fstream.binance.com/ws/"
                    }
                },
                "okx": {
                    "enabled": True,
                    "weight": 0.2,
                    "endpoints": {
                        "spot": "wss://ws.okx.com:8443/ws/v5/public"
                    }
                },
                "bybit": {
                    "enabled": True,
                    "weight": 0.1,
                    "endpoints": {
                        "spot": "wss://stream.bybit.com/v5/public/spot"
                    }
                }
            },
            "performance": {
                "max_latency_ms": 12,
                "buffer_size": 1000,
                "heartbeat_interval": 30,
                "high_performance_mode": False
            },
            "integration": {
                "intelligent_trigger": {
                    "enabled": True,
                    "data_forwarding": ["ticker", "kline", "depth", "trade"],
                    "conversion_format": "trigger_format"
                },
                "backtest_validator": {
                    "enabled": True,
                    "price_updates": ["ticker", "kline"],
                    "real_time_tracking": True
                }
            }
        }
    
    def get_websocket_config(self) -> Dict[str, Any]:
        """獲取WebSocket配置"""
        return self.config.get("websocket_realtime_driver", {})
    
    def get_exchange_config(self, exchange: str = None) -> Dict[str, Any]:
        """獲取交易所配置"""
        exchanges = self.config.get("exchanges", {})
        if exchange:
            return exchanges.get(exchange, {})
        return exchanges
    
    def get_performance_config(self) -> Dict[str, Any]:
        """獲取性能配置"""
        return self.config.get("performance", {})
    
    def get_integration_config(self) -> Dict[str, Any]:
        """獲取整合配置"""
        return self.config.get("integration", {})
    
    def is_intelligent_trigger_enabled(self) -> bool:
        """檢查智能觸發引擎是否啟用"""
        return self.config.get("integration", {}).get("intelligent_trigger", {}).get("enabled", False)
    
    def is_backtest_validator_enabled(self) -> bool:
        """檢查回測驗證器是否啟用"""
        return self.config.get("integration", {}).get("backtest_validator", {}).get("enabled", False)
    
    def get_target_latency(self) -> int:
        """獲取目標延遲"""
        return self.config.get("websocket_realtime_driver", {}).get("target_latency_ms", 50)
    
    def get_throughput_target(self) -> int:
        """獲取吞吐量目標"""
        return self.config.get("websocket_realtime_driver", {}).get("throughput_target", 1000)
    
    def is_high_performance_mode(self) -> bool:
        """檢查是否啟用高性能模式"""
        return self.config.get("performance", {}).get("high_performance_mode", False)
    
    def get_enabled_exchanges(self) -> List[str]:
        """獲取啟用的交易所列表"""
        exchanges = self.config.get("exchanges", {})
        return [name for name, config in exchanges.items() if config.get("enabled", False)]
    
    def get_exchange_endpoints(self, exchange: str) -> Dict[str, str]:
        """獲取交易所端點"""
        return self.config.get("exchanges", {}).get(exchange, {}).get("endpoints", {})
    
    def get_exchange_weight(self, exchange: str) -> float:
        """獲取交易所權重"""
        return self.config.get("exchanges", {}).get(exchange, {}).get("weight", 0.0)
    
    def update_config(self, key_path: str, value: Any):
        """更新配置值"""
        try:
            keys = key_path.split('.')
            config_ref = self.config
            
            # 導航到目標位置
            for key in keys[:-1]:
                if key not in config_ref:
                    config_ref[key] = {}
                config_ref = config_ref[key]
            
            # 設置值
            config_ref[keys[-1]] = value
            
            self.logger.info(f"✅ 配置更新成功: {key_path} = {value}")
            
        except Exception as e:
            self.logger.error(f"❌ 配置更新失敗: {e}")
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"✅ 配置保存成功: {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"❌ 配置保存失敗: {e}")
    
    def reload_config(self):
        """重新載入配置"""
        try:
            self.config = self._load_config()
            self.logger.info("✅ 配置重新載入成功")
            
        except Exception as e:
            self.logger.error(f"❌ 配置重新載入失敗: {e}")
    
    def validate_config(self) -> bool:
        """驗證配置有效性"""
        try:
            # 檢查必要的配置項
            required_keys = [
                "websocket_realtime_driver",
                "exchanges",
                "performance"
            ]
            
            for key in required_keys:
                if key not in self.config:
                    self.logger.error(f"❌ 缺少必要配置項: {key}")
                    return False
            
            # 檢查交易所配置
            exchanges = self.config.get("exchanges", {})
            if not exchanges:
                self.logger.error("❌ 沒有配置任何交易所")
                return False
            
            enabled_exchanges = self.get_enabled_exchanges()
            if not enabled_exchanges:
                self.logger.error("❌ 沒有啟用任何交易所")
                return False
            
            # 檢查性能配置
            performance = self.config.get("performance", {})
            max_latency = performance.get("max_latency_ms", 0)
            if max_latency <= 0:
                self.logger.error("❌ 無效的延遲配置")
                return False
            
            self.logger.info("✅ 配置驗證通過")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 配置驗證失敗: {e}")
            return False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """獲取配置摘要"""
        try:
            return {
                "config_path": self.config_path,
                "target_latency_ms": self.get_target_latency(),
                "throughput_target": self.get_throughput_target(),
                "enabled_exchanges": self.get_enabled_exchanges(),
                "high_performance_mode": self.is_high_performance_mode(),
                "intelligent_trigger_enabled": self.is_intelligent_trigger_enabled(),
                "backtest_validator_enabled": self.is_backtest_validator_enabled(),
                "total_exchange_count": len(self.config.get("exchanges", {})),
                "enabled_exchange_count": len(self.get_enabled_exchanges())
            }
            
        except Exception as e:
            self.logger.error(f"❌ 獲取配置摘要失敗: {e}")
            return {"error": str(e)}

# 全局配置實例
websocket_config = WebSocketRealtimeConfig()

# 便捷函數
def get_websocket_config() -> WebSocketRealtimeConfig:
    """獲取WebSocket配置實例"""
    return websocket_config

def reload_websocket_config():
    """重新載入WebSocket配置"""
    websocket_config.reload_config()

def get_target_latency() -> int:
    """獲取目標延遲"""
    return websocket_config.get_target_latency()

def get_enabled_exchanges() -> List[str]:
    """獲取啟用的交易所"""
    return websocket_config.get_enabled_exchanges()

def is_integration_enabled(integration_type: str) -> bool:
    """檢查整合是否啟用"""
    if integration_type == "intelligent_trigger":
        return websocket_config.is_intelligent_trigger_enabled()
    elif integration_type == "backtest_validator":
        return websocket_config.is_backtest_validator_enabled()
    return False
