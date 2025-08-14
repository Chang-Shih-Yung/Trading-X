#!/usr/bin/env python3
"""
🔧 週期參數優化器調試測試
用於隔離和解決配置問題
"""

import asyncio
import logging
import sys
from pathlib import Path

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_phase1a_integration():
    """測試 Phase1A 整合"""
    try:
        logger.info("🔍 測試 Phase1A 信號生成器整合...")
        
        # 添加路徑
        phase1a_path = Path(__file__).parent.parent.parent / "phase1_signal_generation" / "phase1a_basic_signal_generation"
        sys.path.append(str(phase1a_path))
        
        logger.info(f"📁 Phase1A 路徑: {phase1a_path}")
        logger.info(f"📁 路徑存在: {phase1a_path.exists()}")
        
        # 導入 Phase1A
        from phase1a_basic_signal_generation import Phase1ABasicSignalGeneration
        logger.info("✅ Phase1A 模組導入成功")
        
        # 初始化生成器
        generator = Phase1ABasicSignalGeneration()
        logger.info("✅ Phase1A 生成器初始化成功")
        
        return generator
        
    except Exception as e:
        logger.error(f"❌ Phase1A 整合測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_auto_backtest_validator():
    """測試自動回測驗證器"""
    try:
        logger.info("🔍 測試自動回測驗證器...")
        
        # 添加路徑
        validator_path = Path(__file__).parent.parent / "auto_backtest_validator"
        sys.path.append(str(validator_path))
        
        logger.info(f"📁 驗證器路徑: {validator_path}")
        logger.info(f"📁 路徑存在: {validator_path.exists()}")
        
        # 導入驗證器
        from auto_backtest_validator import AutoBacktestValidator
        logger.info("✅ 驗證器模組導入成功")
        
        # 初始化驗證器
        validator = AutoBacktestValidator()
        logger.info("✅ 驗證器初始化成功")
        
        return validator
        
    except Exception as e:
        logger.error(f"❌ 驗證器測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_configuration_files():
    """測試配置文件"""
    try:
        logger.info("🔍 檢查配置文件...")
        
        # Phase1A 配置
        phase1a_config = Path(__file__).parent.parent.parent / "phase1_signal_generation" / "phase1a_basic_signal_generation" / "phase1a_basic_signal_generation.json"
        logger.info(f"📄 Phase1A 配置: {phase1a_config}")
        logger.info(f"📄 存在: {phase1a_config.exists()}")
        
        if phase1a_config.exists():
            import json
            with open(phase1a_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"📄 Phase1A 配置載入成功，大小: {len(str(config))} 字符")
        
        # 回測驗證器配置
        validator_config = Path(__file__).parent.parent / "auto_backtest_validator" / "auto_backtest_config.json"
        logger.info(f"📄 驗證器配置: {validator_config}")
        logger.info(f"📄 存在: {validator_config.exists()}")
        
        if validator_config.exists():
            with open(validator_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"📄 驗證器配置載入成功，版本: {config.get('version', 'unknown')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 配置文件檢查失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主測試流程"""
    logger.info("🚀 開始調試測試...")
    
    # 測試配置文件
    config_ok = await test_configuration_files()
    if not config_ok:
        logger.error("❌ 配置文件測試失敗，停止測試")
        return
    
    # 測試 Phase1A
    phase1a = await test_phase1a_integration()
    if not phase1a:
        logger.error("❌ Phase1A 整合失敗，停止測試")
        return
    
    # 測試驗證器
    validator = await test_auto_backtest_validator()
    if not validator:
        logger.error("❌ 驗證器整合失敗，停止測試")
        return
    
    logger.info("✅ 所有組件測試通過！")
    
    # 嘗試執行簡單的驗證循環
    try:
        logger.info("🔄 嘗試執行驗證循環...")
        result = await validator.run_phase1a_validation_cycle()
        logger.info(f"✅ 驗證循環完成: {result.get('status', 'unknown')}")
    except Exception as e:
        logger.error(f"❌ 驗證循環失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
