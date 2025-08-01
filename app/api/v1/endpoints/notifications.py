from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
import os
from datetime import datetime
import logging
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

class EmailNotificationRequest(BaseModel):
    strategy: Dict[str, Any]
    type: str = "sniper-signal"

class EmailStatusResponse(BaseModel):
    enabled: bool
    last_sent: Optional[str]
    configuration_status: str

@router.post("/email")
async def send_email_notification(request: EmailNotificationRequest):
    """
    🎯 狙擊手計劃 - Email 通知發送
    
    發送狙擊手策略信號的 Email 通知
    """
    try:
        # 檢查 Gmail 配置
        if not settings.GMAIL_SENDER or not settings.GMAIL_APP_PASSWORD or not settings.GMAIL_RECIPIENT:
            raise HTTPException(status_code=503, detail="Gmail 配置未完成，請檢查 .env 文件")
        
        strategy = request.strategy
        
        # 準備 Email 內容
        email_subject = f"🎯 狙擊手計劃信號 - {strategy.get('symbol', 'Unknown')} {strategy.get('signal_type', 'Signal')}"
        
        email_body = f"""
🎯 狙擊手計劃 - 高精準度交易信號

📊 交易標的: {strategy.get('symbol', 'N/A')}
📈 信號類型: {strategy.get('signal_type', 'N/A')}
💰 進場價格: ${strategy.get('entry_price', 0):.4f}
🛑 止損價格: ${strategy.get('stop_loss', 0):.4f}
🎯 止盈價格: ${strategy.get('take_profit', 0):.4f}
⭐ 信心度: {int(strategy.get('confidence', 0) * 100)}%
⏰ 時間框架: {strategy.get('timeframe', 'N/A')}

🎯 狙擊手分析:
{strategy.get('reasoning', '無分析內容')}

🔍 技術指標:
{', '.join(strategy.get('technical_indicators', []))}

⚡ 狙擊手指標:
• 市場狀態: {strategy.get('sniper_metrics', {}).get('market_regime', 'Unknown')}
• Layer 1 時間: {strategy.get('sniper_metrics', {}).get('layer_one_time', 0) * 1000:.1f}ms
• Layer 2 時間: {strategy.get('sniper_metrics', {}).get('layer_two_time', 0) * 1000:.1f}ms
• 信號通過率: {strategy.get('sniper_metrics', {}).get('pass_rate', 0) * 100:.1f}%

📅 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
🎯 狙擊手計劃自動生成
Trading X 進階交易策略系統
        """.strip()
        
        # 使用直接 SMTP 發送（已測試成功的方法）
        import smtplib
        import ssl
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # 創建郵件
        message = MIMEMultipart("alternative")
        message["Subject"] = email_subject
        message["From"] = settings.GMAIL_SENDER
        message["To"] = settings.GMAIL_RECIPIENT
        
        part = MIMEText(email_body, "plain")
        message.attach(part)
        
        # 發送郵件
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(settings.GMAIL_SENDER, settings.GMAIL_APP_PASSWORD)
            server.sendmail(settings.GMAIL_SENDER, settings.GMAIL_RECIPIENT, message.as_string())
        
        success = True
        
        if success:
            logger.info(f"📧 狙擊手 Email 通知發送成功: {strategy.get('symbol')} - {strategy.get('signal_type')}")
            return {
                "status": "success",
                "message": f"📧 狙擊手信號通知已成功發送至 {settings.GMAIL_RECIPIENT}: {strategy.get('symbol')}",
                "email_subject": email_subject,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Email 發送失敗")
        
    except Exception as e:
        logger.error(f"❌ 狙擊手 Email 通知發送失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Email 發送失敗: {str(e)}")

@router.get("/email/status", response_model=EmailStatusResponse)
async def get_email_status():
    """
    檢查 Email 通知配置狀態
    """
    try:
        # 檢查 .env 文件中的 Gmail 配置
        gmail_enabled = False
        
        if settings.GMAIL_SENDER and settings.GMAIL_APP_PASSWORD and settings.GMAIL_RECIPIENT:
            gmail_enabled = True
        
        return EmailStatusResponse(
            enabled=gmail_enabled,
            last_sent=None,  # 這裡可以從數據庫或日誌中獲取最後發送時間
            configuration_status="已配置" if gmail_enabled else "未配置"
        )
        
    except Exception as e:
        logger.error(f"❌ 檢查 Email 狀態失敗: {str(e)}")
        return EmailStatusResponse(
            enabled=False,
            last_sent=None,
            configuration_status=f"檢查失敗: {str(e)}"
        )

@router.get("/email/test")
async def test_email_notification():
    """
    測試 Email 通知功能
    """
    try:
        # 創建測試策略數據
        test_strategy = {
            "symbol": "BTCUSDT",
            "signal_type": "BUY",
            "entry_price": 45000.0,
            "stop_loss": 43000.0,
            "take_profit": 48000.0,
            "confidence": 0.85,
            "timeframe": "1h",
            "reasoning": "🎯 這是狙擊手計劃的測試信號，用於驗證 Email 通知功能是否正常運作。",
            "technical_indicators": ["🎯 狙擊手測試", "📊 RSI", "📈 MACD"],
            "sniper_metrics": {
                "market_regime": "TESTING",
                "layer_one_time": 0.012,
                "layer_two_time": 0.023,
                "pass_rate": 0.85
            }
        }
        
        # 調用發送通知
        request = EmailNotificationRequest(strategy=test_strategy, type="test-signal")
        result = await send_email_notification(request)
        
        return {
            "status": "success",
            "message": "📧 狙擊手 Email 測試通知已發送",
            "test_result": result
        }
        
    except Exception as e:
        logger.error(f"❌ Email 測試失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Email 測試失敗: {str(e)}")
