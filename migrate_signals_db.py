#!/usr/bin/env python3
"""
signals.db 遷移腳本
將 signals.db 從子目錄遷移到統一的 X/databases/ 目錄
"""

import os
import shutil
import sqlite3
from pathlib import Path
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate_signals_database():
    """遷移 signals.db 到統一目錄"""
    
    # 確定路徑
    script_dir = Path(__file__).parent
    x_dir = script_dir / "X"
    
    # 舊位置
    old_db_path = x_dir / "backend" / "phase2_adaptive_learning" / "storage" / "signals.db"
    
    # 新位置
    new_db_dir = x_dir / "databases"
    new_db_path = new_db_dir / "signals.db"
    
    print(f"🔄 開始遷移 signals.db")
    print(f"📂 舊位置: {old_db_path}")
    print(f"📂 新位置: {new_db_path}")
    
    # 確保新目錄存在
    new_db_dir.mkdir(exist_ok=True)
    
    # 檢查舊檔案是否存在
    if old_db_path.exists():
        try:
            # 檢查舊資料庫的內容
            conn = sqlite3.connect(str(old_db_path))
            cursor = conn.cursor()
            
            # 檢查表格和記錄數量
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            total_records = 0
            print(f"📊 舊資料庫內容:")
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                total_records += count
                print(f"   📋 {table_name}: {count} 筆記錄")
            
            conn.close()
            
            # 如果新位置已經有檔案，詢問是否覆蓋
            if new_db_path.exists():
                print(f"⚠️  新位置已存在 signals.db")
                
                # 檢查新檔案內容
                new_conn = sqlite3.connect(str(new_db_path))
                new_cursor = new_conn.cursor()
                new_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                new_tables = new_cursor.fetchall()
                
                new_total_records = 0
                print(f"📊 新位置資料庫內容:")
                for table in new_tables:
                    table_name = table[0]
                    new_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = new_cursor.fetchone()[0]
                    new_total_records += count
                    print(f"   📋 {table_name}: {count} 筆記錄")
                
                new_conn.close()
                
                if total_records > new_total_records:
                    print(f"🔄 舊檔案有更多數據 ({total_records} vs {new_total_records})，執行遷移...")
                    backup_path = new_db_path.with_suffix('.db.backup')
                    shutil.copy2(str(new_db_path), str(backup_path))
                    print(f"📦 已備份現有檔案到: {backup_path}")
                    
                    # 複製舊檔案到新位置
                    shutil.copy2(str(old_db_path), str(new_db_path))
                    print(f"✅ 成功遷移 signals.db ({total_records} 筆記錄)")
                else:
                    print(f"ℹ️  新位置的資料已是最新，跳過遷移")
            else:
                # 直接複製
                shutil.copy2(str(old_db_path), str(new_db_path))
                print(f"✅ 成功遷移 signals.db ({total_records} 筆記錄)")
            
            # 驗證新檔案
            if new_db_path.exists():
                # 測試新檔案是否可以正常打開
                test_conn = sqlite3.connect(str(new_db_path))
                test_cursor = test_conn.cursor()
                test_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                test_tables = test_cursor.fetchall()
                test_conn.close()
                
                print(f"✅ 新位置檔案驗證成功，包含 {len(test_tables)} 個表格")
                
                # 備份舊檔案而不是刪除
                backup_old_path = old_db_path.with_suffix('.db.old')
                shutil.move(str(old_db_path), str(backup_old_path))
                print(f"📦 舊檔案已備份為: {backup_old_path}")
            
        except Exception as e:
            logger.error(f"❌ 遷移過程發生錯誤: {e}")
            return False
    else:
        print(f"ℹ️  舊位置找不到 signals.db，可能已經遷移過了")
    
    # 更新 database_separated.py 以包含 signals.db
    update_database_separated_config()
    
    print(f"🎉 signals.db 遷移完成！")
    return True

def update_database_separated_config():
    """更新 database_separated.py 配置以包含 signals.db"""
    
    config_file = Path(__file__).parent / "X" / "app" / "core" / "database_separated.py"
    
    if config_file.exists():
        try:
            # 讀取檔案內容
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 檢查是否已經包含 signals.db
            if '"signals"' not in content:
                # 找到 databases 字典定義的位置
                if 'self.databases = {' in content:
                    # 在 extreme_events 後添加 signals
                    old_pattern = '''        self.databases = {
            "market_data": self.db_dir / "market_data.db",
            "learning_records": self.db_dir / "learning_records.db", 
            "extreme_events": self.db_dir / "extreme_events.db"
        }'''
                    
                    new_pattern = '''        self.databases = {
            "market_data": self.db_dir / "market_data.db",
            "learning_records": self.db_dir / "learning_records.db", 
            "extreme_events": self.db_dir / "extreme_events.db",
            "signals": self.db_dir / "signals.db"
        }'''
                    
                    if old_pattern in content:
                        content = content.replace(old_pattern, new_pattern)
                        
                        # 寫回檔案
                        with open(config_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        print(f"✅ 已更新 database_separated.py 配置")
                    else:
                        print(f"⚠️  無法自動更新 database_separated.py，請手動添加 signals.db")
                else:
                    print(f"⚠️  無法找到 databases 配置，請手動更新 database_separated.py")
            else:
                print(f"ℹ️  database_separated.py 已包含 signals 配置")
                
        except Exception as e:
            logger.error(f"❌ 更新配置檔案時發生錯誤: {e}")

def verify_migration():
    """驗證遷移結果"""
    
    script_dir = Path(__file__).parent
    x_dir = script_dir / "X"
    
    # 檢查新位置的檔案
    new_db_path = x_dir / "databases" / "signals.db"
    
    if new_db_path.exists():
        print(f"✅ 驗證: signals.db 已存在於 {new_db_path}")
        
        # 測試資料庫連接
        try:
            conn = sqlite3.connect(str(new_db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print(f"📊 資料庫包含 {len(tables)} 個表格:")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"   📋 {table[0]}: {count} 筆記錄")
            
            conn.close()
            print(f"✅ 資料庫連接測試成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 資料庫連接測試失敗: {e}")
            return False
    else:
        print(f"❌ 驗證失敗: 找不到 {new_db_path}")
        return False

if __name__ == "__main__":
    print(f"🚀 開始 signals.db 遷移程序")
    print(f"=" * 50)
    
    success = migrate_signals_database()
    
    if success:
        print(f"=" * 50)
        print(f"🔍 執行遷移驗證...")
        verify_migration()
    
    print(f"=" * 50)
    print(f"📋 遷移完成摘要:")
    print(f"   📂 新位置: X/databases/signals.db")
    print(f"   🔧 配置: signal_database.py 已更新")
    print(f"   📊 統一管理: 所有資料庫現在都在 X/databases/ 下")
