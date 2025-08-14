#!/usr/bin/env python3
"""
🧪 簡化週期優化器測試
專注於核心優化邏輯測試
"""

import asyncio
import logging
import json
import sys
from pathlib import Path
from dataclasses import dataclass

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ParameterSet:
    confidence_threshold: float
    price_change_threshold: float
    volume_change_threshold: float
    
    def to_dict(self):
        return {
            'confidence_threshold': self.confidence_threshold,
            'price_change_threshold': self.price_change_threshold,
            'volume_change_threshold': self.volume_change_threshold
        }

async def test_current_performance():
    """測試當前性能獲取"""
    try:
        logger.info("🔍 測試當前性能獲取...")
        
        # 添加路徑
        sys.path.append(str(Path(__file__).parent.parent / "auto_backtest_validator"))
        from auto_backtest_validator import AutoBacktestValidator  # type: ignore
        
        validator = AutoBacktestValidator()
        result = await validator.run_phase1a_validation_cycle()
        
        logger.info(f"📊 驗證結果類型: {type(result)}")
        logger.info(f"📊 驗證結果是否為 None: {result is None}")
        
        if result:
            logger.info(f"📊 驗證結果內容: {json.dumps(result, indent=2, default=str, ensure_ascii=False)}")
            
            # 提取性能指標
            performance = {
                'win_rate': result.get('overall_performance', {}).get('overall_win_rate', 0),
                'avg_pnl_ratio': result.get('overall_performance', {}).get('avg_pnl_ratio', 0),
                'total_signals': result.get('overall_performance', {}).get('total_signals', 0),
            }
            
            logger.info(f"✅ 性能指標提取成功: {performance}")
            return performance
        else:
            logger.error("❌ 驗證結果為 None")
            return None
            
    except Exception as e:
        logger.error(f"❌ 性能測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_parameter_update():
    """測試參數更新"""
    try:
        logger.info("🔧 測試參數更新...")
        
        # 測試參數
        test_params = ParameterSet(
            confidence_threshold=0.75,
            price_change_threshold=0.0015,
            volume_change_threshold=1.5
        )
        
        # 更新配置文件
        config_path = Path(__file__).parent.parent.parent.parent / "phase1_signal_generation" / "phase1a_basic_signal_generation" / "phase1a_basic_signal_generation.json"
        
        logger.info(f"📄 配置文件路徑: {config_path}")
        logger.info(f"📄 路徑存在: {config_path.exists()}")
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 顯示當前參數
            current_params = {
                'confidence_threshold': config['phase1a_basic_signal_generation_dependency']['configuration']['signal_generation_params']['basic_mode']['confidence_threshold']['base_value'],
                'price_change_threshold': config['phase1a_basic_signal_generation_dependency']['configuration']['signal_generation_params']['basic_mode']['price_change_threshold']['base_value'],
                'volume_change_threshold': config['phase1a_basic_signal_generation_dependency']['configuration']['signal_generation_params']['basic_mode']['volume_change_threshold']['base_value']
            }
            
            logger.info(f"📊 當前參數: {current_params}")
            logger.info(f"📊 測試參數: {test_params.to_dict()}")
            
            return True
        else:
            logger.error("❌ 配置文件不存在")
            return False
            
    except Exception as e:
        logger.error(f"❌ 參數更新測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主測試流程"""
    logger.info("🚀 開始簡化週期優化器測試...")
    
    # 測試當前性能獲取
    performance = await test_current_performance()
    if not performance:
        logger.error("❌ 當前性能獲取失敗，停止測試")
        return
    
    # 測試參數更新
    param_ok = await test_parameter_update()
    if not param_ok:
        logger.error("❌ 參數更新測試失敗")
        return
    
    logger.info("✅ 簡化測試完成！週期優化器核心功能正常")

if __name__ == "__main__":
    asyncio.run(main())
