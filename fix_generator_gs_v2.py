"""
修复 generator.py，使用 Ghostscript 直接调用
"""

import sys
from pathlib import Path

# 读取 generator.py
gen_file = Path("generator.py")
content = gen_file.read_text(encoding='utf-8')

# 1. 添加 subprocess 和 tempfile 导入
if 'import subprocess' not in content:
    # 在文件开头添加导入
    import_lines = [
        'import subprocess',
        'import tempfile'
    ]
    import_section = '\n'.join(import_lines)
    
    # 在第一个 import 语句之后添加
    first_import = content.find('from pathlib import')
    if first_import != -1:
        content = content[:first_import] + import_section + '\n' + content[first_import:]

# 2. 添加 Ghostscript 转换方法
gs_method = '''
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

# 3. 找到 _add_qualifications_with_pdf_images 方法的位置
pattern = r'def _add_qualifications_with_pdf_images\(self, doc: Document, qualifications: List\[Dict\], data_dir: Path\):'
match = content.find(pattern)

if match != -1:
    # 在方法之前添加 Ghostscript 转换方法
    content = content[:match] + gs_method + '\n' + content[match:]
    print("✓ 已添加 Ghostscript 转换方法")
else:
    print("✗ 未找到 _add_qualifications_with_pdf_images 方法定义")

# 4. 更新 _add_qualifications_with_pdf_images 方法，使用 Ghostscript
old_pdf_convert = '''            # 转换PDF为图片
            try:
                print(f"[DEBUG]   - 开始转换 PDF...")
                with tempfile.TemporaryDirectory() as temp_dir:
                    # 【修复】使用 first_page 参数代替 first_page_only
                    images = convert_from_path(
                        str(cert_path),
                        output_folder=temp_dir,
                        first_page=1,  # 【修复】从第1页开始（等同于 first_page_only）
                        last_page=1,  # 【修复】只转换第1页
                        dpi=200,  # 分辨率，200dpi打印效果较好
                        fmt='jpg',  # 输出为JPG格式
                        use_cropbox=True
                    )'''

new_pdf_convert = '''            # 转换PDF为图片（使用 Ghostscript 直接调用）
            try:
                print(f"[DEBUG]   - 开始转换 PDF...")
                output_path = Path(temp_dir) / f"cert_{cert['id']}.jpg"
                print(f"[DEBUG]   - 输出路径：{output_path}")
                
                success = self._convert_pdf_to_jpeg_gs(
                    str(cert_path),
                    str(output_path),
                    dpi=200
                )
                
                if success:
                    images = [str(output_path)]
                    print(f"[DEBUG]   - ✓ 转换成功！生成 {len(images)} 张图片")
                else:
                    images = []
                    print(f"[DEBUG]   - ✗ 转换失败")
            '''

content = content.replace(old_pdf_convert, new_pdf_convert)
print("✓ 已更新 _add_qualifications_with_pdf_images 方法，使用 Ghostscript 直接调用")

# 5. 保存文件
gen_file.write_text(content, encoding='utf-8')
print(f"✓ 已更新 {gen_file}")

# 6. 验证语法
import subprocess
result = subprocess.run([sys.executable, '-m', 'py_compile', str(gen_file)],
                       capture_output=True, text=True)

if result.returncode == 0:
    print("✓ generator.py 语法检查通过")
else:
    print("✗ generator.py 语法检查失败")
    print(result.stderr)
