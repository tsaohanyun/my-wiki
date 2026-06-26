#!/usr/bin/env python3
"""
Wiki Frontmatter 验证器
用于pre-commit hook，检查所有.md文件是否包含有效的YAML frontmatter
"""

import os
import sys
import yaml
import re
from pathlib import Path
from datetime import datetime

# 配置
REQUIRED_FIELDS = ['title', 'project', 'created', 'updated', 'type']
VALID_TYPES = ['concept', 'blueprint', 'architecture', 'design', 'reference', 'entity', 'training']
DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')
MAX_TAGS = 5
MAX_DESC_LENGTH = 200

def extract_frontmatter(content):
    """提取frontmatter内容"""
    if not content.startswith('---'):
        return None
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return None
    
    return parts[1].strip()

def validate_frontmatter(frontmatter_text, file_path):
    """验证frontmatter内容"""
    errors = []
    warnings = []
    
    try:
        data = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as e:
        return [f"YAML解析错误: {e}"], []
    
    if not isinstance(data, dict):
        return ["frontmatter不是有效的YAML字典"], []
    
    # 检查必填字段
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"缺少必填字段: {field}")
    
    # 验证日期格式
    for date_field in ['created', 'updated']:
        if date_field in data:
            date_str = str(data[date_field])
            if not DATE_PATTERN.match(date_str):
                errors.append(f"{date_field}日期格式错误，应为YYYY-MM-DD，实际: {date_str}")
    
    # 验证type值
    if 'type' in data:
        if data['type'] not in VALID_TYPES:
            warnings.append(f"type值'{data['type']}'不在预定义列表中: {VALID_TYPES}")
    
    # 验证tags
    if 'tags' in data:
        if isinstance(data['tags'], list):
            if len(data['tags']) > MAX_TAGS:
                warnings.append(f"tags数量({len(data['tags'])})超过建议值({MAX_TAGS})")
        else:
            warnings.append("tags应该是列表格式")
    
    # 验证description长度
    if 'description' in data:
        desc = str(data['description'])
        if len(desc) > MAX_DESC_LENGTH:
            warnings.append(f"description长度({len(desc)})超过建议值({MAX_DESC_LENGTH})")
    
    return errors, warnings

def check_file(file_path):
    """检查单个文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter_text = extract_frontmatter(content)
        
        if frontmatter_text is None:
            return ["缺少frontmatter（文件应以---开头）"], []
        
        if not frontmatter_text:
            return ["frontmatter为空"], []
        
        return validate_frontmatter(frontmatter_text, file_path)
    
    except Exception as e:
        return [f"读取文件错误: {e}"], []

def main():
    """主函数"""
    # 获取git暂存区的.md文件
    import subprocess
    
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            print("错误: 无法获取git暂存区文件")
            sys.exit(1)
        
        files = [f for f in result.stdout.strip().split('\n') if f.endswith('.md')]
        
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)
    
    if not files:
        print("没有.md文件需要检查")
        sys.exit(0)
    
    total_errors = 0
    total_warnings = 0
    
    print(f"检查 {len(files)} 个.md文件的frontmatter...\n")
    
    for file_path in files:
        if not os.path.exists(file_path):
            continue
        
        errors, warnings = check_file(file_path)
        
        if errors or warnings:
            print(f"📄 {file_path}")
            
            for error in errors:
                print(f"  ❌ 错误: {error}")
                total_errors += 1
            
            for warning in warnings:
                print(f"  ⚠️  警告: {warning}")
                total_warnings += 1
            
            print()
    
    # 输出统计
    print("=" * 50)
    print(f"检查完成:")
    print(f"  总文件数: {len(files)}")
    print(f"  错误数: {total_errors}")
    print(f"  警告数: {total_warnings}")
    
    if total_errors > 0:
        print("\n❌ 发现错误，请修复后重新提交")
        print("参考标准: wiki/FRONTMATTER_STANDARD.md")
        sys.exit(1)
    elif total_warnings > 0:
        print("\n⚠️  发现警告，建议修复但不阻止提交")
        sys.exit(0)
    else:
        print("\n✅ 所有文件frontmatter验证通过")
        sys.exit(0)

if __name__ == "__main__":
    main()
