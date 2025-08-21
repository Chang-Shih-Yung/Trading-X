"""
閃崩檢測系統
多重時間框架的市場異常檢測機制
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import aiohttp
import logging
from pathlib import Path
import fcntl

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CrashSeverity(Enum):
    """崩盤嚴重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

class CrashType(Enum):
    """崩盤類型"""
    FLASH_CRASH_5MIN = "flash_crash_5min"
    RAPID_DECLINE_15MIN = "rapid_decline_15min"
    SUSTAINED_CRASH_1HOUR = "sustained_crash_1hour"
    EXTREME_CRASH_24HOUR = "extreme_crash_24hour"
    VOLUME_ANOMALY = "volume_anomaly"
    LIQUIDITY_CRISIS = "liquidity_crisis"

@dataclass
class CrashDetectionConfig:
    """崩盤檢測配置"""
    crash_type: CrashType
    timeframe_minutes: int
    price_threshold_percent: float
    volume_multiplier: Optional[float] = None
    confirmation_count: int = 2
    monitoring_interval_seconds: int = 60
    action_duration_minutes: int = 30

@dataclass
class MarketData:
    """市場數據結構"""
    symbol: str
    timestamp: datetime
    price: float
    volume: float
    high: float
    low: float

@dataclass
class CrashEvent:
    """崩盤事件結構"""
    event_id: str
    symbol: str
    crash_type: CrashType
    severity: CrashSeverity
    detection_time: datetime
    price_before: float
    price_lowest: float
    drop_percentage: float
    volume_spike: bool
    volume_multiplier: float
    trigger_conditions: Dict[str, Any]
    system_action: Dict[str, Any]

class CrashDetector:
    """閃崩檢測器"""
    
    def __init__(self, config_path: str = None):
        # 修正為X資料夾內的相對路徑
        if config_path is None:
            self.base_dir = Path(__file__).parent.parent.parent
            config_path = self.base_dir / "config" / "crash_detection_config.json"
        
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 檢測配置
        self.detection_configs = self._load_detection_configs()
        
        # 數據存儲
        self.price_history: Dict[str, List[MarketData]] = {}
        self.volume_history: Dict[str, List[float]] = {}
        self.crash_events: List[CrashEvent] = []
        
        # 監控狀態
        self.is_monitoring = False
        self.protected_symbols: Dict[str, datetime] = {}  # 受保護的交易對及解除時間
        
        # 設置交易對
        self.symbols = ["XRPUSDT", "DOGEUSDT", "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"]
        
        # 檔案鎖定路徑
        # 文件鎖和日誌 (修正為X資料夾內)
        self.lock_file_path = self.base_dir / "data" / "locks" / "crash_detector.lock"
        self.lock_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_detection_configs(self) -> List[CrashDetectionConfig]:
        """載入檢測配置"""
        default_configs = [
            # 5分鐘閃崩檢測
            CrashDetectionConfig(
                crash_type=CrashType.FLASH_CRASH_5MIN,
                timeframe_minutes=5,
                price_threshold_percent=10.0,
                confirmation_count=2,
                monitoring_interval_seconds=60,
                action_duration_minutes=30
            ),
            # 15分鐘急速下跌
            CrashDetectionConfig(
                crash_type=CrashType.RAPID_DECLINE_15MIN,
                timeframe_minutes=15,
                price_threshold_percent=15.0,
                volume_multiplier=3.0,
                confirmation_count=2,
                monitoring_interval_seconds=180,
                action_duration_minutes=60
            ),
            # 1小時持續暴跌
            CrashDetectionConfig(
                crash_type=CrashType.SUSTAINED_CRASH_1HOUR,
                timeframe_minutes=60,
                price_threshold_percent=20.0,
                confirmation_count=3,
                monitoring_interval_seconds=300,
                action_duration_minutes=240
            ),
            # 24小時極端崩盤
            CrashDetectionConfig(
                crash_type=CrashType.EXTREME_CRASH_24HOUR,
                timeframe_minutes=1440,
                price_threshold_percent=30.0,
                confirmation_count=3,
                monitoring_interval_seconds=900,
                action_duration_minutes=1440
            ),
            # 成交量異常
            CrashDetectionConfig(
                crash_type=CrashType.VOLUME_ANOMALY,
                timeframe_minutes=0,  # 即時檢測
                price_threshold_percent=5.0,
                volume_multiplier=10.0,
                confirmation_count=1,
                monitoring_interval_seconds=30,
                action_duration_minutes=60
            ),
            # 流動性危機
            CrashDetectionConfig(
                crash_type=CrashType.LIQUIDITY_CRISIS,
                timeframe_minutes=0,  # 即時檢測
                price_threshold_percent=1.0,  # 買賣價差>1%
                confirmation_count=1,
                monitoring_interval_seconds=30,
                action_duration_minutes=30
            )
        ]
        
        # 保存默認配置
        if not self.config_path.exists():
            self._save_detection_configs(default_configs)
        
        return default_configs
    
    def _save_detection_configs(self, configs: List[CrashDetectionConfig]):
        """保存檢測配置"""
        config_data = []
        for config in configs:
            config_data.append({
                "crash_type": config.crash_type.value,
                "timeframe_minutes": config.timeframe_minutes,
                "price_threshold_percent": config.price_threshold_percent,
                "volume_multiplier": config.volume_multiplier,
                "confirmation_count": config.confirmation_count,
                "monitoring_interval_seconds": config.monitoring_interval_seconds,
                "action_duration_minutes": config.action_duration_minutes
            })
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
    
    async def get_market_data(self, symbol: str) -> Optional[MarketData]:
        """獲取市場數據（模擬實現）"""
        try:
            # 實際實現中這裡會連接交易所API
            # 這裡使用模擬數據進行演示
            current_time = datetime.now()
            
            # 模擬價格數據（實際使用中替換為真實API調用）
            import random
            base_price = {
                "XRPUSDT": 0.5,
                "DOGEUSDT": 0.08,
                "BTCUSDT": 45000,
                "ETHUSDT": 2500,
                "BNBUSDT": 300,
                "ADAUSDT": 0.4,
                "SOLUSDT": 100
            }.get(symbol, 1.0)
            
            # 添加隨機波動
            price_variation = random.uniform(-0.02, 0.02)  # ±2%波動
            current_price = base_price * (1 + price_variation)
            
            volume = random.uniform(1000000, 10000000)  # 隨機成交量
            
            return MarketData(
                symbol=symbol,
                timestamp=current_time,
                price=current_price,
                volume=volume,
                high=current_price * 1.01,
                low=current_price * 0.99
            )
        except Exception as e:
            logger.error(f"獲取{symbol}市場數據失敗: {e}")
            return None
    
    def _calculate_price_drop(self, current_price: float, past_price: float) -> float:
        """計算價格跌幅百分比"""
        if past_price <= 0:
            return 0.0
        return ((past_price - current_price) / past_price) * 100
    
    def _calculate_volume_multiplier(self, current_volume: float, historical_volumes: List[float]) -> float:
        """計算成交量倍數"""
        if not historical_volumes:
            return 1.0
        
        avg_volume = sum(historical_volumes) / len(historical_volumes)
        if avg_volume <= 0:
            return 1.0
        
        return current_volume / avg_volume
    
    def _detect_flash_crash(self, symbol: str, config: CrashDetectionConfig) -> Optional[CrashEvent]:
        """檢測閃崩"""
        if symbol not in self.price_history or len(self.price_history[symbol]) < 2:
            return None
        
        current_data = self.price_history[symbol][-1]
        
        # 根據時間框架選擇比較點
        target_time = current_data.timestamp - timedelta(minutes=config.timeframe_minutes)
        past_data = None
        
        for data in reversed(self.price_history[symbol][:-1]):
            if data.timestamp <= target_time:
                past_data = data
                break
        
        if not past_data:
            return None
        
        # 計算跌幅
        drop_percentage = self._calculate_price_drop(current_data.price, past_data.price)
        
        # 檢查是否達到閾值
        if drop_percentage < config.price_threshold_percent:
            return None
        
        # 檢查成交量異常（如果配置了）
        volume_spike = False
        volume_multiplier = 1.0
        
        if config.volume_multiplier and symbol in self.volume_history:
            volume_multiplier = self._calculate_volume_multiplier(
                current_data.volume, 
                self.volume_history[symbol][-30:]  # 使用過去30個數據點計算平均
            )
            volume_spike = volume_multiplier >= config.volume_multiplier
        
        # 確定嚴重程度
        severity = self._determine_severity(drop_percentage, volume_multiplier)
        
        # 生成事件
        event_id = f"crash_{symbol}_{int(time.time())}"
        
        return CrashEvent(
            event_id=event_id,
            symbol=symbol,
            crash_type=config.crash_type,
            severity=severity,
            detection_time=current_data.timestamp,
            price_before=past_data.price,
            price_lowest=current_data.price,
            drop_percentage=drop_percentage,
            volume_spike=volume_spike,
            volume_multiplier=volume_multiplier,
            trigger_conditions={
                "timeframe_minutes": config.timeframe_minutes,
                "threshold_percent": config.price_threshold_percent,
                "actual_drop_percent": drop_percentage,
                "volume_required": config.volume_multiplier,
                "actual_volume_multiplier": volume_multiplier
            },
            system_action=self._determine_system_action(config, severity)
        )
    
    def _determine_severity(self, drop_percentage: float, volume_multiplier: float) -> CrashSeverity:
        """確定崩盤嚴重程度"""
        if drop_percentage >= 30 or volume_multiplier >= 20:
            return CrashSeverity.EXTREME
        elif drop_percentage >= 20 or volume_multiplier >= 10:
            return CrashSeverity.HIGH
        elif drop_percentage >= 10 or volume_multiplier >= 5:
            return CrashSeverity.MEDIUM
        else:
            return CrashSeverity.LOW
    
    def _determine_system_action(self, config: CrashDetectionConfig, severity: CrashSeverity) -> Dict[str, Any]:
        """確定系統採取的行動"""
        base_action = {
            "crash_type": config.crash_type.value,
            "action_duration_minutes": config.action_duration_minutes,
            "timestamp": datetime.now().isoformat()
        }
        
        if config.crash_type == CrashType.FLASH_CRASH_5MIN:
            base_action.update({
                "action": "暫停新交易信號",
                "scope": "single_symbol",
                "risk_level": "moderate"
            })
        elif config.crash_type == CrashType.RAPID_DECLINE_15MIN:
            base_action.update({
                "action": "暫停所有交易",
                "scope": "all_symbols",
                "risk_level": "high"
            })
        elif config.crash_type == CrashType.SUSTAINED_CRASH_1HOUR:
            base_action.update({
                "action": "進入保護模式",
                "scope": "system_wide",
                "risk_level": "high"
            })
        elif config.crash_type == CrashType.EXTREME_CRASH_24HOUR:
            base_action.update({
                "action": "系統緊急停止",
                "scope": "complete_shutdown",
                "risk_level": "extreme"
            })
        
        # 根據嚴重程度調整
        if severity == CrashSeverity.EXTREME:
            base_action["action_duration_minutes"] *= 2
            base_action["additional_measures"] = ["通知管理員", "深度風險評估", "市場結構分析"]
        
        return base_action
    
    async def _apply_protection_measures(self, event: CrashEvent):
        """應用保護措施"""
        try:
            # 檔案鎖定保護
            with open(self.lock_file_path, 'w') as lock_file:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
                
                try:
                    # 設置保護期限
                    protection_end_time = event.detection_time + timedelta(
                        minutes=event.system_action["action_duration_minutes"]
                    )
                    
                    if event.system_action.get("scope") == "single_symbol":
                        self.protected_symbols[event.symbol] = protection_end_time
                    elif event.system_action.get("scope") in ["all_symbols", "system_wide", "complete_shutdown"]:
                        # 保護所有交易對
                        for symbol in self.symbols:
                            self.protected_symbols[symbol] = protection_end_time
                    
                    # 記錄保護措施
                    protection_log = {
                        "event_id": event.event_id,
                        "symbol": event.symbol,
                        "protection_start": event.detection_time.isoformat(),
                        "protection_end": protection_end_time.isoformat(),
                        "action": event.system_action,
                        "severity": event.severity.value
                    }
                    
                    # 保存保護記錄
                    await self._save_protection_log(protection_log)
                    
                    logger.warning(f"🚨 崩盤檢測觸發保護措施: {event.symbol} {event.crash_type.value}")
                    logger.warning(f"   跌幅: {event.drop_percentage:.2f}%")
                    logger.warning(f"   行動: {event.system_action['action']}")
                    logger.warning(f"   持續時間: {event.system_action['action_duration_minutes']}分鐘")
                    
                finally:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                    
        except Exception as e:
            logger.error(f"應用保護措施失敗: {e}")
    
    async def _save_protection_log(self, log_data: Dict[str, Any]):
        """保存保護記錄"""
        log_file = self.base_dir / "data" / "logs" / "crash_protection.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"保存保護記錄失敗: {e}")
    
    def is_symbol_protected(self, symbol: str) -> bool:
        """檢查交易對是否處於保護狀態"""
        if symbol not in self.protected_symbols:
            return False
        
        current_time = datetime.now()
        if current_time >= self.protected_symbols[symbol]:
            # 保護期已過，移除保護
            del self.protected_symbols[symbol]
            return False
        
        return True
    
    async def update_market_data(self, symbol: str):
        """更新市場數據"""
        market_data = await self.get_market_data(symbol)
        if not market_data:
            return
        
        # 更新價格歷史
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append(market_data)
        
        # 保持最近1000個數據點
        if len(self.price_history[symbol]) > 1000:
            self.price_history[symbol] = self.price_history[symbol][-1000:]
        
        # 更新成交量歷史
        if symbol not in self.volume_history:
            self.volume_history[symbol] = []
        
        self.volume_history[symbol].append(market_data.volume)
        
        # 保持最近100個成交量數據點
        if len(self.volume_history[symbol]) > 100:
            self.volume_history[symbol] = self.volume_history[symbol][-100:]
    
    async def detect_crashes(self) -> List[CrashEvent]:
        """執行崩盤檢測"""
        detected_events = []
        
        for symbol in self.symbols:
            # 跳過已受保護的交易對
            if self.is_symbol_protected(symbol):
                continue
            
            # 更新市場數據
            await self.update_market_data(symbol)
            
            # 對每種檢測配置進行檢查
            for config in self.detection_configs:
                event = self._detect_flash_crash(symbol, config)
                if event:
                    detected_events.append(event)
                    self.crash_events.append(event)
                    
                    # 應用保護措施
                    await self._apply_protection_measures(event)
        
        return detected_events
    
    async def start_monitoring(self):
        """開始監控"""
        if self.is_monitoring:
            logger.warning("崩盤檢測器已在運行中")
            return
        
        self.is_monitoring = True
        logger.info("🚀 啟動閃崩檢測系統")
        logger.info(f"   監控交易對: {', '.join(self.symbols)}")
        logger.info(f"   檢測機制: {len(self.detection_configs)}種")
        
        try:
            while self.is_monitoring:
                # 執行檢測
                events = await self.detect_crashes()
                
                if events:
                    logger.warning(f"檢測到 {len(events)} 個崩盤事件")
                
                # 等待下次檢測
                await asyncio.sleep(30)  # 每30秒檢測一次
                
        except Exception as e:
            logger.error(f"監控過程發生錯誤: {e}")
        finally:
            self.is_monitoring = False
    
    def stop_monitoring(self):
        """停止監控"""
        if self.is_monitoring:
            self.is_monitoring = False
            logger.info("🛑 停止閃崩檢測系統")
    
    def get_protection_status(self) -> Dict[str, Any]:
        """獲取保護狀態"""
        current_time = datetime.now()
        
        status = {
            "monitoring_active": self.is_monitoring,
            "protected_symbols": {},
            "recent_events": len([e for e in self.crash_events if (current_time - e.detection_time).total_seconds() < 3600]),
            "total_events": len(self.crash_events)
        }
        
        for symbol, end_time in self.protected_symbols.items():
            remaining_minutes = (end_time - current_time).total_seconds() / 60
            if remaining_minutes > 0:
                status["protected_symbols"][symbol] = {
                    "protection_end": end_time.isoformat(),
                    "remaining_minutes": round(remaining_minutes, 1)
                }
        
        return status

# 全域崩盤檢測器實例
crash_detector = CrashDetector()

async def main():
    """測試函數"""
    logger.info("測試閃崩檢測系統")
    
    # 測試獲取市場數據
    for symbol in crash_detector.symbols:
        data = await crash_detector.get_market_data(symbol)
        if data:
            logger.info(f"{symbol}: {data.price:.6f} USDT, 成交量: {data.volume:.0f}")
    
    # 測試保護狀態
    status = crash_detector.get_protection_status()
    logger.info(f"保護狀態: {json.dumps(status, ensure_ascii=False, indent=2)}")
    
    logger.info("閃崩檢測系統測試完成")

if __name__ == "__main__":
    asyncio.run(main())
