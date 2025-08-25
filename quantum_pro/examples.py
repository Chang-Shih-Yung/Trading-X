"""
Trading X Quantum Pro 使用示例

演示如何使用量子決策系統的各種功能
"""

import asyncio
import sys
from pathlib import Path

# 添加項目路徑
sys.path.append(str(Path(__file__).parent.parent))

from quantum_pro import (
    MarketObservation,
    ProductionQuantumProcessor,
    QuantumDecisionEngine,
    TradingHypothesis,
    get_config_manager,
    get_system_info,
)


async def basic_example():
    """基本使用示例"""
    print("=== Trading X Quantum Pro 基本示例 ===")
    
    # 1. 獲取系統資訊
    info = get_system_info()
    print(f"系統: {info['name']} v{info['version']}")
    print(f"支援交易對: {info['supported_symbols']}")
    
    # 2. 載入配置
    try:
        config_manager = get_config_manager()
        config = config_manager.get_quantum_decision_config()
        print(f"配置載入成功 - SPRT: α={config.alpha}, β={config.beta}")
    except Exception as e:
        print(f"配置載入失敗: {e}")
        return
    
    # 3. 初始化量子決策引擎
    engine = QuantumDecisionEngine(config)
    print("量子決策引擎初始化完成")
    
    # 4. 獲取當前狀態
    state = engine.get_current_state()
    print(f"信念狀態: {state['belief_state']}")
    print(f"SPRT 閾值: 上={state['sprt_thresholds']['upper']:.3f}, 下={state['sprt_thresholds']['lower']:.3f}")

async def production_example():
    """生產環境示例"""
    print("\n=== 生產環境啟動示例 ===")
    
    try:
        # 載入配置
        config_manager = get_config_manager()
        config = config_manager.get_quantum_decision_config()
        
        # 初始化生產處理器
        processor = ProductionQuantumProcessor(config)
        print("生產處理器初始化成功")
        
        # 獲取活躍交易對
        symbols = config_manager.get_active_symbols()
        print(f"監控 {len(symbols)} 個交易對:")
        for symbol in symbols:
            print(f"  - {symbol.symbol}: 權重={symbol.weight}, 最大倉位={symbol.max_position}")
        
        # 獲取制度定義
        regimes = config_manager.get_regime_definitions()
        print(f"\n市場制度定義 ({len(regimes)} 個):")
        for regime_id, regime in regimes.items():
            print(f"  - 制度 {regime_id}: {regime.name} - {regime.description}")
        
        print("\n注意: 要完整啟動生產系統，請使用 start_quantum_pro.py")
        
    except Exception as e:
        print(f"生產環境示例失敗: {e}")

def configuration_example():
    """配置管理示例"""
    print("\n=== 配置管理示例 ===")
    
    try:
        config_manager = get_config_manager()
        
        # 驗證配置
        if config_manager.validate_config():
            print("✓ 配置文件驗證通過")
        else:
            print("✗ 配置文件驗證失敗")
            return
        
        # 獲取技術指標配置
        tech_config = config_manager.get_technical_indicator_config()
        print(f"技術指標配置: {tech_config}")
        
        # 獲取執行配置
        exec_config = config_manager.get_execution_config()
        print(f"執行配置: {exec_config}")
        
        # 獲取監控配置
        monitor_config = config_manager.get_monitoring_config()
        print(f"監控配置: {monitor_config}")
        
    except Exception as e:
        print(f"配置管理示例失敗: {e}")

async def main():
    """主函數"""
    print("Trading X Quantum Pro 系統演示")
    print("=" * 50)
    
    # 基本功能演示
    await basic_example()
    
    # 生產環境演示
    await production_example()
    
    # 配置管理演示
    configuration_example()
    
    print("\n" + "=" * 50)
    print("演示完成!")
    print("\n啟動完整系統:")
    print("python start_quantum_pro.py")
    print("\n或者:")
    print("python -m quantum_pro.quantum_launcher")

if __name__ == "__main__":
    asyncio.run(main())
