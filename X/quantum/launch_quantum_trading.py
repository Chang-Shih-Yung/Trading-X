#!/usr/bin/env python3
"""
🚀 Trading X - 量子交易引擎啟動器
正式啟動量子交易系統，與X系統Phase1A-Phase5完美融合

啟動流程：
1. 系統預檢 - 驗證所有組件
2. 數據庫初始化 - 確保所有數據庫連接正常  
3. Phase集成檢查 - 驗證Phase1A-Phase5數據流
4. 量子引擎啟動 - 開始量子疊加決策
5. 實時監控 - 持續監控量子交易表現
"""

import asyncio
import logging
import signal
import sys
import json
from datetime import datetime
from typing import Optional

# 添加路徑
sys.path.append('./X')
sys.path.append('./X/backend')
sys.path.append('.')

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'quantum_trading_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 導入量子模塊
from quantum_precision_trading_engine import QuantumTradingCoordinator
from quantum_phase_data_integrator import get_quantum_phase_coordinator

class QuantumTradingSystemLauncher:
    """量子交易系統啟動器"""
    
    def __init__(self):
        self.coordinator: Optional[QuantumTradingCoordinator] = None
        self.phase_coordinator = None
        self.running = False
        self.startup_time = None
        
        # 配置參數
        self.config = {
            "monitored_symbols": ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 'SOLUSDT'],
            "timeframes": ['1m', '5m', '15m', '1h', '4h'],
            "analysis_interval": 30,  # 秒
            "min_confidence_threshold": 0.65,
            "max_signals_per_hour": 10,
            "auto_save_interval": 300,  # 5分鐘
            "performance_log_interval": 1800  # 30分鐘
        }
        
        # 統計數據
        self.stats = {
            "startup_time": None,
            "total_analysis_cycles": 0,
            "total_decisions_generated": 0,
            "quantum_collapses": 0,
            "phase_integrations": 0,
            "last_decision_time": None,
            "uptime_seconds": 0
        }
    
    async def pre_startup_checks(self) -> bool:
        """啟動前檢查"""
        logger.info("🔍 執行啟動前系統檢查...")
        
        try:
            # 檢查量子引擎
            logger.info("   ⚛️ 檢查量子引擎...")
            test_coordinator = QuantumTradingCoordinator()
            await test_coordinator.initialize()
            logger.info("   ✅ 量子引擎: 正常")
            
            # 檢查Phase集成器
            logger.info("   🔗 檢查Phase集成器...")
            self.phase_coordinator = await get_quantum_phase_coordinator()
            phase_status = self.phase_coordinator.get_phase_status()
            
            available_phases = sum(phase_status.values())
            total_phases = len(phase_status)
            logger.info(f"   ✅ Phase集成器: {available_phases}/{total_phases} Phase可用")
            
            for phase, status in phase_status.items():
                status_icon = "✅" if status else "⚠️"
                logger.info(f"      {status_icon} {phase}: {'可用' if status else '不可用'}")
            
            # 檢查數據庫
            logger.info("   🔗 檢查數據庫連接...")
            from X.app.core.database_separated import get_learning_db, get_signals_db, get_market_db
            
            learning_db = get_learning_db
            signals_db = get_signals_db
            market_db = get_market_db
            
            # 測試連接
            async for db in learning_db():
                await db.execute("SELECT 1")
                break
            async for db in signals_db():
                await db.execute("SELECT 1")
                break
            async for db in market_db():
                await db.execute("SELECT 1")
                break
                
            logger.info("   ✅ 數據庫連接: 正常")
            
            # 檢查必要配置文件
            config_files = [
                "./X/app/config/pandas_ta_trading_signals.json",
                "./X/app/config/intelligent_consensus_config.json"
            ]
            
            for config_file in config_files:
                try:
                    with open(config_file, 'r') as f:
                        json.load(f)
                    logger.info(f"   ✅ 配置文件: {config_file}")
                except:
                    logger.warning(f"   ⚠️ 配置文件: {config_file} (可選)")
            
            logger.info("✅ 啟動前檢查完成，所有系統就緒")
            return True
            
        except Exception as e:
            logger.error(f"❌ 啟動前檢查失敗: {e}")
            return False
    
    async def initialize_quantum_system(self):
        """初始化量子系統"""
        logger.info("🚀 初始化量子交易系統...")
        
        try:
            # 創建量子協調器
            self.coordinator = QuantumTradingCoordinator()
            await self.coordinator.initialize()
            
            # 設置配置
            self.coordinator.monitored_symbols = self.config["monitored_symbols"]
            self.coordinator.timeframes = self.config["timeframes"]
            
            self.startup_time = datetime.now()
            self.stats["startup_time"] = self.startup_time
            
            logger.info("✅ 量子交易系統初始化完成")
            logger.info(f"   監控符號: {len(self.config['monitored_symbols'])} 個")
            logger.info(f"   時間框架: {len(self.config['timeframes'])} 個")
            logger.info(f"   分析間隔: {self.config['analysis_interval']} 秒")
            
        except Exception as e:
            logger.error(f"❌ 量子系統初始化失敗: {e}")
            raise
    
    async def start_quantum_trading(self):
        """啟動量子交易主循環"""
        logger.info("🌀 啟動量子交易主循環...")
        
        self.running = True
        cycle_count = 0
        last_save_time = datetime.now()
        last_log_time = datetime.now()
        
        try:
            while self.running:
                cycle_start = datetime.now()
                cycle_count += 1
                self.stats["total_analysis_cycles"] = cycle_count
                
                logger.info(f"⚛️ 量子分析周期 #{cycle_count}")
                
                # 執行量子分析
                decisions_this_cycle = 0
                
                for symbol in self.config["monitored_symbols"]:
                    for timeframe in self.config["timeframes"]:
                        try:
                            decision = await self.coordinator.run_quantum_analysis(symbol, timeframe)
                            
                            if decision:
                                decisions_this_cycle += 1
                                self.stats["total_decisions_generated"] += 1
                                self.stats["last_decision_time"] = datetime.now()
                                
                                # 記錄量子塌縮事件
                                if decision.get("quantum_metadata", {}).get("collapse_readiness", 0) > 0.7:
                                    self.stats["quantum_collapses"] += 1
                                
                                logger.info(f"   💎 量子決策: {symbol} {timeframe} -> {decision['signal_type']} "
                                           f"(信心度: {decision['confidence']:.3f})")
                        
                        except Exception as e:
                            logger.error(f"   ❌ {symbol} {timeframe} 分析失敗: {e}")
                
                # 統計本周期
                cycle_duration = (datetime.now() - cycle_start).total_seconds()
                logger.info(f"   📊 周期 #{cycle_count}: {decisions_this_cycle} 個決策，耗時 {cycle_duration:.2f}s")
                
                # 定期保存和日誌
                now = datetime.now()
                
                # 自動保存統計
                if (now - last_save_time).total_seconds() > self.config["auto_save_interval"]:
                    await self._save_statistics()
                    last_save_time = now
                
                # 性能日誌
                if (now - last_log_time).total_seconds() > self.config["performance_log_interval"]:
                    await self._log_performance_summary()
                    last_log_time = now
                
                # 更新運行時間
                if self.startup_time:
                    self.stats["uptime_seconds"] = (now - self.startup_time).total_seconds()
                
                # 休眠到下個周期
                await asyncio.sleep(self.config["analysis_interval"])
        
        except Exception as e:
            logger.error(f"❌ 量子交易主循環錯誤: {e}")
        finally:
            logger.info("🔚 量子交易主循環已停止")
    
    async def _save_statistics(self):
        """保存統計數據"""
        try:
            stats_file = f"quantum_trading_stats_{datetime.now().strftime('%Y%m%d')}.json"
            
            # 添加時間戳
            save_data = self.stats.copy()
            save_data["last_save_time"] = datetime.now().isoformat()
            save_data["config"] = self.config
            
            # 序列化datetime對象
            for key, value in save_data.items():
                if isinstance(value, datetime):
                    save_data[key] = value.isoformat()
            
            with open(stats_file, 'w') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"📊 統計數據已保存到 {stats_file}")
            
        except Exception as e:
            logger.error(f"❌ 保存統計數據失敗: {e}")
    
    async def _log_performance_summary(self):
        """記錄性能總結"""
        uptime_hours = self.stats["uptime_seconds"] / 3600
        
        logger.info("📈 量子交易系統性能總結:")
        logger.info(f"   ⏱️ 運行時間: {uptime_hours:.1f} 小時")
        logger.info(f"   🔄 分析周期: {self.stats['total_analysis_cycles']} 次")
        logger.info(f"   💎 總決策數: {self.stats['total_decisions_generated']} 個")
        logger.info(f"   ⚛️ 量子塌縮: {self.stats['quantum_collapses']} 次")
        
        if self.stats["total_analysis_cycles"] > 0:
            decision_rate = self.stats["total_decisions_generated"] / self.stats["total_analysis_cycles"]
            logger.info(f"   📊 決策率: {decision_rate:.3f} 決策/周期")
        
        if uptime_hours > 0:
            decisions_per_hour = self.stats["total_decisions_generated"] / uptime_hours
            logger.info(f"   ⚡ 效率: {decisions_per_hour:.1f} 決策/小時")
    
    def setup_signal_handlers(self):
        """設置信號處理器"""
        def signal_handler(signum, frame):
            logger.info(f"🛑 收到停止信號 ({signum})，正在優雅關閉...")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def shutdown(self):
        """系統關閉"""
        logger.info("🔚 正在關閉量子交易系統...")
        
        self.running = False
        
        # 保存最終統計
        await self._save_statistics()
        await self._log_performance_summary()
        
        # 停止量子協調器
        if self.coordinator:
            self.coordinator.stop()
        
        logger.info("✅ 量子交易系統已安全關閉")

async def main():
    """主函數"""
    print("🚀 Trading X - 量子交易引擎啟動器")
    print("⚛️ 基於X系統Phase1A-Phase5的量子疊加決策引擎")
    print("=" * 70)
    
    launcher = QuantumTradingSystemLauncher()
    
    try:
        # 設置信號處理
        launcher.setup_signal_handlers()
        
        # 啟動前檢查
        logger.info("🔍 執行系統預檢...")
        if not await launcher.pre_startup_checks():
            logger.error("❌ 系統預檢失敗，無法啟動")
            return 1
        
        # 初始化系統
        logger.info("🚀 初始化量子系統...")
        await launcher.initialize_quantum_system()
        
        # 確認啟動
        print(f"\n✅ 量子交易系統準備完成 ({datetime.now()})")
        print(f"📊 監控符號: {launcher.config['monitored_symbols']}")
        print(f"⏱️ 分析間隔: {launcher.config['analysis_interval']} 秒")
        print(f"🎯 最小信心度: {launcher.config['min_confidence_threshold']}")
        
        user_input = input("\n🚀 是否立即開始量子交易? (Y/n): ")
        if user_input.lower() not in ['n', 'no']:
            
            logger.info("🌀 啟動量子交易...")
            print("\n" + "="*50)
            print("⚛️ 量子交易引擎正在運行...")
            print("   按 Ctrl+C 安全停止系統")
            print("="*50)
            
            # 啟動量子交易
            await launcher.start_quantum_trading()
        else:
            logger.info("👋 用戶選擇不啟動交易")
        
    except KeyboardInterrupt:
        logger.info("🛑 用戶中斷")
    except Exception as e:
        logger.error(f"❌ 系統錯誤: {e}")
        return 1
    finally:
        await launcher.shutdown()
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
