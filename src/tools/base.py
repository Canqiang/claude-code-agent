"""Base classes for tools."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    """Tool parameter definition."""
    name: str
    type: str
    description: str
    required: bool = True
    enum: Optional[List[str]] = None


class Tool(ABC):
    """Base class for all tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass

    @property
    @abstractmethod
    def parameters(self) -> List[ToolParameter]:
        """Tool parameters."""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool.

        Returns:
            Dictionary with 'success' boolean and 'result' or 'error' key
        """
        pass

    def to_openai_format(self) -> Dict[str, Any]:
        """Convert tool definition to OpenAI function calling format."""
        properties = {}
        required = []

        for param in self.parameters:
            param_def = {
                "type": param.type,
                "description": param.description
            }
            if param.enum:
                param_def["enum"] = param.enum

            properties[param.name] = param_def
            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }


class ToolRegistry:
    """Registry for managing available tools."""

    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        """Register a tool."""
        self.tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(name)

    def get_all(self) -> List[Tool]:
        """Get all registered tools."""
        return list(self.tools.values())

    def to_openai_format(self) -> List[Dict[str, Any]]:
        """Convert all tools to OpenAI format."""
        return [tool.to_openai_format() for tool in self.tools.values()]
