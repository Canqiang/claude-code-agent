"""Thinking module for reasoning and reflection."""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from .utils.llm_client import AzureOpenAIClient


class Thought(BaseModel):
    """A single thought in the reasoning process."""
    content: str
    type: str  # observation, reasoning, reflection, decision
    timestamp: str


class ThinkingModule:
    """Module for explicit reasoning and reflection."""

    def __init__(self, llm_client: AzureOpenAIClient, verbose: bool = True):
        """Initialize the thinking module.

        Args:
            llm_client: Azure OpenAI client
            verbose: Whether to output thinking process
        """
        self.llm_client = llm_client
        self.verbose = verbose
        self.thoughts: List[Thought] = []

    def think(
        self,
        context: str,
        question: str,
        thinking_type: str = "reasoning"
    ) -> str:
        """Generate a thought about the current situation.

        Args:
            context: Current context
            question: Question to think about
            thinking_type: Type of thinking (reasoning, reflection, decision)

        Returns:
            The thought content
        """
        prompts = {
            "reasoning": """You are thinking through a problem step by step. Analyze the situation logically and explain your reasoning.""",
            "reflection": """You are reflecting on what has happened. Consider what went well, what didn't, and what can be learned.""",
            "decision": """You are making a decision. Consider the options, their pros and cons, and choose the best path forward.""",
            "observation": """You are observing the current state. What do you notice? What is important?"""
        }

        system_prompt = prompts.get(thinking_type, prompts["reasoning"])
        system_prompt += "\n\nThink aloud and be explicit about your reasoning process."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
        ]

        response = self.llm_client.chat_completion(
            messages=messages,
            temperature=0.7
        )

        thought_content = self.llm_client.extract_message_content(response)

        # Record the thought
        from datetime import datetime
        thought = Thought(
            content=thought_content,
            type=thinking_type,
            timestamp=datetime.now().isoformat()
        )
        self.thoughts.append(thought)

        if self.verbose:
            print(f"\n[{thinking_type.upper()}]")
            print(f"{thought_content}\n")

        return thought_content

    def reflect_on_action(
        self,
        action: str,
        result: Dict[str, Any],
        expected_outcome: str
    ) -> str:
        """Reflect on the result of an action.

        Args:
            action: The action that was taken
            result: The result of the action
            expected_outcome: What was expected

        Returns:
            Reflection content
        """
        context = f"""Action taken: {action}
Expected outcome: {expected_outcome}
Actual result: {result}"""

        question = "Did this action achieve what we wanted? What should we do next?"

        return self.think(context, question, thinking_type="reflection")

    def analyze_failure(
        self,
        task: str,
        error: str,
        attempts: int
    ) -> str:
        """Analyze why a task failed.

        Args:
            task: The task that failed
            error: The error message
            attempts: Number of attempts made

        Returns:
            Analysis content
        """
        context = f"""Task: {task}
Error: {error}
Attempts made: {attempts}"""

        question = "Why did this fail? What are the root causes? How can we fix it?"

        return self.think(context, question, thinking_type="reasoning")

    def make_decision(
        self,
        situation: str,
        options: List[str]
    ) -> str:
        """Make a decision between options.

        Args:
            situation: Current situation
            options: Available options

        Returns:
            Decision and reasoning
        """
        context = f"""Situation: {situation}
Available options:
{chr(10).join(f"{i+1}. {opt}" for i, opt in enumerate(options))}"""

        question = "Which option should we choose and why?"

        return self.think(context, question, thinking_type="decision")

    def get_thoughts_summary(self) -> str:
        """Get a summary of all thoughts.

        Returns:
            Summary of thinking process
        """
        if not self.thoughts:
            return "No thoughts recorded yet."

        summary = "Thinking Process Summary:\n\n"
        for i, thought in enumerate(self.thoughts, 1):
            summary += f"{i}. [{thought.type}] {thought.content[:100]}...\n"

        return summary

    def clear_thoughts(self):
        """Clear all recorded thoughts."""
        self.thoughts.clear()
