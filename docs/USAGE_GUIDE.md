# Usage Guide

## Quick Reference

### Installation & Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

# 3. Run quick start
python quickstart.py
```

### Basic Usage Patterns

#### Pattern 1: Simple Task Execution

```python
from src.agent import GeneralPurposeAgent

agent = GeneralPurposeAgent()
result = agent.quick_task("List all Python files in the current directory")
print(result.output)
```

**When to use:**
- Single-step tasks
- No need for planning
- Quick operations

#### Pattern 2: Complex Goal with Planning

```python
from src.agent import GeneralPurposeAgent

agent = GeneralPurposeAgent(verbose=True)

goal = """
Analyze the codebase and create a report:
1. Find all Python files
2. Count lines of code
3. Identify main modules
4. Save report to 'analysis.txt'
"""

evaluation = agent.run(goal)
```

**When to use:**
- Multi-step tasks
- Need decomposition
- Want evaluation

#### Pattern 3: Custom Configuration

```python
config = {
    'agent': {
        'name': 'DataAnalysisAgent',
        'max_iterations': 20,
        'thinking_enabled': True,
        'verbose': False
    },
    'llm': {
        'temperature': 0.5,  # Lower for more deterministic
        'max_tokens': 8192
    },
    'planning': {
        'max_subtasks': 15,
        'allow_replanning': True
    },
    'evaluation': {
        'success_threshold': 0.8  # Higher standard
    }
}

agent = GeneralPurposeAgent(config=config)
```

**When to use:**
- Specific domain tasks
- Need fine-tuning
- Production deployment

#### Pattern 4: Custom Tools

```python
from src.tools.base import Tool, ToolParameter
from typing import List, Dict, Any

class DatabaseQueryTool(Tool):
    @property
    def name(self) -> str:
        return "query_database"

    @property
    def description(self) -> str:
        return "Execute SQL queries on the database"

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="query",
                type="string",
                description="SQL query to execute",
                required=True
            )
        ]

    def execute(self, **kwargs) -> Dict[str, Any]:
        query = kwargs.get("query")
        # Your database logic here
        return {
            "success": True,
            "result": {"rows": [...]}
        }

# Register and use
agent = GeneralPurposeAgent()
agent.register_tool(DatabaseQueryTool())
```

**When to use:**
- Domain-specific operations
- Integration with systems
- Specialized capabilities

## Common Use Cases

### Use Case 1: File Processing

```python
agent = GeneralPurposeAgent()

goal = """
Process all CSV files in the data/ directory:
1. Read each CSV file
2. Calculate basic statistics
3. Create a summary report
4. Save to 'data_summary.txt'
"""

evaluation = agent.run(goal)
```

### Use Case 2: Code Generation

```python
agent = GeneralPurposeAgent(verbose=True)

goal = """
Create a Python script that:
1. Connects to an API
2. Fetches user data
3. Processes and filters the data
4. Saves results to JSON
Include error handling and logging
"""

evaluation = agent.run(goal)
```

### Use Case 3: Data Analysis

```python
agent = GeneralPurposeAgent()

goal = """
Analyze the sales data:
1. Read sales.csv
2. Calculate monthly totals
3. Find top products
4. Generate Python visualization code
5. Save analysis to report.txt
"""

evaluation = agent.run(goal)
```

### Use Case 4: Documentation Generation

```python
agent = GeneralPurposeAgent()

goal = """
Generate documentation:
1. Read all Python files in src/
2. Extract docstrings and function signatures
3. Create markdown documentation
4. Save to docs/API.md
"""

evaluation = agent.run(goal)
```

## Configuration Guide

### Temperature Settings

```python
# Creative tasks (0.7-1.0)
config = {'llm': {'temperature': 0.9}}

# Balanced (0.5-0.7)
config = {'llm': {'temperature': 0.6}}

# Deterministic (0.0-0.5)
config = {'llm': {'temperature': 0.3}}
```

### Iteration Limits

```python
# Simple tasks
config = {'agent': {'max_iterations': 5}}

# Complex tasks
config = {'agent': {'max_iterations': 15}}

# Very complex tasks
config = {'agent': {'max_iterations': 30}}
```

### Success Thresholds

```python
# Lenient (0.5-0.6)
config = {'evaluation': {'success_threshold': 0.5}}

# Standard (0.7-0.8)
config = {'evaluation': {'success_threshold': 0.7}}

# Strict (0.9-1.0)
config = {'evaluation': {'success_threshold': 0.95}}
```

## Debugging Tips

### Enable Verbose Mode

```python
agent = GeneralPurposeAgent(verbose=True)
```

**Shows:**
- Planning process
- Tool executions
- Thinking process
- Evaluations

### Check Step Evaluations

```python
evaluation = agent.run(goal)

for step in evaluation.step_evaluations:
    print(f"Step {step.step_id}: {step.success}")
    print(f"Score: {step.score}")
    if step.issues:
        print(f"Issues: {step.issues}")
```

### Monitor Tool Calls

```python
result = agent.quick_task(task)
print(f"Tool calls made: {len(result.tool_calls)}")
for call in result.tool_calls:
    print(f"  - {call['tool']}: {call['result']}")
```

### Review Thinking Process

```python
agent = GeneralPurposeAgent(verbose=True)
# Thinking will be printed during execution
```

## Performance Optimization

### Reduce Token Usage

```python
# Use quick_task for simple operations
result = agent.quick_task("Simple task")

# Instead of full run with planning
evaluation = agent.run("Simple task")
```

### Cache Results

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_agent_task(task_hash):
    agent = GeneralPurposeAgent()
    return agent.quick_task(task_hash)
```

### Batch Operations

```python
# Instead of multiple calls
for file in files:
    agent.quick_task(f"Process {file}")

# Batch into one call
goal = f"Process these files: {', '.join(files)}"
agent.run(goal)
```

## Error Handling

### Basic Error Handling

```python
try:
    evaluation = agent.run(goal)
    if not evaluation.overall_success:
        print(f"Task failed with score: {evaluation.overall_score}")
        print(f"Weaknesses: {evaluation.weaknesses}")
except Exception as e:
    print(f"Agent error: {e}")
```

### Retry Logic

```python
max_retries = 3
for attempt in range(max_retries):
    try:
        evaluation = agent.run(goal)
        if evaluation.overall_success:
            break
    except Exception as e:
        if attempt == max_retries - 1:
            raise
        print(f"Retry {attempt + 1}/{max_retries}")
```

### Graceful Degradation

```python
# Try with planning first
try:
    evaluation = agent.run(goal)
except Exception:
    # Fall back to quick task
    result = agent.quick_task(goal)
```

## Advanced Patterns

### Multi-Agent Workflow

```python
# Specialized agents
planner_agent = GeneralPurposeAgent(config={
    'llm': {'temperature': 0.3}
})

executor_agent = GeneralPurposeAgent(config={
    'agent': {'max_iterations': 20}
})

# Plan with one, execute with another
plan = planner_agent.planning_module.create_plan(goal)
# Execute subtasks with executor_agent
```

### Conditional Execution

```python
agent = GeneralPurposeAgent()

# Execute based on previous result
result1 = agent.quick_task("Check if file exists")

if "exists" in result1.output.lower():
    result2 = agent.quick_task("Read the file")
else:
    result2 = agent.quick_task("Create the file")
```

### Progressive Enhancement

```python
agent = GeneralPurposeAgent()

# Start simple
result = agent.quick_task("List files")

# Enhance based on result
if result.success:
    goal = f"Analyze these files: {result.output}"
    evaluation = agent.run(goal)
```

## Testing Your Agent

### Unit Test Example

```python
import unittest
from src.agent import GeneralPurposeAgent

class TestMyAgent(unittest.TestCase):
    def setUp(self):
        self.agent = GeneralPurposeAgent(verbose=False)

    def test_simple_task(self):
        result = self.agent.quick_task("Test task")
        self.assertTrue(result.success)

    def test_complex_task(self):
        evaluation = self.agent.run("Complex goal")
        self.assertGreater(evaluation.overall_score, 0.7)
```

### Integration Test Example

```python
def test_file_workflow():
    agent = GeneralPurposeAgent()

    # Create file
    agent.quick_task("Create test.txt with content 'Hello'")

    # Read file
    result = agent.quick_task("Read test.txt")

    assert "Hello" in result.output
```

## Best Practices

### DO:
- Use descriptive goals
- Enable verbose mode for debugging
- Check evaluation results
- Handle errors gracefully
- Test with different configurations
- Monitor token usage
- Use appropriate tools

### DON'T:
- Use quick_task for complex multi-step tasks
- Ignore evaluation scores
- Set max_iterations too low
- Use very high temperature for critical tasks
- Execute untrusted code without sandboxing
- Ignore error messages
- Overload single tasks

## Troubleshooting

### Problem: Agent not calling tools

**Solution:**
```python
# Make goal more explicit
goal = "Use the read_file tool to read config.yaml"

# Instead of
goal = "Show me the config"
```

### Problem: Low evaluation scores

**Solution:**
```python
# Lower threshold
config = {'evaluation': {'success_threshold': 0.6}}

# Or improve task description
goal = "Create a Python script that prints 'Hello' and save as hello.py"
# Instead of: "Make a hello script"
```

### Problem: Timeout errors

**Solution:**
```python
# Increase iterations
config = {'agent': {'max_iterations': 20}}

# Or break into smaller tasks
agent.quick_task("Task part 1")
agent.quick_task("Task part 2")
```

## Support

For more help:
- Check [README.md](README.md) for overview
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for deep dive
- See [examples/example_usage.py](examples/example_usage.py) for examples
- Run [quickstart.py](quickstart.py) for hands-on demo

---

Happy agent building! 🤖
