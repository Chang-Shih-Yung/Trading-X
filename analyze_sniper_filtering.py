#!/usr/bin/env python3
"""
狙擊手策略信號篩選分析報告
分析當前的信號生成、篩選和顯示流程
"""

import asyncio
import sys
sys.path.append('.')

async def analyze_sniper_signal_filtering():
    print("🎯 狙擊手策略信號篩選分析報告")
    print("=" * 80)
    
    try:
        # 1. 檢查數據庫中的原始信號數據
        print("\n📊 第一部分：數據庫原始信號分析")
        
        from app.core.database import get_db
        from app.models.sniper_signal_history import SniperSignalDetails, SignalStatus
        from sqlalchemy import select, func, desc
        from datetime import timedelta
        from app.utils.timezone_utils import get_taiwan_now
        
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        try:
            # 查詢總信號統計
            total_result = await db.execute(
                select(func.count(SniperSignalDetails.id))
            )
            total_signals = total_result.scalar() or 0
            
            # 查詢各狀態信號
            status_result = await db.execute(
                select(
                    SniperSignalDetails.status,
                    func.count(SniperSignalDetails.id)
                ).group_by(SniperSignalDetails.status)
            )
            
            print(f"   數據庫總信號數: {total_signals}")
            print("   狀態分佈:")
            for status, count in status_result.fetchall():
                print(f"     {status.value}: {count} 個")
            
            # 查詢品質評分分佈
            quality_result = await db.execute(
                select(
                    SniperSignalDetails.symbol,
                    SniperSignalDetails.signal_quality,
                    func.count(SniperSignalDetails.id)
                ).group_by(
                    SniperSignalDetails.symbol,
                    SniperSignalDetails.signal_quality
                )
            )
            
            print("\n   品質評分分佈:")
            quality_stats = {}
            for symbol, quality, count in quality_result.fetchall():
                if symbol not in quality_stats:
                    quality_stats[symbol] = {}
                quality_stats[symbol][quality.value] = count
            
            for symbol, qualities in quality_stats.items():
                print(f"     {symbol}:")
                for quality, count in qualities.items():
                    print(f"       {quality}: {count} 個")
            
            # 查詢最近24小時的信號
            recent_24h = get_taiwan_now() - timedelta(hours=24)
            recent_result = await db.execute(
                select(func.count(SniperSignalDetails.id))
                .where(SniperSignalDetails.created_at >= recent_24h)
            )
            recent_signals = recent_result.scalar() or 0
            print(f"\n   最近24小時信號: {recent_signals} 個")
            
            # 查詢最新10個信號的詳細信息
            latest_result = await db.execute(
                select(
                    SniperSignalDetails.symbol,
                    SniperSignalDetails.signal_type,
                    SniperSignalDetails.signal_strength,
                    SniperSignalDetails.signal_quality,
                    SniperSignalDetails.status,
                    SniperSignalDetails.created_at
                ).order_by(desc(SniperSignalDetails.created_at))
                .limit(10)
            )
            
            print("\n   最新10個信號詳情:")
            for i, signal in enumerate(latest_result.fetchall(), 1):
                print(f"     {i}. {signal.symbol} {signal.signal_type} "
                      f"強度:{signal.signal_strength:.2f} 品質:{signal.signal_quality.value} "
                      f"狀態:{signal.status.value} {signal.created_at}")
        
        finally:
            await db_gen.aclose()
        
        # 2. 分析API篩選邏輯
        print(f"\n🔍 第二部分：API篩選邏輯分析")
        
        # 測試API篩選功能
        import aiohttp
        import json
        
        async with aiohttp.ClientSession() as session:
            # 測試不同的篩選參數
            test_params = [
                {"quality_threshold": 0.0, "strategy_mode": "comprehensive"},
                {"quality_threshold": 4.0, "strategy_mode": "precision"},
                {"quality_threshold": 6.0, "strategy_mode": "precision"},
                {"quality_threshold": 8.0, "strategy_mode": "precision"}
            ]
            
            for params in test_params:
                try:
                    url = "http://localhost:8000/api/v1/sniper/smart-layer-signals"
                    async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=5)) as response:
                        if response.status == 200:
                            data = await response.json()
                            signal_count = data.get('total_count', 0)
                            quality_dist = data.get('quality_distribution', {})
                            
                            print(f"   篩選參數 {params}:")
                            print(f"     返回信號數: {signal_count}")
                            print(f"     品質分佈: 高={quality_dist.get('high', 0)} "
                                  f"中={quality_dist.get('medium', 0)} 低={quality_dist.get('low', 0)}")
                        else:
                            print(f"   篩選參數 {params}: API錯誤 {response.status}")
                except asyncio.TimeoutError:
                    print(f"   篩選參數 {params}: 請求超時")
                except Exception as e:
                    print(f"   篩選參數 {params}: 錯誤 {e}")
        
        # 3. 分析篩選關鍵點
        print(f"\n⚙️ 第三部分：篩選關鍵點分析")
        
        print("   篩選流程:")
        print("   1. 信號生成階段:")
        print("      - 執行狙擊手分析 (_execute_sniper_analysis)")
        print("      - 品質評分計算 (quality_analyzer.calculate_quality_score)")
        print("      - 品質閾值篩選 (_get_quality_threshold)")
        print("      - 當前閾值: 短線=4.0, 中線=4.3, 長線=4.6")
        
        print("   2. API返回階段:")
        print("      - 獲取活躍信號 (get_all_active_signals)")
        print("      - 時間優先篩選 (precision模式)")
        print("      - 幣種篩選 (symbols參數)")
        print("      - 品質閾值篩選 (quality_threshold參數，默認6.0)")
        print("      - 每幣種限制 (max_signals_per_symbol參數)")
        
        print("   3. 前端顯示階段:")
        print("      - 精準策略時間篩選 (10秒>1分鐘>5分鐘>15分鐘)")
        print("      - 品質分佈統計")
        print("      - 優先級排序")
        
        # 4. 問題診斷
        print(f"\n🔧 第四部分：問題診斷")
        
        print("   前端顯示0的可能原因:")
        print("   1. ❌ 雙重品質篩選問題:")
        print("      - 生成時篩選: 4.0-4.6 (較寬鬆)")
        print("      - API篩選: 6.0 (較嚴格)")
        print("      - 導致生成的信號被API再次過濾掉")
        
        print("   2. ❌ 時間篩選過於嚴格:")
        print("      - 精準策略優先10秒內信號")
        print("      - 但信號生成間隔可能大於10秒")
        print("      - 導致大部分信號被時間篩選淘汰")
        
        print("   3. ❌ 狀態管理問題:")
        print("      - 信號可能快速過期或被標記為非活躍")
        print("      - get_all_active_signals 返回空列表")
        
        print("   4. ❌ 模擬數據問題:")
        print("      - _execute_sniper_analysis 使用隨機模擬")
        print("      - 可能生成品質過低的信號")
        
        print(f"\n💡 第五部分：建議修復方案")
        
        print("   1. 調整API默認品質閾值:")
        print("      - 從 6.0 降低到 4.0")
        print("      - 與生成階段閾值保持一致")
        
        print("   2. 放寬時間篩選條件:")
        print("      - 將10秒擴展到5分鐘")
        print("      - 或允許用戶選擇時間範圍")
        
        print("   3. 增加統計透明度:")
        print("      - API返回原始信號數 vs 篩選後信號數")
        print("      - 顯示篩選過程的詳細信息")
        
        print("   4. 改善信號生成質量:")
        print("      - 替換模擬數據為真實技術分析")
        print("      - 調整品質評分算法")
        
        print("\n✅ 分析完成")
        
    except Exception as e:
        print(f"❌ 分析失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(analyze_sniper_signal_filtering())
