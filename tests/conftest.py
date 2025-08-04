import pytest
from src.coppelia.config import CoppeliaConfig
from src.coppelia.utils.logging_config import configure_logging

@pytest.fixture(scope="session")
def config():
    """Test configuration"""
    return CoppeliaConfig(
        OPENAI_API_KEY="test-key",
        LOG_LEVEL="DEBUG",
        MAX_TOKENS=100,
        TEMPERATURE=0.0
    )

@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    """Configure logging for tests"""
    configure_logging("DEBUG")
