#!/usr/bin/env python3
"""
为章节标题添加数字编号，让它们和目录一致
"""

import re

# 章节编号映射（注意：key 不包含中文数字前缀）
chapter_numbers = {
    '单一文件': {
        '封面': '1.',
        '目录': '2.',
        '公司概况': '3.',
        '投标纲领': '4.',
        '技术偏离表': '5.',
        '公司简介': '6.',
        '技术方案': '7.',
        '法定代表人授权书': '8.',
        '投标保证金缴纳证明': '9.',
        '质保期满后三年内的备品备件供货承诺': '10.',
        '设备说明一览表': '11.',
        '近三年无重大违法记录声明': '12.',
        '质量控制专项方案': '13.',
        '安全保证': '14.',
        '供货组织及进度计划': '15.',
        '技术培训、售后服务': '16.',
        '报价说明': '17.',
        '资质证书': '18.',
        '项目案例': '19.',
        '售后服务': '20.',
        '技术承诺': '21.',
        '响应承诺': '22.',
        '商务承诺': '23.',
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

# 中文数字列表
chinese_numbers = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二', '十三', '十四', '十五']


def get_chapter_title(title, bid_type='单一文件'):
    """
    获取带编号的章节标题

    Args:
        title: 原始标题
        bid_type: 投标类型（单一文件、技术标、商务标）

    Returns:
        带编号的章节标题
    """
    # 检查标题是否已包含阿拉伯数字编号
    if re.match(r'^\d+\.\d*\s', title):
        return title

    # 检查是否以中文数字开头（如 "二、法定代表人授权书"）
    # 如果是，去掉中文数字前缀后再查找
    for cn_num in chinese_numbers:
        prefix = cn_num + '、'
        if title.startswith(prefix):
            title_without_prefix = title[len(prefix):]
            # 在章节编号映射中查找（key 不包含中文数字前缀）
            for key, number in chapter_numbers.get(bid_type, {}).items():
                if title_without_prefix == key:
                    return f"{number} {title_without_prefix}"
            # 如果没有找到匹配，返回原标题
            return title

    # 查找对应的编号（处理没有编号的标题）
    for key, number in chapter_numbers.get(bid_type, {}).items():
        if title == key:
            return f"{number} {title}"

    # 如果没有找到编号，返回原标题
    return title


def test_chapter_numbers():
    """测试章节编号"""
    print('测试章节编号：')
    print('=' * 60)

    # 单一文件
    titles = [
        '封面',
        '公司概况',
        '公司简介',
        '技术方案',
        '设备说明一览表',
        '二、法定代表人授权书',
        '三、投标保证金缴纳证明',
        '九、近三年无重大违法记录声明',
        '十二、质量控制专项方案',
    ]
    print('\n单一文件：')
    for title in titles:
        numbered_title = get_chapter_title(title, '单一文件')
        print(f'  {title:45} -> {numbered_title}')

    # 技术标
    titles = [
        '封面',
        '公司概况',
        '技术方案',
        '设备说明一览表',
        '九、近三年无重大违法记录声明',
        '十二、质量控制专项方案',
    ]
    print('\n技术标：')
    for title in titles:
        numbered_title = get_chapter_title(title, '技术标')
        print(f'  {title:45} -> {numbered_title}')

    # 商务标
    titles = ['封面', '公司概况', '商务承诺']
    print('\n商务标：')
    for title in titles:
        numbered_title = get_chapter_title(title, '商务标')
        print(f'  {title:45} -> {numbered_title}')

    print()
    print('=' * 60)


if __name__ == '__main__':
    test_chapter_numbers()
    print('✅ 章节编号测试完成')
