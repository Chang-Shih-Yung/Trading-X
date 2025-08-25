#!/usr/bin/env python3
"""
🗄️ Enhanced Signal Database - Priority 3 Support
增強版信號資料庫 - 支援優先級3時間框架感知

功能特色：
- 支援時間框架增強信號存儲
- 三維學習權重追蹤（時間衰減 × 幣種 × 時間框架）
- 跨時間框架查詢和分析
- 產品級數據完整性保證
"""

import asyncio
import aiosqlite
import json
import os
import tempfile
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import logging

# 導入優先級3增強信號
try:
    from ..priority3_timeframe_learning.timeframe_enhanced_signal import (
        TimeFrameEnhancedSignal, TimeFrameConsensus
    )
    ENHANCED_SIGNAL_AVAILABLE = True
except ImportError:
    ENHANCED_SIGNAL_AVAILABLE = False
    TimeFrameEnhancedSignal = None
    TimeFrameConsensus = None

logger = logging.getLogger(__name__)

class SignalStatus(Enum):
    """信號狀態枚舉"""
    PENDING = "PENDING"          # 等待
    EXECUTED = "EXECUTED"        # 已執行
    SUCCESS = "SUCCESS"          # 成功
    FAILED = "FAILED"            # 失敗
    CANCELLED = "CANCELLED"      # 取消

class EnhancedSignalDatabase:
    """增強版信號資料庫 - 支援優先級3"""
    
    def __init__(self, db_path: Optional[str] = None):
        """初始化增強版信號資料庫"""
        if db_path is None:
            # 🔧 修復：使用檔案相對路徑，避免硬編碼
            current_file_dir = os.path.dirname(os.path.abspath(__file__))
            # 從當前檔案路徑推導出專案根目錄
            # enhanced_signal_database.py 位於 X/backend/phase2_adaptive_learning/priority3_timeframe_learning/
            # 需要回到 X/ 目錄
            x_dir = os.path.join(current_file_dir, "..", "..", "..", "..")
            x_dir = os.path.normpath(x_dir)  # 正規化路徑
            
            # 確保 databases 目錄在 X/ 下
            databases_dir = os.path.join(x_dir, "X", "databases")
            project_db_path = os.path.join(databases_dir, "learning_records.db")
            
            # 檢查標準資料庫路徑是否存在和可寫
            try:
                # 確保目錄存在
                os.makedirs(databases_dir, exist_ok=True)
                
                # 測試寫入權限
                test_file = project_db_path + ".test"
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                
                db_path = project_db_path
                logger.info(f"✅ 使用學習記錄資料庫: {db_path}")
            except (OSError, PermissionError) as e:
                # 如果標準路徑不可用，使用臨時目錄
                logger.warning(f"⚠️ 標準資料庫路徑不可用: {e}")
                import tempfile
                db_path = os.path.join(tempfile.gettempdir(), "learning_records.db")
        
        self.db_path = str(db_path)
        self.connection: Optional[aiosqlite.Connection] = None
        
        logger.info(f"🗄️ 初始化增強版信號資料庫: {self.db_path}")
        
        if not ENHANCED_SIGNAL_AVAILABLE:
            logger.error("❌ 優先級3增強信號模組不可用")
            raise ImportError("無法導入TimeFrameEnhancedSignal")
    
    def _safe_json_serialize(self, obj):
        """
        安全的 JSON 序列化，處理 SignalType 和其他特殊對象
        """
        def convert_obj(item):
            # 處理 SignalType 枚舉
            if hasattr(item, 'value'):  # 枚舉對象
                return item.value
            elif hasattr(item, '__dict__'):  # 自定義對象
                return str(item)
            return item
        
        def recursive_convert(data):
            if isinstance(data, dict):
                return {k: recursive_convert(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [recursive_convert(item) for item in data]
            elif isinstance(data, tuple):
                return [recursive_convert(item) for item in data]
            else:
                return convert_obj(data)
        
        try:
            cleaned_obj = recursive_convert(obj)
            return json.dumps(cleaned_obj)
        except Exception as e:
            logger.warning(f"JSON 序列化失敗，使用空對象: {e}")
            return json.dumps({})
    
    async def initialize(self):
        """初始化資料庫結構"""
        max_retries = 3
        retry_delay = 0.5
        
        for attempt in range(max_retries):
            try:
                # 確保資料庫檔案目錄存在
                import os
                import asyncio
                db_dir = os.path.dirname(self.db_path)
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir, mode=0o755, exist_ok=True)
                
                # 使用WAL模式和更長的超時，支持並發訪問
                self.connection = await aiosqlite.connect(
                    self.db_path,
                    timeout=10.0  # 10秒超時
                )
                
                # 設置WAL模式以支持並發讀寫
                await self.connection.execute("PRAGMA journal_mode=WAL")
                await self.connection.execute("PRAGMA synchronous=NORMAL")
                await self.connection.execute("PRAGMA cache_size=10000")
                await self.connection.execute("PRAGMA temp_store=memory")
                
                await self._create_tables()
                logger.info(f"✅ 增強版信號資料庫初始化完成 (嘗試 {attempt + 1}/{max_retries})")
                return
                
            except Exception as e:
                logger.warning(f"⚠️ 資料庫初始化失敗 (嘗試 {attempt + 1}/{max_retries}): {e}")
                
                if self.connection:
                    try:
                        await self.connection.close()
                    except:
                        pass
                    self.connection = None
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # 指數退避
                else:
                    # 最後嘗試使用備用路徑
                    try:
                        import tempfile
                        backup_path = os.path.join(tempfile.gettempdir(), f"enhanced_signals_backup_{os.getpid()}.db")
                        logger.warning(f"🔄 嘗試備用資料庫路徑: {backup_path}")
                        self.db_path = backup_path
                        self.connection = await aiosqlite.connect(self.db_path, timeout=10.0)
                        await self.connection.execute("PRAGMA journal_mode=WAL")
                        await self._create_tables()
                        logger.info("✅ 備用資料庫初始化完成")
                        return
                    except Exception as backup_error:
                        logger.error(f"❌ 備用資料庫也失敗: {backup_error}")
                        raise
    
    async def _create_tables(self):
        """創建增強版信號表結構"""
        
        if not self.connection:
            raise RuntimeError("Database connection not initialized")
        
        # 主要增強信號表
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS enhanced_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id TEXT UNIQUE NOT NULL,
                symbol TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                signal_strength REAL NOT NULL,
                timestamp TEXT NOT NULL,
                features TEXT NOT NULL,
                market_conditions TEXT NOT NULL,
                tier TEXT NOT NULL,
                
                -- 優先級1：時間衰減
                time_decay_weight REAL DEFAULT 1.0,
                hours_since_generation REAL DEFAULT 0.0,
                
                -- 優先級2：幣種分類  
                coin_category TEXT DEFAULT 'alt',
                category_weight REAL DEFAULT 1.0,
                category_risk_multiplier REAL DEFAULT 1.0,
                
                -- 優先級3：時間框架感知
                primary_timeframe TEXT DEFAULT '5m',
                timeframe_consensus TEXT DEFAULT '{}',
                cross_timeframe_weight REAL DEFAULT 1.0,
                
                -- 最終融合權重
                final_learning_weight REAL DEFAULT 1.0,
                
                -- 結果數據
                status TEXT DEFAULT 'PENDING',
                actual_outcome REAL,
                performance_score REAL,
                execution_time TEXT,
                
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 時間框架分析表
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS timeframe_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                signal_strength REAL NOT NULL,
                weight REAL NOT NULL,
                consensus_score REAL DEFAULT 0.0,
                dominant_frame TEXT,
                conflict_level REAL DEFAULT 0.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (signal_id) REFERENCES enhanced_signals (signal_id)
            )
        """)
        
        # 學習權重歷史表
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS learning_weight_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id TEXT NOT NULL,
                weight_type TEXT NOT NULL,  -- time_decay/category/timeframe/final
                weight_value REAL NOT NULL,
                calculation_details TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (signal_id) REFERENCES enhanced_signals (signal_id)
            )
        """)
        
        # 創建索引
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_symbol ON enhanced_signals(symbol)")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON enhanced_signals(timestamp)")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_category ON enhanced_signals(coin_category)")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_timeframe ON enhanced_signals(primary_timeframe)")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_final_weight ON enhanced_signals(final_learning_weight)")
        
        await self.connection.commit()
        
        # 🔧 表格創建完成後，進行資料庫版本檢查與升級
        await self._check_and_upgrade_database()
        
        logger.info("✅ 增強版信號表結構創建完成")
    
    async def store_enhanced_signal(self, signal) -> bool:
        """存儲增強版信號 - 產品級容錯"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                if not self.connection:
                    await self.initialize()
                
                # 🔧 產品級修正：信號存儲前驗證表結構
                if attempt == 0:  # 只在第一次嘗試時檢查
                    await self._validate_and_fix_table_structure()
                
                # 提取信號數據 - 🎯 產品級序列化處理
                signal_data = (
                    str(signal.signal_id),                                                # TEXT
                    str(signal.symbol),                                                   # TEXT
                    str(signal.signal_type.value if hasattr(signal.signal_type, 'value') else str(signal.signal_type)), # TEXT - 枚舉安全處理
                    float(signal.signal_strength),                                       # REAL
                    str(signal.timestamp.isoformat()),                                  # TEXT
                    self._safe_json_serialize(signal.features if hasattr(signal, 'features') else {}), # TEXT - features 安全序列化
                    self._safe_json_serialize(signal.market_conditions if hasattr(signal, 'market_conditions') else {}), # TEXT - market_conditions 安全序列化
                    str(signal.tier),                                                    # TEXT
                    
                    # 優先級1：時間衰減
                    float(getattr(signal, 'time_decay_weight', 1.0)),                   # REAL
                    float(getattr(signal, 'hours_since_generation', 0.0)),              # REAL
                    
                    # 優先級2：幣種分類
                    str(getattr(signal, 'coin_category', 'alt')),                       # TEXT
                    float(getattr(signal, 'category_weight', 1.0)),                     # REAL
                    float(getattr(signal, 'category_risk_multiplier', 1.0)),           # REAL
                    
                    # 優先級3：時間框架感知
                    str(getattr(signal, 'primary_timeframe', '5m')),                    # TEXT
                    self._safe_json_serialize(getattr(signal, 'timeframe_consensus', {})),             # TEXT - 安全序列化
                    float(getattr(signal, 'cross_timeframe_weight', 1.0)),              # REAL
                    
                    # 最終權重
                    float(getattr(signal, 'final_learning_weight', 1.0)),               # REAL
                    
                    # 結果
                    str(signal.status),                                                   # TEXT
                    float(signal.actual_outcome) if signal.actual_outcome is not None else None,  # REAL or NULL
                    float(signal.performance_score) if signal.performance_score is not None else None,  # REAL or NULL
                    str(signal.execution_time.isoformat()) if signal.execution_time else None  # TEXT or NULL
                )
                
                await self.connection.execute("""
                    INSERT OR REPLACE INTO enhanced_signals (
                        signal_id, symbol, signal_type, signal_strength, timestamp,
                        features, market_conditions, tier,
                        time_decay_weight, hours_since_generation,
                        coin_category, category_weight, category_risk_multiplier,
                        primary_timeframe, timeframe_consensus, cross_timeframe_weight,
                        final_learning_weight,
                        status, actual_outcome, performance_score, execution_time
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, signal_data)
                
                # 存儲時間框架分析數據
                await self._store_timeframe_analysis(signal)
                
                # 存儲學習權重歷史
                await self._store_weight_history(signal)
                
                await self.connection.commit()
                logger.debug(f"✅ 增強信號已存儲: {signal.signal_id}")
                return True
                
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"⚠️ 存儲增強信號失敗 (嘗試 {attempt + 1}/{max_retries}): {error_msg}")
                
                # 🔧 產品級錯誤處理：如果是表結構問題，嘗試修正
                if "has no column named" in error_msg and attempt < max_retries - 1:
                    logger.info("🔧 檢測到表結構問題，嘗試動態修正...")
                    try:
                        await self._validate_and_fix_table_structure()
                        logger.info("✅ 表結構修正完成，將重試存儲")
                        continue
                    except Exception as fix_error:
                        logger.error(f"❌ 表結構修正失敗: {fix_error}")
                
                if self.connection:
                    try:
                        await self.connection.rollback()
                    except:
                        pass
                
                if attempt < max_retries - 1:
                    import asyncio
                    await asyncio.sleep(0.1 * (attempt + 1))
                else:
                    logger.error(f"❌ 存儲增強信號最終失敗: {error_msg}")
                    return False
        
        return False
    
    async def _store_timeframe_analysis(self, signal):
        """存儲時間框架分析數據 - 產品級容錯"""
        try:
            # 🔧 產品級容錯：檢查必需屬性
            if not hasattr(signal, 'timeframe_consensus'):
                logger.debug(f"⚠️ 信號 {signal.signal_id} 缺少 timeframe_consensus 屬性，跳過時間框架分析存儲")
                return
                
            consensus = signal.timeframe_consensus
            
            # 容錯檢查：確保 consensus 有必需的屬性
            if not hasattr(consensus, 'timeframe_signals'):
                logger.debug(f"⚠️ 共識對象缺少 timeframe_signals 屬性，跳過存儲")
                return
            
            # 存儲各時間框架信號
            for timeframe, strength in consensus.timeframe_signals.items():
                await self.connection.execute("""
                    INSERT INTO timeframe_analysis (
                        signal_id, timeframe, signal_strength, weight,
                        consensus_score, dominant_frame, conflict_level
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(signal.signal_id),                     # TEXT
                    str(timeframe),                            # TEXT
                    float(strength),                           # REAL
                    float(getattr(signal, 'cross_timeframe_weight', 1.0)),      # REAL - 容錯
                    float(getattr(consensus, 'consensus_score', 0.0)),          # REAL - 容錯
                    str(getattr(consensus, 'dominant_timeframe', 'unknown')),   # TEXT - 容錯
                    float(getattr(consensus, 'conflict_level', 0.0))            # REAL - 容錯
                ))
                
        except Exception as e:
            logger.error(f"❌ 存儲時間框架分析失敗: {e}")
    
    async def _store_weight_history(self, signal):
        """存儲學習權重歷史 - 產品級容錯"""
        try:
            # 🔧 產品級容錯：安全獲取屬性值
            time_decay_weight = getattr(signal, 'time_decay_weight', 1.0)
            category_weight = getattr(signal, 'category_weight', 1.0)
            cross_timeframe_weight = getattr(signal, 'cross_timeframe_weight', 1.0)
            final_learning_weight = getattr(signal, 'final_learning_weight', 1.0)
            hours_since_generation = getattr(signal, 'hours_since_generation', 0.0)
            coin_category = getattr(signal, 'coin_category', 'unknown')
            
            # 容錯處理 timeframe_consensus
            consensus_score = 0.0
            if hasattr(signal, 'timeframe_consensus') and signal.timeframe_consensus:
                consensus_score = getattr(signal.timeframe_consensus, 'consensus_score', 0.0)
            
            weights = [
                ('time_decay', time_decay_weight, {'hours_elapsed': hours_since_generation}),
                ('category', category_weight, {'coin_category': coin_category}),
                ('timeframe', cross_timeframe_weight, {'consensus_score': consensus_score}),
                ('final', final_learning_weight, {'calculation': 'time_decay × category × timeframe'})
            ]
            
            for weight_type, weight_value, details in weights:
                await self.connection.execute("""
                    INSERT INTO learning_weight_history (
                        signal_id, weight_type, weight_value, calculation_details
                    ) VALUES (?, ?, ?, ?)
                """, (
                    str(signal.signal_id),                     # TEXT
                    str(weight_type),                          # TEXT
                    float(weight_value),                       # REAL
                    self._safe_json_serialize(details)         # TEXT - 安全序列化
                ))
                
        except Exception as e:
            logger.error(f"❌ 存儲權重歷史失敗: {e}")
    
    async def get_signals_by_timeframe(self, timeframe: str, limit: int = 100) -> List[Dict[str, Any]]:
        """按時間框架查詢信號"""
        try:
            if not self.connection:
                await self.initialize()
            
            cursor = await self.connection.execute("""
                SELECT * FROM enhanced_signals 
                WHERE primary_timeframe = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (timeframe, limit))
            
            rows = await cursor.fetchall()
            
            signals = []
            for row in rows:
                signal_dict = dict(row)
                # 解析JSON字段
                signal_dict['features'] = json.loads(signal_dict['features'])
                signal_dict['market_conditions'] = json.loads(signal_dict['market_conditions'])
                signal_dict['timeframe_consensus'] = json.loads(signal_dict['timeframe_consensus'])
                signals.append(signal_dict)
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ 按時間框架查詢失敗: {e}")
            return []
    
    async def get_signals_by_category(self, category: str, limit: int = 100) -> List[Dict[str, Any]]:
        """按幣種分類查詢信號"""
        try:
            if not self.connection:
                await self.initialize()
            
            cursor = await self.connection.execute("""
                SELECT * FROM enhanced_signals 
                WHERE coin_category = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (category, limit))
            
            rows = await cursor.fetchall()
            
            signals = []
            for row in rows:
                signal_dict = dict(row)
                signal_dict['features'] = json.loads(signal_dict['features'])
                signal_dict['market_conditions'] = json.loads(signal_dict['market_conditions'])
                signal_dict['timeframe_consensus'] = json.loads(signal_dict['timeframe_consensus'])
                signals.append(signal_dict)
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ 按分類查詢失敗: {e}")
            return []
    
    async def get_weight_analysis(self, hours: int = 24) -> Dict[str, Any]:
        """獲取權重分析報告"""
        try:
            if not self.connection:
                await self.initialize()
            
            since_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            # 平均權重統計
            cursor = await self.connection.execute("""
                SELECT 
                    AVG(time_decay_weight) as avg_time_decay,
                    AVG(category_weight) as avg_category,
                    AVG(cross_timeframe_weight) as avg_timeframe,
                    AVG(final_learning_weight) as avg_final,
                    COUNT(*) as total_signals
                FROM enhanced_signals 
                WHERE timestamp > ?
            """, (since_time,))
            
            weight_stats = dict(await cursor.fetchone())
            
            # 各分類權重分佈
            cursor = await self.connection.execute("""
                SELECT 
                    coin_category,
                    AVG(final_learning_weight) as avg_weight,
                    COUNT(*) as count
                FROM enhanced_signals 
                WHERE timestamp > ?
                GROUP BY coin_category
            """, (since_time,))
            
            category_weights = {row[0]: {'avg_weight': row[1], 'count': row[2]} 
                              for row in await cursor.fetchall()}
            
            # 各時間框架權重分佈
            cursor = await self.connection.execute("""
                SELECT 
                    primary_timeframe,
                    AVG(final_learning_weight) as avg_weight,
                    COUNT(*) as count
                FROM enhanced_signals 
                WHERE timestamp > ?
                GROUP BY primary_timeframe
            """, (since_time,))
            
            timeframe_weights = {row[0]: {'avg_weight': row[1], 'count': row[2]} 
                               for row in await cursor.fetchall()}
            
            return {
                'analysis_period_hours': hours,
                'weight_statistics': weight_stats,
                'category_distribution': category_weights,
                'timeframe_distribution': timeframe_weights,
                'analysis_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 權重分析失敗: {e}")
            return {}
    
    async def update_signal_outcome(self, signal_id: str, outcome: float, performance_score: float = None) -> bool:
        """更新信號結果"""
        try:
            if not self.connection:
                await self.initialize()
            
            await self.connection.execute("""
                UPDATE enhanced_signals 
                SET actual_outcome = ?, 
                    performance_score = ?,
                    status = 'SUCCESS',
                    execution_time = ?
                WHERE signal_id = ?
            """, (outcome, performance_score, datetime.now().isoformat(), signal_id))
            
            await self.connection.commit()
            logger.debug(f"✅ 信號結果已更新: {signal_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 更新信號結果失敗: {e}")
            return False
    
    async def close(self):
        """關閉資料庫連接"""
        if self.connection:
            await self.connection.close()
            logger.info("🗄️ 增強版信號資料庫連接已關閉")
    
    async def _check_and_upgrade_database(self):
        """檢查並升級資料庫結構"""
        try:
            # 檢查版本表是否存在
            cursor = await self.connection.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='database_version'
            """)
            table_exists = await cursor.fetchone()
            await cursor.close()
            
            if not table_exists:
                # 創建版本表
                await self.connection.execute("""
                    CREATE TABLE database_version (
                        version INTEGER PRIMARY KEY,
                        upgraded_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                await self.connection.execute("INSERT INTO database_version (version) VALUES (1)")
                logger.info("✅ 創建資料庫版本表 (版本: 1)")
            
            # 獲取當前版本
            cursor = await self.connection.execute("SELECT MAX(version) FROM database_version")
            current_version = (await cursor.fetchone())[0] or 0
            await cursor.close()
            
            # 定義最新版本
            LATEST_VERSION = 4
            
            if current_version < LATEST_VERSION:
                logger.info(f"🔄 檢測到資料庫需要升級: {current_version} → {LATEST_VERSION}")
                await self._perform_database_upgrade(current_version, LATEST_VERSION)
            else:
                logger.debug(f"✅ 資料庫版本已是最新: {current_version}")
                
            # 🔧 產品級修正：升級完成後檢查表結構
            await self._validate_and_fix_table_structure()
                
        except Exception as e:
            logger.error(f"❌ 資料庫版本檢查失敗: {e}")
            raise
    
    async def _validate_and_fix_table_structure(self):
        """驗證並修正表結構 - 產品級修正"""
        try:
            # 檢查 enhanced_signals 表是否存在
            cursor = await self.connection.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='enhanced_signals'
            """)
            table_exists = await cursor.fetchone()
            await cursor.close()
            
            if not table_exists:
                logger.info("🔧 enhanced_signals 表不存在，將在 _create_tables 中創建")
                return
            
            # 檢查表結構
            cursor = await self.connection.execute("PRAGMA table_info(enhanced_signals)")
            columns = await cursor.fetchall()
            await cursor.close()
            
            column_names = [col[1] for col in columns]
            
            # 🎯 產品級必需欄位列表
            required_columns = {
                'features': "TEXT DEFAULT '{}'",
                'market_conditions': "TEXT DEFAULT '{}'", 
                'tier': "TEXT DEFAULT 'MEDIUM'",
                'coin_category': "TEXT DEFAULT 'alt'",
                'category_weight': "REAL DEFAULT 1.0",
                'category_risk_multiplier': "REAL DEFAULT 1.0",
                'primary_timeframe': "TEXT DEFAULT '5m'",
                'timeframe_consensus': "TEXT DEFAULT '{}'",
                'time_decay_weight': "REAL DEFAULT 1.0",
                'hours_since_generation': "REAL DEFAULT 0.0",
                'cross_timeframe_weight': "REAL DEFAULT 1.0",
                'final_learning_weight': "REAL DEFAULT 1.0",
                'status': "TEXT DEFAULT 'PENDING'",
                'actual_outcome': "REAL DEFAULT NULL",
                'performance_score': "REAL DEFAULT NULL",
                'execution_time': "TEXT DEFAULT NULL"
            }
            
            # 檢查並添加缺失的欄位
            missing_columns = []
            for col_name, col_def in required_columns.items():
                if col_name not in column_names:
                    missing_columns.append((col_name, col_def))
            
            if missing_columns:
                logger.warning(f"🔧 檢測到 {len(missing_columns)} 個缺失欄位，正在修正...")
                for col_name, col_def in missing_columns:
                    await self.connection.execute(f"""
                        ALTER TABLE enhanced_signals 
                        ADD COLUMN {col_name} {col_def}
                    """)
                    logger.info(f"✅ 添加缺失欄位: {col_name}")
                
                await self.connection.commit()
                logger.info(f"✅ 表結構修正完成，添加了 {len(missing_columns)} 個欄位")
            else:
                logger.debug("✅ 表結構完整，無需修正")
                
        except Exception as e:
            logger.error(f"❌ 表結構驗證失敗: {e}")
            raise

    async def _perform_database_upgrade(self, from_version: int, to_version: int):
        """執行資料庫升級"""
        try:
            # 版本 1 → 2: 添加 coin_category 欄位
            if from_version < 2:
                await self._upgrade_to_version_2()
                
            # 版本 2 → 3: 確保所有必需欄位完整 (包含在v2升級中)
            if from_version < 3:
                # v2升級已包含所有必需欄位，無需額外操作
                pass
                
            # 版本 3 → 4: 強制表結構完整性驗證
            if from_version < 4:
                logger.info("🔧 執行版本4升級：強制表結構完整性驗證")
                await self._validate_and_fix_table_structure()
                
            # 更新版本號
            await self.connection.execute(
                "INSERT INTO database_version (version) VALUES (?)", 
                (to_version,)
            )
            await self.connection.commit()
            
            logger.info(f"✅ 資料庫升級完成: {from_version} → {to_version}")
            
        except Exception as e:
            logger.error(f"❌ 資料庫升級失敗: {e}")
            # 直接報錯，不降級
            raise RuntimeError(f"資料庫升級失敗: {e}")
    
    async def _upgrade_to_version_2(self):
        """升級到版本2: 添加幣種分類支援和缺失欄位"""
        try:
            # 🔧 首先檢查 enhanced_signals 表是否存在
            cursor = await self.connection.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='enhanced_signals'
            """)
            table_exists = await cursor.fetchone()
            await cursor.close()
            
            if not table_exists:
                # 如果表不存在，跳過此升級（表將在 _create_tables 中創建）
                logger.info("🔧 enhanced_signals 表不存在，跳過版本2升級")
                return
            
            # 檢查所有必需欄位是否存在
            cursor = await self.connection.execute("PRAGMA table_info(enhanced_signals)")
            columns = await cursor.fetchall()
            await cursor.close()
            
            column_names = [col[1] for col in columns]
            
            # 檢查並添加 features 欄位 (如果不存在)
            if 'features' not in column_names:
                await self.connection.execute("""
                    ALTER TABLE enhanced_signals 
                    ADD COLUMN features TEXT DEFAULT '{}'
                """)
                logger.info("✅ 添加 features 欄位")
            
            # 檢查並添加 market_conditions 欄位 (如果不存在)
            if 'market_conditions' not in column_names:
                await self.connection.execute("""
                    ALTER TABLE enhanced_signals 
                    ADD COLUMN market_conditions TEXT DEFAULT '{}'
                """)
                logger.info("✅ 添加 market_conditions 欄位")
            
            # 檢查並添加幣種分類相關欄位
            if 'coin_category' not in column_names:
                await self.connection.execute("""
                    ALTER TABLE enhanced_signals 
                    ADD COLUMN coin_category TEXT DEFAULT 'alt'
                """)
                logger.info("✅ 添加 coin_category 欄位")
            
            if 'category_weight' not in column_names:
                await self.connection.execute("""
                    ALTER TABLE enhanced_signals 
                    ADD COLUMN category_weight REAL DEFAULT 1.0
                """)
                logger.info("✅ 添加 category_weight 欄位")
            
            if 'category_risk_multiplier' not in column_names:
                await self.connection.execute("""
                    ALTER TABLE enhanced_signals 
                    ADD COLUMN category_risk_multiplier REAL DEFAULT 1.0
                """)
                logger.info("✅ 添加 category_risk_multiplier 欄位")
            
            # 檢查並添加時間框架相關欄位
            if 'primary_timeframe' not in column_names:
                await self.connection.execute("""
                    ALTER TABLE enhanced_signals 
                    ADD COLUMN primary_timeframe TEXT DEFAULT '5m'
                """)
                logger.info("✅ 添加 primary_timeframe 欄位")
            
            if 'timeframe_consensus' not in column_names:
                await self.connection.execute("""
                    ALTER TABLE enhanced_signals 
                    ADD COLUMN timeframe_consensus TEXT DEFAULT '{}'
                """)
                logger.info("✅ 添加 timeframe_consensus 欄位")
                
            # 創建索引
            await self.connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_category 
                ON enhanced_signals(coin_category)
            """)
            
            logger.info("✅ 版本2/3升級完成: 幣種分類支援和所有必需欄位已添加")
            
        except Exception as e:
            logger.error(f"❌ 版本2升級失敗: {e}")
            raise

# 全局實例
enhanced_signal_db = EnhancedSignalDatabase()

async def main():
    """測試函數"""
    print("🗄️ 增強版信號資料庫測試")
    
    # 模擬測試（需要實際的TimeFrameEnhancedSignal實例）
    await enhanced_signal_db.initialize()
    
    # 獲取權重分析
    analysis = await enhanced_signal_db.get_weight_analysis(24)
    print(f"權重分析: {enhanced_signal_db._safe_json_serialize(analysis)}")
    
    await enhanced_signal_db.close()

if __name__ == "__main__":
    asyncio.run(main())
