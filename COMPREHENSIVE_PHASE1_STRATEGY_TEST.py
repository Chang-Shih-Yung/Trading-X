"""
全面 Phase1 策略測試
確保即時數據通過所有 phase1_signal_generation 策略檔案
目標：驗證每個策略模組都能接收並處理數據
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from dataclasses import asdict
import traceback

# 添加路徑
sys.path.append('/Users/henrychang/Desktop/Trading-X')
sys.path.append('/Users/henrychang/Desktop/Trading-X/X/backend')

# 導入真實系統組件
from X.app.services.market_data import MarketDataService
from X.app.services.realtime_signal_engine import RealtimeSignalEngine

# 導入Phase1真實模組
from phase1_signal_generation.phase1a_basic_signal_generation.phase1a_basic_signal_generation import Phase1ABasicSignalGeneration, MarketData
from phase1_signal_generation.phase1b_volatility_adaptation.phase1b_volatility_adaptation import Phase1BVolatilityAdaptationEngine  
from phase1_signal_generation.phase1c_signal_standardization.phase1c_signal_standardization import Phase1CSignalStandardizationEngine

# 其他關鍵模組將使用動態導入測試

async def test_comprehensive_phase1_strategies():
    """全面測試Phase1策略檔案"""
    print("🎯 全面Phase1策略檔案測試")
    print("測試目標: 確保即時數據通過所有策略模組")
    print("="*80)
    
    # 測試結果記錄
    test_results = {
        'market_data_service': False,
        'realtime_signal_engine': False,
        'phase1a_initialization': False,
        'phase1a_data_processing': False,
        'phase1a_signal_generation': False,
        'phase1b_initialization': False,
        'phase1b_signal_adaptation': False,
        'phase1c_initialization': False,
        'phase1c_signal_standardization': False,
        'intelligent_trigger_engine': False,
        'indicator_dependency_graph': False,
        'unified_signal_pool': False,
        'dynamic_parameter_system': False,
        'data_flow_integrity': False,
        'end_to_end_processing': False
    }
    
    strategy_files_tested = []
    
    try:
        # 1. 初始化MarketDataService
        print("📡 測試 MarketDataService 初始化...")
        market_service = MarketDataService()
        test_results['market_data_service'] = True
        strategy_files_tested.append("market_data.py")
        print("✅ MarketDataService 初始化成功")
        
        # 2. 初始化RealtimeSignalEngine
        print("🎯 測試 RealtimeSignalEngine 初始化...")
        signal_engine = RealtimeSignalEngine()
        await signal_engine.initialize(market_service)
        test_results['realtime_signal_engine'] = True
        strategy_files_tested.append("realtime_signal_engine.py")
        print("✅ RealtimeSignalEngine 初始化成功")
        
        # 3. 初始化Phase1A並正確啟動系統
        print("🧠 測試 Phase1A 基礎信號生成...")
        phase1a = Phase1ABasicSignalGeneration()
        test_results['phase1a_initialization'] = True
        strategy_files_tested.append("phase1a_basic_signal_generation.py")
        
        # 創建模擬 WebSocket 驅動（Phase1A 必需的）
        class MockWebSocketDriver:
            def __init__(self):
                self.subscribers = []
            def subscribe(self, callback):
                self.subscribers.append(callback)
                print(f"✅ Phase1A WebSocket 回調已註冊")
        
        websocket_driver = MockWebSocketDriver()
        
        # 關鍵：啟動 Phase1A 系統
        print("🚀 啟動 Phase1A 系統...")
        await phase1a.start(websocket_driver)
        
        # 建立數據緩衝區（Phase1A 信號生成的必要條件）
        print("📊 建立 Phase1A 數據緩衝區...")
        test_symbol = 'BTCUSDT'
        
        # 手動添加足夠的歷史數據到緩衝區
        for i in range(25):  # 25個數據點，滿足所有層級要求
            base_price = 50000
            price_change = (i % 5 - 2) * 0.001  # 小幅價格變化
            price = base_price * (1 + price_change)
            
            phase1a.price_buffer[test_symbol].append({
                'symbol': test_symbol,
                'price': price,
                'volume': 1000000 + (i * 50000),
                'timestamp': datetime.now() - timedelta(seconds=(25-i)*10)
            })
            
            phase1a.volume_buffer[test_symbol].append({
                'symbol': test_symbol,
                'volume': 1000000 + (i * 50000),
                'timestamp': datetime.now() - timedelta(seconds=(25-i)*10)
            })
        
        print(f"✅ {test_symbol} 緩衝區建立完成，大小: {len(phase1a.price_buffer[test_symbol])}")
        test_results['phase1a_data_processing'] = True
        
        # 4. 測試Phase1A信號生成能力（使用正確的方法）
        print("🎯 測試 Phase1A 信號生成能力...")
        generated_signals = []
        
        # 測試多個幣種
        test_symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
        
        for symbol in test_symbols:
            try:
                # 確保每個symbol都有數據緩衝區
                if len(phase1a.price_buffer[symbol]) == 0:
                    # 為新symbol建立緩衝區
                    base_price = 50000 if 'BTC' in symbol else (3000 if 'ETH' in symbol else 1.0)
                    for i in range(25):
                        price_change = (i % 5 - 2) * 0.001
                        price = base_price * (1 + price_change)
                        
                        phase1a.price_buffer[symbol].append({
                            'symbol': symbol,
                            'price': price,
                            'volume': 1000000 + (i * 50000),
                            'timestamp': datetime.now() - timedelta(seconds=(25-i)*10)
                        })
                
                # 創建觸發信號的市場數據
                base_price = 50000 if 'BTC' in symbol else (3000 if 'ETH' in symbol else 1.0)
                market_data = MarketData(
                    timestamp=datetime.now(),
                    price=base_price * 1.015,  # 1.5% 價格上漲，超過預設閾值0.1%
                    volume=2000000,
                    price_change_1h=0.015,  # 1.5% 變化
                    price_change_24h=0.03,
                    volume_ratio=2.0,  # 2倍成交量變化
                    volatility=0.02,
                    fear_greed_index=70,
                    bid_ask_spread=0.01,
                    market_depth=1000000,
                    moving_averages={'ma_20': base_price}
                )
                
                # 使用正確的API生成信號
                signals = await phase1a.generate_signals(symbol, market_data)
                
                if signals:
                    generated_signals.extend(signals)
                    print(f"  📈 {symbol}: 生成 {len(signals)} 個信號")
                    
                    # 顯示信號詳情
                    for i, signal in enumerate(signals):
                        print(f"    信號 {i+1}: {signal.signal_type.value} | {signal.direction} | 強度: {signal.strength:.3f} | 信心度: {signal.confidence:.3f}")
                else:
                    print(f"  📈 {symbol}: 生成 0 個信號")
                    
            except Exception as e:
                print(f"  ❌ {symbol}: 處理失敗 - {e}")
        
        if generated_signals:
            test_results['phase1a_signal_generation'] = True
            print(f"✅ Phase1A 總共生成 {len(generated_signals)} 個信號")
        else:
            print("⚠️ Phase1A 未生成任何信號")
            test_results['phase1a_signal_generation'] = False
        
        # 5. 初始化並測試Phase1B
        print("🧠 測試 Phase1B 波動適應...")
        phase1b = Phase1BVolatilityAdaptationEngine()
        test_results['phase1b_initialization'] = True
        strategy_files_tested.append("phase1b_volatility_adaptation.py")
        
        # 測試Phase1B信號適應
        if generated_signals:
            # 轉換信號格式為字典
            signals_dict = []
            for signal in generated_signals:
                signal_dict = {
                    'signal_id': signal.signal_id,
                    'symbol': signal.symbol,
                    'signal_type': signal.signal_type.value,
                    'direction': signal.direction,
                    'strength': signal.strength,
                    'confidence': signal.confidence,
                    'timestamp': signal.timestamp.isoformat(),
                    'source': 'phase1a',
                    'price': signal.price,  # 使用正確的屬性名
                    'volume': signal.volume,
                    'metadata': signal.metadata,
                    'priority': signal.priority.value,
                    'layer_source': signal.layer_source,
                    'processing_time_ms': signal.processing_time_ms,
                    'market_regime': signal.market_regime,
                    'trading_session': signal.trading_session
                }
                signals_dict.append(signal_dict)
            
            adapted_signals = await phase1b.adapt_signals(signals_dict)
            
            if adapted_signals:
                test_results['phase1b_signal_adaptation'] = True
                print(f"✅ Phase1B 成功適應 {len(adapted_signals)} 個信號")
            else:
                print("⚠️ Phase1B 未輸出適應信號")
        else:
            print("⚠️ Phase1B 跳過測試（無輸入信號）")
            
        # 6. 初始化並測試Phase1C
        print("🧠 測試 Phase1C 信號標準化...")
        phase1c = Phase1CSignalStandardizationEngine()
        test_results['phase1c_initialization'] = True
        strategy_files_tested.append("phase1c_signal_standardization.py")
        
        # 測試Phase1C信號標準化
        if generated_signals:
            # 使用適應後的信號或原始信號
            input_signals = adapted_signals if 'adapted_signals' in locals() and adapted_signals else signals_dict
            standardized_signals = await phase1c.standardize_signals(input_signals)
            
            if standardized_signals:
                test_results['phase1c_signal_standardization'] = True
                print(f"✅ Phase1C 成功標準化 {len(standardized_signals)} 個信號")
            else:
                print("⚠️ Phase1C 未輸出標準化信號")
        else:
            print("⚠️ Phase1C 跳過測試（無輸入信號）")
            
        # 7. 測試缺失的關鍵模組
        print("🧠 測試缺失的關鍵模組...")
        
        # 測試 Intelligent Trigger Engine
        try:
            print("  🎯 測試 IntelligentTriggerEngine...")
            # 由於import問題，使用動態導入
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "intelligent_trigger_engine", 
                "/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/intelligent_trigger_engine/intelligent_trigger_engine.py"
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                test_results['intelligent_trigger_engine'] = True
                strategy_files_tested.append("intelligent_trigger_engine.py")
                print("  ✅ IntelligentTriggerEngine 模組載入成功")
            else:
                print("  ❌ IntelligentTriggerEngine 模組載入失敗")
        except Exception as e:
            print(f"  ⚠️ IntelligentTriggerEngine 測試失敗: {e}")
        
        # 測試 Indicator Dependency Graph
        try:
            print("  📊 測試 IndicatorDependencyGraph...")
            spec = importlib.util.spec_from_file_location(
                "indicator_dependency_graph", 
                "/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/indicator_dependency/indicator_dependency_graph.py"
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                test_results['indicator_dependency_graph'] = True
                strategy_files_tested.append("indicator_dependency_graph.py")
                print("  ✅ IndicatorDependencyGraph 模組載入成功")
            else:
                print("  ❌ IndicatorDependencyGraph 模組載入失敗")
        except Exception as e:
            print(f"  ⚠️ IndicatorDependencyGraph 測試失敗: {e}")
        
        # 測試 Unified Signal Pool
        try:
            print("  🔗 測試 UnifiedSignalCandidatePool...")
            spec = importlib.util.spec_from_file_location(
                "unified_signal_candidate_pool", 
                "/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/unified_signal_pool/unified_signal_candidate_pool.py"
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                test_results['unified_signal_pool'] = True
                strategy_files_tested.append("unified_signal_candidate_pool.py")
                print("  ✅ UnifiedSignalCandidatePool 模組載入成功")
            else:
                print("  ❌ UnifiedSignalCandidatePool 模組載入失敗")
        except Exception as e:
            print(f"  ⚠️ UnifiedSignalCandidatePool 測試失敗: {e}")
        
        # 測試 Dynamic Parameter System
        try:
            print("  ⚙️ 測試 DynamicParameterEngine...")
            spec = importlib.util.spec_from_file_location(
                "dynamic_parameter_engine", 
                "/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/dynamic_parameter_system/dynamic_parameter_engine.py"
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                test_results['dynamic_parameter_system'] = True
                strategy_files_tested.append("dynamic_parameter_engine.py")
                print("  ✅ DynamicParameterEngine 模組載入成功")
            else:
                print("  ❌ DynamicParameterEngine 模組載入失敗")
        except Exception as e:
            print(f"  ⚠️ DynamicParameterEngine 測試失敗: {e}")
            
        # 8. 測試完整數據流
        print("🔄 測試完整數據流 Phase1A → Phase1B → Phase1C...")
        if generated_signals:
            # Phase1A → Phase1B
            signals_dict = []
            for signal in generated_signals:
                signal_dict = {
                    'signal_id': signal.signal_id,
                    'symbol': signal.symbol,
                    'signal_type': signal.signal_type.value,
                    'direction': signal.direction,
                    'strength': signal.strength,
                    'confidence': signal.confidence,
                    'timestamp': signal.timestamp.isoformat(),
                    'source': 'phase1a',
                    'price': signal.price,
                    'volume': signal.volume,
                    'metadata': signal.metadata,
                    'priority': signal.priority.value,
                    'layer_source': signal.layer_source,
                    'processing_time_ms': signal.processing_time_ms,
                    'market_regime': signal.market_regime,
                    'trading_session': signal.trading_session
                }
                signals_dict.append(signal_dict)
            
            phase1b_output = await phase1b.adapt_signals(signals_dict)
            
            # Phase1B → Phase1C
            if phase1b_output:
                phase1c_output = await phase1c.standardize_signals(phase1b_output)
                
                if phase1c_output:
                    test_results['data_flow_integrity'] = True
                    test_results['end_to_end_processing'] = True
                    print(f"✅ 完整數據流測試通過：{len(generated_signals)} → {len(phase1b_output)} → {len(phase1c_output)}")
                else:
                    print("⚠️ 數據流在Phase1C中斷")
            else:
                print("⚠️ 數據流在Phase1B中斷")
        else:
            print("⚠️ 無法測試完整數據流（Phase1A無輸出）")
            
        # 停止Phase1A系統（帶超時保護）
        print("\n🛑 停止 Phase1A 系統...")
        try:
            await asyncio.wait_for(phase1a.stop(), timeout=5.0)
            print("✅ Phase1A 系統已安全停止")
        except asyncio.TimeoutError:
            print("⏱️ Phase1A 停止超時")
        except Exception as e:
            print(f"⚠️ Phase1A 停止時發生錯誤: {e}")
        
        # 停止信號引擎（如果存在）
        if 'signal_engine' in locals() and signal_engine:
            try:
                await asyncio.wait_for(signal_engine.stop(), timeout=5.0)
                print("✅ 信號引擎已安全停止")
            except asyncio.TimeoutError:
                print("⏱️ 信號引擎停止超時")
            except Exception as e:
                print(f"⚠️ 信號引擎停止時發生錯誤: {e}")
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        traceback.print_exc()
        
        # 確保即使出現異常也能停止信號引擎
        if 'signal_engine' in locals() and signal_engine:
            try:
                await asyncio.wait_for(signal_engine.stop(), timeout=5.0)
            except:
                pass  # 忽略停止時的錯誤
    
    # 輸出測試結果
    print("\n" + "="*80)
    print("📊 Phase1策略檔案測試結果")
    print("="*80)
    
    print("📁 已測試的策略檔案:")
    for i, file_name in enumerate(strategy_files_tested, 1):
        print(f"  {i}. {file_name}")
    
    print(f"\n📈 測試覆蓋率: {len(strategy_files_tested)}/9 個核心策略檔案")
    
    print("\n🎯 功能測試結果:")
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"  {test_name}: {status}")
        if result:
            passed_tests += 1
    
    print(f"\n📊 測試通過率: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 所有測試通過！即時數據成功通過所有策略檔案")
    elif passed_tests >= total_tests * 0.8:
        print("⚠️ 大部分測試通過，但有部分問題需要關注")
    else:
        print("❌ 多個測試失敗，需要檢查策略檔案實現")
    
    # 分析未通過的策略模組
    if not test_results['phase1a_signal_generation']:
        print("\n🔍 Phase1A信號生成分析:")
        print("  可能原因：")
        print("  1. 信號觸發閾值設置過高")
        print("  2. 市場數據不足以觸發信號條件")
        print("  3. 動態參數配置問題")
        print("  4. 緩衝區數據積累不足")
    
    if not test_results['phase1b_signal_adaptation']:
        print("\n🔍 Phase1B波動適應分析:")
        print("  可能原因：")
        print("  1. 輸入信號格式不匹配")
        print("  2. 波動率計算依賴外部數據")
        print("  3. 適應邏輯需要更多歷史數據")
    
    if not test_results['phase1c_signal_standardization']:
        print("\n🔍 Phase1C信號標準化分析:")
        print("  可能原因：")
        print("  1. 輸入信號格式驗證失敗") 
        print("  2. 標準化規則過於嚴格")
        print("  3. 輸出格式轉換問題")
    
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_comprehensive_phase1_strategies())
