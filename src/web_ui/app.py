"""FastAPI web application for Agent Dashboard."""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import asyncio
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agent import GeneralPurposeAgent
from src.streaming import StreamHandler, StreamEvent, StreamEventType
from src.collaboration import AgentOrchestrator

app = FastAPI(title="Agent Dashboard", version="1.0.0")

# Setup templates and static files
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


class TaskRequest(BaseModel):
    """Request model for tasks."""
    goal: str
    config: Optional[Dict[str, Any]] = None
    use_collaboration: bool = False


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass


manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render home page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.post("/api/run")
async def run_task(task: TaskRequest):
    """Run a task with the agent."""
    try:
        agent = GeneralPurposeAgent(
            config=task.config,
            verbose=False
        )

        evaluation = agent.run(task.goal)

        return {
            "success": evaluation.overall_success,
            "score": evaluation.overall_score,
            "summary": evaluation.summary,
            "evaluation": {
                "overall_success": evaluation.overall_success,
                "overall_score": evaluation.overall_score,
                "strengths": evaluation.strengths,
                "weaknesses": evaluation.weaknesses,
                "lessons_learned": evaluation.lessons_learned
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/stream/{goal}")
async def stream_task(goal: str):
    """Stream task execution with Server-Sent Events."""

    async def event_generator():
        try:
            stream_handler = StreamHandler()

            # Emit start
            stream_handler.emit_start(goal)
            for event in stream_handler.get_history():
                yield event.to_sse()
                await asyncio.sleep(0.1)

            # Create and run agent
            agent = GeneralPurposeAgent(verbose=False)

            # Emit planning
            stream_handler.emit_progress("Creating plan...", 20)
            yield stream_handler.get_history()[-1].to_sse()
            await asyncio.sleep(0.1)

            # Run agent (in practice, you'd integrate streaming into the agent)
            evaluation = agent.run(goal)

            # Emit progress updates
            stream_handler.emit_progress("Executing tasks...", 60)
            yield stream_handler.get_history()[-1].to_sse()
            await asyncio.sleep(0.1)

            stream_handler.emit_progress("Evaluating results...", 90)
            yield stream_handler.get_history()[-1].to_sse()
            await asyncio.sleep(0.1)

            # Emit completion
            stream_handler.emit_complete({
                "success": evaluation.overall_success,
                "score": evaluation.overall_score,
                "summary": evaluation.summary
            })
            yield stream_handler.get_history()[-1].to_sse()

        except Exception as e:
            error_event = StreamEvent(
                type=StreamEventType.ERROR,
                data={'error': str(e)}
            )
            yield error_event.to_sse()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await manager.connect(websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get('type') == 'run_task':
                goal = message.get('goal')

                # Send start event
                await websocket.send_json({
                    'type': 'start',
                    'data': {'goal': goal}
                })

                try:
                    # Run agent
                    agent = GeneralPurposeAgent(verbose=False)

                    # Send progress updates
                    await websocket.send_json({
                        'type': 'progress',
                        'data': {'message': 'Planning...', 'percentage': 20}
                    })

                    evaluation = agent.run(goal)

                    await websocket.send_json({
                        'type': 'progress',
                        'data': {'message': 'Executing...', 'percentage': 60}
                    })

                    await websocket.send_json({
                        'type': 'progress',
                        'data': {'message': 'Evaluating...', 'percentage': 90}
                    })

                    # Send result
                    await websocket.send_json({
                        'type': 'complete',
                        'data': {
                            'success': evaluation.overall_success,
                            'score': evaluation.overall_score,
                            'summary': evaluation.summary,
                            'strengths': evaluation.strengths,
                            'weaknesses': evaluation.weaknesses
                        }
                    })

                except Exception as e:
                    await websocket.send_json({
                        'type': 'error',
                        'data': {'error': str(e)}
                    })

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/api/collaboration/run")
async def run_collaboration(goal: str):
    """Run multi-agent collaboration."""
    try:
        # Create agents
        from src.utils.llm_client import AzureOpenAIClient
        from src.planning import PlanningModule
        from src.execution import ExecutionEngine
        from src.evaluation import EvaluationModule
        from src.tools.base import ToolRegistry
        from src.tools import FileReadTool, FileWriteTool
        from src.collaboration import (
            AgentOrchestrator,
            PlannerAgent,
            ExecutorAgent,
            ReviewerAgent,
            AgentRole
        )

        llm_client = AzureOpenAIClient()
        tool_registry = ToolRegistry()
        tool_registry.register(FileReadTool())
        tool_registry.register(FileWriteTool())

        # Create orchestrator
        orchestrator = AgentOrchestrator(verbose=False)

        # Create specialized agents
        planner = PlannerAgent(PlanningModule(llm_client))
        executor = ExecutorAgent(ExecutionEngine(llm_client, tool_registry))
        reviewer = ReviewerAgent(EvaluationModule(llm_client))

        # Register agents
        orchestrator.register_agent('planner', planner, AgentRole.PLANNER)
        orchestrator.register_agent('executor', executor, AgentRole.EXECUTOR)
        orchestrator.register_agent('reviewer', reviewer, AgentRole.REVIEWER)

        # Run collaboration
        result = orchestrator.collaborate(goal)

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
