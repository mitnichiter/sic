import argparse
from ingestion.collector import main as run_collector
from database import SessionLocal
from logic.clustering import ClusterEngine
from logic.ideation import IdeaGenerator
from logic.scoring import ScoringEngine

def run_pipeline():
    print("Starting Pipeline...")
    
    # 1. Collection (Already implemented in collector.py, usually runs separately)
    # run_collector() 
    
    db = SessionLocal()
    
    # 2. AI Processing (Placeholder loop - in real app would use extracting/embedding)
    # For now, we assume data is ingested and processed by extraction/embedding scripts which we'd need to loop over.
    # But since we didn't make a dedicated "processor.py" that loops over DB, we can add it here or just skip to clustering for now.
    
    # 3. Clustering
    print("Running Clustering...")
    clusterer = ClusterEngine(db)
    clusterer.run_clustering()
    
    # 4. Scoring
    print("Running Scoring...")
    scorer = ScoringEngine(db)
    scorer.score_all_clusters()
    
    # 5. Ideation
    print("Running Ideation...")
    generator = IdeaGenerator(db)
    # Get top 5 clusters by score
    from models import ProblemCluster
    top_clusters = db.query(ProblemCluster).order_by(ProblemCluster.total_validation_score.desc()).limit(5).all()
    
    for cluster in top_clusters:
        print(f"Generating ideas for Cluster: {cluster.name} (Score: {cluster.total_validation_score})")
        generator.generate_ideas_for_cluster(cluster.id)

    db.close()
    print("Pipeline Complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--collect", action="store_true", help="Run data collection")
    parser.add_argument("--pipeline", action="store_true", help="Run AI pipeline")
    
    args = parser.parse_args()
    
    if args.collect:
        run_collector()
    elif args.pipeline:
        run_pipeline()
    else:
        print("Use --collect or --pipeline")
