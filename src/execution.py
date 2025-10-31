"""Execution engine for running tasks with tools."""
import json
from typing import List, Dict, Any, Optional
from .utils.llm_client import AzureOpenAIClient
from .tools.base import ToolRegistry
from .thinking import ThinkingModule


class ExecutionResult:
    """Result of executing a task."""

    def __init__(
        self,
        success: bool,
        output: Any,
        error: Optional[str] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None
    ):
        self.success = success
        self.output = output
        self.error = error
        self.tool_calls = tool_calls or []


class ExecutionEngine:
    """Engine for executing tasks using tools and LLM."""

    def __init__(
        self,
        llm_client: AzureOpenAIClient,
        tool_registry: ToolRegistry,
        thinking_module: Optional[ThinkingModule] = None,
        max_iterations: int = 10
    ):
        """Initialize the execution engine.

        Args:
            llm_client: Azure OpenAI client
            tool_registry: Registry of available tools
            thinking_module: Optional thinking module
            max_iterations: Maximum iterations per task
        """
        self.llm_client = llm_client
        self.tool_registry = tool_registry
        self.thinking_module = thinking_module
        self.max_iterations = max_iterations

    def execute_task(
        self,
        task_description: str,
        context: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None
    ) -> ExecutionResult:
        """Execute a task using available tools.

        Args:
            task_description: Description of the task
            context: Additional context
            messages: Existing message history

        Returns:
            ExecutionResult
        """
        # Initialize messages
        if messages is None:
            messages = []

        if not messages:
            system_prompt = """You are a capable AI agent that can use tools to accomplish tasks.

When you need to use a tool:
1. Think about which tool would be most appropriate
2. Call the tool with the correct parameters
3. Analyze the result
4. Decide on the next action

You can use multiple tools in sequence to accomplish complex tasks. Always provide a final answer when the task is complete."""

            messages.append({"role": "system", "content": system_prompt})

            user_message = f"Task: {task_description}"
            if context:
                user_message += f"\n\nContext: {context}"

            messages.append({"role": "user", "content": user_message})

        # Think about the task if thinking module is available
        if self.thinking_module:
            thought = self.thinking_module.think(
                context=context or "Starting new task",
                question=f"How should I approach this task: {task_description}?",
                thinking_type="reasoning"
            )

        # Execution loop
        iterations = 0
        tool_calls_made = []

        while iterations < self.max_iterations:
            iterations += 1

            # Get response from LLM
            response = self.llm_client.chat_completion(
                messages=messages,
                tools=self.tool_registry.to_openai_format()
            )

            message = response.choices[0].message
            finish_reason = response.choices[0].finish_reason

            # Add assistant message to history
            assistant_message = {"role": "assistant", "content": message.content or ""}

            # Check if there are tool calls
            tool_calls = self.llm_client.extract_tool_calls(response)

            if tool_calls:
                assistant_message["tool_calls"] = tool_calls
                messages.append(assistant_message)

                # Execute each tool call
                for tool_call in tool_calls:
                    tool_name = tool_call["function"]["name"]
                    tool_args_str = tool_call["function"]["arguments"]

                    try:
                        tool_args = json.loads(tool_args_str)
                    except json.JSONDecodeError:
                        tool_args = {}

                    # Get and execute the tool
                    tool = self.tool_registry.get(tool_name)

                    if tool:
                        print(f"\n[Executing tool: {tool_name}]")
                        print(f"Arguments: {tool_args}")

                        result = tool.execute(**tool_args)
                        tool_calls_made.append({
                            "tool": tool_name,
                            "args": tool_args,
                            "result": result
                        })

                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "name": tool_name,
                            "content": json.dumps(result)
                        })

                        print(f"Result: {result}\n")

                        # Reflect on the tool result if thinking module is available
                        if self.thinking_module and result.get("success"):
                            self.thinking_module.reflect_on_action(
                                action=f"Used {tool_name} with {tool_args}",
                                result=result,
                                expected_outcome="Successfully execute the tool"
                            )

                    else:
                        # Tool not found
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "name": tool_name,
                            "content": json.dumps({
                                "success": False,
                                "error": f"Tool '{tool_name}' not found"
                            })
                        })

            else:
                # No more tool calls, task is complete
                messages.append(assistant_message)

                if finish_reason == "stop":
                    return ExecutionResult(
                        success=True,
                        output=message.content,
                        tool_calls=tool_calls_made
                    )

        # Max iterations reached
        return ExecutionResult(
            success=False,
            output="Max iterations reached",
            error="Task execution exceeded maximum iterations",
            tool_calls=tool_calls_made
        )
