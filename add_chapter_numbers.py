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
        '公司概况': '2.',
        '公司简介': '3.',
        '公司资质': '4.',
        '公司业绩': '5.',
        '投标纲领': '6.',
        '技术偏离表': '7.',
        '技术方案': '8.',
        '设备说明一览表': '9.',
        '资质证书': '10.',
        '项目案例': '11.',
        '报价说明': '12.',
        '售后服务': '13.',
        '技术承诺': '14.',
        '响应承诺': '15.',
        '商务承诺': '16.',
    },
    '技术标': {
        '封面': '1.1',
        '目录': '1.2',
        '公司概况': '1.3',
        '公司简介': '1.4',
        '公司资质': '1.5',
        '公司业绩': '1.6',
        '投标纲领': '1.7',
        '技术偏离表': '1.8',
        '技术方案': '1.9',
        '项目团队': '1.10',
        '设备说明一览表': '1.11',
        '技术承诺': '1.12',
        '响应承诺': '1.13',
    },
    '商务标': {
        '封面': '2.1',
        '目录': '2.2',
        '公司概况': '2.3',
        '投标纲领': '2.4',
        '商务偏离表': '2.5',
        '报价说明': '2.6',
        '商务承诺': '2.7',
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
    # 检查标题是否已包含编号
    if title.startswith('一、') or title.startswith('二、') or \
       title.startswith('三、') or title.startswith('四、') or \
       title.startswith('五、') or title.startswith('六、') or \
       title.startswith('七、') or title.startswith('八、') or \
       title.startswith('九、') or title.startswith('十、') or \
       title.startswith('十一、') or title.startswith('十二、') or \
       title.startswith('十三、') or title.startswith('十四、') or \
       title.startswith('十五、') or title.startswith('1.') or \
       title.startswith('2.') or title.startswith('目录'):
        return title
    
    # 查找对应的编号
    for key, number in chapter_numbers.get(bid_type, {}).items():
        if key in title:
            return f"{number} {title}"
    
    # 如果没有找到编号，返回原标题
    return title


def test_chapter_numbers():
    """测试章节编号"""
    print('测试章节编号：')
    print('=' * 60)
    
    # 单一文件
    titles = ['封面', '公司概况', '公司简介', '设备说明一览表']
    for title in titles:
        numbered_title = get_chapter_title(title, '单一文件')
        print(f'  {title:15} -> {numbered_title}')
    
    print()
    
    # 技术标
    titles = ['封面', '公司概况', '设备说明一览表']
    for title in titles:
        numbered_title = get_chapter_title(title, '技术标')
        print(f'  {title:15} -> {numbered_title}')
    
    print()
    
    # 商务标
    titles = ['封面', '公司概况', '商务承诺']
    for title in titles:
        numbered_title = get_chapter_title(title, '商务标')
        print(f'  {title:15} -> {numbered_title}')
    
    print()
    print('=' * 60)


if __name__ == '__main__':
    test_chapter_numbers()
    print('✅ 章节编号测试完成')
