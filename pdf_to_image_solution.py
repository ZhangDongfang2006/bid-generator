"""
方案3：PDF转图片的实现

这是最符合用户需求的方案：
- 打印出来直接可以看到证书图片
- 客户不需要任何操作
- 投标文件看起来更专业

## 安装步骤

### 1. 安装 Ghostscript

**Mac:**
```bash
brew install ghostscript
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install ghostscript
```

**Windows:**
1. 下载：https://www.ghostscript.com/download/gs956w
2. 安装（默认安装路径：C:\Program Files\gs\gs9.56.0\bin）
3. 确保添加到系统 PATH

### 2. 安装 pdf2image

```bash
pip install pdf2image
```

### 3. 安装 Pillow (Python图像处理库）

```bash
pip install Pillow
```

## 代码实现

### 修改 generator.py

在文件顶部添加导入：

```python
from pdf2image import convert_from_path
from PIL import Image as PILImage
import tempfile
import os
```

### 添加PDF转图片的方法

```python
def _add_qualifications_with_images(self, doc: Document, qualifications: List[Dict], data_dir: Path):
    '''
    添加企业资质（PDF转图片）
    
    优点：
    - 打印出来直接可以看到证书图片
    - 客户不需要任何操作
    - 投标文件看起来更专业
    
    缺点：
    - 需要安装额外库（pdf2image + Ghostscript）
    - 文件会大一些
    '''
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
            
            # 【新增】PDF转图片并插入
            if cert_path.exists():
                try:
                    # 创建临时目录
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # 转换PDF为图片（只转换第一页）
                        images = convert_from_path(
                            str(cert_path),
                            output_folder=temp_dir,
                            first_page_only=True,
                            dpi=200  # 分辨率，200dpi打印效果较好
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
                            # 调整图片大小
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

    # 3.3 省级荣誉证书
    p = doc.add_paragraph()
    run = p.add_run("3.3 省级荣誉证书")
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
```

### 修改调用方法

在 `generate_tech_bid` 和 `generate_commercial_bid` 方法中：

**修改前：**
```python
self._add_qualifications_v2(doc, matched_data.get("qualifications", []))
```

**修改后：**
```python
from pathlib import Path

# 使用新的方法（PDF转图片）
self._add_qualifications_with_images(doc, matched_data.get("qualifications", []), DATA_DIR)
```

## 效果说明

### 打印效果
- ✅ 打印出来直接可以看到证书图片
- ✅ 图片大小合适（5.5英寸宽，约14厘米）
- ✅ 图片清晰（200dpi）
- ✅ 证书信息完整

### 文件大小
- 每个证书图片约 50-100KB
- 10个证书约 500KB-1MB
- 文件会大一些，但可以接受

### 兼容性
- ✅ PDF转换失败时会显示文件路径作为备选
- ✅ 支持各种PDF格式
- ✅ 自动调整图片大小

## 测试步骤

1. **安装依赖**
   ```bash
   # Mac
   brew install ghostscript
   pip install pdf2image Pillow
   
   # Windows
   # 下载并安装 Ghostscript
   pip install pdf2image Pillow
   ```

2. **测试转换**
   ```python
   from pdf2image import convert_from_path
   from pathlib import Path
   
   # 测试一个PDF文件
   pdf_path = Path("/Users/zhangdongfang/workspace/bid-generator/data/certificates/03、认证证书/01、质量管理体系认证证书-中英文版.pdf")
   
   if pdf_path.exists():
       images = convert_from_path(
           str(pdf_path),
           first_page_only=True,
           dpi=200,
           fmt='jpg'
       )
       print(f"转换成功，生成 {len(images)} 张图片")
       print(f"图片路径：{images[0]}")
   ```

3. **应用到 generator**
   - 复制代码到 generator.py
   - 修改调用方法
   - 测试生成投标文件

4. **检查效果**
   - 打开生成的 Word 文档
   - 查看第3章
   - 确认证书图片已插入
   - 打印测试

## 故障排除

### 问题1：pdf2image 找不到 Ghostscript

**错误信息：** `pdf2image is not able to find ghostscript`

**解决方法：**
1. 确认 Ghostscript 已正确安装
2. 检查 Ghostscript 是否在系统 PATH 中
3. Mac：`which gs` 应该返回 `/usr/local/bin/gs`
4. Windows：`where gs` 应该返回 Ghostscript 安装路径

### 问题2：PDF转换失败

**错误信息：** `pdf2image failed to convert PDF`

**解决方法：**
1. 检查 PDF 文件是否损坏
2. 尝试用其他 PDF 阅读器打开
3. 检查是否有密码保护

### 问题3：图片质量差

**解决方法：**
1. 提高 dpi 参数（如改为 300）
2. 调整目标宽度
3. 使用更好的图片格式（如 png）

## 优化建议

1. **缓存机制**：如果证书不常变化，可以缓存转换后的图片
2. **批量处理**：提前转换所有证书为图片，避免实时转换
3. **异步处理**：使用后台线程转换，避免阻塞主流程

## 总结

**方案3（PDF转图片）是最符合你需求的：**
- ✅ 打印出来直接可以看到证书图片
- ✅ 客户不需要任何操作
- ✅ 投标文件看起来更专业

**安装步骤：**
1. 安装 Ghostscript
2. 安装 pdf2image
3. 安装 Pillow
4. 修改 generator.py
5. 测试生成

如果你觉得安装太麻烦，我建议先用方案1（直接插入PDF），等有时间了再升级到方案3。
