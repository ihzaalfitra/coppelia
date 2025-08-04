"""
Coppelia MVP: Multi-Entity Consensus AI System

A meta-agentic AI system that prevents hallucination cascades through
multi-entity consensus, inspired by the Thousand Brains theory.
"""

__version__ = "0.1.0"
__author__ = "Coppelia Team"

from .config import CoppeliaConfig
from .models.assessment import Assessment, ConsensusResult
from .models.entity import EntityMetadata
from .models.consensus import DiscussionRound, ConsensusProcess
from .entities.base_entity import BaseEntity, EntityProtocol
from .exceptions import (
    CoppeliaException,
    EntityEvaluationError,
    ConsensusError,
    SafetyVetoError,
    InvalidProposalError,
    ConfigurationError
)

__all__ = [
    "CoppeliaConfig",
    "Assessment",
    "ConsensusResult",
    "EntityMetadata",
    "DiscussionRound",
    "ConsensusProcess",
    "BaseEntity",
    "EntityProtocol",
    "CoppeliaException",
    "EntityEvaluationError",
    "ConsensusError",
    "SafetyVetoError",
    "InvalidProposalError",
    "ConfigurationError"
]
