"""
公司资料数据库管理模块
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class CompanyDatabase:
    """公司资料数据库"""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.qualification_file = data_dir / "qualifications.json"
        self.cases_file = data_dir / "cases.json"
        self.products_file = data_dir / "products.json"
        self.personnel_file = data_dir / "personnel.json"

        # 初始化数据文件
        self._init_data_files()

    def _init_data_files(self):
        """初始化数据文件"""
        if not self.qualification_file.exists():
            self._save_json(self.qualification_file, {
                "qualifications": [],
                "certificates": [],
                "honors": []
            })

        if not self.cases_file.exists():
            self._save_json(self.cases_file, {
                "cases": []
            })

        if not self.products_file.exists():
            self._save_json(self.products_file, {
                "products": [],
                "prices": {}
            })

        if not self.personnel_file.exists():
            self._save_json(self.personnel_file, {
                "management": [],
                "engineers": [],
                "workers": []
            })

    def _load_json(self, filepath: Path) -> Dict:
        """加载JSON文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return {}

    def _save_json(self, filepath: Path, data: Dict):
        """保存JSON文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ==================== 资质管理 ====================

    def get_qualifications(self) -> List[Dict]:
        """获取所有资质"""
        data = self._load_json(self.qualification_file)
        return data.get("qualifications", [])

    def add_qualification(self, name: str, level: str, cert_no: str,
                          valid_until: str, cert_file: str = ""):
        """添加资质"""
        data = self._load_json(self.qualification_file)
        data["qualifications"].append({
            "id": len(data["qualifications"]) + 1,
            "name": name,
            "level": level,
            "cert_no": cert_no,
            "valid_until": valid_until,
            "cert_file": cert_file,
            "created_at": datetime.now().isoformat()
        })
        self._save_json(self.qualification_file, data)

    def get_valid_qualifications(self) -> List[Dict]:
        """获取有效资质"""
        today = datetime.now().strftime("%Y-%m-%d")
        qualifications = self.get_qualifications()
        valid = []

        for q in qualifications:
            valid_until = q.get("valid_until", "").strip()
            # 如果有效期是空的，认为永久有效
            if not valid_until:
                valid.append(q)
            # 否则检查是否过期
            elif valid_until >= today:
                valid.append(q)

        return valid

    # ==================== 案例管理 ====================

    def get_cases(self, industry: str = None) -> List[Dict]:
        """获取案例"""
        data = self._load_json(self.cases_file)
        cases = data.get("cases", [])

        if industry:
            return [c for c in cases if industry.lower() in c.get("industry", "").lower()]
        return cases

    def add_case(self, project_name: str, client: str, industry: str,
                 product_type: str, amount: float, year: int,
                 description: str = ""):
        """添加案例"""
        data = self._load_json(self.cases_file)
        data["cases"].append({
            "id": len(data["cases"]) + 1,
            "project_name": project_name,
            "client": client,
            "industry": industry,
            "product_type": product_type,
            "amount": amount,
            "year": year,
            "description": description,
            "created_at": datetime.now().isoformat()
        })
        self._save_json(self.cases_file, data)

    # ==================== 产品管理 ====================

    def get_products(self, category: str = None) -> List[Dict]:
        """获取产品"""
        data = self._load_json(self.products_file)
        products = data.get("products", [])

        if category:
            return [p for p in products if category.lower() in p.get("category", "").lower()]
        return products

    def add_product(self, name: str, model: str, category: str,
                    description: str = "", base_price: float = 0):
        """添加产品"""
        data = self._load_json(self.products_file)
        data["products"].append({
            "id": len(data["products"]) + 1,
            "name": name,
            "model": model,
            "category": category,
            "description": description,
            "base_price": base_price,
            "created_at": datetime.now().isoformat()
        })
        self._save_json(self.products_file, data)

    def get_product_by_model(self, model: str) -> Optional[Dict]:
        """根据型号获取产品"""
        products = self.get_products()
        for p in products:
            if p["model"].lower() == model.lower():
                return p
        return None

    # ==================== 人员管理 ====================

    def get_personnel(self, role: str = None) -> List[Dict]:
        """获取人员"""
        data = self._load_json(self.personnel_file)
        all_personnel = []

        for key in ["management", "engineers", "workers"]:
            all_personnel.extend(data.get(key, []))

        if role:
            return [p for p in all_personnel if role.lower() in p.get("role", "").lower()]
        return all_personnel

    def add_personnel(self, name: str, role: str, title: str,
                      experience: int, certificates: List[str] = None):
        """添加人员"""
        data = self._load_json(self.personnel_file)

        # 根据职位分类
        if "经理" in role or "总监" in role or "总经理" in role:
            category = "management"
        elif "工程师" in role or "技术" in role:
            category = "engineers"
        else:
            category = "workers"

        data[category].append({
            "id": len(data.get(category, [])) + 1,
            "name": name,
            "role": role,
            "title": title,
            "experience": experience,
            "certificates": certificates or [],
            "created_at": datetime.now().isoformat()
        })
        self._save_json(self.personnel_file, data)

    # ==================== 智能匹配 ====================

    def match_qualifications(self, requirements: List[str]) -> List[Dict]:
        """智能匹配资质"""
        qualifications = self.get_qualifications()  # 改为获取所有资质，不再过滤
        matched = []
        matched_ids = set()

        for req in requirements:
            req_lower = req.lower()

            for q in qualifications:
                if q["id"] in matched_ids:
                    continue

                q_name_lower = q["name"].lower()
                q_level_lower = q["level"].lower()

                # 尝试多种匹配方式
                if (req_lower in q_name_lower or
                    req_lower in q_level_lower or
                    q_name_lower in req_lower or
                    q_level_lower in req_lower):

                    matched.append(q)
                    matched_ids.add(q["id"])
                    break

        # 如果匹配到的证书少于10个，返回所有有PDF的证书的前20个
        if len(matched) < 10 and qualifications:
            # 筛选出有PDF的证书
            with_pdf = [q for q in qualifications if q.get('cert_file')]
            matched = with_pdf[:20]

        return matched

    def match_cases(self, industry: str, product_type: str = None,
                    min_amount: float = 0, limit: int = 5) -> List[Dict]:
        """智能匹配案例"""
        # 获取所有案例（不再按行业过滤）
        cases = self.get_cases()

        # 如果没有product_type，返回最新的案例
        if not product_type:
            cases.sort(key=lambda x: x.get("year", 0), reverse=True)
            return cases[:limit]

        # 按产品类型智能匹配
        product_type_lower = product_type.lower()
        matched_cases = []

        for c in cases:
            c_product_type = c.get("product_type", "").lower()
            c_name = c.get("project_name", "").lower()

            # 检查产品类型是否匹配（多种方式）
            if (product_type_lower in c_product_type or
                c_product_type in product_type_lower or
                product_type_lower in c_name):

                matched_cases.append(c)

        # 如果没有匹配到，返回最新的案例
        if not matched_cases:
            cases.sort(key=lambda x: x.get("year", 0), reverse=True)
            return cases[:limit]

        # 按金额过滤
        if min_amount > 0:
            matched_cases = [c for c in matched_cases if c.get("amount", 0) >= min_amount]

        # 按年份排序（最新的优先）
        matched_cases.sort(key=lambda x: x.get("year", 0), reverse=True)

        return matched_cases[:limit]

    def match_products(self, keywords: List[str]) -> List[Dict]:
        """智能匹配产品"""
        products = self.get_products()
        matched = []

        if not keywords:
            return products[:10]  # 如果没有关键词，返回前10个产品

        for p in products:
            p_name_lower = p["name"].lower()
            p_model_lower = p["model"].lower()
            p_category_lower = p.get("category", "").lower()

            # 检查是否匹配任何一个关键词
            for kw in keywords:
                kw_lower = kw.lower()

                if (kw_lower in p_name_lower or
                    kw_lower in p_model_lower or
                    kw_lower in p_category_lower or
                    p_name_lower in kw_lower or
                    p_model_lower in kw_lower):

                    matched.append(p)
                    break

        # 如果没有匹配到，返回所有产品
        if not matched and products:
            matched = products

        return matched


# 初始化数据库（用于测试）
if __name__ == "__main__":
    data_dir = Path(__file__).parent / "data"
    db = CompanyDatabase(data_dir)

    # 添加测试数据
    print("初始化数据库...")

    # 添加资质
    db.add_qualification(
        name="电力工程施工总承包",
        level="三级",
        cert_no="D242010979",
        valid_until="2028-12-31"
    )

    db.add_qualification(
        name="承装（修、试）电力设施许可证",
        level="四级",
        cert_no="6-1-00357-2018",
        valid_until="2027-06-30"
    )

    # 添加案例
    db.add_case(
        project_name="中天钢铁集团（淮安）新材料有限公司10kV中压柜",
        client="中天钢铁集团",
        industry="钢铁",
        product_type="高压开关柜",
        amount=550000,
        year=2025,
        description="三厂10kV中压柜采购项目"
    )

    db.add_case(
        project_name="汉西污水处理厂三期工程低压开关柜",
        client="葛洲坝集团",
        industry="环保",
        product_type="低压开关柜",
        amount=2800000,
        year=2025,
        description="低压开关柜、动力配电箱等采购"
    )

    # 添加产品
    db.add_product(
        name="户内交流金属铠装移开式开关设备",
        model="KYN28A-12",
        category="高压开关柜",
        description="适用于额定电压3.6-12kV三相交流50Hz电力系统中",
        base_price=50000
    )

    db.add_product(
        name="低压抽出式开关柜",
        model="MNS",
        category="低压开关柜",
        description="适用于发电厂、变电站、石油化工等场所",
        base_price=30000
    )

    db.add_product(
        name="箱式变电站",
        model="ZGS11",
        category="预制舱",
        description="一体化预装式变电站",
        base_price=80000
    )

    # 添加人员
    db.add_personnel(
        name="张三",
        role="技术总监",
        title="高级工程师",
        experience=20,
        certificates=["注册电气工程师", "高级工程师"]
    )

    db.add_personnel(
        name="李四",
        role="项目经理",
        title="工程师",
        experience=10,
        certificates=["一级建造师", "PMP"]
    )

    print("数据库初始化完成！")
    print(f"资质: {len(db.get_qualifications())}")
    print(f"案例: {len(db.get_cases())}")
    print(f"产品: {len(db.get_products())}")
    print(f"人员: {len(db.get_personnel())}")
