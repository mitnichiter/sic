from sqlalchemy.orm import Session
from models import ProblemCluster, GeneratedIdea
from ai.llm_provider import LLMProvider
from config import settings
import logging
import json

logger = logging.getLogger(__name__)

class IdeaGenerator:
    def __init__(self, db: Session):
        self.db = db
        self.llm = LLMProvider()

    def generate_ideas_for_cluster(self, cluster_id: int):
        cluster = self.db.query(ProblemCluster).filter(ProblemCluster.id == cluster_id).first()
        if not cluster:
            logger.error(f"Cluster {cluster_id} not found.")
            return

        # Gather context
        problems = [p.text for p in cluster.problems[:10]] # Limit context
        context_text = "\n- ".join(problems)

        prompt = (
            f"Based on the following list of user problems/complaints, generate 3 startup ideas.\n"
            f"Problems:\n- {context_text}\n\n"
            "Format the output as a valid JSON object with a key 'ideas' containing a list of objects with keys: "
            "'title', 'description', 'solution_type', 'monetization_strategy', 'technical_complexity', 'market_size_estimate'."
        )

        try:
            data = self.llm.generate_json(
                system_prompt="You are a creative startup founder. Output strictly JSON.",
                user_prompt=prompt
            )
            
            if not data:
                logger.error("Failed to generate valid JSON from LLM.")
                return

            ideas = data.get("ideas", []) 
            # Handle edge cases where LLM returns list directly or unwrapped dict
            if not ideas and isinstance(data, list):
                 ideas = data
            elif isinstance(data, dict) and "ideas" not in data:
                 # Try to find a list value in any key
                 for k, v in data.items():
                     if isinstance(v, list):
                         ideas = v
                         break

            for idea in ideas:
                new_idea = GeneratedIdea(
                    cluster_id=cluster.id,
                    title=idea.get("title", "Untitled"),
                    description=idea.get("description", ""),
                    solution_type=idea.get("solution_type", "SaaS"),
                    monetization_strategy=idea.get("monetization_strategy", "Subscription"),
                    technical_complexity=idea.get("technical_complexity", "Medium"),
                    market_size_estimate=idea.get("market_size_estimate", "Unknown")
                )
                self.db.add(new_idea)
            
            self.db.commit()
            logger.info(f"Generated {len(ideas)} ideas for Cluster {cluster.id}")

        except Exception as e:
            logger.error(f"Error generating ideas: {e}")
