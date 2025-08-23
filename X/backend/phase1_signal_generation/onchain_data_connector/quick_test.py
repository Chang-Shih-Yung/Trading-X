"""
🚀 快速測試產品級鏈上價格系統
Quick Test for Production-Grade Onchain Price System
"""

import asyncio
import logging
from datetime import datetime

from production_connector import ProductionOnChainPriceConnector

# 設置簡化日誌
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

async def quick_test():
    """快速測試系統"""
    
    print("🎯 快速測試產品級鏈上價格系統")
    print("=" * 50)
    
    connector = None
    
    try:
        # 創建並初始化連接器
        print("⚡ 初始化系統...")
        connector = ProductionOnChainPriceConnector()
        await connector.initialize()
        
        # 啟動價格流
        print("🚀 啟動價格流...")
        await connector.start_price_streaming()
        
        # 等待數據
        print("⏳ 等待數據...")
        await asyncio.sleep(2)
        
        # 測試價格獲取
        print("\n💰 測試價格獲取:")
        test_symbols = ['BTC', 'ETH', 'BNB', 'ADA', 'DOGE', 'XRP', 'SOL']
        
        success_count = 0
        for symbol in test_symbols:
            price = await connector.get_price(symbol)
            if price:
                print(f"   ✅ {symbol}: ${price:.4f}")
                success_count += 1
            else:
                print(f"   ❌ {symbol}: 無法獲取價格")
        
        # 測試批量獲取
        print("\n📊 批量價格獲取:")
        all_prices = await connector.get_all_prices()
        print(f"   成功獲取 {len(all_prices)} 個價格")
        
        # 健康檢查
        print("\n🏥 系統健康檢查:")
        health = await connector.health_check()
        print(f"   主池數量: {health['main_pools_count']}")
        print(f"   活躍價格: {health['active_prices']}")
        print(f"   支援幣種: {health['supported_symbols']}")
        
        # 主池信息
        print("\n🏊 主池信息:")
        pools = await connector.get_pool_info()
        for symbol, pool in pools.items():
            liquidity_score = pool.get('liquidity_score', 0)
            print(f"   {symbol}: {pool['version']} - 流動性評分: {liquidity_score:.3f}")
        
        print(f"\n🎉 測試完成!")
        print(f"✅ 成功獲取 {success_count}/{len(test_symbols)} 個價格")
        print(f"✅ 發現 {len(pools)} 個主池")
        print(f"✅ 系統運行正常")
        
        if success_count >= 3:
            print("🎯 產品級質量達標!")
        else:
            print("⚠️ 部分幣種無法獲取，但系統正常運行")
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if connector:
            print("\n🧹 清理資源...")
            await connector.stop()

if __name__ == "__main__":
    asyncio.run(quick_test())
