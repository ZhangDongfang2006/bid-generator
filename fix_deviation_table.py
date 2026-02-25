"""
修复 _add_deviation_table 方法的补丁

问题：在 _add_deviation_table 中使用 _parse_xml 手动创建 XML 元素时出错：
  ValueError: too many values to unpack (expected 2)

原因：OxmlElement 内部处理 XML 字符串时出错

解决方案：使用 docx 库提供的 API 来设置单元格样式，而不是手动创建 XML 元素
"""

def fix_add_deviation_table():
    """
    修复 _add_deviation_table 方法

    将手动创建 XML 元素改为使用 docx 的 CT_Pr 类
    """
    
    code_snippet_old = """
            # 设置单元格背景色
            cell._element.get_or_add_tcPr().append(
                self._parse_xml(f'<w:shd {self._nsdecls("w")} w:fill="D9E2F3"/>')
            )
    """
    
    code_snippet_new = """
            # 设置单元格背景色
            from docx.oxml.ns import qn
            from docx.oxml import OxmlElement
            
            # 使用 CT_Shd 类创建阴影元素
            from docx.oxml.shared import CT_Shd
            shd = CT_Shd()
            shd.fill = "D9E2F3"  # 设置背景色
            
            # 添加到单元格的 tcPr
            tcPr = cell._element.get_or_add_tcPr()
            tcPr.shd = shd
    """
    
    return code_snippet_old, code_snippet_new


def apply_fix():
    """
    应用修复到 generator.py
    """
    import re
    from pathlib import Path
    
    generator_file = Path("/Users/zhangdongfang/workspace/bid-generator/generator.py")
    
    # 读取文件
    with open(generator_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换旧代码
    old_code = """            # 设置单元格背景色
            cell._element.get_or_add_tcPr().append(
                self._parse_xml(f'<w:shd {self._nsdecls("w")} w:fill="D9E2F3"/>')
            )"""
    
    new_code = """            # 设置单元格背景色
            from docx.oxml.ns import qn
            from docx.oxml import OxmlElement
            from docx.oxml.shared import CT_Shd
            
            # 创建阴影元素
            shd = CT_Shd()
            shd.fill = "D9E2F3"
            
            # 添加到单元格的 tcPr
            tcPr = cell._element.get_or_add_tcPr()
            tcPr.shd = shd"""
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        
        # 写回文件
        with open(generator_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    else:
        return False


if __name__ == "__main__":
    print("修复 _add_deviation_table 方法...")
    
    old, new = fix_add_deviation_table()
    print("\n旧代码:")
    print(old)
    print("\n新代码:")
    print(new)
    
    print("\n应用修复...")
    if apply_fix():
        print("✓ 修复已应用")
    else:
        print("✗ 旧代码未找到，可能已经被修复")
