import pytest
from datetime import datetime
from src.coppelia.models.assessment import Assessment, ConsensusResult

def test_assessment_creation():
    """Test valid assessment creation"""
    assessment = Assessment(
        entity_id="test_entity",
        score=0.8,
        reasoning="Test reasoning that is long enough",
        concerns=["concern1", "concern2"],
        suggestions=["suggestion1"],
        confidence=0.9
    )

    assert assessment.entity_id == "test_entity"
    assert assessment.score == 0.8
    assert len(assessment.concerns) == 2
    assert isinstance(assessment.timestamp, datetime)

def test_assessment_validation():
    """Test assessment validation"""
    with pytest.raises(ValueError):
        Assessment(
            entity_id="test",
            score=1.5,  # Invalid score > 1.0
            reasoning="Short",  # Too short
            confidence=0.9
        )

def test_consensus_result_creation():
    """Test consensus result creation"""
    assessment = Assessment(
        entity_id="test",
        score=0.8,
        reasoning="Test reasoning that is long enough",
        confidence=0.9
    )

    result = ConsensusResult(
        approved=True,
        final_score=0.75,
        reason="Consensus reached",
        assessments=[assessment]
    )

    assert result.approved
    assert result.final_score == 0.75
    assert len(result.assessments) == 1
