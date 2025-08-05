#!/usr/bin/env python3
"""
🛡️ 價格邏輯驗證器
確保所有交易信號的止損止盈邏輯正確，拒絕任何邏輯錯誤的信號
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class SignalType(Enum):
    BUY = "BUY"
    STRONG_BUY = "STRONG_BUY"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"
    HOLD = "HOLD"

@dataclass
class PriceValidationResult:
    """價格驗證結果"""
    is_valid: bool
    error_message: str = ""
    risk_reward_ratio: float = 0.0
    warnings: list = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []

class PriceLogicValidator:
    """價格邏輯驗證器"""
    
    def __init__(self, min_risk_reward_ratio: float = 1.5):
        self.min_risk_reward_ratio = min_risk_reward_ratio
        self.validation_count = 0
        self.error_count = 0
    
    def validate_trading_signal(
        self, 
        signal_type: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        symbol: str = "UNKNOWN"
    ) -> PriceValidationResult:
        """
        驗證交易信號的價格邏輯
        
        Args:
            signal_type: 信號類型 (BUY, SELL, etc.)
            entry_price: 進場價格
            stop_loss: 止損價格  
            take_profit: 止盈價格
            symbol: 交易對名稱
            
        Returns:
            PriceValidationResult: 驗證結果
        """
        self.validation_count += 1
        
        try:
            # 🚫 基礎數據驗證 - 拒絕無效數據
            if not all(isinstance(price, (int, float)) for price in [entry_price, stop_loss, take_profit]):
                self.error_count += 1
                return PriceValidationResult(
                    is_valid=False,
                    error_message=f"❌ {symbol} 價格數據類型無效: 進場={type(entry_price)}, 止損={type(stop_loss)}, 止盈={type(take_profit)}"
                )
            
            if any(price <= 0 for price in [entry_price, stop_loss, take_profit]):
                self.error_count += 1
                return PriceValidationResult(
                    is_valid=False,
                    error_message=f"❌ {symbol} 價格必須為正數: 進場={entry_price}, 止損={stop_loss}, 止盈={take_profit}"
                )
            
            # 🎯 做多邏輯驗證
            if signal_type in [SignalType.BUY.value, SignalType.STRONG_BUY.value]:
                if not (stop_loss < entry_price < take_profit):
                    self.error_count += 1
                    return PriceValidationResult(
                        is_valid=False,
                        error_message=f"❌ {symbol} 做多邏輯錯誤: 止損({stop_loss:.6f}) < 進場({entry_price:.6f}) < 止盈({take_profit:.6f}) 不成立"
                    )
            
            # 🎯 做空邏輯驗證
            elif signal_type in [SignalType.SELL.value, SignalType.STRONG_SELL.value]:
                if not (take_profit < entry_price < stop_loss):
                    self.error_count += 1
                    return PriceValidationResult(
                        is_valid=False,
                        error_message=f"❌ {symbol} 做空邏輯錯誤: 止盈({take_profit:.6f}) < 進場({entry_price:.6f}) < 止損({stop_loss:.6f}) 不成立"
                    )
            
            else:
                # HOLD或其他類型，不強制驗證邏輯
                logger.warning(f"⚠️ {symbol} 未知信號類型: {signal_type}，跳過邏輯驗證")
            
            # 🎯 風險回報比驗證
            risk_amount = abs(entry_price - stop_loss)
            reward_amount = abs(take_profit - entry_price)
            
            if risk_amount == 0:
                self.error_count += 1
                return PriceValidationResult(
                    is_valid=False,
                    error_message=f"❌ {symbol} 風險金額為零: 進場價等於止損價"
                )
            
            risk_reward_ratio = reward_amount / risk_amount
            
            warnings = []
            if risk_reward_ratio < self.min_risk_reward_ratio:
                warnings.append(f"⚠️ 風險回報比過低: {risk_reward_ratio:.2f} < {self.min_risk_reward_ratio}")
            
            # 🎯 價格合理性檢查
            max_risk_pct = (risk_amount / entry_price) * 100
            max_reward_pct = (reward_amount / entry_price) * 100
            
            if max_risk_pct > 10:  # 風險超過10%
                warnings.append(f"⚠️ 風險過高: {max_risk_pct:.2f}%")
            
            if max_reward_pct > 50:  # 收益目標超過50%
                warnings.append(f"⚠️ 收益目標過高: {max_reward_pct:.2f}%")
            
            logger.info(f"✅ {symbol} 價格邏輯驗證通過: {signal_type}, 風險回報比={risk_reward_ratio:.2f}")
            
            return PriceValidationResult(
                is_valid=True,
                risk_reward_ratio=risk_reward_ratio,
                warnings=warnings
            )
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"❌ {symbol} 價格邏輯驗證異常: {e}")
            return PriceValidationResult(
                is_valid=False,
                error_message=f"❌ 驗證過程異常: {str(e)}"
            )
    
    def validate_signal_dict(self, signal: Dict[str, Any]) -> PriceValidationResult:
        """驗證信號字典格式的數據"""
        try:
            return self.validate_trading_signal(
                signal_type=signal.get('signal_type', 'UNKNOWN'),
                entry_price=float(signal.get('entry_price', 0)),
                stop_loss=float(signal.get('stop_loss', 0)),
                take_profit=float(signal.get('take_profit', 0)),
                symbol=signal.get('symbol', 'UNKNOWN')
            )
        except (ValueError, TypeError) as e:
            return PriceValidationResult(
                is_valid=False,
                error_message=f"❌ 信號數據格式錯誤: {e}"
            )
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """獲取驗證統計"""
        success_rate = ((self.validation_count - self.error_count) / self.validation_count * 100) if self.validation_count > 0 else 0
        
        return {
            'total_validations': self.validation_count,
            'error_count': self.error_count,
            'success_count': self.validation_count - self.error_count,
            'success_rate': round(success_rate, 2),
            'min_risk_reward_ratio': self.min_risk_reward_ratio
        }

# 全局驗證器實例
price_validator = PriceLogicValidator(min_risk_reward_ratio=1.5)

def validate_signal_prices(signal: Dict[str, Any]) -> PriceValidationResult:
    """快速驗證信號價格的全局函數"""
    return price_validator.validate_signal_dict(signal)

if __name__ == "__main__":
    # 測試案例
    validator = PriceLogicValidator()
    
    # 測試做多信號
    test_buy = {
        'signal_type': 'BUY',
        'entry_price': 100.0,
        'stop_loss': 95.0,    # 5% 風險
        'take_profit': 110.0, # 10% 收益
        'symbol': 'BTCUSDT'
    }
    
    result = validator.validate_signal_dict(test_buy)
    print(f"做多測試: {result}")
    
    # 測試做空信號
    test_sell = {
        'signal_type': 'SELL',
        'entry_price': 100.0,
        'stop_loss': 105.0,   # 5% 風險
        'take_profit': 90.0,  # 10% 收益
        'symbol': 'ETHUSDT'
    }
    
    result = validator.validate_signal_dict(test_sell)
    print(f"做空測試: {result}")
    
    # 測試錯誤案例
    test_error = {
        'signal_type': 'BUY',
        'entry_price': 100.0,
        'stop_loss': 110.0,   # ❌ 錯誤：做多止損高於進場價
        'take_profit': 90.0,  # ❌ 錯誤：做多止盈低於進場價
        'symbol': 'ERROR_TEST'
    }
    
    result = validator.validate_signal_dict(test_error)
    print(f"錯誤測試: {result}")
    
    print(f"驗證統計: {validator.get_validation_stats()}")
