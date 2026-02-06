from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from src.api.app import app
from src.core.base_agent import AgentStatus

client = TestClient(app)


# Mock Orchestrator setup
@pytest.fixture
def mock_orchestrator():
    orchestrator = MagicMock()
    orchestrator.agents = {}

    # Mock an agent
    mock_agent = MagicMock()
    mock_agent.agent_id = "test_agent_001"
    mock_agent.status = AgentStatus.WORKING
    orchestrator.agents["test_agent_001"] = mock_agent
    orchestrator.agents["trend_fetcher_001"] = (
        mock_agent  # Add default agent for manual trigger test
    )

    return orchestrator


@pytest.fixture
def override_dependency(mock_orchestrator):
    # Inject mock orchestrator into app.state
    app.state.orchestrator = mock_orchestrator
    yield
    # Cleanup (optional if state persists)
    del app.state.orchestrator


def test_get_logs():
    """Test getting logs"""
    response = client.get("/api/v1/dashboard/logs")
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data
    assert len(data["logs"]) > 0


def test_get_config():
    """Test getting config"""
    response = client.get("/api/v1/dashboard/config")
    assert response.status_code == 200
    data = response.json()
    assert "environment" in data
    # Ensure sensitive keys are NOT present
    assert "secret_key" not in data
    assert "openrouter_api_key" not in data


def test_control_agent_success(override_dependency):
    """Test controlling an agent successfully"""
    # Test Pause
    response = client.post(
        "/api/v1/dashboard/agents/test_agent_001/control?action=pause"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["action"] == "pause"


def test_control_agent_invalid_action(override_dependency):
    """Test invalid action"""
    response = client.post(
        "/api/v1/dashboard/agents/test_agent_001/control?action=dance"
    )
    assert response.status_code == 400


def test_control_agent_not_found(override_dependency):
    """Test controlling non-existent agent"""
    response = client.post(
        "/api/v1/dashboard/agents/missing_agent/control?action=start"
    )
    assert response.status_code == 404


def test_manual_task_trigger(override_dependency):
    """Test manual task trigger"""
    from unittest.mock import AsyncMock

    # Setup mock assign_task as AsyncMock
    app.state.orchestrator.assign_task = AsyncMock(return_value={"status": "success"})

    payload = {"topic": "Test Topic"}
    response = client.post(
        "/api/v1/dashboard/tasks/manual",
        params={"task_type": "analyze_trends"},
        json=payload,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
