#!/usr/bin/env python3
"""
测试 .doc 到 .docx 的转换功能
"""

import sys
sys.path.insert(0, '/Users/zhangdongfang/workspace/bid-generator')

from pathlib import Path
import tempfile

# 测试转换
print("测试 .doc 到 .docx 转换功能")
print()

try:
    from docx2python import convert
    print("✓ docx2python 已安装")
except ImportError as e:
    print(f"✗ docx2python 未安装: {e}")
    print("安装命令: pip install docx2python")
    sys.exit(1)

# 测试文件
data_dir = Path('/Users/zhangdongfang/workspace/bid-generator/data')

# 查找 .doc 文件
doc_files = list(data_dir.rglob('*.doc'))[:3]

if not doc_files:
    print("没有找到 .doc 文件用于测试")
    sys.exit(1)

print(f"找到 {len(doc_files)} 个 .doc 文件用于测试")
print()

for i, doc_file in enumerate(doc_files, 1):
    print(f"测试 {i}: {doc_file.name}")
    
    try:
        # 转换
        with tempfile.TemporaryDirectory() as temp_dir:
            convert(doc_file, temp_dir)
            
            # 转换后的文件名
            output_filename = doc_file.stem + '.docx'
            output_path = Path(temp_dir) / output_filename
            
            # 检查文件是否存在
            if output_path.exists():
                size = output_path.stat().st_size
                print(f"  ✓ 转换成功: {output_filename} ({size} bytes)")
            else:
                print(f"  ✗ 转换失败: 文件不存在")
    except Exception as e:
        print(f"  ✗ 转换失败: {e}")
        import traceback
        traceback.print_exc()
    
    print()

print("=" * 60)
print("测试完成！")
