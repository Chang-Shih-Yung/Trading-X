#!/usr/bin/env python3
"""
🚀 Trading X - 量子區塊鏈主池價格整合引擎
Quantum Blockchain Main Pool Price Integration Engine
整合區塊鏈主池價格數據的量子交易引擎
"""

import sys
import asyncio
import logging
from pathlib import Path

# 確保正確的路徑
current_dir = Path(__file__).parent
project_root = current_dir
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "X"))

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def start_quantum_blockchain_trading():
    """啟動量子區塊鏈交易引擎"""
    try:
        print("🌀 Trading X - 量子區塊鏈主池價格整合引擎")
        print("⚛️ 整合PancakeSwap主池價格 + 量子疊加決策")
        print("🔗 區塊鏈數據為主，幣安API智能回退")
        print("=" * 60)
        
        # 1. 初始化區塊鏈價格系統
        print("\n🔗 正在初始化區塊鏈主池價格系統...")
        try:
            from X.backend.phase1_signal_generation.onchain_data_connector.production_price_integration import get_price_system_manager
            price_manager = await get_price_system_manager()
            
            # 檢查系統狀態
            status = await price_manager.get_system_status()
            print(f"✅ 區塊鏈價格系統狀態:")
            print(f"   模式: {status['current_mode']}")
            print(f"   主池可用: {status['hybrid_available']}")
            print(f"   幣安回退: {status['binance_websocket_available']}")
            
            if 'onchain_status' in status:
                onchain = status['onchain_status']
                print(f"   主池數量: {onchain.get('main_pools_count', 0)}")
                print(f"   價格流: {onchain.get('streaming', False)}")
            
        except Exception as e:
            logger.warning(f"⚠️ 區塊鏈價格系統初始化失敗: {e}")
            print("🔄 將使用傳統價格源進行量子分析")
            price_manager = None
        
        # 2. 初始化量子引擎
        print("\n⚛️ 正在初始化量子交易引擎...")
        from X.quantum.simple_quantum_trading_engine import SimpleQuantumEngine
        
        quantum_engine = SimpleQuantumEngine()
        
        # 如果有區塊鏈價格系統，整合到量子引擎
        if price_manager:
            quantum_engine.blockchain_price_manager = price_manager
            print("✅ 量子引擎已整合區塊鏈主池價格系統")
        
        # 3. 執行量子分析測試
        print("\n🧪 執行量子區塊鏈價格分析測試...")
        
        # 測試區塊鏈價格獲取
        test_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        
        if price_manager:
            print("📊 測試區塊鏈主池價格:")
            for symbol in test_symbols:
                try:
                    price_data = await price_manager.get_price_data(symbol.replace('USDT', ''))
                    if price_data:
                        price = price_data['price']
                        source = price_data.get('source', 'unknown')
                        is_fallback = price_data.get('is_fallback', False)
                        status_icon = "🔄" if is_fallback else "🔗"
                        print(f"   {status_icon} {symbol}: ${price:.4f} (來源: {source})")
                    else:
                        print(f"   ❌ {symbol}: 價格獲取失敗")
                except Exception as e:
                    print(f"   ⚠️ {symbol}: {e}")
        
        # 4. 執行量子決策
        print("\n⚛️ 執行量子疊加決策分析...")
        decisions = await quantum_engine.run_quantum_analysis_cycle()
        
        if decisions:
            print(f"✅ 成功生成 {len(decisions)} 個量子決策:")
            for i, decision in enumerate(decisions, 1):
                print(f"   {i}. 🎯 {decision.symbol} {decision.timeframe} -> {decision.signal_type.value}")
                print(f"      ⚛️ 信心度: {decision.confidence:.3f}")
                print(f"      🏷️ 分層: {decision.tier.value}")
                print(f"      🌊 市場: {decision.market_regime.value}")
                print(f"      💰 進場: ${decision.entry_price:.4f}")
                print(f"      🛑 止損: ${decision.stop_loss:.4f}")
                print(f"      🎯 止盈: ${decision.take_profit:.4f}")
                print(f"      📊 風險回報: {decision.risk_reward_ratio:.2f}")
                print(f"      🧠 推理: {decision.reasoning}")
                print()
        else:
            print("📊 當前市場條件未觸發量子塌縮")
        
        # 5. 詢問是否啟動持續模式
        print("🌀 量子區塊鏈整合配置:")
        print(f"   量子塌縮閾值: {quantum_engine.collapse_threshold}")
        print(f"   分離閾值: {quantum_engine.separation_threshold}")
        print(f"   監控符號: {len(quantum_engine.monitored_symbols)} 個")
        print(f"   時間框架: {len(quantum_engine.timeframes)} 個")
        
        if price_manager:
            print(f"   🔗 區塊鏈主池: 已整合")
            print(f"   🔄 智能回退: 已配置")
        
        user_input = input("\n🌀 是否啟動持續量子區塊鏈交易模式? (y/N): ")
        if user_input.lower() == 'y':
            cycles_input = input("指定運行周期數 (直接回車表示無限): ")
            cycles = int(cycles_input) if cycles_input.strip() else None
            
            print("\n" + "="*60)
            print("⚛️ 量子區塊鏈交易引擎正在運行...")
            print("   🔗 使用PancakeSwap主池價格數據")
            print("   ⚛️ 量子疊加決策機制")
            print("   🔄 智能幣安API回退")
            print("   按 Ctrl+C 安全停止系統")
            print("="*60)
            
            await quantum_engine.run_continuous_quantum_trading(cycles)
        else:
            print("👋 量子區塊鏈交易引擎測試完成")
            
        # 6. 清理資源
        if price_manager:
            await price_manager.stop()
            
    except ImportError as e:
        logger.error(f"❌ 導入錯誤: {e}")
        print("請檢查量子模組和區塊鏈價格系統是否正確安裝")
    except Exception as e:
        logger.error(f"❌ 量子區塊鏈引擎啟動失敗: {e}")

if __name__ == "__main__":
    print("🎯 Trading X - 量子區塊鏈主池價格整合啟動")
    print("   區塊鏈主池 + 量子疊加 = 精確交易決策")
    asyncio.run(start_quantum_blockchain_trading())
