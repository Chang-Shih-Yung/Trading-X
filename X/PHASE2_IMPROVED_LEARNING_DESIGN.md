# Phase2 分層學習機制設計

## 🎯 問題分析

當前 Phase2 學習機制存在以下問題：

1. **時間混合問題**：1 小時前的信號和 1 天前的信號權重相同
2. **幣種混合問題**：BTC、ETH、DOGE 等不同特性的幣種信號混合學習
3. **市場環境混合**：不同市場制度下的信號被統一處理
4. **缺乏優先級**：所有信號平等對待，無法突出重要信號

## 🔄 改進方案

### 方案一：時間加權分層學習

```python
class TimeWeightedLearning:
    def calculate_signal_weight(self, signal_timestamp: datetime) -> float:
        """根據時間計算信號權重"""
        time_diff = datetime.now() - signal_timestamp
        hours_ago = time_diff.total_seconds() / 3600

        if hours_ago <= 1:
            return 1.0  # 最高權重
        elif hours_ago <= 6:
            return 0.8  # 較高權重
        elif hours_ago <= 24:
            return 0.5  # 中等權重
        elif hours_ago <= 72:
            return 0.3  # 較低權重
        else:
            return 0.1  # 最低權重
```

### 方案二：幣種分類學習

```python
class CoinCategoryLearning:
    def __init__(self):
        self.coin_categories = {
            'major': ['BTCUSDT', 'ETHUSDT'],      # 主流幣：穩定性優先
            'alt': ['BNBUSDT', 'ADAUSDT', 'SOLUSDT'],  # 主流替代幣：平衡策略
            'meme': ['DOGEUSDT'],                 # Meme幣：高風險高收益
            'defi': ['XRPUSDT']                   # DeFi/支付幣：特殊策略
        }

    def get_category_specific_params(self, category: str) -> dict:
        """針對不同類別的幣種使用不同參數"""
        if category == 'major':
            return {
                'signal_threshold': 0.65,     # 較高門檻，追求穩定
                'risk_multiplier': 0.8,       # 保守風險
                'momentum_weight': 1.0        # 標準動量
            }
        elif category == 'meme':
            return {
                'signal_threshold': 0.55,     # 較低門檻，捕捉機會
                'risk_multiplier': 1.2,       # 積極風險
                'momentum_weight': 1.3        # 強調動量
            }
        # ... 其他類別
```

### 方案三：市場制度感知學習

```python
class MarketRegimeAwareLearning:
    def __init__(self):
        self.market_regimes = ['bull', 'bear', 'sideways', 'volatile']
        self.regime_params = {}  # 每個制度下的最佳參數

    def detect_current_regime(self) -> str:
        """檢測當前市場制度"""
        # 基於市場指標判斷當前制度
        pass

    def get_regime_signals(self, regime: str, lookback_hours: int = 24) -> List[SignalPerformance]:
        """獲取特定市場制度下的信號"""
        current_time = datetime.now()
        regime_signals = []

        for signal in self.signal_history:
            signal_regime = self._detect_signal_regime(signal)
            time_diff = (current_time - signal.timestamp).total_seconds() / 3600

            if signal_regime == regime and time_diff <= lookback_hours:
                regime_signals.append(signal)

        return regime_signals
```

## 🎲 推薦實施策略

### 階段一：時間衰減權重（立即實施）

```python
def evaluate_performance_with_time_weight(self) -> float:
    """基於時間衰減的性能評估"""
    weighted_scores = []
    current_time = datetime.now()

    for signal in self.signal_history[-50:]:  # 最近50個信號
        time_weight = self._calculate_time_weight(signal.timestamp, current_time)
        if signal.performance_score:
            weighted_scores.append(signal.performance_score * time_weight)

    return np.average(weighted_scores) if weighted_scores else 0.0

def _calculate_time_weight(self, signal_time: datetime, current_time: datetime) -> float:
    """計算時間權重：越近期權重越高"""
    hours_ago = (current_time - signal_time).total_seconds() / 3600
    return np.exp(-hours_ago / 12)  # 12小時半衰期
```

### 階段二：幣種分群學習（1 週內實施）

```python
def optimize_parameters_by_category(self):
    """按幣種類別分別優化參數"""
    for category, symbols in self.coin_categories.items():
        category_signals = [
            s for s in self.signal_history
            if s.symbol in symbols
        ]

        if len(category_signals) >= 20:  # 最少20個信號才進行分類優化
            category_params = self._optimize_for_category(category_signals)
            self.category_params[category] = category_params
            logger.info(f"✅ {category} 類別參數優化完成")
```

### 階段三：動態權重系統（1 個月內實施）

```python
class DynamicWeightLearning:
    def calculate_comprehensive_weight(self, signal: SignalPerformance) -> float:
        """計算綜合權重"""
        time_weight = self._calculate_time_weight(signal.timestamp)
        category_weight = self._calculate_category_weight(signal.symbol)
        performance_weight = self._calculate_performance_weight(signal)
        market_weight = self._calculate_market_weight(signal)

        return time_weight * category_weight * performance_weight * market_weight
```

## 📊 實施效果預期

1. **短期（1 週）**：時間衰減機制減少過時信號影響
2. **中期（1 月）**：幣種分類學習提升不同類型幣種表現
3. **長期（3 月）**：綜合權重系統實現精準參數調整

## 🔧 監控指標

```python
learning_metrics = {
    'time_weight_distribution': '時間權重分布',
    'category_performance': '各類別表現',
    'regime_adaptation': '市場制度適應度',
    'parameter_stability': '參數穩定性'
}
```
