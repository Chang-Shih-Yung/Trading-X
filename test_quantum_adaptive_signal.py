#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Quantum Adaptive Trading Launcher 信號生成
==============================================
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加路徑
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "quantum_pro"))

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_quantum_adaptive_signal():
    """測試 Quantum Adaptive Trading Launcher 信號生成"""
    
    try:
        logger.info("🔄 開始測試 Quantum Adaptive Trading Launcher...")
        
        # 導入系統
        from quantum_pro.launcher.quantum_adaptive_trading_launcher import (
            QuantumAdaptiveTradingLauncher,
        )

        # 創建啟動器實例
        logger.info("🔧 創建 Quantum Adaptive Trading Launcher 實例...")
        launcher = QuantumAdaptiveTradingLauncher()
        
        # 初始化量子系統
        logger.info("🔧 初始化量子系統...")
        init_success = await launcher.initialize_quantum_systems()
        
        if not init_success:
            logger.error("❌ 量子系統初始化失敗")
            return False
        
        # 獲取信號處理器
        logger.info("🔮 初始化信號處理器...")
        signal_processor = await launcher._initialize_real_quantum_signal_processor()
        
        # 準備測試市場數據
        test_market_data = {
            'current_price': 108000.0,
            'price_change_percent': 2.5,
            'volatility': 0.025,
            'momentum': 0.15,
            'rsi': 65.0,
            'bb_position': 0.75,
            'volume': 1000000.0,
            'volume_change_percent': 5.0
        }
        
        # 測試信號生成
        logger.info("🔮 測試信號生成...")
        signal = await signal_processor.generate_signal('BTCUSDT', test_market_data)
        
        if signal:
            logger.info("✅ 信號生成成功！")
            logger.info(f"📊 信號詳細信息:")
            logger.info(f"   - 交易對: {signal.get('symbol', 'N/A')}")
            logger.info(f"   - 信號類型: {signal.get('signal', 'N/A')}")
            logger.info(f"   - 信心度: {signal.get('confidence', 0):.4f}")
            logger.info(f"   - 信號強度: {signal.get('signal_strength', 0):.4f}")
            logger.info(f"   - 量子狀態: {signal.get('quantum_state', 'N/A')}")
            logger.info(f"   - 量子後端: {signal.get('quantum_backend', 'N/A')}")
            logger.info(f"   - 模型狀態: {signal.get('model_status', 'N/A')}")
            
            # 檢查概率分布
            probabilities = signal.get('probabilities', {})
            if probabilities:
                logger.info(f"   - 概率分布:")
                logger.info(f"     * Bear: {probabilities.get('bear', 0):.4f}")
                logger.info(f"     * Side: {probabilities.get('side', 0):.4f}")
                logger.info(f"     * Bull: {probabilities.get('bull', 0):.4f}")
            
            # 檢查量子指標
            quantum_metrics = signal.get('quantum_metrics', {})
            if quantum_metrics:
                logger.info(f"   - 量子指標:")
                logger.info(f"     * 量子信心度: {quantum_metrics.get('quantum_confidence', 0):.4f}")
                logger.info(f"     * 量子保真度: {quantum_metrics.get('quantum_fidelity', 0):.4f}")
                logger.info(f"     * 風險報酬比: {quantum_metrics.get('risk_reward_ratio', 0):.4f}")
                
            # 檢查信號格式
            required_fields = [
                'symbol', 'signal', 'confidence', 'signal_strength',
                'quantum_state', 'probabilities', 'quantum_backend', 'model_status'
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in signal:
                    missing_fields.append(field)
            
            if missing_fields:
                logger.warning(f"⚠️ 信號缺少以下字段: {missing_fields}")
            else:
                logger.info("✅ 信號格式完整，符合 Quantum Adaptive 標準")
                
            return True
        else:
            logger.error("❌ 信號生成失敗：返回 None")
            return False
            
    except ImportError as e:
        logger.error(f"❌ 導入錯誤: {e}")
        logger.error("💡 請確認 quantum_pro.launcher 模組路徑正確")
        return False
    except Exception as e:
        logger.error(f"❌ 測試失敗: {e}")
        logger.error(f"❌ 錯誤類型: {type(e).__name__}")
        import traceback
        logger.error(f"❌ 詳細錯誤: {traceback.format_exc()}")
        return False

async def main():
    """主測試函數"""
    logger.info("🚀 開始 Quantum Adaptive Trading Launcher 信號測試")
    logger.info("=" * 60)
    
    success = await test_quantum_adaptive_signal()
    
    logger.info("=" * 60)
    if success:
        logger.info("🎉 Quantum Adaptive Trading Launcher 信號測試成功！")
    else:
        logger.error("💥 Quantum Adaptive Trading Launcher 信號測試失敗！")
        
    return success

if __name__ == "__main__":
    asyncio.run(main())
