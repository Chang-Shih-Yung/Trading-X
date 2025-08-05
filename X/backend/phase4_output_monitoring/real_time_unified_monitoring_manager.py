"""
🎯 Trading X - 統一即時監控管理系統
整合真實數據源的信號處理和Gmail通知系統

真實系統整合：
- app.services.gmail_notification (Gmail通知系統)
- app.services.sniper_email_manager (狙擊手郵件管理)
- X.real_data_signal_quality_engine (信號質量控制)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json

# 導入真實系統組件
import sys
from pathlib import Path

# 添加上級目錄到路徑
current_dir = Path(__file__).parent
sys.path.append(str(current_dir.parent.parent / "app" / "services"))
sys.path.append(str(current_dir.parent / "core"))

from gmail_notification import GmailNotificationService
from sniper_email_manager import SniperEmailManager

# 導入我們的信號質量控制引擎
from real_data_signal_quality_engine import (
    RealDataSignalQualityEngine,
    SignalCandidate,
    EPLDecision,
    SignalPriority,
    RealTimeDataSnapshot,
    DataIntegrityStatus
)

logger = logging.getLogger(__name__)

@dataclass
class NotificationTemplate:
    """通知模板"""
    priority: SignalPriority
    subject_template: str
    body_template: str
    cooldown_minutes: int
    max_per_hour: int

@dataclass
class MonitoringStats:
    """監控統計"""
    total_signals_processed: int
    signals_by_priority: Dict[str, int]
    data_integrity_stats: Dict[str, int]
    notification_stats: Dict[str, int]
    performance_metrics: Dict[str, float]
    last_update: datetime

class RealTimeUnifiedMonitoringManager:
    """即時統一監控管理系統"""
    
    def __init__(self):
        # 初始化真實系統組件
        self.signal_engine = RealDataSignalQualityEngine()
        self.gmail_service = GmailNotificationService()
        self.sniper_email = SniperEmailManager()
        
        # 監控設定
        self.monitoring_enabled = True
        self.processing_interval = 30  # 30秒處理間隔
        self.symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]  # 監控標的
        
        # 通知設定
        self.notification_templates = self._setup_notification_templates()
        self.notification_cooldowns = {}  # 通知冷卻記錄
        self.hourly_notification_counts = {}  # 每小時通知計數
        
        # 統計數據
        self.stats = MonitoringStats(
            total_signals_processed=0,
            signals_by_priority={},
            data_integrity_stats={},
            notification_stats={},
            performance_metrics={},
            last_update=datetime.now()
        )
        
        # 歷史記錄
        self.signal_history = []
        self.decision_history = []
        self.max_history_size = 1000
        
    def _setup_notification_templates(self) -> Dict[SignalPriority, NotificationTemplate]:
        """設置通知模板"""
        return {
            SignalPriority.CRITICAL: NotificationTemplate(
                priority=SignalPriority.CRITICAL,
                subject_template="🚨 [CRITICAL] Trading X 緊急信號 - {symbol}",
                body_template="""
🚨 **緊急交易信號**

📊 **信號詳情:**
- 標的: {symbol}
- 信號強度: {signal_strength:.3f}
- 執行信心度: {execution_confidence:.3f}
- 建議操作: {recommended_action}

⚡ **數據來源:**
- 來源類型: {source_type}
- 數據完整性: {data_integrity}
- 質量評分: {data_quality:.3f}

🎯 **風險管理:**
- 止損比例: {stop_loss:.2%}
- 止盈比例: {take_profit:.2%}
- 建議倉位: {position_size:.2%}

⏰ 生成時間: {timestamp}
""",
                cooldown_minutes=5,
                max_per_hour=6
            ),
            
            SignalPriority.HIGH: NotificationTemplate(
                priority=SignalPriority.HIGH,
                subject_template="⚡ [HIGH] Trading X 強信號 - {symbol}",
                body_template="""
⚡ **高優先級交易信號**

📊 **信號詳情:**
- 標的: {symbol}
- 信號強度: {signal_strength:.3f}
- 執行信心度: {execution_confidence:.3f}
- 建議操作: {recommended_action}

📈 **決策分析:**
- 市場環境評分: {market_score:.3f}
- 風險評估評分: {risk_score:.3f}
- 時機優化評分: {timing_score:.3f}

⏰ 生成時間: {timestamp}
""",
                cooldown_minutes=10,
                max_per_hour=4
            ),
            
            SignalPriority.MEDIUM: NotificationTemplate(
                priority=SignalPriority.MEDIUM,
                subject_template="📊 [MEDIUM] Trading X 中等信號 - {symbol}",
                body_template="""
📊 **中等優先級信號**

- 標的: {symbol}
- 信號強度: {signal_strength:.3f}
- 執行信心度: {execution_confidence:.3f}
- 建議操作: {recommended_action}

⏰ 生成時間: {timestamp}
""",
                cooldown_minutes=30,
                max_per_hour=2
            )
        }
    
    async def start_monitoring(self):
        """開始監控"""
        logger.info("🎯 啟動 Trading X 統一即時監控系統")
        
        while self.monitoring_enabled:
            try:
                await self._process_monitoring_cycle()
                await asyncio.sleep(self.processing_interval)
                
            except Exception as e:
                logger.error(f"監控循環錯誤: {e}")
                await asyncio.sleep(5)  # 錯誤後短暫暫停
    
    async def _process_monitoring_cycle(self):
        """處理監控循環"""
        cycle_start = datetime.now()
        
        for symbol in self.symbols:
            try:
                # 1. 收集即時數據
                data_snapshot = await self.signal_engine.collect_real_time_data(symbol)
                
                # 2. 檢查數據完整性
                if data_snapshot.data_integrity == DataIntegrityStatus.INVALID:
                    logger.warning(f"{symbol} 數據無效，跳過處理")
                    continue
                
                # 3. 第一階段：信號候選者池
                candidates = await self.signal_engine.stage1_signal_candidate_pool(data_snapshot)
                
                if not candidates:
                    continue
                
                # 4. 準備市場環境數據
                market_context = await self._prepare_market_context(symbol, data_snapshot)
                
                # 5. 第二階段：EPL決策層
                decisions = await self.signal_engine.stage2_epl_decision_layer(candidates, market_context)
                
                # 6. 處理決策結果
                await self._process_decisions(symbol, decisions, data_snapshot)
                
                # 7. 更新統計
                self._update_statistics(candidates, decisions, data_snapshot)
                
            except Exception as e:
                logger.error(f"{symbol} 監控處理錯誤: {e}")
                continue
        
        # 記錄處理時間
        processing_time = (datetime.now() - cycle_start).total_seconds()
        self.stats.performance_metrics["last_cycle_time"] = processing_time
        
        logger.info(f"監控循環完成，處理時間: {processing_time:.2f}秒")
    
    async def _prepare_market_context(self, symbol: str, data_snapshot: RealTimeDataSnapshot) -> Dict[str, Any]:
        """準備市場環境數據"""
        context = {
            "market_trend": 0.5,
            "volatility": 0.5,
            "liquidity": 0.7,
            "market_uncertainty": 0.3,
            "market_activity": 0.7
        }
        
        try:
            # 基於即時數據調整市場環境
            if data_snapshot.volatility_metrics:
                context["volatility"] = data_snapshot.volatility_metrics.current_volatility
                context["market_uncertainty"] = 1.0 - data_snapshot.volatility_metrics.regime_stability
            
            if data_snapshot.order_book_analysis:
                # 基於訂單簿數據調整流動性
                total_volume = (data_snapshot.order_book_analysis.total_bid_volume + 
                              data_snapshot.order_book_analysis.total_ask_volume)
                context["liquidity"] = min(1.0, total_volume / 1000000)  # 標準化流動性
            
            if data_snapshot.technical_indicators:
                # 基於技術指標調整趨勢
                rsi = data_snapshot.technical_indicators.get("RSI", 50)
                if rsi > 60:
                    context["market_trend"] = 0.7
                elif rsi < 40:
                    context["market_trend"] = 0.3
                
        except Exception as e:
            logger.error(f"市場環境準備錯誤: {e}")
        
        return context
    
    async def _process_decisions(self, symbol: str, decisions: List[EPLDecision], 
                               data_snapshot: RealTimeDataSnapshot):
        """處理決策結果"""
        
        for decision in decisions:
            try:
                # 記錄決策歷史
                self.decision_history.append({
                    "symbol": symbol,
                    "decision": asdict(decision),
                    "data_snapshot_summary": {
                        "timestamp": data_snapshot.timestamp.isoformat(),
                        "data_integrity": data_snapshot.data_integrity.value,
                        "missing_components": data_snapshot.missing_components
                    }
                })
                
                # 限制歷史記錄大小
                if len(self.decision_history) > self.max_history_size:
                    self.decision_history = self.decision_history[-self.max_history_size:]
                
                # 發送通知（如果符合條件）
                await self._send_notification_if_needed(symbol, decision)
                
                # 記錄信號到狙擊手系統（高優先級信號）
                if decision.final_priority in [SignalPriority.CRITICAL, SignalPriority.HIGH]:
                    await self._record_to_sniper_system(symbol, decision)
                
            except Exception as e:
                logger.error(f"決策處理錯誤: {e}")
                continue
    
    async def _send_notification_if_needed(self, symbol: str, decision: EPLDecision):
        """根據需要發送通知"""
        priority = decision.final_priority
        
        # 只對重要信號發送通知
        if priority not in [SignalPriority.CRITICAL, SignalPriority.HIGH, SignalPriority.MEDIUM]:
            return
        
        # 檢查冷卻時間
        cooldown_key = f"{symbol}_{priority.value}"
        if not self._check_notification_cooldown(cooldown_key, priority):
            return
        
        # 檢查每小時限制
        if not self._check_hourly_limit(priority):
            return
        
        try:
            template = self.notification_templates[priority]
            
            # 準備通知數據
            notification_data = {
                "symbol": symbol,
                "signal_strength": decision.original_candidate.raw_signal_strength,
                "execution_confidence": decision.execution_confidence,
                "recommended_action": decision.recommended_action,
                "source_type": decision.original_candidate.source_type,
                "data_integrity": decision.original_candidate.integrity_check,
                "data_quality": decision.original_candidate.data_quality_score,
                "market_score": decision.market_context_score,
                "risk_score": decision.risk_assessment_score,
                "timing_score": decision.timing_optimization_score,
                "stop_loss": decision.risk_management_params.get("stop_loss_ratio", 0.02),
                "take_profit": decision.risk_management_params.get("take_profit_ratio", 0.03),
                "position_size": decision.risk_management_params.get("position_size_ratio", 0.1),
                "timestamp": decision.original_candidate.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 格式化郵件內容
            subject = template.subject_template.format(**notification_data)
            body = template.body_template.format(**notification_data)
            
            # 發送郵件
            await self.gmail_service.send_signal_notification(
                subject=subject,
                body=body,
                priority=priority.value
            )
            
            # 更新冷卻記錄
            self.notification_cooldowns[cooldown_key] = datetime.now()
            
            # 更新計數
            hour_key = datetime.now().strftime("%Y%m%d_%H")
            priority_hour_key = f"{priority.value}_{hour_key}"
            self.hourly_notification_counts[priority_hour_key] = \
                self.hourly_notification_counts.get(priority_hour_key, 0) + 1
            
            # 更新統計
            self.stats.notification_stats[priority.value] = \
                self.stats.notification_stats.get(priority.value, 0) + 1
            
            logger.info(f"📧 {priority.value} 優先級通知已發送: {symbol}")
            
        except Exception as e:
            logger.error(f"通知發送失敗: {e}")
    
    def _check_notification_cooldown(self, cooldown_key: str, priority: SignalPriority) -> bool:
        """檢查通知冷卻時間"""
        if cooldown_key not in self.notification_cooldowns:
            return True
        
        last_notification = self.notification_cooldowns[cooldown_key]
        template = self.notification_templates[priority]
        cooldown_period = timedelta(minutes=template.cooldown_minutes)
        
        return datetime.now() - last_notification >= cooldown_period
    
    def _check_hourly_limit(self, priority: SignalPriority) -> bool:
        """檢查每小時通知限制"""
        template = self.notification_templates[priority]
        hour_key = datetime.now().strftime("%Y%m%d_%H")
        priority_hour_key = f"{priority.value}_{hour_key}"
        
        current_count = self.hourly_notification_counts.get(priority_hour_key, 0)
        return current_count < template.max_per_hour
    
    async def _record_to_sniper_system(self, symbol: str, decision: EPLDecision):
        """記錄到狙擊手系統"""
        try:
            # 準備狙擊手信號數據
            sniper_signal = {
                "symbol": symbol,
                "signal_type": decision.recommended_action,
                "strength": decision.execution_confidence,
                "priority": decision.final_priority.value,
                "source": decision.original_candidate.source_type,
                "risk_params": decision.risk_management_params,
                "timestamp": decision.original_candidate.timestamp,
                "decision_reasoning": decision.decision_reasoning
            }
            
            # 使用狙擊手郵件管理器記錄
            await self.sniper_email.record_signal_event(sniper_signal)
            
            logger.info(f"🎯 狙擊手系統記錄: {symbol} - {decision.final_priority.value}")
            
        except Exception as e:
            logger.error(f"狙擊手系統記錄錯誤: {e}")
    
    def _update_statistics(self, candidates: List[SignalCandidate], 
                          decisions: List[EPLDecision],
                          data_snapshot: RealTimeDataSnapshot):
        """更新統計數據"""
        # 更新總處理數量
        self.stats.total_signals_processed += len(candidates)
        
        # 更新優先級統計
        for decision in decisions:
            priority = decision.final_priority.value
            self.stats.signals_by_priority[priority] = \
                self.stats.signals_by_priority.get(priority, 0) + 1
        
        # 更新數據完整性統計
        integrity_status = data_snapshot.data_integrity.value
        self.stats.data_integrity_stats[integrity_status] = \
            self.stats.data_integrity_stats.get(integrity_status, 0) + 1
        
        # 更新性能指標
        if decisions:
            avg_confidence = sum(d.execution_confidence for d in decisions) / len(decisions)
            self.stats.performance_metrics["avg_execution_confidence"] = avg_confidence
        
        # 更新最後更新時間
        self.stats.last_update = datetime.now()
    
    async def get_monitoring_dashboard_data(self) -> Dict[str, Any]:
        """獲取監控儀表板數據"""
        return {
            "monitoring_status": "ACTIVE" if self.monitoring_enabled else "INACTIVE",
            "monitored_symbols": self.symbols,
            "processing_interval": self.processing_interval,
            "statistics": asdict(self.stats),
            "recent_decisions": self.decision_history[-10:],  # 最近10個決策
            "notification_cooldowns": {
                k: v.isoformat() for k, v in self.notification_cooldowns.items()
            },
            "hourly_notification_counts": self.hourly_notification_counts,
            "system_health": {
                "signal_engine_status": "OK",
                "gmail_service_status": "OK",
                "sniper_system_status": "OK"
            }
        }
    
    async def get_signal_history(self, symbol: Optional[str] = None, 
                               priority: Optional[SignalPriority] = None,
                               limit: int = 50) -> List[Dict[str, Any]]:
        """獲取信號歷史"""
        filtered_history = self.decision_history
        
        # 按標的過濾
        if symbol:
            filtered_history = [h for h in filtered_history if h["symbol"] == symbol]
        
        # 按優先級過濾
        if priority:
            filtered_history = [
                h for h in filtered_history 
                if h["decision"]["final_priority"] == priority.value
            ]
        
        # 限制數量
        return filtered_history[-limit:]
    
    async def update_monitoring_config(self, config: Dict[str, Any]):
        """更新監控配置"""
        if "symbols" in config:
            self.symbols = config["symbols"]
        
        if "processing_interval" in config:
            self.processing_interval = max(10, config["processing_interval"])  # 最少10秒
        
        if "enabled" in config:
            self.monitoring_enabled = config["enabled"]
        
        logger.info(f"監控配置已更新: {config}")
    
    async def stop_monitoring(self):
        """停止監控"""
        self.monitoring_enabled = False
        logger.info("📊 Trading X 統一監控系統已停止")

# 全局實例
unified_monitoring_manager = RealTimeUnifiedMonitoringManager()
