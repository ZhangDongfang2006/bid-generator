#!/usr/bin/env python3
"""
测试实际的匹配流程，看看为什么只匹配到一个证书
"""

import sys
sys.path.insert(0, '/Users/zhangdongfang/workspace/bid-generator')

from pathlib import Path
import json
from database import CompanyDatabase

# 读取资质数据
data_dir = Path('/Users/zhangdongfang/workspace/bid-generator/data')
with open(data_dir / 'qualifications.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

all_qualifications = data.get('qualifications', [])

print(f"数据库中总共有 {len(all_qualifications)} 个证书")
print()

# 初始化数据库
db = CompanyDatabase(data_dir=data_dir)

# 测试几种不同的资质要求
test_requirements_list = [
    ["体系认证", "AAA"],  # 应该匹配到多个证书
    ["质量体系"],  # 应该匹配到质量管理体系认证
    ["高压开关", "低压开关"],  # 应该匹配到多个报告
    [],  # 空要求，应该返回前10个
]

for i, test_reqs in enumerate(test_requirements_list, 1):
    print(f"测试 {i}: 资质要求 = {test_reqs}")
    
    matched = db.match_qualifications(test_reqs)
    print(f"  匹配到 {len(matched)} 个证书")
    
    for j, cert in enumerate(matched[:5], 1):
        has_file = '有PDF' if cert.get('cert_file') else '无PDF'
        print(f"    {j}. {cert['name']} ({cert['level']}) [{has_file}]")
    
    if len(matched) > 5:
        print(f"    ... 还有 {len(matched) - 5} 个证书")
    print()
