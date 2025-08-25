#!/usr/bin/env python3
"""
🚀 Trading X - 精確量子交易啟動器
直接啟動量子精密交易引擎，避免SQLAlchemy表重複定義問題
"""

import sys
import asyncio
import logging
from pathlib import Path

# 確保正確的路徑
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def start_precise_quantum_trading():
    """啟動精確量子交易引擎"""
    try:
        # 直接導入量子引擎，避免循環導入
        from X.quantum.simple_quantum_trading_engine import SimpleQuantumEngine
        
        print("🌀 Trading X - 精確量子交易引擎")
        print("⚛️ 啟動基於X系統真實交易類型的量子疊加決策")
        print("=" * 60)
        
        # 創建量子引擎
        engine = SimpleQuantumEngine()
        
        # 運行量子分析
        print("\n🧪 執行精確量子分析...")
        
        # 測試量子決策生成
        decisions = await engine.run_quantum_analysis_cycle()
        
        if decisions:
            print(f"✅ 成功生成 {len(decisions)} 個量子決策")
            for i, decision in enumerate(decisions, 1):
                print(f"   {i}. {decision.symbol} {decision.timeframe} -> {decision.signal_type.value}")
                print(f"      信心度: {decision.confidence:.3f}, 分層: {decision.tier.value}")
                print(f"      市場狀態: {decision.market_regime.value}")
        else:
            print("📊 當前市場條件未觸發量子塌縮")
        
        # 詢問是否啟動持續模式
        user_input = input("\n🌀 是否啟動持續精確量子交易模式? (y/N): ")
        if user_input.lower() == 'y':
            cycles_input = input("指定運行周期數 (直接回車表示無限): ")
            cycles = int(cycles_input) if cycles_input.strip() else None
            
            print("\n" + "="*50)
            print("⚛️ 精確量子交易引擎正在運行...")
            print("   使用真實X系統交易類型進行量子疊加決策")
            print("   按 Ctrl+C 安全停止系統")
            print("="*50)
            
            await engine.run_continuous_quantum_trading(cycles)
        else:
            print("👋 精確量子交易引擎測試完成")
            
    except ImportError as e:
        logger.error(f"❌ 導入錯誤: {e}")
        print("請檢查量子模組是否正確安裝")
    except Exception as e:
        logger.error(f"❌ 量子引擎啟動失敗: {e}")

if __name__ == "__main__":
    print("🎯 Trading X - 精確量子交易直接啟動")
    asyncio.run(start_precise_quantum_trading())
