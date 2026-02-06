import logging

from ..agents.content_agents import (
    ScriptWriterAgent,
    ThumbnailDesignerAgent,
    VideoGeneratorAgent,
)
from ..agents.distribution_agents import OpenClawAnnouncerAgent, PlatformPublisherAgent
from ..agents.research_agents import NicheAnalystAgent, TrendFetcherAgent
from ..agents.safety_agents import ContentModerationAgent, HumanInLoopAgent
from ..agents.supervisor_agent import SupervisorAgent

logger = logging.getLogger(__name__)


async def initialize_agents():
    """
    Initialize and register all agents with the supervisor.
    Returns the supervisor agent instance.
    """
    logger.info("Initializing Project Chimera agents via AgentFactory...")

    # Create supervisor agent
    supervisor = SupervisorAgent()

    # Create ResearchSwarm agents
    trend_fetcher = TrendFetcherAgent("trend_fetcher_001", "TrendFetcherAgent")
    niche_analyst = NicheAnalystAgent("niche_analyst_001", "NicheAnalystAgent")

    # Create ContentSwarm agents
    script_writer = ScriptWriterAgent("script_writer_001", "ScriptWriterAgent")
    video_generator = VideoGeneratorAgent("video_gen_001", "VideoGeneratorAgent")
    thumbnail_designer = ThumbnailDesignerAgent(
        "thumbnail_designer_001", "ThumbnailDesignerAgent"
    )

    # Create SafetyLayer agents
    hitl_agent = HumanInLoopAgent("hitl_001", "HumanInLoopAgent")
    moderation_agent = ContentModerationAgent(
        "moderation_001", "ContentModerationAgent"
    )

    # Create DistributionSwarm agents
    publisher_agent = PlatformPublisherAgent("publisher_001", "PlatformPublisherAgent")
    openclaw_announcer = OpenClawAnnouncerAgent(
        "openclaw_001", "OpenClawAnnouncerAgent"
    )

    # Register agents with supervisor
    agents_config = [
        (trend_fetcher, "research"),
        (niche_analyst, "research"),
        (script_writer, "content"),
        (video_generator, "content"),
        (thumbnail_designer, "content"),
        (hitl_agent, "safety"),
        (moderation_agent, "safety"),
        (publisher_agent, "distribution"),
        (openclaw_announcer, "distribution"),
    ]

    for agent, swarm_type in agents_config:
        await supervisor.register_subagent({"agent": agent, "swarm_type": swarm_type})

    logger.info("All agents initialized and registered with supervisor")
    return supervisor
