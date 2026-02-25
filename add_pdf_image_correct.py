"""
正确添加 PDF 转图片功能到 generator.py

分步骤修改，避免语法错误
"""

print("PDF 转图片功能 - 添加步骤")
print("=" * 60)

# 步骤1：在文件顶部添加导入
print("\n【步骤1：添加导入】")
print("在文件顶部的导入部分添加：")
print()
print("# 在现有的导入之后添加：")
print('try:')
print('    from pdf2image import convert_from_path')
print('    from PIL import Image as PILImage')
print('    PDF_TO_IMAGE_AVAILABLE = True')
print('except ImportError:')
print('    PDF_TO_IMAGE_AVAILABLE = False')
print('    PILImage = None')
print('    print("警告: pdf2image 或 Pillow 未安装，PDF转图片功能将不可用")')
print('    print("安装命令: pip install pdf2image Pillow")')

# 步骤2：在 _add_qualifications_v2 方法之后添加新方法
print("\n【步骤2：添加新方法】")
print("在 _add_qualifications_v2 方法结束后（doc.add_page_break() 之后）添加新方法")
print("新方法名称：_add_qualifications_with_images")
print()
print("完整的方法代码见下面的【完整代码】部分")

# 步骤3：修改调用方法的地方
print("\n【步骤3：修改调用方法】")
print("找到所有调用 _add_qualifications_v2 的地方：")
print("- generate_tech_bid 方法（约第100行）")
print("- generate_commercial_bid 方法（约第160行）")
print()
print("修改前：")
print('self._add_qualifications_v2(doc, matched_data.get("qualifications", []))')
print()
print("修改后：")
print('self._add_qualifications_with_images(doc, matched_data.get("qualifications", []), DATA_DIR)')

print()
print("=" * 60)
print("完整方法代码：")
print("=" * 60)
print("""
    def _add_qualifications_with_images(self, doc: Document, qualifications: List[Dict], data_dir: Path):
        '''
        添加企业资质（PDF转图片）
        
        优点：
        - 打印出来直接可以看到证书图片
        - 客户不需要任何操作
        - 投标文件看起来更专业
        
        缺点：
        - 需要安装额外库（pdf2image + Pillow + Ghostscript）
        - 文件会大一些
        '''
        if not PDF_TO_IMAGE_AVAILABLE or PILImage is None:
            # PDF转图片功能不可用，使用原方法
            self._add_qualifications_v2(doc, qualifications)
            return

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
            if cert.get('cert_file'):
                cert_path = data_dir / cert['cert_file']
                
                # 显示证书名称
                p = doc.add_paragraph()
                run = p.add_run(f"• {cert['name']}（{cert['level']}）")
                run.bold = True
                
                # 显示证书编号和有效期
                if cert.get('cert_no'):
                    p.add_paragraph(f"  证书编号：{cert['cert_no']}")
                if cert.get('valid_until'):
                    p.add_paragraph(f"  有效期至：{cert['valid_until']}")
                
                # PDF转图片并插入
                if cert_path.exists():
                    try:
                        import tempfile
                        with tempfile.TemporaryDirectory() as temp_dir:
                            # 转换PDF为图片（只转换第一页）
                            images = convert_from_path(
                                str(cert_path),
                                output_folder=temp_dir,
                                first_page_only=True,
                                dpi=200,  # 分辨率，200dpi打印效果较好
                                fmt='jpg'  # 输出为JPG格式
                                use_cropbox=True
                            )
                            
                            if images:
                                # 调整图片大小
                                img = PILImage.open(images[0])
                                img_width, img_height = img.size
                                
                                # 如果图片太宽，调整宽度
                                target_width = 500  # 目标宽度500像素
                                if img_width > target_width:
                                    ratio = target_width / img_width
                                    new_height = int(img_height * ratio)
                                    img = img.resize((target_width, new_height), PILImage.LANCZOS)
                                    
                                    # 保存调整后的图片
                                    img.save(images[0], quality=85)
                                
                                # 插入图片到Word文档
                                doc.add_paragraph()  # 空行
                                doc.add_picture(images[0], width=Inches(5.5))  # 宽度5.5英寸
                                doc.add_paragraph()  # 空行
                    except Exception as e:
                        # 如果转换失败，显示文件路径
                        p.add_paragraph(f"  证书文件：{cert['cert_file']}（图片转换失败：{str(e)}）")
                else:
                    p.add_paragraph(f"  证书文件：{cert['cert_file']}（文件不存在）")
        
        doc.add_paragraph()  # 证书之间空一行

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
            if cert.get('cert_file'):
                cert_path = data_dir / cert['cert_file']
                
                p = doc.add_paragraph()
                run = p.add_run(f"• {cert['name']}")
                run.bold = True
                
                if cert.get('cert_no'):
                    p.add_paragraph(f"  证书编号：{cert['cert_no']}")
                if cert.get('valid_until'):
                    p.add_paragraph(f"  有效期至：{cert['valid_until']}")
                
                # PDF转图片并插入
                if cert_path.exists():
                    try:
                        import tempfile
                        with tempfile.TemporaryDirectory() as temp_dir:
                            images = convert_from_path(
                                str(cert_path),
                                output_folder=temp_dir,
                                first_page_only=True,
                                dpi=200,
                                fmt='jpg',
                                use_cropbox=True
                            )
                            
                            if images:
                                img = PILImage.open(images[0])
                                img_width, img_height = img.size
                                
                                target_width = 500
                                if img_width > target_width:
                                    ratio = target_width / img_width
                                    new_height = int(img_height * ratio)
                                    img = img.resize((target_width, new_height), PILImage.LANCZOS)
                                    img.save(images[0], quality=85)
                                
                                doc.add_paragraph()
                                doc.add_picture(images[0], width=Inches(5.5))
                                doc.add_paragraph()
                    except Exception as e:
                        p.add_paragraph(f"  证书文件：{cert['cert_file']}（图片转换失败：{str(e)}）")
                else:
                    p.add_paragraph(f"  证书文件：{cert['cert_file']}（文件不存在）")
        
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
            if cert.get('cert_file'):
                cert_path = data_dir / cert['cert_file']
                
                p = doc.add_paragraph()
                run = p.add_run(f"• {cert['name']}")
                run.bold = True
                
                if cert.get('cert_no'):
                    p.add_paragraph(f"  证书编号：{cert['cert_no']}")
                if cert.get('valid_until'):
                    p.add_paragraph(f"  有效期至：{cert['valid_until']}")
                
                # PDF转图片并插入
                if cert_path.exists():
                    try:
                        import tempfile
                        with tempfile.TemporaryDirectory() as temp_dir:
                            images = convert_from_path(
                                str(cert_path),
                                output_folder=temp_dir,
                                first_page_only=True,
                                dpi=200,
                                fmt='jpg',
                                use_cropbox=True
                            )
                            
                            if images:
                                img = PILImage.open(images[0])
                                img_width, img_height = img.size
                                
                                target_width = 500
                                if img_width > target_width:
                                    ratio = target_width / img_width
                                    new_height = int(img_height * ratio)
                                    img = img.resize((target_width, new_height), PILImage.LANCZOS)
                                    img.save(images[0], quality=85)
                                
                                doc.add_paragraph()
                                doc.add_picture(images[0], width=Inches(5.5))
                                doc.add_paragraph()
                    except Exception as e:
                        p.add_paragraph(f"  证书文件：{cert['cert_file']}（图片转换失败：{str(e)}）")
                else:
                    p.add_paragraph(f"  证书文件：{cert['cert_file']}（文件不存在）")
        
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
            if cert.get('cert_file'):
                cert_path = data_dir / cert['cert_file']
                
                p = doc.add_paragraph()
                run = p.add_run(f"• {cert['name']}")
                run.bold = True
                
                # PDF转图片并插入
                if cert_path.exists():
                    try:
                        import tempfile
                        with tempfile.TemporaryDirectory() as temp_dir:
                            images = convert_from_path(
                                str(cert_path),
                                output_folder=temp_dir,
                                first_page_only=True,
                                dpi=200,
                                fmt='jpg',
                                use_cropbox=True
                            )
                            
                            if images:
                                img = PILImage.open(images[0])
                                img_width, img_height = img.size
                                
                                target_width = 500
                                if img_width > target_width:
                                    ratio = target_width / img_width
                                    new_height = int(img_height * ratio)
                                    img = img.resize((target_width, new_height), PILImage.LANCZOS)
                                    img.save(images[0], quality=85)
                                
                                doc.add_paragraph()
                                doc.add_picture(images[0], width=Inches(5.5))
                                doc.add_paragraph()
                    except Exception as e:
                        p.add_paragraph(f"  证书文件：{cert['cert_file']}（图片转换失败：{str(e)}）")
                else:
                    p.add_paragraph(f"  证书文件：{cert['cert_file']}（文件不存在）")
        
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
            
            # 插入剩余证书的前5个（图片形式）
            other_certs = [q for q in qualifications if q not in system_certs and q not in credit_certs and q not in honor_certs and q not in partner_certs]
            for cert in other_certs[:5]:
                if cert.get('cert_file'):
                    cert_path = data_dir / cert['cert_file']
                    if cert_path.exists():
                        try:
                            import tempfile
                            with tempfile.TemporaryDirectory() as temp_dir:
                                images = convert_from_path(
                                    str(cert_path),
                                    output_folder=temp_dir,
                                    first_page_only=True,
                                    dpi=200,
                                    fmt='jpg',
                                    use_cropbox=True
                                )
                                
                                if images:
                                    img = PILImage.open(images[0])
                                    img_width, img_height = img.size
                                    
                                    target_width = 500
                                    if img_width > target_width:
                                        ratio = target_width / img_width
                                        new_height = int(img_height * ratio)
                                        img = img.resize((target_width, new_height), PILImage.LANCZOS)
                                        img.save(images[0], quality=85)
                                    
                                    p = doc.add_paragraph()
                                    run = p.add_run(f"• {cert['name']}（{cert['level']}）")
                                    run.bold = True
                                    doc.add_paragraph()
                                    doc.add_picture(images[0], width=Inches(5.5))
                                    doc.add_paragraph()
                        except:
                            pass

        doc.add_page_break()
""")

print()
print("=" * 60)
print("添加顺序：")
print("1. 先添加导入（步骤1）")
print("2. 再添加新方法（步骤2）")
print("3. 最后修改调用方法的地方（步骤3）")
print()
print("注意：")
print("- 需要先安装 Ghostscript（brew install ghostscript）")
print("- 已经安装了 pdf2image 和 Pillow")
print("- 如果没有安装 Ghostscript，会自动使用原方法")
