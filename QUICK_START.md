# 🚀 Trading X - Windows 快速開始

## 一分鐘快速啟動

### 1️⃣ 環境準備（僅需一次）

下載並安裝以下軟體（按順序）：

1. **Git**: https://git-scm.com/download/win
2. **Python 3.9+**: https://www.python.org/downloads/ （⚠️ 勾選"Add to PATH"）
3. **Node.js**: https://nodejs.org/ （選擇 LTS 版本）

### 2️⃣ 克隆專案

```bash
git clone https://github.com/Chang-Shih-Yung/Trading-X.git
cd Trading-X
```

### 3️⃣ 一鍵啟動

**方法 1: 使用批處理文件**

1. 雙擊 `start_backend.bat` 啟動後端
2. 雙擊 `start_frontend.bat` 啟動前端
3. 瀏覽器打開 http://localhost:3000

**方法 2: 使用 PowerShell（推薦）**

```powershell
# 右鍵專案資料夾，選擇 "在終端中打開"
.\start_all.ps1
```

**方法 3: 手動啟動**

```bash
# 終端1 - 後端
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 終端2 - 前端
cd frontend
npm install
npm run dev
```

## ✅ 驗證成功

- 後端: http://localhost:8000/docs 顯示 API 文檔
- 前端: http://localhost:3000 顯示交易平台界面

## 🔧 常見問題一鍵修復

**Python 找不到:**

```bash
py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**npm 安裝慢:**

```bash
npm config set registry https://registry.npmmirror.com
```

**端口被占用:**

```bash
# 查看並結束進程
netstat -ano | findstr :8000
taskkill /PID [進程ID] /F
```

---

**完整說明請參考: WINDOWS_SETUP_GUIDE.md**
