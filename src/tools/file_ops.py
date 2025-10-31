"""File operation tools."""
import os
from typing import Dict, Any, List
from .base import Tool, ToolParameter


class FileReadTool(Tool):
    """Tool for reading files."""

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read the contents of a file from the filesystem"

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="file_path",
                type="string",
                description="The path to the file to read",
                required=True
            )
        ]

    def execute(self, **kwargs) -> Dict[str, Any]:
        file_path = kwargs.get("file_path")

        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                "success": True,
                "result": {
                    "file_path": file_path,
                    "content": content,
                    "size": len(content)
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error reading file: {str(e)}"
            }


class FileWriteTool(Tool):
    """Tool for writing files."""

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Write content to a file on the filesystem"

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="file_path",
                type="string",
                description="The path to the file to write",
                required=True
            ),
            ToolParameter(
                name="content",
                type="string",
                description="The content to write to the file",
                required=True
            )
        ]

    def execute(self, **kwargs) -> Dict[str, Any]:
        file_path = kwargs.get("file_path")
        content = kwargs.get("content")

        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                "success": True,
                "result": {
                    "file_path": file_path,
                    "bytes_written": len(content.encode('utf-8'))
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error writing file: {str(e)}"
            }


class FileListTool(Tool):
    """Tool for listing files in a directory."""

    @property
    def name(self) -> str:
        return "list_files"

    @property
    def description(self) -> str:
        return "List files and directories in a given path"

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="directory_path",
                type="string",
                description="The directory path to list files from",
                required=True
            )
        ]

    def execute(self, **kwargs) -> Dict[str, Any]:
        directory_path = kwargs.get("directory_path")

        try:
            if not os.path.exists(directory_path):
                return {
                    "success": False,
                    "error": f"Directory not found: {directory_path}"
                }

            if not os.path.isdir(directory_path):
                return {
                    "success": False,
                    "error": f"Not a directory: {directory_path}"
                }

            items = os.listdir(directory_path)
            files = []
            directories = []

            for item in items:
                full_path = os.path.join(directory_path, item)
                if os.path.isfile(full_path):
                    files.append(item)
                elif os.path.isdir(full_path):
                    directories.append(item)

            return {
                "success": True,
                "result": {
                    "directory_path": directory_path,
                    "files": files,
                    "directories": directories,
                    "total_items": len(items)
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error listing directory: {str(e)}"
            }
