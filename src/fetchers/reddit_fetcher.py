"""
Reddit fetcher
Fetches posts from user's personal Reddit feed
"""

import praw
from typing import List, Dict
import logging
import os

logger = logging.getLogger(__name__)


class RedditFetcher:
    """Fetches posts from user's personal Reddit feed"""

    def __init__(self, post_count: int = 30, use_personal_feed: bool = True):
        """
        Initialize Reddit fetcher

        Args:
            post_count: Number of posts to fetch
            use_personal_feed: Whether to use personal feed (subscribed subreddits)
        """
        self.post_count = post_count
        self.use_personal_feed = use_personal_feed

        # Initialize Reddit client with credentials from environment
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                username=os.getenv('REDDIT_USERNAME'),
                password=os.getenv('REDDIT_PASSWORD'),
                user_agent='DailyDigestBot/1.0'
            )
            logger.info("Reddit client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Reddit client: {e}")
            self.reddit = None

    def fetch_posts(self) -> List[Dict[str, any]]:
        """
        Fetch posts from user's personal feed

        Returns:
            List of post dictionaries
        """
        if not self.reddit:
            logger.error("Reddit client not initialized")
            return []

        logger.info(f"Fetching {self.post_count} posts from Reddit personal feed...")

        try:
            posts = []

            if self.use_personal_feed:
                # Fetch from user's front page (subscribed subreddits)
                for submission in self.reddit.front.hot(limit=self.post_count):
                    post = self._parse_submission(submission)
                    if post:
                        posts.append(post)
            else:
                # Fetch from r/all as fallback
                for submission in self.reddit.subreddit('all').hot(limit=self.post_count):
                    post = self._parse_submission(submission)
                    if post:
                        posts.append(post)

            logger.info(f"Successfully fetched {len(posts)} Reddit posts")
            return posts

        except Exception as e:
            logger.error(f"Error fetching Reddit posts: {e}")
            return []

    def _parse_submission(self, submission) -> Dict[str, any]:
        """
        Parse a Reddit submission into a dictionary

        Args:
            submission: PRAW Submission object

        Returns:
            Dictionary with post data
        """
        try:
            # Get the URL - prefer link posts, but include self posts too
            url = submission.url
            if submission.is_self:
                url = f"https://reddit.com{submission.permalink}"

            return {
                'source': 'Reddit',
                'title': submission.title,
                'url': url,
                'score': submission.score,
                'subreddit': submission.subreddit.display_name,
                'comments_count': submission.num_comments,
                'score_label': f"{submission.score} upvotes",
                'reddit_url': f"https://reddit.com{submission.permalink}",
                'author': str(submission.author) if submission.author else '[deleted]',
                'is_self': submission.is_self,
                'selftext': submission.selftext[:200] if submission.is_self else ''
            }

        except Exception as e:
            logger.warning(f"Error parsing Reddit submission: {e}")
            return None

    def fetch_all(self) -> List[Dict[str, any]]:
        """
        Fetch all posts

        Returns:
            List of all posts
        """
        return self.fetch_posts()
