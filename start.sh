#!/bin/bash

# Trading X 系統啟動腳本

echo "🚀 啟動 Trading X 進階交易策略系統..."

# 檢查 Python 版本
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+')
if [[ $(echo "$python_version >= 3.9" | bc -l) -eq 0 ]]; then
    echo "❌ 需要 Python 3.9 或以上版本"
    exit 1
fi

echo "✅ Python 版本: $(python3 --version)"

# 創建虛擬環境（如果不存在）
if [ ! -d "venv" ]; then
    echo "📦 創建虛擬環境..."
    python3 -m venv venv
fi

# 激活虛擬環境
echo "🔧 激活虛擬環境..."
source venv/bin/activate

# 安裝依賴
echo "📥 安裝 Python 依賴..."
pip install -r requirements.txt

# 檢查環境變數文件
if [ ! -f ".env" ]; then
    echo "⚙️ 複製環境變數模板..."
    cp .env.example .env
    echo "📝 請編輯 .env 文件，添加您的 API 金鑰"
fi

# 啟動資料庫（Docker方式）
echo "🗄️ 啟動資料庫服務..."
if command -v docker-compose &> /dev/null; then
    docker-compose up -d postgres redis influxdb
    echo "⏳ 等待資料庫啟動..."
    sleep 10
else
    echo "⚠️ 未找到 docker-compose，請手動啟動 PostgreSQL、Redis 和 InfluxDB"
fi

# 初始化資料庫
echo "🔨 初始化資料庫..."
python -c "
import asyncio
from app.core.database import create_tables
asyncio.run(create_tables())
print('✅ 資料庫初始化完成')
"

# 啟動後端服務
echo "🌐 啟動後端 API 服務..."
echo "📍 API 文檔: http://localhost:8000/docs"
echo "📊 系統監控: http://localhost:8000"
echo ""
echo "按 Ctrl+C 停止服務"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
