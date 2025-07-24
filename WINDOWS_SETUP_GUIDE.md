# Trading X - Windows 環境部署指南

## 📋 系統需求

- Windows 10/11
- Git for Windows
- Python 3.9+
- Node.js 16+
- 瀏覽器 (Chrome/Edge/Firefox)

## 🚀 一鍵安裝腳本

### 第一步：環境準備

#### 1.1 安裝 Git for Windows

```bash
# 下載並安裝 Git for Windows
# https://git-scm.com/download/win
# 安裝時選擇 "Git Bash Here" 選項
```

#### 1.2 安裝 Python 3.9+

```bash
# 下載並安裝 Python
# https://www.python.org/downloads/windows/
# ⚠️ 重要：安裝時勾選 "Add Python to PATH"
```

#### 1.3 安裝 Node.js 16+

```bash
# 下載並安裝 Node.js LTS 版本
# https://nodejs.org/en/download/
# 安裝完成後會自動包含 npm
```

#### 1.4 驗證安裝

打開 **PowerShell** 或 **Command Prompt**，執行：

```bash
python --version     # 應顯示 Python 3.9.x
node --version       # 應顯示 v16.x.x 或更高
npm --version        # 應顯示 npm 版本
git --version        # 應顯示 git 版本
```

### 第二步：克隆專案

#### 2.1 創建工作目錄

```bash
# 在您喜歡的位置創建目錄，例如：
mkdir C:\Projects
cd C:\Projects
```

#### 2.2 克隆 Trading X 專案

```bash
git clone https://github.com/Chang-Shih-Yung/Trading-X.git
cd Trading-X
```

### 第三步：後端設置

#### 3.1 安裝 Python 依賴

```bash
# 在專案根目錄執行
pip install -r requirements.txt
```

如果遇到權限問題，使用：

```bash
pip install --user -r requirements.txt
```

#### 3.2 初始化資料庫

```bash
python -c "from app.core.database import create_tables; import asyncio; asyncio.run(create_tables())"
```

### 第四步：前端設置

#### 4.1 安裝前端依賴

```bash
cd frontend
npm install
```

如果遇到網路問題，可以使用淘寶鏡像：

```bash
npm install --registry https://registry.npmmirror.com
```

### 第五步：啟動服務

#### 5.1 啟動後端服務

**新開一個終端窗口**，在專案根目錄執行：

```bash
# 方法1：使用 uvicorn 直接啟動
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 方法2：如果有依賴問題，使用 python 直接運行
python main.py
```

✅ 成功啟動後會顯示：

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

#### 5.2 啟動前端服務

**另開一個終端窗口**，在 frontend 目錄執行：

```bash
cd frontend
npm run dev
```

✅ 成功啟動後會顯示：

```
Local:   http://localhost:3000/
Network: http://[你的IP]:3000/
```

### 第六步：訪問應用

- **前端界面**: http://localhost:3000
- **後端 API**: http://localhost:8000
- **API 文檔**: http://localhost:8000/docs

## 🛠️ 常見問題解決

### Python 相關問題

#### 問題 1：找不到 python 命令

```bash
# 解決方案1：檢查環境變數
# 將 Python 安裝路徑添加到 PATH 環境變數

# 解決方案2：使用完整路徑
C:\Users\[你的用戶名]\AppData\Local\Programs\Python\Python39\python.exe

# 解決方案3：使用 py 命令
py -m pip install -r requirements.txt
py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 問題 2：pip 安裝失敗

```bash
# 升級 pip
python -m pip install --upgrade pip

# 使用國內鏡像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 如果有 SSL 錯誤
pip install -r requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
```

#### 問題 3：uvicorn 找不到命令

```bash
# 使用 python -m 方式運行
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 或者直接安裝 uvicorn
pip install uvicorn[standard]
```

### Node.js 相關問題

#### 問題 1：npm 安裝緩慢

```bash
# 使用淘寶鏡像
npm config set registry https://registry.npmmirror.com
npm install

# 或者使用 cnpm
npm install -g cnpm --registry=https://registry.npmmirror.com
cnpm install
```

#### 問題 2：權限錯誤

```bash
# 清除 npm 快取
npm cache clean --force

# 刪除 node_modules 重新安裝
rmdir /s node_modules
del package-lock.json
npm install
```

#### 問題 3：端口被占用

```bash
# 查看端口占用
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# 結束占用進程（以端口3000為例）
taskkill /PID [進程ID] /F

# 或者修改端口
npm run dev -- --port 3001
```

### 網路相關問題

#### 問題 1：API 連接失敗

檢查 `frontend/src/main.ts` 中的 API 基礎 URL：

```typescript
// 確保指向正確的後端地址
axios.defaults.baseURL = "http://localhost:8000";
```

#### 問題 2：CORS 錯誤

後端已配置 CORS，如果仍有問題，檢查 `main.py` 中的 CORS 設置：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 確保包含前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🔧 進階配置

### 環境變數設置

創建 `.env` 文件在專案根目錄：

```bash
# 資料庫設置
DATABASE_URL=sqlite:///./tradingx.db

# API 設置
API_HOST=0.0.0.0
API_PORT=8000

# 日誌級別
LOG_LEVEL=INFO
```

### 生產環境部署

#### 後端生產運行

```bash
# 使用 gunicorn (需要先安裝)
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 或使用 uvicorn 生產模式
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 前端生產構建

```bash
cd frontend
npm run build

# 使用靜態服務器運行
npm install -g serve
serve -s dist -l 3000
```

## 📁 專案結構說明

```
Trading-X/
├── app/                    # 後端應用
│   ├── api/               # API 路由
│   ├── core/              # 核心配置
│   ├── models/            # 資料模型
│   ├── schemas/           # 數據驗證
│   └── services/          # 業務邏輯
├── frontend/              # 前端應用
│   ├── src/              # 源代碼
│   ├── public/           # 靜態資源
│   └── dist/             # 構建輸出
├── tests/                 # 測試文件
├── requirements.txt       # Python 依賴
├── main.py               # 後端入口
└── README.md             # 專案說明
```

## 🚦 快速啟動腳本

### Windows 批處理腳本

創建 `start_backend.bat`：

```batch
@echo off
echo 啟動 Trading X 後端服務...
cd /d "%~dp0"
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
```

創建 `start_frontend.bat`：

```batch
@echo off
echo 啟動 Trading X 前端服務...
cd /d "%~dp0\frontend"
npm run dev
pause
```

### PowerShell 腳本

創建 `start_all.ps1`：

```powershell
# 啟動後端
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

# 等待2秒
Start-Sleep -Seconds 2

# 啟動前端
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev"

# 等待5秒後打開瀏覽器
Start-Sleep -Seconds 5
Start-Process "http://localhost:3000"
```

## 📞 技術支援

如果遇到問題，請檢查：

1. **依賴版本**: 確保 Python 3.9+、Node.js 16+
2. **網路連接**: 確保可以訪問 GitHub 和 npm 倉庫
3. **防火牆設置**: 確保端口 3000 和 8000 未被阻擋
4. **日誌輸出**: 查看終端錯誤信息

## 🎯 成功指標

✅ 後端服務正常啟動（http://localhost:8000/docs 可訪問）
✅ 前端界面正常載入（http://localhost:3000 可訪問）
✅ API 連接正常（前端可以獲取後端數據）
✅ 所有功能頁面可以正常切換

---

**祝您使用愉快！如有問題，請查看上述故障排除指南。** 🚀
