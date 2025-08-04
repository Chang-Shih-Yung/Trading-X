#!/usr/bin/env python3
"""
🗑️  Trading X - 全面清理測試和假資料腳本
⚠️  警告：這會清除所有測試資料和假資料！
✅ 確保系統符合「不准有假資料或測試資料」的要求
"""

import sqlite3
import asyncio
import os
import sys
from datetime import datetime

def print_warning():
    """顯示警告信息"""
    print("=" * 80)
    print("⚠️  ⚠️  ⚠️   警告：全面清理測試和假資料   ⚠️  ⚠️  ⚠️")
    print("=" * 80)
    print()
    print("📋 此腳本將執行以下清理操作：")
    print("   1. 清除所有 trading_signals 表中的測試信號")
    print("   2. 清除所有 sniper_signal_details 表中的測試數據")  
    print("   3. 清除所有 market_data 表中的模擬市場數據")
    print("   4. 清除所有 backtest_results 表中的回測結果")
    print("   5. 清除所有 risk_metrics 表中的風險指標")
    print("   6. 清除所有 strategies 表中的策略配置")
    print("   7. 清除所有 technical_indicators 表中的技術指標")
    print("   8. 清除所有 sniper_signal_summary 表中的匯總數據")
    print()
    print("🎯 目標：確保系統完全乾淨，只包含真實的交易信號和數據")
    print("📊 符合「不准有假資料或測試資料」的嚴格要求")
    print()

def cleanup_database():
    """清理資料庫中的所有測試和假資料"""
    try:
        # 連接資料庫
        conn = sqlite3.connect('tradingx.db')
        cursor = conn.cursor()
        
        print("🔍 檢查當前資料庫狀態...")
        
        # 檢查各表的資料數量
        tables_to_check = [
            'trading_signals',
            'sniper_signal_details', 
            'sniper_signal_summary',
            'market_data',
            'backtest_results',
            'risk_metrics',
            'strategies',
            'technical_indicators'
        ]
        
        before_counts = {}
        for table in tables_to_check:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                before_counts[table] = count
                print(f"   {table}: {count} 筆記錄")
            except sqlite3.Error as e:
                print(f"   {table}: 表不存在或查詢失敗 ({e})")
                before_counts[table] = 0
        
        total_before = sum(before_counts.values())
        print(f"\n📊 清理前總計：{total_before} 筆記錄")
        
        if total_before == 0:
            print("✅ 資料庫已經是乾淨的，無需清理")
            conn.close()
            return True
        
        print(f"\n🗑️  開始清理 {total_before} 筆記錄...")
        
        # 執行清理操作
        cleanup_queries = [
            "DELETE FROM trading_signals",
            "DELETE FROM sniper_signal_details", 
            "DELETE FROM sniper_signal_summary",
            "DELETE FROM market_data",
            "DELETE FROM backtest_results",
            "DELETE FROM risk_metrics", 
            "DELETE FROM strategies",
            "DELETE FROM technical_indicators"
        ]
        
        cleaned_tables = []
        for query in cleanup_queries:
            try:
                cursor.execute(query)
                table_name = query.split()[2]  # 獲取表名
                rows_affected = cursor.rowcount
                if rows_affected > 0:
                    cleaned_tables.append(f"{table_name} ({rows_affected} 筆)")
                    print(f"✅ {table_name}: 清除 {rows_affected} 筆記錄")
                else:
                    print(f"📭 {table_name}: 已經是空的")
            except sqlite3.Error as e:
                print(f"❌ 清理失敗 - {query}: {e}")
        
        # 提交變更
        conn.commit()
        
        # 驗證清理結果
        print(f"\n🔍 驗證清理結果...")
        after_counts = {}
        for table in tables_to_check:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                after_counts[table] = count
                if count == 0:
                    print(f"✅ {table}: 已清空")
                else:
                    print(f"⚠️  {table}: 仍有 {count} 筆記錄")
            except sqlite3.Error:
                after_counts[table] = 0
        
        total_after = sum(after_counts.values())
        
        conn.close()
        
        print(f"\n📊 清理結果摘要:")
        print(f"   清理前：{total_before} 筆記錄")
        print(f"   清理後：{total_after} 筆記錄")
        print(f"   已清除：{total_before - total_after} 筆記錄")
        
        if total_after == 0:
            print("✅ 資料庫完全清空 - 符合「不准有假資料或測試資料」要求")
            return True
        else:
            print(f"⚠️  資料庫仍有 {total_after} 筆記錄需要進一步檢查")
            return False
            
    except Exception as e:
        print(f"❌ 資料庫清理失敗: {e}")
        return False

def main():
    """主程式"""
    print_warning()
    
    # 確認操作
    confirm1 = input("❓ 你確定要清除所有測試和假資料嗎？(yes/no): ")
    if confirm1.lower() not in ['yes', 'y']:
        print("❌ 操作已取消")
        return
    
    confirm2 = input("❓ 再次確認：這將永久刪除所有資料，無法恢復！(yes/no): ")
    if confirm2.lower() not in ['yes', 'y']:
        print("❌ 操作已取消")
        return
    
    print("\n🚀 開始執行全面清理...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 執行資料庫清理
    if cleanup_database():
        print(f"\n🎉 清理完成！({timestamp})")
        print("✅ 資料庫現在完全乾淨，符合系統要求")
        print("📝 建議：")
        print("   1. 重啟後端服務以確保狀態同步")
        print("   2. 避免運行測試腳本除非必要")
        print("   3. 確保只有真實交易信號進入系統")
    else:
        print(f"\n⚠️  清理部分完成，請檢查剩餘資料 ({timestamp})")
        
    print("\n📊 系統現在準備接收真實的交易信號和數據")

if __name__ == "__main__":
    main()
