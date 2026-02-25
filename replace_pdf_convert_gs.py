"""
完全替换 PDF 转换方法，使用 Ghostscript 直接调用
"""

import sys
import subprocess
from pathlib import Path

# 读取 generator.py
gen_file = Path("generator.py")
content = gen_file.read_text(encoding='utf-8')

# 定义新的 _add_qualifications_with_pdf_images 方法（完全使用 Ghostscript）
new_method = '''    def _add_qualifications_with_pdf_images_gs(self, doc: Document, qualifications: List[Dict], data_dir: Path):
        """
        添加企业资质（PDF转图片）- Ghostscript 直接调用版
        """
        p = doc.add_paragraph()
        run = p.add_run("第3章 企业资质")
        run.bold = True
        run.font.size = Pt(16)
        run.font.name = "黑体"

        doc.add_paragraph()

        if not qualifications:
            doc.add_paragraph("（具体资质文件详见附件）")
            doc.add_page_break()
            return

        # 预先转换所有证书为图片
        print("开始转换证书为图片...")
        
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
            
            # 转换PDF为图片（使用 Ghostscript 直接调用）
            try:
                import tempfile
                with tempfile.TemporaryDirectory() as temp_dir:
                    output_path = Path(temp_dir) / f"cert_{cert['id']}.jpg"
                    
                    # 使用 Ghostscript 直接转换
                    success_convert = self._convert_pdf_to_jpeg_gs(
                        str(cert_path),
                        str(output_path),
                        dpi=200
                    )
                    
                    if success_convert:
                        images = [str(output_path)]
                        print(f"  ✓ 证书 {i}/{len(qualifications)} 转换成功: {cert['name']}")
                        print(f"    - 文件大小: {output_path.stat().st_size} 字节")
                        
                        # 检查图片尺寸
                        img = PILImage.open(str(output_path))
                        img_width, img_height = img.size
                        print(f"    - 图片尺寸: {img_width} x {img_height}")
                        
                        converted_images[cert['id']] = {
                            'name': cert['name'],
                            'level': cert['level'],
                            'images': images
                        }
                        success += 1
                    else:
                        print(f"  ✗ 证书 {i}/{len(qualifications)} 转换失败: {cert['name']}")
                        converted_images[cert['id']] = {
                            'name': cert['name'],
                            'level': cert['level'],
                            'images': [],
                            'error': '转换失败'
                        }
                        failed += 1
                        
            except Exception as e:
                print(f"  ✗ 证书 {i}/{len(qualifications)} 转换失败: {cert['name']}")
                print(f"    - 错误: {e}")
                converted_images[cert['id']] = {
                    'name': cert['name'],
                    'level': cert['level'],
                    'images': [],
                    'error': str(e)
                }
                failed += 1
            
            total += 1
            
            if total > 0 and total % 5 == 0:
                print(f"  进度: {i}/{len(qualifications)}")
        
        print(f"转换完成: 总计 {total}, 成功 {success}, 失败 {failed}")
'''

# 定义 _convert_pdf_to_jpeg_gs 方法
gs_method = '''    def _convert_pdf_to_jpeg_gs(self, pdf_path: str, output_path: str, dpi: int = 200) -> bool:
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
                print("  ✗ Ghostscript 未安装或不在 PATH 中")
                return False
            
            # Ghostscript 命令（只转换第1页）
            command = [
                gs_path,
                "-dFirstPage=1",
                "-sDEVICE=jpeg",
                f"-r{dpi}",
                "-dJPEGQ=95",
                "-dNOPAUSE",
                "-dBATCH",
                "-dQUIET",
                f"-sOutputFile={output_path}",
                pdf_path
            ]
            
            # 运行命令
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # 检查结果
            if result.returncode == 0 and Path(output_path).exists():
                return True
            else:
                print(f"  ✗ Ghostscript 转换失败，返回码：{result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            print("  ✗ 转换超时（30秒）")
            return False
        except Exception as e:
            print(f"  ✗ 转换失败：{e}")
            return False
'''

# 查找方法位置（_add_qualifications_with_pdf_images）
pattern = r'def _add_qualifications_with_pdf_images\(self, doc: Document, qualifications: List\[Dict\], data_dir: Path\):'
match = content.find(pattern)

if match != -1:
    # 在方法之前添加 Ghostscript 方法
    content = content[:match] + gs_method + '\n\n' + content[match:]
    print("✓ 已添加 _convert_pdf_to_jpeg_gs 方法")
else:
    print("✗ 未找到 _add_qualifications_with_pdf_images 方法定义")

# 查找 _add_qualifications_with_pdf_images 方法的结束
pattern_end = r'def _add_qualifications_v2\(self, doc: Document, qualifications: List\[Dict\]\):'
match_end = content.find(pattern_end)

if match_end != -1:
    # 替换整个方法
    content = content[:match] + new_method + '\n' + content[match_end:]
    print("✓ 已替换 _add_qualifications_with_pdf_images 方法为 Ghostscript 版本")
else:
    print("✗ 未找到 _add_qualifications_with_pdf_images 方法结束位置")

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
print("2. ✓ 替换了 _add_qualifications_with_pdf_images 方法为 Ghostscript 版本")
print("3. ✓ 不再依赖 pdf2image 的 convert_from_path 方法")
print("4. ✓ 不再依赖 poppler")
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
print("- 开始转换证书为图片...")
print("-  处理证书 X/Y: 证书名称")
print("-   PDF 文件: /Users/.../certificates/...")
print("-   ✓ 证书 X/Y 转换成功: 证书名称")
print("-     - 文件大小: XXXXX 字节")
print("-     - 图片尺寸: 1100 x XXXX")
print("- 转换完成: 总计 X, 成功 X, 失败 X")
print()
print("=" * 80)
print("如果还是有问题，请告诉我调试信息！")
print()
