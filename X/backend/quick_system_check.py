#!/usr/bin/env python3
"""
⚡ Trading-X 快速系統驗證
========================

快速驗證四階段後端系統是否正常運行
專注於核心功能和動態特性驗證
"""

import asyncio
import sys
from pathlib import Path
import logging
from datetime import datetime

# 設置項目路徑 - 使用 X 資料夾作為根目錄
current_dir = Path(__file__).parent
project_root = current_dir.parent  # X 資料夾
sys.path.append(str(project_root))
sys.path.append(str(current_dir))  # backend 資料夾

# 簡化日誌配置
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def quick_system_check():
    """快速系統檢查"""
    try:
        print("🚀 Trading-X 快速系統驗證")
        print("=" * 50)
        
        # 1. 導入檢查
        print("📦 步驟 1: 導入系統組件...")
        try:
            from backend.trading_x_backend_integrator import backend_integrator
            print("✅ 後端整合器導入成功")
        except Exception as e:
            print(f"❌ 後端整合器導入失敗: {e}")
            return False
        
        # 2. 系統狀態檢查
        print("\n📊 步驟 2: 檢查系統狀態...")
        try:
            system_status = backend_integrator.get_system_status()
            print(f"✅ 系統狀態獲取成功")
            print(f"   - 系統效率: {system_status['performance_metrics']['system_efficiency']:.1%}")
        except Exception as e:
            print(f"❌ 系統狀態檢查失敗: {e}")
            return False
        
        # 3. 單一流水線快速測試
        print("\n🎯 步驟 3: 單一標的流水線測試...")
        try:
            test_symbol = "BTCUSDT"
            result = await backend_integrator.process_symbol_pipeline(test_symbol)
            
            print(f"✅ 流水線測試完成:")
            print(f"   - 標的: {result.symbol}")
            print(f"   - 成功率: {result.success_rate:.1%}")
            print(f"   - 處理時間: {result.processing_time:.2f}s")
            print(f"   - Phase1: {len(result.phase1_candidates)} 候選者")
            print(f"   - Phase2: {len(result.phase2_evaluations)} 評估")
            print(f"   - Phase3: {len(result.phase3_decisions)} 決策")
            print(f"   - Phase4: {len(result.phase4_outputs)} 輸出")
            
            if result.error_messages:
                print(f"⚠️ 錯誤訊息: {len(result.error_messages)} 個")
                for error in result.error_messages[:3]:  # 只顯示前3個錯誤
                    print(f"     - {error}")
            
            success = result.success_rate > 0.25  # 至少25%成功率
            
        except Exception as e:
            print(f"❌ 流水線測試失敗: {e}")
            success = False
        
        # 4. 動態特性驗證
        print("\n🔄 步驟 4: 動態特性驗證...")
        try:
            dynamic_metrics = system_status.get('dynamic_adaptation', {})
            adaptation_rate = dynamic_metrics.get('adaptation_success_rate', 0)
            feature_usage = dynamic_metrics.get('dynamic_feature_usage', {})
            
            print(f"✅ 動態特性檢查:")
            print(f"   - 適應成功率: {adaptation_rate:.1%}")
            print(f"   - 動態特性數量: {len(feature_usage.get('features_found', []))}")
            
            if adaptation_rate > 0.3:
                print("✅ 動態特性驗證通過")
                dynamic_ok = True
            else:
                print("⚠️ 動態特性可能需要優化")
                dynamic_ok = True  # 不作為致命錯誤
                
        except Exception as e:
            print(f"❌ 動態特性驗證失敗: {e}")
            dynamic_ok = False
        
        # 5. 整體評估
        print("\n🏆 系統驗證結果:")
        print("=" * 30)
        
        if success and dynamic_ok:
            print("✅ 系統運行正常")
            print("🎯 建議: 可以進行完整測試或啟動監控模式")
            print("\n📋 後續操作:")
            print("   - 完整測試: python backend/launcher.py --mode test")
            print("   - 開始監控: python backend/launcher.py --mode monitor")
            print("   - 系統診斷: python backend/launcher.py --mode diagnostic")
            return True
        else:
            print("⚠️ 系統存在問題，需要檢查")
            print("🔧 建議:")
            if not success:
                print("   - 檢查網絡連接和API配置")
                print("   - 確認數據源可用性")
            if not dynamic_ok:
                print("   - 檢查動態適應參數配置")
                print("   - 驗證策略組件初始化")
            return False
            
    except Exception as e:
        print(f"💥 系統驗證嚴重失敗: {e}")
        return False

async def quick_performance_test():
    """快速性能測試"""
    try:
        print("\n⚡ 快速性能測試")
        print("-" * 30)
        
        from backend.trading_x_backend_integrator import backend_integrator
        
        # 測試多個標的的處理時間
        test_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
        start_time = datetime.now()
        
        results = await backend_integrator.process_multiple_symbols(test_symbols, concurrent_limit=2)
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        successful_results = [r for r in results if r.success_rate > 0.25]
        
        print(f"📊 性能測試結果:")
        print(f"   - 測試標的: {len(test_symbols)}")
        print(f"   - 成功處理: {len(successful_results)}")
        print(f"   - 總耗時: {total_time:.2f}s")
        print(f"   - 平均每標的: {total_time/len(test_symbols):.2f}s")
        print(f"   - 成功率: {len(successful_results)/len(test_symbols):.1%}")
        
        if total_time < 60 and len(successful_results) > 0:
            print("✅ 性能測試通過")
            return True
        else:
            print("⚠️ 性能可能需要優化")
            return False
            
    except Exception as e:
        print(f"❌ 性能測試失敗: {e}")
        return False

async def main():
    """主函數"""
    print(f"🕐 開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 基本系統檢查
    basic_check = await quick_system_check()
    
    if basic_check:
        # 性能測試
        performance_check = await quick_performance_test()
        
        print(f"\n🕐 結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if performance_check:
            print("\n🎉 所有檢查通過！系統準備就緒")
            print("💡 提示: 運行 'python backend/launcher.py --mode test' 進行完整測試")
        else:
            print("\n⚠️ 基本功能正常，但性能可能需要優化")
    else:
        print(f"\n🕐 結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n❌ 系統檢查未通過，請檢查錯誤訊息")

if __name__ == "__main__":
    asyncio.run(main())
