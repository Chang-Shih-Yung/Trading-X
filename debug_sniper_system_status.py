#!/usr/bin/env python3
"""
🔧 狙擊手系統狀態檢查和手動觸發信號生成

檢查項目：
1. ✅ 狙擊手服務狀態
2. 📊 內存中活躍信號數量  
3. 🚀 手動觸發信號生成
4. 🔍 檢查觸發結果
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict
import sys
import os

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.sniper_smart_layer import sniper_smart_layer
from app.utils.timezone_utils import ensure_taiwan_timezone, get_taiwan_now

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SniperSystemDebugger:
    """狙擊手系統調試器"""
    
    def __init__(self):
        self.sniper_service = sniper_smart_layer
    
    async def check_system_status(self):
        """檢查系統狀態"""
        print("🔧 狙擊手系統狀態檢查")
        print("=" * 50)
        
        # 1. 檢查服務狀態
        print(f"📍 服務實例: {type(self.sniper_service).__name__}")
        print(f"📊 活躍信號數量: {len(self.sniper_service.active_signals)}")
        print(f"🔒 更新鎖數量: {len(self.sniper_service.update_locks)}")
        print(f"🌐 WebSocket客戶端: {len(self.sniper_service.websocket_clients)}")
        
        # 2. 檢查活躍信號詳細信息
        if self.sniper_service.active_signals:
            print("\n📈 活躍信號詳情:")
            for symbol, signal in self.sniper_service.active_signals.items():
                print(f"  💰 {symbol}: {signal.signal_type} @ ${signal.entry_price:.4f} "
                      f"(信心度: {signal.confidence:.2f}, 品質: {signal.quality_score:.2f})")
        else:
            print("\n⚠️ 內存中沒有活躍信號")
        
        # 3. 檢查緩存狀態
        cache_count = sum(len(signals) for signals in self.sniper_service.signal_cache.values())
        print(f"\n📂 信號緩存數量: {cache_count}")
        
        return len(self.sniper_service.active_signals)
    
    async def trigger_manual_signal_generation(self, symbols: List[str] = None):
        """手動觸發信號生成"""
        if symbols is None:
            symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT', 'SOLUSDT']
        
        print(f"\n🚀 手動觸發信號生成 - 目標幣種: {symbols}")
        print("=" * 50)
        
        success_count = 0
        error_count = 0
        
        for symbol in symbols:
            try:
                print(f"\n🎯 處理 {symbol}...")
                
                # 觸發更新
                await self.sniper_service.force_generate_signal(symbol)
                print(f"✅ {symbol} 信號更新完成")
                success_count += 1
                
            except Exception as e:
                print(f"❌ {symbol} 信號更新失敗: {e}")
                error_count += 1
        
        print(f"\n📊 觸發結果統計:")
        print(f"  ✅ 成功: {success_count}")
        print(f"  ❌ 失敗: {error_count}")
        
        return success_count, error_count
    
    async def check_signal_generation_process(self, symbol: str = 'BTCUSDT'):
        """詳細檢查信號生成過程"""
        print(f"\n🔍 檢查 {symbol} 信號生成過程")
        print("=" * 50)
        
        try:
            # 獲取市場數據
            print("📊 正在獲取市場數據...")
            
            # 檢查是否有現有信號
            existing_signal = self.sniper_service.active_signals.get(symbol)
            if existing_signal:
                print(f"💰 現有信號: {existing_signal.action} @ ${existing_signal.current_price:.4f}")
            else:
                print("⚠️ 沒有現有信號")
            
            # 嘗試觸發更新
            print(f"🚀 觸發 {symbol} 信號更新...")
            await self.sniper_service.force_generate_signal(symbol)
            
            # 檢查更新後的狀態
            updated_signal = self.sniper_service.active_signals.get(symbol)
            if updated_signal:
                print(f"✅ 更新後信號: {updated_signal.signal_type} @ ${updated_signal.entry_price:.4f}")
                print(f"   信心度: {updated_signal.confidence:.2f}")
                print(f"   品質評分: {updated_signal.quality_score:.2f}")
                print(f"   生成時間: {updated_signal.created_at}")
                return True
            else:
                print("❌ 更新後仍然沒有信號")
                return False
                
        except Exception as e:
            print(f"❌ 信號生成過程檢查失敗: {e}")
            import traceback
            traceback.print_exc()
    
    async def test_api_response(self):
        """測試API響應"""
        print(f"\n🌐 測試狙擊手API響應")
        print("=" * 50)
        
        try:
            # 獲取所有活躍信號
            active_signals = await self.sniper_service.get_all_active_signals()
            print(f"📊 API返回信號數量: {len(active_signals)}")
            
            if active_signals:
                print("📈 信號列表:")
                for i, signal in enumerate(active_signals, 1):
                    print(f"  {i}. {signal.get('symbol')} - {signal.get('signal_type')} "
                          f"@ ${signal.get('entry_price', 0):.4f} "
                          f"(品質: {signal.get('quality_score', 0):.2f})")
            else:
                print("⚠️ API返回空信號列表")
                
        except Exception as e:
            print(f"❌ API測試失敗: {e}")
            import traceback
            traceback.print_exc()

async def main():
    """主執行函數"""
    debugger = SniperSystemDebugger()
    
    print("🎯 狙擊手系統完整診斷開始")
    print("=" * 60)
    print(f"⏰ 檢查時間: {get_taiwan_now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 檢查系統狀態
    active_count = await debugger.check_system_status()
    
    # 2. 如果沒有活躍信號，嘗試觸發生成
    if active_count == 0:
        print("\n🔄 檢測到沒有活躍信號，開始手動觸發...")
        success, error = await debugger.trigger_manual_signal_generation()
        
        # 3. 檢查觸發後的狀態
        await asyncio.sleep(2)  # 等待處理完成
        print(f"\n🔍 觸發後系統狀態檢查:")
        new_active_count = await debugger.check_system_status()
        
        if new_active_count > 0:
            print(f"✅ 成功生成 {new_active_count} 個活躍信號")
        else:
            print("❌ 觸發後仍然沒有活躍信號")
    
        # 4. 詳細檢查信號生成過程
        success = await debugger.check_signal_generation_process('BTCUSDT')
        if success:
            print("🎯 BTCUSDT信號生成成功，檢查整體狀態")
            await debugger.check_system_status()
        else:
            print("⚠️ BTCUSDT信號生成失敗，嘗試其他幣種")
            for symbol in ['ETHUSDT', 'SOLUSDT']:
                success = await debugger.check_signal_generation_process(symbol)
                if success:
                    break    # 5. 測試API響應
    await debugger.test_api_response()
    
    print(f"\n🎯 狙擊手系統診斷完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
