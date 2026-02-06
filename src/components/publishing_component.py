"""
Publishing Component for Project Chimera
Handles content publishing to various platforms and distribution channels
"""

import logging
from datetime import datetime
from typing import Any

from ..services.publishing_service import PublishingService
from .base_component import BaseComponent

logger = logging.getLogger(__name__)


class PublishingComponent(BaseComponent):
    """
    Component for handling publishing-related operations in Project Chimera.
    Manages content distribution to various social media platforms.
    """

    def __init__(
        self,
        component_id: str = "publishing_001",
        name: str = "PublishingComponent",
        version: str = "1.0.0",
    ):
        super().__init__(component_id, name, version)

        # Initialize the publishing service
        self.publishing_service = PublishingService()

        # Add component-specific configuration
        self.config.update(
            {
                "supported_platforms": list(
                    self.publishing_service.supported_platforms.keys()
                ),
                "max_simultaneous_publishes": 5,
                "publishing_timeout": 600,  # 10 minutes
                "retry_attempts": 3,
                "retry_delay": 5,  # seconds
            }
        )

    async def execute(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute publishing task based on task type.
        """
        task_type = task_data.get("task_type", "unknown")
        logger.info(f"PublishingComponent executing task: {task_type}")

        if task_type == "publish_content":
            return await self.publish_content(task_data)
        elif task_type == "schedule_publication":
            return await self.schedule_publication(task_data)
        elif task_type == "bulk_publish":
            return await self.bulk_publish(task_data)
        elif task_type == "get_publication_history":
            return await self.get_publication_history(task_data)
        elif task_type == "get_publishing_stats":
            return await self.get_publishing_stats(task_data)
        elif task_type == "get_platform_status":
            return await self.get_platform_status(task_data)
        else:
            raise ValueError(f"Unknown publishing task type: {task_type}")

    async def publish_content(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Publish content to specified platforms.
        """
        content_data = task_data.get("content_data", {})
        platforms = task_data.get("platforms", [])
        schedule_immediate = task_data.get("schedule_immediate", True)

        # Validate inputs
        if not platforms:
            raise ValueError("At least one platform must be specified for publishing")

        if not content_data:
            raise ValueError("Content data must be provided for publishing")

        logger.info(f"Publishing content to platforms: {platforms}")

        # Perform publishing using the service
        result = await self.publishing_service.publish_content(
            content_data, platforms, schedule_immediate
        )

        return result

    async def schedule_publication(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Schedule content publication for a future date/time.
        """
        content_data = task_data.get("content_data", {})
        platforms = task_data.get("platforms", [])
        scheduled_datetime_str = task_data.get("scheduled_datetime")

        # Validate inputs
        if not platforms:
            raise ValueError("At least one platform must be specified for scheduling")

        if not content_data:
            raise ValueError("Content data must be provided for scheduling")

        if not scheduled_datetime_str:
            raise ValueError("Scheduled datetime must be provided for scheduling")

        try:
            from datetime import datetime

            scheduled_datetime = datetime.fromisoformat(
                scheduled_datetime_str.replace("Z", "+00:00")
            )
        except ValueError as err:
            raise ValueError(
                "Invalid datetime format. Use ISO format (e.g., 2023-12-01T10:00:00Z)"
            ) from err

        logger.info(
            f"Scheduling publication for {scheduled_datetime} to platforms: {platforms}"
        )

        # Schedule publication using the service
        result = await self.publishing_service.schedule_publication(
            content_data, platforms, scheduled_datetime
        )

        return result

    async def bulk_publish(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Publish multiple pieces of content to specified platforms.
        """
        content_list = task_data.get("content_list", [])
        platforms = task_data.get("platforms", [])

        # Validate inputs
        if not platforms:
            raise ValueError(
                "At least one platform must be specified for bulk publishing"
            )

        if not content_list:
            raise ValueError("Content list must be provided for bulk publishing")

        if len(content_list) > 50:  # Reasonable limit
            raise ValueError(
                "Bulk publish limit exceeded. Maximum 50 items per request."
            )

        logger.info(
            f"Bulk publishing {len(content_list)} items to platforms: {platforms}"
        )

        # Perform bulk publishing using the service
        result = await self.publishing_service.bulk_publish(content_list, platforms)

        return result

    async def get_publication_history(
        self, task_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Get the history of publications.
        """
        logger.info("Retrieving publication history")

        history = self.publishing_service.get_publication_history()

        return {"history": history, "count": len(history)}

    async def get_publishing_stats(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Get statistics about publishing activities.
        """
        logger.info("Retrieving publishing statistics")

        stats = self.publishing_service.get_publishing_statistics()

        return stats

    async def get_platform_status(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Get the current status of a publishing platform.
        """
        platform = task_data.get("platform")

        if not platform:
            raise ValueError("Platform name must be provided")

        logger.info(f"Getting status for platform: {platform}")

        # Get platform status using the service
        result = await self.publishing_service.get_platform_status(platform)

        return result

    def _check_dependencies(self) -> bool:
        """
        Check if publishing service dependencies are available.
        """
        # In a real implementation, this would check if platform APIs are reachable
        # For now, just check if the service is initialized
        return self.publishing_service is not None

    async def health_check(self) -> dict[str, Any]:
        """
        Perform a health check specific to the publishing component.
        """
        health_details = await super().health_check()

        # Add publishing-specific checks
        try:
            # Test basic functionality with a simple status check
            if self.config["supported_platforms"]:
                test_platform = self.config["supported_platforms"][0]
                platform_status = await self.publishing_service.get_platform_status(
                    test_platform
                )

                health_details["checks"]["platform_connectivity"] = True
                health_details["checks"]["platform_status"] = platform_status
            else:
                health_details["checks"]["platform_connectivity"] = False
                health_details["checks"][
                    "platform_status_error"
                ] = "No supported platforms configured"
        except Exception as e:
            health_details["checks"]["platform_connectivity"] = False
            health_details["checks"]["platform_status_error"] = str(e)

        # Update health based on connectivity check
        if not health_details["checks"]["platform_connectivity"]:
            self.health = "degraded"
            health_details["health"] = "degraded"

        return health_details


class PublishingMonitoringComponent(BaseComponent):
    """
    Component for monitoring publishing performance and analytics.
    """

    def __init__(
        self,
        component_id: str = "publishing_monitor_001",
        name: str = "PublishingMonitoringComponent",
        version: str = "1.0.0",
    ):
        super().__init__(component_id, name, version)

        self.publishing_service = PublishingService()
        self.analytics_cache = {}
        self.monitoring_enabled = True
        self.performance_thresholds = {
            "success_rate": 0.95,  # 95% success rate threshold
            "avg_publish_time": 60,  # 60 seconds average publish time threshold
            "error_rate": 0.05,  # 5% error rate threshold
        }

    async def execute(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute publishing monitoring task based on task type.
        """
        task_type = task_data.get("task_type", "unknown")
        logger.info(f"PublishingMonitoringComponent executing task: {task_type}")

        if task_type == "get_performance_metrics":
            return await self.get_performance_metrics(task_data)
        elif task_type == "get_platform_analytics":
            return await self.get_platform_analytics(task_data)
        elif task_type == "generate_publishing_report":
            return await self.generate_publishing_report(task_data)
        elif task_type == "set_performance_thresholds":
            return await self.set_performance_thresholds(task_data)
        elif task_type == "get_alerts":
            return await self.get_alerts(task_data)
        else:
            raise ValueError(f"Unknown publishing monitoring task type: {task_type}")

    async def get_performance_metrics(
        self, task_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Get performance metrics for publishing operations.
        """
        logger.info("Retrieving publishing performance metrics")

        # Get statistics from the publishing service
        stats = self.publishing_service.get_publishing_statistics()

        # Calculate additional metrics
        total_attempts = stats.get("total_attempts", 0)
        total_successes = stats.get("successful_publications", 0)
        total_failures = stats.get("failed_publications", 0)

        success_rate = (total_successes / total_attempts) if total_attempts > 0 else 0
        error_rate = (total_failures / total_attempts) if total_attempts > 0 else 0

        # Calculate platform-specific metrics
        platform_metrics = {}
        for platform, platform_stats in stats.get("platform_stats", {}).items():
            platform_total = platform_stats.get("attempts", 0)
            if platform_total > 0:
                platform_success_rate = (
                    platform_stats.get("successes", 0) / platform_total
                )
                platform_error_rate = platform_stats.get("failures", 0) / platform_total

                platform_metrics[platform] = {
                    "success_rate": platform_success_rate,
                    "error_rate": platform_error_rate,
                    "total_attempts": platform_total,
                    "successes": platform_stats.get("successes", 0),
                    "failures": platform_stats.get("failures", 0),
                }

        metrics = {
            "overall_success_rate": success_rate,
            "overall_error_rate": error_rate,
            "total_attempts": total_attempts,
            "total_successes": total_successes,
            "total_failures": total_failures,
            "platform_metrics": platform_metrics,
            "is_above_thresholds": {
                "success_rate": success_rate
                >= self.performance_thresholds["success_rate"],
                "error_rate": error_rate <= self.performance_thresholds["error_rate"],
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        return metrics

    async def get_platform_analytics(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Get analytics for specific platforms.
        """
        platform = task_data.get("platform")

        logger.info(
            f"Retrieving analytics for platform: {platform if platform else 'all'}"
        )

        # Get statistics from the publishing service
        stats = self.publishing_service.get_publishing_statistics()

        if platform:
            # Get specific platform analytics
            platform_stats = stats.get("platform_stats", {}).get(platform)
            if platform_stats:
                return {
                    "platform": platform,
                    "analytics": platform_stats,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            else:
                return {
                    "platform": platform,
                    "error": f"No analytics available for platform: {platform}",
                    "available_platforms": list(stats.get("platform_stats", {}).keys()),
                }
        else:
            # Get all platform analytics
            return {
                "all_platform_analytics": stats.get("platform_stats", {}),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def generate_publishing_report(
        self, task_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Generate a comprehensive publishing report.
        """
        logger.info("Generating comprehensive publishing report")

        # Get performance metrics
        performance_metrics = await self.get_performance_metrics({})

        # Get publication history
        history_result = await self.publishing_service.get_publication_history()

        # Get platform statuses
        platform_statuses = {}
        for platform in self.publishing_service.supported_platforms.keys():
            try:
                status = await self.publishing_service.get_platform_status(platform)
                platform_statuses[platform] = status
            except Exception as e:
                platform_statuses[platform] = {"error": str(e)}

        report = {
            "report_type": "publishing_comprehensive",
            "performance_metrics": performance_metrics,
            "publication_history": history_result,
            "platform_statuses": platform_statuses,
            "recommendations": self._generate_recommendations(performance_metrics),
            "report_generated_at": datetime.utcnow().isoformat(),
        }

        return report

    def _generate_recommendations(
        self, performance_metrics: dict[str, Any]
    ) -> list[dict[str, str]]:
        """
        Generate recommendations based on performance metrics.
        """
        recommendations = []

        # Success rate recommendation
        if (
            performance_metrics["overall_success_rate"]
            < self.performance_thresholds["success_rate"]
        ):
            recommendations.append(
                {
                    "type": "performance",
                    "priority": "high",
                    "content": f"Success rate ({performance_metrics['overall_success_rate']:.2%}) is below threshold ({self.performance_thresholds['success_rate']:.0%}). Investigate publishing failures.",
                }
            )

        # Error rate recommendation
        if (
            performance_metrics["overall_error_rate"]
            > self.performance_thresholds["error_rate"]
        ):
            recommendations.append(
                {
                    "type": "performance",
                    "priority": "high",
                    "content": f"Error rate ({performance_metrics['overall_error_rate']:.2%}) is above threshold ({self.performance_thresholds['error_rate']:.0%}). Review platform configurations.",
                }
            )

        # Platform-specific recommendations
        for platform, metrics in performance_metrics.get(
            "platform_metrics", {}
        ).items():
            if metrics["error_rate"] > self.performance_thresholds["error_rate"]:
                recommendations.append(
                    {
                        "type": "platform_specific",
                        "priority": "medium",
                        "content": f"Platform '{platform}' has high error rate ({metrics['error_rate']:.2%}). Consider reviewing credentials or reducing publishing frequency.",
                    }
                )

        return recommendations

    async def set_performance_thresholds(
        self, task_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Set performance thresholds for monitoring.
        """
        new_thresholds = task_data.get("thresholds", {})

        # Update thresholds
        for key, value in new_thresholds.items():
            if key in self.performance_thresholds:
                self.performance_thresholds[key] = value

        return {
            "thresholds_updated": True,
            "new_thresholds": self.performance_thresholds,
        }

    async def get_alerts(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Get publishing-related alerts.
        """
        # Get current performance metrics
        metrics = await self.get_performance_metrics({})

        alerts = []

        # Check for threshold breaches
        if (
            metrics["overall_success_rate"]
            < self.performance_thresholds["success_rate"]
        ):
            alerts.append(
                {
                    "type": "success_rate_low",
                    "severity": "high",
                    "message": f"Success rate is low: {metrics['overall_success_rate']:.2%} (threshold: {self.performance_thresholds['success_rate']:.0%})",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        if metrics["overall_error_rate"] > self.performance_thresholds["error_rate"]:
            alerts.append(
                {
                    "type": "error_rate_high",
                    "severity": "high",
                    "message": f"Error rate is high: {metrics['overall_error_rate']:.2%} (threshold: {self.performance_thresholds['error_rate']:.0%})",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        # Platform-specific alerts
        for platform, platform_metrics in metrics.get("platform_metrics", {}).items():
            if (
                platform_metrics["error_rate"]
                > self.performance_thresholds["error_rate"]
            ):
                alerts.append(
                    {
                        "type": "platform_error_rate_high",
                        "severity": "medium",
                        "platform": platform,
                        "message": f"Platform '{platform}' error rate is high: {platform_metrics['error_rate']:.2%}",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

        return {
            "alerts": alerts,
            "count": len(alerts),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _check_dependencies(self) -> bool:
        """
        Check if publishing monitoring dependencies are available.
        """
        return self.publishing_service is not None

    async def health_check(self) -> dict[str, Any]:
        """
        Perform a health check specific to the publishing monitoring component.
        """
        health_details = await super().health_check()

        # Add monitoring-specific checks
        health_details["checks"]["monitoring_enabled"] = self.monitoring_enabled
        health_details["checks"]["performance_thresholds_configured"] = (
            len(self.performance_thresholds) > 0
        )

        return health_details
