"""Code execution tools."""
import subprocess
import sys
from typing import Dict, Any, List
from .base import Tool, ToolParameter


class PythonExecuteTool(Tool):
    """Tool for executing Python code."""

    @property
    def name(self) -> str:
        return "execute_python"

    @property
    def description(self) -> str:
        return "Execute Python code and return the output"

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="code",
                type="string",
                description="The Python code to execute",
                required=True
            ),
            ToolParameter(
                name="timeout",
                type="number",
                description="Timeout in seconds (default: 30)",
                required=False
            )
        ]

    def execute(self, **kwargs) -> Dict[str, Any]:
        code = kwargs.get("code")
        timeout = kwargs.get("timeout", 30)

        try:
            # Execute code in a subprocess for safety
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                "success": result.returncode == 0,
                "result": {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode
                }
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Code execution timed out after {timeout} seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing code: {str(e)}"
            }
