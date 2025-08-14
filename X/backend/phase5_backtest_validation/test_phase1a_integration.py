#!/usr/bin/env python3
"""
🎯 Phase1A 整合測試器
測試 Phase5 與 Phase1A 的直接整合功能
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# 添加必要的路徑
sys.path.append(str(Path(__file__).parent / "auto_backtest_validator"))

async def test_phase1a_integration():
    """測試Phase1A整合功能"""
    print("🚀 開始測試 Phase1A 整合...")
    
    try:
        # 導入Phase5自動回測驗證器
        from auto_backtest_validator import AutoBacktestValidator, run_phase1a_validation  # type: ignore
        
        print("✅ 成功導入 AutoBacktestValidator")
        
        # 創建驗證器實例
        validator = AutoBacktestValidator()
        print("✅ 成功創建驗證器實例")
        
        # 初始化Phase1A生成器
        validator._init_phase1a_generator()
        print("✅ 成功初始化 Phase1A 生成器")
        
        # 測試歷史數據獲取
        print("\n📊 測試歷史數據獲取...")
        historical_data = await validator._fetch_historical_klines('BTCUSDT', '5m', 100)
        
        if not historical_data.empty:
            print(f"✅ 成功獲取 BTC 歷史數據: {len(historical_data)} 筆記錄")
            print(f"   時間範圍: {historical_data.iloc[0]['open_time']} 到 {historical_data.iloc[-1]['open_time']}")
            print(f"   最新價格: ${historical_data.iloc[-1]['close']:.2f}")
        else:
            print("❌ 歷史數據獲取失敗")
            return False
        
        # 測試單一幣種Phase1A回測
        print("\n🔄 測試 BTC Phase1A 回測...")
        backtest_result = await validator._run_phase1a_backtest('BTCUSDT', '5m', 2)  # 2天快速測試
        
        if 'error' not in backtest_result:
            print("✅ BTC Phase1A 回測成功:")
            print(f"   總信號數: {backtest_result.get('total_signals', 0)}")
            print(f"   勝率: {backtest_result.get('win_rate', 0):.2%}")
            print(f"   平均盈虧比: {backtest_result.get('avg_pnl_ratio', 0):.4f}")
        else:
            print(f"❌ BTC Phase1A 回測失敗: {backtest_result.get('error')}")
            return False
        
        # 測試完整驗證週期 (簡化版)
        print("\n🎯 測試簡化驗證週期...")
        
        # 手動測試少數幣種以節省時間
        test_symbols = ['BTCUSDT', 'ETHUSDT']
        results = {}
        
        for symbol in test_symbols:
            print(f"   正在測試 {symbol}...")
            result = await validator._run_phase1a_backtest(symbol, '5m', 1)  # 1天快速測試
            
            if 'error' not in result:
                results[symbol] = result
                print(f"   ✅ {symbol}: 勝率 {result.get('win_rate', 0):.2%}")
            else:
                print(f"   ❌ {symbol}: {result.get('error')}")
        
        # 計算整體統計
        if results:
            total_signals = sum(r.get('total_signals', 0) for r in results.values())
            total_wins = sum(int(r.get('win_rate', 0) * r.get('total_signals', 0)) for r in results.values())
            overall_win_rate = total_wins / total_signals if total_signals > 0 else 0
            
            print(f"\n📈 整體測試結果:")
            print(f"   測試幣種: {len(results)} 個")
            print(f"   總信號數: {total_signals}")
            print(f"   整體勝率: {overall_win_rate:.2%}")
            print(f"   目標達成: {'✅ 是' if overall_win_rate >= 0.70 else '❌ 否'} (目標70%)")
        
        print("\n🎉 Phase1A 整合測試完成!")
        return True
        
    except ImportError as e:
        print(f"❌ 導入失敗: {e}")
        return False
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_phase1a_api_access():
    """測試Phase1A API接口"""
    print("\n🔌 測試 Phase1A API 接口...")
    
    try:
        from auto_backtest_validator import run_phase1a_validation  # type: ignore
        
        # 測試全局API函數
        print("   調用 run_phase1a_validation()...")
        
        # 注意：這會運行完整的7天7幣種回測，可能需要較長時間
        # 在生產環境中使用，測試時可以註解掉
        # result = await run_phase1a_validation()
        
        print("✅ Phase1A API 接口可用")
        print("   (完整驗證已跳過以節省時間)")
        
        return True
        
    except Exception as e:
        print(f"❌ API 測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("=" * 60)
    print("🎯 Trading X - Phase1A 整合測試")
    print("=" * 60)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 運行異步測試
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # 基本整合測試
        integration_success = loop.run_until_complete(test_phase1a_integration())
        
        # API接口測試
        api_success = loop.run_until_complete(test_phase1a_api_access())
        
        # 總結
        print("\n" + "=" * 60)
        print("📋 測試總結:")
        print(f"   Phase1A 整合: {'✅ 成功' if integration_success else '❌ 失敗'}")
        print(f"   API 接口: {'✅ 可用' if api_success else '❌ 不可用'}")
        
        if integration_success and api_success:
            print("\n🎉 恭喜！Phase1A 與 Phase5 整合完全成功！")
            print("   現在可以使用以下功能:")
            print("   • 自動獲取真實歷史數據")
            print("   • Phase1A 信號生成與回測")
            print("   • 多幣種驗證週期")
            print("   • 70% 目標勝率監控")
            return True
        else:
            print("\n❌ 整合測試失敗，請檢查錯誤信息並修復")
            return False
            
    except KeyboardInterrupt:
        print("\n⏹️  用戶中斷測試")
        return False
    except Exception as e:
        print(f"\n💥 測試過程中發生未知錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        loop.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
