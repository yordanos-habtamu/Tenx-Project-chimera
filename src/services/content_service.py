"""
Content Service for Project Chimera
Handles content creation, management, and workflow orchestration
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from ..database.models import Video
from ..database.connection import get_db
from ..core.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ContentService:
    """
    Service class for handling content-related operations in Project Chimera.
    Manages the content creation workflow from research to publication.
    """
    
    def __init__(self):
        self.agents = {}  # Will hold agent instances
        self.workflow_history = []
    
    async def create_content_from_research(
        self, 
        research_data: Dict[str, Any], 
        content_type: str = "educational"
    ) -> Dict[str, Any]:
        """
        Create content based on research data following the complete workflow.
        """
        logger.info(f"Starting content creation workflow for type: {content_type}")
        
        try:
            # Step 1: Generate script from research data
            script_result = await self._generate_script(research_data, content_type)
            
            # Step 2: Create video content
            video_result = await self._generate_video(script_result)
            
            # Step 3: Create thumbnail
            thumbnail_result = await self._generate_thumbnail(script_result)
            
            # Step 4: Save to database
            video_record = await self._save_video_record({
                **script_result,
                **video_result,
                **thumbnail_result
            })
            
            result = {
                "video_id": video_record.id,
                "title": video_record.title,
                "status": "created",
                "created_at": video_record.created_at.isoformat(),
                "steps_completed": [
                    "script_generation",
                    "video_generation", 
                    "thumbnail_generation",
                    "database_storage"
                ]
            }
            
            self.workflow_history.append(result)
            logger.info(f"Content creation workflow completed successfully: {video_record.id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Content creation workflow failed: {str(e)}")
            raise
    
    async def _generate_script(
        self, 
        research_data: Dict[str, Any], 
        content_type: str
    ) -> Dict[str, Any]:
        """
        Generate a script based on research data.
        """
        logger.info("Generating script from research data")
        
        # Extract key information from research data
        trends = research_data.get("fetched_trends", [])
        if not trends:
            # Handle case where research data structure is different
            results_list = research_data.get("results", [])
            if results_list and isinstance(results_list[0], dict):
                result_data = results_list[0].get("result", {})
                trends = result_data.get("fetched_trends", [])
        
        if not trends:
            # Use default trend if none found
            primary_trend = {"keyword": "Technology", "volume": 5000}
        else:
            # Select the most relevant trend
            primary_trend = max(trends, key=lambda x: x.get("volume", 0))
        
        # Generate content based on type
        if content_type == "educational":
            script_parts = [
                f"INTRODUCTION: Today we're discussing {primary_trend['keyword']}, "
                f"a trending topic with {primary_trend['volume']} weekly searches.",
                
                f"MAIN CONTENT: {primary_trend['keyword']} is transforming the industry "
                f"by providing innovative solutions to common challenges.",
                
                f"PRACTICAL EXAMPLE: Real-world applications of {primary_trend['keyword']} "
                f"are already impacting businesses and consumers.",
                
                f"CONCLUSION: The future of {primary_trend['keyword']} looks promising, "
                f"and staying informed about these trends is crucial for success."
            ]
        else:
            # Default script for other content types
            script_parts = [
                f"Exploring the latest developments in {primary_trend['keyword']}",
                f"Why {primary_trend['keyword']} matters in today's landscape",
                f"Key insights and future outlook for {primary_trend['keyword']}"
            ]
        
        script = "\n\n".join(script_parts)
        
        return {
            "title": f"The Ultimate Guide to {primary_trend['keyword']}",
            "script": script,
            "trend_keyword": primary_trend['keyword'],
            "trend_volume": primary_trend.get('volume', 0),
            "content_type": content_type,
            "estimated_duration": "8-12 minutes"
        }
    
    async def _generate_video(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate video content based on script.
        """
        logger.info("Generating video content")
        
        # Simulate video generation
        import uuid
        video_id = str(uuid.uuid4())
        
        return {
            "video_id": video_id,
            "video_url": f"https://example.com/videos/{video_id}",
            "video_format": "mp4",
            "resolution": "1920x1080",
            "duration_seconds": 600,  # 10 minutes
            "file_size_mb": 150,
            "generated": True
        }
    
    async def _generate_thumbnail(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate thumbnail for the video.
        """
        logger.info("Generating thumbnail")
        
        import uuid
        thumb_id = str(uuid.uuid4())
        
        return {
            "thumbnail_id": thumb_id,
            "thumbnail_url": f"https://example.com/thumbnails/{thumb_id}",
            "dimensions": "1280x720",
            "generated": True
        }
    
    async def _save_video_record(self, content_data: Dict[str, Any]) -> Video:
        """
        Save video record to database.
        """
        logger.info("Saving video record to database")
        
        from sqlalchemy.orm import Session
        
        video = Video(
            title=content_data.get("title", "Untitled"),
            script=content_data.get("script"),
            video_url=content_data.get("video_url"),
            platform=content_data.get("platform", "youtube"),
            status=content_data.get("status", "draft")
        )
        
        # Use context manager to ensure proper session handling
        with get_db() as db_session:
            db_session.add(video)
            db_session.commit()
            db_session.refresh(video)
        
        return video
    
    def get_workflow_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of content creation workflows.
        """
        return self.workflow_history[:]
    
    def get_content_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about created content.
        """
        total_content = len(self.workflow_history)
        content_by_type = {}
        
        for item in self.workflow_history:
            content_type = item.get("content_type", "unknown")
            content_by_type[content_type] = content_by_type.get(content_type, 0) + 1
        
        return {
            "total_content_created": total_content,
            "content_by_type": content_by_type,
            "latest_workflow": self.workflow_history[-1] if self.workflow_history else None
        }