#!/usr/bin/env python3
"""Convert a Markdown file to a styled DOCX with python-docx."""
import re, sys, os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

def md_to_docx(md_path, docx_path):
    doc = Document()
    
    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = '宋体'
    font.size = Pt(12)
    style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    
    # Page margins
    for section in doc.sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(3.17)
        section.right_margin = Cm(3.17)
    
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n')
        stripped = line.strip()
        
        # Skip empty lines
        if not stripped:
            i += 1
            continue
        
        # Headings
        if stripped.startswith('# '):
            p = doc.add_heading(stripped[2:], level=1)
            for run in p.runs:
                run.font.color.rgb = RGBColor(0, 0, 0)
                run.font.name = '黑体'
                run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
            i += 1
            continue
        
        if stripped.startswith('## '):
            p = doc.add_heading(stripped[3:], level=2)
            for run in p.runs:
                run.font.color.rgb = RGBColor(0, 0, 0)
                run.font.name = '黑体'
                run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
            i += 1
            continue
        
        if stripped.startswith('### '):
            p = doc.add_heading(stripped[4:], level=3)
            for run in p.runs:
                run.font.color.rgb = RGBColor(0, 0, 0)
                run.font.name = '黑体'
                run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
            i += 1
            continue
        
        if stripped.startswith('#### '):
            p = doc.add_heading(stripped[5:], level=4)
            i += 1
            continue
        
        # Horizontal rule - skip in formal docs
        if stripped.startswith('---'):
            i += 1
            continue
        
        # Table
        if stripped.startswith('|'):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                tl = lines[i].strip()
                # Skip separator lines
                if re.match(r'^\|[\s\-:]+\|', tl):
                    i += 1
                    continue
                table_lines.append(tl)
                i += 1
            
            if table_lines:
                rows = []
                for tl in table_lines:
                    cells = [c.strip() for c in tl.split('|')[1:-1]]
                    rows.append(cells)
                
                if rows:
                    num_cols = max(len(r) for r in rows)
                    table = doc.add_table(rows=len(rows), cols=num_cols)
                    table.style = 'Table Grid'
                    table.alignment = WD_TABLE_ALIGNMENT.CENTER
                    
                    for ri, row_data in enumerate(rows):
                        for ci, cell_text in enumerate(row_data):
                            if ci < num_cols:
                                cell = table.cell(ri, ci)
                                cell.text = cell_text
                                for paragraph in cell.paragraphs:
                                    paragraph.style = doc.styles['Normal']
                                    for run in paragraph.runs:
                                        run.font.size = Pt(10)
                                        run.font.name = '宋体'
                                        run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
                                        if ri == 0:
                                            run.bold = True
                                # Red for placeholders in tables
                                placeholder_patterns = [
                                    r'___+', r'XXX+', r'XX+', r'待填写', r'待补充',
                                    r'待确认', r'待定', r'TODO',
                                    r'\d{3}XXXXXXXX.*', r'0712-XXXXXXXX',
                                    r'422202XXXXXXXXXXXX', r'91420900XXXXXXXXXX',
                                ]
                                if any(re.search(pat, cell_text) for pat in placeholder_patterns):
                                    run.font.color.rgb = RGBColor(255, 0, 0)
            continue
        
        # Bold line (e.g. **text**)
        # Regular paragraph
        p = doc.add_paragraph()
        # Handle inline formatting
        # Patterns that need user to fill in -> RED
        placeholder_patterns = [
            r'___+', r'XXX+', r'XX+', r'待填写', r'待补充', r'待确认',
            r'待定', r'请填写', r'需要填写', r'需确认', r'【待.*?】',
            r'TODO', r'\d{3}XXXXXXXX.*', r'0712-XXXXXXXX',
            r'422202XXXXXXXXXXXX', r'91420900XXXXXXXXXX',
            r'QMS2023XXXXXX', r'EMS2023XXXXXX', r'OHS2023XXXXXX',
            r'CCC2023XXXXXX', r'CQC2023XXXXXX', r'PCCC2023XXXXXX',
            r'D342XXXXXX', r'PXZZ-XXXX', r'WTC-2023-XXXXX', r'KJ-2024-XXXXX',
            r'2023XXXXXXXX', r'2024XXXXXXXX',
        ]
        is_placeholder = any(re.search(pat, stripped) for pat in placeholder_patterns)
        
        parts = re.split(r'(\*\*.*?\*\*)', stripped)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                run = p.add_run(part[2:-2])
                run.bold = True
                run.font.name = '宋体'
                run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
                if is_placeholder:
                    run.font.color.rgb = RGBColor(255, 0, 0)
            elif part:
                run = p.add_run(part)
                run.font.name = '宋体'
                run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
                if is_placeholder:
                    run.font.color.rgb = RGBColor(255, 0, 0)
        
        # Indent if it's a sub-item (starts with - or spaces)
        if stripped.startswith('- ') or stripped.startswith('  -') or stripped.startswith('  *'):
            p.paragraph_format.left_indent = Cm(1)
        elif stripped.startswith('    '):
            p.paragraph_format.left_indent = Cm(2)
        
        i += 1
    
    doc.save(docx_path)
    print(f"Saved: {docx_path}")
    print(f"Size: {os.path.getsize(docx_path)} bytes")

if __name__ == '__main__':
    md_path = sys.argv[1] if len(sys.argv) > 1 else 'input.md'
    docx_path = sys.argv[2] if len(sys.argv) > 2 else md_path.replace('.md', '.docx')
    md_to_docx(md_path, docx_path)
