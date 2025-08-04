#!/usr/bin/env python3
"""
檢查當前信號的動態時間分布和前端顯示
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, text
from app.models.sniper_signal_history import SniperSignalDetails
import logging

# 設置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

async def analyze_dynamic_times():
    """分析當前信號的動態時間分布"""
    
    # 創建數據庫連接
    DATABASE_URL = "sqlite+aiosqlite:///./trading_x.db"
    engine = create_async_engine(DATABASE_URL)
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    print("📊 分析當前信號的動態時間分布...")
    print("=" * 100)
    
    async with AsyncSessionLocal() as session:
        # 獲取最新的20個信號
        recent_signals = await session.execute(
            select(SniperSignalDetails)
            .where(SniperSignalDetails.created_at >= text("datetime('now', '-2 hours')"))
            .order_by(SniperSignalDetails.created_at.desc())
            .limit(20)
        )
        
        signals = recent_signals.scalars().all()
        
        if not signals:
            print("❌ 沒有找到最近的信號")
            return
        
        print(f"🎯 找到 {len(signals)} 個最近信號:")
        print()
        
        # 按動態時間分組統計
        time_distribution = {}
        
        for i, signal in enumerate(signals, 1):
            time_diff = signal.expires_at - signal.created_at
            actual_hours = time_diff.total_seconds() / 3600
            
            # 四捨五入到最近的小時
            rounded_hours = round(actual_hours)
            
            if rounded_hours not in time_distribution:
                time_distribution[rounded_hours] = []
            time_distribution[rounded_hours].append(signal)
            
            print(f"🔍 信號 {i}: {signal.symbol}")
            print(f"   時間框架: {signal.timeframe.value if signal.timeframe else 'N/A'}")
            print(f"   信號品質: {signal.signal_quality.value if signal.signal_quality else 'N/A'}")
            print(f"   設定時長: {signal.expiry_hours:.1f}小時")
            print(f"   實際時長: {actual_hours:.1f}小時")
            print(f"   創建時間: {signal.created_at}")
            print(f"   過期時間: {signal.expires_at}")
            
            # 判斷是否為動態時間
            if abs(actual_hours - 24.0) > 0.5:  # 不是接近24小時
                print(f"   ✅ 動態時間計算生效")
            else:
                print(f"   ⚠️  可能仍是固定24小時")
            print()
        
        print("\n📈 動態時間分布統計:")
        print("=" * 60)
        for hours in sorted(time_distribution.keys()):
            count = len(time_distribution[hours])
            symbols = [s.symbol for s in time_distribution[hours][:3]]  # 顯示前3個
            print(f"🕐 {hours}小時: {count}個信號 ({', '.join(symbols)}{'...' if count > 3 else ''})")
        
        # 檢查是否有真正的動態時間變化
        unique_hours = set(time_distribution.keys())
        if len(unique_hours) == 1 and 24 in unique_hours:
            print("\n⚠️  所有信號都使用24小時，動態時間計算可能未生效")
        elif len(unique_hours) == 1 and 21 in unique_hours:
            print("\n📊 所有信號都使用21小時，動態時間計算部分生效")
        else:
            print(f"\n✅ 發現 {len(unique_hours)} 種不同的動態時間，系統正常工作")

async def check_frontend_display():
    """檢查前端如何顯示時間信息"""
    
    print("\n🖥️  檢查前端時間顯示...")
    print("=" * 100)
    
    # 檢查前端相關文件
    frontend_files = [
        "static/js/sniper_signals.js",
        "static/sniper_signals.html", 
        "templates/sniper_signals.html",
        "app/api/v1/endpoints/scalping_precision.py"
    ]
    
    print("📂 需要檢查的前端文件:")
    for file in frontend_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} (不存在)")

if __name__ == "__main__":
    asyncio.run(analyze_dynamic_times())
    asyncio.run(check_frontend_display())
