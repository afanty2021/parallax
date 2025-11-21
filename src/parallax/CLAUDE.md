# Parallax 核心模块

[根目录](../../CLAUDE.md) > [src](../) > **parallax**

## 变更记录 (Changelog)
- **2025-01-21**: 初始化模块文档，识别核心组件和接口

## 模块职责
Parallax 核心模块负责分布式AI推理引擎的核心功能，包括：
- 模型分片和分布式执行
- P2P网络通信和节点管理
- KV缓存管理和请求调度
- HTTP API服务和请求处理
- 多种LLM模型支持

## 入口与启动

### 主要入口点
- **CLI工具**: `cli.py` - 命令行接口，支持 `run` 和 `join` 命令
- **服务启动**: `launch.py` - 分布式推理服务器启动脚本

### 启动流程
1. 解析命令行参数和配置
2. 初始化P2P网络连接
3. 启动Executor进程（tp_rank=0在主进程，其他在子进程）
4. 启动HTTP服务器子进程
5. 启动P2P服务器线程

## 对外接口

### P2P通信接口
```python
# 关键类和方法 (src/p2p/server.py)
class ServerState:
    """P2P服务器状态管理"""

class Lattica:
    """Lattica P2P网络接口"""

@rpc_method
def forward_request(self, request: Request):
    """处理前向传播请求"""

@rpc_stream
def stream_request(self, request: Request):
    """流式请求处理"""
```

### HTTP API接口
```python
# 关键端点 (src/server/http_server.py)
POST /v1/chat/completions  # 聊天完成接口
POST /v1/completions       # 文本完成接口
GET  /v1/models           # 模型列表接口
POST /v1/stop_request     # 请求终止接口
```

### Executor执行器接口
```python
# 核心执行器 (src/server/executor.py)
class Executor:
    def __init__(self, args: argparse.Namespace):
        """初始化执行器"""

    def start(self):
        """启动执行器服务"""

    def handle_request(self, request: Request):
        """处理推理请求"""
```

## 关键依赖与配置

### 核心依赖
- **lattica**: P2P网络通信框架
- **mlx-lm**: Mac端MLX推理后端
- **sglang**: GPU端推理引擎
- **zmq**: 进程间通信
- **fastapi**: HTTP API服务框架

### 配置参数
```python
# 关键配置项 (src/server/server_args.py)
--model-path: 模型路径
--max-num-tokens-per-batch: 批处理最大token数
--max-batch-size: 最大批处理大小
--start-layer: 模型起始层
--end-layer: 模型结束层
--tp-pp-size: 张量并行和流水线并行大小
```

## 数据模型

### 请求模型
```python
# 请求定义 (src/server/request.py)
class Request:
    """推理请求基类"""
    request_id: str
    prompt: str
    sampling_params: SamplingParams

class InitialRequest(Request):
    """初始请求（prefill阶段）"""

class IntermediateRequest(Request):
    """中间请求（decode阶段）"""
```

### 采样参数
```python
# 采样配置 (src/server/sampling/sampling_params.py)
class SamplingParams:
    max_tokens: int
    temperature: float
    top_p: float
    presence_penalty: float
    frequency_penalty: float
```

## 支持的模型

### 已实现模型适配器
- **Qwen系列**: `models/qwen2.py`, `models/qwen3.py`, `models/qwen3_next.py`
- **DeepSeek系列**: `models/deepseek_v2.py`, `models/deepseek_v3.py`
- **Llama系列**: `models/llama.py`
- **GLM系列**: `models/glm4_moe.py`
- **MiniMax**: `models/minimax.py`
- **GPT-OSS**: `models/gpt_oss.py`

### 模型适配器接口
```python
# 统一模型接口 (以Llama为例)
class ParallaxLlamaAttention(MLXLlamaAttention):
    """自定义Llama注意力，支持显式KV缓存"""

    def __call__(self, x, mask=None, cache=None, offset=0):
        """返回(keys_rotated, values)用于外部KV缓存管理"""
```

## 核心组件详解

### 1. 执行器 (Executor)
**位置**: `src/server/executor.py`

**职责**:
- 管理模型分片加载
- 实例化调度器和KV缓存管理器
- 处理tokenization/detokenization
- 监听RPC请求并传递给调度器
- 执行模型前向传播

**关键方法**:
```python
def load_model_shard(self) -> ShardedModel:
    """加载模型分片"""

def process_prefill_batch(self, requests: List[InitialRequest]):
    """处理prefill批处理"""

def process_decode_batch(self, requests: List[IntermediateRequest]):
    """处理decode批处理"""
```

### 2. 调度器 (Scheduler)
**位置**: `src/server/scheduler.py`

**职责**:
- 管理请求队列和批次
- KV缓存分配和释放
- 连续批处理优化
- 请求优先级管理

**关键方法**:
```python
def add_request(self, request: Request):
    """添加新请求到调度队列"""

def schedule(self) -> BatchInfo:
    """生成下一个执行批次"""

def free_request(self, request_id: str):
    """释放请求资源"""
```

### 3. KV缓存管理器
**位置**: `src/server/kv_cache.py`, `src/server/radix_cache.py`

**职责**:
- 管理跨层的KV缓存
- Radix树前缀共享优化
- 缓存内存管理

### 4. HTTP服务器
**位置**: `src/server/http_server.py`

**职责**:
- 提供OpenAI兼容的API接口
- 处理流式响应
- 请求验证和格式转换

### 5. P2P服务器
**位置**: `src/p2p/server.py`

**职责**:
- 基于Lattica的节点发现和通信
- 请求转发和负载均衡
- 节点健康监控

## 模型后端支持

### SGLang后端
**位置**: `src/sglang/`

**特性**:
- GPU高性能推理
- 批处理优化
- 自定义内核支持

**关键文件**:
- `model_runner.py`: SGLang模型运行器适配
- `monkey_patch.py`: SGLang行为修改
- `monkey_patch_utils/`: 各种模型的特定补丁

### MLX后端
**位置**: `src/vllm/` (命名历史遗留)

**特性**:
- Apple Silicon优化
- 统一内存架构
- 低延迟推理

### VLLM后端
**位置**: `src/vllm/`

**特性**:
- 高吞吐量推理
- PagedAttention支持
- 分布式推理

## 通信协议

### P2P消息格式
```protobuf
// Protocol Buffers定义 (src/p2p/proto/forward_pb2.py)
message ForwardRequest {
  string request_id = 1;
  repeated int32 input_ids = 2;
  // ... 其他字段
}

message ForwardResponse {
  repeated int32 output_ids = 1;
  bool finished = 2;
  // ... 其他字段
}
```

### ZMQ通信
- 使用ZMQ进行进程间通信
- 支持REQ-REP和PUB-SUB模式
- 异步消息处理

## 工具函数

### 实用工具
**位置**: `src/utils/`

- `tokenizer_utils.py`: 分词器工具
- `utils.py`: 通用工具函数
- `selective_download.py`: 智能模型下载
- `weight_filter_utils.py`: 权重过滤工具

## 测试与质量

### 当前测试状态
- **测试覆盖**: 0% (未发现测试文件)
- **建议测试点**:
  - Executor请求处理流程
  - 调度器批次生成逻辑
  - KV缓存内存管理
  - P2P消息序列化/反序列化
  - HTTP API接口功能

### 质量工具
- **代码格式**: Black (line-length=100)
- **导入排序**: isort (profile=black)
- **代码检查**: Ruff

## 性能优化建议

### 内存优化
1. **KV缓存共享**: 使用Radix树减少重复计算
2. **批处理优化**: 动态批次大小调整
3. **权重加载**: 按需加载和释放模型权重

### 计算优化
1. **内核融合**: 自定义CUDA/MLX内核
2. **并行策略**: 张量并行 + 流水线并行
3. **缓存策略**: 多级缓存系统

### 网络优化
1. **压缩传输**: 模型权重和激活值压缩
2. **连接池**: 复用网络连接
3. **负载均衡**: 智能请求路由

## 常见问题 (FAQ)

### Q: 如何添加新的LLM模型支持？
A: 在 `src/parallax/models/` 目录下创建新的模型适配器，实现统一的注意力接口，确保支持显式KV缓存返回。

### Q: 如何调试分布式推理问题？
A: 检查各组件日志，重点关注：
- P2P网络连接状态
- 请求在各节点间的传递
- KV缓存分配和释放
- 模型分片加载情况

### Q: 如何优化推理延迟？
A: 可以通过以下方式：
- 减少批次大小降低延迟
- 优化KV缓存策略
- 调整并行度参数
- 使用更高效的模型后端

## 相关文件清单

### 核心文件
- `__init__.py` - 模块初始化
- `cli.py` - 命令行接口
- `launch.py` - 服务启动脚本
- `launch_chat.py` - 聊天服务启动

### 服务端文件
- `server/executor.py` - 执行器核心
- `server/http_server.py` - HTTP API服务
- `server/scheduler.py` - 请求调度器
- `server/kv_cache.py` - KV缓存管理
- `server/radix_cache.py` - Radix树缓存
- `server/model.py` - 模型封装
- `server/request.py` - 请求数据模型

### P2P通信
- `p2p/server.py` - P2P服务器
- `p2p/message_util.py` - 消息工具
- `p2p/utils.py` - P2P工具函数

### 模型支持
- `models/` - 各种LLM模型适配器
- `sglang/` - SGLang后端适配
- `vllm/` - VLLM后端适配

### 工具函数
- `utils/` - 通用工具函数

---

*本文档由 AI 自动生成和更新，最后更新时间: 2025-01-21*