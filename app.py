"""
投标文件自动生成系统 - 主应用（修复版）
基于 Streamlit 的Web界面

修复内容：
1. 修复 quote_file 未保存到 session state 的问题
2. 增强错误记录机制，记录上传文件和步骤状态
3. 添加更详细的日志记录
"""

import streamlit as st
from pathlib import Path
import sys
import os
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from config import COMPANY_INFO, DATA_DIR, UPLOADS_DIR, OUTPUT_DIR, PRODUCTION_BASES
from database import CompanyDatabase
from parser import TenderParser
from generator import BidDocumentGenerator
from error_handler import get_error_handler, handle_error, format_error_for_display
import shutil


# ==================== 页面配置 ====================
st.set_page_config(
    page_title="投标文件自动生成系统",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 初始化错误处理器 ====================
eh = get_error_handler()

# ==================== 调试模式 ====================
if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False

def toggle_debug_mode():
    """切换调试模式"""
    st.session_state.debug_mode = not st.session_state.debug_mode
    if st.session_state.debug_mode:
        eh.log_info("调试模式已开启")
    else:
        eh.log_info("调试模式已关闭")

# ==================== 日志辅助函数 ====================
def log_step(step_name: str, additional_info: dict = None):
    """记录步骤信息

    Args:
        step_name: 步骤名称
        additional_info: 额外信息
    """
    log_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "step": step_name
    }

    if additional_info:
        log_data.update(additional_info)

    eh.log_debug(f"步骤日志: {log_data}")

    # 保存到 session state 中的步骤日志
    if "step_logs" not in st.session_state:
        st.session_state.step_logs = []

    st.session_state.step_logs.append(log_data)


def log_file_upload(filename: str, file_size: int, file_type: str):
    """记录文件上传

    Args:
        filename: 文件名
        file_size: 文件大小（字节）
        file_type: 文件类型（tender/quote）
    """
    eh.log_info(f"文件上传 - {file_type}: {filename} ({file_size} bytes)")

    # 保存到 session state
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

    st.session_state.uploaded_files.append({
        "filename": filename,
        "size": file_size,
        "type": file_type,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


# ==================== 初始化数据库 ====================
@st.cache_resource
def get_database():
    """获取数据库实例"""
    return CompanyDatabase(DATA_DIR)

@st.cache_resource
def get_parser():
    """获取解析器实例"""
    return TenderParser()

@st.cache_resource
def get_generator():
    """获取生成器实例"""
    return BidDocumentGenerator(
        templates_dir=Path(__file__).parent / "templates",
        output_dir=OUTPUT_DIR
    )


# ==================== 侧边栏 ====================
def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.title("📄 投标文件自动生成")
        st.markdown("---")

        # 系统状态
        st.subheader("📊 系统状态")
        db = get_database()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("资质", len(db.get_qualifications()))
        with col2:
            st.metric("案例", len(db.get_cases()))

        col3, col4 = st.columns(2)
        with col3:
            st.metric("产品", len(db.get_products()))
        with col4:
            st.metric("人员", len(db.get_personnel()))

        st.markdown("---")

        # 调试模式和错误查看
        st.subheader("🔧 调试工具")

        # 调试模式开关
        debug_col1, debug_col2 = st.columns(2)
        with debug_col1:
            if st.button("🐛 调试模式", use_container_width=True,
                        type="primary" if st.session_state.debug_mode else "secondary"):
                toggle_debug_mode()
                st.rerun()

        with debug_col2:
            if st.button("📋 查看错误日志", use_container_width=True):
                st.session_state.show_errors = True
                st.rerun()

        if st.session_state.debug_mode:
            st.success("🔓 调试模式已开启 - 将显示详细错误信息")
        else:
            st.info("🔒 调试模式已关闭 - 仅显示基本错误信息")

        st.markdown("---")

        # 导航
        st.subheader("🔧 功能导航")
        page = st.radio(
            "选择功能",
            ["📄 生成投标文件", "📊 资料管理", "⚙️ 系统设置", "🔍 错误日志"],
            label_visibility="collapsed"
        )

        st.markdown("---")

        # 公司信息
        st.subheader("🏢 公司信息")
        st.info(f"{COMPANY_INFO['name']}\n{COMPANY_INFO['address']}")

        return page


# ==================== 页面1：生成投标文件 ====================
def page_generate_bid():
    """生成投标文件页面"""
    st.header("📄 生成投标文件")
    st.markdown("上传招标文件，系统将自动解析并生成投标文件。")

    # 步骤指示器
    steps = ["上传文件", "解析文件", "匹配资料", "生成文件"]
    current_step = st.session_state.get("step", 0)

    cols = st.columns(4)
    for i, step in enumerate(steps):
        with cols[i]:
            if i < current_step:
                st.success(f"✓ {step}")
            elif i == current_step:
                st.info(f"→ {step}")
            else:
                st.write(step)

    st.markdown("---")

    # 步骤1：上传文件
    with st.expander("📤 步骤1：上传招标文件", expanded=(current_step == 0)):
        st.info("💡 提示：可以上传多个招标文件（如招标文件、技术要求、商务要求等），系统会综合解析所有文件内容。")
        st.warning("⚠️ 注意：.doc格式的文件需要额外工具支持。建议将.doc文件另存为.docx格式以获得更好的兼容性。")

        col1, col2 = st.columns(2)

        with col1:
            tender_files = st.file_uploader(
                "上传招标文件（可多选）",
                type=["pdf", "doc", "docx"],
                key="tender_files",
                accept_multiple_files=True
            )

        with col2:
            quote_file = st.file_uploader(
                "上传报价单（可选）",
                type=["xls", "xlsx"],
                key="quote_file"
            )

        # 显示已上传的文件列表
        if tender_files:
            st.write(f"✓ 已选择 {len(tender_files)} 个招标文件：")
            doc_count = 0
            for i, f in enumerate(tender_files, 1):
                if f.name.lower().endswith('.doc'):
                    doc_count += 1
                    st.write(f"  {i}. ⚠️ {f.name} （旧版Word格式，可能需要安装额外工具）")
                else:
                    st.write(f"  {i}. ✓ {f.name}")

                # 记录文件上传
                log_file_upload(f.name, len(f.getbuffer()), "tender")

            if doc_count > 0:
                st.warning(f"检测到 {doc_count} 个.doc格式文件。如果解析失败，请将这些文件另存为.docx格式后重新上传。")

        # 记录报价单上传（如果有的话）
        if quote_file:
            log_file_upload(quote_file.name, len(quote_file.getbuffer()), "quote")

        if st.button("下一步：解析文件", use_container_width=True):
            if tender_files:
                # 记录步骤开始
                log_step("上传文件完成", {
                    "tender_file_count": len(tender_files),
                    "has_quote_file": quote_file is not None
                })

                # 保存所有上传的文件
                tender_paths = []
                for tender_file in tender_files:
                    tender_path = UPLOADS_DIR / tender_file.name
                    with open(tender_path, "wb") as f:
                        f.write(tender_file.getbuffer())
                    tender_paths.append(str(tender_path))

                st.session_state.tender_paths = tender_paths

                # 【修复】保存 quote_file 到 session state
                if quote_file:
                    quote_path = UPLOADS_DIR / quote_file.name
                    with open(quote_path, "wb") as f:
                        f.write(quote_file.getbuffer())
                    st.session_state.quote_path = str(quote_path)
                    st.session_state.quote_filename = quote_file.name
                else:
                    st.session_state.quote_path = None
                    st.session_state.quote_filename = None

                st.session_state.step = 1
                st.rerun()
            else:
                st.error("请先上传招标文件！")

    # 步骤2：解析文件
    if current_step >= 1:
        with st.expander("🔍 步骤2：解析招标文件", expanded=(current_step == 1)):
            if "tender_paths" in st.session_state:
                parser = get_parser()
                tender_paths = st.session_state.tender_paths

                # 记录步骤开始
                log_step("开始解析招标文件", {
                    "file_count": len(tender_paths),
                    "files": tender_paths
                })

                with st.spinner(f"正在解析 {len(tender_paths)} 个招标文件..."):
                    try:
                        # 解析所有文件并合并结果
                        tender_info = parser.parse_multiple_files(tender_paths)

                        # 记录解析结果
                        log_step("招标文件解析完成", {
                            "project_name": tender_info.get("project_info", {}).get("project_name"),
                            "require_separate_bids": tender_info.get("require_separate_bids", False)
                        })

                        # 显示解析结果
                        project_info = tender_info.get("project_info", {})

                        # 检查是否需要分开技术标和商务标
                        require_separate = tender_info.get("require_separate_bids", False)
                        if require_separate:
                            st.warning("⚠️ 检测到招标文件要求技术标和商务标分开，将分别生成两个投标文件。")
                        else:
                            st.success("✓ 将生成合并的投标文件。")

                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("项目信息")
                            st.write(f"**项目名称：** {project_info.get('project_name', '未识别')}")
                            st.write(f"**项目编号：** {project_info.get('project_no', '未识别')}")
                            st.write(f"**招标人：** {project_info.get('tenderer', '未识别')}")

                        with col2:
                            st.subheader("识别的关键词")
                            st.write(f"**产品类型：** {', '.join(tender_info.get('product_requirements', []))}")
                            st.write(f"**资质要求：** {', '.join(tender_info.get('qualification_requirements', []))}")

                        st.session_state.tender_info = tender_info

                        # 【修复】从 session state 读取报价单路径
                        if st.session_state.get("quote_path"):
                            quote_path = Path(st.session_state.quote_path)
                            try:
                                products = parser.extract_products_from_excel(quote_path)
                                st.session_state.quote_data = {"products": products}
                                st.success(f"✓ 已解析报价单，共 {len(products)} 个产品")

                                # 记录报价单解析
                                log_step("报价单解析完成", {
                                    "product_count": len(products),
                                    "quote_file": st.session_state.get("quote_filename")
                                })
                            except Exception as e:
                                # 记录错误但继续执行（报价单不是必需的）
                                error_info = handle_error(e, context="解析报价单", show_traceback=False)
                                st.warning(f"⚠️ 报价单解析失败，将跳过：{str(e)}")
                                log_step("报价单解析失败", {"error": str(e)})

                        if st.button("下一步：匹配资料", use_container_width=True):
                            st.session_state.step = 2
                            st.rerun()

                    except Exception as e:
                        # 记录详细错误
                        error_info = handle_error(e, context="解析招标文件")
                        log_step("招标文件解析失败", {"error": str(e)})

                        # 显示错误信息
                        st.error(f"解析失败：{str(e)}")

                        # 调试模式下显示详细信息
                        if st.session_state.debug_mode:
                            with st.expander("🔍 详细错误信息（调试模式）"):
                                st.markdown(format_error_for_display(error_info))

                                # 显示会话状态（用于调试）
                                st.subheader("📋 会话状态")
                                st.write("当前步骤:", st.session_state.get("step", 0))
                                st.write("是否有招标信息:", "tender_info" in st.session_state)
                                st.write("是否有匹配数据:", "matched_data" in st.session_state)
                                st.write("上传的招标文件:", st.session_state.get("tender_paths", []))
                                st.write("报价单路径:", st.session_state.get("quote_path"))
                                st.write("报价单文件名:", st.session_state.get("quote_filename"))

                                # 提供下载错误日志的选项
                                if eh.log_file.exists():
                                    with open(eh.log_file, 'r', encoding='utf-8') as f:
                                        log_content = f.read()
                                    st.download_button(
                                        label="📥 下载完整错误日志",
                                        data=log_content,
                                        file_name=eh.log_file.name,
                                        mime="text/plain"
                                    )

                        # 根据错误类型给出提示
                        error_str = str(e).lower()
                        if "doc" in error_str and "format" in error_str:
                            st.warning("💡 提示：.doc格式文件需要安装额外工具。建议将文件另存为.docx格式。")
                        elif "permission" in error_str or "denied" in error_str:
                            st.warning("💡 提示：文件访问被拒绝。请检查文件权限或关闭文件后重试。")
                        elif "memory" in error_str:
                            st.warning("💡 提示：内存不足。请尝试上传较小的文件。")
                        elif "too many values" in error_str:
                            st.warning("💡 提示：解包错误。这可能是由数据格式问题引起的。请检查上传的文件格式是否正确。")

    # 步骤3：匹配资料
    if current_step >= 2:
        with st.expander("🔗 步骤3：匹配公司资料", expanded=(current_step == 2)):
            if "tender_info" in st.session_state:
                tender_info = st.session_state.tender_info
                db = get_database()

                # 记录步骤开始
                log_step("开始匹配资料", {
                    "qualification_requirements": tender_info.get("qualification_requirements", []),
                    "product_requirements": tender_info.get("product_requirements", [])
                })

                with st.spinner("正在匹配相关资料..."):
                    try:
                        # 匹配资质
                        qual_reqs = tender_info.get("qualification_requirements", [])
                        matched_qualifications = db.match_qualifications(qual_reqs)

                        # 匹配案例
                        product_reqs = tender_info.get("product_requirements", [])
                        matched_cases = db.match_cases(
                            industry=None,  # 不限制行业
                            product_type=product_reqs[0] if product_reqs else None,
                            limit=5
                        )

                        # 匹配产品
                        matched_products = db.match_products(product_reqs)

                        # 调试信息（显示解析出来的关键词）
                        st.info("💡 解析信息：")
                        st.write(f"识别的资质要求关键词：{qual_reqs}")
                        st.write(f"识别的产品类型关键词：{product_reqs}")

                        st.session_state.matched_data = {
                            "qualifications": matched_qualifications,
                            "cases": matched_cases,
                            "products": matched_products,
                        }

                        # 记录匹配结果
                        log_step("资料匹配完成", {
                            "matched_qualifications": len(matched_qualifications),
                            "matched_cases": len(matched_cases),
                            "matched_products": len(matched_products)
                        })

                        # 显示匹配结果
                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader(f"✓ 匹配到 {len(matched_qualifications)} 项资质")
                            for qual in matched_qualifications:
                                st.write(f"• {qual['name']}（{qual['level']}）")

                            st.subheader(f"✓ 匹配到 {len(matched_cases)} 个案例")
                            for case in matched_cases:
                                st.write(f"• {case['project_name']} - {case['amount'] / 10000:.1f}万元")

                        with col2:
                            st.subheader(f"✓ 匹配到 {len(matched_products)} 个产品")
                            for product in matched_products:
                                st.write(f"• {product['name']} ({product['model']})")

                        # 允许用户调整匹配结果
                        st.subheader("📝 补充信息")
                        delivery_days = st.number_input("交货期（天）", min_value=1, max_value=365, value=30)
                        warranty_period = st.text_input("质保期", value="一年")

                        if st.button("下一步：生成文件", use_container_width=True):
                            st.session_state.step = 3
                            st.session_state.delivery_days = delivery_days
                            st.session_state.warranty_period = warranty_period
                            st.rerun()

                    except Exception as e:
                        # 记录详细错误
                        error_info = handle_error(e, context="匹配资料")
                        log_step("资料匹配失败", {"error": str(e)})

                        # 显示错误信息
                        st.error(f"匹配失败：{str(e)}")

                        # 调试模式下显示详细信息
                        if st.session_state.debug_mode:
                            with st.expander("🔍 详细错误信息（调试模式）"):
                                st.markdown(format_error_for_display(error_info))

    # 步骤4：生成文件
    if current_step >= 3:
        # 直接启用证书图片功能
        show_cert_images = True

        with st.expander("📝 步骤4：生成投标文件", expanded=(current_step == 3)):
            st.info("点击下方按钮生成投标文件")

            generator = get_generator()
            tender_info = st.session_state.tender_info
            require_separate = tender_info.get("require_separate_bids", False)

            if require_separate:
                st.warning("⚠️ 根据招标文件要求，将分别生成技术标和商务标。")
            else:
                st.success("✓ 将生成合并的投标文件。")

            if st.button("🚀 生成投标文件", type="primary", use_container_width=True):
                # 记录生成开始
                log_step("开始生成投标文件", {
                    "require_separate_bids": require_separate,
                    "show_cert_images": show_cert_images
                })

                # 调试信息
                if st.session_state.debug_mode:
                    st.info("🔍 调试: 正在启用证书图片转换功能")

                with st.spinner("正在生成投标文件..."):
                    try:
                        if require_separate:
                            # 生成技术标和商务标
                            output_paths = generator.generate_separate_bids(
                                tender_info=tender_info,
                                company_info=COMPANY_INFO,
                                matched_data=st.session_state.matched_data,
                                quote_data=st.session_state.get("quote_data", {}),
                                show_cert_images=show_cert_images
                            )

                            st.success(f"✓ 已生成2个投标文件：")
                            st.write(f"  • {output_paths['tech'].name}")
                            st.write(f"  • {output_paths['commercial'].name}")

                            # 调试信息
                            if st.session_state.debug_mode:
                                st.success("✓ 调试: 证书图片已插入到生成的文档中")

                            # 记录生成成功
                            log_step("投标文件生成成功", {
                                "tech_file": output_paths['tech'].name,
                                "commercial_file": output_paths['commercial'].name,
                                "cert_images_enabled": show_cert_images
                            })

                            # 下载技术标
                            with open(output_paths['tech'], "rb") as f:
                                st.download_button(
                                    label="📥 下载技术标",
                                    data=f.read(),
                                    file_name=output_paths['tech'].name,
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    key="download_tech"
                                )

                            # 下载商务标
                            with open(output_paths['commercial'], "rb") as f:
                                st.download_button(
                                    label="📥 下载商务标",
                                    data=f.read(),
                                    file_name=output_paths['commercial'].name,
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    key="download_commercial"
                                )
                        else:
                            # 生成单一投标文件
                            output_path = generator.generate_bid(
                                tender_info=tender_info,
                                company_info=COMPANY_INFO,
                                matched_data=st.session_state.matched_data,
                                quote_data=st.session_state.get("quote_data", {}),
                                show_cert_images=show_cert_images
                            )

                            st.success(f"✓ 投标文件已生成：{output_path.name}")

                            # 调试信息
                            if st.session_state.debug_mode:
                                st.success("✓ 调试: 证书图片已插入到生成的文档中")

                            # 记录生成成功
                            log_step("投标文件生成成功", {
                                "file": output_path.name,
                                "cert_images_enabled": True
                            })

                            # 下载按钮
                            with open(output_path, "rb") as f:
                                st.download_button(
                                    label="📥 下载投标文件",
                                    data=f.read(),
                                    file_name=output_path.name,
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                )

                    except Exception as e:
                        # 记录详细错误
                        error_info = handle_error(e, context="生成投标文件")
                        log_step("投标文件生成失败", {"error": str(e)})

                        # 显示错误信息
                        st.error(f"生成失败：{str(e)}")

                        # 调试模式下显示详细信息
                        if st.session_state.debug_mode:
                            with st.expander("🔍 详细错误信息（调试模式）"):
                                st.markdown(format_error_for_display(error_info))

                                # 显示会话状态（用于调试）
                                st.subheader("📋 会话状态")
                                st.write("当前步骤:", st.session_state.get("step", 0))
                                st.write("是否有招标信息:", "tender_info" in st.session_state)
                                st.write("是否有匹配数据:", "matched_data" in st.session_state)

                                # 显示步骤日志
                                if "step_logs" in st.session_state:
                                    st.subheader("📋 步骤日志")
                                    for i, log in enumerate(st.session_state.step_logs, 1):
                                        st.write(f"{i}. {log}")

                                # 显示上传的文件
                                if "uploaded_files" in st.session_state:
                                    st.subheader("📋 上传的文件")
                                    for f in st.session_state.uploaded_files:
                                        st.write(f"• {f['filename']} ({f['size']} bytes) - {f['type']}")

                                # 提供下载错误日志的选项
                                if eh.log_file.exists():
                                    with open(eh.log_file, 'r', encoding='utf-8') as f:
                                        log_content = f.read()
                                    st.download_button(
                                        label="📥 下载完整错误日志",
                                        data=log_content,
                                        file_name=eh.log_file.name,
                                        mime="text/plain"
                                    )

                        # 根据错误类型给出提示
                        error_str = str(e).lower()
                        if "too many values" in error_str:
                            st.warning("💡 提示：解包错误。请检查数据文件格式是否正确。")
                        elif "template" in error_str or "模板" in error_str:
                            st.warning("💡 提示：模板文件缺失或损坏。请检查 templates 目录。")
                        elif "key" in error_str or "缺少" in error_str:
                            st.warning("💡 提示：缺少必要的数据字段。请检查资料是否完整。")

            if st.button("🔄 重新开始", use_container_width=True):
                st.session_state.clear()
                st.rerun()


# ==================== 主函数 ====================
def main():
    """主函数"""
    page = render_sidebar()

    if page == "📄 生成投标文件":
        page_generate_bid()
    elif page == "📊 资料管理":
        st.info("资料管理页面（待实现）")
    elif page == "⚙️ 系统设置":
        st.info("系统设置页面（待实现）")
    elif page == "🔍 错误日志":
        if st.session_state.get("show_errors"):
            st.header("🔍 错误日志")
            st.markdown("以下是最近的错误日志：")

            recent_errors = eh.get_recent_errors(20)
            if recent_errors:
                for i, error in enumerate(recent_errors, 1):
                    with st.expander(f"错误 {i}: {error.get('error_type', 'Unknown')} - {error.get('error_message', '')[:50]}"):
                        st.markdown(format_error_for_display(error))
            else:
                st.info("暂无错误日志")

            if st.button("关闭错误日志"):
                st.session_state.show_errors = False
                st.rerun()
        else:
            st.info("点击侧边栏的'查看错误日志'按钮查看错误")


if __name__ == "__main__":
    main()
