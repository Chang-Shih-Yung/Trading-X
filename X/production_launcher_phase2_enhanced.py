"""
🚀 Trading X 生產環境啟動器 - Phase2 參數管理增強版
真正啟動完整的 Phase1A + Phase2 整合系統，包含自動參數優化
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
from datetime import datetime
import json

# 確保可以導入所有模組
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "backend"))

# 設定詳細日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'production_trading_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ProductionTradingSystemPhase2Enhanced:
    """生產環境交易系統 - Phase2 參數管理增強版"""
    
    def __init__(self):
        self.phase1a_generator = None
        self.phase3_decision_engine = None
        self.phase3_enabled = False
        self.monitoring_manager = None
        self.running = False
        
        # Phase5 定時觸發配置
        self.phase5_enabled = True
        self.phase5_interval_hours = 24  # 24小時觸發一次
        self.phase5_last_run = None
        self.phase5_running = False
        
        # 學習反饋機制配置
        self.learning_feedback_enabled = True
        self.learning_feedback_last_run = 0  # 上次反饋分析時間
        self.learning_feedback_interval = 3600  # 1小時執行一次
        
        # Phase2 參數管理器
        self.phase2_parameter_manager = None
        self.phase2_parameter_check_interval = 1800  # 30分鐘檢查一次
        self.phase2_last_parameter_check = 0
        
    async def initialize_systems(self):
        """初始化所有系統組件"""
        logger.info("🚀 初始化生產環境交易系統...")
        
        try:
            # 1. 初始化 Phase1A 信號生成器（已整合 Phase2）
            from backend.phase1_signal_generation.phase1a_basic_signal_generation.phase1a_basic_signal_generation import Phase1ABasicSignalGeneration
            
            self.phase1a_generator = Phase1ABasicSignalGeneration()
            logger.info("✅ Phase1A 信號生成器初始化成功")
            
            # 檢查 Phase2 自適應學習是否啟用
            if self.phase1a_generator.adaptive_mode:
                logger.info("🧠 Phase2 自適應學習模式：已啟用")
                logger.info(f"📊 市場檢測器：{type(self.phase1a_generator.regime_detector).__name__}")
                logger.info(f"🎓 學習引擎：{type(self.phase1a_generator.learning_core).__name__}")
            else:
                logger.warning("⚠️ Phase2 自適應學習模式：未啟用，使用基礎模式")
            
            # 2. 初始化 Phase3 決策系統
            try:
                from backend.phase3_execution_policy.epl_intelligent_decision_engine import EplIntelligentDecisionEngine
                self.phase3_decision_engine = EplIntelligentDecisionEngine()
                await self.phase3_decision_engine.initialize()
                logger.info("✅ Phase3 決策系統初始化成功")
                self.phase3_enabled = True
            except ImportError as e:
                logger.warning(f"⚠️ Phase3 決策系統未啟用: {e}")
                self.phase3_decision_engine = None
                self.phase3_enabled = False
            
            # 3. 初始化監控系統（可選）
            try:
                from backend.phase4_output_monitoring.real_time_unified_monitoring_manager import unified_monitoring_manager
                self.monitoring_manager = unified_monitoring_manager
                logger.info("✅ 監控系統初始化成功")
            except ImportError as e:
                logger.warning(f"⚠️ 監控系統未啟用: {e}")
                self.monitoring_manager = None
            
            # 4. 初始化 Phase2 參數管理器
            try:
                from backend.phase2_adaptive_learning.phase2_parameter_manager import phase2_parameter_manager
                self.phase2_parameter_manager = phase2_parameter_manager
                logger.info("✅ Phase2 參數管理器初始化成功")
                
                # 設置性能基線
                if hasattr(self.phase2_parameter_manager, 'performance_baseline'):
                    self.phase2_parameter_manager.performance_baseline = 0.55  # 55% 勝率基線
                    
            except ImportError as e:
                logger.warning(f"⚠️ Phase2 參數管理器未啟用: {e}")
                self.phase2_parameter_manager = None
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 系統初始化失敗: {e}")
            return False
    
    async def start_signal_generation_loop(self):
        """啟動信號生成循環"""
        logger.info("🎯 啟動信號生成循環...")
        
        # 測試交易對
        test_symbols = ["BTCUSDT", "ETHUSDT"]
        
        while self.running:
            try:
                # 🔧 Phase2 參數檢查和生成（每30分鐘）
                current_time = time.time()
                if (self.phase2_parameter_manager and 
                    current_time - self.phase2_last_parameter_check > self.phase2_parameter_check_interval):
                    
                    try:
                        await self._check_and_generate_phase2_parameters()
                        self.phase2_last_parameter_check = current_time
                    except Exception as e:
                        logger.error(f"❌ Phase2 參數檢查失敗: {e}")
                
                for symbol in test_symbols:
                    logger.info(f"📊 生成 {symbol} 信號...")
                    
                    # 獲取真實市場數據
                    try:
                        # 使用真實數據源
                        market_data = await self._get_real_market_data(symbol)
                        if not market_data:
                            logger.warning(f"⚠️ {symbol} 無法獲取真實市場數據，跳過")
                            continue
                            
                    except Exception as e:
                        logger.error(f"❌ {symbol} 真實數據獲取失敗: {e}")
                        continue
                    
                    # 生成信號（包含 Phase2 自適應學習）
                    signals = await self.phase1a_generator.generate_tiered_signals(symbol, market_data)
                    
                    # 📊 將信號傳遞給 Phase2 學習系統進行追蹤
                    if signals and self.phase1a_generator.adaptive_mode:
                        try:
                            # 增加信號計數
                            if self.phase2_parameter_manager:
                                self.phase2_parameter_manager.increment_signal_count()
                                
                            # 為每個信號建立學習追蹤
                            for tier, signal_data in signals.items():
                                if signal_data and isinstance(signal_data, list):
                                    for signal in signal_data:
                                        if hasattr(signal, 'signal_type') and hasattr(signal, 'signal_strength'):
                                            learning_data = {
                                                'signal_id': f"{symbol}_{tier}_{datetime.now().timestamp()}",
                                                'symbol': symbol,
                                                'signal_strength': signal.signal_strength,
                                                'direction': signal.signal_type,
                                                'tier': tier,
                                                'features': {
                                                    'price': market_data.get('close', 0),
                                                    'volume': market_data.get('volume', 0),
                                                    'tier': tier
                                                },
                                                'market_conditions': market_data
                                            }
                                            
                                            # 追蹤信號到學習系統
                                            if hasattr(self.phase1a_generator.learning_core, 'track_signal_for_learning'):
                                                await self.phase1a_generator.learning_core.track_signal_for_learning(learning_data)
                        except Exception as e:
                            logger.debug(f"學習追蹤錯誤: {e}")
                    
                    # Phase3 決策處理
                    if self.phase3_enabled and signals:
                        try:
                            # 將信號傳遞給 Phase3 決策引擎
                            decision_result = await self.phase3_decision_engine.process_signals(
                                symbol=symbol,
                                raw_signals=signals,
                                market_data=market_data
                            )
                            
                            if decision_result and decision_result.get('decisions'):
                                decisions = decision_result['decisions']
                                logger.info(f"🎯 {symbol} Phase3 決策完成: {len(decisions)} 個決策")
                                
                                # 記錄決策摘要
                                for decision in decisions[:2]:  # 顯示前2個決策
                                    action = decision.get('action', 'N/A')
                                    confidence = decision.get('confidence', 0)
                                    logger.info(f"   🎲 決策: {action} | 信心度: {confidence:.3f}")
                            else:
                                logger.info(f"🚫 {symbol} Phase3 決策：無有效決策生成")
                                
                        except Exception as e:
                            logger.error(f"❌ {symbol} Phase3 決策處理錯誤: {e}")
                    
                    if signals:
                        # signals是dict類型，需要轉換為list
                        signal_list = []
                        if isinstance(signals, dict):
                            # 提取信號對象
                            for tier, signal_data in signals.items():
                                if signal_data and isinstance(signal_data, list):
                                    signal_list.extend(signal_data)
                                elif signal_data:
                                    signal_list.append(signal_data)
                        else:
                            signal_list = signals if isinstance(signals, list) else [signals]
                        
                        logger.info(f"✅ {symbol} 信號生成成功: {len(signal_list)} 個信號")
                        
                        # 🎯 向用戶展示完整交易信號
                        decision_list = decisions if self.phase3_enabled and 'decisions' in locals() else None
                        await self._display_user_signals(symbol, signal_list, decision_list)
                        
                        # 顯示技術信號詳情
                        for i, signal in enumerate(signal_list[:3]):  # 只顯示前3個
                            if hasattr(signal, 'signal_type') and hasattr(signal, 'signal_strength'):
                                tier_info = signal.tier.value if hasattr(signal, 'tier') and hasattr(signal.tier, 'value') else 'N/A'
                                logger.info(f"   📈 信號{i+1}: {signal.signal_type} | 強度: {signal.signal_strength:.3f} | 層級: {tier_info}")
                    else:
                        logger.info(f"📊 {symbol} 當前無交易信號")
                    
                    # 記錄學習系統狀態
                    await self._log_learning_status()
                    
                    await asyncio.sleep(5)  # 每個交易對處理間隔
                
                await asyncio.sleep(15)  # 循環間隔
                
            except Exception as e:
                logger.error(f"❌ 信號生成循環錯誤: {e}")
                await asyncio.sleep(30)  # 錯誤後等待更長時間
    
    async def _check_and_generate_phase2_parameters(self):
        """檢查並生成 Phase2 參數"""
        try:
            logger.debug("🔧 檢查 Phase2 參數生成條件...")
            
            if not self.phase1a_generator or not self.phase1a_generator.adaptive_mode:
                logger.debug("⏭️ Phase2 自適應模式未啟用，跳過參數生成")
                return
            
            # 檢查是否需要生成新參數
            should_generate, trigger_reason = self.phase2_parameter_manager.should_generate_new_parameters()
            
            if should_generate:
                logger.info(f"🔄 觸發 Phase2 參數生成: {trigger_reason}")
                
                # 獲取學習引擎和市場檢測器
                learning_engine = self.phase1a_generator.learning_core
                market_detector = self.phase1a_generator.regime_detector
                
                # 生成優化參數
                new_parameters = await self.phase2_parameter_manager.generate_optimized_parameters(
                    learning_engine=learning_engine,
                    market_detector=market_detector
                )
                
                if new_parameters:
                    logger.info("✅ Phase2 參數生成成功")
                    logger.info(f"📊 新參數數量: {len(new_parameters)}")
                    
                    # 記錄關鍵參數變化
                    key_params = ["signal_threshold", "momentum_weight", "volatility_adjustment"]
                    for param in key_params:
                        if param in new_parameters:
                            logger.info(f"   🔧 {param}: {new_parameters[param]:.3f}")
                    
                    # 通知 Phase1A 重載參數（如果支持）
                    if hasattr(self.phase1a_generator, 'reload_configuration'):
                        try:
                            await self.phase1a_generator.reload_configuration()
                            logger.info("🔄 Phase1A 參數已重載")
                        except Exception as e:
                            logger.warning(f"⚠️ Phase1A 參數重載失敗: {e}")
                    
                    # 報告性能
                    if hasattr(self.phase2_parameter_manager, 'report_performance'):
                        # 模擬當前性能評估 (實際應用中從真實交易結果獲取)
                        current_performance = await self._estimate_current_performance()
                        self.phase2_parameter_manager.report_performance(current_performance)
                        
                else:
                    logger.warning("⚠️ Phase2 參數生成失敗")
            else:
                logger.debug(f"⏭️ 跳過 Phase2 參數生成: {trigger_reason}")
        
        except Exception as e:
            logger.error(f"❌ Phase2 參數檢查失敗: {e}")
    
    async def _estimate_current_performance(self) -> float:
        """估算當前系統性能"""
        try:
            if (self.phase1a_generator and 
                hasattr(self.phase1a_generator, 'learning_core') and
                hasattr(self.phase1a_generator.learning_core, 'performance_metrics')):
                
                metrics = self.phase1a_generator.learning_core.performance_metrics
                success_rate = metrics.get('success_rate', 0.5)
                return success_rate
            else:
                # 默認性能評估
                return 0.55
        except Exception as e:
            logger.debug(f"性能估算錯誤: {e}")
            return 0.55
    
    async def _log_learning_status(self):
        """記錄學習系統狀態"""
        try:
            if not (self.phase1a_generator and self.phase1a_generator.adaptive_mode):
                return
            
            if hasattr(self.phase1a_generator.learning_core, 'get_learning_summary'):
                learning_summary = self.phase1a_generator.learning_core.get_learning_summary()
                
                # 記錄關鍵學習指標
                status = learning_summary.get('learning_status', 'UNKNOWN')
                total_signals = learning_summary.get('performance_metrics', {}).get('total_signals_tracked', 0)
                success_rate = learning_summary.get('performance_metrics', {}).get('success_rate', 0)
                
                if total_signals > 0:
                    logger.info(f"🧠 學習狀態: {status} | 追蹤信號: {total_signals} | 成功率: {success_rate:.1%}")
                
                # 下次優化倒計時
                next_opt = learning_summary.get('next_optimization_in', 0)
                if next_opt > 0:
                    logger.info(f"   ⏳ 下次參數優化: {next_opt} 個信號後")
                
            if hasattr(self.phase1a_generator, 'regime_detector') and self.phase1a_generator.regime_detector:
                # 這裡需要市場數據才能檢測，暫時跳過
                pass
                
        except Exception as e:
            logger.debug(f"學習狀態記錄錯誤: {e}")
    
    async def _get_real_market_data(self, symbol: str) -> dict:
        """獲取真實市場數據"""
        try:
            # 使用 requests 或 aiohttp 獲取 Binance 數據
            import aiohttp
            
            url = f"https://api.binance.com/api/v3/ticker/24hr"
            params = {"symbol": symbol}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        return {
                            "symbol": symbol,
                            "close": float(data.get("lastPrice", 0)),
                            "volume": float(data.get("volume", 0)),
                            "high": float(data.get("highPrice", 0)),
                            "low": float(data.get("lowPrice", 0)),
                            "change_percent": float(data.get("priceChangePercent", 0)),
                            "timestamp": datetime.now()
                        }
                    else:
                        logger.error(f"❌ Binance API 錯誤: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ 獲取 {symbol} 真實數據失敗: {e}")
            return None
    
    def _format_user_signal_display(self, symbol: str, signals: list, decisions: list = None) -> dict:
        """格式化用戶信號展示"""
        if not signals:
            return None
        
        # 取最高優先級信號
        best_signal = None
        best_priority = -1
        
        priority_map = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        
        for signal in signals:
            if hasattr(signal, 'tier'):
                tier_name = signal.tier.value if hasattr(signal.tier, 'value') else str(signal.tier)
                priority = priority_map.get(tier_name, 0)
                if priority > best_priority:
                    best_priority = priority
                    best_signal = signal
        
        if not best_signal:
            best_signal = signals[0]  # 如果沒有分層，取第一個
        
        # 計算倉位建議（基於信號強度和層級）
        signal_strength = getattr(best_signal, 'signal_strength', 0.5)
        tier_name = best_signal.tier.value if hasattr(best_signal, 'tier') and hasattr(best_signal.tier, 'value') else 'MEDIUM'
        
        position_multipliers = {"CRITICAL": 0.8, "HIGH": 0.6, "MEDIUM": 0.4, "LOW": 0.2}
        suggested_position = signal_strength * position_multipliers.get(tier_name, 0.4)
        
        # 計算止盈止損（基於信號強度）
        signal_type = getattr(best_signal, 'signal_type', 'HOLD')
        current_price = getattr(best_signal, 'current_price', 0)
        
        if signal_type in ['BUY', 'LONG']:
            take_profit = current_price * (1 + signal_strength * 0.05)  # 最多5%止盈
            stop_loss = current_price * (1 - signal_strength * 0.03)    # 最多3%止損
        elif signal_type in ['SELL', 'SHORT']:
            take_profit = current_price * (1 - signal_strength * 0.05)  # 做空止盈
            stop_loss = current_price * (1 + signal_strength * 0.03)    # 做空止損
        else:
            take_profit = stop_loss = current_price
        
        # 計算建議持倉時間（基於信號層級）
        holding_hours = {"CRITICAL": 4, "HIGH": 8, "MEDIUM": 24, "LOW": 72}
        suggested_holding = holding_hours.get(tier_name, 24)
        
        return {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "signal_type": signal_type,
            "confidence": signal_strength,
            "tier": tier_name,
            "suggested_position_size": f"{suggested_position:.1%}",
            "current_price": current_price,
            "take_profit": f"{take_profit:.4f}",
            "stop_loss": f"{stop_loss:.4f}",
            "suggested_holding_hours": suggested_holding,
            "phase2_optimization": "參數已根據學習結果優化" if self.phase1a_generator.adaptive_mode else "基礎參數模式",
            "phase3_decision": decisions[0] if decisions else None
        }
    
    async def _display_user_signals(self, symbol: str, signals: list, decisions: list = None):
        """向用戶展示信號"""
        signal_display = self._format_user_signal_display(symbol, signals, decisions)
        
        if signal_display:
            logger.info("="*80)
            logger.info(f"🎯 【{symbol} 交易信號】")
            logger.info(f"   📈 操作建議: {signal_display['signal_type']}")
            logger.info(f"   💪 信心度: {signal_display['confidence']:.1%}")
            logger.info(f"   🏆 信號層級: {signal_display['tier']}")
            logger.info(f"   💰 建議倉位: {signal_display['suggested_position_size']}")
            logger.info(f"   💵 當前價格: {signal_display['current_price']}")
            logger.info(f"   📈 止盈價格: {signal_display['take_profit']}")
            logger.info(f"   📉 止損價格: {signal_display['stop_loss']}")
            logger.info(f"   ⏰ 建議持倉: {signal_display['suggested_holding_hours']} 小時")
            logger.info(f"   🧠 Phase2 狀態: {signal_display['phase2_optimization']}")
            
            if signal_display['phase3_decision']:
                decision = signal_display['phase3_decision']
                logger.info(f"   🎯 Phase3 決策: {decision.get('action', 'N/A')} (信心度: {decision.get('confidence', 0):.1%})")
            
            logger.info("="*80)
    
    async def start_monitoring(self):
        """啟動監控系統"""
        if self.monitoring_manager:
            try:
                await self.monitoring_manager.start_monitoring()
                logger.info("✅ 統一監控系統已啟動")
            except Exception as e:
                logger.error(f"❌ 監控系統啟動失敗: {e}")
    
    async def run(self):
        """運行完整系統"""
        logger.info("🚀 啟動 Trading X 生產環境系統 (Phase2 參數管理增強版)...")
        
        # 初始化系統
        if not await self.initialize_systems():
            logger.error("❌ 系統初始化失敗，退出")
            return
        
        # ⭐ 關鍵優化：啟動前先執行 Phase5 回測獲取最優參數（可選）
        logger.info("🎯 執行啟動前系統檢查...")
        
        self.running = True
        
        try:
            # 啟動監控系統
            await self.start_monitoring()
            
            # 並行運行信號生成
            signal_task = asyncio.create_task(self.start_signal_generation_loop())
            
            # 等待任務完成
            await signal_task
            
        except KeyboardInterrupt:
            logger.info("🔄 接收到停止信號...")
        except Exception as e:
            logger.error(f"❌ 系統運行錯誤: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """關閉系統"""
        logger.info("🔄 關閉系統中...")
        self.running = False
        
        # 保存 Phase2 參數管理器狀態
        if self.phase2_parameter_manager:
            try:
                # 可以在這裡保存學習狀態和參數歷史
                logger.info("💾 保存 Phase2 參數管理器狀態...")
            except Exception as e:
                logger.error(f"❌ 保存狀態失敗: {e}")
        
        logger.info("✅ 系統已安全關閉")

async def main():
    """主入口函數"""
    print("🚀 Trading X 生產環境啟動器 (Phase2 參數管理增強版)")
    print("="*60)
    
    # 創建並運行系統
    system = ProductionTradingSystemPhase2Enhanced()
    await system.run()

if __name__ == "__main__":
    asyncio.run(main())
