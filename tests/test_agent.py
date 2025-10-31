"""Unit tests for the General Purpose Agent."""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import GeneralPurposeAgent
from src.tools.base import Tool, ToolParameter, ToolRegistry
from src.planning import SubTask, Plan
from src.evaluation import StepEvaluation, FinalEvaluation


class TestToolRegistry(unittest.TestCase):
    """Test the ToolRegistry."""

    def test_register_and_get_tool(self):
        """Test registering and retrieving a tool."""
        registry = ToolRegistry()

        # Create a mock tool
        mock_tool = Mock(spec=Tool)
        mock_tool.name = "test_tool"

        registry.register(mock_tool)

        retrieved_tool = registry.get("test_tool")
        self.assertEqual(retrieved_tool, mock_tool)

    def test_get_nonexistent_tool(self):
        """Test retrieving a nonexistent tool."""
        registry = ToolRegistry()
        tool = registry.get("nonexistent")
        self.assertIsNone(tool)


class TestSubTask(unittest.TestCase):
    """Test the SubTask model."""

    def test_subtask_creation(self):
        """Test creating a subtask."""
        subtask = SubTask(
            id=1,
            description="Test task",
            reasoning="Test reasoning",
            dependencies=[],
            status="pending"
        )

        self.assertEqual(subtask.id, 1)
        self.assertEqual(subtask.description, "Test task")
        self.assertEqual(subtask.status, "pending")


class TestPlan(unittest.TestCase):
    """Test the Plan model."""

    def test_plan_creation(self):
        """Test creating a plan."""
        subtasks = [
            SubTask(
                id=1,
                description="Task 1",
                reasoning="Reason 1",
                dependencies=[]
            ),
            SubTask(
                id=2,
                description="Task 2",
                reasoning="Reason 2",
                dependencies=[1]
            )
        ]

        plan = Plan(
            goal="Test goal",
            subtasks=subtasks,
            strategy="Test strategy",
            created_at="2024-01-01T00:00:00"
        )

        self.assertEqual(plan.goal, "Test goal")
        self.assertEqual(len(plan.subtasks), 2)
        self.assertEqual(plan.strategy, "Test strategy")


class TestStepEvaluation(unittest.TestCase):
    """Test the StepEvaluation model."""

    def test_step_evaluation_creation(self):
        """Test creating a step evaluation."""
        evaluation = StepEvaluation(
            step_id=1,
            step_description="Test step",
            success=True,
            score=0.9,
            reasoning="Good execution",
            issues=[],
            suggestions=[]
        )

        self.assertTrue(evaluation.success)
        self.assertEqual(evaluation.score, 0.9)


class TestFinalEvaluation(unittest.TestCase):
    """Test the FinalEvaluation model."""

    def test_final_evaluation_creation(self):
        """Test creating a final evaluation."""
        step_eval = StepEvaluation(
            step_id=1,
            step_description="Test step",
            success=True,
            score=1.0,
            reasoning="Perfect",
            issues=[],
            suggestions=[]
        )

        final_eval = FinalEvaluation(
            goal="Test goal",
            overall_success=True,
            overall_score=1.0,
            step_evaluations=[step_eval],
            summary="Test summary",
            strengths=["Fast execution"],
            weaknesses=[],
            lessons_learned=["Testing is important"]
        )

        self.assertTrue(final_eval.overall_success)
        self.assertEqual(final_eval.overall_score, 1.0)
        self.assertEqual(len(final_eval.step_evaluations), 1)


class TestGeneralPurposeAgent(unittest.TestCase):
    """Test the GeneralPurposeAgent."""

    @patch('src.agent.AzureOpenAIClient')
    def test_agent_initialization(self, mock_llm_client):
        """Test agent initialization."""
        agent = GeneralPurposeAgent(verbose=False)

        self.assertIsNotNone(agent.tool_registry)
        self.assertIsNotNone(agent.planning_module)
        self.assertIsNotNone(agent.thinking_module)
        self.assertIsNotNone(agent.execution_engine)
        self.assertIsNotNone(agent.evaluation_module)

    @patch('src.agent.AzureOpenAIClient')
    def test_register_custom_tool(self, mock_llm_client):
        """Test registering a custom tool."""
        agent = GeneralPurposeAgent(verbose=False)

        mock_tool = Mock(spec=Tool)
        mock_tool.name = "custom_tool"

        agent.register_tool(mock_tool)

        retrieved_tool = agent.tool_registry.get("custom_tool")
        self.assertEqual(retrieved_tool, mock_tool)


if __name__ == "__main__":
    unittest.main()
