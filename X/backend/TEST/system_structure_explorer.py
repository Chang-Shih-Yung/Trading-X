#!/usr/bin/env python3
"""
🔍 Trading-X 系統結構探測器
檢查各 Phase 系統的實際可用方法和類別
"""

import sys
import os
import importlib.util
import inspect
from pathlib import Path

# 添加系統路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def explore_module(module_path, module_name):
    """探測模組結構"""
    print(f"\n🔍 探測模組: {module_name}")
    print("=" * 60)
    
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 獲取所有公開的屬性
        for name in dir(module):
            if not name.startswith('_'):
                attr = getattr(module, name)
                
                if inspect.isclass(attr):
                    print(f"📦 類別: {name}")
                    # 列出類別方法
                    for method_name in dir(attr):
                        if not method_name.startswith('_'):
                            method = getattr(attr, method_name)
                            if callable(method):
                                print(f"  ┗ 方法: {method_name}")
                
                elif inspect.isfunction(attr):
                    print(f"🔧 函數: {name}")
                    try:
                        sig = inspect.signature(attr)
                        print(f"  ┗ 簽名: {name}{sig}")
                    except:
                        pass
                
                elif inspect.ismodule(attr):
                    print(f"📁 子模組: {name}")
        
    except Exception as e:
        print(f"❌ 無法探測 {module_name}: {e}")

def main():
    """主函數"""
    backend_path = Path(__file__).parent.parent
    
    # 探測各 Phase 系統
    phase_systems = [
        {
            "path": backend_path / "phase1_signal_generation" / "phase1_main_coordinator.py",
            "name": "Phase1 主協調器"
        },
        {
            "path": backend_path / "phase3_execution_policy" / "epl_intelligent_decision_engine.py", 
            "name": "Phase3 EPL 決策引擎"
        }
    ]
    
    print("🚀 Trading-X 系統結構探測開始")
    print("=" * 80)
    
    for system in phase_systems:
        if system["path"].exists():
            explore_module(system["path"], system["name"])
        else:
            print(f"❌ 找不到檔案: {system['path']}")
    
    print("\n" + "=" * 80)
    print("🎯 探測完成")

if __name__ == "__main__":
    main()
