"""
Parallax 服务器命令行参数解析器

该模块为 Parallax 分布式推理执行器提供命令行参数解析功能，
支持各种配置选项，包括模型加载、层分片和性能调优等。

主要功能：
1. 解析HTTP服务器配置参数
2. 解析P2P网络(Lattica)配置参数
3. 解析模型配置参数
4. 解析KV缓存配置参数
5. 解析调度器配置参数
6. 解析GPU/SGLang专用配置参数
7. 参数有效性验证

使用示例：
    python -m parallax.launch_chat --model-path Qwen/Qwen3-0.6B --port 3000 --max-batch-size 16
"""

import argparse

from parallax_utils.logging_config import get_logger

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    """
    解析 Parallax 执行器的命令行参数

    该函数定义并解析所有支持命令行参数，包括：
    - HTTP服务器配置：主机地址、端口等
    - P2P网络配置：初始节点、中继服务器等
    - 模型配置：模型路径、数据类型、层分配等
    - 缓存配置：KV缓存内存分配、块大小等
    - 调度配置：批处理大小、超时设置等
    - GPU后端配置：注意力计算、MoE运行器等

    Returns:
        argparse.Namespace: 包含所有解析后参数的命名空间对象
    """
    parser = argparse.ArgumentParser(
        description="Parallax Executor - Distributed LLM Inference",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # ===== HTTP 服务器配置 =====
    # HTTP服务器监听的主机地址，默认为localhost（仅本地访问）
    parser.add_argument("--host", type=str, default="localhost", help="HTTP服务器的主机地址")

    # HTTP服务器监听的端口号，默认3000
    parser.add_argument("--port", type=int, default=3000, help="HTTP服务器的端口号")

    # 节点聊天HTTP服务器的专用端口，默认3002，用于处理聊天推理请求
    parser.add_argument(
        "--node-chat-port", type=int, default=3002, help="节点聊天HTTP服务器的端口号"
    )

    # ===== Lattica P2P 网络配置 =====
    # DHT（分布式哈希表）的初始节点列表，用于加入P2P网络
    parser.add_argument("--initial-peers", nargs="+", default=[], help="DHT初始节点地址列表")

    # 调度器节点的网络地址，用于连接到集群调度器
    parser.add_argument("--scheduler-addr", type=str, default=None, help="调度器节点的网络地址")

    # 中继服务器节点列表，用于网络拓扑中转和连接优化
    parser.add_argument("--relay-servers", nargs="+", default=[], help="中继DHT节点地址列表")

    # Lattica P2P网络的TCP监听端口，0表示自动分配
    parser.add_argument("--tcp-port", type=int, default=0, help="Lattica TCP监听端口（0为自动分配）")

    # Lattica P2P网络的UDP监听端口，0表示自动分配
    parser.add_argument("--udp-port", type=int, default=0, help="Lattica UDP监听端口（0为自动分配）")

    # 需要向网络宣告的多地址列表，用于其他节点发现和连接此节点
    parser.add_argument(
        "--announce-maddrs", nargs="+", default=[], help="向P2P网络宣告的多地址列表"
    )

    # DHT键的前缀，用于区分不同的应用或网络，默认为"gradient"
    parser.add_argument("--dht-prefix", type=str, default="gradient", help="DHT键的前缀标识")

    # 请求完成时的通知URL，用于回调机制和外部系统集成
    parser.add_argument(
        "--notify-url", type=str, default=None, help="请求完成时的回调通知URL"
    )

    # ===== 模型配置 =====
    # 模型仓库路径或模型名称，支持HuggingFace模型ID
    # 例如：'mlx-community/Qwen3-0.6B-bf16' 或 '/path/to/local/model'
    parser.add_argument(
        "--model-path",
        type=str,
        default=None,
        help="模型仓库路径或模型名称（如：'mlx-community/Qwen3-0.6B-bf16'）",
    )

    # 模型支持的最大序列长度，决定能处理的最大输入+输出token数量
    # None表示使用模型默认值
    parser.add_argument(
        "--max-sequence-length",
        type=int,
        default=None,
        help="模型支持的最大序列长度",
    )

    # GPU内存中用于存储模型参数的比例，默认65%
    # 剩余内存将用于KV缓存和其他计算
    parser.add_argument(
        "--param-mem-ratio",
        type=float,
        default=0.65,
        help="用于存储模型参数的GPU内存比例（默认0.65）",
    )

    # GPU内存中用于KV缓存的比例，默认25%
    # 影响能同时处理的请求数量和上下文长度
    parser.add_argument(
        "--kvcache-mem-ratio",
        type=float,
        default=0.25,
        help="用于KV缓存的GPU内存比例（默认0.25）",
    )

    # 当前节点负责的模型层起始索引（包含）
    # 用于模型分片，None表示自动分配
    parser.add_argument(
        "--start-layer",
        type=int,
        default=None,
        help="当前分片负责的起始层索引（包含）",
    )

    # 当前节点负责的模型层结束索引（不包含）
    # 用于模型分片，None表示自动分配
    parser.add_argument(
        "--end-layer", type=int, default=None, help="当前分片负责的结束层索引（不包含）"
    )

    # 模型权重和计算的数据类型，影响内存占用和计算精度
    # bfloat16: 平衡精度和内存，推荐选择
    # float16: 更省内存，可能影响精度
    # float32: 最高精度，占用内存最多
    parser.add_argument(
        "--dtype",
        type=str,
        default="bfloat16",
        choices=["float16", "bfloat16", "float32"],
        help="模型权重和计算的数据类型",
    )

    # ===== KV 缓存配置 =====
    # 可用内存中用于KV缓存的分数（0.0到1.0）
    # 较高的值支持更多并发请求和更长上下文，但可能导致OOM
    parser.add_argument(
        "--kv-cache-memory-fraction",
        type=float,
        default=0.8,
        help="用于KV缓存的可用内存分数（0.0到1.0）",
    )

    # KV缓存管理的块大小，影响内存分配效率
    # 较大的块减少内存碎片，较小的块提高内存利用率
    parser.add_argument(
        "--kv-block-size", type=int, default=64, help="KV缓存管理的块大小"
    )

    # 启用前缀缓存复用，可以显著提高重复前缀请求的推理速度
    parser.add_argument(
        "--enable-prefix-cache", action="store_true", help="启用前缀缓存复用"
    )

    # Scheduler configuration
    parser.add_argument(
        "--max-batch-size",
        type=int,
        default=8,
        help="Maximum batch size for processing requests",
    )

    parser.add_argument(
        "--max-num-tokens-per-batch",
        type=int,
        default=1024,
        help="Maximum number of tokens in a batch",
    )

    parser.add_argument(
        "--prefill-priority",
        type=int,
        default=0,
        choices=[0, 1],
        help="Priority for prefill requests (0 or 1)",
    )

    parser.add_argument(
        "--micro-batch-ratio", type=int, default=2, help="Micro batch ratio for scheduling"
    )

    parser.add_argument(
        "--scheduler-wait-ms", type=int, default=500, help="Scheduler wait time in milliseconds"
    )

    parser.add_argument(
        "--request-timeout-s",
        type=int,
        default=600,
        help="Per-request timeout in seconds before automatic abort",
    )

    # GPU/SGLang specialized configuration
    parser.add_argument(
        "--attention-backend",
        type=str,
        default="flashinfer",
        choices=["torch_native", "flashinfer", "triton", "fa3"],
        help="Choose the GPU attention kernels",
    )

    parser.add_argument(
        "--moe-runner-backend",
        type=str,
        default="auto",
        choices=[
            "auto",
            "triton",
            "triton_kernel",
            "flashinfer_trtllm",
            "flashinfer_cutlass",
            "flashinfer_mxfp4",
        ],
        help="Choose the GPU moe kernels",
    )

    # Tensor parallel configuration
    parser.add_argument("--tp-size", type=int, default=1, help="Tensor parallel size")

    parser.add_argument(
        "--nccl-port",
        type=int,
        default=None,
        help="The port for NCCL distributed environment setup",
    )

    # Logging and debugging
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    parser.add_argument(
        "--gpu-backend",
        type=str,
        default="sglang",
        choices=["sglang", "vllm"],
        help="GPU backend to use",
    )

    parser.add_argument(
        "--use-hfcache",
        action="store_true",
        default=False,
        help="Use local Hugging Face cache only (no network download)",
    )

    args = parser.parse_args()

    # Validate arguments
    validate_args(args)

    return args


def validate_args(args: argparse.Namespace) -> None:
    """
    Validate parsed arguments.

    Args:
        args: Parsed arguments namespace

    Raises:
        ValueError: If arguments are invalid
    """
    # Validate layer indices
    if args.start_layer is not None and args.start_layer < 0:
        raise ValueError("start_layer must be non-negative")

    if args.end_layer is not None and args.end_layer <= args.start_layer:
        raise ValueError("end_layer must be greater than start_layer")

    # Validate memory fraction
    if not 0.0 <= args.kv_cache_memory_fraction <= 1.0:
        raise ValueError("kv_cache_memory_fraction must be between 0.0 and 1.0")

    # Validate batch sizes
    if getattr(args, "max_batch_size", None) is not None and args.max_batch_size <= 0:
        raise ValueError("max_batch_size must be positive")

    max_seq_len = getattr(args, "max_sequence_length", None)
    if max_seq_len is not None and max_seq_len <= 0:
        raise ValueError("max_sequence_len must be positive")

    if max_seq_len is None and getattr(args, "max_batch_size", None) is None:
        raise ValueError("max_sequence_len or max_batch_size must be provided")

    if args.max_num_tokens_per_batch <= 0:
        raise ValueError("max_num_tokens_per_batch must be positive")

    if args.kv_block_size <= 0:
        raise ValueError("kv_block_size must be positive")

    if args.micro_batch_ratio <= 0:
        raise ValueError("micro_batch_ratio must be positive")

    if args.scheduler_wait_ms < 0:
        raise ValueError("scheduler_wait_ms must be non-negative")

    if getattr(args, "request_timeout_s", None) is not None and args.request_timeout_s <= 0:
        raise ValueError("request_timeout_s must be positive")

    # Validate supported dtypes
    dtype_list = [
        "float16",
        "bfloat16",
        "float32",
    ]
    if args.dtype not in dtype_list:
        raise ValueError(f"Unsupported dtype: {args.dtype}. Supported dtypes: {dtype_list}")
