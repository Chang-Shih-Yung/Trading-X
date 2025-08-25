#!/usr/bin/env python3
"""
🗄️ Signal Database System
信號資料庫系統 - 解決學習歷史丟失問題

功能：
- 持久化信號歷史存儲
- 結構化信號檢索
- 學習進度追蹤
- 性能分析支援
"""

import asyncio
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)

class SignalStatus(Enum):
    """信號狀態"""
    PENDING = "PENDING"           # 等待結果
    COMPLETED = "COMPLETED"       # 已完成
    FAILED = "FAILED"            # 失敗
    CANCELLED = "CANCELLED"       # 取消

@dataclass
class StoredSignal:
    """存儲的信號數據"""
    signal_id: str
    symbol: str
    signal_type: str              # BUY/SELL
    signal_strength: float
    timestamp: datetime
    features: Dict[str, Any]
    market_conditions: Dict[str, Any]
    tier: str                     # CRITICAL/HIGH/MEDIUM/LOW
    
    # 結果數據
    status: SignalStatus = SignalStatus.PENDING
    actual_outcome: Optional[float] = None
    performance_score: Optional[float] = None
    execution_time: Optional[datetime] = None
    
    # 學習相關
    used_for_learning: bool = False
    learning_weight: float = 1.0

class SignalDatabase:
    """信號資料庫管理器"""
    
    def __init__(self, db_path: str = None):
        """初始化資料庫"""
        if db_path is None:
            # 修改為統一的 databases 目錄
            # 從當前位置 X/backend/phase2_adaptive_learning/storage/ 導航到 X/databases/
            current_file = Path(__file__)
            x_dir = current_file.parent.parent.parent.parent  # 到達 X/ 目錄
            db_dir = x_dir / "databases"
            db_dir.mkdir(exist_ok=True)
            db_path = db_dir / "signals.db"
        
        self.db_path = str(db_path)
        self.connection = None
        
        # 初始化資料庫
        self._initialize_database()
        logger.info(f"✅ 信號資料庫初始化完成: {self.db_path}")
    
    def _json_serializer(self, obj):
        """JSON序列化器，處理datetime等特殊對象"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)
    
    def _initialize_database(self):
        """初始化資料庫結構"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 創建信號表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    signal_id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    signal_type TEXT NOT NULL,
                    signal_strength REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    features TEXT NOT NULL,
                    market_conditions TEXT NOT NULL,
                    tier TEXT NOT NULL,
                    status TEXT DEFAULT 'PENDING',
                    actual_outcome REAL,
                    performance_score REAL,
                    execution_time TEXT,
                    used_for_learning BOOLEAN DEFAULT 0,
                    learning_weight REAL DEFAULT 1.0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 創建學習統計表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_signals INTEGER NOT NULL,
                    completed_signals INTEGER NOT NULL,
                    learning_ready_signals INTEGER NOT NULL,
                    avg_performance REAL,
                    last_learning_update TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 創建參數歷史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS parameter_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parameter_name TEXT NOT NULL,
                    old_value REAL,
                    new_value REAL NOT NULL,
                    confidence_score REAL,
                    signal_count INTEGER,
                    trigger_reason TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 創建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_symbol ON signals(symbol)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON signals(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON signals(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tier ON signals(tier)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ 資料庫初始化失敗: {e}")
            raise
    
    async def store_signal(self, signal: StoredSignal) -> bool:
        """存儲信號"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO signals 
                (signal_id, symbol, signal_type, signal_strength, timestamp, 
                 features, market_conditions, tier, status, actual_outcome, 
                 performance_score, execution_time, used_for_learning, learning_weight)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal.signal_id,
                signal.symbol,
                str(signal.signal_type.value) if hasattr(signal.signal_type, 'value') else str(signal.signal_type),  # 修正 enum 存儲
                signal.signal_strength,
                signal.timestamp.isoformat(),
                json.dumps(signal.features, default=self._json_serializer),
                json.dumps(signal.market_conditions, default=self._json_serializer),
                signal.tier,
                signal.status.value,
                signal.actual_outcome,
                signal.performance_score,
                signal.execution_time.isoformat() if signal.execution_time else None,
                signal.used_for_learning,
                signal.learning_weight
            ))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"✅ 信號已存儲: {signal.signal_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 信號存儲失敗: {e}")
            return False
    
    async def update_signal_outcome(self, signal_id: str, outcome: float, 
                                  performance_score: float = None) -> bool:
        """更新信號結果"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE signals 
                SET actual_outcome = ?, performance_score = ?, 
                    status = ?, execution_time = ?
                WHERE signal_id = ?
            ''', (
                outcome,
                performance_score,
                SignalStatus.COMPLETED.value,
                datetime.now().isoformat(),
                signal_id
            ))
            
            conn.commit()
            conn.close()
            
            if cursor.rowcount > 0:
                logger.debug(f"✅ 信號結果已更新: {signal_id}")
                return True
            else:
                logger.warning(f"⚠️ 信號不存在: {signal_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 信號結果更新失敗: {e}")
            return False
    
    async def get_signals_for_learning(self, limit: int = None, 
                                     min_performance: float = None) -> List[StoredSignal]:
        """獲取用於學習的信號"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = '''
                SELECT * FROM signals 
                WHERE status = 'COMPLETED' AND actual_outcome IS NOT NULL
            '''
            params = []
            
            if min_performance is not None:
                query += ' AND performance_score >= ?'
                params.append(min_performance)
            
            query += ' ORDER BY timestamp DESC'
            
            if limit is not None:
                query += ' LIMIT ?'
                params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            signals = []
            for row in rows:
                signal = self._row_to_signal(row)
                if signal:
                    signals.append(signal)
            
            logger.info(f"📊 獲取學習信號: {len(signals)} 個")
            return signals
            
        except Exception as e:
            logger.error(f"❌ 獲取學習信號失敗: {e}")
            return []
    
    async def get_signal_statistics(self) -> Dict[str, Any]:
        """獲取信號統計"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 總信號數
            cursor.execute('SELECT COUNT(*) FROM signals')
            total_signals = cursor.fetchone()[0]
            
            # 已完成信號數
            cursor.execute("SELECT COUNT(*) FROM signals WHERE status = 'COMPLETED'")
            completed_signals = cursor.fetchone()[0]
            
            # 各層級信號統計
            cursor.execute('''
                SELECT tier, COUNT(*), AVG(performance_score) 
                FROM signals 
                WHERE status = 'COMPLETED' AND performance_score IS NOT NULL
                GROUP BY tier
            ''')
            tier_stats = cursor.fetchall()
            
            # 近期性能
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute('''
                SELECT AVG(performance_score), COUNT(*) 
                FROM signals 
                WHERE status = 'COMPLETED' AND timestamp >= ? 
                AND performance_score IS NOT NULL
            ''', (week_ago,))
            recent_performance = cursor.fetchone()
            
            conn.close()
            
            stats = {
                'total_signals': total_signals,
                'completed_signals': completed_signals,
                'completion_rate': completed_signals / total_signals if total_signals > 0 else 0,
                'learning_ready': completed_signals >= 50,  # 配合學習閾值
                'tier_statistics': {
                    tier: {'count': count, 'avg_performance': avg_perf or 0.0}
                    for tier, count, avg_perf in tier_stats
                },
                'recent_performance': {
                    'avg_score': recent_performance[0] or 0.0,
                    'signal_count': recent_performance[1] or 0
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ 信號統計獲取失敗: {e}")
            return {'error': str(e)}
    
    async def delete_signal(self, signal_id: str) -> bool:
        """刪除指定信號"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM signals WHERE signal_id = ?', (signal_id,))
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                logger.info(f"🗑️ 刪除信號: {signal_id}")
                return True
            else:
                logger.warning(f"⚠️ 信號不存在: {signal_id}")
                return False
            
        except Exception as e:
            logger.error(f"❌ 信號刪除失敗: {e}")
            return False
    
    async def cleanup_old_signals(self, days_to_keep: int = 30) -> int:
        """清理舊信號"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
            
            cursor.execute('DELETE FROM signals WHERE timestamp < ?', (cutoff_date,))
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"🧹 清理舊信號: {deleted_count} 個")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ 信號清理失敗: {e}")
            return 0
    
    def _row_to_signal(self, row) -> Optional[StoredSignal]:
        """將資料庫行轉換為信號對象"""
        try:
            return StoredSignal(
                signal_id=row[0],
                symbol=row[1],
                signal_type=row[2],
                signal_strength=row[3],
                timestamp=datetime.fromisoformat(row[4]),
                features=json.loads(row[5]),
                market_conditions=json.loads(row[6]),
                tier=row[7],
                status=SignalStatus(row[8]),
                actual_outcome=row[9],
                performance_score=row[10],
                execution_time=datetime.fromisoformat(row[11]) if row[11] else None,
                used_for_learning=bool(row[12]),
                learning_weight=row[13]
            )
        except Exception as e:
            logger.error(f"❌ 信號數據轉換失敗: {e}")
            return None
    
    async def get_learning_progress(self) -> Dict[str, Any]:
        """獲取學習進度"""
        stats = await self.get_signal_statistics()
        
        # 計算學習就緒程度
        completed = stats.get('completed_signals', 0)
        learning_threshold = 50
        
        progress = {
            'signals_collected': completed,
            'learning_threshold': learning_threshold,
            'learning_ready': completed >= learning_threshold,
            'progress_percentage': min(100, (completed / learning_threshold) * 100),
            'next_milestone': max(0, learning_threshold - completed),
            'estimated_time_to_ready': self._estimate_time_to_ready(completed, learning_threshold)
        }
        
        return progress
    
    def _estimate_time_to_ready(self, current: int, target: int) -> str:
        """估算學習就緒時間"""
        if current >= target:
            return "已就緒"
        
        # 簡單估算：假設每小時 1 個信號
        hours_needed = target - current
        
        if hours_needed <= 24:
            return f"約 {hours_needed} 小時"
        else:
            days = hours_needed // 24
            return f"約 {days} 天"

# 全局實例
signal_db = SignalDatabase()

async def main():
    """測試函數"""
    print("🗄️ Signal Database 測試")
    
    # 創建測試信號
    test_signal = StoredSignal(
        signal_id="test_signal_001",
        symbol="BTCUSDT",
        signal_type="BUY",
        signal_strength=0.85,
        timestamp=datetime.now(),
        features={"rsi": 65, "macd": 0.5},
        market_conditions={"volatility": 0.3, "trend": "UP"},
        tier="HIGH"
    )
    
    # 測試存儲
    success = await signal_db.store_signal(test_signal)
    print(f"存儲測試: {'✅' if success else '❌'}")
    
    # 測試更新結果
    success = await signal_db.update_signal_outcome("test_signal_001", 1.02, 1.5)
    print(f"更新測試: {'✅' if success else '❌'}")
    
    # 測試統計
    stats = await signal_db.get_signal_statistics()
    print(f"統計測試: {stats}")
    
    # 測試學習進度
    progress = await signal_db.get_learning_progress()
    print(f"進度測試: {progress}")
    
    print("✅ 測試完成")

if __name__ == "__main__":
    asyncio.run(main())
