"""
🎯 Trading X - X資料夾主程式
整合所有監控系統組件的主要啟動程式

系統架構：
1. 真實數據信號質量控制引擎
2. 即時統一監控管理系統  
3. FastAPI監控API端點
4. Gmail通知整合
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加父目錄到路徑以導入app模組
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 導入backend的監控系統
from backend.phase4_output_monitoring.real_time_unified_monitoring_manager import unified_monitoring_manager
from backend.phase4_output_monitoring.monitoring_api import include_monitoring_routes

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('x_monitoring.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 創建FastAPI應用
app = FastAPI(
    title="Trading X - 獨立監控系統",
    description="基於真實數據源的信號質量控制和監控系統",
    version="1.0.0",
    docs_url="/x-docs",
    redoc_url="/x-redoc"
)

# 添加CORS中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含監控API路由
include_monitoring_routes(app)

@app.on_event("startup")
async def startup_event():
    """應用啟動事件"""
    logger.info("🎯 Trading X 監控系統啟動...")
    
    try:
        logger.info("✅ 監控系統準備就緒")
        logger.info("� 系統功能: 信號質量控制、數據完整性檢查、智能通知")
        logger.info("🌐 API文檔: http://localhost:8001/x-docs")
        
    except Exception as e:
        logger.error(f"❌ 系統啟動失敗: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """應用關閉事件"""
    logger.info("🔄 系統關閉中...")
    
    try:
        await unified_monitoring_manager.stop_monitoring()
        logger.info("✅ 系統已安全關閉")
        
    except Exception as e:
        logger.error(f"❌ 系統關閉錯誤: {e}")

@app.get("/")
async def root():
    """系統根路徑"""
    return {
        "message": "🎯 Trading X 獨立監控系統",
        "version": "1.0.0",
        "status": "running",
        "monitoring_status": "ready" if not unified_monitoring_manager.monitoring_enabled else "active",
        "api_docs": "/x-docs",
        "admin_panel": "/x-redoc"
    }

@app.get("/x-info")
async def system_info():
    """系統詳細信息"""
    try:
        dashboard_data = await unified_monitoring_manager.get_monitoring_dashboard_data()
        
        return {
            "system": {
                "name": "Trading X 獨立監控系統",
                "version": "1.0.0",
                "description": "基於真實數據源的信號質量控制和監控系統"
            },
            "data_sources": {
                "phase1b": "波動適應性分析引擎",
                "phase1c": "信號標準化處理引擎", 
                "phase3": "市場深度分析引擎",
                "pandas_ta": "技術指標引擎"
            },
            "monitoring": {
                "enabled": unified_monitoring_manager.monitoring_enabled,
                "symbols": unified_monitoring_manager.symbols,
                "interval": f"{unified_monitoring_manager.processing_interval}秒",
                "statistics": dashboard_data.get("statistics", {})
            },
            "api_endpoints": {
                "start_monitoring": "POST /api/v1/x-monitoring/start",
                "stop_monitoring": "POST /api/v1/x-monitoring/stop", 
                "dashboard": "GET /api/v1/x-monitoring/dashboard",
                "status": "GET /api/v1/x-monitoring/status",
                "recent_signals": "GET /api/v1/x-monitoring/signals/recent",
                "manual_trigger": "POST /api/v1/x-monitoring/signals/manual-trigger"
            }
        }
        
    except Exception as e:
        return {
            "error": f"系統信息獲取失敗: {str(e)}",
            "system": {
                "name": "Trading X 獨立監控系統",
                "version": "1.0.0",
                "status": "error"
            }
        }

async def main():
    """主程式入口"""
    try:
        logger.info("🚀 啟動 Trading X 獨立監控系統...")
        
        # 運行FastAPI服務器
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=8001,  # 使用不同端口避免與主系統衝突
            log_level="info",
            reload=False  # 生產環境建議關閉
        )
        
        server = uvicorn.Server(config)
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("👋 用戶中斷，系統正在關閉...")
    except Exception as e:
        logger.error(f"❌ 系統運行錯誤: {e}")
        raise

if __name__ == "__main__":
    # 直接運行主程式
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 系統已關閉")
    except Exception as e:
        print(f"❌ 系統錯誤: {e}")
        sys.exit(1)
