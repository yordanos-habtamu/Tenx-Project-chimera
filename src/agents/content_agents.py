import asyncio
import logging
import random
import uuid
from datetime import datetime
from typing import Any

import aiohttp

# Optional: import openai if installed, else handle gracefully or assume installed
try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

from ..config.settings import (
    CONTENT_GENERATION_TIMEOUT,
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
    VIDEO_GEN_API_KEY,
    VIDEO_GEN_ENDPOINT,
    VIDEO_GEN_PROVIDER,
)
from ..core.base_agent import BaseAgent

logger = logging.getLogger(__name__)

if not AsyncOpenAI:
    logger.warning("openai package not installed. OpenRouter integration will fail.")


class ScriptWriterAgent(BaseAgent):
    """
    Agent responsible for writing scripts for various types of content using LLM.
    """

    def __init__(
        self, agent_id: str = "script_writer_001", name: str = "ScriptWriterAgent"
    ):
        super().__init__(agent_id, name)
        self.client = None
        if OPENROUTER_API_KEY and AsyncOpenAI:
            self.client = AsyncOpenAI(
                api_key=OPENROUTER_API_KEY,
                base_url=OPENROUTER_BASE_URL,
            )
        else:
            logger.warning(
                "OpenRouter API Key not found or openai not installed. Falling back to mock generation."
            )

    async def execute(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute script writing task.
        """
        task_type = task_data.get("task_type", "unknown")
        logger.info(f"ScriptWriter executing task: {task_type}")

        if task_type == "generate_content":
            return await self.write_script(task_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def write_script(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Write a script based on the provided research data and parameters.
        """
        research_data = task_data.get("research_data", {})
        content_type = task_data.get("content_type", "educational")

        logger.info(f"Writing script of type: {content_type}")

        # Extract relevant information from research data
        # Handle various input structures safely
        trends = []
        if "results" in research_data:
            results = research_data.get("results", [])
            if results and isinstance(results, list):
                trends = results[0].get("result", {}).get("fetched_trends", [])
        elif "fetched_trends" in research_data:
            trends = research_data.get("fetched_trends", [])

        if not trends:
            # Fallback mock trends
            trends = [
                {
                    "keyword": "Artificial Intelligence",
                    "volume": 8500,
                    "sentiment_score": 0.7,
                }
            ]

        # Select the most relevant trend
        primary_trend = (
            max(trends, key=lambda x: x.get("volume", 0)) if trends else trends[0]
        )
        topic = primary_trend.get("keyword", "Technology")

        if self.client:
            try:
                return await self._generate_with_llm(topic, content_type, primary_trend)
            except Exception as e:
                logger.error(
                    f"OpenRouter generation failed: {e}. Falling back to template."
                )

        # Fallback to template if no client or error
        return self._generate_with_template(topic, content_type, primary_trend)

    async def _generate_with_llm(
        self, topic: str, content_type: str, trend_data: dict
    ) -> dict[str, Any]:
        """Generate script using OpenRouter."""
        prompt = f"""
        Write a video script for a {content_type} video about "{topic}".
        Trend Data: {trend_data}

        Format the output clearly with sections: Title, Introduction, Main Content, Conclusion.
        The script should be engaging and suitable for social media.
        """

        response = await self.client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional viral video script writer.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        script_content = response.choices[0].message.content

        # Simple parsing logic (could be improved with structured output)
        lines = script_content.split("\n")
        title = f"Video about {topic}"
        for line in lines:
            if "Title:" in line or "TITLE:" in line:
                title = line.replace("Title:", "").replace("TITLE:", "").strip()
                break

        return {
            "video_id": str(uuid.uuid4()),
            "title": title,
            "script": script_content,
            "trend_keyword": topic,
            "trend_volume": trend_data.get("volume", 0),
            "content_type": content_type,
            "estimated_duration": "Generic LLM Estimate",
            "script_written": True,
            "source": "OpenRouter",
        }

    def _generate_with_template(
        self, topic: str, content_type: str, trend_data: dict
    ) -> dict[str, Any]:
        """Fallback template generation."""
        logger.info("Using template fallback for script generation.")
        # ... (Existing template logic simplified for brevity/fallback) ...
        return {
            "video_id": str(uuid.uuid4()),
            "title": f"Guide to {topic}",
            "script": f"Intro: {topic} is trending.\nBody: Here is why.\nOutro: Subscribe.",
            "trend_keyword": topic,
            "trend_volume": trend_data.get("volume", 0),
            "content_type": content_type,
            "estimated_duration": "5 minutes",
            "script_written": True,
            "source": "TemplateFallback",
        }


class VideoGeneratorAgent(BaseAgent):
    """
    Agent responsible for generating video content based on scripts using external API.
    """

    def __init__(
        self, agent_id: str = "video_gen_001", name: str = "VideoGeneratorAgent"
    ):
        super().__init__(agent_id, name)

    async def execute(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute video generation task.
        """
        task_type = task_data.get("task_type", "unknown")
        logger.info(f"VideoGenerator executing task: {task_type}")

        if task_type == "generate_content":
            return await self.generate_video(task_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def generate_video(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Generate video content based on the provided script and parameters.
        """
        content_data = task_data.get("content_data", {})
        # Handle nested structure from previous steps
        if isinstance(content_data, dict) and "results" in content_data:
            script_data = content_data.get("results", [{}])[0].get("result", {})
        else:
            script_data = content_data

        video_id = script_data.get("video_id", str(uuid.uuid4()))
        title = script_data.get("title", "Generated Video")
        script = script_data.get("script", "")

        if VIDEO_GEN_API_KEY and VIDEO_GEN_ENDPOINT:
            try:
                return await self._generate_with_api(title, script, video_id)
            except Exception as e:
                logger.error(f"Video API generation failed: {e}. Falling back to mock.")

        return self._generate_mock(title, video_id)

    async def _generate_with_api(
        self, title: str, script: str, video_id: str
    ) -> dict[str, Any]:
        """Generate video using generic API pattern (Submit -> Poll)."""
        logger.info(f"Submitting video generation job to {VIDEO_GEN_ENDPOINT}")

        async with aiohttp.ClientSession() as session:
            # 1. Submit Job
            payload = {"title": title, "script": script, "provider": VIDEO_GEN_PROVIDER}
            headers = {"Authorization": f"Bearer {VIDEO_GEN_API_KEY}"}

            async with session.post(
                f"{VIDEO_GEN_ENDPOINT}/jobs", json=payload, headers=headers
            ) as resp:
                if resp.status != 200:
                    raise Exception(f"API Error: {await resp.text()}")
                data = await resp.json()
                job_id = data.get("id")

            # 2. Poll for completion
            start_time = datetime.utcnow()
            while (datetime.utcnow() - start_time).seconds < CONTENT_GENERATION_TIMEOUT:
                await asyncio.sleep(10)  # Poll every 10 seconds

                async with session.get(
                    f"{VIDEO_GEN_ENDPOINT}/jobs/{job_id}", headers=headers
                ) as resp:
                    if resp.status != 200:
                        continue
                    job_status = await resp.json()

                    if job_status.get("status") == "completed":
                        return {
                            "video_id": video_id,
                            "title": title,
                            "video_url": job_status.get("url"),
                            "status": "completed",
                            "provider": VIDEO_GEN_PROVIDER,
                            "generated": True,
                        }
                    elif job_status.get("status") == "failed":
                        raise Exception(
                            f"Video generation failed: {job_status.get('error')}"
                        )

            raise Exception("Video generation timed out")

    def _generate_mock(self, title: str, video_id: str) -> dict[str, Any]:
        """Mock generation for development/fallback."""
        logger.info(f"Generating usage mock video for: {title}")
        return {
            "video_id": video_id,
            "title": title,
            "video_url": f"https://mock-provider.com/watch?v={video_id[:8]}",
            "video_style": "mock_style",
            "platform": "youtube",
            "generated": True,
            "estimated_completion_time": "Instant (Mock)",
            "file_path": f"/tmp/generated_videos/{video_id}.mp4",
        }


class ThumbnailDesignerAgent(BaseAgent):
    """
    Agent responsible for designing thumbnails for video content.
    Note: This is a simulation - actual thumbnail generation would require image processing.
    """

    def __init__(
        self,
        agent_id: str = "thumbnail_designer_001",
        name: str = "ThumbnailDesignerAgent",
    ):
        super().__init__(agent_id, name)
        self.color_schemes = [
            ["#FF5733", "#33FF57", "#3357FF"],  # Vibrant
            ["#000000", "#FFFFFF", "#FFD700"],  # Classic
            ["#FF6B6B", "#4ECDC4", "#FFE66D"],  # Modern
            ["#6A0572", "#AB83A1", "#5CACBC"],  # Professional
        ]
        self.font_styles = ["bold", "rounded", "serif", "sans-serif"]
        self.layout_styles = ["split", "overlay", "minimal", "busy"]

    async def execute(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute thumbnail design task.
        """
        task_type = task_data.get("task_type", "unknown")
        logger.info(f"ThumbnailDesigner executing task: {task_type}")

        if task_type == "generate_content":
            return await self.design_thumbnail(task_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def design_thumbnail(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Design a thumbnail based on the video content and parameters.
        """
        content_data = task_data.get("content_data", {})
        script_data = (
            content_data.get("results", [{}])[0].get("result", {})
            if isinstance(content_data, dict)
            else content_data
        )

        # Handle different input structures
        if not script_data:
            # If content_data is the script data itself
            script_data = content_data

        video_title = script_data.get("title", "New Video")
        trend_keyword = script_data.get("trend_keyword", "Technology")

        logger.info(f"Designing thumbnail for: {video_title}")

        # Generate mock thumbnail details
        video_id = script_data.get("video_id", str(uuid.uuid4()))

        # Select design elements
        color_scheme = random.choice(self.color_schemes)
        font_style = random.choice(self.font_styles)
        layout_style = random.choice(self.layout_styles)

        # Generate mock text elements
        text_elements = [
            {
                "text": trend_keyword.upper(),
                "position": "top",
                "size": "large",
                "color": color_scheme[0],
            },
            {"text": "NEW", "position": "corner", "size": "small", "color": "#FF0000"},
        ]

        # Generate mock thumbnail URL (simulated creation)
        thumbnail_url = f"https://i.ytimg.com/vi/{video_id[:11]}/maxresdefault.jpg"

        return {
            "video_id": video_id,
            "thumbnail_url": thumbnail_url,
            "design_elements": {
                "color_scheme": color_scheme,
                "font_style": font_style,
                "layout_style": layout_style,
                "text_elements": text_elements,
            },
            "dimensions": "1280x720",
            "designed": True,
            "file_path": f"/tmp/generated_thumbnails/{video_id}_thumb.jpg",  # Mock file path
        }
