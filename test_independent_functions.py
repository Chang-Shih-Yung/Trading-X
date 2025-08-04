#!/usr/bin/env python3
"""
獨立測試增強統計功能 - 不依賴整個系統初始化
"""

import asyncio
import aiohttp
import sys
sys.path.append('.')

async def test_independent_functions():
    print("🧪 獨立測試增強統計功能...")
    
    try:
        # 測試1: 直接測試價格獲取
        print("\n📊 測試1: 價格獲取功能")
        
        async def get_price_api(symbol: str):
            """獨立的價格獲取函數"""
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return float(data['price'])
                    return None
        
        test_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
        prices = {}
        
        for symbol in test_symbols:
            price = await get_price_api(symbol)
            prices[symbol] = price
            print(f"   {symbol}: ${price:,.2f}")
        
        # 測試2: PnL計算
        print("\n📈 測試2: PnL計算功能")
        
        def calculate_pnl(entry_price: float, current_price: float, signal_type: str) -> float:
            """獨立的PnL計算函數"""
            if entry_price == 0 or current_price == 0:
                return 0.0
            
            if signal_type == 'BUY':
                pnl = ((current_price - entry_price) / entry_price) * 100
            else:  # SELL
                pnl = ((entry_price - current_price) / entry_price) * 100
            
            return round(pnl, 2)
        
        # 測試不同入場價格
        btc_price = prices.get('BTCUSDT', 100000)
        test_entries = [50000, 80000, 120000, 150000]
        
        for entry in test_entries:
            buy_pnl = calculate_pnl(entry, btc_price, 'BUY')
            sell_pnl = calculate_pnl(entry, btc_price, 'SELL')
            print(f"   入場 ${entry:,} -> 當前 ${btc_price:,}: BUY {buy_pnl:+.2f}%, SELL {sell_pnl:+.2f}%")
        
        # 測試3: 統計指標計算
        print("\n📊 測試3: 統計指標計算")
        
        def calculate_profit_factor(profitable_signals: int, unprofitable_signals: int, 
                                   total_profit: float, total_loss: float) -> float:
            """盈虧比計算"""
            if unprofitable_signals == 0 or total_loss == 0:
                return float('inf') if profitable_signals > 0 else 0.0
            return abs(total_profit / total_loss)
        
        def calculate_win_rates(tp_count: int, sl_count: int, expired_count: int, 
                               profitable_count: int, total_count: int) -> dict:
            """勝率計算"""
            completed = tp_count + sl_count + expired_count
            traditional_win_rate = (tp_count / completed * 100) if completed > 0 else 0.0
            real_success_rate = (profitable_count / total_count * 100) if total_count > 0 else 0.0
            
            return {
                'traditional_win_rate': round(traditional_win_rate, 2),
                'real_success_rate': round(real_success_rate, 2),
                'completion_rate': round((completed / total_count * 100) if total_count > 0 else 0, 2)
            }
        
        # 模擬統計數據
        test_stats = {
            'tp_signals': 25,
            'sl_signals': 15,
            'expired_signals': 10,
            'profitable_signals': 30,  # 基於PnL > 0
            'total_signals': 50,
            'total_profit': 450.5,
            'total_loss': -180.2
        }
        
        profit_factor = calculate_profit_factor(
            test_stats['profitable_signals'],
            test_stats['total_signals'] - test_stats['profitable_signals'],
            test_stats['total_profit'],
            test_stats['total_loss']
        )
        
        win_rates = calculate_win_rates(
            test_stats['tp_signals'],
            test_stats['sl_signals'],
            test_stats['expired_signals'],
            test_stats['profitable_signals'],
            test_stats['total_signals']
        )
        
        print(f"   傳統勝率: {win_rates['traditional_win_rate']:.1f}%")
        print(f"   真實成功率: {win_rates['real_success_rate']:.1f}%")
        print(f"   完成率: {win_rates['completion_rate']:.1f}%")
        print(f"   盈虧比: {profit_factor:.2f}")
        print(f"   平均收益: {test_stats['total_profit'] / test_stats['total_signals']:.2f}%")
        
        # 測試4: 數據庫統計
        print("\n💾 測試4: 數據庫統計查詢")
        
        from app.core.database import get_db
        from app.models.sniper_signal_history import SniperSignalDetails, SignalStatus
        from sqlalchemy import select, func
        
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        try:
            # 獲取真實的數據庫統計
            total_result = await db.execute(
                select(func.count(SniperSignalDetails.id))
            )
            total_signals = total_result.scalar() or 0
            
            status_result = await db.execute(
                select(
                    SniperSignalDetails.status,
                    func.count(SniperSignalDetails.id).label('count'),
                    func.avg(SniperSignalDetails.pnl_percentage).label('avg_pnl'),
                    func.sum(SniperSignalDetails.pnl_percentage).label('total_pnl')
                ).group_by(SniperSignalDetails.status)
            )
            
            print(f"   數據庫總信號: {total_signals}")
            
            real_profitable = 0
            real_total_pnl = 0.0
            
            for row in status_result.fetchall():
                status = row.status
                count = row.count
                avg_pnl = row.avg_pnl or 0.0
                total_pnl = row.total_pnl or 0.0
                
                print(f"   {status}: {count} 個, 平均PnL: {avg_pnl:.2f}%, 總PnL: {total_pnl:.2f}%")
                
                if avg_pnl > 0:
                    real_profitable += count
                real_total_pnl += total_pnl
            
            if total_signals > 0:
                real_success_rate = (real_profitable / total_signals) * 100
                avg_pnl = real_total_pnl / total_signals
                print(f"   真實成功率: {real_success_rate:.1f}%")
                print(f"   平均總收益: {avg_pnl:.2f}%")
                print(f"   盈利信號數: {real_profitable}")
        
        finally:
            await db_gen.aclose()
        
        print("\n✅ 所有獨立測試完成")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_independent_functions())
