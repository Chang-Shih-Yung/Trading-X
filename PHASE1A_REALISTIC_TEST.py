"""
Phase1A 實際工作方式測試
基於真實的信號生成機制和要求
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from dataclasses import asdict
import traceback
import json

# 添加路徑
sys.path.append('/Users/henrychang/Desktop/Trading-X')
sys.path.append('/Users/henrychang/Desktop/Trading-X/X/backend')

# 導入真實系統組件
from X.app.services.market_data import MarketDataService

# 導入Phase1A真實模組
from X.backend.phase1_signal_generation.phase1a_basic_signal_generation.phase1a_basic_signal_generation import (
    Phase1ABasicSignalGeneration, 
    MarketData,
    BasicSignal
)

class MockWebSocketDriver:
    """模擬 WebSocket 驅動程序"""
    def __init__(self):
        self.subscribers = []
        
    def subscribe(self, callback):
        """訂閱數據更新"""
        self.subscribers.append(callback)
        print(f"✅ WebSocket 驅動已註冊回調: {callback.__name__}")
        
    async def simulate_price_updates(self, symbol: str, count: int = 25):
        """模擬價格更新來建立數據緩衝區"""
        print(f"📊 為 {symbol} 模擬 {count} 個價格更新...")
        
        base_price = 50000 if symbol == 'BTCUSDT' else 3000
        
        for i in range(count):
            # 生成模擬價格數據
            price_change = (i % 5 - 2) * 0.002  # -0.4% 到 +0.4% 的變化
            current_price = base_price * (1 + price_change)
            
            price_data = {
                'symbol': symbol,
                'price': current_price,
                'volume': 1000000 + (i * 50000),
                'timestamp': datetime.now() - timedelta(seconds=(count-i)*10)
            }
            
            # 通知所有訂閱者
            for callback in self.subscribers:
                try:
                    await callback('ticker', type('TickerData', (), price_data)())
                except Exception as e:
                    print(f"⚠️ 回調失敗: {e}")
            
            # 小延遲模擬真實數據流
            await asyncio.sleep(0.01)
        
        print(f"✅ {symbol} 數據緩衝區建立完成")

async def test_phase1a_realistic():
    """測試 Phase1A 的實際工作方式"""
    print("🎯 Phase1A 實際工作方式測試")
    print("="*60)
    
    test_results = {
        'phase1a_initialization': False,
        'websocket_driver_setup': False,
        'phase1a_startup': False,
        'data_buffer_creation': False,
        'signal_generation_layer0': False,
        'signal_generation_layer1': False,
        'signal_generation_layer2': False,
        'signal_generation_layer3': False,
        'signal_generation_total': False
    }
    
    try:
        # 1. 初始化 Phase1A
        print("🧠 初始化 Phase1A...")
        phase1a = Phase1ABasicSignalGeneration()
        test_results['phase1a_initialization'] = True
        print("✅ Phase1A 初始化成功")
        
        # 2. 創建 WebSocket 驅動
        print("📡 設置 WebSocket 驅動...")
        websocket_driver = MockWebSocketDriver()
        test_results['websocket_driver_setup'] = True
        print("✅ WebSocket 驅動設置完成")
        
        # 3. 啟動 Phase1A（這是關鍵步驟！）
        print("🚀 啟動 Phase1A 系統...")
        await phase1a.start(websocket_driver)
        test_results['phase1a_startup'] = True
        print("✅ Phase1A 系統啟動成功")
        
        # 4. 建立數據緩衝區
        print("📊 建立數據緩衝區...")
        test_symbol = 'BTCUSDT'
        
        # 模擬足夠的價格更新來滿足各層要求
        await websocket_driver.simulate_price_updates(test_symbol, 25)
        test_results['data_buffer_creation'] = True
        
        # 等待數據處理
        await asyncio.sleep(0.5)
        
        # 檢查緩衝區狀態
        buffer_size = len(phase1a.price_buffer[test_symbol])
        print(f"📈 {test_symbol} 緩衝區大小: {buffer_size}")
        
        if buffer_size >= 2:
            print("✅ Layer 0 數據要求滿足 (>= 2)")
        if buffer_size >= 14:
            print("✅ Layer 2 數據要求滿足 (>= 14)")
        if buffer_size >= 20:
            print("✅ Layer 3 數據要求滿足 (>= 20)")
        
        # 5. 手動觸發信號生成 - 使用正確的格式
        print("🎯 測試信號生成...")
        
        # 創建符合要求的 MarketData
        market_data = MarketData(
            timestamp=datetime.now(),
            price=51000.0,  # 比基準價格高2%，應該觸發信號
            volume=2000000,
            price_change_1h=0.02,  # 2% 變化，超過預設閾值0.1%
            price_change_24h=0.05,
            volume_ratio=2.0,  # 2倍成交量，超過預設閾值1.5
            volatility=0.03,
            fear_greed_index=65,
            bid_ask_spread=0.01,
            market_depth=1000000,
            moving_averages={'ma_20': 50500.0}
        )
        
        # 呼叫信號生成
        generated_signals = await phase1a.generate_signals(test_symbol, market_data)
        
        print(f"📊 生成信號數量: {len(generated_signals)}")
        
        if generated_signals:
            test_results['signal_generation_total'] = True
            print("✅ 成功生成信號！")
            
            # 分析信號詳情
            for i, signal in enumerate(generated_signals):
                print(f"  信號 {i+1}:")
                print(f"    類型: {signal.signal_type}")
                print(f"    方向: {signal.direction}")
                print(f"    強度: {signal.strength:.3f}")
                print(f"    信心度: {signal.confidence:.3f}")
                print(f"    來源層: {getattr(signal, 'layer_id', '未知')}")
        else:
            print("⚠️ 未生成信號 - 讓我們分析原因...")
            
            # 檢查系統狀態
            print(f"🔍 系統診斷:")
            print(f"  - is_running: {phase1a.is_running}")
            print(f"  - 緩衝區大小: {len(phase1a.price_buffer[test_symbol])}")
            print(f"  - 成交量緩衝區: {len(phase1a.volume_buffer[test_symbol])}")
            
            # 嘗試獲取動態參數
            try:
                dynamic_params = await phase1a._get_dynamic_parameters("basic_mode")
                print(f"  - 價格變化閾值: {dynamic_params.price_change_threshold}")
                print(f"  - 成交量變化閾值: {dynamic_params.volume_change_threshold}")
                print(f"  - 信心度閾值: {dynamic_params.confidence_threshold}")
            except Exception as e:
                print(f"  - 動態參數獲取失敗: {e}")
        
        # 6. 測試強制觸發條件
        print("\n🔥 測試強制觸發條件...")
        
        # 創建極端市場數據
        extreme_market_data = MarketData(
            timestamp=datetime.now(),
            price=52000.0,  # 4% 價格變化
            volume=5000000,  # 5倍成交量
            price_change_1h=0.04,  # 4% 變化
            price_change_24h=0.08,  # 8% 日變化
            volume_ratio=5.0,  # 5倍成交量比率
            volatility=0.05,
            fear_greed_index=80,
            bid_ask_spread=0.02,
            market_depth=2000000,
            moving_averages={'ma_20': 50000.0}
        )
        
        extreme_signals = await phase1a.generate_signals(test_symbol, extreme_market_data)
        
        if extreme_signals:
            print(f"✅ 極端條件下生成 {len(extreme_signals)} 個信號")
            test_results['signal_generation_total'] = True
        else:
            print("❌ 即使在極端條件下也未生成信號")
        
        # 7. 停止系統
        print("\n🛑 停止 Phase1A 系統...")
        await phase1a.stop()
        print("✅ Phase1A 系統已停止")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        traceback.print_exc()
    
    # 8. 輸出結果
    print("\n" + "="*60)
    print("📊 測試結果摘要")
    print("="*60)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"  {test_name}: {status}")
    
    print(f"\n📈 通過率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    # 9. 分析和建議
    print("\n🔍 分析和建議:")
    
    if not test_results['signal_generation_total']:
        print("🔧 可能的解決方案:")
        print("  1. 檢查動態參數配置檔案")
        print("  2. 確認市場制度檢測是否正常")
        print("  3. 驗證價格變化計算邏輯")
        print("  4. 檢查信號過濾條件")
        print("  5. 確認 is_running 狀態")
        
        print("\n🎯 下一步行動:")
        print("  1. 修改 COMPREHENSIVE_PHASE1_STRATEGY_TEST.py")
        print("  2. 實現正確的 Phase1A 啟動序列") 
        print("  3. 建立適當的數據緩衝區")
        print("  4. 使用正確的信號生成API")
    else:
        print("🎉 Phase1A 信號生成機制正常工作！")
        print("📋 可以將此邏輯應用到主測試中")

if __name__ == "__main__":
    asyncio.run(test_phase1a_realistic())
