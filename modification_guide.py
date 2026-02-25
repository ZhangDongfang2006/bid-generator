"""
修改 generator.py 添加 PDF 转图片功能的脚本

这个脚本会：
1. 读取当前的 generator.py
2. 在 _add_qualifications_v2 方法之后添加新方法
3. 修改调用方法的地方
"""

print("修改 generator.py 添加 PDF 转图片功能")
print("=" * 60)

# 步骤1：在文件顶部添加导入
print("\n【步骤1：添加导入】")
print("在文件顶部的导入部分添加：")
print()
print("# PDF 转图片相关导入")
print("import tempfile")
print("from pdf_to_image_service import pdf_to_images, convert_certificates")
print()

# 步骤2：修改 _add_qualifications_v2 方法
print("\n【步骤2：修改资质章节】")
print("找到所有调用 _add_qualifications_v2 的地方，添加 PDF 转图片选项")
print()
print("在 app.py 或 generator.py 中添加一个选项：")
print()
print("# 在步骤3 匹配资料部分添加选项")
print("show_cert_images = st.checkbox('显示证书图片', value=False, key='show_cert_images')")
print()
print("然后在生成投标文件时，将这个选项传递给生成器")
print()

# 步骤3：测试方法
print("\n【步骤3：测试 PDF 转图片】")
print("运行以下命令测试：")
print()
print("cd /Users/zhangdongfang/workspace/bid-generator")
print("python pdf_to_image_service.py test")
print()

# 步骤4：安装依赖
print("\n【步骤4：安装依赖（如果需要）】")
print()
print("Mac:")
print("  brew install ghostscript")
print("  pip install pdf2image Pillow")
print()
print("Windows:")
print("  1. 下载并安装 Ghostscript")
print("     https://www.ghostscript.com/download/gs956w")
print("  2. pip install pdf2image Pillow")
print()
print("Linux (Ubuntu/Debian):")
print("  sudo apt-get update")
print("  sudo apt-get install ghostscript")
print("  pip install pdf2image Pillow")
print()

print("=" * 60)
print("修改说明：")
print("=" * 60)
print()
print("当前方案：")
print("  1. 使用独立的 PDF 转图片服务")
print("  2. 在投标文件中添加选项：显示证书图片")
print("  3. 用户可以选择是否显示证书图片")
print("  4. 如果选择显示，则转换 PDF 为图片并插入")
print()
print("优点：")
print("  - 不破坏现有功能")
print("  - 用户可以选择是否启用")
print("  - 错误不会影响其他功能")
print("  - 更容易调试和维护")
print()
print("缺点：")
print("  - 需要额外的依赖（Ghostscript）")
print("  - 文件会大一些")
print()
print("使用方法：")
print("  1. 安装 Ghostscript（如果未安装）")
print("  2. 在 Streamlit 界面上勾选'显示证书图片'")
print("  3. 生成投标文件")
print("  4. 查看第3章企业资质部分")
