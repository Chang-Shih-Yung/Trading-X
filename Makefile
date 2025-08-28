.PHONY: setup install run test clean docker-build docker-run lint format help verify quick-setup quantum-test

# 函數：檢測 Python 命令
PYTHON_CMD := $(shell \
	if command -v python3 >/dev/null 2>&1; then \
		echo "python3"; \
	elif command -v python >/dev/null 2>&1 && python --version 2>&1 | grep -q "Python 3"; then \
		echo "python"; \
	else \
		echo "python3"; \
	fi)

# 🚀 一鍵快速設置（推薦）
quick-setup:
	@echo "🚀 Trading X 一鍵環境配置..."
ifeq ($(OS),Windows_NT)
	@echo "🪟 檢測到 Windows 系統"
	setup-windows.bat
else
	chmod +x quick-setup.sh
	./quick-setup.sh
endif

# 🔧 完整設置開發環境（進階）
setup:
	@echo "� 設置 Trading X 完整開發環境..."
	@echo "🐍 檢測到 Python 命令: $(PYTHON_CMD)"
	chmod +x setup-dev-environment.sh
	chmod +x verify-cross-device.sh
	./setup-dev-environment.sh

# 🔍 驗證跨設備環境
verify:
	@echo "🔍 驗證跨設備環境配置..."
	./verify-cross-device.sh

# 🌐 跨平台環境檢查
check-env:
	@echo "🌐 跨平台環境檢查..."
	chmod +x check-environment.sh
	./check-environment.sh

# ⚛️ 測試量子系統
quantum-test:
	@echo "⚛️ 測試量子交易系統..."
	cd quantum_pro && $(PYTHON_CMD) btc_quantum_ultimate_model.py --demo

# 📦 僅安裝依賴（支援跨設備）
install:
	@echo "📦 安裝依賴..."
	@echo "🐍 使用 Python 命令: $(PYTHON_CMD)"
	$(PYTHON_CMD) -m pip install --upgrade pip
	$(PYTHON_CMD) -m pip install -r requirements.txt
	@bash -c "source venv/bin/activate && pip install -r requirements.txt"
	@echo "🌌 驗證量子模組..."
	@bash -c "source venv/bin/activate && python -c 'import qiskit; from qiskit_aer import Aer; print(\"✅ 量子模組安裝成功\")'"

# ▶️ 運行主系統（統一虛擬環境路徑）
run:
	@echo "▶️ 啟動 Trading X 系統..."
	@if [ ! -d "venv" ]; then echo "❌ 虛擬環境不存在，請先執行 make setup"; exit 1; fi
	@bash -c "source venv/bin/activate && python X/production_launcher_phase2_enhanced.py"

# 🔮 檢查量子環境
check-quantum:
	@echo "🔮 檢查量子計算環境..."
	@if [ ! -d "venv" ]; then echo "❌ 虛擬環境不存在，請先執行 make setup"; exit 1; fi
	@bash -c "source venv/bin/activate && python quantum_pro/check_quantum_environment.py"

# 🌌 運行量子自適應系統 (推薦)
run-quantum:
	@echo "🌌 啟動量子自適應交易系統..."
	@if [ ! -d "venv" ]; then echo "❌ 虛擬環境不存在，請先執行 make setup"; exit 1; fi
	@echo "🔍 執行量子環境預檢..."
	@bash -c "source venv/bin/activate && python quantum_pro/check_quantum_environment.py"
	@echo "🚀 啟動量子自適應引擎..."
	@bash -c "source venv/bin/activate && cd quantum_pro/launcher && ./一鍵啟動_量子自適應.sh"

# 🎯 僅運行量子模型訓練
train-quantum:
	@echo "🎯 運行量子模型訓練..."
	@if [ ! -d "venv" ]; then echo "❌ 虛擬環境不存在，請先執行 make setup"; exit 1; fi
	@bash -c "source venv/bin/activate && cd quantum_pro/launcher && python quantum_model_trainer.py"

# 🔮 量子模組測試
test-quantum:
	@echo "🔮 測試量子模組..."
	@if [ ! -d "venv" ]; then echo "❌ 虛擬環境不存在，請先執行 make setup"; exit 1; fi
	@bash -c "source venv/bin/activate && python quantum_pro/check_quantum_environment.py && echo '✅ 量子環境測試通過'"

# 🧪 運行測試
test:
	@echo "🧪 運行測試..."
	@bash -c "source venv/bin/activate && pytest tests/ -v"

# 📊 運行測試覆蓋率
test-cov:
	@echo "📊 運行測試覆蓋率..."
	@bash -c "source venv/bin/activate && pytest tests/ --cov=. --cov-report=html"

# 🔍 代碼檢查
lint:
	@echo "🔍 代碼檢查..."
	@bash -c "source venv/bin/activate && flake8 . --max-line-length=88 --exclude=venv"
	@bash -c "source venv/bin/activate && mypy . --exclude=venv"

# 🎨 代碼格式化
format:
	@echo "🎨 代碼格式化..."
	@bash -c "source venv/bin/activate && black . --exclude=venv"
	@bash -c "source venv/bin/activate && isort . --skip=venv"

# 🧹 清理環境
clean:
	@echo "🧹 清理環境..."
	rm -rf venv
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .mypy_cache
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

# 🐳 Docker 操作
docker-build:
	@echo "🐳 構建 Docker 映像..."
	docker build -t trading-x:latest .

docker-run:
	@echo "🐳 運行 Docker 容器..."
	docker-compose up -d

docker-stop:
	@echo "🐳 停止 Docker 容器..."
	docker-compose down

docker-logs:
	@echo "🐳 查看 Docker 日誌..."
	docker-compose logs -f

# 📋 顯示幫助
help:
	@echo "Trading X 開發指令 (跨設備兼容):"
	@echo "  make setup       - 設置開發環境 (自動檢測 python/python3)"
	@echo "  make verify      - 驗證跨設備環境配置"
	@echo "  make install     - 安裝依賴"
	@echo "  make run         - 運行主系統"
	@echo ""
	@echo "🔮 量子計算相關："
	@echo "  make check-quantum - 檢查量子環境完整性"
	@echo "  make run-quantum   - 運行量子自適應系統 (推薦)"
	@echo "  make train-quantum - 僅運行量子模型訓練"
	@echo "  make test-quantum  - 測試量子模組"
	@echo ""
	@echo "🛠️ 開發工具："
	@echo "  make test        - 運行測試"
	@echo "  make lint        - 代碼檢查"
	@echo "  make format      - 代碼格式化"
	@echo "  make clean       - 清理環境"
	@echo "  make docker-*    - Docker 相關操作"
	@echo ""
	@echo "🔧 跨設備使用流程："
	@echo "  1. 初次設置: make setup"
	@echo "  2. 驗證配置: make verify"
	@echo "  3. 檢查量子環境: make check-quantum"
	@echo "  4. 運行量子系統: make run-quantum"
	@echo ""
	@echo "⚡ 換電腦快速啟動："
	@echo "  1. make setup (自動檢測並安裝所有依賴)"
	@echo "  2. make run-quantum (自動檢測模型並啟動)"
