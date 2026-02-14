from sqlalchemy.orm import Session
from sqlalchemy import select
from models import ProblemCluster, ProblemStatement
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, db: Session):
        self.db = db

    def add_problem(self, extracted_text: str, original_text: str, post_id: str, embedding: List[float]):
        """
        Adds a new extracted problem to the database with its embedding.
        """
        try:
            new_problem = ProblemStatement(
                post_id=post_id,
                text=extracted_text,
                original_text_segment=original_text,
                embedding=embedding
            )
            self.db.add(new_problem)
            self.db.commit()
            self.db.refresh(new_problem)
            logger.info(f"Added problem ID {new_problem.id} to vector store.")
            return new_problem
        except Exception as e:
            logger.error(f"Error adding to vector store: {e}")
            self.db.rollback()
            return None

    def search_similar(self, query_embedding: List[float], limit: int = 5):
        """
        Finds similar problems using cosine similarity (L2 distance is default in pgvector but we can use operators).
        """
        # Note: pgvector supports <-> (L2 distance), <=> (Cosine distance), <#> (Inner product)
        # We'll use cosine distance (<=>) for standardized vectors.
        stmt = select(ProblemStatement).order_by(
            ProblemStatement.embedding.cosine_distance(query_embedding)
        ).limit(limit)
        
        results = self.db.execute(stmt).scalars().all()
        return results
