#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trading X 模型路徑配置
==================

統一管理所有模型檔案的路徑配置
"""

import os
from pathlib import Path

# 獲取 quantum_pro 目錄
QUANTUM_PRO_DIR = Path(__file__).parent.parent

# 模型儲存目錄
MODELS_DIR = QUANTUM_PRO_DIR / "data" / "models"

# 確保目錄存在
MODELS_DIR.mkdir(parents=True, exist_ok=True)

def get_quantum_model_path(coin_symbol: str) -> str:
    """獲取量子模型檔案路徑"""
    coin = coin_symbol.upper().replace("USDT", "")
    return str(MODELS_DIR / f"quantum_model_{coin.lower()}.pkl")

def get_model_directory() -> str:
    """獲取模型目錄路徑"""
    return str(MODELS_DIR)

# 預定義常用幣種的模型路徑
COIN_MODEL_PATHS = {
    "BTC": get_quantum_model_path("BTCUSDT"),
    "ETH": get_quantum_model_path("ETHUSDT"), 
    "ADA": get_quantum_model_path("ADAUSDT"),
    "SOL": get_quantum_model_path("SOLUSDT"),
    "XRP": get_quantum_model_path("XRPUSDT"),
    "DOGE": get_quantum_model_path("DOGEUSDT"),
    "BNB": get_quantum_model_path("BNBUSDT"),
}

if __name__ == "__main__":
    print(f"📁 量子模型目錄: {MODELS_DIR}")
    print(f"🔍 支援的幣種模型路徑:")
    for coin, path in COIN_MODEL_PATHS.items():
        print(f"   {coin}: {path}")
