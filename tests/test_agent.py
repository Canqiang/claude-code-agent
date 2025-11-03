"""
Test Agent using Azure OpenAI

This test demonstrates using the General Purpose Agent framework with Azure OpenAI.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import GeneralPurposeAgent
from src.utils.llm_client import AzureOpenAIClient
from src.streaming import StreamHandler, StreamEvent


def test_simple_task():
    """Test agent with a simple task."""
    print("\n" + "=" * 70)
    print("Test 1: Simple Task")
    print("=" * 70)

    # Load environment variables
    load_dotenv()

    # Create agent with Azure OpenAI
    agent = GeneralPurposeAgent(verbose=True)

    # Test task
    goal = "List the first 5 prime numbers"

    print(f"\n📝 Goal: {goal}\n")

    # Execute task
    evaluation = agent.run(goal)

    # Print results
    print("\n" + "=" * 70)
    print("📊 Results")
    print("=" * 70)
    print(f"✅ Success: {evaluation.overall_success}")
    print(f"📈 Score: {evaluation.overall_score:.2f}")
    print(f"\n💬 Summary:\n{evaluation.summary}")

    if evaluation.strengths:
        print(f"\n💪 Strengths:")
        for strength in evaluation.strengths:
            print(f"  • {strength}")

    if evaluation.weaknesses:
        print(f"\n⚠️  Weaknesses:")
        for weakness in evaluation.weaknesses:
            print(f"  • {weakness}")


def test_complex_task():
    """Test agent with a complex task."""
    print("\n" + "=" * 70)
    print("Test 2: Complex Task")
    print("=" * 70)

    load_dotenv()

    agent = GeneralPurposeAgent(verbose=True)

    goal = """Create a Python script that:
1. Calculates the factorial of numbers from 1 to 10
2. Saves the results to a file named 'factorials.txt'
3. Each line should be in format: 'factorial(n) = result'
"""

    print(f"\n📝 Goal: {goal}\n")

    evaluation = agent.run(goal)

    print("\n" + "=" * 70)
    print("📊 Results")
    print("=" * 70)
    print(f"✅ Success: {evaluation.overall_success}")
    print(f"📈 Score: {evaluation.overall_score:.2f}")


def test_llm_client():
    """Test Azure OpenAI client directly."""
    print("\n" + "=" * 70)
    print("Test 3: Azure OpenAI Client")
    print("=" * 70)

    load_dotenv()

    # Test LLM client
    client = AzureOpenAIClient()

    print("\n🔧 Testing Azure OpenAI connection...")

    response = client.chat_completion(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello in one sentence."}
        ],
        temperature=0.7,
        max_tokens=100
    )

    print(f"\n✅ Response: {response['content']}")
    print(f"📊 Tokens: {response.get('usage', {})}")


def test_streaming():
    """Test streaming with Azure OpenAI."""
    print("\n" + "=" * 70)
    print("Test 4: Streaming")
    print("=" * 70)

    load_dotenv()

    stream_handler = StreamHandler()

    # Subscribe to events
    def on_event(event: StreamEvent):
        print(f"[{event.type.value}] {event.data}")

    stream_handler.subscribe(on_event)

    # Simulate agent workflow
    print("\n🎬 Simulating agent workflow...\n")

    stream_handler.emit_start("Calculate fibonacci sequence")
    stream_handler.emit_planning("Breaking down the task...")
    stream_handler.emit_thinking("Deciding on algorithm...")
    stream_handler.emit_execution("Calculating fibonacci...", 50)
    stream_handler.emit_progress("Almost done...", 90)
    stream_handler.emit_evaluation({"score": 0.95, "success": True})
    stream_handler.emit_complete({
        "success": True,
        "score": 0.95,
        "summary": "Successfully calculated fibonacci sequence"
    })

    print("\n✅ Streaming test completed")


def test_interactive():
    """Interactive test - chat with the agent."""
    print("\n" + "=" * 70)
    print("Test 5: Interactive Chat (Azure OpenAI)")
    print("=" * 70)

    load_dotenv()

    agent = GeneralPurposeAgent(verbose=False)

    print("\n💬 Interactive Mode (type 'exit' to quit)")
    print("=" * 70 + "\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\n👋 Goodbye!")
                break

            if not user_input:
                continue

            print(f"\n🤖 Agent: Processing...\n")

            # Run agent
            evaluation = agent.run(user_input)

            # Print response
            print(f"🤖 Agent: {evaluation.summary}")

            if evaluation.overall_success:
                print(f"\n✅ Task completed successfully (Score: {evaluation.overall_score:.2f})")
            else:
                print(f"\n⚠️  Task completed with issues (Score: {evaluation.overall_score:.2f})")

            print()

        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    try:
        # Check Azure OpenAI configuration
        load_dotenv()

        required_vars = [
            'AZURE_OPENAI_API_KEY',
            'AZURE_OPENAI_ENDPOINT',
            'AZURE_OPENAI_DEPLOYMENT_NAME'
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            print("\n⚠️  Warning: Missing Azure OpenAI configuration")
            print("Missing environment variables:")
            for var in missing_vars:
                print(f"  - {var}")
            print("\nPlease configure .env file before running tests.")
            print("See .env.example for reference.")
            sys.exit(1)

        print("\n" + "=" * 70)
        print("🚀 Azure OpenAI Agent Tests")
        print("=" * 70)
        print("\nConfiguration:")
        print(f"  • Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
        print(f"  • Deployment: {os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')}")
        print(f"  • API Version: {os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')}")
        print("=" * 70)

        # Run tests
        test_llm_client()
        test_simple_task()
        test_complex_task()
        test_streaming()

        # Optional: Interactive mode
        print("\n" + "=" * 70)
        interactive = input("\n🤔 Run interactive mode? (y/n): ").strip().lower()

        if interactive == 'y':
            test_interactive()

        print("\n" + "=" * 70)
        print("✅ All tests completed!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
