# Scheduling 调度模块

[根目录](../../CLAUDE.md) > [src](../) > **scheduling**

## 变更记录 (Changelog)
- **2025-01-21**: 初始化模块文档，分析调度算法和路由策略

## 模块职责
Scheduling 调度模块负责分布式AI推理的智能调度，包括：
- 模型层分配策略 (Layer Allocation)
- 请求路由优化 (Request Routing)
- 节点资源管理和负载均衡
- 动态调度算法实现

## 入口与启动

### 主要组件
- **调度器**: `scheduler.py` - 统一调度协调器
- **层分配**: `layer_allocation.py` - 模型层分割策略
- **请求路由**: `request_routing.py` - 智能路由算法
- **节点管理**: `node.py` - 节点状态和资源
- **模型信息**: `model_info.py` - 模型架构数据

## 核心算法

### 1. 层分配算法 (Layer Allocation)

#### 贪心算法 (GreedyLayerAllocator)
**位置**: `layer_allocation.py`

**原理**:
- 按节点性能从高到低排序
- 优先分配层到性能最好的节点
- 简单高效，适用于均匀场景

**核心逻辑**:
```python
def allocate_layers(self, nodes: List[Node], model_info: ModelInfo):
    """贪心层分配算法"""
    sorted_nodes = sorted(nodes, key=lambda n: n.compute_capability, reverse=True)
    # 按性能顺序分配层
```

#### 动态规划算法 (DynamicProgrammingLayerAllocator)
**位置**: `layer_allocation.py`

**原理**:
- 考虑层间依赖关系
- 最小化总体推理延迟
- 计算最优层分配方案

**核心逻辑**:
```python
def allocate_layers_dp(self, nodes: List[Node], model_info: ModelInfo):
    """动态规划层分配"""
    # DP状态: dp[i][j] = 前i层分配给前j个节点的最小时间
    # 转移: 考虑每个节点分配连续的层
```

### 2. 请求路由算法 (Request Routing)

#### 轮询路由 (RoundRobinPipelineRouting)
**位置**: `request_routing.py`

**原理**:
- 按顺序轮询分配请求
- 简单负载均衡
- 适用于同质节点

#### 动态规划路由 (DynamicProgrammingRouting)
**位置**: `request_routing.py`

**原理**:
- 基于实时负载状态
- 考虑网络延迟和计算延迟
- 最小化端到端延迟

## 对外接口

### 调度器接口
```python
class Scheduler:
    """统一调度协调器"""

    def __init__(self, model_info: ModelInfo, nodes: List[Node],
                 strategy: str = "dp", routing_strategy: str = "rr"):
        """初始化调度器"""

    def add_node(self, node: Node):
        """添加新节点到集群"""

    def remove_node(self, node_id: str):
        """从集群移除节点"""

    def schedule_request(self, request: Request):
        """调度新请求到合适节点"""

    def rebalance(self):
        """负载重平衡"""
```

### 节点管理接口
```python
class Node:
    """分布式节点抽象"""

    def __init__(self, node_id: str, compute_capability: float):
        """初始化节点"""

    def get_current_load(self) -> float:
        """获取当前负载"""

    def can_handle_request(self, request: Request) -> bool:
        """判断是否能处理请求"""

    def get_latency_estimate(self, request: Request) -> float:
        """估算处理延迟"""
```

## 数据模型

### 模型信息
**位置**: `model_info.py`

```python
class ModelInfo:
    """模型架构信息"""

    model_name: str
    num_layers: int
    hidden_size: int
    num_attention_heads: int
    intermediate_size: int
    max_position_embeddings: int
    layer_memory_requirement: List[int]  # 每层内存需求
    layer_compute_cost: List[float]      # 每层计算开销
```

### 请求信号
**位置**: `node.py`

```python
class RequestSignal:
    """请求传输信号"""

    request_id: str
    source_node: str
    target_node: str
    layer_range: Tuple[int, int]
    input_data: Any
    priority: int
```

## 调度策略

### 策略配置
```python
# 调度器配置选项
scheduler_config = {
    "allocation_strategy": "dp",      # "greedy" 或 "dp"
    "routing_strategy": "rr",         # "rr" 或 "dp"
    "rebalance_threshold": 0.8,       # 重平衡阈值
    "heartbeat_timeout": 60.0,        # 心跳超时时间
    "request_arrival_horizon": 600.0, # 请求到达预测窗口
}
```

### 重平衡机制
1. **负载监控**: 持续监控各节点负载
2. **阈值检测**: 负载超过阈值时触发重平衡
3. **迁移决策**: 选择最优迁移方案
4. **状态转移**: 平滑迁移进行中请求

## 性能优化

### 层分配优化
- **计算均衡**: 考虑各节点计算能力差异
- **内存限制**: 尊重节点内存约束
- **网络延迟**: 考虑节点间通信开销
- **热点避免**: 防止某些节点过载

### 路由优化
- **延迟感知**: 基于实时延迟估算
- **带宽考虑**: 考虑网络带宽限制
- **拥塞控制**: 避免网络拥塞
- **优先级队列**: 支持请求优先级

## 关键算法详解

### 动态规划层分配
```python
def dynamic_programming_allocation(nodes, model_info):
    """动态规划求解最优层分配"""

    # DP表初始化
    num_layers = model_info.num_layers
    num_nodes = len(nodes)
    dp = [[float('inf')] * (num_nodes + 1) for _ in range(num_layers + 1)]

    # 状态转移
    for i in range(1, num_layers + 1):
        for j in range(1, num_nodes + 1):
            for k in range(1, i + 1):
                # 计算将层[k..i]分配给节点j的成本
                cost = compute_layer_cost(k, i, nodes[j-1])
                dp[i][j] = min(dp[i][j], dp[k-1][j-1] + cost)

    # 回溯最优分配方案
    return backtrack_optimal_allocation(dp)
```

### 动态规划路由
```python
def dynamic_programming_routing(request, nodes):
    """基于动态规划的最优路径选择"""

    # 考虑因素
    # 1. 当前节点负载
    # 2. 网络传输延迟
    # 3. 计算处理延迟
    # 4. 队列等待时间

    # DP状态: dp[i][j] = 请求到节点i，经过j跳的最小延迟
    # 目标: 找到从源到目标的最小延迟路径

    min_latency = float('inf')
    optimal_path = []

    # 枚举所有可能的路径，计算端到端延迟
    for path in generate_all_paths(request.source, request.target):
        total_latency = compute_path_latency(path, request)
        if total_latency < min_latency:
            min_latency = total_latency
            optimal_path = path

    return optimal_path
```

## 监控指标

### 关键性能指标 (KPI)
- **请求延迟**: 端到端请求处理时间
- **吞吐量**: 每秒处理的请求数
- **资源利用率**: CPU/GPU/内存使用率
- **负载均衡度**: 节点间负载差异
- **网络效率**: 网络带宽利用率

### 监控实现
```python
class MetricsCollector:
    """性能指标收集器"""

    def collect_request_latency(self, request_id: str, latency: float):
        """收集请求延迟"""

    def collect_throughput(self, node_id: str, throughput: float):
        """收集吞吐量数据"""

    def collect_resource_usage(self, node_id: str, usage: Dict[str, float]):
        """收集资源使用情况"""

    def generate_report(self) -> Dict[str, Any]:
        """生成性能报告"""
```

## 测试与质量

### 当前测试状态
- **测试覆盖**: 0% (未发现测试文件)

### 建议测试场景
1. **层分配算法测试**
   - 贪心vs动态规划性能对比
   - 不同模型架构的分配效果
   - 异构节点环境下的分配策略

2. **路由算法测试**
   - 轮询vs动态规划路由效果
   - 网络拥塞场景下的路由表现
   - 大规模请求并发处理

3. **重平衡机制测试**
   - 节点动态加入/离开
   - 负载重平衡的平滑性
   - 重平衡过程中的请求处理

4. **集成测试**
   - 与实际推理引擎集成
   - 多节点协调测试
   - 故障恢复测试

## 常见问题 (FAQ)

### Q: 如何选择合适的分配策略？
A:
- **贪心策略**: 适用于节点性能差异小、模型层数少的场景
- **动态规划**: 适用于复杂模型、异构节点、对性能要求高的场景

### Q: 如何处理节点故障？
A: 调度器会检测节点心跳超时，自动将故障节点从集群中移除，并重新分配其处理中的请求到其他健康节点。

### Q: 如何优化调度延迟？
A:
1. 使用缓存避免重复计算
2. 并行化调度决策过程
3. 简化算法复杂度
4. 预计算常用分配方案

## 相关文件清单

### 核心文件
- `__init__.py` - 模块初始化
- `scheduler.py` - 统一调度协调器
- `layer_allocation.py` - 层分配算法
- `request_routing.py` - 请求路由算法
- `node.py` - 节点抽象和管理
- `model_info.py` - 模型架构信息

---

*本文档由 AI 自动生成和更新，最后更新时间: 2025-01-21*