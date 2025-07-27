"""
智能時間配置管理API
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import json
import os
from pydantic import BaseModel

from app.services.smart_timing_service import smart_timing_service

router = APIRouter()

class SmartTimingConfigUpdate(BaseModel):
    """智能時間配置更新模型"""
    config: Dict[str, Any]

@router.get("/smart-timing/config")
async def get_smart_timing_config():
    """獲取當前智能時間配置"""
    try:
        return {
            "success": True,
            "config": smart_timing_service.config,
            "message": "智能時間配置獲取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取配置失敗: {str(e)}")

@router.post("/smart-timing/config")
async def update_smart_timing_config(config_update: SmartTimingConfigUpdate):
    """更新智能時間配置"""
    try:
        # 驗證配置格式
        if "smart_timing" not in config_update.config:
            raise ValueError("配置必須包含 'smart_timing' 字段")
        
        # 保存到文件
        config_path = os.path.join(
            os.path.dirname(__file__), 
            "..", "..", "..", 
            "config", 
            "smart_timing_config.json"
        )
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_update.config, f, indent=2, ensure_ascii=False)
        
        # 重新載入配置
        smart_timing_service.config = config_update.config
        
        return {
            "success": True,
            "message": "智能時間配置更新成功",
            "config": config_update.config
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"更新配置失敗: {str(e)}")

@router.get("/smart-timing/test")
async def test_smart_timing_calculation(
    timeframe: str = "5m",
    signal_strength: float = 0.8,
    signal_type: str = "MOMENTUM_BREAKOUT"
):
    """測試智能時間計算"""
    try:
        result = smart_timing_service.calculate_smart_expiry_minutes(
            base_timeframe=timeframe,
            signal_strength=signal_strength,
            signal_type=signal_type
        )
        
        return {
            "success": True,
            "result": result,
            "message": "智能時間計算測試成功"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"測試失敗: {str(e)}")

@router.get("/smart-timing/stats")
async def get_smart_timing_stats():
    """獲取智能時間統計信息"""
    try:
        # 這裡可以添加統計邏輯，比如不同時間長度的成功率等
        return {
            "success": True,
            "stats": {
                "enabled": smart_timing_service.config["smart_timing"]["enable_smart_expiry"],
                "total_signal_types": len(smart_timing_service.config["smart_timing"]["signal_type_multipliers"]),
                "timeframe_options": list(smart_timing_service.config["smart_timing"]["base_timeframes"].keys()),
                "limits": smart_timing_service.config["smart_timing"]["limits"]
            },
            "message": "統計信息獲取成功"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取統計信息失敗: {str(e)}")
