#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vue 前端服務器 - 為量子對戰系統提供 Web 界面
"""

import asyncio
import json
import sqlite3
import subprocess
import sys
import threading
import time
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse


class QuantumBattleAPIHandler(SimpleHTTPRequestHandler):
    """API 和靜態文件處理器"""
    
    def __init__(self, *args, **kwargs):
        self.database_path = kwargs.pop('database_path', 'quantum_battle_results.db')
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """處理 GET 請求"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/data':
            self.handle_api_data()
        else:
            # 提供靜態文件
            if self.path == '/' or self.path == '':
                self.path = '/index.html'
            super().do_GET()
    
    def handle_api_data(self):
        """處理 API 數據請求"""
        try:
            # 讀取資料庫數據
            data = self.get_database_data()
            
            # 設置響應頭
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # 發送數據
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"API 錯誤: {e}")
            self.send_error(500, f"API Error: {e}")
    
    def get_database_data(self):
        """從資料庫獲取數據"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            data = {}
            
            # 獲取最新信號
            cursor.execute('''
                SELECT * FROM battle_signals 
                ORDER BY created_at DESC LIMIT 50
            ''')
            data['signals'] = [dict(zip([col[0] for col in cursor.description], row)) 
                              for row in cursor.fetchall()]
            
            # 獲取最新投資組合狀態
            cursor.execute('''
                SELECT * FROM portfolio_status 
                ORDER BY created_at DESC LIMIT 20
            ''')
            data['portfolios'] = [dict(zip([col[0] for col in cursor.description], row)) 
                                 for row in cursor.fetchall()]
            
            # 獲取最新交易
            cursor.execute('''
                SELECT * FROM trade_history 
                ORDER BY created_at DESC LIMIT 100
            ''')
            data['trades'] = [dict(zip([col[0] for col in cursor.description], row)) 
                             for row in cursor.fetchall()]
            
            # 獲取對戰結果
            cursor.execute('''
                SELECT * FROM battle_results 
                ORDER BY created_at DESC LIMIT 10
            ''')
            data['results'] = [dict(zip([col[0] for col in cursor.description], row)) 
                              for row in cursor.fetchall()]
            
            conn.close()
            return data
            
        except Exception as e:
            print(f"資料庫讀取錯誤: {e}")
            return {
                'signals': [],
                'portfolios': [],
                'trades': [],
                'results': []
            }
    
    def do_OPTIONS(self):
        """處理 CORS 預檢請求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

class QuantumBattleFrontendServer:
    """量子對戰前端服務器"""
    
    def __init__(self, port=8888, database_path='quantum_battle_results.db'):
        self.port = port
        self.database_path = database_path
        self.httpd = None
        self.server_thread = None
        
    def start_server(self):
        """啟動服務器"""
        try:
            # 切換到前端目錄
            frontend_dir = Path(__file__).parent / 'frontend'
            if not frontend_dir.exists():
                print(f"❌ 前端目錄不存在: {frontend_dir}")
                return False
            
            import os
            os.chdir(frontend_dir)
            
            # 創建處理器類，綁定資料庫路徑
            handler_class = lambda *args, **kwargs: QuantumBattleAPIHandler(*args, database_path=self.database_path, **kwargs)
            
            # 啟動 HTTP 服務器
            self.httpd = HTTPServer(('localhost', self.port), handler_class)
            
            print(f"🌐 量子對戰前端服務器啟動於: http://localhost:{self.port}")
            print(f"📊 API 端點: http://localhost:{self.port}/api/data")
            print(f"💾 資料庫: {self.database_path}")
            
            # 在背景線程中運行服務器
            self.server_thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
            self.server_thread.start()
            
            # 等待一下然後打開瀏覽器
            time.sleep(1)
            webbrowser.open(f"http://localhost:{self.port}")
            
            return True
            
        except Exception as e:
            print(f"❌ 前端服務器啟動失敗: {e}")
            return False
    
    def stop_server(self):
        """停止服務器"""
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            print("🛑 前端服務器已停止")

def main():
    """主函數 - 獨立運行前端服務器"""
    import argparse
    
    parser = argparse.ArgumentParser(description='量子對戰前端服務器')
    parser.add_argument('--port', type=int, default=8888, help='服務器端口 (默認: 8888)')
    parser.add_argument('--database', default='quantum_battle_results.db', help='資料庫文件路徑')
    
    args = parser.parse_args()
    
    server = QuantumBattleFrontendServer(args.port, args.database)
    
    if server.start_server():
        try:
            print("💡 按 Ctrl+C 停止服務器")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🔌 收到停止信號...")
            server.stop_server()
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
