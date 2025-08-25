"""
X 系統量子交易模組

此模組包含量子交易引擎的所有核心組件：
- 量子精密交易引擎 (QuantumPrecisionTradingEngine)
- 量子相位數據整合器 (QuantumPhaseDataIntegrator)
- 簡化量子交易引擎 (SimpleQuantumEngine)
- 量子啟動器 (QuantumLauncher)

使用方式：
from X.quantum.simple_quantum_trading_engine import SimpleQuantumEngine
"""

__version__ = "1.0.0"
__author__ = "Trading X Quantum Team"

# 量子核心組件導入
try:
    from .simple_quantum_trading_engine import SimpleQuantumEngine
    SIMPLE_QUANTUM_AVAILABLE = True
except ImportError:
    SIMPLE_QUANTUM_AVAILABLE = False

try:
    from .quantum_precision_trading_engine import QuantumTradingCoordinator
    PRECISION_QUANTUM_AVAILABLE = True
except ImportError:
    PRECISION_QUANTUM_AVAILABLE = False

try:
    from .quantum_phase_data_integrator import get_quantum_phase_coordinator
    PHASE_INTEGRATOR_AVAILABLE = True
except ImportError as e:
    PHASE_INTEGRATOR_AVAILABLE = False
    print(f"量子相位整合器不可用: {e}")

__all__ = []
if SIMPLE_QUANTUM_AVAILABLE:
    __all__.append("SimpleQuantumEngine")
if PRECISION_QUANTUM_AVAILABLE:
    __all__.append("QuantumTradingCoordinator")
if PHASE_INTEGRATOR_AVAILABLE:
    __all__.append("get_quantum_phase_coordinator")
