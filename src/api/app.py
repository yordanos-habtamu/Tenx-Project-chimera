"""
Main API Application for Project Chimera
FastAPI application with all routes and configuration
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from ..config.logging_config import setup_logging
from ..core.base_agent import AgentOrchestrator
from ..database.connection import init_db
from ..services.agent_factory import initialize_agents
from .dashboard import router as dashboard_router
from .routers import router

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown events.
    """
    logger.info("Starting Project Chimera API...")

    # Startup
    logger.info("Initializing database...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        logger.warning(
            "Continuing without database connection. Some features may fail."
        )
        # Do not raise, allow app to start for frontend testing

    # Initialize agent orchestrator
    logger.info("Initializing agent orchestrator...")
    try:
        supervisor = await initialize_agents()
        app.state.orchestrator = supervisor.orchestrator
        logger.info("Agent orchestrator initialized (Real Agents)")
    except Exception as e:
        logger.error(f"Failed to initialize orchestrator: {str(e)}")
        # Fallback to empty orchestrator if init fails
        app.state.orchestrator = AgentOrchestrator()
        raise

    logger.info("Project Chimera API started successfully")

    yield  # This is where the application runs

    # Shutdown
    logger.info("Shutting down Project Chimera API...")
    logger.info("API shutdown completed")


# Create FastAPI application
app = FastAPI(
    title="Project Chimera - Autonomous AI Influencer API",
    description="API for the autonomous AI influencer infrastructure",
    version="1.0.0",
    lifespan=lifespan,
    contact={
        "name": "Project Chimera Team",
        "email": "team@chimera.ai",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Expose headers for client-side access
    expose_headers=["Access-Control-Allow-Origin"],
)

# Include API routes

# Include API routes
app.include_router(router)
app.include_router(dashboard_router, prefix="/api/v1")

# Mount Static Files for Dashboard
# Ensure directory exists before mounting to avoid errors if user didn't run mkdir
if os.path.exists("src/static"):
    app.mount(
        "/dashboard", StaticFiles(directory="src/static", html=True), name="static"
    )


@app.get("/")
async def root():
    """
    Redirect root to dashboard.
    """
    return RedirectResponse(url="/dashboard")


@app.get("/api/v1/info")
async def api_info():
    """
    Get information about the API.
    """
    return {
        "name": "Project Chimera API",
        "version": "1.0.0",
        "description": "Autonomous AI Influencer Infrastructure API",
        "endpoints": [
            "/api/v1/health",
            "/api/v1/research/*",
            "/api/v1/content/*",
            "/api/v1/publish/*",
            "/api/v1/publish/*",
            "/api/v1/dashboard/*",
            "/api/v1/agents/*",
        ],
        "documentation": "/docs",
        "contact": {"email": "team@chimera.ai"},
    }


# Error handlers


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """
    Handle 404 errors.
    """
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"Endpoint {request.url.path} not found",
            "status_code": 404,
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """
    Handle 500 errors.
    """
    logger.error(f"Internal server error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An internal error occurred",
            "status_code": 500,
        },
    )


# Additional utility endpoints
@app.get("/api/v1/config")
async def get_config():
    """
    Get current API configuration.
    """
    return {
        "database_url": os.getenv("DATABASE_URL", "postgresql://localhost/chimera_db"),
        "debug_mode": os.getenv("DEBUG", "false").lower() == "true",
        "allowed_origins": os.getenv("ALLOWED_ORIGINS", "*"),
        "max_content_length": os.getenv("MAX_CONTENT_LENGTH", "50MB"),
        "api_version": "v1",
    }


@app.get("/api/v1/status")
async def detailed_status():
    """
    Get detailed system status.
    """
    # In a real implementation, this would check actual service status
    return {
        "status": "operational",
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        "services": {
            "database": "connected",
            "research_service": "operational",
            "content_service": "operational",
            "publishing_service": "operational",
            "agent_orchestrator": "initialized",
        },
        "memory_usage": "N/A",  # Would be implemented with actual monitoring
        "cpu_usage": "N/A",  # Would be implemented with actual monitoring
        "active_connections": 0,  # Would be tracked in real implementation
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("RELOAD", "false").lower() == "true",
    )
