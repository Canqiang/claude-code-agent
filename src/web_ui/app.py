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


def is_azure_openai_configured() -> bool:
    """
    Check if Azure OpenAI is properly configured.
    
    Returns:
        bool: True if all required environment variables are set, False otherwise.
    """
    import os
    
    has_api_key = bool(os.getenv('AZURE_OPENAI_API_KEY'))
    has_endpoint = bool(os.getenv('AZURE_OPENAI_ENDPOINT'))
    has_deployment = bool(os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'))
    
    return has_api_key and has_endpoint and has_deployment


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render chat page (default)."""
    return templates.TemplateResponse("chat.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render dashboard page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    """Render chat page."""
    return templates.TemplateResponse("chat.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    import os

    # Check if environment variables are set
    has_api_key = bool(os.getenv('AZURE_OPENAI_API_KEY'))
    has_endpoint = bool(os.getenv('AZURE_OPENAI_ENDPOINT'))
    has_deployment = bool(os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'))

    is_configured = is_azure_openai_configured()

    return {
        "status": "healthy",
        "version": "1.0.0",
        "configured": is_configured,
        "environment": {
            "has_api_key": has_api_key,
            "has_endpoint": has_endpoint,
            "has_deployment": has_deployment
        }
    }


@app.post("/api/run")
async def run_task(task: TaskRequest):
    """Run a task with the agent."""
    try:
        # Check if configured
        is_configured = is_azure_openai_configured()

        if not is_configured:
            # Return demo response
            return {
                "success": True,
                "score": 0.85,
                "summary": "Demo mode: Azure OpenAI not configured. This is a simulated response.",
                "evaluation": {
                    "overall_success": True,
                    "overall_score": 0.85,
                    "strengths": [
                        "Demo mode is working correctly",
                        "UI is responsive and functional"
                    ],
                    "weaknesses": [
                        "Azure OpenAI credentials not configured",
                        "Cannot execute real tasks"
                    ],
                    "lessons_learned": [
                        "Configure .env file with Azure OpenAI credentials to enable real functionality"
                    ]
                },
                "demo_mode": True
            }

        # Real execution
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
            },
            "demo_mode": False
        }
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


@app.get("/api/stream/{goal}")
async def stream_task(goal: str):
    """Stream task execution with Server-Sent Events."""
    async def event_generator():
        try:
            from src.utils.query_classifier import QueryClassifier

            stream_handler = StreamHandler()
            is_configured = is_azure_openai_configured()

            # Emit start
            stream_handler.emit_start(goal)
            for event in stream_handler.get_history():
                yield event.to_sse()
                await asyncio.sleep(0.1)

            # Classify query to determine response strategy using LLM
            from src.utils.llm_client import AzureOpenAIClient

            llm_client = None
            if is_configured:
                try:
                    llm_client = AzureOpenAIClient()
                except Exception as e:
                    print(f"Failed to initialize LLM client for classification: {e}")

            classifier = QueryClassifier(llm_client=llm_client)
            classification = classifier.classify(goal)

            # Handle simple queries with quick responses
            if not classification["use_full_workflow"]:
                quick_response = classifier.get_quick_response(goal, classification)

                if quick_response:
                    # Direct response without full workflow
                    stream_handler.emit_complete({
                        "success": True,
                        "score": 1.0,
                        "summary": quick_response,
                        "quick_response": True,
                        "query_type": classification["type"].value
                    })
                    yield stream_handler.get_history()[-1].to_sse()
                    return

            if not is_configured:
                # Demo mode
                stream_handler.emit_planning("Demo mode: Planning task...")
                yield stream_handler.get_history()[-1].to_sse()
                await asyncio.sleep(0.5)

                stream_handler.emit_progress("Demo mode: Simulating execution...", 30)
                yield stream_handler.get_history()[-1].to_sse()
                await asyncio.sleep(0.5)

                stream_handler.emit_execution("Demo mode: Processing...", 50)
                yield stream_handler.get_history()[-1].to_sse()
                await asyncio.sleep(0.5)

                stream_handler.emit_progress("Demo mode: Almost done...", 70)
                yield stream_handler.get_history()[-1].to_sse()
                await asyncio.sleep(0.5)

                stream_handler.emit_evaluation({"score": 0.85, "success": True})
                yield stream_handler.get_history()[-1].to_sse()
                await asyncio.sleep(0.5)

                stream_handler.emit_complete({
                    "success": True,
                    "score": 0.85,
                    "summary": "Demo mode: Azure OpenAI not configured. Configure .env to enable real functionality.",
                    "demo_mode": True
                })
                yield stream_handler.get_history()[-1].to_sse()
            else:
                # Real execution - run in executor to avoid blocking
                import concurrent.futures

                stream_handler.emit_planning("Creating execution plan...")
                yield stream_handler.get_history()[-1].to_sse()
                await asyncio.sleep(0.3)

                stream_handler.emit_progress("Initializing agent...", 10)
                yield stream_handler.get_history()[-1].to_sse()
                await asyncio.sleep(0.3)

                stream_handler.emit_thinking("Analyzing task requirements...")
                yield stream_handler.get_history()[-1].to_sse()
                await asyncio.sleep(0.3)

                stream_handler.emit_progress("Planning approach...", 30)
                yield stream_handler.get_history()[-1].to_sse()
                await asyncio.sleep(0.3)

                # Run agent in executor to avoid blocking the event loop
                def run_agent():
                    agent = GeneralPurposeAgent(verbose=False)
                    return agent.run(goal)

                stream_handler.emit_execution("Executing task...", 60)
                yield stream_handler.get_history()[-1].to_sse()
                await asyncio.sleep(0.3)

                stream_handler.emit_progress("Running agent...", 50)
                yield stream_handler.get_history()[-1].to_sse()

                # Execute in thread pool
                loop = asyncio.get_event_loop()
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    evaluation = await loop.run_in_executor(executor, run_agent)

                stream_handler.emit_progress("Task completed, evaluating...", 80)
                yield stream_handler.get_history()[-1].to_sse()
                await asyncio.sleep(0.3)

                stream_handler.emit_evaluation({
                    "score": evaluation.overall_score,
                    "success": evaluation.overall_success
                })
                yield stream_handler.get_history()[-1].to_sse()
                await asyncio.sleep(0.3)

                # Build comprehensive response
                response_summary = evaluation.summary

                if evaluation.strengths:
                    response_summary += "\n\n**Strengths:**\n"
                    for strength in evaluation.strengths:
                        response_summary += f"- {strength}\n"

                if evaluation.weaknesses:
                    response_summary += "\n\n**Areas for Improvement:**\n"
                    for weakness in evaluation.weaknesses:
                        response_summary += f"- {weakness}\n"

                stream_handler.emit_complete({
                    "success": evaluation.overall_success,
                    "score": evaluation.overall_score,
                    "summary": response_summary
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
                    # Check if configured
                    is_configured = is_azure_openai_configured()

                    if not is_configured:
                        # Demo mode
                        await websocket.send_json({
                            'type': 'progress',
                            'data': {'message': 'Demo mode: Planning...', 'percentage': 20}
                        })

                        await asyncio.sleep(0.5)

                        await websocket.send_json({
                            'type': 'progress',
                            'data': {'message': 'Demo mode: Executing...', 'percentage': 60}
                        })

                        await asyncio.sleep(0.5)

                        await websocket.send_json({
                            'type': 'progress',
                            'data': {'message': 'Demo mode: Evaluating...', 'percentage': 90}
                        })

                        await asyncio.sleep(0.5)

                        # Send demo result
                        await websocket.send_json({
                            'type': 'complete',
                            'data': {
                                'success': True,
                                'score': 0.85,
                                'summary': 'Demo mode: Azure OpenAI not configured. This is a simulated response. Configure .env to enable real functionality.',
                                'strengths': ['Demo mode working correctly', 'UI is responsive and functional'],
                                'weaknesses': ['Azure OpenAI credentials not configured', 'Cannot execute real tasks'],
                                'demo_mode': True
                            }
                        })
                    else:
                        # Real execution
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
                                'weaknesses': evaluation.weaknesses,
                                'demo_mode': False
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
        is_configured = is_azure_openai_configured()

        if not is_configured:
            # Demo mode
            return {
                "success": True,
                "result": {
                    "goal": goal,
                    "plan": {
                        "subtasks": [
                            {"id": 1, "description": "Demo: Analyze requirements", "status": "completed"},
                            {"id": 2, "description": "Demo: Design solution", "status": "completed"},
                            {"id": 3, "description": "Demo: Implement solution", "status": "completed"}
                        ]
                    },
                    "output": "Demo mode: Multi-agent collaboration completed successfully. Configure Azure OpenAI to enable real functionality.",
                    "evaluation": {
                        "overall_score": 0.85,
                        "overall_success": True,
                        "strengths": ["Demo mode working", "UI functional"],
                        "weaknesses": ["Azure OpenAI not configured"]
                    }
                },
                "demo_mode": True
            }

        # Real execution
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
            "result": result,
            "demo_mode": False
        }

    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
