"""Multi-agent orchestration system."""
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import asyncio


class AgentRole(Enum):
    """Roles for specialized agents."""
    PLANNER = "planner"
    EXECUTOR = "executor"
    REVIEWER = "reviewer"
    COORDINATOR = "coordinator"


@dataclass
class AgentMessage:
    """Message passed between agents."""
    from_agent: str
    to_agent: str
    role: AgentRole
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class AgentOrchestrator:
    """Orchestrator for managing multiple agents in collaboration."""

    def __init__(self, verbose: bool = True):
        """Initialize the orchestrator.

        Args:
            verbose: Whether to print collaboration details
        """
        self.verbose = verbose
        self.agents: Dict[str, Any] = {}
        self.message_history: List[AgentMessage] = []
        self.callbacks: Dict[str, List[Callable]] = {}

    def register_agent(self, name: str, agent: Any, role: AgentRole):
        """Register an agent with the orchestrator.

        Args:
            name: Agent identifier
            agent: Agent instance
            role: Agent role
        """
        self.agents[name] = {
            'instance': agent,
            'role': role,
            'status': 'idle'
        }

        if self.verbose:
            print(f"[Orchestrator] Registered agent '{name}' with role {role.value}")

    def send_message(self, message: AgentMessage):
        """Send a message between agents.

        Args:
            message: AgentMessage to send
        """
        self.message_history.append(message)

        if self.verbose:
            print(f"\n[Message] {message.from_agent} → {message.to_agent}")
            print(f"Role: {message.role.value}")
            print(f"Content: {message.content[:100]}...")

    def collaborate(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a collaborative task with multiple agents.

        Args:
            goal: The goal to achieve
            context: Additional context

        Returns:
            Result dictionary with outputs from all agents
        """
        if self.verbose:
            print(f"\n{'='*70}")
            print(f"MULTI-AGENT COLLABORATION")
            print(f"Goal: {goal}")
            print(f"{'='*70}\n")

        results = {}

        # Phase 1: Planning
        if 'planner' in self.agents:
            planner = self.agents['planner']['instance']
            self.agents['planner']['status'] = 'active'

            if self.verbose:
                print("\n[Phase 1: Planning]")

            plan_result = planner.create_plan(goal, context)
            results['plan'] = plan_result

            # Send plan to other agents
            message = AgentMessage(
                from_agent='planner',
                to_agent='all',
                role=AgentRole.PLANNER,
                content=f"Plan created with {len(plan_result.subtasks)} subtasks",
                metadata={'plan': plan_result.dict()}
            )
            self.send_message(message)

            self.agents['planner']['status'] = 'idle'

        # Phase 2: Execution
        if 'executor' in self.agents:
            executor = self.agents['executor']['instance']
            self.agents['executor']['status'] = 'active'

            if self.verbose:
                print("\n[Phase 2: Execution]")

            exec_result = executor.execute_plan(results.get('plan'), context)
            results['execution'] = exec_result

            # Send execution result
            message = AgentMessage(
                from_agent='executor',
                to_agent='reviewer',
                role=AgentRole.EXECUTOR,
                content="Execution completed",
                metadata={'result': exec_result}
            )
            self.send_message(message)

            self.agents['executor']['status'] = 'idle'

        # Phase 3: Review
        if 'reviewer' in self.agents:
            reviewer = self.agents['reviewer']['instance']
            self.agents['reviewer']['status'] = 'active'

            if self.verbose:
                print("\n[Phase 3: Review]")

            review_result = reviewer.review_execution(
                results.get('plan'),
                results.get('execution')
            )
            results['review'] = review_result

            # Send review result
            message = AgentMessage(
                from_agent='reviewer',
                to_agent='coordinator',
                role=AgentRole.REVIEWER,
                content=f"Review completed: {'Success' if review_result['approved'] else 'Needs revision'}",
                metadata={'review': review_result}
            )
            self.send_message(message)

            self.agents['reviewer']['status'] = 'idle'

        if self.verbose:
            print(f"\n{'='*70}")
            print("COLLABORATION COMPLETED")
            print(f"{'='*70}\n")

        return {
            'goal': goal,
            'results': results,
            'messages': [
                {
                    'from': msg.from_agent,
                    'to': msg.to_agent,
                    'role': msg.role.value,
                    'content': msg.content,
                    'timestamp': msg.timestamp.isoformat()
                }
                for msg in self.message_history
            ]
        }

    def get_agent_status(self) -> Dict[str, str]:
        """Get status of all registered agents.

        Returns:
            Dictionary mapping agent names to their status
        """
        return {name: info['status'] for name, info in self.agents.items()}

    def register_callback(self, event: str, callback: Callable):
        """Register a callback for events.

        Args:
            event: Event name
            callback: Callback function
        """
        if event not in self.callbacks:
            self.callbacks[event] = []
        self.callbacks[event].append(callback)

    def trigger_callback(self, event: str, data: Any):
        """Trigger callbacks for an event.

        Args:
            event: Event name
            data: Event data
        """
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                callback(data)
