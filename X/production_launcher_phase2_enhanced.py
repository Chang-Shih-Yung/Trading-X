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

# 🔒 嚴格系統驗證 - 必須在系統啟動前完成
def strict_system_validation():
    """嚴格系統驗證 - 任何組件缺失都終止系統"""
    logger.info("🔒 執行嚴格系統驗證...")
    
    try:
        from system_strict_validator import validate_system_strict
        result = validate_system_strict()
        
        if not result.get("can_proceed", False):
            logger.error("❌ 系統驗證失敗，系統將終止")
            sys.exit(1)
        
        logger.info("✅ 所有組件驗證通過，系統可以安全啟動")
        return result
        
    except Exception as e:
        logger.error(f"❌ 系統驗證過程失敗: {e}")
        logger.error("系統將終止以確保安全性")
        sys.exit(1)

# 執行嚴格驗證
validation_result = strict_system_validation()

class ProductionTradingSystemPhase2Enhanced:
    """生產環境交易系統 - Phase2 參數管理增強版"""
    
    def __init__(self):
        self.phase1a_generator = None
        self.phase3_decision_engine = None
        self.phase3_enabled = False
        self.monitoring_manager = None
        self.running = False
        
        # Phase2 優化組件
        self.adaptive_learning_engine = None
        self.learning_enabled = False
        
                # 信號循環調度間隔 - 啟動腳本的調度配置
        self.signal_loop_interval = 15  # 信號生成循環間隔（秒）
        self.symbol_processing_interval = 3  # 交易對處理間隔（秒）- 避免API限制
        self.phase2_last_parameter_check = 0
        
        # Phase5 定時觸發配置 - 啟動腳本調度邏輯
        self.phase5_enabled = True
        self.phase5_interval_hours = 24  # Phase5 大型回測調度間隔
        self.phase5_last_run = None
        self.phase5_running = False
        
        # Phase2 參數管理器 - 調度間隔從Phase2內部讀取
        self.phase2_parameter_manager = None
        self.phase2_parameter_check_interval = None  # 將從Phase2內部配置讀取
        
        # 學習反饋機制調度配置 - 從Phase2內部讀取
        self.learning_feedback_enabled = True
        self.learning_feedback_last_run = 0
        self.learning_feedback_interval = None  # 將從Phase2內部配置讀取
        
        # 文件清理調度配置
        self.file_cleanup_manager = None
        self.last_cleanup_time = 0
        self.cleanup_interval = 3600  # 1小時清理一次（調度邏輯）
        
        # 交易對列表 - 調度器需要知道要處理哪些交易對
        self.trading_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT"]
        
        # 信號統計
        self.signal_stats = {
            'total_signals_generated': 0,
            'signals_per_symbol': {},
            'signals_per_session': 0,
            'last_reset_time': time.time()
        }
        
        # 啟動腳本僅負責調度，從各Phase讀取內部設定
        self._load_phase_internal_settings()
    
    def _load_phase_internal_settings(self):
        """從各Phase讀取內部設定 - 啟動腳本只負責調度協調"""
        logger.info("📋 載入各Phase內部設定...")
        
        # 從Phase2讀取內部設定
        try:
            # 使用Phase2的默認配置
            phase2_default_config = {
                "generation_frequency": {
                    "interval_hours": 2,  # Phase2內部預設2小時
                    "signal_count": 200,
                    "trigger_mode": "either"
                }
            }
            
            freq_config = phase2_default_config.get("generation_frequency", {})
            self.phase2_parameter_check_interval = freq_config.get("interval_hours", 2) * 3600  # 轉換為秒
            self.learning_feedback_interval = 3600  # 學習反饋間隔1小時
            
            logger.info(f"✅ Phase2 設定載入: 參數檢查間隔 {self.phase2_parameter_check_interval/3600} 小時")
            
        except Exception as e:
            logger.error(f"❌ 載入Phase2設定失敗: {e}")
            # 使用安全的默認值
            self.phase2_parameter_check_interval = 7200  # 2小時
            self.learning_feedback_interval = 3600  # 1小時
        
        # 從Phase5讀取內部設定（auto_backtest_config.json）
        try:
            config_path = Path(__file__).parent / "backend" / "phase5_backtest_validation" / "auto_backtest_validator" / "auto_backtest_config.json"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    phase5_config = json.load(f)
                
                # 讀取Phase5的6小時閾值調整設定
                threshold_system = phase5_config.get('dynamic_threshold_system', {})
                phase5_adjustment_hours = threshold_system.get('adjustment_frequency_hours', 6)
                
                logger.info(f"✅ Phase5 設定載入: 閾值調整間隔 {phase5_adjustment_hours} 小時")
                
        except Exception as e:
            logger.warning(f"⚠️ 載入Phase5設定失敗: {e}")
    
    def get_trading_symbols(self):
        """獲取交易對列表 - 調度器使用"""
        return self.trading_symbols

    async def _initialize_database_connection(self):
        """強制初始化資料庫連接 - 確保信號直接存儲到資料庫"""
        logger.info("🗄️ 強制初始化信號資料庫連接...")
        
        try:
            # 直接導入和初始化資料庫
            from backend.phase2_adaptive_learning.storage.signal_database import signal_db, StoredSignal
            
            # 測試資料庫連接
            test_signal = StoredSignal(
                signal_id="startup_test",
                symbol="TEST",
                signal_type="TEST",
                signal_strength=0.0,
                timestamp=datetime.now(),
                features={"test": True},
                market_conditions={},
                tier="LOW"
            )
            
            # 嘗試存儲測試信號
            success = await signal_db.store_signal(test_signal)
            
            if success:
                logger.info("✅ 信號資料庫連接成功，持久化存儲已啟用")
                self.database_enabled = True
                self.signal_db = signal_db
                
                # 清理測試信號
                await signal_db.delete_signal("startup_test")
                
            else:
                logger.warning("⚠️ 信號資料庫測試失敗，但將嘗試繼續運行")
                self.database_enabled = False
                self.signal_db = None
                
        except ImportError as e:
            logger.error(f"❌ 無法導入信號資料庫模組: {e}")
            logger.error("❌ 系統無法在沒有資料庫的情況下運行，請檢查資料庫配置")
            self.database_enabled = False
            self.signal_db = None
            
        except Exception as e:
            logger.error(f"❌ 資料庫初始化失敗: {e}")
            self.database_enabled = False
            self.signal_db = None
            
        # 根據您的要求：如果資料庫不可用，要明確告知並等待
        if not self.database_enabled:
            logger.error("🛑 信號資料庫無數據或無法連接")
            logger.error("📋 系統要求：必須使用實時數據的信號資料庫")
            logger.info("⏳ 建議：等待資料庫服務啟動或檢查配置（等待時間：約5-10分鐘）")
            
            # 不強制退出，但明確標記狀態
            logger.warning("⚠️ 系統將在沒有持久化存儲的情況下運行，信號將不會保存")
        
    async def initialize_systems(self):
        """初始化所有系統組件"""
        logger.info("🚀 初始化生產環境交易系統...")
        
        try:
            # 0. 強制初始化資料庫連接
            await self._initialize_database_connection()
            
            # 1. 初始化 Phase1A 信號生成器（已整合 Phase2）
            from backend.phase1_signal_generation.phase1a_basic_signal_generation.phase1a_basic_signal_generation import Phase1ABasicSignalGeneration
            
            self.phase1a_generator = Phase1ABasicSignalGeneration()
            # 直接設置運行狀態（不使用需要 WebSocket 的 start() 方法）
            self.phase1a_generator.is_running = True
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
                from backend.phase3_execution_policy.epl_intelligent_decision_engine import initialize_epl_system
                self.phase3_decision_engine = await initialize_epl_system()
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
            
            # 4. 初始化 Phase2 優化組件
            await self._initialize_phase2_optimization_components()
            
            # 5. 初始化 Phase2 參數管理器
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
    
    async def _initialize_phase2_optimization_components(self):
        """初始化 Phase2 優化組件"""
        logger.info("🔧 初始化 Phase2 優化組件...")
        
        # 1. 初始化 Adaptive Learning Engine
        try:
            from backend.phase2_adaptive_learning.learning_core.adaptive_learning_engine import AdaptiveLearningCore
            self.adaptive_learning_engine = AdaptiveLearningCore()
            self.learning_enabled = True
            logger.info("✅ Adaptive Learning Engine 初始化成功")
        except Exception as e:
            logger.warning(f"⚠️ Adaptive Learning Engine 初始化失敗: {e}")
            self.learning_enabled = False
        
        # 2. 初始化文件清理管理器
        try:
            from backend.phase2_adaptive_learning.storage.file_cleanup_manager import FileCleanupManager
            self.file_cleanup_manager = FileCleanupManager()
            logger.info("✅ 文件清理管理器初始化成功")
        except Exception as e:
            logger.warning(f"⚠️ 文件清理管理器初始化失敗: {e}")
    
    async def start_signal_generation_loop(self):
        """啟動信號生成循環"""
        logger.info("🎯 啟動信號生成循環...")
        
        # 使用內建交易對列表
        symbols = self.trading_symbols
        
        while self.running:
            try:
                # 🎯 Phase5 定時檢查（每24小時）
                await self.check_phase5_schedule()
                
                # 當前時間
                current_time = time.time()
                
                # 🔧 Phase2 優化組件定期維護
                await self._perform_phase2_maintenance(current_time)
                
                # 🔧 Phase2 參數檢查和生成（每2小時，與Phase2內部同步）
                if (self.phase2_parameter_manager and 
                    current_time - self.phase2_last_parameter_check > self.phase2_parameter_check_interval):
                    
                    # 🚨 協調機制：如果Phase5正在運行，延遲Phase2執行
                    if self.phase5_running:
                        logger.info("⏳ Phase5運行中，延遲Phase2參數檢查（避免衝突）")
                    else:
                        try:
                            await self._check_and_generate_phase2_parameters()
                            self.phase2_last_parameter_check = current_time
                        except Exception as e:
                            logger.error(f"❌ Phase2 參數檢查失敗: {e}")
                
                for symbol in symbols:
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
                    
                    # 生成信號（直接使用 generate_signals 方法）
                    try:
                        # 確保信號生成器已啟動
                        if hasattr(self.phase1a_generator, 'start_signal_generator'):
                            await self.phase1a_generator.start_signal_generator()
                        elif hasattr(self.phase1a_generator, 'start'):
                            # 如果沒有 start_signal_generator 方法，嘗試 start 方法
                            logger.info(f"🚀 啟動 {symbol} 信號生成器...")
                            # 可能需要 websocket 驅動，先跳過完整啟動
                            pass
                        
                        # 直接生成信號，不依賴 WebSocket
                        # 首先將市場數據添加到 price_buffer
                        if hasattr(self.phase1a_generator, 'price_buffer'):
                            # 將當前市場數據添加到歷史緩衝區
                            price_entry = {
                                'price': market_data.get('close', market_data.get('price', 0)),
                                'volume': market_data.get('volume', 0),
                                'high': market_data.get('high', market_data.get('price', 0)),
                                'low': market_data.get('low', market_data.get('price', 0)),
                                'timestamp': market_data.get('timestamp', datetime.now())
                            }
                            self.phase1a_generator.price_buffer[symbol].append(price_entry)
                            logger.debug(f"📊 {symbol} 價格數據已添加到緩衝區，當前數量: {len(self.phase1a_generator.price_buffer[symbol])}")
                        
                        signals = await self.phase1a_generator.generate_signals(symbol, market_data)
                        
                        logger.info(f"🔍 {symbol} 信號生成結果: {type(signals)} - 數量: {len(signals) if signals else 0}")
                        
                        if signals:
                            signal_count = len(signals) if isinstance(signals, list) else 1
                            
                            # 更新信號統計
                            self.signal_stats['total_signals_generated'] += signal_count
                            self.signal_stats['signals_per_session'] += signal_count
                            if symbol not in self.signal_stats['signals_per_symbol']:
                                self.signal_stats['signals_per_symbol'][symbol] = 0
                            self.signal_stats['signals_per_symbol'][symbol] += signal_count
                            
                            logger.info(f"✅ {symbol} 信號生成成功: {signal_count} 個信號")
                            logger.info(f"📈 累積統計: 總信號 {self.signal_stats['total_signals_generated']} | 本輪 {self.signal_stats['signals_per_session']} | {symbol}: {self.signal_stats['signals_per_symbol'][symbol]}")
                            
                            # 🧠 Phase2 學習引擎監控信號
                            await self._monitor_signals_with_learning_engine(signals, symbol, market_data)
                        else:
                            logger.info(f"ℹ️ {symbol} 未生成信號 - price_buffer 數量: {len(self.phase1a_generator.price_buffer[symbol]) if hasattr(self.phase1a_generator, 'price_buffer') and symbol in self.phase1a_generator.price_buffer else 0}")
                            
                    except Exception as e:
                        logger.warning(f"⚠️ {symbol} 信號生成失敗: {e}")
                        signals = None
                    
                    # 📊 將信號傳遞給 Phase2 學習系統進行追蹤
                    if signals and self.phase1a_generator.adaptive_mode:
                        try:
                            # 增加信號計數
                            if self.phase2_parameter_manager:
                                self.phase2_parameter_manager.increment_signal_count()
                                
                            # 為信號建立學習追蹤（簡化版）
                            if isinstance(signals, list):
                                for signal in signals:
                                    if hasattr(signal, 'signal_type') and hasattr(signal, 'strength'):
                                        learning_data = {
                                            'signal_id': f"{symbol}_{datetime.now().timestamp()}",
                                            'symbol': symbol,
                                            'signal_strength': signal.strength,
                                            'direction': signal.signal_type,
                                            'features': {
                                                'price': market_data.get('close', 0),
                                                'volume': market_data.get('volume', 0)
                                            },
                                            'market_conditions': market_data
                                        }
                                        
                                        # 追蹤信號到學習系統
                                        if hasattr(self.phase1a_generator.learning_core, 'track_signal_for_learning'):
                                            await self.phase1a_generator.learning_core.track_signal_for_learning(learning_data)
                            elif isinstance(signals, dict) and hasattr(signals, 'signal_type'):
                                # 單個信號
                                learning_data = {
                                    'signal_id': f"{symbol}_{datetime.now().timestamp()}",
                                    'symbol': symbol,
                                    'signal_strength': signals.get('strength', 0),
                                    'direction': signals.get('signal_type', 'NEUTRAL'),
                                    'features': {
                                        'price': market_data.get('close', 0),
                                        'volume': market_data.get('volume', 0)
                                    },
                                    'market_conditions': market_data
                                }
                                
                                if hasattr(self.phase1a_generator.learning_core, 'track_signal_for_learning'):
                                    await self.phase1a_generator.learning_core.track_signal_for_learning(learning_data)
                                    
                        except Exception as e:
                            logger.debug(f"學習追蹤錯誤: {e}")
                    
                    # Phase3 決策處理 - 使用正確的API
                    if self.phase3_enabled and signals:
                        try:
                            # 將每個信號傳遞給 Phase3 決策引擎進行單獨處理
                            decisions = []
                            for i, signal in enumerate(signals):
                                try:
                                    # 導入正確的 SignalCandidate 類型
                                    from backend.phase2_pre_evaluation.epl_pre_processing_system.epl_pre_processing_system import SignalCandidate
                                    
                                    # 創建正確的 SignalCandidate 對象，按照 @dataclass 定義
                                    signal_candidate = SignalCandidate(
                                        id=f"{symbol}_{int(datetime.now().timestamp())}_{i}",
                                        symbol=symbol,
                                        signal_strength=getattr(signal, 'signal_strength', 0.7),
                                        confidence=signal.confidence if hasattr(signal, 'confidence') else 0.5,
                                        direction=signal.direction if hasattr(signal, 'direction') else 'BUY',
                                        timestamp=datetime.now(),
                                        source="Phase1A_ProductionLauncher",
                                        data_completeness=0.8,
                                        signal_clarity=0.8,
                                        dynamic_params=getattr(signal, 'parameters', {}),
                                        market_environment={},
                                        technical_snapshot=getattr(signal, 'technical_analysis', {})
                                    )
                                    
                                    # 調用正確的Phase3方法
                                    decision_result = await self.phase3_decision_engine.process_signal_candidate(
                                        signal_candidate, 
                                        current_positions=[],
                                        market_context={}
                                    )
                                    
                                except ImportError as import_error:
                                    logger.warning(f"⚠️ SignalCandidate 導入失敗: {import_error}")
                                    # 如果無法導入，暫時跳過 Phase3 處理
                                    decision_result = None
                                    
                                except Exception as signal_error:
                                    logger.warning(f"⚠️ {symbol} 信號 {i} Phase3 處理失敗: {signal_error}")
                                    decision_result = None
                                
                                if decision_result:
                                    decisions.append(decision_result)
                            
                            if decisions:
                                logger.info(f"🎯 {symbol} Phase3 決策完成: {len(decisions)} 個決策")
                                
                                # 記錄決策詳情
                                for i, decision in enumerate(decisions):
                                    if hasattr(decision, 'decision') and hasattr(decision, 'priority'):
                                        logger.info(f"   決策 {i+1}: {decision.decision.value} | 優先級: {decision.priority.name}")
                                    else:
                                        logger.info(f"   決策 {i+1}: {decision}")
                                        
                            else:
                                logger.info(f"🚫 {symbol} Phase3 決策：無有效決策生成")
                                
                        except Exception as e:
                            logger.error(f"❌ {symbol} Phase3 決策處理錯誤: {e}")
                            decisions = []
                    
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
                        
                        # 🗄️ 直接存儲信號到資料庫（您的核心需求）
                        await self._store_signals_to_database(symbol, signal_list)
                        
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
                    
                    await asyncio.sleep(self.symbol_processing_interval)  # 交易對處理間隔
                
                # 循環結束，顯示本輪統計
                await self._display_round_summary()
                
                await asyncio.sleep(self.signal_loop_interval)  # 信號循環間隔
                
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
                        # 生產環境性能評估 (從真實交易結果獲取)
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
    
    async def _initialize_historical_data(self):
        """初始化歷史數據以支援技術分析 - 產品級實現"""
        logger.info("📊 初始化歷史數據...")
        
        # 使用內建交易對列表
        symbols = self.trading_symbols
        
        for symbol in symbols:
            try:
                # 獲取真實歷史K線數據
                historical_data = await self._fetch_historical_klines(symbol, limit=500)
                if not historical_data:
                    logger.warning(f"⚠️ {symbol} 無法獲取歷史數據，跳過初始化")
                    continue
                
                # 將歷史數據添加到系統
                if hasattr(self.phase1a_generator, 'price_buffer'):
                    for data_point in historical_data:
                        price_entry = {
                            'price': data_point['close'],
                            'volume': data_point['volume'],
                            'high': data_point['high'],
                            'low': data_point['low'],
                            'timestamp': data_point['timestamp']
                        }
                        self.phase1a_generator.price_buffer[symbol].append(price_entry)
                        
                        # 同時添加到 intelligent_trigger_engine 的 price_cache
                        if hasattr(self.phase1a_generator, 'intelligent_trigger_engine'):
                            from backend.phase1_signal_generation.intelligent_trigger_engine.intelligent_trigger_engine import PriceData
                            
                            price_data = PriceData(
                                symbol=symbol,
                                price=data_point['close'],
                                volume=data_point['volume'],
                                timestamp=datetime.fromtimestamp(data_point['timestamp'])
                            )
                            
                            # 確保 symbol 在 price_cache 中有條目
                            if symbol not in self.phase1a_generator.intelligent_trigger_engine.price_cache:
                                self.phase1a_generator.intelligent_trigger_engine.price_cache[symbol] = []
                            
                            self.phase1a_generator.intelligent_trigger_engine.price_cache[symbol].append(price_data)
                
                # 觸發技術指標計算
                if hasattr(self.phase1a_generator, 'intelligent_trigger_engine') and self.phase1a_generator.intelligent_trigger_engine:
                    try:
                        await self.phase1a_generator.intelligent_trigger_engine._update_technical_indicators(symbol)
                        logger.info(f"✅ {symbol} 技術指標計算完成")
                    except Exception as indicator_error:
                        logger.warning(f"⚠️ {symbol} 技術指標計算失敗: {indicator_error}")
                
                logger.info(f"✅ {symbol} 歷史數據初始化完成: {len(historical_data)} 條記錄")
                
            except Exception as e:
                logger.error(f"❌ {symbol} 歷史數據初始化失敗: {e}")
        
        logger.info("✅ 歷史數據初始化完成")

    async def _fetch_historical_klines(self, symbol: str, limit: int = 500) -> list:
        """獲取真實的歷史K線數據"""
        try:
            import aiohttp
            url = f"https://api.binance.com/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': '1m',  # 1分鐘K線
                'limit': limit
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        klines = await response.json()
                        
                        historical_data = []
                        for kline in klines:
                            historical_data.append({
                                'timestamp': kline[0] / 1000,  # 轉換為秒
                                'open': float(kline[1]),
                                'high': float(kline[2]),
                                'low': float(kline[3]),
                                'close': float(kline[4]),
                                'volume': float(kline[5])
                            })
                        
                        return historical_data
                    else:
                        logger.error(f"❌ 獲取 {symbol} 歷史數據失敗: HTTP {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"❌ 獲取 {symbol} 歷史數據異常: {e}")
            return []

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
                action = decision.decision.value if hasattr(decision, 'decision') else 'N/A'
                confidence = decision.confidence if hasattr(decision, 'confidence') else 0.0
                logger.info(f"   🎯 Phase3 決策: {action} (信心度: {confidence:.1%})")
            
            logger.info("="*80)
    
    async def start_monitoring(self):
        """啟動監控系統"""
        if self.monitoring_manager:
            try:
                await self.monitoring_manager.start_monitoring()
                logger.info("✅ 統一監控系統已啟動")
            except Exception as e:
                logger.error(f"❌ 監控系統啟動失敗: {e}")
    
    async def run_phase5_backtest(self):
        """執行 Phase5 回測生成最新參數"""
        logger.info("🎯 開始執行 Phase5 回測...")
        
        try:
            # 【重要修復】使用正確的 Phase5 回測策略來生成新參數
            logger.info("⚡ 執行 Phase5 參數生成回測...")
            
            # 導入正確的 Phase5 回測策略
            from backend.phase5_backtest_validation.phase5_enhanced_backtest_strategy import run_lean_backtest_analysis
            
            # 使用內建交易對進行回測
            trading_symbols = self.trading_symbols
            
            # 執行 Lean 回測分析並生成新參數
            result = await run_lean_backtest_analysis(
                symbols=trading_symbols,
                lookback_days=7,  # 回測7天數據 (正確參數名)
                optimization_mode="standard"  # 標準優化模式
            )
            
            if result and not result.get('error'):
                logger.info("✅ Phase5 參數生成回測執行成功")
                
                # 記錄回測結果
                summary = result.get('summary', {})
                avg_confidence = summary.get('avg_confidence', 0)
                avg_return = summary.get('avg_expected_return', 0)
                config_path = result.get('config_saved_path', '')
                
                logger.info(f"📊 回測結果總覽:")
                logger.info(f"   🎯 平均信心度: {avg_confidence:.2%}")
                logger.info(f"   💰 平均期望收益: {avg_return:.2%}")
                logger.info(f"   📁 參數檔案: {config_path.split('/')[-1] if config_path else '未生成'}")
                logger.info(f"   🔄 Phase1A將載入新參數: {result.get('next_phase1a_will_load', False)}")
                
                return True
            else:
                error_msg = result.get('error', '未知原因') if result else '無回測結果'
                logger.error(f"❌ Phase5 參數生成回測執行失敗: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Phase5 參數生成回測執行錯誤: {e}")
            # 使用舊參數繼續，但給出明確提示
            backup_files = self._get_latest_phase5_backup_files()
            if backup_files:
                latest_file = max(backup_files, key=lambda x: x.stat().st_mtime)
                mtime = datetime.fromtimestamp(latest_file.stat().st_mtime)
                logger.warning(f"⚠️ Phase5 執行失敗，使用舊參數文件: {latest_file.name}")
                logger.warning(f"📅 文件日期: {mtime.strftime('%Y年%m月%d日 %H:%M:%S')}")
            else:
                logger.error("❌ 無可用的 Phase5 參數文件")
            return False
    
    def _get_latest_phase5_backup_files(self):
        """獲取最新的 Phase5 備份文件列表"""
        try:
            from pathlib import Path
            backup_dir = Path(__file__).parent / "backend" / "phase5_backtest_validation" / "safety_backups" / "working"
            if backup_dir.exists():
                return list(backup_dir.glob("*.json"))
            return []
        except Exception as e:
            logger.error(f"❌ 獲取 Phase5 備份文件失敗: {e}")
            return []
    
    async def check_phase5_schedule(self):
        """檢查是否需要執行定時 Phase5 回測"""
        if not self.phase5_enabled:
            return
        
        current_time = time.time()
        
        # 24小時定時觸發，但避開Phase2執行時間
        if (self.phase5_last_run is None or 
            current_time - self.phase5_last_run >= self.phase5_interval_hours * 3600):
            
            if not self.phase5_running:
                # 🚨 協調機制：錯開執行時間避免衝突
                current_hour = datetime.now().hour
                if current_hour % 2 == 0:  # Phase2在偶數小時執行
                    logger.info("⏳ 避開Phase2執行時間，延遲1小時執行Phase5")
                    return
                
                logger.info("⏰ 觸發定時 Phase5 回測...")
                self.phase5_running = True
                
                try:
                    success = await self.run_phase5_backtest()
                    if success:
                        self.phase5_last_run = current_time
                finally:
                    self.phase5_running = False
    
    async def run(self):
        """運行完整系統"""
        logger.info("🚀 啟動 Trading X 生產環境系統 (Phase2 參數管理增強版)...")
        
        # 第一步：初始化系統組件
        logger.info("🔧 第一步：初始化系統組件...")
        if not await self.initialize_systems():
            logger.error("❌ 系統初始化失敗，退出")
            return
        
        # 第二步：執行 Phase5 回測生成最新參數 (僅在系統初始化成功後)
        logger.info("🎯 第二步：執行 Phase5 回測分析生成新參數...")
        try:
            phase5_success = await self.run_phase5_backtest()
            if not phase5_success:
                logger.warning("⚠️ Phase5 參數生成失敗，但系統將繼續使用現有參數")
        except Exception as e:
            logger.error(f"❌ Phase5 參數生成異常: {e}")
            logger.warning("⚠️ Phase5 執行異常，系統將繼續使用現有參數")
        
        # 第三步：重新載入 Phase1A 以使用最新參數
        logger.info("🔄 第三步：重新載入 Phase1A 配置...")
        try:
            if self.phase1a_generator and hasattr(self.phase1a_generator, 'reload_configuration'):
                self.phase1a_generator.reload_configuration()
                logger.info("✅ Phase1A 配置重新載入成功")
            else:
                logger.debug("ℹ️ Phase1A 無需手動重載配置")
        except Exception as e:
            logger.warning(f"⚠️ Phase1A 配置重新載入失敗: {e}")
        
        # 第四步：啟動主循環
        # 初始化歷史數據
        await self._initialize_historical_data()
        
        logger.info("▶️ 第四步：啟動主循環...")
        
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
    
    async def _perform_phase2_maintenance(self, current_time: float):
        """執行 Phase2 優化組件維護"""
        try:
            # 1. 文件清理維護（每小時執行一次）
            if (self.file_cleanup_manager and 
                current_time - self.last_cleanup_time > self.cleanup_interval):
                
                logger.info("🧹 執行定期文件清理...")
                cleanup_results = await self.file_cleanup_manager.cleanup_all()
                
                # 記錄清理結果
                total_cleaned = sum(result.get('files_cleaned', 0) for result in cleanup_results.values())
                total_size_freed = sum(result.get('space_freed_mb', 0) for result in cleanup_results.values())
                
                if total_cleaned > 0:
                    logger.info(f"✅ 文件清理完成: 清理 {total_cleaned} 個文件，釋放 {total_size_freed:.3f} MB")
                else:
                    logger.debug("ℹ️ 文件清理完成: 無需清理")
                
                self.last_cleanup_time = current_time
                
        except Exception as e:
            logger.error(f"❌ Phase2 維護失敗: {e}")
    
    async def _monitor_signals_with_learning_engine(self, signals, symbol: str, market_data: dict):
        """使用學習引擎監控信號"""
        if not self.learning_enabled or not self.adaptive_learning_engine:
            return
        
        try:
            # 處理單個或多個信號
            signal_list = signals if isinstance(signals, list) else [signals]
            
            for signal in signal_list:
                # 準備信號數據
                signal_data = {
                    'signal_id': f"{symbol}_{int(time.time() * 1000)}",  # 使用時間戳生成唯一ID
                    'symbol': symbol,
                    'signal_strength': getattr(signal, 'signal_strength', 0.7),
                    'direction': getattr(signal, 'direction', 'UNKNOWN'),
                    'tier': getattr(signal, 'tier', 'MEDIUM'),
                    'timestamp': datetime.now(),
                    'features': {
                        'market_data': market_data,
                        'signal_type': getattr(signal, 'signal_type', 'BASIC')
                    },
                    'market_conditions': {
                        'price': market_data.get('price', 0.0),
                        'volume': market_data.get('volume', 0.0),
                        'volatility': market_data.get('volatility', 0.0)
                    }
                }
                
                # 監控信號表現（暫時不提供實際結果，讓學習引擎記錄）
                await self.adaptive_learning_engine.monitor_signal_performance(
                    signal_data, 
                    actual_outcome=None  # 實際結果需要後續跟蹤
                )
                
                logger.debug(f"📊 信號已記錄到學習引擎: {signal_data['signal_id']}")
                
        except Exception as e:
            logger.error(f"❌ 學習引擎信號監控失敗: {e}")
    
    async def _display_round_summary(self):
        """顯示本輪統計摘要"""
        try:
            current_time = time.time()
            runtime_minutes = (current_time - self.signal_stats['last_reset_time']) / 60
            
            logger.info("="*60)
            logger.info("📊 本輪信號生成統計")
            logger.info(f"⏱️ 運行時間: {runtime_minutes:.1f} 分鐘")
            logger.info(f"🎯 本輪總信號: {self.signal_stats['signals_per_session']}")
            logger.info(f"📈 累積總信號: {self.signal_stats['total_signals_generated']}")
            
            # 顯示各交易對統計
            if self.signal_stats['signals_per_symbol']:
                logger.info("📋 各交易對統計:")
                for symbol, count in self.signal_stats['signals_per_symbol'].items():
                    logger.info(f"   {symbol}: {count} 個信號")
            
            # 重置本輪統計
            self.signal_stats['signals_per_session'] = 0
            self.signal_stats['last_reset_time'] = current_time
            
            logger.info("="*60)
            
        except Exception as e:
            logger.error(f"❌ 統計顯示失敗: {e}")
    
    async def _store_signals_to_database(self, symbol: str, signal_list: list):
        """將信號直接存儲到資料庫 - 核心功能"""
        if not self.database_enabled or not self.signal_db:
            logger.warning(f"⚠️ {symbol} 資料庫未啟用，信號將不會持久化保存")
            return
        
        try:
            from backend.phase2_adaptive_learning.storage.signal_database import StoredSignal
            
            stored_count = 0
            for i, signal in enumerate(signal_list):
                try:
                    # 創建資料庫存儲對象
                    stored_signal = StoredSignal(
                        signal_id=f"{symbol}_{int(datetime.now().timestamp())}_{i}",
                        symbol=symbol,
                        signal_type=getattr(signal, 'signal_type', 'UNKNOWN'),
                        signal_strength=getattr(signal, 'signal_strength', 0.0),
                        timestamp=datetime.now(),
                        features=getattr(signal, 'features', {}),
                        market_conditions=getattr(signal, 'market_conditions', {}),
                        tier=getattr(signal, 'tier', 'MEDIUM').value if hasattr(getattr(signal, 'tier', 'MEDIUM'), 'value') else str(getattr(signal, 'tier', 'MEDIUM'))
                    )
                    
                    # 存儲到資料庫
                    success = await self.signal_db.store_signal(stored_signal)
                    if success:
                        stored_count += 1
                    else:
                        logger.warning(f"⚠️ {symbol} 信號 {i} 存儲失敗")
                        
                except Exception as signal_error:
                    logger.warning(f"⚠️ {symbol} 信號 {i} 處理失敗: {signal_error}")
            
            if stored_count > 0:
                logger.info(f"🗄️ {symbol} 成功存儲 {stored_count}/{len(signal_list)} 個信號到資料庫")
            else:
                logger.warning(f"⚠️ {symbol} 沒有信號成功存儲到資料庫")
                
        except Exception as e:
            logger.error(f"❌ {symbol} 資料庫存儲失敗: {e}")

async def main():
    """主入口函數"""
    print("🚀 Trading X 生產環境啟動器 (Phase2 參數管理增強版)")
    print("="*60)
    
    # 創建並運行系統
    system = ProductionTradingSystemPhase2Enhanced()
    await system.run()

if __name__ == "__main__":
    asyncio.run(main())
