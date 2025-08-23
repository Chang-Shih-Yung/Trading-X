#!/usr/bin/env python3
"""
🕒 Priority 3: Timeframe-Enhanced Signal System
優先級3：時間框架增強信號系統

功能特色：
- 多時間框架信號數據結構
- 跨週期一致性檢測
- 時間框架感知學習權重
- 產品級真實數據保證

整合優先級1、2：
- 時間衰減機制（優先級1）
- 幣種分類系統（優先級2）  
- 時間框架感知（優先級3）- 新增
"""

import asyncio
import math
import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class TimeFrame(Enum):
    """時間框架枚舉 - 產品級標準"""
    M1 = "1m"       # 1分鐘：超短期反應
    M5 = "5m"       # 5分鐘：短期交易主週期
    M15 = "15m"     # 15分鐘：中期趨勢確認
    H1 = "1h"       # 1小時：背景方向驗證
    H4 = "4h"       # 4小時：長期趨勢
    D1 = "1d"       # 日線：戰略方向

class TimeFrameCategory(Enum):
    """時間框架分類"""
    ULTRA_SHORT = "ultra_short"    # 1m
    SHORT = "short"                # 5m, 15m
    MEDIUM = "medium"              # 1h, 4h  
    LONG = "long"                  # 1d

@dataclass
class TimeFrameConsensus:
    """時間框架一致性分析"""
    timeframe_signals: Dict[str, float] = field(default_factory=dict)  # 各時間框架信號強度
    consensus_score: float = 0.0                # 總體一致性分數 (0-1)
    dominant_timeframe: Optional[str] = None    # 主導時間框架
    conflict_level: float = 0.0                 # 衝突程度 (0-1)
    weight_adjustment: float = 1.0              # 權重調整因子

@dataclass
class TimeFrameEnhancedSignal:
    """時間框架增強信號 - 整合優先級1、2、3"""
    
    # === 基礎信號信息 ===
    signal_id: str
    symbol: str
    signal_type: str              # BUY/SELL
    signal_strength: float
    timestamp: datetime
    features: Dict[str, Any]
    market_conditions: Dict[str, Any]
    tier: str                     # CRITICAL/HIGH/MEDIUM/LOW
    
    # === 優先級1：時間衰減機制 ===
    time_decay_weight: float = 1.0              # 時間衰減權重
    hours_since_generation: float = 0.0         # 生成至今小時數
    
    # === 優先級2：幣種分類系統 ===
    coin_category: str = "alt"                   # major/alt/meme/payment
    category_weight: float = 1.0                # 幣種分類權重
    category_risk_multiplier: float = 1.0       # 幣種風險乘數
    
    # === 優先級3：時間框架感知 ===
    primary_timeframe: str = "5m"               # 主要時間框架
    timeframe_consensus: TimeFrameConsensus = field(default_factory=TimeFrameConsensus)
    cross_timeframe_weight: float = 1.0         # 跨時間框架權重
    
    # === 最終融合權重 ===
    final_learning_weight: float = 1.0          # 時間衰減 × 幣種 × 時間框架
    
    # === 結果數據 ===
    status: str = "PENDING"
    actual_outcome: Optional[float] = None
    performance_score: Optional[float] = None
    execution_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        if self.execution_time:
            result['execution_time'] = self.execution_time.isoformat()
        return result

class TimeFrameAwareLearningEngine:
    """時間框架感知學習引擎 - 優先級3核心"""
    
    def __init__(self):
        """初始化時間框架感知學習引擎"""
        
        # === 產品級配置：時間框架權重 ===
        self.timeframe_weights = {
            "1m": 0.15,    # 超短期：快速反應但噪音較多
            "5m": 0.35,    # 短期：主要交易週期
            "15m": 0.30,   # 中期：趨勢確認
            "1h": 0.15,    # 背景：方向驗證
            "4h": 0.05,    # 長期：戰略方向
            "1d": 0.02     # 超長期：制度背景
        }
        
        # === 時間框架分類映射 ===
        self.timeframe_categories = {
            'ultra_short': ['1m'],
            'short': ['5m', '15m'],
            'medium': ['1h', '4h'],
            'long': ['1d']
        }
        
        # === 優先級1：時間衰減配置（12小時半衰期）===
        self.time_decay_config = {
            'half_life_hours': 12.0,           # 12小時半衰期
            'min_weight': 0.1,                 # 最小權重
            'max_hours': 48.0                  # 48小時後完全失效
        }
        
        # === 優先級2：幣種分類配置 ===
        self.coin_categories = {
            'major': {
                'symbols': ['BTCUSDT', 'ETHUSDT'],
                'weight': 1.2,                 # 主流幣：較高權重
                'risk_multiplier': 0.85,       # 保守風險
                'signal_threshold': 0.65       # 較高門檻
            },
            'alt': {
                'symbols': ['BNBUSDT', 'ADAUSDT', 'SOLUSDT'],
                'weight': 1.0,                 # 標準權重
                'risk_multiplier': 1.0,        # 標準風險
                'signal_threshold': 0.60       # 平衡門檻
            },
            'meme': {
                'symbols': ['DOGEUSDT'],
                'weight': 0.8,                 # 較低權重（高風險）
                'risk_multiplier': 1.2,        # 積極風險
                'signal_threshold': 0.55       # 較低門檻
            },
            'payment': {
                'symbols': ['XRPUSDT'],
                'weight': 1.1,                 # 稍高權重
                'risk_multiplier': 0.9,        # 稍保守風險
                'signal_threshold': 0.62       # 中等門檻
            }
        }
        
        # === 優先級3：時間框架一致性閾值 ===
        self.consensus_thresholds = {
            'high_consensus': 0.8,             # 高一致性
            'medium_consensus': 0.6,           # 中等一致性
            'low_consensus': 0.4,              # 低一致性
            'conflict_threshold': 0.3          # 衝突閾值
        }
        
        # === 學習統計 ===
        # 學習統計 - 產品級監控指標
        self.learning_stats = {
            'total_signals_processed': 0,
            'weight_calculations': 0,  # 添加權重計算統計
            'timeframe_distribution': defaultdict(int),
            'category_performance': defaultdict(list),
            'consensus_performance': defaultdict(int)  # 修正：改為int類型
        }
        
        logger.info("✅ 時間框架感知學習引擎初始化完成")
        logger.info(f"📊 支援時間框架: {list(self.timeframe_weights.keys())}")
        logger.info(f"🏷️ 支援幣種分類: {list(self.coin_categories.keys())}")
    
    def get_coin_category(self, symbol: str) -> str:
        """獲取幣種分類"""
        for category, config in self.coin_categories.items():
            if symbol in config['symbols']:
                return category
        return 'alt'  # 預設為alt類別（產品級安全設計）
    
    def calculate_time_decay_weight(self, timestamp: datetime) -> float:
        """計算時間衰減權重（優先級1）"""
        try:
            hours_elapsed = (datetime.now() - timestamp).total_seconds() / 3600
            
            if hours_elapsed >= self.time_decay_config['max_hours']:
                return self.time_decay_config['min_weight']
            
            # 指數衰減：weight = exp(-ln(2) * hours / half_life)
            half_life = self.time_decay_config['half_life_hours']
            decay_weight = np.exp(-np.log(2) * hours_elapsed / half_life)
            
            return max(self.time_decay_config['min_weight'], decay_weight)
            
        except Exception as e:
            logger.warning(f"⚠️ 時間衰減計算失敗: {e}")
            return 1.0
    
    def calculate_category_weight(self, symbol: str) -> Tuple[float, float]:
        """計算幣種分類權重（優先級2）"""
        try:
            category = self.get_coin_category(symbol)
            config = self.coin_categories[category]
            
            return config['weight'], config['risk_multiplier']
            
        except Exception as e:
            logger.warning(f"⚠️ 幣種分類權重計算失敗: {e}")
            return 1.0, 1.0
    
    async def analyze_timeframe_consensus(self, 
                                        symbol: str, 
                                        timeframe_data: Dict[str, Any]) -> TimeFrameConsensus:
        """分析時間框架一致性（優先級3核心）"""
        try:
            consensus = TimeFrameConsensus()
            
            # 嚴格驗證輸入數據
            if not isinstance(timeframe_data, dict):
                logger.error(f"❌ {symbol}: timeframe_data 不是字典類型: {type(timeframe_data)}")
                return consensus
            
            logger.debug(f"🔍 {symbol}: 開始分析時間框架共識")
            logger.debug(f"🔍 {symbol}: timeframe_weights.keys() = {list(self.timeframe_weights.keys())}")
            logger.debug(f"🔍 {symbol}: timeframe_data.keys() = {list(timeframe_data.keys())}")
                
            # 提取各時間框架的信號強度
            timeframe_signals = {}
            for tf in self.timeframe_weights.keys():
                logger.debug(f"🔍 {symbol}: 處理時間框架: {tf}")
                if tf in timeframe_data:
                    tf_data = timeframe_data[tf]
                    
                    # 驗證時間框架數據格式
                    if not isinstance(tf_data, dict):
                        logger.warning(f"⚠️ {symbol}: {tf} 數據不是字典格式: {type(tf_data)}")
                        continue
                        
                    signal_strength = tf_data.get('signal_strength', 0.0)
                    
                    # 確保信號強度是數值
                    try:
                        signal_strength = float(signal_strength)
                        timeframe_signals[tf] = signal_strength
                        logger.debug(f"✅ {symbol}: {tf} 信號強度: {signal_strength}")
                    except (ValueError, TypeError) as e:
                        logger.warning(f"⚠️ {symbol}: {tf} 信號強度轉換失敗: {e}")
                        continue
            
            consensus.timeframe_signals = timeframe_signals
            
            if not timeframe_signals:
                logger.warning(f"⚠️ {symbol}: 無有效時間框架信號數據")
                return consensus
            
            logger.debug(f"🔍 {symbol}: timeframe_signals 類型: {type(timeframe_signals)}")
            logger.debug(f"🔍 {symbol}: timeframe_signals 內容: {timeframe_signals}")

            # 計算加權平均信號強度
            weighted_signals = []
            total_weight = 0
            
            # 安全迭代時間框架信號
            try:
                # 再次驗證 timeframe_signals 是字典
                if not isinstance(timeframe_signals, dict):
                    logger.error(f"❌ {symbol}: timeframe_signals 不是字典: {type(timeframe_signals)} = {timeframe_signals}")
                    return consensus
                    
                for tf, signal in timeframe_signals.items():
                    weight = self.timeframe_weights.get(tf, 0)
                    if isinstance(signal, (int, float)) and isinstance(weight, (int, float)):
                        weighted_signals.append(signal * weight)
                        total_weight += weight
                    else:
                        logger.warning(f"⚠️ {symbol}: {tf} 數據類型錯誤 - signal: {type(signal)}, weight: {type(weight)}")
            except Exception as e:
                logger.error(f"❌ {symbol}: 計算加權信號時出錯: {e}")
                import traceback
                traceback.print_exc()
                return consensus
                
            if total_weight > 0:
                avg_signal = sum(weighted_signals) / total_weight
            else:
                avg_signal = 0
                
            logger.debug(f"✅ {symbol}: 加權平均信號: {avg_signal:.3f}")
            
            # 計算一致性分數
            if len(timeframe_signals) > 1:
                try:
                    signals_list = list(timeframe_signals.values())
                    # 確保所有信號都是數值
                    signals_list = [float(s) for s in signals_list if isinstance(s, (int, float))]
                    
                    if len(signals_list) > 1:
                        signal_std = np.std(signals_list)
                        signal_range = max(signals_list) - min(signals_list)
                        
                        # 一致性 = 1 - 標準差/範圍（標準化）
                        if signal_range > 0:
                            consensus.consensus_score = max(0, 1 - (signal_std / signal_range))
                        else:
                            consensus.consensus_score = 1.0
                    else:
                        consensus.consensus_score = 1.0
                except Exception as e:
                    logger.error(f"❌ {symbol}: 一致性分數計算失敗: {e}")
                    consensus.consensus_score = 0.0
            else:
                consensus.consensus_score = 1.0
            
            # 確定主導時間框架
            if timeframe_signals:
                consensus.dominant_timeframe = max(timeframe_signals, 
                                                 key=lambda tf: timeframe_signals[tf] * self.timeframe_weights.get(tf, 0))
            
            # 計算衝突程度
            consensus.conflict_level = 1 - consensus.consensus_score
            
            # 計算權重調整因子
            if consensus.consensus_score >= self.consensus_thresholds['high_consensus']:
                consensus.weight_adjustment = 1.2  # 高一致性加成
            elif consensus.consensus_score >= self.consensus_thresholds['medium_consensus']:
                consensus.weight_adjustment = 1.0  # 標準權重
            elif consensus.consensus_score >= self.consensus_thresholds['low_consensus']:
                consensus.weight_adjustment = 0.8  # 低一致性減分
            else:
                consensus.weight_adjustment = 0.6  # 衝突懲罰
            
            # 更新統計
            if consensus.consensus_score >= self.consensus_thresholds['high_consensus']:
                self.learning_stats['consensus_performance']['high'] += 1
            elif consensus.consensus_score >= self.consensus_thresholds['medium_consensus']:
                self.learning_stats['consensus_performance']['medium'] += 1
            elif consensus.consensus_score >= self.consensus_thresholds['low_consensus']:
                self.learning_stats['consensus_performance']['low'] += 1
            else:
                self.learning_stats['consensus_performance']['conflict'] += 1
            
            return consensus
            
        except Exception as e:
            logger.error(f"❌ 時間框架一致性分析失敗: {e}")
            return TimeFrameConsensus()
    
    async def create_enhanced_signal(self,
                                   base_signal: Dict[str, Any],
                                   timeframe_data: Dict[str, Any]) -> TimeFrameEnhancedSignal:
        """創建時間框架增強信號（三維整合）"""
        try:
            # 基礎信號信息
            signal = TimeFrameEnhancedSignal(
                signal_id=base_signal.get('signal_id', ''),
                symbol=base_signal.get('symbol', ''),
                signal_type=base_signal.get('signal_type', ''),
                signal_strength=base_signal.get('signal_strength', 0.0),
                timestamp=base_signal.get('timestamp', datetime.now()),
                features=base_signal.get('features', {}),
                market_conditions=base_signal.get('market_conditions', {}),
                tier=base_signal.get('tier', 'MEDIUM'),
                primary_timeframe=base_signal.get('primary_timeframe', '5m')
            )
            
            # === 優先級1：時間衰減權重 ===
            signal.time_decay_weight = self.calculate_time_decay_weight(signal.timestamp)
            signal.hours_since_generation = (datetime.now() - signal.timestamp).total_seconds() / 3600
            
            # === 優先級2：幣種分類權重 ===
            signal.coin_category = self.get_coin_category(signal.symbol)
            signal.category_weight, signal.category_risk_multiplier = self.calculate_category_weight(signal.symbol)
            
            # === 優先級3：時間框架一致性 ===
            signal.timeframe_consensus = await self.analyze_timeframe_consensus(signal.symbol, timeframe_data)
            signal.cross_timeframe_weight = signal.timeframe_consensus.weight_adjustment
            
            # === 計算最終融合權重 ===
            signal.calculate_final_weight()
            
            # 更新統計
            self.learning_stats['total_signals_processed'] += 1
            self.learning_stats['timeframe_distribution'][signal.primary_timeframe] += 1
            
            logger.info(f"✅ {signal.symbol}: 增強信號創建完成")
            logger.debug(f"🔍 最終權重: {signal.final_learning_weight:.3f} "
                        f"(時間:{signal.time_decay_weight:.3f} × "
                        f"幣種:{signal.category_weight:.3f} × "
                        f"時間框架:{signal.cross_timeframe_weight:.3f})")
            
            return signal
            
        except Exception as e:
            logger.error(f"❌ 增強信號創建失敗: {e}")
            import traceback
            traceback.print_exc()
            
            # 返回基礎信號（產品級容錯）
            return TimeFrameEnhancedSignal(
                signal_id=base_signal.get('signal_id', ''),
                symbol=base_signal.get('symbol', ''),
                signal_type=base_signal.get('signal_type', ''),
                signal_strength=base_signal.get('signal_strength', 0.0),
                timestamp=base_signal.get('timestamp', datetime.now()),
                features=base_signal.get('features', {}),
                market_conditions=base_signal.get('market_conditions', {}),
                tier=base_signal.get('tier', 'MEDIUM')
            )
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """獲取學習摘要"""
        return {
            'engine_status': '運行正常',
            'total_signals_processed': self.learning_stats['total_signals_processed'],
            'timeframe_distribution': self.learning_stats['timeframe_distribution'],
            'category_performance': self.learning_stats['category_performance'],
            'consensus_performance': self.learning_stats['consensus_performance'],
            'configuration': {
                'timeframe_weights': self.timeframe_weights,
                'time_decay_half_life': self.time_decay_config['half_life_hours'],
                'coin_categories': list(self.coin_categories.keys()),
                'consensus_thresholds': self.consensus_thresholds
            }
        }
    
    async def calculate_final_weight(self, signal: TimeFrameEnhancedSignal, timeframe_analysis) -> Dict[str, float]:
        """計算最終的三維融合權重"""
        try:
            # 1. 計算時間衰減權重（優先級1）
            hours_since = signal.hours_since_generation
            time_decay_weight = math.exp(-hours_since / self.time_decay_config['half_life_hours'])
            
            # 2. 計算幣種分類權重（優先級2）
            category = signal.coin_category
            category_config = self.coin_categories.get(category, self.coin_categories['alt'])
            category_weight = category_config.get('weight', 1.0)  # 🔧 修復：使用 'weight'
            risk_multiplier = category_config.get('risk_multiplier', 1.0)
            category_weight *= risk_multiplier
            
            # 3. 計算跨時間框架權重（優先級3）
            if hasattr(timeframe_analysis, 'consensus_score'):
                # TimeFrameConsensus 對象
                consensus_score = timeframe_analysis.consensus_score
                weight_adjustment = timeframe_analysis.weight_adjustment
                logger.debug(f"✅ 使用TimeFrameConsensus: 共識={consensus_score:.3f}, 調整={weight_adjustment:.3f}")
            elif isinstance(timeframe_analysis, dict):
                # 字典格式
                consensus_score = timeframe_analysis.get('consensus_score', 0.0)
                weight_adjustment = timeframe_analysis.get('weight_adjustment', 1.0)
                logger.debug(f"✅ 使用字典格式: 共識={consensus_score:.3f}, 調整={weight_adjustment:.3f}")
            else:
                # 無效格式，使用默認值
                consensus_score = 0.0
                weight_adjustment = 1.0
                logger.warning(f"⚠️ 時間框架分析格式無效: {type(timeframe_analysis)}")
            
            cross_timeframe_weight = consensus_score * weight_adjustment
            
            # 4. 三維權重融合
            final_weight = time_decay_weight * category_weight * cross_timeframe_weight
            
            # 5. 更新統計
            self.learning_stats['weight_calculations'] += 1
            
            logger.debug(f"✅ 三維權重計算完成: "
                        f"時間衰減={time_decay_weight:.3f}, "
                        f"幣種分類={category_weight:.3f}, "
                        f"跨時間框架={cross_timeframe_weight:.3f}, "
                        f"最終權重={final_weight:.3f}")
            
            return {
                'time_decay_weight': time_decay_weight,
                'category_weight': category_weight,
                'cross_timeframe_weight': cross_timeframe_weight,
                'final_weight': final_weight
            }
            
        except Exception as e:
            logger.error(f"❌ 三維權重計算失敗: {e}")
            import traceback
            traceback.print_exc()
            # 返回默認權重
            return {
                'time_decay_weight': 0.5,
                'category_weight': 0.5,
                'cross_timeframe_weight': 0.5,
                'final_weight': 0.125  # 0.5^3
            }

# 全局實例（產品級單例）
timeframe_learning_engine = TimeFrameAwareLearningEngine()

async def main():
    """測試函數"""
    print("🕒 時間框架感知學習引擎測試")
    
    # 測試信號
    test_signal = {
        'signal_id': 'TEST_001',
        'symbol': 'BTCUSDT',
        'signal_type': 'BUY',
        'signal_strength': 0.75,
        'timestamp': datetime.now() - timedelta(hours=2),
        'features': {'momentum': 0.8, 'volume': 1.2},
        'market_conditions': {'volatility': 0.3},
        'tier': 'HIGH',
        'primary_timeframe': '5m'
    }
    
    # 測試時間框架數據
    timeframe_data = {
        '1m': {'signal_strength': 0.7},
        '5m': {'signal_strength': 0.8},
        '15m': {'signal_strength': 0.75},
        '1h': {'signal_strength': 0.6}
    }
    
    # 創建增強信號
    enhanced_signal = await timeframe_learning_engine.create_enhanced_signal(
        test_signal, timeframe_data
    )
    
    print(f"增強信號: {enhanced_signal.symbol}")
    print(f"最終權重: {enhanced_signal.final_learning_weight:.3f}")
    print(f"時間衰減: {enhanced_signal.time_decay_weight:.3f}")
    print(f"幣種權重: {enhanced_signal.category_weight:.3f}")
    print(f"時間框架權重: {enhanced_signal.cross_timeframe_weight:.3f}")
    print(f"一致性分數: {enhanced_signal.timeframe_consensus.consensus_score:.3f}")
    
    # 獲取摘要
    summary = timeframe_learning_engine.get_learning_summary()
    print(f"\n學習摘要: {json.dumps(summary, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    asyncio.run(main())
