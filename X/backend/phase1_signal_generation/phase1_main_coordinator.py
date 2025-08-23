"""
🎯 Trading X - Phase1 主協調器
統一管理整個 Phase1 信號生成流水線
WebSocket → Phase1A → Phase1B → Phase1C → 輸出
實現 < 180ms 端到端處理延遲
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import time

# 導入 Phase1 組件
from .websocket_realtime_driver.websocket_realtime_driver import (
    websocket_realtime_driver, start_realtime_driver, stop_realtime_driver
)
from .phase1a_basic_signal_generation.phase1a_basic_signal_generation import (
    phase1a_signal_generator, start_phase1a_generator, stop_phase1a_generator
)
from .phase1b_volatility_adaptation.phase1b_volatility_adaptation import (
    phase1b_volatility_adapter, start_phase1b_adapter, stop_phase1b_adapter
)
from .unified_signal_pool.unified_signal_candidate_pool import (
    unified_signal_pool, start_unified_pool, stop_unified_pool
)
from .intelligent_trigger_engine import (
    intelligent_trigger_engine, start_intelligent_trigger_engine, stop_intelligent_trigger_engine,
    subscribe_to_intelligent_signals, process_realtime_price_update, get_intelligent_trigger_status
)
# 🔗 真實區塊鏈數據連接器導入 (主要)
from .onchain_data_connector import (
    real_blockchain_connector, start_real_blockchain_connector, stop_real_blockchain_connector,
    get_real_onchain_price, get_supported_real_symbols, RealOnChainPrice
)
# 原有 API 連接器導入 (備用)
from .onchain_data_connector import (
    onchain_data_connector, start_onchain_connector, stop_onchain_connector,
    get_onchain_price, get_supported_onchain_symbols, OnChainPrice
)

logger = logging.getLogger(__name__)

@dataclass
class Phase1Performance:
    """Phase1 性能指標"""
    total_signals_processed: int = 0
    average_processing_time: float = 0.0
    websocket_latency: float = 0.0
    phase1a_throughput: float = 0.0
    phase1b_filter_rate: float = 0.0
    phase1c_pool_size: int = 0
    last_update_time: Optional[datetime] = None

@dataclass  
class Phase1Status:
    """Phase1 狀態管理 - 真實區塊鏈連接器狀態"""
    onchain_active: bool = False  # 🔗 鏈上數據連接器狀態 (API 或真實區塊鏈)
    real_blockchain_active: bool = False  # 🔗 新增：真實區塊鏈連接器狀態
    websocket_active: bool = False
    indicator_engine_active: bool = False
    phase1a_active: bool = False
    phase1b_active: bool = False
    phase1c_active: bool = False
    intelligent_trigger_active: bool = False
    coordinator_running: bool = False
    total_processed_signals: int = 0
    last_signal_time: Optional[datetime] = None
    error_count: int = 0
    # 🔗 鏈上數據指標
    onchain_symbols_active: int = 0
    onchain_last_update: Optional[datetime] = None
    binance_fallback_count: int = 0
    real_blockchain_contracts_active: int = 0  # 活躍的智能合約數量
    
class Phase1MainCoordinator:
    """Phase1 主協調器
    
    職責：
    1. 統一管理 WebSocket → Phase1A → Phase1B → Phase1C → 智能觸發 流水線
    2. 監控各組件健康狀態和性能指標
    3. 處理組件間的信號傳遞和數據流
    4. 提供統一的啟動、停止和配置接口
    5. 實現 < 180ms 端到端處理延遲目標
    """
    
    def __init__(self):
        self.config = self._load_config()
        self.status = Phase1Status()
        self.performance = Phase1Performance()
        self.coordinator_tasks = []
        self.signal_subscribers = []
        
        logger.info("Phase1 主協調器初始化完成")
    
    def _load_config(self) -> Dict[str, Any]:
        """載入配置"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), "phase1_config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._get_default_config()
        except Exception as e:
            logger.warning(f"載入配置失敗，使用預設配置: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """獲取預設配置"""
        return {
            "startup_sequence_delays": {
                "websocket_to_indicator": 1.0,
                "indicator_to_phase1a": 0.5,
                "phase1a_to_phase1b": 0.3,
                "phase1b_to_phase1c": 0.3,
                "phase1c_to_trigger": 0.2
            },
            "performance_targets": {
                "max_end_to_end_latency": 180,  # ms
                "min_throughput": 100,  # signals/sec
                "max_error_rate": 0.01  # 1%
            },
            "monitoring": {
                "health_check_interval": 5,  # seconds
                "performance_report_interval": 30,  # seconds
                "log_level": "INFO"
            }
        }
    
    async def start_phase1_pipeline(self, symbols: List[str] = None) -> bool:
        """啟動完整的 Phase1 處理流水線 - 整合鏈上數據優先策略"""
        
        try:
            logger.info("🚀 開始啟動 Phase1 處理流水線...")
            logger.info("🔗 優先使用鏈上數據，Binance API 作為備用")
            logger.info("="*60)
            
            # 設定七大幣種
            if symbols is None:
                symbols = ["BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "BNB"]
            
            # 0. 🔗 優先啟動真實區塊鏈連接器 (無限制)
            logger.info("步驟 0/7: 🔗 啟動真實區塊鏈連接器 (完全無限制)")
            real_blockchain_success = await start_real_blockchain_connector(symbols)
            if real_blockchain_success:
                logger.info("✅ 真實區塊鏈連接器啟動完成 - 七大幣種直接智能合約互動")
                self.status.onchain_active = True
                self.status.real_blockchain_active = True
            else:
                logger.warning("⚠️ 真實區塊鏈連接器啟動失敗，嘗試備用 API 連接器")
                api_backup_success = await start_onchain_connector(symbols)
                if api_backup_success:
                    logger.info("✅ 備用 API 連接器啟動完成")
                    self.status.onchain_active = True
                    self.status.real_blockchain_active = False
                else:
                    logger.warning("⚠️ 所有鏈上數據連接器啟動失敗，將依賴 Binance API")
                    self.status.onchain_active = False
                    self.status.real_blockchain_active = False
            
            # 1. 啟動 WebSocket 實時數據驅動器 (備用數據源)
            logger.info("步驟 1/7: 啟動 WebSocket 實時數據驅動器 (Binance 備用)")
            binance_symbols = [f"{symbol}USDT" for symbol in symbols if symbol != "USDT"]
            try:
                await start_realtime_driver(binance_symbols)
                await asyncio.sleep(self.config["startup_sequence_delays"]["websocket_to_indicator"])
                self.status.websocket_active = True
                logger.info("✅ WebSocket 實時數據驅動器啟動完成 (備用數據源)")
            except Exception as e:
                logger.warning(f"⚠️ Binance WebSocket 啟動失敗: {e} (鏈上數據將承擔主要角色)")
                self.status.websocket_active = False
            
            # 2. 啟動指標依賴引擎 (整合鏈上+備用數據)
            logger.info("步驟 2/7: 啟動混合數據指標依賴引擎")
            try:
                await start_indicator_engine(websocket_realtime_driver)
                await asyncio.sleep(self.config["startup_sequence_delays"]["indicator_to_phase1a"])
                self.status.indicator_engine_active = True
                logger.info("✅ 混合數據指標依賴引擎啟動完成")
            except Exception as e:
                logger.error(f"❌ 指標依賴引擎啟動失敗: {e}")
                # 繼續運行，依賴鏈上數據
            
            # 3. 啟動 Phase1A 基礎信號生成器
            logger.info("步驟 3/7: 啟動 Phase1A 基礎信號生成器")
            await start_phase1a_generator(indicator_dependency_graph)
            await asyncio.sleep(self.config["startup_sequence_delays"]["phase1a_to_phase1b"])
            self.status.phase1a_active = True
            logger.info("✅ Phase1A 基礎信號生成器啟動完成")
            
            # 4. 啟動 Phase1B 信號過濾增強器
            logger.info("步驟 4/7: 啟動 Phase1B 信號過濾增強器")
            await start_phase1b_adapter()
            await asyncio.sleep(self.config["startup_sequence_delays"]["phase1b_to_phase1c"])
            self.status.phase1b_active = True
            logger.info("✅ Phase1B 信號過濾增強器啟動完成")
            
            # 5. 啟動 Phase1C 統一信號池
            logger.info("步驟 5/7: 啟動 Phase1C 統一信號池")
            await start_unified_pool()
            self.status.phase1c_active = True
            logger.info("✅ Phase1C 統一信號池啟動完成")
            
            # 6. 啟動智能觸發引擎
            logger.info("步驟 6/7: 啟動智能觸發引擎")
            await start_intelligent_trigger_engine()
            self.status.intelligent_trigger_active = True
            logger.info("✅ 智能觸發引擎啟動完成")
            
            # 7. 🔗 設定鏈上數據優先的信號處理鏈
            logger.info("步驟 7/7: 設定鏈上數據優先處理鏈")
            await self._setup_onchain_priority_signal_chain()
            
            # 建立信號處理鏈
            await self._setup_signal_processing_chain()
            
            # 啟動協調器任務
            self.coordinator_tasks = [
                asyncio.create_task(self._health_monitor()),
                asyncio.create_task(self._performance_monitor()),
                asyncio.create_task(self._signal_flow_coordinator()),
                asyncio.create_task(self._onchain_data_monitor())  # 🔗 新增鏈上數據監控
            ]
            
            self.status.coordinator_running = True
            
            logger.info("="*60)
            logger.info("🎉 Phase1 處理流水線啟動完成！")
            logger.info(f"🔗 真實區塊鏈狀態: {'✅ 活躍 (智能合約直接互動)' if self.status.real_blockchain_active else '❌ 離線'}")
            logger.info(f"🔗 鏈上數據狀態: {'✅ 活躍' if self.status.onchain_active else '❌ 離線'}")
            logger.info(f"📡 Binance 備用狀態: {'✅ 活躍' if self.status.websocket_active else '❌ 離線'}")
            logger.info(f"📊 目標延遲: < {self.config['performance_targets']['max_end_to_end_latency']}ms")
            logger.info(f"📈 目標吞吐量: > {self.config['performance_targets']['min_throughput']} signals/sec")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Phase1 流水線啟動失敗: {e}")
            await self._emergency_shutdown()
            return False
    
    async def stop_phase1_pipeline(self) -> bool:
        """停止 Phase1 處理流水線"""
        
        try:
            logger.info("🛑 開始停止 Phase1 處理流水線...")
            
            # 停止協調器任務
            for task in self.coordinator_tasks:
                task.cancel()
            self.coordinator_tasks.clear()
            self.status.coordinator_running = False
            
            logger.info("停止智能觸發引擎")
            await stop_intelligent_trigger_engine()
            self.status.intelligent_trigger_active = False
            
            logger.info("停止 Phase1C 統一信號池")
            await stop_unified_pool()
            self.status.phase1c_active = False
            
            logger.info("停止 Phase1B 信號過濾增強器")
            await stop_phase1b_adapter()
            self.status.phase1b_active = False
            
            logger.info("停止 Phase1A 基礎信號生成器")
            await stop_phase1a_generator()
            self.status.phase1a_active = False
            
            logger.info("停止指標依賴引擎")
            await stop_indicator_engine()
            self.status.indicator_engine_active = False
            
            logger.info("停止 WebSocket 實時數據驅動器")
            await stop_realtime_driver()
            self.status.websocket_active = False
            
            logger.info("✅ Phase1 處理流水線停止完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ Phase1 流水線停止失敗: {e}")
            return False
    
    async def _setup_signal_processing_chain(self):
        """建立信號處理鏈"""
        try:
            # 訂閱各組件的輸出
            websocket_realtime_driver.subscribe_to_price_updates(self._on_websocket_price_update)
            intelligent_trigger_engine.subscribe_to_intelligent_signals(self._on_intelligent_trigger_signal)
            phase1a_signal_generator.subscribe_to_basic_signals(self._on_phase1a_signals)
            unified_signal_pool.subscribe_to_unified_signals(self._on_phase1c_output)
            
            logger.info("✅ 信號處理鏈建立完成")
            
        except Exception as e:
            logger.error(f"❌ 信號處理鏈建立失敗: {e}")
            raise
    
    async def _on_websocket_price_update(self, symbol: str, price_data: Dict[str, Any]):
        """處理 WebSocket 價格更新"""
        try:
            # 更新性能指標
            self.performance.last_update_time = datetime.now()
            
            # 傳遞給智能觸發引擎進行實時處理
            await process_realtime_price_update(symbol, price_data)
            
        except Exception as e:
            logger.error(f"❌ WebSocket 價格更新處理失敗: {e}")
            self.status.error_count += 1
    
    async def _on_intelligent_trigger_signal(self, signal: Dict[str, Any]):
        """處理智能觸發信號"""
        try:
            # 添加到統一信號池
            signal_id = await unified_signal_pool.add_intelligent_signal(signal)
            
            logger.debug(f"智能觸發信號已添加到統一池: {signal_id}")
            
        except Exception as e:
            logger.error(f"❌ 智能觸發信號處理失敗: {e}")
            self.status.error_count += 1
    
    async def _on_phase1a_signals(self, signals: List[Any]):
        """處理 Phase1A 基礎信號"""
        try:
            if not signals:
                return
            
            # 通過 Phase1B 過濾器處理
            filtered_signals = await phase1b_volatility_adapter.process_signals(signals)
            
            if filtered_signals:
                # 添加到 Phase1C 統一信號池
                added_signal_ids = await unified_signal_pool.add_signals(filtered_signals)
                logger.debug(f"Phase1A 信號已處理並添加到統一池: {len(added_signal_ids)} 個")
            
            # 更新統計
            self.status.total_processed_signals += len(signals)
            self.status.last_signal_time = datetime.now()
            
        except Exception as e:
            logger.error(f"❌ Phase1A 信號處理失敗: {e}")
            self.status.error_count += 1
    
    async def _on_phase1c_output(self, unified_signals: List[Any]):
        """處理 Phase1C 統一輸出"""
        try:
            if not unified_signals:
                return
            
            # 通知所有訂閱者
            for subscriber in self.signal_subscribers:
                try:
                    if asyncio.iscoroutinefunction(subscriber):
                        await subscriber(unified_signals)
                    else:
                        subscriber(unified_signals)
                except Exception as e:
                    logger.error(f"❌ 訂閱者通知失敗: {e}")
            
            logger.info(f"📤 Phase1 最終輸出: {len(unified_signals)} 個統一信號")
            
        except Exception as e:
            logger.error(f"❌ Phase1C 輸出處理失敗: {e}")
            self.status.error_count += 1
    
    def subscribe_to_phase1_output(self, callback: Callable):
        """訂閱 Phase1 最終輸出"""
        self.signal_subscribers.append(callback)
        logger.info(f"新訂閱者已添加，當前訂閱者數量: {len(self.signal_subscribers)}")
    
    async def _health_monitor(self):
        """健康監控任務"""
        while self.status.coordinator_running:
            try:
                await asyncio.sleep(self.config["monitoring"]["health_check_interval"])
                
                # 檢查各組件狀態
                websocket_ok = websocket_realtime_driver.is_connected
                indicator_ok = indicator_dependency_graph.is_running
                phase1a_ok = phase1a_signal_generator.is_running
                phase1b_ok = phase1b_volatility_adapter.is_running
                phase1c_ok = unified_signal_pool.is_running
                trigger_ok = get_intelligent_trigger_status()
                
                if not all([websocket_ok, indicator_ok, phase1a_ok, phase1b_ok, phase1c_ok, trigger_ok]):
                    logger.warning("⚠️ 檢測到組件健康狀態異常")
                    
                    # 記錄詳細狀態
                    status_details = {
                        "websocket": websocket_ok,
                        "indicator": indicator_ok, 
                        "phase1a": phase1a_ok,
                        "phase1b": phase1b_ok,
                        "phase1c": phase1c_ok,
                        "trigger": trigger_ok
                    }
                    
                    for component, status in status_details.items():
                        if not status:
                            logger.error(f"❌ {component} 組件狀態異常")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ 健康監控錯誤: {e}")
    
    async def _performance_monitor(self):
        """性能監控任務"""
        while self.status.coordinator_running:
            try:
                await asyncio.sleep(self.config["monitoring"]["performance_report_interval"])
                
                # 收集性能數據
                phase1b_stats = await phase1b_volatility_adapter.get_filter_statistics()
                phase1c_stats = await unified_signal_pool.get_pool_status()
                
                # 更新性能指標
                self.performance.phase1b_filter_rate = phase1b_stats.get("filter_rate", 0.0)
                self.performance.phase1c_pool_size = phase1c_stats.get("pool_size", 0)
                
                # 計算平均處理時間
                if self.status.total_processed_signals > 0:
                    total_time = (datetime.now() - self.performance.last_update_time).total_seconds()
                    self.performance.average_processing_time = total_time / self.status.total_processed_signals
                
                # 記錄性能報告
                logger.info(f"📊 Phase1 性能報告:")
                logger.info(f"   總處理信號: {self.status.total_processed_signals}")
                logger.info(f"   平均處理時間: {self.performance.average_processing_time:.3f}ms")
                logger.info(f"   Phase1B 過濾率: {self.performance.phase1b_filter_rate:.2%}")
                logger.info(f"   Phase1C 池大小: {self.performance.phase1c_pool_size}")
                logger.info(f"   錯誤計數: {self.status.error_count}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ 性能監控錯誤: {e}")
    
    async def _signal_flow_coordinator(self):
        """信號流協調任務"""
        while self.status.coordinator_running:
            try:
                await asyncio.sleep(1.0)  # 每秒檢查一次
                
                # 檢查信號流是否暢通
                phase1c_stats = await unified_signal_pool.get_pool_status()
                
                # 如果池中積壓過多信號，觸發處理
                if phase1c_stats.get("pool_size", 0) > 100:
                    logger.warning("⚠️ Phase1C 信號池積壓過多，觸發緊急處理")
                    # 可以在這裡實現緊急處理邏輯
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ 信號流協調錯誤: {e}")
    
    async def get_phase1_status(self) -> Dict[str, Any]:
        """獲取 Phase1 系統狀態"""
        return {
            "status": asdict(self.status),
            "performance": asdict(self.performance),
            "config": self.config,
            "component_status": {
                "websocket": websocket_realtime_driver.is_connected if hasattr(websocket_realtime_driver, 'is_connected') else False,
                "indicator": indicator_dependency_graph.is_running if hasattr(indicator_dependency_graph, 'is_running') else False,
                "phase1a": phase1a_signal_generator.is_running if hasattr(phase1a_signal_generator, 'is_running') else False,
                "phase1b": phase1b_volatility_adapter.is_running if hasattr(phase1b_volatility_adapter, 'is_running') else False,
                "phase1c": unified_signal_pool.is_running if hasattr(unified_signal_pool, 'is_running') else False,
                "trigger": get_intelligent_trigger_status() if callable(get_intelligent_trigger_status) else False
            }
        }
    
    async def restart_component(self, component: str) -> bool:
        """重啟指定組件"""
        try:
            logger.info(f"🔄 重啟組件: {component}")
            
            if component == 'websocket':
                await stop_realtime_driver()
                await start_realtime_driver()
                self.status.websocket_active = True
                
            elif component == 'indicator':
                await stop_indicator_engine()
                await start_indicator_engine(websocket_realtime_driver)
                self.status.indicator_engine_active = True
                
            elif component == 'phase1a':
                await stop_phase1a_generator()
                await start_phase1a_generator(websocket_realtime_driver)
                self.status.phase1a_active = True
                
            elif component == 'phase1b':
                await stop_phase1b_adapter()
                await start_phase1b_adapter()
                self.status.phase1b_active = True
                
            elif component == 'phase1c':
                await stop_unified_pool()
                await start_unified_pool()
                self.status.phase1c_active = True
                
            elif component == 'trigger':
                await stop_intelligent_trigger_engine()
                await start_intelligent_trigger_engine()
                self.status.intelligent_trigger_active = True
                
            else:
                logger.error(f"❌ 未知組件: {component}")
                return False
            
            logger.info(f"✅ 組件重啟成功: {component}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 組件重啟失敗: {component} - {e}")
            return False
    
    async def _emergency_shutdown(self):
        """緊急關閉"""
        logger.error("🚨 執行緊急關閉...")
        try:
            await self.stop_phase1_pipeline()
        except Exception as e:
            logger.error(f"❌ 緊急關閉失敗: {e}")

    # === 🔗 新增：鏈上數據相關方法 ===
    
    async def _setup_onchain_priority_signal_chain(self):
        """設定鏈上數據優先的信號處理鏈"""
        try:
            logger.info("🔗 設定鏈上數據優先處理策略...")
            
            # 檢查支援的鏈上幣種
            supported_symbols = await get_supported_onchain_symbols()
            self.status.onchain_symbols_active = len(supported_symbols)
            
            logger.info(f"✅ 鏈上數據支援 {len(supported_symbols)} 個幣種: {supported_symbols}")
            
            # 設定數據源優先級
            self.data_source_priority = {
                'primary': 'onchain',      # 🔗 鏈上數據為主要來源
                'fallback': 'binance_api', # 📡 Binance API 為備用
                'emergency': 'static'      # 📊 靜態數據為緊急備用
            }
            
            logger.info("✅ 鏈上數據優先處理鏈設定完成")
            
        except Exception as e:
            logger.error(f"❌ 鏈上數據處理鏈設定失敗: {e}")
    
    async def _onchain_data_monitor(self):
        """🔗 鏈上數據監控任務"""
        while self.status.coordinator_running:
            try:
                # 檢查鏈上數據狀態
                onchain_status = await self._check_onchain_data_health()
                
                if onchain_status['healthy']:
                    self.status.onchain_last_update = datetime.now()
                    
                    # 記錄鏈上數據統計
                    active_symbols = onchain_status.get('active_symbols', 0)
                    latest_prices = onchain_status.get('latest_prices', {})
                    
                    logger.debug(f"🔗 鏈上數據健康: {active_symbols} 幣種活躍")
                    
                    # 檢查是否需要啟用 Binance 備用
                    if active_symbols < 5:  # 如果活躍幣種少於5個
                        logger.warning(f"⚠️ 鏈上數據覆蓋不足 ({active_symbols}/7)，增強 Binance 備用")
                        self.status.binance_fallback_count += 1
                    
                else:
                    logger.warning("⚠️ 鏈上數據健康檢查失敗，依賴 Binance 備用")
                    self.status.binance_fallback_count += 1
                
                await asyncio.sleep(10)  # 每10秒檢查一次
                
            except Exception as e:
                logger.error(f"❌ 鏈上數據監控錯誤: {e}")
                await asyncio.sleep(30)  # 錯誤時等待更久
    
    async def _check_onchain_data_health(self) -> Dict[str, Any]:
        """檢查鏈上數據健康狀態"""
        try:
            supported_symbols = await get_supported_onchain_symbols()
            health_status = {
                'healthy': True,
                'active_symbols': 0,
                'latest_prices': {},
                'issues': []
            }
            
            # 檢查每個幣種的最新價格
            for symbol in supported_symbols:
                try:
                    price_data = await get_onchain_price(symbol)
                    if price_data and price_data.price_usd > 0:
                        health_status['active_symbols'] += 1
                        health_status['latest_prices'][symbol] = {
                            'price': price_data.price_usd,
                            'source': price_data.price_source,
                            'confidence': price_data.confidence,
                            'timestamp': price_data.timestamp
                        }
                        
                        # 檢查數據新鮮度 (5分鐘內)
                        age = datetime.now() - price_data.timestamp
                        if age.total_seconds() > 300:
                            health_status['issues'].append(f"{symbol} 數據過期 ({age.total_seconds():.1f}s)")
                    else:
                        health_status['issues'].append(f"{symbol} 價格數據無效")
                        
                except Exception as e:
                    health_status['issues'].append(f"{symbol} 查詢失敗: {e}")
            
            # 判斷整體健康狀態
            if health_status['active_symbols'] < 4:  # 少於4個幣種活躍
                health_status['healthy'] = False
                health_status['issues'].append("活躍幣種數量不足")
            
            return health_status
            
        except Exception as e:
            return {
                'healthy': False,
                'active_symbols': 0,
                'latest_prices': {},
                'issues': [f"健康檢查異常: {e}"]
            }
    
    async def get_market_data_unified(self, symbol: str) -> Optional[Dict[str, Any]]:
        """🔗 統一市場數據獲取接口 - 鏈上優先策略"""
        try:
            # 1. 優先嘗試鏈上數據
            if self.status.onchain_active:
                onchain_price = await get_onchain_price(symbol)
                if onchain_price and onchain_price.confidence > 0.8:
                    logger.debug(f"🔗 {symbol} 使用鏈上數據: ${onchain_price.price_usd:.2f}")
                    return {
                        'symbol': symbol,
                        'price': onchain_price.price_usd,
                        'volume': onchain_price.volume_24h,
                        'timestamp': onchain_price.timestamp,
                        'source': 'onchain',
                        'confidence': onchain_price.confidence,
                        'metadata': {
                            'price_source': onchain_price.price_source,
                            'liquidity': onchain_price.liquidity,
                            'price_impact': onchain_price.price_impact
                        }
                    }
            
            # 2. 備用：使用 Binance WebSocket 數據
            if self.status.websocket_active:
                # 這裡應該從 WebSocket 獲取數據
                # 暫時返回標準化格式的備用數據結構
                logger.debug(f"📡 {symbol} 使用 Binance 備用數據")
                self.status.binance_fallback_count += 1
                return {
                    'symbol': symbol,
                    'price': 0.0,  # 實際需要從 WebSocket 獲取
                    'volume': 0.0,
                    'timestamp': datetime.now(),
                    'source': 'binance_fallback',
                    'confidence': 0.7,
                    'metadata': {'fallback_reason': 'onchain_unavailable'}
                }
            
            # 3. 緊急備用：返回空數據
            logger.warning(f"⚠️ {symbol} 所有數據源不可用")
            return None
            
        except Exception as e:
            logger.error(f"❌ {symbol} 統一數據獲取失敗: {e}")
            return None
    
    async def get_onchain_status_report(self) -> Dict[str, Any]:
        """🔗 獲取鏈上數據狀態報告"""
        try:
            health_status = await self._check_onchain_data_health()
            
            return {
                'onchain_active': self.status.onchain_active,
                'active_symbols': health_status['active_symbols'],
                'supported_symbols': await get_supported_onchain_symbols(),
                'latest_prices': health_status['latest_prices'],
                'binance_fallback_count': self.status.binance_fallback_count,
                'last_update': self.status.onchain_last_update,
                'issues': health_status['issues'],
                'data_source_priority': getattr(self, 'data_source_priority', {}),
                'health_score': health_status['active_symbols'] / 7 * 100  # 7個幣種的健康分數
            }
            
        except Exception as e:
            logger.error(f"❌ 鏈上狀態報告生成失敗: {e}")
            return {'error': str(e)}

# 全局實例 - 🔗 整合鏈上數據支援
_phase1_coordinator = None

async def start_phase1_system(symbols: List[str] = None) -> bool:
    """啟動 Phase1 系統 - 🔗 支援鏈上數據優先"""
    global _phase1_coordinator
    _phase1_coordinator = Phase1MainCoordinator()
    return await _phase1_coordinator.start_phase1_pipeline(symbols)

async def start_phase1_with_onchain_priority(symbols: List[str] = None) -> bool:
    """🔗 啟動支援鏈上數據優先的 Phase1 系統"""
    if symbols is None:
        symbols = ["BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "BNB"]
    return await start_phase1_system(symbols)

async def get_unified_market_data(symbol: str) -> Optional[Dict[str, Any]]:
    """🔗 統一市場數據獲取 - 鏈上優先"""
    global _phase1_coordinator
    if _phase1_coordinator:
        return await _phase1_coordinator.get_market_data_unified(symbol)
    return None

async def get_phase1_onchain_status() -> Dict[str, Any]:
    """🔗 獲取 Phase1 鏈上數據狀態"""
    global _phase1_coordinator
    if _phase1_coordinator:
        return await _phase1_coordinator.get_onchain_status_report()
    return {"error": "Phase1 coordinator not initialized"}

async def stop_phase1_system() -> bool:
    """停止 Phase1 系統"""
    global _phase1_coordinator
    if _phase1_coordinator:
        return await _phase1_coordinator.stop_phase1_pipeline()
    return False

def subscribe_to_phase1_output(callback: Callable):
    """訂閱 Phase1 輸出"""
    global _phase1_coordinator
    if _phase1_coordinator:
        _phase1_coordinator.subscribe_to_phase1_output(callback)

async def get_phase1_system_status() -> Dict[str, Any]:
    """獲取 Phase1 系統狀態"""
    global _phase1_coordinator
    if _phase1_coordinator:
        return await _phase1_coordinator.get_phase1_status()
    return {"error": "Phase1 coordinator not initialized"}

async def restart_phase1_component(component: str) -> bool:
    """重啟 Phase1 組件"""
    global _phase1_coordinator
    if _phase1_coordinator:
        return await _phase1_coordinator.restart_component(component)
    return False
