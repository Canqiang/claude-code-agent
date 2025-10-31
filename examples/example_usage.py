"""Example usage of the General Purpose Agent."""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.agent import GeneralPurposeAgent

# Load environment variables
load_dotenv()


def example_1_simple_task():
    """Example 1: Simple file operation task."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Simple File Operation")
    print("="*80)

    agent = GeneralPurposeAgent(verbose=True)

    goal = "Create a file called 'test_output.txt' with the content 'Hello from Agent!'"

    result = agent.quick_task(goal)

    print(f"\nResult: {result.success}")
    print(f"Output: {result.output}")


def example_2_complex_task_with_planning():
    """Example 2: Complex task requiring planning."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Complex Task with Planning")
    print("="*80)

    agent = GeneralPurposeAgent(verbose=True)

    goal = """Analyze the current directory structure and create a summary report:
    1. List all Python files
    2. Count the total number of files
    3. Save the report to 'directory_report.txt'
    """

    evaluation = agent.run(goal)

    print(f"\nFinal Success: {evaluation.overall_success}")
    print(f"Final Score: {evaluation.overall_score:.2f}")


def example_3_with_python_execution():
    """Example 3: Task involving Python code execution."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Python Code Execution")
    print("="*80)

    agent = GeneralPurposeAgent(verbose=True)

    goal = """Calculate the factorial of 10 using Python and save the result to a file called 'factorial.txt'"""

    evaluation = agent.run(goal)

    print(f"\nFinal Success: {evaluation.overall_success}")
    print(f"Final Score: {evaluation.overall_score:.2f}")


def example_4_with_thinking():
    """Example 4: Complex reasoning task."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Complex Reasoning Task")
    print("="*80)

    agent = GeneralPurposeAgent(
        config={
            'agent': {
                'name': 'ThinkingAgent',
                'max_iterations': 15,
                'thinking_enabled': True,
                'verbose': True
            },
            'llm': {
                'temperature': 0.8,
                'max_tokens': 4096
            },
            'planning': {
                'max_subtasks': 10,
                'allow_replanning': True
            },
            'evaluation': {
                'step_evaluation': True,
                'final_evaluation': True,
                'success_threshold': 0.7
            }
        }
    )

    goal = """Create a simple Python script that:
    1. Generates 10 random numbers between 1 and 100
    2. Calculates their mean and median
    3. Saves the results to 'statistics.txt'
    4. Then execute the script and verify it works
    """

    evaluation = agent.run(goal)

    print(f"\nFinal Success: {evaluation.overall_success}")
    print(f"Final Score: {evaluation.overall_score:.2f}")


def example_5_custom_tool():
    """Example 5: Using a custom tool."""
    print("\n" + "="*80)
    print("EXAMPLE 5: Custom Tool")
    print("="*80)

    from src.tools.base import Tool, ToolParameter
    from typing import List, Dict, Any
    import random

    class RandomNumberTool(Tool):
        """Custom tool for generating random numbers."""

        @property
        def name(self) -> str:
            return "generate_random_numbers"

        @property
        def description(self) -> str:
            return "Generate a list of random numbers"

        @property
        def parameters(self) -> List[ToolParameter]:
            return [
                ToolParameter(
                    name="count",
                    type="integer",
                    description="Number of random numbers to generate",
                    required=True
                ),
                ToolParameter(
                    name="min_value",
                    type="integer",
                    description="Minimum value (default: 1)",
                    required=False
                ),
                ToolParameter(
                    name="max_value",
                    type="integer",
                    description="Maximum value (default: 100)",
                    required=False
                )
            ]

        def execute(self, **kwargs) -> Dict[str, Any]:
            count = kwargs.get("count", 10)
            min_value = kwargs.get("min_value", 1)
            max_value = kwargs.get("max_value", 100)

            try:
                numbers = [random.randint(min_value, max_value) for _ in range(count)]
                return {
                    "success": True,
                    "result": {
                        "numbers": numbers,
                        "count": len(numbers),
                        "min": min(numbers),
                        "max": max(numbers),
                        "sum": sum(numbers)
                    }
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }

    # Create agent and register custom tool
    agent = GeneralPurposeAgent(verbose=True)
    agent.register_tool(RandomNumberTool())

    goal = "Generate 20 random numbers between 1 and 50 and tell me their sum"

    result = agent.quick_task(goal)

    print(f"\nResult: {result.success}")
    print(f"Output: {result.output}")


if __name__ == "__main__":
    # Check if Azure OpenAI credentials are set
    required_env_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_DEPLOYMENT_NAME"
    ]

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables in a .env file or your environment.")
        sys.exit(1)

    # Run examples
    print("\n" + "="*80)
    print("GENERAL PURPOSE AGENT - EXAMPLES")
    print("="*80)

    # Uncomment the examples you want to run:

    # example_1_simple_task()
    # example_2_complex_task_with_planning()
    # example_3_with_python_execution()
    # example_4_with_thinking()
    # example_5_custom_tool()

    # Run a specific example
    print("\nTo run examples, uncomment them in the main block.")
    print("Or run a specific example:")
    print("  python examples/example_usage.py")
