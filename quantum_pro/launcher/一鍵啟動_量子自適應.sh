#!/bin/bash
# -*- coding: utf-8 -*-
"""
🔮 Trading X 量子自適應交易系統一鍵啟動
═══════════════════════════════════════════════

突破性改進：
- ❌ 告別固定30秒週期
- ✅ 擁抱量子狀態驅動
- ⚡ 純物理定律觸發信號
- 🌌 自適應間隔調整

系統會自動：
1. 檢測模型狀態
2. 需要時自動訓練
3. 啟動量子自適應引擎
"""

echo "🔮 Trading X 量子自適應交易系統啟動"
echo "=" * 80
echo "⚡ 突破性升級：量子狀態驅動，告別固定週期！"
echo "🌌 純物理定律觸發，零人為限制"
echo "=" * 80

# 進入量子系統目錄
cd "$(dirname "$0")"
cd ../

# 檢查 Python 環境
if ! command -v python3 &> /dev/null; then
    echo "❌ 錯誤：未找到 Python3"
    echo "請安裝 Python 3.8+ 版本"
    exit 1
fi

echo "🔍 檢查量子模型狀態..."

# 檢查模型目錄
MODEL_DIR="data/models"
if [ ! -d "$MODEL_DIR" ]; then
    echo "📁 創建模型目錄..."
    mkdir -p "$MODEL_DIR"
fi

# 檢查已訓練的模型數量
TRAINED_MODELS=$(find "$MODEL_DIR" -name "quantum_model_*.pkl" 2>/dev/null | wc -l)

echo "📊 已訓練模型數量: $TRAINED_MODELS/7"

if [ "$TRAINED_MODELS" -eq 0 ]; then
    echo ""
    echo "🎯 發現未訓練的量子模型，開始自動訓練..."
    echo "⏱️ 預計耗時: 20-40分鐘 (7個幣種)"
    echo ""
    
    # 自動訓練所有模型
    cd launcher
    python3 quantum_model_trainer.py << EOF
2
EOF
    
    if [ $? -eq 0 ]; then
        echo "✅ 量子模型訓練完成！"
    else
        echo "❌ 量子模型訓練失敗，請檢查錯誤訊息"
        exit 1
    fi
    
    cd ..
elif [ "$TRAINED_MODELS" -lt 7 ]; then
    echo "⚠️ 檢測到部分模型缺失 ($TRAINED_MODELS/7)"
    echo "🔄 建議重新訓練所有模型以確保一致性"
    
    read -p "是否重新訓練所有模型？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd launcher
        python3 quantum_model_trainer.py << EOF
2
EOF
        cd ..
    fi
else
    echo "✅ 所有量子模型已就緒！"
fi

echo ""
echo "🚀 啟動量子自適應交易引擎..."
echo "🌌 系統特色："
echo "   ⚡ 量子狀態觸發 (非固定週期)"
echo "   🔮 疊加態坍縮檢測"
echo "   🌀 量子糾纏監控"
echo "   ⚛️  海森堡不確定性管理"
echo "   🕐 自適應間隔調整 (0.1-3600秒)"
echo ""

# 啟動量子自適應引擎
cd launcher
exec python3 quantum_adaptive_trading_launcher.py
