# 通用 AI Agent 🤖

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](../LICENSE)
[![Azure OpenAI](https://img.shields.io/badge/Azure-OpenAI-blue.svg)](https://azure.microsoft.com/zh-cn/products/ai-services/openai-service)

**语言:** [English](../README.md) | [中文](README.zh-CN.md)

一个受 Claude Code 启发的智能 AI Agent 系统，具备**规划**、**思考**、**执行**和**评估**能力，可自主处理复杂任务。

## ✨ 核心特性

- 🧠 **智能规划** - 自动任务分解与依赖管理
- 💭 **显式思考** - 透明的推理过程与反思能力
- ⚡ **稳健执行** - 基于工具的任务执行，集成 Azure OpenAI GPT
- 📊 **全面评估** - 多层次质量评估与学习
- 🔧 **可扩展工具** - 易于使用的自定义工具框架
- 💾 **记忆系统** - 上下文管理与长期学习

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

- 📘 **[入门指南](GETTING_STARTED.md)** - 设置与第一步
- 🏗️ **[架构文档](ARCHITECTURE.md)** - 系统设计与组件
- 📚 **[使用指南](USAGE_GUIDE.md)** - 模式与最佳实践
- 💡 **[示例代码](../examples/example_usage.py)** - 代码示例

## 🚀 快速开始

### 安装

```bash
# 1. 克隆仓库
git clone <repository-url>
cd agent-test

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 Azure OpenAI
cp .env.example .env
# 编辑 .env 文件，填入你的 Azure OpenAI 凭证

# 4. 运行快速入门
python quickstart.py
```

### 基本用法

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
│   ├── tools/             # 工具系统
│   │   ├── base.py
│   │   ├── file_ops.py
│   │   ├── code_exec.py
│   │   └── web_search.py
│   └── utils/             # 工具类
│       └── llm_client.py
├── docs/                   # 文档
│   ├── GETTING_STARTED.md
│   ├── ARCHITECTURE.md
│   └── USAGE_GUIDE.md
├── examples/              # 使用示例
├── tests/                 # 单元测试
├── config.yaml           # 配置文件
└── requirements.txt      # 依赖项
```

## 🔧 系统要求

- Python 3.8+
- Azure OpenAI API（支持 GPT-4）
- 详见 [requirements.txt](../requirements.txt) 的依赖项

## 🚧 路线图

- [ ] 支持多种 LLM 提供商（OpenAI、Anthropic、本地模型）
- [ ] 异步工具执行
- [ ] 基于向量的语义搜索记忆
- [ ] 多 Agent 协作
- [ ] Web UI 仪表板
- [ ] 工具市场
- [ ] 流式响应
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
