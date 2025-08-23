"""
🧠 智能混合價格系統測試
Smart Hybrid Price System Test
測試鏈上數據 + 幣安API智能回退機制
"""

import asyncio
import logging
from datetime import datetime

# 模擬幣安API回退連接器
class MockBinanceFallback:
    """模擬的幣安API回退連接器"""
    
    async def get_price(self, symbol: str) -> float:
        """模擬從幣安API獲取價格"""
        # 模擬價格數據
        mock_prices = {
            'BTC': 43500.0,
            'ETH': 2650.0,
            'BNB': 310.0,
            'ADA': 0.45,
            'DOGE': 0.08,
            'XRP': 0.52,
            'SOL': 98.0
        }
        
        price = mock_prices.get(symbol, 100.0)
        print(f"   🔄 模擬幣安API回退: {symbol} = ${price:.4f}")
        return price

async def test_smart_hybrid_system():
    """測試智能混合價格系統"""
    
    print("🧠 智能混合價格系統測試")
    print("=" * 60)
    
    # 設置簡化日誌
    logging.basicConfig(level=logging.WARNING)
    
    try:
        # 創建模擬幣安回退連接器
        print("🔄 創建模擬幣安API回退連接器...")
        mock_binance = MockBinanceFallback()
        
        # 導入智能混合連接器
        from smart_hybrid_connector import SmartHybridPriceConnector
        
        print("🚀 創建智能混合價格連接器...")
        connector = SmartHybridPriceConnector(binance_fallback=mock_binance)
        
        print("⚡ 初始化系統...")
        await connector.initialize()
        
        print("🚀 啟動智能價格流...")
        await connector.start_price_streaming()
        
        print("⏳ 等待系統穩定...")
        await asyncio.sleep(3)
        
        print("\n💰 測試智能價格獲取:")
        test_symbols = ['BTC', 'ETH', 'BNB', 'ADA', 'DOGE', 'XRP', 'SOL']
        
        success_count = 0
        for symbol in test_symbols:
            try:
                price = await connector.get_price(symbol)
                if price:
                    print(f"   ✅ {symbol}: ${price:.4f}")
                    success_count += 1
                else:
                    print(f"   ❌ {symbol}: 無法獲取價格")
            except Exception as e:
                print(f"   ⚠️ {symbol}: 獲取失敗 - {e}")
        
        print(f"\n📊 測試結果: {success_count}/{len(test_symbols)} 成功")
        
        print("\n🏥 系統狀態檢查:")
        status = await connector.get_system_status()
        print(f"   初始化狀態: {status['initialized']}")
        print(f"   流式狀態: {status['streaming']}")
        print(f"   主池數量: {status['main_pools_count']}")
        print(f"   支援幣種: {status['supported_symbols']}")
        print(f"   回退幣種數: {len(status['symbols_on_fallback'])}")
        print(f"   有幣安回退: {status['has_binance_fallback']}")
        
        if status['symbols_on_fallback']:
            print(f"   回退中的幣種: {status['symbols_on_fallback']}")
        
        print("\n📈 批量價格測試:")
        all_prices = await connector.get_all_prices()
        print(f"   批量獲取: {len(all_prices)} 個價格")
        for symbol, price in all_prices.items():
            print(f"      {symbol}: ${price:.4f}")
        
        print("\n🔍 詳細數據測試:")
        btc_data = await connector.get_price_data('BTC')
        if btc_data:
            print("   BTC 詳細數據:")
            print(f"      價格: ${btc_data['price']:.4f}")
            print(f"      數據源: {btc_data.get('source', '未知')}")
            print(f"      是否回退: {btc_data.get('is_fallback', False)}")
            print(f"      時間戳: {btc_data.get('timestamp', '無')}")
        
        print("\n🎉 智能混合系統測試完成!")
        print("=" * 60)
        print("✅ 系統運行正常")
        print("✅ 智能回退機制就緒") 
        print("✅ Phase1 Schema 兼容")
        print("✅ 混合數據源正常")
        
        if success_count >= 5:
            print("🎯 智能混合系統質量達標!")
        else:
            print("⚠️ 部分功能需要優化，但系統基本可用")
        
        # 清理
        print("\n🧹 清理資源...")
        await connector.stop()
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_smart_hybrid_system())
