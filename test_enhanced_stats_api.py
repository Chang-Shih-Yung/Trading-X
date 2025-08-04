#!/usr/bin/env python3
"""
測試增強統計API端點
"""

import asyncio
import aiohttp
import json
import sys
sys.path.append('.')

async def test_enhanced_stats_api():
    print("🧪 測試增強統計API端點...")
    
    try:
        base_url = "http://localhost:8000"
        
        # 測試1: 基本統計端點
        print("\n📊 測試1: 基本統計查詢")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/api/v1/sniper/smart-layer-signals") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   狀態: {data.get('status')}")
                    print(f"   信號數: {data.get('total_count', 0)}")
                    
                    quality_dist = data.get('quality_distribution', {})
                    print(f"   品質分佈: 高={quality_dist.get('high', 0)}, 中={quality_dist.get('medium', 0)}, 低={quality_dist.get('low', 0)}")
                else:
                    print(f"   ❌ API錯誤: {response.status}")
        
        # 測試2: 直接調用增強統計功能
        print("\n📈 測試2: 直接調用增強統計")
        from app.services.sniper_smart_layer import sniper_smart_layer
        
        # 測試增強的績效統計
        perf_stats = await sniper_smart_layer._get_performance_statistics()
        
        print(f"   總信號: {perf_stats.get('total_signals', 0)}")
        print(f"   傳統勝率: {perf_stats.get('traditional_win_rate', 0):.1f}%")
        print(f"   真實成功率: {perf_stats.get('real_success_rate', 0):.1f}%")
        print(f"   平均收益: {perf_stats.get('average_pnl', 0):.2f}%")
        print(f"   總收益: {perf_stats.get('total_pnl', 0):.2f}%")
        print(f"   盈虧比: {perf_stats.get('profit_factor', 0):.2f}")
        
        # 檢查時間段分析
        recent_7 = perf_stats.get('recent_7days', {})
        recent_30 = perf_stats.get('recent_30days', {})
        
        print(f"   近7天: {recent_7.get('signals', 0)} 信號, 平均PnL {recent_7.get('avg_pnl', 0):.2f}%")
        print(f"   近30天: {recent_30.get('signals', 0)} 信號, 平均PnL {recent_30.get('avg_pnl', 0):.2f}%")
        
        # 測試3: 風險指標
        print("\n🛡️ 測試3: 風險指標")
        risk_metrics = await sniper_smart_layer._calculate_risk_metrics()
        
        print(f"   最大收益: {risk_metrics.get('max_gain', 0):.2f}%")
        print(f"   最大虧損: {risk_metrics.get('max_loss', 0):.2f}%")
        print(f"   波動率: {risk_metrics.get('volatility', 0):.2f}%")
        print(f"   風險回報比: {risk_metrics.get('risk_reward_ratio', 0):.2f}")
        print(f"   樣本數: {risk_metrics.get('sample_size', 0)}")
        
        # 測試4: 實時價格獲取
        print("\n💰 測試4: 實時價格獲取")
        test_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
        
        for symbol in test_symbols[:2]:  # 只測試前2個避免過多請求
            price = await sniper_smart_layer._get_realtime_price(symbol)
            if price:
                print(f"   {symbol}: ${price:,.2f}")
            else:
                print(f"   {symbol}: 價格獲取失敗")
        
        # 測試5: 完整增強統計
        print("\n🚀 測試5: 完整增強統計")
        try:
            enhanced_stats = await sniper_smart_layer.get_enhanced_statistics()
            
            print(f"   狀態: {enhanced_stats.get('status')}")
            print(f"   版本: {enhanced_stats.get('version')}")
            
            perf_metrics = enhanced_stats.get('performance_metrics', {})
            print(f"   傳統勝率: {perf_metrics.get('traditional_win_rate', 0):.1f}%")
            print(f"   真實成功率: {perf_metrics.get('real_success_rate', 0):.1f}%")
            print(f"   夏普比率: {perf_metrics.get('sharpe_ratio', 0):.2f}")
            
            realtime_data = enhanced_stats.get('realtime_monitoring', {})
            active_positions = realtime_data.get('active_positions', {})
            print(f"   實時監控: {len(active_positions)} 個活躍信號")
            
            for symbol, data in list(active_positions.items())[:3]:
                current_pnl = data.get('current_pnl', 0)
                print(f"     {symbol}: 當前PnL {current_pnl:+.2f}%")
                
        except Exception as e:
            print(f"   ❌ 完整統計測試失敗: {e}")
        
        print("\n✅ 所有API測試完成")
        
    except Exception as e:
        print(f"❌ API測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_enhanced_stats_api())
