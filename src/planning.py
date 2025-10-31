"""Planning module for task decomposition."""
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from .utils.llm_client import AzureOpenAIClient


class SubTask(BaseModel):
    """A subtask in the plan."""
    id: int
    description: str
    reasoning: str
    dependencies: List[int] = []
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Optional[Dict[str, Any]] = None


class Plan(BaseModel):
    """A plan consisting of multiple subtasks."""
    goal: str
    subtasks: List[SubTask]
    strategy: str
    created_at: str


class PlanningModule:
    """Module for decomposing complex tasks into subtasks."""

    def __init__(self, llm_client: AzureOpenAIClient, max_subtasks: int = 20):
        """Initialize the planning module.

        Args:
            llm_client: Azure OpenAI client
            max_subtasks: Maximum number of subtasks
        """
        self.llm_client = llm_client
        self.max_subtasks = max_subtasks

    def create_plan(self, goal: str, context: Optional[str] = None) -> Plan:
        """Create a plan for achieving the goal.

        Args:
            goal: The goal to achieve
            context: Additional context information

        Returns:
            A Plan object with subtasks
        """
        system_prompt = f"""You are an expert planning agent. Your task is to decompose complex goals into clear, actionable subtasks.

Rules:
1. Break down the goal into {self.max_subtasks} or fewer subtasks
2. Each subtask should be specific and actionable
3. Identify dependencies between subtasks
4. Provide reasoning for each subtask
5. Define a high-level strategy

Output your plan as valid JSON with this structure:
{{
    "strategy": "Overall strategy description",
    "subtasks": [
        {{
            "id": 1,
            "description": "Subtask description",
            "reasoning": "Why this subtask is needed",
            "dependencies": [0]  // IDs of subtasks that must complete first
        }}
    ]
}}"""

        user_prompt = f"""Goal: {goal}

{f'Context: {context}' if context else ''}

Please create a detailed plan to achieve this goal."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = self.llm_client.chat_completion(messages=messages)
        content = self.llm_client.extract_message_content(response)

        # Parse JSON response
        try:
            # Extract JSON from potential markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            plan_data = json.loads(content)

            subtasks = [
                SubTask(
                    id=task.get("id", idx + 1),
                    description=task["description"],
                    reasoning=task.get("reasoning", ""),
                    dependencies=task.get("dependencies", [])
                )
                for idx, task in enumerate(plan_data.get("subtasks", []))
            ]

            from datetime import datetime
            return Plan(
                goal=goal,
                subtasks=subtasks,
                strategy=plan_data.get("strategy", ""),
                created_at=datetime.now().isoformat()
            )

        except (json.JSONDecodeError, KeyError) as e:
            # Fallback: create a simple single-task plan
            return Plan(
                goal=goal,
                subtasks=[
                    SubTask(
                        id=1,
                        description=goal,
                        reasoning="Direct execution of the goal",
                        dependencies=[]
                    )
                ],
                strategy="Direct execution",
                created_at=datetime.now().isoformat()
            )

    def replan(self, original_plan: Plan, completed_subtasks: List[int], failure_reason: str) -> Plan:
        """Replan based on failures or new information.

        Args:
            original_plan: The original plan
            completed_subtasks: IDs of completed subtasks
            failure_reason: Reason for replanning

        Returns:
            Updated Plan
        """
        system_prompt = """You are an expert planning agent. A previous plan has encountered issues and needs to be revised.

Analyze the situation and create an updated plan that:
1. Preserves completed subtasks
2. Addresses the failure
3. Adds new subtasks if needed
4. Adjusts the strategy

Output your updated plan in the same JSON format as before."""

        user_prompt = f"""Original Goal: {original_plan.goal}
Original Strategy: {original_plan.strategy}
Completed Subtasks: {completed_subtasks}
Failure Reason: {failure_reason}

Original Subtasks:
{json.dumps([task.dict() for task in original_plan.subtasks], indent=2)}

Please create an updated plan to continue towards the goal."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = self.llm_client.chat_completion(messages=messages)
        content = self.llm_client.extract_message_content(response)

        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            plan_data = json.loads(content)

            subtasks = [
                SubTask(
                    id=task.get("id", idx + 1),
                    description=task["description"],
                    reasoning=task.get("reasoning", ""),
                    dependencies=task.get("dependencies", []),
                    status="completed" if task.get("id", idx + 1) in completed_subtasks else "pending"
                )
                for idx, task in enumerate(plan_data.get("subtasks", []))
            ]

            from datetime import datetime
            return Plan(
                goal=original_plan.goal,
                subtasks=subtasks,
                strategy=plan_data.get("strategy", original_plan.strategy),
                created_at=datetime.now().isoformat()
            )

        except (json.JSONDecodeError, KeyError):
            # Return original plan if replanning fails
            return original_plan
