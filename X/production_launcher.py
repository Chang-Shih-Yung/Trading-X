"""
🚀 Trading X 生產環境啟動器
真正啟動完整的 Phase1A + Phase2 整合系統
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
    
    async def run(self):logging.getLogger(__name__)

class ProductionTradingSystem:
    """生產環境交易系統"""
    
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
                                tier_info = signal.tier.value if hasattr(signal, 'tier') else 'N/A'
                                logger.info(f"   📈 技術信號 {i+1}: {signal.signal_type} | 強度: {signal.signal_strength:.3f} | 層級: {tier_info}")
                            else:
                                logger.info(f"   📊 信號 {i+1}: {type(signal).__name__}")
                        
                        # 如果是自適應模式，顯示學習狀態
                        if self.phase1a_generator.adaptive_mode:
                            await self._log_learning_status(symbol)
                    
                    else:
                        logger.warning(f"⚠️ {symbol} 未生成信號")
                
                # 每30秒生成一次信號
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ 信號生成錯誤: {e}")
                await asyncio.sleep(10)
    
    async def _log_learning_status(self, symbol: str):
        """記錄學習狀態"""
        try:
            if hasattr(self.phase1a_generator, 'learning_core') and self.phase1a_generator.learning_core:
                learning_summary = await self.phase1a_generator.learning_core.get_learning_summary()
                
                # 詳細學習狀態記錄
                logger.info(f"🧠 {symbol} 學習狀態摘要:")
                logger.info(f"   📊 狀態: {learning_summary.get('learning_status', 'N/A')}")
                logger.info(f"   🎯 追蹤信號數: {learning_summary.get('update_frequency', 0)}")
                logger.info(f"   📈 勝率: {learning_summary.get('performance_metrics', {}).get('success_rate', 0):.2%}")
                logger.info(f"   💰 平均收益: {learning_summary.get('performance_metrics', {}).get('average_return', 0):.4f}")
                logger.info(f"   🔧 參數優化次數: {learning_summary.get('learning_statistics', {}).get('parameters_optimized', 0)}")
                
                # 顯示當前優化參數
                current_params = learning_summary.get('current_parameters', {})
                logger.info(f"   ⚙️ 當前參數: 閾值={current_params.get('signal_threshold', 0):.3f}, 風險={current_params.get('risk_multiplier', 0):.3f}")
                
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
            "recommendation": f"{'做多' if signal_type in ['BUY', 'LONG'] else '做空' if signal_type in ['SELL', 'SHORT'] else '觀望'} {symbol}",
            "risk_level": tier_name,
            "confidence_display": f"{signal_strength:.1%}"
        }
    
    async def _display_user_signals(self, symbol: str, signals: list, decisions: list = None):
        """向用戶展示完整信號信息"""
        display_data = self._format_user_signal_display(symbol, signals, decisions)
        
        if display_data:
            logger.info("=" * 60)
            logger.info(f"🎯 {display_data['symbol']} 交易信號")
            logger.info(f"📊 推薦操作: {display_data['recommendation']}")
            logger.info(f"📈 信號類型: {display_data['signal_type']}")
            logger.info(f"🎲 信心度: {display_data['confidence_display']}")
            logger.info(f"🔥 風險等級: {display_data['risk_level']}")
            logger.info(f"💰 建議倉位: {display_data['suggested_position_size']}")
            logger.info(f"💵 當前價格: {display_data['current_price']}")
            logger.info(f"🎯 止盈價格: {display_data['take_profit']}")
            logger.info(f"🛡️ 止損價格: {display_data['stop_loss']}")
            logger.info(f"⏰ 建議持倉: {display_data['suggested_holding_hours']} 小時")
            logger.info(f"📅 生成時間: {display_data['timestamp']}")
            logger.info("=" * 60)
    
    async def start_phase5_scheduler(self):
        """啟動 Phase5 定時調度器"""
        logger.info("📅 Phase5 定時調度器已啟動 (每24小時執行回測)")
        
        while self.running:
            try:
                # 檢查是否需要執行 Phase5 回測
                if self._should_run_phase5():
                    logger.info("🚀 開始執行 Phase5 定時回測...")
                    await self._execute_phase5_backtest()
                
                # 檢查是否需要執行學習反饋分析
                if self._should_run_learning_feedback():
                    logger.info("🧠 開始執行學習反饋分析...")
                    await self._execute_learning_feedback()
                
                # 每小時檢查一次是否需要執行
                await asyncio.sleep(3600)  # 1小時 = 3600秒
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Phase5 調度器錯誤: {e}")
                await asyncio.sleep(300)  # 錯誤後等待5分鐘
    
    def _should_run_phase5(self) -> bool:
        """檢查是否應該執行 Phase5 回測"""
        if not self.phase5_enabled:
            return False
        
        if self.phase5_running:
            logger.debug("Phase5 回測正在運行中，跳過")
            return False
        
        if self.phase5_last_run is None:
            # 首次運行
            return True
        
        # 檢查距離上次運行是否超過24小時
        hours_since_last_run = (datetime.now() - self.phase5_last_run).total_seconds() / 3600
        return hours_since_last_run >= self.phase5_interval_hours
    
    async def _execute_phase5_backtest(self):
        """執行 Phase5 回測優化"""
        if self.phase5_running:
            return
        
        self.phase5_running = True
        self.phase5_last_run = datetime.now()
        
        try:
            logger.info("📊 啟動 Phase5 Lean 回測分析...")
            start_time = time.time()
            
            # 導入 Phase5 回測模組
            from backend.phase5_backtest_validation.phase5_enhanced_backtest_strategy import run_lean_backtest_analysis
            
            # 執行回測分析（使用真實數據）
            symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT"]
            logger.info(f"🔍 分析幣種: {', '.join(symbols)}")
            
            analysis_result = await run_lean_backtest_analysis(symbols)
            
            if analysis_result and analysis_result.get('success'):
                execution_time = time.time() - start_time
                logger.info(f"✅ Phase5 回測完成，耗時: {execution_time:.1f} 秒")
                
                # 記錄回測摘要
                summary = analysis_result.get('summary', {})
                logger.info(f"📈 平均信心度: {summary.get('avg_confidence', 0):.2%}")
                logger.info(f"🎯 制度閘門通過率: {summary.get('regime_gate_pass_rate', 0):.1%}")
                logger.info(f"📊 看多信號: {summary.get('bullish_signals', 0)}")
                logger.info(f"📉 看空信號: {summary.get('bearish_signals', 0)}")
                
                # 檢查是否生成了新的配置文件
                config_path = analysis_result.get('config_saved_path')
                if config_path:
                    logger.info(f"🔄 新配置已生成: {Path(config_path).name}")
                    logger.info("🎯 Phase1A 將在下次信號生成時自動使用新配置")
                
            else:
                logger.warning("⚠️ Phase5 回測未能成功完成")
                
        except Exception as e:
            logger.error(f"❌ Phase5 回測執行失敗: {e}")
            
        finally:
            self.phase5_running = False
            logger.info("📅 Phase5 回測任務完成，下次執行時間: 24小時後")
    
    def _should_run_learning_feedback(self) -> bool:
        """檢查是否應該執行學習反饋分析"""
        if not self.learning_feedback_enabled:
            return False
        
        current_time = time.time()
        return (current_time - self.learning_feedback_last_run) >= self.learning_feedback_interval
    
    async def _execute_learning_feedback(self):
        """執行學習反饋分析"""
        try:
            logger.info("📊 開始學習反饋數據分析...")
            start_time = time.time()
            
            # 導入交易結果追蹤器
            from backend.shared_core.trading_result_tracker import generate_feedback_for_symbol
            
            # 分析交易對
            symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT"]
            feedback_generated = 0
            
            for symbol in symbols:
                try:
                    feedback = await generate_feedback_for_symbol(symbol, hours_back=24)
                    if feedback:
                        logger.info(f"📈 {symbol} 學習反饋:")
                        logger.info(f"   勝率: {feedback.win_rate:.2%}")
                        logger.info(f"   平均收益: {feedback.average_return:.4f}")
                        logger.info(f"   夏普比率: {feedback.sharpe_ratio:.3f}")
                        logger.info(f"   最大回撤: {feedback.max_drawdown:.2%}")
                        
                        # 如果有推薦建議，記錄重要建議
                        if feedback.recommendations:
                            for rec in feedback.recommendations[:2]:  # 顯示前2個建議
                                logger.info(f"   💡 建議: {rec}")
                        
                        # 將反饋傳遞給 Phase2 學習系統
                        if (self.phase1a_generator and 
                            self.phase1a_generator.adaptive_mode and
                            hasattr(self.phase1a_generator.learning_core, 'update_from_feedback')):
                            
                            await self.phase1a_generator.learning_core.update_from_feedback(
                                symbol, feedback
                            )
                            logger.debug(f"🔄 {symbol} 學習參數已更新")
                        
                        feedback_generated += 1
                    else:
                        logger.debug(f"🔍 {symbol} 暫無足夠數據生成反饋")
                        
                except Exception as e:
                    logger.error(f"❌ {symbol} 反饋分析失敗: {e}")
            
            execution_time = time.time() - start_time
            self.learning_feedback_last_run = time.time()
            
            logger.info(f"✅ 學習反饋分析完成")
            logger.info(f"📊 處理 {len(symbols)} 個交易對，生成 {feedback_generated} 個反饋")
            logger.info(f"⏱️ 耗時: {execution_time:.1f} 秒")
            
        except Exception as e:
            logger.error(f"❌ 學習反饋分析執行失敗: {e}")
    
    async def _execute_startup_phase5_optimization(self):
        """啟動前執行 Phase5 參數優化"""
        logger.info("🎯 開始啟動前 Phase5 參數優化...")
        logger.info("💡 目標：為 Phase1A 獲取最佳信號生成參數")
        
        try:
            start_time = time.time()
            
            # 導入 Phase5 回測模組
            from backend.phase5_backtest_validation.phase5_enhanced_backtest_strategy import run_lean_backtest_analysis
            
            # 執行啟動優化回測（使用完整幣種列表但縮短時間範圍）
            symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT", "SOLUSDT", "DOGEUSDT"]  # 完整7個幣種
            logger.info(f"🔍 啟動優化分析幣種: {', '.join(symbols)}")
            
            analysis_result = await run_lean_backtest_analysis(
                symbols,
                lookback_days=7,  # 縮短為7天以加快啟動
                optimization_mode="startup_optimization"
            )
            
            if analysis_result and analysis_result.get('success'):
                execution_time = time.time() - start_time
                logger.info(f"✅ 啟動前 Phase5 優化完成，耗時: {execution_time:.1f} 秒")
                
                # 記錄優化摘要
                summary = analysis_result.get('summary', {})
                logger.info(f"📈 優化信心度: {summary.get('avg_confidence', 0):.2%}")
                logger.info(f"🎯 參數有效性: {summary.get('regime_gate_pass_rate', 0):.1%}")
                
                # 檢查是否生成了新的配置文件
                config_path = analysis_result.get('config_saved_path')
                if config_path:
                    logger.info(f"🔄 啟動優化配置已生成: {Path(config_path).name}")
                    
                    # 立即重新載入 Phase1A 配置
                    if self.phase1a_generator:
                        try:
                            await self.phase1a_generator.reload_configuration()
                            logger.info("✅ Phase1A 已重新載入最新優化配置")
                        except Exception as e:
                            logger.warning(f"⚠️ Phase1A 配置重載失敗: {e}")
                
                logger.info("🚀 Phase1A 現在將使用最新優化參數開始信號生成")
                
            else:
                logger.warning("⚠️ 啟動前 Phase5 優化未完成，使用默認配置")
                
        except Exception as e:
            logger.error(f"❌ 啟動前 Phase5 優化失敗: {e}")
            logger.warning("⚠️ 將使用默認配置啟動 Phase1A")
        
        logger.info("🎯 啟動前優化階段完成，開始正常信號生成流程")
    
    async def start_monitoring(self):
        """啟動監控系統"""
        if self.monitoring_manager:
            try:
                await self.monitoring_manager.start_monitoring()
                logger.info("✅ 監控系統已啟動")
            except Exception as e:
                logger.error(f"❌ 監控系統啟動失敗: {e}")
    
    async def run(self):
        """運行完整系統"""
        logger.info("🚀 啟動 Trading X 生產環境系統...")
        
        # 初始化系統
        if not await self.initialize_systems():
            logger.error("❌ 系統初始化失敗，退出")
            return
        
        # ⭐ 關鍵優化：啟動前先執行 Phase5 回測獲取最優參數
        logger.info("🎯 執行啟動前 Phase5 參數優化...")
        await self._execute_startup_phase5_optimization()
        
        self.running = True
        
        try:
            # 啟動監控系統
            await self.start_monitoring()
            
            # 並行運行信號生成和 Phase5 定時任務
            signal_task = asyncio.create_task(self.start_signal_generation_loop())
            phase5_task = asyncio.create_task(self.start_phase5_scheduler())
            
            # 等待任意一個任務完成（通常是由於錯誤或停止信號）
            done, pending = await asyncio.wait(
                [signal_task, phase5_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # 取消未完成的任務
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
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
        
        if self.monitoring_manager:
            try:
                await self.monitoring_manager.stop_monitoring()
            except Exception as e:
                logger.error(f"監控系統關閉錯誤: {e}")
        
        logger.info("✅ 系統已安全關閉")

async def main():
    """主函數"""
    system = ProductionTradingSystem()
    await system.run()

if __name__ == "__main__":
    print("🎯 Trading X 生產環境啟動器")
    print("📊 Phase1A + Phase2 完整整合系統")
    print("🧠 自適應學習已啟用")
    print("🎯 Phase3 智能決策引擎已整合")
    print("📈 Phase4 統一監控系統已重建")
    print("⏰ Phase5 24小時自動回測調度已啟用")
    print("🔄 學習反饋機制已完善")
    print("⭐ 啟動前 Phase5 參數優化已啟用")
    print("📈 即將開始真實信號生成...")
    print("⚠️ 按 Ctrl+C 停止系統")
    print("-" * 50)
    
    asyncio.run(main())
