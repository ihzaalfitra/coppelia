from typing import Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings

class CoppeliaConfig(BaseSettings):
    """System configuration with safety constraints"""

    # Consensus Parameters (IMMUTABLE)
    # NEW - Just use Field() or direct assignment
    SAFETY_VETO_THRESHOLD: float = 0.6
    CONSENSUS_THRESHOLD: float = 0.7
    MAX_DISCUSSION_ROUNDS: int = 3
    ENTITY_WEIGHTS: Dict[str, float] = {
        "safety_validator": 0.5,
        "logic_checker": 0.35,
        "efficiency_monitor": 0.15
    }

    # Runtime Configuration (MUTABLE)
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    MAX_TOKENS: int = Field(1000, env="MAX_TOKENS")
    TEMPERATURE: float = Field(0.3, env="TEMPERATURE")

    class Config:
        env_file = ".env"
        case_sensitive = True
