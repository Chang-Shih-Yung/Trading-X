#!/usr/bin/env python3
"""
🔍 Trading X - 市場狀況提取器 (階段2實施)
從現有Phase1/2/4系統提取真實市場狀況進行參數優化分析
"""

import json
import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import statistics

logger = logging.getLogger(__name__)

# 導入真實數據連接器
sys.path.append('/Users/henrychang/Desktop/Trading-X/X/backend/shared_core')
try:
    from binance_data_connector import binance_connector
except ImportError:
    logger.warning("無法導入binance_data_connector，將使用備用數據源")
    binance_connector = None

@dataclass
class MarketCondition:
    """真實市場狀況數據結構"""
    timestamp: datetime
    symbol: str
    price: float
    volume: float
    volatility: float
    market_regime: str
    signal_quality_score: float
    processing_latency_ms: float

class MarketConditionExtractor:
    """市場狀況提取器 - 基於真實Phase系統數據"""
    
    def __init__(self):
        """初始化提取器"""
        self.market_conditions_history = []
        self.phase1_config_path = Path("/Users/henrychang/Desktop/Trading-X/X/backend/phase1_signal_generation/phase1a_basic_signal_generation/phase1a_basic_signal_generation.json")
        # 從真實配置中獲取的7個目標幣種
        self.target_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT"]
        logger.info("🔍 市場狀況提取器初始化完成")
    
    async def extract_all_symbols_market_conditions(self) -> Dict[str, MarketCondition]:
        """提取所有目標幣種的真實市場狀況"""
        results = {}
        
        for symbol in self.target_symbols:
            logger.info(f"📊 提取 {symbol} 真實市場狀況...")
            condition = await self.extract_current_market_conditions(symbol)
            if condition:
                results[symbol] = condition
        
        logger.info(f"✅ 成功提取 {len(results)}/{len(self.target_symbols)} 個幣種的真實市場狀況")
        return results
    
    async def extract_current_market_conditions(self, symbol: str = "BTCUSDT") -> Optional[MarketCondition]:
        """提取當前真實市場狀況"""
        try:
            logger.info(f"📊 提取 {symbol} 當前市場狀況...")
            
            # 從Phase1提取真實配置和實時數據
            phase1_data = await self._extract_phase1_real_data(symbol)
            phase2_data = await self._extract_phase2_real_data(symbol)
            phase4_data = await self._extract_phase4_real_data(symbol)
            
            if not phase1_data:
                logger.warning("無法獲取真實Phase1數據")
                return None
            
            # 使用真實數據構建市場狀況
            market_condition = MarketCondition(
                timestamp=datetime.now(),
                symbol=symbol,
                price=phase1_data.get('real_price', 0.0),
                volume=phase1_data.get('real_volume', 0.0),
                volatility=phase1_data.get('real_volatility', 0.0),
                market_regime=phase1_data.get('detected_regime', 'UNKNOWN'),
                signal_quality_score=phase2_data.get('real_quality_score', 0.0),
                processing_latency_ms=phase4_data.get('real_latency_ms', 0.0)
            )
            
            # 保存歷史記錄
            self.market_conditions_history.append(market_condition)
            if len(self.market_conditions_history) > 500:
                self.market_conditions_history.pop(0)
            
            logger.info(f"✅ 成功提取真實市場狀況: {market_condition.market_regime}, 價格: ${market_condition.price:,.2f}")
            return market_condition
            
        except Exception as e:
            logger.error(f"❌ 真實市場狀況提取失敗: {e}")
            return None
    
    async def _extract_phase1_real_data(self, symbol: str) -> Dict[str, Any]:
        """從Phase1系統提取真實市場數據"""
        try:
            # 讀取Phase1真實配置
            with open(self.phase1_config_path, 'r', encoding='utf-8') as f:
                phase1_config = json.load(f)
            
            # 提取當前參數
            regime_config = phase1_config['phase1a_basic_signal_generation_dependency']['configuration']['dynamic_parameter_integration']['market_regime_detection']
            current_confidence_threshold = regime_config['regime_types']['BULL_TREND']['confidence_threshold']
            
            logger.info(f"📋 當前confidence_threshold: {current_confidence_threshold}")
            
            # 🔥 獲取真實Binance市場數據
            real_market_data = await self._fetch_real_binance_data(symbol)
            
            return {
                'real_price': real_market_data.get('price', 0.0),
                'real_volume': real_market_data.get('volume', 0.0),
                'real_volatility': real_market_data.get('volatility', 0.0),
                'detected_regime': self._detect_current_regime_from_real_data(real_market_data),
                'current_parameters': {
                    'confidence_threshold': current_confidence_threshold
                }
            }
            
        except Exception as e:
            logger.error(f"Phase1真實數據提取錯誤: {e}")
            return {}
    
    async def _fetch_real_binance_data(self, symbol: str) -> Dict[str, Any]:
        """獲取真實Binance市場數據"""
        try:
            # 使用標準庫urllib請求Binance API獲取真實數據
            import urllib.request
            import urllib.parse
            
            # Binance 24hr ticker API (真實數據)
            base_url = "https://api.binance.com/api/v3/ticker/24hr"
            params = urllib.parse.urlencode({"symbol": symbol})
            url = f"{base_url}?{params}"
            
            # 發送真實API請求
            with urllib.request.urlopen(url, timeout=10) as response:
                if response.status == 200:
                    data_bytes = response.read()
                    data = json.loads(data_bytes.decode('utf-8'))
                    
                    # 提取真實市場數據
                    current_price = float(data['lastPrice'])
                    volume_24h = float(data['volume'])
                    price_change_24h_pct = float(data['priceChangePercent'])
                    high_24h = float(data['highPrice'])
                    low_24h = float(data['lowPrice'])
                    
                    # 計算真實波動率 (基於24h高低價)
                    volatility = abs(high_24h - low_24h) / current_price if current_price > 0 else 0
                    
                    logger.info(f"📈 真實Binance數據: 價格=${current_price:,.2f}, 24h變化={price_change_24h_pct:+.3f}%, 成交量={volume_24h:,.0f}")
                    
                    return {
                        'price': current_price,
                        'volume': volume_24h,
                        'volatility': volatility,
                        'price_change_24h': price_change_24h_pct / 100,  # 轉為小數
                        'high_24h': high_24h,
                        'low_24h': low_24h,
                        'data_source': 'BINANCE_API_REAL'
                    }
                else:
                    logger.error(f"Binance API請求失敗: HTTP {response.status}")
                    return {}
                        
        except Exception as e:
            logger.error(f"真實Binance數據獲取失敗: {e}")
            return {}
    
    async def _extract_phase2_real_data(self, symbol: str) -> Dict[str, Any]:
        """從Phase2系統提取真實信號評分數據"""
        try:
            # 這裡應該從真實運行的Phase2系統獲取信號評分
            # 目前先從配置文件中讀取可用的評分標準
            phase2_config_path = self.phase1_config_path.parent.parent.parent / "phase2_pre_evaluation"
            
            # 模擬從Phase2系統讀取當前信號質量評分
            # 在真實環境中，這會是Phase2系統的實時輸出
            return {
                'real_quality_score': 0.0  # 暫時返回0，等待Phase2系統連接
            }
            
        except Exception as e:
            logger.error(f"Phase2真實數據提取錯誤: {e}")
            return {}
    
    async def _extract_phase4_real_data(self, symbol: str) -> Dict[str, Any]:
        """從Phase4系統提取真實監控數據"""
        try:
            # 這裡應該從真實運行的Phase4監控系統獲取性能數據
            # 目前先返回基本值
            return {
                'real_latency_ms': 0.0  # 暫時返回0，等待Phase4系統連接
            }
            
        except Exception as e:
            logger.error(f"Phase4真實數據提取錯誤: {e}")
            return {}
    
    def _detect_current_regime_from_real_data(self, real_data: Dict[str, Any]) -> str:
        """基於真實數據檢測市場制度"""
        try:
            price_change_24h = real_data.get('price_change_24h', 0)
            volatility = real_data.get('volatility', 0)
            
            # 基於真實數據的制度檢測邏輯
            if price_change_24h > 0.02 and volatility < 0.05:
                return 'BULL_TREND'
            elif price_change_24h < -0.02 and volatility < 0.05:
                return 'BEAR_TREND'
            elif volatility > 0.08:
                return 'VOLATILE'
            else:
                return 'SIDEWAYS'
                
        except Exception as e:
            logger.error(f"市場制度檢測失敗: {e}")
            return 'UNKNOWN'
    
    def get_optimization_recommendation(self) -> Dict[str, Any]:
        """為參數優化提供建議"""
        if not self.market_conditions_history:
            return {
                'current_regime': 'UNKNOWN',
                'recommendation': 'COLLECT_MORE_DATA'
            }
        
        # 分析最近市場狀況
        recent_conditions = self.market_conditions_history[-10:]
        regimes = [c.market_regime for c in recent_conditions]
        current_regime = max(set(regimes), key=regimes.count)
        
        # 生成優化建議
        if current_regime in ['BULL_TREND', 'BEAR_TREND']:
            recommendation = 'TRENDING_OPTIMIZATION'
        else:
            recommendation = 'RANGE_OPTIMIZATION'
        
        return {
            'current_regime': current_regime,
            'recommendation': recommendation,
            'data_points': len(self.market_conditions_history)
        }

async def test_market_extractor():
    """測試市場狀況提取器 - 使用真實數據"""
    print("🔍 Trading X - 市場狀況提取器測試 (真實數據)")
    print("=" * 60)
    
    # 創建提取器
    extractor = MarketConditionExtractor()
    
    print(f"\n📊 Step 1: 提取所有 {len(extractor.target_symbols)} 個目標幣種的真實市場狀況...")
    all_conditions = await extractor.extract_all_symbols_market_conditions()
    
    if all_conditions:
        print(f"✅ 成功提取 {len(all_conditions)} 個幣種的真實市場狀況:")
        for symbol, condition in all_conditions.items():
            print(f"   {symbol}: ${condition.price:,.2f} | {condition.market_regime} | 波動率: {condition.volatility:.4f}")
    
    # 真實數據收集測試
    print(f"\n🔄 Step 2: 真實數據收集測試...")
    print(f"   正在收集多個時間點的真實市場數據...")
    
    for i in range(5):  # 減少測試次數，使用真實數據
        symbol = extractor.target_symbols[i % len(extractor.target_symbols)]
        await extractor.extract_current_market_conditions(symbol)
        print(f"   ✓ 收集第 {i+1} 個真實數據點 ({symbol})")
    
    print(f"✅ 已收集 {len(extractor.market_conditions_history)} 個真實數據點")
    
    print(f"\n🎯 Step 3: 基於真實數據生成優化建議...")
    recommendation = extractor.get_optimization_recommendation()
    print(f"   當前制度: {recommendation['current_regime']}")
    print(f"   優化建議: {recommendation['recommendation']}")
    print(f"   真實數據點數: {recommendation['data_points']}")
    
    print(f"\n✅ 真實市場狀況提取器測試完成！")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_market_extractor())
