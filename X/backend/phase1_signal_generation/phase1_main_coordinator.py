"""
🎯 Trading X - Phase1 主協調器
統一管理整個 Phase1 信號生成流水線
WebSocket → Phase1A → Phase1B → Phase1C → 輸出
實現 < 180ms 端到端處理延遲
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import time

# 導入 Phase1 組件
from .websocket_realtime_driver.websocket_realtime_driver import (
    websocket_realtime_driver, start_realtime_driver, stop_realtime_driver
)
from .indicator_dependency.indicator_dependency_graph import (
    indicator_dependency_graph, start_indicator_engine, stop_indicator_engine
)
from .phase1a_basic_signal_generation.phase1a_basic_signal_generation import (
    phase1a_signal_generator, start_phase1a_generator, stop_phase1a_generator
)
from .phase1b_signal_filtering_enhancement.phase1b_signal_filtering_enhancement import (
    phase1b_filter_enhancer, start_phase1b_filter, stop_phase1b_filter
)
from .phase1c_unified_signal_pool.unified_signal_pool_v3 import (
    phase1c_unified_pool, start_phase1c_pool, stop_phase1c_pool
)
from .intelligent_trigger_engine import (
    intelligent_trigger_engine, start_intelligent_trigger_engine, stop_intelligent_trigger_engine,
    subscribe_to_intelligent_signals, process_realtime_price_update, get_intelligent_trigger_status
)

logger = logging.getLogger(__name__)

@dataclass
class Phase1Performance:
    """Phase1 性能統計"""
    total_processing_time_ms: float
    websocket_latency_ms: float
    indicator_processing_ms: float
    phase1a_processing_ms: float
    phase1b_processing_ms: float
    phase1c_processing_ms: float
    end_to_end_latency_ms: float
    throughput_signals_per_minute: float
    success_rate: float

@dataclass
class Phase1Status:
    """Phase1 運行狀態"""
    is_running: bool
    websocket_connected: bool
    indicator_engine_active: bool
    phase1a_active: bool
    phase1b_active: bool
    phase1c_active: bool
    intelligent_trigger_active: bool  # 新增
    total_signals_processed: int
    error_count: int
    last_signal_time: Optional[datetime]

class Phase1Coordinator:
    """Phase1 主協調器"""
    
    def __init__(self):
        self.config = self._load_config()
        
        # 性能監控
        self.performance_stats = []
        self.error_log = []
        self.processing_chain_times = {}
        
        # 運行狀態
        self.status = Phase1Status(
            is_running=False,
            websocket_connected=False,
            indicator_engine_active=False,
            phase1a_active=False,
            phase1b_active=False,
            phase1c_active=False,
            intelligent_trigger_active=False,  # 新增
            total_signals_processed=0,
            error_count=0,
            last_signal_time=None
        )
        
        # 輸出訂閱者
        self.phase1_output_subscribers = []
        
        # 內部任務
        self.coordinator_tasks = []
        
        logger.info("Phase1 主協調器初始化完成")
    
    def _load_config(self) -> Dict[str, Any]:
        """載入配置"""
        try:
            config_path = "/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/phase1_main_coordinator_dependency.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"配置載入失敗: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """預設配置"""
        return {
            "symbols": ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT", "SOLUSDT"],
            "performance_targets": {
                "end_to_end_latency": "< 180ms",
                "websocket_latency": "< 12ms",
                "indicator_processing": "< 45ms",
                "phase1a_processing": "< 45ms",
                "phase1b_processing": "< 25ms",
                "phase1c_processing": "< 15ms",
                "throughput": "> 500 signals/min"
            },
            "startup_sequence_delays": {
                "websocket_to_indicators": 2.0,
                "indicators_to_phase1a": 1.0,
                "phase1a_to_phase1b": 0.5,
                "phase1b_to_phase1c": 0.5
            },
            "health_check_interval": 30,
            "performance_monitoring_interval": 60
        }
    
    async def start_phase1_pipeline(self, symbols: List[str] = None) -> bool:
        """啟動完整的 Phase1 信號生成流水線"""
        if self.status.is_running:
            logger.warning("Phase1 流水線已在運行")
            return True
        
        try:
            symbols = symbols or self.config.get("symbols", ["BTCUSDT"])
            logger.info(f"啟動 Phase1 信號生成流水線: {symbols}")
            
            # 1. 啟動 WebSocket 實時驅動器
            logger.info("步驟 1/5: 啟動 WebSocket 實時驅動器")
            await start_realtime_driver(symbols)
            await asyncio.sleep(self.config["startup_sequence_delays"]["websocket_to_indicators"])
            self.status.websocket_connected = True
            logger.info("✅ WebSocket 驅動器啟動完成")
            
            # 2. 啟動技術指標引擎
            logger.info("步驟 2/5: 啟動技術指標引擎")
            await start_indicator_engine()
            await asyncio.sleep(self.config["startup_sequence_delays"]["indicators_to_phase1a"])
            self.status.indicator_engine_active = True
            logger.info("✅ 技術指標引擎啟動完成")
            
            # 3. 啟動 Phase1A 基礎信號生成器
            logger.info("步驟 3/5: 啟動 Phase1A 基礎信號生成器")
            await start_phase1a_generator(websocket_realtime_driver)
            await asyncio.sleep(self.config["startup_sequence_delays"]["phase1a_to_phase1b"])
            self.status.phase1a_active = True
            logger.info("✅ Phase1A 基礎信號生成器啟動完成")
            
            # 4. 啟動 Phase1B 信號過濾增強器
            logger.info("步驟 4/5: 啟動 Phase1B 信號過濾增強器")
            await start_phase1b_filter()
            await asyncio.sleep(self.config["startup_sequence_delays"]["phase1b_to_phase1c"])
            self.status.phase1b_active = True
            logger.info("✅ Phase1B 信號過濾增強器啟動完成")
            
            # 5. 啟動 Phase1C 統一信號池
            logger.info("步驟 5/6: 啟動 Phase1C 統一信號池")
            await start_phase1c_pool()
            self.status.phase1c_active = True
            logger.info("✅ Phase1C 統一信號池啟動完成")
            
            # 6. 啟動智能觸發引擎
            logger.info("步驟 6/6: 啟動智能觸發引擎")
            await start_intelligent_trigger_engine()
            self.status.intelligent_trigger_active = True
            logger.info("✅ 智能觸發引擎啟動完成")
            
            # 建立信號處理鏈
            await self._setup_signal_processing_chain()
            
            # 啟動協調器任務
            self.coordinator_tasks = [
                asyncio.create_task(self._health_monitor()),
                asyncio.create_task(self._performance_monitor()),
                asyncio.create_task(self._end_to_end_latency_tracker())
            ]
            
            self.status.is_running = True
            logger.info("🎉 Phase1 信號生成流水線完全啟動成功!")
            
            return True
            
        except Exception as e:
            logger.error(f"Phase1 流水線啟動失敗: {e}")
            await self.stop_phase1_pipeline()
            return False
    
    async def stop_phase1_pipeline(self):
        """停止 Phase1 信號生成流水線"""
        logger.info("停止 Phase1 信號生成流水線")
        
        try:
            # 取消協調器任務
            for task in self.coordinator_tasks:
                if not task.done():
                    task.cancel()
            self.coordinator_tasks.clear()
            
            # 反向順序停止組件
            logger.info("停止智能觸發引擎")
            await stop_intelligent_trigger_engine()
            self.status.intelligent_trigger_active = False
            
            logger.info("停止 Phase1C 統一信號池")
            await stop_phase1c_pool()
            self.status.phase1c_active = False
            
            logger.info("停止 Phase1B 信號過濾增強器")
            await stop_phase1b_filter()
            self.status.phase1b_active = False
            
            logger.info("停止 Phase1A 基礎信號生成器")
            await stop_phase1a_generator()
            self.status.phase1a_active = False
            
            logger.info("停止技術指標引擎")
            await stop_indicator_engine()
            self.status.indicator_engine_active = False
            
            logger.info("停止 WebSocket 實時驅動器")
            await stop_realtime_driver()
            self.status.websocket_connected = False
            
            self.status.is_running = False
            logger.info("✅ Phase1 信號生成流水線已完全停止")
            
        except Exception as e:
            logger.error(f"Phase1 流水線停止失敗: {e}")
    
    async def _setup_signal_processing_chain(self):
        """建立信號處理鏈"""
        try:
            # Phase1A -> Phase1B 連接
            phase1a_signal_generator.subscribe_to_signals(self._on_phase1a_signals)
            
            # Phase1C -> 外部輸出連接
            phase1c_unified_pool.subscribe_to_unified_signals(self._on_phase1c_output)
            
            # WebSocket -> 智能觸發引擎連接
            websocket_realtime_driver.subscribe_to_price_updates(self._on_websocket_price_update)
            
            # 智能觸發引擎 -> Phase1C 連接
            subscribe_to_intelligent_signals(self._on_intelligent_trigger_signal)
            
            logger.info("信號處理鏈建立完成 (包含智能觸發引擎)")
            
        except Exception as e:
            logger.error(f"信號處理鏈建立失敗: {e}")
    
    async def _on_websocket_price_update(self, symbol: str, price_data: Dict[str, Any]):
        """處理WebSocket價格更新"""
        try:
            # 轉發到智能觸發引擎
            await process_realtime_price_update(
                symbol=symbol,
                price=price_data.get('price', 0),
                volume=price_data.get('volume', 0)
            )
        except Exception as e:
            logger.error(f"WebSocket價格更新處理失敗: {e}")
    
    async def _on_intelligent_trigger_signal(self, signal: Dict[str, Any]):
        """處理智能觸發信號"""
        try:
            # 將智能觸發信號加入到Phase1C統一信號池
            signal_id = await phase1c_unified_pool.add_intelligent_signal(signal)
            
            if signal_id:
                self.status.total_signals_processed += 1
                self.status.last_signal_time = datetime.now()
                
                logger.info(f"🧠 智能觸發信號已加入信號池: {signal['symbol']} | 勝率: {signal.get('win_rate_prediction', 0):.2%}")
            
        except Exception as e:
            logger.error(f"智能觸發信號處理失敗: {e}")
            self.status.error_count += 1
    
    async def _on_phase1a_signals(self, signals: List[Any]):
        """處理 Phase1A 信號"""
        try:
            start_time = time.time()
            
            # Phase1A -> Phase1B
            filtered_signals = await phase1b_filter_enhancer.process_signals(signals)
            
            phase1b_time = time.time()
            
            # Phase1B -> Phase1C
            if filtered_signals:
                added_signal_ids = await phase1c_unified_pool.add_signals(filtered_signals)
                
                phase1c_time = time.time()
                
                # 記錄處理時間
                self.processing_chain_times.update({
                    'phase1b_processing': (phase1b_time - start_time) * 1000,
                    'phase1c_processing': (phase1c_time - phase1b_time) * 1000,
                    'phase1bc_total': (phase1c_time - start_time) * 1000
                })
                
                self.status.total_signals_processed += len(added_signal_ids)
                self.status.last_signal_time = datetime.now()
                
        except Exception as e:
            logger.error(f"Phase1A 信號處理失敗: {e}")
            self.status.error_count += 1
    
    async def _on_phase1c_output(self, unified_signals: List[Any]):
        """處理 Phase1C 輸出信號 - 最終輸出"""
        try:
            # 記錄最終輸出性能
            end_time = time.time()
            
            # 通知外部訂閱者
            for subscriber in self.phase1_output_subscribers:
                try:
                    if asyncio.iscoroutinefunction(subscriber):
                        await subscriber(unified_signals)
                    else:
                        subscriber(unified_signals)
                except Exception as e:
                    logger.error(f"Phase1 輸出訂閱者通知失敗: {e}")
            
            logger.info(f"🎯 Phase1 完成輸出: {len(unified_signals)} 個統一信號")
            
        except Exception as e:
            logger.error(f"Phase1C 輸出處理失敗: {e}")
            self.status.error_count += 1
    
    def subscribe_to_phase1_output(self, callback: Callable):
        """訂閱 Phase1 最終輸出"""
        if callback not in self.phase1_output_subscribers:
            self.phase1_output_subscribers.append(callback)
            logger.info(f"新增 Phase1 輸出訂閱者: {callback.__name__}")
    
    async def _health_monitor(self):
        """健康監控器"""
        while self.status.is_running:
            try:
                # 檢查各組件健康狀態
                websocket_health = await self._check_websocket_health()
                indicator_health = await self._check_indicator_health()
                phase1a_health = await self._check_phase1a_health()
                phase1b_health = await self._check_phase1b_health()
                phase1c_health = await self._check_phase1c_health()
                trigger_engine_health = await self._check_trigger_engine_health()
                
                # 更新狀態
                overall_health = all([
                    websocket_health, indicator_health, 
                    phase1a_health, phase1b_health, phase1c_health, trigger_engine_health
                ])
                
                if not overall_health:
                    logger.warning("檢測到組件健康問題")
                    logger.info(f"WebSocket: {'✅' if websocket_health else '❌'}")
                    logger.info(f"指標引擎: {'✅' if indicator_health else '❌'}")
                    logger.info(f"Phase1A: {'✅' if phase1a_health else '❌'}")
                    logger.info(f"Phase1B: {'✅' if phase1b_health else '❌'}")
                    logger.info(f"Phase1C: {'✅' if phase1c_health else '❌'}")
                    logger.info(f"智能觸發引擎: {'✅' if trigger_engine_health else '❌'}")
                
                await asyncio.sleep(self.config["health_check_interval"])
                
            except Exception as e:
                logger.error(f"健康監控失敗: {e}")
                await asyncio.sleep(30)
    
    async def _check_websocket_health(self) -> bool:
        """檢查 WebSocket 健康狀態"""
        try:
            stats = await websocket_realtime_driver.get_performance_stats()
            return stats.get('active_connections', 0) > 0
        except:
            return False
    
    async def _check_indicator_health(self) -> bool:
        """檢查指標引擎健康狀態"""
        try:
            return indicator_dependency_graph.is_running
        except:
            return False
    
    async def _check_phase1a_health(self) -> bool:
        """檢查 Phase1A 健康狀態"""
        try:
            return phase1a_signal_generator.is_running
        except:
            return False
    
    async def _check_phase1b_health(self) -> bool:
        """檢查 Phase1B 健康狀態"""
        try:
            return phase1b_filter_enhancer.is_running
        except:
            return False
    
    async def _check_phase1c_health(self) -> bool:
        """檢查 Phase1C 健康狀態"""
        try:
            return phase1c_unified_pool.is_running
        except:
            return False
    
    async def _check_trigger_engine_health(self) -> bool:
        """檢查智能觸發引擎健康狀態"""
        try:
            status = await get_intelligent_trigger_status()
            return status.get('is_running', False)
        except:
            return False
    
    async def _performance_monitor(self):
        """性能監控器"""
        while self.status.is_running:
            try:
                # 收集各組件性能數據
                websocket_stats = await websocket_realtime_driver.get_performance_stats()
                phase1a_stats = await phase1a_signal_generator.get_performance_summary()
                phase1b_stats = await phase1b_filter_enhancer.get_filter_statistics()
                phase1c_stats = await phase1c_unified_pool.get_pool_status()
                
                # 計算整體性能
                performance = Phase1Performance(
                    total_processing_time_ms=sum(self.processing_chain_times.values()),
                    websocket_latency_ms=websocket_stats.get('average_latencies', {}).get('binance_processing', 0),
                    indicator_processing_ms=0,  # 需要從指標引擎獲取
                    phase1a_processing_ms=phase1a_stats.get('average_processing_time_ms', 0),
                    phase1b_processing_ms=self.processing_chain_times.get('phase1b_processing', 0),
                    phase1c_processing_ms=self.processing_chain_times.get('phase1c_processing', 0),
                    end_to_end_latency_ms=0,  # 將在延遲追蹤器中計算
                    throughput_signals_per_minute=phase1c_stats.get('performance', {}).get('throughput_per_minute', 0),
                    success_rate=max(0, 1 - self.status.error_count / max(self.status.total_signals_processed, 1))
                )
                
                self.performance_stats.append(performance)
                
                # 限制歷史記錄
                if len(self.performance_stats) > 100:
                    self.performance_stats = self.performance_stats[-50:]
                
                logger.info(f"📊 Phase1 性能: {performance.total_processing_time_ms:.1f}ms 總處理時間, {performance.throughput_signals_per_minute:.0f} 信號/分鐘")
                
                await asyncio.sleep(self.config["performance_monitoring_interval"])
                
            except Exception as e:
                logger.error(f"性能監控失敗: {e}")
                await asyncio.sleep(60)
    
    async def _end_to_end_latency_tracker(self):
        """端到端延遲追蹤器"""
        while self.status.is_running:
            try:
                # 實施端到端延遲測量
                # 這裡可以添加更詳細的延遲追蹤邏輯
                pass
                
            except Exception as e:
                logger.error(f"延遲追蹤失敗: {e}")
            
            await asyncio.sleep(10)
    
    async def get_phase1_status(self) -> Dict[str, Any]:
        """獲取 Phase1 完整狀態"""
        try:
            # 獲取各組件狀態
            websocket_stats = await websocket_realtime_driver.get_performance_stats()
            phase1a_stats = await phase1a_signal_generator.get_performance_summary()
            phase1c_stats = await phase1c_unified_pool.get_pool_status()
            
            return {
                'status': asdict(self.status),
                'performance': asdict(self.performance_stats[-1]) if self.performance_stats else {},
                'component_stats': {
                    'websocket': websocket_stats,
                    'phase1a': phase1a_stats,
                    'phase1c': phase1c_stats
                },
                'processing_chain_times': self.processing_chain_times,
                'configuration': self.config
            }
            
        except Exception as e:
            logger.error(f"狀態獲取失敗: {e}")
            return {'error': str(e)}
    
    async def restart_component(self, component: str) -> bool:
        """重啟指定組件"""
        try:
            logger.info(f"重啟組件: {component}")
            
            if component == 'websocket':
                await stop_realtime_driver()
                await start_realtime_driver(self.config.get("symbols", ["BTCUSDT"]))
                self.status.websocket_connected = True
                
            elif component == 'phase1a':
                await stop_phase1a_generator()
                await start_phase1a_generator(websocket_realtime_driver)
                self.status.phase1a_active = True
                
            elif component == 'phase1b':
                await stop_phase1b_filter()
                await start_phase1b_filter()
                self.status.phase1b_active = True
                
            elif component == 'phase1c':
                await stop_phase1c_pool()
                await start_phase1c_pool()
                self.status.phase1c_active = True
                
            elif component == 'intelligent_trigger':
                await stop_intelligent_trigger_engine()
                await start_intelligent_trigger_engine()
                self.status.intelligent_trigger_active = True
                
            else:
                logger.error(f"未知組件: {component}")
                return False
            
            logger.info(f"✅ 組件 {component} 重啟成功")
            return True
            
        except Exception as e:
            logger.error(f"組件 {component} 重啟失敗: {e}")
            return False

# 全局實例
phase1_coordinator = Phase1Coordinator()

# 便捷函數
async def start_phase1_system(symbols: List[str] = None) -> bool:
    """啟動完整 Phase1 系統"""
    return await phase1_coordinator.start_phase1_pipeline(symbols)

async def stop_phase1_system():
    """停止 Phase1 系統"""
    await phase1_coordinator.stop_phase1_pipeline()

def subscribe_to_phase1_output(callback: Callable):
    """訂閱 Phase1 最終輸出"""
    phase1_coordinator.subscribe_to_phase1_output(callback)

async def get_phase1_system_status() -> Dict[str, Any]:
    """獲取 Phase1 系統狀態"""
    return await phase1_coordinator.get_phase1_status()

async def restart_phase1_component(component: str) -> bool:
    """重啟 Phase1 組件"""
    return await phase1_coordinator.restart_component(component)
