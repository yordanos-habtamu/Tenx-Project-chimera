"""
Base Component Class for Project Chimera
Defines the common interface and functionality for all system components
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from datetime import datetime
import asyncio
import logging
from enum import Enum

from ..config.settings import settings

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


class ComponentStatus(Enum):
    """Enumeration of possible component statuses"""
    INITIALIZED = "initialized"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class ComponentHealth(Enum):
    """Enumeration of possible component health states"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class BaseComponent(ABC):
    """
    Abstract base class for all components in the Project Chimera system.
    Provides common functionality and interface for component implementations.
    """
    
    def __init__(self, component_id: str, name: str, version: str = "1.0.0"):
        self.component_id = component_id
        self.name = name
        self.version = version
        self.status = ComponentStatus.INITIALIZED
        self.health = ComponentHealth.UNKNOWN
        self.created_at = datetime.utcnow()
        self.last_updated = datetime.utcnow()
        self.dependencies = []
        self.config = {}
        self.metrics = {}
        self.task_queue = asyncio.Queue()
        self.is_running = False
        
        # Initialize with default configuration
        self._initialize_config()
        
        # Mark as ready after initialization
        self.status = ComponentStatus.READY
        logger.info(f"Component {self.name} ({self.component_id}) initialized and ready")
    
    def _initialize_config(self):
        """
        Initialize component configuration with default values.
        Subclasses can override this method to set specific configurations.
        """
        self.config = {
            "component_id": self.component_id,
            "name": self.name,
            "version": self.version,
            "status": self.status.value,
            "health": self.health.value,
            "created_at": self.created_at.isoformat(),
            "max_concurrent_tasks": settings.agent_max_concurrent_tasks,
            "task_timeout": settings.agent_task_timeout,
            "health_check_interval": settings.agent_health_check_interval
        }
    
    @abstractmethod
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the main function of the component.
        This must be implemented by subclasses.
        """
        pass
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single task with error handling, status updates, and metrics collection.
        """
        if self.status != ComponentStatus.READY:
            raise RuntimeError(f"Component {self.name} is not ready (status: {self.status.value})")
        
        self.status = ComponentStatus.BUSY
        self.last_updated = datetime.utcnow()
        
        # Record start time for metrics
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Component {self.name} starting task: {task.get('task_type', 'unknown')}")
            
            # Execute the actual task
            result = await self.execute(task)
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Update metrics
            self._update_metrics(task, execution_time, success=True)
            
            self.status = ComponentStatus.READY
            logger.info(f"Component {self.name} completed task successfully")
            
            return {
                "component_id": self.component_id,
                "task_id": task.get("task_id"),
                "result": result,
                "status": "success",
                "execution_time_seconds": execution_time,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.status = ComponentStatus.ERROR
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Update metrics for failed task
            self._update_metrics(task, execution_time, success=False, error=str(e))
            
            logger.error(f"Component {self.name} failed to execute task: {str(e)}")
            
            return {
                "component_id": self.component_id,
                "task_id": task.get("task_id"),
                "error": str(e),
                "status": "error",
                "execution_time_seconds": execution_time,
                "timestamp": datetime.utcnow().isoformat()
            }
        finally:
            self.last_updated = datetime.utcnow()
    
    def _update_metrics(self, task: Dict[str, Any], execution_time: float, success: bool, error: str = None):
        """
        Update component metrics based on task execution.
        """
        task_type = task.get("task_type", "unknown")
        
        # Initialize metrics for this task type if not exists
        if task_type not in self.metrics:
            self.metrics[task_type] = {
                "total_executed": 0,
                "total_successful": 0,
                "total_failed": 0,
                "avg_execution_time": 0.0,
                "total_execution_time": 0.0,
                "last_execution_time": 0.0
            }
        
        # Update metrics
        metrics = self.metrics[task_type]
        metrics["total_executed"] += 1
        
        if success:
            metrics["total_successful"] += 1
        else:
            metrics["total_failed"] += 1
        
        # Update execution time metrics
        metrics["last_execution_time"] = execution_time
        metrics["total_execution_time"] += execution_time
        
        # Recalculate average
        successful_count = metrics["total_successful"]
        if successful_count > 0:
            metrics["avg_execution_time"] = metrics["total_execution_time"] / successful_count
    
    async def add_task(self, task: Dict[str, Any]):
        """
        Add a task to the component's queue.
        """
        await self.task_queue.put(task)
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the component.
        """
        return {
            "component_id": self.component_id,
            "name": self.name,
            "version": self.version,
            "status": self.status.value,
            "health": self.health.value,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "queue_size": self.task_queue.qsize(),
            "metrics": self.metrics
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the component.
        """
        # Default health check - can be overridden by subclasses
        health_details = {
            "component_id": self.component_id,
            "name": self.name,
            "status": self.status.value,
            "health": self.health.value,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "status_check": self.status in [ComponentStatus.READY, ComponentStatus.BUSY],
                "dependency_check": self._check_dependencies(),
                "resource_check": True,  # Basic resource check - override in subclasses
                "configuration_check": self._check_configuration()
            }
        }
        
        # Determine overall health based on individual checks
        if not health_details["checks"]["status_check"]:
            self.health = ComponentHealth.UNHEALTHY
        elif not health_details["checks"]["dependency_check"]:
            self.health = ComponentHealth.DEGRADED
        elif not health_details["checks"]["configuration_check"]:
            self.health = ComponentHealth.DEGRADED
        else:
            self.health = ComponentHealth.HEALTHY
        
        health_details["health"] = self.health.value
        return health_details
    
    def _check_dependencies(self) -> bool:
        """
        Check if all required dependencies are available.
        """
        # For now, just check if dependencies list is populated and accessible
        # Subclasses should implement specific dependency checks
        return True
    
    def _check_configuration(self) -> bool:
        """
        Check if component configuration is valid.
        """
        # Basic check - ensure required config items exist
        required_config = ["component_id", "name", "version"]
        return all(key in self.config for key in required_config)
    
    def update_config(self, config: Dict[str, Any]):
        """
        Update the component's configuration.
        """
        self.config.update(config)
        logger.info(f"Component {self.name} configuration updated")
    
    def add_dependency(self, dependency_id: str):
        """
        Add a dependency to this component.
        """
        if dependency_id not in self.dependencies:
            self.dependencies.append(dependency_id)
            logger.info(f"Added dependency {dependency_id} to component {self.name}")
    
    def remove_dependency(self, dependency_id: str):
        """
        Remove a dependency from this component.
        """
        if dependency_id in self.dependencies:
            self.dependencies.remove(dependency_id)
            logger.info(f"Removed dependency {dependency_id} from component {self.name}")
    
    async def start(self):
        """
        Start the component and any background processes.
        """
        if self.is_running:
            logger.warning(f"Component {self.name} is already running")
            return
        
        self.is_running = True
        self.status = ComponentStatus.READY
        logger.info(f"Component {self.name} started")
    
    async def stop(self):
        """
        Stop the component and clean up resources.
        """
        if not self.is_running:
            logger.warning(f"Component {self.name} is not running")
            return
        
        # Wait for any pending tasks to complete
        while not self.task_queue.empty():
            await asyncio.sleep(0.1)
        
        self.is_running = False
        self.status = ComponentStatus.SHUTDOWN
        logger.info(f"Component {self.name} stopped")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert component to dictionary representation for serialization.
        """
        return {
            "component_id": self.component_id,
            "name": self.name,
            "version": self.version,
            "status": self.status.value,
            "health": self.health.value,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "dependencies": self.dependencies,
            "metrics_summary": self._get_metrics_summary()
        }
    
    def _get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get a summary of component metrics.
        """
        total_tasks = sum(
            metrics["total_executed"] 
            for metrics in self.metrics.values()
        )
        
        total_success = sum(
            metrics["total_successful"] 
            for metrics in self.metrics.values()
        )
        
        success_rate = (total_success / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            "total_tasks_processed": total_tasks,
            "total_successful": total_success,
            "success_rate_percent": round(success_rate, 2),
            "task_types": list(self.metrics.keys()),
            "active": self.is_running
        }


class ComponentRegistry:
    """
    Registry for managing all system components.
    Provides centralized access and management of components.
    """
    
    def __init__(self):
        self.components = {}
        self.component_types = {}
    
    def register_component(self, component: BaseComponent):
        """
        Register a component with the registry.
        """
        self.components[component.component_id] = component
        component_type = type(component).__name__
        
        if component_type not in self.component_types:
            self.component_types[component_type] = []
        
        self.component_types[component_type].append(component.component_id)
        logger.info(f"Registered component: {component.name} ({component.component_id})")
    
    def unregister_component(self, component_id: str):
        """
        Unregister a component from the registry.
        """
        if component_id in self.components:
            component = self.components[component_id]
            component_type = type(component).__name__
            
            # Remove from type list
            if component_type in self.component_types:
                if component_id in self.component_types[component_type]:
                    self.component_types[component_type].remove(component_id)
            
            # Remove from main registry
            del self.components[component_id]
            logger.info(f"Unregistered component: {component_id}")
    
    def get_component(self, component_id: str) -> Optional[BaseComponent]:
        """
        Get a component by ID.
        """
        return self.components.get(component_id)
    
    def get_components_by_type(self, component_type: str) -> List[BaseComponent]:
        """
        Get all components of a specific type.
        """
        component_ids = self.component_types.get(component_type, [])
        return [self.components[cid] for cid in component_ids if cid in self.components]
    
    def get_all_components(self) -> List[BaseComponent]:
        """
        Get all registered components.
        """
        return list(self.components.values())
    
    async def get_all_statuses(self) -> Dict[str, Any]:
        """
        Get statuses of all registered components.
        """
        statuses = {}
        for component_id, component in self.components.items():
            statuses[component_id] = await component.get_status()
        return statuses
    
    async def perform_health_check(self) -> Dict[str, Any]:
        """
        Perform health checks on all registered components.
        """
        health_results = {}
        overall_health = ComponentHealth.HEALTHY
        
        for component_id, component in self.components.items():
            health_result = await component.health_check()
            health_results[component_id] = health_result
            
            # Update overall health based on component health
            component_health = ComponentHealth(health_result["health"])
            if component_health == ComponentHealth.UNHEALTHY:
                overall_health = ComponentHealth.UNHEALTHY
            elif component_health == ComponentHealth.DEGRADED and overall_health == ComponentHealth.HEALTHY:
                overall_health = ComponentHealth.DEGRADED
    
        return {
            "overall_health": overall_health.value,
            "component_health": health_results,
            "total_components": len(self.components),
            "timestamp": datetime.utcnow().isoformat()
        }