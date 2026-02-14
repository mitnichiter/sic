from typing import List
from ai.llm_provider import LLMProvider
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.llm = LLMProvider()

    def get_embedding(self, text: str) -> List[float]:
        """
        Generates a vector embedding for the given text.
        """
        try:
            return self.llm.get_embedding(text)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []
