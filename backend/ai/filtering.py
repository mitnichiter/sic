from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class NoiseFilter:
    def __init__(self):
        self.min_length = 50
        self.meme_flairs = ["Meme", "Comedy", "Satire", "Funny", "Shitpost"]
        self.ignore_keywords = ["promotion", "promo", "discount", "code", "referral"]

    def is_noise(self, post: Dict[str, Any]) -> bool:
        """
        Returns True if the post is considered noise.
        """
        text = post.get("text", "") or ""
        title = post.get("title", "") or ""
        flair = post.get("link_flair_text", "")
        
        # 1. Length Check
        if len(text) < self.min_length:
            return True
            
        # 2. Flair Check
        if flair and any(f.lower() in str(flair).lower() for f in self.meme_flairs):
            return True
            
        # 3. Keyword Check (Simple spam detection)
        content = (title + " " + text).lower()
        if any(kw in content for kw in self.ignore_keywords):
            return True

        return False

    def filter_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filters a list of posts.
        """
        filtered = [p for p in posts if not self.is_noise(p)]
        logger.info(f"Filtered {len(posts)} posts down to {len(filtered)} potential signals.")
        return filtered
