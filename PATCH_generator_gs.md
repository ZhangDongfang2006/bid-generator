# PDF 转图片功能修复补丁（Ghostscript 直接调用版）

## 问题发现

### 问题1：pdf2image API 参数不兼容
- 错误：`convert_from_path() got an unexpected keyword argument 'first_page_only'`
- 原因：pdf2image 的 API 中没有 `first_page_only` 和 `paths` 参数
- 解决方案：使用 `first_page=1, last_page=1` 参数

### 问题2：Ghostscript 参数问题
- 错误：`Unrecoverable error: rangecheck in .putdeviceprops`
- 原因：使用了太复杂的 Ghostscript 参数
- 解决方案：简化参数，只使用 `-dFirstPage=1 -sDEVICE=jpeg` 等

## 修复方案

### 方案1：使用 Ghostscript 直接调用（推荐）

**优点：**
- 不依赖 pdf2image
- 不依赖 poppler
- 更可控
- 错误更容易调试

**缺点：**
- 需要编写更多的代码
- 需要手动处理 Ghostscript 的输出

**实现步骤：**

1. **更新 generator.py**

在 `_add_qualifications_with_pdf_images` 方法中，替换 PDF 转换代码：

**修复前（错误）：**
```python
import pdf2image
from pdf2image import convert_from_path

images = convert_from_path(
    str(cert_path),
    output_folder=temp_dir,
    first_page_only=True,  # ❌ 不支持的参数
    dpi=200,
    fmt='jpg',
    use_cropbox=True
)
```

**修复后（正确）：**
```python
import subprocess
import tempfile

# Ghostscript 命令（只转换第1页）
gs_path = subprocess.run(["which", "gs"], capture_output=True, text=True).stdout.strip()
command = [
    gs_path,
    "-dFirstPage=1",  # 只转换第1页
    "-sDEVICE=jpeg",  # 输出为 JPEG
    "-r200",  # 200dpi
    "-dJPEGQ=95",  # JPEG 质量 95
    "-dNOPAUSE",
    "-dBATCH",
    "-dQUIET",
    f"-sOutputFile={output_path}",
    str(cert_path)
]

# 运行命令
result = subprocess.run(
    command,
    capture_output=True,
    text=True,
    timeout=30
)

if result.returncode == 0 and Path(output_path).exists():
    # 转换成功，使用图片
    images = [str(output_path)]
```

### 方案2：使用 pdf2image（备选）

**优点：**
- 代码更简洁
- pdf2image 处理了大部分细节

**缺点：**
- 依赖 pdf2image 和 poppler
- 参数不兼容

**实现步骤：**

在 `_add_qualifications_with_pdf_images` 方法中，替换 PDF 转换代码：

**修复前（错误）：**
```python
images = convert_from_path(
    str(cert_path),
    output_folder=temp_dir,
    first_page_only=True,  # ❌ 不支持的参数
    dpi=200,
    fmt='jpg',
    use_cropbox=True
)
```

**修复后（正确）：**
```python
images = convert_from_path(
    str(cert_path),
    output_folder=temp_dir,
    first_page=1,  # ✅ 从第1页开始
    last_page=1,   # ✅ 到第1页结束（只转换第1页）
    dpi=200,
    fmt='jpg',
    use_cropbox=True
)
```

## 快速修复

### 方法1：使用 fix_generator_gs.py（推荐）

1. **备份当前的 generator.py**
   ```bash
   cp /Users/zhangdongfang/workspace/bid-generator/generator.py /Users/zhangdongfang/workspace/bid-generator/generator.py.backup
   ```

2. **测试修复脚本**
   ```bash
   cd /Users/zhangdongfang/workspace/bid-generator
   python3 fix_generator_gs.py
   ```

3. **如果测试成功，应用修复**
   - 将 `fix_generator_gs.py` 中的 `convert_pdf_to_jpeg_gs` 函数
   - 复制到 `generator.py` 中
   - 更新 `_add_qualifications_with_pdf_images` 方法，调用 `convert_pdf_to_jpeg_gs`

### 方法2：手动更新 generator.py

1. **在文件顶部添加导入**
   ```python
   import subprocess
   import tempfile
   ```

2. **添加 `convert_pdf_to_jpeg_gs` 函数**
   - 从 `fix_generator_gs.py` 中复制整个函数
   - 添加到 `BidDocumentGenerator` 类中（在 `_add_qualifications_with_images` 方法之前）

3. **更新 `_add_qualifications_with_pdf_images` 方法**
   - 将 PDF 转换部分替换为：
   ```python
   # 转换PDF为图片（使用 Ghostscript 直接调用）
   try:
       print(f"[DEBUG]   - 开始转换 PDF...")
       output_path = Path(temp_dir) / f"cert_{cert['id']}.jpg"
       
       success = self.convert_pdf_to_jpeg_gs(
           str(cert_path),
           str(output_path),
           dpi=200
       )
       
       if success:
           images = [str(output_path)]
           print(f"[DEBUG]   - ✓ 转换成功！生成 {len(images)} 张图片")
       else:
           print(f"[DEBUG]   - ✗ 转换失败")
           images = []
   except Exception as e:
       print(f"[DEBUG]   - ✗ 转换失败：{e}")
       images = []
   ```

4. **保存文件**
   ```bash
   cp /Users/zhangdongfang/workspace/bid-generator/generator.py /Users/zhangdongfang/workspace/bid-generator/generator.py.fixed
   ```

## 测试步骤

1. **重启应用**
   ```bash
   cd /Users/zhangdongfang/workspace/bid-generator
   ./start.sh
   ```

2. **开启调试模式**
   - 点击左侧边栏的"🐛 调试模式"按钮

3. **完成步骤1-3**
   - 上传文件
   - 解析文件
   - 匹配资料

4. **步骤4：生成文件**
   - **勾选"显示证书图片"**（重要！）
   - 点击"生成投标文件"

5. **查看调试信息**
   - 应该看到：
   ```
   🔍 调试信息（当前会话状态）
   show_cert_images_final = True
   ```

6. **下载技术标**
   - 打开文件
   - 查看"第3章 企业资质"部分
   - **查看是否有证书图片！**

## 判断标准

- **如果 `show_cert_images_final = True`**：
  - ✅ 你勾选了"显示证书图片"
  - ✅ 应该会显示证书图片
  - ✅ 如果还是看不到图片，说明 PDF 转图片失败了

- **如果 `show_cert_images_final = False`**：
  - ❌ 你没有勾选"显示证书图片"
  - ❌ 不会显示证书图片

- **如果调试信息显示 `True` 但文件中没有图片**：
  - 说明 PDF 转图片失败
  - 可能原因：
    - PDF 文件不存在
    - PDF 文件路径错误
    - Ghostscript 未正确安装
    - 转换参数不兼容

## 故障排除

### 问题1：仍然没有图片

**检查：**
1. 调试信息中 `show_cert_images_final` 的值是什么？
   - 如果是 `False`，说明没有勾选"显示证书图片"

2. 在终端中运行：
   ```bash
   cd /Users/zhangdongfang/workspace/bid-generator
   python3 fix_generator_gs.py
   ```
   看测试是否成功

3. 查看终端输出，是否有错误信息

### 问题2：转换失败

**检查：**
1. Ghostscript 是否安装？
   ```bash
   which gs
   ```
   应该显示：`/opt/homebrew/bin/gs`

2. Ghostscript 版本是否兼容？
   ```bash
   gs --version
   ```
   应该显示：`10.06.0` 或更高

3. PDF 文件是否存在？
   ```bash
   ls -la data/certificates/03、认证证书/01、质量管理体系认证证书-中英文版.pdf
   ```
   应该显示文件信息

### 问题3：Word 文档生成失败

**检查：**
1. Pillow 是否安装？
   ```bash
   pip3 list | grep -i pillow
   ```
   应该显示 Pillow 版本

2. python-docx 是否安装？
   ```bash
   pip3 list | grep -i docx
   ```
   应该显示 python-docx 版本

## 总结

**修复内容：**
1. ✅ 发现了 pdf2image API 参数不兼容问题
2. ✅ 发现了 Ghostscript 参数问题
3. ✅ 测试了 Ghostscript 直接调用（成功！）
4. ✅ 创建了 Ghostscript 直接调用版本的修复脚本
5. ✅ 创建了补丁文件，说明如何更新 generator.py

**用户需要做的：**
1. ✅ 重启应用
2. ✅ 开启调试模式
3. ✅ 勾选"显示证书图片"
4. ✅ 生成投标文件
5. ✅ 查看调试信息和生成的文件

**判断标准：**
- 如果 `show_cert_images_final = True`，应该会显示证书图片
- 如果 `show_cert_images_final = False`，不会显示证书图片
- 如果调试信息显示 `True` 但文件中没有图片，说明还有其他问题

**测试结果：**
- ✅ Ghostscript 可以正常工作
- ✅ PDF 可以转换为图片
- ✅ 图片可以插入到 Word 文档
- ✅ Word 文档可以保存
- ✅ Ghostscript 直接调用方式正常！

**现在可以开始测试了！**
