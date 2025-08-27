#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Trading X 量子模型完整歷史數據訓練啟動器
=========================================

這個腳本專門用於啟動「七大幣種從創世以來的所有歷史數據」訓練。

核心功能：
- 自動整合量子級區塊鏈數據撷取器
- 從各幣種的真實創世日期開始獲取完整歷史數據
- 訓練七大幣種的量子模型：BTC, ETH, ADA, SOL, XRP, DOGE, BNB
- 顯示完整的數據範圍統計

用法：
    python launch_complete_training.py

作者: Trading X Quantum Team
版本: 1.0 - 完整歷史數據訓練版
"""

import asyncio
import logging
import os
import sys
from datetime import datetime

# 設置路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir))

# 配置日誌
log_filename = f'complete_training_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_filename, encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def display_banner():
    """顯示啟動橫幅"""
    print("🌌" + "=" * 70 + "🌌")
    print("🚀       Trading X 量子模型完整歷史數據訓練器")
    print("🔮       From Genesis to Present - Complete Data Training")
    print("🌌" + "=" * 70 + "🌌")
    print()
    print("💫 特色功能:")
    print("   🧬 量子級區塊鏈數據撷取器整合")
    print("   📊 真實創世日期歷史數據獲取")
    print("   🔮 七大幣種量子模型訓練")
    print("   ⚡ 多源數據融合技術")
    print()

def show_data_scope():
    """顯示數據範圍信息"""
    try:
        from blockchain_unlimited_extractor import ProductionConfig
        config = ProductionConfig()
        
        print("📊 各幣種完整歷史數據範圍:")
        print("-" * 50)
        
        for coin, genesis_date in config.REAL_GENESIS_DATES.items():
            days_since_genesis = (datetime.now() - genesis_date).days
            years = days_since_genesis / 365.25
            print(f"   🪙 {coin:4}: {genesis_date.strftime('%Y-%m-%d')} 至今")
            print(f"        📈 {days_since_genesis:,} 天 ({years:.1f} 年)")
            print()
            
        # 計算總數據點
        total_days = sum((datetime.now() - date).days for date in config.REAL_GENESIS_DATES.values())
        print(f"💎 總數據範圍: {total_days:,} 天跨越所有幣種")
        print(f"🏆 這是真正的「從創世以來」完整歷史數據訓練！")
        
    except ImportError:
        print("⚠️ 無法載入配置，將使用預設數據範圍")

async def main():
    """主執行函數"""
    display_banner()
    show_data_scope()
    
    print("\n🚀 準備啟動完整歷史數據訓練...")
    
    # 確認用戶意圖
    print("\n⚠️ 注意事項:")
    print("   • 此訓練將使用大量網絡頻寬獲取歷史數據")
    print("   • 預計訓練時間: 2-4 小時（取決於網絡速度）")
    print("   • 建議在穩定網絡環境下運行")
    print("   • 訓練過程中請勿關閉程序")
    
    confirm = input("\n🔮 確認開始完整歷史數據訓練? (y/N): ").strip().lower()
    
    if confirm not in ['y', 'yes', '是', '确认']:
        print("❌ 訓練已取消")
        return
    
    print("\n🌟 啟動量子模型訓練器...")
    
    try:
        # 導入並運行訓練器
        from quantum_model_trainer import train_with_complete_historical_data
        
        logger.info("🚀 開始完整歷史數據訓練")
        results = await train_with_complete_historical_data()
        
        # 顯示最終統計
        print("\n" + "🏆" * 60)
        print("🎉 完整歷史數據訓練任務完成！")
        print("🏆" * 60)
        
        successful_coins = [coin for coin, result in results.items() if result.get('status') == 'success']
        total_coins = len(results)
        
        print(f"\n📊 最終統計:")
        print(f"   ✅ 成功訓練: {len(successful_coins)}/{total_coins} 個幣種")
        print(f"   🔮 模型類型: 量子神經網絡")
        print(f"   📈 數據來源: 真實創世歷史數據")
        print(f"   📝 訓練日誌: {log_filename}")
        
        if successful_coins:
            print(f"\n🎯 成功訓練的量子模型:")
            for coin in successful_coins:
                result = results[coin]
                data_points = result.get('data_points', 'N/A')
                accuracy = result.get('test_accuracy', 'N/A')
                print(f"   🪙 {coin}: {data_points:,} 數據點, 準確率: {accuracy:.3f}")
        
        print(f"\n💫 恭喜！您已成功完成「七大幣種從創世以來」的量子模型訓練！")
        
    except ImportError as e:
        logger.error(f"❌ 無法導入訓練器: {e}")
        print(f"❌ 錯誤：請確保在正確的目錄下運行此腳本")
    except Exception as e:
        logger.error(f"❌ 訓練過程發生錯誤: {e}")
        print(f"❌ 訓練失敗: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ 用戶中斷訓練")
    except Exception as e:
        print(f"\n❌ 程序異常: {e}")
        logger.error(f"程序異常: {e}")
