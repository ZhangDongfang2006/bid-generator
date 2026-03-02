#!/usr/bin/env python3
"""
清理输出目录，保留最新10份文件

功能：
1. 列出 output 目录中的所有文件
2. 按修改时间排序
3. 保留最新的10份投标文件
4. 移动其他文件到 output/archive 目录
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def cleanup_output(output_dir: str = "output", keep_count: int = 10):
    """
    清理输出目录，保留最新文件
    
    Args:
        output_dir: 输出目录路径
        keep_count: 保留的最新文件数量
    """
    output_path = Path(output_dir)
    
    if not output_path.exists():
        print(f"✗ 输出目录不存在: {output_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"开始清理输出目录: {output_dir}")
    print(f"保留最新 {keep_count} 份文件")
    print(f"{'='*60}\n")
    
    # 创建 archive 目录
    archive_dir = output_path / "archive"
    archive_dir.mkdir(exist_ok=True)
    
    # 获取所有投标文件（.docx）
    files = []
    for file in output_path.glob("*.docx"):
        if file.is_file():
            files.append(file)
    
    print(f"📋 找到 {len(files)} 份投标文件")
    
    if not files:
        print("✗ 没有找到投标文件")
        return
    
    # 按修改时间排序（最新的在前）
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    # 保留最新的 keep_count 份文件
    keep_files = files[:keep_count]
    archive_files = files[keep_count:]
    
    print(f"\n📄 保留的最新 {keep_count} 份文件:")
    for i, file in enumerate(keep_files, 1):
        mod_time = datetime.fromtimestamp(file.stat().st_mtime)
        size_mb = file.stat().st_size / 1024 / 1024
        print(f"  {i}. {file.name:40} | {mod_time.strftime('%Y-%m-%d %H:%M:%S')} | {size_mb:.2f} MB")
    
    if archive_files:
        print(f"\n📦 移动到 archive 目录: {len(archive_files)} 份文件")
        for file in archive_files:
            dest = archive_dir / file.name
            try:
                # 检查文件是否存在（避免重复移动导致的错误）
                if file.exists():
                    # 如果目标文件已存在，添加时间戳避免冲突
                    if dest.exists():
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        dest = archive_dir / f"{file.stem}_{timestamp}{file.suffix}"
                    shutil.move(str(file), str(dest))
                    print(f"  ✓ 移动: {file.name}")
                else:
                    print(f"  ⚠️  跳过（文件不存在）: {file.name}")
            except Exception as e:
                print(f"  ✗ 移动失败: {file.name} - {e}")
    else:
        print(f"\n✅ 没有需要移动的文件")
    
    # 显示统计信息
    kept_size = sum(f.stat().st_size for f in keep_files) / 1024 / 1024
    archived_size = sum(f.stat().st_size for f in archive_files) / 1024 / 1024
    
    print(f"\n{'='*60}")
    print(f"📊 清理统计")
    print(f"{'='*60}")
    print(f"保留文件: {len(keep_files)} 份")
    print(f"保留大小: {kept_size:.2f} MB")
    print(f"移动文件: {len(archive_files)} 份")
    print(f"移动大小: {archived_size:.2f} MB")
    print(f"节省空间: {archived_size:.2f} MB")
    print(f"{'='*60}\n")
    
    print("✅ 清理完成！")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="清理输出目录，保留最新文件")
    parser.add_argument("--output-dir", type=str, default="output",
                       help="输出目录路径（默认: output）")
    parser.add_argument("--keep", type=int, default=10,
                       help="保留的最新文件数量（默认: 10）")
    parser.add_argument("--dry-run", action="store_true",
                       help="模拟运行，不实际移动文件")
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("\n🔍 模拟运行模式（不实际移动文件）")
    
    cleanup_output(args.output_dir, args.keep)
