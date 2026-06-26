#!/usr/bin/env python3
"""
Wiki Frontmatter 定时扫描脚本
定期扫描wiki目录，修复缺失的frontmatter
"""

import os
import sys
import yaml
import re
from pathlib import Path
from datetime import datetime
import subprocess
import json

# 配置
WIKI_DIR = Path("/home/agentuser/wiki")
REPORT_FILE = WIKI_DIR / "reports" / f"frontmatter_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
VALID_TYPES = ['concept', 'blueprint', 'architecture', 'design', 'reference', 'entity', 'training']

def extract_title(content):
    """从内容中提取标题"""
    lines = content.split('\n')
    for line in lines[:10]:
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
    else:
        return "reference"

def extract_tags(content, file_path):
    """提取可能的标签"""
    tags = []
    content_lower = content.lower()
    rel_path = str(file_path.relative_to(WIKI_DIR)).lower()
    
    # 内容关键词
    tag_keywords = {
        "mes": "mes", "wms": "wms", "aps": "aps", "sql": "sql",
        "数据库": "database", "接口": "api", "流程": "workflow",
        "设备": "equipment", "质量": "quality", "仓储": "warehouse",
        "网络": "network", "模板": "template", "vsdx": "visio",
        "异常": "exception", "指标": "kpi", "报表": "report"
    }
    
    for keyword, tag in tag_keywords.items():
        if keyword in content_lower:
            tags.append(tag)
    
    # 路径标签
    if "concepts/" in rel_path:
        tags.append("concept")
    if "通威农发" in rel_path:
        tags.append("tw-nongfa")
    
    return list(set(tags))[:5]

def generate_description(content, max_len=200):
    """生成简短描述"""
    lines = content.split('\n')
    desc_lines = []
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('---') and not line.startswith('|'):
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

def fix_frontmatter(file_path):
    """修复缺失的frontmatter"""
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
        
        # 生成frontmatter
        frontmatter = f"""---
title: {title}
project: {project}
created: '{created}'
updated: '{updated}'
type: {file_type}
description: '{description}'
tags:
{chr(10).join(f'- {tag}' for tag in tags)}
---

"""
        
        # 写入文件
        new_content = frontmatter + content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, f"已添加frontmatter: {title}"
    
    except Exception as e:
        return False, f"修复失败: {e}"

def scan_and_fix():
    """扫描并修复"""
    print(f"🔍 开始扫描wiki目录: {WIKI_DIR}")
    
    md_files = list(WIKI_DIR.rglob("*.md"))
    print(f"找到 {len(md_files)} 个.md文件")
    
    results = {
        "total": len(md_files),
        "already_valid": 0,
        "fixed": 0,
        "failed": 0,
        "details": []
    }
    
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if has_valid_frontmatter(content):
                results["already_valid"] += 1
                continue
            
            # 需要修复
            success, message = fix_frontmatter(file_path)
            rel_path = str(file_path.relative_to(WIKI_DIR))
            
            if success:
                results["fixed"] += 1
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
    """生成报告"""
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Wiki Frontmatter 扫描报告\n\n")
        f.write(f"**扫描时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**扫描目录**: {WIKI_DIR}\n\n")
        
        f.write("## 统计摘要\n\n")
        f.write(f"- 总文件数: {results['total']}\n")
        f.write(f"- 已有有效frontmatter: {results['already_valid']}\n")
        f.write(f"- 已修复: {results['fixed']}\n")
        f.write(f"- 修复失败: {results['failed']}\n")
        f.write(f"- 合规率: {(results['already_valid'] + results['fixed']) / results['total'] * 100:.1f}%\n\n")
        
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
        
        print("\n" + "=" * 50)
        print("扫描完成:")
        print(f"  总文件数: {results['total']}")
        print(f"  已有有效frontmatter: {results['already_valid']}")
        print(f"  已修复: {results['fixed']}")
        print(f"  修复失败: {results['failed']}")
        print(f"  合规率: {(results['already_valid'] + results['fixed']) / results['total'] * 100:.1f}%")
        
        if results['failed'] > 0:
            print(f"\n⚠️  有 {results['failed']} 个文件修复失败，请检查报告")
            sys.exit(1)
        else:
            print("\n✅ 所有文件frontmatter验证通过")
            sys.exit(0)
    
    except Exception as e:
        print(f"❌ 扫描过程中发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
