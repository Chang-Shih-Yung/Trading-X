"""
🎯 Trading X - 測試腳本初始化
測試資料夾結構說明
"""

# 測試目錄結構
TESTS_STRUCTURE = {
    "unit/": "單元測試 - 測試個別函數和類別",
    "integration/": "整合測試 - 測試組件間的互動",
    "flow/": "流程測試 - 測試完整業務流程",
    "performance/": "性能測試 - 測試系統性能和負載"
}

# 測試分類標準
TEST_CATEGORIES = {
    "UNIT": {
        "description": "單元測試",
        "scope": "個別函數、方法、類別",
        "isolation": "完全隔離，使用模擬數據",
        "execution_time": "< 1秒",
        "examples": [
            "test_signal_priority_enum.py",
            "test_data_integrity_status.py", 
            "test_signal_candidate_creation.py",
            "test_epl_decision_logic.py"
        ]
    },
    "INTEGRATION": {
        "description": "整合測試",
        "scope": "組件間互動",
        "isolation": "部分隔離，測試真實整合",
        "execution_time": "< 10秒",
        "examples": [
            "test_engine_manager_integration.py",
            "test_api_monitoring_integration.py",
            "test_notification_integration.py"
        ]
    },
    "FLOW": {
        "description": "流程測試",
        "scope": "完整業務流程",
        "isolation": "端到端測試，模擬真實場景",
        "execution_time": "< 30秒",
        "examples": [
            "test_complete_signal_flow.py",
            "test_monitoring_lifecycle.py",
            "test_notification_workflow.py"
        ]
    },
    "PERFORMANCE": {
        "description": "性能測試",
        "scope": "系統性能和負載",
        "isolation": "壓力測試環境",
        "execution_time": "1-5分鐘",
        "examples": [
            "test_signal_processing_performance.py",
            "test_concurrent_monitoring.py",
            "test_memory_usage.py"
        ]
    }
}

# 測試執行順序
EXECUTION_ORDER = [
    "unit",      # 先執行單元測試
    "integration",  # 再執行整合測試
    "flow",      # 然後執行流程測試
    "performance"   # 最後執行性能測試
]

# 測試報告格式
REPORT_FORMAT = {
    "timestamp": "執行時間",
    "category": "測試分類",
    "total_tests": "總測試數",
    "passed": "通過數量",
    "failed": "失敗數量",
    "skipped": "跳過數量",
    "duration": "執行時長",
    "coverage": "覆蓋率",
    "details": "詳細結果"
}

def get_test_info():
    """獲取測試資訊"""
    return {
        "structure": TESTS_STRUCTURE,
        "categories": TEST_CATEGORIES,
        "execution_order": EXECUTION_ORDER,
        "report_format": REPORT_FORMAT
    }
