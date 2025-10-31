"""
Multi-Agent Collaboration Example

This example demonstrates how to use multiple specialized agents
working together to accomplish complex tasks.
"""

import os
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.llm_client import AzureOpenAIClient
from src.planning import PlanningModule
from src.execution import ExecutionEngine
from src.evaluation import EvaluationModule
from src.tools.base import ToolRegistry
from src.tools.file_ops import FileReadTool, FileWriteTool
from src.tools.code_exec import PythonExecuteTool
from src.collaboration import (
    AgentOrchestrator,
    PlannerAgent,
    ExecutorAgent,
    ReviewerAgent,
    AgentRole
)


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


def example_1_basic_collaboration():
    """Example 1: Basic multi-agent collaboration."""
    print("=" * 60)
    print("Example 1: Basic Multi-Agent Collaboration")
    print("=" * 60)

    # Create components
    llm_client = AzureOpenAIClient()
    tool_registry = ToolRegistry()
    tool_registry.register(FileReadTool())
    tool_registry.register(FileWriteTool())
    tool_registry.register(PythonExecuteTool())

    # Create orchestrator
    orchestrator = AgentOrchestrator(verbose=True)

    # Create specialized agents
    planner = PlannerAgent(PlanningModule(llm_client))
    executor = ExecutorAgent(ExecutionEngine(llm_client, tool_registry))
    reviewer = ReviewerAgent(EvaluationModule(llm_client))

    # Register agents
    orchestrator.register_agent('planner', planner, AgentRole.PLANNER)
    orchestrator.register_agent('executor', executor, AgentRole.EXECUTOR)
    orchestrator.register_agent('reviewer', reviewer, AgentRole.REVIEWER)

    # Run collaboration
    goal = "Create a Python function that calculates the Fibonacci sequence and save it to a file"
    print(f"\n🎯 Goal: {goal}\n")

    result = orchestrator.collaborate(goal)

    print("\n✅ Collaboration Result:")
    print(f"   Success: {result.get('success', False)}")
    print(f"   Output: {result.get('output', 'No output')}")

    return result


def example_2_data_analysis_collaboration():
    """Example 2: Multi-agent collaboration for data analysis."""
    print("\n" + "=" * 60)
    print("Example 2: Data Analysis Collaboration")
    print("=" * 60)

    # Create components
    llm_client = AzureOpenAIClient()
    tool_registry = ToolRegistry()
    tool_registry.register(FileReadTool())
    tool_registry.register(FileWriteTool())
    tool_registry.register(PythonExecuteTool())

    # Create orchestrator
    orchestrator = AgentOrchestrator(verbose=True)

    # Create specialized agents
    planner = PlannerAgent(PlanningModule(llm_client))
    executor = ExecutorAgent(ExecutionEngine(llm_client, tool_registry))
    reviewer = ReviewerAgent(EvaluationModule(llm_client))

    # Register agents
    orchestrator.register_agent('planner', planner, AgentRole.PLANNER)
    orchestrator.register_agent('executor', executor, AgentRole.EXECUTOR)
    orchestrator.register_agent('reviewer', reviewer, AgentRole.REVIEWER)

    # Complex task requiring multiple steps
    goal = """
    Create a data analysis pipeline that:
    1. Generates sample sales data (10 records)
    2. Calculates total revenue and average order value
    3. Saves the analysis results to a file
    """

    print(f"\n🎯 Goal: {goal}\n")

    result = orchestrator.collaborate(goal)

    print("\n✅ Collaboration Result:")
    print(f"   Success: {result.get('success', False)}")
    if result.get('plan'):
        print(f"   Tasks completed: {len(result['plan'].subtasks)}")

    return result


def example_3_custom_agent_workflow():
    """Example 3: Custom multi-agent workflow."""
    print("\n" + "=" * 60)
    print("Example 3: Custom Agent Workflow")
    print("=" * 60)

    # Create components
    llm_client = AzureOpenAIClient()
    tool_registry = ToolRegistry()
    tool_registry.register(FileReadTool())
    tool_registry.register(FileWriteTool())
    tool_registry.register(PythonExecuteTool())

    # Create orchestrator with custom settings
    orchestrator = AgentOrchestrator(
        verbose=True,
        max_iterations=15  # Allow more iterations for complex tasks
    )

    # Create specialized agents
    planner = PlannerAgent(PlanningModule(llm_client))
    executor = ExecutorAgent(ExecutionEngine(llm_client, tool_registry))
    reviewer = ReviewerAgent(EvaluationModule(llm_client))

    # Register agents
    orchestrator.register_agent('planner', planner, AgentRole.PLANNER)
    orchestrator.register_agent('executor', executor, AgentRole.EXECUTOR)
    orchestrator.register_agent('reviewer', reviewer, AgentRole.REVIEWER)

    # Complex task
    goal = """
    Build a simple password strength checker that:
    1. Checks password length (minimum 8 characters)
    2. Checks for uppercase and lowercase letters
    3. Checks for numbers and special characters
    4. Returns a strength score (weak/medium/strong)
    5. Includes test cases
    """

    print(f"\n🎯 Goal: {goal}\n")

    result = orchestrator.collaborate(goal)

    print("\n✅ Collaboration Result:")
    print(f"   Success: {result.get('success', False)}")
    print(f"   Evaluation Score: {result.get('evaluation', {}).get('overall_score', 0):.2f}")

    return result


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("🤖 Multi-Agent Collaboration Examples")
    print("=" * 60)

    # Check environment
    if not check_environment():
        return

    print("\n✅ Environment variables are set correctly!")

    try:
        # Run examples
        example_1_basic_collaboration()
        example_2_data_analysis_collaboration()
        example_3_custom_agent_workflow()

        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)

        print("\n📚 Next Steps:")
        print("   1. Check the created files in your directory")
        print("   2. Experiment with different goals and tasks")
        print("   3. Add more specialized agents for specific domains")
        print("   4. Try the streaming examples for real-time updates")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
