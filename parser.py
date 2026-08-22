"""
招标文件解析模块 - 增强版
"""

import re
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import PyPDF2
import docx
import subprocess


class ParseResult:
    """解析结果类"""
    def __init__(self, requirements, confidence_score=0.0, project_name=None):
        self.requirements = requirements
        self.confidence_score = confidence_score  # 0.0-1.0
        self.project_name = project_name  # 项目名称

    def get_confidence_level(self):
        """获取置信度等级"""
        if self.confidence_score >= 0.8:
            return "高"
        elif self.confidence_score >= 0.6:
            return "中"
        elif self.confidence_score >= 0.4:
            return "低"
        else:
            return "不确定"

    def get_confidence_color(self):
        """获取置信度颜色标识"""
        if self.confidence_score >= 0.8:
            return "🟢"  # 高 - 绿色
        elif self.confidence_score >= 0.6:
            return "🟡"  # 中 - 黄色
        elif self.confidence_score >= 0.4:
            return "🟠"  # 低 - 橙色
        else:
            return "⚪"  # 不确定 - 白色


class TenderParser:
    """招标文件解析器"""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def extract_project_name(self, filepath: Path, text: str) -> str:
        """从文件名和内容中提取项目名称"""
        # 方法1：从文件名中提取
        filename = filepath.stem  # 不含扩展名的文件名

        # 清理文件名
        filename = re.sub(r'^[\d\-\_\.]+', '', filename)  # 去除前缀的数字、下划线、点
        filename = re.sub(r'(招标文件|投标文件|采购|询价|需求)$', '', filename)  # 去除后缀

        # 如果文件名看起来像项目名称（长度>=4），使用它
        if len(filename) >= 4 and not re.match(r'^\d+$', filename):
            return filename.strip()

        # 方法2：从内容中提取
        project_patterns = [
            r'项目名称[:：]\s*([^\n\r]+)',
            r'项目[:：]\s*([^\n\r]+)',
            r'工程名称[:：]\s*([^\n\r]+)',
            r'采购项目[:：]\s*([^\n\r]+)',
            r'标的名称[:：]\s*([^\n\r]+)',
        ]

        for pattern in project_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                project_name = match.group(1).strip()
                # 去除多余的标点符号
                project_name = re.sub(r'[。、；;，,\s]+$', '', project_name)
                if len(project_name) >= 4:
                    return project_name

        # 方法3：如果文件名太短，使用通用名称
        if len(filename) < 4:
            return "未命名项目"

        return filename.strip() or "未命名项目"

    def parse_file(self, filepath: Path) -> ParseResult:
        """解析招标文件"""
        
        # 根据文件类型选择解析方法
        if not filepath.exists():
            return ParseResult([], confidence_score=0.0)

        try:
            if filepath.suffix.lower() == '.pdf':
                return self._parse_pdf(filepath)
            elif filepath.suffix.lower() == '.docx':
                return self._parse_docx(filepath)
            elif filepath.suffix.lower() == '.doc':
                return self._parse_doc(filepath)
            else:
                return ParseResult([], confidence_score=0.0)
        except Exception as e:
            print(f"✗ 文件解析失败: {e}")
            return ParseResult([], confidence_score=0.0)

    def _parse_pdf(self, filepath: Path) -> ParseResult:
        """解析PDF文件"""
        print(f"📄 开始解析PDF文件: {filepath.name}")
        
        requirements = []
        
        try:
            reader = PyPDF2.PdfReader(filepath)
            
            # 提取文本
            text = ""
            for page in reader.pages:
                text += page.extract_text()

            # 解析需求
            requirements = self._extract_requirements_from_text(text)

            # 提取项目名称
            project_name = self.extract_project_name(filepath, text)

            # 计算置信度
            confidence = self._calculate_confidence(requirements, 'pdf')
            
            print(f"✓ PDF解析完成")
            print(f"  - 项目名称: {project_name}")
            print(f"  - 提取需求: {len(requirements)}")
            print(f"  - 置信度: {confidence:.2f} ({confidence * 100:.0f}%)")

            return ParseResult(requirements, confidence_score=confidence, project_name=project_name)
            
        except Exception as e:
            print(f"✗ PDF解析失败: {e}")
            return ParseResult([], confidence_score=0.0)

    def _parse_docx(self, filepath: Path) -> ParseResult:
        """解析 DOCX 文件"""
        print(f"📄 开始解析 DOCX 文件: {filepath.name}")
        
        requirements = []
        
        try:
            doc = docx.Document(filepath)
            
            # 提取文本
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])

            # 解析需求
            requirements = self._extract_requirements_from_text(text)

            # 提取项目名称
            project_name = self.extract_project_name(filepath, text)

            # 计算置信度
            confidence = self._calculate_confidence(requirements, 'docx')
            
            print(f"✓ DOCX解析完成")
            print(f"  - 项目名称: {project_name}")
            print(f"  - 提取需求: {len(requirements)}")
            print(f"  - 置信度: {confidence:.2f} ({confidence * 100:.0f}%)")

            return ParseResult(requirements, confidence_score=confidence, project_name=project_name)
            
        except Exception as e:
            print(f"✗ DOCX解析失败: {e}")
            return ParseResult([], confidence_score=0.0)

    def _parse_doc(self, filepath: Path) -> ParseResult:
        """解析 DOC 文件（使用 antiword 转换）"""
        print(f"📄 开始解析 DOC 文件: {filepath.name}")
        
        try:
            # 检查 antiword 是否安装
            result = subprocess.run(['which', 'antiword'], 
                                 capture_output=True, text=True)
            antiword_path = result.stdout.strip()
            
            if not antiword_path:
                print("⚠️  antiword 未安装，尝试使用其他方法")
                # 尝试使用 LibreOffice 转换
                libreoffice_result = subprocess.run(['which', 'libreoffice', 'soffice'], 
                                                 capture_output=True, text=True)
                libreoffice_path = libreoffice_result.stdout.strip() or libreoffice_result.stderr.strip()
                
                if libreoffice_path:
                    print(f"✓ 找到 LibreOffice: {libreoffice_path}")
                    # 使用 LibreOffice 转换 DOC 为 DOCX
                    temp_dir = Path("temp")
                    temp_dir.mkdir(exist_ok=True)
                    
                    convert_result = subprocess.run(
                        [libreoffice_path, '--headless', '--convert-to', 'docx', 
                         '--outdir', str(temp_dir), str(filepath)],
                        capture_output=True, text=True, timeout=60
                    )
                    
                    if convert_result.returncode == 0:
                        # 查找转换后的文件
                        temp_docx = temp_dir / filepath.with_suffix('.docx').name
                        if temp_docx.exists():
                            print(f"✓ LibreOffice 转换成功")
                            doc = docx.Document(str(temp_docx))
                            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                            requirements = self._extract_requirements_from_text(text)
                            project_name = self.extract_project_name(filepath, text)
                            confidence = self._calculate_confidence(requirements, 'doc')

                            # 删除临时文件
                            temp_docx.unlink()

                            print(f"✓ DOC解析完成")
                            print(f"  - 项目名称: {project_name}")
                            print(f"  - 提取需求: {len(requirements)}")
                            print(f"  - 置信度: {confidence:.2f} ({confidence * 100:.0f}%)")

                            return ParseResult(requirements, confidence_score=confidence, project_name=project_name)
                        else:
                            print("⚠️  转换后的文件未找到")
                    else:
                        print(f"⚠️  LibreOffice 转换失败: {convert_result.stderr}")
                
                # LibreOffice 失败，返回低置信度
                print("⚠️  无法解析 DOC 文件")
                return ParseResult([], confidence_score=0.0)
            else:
                # 使用 antiword 直接提取文本
                result = subprocess.run([antiword_path, '-t', str(filepath)],
                                     capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    print(f"⚠️  antiword 提取失败: {result.stderr}")
                    return ParseResult([], confidence_score=0.0)
                
                text = result.stdout
                requirements = self._extract_requirements_from_text(text)
                project_name = self.extract_project_name(filepath, text)
                confidence = self._calculate_confidence(requirements, 'doc')

                print(f"✓ DOC解析完成")
                print(f"  - 项目名称: {project_name}")
                print(f"  - 提取需求: {len(requirements)}")
                print(f"  - 置信度: {confidence:.2f} ({confidence * 100:.0f}%)")

                return ParseResult(requirements, confidence_score=confidence, project_name=project_name)
            
        except Exception as e:
            print(f"✗ DOC解析失败: {e}")
            import traceback
            traceback.print_exc()
            return ParseResult([], confidence_score=0.0)

    def _extract_requirements_from_text(self, text: str) -> List[str]:
        """从文本中提取需求"""
        requirements = []
        seen = set()  # 用于去重
        
        # 定义需求关键词
        requirement_keywords = [
            "要求", "规定", "必须", "应", "需", "不得",
            "资质", "证书", "认证", "许可", "执照",
            "标准", "符合", "满足", "达到",
            "技术", "设备", "产品", "材料",
            "案例", "业绩", "经验", "年限", "年",
            "人员", "工程师", "项目经理", "技术负责人",
            "保修", "质保", "服务", "售后",
            "金额", "价格", "报价", "费用",
            "质量", "安全", "环保", "环境",
            "工期", "时间", "交付", "完工",
            "文件", "报告", "检测", "测试",
            "图纸", "设计", "方案",
            "验收", "规范", "条件",
            "证书编号", "证书等级", "有效期",
            "注册资金", "注册资本", "营业额",
            "ISO", "9001", "CCC", "CE"
        ]
        
        # 定义需要过滤的无意义内容模式
        filter_patterns = [
            r'^[一二三四五六七八九十]+[、\.]',  # 序号
            r'^\d+[、\.]',  # 数字序号
            r'^\d+\.\d+\.\d+\.\d+',  # IP地址
            r'^\d{4}-\d{2}-\d{2}',  # 日期
            r'^\d{11}$',  # 电话号码
            r'^\w+@\w+\.\w+$',  # 邮箱
            r'^http',  # URL
            r'^www',  # URL
            r'^XX',  # 公司名称开头
            r'^湖北',  # 地区名称开头
            r'^电气',  # 公司名称开头
            r'^公司',  # 公司名称
            r'^招标文件',  # 文档类型
            r'^投标文件',  # 文档类型
            r'^技术文件',  # 文档类型
        ]
        
        # 分割文本为段落
        paragraphs = text.split('\n')
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            
            # 跳过空行或太短的行
            if not paragraph or len(paragraph) < 5:
                continue
            
            # 跳过明显无意义的行
            if any(re.match(pattern, paragraph) for pattern in filter_patterns):
                continue
            
            # 提取包含关键词的句子
            sentences = re.split(r'[。！？；\n]', paragraph)
            
            for sentence in sentences:
                sentence = sentence.strip()
                
                # 跳过空行或太短的句子
                if not sentence or len(sentence) < 5:
                    continue
                
                # 去除多余空白
                sentence = ' '.join(sentence.split())
                
                # 检查是否包含需求关键词
                has_requirement = any(keyword in sentence for keyword in requirement_keywords)
                
                if has_requirement:
                    # 去重：只保留第一次出现的
                    sentence_lower = sentence.lower()
                    if sentence_lower not in seen:
                        seen.add(sentence_lower)
                        requirements.append(sentence)
                        if len(requirements) >= 20:  # 最多提取20个需求
                            break
            
            # 如果已经提取了足够的需求，停止
            if len(requirements) >= 20:
                break
        
        return requirements

    def _calculate_confidence(self, requirements: List[str], file_type: str) -> float:
        """计算解析置信度"""
        if not requirements:
            return 0.0
        
        confidence = 0.0
        
        # 1. 基于需求数量的置信度（最多 30 分）
        count_score = min(len(requirements) * 1.5, 30)
        
        # 2. 基于需求质量的置信度（最多 40 分）
        quality_score = 0.0
        for req in requirements[:10]:  # 只检查前10个
            req_lower = req.lower()
            
            # 需求长度
            if len(req) > 10:
                quality_score += 3
            elif len(req) > 20:
                quality_score += 4
            
            # 需求具体性
            concrete_keywords = ["资质", "证书", "经验", "年限", "年", "级", "ISO", "9001", "CCC", "CE"]
            if any(keyword in req_lower for keyword in concrete_keywords):
                quality_score += 2
            
            # 需求明确性
            vague_keywords = ["等", "相关", "类似", "最好", "应", "需"]
            if not any(keyword in req_lower for keyword in vague_keywords):
                quality_score += 2
        
        # 归一化
        quality_score = min(quality_score, 40) / len(requirements[:10]) * 10 if requirements else 0
        
        # 3. 基于文件类型的置信度（最多 30 分）
        type_score = {
            'pdf': 30,      # PDF 解析通常最可靠
            'docx': 25,     # DOCX 解析较可靠
            'doc': 15       # DOC 需要转换，置信度较低
        }.get(file_type, 10)
        
        # 总置信度
        confidence = (count_score + quality_score + type_score) / 100
        
        # 确保置信度在 0.0-1.0 之间
        return max(0.0, min(confidence, 1.0))
    
    def _get_suggestions(self, parse_result: ParseResult) -> List[str]:
        """生成改进建议"""
        suggestions = []
        level = parse_result.get_confidence_level()
        
        if level == "低" or level == "不确定":
            suggestions.append("文件可能不是标准招标文件格式，请检查文件内容")
            suggestions.append("建议将文件转换为 PDF 或 DOCX 格式后重新上传")
            suggestions.append("可以尝试手动输入需求")
        
        if len(parse_result.requirements) < 5:
            suggestions.append("提取的需求较少，可能遗漏了部分内容")
            suggestions.append("建议人工补充重要的需求")
        
        # 检查需求质量
        vague_count = 0
        for req in parse_result.requirements[:10]:
            if any(kw in req.lower() for kw in ["等", "相关", "类似", "最好"]):
                vague_count += 1
        
        if vague_count > 2:
            suggestions.append("部分需求表达不够具体，建议明确化")
        
        return suggestions


# 测试代码
if __name__ == "__main__":
    import sys
    import time
    
    # 测试解析
    test_dir = Path(__file__).parent / "tests"
    test_dir.mkdir(exist_ok=True)
    
    # 创建测试文件
    print("创建测试文件...")
    test_pdf = test_dir / "test_tender.pdf"
    test_docx = test_dir / "test_tender.docx"
    test_doc = test_dir / "test_tender.doc"
    
    # 创建简单的测试文件（如果不存在）
    if not test_docx.exists():
        try:
            from docx import Document
            doc = Document()
            doc.add_heading("测试招标文件", level=1)
            doc.add_paragraph("项目名称：某工业园区10kV开关柜采购")
            doc.add_paragraph("客户：某工业园区")
            doc.add_paragraph("截止日期：2026-03-15")
            doc.add_paragraph("")
            doc.add_heading("技术要求", level=2)
            doc.add_paragraph("1. 产品要求")
            doc.add_paragraph("   - KYN28A-12 户内交流金属铠装移开式开关设备", style="List Bullet")
            doc.add_paragraph("   - 额定电压：10kV", style="List Bullet")
            doc.add_paragraph("   - 额定电流：630A", style="List Bullet")
            doc.add_paragraph("   - 防护等级：IP30", style="List Bullet")
            doc.add_paragraph("")
            doc.add_paragraph("2. 资质要求")
            doc.add_paragraph("   - 电力工程施工总承包三级及以上", style="List Bullet")
            doc.add_paragraph("   - 质量管理体系认证", style="List Bullet")
            doc.add_paragraph("   - 环境管理体系认证", style="List Bullet")
            doc.add_paragraph("")
            doc.add_paragraph("3. 业绩要求")
            doc.add_paragraph("   - 提供类似项目案例3个", style="List Bullet")
            doc.add_paragraph("   - 项目金额在50万元以上", style="List Bullet")
            doc.add_paragraph("   - 项目经验5年以上", style="List Bullet")
            doc.add_paragraph("")
            doc.add_heading("商务要求", level=2)
            doc.add_paragraph("1. 报价要求")
            doc.add_paragraph("   - 固定总价", style="List Bullet")
            doc.add_paragraph("   - 报价有效期30天", style="List Bullet")
            doc.add_paragraph("")
            doc.add_paragraph("2. 付款要求")
            doc.add_paragraph("   - 验收后90天付款", style="List Bullet")
            
            doc.save(str(test_docx))
            print(f"✓ 创建测试 DOCX 文件: {test_docx}")
        except Exception as e:
            print(f"✗ 创建测试文件失败: {e}")
    
    # 测试解析
    parser = TenderParser(Path(__file__).parent / "data")
    
    print("\n" + "=" * 60)
    print("开始测试解析器")
    print("=" * 60 + "\n")
    
    if test_docx.exists():
        print("\n测试 1：解析 DOCX 文件")
        result = parser.parse_file(test_docx)
        print(f"置信度：{result.confidence_score:.2f}")
        print(f"等级：{result.get_confidence_level()}")
    
    time.sleep(1)
    
    print("\n✓ 所有测试完成")
