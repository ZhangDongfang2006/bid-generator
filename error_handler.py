#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误处理和日志记录模块
"""

import logging
import sys
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional


class ErrorHandler:
    """错误处理器 - 统一处理错误和日志"""

    def __init__(self, log_dir: Path = None):
        """初始化错误处理器

        Args:
            log_dir: 日志目录，默认为当前目录下的 logs 文件夹
        """
        if log_dir is None:
            log_dir = Path(__file__).parent / "logs"

        self.log_dir = log_dir
        self.log_dir.mkdir(exist_ok=True)

        # 设置日志文件名（按日期）
        today = datetime.now().strftime("%Y-%m-%d")
        self.log_file = self.log_dir / f"error_{today}.log"

        # 配置日志
        self._setup_logger()

    def _setup_logger(self):
        """配置日志记录器"""
        self.logger = logging.getLogger("BidGenerator")
        self.logger.setLevel(logging.DEBUG)

        # 清除已有的处理器
        self.logger.handlers.clear()

        # 文件处理器（记录所有级别）
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # 控制台处理器（只记录WARNING及以上级别）
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def log_error(self, error: Exception, context: str = "",
                   show_traceback: bool = True) -> dict:
        """记录错误并返回格式化的错误信息

        Args:
            error: 异常对象
            context: 错误上下文信息（如：正在做什么操作）
            show_traceback: 是否显示完整的堆栈跟踪

        Returns:
            包含错误信息的字典
        """
        error_type = type(error).__name__
        error_msg = str(error)

        # 记录错误
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "context": context,
            "error_type": error_type,
            "error_message": error_msg
        }

        if show_traceback:
            tb_str = traceback.format_exc()
            log_entry["traceback"] = tb_str
            self.logger.error(f"{context}\n错误类型: {error_type}\n错误信息: {error_msg}\n堆栈跟踪:\n{tb_str}")
        else:
            self.logger.error(f"{context}\n错误类型: {error_type}\n错误信息: {error_msg}")

        return log_entry

    def log_info(self, message: str):
        """记录信息日志"""
        self.logger.info(message)

    def log_warning(self, message: str):
        """记录警告日志"""
        self.logger.warning(message)

    def log_debug(self, message: str):
        """记录调试日志"""
        self.logger.debug(message)

    def get_recent_errors(self, limit: int = 10) -> list:
        """获取最近的错误日志

        Args:
            limit: 返回的错误数量

        Returns:
            错误列表
        """
        if not self.log_file.exists():
            return []

        errors = []
        with open(self.log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 简单解析（实际可以使用更复杂的日志解析）
        current_error = {}
        for line in lines:
            if line.strip().startswith("错误类型:"):
                if current_error:
                    errors.append(current_error)
                current_error = {}
            current_error.setdefault('log', []).append(line.strip())

        if current_error:
            errors.append(current_error)

        return errors[-limit:]

    def get_log_content(self, lines: int = 100) -> str:
        """获取日志文件内容

        Args:
            lines: 读取的行数

        Returns:
            日志内容
        """
        if not self.log_file.exists():
            return "日志文件不存在"

        with open(self.log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            return ''.join(all_lines[-lines:])

    def clear_logs(self):
        """清空日志文件"""
        if self.log_file.exists():
            self.log_file.unlink()
            self.logger.info("日志已清空")


# 全局错误处理器实例
_error_handler = None


def get_error_handler() -> ErrorHandler:
    """获取全局错误处理器实例"""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


def handle_error(error: Exception, context: str = "",
                 show_traceback: bool = True,
                 reraise: bool = False) -> dict:
    """处理错误的便捷函数

    Args:
        error: 异常对象
        context: 错误上下文
        show_traceback: 是否显示堆栈跟踪
        reraise: 是否重新抛出异常

    Returns:
        错误信息字典

    Raises:
        Exception: 如果 reraise=True
    """
    handler = get_error_handler()
    error_info = handler.log_error(error, context, show_traceback)

    if reraise:
        raise error

    return error_info


def get_full_traceback(error: Exception) -> str:
    """获取完整的堆栈跟踪字符串

    Args:
        error: 异常对象

    Returns:
        格式化的堆栈跟踪
    """
    return ''.join(traceback.format_exception(type(error), error, error.__traceback__))


def format_error_for_display(error_info: dict) -> str:
    """格式化错误信息用于显示

    Args:
        error_info: 错误信息字典

    Returns:
        格式化的字符串
    """
    result = []

    if "timestamp" in error_info:
        result.append(f"⏰ 时间: {error_info['timestamp']}")

    if "context" in error_info and error_info["context"]:
        result.append(f"📍 上下文: {error_info['context']}")

    if "error_type" in error_info:
        result.append(f"❌ 错误类型: {error_info['error_type']}")

    if "error_message" in error_info:
        result.append(f"💬 错误信息: {error_info['error_message']}")

    if "traceback" in error_info:
        result.append("\n🔍 堆栈跟踪:")
        result.append("```")
        result.append(error_info["traceback"])
        result.append("```")

    return "\n".join(result)
