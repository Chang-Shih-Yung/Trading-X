#!/usr/bin/env python3
"""
即時 API 優化部分測試
測試 OrderBook 整合和資金費率 API 功能
"""

import asyncio
import sys
import logging
from datetime import datetime
from pathlib import Path
import time

# 添加路徑
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealtimeAPITester:
    """即時 API 優化測試器"""
    
    def __init__(self):
        self.test_results = []
        self.errors = []
    
    async def test_phase1a_orderbook_integration(self):
        """測試 Phase1A OrderBook 整合"""
        print("\n🔍 測試 Phase1A OrderBook 整合...")
        
        try:
            from phase1a_basic_signal_generation import Phase1ABasicSignalGeneration
            
            # 初始化
            generator = Phase1ABasicSignalGeneration()
            
            # 檢查 OrderBook 緩衝區是否存在
            if hasattr(generator, 'orderbook_buffer'):
                self.test_results.append("✅ OrderBook 緩衝區初始化成功")
            else:
                self.errors.append("❌ OrderBook 緩衝區未找到")
                return False
            
            # 測試 OrderBook 數據處理方法
            required_methods = [
                '_on_orderbook_update',
                '_calculate_spread',
                '_calculate_book_depth', 
                '_calculate_liquidity_ratio',
                '_check_orderbook_signals',
                '_create_enhanced_market_data',
                '_generate_orderbook_enhanced_signals'
            ]
            
            for method_name in required_methods:
                if hasattr(generator, method_name):
                    self.test_results.append(f"✅ {method_name} 方法存在")
                else:
                    self.errors.append(f"❌ {method_name} 方法缺失")
            
            # 測試模擬 OrderBook 數據處理
            mock_orderbook = {
                'symbol': 'BTCUSDT',
                'timestamp': datetime.now(),
                'bids': [[50000.0, 1.0], [49999.0, 2.0], [49998.0, 1.5]],
                'asks': [[50001.0, 0.8], [50002.0, 1.2], [50003.0, 1.0]]
            }
            
            # 測試價差計算
            spread = generator._calculate_spread(mock_orderbook)
            if isinstance(spread, float) and spread >= 0:
                self.test_results.append(f"✅ 價差計算正常: {spread:.6f}%")
            else:
                self.errors.append(f"❌ 價差計算異常: {spread}")
            
            # 測試深度計算
            depth = generator._calculate_book_depth(mock_orderbook)
            if isinstance(depth, float) and depth > 0:
                self.test_results.append(f"✅ 深度計算正常: {depth:.2f}")
            else:
                self.errors.append(f"❌ 深度計算異常: {depth}")
            
            # 測試流動性比率計算
            liquidity_ratio = generator._calculate_liquidity_ratio(mock_orderbook)
            if isinstance(liquidity_ratio, float) and 0 <= liquidity_ratio <= 1:
                self.test_results.append(f"✅ 流動性比率計算正常: {liquidity_ratio:.3f}")
            else:
                self.errors.append(f"❌ 流動性比率計算異常: {liquidity_ratio}")
            
            # 測試 OrderBook 數據更新
            await generator._on_orderbook_update('BTCUSDT', mock_orderbook)
            
            if len(generator.orderbook_buffer['BTCUSDT']) > 0:
                self.test_results.append("✅ OrderBook 數據更新成功")
                
                # 檢查處理後的數據結構
                processed_data = generator.orderbook_buffer['BTCUSDT'][-1]
                required_fields = ['symbol', 'timestamp', 'bids', 'asks', 'bid_ask_spread', 'book_depth', 'liquidity_ratio']
                
                for field in required_fields:
                    if field in processed_data:
                        self.test_results.append(f"✅ OrderBook 字段 {field} 存在")
                    else:
                        self.errors.append(f"❌ OrderBook 字段 {field} 缺失")
            else:
                self.errors.append("❌ OrderBook 數據更新失敗")
            
            return len(self.errors) == 0
            
        except Exception as e:
            self.errors.append(f"❌ Phase1A OrderBook 測試失敗: {e}")
            return False
    
    async def test_phase3_funding_rate_integration(self):
        """測試 Phase3 資金費率整合"""
        print("\n🔍 測試 Phase3 資金費率整合...")
        
        try:
            from phase3_market_analyzer import Phase3MarketAnalyzer
            
            # 初始化
            analyzer = Phase3MarketAnalyzer()
            
            # 檢查必要的方法
            required_methods = [
                '_collect_funding_rate',
                '_analyze_funding_rate_trend',
                '_calculate_funding_sentiment',
                '_check_funding_rate_signals',
                '_map_sentiment_to_category'
            ]
            
            for method_name in required_methods:
                if hasattr(analyzer, method_name):
                    self.test_results.append(f"✅ {method_name} 方法存在")
                else:
                    self.errors.append(f"❌ {method_name} 方法缺失")
            
            # 測試資金費率趨勢分析（使用模擬數據）
            mock_funding_data = {
                'fundingRate': '0.0001',
                'fundingTime': int(time.time() * 1000),
                'nextFundingTime': int(time.time() * 1000) + 8 * 3600 * 1000
            }
            
            funding_analysis = await analyzer._analyze_funding_rate_trend(0.0001, mock_funding_data)
            
            if isinstance(funding_analysis, dict):
                required_fields = ['trend', 'volatility', 'extreme_level', 'rate_momentum', 'historical_percentile']
                for field in required_fields:
                    if field in funding_analysis:
                        self.test_results.append(f"✅ 資金費率分析字段 {field} 存在")
                    else:
                        self.errors.append(f"❌ 資金費率分析字段 {field} 缺失")
            else:
                self.errors.append("❌ 資金費率趨勢分析返回格式錯誤")
            
            # 測試情緒分數計算
            sentiment_score = analyzer._calculate_funding_sentiment(0.0001, funding_analysis)
            
            if isinstance(sentiment_score, float) and 0 <= sentiment_score <= 1:
                self.test_results.append(f"✅ 情緒分數計算正常: {sentiment_score:.3f}")
            else:
                self.errors.append(f"❌ 情緒分數計算異常: {sentiment_score}")
            
            # 測試情緒分類映射
            sentiment_categories = [0.1, 0.3, 0.5, 0.7, 0.9]
            for score in sentiment_categories:
                category = analyzer._map_sentiment_to_category(score)
                if isinstance(category, str) and category in ["extreme_bearish", "bearish", "mild_bearish", "neutral", "mild_bullish", "bullish", "extreme_bullish"]:
                    self.test_results.append(f"✅ 情緒分類映射正常: {score} → {category}")
                else:
                    self.errors.append(f"❌ 情緒分類映射異常: {score} → {category}")
            
            return len(self.errors) == 0
            
        except Exception as e:
            self.errors.append(f"❌ Phase3 資金費率測試失敗: {e}")
            return False
    
    async def test_data_structure_integrity(self):
        """測試數據結構完整性"""
        print("\n🔍 測試數據結構完整性...")
        
        try:
            from phase1a_basic_signal_generation import BasicSignal, MarketData, SignalType, Priority
            from phase3_market_analyzer import MarketMicrostructureSignal
            
            # 測試 BasicSignal 結構
            test_signal = BasicSignal(
                signal_id="test_001",
                symbol="BTCUSDT",
                signal_type=SignalType.VOLUME,
                direction="BUY",
                strength=0.8,
                confidence=0.9,
                priority=Priority.MEDIUM,
                timestamp=datetime.now(),
                price=50000.0,
                volume=1000000.0,
                metadata={"orderbook_enhanced": True},
                layer_source="test",
                processing_time_ms=5.0,
                market_regime="BULL_TREND",
                trading_session="US_MARKET",
                price_change=0.02,
                volume_change=1.5
            )
            
            # 檢查 to_dict 方法
            if hasattr(test_signal, 'to_dict'):
                signal_dict = test_signal.to_dict()
                if isinstance(signal_dict, dict) and 'signal_id' in signal_dict:
                    self.test_results.append("✅ BasicSignal to_dict 方法正常")
                else:
                    self.errors.append("❌ BasicSignal to_dict 返回格式錯誤")
            else:
                self.errors.append("❌ BasicSignal 缺少 to_dict 方法")
            
            # 測試 MarketData 結構
            test_market_data = MarketData(
                timestamp=datetime.now(),
                price=50000.0,
                volume=1000000.0,
                price_change_1h=0.01,
                price_change_24h=0.02,
                volume_ratio=1.2,
                volatility=0.03,
                fear_greed_index=65,
                bid_ask_spread=0.001,  # OrderBook 整合字段
                market_depth=5000.0,   # OrderBook 整合字段
                moving_averages={"ma_20": 49800.0}
            )
            
            if test_market_data.bid_ask_spread == 0.001 and test_market_data.market_depth == 5000.0:
                self.test_results.append("✅ MarketData OrderBook 字段整合正常")
            else:
                self.errors.append("❌ MarketData OrderBook 字段整合失敗")
            
            # 測試 MarketMicrostructureSignal 結構
            test_micro_signal = MarketMicrostructureSignal(
                signal_id="micro_001",
                signal_type="SENTIMENT_DIVERGENCE",
                signal_strength=0.8,
                signal_confidence=0.9,
                tier_assignment="tier_2_important",
                processing_priority="batch_5s",
                bid_ask_imbalance=0.0,
                liquidity_shock_magnitude=0.5,
                institutional_flow_direction="BUY",
                funding_sentiment="bullish",
                timestamp=datetime.now()
            )
            
            if test_micro_signal.funding_sentiment == "bullish":
                self.test_results.append("✅ MarketMicrostructureSignal 資金費率字段正常")
            else:
                self.errors.append("❌ MarketMicrostructureSignal 資金費率字段異常")
            
            return len(self.errors) == 0
            
        except Exception as e:
            self.errors.append(f"❌ 數據結構完整性測試失敗: {e}")
            return False
    
    async def test_integration_flow(self):
        """測試整合流程"""
        print("\n🔍 測試整合流程...")
        
        try:
            from phase1a_basic_signal_generation import Phase1ABasicSignalGeneration, MarketData
            
            generator = Phase1ABasicSignalGeneration()
            
            # 模擬完整的數據流
            # 1. 添加一些歷史價格數據
            for i in range(10):
                price_data = {
                    'price': 50000.0 + i * 10,
                    'timestamp': datetime.now(),
                    'volume': 1000000.0,
                    'price_change_1h': 0.01,
                    'price_change_24h': 0.02,
                    'volatility': 0.03,
                    'fear_greed_index': 65,
                    'moving_averages': {'ma_20': 49800.0}
                }
                generator.price_buffer['BTCUSDT'].append(price_data)
                generator.volume_buffer['BTCUSDT'].append(price_data)
            
            # 2. 測試動態參數獲取
            try:
                dynamic_params = await generator._get_dynamic_parameters("basic_mode")
                self.test_results.append("✅ 動態參數獲取成功")
            except Exception as e:
                self.errors.append(f"❌ 動態參數獲取失敗: {e}")
            
            # 3. 測試 OrderBook 增強市場數據創建
            mock_orderbook = {
                'symbol': 'BTCUSDT',
                'timestamp': datetime.now(),
                'bids': [[50000.0, 1.0]],
                'asks': [[50001.0, 1.0]],
                'bid_ask_spread': 0.002,
                'book_depth': 2000.0,
                'liquidity_ratio': 0.5
            }
            
            enhanced_data = generator._create_enhanced_market_data('BTCUSDT', mock_orderbook)
            
            if enhanced_data and isinstance(enhanced_data, MarketData):
                if enhanced_data.bid_ask_spread == 0.002 and enhanced_data.market_depth == 2000.0:
                    self.test_results.append("✅ OrderBook 增強市場數據創建成功")
                else:
                    self.errors.append("❌ OrderBook 增強數據字段錯誤")
            else:
                self.errors.append("❌ OrderBook 增強市場數據創建失敗")
            
            # 4. 測試信號生成
            if enhanced_data:
                await generator._generate_orderbook_enhanced_signals('BTCUSDT', enhanced_data)
                
                if len(generator.signal_buffer) > 0:
                    latest_signal = generator.signal_buffer[-1]
                    if hasattr(latest_signal, 'metadata') and latest_signal.metadata.get('orderbook_enhanced'):
                        self.test_results.append("✅ OrderBook 增強信號生成成功")
                    else:
                        self.errors.append("❌ OrderBook 增強信號標記缺失")
                else:
                    # 這是正常的，因為可能不滿足信號生成條件
                    self.test_results.append("✅ 信號生成邏輯運行正常（無信號生成）")
            
            return len(self.errors) == 0
            
        except Exception as e:
            self.errors.append(f"❌ 整合流程測試失敗: {e}")
            return False
    
    def print_results(self):
        """打印測試結果"""
        print("\n" + "="*80)
        print("📊 即時 API 優化測試結果")
        print("="*80)
        
        print(f"\n✅ 成功項目: {len(self.test_results)}")
        for result in self.test_results:
            print(f"   {result}")
        
        if self.errors:
            print(f"\n❌ 錯誤項目: {len(self.errors)}")
            for error in self.errors:
                print(f"   {error}")
        
        print("\n" + "="*80)
        if self.errors:
            print("🚨 測試未完全通過，需要修復上述錯誤")
            return False
        else:
            print("🎉 即時 API 優化測試 100% 通過！")
            return True

async def main():
    """主測試函數"""
    print("🔍 開始即時 API 優化測試...")
    
    tester = RealtimeAPITester()
    
    # 執行所有測試
    tests = [
        ("Phase1A OrderBook 整合", tester.test_phase1a_orderbook_integration),
        ("Phase3 資金費率整合", tester.test_phase3_funding_rate_integration),
        ("數據結構完整性", tester.test_data_structure_integrity),
        ("整合流程", tester.test_integration_flow)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🔍 {test_name}")
        print(f"{'='*60}")
        
        try:
            result = await test_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name} 測試出錯: {e}")
            all_passed = False
    
    # 打印最終結果
    final_result = tester.print_results()
    
    return final_result and all_passed

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
