from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean, JSON, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from database import Base

class Subreddit(Base):
    __tablename__ = "subreddits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    category = Column(String) # e.g., "Entrepreneurship", "Developer"
    description = Column(Text, nullable=True)
    subscriber_count = Column(Integer, default=0)
    last_scanned_at = Column(DateTime(timezone=True), nullable=True)
    
    posts = relationship("Post", back_populates="subreddit")

class Post(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True) # Reddit ID (e.g., "t3_xxxxx")
    subreddit_id = Column(Integer, ForeignKey("subreddits.id"))
    title = Column(String)
    text = Column(Text)
    url = Column(String)
    author = Column(String)
    score = Column(Integer, default=0)
    num_comments = Column(Integer, default=0)
    created_utc = Column(DateTime(timezone=True))
    
    # Processing Status
    is_processed = Column(Boolean, default=False)
    has_problem = Column(Boolean, default=False)
    
    subreddit = relationship("Subreddit", back_populates="posts")
    extracted_problems = relationship("ProblemStatement", back_populates="post")

class ProblemStatement(Base):
    __tablename__ = "problem_statements"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String, ForeignKey("posts.id"))
    
    text = Column(Text) # The extracted problem statement
    original_text_segment = Column(Text) # The quote from the post
    sentiment_score = Column(Float, nullable=True)
    embedding = Column(Vector(1536)) # OpenAI embedding dimension
    
    cluster_id = Column(Integer, ForeignKey("problem_clusters.id"), nullable=True)
    
    post = relationship("Post", back_populates="extracted_problems")
    cluster = relationship("ProblemCluster", back_populates="problems")

class ProblemCluster(Base):
    __tablename__ = "problem_clusters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String) # Auto-generated name
    description = Column(Text)
    
    # Metrics
    frequency_score = Column(Float, default=0.0)
    intensity_score = Column(Float, default=0.0)
    engagement_score = Column(Float, default=0.0)
    recency_score = Column(Float, default=0.0)
    total_validation_score = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    problems = relationship("ProblemStatement", back_populates="cluster")
    generated_ideas = relationship("GeneratedIdea", back_populates="cluster")

class GeneratedIdea(Base):
    __tablename__ = "generated_ideas"

    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("problem_clusters.id"))
    
    title = Column(String)
    description = Column(Text)
    solution_type = Column(String) # SaaS, App, Extension, etc.
    monetization_strategy = Column(String)
    technical_complexity = Column(String)
    market_size_estimate = Column(String)
    
    cluster = relationship("ProblemCluster", back_populates="generated_ideas")
