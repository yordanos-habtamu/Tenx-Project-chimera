"""
Content Component for Project Chimera
Handles content creation, management, and workflow orchestration
"""
from typing import Dict, Any, List
import asyncio
import logging
from datetime import datetime

from .base_component import BaseComponent, ComponentStatus
from ..services.content_service import ContentService

logger = logging.getLogger(__name__)


class ContentComponent(BaseComponent):
    """
    Component for handling content-related operations in Project Chimera.
    Manages the content creation workflow from research to publication.
    """
    
    def __init__(self, component_id: str = "content_001", name: str = "ContentComponent", version: str = "1.0.0"):
        super().__init__(component_id, name, version)
        
        # Initialize the content service
        self.content_service = ContentService()
        
        # Add component-specific configuration
        self.config.update({
            "supported_content_types": ["educational", "review", "tutorial", "news", "opinion"],
            "max_script_length": 5000,
            "min_script_length": 100,
            "default_content_type": "educational",
            "workflow_timeout": 300  # 5 minutes
        })
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute content task based on task type.
        """
        task_type = task_data.get("task_type", "unknown")
        logger.info(f"ContentComponent executing task: {task_type}")
        
        if task_type == "create_content_from_research":
            return await self.create_content_from_research(task_data)
        elif task_type == "get_workflow_history":
            return await self.get_workflow_history(task_data)
        elif task_type == "get_content_stats":
            return await self.get_content_stats(task_data)
        elif task_type == "validate_content":
            return await self.validate_content(task_data)
        else:
            raise ValueError(f"Unknown content task type: {task_type}")
    
    async def create_content_from_research(
        self, 
        task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create content based on research data following the complete workflow.
        """
        research_data = task_data.get("research_data", {})
        content_type = task_data.get("content_type", self.config["default_content_type"])
        
        # Validate content type
        if content_type not in self.config["supported_content_types"]:
            raise ValueError(f"Unsupported content type: {content_type}. Supported types: {self.config['supported_content_types']}")
        
        logger.info(f"Starting content creation workflow for type: {content_type}")
        
        # Perform content creation using the service
        result = await self.content_service.create_content_from_research(
            research_data, content_type
        )
        
        return result
    
    async def get_workflow_history(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the history of content creation workflows.
        """
        logger.info("Retrieving content workflow history")
        
        history = self.content_service.get_workflow_history()
        
        return {
            "history": history,
            "count": len(history)
        }
    
    async def get_content_stats(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get statistics about created content.
        """
        logger.info("Retrieving content statistics")
        
        stats = self.content_service.get_content_statistics()
        
        return stats
    
    async def validate_content(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate content based on specified criteria.
        """
        content_data = task_data.get("content_data", {})
        validation_type = task_data.get("validation_type", "all")
        
        logger.info(f"Validating content, type: {validation_type}")
        
        validations = {}
        
        if validation_type in ["all", "length"]:
            validations["length"] = self._validate_content_length(content_data)
        
        if validation_type in ["all", "format"]:
            validations["format"] = self._validate_content_format(content_data)
        
        if validation_type in ["all", "completeness"]:
            validations["completeness"] = self._validate_content_completeness(content_data)
        
        is_valid = all(validations.get(k, {}).get("valid", True) for k in validations)
        
        return {
            "validations": validations,
            "overall_valid": is_valid,
            "validation_type": validation_type
        }
    
    def _validate_content_length(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate content length against configured limits.
        """
        script = content_data.get("script", "")
        script_length = len(script) if script else 0
        
        is_valid = (
            script_length >= self.config["min_script_length"] and 
            script_length <= self.config["max_script_length"]
        )
        
        return {
            "valid": is_valid,
            "length": script_length,
            "min_required": self.config["min_script_length"],
            "max_allowed": self.config["max_script_length"],
            "issues": [] if is_valid else [
                f"Script length {script_length} is out of range [{self.config['min_script_length']}-{self.config['max_script_length']}]"
            ]
        }
    
    def _validate_content_format(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate content format and structure.
        """
        required_fields = ["title", "script"]
        missing_fields = [field for field in required_fields if field not in content_data]
        
        is_valid = len(missing_fields) == 0
        
        return {
            "valid": is_valid,
            "missing_fields": missing_fields,
            "required_fields": required_fields
        }
    
    def _validate_content_completeness(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate content completeness and required attributes.
        """
        issues = []
        
        # Check for empty or placeholder content
        title = content_data.get("title", "").strip()
        script = content_data.get("script", "").strip()
        
        if not title:
            issues.append("Content title is empty")
        elif len(title) < 5:
            issues.append("Content title is too short")
        
        if not script:
            issues.append("Content script is empty")
        elif len(script) < self.config["min_script_length"]:
            issues.append(f"Content script is too short (minimum {self.config['min_script_length']} characters)")
        
        is_valid = len(issues) == 0
        
        return {
            "valid": is_valid,
            "issues": issues
        }
    
    def _check_dependencies(self) -> bool:
        """
        Check if content service dependencies are available.
        """
        # In a real implementation, this would check if required services are reachable
        # For now, just check if the service is initialized
        return self.content_service is not None
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check specific to the content component.
        """
        health_details = await super().health_check()
        
        # Add content-specific checks
        try:
            # Test basic functionality with a simple validation
            test_content = {"title": "Test", "script": "This is a test script."}
            validation_result = self.validate_content({
                "content_data": test_content,
                "validation_type": "all"
            })
            
            health_details["checks"]["functionality_check"] = True
            health_details["checks"]["validation_result"] = validation_result
        except Exception as e:
            health_details["checks"]["functionality_check"] = False
            health_details["checks"]["functionality_error"] = str(e)
        
        # Update health based on functionality check
        if not health_details["checks"]["functionality_check"]:
            self.health = "unhealthy"
            health_details["health"] = "unhealthy"
        
        return health_details


class ContentModerationComponent(BaseComponent):
    """
    Component for content moderation and safety checks.
    """
    
    def __init__(self, component_id: str = "moderation_001", name: str = "ContentModerationComponent", version: str = "1.0.0"):
        super().__init__(component_id, name, version)
        
        self.moderation_rules = {
            "banned_phrases": [
                "clickbait", "you won't believe", "incredible", "shocking", "miracle"
            ],
            "content_filters": [
                "violence", "hatred", "discrimination", "explicit", "dangerous"
            ],
            "title_filters": [
                "best", "worst", "top", "ultimate"  # Potential clickbait indicators
            ]
        }
        self.auto_approve_threshold = 0.8  # Confidence score for auto-approval
        self.requires_human_review = True  # Whether human review is required
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute moderation task based on task type.
        """
        task_type = task_data.get("task_type", "unknown")
        logger.info(f"ContentModerationComponent executing task: {task_type}")
        
        if task_type == "moderate_content":
            return await self.moderate_content(task_data)
        elif task_type == "update_moderation_rules":
            return await self.update_moderation_rules(task_data)
        elif task_type == "get_moderation_stats":
            return await self.get_moderation_stats(task_data)
        elif task_type == "approve_content":
            return await self.approve_content(task_data)
        else:
            raise ValueError(f"Unknown moderation task type: {task_type}")
    
    async def moderate_content(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Moderate content based on configured rules and filters.
        """
        content_data = task_data.get("content_data", {})
        
        logger.info(f"Moderating content: {content_data.get('title', 'Unknown')}")
        
        # Perform various checks
        checks = {
            "title_quality": self._check_title_quality(content_data),
            "script_quality": self._check_script_quality(content_data),
            "content_safety": self._check_content_safety(content_data),
            "compliance": self._check_compliance(content_data)
        }
        
        # Calculate overall moderation score
        scores = [check["score"] for check in checks.values() if "score" in check]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Determine if content passes moderation
        passes_moderation = avg_score >= self.auto_approve_threshold
        requires_review = self.requires_human_review or avg_score < self.auto_approve_threshold
        
        # Collect all issues
        issues = []
        for check_name, check_result in checks.items():
            if not check_result.get("passed", True):
                issues.extend(check_result.get("issues", []))
        
        result = {
            "content_id": content_data.get("video_id", "unknown"),
            "title": content_data.get("title", "Unknown"),
            "moderation_score": round(avg_score, 2),
            "passes_moderation": passes_moderation,
            "requires_human_review": requires_review,
            "checks": checks,
            "issues": issues,
            "moderation_completed": True,
            "recommendation": "approve" if passes_moderation and not requires_review else "review"
        }
        
        return result
    
    def _check_title_quality(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check the quality of the content title.
        """
        title = content_data.get("title", "")
        issues = []
        
        # Check length
        if len(title) < 5:
            issues.append(f"Title too short: {len(title)} chars (min: 5)")
        elif len(title) > 100:
            issues.append(f"Title too long: {len(title)} chars (max: 100)")
        
        # Check for banned phrases
        title_lower = title.lower()
        for phrase in self.moderation_rules["banned_phrases"]:
            if phrase.lower() in title_lower:
                issues.append(f"Banned phrase detected in title: '{phrase}'")
        
        # Check for potential clickbait indicators
        for indicator in self.moderation_rules["title_filters"]:
            if indicator.lower() in title_lower:
                issues.append(f"Potential clickbait indicator in title: '{indicator}'")
        
        # Calculate score (higher is better)
        max_issues = 5  # Maximum possible issues
        score = max(0, (max_issues - len(issues)) / max_issues)
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "score": round(score, 2)
        }
    
    def _check_script_quality(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check the quality of the content script.
        """
        script = content_data.get("script", "")
        issues = []
        
        # Check length
        if len(script) < 100:
            issues.append(f"Script too short: {len(script)} chars (min: 100)")
        elif len(script) > 5000:
            issues.append(f"Script too long: {len(script)} chars (max: 5000)")
        
        # Additional checks can be added here
        
        # Calculate score (higher is better)
        max_issues = 3  # Maximum possible issues
        score = max(0, (max_issues - len(issues)) / max_issues)
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "score": round(score, 2)
        }
    
    def _check_content_safety(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check content for safety concerns.
        """
        title = content_data.get("title", "")
        script = content_data.get("script", "")
        issues = []
        
        # Combine content for analysis
        combined_content = f"{title} {script}".lower()
        
        # Check for potentially unsafe content
        for filter_word in self.moderation_rules["content_filters"]:
            if filter_word in combined_content:
                issues.append(f"Potentially unsafe content pattern detected: {filter_word}")
        
        # Calculate score (higher is better)
        max_issues = 3  # Maximum possible issues
        score = max(0, (max_issues - len(issues)) / max_issues)
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "score": round(score, 2)
        }
    
    def _check_compliance(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check content compliance with regulations and policies.
        """
        issues = []
        
        # Check for required fields
        required_fields = ["trend_keyword", "created_by"]
        for field in required_fields:
            if field not in content_data:
                issues.append(f"Missing required field: {field}")
        
        # Calculate score (higher is better)
        max_issues = 3  # Maximum possible issues
        score = max(0, (max_issues - len(issues)) / max_issues)
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "score": round(score, 2)
        }
    
    async def update_moderation_rules(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update moderation rules dynamically.
        """
        new_rules = task_data.get("rules", {})
        
        # Update specific rule sets
        if "banned_phrases" in new_rules:
            self.moderation_rules["banned_phrases"] = new_rules["banned_phrases"]
        
        if "content_filters" in new_rules:
            self.moderation_rules["content_filters"] = new_rules["content_filters"]
        
        if "title_filters" in new_rules:
            self.moderation_rules["title_filters"] = new_rules["title_filters"]
        
        # Update thresholds if provided
        if "auto_approve_threshold" in task_data:
            self.auto_approve_threshold = task_data["auto_approve_threshold"]
        
        if "requires_human_review" in task_data:
            self.requires_human_review = task_data["requires_human_review"]
        
        return {
            "rules_updated": True,
            "updated_rules": self.moderation_rules,
            "new_threshold": self.auto_approve_threshold,
            "human_review_required": self.requires_human_review
        }
    
    async def get_moderation_stats(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get statistics about moderation activities.
        """
        # This would track actual stats in a real implementation
        return {
            "total_moderated": 0,  # Placeholder
            "auto_approved": 0,    # Placeholder
            "sent_for_review": 0,  # Placeholder
            "rejected": 0,         # Placeholder
            "rules_applied": len(self.moderation_rules),
            "banned_phrases_count": len(self.moderation_rules["banned_phrases"]),
            "content_filters_count": len(self.moderation_rules["content_filters"])
        }
    
    async def approve_content(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Approve content that has been moderated.
        """
        content_id = task_data.get("content_id")
        approver = task_data.get("approver", "system")
        
        # In a real implementation, this would update the content status in a database
        # For now, just return an approval confirmation
        
        return {
            "content_approved": True,
            "content_id": content_id,
            "approved_by": approver,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _check_dependencies(self) -> bool:
        """
        Check if moderation dependencies are available.
        """
        # Check if moderation rules are properly configured
        return all(key in self.moderation_rules for key in ["banned_phrases", "content_filters", "title_filters"])
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check specific to the moderation component.
        """
        health_details = await super().health_check()
        
        # Add moderation-specific checks
        health_details["checks"]["rules_loaded"] = len(self.moderation_rules) > 0
        health_details["checks"]["auto_approve_threshold_valid"] = 0 <= self.auto_approve_threshold <= 1
        
        return health_details