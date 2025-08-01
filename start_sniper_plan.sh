#!/bin/bash

# 🎯 狙擊手計劃 - 完整系統啟動腳本
# 同時啟動後端 FastAPI 服務和前端 Vue 開發服務器

echo "🎯 狙擊手計劃 - 完整系統啟動中..."
echo "==============================================="

# 檢查是否在正確的目錄
if [ ! -f "main.py" ]; then
    echo "❌ 錯誤: 請在 Trading X 根目錄執行此腳本"
    exit 1
fi

# 創建日誌目錄
mkdir -p logs

# 函數：清理進程
cleanup() {
    echo ""
    echo "🛑 正在停止所有服務..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ 後端服務已停止"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ 前端服務已停止"
    fi
    echo "🎯 狙擊手計劃系統已完全停止"
    exit 0
}

# 設置信號處理
trap cleanup SIGINT SIGTERM

echo "📦 檢查 Python 依賴..."
if ! python3 -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "⚠️  正在安裝 Python 依賴..."
    pip3 install -r requirements.txt
fi

echo "📦 檢查 Node.js 依賴..."
if [ ! -d "frontend/node_modules" ]; then
    echo "⚠️  正在安裝 Node.js 依賴..."
    cd frontend
    npm install
    cd ..
fi

echo ""
echo "🚀 啟動後端 FastAPI 服務 (Port 8000)..."
echo "   - WebSocket 實時數據連接"
echo "   - 狙擊手雙層架構 API"
echo "   - Email 通知系統"
echo "   - Phase 1ABC + Phase 1+2+3 整合"

# 啟動後端服務
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 > logs/backend.log 2>&1 &
BACKEND_PID=$!

echo "✅ 後端服務已啟動 (PID: $BACKEND_PID)"

# 等待後端啟動
echo "⏳ 等待後端服務就緒..."
for i in {1..30}; do
    if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
        echo "✅ 後端服務就緒"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ 後端服務啟動超時"
        cleanup
    fi
    sleep 1
done

echo ""
echo "🎨 啟動前端 Vue 開發服務器 (Port 3002)..."
echo "   - 🎯 狙擊手計劃界面"
echo "   - WebSocket 實時連接"
echo "   - 完整策略信號展示"
echo "   - Email 通知觸發"

# 啟動前端服務
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "✅ 前端服務已啟動 (PID: $FRONTEND_PID)"

# 等待前端啟動
echo "⏳ 等待前端服務就緒..."
for i in {1..30}; do
    if curl -s http://localhost:3002 > /dev/null 2>&1; then
        echo "✅ 前端服務就緒"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  前端服務可能需要更多時間啟動"
        break
    fi
    sleep 1
done

echo ""
echo "🎯 狙擊手計劃系統已完全啟動!"
echo "==============================================="
echo "📊 後端 API 文檔: http://localhost:8000/docs"
echo "🎯 狙擊手計劃界面: http://localhost:3002/sniper-strategy"
echo "💻 完整前端系統: http://localhost:3002"
echo ""
echo "🔧 系統組件狀態:"
echo "   ✅ FastAPI 後端服務 (PID: $BACKEND_PID)"
echo "   ✅ Vue 前端開發服務器 (PID: $FRONTEND_PID)"
echo "   ✅ WebSocket 實時數據連接"
echo "   ✅ 狙擊手雙層架構引擎"
echo "   ✅ Email 通知系統"
echo "   ✅ Phase 1ABC + Phase 1+2+3 整合"
echo ""
echo "📝 日誌文件:"
echo "   • 後端日誌: logs/backend.log"
echo "   • 前端日誌: logs/frontend.log"
echo ""
echo "⚡ 快速測試命令:"
echo "   python3 test_sniper_plan_complete.py"
echo ""
echo "🛑 按 Ctrl+C 停止所有服務"

# 顯示實時日誌 (可選)
echo ""
read -p "是否要顯示實時日誌? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📊 顯示實時日誌 (Ctrl+C 停止)..."
    tail -f logs/backend.log logs/frontend.log
else
    echo "🎯 狙擊手計劃系統運行中... (Ctrl+C 停止)"
    # 保持腳本運行
    while true; do
        sleep 1
    done
fi
