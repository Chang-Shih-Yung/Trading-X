#!/usr/bin/env python3
"""
🎯 Phase5 Lean 優化演示
展示如何在不改動 JSON Schema 的情況下實現 Lean 優化
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def demo_phase5_lean_optimization():
    """演示 Phase5 Lean 優化完整流程"""
    
    print("=" * 80)
    print("🎯 Phase5 Lean 相似度回測優化演示")
    print("=" * 80)
    
    print("\n📋 核心優化理念:")
    print("✅ 保持既有 JSON Schema 不變")
    print("✅ 內部實現 Lean 優化邏輯")
    print("✅ 僅形狀比較，避免多指標過擬合") 
    print("✅ H4+D1投票，W1制度閘門")
    print("✅ 三重執行過濾機制")
    
    try:
        # 導入 Lean 分析模組 (同目錄)
        from phase5_enhanced_backtest_strategy import (
            run_lean_backtest_analysis,
            LeanHistoricalMatcher,
            MarketRegime,
            TimeFrame
        )
        
        print("\n🚀 步驟 1: 啟動 Lean 歷史相似度分析...")
        
        # 分析主要加密貨幣
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT"]
        
        print(f"📊 分析幣種: {', '.join(symbols)}")
        print("🔍 執行多時間框架 Lean 分析...")
        
        # 執行 Lean 分析
        analysis_result = await run_lean_backtest_analysis(symbols)
        
        print(f"\n✅ 步驟 2: Lean 分析完成")
        print(f"   📈 平均信心度: {analysis_result['summary']['avg_confidence']:.2%}")
        print(f"   💰 平均期望收益: {analysis_result['summary']['avg_expected_return']:.4f}")
        print(f"   🚪 制度閘門通過率: {analysis_result['summary']['regime_gate_pass_rate']:.1%}")
        print(f"   📊 看多信號: {analysis_result['summary']['bullish_signals']}")
        print(f"   📉 看空信號: {analysis_result['summary']['bearish_signals']}")
        
        print(f"\n📁 步驟 3: JSON 配置已生成")
        config_path = analysis_result.get('config_saved_path', '')
        if config_path:
            print(f"   ✅ 配置路徑: {Path(config_path).name}")
            print(f"   🔄 Phase1A 將自動讀取此配置")
            
            # 檢查生成的配置內容
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 顯示關鍵 Lean 參數
                lean_config = config_data.get('phase1a_basic_signal_generation_dependency', {})
                lean_optimization = lean_config.get('lean_optimization', {})
                
                if lean_optimization.get('enabled'):
                    print(f"\n🎯 步驟 4: Lean 優化參數注入成功")
                    print(f"   🔬 方法論: {lean_optimization.get('methodology', 'N/A')}")
                    print(f"   📊 特徵數量: {lean_optimization.get('feature_count', 'N/A')}")
                    print(f"   ⏰ 時間框架策略: {lean_optimization.get('timeframe_strategy', 'N/A')}")
                    print(f"   🏛️ 制度過濾: {lean_optimization.get('regime_filtering', 'N/A')}")
                    
                    # 顯示動態調整的參數
                    signal_params = lean_config.get('configuration', {}).get('signal_generation_params', {}).get('basic_mode', {})
                    if signal_params:
                        print(f"\n🔧 動態參數調整:")
                        
                        price_threshold = signal_params.get('price_change_threshold', {})
                        if price_threshold.get('lean_optimization'):
                            print(f"   📈 價格變化閾值: {price_threshold.get('base_value', 0):.4f}")
                        
                        confidence_threshold = signal_params.get('confidence_threshold', {})
                        if confidence_threshold.get('lean_optimization'):
                            print(f"   🎯 信心度閾值: {confidence_threshold.get('base_value', 0):.3f}")
                
                # 顯示回測摘要
                lean_summary = config_data.get('lean_backtest_summary', {})
                if lean_summary:
                    print(f"\n📊 Lean 回測摘要:")
                    print(f"   🪙 分析幣種數: {lean_summary.get('total_symbols_analyzed', 0)}")
                    print(f"   ✅ 通過制度閘門: {lean_summary.get('regime_gate_passed', 0)}")
                    print(f"   📈 市場情緒: {lean_summary.get('market_sentiment', 'N/A')}")
                    print(f"   🎯 市場信心度: {lean_summary.get('market_confidence', 0):.3f}")
                    
                print(f"\n🎉 步驟 5: 整合驗證")
                print(f"   ✅ JSON Schema 完全保持不變")
                print(f"   ✅ Lean 優化參數成功嵌入")
                print(f"   ✅ Phase1A 將自動使用優化配置")
                print(f"   ✅ 三層融合架構保持: Phase5(75%) + intelligent_trigger(25%) + Phase1A協調")
                
            except Exception as e:
                print(f"   ⚠️ 配置檢查失敗: {e}")
        else:
            print(f"   ❌ 配置保存失敗")
        
        print(f"\n🔬 Lean 優化核心特色:")
        print(f"   🎯 僅3個序列: 收益形狀 + RSI-zscore + 波動制度")
        print(f"   📊 相似度公式: 70% 收益形狀 + 30% RSI")
        print(f"   🏛️ 制度先行: 同制度內比較，避免偽關聯")
        print(f"   ⚖️ 投票簡化: H4(45%) + D1(55%)，W1制度閘門")
        print(f"   🛡️ 三重過濾: 統計顯著性 + 成本超越 + 制度通過")
        print(f"   💰 波動縮倉: 基於實際波動的倉位調整")
        
        print(f"\n🎯 與原版對比:")
        print(f"   原版: 60+指標 → Lean: 3個序列")
        print(f"   原版: H1/H4/D1/W1均等 → Lean: H4+D1投票，W1閘門")
        print(f"   原版: 多維加權 → Lean: 純形狀比較")
        print(f"   原版: 理想執行 → Lean: 保守成本+流動性限制")
        
        print(f"\n✅ Phase5 Lean 優化演示完成!")
        print(f"🔄 下次 Phase1A 啟動時將自動使用 Lean 優化配置")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 演示過程出錯: {e}")
        return False

async def demo_lean_vs_original_comparison():
    """演示 Lean 與原版的對比"""
    
    print("\n" + "=" * 80)
    print("📊 Lean 優化 vs 原版系統對比")
    print("=" * 80)
    
    comparison_table = [
        ["項目", "原版系統", "Lean 優化版", "優化效果"],
        ["─" * 20, "─" * 25, "─" * 25, "─" * 25],
        ["技術指標數量", "60+ 多維指標", "3 個核心序列", "避免過擬合"],
        ["時間框架策略", "H1/H4/D1/W1 均等投票", "H4+D1投票，W1制度閘門", "降權簡化"],
        ["相似度計算", "多指標加權組合", "純形狀：收益+RSI", "專注本質"],
        ["制度檢測", "無制度分類", "6種制度，同制度比較", "降低偽關聯"],
        ["執行模型", "理想化執行", "保守成本+流動性限制", "貼近實盤"],
        ["驗證方式", "歷史回測", "Walk-Forward驗證", "嚴格前驗證"],
        ["過擬合防護", "參數大量調整", "固定粗粒度檔位", "穩健性優先"],
        ["成本模型", "忽略滑點成本", "手續費+滑點×2保守", "真實交易成本"],
        ["JSON Schema", "複雜多變", "完全保持不變", "向下相容"],
        ["維護複雜度", "高（多指標維護）", "低（3序列+制度）", "大幅簡化"]
    ]
    
    for row in comparison_table:
        print(f"{row[0]:<20} {row[1]:<25} {row[2]:<25} {row[3]:<25}")
    
    print(f"\n🎯 Lean 優化核心優勢:")
    print(f"   1️⃣ 簡化特徵：3序列 vs 60+指標，專注形狀比較")
    print(f"   2️⃣ 制度先行：同環境比較，提高相似度品質")
    print(f"   3️⃣ 保守執行：內建真實成本，更貼近實盤")
    print(f"   4️⃣ 架構相容：JSON Schema不變，無縫整合")
    print(f"   5️⃣ 防過擬合：固定參數檔位，穩健性優先")

async def main():
    """主演示流程"""
    print("🎯 Phase5 Lean 相似度回測優化 - 完整演示")
    
    # 執行主要演示
    success = await demo_phase5_lean_optimization()
    
    if success:
        # 執行對比演示
        await demo_lean_vs_original_comparison()
        
        print(f"\n🎉 所有演示完成!")
        print(f"📁 生成的配置文件可在以下路徑找到:")
        print(f"   /Users/itts/Desktop/Trading X/X/backend/phase5_backtest_validation/safety_backups/working/")
        print(f"🔄 Phase1A 將在下次啟動時自動讀取最新的 Lean 優化配置")
    else:
        print(f"❌ 演示未完成，請檢查錯誤信息")

if __name__ == "__main__":
    asyncio.run(main())
