from pydantic import BaseModel, Field
from typing import Dict, Optional, Any
from datetime import datetime

class StrategyBase(BaseModel):
    name: str = Field(..., description="策略名稱")
    description: Optional[str] = Field(None, description="策略描述")
    config: Dict[str, Any] = Field(..., description="策略配置")

class StrategyCreate(StrategyBase):
    created_by: Optional[str] = Field(None, description="創建者")

class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class StrategyResponse(StrategyBase):
    id: int
    is_active: bool
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class StrategyPreset(BaseModel):
    name: str
    description: str
    config: Dict[str, Any]
    category: str
