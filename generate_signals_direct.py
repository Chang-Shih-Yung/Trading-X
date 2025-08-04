#!/usr/bin/env python3
"""
通過HTTP API生成測試信號
"""

import requests
import json
import random
from datetime import datetime, timedelta

def generate_test_signals_via_api():
    """通過API生成測試信號"""
    base_url = "http://localhost:8000"
    test_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
    
    print("🔧 通過HTTP API生成測試信號...")
    
    for symbol in test_symbols:
        # 生成測試信號數據
        now = datetime.now()
        
        # 隨機基礎價格
        base_prices = {"BTCUSDT": 50000, "ETHUSDT": 3000, "ADAUSDT": 0.5}
        base_price = base_prices.get(symbol, 1)
        current_price = base_price * (1 + random.uniform(-0.03, 0.03))
        
        signal_type = random.choice(["BUY", "SELL"])
        
        if signal_type == "BUY":
            entry_price = current_price
            stop_loss = entry_price * 0.97
            take_profit = entry_price * 1.06
        else:
            entry_price = current_price
            stop_loss = entry_price * 1.03
            take_profit = entry_price * 0.94
        
        quality_score = random.uniform(7.0, 9.5)
        
        # 直接調用內部方法來添加信號
        test_data = {
            "symbol": symbol,
            "signal_type": signal_type,
            "entry_price": round(entry_price, 4),
            "stop_loss": round(stop_loss, 4),
            "take_profit": round(take_profit, 4),
            "quality_score": round(quality_score, 1)
        }
        
        print(f"🎯 生成 {symbol} 測試信號: {signal_type}, 品質評分: {quality_score:.1f}")

if __name__ == "__main__":
    # 直接修改服務實例
    import sys
    sys.path.append('.')
    
    from app.services.sniper_smart_layer import sniper_smart_layer, SmartSignal, TimeframeCategory
    import asyncio
    
    async def add_signals_directly():
        """直接添加信號到服務實例"""
        symbols_data = [
            {"symbol": "BTCUSDT", "price": 50000, "type": "SELL", "quality": 8.5},
            {"symbol": "ETHUSDT", "price": 3000, "type": "BUY", "quality": 7.8},
            {"symbol": "ADAUSDT", "price": 0.5, "type": "BUY", "quality": 9.1}
        ]
        
        for data in symbols_data:
            symbol = data["symbol"]
            base_price = data["price"]
            signal_type = data["type"]
            quality_score = data["quality"]
            
            current_price = base_price * (1 + random.uniform(-0.02, 0.02))
            
            if signal_type == "BUY":
                entry_price = current_price
                stop_loss = entry_price * 0.97
                take_profit = entry_price * 1.06
            else:
                entry_price = current_price
                stop_loss = entry_price * 1.03
                take_profit = entry_price * 0.94
            
            now = datetime.now()
            
            smart_signal = SmartSignal(
                symbol=symbol,
                signal_id=f"direct_{symbol}_{int(now.timestamp())}",
                signal_type=signal_type,
                entry_price=round(entry_price, 4),
                stop_loss=round(stop_loss, 4),
                take_profit=round(take_profit, 4),
                confidence=round(random.uniform(0.75, 0.95), 3),
                timeframe_category=TimeframeCategory.SHORT_TERM,
                quality_score=quality_score,
                priority_rank=random.randint(1, 3),
                reasoning=f"🎯 直接生成的測試信號 - {symbol}\n\n📊 技術分析:\n• 品質評分: {quality_score}/10.0\n• 信號類型: {signal_type}\n• 風險回報比: {abs(take_profit-entry_price)/abs(entry_price-stop_loss):.1f}:1\n\n💡 這是為前端測試直接生成的信號。",
                technical_indicators=[
                    f"🎯 智能分層 (1h)",
                    f"⭐ 品質評分: {quality_score}",
                    f"🏆 優先級排名: #{random.randint(1, 3)}",
                    "📊 RSI 信號", "📈 MACD 交叉"
                ],
                sniper_metrics={
                    "layer_one_time": round(random.uniform(0.008, 0.015), 3),
                    "layer_two_time": round(random.uniform(0.015, 0.025), 3),
                    "pass_rate": round(random.uniform(0.8, 0.95), 2),
                    "precision": round(random.uniform(0.9, 0.98), 2),
                    "market_regime": random.choice(["BULL_TREND", "CONSOLIDATION"])
                },
                created_at=now,
                expires_at=now + timedelta(hours=3)
            )
            
            # 直接添加到活躍信號字典
            sniper_smart_layer.active_signals[symbol] = smart_signal
            print(f"✅ {symbol} 測試信號已直接添加 (品質評分: {quality_score})")
        
        print(f"\n🎯 現在活躍信號數量: {len(sniper_smart_layer.active_signals)}")
    
    asyncio.run(add_signals_directly())
    generate_test_signals_via_api()
