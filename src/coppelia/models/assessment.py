from typing import List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime

class Assessment(BaseModel):
    """Immutable assessment object for entity evaluations"""
    entity_id: str = Field(..., description="Unique entity identifier")
    score: float = Field(..., ge=0.0, le=1.0, description="Assessment score 0-1")
    reasoning: str = Field(..., min_length=10, description="Detailed reasoning")
    concerns: List[str] = Field(default_factory=list, description="Specific issues")
    suggestions: List[str] = Field(default_factory=list, description="Improvements")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @validator('concerns', 'suggestions')
    def validate_lists(cls, v):
        """Ensure list items are non-empty strings"""
        return [item.strip() for item in v if item.strip()]

class ConsensusResult(BaseModel):
    """Result of consensus evaluation"""
    approved: bool
    final_score: float = Field(ge=0.0, le=1.0)
    reason: str
    assessments: List[Assessment]
    discussion_rounds: int = Field(default=0, ge=0, le=3)
    safety_veto_triggered: bool = Field(default=False)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
