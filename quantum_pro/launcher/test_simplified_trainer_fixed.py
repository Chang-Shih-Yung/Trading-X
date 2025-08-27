#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試簡化後的量子模型訓練器
========================

驗證模型保存路徑修正和簡化的幣安API數據獲取
"""

import sys
import os
from datetime import datetime

# 添加路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from quantum_model_trainer import QuantumModelTrainer
    print("✅ 簡化版量子模型訓練器導入成功")
except ImportError as e:
    print(f"❌ 導入失敗: {e}")
    sys.exit(1)

def test_model_path_fix():
    """測試模型保存路徑修正"""
    print("🧪 測試模型保存路徑修正")
    print("=" * 40)
    
    symbols = ["BTCUSDT", "ETHUSDT"]
    
    for symbol in symbols:
        trainer = QuantumModelTrainer(symbol)
        print(f"💾 {symbol} 模型路徑: {trainer.model_path}")
        
        # 驗證路徑格式
        if "quantum_pro/data/models/" in trainer.model_path:
            print(f"✅ {symbol} 路徑格式正確")
        else:
            print(f"❌ {symbol} 路徑格式錯誤")
            
        # 驗證目錄存在
        if os.path.exists(trainer.models_dir):
            print(f"✅ {symbol} 模型目錄已創建")
        else:
            print(f"❌ {symbol} 模型目錄創建失敗")

def test_simplified_data_fetching():
    """測試簡化的數據獲取"""
    print("\n🧪 測試簡化的數據獲取")
    print("=" * 40)
    
    trainer = QuantumModelTrainer("BTCUSDT")
    
    try:
        print("📡 開始獲取幣安API數據...")
        start_time = datetime.now()
        
        data = trainer.fetch_historical_data(days=7)  # 測試7天數據
        
        fetch_time = (datetime.now() - start_time).total_seconds()
        
        if data is not None and not data.empty:
            print(f"✅ 數據獲取成功")
            print(f"📊 數據量: {len(data)} 條記錄")
            print(f"📅 數據範圍: {data.index[0]} 到 {data.index[-1]}")
            print(f"💰 價格範圍: ${data['Close'].min():.2f} - ${data['Close'].max():.2f}")
            print(f"⏱️ 獲取耗時: {fetch_time:.2f} 秒")
            print(f"📈 包含列: {list(data.columns)}")
        else:
            print("❌ 數據獲取失敗")
            
    except Exception as e:
        print(f"❌ 數據獲取異常: {e}")

def test_model_initialization():
    """測試模型初始化"""
    print("\n🧪 測試模型初始化")
    print("=" * 40)
    
    try:
        trainer = QuantumModelTrainer("ETHUSDT")
        print(f"✅ 訓練器初始化成功")
        print(f"🔮 幣種: {trainer.coin_symbol}")
        print(f"💾 模型路徑: {trainer.model_path}")
        
        # 檢查必要屬性
        assert hasattr(trainer, 'symbol')
        assert hasattr(trainer, 'coin_symbol')
        assert hasattr(trainer, 'models_dir')
        assert hasattr(trainer, 'model_path')
        
        print("✅ 所有必要屬性存在")
        
    except Exception as e:
        print(f"❌ 模型初始化失敗: {e}")

if __name__ == "__main__":
    print("🚀 啟動簡化版訓練器測試")
    
    # 測試模型路徑修正
    test_model_path_fix()
    
    # 測試模型初始化
    test_model_initialization()
    
    # 測試簡化的數據獲取
    test_simplified_data_fetching()
    
    print("\n🎉 所有測試完成")
