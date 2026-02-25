"""
PDF 转图片服务

这个服务负责将证书 PDF 转换为图片，
然后在投标文件中插入图片。
"""

import sys
import os
from pathlib import Path
import tempfile
from datetime import datetime


def pdf_to_images(pdf_path: Path, output_dir: Path, dpi: int = 200, max_width: int = 500):
    """
    将 PDF 转换为图片
    
    Args:
        pdf_path: PDF 文件路径
        output_dir: 输出目录
        dpi: 分辨率（默认 200）
        max_width: 最大宽度（像素，默认 500）
    
    Returns:
        转换后的图片路径列表
    """
    try:
        from pdf2image import convert_from_path
        from PIL import Image as PILImage
    except ImportError as e:
        print(f"✗ 导入错误: {e}")
        print("请安装: pip install pdf2image Pillow")
        print("还需要安装 Ghostscript")
        return []
    
    images = []
    
    try:
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 转换 PDF 为图片（只转换第一页）
            # 不使用 output_folder，直接返回 PIL Image 对象
            converted = convert_from_path(
                str(pdf_path),
                first_page=1,
                last_page=1,
                dpi=dpi,
                fmt='jpg',
                use_cropbox=True
            )

            if not converted:
                print(f"✗ PDF 转换失败: {pdf_path.name}")
                return []

            # 调整图片大小并保存
            for img in converted:
                img_width, img_height = img.size

                # 如果图片太宽，调整宽度
                if img_width > max_width:
                    ratio = max_width / img_width
                    new_height = int(img_height * ratio)
                    img = img.resize((max_width, new_height), PILImage.LANCZOS)

                # 保存到输出目录
                output_filename = f"{pdf_path.stem}_{len(images) + 1}.jpg"
                output_path = output_dir / output_filename
                img.save(output_path, quality=85)
                images.append(output_path)
                
            print(f"✓ PDF 转换成功: {pdf_path.name} -> {len(images)} 张图片")
            
    except Exception as e:
        print(f"✗ PDF 转换失败: {pdf_path.name} - {e}")
        import traceback
        traceback.print_exc()
    
    return images


def convert_certificates(qualifications: list, data_dir: Path, output_dir: Path):
    """
    批量转换证书 PDF 为图片
    
    Args:
        qualifications: 资质列表
        data_dir: 数据目录
        output_dir: 输出目录
    
    Returns:
        转换结果字典 {证书ID: 图片路径列表}
    """
    results = {}
    total = 0
    success = 0
    failed = 0
    
    print(f"开始转换 {len(qualifications)} 个证书...")
    
    for i, cert in enumerate(qualifications, 1):
        cert_file = cert.get('cert_file')
        if not cert_file:
            continue
        
        cert_path = data_dir / cert_file
        if not cert_path.exists():
            print(f"✗ 证书文件不存在: {cert_file}")
            failed += 1
            continue
        
        # 转换 PDF 为图片
        images = pdf_to_images(cert_path, output_dir)
        
        if images:
            results[cert['id']] = {
                'name': cert['name'],
                'level': cert['level'],
                'images': images
            }
            success += 1
        else:
            results[cert['id']] = {
                'name': cert['name'],
                'level': cert['level'],
                'images': [],
                'error': '转换失败'
            }
            failed += 1
        
        total += 1
        
        if total > 0 and total % 5 == 0:
            print(f"进度: {i}/{len(qualifications)}")
    
    print()
    print(f"转换完成: 总计 {total}, 成功 {success}, 失败 {failed}")
    
    return results


if __name__ == "__main__":
    print("PDF 转图片服务")
    print("=" * 60)
    print()
    
    # 检查依赖
    try:
        from pdf2image import convert_from_path
        print("✓ pdf2image 已安装")
    except ImportError:
        print("✗ pdf2image 未安装")
        print("  安装命令: pip install pdf2image")
        sys.exit(1)
    
    try:
        from PIL import Image as PILImage
        print("✓ Pillow 已安装")
    except ImportError:
        print("✗ Pillow 未安装")
        print("  安装命令: pip install Pillow")
        sys.exit(1)
    
    # 检查 Ghostscript
    if os.name == 'posix':  # Mac/Linux
        try:
            result = os.system('which gs > /dev/null 2>&1')
            if result == 0:
                print("✓ Ghostscript 已安装")
            else:
                print("✗ Ghostscript 未安装")
                print("  Mac 安装命令: brew install ghostscript")
                print("  Linux 安装命令: sudo apt-get install ghostscript")
        except:
            print("? 无法检测 Ghostscript")
    elif os.name == 'nt':  # Windows
        if 'gs' in os.environ['PATH'].lower():
            print("✓ Ghostscript 已安装（在 PATH 中）")
        else:
            print("✗ Ghostscript 未安装")
            print("  下载地址: https://www.ghostscript.com/download/gs956w")
    
    print()
    print("=" * 60)
    print("所有依赖已就绪，PDF 转图片功能可用")
    print()
    print("使用方法：")
    print("  在 generator.py 中导入此服务")
    print("  调用 convert_certificates() 方法")
    print()
    print("或使用命令行测试：")
    print("  python pdf_to_image_service.py test")
    print()
    
    # 测试模式
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        print("测试模式")
        print("-" * 60)
        
        data_dir = Path('/Users/zhangdongfang/workspace/bid-generator/data')
        output_dir = Path('/Users/zhangdongfang/workspace/bid-generator/output/converted_certs')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 读取资质数据
        import json
        with open(data_dir / 'qualifications.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 只转换前 5 个证书
        test_certs = data.get('qualifications', [])[:5]
        
        results = convert_certificates(test_certs, data_dir, output_dir)
        
        print()
        print("转换结果：")
        for cert_id, result in results.items():
            print(f"  证书 {cert_id}: {result['name']} - {len(result['images'])} 张图片")
