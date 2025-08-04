import openai
from typing import Dict, List, Optional
from ..config import CoppeliaConfig
from ..exceptions import EntityEvaluationError
from .logging_config import get_logger

logger = get_logger(__name__)

class LLMClient:
    """OpenAI API wrapper with error handling and logging"""

    def __init__(self, config: CoppeliaConfig):
        self.config = config
        self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        entity_id: str,
        max_retries: int = 3
    ) -> str:
        """Generate LLM response with retries and error handling"""

        for attempt in range(max_retries):
            try:
                logger.info(
                    "Generating LLM response",
                    entity_id=entity_id,
                    attempt=attempt + 1,
                    message_count=len(messages)
                )

                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    max_tokens=self.config.MAX_TOKENS,
                    temperature=self.config.TEMPERATURE,
                    response_format={"type": "json_object"}
                )

                content = response.choices[0].message.content

                logger.info(
                    "LLM response generated successfully",
                    entity_id=entity_id,
                    response_length=len(content) if content else 0
                )

                return content

            except Exception as e:
                logger.error(
                    "LLM API error",
                    entity_id=entity_id,
                    attempt=attempt + 1,
                    error=str(e)
                )

                if attempt == max_retries - 1:
                    raise EntityEvaluationError(
                        f"Failed to generate response for {entity_id} after {max_retries} attempts: {e}"
                    )

        raise EntityEvaluationError(f"Unexpected error in LLM client for {entity_id}")
