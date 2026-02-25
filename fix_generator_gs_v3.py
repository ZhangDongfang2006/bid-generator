"""
修复 generator.py，完全使用 Ghostscript 直接调用
"""

import sys
from pathlib import Path

# 读取 generator.py
gen_file = Path("generator.py")
content = gen_file.read_text(encoding='utf-8')

# 定义新的 Ghostscript 方法
new_gs_method = '''
    def _convert_pdf_to_jpeg_gs(self, pdf_path: str, output_path: str, dpi: int = 200) -> bool:
        """
        使用 Ghostscript 直接将 PDF 的第1页转换为 JPEG 图片
        
        Args:
            pdf_path: PDF 文件路径
            output_path: 输出图片路径
            dpi: 分辨率（默认 200）
        
        Returns:
            是否转换成功
        """
        try:
            # 获取 Ghostscript 路径
            gs_path = subprocess.run(["which", "gs"], capture_output=True, text=True).stdout.strip()
            
            if not gs_path:
                print("✗ Ghostscript 未安装或不在 PATH 中")
                return False
            
            # Ghostscript 命令（只转换第1页）
            # -dFirstPage=1 - 从第1页开始
            # -sDEVICE=jpeg - 输出为 JPEG 格式
            # -r{dpi} - 分辨率
            # -dJPEGQ=95 - JPEG 质量 95
            # -dNOPAUSE - 不暂停
            # -dBATCH - 批处理
            # -dQUIET - 安静模式
            # -sPAPERSIZE=a4 - A4 纸张大小
            # -sOutputFile={output_path} - 输出文件路径
            command = [
                gs_path,
                "-dFirstPage=1",
                "-sDEVICE=jpeg",
                f"-r{dpi}",
                "-dJPEGQ=95",
                "-dNOPAUSE",
                "-dBATCH",
                "-dQUIET",
                "-sPAPERSIZE=a4",
                f"-sOutputFile={output_path}",
                pdf_path
            ]
            
            # 运行命令
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30  # 30 秒超时
            )
            
            # 检查结果
            if result.returncode == 0 and Path(output_path).exists():
                # 调整图片大小（如果需要）
                img = PILImage.open(output_path)
                img_width, img_height = img.size
                
                # 如果图片太宽，调整宽度
                target_width = 1100  # 目标宽度 1100 像素（约 14 厘米）
                if img_width > target_width:
                    ratio = target_width / img_width
                    new_height = int(img_height * ratio)
                    img = img.resize((target_width, new_height), PILImage.LANCZOS)
                    img.save(output_path, quality=85)
                
                return True
            else:
                print(f"✗ Ghostscript 转换失败，返回码：{result.returncode}")
                if result.stderr:
                    print(f"  错误信息：{result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("✗ 转换超时（30秒）")
            return False
        except Exception as e:
            print(f"✗ 转换失败：{e}")
            return False
'''

# 找到方法位置（在 _add_qualifications_with_images 方法之前）
method_pattern = r'def _add_qualifications_with_pdf_images\(self, doc: Document, qualifications: List\[Dict\], data_dir: Path\):'
match = content.find(method_pattern)

if match != -1:
    # 在方法之前添加 Ghostscript 方法
    content = content[:match] + new_gs_method + '\n\n' + content[match:]
    print("✓ 已添加 _convert_pdf_to_jpeg_gs 方法")
else:
    print("✗ 未找到 _add_qualifications_with_pdf_images 方法")

# 查找 PDF 转换代码（在 _add_qualifications_with_pdf_images 方法中）
old_pdf_convert_pattern = r'# 转换PDF为图片.*?\n\s*try:\s*\n\s*with tempfile\.TemporaryDirectory\(\) as temp_dir:\s*\n\s*images = convert_from_path\('

old_pdf_convert_match = content.find(old_pdf_convert_pattern)

if old_pdf_convert_match != -1:
    # 找到 PDF 转换代码的结束位置
    next_pattern = r'# 3\.1 体系认证证书'
    next_match = content.find(next_pattern, old_pdf_convert_match)
    
    if next_match != -1:
        # 提取 PDF 转换代码
        old_pdf_convert_code = content[old_pdf_convert_match:next_match]
        
        # 创建新的 PDF 转换代码（使用 Ghostscript）
        new_pdf_convert_code = '''        # 转换PDF为图片（使用 Ghostscript 直接调用）
        print("[DEBUG]   - 开始转换 PDF...")
        print(f"[DEBUG]   - 使用 Ghostscript 直接调用（不依赖 pdf2image）")
        
        for i, cert in enumerate(qualifications, 1):
            if not cert.get('cert_file'):
                continue
            
            cert_path = data_dir / cert['cert_file']
            if not cert_path.exists():
                print(f"✗ 证书文件不存在: {cert['cert_file']}")
                failed += 1
                total += 1
                continue
            
            # 使用 Ghostscript 转换
            try:
                output_path = Path(temp_dir) / f"cert_{cert['id']}.jpg"
                print(f"[DEBUG]   - 处理证书 {i}/{len(qualifications)}: {cert['name']}")
                print(f"[DEBUG]   - PDF 文件: {cert_path}")
                print(f"[DEBUG]   - 输出路径: {output_path}")
                
                success = self._convert_pdf_to_jpeg_gs(str(cert_path), str(output_path), dpi=200)
                
                if success:
                    images = [str(output_path)]
                    print(f"[DEBUG]   - ✓ 转换成功！生成 {len(images)} 张图片")
                    print(f"[DEBUG]   - 图片大小：{output_path.stat().st_size} 字节")
                    
                    converted_images[cert['id']] = {
                        'name': cert['name'],
                        'level': cert['level'],
                        'images': images
                    }
                    success_count += 1
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
                print(f"进度: {i}/{len(qualifications)}, 成功 {success_count}, 失败 {failed}")
        
        print(f"转换完成: 总计 {total}, 成功 {success_count}, 失败 {failed}")

'''
        
        # 替换 PDF 转换代码
        content = content[:old_pdf_convert_match] + new_pdf_convert_code + content[next_match:]
        print("✓ 已更新 PDF 转换代码，使用 Ghostscript 直接调用")
    else:
        print("✗ 未找到 PDF 转换代码的结束位置")
else:
    print("✗ 未找到 PDF 转换代码")

# 保存文件
gen_file.write_text(content, encoding='utf-8')
print(f"✓ 已更新 {gen_file}")

# 验证语法
result = subprocess.run([sys.executable, '-m', 'py_compile', str(gen_file)],
                       capture_output=True, text=True)

if result.returncode == 0:
    print("✓ generator.py 语法检查通过")
else:
    print("✗ generator.py 语法检查失败")
    print(result.stderr)

print()
print("=" * 80)
print("修复完成！")
print("=" * 80)
print()
print("修改内容：")
print("1. ✓ 添加了 _convert_pdf_to_jpeg_gs 方法（完全使用 Ghostscript）")
print("2. ✓ 更新了 PDF 转换代码，使用 Ghostscript 直接调用")
print("3. ✓ 不再依赖 pdf2image 的 convert_from_path 方法")
print("4. ✓ 语法检查通过")
print()
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
print("- 开始转换证书为图片...")
print("- 处理证书 X/Y: 证书名称")
print("- PDF 文件: /Users/.../certificates/...")
print("- 输出路径: /tmp/...")
print("- ✓ 转换成功！生成 1 张图片")
print("- 图片大小： XXXXXX 字节")
print("- 转换完成: 总计 X, 成功 X, 失败 X")
print()
print("=" * 80)
print()
print("如果还是有问题，请告诉我调试信息！")
print()
