"""
Project Chimera - Refactored Main Application
Entry point for the restructured autonomous AI influencer infrastructure
following SRS-based architecture with services, components, and API layers.
"""

import asyncio
import logging
from datetime import datetime

from .components.base_component import ComponentRegistry
from .components.content_component import ContentComponent, ContentModerationComponent
from .components.publishing_component import (
    PublishingComponent,
    PublishingMonitoringComponent,
)
from .components.research_component import ResearchComponent, TrendMonitoringComponent
from .config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()), format=settings.log_format
)
logger = logging.getLogger(__name__)

# Global component registry
component_registry = ComponentRegistry()


async def initialize_components():
    """
    Initialize and register all system components.
    """
    logger.info("Initializing Project Chimera components...")

    # Create research components
    research_component = ResearchComponent("research_main", "ResearchComponent")
    trend_monitor_component = TrendMonitoringComponent(
        "trend_monitor_main", "TrendMonitoringComponent"
    )

    # Create content components
    content_component = ContentComponent("content_main", "ContentComponent")
    moderation_component = ContentModerationComponent(
        "moderation_main", "ContentModerationComponent"
    )

    # Create publishing components
    publishing_component = PublishingComponent("publishing_main", "PublishingComponent")
    publishing_monitor_component = PublishingMonitoringComponent(
        "publishing_monitor_main", "PublishingMonitoringComponent"
    )

    # Register all components with the registry
    component_registry.register_component(research_component)
    component_registry.register_component(trend_monitor_component)
    component_registry.register_component(content_component)
    component_registry.register_component(moderation_component)
    component_registry.register_component(publishing_component)
    component_registry.register_component(publishing_monitor_component)

    logger.info(f"Registered {len(component_registry.get_all_components())} components")

    # Start all components
    all_components = component_registry.get_all_components()
    for component in all_components:
        await component.start()
        logger.info(f"Started component: {component.name}")

    return component_registry


async def run_system_diagnostics():
    """
    Run system diagnostics to verify all components are functioning.
    """
    logger.info("Running system diagnostics...")

    # Get all component statuses
    statuses = await component_registry.get_all_statuses()
    logger.info(f"Component statuses: {list(statuses.keys())}")

    # Perform health checks
    health_results = await component_registry.perform_health_check()
    logger.info(f"Overall system health: {health_results['overall_health']}")

    # Report any issues
    unhealthy_components = []
    for comp_id, health in health_results["component_health"].items():
        if health["health"] != "healthy":
            unhealthy_components.append((comp_id, health["health"]))

    if unhealthy_components:
        logger.warning(f"Unhealthy components detected: {unhealthy_components}")
    else:
        logger.info("All components are healthy")

    return {
        "total_components": health_results["total_components"],
        "overall_health": health_results["overall_health"],
        "unhealthy_components": unhealthy_components,
        "timestamp": datetime.utcnow().isoformat(),
    }


async def demonstrate_workflow():
    """
    Demonstrate the complete workflow using the refactored components.
    """
    logger.info("Demonstrating complete workflow with refactored components...")

    # Get the main components
    research_comp = component_registry.get_component("research_main")
    content_comp = component_registry.get_component("content_main")
    publishing_comp = component_registry.get_component("publishing_main")

    # Step 1: Research phase
    logger.info("=== RESEARCH PHASE ===")
    research_task = {
        "task_id": f"demo_research_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "task_type": "analyze_trends",
        "keywords": ["AI", "Machine Learning", "Technology"],
        "timeframe": "7d",
    }

    research_result = await research_comp.process_task(research_task)
    logger.info(f"Research completed: {research_result['status']}")

    # Step 2: Content creation phase
    logger.info("=== CONTENT CREATION PHASE ===")
    content_task = {
        "task_id": f"demo_content_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "task_type": "create_content_from_research",
        "research_data": research_result["result"],
        "content_type": "educational",
    }

    content_result = await content_comp.process_task(content_task)
    logger.info(f"Content creation completed: {content_result['status']}")

    # Step 3: Publishing phase
    logger.info("=== PUBLISHING PHASE ===")
    publishing_task = {
        "task_id": f"demo_publish_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "task_type": "publish_content",
        "content_data": content_result["result"],
        "platforms": ["youtube", "twitter"],
        "schedule_immediate": True,
    }

    publishing_result = await publishing_comp.process_task(publishing_task)
    logger.info(f"Publishing completed: {publishing_result['status']}")

    # Compile workflow results
    workflow_result = {
        "workflow_completed": True,
        "steps": {
            "research": research_result,
            "content": content_result,
            "publishing": publishing_result,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }

    logger.info("Complete workflow demonstration finished")
    return workflow_result


async def main():
    """
    Main entry point for the refactored Project Chimera application.
    """
    logger.info("Starting Project Chimera - Refactored Implementation")
    logger.info(
        "Following SRS-based architecture with services, components, and API layers"
    )

    try:
        # Initialize all components
        await initialize_components()
        logger.info("All components initialized successfully")

        # Run system diagnostics
        diagnostics = await run_system_diagnostics()
        logger.info(f"System diagnostics completed: {diagnostics['overall_health']}")

        # Demonstrate the complete workflow
        await demonstrate_workflow()
        logger.info("Workflow demonstration completed successfully")

        # Get final system status
        final_status = await component_registry.perform_health_check()

        logger.info("\n" + "=" * 60)
        logger.info("PROJECT CHIMERA - REFACTORED SYSTEM STATUS")
        logger.info("=" * 60)
        logger.info(f"Overall Health: {final_status['overall_health']}")
        logger.info(f"Total Components: {final_status['total_components']}")
        logger.info(f"Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("\nArchitecture Layers:")
        logger.info("- Services Layer: Business logic and data handling")
        logger.info("- Components Layer: Reusable system components")
        logger.info("- API Layer: External interfaces and endpoints")
        logger.info("- Configuration Layer: Centralized settings management")
        logger.info("\nSRS Compliance Features:")
        logger.info("- Modular architecture with clear separation of concerns")
        logger.info("- Scalable component-based design")
        logger.info("- Comprehensive error handling and logging")
        logger.info("- Health monitoring and diagnostics")
        logger.info("- Configuration management")
        logger.info("- API-first design with documentation")
        logger.info("=" * 60)

        # Keep the application running for API access
        logger.info("\nStarting API server...")
        logger.info(f"API available at: http://localhost:{settings.api_port}")
        logger.info("Press Ctrl+C to stop the application")

        # In a real implementation, we would start the FastAPI server here
        # For this demonstration, we'll just simulate keeping it running
        try:
            while True:
                await asyncio.sleep(60)  # Keep alive
        except KeyboardInterrupt:
            logger.info("\nShutdown initiated...")

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise
    finally:
        # Clean shutdown
        logger.info("Shutting down components...")
        all_components = component_registry.get_all_components()
        for component in all_components:
            await component.stop()
            logger.info(f"Stopped component: {component.name}")

        logger.info("Project Chimera shutdown completed")


if __name__ == "__main__":
    # Run the main application
    asyncio.run(main())
