from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import ProblemCluster, GeneratedIdea
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel

app = FastAPI(title="Reddit Idea Validator API")

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models for Response
class IdeaResponse(BaseModel):
    title: str
    description: str
    solution_type: str
    monetization_strategy: str
    market_size_estimate: str

class ClusterResponse(BaseModel):
    id: int
    name: str
    description: str
    frequency_score: float
    intensity_score: float
    engagement_score: float
    recency_score: float
    total_validation_score: float
    generated_ideas: List[IdeaResponse] = []

    class Config:
        from_attributes = True

@app.get("/clusters", response_model=List[ClusterResponse])
def get_clusters(db: Session = Depends(get_db)):
    clusters = db.query(ProblemCluster).order_by(ProblemCluster.total_validation_score.desc()).all()
    return clusters

@app.get("/clusters/{cluster_id}", response_model=ClusterResponse)
def get_cluster(cluster_id: int, db: Session = Depends(get_db)):
    cluster = db.query(ProblemCluster).filter(ProblemCluster.id == cluster_id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return cluster

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Reddit Validator API is running"}
