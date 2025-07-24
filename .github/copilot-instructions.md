<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Trading X 系統 Copilot 指示

## 專案概述

這是一個進階的交易策略系統，專注於加密貨幣市場的技術分析和自動化交易信號生成。

## 代碼風格與標準

- 使用 Python 3.9+ 和 FastAPI 框架
- 遵循 PEP 8 代碼風格
- 使用 Type Hints 進行類型標註
- 採用異步編程模式 (async/await)
- 使用 Pydantic 進行數據驗證

## 核心技術指標實現

當生成技術指標相關代碼時，請：

1. 使用 TA-Lib 或 pandas_ta 庫
2. 實現多時間框架分析
3. 包含信號強度計算
4. 添加適當的錯誤處理
5. 支援動態參數調整

## 交易信號邏輯

- 實現多重確認機制
- 計算精確的盈虧比 (Risk/Reward Ratio)
- 包含止損和止盈邏輯
- 支援不同市場條件的策略調整

## 數據處理原則

- 使用 pandas 進行數據處理
- 實現數據快取機制
- 處理缺失數據和異常值
- 支援實時和歷史數據

## API 設計

- 使用 RESTful API 設計
- 實現適當的錯誤回應
- 添加請求驗證和限流
- 支援分頁和排序

## 測試與質量

- 為所有核心功能編寫單元測試
- 使用 pytest 測試框架
- 實現回測驗證
- 添加性能監控

## 安全考量

- 妥善處理 API 金鑰
- 實現請求認證
- 添加輸入驗證
- 記錄安全相關事件

## 性能優化

- 使用異步數據庫操作
- 實現智能快取策略
- 優化數據庫查詢
- 支援水平擴展
