"""Memory management for the agent."""
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel


class Message(BaseModel):
    """A message in the conversation."""
    role: str  # 'system', 'user', 'assistant', 'tool'
    content: str
    timestamp: datetime = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None

    def __init__(self, **data):
        if 'timestamp' not in data or data['timestamp'] is None:
            data['timestamp'] = datetime.now()
        super().__init__(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls."""
        msg = {
            "role": self.role,
            "content": self.content
        }
        if self.tool_calls:
            msg["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            msg["tool_call_id"] = self.tool_call_id
        if self.name:
            msg["name"] = self.name
        return msg


class WorkingMemory:
    """Working memory for current task execution."""

    def __init__(self):
        self.messages: List[Message] = []
        self.context: Dict[str, Any] = {}

    def add_message(self, role: str, content: str, **kwargs):
        """Add a message to working memory."""
        message = Message(role=role, content=content, **kwargs)
        self.messages.append(message)

    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all messages in API format."""
        return [msg.to_dict() for msg in self.messages]

    def update_context(self, key: str, value: Any):
        """Update context information."""
        self.context[key] = value

    def get_context(self, key: str) -> Any:
        """Get context information."""
        return self.context.get(key)

    def clear(self):
        """Clear working memory."""
        self.messages.clear()
        self.context.clear()


class LongTermMemory:
    """Long-term memory for storing task history and learnings."""

    def __init__(self):
        self.task_history: List[Dict[str, Any]] = []
        self.learnings: Dict[str, Any] = {}

    def save_task(self, task: Dict[str, Any]):
        """Save a completed task to history."""
        task['completed_at'] = datetime.now().isoformat()
        self.task_history.append(task)

    def get_recent_tasks(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get the n most recent tasks."""
        return self.task_history[-n:]

    def add_learning(self, key: str, value: Any):
        """Add a learning to long-term memory."""
        self.learnings[key] = value

    def get_learning(self, key: str) -> Any:
        """Retrieve a learning."""
        return self.learnings.get(key)
