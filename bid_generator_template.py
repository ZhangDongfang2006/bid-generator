#!/usr/bin/env python3
"""
投标文件生成器（按照参考模板）
- 根据参考 PDF 的结构生成投标文件
- 报价清单、备件清单等只做框架，内容留空
- 其他章节按照参考文件答题方式生成
- 使用分类后的图片
"""

import json
import os
from pathlib import Path
from datetime import datetime
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Alignment
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml.ns.qformat import CT_Boolean

class BidDocumentGenerator:
    """投标文件生成器"""
    
    def __init__(self, config_file='config.py', data_dir='data'):
        """初始化生成器"""
        self.data_dir = Path(data_dir)
        self.images_dir = self.data_dir / 'images'
        
        # 加载配置
        try:
            import config
            self.company_info = config.COMPANY_INFO
        except Exception as e:
            print(f"✗ 加载配置失败: {e}")
            # 使用默认配置
            self.company_info = {
                'company_name': 'XX(湖北）电气股份有限公司',
                'legal_rep': '',
                'phone': '',
                'email': '',
                'address': '',
                'website': ''
            }
        
        # 加载数据
        self.personnel = self._load_json('personnel.json')
        self.qualifications = self._load_json('qualifications.json')
        self.cases = self._load_json('cases.json')
        self.products = self._load_json('products.json')
        
        # 文档
        self.doc = None
        
        # 图片目录
        self.image_dirs = {
            'projects': self.images_dir / 'projects',
            'products': self.images_dir / 'products',
            'certificates': self.images_dir / 'certificates',
            'documents': self.images_dir / 'documents',
            'charts': self.images_dir / 'charts',
            'others': self.images_dir / 'others'
        }
    
    def _load_json(self, filename):
        """加载 JSON 数据文件"""
        file_path = self.data_dir / filename
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def create_document(self):
        """创建 Word 文档"""
        self.doc = Document()
        
        # 设置页边距（A4）
        sections = self.doc.sections
        for section in sections:
            section.top_margin = Pt(36)  # 1.27cm
            section.bottom_margin = Pt(36)
            section.left_margin = Pt(36)
            section.right_margin = Pt(36)
        
        return self.doc
    
    def add_heading(self, text, level=1):
        """添加标题"""
        heading = self.doc.add_heading(text, level=level)
        # 设置标题格式
        heading.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        return heading
    
    def add_paragraph(self, text, bold=False, alignment=WD_PARAGRAPH_ALIGNMENT.LEFT):
        """添加段落"""
        p = self.doc.add_paragraph(text)
        p.alignment = alignment
        if bold:
            for run in p.runs:
                run.bold = True
        return p
    
    def add_table(self, data, headers=None, style='Light Grid Accent 1'):
        """添加表格"""
        if not data:
            return None
        
        # 转换数据为列表
        if isinstance(data[0], dict):
            # 字典列表，需要提取 keys 作为 headers
            if not headers:
                headers = list(data[0].keys())
            
            table_data = []
            for row in data:
                table_data.append([row.get(key, '') for key in headers])
        else:
            # 直接是列表
            table_data = data
        
        # 创建表格
        table = self.doc.add_table(rows=len(table_data), cols=len(table_data[0]))
        table.style = style
        
        # 添加表头
        if headers:
            for i, header in enumerate(headers):
                table.rows[0].cells[i].text = header
                table.rows[0].cells[i].paragraphs[0].runs[0].bold = True
        
        # 添加数据
        for i, row in enumerate(table_data, 1):
            for j, cell_data in enumerate(row):
                table.rows[i].cells[j].text = str(cell_data)
        
        return table
    
    def add_image(self, image_path, width=Inches(5.5)):
        """添加图片"""
        if not Path(image_path).exists():
            return None
        
        try:
            self.doc.add_picture(image_path, width=width)
            return True
        except Exception as e:
            print(f"✗ 添加图片失败: {image_path} - {e}")
            return False
    
    def get_images_from_dir(self, category, limit=None):
        """获取指定分类的图片"""
        img_dir = self.image_dirs.get(category)
        if not img_dir or not img_dir.exists():
            return []
        
        images = sorted(img_dir.glob('*.jpeg'))
        if limit:
            images = images[:limit]
        
        return images
    
    def generate_tender_letter(self):
        """生成投标函（第一章）"""
        self.add_heading('一、投标函', level=1)
        self.add_paragraph()  # 空行
        
        # 投标函内容
        content = f"""尊敬的汉西污水处理厂三期工程（低压开关柜、动力配电箱等采购及伴随服务）项目招标人：

根据贵方《汉西污水处理厂三期工程电气设备（低压开关柜、动力配电箱等）采购及伴随服务 招标文件》的投标邀请，我方经过对招标文件的认真研究，决定参加本项目的投标。

我方郑重声明，我方投标文件的所有内容以及所附资料均为真实、准确、完整，并愿意对其中任何不真实、不准确、不完整之处承担全部责任。

我方愿意按照贵方招标文件的要求和合同规定，完成本项目的供货及伴随服务工作。

本投标文件所附资料如与招标文件不一致的，以招标文件为准。

特此声明。

投标单位：{self.company_info['company_name']}
法定代表人或其授权代理人：（签字或盖章）
日  期：{datetime.now().strftime('%Y年%m月%d日')}
"""
        
        self.add_paragraph(content)
        self.add_paragraph()
    
    def generate_tender_overview(self):
        """生成投标一览表（第二章）"""
        self.add_heading('二、投标一览表', level=1)
        self.add_paragraph()
        
        # 创建表格
        headers = ['项目名称', '投标报价（元）', '交货期', '备注']
        data = [
            ['汉西污水处理厂三期工程电气设备（低压开关柜、动力配电箱等）采购及伴随服务', 
             '（待填写）', 
             '（待填写）', 
             '']
        ]
        
        table = self.add_table(data, headers)
        
        self.add_paragraph()
        self.add_paragraph("注：本表为投标一览表框架，投标报价需在分部分项报价清单中体现。", bold=False)
        self.add_paragraph()
    
    def generate_legal_rep_info(self):
        """生成法定代表人身份证明（第三章）"""
        self.add_heading('三、法定代表人身份证明', level=1)
        self.add_paragraph()
        
        content = f"""法定代表人身份证明

本人{self.company_info['legal_rep']}（姓名：{self.company_info['legal_rep']}，身份证号：{self.personnel.get('legal_rep_id_card', '（待填写）'}），系{self.company_info['company_name']}的法定代表人。

特此证明。

投标单位：{self.company_info_company_name']}
（盖章）
法定代表人：（签字）
日  期：{datetime.now().strftime('%Y年%m月%d日')}
"""
        
        self.add_paragraph(content)
        self.add_paragraph()
        
        # 添加身份证图片（如果存在）
        id_card_images = self.get_images_from_dir('documents', limit=1)
        for img_path in id_card_images:
            self.add_image(img_path)
    
    def generate_legal_rep_authorization(self):
        """生成法定代表人授权委托书（第四章）"""
        self.add_heading('四、法定代表人授权委托书', level=1)
        self.add_paragraph()
        
        # 使用文档目录中的授权书图片
        auth_images = self.get_images_from_dir('documents')
        if auth_images:
            for img_path in auth_images[:2]:
                self.add_image(img_path)
        
        self.add_paragraph()
        
        # 授权委托书内容
        content = f"""法定代表人授权委托书

本授权委托书声明：我，{self.company_info['legal_rep']}，系{self.company_info['company_name']}的法定代表人，现授权{self.personnel.get('authorized_rep', '（待填写）'}（姓名：{self.personnel.get('authorized_rep', '（待填写）'}，职务：{self.personnel.get('authorized_rep_title', '（待填写）'}）为我方的合法代理人，就贵方组织{self.company_info['company_name']}参加"汉西污水处理厂三期工程电气设备（低压开关柜、动力配电箱等）采购及伴随服务"项目投标、谈判、签约等事宜，以我方名义全权处理。

委托期限：自本授权委托书签发之日起至本项目投标结束止。

授权方：{self.company_info['company_name']}
法定代表人：（签字或盖章）
委托期限：{datetime.now().strftime('%Y年%m月%d日')}
"""
        
        self.add_paragraph(content)
        self.add_paragraph()
    
    def generate_business_deviation_table(self):
        """生成商务偏离表（第五章）"""
        self.add_heading('五、商务偏离表', level=1)
        self.add_paragraph()
        
        # 创建表格（框架，内容留空）
        headers = ['条款号', '招标文件条款', '投标文件响应', '说明']
        data = [['', '', '', '']]  # 只有一行空数据作为框架
        
        table = self.add_table(data, headers)
        
        self.add_paragraph()
        self.add_paragraph("注：本表为商务偏离表框架，如有偏离请填写。", bold=False)
        self.add_paragraph()
    
    def generate_price_summary(self):
        """生成报价一览表（第六章）"""
        self.add_heading('六、报价一览表', level=1)
        self.add_paragraph()
        
        # 创建表格（框架，内容留空）
        headers = ['序号', '项目名称', '规格型号', '单位', '数量', '单价（元）', '合价（元）', '备注']
        data = [['1', '', '', '', '', '', '', '', '']]  # 一行空数据作为框架
        
        table = self.add_table(data, headers)
        
        self.add_paragraph()
        self.add_paragraph("注：本表为报价一览表框架，报价需在分部分项报价清单中体现。", bold=False)
        self.add_paragraph("     投标报价须包含所有设备及服务的费用。", bold=False)
        self.add_paragraph("     分部分项报价清单中的报价合计应与报价一览表中的总报价一致。", bold=False)
        self.add_paragraph()
    
    def generate_itemized_price_list(self):
        """生成分部分项报价清单（第七章）"""
        self.add_heading('七、分部分项报价清单', level=1)
        self.add_paragraph()
        
        # 添加产品图片
        product_images = self.get_images_from_dir('products')
        if product_images:
            self.add_paragraph("7.1 产品图片：", bold=True)
            for img_path in product_images:
                self.add_image(img_path)
            self.add_paragraph()
        
        # 创建表格（框架，内容留空）
        headers = ['序号', '项目名称', '规格型号', '单位', '数量', '单价（元）', '合价（元）', '备注']
        data = [
            ['第一部分：设备部分', '', '', '', '', '', '', ''],
            ['1', '', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', '', ''],
            ['小计', '', '', '', '', '', '', ''],
            ['第二部分：服务部分', '', '', '', '', '', '', '', ''],
            ['1', '', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', '', ''],
            ['小计', '', '', '', '', '', '', '', ''],
            ['第三部分：其他部分', '', '', '', '', '', '', '', ''],
            ['1', '', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', '', ''],
            ['小计', '', '', '', '', '', '', '', ''],
            ['总计', '', '', '', '', '', '', '', '']
        ]
        
        table = self.add_table(data, headers)
        
        self.add_paragraph()
        self.add_paragraph("注：", bold=False)
        self.add_paragraph("     1. 本表为分部分项报价清单框架，报价请根据招标文件要求填写。", bold=False)
        self.add_paragraph("     2. 报价应包含所有设备及服务的费用。", bold=False)
        self.add_paragraph("     3. 分部分项报价清单中的报价合计应与报价一览表中的总报价一致。", bold=False)
        self.add_paragraph("     4. 本表为框架，内容留空，请根据招标文件要求填写。", bold=False)
        self.add_paragraph()
    
    def generate_spare_parts_list(self):
        """生成备件清单（第八章）"""
        self.add_heading('八、备件清单', level=1)
        self.add_paragraph()
        
        # 添加产品图片
        product_images = self.get_images_from_dir('products')
        if product_images:
            self.add_paragraph("8.1 产品图片：", bold=True)
            for img_path in product_images:
                self.add_image(img_path)
            self.add_paragraph()
        
        # 创建表格（框架，内容留空）
        headers = ['序号', '备件名称', '规格型号', '单位', '数量', '单价（元）', '合价（元）', '备注']
        data = [['', '', '', '', '', '', '', '']]  # 一行空数据作为框架
        
        table = self.add_table(data, headers)
        
        self.add_paragraph()
        self.add_paragraph("注：本表为备件清单框架，内容留空。", bold=False)
        self.add_paragraph("     如有备件，请根据招标文件要求填写。", bold=False)
        self.add_paragraph("     备件清单中的报价应包含在报价一览表和分部分项报价清单的总价中。", bold=False)
        self.add_paragraph()
    
    def generate_company_qualifications(self):
        """生成企业资质证明文件（第九章）"""
        self.add_heading('九、企业资质证明文件', level=1)
        self.add_paragraph()
        
        # 9.1 体系认证证书
        self.add_heading('9.1 体系认证证书', level=2)
        self.add_paragraph()
        
        # 添加证书图片
        cert_images = self.get_images_from_dir('certificates')
        if cert_images:
            for img_path in cert_images:
                self.add_image(img_path)
            self.add_paragraph()
        
        # 9.2 企业信誉
        self.add_heading('9.2 企业信誉', level=2)
        self.add_paragraph()
        self.add_paragraph("（此处插入企业信誉证明材料）", bold=False)
        self.add_paragraph()
        
        # 9.3 荣誉证书
        self.add_heading('9.3 荣誉证书', level=2)
        self.add_paragraph()
        self.add_paragraph("（此处插入荣誉证书材料）", bold=False)
        self.add_paragraph()
        
        # 9.4 其他证书
        self.add_heading('9.4 其他证书', level=2)
        self.add_paragraph()
        self.add_paragraph("（此处插入其他证书材料）", bold=False)
        self.add_paragraph()
    
    def generate_project_performance(self):
        """生成工程业绩（第十章）"""
        self.add_heading('十、工程业绩', level=1)
        self.add_paragraph()
        
        # 10.1 类似项目一览表
        self.add_heading('10.1 类似项目一览表', level=2)
        self.add_paragraph()
        
        # 添加项目案例图片
        project_images = self.get_images_from_dir('projects')
        if project_images:
            for img_path in project_images[:5]:
                self.add_image(img_path)
            self.add_paragraph()
        
        # 创建表格
        headers = ['序号', '项目名称', '项目地点', '项目规模', '完成时间', '客户名称', '备注']
        
        data = []
        for i, case in enumerate(self.cases[:10], 1):  # 显示前10个案例
            data.append([
                i,
                case.get('project_name', ''),
                case.get('project_location', ''),
                case.get('project_scale', ''),
                case.get('completion_date', ''),
                case.get('customer', ''),
                ''
            ])
        
        if not data:
            # 如果没有案例数据，创建空表格
            data = [['1', '', '', '', '', '', '']]
        
        table = self.add_table(data, headers)
        
        self.add_paragraph()
        self.add_paragraph("注：以上为类似项目一览表。", bold=False)
        self.add_paragraph()
        
        # 10.2 业绩证明
        self.add_heading('10.2 业绩证明', level=2)
        self.add_paragraph()
        
        # 添加更多项目案例图片
        if project_images:
            self.add_paragraph("项目案例图片：", bold=True)
            for img_path in project_images[5:]:
                self.add_image(img_path)
            self.add_paragraph()
        
        self.add_paragraph("（此处插入业绩证明材料）", bold=False)
        self.add_paragraph()
    
    def generate_project_bidding_outline(self):
        """生成项目投标纲领（第十一章）"""
        self.add_heading('十一、项目投标纲领', level=1)
        self.add_paragraph()
        
        # 添加项目纲领图片
        other_images = self.get_images_from_dir('others')
       纲领_images = [img for img in other_images if '纲领' in img.name]
        
        for img_path in 纲领_images[:2]:
            self.add_image(img_path)
        self.add_paragraph()
        
        # 内容
        content = f"""11.1 投标人概况

{self.company_info['company_name']}是一家专注于电气设备研发、生产、销售和服务的高新技术企业。公司拥有一支经验丰富、技术过硬的专业团队，具备完善的研发、生产、质量保证和售后服务体系。

11.2 投标优势

11.2.1 技术优势
公司拥有先进的生产设备和完善的质量管理体系，能够提供高品质的产品和优质的服务。

11.2.2 价格优势
公司具有合理的成本控制能力和供应链管理能力，能够提供具有竞争力的价格。

11.2.3 服务优势
公司建立了完善的售后服务体系，能够及时响应客户的需求，为客户提供全方位的服务。

11.3 投标承诺

11.3.1 质量承诺
公司承诺所提供的产品符合国家相关标准和行业规范，质量可靠。

11.3.2 交货期承诺
公司承诺按照招标文件要求和合同约定的时间交货。

11.3.3 服务承诺
公司承诺提供优质的售后服务，及时处理客户反馈的问题。

11.3.4 其他承诺
公司承诺严格遵守招标文件和合同的约定，履行各项义务。
"""
        
        self.add_paragraph(content)
        self.add_paragraph()
    
    def generate_quality_control_plan(self):
        """生成质量控制专项方案（第十二章）"""
        self.add_heading('十二、质量控制专项方案', level=1)
        self.add_paragraph()
        
        # 添加质量控制方案图片
        chart_images = self.get_images_from_dir('charts')
        质量_images = [img for img in chart_images if '质量' in img.name]
        
        for img_path in 质量_images[:2]:
            self.add_image(img_path)
        self.add_paragraph()
        
        # 内容
        content = """12.1 质量控制目标

确保项目产品质量符合招标文件要求、国家相关标准和行业规范。

12.2 质量控制体系

12.2.1 质量控制组织
公司建立了完善的质量控制组织，明确质量控制职责，确保质量控制工作有效开展。

12.2.2 质量控制制度
公司建立了完善的质量控制制度，包括进货检验、过程检验、最终检验等环节，确保产品质量。

12.2.3 质量控制流程
公司建立了完善的质量控制流程，从原材料采购到产品出厂，全程质量控制。

12.3 质量控制措施

12.3.1 原材料质量控制
严格执行原材料采购检验制度，确保原材料质量符合要求。

12.3.2 生产过程质量控制
严格执行生产工艺规程，加强生产过程质量控制，确保产品质量。

12.3.3 产品检验质量控制
严格执行产品检验制度，确保产品符合标准。

12.3.4 出厂质量控制
严格执行出厂检验制度，确保产品合格出厂。

12.4 质量保证措施

12.4.1 设备保证
公司拥有先进的生产设备，确保产品质量稳定。

12.4.2 工艺保证
公司拥有先进的工艺技术，确保产品质量可靠。

12.4.3 人员保证
公司拥有一支经验丰富的技术团队，确保产品质量。

12.4.4 管理保证
公司建立了完善的质量管理体系，确保质量控制工作有效开展。

12.5 质量改进措施

公司将持续改进质量管理体系，提高产品质量和客户满意度。
"""
        
        self.add_paragraph(content)
        self.add_paragraph()
    
    def generate_quality_assurance(self):
        """生成质量保证（第十三章）"""
        self.add_heading('十三、质量保证', level=1)
        self.add_paragraph()
        
        # 添加质量保证图片
        other_images = self.get_images_from_dir('others')
        保证_images = [img for img in other_images if '保证' in img.name]
        
        for img_path in 保证_images[:2]:
            self.add_image(img_path)
        self.add_paragraph()
        
        # 内容
        content = f"""13.1 质量标准

公司所提供的产品符合以下标准：
1. 国家相关标准
2. 行业规范
3. 招标文件要求

13.2 质量管理体系

公司已通过质量管理体系认证，建立了完善的质量管理体系。

13.3 质量控制流程

公司建立了完善的质量控制流程，从原材料采购到产品出厂，全程质量控制。

13.4 质量保证措施

13.4.1 人员保证
公司拥有一支经验丰富的技术团队，确保产品质量。

13.4.2 设备保证
公司拥有先进的生产设备，确保产品质量稳定。

13.4.3 工艺保证
公司拥有先进的工艺技术，确保产品质量可靠。

13.4.4 检验保证
公司建立了完善的检验制度，确保产品合格出厂。

13.5 质量承诺

公司郑重承诺所提供的产品符合质量要求，并承担相应的质量责任。
"""
        
        self.add_paragraph(content)
        self.add_paragraph()
    
    def generate_delivery_quality_after_sales(self):
        """生成交货期、质量保证和售后服务（第十四章）"""
        self.add_heading('十四、交货期、质量保证和售后服务', level=1)
        self.add_paragraph()
        
        # 内容
        content = f"""14.1 交货期

公司承诺按照招标文件要求和合同约定的时间交货。

14.1.1 交货计划
公司制定详细的交货计划，确保按时交货。

14.1.2 交货方式
公司按照招标文件要求和合同约定的方式交货。

14.2 质量保证

14.2.1 产品质量保证
公司所提供的产品符合国家相关标准和行业规范。

14.2.2 质量责任
公司对产品质量承担相应的质量责任。

14.3 售后服务

14.3.1 售后服务承诺
公司提供优质的售后服务，及时响应客户的需求。

14.3.2 售后服务内容
公司提供以下售后服务内容：
1. 产品安装调试
2. 技术培训
3. 故障排除
4. 产品维护

14.3.3 售后服务响应时间
公司承诺在接到客户需求后 24 小时内响应。

14.3.4 售后服务期限
公司提供为期一年的免费售后服务，售后期满后提供有偿服务。
"""
        
        self.add_paragraph(content)
        self.add_paragraph()
    
    def generate_after_sales_commitment(self):
        """生成售后服务及质量承诺（第十五章）"""
        self.add_heading('十五、售后服务及质量承诺', level=1)
        self.add_paragraph()
        
        # 添加相关图片
        other_images = self.get_images_from_dir('others')
        
        self.add_paragraph("15.1 服务承诺：", bold=True)
        self.add_paragraph("（此处插入服务承诺材料）", bold=False)
        self.add_paragraph()
        
        self.add_paragraph("15.2 质量承诺：", bold=True)
        self.add_paragraph("（此处插入质量承诺材料）", bold=False)
        self.add_paragraph()
        
        # 添加其他图片
        for img_path in other_images[:5]:
            self.add_image(img_path)
        self.add_paragraph()
    
    def generate_equipment_service_qualification(self):
        """生成证明设备及服务合格性的文件（第十六章）"""
        self.add_heading('十六、证明设备及服务合格性的文件', level=1)
        self.add_paragraph()
        
        # 16.1 设备清单
        self.add_heading('16.1 设备清单', level=2)
        self.add_paragraph()
        
        # 创建表格（框架，内容留空）
        headers = ['序号', '设备名称', '规格型号', '单位', '数量', '备注']
        data = [['1', '', '', '', '', '']]  # 一行空数据作为框架
        
        table = self.add_table(data, headers)
        
        self.add_paragraph()
        self.add_paragraph("注：本表为设备清单框架，内容留空。", bold=False)
        self.add_paragraph("     设备清单中的设备应包含在报价一览表和分部分项报价清单中。", bold=False)
        self.add_paragraph()
        
        # 16.2 技术响应
        self.add_heading('16.2 技术响应', level=2)
        self.add_paragraph()
        self.add_paragraph("（此处插入技术响应材料）", bold=False)
        self.add_paragraph()
        
        # 16.3 供货进度
        self.add_heading('16.3 供货进度', level=2)
        self.add_paragraph()
        
        # 添加供货进度图表
        chart_images = self.get_images_from_dir('charts')
        进度_images = [img for img in chart_images if '进度' in img.name]
        
        for img_path in 进度_images:
            self.add_image(img_path)
        
        self.add_paragraph()
        
        # 创建供货进度表（框架）
        headers = ['序号', '设备名称', '预计供货时间', '实际供货时间', '备注']
        data = [['1', '', '', '', '']]  # 一行空数据作为框架
        
        table = self.add_table(data, headers)
        
        self.add_paragraph()
        self.add_paragraph("注：本表为供货进度表框架，内容留空。", bold=False)
        self.add_paragraph()
        
        # 16.4 施工组织方案
        self.add_heading('16.4 施工组织方案', level=2)
        self.add_paragraph()
        self.add_paragraph("（此处插入施工组织方案材料）", bold=False)
        self.add_paragraph()
        
        # 16.5 质量管理体系
        self.add_heading('16.5 质量管理体系', level=2)
        self.add_paragraph()
        self.add_paragraph("（此处插入质量管理体系材料）", bold=False)
        self.add_paragraph()
        
        # 16.6 安全文明施工
        self.add_heading('16.6 安全文明施工', level=2)
        self.add_paragraph()
        self.add_paragraph("（此处插入安全文明施工材料）", bold=False)
        self.add_paragraph()
        
        # 16.7 交货验收
        self.add_heading('16.7 交货验收', level=2)
        self.add_paragraph()
        self.add_paragraph("（此处插入交货验收材料）", bold=False)
        self.add_paragraph()
    
    def generate_attachments(self):
        """生成附件（第十七章）"""
        self.add_heading('十七、附件', level=1)
        self.add_paragraph()
        
        content = """附件清单：
1. 营业执照
2. 法定代表人身份证复印件
3. 授权委托书
4. 体系认证证书
5. 其他证书
"""
        
        self.add_paragraph(content)
        self.add_paragraph()
    
    def generate_bid_document(self, output_path='output/投标文件.docx'):
        """生成完整的投标文件"""
        print("=" * 60)
        print("生成投标文件（按照参考模板）")
        print("=" * 60)
        print()
        
        # 创建文档
        self.create_document()
        
        # 生成各章节
        print("1️⃣  生成第一章：投标函...")
        self.generate_tender_letter()
        
        print("2️⃣  生成第二章：投标一览表...")
        self.generate_tender_overview()
        
        print("3️⃣  生成第三章：法定代表人身份证明...")
        self.generate_legal_rep_info()
        
        print("4️⃣  生成第四章：法定代表人授权委托书...")
        self.generate_legal_rep_authorization()
        
        print("5️⃣  生成第五章：商务偏离表...")
        self.generate_business_deviation_table()
        
        print("6️⃣  生成第六章：报价一览表...")
        self.generate_price_summary()
        
        print("7️⃣  生成第七章：分部分项报价清单...")
        self.generate_itemized_price_list()
        
        print("8️⃣  生成第八章：备件清单...")
        self.generate_spare_parts_list()
        
        print("9️⃣  生成第九章：企业资质证明文件...")
        self.generate_company_qualifications()
        
        print("10️⃣  生成第十章：工程业绩...")
        self.generate_project_performance()
        
        print("11️⃣  生成第十一章：项目投标纲领...")
        self.generate_project_bidding_outline()
        
        print("12️⃣  生成第十二章：质量控制专项方案...")
        self.generate_quality_control_plan()
        
        print("13️⃣  生成第十三章：质量保证...")
        self.generate_quality_assurance()
        
        print("14️⃣  生成第十四章：交货期、质量保证和售后服务...")
        self.generate_delivery_quality_after_sales()
        
        print("15️⃣  生成第十五章：售后服务及质量承诺...")
        self.generate_after_sales_commitment()
        
        print("16️⃣  生成第十六章：证明设备及服务合格性的文件...")
        self.generate_equipment_service_qualification()
        
        print("17️⃣  生成第十七章：附件...")
        self.generate_attachments()
        
        # 保存文档
        print()
        print("💾 保存投标文件...")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.doc.save(output_path)
        
        print(f"✓ 投标文件已保存: {output_path.absolute()}")
        print(f"  文件大小: {output_path.stat().st_size / (1024*1024):.2f} MB")
        
        return output_path

def main():
    """主函数"""
    generator = BidDocumentGenerator()
    
    # 生成投标文件
    output_file = f"output/投标文件_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    
    generator.generate_bid_document(output_file)
    
    print()
    print("=" * 60)
    print("完成！")
    print("=" * 60)
    print(f"\n✓ 投标文件已生成")
    print(f"  文件名: {output_file}")
    print(f"\n💡 下一步操作:")
    print(f"  1. 下载并打开投标文件")
    print(f"  2. 检查文件内容和格式")
    print(f"  3. 根据需要填写报价清单和备件清单")
    print(f"  4. 根据招标文件要求修改和补充内容")

if __name__ == "__main__":
    main()
