#!/usr/bin/env python3
"""
Trading X 測試統計腳本
顯示所有可用的測試腳本和使用說明
"""

import os
from pathlib import Path

def get_test_files():
    """獲取所有測試文件信息"""
    test_dir = Path("TEST")
    
    backend_tests = []
    frontend_tests = []
    config_tests = []
    main_tests = []
    
    # 後端測試
    backend_dir = test_dir / "backend"
    if backend_dir.exists():
        for file in backend_dir.glob("*.py"):
            backend_tests.append(file.name)
    
    # 前端測試
    frontend_dir = test_dir / "frontend"
    if frontend_dir.exists():
        for file in frontend_dir.glob("*.js"):
            frontend_tests.append(file.name)
    
    # 配置測試
    config_dir = test_dir / "config"
    if config_dir.exists():
        for file in config_dir.glob("*.py"):
            config_tests.append(file.name)
    
    # 主要測試腳本
    for file in test_dir.glob("*.py"):
        if file.is_file():
            main_tests.append(file.name)
    
    return {
        "backend": sorted(backend_tests),
        "frontend": sorted(frontend_tests),
        "config": sorted(config_tests),
        "main": sorted(main_tests)
    }

def get_file_description(filename):
    """獲取文件描述"""
    descriptions = {
        # 後端測試
        "test_precision_signal.py": "精準信號時間顯示和過期機制測試",
        "test_real_price.py": "實時價格數據獲取測試",
        "test_timeframe_integration.py": "時間框架整合測試",
        "test_trading_system.py": "交易系統整體測試",
        "verify_signals.py": "信號驗證腳本",
        
        # 前端測試
        "test_frontend_display.js": "前端顯示功能測試",
        "test_time_format.js": "時間格式測試",
        
        # 配置測試
        "test_config.py": "配置文件測試",
        
        # 主要測試
        "quick_test.py": "快速功能測試 - 核心API檢查",
        "run_all_tests.py": "完整測試套件 - 運行所有後端測試"
    }
    return descriptions.get(filename, "測試腳本")

def print_section(title, tests, prefix=""):
    """打印測試部分"""
    if not tests:
        return
    
    print(f"\n📁 {title}")
    print("-" * 50)
    
    for i, test in enumerate(tests, 1):
        description = get_file_description(test)
        print(f"{i:2d}. {test}")
        print(f"    📝 {description}")
        if prefix:
            print(f"    🚀 運行: python {prefix}/{test}")
        else:
            print(f"    🚀 運行: python TEST/{test}")

def show_usage_examples():
    """顯示使用示例"""
    print("\n" + "="*60)
    print("📚 使用示例")
    print("="*60)
    
    examples = [
        ("快速檢查系統狀態", "python TEST/quick_test.py"),
        ("運行完整測試套件", "python TEST/run_all_tests.py"),
        ("測試精準信號功能", "python TEST/backend/test_precision_signal.py"),
        ("驗證實時價格數據", "python TEST/backend/test_real_price.py"),
        ("檢查配置文件", "python TEST/config/test_config.py"),
        ("前端時間格式測試", "node TEST/frontend/test_time_format.js"),
        ("前端顯示測試", "node TEST/frontend/test_frontend_display.js")
    ]
    
    for i, (desc, cmd) in enumerate(examples, 1):
        print(f"\n{i}. {desc}:")
        print(f"   {cmd}")

def check_requirements():
    """檢查測試要求"""
    print("\n" + "="*60)
    print("⚠️  測試前置要求")
    print("="*60)
    
    requirements = [
        "🔧 確保後端服務已啟動: uvicorn main:app --reload --host 0.0.0.0 --port 8000",
        "📦 安裝所需的Python包: pip install -r requirements.txt",
        "🌐 確保網絡連接正常（用於獲取市場數據）",
        "📊 檢查數據庫文件存在: tradingx.db",
        "🎯 前端測試需要Node.js環境"
    ]
    
    for req in requirements:
        print(f"  • {req}")

def main():
    """主函數"""
    print("🧪 Trading X 測試統計")
    print("="*60)
    print("📅 測試腳本整理完成")
    print("📍 所有測試腳本已移動到 TEST/ 資料夾")
    
    # 獲取測試文件
    tests = get_test_files()
    
    # 顯示各類測試
    print_section("後端測試腳本", tests["backend"], "TEST/backend")
    print_section("前端測試腳本", tests["frontend"], "TEST/frontend") 
    print_section("配置測試腳本", tests["config"], "TEST/config")
    print_section("主要測試腳本", tests["main"])
    
    # 統計信息
    total_tests = sum(len(tests[key]) for key in tests)
    print(f"\n📊 統計信息:")
    print(f"   • 總測試腳本數量: {total_tests}")
    print(f"   • 後端測試: {len(tests['backend'])}")
    print(f"   • 前端測試: {len(tests['frontend'])}")
    print(f"   • 配置測試: {len(tests['config'])}")
    print(f"   • 主要測試: {len(tests['main'])}")
    
    # 使用示例
    show_usage_examples()
    
    # 前置要求
    check_requirements()
    
    print(f"\n{'='*60}")
    print("✅ 測試腳本整理完成！")
    print("💡 建議先運行 'python TEST/quick_test.py' 進行快速檢查")
    print("="*60)

if __name__ == "__main__":
    main()
