#!/usr/bin/env python3
"""
三個資料庫分離系統測試
"""

import asyncio
import sys
from pathlib import Path

# 添加路徑
sys.path.append(str(Path(__file__).parent))

from app.core.database_separated import SeparatedDatabaseManager

async def test_three_databases():
    print('🗄️ 測試三個資料庫分離系統...')
    print('=' * 50)
    
    db_manager = SeparatedDatabaseManager()
    
    # 測試三個資料庫連接
    print('📊 測試資料庫連接:')
    try:
        market_session = await db_manager.create_session('market_data')
        learning_session = await db_manager.create_session('learning_records')
        extreme_session = await db_manager.create_session('extreme_events')
        
        print('   ✅ market_data.db - 連接成功')
        print('   ✅ learning_records.db - 連接成功') 
        print('   ✅ extreme_events.db - 連接成功')
        
        await market_session.close()
        await learning_session.close()
        await extreme_session.close()
        
    except Exception as e:
        print(f'   ❌ 資料庫連接失敗: {e}')
        return False
    
    # 檢查資料庫檔案
    print('\n📁 檢查資料庫檔案:')
    db_dir = db_manager.db_dir
    for db_name, db_path in db_manager.databases.items():
        if db_path.exists():
            size = db_path.stat().st_size
            print(f'   ✅ {db_name}: {db_path.name} ({size} bytes)')
        else:
            print(f'   ❌ {db_name}: 檔案不存在')
    
    # 檢查引擎和會話工廠
    print('\n⚙️ 檢查系統組件:')
    for db_name in ['market_data', 'learning_records', 'extreme_events']:
        engine = db_manager.get_engine(db_name)
        factory = db_manager.get_session_factory(db_name)
        base = db_manager.get_base(db_name)
        
        print(f'   ✅ {db_name}: Engine={engine is not None}, Factory={factory is not None}, Base={base is not None}')
    
    # 測試表格創建
    print('\n🏗️ 測試表格創建:')
    try:
        await db_manager.create_all_tables()
        print('   ✅ 所有表格創建成功')
    except Exception as e:
        print(f'   ❌ 表格創建失敗: {e}')
    
    print('\n🎉 三個資料庫分離系統測試完成！')
    return True

if __name__ == "__main__":
    asyncio.run(test_three_databases())
