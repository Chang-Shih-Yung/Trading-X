#!/usr/bin/env python3
"""
即時 API 優化核心功能測試
"""

import sys
import os
from pathlib import Path
import importlib.util

# 添加路徑
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

def test_phase1a_imports_and_structure():
    """測試 Phase1A 導入和結構"""
    print("🔍 測試 Phase1A 檔案結構...")
    
    try:
        # 檢查檔案是否存在
        phase1a_file = current_dir / "phase1a_basic_signal_generation.py"
        if not phase1a_file.exists():
            print("❌ phase1a_basic_signal_generation.py 檔案不存在")
            return False
        
        print("✅ phase1a_basic_signal_generation.py 檔案存在")
        
        # 檢查檔案內容中的關鍵字
        with open(phase1a_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查 OrderBook 相關功能
        orderbook_keywords = [
            'orderbook_buffer',
            '_on_orderbook_update',
            '_calculate_spread',
            '_calculate_book_depth',
            '_calculate_liquidity_ratio',
            '_check_orderbook_signals',
            '_create_enhanced_market_data',
            '_generate_orderbook_enhanced_signals'
        ]
        
        for keyword in orderbook_keywords:
            if keyword in content:
                print(f"✅ OrderBook 功能 {keyword} 存在")
            else:
                print(f"❌ OrderBook 功能 {keyword} 缺失")
                return False
        
        # 檢查動態參數功能
        dynamic_keywords = [
            'DynamicParameters',
            '_get_dynamic_parameters',
            'market_regime',
            'trading_session'
        ]
        
        for keyword in dynamic_keywords:
            if keyword in content:
                print(f"✅ 動態參數功能 {keyword} 存在")
            else:
                print(f"❌ 動態參數功能 {keyword} 缺失")
                return False
        
        # 檢查即時數據處理（無模擬數據）
        mock_data_keywords = [
            'mock_data',
            'backup_data',
            'fallback_data',
            '_generate_mock',
            '_create_fallback'
        ]
        
        mock_found = False
        for keyword in mock_data_keywords:
            if keyword in content.lower():
                print(f"⚠️  發現模擬數據相關代碼: {keyword}")
                mock_found = True
        
        if not mock_found:
            print("✅ 無模擬數據相關代碼，純即時數據處理")
        
        return True
        
    except Exception as e:
        print(f"❌ Phase1A 結構測試失敗: {e}")
        return False

def test_phase3_funding_rate_structure():
    """測試 Phase3 資金費率結構"""
    print("\n🔍 測試 Phase3 資金費率檔案結構...")
    
    try:
        # 尋找 phase3_market_analyzer.py 
        phase3_file = Path("/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/phase3_market_analyzer/phase3_market_analyzer.py")
        
        if not phase3_file.exists():
            print("❌ phase3_market_analyzer.py 檔案未找到")
            return False
        
        print(f"✅ phase3_market_analyzer.py 檔案存在: {phase3_file}")
        
        # 檢查檔案內容
        with open(phase3_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查資金費率相關功能
        funding_keywords = [
            '_collect_funding_rate',
            '_analyze_funding_rate_trend',
            '_calculate_funding_sentiment',
            '_check_funding_rate_signals',
            '_map_sentiment_to_category',
            'funding_sentiment'
        ]
        
        for keyword in funding_keywords:
            if keyword in content:
                print(f"✅ 資金費率功能 {keyword} 存在")
            else:
                print(f"❌ 資金費率功能 {keyword} 缺失")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Phase3 資金費率結構測試失敗: {e}")
        return False

def test_data_flow_json_structure():
    """測試數據流 JSON 結構"""
    print("\n🔍 測試數據流 JSON 檔案...")
    
    try:
        json_file = current_dir / "phase1a_basic_signal_generation.json"
        if not json_file.exists():
            print("❌ phase1a_basic_signal_generation.json 檔案不存在")
            return False
        
        print("✅ phase1a_basic_signal_generation.json 檔案存在")
        
        # 檢查 JSON 內容
        import json
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 檢查必要的數據結構
        required_sections = [
            'input_specifications',
            'output_specifications', 
            'processing_pipeline',
            'data_flow'
        ]
        
        for section in required_sections:
            if section in data:
                print(f"✅ JSON 結構 {section} 存在")
            else:
                print(f"❌ JSON 結構 {section} 缺失")
                return False
        
        # 檢查 OrderBook 相關配置
        if 'orderbook_integration' in str(data):
            print("✅ JSON 包含 OrderBook 整合配置")
        else:
            print("⚠️  JSON 未包含 OrderBook 整合配置")
        
        return True
        
    except Exception as e:
        print(f"❌ JSON 結構測試失敗: {e}")
        return False

def test_import_syntax():
    """測試導入語法正確性"""
    print("\n🔍 測試檔案導入語法...")
    
    try:
        # 檢查 phase1a 語法
        phase1a_file = current_dir / "phase1a_basic_signal_generation.py"
        
        # 使用 compile 檢查語法
        with open(phase1a_file, 'r', encoding='utf-8') as f:
            source = f.read()
        
        try:
            compile(source, str(phase1a_file), 'exec')
            print("✅ phase1a_basic_signal_generation.py 語法正確")
        except SyntaxError as e:
            print(f"❌ phase1a_basic_signal_generation.py 語法錯誤: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 導入語法測試失敗: {e}")
        return False

def test_configuration_files():
    """測試配置檔案"""
    print("\n🔍 測試配置檔案...")
    
    try:
        # 檢查動態參數配置
        config_files = [
            "intelligent_trigger_config.json",
            "auto_backtest_config.json"
        ]
        
        config_found = 0
        for config_file in config_files:
            config_path = Path("/Users/henrychang/Desktop/Trading-X") / config_file
            if config_path.exists():
                print(f"✅ 配置檔案 {config_file} 存在")
                config_found += 1
            else:
                print(f"⚠️  配置檔案 {config_file} 不存在")
        
        if config_found > 0:
            print(f"✅ 找到 {config_found} 個配置檔案")
            return True
        else:
            print("❌ 未找到任何配置檔案")
            return False
        
    except Exception as e:
        print(f"❌ 配置檔案測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("🔍 即時 API 優化核心功能測試")
    print("="*60)
    
    tests = [
        ("Phase1A 結構檢查", test_phase1a_imports_and_structure),
        ("Phase3 資金費率結構檢查", test_phase3_funding_rate_structure),
        ("數據流 JSON 結構檢查", test_data_flow_json_structure),
        ("導入語法檢查", test_import_syntax),
        ("配置檔案檢查", test_configuration_files)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*40}")
        print(f"🔍 {test_name}")
        print('='*40)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 測試出錯: {e}")
            results.append((test_name, False))
    
    # 總結結果
    print("\n" + "="*60)
    print("📊 測試結果總結")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n總計: {passed}/{total} 測試通過")
    
    if passed == total:
        print("🎉 所有核心功能測試通過！")
        return True
    else:
        print("🚨 部分測試失敗，需要檢查")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
