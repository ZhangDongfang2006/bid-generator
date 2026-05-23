#!/usr/bin/env python3
"""
Insert qualification images into the bid document - V2
Each image gets a unique file to avoid python-docx dedup.
"""
import os, re, shutil, hashlib, uuid
from pathlib import Path
from docx import Document
from docx.shared import Cm, Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
import fitz  # PyMuPDF

BASE = Path("/Users/zhangdongfang/.openclaw/workspace-company/公司资质")
QUAL_PKG = BASE / "海越资质文件素材包"
HONOR_PKG = QUAL_PKG / "02、企业资质荣誉篇"
PRODUCT_PKG = QUAL_PKG / "03、产品展示篇"
DOCX_PATH = Path("/Users/zhangdongfang/.openclaw/workspace-notebooklm/合浦矿业箱变项目_投标文件.docx")
OUTPUT_PATH = Path("/Users/zhangdongfang/.openclaw/workspace-notebooklm/合浦矿业箱变项目_投标文件_完整版.docx")
IMG_DIR = Path("/Users/zhangdongfang/.openclaw/workspace-notebooklm/bid_images_v2")
INSPECTION = BASE / "05、检验报告"
TEST_REPORT = BASE / "06、试验报告"
SELF_DECL = BASE / "07、自我声明"
PATENT = BASE / "09、专利证书"
TYPE_CERT = BASE / "08、型式试验证书"

if IMG_DIR.exists():
    shutil.rmtree(IMG_DIR)
IMG_DIR.mkdir(parents=True, exist_ok=True)

img_counter = 0
def get_unique_name(base_name):
    global img_counter
    img_counter += 1
    return f"img_{img_counter:03d}_{base_name}"

def pdf_first_page(pdf_path, output_path, dpi=150):
    doc = fitz.open(str(pdf_path))
    if len(doc) == 0:
        return False
    page = doc[0]
    mat = fitz.Matrix(dpi/72, dpi/72)
    pix = page.get_pixmap(matrix=mat)
    pix.save(str(output_path))
    doc.close()
    os.system(f'sips -Z 1200 "{output_path}" --out "{output_path}" 2>/dev/null')
    return True

def find_file(directory, keyword):
    if not directory.exists():
        return None
    for f in directory.iterdir():
        if keyword.lower() in f.name.lower():
            return f
    return None

def extract_pdf(pdf_path, label):
    """Extract first page from PDF, return unique-named image path."""
    global img_counter
    img_counter += 1
    ext = ".png"
    out = IMG_DIR / f"img_{img_counter:03d}_{label}{ext}"
    if pdf_first_page(pdf_path, out):
        print(f"  ✓ {label}")
        return out
    return None

def copy_img(src_path, label):
    """Copy an image file with unique name."""
    global img_counter
    img_counter += 1
    ext = src_path.suffix.lower()
    out = IMG_DIR / f"img_{img_counter:03d}_{label}{ext}"
    shutil.copy2(src_path, out)
    os.system(f'sips -Z 1200 "{out}" --out "{out}" 2>/dev/null')
    return out

# ==========================================
# Step 1: Extract all needed images
# ==========================================
print("=== Extracting images ===")

images = {}  # key -> path

# --- 商务标 ---
# 营业执照
images["营业执照"] = extract_pdf(BASE / "营业执照.pdf", "营业执照")

# ISO三体系
for label, fname in [("ISO质量", "2、质量管理体系认证证书.pdf"), 
                      ("ISO环境", "3、环境管理体系认证证书.pdf"),
                      ("ISO职业健康", "4、职业健康安全管理体系认证证书.pdf")]:
    images[label] = extract_pdf(HONOR_PKG / fname, label)

# 荣誉证书 - 精选
honor_picks = [
    ("AAA信用企业", "21、 AAA信用企业证书.pdf"),
    ("AAA资信等级", "22、资信等级AAA 级企业证书.pdf"),
    ("AAA重合同守信用", "23、AAA级重合同守信用企业证书.pdf"),
    ("省级重点项目", "27、省级重点项目及证书.pdf"),
    ("高新技术企业", "17、高新技术企业证书.pdf"),
    ("智能工厂", "15、智能工厂管理体系认证证书.pdf"),
    ("绿色工厂", "10、绿色工厂管理体系认证证书.pdf"),
    ("未来工厂", "12、未来工厂认证证书.pdf"),
    ("数字化车间", "13、数字化车间管理体系认证证书.pdf"),
]
for label, fname in honor_picks:
    images[label] = extract_pdf(HONOR_PKG / fname, label)

# 合作伙伴授权
partner_picks = [
    ("西门子SIVACON授权", "31、SIVACON 8PT 西门子授权合作伙伴证书.pdf"),
    ("ABB合作伙伴", "34、ABB 紧密合作伙伴.pdf"),
    ("常熟开关合作伙伴", "36、常熟开关制造有限公司紧密合作伙伴.pdf"),
    ("西门子NXAirS授权", "33、西门子授权 NXAirS 12kV24kV 中压开关柜 .pdf"),
]
for label, fname in partner_picks:
    images[label] = extract_pdf(HONOR_PKG / fname, label)

# --- 技术标 ---
# 箱变检验报告
box_inspections = [
    ("箱变检验YB12", "01、高压低压预装式变电站检验报告 型号：YB□-12 -0.4-1600.pdf"),
    ("箱变检验YZB", "06、预装式变电站（箱式变电站) 检验报告 型号：YZB-40.50.8-4000 .pdf"),
]
for label, fname in box_inspections:
    images[label] = extract_pdf(INSPECTION / fname, label)

# 型式试验证书
type_certs = [
    ("SIVACON_CB认证", "02、海越8PT CB认证证书.pdf"),
]
for label, fname in type_certs:
    f = TYPE_CERT / fname
    if f.exists():
        images[label] = extract_pdf(f, label)

# 自我声明
f = find_file(SELF_DECL, "SIVACON 8PT 6300A")
if f:
    images["SIVACON_8PT_自我声明"] = extract_pdf(f, "SIVACON_8PT自我声明")

# 专利
patent_picks = [
    ("专利_非标箱支架", "01、202421847849.8-一种非标箱装配及展示支架"),
    ("专利_焊接吸尘", "02、202422221434.6-焊接吸尘装置"),
    ("专利_面板折弯机", "04、202422746950.0-一种面板折弯机"),
]
for label, kw in patent_picks:
    f = find_file(PATENT, kw)
    if f:
        images[label] = extract_pdf(f, label)

# 箱变产品图
box_product_dir = PRODUCT_PKG / "01、高压 、低压预装式变电站YB口-12型"
if box_product_dir.exists():
    for img_f in sorted(box_product_dir.iterdir()):
        if img_f.suffix.lower() in ('.jpg', '.jpeg', '.png'):
            label = f"箱变产品_{img_f.stem[:10]}"
            images[label] = copy_img(img_f, label)
            print(f"  ✓ {label}")

# 工厂照片
factory_dir = QUAL_PKG / "01、企业风采篇" / "04、现代化智能工厂"
if factory_dir.exists():
    for img_f in sorted(factory_dir.iterdir())[:3]:
        if img_f.suffix.lower() in ('.jpg', '.jpeg', '.png'):
            label = f"工厂_{img_f.stem[:15]}"
            images[label] = copy_img(img_f, label)
            print(f"  ✓ {label}")

# 地标/投产仪式
for img_f in (QUAL_PKG / "01、企业风采篇").iterdir():
    if img_f.suffix.lower() in ('.jpg', '.jpeg', '.png') and ("地标" in img_f.name or "投产" in img_f.name):
        label = f"企业_{img_f.stem[:10]}"
        images[label] = copy_img(img_f, label)
        print(f"  ✓ {label}")

print(f"\nTotal: {len(images)} images ready")

# ==========================================
# Step 2: Rebuild document with images at right positions
# ==========================================
print("\n=== Building document ===")

doc = Document(str(DOCX_PATH))
paras = doc.paragraphs

# Build a plan: scan through paragraphs, track where to insert
# We'll rebuild by adding content + images to a new approach
# Since modifying in-place with python-docx is tricky, we'll append at end
# then note the positions for user reference

# Better approach: insert at correct paragraph positions using XML manipulation
from docx.oxml import OxmlElement
from lxml import etree

def insert_image_after_paragraph(para, img_path, width=Cm(14)):
    """Insert an image paragraph after the given paragraph using XML."""
    # Create a new paragraph element
    new_p = OxmlElement('w:p')
    # Center alignment
    pPr = OxmlElement('w:pPr')
    jc = OxmlElement('w:jc')
    jc.set(qn('w:val'), 'center')
    pPr.append(jc)
    new_p.append(pPr)
    
    # Create run with drawing
    new_r = OxmlElement('w:r')
    new_p.append(new_r)
    
    # Add picture using python-docx helper (create temp para, add pic, move XML)
    from docx.shared import Inches, Cm
    import io
    
    # Use the paragraph's document part to add image relationship
    para_element = para._element
    run = para.add_run()
    # We need to get the parent document
    
    return None  # Fallback to simpler method

# Simpler but effective: just append all images at the end in organized sections
# This is actually more practical for bid documents

# First, let's check what section headings exist
print("\nDocument structure (key headings):")
for i, p in enumerate(paras):
    text = p.text.strip()
    if text and ('#' in text or any(kw in text for kw in ['投标函', '授权委托', '资格', '技术方案', '售后服务', '检验报告', '型式试验', '专利', '产品展示', '企业简介', '公司简介', '业绩', '荣誉', '认证', '营业执照'])):
        style = p.style.name if p.style else 'none'
        if 'Heading' in style:
            print(f"  [{i}] {style}: {text[:60]}")

# Strategy: Find key section headings and insert images after them
# Using the append-at-end approach with clear section markers

# Clear approach: add images at the end, organized by section
doc.add_page_break()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("附件：资质证书及相关证明材料")
run.bold = True
run.font.size = Pt(16)
run.font.name = '黑体'
run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')

# === 商务标附件 ===
doc.add_heading("一、企业基础资质", level=2)

if "营业执照" in images:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(str(images["营业执照"]), width=Cm(12))
    cap = doc.add_paragraph("附件1：营业执照")
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_heading("二、管理体系认证证书", level=2)
for key in ["ISO质量", "ISO环境", "ISO职业健康"]:
    if key in images:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(str(images[key]), width=Cm(14))
        labels = {"ISO质量": "附件2：质量管理体系认证证书（ISO 9001）",
                   "ISO环境": "附件3：环境管理体系认证证书（ISO 14001）",
                   "ISO职业健康": "附件4：职业健康安全管理体系认证证书（ISO 45001）"}
        cap = doc.add_paragraph(labels[key])
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_heading("三、荣誉及信用证书", level=2)
for key in ["AAA信用企业", "AAA资信等级", "AAA重合同守信用", "省级重点项目", "高新技术企业", "智能工厂", "绿色工厂", "未来工厂", "数字化车间"]:
    if key in images:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(str(images[key]), width=Cm(14))

doc.add_heading("四、合作伙伴授权证书", level=2)
for key in ["西门子SIVACON授权", "ABB合作伙伴", "常熟开关合作伙伴", "西门子NXAirS授权"]:
    if key in images:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(str(images[key]), width=Cm(14))

doc.add_page_break()

# === 技术标附件 ===
doc.add_heading("五、产品检验报告", level=2)
for key in ["箱变检验YB12", "箱变检验YZB"]:
    if key in images:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(str(images[key]), width=Cm(14))

doc.add_heading("六、产品认证及型式试验证书", level=2)
for key in ["SIVACON_CB认证", "SIVACON_8PT_自我声明"]:
    if key in images:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(str(images[key]), width=Cm(14))

doc.add_heading("七、专利证书", level=2)
for key in list(images.keys()):
    if key.startswith("专利_"):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(str(images[key]), width=Cm(14))

doc.add_page_break()

doc.add_heading("八、产品展示", level=2)
for key in list(images.keys()):
    if key.startswith("箱变产品_"):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(str(images[key]), width=Cm(14))

doc.add_heading("九、企业风采", level=2)
for key in list(images.keys()):
    if key.startswith("工厂_") or key.startswith("企业_"):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(str(images[key]), width=Cm(14))

# Save
doc.save(str(OUTPUT_PATH))
size_mb = os.path.getsize(str(OUTPUT_PATH)) / (1024*1024)
print(f"\n✅ Done! File: {OUTPUT_PATH}")
print(f"   Size: {size_mb:.1f} MB")
print(f"   Images: {len(images)}")
