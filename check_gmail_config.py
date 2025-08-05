#!/usr/bin/env python3
"""
檢查 Gmail 設置配置
"""

import sys
sys.path.append('/Users/itts/Desktop/Trading X')

from app.core.config import settings
import os
from dotenv import load_dotenv

print("🔧 檢查 Gmail 設置配置")
print("=" * 40)

# 加載 .env 文件
load_dotenv()

print("1️⃣ 環境變數檢查:")
print(f"   GMAIL_SENDER: {os.getenv('GMAIL_SENDER', 'Not Set')}")
print(f"   GMAIL_APP_PASSWORD: {'Set' if os.getenv('GMAIL_APP_PASSWORD') else 'Not Set'}")
print(f"   GMAIL_RECIPIENT: {os.getenv('GMAIL_RECIPIENT', 'Not Set')}")

print("\n2️⃣ Settings 配置檢查:")
print(f"   settings.GMAIL_SENDER: {settings.GMAIL_SENDER}")
print(f"   settings.GMAIL_APP_PASSWORD: {'Set' if settings.GMAIL_APP_PASSWORD else 'Not Set'}")
print(f"   settings.GMAIL_RECIPIENT: {settings.GMAIL_RECIPIENT}")

print("\n3️⃣ 設置狀態:")
if settings.GMAIL_SENDER and settings.GMAIL_APP_PASSWORD:
    print("   ✅ Gmail 設置完整")
else:
    print("   ❌ Gmail 設置不完整")
    if not settings.GMAIL_SENDER:
        print("      - 缺少 GMAIL_SENDER")
    if not settings.GMAIL_APP_PASSWORD:
        print("      - 缺少 GMAIL_APP_PASSWORD")
