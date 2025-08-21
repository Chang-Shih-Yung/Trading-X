#!/usr/bin/env python3
"""
資料庫存儲策略與極端情況分析器
===============================

分析長期運行下的資料庫存儲策略、數據保留機制，
以及Phase1-5對黑天鵝事件和極端市場情況的處理能力。
"""

import os
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

class DatabaseStorageAnalyzer:
    """資料庫存儲與極端情況分析器"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent / "X"
        
        # 數據存儲估算
        self.data_categories = {
            "market_data": {
                "description": "市場數據 (OHLCV)",
                "symbols": 7,
                "timeframes": ["1m", "5m", "15m", "1h", "4h", "1d"],
                "record_size_bytes": 150,  # 每筆記錄大小
                "retention_days": 365,     # 保留天數
                "priority": "高"
            },
            "signal_data": {
                "description": "信號數據",
                "daily_signals": 840,     # 正常市場每日信號數
                "record_size_bytes": 500, # 每個信號記錄大小
                "retention_days": 180,    # 保留天數
                "priority": "高"
            },
            "learning_records": {
                "description": "學習記錄 (Phase2)",
                "daily_records": 12,      # 每2小時一次
                "record_size_bytes": 2048, # 每次學習記錄大小
                "retention_days": 365,    # 保留天數
                "priority": "中"
            },
            "backtest_results": {
                "description": "回測結果 (Phase5)",
                "daily_records": 1,       # 每24小時一次
                "record_size_bytes": 10240, # 每次回測記錄大小
                "retention_days": 365,    # 保留天數
                "priority": "中"
            },
            "performance_metrics": {
                "description": "性能指標",
                "daily_records": 1440,    # 每分鐘記錄
                "record_size_bytes": 200, # 每筆記錄大小
                "retention_days": 90,     # 保留天數
                "priority": "低"
            },
            "extreme_events": {
                "description": "極端事件記錄",
                "monthly_events": 5,      # 每月極端事件
                "record_size_bytes": 5120, # 詳細事件記錄
                "retention_days": 1095,   # 3年保留
                "priority": "極高"
            }
        }
        
        # 極端情況定義
        self.extreme_scenarios = {
            "flash_crash": {
                "definition": "閃崩 - 短時間內價格暴跌>10%",
                "frequency": "每年2-3次",
                "impact_level": "高",
                "detection_threshold": {"price_drop_percent": 10, "time_window_minutes": 5}
            },
            "black_swan": {
                "definition": "黑天鵝 - 極低機率但影響巨大的事件",
                "frequency": "每2-3年1次",
                "impact_level": "極高",
                "detection_threshold": {"price_change_percent": 30, "volume_spike": 10}
            },
            "liquidity_crisis": {
                "definition": "流動性危機 - 交易量急劇萎縮",
                "frequency": "每年1-2次",
                "impact_level": "中高",
                "detection_threshold": {"volume_drop_percent": 70, "spread_increase": 5}
            },
            "circuit_breaker": {
                "definition": "熔斷機制觸發",
                "frequency": "每年3-5次",
                "impact_level": "中",
                "detection_threshold": {"halt_duration_minutes": 15}
            },
            "whale_manipulation": {
                "definition": "巨鯨操縱 - 大額訂單影響價格",
                "frequency": "每月2-3次",
                "impact_level": "中",
                "detection_threshold": {"order_size_ratio": 0.1, "price_impact": 3}
            }
        }
    
    def calculate_storage_requirements(self) -> Dict[str, Any]:
        """計算存儲需求"""
        storage_analysis = {}
        total_daily_mb = 0
        total_annual_gb = 0
        
        for category, config in self.data_categories.items():
            if category == "market_data":
                # 市場數據計算
                daily_records = 0
                for timeframe in config["timeframes"]:
                    if timeframe == "1m":
                        daily_records += 1440 * config["symbols"]  # 每分鐘 * 7幣種
                    elif timeframe == "5m":
                        daily_records += 288 * config["symbols"]   # 每5分鐘 * 7幣種
                    elif timeframe == "15m":
                        daily_records += 96 * config["symbols"]    # 每15分鐘 * 7幣種
                    elif timeframe == "1h":
                        daily_records += 24 * config["symbols"]    # 每小時 * 7幣種
                    elif timeframe == "4h":
                        daily_records += 6 * config["symbols"]     # 每4小時 * 7幣種
                    elif timeframe == "1d":
                        daily_records += 1 * config["symbols"]     # 每日 * 7幣種
            else:
                daily_records = config.get("daily_records", config.get("monthly_events", 1) * 30 if "monthly_events" in config else 1)
            
            daily_size_mb = (daily_records * config["record_size_bytes"]) / 1024 / 1024
            retention_size_mb = daily_size_mb * config["retention_days"]
            annual_size_gb = (daily_size_mb * 365) / 1024
            
            storage_analysis[category] = {
                "description": config["description"],
                "daily_records": daily_records,
                "daily_size_mb": round(daily_size_mb, 2),
                "retention_size_mb": round(retention_size_mb, 2),
                "annual_size_gb": round(annual_size_gb, 2),
                "retention_days": config["retention_days"],
                "priority": config["priority"]
            }
            
            total_daily_mb += daily_size_mb
            total_annual_gb += annual_size_gb
        
        storage_analysis["summary"] = {
            "total_daily_mb": round(total_daily_mb, 2),
            "total_annual_gb": round(total_annual_gb, 2),
            "5_year_projection_gb": round(total_annual_gb * 5, 2),
            "storage_growth_rate": "線性增長，需要分層存儲策略"
        }
        
        return storage_analysis
    
    def design_tiered_storage_strategy(self) -> Dict[str, Any]:
        """設計分層存儲策略"""
        return {
            "hot_storage": {
                "description": "熱存儲 - 本地SSD",
                "data_types": ["最近30天市場數據", "最近7天信號數據", "當前學習參數"],
                "retention": "30天",
                "access_speed": "毫秒級",
                "estimated_size": "5-10GB",
                "technology": "SQLite + JSON files"
            },
            "warm_storage": {
                "description": "溫存儲 - 本地硬盤",
                "data_types": ["30-365天歷史數據", "學習記錄", "回測結果"],
                "retention": "1年",
                "access_speed": "秒級",
                "estimated_size": "50-100GB",
                "technology": "壓縮數據庫"
            },
            "cold_storage": {
                "description": "冷存儲 - 雲端或外部硬盤",
                "data_types": ["1年以上歷史數據", "極端事件完整記錄"],
                "retention": "永久保存",
                "access_speed": "分鐘級",
                "estimated_size": "無限制",
                "technology": "雲端存儲 + 本地備份"
            },
            "compression_strategy": {
                "market_data": "時間序列壓縮 (70-80%壓縮率)",
                "signal_data": "JSON壓縮 (60-70%壓縮率)",
                "learning_records": "增量存儲 (50-60%壓縮率)",
                "extreme_events": "無壓縮 (保持完整性)"
            },
            "cleanup_automation": {
                "daily_cleanup": "清理臨時文件和日誌",
                "weekly_cleanup": "壓縮溫存儲數據",
                "monthly_cleanup": "遷移到冷存儲",
                "annual_cleanup": "極端事件歸檔"
            }
        }
    
    def analyze_extreme_event_handling(self) -> Dict[str, Any]:
        """分析極端事件處理機制"""
        
        # 檢查各Phase對極端情況的處理
        phase_analysis = {
            "phase1a_signal_generation": {
                "extreme_detection": {
                    "price_volatility_filter": "檢測異常波動並調整信號閾值",
                    "volume_anomaly_detection": "識別異常成交量模式", 
                    "correlation_breakdown": "監測幣種間相關性突變",
                    "implementation_status": "需要檢查實際代碼"
                },
                "protection_mechanisms": [
                    "動態信號閾值調整",
                    "多時間框架驗證", 
                    "成交量確認機制",
                    "相關性檢查"
                ]
            },
            "phase2_adaptive_learning": {
                "extreme_learning": {
                    "outlier_detection": "學習過程中排除極端數據點",
                    "model_stability": "防止極端事件破壞學習模型",
                    "parameter_bounds": "參數調整範圍限制",
                    "implementation_status": "需要檢查學習引擎"
                },
                "protection_mechanisms": [
                    "學習數據清洗",
                    "參數變化限制",
                    "模型穩定性監控",
                    "異常學習回滾"
                ]
            },
            "phase3_decision_engine": {
                "risk_management": {
                    "position_sizing_limits": "極端情況下的倉位限制",
                    "correlation_monitoring": "相關性風險監控",
                    "market_regime_detection": "市場制度突變檢測",
                    "implementation_status": "需要檢查決策邏輯"
                },
                "protection_mechanisms": [
                    "緊急停損機制",
                    "倉位緊急平倉",
                    "交易暫停邏輯",
                    "風險預警系統"
                ]
            },
            "phase4_execution": {
                "execution_protection": {
                    "slippage_monitoring": "滑點異常監控",
                    "liquidity_check": "流動性檢查",
                    "order_validation": "訂單有效性驗證",
                    "implementation_status": "需要檢查執行模組"
                },
                "protection_mechanisms": [
                    "訂單大小限制",
                    "執行時間限制",
                    "流動性門檻檢查",
                    "緊急取消機制"
                ]
            },
            "phase5_backtest_validation": {
                "historical_stress_testing": {
                    "black_swan_simulation": "黑天鵝事件回測",
                    "crisis_period_analysis": "危機期間表現分析",
                    "drawdown_analysis": "最大回撤分析",
                    "implementation_status": "Lean回測包含部分極端情況"
                },
                "protection_mechanisms": [
                    "極端情況回測驗證",
                    "壓力測試機制",
                    "風險指標監控",
                    "策略穩健性評估"
                ]
            }
        }
        
        return phase_analysis
    
    def check_existing_extreme_protection(self) -> Dict[str, Any]:
        """檢查現有的極端情況保護機制"""
        
        # 基於我們之前看到的代碼，分析現有保護
        existing_protections = {
            "data_validation": {
                "json_file_locks": "✅ 已實現 - 防止併發讀寫corruption",
                "parameter_range_validation": "✅ 已實現 - Phase2參數範圍限制",
                "configuration_integrity": "✅ 已實現 - 配置文件完整性檢查"
            },
            "learning_stability": {
                "parameter_bounds": "✅ 已實現 - Phase2參數調整範圍限制",
                "learning_confidence": "✅ 已實現 - 學習信心度評估",
                "conflict_resolution": "✅ 已實現 - Phase2/Phase5參數衝突處理"
            },
            "signal_filtering": {
                "multi_timeframe_validation": "✅ 已實現 - H4+D1投票+W1閘門",
                "lean_similarity_matching": "✅ 已實現 - 歷史相似度比對",
                "confidence_thresholds": "✅ 已實現 - 多層信心閾值"
            },
            "performance_monitoring": {
                "rollback_mechanism": "✅ 已實現 - Phase2性能下降自動回滾",
                "performance_tracking": "✅ 已實現 - 持續性能監控",
                "boost_optimization": "✅ 已實現 - 性能提升機制"
            },
            "missing_protections": {
                "flash_crash_detection": "❌ 缺少 - 需要價格突變檢測",
                "liquidity_crisis_handling": "❌ 缺少 - 需要流動性監控",
                "volume_anomaly_detection": "❌ 缺少 - 需要成交量異常檢測",
                "correlation_breakdown_alert": "❌ 缺少 - 需要相關性監控",
                "emergency_shutdown": "❌ 缺少 - 需要緊急停止機制"
            }
        }
        
        return existing_protections
    
    def recommend_extreme_protection_enhancements(self) -> Dict[str, Any]:
        """推薦極端情況保護增強機制"""
        
        return {
            "immediate_enhancements": {
                "flash_crash_detector": {
                    "description": "閃崩檢測器",
                    "trigger": "5分鐘內跌幅>10%",
                    "action": "暫停新信號生成，縮小倉位",
                    "implementation": "Phase1A添加價格突變檢測"
                },
                "volume_anomaly_monitor": {
                    "description": "成交量異常監控",
                    "trigger": "成交量異常(>5倍或<20%正常值)",
                    "action": "降低信號權重，增加確認要求",
                    "implementation": "Phase1A添加成交量統計分析"
                },
                "correlation_breakdown_alert": {
                    "description": "相關性崩潰警報",
                    "trigger": "幣種間相關性突變>50%",
                    "action": "切換到單幣種模式",
                    "implementation": "Phase2添加相關性監控"
                }
            },
            "advanced_enhancements": {
                "market_regime_classifier": {
                    "description": "市場制度分類器",
                    "regimes": ["正常", "波動", "危機", "恢復"],
                    "action": "根據制度調整所有參數",
                    "implementation": "Phase5添加制度識別ML模型"
                },
                "stress_testing_framework": {
                    "description": "壓力測試框架",
                    "scenarios": ["2008金融危機", "2020疫情崩盤", "加密貨幣熊市"],
                    "action": "定期驗證策略在極端情況下的表現",
                    "implementation": "Phase5增強歷史壓力測試"
                },
                "emergency_shutdown_system": {
                    "description": "緊急停止系統",
                    "triggers": ["系統性風險", "技術故障", "監管變化"],
                    "action": "自動平倉、停止交易、發送警報",
                    "implementation": "全系統緊急控制機制"
                }
            },
            "data_protection_enhancements": {
                "extreme_event_logger": {
                    "description": "極端事件詳細記錄器",
                    "content": "完整市場快照、系統響應、影響分析",
                    "retention": "永久保存",
                    "implementation": "專用極端事件數據庫"
                },
                "backup_strategy": {
                    "description": "多重備份策略",
                    "local_backup": "本地RAID冗餘",
                    "cloud_backup": "實時雲端同步",
                    "offline_backup": "定期離線備份"
                }
            }
        }
    
    def generate_comprehensive_analysis(self):
        """生成綜合分析報告"""
        print("🗄️  資料庫存儲策略與極端情況分析")
        print("=" * 70)
        
        # 1. 存儲需求分析
        print("📊 存儲需求分析:")
        storage_req = self.calculate_storage_requirements()
        
        print(f"   💾 每日數據量: {storage_req['summary']['total_daily_mb']:.1f} MB")
        print(f"   📈 年度數據量: {storage_req['summary']['total_annual_gb']:.1f} GB")
        print(f"   🚀 5年預估: {storage_req['summary']['5_year_projection_gb']:.1f} GB")
        print()
        
        print("   📋 各類數據詳情:")
        for category, data in storage_req.items():
            if category != "summary":
                print(f"     📌 {data['description']}:")
                print(f"       每日: {data['daily_size_mb']:.1f}MB ({data['daily_records']}筆)")
                print(f"       保留: {data['retention_days']}天 ({data['retention_size_mb']:.1f}MB)")
                print(f"       優先級: {data['priority']}")
        print()
        
        # 2. 分層存儲策略
        print("🏗️  分層存儲策略設計:")
        storage_strategy = self.design_tiered_storage_strategy()
        
        for tier, config in storage_strategy.items():
            if tier != "compression_strategy" and tier != "cleanup_automation":
                print(f"   🔥 {config['description']}:")
                print(f"     數據類型: {', '.join(config['data_types'])}")
                print(f"     保留期: {config['retention']}")
                print(f"     訪問速度: {config['access_speed']}")
                print(f"     預估大小: {config['estimated_size']}")
                print(f"     技術方案: {config['technology']}")
        
        print(f"   🗜️  壓縮策略:")
        for data_type, compression in storage_strategy["compression_strategy"].items():
            print(f"     • {data_type}: {compression}")
        
        print(f"   🧹 自動清理:")
        for cleanup_type, action in storage_strategy["cleanup_automation"].items():
            print(f"     • {cleanup_type}: {action}")
        print()
        
        # 3. 極端情況定義
        print("⚡ 極端情況定義與檢測:")
        for scenario, config in self.extreme_scenarios.items():
            print(f"   🚨 {config['definition']}:")
            print(f"     頻率: {config['frequency']}")
            print(f"     影響: {config['impact_level']}")
            if 'detection_threshold' in config:
                thresholds = ', '.join([f"{k}:{v}" for k, v in config['detection_threshold'].items()])
                print(f"     檢測閾值: {thresholds}")
        print()
        
        # 4. 現有保護機制檢查
        print("🛡️  現有極端情況保護機制:")
        existing = self.check_existing_extreme_protection()
        
        for category, protections in existing.items():
            if category != "missing_protections":
                category_name = {
                    "data_validation": "數據驗證",
                    "learning_stability": "學習穩定性", 
                    "signal_filtering": "信號過濾",
                    "performance_monitoring": "性能監控"
                }[category]
                
                print(f"   ✅ {category_name}:")
                for protection, status in protections.items():
                    print(f"     {status} {protection}")
        
        print(f"   ❌ 缺少的保護機制:")
        for protection, status in existing["missing_protections"].items():
            print(f"     {status} {protection}")
        print()
        
        # 5. Phase分析
        print("🔍 各Phase極端情況處理能力:")
        phase_analysis = self.analyze_extreme_event_handling()
        
        for phase, analysis in phase_analysis.items():
            phase_name = phase.replace('_', ' ').title()
            print(f"   📍 {phase_name}:")
            
            # 顯示檢測能力
            if 'extreme_detection' in analysis:
                print(f"     檢測能力:")
                for detection, desc in analysis['extreme_detection'].items():
                    if detection != 'implementation_status':
                        print(f"       • {desc}")
                print(f"     實現狀態: {analysis['extreme_detection']['implementation_status']}")
            
            # 顯示保護機制
            print(f"     保護機制: {', '.join(analysis['protection_mechanisms'][:2])}...")
        print()
        
        # 6. 推薦增強機制
        print("💡 推薦極端情況保護增強:")
        recommendations = self.recommend_extreme_protection_enhancements()
        
        print(f"   🚀 立即增強 (高優先級):")
        for enhancement, config in recommendations["immediate_enhancements"].items():
            print(f"     🔧 {config['description']}:")
            print(f"       觸發條件: {config['trigger']}")
            print(f"       響應動作: {config['action']}")
        
        print(f"   🎯 進階增強 (中優先級):")
        for enhancement, config in recommendations["advanced_enhancements"].items():
            print(f"     🛠️  {config['description']}: {config['action']}")
        print()
        
        # 7. 總結與建議
        print("🎯 總結與建議:")
        print("=" * 40)
        
        annual_gb = storage_req['summary']['total_annual_gb']
        if annual_gb > 500:
            storage_risk = "高風險"
            storage_action = "必須實施分層存儲"
        elif annual_gb > 100:
            storage_risk = "中風險"
            storage_action = "建議實施壓縮和清理"
        else:
            storage_risk = "低風險"
            storage_action = "定期監控即可"
        
        print(f"📊 存儲風險評估: {storage_risk}")
        print(f"   年度數據量: {annual_gb:.1f}GB")
        print(f"   建議行動: {storage_action}")
        
        missing_count = len(existing["missing_protections"])
        if missing_count > 3:
            protection_risk = "高風險"
        elif missing_count > 1:
            protection_risk = "中風險"
        else:
            protection_risk = "低風險"
        
        print(f"⚡ 極端情況保護: {protection_risk}")
        print(f"   缺少機制: {missing_count} 個")
        print(f"   建議: 優先實施閃崩檢測和流動性監控")
        
        print(f"\n💎 最終建議:")
        print(f"   1. 立即實施分層存儲策略，避免本地存儲爆滿")
        print(f"   2. 優先添加閃崩檢測和成交量異常監控")
        print(f"   3. 建立極端事件專用數據庫，永久保存學習案例")
        print(f"   4. 實施自動備份和緊急停止機制")
        print(f"   5. 定期進行歷史極端事件壓力測試")

def main():
    analyzer = DatabaseStorageAnalyzer()
    analyzer.generate_comprehensive_analysis()

if __name__ == "__main__":
    main()
