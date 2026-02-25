#!/usr/bin/env python3
"""
测试 PDF 转图片功能
"""

from pathlib import Path
import sys

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from pdf_to_image_service import pdf_to_images

# 测试数据目录
data_dir = Path('/Users/zhangdongfang/workspace/bid-generator/data')

# 使用固定的 PDF 文件
pdf_path = Path('/Users/zhangdongfang/workspace/bid-generator/data/certificates/06、试验报告/18、三相多表位金属低压计量箱 型号：BXS2  （申请编号：20250102000442）(报告编号： .pdf')

if not pdf_path.exists():
    print(f"✗ PDF 文件不存在: {pdf_path}")
    sys.exit(1)

print(f"测试文件: {pdf_path.name}")
print(f"文件大小: {pdf_path.stat().st_size} bytes")
print()

# 创建输出目录
output_dir = Path('/tmp/test_pdf_to_image')
output_dir.mkdir(exist_ok=True)

# 转换 PDF
print("开始转换...")
images = pdf_to_images(pdf_path, output_dir, dpi=200, max_width=500)

print()
print(f"转换结果: {len(images)} 张图片")

if images:
    print("图片文件:")
    for img_path in images:
        size = img_path.stat().st_size
        print(f"  - {img_path.name} ({size} bytes)")
else:
    print("✗ 转换失败")
    sys.exit(1)

print()
print("✓ 测试通过")
