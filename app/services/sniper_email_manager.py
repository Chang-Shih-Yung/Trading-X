# 🎯 狙擊手 Email 自動發送與補發機制

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.sniper_signal_history import SniperSignalDetails, EmailStatus
from app.services.gmail_notification import GmailNotificationService

logger = logging.getLogger(__name__)

class SniperEmailManager:
    """🎯 狙擊手 Email 管理器 - 自動發送與補發機制"""
    
    def __init__(self):
        self.gmail_service: Optional[GmailNotificationService] = None
        self.scanning_task: Optional[asyncio.Task] = None
        self.is_running = False
        self._sent_signals_today = set()  # 🎯 今日已發送的幣種記錄
        
    def initialize_gmail_service(self, sender_email: str, sender_password: str, recipient_email: str):
        """初始化 Gmail 服務"""
        try:
            self.gmail_service = GmailNotificationService(
                sender_email=sender_email,
                sender_password=sender_password,
                recipient_email=recipient_email
            )
            logger.info("✅ Email 管理器 Gmail 服務初始化成功")
            return True
        except Exception as e:
            logger.error(f"❌ Email 管理器 Gmail 服務初始化失敗: {e}")
            return False
    
    async def start_auto_scanning(self):
        """啟動自動掃描任務 - 每個幣種只發送最優秀的信號"""
        if self.is_running:
            logger.warning("Email 自動掃描已在運行中")
            return
            
        self.is_running = True
        logger.info("🚀 啟動 Email 自動掃描 (30秒間隔，每幣種最優信號)")
        
        # 🎯 清理昨日記錄
        self._cleanup_sent_signals_record()
        
        while self.is_running:
            try:
                await self._scan_and_send_best_signals()
                await asyncio.sleep(30)  # 🎯 30秒掃描間隔
            except Exception as e:
                logger.error(f"❌ Email 自動掃描異常: {e}")
                await asyncio.sleep(30)

    async def stop_auto_scanning(self):
        """停止自動掃描任務"""
        self.is_running = False
        if self.scanning_task:
            self.scanning_task.cancel()
        logger.info("🛑 Email 自動掃描已停止")
    
    def _cleanup_sent_signals_record(self):
        """清理過期的已發送記錄"""
        today_prefix = datetime.now().strftime('%Y%m%d')
        # 移除非今日的記錄
        self._sent_signals_today = {
            key for key in self._sent_signals_today 
            if key.endswith(today_prefix)
        }
        logger.info(f"🧹 清理過期發送記錄，保留今日記錄: {len(self._sent_signals_today)} 筆")
    
    async def has_sent_signal_email(self, signal_id: str) -> bool:
        """檢查指定信號是否已發送過Email"""
        try:
            # 🎯 優先檢查記憶體記錄（用於精選信號）
            if hasattr(self, '_sent_signal_ids') and signal_id in self._sent_signal_ids:
                return True
            
            # 檢查資料庫記錄
            db_gen = get_db()
            db = await db_gen.__anext__()
            
            try:
                result = await db.execute(
                    select(SniperSignalDetails).where(
                        SniperSignalDetails.signal_id == signal_id
                    )
                )
                signal = result.scalar_one_or_none()
                
                if signal and signal.email_status == EmailStatus.SENT:
                    return True
                return False
                
            finally:
                await db_gen.aclose()
                
        except Exception as e:
            logger.error(f"檢查Email發送狀態失敗 {signal_id}: {e}")
            return False
    
    async def send_signal_email_immediately(self, signal_id: str, signal_data: dict = None) -> bool:
        """立即發送信號 Email (新信號產生時調用)"""
        if not self.gmail_service:
            logger.warning("Gmail 服務未初始化，跳過立即發送")
            return False
            
        try:
            # 🎯 改進：支援直接使用傳入的信號數據（用於API精選信號）
            if signal_data:
                # 使用傳入的精選信號數據
                logger.info(f"📧 使用API精選信號數據發送Email: {signal_id}")
                
                # 檢查是否已發送過（基於信號ID）
                if await self.has_sent_signal_email(signal_id):
                    logger.info(f"📧 精選信號 {signal_id} Email 已發送，跳過")
                    return True
                
                # 創建臨時信號對象用於發送Email
                class TempSignal:
                    def __init__(self, data):
                        self.signal_id = signal_id
                        self.symbol = data.get('symbol', 'Unknown')
                        self.signal_type = data.get('signal_type', 'BUY')
                        self.entry_price = data.get('entry_price', 0)
                        self.stop_loss = data.get('stop_loss', 0)
                        self.take_profit = data.get('take_profit', 0)
                        self.confidence = data.get('confidence', 0)
                        self.reasoning = data.get('reasoning', '狙擊手精選信號')
                        self.created_at = datetime.utcnow()
                        self.email_status = EmailStatus.PENDING
                
                temp_signal = TempSignal(signal_data)
                success = await self._attempt_send_email(temp_signal, max_retries=3)
                
                if success:
                    # 記錄發送成功（避免重複發送）
                    await self._record_email_sent(signal_id)
                    logger.info(f"✅ 精選信號 {signal_id} Email 發送成功")
                    return True
                else:
                    logger.error(f"❌ 精選信號 {signal_id} Email 發送失敗")
                    return False
            
            else:
                # 原始邏輯：從資料庫獲取信號詳情
                db_gen = get_db()
                db = await db_gen.__anext__()
                
                try:
                    result = await db.execute(
                        select(SniperSignalDetails).where(
                            SniperSignalDetails.signal_id == signal_id
                        )
                    )
                    signal = result.scalar_one_or_none()
                    
                    if not signal:
                        logger.warning(f"找不到信號: {signal_id}")
                        return False
                    
                    # 檢查是否已發送過
                    if signal.email_status == EmailStatus.SENT:
                        logger.info(f"📧 信號 {signal_id} Email 已發送，跳過")
                        return True
                    
                    # 更新狀態為發送中
                    await self._update_email_status(db, signal_id, EmailStatus.SENDING)
                    
                    # 嘗試發送 (最多重試 3 次)
                    success = await self._attempt_send_email(signal, max_retries=3)
                    
                    if success:
                        await self._update_email_status(db, signal_id, EmailStatus.SENT, 
                                                      sent_at=datetime.utcnow())
                        logger.info(f"✅ 信號 {signal_id} Email 立即發送成功")
                        return True
                    else:
                        await self._update_email_status(db, signal_id, EmailStatus.FAILED,
                                                      error_msg="立即發送失敗，等待定期掃描重試")
                        logger.warning(f"❌ 信號 {signal_id} Email 立即發送失敗")
                        return False
                        
                finally:
                    await db_gen.aclose()
                
        except Exception as e:
            logger.error(f"❌ 立即發送 Email 異常: {e}")
            return False
    
    async def _record_email_sent(self, signal_id: str):
        """記錄Email已發送狀態（用於精選信號）"""
        try:
            # 這裡可以選擇將記錄保存到記憶體或資料庫
            # 簡單實現：使用類屬性記錄已發送的信號ID
            if not hasattr(self, '_sent_signal_ids'):
                self._sent_signal_ids = set()
            
            self._sent_signal_ids.add(signal_id)
            logger.info(f"📧 記錄信號 {signal_id} Email 已發送")
            
        except Exception as e:
            logger.error(f"記錄Email發送狀態失敗 {signal_id}: {e}")
    
    
    async def _scan_and_send_best_signals(self):
        """掃描並發送每個幣種最優秀的信號 Email"""
        if not self.gmail_service:
            return
            
        try:
            # 🧹 首先清理過期的已發送記錄
            self._cleanup_sent_signals_record()
            
            db_gen = get_db()
            db = await db_gen.__anext__()
            
            try:
                from sqlalchemy import func, desc
                
                # 🎯 查詢每個幣種信心度最高且未發送的信號
                subquery = (
                    select(
                        SniperSignalDetails.symbol,
                        func.max(SniperSignalDetails.signal_strength).label('max_strength'),
                        func.min(SniperSignalDetails.created_at).label('earliest_time')  # 🎯 找最早的時間
                    )
                    .where(
                        and_(
                            SniperSignalDetails.email_status.in_([EmailStatus.PENDING, EmailStatus.FAILED]),
                            SniperSignalDetails.email_sent_at.is_(None),  # 🛡️ 確保未發送過
                            SniperSignalDetails.email_retry_count < 5,    # 🛡️ 重試次數限制
                            SniperSignalDetails.created_at >= datetime.now() - timedelta(hours=24)  # 只處理24小時內的信號
                        )
                    )
                    .group_by(SniperSignalDetails.symbol)
                    .subquery()
                )
                
                # 獲取最優秀的信號詳情 (每個幣種只取最早的最佳品質信號)
                result = await db.execute(
                    select(SniperSignalDetails)
                    .join(
                        subquery,
                        and_(
                            SniperSignalDetails.symbol == subquery.c.symbol,
                            SniperSignalDetails.signal_strength == subquery.c.max_strength
                        )
                    )
                    .where(
                        and_(
                            SniperSignalDetails.email_status.in_([EmailStatus.PENDING, EmailStatus.FAILED]),
                            SniperSignalDetails.email_sent_at.is_(None),  # 🛡️ 雙重確認未發送
                            SniperSignalDetails.email_retry_count < 5      # 🛡️ 重試次數限制
                        )
                    )
                    .order_by(
                        SniperSignalDetails.symbol,
                        desc(SniperSignalDetails.signal_strength),
                        SniperSignalDetails.created_at.asc()  # 🎯 相同品質時，選擇最早的
                    )
                )
                
                best_signals = result.scalars().all()
                
                if not best_signals:
                    logger.debug("📧 沒有待發送的最優信號")
                    return
                
                # 🎯 去重：確保每個幣種只選擇一個信號（選擇最早的最佳品質信號）
                unique_signals = {}
                for signal in best_signals:
                    if signal.symbol not in unique_signals:
                        unique_signals[signal.symbol] = signal
                    else:
                        # 如果已存在該幣種，比較創建時間，選擇更早的
                        existing = unique_signals[signal.symbol]
                        if signal.created_at < existing.created_at:  # 🎯 選擇更早的
                            unique_signals[signal.symbol] = signal
                
                best_signals = list(unique_signals.values())
                logger.info(f"📧 找到 {len(best_signals)} 個幣種的最優信號 (已去重)")
                
                for signal in best_signals:
                    try:
                        # 🛡️ 檢查今日是否已發送該幣種信號
                        symbol_key = f"{signal.symbol}_{datetime.now().strftime('%Y%m%d')}"
                        if symbol_key in self._sent_signals_today:
                            logger.debug(f"⏭️ 今日已發送 {signal.symbol} 信號，跳過")
                            continue
                        
                        # 🛡️ 再次確認未發送過
                        if signal.email_status == EmailStatus.SENT or signal.email_sent_at:
                            logger.debug(f"⏭️ 跳過已發送信號: {signal.signal_id}")
                            continue
                        
                        # 更新狀態為發送中
                        await self._update_email_status(db, signal.signal_id, EmailStatus.SENDING)
                        
                        # 嘗試發送
                        success = await self._attempt_send_email(signal, max_retries=3)
                        
                        if success:
                            await self._update_email_status(db, signal.signal_id, EmailStatus.SENT,
                                                          sent_at=datetime.utcnow())
                            
                            # 🎯 記錄今日已發送該幣種
                            self._sent_signals_today.add(symbol_key)
                            
                            logger.info(f"✅ 發送成功: {signal.symbol} 最優信號 (信心度: {signal.signal_strength:.3f})")
                        else:
                            # 檢查重試次數限制
                            current_retry_count = signal.email_retry_count + 1
                            
                            if current_retry_count >= 5:  # 最多重試 5 次
                                await self._update_email_status(db, signal.signal_id, EmailStatus.FAILED,
                                                              error_msg=f"發送失敗，已達最大重試次數 ({current_retry_count})")
                                logger.error(f"❌ 發送徹底失敗: {signal.symbol} {signal.signal_id}，已達最大重試次數 {current_retry_count}")
                            else:
                                # 發送失敗，增加重試次數
                                await self._increment_retry_count(db, signal.signal_id)
                                await self._update_email_status(db, signal.signal_id, EmailStatus.FAILED,
                                                              error_msg=f"發送失敗，30秒後重試 (次數: {current_retry_count})")
                                logger.warning(f"❌ 發送失敗: {signal.symbol} {signal.signal_id}，30秒後重試 (次數: {current_retry_count})")
                        
                        # 發送間隔 - 避免過於頻繁
                        await asyncio.sleep(3)
                        
                    except Exception as e:
                        logger.error(f"❌ 處理信號 {signal.signal_id} 時異常: {e}")
                        continue
                        
            finally:
                await db.close()
                
        except Exception as e:
            logger.error(f"❌ 掃描最優信號異常: {e}")
    
    async def _scan_and_send_pending_emails(self):
        """掃描並發送待發送的 Email"""
        if not self.gmail_service:
            return
            
        try:
            db_gen = get_db()
            db = await db_gen.__anext__()
            
            try:
                # 查詢待發送和失敗的信號 (排除已發送和發送中的)
                result = await db.execute(
                    select(SniperSignalDetails).where(
                        and_(
                            SniperSignalDetails.email_status.in_([
                                EmailStatus.PENDING, 
                                EmailStatus.FAILED
                            ]),
                            SniperSignalDetails.email_retry_count < 5,  # 🎯 統一重試限制為 5 次
                            SniperSignalDetails.email_sent_at.is_(None)  # 🛡️ 確保未發送過
                        )
                    )
                )
                pending_signals = result.scalars().all()
                
                if not pending_signals:
                    logger.debug("📧 沒有待發送的 Email")
                    return
                
                logger.info(f"📧 掃描到 {len(pending_signals)} 個待發送信號")
                
                for signal in pending_signals:
                    try:
                        # 🛡️ 雙重檢查：確保信號未發送過
                        if signal.email_status == EmailStatus.SENT or signal.email_sent_at:
                            logger.debug(f"⏭️ 跳過已發送信號: {signal.signal_id}")
                            continue
                        
                        # 更新狀態為重試中
                        await self._update_email_status(db, signal.signal_id, EmailStatus.RETRYING)
                        
                        # 嘗試發送
                        success = await self._attempt_send_email(signal, max_retries=1)
                        
                        if success:
                            await self._update_email_status(db, signal.signal_id, EmailStatus.SENT,
                                                          sent_at=datetime.utcnow())
                            logger.info(f"✅ 補發成功: {signal.symbol} {signal.signal_id}")
                        else:
                            # 檢查重試次數限制
                            current_retry_count = signal.email_retry_count + 1
                            
                            if current_retry_count >= 5:  # 最多重試 5 次
                                await self._update_email_status(db, signal.signal_id, EmailStatus.FAILED,
                                                              error_msg=f"補發徹底失敗，已達最大重試次數 ({current_retry_count})")
                                logger.error(f"❌ 補發徹底失敗: {signal.symbol} {signal.signal_id}，已達最大重試次數 {current_retry_count}")
                            else:
                                # 增加重試次數
                                await self._increment_retry_count(db, signal.signal_id)
                                await self._update_email_status(db, signal.signal_id, EmailStatus.FAILED,
                                                              error_msg=f"掃描重試失敗 (次數: {current_retry_count})")
                                logger.warning(f"❌ 補發失敗: {signal.symbol} {signal.signal_id}，重試次數: {current_retry_count}")
                        
                        # 避免發送過快 - 加長間隔
                        await asyncio.sleep(15)  # 🎯 延長到5秒，避免頻繁操作
                        
                    except Exception as e:
                        logger.error(f"❌ 處理信號 {signal.signal_id} 時異常: {e}")
                        continue
                        
            finally:
                await db.close()
                
        except Exception as e:
            logger.error(f"❌ 掃描待發送 Email 異常: {e}")
    
    async def resend_failed_email(self, signal_id: str) -> bool:
        """手動重新發送失敗的 Email (前端按鈕調用)"""
        if not self.gmail_service:
            logger.warning("Gmail 服務未初始化")
            return False
            
        try:
            db_gen = get_db()
            db = await db_gen.__anext__()
            
            try:
                result = await db.execute(
                    select(SniperSignalDetails).where(
                        SniperSignalDetails.signal_id == signal_id
                    )
                )
                signal = result.scalar_one_or_none()
                
                if not signal:
                    logger.warning(f"找不到信號: {signal_id}")
                    return False
                
                # 檢查是否已發送
                if signal.email_status == EmailStatus.SENT:
                    logger.warning(f"信號 {signal_id} Email 已發送，不能重複發送")
                    return False
                
                # 更新狀態為發送中
                await self._update_email_status(db, signal_id, EmailStatus.SENDING)
                
                # 嘗試發送
                success = await self._attempt_send_email(signal, max_retries=3)
                
                if success:
                    await self._update_email_status(db, signal_id, EmailStatus.SENT,
                                                  sent_at=datetime.utcnow())
                    logger.info(f"✅ 手動重發成功: {signal.symbol} {signal_id}")
                    return True
                else:
                    await self._update_email_status(db, signal_id, EmailStatus.FAILED,
                                                  error_msg="手動重發失敗")
                    logger.warning(f"❌ 手動重發失敗: {signal.symbol} {signal_id}")
                    return False
                    
            finally:
                await db.close()
                
        except Exception as e:
            logger.error(f"❌ 手動重發 Email 異常: {e}")
            return False
    
    async def _attempt_send_email(self, signal: SniperSignalDetails, max_retries: int = 3) -> bool:
        """嘗試發送 Email (帶重試機制)"""
        for attempt in range(max_retries):
            try:
                # 構建信號資訊
                signal_info = {
                    'symbol': signal.symbol,
                    'signal_type': signal.signal_type,
                    'entry_price': signal.entry_price,
                    'stop_loss': signal.stop_loss_price,
                    'take_profit': signal.take_profit_price,
                    'confidence': signal.signal_strength,
                    'quality_score': signal.signal_strength * 10,  # 轉換為1-10分
                    'timeframe': signal.timeframe.value if signal.timeframe else '1h',
                    'reasoning': signal.reasoning or '狙擊手智能分層信號',
                    'created_at': signal.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'update_type': 'REGULAR',
                    'priority': 'HIGH' if signal.signal_strength >= 0.7 else 'MEDIUM',
                    'risk_reward_ratio': signal.risk_reward_ratio
                }
                
                # 發送 Email
                success = await self.gmail_service.send_sniper_signal_notification_async(signal_info)
                
                if success:
                    return True
                else:
                    logger.warning(f"第 {attempt + 1} 次發送失敗: {signal.signal_id}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # 指數退避
                    
            except Exception as e:
                logger.error(f"第 {attempt + 1} 次發送異常: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    
        return False
    
    async def _update_email_status(self, db: AsyncSession, signal_id: str, status: EmailStatus, 
                                  sent_at: Optional[datetime] = None, error_msg: Optional[str] = None):
        """更新 Email 狀態"""
        update_data = {'email_status': status}
        
        if sent_at:
            update_data['email_sent_at'] = sent_at
        if error_msg:
            update_data['email_last_error'] = error_msg
            
        await db.execute(
            update(SniperSignalDetails)
            .where(SniperSignalDetails.signal_id == signal_id)
            .values(**update_data)
        )
        await db.commit()
    
    async def _increment_retry_count(self, db: AsyncSession, signal_id: str):
        """增加重試次數"""
        await db.execute(
            update(SniperSignalDetails)
            .where(SniperSignalDetails.signal_id == signal_id)
            .values(email_retry_count=SniperSignalDetails.email_retry_count + 1)
        )
        await db.commit()
    
    async def get_email_status_summary(self) -> dict:
        """獲取 Email 發送狀態統計"""
        try:
            db_gen = get_db()
            db = await db_gen.__anext__()
            
            try:
                from sqlalchemy import func
                
                result = await db.execute(
                    select(
                        SniperSignalDetails.email_status,
                        func.count(SniperSignalDetails.id).label('count')
                    ).group_by(SniperSignalDetails.email_status)
                )
                
                status_counts = {row.email_status.value: row.count for row in result}
                
                return {
                    'total_signals': sum(status_counts.values()),
                    'status_breakdown': status_counts,
                    'success_rate': round(status_counts.get('SENT', 0) / max(sum(status_counts.values()), 1) * 100, 2)
                }
                
            finally:
                await db.close()
                
        except Exception as e:
            logger.error(f"❌ 獲取 Email 狀態統計異常: {e}")
            return {'error': str(e)}

# 全局實例
sniper_email_manager = SniperEmailManager()
