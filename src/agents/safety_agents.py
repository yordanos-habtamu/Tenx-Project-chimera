from ..core.base_agent import BaseAgent
from typing import Dict, Any
import asyncio
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class HumanInLoopAgent(BaseAgent):
    """
    Agent responsible for handling Human-in-the-Loop (HITL) processes.
    Manages content approval workflows and human oversight.
    """
    
    def __init__(self, agent_id: str = "hitl_001", name: str = "HumanInLoopAgent"):
        super().__init__(agent_id, name)
        self.approval_thresholds = {
            "first_post_to_platform": True,
            "engagement_spike": 10000,  # Threshold for engagement that triggers review
            "content_flagged": True,
            "schedule_deviation": True
        }
        self.pending_approvals = {}
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute HITL validation task.
        """
        task_type = task_data.get("task_type", "unknown")
        logger.info(f"HITL agent executing task: {task_type}")
        
        if task_type == "validate_content":
            return await self.validate_content(task_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def validate_content(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate content and determine if human approval is needed.
        """
        content_data = task_data.get("content_data", {})
        
        logger.info("Validating content for human approval requirements")
        
        # Determine if content needs human approval
        needs_approval = self._check_approval_requirements(content_data)
        
        if needs_approval:
            # Add to pending approvals queue
            approval_request = {
                "content_id": content_data.get("video_id", "unknown"),
                "title": content_data.get("title", "Untitled"),
                "content_type": content_data.get("content_type", "unknown"),
                "request_timestamp": datetime.utcnow().isoformat(),
                "reasons": self._get_approval_reasons(content_data)
            }
            
            approval_id = f"approval_{len(self.pending_approvals) + 1}"
            self.pending_approvals[approval_id] = approval_request
            
            return {
                "approved": False,
                "needs_human_review": True,
                "approval_id": approval_id,
                "reasons": approval_request["reasons"],
                "content_held": True
            }
        else:
            # Content passes automated checks
            return {
                "approved": True,
                "needs_human_review": False,
                "reasons": ["Content passed automated safety checks"],
                "content_approved": True
            }
    
    def _check_approval_requirements(self, content_data: Dict[str, Any]) -> bool:
        """
        Check if content meets approval requirements.
        """
        # Check for first post to a new platform
        platform = content_data.get("platform", "")
        if platform and self._is_first_post_to_platform(platform):
            return True
        
        # Check for content flagged by classifiers (simulated)
        content_flags = content_data.get("flags", [])
        if content_flags:
            return True
        
        # Check for engagement spikes (simulated)
        estimated_engagement = content_data.get("estimated_engagement", 0)
        if estimated_engagement > self.approval_thresholds["engagement_spike"]:
            return True
        
        # Check for schedule deviations (simulated)
        scheduled_time = content_data.get("scheduled_time")
        if scheduled_time and self._is_schedule_deviation(scheduled_time):
            return True
        
        # Perform content safety checks
        content_safe = self._perform_content_safety_check(content_data)
        if not content_safe:
            return True
        
        return False
    
    def _is_first_post_to_platform(self, platform: str) -> bool:
        """
        Check if this is the first post to a given platform.
        In a real implementation, this would check against published content history.
        """
        # Simulate first post detection
        return False  # For now, assuming we've posted to all platforms before
    
    def _is_schedule_deviation(self, scheduled_time: str) -> bool:
        """
        Check if scheduled time deviates from standard posting schedule.
        """
        # Simulate schedule deviation check
        return False  # For now, assuming all schedules are acceptable
    
    def _perform_content_safety_check(self, content_data: Dict[str, Any]) -> bool:
        """
        Perform basic content safety checks.
        """
        title = content_data.get("title", "")
        script = content_data.get("script", "")
        
        # Check for potentially unsafe content
        unsafe_patterns = [
            r"\b(hate|violence|explicit|adult)\b",
            r"\b(politics|controversial)\b",  # Depending on strategy
        ]
        
        combined_content = f"{title} {script}".lower()
        
        for pattern in unsafe_patterns:
            if re.search(pattern, combined_content):
                logger.warning(f"Content flagged for potentially unsafe content: {pattern}")
                return False
        
        return True
    
    def _get_approval_reasons(self, content_data: Dict[str, Any]) -> list:
        """
        Get reasons why content needs approval.
        """
        reasons = []
        
        # Check various conditions that trigger approval
        if self._is_first_post_to_platform(content_data.get("platform", "")):
            reasons.append("First post to platform")
        
        content_flags = content_data.get("flags", [])
        if content_flags:
            reasons.extend([f"Content flagged: {flag}" for flag in content_flags])
        
        estimated_engagement = content_data.get("estimated_engagement", 0)
        if estimated_engagement > self.approval_thresholds["engagement_spike"]:
            reasons.append(f"Estimated engagement exceeds threshold ({estimated_engagement} > {self.approval_thresholds['engagement_spike']})")
        
        scheduled_time = content_data.get("scheduled_time")
        if scheduled_time and self._is_schedule_deviation(scheduled_time):
            reasons.append("Schedule deviation detected")
        
        if not self._perform_content_safety_check(content_data):
            reasons.append("Content safety check failed")
        
        return reasons if reasons else ["Standard review process"]
    
    async def approve_content(self, approval_id: str, approved: bool, notes: str = "") -> Dict[str, Any]:
        """
        Approve or reject content based on human decision.
        """
        if approval_id not in self.pending_approvals:
            return {"error": f"Approval ID {approval_id} not found"}
        
        approval_request = self.pending_approvals[approval_id]
        
        result = {
            "approval_id": approval_id,
            "content_id": approval_request["content_id"],
            "approved": approved,
            "notes": notes,
            "processed_at": datetime.utcnow().isoformat()
        }
        
        # Remove from pending approvals
        del self.pending_approvals[approval_id]
        
        if approved:
            logger.info(f"Content {approval_request['content_id']} approved by human reviewer")
        else:
            logger.info(f"Content {approval_request['content_id']} rejected by human reviewer")
        
        return result


class ContentModerationAgent(BaseAgent):
    """
    Agent responsible for automated content moderation and quality checks.
    """
    
    def __init__(self, agent_id: str = "moderation_001", name: str = "ContentModerationAgent"):
        super().__init__(agent_id, name)
        self.quality_thresholds = {
            "min_script_length": 100,  # Minimum characters in script
            "max_script_length": 5000,  # Maximum characters in script
            "min_title_length": 5,     # Minimum characters in title
            "max_title_length": 100,   # Maximum characters in title
        }
        self.banned_phrases = [
            "clickbait", "you won't believe", "incredible", "shocking"
        ]
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute content moderation task.
        """
        task_type = task_data.get("task_type", "unknown")
        logger.info(f"ContentModeration agent executing task: {task_type}")
        
        if task_type == "validate_content":
            return await self.moderate_content(task_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def moderate_content(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Moderate content based on quality and safety standards.
        """
        content_data = task_data.get("content_data", {})
        
        logger.info("Moderating content for quality and safety")
        
        # Perform various checks
        checks = {
            "title_quality": self._check_title_quality(content_data),
            "script_quality": self._check_script_quality(content_data),
            "content_safety": self._check_content_safety(content_data),
            "provenance_valid": self._check_provenance(content_data)
        }
        
        # Determine overall approval status
        all_checks_passed = all(check["passed"] for check in checks.values())
        
        # Collect all issues
        issues = []
        for check_name, check_result in checks.items():
            if not check_result["passed"]:
                issues.extend(check_result["issues"])
        
        return {
            "approved": all_checks_passed,
            "checks": checks,
            "issues": issues,
            "moderation_completed": True,
            "content_passed_moderation": all_checks_passed
        }
    
    def _check_title_quality(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check the quality of the content title.
        """
        title = content_data.get("title", "")
        issues = []
        
        # Check length
        if len(title) < self.quality_thresholds["min_title_length"]:
            issues.append(f"Title too short: {len(title)} chars (min: {self.quality_thresholds['min_title_length']})")
        elif len(title) > self.quality_thresholds["max_title_length"]:
            issues.append(f"Title too long: {len(title)} chars (max: {self.quality_thresholds['max_title_length']})")
        
        # Check for banned phrases
        title_lower = title.lower()
        for phrase in self.banned_phrases:
            if phrase in title_lower:
                issues.append(f"Banned phrase detected in title: '{phrase}'")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "score": 100 - (len(issues) * 20)  # Deduct 20 points per issue
        }
    
    def _check_script_quality(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check the quality of the content script.
        """
        script = content_data.get("script", "")
        issues = []
        
        # Check length
        if len(script) < self.quality_thresholds["min_script_length"]:
            issues.append(f"Script too short: {len(script)} chars (min: {self.quality_thresholds['min_script_length']})")
        elif len(script) > self.quality_thresholds["max_script_length"]:
            issues.append(f"Script too long: {len(script)} chars (max: {self.quality_thresholds['max_script_length']})")
        
        # Additional checks can be added here
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "score": 100 - (len(issues) * 25)  # Deduct 25 points per issue
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
        unsafe_patterns = [
            r"\b(violence|hatred|discrimination|explicit)\b",
            r"\b(dangerous|unsafe|illegal)\b"
        ]
        
        for pattern in unsafe_patterns:
            if re.search(pattern, combined_content):
                issues.append(f"Potentially unsafe content pattern detected: {pattern}")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "score": 100 - (len(issues) * 30)  # Deduct 30 points per safety issue
        }
    
    def _check_provenance(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check content provenance and attribution.
        """
        # In a real implementation, this would verify sources and attributions
        issues = []
        
        # For now, just check if required fields exist
        required_fields = ["trend_keyword", "research_source"]
        for field in required_fields:
            if field not in content_data:
                issues.append(f"Missing provenance field: {field}")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "score": 100 - (len(issues) * 15)  # Deduct 15 points per missing provenance
        }