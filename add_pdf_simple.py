"""
证书PDF插入功能（最简单版本）

这个脚本可以直接复制到 generator.py 中使用
"""

def _add_qualifications_with_pdf(self, doc: Document, qualifications: List[Dict], data_dir: Path):
    """
    添加企业资质（带PDF插入功能）

    Args:
        doc: Word 文档对象
        qualifications: 资质列表
        data_dir: 数据目录
    """
    p = doc.add_paragraph()
    run = p.add_run("第3章 企业资质")
    run.bold = True
    run.font.size = Pt(16)
    run.font.name = "黑体"

    doc.add_paragraph()

    if not qualifications:
        doc.add_paragraph("（具体资质详见附件）")
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
            
            # 【新增】直接插入PDF文件
            if cert_path.exists():
                try:
                    doc.add_paragraph()  # 空行
                    doc.add_picture(str(cert_path), width=Inches(6.0))  # 插入PDF，宽度6英寸
                    doc.add_paragraph()  # 空行
                except Exception as e:
                    # 如果插入失败，显示文件路径
                    p.add_paragraph(f"  证书文件详见附件：{cert['cert_file']}")
                    p.add_paragraph(f"  （插入失败：{str(e)}）")
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
            
            # 显示证书编号和有效期
            if cert.get('cert_no'):
                p.add_paragraph(f"  证书编号：{cert['cert_no']}")
            if cert.get('valid_until'):
                p.add_paragraph(f"  有效期至：{cert['valid_until']}")
            
            # 插入PDF文件
            if cert_path.exists():
                try:
                    doc.add_paragraph()
                    doc.add_picture(str(cert_path), width=Inches(6.0))
                    doc.add_paragraph()
                except Exception as e:
                    p.add_paragraph(f"  证书文件详见附件：{cert['cert_file']}")
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
            
            # 显示证书编号和有效期
            if cert.get('cert_no'):
                p.add_paragraph(f"  证书编号：{cert['cert_no']}")
            if cert.get('valid_until'):
                p.add_paragraph(f"  有效期至：{cert['valid_until']}")
            
            # 插入PDF文件
            if cert_path.exists():
                try:
                    doc.add_paragraph()
                    doc.add_picture(str(cert_path), width=Inches(6.0))
                    doc.add_paragraph()
                except Exception as e:
                    p.add_paragraph(f"  证书文件详见附件：{cert['cert_file']}")
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
            
            # 插入PDF文件
            if cert_path.exists():
                try:
                    doc.add_paragraph()
                    doc.add_picture(str(cert_path), width=Inches(6.0))
                    doc.add_paragraph()
                except Exception as e:
                    p.add_paragraph(f"  证书文件详见附件：{cert['cert_file']}")
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

        # 插入剩余证书的PDF文件（前5个）
        other_certs = [q for q in qualifications if q not in system_certs and q not in credit_certs and q not in honor_certs and q not in partner_certs]
        for cert in other_certs[:5]:
            if cert.get('cert_file'):
                cert_path = data_dir / cert['cert_file']
                if cert_path.exists():
                    try:
                        p = doc.add_paragraph()
                        run = p.add_run(f"• {cert['name']}（{cert['level']}）")
                        doc.add_paragraph()
                        doc.add_picture(str(cert_path), width=Inches(6.0))
                        doc.add_paragraph()
                    except:
                        pass

    doc.add_page_break()


def add_certificates_simple(generator_instance, data_dir: Path):
    """
    修改 BidDocumentGenerator 类的 _add_qualifications_v2 方法
    
    使用方法：
    1. 打开 generator.py
    2. 找到 _add_qualifications_v2 方法（第608行左右）
    3. 用下面的新方法替换
    4. 在 generate_tech_bid 方法中添加：self.data_dir = DATA_DIR
    """
    
    # 需要在 __init__ 方法中添加：
    # self.data_dir = templates_dir.parent / "data"  # 或其他数据目录路径
    
    pass


if __name__ == "__main__":
    print("证书PDF插入功能")
    print("=" * 60)
    print()
    print("功能说明：")
    print("- 直接在Word文档中插入PDF证书文件")
    print("- 使用 docx.add_picture() 方法插入PDF")
    print("- 宽度设置为 6 英寸，适合A4纸张")
    print()
    print("优点：")
    print("- 代码简单，不需要额外安装库")
    print("- Word 支持直接插入PDF，显示效果良好")
    print("- 用户可以双击打开PDF查看完整内容")
    print()
    print("缺点：")
    print("- 不是以图片形式显示（需要双击打开）")
    print("- 如果PDF文件太大，可能导致文档体积大")
    print()
    print("使用方法：")
    print("1. 在 BidDocumentGenerator 类的 __init__ 方法中添加：")
    print("   self.data_dir = DATA_DIR")
    print()
    print("2. 找到 _add_qualifications_v2 方法（第608行）")
    print("3. 将方法替换为新方法 _add_qualifications_with_pdf")
    print()
    print("示例代码（修改 generate_tech_bid 方法）：")
    print("""
# 在 generate_tech_bid 方法开头添加：
self.data_dir = Path(__file__).parent.parent / "data"

# 调用新方法：
self._add_qualifications_with_pdf(doc, matched_data.get("qualifications", []), self.data_dir)
    """)
    print()
    print("=" * 60)
