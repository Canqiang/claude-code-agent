# 💬 Chat Interface Guide

This guide explains how to use the chat interfaces for interacting with the Agent system.

## 🖥️ Terminal Chat (CLI)

### Starting the Chat

```bash
# Method 1: Run chat.py directly
python chat.py

# Method 2: Make it executable and run
chmod +x chat.py
./chat.py
```

### Chat Commands

The terminal chat interface supports the following commands:

- `/help` - Show help message and available commands
- `/clear` - Clear conversation history
- `/history` - Display conversation history
- `/exit` or `/quit` - Exit the chat

### Features

- ✅ **Conversational Interface** - Natural chat-like interaction
- 📊 **Real-time Status** - See agent progress with live indicators
- 📜 **History Tracking** - Maintains conversation context
- 🎨 **Formatted Output** - Color-coded messages with timestamps
- ⚠️ **Demo Mode** - Works even without Azure OpenAI configured

### Example Session

```
💬 You: Create a Python function to calculate factorial

🤖 Assistant [Processing...]
   🎯 Planning task...
   🤔 Analyzing request...
   ⚙️ Generating response...
   ✅ Complete!

🤖 Assistant [14:30:15]
   I'll help you create a factorial function...

   [Response continues...]
```

## 🌐 Web Chat Interface

### Starting the Web Chat

```bash
# Start the server
python -m uvicorn src.web_ui.app:app --host 0.0.0.0 --port 8000

# Or use the web UI example
python examples/web_ui_example.py
```

### Accessing the Chat

Open your browser and navigate to:
- **Chat Interface**: http://localhost:8000 (default)
- **Chat Interface**: http://localhost:8000/chat
- **Dashboard Interface**: http://localhost:8000/dashboard (old task-based UI)

### Features

- 💬 **Modern Chat UI** - Beautiful, responsive chat interface
- 🔄 **Real-time Streaming** - See responses as they're generated
- 📱 **Mobile Friendly** - Works on all devices
- 🎨 **Syntax Highlighting** - Code blocks are properly formatted
- 📊 **Progress Indicators** - Visual progress bars during execution
- ⚠️ **Demo Mode Support** - Test the UI without Azure OpenAI
- 🗑️ **Clear Chat** - Start fresh conversations anytime

### Web Chat Controls

- **Enter** - Send message
- **Shift + Enter** - New line in message
- **🗑️ Clear Button** - Clear chat history
- **⚙️ Settings Button** - Configuration (coming soon)

## 🎯 Usage Examples

### Simple Question

```
You: What is the factorial of 5?
Agent: The factorial of 5 is 120.

Calculation: 5! = 5 × 4 × 3 × 2 × 1 = 120
```

### Complex Task

```
You: Create a Python script that reads a CSV file and calculates statistics

Agent: [Processing with real-time status updates]
   🎯 Planning: Breaking down into subtasks
   🤔 Thinking: Need to handle file I/O and statistics
   ⚙️ Executing: Creating script...
   ✅ Complete!

[Agent provides detailed script with explanations]
```

### Code Request

```
You: Write a function to check if a number is prime

Agent: Here's a prime number checker:

```python
def is_prime(n):
    """Check if a number is prime."""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True
```

This function efficiently checks primality by only testing divisors up to √n.
```

## 🎨 Chat Interface Features

### Message Formatting

The chat interfaces support basic Markdown-like formatting:

- **Bold**: `**text**` → **text**
- *Italic*: `*text*` → *text*
- `Code`: `` `code` `` → `code`
- Code blocks: Triple backticks

### Status Indicators

- 🚀 START - Task initiated
- 🎯 PLANNING - Creating execution plan
- 🤔 THINKING - Reasoning about approach
- ⚙️ EXECUTION - Running tasks
- 🔧 TOOL_CALL - Using tools
- 📊 EVALUATION - Assessing results
- ✅ COMPLETE - Task finished
- ❌ ERROR - Something went wrong

## ⚙️ Configuration

### Demo Mode vs Real Mode

**Demo Mode** (No Azure OpenAI configured):
- ⚠️ Shows demo responses
- Simulates agent behavior
- Good for testing UI
- No real task execution

**Real Mode** (Azure OpenAI configured):
- ✅ Full agent capabilities
- Real task planning and execution
- Tool usage (file ops, code execution, web search)
- Accurate evaluations

### Enabling Real Mode

1. Create `.env` file:
```bash
cp .env.example .env
```

2. Add your credentials to `.env`:
```
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
```

3. Restart the chat interface

## 🔄 Comparison: CLI vs Web Chat

| Feature | CLI Chat | Web Chat |
|---------|----------|----------|
| Interface | Terminal | Browser |
| Portability | Requires Python | Any device with browser |
| History | Session only | Session only |
| Formatting | Basic | Rich (Markdown) |
| Status Updates | Text indicators | Progress bars |
| Mobile | No | Yes |
| Accessibility | Keyboard only | Mouse + Keyboard |

## 💡 Tips and Best Practices

1. **Be Specific**: Clear requests get better responses
   - ❌ "Help with code"
   - ✅ "Write a Python function to validate email addresses"

2. **Provide Context**: Reference previous messages for continuity
   - "Can you modify that function to also check for..."

3. **Break Down Complex Tasks**: For large tasks, break into steps
   - "First, help me plan the project structure"
   - "Now, let's implement the data processing module"

4. **Use Commands**: Leverage chat commands for better experience
   - Use `/clear` to start fresh conversations
   - Use `/history` to review what you've discussed

5. **Check Demo Mode**: Look for the configuration banner
   - ⚠️ Demo mode → Configure Azure OpenAI for full features
   - ✅ Configured → Full functionality available

## 🐛 Troubleshooting

### Chat Not Responding

1. Check server is running: `http://localhost:8000/health`
2. Check browser console for errors (F12)
3. Verify Azure OpenAI configuration (if not in demo mode)

### Terminal Chat Issues

1. Ensure Python 3.8+ is installed
2. Install dependencies: `pip install -r requirements.txt`
3. Check environment variables are loaded

### Streaming Not Working

1. Verify Server-Sent Events (SSE) support in browser
2. Check firewall/proxy settings
3. Try refreshing the page

## 📚 Next Steps

- Explore [examples](examples/) for more usage patterns
- Read [ARCHITECTURE.md](docs/ARCHITECTURE.md) to understand how it works
- Check [USAGE_GUIDE.md](docs/USAGE_GUIDE.md) for advanced features
- Contribute improvements via GitHub

---

**Happy Chatting! 🎉**
