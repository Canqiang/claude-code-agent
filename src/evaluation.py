"""Evaluation module for assessing task and step results."""
import json
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from .utils.llm_client import AzureOpenAIClient


class StepEvaluation(BaseModel):
    """Evaluation of a single step."""
    step_id: int
    step_description: str
    success: bool
    score: float  # 0.0 to 1.0
    reasoning: str
    issues: List[str] = []
    suggestions: List[str] = []


class FinalEvaluation(BaseModel):
    """Final evaluation of the entire task."""
    goal: str
    overall_success: bool
    overall_score: float  # 0.0 to 1.0
    step_evaluations: List[StepEvaluation]
    summary: str
    strengths: List[str]
    weaknesses: List[str]
    lessons_learned: List[str]


class EvaluationModule:
    """Module for evaluating task execution results."""

    def __init__(
        self,
        llm_client: AzureOpenAIClient,
        success_threshold: float = 0.7
    ):
        """Initialize the evaluation module.

        Args:
            llm_client: Azure OpenAI client
            success_threshold: Threshold for considering a task successful
        """
        self.llm_client = llm_client
        self.success_threshold = success_threshold

    def evaluate_step(
        self,
        step_id: int,
        step_description: str,
        expected_outcome: str,
        actual_result: Dict[str, Any]
    ) -> StepEvaluation:
        """Evaluate a single step.

        Args:
            step_id: Step identifier
            step_description: Description of the step
            expected_outcome: What was expected to happen
            actual_result: What actually happened

        Returns:
            StepEvaluation object
        """
        system_prompt = """You are an expert evaluator. Assess whether a task step was successful.

Provide your evaluation as JSON with this structure:
{
    "success": true/false,
    "score": 0.0-1.0,
    "reasoning": "Explanation of your evaluation",
    "issues": ["List of issues found"],
    "suggestions": ["List of suggestions for improvement"]
}"""

        user_prompt = f"""Step: {step_description}
Expected Outcome: {expected_outcome}
Actual Result: {json.dumps(actual_result, indent=2)}

Please evaluate this step."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = self.llm_client.chat_completion(messages=messages, temperature=0.3)
        content = self.llm_client.extract_message_content(response)

        try:
            # Parse JSON response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            eval_data = json.loads(content)

            return StepEvaluation(
                step_id=step_id,
                step_description=step_description,
                success=eval_data.get("success", False),
                score=eval_data.get("score", 0.0),
                reasoning=eval_data.get("reasoning", ""),
                issues=eval_data.get("issues", []),
                suggestions=eval_data.get("suggestions", [])
            )

        except (json.JSONDecodeError, KeyError):
            # Fallback evaluation based on actual_result
            success = actual_result.get("success", False)
            return StepEvaluation(
                step_id=step_id,
                step_description=step_description,
                success=success,
                score=1.0 if success else 0.0,
                reasoning="Automatic evaluation based on result status",
                issues=[] if success else [actual_result.get("error", "Unknown error")],
                suggestions=[]
            )

    def evaluate_final(
        self,
        goal: str,
        step_evaluations: List[StepEvaluation],
        final_output: Any
    ) -> FinalEvaluation:
        """Evaluate the final result of the entire task.

        Args:
            goal: The original goal
            step_evaluations: Evaluations of individual steps
            final_output: The final output

        Returns:
            FinalEvaluation object
        """
        # Calculate overall score
        if step_evaluations:
            overall_score = sum(e.score for e in step_evaluations) / len(step_evaluations)
        else:
            overall_score = 0.0

        overall_success = overall_score >= self.success_threshold

        # Use LLM for comprehensive final evaluation
        system_prompt = """You are an expert evaluator conducting a final assessment of a task execution.

Analyze the overall performance and provide insights as JSON:
{
    "summary": "Overall summary of the execution",
    "strengths": ["List of strengths"],
    "weaknesses": ["List of weaknesses"],
    "lessons_learned": ["Key lessons from this execution"]
}"""

        steps_summary = "\n".join([
            f"Step {e.step_id}: {e.step_description} - "
            f"{'Success' if e.success else 'Failed'} (Score: {e.score})"
            for e in step_evaluations
        ])

        user_prompt = f"""Goal: {goal}

Steps Executed:
{steps_summary}

Overall Score: {overall_score:.2f}

Final Output: {final_output}

Please provide a comprehensive final evaluation."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            response = self.llm_client.chat_completion(messages=messages, temperature=0.3)
            content = self.llm_client.extract_message_content(response)

            # Parse JSON response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            eval_data = json.loads(content)

            return FinalEvaluation(
                goal=goal,
                overall_success=overall_success,
                overall_score=overall_score,
                step_evaluations=step_evaluations,
                summary=eval_data.get("summary", ""),
                strengths=eval_data.get("strengths", []),
                weaknesses=eval_data.get("weaknesses", []),
                lessons_learned=eval_data.get("lessons_learned", [])
            )

        except (json.JSONDecodeError, KeyError):
            # Fallback evaluation
            return FinalEvaluation(
                goal=goal,
                overall_success=overall_success,
                overall_score=overall_score,
                step_evaluations=step_evaluations,
                summary=f"Task {'completed successfully' if overall_success else 'failed'} "
                        f"with an overall score of {overall_score:.2f}",
                strengths=["Task execution attempted"],
                weaknesses=[] if overall_success else ["Some steps failed"],
                lessons_learned=[]
            )

    def print_step_evaluation(self, evaluation: StepEvaluation):
        """Print a step evaluation in a readable format."""
        print(f"\n{'='*60}")
        print(f"Step {evaluation.step_id} Evaluation")
        print(f"{'='*60}")
        print(f"Description: {evaluation.step_description}")
        print(f"Success: {'✓' if evaluation.success else '✗'}")
        print(f"Score: {evaluation.score:.2f}")
        print(f"\nReasoning: {evaluation.reasoning}")

        if evaluation.issues:
            print(f"\nIssues:")
            for issue in evaluation.issues:
                print(f"  - {issue}")

        if evaluation.suggestions:
            print(f"\nSuggestions:")
            for suggestion in evaluation.suggestions:
                print(f"  - {suggestion}")

        print(f"{'='*60}\n")

    def print_final_evaluation(self, evaluation: FinalEvaluation):
        """Print a final evaluation in a readable format."""
        print(f"\n{'='*60}")
        print(f"FINAL EVALUATION")
        print(f"{'='*60}")
        print(f"Goal: {evaluation.goal}")
        print(f"Overall Success: {'✓' if evaluation.overall_success else '✗'}")
        print(f"Overall Score: {evaluation.overall_score:.2f}")
        print(f"\nSummary: {evaluation.summary}")

        if evaluation.strengths:
            print(f"\nStrengths:")
            for strength in evaluation.strengths:
                print(f"  + {strength}")

        if evaluation.weaknesses:
            print(f"\nWeaknesses:")
            for weakness in evaluation.weaknesses:
                print(f"  - {weakness}")

        if evaluation.lessons_learned:
            print(f"\nLessons Learned:")
            for lesson in evaluation.lessons_learned:
                print(f"  → {lesson}")

        print(f"\nStep Results:")
        for step_eval in evaluation.step_evaluations:
            status = "✓" if step_eval.success else "✗"
            print(f"  {status} Step {step_eval.step_id}: {step_eval.step_description} "
                  f"(Score: {step_eval.score:.2f})")

        print(f"{'='*60}\n")
