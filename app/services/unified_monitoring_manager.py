#!/usr/bin/env python3
"""
🎯 Trading X - 整合監控與通知管理器
統一管理所有信號處理流程與Gmail通知

Author: Trading X Team  
Version: 2.0.0
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

from .signal_quality_control_engine import (
    SignalQualityControlEngine, 
    SignalCandidate, 
    EPLDecision, 
    SignalPriority, 
    EPLAction,
    signal_quality_engine
)
from .gmail_notification import GmailNotificationService
from .realtime_signal_engine import RealtimeSignalEngine

logger = logging.getLogger(__name__)

class UnifiedMonitoringManager:
    """🎯 統一監控管理器 - 整合信號處理、品質控制與通知"""
    
    def __init__(self):
        self.quality_engine = signal_quality_engine
        self.gmail_service: Optional[GmailNotificationService] = None
        self.realtime_engine: Optional[RealtimeSignalEngine] = None
        
        # 監控狀態
        self.monitoring_active = False
        self.websocket_callbacks = []
        
        # 通知設定
        self.notification_config = {
            'gmail_enabled': False,
            'notification_rules': {
                'CRITICAL': {'immediate': True, 'cooldown_minutes': 1},
                'HIGH': {'immediate': False, 'delay_minutes': 5, 'cooldown_minutes': 15},
                'MEDIUM': {'immediate': False, 'delay_minutes': 30, 'cooldown_minutes': 60},
                'LOW': {'immediate': False, 'batch_notify': True}
            }
        }
        
        # 統計監控
        self.monitoring_stats = {
            'signals_processed_today': 0,
            'notifications_sent_today': 0,
            'last_signal_time': None,
            'system_health': 'HEALTHY',
            'performance_metrics': {
                'avg_processing_time_ms': 0,
                'success_rate': 0.0,
                'notification_success_rate': 0.0
            }
        }
        
        logger.info("🎯 統一監控管理器初始化完成")

    async def initialize_services(self, 
                                  gmail_sender: str = None,
                                  gmail_password: str = None, 
                                  gmail_recipient: str = None):
        """初始化所有服務"""
        try:
            # 設置Gmail服務
            if gmail_sender and gmail_password:
                self.gmail_service = GmailNotificationService(
                    sender_email=gmail_sender,
                    sender_password=gmail_password,
                    recipient_email=gmail_recipient or gmail_sender
                )
                self.notification_config['gmail_enabled'] = True
                logger.info("📧 Gmail通知服務已初始化")
            
            # 整合實時信號引擎
            try:
                from .realtime_signal_engine import realtime_signal_engine
                self.realtime_engine = realtime_signal_engine
                logger.info("🔗 實時信號引擎已連接")
            except ImportError:
                logger.warning("⚠️ 實時信號引擎不可用")
            
            # 啟動監控
            self.monitoring_active = True
            logger.info("✅ 統一監控系統已啟動")
            
        except Exception as e:
            logger.error(f"❌ 初始化服務失敗: {e}")
            raise

    async def process_incoming_signal(self, signal_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        處理傳入的信號 - 主要入口點
        
        Args:
            signal_data: 原始信號數據
            
        Returns:
            處理結果與決策信息
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"🎯 接收新信號: {signal_data.get('symbol', 'UNKNOWN')} {signal_data.get('signal_type', 'UNKNOWN')}")
            
            # 轉換為SignalCandidate
            candidate = self._convert_to_candidate(signal_data)
            if not candidate:
                logger.warning("⚠️ 信號數據轉換失敗")
                return None
            
            # 通過品質控制引擎處理
            decision = await self.quality_engine.process_signal_candidate(candidate)
            
            if not decision:
                logger.info(f"🔍 信號被過濾: {candidate.symbol} (去重或品質不足)")
                return {'status': 'filtered', 'reason': 'duplicate_or_low_quality'}
            
            # 根據決策執行動作
            result = await self._execute_decision(candidate, decision)
            
            # 發送通知（如果需要）
            await self._handle_notifications(candidate, decision, result)
            
            # 更新統計
            self._update_statistics(start_time, True)
            
            logger.info(f"✅ 信號處理完成: {decision.action.value} | 優先級: {decision.priority.value}")
            
            return {
                'status': 'processed',
                'candidate': candidate.to_dict(),
                'decision': {
                    'action': decision.action.value,
                    'priority': decision.priority.value,
                    'reasoning': decision.reasoning
                },
                'result': result,
                'processing_time_ms': (datetime.now() - start_time).total_seconds() * 1000
            }
            
        except Exception as e:
            logger.error(f"❌ 處理信號時發生錯誤: {e}")
            self._update_statistics(start_time, False)
            return {'status': 'error', 'error': str(e)}

    def _convert_to_candidate(self, signal_data: Dict[str, Any]) -> Optional[SignalCandidate]:
        """將原始信號數據轉換為SignalCandidate"""
        try:
            # 必要欄位檢查
            required_fields = ['symbol', 'signal_type', 'confidence', 'entry_price']
            for field in required_fields:
                if field not in signal_data:
                    logger.error(f"❌ 缺少必要欄位: {field}")
                    return None
            
            # 計算品質分數（如果沒有提供）
            quality_score = signal_data.get('quality_score')
            if quality_score is None:
                quality_score = self._calculate_quality_score(signal_data)
            
            # 生成唯一ID
            signal_id = f"{signal_data['symbol']}_{signal_data['signal_type']}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            return SignalCandidate(
                id=signal_id,
                symbol=signal_data['symbol'],
                signal_type=signal_data['signal_type'],
                confidence=float(signal_data['confidence']),
                entry_price=float(signal_data['entry_price']),
                stop_loss=float(signal_data.get('stop_loss', 0)),
                take_profit=float(signal_data.get('take_profit', 0)),
                quality_score=float(quality_score),
                source=signal_data.get('source', 'unknown'),
                indicators_used=signal_data.get('indicators_used', []),
                reasoning=signal_data.get('reasoning', '技術分析指標匯聚'),
                timeframe=signal_data.get('timeframe', '1h'),
                created_at=datetime.now(),
                market_conditions=signal_data.get('market_conditions', {})
            )
            
        except Exception as e:
            logger.error(f"❌ 轉換信號數據錯誤: {e}")
            return None

    def _calculate_quality_score(self, signal_data: Dict[str, Any]) -> float:
        """計算信號品質分數"""
        try:
            score = 50.0  # 基礎分數
            
            # 信心度貢獻 (0-30分)
            confidence = float(signal_data.get('confidence', 0))
            score += confidence * 30
            
            # 技術指標數量貢獻 (0-15分)
            indicators_count = len(signal_data.get('indicators_used', []))
            score += min(indicators_count * 3, 15)
            
            # 風險回報比貢獻 (0-15分)
            rr_ratio = signal_data.get('risk_reward_ratio', 1.0)
            if rr_ratio >= 2.0:
                score += 15
            elif rr_ratio >= 1.5:
                score += 10
            elif rr_ratio >= 1.0:
                score += 5
            
            # 來源權重調整
            source_weights = {
                'sniper': 1.2,      # 狙擊手系統
                'phase1abc': 1.15,  # Phase1ABC系統
                'phase23': 1.1,     # Phase2+3系統
                'pandas_ta': 1.0    # 標準技術分析
            }
            source = signal_data.get('source', 'unknown')
            weight = source_weights.get(source, 1.0)
            score *= weight
            
            return min(score, 100.0)  # 限制最高分數
            
        except Exception as e:
            logger.error(f"❌ 計算品質分數錯誤: {e}")
            return 50.0

    async def _execute_decision(self, candidate: SignalCandidate, decision: EPLDecision) -> Dict[str, Any]:
        """執行EPL決策"""
        try:
            result = {
                'executed': False,
                'action_taken': decision.action.value,
                'priority': decision.priority.value,
                'timestamp': datetime.now().isoformat()
            }
            
            if decision.action == EPLAction.NEW_ORDER:
                # 建立新信號
                result.update(await self._create_new_signal(candidate, decision))
                
            elif decision.action == EPLAction.REPLACE:
                # 替換現有信號
                result.update(await self._replace_existing_signal(candidate, decision))
                
            elif decision.action == EPLAction.ENHANCE:
                # 強化現有信號
                result.update(await self._enhance_existing_signal(candidate, decision))
                
            elif decision.action == EPLAction.IGNORE:
                # 忽略信號
                result['ignored_reason'] = decision.reasoning
                
            return result
            
        except Exception as e:
            logger.error(f"❌ 執行決策錯誤: {e}")
            return {'executed': False, 'error': str(e)}

    async def _create_new_signal(self, candidate: SignalCandidate, decision: EPLDecision) -> Dict[str, Any]:
        """建立新信號"""
        try:
            # 這裡可以整合到實際的信號儲存系統
            # 例如：狙擊手資料庫、交易信號表等
            
            logger.info(f"📊 建立新信號: {candidate.symbol} {candidate.signal_type}")
            
            # 如果有實時引擎，可以直接儲存
            if self.realtime_engine:
                # 轉換為TradingSignalAlert格式並儲存
                pass
            
            return {
                'executed': True,
                'signal_id': candidate.id,
                'action': 'new_signal_created',
                'position_size': decision.execution_params.get('position_size', 0.05)
            }
            
        except Exception as e:
            logger.error(f"❌ 建立新信號錯誤: {e}")
            return {'executed': False, 'error': str(e)}

    async def _replace_existing_signal(self, candidate: SignalCandidate, decision: EPLDecision) -> Dict[str, Any]:
        """替換現有信號"""
        try:
            logger.info(f"🔁 替換信號: {candidate.symbol} (舊信號ID: {decision.related_signal_id})")
            
            return {
                'executed': True,
                'new_signal_id': candidate.id,
                'replaced_signal_id': decision.related_signal_id,
                'action': 'signal_replaced',
                'confidence_improvement': decision.confidence_delta
            }
            
        except Exception as e:
            logger.error(f"❌ 替換信號錯誤: {e}")
            return {'executed': False, 'error': str(e)}

    async def _enhance_existing_signal(self, candidate: SignalCandidate, decision: EPLDecision) -> Dict[str, Any]:
        """強化現有信號"""
        try:
            logger.info(f"➕ 強化信號: {candidate.symbol} (基於信號ID: {decision.related_signal_id})")
            
            enhancement_ratio = decision.execution_params.get('enhancement_ratio', 0.2)
            
            return {
                'executed': True,
                'enhanced_signal_id': decision.related_signal_id,
                'enhancement_signal_id': candidate.id,
                'action': 'signal_enhanced',
                'enhancement_ratio': enhancement_ratio,
                'confidence_improvement': decision.confidence_delta
            }
            
        except Exception as e:
            logger.error(f"❌ 強化信號錯誤: {e}")
            return {'executed': False, 'error': str(e)}

    async def _handle_notifications(self, candidate: SignalCandidate, decision: EPLDecision, result: Dict[str, Any]):
        """處理通知發送"""
        try:
            if not self.notification_config['gmail_enabled'] or not self.gmail_service:
                logger.debug("📧 Gmail通知未啟用")
                return
            
            # 檢查是否需要發送通知
            priority = decision.priority
            rules = self.notification_config['notification_rules'].get(priority.value, {})
            
            if decision.action == EPLAction.IGNORE:
                logger.debug("📧 忽略的信號不發送通知")
                return
            
            # 準備通知數據
            notification_data = {
                'symbol': candidate.symbol,
                'signal_type': candidate.signal_type,
                'priority': priority.value,
                'confidence': candidate.confidence,
                'quality_score': candidate.quality_score,
                'entry_price': candidate.entry_price,
                'stop_loss': candidate.stop_loss,
                'take_profit': candidate.take_profit,
                'reasoning': candidate.reasoning,
                'action_taken': decision.action.value,
                'decision_reasoning': decision.reasoning,
                'created_at': candidate.created_at.isoformat(),
                'update_type': 'EMERGENCY' if rules.get('immediate') else 'REGULAR'
            }
            
            # 根據優先級決定發送時機
            if rules.get('immediate', False):
                # 立即發送
                await self._send_immediate_notification(notification_data)
            else:
                # 延遲發送
                delay_minutes = rules.get('delay_minutes', 0)
                if delay_minutes > 0:
                    asyncio.create_task(self._send_delayed_notification(notification_data, delay_minutes))
                else:
                    await self._send_immediate_notification(notification_data)
                    
        except Exception as e:
            logger.error(f"❌ 處理通知錯誤: {e}")

    async def _send_immediate_notification(self, notification_data: Dict[str, Any]):
        """立即發送通知"""
        try:
            logger.info(f"📧 立即發送通知: {notification_data['symbol']} {notification_data['priority']}")
            
            success = await self.gmail_service.send_sniper_signal_notification_async(notification_data)
            
            if success:
                self.monitoring_stats['notifications_sent_today'] += 1
                logger.info(f"✅ 通知發送成功: {notification_data['symbol']}")
            else:
                logger.error(f"❌ 通知發送失敗: {notification_data['symbol']}")
                
        except Exception as e:
            logger.error(f"❌ 立即發送通知錯誤: {e}")

    async def _send_delayed_notification(self, notification_data: Dict[str, Any], delay_minutes: int):
        """延遲發送通知"""
        try:
            logger.info(f"⏰ 延遲 {delay_minutes} 分鐘發送通知: {notification_data['symbol']}")
            
            await asyncio.sleep(delay_minutes * 60)
            await self._send_immediate_notification(notification_data)
            
        except Exception as e:
            logger.error(f"❌ 延遲發送通知錯誤: {e}")

    def _update_statistics(self, start_time: datetime, success: bool):
        """更新統計數據"""
        try:
            processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            self.monitoring_stats['signals_processed_today'] += 1
            self.monitoring_stats['last_signal_time'] = datetime.now().isoformat()
            
            # 更新平均處理時間
            current_avg = self.monitoring_stats['performance_metrics']['avg_processing_time_ms']
            total_processed = self.monitoring_stats['signals_processed_today']
            
            new_avg = ((current_avg * (total_processed - 1)) + processing_time_ms) / total_processed
            self.monitoring_stats['performance_metrics']['avg_processing_time_ms'] = new_avg
            
            # 更新成功率
            if success:
                success_count = getattr(self, '_success_count', 0) + 1
                setattr(self, '_success_count', success_count)
            else:
                success_count = getattr(self, '_success_count', 0)
            
            success_rate = success_count / total_processed if total_processed > 0 else 0
            self.monitoring_stats['performance_metrics']['success_rate'] = success_rate
            
        except Exception as e:
            logger.error(f"❌ 更新統計錯誤: {e}")

    def get_monitoring_dashboard_data(self) -> Dict[str, Any]:
        """獲取監控儀表板數據"""
        try:
            # 整合各系統統計數據
            quality_stats = self.quality_engine.get_engine_statistics()
            
            dashboard_data = {
                'timestamp': datetime.now().isoformat(),
                'system_status': {
                    'monitoring_active': self.monitoring_active,
                    'gmail_enabled': self.notification_config['gmail_enabled'],
                    'system_health': self.monitoring_stats['system_health']
                },
                'today_statistics': self.monitoring_stats,
                'quality_engine': quality_stats,
                'notification_stats': self.gmail_service.get_notification_stats() if self.gmail_service else {},
                'performance_metrics': self.monitoring_stats['performance_metrics']
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"❌ 獲取儀表板數據錯誤: {e}")
            return {'error': str(e)}

    async def start_monitoring(self):
        """啟動監控循環"""
        try:
            self.monitoring_active = True
            logger.info("🎯 開始統一監控循環")
            
            while self.monitoring_active:
                # 定期清理過期數據
                await self.quality_engine.cleanup_expired_positions()
                
                # 健康檢查
                await self._health_check()
                
                # 每30秒檢查一次
                await asyncio.sleep(30)
                
        except Exception as e:
            logger.error(f"❌ 監控循環錯誤: {e}")
            self.monitoring_stats['system_health'] = 'ERROR'

    async def _health_check(self):
        """系統健康檢查"""
        try:
            # 檢查各組件狀態
            health_status = 'HEALTHY'
            
            # 檢查品質引擎
            quality_stats = self.quality_engine.get_engine_statistics()
            if quality_stats['stats']['total_candidates'] == 0:
                # 如果長時間沒有信號，可能有問題
                pass
            
            # 檢查Gmail服務
            if self.gmail_service and self.notification_config['gmail_enabled']:
                # 可以定期發送測試通知檢查
                pass
            
            self.monitoring_stats['system_health'] = health_status
            
        except Exception as e:
            logger.error(f"❌ 健康檢查錯誤: {e}")
            self.monitoring_stats['system_health'] = 'ERROR'

    def stop_monitoring(self):
        """停止監控"""
        self.monitoring_active = False
        logger.info("🛑 監控已停止")

# 全域統一監控管理器實例
unified_monitoring = UnifiedMonitoringManager()
