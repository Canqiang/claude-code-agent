# 通用 AI Agent 框架 🤖

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](../LICENSE)
[![Azure OpenAI](https://img.shields.io/badge/Azure-OpenAI-blue.svg)](https://azure.microsoft.com/zh-cn/products/ai-services/openai-service)
[![Framework](https://img.shields.io/badge/type-framework-orange.svg)]()

**语言:** [English](../README.md) | [中文](README.zh-CN.md)

一个受 Claude Code 启发的**通用 AI Agent 框架**。为任何领域构建自定义 Agent，具备**规划**、**思考**、**执行**和**评估**能力。

> **🎯 这是一个框架，不是特定的 Agent。** 您可以用它构建：
> - 代码审查 Agent
> - 数据分析 Agent
> - 客户支持 Agent
> - DevOps 自动化 Agent
> - 或任何您需要的专业化 Agent！

## ✨ 核心特性

- 🎯 **智能查询路由** - 智能分类查询，选择最优响应策略
- 🧠 **智能规划** - 自动任务分解与依赖管理
- 💭 **显式思考** - 透明的推理过程与反思能力
- ⚡ **稳健执行** - 基于工具的任务执行，集成 Azure OpenAI GPT
- 📊 **全面评估** - 多层次质量评估与学习
- 🔧 **可扩展工具** - 易于使用的自定义工具框架
- 💾 **记忆系统** - 上下文管理与长期学习
- 🤝 **多 Agent 协作** - 专业化 Agent 协同工作处理复杂任务
- 📡 **流式响应** - 通过 Server-Sent Events 实现实时进度更新
- 🌐 **Web UI 仪表板** - 任务执行和监控的交互式界面

## 🛠️ 内置工具

| 工具 | 描述 |
|------|------|
| 📄 `read_file` | 读取文件内容 |
| 📝 `write_file` | 写入文件内容 |
| 📁 `list_files` | 列出目录内容 |
| 🐍 `execute_python` | 安全执行 Python 代码 |
| 🌐 `fetch_web_content` | 获取和解析网页 |

## 📋 架构

```
+----------------------------------------------------------+
|                     通用 AI Agent                         |
+----------------------------------------------------------+
                          |
        +-----------------+-----------------+
        |                 |                 |
        v                 v                 v
  +----------+      +----------+      +------------+
  |   规划   |      |   思考   |      |    执行    |
  |   模块   | ---> |   模块   | ---> |    引擎    |
  +----------+      +----------+      +------------+
        |                 |                 |
        +-----------------+-----------------+
                          |
                          v
                  +-------------+
                  |    评估     |
                  |    模块     |
                  +-------------+
                          |
                          v
              +---------------------+
              |  工具注册表 &       |
              |      记忆           |
              +---------------------+
```

## 📖 文档

### 快速开始
- 📘 **[入门指南](GETTING_STARTED.md)** - 设置与第一步
- 💬 **[聊天指南](CHAT_GUIDE.md)** - 交互式聊天界面（CLI & Web）

### 框架定制
- 🎨 **[构建自定义 Agent](BUILDING_CUSTOM_AGENTS.md)** - 构建您自己的专业化 Agent
- 🎯 **[查询路由](QUERY_ROUTING.md)** - 基于 LLM 的查询分类
- 🏗️ **[架构文档](ARCHITECTURE.md)** - 系统设计与组件

### 使用与示例
- 📚 **[使用指南](USAGE_GUIDE.md)** - 模式与最佳实践
- 💡 **[基础示例](../examples/example_usage.py)** - 核心使用示例
- 🎨 **[自定义分类器示例](../examples/custom_classifier_example.py)** - 领域特定 Agent
- 🤝 **[多 Agent 示例](../examples/multi_agent_example.py)** - 协作示例
- 📡 **[流式响应示例](../examples/streaming_example.py)** - 实时流式处理

## 🚀 快速开始

### 安装

```bash
# 1. 克隆仓库
git clone <repository-url>
cd agent-test

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 Azure OpenAI（演示模式可选）
cp .env.example .env
# 编辑 .env 文件，填入你的 Azure OpenAI 凭证
```

### 💬 聊天界面（推荐）

#### 终端聊天
```bash
python chat.py
```

#### Web 聊天
```bash
python start_server.py
# 在浏览器中打开 http://localhost:8000
```

特性：
- 🗨️ **对话式界面** 类似 Claude Code
- 📊 **实时状态更新** 执行过程可视化
- 📜 **消息历史** 保持上下文
- ⚠️ **演示模式** 无需配置 Azure OpenAI 即可体验

### 📝 编程式使用

```python
from dotenv import load_dotenv
from src.agent import GeneralPurposeAgent

load_dotenv()

# 创建 Agent
agent = GeneralPurposeAgent(verbose=True)

# 执行任务
goal = "创建一个 Python 脚本，打印 'Hello, World!' 并保存为 hello.py"
evaluation = agent.run(goal)

# 检查结果
print(f"成功: {evaluation.overall_success}")
print(f"得分: {evaluation.overall_score:.2f}")
```


## 🎯 Agent 工作流程

Agent 遵循结构化的 4 阶段工作流程：

```
1️⃣ 规划阶段
   └─ 分析目标并分解为子任务
   └─ 识别依赖关系并制定策略

2️⃣ 思考阶段
   └─ 推理处理方法
   └─ 反思每个行动

3️⃣ 执行阶段
   └─ 按顺序执行子任务
   └─ 使用适当的工具
   └─ 处理错误并重新规划

4️⃣ 评估阶段
   └─ 评估每个步骤
   └─ 计算整体成功率
   └─ 提取经验教训
```

## 💡 使用示例

### 简单任务

```python
agent = GeneralPurposeAgent()
result = agent.quick_task("列出当前目录下的所有 Python 文件")
```

### 带规划的复杂任务

```python
goal = """
分析项目结构并创建报告：
1. 找到所有 Python 文件
2. 统计每个文件的代码行数
3. 识别主要模块
4. 将分析结果保存到 'project_analysis.txt'
"""

evaluation = agent.run(goal)
```

### 自定义工具

```python
from src.tools.base import Tool, ToolParameter

class MyCustomTool(Tool):
    @property
    def name(self) -> str:
        return "my_tool"

    @property
    def description(self) -> str:
        return "工具功能描述"

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="param",
                type="string",
                description="参数描述",
                required=True
            )
        ]

    def execute(self, **kwargs) -> Dict[str, Any]:
        # 你的实现
        return {"success": True, "result": "..."}

# 注册并使用
agent = GeneralPurposeAgent()
agent.register_tool(MyCustomTool())
```

### 多 Agent 协作

```python
from src.collaboration import AgentOrchestrator, PlannerAgent, ExecutorAgent, ReviewerAgent, AgentRole
from src.planning import PlanningModule
from src.execution import ExecutionEngine
from src.evaluation import EvaluationModule
from src.utils.llm_client import AzureOpenAIClient
from src.tools.base import ToolRegistry

# 创建组件
llm_client = AzureOpenAIClient()
tool_registry = ToolRegistry()

# 创建协调器
orchestrator = AgentOrchestrator(verbose=True)

# 创建并注册专业化 Agent
orchestrator.register_agent('planner', PlannerAgent(PlanningModule(llm_client)), AgentRole.PLANNER)
orchestrator.register_agent('executor', ExecutorAgent(ExecutionEngine(llm_client, tool_registry)), AgentRole.EXECUTOR)
orchestrator.register_agent('reviewer', ReviewerAgent(EvaluationModule(llm_client)), AgentRole.REVIEWER)

# 运行协作
goal = "创建一个带可视化的数据分析脚本"
result = orchestrator.collaborate(goal)
```

### 流式响应

```python
from src.streaming import StreamHandler, StreamEventType

# 创建流处理器
stream_handler = StreamHandler()

# 订阅事件
def on_event(event):
    print(f"[{event.type.value}] {event.data}")

stream_handler.subscribe(on_event)

# 使用流式执行
stream_handler.emit_start("计算统计数据")
stream_handler.emit_planning("分解任务...")
stream_handler.emit_execution("运行计算...")
stream_handler.emit_complete({"result": "完成", "success": True})

# 获取事件历史
for event in stream_handler.get_history():
    print(event.to_json())
```

### Web UI 仪表板

```bash
# 启动 Web 服务器
python -m uvicorn src.web_ui.app:app --host 0.0.0.0 --port 8000

# 或使用示例脚本
python examples/web_ui_example.py
```

访问仪表板：[http://localhost:8000](http://localhost:8000)

**可用端点：**
- `POST /api/run` - 执行任务
- `GET /api/stream/{goal}` - 使用 SSE 流式执行
- `GET /api/collaboration/run` - 多 Agent 协作
- `WS /ws` - WebSocket 实时更新

## ⚙️ 配置

通过 YAML 配置自定义 Agent 行为：

```yaml
agent:
  name: "MyAgent"
  max_iterations: 10
  thinking_enabled: true
  verbose: true

llm:
  temperature: 0.7
  max_tokens: 4096

planning:
  max_subtasks: 20
  allow_replanning: true

evaluation:
  step_evaluation: true
  final_evaluation: true
  success_threshold: 0.7
```

加载配置：

```python
agent = GeneralPurposeAgent(config_path="config.yaml")
```

## 🧪 测试

```bash
# 运行单元测试
python -m pytest tests/

# 或使用 unittest
python -m unittest discover tests/
```

## 📦 项目结构

```
agent-test/
├── src/                    # 核心源代码
│   ├── agent.py           # 主 Agent 类
│   ├── planning.py        # 规划模块
│   ├── thinking.py        # 思考模块
│   ├── execution.py       # 执行引擎
│   ├── evaluation.py      # 评估模块
│   ├── memory.py          # 记忆管理
│   ├── collaboration/     # 多 Agent 系统
│   │   ├── orchestrator.py
│   │   └── specialized_agents.py
│   ├── streaming/         # 流式响应
│   │   └── stream_handler.py
│   ├── web_ui/            # Web 仪表板
│   │   ├── app.py
│   │   ├── templates/
│   │   └── static/
│   ├── tools/             # 工具系统
│   │   ├── base.py
│   │   ├── file_ops.py
│   │   ├── code_exec.py
│   │   └── web_search.py
│   └── utils/             # 工具类
│       └── llm_client.py
├── docs/                   # 文档
│   ├── README.zh-CN.md
│   ├── GETTING_STARTED.md
│   ├── ARCHITECTURE.md
│   └── USAGE_GUIDE.md
├── examples/              # 使用示例
│   ├── example_usage.py
│   ├── multi_agent_example.py
│   ├── streaming_example.py
│   └── web_ui_example.py
├── tests/                 # 单元测试
├── config.yaml           # 配置文件
└── requirements.txt      # 依赖项
```

## 🔧 系统要求

- Python 3.8+
- Azure OpenAI API（支持 GPT-4）
- 详见 [requirements.txt](../requirements.txt) 的依赖项

## 🚧 路线图

- [x] **多 Agent 协作** - ✅ 已完成
- [x] **流式响应** - ✅ 已完成
- [x] **Web UI 仪表板** - ✅ 已完成
- [ ] 支持多种 LLM 提供商（OpenAI、Anthropic、本地模型）
- [ ] 异步工具执行
- [ ] 基于向量的语义搜索记忆
- [ ] 工具市场
- [ ] 高级上下文管理

## 🤝 贡献

欢迎贡献！请：

1. Fork 本仓库
2. 创建特性分支
3. 为新功能添加测试
4. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](../LICENSE) 文件。

## 🙏 致谢

- 受 [Claude Code](https://claude.com/claude-code) 和现代 AI Agent 架构启发
- 使用 Azure OpenAI GPT-4 构建
- 感谢开源 AI 社区

## 📞 支持

- 📚 查看[文档](./)
- 💡 尝试[示例](../examples/example_usage.py)
- 🐛 在 GitHub 上报告问题
- 📧 联系维护者

---

**使用 ❤️、Azure OpenAI 和 Python 构建**

[⬆ 返回顶部](#通用-ai-agent-)
