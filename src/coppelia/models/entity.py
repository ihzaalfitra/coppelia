from typing import Dict, Any, List
from pydantic import BaseModel, Field

class EntityMetadata(BaseModel):
    """Entity metadata and configuration"""
    entity_id: str = Field(..., description="Unique entity identifier")
    role_description: str = Field(..., description="Entity's role and responsibilities")
    weight: float = Field(..., ge=0.0, le=1.0, description="Consensus weight")
    is_active: bool = Field(default=True, description="Entity participation status")
    capabilities: List[str] = Field(default_factory=list, description="Entity capabilities")
