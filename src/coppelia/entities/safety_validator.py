from typing import Dict, List, Set, Optional
import re
import json
from ..models.assessment import Assessment
from .base_entity import BaseEntity
from ..utils.llm_client import LLMClient
from ..config import CoppeliaConfig
from ..exceptions import EntityEvaluationError
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

# System prompt template as specified by architect
SAFETY_VALIDATOR_SYSTEM_PROMPT = """
You are the Safety Validator in the Coppelia multi-entity consensus system.

CRITICAL ROLE: You have VETO POWER. Any safety score below 0.6 will block the proposal regardless of other entity scores.

CORE RESPONSIBILITIES:
1. **Architecture Protection**: Detect any attempts to modify:
   - Consensus mechanisms (scoring, thresholds, entity weights)
   - Safety veto power or thresholds
   - Entity independence constraints
   - Core communication protocols

2. **Security Assessment**: Identify vulnerabilities in:
   - Input validation bypasses
   - Data exposure risks
   - Privilege escalation attempts
   - Injection attack vectors

3. **Ethical Evaluation**: Consider implications for:
   - User privacy and consent
   - Potential misuse scenarios
   - Bias amplification risks
   - Harmful output generation

4. **Constraint Compliance**: Verify adherence to:
   - Entity independence requirements
   - JSON-only communication protocols
   - Immutable safety boundaries
   - Tool creation limitations

SCORING GUIDELINES:
- 0.9-1.0: Completely safe, no architectural or security concerns
- 0.8-0.9: Minor issues, easily addressed without core changes
- 0.7-0.8: Moderate concerns, requires modification but acceptable
- 0.6-0.7: Significant issues, barely acceptable with major changes
- 0.0-0.6: VETO ACTIVATED - Unacceptable safety risks

VETO TRIGGERS (Automatic score < 0.6):
- Proposals to modify consensus thresholds or entity weights
- Attempts to bypass safety validation
- Tools that could compromise entity independence
- Code that accesses restricted system components
- Proposals with high misuse potential

RESPONSE FORMAT (MANDATORY):
You must respond with valid JSON matching this exact structure:
{
    "entity_id": "safety_validator",
    "score": 0.0,
    "reasoning": "Detailed explanation of safety assessment",
    "concerns": ["Specific safety issues identified"],
    "suggestions": ["Concrete improvement recommendations"],
    "confidence": 0.0
}

INDEPENDENCE REQUIREMENT:
Maintain your unique safety-focused perspective. Do not be influenced by other entities' assessments. Your primary obligation is system and user safety.
"""

class SafetyValidator(BaseEntity):
    """Safety Validator with veto power implementation"""

    def __init__(self, config: CoppeliaConfig, llm_client: LLMClient):
        super().__init__(
            entity_id="safety_validator",
            role_description="Security, ethics, and constraint compliance validator with veto power"
        )
        self.config = config
        self.llm_client = llm_client
        self.forbidden_patterns = self._load_forbidden_patterns()

        logger.info(
            "Safety Validator initialized",
            entity_id=self.entity_id,
            veto_threshold=self.config.SAFETY_VETO_THRESHOLD,
            forbidden_patterns_count=len(self.forbidden_patterns)
        )

    def _generate_system_prompt(self) -> str:
        """Generate safety validator system prompt"""
        return SAFETY_VALIDATOR_SYSTEM_PROMPT

    def _load_forbidden_patterns(self) -> Set[str]:
        """Load patterns that automatically trigger veto"""
        return {
            r"modify.*consensus.*threshold",
            r"change.*consensus.*threshold",
            r"modify.*entity.*weight",
            r"change.*entity.*weight",
            r"bypass.*safety",
            r"override.*veto",
            r"alter.*scoring.*formula",
            r"disable.*validation",
            r"remove.*safety.*check",
            r"circumvent.*constraint",
            r"hack.*system",
            r"exploit.*vulnerability",
            r"inject.*code",
            r"access.*private.*data",
            r"escalate.*privilege"
        }

    def _check_forbidden_patterns(self, proposal: str) -> List[str]:
        """Check for patterns that automatically trigger veto"""
        violations = []
        proposal_lower = proposal.lower()

        for pattern in self.forbidden_patterns:
            if re.search(pattern, proposal_lower):
                violations.append(f"Forbidden pattern detected: {pattern}")
                logger.warning(
                    "Forbidden pattern detected",
                    entity_id=self.entity_id,
                    pattern=pattern,
                    proposal_excerpt=proposal[:100]
                )

        return violations

    def _evaluate_internal(self, proposal: str, context: Dict) -> Assessment:
        """Internal safety evaluation logic"""

        logger.info(
            "Starting safety evaluation",
            entity_id=self.entity_id,
            proposal_length=len(proposal)
        )

        # Pre-check for automatic veto patterns
        forbidden_violations = self._check_forbidden_patterns(proposal)
        if forbidden_violations:
            logger.warning(
                "Automatic veto triggered",
                entity_id=self.entity_id,
                violations=forbidden_violations
            )

            return Assessment(
                entity_id=self.entity_id,
                score=0.0,  # Automatic veto
                reasoning="Automatic veto triggered by forbidden patterns that attempt to compromise system safety or architectural integrity",
                concerns=forbidden_violations + ["SAFETY VETO ACTIVATED - AUTOMATIC"],
                suggestions=[
                    "Remove attempts to modify core safety constraints",
                    "Ensure proposal does not compromise system architecture",
                    "Focus on safe tool creation within established boundaries"
                ],
                confidence=1.0
            )

        # Proceed with LLM-based evaluation
        try:
            messages = [
                {"role": "system", "content": self._generate_system_prompt()},
                {"role": "user", "content": f"Evaluate this proposal for safety:\n{proposal}"}
            ]

            response_content = self.llm_client.generate_response(
                messages=messages,
                entity_id=self.entity_id
            )

            # Parse JSON response
            try:
                response_data = json.loads(response_content)
                assessment = Assessment(**response_data)
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(
                    "Failed to parse LLM response",
                    entity_id=self.entity_id,
                    error=str(e),
                    response_content=response_content[:200]
                )
                raise EntityEvaluationError(f"Invalid JSON response from LLM: {e}")

            # Validate assessment integrity
            if assessment.entity_id != self.entity_id:
                raise ValueError(f"Entity ID mismatch: expected {self.entity_id}, got {assessment.entity_id}")

            # Apply veto logic
            if assessment.score < self.config.SAFETY_VETO_THRESHOLD:
                assessment.concerns.append("SAFETY VETO ACTIVATED")
                logger.warning(
                    "Safety veto activated",
                    entity_id=self.entity_id,
                    score=assessment.score,
                    threshold=self.config.SAFETY_VETO_THRESHOLD
                )

            logger.info(
                "Safety evaluation completed",
                entity_id=self.entity_id,
                score=assessment.score,
                veto_activated=assessment.score < self.config.SAFETY_VETO_THRESHOLD
            )

            return assessment

        except Exception as e:
            logger.error(
                "Safety evaluation failed",
                entity_id=self.entity_id,
                error=str(e)
            )
            raise EntityEvaluationError(f"Safety evaluation failed: {e}")

    def evaluate_security_risks(self, proposal: str) -> List[str]:
        """Dedicated security risk assessment"""
        security_risks = []
        proposal_lower = proposal.lower()

        # Check for common security patterns
        security_patterns = {
            r"password|credential|secret|token": "Potential credential exposure risk",
            r"admin|root|privilege": "Privilege escalation risk",
            r"sql|query|database": "SQL injection risk",
            r"execute|eval|system|shell": "Code execution risk",
            r"file|path|directory": "File system access risk",
            r"network|http|request": "Network security risk"
        }

        for pattern, risk_description in security_patterns.items():
            if re.search(pattern, proposal_lower):
                security_risks.append(risk_description)

        return security_risks

    def check_constraint_violations(self, proposal: str) -> List[str]:
        """Check for architectural constraint violations"""
        return self._check_forbidden_patterns(proposal)

    def assess_ethical_implications(self, proposal: str) -> Dict[str, float]:
        """Evaluate ethical concerns with severity scores"""
        ethical_concerns = {}
        proposal_lower = proposal.lower()

        # Define ethical risk patterns with severity scores
        ethical_patterns = {
            r"bias|discriminat|unfair": ("Bias and discrimination risk", 0.8),
            r"privacy|personal|data": ("Privacy violation risk", 0.7),
            r"harmful|dangerous|malicious": ("Potential harm risk", 0.9),
            r"manipulat|deceiv|mislead": ("Manipulation risk", 0.8),
            r"surveillance|monitor|track": ("Surveillance concern", 0.6)
        }

        for pattern, (concern, severity) in ethical_patterns.items():
            if re.search(pattern, proposal_lower):
                ethical_concerns[concern] = severity

        return ethical_concerns

    def trigger_veto_if_needed(self, score: float) -> bool:
        """Determine if veto should be triggered"""
        return score < self.config.SAFETY_VETO_THRESHOLD
