import asyncio
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Post, Subreddit
from ingestion.reddit_client import RedditClient
import logging
from datetime import datetime

# Build DB tables if they don't exist
Base.metadata.create_all(bind=engine)

logger = logging.getLogger(__name__)

# List of strategic subreddits to monitor
TARGET_SUBREDDITS = [
    {"name": "startups", "category": "Entrepreneurship"},
    {"name": "entrepreneur", "category": "Entrepreneurship"},
    {"name": "saas", "category": "SaaS"},
    {"name": "webdev", "category": "Developer"},
    {"name": "marketing", "category": "Niche"},
    {"name": "automation", "category": "Automation"},
]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_posts(db: Session, posts_data: list):
    new_count = 0
    for post_dict in posts_data:
        # Check if exists
        existing = db.query(Post).filter(Post.id == post_dict["id"]).first()
        if existing:
            continue
        
        # Ensure Subreddit exists
        sub_name = post_dict["subreddit"]
        subreddit = db.query(Subreddit).filter(Subreddit.name == sub_name).first()
        if not subreddit:
            # We should have created them, but just in case
            subreddit = Subreddit(name=sub_name, category="Unknown")
            db.add(subreddit)
            db.commit()
            db.refresh(subreddit)

        new_post = Post(
            id=post_dict["id"],
            subreddit_id=subreddit.id,
            title=post_dict["title"],
            text=post_dict["text"],
            url=post_dict["url"],
            author=post_dict["author"],
            score=post_dict["score"],
            num_comments=post_dict["num_comments"],
            created_utc=datetime.fromtimestamp(post_dict["created_utc"]),
            is_processed=False
        )
        db.add(new_post)
        new_count += 1
    
    db.commit()
    logger.info(f"Saved {new_count} new posts to database.")

def main():
    db = SessionLocal()
    client = RedditClient()
    
    # 1. Initialize Subreddits
    for sub in TARGET_SUBREDDITS:
        existing = db.query(Subreddit).filter(Subreddit.name == sub["name"]).first()
        if not existing:
            new_sub = Subreddit(name=sub["name"], category=sub["category"])
            db.add(new_sub)
    db.commit()
    
    # 2. Fetch & Save
    for sub in TARGET_SUBREDDITS:
        logger.info(f"Scanning r/{sub['name']}...")
        posts = client.get_posts(sub["name"], limit=50, filters=["hot", "top"])
        save_posts(db, posts)
        
        # Update last_scanned
        db_sub = db.query(Subreddit).filter(Subreddit.name == sub["name"]).first()
        if db_sub:
            db_sub.last_scanned_at = datetime.now()
            db.commit()

    db.close()

if __name__ == "__main__":
    main()
