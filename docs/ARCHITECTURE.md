# Agent Architecture Documentation

## System Overview

The General Purpose Agent is designed following the principles of Claude Code, with a modular architecture that separates concerns into distinct, reusable components.

## Core Components

### 1. Agent Core (`agent.py`)

The main orchestrator that coordinates all modules.

**Responsibilities:**
- Initialize and configure all modules
- Manage the agent lifecycle
- Coordinate the workflow between modules
- Handle task routing (quick tasks vs. planned tasks)

**Key Methods:**
- `run(goal, context)`: Full workflow with planning and evaluation
- `quick_task(task)`: Direct execution without planning
- `register_tool(tool)`: Add custom tools

### 2. Planning Module (`planning.py`)

Decomposes complex goals into actionable subtasks.

**Key Features:**
- Task decomposition using LLM
- Dependency management
- Replanning on failure
- Strategy formulation

**Data Structures:**
```python
SubTask:
    - id: int
    - description: str
    - reasoning: str
    - dependencies: List[int]
    - status: str  # pending, in_progress, completed, failed
    - result: Optional[Dict]

Plan:
    - goal: str
    - subtasks: List[SubTask]
    - strategy: str
    - created_at: str
```

**Workflow:**
1. Receive goal and context
2. Use LLM to analyze and decompose
3. Generate structured plan with dependencies
4. Return Plan object

### 3. Thinking Module (`thinking.py`)

Provides explicit reasoning capabilities.

**Thinking Types:**
- **Observation**: Notice current state
- **Reasoning**: Logical step-by-step analysis
- **Reflection**: Analyze past actions
- **Decision**: Choose between options

**Key Methods:**
- `think(context, question, type)`: Generate thought
- `reflect_on_action(action, result, expected)`: Reflect on outcomes
- `analyze_failure(task, error, attempts)`: Analyze failures
- `make_decision(situation, options)`: Decision making

**Benefits:**
- Transparent decision-making
- Improved debugging
- Learning from experience
- Better error handling

### 4. Execution Engine (`execution.py`)

Executes tasks using available tools and LLM.

**Key Features:**
- Tool integration via function calling
- Iterative execution loop
- Context management
- Error handling and recovery

**Execution Loop:**
```
1. Send task to LLM with available tools
2. Receive response (may include tool calls)
3. If tool calls:
   a. Execute each tool
   b. Add results to context
   c. Continue to step 1
4. If no tool calls:
   a. Task complete
   b. Return result
5. Repeat until max iterations or completion
```

**Tool Integration:**
- Tools registered in ToolRegistry
- Converted to OpenAI function calling format
- Executed with parameter validation
- Results fed back to LLM

### 5. Evaluation Module (`evaluation.py`)

Assesses task execution quality.

**Two-Level Evaluation:**

**Step Evaluation:**
- Evaluate individual subtasks
- Compare expected vs. actual outcomes
- Generate numeric score (0-1)
- Identify issues and suggestions

**Final Evaluation:**
- Aggregate all step evaluations
- Calculate overall score
- Extract strengths/weaknesses
- Document lessons learned

**Evaluation Criteria:**
- Task success (binary)
- Execution quality (0-1 score)
- Issues encountered
- Potential improvements

### 6. Memory System (`memory.py`)

Manages context and history.

**Working Memory:**
- Current conversation messages
- Task context
- Temporary state

**Long-term Memory:**
- Task history
- Learned patterns
- Performance metrics

**Usage:**
```python
working_memory.add_message(role, content)
working_memory.update_context(key, value)
long_term_memory.save_task(task_data)
```

### 7. Tool System (`tools/`)

Extensible framework for agent capabilities.

**Base Classes:**
- `Tool`: Abstract base class
- `ToolParameter`: Parameter definition
- `ToolRegistry`: Tool management

**Built-in Tools:**
- `FileReadTool`: Read file contents
- `FileWriteTool`: Write to files
- `FileListTool`: List directory contents
- `PythonExecuteTool`: Execute Python code
- `WebSearchTool`: Fetch web content

**Custom Tool Creation:**
```python
class CustomTool(Tool):
    @property
    def name(self) -> str:
        return "tool_name"

    @property
    def description(self) -> str:
        return "Tool description"

    @property
    def parameters(self) -> List[ToolParameter]:
        return [...]

    def execute(self, **kwargs) -> Dict[str, Any]:
        # Implementation
        return {"success": True, "result": ...}
```

### 8. LLM Client (`utils/llm_client.py`)

Azure OpenAI integration.

**Features:**
- Chat completion API
- Function calling support
- Retry logic with exponential backoff
- Response parsing

**Configuration:**
- API key and endpoint
- Deployment name
- Temperature and max tokens
- API version

## Data Flow

```
User Goal
    ↓
┌─────────────────────────────────────────┐
│         Agent Core                      │
│  ┌───────────────────────────────────┐ │
│  │  1. PLANNING PHASE                │ │
│  │     - Thinking: Analyze goal      │ │
│  │     - Planning: Decompose tasks   │ │
│  └───────────────────────────────────┘ │
│              ↓                          │
│  ┌───────────────────────────────────┐ │
│  │  2. EXECUTION PHASE               │ │
│  │     For each subtask:             │ │
│  │     - Check dependencies          │ │
│  │     - Execute with tools          │ │
│  │     - Thinking: Reflect           │ │
│  │     - Evaluate step               │ │
│  └───────────────────────────────────┘ │
│              ↓                          │
│  ┌───────────────────────────────────┐ │
│  │  3. EVALUATION PHASE              │ │
│  │     - Aggregate step results      │ │
│  │     - Calculate overall score     │ │
│  │     - Extract insights            │ │
│  └───────────────────────────────────┘ │
│              ↓                          │
│  ┌───────────────────────────────────┐ │
│  │  4. MEMORY PHASE                  │ │
│  │     - Save to long-term memory    │ │
│  │     - Clear working memory        │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
    ↓
Final Evaluation Result
```

## Tool Execution Flow

```
LLM Response
    ↓
Has tool_calls?
    ↓ Yes
┌────────────────────────┐
│  For each tool_call:   │
│  1. Parse function     │
│  2. Get tool from      │
│     registry           │
│  3. Execute tool       │
│  4. Capture result     │
└────────────────────────┘
    ↓
Add tool results to messages
    ↓
Send back to LLM
    ↓
Repeat until no tool_calls
    ↓
Return final response
```

## Configuration System

Configuration can be provided via:
1. YAML file (`config.yaml`)
2. Dictionary (programmatic)
3. Defaults (built-in)

**Configuration Hierarchy:**
```yaml
agent:
  name: str
  max_iterations: int
  thinking_enabled: bool
  verbose: bool

llm:
  temperature: float
  max_tokens: int
  top_p: float

planning:
  max_subtasks: int
  allow_replanning: bool

evaluation:
  step_evaluation: bool
  final_evaluation: bool
  success_threshold: float
```

## Error Handling

**Strategy:**
1. **Tool Level**: Return error in result dict
2. **Execution Level**: Continue with error context
3. **Planning Level**: Trigger replanning if enabled
4. **Agent Level**: Graceful degradation

**Error Types:**
- Tool execution failures
- LLM API errors (with retry)
- Timeout errors
- Validation errors

## Extensibility Points

### 1. Custom Tools
Add domain-specific capabilities:
```python
agent.register_tool(CustomTool())
```

### 2. Custom Thinking Types
Extend thinking module:
```python
thinking_module.think(context, question, type="custom")
```

### 3. Custom Evaluation Criteria
Override evaluation logic:
```python
class CustomEvaluationModule(EvaluationModule):
    def evaluate_step(self, ...):
        # Custom logic
```

### 4. Custom Memory Strategies
Implement different memory patterns:
```python
class VectorMemory(LongTermMemory):
    # Vector-based retrieval
```

## Performance Considerations

### Token Usage
- Planning: 1-2K tokens
- Execution: Variable (depends on iterations)
- Evaluation: 500-1K tokens per evaluation
- Total: 5-10K tokens for typical task

### Latency
- Planning: 2-5 seconds
- Tool execution: Variable
- Step evaluation: 1-2 seconds each
- Final evaluation: 2-3 seconds

### Optimization Strategies
1. Cache tool results
2. Batch evaluations
3. Async tool execution (future)
4. Smart context pruning

## Security Considerations

### Code Execution
- Python execution uses subprocess
- No access to environment variables
- Timeout enforced
- Consider sandboxing for production

### File Operations
- No path validation by default
- Consider restricting to specific directories
- Add permission checks

### Web Operations
- No authentication by default
- Rate limiting not implemented
- Consider adding safety checks

## Testing Strategy

### Unit Tests
- Test each module independently
- Mock LLM responses
- Test error conditions

### Integration Tests
- Test module interactions
- Real LLM calls (expensive)
- End-to-end scenarios

### Example Tests
```python
# Unit test
def test_tool_registry():
    registry = ToolRegistry()
    registry.register(MockTool())
    assert registry.get("mock_tool") is not None

# Integration test
def test_agent_run():
    agent = GeneralPurposeAgent()
    result = agent.run("Simple task")
    assert result.overall_success
```

## Future Enhancements

### Planned Features
1. **Multi-Agent Collaboration**
   - Agent-to-agent communication
   - Task delegation
   - Parallel execution

2. **Advanced Memory**
   - Vector storage integration
   - Semantic retrieval
   - Memory compression

3. **Streaming**
   - Real-time output
   - Progress updates
   - Cancellation support

4. **Observability**
   - Tracing integration
   - Metrics collection
   - Dashboard

5. **Tool Marketplace**
   - Community tools
   - Tool discovery
   - Version management

## Best Practices

### Agent Usage
1. Start with verbose mode for debugging
2. Use quick_task for simple operations
3. Enable thinking for complex tasks
4. Set appropriate success thresholds

### Tool Development
1. Clear, descriptive names
2. Comprehensive parameter descriptions
3. Consistent error handling
4. Return structured results

### Configuration
1. Use config files for production
2. Override specific values as needed
3. Test with different thresholds
4. Monitor token usage

### Error Handling
1. Always catch exceptions in tools
2. Provide informative error messages
3. Enable replanning for critical tasks
4. Log failures for analysis

## Troubleshooting

### Common Issues

**LLM Not Calling Tools:**
- Check tool descriptions are clear
- Verify function calling is enabled
- Ensure parameters are well-defined

**Execution Timeout:**
- Increase max_iterations
- Break tasks into smaller subtasks
- Check tool execution time

**Low Evaluation Scores:**
- Review expected outcomes
- Check tool implementations
- Adjust success threshold

**Memory Issues:**
- Clear working memory regularly
- Prune long-term memory
- Reduce context size

## Conclusion

This architecture provides a robust foundation for building intelligent agents capable of handling complex tasks through planning, thinking, execution, and evaluation. The modular design allows for easy extension and customization while maintaining clear separation of concerns.
