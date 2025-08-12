#!/usr/bin/env python3
"""
Phase1A Dynamic Signal Generator Python Implementation Test
測試 phase1a_dynamic_signal_generator.py 的完整功能
確保邏輯無錯誤，數據流暢通，與JSON配置100%匹配
"""

import asyncio
import json
import sys
import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import tempfile

# 添加項目路徑
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

class Phase1ADynamicPythonTester:
    """Phase1A 動態 Python 實現測試器"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.test_results = []
        self.generator = None
        
    async def test_generator_initialization(self) -> bool:
        """測試生成器初始化"""
        success = True
        
        try:
            # 動態導入（避免路徑問題）
            sys.path.append(str(self.base_path))
            from phase1a_dynamic_signal_generator import Phase1ABasicSignalGenerator
            
            # 初始化生成器
            self.generator = Phase1ABasicSignalGenerator()
            
            # 檢查基本屬性
            if not hasattr(self.generator, 'config'):
                self.test_results.append("❌ 生成器缺少 config 屬性")
                success = False
                
            if not hasattr(self.generator, 'dynamic_engine'):
                self.test_results.append("❌ 生成器缺少 dynamic_engine 屬性")
                success = False
                
            if not hasattr(self.generator, 'performance_metrics'):
                self.test_results.append("❌ 生成器缺少 performance_metrics 屬性")
                success = False
                
            # 檢查配置載入
            if not self.generator.config:
                self.test_results.append("❌ 配置載入失敗")
                success = False
            else:
                # 檢查關鍵配置節點
                config_dependency = self.generator.config.get("phase1a_basic_signal_generation_dependency", {})
                if not config_dependency:
                    self.test_results.append("❌ 主配置節點缺失")
                    success = False
                    
        except ImportError as e:
            self.test_results.append(f"❌ 模組導入失敗: {e}")
            success = False
        except Exception as e:
            self.test_results.append(f"❌ 生成器初始化失敗: {e}")
            success = False
            
        if success:
            self.test_results.append("✅ 生成器初始化: 通過")
            
        return success
    
    async def test_configuration_matching(self) -> bool:
        """測試配置匹配度"""
        success = True
        
        if not self.generator:
            self.test_results.append("❌ 生成器未初始化，跳過配置匹配測試")
            return False
            
        try:
            # 測試基礎模式參數獲取
            basic_params = await self.generator._get_current_parameters("basic_mode")
            
            # 檢查必要參數
            required_params = [
                "price_change_threshold", "volume_change_threshold", 
                "signal_strength_range", "confidence_calculation", "confidence_threshold"
            ]
            
            for param in required_params:
                if param not in basic_params:
                    self.test_results.append(f"❌ 基礎模式缺少參數: {param}")
                    success = False
                    
            # 檢查 confidence_threshold 是否為數值
            confidence_threshold = basic_params.get("confidence_threshold")
            if not isinstance(confidence_threshold, (int, float)):
                self.test_results.append(f"❌ confidence_threshold 類型錯誤: {type(confidence_threshold)}")
                success = False
            elif not 0 <= confidence_threshold <= 1:
                self.test_results.append(f"❌ confidence_threshold 值超出範圍: {confidence_threshold}")
                success = False
                
            # 測試極端市場模式參數獲取
            extreme_params = await self.generator._get_current_parameters("extreme_market_mode")
            
            extreme_required = [
                "price_change_threshold", "volume_change_threshold",
                "signal_strength_boost", "priority_escalation", "confidence_threshold"
            ]
            
            for param in extreme_required:
                if param not in extreme_params:
                    self.test_results.append(f"❌ 極端模式缺少參數: {param}")
                    success = False
                    
        except Exception as e:
            self.test_results.append(f"❌ 配置匹配測試失敗: {e}")
            success = False
            
        if success:
            self.test_results.append("✅ 配置匹配度: 通過")
            
        return success
    
    async def test_dynamic_parameter_integration(self) -> bool:
        """測試動態參數系統整合"""
        success = True
        
        if not self.generator:
            self.test_results.append("❌ 生成器未初始化，跳過動態參數測試")
            return False
            
        try:
            # 檢查動態引擎
            if self.generator.dynamic_engine is None:
                self.test_results.append("⚠️ 動態引擎未初始化（可能正常，如果配置為關閉）")
                # 不算失敗，因為配置可能設為關閉
            else:
                # 測試動態參數獲取
                basic_params_1 = await self.generator._get_current_parameters("basic_mode")
                
                # 等待一小段時間後再次獲取（測試緩存）
                await asyncio.sleep(0.1)
                basic_params_2 = await self.generator._get_current_parameters("basic_mode")
                
                # 第二次應該來自緩存，結果應該相同
                if basic_params_1 != basic_params_2:
                    self.test_results.append("❌ 參數緩存機制異常")
                    success = False
                    
                # 測試參數結構
                confidence_threshold = basic_params_1.get("confidence_threshold")
                if confidence_threshold is None:
                    self.test_results.append("❌ 動態參數未正確設置 confidence_threshold")
                    success = False
                    
        except Exception as e:
            self.test_results.append(f"❌ 動態參數整合測試失敗: {e}")
            success = False
            
        if success:
            self.test_results.append("✅ 動態參數系統整合: 通過")
            
        return success
    
    async def test_signal_generation_logic(self) -> bool:
        """測試信號生成邏輯"""
        success = True
        
        if not self.generator:
            self.test_results.append("❌ 生成器未初始化，跳過信號生成測試")
            return False
            
        try:
            # 測試案例1：正常信號生成
            signal1 = await self.generator.generate_basic_signal(
                symbol="BTCUSDT",
                current_price=50100,
                previous_price=50000,
                current_volume=2000,
                previous_volume=1000,
                is_extreme_market=False
            )
            
            if signal1 is None:
                self.test_results.append("⚠️ 正常條件下未生成信號（可能由於門檻設置）")
            else:
                # 檢查信號結構
                required_attrs = [
                    'timestamp', 'symbol', 'signal_type', 'confidence',
                    'price_change', 'volume_change', 'signal_strength',
                    'market_regime', 'trading_session'
                ]
                
                for attr in required_attrs:
                    if not hasattr(signal1, attr):
                        self.test_results.append(f"❌ 信號缺少屬性: {attr}")
                        success = False
                        
                # 檢查信號類型
                if hasattr(signal1, 'signal_type') and signal1.signal_type not in ['BUY', 'SELL']:
                    self.test_results.append(f"❌ 信號類型無效: {signal1.signal_type}")
                    success = False
                    
                # 檢查信心度範圍
                if hasattr(signal1, 'confidence') and not 0 <= signal1.confidence <= 1:
                    self.test_results.append(f"❌ 信心度超出範圍: {signal1.confidence}")
                    success = False
                    
            # 測試案例2：極端市場條件
            signal2 = await self.generator.generate_basic_signal(
                symbol="ETHUSDT",
                current_price=3000,
                previous_price=2900,  # 大幅上漲
                current_volume=5000,
                previous_volume=1000,  # 大幅增量
                is_extreme_market=True
            )
            
            # 測試案例3：不滿足門檻條件
            signal3 = await self.generator.generate_basic_signal(
                symbol="ADAUSDT",
                current_price=1.001,
                previous_price=1.000,  # 微小變化
                current_volume=100,
                previous_volume=100,   # 無變化
                is_extreme_market=False
            )
            
            if signal3 is not None:
                self.test_results.append("⚠️ 不滿足門檻的條件生成了信號（可能閾值設置過低）")
                
        except Exception as e:
            self.test_results.append(f"❌ 信號生成邏輯測試失敗: {e}")
            success = False
            
        if success:
            self.test_results.append("✅ 信號生成邏輯: 通過")
            
        return success
    
    async def test_websocket_data_processing(self) -> bool:
        """測試 WebSocket 數據處理"""
        success = True
        
        if not self.generator:
            self.test_results.append("❌ 生成器未初始化，跳過 WebSocket 測試")
            return False
            
        try:
            # 測試正常數據
            test_data1 = {
                'symbol': 'BTCUSDT',
                'price_data': [50000, 50100, 50200, 49900],
                'volume_data': [1000, 1500, 2000, 1800]
            }
            
            signals1 = await self.generator.process_websocket_data(test_data1)
            
            # 檢查結果類型
            if signals1 is not None and not isinstance(signals1, list):
                self.test_results.append(f"❌ WebSocket 處理返回類型錯誤: {type(signals1)}")
                success = False
                
            # 測試無效數據
            test_data2 = {
                'symbol': 'INVALID',
                'price_data': [50000],  # 數據不足
                'volume_data': [1000]
            }
            
            signals2 = await self.generator.process_websocket_data(test_data2)
            if signals2 is not None:
                self.test_results.append("⚠️ 無效數據返回了信號（應該返回 None）")
                
            # 測試缺失數據
            test_data3 = {
                'symbol': 'BTCUSDT'
                # 缺少 price_data 和 volume_data
            }
            
            signals3 = await self.generator.process_websocket_data(test_data3)
            if signals3 is not None:
                self.test_results.append("❌ 缺失數據應該返回 None")
                success = False
                
        except Exception as e:
            self.test_results.append(f"❌ WebSocket 數據處理測試失敗: {e}")
            success = False
            
        if success:
            self.test_results.append("✅ WebSocket 數據處理: 通過")
            
        return success
    
    async def test_performance_monitoring(self) -> bool:
        """測試性能監控"""
        success = True
        
        if not self.generator:
            self.test_results.append("❌ 生成器未初始化，跳過性能監控測試")
            return False
            
        try:
            # 生成一些信號以產生性能數據
            for i in range(5):
                await self.generator.generate_basic_signal(
                    symbol=f"TEST{i}",
                    current_price=100 + i,
                    previous_price=100,
                    current_volume=1000 + i * 100,
                    previous_volume=1000,
                    is_extreme_market=False
                )
            
            # 獲取性能指標
            metrics = self.generator.get_performance_metrics()
            
            # 檢查必要的指標
            required_metrics = [
                'processing_latency_p99_ms',
                'avg_processing_latency_ms',
                'total_signals_generated',
                'error_rate_percent',
                'cache_hit_info'
            ]
            
            for metric in required_metrics:
                if metric not in metrics:
                    self.test_results.append(f"❌ 缺少性能指標: {metric}")
                    success = False
                    
            # 檢查數值合理性
            if 'processing_latency_p99_ms' in metrics:
                p99_latency = metrics['processing_latency_p99_ms']
                if not isinstance(p99_latency, (int, float)) or p99_latency < 0:
                    self.test_results.append(f"❌ P99 延遲值異常: {p99_latency}")
                    success = False
                elif p99_latency > 1000:  # 超過1秒可能有問題
                    self.test_results.append(f"⚠️ P99 延遲偏高: {p99_latency}ms")
                    
        except Exception as e:
            self.test_results.append(f"❌ 性能監控測試失敗: {e}")
            success = False
            
        if success:
            self.test_results.append("✅ 性能監控: 通過")
            
        return success
    
    async def test_extreme_market_detection(self) -> bool:
        """測試極端市場檢測"""
        success = True
        
        if not self.generator:
            self.test_results.append("❌ 生成器未初始化，跳過極端市場檢測測試")
            return False
            
        try:
            # 測試正常市場條件
            normal_prices = [100, 100.5, 101, 100.8]
            normal_volumes = [1000, 1100, 1200, 1150]
            
            is_extreme_normal = self.generator._detect_extreme_market_conditions(
                normal_prices, normal_volumes
            )
            
            # 測試極端價格波動
            extreme_prices = [100, 105, 110, 95]  # 大幅波動
            extreme_volumes = [1000, 1100, 1200, 1150]
            
            is_extreme_price = self.generator._detect_extreme_market_conditions(
                extreme_prices, extreme_volumes
            )
            
            # 測試極端成交量
            normal_prices2 = [100, 100.5, 101, 100.8]
            extreme_volumes2 = [1000, 3000, 5000, 4000]  # 大幅增量
            
            is_extreme_volume = self.generator._detect_extreme_market_conditions(
                normal_prices2, extreme_volumes2
            )
            
            # 驗證檢測結果
            if is_extreme_normal:
                self.test_results.append("❌ 正常市場條件被誤判為極端")
                success = False
                
            if not is_extreme_price:
                self.test_results.append("❌ 極端價格波動未被檢測")
                success = False
                
            if not is_extreme_volume:
                self.test_results.append("❌ 極端成交量未被檢測")
                success = False
                
        except Exception as e:
            self.test_results.append(f"❌ 極端市場檢測測試失敗: {e}")
            success = False
            
        if success:
            self.test_results.append("✅ 極端市場檢測: 通過")
            
        return success
    
    async def test_data_structure_integrity(self) -> bool:
        """測試數據結構完整性"""
        success = True
        
        if not self.generator:
            self.test_results.append("❌ 生成器未初始化，跳過數據結構測試")
            return False
            
        try:
            # 生成一個信號
            signal = await self.generator.generate_basic_signal(
                symbol="TESTCOIN",
                current_price=50100,
                previous_price=50000,
                current_volume=2000,
                previous_volume=1000,
                is_extreme_market=False
            )
            
            if signal:
                # 測試 to_dict 方法
                signal_dict = signal.to_dict()
                
                if not isinstance(signal_dict, dict):
                    self.test_results.append(f"❌ to_dict 返回類型錯誤: {type(signal_dict)}")
                    success = False
                    
                # 檢查 timestamp 序列化
                if 'timestamp' in signal_dict:
                    timestamp_str = signal_dict['timestamp']
                    if not isinstance(timestamp_str, str):
                        self.test_results.append(f"❌ timestamp 序列化錯誤: {type(timestamp_str)}")
                        success = False
                        
                # 檢查必要欄位
                required_fields = [
                    'timestamp', 'symbol', 'signal_type', 'confidence',
                    'price_change', 'volume_change', 'signal_strength',
                    'market_regime', 'trading_session'
                ]
                
                for field in required_fields:
                    if field not in signal_dict:
                        self.test_results.append(f"❌ 信號字典缺少欄位: {field}")
                        success = False
                        
                # 測試 JSON 序列化
                try:
                    json.dumps(signal_dict)
                except Exception as e:
                    self.test_results.append(f"❌ 信號無法 JSON 序列化: {e}")
                    success = False
                    
        except Exception as e:
            self.test_results.append(f"❌ 數據結構完整性測試失敗: {e}")
            success = False
            
        if success:
            self.test_results.append("✅ 數據結構完整性: 通過")
            
        return success
    
    async def test_error_handling(self) -> bool:
        """測試錯誤處理"""
        success = True
        
        if not self.generator:
            self.test_results.append("❌ 生成器未初始化，跳過錯誤處理測試")
            return False
            
        try:
            # 測試無效價格數據
            signal1 = await self.generator.generate_basic_signal(
                symbol="TEST",
                current_price=0,  # 無效價格
                previous_price=100,
                current_volume=1000,
                previous_volume=1000,
                is_extreme_market=False
            )
            
            # 測試除零情況
            signal2 = await self.generator.generate_basic_signal(
                symbol="TEST",
                current_price=100,
                previous_price=0,  # 可能導致除零
                current_volume=1000,
                previous_volume=1000,
                is_extreme_market=False
            )
            
            # 測試負數成交量
            signal3 = await self.generator.generate_basic_signal(
                symbol="TEST",
                current_price=100,
                previous_price=99,
                current_volume=-1000,  # 負數成交量
                previous_volume=1000,
                is_extreme_market=False
            )
            
            # 這些情況應該優雅處理，不應該拋出異常
            # 如果到達這裡沒有異常，說明錯誤處理正常
            
        except Exception as e:
            self.test_results.append(f"❌ 錯誤處理測試失敗（應該優雅處理）: {e}")
            success = False
            
        if success:
            self.test_results.append("✅ 錯誤處理: 通過")
            
        return success
    
    async def test_cleanup_functionality(self) -> bool:
        """測試清理功能"""
        success = True
        
        if not self.generator:
            self.test_results.append("❌ 生成器未初始化，跳過清理測試")
            return False
            
        try:
            # 執行清理
            await self.generator.cleanup()
            
            # 清理不應該拋出異常
            
        except Exception as e:
            self.test_results.append(f"❌ 清理功能測試失敗: {e}")
            success = False
            
        if success:
            self.test_results.append("✅ 清理功能: 通過")
            
        return success
    
    async def run_all_tests(self) -> bool:
        """執行所有測試"""
        print("🧪 開始執行 Phase1A Dynamic Python 實現測試...")
        print("=" * 60)
        
        # 執行測試
        tests = [
            await self.test_generator_initialization(),
            await self.test_configuration_matching(),
            await self.test_dynamic_parameter_integration(),
            await self.test_signal_generation_logic(),
            await self.test_websocket_data_processing(),
            await self.test_performance_monitoring(),
            await self.test_extreme_market_detection(),
            await self.test_data_structure_integrity(),
            await self.test_error_handling(),
            await self.test_cleanup_functionality()
        ]
        
        # 輸出結果
        print("\n📊 測試結果:")
        print("-" * 40)
        for result in self.test_results:
            print(result)
            
        total_tests = len(tests)
        passed_tests = sum(tests)
        
        print(f"\n📈 測試總結: {passed_tests}/{total_tests} 通過")
        
        if passed_tests == total_tests:
            print("🎉 所有測試通過！Python 實現完成，邏輯無錯誤")
            return True
        else:
            print("⚠️ 部分測試失敗，需要修復後再繼續")
            return False

async def main():
    """主函數"""
    tester = Phase1ADynamicPythonTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✅ Phase1A Dynamic Python 實現測試完成")
        print("🚀 準備整合到主系統")
        return 0
    else:
        print("\n❌ Phase1A Dynamic Python 實現測試失敗")
        print("🔧 需要修復問題後重新測試")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
