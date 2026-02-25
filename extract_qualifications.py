#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从海越湖北电气资质文件PDF中提取信息并更新到投标生成系统
"""

import pdfplumber
import pytesseract
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# 文件路径
PDF_PATH = "/Users/zhangdongfang/Downloads/海越湖北电气资质文件.pdf"
DATA_DIR = Path(__file__).parent / "data"

# OCR 配置
TESSERACT_CONFIG = '--psm 6 --oem 3'

class QualificationExtractor:
    """资质信息提取器"""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.company_info = {}
        self.qualifications = []
        self.cases = []
        self.products = []
        self.certificates = []
        self.honors = []
        self.equipment = []

    def ocr_page(self, page_num: int, page) -> str:
        """OCR识别单页"""
        print(f"正在OCR识别第{page_num+1}页...")
        try:
            img = page.to_image()
            text = pytesseract.image_to_string(img.original, lang='chi_sim', config=TESSERACT_CONFIG)
            return text
        except Exception as e:
            print(f"OCR识别第{page_num+1}页失败: {e}")
            return ""

    def extract_company_info(self, text: str, page_num: int):
        """提取公司基本信息"""
        # 公司名称
        company_patterns = [
            r'海越[（\(]湖北[）\)]电气股份有限公司',
            r'宁波海越电器制造有限公司',
        ]
        for pattern in company_patterns:
            match = re.search(pattern, text)
            if match and not self.company_info.get('name'):
                self.company_info['name'] = match.group()
                print(f"找到公司名称: {self.company_info['name']}")

        # 注册资本
        capital_patterns = [
            r'注册资本[：:\s]*([\d,.]+)\s*(万元|元)',
            r'Registered Capital[：:\s]*([\d,.]+)',
        ]
        for pattern in capital_patterns:
            match = re.search(pattern, text)
            if match and not self.company_info.get('capital'):
                self.company_info['capital'] = match.group(1) + (match.group(2) if match.group(2) else '')
                print(f"找到注册资本: {self.company_info['capital']}")

        # 成立时间
        date_patterns = [
            r'始创于\s*(\d{4})年',
            r'成立时间[：:\s]*(\d{4})',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match and not self.company_info.get('founded'):
                self.company_info['founded'] = match.group(1)
                print(f"找到成立时间: {self.company_info['founded']}")

        # 员工人数
        employee_patterns = [
            r'员工[：:\s]*(\d+)\s*人',
            r'员工数[：:\s]*(\d+)',
        ]
        for pattern in employee_patterns:
            match = re.search(pattern, text)
            if match and not self.company_info.get('employees'):
                self.company_info['employees'] = match.group(1)
                print(f"找到员工人数: {self.company_info['employees']}")

        # 厂房面积
        area_patterns = [
            r'厂房面积[：:\s]*([\d,.]+)\s*(m²|平方米)',
        ]
        for pattern in area_patterns:
            match = re.search(pattern, text)
            if match and not self.company_info.get('area'):
                self.company_info['area'] = match.group(1) + 'm²'
                print(f"找到厂房面积: {self.company_info['area']}")

    def extract_qualification(self, text: str, page_num: int):
        """提取资质证书信息"""
        # 质量管理体系认证
        quality_patterns = [
            r'质量管理体系认证证书[^\n]*证书号[：:\s]*([A-Z\d]+)',
            r'证者号[：:\s]*([A-Z0-9]+)',
        ]
        for pattern in quality_patterns:
            match = re.search(pattern, text)
            if match:
                cert_no = match.group(1)
                # 检查是否已存在
                if not any(q.get('cert_no') == cert_no for q in self.qualifications):
                    self.qualifications.append({
                        'name': '质量管理体系认证',
                        'level': 'GB/T19001-2016/ISO9001:2015',
                        'cert_no': cert_no,
                        'valid_until': '2025-12-31',  # 需要从文本中提取
                        'cert_file': '',
                        'page': page_num + 1
                    })
                    print(f"找到资质: 质量管理体系认证 - {cert_no}")

        # 电力工程施工总承包
        construction_patterns = [
            r'电力工程施工总承包[^\n]*([一二三四]级|Level\s*[1-4])',
        ]
        for pattern in construction_patterns:
            match = re.search(pattern, text)
            if match:
                level = match.group(1)
                # 检查是否已存在
                if not any(q.get('name') == '电力工程施工总承包' for q in self.qualifications):
                    self.qualifications.append({
                        'name': '电力工程施工总承包',
                        'level': level,
                        'cert_no': '',
                        'valid_until': '',
                        'cert_file': '',
                        'page': page_num + 1
                    })
                    print(f"找到资质: 电力工程施工总承包 - {level}")

    def extract_case(self, text: str, page_num: int):
        """提取业绩案例"""
        # 查找项目名称
        project_patterns = [
            r'项目名称[：:\s]*([^\n]{5,50})',
            r'([^\n]{10,30})[项目工程]',
        ]

        lines = text.split('\n')
        for i, line in enumerate(lines):
            # 查找包含"项目"、"工程"的行
            if '项目' in line or '工程' in line or '厂' in line:
                # 尝试提取项目信息
                if len(line) > 5 and len(line) < 100:
                    # 查找金额
                    amount_patterns = [r'([\d,.]+)\s*(万元|元)']
                    for pattern in amount_patterns:
                        match = re.search(pattern, line)
                        if match:
                            amount = match.group(1).replace(',', '')
                            unit = match.group(2)
                            if unit == '万元':
                                amount = float(amount) * 10000
                            else:
                                amount = float(amount)

                            # 检查是否已存在
                            if not any(c.get('project_name') == line.strip() for c in self.cases):
                                self.cases.append({
                                    'project_name': line.strip(),
                                    'client': '',
                                    'industry': '电力',
                                    'product_type': '配电设备',
                                    'amount': amount,
                                    'year': 2025,
                                    'description': f'第{page_num+1}页提取',
                                    'page': page_num + 1
                                })
                                print(f"找到业绩: {line.strip()} - {amount}元")
                                break

    def extract_product(self, text: str, page_num: int):
        """提取产品信息"""
        # 产品型号模式
        model_patterns = [
            r'KYN\d+-\d+',
            r'MNS',
            r'GCS',
            r'ZGS\d+',
            r'XGN\d+',
            r'HXGN',
            r'GGD',
            r'XL-\d+',
        ]

        # 产品名称模式
        product_names = [
            '开关柜', '变压器', '配电箱', '断路器',
            '接触器', '继电器', '电容器', '电抗器',
        ]

        for pattern in model_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                model = match.group().upper()
                # 尝试获取产品名称
                context_start = max(0, match.start() - 30)
                context_end = min(len(text), match.end() + 30)
                context = text[context_start:context_end]

                category = '配电设备'
                for name in product_names:
                    if name in context:
                        category = name
                        break

                # 检查是否已存在
                if not any(p.get('model') == model for p in self.products):
                    self.products.append({
                        'name': f'{category} {model}',
                        'model': model,
                        'category': category,
                        'description': f'第{page_num+1}页提取',
                        'base_price': 0,
                        'page': page_num + 1
                    })
                    print(f"找到产品: {model} - {category}")

    def process(self):
        """处理整个PDF"""
        print("=" * 80)
        print("开始提取海越湖北电气资质文件信息")
        print("=" * 80)

        with pdfplumber.open(self.pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"PDF总页数: {total_pages}")
            print()

            # 关键词定位
            keywords_section = {
                '企业简介': [1, 5],
                '资质证书': [10, 50],
                '产品认证': [20, 80],
                '业绩案例': [80, 150],
                '生产设备': [150, 180],
                '售后服务': [180, 200],
            }

            for section, (start, end) in keywords_section.items():
                print(f"\n--- 提取{section} (第{start}-{end}页) ---")
                for page_num in range(start-1, min(end, total_pages)):
                    page = pdf.pages[page_num]
                    text = self.ocr_page(page_num, page)

                    if section == '企业简介':
                        self.extract_company_info(text, page_num)
                    elif section == '资质证书':
                        self.extract_qualification(text, page_num)
                    elif section == '产品认证':
                        self.extract_product(text, page_num)
                    elif section == '业绩案例':
                        self.extract_case(text, page_num)

        # 输出结果
        print("\n" + "=" * 80)
        print("提取完成！统计结果：")
        print("=" * 80)
        print(f"公司信息: {len(self.company_info)} 项")
        print(f"资质证书: {len(self.qualifications)} 项")
        print(f"产品信息: {len(self.products)} 项")
        print(f"业绩案例: {len(self.cases)} 项")

        return {
            'company_info': self.company_info,
            'qualifications': self.qualifications,
            'products': self.products,
            'cases': self.cases,
        }


def update_database(extracted_data: Dict):
    """更新数据库"""
    print("\n" + "=" * 80)
    print("开始更新数据库...")
    print("=" * 80)

    # 更新资质
    qual_file = DATA_DIR / "qualifications.json"
    qual_data = json.loads(qual_file.read_text(encoding='utf-8'))

    for qual in extracted_data['qualifications']:
        # 检查是否已存在
        if not any(q.get('cert_no') == qual['cert_no'] for q in qual_data['qualifications']):
            qual_data['qualifications'].append({
                'id': len(qual_data['qualifications']) + 1,
                'name': qual['name'],
                'level': qual['level'],
                'cert_no': qual['cert_no'],
                'valid_until': qual['valid_until'],
                'cert_file': qual['cert_file'],
                'created_at': datetime.now().isoformat()
            })
            print(f"✓ 已添加资质: {qual['name']}")

    qual_file.write_text(json.dumps(qual_data, ensure_ascii=False, indent=2), encoding='utf-8')

    # 更新产品
    product_file = DATA_DIR / "products.json"
    product_data = json.loads(product_file.read_text(encoding='utf-8'))

    for product in extracted_data['products']:
        # 检查是否已存在
        if not any(p.get('model') == product['model'] for p in product_data['products']):
            product_data['products'].append({
                'id': len(product_data['products']) + 1,
                'name': product['name'],
                'model': product['model'],
                'category': product['category'],
                'description': product['description'],
                'base_price': product['base_price'],
                'created_at': datetime.now().isoformat()
            })
            print(f"✓ 已添加产品: {product['name']}")

    product_file.write_text(json.dumps(product_data, ensure_ascii=False, indent=2), encoding='utf-8')

    # 更新案例
    case_file = DATA_DIR / "cases.json"
    case_data = json.loads(case_file.read_text(encoding='utf-8'))

    for case in extracted_data['cases']:
        # 检查是否已存在
        if not any(c.get('project_name') == case['project_name'] for c in case_data['cases']):
            case_data['cases'].append({
                'id': len(case_data['cases']) + 1,
                'project_name': case['project_name'],
                'client': case['client'],
                'industry': case['industry'],
                'product_type': case['product_type'],
                'amount': case['amount'],
                'year': case['year'],
                'description': case['description'],
                'created_at': datetime.now().isoformat()
            })
            print(f"✓ 已添加案例: {case['project_name']}")

    case_file.write_text(json.dumps(case_data, ensure_ascii=False, indent=2), encoding='utf-8')

    print("\n" + "=" * 80)
    print("数据库更新完成！")
    print("=" * 80)

    # 输出统计
    print(f"\n当前数据库状态：")
    print(f"资质: {len(qual_data['qualifications'])} 项")
    print(f"产品: {len(product_data['products'])} 项")
    print(f"案例: {len(case_data['cases'])} 项")


def main():
    """主函数"""
    extractor = QualificationExtractor(PDF_PATH)
    extracted_data = extractor.process()

    # 保存提取结果到文件
    output_file = DATA_DIR / "提取结果_智能.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=2)
    print(f"\n提取结果已保存到: {output_file}")

    # 更新数据库
    update_database(extracted_data)


if __name__ == "__main__":
    main()
