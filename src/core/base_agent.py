import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Enumeration of possible agent statuses"""

    IDLE = "idle"
    WORKING = "working"
    PAUSED = "paused"
    ERROR = "error"
    COMPLETED = "completed"


class TaskPriority(Enum):
    """Enumeration of task priorities"""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the Project Chimera system.
    Provides common functionality and interface for agent implementations.
    """

    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name
        self.status = AgentStatus.IDLE
        self.created_at = datetime.utcnow()
        self.last_updated = datetime.utcnow()
        self.task_queue = asyncio.Queue()
        self.config = {}

    @abstractmethod
    async def execute(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the main function of the agent.
        This must be implemented by subclasses.
        """
        pass

    async def process_task(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Process a single task with error handling and status updates.
        """
        self.status = AgentStatus.WORKING
        self.last_updated = datetime.utcnow()

        try:
            logger.info(
                f"Agent {self.name} starting task: {task.get('task_type', 'unknown')}"
            )
            result = await self.execute(task)

            self.status = AgentStatus.COMPLETED
            logger.info(f"Agent {self.name} completed task successfully")

            return {
                "agent_id": self.agent_id,
                "task_id": task.get("task_id"),
                "result": result,
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            self.status = AgentStatus.ERROR
            logger.error(f"Agent {self.name} failed to execute task: {str(e)}")

            return {
                "agent_id": self.agent_id,
                "task_id": task.get("task_id"),
                "error": str(e),
                "status": "error",
                "timestamp": datetime.utcnow().isoformat(),
            }
        finally:
            self.last_updated = datetime.utcnow()

    async def add_task(self, task: dict[str, Any]):
        """
        Add a task to the agent's queue.
        """
        await self.task_queue.put(task)

    async def get_status(self) -> dict[str, Any]:
        """
        Get the current status of the agent.
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "queue_size": self.task_queue.qsize(),
        }

    def update_config(self, config: dict[str, Any]):
        """
        Update the agent's configuration.
        """
        self.config.update(config)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert agent to dictionary representation for serialization.
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }


class AgentOrchestrator:
    """
    Orchestrates multiple agents, manages their lifecycle and task distribution.
    """

    def __init__(self):
        self.agents = {}
        self.active_tasks = {}

    def register_agent(self, agent: BaseAgent):
        """
        Register an agent with the orchestrator.
        """
        self.agents[agent.agent_id] = agent
        logger.info(f"Registered agent: {agent.name} ({agent.agent_id})")

    def deregister_agent(self, agent_id: str):
        """
        Remove an agent from the orchestrator.
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Deregistered agent: {agent_id}")

    async def assign_task(self, agent_id: str, task: dict[str, Any]) -> dict[str, Any]:
        """
        Assign a task to a specific agent.
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found in orchestrator")

        agent = self.agents[agent_id]
        return await agent.process_task(task)

    async def broadcast_task(
        self, task: dict[str, Any], filter_func=None
    ) -> list[dict[str, Any]]:
        """
        Broadcast a task to multiple agents that match the filter criteria.
        """
        results = []

        for _agent_id, agent in self.agents.items():
            if filter_func is None or filter_func(agent):
                result = await agent.process_task(task)
                results.append(result)

        return results

    async def get_all_statuses(self) -> dict[str, Any]:
        """
        Get statuses of all registered agents.
        """
        statuses = {}
        for _agent_id, agent in self.agents.items():
            statuses[_agent_id] = await agent.get_status()
        return statuses
