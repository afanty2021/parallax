"""
Parallax 日志配置模块

该模块为 Parallax 分布式AI推理系统提供统一的日志配置和管理功能。
主要特性包括：

1. 彩色日志输出：支持不同日志级别的颜色区分，提高可读性
2. 统一格式化：提供一致的日志格式，包含时间、级别、模块名等信息
3. 线程安全：使用锁机制确保多线程环境下的安全性
4. 灵活配置：支持动态调整日志级别和输出格式
5. 环境适配：自动检测终端环境，禁用非终端环境的颜色输出

日志级别颜色说明：
- DEBUG: 青色 (CYAN) - 调试信息，开发阶段使用
- INFO: 绿色 (GREEN) - 一般信息，正常运行状态
- WARNING: 黄色 (YELLOW) - 警告信息，需要注意但不影响运行
- ERROR: 红色 (RED) - 错误信息，影响功能但可继续运行
- CRITICAL: 紫色 (MAGENTA) - 严重错误，可能导致系统崩溃

使用示例：
    from parallax_utils.logging_config import get_logger, set_log_level

    logger = get_logger(__name__)
    set_log_level("INFO")
    logger.info("系统启动成功")
"""

import logging
import os
import sys
import threading
from typing import Optional

# 导出的公共接口
__all__ = ["get_logger", "use_parallax_log_handler", "set_log_level"]

# 线程锁，确保日志初始化的线程安全
_init_lock = threading.Lock()

# 默认日志处理器，全局唯一
_default_handler: logging.Handler | None = None


class _Ansi:
    """
    ANSI 颜色代码定义类

    定义了终端输出的颜色控制代码，用于实现彩色日志输出。
    这些代码遵循 ANSI escape sequence 标准。
    """
    RESET = "\033[0m"      # 重置所有格式
    BOLD = "\033[1m"       # 粗体
    RED = "\033[31m"       # 红色
    YELLOW = "\033[33m"    # 黄色
    GREEN = "\033[32m"     # 绿色
    CYAN = "\033[36m"      # 青色
    MAGENTA = "\033[35m"   # 紫色


# 日志级别与颜色的映射关系
_LEVEL_COLOR = {
    "DEBUG": _Ansi.CYAN,      # 调试信息用青色
    "INFO": _Ansi.GREEN,      # 一般信息用绿色
    "WARNING": _Ansi.YELLOW,  # 警告信息用黄色
    "ERROR": _Ansi.RED,       # 错误信息用红色
    "CRITICAL": _Ansi.MAGENTA, # 严重错误用紫色
}


class CustomFormatter(logging.Formatter):
    """
    自定义日志格式化器

    为 Parallax 系统提供彩色、结构化的日志输出格式。
    格式包括：时间戳、日志级别（带颜色）、模块名、消息内容。
    """

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        """
        格式化日志记录

        Args:
            record (logging.LogRecord): 日志记录对象

        Returns:
            str: 格式化后的日志字符串
        """
        # 转换日志级别为大写
        levelname = record.levelname.upper()

        # 获取对应级别的颜色，如果没有对应颜色则使用默认（无颜色）
        levelcolor = _LEVEL_COLOR.get(levelname, "")

        # 为日志记录对象添加颜色相关的属性
        record.levelcolor = levelcolor
        record.bold = _Ansi.BOLD
        record.reset = _Ansi.RESET

        # caller_block: last path component + line no
        pathname = record.pathname.rsplit("/", 1)[-1]
        record.caller_block = f"{pathname}:{record.lineno}"

        return super().format(record)


def _enable_default_handler(target_module_prefix):
    """Attach the default handler to the root logger with a name-prefix filter.

    Accepts either a single string prefix or an iterable of prefixes; a record
    passes the filter if its logger name starts with any provided prefix.
    """
    root = logging.getLogger()

    # attach the handler only to loggers that start with any of target prefixes
    class _ModuleFilter(logging.Filter):
        def __init__(self, prefixes):
            super().__init__()
            if isinstance(prefixes, str):
                self._prefixes = (prefixes,)
            else:
                try:
                    self._prefixes = tuple(prefixes)
                except TypeError:
                    self._prefixes = (str(prefixes),)

        def filter(self, rec: logging.LogRecord) -> bool:
            return any(rec.name.startswith(p) for p in self._prefixes)

    _default_handler.addFilter(_ModuleFilter(target_module_prefix))
    root.addHandler(_default_handler)


def _initialize_if_necessary():
    global _default_handler

    with _init_lock:
        if _default_handler is not None:
            return

        fmt = (
            "{asctime}.{msecs:03.0f} "
            "[{bold}{levelcolor}{levelname:<8}{reset}] "
            "{caller_block:<25} {message}"
        )
        formatter = CustomFormatter(fmt=fmt, style="{", datefmt="%b %d %H:%M:%S")
        _default_handler = logging.StreamHandler(stream=sys.stdout)
        _default_handler.setFormatter(formatter)

        # root level from env or INFO
        logging.getLogger().setLevel("INFO")

        # Allow logs from our main packages by default
        _enable_default_handler(("parallax", "scheduling", "backend", "sglang"))


def set_log_level(level_name: str):
    """Set the root logger level."""
    _initialize_if_necessary()
    logging.getLogger().setLevel(level_name.upper())
    if level_name.upper() == "DEBUG":
        os.environ["RUST_LOG"] = "info"


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Grab a logger with parallax’s default handler attached.
    Call this in every module instead of logging.getLogger().
    """
    _initialize_if_necessary()
    return logging.getLogger(name)


def use_parallax_log_handler(for_root: bool = True):
    """
    Extend the custom handler to the root logger (so *all* libraries print
    with the same style) or to any logger you call this on.

    Example
    -------
        from parallax.logging import use_parallax_log_handler
        use_parallax_log_handler()            # now requests, hivemind, etc. share the style
    """
    del for_root
    _initialize_if_necessary()
    root = logging.getLogger()
    if _default_handler not in root.handlers:
        root.addHandler(_default_handler)
