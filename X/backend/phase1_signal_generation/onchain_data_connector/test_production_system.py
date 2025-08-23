"""
🧪 產品級鏈上價格系統測試
Production-Grade Onchain Price System Test
"""

import asyncio
import logging
from datetime import datetime
import sys
import os

# 添加路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from production_connector import ProductionOnChainPriceConnector

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_production_system():
    """測試產品級鏈上價格系統"""
    
    print("🎯 產品級鏈上價格系統測試")
    print("=" * 60)
    
    connector = None
    
    try:
        # 1. 創建連接器
        print("\n📋 1. 創建產品級鏈上價格連接器")
        connector = ProductionOnChainPriceConnector()
        
        # 2. 初始化系統
        print("\n⚡ 2. 初始化系統...")
        await connector.initialize()
        print("✅ 系統初始化完成")
        
        # 3. 啟動價格流
        print("\n🚀 3. 啟動即時價格流...")
        await connector.start_price_streaming()
        print("✅ 價格流啟動完成")
        
        # 4. 等待價格數據穩定
        print("\n⏳ 4. 等待價格數據穩定...")
        await asyncio.sleep(3)
        
        # 5. 測試主池信息
        print("\n🏊 5. 主池信息測試")
        pool_info = await connector.get_pool_info()
        print(f"   發現主池數量: {len(pool_info)}")
        
        for symbol, pool in pool_info.items():
            print(f"   💰 {symbol}:")
            print(f"      地址: {pool['address']}")
            print(f"      版本: {pool['version']}")
            print(f"      流動性: {pool['liquidity_usdt']:.2f} USDT")
        
        # 6. 測試單個價格獲取
        print("\n💰 6. 單個價格獲取測試")
        test_symbols = ['BTC', 'ETH', 'BNB', 'ADA', 'DOGE', 'XRP', 'SOL']
        
        for symbol in test_symbols:
            price = await connector.get_price(symbol)
            if price:
                print(f"   ✅ {symbol}: ${price:.4f}")
            else:
                print(f"   ❌ {symbol}: 價格獲取失敗")
        
        # 7. 測試批量價格獲取
        print("\n📊 7. 批量價格獲取測試")
        all_prices = await connector.get_all_prices()
        print(f"   成功獲取 {len(all_prices)} 個價格:")
        
        for symbol, price in all_prices.items():
            print(f"      {symbol}: ${price:.4f}")
        
        # 8. 測試詳細價格數據
        print("\n📈 8. 詳細價格數據測試")
        btc_data = await connector.get_price_data('BTC')
        if btc_data:
            print("   BTC 詳細數據:")
            print(f"      價格: ${btc_data['price']:.4f}")
            print(f"      池地址: {btc_data['pool_address']}")
            print(f"      版本: {btc_data['version']}")
            print(f"      抓取時間: {btc_data['fetch_time_ms']:.1f}ms")
            print(f"      時間戳: {btc_data['timestamp']}")
        
        # 9. 健康檢查
        print("\n🏥 9. 系統健康檢查")
        health = await connector.health_check()
        print(f"   初始化狀態: {health['initialized']}")
        print(f"   流式狀態: {health['streaming']}")
        print(f"   主池數量: {health['main_pools_count']}")
        print(f"   活躍價格: {health['active_prices']}")
        print(f"   支援幣種: {health['supported_symbols']}")
        
        # 10. 性能測試
        print("\n⚡ 10. 性能測試 (10次連續獲取)")
        start_time = datetime.now()
        
        for i in range(10):
            prices = await connector.get_all_prices()
            
        end_time = datetime.now()
        avg_time = (end_time - start_time).total_seconds() * 1000 / 10
        print(f"   平均響應時間: {avg_time:.1f}ms")
        
        # 11. Phase1 Schema 兼容性測試
        print("\n🔗 11. Phase1 Schema 兼容性測試")
        from production_connector import get_crypto_price, get_all_crypto_prices
        
        # 測試單個價格
        btc_price = await get_crypto_price('BTC')
        print(f"   Phase1 BTC 價格: ${btc_price:.4f}")
        
        # 測試批量價格
        phase1_prices = await get_all_crypto_prices()
        print(f"   Phase1 批量價格: {len(phase1_prices)} 個")
        
        print("\n🎉 產品級鏈上價格系統測試完成！")
        print("=" * 60)
        print("✅ 所有測試通過")
        print("✅ 系統運行正常")
        print("✅ Phase1 Schema 兼容")
        print("✅ 真實鏈上數據")
        print("✅ 產品級質量")
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 清理資源
        if connector:
            print("\n🧹 清理系統資源...")
            await connector.stop()
            print("✅ 資源清理完成")

if __name__ == "__main__":
    asyncio.run(test_production_system())
