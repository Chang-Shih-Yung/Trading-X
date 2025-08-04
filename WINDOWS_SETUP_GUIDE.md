# Trading-X Windows 環境設置指南

## 方法一：自動安裝（推薦）

以管理員身份運行 PowerShell，然後執行：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
cd "c:\Users\User\Desktop\Trading-X"
.\setup_windows_environment.ps1
```

## 方法二：手動安裝

### 步驟 1: 安裝 Python

1. 前往 https://www.python.org/downloads/windows/
2. 下載 Python 3.11.x (推薦) 或 3.9+ 版本
3. 運行安裝程序時，**務必勾選 "Add Python to PATH"**
4. 選擇 "Install Now" 完成安裝

### 步驟 2: 驗證安裝

打開新的 PowerShell 窗口，運行：

```powershell
python --version
pip --version
```

如果看到版本號，說明安裝成功。

### 步驟 3: 創建虛擬環境

```powershell
cd "c:\Users\User\Desktop\Trading-X"
python -m venv venv
```

### 步驟 4: 激活虛擬環境

```powershell
.\venv\Scripts\Activate.ps1
```

如果出現執行策略錯誤，請先運行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 步驟 5: 安裝依賴

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 步驟 6: 啟動後端服務

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 常見問題

### 問題 1: 'python' 不是內部或外部命令
- 解決方案：重新安裝 Python 並確保勾選 "Add Python to PATH"
- 或者手動添加 Python 到系統 PATH

### 問題 2: 執行策略錯誤
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 問題 3: pip 安裝速度慢
```powershell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

## 驗證安裝

啟動成功後，您應該看到：
- 後端服務：http://localhost:8000
- API 文檔：http://localhost:8000/docs

## 下次啟動

創建快捷腳本 `start.ps1`：

```powershell
cd "c:\Users\User\Desktop\Trading-X"
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
