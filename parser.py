"""
招标文件解析模块
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import re
from docx import Document
from pypdf import PdfReader
import jieba
import subprocess
import tempfile
import os

try:
    from docx2python import convert
    DOCX2PYTHON_AVAILABLE = True
except ImportError:
    DOCX2PYTHON_AVAILABLE = False
    print("警告: docx2python 未安装，无法自动转换 .doc 到 .docx")
    print("安装命令: pip install docx2python")


class TenderParser:
    """招标文件解析器"""

    def __init__(self):
        # 关键词库
        self.keywords = {
            "资质要求": [
                "资质", "资格", "许可证", "证书", "认证", "等级",
                "营业执照", "安全生产许可证", "承装修试",
            ],
            "产品类型": [
                "开关柜", "配电柜", "变压器", "箱变", "预制舱",
                "高压柜", "低压柜", "配电箱", "母线桥", "10kV", "35kV",
                "中压", "低压", "高压",
            ],
            "技术要求": [
                "技术", "规范", "标准", "参数", "性能",
                "防护等级", "绝缘等级", "额定电流", "额定电压",
            ],
            "商务要求": [
                "报价", "交货期", "付款", "质保", "售后",
                "验收", "培训", "服务", "合同",
            ],
            "时间要求": [
                "交货期", "工期", "交付时间", "完成时间",
                "天", "个月", "日", "年",
            ],
        }

    def parse_file(self, filepath: Path) -> Dict[str, Any]:
        """
        解析招标文件

        Args:
            filepath: 文件路径

        Returns:
            解析结果字典
        """
        if not filepath.exists():
            raise FileNotFoundError(f"文件不存在: {filepath}")

        suffix = filepath.suffix.lower()

        if suffix == ".pdf":
            return self._parse_pdf(filepath)
        elif suffix == ".docx":
            return self._parse_docx(filepath)
        elif suffix == ".doc":
            # 先将 .doc 转换为 .docx，然后解析
            if DOCX2PYTHON_AVAILABLE:
                docx_path = self._convert_doc_to_docx(filepath)
                return self._parse_docx(docx_path)
            else:
                # 如果没有 docx2python，使用原来的方法
                return self._parse_doc(filepath)
        else:
            raise ValueError(f"不支持的文件格式: {suffix}")

    def parse_multiple_files(self, filepaths: List[str]) -> Dict[str, Any]:
        """
        解析多个招标文件并合并结果

        Args:
            filepaths: 文件路径列表

        Returns:
            合并后的解析结果字典
        """
        if not filepaths:
            raise ValueError("文件路径列表不能为空")

        # 解析第一个文件作为基础
        base_result = self.parse_file(Path(filepaths[0]))

        # 合并其他文件的结果
        for filepath in filepaths[1:]:
            result = self.parse_file(Path(filepath))
            base_result = self._merge_results(base_result, result)

        # 检查是否需要分开技术标和商务标
        base_result["require_separate_bids"] = self._check_separate_bids(base_result)

        return base_result

    def _merge_results(self, base: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并两个解析结果

        Args:
            base: 基础结果
            new: 新结果

        Returns:
            合并后的结果
        """
        # 合并项目信息（以非空值为准）
        for key in ["project_name", "project_no", "tenderer", "address", "delivery_period"]:
            if key in new.get("project_info", {}) and new["project_info"][key]:
                base["project_info"][key] = new["project_info"][key]

        # 合并列表类型的要求（去重）
        for key in ["qualification_requirements", "product_requirements",
                     "technical_requirements", "commercial_requirements"]:
            if key in new:
                base[key] = list(set(base[key] + new[key]))

        # 合并交货期要求
        if "delivery_requirements" in new and new["delivery_requirements"].get("delivery_days"):
            base["delivery_requirements"]["delivery_days"] = new["delivery_requirements"]["delivery_days"]

        # 合并原始文本
        base["raw_text"] += "\n\n" + new.get("raw_text", "")

        return base

    def _check_separate_bids(self, result: Dict[str, Any]) -> bool:
        """
        检查是否需要分开技术标和商务标

        Args:
            result: 解析结果

        Returns:
            True如果需要分开，否则False
        """
        text = result.get("raw_text", "")

        # 检查关键词
        keywords = [
            "技术标",
            "商务标",
            "分开",
            "分别",
            "技术部分",
            "商务部分",
            "技术文件",
            "商务文件",
        ]

        for kw in keywords:
            if kw in text:
                return True

        return False

    def _parse_pdf(self, filepath: Path) -> Dict[str, Any]:
        """解析PDF文件"""
        reader = PdfReader(filepath)
        text = ""

        # 提取所有文本
        for page in reader.pages:
            text += page.extract_text() + "\n"

        return self._extract_info(text)

    def _parse_docx(self, filepath: Path) -> Dict[str, Any]:
        """解析Word文件（.docx格式）"""
        doc = Document(filepath)
        text = ""

        # 提取所有段落文本
        for para in doc.paragraphs:
            text += para.text + "\n"

        return self._extract_info(text)

    def _convert_doc_to_docx(self, filepath: Path) -> Path:
        """
        将 .doc 文件转换为 .docx 格式

        Args:
            filepath: .doc 文件路径

        Returns:
            转换后的 .docx 文件路径
        """
        try:
            print(f"  正在将 {filepath.name} 转换为 .docx 格式...")

            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                # 转换文件
                convert(filepath, temp_dir)

                # 转换后的文件名
                output_filename = filepath.stem + '.docx'
                output_path = Path(temp_dir) / output_filename

                # 移动到原来的目录
                final_path = filepath.parent / output_filename
                import shutil
                shutil.move(str(output_path), str(final_path))

                print(f"  ✓ 转换成功: {output_filename}")
                return final_path
        except Exception as e:
            print(f"  ✗ 转换失败: {e}")
            import traceback
            traceback.print_exc()
            # 转换失败，返回原文件路径
            return filepath

    def _parse_doc(self, filepath: Path) -> Dict[str, Any]:
        """
        解析旧版Word文件（.doc格式）

        使用textool或命令行工具提取文本
        """
        text = ""

        # 方法1: 尝试使用textool库
        try:
            import textract
            text = textract.process(str(filepath)).decode('utf-8')
            if text.strip():
                return self._extract_info(text)
        except ImportError:
            pass
        except Exception as e:
            print(f"textool解析失败: {e}")

        # 方法2: 尝试使用antiword命令（Linux/Mac）
        if not text.strip():
            try:
                result = subprocess.run(['antiword', '-t', str(filepath)],
                                       capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    text = result.stdout
                    return self._extract_info(text)
            except FileNotFoundError:
                pass
            except Exception as e:
                print(f"antiword解析失败: {e}")

        # 方法3: 尝试使用catdoc命令（Linux/Mac）
        if not text.strip():
            try:
                result = subprocess.run(['catdoc', str(filepath)],
                                       capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    text = result.stdout
                    return self._extract_info(text)
            except FileNotFoundError:
                pass
            except Exception as e:
                print(f"catdoc解析失败: {e}")

        # 方法4: 尝试使用LibreOffice转换为文本
        if not text.strip():
            try:
                with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
                    tmp_path = tmp.name

                # 使用LibreOffice转换为文本
                result = subprocess.run([
                    'libreoffice', '--headless', '--convert-to', 'txt',
                    '--outdir', os.path.dirname(tmp_path),
                    str(filepath)
                ], capture_output=True, timeout=60)

                # 读取转换后的文本文件
                converted_path = os.path.splitext(str(filepath))[0] + '.txt'
                if os.path.exists(converted_path):
                    with open(converted_path, 'r', encoding='utf-8', errors='ignore') as f:
                        text = f.read()
                    # 删除临时文件
                    try:
                        os.remove(converted_path)
                    except:
                        pass

                if text.strip():
                    return self._extract_info(text)

            except FileNotFoundError:
                pass
            except Exception as e:
                print(f"LibreOffice解析失败: {e}")

        # 如果所有方法都失败，抛出异常并提供提示
        if not text.strip():
            raise ValueError(
                "无法解析.doc文件。请尝试以下方法：\n"
                "1. 将.doc文件另存为.docx格式\n"
                "2. 安装antiword: brew install antiword\n"
                "3. 安装LibreOffice: brew install --cask libreoffice\n"
                "4. 安装textract库: pip install textract"
            )

        return self._extract_info(text)

    def _extract_info(self, text: str) -> Dict[str, Any]:
        """
        从文本中提取关键信息

        Args:
            text: 文本内容

        Returns:
            提取的信息字典
        """
        result = {
            "project_info": {},
            "qualification_requirements": [],
            "product_requirements": [],
            "technical_requirements": [],
            "commercial_requirements": [],
            "delivery_requirements": [],
            "raw_text": text,
        }

        # 1. 提取项目基本信息
        result["project_info"] = self._extract_project_info(text)

        # 2. 提取资质要求
        result["qualification_requirements"] = self._extract_requirements(
            text, "资质要求"
        )

        # 3. 提取产品要求
        result["product_requirements"] = self._extract_requirements(
            text, "产品类型"
        )

        # 4. 提取技术要求
        result["technical_requirements"] = self._extract_requirements(
            text, "技术要求"
        )

        # 5. 提取商务要求
        result["commercial_requirements"] = self._extract_requirements(
            text, "商务要求"
        )

        # 6. 提取交货期要求
        result["delivery_requirements"] = self._extract_delivery(text)

        return result

    def _extract_project_info(self, text: str) -> Dict[str, str]:
        """提取项目基本信息"""
        info = {}

        # 提取项目名称
        project_name_match = re.search(r"项目名称[：:]\s*([^\n]+)", text)
        if project_name_match:
            info["project_name"] = project_name_match.group(1).strip()

        # 提取项目编号
        project_no_match = re.search(r"项目编号[：:]\s*([^\n]+)", text)
        if project_no_match:
            info["project_no"] = project_no_match.group(1).strip()

        # 提取招标人
        tenderer_match = re.search(r"招标人[：:]\s*([^\n]+)", text)
        if tenderer_match:
            info["tenderer"] = tenderer_match.group(1).strip()

        # 提取项目地址
        address_match = re.search(r"项目地址[：:]\s*([^\n]+)", text)
        if address_match:
            info["address"] = address_match.group(1).strip()

        # 提取交货期
        delivery_match = re.search(r"交货期[：:]\s*([^\n]+)", text)
        if delivery_match:
            info["delivery_period"] = delivery_match.group(1).strip()

        # 提取投标人资格要求（整体）
        qualification_section = self._extract_section(text, "投标人资格要求")
        if qualification_section:
            info["qualification_section"] = qualification_section

        return info

    def _extract_section(self, text: str, section_title: str) -> str:
        """
        提取特定章节内容

        Args:
            text: 文本
            section_title: 章节标题

        Returns:
            章节内容
        """
        # 查找章节开始
        start_idx = text.find(section_title)
        if start_idx == -1:
            return ""

        # 查找下一个章节标题（粗略判断）
        lines = text[start_idx + len(section_title):].split("\n")
        content = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 判断是否是新的章节（简单判断：以数字开头的行）
            if re.match(r"^[一二三四五六七八九十]、", line):
                break

            content.append(line)

        return "\n".join(content)

    def _extract_requirements(self, text: str, req_type: str) -> List[str]:
        """
        提取特定类型的要求

        Args:
            text: 文本
            req_type: 要求类型

        Returns:
            要求列表
        """
        keywords = self.keywords.get(req_type, [])

        # 分词
        words = jieba.lcut(text)
        word_freq = {}

        # 统计关键词出现频率
        for word in words:
            for kw in keywords:
                if kw in word:
                    word_freq[word] = word_freq.get(word, 0) + 1

        # 返回关键词列表（去重）
        return list(set(word_freq.keys()))

    def _extract_delivery(self, text: str) -> Dict[str, Any]:
        """提取交货期相关信息"""
        result = {
            "delivery_days": None,
            "delivery_text": "",
        }

        # 查找交货期数字
        delivery_patterns = [
            r"交货期[：:]\s*(\d+)[天日]",
            r"(\d+)[天日][内内]?交货",
            r"工期[：:]\s*(\d+)[天日]",
        ]

        for pattern in delivery_patterns:
            match = re.search(pattern, text)
            if match:
                result["delivery_days"] = int(match.group(1))
                break

        # 提取交货期完整描述
        delivery_match = re.search(r"交货期[：:]\s*([^\n]+)", text)
        if delivery_match:
            result["delivery_text"] = delivery_match.group(1).strip()

        return result

    def extract_products_from_excel(self, filepath: Path) -> List[Dict[str, Any]]:
        """
        从Excel文件中提取产品清单

        Args:
            filepath: Excel文件路径

        Returns:
            产品列表
        """
        try:
            import xlrd
        except ImportError:
            raise ImportError("请安装xlrd库: pip install xlrd")

        workbook = xlrd.open_workbook(filepath)
        sheet = workbook.sheet_by_index(0)

        products = []

        # 假设第一行是表头
        headers = []
        for col in range(sheet.ncols):
            cell_value = sheet.cell_value(0, col)
            if cell_value:
                headers.append(str(cell_value).strip())

        # 解析数据行
        for row in range(1, sheet.nrows):
            product = {}

            for col, header in enumerate(headers):
                if col >= sheet.ncols:
                    break

                cell_value = sheet.cell_value(row, col)

                # 跳过空值
                if cell_value == "" or cell_value == "/":
                    continue

                # 转换类型
                if isinstance(cell_value, float) and cell_value.is_integer():
                    cell_value = int(cell_value)
                elif isinstance(cell_value, float):
                    cell_value = round(cell_value, 2)

                product[header] = cell_value

            if product:  # 只添加非空行
                products.append(product)

        return products


# 测试代码
if __name__ == "__main__":
    parser = TenderParser()

    # 测试解析Word文件
    docx_file = Path(__file__).parent.parent / "downloads" / "报价，有投标文件" / \
                "中天钢铁集团（淮安）新材料有限公司（10KV开关柜）" / \
                "（中天云链）招标文件.docx"

    if docx_file.exists():
        print("=" * 60)
        print("解析Word文件:")
        print("=" * 60)
        result = parser.parse_file(docx_file)
        print(f"项目名称: {result['project_info'].get('project_name')}")
        print(f"项目编号: {result['project_info'].get('project_no')}")
        print(f"招标人: {result['project_info'].get('tenderer')}")
        print(f"产品要求: {result['product_requirements']}")
        print(f"资质要求: {result['qualification_requirements']}")
    else:
        print(f"文件不存在: {docx_file}")
