from sqlalchemy.orm import Session
from models import ProblemCluster, ProblemStatement, Post
from sqlalchemy import func
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ScoringEngine:
    def __init__(self, db: Session):
        self.db = db

    def calculate_scores(self, cluster_id: int):
        cluster = self.db.query(ProblemCluster).filter(ProblemCluster.id == cluster_id).first()
        if not cluster:
            return

        problems = cluster.problems
        if not problems:
            return

        # 1. Frequency (Normalizing? Let's just use raw count for now, capped at 50)
        # In a real app, we'd normalize against the average cluster size.
        count = len(problems)
        f_score = min(count / 50.0, 1.0) * 100

        # 2. Intensity (Sentiment)
        # Assuming sentiment_score in DB is -1 to 1. We want negative intensity.
        # So close to -1 is high intensity.
        dataset_intensity = []
        for p in problems:
            # If we haven't computed sentiment yet, assume neutral (0)
            s = p.sentiment_score if p.sentiment_score is not None else 0
            # Convert to intensity: -1 -> 1.0, 1 -> 0.0
            intensity = (s * -1 + 1) / 2
            dataset_intensity.append(intensity)
        
        avg_intensity = sum(dataset_intensity) / len(dataset_intensity) if dataset_intensity else 0
        i_score = avg_intensity * 100

        # 3. Engagement
        # (Upvotes + Comments)
        total_engagement = 0
        for p in problems:
            if p.post:
                total_engagement += (p.post.score + p.post.num_comments)
        
        avg_engagement = total_engagement / count
        # Cap at 1000 for normalization
        e_score = min(avg_engagement / 1000.0, 1.0) * 100

        # 4. Recency
        # % of posts in last 30 days
        now = datetime.utcnow()
        recent_count = 0
        for p in problems:
            if p.post and p.post.created_utc:
                if p.post.created_utc > now - timedelta(days=30):
                    recent_count += 1
        
        r_score = (recent_count / count) * 100

        # Weighted Sum
        # F: 40%, I: 30%, E: 20%, R: 10%
        final_score = (f_score * 0.4) + (i_score * 0.3) + (e_score * 0.2) + (r_score * 0.1)

        # Update Cluster
        cluster.frequency_score = f_score
        cluster.intensity_score = i_score
        cluster.engagement_score = e_score
        cluster.recency_score = r_score
        cluster.total_validation_score = final_score
        
        self.db.commit()
        logger.info(f"Cluster {cluster.id} Score: {final_score:.2f}")

    def score_all_clusters(self):
        clusters = self.db.query(ProblemCluster).all()
        for cluster in clusters:
            self.calculate_scores(cluster.id)
