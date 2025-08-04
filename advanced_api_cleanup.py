#!/usr/bin/env python3
"""
第二階段API清理 - 移除複雜事件系統和重複功能API
"""

import os
import re
import shutil
from datetime import datetime

class AdvancedAPICleanup:
    def __init__(self):
        # 第二階段清理 - 複雜功能和重複API
        self.phase2_remove_endpoints = [
            # 複雜事件系統 (前端未使用)
            'create-market-event',
            'event-multipliers',
            'execute-reallocation',
            'reallocation-status',
            'execute-timeframe-switch',
            'timeframe-status',
            'start-monitoring',
            'stop-monitoring',
            'event-predictions',
            'validate-predictions',
            'process-composite-events',
            'event-relations',
            'advanced-event-status',
            'assess-event-impact',
            'impact-assessment',
            'recent-impact-assessments',
            'asset-sensitivity-analysis',
            'impact-assessment-summary',
            
            # Phase 詳細分析API (前端未直接使用)
            'phase1a-signal-scoring',
            'phase1a-templates-overview',
            'phase1b-enhanced-signal-scoring',
            'phase1b-volatility-metrics',
            'phase1b-signal-continuity',
            'phase1ab-integration-status',
            'phase1c-enhanced-signal-scoring',
            'phase1c-standardization-metrics',
            'phase1c-extreme-signals',
            
            # 重複的過期處理API
            'force-precision-refresh',
            'process-expired',
            'cleanup-expired',
            'process-dynamic-expiration',
            'expiration-scheduler-status',
            'manual-expiration-trigger',
            
            # 低優先級監控API
            'precision-signal-stats',
            'signal-health-dashboard',
            'multi-timeframe-weights',
            'realtime-sync-status',
            'performance-metrics',
        ]
        
        # 需要檢查的文件
        self.target_files = [
            'app/api/v1/endpoints/scalping_precision.py'
        ]
    
    def remove_endpoint_from_file(self, file_path: str, endpoint: str):
        """從文件中移除特定端點"""
        if not os.path.exists(file_path):
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更精確的匹配 - 匹配完整的函數定義
        escaped_endpoint = re.escape(endpoint)
        
        # 匹配從 @router 裝飾器到下一個 @router 或文件結尾的完整函數
        pattern = rf'@router\.(get|post|put|delete)\(["\'][^"\']*{escaped_endpoint}[^"\']*["\']\).*?(?=@router\.|$)'
        
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, '', content, flags=re.DOTALL)
            
            # 清理多餘空行
            content = re.sub(r'\n{4,}', '\n\n\n', content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✅ 移除: {endpoint}")
            return True
        
        return False
    
    def clean_phase2_apis(self):
        """執行第二階段API清理"""
        print("🧹 第二階段API清理 - 移除複雜功能和重複API")
        print("=" * 70)
        
        total_removed = 0
        
        for file_path in self.target_files:
            if not os.path.exists(file_path):
                continue
                
            print(f"\n📄 處理文件: {file_path}")
            
            for endpoint in self.phase2_remove_endpoints:
                if self.remove_endpoint_from_file(file_path, endpoint):
                    total_removed += 1
        
        print(f"\n✅ 第二階段清理完成！移除 {total_removed} 個端點")
        
        # 統計剩餘端點
        self.count_remaining_endpoints()
    
    def count_remaining_endpoints(self):
        """統計剩餘端點"""
        print("\n📊 清理後剩餘端點:")
        
        for file_path in self.target_files:
            if not os.path.exists(file_path):
                continue
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 計算剩餘端點
            routes = re.findall(r'@router\.(get|post|put|delete)\(["\']([^"\']+)["\']', content)
            
            print(f"\n📄 {os.path.basename(file_path)}: {len(routes)} 個端點")
            
            # 按重要性分類顯示
            core_apis = []
            other_apis = []
            
            core_keywords = ['dashboard-precision-signals', 'sniper-unified-data-layer', 
                           'pandas-ta-direct', 'signals', 'expired', 'dynamic-parameters',
                           'phase1abc-integration-status', 'phase3-market-depth']
            
            for method, path in routes:
                if any(keyword in path for keyword in core_keywords):
                    core_apis.append(f"{method.upper()} {path}")
                else:
                    other_apis.append(f"{method.upper()} {path}")
            
            if core_apis:
                print("  ✅ 核心API:")
                for api in core_apis:
                    print(f"    {api}")
            
            if other_apis:
                print("  ⚠️ 其他API:")
                for api in other_apis[:5]:  # 只顯示前5個
                    print(f"    {api}")
                if len(other_apis) > 5:
                    print(f"    ... 和其他 {len(other_apis) - 5} 個")

if __name__ == "__main__":
    cleaner = AdvancedAPICleanup()
    
    print("⚠️ 這將移除複雜事件系統和重複功能的API端點")
    print("這些端點前端未使用，但可能影響某些內部功能")
    print("確認執行清理嗎？(y/N): ", end="")
    
    response = input().lower().strip()
    if response in ['y', 'yes']:
        cleaner.clean_phase2_apis()
        
        print("\n📋 建議:")
        print("1. 重啟後端服務")
        print("2. 測試前端狙擊手功能")
        print("3. 檢查信號生成是否正常")
        print("4. 如有問題可從備份恢復")
    else:
        print("❌ 已取消清理操作")
