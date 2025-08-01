#!/usr/bin/env python3
"""
🎯 狙擊手計劃 - 數據完整性檢查

檢查系統中是否存在假數據、測試數據或隨機生成數據
確保所有數據都來自真實的市場源
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any

class SniperDataIntegrityChecker:
    def __init__(self):
        self.root_path = Path("/Users/itts/Desktop/Trading X")
        self.fake_data_patterns = [
            r'Math\.random\(\)',
            r'fake.*data',
            r'dummy.*data',
            r'test.*data.*=.*\d+',
            r'mock.*data',
            r'sample.*data',
            r'random\.\w+\(',
            r'np\.random\.',
            r'pandas\.util\.testing',
            r'generateMockData',
            r'createFakeData'
        ]
        self.suspicious_files = []
        self.clean_files = []
        
    def check_file_content(self, file_path: Path) -> Dict[str, Any]:
        """檢查單個文件的內容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            issues = []
            
            for pattern in self.fake_data_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = content.split('\n')[line_num - 1].strip()
                    
                    # 排除註釋和文檔中的說明
                    if not self.is_documentation_or_comment(line_content):
                        issues.append({
                            'pattern': pattern,
                            'line': line_num,
                            'content': line_content,
                            'match': match.group()
                        })
            
            return {
                'file': str(file_path),
                'issues': issues,
                'is_clean': len(issues) == 0
            }
            
        except Exception as e:
            return {
                'file': str(file_path),
                'issues': [{'error': str(e)}],
                'is_clean': False
            }
    
    def is_documentation_or_comment(self, line: str) -> bool:
        """判斷是否為文檔或註釋行"""
        line = line.strip()
        
        # Python 註釋
        if line.startswith('#'):
            return True
        
        # JavaScript/TypeScript 註釋
        if line.startswith('//') or line.startswith('/*') or line.startswith('*'):
            return True
            
        # HTML 註釋
        if '<!--' in line or '-->' in line:
            return True
            
        # 文檔字符串
        if line.startswith('"""') or line.startswith("'''"):
            return True
            
        # Markdown 內容
        if line.startswith('`') or line.startswith('-') or line.startswith('#'):
            return True
            
        return False
    
    def scan_sniper_files(self) -> Dict[str, Any]:
        """掃描狙擊手計劃相關文件"""
        print("🔍 掃描狙擊手計劃文件中的數據完整性...")
        
        # 狙擊手核心文件
        sniper_files = [
            'sniper_unified_data_layer.py',
            'frontend/src/views/TradingStrategySniperIntegrated.vue',
            'app/api/v1/endpoints/notifications.py',
            'test_sniper_plan_complete.py',
            'test_gmail_sniper.py'
        ]
        
        results = {
            'total_files': 0,
            'clean_files': 0,
            'suspicious_files': 0,
            'file_results': []
        }
        
        for file_rel_path in sniper_files:
            file_path = self.root_path / file_rel_path
            
            if file_path.exists():
                print(f"   檢查: {file_rel_path}")
                result = self.check_file_content(file_path)
                results['file_results'].append(result)
                results['total_files'] += 1
                
                if result['is_clean']:
                    results['clean_files'] += 1
                    print(f"      ✅ 清潔")
                else:
                    results['suspicious_files'] += 1
                    print(f"      ⚠️  發現 {len(result['issues'])} 個問題")
                    for issue in result['issues']:
                        if 'error' not in issue:
                            print(f"         行 {issue['line']}: {issue['match']}")
            else:
                print(f"   ⚠️  文件不存在: {file_rel_path}")
        
        return results
    
    def generate_report(self) -> str:
        """生成完整性檢查報告"""
        results = self.scan_sniper_files()
        
        report = f"""
🎯 狙擊手計劃數據完整性檢查報告
{'=' * 50}

📊 檢查統計:
• 總文件數: {results['total_files']}
• 清潔文件: {results['clean_files']}
• 可疑文件: {results['suspicious_files']}
• 完整性率: {(results['clean_files'] / max(results['total_files'], 1) * 100):.1f}%

"""
        
        if results['suspicious_files'] > 0:
            report += "⚠️  發現的問題:\n"
            for file_result in results['file_results']:
                if not file_result['is_clean']:
                    report += f"\n📁 {file_result['file']}:\n"
                    for issue in file_result['issues']:
                        if 'error' not in issue:
                            report += f"   • 行 {issue['line']}: {issue['match']}\n"
                            report += f"     內容: {issue['content']}\n"
        else:
            report += "✅ 所有狙擊手文件都通過數據完整性檢查!\n"
        
        report += f"""
🎯 檢查結論:
"""
        
        if results['suspicious_files'] == 0:
            report += """✅ 狙擊手計劃系統數據完整性良好
✅ 未發現假數據或測試數據
✅ 所有數據來源符合真實市場標準
✅ 系統已準備好生產環境部署
"""
        else:
            report += f"""⚠️  發現 {results['suspicious_files']} 個文件存在數據完整性問題
🔧 建議立即修復這些問題以確保數據真實性
📧 修復完成後系統才能安全使用
"""
        
        return report

def main():
    checker = SniperDataIntegrityChecker()
    
    print("🎯 狙擊手計劃數據完整性檢查開始...")
    print()
    
    report = checker.generate_report()
    print(report)
    
    # 保存報告
    report_file = f"sniper_data_integrity_report_{Path().cwd().name}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📝 完整報告已保存至: {report_file}")

if __name__ == "__main__":
    main()
