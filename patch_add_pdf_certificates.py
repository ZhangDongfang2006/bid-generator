"""
添加PDF证书文件插入功能 - 补丁文件

这个补丁修改 generator.py 中的 _add_qualifications_v2 方法，
添加直接插入PDF证书文件的功能。
"""

# 修改位置1：方法签名（第608行）
# 修改前：
# def _add_qualifications_v2(self, doc: Document, qualifications: List[Dict]):

# 修改后：
# def _add_qualifications_v2(self, doc: Document, qualifications: List[Dict], data_dir: Path = None):

# 修改位置2：方法开头（第620行左右）
# 添加代码：
# # 检查 data_dir
# if data_dir is None:
#     # 使用默认数据目录
#     data_dir = self.templates_dir.parent / "data"

# 修改位置3：体系认证证书（第640-650行左右）
# 修改前：
# for cert in system_certs[:10]:  # 最多显示10个
#     doc.add_paragraph(f"• {cert['name']}（{cert['level']}）")
#     if cert.get('cert_file'):
#         doc.add_paragraph(f"  证书文件：{cert['cert_file']}")

# 修改后：
# for cert in system_certs[:10]:  # 最多显示10个
#     doc.add_paragraph(f"• {cert['name']}（{cert['level']}）")
#     if cert.get('cert_file'):
#         # 【新增】插入PDF证书文件
#         cert_path = data_dir / cert['cert_file']
#         if cert_path.exists():
#             try:
#                 doc.add_paragraph()
#                 doc.add_picture(str(cert_path), width=Inches(6.0))
#                 doc.add_paragraph()
#             except Exception as e:
#                 doc.add_paragraph(f"  （证书文件插入失败：{str(e)}）")
#         else:
#             doc.add_paragraph(f"  证书文件：{cert['cert_file']}（文件不存在）")

# 需要修改4个地方：
# 1. 体系认证证书（约第640-650行）
# 2. 信用等级证书（约第660-670行）
# 3. 荣誉证书（约第680-690行）
# 4. 合作伙伴证书（约第700-710行）

print("""
PDF证书文件插入功能 - 补丁说明

修改文件：generator.py

修改步骤：

1. 修改方法签名（第608行）
   - 添加 data_dir 参数

2. 在方法开头检查 data_dir（第620行左右）
   - 添加默认值检查

3. 在体系认证证书部分添加插入PDF代码（约第640-650行）

4. 在信用等级证书部分添加插入PDF代码（约第660-670行）

5. 在荣誉证书部分添加插入PDF代码（约第680-690行）

6. 在合作伙伴证书部分添加插入PDF代码（约第700-710行）

7. 修改调用方法的地方（2处）：
   - generate_tech_bid 方法（第100行左右）
   - generate_commercial_bid 方法（第160行左右）
   - 修改前：self._add_qualifications_v2(doc, matched_data.get("qualifications", []))
   - 修改后：self._add_qualifications_v2(doc, matched_data.get("qualifications", []), DATA_DIR)

效果：
- 证书PDF文件会直接插入到Word文档中
- 可以在文档中直接查看证书
- 不需要双击打开
- 显示宽度为6英寸，适合A4纸张

注意事项：
1. 确保证书文件路径正确
2. 如果PDF文件太大，可能导致文档体积增大
3. 建议只插入前10个证书的PDF
4. 如果插入失败，会显示文件路径作为备选方案

测试：
1. 重启应用程序
2. 生成投标文件
3. 检查"第3章 企业资质"部分
4. 确认证书PDF文件已插入
""")
