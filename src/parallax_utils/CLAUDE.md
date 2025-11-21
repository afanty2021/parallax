# Parallax Utils 工具模块

[根目录](../../CLAUDE.md) > [src](../) > **parallax_utils**

## 变更记录 (Changelog)
- **2025-01-21**: 初始化模块文档，整理工具函数和动画资源

## 模块职责
Parallax Utils 工具模块提供通用工具和辅助功能，包括：
- 日志配置和管理
- 版本检查和更新提醒
- 文件操作和路径管理
- ASCII动画效果
- 请求指标收集
- 通用工具函数

## 入口与启动

### 模块结构
- `__init__.py` - 模块初始化
- `logging_config.py` - 日志系统配置
- `version_check.py` - 版本管理
- `file_util.py` - 文件操作工具
- `ascii_anime.py` - ASCII动画效果
- `request_metrics.py` - 请求指标收集
- `utils.py` - 通用工具函数

## 核心组件

### 1. 日志配置 (logging_config.py)

#### 功能特性
- 统一日志格式配置
- 多级别日志支持
- 控制台和文件输出
- 模块化日志获取

#### 接口使用
```python
from parallax_utils.logging_config import get_logger, set_log_level

# 获取模块专属日志器
logger = get_logger("parallax.cli")
logger.info("Parallax starting...")

# 设置全局日志级别
set_log_level("DEBUG")
```

#### 日志格式
```
[2025-01-21 10:30:45] [INFO] [parallax.cli] Parallax starting...
```

### 2. 版本检查 (version_check.py)

#### 功能特性
- 本地版本检测
- 远程版本查询
- 更新提醒机制
- 版本兼容性检查

#### 使用示例
```python
from parallax_utils.version_check import (
    get_current_version,
    check_latest_release,
    is_version_compatible
)

# 获取当前版本
current_version = get_current_version()

# 检查最新版本
check_latest_release()

# 版本兼容性检查
if is_version_compatible("0.1.0", "0.2.0"):
    logger.info("Version compatible")
```

### 3. 文件工具 (file_util.py)

#### 功能特性
- 项目根目录获取
- 配置文件路径解析
- 文件存在性检查
- 安全文件操作

#### 使用示例
```python
from parallax_utils.file_util import (
    get_project_root,
    get_config_path,
    ensure_directory_exists
)

# 获取项目根目录
root_dir = get_project_root()

# 获取配置文件路径
config_path = get_config_path("model_config.json")

# 确保目录存在
ensure_directory_exists("./logs")
```

### 4. ASCII动画 (ascii_anime.py)

#### 功能特性
- 启动动画效果
- 节点加入动画
- 彩色终端输出
- 动画配置选项

#### 动画资源
- `anime/parallax_run.json` - 运行时动画配置
- `anime/parallax_join.json` - 加入时动画配置

#### 使用示例
```python
from parallax_utils.ascii_anime import (
    display_parallax_run,
    display_parallax_join
)

# 显示启动动画
display_parallax_run()

# 显示加入动画
display_parallax_join()
```

### 5. 请求指标 (request_metrics.py)

#### 功能特性
- 请求延迟统计
- 吞吐量计算
- 错误率监控
- 指标聚合报告

#### 使用示例
```python
from parallax_utils.request_metrics import (
    record_request_latency,
    get_throughput_metrics,
    generate_metrics_report
)

# 记录请求延迟
record_request_latency("request_123", 1.23)

# 获取吞吐量指标
throughput = get_throughput_metrics()

# 生成指标报告
report = generate_metrics_report()
```

### 6. 通用工具 (utils.py)

#### 功能特性
- 字符串处理工具
- 时间格式化
- 数据转换函数
- 系统信息获取

#### 使用示例
```python
from parallax_utils.utils import (
    format_duration,
    safe_json_load,
    get_system_info
)

# 格式化时间长度
duration_str = format_duration(123.45)  # "2m 3s"

# 安全JSON加载
data = safe_json_load("config.json", {})

# 获取系统信息
sys_info = get_system_info()
```

## 动画资源详解

### 启动动画配置
**位置**: `anime/parallax_run.json`

```json
{
  "frames": [
    {
      "delay": 100,
      "text": "🚀 Starting Parallax..."
    },
    {
      "delay": 200,
      "text": "⚡ Initializing distributed engine..."
    },
    {
      "delay": 300,
      "text": "🌐 Connecting to P2P network..."
    }
  ],
  "colors": ["cyan", "green", "yellow"]
}
```

### 加入动画配置
**位置**: `anime/parallax_join.json`

```json
{
  "frames": [
    {
      "delay": 150,
      "text": "🔗 Joining Parallax cluster..."
    },
    {
      "delay": 200,
      "text": "📡 Establishing P2P connection..."
    }
  ]
}
```

## 日志系统架构

### 日志级别
- **DEBUG**: 详细调试信息
- **INFO**: 一般信息消息
- **WARNING**: 警告信息
- **ERROR**: 错误信息
- **CRITICAL**: 严重错误

### 日志配置
```python
LOGGING_CONFIG = {
    "format": "[{timestamp}] [{level}] [{module}] {message}",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "file_rotation": True,
    "max_file_size": "10MB",
    "backup_count": 5
}
```

### 模块化日志
每个模块获取独立的日志器实例：
```python
# CLI模块
cli_logger = get_logger("parallax.cli")

# 调度模块
scheduler_logger = get_logger("scheduling.scheduler")

# 执行器模块
executor_logger = get_logger("parallax.executor")
```

## 版本管理策略

### 版本格式
使用语义化版本控制 (SemVer): `MAJOR.MINOR.PATCH`

### 版本检查流程
1. **本地版本检测**: 读取当前安装版本
2. **远程版本查询**: 检查GitHub最新Release
3. **版本比较**: 使用语义化比较算法
4. **更新提醒**: 如有新版本则提示用户

### 兼容性策略
- **主版本**: 不兼容的API变更
- **次版本**: 向后兼容的功能性新增
- **修订版本**: 向后兼容的问题修正

## 性能监控

### 关键指标
1. **请求延迟 (Request Latency)**
   - 平均响应时间
   - P95/P99延迟
   - 延迟分布

2. **吞吐量 (Throughput)**
   - 每秒请求数 (RPS)
   - Token处理速度
   - 批处理效率

3. **资源使用 (Resource Usage)**
   - CPU利用率
   - 内存使用量
   - GPU利用率
   - 网络带宽

4. **错误率 (Error Rate)**
   - 请求失败率
   - 错误类型分布
   - 重试次数

### 指标收集
```python
class RequestMetrics:
    """请求指标收集器"""

    def __init__(self):
        self.latency_samples = []
        self.error_count = 0
        self.total_requests = 0

    def record_request(self, latency: float, success: bool = True):
        """记录请求指标"""
        self.latency_samples.append(latency)
        self.total_requests += 1
        if not success:
            self.error_count += 1

    def get_metrics(self) -> Dict[str, float]:
        """获取聚合指标"""
        return {
            "avg_latency": sum(self.latency_samples) / len(self.latency_samples),
            "error_rate": self.error_count / self.total_requests,
            "total_requests": self.total_requests
        }
```

## 测试与质量

### 当前测试状态
- **测试覆盖**: 0% (未发现测试文件)

### 建议测试覆盖
1. **日志配置测试**
   - 不同日志级别输出
   - 文件轮转机制
   - 模块化日志获取

2. **版本检查测试**
   - 版本比较逻辑
   - 网络请求异常处理
   - 缓存机制测试

3. **文件工具测试**
   - 路径解析正确性
   - 文件操作安全性
   - 边界条件处理

4. **指标收集测试**
   - 指标计算准确性
   - 内存使用优化
   - 并发安全性

## 常见问题 (FAQ)

### Q: 如何自定义日志格式？
A: 修改 `logging_config.py` 中的日志格式配置，或者使用标准库的 `logging.config.dictConfig` 进行更复杂的配置。

### Q: 如何禁用版本检查？
A: 设置环境变量 `PARALLAX_SKIP_VERSION_CHECK=1` 或者在代码中跳过版本检查调用。

### Q: 如何添加自定义动画？
A: 在 `anime/` 目录下添加新的JSON配置文件，并在 `ascii_anime.py` 中添加对应的显示函数。

### Q: 指标收集会影响性能吗？
A: 指标收集采用异步方式，对性能影响很小。如需要更高性能，可以采样收集部分指标。

## 配置选项

### 环境变量
- `PARALLAX_LOG_LEVEL`: 设置日志级别
- `PARALLAX_SKIP_VERSION_CHECK`: 跳过版本检查
- `PARALLAX_DISABLE_ANIMATION`: 禁用动画效果
- `PARALLAX_METRICS_SAMPLE_RATE`: 指标采样率 (0-1)

### 配置文件
```json
{
  "logging": {
    "level": "INFO",
    "file_path": "./logs/parallax.log",
    "max_size": "10MB",
    "backup_count": 5
  },
  "metrics": {
    "enabled": true,
    "sample_rate": 1.0,
    "export_interval": 60
  },
  "animation": {
    "enabled": true,
    "speed": 1.0
  }
}
```

## 相关文件清单

### 核心文件
- `__init__.py` - 模块初始化
- `logging_config.py` - 日志配置管理
- `version_check.py` - 版本检查和更新
- `file_util.py` - 文件操作工具
- `ascii_anime.py` - ASCII动画效果
- `request_metrics.py` - 请求指标收集
- `utils.py` - 通用工具函数

### 资源文件
- `anime/parallax_run.json` - 启动动画配置
- `anime/parallax_join.json` - 加入动画配置

---

*本文档由 AI 自动生成和更新，最后更新时间: 2025-01-21*