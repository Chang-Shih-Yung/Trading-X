#!/usr/bin/env python3
"""
檢查 Trading-X 系統的數據流程
確認前端顯示的數據是真實 pandas-ta 分析還是假資料
"""

import requests
import json
import time
from datetime import datetime, timedelta

def check_data_authenticity():
    """檢查數據真實性"""
    print("🔍 Trading-X 數據真實性檢查")
    print("=" * 70)
    
    base_url = "http://localhost:8000"
    
    # 1. 檢查 signals/latest 端點
    print("\n📊 檢查 /api/v1/signals/latest 端點")
    print("-" * 50)
    
    try:
        response = requests.get(f"{base_url}/api/v1/signals/latest?hours=24")
        if response.status_code == 200:
            signals = response.json()
            
            if signals:
                signal = signals[0]
                print(f"✅ 找到 {len(signals)} 個信號")
                print(f"📈 樣本信號:")
                print(f"   - 幣種: {signal.get('symbol')}")
                print(f"   - 分析內容: {signal.get('reasoning', '無')[:50]}...")
                print(f"   - 信心度: {signal.get('confidence')}")
                print(f"   - 創建時間: {signal.get('created_at')}")
                
                # 檢查分析內容是否為模板
                reasoning = signal.get('reasoning', '')
                if '【' in reasoning and '】' in reasoning and '多時間軸確認' in reasoning:
                    print("⚠️  這是 **模板/假資料** - 包含固定格式的技術分析模板")
                    return "fake_data"
                else:
                    print("✅ 可能是真實分析 - 內容看起來不像模板")
            else:
                print("❌ 沒有信號")
                
    except Exception as e:
        print(f"❌ API 調用失敗: {e}")
    
    # 2. 檢查 scalping/signals 端點
    print("\n🎯 檢查 /api/v1/scalping/signals 端點")
    print("-" * 50)
    
    try:
        response = requests.get(f"{base_url}/api/v1/scalping/signals")
        if response.status_code == 200:
            data = response.json()
            signals = data.get('signals', [])
            
            if signals:
                print(f"✅ 找到 {len(signals)} 個精準信號")
                
                signal = signals[0]
                print(f"📈 精準信號樣本:")
                print(f"   - 幣種: {signal.get('symbol')}")
                print(f"   - 策略: {signal.get('strategy_name')}")
                print(f"   - 信心度: {signal.get('confidence')}")
                print(f"   - 精準度: {signal.get('precision_score')}")
                print(f"   - 分析: {signal.get('reasoning', '無')[:50]}...")
                
                # 檢查是否為實時生成
                created_at = signal.get('created_at')
                if created_at:
                    signal_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    time_diff = datetime.now().astimezone() - signal_time.astimezone()
                    
                    if time_diff.total_seconds() < 3600:  # 1小時內
                        print("✅ 信號較新，可能是實時生成")
                        return "recent_analysis"
                    else:
                        print(f"⚠️  信號較舊 ({time_diff})")
                        
            else:
                print("❌ 沒有精準信號")
                return "no_signals"
                
    except Exception as e:
        print(f"❌ API 調用失敗: {e}")
    
    # 3. 檢查是否有 pandas-ta 服務運行
    print("\n🔬 檢查 pandas-ta 整合狀態")
    print("-" * 50)
    
    try:
        # 嘗試直接測試 pandas-ta 功能
        import sys
        sys.path.append('/Users/henrychang/Desktop/Trading-X')
        
        from app.services.pandas_ta_indicators import PandasTAIndicators
        
        # 創建測試實例
        ta_service = PandasTAIndicators()
        print("✅ pandas-ta 服務可以實例化")
        
        # 檢查是否有即時數據
        from app.services.market_data import MarketDataService
        market_service = MarketDataService()
        
        # 嘗試獲取數據
        print("🔍 檢查實時市場數據...")
        
        return "pandas_ta_available"
        
    except Exception as e:
        print(f"❌ pandas-ta 服務檢查失敗: {e}")
        return "pandas_ta_unavailable"

def check_realtime_engine():
    """檢查實時引擎狀態"""
    print("\n⚡ 檢查實時信號引擎狀態")
    print("-" * 50)
    
    try:
        import sys
        sys.path.append('/Users/henrychang/Desktop/Trading-X')
        
        from app.services.realtime_signal_engine import RealtimeSignalEngine
        
        # 檢查引擎配置
        engine = RealtimeSignalEngine()
        print("✅ 實時信號引擎可以實例化")
        print(f"📊 監控幣種: {engine.monitored_symbols}")
        
        # 檢查引擎是否在運行
        if hasattr(engine, 'running'):
            print(f"🔄 引擎運行狀態: {engine.running}")
        
        return True
        
    except Exception as e:
        print(f"❌ 實時信號引擎檢查失敗: {e}")
        return False

def main():
    """主函數"""
    print("🚀 開始檢查 Trading-X 系統數據流程...")
    print("🎯 確認前端顯示的是真實 pandas-ta 分析還是假資料")
    print()
    
    # 數據真實性檢查
    data_status = check_data_authenticity()
    
    # 實時引擎檢查
    engine_status = check_realtime_engine()
    
    # 總結報告
    print("\n" + "=" * 70)
    print("📋 數據流程檢查報告")
    print("=" * 70)
    
    if data_status == "fake_data":
        print("❌ **結論: 前端顯示的是假資料/模板數據**")
        print("🔧 建議:")
        print("   1. 啟動實時信號引擎")
        print("   2. 確保 WebSocket → pandas-ta → 信號生成 流程運行")
        print("   3. 修改前端 API 調用，使用真實分析結果")
        
    elif data_status == "recent_analysis":
        print("✅ **結論: 前端顯示的可能是真實分析**")
        print("📊 信號較新，符合實時分析特徵")
        
    elif data_status == "no_signals":
        print("⚠️  **結論: 沒有活躍的信號數據**")
        print("🔧 建議: 啟動信號生成流程")
        
    elif data_status == "pandas_ta_available":
        print("✅ **pandas-ta 服務可用**")
        print("🔧 需要檢查是否正確整合到 API 端點")
        
    else:
        print("❓ **狀態不明確，需要進一步檢查**")
    
    if not engine_status:
        print("\n⚠️  **實時信號引擎未運行**")
        print("💡 這可能是前端顯示假資料的原因")
    
    print("\n🎯 **關鍵問題**: 需要確認實時分析流程是否正在運行")
    print("📝 **建議**: 檢查主程序是否啟動了 WebSocket → pandas-ta → 信號廣播 流程")

if __name__ == "__main__":
    main()
