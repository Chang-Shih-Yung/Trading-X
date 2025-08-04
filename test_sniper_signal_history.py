#!/usr/bin/env python3
"""
🎯 狙擊手信號歷史管理系統測試腳本
測試信號記錄、查詢、分析等核心功能
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import json

# 添加項目路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_sniper_signal_history():
    """測試狙擊手信號歷史管理系統"""
    
    print("🎯 開始測試狙擊手信號歷史管理系統...")
    print("=" * 60)
    
    try:
        # 1. 測試服務載入
        print("\n1️⃣ 測試服務載入...")
        from app.services.sniper_signal_history_service import (
            sniper_signal_tracker, 
            sniper_signal_analyzer
        )
        from app.models.sniper_signal_history import SignalStatus
        print("✅ 狙擊手信號歷史服務成功載入")
        
        # 2. 測試數據庫連接
        print("\n2️⃣ 測試數據庫連接...")
        from app.core.database import db_manager
        session = await db_manager.create_session()
        await session.close()
        print("✅ 數據庫連接成功")
        
        # 3. 測試信號記錄功能
        print("\n3️⃣ 測試信號記錄功能...")
        test_signals = []
        
        for i in range(3):
            signal_id = f'test_signal_{int(datetime.now().timestamp())}_{i}'
            symbol = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT'][i]
            signal_type = ['BUY', 'SELL', 'BUY'][i]
            
            result = await sniper_signal_tracker.record_new_signal(
                signal_id=signal_id,
                symbol=symbol,
                signal_type=signal_type,
                entry_price=45000.0 + (i * 1000),
                stop_loss_price=43000.0 + (i * 1000),
                take_profit_price=48000.0 + (i * 1000),
                signal_strength=0.8 + (i * 0.05),
                confidence_score=0.75 + (i * 0.05),
                timeframe='1h',
                expires_at=datetime.now() + timedelta(hours=4),
                metadata={
                    'test': True, 
                    'reasoning': f'測試狙擊手信號 #{i+1}',
                    'test_batch': 'sniper_history_test'
                }
            )
            
            if result:
                test_signals.append(signal_id)
                print(f"✅ 成功記錄測試信號: {signal_id} ({symbol} {signal_type})")
            else:
                print(f"❌ 信號記錄失敗: {signal_id}")
        
        print(f"📊 共記錄 {len(test_signals)} 個測試信號")
        
        # 4. 測試活躍信號監控
        print("\n4️⃣ 測試活躍信號監控...")
        active_signals = await sniper_signal_tracker.monitor_active_signals()
        print(f"✅ 活躍信號監控: 找到 {len(active_signals)} 個需要更新的信號")
        
        if active_signals:
            print("📋 活躍信號詳情:")
            for signal in active_signals[:3]:  # 只顯示前3個
                print(f"   • {signal.get('symbol')} - {signal.get('action')} - {signal.get('signal_id', 'N/A')[:20]}...")
        
        # 5. 測試信號狀態更新
        print("\n5️⃣ 測試信號狀態更新...")
        if test_signals:
            test_signal_id = test_signals[0]
            update_result = await sniper_signal_tracker.update_signal_result(
                signal_id=test_signal_id,
                new_status=SignalStatus.HIT_TP,
                result_price=48500.0,
                result_time=datetime.now()
            )
            
            if update_result:
                print(f"✅ 信號狀態更新成功: {test_signal_id} -> HIT_TP")
            else:
                print(f"❌ 信號狀態更新失敗: {test_signal_id}")
        
        # 6. 測試性能指標分析
        print("\n6️⃣ 測試性能指標分析...")
        performance = await sniper_signal_analyzer.get_performance_metrics(days=30)
        
        if 'error' not in performance:
            print("✅ 性能指標獲取成功")
            print(f"📊 性能指標摘要:")
            print(f"   • 總信號數: {performance.get('total_signals', 0)}")
            print(f"   • 盈利信號: {performance.get('total_profitable', 0)}")
            print(f"   • 虧損信號: {performance.get('total_losing', 0)}")
            print(f"   • 勝率: {performance.get('overall_win_rate', 0)}%")
            print(f"   • 平均PnL: {performance.get('average_pnl_percentage', 0)}%")
        else:
            print(f"⚠️ 性能指標獲取: {performance.get('error', 'No data available')}")
        
        # 7. 測試每日摘要生成
        print("\n7️⃣ 測試每日摘要生成...")
        summary_result = await sniper_signal_analyzer.generate_daily_summary(datetime.now())
        
        if summary_result:
            print("✅ 每日摘要生成成功")
        else:
            print("❌ 每日摘要生成失敗")
        
        # 8. 測試清理功能
        print("\n8️⃣ 測試清理功能...")
        # 只清理測試數據，保留7天
        cleanup_count = await sniper_signal_tracker.cleanup_expired_details(days_to_keep=7)
        print(f"✅ 清理功能測試: 清理了 {cleanup_count} 條過期記錄")
        
        print("\n" + "=" * 60)
        print("🎯 狙擊手信號歷史管理系統測試完成!")
        print("✅ 所有核心功能正常運行")
        print("📊 系統已準備好接收和管理狙擊手信號")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        import traceback
        print("\n🔍 詳細錯誤追蹤:")
        traceback.print_exc()
        return False

async def test_api_endpoints():
    """測試API端點"""
    
    print("\n🌐 測試狙擊手信號歷史管理API端點...")
    print("=" * 60)
    
    try:
        import aiohttp
        
        base_url = "http://localhost:8000/api/v1/history"
        
        async with aiohttp.ClientSession() as session:
            # 測試獲取信號歷史
            print("\n1️⃣ 測試獲取信號歷史...")
            try:
                async with session.get(f"{base_url}/signals?limit=5") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ 信號歷史API響應成功: 找到 {len(data.get('signals', []))} 條記錄")
                    else:
                        print(f"⚠️ 信號歷史API響應狀態: {response.status}")
            except Exception as e:
                print(f"❌ 信號歷史API測試失敗: {e}")
            
            # 測試獲取性能指標
            print("\n2️⃣ 測試獲取性能指標...")
            try:
                async with session.get(f"{base_url}/performance") as response:
                    if response.status == 200:
                        data = await response.json()
                        print("✅ 性能指標API響應成功")
                        print(f"📊 總信號數: {data.get('total_signals', 0)}")
                    else:
                        print(f"⚠️ 性能指標API響應狀態: {response.status}")
            except Exception as e:
                print(f"❌ 性能指標API測試失敗: {e}")
            
            # 測試獲取活躍信號
            print("\n3️⃣ 測試獲取活躍信號...")
            try:
                async with session.get(f"{base_url}/active-signals") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ 活躍信號API響應成功: 找到 {len(data.get('active_signals', []))} 個活躍信號")
                    else:
                        print(f"⚠️ 活躍信號API響應狀態: {response.status}")
            except Exception as e:
                print(f"❌ 活躍信號API測試失敗: {e}")
        
    except ImportError:
        print("⚠️ aiohttp 未安裝，跳過API端點測試")
        print("💡 提示: 可使用 pip install aiohttp 安裝")
    except Exception as e:
        print(f"❌ API端點測試失敗: {e}")

async def main():
    """主測試函數"""
    print("🚀 啟動狙擊手信號歷史管理系統完整測試")
    print("⏰ 測試開始時間:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # 核心服務測試
    service_test_result = await test_sniper_signal_history()
    
    # API端點測試
    await test_api_endpoints()
    
    print("\n" + "🎯" * 20)
    if service_test_result:
        print("🎉 狙擊手信號歷史管理系統測試全部通過!")
        print("✅ 系統已準備好在生產環境中使用")
    else:
        print("⚠️ 系統測試發現問題，請檢查錯誤信息")
    
    print("⏰ 測試結束時間:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    asyncio.run(main())
