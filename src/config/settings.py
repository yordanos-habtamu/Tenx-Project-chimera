"""
Configuration Settings for Project Chimera
Centralized configuration management using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from enum import Enum
import os


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """
    Application settings class that loads configuration from environment variables
    and .env files with proper validation.
    """
    
    # Environment
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1
    api_reload: bool = True
    api_log_level: str = "info"
    
    # Database Configuration
    database_url: str = "postgresql://chimera_user:chimera_password@localhost/chimera_db"
    database_pool_size: int = 20
    database_pool_overflow: int = 0
    database_echo: bool = False
    
    # Security Configuration
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # External API Keys and Credentials
    google_trends_api_key: Optional[str] = None
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    youtube_api_key: Optional[str] = None
    instagram_access_token: Optional[str] = None
    tiktok_client_key: Optional[str] = None
    linkedin_client_id: Optional[str] = None
    linkedin_client_secret: Optional[str] = None

    # OpenRouter Configuration (for Content Generation)
    openrouter_api_key: Optional[str] = None
    openrouter_model: str = "liquid/lfm-40b"  # Default model, can be changed
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Video Generation API Configuration
    video_gen_api_key: Optional[str] = None
    video_gen_provider: str = "generic"  # generic, heygen, d-id, runway, luma
    video_gen_endpoint: Optional[str] = None
    
    # Content Generation Settings
    content_generation_timeout: int = 600  # Increased to 10 minutes for video gen
    max_content_length: int = 50000  # Max characters for generated content
    min_content_length: int = 100    # Min characters for generated content
    supported_content_types: List[str] = ["educational", "review", "tutorial", "news", "opinion"]
    
    # Publishing Settings
    publishing_retry_attempts: int = 3
    publishing_retry_delay: int = 5  # seconds
    max_simultaneous_publishes: int = 5
    publishing_timeout: int = 600  # 10 minutes
    
    # Agent Configuration
    agent_max_concurrent_tasks: int = 10
    agent_task_timeout: int = 120  # 2 minutes
    agent_health_check_interval: int = 30  # seconds
    agent_registration_timeout: int = 60  # seconds
    
    # MCP (Model Context Protocol) Configuration
    mcp_enabled: bool = True
    mcp_endpoint: str = "http://localhost:3000"
    mcp_timeout: int = 30
    mcp_max_retries: int = 3
    
    # Monitoring and Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_structured_logging: bool = True
    metrics_enabled: bool = False
    metrics_port: int = 9090
    
    # Feature Flags
    enable_content_moderation: bool = True
    enable_human_approval: bool = True
    enable_auto_publishing: bool = True
    enable_social_listening: bool = True
    enable_performance_analytics: bool = True
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # File Storage
    file_upload_max_size: int = 50 * 1024 * 1024  # 50 MB
    allowed_file_types: List[str] = ["jpg", "jpeg", "png", "gif", "mp4", "mov", "avi"]
    file_storage_path: str = "./uploads"
    
    # Email Configuration (for notifications)
    smtp_server: str = "localhost"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    notification_email_from: str = "noreply@chimera.ai"
    
    # Cache Configuration
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour
    redis_url: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"  # Allow extra fields not defined in the model


class AgentConfig:
    """
    Configuration specifically for agent operations
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    @property
    def research_agent_config(self) -> dict:
        """Configuration for research agents"""
        return {
            "max_concurrent_requests": 5,
            "request_timeout": 30,
            "cache_enabled": True,
            "cache_ttl": 1800,  # 30 minutes
            "retry_attempts": 3
        }
    
    @property
    def content_agent_config(self) -> dict:
        """Configuration for content agents"""
        return {
            "generation_timeout": self.settings.content_generation_timeout,
            "max_content_length": self.settings.max_content_length,
            "min_content_length": self.settings.min_content_length,
            "supported_types": self.settings.supported_content_types
        }
    
    @property
    def publishing_agent_config(self) -> dict:
        """Configuration for publishing agents"""
        return {
            "max_simultaneous_publishes": self.settings.max_simultaneous_publishes,
            "retry_attempts": self.settings.publishing_retry_attempts,
            "retry_delay": self.settings.publishing_retry_delay,
            "timeout": self.settings.publishing_timeout
        }
    
    @property
    def safety_agent_config(self) -> dict:
        """Configuration for safety agents"""
        return {
            "moderation_enabled": self.settings.enable_content_moderation,
            "human_approval_required": self.settings.enable_human_approval,
            "auto_publishing_enabled": self.settings.enable_auto_publishing
        }


class DatabaseConfig:
    """
    Configuration specifically for database operations
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    @property
    def connection_params(self) -> dict:
        """Database connection parameters"""
        return {
            "pool_size": self.settings.database_pool_size,
            "pool_overflow": self.settings.database_pool_overflow,
            "echo": self.settings.database_echo
        }
    
    @property
    def migration_config(self) -> dict:
        """Database migration configuration"""
        return {
            "alembic_ini_path": "./alembic.ini",
            "migration_path": "./migrations",
            "auto_generate": True
        }


class APISettings:
    """
    Configuration specifically for API operations
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    @property
    def cors_config(self) -> dict:
        """CORS configuration"""
        return {
            "allow_origins": ["*"] if self.settings.environment == Environment.DEVELOPMENT else [],
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }
    
    @property
    def rate_limit_config(self) -> dict:
        """Rate limiting configuration"""
        return {
            "requests": self.settings.rate_limit_requests,
            "window_seconds": self.settings.rate_limit_window
        }


# Global settings instance
settings = Settings()

# Convenience instances
agent_config = AgentConfig(settings)
database_config = DatabaseConfig(settings)
api_config = APISettings(settings)

# Export commonly used settings
ENVIRONMENT = settings.environment
DEBUG = settings.debug
DATABASE_URL = settings.database_url
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# Platform API keys
GOOGLE_TRENDS_API_KEY = settings.google_trends_api_key
TWITTER_API_KEY = settings.twitter_api_key
YOUTUBE_API_KEY = settings.youtube_api_key
INSTAGRAM_ACCESS_TOKEN = settings.instagram_access_token
TIKTOK_CLIENT_KEY = settings.tiktok_client_key
LINKEDIN_CLIENT_ID = settings.linkedin_client_id
LINKEDIN_CLIENT_SECRET = settings.linkedin_client_secret

# Feature flags
ENABLE_CONTENT_MODERATION = settings.enable_content_moderation
ENABLE_HUMAN_APPROVAL = settings.enable_human_approval
ENABLE_AUTO_PUBLISHING = settings.enable_auto_publishing
ENABLE_SOCIAL_LISTENING = settings.enable_social_listening
ENABLE_PERFORMANCE_ANALYTICS = settings.enable_performance_analytics

# OpenRouter Settings
OPENROUTER_API_KEY = settings.openrouter_api_key
OPENROUTER_MODEL = settings.openrouter_model
OPENROUTER_BASE_URL = settings.openrouter_base_url

# Video Generation Settings
VIDEO_GEN_API_KEY = settings.video_gen_api_key
VIDEO_GEN_PROVIDER = settings.video_gen_provider
VIDEO_GEN_ENDPOINT = settings.video_gen_endpoint
CONTENT_GENERATION_TIMEOUT = settings.content_generation_timeout