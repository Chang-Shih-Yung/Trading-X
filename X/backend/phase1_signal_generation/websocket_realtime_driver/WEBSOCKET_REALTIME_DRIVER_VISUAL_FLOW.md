# 🌊 WebSocket Realtime Driver v2.0 現有架構視覺化流程

## 📡 **完整數據處理流程 - 從即時價格到Phase1**

```mermaid
flowchart TD
    subgraph "📡 數據接收層"
        A[Binance WebSocket] --> D[ConnectionManager]
        B[OKX WebSocket] --> D
        C[Bybit WebSocket] --> D
        D --> E[MessageProcessor]
    end
    
    subgraph "🔍 Layer 1: 數據驗證"
        E --> F[DataValidator]
        F --> F1{時間戳驗證}
        F --> F2{價格合理性檢查}
        F --> F3{跨交易所價格驗證}
        F1 --> G{驗證通過?}
        F2 --> G
        F3 --> G
        G -->|❌| H[標記異常但保留]
        G -->|✅| I[Layer 2 清理]
    end
    
    subgraph "🧹 Layer 2: 數據清理"
        I --> J[DataCleaner]
        J --> J1[離群值檢測]
        J --> J2[缺失值處理]  
        J --> J3[去重邏輯]
        J1 --> K[DataStandardizer]
        J2 --> K
        J3 --> K
    end
    
    subgraph "📏 Layer 3: 數據標準化"
        K --> K1[價格標準化]
        K --> K2[成交量標準化]
        K --> K3[時間標準化]
        K --> K4[market_depth生成]
        K1 --> L[BasicComputationEngine]
        K2 --> L
        K3 --> L
        K4 --> L
    end
    
    subgraph "🔢 Layer 4: 基礎計算"
        L --> L1[價格指標計算]
        L --> L2[成交量指標計算] 
        L --> L3[流動性指標計算]
        L1 --> M[EventBroadcaster]
        L2 --> M
        L3 --> M
    end
    
    subgraph "📢 Layer 5: 事件廣播"
        M --> M1[real_time_price廣播]
        M --> M2[market_depth廣播]
        M --> M3[technical_indicators廣播]
        M1 --> N[路由分發]
        M2 --> N
        M3 --> N
    end
    
    subgraph "🎯 Layer 6: 智能路由"
        N --> N1[Phase1A基礎信號生成]
        N --> N2[指標依賴圖更新]
        N --> N3[Phase1B波動率適應]
        N --> N4[統一信號候選池]
    end
    
    subgraph "⚡ 並行處理系統"
        O[智能觸發引擎] --> O1{每1秒檢查}
        O1 --> O2[技術指標收斂檢測]
        O1 --> O3[高勝率信號檢測]
        O1 --> O4[關鍵時刻檢測]
        
        O2 --> P{勝率評估}
        O3 --> P
        O4 --> Q[緊急優先級]
        
        P --> P1[🔥 75%+ 高勝率]
        P --> P2[⚡ 40-75% 中勝率]
        P --> P3[🚫 <40% 過濾]
        
        P1 --> R[Phase1 信號生成]
        P2 --> R
        Q --> R
    end
    
    N1 --> R
    N2 --> R
    N3 --> R  
    N4 --> R
    
    R --> S[Phase2 市場環境分析]
    S --> T[Phase3 執行政策決策]
    T --> U[Phase4 統一監控儀表板]
    U --> V[📱 用戶看到結果]
    
    style A fill:#e3f2fd
    style B fill:#e3f2fd  
    style C fill:#e3f2fd
    style D fill:#fff3e0
    style G fill:#fff3e0
    style O1 fill:#ffebee
    style P1 fill:#e8f5e8
    style P2 fill:#fff8e1
    style P3 fill:#fce4ec
    style Q fill:#ffcdd2
    style V fill:#f3e5f5
```

## 🔍 **詳細判斷邏輯流程**

### **📊 數據驗證層 (Layer 1) 判斷邏輯**

```mermaid
flowchart TD
    A[收到原始數據] --> B{時間戳檢查}
    B -->|時間戳 > 5秒前| C[❌ 數據過舊]
    B -->|時間戳正常| D{價格合理性檢查}
    
    D -->|價格變化 > 10%| E[❌ 價格異常]
    D -->|價格合理| F{跨交易所驗證}
    
    F -->|價差 > 5%| G[❌ 交易所價差異常]
    F -->|價差正常| H[✅ 驗證通過]
    
    C --> I[標記異常但保留數據]
    E --> I
    G --> I
    H --> J[進入清理層]
    I --> J
    
    style H fill:#c8e6c9
    style I fill:#ffcccb
```

### **🧹 數據清理層 (Layer 2) 處理邏輯**

```mermaid
flowchart TD
    A[接收驗證後數據] --> B[離群值檢測]
    B --> C{Z-Score檢測}
    C -->|Z-Score > 3| D[標記為離群值]
    C -->|Z-Score正常| E[缺失值檢查]
    
    E --> F{是否有缺失值?}
    F -->|有缺失| G[使用最後有效值填充]
    F -->|無缺失| H[去重檢查]
    
    H --> I{與最近5條數據比較}
    I -->|相同時間戳+相同價格| J[標記為重複]
    I -->|數據唯一| K[✅ 清理完成]
    
    D --> K
    G --> K
    J --> K
    K --> L[進入標準化層]
    
    style K fill:#c8e6c9
```

### **📏 標準化層 (Layer 3) 處理邏輯**

```mermaid
flowchart TD
    A[接收清理後數據] --> B{數據類型判斷}
    
    B -->|kline_data| C[價格標準化]
    B -->|orderbook_data| D[市場深度處理]
    B -->|real_time_trades| E[交易數據標準化]
    
    C --> F[計算價格變化百分比]
    C --> G[Min-Max縮放到[0,1]]
    
    D --> H[計算買賣價差]
    D --> I[生成market_depth輸出]
    
    E --> J[標準化成交量]
    E --> K[計算交易強度]
    
    F --> L[BasicComputationEngine]
    G --> L
    H --> L
    I --> L
    J --> L
    K --> L
    
    style L fill:#e1f5fe
```

### **🔢 基礎計算層 (Layer 4) 計算邏輯**

```mermaid
flowchart TD
    A[接收標準化數據] --> B{計算類型選擇}
    
    B -->|價格數據| C[計算價格指標]
    B -->|成交量數據| D[計算成交量指標]
    B -->|訂單簿數據| E[計算流動性指標]
    
    C --> F[price_momentum計算]
    C --> G[rolling_volatility計算]
    
    D --> H[volume_trend計算]
    D --> I[volume_anomaly檢測]
    
    E --> J[bid_ask_spread計算]
    E --> K[book_depth計算]
    E --> L[liquidity_ratio計算]
    
    F --> M[EventBroadcaster]
    G --> M
    H --> M
    I --> M
    J --> M
    K --> M
    L --> M
    
    style M fill:#fff3e0
```

### **📢 事件廣播層 (Layer 5) 路由邏輯**

```mermaid
flowchart TD
    A[接收計算結果] --> B{事件類型判斷}
    
    B -->|kline_data完成| C[生成real_time_price事件]
    B -->|orderbook_data完成| D[生成market_depth事件]
    B -->|指標計算完成| E[生成technical_indicators事件]
    
    C --> F[廣播給所有訂閱者]
    D --> F
    E --> F
    
    F --> G[分發到路由目標]
    G --> H[Phase1A基礎信號生成]
    G --> I[指標依賴圖更新]
    G --> J[Phase1B波動率適應]
    G --> K[統一信號候選池]
    
    style F fill:#fff8e1
    style G fill:#e8f5e8
```

### **🎯 路由分發層 (Layer 6) 決策邏輯**

```mermaid
flowchart TD
    A[接收廣播事件] --> B{數據類型路由}
    
    B -->|kline_data<br/>real_time_trades| C[路由到Phase1A]
    B -->|orderbook_data<br/>mark_price| D[路由到Phase1B]
    B -->|所有數據類型| E[路由到統一池]
    B -->|指標更新| F[路由到依賴圖]
    
    C --> G[Phase1A: 基礎信號生成]
    G --> H[計算基礎指標]
    H --> I[生成信號候選者]
    
    D --> J[Phase1B: 波動率適應]
    J --> K[計算波動率指標]
    K --> L[生成適應參數]
    
    E --> M[統一信號候選池]
    M --> N[數據品質評分]
    N --> O[信號聚合]
    
    F --> P[指標依賴圖更新]
    P --> Q[更新依賴關係]
    
    I --> R[Phase1完成]
    L --> R
    O --> R
    Q --> R
    
    style R fill:#c8e6c9
```

## ⚡ **並行高勝率檢測流程**

### **🏆 智能觸發引擎邏輯**

```mermaid
flowchart TD
    A[每1秒觸發檢查] --> B[從記憶體快取獲取最新數據]
    B --> C{技術指標收斂檢測}
    
    C --> D[RSI檢查]
    C --> E[MACD檢查]  
    C --> F[EMA趨勢檢查]
    
    D --> G{RSI < 30 或 RSI > 70?}
    E --> H{MACD信號線交叉?}
    F --> I{EMA趨勢明確?}
    
    G -->|是| J[多頭/空頭條件1滿足]
    H -->|是| K[多頭/空頭條件2滿足]
    I -->|是| L[多頭/空頭條件3滿足]
    
    J --> M{至少3個指標收斂?}
    K --> M
    L --> M
    
    M -->|是| N[觸發收斂信號]
    M -->|否| O[等待下次檢查]
    
    N --> P[歷史勝率查詢]
    P --> Q{勝率 >= 75%?}
    Q -->|是| R[🔥 高勝率信號]
    Q -->|否| S{勝率 >= 40%?}
    S -->|是| T[⚡ 中勝率信號]
    S -->|否| U[🚫 過濾信號]
    
    R --> V[立即觸發Phase1]
    T --> W[特別標記觸發Phase1]
    U --> O
    
    style R fill:#c8e6c9
    style T fill:#fff8e1
    style U fill:#ffcccb
```

## 📊 **完整性能監控指標**

```
🚀 實時性能指標:
├── 🔄 數據接收頻率: 100ms/次
├── ⚡ 6層處理延遲: <3ms總計
├── 📡 廣播延遲: <1ms
└── 🎯 端到端延遲: <12ms

📈 數據品質指標:  
├── ✅ 驗證通過率: >95%
├── 🧹 清理有效率: >98%
├── 📏 標準化成功率: >99%
└── 🔢 計算準確率: >99.9%

🏆 高勝率檢測指標:
├── 🔍 收斂檢測準確率: >85%
├── 🎯 勝率預測準確率: >80%
├── ⚡ 觸發響應時間: <1秒
└── 🚫 假陽性率: <15%

🎛️ 系統穩定性指標:
├── 🔌 連接穩定性: >99.5%
├── 💾 記憶體使用率: <80%
├── 🖥️ CPU使用率: <70%
└── 🔄 重連成功率: >95%
```

---

**🔑 核心優勢:**
1. **📡 多交易所並行**: Binance + OKX + Bybit 同時連接
2. **⚡ 超低延遲**: 6層處理管道總延遲 <3ms
3. **🔍 智能驗證**: 多層數據品質檢查與異常處理
4. **🏆 勝率優化**: 並行高勝率信號檢測系統
5. **🎯 精準路由**: 基於數據類型的智能分發機制
6. **📊 實時監控**: 全方位性能與品質指標追蹤
