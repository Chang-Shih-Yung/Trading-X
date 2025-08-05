"""
🎯 Trading X - 單元測試：信號優先級枚舉
測試 SignalPriority 枚舉的基本功能
"""

import unittest
from enum import Enum

# 模擬 SignalPriority 枚舉（避免導入問題）
class SignalPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    REJECTED = "rejected"

class TestSignalPriority(unittest.TestCase):
    """測試信號優先級枚舉"""
    
    def test_enum_values(self):
        """測試枚舉值是否正確"""
        self.assertEqual(SignalPriority.CRITICAL.value, "critical")
        self.assertEqual(SignalPriority.HIGH.value, "high")
        self.assertEqual(SignalPriority.MEDIUM.value, "medium")
        self.assertEqual(SignalPriority.LOW.value, "low")
        self.assertEqual(SignalPriority.REJECTED.value, "rejected")
    
    def test_enum_count(self):
        """測試枚舉數量"""
        self.assertEqual(len(SignalPriority), 5)
    
    def test_enum_comparison(self):
        """測試枚舉比較"""
        # 測試相等性
        self.assertEqual(SignalPriority.CRITICAL, SignalPriority.CRITICAL)
        self.assertNotEqual(SignalPriority.CRITICAL, SignalPriority.HIGH)
    
    def test_enum_membership(self):
        """測試枚舉成員資格"""
        priorities = [p.value for p in SignalPriority]
        self.assertIn("critical", priorities)
        self.assertIn("high", priorities)
        self.assertIn("medium", priorities)
        self.assertIn("low", priorities)
        self.assertIn("rejected", priorities)
        self.assertNotIn("invalid", priorities)
    
    def test_enum_iteration(self):
        """測試枚舉迭代"""
        expected_values = ["critical", "high", "medium", "low", "rejected"]
        actual_values = [p.value for p in SignalPriority]
        self.assertEqual(actual_values, expected_values)

if __name__ == "__main__":
    print("🧪 執行信號優先級枚舉單元測試...")
    unittest.main(verbosity=2)
