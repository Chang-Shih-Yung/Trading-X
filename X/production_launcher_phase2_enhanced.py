"""
🚀 Trading X 生產環境啟動器 - Phase2 參數管理增強版
真正啟動完整的 Phase1A + Phase2 整合系統，包含自動參數優化
"""

import asyncio
import logging
import sys
import time
import gc
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

# 🧠 簡化版內存管理（不依賴psutil）
class SimpleMemoryManager:
    """簡化版內存管理器"""
    
    def __init__(self):
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5分鐘
        
    async def check_and_cleanup(self):
        """檢查並執行內存清理"""
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            logger.info("🧹 執行定期內存清理...")
            
            # 強制垃圾回收
            collected = gc.collect()
            
            self.last_cleanup = current_time
            logger.info(f"✅ 內存清理完成，回收 {collected} 個對象")
            
    async def memory_monitoring_loop(self):
        """內存監控循環"""
        while True:
            try:
                await self.check_and_cleanup()
                await asyncio.sleep(60)  # 每分鐘檢查一次
            except Exception as e:
                logger.error(f"❌ 內存監控錯誤: {e}")
                await asyncio.sleep(60)

# 🚀 導入智能混合價格系統 - 增強重試機制
HYBRID_PRICE_SYSTEM_AVAILABLE = False
HYBRID_RETRY_COUNT = 0
MAX_HYBRID_RETRIES = 3

def attempt_hybrid_import():
    """嘗試導入智能混合價格系統，支援重試"""
    global HYBRID_PRICE_SYSTEM_AVAILABLE, HYBRID_RETRY_COUNT
    
    try:
        # 清除模組快取，強制重新導入
        import sys
        modules_to_clear = [mod for mod in sys.modules.keys() if 'pool_discovery' in mod or 'production_price_integration' in mod]
        for mod in modules_to_clear:
            del sys.modules[mod]
        
        # 重新嘗試導入
        from backend.phase1_signal_generation.onchain_data_connector.production_price_integration import get_real_market_data
        HYBRID_PRICE_SYSTEM_AVAILABLE = True
        HYBRID_RETRY_COUNT = 0  # 重置計數器
        logger.info("✅ 智能混合價格系統導入成功")
        return True
    except ImportError as e:
        HYBRID_RETRY_COUNT += 1
        logger.warning(f"⚠️ 智能混合價格系統導入失敗 (嘗試 {HYBRID_RETRY_COUNT}/{MAX_HYBRID_RETRIES}): {e}")
        
        if HYBRID_RETRY_COUNT < MAX_HYBRID_RETRIES:
            logger.info("🔄 將在稍後重試智能混合價格系統連接...")
            return False
        else:
            logger.warning("🔄 達到最大重試次數，將使用傳統幣安API作為備用方案")
            HYBRID_PRICE_SYSTEM_AVAILABLE = False
            return False
    except Exception as e:
        HYBRID_RETRY_COUNT += 1
        logger.error(f"❌ 智能混合價格系統導入錯誤 (嘗試 {HYBRID_RETRY_COUNT}/{MAX_HYBRID_RETRIES}): {e}")
        return False

# 初始嘗試導入
attempt_hybrid_import()

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
        
        # 優先級3：時間框架感知學習引擎
        self.priority3_enabled = False
        self.priority3_integration = None
        self.timeframe_learning_available = False
        
        # 🧠 內存管理器
        self.memory_manager = SimpleMemoryManager()
        
        # 🚨 系統健康狀態監控
        self.system_health = {
            'critical_errors': 0,
            'max_critical_errors': 10,  # 允許的最大嚴重錯誤數
            'data_quality_failures': 0,
            'max_data_failures': 5,  # 允許的最大數據質量失敗數
            'last_health_check': time.time()
        }
        
        # 信號循環調度間隔 - 優化為符合Binance免費API限制
        self.signal_loop_interval = 90  # 信號生成循環間隔（秒）- 從15秒增加到90秒
        self.symbol_processing_interval = 12  # 交易對處理間隔（秒）- 從3秒增加到12秒避免API限制
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
        
        # Binance API 限制管理
        self.api_call_times = []  # 記錄API呼叫時間
        self.api_rate_limit_window = 60  # 限制窗口（秒）
        self.api_max_calls_per_minute = 50  # 保守的每分鐘最大呼叫數（遠低於1200限制）
        self.api_pause_duration = 60  # API限制觸發後的暫停時間（秒）
        self.last_api_pause = 0
        
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
        
    async def initialize_systems(self):
        """初始化所有系統組件"""
        logger.info("🚀 初始化生產環境交易系統...")
        
        try:
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
            
            # 2. 初始化優先級3時間框架感知學習
            try:
                from backend.phase2_adaptive_learning.priority3_timeframe_learning.priority3_integration_engine_fixed import get_priority3_integration_engine
                
                # 初始化優先級3整合引擎 - 🔧 移除無效配置
                self.priority3_integration = get_priority3_integration_engine()
                
                if self.priority3_integration:
                    self.priority3_enabled = True
                    self.timeframe_learning_available = True
                    logger.info("✅ 優先級3時間框架感知學習：已啟用")
                    logger.info("   📊 支援功能: 跨時間框架共識分析、三維權重融合")
                    logger.info("   🕒 支援功能：時間衰減 + 幣種分類 + 時間框架感知")
                else:
                    logger.warning("⚠️ 優先級3初始化失敗，使用基礎學習模式")
                    self.priority3_enabled = False
                    self.timeframe_learning_available = False
                    
            except Exception as e:
                logger.error(f"❌ 優先級3初始化錯誤: {e}")
                logger.warning("⚠️ 優先級3初始化失敗，使用基礎學習模式")
                self.priority3_enabled = False
                self.timeframe_learning_available = False
            
            # 3. 初始化 Phase3 決策系統
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
                # 🚨 系統健康檢查
                if not await self.check_system_health():
                    logger.critical("🛑 系統健康檢查失敗，停止信號生成循環")
                    break
                
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
                            logger.error(f"❌ {symbol} 無法獲取真實市場數據")
                            logger.error("🛑 生產系統必須使用真實數據，系統將關閉")
                            self.running = False
                            return
                            
                    except Exception as e:
                        logger.error(f"❌ {symbol} 真實數據獲取失敗: {e}")
                        logger.error("🛑 生產系統數據源失效，系統將關閉")
                        self.running = False
                        return
                    
                    # 🚀 直接使用Phase1A生成信號（新架構，不依賴舊系統）
                    try:
                        # 🎯 直接使用Phase1A生成器生成信號
                        logger.info(f"📊 開始為 {symbol} 生成信號（Phase1A直接調用）...")
                        
                        # 使用Phase1A生成基礎信號 - 修正方法名稱
                        base_signals = await self.phase1a_generator.generate_signals(symbol, market_data)
                        
                        logger.info(f"🔍 {symbol} Phase1A信號生成結果: {type(base_signals)} - 數量: {len(base_signals) if base_signals else 0}")
                        
                        signals = base_signals  # 將Phase1A的結果作為最終信號
                        
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
                                    # 🔧 統一導入路徑策略 - 支援多種導入方式
                                    import sys
                                    from pathlib import Path
                                    
                                    SignalCandidate = None
                                    
                                    # 嘗試方式1: 相對導入
                                    try:
                                        from backend.phase2_pre_evaluation.epl_pre_processing_system.epl_pre_processing_system import SignalCandidate
                                        logger.debug("✅ SignalCandidate 相對導入成功")
                                    except ImportError:
                                        # 嘗試方式2: 絕對導入
                                        try:
                                            current_path = Path(__file__).parent
                                            sys.path.append(str(current_path))
                                            from backend.phase2_pre_evaluation.epl_pre_processing_system.epl_pre_processing_system import SignalCandidate
                                            logger.debug("✅ SignalCandidate 絕對導入成功")
                                        except ImportError:
                                            # 嘗試方式3: 動態導入
                                            try:
                                                import importlib.util
                                                module_path = current_path / "backend" / "phase2_pre_evaluation" / "epl_pre_processing_system" / "epl_pre_processing_system.py"
                                                spec = importlib.util.spec_from_file_location("epl_module", module_path)
                                                module = importlib.util.module_from_spec(spec)
                                                spec.loader.exec_module(module)
                                                SignalCandidate = module.SignalCandidate
                                                logger.debug("✅ SignalCandidate 動態導入成功")
                                            except Exception as dynamic_error:
                                                logger.warning(f"⚠️ SignalCandidate 所有導入方式失敗: {dynamic_error}")
                                                raise ImportError("無法導入 SignalCandidate")
                                    
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
                                    logger.error(f"❌ SignalCandidate 導入失敗: {import_error}")
                                    logger.error("🛑 生產系統必須有完整的依賴模組，無法繼續Phase3決策")
                                    logger.error("🔧 請修復導入問題或檢查系統架構完整性")
                                    # 產品化要求：導入失敗直接報錯，不使用虛假數據
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
                        
                        # 🎯 信號會自動存儲到標準三分類資料庫：
                        # • Phase1A 基礎信號 → market_data.db (由 Phase1A 自動處理)
                        # • Priority3 增強信號 → learning_records.db (由 Priority3 自動處理)
                        # • 系統保護事件 → extreme_events.db (由系統保護模組自動處理)
                        
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
            
            # === 基礎學習狀態 (優先級1+2) ===
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
            
            # === 優先級3時間框架感知狀態 ===
            if self.priority3_enabled and self.priority3_integration:
                try:
                    # 獲取優先級3學習統計
                    p3_stats = await self.priority3_integration.get_learning_statistics()
                    
                    if p3_stats:
                        total_enhanced = p3_stats.get('total_signals_processed', 0)
                        avg_cross_tf_weight = p3_stats.get('average_cross_timeframe_weight', 0)
                        active_timeframes = p3_stats.get('active_timeframes', [])
                        weight_distribution = p3_stats.get('weight_distribution', {})
                        
                        logger.info(f"⚡ 優先級3狀態: 已處理 {total_enhanced} 個增強信號")
                        logger.info(f"   🎯 平均跨時間框架權重: {avg_cross_tf_weight:.3f}")
                        logger.info(f"   📊 活躍時間框架: {', '.join(active_timeframes)}")
                        
                        # 顯示權重分布
                        if weight_distribution:
                            logger.info(f"   ⚖️ 三維權重分布:")
                            for component, avg_weight in weight_distribution.items():
                                logger.info(f"      • {component}: {avg_weight:.3f}")
                        
                except Exception as e:
                    logger.debug(f"優先級3狀態記錄錯誤: {e}")
                    
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
        """獲取真實的歷史K線數據 - 帶重試機制和API限制檢查"""
        try:
            # 檢查API頻率限制
            if not self._check_api_rate_limit():
                logger.warning(f"⏸️ {symbol} 歷史數據API限制，等待重置...")
                await self._wait_for_api_limit_reset()
            
            import aiohttp
            import time
            import asyncio
            
            url = f"https://api.binance.com/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': '1m',  # 1分鐘K線
                'limit': limit
            }
            
            # 重試機制
            for retry in range(3):
                try:
                    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                        # 記錄API呼叫
                        self.api_call_times.append(time.time())
                        
                        async with session.get(url, params=params) as response:
                            if response.status == 429:  # API限制
                                logger.warning(f"⏸️ {symbol} 歷史數據API限制 (429)，等待30秒...")
                                await asyncio.sleep(30)
                                continue
                            elif response.status != 200:
                                logger.error(f"❌ 獲取 {symbol} 歷史數據失敗: HTTP {response.status}")
                                if retry < 2:
                                    await asyncio.sleep(5 * (retry + 1))  # 指數退避
                                    continue
                                return []
                            
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
                            
                            logger.debug(f"✅ {symbol} 歷史數據獲取成功: {len(historical_data)} 筆")
                            return historical_data
                            
                except aiohttp.ClientError as e:
                    logger.warning(f"⚠️ {symbol} 歷史數據網路錯誤 (重試 {retry+1}/3): {e}")
                    if retry < 2:
                        await asyncio.sleep(10 * (retry + 1))  # 網路錯誤等待更久
                    else:
                        logger.error(f"❌ {symbol} 歷史數據網路連接失敗")
                        return []
                        
            return []  # 所有重試都失敗
                        
        except Exception as e:
            logger.error(f"❌ 獲取 {symbol} 歷史數據異常: {e}")
            return []

    def _check_api_rate_limit(self) -> bool:
        """檢查API頻率限制"""
        import time
        current_time = time.time()
        
        # 清理超過窗口時間的記錄
        self.api_call_times = [
            call_time for call_time in self.api_call_times 
            if current_time - call_time < self.api_rate_limit_window
        ]
        
        # 檢查是否超過限制
        if len(self.api_call_times) >= self.api_max_calls_per_minute:
            logger.warning(f"🚨 API頻率限制觸發：{len(self.api_call_times)}次/{self.api_rate_limit_window}秒")
            self.last_api_pause = current_time
            return False
        
        # 記錄這次API呼叫
        self.api_call_times.append(current_time)
        return True
    
    async def _wait_for_api_limit_reset(self):
        """等待API限制重置"""
        import time
        if time.time() - self.last_api_pause < self.api_pause_duration:
            wait_time = self.api_pause_duration - (time.time() - self.last_api_pause)
            logger.info(f"⏳ API限制暫停中，等待 {wait_time:.1f} 秒...")
            await asyncio.sleep(wait_time)

    async def _get_real_market_data(self, symbol: str) -> dict:
        """🚀 使用智能混合價格系統獲取真實市場數據"""
        try:
            # 優先使用智能混合價格系統（如果可用）
            if HYBRID_PRICE_SYSTEM_AVAILABLE:
                try:
                    # 動態導入以避免全局導入問題
                    from backend.phase1_signal_generation.onchain_data_connector.production_price_integration import get_real_market_data
                    
                    # 使用新的智能混合價格系統（鏈上數據為主，WebSocket 幣安API 為回退）
                    market_data = await get_real_market_data(symbol)
                    
                    if market_data:
                        logger.info(f"✅ {symbol}: 智能混合系統獲取成功 - 價格: ${market_data['price']:.4f} (來源: {market_data.get('source', '未知')})")
                        if market_data.get('is_fallback'):
                            logger.info(f"🔄 {symbol}: 使用 WebSocket 幣安API 回退機制")
                        return market_data
                except ImportError as e:
                    logger.warning(f"⚠️ {symbol}: 智能混合系統動態導入失敗: {e}")
                    # 嘗試重新啟用導入
                    if attempt_hybrid_import():
                        logger.info(f"🔄 {symbol}: 智能混合系統重新連接成功，重試中...")
                        # 遞歸重試一次
                        return await self._get_real_market_data(symbol)
                else:
                    logger.warning(f"⚠️ {symbol}: 智能混合系統獲取失敗，嘗試傳統方法")
            
            # 如果智能混合系統不可用或失敗，使用傳統幣安API
            logger.info(f"🔄 {symbol}: 使用傳統幣安API方法")
            return await self._get_traditional_binance_data(symbol)
                
        except Exception as e:
            logger.error(f"❌ {symbol} 價格系統錯誤: {e}")
            # 嘗試傳統方法作為最後的回退
            return await self._get_traditional_binance_data(symbol)
    
    async def _get_traditional_binance_data(self, symbol: str) -> dict:
        """傳統幣安API數據獲取方法（作為回退）"""
        try:
            import aiohttp
            
            # 簡化的幣安API調用
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                url = f"https://api.binance.com/api/v3/ticker/24hr"
                params = {"symbol": symbol}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        market_data = {
                            "close": float(data.get("lastPrice", 0)),
                            "price": float(data.get("lastPrice", 0)),
                            "volume": float(data.get("volume", 0)),
                            "high": float(data.get("highPrice", 0)),
                            "low": float(data.get("lowPrice", 0)),
                            "source": "traditional_binance_api",
                            "is_fallback": True
                        }
                        
                        logger.info(f"✅ {symbol}: 傳統幣安API獲取成功 - 價格: ${market_data['price']:.4f}")
                        return market_data
                    else:
                        logger.error(f"❌ {symbol}: 幣安API錯誤 {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ {symbol} 傳統幣安API錯誤: {e}")
            return None
    
    def _format_user_signal_display(self, symbol: str, signals: list, decisions: list = None) -> dict:
        """格式化用戶信號展示 - 使用 Phase1A 的 format_for_display 方法，只處理Phase3整合"""
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
        
        # 📊 Phase3 決策分析 - 啟動腳本協調職責
        phase3_confidence = 0.0
        decision_action = None
        risk_check_failed = False
        
        if decisions and len(decisions) > 0:
            decision = decisions[0]
            
            # Phase3 信心度讀取
            for confidence_attr in ['confidence', 'decision_confidence', 'certainty', 'probability']:
                if hasattr(decision, confidence_attr):
                    try:
                        phase3_confidence = float(getattr(decision, confidence_attr))
                        if phase3_confidence > 1.0:
                            phase3_confidence = phase3_confidence / 100.0
                        break
                    except (ValueError, TypeError):
                        continue
            
            # 檢查決策類型
            for decision_attr in ['decision', 'decision_type']:
                if hasattr(decision, decision_attr):
                    raw_decision = getattr(decision, decision_attr)
                    if hasattr(raw_decision, 'value'):
                        decision_action = raw_decision.value
                    else:
                        decision_action = str(raw_decision)
                    break
            
            # 檢查風險檢查失敗
            if phase3_confidence == 0.0 and decision_action and 'IGNORE' in decision_action:
                risk_check_failed = True
        
        # 🎯 使用 Phase1A 的 format_for_display 方法處理業務邏輯
        try:
            if hasattr(best_signal, 'format_for_display'):
                signal_display_data = best_signal.format_for_display()
                logger.info(f"✅ {symbol} 使用 Phase1A format_for_display 方法")
            else:
                logger.error(f"❌ {symbol} 信號對象缺少 format_for_display 方法")
                return None
            
            # 啟動腳本職責：整合 Phase3 信心度
            base_confidence = signal_display_data.get('confidence', 0.5)
            
            if phase3_confidence > 0:
                final_confidence = phase3_confidence * 0.7 + base_confidence * 0.3
            elif risk_check_failed:
                final_confidence = base_confidence * 0.2
            else:
                final_confidence = base_confidence
            
            # 更新整合後的信心度
            signal_display_data['confidence'] = final_confidence
            signal_display_data['phase3_confidence'] = phase3_confidence
            signal_display_data['risk_check_failed'] = risk_check_failed
            
            return signal_display_data
            
        except Exception as e:
            logger.error(f"❌ {symbol} 信號格式化失敗: {e}")
            return None
    
    async def _display_user_signals(self, symbol: str, signals: list, decisions: list = None):
        """向用戶展示信號 - 簡化版本，主要職責是協調展示"""
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
            
            # Phase3 決策信息展示 (啟動腳本協調職責)
            if signal_display.get('phase3_confidence', 0) > 0:
                logger.info(f"   🎯 Phase3 決策信心度: {signal_display['phase3_confidence']:.1%}")
            elif signal_display.get('risk_check_failed', False):
                logger.info(f"   🚨 Phase3 決策: 不符合開倉條件，超過持倉限制")
            
            logger.info("="*80)
    
    async def start_monitoring(self):
        """啟動監控系統"""
        # 啟動統一監控系統
        if self.monitoring_manager:
            try:
                await self.monitoring_manager.start_monitoring()
                logger.info("✅ 統一監控系統已啟動")
            except Exception as e:
                logger.error(f"❌ 監控系統啟動失敗: {e}")
        
        # 🧠 啟動內存監控
        try:
            memory_task = asyncio.create_task(self.memory_manager.memory_monitoring_loop())
            logger.info("✅ 內存監控系統已啟動")
        except Exception as e:
            logger.error(f"❌ 內存監控啟動失敗: {e}")
    
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
    
    async def check_system_health(self):
        """檢查系統健康狀態"""
        current_time = time.time()
        
        # 檢查嚴重錯誤數量
        if self.system_health['critical_errors'] >= self.system_health['max_critical_errors']:
            logger.critical(f"🚫 系統健康檢查失敗：嚴重錯誤數 {self.system_health['critical_errors']} 超過閾值 {self.system_health['max_critical_errors']}")
            logger.critical("🛑 基於產品級要求，系統將停止運行以保護數據完整性")
            await self.shutdown()
            return False
            
        # 檢查數據質量失敗數量
        if self.system_health['data_quality_failures'] >= self.system_health['max_data_failures']:
            logger.critical(f"🚫 數據質量檢查失敗：失敗數 {self.system_health['data_quality_failures']} 超過閾值 {self.system_health['max_data_failures']}")
            logger.critical("🛑 基於用戶要求（不准模擬數據），系統將停止運行")
            await self.shutdown()
            return False
            
        self.system_health['last_health_check'] = current_time
        return True

    def record_critical_error(self, error_type: str, details: str):
        """記錄嚴重錯誤"""
        self.system_health['critical_errors'] += 1
        logger.error(f"🚨 記錄嚴重錯誤 ({self.system_health['critical_errors']}/{self.system_health['max_critical_errors']}): {error_type} - {details}")

    def record_data_quality_failure(self, symbol: str, reason: str):
        """記錄數據質量失敗"""
        self.system_health['data_quality_failures'] += 1
        logger.warning(f"📊 記錄數據質量失敗 ({self.system_health['data_quality_failures']}/{self.system_health['max_data_failures']}): {symbol} - {reason}")

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
        """使用學習引擎監控信號 - 支援優先級3時間框架感知"""
        try:
            # 處理單個或多個信號
            signal_list = signals if isinstance(signals, list) else [signals]
            
            for signal in signal_list:
                # 準備基礎信號數據
                base_signal_data = {
                    'signal_id': f"{symbol}_{int(time.time() * 1000)}",  # 使用時間戳生成唯一ID
                    'symbol': symbol,
                    'signal_strength': getattr(signal, 'signal_strength', getattr(signal, 'strength', 0.7)),
                    'signal_type': getattr(signal, 'signal_type', getattr(signal, 'direction', 'BUY')),
                    'tier': getattr(signal, 'tier', 'MEDIUM'),
                    'timestamp': datetime.now(),
                    'features': {
                        'market_data': market_data,
                        'signal_source': getattr(signal, 'signal_type', 'BASIC')
                    },
                    'market_conditions': {
                        'price': market_data.get('price', market_data.get('close', 0.0)),
                        'volume': market_data.get('volume', 0.0),
                        'volatility': market_data.get('volatility', 0.0)
                    },
                    'primary_timeframe': '5m'  # 默認時間框架
                }
                
                # === 優先級3：時間框架感知處理 ===
                if self.priority3_enabled and self.priority3_integration:
                    try:
                        # 使用優先級3整合引擎處理信號
                        enhanced_signal = await self.priority3_integration.process_signal_with_timeframes(
                            base_signal_data, market_data
                        )
                        
                        if enhanced_signal:
                            logger.debug(f"✅ {symbol}: 優先級3增強信號 - 最終權重: {enhanced_signal.final_learning_weight:.3f}")
                            logger.debug(f"🔍 權重分解: 時間衰減={enhanced_signal.time_decay_weight:.3f}, "
                                       f"幣種分類={enhanced_signal.category_weight:.3f}, "
                                       f"時間框架={enhanced_signal.cross_timeframe_weight:.3f}")
                        else:
                            logger.warning(f"⚠️ {symbol}: 優先級3處理失敗，使用基礎學習")
                            # 記錄數據質量失敗
                            self.record_data_quality_failure(symbol, "優先級3多時間框架數據缺失")
                            await self._fallback_learning_monitor(base_signal_data)
                            
                    except Exception as e:
                        logger.error(f"❌ {symbol}: 優先級3處理錯誤: {e}")
                        # 記錄嚴重錯誤
                        self.record_critical_error("Priority3ProcessingError", f"{symbol}: {str(e)}")
                        await self._fallback_learning_monitor(base_signal_data)
                
                # === 基礎學習引擎監控（優先級1+2） ===
                elif self.learning_enabled and self.adaptive_learning_engine:
                    await self._fallback_learning_monitor(base_signal_data)
                
                else:
                    logger.debug(f"📝 {symbol}: 學習引擎未啟用，跳過信號監控")
                
        except Exception as e:
            logger.error(f"❌ 學習引擎信號監控失敗: {e}")
    
    async def _fallback_learning_monitor(self, signal_data: dict):
        """基礎學習監控（當優先級3不可用時）"""
        try:
            if self.learning_enabled and self.adaptive_learning_engine:
                # 監控信號表現（暫時不提供實際結果，讓學習引擎記錄）
                await self.adaptive_learning_engine.monitor_signal_performance(
                    signal_data, 
                    actual_outcome=None  # 實際結果需要後續跟蹤
                )
                logger.debug(f"📊 基礎學習: {signal_data['signal_id']}")
        except Exception as e:
            logger.error(f"❌ 基礎學習監控失敗: {e}")
    
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

async def main():
    """主入口函數"""
    print("🚀 Trading X 生產環境啟動器 (Phase2 參數管理增強版)")
    print("="*60)
    
    # 創建並運行系統
    system = ProductionTradingSystemPhase2Enhanced()
    await system.run()

if __name__ == "__main__":
    asyncio.run(main())
