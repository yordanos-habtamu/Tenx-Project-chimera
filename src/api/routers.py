"""
API Routers for Project Chimera
Defines the REST API endpoints for the autonomous influencer system
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException

from ..services.content_service import ContentService
from ..services.publishing_service import PublishingService
from ..services.research_service import ResearchService

# Initialize services
content_service = ContentService()
research_service = ResearchService()
publishing_service = PublishingService()

# Setup logging
logger = logging.getLogger(__name__)

# Create API routers
router = APIRouter(prefix="/api/v1")


# Health check endpoint
@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify system status.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "content_service": "available",
            "research_service": "available",
            "publishing_service": "available",
        },
    }


# Research endpoints
@router.post("/research/trends")
async def analyze_trends(keywords: list[str], timeframe: str = "7d", topic: str = ""):
    """
    Analyze trends for specified keywords or topic.
    """
    try:
        result = await research_service.analyze_trends(keywords, timeframe, topic)
        logger.info(f"Trend analysis completed for keywords: {keywords}")
        return result
    except Exception as e:
        logger.error(f"Trend analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}") from e


@router.post("/research/niches")
async def analyze_niches(keywords: list[str], topic: str = ""):
    """
    Analyze niches based on keywords and topic.
    """
    try:
        result = await research_service.analyze_niches(keywords, topic)
        logger.info(f"Niches analysis completed for keywords: {keywords}")
        return result
    except Exception as e:
        logger.error(f"Niches analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}") from e


@router.post("/research/report")
async def generate_research_report(keywords: list[str], timeframe: str = "7d"):
    """
    Generate a comprehensive research report combining trend and niche analysis.
    """
    try:
        result = await research_service.generate_research_report(keywords, timeframe)
        logger.info(f"Research report generated for keywords: {keywords}")
        return result
    except Exception as e:
        logger.error(f"Research report generation failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Report generation failed: {str(e)}"
        ) from e


@router.get("/research/history")
async def get_research_history():
    """
    Get the history of research analyses.
    """
    try:
        history = research_service.get_analysis_history()
        return {"history": history, "count": len(history)}
    except Exception as e:
        logger.error(f"Failed to retrieve research history: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"History retrieval failed: {str(e)}"
        ) from e


@router.get("/research/stats")
async def get_research_stats():
    """
    Get statistics about research activities.
    """
    try:
        stats = research_service.get_research_statistics()
        return stats
    except Exception as e:
        logger.error(f"Failed to retrieve research stats: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Stats retrieval failed: {str(e)}"
        ) from e


# Content endpoints
@router.post("/content/create")
async def create_content_from_research(
    research_data: dict[str, Any], content_type: str = "educational"
):
    """
    Create content based on research data following the complete workflow.
    """
    try:
        result = await content_service.create_content_from_research(
            research_data, content_type
        )
        logger.info(f"Content creation completed: {result.get('video_id')}")
        return result
    except Exception as e:
        logger.error(f"Content creation failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Content creation failed: {str(e)}"
        ) from e


@router.get("/content/history")
async def get_content_history():
    """
    Get the history of content creation workflows.
    """
    try:
        history = content_service.get_workflow_history()
        return {"history": history, "count": len(history)}
    except Exception as e:
        logger.error(f"Failed to retrieve content history: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"History retrieval failed: {str(e)}"
        ) from e


@router.get("/content/stats")
async def get_content_stats():
    """
    Get statistics about created content.
    """
    try:
        stats = content_service.get_content_statistics()
        return stats
    except Exception as e:
        logger.error(f"Failed to retrieve content stats: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Stats retrieval failed: {str(e)}"
        ) from e


# Publishing endpoints
@router.post("/publish")
async def publish_content(
    content_data: dict[str, Any], platforms: list[str], schedule_immediate: bool = True
):
    """
    Publish content to specified platforms.
    """
    try:
        result = await publishing_service.publish_content(
            content_data, platforms, schedule_immediate
        )
        logger.info(
            f"Publishing completed: {result.get('successful_publishes')} successes"
        )
        return result
    except Exception as e:
        logger.error(f"Publishing failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Publishing failed: {str(e)}"
        ) from e


@router.post("/publish/schedule")
async def schedule_publication(
    content_data: dict[str, Any], platforms: list[str], scheduled_datetime: str
):
    """
    Schedule content publication for a future date/time.
    """
    try:
        # Parse the scheduled datetime string
        from datetime import datetime

        scheduled_dt = datetime.fromisoformat(scheduled_datetime.replace("Z", "+00:00"))

        result = await publishing_service.schedule_publication(
            content_data, platforms, scheduled_dt
        )
        logger.info(f"Publication scheduled: {result.get('scheduled')}")
        return result
    except Exception as e:
        logger.error(f"Scheduling failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Scheduling failed: {str(e)}"
        ) from e


@router.post("/publish/bulk")
async def bulk_publish(content_list: list[dict[str, Any]], platforms: list[str]):
    """
    Publish multiple pieces of content to specified platforms.
    """
    try:
        result = await publishing_service.bulk_publish(content_list, platforms)
        logger.info(f"Bulk publishing completed: {len(content_list)} items")
        return result
    except Exception as e:
        logger.error(f"Bulk publishing failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Bulk publishing failed: {str(e)}"
        ) from e


@router.get("/publish/history")
async def get_publication_history():
    """
    Get the history of publications.
    """
    try:
        history = publishing_service.get_publication_history()
        return {"history": history, "count": len(history)}
    except Exception as e:
        logger.error(f"Failed to retrieve publication history: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"History retrieval failed: {str(e)}"
        ) from e


@router.get("/publish/stats")
async def get_publishing_stats():
    """
    Get statistics about publishing activities.
    """
    try:
        stats = publishing_service.get_publishing_statistics()
        return stats
    except Exception as e:
        logger.error(f"Failed to retrieve publishing stats: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Stats retrieval failed: {str(e)}"
        ) from e


@router.get("/publish/platform-status/{platform}")
async def get_platform_status(platform: str):
    """
    Get the current status of a publishing platform.
    """
    try:
        result = await publishing_service.get_platform_status(platform)
        return result
    except Exception as e:
        logger.error(f"Failed to get platform status for {platform}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Status check failed: {str(e)}"
        ) from e


# Dashboard endpoints for monitoring
@router.get("/dashboard/overview")
async def get_dashboard_overview():
    """
    Get an overview of the system status and recent activity.
    """
    try:
        # Get stats from all services
        research_stats = research_service.get_research_statistics()
        content_stats = content_service.get_content_statistics()
        publishing_stats = publishing_service.get_publishing_statistics()

        overview = {
            "timestamp": datetime.utcnow().isoformat(),
            "research": research_stats,
            "content": content_stats,
            "publishing": publishing_stats,
            "system_uptime_hours": 24,  # Placeholder
            "active_agents": 0,  # Would come from orchestrator in real implementation
            "recent_activity": {
                "latest_research": (
                    research_stats.get("latest_analysis", {}).get("timestamp")
                    if research_stats.get("latest_analysis")
                    else None
                ),
                "latest_content": (
                    content_stats.get("latest_workflow", {}).get("created_at")
                    if content_stats.get("latest_workflow")
                    else None
                ),
                "latest_publishing": (
                    publishing_stats.get("latest_publication", {}).get("timestamp")
                    if publishing_stats.get("latest_publication")
                    else None
                ),
            },
        }

        return overview
    except Exception as e:
        logger.error(f"Failed to get dashboard overview: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Dashboard overview failed: {str(e)}"
        ) from e


# Agent management endpoints (for orchestrator)
@router.get("/agents/status")
async def get_agent_status():
    """
    Get the status of all registered agents.
    """
    try:
        # In a real implementation, this would connect to the orchestrator
        # For now, return a placeholder response
        return {
            "agents": [],
            "total_agents": 0,
            "active_agents": 0,
            "status": "standalone_mode",
            "message": "Agent orchestration service not yet connected to orchestrator",
        }
    except Exception as e:
        logger.error(f"Failed to get agent status: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Agent status check failed: {str(e)}"
        ) from e
