#!/usr/bin/env python3
"""
Wiki Frontmatter 迁移脚本
将v1格式的frontmatter升级到v2标准
"""

import os
import sys
import yaml
from pathlib import Path
from datetime import datetime
import shutil

# 配置
WIKI_DIR = Path("/home/agentuser/wiki")
BACKUP_DIR = WIKI_DIR / "backups" / f"frontmatter_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# v2新增字段默认值
V2_DEFAULTS = {
    'status': 'published',
    'author': 'Hermes Wiki Agent',
    'version': '1.0.0'
}

def is_v1_frontmatter(data):
    """检查是否是v1格式的frontmatter"""
    v1_fields = ['title', 'project', 'created', 'updated', 'type']
    v2_fields = ['status', 'version', 'author']
    
    # 有v1字段但没有v2字段
    has_v1 = all(field in data for field in v1_fields)
    has_v2 = any(field in data for field in v2_fields)
    
    return has_v1 and not has_v2

def migrate_frontmatter(data, file_path):
    """迁移frontmatter到v2格式"""
    migrated = data.copy()
    
    # 添加v2默认字段
    for field, default_value in V2_DEFAULTS.items():
        if field not in migrated:
            migrated[field] = default_value
    
    # 基于文件修改时间生成版本号
    stat = os.stat(file_path)
    mtime = datetime.fromtimestamp(stat.st_mtime)
    migrated['version'] = f"1.0.{mtime.strftime('%Y%m%d')}"
    
    return migrated

def backup_file(file_path):
    """备份文件"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    rel_path = file_path.relative_to(WIKI_DIR)
    backup_path = BACKUP_DIR / rel_path
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(file_path, backup_path)
    return backup_path

def migrate_file(file_path, dry_run=False):
    """迁移单个文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---'):
            return False, "无frontmatter"
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            return False, "frontmatter格式错误"
        
        frontmatter_text = parts[1].strip()
        if not frontmatter_text:
            return False, "frontmatter为空"
        
        try:
            data = yaml.safe_load(frontmatter_text)
        except yaml.YAMLError as e:
            return False, f"YAML解析错误: {e}"
        
        if not isinstance(data, dict):
            return False, "frontmatter不是字典"
        
        if not is_v1_frontmatter(data):
            return False, "已是v2格式或格式不符"
        
        # 迁移
        migrated_data = migrate_frontmatter(data, file_path)
        
        if dry_run:
            return True, "DRY RUN: 将迁移"
        
        # 备份原文件
        backup_path = backup_file(file_path)
        
        # 生成新的frontmatter
        new_frontmatter = yaml.dump(migrated_data, default_flow_style=False, allow_unicode=True)
        new_content = f"---\n{new_frontmatter}---\n{parts[2]}"
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, f"已迁移到v2格式 (备份: {backup_path.name})"
    
    except Exception as e:
        return False, f"迁移失败: {e}"

def scan_and_migrate(dry_run=False):
    """扫描并迁移"""
    mode = "DRY RUN" if dry_run else "实际迁移"
    print(f"🔍 开始扫描wiki目录 ({mode}模式)...")
    
    md_files = list(WIKI_DIR.rglob("*.md"))
    # 排除备份目录和报告文件
    md_files = [f for f in md_files if 'backups' not in str(f) and 'frontmatter_scan_' not in f.name]
    print(f"找到 {len(md_files)} 个.md文件")
    
    results = {
        "total": len(md_files),
        "already_v2": 0,
        "migrated": 0,
        "skipped": 0,
        "failed": 0,
        "details": []
    }
    
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.startswith('---'):
                results["skipped"] += 1
                continue
            
            parts = content.split('---', 2)
            if len(parts) < 3:
                results["skipped"] += 1
                continue
            
            frontmatter_text = parts[1].strip()
            if not frontmatter_text:
                results["skipped"] += 1
                continue
            
            try:
                data = yaml.safe_load(frontmatter_text)
            except:
                results["skipped"] += 1
                continue
            
            if not isinstance(data, dict):
                results["skipped"] += 1
                continue
            
            if is_v1_frontmatter(data):
                success, message = migrate_file(file_path, dry_run)
                rel_path = str(file_path.relative_to(WIKI_DIR))
                
                if success:
                    results["migrated"] += 1
                    results["details"].append({
                        "file": rel_path,
                        "status": "migrated",
                        "message": message
                    })
                else:
                    results["failed"] += 1
                    results["details"].append({
                        "file": rel_path,
                        "status": "failed",
                        "message": message
                    })
            else:
                results["already_v2"] += 1
        
        except Exception as e:
            results["failed"] += 1
            rel_path = str(file_path.relative_to(WIKI_DIR))
            results["details"].append({
                "file": rel_path,
                "status": "error",
                "message": str(e)
            })
    
    return results

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='迁移wiki frontmatter到v2格式')
    parser.add_argument('--dry-run', action='store_true', help='只扫描不实际迁移')
    parser.add_argument('--backup-dir', type=str, help='备份目录')
    
    args = parser.parse_args()
    
    if args.backup_dir:
        global BACKUP_DIR
        BACKUP_DIR = Path(args.backup_dir)
    
    try:
        results = scan_and_migrate(dry_run=args.dry_run)
        
        mode = "DRY RUN" if args.dry_run else "实际迁移"
        print(f"\n{'='*60}")
        print(f"迁移完成 ({mode}):")
        print(f"  总文件数: {results['total']}")
        print(f"  已是v2格式: {results['already_v2']}")
        print(f"  已迁移: {results['migrated']}")
        print(f"  跳过: {results['skipped']}")
        print(f"  失败: {results['failed']}")
        
        if results['details']:
            print(f"\n{'='*60}")
            print("迁移详情:")
            for detail in results['details'][:20]:  # 只显示前20个
                status_icon = "✅" if detail['status'] == 'migrated' else "❌"
                print(f"  {status_icon} {detail['file']}: {detail['message']}")
            
            if len(results['details']) > 20:
                print(f"  ... 还有 {len(results['details']) - 20} 个文件")
        
        if args.dry_run:
            print(f"\n💡 提示: 运行不带 --dry-run 参数的命令执行实际迁移")
        elif results['migrated'] > 0:
            print(f"\n✅ 已迁移 {results['migrated']} 个文件到v2格式")
            print(f"📁 备份目录: {BACKUP_DIR}")
        
        sys.exit(0 if results['failed'] == 0 else 1)
    
    except Exception as e:
        print(f"❌ 迁移过程中发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
