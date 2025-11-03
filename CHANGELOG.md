# 更新日志 (Changelog)

## 2025-10-31 - v2.0.0 重大更新：LLM 驱动的智能分类 🎯

### 🎯 核心理念变更 (Core Philosophy Change)

**之前 (Before)**: 特定用途的 Agent 系统
**现在 (Now)**: **通用 Agent 框架** - 可用于构建任何领域的专业化 Agent

### ✨ 主要更新 (Major Updates)

#### 1. LLM 驱动的查询分类 (LLM-Driven Query Classification)

**变更内容**:
- ❌ 移除硬编码的正则表达式规则
- ✅ 使用 LLM 进行智能查询分类
- ✅ 支持自定义分类提示词

**原因**:
> "我希望是交给 llm 判断而不是代码。我希望这个项目是一个通用的 Agent 架构，用户可以用这个框架来做各种 Agent"
> - 用户反馈

**优势**:
- 更智能和灵活的分类
- 支持任何语言的查询
- 可为不同领域定制
- 无需维护复杂的规则

#### 2. 框架化设计 (Framework Design)

**新增组件**:
- `QueryClassifier` - 可定制的 LLM 查询分类器
- 自定义分类提示词支持
- Fallback 机制（无 LLM 时）

**文件结构**:
```
src/utils/query_classifier.py          # LLM 驱动的分类器
examples/custom_classifier_example.py  # 5个自定义示例
docs/BUILDING_CUSTOM_AGENTS.md        # 构建指南
```

#### 3. 新增文档 (New Documentation)

- 📚 **[构建自定义 Agent](docs/BUILDING_CUSTOM_AGENTS.md)** - 完整的自定义指南
- 🎯 **[查询路由](docs/QUERY_ROUTING.md)** - 智能路由详解
- 💡 **[自定义分类器示例](examples/custom_classifier_example.py)** - 5个实用示例

### 📝 代码示例 (Code Examples)

#### 示例 1: 使用默认分类器

```python
from src.utils.query_classifier import QueryClassifier
from src.utils.llm_client import AzureOpenAIClient

llm_client = AzureOpenAIClient()
classifier = QueryClassifier(llm_client=llm_client)

classification = classifier.classify("Create a web application")
# LLM 智能判断: COMPLEX_TASK, use_full_workflow=True
```

#### 示例 2: 代码审查 Agent

```python
CODE_REVIEW_PROMPT = """Classify code review queries into:
- CODE_REVIEW_REQUEST
- SECURITY_CHECK
- PERFORMANCE_ANALYSIS
- SIMPLE_QUESTION
"""

classifier = QueryClassifier(
    llm_client=llm_client,
    custom_prompt=CODE_REVIEW_PROMPT
)

# 现在分类器专门用于代码审查
classification = classifier.classify("Check for security vulnerabilities")
```

#### 示例 3: 数据分析 Agent

```python
DATA_ANALYSIS_PROMPT = """Classify data analysis queries into:
- DATA_EXPLORATION
- STATISTICAL_ANALYSIS
- ML_MODELING
- DATA_CLEANING
"""

classifier = QueryClassifier(
    llm_client=llm_client,
    custom_prompt=DATA_ANALYSIS_PROMPT
)
```

### 🔧 技术改进 (Technical Improvements)

#### 查询分类器 (QueryClassifier)

**之前 (Before)**:
```python
# 硬编码规则
GREETING_PATTERNS = [r'^(hi|hello|hey)', ...]
if re.search(pattern, query):
    return QueryType.GREETING
```

**现在 (Now)**:
```python
# LLM 智能判断
response = self.llm_client.chat_completion(
    messages=[{"role": "user", "content": prompt}],
    temperature=0.1
)
classification = json.loads(response['content'])
```

**优势**:
- ✅ 智能理解用户意图
- ✅ 支持任何语言
- ✅ 可处理复杂/模糊查询
- ✅ 可为不同领域定制

#### 集成点更新 (Integration Updates)

**Web API** (`src/web_ui/app.py`):
```python
# 使用 LLM 进行分类
llm_client = AzureOpenAIClient() if is_configured else None
classifier = QueryClassifier(llm_client=llm_client)
classification = classifier.classify(goal)
```

**Terminal Chat** (`chat.py`):
```python
# 使用 LLM 进行分类
llm_client = AzureOpenAIClient() if self.is_configured else None
classifier = QueryClassifier(llm_client=llm_client)
classification = classifier.classify(user_input)
```

### 📚 新增示例 (New Examples)

#### 1. 默认通用分类器
```bash
python examples/custom_classifier_example.py
# 运行 example_1_default_classifier()
```

#### 2. 代码审查 Agent
- 分类: CODE_REVIEW_REQUEST, SECURITY_CHECK, PERFORMANCE_ANALYSIS
- 用途: 代码审查、安全检查、性能分析

#### 3. 数据分析 Agent
- 分类: DATA_EXPLORATION, STATISTICAL_ANALYSIS, ML_MODELING
- 用途: 数据探索、统计分析、机器学习

#### 4. 客户支持 Agent
- 分类: PRODUCT_QUESTION, TECHNICAL_ISSUE, BILLING_INQUIRY
- 用途: 客户服务、技术支持

#### 5. 多语言支持
- 支持中文、英文、西班牙文等
- LLM 自动理解不同语言

### 🚀 性能与可靠性 (Performance & Reliability)

#### Fallback 机制
当 LLM 不可用时:
```python
def _fallback_classification(self, query: str):
    # 简单启发式规则
    if 'hello' in query.lower() and len(query.split()) <= 3:
        return QueryType.GREETING
    # 默认: 安全起见使用完整流程
    return QueryType.COMPLEX_TASK
```

#### 性能优化
- LLM 调用使用 `temperature=0.1` 确保一致性
- 简单问候使用 fallback，避免 LLM 调用
- 缓存机制可在未来添加

### 📖 更新的文档 (Updated Documentation)

#### README 更新
- ✅ 标题改为 "General Purpose Agent **Framework**"
- ✅ 强调这是框架而非特定 Agent
- ✅ 添加框架徽章
- ✅ 提供定制示例
- ✅ 重组文档结构

#### 新增指南
1. **[BUILDING_CUSTOM_AGENTS.md](docs/BUILDING_CUSTOM_AGENTS.md)**
   - 框架理念
   - 自定义组件指南
   - 5个完整示例
   - 快速开始模板
   - 最佳实践

2. **[QUERY_ROUTING.md](docs/QUERY_ROUTING.md)**
   - 查询分类详解
   - 工作流程图
   - 配置选项
   - 调试和监控

### 🎯 框架核心理念 (Framework Core Philosophy)

```
┌─────────────────────────────────────────────────────┐
│         General Purpose Agent Framework            │
│                                                     │
│  "A framework for building ANY agent you need"     │
│                                                     │
│  ✓ Customize query classification                 │
│  ✓ Add domain-specific tools                      │
│  ✓ Define custom planning strategies              │
│  ✓ Implement specialized evaluation               │
│  ✓ Build for ANY domain                           │
└─────────────────────────────────────────────────────┘
```

### ⚠️ 破坏性变更 (Breaking Changes)

#### QueryClassifier API 变更

**之前 (v1.x)**:
```python
classifier = QueryClassifier()  # 内部使用正则表达式
```

**现在 (v2.0)**:
```python
# 需要传入 LLM client 以使用 LLM 分类
classifier = QueryClassifier(llm_client=llm_client)

# 或使用 fallback（无 LLM）
classifier = QueryClassifier(llm_client=None)
```

#### 自定义提示词支持

**新增**:
```python
classifier = QueryClassifier(
    llm_client=llm_client,
    custom_prompt=YOUR_CUSTOM_PROMPT
)
```

### 🔄 迁移指南 (Migration Guide)

如果您使用了旧版本的 `QueryClassifier`:

```python
# v1.x
from src.utils.query_classifier import QueryClassifier
classifier = QueryClassifier()

# v2.0
from src.utils.query_classifier import QueryClassifier
from src.utils.llm_client import AzureOpenAIClient

llm_client = AzureOpenAIClient()
classifier = QueryClassifier(llm_client=llm_client)

# 或使用 fallback
classifier = QueryClassifier(llm_client=None)
```

### 🐛 Bug 修复 (Bug Fixes)

#### 1. Web 聊天流式响应错误
**问题**: `emit_execution()` 缺少必需的 `progress` 参数
**修复**:
- `src/web_ui/app.py:202` - 添加 progress=50
- `src/web_ui/app.py:246` - 添加 progress=60

#### 2. 依赖项缺失
**问题**: 服务器启动时缺少 fastapi/uvicorn
**修复**: 添加安装步骤和错误处理

### 📊 影响范围 (Impact Scope)

**影响的文件**:
- ✅ `src/utils/query_classifier.py` - 完全重写
- ✅ `src/web_ui/app.py` - 更新以使用 LLM 分类
- ✅ `chat.py` - 更新以使用 LLM 分类
- ✅ `README.md` - 重点强调框架特性
- ✅ `docs/README.zh-CN.md` - 同步更新
- ✅ 新增多个文档和示例

**向后兼容性**:
- ⚠️ `QueryClassifier` API 有破坏性变更
- ✅ 其他组件保持兼容
- ✅ 提供 fallback 机制

### 🎉 总结 (Summary)

这个更新将项目从一个**特定的 Agent 系统**转变为一个**通用的 Agent 框架**。

**核心变化**:
1. LLM 驱动的决策，而非硬编码规则
2. 完全可定制的组件
3. 为任何领域构建 Agent
4. 完整的文档和示例

**现在您可以**:
- ✅ 构建代码审查 Agent
- ✅ 构建数据分析 Agent
- ✅ 构建客户支持 Agent
- ✅ 构建任何您需要的 Agent！

---

**相关文档**:
- [Building Custom Agents](docs/BUILDING_CUSTOM_AGENTS.md)
- [Query Routing Guide](docs/QUERY_ROUTING.md)
- [Custom Classifier Examples](examples/custom_classifier_example.py)

---

**用户反馈驱动的改进** ❤️

> "我希望是交给 llm 判断而不是代码。我希望这个项目是一个通用的 Agent 架构，用户可以用这个框架来做各种 Agent"

感谢用户的宝贵反馈，推动了这次重要的架构改进！
