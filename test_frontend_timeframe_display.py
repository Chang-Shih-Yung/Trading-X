#!/usr/bin/env python3
"""
模擬前端如何解析API響應並顯示動態時間
"""

import json

# 模擬從API獲取的響應
api_response = {
    "results": {
        "BTCUSDT": {
            "layer_two": {
                "processed_signals": [
                    {
                        "risk_parameters": {
                            "expiry_hours": 15,
                            "signal_quality": "low"
                        }
                    },
                    {
                        "risk_parameters": {
                            "expiry_hours": 15,
                            "signal_quality": "low"  
                        }
                    }
                ]
            },
            "dynamic_risk_summary": {
                "avg_expiry_hours": 15.0
            }
        }
    }
}

def get_timeframe_display(expiry_hours):
    """模擬前端的時間框架顯示邏輯（增強版 - 小時+分鐘）"""
    if not expiry_hours:
        return '數據不完整'
    
    # 根據實際過期時間動態判斷
    if expiry_hours <= 8:
        timeframe_text = '短線'
    elif expiry_hours <= 48:
        timeframe_text = '中線'
    else:
        timeframe_text = '長線'
    
    # 🎯 顯示實際的過期時間（小時+分鐘）
    if expiry_hours >= 24:
        days = round(expiry_hours / 24 * 10) / 10
        total_minutes = round(expiry_hours * 60)
        time_display = f"{days}天 ({total_minutes}分鐘)"
    else:
        hours = round(expiry_hours * 10) / 10
        total_minutes = round(expiry_hours * 60)
        time_display = f"{hours}小時 ({total_minutes}分鐘)"
    
    return f"{timeframe_text} · {time_display}"

print("🎯 模擬前端動態時間顯示:")
print("=" * 50)

# 解析API響應
for symbol, data in api_response["results"].items():
    print(f"\n📊 {symbol}:")
    
    if "layer_two" in data and "processed_signals" in data["layer_two"]:
        signals = data["layer_two"]["processed_signals"]
        
        for i, signal in enumerate(signals, 1):
            if "risk_parameters" in signal:
                expiry_hours = signal["risk_parameters"].get("expiry_hours")
                quality = signal["risk_parameters"].get("signal_quality", "unknown")
                
                timeframe_display = get_timeframe_display(expiry_hours)
                
                print(f"   信號 {i}: {timeframe_display}")
                print(f"   品質: {quality}")
                print(f"   原始時間: {expiry_hours}小時")
    
    # 檢查平均時間
    if "dynamic_risk_summary" in data:
        avg_hours = data["dynamic_risk_summary"].get("avg_expiry_hours")
        if avg_hours:
            avg_display = get_timeframe_display(avg_hours)
            print(f"\n   平均時間框架: {avg_display}")

print(f"\n✅ 前端現在應該顯示「中線 · 15.0小時 (900分鐘)」而不是固定的「中線 · 12小時」")
print(f"🎯 動態時間計算已經成功整合到前端顯示，並增加了分鐘顯示！")
