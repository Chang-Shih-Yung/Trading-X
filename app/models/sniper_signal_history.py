# 🎯 狙擊手信號歷史管理 - 資料庫模型

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Boolean, Text, Index
from sqlalchemy.sql import func
from enum import Enum as PyEnum
import datetime
from app.core.database import Base

class SignalStatus(PyEnum):
    """信號狀態枚舉"""
    ACTIVE = "ACTIVE"           # 活躍中
    EXPIRED = "EXPIRED"         # 已過期
    HIT_TP = "HIT_TP"          # 止盈成功
    HIT_SL = "HIT_SL"          # 止損觸發
    CANCELLED = "CANCELLED"     # 已取消

class EmailStatus(PyEnum):
    """Email 發送狀態枚舉"""
    PENDING = "PENDING"         # 待發送
    SENDING = "SENDING"         # 發送中
    SENT = "SENT"              # 已發送
    FAILED = "FAILED"          # 發送失敗
    RETRYING = "RETRYING"      # 重試中

class SignalQuality(PyEnum):
    """信號品質枚舉"""
    HIGH = "HIGH"       # 高品質 (信號強度 >= 0.7)
    MEDIUM = "MEDIUM"   # 中品質 (信號強度 >= 0.4)
    LOW = "LOW"         # 低品質 (信號強度 < 0.4)

class TradingTimeframe(PyEnum):
    """交易時間框架枚舉"""
    SHORT_TERM = "SHORT_TERM"   # 短線 (1-12小時)
    MEDIUM_TERM = "MEDIUM_TERM" # 中線 (6-36小時)
    LONG_TERM = "LONG_TERM"     # 長線 (12-96小時)

class SniperSignalDetails(Base):
    """
    🎯 狙擊手信號詳細記錄表
    
    保存所有信號的完整資訊，保留期：7天
    用於即時查詢和詳細分析
    """
    __tablename__ = 'sniper_signal_details'
    
    # 基本資訊
    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_id = Column(String(64), unique=True, nullable=False, index=True)  # 信號唯一標識
    symbol = Column(String(20), nullable=False, index=True)                   # 交易對
    signal_type = Column(String(10), nullable=False)                         # BUY/SELL
    
    # 價格資訊
    entry_price = Column(Float, nullable=False)                              # 入場價格
    stop_loss_price = Column(Float, nullable=False)                          # 止損價格
    take_profit_price = Column(Float, nullable=False)                        # 止盈價格
    
    # 信號品質指標
    signal_strength = Column(Float, nullable=False)                          # 信號強度 0.0-1.0
    confluence_count = Column(Integer, nullable=False, default=0)            # 指標匯合數量
    signal_quality = Column(Enum(SignalQuality), nullable=False)             # 信號品質等級
    
    # 時間和風險管理
    timeframe = Column(Enum(TradingTimeframe), nullable=False)               # 時間框架
    expiry_hours = Column(Integer, nullable=False)                           # 過期時間(小時)
    risk_reward_ratio = Column(Float, nullable=False)                        # 風險回報比
    
    # 市場條件
    market_volatility = Column(Float, nullable=False)                        # 市場波動率
    atr_value = Column(Float, nullable=False)                               # ATR值
    market_regime = Column(String(20), nullable=True)                       # 市場狀態
    
    # 時間戳記
    created_at = Column(DateTime, nullable=False, default=func.now())        # 創建時間
    expires_at = Column(DateTime, nullable=False)                           # 過期時間
    
    # 結果追蹤
    status = Column(Enum(SignalStatus), nullable=False, default=SignalStatus.ACTIVE)  # 狀態
    result_price = Column(Float, nullable=True)                             # 結果價格
    result_time = Column(DateTime, nullable=True)                           # 結果時間
    pnl_percentage = Column(Float, nullable=True)                           # 盈虧百分比
    
    # Email 通知狀態
    email_status = Column(Enum(EmailStatus), nullable=False, default=EmailStatus.PENDING)  # Email狀態
    email_sent_at = Column(DateTime, nullable=True)                         # Email發送時間
    email_retry_count = Column(Integer, nullable=False, default=0)          # 重試次數
    email_last_error = Column(Text, nullable=True)                          # 最後錯誤訊息
    
    # 狙擊手特定指標
    layer_one_time = Column(Float, nullable=True)                           # 第一層處理時間
    layer_two_time = Column(Float, nullable=True)                           # 第二層處理時間
    pass_rate = Column(Float, nullable=True)                                # 通過率
    
    # 額外資訊
    metadata_json = Column(Text, nullable=True)                             # JSON格式的額外數據
    reasoning = Column(Text, nullable=True)                                  # 信號推理說明
    
    # 索引優化
    __table_args__ = (
        Index('idx_symbol_created', 'symbol', 'created_at'),
        Index('idx_status_expires', 'status', 'expires_at'),
        Index('idx_quality_timeframe', 'signal_quality', 'timeframe'),
    )

class SniperSignalSummary(Base):
    """
    🎯 狙擊手信號統計摘要表
    
    每日統計數據，永久保留
    用於長期趨勢分析和性能評估
    """
    __tablename__ = 'sniper_signal_summary'
    
    # 基本資訊
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)                  # 交易對
    date = Column(DateTime, nullable=False, index=True)                      # 日期 (UTC日期)
    timeframe = Column(Enum(TradingTimeframe), nullable=False)               # 時間框架
    
    # 信號統計
    total_signals = Column(Integer, nullable=False, default=0)               # 當日總信號數
    high_quality_signals = Column(Integer, nullable=False, default=0)        # 高品質信號數
    medium_quality_signals = Column(Integer, nullable=False, default=0)      # 中品質信號數
    low_quality_signals = Column(Integer, nullable=False, default=0)         # 低品質信號數
    
    # 結果統計
    hit_tp_count = Column(Integer, nullable=False, default=0)                # 止盈成功數
    hit_sl_count = Column(Integer, nullable=False, default=0)                # 止損數
    expired_count = Column(Integer, nullable=False, default=0)               # 過期數
    cancelled_count = Column(Integer, nullable=False, default=0)             # 取消數
    
    # 性能指標
    win_rate = Column(Float, nullable=False, default=0.0)                   # 勝率 (止盈/總結果)
    avg_pnl_percentage = Column(Float, nullable=False, default=0.0)         # 平均盈虧%
    avg_signal_strength = Column(Float, nullable=False, default=0.0)        # 平均信號強度
    avg_confluence_count = Column(Float, nullable=False, default=0.0)       # 平均匯合數
    avg_risk_reward_ratio = Column(Float, nullable=False, default=0.0)      # 平均風險回報比
    
    # 市場條件統計
    avg_market_volatility = Column(Float, nullable=False, default=0.0)      # 平均市場波動率
    avg_atr_value = Column(Float, nullable=False, default=0.0)              # 平均ATR值
    
    # 處理性能統計
    avg_layer_one_time = Column(Float, nullable=False, default=0.0)         # 平均第一層時間
    avg_layer_two_time = Column(Float, nullable=False, default=0.0)         # 平均第二層時間
    avg_pass_rate = Column(Float, nullable=False, default=0.0)              # 平均通過率
    
    # 時間戳記
    created_at = Column(DateTime, nullable=False, default=func.now())        # 創建時間
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())  # 更新時間
    
    # 唯一約束：每個交易對每日每時間框架只有一條記錄
    __table_args__ = (
        Index('idx_symbol_date_timeframe', 'symbol', 'date', 'timeframe', unique=True),
        Index('idx_date_win_rate', 'date', 'win_rate'),
    )

# 創建資料庫表的輔助函數
async def create_tables_async(engine):
    """使用異步引擎創建所有信號歷史相關的資料庫表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ 狙擊手信號歷史管理資料庫表創建完成")
    print("   - SniperSignalDetails: 詳細記錄表 (7天保留)")  
    print("   - SniperSignalSummary: 統計摘要表 (永久保留)")

def create_tables(sync_engine):
    """使用同步引擎創建所有信號歷史相關的資料庫表"""
    Base.metadata.create_all(sync_engine)
    print("✅ 狙擊手信號歷史管理資料庫表創建完成")
    print("   - SniperSignalDetails: 詳細記錄表 (7天保留)")  
    print("   - SniperSignalSummary: 統計摘要表 (永久保留)")

def drop_tables(sync_engine):
    """刪除所有信號歷史相關的資料庫表"""
    Base.metadata.drop_all(sync_engine)
    print("⚠️ 狙擊手信號歷史管理資料庫表已刪除")
