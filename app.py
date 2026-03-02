"""
投标文件生成应用 - AI置信度分析版
"""

import streamlit as st
import os
from pathlib import Path
from io import BytesIO
from datetime import datetime
import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

# 导入本地模块
from parser import TenderParser, ParseResult
from generator import BidDocumentGenerator as BidGenerator
from database import CompanyDatabase
import config


# ==================== 配置 ====================

# 页面设置
st.set_page_config(
    page_title="海越（湖北）电气 - 智能投标文件生成系统",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.stMarkdown {
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ==================== 初始化 ====================

# 初始化数据库
data_dir = Path(__file__).parent / "data"
db = CompanyDatabase(data_dir)

# 初始化解析器
parser = TenderParser(data_dir)

# 初始化生成器
templates_dir = Path(__file__).parent / "templates"
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)
generator = BidGenerator(templates_dir, output_dir)

# ==================== 会话状态 ====================

# 初始化session state
if 'tender_info' not in st.session_state:
    st.session_state.tender_info = {}

if 'matched_data' not in st.session_state:
    st.session_state.matched_data = {}

if 'parse_result' not in st.session_state:
    st.session_state.parse_result = None

if 'bid_generated' not in st.session_state:
    st.session_state.bid_generated = False

if 'active_page' not in st.session_state:
    st.session_state.active_page = 'main'
    # 初始化配置
    if 'config' not in st.session_state:
        st.session_state.config = {
            'tenderer': '上海国际招标有限公司',
            'project_no': '2401071015',
            'project_amount': '5723291',
            'project_tax_rate': '13%',
            'rep_name': '阎海',
            'rep_title': '投标中心主任'
        }

# ==================== 主界面 ====================

# 侧边栏
with st.sidebar:
    st.header("🏢 海越投标助手")
    st.divider()
    
    # 资料管理入口
    if st.button("📊 资料管理", use_container_width=True):
        st.session_state.active_page = "data_management"
    
    # 快速操作
    st.divider()
    st.markdown("### 🚀 快速操作")
    
    # 查看数据库状态
    st.markdown("#### 📊 数据库状态")
    st.markdown(f"- **资质**: {len(db.get_qualifications())} 项")
    st.markdown(f"- **案例**: {len(db.get_cases())} 项")
    st.markdown(f"- **产品**: {len(db.get_products())} 项")
    st.markdown(f"- **人员**: {len(db.get_personnel())} 项")

# 主内容区
if st.session_state.get('active_page') == 'data_management':
    st.title("📊 资料管理")
    
    st.markdown("---")
    st.markdown("请在本地文件系统中管理以下目录中的内容：")
    st.markdown(f"- `{data_dir}/qualifications.json`")
    st.markdown(f"- `{data_dir}/cases.json`")
    st.markdown(f"- `{data_dir}/products.json`")
    st.markdown(f"- `{data_dir}/personnel.json`")
    
else:
    st.title("📄 智能投标文件生成")
    st.markdown("---")
    
    # 第一步：上传招标文件
    st.header("📤 第一步：上传招标文件")
    st.markdown("支持 PDF、Word (.docx, .doc) 格式的招标文件（可上传多个文件）")
    
    # 文件上传（支持多个文件）
    uploaded_files = st.file_uploader(
        "上传招标文件",
        type=['pdf', 'docx', 'doc'],
        accept_multiple_files=True,
        help="支持上传多个招标文件，将自动合并解析结果",
        key="tender_file_uploader"
    )
    
    # 解析上传的文件
    if uploaded_files is not None and len(uploaded_files) > 0:
        st.info(f"📄 已上传 {len(uploaded_files)} 个文件")
        
        # 合并所有文件的解析结果
        all_requirements = []
        confidence_scores = []
        project_names = []  # 保存每个文件的项目名称

        for i, uploaded_file in enumerate(uploaded_files, 1):
            # 保存到临时文件
            temp_file = Path("temp") / uploaded_file.name
            temp_file.parent.mkdir(exist_ok=True)

            with open(temp_file, 'wb') as f:
                f.write(uploaded_file.getbuffer())

            # 解析文件
            parsing_status = st.empty()
            parsing_status.info(f"🔄 正在解析第 {i}/{len(uploaded_files)} 个文件: {uploaded_file.name}...")

            parse_result = parser.parse_file(temp_file)
            all_requirements.extend(parse_result.requirements)
            confidence_scores.append(parse_result.confidence_score)
            if parse_result.project_name:
                project_names.append(parse_result.project_name)

            # 清除解析状态
            parsing_status.empty()

        # 合并解析结果
        avg_confidence = sum(confidence_scores) / len(confidence_scores)

        # 确定项目名称（使用第一个文件的项目名称）
        project_name = project_names[0] if project_names else None

        st.session_state.parse_result = ParseResult(all_requirements, confidence_score=avg_confidence, project_name=project_name)
        st.session_state.confidence_scores = confidence_scores  # 保存每个文件的置信度
        st.session_state.project_name = project_name  # 保存项目名称

        # 显示解析结果
        st.markdown("---")
        st.subheader("📋 文件解析结果")

        # 显示每个文件的置信度
        st.markdown(f"### 📊 各文件解析置信度")
        for i, (file, score) in enumerate(zip(uploaded_files, confidence_scores), 1):
            # 根据置信度显示颜色
            if score >= 0.8:
                color = "🟢"
            elif score >= 0.6:
                color = "🟡"
            elif score >= 0.4:
                color = "🟠"
            else:
                color = "⚪"
            st.metric(
                f"文件 {i}: {file.name}",
                f"{score:.2f}",
                delta=f"{score:.2f}",
                help=f"解析置信度 - AI 对此文件解析的可信程度"
            )

        # 显示总置信度
        st.markdown("---")
        st.markdown(f"### {parse_result.get_confidence_color()} 总体解析置信度")
        st.metric(
            "平均置信度",
            f"{avg_confidence:.2f}",
            delta=f"{avg_confidence:.2f}",
            help=f"{parse_result.get_confidence_level()} - AI 对所有文件解析的平均可信程度"
        )

        # 显示项目名称
        if project_name:
            st.markdown("---")
            st.markdown("### 📌 项目信息")
            st.markdown(f"**项目名称**: {project_name}")

            # 项目编号
            project_no = st.text_input(
                "项目编号",
                value="2401071015",
                help="招标文件中的项目编号"
            )

            # 项目全称
            project_full_name = st.text_input(
                "项目全称",
                value=f"{st.session_state.config.get('tenderer', '上海国际招标有限公司')}{project_name}",
                help="项目的完整名称"
            )

            # 招标人
            tenderer = st.text_input(
                "招标人",
                value=st.session_state.config.get('tenderer', '上海国际招标有限公司'),
                help="招标单位名称"
            )

            # 项目金额
            project_amount = st.text_input(
                "项目金额",
                value="5723291",
                help="项目总金额（元）"
            )

            # 投标金额
            bid_amount = st.text_input(
                "投标金额",
                value="5723291",
                help="投标总金额（元）"
            )

            # 投标金额大写
            bid_amount_upper = st.text_input(
                "投标金额大写",
                value="伍佰柒拾贰万叁仟贰佰玖拾壹",
                help="投标总金额大写"
            )

            # 税率
            tax_rate = st.text_input(
                "税率",
                value="13%",
                help="增值税税率"
            )

            # 投标办理人信息
            st.markdown("---")
            st.markdown("### 👤 投标办理人信息")

            rep_name = st.text_input(
                "投标办理人姓名",
                value="阎海",
                help="投标办理人姓名"
            )

            rep_title = st.text_input(
                "投标办理人职务",
                value="投标中心主任",
                help="投标办理人职务"
            )

            # 更新项目信息
            st.session_state.tender_info['project_info'] = {
                'project_name': project_name,
                'project_no': project_no,
                'project_full_name': project_full_name,
                'tenderer': tenderer,
                'project_amount': project_amount,
                'project_tax_rate': tax_rate,
                'bid_amount': bid_amount,
                'bid_amount_upper': bid_amount_upper,
            }

        # 显示解析出的需求
        st.markdown(f"**提取需求**: {len(parse_result.requirements)}")
        
        # 提供人工校验
        st.markdown("---")
        st.subheader("🔍 人工校验")
        st.markdown("如果解析结果有误，可以在下方修改或添加需求：")
        
        # 编辑需求（使用大文本框，每个需求一行）
        requirements_text = "\n".join(parse_result.requirements)
        edited_text = st.text_area(
            "需求列表（每行一个需求）",
            value=requirements_text,
            height=300,
            help="每行一个需求，可以修改、添加或删除"
        )
        
        # 将文本转换为列表
        edited_requirements = [line.strip() for line in edited_text.split('\n') if line.strip()]
        st.caption(f"共 {len(edited_requirements)} 个需求")
        
        # 更新session state
        st.session_state.tender_info['requirements'] = edited_requirements
        
        # 显示建议
        if parse_result.get_confidence_level() != "高":
            st.warning(f"⚠️ {parse_result.get_confidence_level()}置信度：建议仔细校验解析结果")
            
            # 生成改进建议
            suggestions = parser._get_suggestions(parse_result)
            if suggestions:
                st.markdown("---")
                st.subheader("💡 改进建议")
                for i, suggestion in enumerate(suggestions, 1):
                    st.markdown(f"{i}. {suggestion}")
    
    # 第二步：匹配公司数据
    if st.session_state.parse_result:
        st.markdown("---")
        st.header("🎯 第二步：匹配公司数据")
        st.markdown("根据提取的需求，智能匹配公司的资质、案例、产品")
        
        # 匹配资质
        st.subheader("📋 匹配资质")
        requirements = st.session_state.tender_info.get('requirements', [])
        matched_qualifications = db.match_qualifications(requirements)
        
        st.markdown(f"**匹配结果**: {len(matched_qualifications)} 项")
        
        # 显示匹配的资质（最多前5个）
        with st.expander("查看匹配的资质", expanded=False):
            for i, qual in enumerate(matched_qualifications[:5], 1):
                st.markdown(f"{i}. **{qual['name']}** - {qual['level']}")
                st.caption(f"证书编号：{qual.get('cert_no', 'N/A')}")
        
        # 更新session state
        st.session_state.matched_data['qualifications'] = matched_qualifications
        
        # 匹配案例
        st.subheader("📋 匹配案例")
        matched_cases = db.match_cases(requirements)
        
        st.markdown(f"**匹配结果**: {len(matched_cases)} 项")
        
        # 显示匹配的案例（最多前5个）
        with st.expander("查看匹配的案例", expanded=False):
            for i, case in enumerate(matched_cases[:5], 1):
                st.markdown(f"{i}. **{case['project_name']}**")
                st.caption(f"客户：{case.get('client', 'N/A')} | 金额：{case.get('amount', 0):,.0f} 元")
        
        # 更新session state
        st.session_state.matched_data['cases'] = matched_cases
        
        # 匹配产品
        st.subheader("📋 匹配产品")
        matched_products = db.match_products(requirements)
        
        st.markdown(f"**匹配结果**: {len(matched_products)} 项")
        
        # 显示匹配的产品（最多前5个）
        with st.expander("查看匹配的产品", expanded=False):
            for i, product in enumerate(matched_products[:5], 1):
                st.markdown(f"{i}. **{product['name']}**")
                st.caption(f"型号：{product['model']} | 分类：{product.get('category', 'N/A')}")
        
        # 更新session state
        st.session_state.matched_data['products'] = matched_products
        
        # 匹配人员（直接获取所有人员）
        st.subheader("📋 项目团队")
        matched_personnel = db.get_personnel()
        
        st.markdown(f"**可用人员**: {len(matched_personnel)} 项")
        
        # 显示人员（最多前5个）
        with st.expander("查看项目团队", expanded=False):
            for i, person in enumerate(matched_personnel[:5], 1):
                st.markdown(f"{i}. **{person['name']}** - {person.get('role', '')}")
                st.caption(f"职位：{person.get('title', 'N/A')} | 经验：{person.get('experience', 0)} 年")
        
        # 更新session state
        st.session_state.matched_data['personnel'] = matched_personnel
    
    # 第三步：生成投标文件
    if st.session_state.matched_data:
        st.markdown("---")
        st.header("🚀 第三步：生成投标文件")
        st.markdown("一键生成技术标和商务标（或合并文档）")
        st.info("✅ 生成的投标文件中将自动包含证书图片")
        
        # 生成选项
        separate_bids = st.checkbox("技术标和商务标分开生成", value=False, key="separate_bids")
        st.caption("勾选后，将生成技术标和商务标两个独立的文件")

        # 生成按钮
        if st.button("🚀 生成投标文件", type="primary", key="generate_bid"):
            try:
                # 更新 tender_info
                st.session_state.tender_info['show_cert_images'] = True
                st.session_state.tender_info['generate_time'] = datetime.now().isoformat()

                # 添加项目名称
                if st.session_state.get('project_name'):
                    st.session_state.tender_info['project_info'] = {
                        'project_name': st.session_state.project_name
                    }

                # 准备匹配数据
                matched_data = st.session_state.matched_data

                # 生成投标文件
                if separate_bids:
                    # 生成技术标和商务标分开
                    output_paths = generator.generate_separate_bids(
                        st.session_state.tender_info,
                        config.COMPANY_INFO,
                        matched_data,
                        show_cert_images=True
                    )
                    st.success("✅ 投标文件生成成功！")
                else:
                    # 生成单一投标文件
                    output_path = generator.generate_bid(
                        st.session_state.tender_info,
                        config.COMPANY_INFO,
                        matched_data,
                        show_cert_images=True
                    )
                    st.success("✅ 投标文件生成成功！")

                # 添加下载按钮
                st.markdown("---")
                st.markdown("### 📥 下载投标文件")

                # 查找生成的文件
                output_dir = Path("output")
                if output_dir.exists():
                    files = list(output_dir.glob("*.docx"))

                    if files:
                        # 根据生成模式显示文件
                        if separate_bids:
                            # 生成了技术标和商务标，显示最新的2份文件
                            latest_files = sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)[:2]
                        else:
                            # 生成单一投标文件，显示最新的1份文件
                            latest_files = sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)[:1]

                        for file in latest_files:
                            with open(file, 'rb') as f:
                                st.download_button(
                                    label=f"⬇️ 下载 {file.name}",
                                    data=f,
                                    file_name=file.name,
                                    mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                                    key=f"download_{file.name}"
                                )
                            st.caption(f"生成时间: {datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')} | 大小: {file.stat().st_size / 1024:.1f} KB")
                    else:
                        st.info("暂无生成的文件")
            except Exception as e:
                st.error(f"❌ 生成失败：{e}")
