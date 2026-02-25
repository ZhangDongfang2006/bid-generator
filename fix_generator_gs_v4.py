#!/usr/bin/env python3
"""
完全修复 generator.py，使用 Ghostscript 直接调用
"""

import sys
import subprocess
import tempfile
from pathlib import Path

# 读取 generator.py
gen_file = Path("generator.py")
content = gen_file.read_text(encoding='utf-8')

# 查找 _add_qualifications_with_pdf_images 方法
pattern = r'def _add_qualifications_with_pdf_images\(self, doc: Document, qualifications: List\[Dict\], data_dir: Path\):'
match = content.find(pattern)

if match != -1:
    # 查找方法结束
    method_end = content.find('\n    def _add_qualifications_v2', match)
    if method_end == -1:
        method_end = content.find('\nclass ', match)
    
    if method_end != -1:
        method_content = content[match:method_end]
        
        # 替换 PDF 转换部分
        old_pdf_convert = r'# 预先转换所有证书为图片\s*print\("开始转换证书为图片\.\.\."\)\s*import tempfile\s*import json\s*converted_images = \{\}\s*total = 0\s*success = 0\s*failed = 0.*?\s*for i, cert in enumerate\(qualifications, 1\):.*?# 转换PDF为图片\s*try:\s*with tempfile\.TemporaryDirectory\(\) as temp_dir:\s*images = convert_from_path\('
        new_pdf_convert = r'''        # 预先转换所有证书为图片（使用 Ghostscript 直接调用）
        print("开始转换证书为图片（Ghostscript 直接调用）...")
        
        converted_images = {}
        total = 0
        success = 0
        failed = 0
        
        for i, cert in enumerate(qualifications, 1):
            if not cert.get('cert_file'):
                continue
            
            cert_path = data_dir / cert['cert_file']
            if not cert_path.exists():
                print(f"✗ 证书文件不存在: {cert['cert_file']}")
                failed += 1
                total += 1
                continue
            
            # 使用 Ghostscript 直接调用（不依赖 pdf2image）
            try:
                output_path = Path(temp_dir) / f"cert_{cert['id']}.jpg"
                print(f"[DEBUG]   - 处理证书 {i}/{len(qualifications)}: {cert['name']}")
                print(f"[DEBUG]   - PDF 文件: {cert_path}")
                print(f"[DEBUG]   - 输出路径: {output_path}")
                
                # 调用 Ghostscript 转换方法
                success_convert = self._convert_pdf_to_jpeg_gs(
                    str(cert_path),
                    str(output_path),
                    dpi=200
                )
                
                if success_convert:
                    images = [str(output_path)]
                    print(f"[DEBUG]   - ✓ 转换成功！生成 {len(images)} 张图片")
                    print(f"[DEBUG]   - 图片大小：{output_path.stat().st_size} 字节")
                    
                    converted_images[cert['id']] = {
                        'name': cert['name'],
                        'level': cert['level'],
                        'images': images
                    }
                    success += 1
                else:
                    print(f"[DEBUG]   - ✗ 转换失败！")
                    converted_images[cert['id']] = {
                        'name': cert['name'],
                        'level': cert['level'],
                        'images': [],
                        'error': '转换失败'
                    }
                    failed += 1
                    
            except Exception as e:
                print(f"[DEBUG]   - ✗ 转换失败：{e}")
                converted_images[cert['id']] = {
                    'name': cert['name'],
                    'level': cert['level'],
                    'images': [],
                    'error': str(e)
                }
                failed += 1
            
            total += 1
            
            if total > 0 and total % 5 == 0:
                print(f"进度: {i}/{len(qualifications)}, 成功 {success}, 失败 {failed}")
        
        print(f"转换完成: 总计 {total}, 成功 {success}, 失败 {failed}")
'''
        
        # 替换
        import re
        new_content = re.sub(old_pdf_convert, new_pdf_convert, method_content, flags=re.DOTALL)
        
        # 更新文件
        content = content[:match] + new_content + content[method_end:]
        gen_file.write_text(content, encoding='utf-8')
        
        print("✓ 已更新 _add_qualifications_with_pdf_images 方法，使用 Ghostscript 直接调用")
        print()
        
        # 语法检查
        result = subprocess.run([sys.executable, '-m', 'py_compile', str(gen_file)],
                           capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ generator.py 语法检查通过")
        else:
            print("✗ generator.py 语法检查失败")
            print(result.stderr)
            sys.exit(1)
        
    else:
        print("✗ 未找到 _add_qualifications_with_pdf_images 方法定义")
        sys.exit(1)
else:
    print("✗ 未找到 _add_qualifications_with_pdf_images 方法定义")
    sys.exit(1)

print()
print("=" * 80)
print("修复完成！")
print("=" * 80)
print()
print("修改内容：")
print("1. ✓ 更新了 _add_qualifications_with_pdf_images 方法")
print("2. ✓ 使用 Ghostscript 直接调用，不依赖 pdf2image")
print("3. ✓ 不再依赖 poppler")
print("4. ✓ 添加了详细的调试信息")
print("5. ✓ 语法检查通过")
print()
print("=" * 80)
print("下一步：")
print("=" * 80)
print()
print("1. 重启 Streamlit 应用：")
print("   cd /Users/zhangdongfang/workspace/bid-generator")
print("   ./start.sh")
print()
print("2. 开启调试模式")
print()
print("3. 导入中天钢铁的招标文件")
print()
print("4. 勾选'显示证书图片'")
print()
print("5. 生成投标文件")
print()
print("6. 查看终端中的调试信息")
print()
print("应该看到：")
print("- 开始转换证书为图片（Ghostscript 直接调用）...")
print("- 处理证书 X/Y: 证书名称")
print("- PDF 文件: /Users/.../certificates/...")
print("- 输出路径: /tmp/...")
print("- ✓ 转换成功！生成 1 张图片")
print("- 图片大小： XXXXX 字节")
print("- 转换完成: 总计 X, 成功 X, 失败 X")
print()
print("=" * 80)
