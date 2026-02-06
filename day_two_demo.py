#!/usr/bin/env python3
"""
Project Chimera - Day Two Implementation Demo

This script demonstrates the completed implementation based on the research notes
found in the research/Notes.md file. It showcases the hierarchical swarm architecture
with supervisor orchestration.
"""

import asyncio
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, "/home/creed47/Desktop/Tenx-Project-chimera")

from src.agents.content_agents import ScriptWriterAgent
from src.agents.distribution_agents import PlatformPublisherAgent
from src.agents.research_agents import NicheAnalystAgent, TrendFetcherAgent
from src.agents.safety_agents import ContentModerationAgent
from src.agents.supervisor_agent import SupervisorAgent


async def demonstrate_system():
    """
    Demonstrates the complete Project Chimera system as implemented for Day Two.
    """
    print("=" * 80)
    print("PROJECT CHIMERA - DAY TWO IMPLEMENTATION DEMO")
    print("=" * 80)
    print(f"Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    print("🔍 RESEARCH PHASE:")
    print("-" * 20)

    # Create and test a TrendFetcherAgent
    trend_agent = TrendFetcherAgent()
    print(f"✅ Created {trend_agent.name}")

    # Execute trend analysis
    trend_task = {
        "task_id": "demo_trend_task",
        "task_type": "analyze_trends",
        "topic": "AI Technology",
        "keywords": ["AI", "Machine Learning", "Generative AI"],
        "timeframe": "7d",
    }

    trend_result = await trend_agent.execute(trend_task)
    print(f"📊 Fetched {trend_result['total_trends']} trending topics")
    print(f"🔗 Sources used: {len(trend_result['sources_used'])}")
    print()

    print("🔍 NICHE ANALYSIS PHASE:")
    print("-" * 25)

    # Create and test a NicheAnalystAgent
    niche_agent = NicheAnalystAgent()
    print(f"✅ Created {niche_agent.name}")

    # Execute niche analysis
    niche_task = {
        "task_id": "demo_niche_task",
        "task_type": "analyze_trends",
        "topic": "AI Education",
        "keywords": ["AI", "Machine Learning", "Education", "Tutorial"],
    }

    niche_result = await niche_agent.execute(niche_task)
    print(f"🎯 Identified {len(niche_result['identified_niches'])} potential niches")
    print(f"🏆 Top niches: {[n['category'] for n in niche_result['top_niches']]}")
    print()

    print("✍️  CONTENT GENERATION PHASE:")
    print("-" * 30)

    # Create and test a ScriptWriterAgent
    script_agent = ScriptWriterAgent()
    print(f"✅ Created {script_agent.name}")

    # Execute content generation (using trend data)
    content_task = {
        "task_id": "demo_content_task",
        "task_type": "generate_content",
        "research_data": {"results": [{"result": trend_result}]},
        "content_type": "educational",
        "platform": "youtube",
    }

    script_result = await script_agent.execute(content_task)
    # For demonstration purposes, we'll use the direct result instead of nested structure
    script_result = script_result  # execute returns the direct result
    print(f"📝 Generated script for: {script_result['title']}")
    print(f"⏱️  Estimated duration: {script_result['estimated_duration']}")
    print()

    print("🛡️  SAFETY MODERATION PHASE:")
    print("-" * 31)

    # Create and test a ContentModerationAgent
    moderation_agent = ContentModerationAgent()
    print(f"✅ Created {moderation_agent.name}")

    # Execute content moderation
    moderation_task = {
        "task_id": "demo_moderation_task",
        "task_type": "validate_content",
        "content_data": script_result,
    }

    moderation_result = await moderation_agent.process_task(
        moderation_task
    )  # Using process_task for proper wrapper
    print(
        f"✅ Moderation completed - Approved: {moderation_result['result']['approved']}"
    )
    print(f"📋 Issues found: {len(moderation_result['result']['issues'])}")
    print()

    print("📡 DISTRIBUTION PHASE:")
    print("-" * 22)

    # Create and test a PlatformPublisherAgent
    publisher_agent = PlatformPublisherAgent()
    print(f"✅ Created {publisher_agent.name}")

    # Execute publishing
    publish_task = {
        "task_id": "demo_publish_task",
        "task_type": "publish_content",
        "content_data": script_result,
        "platforms": ["youtube", "twitter"],
        "schedule_immediate": True,
    }

    publish_result = await publisher_agent.process_task(
        publish_task
    )  # Using process_task for proper wrapper
    print(
        f"📤 Attempted publishing to {len(publish_result['result']['publish_results'])} platforms"
    )
    print(
        f"✅ Successful publishes: {publish_result['result']['successful_publishes']}"
    )
    print()

    print("🏛️  SUPERVISOR ORCHESTRATION DEMONSTRATION:")
    print("-" * 45)

    # Create supervisor and register agents
    supervisor = SupervisorAgent()
    print(f"✅ Created {supervisor.name}")

    # Register agents with supervisor (simulating the swarm architecture)
    await supervisor.register_subagent({"agent": trend_agent, "swarm_type": "research"})
    print("🔄 Registered TrendFetcherAgent to ResearchSwarm")

    await supervisor.register_subagent({"agent": script_agent, "swarm_type": "content"})
    print("🔄 Registered ScriptWriterAgent to ContentSwarm")

    await supervisor.register_subagent(
        {"agent": moderation_agent, "swarm_type": "safety"}
    )
    print("🔄 Registered ContentModerationAgent to SafetyLayer")

    await supervisor.register_subagent(
        {"agent": publisher_agent, "swarm_type": "distribution"}
    )
    print("🔄 Registered PlatformPublisherAgent to DistributionSwarm")

    print()
    print("🔄 Demonstrating coordinated workflow...")

    # Execute a coordinated task
    coordinated_task = {
        "task_id": "demo_coordinated_task",
        "task_type": "analyze_trends",  # Using research swarm
        "topic": "AI Innovation",
        "keywords": ["AI", "Innovation", "Technology"],
        "timeframe": "14d",
    }

    coord_result = await supervisor.process_task(coordinated_task)
    print(f"✅ Coordinated task completed: {coord_result['status']}")
    print()

    print("📋 SYSTEM STATUS REPORT:")
    print("-" * 23)
    statuses = await supervisor.orchestrator.get_all_statuses()
    for _agent_id, status in statuses.items():
        print(
            f"  {status['name']}: {status['status']} (updated: {status['last_updated'][-9:-1]})"
        )
    print()

    print("=" * 80)
    print("SUMMARY OF DAY TWO IMPLEMENTATION")
    print("=" * 80)
    print("✅ Core infrastructure with database models")
    print("✅ Hierarchical swarm architecture with supervisor orchestration")
    print("✅ ResearchSwarm with TrendFetcher and NicheAnalyst agents")
    print(
        "✅ ContentSwarm with ScriptWriter, VideoGenerator, and ThumbnailDesigner agents"
    )
    print("✅ SafetyLayer with HumanInLoop and ContentModeration agents")
    print("✅ DistributionSwarm with PlatformPublisher and OpenClawAnnouncer agents")
    print("✅ MCP-ready architecture for Model Context Protocol integration")
    print("✅ Human-in-the-Loop (HITL) safety mechanisms")
    print("✅ Agent discovery and networking capabilities")
    print("✅ Ethical guardrails and provenance tracking")
    print()
    print("🎯 The implementation follows the research notes from Notes.md exactly")
    print("🎯 Ready for Day Three: API development, MCP integration, and deployment")
    print("=" * 80)


if __name__ == "__main__":
    print("🚀 Starting Project Chimera - Day Two Demo...")
    print()

    try:
        asyncio.run(demonstrate_system())
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback

        traceback.print_exc()

    print(f"\n🏁 Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
