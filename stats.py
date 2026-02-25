#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库统计脚本 - 显示当前数据状态
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

def load_json(filepath):
    """加载JSON文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    print("=" * 80)
    print("海越湖北电气投标生成系统 - 数据库统计")
    print("=" * 80)
    print()

    # 1. 资质统计
    qual_file = DATA_DIR / "qualifications.json"
    qual_data = load_json(qual_file)

    print("【资质证书】")
    print(f"  总计：{len(qual_data['qualifications'])} 项")
    print()
    print("  主要资质：")
    for qual in qual_data['qualifications'][:5]:
        print(f"    - {qual['name']} ({qual['level']})")
    if len(qual_data['qualifications']) > 5:
        print(f"    ... 还有 {len(qual_data['qualifications']) - 5} 项")
    print()

    # 证书和荣誉
    print(f"  产品认证：{len(qual_data['certificates'])} 项")
    for cert in qual_data['certificates']:
        print(f"    - {cert['name']}")
    print()

    print(f"  企业荣誉：{len(qual_data['honors'])} 项")
    for honor in qual_data['honors']:
        print(f"    - {honor['name']} ({honor['year']})")
    print()

    # 2. 产品统计
    product_file = DATA_DIR / "products.json"
    product_data = load_json(product_file)

    print("【产品信息】")
    print(f"  总计：{len(product_data['products'])} 个产品")
    print()

    # 按类别统计
    categories = {}
    for product in product_data['products']:
        category = product['category']
        categories[category] = categories.get(category, 0) + 1

    for category, count in categories.items():
        print(f"  {category}：{count} 个")
    print()

    # 价格范围
    prices = [p['base_price'] for p in product_data['products'] if p['base_price'] > 0]
    if prices:
        print(f"  价格范围：{min(prices):,.0f} 元 - {max(prices):,.0f} 元")
    print()

    # 3. 案例统计
    case_file = DATA_DIR / "cases.json"
    case_data = load_json(case_file)

    print("【业绩案例】")
    print(f"  总计：{len(case_data['cases'])} 个案例")
    print()

    # 按行业统计
    industries = {}
    for case in case_data['cases']:
        industry = case['industry']
        industries[industry] = industries.get(industry, 0) + 1

    print("  按行业分布：")
    for industry, count in sorted(industries.items(), key=lambda x: x[1], reverse=True):
        print(f"    - {industry}：{count} 项")
    print()

    # 按年份统计
    years = {}
    for case in case_data['cases']:
        year = case['year']
        years[year] = years.get(year, 0) + 1

    print("  按年份分布：")
    for year, count in sorted(years.items(), reverse=True):
        print(f"    - {year} 年：{count} 项")
    print()

    # 金额统计
    amounts = [c['amount'] for c in case_data['cases']]
    if amounts:
        print(f"  金额范围：{min(amounts):,.0f} 元 - {max(amounts):,.0f} 元")
        print(f"  金额总计：{sum(amounts):,.0f} 元")
        print(f"  平均金额：{sum(amounts)/len(amounts):,.0f} 元")
    print()

    # 4. 人员统计
    personnel_file = DATA_DIR / "personnel.json"
    personnel_data = load_json(personnel_file)

    all_personnel = []
    for category in personnel_data:
        all_personnel.extend(personnel_data[category])

    print("【人员信息】")
    print(f"  总计：{len(all_personnel)} 人")
    print()

    print("  按职位分类：")
    for category in personnel_data:
        count = len(personnel_data[category])
        print(f"    - {category}：{count} 人")
    print()

    # 平均工龄
    experiences = [p['experience'] for p in all_personnel if p.get('experience')]
    if experiences:
        print(f"  平均工龄：{sum(experiences)/len(experiences):.1f} 年")
        print(f"  最长工龄：{max(experiences)} 年")
    print()

    # 5. 合作伙伴
    print("【合作伙伴】")
    partners = ["中天钢铁集团", "国家电网", "中国电信", "中国联通", "中国能建", "中国电建", "葛洲坝集团"]
    print(f"  主要合作伙伴：{len(partners)} 家")
    for partner in partners:
        print(f"    - {partner}")
    print()

    print("=" * 80)
    print("数据统计完成！")
    print("=" * 80)
    print()
    print("提示：使用 'streamlit run app.py' 启动投标生成系统查看详情")

if __name__ == "__main__":
    main()
