#!/usr/bin/env python3
"""
實際執行狙擊手API清理的腳本
移除明確未使用的調試和測試端點
"""

import os
import re
import shutil
from datetime import datetime

class APIEndpointRemover:
    def __init__(self):
        # 明確可以安全移除的調試/測試端點
        self.safe_remove_endpoints = [
            'debug-active-signals',
            'test-email-notification', 
            'create-test-signal',
            'clear-all-signals',
            'active-signals-simple',
            'optimize-thresholds',
        ]
        
        # 需要檢查的文件
        self.target_files = [
            'app/api/v1/endpoints/sniper_smart_layer.py',
            'app/api/v1/endpoints/scalping_precision.py'
        ]
    
    def backup_files(self):
        """備份原始文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"api_backup_{timestamp}"
        
        os.makedirs(backup_dir, exist_ok=True)
        
        for file_path in self.target_files:
            if os.path.exists(file_path):
                backup_path = os.path.join(backup_dir, os.path.basename(file_path))
                shutil.copy2(file_path, backup_path)
                print(f"✅ 備份: {file_path} -> {backup_path}")
        
        return backup_dir
    
    def remove_endpoint_from_file(self, file_path: str, endpoint: str):
        """從文件中移除特定端點"""
        if not os.path.exists(file_path):
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 構建匹配模式 - 匹配從 @router 到下一個 @router 或文件結尾
        patterns = [
            # GET/POST/PUT/DELETE 路由
            rf'@router\.(get|post|put|delete)\(["\'].*?{re.escape(endpoint)}.*?["\']\).*?(?=@router|$)',
            # WebSocket 路由
            rf'@router\.websocket\(["\'].*?{re.escape(endpoint)}.*?["\']\).*?(?=@router|$)',
        ]
        
        removed = False
        for pattern in patterns:
            if re.search(pattern, content, re.DOTALL):
                content = re.sub(pattern, '', content, flags=re.DOTALL)
                removed = True
                break
        
        if removed:
            # 清理多餘空行
            content = re.sub(r'\n{3,}', '\n\n', content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✅ 已從 {file_path} 移除端點: {endpoint}")
            return True
        
        return False
    
    def clean_apis(self):
        """執行API清理"""
        print("🧹 開始清理狙擊手API中的調試端點")
        print("=" * 60)
        
        # 備份文件
        backup_dir = self.backup_files()
        print(f"📦 備份目錄: {backup_dir}")
        
        print("\n🗑️ 移除調試端點:")
        total_removed = 0
        
        for endpoint in self.safe_remove_endpoints:
            print(f"\n🎯 處理端點: {endpoint}")
            
            for file_path in self.target_files:
                if self.remove_endpoint_from_file(file_path, endpoint):
                    total_removed += 1
        
        print(f"\n✅ 清理完成！總共移除 {total_removed} 個端點")
        
        # 驗證清理結果
        self.verify_cleanup()
    
    def verify_cleanup(self):
        """驗證清理結果"""
        print("\n🔍 驗證清理結果:")
        
        for file_path in self.target_files:
            if not os.path.exists(file_path):
                continue
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 計算剩餘端點數
            router_count = len(re.findall(r'@router\.\w+\(', content))
            print(f"  📄 {file_path}: 剩餘 {router_count} 個端點")
            
            # 檢查是否還有調試端點
            for endpoint in self.safe_remove_endpoints:
                if endpoint in content:
                    print(f"    ⚠️ 仍存在: {endpoint}")
    
    def show_remaining_endpoints(self):
        """顯示剩餘的端點"""
        print("\n📊 剩餘端點統計:")
        
        for file_path in self.target_files:
            if not os.path.exists(file_path):
                continue
                
            print(f"\n📄 {os.path.basename(file_path)}:")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取所有路由
            routes = re.findall(r'@router\.(get|post|put|delete|websocket)\(["\']([^"\']+)["\']', content)
            
            for method, path in routes:
                print(f"  {method.upper()} {path}")

if __name__ == "__main__":
    remover = APIEndpointRemover()
    
    print("⚠️ 這將移除調試和測試用的API端點")
    print("確認執行清理嗎？(y/N): ", end="")
    
    response = input().lower().strip()
    if response in ['y', 'yes']:
        remover.clean_apis()
        remover.show_remaining_endpoints()
        
        print("\n📋 後續建議:")
        print("1. 重啟後端服務測試")
        print("2. 檢查前端功能正常")
        print("3. 如有問題可從備份恢復")
    else:
        print("❌ 已取消清理操作")
