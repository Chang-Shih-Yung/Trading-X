# 🎯 狙擊手測試端點

from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_sniper():
    """測試狙擊手API是否正常工作"""
    return {
        "message": "狙擊手測試API正常",
        "status": "ok"
    }
