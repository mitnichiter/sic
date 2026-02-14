from typing import Optional
from ai.llm_provider import LLMProvider
import logging

logger = logging.getLogger(__name__)

class ProblemExtractor:
    def __init__(self):
        self.llm = LLMProvider()

    def extract_problem(self, text: str) -> Optional[str]:
        """
        Extracts a core problem statement from the text. Returns None if no clear problem is found.
        """
        prompt = (
            "Analyze the following Reddit post text and extract the core problem, frustration, or unmet need. "
            "Ignore broad complaints or memes. "
            "If a specific problem is found, return it as a concise single sentence starting with 'Problem: ...'. "
            "If no clear problem is found, return 'NO_PROBLEM'.\n\n"
            f"Text: {text[:2000]}" # Truncate for token limits
        )

        try:
            result = self.llm.generate_text(
                system_prompt="You are an expert product researcher finding startup opportunities.",
                user_prompt=prompt,
                max_tokens=100
            )
            
            if not result:
                return None
                
            if result.startswith("Problem:"):
                return result.replace("Problem:", "").strip()
            elif result == "NO_PROBLEM":
                return None
            else:
                return result # Fallback

        except Exception as e:
            logger.error(f"Error extracting problem: {e}")
            return None
