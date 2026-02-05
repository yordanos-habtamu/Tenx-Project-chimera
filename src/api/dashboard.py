"""
Dashboard API Router
Provides endpoints for the User Dashboard to monitor and control the system.
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import os

from ..config.settings import settings
from ..core.base_agent import AgentStatus

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
logger = logging.getLogger(__name__)

@router.get("/logs")
async def get_system_logs(limit: int = 50, level: str = "INFO"):
    """
    Get recent system logs from the log file.
    """
    log_file = "logs/chimera.log"
    logs = []
    
    if os.path.exists(log_file):
        try:
            with open(log_file, "r") as f:
                # Read all lines and reverse to get newest first
                lines = f.readlines()[::-1]
                
                for line in lines:
                    if len(logs) >= limit:
                        break
                    
                    # Basic parsing of log format: 'Timestamp - Logger - Level - Message'
                    parts = line.split(" - ", 3)
                    if len(parts) == 4:
                        timestamp, source, log_level, message = parts
                        
                        # Filter by level if needed (simple string match)
                        if level != "ALL" and level not in log_level:
                            continue
                            
                        logs.append({
                            "timestamp": timestamp,
                            "level": log_level,
                            "source": source,
                            "message": message.strip()
                        })
        except Exception as e:
            logger.error(f"Error reading log file: {e}")
            return {"logs": [], "error": "Failed to read logs"}
            
    return {
        "logs": logs,
        "count": len(logs),
        "note": "Real-time logs from logs/chimera.log"
    }

@router.get("/config")
async def get_system_config():
    """
    Get current system configuration (safetied).
    """
    # Create a safe copy of settings
    safe_config = settings.model_dump(exclude={"secret_key", "openrouter_api_key", "video_gen_api_key"})
    return {
        "environment": safe_config.get("environment"),
        "features": {k: v for k, v in safe_config.items() if k.startswith("enable_")},
        "limits": {
            "content_timeout": safe_config.get("content_generation_timeout"),
            "max_concurrent_tasks": safe_config.get("agent_max_concurrent_tasks")
        },
        "api_config": {
            "openrouter_model": safe_config.get("openrouter_model"),
            "video_provider": safe_config.get("video_gen_provider")
        }
    }

@router.post("/agents/{agent_id}/control")
async def control_agent(agent_id: str, action: str, request: Request):
    """
    Control a specific agent (start, stop, pause, restart).
    """
    valid_actions = ["start", "stop", "pause", "restart"]
    if action not in valid_actions:
        raise HTTPException(status_code=400, detail=f"Invalid action. Must be one of {valid_actions}")
    
    # Access the orchestrator from the app state
    orchestrator = getattr(request.app.state, "orchestrator", None)
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    # Find agent
    agent = orchestrator.agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

    # Perform action (simulated logic for now as BaseAgent needs extensions for real control)
    previous_status = agent.status
    
    if action == "pause":
        agent.status = AgentStatus.PAUSED
    elif action == "start" or action == "restart":
        agent.status = AgentStatus.IDLE
    elif action == "stop":
        agent.status = AgentStatus.IDLE # 'Stop' often means reset to IDLE in soft-systems
        
    logger.info(f"Agent {agent_id} control action '{action}' executed. Status: {previous_status} -> {agent.status}")

    return {
        "agent_id": agent_id,
        "action": action,
        "status": "success",
        "current_state": agent.status.value
    }

@router.post("/tasks/manual")
async def trigger_manual_task(task_type: str, payload: Dict[str, Any], request: Request):
    """
    Manually trigger a task in the system.
    """
    orchestrator = getattr(request.app.state, "orchestrator", None)
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    # Determine target agent based on task type (simplified routing logic)
    target_agent_id = None
    if task_type == "analyze_trends":
        target_agent_id = "trend_fetcher_001" # Default ID
    elif task_type == "generate_content":
        target_agent_id = "script_writer_001"
    
    if not target_agent_id:
        raise HTTPException(status_code=400, detail=f"Unknown or router-less task type: {task_type}")

    # Create task object
    task = {
        "task_id": f"manual_{datetime.utcnow().timestamp()}",
        "task_type": task_type,
        **payload
    }

    # Execute (Note: In a real system this might be backgrounded)
    try:
        if target_agent_id in orchestrator.agents:
            result = await orchestrator.assign_task(target_agent_id, task)
            return {"status": "success", "task_id": task["task_id"], "result": result}
        else:
             raise HTTPException(status_code=404, detail=f"Target agent {target_agent_id} not found/active")
    except Exception as e:
        logger.error(f"Manual task failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
