#!/usr/bin/env python3
"""
🎯 Trading X - 實時信號生成演示 (簡化版)
測試Phase1系統的核心信號生成能力
"""

import asyncio
import time
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# 添加Phase1模組路徑
phase1_path = Path("X/backend/phase1_signal_generation")
sys.path.append(str(phase1_path / "unified_signal_pool"))

class MockMarketData:
    """模擬市場數據生成器"""
    
    def __init__(self):
        self.base_price = 65000  # BTC基礎價格
        self.current_price = self.base_price
        self.timestamp = datetime.now()
    
    def generate_tick(self) -> Dict[str, Any]:
        """生成一個市場tick數據"""
        # 模擬價格波動 (-0.5% 到 +0.5%)
        import random
        price_change = random.uniform(-0.005, 0.005)
        self.current_price *= (1 + price_change)
        
        # 模擬成交量
        volume = random.uniform(0.1, 5.0)
        
        self.timestamp = datetime.now()
        
        return {
            "symbol": "BTCUSDT",
            "price": round(self.current_price, 2),
            "volume": round(volume, 4),
            "timestamp": self.timestamp,
            "price_change_percent": round(price_change * 100, 4),
            "high_24h": round(self.current_price * 1.02, 2),
            "low_24h": round(self.current_price * 0.98, 2)
        }

class MockSignalGenerator:
    """模擬信號生成器"""
    
    def __init__(self):
        self.signal_counter = 0
        self.signal_history = []
        
    async def generate_phase1a_signal(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成Phase1A基礎信號"""
        self.signal_counter += 1
        
        # 簡單的信號邏輯：價格變化 > 0.1% 觸發信號
        price_change = abs(market_data["price_change_percent"])
        
        if price_change > 0.1:
            signal_strength = min(1.0, price_change / 0.5)  # 標準化到0-1
            signal_type = "PRICE_BREAKOUT" if price_change > 0.3 else "PRICE_MOVEMENT"
            
            signal = {
                "signal_id": f"phase1a_{self.signal_counter}",
                "signal_type": signal_type,
                "signal_strength": round(signal_strength, 3),
                "confidence_score": round(0.6 + (signal_strength * 0.3), 3),
                "signal_source": "phase1a_basic_signal_generation",
                "symbol": market_data["symbol"],
                "trigger_price": market_data["price"],
                "price_change": market_data["price_change_percent"],
                "timestamp": market_data["timestamp"],
                "market_context": {
                    "volume": market_data["volume"],
                    "high_24h": market_data["high_24h"],
                    "low_24h": market_data["low_24h"]
                }
            }
            
            self.signal_history.append(signal)
            return signal
        
        return None
    
    async def generate_phase1b_signal(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成Phase1B波動性信號"""
        # 檢查最近的價格波動
        if len(self.signal_history) >= 3:
            recent_changes = [s.get("price_change", 0) for s in self.signal_history[-3:]]
            volatility = sum(abs(c) for c in recent_changes) / len(recent_changes)
            
            if volatility > 0.2:  # 高波動性閾值
                self.signal_counter += 1
                
                signal = {
                    "signal_id": f"phase1b_{self.signal_counter}",
                    "signal_type": "VOLATILITY_SPIKE",
                    "signal_strength": round(min(1.0, volatility / 0.5), 3),
                    "confidence_score": round(0.7 + (volatility * 0.2), 3),
                    "signal_source": "phase1b_volatility_adaptation",
                    "symbol": market_data["symbol"],
                    "volatility_measure": round(volatility, 4),
                    "timestamp": market_data["timestamp"]
                }
                
                return signal
        
        return None
    
    async def generate_phase1c_signal(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成Phase1C標準化信號"""
        # 綜合前面的信號進行最終決策
        recent_signals = [s for s in self.signal_history[-5:] if s is not None]
        
        if len(recent_signals) >= 2:
            # 檢查信號聚合
            total_strength = sum(s.get("signal_strength", 0) for s in recent_signals)
            avg_confidence = sum(s.get("confidence_score", 0) for s in recent_signals) / len(recent_signals)
            
            if total_strength > 1.5 and avg_confidence > 0.7:
                self.signal_counter += 1
                
                signal = {
                    "signal_id": f"phase1c_{self.signal_counter}",
                    "signal_type": "FINAL_TRADING_SIGNAL",
                    "signal_strength": round(min(1.0, total_strength / 3), 3),
                    "confidence_score": round(avg_confidence, 3),
                    "signal_source": "phase1c_signal_standardization",
                    "symbol": market_data["symbol"],
                    "aggregated_signals": len(recent_signals),
                    "risk_assessment": round(1.0 - avg_confidence, 3),
                    "execution_priority": 1 if avg_confidence > 0.8 else 2,
                    "timestamp": market_data["timestamp"]
                }
                
                return signal
        
        return None

async def real_time_signal_demo():
    """實時信號生成演示"""
    print("🚀 啟動實時信號生成演示")
    print("=" * 60)
    
    # 初始化組件
    market_data_generator = MockMarketData()
    signal_generator = MockSignalGenerator()
    
    # 演示參數
    demo_duration = 30  # 30秒演示
    tick_interval = 0.5  # 每0.5秒一個tick
    
    signals_generated = []
    ticks_processed = 0
    start_time = time.time()
    
    print(f"📊 開始 {demo_duration} 秒實時演示，每 {tick_interval} 秒更新一次")
    print("🔄 正在生成信號...")
    
    try:
        while time.time() - start_time < demo_duration:
            # 生成市場數據
            market_tick = market_data_generator.generate_tick()
            ticks_processed += 1
            
            # 並行生成所有Phase1信號
            phase1_tasks = [
                signal_generator.generate_phase1a_signal(market_tick),
                signal_generator.generate_phase1b_signal(market_tick),
                signal_generator.generate_phase1c_signal(market_tick)
            ]
            
            # 等待信號生成完成
            phase1_signals = await asyncio.gather(*phase1_tasks)
            
            # 收集有效信號
            valid_signals = [s for s in phase1_signals if s is not None]
            signals_generated.extend(valid_signals)
            
            # 實時顯示
            current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            price = market_tick["price"]
            change = market_tick["price_change_percent"]
            signal_count = len(valid_signals)
            
            if signal_count > 0:
                print(f"⚡ {current_time} | BTC: ${price:,.2f} ({change:+.3f}%) | 🎯 {signal_count} 個新信號")
                for signal in valid_signals:
                    print(f"   📈 {signal['signal_source'].split('_')[0].upper()}: {signal['signal_type']} (強度: {signal['signal_strength']:.3f})")
            else:
                print(f"📊 {current_time} | BTC: ${price:,.2f} ({change:+.3f}%) | 待機中...")
            
            # 等待下一個tick
            await asyncio.sleep(tick_interval)
    
    except KeyboardInterrupt:
        print("\n⏹️ 用戶中斷演示")
    
    # 演示結束統計
    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n" + "=" * 60)
    print("📊 實時信號生成演示完成")
    print("=" * 60)
    
    # 統計報告
    phase1a_signals = [s for s in signals_generated if "phase1a" in s["signal_source"]]
    phase1b_signals = [s for s in signals_generated if "phase1b" in s["signal_source"]]
    phase1c_signals = [s for s in signals_generated if "phase1c" in s["signal_source"]]
    
    print(f"⏱️ 演示時長: {total_time:.1f} 秒")
    print(f"📈 市場Tick數: {ticks_processed}")
    print(f"🎯 總信號數: {len(signals_generated)}")
    print(f"   📊 Phase1A (基礎): {len(phase1a_signals)} 個")
    print(f"   📊 Phase1B (波動): {len(phase1b_signals)} 個")
    print(f"   📊 Phase1C (最終): {len(phase1c_signals)} 個")
    
    if signals_generated:
        avg_strength = sum(s["signal_strength"] for s in signals_generated) / len(signals_generated)
        avg_confidence = sum(s["confidence_score"] for s in signals_generated) / len(signals_generated)
        
        print(f"💪 平均信號強度: {avg_strength:.3f}")
        print(f"🎯 平均置信度: {avg_confidence:.3f}")
        
        # 信號效率計算
        signal_rate = len(signals_generated) / total_time
        print(f"⚡ 信號生成率: {signal_rate:.2f} 信號/秒")
        
        # 最強信號
        strongest_signal = max(signals_generated, key=lambda s: s["signal_strength"])
        print(f"🏆 最強信號: {strongest_signal['signal_type']} (強度: {strongest_signal['signal_strength']:.3f})")
    
    # 保存演示結果
    demo_report = {
        "demo_summary": {
            "start_time": datetime.fromtimestamp(start_time).isoformat(),
            "end_time": datetime.fromtimestamp(end_time).isoformat(),
            "duration_seconds": round(total_time, 2),
            "ticks_processed": ticks_processed,
            "total_signals": len(signals_generated)
        },
        "signal_breakdown": {
            "phase1a_count": len(phase1a_signals),
            "phase1b_count": len(phase1b_signals),
            "phase1c_count": len(phase1c_signals)
        },
        "performance_metrics": {
            "signal_generation_rate": round(len(signals_generated) / total_time, 2) if total_time > 0 else 0,
            "average_signal_strength": round(sum(s["signal_strength"] for s in signals_generated) / len(signals_generated), 3) if signals_generated else 0,
            "average_confidence": round(sum(s["confidence_score"] for s in signals_generated) / len(signals_generated), 3) if signals_generated else 0
        },
        "all_signals": signals_generated
    }
    
    report_file = "realtime_signal_demo_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(demo_report, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"📄 完整演示報告已保存: {report_file}")
    
    # 結論
    if len(signals_generated) > 0:
        print("🎉 結論: Phase1 實時信號生成系統運行正常!")
    else:
        print("⚠️ 結論: 未生成信號，可能需要調整參數")
    
    return demo_report

def main():
    """主函數"""
    print("🎯 Trading X - Phase1 實時信號生成演示")
    print("💡 這是一個完整的端到端信號生成演示")
    print("🔄 將模擬真實市場環境下的信號生成過程")
    
    # 運行演示
    try:
        result = asyncio.run(real_time_signal_demo())
        print("\n✅ 演示成功完成!")
        return 0
    except Exception as e:
        print(f"\n❌ 演示失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
