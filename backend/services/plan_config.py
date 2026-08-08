from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PlanConfig:
    key: str
    name: str
    description: str
    price_monthly_cents: int
    price_annual_cents: int
    
    max_projects: int
    max_media_uploads: int
    max_processing_minutes: int
    max_ai_generations: int
    max_storage_bytes: int
    
    priority_processing: bool = False
    creator_intelligence_advanced: bool = False
    api_access: bool = False
    team_workspaces: bool = False
    enterprise_support: bool = False
    
    features: dict = field(default_factory=dict)
    is_active: bool = True
    display_order: int = 0


PLAN_CONFIGS: dict[str, PlanConfig] = {
    "free": PlanConfig(
        key="free",
        name="Free Plan",
        description="Experience Scriptloom before upgrading",
        price_monthly_cents=0,
        price_annual_cents=0,
        max_projects=3,
        max_media_uploads=10,
        max_processing_minutes=60,
        max_ai_generations=20,
        max_storage_bytes=2 * 1024 * 1024 * 1024,
        priority_processing=False,
        creator_intelligence_advanced=False,
        api_access=False,
        team_workspaces=False,
        enterprise_support=False,
        features={
            "project_management": True,
            "media_upload": True,
            "clip_generation": True,
            "transcription": True,
            "ai_content_generation": True,
            "export": True,
            "creator_intelligence_basic": True,
        },
        is_active=True,
        display_order=1,
    ),
    "pro": PlanConfig(
        key="pro",
        name="Pro Plan",
        description="For individual creators, freelancers, and small businesses",
        price_monthly_cents=1900,
        price_annual_cents=18240,
        max_projects=-1,
        max_media_uploads=200,
        max_processing_minutes=1000,
        max_ai_generations=500,
        max_storage_bytes=100 * 1024 * 1024 * 1024,
        priority_processing=True,
        creator_intelligence_advanced=True,
        api_access=False,
        team_workspaces=False,
        enterprise_support=False,
        features={
            "project_management": True,
            "media_upload": True,
            "clip_generation": True,
            "transcription": True,
            "ai_content_generation": True,
            "export": True,
            "creator_intelligence_basic": True,
            "advanced_exports": True,
            "bulk_operations": True,
        },
        is_active=True,
        display_order=2,
    ),
    "enterprise": PlanConfig(
        key="enterprise",
        name="Enterprise Plan",
        description="For agencies and organizations with custom requirements",
        price_monthly_cents=0,
        price_annual_cents=0,
        max_projects=-1,
        max_media_uploads=-1,
        max_processing_minutes=-1,
        max_ai_generations=-1,
        max_storage_bytes=-1,
        priority_processing=True,
        creator_intelligence_advanced=True,
        api_access=True,
        team_workspaces=True,
        enterprise_support=True,
        features={
            "project_management": True,
            "media_upload": True,
            "clip_generation": True,
            "transcription": True,
            "ai_content_generation": True,
            "export": True,
            "creator_intelligence_basic": True,
            "advanced_exports": True,
            "bulk_operations": True,
            "team_workspaces": True,
            "role_based_access": True,
            "custom_integrations": True,
            "advanced_analytics": True,
        },
        is_active=True,
        display_order=3,
    ),
}


def get_plan_config(plan_key: str) -> Optional[PlanConfig]:
    return PLAN_CONFIGS.get(plan_key)


def get_all_plans() -> list[PlanConfig]:
    return sorted(PLAN_CONFIGS.values(), key=lambda p: p.display_order)
