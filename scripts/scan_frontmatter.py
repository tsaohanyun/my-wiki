#!/usr/bin/env python3
"""
Wiki Frontmatter 扫描脚本 (v2)
支持Azure DevOps YAML schema最佳实践
"""

import os
import sys
import yaml
import re
from pathlib import Path
from datetime import datetime
import subprocess
import json

# v2 配置
WIKI_DIR = Path("/home/agentuser/wiki")
REPORT_FILE = WIKI_DIR / "reports" / f"frontmatter_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
VALID_TYPES = ['concept', 'blueprint', 'architecture', 'design', 'reference', 
               'entity', 'training', 'glossary', 'case']
VALID_STATUS = ['draft', 'review', 'published', 'archived']

# 自动提取规则
EXTRACTION_RULES = {
    'title': {
        'priority': ['h1', 'h2', 'filename']
    },
    'project': {
        'rules': [
            {'path': '*/通威农发/*', 'value': '通威农发'},
            {'path': '*/欧软/*', 'value': '欧软'},
            {'default': '通用'}
        ]
    },
    'type': {
        'rules': [
            {'path': '*/concepts/*', 'value': 'concept'},
            {'path': '*/业务蓝图/*', 'value': 'blueprint'},
            {'path': '*/技术架构/*', 'value': 'architecture'},
            {'path': '*/详细设计/*', 'value': 'design'},
            {'path': '*/培训/*', 'value': 'training'},
            {'default': 'reference'}
        ]
    }
}

# 标签提取关键词
TAG_KEYWORDS = {
    'mes': 'mes', 'wms': 'wms', 'aps': 'aps', 'erp': 'erp',
    'sql': 'sql', '数据库': 'database', '接口': 'api', '集成': 'integration',
    '流程': 'workflow', '设备': 'equipment', '质量': 'quality',
    '仓储': 'warehouse', '网络': 'network', '模板': 'template',
    'vsdx': 'visio', '异常': 'exception', '指标': 'kpi', '报表': 'report',
    '智能制造': 'smart-manufacturing', '数字化转型': 'digital-transformation',
    '工业4.0': 'industry-4', '物联网': 'iot', '人工智能': 'ai'
}

def extract_title(content):
    """从内容中提取标题"""
    lines = content.split('\n')
    for line in lines[:15]:
        line = line.strip()
        if line.startswith('# '):
            return line[2:].strip()
        elif line.startswith('## '):
            return line[3:].strip()
    return "未命名文档"

def determine_project(file_path):
    """根据路径确定项目"""
    rel_path = str(file_path.relative_to(WIKI_DIR))
    if "通威农发" in rel_path:
        return "通威农发"
    elif "欧软" in rel_path:
        return "欧软"
    else:
        return "通用"

def determine_type(file_path, content):
    """根据路径和内容确定类型"""
    rel_path = str(file_path.relative_to(WIKI_DIR))
    if "concepts/" in rel_path:
        return "concept"
    elif "业务蓝图" in rel_path:
        return "blueprint"
    elif "技术架构" in rel_path:
        return "architecture"
    elif "详细设计" in rel_path:
        return "design"
    elif "培训" in rel_path:
        return "training"
    elif "术语" in rel_path or "glossary" in rel_path.lower():
        return "glossary"
    elif "案例" in rel_path or "踩坑" in rel_path:
        return "case"
    else:
        return "reference"

def extract_tags(content, file_path):
    """提取可能的标签"""
    tags = []
    content_lower = content.lower()
    rel_path = str(file_path.relative_to(WIKI_DIR)).lower()
    
    # 内容关键词提取
    for keyword, tag in TAG_KEYWORDS.items():
        if keyword in content_lower:
            tags.append(tag)
    
    # 路径标签提取
    if "concepts/" in rel_path:
        tags.append("concept")
    if "通威农发" in rel_path:
        tags.append("tw-nongfa")
    if "欧软" in rel_path:
        tags.append("ouft")
    
    # 去重并限制数量
    unique_tags = list(set(tags))[:5]
    return unique_tags

def generate_description(content, max_len=200):
    """生成简短描述"""
    lines = content.split('\n')
    desc_lines = []
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('---') and not line.startswith('|'):
            # 跳过元数据行
            if ':' in line and line.split(':')[0].strip().lower() in ['title', 'project', 'created', 'updated', 'type']:
                continue
            desc_lines.append(line)
        if len(' '.join(desc_lines)) > max_len:
            break
    
    desc = ' '.join(desc_lines)[:max_len]
    if len(desc) == max_len:
        desc += "..."
    return desc

def get_file_dates(file_path):
    """获取文件的创建和修改时间"""
    stat = os.stat(file_path)
    created = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d')
    updated = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')
    return created, updated

def has_valid_frontmatter(content):
    """检查是否有有效的frontmatter"""
    if not content.startswith('---'):
        return False
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return False
    
    frontmatter = parts[1].strip()
    if not frontmatter:
        return False
    
    try:
        data = yaml.safe_load(frontmatter)
        return isinstance(data, dict)
    except:
        return False

def generate_version(file_path):
    """生成版本号"""
    # 基于文件修改时间生成版本号
    stat = os.stat(file_path)
    mtime = datetime.fromtimestamp(stat.st_mtime)
    return f"1.0.{mtime.strftime('%Y%m%d')}"

def fix_frontmatter(file_path):
    """修复缺失的frontmatter (v2版本)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if has_valid_frontmatter(content):
            return False, "已有有效frontmatter"
        
        # 提取信息
        title = extract_title(content)
        project = determine_project(file_path)
        file_type = determine_type(file_path, content)
        tags = extract_tags(content, file_path)
        description = generate_description(content)
        created, updated = get_file_dates(file_path)
        version = generate_version(file_path)
        
        # 生成frontmatter (v2格式)
        frontmatter = f"""---
title: {title}
project: {project}
created: '{created}'
updated: '{updated}'
type: {file_type}
status: published
description: '{description}'
tags:
{chr(10).join(f'- {tag}' for tag in tags)}
author: Hermes Wiki Agent
version: '{version}'
---

"""
        
        # 写入文件
        new_content = frontmatter + content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, f"已添加frontmatter (v2): {title}"
    
    except Exception as e:
        return False, f"修复失败: {e}"

def scan_and_fix():
    """扫描并修复"""
    print(f"🔍 开始扫描wiki目录 (v2标准): {WIKI_DIR}")
    
    md_files = list(WIKI_DIR.rglob("*.md"))
    # 排除备份目录和报告文件
    md_files = [f for f in md_files if 'backups' not in str(f) and 'frontmatter_scan_' not in f.name]
    print(f"找到 {len(md_files)} 个.md文件")
    
    results = {
        "total": len(md_files),
        "already_valid": 0,
        "fixed": 0,
        "failed": 0,
        "v1_compatible": 0,
        "v2_compliant": 0,
        "details": []
    }
    
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if has_valid_frontmatter(content):
                results["already_valid"] += 1
                
                # 检查是否符合v2标准
                parts = content.split('---', 2)
                frontmatter = parts[1].strip()
                data = yaml.safe_load(frontmatter)
                
                v2_fields = ['status', 'version', 'author']
                has_v2_fields = all(field in data for field in v2_fields)
                
                if has_v2_fields:
                    results["v2_compliant"] += 1
                else:
                    results["v1_compatible"] += 1
                
                continue
            
            # 需要修复
            success, message = fix_frontmatter(file_path)
            rel_path = str(file_path.relative_to(WIKI_DIR))
            
            if success:
                results["fixed"] += 1
                results["v2_compliant"] += 1
                results["details"].append({
                    "file": rel_path,
                    "status": "fixed",
                    "message": message
                })
            else:
                results["failed"] += 1
                results["details"].append({
                    "file": rel_path,
                    "status": "failed",
                    "message": message
                })
        
        except Exception as e:
            results["failed"] += 1
            rel_path = str(file_path.relative_to(WIKI_DIR))
            results["details"].append({
                "file": rel_path,
                "status": "error",
                "message": str(e)
            })
    
    return results

def generate_report(results):
    """生成报告 (v2格式)"""
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # 获取报告文件名作为标题
    report_title = f"Wiki Frontmatter 扫描报告 (v2)"
    report_date = datetime.now().strftime('%Y-%m-%d')
    report_desc = f"Wiki frontmatter扫描报告 (v2标准)，显示{results['total']}个文件的检查结果"
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        # 先写frontmatter (v2格式)
        f.write(f"""---
title: {report_title}
project: 通用
created: '{report_date}'
updated: '{report_date}'
type: reference
status: published
description: '{report_desc}'
tags:
- frontmatter
- scan
- report
- v2
author: Hermes Wiki Agent
version: '1.0.0'
---

""")
        # 再写报告内容
        f.write(f"# {report_title}\n\n")
        f.write(f"**扫描时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**扫描目录**: {WIKI_DIR}\n")
        f.write(f"**标准版本**: v2\n\n")
        
        f.write("## 统计摘要\n\n")
        f.write(f"- 总文件数: {results['total']}\n")
        f.write(f"- 已有有效frontmatter: {results['already_valid']}\n")
        f.write(f"  - v1兼容: {results['v1_compatible']}\n")
        f.write(f"  - v2合规: {results['v2_compliant']}\n")
        f.write(f"- 已修复: {results['fixed']}\n")
        f.write(f"- 修复失败: {results['failed']}\n")
        f.write(f"- v2合规率: {(results['v2_compliant'] + results['fixed']) / results['total'] * 100:.1f}%\n\n")
        
        if results['details']:
            f.write("## 修复详情\n\n")
            for detail in results['details']:
                status_icon = "✅" if detail['status'] == 'fixed' else "❌"
                f.write(f"### {status_icon} {detail['file']}\n")
                f.write(f"- 状态: {detail['status']}\n")
                f.write(f"- 信息: {detail['message']}\n\n")
    
    print(f"\n📊 报告已生成: {REPORT_FILE}")

def main():
    """主函数"""
    try:
        results = scan_and_fix()
        generate_report(results)
        
        print("\n" + "=" * 60)
        print("扫描完成 (v2标准):")
        print(f"  总文件数: {results['total']}")
        print(f"  已有有效frontmatter: {results['already_valid']}")
        print(f"    - v1兼容: {results['v1_compatible']}")
        print(f"    - v2合规: {results['v2_compliant']}")
        print(f"  已修复: {results['fixed']}")
        print(f"  修复失败: {results['failed']}")
        print(f"  v2合规率: {(results['v2_compliant'] + results['fixed']) / results['total'] * 100:.1f}%")
        
        if results['failed'] > 0:
            print(f"\n⚠️  有 {results['failed']} 个文件修复失败，请检查报告")
            sys.exit(1)
        else:
            print("\n✅ 所有文件frontmatter验证通过 (v2标准)")
            sys.exit(0)
    
    except Exception as e:
        print(f"❌ 扫描过程中发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
