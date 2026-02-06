"""
Research Component for Project Chimera
Handles trend analysis, market research, and opportunity identification
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

from ..services.research_service import ResearchService
from .base_component import BaseComponent

logger = logging.getLogger(__name__)


class ResearchComponent(BaseComponent):
    """
    Component for handling research-related operations in Project Chimera.
    Manages trend analysis, market research, and opportunity identification.
    """

    def __init__(
        self,
        component_id: str = "research_001",
        name: str = "ResearchComponent",
        version: str = "1.0.0",
    ):
        super().__init__(component_id, name, version)

        # Initialize the research service
        self.research_service = ResearchService()

        # Add component-specific configuration
        self.config.update(
            {
                "trend_sources": self.research_service.trend_sources,
                "niche_categories": self.research_service.niche_categories,
                "max_keywords_per_request": 10,
                "max_niches_per_analysis": 10,
            }
        )

    async def execute(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute research task based on task type.
        """
        task_type = task_data.get("task_type", "unknown")
        logger.info(f"ResearchComponent executing task: {task_type}")

        if task_type == "analyze_trends":
            return await self.analyze_trends(task_data)
        elif task_type == "analyze_niches":
            return await self.analyze_niches(task_data)
        elif task_type == "generate_research_report":
            return await self.generate_research_report(task_data)
        elif task_type == "get_analysis_history":
            return await self.get_analysis_history(task_data)
        elif task_type == "get_research_stats":
            return await self.get_research_stats(task_data)
        else:
            raise ValueError(f"Unknown research task type: {task_type}")

    async def analyze_trends(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze trends for specified keywords or topic.
        """
        keywords = task_data.get("keywords", [])
        timeframe = task_data.get("timeframe", "7d")
        topic = task_data.get("topic", "")

        # Validate input
        if not keywords and not topic:
            raise ValueError(
                "Either keywords or topic must be provided for trend analysis"
            )

        # Limit keywords to prevent abuse
        if len(keywords) > self.config["max_keywords_per_request"]:
            keywords = keywords[: self.config["max_keywords_per_request"]]

        logger.info(
            f"Analyzing trends for keywords: {keywords or topic}, timeframe: {timeframe}"
        )

        # Perform trend analysis using the service
        result = await self.research_service.analyze_trends(keywords, timeframe, topic)

        return result

    async def analyze_niches(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze niches based on keywords and topic.
        """
        keywords = task_data.get("keywords", [])
        topic = task_data.get("topic", "")

        # Validate input
        if not keywords and not topic:
            raise ValueError(
                "Either keywords or topic must be provided for niche analysis"
            )

        # Combine topic with keywords if both provided
        if topic and topic not in keywords:
            keywords.append(topic)

        logger.info(f"Analyzing niches for keywords: {keywords}")

        # Perform niche analysis using the service
        result = await self.research_service.analyze_niches(keywords, topic)

        return result

    async def generate_research_report(
        self, task_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Generate a comprehensive research report combining trend and niche analysis.
        """
        keywords = task_data.get("keywords", [])
        timeframe = task_data.get("timeframe", "7d")

        if not keywords:
            raise ValueError("Keywords must be provided for research report generation")

        logger.info(f"Generating comprehensive research report for: {keywords}")

        # Generate report using the service
        result = await self.research_service.generate_research_report(
            keywords, timeframe
        )

        return result

    async def get_analysis_history(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Get the history of research analyses.
        """
        logger.info("Retrieving research analysis history")

        history = self.research_service.get_analysis_history()

        return {"history": history, "count": len(history)}

    async def get_research_stats(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Get statistics about research activities.
        """
        logger.info("Retrieving research statistics")

        stats = self.research_service.get_research_statistics()

        return stats

    def _check_dependencies(self) -> bool:
        """
        Check if research service dependencies are available.
        """
        # In a real implementation, this would check if external APIs are reachable
        # For now, just check if the service is initialized
        return self.research_service is not None

    async def health_check(self) -> dict[str, Any]:
        """
        Perform a health check specific to the research component.
        """
        health_details = await super().health_check()

        # Add research-specific checks
        try:
            # Test basic functionality with a simple analysis
            test_result = await self.research_service.analyze_trends(
                ["test"], "1d", "test"
            )
            health_details["checks"]["functionality_check"] = True
            health_details["checks"]["functionality_result"] = {
                "trends_found": len(test_result.get("fetched_trends", [])),
                "analysis_completed": test_result.get("analysis_completed", False),
            }
        except Exception as e:
            health_details["checks"]["functionality_check"] = False
            health_details["checks"]["functionality_error"] = str(e)

        # Update health based on functionality check
        if not health_details["checks"]["functionality_check"]:
            self.health = "unhealthy"
            health_details["health"] = "unhealthy"

        return health_details


class TrendMonitoringComponent(BaseComponent):
    """
    Component for continuous trend monitoring and alerts.
    """

    def __init__(
        self,
        component_id: str = "trend_monitor_001",
        name: str = "TrendMonitoringComponent",
        version: str = "1.0.0",
    ):
        super().__init__(component_id, name, version)

        self.research_service = ResearchService()
        self.monitoring_tasks = {}
        self.alert_thresholds = {
            "volume_change": 0.2,  # 20% change threshold
            "sentiment_shift": 0.3,  # 0.3 sentiment shift threshold
            "trend_strength": "rising",  # Alert on rising trends
        }
        self.is_monitoring = False

    async def execute(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute trend monitoring task based on task type.
        """
        task_type = task_data.get("task_type", "unknown")
        logger.info(f"TrendMonitoringComponent executing task: {task_type}")

        if task_type == "start_monitoring":
            return await self.start_monitoring(task_data)
        elif task_type == "stop_monitoring":
            return await self.stop_monitoring(task_data)
        elif task_type == "get_alerts":
            return await self.get_alerts(task_data)
        elif task_type == "set_alert_thresholds":
            return await self.set_alert_thresholds(task_data)
        else:
            raise ValueError(f"Unknown trend monitoring task type: {task_type}")

    async def start_monitoring(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Start continuous trend monitoring.
        """
        if self.is_monitoring:
            return {
                "status": "already_monitoring",
                "message": "Trend monitoring is already active",
            }

        keywords = task_data.get("keywords", ["AI", "Technology", "Innovation"])
        interval_minutes = task_data.get("interval_minutes", 30)

        logger.info(
            f"Starting trend monitoring for keywords: {keywords}, interval: {interval_minutes} minutes"
        )

        self.is_monitoring = True
        monitoring_id = f"monitor_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        # Start monitoring loop in background
        monitoring_task = asyncio.create_task(
            self._monitoring_loop(keywords, interval_minutes)
        )

        self.monitoring_tasks[monitoring_id] = monitoring_task

        return {
            "monitoring_started": True,
            "monitoring_id": monitoring_id,
            "keywords_monitored": keywords,
            "interval_minutes": interval_minutes,
        }

    async def stop_monitoring(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Stop continuous trend monitoring.
        """
        monitoring_id = task_data.get("monitoring_id")

        if monitoring_id and monitoring_id in self.monitoring_tasks:
            task = self.monitoring_tasks[monitoring_id]
            task.cancel()
            del self.monitoring_tasks[monitoring_id]

            # Wait for task to finish cancellation
            try:
                await task
            except asyncio.CancelledError:
                pass  # Expected when cancelling

            logger.info(f"Stopped monitoring: {monitoring_id}")

            return {"monitoring_stopped": True, "monitoring_id": monitoring_id}
        elif not monitoring_id:
            # Stop all monitoring
            for _mid, task in self.monitoring_tasks.items():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            count = len(self.monitoring_tasks)
            self.monitoring_tasks.clear()
            self.is_monitoring = False

            logger.info(f"Stopped all monitoring tasks: {count}")

            return {"all_monitoring_stopped": True, "tasks_stopped": count}
        else:
            return {
                "monitoring_stopped": False,
                "error": f"Monitoring ID {monitoring_id} not found",
            }

    async def _monitoring_loop(self, keywords: list[str], interval_minutes: int):
        """
        Internal monitoring loop that runs continuously.
        """
        while self.is_monitoring:
            try:
                # Perform trend analysis
                current_trends = await self.research_service.analyze_trends(keywords)

                # Check for significant changes or new opportunities
                alerts = self._detect_changes(current_trends)

                if alerts:
                    logger.info(f"Detected {len(alerts)} trend alerts: {alerts}")
                    await self._handle_alerts(alerts)

                # Wait for the specified interval
                await asyncio.sleep(interval_minutes * 60)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                # Continue monitoring despite errors
                await asyncio.sleep(60)  # Wait 1 minute before retrying

    def _detect_changes(self, current_analysis: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Detect significant changes in trends that warrant alerts.
        """
        alerts = []
        trends = current_analysis.get("fetched_trends", [])

        for trend in trends:
            # Check for significant volume changes
            if trend.get("volume", 0) > 10000:  # High volume threshold
                alerts.append(
                    {
                        "type": "high_volume",
                        "keyword": trend["keyword"],
                        "volume": trend["volume"],
                        "message": f"High volume detected for '{trend['keyword']}': {trend['volume']} searches",
                    }
                )

            # Check for sentiment shifts
            if abs(trend.get("sentiment_score", 0)) > 0.7:  # Strong sentiment
                alerts.append(
                    {
                        "type": "strong_sentiment",
                        "keyword": trend["keyword"],
                        "sentiment": trend["sentiment_score"],
                        "message": f"Strong sentiment detected for '{trend['keyword']}': {trend['sentiment_score']}",
                    }
                )

            # Check for trend strength
            if trend.get("trend_strength") == "rising":
                alerts.append(
                    {
                        "type": "rising_trend",
                        "keyword": trend["keyword"],
                        "message": f"Rising trend detected for '{trend['keyword']}'",
                    }
                )

        return alerts

    async def _handle_alerts(self, alerts: list[dict[str, Any]]):
        """
        Handle detected alerts (could send notifications, store in DB, etc.).
        """
        # In a real implementation, this might send notifications or store alerts in a database
        # For now, just log the alerts
        for alert in alerts:
            logger.info(f"ALERT: {alert['message']}")

    async def get_alerts(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Get recent alerts (placeholder implementation).
        """
        # This would return stored alerts in a real implementation
        return {"alerts": [], "count": 0, "last_check": datetime.utcnow().isoformat()}

    async def set_alert_thresholds(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Set alert thresholds for trend monitoring.
        """
        new_thresholds = task_data.get("thresholds", {})
        self.alert_thresholds.update(new_thresholds)

        return {"thresholds_updated": True, "new_thresholds": self.alert_thresholds}

    def _check_dependencies(self) -> bool:
        """
        Check if trend monitoring dependencies are available.
        """
        return self.research_service is not None

    async def health_check(self) -> dict[str, Any]:
        """
        Perform a health check specific to the trend monitoring component.
        """
        health_details = await super().health_check()

        # Add monitoring-specific checks
        health_details["checks"]["monitoring_active"] = self.is_monitoring
        health_details["checks"]["active_monitoring_tasks"] = len(self.monitoring_tasks)

        return health_details
