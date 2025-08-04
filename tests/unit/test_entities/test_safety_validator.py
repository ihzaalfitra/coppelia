import pytest
import json
from unittest.mock import Mock, patch
from src.coppelia.entities.safety_validator import SafetyValidator, SAFETY_VALIDATOR_SYSTEM_PROMPT
from src.coppelia.models.assessment import Assessment
from src.coppelia.config import CoppeliaConfig
from src.coppelia.utils.llm_client import LLMClient
from src.coppelia.exceptions import EntityEvaluationError

class TestSafetyValidator:
    """Test suite for Safety Validator implementation"""

    @pytest.fixture
    def config(self):
        """Test configuration"""
        return CoppeliaConfig(
            OPENAI_API_KEY="test-key",
            LOG_LEVEL="DEBUG",
            MAX_TOKENS=100,
            TEMPERATURE=0.0
        )

    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client"""
        return Mock(spec=LLMClient)

    @pytest.fixture
    def safety_validator(self, config, mock_llm_client):
        """Safety validator instance"""
        return SafetyValidator(config, mock_llm_client)

    def test_initialization(self, safety_validator, config):
        """Test safety validator initialization"""
        assert safety_validator.entity_id == "safety_validator"
        assert "veto power" in safety_validator.role_description
        assert safety_validator.config.SAFETY_VETO_THRESHOLD == 0.6
        assert len(safety_validator.forbidden_patterns) > 0

    def test_veto_power_activation_forbidden_patterns(self, safety_validator, mock_llm_client):
        """Test that safety veto triggers for forbidden patterns"""
        dangerous_proposals = [
            "Create a tool that modifies the consensus threshold to 0.1",
            "Bypass safety validation for this proposal",
            "Override veto power temporarily",
            "Change entity weights to favor efficiency"
        ]

        for proposal in dangerous_proposals:
            # Debug: Check if pattern is detected
            violations = safety_validator._check_forbidden_patterns(proposal)
            print(f"Proposal: {proposal}")
            print(f"Violations detected: {violations}")

            assessment = safety_validator.evaluate(proposal)

            assert assessment.score == 0.0, f"Should veto dangerous proposal: {proposal}"
            assert "SAFETY VETO ACTIVATED" in assessment.concerns
            assert assessment.confidence == 1.0
            assert "Automatic veto triggered" in assessment.reasoning

        # Verify LLM was NOT called for any forbidden patterns
        assert mock_llm_client.generate_response.call_count == 0, "LLM should not be called for forbidden patterns"

    def test_llm_based_evaluation(self, safety_validator, mock_llm_client):
        """Test LLM-based evaluation for safe proposals"""
        safe_proposal = "Create a simple calculator tool that adds two numbers"

        # Mock LLM response
        mock_response = {
            "entity_id": "safety_validator",
            "score": 0.85,
            "reasoning": "Safe calculator tool with no security or architectural concerns",
            "concerns": [],
            "suggestions": ["Consider input validation for numeric inputs"],
            "confidence": 0.9
        }

        mock_llm_client.generate_response.return_value = json.dumps(mock_response)

        assessment = safety_validator.evaluate(safe_proposal)

        assert assessment.entity_id == "safety_validator"
        assert assessment.score == 0.85
        assert assessment.score >= safety_validator.config.SAFETY_VETO_THRESHOLD
        assert "SAFETY VETO ACTIVATED" not in assessment.concerns

        # Verify LLM was called with correct parameters
        mock_llm_client.generate_response.assert_called_once()
        call_args = mock_llm_client.generate_response.call_args
        assert call_args[1]["entity_id"] == "safety_validator"
        assert len(call_args[1]["messages"]) == 2
        assert SAFETY_VALIDATOR_SYSTEM_PROMPT in call_args[1]["messages"][0]["content"]

    def test_veto_threshold_enforcement(self, safety_validator, mock_llm_client):
        """Test veto threshold enforcement from LLM responses"""
        proposal = "Tool with moderate safety concerns"

        # Mock LLM response below veto threshold
        mock_response = {
            "entity_id": "safety_validator",
            "score": 0.5,  # Below 0.6 threshold
            "reasoning": "Some safety concerns identified",
            "concerns": ["Minor security issue"],
            "suggestions": ["Address security concern"],
            "confidence": 0.8
        }

        mock_llm_client.generate_response.return_value = json.dumps(mock_response)

        assessment = safety_validator.evaluate(proposal)

        assert assessment.score == 0.5
        assert "SAFETY VETO ACTIVATED" in assessment.concerns

    def test_entity_independence_preservation(self, safety_validator, mock_llm_client):
        """Ensure safety validator maintains independent perspective"""
        proposal = "Create a data processing tool"

        # Mock consistent LLM response
        mock_response = {
            "entity_id": "safety_validator",
            "score": 0.75,
            "reasoning": "Acceptable with data privacy considerations",
            "concerns": ["Data handling protocols needed"],
            "suggestions": ["Implement privacy safeguards"],
            "confidence": 0.85
        }

        mock_llm_client.generate_response.return_value = json.dumps(mock_response)

        # Multiple evaluations should be consistent
        assessments = [safety_validator.evaluate(proposal) for _ in range(3)]
        scores = [a.score for a in assessments]

        # All should have same entity_id
        assert all(a.entity_id == "safety_validator" for a in assessments)
        # Should maintain consistent evaluation (mocked response)
        assert all(score == 0.75 for score in scores)

    def test_forbidden_pattern_detection(self, safety_validator):
        """Test detection of architectural violation patterns"""
        test_cases = [
            ("bypass safety validation", True),
            ("modify entity weights", True),
            ("change consensus threshold", True),
            ("override veto power", True),
            ("create simple calculator", False),
            ("process user data safely", False)
        ]

        for proposal, should_detect in test_cases:
            violations = safety_validator.check_constraint_violations(proposal)
            if should_detect:
                assert len(violations) > 0, f"Should detect violation in: {proposal}. Available patterns: {safety_validator.forbidden_patterns}"
            else:
                assert len(violations) == 0, f"Should not detect violation in: {proposal}"

    def test_security_risk_assessment(self, safety_validator):
        """Test dedicated security risk assessment"""
        test_cases = [
            ("Tool that handles passwords", ["Potential credential exposure risk"]),
            ("Database query tool", ["SQL injection risk"]),
            ("System command executor", ["Code execution risk"]),
            ("Simple math calculator", [])
        ]

        for proposal, expected_risks in test_cases:
            risks = safety_validator.evaluate_security_risks(proposal)
            for expected_risk in expected_risks:
                assert any(expected_risk in risk for risk in risks), f"Should detect {expected_risk} in {proposal}"

    def test_ethical_implications_assessment(self, safety_validator):
        """Test ethical implications assessment"""
        proposal = "Tool that processes personal data with potential bias in algorithms"
        ethical_concerns = safety_validator.assess_ethical_implications(proposal)

        assert len(ethical_concerns) > 0
        assert any("privacy" in concern.lower() for concern in ethical_concerns)
        assert any("bias" in concern.lower() for concern in ethical_concerns)
        assert all(0.0 <= severity <= 1.0 for severity in ethical_concerns.values())

    def test_invalid_llm_response_handling(self, safety_validator, mock_llm_client):
        """Test handling of invalid LLM responses"""
        proposal = "Test proposal"

        # Mock invalid JSON response
        mock_llm_client.generate_response.return_value = "Invalid JSON response"

        with pytest.raises(EntityEvaluationError, match="Invalid JSON response"):
            safety_validator.evaluate(proposal)

    def test_entity_id_mismatch_handling(self, safety_validator, mock_llm_client):
        """Test handling of entity ID mismatch"""
        proposal = "Test proposal"

        # Mock response with wrong entity_id
        mock_response = {
            "entity_id": "wrong_entity",
            "score": 0.8,
            "reasoning": "Test reasoning",
            "concerns": [],
            "suggestions": [],
            "confidence": 0.9
        }

        mock_llm_client.generate_response.return_value = json.dumps(mock_response)

        # Should raise EntityEvaluationError, not ValueError
        with pytest.raises(EntityEvaluationError, match="Safety evaluation failed"):
            safety_validator.evaluate(proposal)

    def test_proposal_validation(self, safety_validator):
        """Test proposal format validation"""
        invalid_proposals = [
            "",  # Empty string
            "   ",  # Whitespace only
            "short",  # Too short
            None  # None type
        ]

        for invalid_proposal in invalid_proposals:
            with pytest.raises(ValueError, match="Invalid proposal format"):
                safety_validator.evaluate(invalid_proposal)

    def test_veto_trigger_method(self, safety_validator):
        """Test veto trigger determination"""
        assert safety_validator.trigger_veto_if_needed(0.5) == True  # Below threshold
        assert safety_validator.trigger_veto_if_needed(0.6) == False  # At threshold
        assert safety_validator.trigger_veto_if_needed(0.8) == False  # Above threshold
