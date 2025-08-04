from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Protocol
from ..models.assessment import Assessment

class EntityProtocol(Protocol):
    """Interface contract for all Coppelia entities"""

    def evaluate(self, proposal: str, context: Optional[Dict] = None) -> Assessment:
        """Primary evaluation method - must preserve entity independence"""
        ...

    def get_entity_info(self) -> Dict[str, str]:
        """Returns entity metadata"""
        ...

    def validate_proposal_format(self, proposal: str) -> bool:
        """Validates proposal structure before evaluation"""
        ...

class BaseEntity(ABC):
    """Abstract base class ensuring entity independence"""

    def __init__(self, entity_id: str, role_description: str):
        self.entity_id = entity_id
        self.role_description = role_description
        self._conversation_history: List[Dict] = []
        self._independent_context: Dict = {}

    @abstractmethod
    def _generate_system_prompt(self) -> str:
        """Generate entity-specific system prompt"""
        pass

    @abstractmethod
    def _evaluate_internal(self, proposal: str, context: Dict) -> Assessment:
        """Internal evaluation logic - entity specific"""
        pass

    def evaluate(self, proposal: str, context: Optional[Dict] = None) -> Assessment:
        """PUBLIC INTERFACE: Evaluate proposal maintaining independence"""
        # Validation prevents malformed proposals
        if not self.validate_proposal_format(proposal):
            raise ValueError(f"Invalid proposal format for {self.entity_id}")

        # Ensure independent evaluation
        eval_context = context.copy() if context else {}
        eval_context["entity_perspective"] = self.role_description

        return self._evaluate_internal(proposal, eval_context)

    def get_entity_info(self) -> Dict[str, str]:
        """Returns entity metadata"""
        return {
            "entity_id": self.entity_id,
            "role_description": self.role_description,
            "type": self.__class__.__name__
        }

    def validate_proposal_format(self, proposal: str) -> bool:
        """Validates proposal structure before evaluation"""
        if not proposal or not isinstance(proposal, str):
            return False
        if len(proposal.strip()) < 10:
            return False
        return True
