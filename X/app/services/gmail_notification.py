import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import asyncio
import logging
from dataclasses import asdict
import json

logger = logging.getLogger(__name__)

class GmailNotificationService:
    """Gmail 通知服務 - 用於發送交易信號通知"""
    
    def __init__(self, 
                 sender_email: str, 
                 sender_password: str, 
                 recipient_email: str):
        """
        初始化 Gmail 通知服務
        
        Args:
            sender_email: 發送者郵箱 (您的Gmail帳號)
            sender_password: 應用程式密碼 (Gmail App Password)
            recipient_email: 接收者郵箱 (您要接收通知的郵箱)
        """
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email = recipient_email
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        # 通知設定
        self.enabled = True
        self.notification_history = []
        self.max_history = 100
        
        # 防止垃圾郵件的設定
        self.min_confidence_threshold = 0.6  # 只有信心度 >= 60% 才發送
        self.cooldown_minutes = 5  # 同一交易對5分鐘內只發送一次
        self.last_notifications = {}  # 追蹤最後通知時間
        
        # 防止重複發送的機制
        self.message_signatures = set()  # 追蹤已發送的消息簽名
        self.max_signatures = 1000  # 最大簽名緩存數量
        
        logger.info(f"📧 Gmail通知服務初始化完成")
    
    async def send_signal_notification(self, signal) -> bool:
        """
        發送交易信號通知郵件
        
        Args:
            signal: TradingSignalAlert 對象
            
        Returns:
            bool: 是否成功發送
        """
        try:
            # 檢查是否應該發送通知
            if not self._should_send_notification(signal):
                return False
            
            # 創建郵件內容
            message = self._create_signal_email(signal)
            
            # 發送郵件
            success = await self._send_email(message)
            
            if success:
                # 只有發送成功後才記錄通知歷史和添加簽名
                self._record_notification(signal)
                
                # 成功發送後添加簽名到緩存
                message_signature = self._generate_message_signature(signal)
                self.message_signatures.add(message_signature)
                
                # 保持簽名緩存大小
                if len(self.message_signatures) > self.max_signatures:
                    signatures_list = list(self.message_signatures)
                    self.message_signatures = set(signatures_list[-self.max_signatures//2:])
                
                logger.info(f"📧 信號通知已發送: {signal.symbol} {signal.signal_type}")
                return True
            else:
                logger.error(f"❌ 信號通知發送失敗: {signal.symbol}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 發送信號通知時發生錯誤: {e}")
            return False
    
    def _should_send_notification(self, signal) -> bool:
        """檢查是否應該發送通知"""
        try:
            # 檢查服務是否啟用
            if not self.enabled:
                return False
            
            # 檢查信心度閾值
            confidence = getattr(signal, 'confidence', 0.5)
            if confidence < self.min_confidence_threshold:
                return False
            
            # 生成消息簽名（防止重複發送相同內容）
            message_signature = self._generate_message_signature(signal)
            if message_signature in self.message_signatures:
                return False
            
            # 檢查冷卻時間
            symbol = getattr(signal, 'symbol', 'UNKNOWN')
            timeframe = getattr(signal, 'timeframe', '1h')
            key = f"{symbol}_{timeframe}"
            if key in self.last_notifications:
                last_time = self.last_notifications[key]
                time_diff = (datetime.now() - last_time).total_seconds() / 60
                if time_diff < self.cooldown_minutes:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 檢查通知條件時發生錯誤: {e}")
            return False
    
    def _generate_message_signature(self, signal) -> str:
        """生成消息簽名用於防重複"""
        try:
            symbol = getattr(signal, 'symbol', 'UNKNOWN')
            signal_type = getattr(signal, 'signal_type', 'UNKNOWN')
            confidence = getattr(signal, 'confidence', 0.5)
            entry_price = getattr(signal, 'entry_price', 0)
            timeframe = getattr(signal, 'timeframe', '1h')
            
            signature_data = f"{symbol}_{signal_type}_{confidence:.3f}_{entry_price:.6f}_{timeframe}"
            return signature_data
        except Exception:
            # 備用簽名
            return f"signal_{datetime.now().strftime('%Y%m%d%H%M')}"
    
    def _create_signal_email(self, signal) -> MIMEMultipart:
        """創建交易信號郵件"""
        try:
            # 創建郵件對象
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = self.recipient_email
            
            symbol = getattr(signal, 'symbol', 'UNKNOWN')
            signal_type = getattr(signal, 'signal_type', 'UNKNOWN')
            
            subject = f"🚀 Trading-X 交易信號 - {symbol} {signal_type}"
            message["Subject"] = subject
            
            # 創建郵件內容
            text_body = self._create_text_email_body(signal)
            
            # 添加郵件內容
            message.attach(MIMEText(text_body, "plain", "utf-8"))
            
            return message
            
        except Exception as e:
            logger.error(f"❌ 創建郵件時發生錯誤: {e}")
            raise
    
    def _create_text_email_body(self, signal) -> str:
        """創建純文字格式的郵件內容"""
        
        try:
            symbol = getattr(signal, 'symbol', 'UNKNOWN')
            signal_type = getattr(signal, 'signal_type', 'UNKNOWN')
            timeframe = getattr(signal, 'timeframe', '1h')
            confidence = getattr(signal, 'confidence', 0.5)
            entry_price = getattr(signal, 'entry_price', 0)
            stop_loss = getattr(signal, 'stop_loss', 0)
            take_profit = getattr(signal, 'take_profit', 0)
            risk_reward_ratio = getattr(signal, 'risk_reward_ratio', 1.0)
            reasoning = getattr(signal, 'reasoning', '技術分析指標匯聚')
            
            text = f"""
🚀 Trading-X 交易信號通知
════════════════════════

交易對: {symbol}
時間框架: {timeframe}
信號類型: {signal_type}
信心度: {confidence:.1%}

💰 價格資訊:
─────────────
進場價格: ${entry_price:.6f}
止損價格: ${stop_loss:.6f}
止盈價格: ${take_profit:.6f}
風險回報比: 1:{risk_reward_ratio:.2f}

🔍 分析原因:
─────────────
{reasoning}

⏰ 信號時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

═══════════════════════════════════════
🤖 此信號由 Trading-X 系統自動生成
⚠️  投資有風險，請謹慎決策
═══════════════════════════════════════
            """
            
            return text.strip()
        except Exception as e:
            logger.error(f"❌ 創建郵件內容失敗: {e}")
            return "Trading-X 信號通知（內容生成失敗）"
    
    async def _send_email(self, message: MIMEMultipart) -> bool:
        """異步發送郵件"""
        try:
            # 在線程池中執行同步的郵件發送
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._send_email_sync, message)
            return result
            
        except Exception as e:
            logger.error(f"❌ 異步發送郵件失敗: {e}")
            return False
    
    def _send_email_sync(self, message: MIMEMultipart) -> bool:
        """同步發送郵件"""
        try:
            # 創建SSL上下文
            context = ssl.create_default_context()
            
            # 連接SMTP伺服器
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)  # 啟用安全連接
                server.login(self.sender_email, self.sender_password)
                
                # 發送郵件
                text = message.as_string()
                server.sendmail(self.sender_email, self.recipient_email, text)
                
            logger.info("📧 郵件發送成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 發送郵件失敗: {e}")
            return False
    
    def _record_notification(self, signal):
        """記錄通知歷史"""
        try:
            symbol = getattr(signal, 'symbol', 'UNKNOWN')
            timeframe = getattr(signal, 'timeframe', '1h')
            
            # 更新最後通知時間
            key = f"{symbol}_{timeframe}"
            self.last_notifications[key] = datetime.now()
            
        except Exception as e:
            logger.error(f"❌ 記錄通知歷史失敗: {e}")

# 創建虛擬的 SniperEmailManager 類
class SniperEmailManager:
    """狙擊手郵件管理器 - X 資料夾內的精簡版本"""
    
    def __init__(self):
        self.enabled = True
        logger.info("📧 狙擊手郵件管理器初始化")
    
    async def send_notification(self, signal_info: Dict[str, Any]) -> bool:
        """發送通知"""
        try:
            logger.info(f"📧 狙擊手通知: {signal_info.get('symbol', 'UNKNOWN')}")
            return True
        except Exception as e:
            logger.error(f"❌ 狙擊手通知失敗: {e}")
            return False
