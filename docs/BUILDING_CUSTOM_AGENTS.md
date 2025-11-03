# 构建自定义 Agent (Building Custom Agents)

本文档说明如何使用此框架构建您自己的专业化 Agent。

This document explains how to use this framework to build your own specialized agents.

---

## 🎯 框架理念 (Framework Philosophy)

这个项目是一个**通用的 Agent 架构框架**，而不是一个特定用途的 Agent。

This project is a **general-purpose agent architecture framework**, not a specific-use agent.

### 核心设计原则 (Core Design Principles)

1. **可扩展性 (Extensibility)** - 所有组件都可以定制
2. **LLM 驱动 (LLM-Driven)** - 决策由 LLM 做出，不是硬编码规则
3. **模块化 (Modularity)** - 可以单独使用或组合各个模块
4. **灵活性 (Flexibility)** - 适配任何领域的 Agent 需求

---

## 🏗️ 框架组件 (Framework Components)

```
General Purpose Agent Framework
├── Planning Module          # 任务规划
├── Thinking Module          # 推理思考
├── Execution Engine         # 任务执行
├── Evaluation Module        # 结果评估
├── Tool System             # 可扩展工具
├── Memory System           # 上下文管理
├── Query Classifier        # 查询路由（可自定义）
└── LLM Client             # LLM 接口
```

### 可定制的组件 (Customizable Components)

| 组件 Component | 定制方式 Customization | 用途 Use Case |
|----------------|----------------------|---------------|
| **QueryClassifier** | 自定义提示词 / 查询类型 | 领域特定的查询分类 |
| **Tool System** | 添加自定义工具 | 特定领域的操作能力 |
| **Planning** | 自定义规划策略 | 特定任务的规划逻辑 |
| **Evaluation** | 自定义评估标准 | 领域特定的质量标准 |

---

## 📝 示例：构建专业化 Agent (Example: Building Specialized Agents)

### 1. 代码审查 Agent (Code Review Agent)

一个专门用于代码审查的 Agent。

```python
from src.agent import GeneralPurposeAgent
from src.utils.query_classifier import QueryClassifier
from src.utils.llm_client import AzureOpenAIClient

# 自定义分类提示词
CODE_REVIEW_PROMPT = """You are a query classifier for a CODE REVIEW agent.
Classify queries into:
1. CODE_REVIEW_REQUEST - Full code review needed
2. SECURITY_CHECK - Security vulnerability analysis
3. PERFORMANCE_ANALYSIS - Performance optimization
4. SIMPLE_QUESTION - Quick programming question

User Query: "{query}"

Return JSON: {{"type": "...", "use_full_workflow": true/false}}"""

# 创建代码审查 Agent
class CodeReviewAgent:
    def __init__(self):
        self.llm_client = AzureOpenAIClient()
        self.classifier = QueryClassifier(
            llm_client=self.llm_client,
            custom_prompt=CODE_REVIEW_PROMPT
        )
        self.agent = GeneralPurposeAgent()

        # 添加代码审查专用工具
        # self.agent.register_tool(StaticAnalysisTool())
        # self.agent.register_tool(SecurityScannerTool())

    def review(self, code: str, query: str):
        """Review code based on query."""
        # 分类查询
        classification = self.classifier.classify(query)

        if classification['use_full_workflow']:
            # 完整的审查流程
            return self.agent.run(f"{query}\n\nCode:\n{code}")
        else:
            # 快速回答
            return self._quick_answer(query, code)

    def _quick_answer(self, query: str, code: str):
        """Quick answer for simple questions."""
        response = self.llm_client.chat_completion(
            messages=[
                {"role": "system", "content": "You are a code review expert."},
                {"role": "user", "content": f"{query}\n\nCode:\n{code}"}
            ]
        )
        return response['content']


# 使用
agent = CodeReviewAgent()
result = agent.review(
    code="def factorial(n): return 1 if n <= 1 else n * factorial(n-1)",
    query="Review this function for best practices"
)
```

### 2. 数据分析 Agent (Data Analysis Agent)

专门用于数据分析的 Agent。

```python
from src.agent import GeneralPurposeAgent
from src.utils.query_classifier import QueryClassifier
from src.tools.base import Tool, ToolParameter

# 自定义数据分析工具
class DataVisualizationTool(Tool):
    @property
    def name(self) -> str:
        return "visualize_data"

    @property
    def description(self) -> str:
        return "Create data visualizations"

    @property
    def parameters(self) -> list:
        return [
            ToolParameter(
                name="data_path",
                type="string",
                description="Path to data file",
                required=True
            ),
            ToolParameter(
                name="plot_type",
                type="string",
                description="Type of plot (histogram, scatter, etc.)",
                required=True
            )
        ]

    def execute(self, **kwargs):
        # 实现数据可视化逻辑
        pass


# 数据分析分类提示词
DATA_ANALYSIS_PROMPT = """Classify data analysis queries:
1. DATA_EXPLORATION - Quick data overview
2. STATISTICAL_ANALYSIS - Statistical tests
3. ML_MODELING - Machine learning tasks
4. DATA_CLEANING - Preprocessing

User Query: "{query}"
Return JSON: {{"type": "...", "use_full_workflow": true/false}}"""


class DataAnalysisAgent:
    def __init__(self):
        self.llm_client = AzureOpenAIClient()
        self.classifier = QueryClassifier(
            llm_client=self.llm_client,
            custom_prompt=DATA_ANALYSIS_PROMPT
        )
        self.agent = GeneralPurposeAgent()

        # 注册数据分析工具
        self.agent.register_tool(DataVisualizationTool())

    def analyze(self, data_path: str, query: str):
        """Analyze data based on query."""
        classification = self.classifier.classify(query)

        full_query = f"{query}\n\nData file: {data_path}"
        return self.agent.run(full_query)


# 使用
agent = DataAnalysisAgent()
result = agent.analyze(
    data_path="sales_data.csv",
    query="Analyze sales trends and create visualizations"
)
```

### 3. 客户支持 Agent (Customer Support Agent)

处理客户查询的 Agent。

```python
CUSTOMER_SUPPORT_PROMPT = """Classify customer support queries:
1. PRODUCT_QUESTION - Questions about products/features
2. TECHNICAL_ISSUE - Technical problems needing troubleshooting
3. BILLING_INQUIRY - Billing/payment related
4. GENERAL_INQUIRY - General questions

User Query: "{query}"
Return JSON: {{"type": "...", "use_full_workflow": true/false}}"""


class CustomerSupportAgent:
    def __init__(self, knowledge_base: dict):
        self.llm_client = AzureOpenAIClient()
        self.classifier = QueryClassifier(
            llm_client=self.llm_client,
            custom_prompt=CUSTOMER_SUPPORT_PROMPT
        )
        self.agent = GeneralPurposeAgent()
        self.knowledge_base = knowledge_base

    def handle_query(self, customer_query: str):
        """Handle customer query."""
        classification = self.classifier.classify(customer_query)

        if classification['type'].value == 'PRODUCT_QUESTION':
            # 快速查询知识库
            return self._search_knowledge_base(customer_query)
        elif classification['use_full_workflow']:
            # 复杂问题需要完整流程
            return self.agent.run(customer_query)
        else:
            # 简单回答
            return self._quick_response(customer_query)

    def _search_knowledge_base(self, query: str):
        """Search knowledge base for quick answers."""
        # 实现知识库搜索
        pass

    def _quick_response(self, query: str):
        """Generate quick response."""
        pass


# 使用
agent = CustomerSupportAgent(knowledge_base={
    "products": [...],
    "faqs": [...]
})
result = agent.handle_query("How do I reset my password?")
```

---

## 🔧 自定义组件指南 (Component Customization Guide)

### 1. 自定义查询分类 (Custom Query Classification)

```python
from src.utils.query_classifier import QueryClassifier

# 方式 1: 使用自定义提示词
custom_prompt = """Your custom classification logic here...
Query: "{query}"
Return JSON: {{"type": "...", "use_full_workflow": true/false}}"""

classifier = QueryClassifier(
    llm_client=llm_client,
    custom_prompt=custom_prompt
)

# 方式 2: 扩展 QueryType
from src.utils.query_classifier import QueryType
from enum import Enum

class MyQueryType(Enum):
    MY_CUSTOM_TYPE_1 = "custom_1"
    MY_CUSTOM_TYPE_2 = "custom_2"
    # 添加更多类型...
```

### 2. 自定义工具 (Custom Tools)

```python
from src.tools.base import Tool, ToolParameter
from typing import List, Dict, Any

class MyCustomTool(Tool):
    @property
    def name(self) -> str:
        return "my_custom_tool"

    @property
    def description(self) -> str:
        return "Tool description for LLM"

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="param1",
                type="string",
                description="Parameter description",
                required=True
            )
        ]

    def execute(self, **kwargs) -> Dict[str, Any]:
        # 实现工具逻辑
        param1 = kwargs.get('param1')

        # 执行操作...
        result = self._do_something(param1)

        return {
            "success": True,
            "result": result
        }

    def _do_something(self, param):
        # 具体实现
        pass


# 注册工具
agent = GeneralPurposeAgent()
agent.register_tool(MyCustomTool())
```

### 3. 自定义规划策略 (Custom Planning)

```python
from src.planning import PlanningModule

class MyPlanningModule(PlanningModule):
    def plan(self, goal: str, context: str = None):
        """Custom planning logic."""
        # 调用 LLM 生成计划
        custom_prompt = f"""Custom planning prompt for: {goal}
        Your domain-specific planning logic here..."""

        response = self.llm_client.chat_completion(
            messages=[{"role": "user", "content": custom_prompt}]
        )

        # 解析并返回计划
        return self._parse_plan(response)


# 使用自定义规划
agent = GeneralPurposeAgent(planning_module=MyPlanningModule(llm_client))
```

### 4. 自定义评估标准 (Custom Evaluation)

```python
from src.evaluation import EvaluationModule, Evaluation

class MyEvaluationModule(EvaluationModule):
    def evaluate_execution(self, goal: str, result: dict) -> Evaluation:
        """Custom evaluation logic."""
        # 领域特定的评估标准
        quality_score = self._calculate_quality(result)
        completeness_score = self._check_completeness(result, goal)

        overall_score = (quality_score + completeness_score) / 2

        return Evaluation(
            overall_success=overall_score >= 0.7,
            overall_score=overall_score,
            summary=f"Custom evaluation: {overall_score:.2f}",
            strengths=self._identify_strengths(result),
            weaknesses=self._identify_weaknesses(result)
        )


# 使用自定义评估
agent = GeneralPurposeAgent(evaluation_module=MyEvaluationModule(llm_client))
```

---

## 🚀 快速开始模板 (Quick Start Template)

```python
#!/usr/bin/env python3
"""
My Custom Agent

Description: [Describe your agent's purpose]
"""

from dotenv import load_dotenv
from src.agent import GeneralPurposeAgent
from src.utils.query_classifier import QueryClassifier
from src.utils.llm_client import AzureOpenAIClient
from src.tools.base import Tool, ToolParameter

load_dotenv()


# 1. 定义自定义分类提示词
MY_CLASSIFICATION_PROMPT = """
[Your custom classification logic]

User Query: "{query}"
Return JSON: {{"type": "...", "use_full_workflow": true/false}}
"""


# 2. 定义自定义工具（如需要）
class MyTool(Tool):
    @property
    def name(self) -> str:
        return "my_tool"

    @property
    def description(self) -> str:
        return "Tool description"

    @property
    def parameters(self) -> list:
        return []

    def execute(self, **kwargs):
        # 实现工具逻辑
        return {"success": True, "result": "..."}


# 3. 创建您的 Agent 类
class MyCustomAgent:
    def __init__(self):
        self.llm_client = AzureOpenAIClient()

        # 初始化分类器
        self.classifier = QueryClassifier(
            llm_client=self.llm_client,
            custom_prompt=MY_CLASSIFICATION_PROMPT
        )

        # 初始化基础 Agent
        self.agent = GeneralPurposeAgent()

        # 注册自定义工具
        self.agent.register_tool(MyTool())

    def process(self, user_query: str):
        """Process user query."""
        # 分类
        classification = self.classifier.classify(user_query)

        # 根据分类决定处理方式
        if classification['use_full_workflow']:
            return self.agent.run(user_query)
        else:
            return self._quick_response(user_query)

    def _quick_response(self, query: str):
        """Quick response for simple queries."""
        # 实现快速响应逻辑
        pass


# 4. 使用您的 Agent
if __name__ == "__main__":
    agent = MyCustomAgent()
    result = agent.process("Your query here")
    print(result)
```

---

## 📚 更多资源 (More Resources)

- **[Query Routing Guide](QUERY_ROUTING.md)** - 查询路由详细说明
- **[Tool Development](../examples/custom_classifier_example.py)** - 工具开发示例
- **[Architecture](ARCHITECTURE.md)** - 系统架构说明
- **[Examples Directory](../examples/)** - 完整示例代码

---

## 💡 最佳实践 (Best Practices)

### 1. LLM 驱动的决策 (LLM-Driven Decisions)

✅ **推荐 (Recommended)**:
```python
# 让 LLM 做决策
classification = classifier.classify(query)
```

❌ **不推荐 (Not Recommended)**:
```python
# 硬编码规则
if "create" in query or "build" in query:
    use_full_workflow = True
```

### 2. 保持通用性 (Keep It Generic)

- 框架应该是通用的
- 领域特定逻辑放在自定义组件中
- 使用配置和提示词而不是硬编码

### 3. 可扩展性 (Extensibility)

- 使用继承扩展基础类
- 通过组合添加新功能
- 保持接口一致

### 4. 文档化 (Documentation)

- 为自定义 Agent 编写清晰的文档
- 提供使用示例
- 说明定制点和扩展方式

---

## 🎓 学习路径 (Learning Path)

1. **理解框架** - 阅读架构文档，运行基础示例
2. **尝试定制** - 修改分类提示词，添加简单工具
3. **构建 Agent** - 创建您自己的专业化 Agent
4. **分享经验** - 贡献您的 Agent 示例回社区

---

## 🤝 贡献您的 Agent (Contributing Your Agent)

如果您构建了有趣的专业化 Agent，欢迎：

1. 在 `examples/` 目录添加示例
2. 编写文档说明用途和用法
3. 提交 Pull Request 分享给社区

---

**记住：这是一个框架，不是一个特定的 Agent。发挥创意，构建您需要的 Agent！**

**Remember: This is a framework, not a specific agent. Be creative and build the agent you need!**
