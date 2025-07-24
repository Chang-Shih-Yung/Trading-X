from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta

from app.services.market_data import MarketDataService
from app.services.technical_indicators import TechnicalIndicatorsService
from app.schemas.market import MarketDataResponse, IndicatorResponse

router = APIRouter()

@router.get("/price/{symbol}")
async def get_current_price(symbol: str, exchange: str = "binance"):
    """獲取當前價格"""
    try:
        market_service = MarketDataService()
        price = await market_service.get_latest_price(symbol, exchange)
        
        if price is None:
            raise HTTPException(status_code=404, detail=f"無法獲取 {symbol} 的價格")
        
        return {
            "symbol": symbol,
            "price": price,
            "exchange": exchange,
            "timestamp": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取價格失敗: {str(e)}")

@router.get("/klines/{symbol}")
async def get_klines(
    symbol: str,
    timeframe: str = "1h",
    limit: int = Query(100, le=1000),
    exchange: str = "binance"
):
    """獲取K線數據"""
    try:
        market_service = MarketDataService()
        df = await market_service.get_historical_data(symbol, timeframe, limit, exchange)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"無法獲取 {symbol} 的K線數據")
        
        # 轉換為JSON格式
        klines = []
        for _, row in df.iterrows():
            klines.append({
                "timestamp": row['timestamp'],
                "open": float(row['open']),
                "high": float(row['high']),
                "low": float(row['low']),
                "close": float(row['close']),
                "volume": float(row['volume'])
            })
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "exchange": exchange,
            "count": len(klines),
            "data": klines
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取K線數據失敗: {str(e)}")

@router.get("/indicators/{symbol}")
async def get_indicators(
    symbol: str,
    timeframe: str = "1h",
    limit: int = Query(100, le=500)
):
    """獲取技術指標"""
    try:
        market_service = MarketDataService()
        df = await market_service.get_market_data_from_db(symbol, timeframe, limit)
        
        if df.empty:
            # 如果資料庫沒有數據，從交易所獲取
            df = await market_service.get_historical_data(symbol, timeframe, limit)
            if not df.empty:
                await market_service.save_market_data(df)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"無法獲取 {symbol} 的數據")
        
        # 計算技術指標
        indicators = TechnicalIndicatorsService.calculate_all_indicators(df)
        
        # 格式化返回結果
        indicator_data = {}
        for name, indicator in indicators.items():
            indicator_data[name] = {
                "name": indicator.name,
                "value": indicator.value,
                "signal": indicator.signal,
                "strength": indicator.strength,
                "metadata": indicator.metadata
            }
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": datetime.utcnow(),
            "indicators": indicator_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取技術指標失敗: {str(e)}")

@router.get("/orderbook/{symbol}")
async def get_orderbook(symbol: str, exchange: str = "binance"):
    """獲取訂單簿"""
    try:
        market_service = MarketDataService()
        orderbook = await market_service.get_orderbook(symbol, exchange)
        
        if orderbook is None:
            raise HTTPException(status_code=404, detail=f"無法獲取 {symbol} 的訂單簿")
        
        return {
            "symbol": symbol,
            "exchange": exchange,
            "timestamp": orderbook.get('timestamp'),
            "bids": orderbook.get('bids', []),
            "asks": orderbook.get('asks', [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取訂單簿失敗: {str(e)}")

@router.get("/symbols")
async def get_available_symbols():
    """獲取可用的交易對列表"""
    try:
        # 主要關注的加密貨幣交易對
        symbols = [
            "BTC/USDT", "ETH/USDT", "BNB/USDT", "ADA/USDT", "XRP/USDT",
            "DOT/USDT", "LINK/USDT", "LTC/USDT", "BCH/USDT", "UNI/USDT",
            "MATIC/USDT", "SOL/USDT", "AVAX/USDT", "ATOM/USDT", "ALGO/USDT",
            "VET/USDT", "FIL/USDT", "TRX/USDT", "EOS/USDT", "THETA/USDT"
        ]
        
        timeframes = ["1m", "5m", "15m", "1h", "4h", "1d"]
        
        return {
            "symbols": symbols,
            "timeframes": timeframes,
            "total_symbols": len(symbols),
            "supported_exchanges": ["binance", "okx"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取交易對列表失敗: {str(e)}")

@router.post("/sync/{symbol}")
async def sync_historical_data(
    symbol: str,
    timeframe: str = "1h",
    days: int = Query(30, le=365, description="同步天數")
):
    """同步歷史數據到資料庫"""
    try:
        market_service = MarketDataService()
        
        # 計算需要的K線數量
        timeframe_minutes = {
            "1m": 1, "5m": 5, "15m": 15, "1h": 60, "4h": 240, "1d": 1440
        }
        
        minutes_per_day = 1440
        limit = int((days * minutes_per_day) / timeframe_minutes.get(timeframe, 60))
        limit = min(limit, 1000)  # API限制
        
        # 獲取歷史數據
        df = await market_service.get_historical_data(symbol, timeframe, limit)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"無法獲取 {symbol} 的歷史數據")
        
        # 儲存到資料庫
        await market_service.save_market_data(df)
        
        return {
            "success": True,
            "message": f"成功同步 {symbol} {timeframe} 數據",
            "records_synced": len(df),
            "date_range": {
                "start": df['timestamp'].min().isoformat(),
                "end": df['timestamp'].max().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步數據失敗: {str(e)}")

@router.get("/market-summary")
async def get_market_summary():
    """獲取市場概況"""
    try:
        market_service = MarketDataService()
        
        # 主要交易對價格
        major_symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
        market_data = []
        
        for symbol in major_symbols:
            try:
                price = await market_service.get_latest_price(symbol)
                if price:
                    # 獲取24小時數據計算變化
                    df = await market_service.get_historical_data(symbol, "1h", 24)
                    if not df.empty:
                        prev_price = df['close'].iloc[0]
                        change_24h = ((price - prev_price) / prev_price) * 100
                    else:
                        change_24h = 0
                    
                    market_data.append({
                        "symbol": symbol,
                        "price": price,
                        "change_24h": round(change_24h, 2)
                    })
            except Exception:
                continue
        
        return {
            "timestamp": datetime.utcnow(),
            "market_data": market_data,
            "total_symbols": len(market_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取市場概況失敗: {str(e)}")
