#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误处理器测试脚本
"""

import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from error_handler import get_error_handler, handle_error, format_error_for_display


def test_basic_error():
    """测试基本的错误记录"""
    print("测试1: 基本错误记录")
    print("=" * 60)

    try:
        # 故意触发一个错误
        result = 1 / 0
    except Exception as e:
        error_info = handle_error(e, context="测试除零错误")
        print("✓ 错误已记录")
        print(f"  错误类型: {error_info.get('error_type')}")
        print(f"  错误信息: {error_info.get('error_message')}")
        print()

    # 测试格式化显示
    print("格式化后的错误信息:")
    print("-" * 60)
    print(format_error_for_display(error_info))
    print()


def test_file_not_found():
    """测试文件不存在错误"""
    print("测试2: 文件不存在错误")
    print("=" * 60)

    try:
        with open("/不存在的文件.txt", "r") as f:
            content = f.read()
    except Exception as e:
        error_info = handle_error(e, context="读取测试文件")
        print("✓ 错误已记录")
        print(f"  错误类型: {error_info.get('error_type')}")
        print()


def test_key_error():
    """测试字典键错误"""
    print("测试3: 字典键错误")
    print("=" * 60)

    try:
        data = {"name": "测试"}
        value = data["不存在的键"]
    except Exception as e:
        error_info = handle_error(e, context="访问字典键")
        print("✓ 错误已记录")
        print()


def test_get_recent_errors():
    """测试获取最近的错误"""
    print("测试4: 获取最近的错误")
    print("=" * 60)

    eh = get_error_handler()
    recent_errors = eh.get_recent_errors(limit=3)
    print(f"✓ 找到 {len(recent_errors)} 个最近的错误")

    if recent_errors:
        print("\n最近的错误:")
        for i, error in enumerate(recent_errors, 1):
            print(f"  {i}. {error.get('error_type', 'Unknown')}")
    print()


def test_get_log_content():
    """测试获取日志内容"""
    print("测试5: 获取日志内容")
    print("=" * 60)

    eh = get_error_handler()
    log_content = eh.get_log_content(lines=50)

    if log_content:
        print(f"✓ 日志内容（前50行）:")
        print("-" * 60)
        print(log_content)
        print("-" * 60)
    else:
        print("  日志为空或不存在")
    print()


def main():
    """主测试函数"""
    print()
    print("=" * 60)
    print("错误处理器功能测试")
    print("=" * 60)
    print()

    # 运行测试
    test_basic_error()
    test_file_not_found()
    test_key_error()
    test_get_recent_errors()
    test_get_log_content()

    print("=" * 60)
    print("✓ 所有测试完成")
    print("=" * 60)

    # 显示日志文件位置
    eh = get_error_handler()
    print()
    print(f"日志文件位置: {eh.log_file}")
    print(f"日志文件存在: {eh.log_file.exists()}")


if __name__ == "__main__":
    main()
