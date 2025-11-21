"""
Parallax 分布式AI推理引擎 - 聊天服务启动入口

该模块是 Parallax 系统中聊天服务的启动入口点，负责：
1. 解析命令行参数
2. 配置日志级别
3. 启动节点聊天HTTP服务器
4. 处理异常和优雅关闭

使用方式:
    python -m parallax.launch_chat --help
"""

from parallax.server.node_chat_http_server import run_node_chat_http_server
from parallax.server.server_args import parse_args
from parallax_utils.logging_config import get_logger, set_log_level

# 获取当前模块的日志记录器，用于记录运行时信息
logger = get_logger(__name__)

if __name__ == "__main__":
    """
    主程序入口点

    执行流程：
    1. 解析命令行参数（包括模型路径、端口配置等）
    2. 根据参数设置日志级别
    3. 启动聊天HTTP服务器，提供对外聊天接口
    4. 处理键盘中断信号，实现优雅关闭
    5. 捕获并记录其他异常
    """
    try:
        # 解析命令行参数，获取模型配置、网络设置等
        args = parse_args()

        # 设置全局日志级别，支持 DEBUG、INFO、WARNING、ERROR、CRITICAL
        set_log_level(args.log_level)

        # 记录解析后的参数，便于调试
        logger.debug(f"解析的命令行参数: {args}")

        # 启动节点聊天HTTP服务器，开始提供聊天推理服务
        # 该服务器将监听指定端口，接收HTTP请求并进行分布式推理
        run_node_chat_http_server(args)

    except KeyboardInterrupt:
        # 处理键盘中断（Ctrl+C），记录优雅关闭信息
        logger.debug("接收到中断信号，正在关闭服务器...")

    except Exception as e:
        # 捕获并记录所有未处理的异常，便于调试和错误追踪
        logger.exception(e)
