"""
调试信息显示优化方案

问题：调试信息太多导致 Streamlit 前端渲染卡住
解决方案：限制显示数量、使用折叠组件、分页显示
"""

def fix_debug_info_display():
    """
    修复调试信息显示
    
    方案1：限制显示的数量
    方案2：使用折叠组件
    方案3：使用 st.code 或 st.text_area
    """
    
    solution1 = """
    # 方案1：限制显示的数量
    if st.session_state.debug_mode:
        st.markdown("---")
        st.subheader("🔍 详细错误信息（调试模式）")
        st.markdown(format_error_for_display(error_info))
        
        # 只显示最近的10条步骤日志
        st.subheader("📋 步骤日志（最近10条）")
        if "step_logs" in st.session_state:
            recent_logs = st.session_state.step_logs[-10:]  # 只显示最近10条
            for i, log in enumerate(recent_logs, 1):
                st.write(f"{i}. {log['step']}")
            
            if len(st.session_state.step_logs) > 10:
                st.info(f"... 还有 {len(st.session_state.step_logs) - 10} 条日志")
    """
    
    solution2 = """
    # 方案2：使用折叠组件
    if st.session_state.debug_mode:
        st.markdown("---")
        st.subheader("🔍 详细错误信息（调试模式）")
        with st.expander("显示错误详情"):  # 外层折叠
            st.markdown(format_error_for_display(error_info))
        
        # 会话状态
        with st.expander("显示会话状态"):
            st.subheader("📋 会话状态")
            st.write("当前步骤:", st.session_state.get("step", 0))
            # ...
        
        # 步骤日志
        with st.expander("显示步骤日志"):
            st.subheader("📋 步骤日志")
            if "step_logs" in st.session_state:
                for i, log in enumerate(st.session_state.step_logs, 1):
                    st.write(f"{i}. {log}")
        
        # 上传的文件
        with st.expander("显示上传的文件"):
            st.subheader("📋 上传的文件")
            if "uploaded_files" in st.session_state:
                for f in st.session_state.uploaded_files:
                    st.write(f"• {f['filename']} ({f['size']} bytes) - {f['type']}")
    """
    
    solution3 = """
    # 方案3：使用 st.code 或 st.text_area 显示大段文本
    if st.session_state.debug_mode:
        st.markdown("---")
        st.subheader("🔍 详细错误信息（调试模式）")
        
        # 使用 st.code 显示错误信息（可折叠）
        with st.expander("显示错误详情"):
            st.code(format_error_for_display(error_info), language='text')
        
        # 使用 st.text_area 显示步骤日志（可折叠）
        with st.expander("显示步骤日志（最近20条）"):
            if "step_logs" in st.session_state:
                import json
                logs_text = json.dumps(st.session_state.step_logs[-20:], 
                                      ensure_ascii=False, indent=2)
                st.text_area("步骤日志", logs_text, height=200)
    """
    
    return solution1, solution2, solution3


def apply_fix(solution_num=1):
    """
    应用修复到 app.py
    
    Args:
        solution_num: 使用的方案编号（1/2/3）
    """
    import re
    from pathlib import Path
    
    app_file = Path("/Users/zhangdongfang/workspace/bid-generator/app.py")
    
    # 读取文件
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 根据方案选择修复代码
    solutions = fix_debug_info_display()
    if solution_num == 1:
        fix_code = solutions[0]
    elif solution_num == 2:
        fix_code = solutions[1]
    else:
        fix_code = solutions[2]
    
    # 找到需要替换的部分（步骤4的调试信息显示部分）
    # 这里需要更精确地定位
    
    # 方案4：在所有调试信息显示后添加 st.rerun() 来强制刷新
    # 这不是最佳方案，但可以确保前端更新
    
    print(f"请手动应用修复方案 {solution_num}")
    print(f"修复代码：")
    print(fix_code)
    
    # 或者直接添加 st.rerun() 在调试信息显示后
    if st.rerun() in content:
        print("已经包含 st.rerun()")
    else:
        print("建议在调试信息显示后添加 st.rerun()")
        print("但这会导致页面重新加载，可能不是最佳方案")


if __name__ == "__main__":
    print("调试信息显示优化方案")
    print("=" * 60)
    
    print("\n【方案1：限制显示的数量（推荐）】")
    solutions = fix_debug_info_display()
    print(solutions[0])
    
    print("\n" + "=" * 60)
    print("【方案2：使用折叠组件】")
    print(solutions[1])
    
    print("\n" + "=" * 60)
    print("【方案3：使用 st.code 或 st.text_area】")
    print(solutions[2])
    
    print("\n" + "=" * 60)
    print("【临时解决方案】")
    print("1. 在调试信息显示后添加：")
    print("   st.rerun()")
    print("2. 这会强制页面重新加载，但可能导致用户体验问题")
    print("3. 或者暂时关闭调试模式进行操作")
    
    print("\n建议：使用方案1，限制显示的调试信息数量。")
