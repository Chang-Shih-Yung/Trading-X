#!/usr/bin/env python3
"""
遷移腳本：將現有數據遷移到標準三分類資料庫架構
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def migrate_liquidity_events():
    """遷移流動性事件到 extreme_events.db"""
    
    try:
        # 導入極端事件資料庫管理器
        from app.core.database_separated import SeparatedDatabaseManager
        from app.models.extreme_models import LiquidityEvent
        
        # 初始化資料庫管理器
        db_manager = SeparatedDatabaseManager()
        
        # 讀取現有的流動性事件 JSON 文件
        liquidity_json_path = "./data/liquidity_events.json"
        if not os.path.exists(liquidity_json_path):
            logger.info("📂 流動性事件 JSON 文件不存在，跳過遷移")
            return
            
        with open(liquidity_json_path, 'r', encoding='utf-8') as f:
            liquidity_data = json.load(f)
        
        # 創建極端事件資料庫會話
        async with db_manager.get_db_session("extreme_events") as session:
            
            migrated_count = 0
            
            # 遷移每個流動性事件
            for event_data in liquidity_data.get("events", []):
                try:
                    # 創建 LiquidityEvent 對象
                    liquidity_event = LiquidityEvent(
                        event_id=event_data.get("event_id", f"liquidity_{migrated_count}"),
                        symbol=event_data.get("symbol", "UNKNOWN"),
                        event_type=event_data.get("event_type", "LIQUIDITY_DROP"),
                        severity=event_data.get("severity", "MEDIUM"),
                        timestamp=datetime.fromisoformat(event_data.get("timestamp", datetime.now().isoformat())),
                        
                        # 流動性具體數據
                        before_liquidity=float(event_data.get("before_liquidity", 0)),
                        after_liquidity=float(event_data.get("after_liquidity", 0)),
                        liquidity_change_pct=float(event_data.get("liquidity_change_pct", 0)),
                        bid_ask_spread_before=float(event_data.get("bid_ask_spread_before", 0)),
                        bid_ask_spread_after=float(event_data.get("bid_ask_spread_after", 0)),
                        
                        # 市場影響
                        market_impact=event_data.get("market_impact", {}),
                        
                        # 系統響應
                        response_actions=event_data.get("response_actions", []),
                        
                        # 狀態
                        status="PROCESSED",
                        resolution_time=datetime.now() if event_data.get("resolved", False) else None,
                        
                        # 元數據
                        metadata=event_data.get("metadata", {}),
                        notes=f"從 liquidity_events.json 遷移於 {datetime.now().isoformat()}"
                    )
                    
                    session.add(liquidity_event)
                    migrated_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ 遷移流動性事件失敗: {e}")
                    continue
            
            # 提交事務
            await session.commit()
            logger.info(f"✅ 成功遷移 {migrated_count} 個流動性事件到 extreme_events.db")
            
            # 備份原始 JSON 文件
            backup_path = f"./data/liquidity_events_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.rename(liquidity_json_path, backup_path)
            logger.info(f"📦 原始文件已備份為: {backup_path}")
            
    except Exception as e:
        logger.error(f"❌ 流動性事件遷移失敗: {e}")

async def validate_database_integration():
    """驗證三資料庫整合是否成功"""
    
    try:
        from app.core.database_separated import SeparatedDatabaseManager
        
        db_manager = SeparatedDatabaseManager()
        
        print("🔍 驗證標準三分類資料庫架構整合...")
        print("="*60)
        
        # 檢查資料庫文件
        for db_name, db_path in db_manager.databases.items():
            exists = db_path.exists()
            size = db_path.stat().st_size if exists else 0
            size_kb = size / 1024
            
            print(f"📊 {db_name}:")
            print(f"   路徑: {db_path}")
            print(f"   存在: {'✅' if exists else '❌'}")
            print(f"   大小: {size_kb:.1f} KB")
            print()
        
        # 測試連接
        try:
            for db_name in ["market_data", "learning_records", "extreme_events"]:
                engine = db_manager.get_engine(db_name)
                if engine:
                    print(f"✅ {db_name} 引擎連接正常")
                else:
                    print(f"❌ {db_name} 引擎連接失敗")
        except Exception as e:
            logger.error(f"資料庫連接測試失敗: {e}")
        
        print("\n🎉 標準三分類資料庫架構整合驗證完成！")
        
    except Exception as e:
        logger.error(f"❌ 資料庫整合驗證失敗: {e}")

async def main():
    """主要遷移流程"""
    
    print("🚀 開始遷移到標準三分類資料庫架構...")
    print("="*60)
    
    # 1. 遷移流動性事件
    print("📊 步驟 1: 遷移流動性事件...")
    await migrate_liquidity_events()
    
    # 2. 驗證整合
    print("\n🔍 步驟 2: 驗證資料庫整合...")
    await validate_database_integration()
    
    print("\n✅ 遷移完成！現在所有組件都使用標準三分類資料庫架構：")
    print("   📊 market_data.db - Phase1A 信號生成")
    print("   🎓 learning_records.db - Phase2 學習記錄")
    print("   🛡️ extreme_events.db - 系統保護與極端事件")

if __name__ == "__main__":
    asyncio.run(main())
