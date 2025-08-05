"""
🎯 Trading X - 流程測試：完整業務流程
測試從數據獲取到信號生成的完整業務流程
"""

import unittest
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any

class MockDataSource:
    """模擬數據來源"""
    
    def __init__(self):
        self.is_connected = False
    
    async def connect(self) -> bool:
        """連接數據源"""
        await asyncio.sleep(0.1)  # 模擬網路延遲
        self.is_connected = True
        return True
    
    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """獲取市場數據"""
        if not self.is_connected:
            raise ConnectionError("數據源未連接")
        
        # 模擬市場數據
        return {
            "symbol": symbol,
            "price": 45000.0,
            "volume": 1000000,
            "timestamp": datetime.now().isoformat(),
            "indicators": {
                "rsi": 30,
                "macd": 0.5,
                "bb_upper": 46000,
                "bb_lower": 44000
            }
        }

class MockSignalGenerator:
    """模擬信號生成器"""
    
    def __init__(self):
        self.total_generated = 0
    
    async def generate_signal(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成交易信號"""
        indicators = market_data["indicators"]
        
        # 簡化的信號生成邏輯
        if indicators["rsi"] < 30:
            signal_type = "BUY"
            strength = 0.8
        elif indicators["rsi"] > 70:
            signal_type = "SELL"
            strength = 0.7
        else:
            signal_type = "HOLD"
            strength = 0.3
        
        self.total_generated += 1
        
        return {
            "symbol": market_data["symbol"],
            "signal_type": signal_type,
            "strength": strength,
            "timestamp": datetime.now().isoformat(),
            "market_data": market_data
        }

class MockNotificationService:
    """模擬通知服務"""
    
    def __init__(self):
        self.sent_notifications = []
    
    async def send_notification(self, signal: Dict[str, Any]) -> bool:
        """發送通知"""
        notification = {
            "signal": signal,
            "sent_at": datetime.now().isoformat(),
            "status": "sent"
        }
        self.sent_notifications.append(notification)
        return True

class BusinessFlowOrchestrator:
    """業務流程編排器"""
    
    def __init__(self):
        self.data_source = MockDataSource()
        self.signal_generator = MockSignalGenerator()
        self.notification_service = MockNotificationService()
        self.processed_symbols = []
        self.errors = []
    
    async def initialize(self) -> bool:
        """初始化系統"""
        try:
            await self.data_source.connect()
            return True
        except Exception as e:
            self.errors.append(f"初始化失敗: {str(e)}")
            return False
    
    async def process_symbol(self, symbol: str) -> Dict[str, Any]:
        """處理單個交易對"""
        try:
            # 1. 獲取市場數據
            market_data = await self.data_source.get_market_data(symbol)
            
            # 2. 生成信號
            signal = await self.signal_generator.generate_signal(market_data)
            
            # 3. 發送通知（僅強信號）
            if signal["strength"] >= 0.7:
                await self.notification_service.send_notification(signal)
            
            self.processed_symbols.append(symbol)
            
            return {
                "symbol": symbol,
                "status": "success",
                "signal": signal,
                "processed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"處理 {symbol} 時發生錯誤: {str(e)}"
            self.errors.append(error_msg)
            return {
                "symbol": symbol,
                "status": "error",
                "error": error_msg,
                "processed_at": datetime.now().isoformat()
            }
    
    async def process_multiple_symbols(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """批次處理多個交易對"""
        results = []
        for symbol in symbols:
            result = await self.process_symbol(symbol)
            results.append(result)
        return results

class TestCompleteBusinessFlow(unittest.TestCase):
    """測試完整業務流程"""
    
    def setUp(self):
        """設置測試環境"""
        self.orchestrator = BusinessFlowOrchestrator()
    
    def test_system_initialization(self):
        """測試系統初始化"""
        async def run_test():
            result = await self.orchestrator.initialize()
            self.assertTrue(result)
            self.assertTrue(self.orchestrator.data_source.is_connected)
        
        asyncio.run(run_test())
    
    def test_single_symbol_processing(self):
        """測試單個交易對處理"""
        async def run_test():
            await self.orchestrator.initialize()
            result = await self.orchestrator.process_symbol("BTCUSDT")
            
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["symbol"], "BTCUSDT")
            self.assertIn("signal", result)
            self.assertIn("BTCUSDT", self.orchestrator.processed_symbols)
        
        asyncio.run(run_test())
    
    def test_multiple_symbols_batch_processing(self):
        """測試多交易對批次處理"""
        symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT"]
        
        async def run_test():
            await self.orchestrator.initialize()
            results = await self.orchestrator.process_multiple_symbols(symbols)
            
            self.assertEqual(len(results), 4)
            
            # 驗證所有結果
            for i, result in enumerate(results):
                self.assertEqual(result["symbol"], symbols[i])
                self.assertEqual(result["status"], "success")
                self.assertIn("signal", result)
            
            # 驗證處理記錄
            self.assertEqual(len(self.orchestrator.processed_symbols), 4)
            self.assertEqual(set(self.orchestrator.processed_symbols), set(symbols))
        
        asyncio.run(run_test())
    
    def test_notification_flow(self):
        """測試通知流程"""
        async def run_test():
            await self.orchestrator.initialize()
            await self.orchestrator.process_symbol("BTCUSDT")
            
            # 檢查是否有通知發送（基於信號強度）
            notifications = self.orchestrator.notification_service.sent_notifications
            
            if len(notifications) > 0:
                notification = notifications[0]
                self.assertIn("signal", notification)
                self.assertIn("sent_at", notification)
                self.assertEqual(notification["status"], "sent")
        
        asyncio.run(run_test())
    
    def test_error_handling(self):
        """測試錯誤處理"""
        async def run_test():
            # 不初始化系統，直接處理交易對（應該產生錯誤）
            result = await self.orchestrator.process_symbol("BTCUSDT")
            
            self.assertEqual(result["status"], "error")
            self.assertIn("error", result)
            self.assertGreater(len(self.orchestrator.errors), 0)
        
        asyncio.run(run_test())
    
    def test_end_to_end_performance(self):
        """測試端到端性能"""
        async def run_test():
            start_time = datetime.now()
            
            await self.orchestrator.initialize()
            symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
            results = await self.orchestrator.process_multiple_symbols(symbols)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # 驗證處理時間合理（應該在幾秒內完成）
            self.assertLess(processing_time, 5.0)
            
            # 驗證所有信號生成
            self.assertEqual(len(results), 3)
            self.assertEqual(self.orchestrator.signal_generator.total_generated, 3)
            
            return processing_time
        
        processing_time = asyncio.run(run_test())
        print(f"📊 端到端處理時間: {processing_time:.3f} 秒")

if __name__ == "__main__":
    print("🧪 執行完整業務流程測試...")
    unittest.main(verbosity=2)
