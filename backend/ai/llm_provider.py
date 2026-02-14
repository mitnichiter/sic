from typing import Optional, Any
from config import settings
from openai import OpenAI
import ollama
import logging
import json

logger = logging.getLogger(__name__)

class LLMProvider:
    def __init__(self):
        self.backend = settings.LLM_BACKEND
        if self.backend == "openai":
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL
        else:
            self.model = settings.OLLAMA_MODEL
            # Ollama client is stateless/http, no init needed usually but good to check connection
            pass

    def generate_text(self, system_prompt: str, user_prompt: str, max_tokens: int = 500) -> Optional[str]:
        try:
            if self.backend == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.0
                )
                return response.choices[0].message.content.strip()
            
            elif self.backend == "ollama":
                # Ollama doesn't always support 'system' role in the same way depending on model modelfile
                # But widely supported as a message parameter.
                response = ollama.chat(model=self.model, messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt},
                ])
                return response['message']['content'].strip()

        except Exception as e:
            logger.error(f"LLM Generation Error ({self.backend}): {e}")
            return None

    def generate_json(self, system_prompt: str, user_prompt: str) -> Optional[Any]:
        """
        Tries to force JSON output. 
        Note: Local models like Phi3/Gemma2 might need stricter prompting for JSON.
        """
        try:
            if self.backend == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)

            elif self.backend == "ollama":
                # For Ollama, we rely on the prompt or 'format="json"' if supported (newer versions)
                response = ollama.chat(
                    model=self.model, 
                    messages=[
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': user_prompt}
                    ],
                    format='json' # Force JSON mode in Ollama
                )
                content = response['message']['content']
                return json.loads(content)

        except Exception as e:
            logger.error(f"LLM JSON Error ({self.backend}): {e}")
            return None
            
    def get_embedding(self, text: str) -> list[float]:
        try:
            if self.backend == "openai":
                text = text.replace("\n", " ")
                response = self.client.embeddings.create(
                    input=[text],
                    model="text-embedding-3-small"
                )
                return response.data[0].embedding
            
            elif self.backend == "ollama":
                # Using nomic-embed-text or similar usually, but let's assume the user has an embedding model
                # or we use the main model (Gemma/Phi aren't great for embedding, better to use 'nomic-embed-text')
                # For simplicity, we'll try to use the configured model, but usually you want a specific embed model.
                # Let's fallback to 'nomic-embed-text' if not specified, or just use the model.
                embed_model = "nomic-embed-text" # Best practice practice for local
                response = ollama.embeddings(model=embed_model, prompt=text)
                return response['embedding']

        except Exception as e:
            logger.error(f"Embedding Error ({self.backend}): {e}")
            return []
