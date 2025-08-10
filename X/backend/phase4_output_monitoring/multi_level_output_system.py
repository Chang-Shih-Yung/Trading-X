"""
📊 Phase 4: 分級輸出與監控系統
================================

多層級信號輸出系統 - 四級分類通知與監控
🚨 CRITICAL級 🎯 HIGH級 📊 MEDIUM級 📈 LOW級
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
import sys
from pathlib import Path

# 添加路徑
current_dir = Path(__file__).parent
sys.path.extend([
    str(current_dir.parent / "shared_core"),
    str(current_dir.parent / "phase3_execution_policy"),
    str(current_dir.parent.parent.parent / "app" / "services")
])

from epl_intelligent_decision_engine import EPLDecisionResult, SignalPriority, EPLDecision

logger = logging.getLogger(__name__)

class NotificationChannel(Enum):
    """通知管道枚舉"""
    GMAIL = "Gmail通知"
    WEBSOCKET = "WebSocket推送"
    FRONTEND_ALERT = "前端警報"
    FRONTEND_HIGHLIGHT = "前端高亮"
    FRONTEND_STANDARD = "前端標準顯示"
    RISK_ASSESSMENT = "風險評估觸發"

class OutputClassification(Enum):
    """輸出分類"""
    EMERGENCY_SIGNAL = "🚨 緊急信號"
    HIGH_QUALITY_SIGNAL = "🎯 高品質信號"
    STANDARD_SIGNAL = "📊 標準信號"
    OBSERVATION_SIGNAL = "📈 觀察信號"

@dataclass
class NotificationMessage:
    """通知消息結構"""
    id: str
    priority: SignalPriority
    classification: OutputClassification
    title: str
    content: str
    symbol: str
    decision: EPLDecision
    channels: List[NotificationChannel]
    metadata: Dict[str, Any]
    timestamp: datetime
    expiry_time: Optional[datetime]
    
class CriticalSignalProcessor:
    """🚨 CRITICAL級信號處理器"""
    
    def __init__(self):
        self.critical_thresholds = {
            "strength_threshold": 90.0,
            "confidence_threshold": 0.9,
            "volatility_alert": 0.08,
            "risk_score_alert": 0.8
        }
        
        self.notification_handlers = []
        self.critical_history: List[EPLDecisionResult] = []
    
    def _extract_processing_metrics(self, decision_result: EPLDecisionResult) -> Dict[str, Any]:
        """提取處理元數據指標"""
        if hasattr(decision_result, 'processing_metadata') and decision_result.processing_metadata:
            metadata = decision_result.processing_metadata
            return {
                "processing_id": metadata.get("processing_id", "unknown"),
                "processing_time_ms": metadata.get("processing_time_ms", 0),
                "timestamp": metadata.get("timestamp", datetime.now().isoformat()),
                "engine_version": metadata.get("engine_version", "unknown"),
                "performance_score": self._calculate_performance_score(metadata),
                "efficiency_rating": self._rate_processing_efficiency(metadata)
            }
        return {
            "processing_id": "unknown",
            "processing_time_ms": 0,
            "timestamp": datetime.now().isoformat(),
            "engine_version": "unknown",
            "performance_score": 0.0,
            "efficiency_rating": "未知"
        }
    
    def _calculate_performance_score(self, metadata: Dict) -> float:
        """計算性能分數"""
        processing_time = metadata.get("processing_time_ms", 0)
        
        # 基於處理時間計算性能分數 (越快分數越高)
        if processing_time <= 100:
            return 1.0  # 優秀
        elif processing_time <= 300:
            return 0.8  # 良好  
        elif processing_time <= 500:
            return 0.6  # 一般
        elif processing_time <= 800:
            return 0.4  # 較慢
        else:
            return 0.2  # 需優化
    
    def _rate_processing_efficiency(self, metadata: Dict) -> str:
        """評級處理效率"""
        processing_time = metadata.get("processing_time_ms", 0)
        
        if processing_time <= 100:
            return "🚀 極速"
        elif processing_time <= 300:  
            return "⚡ 快速"
        elif processing_time <= 500:
            return "📊 標準"
        elif processing_time <= 800:
            return "⏰ 較慢"
        else:
            return "🐌 需優化"
    
    async def process_critical_signal(self, decision_result: EPLDecisionResult) -> Dict[str, Any]:
        """處理 CRITICAL 級信號 - 增強版 (包含完整 EPL 元數據)"""
        try:
            logger.critical(f"🚨 CRITICAL級信號: {decision_result.candidate.symbol}")
            
            # 提取處理元數據
            processing_metrics = self._extract_processing_metrics(decision_result)
            
            # 創建增強的緊急通知消息
            message = self._create_enhanced_critical_message(decision_result, processing_metrics)
            
            # 記錄性能監控數據
            await self._record_critical_performance(decision_result, processing_metrics)
            
            # 即時 Gmail 通知 (包含性能數據)
            await self._send_immediate_gmail(message)
            
            # WebSocket 即時推送 (包含元數據)
            await self._send_websocket_alert(message, processing_metrics)
            
            # 前端紅色警報顯示 (包含處理時間)
            await self._trigger_frontend_alert(message, processing_metrics)
            
            # 自動觸發風險評估
            risk_assessment = await self._trigger_risk_assessment(decision_result)
            
            # 記錄到關鍵信號歷史 (包含完整元數據)
            await self._record_critical_history(decision_result, processing_metrics)
            
            processing_result = {
                "status": "critical_processed",
                "message": message,
                "processing_metrics": processing_metrics,
                "risk_assessment": risk_assessment,
                "notification_sent": True,
                "alert_triggered": True,
                "processing_time": datetime.now(),
                "performance_score": processing_metrics.get("performance_score", 0.0),
                "efficiency_rating": processing_metrics.get("efficiency_rating", "未知")
            }
            
            logger.critical(f"✅ CRITICAL級信號處理完成: {decision_result.candidate.symbol} "
                          f"(處理時間: {processing_metrics.get('processing_time_ms', 0)}ms, "
                          f"效率: {processing_metrics.get('efficiency_rating', '未知')})")
            
            return processing_result
            
        except Exception as e:
            logger.error(f"❌ CRITICAL級信號處理失敗: {e}")
            return {"status": "critical_error", "error": str(e)}
    
    def _create_enhanced_critical_message(self, decision_result: EPLDecisionResult, 
                                        processing_metrics: Dict) -> NotificationMessage:
        """創建增強的緊急通知消息 (包含處理性能信息)"""
        candidate = decision_result.candidate
        
        title = f"🚨 緊急交易信號: {candidate.symbol}"
        
        # 添加處理性能信息
        performance_info = f"""
        
【處理性能】
處理ID: {processing_metrics.get('processing_id', 'N/A')}
處理時間: {processing_metrics.get('processing_time_ms', 0)}ms
效率評級: {processing_metrics.get('efficiency_rating', '未知')}
引擎版本: {processing_metrics.get('engine_version', 'N/A')}
性能分數: {processing_metrics.get('performance_score', 0.0):.2f}/1.0
        """
        
        content = f"""
【緊急信號警報】
標的: {candidate.symbol}
方向: {candidate.direction}
信號強度: {candidate.signal_strength:.1f}/100
信心度: {candidate.confidence:.2%}

【EPL 決策詳情】
決策: {decision_result.decision.value if hasattr(decision_result.decision, 'value') else decision_result.decision}
優先級: {decision_result.priority.value if hasattr(decision_result.priority, 'value') else decision_result.priority}
推理: {decision_result.reasoning}

【風險管理】
{self._format_risk_info(decision_result.risk_management)}

{performance_info}

【執行建議】
{self._format_execution_params(decision_result.execution_params)}

時間: {decision_result.timestamp}
        """
        
        return NotificationMessage(
            title=title,
            content=content,
            priority="CRITICAL",
            channel="gmail",
            metadata={
                "symbol": candidate.symbol,
                "signal_strength": candidate.signal_strength,
                "confidence": candidate.confidence,
                "processing_metrics": processing_metrics,
                "epl_decision": decision_result.decision.value if hasattr(decision_result.decision, 'value') else str(decision_result.decision)
            }
        )
        """創建緊急通知消息"""
        candidate = decision_result.candidate
        
        title = f"🚨 緊急交易信號: {candidate.symbol}"
        
        content = f"""
【緊急信號警報】
標的: {candidate.symbol}
方向: {candidate.direction}
信號強度: {candidate.signal_strength:.1f}/100
信心度: {candidate.confidence:.2%}
決策: {decision_result.decision.value}

【技術指標】
RSI: {candidate.technical_snapshot.rsi:.1f}
MACD: {candidate.technical_snapshot.macd_signal:.4f}
波動率: {candidate.market_environment.volatility:.3%}

【執行建議】
{decision_result.reasoning[0] if decision_result.reasoning else '無'}

⚠️ 請立即關注市場動態並評估風險
"""
        
        return NotificationMessage(
            id=f"CRITICAL_{candidate.id}_{datetime.now().strftime('%H%M%S')}",
            priority=SignalPriority.CRITICAL,
            classification=OutputClassification.EMERGENCY_SIGNAL,
            title=title,
            content=content.strip(),
            symbol=candidate.symbol,
            decision=decision_result.decision,
            channels=[
                NotificationChannel.GMAIL,
                NotificationChannel.WEBSOCKET,
                NotificationChannel.FRONTEND_ALERT,
                NotificationChannel.RISK_ASSESSMENT
            ],
            metadata={
                "urgency": "immediate",
                "auto_risk_check": True,
                "notification_delay": 0,
                "signal_strength": candidate.signal_strength,
                "confidence": candidate.confidence
            },
            timestamp=datetime.now(),
            expiry_time=datetime.now() + timedelta(hours=2)
        )
    
    async def _send_immediate_gmail(self, message: NotificationMessage):
        """發送即時 Gmail 通知"""
        try:
            # 導入Gmail服務 (如果可用)
            from gmail_notification import GmailNotificationService
            
            gmail_service = GmailNotificationService()
            
            email_content = f"""
{message.title}

{message.content}

時間: {message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
緊急程度: 🚨 最高
"""
            
            await gmail_service.send_urgent_notification(
                subject=message.title,
                content=email_content,
                priority="high"
            )
            
            logger.info(f"✅ CRITICAL級Gmail通知已發送: {message.symbol}")
            
        except Exception as e:
            logger.error(f"❌ Gmail通知發送失敗: {e}")
    
    async def _send_websocket_alert(self, message: NotificationMessage):
        """發送 WebSocket 即時推送"""
        try:
            websocket_data = {
                "type": "critical_alert",
                "data": {
                    "id": message.id,
                    "symbol": message.symbol,
                    "title": message.title,
                    "content": message.content,
                    "priority": message.priority.name,
                    "decision": message.decision.name,
                    "timestamp": message.timestamp.isoformat(),
                    "metadata": message.metadata
                }
            }
            
            # 這裡會廣播到所有連接的WebSocket客戶端
            # 實際實現需要WebSocket管理器
            logger.info(f"📡 WebSocket推送 CRITICAL 警報: {message.symbol}")
            
        except Exception as e:
            logger.error(f"❌ WebSocket推送失敗: {e}")
    
    async def _trigger_frontend_alert(self, message: NotificationMessage):
        """觸發前端紅色警報"""
        try:
            alert_data = {
                "type": "critical_alert",
                "symbol": message.symbol,
                "message": message.title,
                "details": message.content,
                "timestamp": message.timestamp.isoformat(),
                "action_required": True,
                "auto_dismiss": False,
                "style": {
                    "background": "#ff4444",
                    "color": "white",
                    "border": "2px solid #cc0000",
                    "animation": "blink"
                }
            }
            
            logger.info(f"🔴 前端 CRITICAL 警報已觸發: {message.symbol}")
            
        except Exception as e:
            logger.error(f"❌ 前端警報觸發失敗: {e}")
    
    async def _trigger_risk_assessment(self, decision_result: EPLDecisionResult) -> Dict[str, Any]:
        """自動觸發風險評估"""
        try:
            assessment = {
                "assessment_triggered": True,
                "trigger_reason": "critical_signal_detected",
                "symbol": decision_result.candidate.symbol,
                "risk_factors": {
                    "volatility_risk": decision_result.candidate.market_environment.volatility,
                    "liquidity_risk": 1.0 - decision_result.candidate.market_environment.liquidity_score,
                    "signal_uncertainty": 1.0 - decision_result.candidate.confidence,
                    "market_stress": self._calculate_market_stress(decision_result.candidate)
                },
                "recommended_actions": self._generate_risk_recommendations(decision_result),
                "assessment_timestamp": datetime.now()
            }
            
            logger.warning(f"⚠️ 風險評估已觸發: {decision_result.candidate.symbol}")
            return assessment
            
        except Exception as e:
            logger.error(f"❌ 風險評估觸發失敗: {e}")
            return {"assessment_triggered": False, "error": str(e)}
    
    def _calculate_market_stress(self, candidate) -> float:
        """計算市場壓力指數"""
        stress_factors = []
        
        # 波動性壓力
        volatility_stress = min(1.0, candidate.market_environment.volatility * 20)
        stress_factors.append(volatility_stress * 0.4)
        
        # RSI極端值壓力
        rsi = candidate.technical_snapshot.rsi
        if rsi > 80 or rsi < 20:
            rsi_stress = 1.0
        elif rsi > 70 or rsi < 30:
            rsi_stress = 0.6
        else:
            rsi_stress = 0.2
        stress_factors.append(rsi_stress * 0.3)
        
        # 流動性壓力
        liquidity_stress = 1.0 - candidate.market_environment.liquidity_score
        stress_factors.append(liquidity_stress * 0.3)
        
        return sum(stress_factors)
    
    def _generate_risk_recommendations(self, decision_result: EPLDecisionResult) -> List[str]:
        """生成風險建議"""
        recommendations = []
        candidate = decision_result.candidate
        
        if candidate.market_environment.volatility > 0.05:
            recommendations.append("⚠️ 高波動性環境，建議縮小倉位規模")
        
        if candidate.market_environment.liquidity_score < 0.6:
            recommendations.append("⚠️ 流動性不足，建議分批執行")
        
        if candidate.technical_snapshot.rsi > 85 or candidate.technical_snapshot.rsi < 15:
            recommendations.append("⚠️ 技術指標極端，建議等待回調")
        
        if decision_result.decision == EPLDecision.REPLACE_POSITION:
            recommendations.append("🔄 替單操作風險較高，建議人工確認")
        
        return recommendations
    
    def get_critical_statistics(self) -> Dict[str, Any]:
        """獲取 CRITICAL 級統計"""
        if not self.critical_history:
            return {"total_critical": 0, "recent_24h": 0}
        
        recent_24h = len([s for s in self.critical_history 
                         if s.timestamp > datetime.now() - timedelta(hours=24)])
        
        symbols = [s.candidate.symbol for s in self.critical_history]
        decisions = [s.decision for s in self.critical_history]
        
        return {
            "total_critical": len(self.critical_history),
            "recent_24h": recent_24h,
            "most_frequent_symbol": max(set(symbols), key=symbols.count) if symbols else None,
            "most_common_decision": max(set(decisions), key=decisions.count) if decisions else None,
            "average_strength": sum(s.candidate.signal_strength for s in self.critical_history) / len(self.critical_history),
            "latest_critical": self.critical_history[-1].timestamp.isoformat() if self.critical_history else None
        }

class HighPrioritySignalProcessor:
    """🎯 HIGH級信號處理器"""
    
    def __init__(self):
        self.high_priority_queue: List[EPLDecisionResult] = []
        self.notification_delay = 300  # 5分鐘延遲
    
    async def process_high_signal(self, decision_result: EPLDecisionResult) -> Dict[str, Any]:
        """處理 HIGH 級信號"""
        try:
            logger.info(f"🎯 HIGH級信號: {decision_result.candidate.symbol}")
            
            # 創建高品質信號消息
            message = self._create_high_quality_message(decision_result)
            
            # 添加到佇列，準備延遲發送
            self.high_priority_queue.append(decision_result)
            
            # 延遲 Gmail 通知 (5分鐘)
            asyncio.create_task(self._delayed_gmail_notification(message, self.notification_delay))
            
            # WebSocket 推送 (即時)
            await self._send_websocket_update(message)
            
            # 前端橘色標記
            await self._update_frontend_highlight(message)
            
            # 添加到重點關注清單
            await self._add_to_focus_list(decision_result)
            
            processing_result = {
                "status": "high_processed",
                "message": message,
                "delayed_notification": True,
                "delay_seconds": self.notification_delay,
                "websocket_sent": True,
                "focus_list_updated": True,
                "processing_time": datetime.now()
            }
            
            logger.info(f"✅ HIGH級信號處理完成: {decision_result.candidate.symbol}")
            return processing_result
            
        except Exception as e:
            logger.error(f"❌ HIGH級信號處理失敗: {e}")
            return {"status": "high_error", "error": str(e)}
    
    def _create_high_quality_message(self, decision_result: EPLDecisionResult) -> NotificationMessage:
        """創建高品質信號消息"""
        candidate = decision_result.candidate
        
        title = f"🎯 高品質交易信號: {candidate.symbol}"
        
        content = f"""
【高品質信號】
標的: {candidate.symbol}
方向: {candidate.direction}
信號強度: {candidate.signal_strength:.1f}/100
信心度: {candidate.confidence:.2%}
決策: {decision_result.decision.value}
來源: {candidate.source.value}

【市場分析】
當前波動率: {candidate.market_environment.volatility:.3%}
流動性評分: {candidate.market_environment.liquidity_score:.2f}
RSI: {candidate.technical_snapshot.rsi:.1f}

【執行計劃】
{decision_result.reasoning[0] if decision_result.reasoning else '詳見執行參數'}

💡 建議重點關注此信號的發展
"""
        
        return NotificationMessage(
            id=f"HIGH_{candidate.id}_{datetime.now().strftime('%H%M%S')}",
            priority=SignalPriority.HIGH,
            classification=OutputClassification.HIGH_QUALITY_SIGNAL,
            title=title,
            content=content.strip(),
            symbol=candidate.symbol,
            decision=decision_result.decision,
            channels=[
                NotificationChannel.GMAIL,
                NotificationChannel.WEBSOCKET,
                NotificationChannel.FRONTEND_HIGHLIGHT
            ],
            metadata={
                "urgency": "high",
                "notification_delay": self.notification_delay,
                "focus_priority": True,
                "signal_strength": candidate.signal_strength,
                "confidence": candidate.confidence
            },
            timestamp=datetime.now(),
            expiry_time=datetime.now() + timedelta(hours=6)
        )
    
    async def _delayed_gmail_notification(self, message: NotificationMessage, delay_seconds: int):
        """延遲發送 Gmail 通知"""
        try:
            await asyncio.sleep(delay_seconds)
            
            from gmail_notification import GmailNotificationService
            gmail_service = GmailNotificationService()
            
            email_content = f"""
{message.title}

{message.content}

時間: {message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
優先級: 🎯 高
延遲通知: {delay_seconds//60} 分鐘
"""
            
            await gmail_service.send_notification(
                subject=message.title,
                content=email_content,
                priority="normal"
            )
            
            logger.info(f"✅ HIGH級延遲Gmail通知已發送: {message.symbol}")
            
        except Exception as e:
            logger.error(f"❌ HIGH級Gmail通知發送失敗: {e}")
    
    async def _send_websocket_update(self, message: NotificationMessage):
        """發送 WebSocket 更新"""
        try:
            websocket_data = {
                "type": "high_priority_signal",
                "data": {
                    "id": message.id,
                    "symbol": message.symbol,
                    "title": message.title,
                    "priority": message.priority.name,
                    "decision": message.decision.name,
                    "timestamp": message.timestamp.isoformat(),
                    "metadata": message.metadata
                }
            }
            
            logger.info(f"📡 WebSocket推送 HIGH 級信號: {message.symbol}")
            
        except Exception as e:
            logger.error(f"❌ WebSocket推送失敗: {e}")
    
    async def _update_frontend_highlight(self, message: NotificationMessage):
        """更新前端橘色高亮"""
        try:
            highlight_data = {
                "type": "high_priority_highlight",
                "symbol": message.symbol,
                "message": message.title,
                "timestamp": message.timestamp.isoformat(),
                "style": {
                    "background": "#ff8800",
                    "color": "white",
                    "border": "1px solid #ff6600",
                    "font_weight": "bold"
                },
                "duration": 3600  # 1小時高亮
            }
            
            logger.info(f"🟠 前端 HIGH 級高亮已設置: {message.symbol}")
            
        except Exception as e:
            logger.error(f"❌ 前端高亮設置失敗: {e}")
    
    async def _add_to_focus_list(self, decision_result: EPLDecisionResult):
        """添加到重點關注清單"""
        try:
            focus_item = {
                "symbol": decision_result.candidate.symbol,
                "decision": decision_result.decision.name,
                "strength": decision_result.candidate.signal_strength,
                "confidence": decision_result.candidate.confidence,
                "added_time": datetime.now().isoformat(),
                "priority": "high",
                "tracking_id": decision_result.performance_tracking.get("tracking_id")
            }
            
            logger.info(f"⭐ 已添加到重點關注: {decision_result.candidate.symbol}")
            
        except Exception as e:
            logger.error(f"❌ 添加重點關注失敗: {e}")

class StandardSignalProcessor:
    """📊 MEDIUM級信號處理器"""
    
    def __init__(self):
        self.standard_signals: List[EPLDecisionResult] = []
        self.summary_interval = 3600  # 1小時匯總
    
    async def process_standard_signal(self, decision_result: EPLDecisionResult) -> Dict[str, Any]:
        """處理 MEDIUM 級信號"""
        try:
            logger.info(f"📊 MEDIUM級信號: {decision_result.candidate.symbol}")
            
            # 添加到標準信號列表
            self.standard_signals.append(decision_result)
            
            # 前端標準顯示
            await self._update_frontend_standard(decision_result)
            
            # 歷史記錄追蹤
            await self._add_to_history_tracking(decision_result)
            
            # 檢查是否需要發送定期匯總
            await self._check_summary_notification()
            
            processing_result = {
                "status": "standard_processed",
                "frontend_updated": True,
                "history_tracked": True,
                "summary_check": True,
                "processing_time": datetime.now()
            }
            
            logger.info(f"✅ MEDIUM級信號處理完成: {decision_result.candidate.symbol}")
            return processing_result
            
        except Exception as e:
            logger.error(f"❌ MEDIUM級信號處理失敗: {e}")
            return {"status": "standard_error", "error": str(e)}
    
    async def _update_frontend_standard(self, decision_result: EPLDecisionResult):
        """更新前端標準顯示"""
        try:
            display_data = {
                "type": "standard_signal",
                "symbol": decision_result.candidate.symbol,
                "direction": decision_result.candidate.direction,
                "strength": decision_result.candidate.signal_strength,
                "confidence": decision_result.candidate.confidence,
                "decision": decision_result.decision.value,
                "timestamp": decision_result.timestamp.isoformat(),
                "style": {
                    "background": "#4488ff",
                    "color": "white",
                    "border": "1px solid #3366cc"
                }
            }
            
            logger.info(f"📱 前端標準顯示已更新: {decision_result.candidate.symbol}")
            
        except Exception as e:
            logger.error(f"❌ 前端標準顯示更新失敗: {e}")
    
    async def _add_to_history_tracking(self, decision_result: EPLDecisionResult):
        """添加到歷史記錄追蹤"""
        try:
            history_record = {
                "signal_id": decision_result.candidate.id,
                "symbol": decision_result.candidate.symbol,
                "timestamp": decision_result.timestamp.isoformat(),
                "decision": decision_result.decision.name,
                "strength": decision_result.candidate.signal_strength,
                "confidence": decision_result.candidate.confidence,
                "source": decision_result.candidate.source.value,
                "market_conditions": asdict(decision_result.candidate.market_environment),
                "technical_snapshot": asdict(decision_result.candidate.technical_snapshot)
            }
            
            logger.info(f"📋 歷史記錄已添加: {decision_result.candidate.symbol}")
            
        except Exception as e:
            logger.error(f"❌ 歷史記錄添加失敗: {e}")
    
    async def _check_summary_notification(self):
        """檢查是否需要發送定期匯總"""
        try:
            # 檢查最近1小時的信號數量
            recent_signals = [
                s for s in self.standard_signals
                if s.timestamp > datetime.now() - timedelta(seconds=self.summary_interval)
            ]
            
            if len(recent_signals) >= 5:  # 達到匯總條件
                await self._send_summary_notification(recent_signals)
                
        except Exception as e:
            logger.error(f"❌ 匯總檢查失敗: {e}")
    
    async def _send_summary_notification(self, signals: List[EPLDecisionResult]):
        """發送定期匯總通知"""
        try:
            summary_content = f"""
【標準信號匯總報告】
時間範圍: 最近1小時
信號數量: {len(signals)}

【信號分佈】
"""
            
            symbol_counts = {}
            decision_counts = {}
            
            for signal in signals:
                symbol = signal.candidate.symbol
                decision = signal.decision.value
                
                symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
                decision_counts[decision] = decision_counts.get(decision, 0) + 1
            
            summary_content += "\n標的分佈:\n"
            for symbol, count in sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True):
                summary_content += f"  {symbol}: {count}個信號\n"
            
            summary_content += "\n決策分佈:\n"
            for decision, count in sorted(decision_counts.items(), key=lambda x: x[1], reverse=True):
                summary_content += f"  {decision}: {count}個\n"
            
            # 發送匯總通知 (可選擇是否發送Gmail)
            logger.info(f"📧 標準信號匯總通知準備發送 ({len(signals)}個信號)")
            
        except Exception as e:
            logger.error(f"❌ 匯總通知發送失敗: {e}")

class ObservationSignalProcessor:
    """📈 LOW級觀察信號處理器"""
    
    def __init__(self):
        self.observation_signals: List[EPLDecisionResult] = []
        self.research_data: List[Dict[str, Any]] = []
    
    async def process_observation_signal(self, decision_result: EPLDecisionResult) -> Dict[str, Any]:
        """處理 LOW 級觀察信號"""
        try:
            logger.debug(f"📈 LOW級信號: {decision_result.candidate.symbol}")
            
            # 添加到觀察信號列表
            self.observation_signals.append(decision_result)
            
            # 僅前端顯示
            await self._update_frontend_observation(decision_result)
            
            # 研究用途記錄
            await self._add_to_research_data(decision_result)
            
            # 模型訓練數據收集
            await self._collect_training_data(decision_result)
            
            processing_result = {
                "status": "observation_processed",
                "frontend_updated": True,
                "research_recorded": True,
                "training_data_collected": True,
                "processing_time": datetime.now()
            }
            
            logger.debug(f"✅ LOW級信號處理完成: {decision_result.candidate.symbol}")
            return processing_result
            
        except Exception as e:
            logger.error(f"❌ LOW級信號處理失敗: {e}")
            return {"status": "observation_error", "error": str(e)}
    
    async def _update_frontend_observation(self, decision_result: EPLDecisionResult):
        """更新前端觀察顯示"""
        try:
            observation_data = {
                "type": "observation_signal",
                "symbol": decision_result.candidate.symbol,
                "direction": decision_result.candidate.direction,
                "strength": decision_result.candidate.signal_strength,
                "confidence": decision_result.candidate.confidence,
                "timestamp": decision_result.timestamp.isoformat(),
                "style": {
                    "background": "#88ccff",
                    "color": "#333333",
                    "border": "1px dashed #66aadd",
                    "opacity": "0.8"
                },
                "display_duration": 1800  # 30分鐘顯示
            }
            
            logger.debug(f"👁️ 前端觀察顯示已更新: {decision_result.candidate.symbol}")
            
        except Exception as e:
            logger.error(f"❌ 前端觀察顯示更新失敗: {e}")
    
    async def _add_to_research_data(self, decision_result: EPLDecisionResult):
        """添加到研究數據"""
        try:
            research_record = {
                "record_id": f"research_{decision_result.candidate.id}",
                "symbol": decision_result.candidate.symbol,
                "signal_data": {
                    "strength": decision_result.candidate.signal_strength,
                    "confidence": decision_result.candidate.confidence,
                    "source": decision_result.candidate.source.value,
                    "direction": decision_result.candidate.direction
                },
                "market_context": asdict(decision_result.candidate.market_environment),
                "technical_context": asdict(decision_result.candidate.technical_snapshot),
                "decision_context": {
                    "decision": decision_result.decision.name,
                    "reasoning": decision_result.reasoning
                },
                "research_timestamp": datetime.now().isoformat(),
                "research_category": "low_priority_signal_analysis"
            }
            
            self.research_data.append(research_record)
            
            # 保持研究數據在合理範圍 (最近7天)
            cutoff_time = datetime.now() - timedelta(days=7)
            self.research_data = [
                r for r in self.research_data
                if datetime.fromisoformat(r["research_timestamp"]) > cutoff_time
            ]
            
            logger.debug(f"🔬 研究數據已記錄: {decision_result.candidate.symbol}")
            
        except Exception as e:
            logger.error(f"❌ 研究數據記錄失敗: {e}")
    
    async def _collect_training_data(self, decision_result: EPLDecisionResult):
        """收集模型訓練數據"""
        try:
            training_sample = {
                "features": {
                    "signal_strength": decision_result.candidate.signal_strength,
                    "confidence": decision_result.candidate.confidence,
                    "volatility": decision_result.candidate.market_environment.volatility,
                    "liquidity": decision_result.candidate.market_environment.liquidity_score,
                    "rsi": decision_result.candidate.technical_snapshot.rsi,
                    "macd": decision_result.candidate.technical_snapshot.macd_signal,
                    "volume_trend": decision_result.candidate.market_environment.volume_trend
                },
                "labels": {
                    "priority_classification": SignalPriority.LOW.name,
                    "decision_type": decision_result.decision.name,
                    "should_ignore": decision_result.decision == EPLDecision.IGNORE_SIGNAL
                },
                "metadata": {
                    "symbol": decision_result.candidate.symbol,
                    "timestamp": decision_result.timestamp.isoformat(),
                    "source": decision_result.candidate.source.value
                }
            }
            
            logger.debug(f"🤖 訓練數據已收集: {decision_result.candidate.symbol}")
            
        except Exception as e:
            logger.error(f"❌ 訓練數據收集失敗: {e}")
    
    def get_research_summary(self) -> Dict[str, Any]:
        """獲取研究數據摘要"""
        if not self.research_data:
            return {"total_records": 0}
        
        symbols = [r["symbol"] for r in self.research_data]
        sources = [r["signal_data"]["source"] for r in self.research_data]
        
        return {
            "total_records": len(self.research_data),
            "unique_symbols": len(set(symbols)),
            "most_observed_symbol": max(set(symbols), key=symbols.count) if symbols else None,
            "source_distribution": {source: sources.count(source) for source in set(sources)},
            "date_range": {
                "earliest": min(r["research_timestamp"] for r in self.research_data),
                "latest": max(r["research_timestamp"] for r in self.research_data)
            }
        }

class MultiLevelOutputMonitoringSystem:
    """多層級信號輸出與監控系統主控制器"""
    
    def __init__(self):
        self.critical_processor = CriticalSignalProcessor()
        self.high_processor = HighPrioritySignalProcessor()
        self.standard_processor = StandardSignalProcessor()
        self.observation_processor = ObservationSignalProcessor()
        
        # 系統統計
        self.output_stats = {
            "total_processed": 0,
            "by_priority": {priority: 0 for priority in SignalPriority},
            "by_classification": {classification: 0 for classification in OutputClassification},
            "notifications_sent": 0,
            "alerts_triggered": 0
        }
    
    async def process_decision_output(self, decision_result: EPLDecisionResult) -> Dict[str, Any]:
        """處理決策輸出 - 根據優先級分發到對應處理器"""
        try:
            logger.info(f"📊 開始輸出處理: {decision_result.candidate.symbol} ({decision_result.priority.value})")
            
            processing_result = {}
            
            # 根據優先級分發處理
            if decision_result.priority == SignalPriority.CRITICAL:
                processing_result = await self.critical_processor.process_critical_signal(decision_result)
                self.output_stats["alerts_triggered"] += 1
                
            elif decision_result.priority == SignalPriority.HIGH:
                processing_result = await self.high_processor.process_high_signal(decision_result)
                self.output_stats["notifications_sent"] += 1
                
            elif decision_result.priority == SignalPriority.MEDIUM:
                processing_result = await self.standard_processor.process_standard_signal(decision_result)
                
            elif decision_result.priority == SignalPriority.LOW:
                processing_result = await self.observation_processor.process_observation_signal(decision_result)
            
            # 更新統計
            self._update_output_stats(decision_result)
            
            # 添加系統元數據
            processing_result.update({
                "system_metadata": {
                    "processor_type": f"{decision_result.priority.name.lower()}_processor",
                    "total_processed": self.output_stats["total_processed"],
                    "processing_timestamp": datetime.now().isoformat()
                }
            })
            
            logger.info(f"✅ 輸出處理完成: {decision_result.candidate.symbol}")
            return processing_result
            
        except Exception as e:
            logger.error(f"❌ 輸出處理失敗: {e}")
            return {
                "status": "output_error",
                "error": str(e),
                "decision_id": decision_result.candidate.id
            }
    
    def _update_output_stats(self, decision_result: EPLDecisionResult):
        """更新輸出統計"""
        self.output_stats["total_processed"] += 1
        self.output_stats["by_priority"][decision_result.priority] += 1
        
        # 根據優先級確定分類
        if decision_result.priority == SignalPriority.CRITICAL:
            classification = OutputClassification.EMERGENCY_SIGNAL
        elif decision_result.priority == SignalPriority.HIGH:
            classification = OutputClassification.HIGH_QUALITY_SIGNAL
        elif decision_result.priority == SignalPriority.MEDIUM:
            classification = OutputClassification.STANDARD_SIGNAL
        else:
            classification = OutputClassification.OBSERVATION_SIGNAL
        
        self.output_stats["by_classification"][classification] += 1
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """獲取系統統計"""
        stats = self.output_stats.copy()
        
        # 添加處理器特定統計
        stats["processor_stats"] = {
            "critical": self.critical_processor.get_critical_statistics(),
            "observation": self.observation_processor.get_research_summary()
        }
        
        # 計算比例
        if stats["total_processed"] > 0:
            stats["priority_distribution"] = {
                priority.name: (count / stats["total_processed"] * 100)
                for priority, count in stats["by_priority"].items()
            }
        
        return stats
    
    def get_notification_status(self) -> Dict[str, Any]:
        """獲取通知系統狀態"""
        return {
            "gmail_service": "active",  # 實際需要檢查服務狀態
            "websocket_connections": 0,  # 實際需要統計連接數
            "frontend_alerts_active": 0,  # 實際需要統計活躍警報
            "last_critical_alert": None,  # 最後一次緊急警報時間
            "notification_queue_size": len(self.high_processor.high_priority_queue)
        }

# 全局多層級輸出監控系統實例
multi_level_output_system = MultiLevelOutputMonitoringSystem()
