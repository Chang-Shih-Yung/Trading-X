import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
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
        
        # 測試通知控制
        self.last_test_time = None
        self.test_cooldown_minutes = 10  # 測試通知冷卻時間
        
        logger.info(f"📧 Gmail通知服務初始化完成")
        logger.info(f"📧 發送者: {sender_email}")
        logger.info(f"📧 接收者: {recipient_email}")
        logger.info(f"🎯 最低信心度閾值: {self.min_confidence_threshold}")
        logger.info(f"⏰ 冷卻時間: {self.cooldown_minutes}分鐘")
    
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
                
                logger.info(f"📧 信號通知已發送: {signal.symbol} {signal.signal_type} (信心度: {signal.confidence:.3f})")
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
                logger.debug("📧 通知服務已禁用")
                return False
            
            # 檢查信心度閾值
            if signal.confidence < self.min_confidence_threshold:
                logger.debug(f"📧 信心度不足 ({signal.confidence:.3f} < {self.min_confidence_threshold})")
                return False
            
            # 生成消息簽名（防止重複發送相同內容）
            message_signature = self._generate_message_signature(signal)
            if message_signature in self.message_signatures:
                logger.debug(f"📧 重複消息，跳過發送: {signal.symbol} {signal.signal_type}")
                return False
            
            # 檢查冷卻時間
            key = f"{signal.symbol}_{signal.timeframe}"
            if key in self.last_notifications:
                last_time = self.last_notifications[key]
                time_diff = (datetime.now() - last_time).total_seconds() / 60
                if time_diff < self.cooldown_minutes:
                    logger.debug(f"📧 冷卻時間未到 ({time_diff:.1f}/{self.cooldown_minutes}分鐘)")
                    return False
            
            # 注意：不在這裡添加簽名，等發送成功後再添加
            return True
            
        except Exception as e:
            logger.error(f"❌ 檢查通知條件時發生錯誤: {e}")
            return False
    
    def _generate_message_signature(self, signal) -> str:
        """生成消息簽名用於防重複"""
        try:
            # 基於關鍵信息生成唯一簽名
            signature_data = f"{signal.symbol}_{signal.signal_type}_{signal.confidence:.3f}_{signal.entry_price:.6f}_{signal.timeframe}"
            return signature_data
        except Exception:
            # 備用簽名
            return f"{signal.symbol}_{signal.signal_type}_{datetime.now().strftime('%Y%m%d%H%M')}"
    
    def _create_signal_email(self, signal) -> MIMEMultipart:
        """創建交易信號郵件"""
        try:
            # 創建郵件對象
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = self.recipient_email
            
            # 根據信號類型設定主題
            urgency_emoji = {
                "critical": "🚨🚨🚨",
                "high": "🔥🔥",
                "medium": "⚡",
                "low": "📊"
            }
            
            signal_emoji = {
                "BUY": "📈🟢",
                "STRONG_BUY": "🚀🟢",
                "SELL": "📉🔴", 
                "STRONG_SELL": "⬇️🔴",
                "HOLD": "⏸️🟡"
            }
            
            urgency_icon = urgency_emoji.get(signal.urgency, "📊")
            signal_icon = signal_emoji.get(signal.signal_type, "📊")
            
            subject = f"{urgency_icon} Trading-X 交易信號 {signal_icon} {signal.symbol} {signal.signal_type}"
            message["Subject"] = subject
            
            # 創建郵件內容
            html_body = self._create_html_email_body(signal)
            text_body = self._create_text_email_body(signal)
            
            # 添加郵件內容
            message.attach(MIMEText(text_body, "plain", "utf-8"))
            message.attach(MIMEText(html_body, "html", "utf-8"))
            
            return message
            
        except Exception as e:
            logger.error(f"❌ 創建郵件時發生錯誤: {e}")
            raise
    
    def _create_html_email_body(self, signal) -> str:
        """創建HTML格式的郵件內容"""
        
        # 根據信號類型選擇顏色
        signal_colors = {
            "BUY": "#28a745",
            "STRONG_BUY": "#20c997", 
            "SELL": "#dc3545",
            "STRONG_SELL": "#fd7e14",
            "HOLD": "#ffc107"
        }
        
        signal_color = signal_colors.get(signal.signal_type, "#6c757d")
        
        # 根據緊急度選擇背景色
        urgency_colors = {
            "critical": "#fff5f5",
            "high": "#fff8f1", 
            "medium": "#f8f9ff",
            "low": "#f8f9fa"
        }
        
        bg_color = urgency_colors.get(signal.urgency, "#f8f9fa")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: {bg_color}; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, {signal_color}, {signal_color}dd); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ padding: 20px; }}
                .signal-box {{ background: {signal_color}15; border-left: 4px solid {signal_color}; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .price-info {{ display: flex; justify-content: space-between; margin: 15px 0; }}
                .price-item {{ text-align: center; padding: 10px; background: #f8f9fa; border-radius: 5px; flex: 1; margin: 0 5px; }}
                .confidence {{ font-size: 18px; font-weight: bold; color: {signal_color}; }}
                .timestamp {{ color: #6c757d; font-size: 12px; }}
                .footer {{ background: #f8f9fa; padding: 15px; text-align: center; border-radius: 0 0 10px 10px; color: #6c757d; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Trading-X 交易信號通知</h1>
                    <p style="margin:0;">{signal.symbol} - {signal.timeframe} 時間框架</p>
                </div>
                
                <div class="content">
                    <div class="signal-box">
                        <h2 style="color: {signal_color}; margin-top: 0;">
                            {signal.signal_type} 信號
                        </h2>
                        <p><strong>信心度:</strong> <span class="confidence">{signal.confidence:.1%}</span></p>
                        <p><strong>緊急程度:</strong> {signal.urgency.upper()}</p>
                        <p><strong>風險回報比:</strong> 1:{signal.risk_reward_ratio:.2f}</p>
                    </div>
                    
                    <div class="price-info">
                        <div class="price-item">
                            <h4>進場價格</h4>
                            <p>${signal.entry_price:.6f}</p>
                        </div>
                        <div class="price-item">
                            <h4>止損價格</h4>
                            <p>${signal.stop_loss:.6f}</p>
                        </div>
                        <div class="price-item">
                            <h4>止盈價格</h4>
                            <p>${signal.take_profit:.6f}</p>
                        </div>
                    </div>
                    
                    <div style="margin: 20px 0;">
                        <h4>使用指標:</h4>
                        <p>{', '.join(signal.indicators_used) if signal.indicators_used else '無'}</p>
                    </div>
                    
                    <div style="margin: 20px 0;">
                        <h4>分析原因:</h4>
                        <p>{signal.reasoning}</p>
                    </div>
                    
                    <div class="timestamp">
                        信號生成時間: {signal.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
                    </div>
                </div>
                
                <div class="footer">
                    <p>🤖 此信號由 Trading-X AI混合決策系統自動生成</p>
                    <p>⚠️ 投資有風險，請謹慎決策</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_text_email_body(self, signal) -> str:
        """創建純文字格式的郵件內容"""
        
        text = f"""
🚀 Trading-X 交易信號通知
════════════════════════

交易對: {signal.symbol}
時間框架: {signal.timeframe}
信號類型: {signal.signal_type}
信心度: {signal.confidence:.1%}
緊急程度: {signal.urgency.upper()}

💰 價格資訊:
─────────────
進場價格: ${signal.entry_price:.6f}
止損價格: ${signal.stop_loss:.6f}
止盈價格: ${signal.take_profit:.6f}
風險回報比: 1:{signal.risk_reward_ratio:.2f}

📊 技術指標:
─────────────
{', '.join(signal.indicators_used) if signal.indicators_used else '無'}

🔍 分析原因:
─────────────
{signal.reasoning}

⏰ 信號時間: {signal.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

═══════════════════════════════════════
🤖 此信號由 Trading-X AI混合決策系統自動生成
⚠️  投資有風險，請謹慎決策
═══════════════════════════════════════
        """
        
        return text.strip()
    
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
            # 更新最後通知時間
            key = f"{signal.symbol}_{signal.timeframe}"
            self.last_notifications[key] = datetime.now()
            
            # 添加到歷史記錄
            notification_record = {
                'timestamp': datetime.now(),
                'symbol': signal.symbol,
                'signal_type': signal.signal_type,
                'confidence': signal.confidence,
                'urgency': signal.urgency
            }
            
            self.notification_history.append(notification_record)
            
            # 保持歷史記錄大小
            if len(self.notification_history) > self.max_history:
                self.notification_history = self.notification_history[-self.max_history:]
                
        except Exception as e:
            logger.error(f"❌ 記錄通知歷史失敗: {e}")
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """獲取通知統計信息"""
        try:
            total_notifications = len(self.notification_history)
            
            if total_notifications == 0:
                return {
                    'total_notifications': 0,
                    'enabled': self.enabled,
                    'recent_notifications': []
                }
            
            # 按信號類型統計
            signal_types = {}
            for record in self.notification_history:
                signal_type = record['signal_type']
                signal_types[signal_type] = signal_types.get(signal_type, 0) + 1
            
            # 最近的通知
            recent_notifications = self.notification_history[-10:]
            
            return {
                'total_notifications': total_notifications,
                'enabled': self.enabled,
                'signal_types': signal_types,
                'recent_notifications': [
                    {
                        'timestamp': record['timestamp'].isoformat(),
                        'symbol': record['symbol'],
                        'signal_type': record['signal_type'],
                        'confidence': record['confidence']
                    }
                    for record in recent_notifications
                ],
                'min_confidence_threshold': self.min_confidence_threshold,
                'cooldown_minutes': self.cooldown_minutes
            }
            
        except Exception as e:
            logger.error(f"❌ 獲取通知統計失敗: {e}")
            return {'error': str(e)}
    
    def enable_notifications(self):
        """啟用通知"""
        self.enabled = True
        logger.info("📧 Gmail通知已啟用")
    
    def disable_notifications(self):
        """禁用通知"""
        self.enabled = False
        logger.info("📧 Gmail通知已禁用")
    
    def update_settings(self, 
                       min_confidence: Optional[float] = None,
                       cooldown_minutes: Optional[int] = None):
        """更新通知設定"""
        if min_confidence is not None:
            self.min_confidence_threshold = min_confidence
            logger.info(f"📧 最低信心度閾值更新為: {min_confidence}")
        
        if cooldown_minutes is not None:
            self.cooldown_minutes = cooldown_minutes
            logger.info(f"📧 冷卻時間更新為: {cooldown_minutes}分鐘")

    async def test_notification(self) -> bool:
        """發送測試通知"""
        try:
            # 檢查測試通知冷卻時間
            if hasattr(self, 'last_test_notification'):
                time_diff = (datetime.now() - self.last_test_notification).total_seconds() / 60
                if time_diff < self.test_cooldown_minutes:
                    logger.debug(f"📧 測試通知冷卻時間未到 ({time_diff:.1f}/{self.test_cooldown_minutes}分鐘)")
                    return False
            
            # 創建測試消息
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = self.recipient_email
            message["Subject"] = "🧪 Trading-X Gmail通知測試"
            
            test_body = f"""
🧪 Trading-X Gmail通知測試

這是一封測試郵件，用於驗證Gmail通知功能是否正常工作。

配置信息:
- 發送者: {self.sender_email}
- 接收者: {self.recipient_email}
- 通知狀態: {'啟用' if self.enabled else '禁用'}
- 最低信心度: {self.min_confidence_threshold}
- 冷卻時間: {self.cooldown_minutes}分鐘

測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

如果您收到此郵件，說明Gmail通知功能配置正確！

🤖 Trading-X 自動交易系統
            """
            
            message.attach(MIMEText(test_body, "plain", "utf-8"))
            
            # 發送測試郵件
            success = await self._send_email(message)
            
            if success:
                # 記錄測試通知時間
                self.last_test_notification = datetime.now()
                logger.info("✅ 測試通知發送成功")
            else:
                logger.error("❌ 測試通知發送失敗")
                
            return success
            
        except Exception as e:
            logger.error(f"❌ 發送測試通知時發生錯誤: {e}")
            return False

    async def send_sniper_signal_notification_async(self, signal_info: Dict[str, Any]) -> bool:
        """
        🎯 方案C：狙擊手專用信號通知（優化版Email模板）
        
        Args:
            signal_info: 包含信號詳細信息的字典
            
        Returns:
            bool: 是否成功發送
        """
        try:
            if not self.enabled:
                logger.debug("Gmail通知功能已禁用")
                return False
            
            # 建立郵件對象
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = self.recipient_email
            
            # 🎯 方案C：根據優先級設定郵件標題
            priority = signal_info.get('priority', 'MEDIUM')
            symbol = signal_info.get('symbol', 'UNKNOWN')
            signal_type = signal_info.get('signal_type', 'UNKNOWN')
            update_type = signal_info.get('update_type', 'REGULAR')
            
            # 分級Email標題
            email_subjects = {
                'CRITICAL': f"🚨 緊急狙擊信號 - {symbol} {signal_type}",
                'HIGH': f"🎯 高品質信號 - {symbol} {signal_type}", 
                'MEDIUM': f"📊 標準信號 - {symbol} {signal_type}",
                'LOW': f"📈 一般信號 - {symbol} {signal_type}"
            }
            
            message["Subject"] = email_subjects.get(priority, f"🎯 狙擊手信號 - {symbol} {signal_type}")
            
            # 🎯 方案C：優化的Email內容模板
            entry_price = signal_info.get('entry_price', 0)
            stop_loss = signal_info.get('stop_loss', 0) 
            take_profit = signal_info.get('take_profit', 0)
            quality_score = signal_info.get('quality_score', 0)
            confidence = signal_info.get('confidence', 0)
            risk_reward_ratio = signal_info.get('risk_reward_ratio', 'N/A')
            reasoning = signal_info.get('reasoning', '技術分析指標匯聚')
            
            # 計算風險收益百分比
            if signal_type == "BUY":
                risk_pct = abs((entry_price - stop_loss) / entry_price * 100)
                reward_pct = abs((take_profit - entry_price) / entry_price * 100)
            else:  # SELL
                risk_pct = abs((stop_loss - entry_price) / entry_price * 100)
                reward_pct = abs((entry_price - take_profit) / entry_price * 100)
            
            # 優先級標籤
            priority_labels = {
                'CRITICAL': '🚨 緊急信號',
                'HIGH': '🎯 高品質',
                'MEDIUM': '📊 標準',
                'LOW': '📈 一般'
            }
            
            # 更新類型標籤
            update_labels = {
                'EMERGENCY': '⚡ 緊急觸發',
                'REGULAR': '📊 定期更新'
            }
            
            email_body = f"""
🎯 Trading-X 狙擊手系統信號通知

═══════════════════════════════════════
📊 信號概要
═══════════════════════════════════════
交易對: {symbol}
方向: {"📈 做多" if signal_type == "BUY" else "📉 做空"}
優先級: {priority_labels.get(priority, priority)}
觸發: {update_labels.get(update_type, update_type)}

═══════════════════════════════════════
💰 交易設定
═══════════════════════════════════════
進場價格: ${entry_price:,.4f}
止損價格: ${stop_loss:,.4f} (-{risk_pct:.2f}%)
止盈價格: ${take_profit:,.4f} (+{reward_pct:.2f}%)
風險報酬比: 1:{risk_reward_ratio}

═══════════════════════════════════════
📊 信號品質
═══════════════════════════════════════
品質分數: {quality_score:.2f}/10.0 {'🟢' if quality_score >= 7 else '🟡' if quality_score >= 5 else '🔴'}
信心度: {confidence:.1%} {'🔥' if confidence >= 0.5 else '⚡' if confidence >= 0.3 else '📊'}
分析理由: {reasoning}

═══════════════════════════════════════
⏰ 時間資訊
═══════════════════════════════════════
信號時間: {signal_info.get('created_at', 'N/A')}
更新類型: {update_type}

═══════════════════════════════════════
💡 操作建議
═══════════════════════════════════════
{"🚨 這是緊急信號，建議立即關注市場動向！" if priority == 'CRITICAL' else ""}
{"🎯 高品質信號，建議重點關注此交易機會。" if priority == 'HIGH' else ""}
{"📊 標準信號，可考慮適度倉位參與。" if priority == 'MEDIUM' else ""}
{"📈 一般信號，僅供參考，謹慎評估。" if priority == 'LOW' else ""}

⚠️ 風險提醒: 任何投資都有風險，請謹慎評估並控制倉位。

🤖 Trading-X 狙擊手系統 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            message.attach(MIMEText(email_body, "plain", "utf-8"))
            
            # 發送郵件
            success = await self._send_email(message)
            
            if success:
                logger.info(f"✅ 狙擊手信號Email發送成功: {symbol} {signal_type} (優先級: {priority})")
                return True
            else:
                logger.error(f"❌ 狙擊手信號Email發送失敗: {symbol}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 狙擊手信號通知發送錯誤: {e}")
            import traceback
            traceback.print_exc()
            return False
