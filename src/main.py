"""
Project Chimera - Autonomous AI Influencer Infrastructure
Main Application Entry Point

This module demonstrates the hierarchical swarm architecture with supervisor orchestration
as outlined in the research notes.
"""

import asyncio
import logging
from datetime import datetime

# Import all agent types
from src.agents.supervisor_agent import SupervisorAgent
from src.database.connection import init_db
from src.services.agent_factory import initialize_agents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("logs/chimera.log")],
)
logger = logging.getLogger("chimera-main")


async def demo_content_creation_workflow(supervisor: SupervisorAgent):
    """
    Demonstrate the complete content creation workflow.
    """
    logger.info("Starting content creation workflow demo...")

    # Define the task for content creation
    content_creation_task = {
        "task_id": f"demo_task_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "task_type": "coordinate_content_creation",
        "topic": "AI and Machine Learning Trends",
        "keywords": ["AI", "Machine Learning", "Technology", "Future"],
        "timeframe": "7d",
        "content_type": "educational",
        "platform": "youtube",
    }

    # Execute the workflow
    result = await supervisor.process_task(content_creation_task)

    logger.info("Content creation workflow completed")
    return result


async def demo_trend_analysis(supervisor: SupervisorAgent):
    """
    Demonstrate trend analysis capabilities.
    """
    logger.info("Starting trend analysis demo...")

    trend_analysis_task = {
        "task_id": f"trend_task_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "task_type": "analyze_trends",
        "topic": "AI Technology",
        "keywords": ["AI", "Machine Learning", "Neural Networks", "Deep Learning"],
        "timeframe": "30d",
    }

    result = await supervisor.process_task(trend_analysis_task)

    logger.info("Trend analysis completed")
    return result


async def main():
    """
    Main entry point for Project Chimera.
    """
    logger.info("Starting Project Chimera - Autonomous AI Influencer Infrastructure")

    # Initialize database
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")

    # Initialize all agents
    supervisor = await initialize_agents()

    # Run demonstration workflows
    logger.info("\n" + "=" * 60)
    logger.info("DEMONSTRATING PROJECT CHIMERA WORKFLOWS")
    logger.info("=" * 60)

    # Demo 1: Content Creation Workflow
    logger.info("\n--- DEMO 1: Content Creation Workflow ---")
    content_result = await demo_content_creation_workflow(supervisor)
    print(f"Content Creation Result: {content_result['status']}")

    # Demo 2: Trend Analysis
    logger.info("\n--- DEMO 2: Trend Analysis ---")
    trend_result = await demo_trend_analysis(supervisor)
    print(f"Trend Analysis Result: {trend_result['status']}")

    # Get final status of all agents
    logger.info("\n--- AGENT STATUS REPORT ---")
    statuses = await supervisor.orchestrator.get_all_statuses()
    for _agent_id, status in statuses.items():
        print(
            f"Agent: {status['name']} | Status: {status['status']} | Updated: {status['last_updated']}"
        )

    logger.info("\nProject Chimera demonstration completed successfully!")
    logger.info("Next steps:")
    logger.info("- Connect to actual API services for trend data")
    logger.info("- Implement real video generation capabilities")
    logger.info("- Deploy to cloud infrastructure")
    logger.info("- Add monitoring and alerting")


if __name__ == "__main__":
    # Run the main application
    asyncio.run(main())
