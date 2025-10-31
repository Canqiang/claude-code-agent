"""Streaming response handler for real-time updates."""
from enum import Enum
from typing import Generator, Callable, Any, Optional, Dict
from dataclasses import dataclass, field
from datetime import datetime
import json


class StreamEventType(Enum):
    """Types of streaming events."""
    START = "start"
    PLANNING = "planning"
    THINKING = "thinking"
    EXECUTION = "execution"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    EVALUATION = "evaluation"
    PROGRESS = "progress"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class StreamEvent:
    """Event in the streaming process."""
    type: StreamEventType
    data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'type': self.type.value,
            'data': self.data,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())

    def to_sse(self) -> str:
        """Convert to Server-Sent Events format."""
        return f"data: {self.to_json()}\n\n"


class StreamHandler:
    """Handler for streaming agent responses."""

    def __init__(self):
        """Initialize stream handler."""
        self.subscribers: list[Callable[[StreamEvent], None]] = []
        self.event_history: list[StreamEvent] = []

    def subscribe(self, callback: Callable[[StreamEvent], None]):
        """Subscribe to stream events.

        Args:
            callback: Function to call with each event
        """
        self.subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[StreamEvent], None]):
        """Unsubscribe from stream events.

        Args:
            callback: Function to remove
        """
        if callback in self.subscribers:
            self.subscribers.remove(callback)

    def emit(self, event: StreamEvent):
        """Emit an event to all subscribers.

        Args:
            event: StreamEvent to emit
        """
        self.event_history.append(event)

        for callback in self.subscribers:
            try:
                callback(event)
            except Exception as e:
                print(f"Error in subscriber callback: {e}")

    def stream_generator(self) -> Generator[StreamEvent, None, None]:
        """Generate stream events as they occur.

        Yields:
            StreamEvent objects
        """
        for event in self.event_history:
            yield event

    def clear_history(self):
        """Clear event history."""
        self.event_history.clear()

    def get_history(self) -> list[StreamEvent]:
        """Get event history.

        Returns:
            List of StreamEvents
        """
        return self.event_history.copy()

    def emit_start(self, goal: str):
        """Emit start event."""
        self.emit(StreamEvent(
            type=StreamEventType.START,
            data={'goal': goal}
        ))

    def emit_planning(self, plan_data: Dict[str, Any]):
        """Emit planning event."""
        self.emit(StreamEvent(
            type=StreamEventType.PLANNING,
            data=plan_data
        ))

    def emit_thinking(self, thought: str):
        """Emit thinking event."""
        self.emit(StreamEvent(
            type=StreamEventType.THINKING,
            data={'thought': thought}
        ))

    def emit_execution(self, task: str, progress: float):
        """Emit execution event."""
        self.emit(StreamEvent(
            type=StreamEventType.EXECUTION,
            data={'task': task, 'progress': progress}
        ))

    def emit_tool_call(self, tool_name: str, args: Dict[str, Any]):
        """Emit tool call event."""
        self.emit(StreamEvent(
            type=StreamEventType.TOOL_CALL,
            data={'tool': tool_name, 'arguments': args}
        ))

    def emit_tool_result(self, tool_name: str, result: Any):
        """Emit tool result event."""
        self.emit(StreamEvent(
            type=StreamEventType.TOOL_RESULT,
            data={'tool': tool_name, 'result': result}
        ))

    def emit_evaluation(self, evaluation_data: Dict[str, Any]):
        """Emit evaluation event."""
        self.emit(StreamEvent(
            type=StreamEventType.EVALUATION,
            data=evaluation_data
        ))

    def emit_progress(self, message: str, percentage: float):
        """Emit progress event."""
        self.emit(StreamEvent(
            type=StreamEventType.PROGRESS,
            data={'message': message, 'percentage': percentage}
        ))

    def emit_complete(self, result: Any):
        """Emit completion event."""
        self.emit(StreamEvent(
            type=StreamEventType.COMPLETE,
            data={'result': result}
        ))

    def emit_error(self, error: str):
        """Emit error event."""
        self.emit(StreamEvent(
            type=StreamEventType.ERROR,
            data={'error': error}
        ))


class StreamingAgent:
    """Agent wrapper with streaming support."""

    def __init__(self, agent: Any, stream_handler: Optional[StreamHandler] = None):
        """Initialize streaming agent.

        Args:
            agent: Base agent instance
            stream_handler: StreamHandler instance
        """
        self.agent = agent
        self.stream_handler = stream_handler or StreamHandler()

    def run_streaming(self, goal: str, **kwargs) -> Generator[StreamEvent, None, Any]:
        """Run agent with streaming updates.

        Args:
            goal: Goal to achieve
            **kwargs: Additional arguments

        Yields:
            StreamEvent objects as they occur
        """
        self.stream_handler.clear_history()
        self.stream_handler.emit_start(goal)
        yield from self.stream_handler.stream_generator()

        try:
            # Run agent
            result = self.agent.run(goal, **kwargs)

            self.stream_handler.emit_complete(result)
            yield from self.stream_handler.stream_generator()

            return result

        except Exception as e:
            self.stream_handler.emit_error(str(e))
            yield from self.stream_handler.stream_generator()
            raise
