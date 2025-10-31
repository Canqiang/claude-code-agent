# Getting Started

## Prerequisites

- Python 3.8 or higher
- Azure OpenAI API access with GPT-4
- pip (Python package manager)

## Step-by-Step Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `openai` - Azure OpenAI SDK
- `pydantic` - Data validation
- `python-dotenv` - Environment management
- `pyyaml` - Configuration parsing
- `tenacity` - Retry logic
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing

### 2. Configure Azure OpenAI

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

**Where to find these values:**
- **API Key**: Azure Portal → Your OpenAI Resource → Keys and Endpoint
- **Endpoint**: Same location as API Key
- **Deployment Name**: Azure Portal → Your OpenAI Resource → Model deployments
- **API Version**: Usually the latest stable version

### 3. Run Quick Start

```bash
python quickstart.py
```

This will:
- Verify your credentials
- Initialize the agent
- Run a simple demo task
- Show you the results

### 4. Try Examples

```bash
python examples/example_usage.py
```

Uncomment specific examples in the file to try different features.

## Your First Agent Task

Create a file `my_first_agent.py`:

```python
from dotenv import load_dotenv
from src.agent import GeneralPurposeAgent

# Load environment variables
load_dotenv()

# Create agent
agent = GeneralPurposeAgent(verbose=True)

# Define goal
goal = "Create a file called 'hello.txt' with the message 'Hello from my agent!'"

# Run agent
evaluation = agent.run(goal)

# Check results
print(f"\nSuccess: {evaluation.overall_success}")
print(f"Score: {evaluation.overall_score:.2f}")
```

Run it:

```bash
python my_first_agent.py
```

## Understanding the Output

The agent will show you:

1. **Planning Phase**: How it breaks down your goal
2. **Execution Phase**: Tools it uses and their results
3. **Evaluation Phase**: How well it performed
4. **Final Results**: Overall success and score

Example output:
```
============================================================
AGENT: GeneralPurposeAgent
GOAL: Create a file called 'hello.txt' with the message...
============================================================

[PHASE 1: PLANNING]

Strategy: Use file write tool to create the file directly

Subtasks (1):
  1. Write 'Hello from my agent!' to hello.txt

[PHASE 2: EXECUTION]

────────────────────────────────────────────────────────
Executing Subtask 1: Write 'Hello from my agent!' to hello.txt
────────────────────────────────────────────────────────

[Executing tool: write_file]
Arguments: {'file_path': 'hello.txt', 'content': 'Hello from my agent!'}
Result: {'success': True, 'result': {...}}

[PHASE 3: STEP EVALUATION]

============================================================
Step 1 Evaluation
============================================================
Success: ✓
Score: 1.00

[PHASE 4: FINAL EVALUATION]

============================================================
FINAL EVALUATION
============================================================
Overall Success: ✓
Overall Score: 1.00
```

## Next Steps

### Learn More
1. Read [README.md](README.md) for full documentation
2. Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
3. Review [USAGE_GUIDE.md](USAGE_GUIDE.md) for patterns

### Try More Examples
1. Complex multi-step tasks
2. Custom tool creation
3. Different configurations
4. Error handling

### Build Something
Ideas to try:
- Automated file organizer
- Code analysis tool
- Data processing pipeline
- Documentation generator
- Test case creator

## Common Issues

### Issue: "Missing required environment variables"

**Solution**: Make sure all variables are set in `.env`:
```bash
# Check if .env exists
ls -la .env

# Verify contents (don't share these!)
cat .env
```

### Issue: "Module not found"

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: "API call failed"

**Solution**: Verify your Azure OpenAI credentials:
1. Check API key is correct
2. Verify endpoint URL format
3. Ensure deployment name matches your Azure deployment
4. Check API version is supported

### Issue: "Tool not found"

**Solution**: Make sure you're using built-in tool names:
- `read_file`
- `write_file`
- `list_files`
- `execute_python`
- `fetch_web_content`

## Getting Help

If you run into issues:
1. Check error messages carefully
2. Enable verbose mode: `GeneralPurposeAgent(verbose=True)`
3. Review the examples
4. Check Azure OpenAI service status
5. Verify your API quota

## What's Next?

Now that you have a working agent, you can:

1. **Customize Configuration**
   ```python
   agent = GeneralPurposeAgent(config_path="my_config.yaml")
   ```

2. **Create Custom Tools**
   ```python
   from src.tools.base import Tool
   # Define your tool
   agent.register_tool(MyCustomTool())
   ```

3. **Build Applications**
   - CLI tools
   - Automation scripts
   - Data pipelines
   - Testing frameworks

Happy building! 🚀
