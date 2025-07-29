"""
Trading-X 市場條件配置系統測試
驗證配置加載器和市場分析功能
"""

import unittest
import json
import tempfile
import os
from typing import Dict

from market_config_loader import (
    MarketConditionConfig, MarketCondition, StrategyType, 
    ConfidenceLevel, IndicatorCondition, StrategyConfig, AssetParameters
)


class TestMarketConditionConfig(unittest.TestCase):
    """市場條件配置測試類"""
    
    def setUp(self):
        """測試前置設置"""
        # 創建測試配置
        self.test_config = {
            "version": "1.0.0",
            "description": "Test Config",
            "assets": {
                "major": ["BTC", "ETH"],
                "all": ["BTC", "ETH", "SOL"]
            },
            "timeframes": {
                "short_term": ["1m", "5m"],
                "mid_term": ["1h", "4h"]
            },
            "market_conditions": {
                "bull": {
                    "description": "Test bull market",
                    "conditions": {
                        "technical_indicators": {
                            "RSI_14": {
                                "min": 60,
                                "max": 80,
                                "weight": 1.5,
                                "description": "RSI in strong zone"
                            },
                            "MA200_slope": {
                                "threshold": 0.02,
                                "weight": 2.0,
                                "description": "200MA upward trend"
                            }
                        }
                    },
                    "total_score_threshold": 6.0,
                    "confidence_levels": {
                        "high": {"min_score": 8.0},
                        "medium": {"min_score": 6.0},
                        "low": {"min_score": 3.0}
                    },
                    "strategies": {
                        "short_term": {
                            "name": "Bull Short Strategy",
                            "timeframe": "1h",
                            "entry": {"conditions": "RSI > 50"},
                            "exit": {"conditions": "RSI > 80"},
                            "stop_loss": "-3%",
                            "indicators": ["RSI_1H", "MACD_1H"]
                        }
                    }
                }
            },
            "custom_parameters": {
                "BTC": {
                    "volatility_factor": 1.0,
                    "entry_padding": 1.0,
                    "stop_loss_multiplier": 1.0,
                    "market_cap_rank": 1
                }
            },
            "risk_management": {
                "position_sizing": {
                    "conservative": {"max_per_trade": 0.02},
                    "moderate": {"max_per_trade": 0.05}
                }
            }
        }
        
        # 創建臨時配置文件
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(self.test_config, self.temp_file, indent=2)
        self.temp_file.close()
        
        # 創建配置管理器
        self.config_manager = MarketConditionConfig(self.temp_file.name)
    
    def tearDown(self):
        """測試後清理"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_config_loading(self):
        """測試配置加載"""
        self.assertEqual(self.config_manager.config["version"], "1.0.0")
        self.assertEqual(self.config_manager.config["description"], "Test Config")
    
    def test_get_assets(self):
        """測試獲取資產列表"""
        major_assets = self.config_manager.get_assets("major")
        all_assets = self.config_manager.get_assets("all")
        
        self.assertEqual(major_assets, ["BTC", "ETH"])
        self.assertEqual(all_assets, ["BTC", "ETH", "SOL"])
    
    def test_get_timeframes(self):
        """測試獲取時間框架"""
        short_tf = self.config_manager.get_timeframes("short_term")
        mid_tf = self.config_manager.get_timeframes("mid_term")
        
        self.assertEqual(short_tf, ["1m", "5m"])
        self.assertEqual(mid_tf, ["1h", "4h"])
    
    def test_get_market_condition_config(self):
        """測試獲取市場條件配置"""
        bull_config = self.config_manager.get_market_condition_config(MarketCondition.BULL)
        
        self.assertIsNotNone(bull_config)
        self.assertEqual(bull_config["description"], "Test bull market")
        self.assertIn("conditions", bull_config)
    
    def test_get_indicator_conditions(self):
        """測試獲取指標條件"""
        indicators = self.config_manager.get_indicator_conditions(
            MarketCondition.BULL, "technical_indicators"
        )
        
        self.assertEqual(len(indicators), 2)
        
        # 檢查RSI指標
        rsi_indicator = next((ind for ind in indicators if ind.name == "RSI_14"), None)
        self.assertIsNotNone(rsi_indicator)
        self.assertEqual(rsi_indicator.min_value, 60)
        self.assertEqual(rsi_indicator.max_value, 80)
        self.assertEqual(rsi_indicator.weight, 1.5)
    
    def test_get_strategy_config(self):
        """測試獲取策略配置"""
        strategy = self.config_manager.get_strategy_config(
            MarketCondition.BULL, StrategyType.SHORT_TERM
        )
        
        self.assertIsNotNone(strategy)
        self.assertEqual(strategy.name, "Bull Short Strategy")
        self.assertEqual(strategy.timeframe, "1h")
        self.assertEqual(strategy.stop_loss, "-3%")
        self.assertIn("RSI_1H", strategy.indicators)
    
    def test_get_asset_parameters(self):
        """測試獲取資產參數"""
        btc_params = self.config_manager.get_asset_parameters("BTC")
        
        self.assertIsNotNone(btc_params)
        self.assertEqual(btc_params.symbol, "BTC")
        self.assertEqual(btc_params.volatility_factor, 1.0)
        self.assertEqual(btc_params.market_cap_rank, 1)
    
    def test_calculate_market_score(self):
        """測試市場評分計算"""
        # 測試數據
        indicator_values = {
            "RSI_14": 70,      # 在範圍內 (60-80)
            "MA200_slope": 0.03  # 超過閾值 (0.02)
        }
        
        score, confidence = self.config_manager.calculate_market_score(
            MarketCondition.BULL, indicator_values
        )
        
        # 應該得到高分，因為兩個指標都符合條件
        self.assertGreater(score, 6.0)
        self.assertIn(confidence, [ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH])
    
    def test_indicator_evaluation(self):
        """測試指標評估邏輯"""
        # 測試閾值評估
        config_threshold = {"threshold": 0.02, "weight": 1.0}
        
        # 值大於閾值
        score = self.config_manager._evaluate_indicator(0.03, config_threshold)
        self.assertEqual(score, 1.0)
        
        # 值小於閾值
        score = self.config_manager._evaluate_indicator(0.01, config_threshold)
        self.assertEqual(score, 0.0)
        
        # 測試範圍評估
        config_range = {"min": 60, "max": 80, "weight": 1.0}
        
        # 值在範圍內
        score = self.config_manager._evaluate_indicator(70, config_range)
        self.assertEqual(score, 1.0)
        
        # 值在範圍外
        score = self.config_manager._evaluate_indicator(90, config_range)
        self.assertLess(score, 1.0)
    
    def test_risk_management_config(self):
        """測試風險管理配置"""
        risk_config = self.config_manager.get_risk_management_config()
        
        self.assertIn("position_sizing", risk_config)
        self.assertEqual(risk_config["position_sizing"]["conservative"]["max_per_trade"], 0.02)


class TestMarketAnalysisIntegration(unittest.TestCase):
    """市場分析整合測試"""
    
    def setUp(self):
        """設置整合測試環境"""
        # 使用實際配置文件進行測試
        try:
            self.config_manager = MarketConditionConfig()
        except FileNotFoundError:
            self.skipTest("實際配置文件未找到，跳過整合測試")
    
    def test_real_config_loading(self):
        """測試實際配置文件加載"""
        self.assertIsNotNone(self.config_manager.config)
        self.assertIn("market_conditions", self.config_manager.config)
        self.assertIn("custom_parameters", self.config_manager.config)
    
    def test_all_market_conditions(self):
        """測試所有市場條件配置"""
        for condition in MarketCondition:
            market_config = self.config_manager.get_market_condition_config(condition)
            self.assertIsNotNone(market_config, f"{condition.value} 配置不存在")
            self.assertIn("conditions", market_config, f"{condition.value} 缺少條件配置")
    
    def test_asset_parameters_completeness(self):
        """測試資產參數完整性"""
        all_assets = self.config_manager.get_assets("all")
        
        for asset in all_assets:
            params = self.config_manager.get_asset_parameters(asset)
            if params:  # 某些資產可能沒有特定參數
                self.assertIsInstance(params.volatility_factor, float)
                self.assertIsInstance(params.entry_padding, float)
                self.assertIsInstance(params.stop_loss_multiplier, float)


def run_performance_test():
    """運行性能測試"""
    import time
    
    print("開始性能測試...")
    
    # 測試配置加載性能
    start_time = time.time()
    config_manager = MarketConditionConfig()
    load_time = time.time() - start_time
    print(f"配置加載時間: {load_time:.4f} 秒")
    
    # 測試市場評分計算性能
    sample_data = {
        "MA200_slope": 0.025,
        "RSI_14": 65,
        "MACD_histogram": 0.5,
        "MVRV": 1.5,
        "FearGreed": 70,
        "FundingRate": 0.01,
        "Volume_MA": 1.8,
        "BB_position": 0.7
    }
    
    start_time = time.time()
    for _ in range(100):
        config_manager.calculate_market_score(MarketCondition.BULL, sample_data)
    calc_time = time.time() - start_time
    print(f"100次評分計算時間: {calc_time:.4f} 秒")
    print(f"平均單次計算時間: {calc_time/100:.6f} 秒")


if __name__ == "__main__":
    # 運行單元測試
    print("運行單元測試...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n" + "="*50)
    
    # 運行性能測試
    run_performance_test()
    
    print("\n測試完成！")
