#!/usr/bin/env python3
"""
流動性監控系統
監控買賣價差、成交量異常、訂單簿深度等流動性指標
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging
import requests

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LiquidityLevel(str):
    """流動性水準"""
    VERY_LOW = "very_low"
    LOW = "low" 
    MEDIUM = "medium"
    HIGH = "high"

class LiquidityMonitor:
    """流動性監控器"""
    
    def __init__(self):
        self.monitoring_active = False
        self.symbols = ["XRPUSDT", "DOGEUSDT", "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"]
        self.liquidity_thresholds = {
            "spread_critical": 0.01,  # 1% 買賣價差為嚴重
            "spread_warning": 0.005,  # 0.5% 為警告
            "volume_drop_critical": 0.5,  # 成交量下降50%為嚴重
            "volume_drop_warning": 0.3,   # 成交量下降30%為警告
        }
        self.historical_data = {}
        self.current_events = {}
        # 修正為動態路徑
        self.base_dir = Path(__file__).parent.parent.parent
        self.events_file = self.base_dir / "data" / "liquidity_events.json"
        self.events_file.parent.mkdir(exist_ok=True)
        
    async def get_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """獲取市場數據"""
        try:
            # 獲取深度數據 (Order Book)
            depth_url = f"https://api.binance.com/api/v3/depth?symbol={symbol}&limit=20"
            depth_response = requests.get(depth_url, timeout=5)
            depth_data = depth_response.json()
            
            # 獲取24小時統計
            ticker_url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
            ticker_response = requests.get(ticker_url, timeout=5)
            ticker_data = ticker_response.json()
            
            # 計算買賣價差
            best_bid = float(depth_data["bids"][0][0]) if depth_data["bids"] else 0
            best_ask = float(depth_data["asks"][0][0]) if depth_data["asks"] else 0
            mid_price = (best_bid + best_ask) / 2 if best_bid and best_ask else 0
            spread = best_ask - best_bid
            spread_percentage = (spread / mid_price) * 100 if mid_price > 0 else 0
            
            # 計算訂單簿深度
            bid_depth = sum(float(bid[1]) for bid in depth_data["bids"][:10])
            ask_depth = sum(float(ask[1]) for ask in depth_data["asks"][:10])
            order_book_imbalance = (bid_depth - ask_depth) / (bid_depth + ask_depth) if (bid_depth + ask_depth) > 0 else 0
            
            return {
                "symbol": symbol,
                "timestamp": datetime.now(),
                "best_bid": best_bid,
                "best_ask": best_ask,
                "mid_price": mid_price,
                "spread": spread,
                "spread_percentage": spread_percentage,
                "volume_24h": float(ticker_data["volume"]),
                "quote_volume_24h": float(ticker_data["quoteVolume"]),
                "count_24h": int(ticker_data["count"]),
                "bid_depth": bid_depth,
                "ask_depth": ask_depth,
                "order_book_imbalance": order_book_imbalance,
                "price_change_24h": float(ticker_data["priceChangePercent"])
            }
            
        except Exception as e:
            logger.error(f"獲取 {symbol} 市場數據失敗: {e}")
            return None
    
    def analyze_liquidity_level(self, market_data: Dict[str, Any]) -> str:
        """分析流動性水準"""
        spread_pct = market_data["spread_percentage"]
        volume_24h = market_data["volume_24h"]
        bid_depth = market_data["bid_depth"]
        ask_depth = market_data["ask_depth"]
        
        # 基於買賣價差判斷
        if spread_pct > 1.0:  # >1%
            return LiquidityLevel.VERY_LOW
        elif spread_pct > 0.5:  # >0.5%
            return LiquidityLevel.LOW
        elif spread_pct > 0.2:  # >0.2%
            return LiquidityLevel.MEDIUM
        else:
            return LiquidityLevel.HIGH
    
    def detect_liquidity_crisis(self, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """檢測流動性危機"""
        symbol = market_data["symbol"]
        spread_pct = market_data["spread_percentage"]
        
        # 檢查是否觸發流動性危機閾值
        crisis_detected = False
        crisis_level = "normal"
        
        if spread_pct > self.liquidity_thresholds["spread_critical"]:
            crisis_detected = True
            crisis_level = "critical"
        elif spread_pct > self.liquidity_thresholds["spread_warning"]:
            crisis_detected = True
            crisis_level = "warning"
        
        if crisis_detected:
            event = {
                "event_id": f"liquidity_{symbol}_{int(time.time())}",
                "symbol": symbol,
                "crisis_level": crisis_level,
                "spread_percentage": spread_pct,
                "liquidity_level": self.analyze_liquidity_level(market_data),
                "market_data": market_data,
                "detected_at": datetime.now().isoformat(),
                "actions_recommended": self._get_recommended_actions(crisis_level, symbol)
            }
            
            return event
        
        return None
    
    def _get_recommended_actions(self, crisis_level: str, symbol: str) -> List[str]:
        """獲取建議採取的行動"""
        if crisis_level == "critical":
            return [
                f"立即暫停 {symbol} 交易",
                "增加風險等級到最高",
                "通知管理員立即介入",
                "監控其他相關幣種"
            ]
        elif crisis_level == "warning":
            return [
                f"提高 {symbol} 風險監控",
                "降低該幣種倉位",
                "增加監控頻率",
                "準備暫停交易"
            ]
        return []
    
    def update_historical_data(self, market_data: Dict[str, Any]):
        """更新歷史數據"""
        symbol = market_data["symbol"]
        if symbol not in self.historical_data:
            self.historical_data[symbol] = []
        
        # 保留最近1小時的數據 (假設每分鐘檢查一次)
        self.historical_data[symbol].append(market_data)
        if len(self.historical_data[symbol]) > 60:
            self.historical_data[symbol] = self.historical_data[symbol][-60:]
    
    def get_volume_trend(self, symbol: str) -> Optional[Dict[str, Any]]:
        """獲取成交量趨勢"""
        if symbol not in self.historical_data or len(self.historical_data[symbol]) < 2:
            return None
        
        recent_data = self.historical_data[symbol][-10:]  # 最近10個數據點
        older_data = self.historical_data[symbol][-20:-10] if len(self.historical_data[symbol]) >= 20 else []
        
        if not older_data:
            return None
        
        recent_avg_volume = sum(data["volume_24h"] for data in recent_data) / len(recent_data)
        older_avg_volume = sum(data["volume_24h"] for data in older_data) / len(older_data)
        
        volume_change_pct = ((recent_avg_volume - older_avg_volume) / older_avg_volume) * 100 if older_avg_volume > 0 else 0
        
        return {
            "symbol": symbol,
            "recent_avg_volume": recent_avg_volume,
            "older_avg_volume": older_avg_volume,
            "volume_change_pct": volume_change_pct,
            "trend": "increasing" if volume_change_pct > 5 else "decreasing" if volume_change_pct < -5 else "stable"
        }
    
    async def save_event(self, event: Dict[str, Any]):
        """保存流動性事件"""
        try:
            events = []
            if self.events_file.exists():
                with open(self.events_file, 'r', encoding='utf-8') as f:
                    events = json.load(f)
            
            events.append(event)
            
            # 保留最近1000個事件
            if len(events) > 1000:
                events = events[-1000:]
            
            with open(self.events_file, 'w', encoding='utf-8') as f:
                json.dump(events, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"流動性事件已保存: {event['event_id']}")
            
        except Exception as e:
            logger.error(f"保存流動性事件失敗: {e}")
    
    def get_current_status(self) -> Dict[str, Any]:
        """獲取當前流動性狀態"""
        return {
            "monitoring_active": self.monitoring_active,
            "monitored_symbols": self.symbols,
            "current_events_count": len(self.current_events),
            "current_events": list(self.current_events.keys()),
            "thresholds": self.liquidity_thresholds,
            "last_update": datetime.now().isoformat()
        }
    
    async def monitor_single_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        """監控單一幣種的流動性"""
        market_data = await self.get_market_data(symbol)
        if not market_data:
            return None
        
        # 更新歷史數據
        self.update_historical_data(market_data)
        
        # 檢測流動性危機
        crisis_event = self.detect_liquidity_crisis(market_data)
        if crisis_event:
            await self.save_event(crisis_event)
            self.current_events[crisis_event["event_id"]] = crisis_event
            logger.warning(f"檢測到流動性危機: {symbol} - {crisis_event['crisis_level']}")
        
        # 分析流動性水準
        liquidity_level = self.analyze_liquidity_level(market_data)
        
        # 獲取成交量趨勢
        volume_trend = self.get_volume_trend(symbol)
        
        return {
            "symbol": symbol,
            "liquidity_level": liquidity_level,
            "spread_percentage": market_data["spread_percentage"],
            "volume_24h": market_data["volume_24h"],
            "crisis_detected": crisis_event is not None,
            "crisis_level": crisis_event["crisis_level"] if crisis_event else "normal",
            "volume_trend": volume_trend,
            "timestamp": market_data["timestamp"].isoformat()
        }
    
    async def monitor_all_symbols(self) -> Dict[str, Any]:
        """監控所有幣種的流動性"""
        self.monitoring_active = True
        results = {}
        
        try:
            logger.info("開始流動性監控...")
            
            for symbol in self.symbols:
                result = await self.monitor_single_symbol(symbol)
                if result:
                    results[symbol] = result
                    
                # 避免API頻率限制
                await asyncio.sleep(0.1)
            
            return {
                "monitoring_completed": True,
                "symbols_monitored": len(results),
                "results": results,
                "current_status": self.get_current_status()
            }
            
        except Exception as e:
            logger.error(f"流動性監控失敗: {e}")
            return {"monitoring_completed": False, "error": str(e)}
        finally:
            self.monitoring_active = False

async def test_liquidity_monitor():
    """測試流動性監控系統"""
    print("🔍 測試流動性監控系統...")
    
    monitor = LiquidityMonitor()
    
    # 測試單一幣種監控
    print("\n📊 測試單一幣種監控 (BTCUSDT):")
    btc_result = await monitor.monitor_single_symbol("BTCUSDT")
    if btc_result:
        print(f"   流動性水準: {btc_result['liquidity_level']}")
        print(f"   買賣價差: {btc_result['spread_percentage']:.4f}%")
        print(f"   24h成交量: {btc_result['volume_24h']:,.0f}")
        print(f"   危機檢測: {btc_result['crisis_detected']}")
    
    # 測試全部幣種監控
    print(f"\n📈 測試全部幣種流動性監控:")
    all_results = await monitor.monitor_all_symbols()
    
    if all_results.get("monitoring_completed"):
        print(f"   監控完成: {all_results['symbols_monitored']} 個幣種")
        
        for symbol, data in all_results["results"].items():
            status = "🔴 危機" if data["crisis_detected"] else "🟢 正常"
            print(f"   {symbol}: {status} - 流動性 {data['liquidity_level']} - 價差 {data['spread_percentage']:.4f}%")
    
    # 顯示當前狀態
    print(f"\n📋 監控狀態:")
    status = monitor.get_current_status()
    print(f"   監控中: {status['monitoring_active']}")
    print(f"   當前事件: {status['current_events_count']}")
    print(f"   監控幣種: {len(status['monitored_symbols'])}")
    
    print(f"\n✅ 流動性監控系統測試完成")
    return all_results

if __name__ == "__main__":
    asyncio.run(test_liquidity_monitor())
