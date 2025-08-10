"""
📊 Phase4 Signal Processing Statistics
=====================================

信號處理統計實現 - 基於配置驅動的多維度信號分析
與 signal_processing_statistics_config.json 配置文件對應
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)

@dataclass
class SignalMetrics:
    """信號指標數據"""
    timestamp: datetime
    symbol: str
    priority: str
    quality_score: float
    processing_latency: float
    source: str
    phase1_duration: float
    phase2_duration: float
    phase3_duration: float

@dataclass
class StatisticalSummary:
    """統計摘要"""
    count: int
    mean: float
    median: float
    std_dev: float
    min_value: float
    max_value: float
    percentile_95: float
    percentile_99: float

class SignalProcessingStatistics:
    """信號處理統計系統"""
    
    def __init__(self):
        # 載入配置文件
        self.config = self._load_config()
        
        # 統計數據存儲
        self.signal_history: deque = deque(maxlen=10000)  # 保留最近10000個信號
        self.quality_distribution: Dict[str, int] = defaultdict(int)
        self.priority_distribution: Dict[str, int] = defaultdict(int)
        self.source_distribution: Dict[str, int] = defaultdict(int)
        
        # 時間窗口統計
        self.hourly_stats: Dict[str, List] = defaultdict(list)
        self.daily_stats: Dict[str, List] = defaultdict(list)
        
        # 性能監控
        self.last_update = datetime.now()
        self.statistics_enabled = True
        
        # 初始化統計模塊
        self._initialize_statistics()
        
        # 驗證配置
        if not self.validate_configuration():
            logger.warning("使用默認配置")
            self.config = self._get_default_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """載入配置文件"""
        try:
            config_path = Path(__file__).parent / "signal_processing_statistics_config.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"載入統計配置失敗: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """獲取默認配置"""
        return {
            "PHASE4_SIGNAL_PROCESSING_STATISTICS": {
                "statistical_analysis": {
                    "quality_distribution_tracking": {
                        "bin_count": 10,
                        "quality_thresholds": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                        "trend_analysis_enabled": True,
                        "quality_target": 0.8
                    },
                    "priority_level_analytics": {
                        "categories": ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                        "success_rate_tracking": True,
                        "processing_time_correlation": True
                    },
                    "processing_time_analysis": {
                        "percentiles": [50, 90, 95, 99],
                        "phases": {
                            "phase1_signal_generation": {"target_latency_ms": 200},
                            "phase2_pre_evaluation": {"target_latency_ms": 15},
                            "phase3_execution_policy": {"target_latency_ms": 450}
                        },
                        "total_target_latency_ms": 800
                    },
                    "source_performance_comparison": {
                        "enable_benchmarking": True,
                        "reliability_tracking": True,
                        "supported_sources": ["binance", "coinbase", "kraken", "huobi", "unknown"]
                    }
                },
                "real_time_monitoring": {
                    "update_intervals": {"comprehensive_statistics_seconds": 5},
                    "data_retention": {"signal_history_max_count": 10000}
                }
            }
        }
    
    def _initialize_statistics(self):
        """初始化統計模塊"""
        logger.info("初始化信號處理統計系統")
        
        # 清理舊數據（如果需要）
        self._cleanup_old_data()
        
        # 設置統計間隔
        self.update_interval = 5  # 5秒更新一次統計
        
    def validate_configuration(self) -> bool:
        """驗證配置完整性"""
        try:
            required_sections = [
                "statistical_analysis",
                "real_time_monitoring"
            ]
            
            stats_config = self.config.get("PHASE4_SIGNAL_PROCESSING_STATISTICS", {})
            
            for section in required_sections:
                if section not in stats_config:
                    logger.warning(f"配置缺少必要部分: {section}")
                    return False
            
            logger.info("配置驗證通過")
            return True
            
        except Exception as e:
            logger.error(f"配置驗證失敗: {e}")
            return False
    
    def get_config_value(self, key_path: str, default_value: Any = None) -> Any:
        """安全獲取配置值"""
        try:
            keys = key_path.split('.')
            current = self.config
            
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return default_value
            
            return current
            
        except Exception:
            return default_value
        
    def _cleanup_old_data(self):
        """清理過舊的數據"""
        cutoff_time = datetime.now() - timedelta(days=7)  # 保留7天數據
        
        # 清理歷史數據
        self.signal_history = deque(
            [signal for signal in self.signal_history 
             if signal.timestamp > cutoff_time],
            maxlen=10000
        )
        
    async def record_signal_metrics(self, signal_data: Dict[str, Any]) -> bool:
        """記錄信號指標"""
        try:
            # 創建信號指標對象
            metrics = SignalMetrics(
                timestamp=datetime.fromisoformat(signal_data.get('timestamp', datetime.now().isoformat())),
                symbol=signal_data.get('symbol', 'UNKNOWN'),
                priority=signal_data.get('priority', 'MEDIUM'),
                quality_score=float(signal_data.get('quality_score', 0.5)),
                processing_latency=float(signal_data.get('total_latency', 0)),
                source=signal_data.get('source', 'unknown'),
                phase1_duration=float(signal_data.get('phase1_duration', 0)),
                phase2_duration=float(signal_data.get('phase2_duration', 0)),
                phase3_duration=float(signal_data.get('phase3_duration', 0))
            )
            
            # 添加到歷史記錄
            self.signal_history.append(metrics)
            
            # 更新分佈統計
            self._update_distributions(metrics)
            
            # 更新時間窗口統計
            self._update_time_window_stats(metrics)
            
            self.last_update = datetime.now()
            return True
            
        except Exception as e:
            logger.error(f"記錄信號指標失敗: {e}")
            return False
    
    def _update_distributions(self, metrics: SignalMetrics):
        """更新分佈統計"""
        # 質量分佈（分成10個區間）
        quality_bin = min(int(metrics.quality_score * 10), 9)
        self.quality_distribution[f"bin_{quality_bin}"] += 1
        
        # 優先級分佈
        self.priority_distribution[metrics.priority] += 1
        
        # 來源分佈
        self.source_distribution[metrics.source] += 1
    
    def _update_time_window_stats(self, metrics: SignalMetrics):
        """更新時間窗口統計"""
        current_hour = metrics.timestamp.replace(minute=0, second=0, microsecond=0)
        current_day = metrics.timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 小時統計
        hour_key = current_hour.isoformat()
        self.hourly_stats[hour_key].append({
            'quality_score': metrics.quality_score,
            'processing_latency': metrics.processing_latency,
            'priority': metrics.priority
        })
        
        # 日統計
        day_key = current_day.isoformat()
        self.daily_stats[day_key].append({
            'quality_score': metrics.quality_score,
            'processing_latency': metrics.processing_latency,
            'priority': metrics.priority
        })
        
        # 限制記錄數量
        if len(self.hourly_stats) > 48:  # 保留48小時
            oldest_hour = min(self.hourly_stats.keys())
            del self.hourly_stats[oldest_hour]
            
        if len(self.daily_stats) > 30:  # 保留30天
            oldest_day = min(self.daily_stats.keys())
            del self.daily_stats[oldest_day]
    
    async def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """獲取綜合統計數據"""
        try:
            current_time = datetime.now()
            
            # 基本統計
            total_signals = len(self.signal_history)
            if total_signals == 0:
                return self._get_empty_statistics()
            
            # 質量分數統計
            quality_scores = [signal.quality_score for signal in self.signal_history]
            quality_stats = self._calculate_statistical_summary(quality_scores)
            
            # 處理延遲統計
            latencies = [signal.processing_latency for signal in self.signal_history]
            latency_stats = self._calculate_statistical_summary(latencies)
            
            # 各階段延遲統計
            phase1_latencies = [signal.phase1_duration for signal in self.signal_history]
            phase2_latencies = [signal.phase2_duration for signal in self.signal_history]
            phase3_latencies = [signal.phase3_duration for signal in self.signal_history]
            
            # 最近24小時趨勢
            recent_trend = self._calculate_recent_trends()
            
            # 性能基準測試
            performance_benchmarks = self._calculate_performance_benchmarks()
            
            return {
                "statistics_metadata": {
                    "generated_at": current_time.isoformat(),
                    "total_signals_analyzed": total_signals,
                    "time_range": {
                        "earliest": min(signal.timestamp for signal in self.signal_history).isoformat(),
                        "latest": max(signal.timestamp for signal in self.signal_history).isoformat()
                    },
                    "last_update": self.last_update.isoformat()
                },
                "quality_distribution_analysis": {
                    "overall_statistics": asdict(quality_stats),
                    "distribution_bins": dict(self.quality_distribution),
                    "quality_trends": recent_trend.get("quality_trend", [])
                },
                "priority_level_analytics": {
                    "distribution": dict(self.priority_distribution),
                    "processing_time_by_priority": self._get_latency_by_priority(),
                    "success_rate_by_priority": self._get_success_rate_by_priority()
                },
                "processing_time_analysis": {
                    "overall_latency": asdict(latency_stats),
                    "phase_breakdown": {
                        "phase1_signal_generation": asdict(self._calculate_statistical_summary(phase1_latencies)),
                        "phase2_pre_evaluation": asdict(self._calculate_statistical_summary(phase2_latencies)),
                        "phase3_execution_policy": asdict(self._calculate_statistical_summary(phase3_latencies))
                    },
                    "latency_trends": recent_trend.get("latency_trend", [])
                },
                "source_performance_comparison": {
                    "source_distribution": dict(self.source_distribution),
                    "performance_by_source": self._get_performance_by_source(),
                    "reliability_metrics": self._get_source_reliability()
                },
                "temporal_analysis": {
                    "hourly_patterns": self._analyze_hourly_patterns(),
                    "daily_patterns": self._analyze_daily_patterns(),
                    "peak_performance_windows": self._identify_peak_windows()
                },
                "performance_benchmarks": performance_benchmarks
            }
            
        except Exception as e:
            logger.error(f"生成綜合統計失敗: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    def _calculate_statistical_summary(self, values: List[float]) -> StatisticalSummary:
        """計算統計摘要"""
        if not values:
            return StatisticalSummary(0, 0, 0, 0, 0, 0, 0, 0)
        
        sorted_values = sorted(values)
        count = len(values)
        
        return StatisticalSummary(
            count=count,
            mean=statistics.mean(values),
            median=statistics.median(values),
            std_dev=statistics.stdev(values) if count > 1 else 0,
            min_value=min(values),
            max_value=max(values),
            percentile_95=sorted_values[int(0.95 * count)] if count > 0 else 0,
            percentile_99=sorted_values[int(0.99 * count)] if count > 0 else 0
        )
    
    def _get_empty_statistics(self) -> Dict[str, Any]:
        """獲取空統計數據"""
        return {
            "statistics_metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_signals_analyzed": 0,
                "status": "no_data"
            },
            "message": "沒有足夠的信號數據生成統計"
        }
    
    def _calculate_recent_trends(self) -> Dict[str, List]:
        """計算最近趨勢"""
        # 最近24小時的趨勢
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_signals = [s for s in self.signal_history if s.timestamp > cutoff_time]
        
        # 按小時分組
        hourly_buckets = defaultdict(list)
        for signal in recent_signals:
            hour_key = signal.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_buckets[hour_key].append(signal)
        
        # 生成趨勢數據
        quality_trend = []
        latency_trend = []
        
        for hour in sorted(hourly_buckets.keys()):
            signals = hourly_buckets[hour]
            if signals:
                avg_quality = statistics.mean([s.quality_score for s in signals])
                avg_latency = statistics.mean([s.processing_latency for s in signals])
                
                quality_trend.append({
                    "timestamp": hour.isoformat(),
                    "average_quality": round(avg_quality, 3),
                    "signal_count": len(signals)
                })
                
                latency_trend.append({
                    "timestamp": hour.isoformat(),
                    "average_latency": round(avg_latency, 2),
                    "signal_count": len(signals)
                })
        
        return {
            "quality_trend": quality_trend,
            "latency_trend": latency_trend
        }
    
    def _get_latency_by_priority(self) -> Dict[str, float]:
        """獲取各優先級的延遲"""
        priority_latencies = defaultdict(list)
        
        for signal in self.signal_history:
            priority_latencies[signal.priority].append(signal.processing_latency)
        
        return {
            priority: statistics.mean(latencies) if latencies else 0
            for priority, latencies in priority_latencies.items()
        }
    
    def _get_success_rate_by_priority(self) -> Dict[str, float]:
        """獲取各優先級的成功率（模擬）"""
        priority_counts = defaultdict(int)
        
        for signal in self.signal_history:
            priority_counts[signal.priority] += 1
        
        # 模擬成功率（實際應該從實際結果計算）
        success_rates = {
            "CRITICAL": 0.95,
            "HIGH": 0.88,
            "MEDIUM": 0.82,
            "LOW": 0.75
        }
        
        return {
            priority: success_rates.get(priority, 0.8)
            for priority in priority_counts.keys()
        }
    
    def _get_performance_by_source(self) -> Dict[str, Dict[str, float]]:
        """獲取各來源的性能"""
        source_metrics = defaultdict(lambda: {"latencies": [], "qualities": []})
        
        for signal in self.signal_history:
            source_metrics[signal.source]["latencies"].append(signal.processing_latency)
            source_metrics[signal.source]["qualities"].append(signal.quality_score)
        
        result = {}
        for source, metrics in source_metrics.items():
            result[source] = {
                "average_latency": statistics.mean(metrics["latencies"]) if metrics["latencies"] else 0,
                "average_quality": statistics.mean(metrics["qualities"]) if metrics["qualities"] else 0,
                "signal_count": len(metrics["latencies"])
            }
        
        return result
    
    def _get_source_reliability(self) -> Dict[str, float]:
        """獲取來源可靠性（模擬）"""
        reliability_scores = {
            "binance": 0.98,
            "coinbase": 0.96,
            "kraken": 0.94,
            "huobi": 0.92,
            "unknown": 0.80
        }
        
        return {
            source: reliability_scores.get(source, 0.85)
            for source in self.source_distribution.keys()
        }
    
    def _analyze_hourly_patterns(self) -> Dict[str, Any]:
        """分析小時模式"""
        hourly_performance = defaultdict(lambda: {"count": 0, "quality_sum": 0, "latency_sum": 0})
        
        for signal in self.signal_history:
            hour = signal.timestamp.hour
            hourly_performance[hour]["count"] += 1
            hourly_performance[hour]["quality_sum"] += signal.quality_score
            hourly_performance[hour]["latency_sum"] += signal.processing_latency
        
        patterns = {}
        for hour, data in hourly_performance.items():
            if data["count"] > 0:
                patterns[f"hour_{hour:02d}"] = {
                    "signal_count": data["count"],
                    "average_quality": data["quality_sum"] / data["count"],
                    "average_latency": data["latency_sum"] / data["count"]
                }
        
        return patterns
    
    def _analyze_daily_patterns(self) -> Dict[str, Any]:
        """分析日模式"""
        daily_performance = defaultdict(lambda: {"count": 0, "quality_sum": 0, "latency_sum": 0})
        
        for signal in self.signal_history:
            weekday = signal.timestamp.weekday()  # 0=Monday, 6=Sunday
            daily_performance[weekday]["count"] += 1
            daily_performance[weekday]["quality_sum"] += signal.quality_score
            daily_performance[weekday]["latency_sum"] += signal.processing_latency
        
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        patterns = {}
        
        for day_num, data in daily_performance.items():
            if data["count"] > 0:
                day_name = weekdays[day_num]
                patterns[day_name] = {
                    "signal_count": data["count"],
                    "average_quality": data["quality_sum"] / data["count"],
                    "average_latency": data["latency_sum"] / data["count"]
                }
        
        return patterns
    
    def _identify_peak_windows(self) -> List[Dict[str, Any]]:
        """識別高峰時段"""
        # 基於歷史數據識別信號量和質量的高峰時段
        hourly_stats = self._analyze_hourly_patterns()
        
        if not hourly_stats:
            return []
        
        # 找出信號量最多的時段
        peak_volume_hours = sorted(
            hourly_stats.items(),
            key=lambda x: x[1]["signal_count"],
            reverse=True
        )[:3]
        
        # 找出質量最高的時段
        peak_quality_hours = sorted(
            hourly_stats.items(),
            key=lambda x: x[1]["average_quality"],
            reverse=True
        )[:3]
        
        return [
            {
                "type": "peak_volume",
                "hours": [hour for hour, _ in peak_volume_hours],
                "description": "信號量最高的時段"
            },
            {
                "type": "peak_quality",
                "hours": [hour for hour, _ in peak_quality_hours],
                "description": "信號質量最高的時段"
            }
        ]
    
    def _calculate_performance_benchmarks(self) -> Dict[str, Any]:
        """計算性能基準"""
        if not self.signal_history:
            return {}
        
        # 計算各種基準指標
        all_latencies = [s.processing_latency for s in self.signal_history]
        all_qualities = [s.quality_score for s in self.signal_history]
        
        return {
            "throughput_benchmarks": {
                "signals_per_minute": len(self.signal_history) / max((datetime.now() - min(s.timestamp for s in self.signal_history)).total_seconds() / 60, 1),
                "target_throughput": 60,  # 目標每分鐘60個信號
                "efficiency_ratio": min(1.0, (len(self.signal_history) / 60) / max(1, (datetime.now() - min(s.timestamp for s in self.signal_history)).total_seconds() / 60))
            },
            "quality_benchmarks": {
                "average_quality": statistics.mean(all_qualities),
                "target_quality": 0.8,
                "quality_achievement_rate": len([q for q in all_qualities if q >= 0.8]) / len(all_qualities)
            },
            "latency_benchmarks": {
                "average_latency": statistics.mean(all_latencies),
                "target_latency": 500,  # 目標500ms
                "latency_compliance_rate": len([l for l in all_latencies if l <= 500]) / len(all_latencies)
            }
        }
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """獲取實時指標"""
        current_time = datetime.now()
        recent_cutoff = current_time - timedelta(minutes=5)
        
        recent_signals = [s for s in self.signal_history if s.timestamp > recent_cutoff]
        
        if not recent_signals:
            return {
                "real_time_status": "no_recent_data",
                "timestamp": current_time.isoformat()
            }
        
        return {
            "real_time_status": "active",
            "timestamp": current_time.isoformat(),
            "recent_5min_metrics": {
                "signal_count": len(recent_signals),
                "average_quality": statistics.mean([s.quality_score for s in recent_signals]),
                "average_latency": statistics.mean([s.processing_latency for s in recent_signals]),
                "priority_distribution": {
                    priority: len([s for s in recent_signals if s.priority == priority])
                    for priority in set(s.priority for s in recent_signals)
                }
            },
            "processing_rate": {
                "signals_per_minute": len(recent_signals),
                "target_rate": 12,  # 目標每5分鐘60個信號
                "performance_ratio": len(recent_signals) / 12
            }
        }

# 全局實例
signal_statistics = SignalProcessingStatistics()
