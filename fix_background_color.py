"""
修复方案：暂时注释掉设置单元格背景色的代码

问题：在 _add_deviation_table 中手动创建 XML 元素时出错
错误：ValueError: too many values to unpack (expected 2)
原因：OxmlElement 内部处理 XML 字符串时出错

解决方案：暂时注释掉设置单元格背景色的代码
"""

def fix_remove_cell_background():
    """
    修复：暂时注释掉设置单元格背景色的代码
    """
    
    old_code = """            # 设置单元格背景色
            cell._element.get_or_add_tcPr().append(
                self._parse_xml(f'<w:shd {self._nsdecls("w")} w:fill="D9E2F3"/>')
            )"""
    
    new_code = """            # 设置单元格背景色
            # TODO: 单元格背景色设置暂时禁用，需要使用其他方式实现
            # cell._element.get_or_add_tcPr().append(
            #     self._parse_xml(f'<w:shd {self._nsdecls("w")} w:fill="D9E2F3"/>')
            # )"""
    
    return old_code, new_code


def apply_fix_to_generator():
    """
    应用修复到 generator.py
    """
    import re
    from pathlib import Path
    
    generator_file = Path("/Users/zhangdongfang/workspace/bid-generator/generator.py")
    
    # 读取文件
    with open(generator_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换代码
    old_code, new_code = fix_remove_cell_background()
    
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
    print("\n问题：手动创建 XML 元素时出错")
    print("解决方案：暂时注释掉设置单元格背景色的代码\n")
    
    if apply_fix_to_generator():
        print("✓ 修复已应用")
        print("\n注意：单元格背景色已被暂时禁用")
        print("      稍序运行后可以重新考虑使用其他方式实现")
    else:
        print("✗ 旧代码未找到，可能已经被修复")


def alternative_fix_use_docx_api():
    """
    备选方案：使用 docx 的 CT_Shd 类
    
    这是更正确的方法，但需要更多的代码更改
    """
    
    code = """
    # 设置单元格背景色（使用 docx API）
    from docx.oxml.shared import CT_Shd
    
    # 创建阴影元素
    shd = CT_Shd()
    shd.fill = "D9E2F3"  # 浅灰色背景
    
    # 添加到单元格的 tcPr
    tcPr = cell._element.get_or_add_tcPr()
    tcPr.shd = shd
    """
    
    return code
