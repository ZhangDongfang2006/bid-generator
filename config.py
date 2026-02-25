"""
投标文件自动生成系统 - 配置文件
"""

import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent

# 数据目录
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "templates"
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"

# 创建目录
for dir_path in [DATA_DIR, TEMPLATES_DIR, UPLOADS_DIR, OUTPUT_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# 公司基本信息
COMPANY_INFO = {
    "name": "海越（湖北）电气股份有限公司",
    "name_en": "Haiyue (Hubei) Electric Co., Ltd.",
    "address": "湖北省孝感市孝昌县经济开发区华阳大道188-1号",
    "postal_code": "432999",
    "email": "info@nbhaiyue.com",
    "phone": "+86-0712-8303818",
    "fax": "86-0712-8303818",
    "website": "www.haiyueelec.com",
    "service_hotline": "400-882-9910",
    "business_contact": "阎海",
    "business_phone": "13586872525",
}

# 生产基地信息
PRODUCTION_BASES = [
    {
        "name": "湖北生产基地",
        "address": "湖北省孝感市孝昌县经济开发区华阳大道188-1号",
    },
    {
        "name": "宁波生产基地",
        "address": "宁波市镇海骆驼机电园区盛兴路348号",
    },
]

# 主营产品
MAIN_PRODUCTS = {
    "high_voltage": {
        "name": "高压成套配电设备",
        "products": [
            "KYN28A-12户内交流金属铠装移开式开关设备",
            "XGN2-12箱式固定式金属封闭开关设备",
            "35kV开关柜",
            "40.5kV开关柜",
            "过电压抑制柜",
            "母线桥",
        ],
    },
    "low_voltage": {
        "name": "低压成套配电设备",
        "products": [
            "MNS低压抽出式开关柜",
            "GCS低压抽出式开关柜",
            "GGD低压固定式开关柜",
            "XL系列动力配电箱",
            "PZ30照明配电箱",
        ],
    },
    "prefabricated": {
        "name": "预制舱式变电站",
        "products": [
            "箱式变电站",
            "升压预制舱",
            "智能预制舱",
            "移动变电站",
        ],
    },
}

# 合作伙伴
PARTNERS = [
    "中天钢铁集团",
    "国家电网",
    "中国电信",
    "中国联通",
    "中国能建",
    "中国电建",
    "葛洲坝集团",
]

# 投标文件模板
BID_TEMPLATES = {
    "cover": "templates/bid_cover.docx",
    "company_intro": "templates/company_intro.docx",
    "tech_solution": "templates/tech_solution.docx",
    "commercial": "templates/commercial.docx",
    "qualifications": "templates/qualifications.docx",
    "performance": "templates/performance.docx",
    "after_sales": "templates/after_sales.docx",
    "commitment": "templates/commitment.docx",
}

# AI 配置（预留接口）
AI_CONFIG = {
    "enabled": False,  # 如果有AI API，设置为True
    "api_key": "",
    "api_url": "",
    "model": "",
}

# 默认报价配置
QUOTE_CONFIG = {
    "tax_rate": 0.13,  # 13%增值税
    "delivery_days": 30,  # 默认交货期30天
    "warranty_period": "一年",  # 质保期
    "quote_validity_days": 30,  # 报价有效期30天
}
