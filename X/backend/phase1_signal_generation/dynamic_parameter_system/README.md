# Trading X - Dynamic Parameter System

## 概述

這是一個為 Trading X 系統設計的動態參數引擎，能夠根據市場制度、交易時段和其他市場條件自動調整 Phase1-5 的信號生成參數，從而提高交易策略的適應性和效能。

## 系統架構

```
dynamic_parameter_system/
├── __init__.py                     # 模組初始化
├── dynamic_parameter_config.json   # 動態參數配置文件
├── dynamic_parameter_engine.py     # 核心引擎實現
├── test_dynamic_parameter_python.py # 測試套件
└── test_report.json               # 測試報告
```

## 核心功能

### 1. 市場制度檢測 (MarketRegimeDetector)

- **牛市趨勢 (BULL_TREND)**: 檢測上升趨勢市場
- **熊市趨勢 (BEAR_TREND)**: 檢測下降趨勢市場
- **橫盤整理 (SIDEWAYS)**: 檢測橫盤震盪市場
- **高波動 (VOLATILE)**: 檢測高波動市場

### 2. 交易時段檢測 (TradingSessionDetector)

- **美股時段 (US_MARKET)**: 09:30-16:00 EST
- **亞洲時段 (ASIA_MARKET)**: 09:00-15:00 JST
- **歐洲時段 (EUROPE_MARKET)**: 08:00-16:30 GMT
- **重疊時段 (OVERLAP_HOURS)**: 市場重疊的高流動性時段
- **非活躍時段 (OFF_HOURS)**: 主要市場閉市時段

### 3. 動態參數適配 (DynamicParameterAdapter)

根據市場條件自動調整以下參數：

#### Phase1 信號生成參數

- `confidence_threshold`: 信心度閾值 (基礎值: 0.75)
- `volume_surge_multiplier`: 成交量激增倍數 (基礎值: 1.0)

#### Phase2 預評估參數

- `similarity_threshold`: 相似度閾值 (基礎值: 0.85)
- `time_overlap_minutes`: 時間重疊窗口 (基礎值: 15 分鐘)

#### Phase3 執行策略參數

- `replacement_score_threshold`: 替換評分閾值 (基礎值: 0.75)
- `position_concentration_limit`: 倉位集中度限制 (基礎值: 0.30)

#### Phase5 回測驗證參數

- `confidence_threshold`: 回測信心度閾值 (基礎值: 0.8)

## 適配規則

### 市場制度適配

- **牛市**: 降低信心度門檻，增加交易機會
- **熊市**: 提高信心度門檻，加強風險控制
- **高波動**: 提高所有閾值，增強保護
- **橫盤**: 使用標準閾值

### 恐懼貪婪指數適配

- **極度恐懼 (0-20)**: 降低門檻，捕捉抄底機會
- **恐懼 (21-40)**: 適度降低門檻
- **中性 (41-59)**: 使用標準值
- **貪婪 (60-79)**: 適度提高門檻
- **極度貪婪 (80-100)**: 提高門檻，加強風險控制

### 交易時段適配

- **美股時段**: 提高敏感度，縮短時間窗口
- **重疊時段**: 最高敏感度，最短時間窗口
- **非活躍時段**: 降低敏感度，延長時間窗口

## 使用方式

### 基本使用

```python
from dynamic_parameter_system import create_dynamic_parameter_engine

# 創建引擎
engine = await create_dynamic_parameter_engine()

# 獲取Phase1動態參數
result = await engine.get_dynamic_parameters("phase1")

# 獲取單個參數值
confidence_threshold = await engine.get_parameter_value("phase1", "confidence_threshold")

# 獲取系統狀態
status = await engine.get_system_status()
```

### 進階使用

```python
# 使用自定義市場數據源
from dynamic_parameter_system import DynamicParameterEngine, MarketDataSource

class CustomMarketDataSource(MarketDataSource):
    async def get_current_market_data(self):
        # 實現自定義數據獲取邏輯
        pass

custom_source = CustomMarketDataSource()
engine = DynamicParameterEngine(config_path, custom_source)
```

## 測試與驗證

運行完整測試套件：

```bash
python test_dynamic_parameter_python.py
```

測試涵蓋：

- ✅ 引擎創建與初始化
- ✅ 市場制度檢測準確性
- ✅ 交易時段檢測正確性
- ✅ 參數適配邏輯驗證
- ✅ Phase1-5 整合測試
- ✅ 錯誤處理機制
- ✅ 邊界值保護驗證
- ✅ 數據流完整性檢查

## 配置說明

所有配置存儲在 `dynamic_parameter_config.json` 中，包括：

- 市場制度檢測規則
- 交易時段定義
- 參數適配規則
- 邊界值限制
- 系統配置

## 性能特點

- **實時響應**: 支持實時市場數據處理
- **容錯機制**: 完善的錯誤處理和邊界保護
- **可擴展性**: 模組化設計，易於擴展新的適配規則
- **配置驅動**: 所有規則通過 JSON 配置，無需修改代碼
- **類型安全**: 完整的 Type Hints 支持

## 系統要求

- Python 3.9+
- 依賴項: `pytz`, `asyncio`
- 可選: 實時市場數據 API 接入

## 開發狀態

- ✅ JSON 配置系統完成
- ✅ 核心引擎實現完成
- ✅ 全面測試套件完成
- ✅ Phase1-5 整合驗證完成
- 🔄 準備整合到主系統

## 下一步整合計劃

1. **Phase1 整合**: 將動態參數系統整合到現有 Phase1 信號生成流程
2. **實時數據源**: 替換 MockMarketDataSource 為真實市場數據
3. **監控面板**: 添加動態參數調整的可視化監控
4. **性能優化**: 針對高頻交易場景進行性能調優
5. **策略回測**: 使用動態參數進行歷史策略回測驗證
