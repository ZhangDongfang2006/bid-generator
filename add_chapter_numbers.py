#!/usr/bin/env python3
"""
为章节标题添加数字编号，让它们和目录一致
"""

import json
from pathlib import Path

# 章节编号映射
chapter_numbers = {
    '单一文件': {
        '封面': '1.',
        '目录': '2.',
        '公司概况': '3.',
        '公司简介': '4.',
        '公司资质': '5.',
        '公司业绩': '6.',
        '投标纲领': '7.',
        '技术偏离表': '8.',
        '技术方案': '9.',
        '设备说明一览表': '10.',
        '资质证书': '11.',
        '项目案例': '12.',
        '报价说明': '13.',
        '售后服务': '14.',
        '技术承诺': '15.',
        '响应承诺': '16.',
        '商务承诺': '17.',
    },
    '技术标': {
        '封面': '1.1',
        '目录': '1.2',
        '公司概况': '1.3',
        '投标纲领': '1.4',
        '技术偏离表': '1.5',
        '公司简介': '1.6',
        '技术方案': '1.7',
        '近三年无重大违法记录声明': '1.8',
        '质量控制专项方案': '1.9',
        '安全保证': '1.10',
        '设备说明一览表': '1.11',
        '供货组织及进度计划': '1.12',
        '技术培训、售后服务': '1.13',
        '资质证书': '1.14',
        '项目案例': '1.15',
        '技术承诺': '1.16',
        '响应承诺': '1.17',
    },
    '商务标': {
        '封面': '1.1',
        '公司概况': '1.2',
        '投标纲领': '1.3',
        '商务偏离表': '1.4',
        '公司简介': '1.5',
        '响应承诺': '1.6',
        '报价说明': '1.7',
        '资质证书': '1.8',
        '项目案例': '1.9',
        '售后服务': '1.10',
        '商务承诺': '1.11',
    }
}


def get_chapter_title(title: str, bid_type: str = '单一文件'):
    """
    获取带编号的章节标题
    
    Args:
        title: 原始标题
        bid_type: 投标类型（单一文件、技术标、商务标）
    
    Returns:
        带编号的章节标题
    """
    # 检查标题是否已包含阿拉伯数字编号（1. 或 2.）
    import re
    if re.match(r'^\d+\.\d*\s', title):
        return title
    
    # 检查标题是否以中文数字开头（一、二、三、...）
    # 如果是，需要根据 bid_type 转换为对应的编号
    chinese_number_map = {
        '单一文件': {
            '二、法定代表人授权书': '3. ',
            '三、投标保证金缴纳证明': '4. ',
            '六、质保期满后三年内的备品备件供货承诺': '5. ',
            '九、近三年无重大违法记录声明': '8. ',
            '十二、质量控制专项方案': '9. ',
            '十三、安全保证': '10. ',
            '十四、供货组织及进度计划': '11. ',
            '十五、技术培训、售后服务的内容、计划及措施': '12. ',
        },
        '技术标': {
            '九、近三年无重大违法记录声明': '1.8 ',
            '十二、质量控制专项方案': '1.9 ',
            '十三、安全保证': '1.10 ',
            '十四、供货组织及进度计划': '1.12 ',
            '十五、技术培训、售后服务的内容、计划及措施': '1.13 ',
        },
        '商务标': {
            # 商务标没有公司通用内容章节
        },
    }
    
    # 检查是否是中文数字开头的章节（精确匹配）
    for chinese_title, arabic_num in chinese_number_map.get(bid_type, {}).items():
        if title == chinese_title:
            # 替换整个标题为阿拉伯数字编号
            # 例如：九、近三年无重大违法记录声明 -> 1.8 近三年无重大违法记录声明
            # 先提取中文数字前缀
            import re
            match = re.match(r'^(一|二|三|四|五|六|七|八|九|十|十一|十二|十三|十四|十五)、', title)
            if match:
                chinese_prefix = match.group(1)
                # 替换中文数字前缀为阿拉伯数字编号
                new_title = title.replace(f'{chinese_prefix}、', arabic_num, 1)
                return new_title
    
    # 查找对应的编号（处理没有编号的标题）
    for key, number in chapter_numbers.get(bid_type, {}).items():
        if title == key:  # 使用精确匹配，而不是子字符串匹配
            return f"{number} {title}"
    
    # 如果没有找到编号，返回原标题
    return title


def test_chapter_numbers():
    """测试章节编号"""
    print('测试章节编号：')
    print('=' * 60)
    
    # 单一文件
    titles = ['封面', '公司概况', '公司简介', '设备说明一览表', '九、近三年无重大违法记录声明', '十二、质量控制专项方案']
    print('\n单一文件：')
    for title in titles:
        numbered_title = get_chapter_title(title, '单一文件')
        print(f'  {title:40} -> {numbered_title}')
    
    # 技术标
    titles = ['封面', '公司概况', '设备说明一览表', '九、近三年无重大违法记录声明', '十二、质量控制专项方案']
    print('\n技术标：')
    for title in titles:
        numbered_title = get_chapter_title(title, '技术标')
        print(f'  {title:40} -> {numbered_title}')
    
    # 商务标
    titles = ['封面', '公司概况', '商务承诺']
    print('\n商务标：')
    for title in titles:
        numbered_title = get_chapter_title(title, '商务标')
        print(f'  {title:40} -> {numbered_title}')
    
    print()
    print('=' * 60)


if __name__ == '__main__':
    test_chapter_numbers()
    print('✅ 章节编号测试完成')
