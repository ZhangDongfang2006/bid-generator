"""
公司资料数据库管理模块

数据保护机制：
- 默认使用示例数据（用于开源演示）
- 只有在设置环境变量后才加载真实数据
- 真实数据目录已被 .gitignore 忽略
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class CompanyDatabase:
    """公司资料数据库"""

    def __init__(self, data_dir: Path):
        # 检查真实数据目录是否存在
        real_data_exists = data_dir.exists() and any(
            (data_dir / f).exists()
            for f in ["qualifications.json", "cases.json", "products.json", "personnel.json"]
        )

        # 如果真实数据存在，使用真实数据；否则使用示例数据
        self.use_demo_data = not real_data_exists
        self.data_dir = data_dir
        self.examples_dir = data_dir.parent / "data" / "examples"

        # 根据模式选择数据目录
        if self.use_demo_data:
            self.base_dir = self.examples_dir
            print("=" * 60)
            print("📊 数据模式：示例数据（DEMO）")
            print("=" * 60)
            print("✓ 当前使用示例数据进行演示")
            print("✓ 未检测到本地数据文件")
            print("")
            print("💡 如需使用真实数据，请将数据文件放到以下目录：")
            print(f"   {self.data_dir}")
            print("   需要的文件：")
            print("   - qualifications.json")
            print("   - cases.json")
            print("   - products.json")
            print("   - personnel.json")
            print("=" * 60)
        else:
            self.base_dir = data_dir
            print("=" * 60)
            print("📊 数据模式：真实数据（PRODUCTION）")
            print("=" * 60)
            print("✓ 检测到本地数据文件")
            print("✓ 正在加载真实公司数据")
            print(f"✓ 数据目录：{self.base_dir}")
            print("=" * 60)

        # 设置数据文件路径
        self.qualification_file = self.base_dir / "qualifications.json"
        self.cases_file = self.base_dir / "cases.json"
        self.products_file = self.base_dir / "products.json"
        self.personnel_file = self.base_dir / "personnel.json"

        # 初始化数据文件
        self._init_data_files()

    def _init_data_files(self):
        """初始化数据文件"""
        # 确保数据目录存在
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # 初始化文件
        for filepath, default_data in [
            (self.qualification_file, {"qualifications": []}),
            (self.cases_file, {"cases": []}),
            (self.products_file, {"products": []}),
            (self.personnel_file, {
                "management": [],
                "engineers": [],
                "workers": []
            })
        ]:
            if not filepath.exists():
                self._save_json(filepath, default_data)
                print(f"✓ 创建数据文件: {filepath.name}")

    def _load_json(self, filepath: Path) -> Dict:
        """加载JSON文件"""
        if not filepath.exists():
            print(f"⚠️ 数据文件不存在: {filepath}")
            return {}

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"✗ 加载数据文件失败 {filepath}: {e}")
            return {}

    def _save_json(self, filepath: Path, data: Dict):
        """保存JSON文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ==================== 资质管理 ====================

    def get_qualifications(self) -> List[Dict]:
        """获取所有资质"""
        return self._load_json(self.qualification_file).get("qualifications", [])

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
            if not valid_until:
                valid.append(q)
            elif valid_until >= today:
                valid.append(q)

        return valid

    # ==================== 案例管理 ====================

    def get_cases(self, industry: str = None) -> List[Dict]:
        """获取案例"""
        return self._load_json(self.cases_file).get("cases", [])

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
        return self._load_json(self.products_file).get("products", [])

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
        qualifications = self.get_qualifications()

        matched = []
        matched_ids = set()

        for req in requirements:
            req_lower = req.lower()

            for q in qualifications:
                if q["id"] in matched_ids:
                    continue

                q_name_lower = q["name"].lower()
                q_level_lower = q["level"].lower()

                if (req_lower in q_name_lower or
                    req_lower in q_level_lower or
                    q_name_lower in req_lower or
                    q_level_lower in req_lower):

                    matched.append(q)
                    matched_ids.add(q["id"])
                    break

        # 如果匹配到的证书少于10个，返回所有有PDF的证书的前20个
        if len(matched) < 10 and qualifications:
            with_pdf = [q for q in qualifications if q.get('cert_file')]
            matched = with_pdf[:20]

        return matched

    def match_cases(self, industry: str = None, product_type: str = None,
                    min_amount: float = 0, limit: int = 5) -> List[Dict]:
        """智能匹配案例"""
        cases = self.get_cases()

        if not product_type:
            cases.sort(key=lambda x: x.get("year", 0), reverse=True)
            return cases[:limit]

        product_type_lower = product_type.lower()
        matched_cases = []

        for c in cases:
            c_product_type = c.get("product_type", "").lower()
            c_name = c.get("project_name", "").lower()

            if (product_type_lower in c_product_type or
                    product_type_lower in product_type_lower or
                    product_type_lower in c_name or
                    product_type_lower in c_name):

                matched_cases.append(c)

        if not matched_cases:
            cases.sort(key=lambda x: x.get("year", 0), reverse=True)
            return cases[:limit]

        if min_amount > 0:
            matched_cases = [c for c in matched_cases if c.get("amount", 0) >= min_amount]

        matched_cases.sort(key=lambda x: x.get("year", 0), reverse=True)

        return matched_cases[:limit]

    def match_products(self, keywords: List[str]) -> List[Dict]:
        """智能匹配产品"""
        products = self.get_products()
        matched = []

        if not keywords:
            return products[:10]

        for p in products:
            p_name_lower = p["name"].lower()
            p_model_lower = p["model"].lower()
            p_category_lower = p.get("category", "").lower()

            for kw in keywords:
                kw_lower = kw.lower()

                if (kw_lower in p_name_lower or
                    kw_lower in p_model_lower or
                    kw_lower in p_category_lower or
                    p_name_lower in kw_lower or
                    p_model_lower in kw_lower):

                    matched.append(p)
                    break

        if not matched and products:
            matched = products

        return matched


# ==================== 数据模式检查 ====================

def check_data_mode(data_dir: Path = None) -> str:
    """检查当前数据模式"""
    if data_dir is None:
        data_dir = Path(__file__).parent.parent / "data"

    real_data_exists = data_dir.exists() and any(
        (data_dir / f).exists()
        for f in ["qualifications.json", "cases.json", "products.json", "personnel.json"]
    )

    if real_data_exists:
        return "PRODUCTION（真实数据）"
    else:
        return "DEMO（示例数据）"


# ==================== 数据目录结构说明 ====================

"""
数据目录结构：

/Users/zhangdongfang/workspace/bid-generator/
├── data/                          # 真实数据（已被 .gitignore 忽略）
│   ├── qualifications.json
│   ├── cases.json
│   ├── products.json
│   └── personnel.json
└── data/examples/                # 示例数据（已提交到 Git）
    ├── qualifications.json
    ├── cases.json
    ├── products.json
    └── personnel.json

.gitignore 配置：
data/                    # 忽略真实数据目录
*.log                   # 忽略日志文件
output/                 # 忽略输出目录
uploads/                # 忽略上传目录

数据模式自动检测：
- 如果 data/ 目录存在且包含任意数据文件 → 使用真实数据
- 否则 → 使用示例数据

无需手动设置环境变量，系统会自动检测！
"""


# 初始化数据库（用于测试）
if __name__ == "__main__":
    data_dir = Path(__file__).parent.parent / "data"
    db = CompanyDatabase(data_dir)

    print("\n" + "=" * 60)
    print(f"数据模式：{check_data_mode()}")
    print("=" * 60)
    print(f"资质：{len(db.get_qualifications())}")
    print(f"案例：{len(db.get_cases())}")
    print(f"产品：{len(db.get_products())}")
    print(f"人员：{len(db.get_personnel())}")
    print("=" * 60)
