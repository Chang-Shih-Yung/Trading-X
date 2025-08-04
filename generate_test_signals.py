#!/usr/bin/env python3
"""
🔧 生成測試信號腳本 - 用於前端測試
"""

import asyncio
import sys
sys.path.append('.')

from app.services.sniper_smart_layer import sniper_smart_layer
from datetime import datetime, timedelta
import random

async def generate_test_signals():
    """生成測試信號"""
    test_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
    
    print("🔧 開始生成測試信號...")
    
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
        confidence = random.uniform(0.75, 0.95)
        
        test_signal = {
            "signal_id": f"test_{symbol}_{int(now.timestamp())}",
            "symbol": symbol,
            "signal_type": signal_type,
            "entry_price": round(entry_price, 4),
            "stop_loss": round(stop_loss, 4),
            "take_profit": round(take_profit, 4),
            "confidence": round(confidence, 3),
            "quality_score": round(quality_score, 1),
            "priority_rank": random.randint(1, 3),
            "timeframe": "1h",
            "reasoning": f"🎯 狙擊手測試信號 - {symbol}\n\n📊 技術分析:\n• 品質評分: {quality_score:.1f}/10.0\n• 信心度: {confidence*100:.1f}%\n• 風險回報比: {abs(take_profit-entry_price)/abs(entry_price-stop_loss):.1f}:1\n\n💡 這是系統生成的測試信號，展示狙擊手智能分層功能。",
            "technical_indicators": [
                f"🎯 智能分層 (1h)",
                f"⭐ 品質評分: {quality_score:.1f}",
                f"🏆 優先級排名: #{random.randint(1, 3)}",
                "📊 RSI 信號", "📈 MACD 交叉", "🔍 布林帶突破"
            ],
            "sniper_metrics": {
                "layer_one_time": round(random.uniform(0.008, 0.015), 3),
                "layer_two_time": round(random.uniform(0.015, 0.025), 3),
                "pass_rate": round(random.uniform(0.8, 0.95), 2),
                "precision": round(random.uniform(0.9, 0.98), 2),
                "market_regime": random.choice(["BULL_TREND", "CONSOLIDATION", "VOLATILE"])
            },
            "created_at": now.isoformat(),
            "expires_at": (now + timedelta(hours=3)).isoformat()
        }
        
        try:
            await sniper_smart_layer._save_test_signal(test_signal)
            print(f"✅ {symbol} 測試信號已生成 (品質評分: {quality_score:.1f})")
        except Exception as e:
            print(f"❌ {symbol} 測試信號生成失敗: {e}")
    
    print(f"\n🎯 測試信號生成完成！現在可以刷新前端頁面查看信號。")

if __name__ == "__main__":
    asyncio.run(generate_test_signals())
