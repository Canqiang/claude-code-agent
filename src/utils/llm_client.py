"""Azure OpenAI Client for LLM interactions."""
import os
from typing import List, Dict, Any, Optional
from openai import AzureOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential


class AzureOpenAIClient:
    """Client for interacting with Azure OpenAI GPT models."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        deployment_name: Optional[str] = None,
        api_version: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        """Initialize Azure OpenAI client.

        Args:
            api_key: Azure OpenAI API key
            endpoint: Azure OpenAI endpoint URL
            deployment_name: Deployment name
            api_version: API version
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        """
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = deployment_name or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        self.temperature = temperature
        self.max_tokens = max_tokens

        if not all([self.api_key, self.endpoint, self.deployment_name]):
            raise ValueError(
                "Missing required Azure OpenAI credentials. "
                "Set AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_DEPLOYMENT_NAME"
            )

        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate chat completion.

        Args:
            messages: List of message dictionaries
            temperature: Override default temperature
            max_tokens: Override default max tokens
            tools: Optional list of tool definitions
            tool_choice: Tool choice strategy ('auto', 'none', or specific tool)

        Returns:
            Response dictionary from Azure OpenAI
        """
        kwargs = {
            "model": self.deployment_name,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice or "auto"

        response = self.client.chat.completions.create(**kwargs)
        return response

    def extract_message_content(self, response: Any) -> str:
        """Extract text content from response.

        Args:
            response: Azure OpenAI response

        Returns:
            Extracted text content
        """
        return response.choices[0].message.content or ""

    def extract_tool_calls(self, response: Any) -> List[Dict[str, Any]]:
        """Extract tool calls from response.

        Args:
            response: Azure OpenAI response

        Returns:
            List of tool call dictionaries
        """
        message = response.choices[0].message
        if not hasattr(message, 'tool_calls') or not message.tool_calls:
            return []

        tool_calls = []
        for tool_call in message.tool_calls:
            tool_calls.append({
                "id": tool_call.id,
                "type": tool_call.type,
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments
                }
            })
        return tool_calls
