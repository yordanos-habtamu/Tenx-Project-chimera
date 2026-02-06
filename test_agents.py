"""
Test module for Project Chimera agents
"""

import pytest

from src.agents.research_agents import NicheAnalystAgent, TrendFetcherAgent
from src.agents.supervisor_agent import SupervisorAgent
from src.core.base_agent import AgentStatus


@pytest.mark.asyncio
async def test_supervisor_initialization():
    """Test that supervisor agent initializes correctly"""
    supervisor = SupervisorAgent()
    assert supervisor.name == "SupervisorAgent"
    assert supervisor.status == AgentStatus.IDLE


@pytest.mark.asyncio
async def test_trend_fetcher_agent():
    """Test that trend fetcher agent works correctly"""
    agent = TrendFetcherAgent()
    task_data = {
        "task_id": "test_task_001",
        "task_type": "analyze_trends",
        "topic": "AI",
        "keywords": ["AI", "Machine Learning"],
        "timeframe": "7d",
    }

    result = await agent.execute(task_data)
    assert "fetched_trends" in result
    assert result["total_trends"] > 0
    assert result["analysis_completed"] is True


@pytest.mark.asyncio
async def test_niche_analyst_agent():
    """Test that niche analyst agent works correctly"""
    agent = NicheAnalystAgent()
    task_data = {
        "task_id": "test_task_002",
        "task_type": "analyze_trends",
        "topic": "Technology",
        "keywords": ["AI", "Machine Learning"],
    }

    result = await agent.execute(task_data)
    assert "identified_niches" in result
    assert "top_niches" in result
    assert result["analysis_completed"] is True


@pytest.mark.asyncio
async def test_agent_orchestration():
    """Test that agents can be orchestrated together"""
    supervisor = SupervisorAgent()

    # Create and register a simple agent
    trend_agent = TrendFetcherAgent()
    await supervisor.register_subagent({"agent": trend_agent, "swarm_type": "research"})

    # Verify agent was registered
    statuses = await supervisor.orchestrator.get_all_statuses()
    assert len(statuses) >= 1

    # Test task execution
    task_data = {
        "task_id": "orchestration_test",
        "task_type": "analyze_trends",
        "topic": "AI",
        "keywords": ["AI"],
        "timeframe": "7d",
    }

    result = await supervisor.process_task(task_data)
    assert result["status"] == "success"


if __name__ == "__main__":
    # Run tests manually if executed directly
    import subprocess
    import sys

    # Install pytest-asyncio if not present
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest-asyncio"])

    # Run tests
    pytest.main([__file__, "-v"])
