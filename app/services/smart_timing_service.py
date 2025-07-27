"""
智能時間區間計算服務
根據多維度因素動態計算信號有效期
"""

import json
import os
from datetime import datetime, time
from typing import Dict, Any, Optional
import pandas as pd
from app.core.config import settings

class SmartTimingService:
    """智能時間區間計算服務"""
    
    def __init__(self):
        self.config = self._load_config()
        self.settings = settings
        
    def _load_config(self) -> Dict[str, Any]:
        """載入智能時間配置"""
        config_path = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "config", 
            "smart_timing_config.json"
        )
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # 如果配置文件不存在，返回預設配置
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """獲取預設配置"""
        return {
            "smart_timing": {
                "enable_smart_expiry": True,
                "base_timeframes": {"1m": 4, "3m": 8, "5m": 12, "15m": 20, "30m": 35},
                "signal_strength_multipliers": {
                    "very_strong": 0.6, "strong": 0.75, "medium": 1.0, 
                    "weak": 1.3, "very_weak": 1.6
                },
                "volatility_adjustments": {
                    "very_high": 0.5, "high": 0.7, "medium": 1.0,
                    "low": 1.3, "very_low": 1.6
                },
                "limits": {"min_minutes": 2, "max_minutes": 60}
            }
        }
    
    def calculate_smart_expiry_minutes(
        self,
        base_timeframe: str,
        signal_strength: float,
        signal_type: str,
        volatility_data: Optional[pd.Series] = None,
        confirmation_count: int = 1,
        current_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        智能計算信號有效期
        
        Args:
            base_timeframe: 基礎時間框架 (1m, 3m, 5m, 15m, 30m)
            signal_strength: 信號強度 (0.0-1.0)
            signal_type: 信號類型
            volatility_data: 波動率數據
            confirmation_count: 確認次數
            current_time: 當前時間
            
        Returns:
            包含計算結果的字典
        """
        if not self.config["smart_timing"]["enable_smart_expiry"]:
            # 如果未啟用智能計算，使用原有邏輯
            return self._get_legacy_expiry(base_timeframe)
        
        try:
            # 1. 基礎時間
            base_minutes = self._get_base_minutes(base_timeframe)
            
            # 2. 信號強度調整
            strength_multiplier = self._get_strength_multiplier(signal_strength)
            
            # 3. 波動率調整
            volatility_multiplier = self._get_volatility_multiplier(volatility_data)
            
            # 4. 信號類型調整
            type_multiplier = self._get_signal_type_multiplier(signal_type)
            
            # 5. 市場時段調整
            session_multiplier = self._get_market_session_multiplier(current_time)
            
            # 6. 確認次數調整
            confirmation_multiplier = self._get_confirmation_multiplier(confirmation_count)
            
            # 7. 計算最終時間
            calculated_minutes = (
                base_minutes * 
                strength_multiplier * 
                volatility_multiplier * 
                type_multiplier * 
                session_multiplier * 
                confirmation_multiplier
            )
            
            # 8. 應用限制
            final_minutes = self._apply_limits(calculated_minutes)
            
            return {
                "expiry_minutes": int(final_minutes),
                "calculation_details": {
                    "base_minutes": base_minutes,
                    "strength_multiplier": strength_multiplier,
                    "volatility_multiplier": volatility_multiplier,
                    "type_multiplier": type_multiplier,
                    "session_multiplier": session_multiplier,
                    "confirmation_multiplier": confirmation_multiplier,
                    "calculated_minutes": calculated_minutes,
                    "final_minutes": final_minutes
                },
                "reasoning": self._generate_reasoning(
                    base_timeframe, signal_strength, signal_type, 
                    volatility_multiplier, session_multiplier
                )
            }
            
        except Exception as e:
            # 出錯時使用預設值
            return self._get_fallback_expiry(base_timeframe, str(e))
    
    def _get_base_minutes(self, timeframe: str) -> int:
        """獲取基礎時間"""
        base_timeframes = self.config["smart_timing"]["base_timeframes"]
        return base_timeframes.get(timeframe, 12)
    
    def _get_strength_multiplier(self, signal_strength: float) -> float:
        """根據信號強度獲取倍數"""
        multipliers = self.config["smart_timing"]["signal_strength_multipliers"]
        thresholds = self.config["smart_timing"].get("signal_strength_thresholds", {
            "very_strong": 0.9, "strong": 0.75, "medium": 0.6, "weak": 0.4
        })
        
        if signal_strength >= thresholds["very_strong"]:
            return multipliers["very_strong"]
        elif signal_strength >= thresholds["strong"]:
            return multipliers["strong"]
        elif signal_strength >= thresholds["medium"]:
            return multipliers["medium"]
        elif signal_strength >= thresholds["weak"]:
            return multipliers["weak"]
        else:
            return multipliers["very_weak"]
    
    def _get_volatility_multiplier(self, volatility_data: Optional[pd.Series]) -> float:
        """根據波動率獲取倍數"""
        if volatility_data is None or len(volatility_data) == 0:
            return 1.0
        
        try:
            # 計算ATR百分比
            atr_pct = volatility_data.iloc[-1] * 100  # 轉換為百分比
            
            adjustments = self.config["smart_timing"]["volatility_adjustments"]
            thresholds = self.config["smart_timing"].get("volatility_thresholds", {
                "very_high": 3.0, "high": 2.0, "medium": 1.0, "low": 0.5
            })
            
            if atr_pct >= thresholds["very_high"]:
                return adjustments["very_high"]
            elif atr_pct >= thresholds["high"]:
                return adjustments["high"]
            elif atr_pct >= thresholds["medium"]:
                return adjustments["medium"]
            elif atr_pct >= thresholds["low"]:
                return adjustments["low"]
            else:
                return adjustments["very_low"]
                
        except Exception:
            return 1.0
    
    def _get_signal_type_multiplier(self, signal_type: str) -> float:
        """根據信號類型獲取倍數"""
        multipliers = self.config["smart_timing"]["signal_type_multipliers"]
        return multipliers.get(signal_type, 1.0)
    
    def _get_market_session_multiplier(self, current_time: Optional[datetime]) -> float:
        """根據市場時段獲取倍數"""
        if current_time is None:
            current_time = datetime.now()
        
        # 轉換為台北時間的小時
        hour = current_time.hour
        
        adjustments = self.config["smart_timing"]["market_session_adjustments"]
        
        # 判斷市場時段
        if 8 <= hour < 12:
            return adjustments.get("asia_morning", 1.2)
        elif 12 <= hour < 15:
            return adjustments.get("asia_afternoon", 1.1)
        elif 15 <= hour < 17:
            return adjustments.get("europe_opening", 0.8)
        elif 17 <= hour < 21:
            return adjustments.get("europe_session", 0.9)
        elif 21 <= hour < 23:
            return adjustments.get("us_opening", 0.6)
        elif 23 <= hour or hour < 2:
            return adjustments.get("us_session", 0.7)
        else:
            return adjustments.get("overnight", 1.5)
    
    def _get_confirmation_multiplier(self, confirmation_count: int) -> float:
        """根據確認次數獲取倍數"""
        multipliers = self.config["smart_timing"]["confirmation_multipliers"]
        
        if confirmation_count >= 4:
            return multipliers["cross_timeframe"]
        elif confirmation_count == 3:
            return multipliers["triple_confirmation"]
        elif confirmation_count == 2:
            return multipliers["dual_confirmation"]
        else:
            return multipliers["single_timeframe"]
    
    def _apply_limits(self, calculated_minutes: float) -> float:
        """應用時間限制"""
        limits = self.config["smart_timing"]["limits"]
        min_minutes = limits.get("min_minutes", 2)
        max_minutes = limits.get("max_minutes", 60)
        
        return max(min_minutes, min(max_minutes, calculated_minutes))
    
    def _generate_reasoning(
        self, 
        timeframe: str, 
        strength: float, 
        signal_type: str,
        volatility_mult: float,
        session_mult: float
    ) -> str:
        """生成時間計算的推理說明"""
        reasons = []
        
        # 基礎時間框架
        reasons.append(f"基於{timeframe}時間框架")
        
        # 信號強度
        if strength >= 0.9:
            reasons.append("極強信號，縮短執行時間")
        elif strength >= 0.75:
            reasons.append("強信號，適度縮短時間")
        elif strength < 0.6:
            reasons.append("弱信號，延長觀察時間")
        
        # 波動率
        if volatility_mult < 0.8:
            reasons.append("高波動環境，加快執行")
        elif volatility_mult > 1.2:
            reasons.append("低波動環境，延長等待")
        
        # 市場時段
        if session_mult < 0.8:
            reasons.append("活躍交易時段，快速執行")
        elif session_mult > 1.2:
            reasons.append("低活躍時段，延長有效期")
        
        # 信號類型
        if "BREAKOUT" in signal_type:
            reasons.append("突破信號需快速確認")
        elif "REVERSAL" in signal_type:
            reasons.append("反轉信號需更多確認時間")
        
        return "；".join(reasons)
    
    def _get_legacy_expiry(self, timeframe: str) -> Dict[str, Any]:
        """獲取傳統的固定有效期"""
        legacy_map = {'1m': 5, '3m': 10, '5m': 15, '15m': 30, '30m': 60}
        minutes = legacy_map.get(timeframe, 15)
        
        return {
            "expiry_minutes": minutes,
            "calculation_details": {"legacy_mode": True},
            "reasoning": f"使用傳統固定時間：{timeframe} → {minutes}分鐘"
        }
    
    def _get_fallback_expiry(self, timeframe: str, error: str) -> Dict[str, Any]:
        """錯誤時的備用有效期"""
        fallback_minutes = 12  # 安全的預設值
        
        return {
            "expiry_minutes": fallback_minutes,
            "calculation_details": {"error": error, "fallback_mode": True},
            "reasoning": f"計算出錯，使用安全預設值：{fallback_minutes}分鐘"
        }

# 全局實例
smart_timing_service = SmartTimingService()
