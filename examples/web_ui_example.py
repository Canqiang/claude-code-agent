"""
Web UI Example

This example demonstrates how to start and use the Web UI Dashboard
for the Agent system.

The Web UI provides:
- Interactive task execution interface
- Real-time streaming of agent progress
- Multi-agent collaboration visualization
- Results display with evaluation metrics
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_environment():
    """Check if environment variables are set."""
    required_vars = [
        'AZURE_OPENAI_API_KEY',
        'AZURE_OPENAI_ENDPOINT',
        'AZURE_OPENAI_DEPLOYMENT_NAME'
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Please copy .env.example to .env and fill in your Azure OpenAI credentials.")
        return False

    return True


def check_dependencies():
    """Check if web dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import websockets
        import jinja2
        return True
    except ImportError as e:
        print("❌ Missing required dependencies for Web UI:")
        print(f"   {e}")
        print("\n💡 Install web dependencies:")
        print("   pip install fastapi uvicorn websockets jinja2 python-multipart")
        return False


def print_usage_guide():
    """Print usage guide for the Web UI."""
    print("\n" + "=" * 70)
    print("📚 Web UI Usage Guide")
    print("=" * 70)

    print("\n🌐 Accessing the Dashboard:")
    print("   Open your browser and navigate to: http://localhost:8000")

    print("\n🎯 Running Tasks:")
    print("   1. Enter your task goal in the text area")
    print("   2. Choose execution mode:")
    print("      • Run Task - Standard execution with final results")
    print("      • Run with Streaming - Real-time progress updates")
    print("      • Multi-Agent Collaboration - Specialized agents working together")

    print("\n📊 Features:")
    print("   • Real-time progress tracking with visual progress bar")
    print("   • Live stream of agent activities (planning, thinking, execution)")
    print("   • Detailed evaluation results with scores and feedback")
    print("   • Multi-agent coordination visualization")

    print("\n🔌 API Endpoints:")
    print("   • POST /api/run - Execute task (REST)")
    print("   • GET  /api/stream/{goal} - Stream task execution (SSE)")
    print("   • GET  /api/collaboration/run - Multi-agent collaboration")
    print("   • WS   /ws - WebSocket for real-time communication")
    print("   • GET  /health - Health check")

    print("\n💡 Example Tasks to Try:")
    print("   1. 'Create a Python function to calculate factorial'")
    print("   2. 'Generate a random password with 12 characters'")
    print("   3. 'Calculate the sum of numbers from 1 to 100'")
    print("   4. 'Create a simple data analysis script'")

    print("\n🛑 Stopping the Server:")
    print("   Press Ctrl+C in the terminal where the server is running")

    print("\n" + "=" * 70)


def print_api_examples():
    """Print API usage examples."""
    print("\n" + "=" * 70)
    print("🔧 API Usage Examples")
    print("=" * 70)

    print("\n1️⃣ Python Requests Example:")
    print("""
import requests
import json

# Run a task
response = requests.post('http://localhost:8000/api/run',
    json={
        'goal': 'Calculate factorial of 5',
        'use_collaboration': False
    }
)

result = response.json()
print(f"Success: {result['success']}")
print(f"Score: {result['score']}")
print(f"Summary: {result['summary']}")
""")

    print("\n2️⃣ JavaScript Fetch Example:")
    print("""
// Run a task
fetch('http://localhost:8000/api/run', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        goal: 'Generate a random password',
        use_collaboration: false
    })
})
.then(response => response.json())
.then(data => {
    console.log('Success:', data.success);
    console.log('Score:', data.score);
    console.log('Summary:', data.summary);
});
""")

    print("\n3️⃣ Server-Sent Events (SSE) Example:")
    print("""
// Stream task execution
const goal = 'Create a function to check prime numbers';
const eventSource = new EventSource(`/api/stream/${encodeURIComponent(goal)}`);

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(`[${data.type}]`, data.data);

    if (data.type === 'COMPLETE') {
        eventSource.close();
    }
};

eventSource.onerror = (error) => {
    console.error('SSE Error:', error);
    eventSource.close();
};
""")

    print("\n4️⃣ cURL Example:")
    print("""
# Run a task
curl -X POST http://localhost:8000/api/run \\
  -H "Content-Type: application/json" \\
  -d '{
    "goal": "Calculate sum of 1 to 10",
    "use_collaboration": false
  }'

# Health check
curl http://localhost:8000/health
""")

    print("\n" + "=" * 70)


def start_server():
    """Start the Web UI server."""
    print("\n" + "=" * 70)
    print("🚀 Starting Agent Dashboard Web UI")
    print("=" * 70)

    try:
        import uvicorn
        from src.web_ui.app import app

        print("\n✅ Server starting...")
        print("   URL: http://localhost:8000")
        print("   Press Ctrl+C to stop")
        print()

        # Start the server
        uvicorn.run(app, host="0.0.0.0", port=8000)

    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point."""
    print("\n" + "=" * 70)
    print("🤖 Agent Dashboard - Web UI")
    print("=" * 70)

    # Check environment
    if not check_environment():
        return

    print("\n✅ Environment variables are set correctly!")

    # Check dependencies
    if not check_dependencies():
        return

    print("✅ All dependencies are installed!")

    # Print guides
    print_usage_guide()
    print_api_examples()

    # Ask user if they want to start the server
    print("\n" + "=" * 70)
    response = input("\n🚀 Start the Web UI server now? (y/n): ").strip().lower()

    if response == 'y':
        start_server()
    else:
        print("\n💡 To start the server later, run:")
        print("   python examples/web_ui_example.py")
        print("\n   Or directly:")
        print("   python -m uvicorn src.web_ui.app:app --host 0.0.0.0 --port 8000")
        print("\n   Or:")
        print("   cd src/web_ui && python app.py")


if __name__ == "__main__":
    main()
