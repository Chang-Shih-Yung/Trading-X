#!/usr/bin/env python3
"""
相關性崩潰檢測系統
監控幣種間相關性變化，檢測市場結構性改變
"""

import asyncio
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging
import requests
from itertools import combinations

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CorrelationMonitor:
    """相關性監控器"""
    
    def __init__(self):
        self.symbols = ["XRPUSDT", "DOGEUSDT", "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"]
        self.correlation_threshold = 0.3  # 相關性變化閾值
        self.calculation_periods = [7, 14, 30]  # 計算週期（天）
        self.price_data = {}
        self.correlation_history = {}
        # 修正為動態路徑
        self.base_dir = Path(__file__).parent.parent.parent
        self.events_file = self.base_dir / "data" / "correlation_events.json"
        self.events_file.parent.mkdir(exist_ok=True)
        
    async def get_historical_prices(self, symbol: str, days: int = 30) -> Optional[pd.DataFrame]:
        """獲取歷史價格數據"""
        try:
            # 使用Binance Kline API獲取歷史數據
            end_time = int(datetime.now().timestamp() * 1000)
            start_time = end_time - (days * 24 * 60 * 60 * 1000)
            
            url = f"https://api.binance.com/api/v3/klines"
            params = {
                "symbol": symbol,
                "interval": "1h",  # 1小時K線
                "startTime": start_time,
                "endTime": end_time,
                "limit": days * 24
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if not data:
                return None
            
            # 轉換為DataFrame
            df = pd.DataFrame(data, columns=[
                "timestamp", "open", "high", "low", "close", "volume",
                "close_time", "quote_volume", "count", "taker_buy_volume",
                "taker_buy_quote_volume", "ignore"
            ])
            
            # 轉換數據類型
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df["close"] = df["close"].astype(float)
            df["volume"] = df["volume"].astype(float)
            
            # 計算價格變化
            df["price_change"] = df["close"].pct_change()
            
            return df[["timestamp", "close", "volume", "price_change"]].dropna()
            
        except Exception as e:
            logger.error(f"獲取 {symbol} 歷史價格失敗: {e}")
            return None
    
    async def load_all_price_data(self) -> bool:
        """載入所有幣種的價格數據"""
        logger.info("開始載入所有幣種價格數據...")
        
        for symbol in self.symbols:
            price_data = await self.get_historical_prices(symbol)
            if price_data is not None:
                self.price_data[symbol] = price_data
                logger.info(f"載入 {symbol} 數據: {len(price_data)} 個數據點")
            else:
                logger.warning(f"無法載入 {symbol} 價格數據")
            
            # 避免API頻率限制
            await asyncio.sleep(0.2)
        
        return len(self.price_data) >= 2
    
    def calculate_correlation_matrix(self, period_days: int) -> Optional[pd.DataFrame]:
        """計算相關性矩陣"""
        if len(self.price_data) < 2:
            return None
        
        try:
            # 準備價格變化數據
            price_changes = {}
            min_length = float('inf')
            
            for symbol, data in self.price_data.items():
                if len(data) >= period_days * 20:  # 確保有足夠數據
                    recent_data = data.tail(period_days * 20)  # 取最近的數據
                    price_changes[symbol] = recent_data["price_change"].values
                    min_length = min(min_length, len(price_changes[symbol]))
            
            if len(price_changes) < 2 or min_length < 50:
                return None
            
            # 對齊數據長度
            aligned_data = {}
            for symbol, changes in price_changes.items():
                aligned_data[symbol] = changes[-min_length:]
            
            # 創建DataFrame並計算相關性
            df = pd.DataFrame(aligned_data)
            correlation_matrix = df.corr()
            
            return correlation_matrix
            
        except Exception as e:
            logger.error(f"計算相關性矩陣失敗: {e}")
            return None
    
    def detect_correlation_breakdown(self, 
                                   current_corr: pd.DataFrame, 
                                   historical_corr: pd.DataFrame) -> List[Dict[str, Any]]:
        """檢測相關性崩潰"""
        breakdowns = []
        
        try:
            for symbol1 in current_corr.index:
                for symbol2 in current_corr.columns:
                    if symbol1 >= symbol2:  # 避免重複檢查
                        continue
                    
                    current_value = current_corr.loc[symbol1, symbol2]
                    historical_value = historical_corr.loc[symbol1, symbol2]
                    
                    # 檢查是否有效數值
                    if pd.isna(current_value) or pd.isna(historical_value):
                        continue
                    
                    correlation_change = abs(current_value - historical_value)
                    
                    # 如果相關性變化超過閾值
                    if correlation_change > self.correlation_threshold:
                        
                        breakdown_type = "breakdown"
                        if current_value > historical_value:
                            breakdown_type = "increase"
                        else:
                            breakdown_type = "decrease"
                        
                        event = {
                            "event_id": f"corr_{symbol1}_{symbol2}_{int(datetime.now().timestamp())}",
                            "symbol_pair": f"{symbol1},{symbol2}",
                            "breakdown_type": breakdown_type,
                            "normal_correlation": round(historical_value, 4),
                            "breakdown_correlation": round(current_value, 4),
                            "correlation_change": round(correlation_change, 4),
                            "change_percentage": round((correlation_change / abs(historical_value)) * 100 if historical_value != 0 else 0, 2),
                            "severity": self._assess_severity(correlation_change),
                            "detected_at": datetime.now().isoformat(),
                            "market_impact": self._assess_market_impact(symbol1, symbol2, correlation_change)
                        }
                        
                        breakdowns.append(event)
            
            return breakdowns
            
        except Exception as e:
            logger.error(f"檢測相關性崩潰失敗: {e}")
            return []
    
    def _assess_severity(self, correlation_change: float) -> str:
        """評估嚴重程度"""
        if correlation_change > 0.7:
            return "critical"
        elif correlation_change > 0.5:
            return "high"
        elif correlation_change > 0.3:
            return "medium"
        else:
            return "low"
    
    def _assess_market_impact(self, symbol1: str, symbol2: str, correlation_change: float) -> Dict[str, Any]:
        """評估市場影響"""
        
        # 主要幣種權重
        major_coins = {"BTCUSDT": 0.4, "ETHUSDT": 0.3, "BNBUSDT": 0.2}
        
        impact_score = 0
        if symbol1 in major_coins:
            impact_score += major_coins[symbol1]
        if symbol2 in major_coins:
            impact_score += major_coins[symbol2]
        
        # 根據相關性變化調整影響分數
        impact_score *= correlation_change
        
        impact_level = "low"
        if impact_score > 0.4:
            impact_level = "critical"
        elif impact_score > 0.3:
            impact_level = "high"
        elif impact_score > 0.2:
            impact_level = "medium"
        
        return {
            "impact_level": impact_level,
            "impact_score": round(impact_score, 3),
            "involves_major_coins": bool(symbol1 in major_coins or symbol2 in major_coins),
            "potential_contagion": impact_score > 0.3
        }
    
    async def save_correlation_event(self, event: Dict[str, Any]):
        """保存相關性事件"""
        try:
            events = []
            if self.events_file.exists():
                with open(self.events_file, 'r', encoding='utf-8') as f:
                    events = json.load(f)
            
            events.append(event)
            
            # 保留最近500個事件
            if len(events) > 500:
                events = events[-500:]
            
            with open(self.events_file, 'w', encoding='utf-8') as f:
                json.dump(events, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"相關性事件已保存: {event['event_id']}")
            
        except Exception as e:
            logger.error(f"保存相關性事件失敗: {e}")
    
    def get_correlation_summary(self, correlation_matrix: pd.DataFrame) -> Dict[str, Any]:
        """獲取相關性摘要"""
        try:
            # 提取上三角矩陣（避免重複計算）
            upper_triangle = np.triu(correlation_matrix.values, k=1)
            correlations = upper_triangle[upper_triangle != 0]
            
            return {
                "average_correlation": round(np.mean(correlations), 4),
                "max_correlation": round(np.max(correlations), 4),
                "min_correlation": round(np.min(correlations), 4),
                "correlation_std": round(np.std(correlations), 4),
                "strong_correlations": int(np.sum(correlations > 0.7)),
                "weak_correlations": int(np.sum(abs(correlations) < 0.3)),
                "negative_correlations": int(np.sum(correlations < 0)),
                "total_pairs": len(correlations)
            }
            
        except Exception as e:
            logger.error(f"計算相關性摘要失敗: {e}")
            return {}
    
    async def monitor_correlations(self) -> Dict[str, Any]:
        """監控相關性變化"""
        logger.info("開始相關性監控...")
        
        # 載入價格數據
        if not await self.load_all_price_data():
            return {"error": "無法載入足夠的價格數據"}
        
        results = {
            "monitoring_completed": False,
            "correlation_matrices": {},
            "correlation_summaries": {},
            "breakdown_events": [],
            "total_breakdown_events": 0
        }
        
        try:
            # 計算不同時期的相關性矩陣
            for period in self.calculation_periods:
                corr_matrix = self.calculate_correlation_matrix(period)
                if corr_matrix is not None:
                    results["correlation_matrices"][f"{period}d"] = corr_matrix.to_dict()
                    results["correlation_summaries"][f"{period}d"] = self.get_correlation_summary(corr_matrix)
            
            # 檢測相關性崩潰（比較7天和30天）
            if "7d" in results["correlation_matrices"] and "30d" in results["correlation_matrices"]:
                current_corr = pd.DataFrame(results["correlation_matrices"]["7d"])
                historical_corr = pd.DataFrame(results["correlation_matrices"]["30d"])
                
                breakdown_events = self.detect_correlation_breakdown(current_corr, historical_corr)
                
                # 保存事件
                for event in breakdown_events:
                    await self.save_correlation_event(event)
                
                results["breakdown_events"] = breakdown_events
                results["total_breakdown_events"] = len(breakdown_events)
            
            results["monitoring_completed"] = True
            results["timestamp"] = datetime.now().isoformat()
            
            return results
            
        except Exception as e:
            logger.error(f"相關性監控失敗: {e}")
            results["error"] = str(e)
            return results

async def test_correlation_monitor():
    """測試相關性監控系統"""
    print("🔍 測試相關性崩潰檢測系統...")
    
    monitor = CorrelationMonitor()
    
    # 執行相關性監控
    results = await monitor.monitor_correlations()
    
    if results.get("monitoring_completed"):
        print(f"✅ 相關性監控完成")
        
        # 顯示相關性摘要
        print(f"\n📊 相關性摘要:")
        for period, summary in results["correlation_summaries"].items():
            print(f"   {period} 週期:")
            print(f"     平均相關性: {summary.get('average_correlation', 'N/A')}")
            print(f"     強相關性對數: {summary.get('strong_correlations', 0)}")
            print(f"     弱相關性對數: {summary.get('weak_correlations', 0)}")
        
        # 顯示崩潰事件
        print(f"\n⚠️  相關性崩潰事件: {results['total_breakdown_events']} 個")
        for event in results["breakdown_events"][:5]:  # 顯示前5個
            print(f"   {event['symbol_pair']}: {event['breakdown_type']}")
            print(f"     變化: {event['normal_correlation']} → {event['breakdown_correlation']}")
            print(f"     嚴重程度: {event['severity']}")
            print(f"     市場影響: {event['market_impact']['impact_level']}")
        
        if results['total_breakdown_events'] > 5:
            print(f"   ... 還有 {results['total_breakdown_events'] - 5} 個事件")
    
    else:
        print(f"❌ 監控失敗: {results.get('error', '未知錯誤')}")
    
    print(f"\n✅ 相關性監控系統測試完成")
    return results

if __name__ == "__main__":
    asyncio.run(test_correlation_monitor())
