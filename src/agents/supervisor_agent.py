import logging
from datetime import datetime
from typing import Any

from ..core.base_agent import AgentOrchestrator, BaseAgent

logger = logging.getLogger(__name__)


class SupervisorAgent(BaseAgent):
    """
    Main orchestrator agent that manages the hierarchical swarm of specialized agents.
    Coordinates the workflow between ResearchSwarm, ContentSwarm, SafetyLayer, and DistributionSwarm.
    """

    def __init__(self, agent_id: str = "supervisor_001", name: str = "SupervisorAgent"):
        super().__init__(agent_id, name)
        self.orchestrator = AgentOrchestrator()
        self.swarms = {"research": [], "content": [], "safety": [], "distribution": []}

    async def execute(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute supervisor tasks - coordinate between different agent swarms.
        """
        task_type = task_data.get("task_type", "unknown")
        logger.info(f"Supervisor executing task: {task_type}")

        if task_type == "coordinate_content_creation":
            return await self.coordinate_content_creation(task_data)
        elif task_type == "analyze_trends":
            return await self.analyze_trends(task_data)
        elif task_type == "publish_content":
            return await self.publish_content(task_data)
        elif task_type == "register_subagent":
            return await self.register_subagent(task_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def register_subagent(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Register a sub-agent with the supervisor.
        """
        agent = task_data.get("agent")
        swarm_type = task_data.get("swarm_type")

        if agent and swarm_type and swarm_type in self.swarms:
            self.orchestrator.register_agent(agent)
            self.swarms[swarm_type].append(agent.agent_id)
            logger.info(f"Registered {agent.name} to {swarm_type} swarm")

            return {
                "message": f"Successfully registered {agent.name} to {swarm_type} swarm",
                "agent_id": agent.agent_id,
                "swarm_type": swarm_type,
            }
        else:
            raise ValueError("Invalid agent registration request")

    async def coordinate_content_creation(
        self, task_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Coordinate the process of content creation across multiple swarms.
        """
        logger.info("Starting content creation coordination...")

        # Step 1: Analyze current trends using ResearchSwarm
        research_results = await self._execute_research_phase(task_data)

        # Step 2: Generate content using ContentSwarm
        content_results = await self._execute_content_phase(research_results)

        # Step 3: Validate content using SafetyLayer
        validation_results = await self._execute_safety_phase(content_results)

        # Step 4: Distribute content using DistributionSwarm
        distribution_results = await self._execute_distribution_phase(
            validation_results
        )

        return {
            "research_results": research_results,
            "content_results": content_results,
            "validation_results": validation_results,
            "distribution_results": distribution_results,
            "workflow_completed": True,
        }

    async def _execute_research_phase(
        self, task_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Execute the research phase using ResearchSwarm agents.
        """
        logger.info("Executing research phase...")

        # Get all agents in the research swarm
        research_agents = list(self.swarms["research"])

        if not research_agents:
            logger.warning("No research agents registered")
            return {"error": "No research agents available"}

        # Prepare research task
        research_task = {
            "task_id": f"research_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "task_type": "analyze_trends",
            "topic": task_data.get("topic", ""),
            "keywords": task_data.get("keywords", []),
            "timeframe": task_data.get("timeframe", "7d"),
        }

        # Broadcast to all research agents
        results = await self.orchestrator.broadcast_task(
            research_task, lambda agent: agent.agent_id in research_agents
        )

        return {"results": results, "phase": "research"}

    async def _execute_content_phase(
        self, research_results: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Execute the content generation phase using ContentSwarm agents.
        """
        logger.info("Executing content phase...")

        content_agents = list(self.swarms["content"])

        if not content_agents:
            logger.warning("No content agents registered")
            return {"error": "No content agents available"}

        # Prepare content task based on research results
        content_task = {
            "task_id": f"content_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "task_type": "generate_content",
            "research_data": research_results,
            "content_type": "script",  # Could be script, video, thumbnail, etc.
            "platform": "youtube",  # Default platform
        }

        # Broadcast to all content agents
        results = await self.orchestrator.broadcast_task(
            content_task, lambda agent: agent.agent_id in content_agents
        )

        return {"results": results, "phase": "content"}

    async def _execute_safety_phase(
        self, content_results: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Execute the safety/validation phase using SafetyLayer agents.
        """
        logger.info("Executing safety phase...")

        safety_agents = list(self.swarms["safety"])

        if not safety_agents:
            logger.warning("No safety agents registered")
            return {
                "error": "No safety agents available",
                "content_passed_validation": False,
            }

        # Prepare validation task
        validation_task = {
            "task_id": f"safety_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "task_type": "validate_content",
            "content_data": content_results,
            "policy_check": True,
            "human_approval_required": True,  # Default to requiring human approval
        }

        # Broadcast to all safety agents
        results = await self.orchestrator.broadcast_task(
            validation_task, lambda agent: agent.agent_id in safety_agents
        )

        # Check if content passed validation
        content_passed = all(
            r.get("result", {}).get("approved", False) for r in results
        )

        return {
            "results": results,
            "phase": "safety",
            "content_passed_validation": content_passed,
        }

    async def _execute_distribution_phase(
        self, validation_results: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Execute the distribution phase using DistributionSwarm agents.
        """
        logger.info("Executing distribution phase...")

        if not validation_results.get("content_passed_validation", False):
            logger.warning(
                "Content did not pass safety validation, skipping distribution"
            )
            return {"skipped": True, "reason": "Failed safety validation"}

        distribution_agents = list(self.swarms["distribution"])

        if not distribution_agents:
            logger.warning("No distribution agents registered")
            return {"error": "No distribution agents available"}

        # Prepare distribution task
        distribution_task = {
            "task_id": f"distribution_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "task_type": "publish_content",
            "content_data": validation_results.get("content_data", {}),
            "platforms": ["youtube", "twitter", "instagram"],  # Default platforms
            "schedule_immediate": True,
        }

        # Broadcast to all distribution agents
        results = await self.orchestrator.broadcast_task(
            distribution_task, lambda agent: agent.agent_id in distribution_agents
        )

        return {"results": results, "phase": "distribution", "published": True}

    async def analyze_trends(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze market trends using the ResearchSwarm.
        """
        logger.info("Analyzing trends...")
        return await self._execute_research_phase(task_data)

    async def publish_content(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Publish content using the DistributionSwarm.
        """
        logger.info("Publishing content...")

        # First validate content
        validation_results = await self._execute_safety_phase(
            {"content_data": task_data}
        )

        if not validation_results.get("content_passed_validation", False):
            return {"error": "Content did not pass validation", "published": False}

        # Then distribute
        return await self._execute_distribution_phase(validation_results)
