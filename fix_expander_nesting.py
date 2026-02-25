"""
修复 expander 嵌套问题的补丁

问题：Streamlit 不允许在 expander 内嵌套另一个 expander
错误：StreamlitAPIException: Expanders may not be nested inside other expanders

解决方案：使用 st.code 或 st.text_area 代替嵌套 expander
"""

# 在 app.py 中找到所有嵌套 expander 的位置

# 位置1：步骤2中（约第337行）
# with st.expander("🔍 详细错误信息（调试模式）"):
# 应该改为：
# if st.session_state.debug_mode:
#     st.subheader("🔍 详细错误信息（调试模式）")
#     st.markdown(format_error_for_display(error_info))
#     # ... 其他调试信息

# 位置2：步骤3中（如果有的话）
# 类似的修改

# 位置3：步骤4中（约第525行）
# 类似的修改


def fix_nested_expanders():
    """
    批量修复代码中的嵌套 expander 问题

    搜索模式：`with st.expander(...):` 在另一个 `with st.expander(...):` 内部
    替换为：使用 st.subheader + st.code 显示调试信息
    """
    code_snippets = [
        {
            "old": """                        if st.session_state.debug_mode:
                            with st.expander("🔍 详细错误信息（调试模式）"):
                                st.markdown(format_error_for_display(error_info))""",
            "new": """                        if st.session_state.debug_mode:
                            st.subheader("🔍 详细错误信息（调试模式）")
                            st.markdown(format_error_for_display(error_info))"""
        },
        {
            "old": """                                # 显示会话状态（用于调试）
                                st.subheader("📋 会话状态")""",
            "new": """                                # 显示会话状态（用于调试）
                                st.markdown("---")
                                st.subheader("📋 会话状态")"""
        },
    ]

    return code_snippets


if __name__ == "__main__":
    # 生成修复建议
    print("修复 expander 嵌套问题的方法：")
    print("\n1. 将嵌套的 st.expander 改为 st.subheader")
    print("2. 如果需要显示大量信息，使用 st.code()")
    print("\n示例：")
    print("\n错误代码：")
    print("""
with st.expander("步骤1"):
    # ... 一些代码 ...
    if debug_mode:
        with st.expander("详细信息"):  # ❌ 嵌套 expander
            st.write("调试信息")
    """)
    print("\n修复后：")
    print("""
with st.expander("步骤1"):
    # ... 一些代码 ...
    if debug_mode:
        st.subheader("详细信息")  # ✅ 不嵌套
        st.write("调试信息")
        if detailed_info:
            st.code(detailed_info, language='json')  # ✅ 代码块显示
    """)
