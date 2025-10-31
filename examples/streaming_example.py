"""
Streaming Response Example

This example demonstrates how to use the streaming API
to get real-time updates during agent execution.
"""

import os
from pathlib import Path
import sys
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import GeneralPurposeAgent
from src.streaming import StreamHandler, StreamEvent, StreamEventType


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


def example_1_basic_streaming():
    """Example 1: Basic streaming with event handler."""
    print("=" * 60)
    print("Example 1: Basic Streaming")
    print("=" * 60)

    # Create stream handler
    stream_handler = StreamHandler()

    # Subscribe to events with a callback
    def on_event(event: StreamEvent):
        """Callback for stream events."""
        print(f"\n[{event.type.value}] {event.timestamp}")
        print(f"  Data: {event.data}")

    stream_handler.subscribe(on_event)

    # Simulate agent execution with streaming
    goal = "Calculate the sum of numbers from 1 to 10"
    print(f"\n🎯 Goal: {goal}\n")

    # Emit events
    stream_handler.emit_start(goal)
    time.sleep(0.5)

    stream_handler.emit_planning("Breaking down the task into steps...")
    time.sleep(0.5)

    stream_handler.emit_thinking("I need to create a loop to sum numbers from 1 to 10")
    time.sleep(0.5)

    stream_handler.emit_execution("Executing calculation...")
    time.sleep(0.5)

    stream_handler.emit_progress("Calculation in progress...", 50)
    time.sleep(0.5)

    result = sum(range(1, 11))
    stream_handler.emit_tool_call("python_execute", {"code": "sum(range(1, 11))"}, {"result": result})
    time.sleep(0.5)

    stream_handler.emit_evaluation({"score": 1.0, "success": True})
    time.sleep(0.5)

    stream_handler.emit_complete({"result": result, "success": True})

    print("\n✅ Streaming completed!")
    return stream_handler


def example_2_streaming_with_history():
    """Example 2: Access streaming history."""
    print("\n" + "=" * 60)
    print("Example 2: Streaming with History")
    print("=" * 60)

    # Create stream handler
    stream_handler = StreamHandler()

    goal = "Create a function to check if a number is prime"
    print(f"\n🎯 Goal: {goal}\n")

    # Emit multiple events
    stream_handler.emit_start(goal)
    stream_handler.emit_planning("Planning the implementation...")
    stream_handler.emit_thinking("Need to check divisibility from 2 to sqrt(n)")
    stream_handler.emit_execution("Writing the function...")
    stream_handler.emit_complete({"success": True})

    # Access history
    print("\n📜 Event History:")
    for i, event in enumerate(stream_handler.get_history(), 1):
        print(f"  {i}. [{event.type.value}] {event.timestamp}")

    print(f"\n✅ Total events: {len(stream_handler.get_history())}")

    return stream_handler


def example_3_streaming_to_sse():
    """Example 3: Convert events to Server-Sent Events format."""
    print("\n" + "=" * 60)
    print("Example 3: Streaming to SSE Format")
    print("=" * 60)

    # Create stream handler
    stream_handler = StreamHandler()

    goal = "Generate a random password"
    print(f"\n🎯 Goal: {goal}\n")

    # Emit events
    stream_handler.emit_start(goal)
    stream_handler.emit_planning("Planning password generation...")
    stream_handler.emit_execution("Generating password...")
    stream_handler.emit_complete({"password": "Xy9$mK2p", "success": True})

    # Convert to SSE format
    print("\n📡 SSE Format Output:")
    print("-" * 60)
    for event in stream_handler.get_history():
        sse_data = event.to_sse()
        print(sse_data)
        print("-" * 60)

    return stream_handler


def example_4_real_agent_streaming():
    """Example 4: Real agent execution with streaming."""
    print("\n" + "=" * 60)
    print("Example 4: Real Agent with Streaming")
    print("=" * 60)

    # Create stream handler
    stream_handler = StreamHandler()

    # Subscribe to events for real-time display
    event_count = {'count': 0}

    def on_event(event: StreamEvent):
        event_count['count'] += 1
        symbol = {
            StreamEventType.START: "🚀",
            StreamEventType.PLANNING: "🎯",
            StreamEventType.THINKING: "🤔",
            StreamEventType.EXECUTION: "⚙️",
            StreamEventType.TOOL_CALL: "🔧",
            StreamEventType.EVALUATION: "📊",
            StreamEventType.COMPLETE: "✅",
            StreamEventType.ERROR: "❌",
            StreamEventType.PROGRESS: "📈"
        }.get(event.type, "•")

        print(f"{symbol} [{event.type.value}]", end="")

        if event.type == StreamEventType.PROGRESS:
            percentage = event.data.get('percentage', 0)
            print(f" {percentage}%")
        elif event.type == StreamEventType.COMPLETE:
            print(f" Done!")
        else:
            print()

    stream_handler.subscribe(on_event)

    # Create agent
    agent = GeneralPurposeAgent(verbose=False)

    goal = "Calculate factorial of 5"
    print(f"\n🎯 Goal: {goal}\n")

    # Emit start event
    stream_handler.emit_start(goal)

    try:
        # Simulate progress updates during agent execution
        stream_handler.emit_planning("Creating execution plan...")
        time.sleep(0.3)

        stream_handler.emit_progress("Planning complete", 25)
        time.sleep(0.3)

        stream_handler.emit_thinking("Analyzing the task...")
        time.sleep(0.3)

        stream_handler.emit_progress("Executing task", 50)
        time.sleep(0.3)

        # Run agent (in real implementation, agent would emit events internally)
        evaluation = agent.run(goal)

        stream_handler.emit_progress("Task completed", 90)
        time.sleep(0.3)

        stream_handler.emit_evaluation({
            "score": evaluation.overall_score,
            "success": evaluation.overall_success
        })
        time.sleep(0.3)

        stream_handler.emit_complete({
            "success": evaluation.overall_success,
            "score": evaluation.overall_score,
            "summary": evaluation.summary
        })

        print(f"\n✅ Agent execution completed!")
        print(f"   Events emitted: {event_count['count']}")
        print(f"   Success: {evaluation.overall_success}")
        print(f"   Score: {evaluation.overall_score:.2f}")

    except Exception as e:
        stream_handler.emit_error(str(e))
        print(f"\n❌ Error: {e}")

    return stream_handler


def example_5_custom_event_processing():
    """Example 5: Custom event processing and filtering."""
    print("\n" + "=" * 60)
    print("Example 5: Custom Event Processing")
    print("=" * 60)

    # Create stream handler
    stream_handler = StreamHandler()

    # Multiple subscribers with different filters
    planning_events = []
    execution_events = []
    all_events = []

    def on_planning_event(event: StreamEvent):
        if event.type == StreamEventType.PLANNING:
            planning_events.append(event)

    def on_execution_event(event: StreamEvent):
        if event.type in [StreamEventType.EXECUTION, StreamEventType.TOOL_CALL]:
            execution_events.append(event)

    def on_all_events(event: StreamEvent):
        all_events.append(event)

    stream_handler.subscribe(on_planning_event)
    stream_handler.subscribe(on_execution_event)
    stream_handler.subscribe(on_all_events)

    goal = "Process data pipeline"
    print(f"\n🎯 Goal: {goal}\n")

    # Emit various events
    stream_handler.emit_start(goal)
    stream_handler.emit_planning("Step 1: Data ingestion")
    stream_handler.emit_planning("Step 2: Data transformation")
    stream_handler.emit_execution("Loading data...")
    stream_handler.emit_tool_call("file_read", {"path": "data.csv"}, {"rows": 100})
    stream_handler.emit_execution("Transforming data...")
    stream_handler.emit_tool_call("python_execute", {"code": "transform(data)"}, {"status": "ok"})
    stream_handler.emit_complete({"success": True})

    # Print filtered results
    print(f"\n📊 Event Statistics:")
    print(f"   Planning events: {len(planning_events)}")
    print(f"   Execution events: {len(execution_events)}")
    print(f"   Total events: {len(all_events)}")

    print(f"\n📋 Planning Events:")
    for event in planning_events:
        print(f"   - {event.data}")

    print(f"\n⚙️ Execution Events:")
    for event in execution_events:
        print(f"   - {event.type.value}: {event.data}")

    return stream_handler


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("📡 Streaming Response Examples")
    print("=" * 60)

    # Check environment
    if not check_environment():
        return

    print("\n✅ Environment variables are set correctly!")

    try:
        # Run examples
        example_1_basic_streaming()
        example_2_streaming_with_history()
        example_3_streaming_to_sse()
        example_4_real_agent_streaming()
        example_5_custom_event_processing()

        print("\n" + "=" * 60)
        print("✅ All streaming examples completed!")
        print("=" * 60)

        print("\n📚 Next Steps:")
        print("   1. Try the Web UI for visual streaming experience")
        print("   2. Integrate streaming into your own applications")
        print("   3. Create custom event subscribers for logging")
        print("   4. Experiment with Server-Sent Events (SSE) in web apps")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
