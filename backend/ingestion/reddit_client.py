import praw
import time
from typing import List, Dict, Any
from config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedditClient:
    def __init__(self):
        if not settings.REDDIT_CLIENT_ID or not settings.REDDIT_CLIENT_SECRET:
            logger.warning("Reddit API credentials not set. Ingestion will fail.")
        
        self.reddit = praw.Reddit(
            client_id=settings.REDDIT_CLIENT_ID,
            client_secret=settings.REDDIT_CLIENT_SECRET,
            user_agent=settings.REDDIT_USER_AGENT
        )

    def get_posts(self, subreddit_name: str, limit: int = 50, filters: List[str] = ["hot", "top"]) -> List[Dict[str, Any]]:
        """
        Fetches posts from a subreddit using specified filters.
        """
        subreddit = self.reddit.subreddit(subreddit_name)
        posts_data = []
        
        try:
            for filter_type in filters:
                if filter_type == "hot":
                    posts = subreddit.hot(limit=limit)
                elif filter_type == "top":
                    posts = subreddit.top(time_filter="week", limit=limit)
                elif filter_type == "new":
                    posts = subreddit.new(limit=limit)
                else:
                    continue

                for post in posts:
                    if post.stickied:
                        continue
                    
                    posts_data.append({
                        "id": post.id,
                        "title": post.title,
                        "text": post.selftext,
                        "url": post.url,
                        "author": str(post.author),
                        "score": post.score,
                        "num_comments": post.num_comments,
                        "created_utc": post.created_utc,
                        "subreddit": subreddit_name
                    })
            
            logger.info(f"Fetched {len(posts_data)} posts from r/{subreddit_name}")
            return posts_data

        except Exception as e:
            logger.error(f"Error fetching from r/{subreddit_name}: {e}")
            return []

    def check_limits(self):
        """
        Logs rate limit status.
        """
        limits = self.reddit.auth.limits
        logger.info(f"Rate Limits: {limits}")
