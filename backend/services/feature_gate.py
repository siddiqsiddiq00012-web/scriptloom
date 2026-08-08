from enum import Enum
from typing import Optional
from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.models.user import User
from backend.models.billing import UserSubscription, UsageRecord, Plan
from backend.services.plan_config import get_plan_config, PlanConfig


class Feature(str, Enum):
    PROJECTS = "projects"
    MEDIA_UPLOADS = "media_uploads"
    PROCESSING = "processing"
    AI_GENERATIONS = "ai_generations"
    STORAGE = "storage"
    PRIORITY_PROCESSING = "priority_processing"
    CREATOR_INTELLIGENCE_ADVANCED = "creator_intelligence_advanced"
    API_ACCESS = "api_access"
    TEAM_WORKSPACES = "team_workspaces"
    ENTERPRISE_SUPPORT = "enterprise_support"


@dataclass
class UsageCheck:
    allowed: bool
    current: int
    limit: int
    feature: str
    message: Optional[str] = None


class FeatureGate:
    def __init__(self, db: Session):
        self.db = db

    def get_user_plan(self, user: User) -> PlanConfig:
        subscription = (
            self.db.query(UserSubscription)
            .filter(UserSubscription.user_id == user.id)
            .first()
        )
        
        if subscription and subscription.plan:
            plan_key = subscription.plan.key
        else:
            plan_key = "free"
        
        return get_plan_config(plan_key) or get_plan_config("free")

    def get_usage(self, user: User) -> UsageRecord:
        from datetime import datetime, timezone
        period_month = datetime.now(timezone.utc).strftime("%Y-%m")
        
        usage = (
            self.db.query(UsageRecord)
            .filter(
                UsageRecord.user_id == user.id,
                UsageRecord.period_month == period_month,
            )
            .first()
        )
        
        if not usage:
            usage = UsageRecord(
                user_id=user.id,
                media_uploads=0,
                processing_seconds=0,
                ai_generations=0,
                storage_bytes=0,
                period_month=period_month,
            )
            self.db.add(usage)
            self.db.commit()
            self.db.refresh(usage)
        
        return usage

    def check_feature(self, user: User, feature: Feature) -> bool:
        plan = self.get_user_plan(user)
        
        feature_mapping = {
            Feature.PRIORITY_PROCESSING: plan.priority_processing,
            Feature.CREATOR_INTELLIGENCE_ADVANCED: plan.creator_intelligence_advanced,
            Feature.API_ACCESS: plan.api_access,
            Feature.TEAM_WORKSPACES: plan.team_workspaces,
            Feature.ENTERPRISE_SUPPORT: plan.enterprise_support,
        }
        
        return feature_mapping.get(feature, False)

    def check_usage_limit(self, user: User, feature: Feature, additional: int = 1) -> UsageCheck:
        plan = self.get_user_plan(user)
        usage = self.get_usage(user)
        
        if feature == Feature.PROJECTS:
            current = self._get_project_count(user)
            limit = plan.max_projects
            return self._evaluate_limit(current, limit, additional, "projects")
        
        elif feature == Feature.MEDIA_UPLOADS:
            current = usage.media_uploads
            limit = plan.max_media_uploads
            return self._evaluate_limit(current, limit, additional, "media uploads")
        
        elif feature == Feature.PROCESSING:
            current_minutes = usage.processing_seconds // 60
            limit = plan.max_processing_minutes
            return self._evaluate_limit(current_minutes, limit, additional, "processing minutes")
        
        elif feature == Feature.AI_GENERATIONS:
            current = usage.ai_generations
            limit = plan.max_ai_generations
            return self._evaluate_limit(current, limit, additional, "AI generations")
        
        elif feature == Feature.STORAGE:
            current = usage.storage_bytes
            limit = plan.max_storage_bytes
            return self._evaluate_limit_bytes(current, limit, additional, "storage")
        
        return UsageCheck(allowed=True, current=0, limit=-1, feature=feature.value)

    def _get_project_count(self, user: User) -> int:
        from backend.models.project import Project
        return self.db.query(Project).filter(Project.owner_id == user.id).count()

    def _evaluate_limit(self, current: int, limit: int, additional: int, feature_name: str) -> UsageCheck:
        if limit == -1:
            return UsageCheck(allowed=True, current=current, limit=limit, feature=feature_name)
        
        allowed = (current + additional) <= limit
        message = None
        
        if not allowed:
            message = f"Monthly {feature_name} limit exceeded. Used {current} of {limit}. Please upgrade your plan."
        
        return UsageCheck(
            allowed=allowed,
            current=current,
            limit=limit,
            feature=feature_name,
            message=message,
        )

    def _evaluate_limit_bytes(self, current: int, limit: int, additional: int, feature_name: str) -> UsageCheck:
        if limit == -1:
            return UsageCheck(allowed=True, current=current, limit=limit, feature=feature_name)
        
        allowed = (current + additional) <= limit
        message = None
        
        if not allowed:
            current_gb = current / (1024 ** 3)
            limit_gb = limit / (1024 ** 3)
            message = f"Storage limit exceeded. Used {current_gb:.1f}GB of {limit_gb:.1f}GB. Please upgrade your plan."
        
        return UsageCheck(
            allowed=allowed,
            current=current,
            limit=limit,
            feature=feature_name,
            message=message,
        )

    def require_feature(self, user: User, feature: Feature) -> None:
        if not self.check_feature(user, feature):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires a higher plan. Please upgrade to access {feature.value}.",
            )

    def require_usage_limit(self, user: User, feature: Feature, additional: int = 1) -> UsageCheck:
        check = self.check_usage_limit(user, feature, additional)
        
        if not check.allowed:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=check.message,
            )
        
        return check

    def record_usage(
        self,
        user: User,
        media_uploads: int = 0,
        processing_seconds: int = 0,
        ai_generations: int = 0,
        storage_bytes: int = 0,
    ) -> UsageRecord:
        usage = self.get_usage(user)
        
        usage.media_uploads += media_uploads
        usage.processing_seconds += processing_seconds
        usage.ai_generations += ai_generations
        usage.storage_bytes += storage_bytes
        
        self.db.commit()
        self.db.refresh(usage)
        
        return usage
