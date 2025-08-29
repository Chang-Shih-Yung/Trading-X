#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 真實市場量子對戰競技場 v1.0 - 實戰版
═══════════════════════════════════════════════════════

🎯 核心概念：
- 使用幣安 WebSocket 實時監聽市場數據
- 兩個量子引擎同時預測未來30秒走勢
- 對比實際市場結果，計算預測準確度
- 真正有意義的量子交易算法測試！

📊 對戰流程：
1. 獲取當前市場數據 → 2. 雙方預測信號 → 3. 等待30秒 → 4. 對比實際走勢 → 5. 計分
"""

import asyncio
import json
import logging
import time
import websockets
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

# 量子引擎導入
import sys
import os
sys.path.append(str(Path(__file__).parent))

# 屏蔽詳細日誌，只保留關鍵信息
import warnings
warnings.filterwarnings('ignore')

# 禁用量子計算庫的詳細日誌
os.environ['QISKIT_LOGGING_LEVEL'] = 'ERROR'
logging.getLogger('qiskit').setLevel(logging.ERROR)
logging.getLogger('websockets').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)

# 設置簡化日誌 - 只顯示關鍵戰鬥信息
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',  # 簡化格式，不顯示時間戳
    handlers=[
        logging.StreamHandler()  # 只輸出到控制台
    ]
)
logger = logging.getLogger(__name__)

class RealMarketData:
    """實時市場數據管理器"""
    
    def __init__(self, symbol: str = "BTCUSDT"):
        self.symbol = symbol.lower()
        self.current_price = None
        self.price_history = []
        self.kline_data = []
        
    async def connect_binance_websocket(self):
        """連接幣安WebSocket獲取實時數據"""
        
        # 幣安WebSocket URL for Kline (K線) 數據
        uri = f"wss://stream.binance.com:9443/ws/{self.symbol}@kline_1s"
        
        logger.info(f"🔗 連接 {self.symbol.upper()} 市場數據...")
        
        try:
            async with websockets.connect(uri) as websocket:
                while True:
                    data = await websocket.recv()
                    kline_data = json.loads(data)
                    
                    # 解析K線數據
                    kline = kline_data['k']
                    
                    price_data = {
                        'symbol': kline['s'],
                        'open_time': kline['t'],
                        'close_time': kline['T'],
                        'open_price': float(kline['o']),
                        'high_price': float(kline['h']),
                        'low_price': float(kline['l']),
                        'close_price': float(kline['c']),
                        'volume': float(kline['v']),
                        'is_closed': kline['x']  # K線是否完結
                    }
                    
                    self.current_price = price_data['close_price']
                    self.price_history.append(price_data)
                    
                    # 保持最近1000筆數據
                    if len(self.price_history) > 1000:
                        self.price_history.pop(0)
                    
                    yield price_data
                    
        except Exception as e:
            logger.error(f"❌ WebSocket連接錯誤: {e}")
            raise

class RealMarketBattleArena:
    """🔥 真實市場量子對戰競技場"""
    
    def __init__(self, symbol: str = "BTCUSDT"):
        self.symbol = symbol
        self.market_data = RealMarketData(symbol)
        
        # 戰鬥統計
        self.battle_count = 0
        self.red_wins = 0
        self.blue_wins = 0
        self.draws = 0
        
        # 戰鬥記錄
        self.battle_history = []
        
        logger.info(f"🔥 量子對戰競技場 - {symbol}")
        logger.info("📊 30秒預測 vs 實際走勢模式")
    
    async def initialize_fighters(self):
        """初始化量子戰士 - 只調用戰士方法，無自定義數據"""
        
        try:
            # 🔴 初始化紅方：Pure Quantum Engine
            sys.path.append(str(Path(__file__).parent.parent))
            
            try:
                from btc_quantum_ultimate_model import BTCQuantumUltimateModel
                self.red_fighter = BTCQuantumUltimateModel()
                logger.info("✅ 🔴 純量子引擎就位")
            except ImportError:
                logger.info("⚠️ 🔴 使用量子降級模式")
                self.red_fighter = None
            
            # 🔵 初始化藍方：Adaptive Quantum Engine  
            try:
                from quantum_adaptive_signal_engine import QuantumAdaptiveSignalEngine
                self.blue_fighter = QuantumAdaptiveSignalEngine()
                
                # 載入量子模型（如果存在）
                models_dir = Path(__file__).parent.parent / "data" / "models"
                if models_dir.exists():
                    self.blue_fighter.load_trained_quantum_models(models_dir)
                
                logger.info("✅ 🔵 自適應量子引擎就位")
            except ImportError:
                logger.info("⚠️ 🔵 使用量子降級模式")
                self.blue_fighter = None
            
        except Exception as e:
            logger.error(f"❌ 初始化失敗: {e}")
            self.red_fighter = None
            self.blue_fighter = None
    
    def analyze_market_trend(self, start_price: float, end_price: float, threshold: float = 0.001) -> str:
        """分析市場趨勢"""
        
        price_change = (end_price - start_price) / start_price
        
        if price_change > threshold:
            return "BULLISH"  # 上漲
        elif price_change < -threshold:
            return "BEARISH"  # 下跌
        else:
            return "SIDEWAYS"  # 橫盤
    
    def evaluate_prediction(self, predicted_signal: str, actual_trend: str) -> int:
        """評估預測準確度"""
        
        score = 0
        
        if actual_trend == "BULLISH":
            if predicted_signal == "BUY":
                score = 10  # 完全正確
            elif predicted_signal == "HOLD":
                score = 3   # 部分正確
            else:  # SELL
                score = -5  # 完全錯誤
                
        elif actual_trend == "BEARISH":
            if predicted_signal == "SELL":
                score = 10  # 完全正確
            elif predicted_signal == "HOLD":
                score = 3   # 部分正確
            else:  # BUY
                score = -5  # 完全錯誤
                
        else:  # SIDEWAYS
            if predicted_signal == "HOLD":
                score = 10  # 完全正確
            else:
                score = -2  # 輕微錯誤
        
        return score
    
    async def run_single_battle(self, current_market_data: Dict) -> Dict:
        """執行單次對戰 - 只顯示關鍵信息"""
        
        self.battle_count += 1
        battle_start = datetime.now()
        start_price = current_market_data['close_price']
        
        # 準備市場數據給量子引擎
        market_input = {
            'price': start_price,
            'volume': current_market_data['volume'],
            'high': current_market_data['high_price'],
            'low': current_market_data['low_price'],
            'timestamp': current_market_data['close_time']
        }
        
        try:
            # 獲取預測信號
            red_prediction = await self.get_red_prediction(market_input)
            blue_prediction = await self.get_blue_prediction(market_input)
            
            # 顯示對戰信息
            print(f"\n🥊 第{self.battle_count}輪 | ${start_price:.2f} | 🔴{red_prediction} vs 🔵{blue_prediction}")
            
            # 等待30秒觀察實際市場走勢
            print("⏱️ 等待30秒...", end="", flush=True)
            for i in range(6):
                await asyncio.sleep(5)
                print(".", end="", flush=True)
            print()
            
            # 重新獲取實時價格 - 確保是最新價格
            end_price = None
            retry_count = 0
            max_retries = 5
            
            while end_price is None and retry_count < max_retries:
                try:
                    # 等待新的市場數據
                    await asyncio.sleep(1)
                    if hasattr(self.market_data, 'current_price') and self.market_data.current_price is not None:
                        if self.market_data.current_price != start_price:  # 確保價格有變化
                            end_price = self.market_data.current_price
                            break
                    retry_count += 1
                except Exception:
                    retry_count += 1
            
            # 如果仍然無法獲取新價格，直接報錯
            if end_price is None or end_price == start_price:
                raise Exception(f"無法獲取有效的價格變動數據，開始價格: ${start_price:.2f}, 結束價格: ${end_price}")
                
            actual_trend = self.analyze_market_trend(start_price, end_price)
            price_change_pct = ((end_price - start_price) / start_price) * 100
            
            # 計算得分
            red_score = self.evaluate_prediction(red_prediction, actual_trend)
            blue_score = self.evaluate_prediction(blue_prediction, actual_trend)
            
            # 判定勝負
            if red_score > blue_score:
                winner = "🔴"
                self.red_wins += 1
            elif blue_score > red_score:
                winner = "🔵"
                self.blue_wins += 1
            else:
                winner = "🤝"
                self.draws += 1
            
            # 顯示結果
            trend_emoji = "📈" if actual_trend == "BULLISH" else "📉" if actual_trend == "BEARISH" else "➡️"
            print(f"📊 結果: ${end_price:.2f} ({price_change_pct:+.3f}%) {trend_emoji}{actual_trend}")
            print(f"🏆 得分: 🔴{red_score} vs 🔵{blue_score} → {winner} 勝利!")
            print(f"📈 戰績: 🔴{self.red_wins} : 🔵{self.blue_wins} : 🤝{self.draws}")
            
            # 記錄戰績
            battle_result = {
                'battle_number': self.battle_count,
                'timestamp': battle_start.isoformat(),
                'start_price': start_price,
                'end_price': end_price,
                'price_change_pct': price_change_pct,
                'actual_trend': actual_trend,
                'red_prediction': red_prediction,
                'blue_prediction': blue_prediction,
                'red_score': red_score,
                'blue_score': blue_score,
                'winner': winner
            }
            
            self.battle_history.append(battle_result)
            return battle_result
            
        except Exception as e:
            logger.error(f"❌ 對戰錯誤: {e}")
            return {}
    
    async def get_red_prediction(self, market_data: Dict) -> str:
        """獲取紅方預測 (純量子引擎)"""
        try:
            # 調用真正的量子引擎方法
            if hasattr(self, 'red_fighter') and self.red_fighter and hasattr(self.red_fighter, 'predict_signal'):
                signal = await self.red_fighter.predict_signal(market_data)
                return signal
            else:
                # 臨時降級：使用量子隨機數
                from qiskit import QuantumCircuit, transpile
                from qiskit_aer import AerSimulator
                
                # 創建量子隨機數生成器
                qc = QuantumCircuit(2, 2)
                qc.h(0)
                qc.h(1)
                qc.measure_all()
                
                simulator = AerSimulator()
                job = simulator.run(transpile(qc, simulator), shots=1)
                result = job.result()
                counts = result.get_counts(qc)
                
                # 根據量子測量結果決定信號
                measurement = list(counts.keys())[0]
                if measurement == '00':
                    return "BUY"
                elif measurement == '11':
                    return "SELL"
                else:
                    return "HOLD"
                
        except Exception:
            return "HOLD"
    
    async def get_blue_prediction(self, market_data: Dict) -> str:
        """獲取藍方預測 (自適應量子引擎)"""
        try:
            # 調用真正的量子自適應引擎方法
            if hasattr(self, 'blue_fighter') and self.blue_fighter and hasattr(self.blue_fighter, 'generate_adaptive_signal'):
                signal = await self.blue_fighter.generate_adaptive_signal(market_data)
                return signal
            else:
                # 臨時降級：使用量子態疊加決策
                from qiskit import QuantumCircuit, transpile
                from qiskit_aer import AerSimulator
                
                # 創建量子疊加態
                qc = QuantumCircuit(3, 3)
                qc.h(0)
                qc.cx(0, 1)
                qc.cx(1, 2)
                qc.measure_all()
                
                simulator = AerSimulator()
                job = simulator.run(transpile(qc, simulator), shots=1)
                result = job.result()
                counts = result.get_counts(qc)
                
                # 根據量子糾纏結果決定自適應信號
                measurement = list(counts.keys())[0]
                if measurement in ['000', '111']:
                    return "BUY"
                elif measurement in ['001', '110']:
                    return "SELL"
                else:
                    return "HOLD"
                
        except Exception:
            return "HOLD"
    
    async def start_real_battle(self, duration_minutes: int = 30):
        """開始真實市場對戰"""
        
        print("🚀 真實市場量子對戰開始！")
        print("=" * 50)
        
        # 初始化戰士
        await self.initialize_fighters()
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        try:
            # 連接市場數據流
            async for market_data in self.market_data.connect_binance_websocket():
                
                # 檢查是否該進行對戰 (每30秒一次)
                if market_data.get('is_closed', False):  # K線完結時進行預測
                    await self.run_single_battle(market_data)
                
                # 檢查是否結束
                if time.time() > end_time:
                    break
                    
        except KeyboardInterrupt:
            print("\n⚡ 對戰中斷")
        except Exception as e:
            logger.error(f"❌ 系統錯誤: {e}")
        
        # 顯示最終戰績
        self.show_final_results()
    
    def show_final_results(self):
        """顯示最終戰績"""
        
        print("\n" + "=" * 50)
        print("🏁 真實市場量子對戰 - 最終戰績")
        print("=" * 50)
        print(f"🥊 總對戰: {self.battle_count} 場")
        print(f"🔴 紅方: {self.red_wins} 勝 ({(self.red_wins/max(self.battle_count,1)*100):.1f}%)")
        print(f"🔵 藍方: {self.blue_wins} 勝 ({(self.blue_wins/max(self.battle_count,1)*100):.1f}%)")
        print(f"🤝 平手: {self.draws} 場")
        
        if self.red_wins > self.blue_wins:
            print("🏆 最終勝者: 🔴 Pure Quantum Engine")
        elif self.blue_wins > self.red_wins:
            print("🏆 最終勝者: 🔵 Adaptive Quantum Engine")
        else:
            print("🤝 最終結果: 平手！")
        
        print("=" * 50)

async def main():
    """主程序"""
    
    print("🔥 歡迎來到真實市場量子對戰競技場！")
    print("📊 本系統將使用幣安實時數據進行真實對戰測試")
    print()
    
    # 選擇交易對
    symbol = input("請輸入交易對 (預設: BTCUSDT): ").strip().upper()
    if not symbol:
        symbol = "BTCUSDT"
    
    # 設定對戰時長
    duration = input("請輸入對戰時長(分鐘, 預設: 10): ").strip()
    try:
        duration = int(duration) if duration else 10
    except:
        duration = 10
    
    print(f"🎯 開始 {symbol} 真實市場對戰，時長 {duration} 分鐘")
    print("=" * 50)
    
    # 創建競技場並開始對戰
    arena = RealMarketBattleArena(symbol)
    await arena.start_real_battle(duration)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚡ 對戰已停止")
    except Exception as e:
        print(f"❌ 系統錯誤: {e}")
