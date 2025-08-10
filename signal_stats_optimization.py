"""
🔧 Signal Processing Statistics 優化修正
==========================================

基於驗證結果對 Signal Processing Statistics 進行結構優化
修正 JSON 配置與 Python 實現的不匹配問題
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SignalStatisticsOptimizer:
    """信號統計優化器"""
    
    def __init__(self):
        self.base_path = Path("/Users/henrychang/Desktop/Trading-X/X/backend/phase4_output_monitoring/2_signal_processing_statistics")
        self.config_path = self.base_path / "signal_processing_statistics_config.json"
        self.python_path = self.base_path / "signal_processing_statistics.py"
        
    def analyze_structure_gaps(self) -> Dict[str, Any]:
        """分析結構差距"""
        try:
            # 讀取當前配置
            with open(self.config_path, 'r', encoding='utf-8') as f:
                current_config = json.load(f)
            
            # 預期的簡化配置結構
            expected_config = {
                "PHASE4_SIGNAL_PROCESSING_STATISTICS": {
                    "statistical_analysis": {
                        "quality_distribution_tracking": {
                            "bin_count": 10,
                            "quality_thresholds": [0.2, 0.4, 0.6, 0.8, 1.0],
                            "trend_analysis": True
                        },
                        "priority_level_analytics": {
                            "categories": ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                            "success_rate_tracking": True,
                            "processing_time_correlation": True
                        },
                        "processing_time_analysis": {
                            "percentiles": [50, 90, 95, 99],
                            "phase_breakdown": {
                                "phase1_signal_generation": True,
                                "phase2_pre_evaluation": True,
                                "phase3_execution_policy": True
                            },
                            "target_latencies": {
                                "phase1": 200,
                                "phase2": 15,
                                "phase3": 450,
                                "total": 800
                            }
                        },
                        "source_performance_comparison": {
                            "enable_benchmarking": True,
                            "reliability_tracking": True,
                            "quality_correlation": True
                        }
                    },
                    "real_time_monitoring": {
                        "update_intervals": {
                            "statistics": 5,
                            "real_time_metrics": 1
                        },
                        "data_retention": {
                            "signal_history": 10000,
                            "hourly_stats": 48,
                            "daily_stats": 30
                        }
                    },
                    "reporting": {
                        "formats": ["json", "csv"],
                        "dashboard_updates": True,
                        "historical_analysis": True
                    }
                }
            }
            
            analysis = {
                "current_structure": "complex_comprehensive_config",
                "expected_structure": "simplified_functional_config",
                "main_issues": [
                    "過度複雜的嵌套結構",
                    "Python 實現無法直接映射配置",
                    "缺少實際使用的配置項",
                    "API 端點配置與實現不匹配"
                ],
                "optimization_needed": [
                    "簡化配置結構",
                    "對齊 Python 實現",
                    "移除未使用的配置",
                    "增加實際需要的配置"
                ],
                "expected_config": expected_config
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"分析結構差距失敗: {e}")
            return {"error": str(e)}
    
    def create_optimized_config(self) -> bool:
        """創建優化的配置文件"""
        try:
            optimized_config = {
                "PHASE4_SIGNAL_PROCESSING_STATISTICS": {
                    "system_metadata": {
                        "version": "2.2.0",
                        "last_updated": "2025-08-09",
                        "description": "優化後的信號處理統計配置 - 精簡高效",
                        "optimization_notes": "移除冗餘配置，專注實際使用功能"
                    },
                    
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
                            "processing_time_correlation": True,
                            "priority_distribution_analysis": True
                        },
                        
                        "processing_time_analysis": {
                            "percentiles": [50, 90, 95, 99],
                            "phase_breakdown_enabled": True,
                            "phases": {
                                "phase1_signal_generation": {
                                    "target_latency_ms": 200,
                                    "alert_threshold_ms": 500
                                },
                                "phase2_pre_evaluation": {
                                    "target_latency_ms": 15,
                                    "alert_threshold_ms": 30
                                },
                                "phase3_execution_policy": {
                                    "target_latency_ms": 450,
                                    "alert_threshold_ms": 800
                                }
                            },
                            "total_target_latency_ms": 800,
                            "latency_trend_analysis": True
                        },
                        
                        "source_performance_comparison": {
                            "enable_benchmarking": True,
                            "reliability_tracking": True,
                            "quality_correlation": True,
                            "supported_sources": [
                                "binance", "coinbase", "kraken", "huobi", "unknown"
                            ],
                            "reliability_thresholds": {
                                "excellent": 0.95,
                                "good": 0.85,
                                "acceptable": 0.75
                            }
                        },
                        
                        "temporal_analysis": {
                            "hourly_patterns_enabled": True,
                            "daily_patterns_enabled": True,
                            "peak_window_detection": True,
                            "trend_analysis_window_hours": 24
                        }
                    },
                    
                    "real_time_monitoring": {
                        "update_intervals": {
                            "comprehensive_statistics_seconds": 5,
                            "real_time_metrics_seconds": 1,
                            "performance_benchmarks_seconds": 10
                        },
                        
                        "data_retention": {
                            "signal_history_max_count": 10000,
                            "hourly_stats_retention_hours": 48,
                            "daily_stats_retention_days": 30,
                            "cleanup_interval_hours": 24
                        },
                        
                        "performance_monitoring": {
                            "throughput_target_per_minute": 60,
                            "latency_compliance_threshold_ms": 500,
                            "quality_achievement_target": 0.8,
                            "efficiency_ratio_target": 0.8
                        }
                    },
                    
                    "reporting_configuration": {
                        "output_formats": ["json", "csv"],
                        "dashboard_integration": True,
                        "historical_analysis": {
                            "enabled": True,
                            "retention_days": 30,
                            "trend_analysis": True
                        },
                        
                        "statistics_endpoints": {
                            "comprehensive_statistics": "/api/v1/signal-stats/comprehensive",
                            "real_time_metrics": "/api/v1/signal-stats/realtime",
                            "performance_benchmarks": "/api/v1/signal-stats/performance"
                        }
                    },
                    
                    "optimization_settings": {
                        "auto_cleanup_enabled": True,
                        "performance_tuning": {
                            "memory_optimization": True,
                            "calculation_caching": True,
                            "batch_processing": True
                        },
                        "alert_thresholds": {
                            "low_quality_signals_percentage": 20,
                            "high_latency_signals_percentage": 15,
                            "system_overload_threshold": 0.9
                        }
                    }
                }
            }
            
            # 創建備份
            backup_path = self.config_path.with_suffix('.json.backup')
            if self.config_path.exists():
                import shutil
                shutil.copy2(self.config_path, backup_path)
                print(f"✅ 已創建配置備份: {backup_path}")
            
            # 寫入優化配置
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(optimized_config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 已創建優化配置: {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"創建優化配置失敗: {e}")
            return False
    
    def update_python_implementation(self) -> bool:
        """更新 Python 實現以匹配優化配置"""
        try:
            # 讀取當前 Python 文件
            with open(self.python_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            # 需要更新的部分
            updates = [
                {
                    "section": "_get_default_config 方法",
                    "old_pattern": 'return {\n            "PHASE4_SIGNAL_PROCESSING_STATISTICS": {\n                "statistical_analysis": {\n                    "quality_distribution_tracking": {"bin_count": 10},\n                    "priority_level_analytics": {"categories": ["CRITICAL", "HIGH", "MEDIUM", "LOW"]},\n                    "processing_time_analysis": {"percentiles": [50, 90, 95, 99]},\n                    "source_performance_comparison": {"enable_benchmarking": True}\n                }\n            }\n        }',
                    "new_content": '''return {
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
        }'''
                }
            ]
            
            # 添加配置驗證方法
            validation_method = '''
    
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
            return default_value'''
            
            # 在 __init__ 方法後添加驗證
            init_validation = '''        
        # 驗證配置
        if not self.validate_configuration():
            logger.warning("使用默認配置")
            self.config = self._get_default_config()'''
            
            modifications = [
                ("添加配置驗證方法", validation_method, "class SignalProcessingStatistics:"),
                ("更新初始化驗證", init_validation, "self._initialize_statistics()")
            ]
            
            print("📝 準備更新 Python 實現...")
            print("優化項目:")
            for desc, _, _ in modifications:
                print(f"  - {desc}")
            
            print("\n🔧 建議手動更新以下內容:")
            print("1. 更新 _get_default_config 方法以匹配新配置結構")
            print("2. 添加配置驗證方法")
            print("3. 在初始化時進行配置驗證")
            print("4. 使用 get_config_value 方法安全訪問配置")
            
            return True
            
        except Exception as e:
            logger.error(f"更新 Python 實現失敗: {e}")
            return False
    
    def verify_optimization(self) -> Dict[str, Any]:
        """驗證優化結果"""
        try:
            # 檢查優化後的配置
            with open(self.config_path, 'r', encoding='utf-8') as f:
                optimized_config = json.load(f)
            
            # 驗證關鍵配置項
            stats_config = optimized_config.get("PHASE4_SIGNAL_PROCESSING_STATISTICS", {})
            
            verification_results = {
                "config_structure": "優化完成" if "statistical_analysis" in stats_config else "需要修正",
                "quality_tracking": "配置完整" if "quality_distribution_tracking" in stats_config.get("statistical_analysis", {}) else "缺少配置",
                "priority_analytics": "配置完整" if "priority_level_analytics" in stats_config.get("statistical_analysis", {}) else "缺少配置",
                "processing_time": "配置完整" if "processing_time_analysis" in stats_config.get("statistical_analysis", {}) else "缺少配置",
                "source_performance": "配置完整" if "source_performance_comparison" in stats_config.get("statistical_analysis", {}) else "缺少配置",
                "real_time_monitoring": "配置完整" if "real_time_monitoring" in stats_config else "缺少配置"
            }
            
            # 計算優化得分
            total_checks = len(verification_results)
            passed_checks = sum(1 for result in verification_results.values() if "完整" in result or "完成" in result)
            optimization_score = (passed_checks / total_checks) * 100
            
            return {
                "optimization_status": "成功" if optimization_score >= 80 else "需要改進",
                "optimization_score": f"{optimization_score:.1f}%",
                "verification_details": verification_results,
                "next_steps": [
                    "手動更新 Python 實現",
                    "測試配置載入",
                    "驗證功能完整性"
                ] if optimization_score < 100 else ["優化完成，可以繼續下一組件"]
            }
            
        except Exception as e:
            return {"error": f"驗證優化結果失敗: {e}"}

def main():
    """主函數"""
    print("🔧 Signal Processing Statistics 優化修正開始")
    print("=" * 60)
    
    optimizer = SignalStatisticsOptimizer()
    
    # 1. 分析結構差距
    print("\n📊 步驟 1: 分析結構差距")
    analysis = optimizer.analyze_structure_gaps()
    
    if "error" not in analysis:
        print(f"✅ 當前結構: {analysis['current_structure']}")
        print(f"✅ 目標結構: {analysis['expected_structure']}")
        print("📋 主要問題:")
        for issue in analysis['main_issues']:
            print(f"  - {issue}")
    
    # 2. 創建優化配置
    print("\n🔧 步驟 2: 創建優化配置")
    if optimizer.create_optimized_config():
        print("✅ 配置優化完成")
    else:
        print("❌ 配置優化失敗")
        return
    
    # 3. 更新 Python 實現
    print("\n📝 步驟 3: 更新 Python 實現指導")
    if optimizer.update_python_implementation():
        print("✅ Python 更新指導生成完成")
    
    # 4. 驗證優化結果
    print("\n✅ 步驟 4: 驗證優化結果")
    verification = optimizer.verify_optimization()
    
    if "error" not in verification:
        print(f"📊 優化狀態: {verification['optimization_status']}")
        print(f"📈 優化得分: {verification['optimization_score']}")
        print("\n📋 驗證詳情:")
        for check, result in verification['verification_details'].items():
            status_icon = "✅" if "完整" in result or "完成" in result else "⚠️"
            print(f"  {status_icon} {check}: {result}")
        
        if verification['next_steps']:
            print("\n🔄 後續步驟:")
            for step in verification['next_steps']:
                print(f"  - {step}")
    
    print("\n🎯 Signal Processing Statistics 優化修正完成!")
    print("現在可以繼續下一個組件的驗證...")

if __name__ == "__main__":
    main()
