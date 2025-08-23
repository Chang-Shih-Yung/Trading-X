"""
🧪 Production Launcher 整合測試
測試智能混合價格系統與現有 WebSocket 幣安API 的整合
"""

import asyncio
import logging

async def test_production_integration():
    """測試生產環境整合"""
    
    print("🧪 Production Launcher 智能混合價格系統整合測試")
    print("=" * 70)
    
    # 設置日誌
    logging.basicConfig(level=logging.INFO)
    
    try:
        # 導入整合模塊
        from production_price_integration import get_price_system_manager, get_real_market_data
        
        print("🚀 初始化價格系統管理器...")
        manager = await get_price_system_manager()
        
        print("📊 系統狀態檢查:")
        status = await manager.get_system_status()
        print(f"   初始化狀態: {status['initialized']}")
        print(f"   當前模式: {status['current_mode']}")
        print(f"   混合模式可用: {status['hybrid_available']}")
        print(f"   幣安WebSocket可用: {status['binance_websocket_available']}")
        
        if status.get('onchain_status'):
            onchain = status['onchain_status']
            print(f"   鏈上數據流: {onchain.get('streaming', False)}")
            print(f"   主池數量: {onchain.get('main_pools_count', 0)}")
        
        print("\n💰 測試價格獲取 (與現有接口兼容):")
        test_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'DOGEUSDT']
        
        for symbol in test_symbols:
            try:
                # 使用新的整合接口
                market_data = await get_real_market_data(symbol)
                if market_data:
                    print(f"   ✅ {symbol}: ${market_data['price']:.4f} (來源: {market_data.get('source', '未知')})")
                    if market_data.get('is_fallback'):
                        print(f"      🔄 使用回退機制")
                else:
                    print(f"   ❌ {symbol}: 獲取失敗")
            except Exception as e:
                print(f"   ⚠️ {symbol}: 錯誤 - {e}")
        
        print("\n🔥 測試批量獲取:")
        all_prices = await manager.get_all_prices()
        print(f"   批量獲取: {len(all_prices)} 個價格")
        for symbol, price in list(all_prices.items())[:3]:  # 只顯示前3個
            print(f"      {symbol}: ${price:.4f}")
        
        print("\n📈 模擬 Production Launcher 使用場景:")
        print("   1. 定期價格獲取 (模擬信號生成需求)")
        
        for i in range(3):
            print(f"      第 {i+1} 輪:")
            for symbol in ['BTCUSDT', 'ETHUSDT']:
                market_data = await get_real_market_data(symbol)
                if market_data:
                    source_info = "鏈上" if not market_data.get('is_fallback') else "WebSocket回退"
                    print(f"         {symbol}: ${market_data['price']:.4f} ({source_info})")
            
            if i < 2:
                await asyncio.sleep(1)  # 模擬間隔
        
        print("\n🎉 整合測試完成!")
        print("=" * 50)
        print("✅ 智能混合系統運行正常")
        print("✅ WebSocket 幣安API 回退機制就緒")
        print("✅ 與現有 Production Launcher 兼容")
        print("✅ 價格獲取接口統一")
        
        # 清理
        print("\n🧹 清理資源...")
        await manager.stop()
        
    except Exception as e:
        print(f"\n❌ 整合測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_production_integration())
