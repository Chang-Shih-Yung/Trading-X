"""
🎯 Trading X - 真實幣安數據即時監控
持續監控真實市場數據和信號生成
"""

import asyncio
import logging
from datetime import datetime
from binance_data_connector import binance_connector
from real_data_signal_quality_engine import real_data_engine

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealTimeMarketMonitor:
    """即時市場監控器"""
    
    def __init__(self, symbol: str = "BTCUSDT", interval: int = 30):
        self.symbol = symbol
        self.interval = interval  # 監控間隔（秒）
        self.running = False
        self.signal_history = []
    
    async def start_monitoring(self):
        """開始監控"""
        self.running = True
        print(f"🚀 開始監控 {self.symbol} 真實市場數據...")
        print(f"📊 監控間隔: {self.interval} 秒")
        print("=" * 80)
        
        cycle_count = 0
        
        try:
            while self.running:
                cycle_count += 1
                timestamp = datetime.now()
                
                print(f"\n🔄 監控週期 #{cycle_count} - {timestamp.strftime('%H:%M:%S')}")
                
                # 獲取即時市場數據
                market_data = await self._get_market_snapshot()
                if market_data:
                    self._display_market_data(market_data)
                
                # 執行信號質量分析
                signal_decisions = await self._analyze_signals()
                if signal_decisions:
                    self._display_signal_analysis(signal_decisions)
                
                # 等待下一個週期
                print(f"⏱️ 等待 {self.interval} 秒至下一次更新...")
                await asyncio.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\n🛑 使用者中斷監控")
        except Exception as e:
            print(f"\n❌ 監控過程發生錯誤: {e}")
        finally:
            self.running = False
            print("\n📊 監控結束")
    
    async def _get_market_snapshot(self) -> dict:
        """獲取市場快照"""
        try:
            async with binance_connector as connector:
                market_data = await connector.get_comprehensive_market_data(self.symbol)
                return market_data
        except Exception as e:
            logger.error(f"市場數據獲取失敗: {e}")
            return {}
    
    def _display_market_data(self, market_data: dict):
        """顯示市場數據"""
        print(f"💰 當前價格: ${market_data.get('current_price', 0):,.2f}")
        
        ticker_24h = market_data.get('ticker_24h', {})
        if ticker_24h:
            change_pct = float(ticker_24h.get('priceChangePercent', 0))
            volume = float(ticker_24h.get('volume', 0))
            high_24h = float(ticker_24h.get('highPrice', 0))
            low_24h = float(ticker_24h.get('lowPrice', 0))
            
            change_emoji = "📈" if change_pct >= 0 else "📉"
            print(f"{change_emoji} 24h變動: {change_pct:+.3f}% | 成交量: {volume:,.2f}")
            print(f"📊 24h區間: ${low_24h:,.2f} - ${high_24h:,.2f}")
        
        volatility_metrics = market_data.get('volatility_metrics', {})
        if volatility_metrics:
            volatility = volatility_metrics.get('current_volatility', 0) * 100
            print(f"📈 波動率: {volatility:.4f}%")
        
        funding_rate = market_data.get('funding_rate', {})
        if funding_rate:
            rate = float(funding_rate.get('fundingRate', 0)) * 100
            print(f"💸 資金費率: {rate:.6f}%")
        
        order_book = market_data.get('order_book', {})
        if order_book and 'bids' in order_book and 'asks' in order_book:
            bids = order_book['bids'][:3]
            asks = order_book['asks'][:3]
            if bids and asks:
                bid_price = float(bids[0][0])
                ask_price = float(asks[0][0])
                spread = ask_price - bid_price
                print(f"📖 買賣價差: ${spread:.2f} (買: ${bid_price:,.2f} | 賣: ${ask_price:,.2f})")
    
    async def _analyze_signals(self) -> list:
        """分析信號"""
        try:
            # 收集即時數據
            data_snapshot = await real_data_engine.collect_real_time_data(self.symbol)
            
            # 生成信號候選者
            candidates = await real_data_engine.stage1_signal_candidate_pool(data_snapshot)
            
            if not candidates:
                return []
            
            # EPL決策
            market_context = {
                "market_trend": 0.7,
                "volatility": 0.5,
                "liquidity": 0.8,
                "market_uncertainty": 0.3,
                "market_activity": 0.9
            }
            
            decisions = await real_data_engine.stage2_epl_decision_layer(candidates, market_context)
            
            # 記錄信號歷史
            self.signal_history.append({
                "timestamp": datetime.now(),
                "candidates": len(candidates),
                "decisions": len(decisions),
                "high_priority": len([d for d in decisions if d.final_priority.value in ["critical", "high"]])
            })
            
            # 保持最近100次記錄
            if len(self.signal_history) > 100:
                self.signal_history = self.signal_history[-100:]
            
            return decisions
            
        except Exception as e:
            logger.error(f"信號分析失敗: {e}")
            return []
    
    def _display_signal_analysis(self, decisions: list):
        """顯示信號分析"""
        if not decisions:
            print("⚪ 無有效信號")
            return
        
        # 統計優先級
        priority_count = {}
        for decision in decisions:
            priority = decision.final_priority.value
            priority_count[priority] = priority_count.get(priority, 0) + 1
        
        print(f"🎯 信號分析: 總計 {len(decisions)} 個決策")
        
        # 顯示優先級分佈
        priority_emojis = {
            "critical": "🔴",
            "high": "🟡", 
            "medium": "🟠",
            "low": "🔵",
            "rejected": "⚫"
        }
        
        for priority, count in priority_count.items():
            emoji = priority_emojis.get(priority, "⚪")
            print(f"  {emoji} {priority.upper()}: {count}")
        
        # 顯示最高優先級信號詳情
        top_decisions = [d for d in decisions if d.final_priority.value in ["critical", "high"]]
        if top_decisions:
            print("🔥 高優先級信號:")
            for decision in top_decisions[:3]:  # 最多顯示3個
                confidence = decision.execution_confidence * 100
                action = decision.recommended_action
                source = decision.original_candidate.source_type
                print(f"  📡 {source}: {confidence:.1f}% 信心度 → {action}")
        
        # 顯示信號歷史統計
        if len(self.signal_history) >= 3:
            recent_high_priority = [h["high_priority"] for h in self.signal_history[-5:]]
            avg_high_priority = sum(recent_high_priority) / len(recent_high_priority)
            print(f"📈 近期高優先級信號平均: {avg_high_priority:.1f}/週期")
    
    def stop_monitoring(self):
        """停止監控"""
        self.running = False

async def main():
    """主函數"""
    print("🎯 Trading X - 真實幣安數據即時監控系統")
    print("按 Ctrl+C 結束監控")
    print("=" * 80)
    
    # 選擇監控參數
    symbol = "BTCUSDT"  # 可改為其他交易對
    interval = 15       # 可調整監控間隔（秒）
    
    monitor = RealTimeMarketMonitor(symbol, interval)
    
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\n👋 監控已停止")
    
    print("\n📊 監控系統已退出")

if __name__ == "__main__":
    asyncio.run(main())
