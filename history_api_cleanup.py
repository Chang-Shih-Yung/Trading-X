#!/usr/bin/env python3
"""
第三階段API清理 - 清理歷史管理中的重複端點
"""

import os
import re

class HistoryAPICleanup:
    def __init__(self):
        # 歷史管理中的重複端點
        self.history_remove_endpoints = [
            'history/performance',      # 重複統計功能
            'history/daily-summary',    # 重複統計功能  
            'history/generate-summary', # 重複統計功能
            'history/cleanup',          # 手動清理功能
        ]
        
        self.target_files = [
            'app/api/v1/endpoints/sniper_signal_history.py'
        ]
    
    def remove_endpoint_from_file(self, file_path: str, endpoint: str):
        """從文件中移除特定端點"""
        if not os.path.exists(file_path):
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配端點路徑
        escaped_endpoint = re.escape(endpoint)
        pattern = rf'@router\.(get|post|put|delete)\(["\'][^"\']*{escaped_endpoint}[^"\']*["\']\).*?(?=@router\.|$)'
        
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, '', content, flags=re.DOTALL)
            content = re.sub(r'\n{4,}', '\n\n\n', content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✅ 移除: {endpoint}")
            return True
        
        return False
    
    def clean_history_apis(self):
        """清理歷史API"""
        print("🧹 第三階段API清理 - 清理歷史管理重複端點")
        print("=" * 60)
        
        total_removed = 0
        
        for file_path in self.target_files:
            if not os.path.exists(file_path):
                continue
                
            print(f"\n📄 處理文件: {file_path}")
            
            for endpoint in self.history_remove_endpoints:
                if self.remove_endpoint_from_file(file_path, endpoint):
                    total_removed += 1
        
        print(f"\n✅ 歷史API清理完成！移除 {total_removed} 個端點")
        
        # 顯示剩餘端點
        self.show_remaining_history_apis()
    
    def show_remaining_history_apis(self):
        """顯示剩餘的歷史API"""
        print("\n📊 歷史管理剩餘端點:")
        
        for file_path in self.target_files:
            if not os.path.exists(file_path):
                continue
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            routes = re.findall(r'@router\.(get|post|put|delete)\(["\']([^"\']+)["\']', content)
            
            print(f"\n📄 {os.path.basename(file_path)}: {len(routes)} 個端點")
            for method, path in routes:
                print(f"  {method.upper()} {path}")

if __name__ == "__main__":
    cleaner = HistoryAPICleanup()
    
    print("⚠️ 這將移除歷史管理中的重複統計和清理端點")
    print("保留核心的 history/signals 和 history/statistics")
    print("確認執行清理嗎？(y/N): ", end="")
    
    response = input().lower().strip()
    if response in ['y', 'yes']:
        cleaner.clean_history_apis()
        print("\n✅ 歷史API清理完成")
    else:
        print("❌ 已取消清理操作")
