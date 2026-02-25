"""
招标文件智能评价模块
"""

from typing import Dict, List, Tuple
from datetime import datetime
from pathlib import Path
import json


class TenderEvaluator:
    """招标文件评价器"""

    def __init__(self, company_capabilities: Dict):
        """
        初始化评价器

        Args:
            company_capabilities: 公司能力数据
                - products: 产品列表
                - certifications: 资质列表
                - cases: 案例列表
                - industries: 行业列表
        """
        self.capabilities = company_capabilities
        self.evaluation_results = {}

    def evaluate_tender_file(self, tender_info: Dict) -> Dict:
        """
        评价招标文件

        Args:
            tender_info: 招标文件解析结果

        Returns:
            评价结果
        """
        # 1. 检查基本信息的完整性
        completeness_score = self._check_completeness(tender_info)

        # 2. 检查是否匹配公司能力
        capability_score = self._check_capability_match(tender_info)

        # 3. 检查需求的明确性
        clarity_score = self._check_requirement_clarity(tender_info)

        # 4. 综合评分
        total_score = (
            completeness_score * 0.25 +  # 完整性权重 25%
            capability_score * 0.40 +    # 能力匹配权重 40%
            clarity_score * 0.35         # 需求明确性权重 35%
        )

        # 5. 生成建议
        suggestions = self._generate_suggestions(
            completeness_score,
            capability_score,
            clarity_score,
            tender_info
        )

        # 6. 综合评价结果
        self.evaluation_results = {
            "timestamp": datetime.now().isoformat(),
            "total_score": round(total_score, 2),
            "completeness_score": round(completeness_score, 2),
            "capability_score": round(capability_score, 2),
            "clarity_score": round(clarity_score, 2),
            "is_suitable": total_score >= 60,  # 60分以上认为合适
            "suggestions": suggestions,
            "risks": self._identify_risks(tender_info)
        }

        return self.evaluation_results

    def _check_completeness(self, tender_info: Dict) -> float:
        """
        检查基本信息的完整性
        """
        score = 0.0

        # 检查项目基本信息
        if tender_info.get("project_name"):
            score += 10
        if tender_info.get("client"):
            score += 10
        if tender_info.get("bid_deadline"):
            score += 10
        if tender_info.get("project_amount"):
            score += 10

        # 检查技术要求
        requirements = tender_info.get("requirements", [])
        if requirements:
            score += 20
        else:
            score -= 10  # 没有技术要求扣分

        # 检查商务要求
        if tender_info.get("quote_format"):
            score += 10
        if tender_info.get("payment_terms"):
            score += 10

        return min(score, 100)

    def _check_capability_match(self, tender_info: Dict) -> float:
        """
        检查是否匹配公司能力
        """
        score = 0.0
        matched_products = []
        matched_certs = []
        matched_cases = []

        # 1. 检查产品匹配
        requirements = tender_info.get("requirements", [])
        product_keywords = self._extract_product_keywords(requirements)

        company_products = self.capabilities.get("products", [])
        for product in company_products:
            for keyword in product_keywords:
                if keyword.lower() in product.get("name", "").lower() or \
                   keyword.lower() in product.get("category", "").lower() or \
                   keyword.lower() in product.get("model", "").lower():
                    matched_products.append(product)
                    break

        if matched_products:
            score += 40
        else:
            score -= 10  # 没有匹配的产品扣分

        # 2. 检查资质匹配
        company_certs = self.capabilities.get("certifications", [])
        for cert in company_certs:
            cert_name = cert.get("name", "").lower()
            cert_level = cert.get("level", "").lower()

            for req in requirements:
                req_lower = req.lower()
                if req_lower in cert_name or cert_level in req_lower:
                    matched_certs.append(cert)
                    break

        if matched_certs:
            score += 30
        else:
            score -= 10  # 没有匹配的资质扣分

        # 3. 检查案例匹配
        company_cases = self.capabilities.get("cases", [])
        company_industries = self.capabilities.get("industries", [])

        if company_cases:
            score += 30  # 有案例得分

        # 4. 检查行业匹配
        for industry in company_industries:
            industry_lower = industry.lower()
            for req in requirements:
                if industry_lower in req.lower():
                    score += 10
                    break

        return min(score, 100)

    def _check_requirement_clarity(self, tender_info: Dict) -> float:
        """
        检查需求的明确性
        """
        score = 0.0
        requirements = tender_info.get("requirements", [])

        if not requirements:
            return 0.0  # 没有需求，得分0

        # 检查需求的数量和质量
        for req in requirements[:10]:  # 只检查前10个需求
            req_lower = req.lower()

            # 需求长度
            if len(req) > 5:
                score += 5

            # 需求具体性（包含关键词）
            concrete_keywords = ["资质", "证书", "产品", "案例", "经验", "职称", "年限", "金额", "等级", "认证"]
            if any(keyword in req_lower for keyword in concrete_keywords):
                score += 5

            # 需求明确性（不模糊）
            vague_keywords = ["等", "相关", "类似", "最好", "需要"]
            if not any(keyword in req_lower for keyword in vague_keywords):
                score += 3

            # 需求可衡量性
            measurable_keywords = ["级", "年", "个", "万元", "万元", "万吨", "km", "MPa", "kV"]
            if any(keyword in req for keyword in measurable_keywords):
                score += 2

        # 归一化得分
        return min(score * 100 / len(requirements[:10]) if requirements else 0, 100)

    def _extract_product_keywords(self, requirements: List[str]) -> List[str]:
        """
        从需求中提取产品关键词
        """
        keywords = []

        # 常见产品类型关键词
        product_types = [
            "开关柜", "高压开关柜", "低压开关柜", "中压开关柜",
            "箱变", "箱式变电站", "预制舱", "组合电器",
            "变压器", "互感器", "电容器", "电抗器",
            "断路器", "负荷开关", "接地开关", "电缆",
            "母线", "桥架", "避雷器", "绝缘子",
            "配电柜", "动力配电箱", "照明配电箱",
            "电表", "计量箱", "集中器", "采集器"
            "保护装置", "继电保护", "测控装置",
            "直流", "交流", "变频器", "软启动"
        ]

        # 从需求中提取关键词
        for req in requirements:
            req_lower = req.lower()
            for product_type in product_types:
                if product_type in req_lower:
                    keywords.append(product_type)

        return keywords

    def _generate_suggestions(self, completeness_score: float,
                         capability_score: float,
                         clarity_score: float,
                         tender_info: Dict) -> List[str]:
        """
        生成改进建议
        """
        suggestions = []

        # 1. 完整性建议
        if completeness_score < 60:
            suggestions.append("❓ 招标文件基本信息不完整，建议补充")
            suggestions.append("   - 缺少项目名称、客户、截止日期等信息")
        elif completeness_score < 80:
            suggestions.append("✅ 招标文件基本信息较完整")

        # 2. 能力匹配建议
        if capability_score < 40:
            suggestions.append("⚠️ 公司产品/资质/案例与招标需求匹配度较低")
            suggestions.append("   - 建议更新公司数据库，添加相关产品")
            suggestions.append("   - 建议补充相关资质证书")
            suggestions.append("   - 建议添加相关行业案例")
        elif capability_score < 70:
            suggestions.append("✅ 公司能力基本匹配")

        # 3. 需求明确性建议
        if clarity_score < 50:
            suggestions.append("⚠️ 招标需求不够明确，存在模糊表述")
            suggestions.append("   - 建议人工确认需求细节")
            suggestions.append("   - 建议与招标方沟通明确需求")
        elif clarity_score < 70:
            suggestions.append("✅ 招标需求较为明确")

        # 4. 风险提示
        if capability_score < 40:
            suggestions.append("⚠️ 风险提示：建议谨慎考虑是否参与投标")
            suggestions.append("   - 中标可能性较低")
            suggestions.append("   - 可能需要投入额外资源满足需求")
        elif capability_score < 60:
            suggestions.append("⚠️ 建议仔细评估后决定是否参与")

        return suggestions

    def _identify_risks(self, tender_info: Dict) -> List[str]:
        """
        识别潜在风险
        """
        risks = []

        # 1. 时间风险
        deadline = tender_info.get("bid_deadline")
        if deadline:
            try:
                deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
                days_left = (deadline_date - datetime.now()).days
                if days_left < 7:
                    risks.append(f"⚠️ 时间风险：距离截止日期只有 {days_left} 天")
                elif days_left < 14:
                    risks.append(f"⚠️ 时间紧张：距离截止日期只有 {days_left} 天")
            except:
                pass

        # 2. 资源风险
        amount = tender_info.get("project_amount")
        if amount and amount > 10000000:  # 1000万以上
            risks.append("⚠️ 资源风险：项目金额较大，需要评估资源")

        # 3. 能力风险
        requirements = tender_info.get("requirements", [])
        if not requirements:
            risks.append("⚠️ 需求风险：没有明确的技术要求")

        return risks

    def get_summary(self) -> Dict:
        """获取评价摘要"""
        if not self.evaluation_results:
            return {"message": "尚未评价任何招标文件"}

        total_score = self.evaluation_results["total_score"]
        is_suitable = self.evaluation_results["is_suitable"]

        # 生成总体评价
        if is_suitable:
            if total_score >= 80:
                summary = "✅ 非常适合：建议积极参与"
            elif total_score >= 70:
                summary = "✅ 适合：建议正常准备"
            else:
                summary = "✅ 基本适合：需要仔细评估"
        else:
            summary = "⚠️ 不太适合：建议谨慎考虑"

        return {
            "message": summary,
            "total_score": total_score,
            "is_suitable": is_suitable,
            "suggestions_count": len(self.evaluation_results["suggestions"]),
            "risks_count": len(self.evaluation_results["risks"])
        }


# 测试代码
if __name__ == "__main__":
    # 示例公司能力
    company_capabilities = {
        "products": [
            {"name": "户内交流金属铠装移开式开关设备", "category": "高压开关柜", "model": "KYN28A-12"},
            {"name": "低压抽出式开关柜", "category": "低压开关柜", "model": "MNS"},
            {"name": "箱式变电站", "category": "预制舱", "model": "ZGS11"},
            {"name": "三相多表位金属低压计量箱", "category": "配电柜", "model": "BXS2"}
        ],
        "certifications": [
            {"name": "电力工程施工总承包", "level": "三级"},
            {"name": "承装（修、试）电力设施许可证", "level": "四级"},
            {"name": "质量管理体系认证", "level": "一级"},
            {"name": "环境管理体系认证", "level": "一级"}
        ],
        "cases": [
            {"project_name": "中天钢铁集团10kV中压柜", "client": "中天钢铁集团", "industry": "钢铁", "amount": 550000, "year": 2025},
            {"project_name": "汉西污水处理厂三期工程", "client": "葛洲坝集团", "industry": "环保", "amount": 2800000, "year": 2025},
            {"project_name": "某医院10kV配电柜", "client": "某医院", "industry": "医疗", "amount": 1200000, "year": 2024}
        ],
        "industries": ["电力", "钢铁", "环保", "医疗", "化工", "基础设施"]
    }

    # 创建评价器
    evaluator = TenderEvaluator(company_capabilities)

    # 示例招标文件
    tender_example = {
        "project_name": "某工业园区10kV开关柜采购",
        "client": "某工业园区",
        "bid_deadline": "2026-03-15",
        "project_amount": 500000,
        "requirements": [
            "KYN28A-12 户内交流金属铠装移开式开关设备",
            "三级及以上电力工程施工总承包资质",
            "质量管理体系认证",
            "类似项目案例3个",
            "项目经理持一级建造师证书",
            "项目经验5年以上"
        ],
        "quote_format": "固定总价",
        "payment_terms": "验收后90天付款"
    }

    # 评价
    result = evaluator.evaluate_tender_file(tender_example)

    # 输出结果
    print("=" * 60)
    print("📊 招标文件智能评价")
    print("=" * 60)
    print()
    print(f"📋 项目：{tender_example['project_name']}")
    print(f"🏢 客户：{tender_example['client']}")
    print()
    print(f"总体评分：{result['total_score']}/100")
    print(f"合适程度：{'✅ 非常适合' if result['total_score'] >= 80 else '✅ 适合' if result['total_score'] >= 60 else '⚠️ 不太适合'}")
    print()
    print(f"详细评分：")
    print(f"  - 完整性（25%）：{result['completeness_score']}/100")
    print(f"  - 能力匹配（40%）：{result['capability_score']}/100")
    print(f"  - 需求明确性（35%）：{result['clarity_score']}/100")
    print()
    print("💡 改进建议（{}）".format(len(result["suggestions"])))
    for i, suggestion in enumerate(result["suggestions"][:5], 1):
        print(f"  {i}. {suggestion}")
    print()
    print("⚠️ 风险提示（{}）".format(len(result["risks"])))
    for i, risk in enumerate(result["risks"][:3], 1):
        print(f"  {i}. {risk}")
    print()
    summary = evaluator.get_summary()
    print(f"📝 总体评价：{summary['message']}")
    print("=" * 60)
