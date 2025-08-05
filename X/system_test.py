"""
🧪 Trading-X 系統快速驗證工具
=============================

驗證重組後的系統是否正常運作
"""

import sys
from pathlib import Path

def test_imports():
    """測試導入是否正常"""
    test_results = {}
    
    # 添加路徑
    current_dir = Path(__file__).parent
    sys.path.extend([
        str(current_dir / "core"),
        str(current_dir / "strategies"),
        str(current_dir / "indicators"), 
        str(current_dir / "monitoring"),
        str(current_dir / "utils"),
        str(current_dir.parent / "app" / "services")
    ])
    
    # 測試核心模組
    try:
        from config import SYSTEM_NAME, SYSTEM_VERSION
        test_results["config"] = f"✅ {SYSTEM_NAME} v{SYSTEM_VERSION}"
    except Exception as e:
        test_results["config"] = f"❌ {e}"
    
    # 測試策略模組
    try:
        import sys
        sys.path.append(str(current_dir / "strategies" / "phase1"))
        sys.path.append(str(current_dir / "strategies" / "phase3"))
        sys.path.append(str(current_dir / "core"))
        
        from phase1b_volatility_adaptation import VolatilityAdaptationEngine
        from phase1c_signal_standardization import SignalStandardizationEngine
        from phase3_market_analyzer import MarketAnalyzer
        test_results["strategies"] = "✅ Phase1B, Phase1C, Phase3 載入成功"
    except Exception as e:
        test_results["strategies"] = f"❌ {e}"
    
    # 測試指標模組
    try:
        from pandas_ta_indicators import TechnicalIndicatorEngine
        test_results["indicators"] = "✅ 技術指標引擎載入成功"
    except Exception as e:
        test_results["indicators"] = f"❌ {e}"
    
    # 測試核心模組
    try:
        from binance_data_connector import binance_connector
        from real_data_signal_quality_engine import RealDataSignalQualityEngine
        test_results["core"] = "✅ 核心組件載入成功"
    except Exception as e:
        test_results["core"] = f"❌ {e}"
    
    return test_results

def main():
    """主測試函數"""
    print("🧪 開始 Trading-X 系統驗證...")
    print("=" * 50)
    
    results = test_imports()
    
    print("📋 測試結果:")
    for component, status in results.items():
        print(f"  {component:12}: {status}")
    
    success_count = sum(1 for status in results.values() if "✅" in status)
    total_count = len(results)
    
    print("=" * 50)
    print(f"✅ 成功: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 系統重組完成，所有組件正常！")
        return True
    else:
        print("⚠️ 部分組件需要修復")
        return False

if __name__ == "__main__":
    main()
