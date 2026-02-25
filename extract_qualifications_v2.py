#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从海越湖北电气资质文件PDF中提取信息并更新到投标生成系统 V2
改进版：只处理关键页面，提高效率
"""

import pdfplumber
import pytesseract
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import sys

# 文件路径
PDF_PATH = "/Users/zhangdongfang/Downloads/海越湖北电气资质文件.pdf"
DATA_DIR = Path(__file__).parent / "data"

# OCR 配置 - 优化速度
TESSERACT_CONFIG = '--psm 6 --oem 3'

class QualificationExtractorV2:
    """资质信息提取器 V2"""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.company_info = {}
        self.qualifications = []
        self.cases = []
        self.products = []
        self.certificates = []
        self.honors = []

    def ocr_page(self, page_num: int, page) -> str:
        """OCR识别单页"""
        try:
            img = page.to_image()
            text = pytesseract.image_to_string(img.original, lang='chi_sim', config=TESSERACT_CONFIG)
            print(f"  ✓ 第{page_num+1}页识别完成")
            return text
        except Exception as e:
            print(f"  ✗ 第{page_num+1}页识别失败: {e}")
            return ""

    def extract_company_info(self, text: str, page_num: int):
        """提取公司基本信息"""
        if self.company_info.get('name'):
            return  # 已提取过

        # 公司名称
        if '海越' in text and '电气' in text:
            match = re.search(r'海越[（\(]湖北[）\)]电气股份有限公司', text)
            if match:
                self.company_info['name'] = match.group()
                print(f"    找到公司名称: {self.company_info['name']}")

        # 注册资本
        match = re.search(r'注册资本[：:\s]*([\d,.]+)\s*(万元|元)', text)
        if match and not self.company_info.get('capital'):
            self.company_info['capital'] = match.group(1) + (match.group(2) if match.group(2) else '')
            print(f"    找到注册资本: {self.company_info['capital']}")

        # 成立时间
        match = re.search(r'始创于\s*(\d{4})年|成立于\s*(\d{4})', text)
        if match and not self.company_info.get('founded'):
            year = match.group(1) if match.group(1) else match.group(2)
            self.company_info['founded'] = year
            print(f"    找到成立时间: {self.company_info['founded']}")

        # 员工人数
        match = re.search(r'员工[：:\s]*(\d+)\s*人', text)
        if match and not self.company_info.get('employees'):
            self.company_info['employees'] = match.group(1)
            print(f"    找到员工人数: {self.company_info['employees']}")

        # 厂房面积
        match = re.search(r'(\d+)\s*m²|(\d+)\s*平方米', text)
        if match and not self.company_info.get('area'):
            area = match.group(1) if match.group(1) else match.group(2)
            self.company_info['area'] = area + 'm²'
            print(f"    找到厂房面积: {self.company_info['area']}")

    def extract_qualification(self, text: str, page_num: int):
        """提取资质证书信息"""
        # 质量管理体系认证
        match = re.search(r'质量管理体系[^\n]*认证[^\n]*证者号[：:\s]*([A-Z\d]+)', text)
        if match:
            cert_no = match.group(1)
            if not any(q.get('cert_no') == cert_no for q in self.qualifications):
                self.qualifications.append({
                    'name': '质量管理体系认证',
                    'level': 'GB/T19001-2016/ISO9001:2015',
                    'cert_no': cert_no,
                    'valid_until': '2025-12-31',
                    'cert_file': '',
                    'page': page_num + 1
                })
                print(f"    找到资质: 质量管理体系认证 - {cert_no}")

        # 资质名称和级别
        patterns = [
            ('电力工程施工总承包', r'电力工程施工总承包[^\n]*([一二三四]级)'),
            ('承装承修承试', r'承装[（\(]修[）\)]试[^\n]*([一二三四]级)'),
            ('安全生产许可证', r'安全生产许可证[^\n]*许可证号[：:\s]*([A-Z\d]+)'),
        ]

        for name, pattern in patterns:
            match = re.search(pattern, text)
            if match:
                level = match.group(1)
                if not any(q.get('name') == name for q in self.qualifications):
                    self.qualifications.append({
                        'name': name,
                        'level': level,
                        'cert_no': '',
                        'valid_until': '',
                        'cert_file': '',
                        'page': page_num + 1
                    })
                    print(f"    找到资质: {name} - {level}")

    def extract_product(self, text: str, page_num: int):
        """提取产品信息"""
        # 常见产品型号
        model_patterns = [
            r'KYN\d+-\d+', r'MNS', r'GCS', r'ZGS\d+',
            r'XGN\d+', r'HXGN', r'GGD', r'XL-\d+', r'GGJ',
            r'XGN15', r'KYN61', r'GCK', r'Blokset',
        ]

        # 产品类型
        product_types = {
            '开关柜': '高压开关柜',
            '变压器': '变压器',
            '配电箱': '低压开关柜',
            '断路器': '开关设备',
            '接触器': '低压电器',
            '继电器': '保护装置',
            '电容器': '无功补偿',
            '电抗器': '无功补偿',
        }

        for pattern in model_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                model = match.group().upper()

                # 检查是否已存在
                if any(p.get('model') == model for p in self.products):
                    continue

                # 确定产品类型
                context = text[max(0, match.start()-20):min(len(text), match.end()+20)]
                category = '配电设备'
                for type_name, category_name in product_types.items():
                    if type_name in context:
                        category = category_name
                        break

                self.products.append({
                    'name': f'{category} {model}',
                    'model': model,
                    'category': category,
                    'description': f'第{page_num+1}页提取',
                    'base_price': 0,
                    'page': page_num + 1
                })
                print(f"    找到产品: {model} - {category}")

    def extract_case(self, text: str, page_num: int):
        """提取业绩案例"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        for line in lines:
            # 查找金额
            amount_match = re.search(r'([\d,.]+)\s*(万元|元)', line)
            if not amount_match:
                continue

            amount = float(amount_match.group(1).replace(',', ''))
            unit = amount_match.group(2)
            if unit == '万元':
                amount = amount * 10000

            # 如果行中包含"项目"、"工程"、"厂"等关键词，认为是案例
            if len(line) > 10 and len(line) < 80:
                if any(keyword in line for keyword in ['项目', '工程', '厂', '公司', '集团']):
                    # 检查是否已存在
                    if not any(c.get('project_name') == line for c in self.cases):
                        self.cases.append({
                            'project_name': line,
                            'client': '',
                            'industry': '电力',
                            'product_type': '配电设备',
                            'amount': amount,
                            'year': 2025,
                            'description': f'第{page_num+1}页提取',
                            'page': page_num + 1
                        })
                        print(f"    找到案例: {line[:50]}...")

    def process(self):
        """处理整个PDF"""
        print("=" * 80)
        print("开始提取海越湖北电气资质文件信息")
        print("=" * 80)

        with pdfplumber.open(self.pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"PDF总页数: {total_pages}")
            print()

            # 只处理关键页面区间
            sections = [
                ('企业简介', [2, 10], 'extract_company_info'),
                ('资质证书', [10, 40], 'extract_qualification'),
                ('产品目录', [40, 70], 'extract_product'),
                ('业绩案例', [70, 130], 'extract_case'),
            ]

            for section_name, (start, end), extract_method in sections:
                print(f"\n--- 提取{section_name} (第{start}-{end}页) ---")

                for page_num in range(start-1, min(end, total_pages)):
                    page = pdf.pages[page_num]
                    text = self.ocr_page(page_num, page)

                    # 调用对应的提取方法
                    getattr(self, extract_method)(text, page_num)

                    # 每处理10页输出一次进度
                    if (page_num - start + 2) % 10 == 0:
                        print(f"  进度: {page_num - start + 2}/{end - start + 1} 页")

        # 输出统计结果
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

    for case in extracted_data['cases'][:20]:  # 最多添加20个案例
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
            print(f"✓ 已添加案例: {case['project_name'][:40]}...")

    case_file.write_text(json.dumps(case_data, ensure_ascii=False, indent=2), encoding='utf-8')

    print("\n" + "=" * 80)
    print("数据库更新完成！")
    print("=" * 80)

    print(f"\n当前数据库状态：")
    print(f"资质: {len(qual_data['qualifications'])} 项")
    print(f"产品: {len(product_data['products'])} 项")
    print(f"案例: {len(case_data['cases'])} 项")


def main():
    """主函数"""
    print("开始运行提取脚本...\n")
    sys.stdout.flush()

    extractor = QualificationExtractorV2(PDF_PATH)
    extracted_data = extractor.process()

    # 保存提取结果
    output_file = DATA_DIR / "提取结果.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=2)
    print(f"\n提取结果已保存到: {output_file}")

    # 更新数据库
    update_database(extracted_data)

    print("\n✓ 所有操作完成！")


if __name__ == "__main__":
    main()
