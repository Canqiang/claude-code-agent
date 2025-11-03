# General Purpose Agent Framework 🤖

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Azure OpenAI](https://img.shields.io/badge/Azure-OpenAI-blue.svg)](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
[![Framework](https://img.shields.io/badge/type-framework-orange.svg)]()

**Language:** [English](README.md) | [中文](docs/README.zh-CN.md)

A **general-purpose AI agent framework** inspired by Claude Code. Build custom agents for any domain with **Planning**, **Thinking**, **Execution**, and **Evaluation** capabilities.

> **🎯 This is a framework, not a specific agent.** Customize it to build:
> - Code review agents
> - Data analysis agents
> - Customer support agents
> - DevOps automation agents
> - Or any specialized agent you need!

## ✨ Key Features

- 🎯 **Intelligent Query Routing** - Smart classification of queries for optimal response strategy
- 🧠 **Intelligent Planning** - Automatic task decomposition with dependency management
- 💭 **Explicit Thinking** - Transparent reasoning process with reflection capabilities
- ⚡ **Robust Execution** - Tool-based task execution with Azure OpenAI GPT
- 📊 **Comprehensive Evaluation** - Multi-level quality assessment and learning
- 🔧 **Extensible Tools** - Easy-to-use framework for custom tool creation
- 💾 **Memory System** - Context management and long-term learning
- 🤝 **Multi-Agent Collaboration** - Specialized agents working together for complex tasks
- 📡 **Streaming Responses** - Real-time progress updates with Server-Sent Events
- 🌐 **Web UI Dashboard** - Interactive interface for task execution and monitoring

## 🛠️ Built-in Tools

| Tool | Description |
|------|-------------|
| 📄 `read_file` | Read file contents |
| 📝 `write_file` | Write content to files |
| 📁 `list_files` | List directory contents |
| 🐍 `execute_python` | Execute Python code safely |
| 🌐 `fetch_web_content` | Fetch and parse web pages |

## Architecture

```
+----------------------------------------------------------+
|              General Purpose Agent                       |
+----------------------------------------------------------+
                          |
        +-----------------+-----------------+
        |                 |                 |
        v                 v                 v
  +----------+      +----------+      +------------+
  | Planning |      | Thinking |      | Execution  |
  |  Module  | ---> |  Module  | ---> |   Engine   |
  +----------+      +----------+      +------------+
        |                 |                 |
        +-----------------+-----------------+
                          |
                          v
                  +-------------+
                  | Evaluation  |
                  |   Module    |
                  +-------------+
                          |
                          v
              +---------------------+
              | Tool Registry &     |
              |      Memory         |
              +---------------------+
```

## 📖 Documentation

### Getting Started
- 📘 **[Getting Started](docs/GETTING_STARTED.md)** - Setup and first steps
- 💬 **[Chat Guide](docs/CHAT_GUIDE.md)** - Interactive chat interfaces (CLI & Web)

### Framework Customization
- 🎨 **[Building Custom Agents](docs/BUILDING_CUSTOM_AGENTS.md)** - Build your own specialized agents
- 🎯 **[Query Routing](docs/QUERY_ROUTING.md)** - LLM-based query classification
- 🏗️ **[Architecture](docs/ARCHITECTURE.md)** - System design and components

### Usage & Examples
- 📚 **[Usage Guide](docs/USAGE_GUIDE.md)** - Patterns and best practices
- 💡 **[Basic Examples](examples/example_usage.py)** - Core usage examples
- 🎨 **[Custom Classifier Examples](examples/custom_classifier_example.py)** - Domain-specific agents
- 🤝 **[Multi-Agent Examples](examples/multi_agent_example.py)** - Collaboration examples
- 📡 **[Streaming Examples](examples/streaming_example.py)** - Real-time streaming

## 🚀 Quick Start

### Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd agent-test

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure Azure OpenAI (optional for demo mode)
cp .env.example .env
# Edit .env with your Azure OpenAI credentials
```

### 💬 Chat Interfaces (Recommended)

#### Terminal Chat
```bash
python chat.py
```

#### Web Chat
```bash
python start_server.py
# Open http://localhost:8000 in your browser
```

Features:
- 🗨️ **Conversational interface** like Claude Code
- 📊 **Real-time status updates** during execution
- 📜 **Message history** for context
- ⚠️ **Demo mode** works without Azure OpenAI configuration

### 📝 Programmatic Usage

```python
from dotenv import load_dotenv
from src.agent import GeneralPurposeAgent

load_dotenv()

# Create an agent
agent = GeneralPurposeAgent(verbose=True)

# Execute a task
goal = "Create a Python script that prints 'Hello, World!' and save it as hello.py"
evaluation = agent.run(goal)

# Check results
print(f"Success: {evaluation.overall_success}")
print(f"Score: {evaluation.overall_score:.2f}")
```

## 🎯 Agent Workflow

The agent follows a structured 4-phase workflow:

```
1️⃣ PLANNING
   └─ Analyze goal and decompose into subtasks
   └─ Identify dependencies and create strategy

2️⃣ THINKING
   └─ Reason about approach
   └─ Reflect on each action

3️⃣ EXECUTION
   └─ Execute subtasks in order
   └─ Use appropriate tools
   └─ Handle errors with replanning

4️⃣ EVALUATION
   └─ Assess each step
   └─ Calculate overall success
   └─ Extract lessons learned
```

## 💡 Usage Examples

### Simple Task

```python
agent = GeneralPurposeAgent()
result = agent.quick_task("List all Python files in the current directory")
```

### Complex Task with Planning

```python
goal = """
Analyze the project structure and create a report:
1. Find all Python files
2. Count lines of code in each file
3. Identify main modules
4. Save analysis to 'project_analysis.txt'
"""

evaluation = agent.run(goal)
```

### Custom Tool

```python
from src.tools.base import Tool, ToolParameter

class MyCustomTool(Tool):
    @property
    def name(self) -> str:
        return "my_tool"

    @property
    def description(self) -> str:
        return "Description of what this tool does"

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="param",
                type="string",
                description="Parameter description",
                required=True
            )
        ]

    def execute(self, **kwargs) -> Dict[str, Any]:
        # Your implementation
        return {"success": True, "result": "..."}

# Register and use
agent = GeneralPurposeAgent()
agent.register_tool(MyCustomTool())
```

### Multi-Agent Collaboration

```python
from src.collaboration import AgentOrchestrator, PlannerAgent, ExecutorAgent, ReviewerAgent, AgentRole
from src.planning import PlanningModule
from src.execution import ExecutionEngine
from src.evaluation import EvaluationModule
from src.utils.llm_client import AzureOpenAIClient
from src.tools.base import ToolRegistry

# Create components
llm_client = AzureOpenAIClient()
tool_registry = ToolRegistry()

# Create orchestrator
orchestrator = AgentOrchestrator(verbose=True)

# Create and register specialized agents
orchestrator.register_agent('planner', PlannerAgent(PlanningModule(llm_client)), AgentRole.PLANNER)
orchestrator.register_agent('executor', ExecutorAgent(ExecutionEngine(llm_client, tool_registry)), AgentRole.EXECUTOR)
orchestrator.register_agent('reviewer', ReviewerAgent(EvaluationModule(llm_client)), AgentRole.REVIEWER)

# Run collaboration
goal = "Create a data analysis script with visualizations"
result = orchestrator.collaborate(goal)
```

### Streaming Responses

```python
from src.streaming import StreamHandler, StreamEventType

# Create stream handler
stream_handler = StreamHandler()

# Subscribe to events
def on_event(event):
    print(f"[{event.type.value}] {event.data}")

stream_handler.subscribe(on_event)

# Execute with streaming
stream_handler.emit_start("Calculate statistics")
stream_handler.emit_planning("Breaking down task...")
stream_handler.emit_execution("Running calculations...")
stream_handler.emit_complete({"result": "Done", "success": True})

# Get event history
for event in stream_handler.get_history():
    print(event.to_json())
```

### Web UI Dashboard

```bash
# Start the web server
python -m uvicorn src.web_ui.app:app --host 0.0.0.0 --port 8000

# Or use the example script
python examples/web_ui_example.py
```

Access the dashboard at: [http://localhost:8000](http://localhost:8000)

**Available Endpoints:**
- `POST /api/run` - Execute task
- `GET /api/stream/{goal}` - Stream execution with SSE
- `GET /api/collaboration/run` - Multi-agent collaboration
- `WS /ws` - WebSocket for real-time updates

## ⚙️ Configuration

Customize agent behavior via YAML configuration:

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

Load configuration:

```python
agent = GeneralPurposeAgent(config_path="config.yaml")
```

## 🧪 Testing

```bash
# Run unit tests
python -m pytest tests/

# Or with unittest
python -m unittest discover tests/
```

## 📦 Project Structure

```
agent-test/
├── src/                    # Core source code
│   ├── agent.py           # Main Agent class
│   ├── planning.py        # Planning module
│   ├── thinking.py        # Thinking module
│   ├── execution.py       # Execution engine
│   ├── evaluation.py      # Evaluation module
│   ├── memory.py          # Memory management
│   ├── collaboration/     # Multi-agent system
│   │   ├── orchestrator.py
│   │   └── specialized_agents.py
│   ├── streaming/         # Streaming responses
│   │   └── stream_handler.py
│   ├── web_ui/            # Web dashboard
│   │   ├── app.py
│   │   ├── templates/
│   │   └── static/
│   ├── tools/             # Tool system
│   │   ├── base.py
│   │   ├── file_ops.py
│   │   ├── code_exec.py
│   │   └── web_search.py
│   └── utils/             # Utilities
│       └── llm_client.py
├── docs/                   # Documentation
│   ├── README.zh-CN.md
│   ├── GETTING_STARTED.md
│   ├── ARCHITECTURE.md
│   └── USAGE_GUIDE.md
├── examples/              # Usage examples
│   ├── example_usage.py
│   ├── multi_agent_example.py
│   ├── streaming_example.py
│   └── web_ui_example.py
├── tests/                 # Unit tests
├── config.yaml           # Configuration
└── requirements.txt      # Dependencies
```

## 🔧 Requirements

- Python 3.8+
- Azure OpenAI API access with GPT-4
- See [requirements.txt](requirements.txt) for dependencies

## 🚧 Roadmap

- [x] **Multi-agent collaboration** - ✅ Completed
- [x] **Streaming responses** - ✅ Completed
- [x] **Web UI dashboard** - ✅ Completed
- [ ] Support for multiple LLM providers (OpenAI, Anthropic, local models)
- [ ] Asynchronous tool execution
- [ ] Vector-based memory with semantic search
- [ ] Tool marketplace
- [ ] Advanced context management

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by [Claude Code](https://claude.com/claude-code) and modern AI agent architectures
- Built with Azure OpenAI GPT-4
- Thanks to the open-source AI community

## 📞 Support

- 📚 Check the [documentation](docs/)
- 💡 Try the [examples](examples/example_usage.py)
- 🐛 Report issues on GitHub
- 📧 Contact the maintainers

---

**Built with ❤️ using Azure OpenAI and Python**

[⬆ Back to top](#general-purpose-agent-)
