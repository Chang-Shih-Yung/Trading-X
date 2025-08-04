#!/usr/bin/env python3
"""
狙擊手策略API整理分析工具
分析 信號生成 > 篩選 > 呈現 > 過期 > 歷史記錄 流程中使用的API
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Set
import json

class SniperAPIAnalyzer:
    def __init__(self):
        self.api_endpoints = {}
        self.frontend_usage = {}
        self.workflow_apis = {
            '信號生成': [],
            '信號篩選': [],
            '前端呈現': [],
            '過期處理': [],
            '歷史記錄': []
        }
        
    def extract_api_endpoints(self, file_path: str) -> List[Dict]:
        """從API文件中提取端點"""
        endpoints = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 匹配 @router.{method}("path") 格式
            pattern = r'@router\.(get|post|put|delete|patch)\("([^"]+)"\)'
            matches = re.findall(pattern, content)
            
            for method, path in matches:
                # 查找函數名和描述
                func_pattern = rf'@router\.{method}\("{re.escape(path)}"\)[^d]*def\s+(\w+)'
                func_match = re.search(func_pattern, content)
                func_name = func_match.group(1) if func_match else "unknown"
                
                # 查找文檔字符串
                doc_pattern = rf'def\s+{func_name}[^:]*:\s*"""([^"]+)"""'
                doc_match = re.search(doc_pattern, content)
                description = doc_match.group(1).strip() if doc_match else ""
                
                endpoints.append({
                    'file': os.path.basename(file_path),
                    'method': method.upper(),
                    'path': path,
                    'function': func_name,
                    'description': description
                })
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            
        return endpoints
    
    def extract_frontend_usage(self, file_path: str) -> List[Dict]:
        """從前端文件中提取API使用"""
        usages = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 匹配各種API調用格式
            patterns = [
                r"(?:fetch|axios\.(?:get|post|put|delete))\s*\(\s*['\"]([^'\"]*api/v1/[^'\"]*)['\"]",
                r"const\s+\w+\s*=\s*['\"]([^'\"]*api/v1/[^'\"]*)['\"]",
                r"websocket.*?['\"]([^'\"]*api/v1/[^'\"]*)['\"]"
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    usages.append({
                        'file': os.path.basename(file_path),
                        'api_path': match
                    })
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            
        return usages
    
    def categorize_workflow_apis(self):
        """將API分類到狙擊手工作流程中"""
        
        # 信號生成相關
        generation_keywords = [
            'sniper-unified-data-layer', 'pandas-ta-direct', 'signals',
            'phase1a-signal-scoring', 'phase1b-enhanced-signal-scoring', 
            'phase1c-enhanced-signal-scoring', 'create-market-event'
        ]
        
        # 信號篩選相關
        filtering_keywords = [
            'dashboard-precision-signals', 'precision-signal', 'precision-signal-stats',
            'signal-health-dashboard', 'multi-timeframe-weights'
        ]
        
        # 前端呈現相關
        presentation_keywords = [
            'dashboard-precision-signals', 'realtime-sync-status', 'performance-metrics',
            'ws', 'websocket'
        ]
        
        # 過期處理相關
        expiration_keywords = [
            'process-expired', 'cleanup-expired', 'expired', 'process-dynamic-expiration',
            'expiration-scheduler-status', 'manual-expiration-trigger'
        ]
        
        # 歷史記錄相關
        history_keywords = [
            'history/signals', 'history/performance', 'history/daily-summary',
            'history/statistics', 'history/cleanup'
        ]
        
        # 分類API
        for file, endpoints in self.api_endpoints.items():
            for endpoint in endpoints:
                path = endpoint['path']
                
                # 檢查各個分類
                if any(keyword in path for keyword in generation_keywords):
                    self.workflow_apis['信號生成'].append(endpoint)
                
                if any(keyword in path for keyword in filtering_keywords):
                    self.workflow_apis['信號篩選'].append(endpoint)
                
                if any(keyword in path for keyword in presentation_keywords):
                    self.workflow_apis['前端呈現'].append(endpoint)
                
                if any(keyword in path for keyword in expiration_keywords):
                    self.workflow_apis['過期處理'].append(endpoint)
                
                if any(keyword in path for keyword in history_keywords):
                    self.workflow_apis['歷史記錄'].append(endpoint)
    
    def find_unused_apis(self) -> List[Dict]:
        """找出未使用的API"""
        unused = []
        
        # 收集所有前端使用的API路徑
        used_paths = set()
        for file, usages in self.frontend_usage.items():
            for usage in usages:
                # 清理路徑，移除查詢參數
                clean_path = usage['api_path'].split('?')[0]
                used_paths.add(clean_path)
        
        # 檢查每個API是否被使用
        for file, endpoints in self.api_endpoints.items():
            for endpoint in endpoints:
                api_path = f"/api/v1{endpoint['path']}"
                
                # 檢查是否有匹配的使用
                is_used = False
                for used_path in used_paths:
                    if api_path in used_path or used_path in api_path:
                        is_used = True
                        break
                
                if not is_used:
                    unused.append({
                        **endpoint,
                        'full_path': api_path
                    })
        
        return unused
    
    def analyze(self):
        """執行完整分析"""
        print("🔍 狙擊手策略API整理分析")
        print("=" * 80)
        
        # 分析API端點
        api_files = [
            'app/api/v1/endpoints/scalping_precision.py',
            'app/api/v1/endpoints/sniper_signal_history.py',
            'app/api/v1/endpoints/sniper_smart_layer.py',
            'app/api/v1/endpoints/sniper_email.py',
            'app/api/v1/endpoints/sniper_backtest.py',
            'app/api/v1/endpoints/realtime_market.py',
            'app/api/v1/endpoints/market_analysis.py'
        ]
        
        for file_path in api_files:
            if os.path.exists(file_path):
                endpoints = self.extract_api_endpoints(file_path)
                if endpoints:
                    self.api_endpoints[os.path.basename(file_path)] = endpoints
        
        # 分析前端使用
        frontend_files = [
            'frontend/src/views/TradingStrategySniperIntegrated.vue',
            'frontend/src/views/TradingStrategy.vue',
            'frontend/src/views/Market_New.vue',
            'frontend/src/views/Strategies.vue',
            'frontend/src/views/ShortTermHistory.vue',
            'frontend/src/views/Backtest.vue'
        ]
        
        for file_path in frontend_files:
            if os.path.exists(file_path):
                usages = self.extract_frontend_usage(file_path)
                if usages:
                    self.frontend_usage[os.path.basename(file_path)] = usages
        
        # 分類工作流程API
        self.categorize_workflow_apis()
        
        # 生成報告
        self.generate_report()
    
    def generate_report(self):
        """生成整理報告"""
        print("\\n📊 狙擊手工作流程 API 分類:")
        print("-" * 80)
        
        for workflow, apis in self.workflow_apis.items():
            print(f"\\n🎯 {workflow} ({len(apis)} 個API):")
            for api in apis:
                status = "✅ 核心" if workflow in ['信號篩選', '前端呈現'] else "⚠️ 檢查"
                print(f"  {status} {api['method']} {api['path']} - {api['description'][:50]}...")
        
        print("\\n" + "=" * 80)
        print("📈 前端API使用統計:")
        print("-" * 80)
        
        total_usage = 0
        for file, usages in self.frontend_usage.items():
            print(f"\\n📄 {file}: {len(usages)} 個API調用")
            total_usage += len(usages)
            for usage in usages[:5]:  # 只顯示前5個
                print(f"  - {usage['api_path']}")
            if len(usages) > 5:
                print(f"  ... 和其他 {len(usages) - 5} 個")
        
        print(f"\\n📊 總API使用量: {total_usage}")
        
        # 找出未使用的API
        unused = self.find_unused_apis()
        print(f"\\n⚠️ 可能未使用的API ({len(unused)} 個):")
        print("-" * 80)
        
        for api in unused[:20]:  # 只顯示前20個
            print(f"❌ {api['method']} {api['full_path']}")
            print(f"   描述: {api['description'][:60]}...")
            print(f"   文件: {api['file']}")
            print()
        
        if len(unused) > 20:
            print(f"... 和其他 {len(unused) - 20} 個未使用的API")
        
        # 生成清理建議
        self.generate_cleanup_suggestions(unused)
    
    def generate_cleanup_suggestions(self, unused_apis: List[Dict]):
        """生成清理建議"""
        print("\\n🧹 API清理建議:")
        print("=" * 80)
        
        # 按文件分組
        by_file = {}
        for api in unused_apis:
            file = api['file']
            if file not in by_file:
                by_file[file] = []
            by_file[file].append(api)
        
        for file, apis in by_file.items():
            print(f"\\n📄 {file} - 建議移除 {len(apis)} 個端點:")
            
            # 分析移除的安全性
            safe_to_remove = []
            need_review = []
            
            for api in apis:
                path = api['path']
                # 判斷是否為測試、調試或實驗性API
                if any(keyword in path.lower() for keyword in 
                      ['test', 'debug', 'experimental', 'temp', 'old', 'legacy']):
                    safe_to_remove.append(api)
                else:
                    need_review.append(api)
            
            if safe_to_remove:
                print("  ✅ 安全移除:")
                for api in safe_to_remove:
                    print(f"    - {api['method']} {api['path']}")
            
            if need_review:
                print("  ⚠️ 需要檢查:")
                for api in need_review:
                    print(f"    - {api['method']} {api['path']}")

if __name__ == "__main__":
    analyzer = SniperAPIAnalyzer()
    analyzer.analyze()
