#!/usr/bin/env python3
"""
狙擊手API清理建議報告
"""

print("🧹 狙擊手API清理建議")
print("=" * 60)

# 核心流程API - 必須保留
CORE_APIS = [
    "dashboard-precision-signals",  # 前端主要API
    "sniper-unified-data-layer",   # 前端數據源
    "pandas-ta-direct",            # 技術分析
    "signals",                     # 基礎信號
    "expired",                     # 過期信號
    "history/signals",             # 歷史記錄
    "status",                      # 系統狀態
]

# 測試/調試API - 可以移除
DEBUG_APIS = [
    "debug-active-signals",
    "test-email-notification", 
    "create-test-signal",
    "clear-all-signals",
    "active-signals-simple",
]

# 複雜功能API - 暫時可移除
COMPLEX_APIS = [
    "force-precision-refresh",
    "process-expired", 
    "cleanup-expired",
    "create-market-event",
    "execute-reallocation",
    "start-monitoring",
    "stop-monitoring",
    "event-predictions",
    "phase1a-signal-scoring",
    "phase1b-enhanced-signal-scoring",
    "impact-assessment",
]

print(f"✅ 保留核心API: {len(CORE_APIS)} 個")
for api in CORE_APIS:
    print(f"  - {api}")

print(f"\n🗑️ 建議移除: {len(DEBUG_APIS + COMPLEX_APIS)} 個")
print("  調試API:")
for api in DEBUG_APIS:
    print(f"    - {api}")
    
print("  複雜功能API:")
for api in COMPLEX_APIS[:5]:
    print(f"    - {api}")
print(f"    ... 和其他 {len(COMPLEX_APIS) - 5} 個")

print("\n📋 清理步驟:")
print("1. 先備份現有API文件")
print("2. 創建精簡版API文件")  
print("3. 測試前端功能正常")
print("4. 逐步移除未使用端點")
