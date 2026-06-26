#!/usr/bin/env python3
"""
Wiki Frontmatter 验证器 (v2)
支持Azure DevOps YAML schema最佳实践
"""

import os
import sys
import yaml
import re
from pathlib import Path
from datetime import datetime

# v2 配置
REQUIRED_FIELDS = ['title', 'project', 'created', 'updated', 'type']
VALID_TYPES = ['concept', 'blueprint', 'architecture', 'design', 'reference', 
               'entity', 'training', 'glossary', 'case']
VALID_STATUS = ['draft', 'review', 'published', 'archived']
DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')
VERSION_PATTERN = re.compile(r'^\d+\.\d+\.\d+$')
MAX_TITLE_LENGTH = 100
MAX_DESC_LENGTH = 200
MAX_TAGS = 5

# 类型定义
TYPE_DEFINITIONS = {
    'concept': {
        'description': '概念性文档，解释理论和方法',
        'required_fields': ['title', 'project', 'created', 'updated', 'type'],
        'recommended_fields': ['description', 'tags']
    },
    'blueprint': {
        'description': '业务蓝图，包含流程设计和规范',
        'required_fields': ['title', 'project', 'created', 'updated', 'type'],
        'recommended_fields': ['description', 'tags', 'sources']
    },
    'architecture': {
        'description': '技术架构，包含系统设计和接口',
        'required_fields': ['title', 'project', 'created', 'updated', 'type'],
        'recommended_fields': ['description', 'tags', 'version']
    },
    'design': {
        'description': '详细设计，包含功能规格和实现',
        'required_fields': ['title', 'project', 'created', 'updated', 'type'],
        'recommended_fields': ['description', 'tags']
    },
    'reference': {
        'description': '参考资料，包含手册和指南',
        'required_fields': ['title', 'project', 'created', 'updated', 'type'],
        'recommended_fields': ['description', 'tags']
    },
    'entity': {
        'description': '实体文档，描述具体业务对象',
        'required_fields': ['title', 'project', 'created', 'updated', 'type'],
        'recommended_fields': ['description', 'tags']
    },
    'training': {
        'description': '培训材料，包含教程和课程',
        'required_fields': ['title', 'project', 'created', 'updated', 'type'],
        'recommended_fields': ['description', 'tags', 'x_duration', 'x_level']
    },
    'glossary': {
        'description': '术语表，包含术语定义和解释',
        'required_fields': ['title', 'project', 'created', 'updated', 'type'],
        'recommended_fields': ['description', 'tags', 'sources']
    },
    'case': {
        'description': '案例文档，包含实际案例和经验',
        'required_fields': ['title', 'project', 'created', 'updated', 'type'],
        'recommended_fields': ['description', 'tags']
    }
}

def extract_frontmatter(content):
    """提取frontmatter内容"""
    if not content.startswith('---'):
        return None
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return None
    
    return parts[1].strip()

def validate_date(date_str, field_name):
    """验证日期格式"""
    if not isinstance(date_str, str):
        return False, f"{field_name}必须是字符串格式"
    
    if not DATE_PATTERN.match(date_str):
        return False, f"{field_name}日期格式错误，应为YYYY-MM-DD，实际: {date_str}"
    
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True, None
    except ValueError:
        return False, f"{field_name}日期无效: {date_str}"

def validate_version(version_str):
    """验证版本号格式"""
    if not isinstance(version_str, str):
        return False, "版本号必须是字符串格式"
    
    if not VERSION_PATTERN.match(version_str):
        return False, f"版本号格式错误，应为x.y.z，实际: {version_str}"
    
    return True, None

def validate_tags(tags):
    """验证标签"""
    if not isinstance(tags, list):
        return False, "标签必须是数组格式"
    
    if len(tags) > MAX_TAGS:
        return False, f"标签数量({len(tags)})超过限制({MAX_TAGS})"
    
    # 检查唯一性
    if len(tags) != len(set(tags)):
        return False, "标签不能重复"
    
    # 检查每个标签是否为字符串
    for tag in tags:
        if not isinstance(tag, str):
            return False, f"标签必须是字符串，实际: {type(tag)}"
    
    return True, None

def validate_frontmatter(frontmatter_text, file_path):
    """验证frontmatter内容 (v2版本)"""
    errors = []
    warnings = []
    recommendations = []
    
    try:
        data = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as e:
        return [f"YAML解析错误: {e}"], [], []
    
    if not isinstance(data, dict):
        return ["frontmatter不是有效的YAML字典"], [], []
    
    # 1. 检查必填字段
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"缺少必填字段: {field}")
    
    # 2. 验证字段类型和格式
    for field, value in data.items():
        # 标题验证
        if field == 'title':
            if not isinstance(value, str):
                errors.append("title必须是字符串")
            elif len(value) > MAX_TITLE_LENGTH:
                warnings.append(f"title长度({len(value)})超过建议值({MAX_TITLE_LENGTH})")
        
        # 日期验证
        elif field in ['created', 'updated']:
            is_valid, error_msg = validate_date(value, field)
            if not is_valid:
                errors.append(error_msg)
        
        # 类型验证
        elif field == 'type':
            if value not in VALID_TYPES:
                warnings.append(f"type值'{value}'不在预定义列表中: {VALID_TYPES}")
        
        # 状态验证
        elif field == 'status':
            if value not in VALID_STATUS:
                warnings.append(f"status值'{value}'不在预定义列表中: {VALID_STATUS}")
        
        # 标签验证
        elif field == 'tags':
            is_valid, error_msg = validate_tags(value)
            if not is_valid:
                errors.append(error_msg)
        
        # 版本验证
        elif field == 'version':
            is_valid, error_msg = validate_version(value)
            if not is_valid:
                warnings.append(error_msg)
        
        # 描述验证
        elif field == 'description':
            if not isinstance(value, str):
                errors.append("description必须是字符串")
            elif len(value) > MAX_DESC_LENGTH:
                warnings.append(f"description长度({len(value)})超过建议值({MAX_DESC_LENGTH})")
        
        # 自定义字段验证
        elif field.startswith('x_'):
            # 自定义字段允许任何类型
            pass
        
        # 未知字段警告
        elif field not in ['author', 'sources', 'related', 'dependencies', 
                          'prerequisites', 'template', 'parameters']:
            warnings.append(f"未知字段: {field}")
    
    # 3. 检查类型特定的推荐字段
    if 'type' in data and data['type'] in TYPE_DEFINITIONS:
        type_def = TYPE_DEFINITIONS[data['type']]
        for field in type_def.get('recommended_fields', []):
            if field not in data:
                recommendations.append(f"类型'{data['type']}'推荐字段: {field}")
    
    # 4. 检查自定义字段格式
    for field in data.keys():
        if field.startswith('x_') and not field[2:].replace('_', '').isalnum():
            warnings.append(f"自定义字段名格式不规范: {field}")
    
    return errors, warnings, recommendations

def check_file(file_path):
    """检查单个文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter_text = extract_frontmatter(content)
        
        if frontmatter_text is None:
            return ["缺少frontmatter（文件应以---开头）"], [], []
        
        if not frontmatter_text:
            return ["frontmatter为空"], [], []
        
        return validate_frontmatter(frontmatter_text, file_path)
    
    except Exception as e:
        return [f"读取文件错误: {e}"], [], []

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
    total_recommendations = 0
    
    print(f"检查 {len(files)} 个.md文件的frontmatter (v2标准)...\n")
    
    for file_path in files:
        if not os.path.exists(file_path):
            continue
        
        errors, warnings, recommendations = check_file(file_path)
        
        if errors or warnings or recommendations:
            print(f"📄 {file_path}")
            
            for error in errors:
                print(f"  ❌ 错误: {error}")
                total_errors += 1
            
            for warning in warnings:
                print(f"  ⚠️  警告: {warning}")
                total_warnings += 1
            
            for recommendation in recommendations:
                print(f"  💡 建议: {recommendation}")
                total_recommendations += 1
            
            print()
    
    # 输出统计
    print("=" * 60)
    print("检查完成 (v2标准):")
    print(f"  总文件数: {len(files)}")
    print(f"  错误数: {total_errors}")
    print(f"  警告数: {total_warnings}")
    print(f"  建议数: {total_recommendations}")
    
    if total_errors > 0:
        print("\n❌ 发现错误，请修复后重新提交")
        print("参考标准: wiki/FRONTMATTER_STANDARD.md (v2)")
        sys.exit(1)
    elif total_warnings > 0:
        print("\n⚠️  发现警告，建议修复但不阻止提交")
        sys.exit(0)
    else:
        print("\n✅ 所有文件frontmatter验证通过 (v2标准)")
        sys.exit(0)

if __name__ == "__main__":
    main()
