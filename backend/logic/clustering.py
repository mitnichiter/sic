import numpy as np
import hdbscan
from sqlalchemy.orm import Session
from models import ProblemStatement, ProblemCluster
import logging
from typing import List

logger = logging.getLogger(__name__)

class ClusterEngine:
    def __init__(self, db: Session):
        self.db = db
        self.min_cluster_size = 3
        self.min_samples = 1

    def run_clustering(self):
        """
        Fetches unclustered problems, runs HDBSCAN, and updates the database.
        """
        # 1. Fetch unclustered problems
        unclustered = self.db.query(ProblemStatement).filter(ProblemStatement.cluster_id == None).all()
        
        if len(unclustered) < self.min_cluster_size:
            logger.info("Not enough data to cluster.")
            return

        ids = [p.id for p in unclustered]
        embeddings = [np.array(p.embedding) for p in unclustered]
        
        # 2. Run HDBSCAN
        # We use a cosine distance metric (or euclidean on normalized vectors)
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=self.min_cluster_size,
            min_samples=self.min_samples,
            metric='euclidean' # Assuming normalized embeddings
        )
        labels = clusterer.fit_predict(embeddings)
        
        # 3. Group and Save
        clusters_found = 0
        unique_labels = set(labels)
        
        for label in unique_labels:
            if label == -1:
                # Noise points
                continue
            
            # Get points in this cluster
            indices = [i for i, x in enumerate(labels) if x == label]
            cluster_problems = [unclustered[i] for i in indices]
            
            # Create new Cluster in DB
            new_cluster = ProblemCluster(
                name=f"Cluster {label} - {cluster_problems[0].text[:30]}...",
                description="Auto-generated cluster based on embedding similarity."
            )
            self.db.add(new_cluster)
            self.db.commit()
            self.db.refresh(new_cluster)
            
            # Assign problems to this cluster
            for p in cluster_problems:
                p.cluster_id = new_cluster.id
            
            self.db.commit()
            clusters_found += 1
            
        logger.info(f"Clustering complete. Found {clusters_found} new clusters.")
