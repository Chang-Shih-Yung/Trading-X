#!/usr/bin/env python3
"""
Email 重試清理腳本 - Trading X
清理超過重試限制的Email信號，防止無限重試
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.models.sniper_signal_history import SniperSignalDetails, EmailStatus
from sqlalchemy import select, update, and_
from datetime import datetime

async def clean_excessive_retries():
    """清理超過重試限制的Email信號"""
    print("🧹 開始清理超過重試限制的Email信號...")
    
    try:
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        try:
            # 查詢所有超過重試限制的信號
            result = await db.execute(
                select(SniperSignalDetails).where(
                    and_(
                        SniperSignalDetails.email_retry_count >= 5,  # 超過重試限制
                        SniperSignalDetails.email_status.in_([
                            EmailStatus.PENDING, 
                            EmailStatus.FAILED, 
                            EmailStatus.RETRYING
                        ])
                    )
                )
            )
            
            excessive_signals = result.scalars().all()
            
            if not excessive_signals:
                print("✅ 沒有發現超過重試限制的信號")
                return
            
            print(f"🔍 發現 {len(excessive_signals)} 個超過重試限制的信號:")
            
            for signal in excessive_signals:
                print(f"   📧 {signal.symbol} {signal.signal_id}: 重試次數 {signal.email_retry_count}")
            
            # 將這些信號標記為徹底失敗
            await db.execute(
                update(SniperSignalDetails)
                .where(
                    and_(
                        SniperSignalDetails.email_retry_count >= 5,
                        SniperSignalDetails.email_status.in_([
                            EmailStatus.PENDING, 
                            EmailStatus.FAILED, 
                            EmailStatus.RETRYING
                        ])
                    )
                )
                .values(
                    email_status=EmailStatus.FAILED,
                    error_message=f"清理腳本: 超過最大重試次數 (5次)，停止重試",
                    updated_at=datetime.utcnow()
                )
            )
            
            await db.commit()
            
            print(f"✅ 成功清理 {len(excessive_signals)} 個超過重試限制的信號")
            print("📧 這些信號已標記為徹底失敗，不會再嘗試發送")
            
        finally:
            await db_gen.aclose()
            
    except Exception as e:
        print(f"❌ 清理過程中發生錯誤: {e}")

async def show_email_status_summary():
    """顯示Email狀態摘要"""
    print("\n📊 Email 狀態摘要:")
    print("-" * 50)
    
    try:
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        try:
            from sqlalchemy import func
            
            # 統計各種狀態的Email數量
            result = await db.execute(
                select(
                    SniperSignalDetails.email_status,
                    func.count(SniperSignalDetails.id).label('count'),
                    func.avg(SniperSignalDetails.email_retry_count).label('avg_retry')
                )
                .group_by(SniperSignalDetails.email_status)
            )
            
            status_stats = result.fetchall()
            
            total_signals = 0
            for row in status_stats:
                status = row[0]
                count = row[1]
                avg_retry = row[2] or 0
                total_signals += count
                
                status_name = {
                    EmailStatus.PENDING: "等待發送",
                    EmailStatus.SENT: "已發送",
                    EmailStatus.FAILED: "發送失敗",
                    EmailStatus.RETRYING: "重試中"
                }.get(status, str(status))
                
                print(f"   📧 {status_name}: {count} 個 (平均重試: {avg_retry:.1f} 次)")
            
            print(f"\n📈 總計: {total_signals} 個Email信號")
            
            # 檢查是否還有問題信號
            problem_result = await db.execute(
                select(func.count(SniperSignalDetails.id))
                .where(
                    and_(
                        SniperSignalDetails.email_retry_count >= 5,
                        SniperSignalDetails.email_status.in_([
                            EmailStatus.PENDING, 
                            EmailStatus.FAILED, 
                            EmailStatus.RETRYING
                        ])
                    )
                )
            )
            
            problem_count = problem_result.scalar() or 0
            
            if problem_count > 0:
                print(f"⚠️  警告: 仍有 {problem_count} 個信號超過重試限制")
            else:
                print("✅ 所有Email信號狀態正常")
                
        finally:
            await db_gen.aclose()
            
    except Exception as e:
        print(f"❌ 獲取狀態摘要失敗: {e}")

async def main():
    """主函數"""
    print("🎯 Email 重試清理工具 - Trading X")
    print("=" * 60)
    
    # 顯示當前狀態
    await show_email_status_summary()
    
    # 清理超過重試限制的信號
    await clean_excessive_retries()
    
    # 顯示清理後的狀態
    await show_email_status_summary()
    
    print("\n✅ 清理完成!")
    print("💡 提示: 修復後的Email管理器將:")
    print("   1. 只發送最早的最佳品質信號")
    print("   2. 最多重試 5 次後停止")
    print("   3. 不會重複發送已發送的信號")

if __name__ == "__main__":
    asyncio.run(main())
