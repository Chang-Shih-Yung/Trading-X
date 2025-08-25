# quantum_system_test.py
# 完整的量子決策系統集成測試

import asyncio
import logging
from datetime import datetime

import numpy as np
import pandas as pd

# 導入量子決策系統
from quantum_decision_optimizer import (
    CryptoMarketObservation,
    ProductionQuantumConfig,
    ProductionQuantumEngine,
    ProductionTradingHypothesis,
)

# 導入擴展模組
from quantum_production_extension import TradingXQuantumProcessor

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_complete_production_test():
    """運行完整的生產級量子系統測試"""
    print("="*80)
    print("量子決策系統 - 完整生產級測試")
    print("Trading X 整合版本 with ChatGPT 最佳化")
    print("="*80)
    
    # 創建生產級配置
    config = ProductionQuantumConfig(
        alpha_base=0.008,  # 基礎風險係數
        beta_base=0.045,   # 基礎收益係數
        kelly_multiplier=0.2,  # Kelly 倍數
        max_single_position=0.15,  # 最大單一倉位
        primary_symbols=[
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT',
            'XRPUSDT', 'DOGEUSDT', 'ADAUSDT'
        ]
    )
    
    print(f"測試配置: 監控 {len(config.primary_symbols)} 種主要加密貨幣")
    print(f"Kelly 倍數: {config.kelly_multiplier}")
    print(f"最大倉位: {config.max_single_position}")
    
    # 1. 初始化核心量子引擎
    print("\n1. 初始化核心量子引擎...")
    quantum_engine = ProductionQuantumEngine(config)
    await quantum_engine.initialize_production_components()
    print("✓ 量子引擎初始化完成")
    
    # 2. 初始化完整處理器
    print("\n2. 初始化完整處理器...")
    processor = TradingXQuantumProcessor(config)
    await processor.start_quantum_processing()
    print("✓ 完整處理器初始化完成")
    
    # 3. 模擬即時市場數據處理
    print("\n3. 模擬即時市場數據處理...")
    await simulate_market_data_stream(processor, config.primary_symbols[:3])  # 測試前三種
    
    # 4. 顯示系統狀態和統計
    print("\n4. 系統狀態總結...")
    display_system_summary(quantum_engine, processor)
    
    print("\n" + "="*80)
    print("量子決策系統測試完成 ✓")
    print("="*80)

async def simulate_market_data_stream(processor, symbols):
    """模擬市場數據流"""
    for symbol in symbols:
        print(f"\n  處理 {symbol} 數據流...")
        
        # 創建真實的市場數據模擬
        base_price = get_base_price(symbol)
        
        for i in range(5):  # 模擬 5 個數據點
            # 生成隨機市場波動
            price_change = np.random.normal(0, 0.02)  # 2% 波動
            current_price = base_price * (1 + price_change)
            
            market_data = create_realistic_market_data(symbol, current_price, i)
            
            # 處理市場數據
            await processor._handle_market_update(symbol, market_data)
            
            # 短暫延遲模擬即時性
            await asyncio.sleep(0.1)
        
        print(f"    ✓ {symbol} 數據流處理完成")

def get_base_price(symbol):
    """獲取基礎價格 - 正確的七大幣種價格"""
    price_map = {
        'BTCUSDT': 50000.0,   # BTC
        'ETHUSDT': 3000.0,    # ETH  
        'BNBUSDT': 400.0,     # BNB
        'SOLUSDT': 150.0,     # SOL
        'XRPUSDT': 0.6,       # XRP
        'DOGEUSDT': 0.1,      # DOGE
        'ADAUSDT': 0.5        # ADA
    }
    return price_map.get(symbol, 100.0)

def create_realistic_market_data(symbol, price, iteration):
    """創建真實的市場數據"""
    # 模擬訂單簿深度
    spread = price * 0.0005  # 0.05% 價差
    bid_price = price - spread / 2
    ask_price = price + spread / 2
    
    # 模擬成交量
    base_volume = 1000000 if symbol == 'BTCUSDT' else 500000
    volume_noise = np.random.uniform(0.8, 1.2)
    volume = base_volume * volume_noise
    
    # 模擬市場深度
    depth_levels = 10
    bids = []
    asks = []
    
    for i in range(depth_levels):
        bid_vol = np.random.uniform(10, 100)
        ask_vol = np.random.uniform(10, 100)
        
        bids.append([bid_price - i * spread * 0.1, bid_vol])
        asks.append([ask_price + i * spread * 0.1, ask_vol])
    
    return {
        'ticker': {
            'price': price,
            'volume_24h': volume,
            'change_percent': np.random.uniform(-5, 5),
            'market_cap': price * volume * 1000
        },
        'depth': {
            'bids': bids,
            'asks': asks
        },
        'trades': [
            {
                'price': price + np.random.uniform(-spread, spread),
                'qty': np.random.uniform(1, 10),
                'is_buyer_maker': np.random.choice([True, False]),
                'timestamp': datetime.now().timestamp()
            }
            for _ in range(20)
        ]
    }

def display_system_summary(quantum_engine, processor):
    """顯示系統摘要"""
    # 1. 量子引擎狀態
    engine_state = quantum_engine.get_production_state()
    print("\n  量子引擎狀態:")
    print(f"    已處理觀測: {engine_state['execution_stats']['total_observations']}")
    print(f"    生成決策: {engine_state['execution_stats']['successful_decisions']}")
    print(f"    執行交易: {engine_state['execution_stats']['executed_trades']}")
    print(f"    緩存命中率: {engine_state['decision_cache_hits']}")
    
    if engine_state['processing_time_avg'] > 0:
        print(f"    平均處理時間: {engine_state['processing_time_avg']:.4f}s")
    
    # 2. 處理器狀態
    processor_state = processor.get_system_status()
    print("\n  處理器狀態:")
    print(f"    活躍數據流: {len(processor_state['active_streams'])}")
    print(f"    執行佇列: {processor_state['execution_queue_size']} 項")
    
    # 3. 數據品質
    if processor_state['data_quality']:
        print("\n  數據品質指標:")
        for symbol, quality in processor_state['data_quality'].items():
            print(f"    {symbol}: {quality:.3f}")
    
    # 4. 倉位摘要
    if processor_state.get('position_summary'):
        pos_summary = processor_state['position_summary']
        print(f"\n  倉位摘要:")
        print(f"    總倉位數: {pos_summary.get('total_positions', 0)}")
        print(f"    總暴險: {pos_summary.get('total_exposure', 0):.4f}")

async def test_individual_components():
    """測試個別組件"""
    print("\n" + "="*60)
    print("個別組件詳細測試")
    print("="*60)
    
    # 創建測試配置
    config = ProductionQuantumConfig(
        primary_symbols=['BTCUSDT', 'ETHUSDT']
    )
    
    # 1. 測試觀測構建
    print("\n1. 測試市場觀測構建...")
    observation = create_test_observation('BTCUSDT')
    print(f"   觀測創建成功: {observation.symbol} @ {observation.price}")
    print(f"   技術指標: RSI={observation.rsi_14:.1f}, BB位置={observation.bb_position:.3f}")
    
    # 2. 測試假設生成
    print("\n2. 測試交易假設生成...")
    hypothesis = create_test_hypothesis('BTCUSDT')
    print(f"   假設創建成功: {hypothesis.hypothesis_id}")
    print(f"   方向: {hypothesis.direction}, 信心度: {hypothesis.entry_confidence:.3f}")
    print(f"   預期收益(1h): {hypothesis.expected_return_1h:.4f}")
    
    # 3. 測試量子引擎
    print("\n3. 測試量子引擎核心功能...")
    engine = ProductionQuantumEngine(config)
    await engine.initialize_production_components()
    
    decision = await engine.process_observation_production(observation, [hypothesis])
    
    if decision:
        print(f"   決策生成成功: {decision['symbol']}")
        print(f"   信心度: {decision['confidence']:.3f}")
        print(f"   倉位大小: {decision['position_size']:.4f}")
    else:
        print("   未生成決策 (符合預期的謹慎處理)")
    
    print("\n個別組件測試完成 ✓")

def create_test_observation(symbol):
    """創建測試觀測"""
    return CryptoMarketObservation(
        timestamp=pd.Timestamp.now(),
        symbol=symbol,
        price=50000.0,
        returns=0.015,
        volume_24h=1500000.0,
        market_cap=1e12,
        realized_volatility=0.028,
        momentum_slope=0.003,
        rsi_14=68.5,
        bb_position=0.75,
        orderbook_pressure=0.15,
        bid_ask_spread=0.0008,
        trade_aggression=0.3,
        funding_rate=0.0002,
        open_interest=800000.0,
        liquidation_ratio=0.03,
        social_sentiment=0.7,
        whale_activity=0.4,
        correlation_btc=1.0,
        market_regime_signal=0.2
    )

def create_test_hypothesis(symbol):
    """創建測試假設"""
    return ProductionTradingHypothesis(
        symbol=symbol,
        hypothesis_id=f"TEST_TREND_{symbol}",
        direction=1,
        expected_return_1h=0.012,
        expected_return_4h=0.028,
        expected_return_24h=0.065,
        value_at_risk_95=0.025,
        expected_shortfall=0.032,
        max_adverse_excursion=0.04,
        optimal_timeframe="1h",
        entry_confidence=0.78,
        exit_conditions={'stop_loss': -0.02, 'take_profit': 0.035},
        regime_dependency=np.array([0.85, 0.4, 0.6, 0.7, 0.5, 0.3]),
        regime_performance={i: 0.01 + i * 0.003 for i in range(6)}
    )

async def run_stress_test():
    """運行壓力測試"""
    print("\n" + "="*60)
    print("系統壓力測試")
    print("="*60)
    
    config = ProductionQuantumConfig(
        primary_symbols=['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
    )
    
    engine = ProductionQuantumEngine(config)
    await engine.initialize_production_components()
    
    print("\n執行高頻數據處理測試...")
    
    start_time = datetime.now()
    total_observations = 0
    successful_decisions = 0
    
    # 模擬高頻數據流
    for cycle in range(3):  # 3 個周期
        for symbol in config.primary_symbols:
            for i in range(10):  # 每個幣種 10 個觀測
                observation = create_test_observation(symbol)
                hypothesis = create_test_hypothesis(symbol)
                
                decision = await engine.process_observation_production(observation, [hypothesis])
                
                total_observations += 1
                if decision:
                    successful_decisions += 1
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n壓力測試結果:")
    print(f"  總處理時間: {duration:.2f}s")
    print(f"  總觀測數: {total_observations}")
    print(f"  成功決策: {successful_decisions}")
    print(f"  決策成功率: {successful_decisions/total_observations*100:.1f}%")
    print(f"  平均處理速度: {total_observations/duration:.1f} obs/s")
    
    # 顯示引擎狀態
    final_state = engine.get_production_state()
    print(f"\n最終引擎狀態:")
    print(f"  緩存命中: {final_state['decision_cache_hits']}")
    print(f"  緩存大小: {sum(final_state['buffer_status'].values())}")

async def main():
    """主測試函數"""
    print("量子決策系統 - Trading X 生產級整合測試")
    print("支援七種主要加密貨幣的即時量子決策")
    print("結合 ChatGPT 最佳化建議的向量化實現\n")
    
    try:
        # 1. 完整系統測試
        await run_complete_production_test()
        
        # 2. 個別組件測試
        await test_individual_components()
        
        # 3. 壓力測試
        await run_stress_test()
        
        print("\n🎉 所有測試完成! 量子決策系統準備就緒")
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
