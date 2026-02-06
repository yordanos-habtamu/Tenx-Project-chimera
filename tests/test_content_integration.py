from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents.content_agents import ScriptWriterAgent, VideoGeneratorAgent


@pytest.mark.asyncio
async def test_script_writer_openrouter_mock():
    """
    Test ScriptWriterAgent with mocked OpenRouter client.
    """
    # Setup mock data
    task_data = {
        "task_type": "generate_content",
        "content_type": "educational",
        "research_data": {
            "fetched_trends": [{"keyword": "Test Trend", "volume": 1000}]
        },
    }

    # Mock the AsyncOpenAI client
    with patch("src.agents.content_agents.AsyncOpenAI") as MockClient:
        # Create instance
        agent = ScriptWriterAgent()

        # Configure the mock client instance
        mock_instance = MockClient.return_value
        # Use simple MagicMock for chat.completions.create
        # but the RETURN value of create must be awaitable if the code awaits it.
        # However, AsyncOpenAI is async, so create() returns a coroutine.

        # We need to simulate the response structure
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            "Title: Test Video\n\nIntro\nBody\nConclusion"
        )

        # Make the create method an AsyncMock that returns the mock_response
        mock_instance.chat.completions.create = AsyncMock(return_value=mock_response)

        # Inject this mock client into the agent (since __init__ might check env vars)
        agent.client = mock_instance

        # Execute
        result = await agent.execute(task_data)

        # Verify
        assert result["script_written"] is True
        assert result["title"] == "Test Video"
        assert result["source"] == "OpenRouter"

        # Verify call arguments
        mock_instance.chat.completions.create.assert_called_once()
        print("\nScriptWriterAgent OpenRouter Test Passed!")


@pytest.mark.asyncio
async def test_video_generator_api_mock():
    """
    Test VideoGeneratorAgent with mocked generic API (aiohttp).
    """
    task_data = {
        "task_type": "generate_content",
        "content_data": {
            "title": "Test Video",
            "script": "Some script",
            "video_id": "123",
        },
    }

    # Mock environment variables to ensure we enter the API path
    with (
        patch("src.agents.content_agents.VIDEO_GEN_API_KEY", "test_key"),
        patch("src.agents.content_agents.VIDEO_GEN_ENDPOINT", "http://test.api"),
        patch("aiohttp.ClientSession.post") as mock_post,
        patch("aiohttp.ClientSession.get") as mock_get,
    ):

        agent = VideoGeneratorAgent()

        # Setup Post Mock (Job Submission)
        mock_post_resp = AsyncMock()
        mock_post_resp.status = 200
        mock_post_resp.json.return_value = {"id": "job_123"}
        # Context manager support for session.post()
        mock_post.return_value.__aenter__.return_value = mock_post_resp

        # Setup Get Mock (Polling)
        # Sequence: First call -> processing, Second call -> completed
        mock_get_resp_processing = AsyncMock()
        mock_get_resp_processing.status = 200
        mock_get_resp_processing.json.return_value = {"status": "processing"}

        mock_get_resp_completed = AsyncMock()
        mock_get_resp_completed.status = 200
        mock_get_resp_completed.json.return_value = {
            "status": "completed",
            "url": "http://video.url/123.mp4",
        }

        # Configure side_effect for get
        mock_get.return_value.__aenter__.side_effect = [
            mock_get_resp_processing,
            mock_get_resp_completed,
        ]

        # Reduce polling sleep time to speed up test
        with patch("asyncio.sleep", return_value=None):
            result = await agent.execute(task_data)

        # Verify
        assert result["generated"] is True
        assert result["video_url"] == "http://video.url/123.mp4"
        assert result["provider"] == "generic"

        print("VideoGeneratorAgent API Test Passed!")
