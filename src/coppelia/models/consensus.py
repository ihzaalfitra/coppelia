from typing import Dict, List
from pydantic import BaseModel, Field
from .assessment import Assessment, ConsensusResult

class DiscussionRound(BaseModel):
    """Single round of entity discussion"""
    round_number: int = Field(..., ge=1, le=3)
    assessments: List[Assessment]
    consensus_score: float = Field(ge=0.0, le=1.0)
    convergence_delta: float = Field(ge=0.0, description="Score change from previous round")

class ConsensusProcess(BaseModel):
    """Complete consensus evaluation process"""
    initial_assessments: List[Assessment]
    discussion_rounds: List[DiscussionRound] = Field(default_factory=list)
    final_result: ConsensusResult
    total_duration_seconds: float = Field(ge=0.0)
