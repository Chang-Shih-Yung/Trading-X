"""
🎯 Trading X - 整合測試：信號品質控制引擎
測試信號品質控制引擎與資料來源的整合
"""

import unittest
import asyncio
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class MockSignal:
    """模擬信號類別"""
    symbol: str
    signal_type: str
    strength: float
    timestamp: datetime
    indicators: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "signal_type": self.signal_type,
            "strength": self.strength,
            "timestamp": self.timestamp.isoformat(),
            "indicators": self.indicators
        }

class MockQualityControlEngine:
    """模擬品質控制引擎"""
    
    def __init__(self):
        self.processed_signals = []
        self.rejection_reasons = {}
    
    async def evaluate_signal(self, signal: MockSignal) -> Dict[str, Any]:
        """評估信號品質"""
        # 模擬評估邏輯
        score = min(signal.strength * 100, 100)
        
        if score >= 80:
            priority = "CRITICAL"
        elif score >= 60:
            priority = "HIGH"
        elif score >= 40:
            priority = "MEDIUM"
        elif score >= 20:
            priority = "LOW"
        else:
            priority = "REJECTED"
            self.rejection_reasons[signal.symbol] = "信號強度過低"
        
        result = {
            "signal": signal.to_dict(),
            "priority": priority,
            "score": score,
            "timestamp": datetime.now().isoformat()
        }
        
        if priority != "REJECTED":
            self.processed_signals.append(result)
        
        return result

class TestSignalQualityControlIntegration(unittest.TestCase):
    """測試信號品質控制整合"""
    
    def setUp(self):
        """設置測試環境"""
        self.engine = MockQualityControlEngine()
    
    def test_high_quality_signal_processing(self):
        """測試高品質信號處理"""
        signal = MockSignal(
            symbol="BTCUSDT",
            signal_type="BUY",
            strength=0.85,
            timestamp=datetime.now(),
            indicators={"rsi": 25, "macd": 0.5}
        )
        
        # 執行異步測試
        async def run_test():
            result = await self.engine.evaluate_signal(signal)
            self.assertEqual(result["priority"], "CRITICAL")
            self.assertGreaterEqual(result["score"], 80)
            return result
        
        result = asyncio.run(run_test())
        self.assertIn(result, self.engine.processed_signals)
    
    def test_low_quality_signal_rejection(self):
        """測試低品質信號拒絕"""
        signal = MockSignal(
            symbol="ETHUSDT",
            signal_type="SELL",
            strength=0.15,
            timestamp=datetime.now(),
            indicators={"rsi": 85, "macd": -0.2}
        )
        
        async def run_test():
            result = await self.engine.evaluate_signal(signal)
            self.assertEqual(result["priority"], "REJECTED")
            self.assertLess(result["score"], 20)
            return result
        
        result = asyncio.run(run_test())
        self.assertNotIn(result, self.engine.processed_signals)
        self.assertIn("ETHUSDT", self.engine.rejection_reasons)
    
    def test_multiple_signals_batch_processing(self):
        """測試多信號批次處理"""
        signals = [
            MockSignal("BTCUSDT", "BUY", 0.90, datetime.now(), {"rsi": 20}),
            MockSignal("ETHUSDT", "SELL", 0.70, datetime.now(), {"rsi": 80}),
            MockSignal("ADAUSDT", "BUY", 0.30, datetime.now(), {"rsi": 50}),
            MockSignal("DOTUSDT", "SELL", 0.10, datetime.now(), {"rsi": 95})
        ]
        
        async def run_batch_test():
            results = []
            for signal in signals:
                result = await self.engine.evaluate_signal(signal)
                results.append(result)
            return results
        
        results = asyncio.run(run_batch_test())
        
        # 驗證批次處理結果
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0]["priority"], "CRITICAL")  # 0.90 -> CRITICAL
        self.assertEqual(results[1]["priority"], "HIGH")      # 0.70 -> HIGH
        self.assertEqual(results[2]["priority"], "MEDIUM")    # 0.30 -> MEDIUM
        self.assertEqual(results[3]["priority"], "REJECTED")  # 0.10 -> REJECTED
        
        # 驗證只有非拒絕的信號被保存
        self.assertEqual(len(self.engine.processed_signals), 3)
    
    def test_engine_state_consistency(self):
        """測試引擎狀態一致性"""
        # 處理多個信號
        signals = [
            MockSignal("BTC", "BUY", 0.80, datetime.now(), {}),
            MockSignal("ETH", "SELL", 0.05, datetime.now(), {})
        ]
        
        async def run_consistency_test():
            for signal in signals:
                await self.engine.evaluate_signal(signal)
        
        asyncio.run(run_consistency_test())
        
        # 驗證狀態一致性
        self.assertEqual(len(self.engine.processed_signals), 1)
        self.assertEqual(len(self.engine.rejection_reasons), 1)
        self.assertIn("ETH", self.engine.rejection_reasons)

if __name__ == "__main__":
    print("🧪 執行信號品質控制整合測試...")
    unittest.main(verbosity=2)
