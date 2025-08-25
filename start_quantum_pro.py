#!/usr/bin/env python3
"""
Trading X Quantum Pro 啟動腳本
"""

import sys
from pathlib import Path

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 啟動量子決策系統
if __name__ == "__main__":
    try:
        import asyncio

        from quantum_pro.quantum_launcher import main
        
        print("正在啟動 Trading X Quantum Pro 系統...")
        asyncio.run(main())
        
    except ImportError as e:
        print(f"導入錯誤: {e}")
        print("請確保所有依賴已安裝: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"啟動失敗: {e}")
        sys.exit(1)
