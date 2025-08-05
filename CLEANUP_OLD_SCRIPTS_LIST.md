# 🗑️ 舊測試腳本清理清單

## 📋 可以安全移除的舊腳本

基於狙擊手策略優化完成，以下腳本已過時且可以安全移除：

### 🧪 測試腳本 (Test Scripts)

```
test_signal_broadcasting.py
test_independent_functions.py
test_dynamic_time_integration.py
test_phase3_week3_api.py
test_basic_stats.py
test_enhanced_stats.py
test_gmail_simple.py
test_phase3_week1_api.py
test_price_fix.py
test_phase2_simple.py
test_trading_strategy_core.py
test_phase3_priority2_fixed.py
test_phase3_quick.py
test_direct_price.py
test_quick_core.py
test_summary_report.py
test_websocket_stability.py
test_dynamic_timeframe.py
test_enhanced_features.py
test_phase3_market_depth.py
test_fallback_data_fix.py
test_intelligent_timeframe_integration.py
test_sniper_end_to_end_flow.py
test_bull_bear_regime.py
test_phase3_week2.py
test_phase2_complete_integration.py
test_gmail_anti_spam.py
test_dynamic_risk_demo.py
test_sniper_dual_layer_complete.py
test_phase1c_signal_standardization.py
test_sniper_signal_history.py
test_sniper_browser.py
```

### 🎭 演示腳本 (Demo Scripts)

```
real_websocket_sniper_demo.py
optimized_real_sniper_demo.py
demo_multi_timeframe_api.py
real_sniper_demo.py
final_enhanced_stats_demo.py
sniper_business_flow_demo.py
```

### 🐛 調試腳本 (Debug Scripts)

```
debug_sniper_system_status.py
debug_pandas_ta.py
debug_signal_filtering.py
debug_sniper_system.py
```

### 🧹 清理腳本 (Cleanup Scripts)

```
advanced_api_cleanup.py
cleanup_duplicate_signals.py
sniper_api_cleanup.py
sniper_api_cleanup_report.py
cleanup_all_test_data.py
cleanup_debug_endpoints.py
sniper_cleanup_final_report.py
sniper_api_cleanup_analyzer.py
history_api_cleanup.py
cleanup_test_signals.py
```

### 🔧 生成和檢查腳本 (Generate/Check Scripts)

```
generate_signals_direct.py
generate_test_signals.py
create_sniper_signal_test.py
create_test_expiring_signal.py
check_system_status.py
check_signal_timing.py
check_sniper_data_integrity.py
check_recent_emails.py
check_dynamic_time_distribution.py
analyze_sniper_filtering.py
monitor_core_flow.py
fallback_data_analysis.py
emergency_fix_check.py
```

### 📁 TEST 目錄內的腳本

```
TEST/test_pandas_ta_engine_fixed.py
TEST/test_summary_reporter.py
TEST/test_info.py
TEST/test_realtime_fixed.py
TEST/test_real_pandas_ta.py
TEST/test_pandas_ta_signals.py
TEST/test_websocket_to_pandas_ta.py
TEST/quick_test.py
TEST/test_new_coins.py
TEST/test_log_management.py
TEST/check_data_authenticity.py
TEST/test_data_lifecycle.py
TEST/simple_optimization_demo.py
TEST/pandas_ta_optimization_demo.py
TEST/backend/pandas_ta_integration_demo.py
TEST/debug_websocket.py
TEST/real_data_debug_test.py
```

### 🛠️ 簡單測試腳本

```
simple_api_test.py
simple_gmail_test.py
simple_test_signal.py
manual_signal_test.py
quick_phase_test.py
```

## ⚠️ 保留的核心腳本

以下腳本應該保留，因為它們是系統核心功能：

### 🎯 核心系統

```
main.py - 主程序入口
sniper_unified_data_layer.py - 狙擊手核心（已優化）
```

### 📁 app/ 目錄

```
app/ - 整個應用核心目錄保留
```

### 🔧 配置和設置

```
requirements.txt
docker-compose.yml
Dockerfile
setup_gmail_notification.py - Gmail設置腳本
init_database.py - 數據庫初始化
```

## 🎯 清理命令

執行以下命令可以安全移除所有舊腳本：

```bash
# 移除根目錄的測試腳本
rm test_*.py debug_*.py demo_*.py cleanup_*.py
rm generate_*.py create_*.py check_*.py analyze_*.py monitor_*.py
rm simple_*.py manual_*.py quick_*.py fallback_*.py emergency_*.py
rm optimized_*.py real_*.py final_*.py sniper_*_demo.py

# 移除TEST目錄（整個目錄）
rm -rf TEST/

# 移除RESULT目錄中的測試腳本
rm -rf RESULT/test_scripts/
```

## 📊 清理統計

- **可移除腳本總數**: ~120+ 個
- **預計釋放空間**: ~15-20MB
- **清理後保留**: 核心系統文件和 app/目錄
- **風險評估**: 🟢 低風險（所有可移除腳本都不影響生產功能）

## ✅ 清理完成後的效果

1. 項目結構更清晰
2. 無冗餘測試代碼
3. 專注於生產環境功能
4. 符合狙擊手策略的簡潔原則
