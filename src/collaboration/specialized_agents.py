"""Specialized agents for collaboration."""
from typing import Dict, Any, Optional
from ..planning import PlanningModule, Plan
from ..execution import ExecutionEngine
from ..evaluation import EvaluationModule


class PlannerAgent:
    """Specialized agent for planning tasks."""

    def __init__(self, planning_module: PlanningModule):
        """Initialize planner agent.

        Args:
            planning_module: Planning module instance
        """
        self.planning_module = planning_module

    def create_plan(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Plan:
        """Create a plan for the given goal.

        Args:
            goal: Goal to plan for
            context: Additional context

        Returns:
            Plan object
        """
        context_str = str(context) if context else None
        return self.planning_module.create_plan(goal, context_str)


class ExecutorAgent:
    """Specialized agent for executing plans."""

    def __init__(self, execution_engine: ExecutionEngine):
        """Initialize executor agent.

        Args:
            execution_engine: Execution engine instance
        """
        self.execution_engine = execution_engine

    def execute_plan(
        self,
        plan: Optional[Plan] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a plan.

        Args:
            plan: Plan to execute
            context: Additional context

        Returns:
            Execution results
        """
        if not plan:
            return {"success": False, "error": "No plan provided"}

        results = []
        for subtask in plan.subtasks:
            result = self.execution_engine.execute_task(
                task_description=subtask.description,
                context=str(context) if context else None
            )
            results.append({
                'subtask_id': subtask.id,
                'description': subtask.description,
                'success': result.success,
                'output': result.output
            })

        return {
            'success': all(r['success'] for r in results),
            'results': results
        }


class ReviewerAgent:
    """Specialized agent for reviewing execution results."""

    def __init__(self, evaluation_module: EvaluationModule):
        """Initialize reviewer agent.

        Args:
            evaluation_module: Evaluation module instance
        """
        self.evaluation_module = evaluation_module

    def review_execution(
        self,
        plan: Optional[Plan] = None,
        execution_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Review execution results.

        Args:
            plan: Original plan
            execution_result: Execution results

        Returns:
            Review results with approval status
        """
        if not plan or not execution_result:
            return {
                'approved': False,
                'reason': 'Missing plan or execution result'
            }

        # Evaluate each subtask
        evaluations = []
        for i, subtask in enumerate(plan.subtasks):
            if i < len(execution_result.get('results', [])):
                result = execution_result['results'][i]
                evaluation = self.evaluation_module.evaluate_step(
                    step_id=subtask.id,
                    step_description=subtask.description,
                    expected_outcome=subtask.reasoning,
                    actual_result=result
                )
                evaluations.append(evaluation)

        # Calculate overall approval
        avg_score = sum(e.score for e in evaluations) / len(evaluations) if evaluations else 0
        approved = avg_score >= self.evaluation_module.success_threshold

        return {
            'approved': approved,
            'average_score': avg_score,
            'evaluations': [
                {
                    'step_id': e.step_id,
                    'score': e.score,
                    'success': e.success,
                    'issues': e.issues
                }
                for e in evaluations
            ],
            'feedback': 'Execution meets quality standards' if approved else 'Revision needed'
        }
