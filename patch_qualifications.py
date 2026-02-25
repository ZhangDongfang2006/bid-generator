"""
修改 _add_qualifications_v2 方法以支持插入PDF证书文件

修改内容：
1. 添加 data_dir 参数
2. 在显示证书后直接插入PDF文件
3. 使用 docx.add_picture() 方法插入PDF
"""

# 修改 _add_qualifications_v2 方法的签名
# 修改前：
# def _add_qualifications_v2(self, doc: Document, qualifications: List[Dict]):

# 修改后：
# def _add_qualifications_v2(self, doc: Document, qualifications: List[Dict], data_dir: Path = None):

# 在方法开头添加：
# if data_dir is None:
#     data_dir = self.templates_dir.parent / "data"


# 然后在显示每个证书的地方添加插入PDF的代码

# 示例修改（体系认证证书部分）：

# 修改前：
"""
for cert in system_certs[:10]:  # 最多显示10个
    doc.add_paragraph(f"• {cert['name']}（{cert['level']}）")
    if cert.get('cert_file'):
        doc.add_paragraph(f"  证书文件：{cert['cert_file']}")
"""

# 修改后：
"""
for cert in system_certs[:10]:  # 最多显示10个
    doc.add_paragraph(f"• {cert['name']}（{cert['level']}）")
    if cert.get('cert_file'):
        doc.add_paragraph(f"  证书文件：{cert['cert_file']}")
        
        # 【新增】插入PDF证书文件
        cert_path = data_dir / cert['cert_file']
        if cert_path.exists():
            try:
                doc.add_paragraph()  # 空行
                doc.add_picture(str(cert_path), width=Inches(6.0))  # 插入PDF，宽度6英寸
                doc.add_paragraph()  # 空行
            except Exception as e:
                doc.add_paragraph(f"  （证书文件插入失败：{str(e)}）")
"""

# 需要修改的地方：
# 1. 第608行：修改方法签名，添加 data_dir 参数
# 2. 第643行：体系认证证书 - 添加插入PDF
# 3. 第663行：信用等级证书 - 添加插入PDF
# 4. 第683行：荣誉证书 - 添加插入PDF
# 5. 第701行：合作伙伴证书 - 添加插入PDF

# 同时需要修改调用这个方法的地方：
# 在 generate_tech_bid 和 generate_commercial_bid 方法中：
# 修改前：self._add_qualifications_v2(doc, matched_data.get("qualifications", []))
# 修改后：self._add_qualifications_v2(doc, matched_data.get("qualifications", []), DATA_DIR)
