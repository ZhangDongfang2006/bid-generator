"""
自动安装和配置 PDF 转图片功能

这个脚本会：
1. 检查依赖
2. 提供安装命令
3. 修改 generator.py 添加 PDF 转图片功能
4. 在 app.py 中添加选项
"""

import sys
import os
import subprocess
from pathlib import Path


def check_dependencies():
    """检查依赖"""
    print("检查依赖...")
    print("-" * 60)
    
    dependencies = {
        'pdf2image': False,
        'Pillow': False,
        'Ghostscript': False
    }
    
    # 检查 pdf2image
    try:
        import pdf2image
        dependencies['pdf2image'] = True
        print("✓ pdf2image 已安装")
    except ImportError:
        print("✗ pdf2image 未安装")
        print("  安装命令: pip install pdf2image")
    
    # 检查 Pillow
    try:
        from PIL import Image as PILImage
        dependencies['Pillow'] = True
        print("✓ Pillow 已安装")
    except ImportError:
        print("✗ Pillow 未安装")
        print("  安装命令: pip install Pillow")
    
    # 检查 Ghostscript
    if os.name == 'posix':  # Mac/Linux
        try:
            result = subprocess.run(['which', 'gs'], capture_output=True, text=True)
            if result.returncode == 0:
                dependencies['Ghostscript'] = True
                print("✓ Ghostscript 已安装")
            else:
                print("✗ Ghostscript 未安装")
                print("  Mac 安装命令: brew install ghostscript")
                print("  Linux 安装命令: sudo apt-get install ghostscript")
        except FileNotFoundError:
            print("? 无法检测 Ghostscript")
            print("  Mac 安装命令: brew install ghostscript")
            print("  Linux 安装命令: sudo apt-get install ghostscript")
    elif os.name == 'nt':  # Windows
        # 检查 gs 是否在 PATH 中
        found = False
        for path in os.environ['PATH'].split(os.pathsep):
            gs_path = os.path.join(path, 'gs.exe')
            if os.path.exists(gs_path):
                dependencies['Ghostscript'] = True
                print(f"✓ Ghostscript 已安装 ({gs_path})")
                found = True
                break
        
        if not found:
            print("✗ Ghostscript 未安装")
            print("  下载地址: https://www.ghostscript.com/download/gs956w")
            print("  安装后确保 gs.exe 在系统 PATH 中")
    
    print()
    
    # 检查是否所有依赖都已安装
    all_installed = all(dependencies.values())
    if all_installed:
        print("✓ 所有依赖已就绪")
        print()
        return True
    else:
        print("✗ 需要安装以下依赖：")
        for dep, installed in dependencies.items():
            if not installed:
                print(f"  - {dep}")
        print()
        print("请运行以下命令安装依赖：")
        print("-" * 60)
        
        # 提供安装命令
        if not dependencies['Ghostscript']:
            if os.name == 'posix':
                print("# Mac/Linux 安装 Ghostscript")
                if sys.platform == 'darwin':
                    print("brew install ghostscript")
                else:
                    print("sudo apt-get install ghostscript")
                print()
        
        if not dependencies['pdf2image'] or not dependencies['Pillow']:
            print("# 安装 Python 依赖")
            print("pip install pdf2image Pillow")
            print()
        
        return False


def modify_generator_py():
    """修改 generator.py"""
    print("修改 generator.py...")
    print("-" * 60)
    
    generator_file = Path("/Users/zhangdongfang/workspace/bid-generator/generator.py")
    
    if not generator_file.exists():
        print(f"✗ 文件不存在: {generator_file}")
        return False
    
    # 读取文件
    with open(generator_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 检查是否已经添加了导入
    already_modified = False
    for i, line in enumerate(lines):
        if 'from pdf_to_image_service import pdf_to_images' in line:
            already_modified = True
            print("✓ 文件已经修改过，跳过")
            break
    
    if already_modified:
        return True
    
    # 添加导入
    new_lines = []
    inserted_import = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # 在导入部分添加 PDF 转图片的导入
        if not inserted_import and 'from docx.shared import' in line:
            # 在这个导入之后添加新导入
            new_lines.append("# PDF 转图片相关导入\n")
            new_lines.append("import tempfile\n")
            new_lines.append("from pdf_to_image_service import pdf_to_images, convert_certificates\n")
            new_lines.append("\n")
            inserted_import = True
    
    # 写回文件
    with open(generator_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✓ 已添加 PDF 转图片导入")
    return True


def modify_app_py():
    """修改 app.py 添加选项"""
    print("修改 app.py...")
    print("-" * 60)
    
    app_file = Path("/Users/zhangdongfang/workspace/bid-generator/app.py")
    
    if not app_file.exists():
        print(f"✗ 文件不存在: {app_file}")
        return False
    
    # 读取文件
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经添加了选项
    if 'show_cert_images' in content:
        print("✓ 文件已经修改过，跳过")
        return True
    
    # 查找需要修改的位置
    # 在步骤3 匹配资料部分添加选项
    target_section = "交付天数 = st.number_input(\"交货期（天）\", min_value=1, max_value=365, value=30)"
    
    if target_section not in content:
        print(f"✗ 找不到目标位置: {target_section}")
        return False
    
    # 添加选项
    new_section = f'''{target_section}
    warranty_period = st.text_input("质保期", value="一年")

    # 【新增】证书显示选项
    st.markdown("---")
    show_cert_images = st.checkbox("显示证书图片", value=False, key="show_cert_images",
                                   help="选中后，证书 PDF 会转换为图片并在投标文件中显示")
'''
    
    # 替换
    new_content = content.replace(target_section, new_section)
    
    # 写回文件
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✓ 已添加证书显示选项")
    return True


def modify_generator_add_image_method():
    """在 generator.py 中添加带图片的资质方法"""
    print("在 generator.py 中添加带图片的资质方法...")
    print("-" * 60)
    
    generator_file = Path("/Users/zhangdongfang/workspace/bid-generator/generator.py")
    
    if not generator_file.exists():
        print(f"✗ 文件不存在: {generator_file}")
        return False
    
    # 读取文件
    with open(generator_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经添加了方法
    if 'def _add_qualifications_with_images' in content:
        print("✓ 方法已经存在，跳过")
        return True
    
    # 找到 _add_qualifications_v2 方法的结束位置
    # 方法以 "    doc.add_page_break()" 结束
    target = '    doc.add_page_break()\n\n    def _add_performance('
    
    if target not in content:
        print("✗ 找不到目标位置")
        return False
    
    # 新方法代码
    new_method = '''    def _add_qualifications_with_images(self, doc: Document, qualifications: List[Dict],
                                                  data_dir: Path, show_images: bool = False):
        """
        添加企业资质（支持 PDF 转图片）
        
        Args:
            doc: Word 文档对象
            qualifications: 资质列表
            data_dir: 数据目录
            show_images: 是否显示证书图片
        """
        if show_images:
            # 使用图片版本
            self._add_qualifications_with_pdf_images(doc, qualifications, data_dir)
        else:
            # 使用原始版本
            self._add_qualifications_v2(doc, qualifications)

    def _add_qualifications_with_pdf_images(self, doc: Document, qualifications: List[Dict],
                                                  data_dir: Path):
        """
        添加企业资质（PDF 转图片）
        
        优点：
        - 打印出来直接可以看到证书图片
        - 客户不需要任何操作
        - 投标文件看起来更专业
        
        缺点：
        - 需要安装额外库（pdf2image + Pillow + Ghostscript）
        - 文件会大一些
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

        # 转换所有证书为图片
        converted_images = convert_certificates(qualifications, data_dir, data_dir / "converted_certs")
        converted_images.mkdir(parents=True, exist_ok=True)

        # 3.1 体系认证证书
        p = doc.add_paragraph()
        run = p.add_run("3.1 体系认证证书")
        run.bold = True
        run.font.size = Pt(14)
        run.font.name = "宋体"

        doc.add_paragraph()

        # 过滤出体系认证
        system_certs = [q for q in qualifications if "体系" in q.get("name", "") or "认证" in q.get("name", "")]

        for cert in system_certs[:10]:  # 最多显示10个
            cert_id = str(cert['id'])
            images = converted_images.get(cert_id, {}).get('images', [])
            
            # 显示证书名称
            p = doc.add_paragraph()
            run = p.add_run(f"• {cert['name']}（{cert['level']}）")
            run.bold = True
            
            # 显示证书编号和有效期
            if cert.get('cert_no'):
                p.add_paragraph(f"  证书编号：{cert['cert_no']}")
            if cert.get('valid_until'):
                p.add_paragraph(f"  有效期至：{cert['valid_until']}")
            
            # 插入图片
            if images:
                for img_path in images:
                    try:
                        doc.add_paragraph()
                        doc.add_picture(str(img_path), width=Inches(5.5))
                        doc.add_paragraph()
                    except:
                        p.add_paragraph(f"  （图片插入失败）")
            elif cert.get('cert_file'):
                p.add_paragraph(f"  证书文件：{cert['cert_file']}（图片转换失败）")
        
        doc.add_paragraph()

        # 3.2 信用等级证书
        p = doc.add_paragraph()
        run = p.add_run("3.2 信用等级证书")
        run.bold = True
        run.font.size = Pt(14)
        run.font.name = "宋体"

        doc.add_paragraph()

        # 过滤出信用等级
        credit_certs = [q for q in qualifications if "AAA" in q.get("name", "") or "信用" in q.get("name", "")]

        for cert in credit_certs[:10]:
            cert_id = str(cert['id'])
            images = converted_images.get(cert_id, {}).get('images', [])
            
            p = doc.add_paragraph()
            run = p.add_run(f"• {cert['name']}")
            run.bold = True
            
            if cert.get('cert_no'):
                p.add_paragraph(f"  证书编号：{cert['cert_no']}")
            if cert.get('valid_until'):
                p.add_paragraph(f"  有效期至：{cert['valid_until']}")
            
            if images:
                for img_path in images:
                    try:
                        doc.add_paragraph()
                        doc.add_picture(str(img_path), width=Inches(5.5))
                        doc.add_paragraph()
                    except:
                        p.add_paragraph(f"  （图片插入失败）")
            elif cert.get('cert_file'):
                p.add_paragraph(f"  证书文件：{cert['cert_file']}（图片转换失败）")
        
        doc.add_paragraph()

        # 3.3 重点荣誉证书
        p = doc.add_paragraph()
        run = p.add_run("3.3 重点荣誉证书")
        run.bold = True
        run.font.size = Pt(14)
        run.font.name = "宋体"

        doc.add_paragraph()

        # 过滤出省级荣誉
        honor_certs = [q for q in qualifications if "重点" in q.get("name", "") or "质量奖" in q.get("name", "")]

        for cert in honor_certs[:10]:
            cert_id = str(cert['id'])
            images = converted_images.get(cert_id, {}).get('images', [])
            
            p = doc.add_paragraph()
            run = p.add_run(f"• {cert['name']}")
            run.bold = True
            
            if cert.get('cert_no'):
                p.add_paragraph(f"  证书编号：{cert['cert_no']}")
            if cert.get('valid_until'):
                p.add_paragraph(f"  有效期至：{cert['valid_until']}")
            
            if images:
                for img_path in images:
                    try:
                        doc.add_paragraph()
                        doc.add_picture(str(img_path), width=Inches(5.5))
                        doc.add_paragraph()
                    except:
                        p.add_paragraph(f"  （图片插入失败）")
            elif cert.get('cert_file'):
                p.add_paragraph(f"  证书文件：{cert['cert_file']}（图片转换失败）")
        
        doc.add_paragraph()

        # 3.4 合作伙伴证书
        p = doc.add_paragraph()
        run = p.add_run("3.4 合作伙伴证书")
        run.bold = True
        run.font.size = Pt(14)
        run.font.name = "宋体"

        doc.add_paragraph()

        # 过滤出合作伙伴
        partner_certs = [q for q in qualifications if "授权" in q.get("name", "") or "合作" in q.get("name", "")]

        for cert in partner_certs[:10]:
            cert_id = str(cert['id'])
            images = converted_images.get(cert_id, {}).get('images', [])
            
            p = doc.add_paragraph()
            run = p.add_run(f"• {cert['name']}")
            run.bold = True
            
            if images:
                for img_path in images:
                    try:
                        doc.add_paragraph()
                        doc.add_picture(str(img_path), width=Inches(5.5))
                        doc.add_paragraph()
                    except:
                        p.add_paragraph(f"  （图片插入失败）")
            elif cert.get('cert_file'):
                p.add_paragraph(f"  证书文件：{cert['cert_file']}（图片转换失败）")
        
        doc.add_paragraph()

        # 3.5 其他证书
        remaining = len(qualifications) - len(system_certs) - len(credit_certs) - len(honor_certs) - len(partner_certs)
        if remaining > 0:
            p = doc.add_paragraph()
            run = p.add_run("3.5 其他证书")
            run.bold = True
            run.font.size = Pt(14)
            run.font.name = "宋体"

            doc.add_paragraph()
            doc.add_paragraph(f"（其他证书共 {remaining} 项，详见附件）")
            
            # 显示前 5 个其他证书的图片
            other_certs = [q for q in qualifications if q not in system_certs and q not in credit_certs
                            and q not in honor_certs and q not in partner_certs]
            for cert in other_certs[:5]:
                cert_id = str(cert['id'])
                images = converted_images.get(cert_id, {}).get('images', [])
                
                if images:
                    p = doc.add_paragraph()
                    run = p.add_run(f"• {cert['name']}（{cert['level']}）")
                    run.bold = True
                    doc.add_paragraph()
                    for img_path in images:
                        try:
                            doc.add_picture(str(img_path), width=Inches(5.5))
                            doc.add_paragraph()
                        except:
                            pass

        doc.add_page_break()
'''
    
    # 在 _add_performance 方法之前添加
    target = '    def _add_performance(self, doc: Document, cases: List[Dict]):'
    
    if target not in content:
        print("✗ 找不到目标位置")
        return False
    
    # 替换
    new_content = content.replace(target, new_method + '\n' + target)
    
    # 写回文件
    with open(generator_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✓ 已添加带图片的资质方法")
    return True


def test_pdf_conversion():
    """测试 PDF 转换"""
    print("测试 PDF 转换...")
    print("-" * 60)
    
    from pdf_to_image_service import convert_certificates
    from pathlib import Path
    import json
    
    data_dir = Path("/Users/zhangdongfang/workspace/bid-generator/data")
    
    # 读取资质数据
    with open(data_dir / 'qualifications.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 只测试前 3 个证书
    test_certs = data.get('qualifications', [])[:3]
    
    if not test_certs:
        print("✗ 没有找到资质数据")
        return False
    
    # 转换
    print(f"测试转换 {len(test_certs)} 个证书...")
    results = convert_certificates(test_certs, data_dir, data_dir / "test_output")
    
    print()
    print("转换结果：")
    success_count = 0
    for cert_id, result in results.items():
        if result.get('images'):
            success_count += 1
            print(f"  ✓ {result['name']}: {len(result['images'])} 张图片")
        else:
            error = result.get('error', '未知错误')
            print(f"  ✗ {result['name']}: {error}")
    
    print()
    if success_count == len(test_certs):
        print("✓ 所有证书转换成功")
        return True
    else:
        print(f"✗ {len(test_certs) - success_count} 个证书转换失败")
        return False


def main():
    """主函数"""
    print("PDF 转图片功能 - 自动安装和配置")
    print("=" * 60)
    print()
    
    # 步骤1：检查依赖
    print("【步骤1】检查依赖")
    print("-" * 60)
    deps_ok = check_dependencies()
    print()
    
    if not deps_ok:
        print("=" * 60)
        print("需要安装依赖")
        print("=" * 60)
        print()
        print("安装依赖后，请再次运行此脚本")
        print("  python auto_install_pdf_images.py")
        print()
        return False
    
    # 步骤2：修改文件
    print("【步骤2】修改文件")
    print("-" * 60)
    
    # 修改 generator.py
    if not modify_generator_py():
        print("✗ 修改 generator.py 失败")
        return False
    
    # 修改 generator.py 添加新方法
    if not modify_generator_add_image_method():
        print("✗ 添加图片方法失败")
        return False
    
    # 修改 app.py
    if not modify_app_py():
        print("✗ 修改 app.py 失败")
        return False
    
    print()
    print("✓ 文件修改完成")
    print()
    
    # 步骤3：测试
    print("【步骤3】测试 PDF 转换")
    print("-" * 60)
    
    if not test_pdf_conversion():
        print("✗ PDF 转换测试失败")
        return False
    
    print()
    print("=" * 60)
    print("✓ PDF 转图片功能安装和配置完成")
    print("=" * 60)
    print()
    print("使用方法：")
    print("1. 重启 Streamlit 应用")
    print("2. 在步骤3 匹配资料部分，勾选 '显示证书图片'")
    print("3. 生成投标文件")
    print("4. 查看第3章企业资质部分")
    print()
    print("效果：")
    print("- 证书 PDF 会自动转换为图片")
    print("- 图片会插入到投标文件中")
    print("- 打印出来直接可以看到证书图片")
    print("- 客户不需要任何操作")
    print()
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
