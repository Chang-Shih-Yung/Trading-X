"""
Phase 2 簡化測試 - 檢查動態權重系統基礎
"""
import requests
import json

def test_phase2_simple():
    """簡化版 Phase 2 測試"""
    print("🚀 Phase 2 簡化測試：動態權重系統基礎")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # 1. 檢查現有的 pandas-ta 是否支援動態參數
    print("1️⃣ 檢查 pandas-ta 動態參數支援")
    print("-" * 30)
    
    try:
        response = requests.get(f"{base_url}/api/v1/scalping/pandas-ta-direct", timeout=8)
        if response.status_code == 200:
            data = response.json()
            phase = data.get('phase', '')
            improvements = data.get('improvements', [])
            
            print(f"✅ pandas-ta 引擎運行中")
            print(f"📊 當前階段: {phase}")
            print(f"🔧 增強功能數量: {len(improvements)}")
            
            # 檢查是否有動態權重相關功能
            weight_features = [imp for imp in improvements if any(
                keyword in str(imp).lower() 
                for keyword in ['權重', 'weight', '動態', 'dynamic', '適應', 'adaptive']
            )]
            
            if weight_features:
                print(f"🎯 發現權重相關功能: {len(weight_features)} 項")
                for feature in weight_features[:3]:
                    print(f"   - {feature}")
            else:
                print(f"⏳ 權重系統功能待開發")
                
        else:
            print(f"❌ pandas-ta 引擎訪問失敗")
            
    except Exception as e:
        print(f"❌ 測試錯誤: {str(e)[:50]}")
    
    # 2. 檢查市場狀態適應功能
    print(f"\n2️⃣ 檢查市場狀態適應功能")
    print("-" * 30)
    
    adaptation_tests = [
        ("enhanced/market-regime", "市場機制識別"),
        ("enhanced/fear-greed-index", "Fear & Greed 指數"),
        ("realtime/market-analysis", "即時市場分析")
    ]
    
    adaptation_score = 0
    for endpoint, name in adaptation_tests:
        try:
            response = requests.get(f"{base_url}/api/v1/{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} - 端點可用")
                adaptation_score += 1
            elif response.status_code == 404:
                print(f"⏳ {name} - 待開發")
            else:
                print(f"⚠️ {name} - 狀態異常")
        except:
            print(f"❌ {name} - 無法訪問")
    
    # 3. 檢查動態參數調整能力
    print(f"\n3️⃣ 檢查動態參數調整能力")
    print("-" * 30)
    
    try:
        # 測試不同時間框架的響應
        timeframes = ["1m", "5m", "1h"]
        dynamic_responses = 0
        
        for tf in timeframes:
            try:
                response = requests.get(
                    f"{base_url}/api/v1/scalping/pandas-ta-direct?timeframe={tf}", 
                    timeout=6
                )
                if response.status_code == 200:
                    data = response.json()
                    if 'phase' in data and 'Phase 2' in str(data.get('phase', '')):
                        print(f"✅ {tf} 時間框架參數支援")
                        dynamic_responses += 1
                    else:
                        print(f"⚠️ {tf} 時間框架基礎支援")
                else:
                    print(f"❌ {tf} 時間框架訪問失敗")
            except:
                print(f"⏰ {tf} 時間框架請求超時")
        
        if dynamic_responses >= 2:
            print(f"🎯 動態參數系統基礎良好")
        else:
            print(f"⏳ 動態參數系統需要加強")
            
    except Exception as e:
        print(f"❌ 動態參數測試錯誤: {str(e)[:50]}")
    
    # Phase 2 狀態總結
    print(f"\n" + "=" * 50)
    print("📊 Phase 2 動態權重系統狀態總結")
    print("=" * 50)
    
    # 基於測試結果評估
    base_system = 1 if 'pandas-ta 引擎運行中' in locals() else 0
    adaptation_ready = 1 if adaptation_score >= 1 else 0
    dynamic_ready = 1 if dynamic_responses >= 1 else 0
    
    total_score = base_system + adaptation_ready + dynamic_ready
    
    print(f"🧠 核心引擎: {'✅' if base_system else '❌'}")
    print(f"🎯 市場適應: {'✅' if adaptation_ready else '❌'}")
    print(f"⚙️ 動態參數: {'✅' if dynamic_ready else '❌'}")
    
    if total_score >= 2:
        print(f"\n🎉 Phase 2 基礎架構就緒！")
        print(f"📋 建議：開始實現具體的動態權重算法")
        print(f"🚀 準備進入 Phase 3 事件驅動增強")
    elif total_score >= 1:
        print(f"\n⚠️ Phase 2 部分功能需要完善")
        print(f"📋 建議：補強市場適應和動態參數功能")
    else:
        print(f"\n🔧 Phase 2 需要更多開發工作")
        print(f"📋 建議：先穩固 pandas-ta 核心引擎")
    
    return total_score

if __name__ == "__main__":
    test_phase2_simple()
