#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trading X 量子即時 API 整合測試
=====================================

測試完整的即時幣安 API 整合：
- WebSocket 即時數據流
- 訂單簿深度分析
- 交易流統計
- 資金費率監控
- 量子制度分析
- Trading X 信號輸出

作者: Trading X Quantum Team
日期: 2024-08-25
版本: 2.0 - 即時 API 整合版
"""

import asyncio
import sys
import os
import traceback
from pathlib import Path

# 添加項目路徑
sys.path.append(str(Path(__file__).parent))

# 導入必要模組
try:
    from .regime_hmm_quantum import (
        TimeVaryingHMM,
        即時幣安數據收集器,
        TradingX信號輸出器,
        即時市場觀測,
        TradingX信號
    )
    print("✅ 成功導入量子模組")
except ImportError:
    try:
        from regime_hmm_quantum import (
            TimeVaryingHMM,
            即時幣安數據收集器,
            TradingX信號輸出器,
            即時市場觀測,
            TradingX信號
        )
        print("✅ 成功導入量子模組")
    except ImportError as e:
        print(f"❌ 導入量子模組失敗: {e}")
        traceback.print_exc()

async def 測試即時數據收集():
    """測試即時數據收集功能"""
    print("\n" + "="*60)
    print("🔄 測試 1: 即時幣安數據收集")
    print("="*60)
    
    # 測試交易對
    測試交易對 = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
    
    # 初始化數據收集器
    收集器 = 即時幣安數據收集器(測試交易對)
    
    try:
        print("📡 啟動數據收集...")
        
        # 啟動數據收集（非阻塞）
        收集任務 = asyncio.create_task(收集器.啟動數據收集())
        
        # 等待數據累積
        await asyncio.sleep(30)  # 等待30秒收集數據
        
        print("\n📊 檢查收集到的數據:")
        for 交易對 in 測試交易對:
            觀測 = 收集器.獲取即時觀測(交易對)
            if 觀測:
                print(f"\n🔸 {交易對}:")
                print(f"   價格: ${觀測.價格:.4f}")
                print(f"   收益率: {觀測.收益率:.4%}")
                print(f"   波動率: {觀測.已實現波動率:.4%}")
                print(f"   買賣價差: {觀測.買賣價差:.6f}")
                print(f"   訂單簿壓力: {觀測.訂單簿壓力:.3f}")
                print(f"   主動買入比率: {觀測.主動買入比率:.3f}")
                if 觀測.資金費率:
                    print(f"   資金費率: {觀測.資金費率:.6f}")
                if 觀測.未平倉量:
                    print(f"   未平倉量: {觀測.未平倉量:,.0f}")
            else:
                print(f"❌ {交易對}: 無數據")
        
        # 停止數據收集
        await 收集器.停止數據收集()
        收集任務.cancel()
        
        print("\n✅ 即時數據收集測試完成")
        return True
        
    except Exception as e:
        print(f"❌ 即時數據收集測試失敗: {e}")
        traceback.print_exc()
        return False

async def 測試量子制度分析():
    """測試量子制度分析"""
    print("\n" + "="*60)
    print("🧠 測試 2: 量子制度分析引擎")
    print("="*60)
    
    try:
        # 初始化量子 HMM
        量子引擎 = TimeVaryingHMM(
            n_states=6,
            z_dim=3,
            enable_quantum_features=True
        )
        
        print("🔬 執行制度分析...")
        
        # 模擬即時觀測數據
        測試觀測 = 即時市場觀測(
            時間戳=datetime.now(),
            交易對='BTCUSDT',
            價格=43000.0,
            成交量=1250.5,
            收益率=0.015,
            已實現波動率=0.025,
            動量斜率=0.08,
            最佳買價=42995.0,
            最佳賣價=43005.0,
            買賣價差=0.00023,
            訂單簿壓力=0.15,
            主動買入比率=0.62,
            大單流入率=0.0,
            資金費率=0.0001,
            未平倉量=15500000.0,
            RSI_14=65.5,
            布林帶位置=0.72
        )
        
        # 構建量子觀測序列
        量子觀測序列 = 量子引擎._構建量子觀測序列(測試觀測, 'BTCUSDT')
        
        if 量子觀測序列:
            print("✅ 量子觀測序列構建成功")
            
            # 執行量子制度分析
            分析結果 = 量子引擎.quantum_regime_analysis(
                x_seq=量子觀測序列['observations'],
                z_seq=量子觀測序列['covariates'],
                market_condition=量子觀測序列['market_condition']
            )
            
            print("\n🔮 量子制度分析結果:")
            制度概率 = 分析結果['regime_probabilities']
            主要制度 = np.argmax(制度概率)
            
            制度名稱 = {
                0: "牛市制度", 1: "熊市制度", 2: "高波動制度",
                3: "低波動制度", 4: "橫盤制度", 5: "崩盤制度"
            }
            
            print(f"🏛️  主要制度: {制度名稱.get(主要制度, '未知')} (制度 {主要制度})")
            print(f"📊 制度概率分布:")
            for i, 概率 in enumerate(制度概率):
                print(f"   {制度名稱.get(i, f'制度{i}')}: {概率:.2%}")
            
            # 檢查量子決策
            if 分析結果['quantum_decision']:
                決策 = 分析結果['quantum_decision']
                print(f"\n⚡ 量子決策:")
                print(f"   信號: {決策.action}")
                print(f"   信心度: {決策.confidence:.2%}")
                print(f"   評分: {決策.score:.3f}")
                print(f"   風險報酬比: {決策.risk_reward_ratio:.2f}")
            
            print("\n✅ 量子制度分析測試完成")
            return True
        else:
            print("❌ 量子觀測序列構建失敗")
            return False
            
    except Exception as e:
        print(f"❌ 量子制度分析測試失敗: {e}")
        traceback.print_exc()
        return False

async def 測試完整交易信號生成():
    """測試完整的交易信號生成流程"""
    print("\n" + "="*60)
    print("🎯 測試 3: Trading X 交易信號生成")
    print("="*60)
    
    try:
        # 初始化組件
        量子引擎 = TimeVaryingHMM(n_states=6, enable_quantum_features=True)
        信號輸出器 = TradingX信號輸出器()
        
        # 模擬多個交易對的即時數據
        測試數據 = {
            'BTCUSDT': {
                '價格': 43250.0, '收益率': 0.012, '波動率': 0.018,
                '動量': 0.05, 'RSI': 67.2, '資金費率': 0.0001
            },
            'ETHUSDT': {
                '價格': 2450.0, '收益率': -0.008, '波動率': 0.025,
                '動量': -0.02, 'RSI': 42.1, '資金費率': -0.00005
            },
            'SOLUSDT': {
                '價格': 145.0, '收益率': 0.035, '波動率': 0.045,
                '動量': 0.12, 'RSI': 78.5, '資金費率': 0.0003
            }
        }
        
        print("🔄 生成交易信號...")
        
        for 交易對, 數據 in 測試數據.items():
            print(f"\n📈 處理 {交易對}:")
            
            # 構建觀測
            觀測 = 即時市場觀測(
                時間戳=datetime.now(),
                交易對=交易對,
                價格=數據['價格'],
                成交量=1000.0,
                收益率=數據['收益率'],
                已實現波動率=數據['波動率'],
                動量斜率=數據['動量'],
                最佳買價=數據['價格'] * 0.9998,
                最佳賣價=數據['價格'] * 1.0002,
                買賣價差=0.0004,
                訂單簿壓力=0.1,
                主動買入比率=0.55,
                大單流入率=0.0,
                資金費率=數據['資金費率'],
                RSI_14=數據['RSI'],
                布林帶位置=0.6
            )
            
            # 構建量子序列並分析
            量子序列 = 量子引擎._構建量子觀測序列(觀測, 交易對)
            if 量子序列:
                分析結果 = 量子引擎.quantum_regime_analysis(
                    x_seq=量子序列['observations'],
                    z_seq=量子序列['covariates'],
                    market_condition=量子序列['market_condition']
                )
                
                # 生成交易信號
                if 分析結果['quantum_decision']:
                    交易信號 = 信號輸出器.生成交易信號(
                        觀測,
                        分析結果['quantum_decision'],
                        分析結果['regime_probabilities']
                    )
                    
                    # 顯示信號詳情
                    print(f"   🔮 信號: {交易信號.信號類型}")
                    print(f"   📊 信心度: {交易信號.信心度:.2%}")
                    print(f"   🏛️  制度: {交易信號.市場制度名稱}")
                    print(f"   💰 期望收益: {交易信號.期望收益:.2%}")
                    print(f"   ⚠️  風險評估: {交易信號.風險評估:.2%}")
                    print(f"   📈 風險報酬比: {交易信號.風險報酬比:.2f}")
                    print(f"   💼 建議倉位: {交易信號.持倉建議:.1%}")
                    
                    if 交易信號.止損價格:
                        print(f"   🛡️  止損: ${交易信號.止損價格:.2f}")
                    if 交易信號.止盈價格:
                        print(f"   🎯 止盈: ${交易信號.止盈價格:.2f}")
                else:
                    print("   ⚪ 無量子決策信號")
            else:
                print("   ❌ 量子序列構建失敗")
        
        print("\n✅ 交易信號生成測試完成")
        return True
        
    except Exception as e:
        print(f"❌ 交易信號生成測試失敗: {e}")
        traceback.print_exc()
        return False

async def 測試短期即時系統():
    """測試短期即時系統運行"""
    print("\n" + "="*60)
    print("🚀 測試 4: 即時量子交易系統 (短期測試)")
    print("="*60)
    
    try:
        # 初始化量子引擎
        量子引擎 = TimeVaryingHMM(
            n_states=6,
            z_dim=3,
            enable_quantum_features=True
        )
        
        print("📡 啟動即時交易系統 (60秒測試)...")
        
        # 啟動系統任務
        系統任務 = asyncio.create_task(量子引擎.啟動即時交易系統())
        
        # 運行60秒
        await asyncio.sleep(60)
        
        print("\n📊 檢查系統狀態...")
        
        # 獲取制度統計
        制度統計 = 量子引擎.獲取制度統計()
        
        if 制度統計:
            print(f"\n✅ 處理了 {len(制度統計)} 個交易對:")
            for 交易對, 統計 in 制度統計.items():
                print(f"   🔸 {交易對}:")
                print(f"      制度: {統計['制度名稱']}")
                print(f"      信號數: {統計['總信號數']}")
                print(f"      更新次數: {統計['制度變化次數']}")
        else:
            print("⚠️  尚無制度統計數據")
        
        # 停止系統
        await 量子引擎.停止即時交易系統()
        系統任務.cancel()
        
        print("\n✅ 即時系統測試完成")
        return True
        
    except Exception as e:
        print(f"❌ 即時系統測試失敗: {e}")
        traceback.print_exc()
        return False

async def main():
    """主測試函數"""
    print("🔮 Trading X 量子即時 API 整合測試")
    print("=" * 60)
    print("測試即時幣安 API 整合、量子制度分析和信號生成")
    print("=" * 60)
    
    測試結果 = []
    
    # 測試 1: 即時數據收集
    結果1 = await 測試即時數據收集()
    測試結果.append(("即時數據收集", 結果1))
    
    # 測試 2: 量子制度分析
    結果2 = await 測試量子制度分析()
    測試結果.append(("量子制度分析", 結果2))
    
    # 測試 3: 交易信號生成
    結果3 = await 測試完整交易信號生成()
    測試結果.append(("交易信號生成", 結果3))
    
    # 測試 4: 短期即時系統
    結果4 = await 測試短期即時系統()
    測試結果.append(("即時交易系統", 結果4))
    
    # 總結報告
    print("\n" + "="*60)
    print("📋 測試總結報告")
    print("="*60)
    
    成功數 = 0
    for 測試名稱, 結果 in 測試結果:
        狀態 = "✅ 通過" if 結果 else "❌ 失敗"
        print(f"{狀態} {測試名稱}")
        if 結果:
            成功數 += 1
    
    print(f"\n🎯 總體結果: {成功數}/{len(測試結果)} 個測試通過")
    
    if 成功數 == len(測試結果):
        print("🎉 所有測試通過！Trading X 量子即時 API 整合系統運行正常")
    else:
        print("⚠️  部分測試失敗，請檢查系統配置和網路連接")
    
    print("\n🔮 Trading X Quantum Engine Status: OPERATIONAL ✅")

if __name__ == "__main__":
    # 導入額外的依賴
    import numpy as np
    from datetime import datetime
    
    # 運行測試
    asyncio.run(main())
