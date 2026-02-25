#!/usr/bin/env python3
"""
测试 generator.py 的导入和PDF转图片功能
"""

print("测试导入 generator.py...")

try:
    from generator import BidDocumentGenerator, PDF_TO_IMAGE_AVAILABLE, PILImage
    print("✓ 导入成功")
    print(f"  PDF_TO_IMAGE_AVAILABLE: {PDF_TO_IMAGE_AVAILABLE}")
    print(f"  PILImage: {PILImage}")
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    import sys
    sys.exit(1)

if not PDF_TO_IMAGE_AVAILABLE:
    print("✗ PDF转图片功能不可用")
    import sys
    sys.exit(1)

if PILImage is None:
    print("✗ PILImage 为 None")
    import sys
    sys.exit(1)

print("✓ PDF转图片功能可用")
print()

# 测试创建生成器
print("测试创建 BidDocumentGenerator...")
from pathlib import Path
templates_dir = Path('/Users/zhangdongfang/workspace/bid-generator/templates')
output_dir = Path('/Users/zhangdongfang/workspace/bid-generator/output')

try:
    generator = BidDocumentGenerator(templates_dir, output_dir)
    print("✓ 创建成功")
except Exception as e:
    print(f"✗ 创建失败: {e}")
    import traceback
    traceback.print_exc()
    import sys
    sys.exit(1)

print()
print("=" * 60)
print("所有测试通过！")
print("可以运行: streamlit run app.py")
