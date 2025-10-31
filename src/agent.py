"""Main Agent class integrating all modules."""
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path

from .utils.llm_client import AzureOpenAIClient
from .planning import PlanningModule, Plan, SubTask
from .thinking import ThinkingModule
from .execution import ExecutionEngine, ExecutionResult
from .evaluation import EvaluationModule, StepEvaluation, FinalEvaluation
from .memory import WorkingMemory, LongTermMemory
from .tools.base import ToolRegistry
from .tools import (
    FileReadTool,
    FileWriteTool,
    FileListTool,
    PythonExecuteTool,
    WebSearchTool,
)


class GeneralPurposeAgent:
    """A general-purpose agent with planning, thinking, execution, and evaluation capabilities."""

    def __init__(
        self,
        config_path: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        verbose: bool = True
    ):
        """Initialize the agent.

        Args:
            config_path: Path to configuration file
            config: Configuration dictionary (overrides config_path)
            verbose: Whether to print detailed output
        """
        # Load configuration
        if config:
            self.config = config
        elif config_path:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            # Default configuration
            self.config = {
                'agent': {
                    'name': 'GeneralPurposeAgent',
                    'max_iterations': 10,
                    'thinking_enabled': True,
                    'verbose': verbose
                },
                'llm': {
                    'temperature': 0.7,
                    'max_tokens': 4096
                },
                'planning': {
                    'max_subtasks': 20,
                    'allow_replanning': True
                },
                'evaluation': {
                    'step_evaluation': True,
                    'final_evaluation': True,
                    'success_threshold': 0.7
                }
            }

        self.verbose = self.config['agent'].get('verbose', verbose)
        self.thinking_enabled = self.config['agent'].get('thinking_enabled', True)

        # Initialize LLM client
        self.llm_client = AzureOpenAIClient(
            temperature=self.config['llm'].get('temperature', 0.7),
            max_tokens=self.config['llm'].get('max_tokens', 4096)
        )

        # Initialize tool registry
        self.tool_registry = ToolRegistry()
        self._register_default_tools()

        # Initialize modules
        self.planning_module = PlanningModule(
            llm_client=self.llm_client,
            max_subtasks=self.config['planning'].get('max_subtasks', 20)
        )

        self.thinking_module = ThinkingModule(
            llm_client=self.llm_client,
            verbose=self.verbose
        ) if self.thinking_enabled else None

        self.execution_engine = ExecutionEngine(
            llm_client=self.llm_client,
            tool_registry=self.tool_registry,
            thinking_module=self.thinking_module,
            max_iterations=self.config['agent'].get('max_iterations', 10)
        )

        self.evaluation_module = EvaluationModule(
            llm_client=self.llm_client,
            success_threshold=self.config['evaluation'].get('success_threshold', 0.7)
        )

        # Initialize memory
        self.working_memory = WorkingMemory()
        self.long_term_memory = LongTermMemory()

        # Current plan
        self.current_plan: Optional[Plan] = None

    def _register_default_tools(self):
        """Register default tools."""
        self.tool_registry.register(FileReadTool())
        self.tool_registry.register(FileWriteTool())
        self.tool_registry.register(FileListTool())
        self.tool_registry.register(PythonExecuteTool())
        self.tool_registry.register(WebSearchTool())

    def register_tool(self, tool):
        """Register a custom tool.

        Args:
            tool: Tool instance to register
        """
        self.tool_registry.register(tool)

    def run(self, goal: str, context: Optional[str] = None) -> FinalEvaluation:
        """Run the agent to achieve a goal.

        Args:
            goal: The goal to achieve
            context: Additional context information

        Returns:
            FinalEvaluation of the task
        """
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"AGENT: {self.config['agent']['name']}")
            print(f"GOAL: {goal}")
            print(f"{'='*60}\n")

        # Phase 1: Planning
        if self.verbose:
            print("[PHASE 1: PLANNING]")

        if self.thinking_enabled:
            self.thinking_module.think(
                context=context or "Starting new task",
                question=f"What is the best approach to achieve this goal: {goal}?",
                thinking_type="reasoning"
            )

        self.current_plan = self.planning_module.create_plan(goal, context)

        if self.verbose:
            print(f"\nStrategy: {self.current_plan.strategy}")
            print(f"\nSubtasks ({len(self.current_plan.subtasks)}):")
            for subtask in self.current_plan.subtasks:
                print(f"  {subtask.id}. {subtask.description}")
                if subtask.dependencies:
                    print(f"     Dependencies: {subtask.dependencies}")
            print()

        # Phase 2: Execution
        if self.verbose:
            print("\n[PHASE 2: EXECUTION]")

        step_evaluations: List[StepEvaluation] = []
        completed_subtasks: List[int] = []

        for subtask in self.current_plan.subtasks:
            # Check dependencies
            if not all(dep in completed_subtasks for dep in subtask.dependencies):
                if self.verbose:
                    print(f"\nSkipping subtask {subtask.id} - dependencies not met")
                continue

            if self.verbose:
                print(f"\n{'─'*60}")
                print(f"Executing Subtask {subtask.id}: {subtask.description}")
                print(f"{'─'*60}")

            # Execute the subtask
            result = self.execution_engine.execute_task(
                task_description=subtask.description,
                context=context
            )

            subtask.status = "completed" if result.success else "failed"
            subtask.result = {
                "success": result.success,
                "output": result.output,
                "error": result.error
            }

            # Phase 3: Step Evaluation
            if self.config['evaluation'].get('step_evaluation', True):
                step_eval = self.evaluation_module.evaluate_step(
                    step_id=subtask.id,
                    step_description=subtask.description,
                    expected_outcome=subtask.reasoning,
                    actual_result=subtask.result
                )
                step_evaluations.append(step_eval)

                if self.verbose:
                    self.evaluation_module.print_step_evaluation(step_eval)

            if result.success:
                completed_subtasks.append(subtask.id)
            else:
                # Handle failure
                if self.thinking_enabled:
                    self.thinking_module.analyze_failure(
                        task=subtask.description,
                        error=result.error or "Unknown error",
                        attempts=1
                    )

                # Optionally replan
                if self.config['planning'].get('allow_replanning', True):
                    if self.verbose:
                        print("\n[REPLANNING due to failure...]")

                    self.current_plan = self.planning_module.replan(
                        original_plan=self.current_plan,
                        completed_subtasks=completed_subtasks,
                        failure_reason=result.error or "Task failed"
                    )

        # Phase 4: Final Evaluation
        if self.verbose:
            print("\n[PHASE 4: FINAL EVALUATION]")

        final_evaluation = self.evaluation_module.evaluate_final(
            goal=goal,
            step_evaluations=step_evaluations,
            final_output=self.current_plan.subtasks[-1].result if self.current_plan.subtasks else None
        )

        if self.verbose:
            self.evaluation_module.print_final_evaluation(final_evaluation)

        # Save to long-term memory
        self.long_term_memory.save_task({
            'goal': goal,
            'plan': self.current_plan.dict(),
            'evaluation': final_evaluation.dict()
        })

        # Clear working memory
        self.working_memory.clear()

        if self.thinking_enabled:
            self.thinking_module.clear_thoughts()

        return final_evaluation

    def quick_task(self, task: str) -> ExecutionResult:
        """Execute a simple task without full planning and evaluation.

        Args:
            task: Task description

        Returns:
            ExecutionResult
        """
        if self.verbose:
            print(f"\n[QUICK TASK: {task}]\n")

        return self.execution_engine.execute_task(task_description=task)
