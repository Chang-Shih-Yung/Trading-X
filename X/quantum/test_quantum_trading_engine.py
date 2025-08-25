#!/usr/bin/env python3
"""
🧪 Trading X - 量子交易引擎測試驗證器
測試量子引擎與X系統Phase1A-Phase5的完整集成

這個腳本會：
1. 驗證所有Phase組件的連接狀態
2. 測試量子引擎的初始化
3. 執行端到端的量子交易決策流程
4. 驗證數據流的完整性
5. 檢查與現有數據庫的兼容性
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# 添加路徑
sys.path.append('./X')
sys.path.append('./X/backend')
sys.path.append('.')

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 導入量子模塊
try:
    from quantum_precision_trading_engine import QuantumTradingCoordinator
    from quantum_phase_data_integrator import get_quantum_phase_coordinator
    QUANTUM_ENGINE_AVAILABLE = True
except ImportError as e:
    QUANTUM_ENGINE_AVAILABLE = False
    logger.error(f"❌ 量子引擎導入失敗: {e}")

# X系統導入測試
X_SYSTEM_STATUS = {}

def test_x_system_imports():
    """測試X系統各模塊導入狀態"""
    print("🔍 測試X系統模塊導入狀態...")
    
    # 測試數據庫模塊
    try:
        from X.app.core.database_separated import get_learning_db, get_signals_db, get_market_db
        X_SYSTEM_STATUS["database"] = True
        print("✅ 數據庫模塊: 正常")
    except ImportError as e:
        X_SYSTEM_STATUS["database"] = False
        print(f"❌ 數據庫模塊: {e}")
    
    # 測試Phase1A
    try:
        from X.backend.phase1_signal_generation.phase1a_basic_signal_generation.phase1a_basic_signal_generation import (
            SignalTier, EnhancedSignalTierSystem, MarketRegime
        )
        X_SYSTEM_STATUS["phase1a"] = True
        print("✅ Phase1A模塊: 正常")
    except ImportError as e:
        X_SYSTEM_STATUS["phase1a"] = False
        print(f"❌ Phase1A模塊: {e}")
    
    # 測試Phase2
    try:
        from X.backend.phase2_adaptive_learning.priority3_timeframe_learning.enhanced_signal_database import (
            EnhancedSignalDatabase
        )
        X_SYSTEM_STATUS["phase2"] = True
        print("✅ Phase2模塊: 正常")
    except ImportError as e:
        X_SYSTEM_STATUS["phase2"] = False
        print(f"❌ Phase2模塊: {e}")
    
    # 測試實時引擎
    try:
        from X.app.services.realtime_signal_engine import RealtimeSignalEngine
        X_SYSTEM_STATUS["realtime_engine"] = True
        print("✅ 實時引擎: 正常")
    except ImportError as e:
        X_SYSTEM_STATUS["realtime_engine"] = False
        print(f"❌ 實時引擎: {e}")
    
    # 測試pandas_ta信號解析器
    try:
        from X.app.services.pandas_ta_trading_signal_parser import PandasTATradingSignals, SignalType
        X_SYSTEM_STATUS["pandas_ta"] = True
        print("✅ pandas_ta信號解析器: 正常")
    except ImportError as e:
        X_SYSTEM_STATUS["pandas_ta"] = False
        print(f"❌ pandas_ta信號解析器: {e}")
    
    return X_SYSTEM_STATUS

async def test_database_connectivity():
    """測試數據庫連接"""
    print("\n🔗 測試數據庫連接...")
    
    if not X_SYSTEM_STATUS.get("database", False):
        print("❌ 數據庫模塊不可用，跳過連接測試")
        return False
    
    try:
        from X.app.core.database_separated import get_learning_db, get_signals_db, get_market_db
        
        # 測試learning_db
        try:
            learning_db = get_learning_db
            async for db in learning_db():
                cursor = await db.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = await cursor.fetchone()
                print(f"✅ learning_records.db: {table_count[0]} 個表")
                break
        except Exception as e:
            print(f"❌ learning_records.db: {e}")
        
        # 測試signals_db
        try:
            signals_db = get_signals_db
            async for db in signals_db():
                cursor = await db.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = await cursor.fetchone()
                print(f"✅ signals.db: {table_count[0]} 個表")
                break
        except Exception as e:
            print(f"❌ signals.db: {e}")
        
        # 測試market_data_db
        try:
            market_db = get_market_db
            async for db in market_db():
                cursor = await db.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = await cursor.fetchone()
                print(f"✅ market_data.db: {table_count[0]} 個表")
                break
        except Exception as e:
            print(f"❌ market_data.db: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 數據庫連接測試失敗: {e}")
        return False

async def test_quantum_engine_initialization():
    """測試量子引擎初始化"""
    print("\n⚛️ 測試量子引擎初始化...")
    
    if not QUANTUM_ENGINE_AVAILABLE:
        print("❌ 量子引擎不可用，跳過初始化測試")
        return None
    
    try:
        # 創建量子交易協調器
        coordinator = QuantumTradingCoordinator()
        await coordinator.initialize()
        
        print("✅ 量子交易協調器初始化成功")
        
        # 測試Phase數據流集成器
        phase_coordinator = await get_quantum_phase_coordinator()
        phase_status = phase_coordinator.get_phase_status()
        
        print("🔗 Phase集成狀態:")
        for phase, status in phase_status.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {phase}: {'可用' if status else '不可用'}")
        
        return coordinator
        
    except Exception as e:
        print(f"❌ 量子引擎初始化失敗: {e}")
        return None

async def test_quantum_analysis():
    """測試量子分析流程"""
    print("\n🧪 測試量子分析流程...")
    
    if not QUANTUM_ENGINE_AVAILABLE:
        print("❌ 量子引擎不可用，跳過分析測試")
        return False
    
    try:
        coordinator = QuantumTradingCoordinator()
        await coordinator.initialize()
        
        # 測試符號列表
        test_symbols = ['BTCUSDT', 'ETHUSDT']
        test_timeframes = ['1h']
        
        for symbol in test_symbols:
            for timeframe in test_timeframes:
                print(f"   🔍 分析 {symbol} {timeframe}...")
                
                try:
                    result = await coordinator.run_quantum_analysis(symbol, timeframe)
                    
                    if result:
                        print(f"   ✅ {symbol} {timeframe}: 量子決策生成")
                        print(f"      信號類型: {result['signal_type']}")
                        print(f"      信心度: {result['confidence']:.3f}")
                        print(f"      量子元數據: {len(result.get('quantum_metadata', {}))} 項")
                    else:
                        print(f"   📊 {symbol} {timeframe}: 未達量子塌縮條件")
                    
                except Exception as e:
                    print(f"   ❌ {symbol} {timeframe}: 分析失敗 - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 量子分析測試失敗: {e}")
        return False

async def test_phase_data_integration():
    """測試Phase數據集成"""
    print("\n🔗 測試Phase數據集成...")
    
    try:
        phase_coordinator = await get_quantum_phase_coordinator()
        
        # 測試數據集成
        test_symbol = "BTCUSDT"
        test_timeframe = "1h"
        
        print(f"   🔍 集成 {test_symbol} {test_timeframe} 的Phase數據...")
        
        integrated_data = await phase_coordinator.get_phase_integrated_data(test_symbol, test_timeframe)
        
        print("   ✅ Phase數據集成成功:")
        print(f"      符號: {integrated_data.get('symbol', 'N/A')}")
        print(f"      時間框架: {integrated_data.get('timeframe', 'N/A')}")
        print(f"      Lean信心度: {integrated_data.get('lean_confidence', 0.0):.3f}")
        print(f"      學習權重: {integrated_data.get('learning_weight', 0.0):.3f}")
        print(f"      技術分數: {integrated_data.get('technical_score', 0.0):.3f}")
        print(f"      執行就緒: {integrated_data.get('execution_ready', False)}")
        print(f"      集成信心度: {integrated_data.get('integrated_confidence', 0.0):.3f}")
        print(f"      量子就緒度: {integrated_data.get('quantum_readiness', 0.0):.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Phase數據集成測試失敗: {e}")
        return False

def check_file_system():
    """檢查文件系統結構"""
    print("\n📁 檢查文件系統結構...")
    
    # 檢查關鍵目錄
    key_dirs = [
        "./X",
        "./X/backend",
        "./X/app",
        "./X/databases",
        "./X/backend/phase1_signal_generation",
        "./X/backend/phase2_adaptive_learning",
        "./X/backend/phase3_execution_policy",
        "./X/backend/phase5_backtest_validation"
    ]
    
    for dir_path in key_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}: 存在")
        else:
            print(f"❌ {dir_path}: 不存在")
    
    # 檢查關鍵文件
    key_files = [
        "./quantum_precision_trading_engine.py",
        "./quantum_phase_data_integrator.py",
        "./X/app/core/database_separated.py",
        "./X/databases/signals.db",
        "./X/databases/learning_records.db",
        "./X/databases/market_data.db"
    ]
    
    for file_path in key_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}: 存在")
        else:
            print(f"❌ {file_path}: 不存在")

async def run_comprehensive_test():
    """運行全面測試"""
    print("🚀 Trading X - 量子交易引擎全面測試")
    print("=" * 60)
    print(f"測試時間: {datetime.now()}")
    print("")
    
    # 1. 檢查文件系統
    check_file_system()
    
    # 2. 測試X系統導入
    x_status = test_x_system_imports()
    
    # 3. 測試數據庫連接
    db_status = await test_database_connectivity()
    
    # 4. 測試量子引擎初始化
    quantum_engine = await test_quantum_engine_initialization()
    
    # 5. 測試Phase數據集成
    phase_integration_status = await test_phase_data_integration()
    
    # 6. 測試量子分析
    quantum_analysis_status = await test_quantum_analysis()
    
    # 總結
    print("\n" + "=" * 60)
    print("📊 測試結果總結:")
    print(f"   📁 文件系統: 手動檢查上方結果")
    print(f"   🔧 X系統模塊: {sum(x_status.values())}/{len(x_status)} 可用")
    print(f"   🔗 數據庫連接: {'✅ 正常' if db_status else '❌ 異常'}")
    print(f"   ⚛️ 量子引擎: {'✅ 正常' if quantum_engine else '❌ 異常'}")
    print(f"   🔗 Phase集成: {'✅ 正常' if phase_integration_status else '❌ 異常'}")
    print(f"   🧪 量子分析: {'✅ 正常' if quantum_analysis_status else '❌ 異常'}")
    
    # 最終評估
    all_systems_ready = (
        QUANTUM_ENGINE_AVAILABLE and
        db_status and
        quantum_engine is not None and
        phase_integration_status and
        quantum_analysis_status
    )
    
    if all_systems_ready:
        print("\n🎉 量子交易引擎已準備就緒!")
        print("   所有系統測試通過，可以開始量子交易")
        
        # 詢問是否運行實際交易測試
        user_input = input("\n🚀 是否立即啟動量子交易引擎? (y/N): ")
        if user_input.lower() == 'y':
            print("\n🌀 啟動量子交易引擎...")
            try:
                await quantum_engine.run_continuous_quantum_trading()
            except KeyboardInterrupt:
                print("\n🛑 用戶中斷量子交易")
            except Exception as e:
                print(f"\n❌ 量子交易運行錯誤: {e}")
    else:
        print("\n⚠️ 量子交易引擎未完全就緒")
        print("   請檢查上方測試結果，修復相關問題後重新測試")
    
    print("\n✅ 測試完成")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())
