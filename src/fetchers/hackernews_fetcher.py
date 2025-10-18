"""
Hacker News fetcher
Fetches top and best stories from Hacker News API
"""

import requests
from typing import List, Dict
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class HackerNewsFetcher:
    """Fetches stories from Hacker News using the official API"""

    BASE_URL = "https://hacker-news.firebaseio.com/v0"
    TOP_STORIES_URL = f"{BASE_URL}/topstories.json"
    BEST_STORIES_URL = f"{BASE_URL}/beststories.json"
    ITEM_URL = f"{BASE_URL}/item/{{item_id}}.json"

    def __init__(self, story_count: int = 30):
        """
        Initialize Hacker News fetcher

        Args:
            story_count: Number of stories to fetch
        """
        self.story_count = story_count
        self.session = requests.Session()

    def fetch_stories(self) -> List[Dict[str, any]]:
        """
        Fetch top stories from Hacker News

        Returns:
            List of story dictionaries
        """
        logger.info(f"Fetching {self.story_count} stories from Hacker News...")
        try:
            # Get top story IDs
            response = self.session.get(self.TOP_STORIES_URL, timeout=10)
            response.raise_for_status()
            story_ids = response.json()[:self.story_count]

            # Fetch story details in parallel
            stories = self._fetch_story_details(story_ids)

            logger.info(f"Successfully fetched {len(stories)} HN stories")
            return stories

        except Exception as e:
            logger.error(f"Error fetching Hacker News stories: {e}")
            return []

    def _fetch_story_details(self, story_ids: List[int]) -> List[Dict[str, any]]:
        """
        Fetch details for multiple stories in parallel

        Args:
            story_ids: List of story IDs to fetch

        Returns:
            List of story dictionaries
        """
        stories = []

        # Use ThreadPoolExecutor for parallel fetching
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_id = {
                executor.submit(self._fetch_single_story, story_id): story_id
                for story_id in story_ids
            }

            for future in as_completed(future_to_id):
                try:
                    story = future.result()
                    if story:
                        stories.append(story)
                except Exception as e:
                    logger.warning(f"Error fetching story: {e}")

        # Sort by score (points) to maintain ranking
        stories.sort(key=lambda x: x.get('score', 0), reverse=True)
        return stories

    def _fetch_single_story(self, story_id: int) -> Dict[str, any]:
        """
        Fetch a single story's details

        Args:
            story_id: Story ID to fetch

        Returns:
            Story dictionary or None if fetch fails
        """
        try:
            url = self.ITEM_URL.format(item_id=story_id)
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            # Only include stories with URLs (not Ask HN, etc.)
            if not data or data.get('type') != 'story':
                return None

            # Get the URL - use story URL if available, otherwise HN discussion
            story_url = data.get('url')
            if not story_url:
                story_url = f"https://news.ycombinator.com/item?id={story_id}"

            return {
                'source': 'Hacker News',
                'title': data.get('title', ''),
                'url': story_url,
                'score': data.get('score', 0),
                'comments_count': data.get('descendants', 0),
                'score_label': f"{data.get('score', 0)} points",
                'hn_url': f"https://news.ycombinator.com/item?id={story_id}",
                'author': data.get('by', ''),
                'time': data.get('time', 0)
            }

        except Exception as e:
            logger.warning(f"Error fetching story {story_id}: {e}")
            return None

    def fetch_all(self) -> List[Dict[str, any]]:
        """
        Fetch all stories

        Returns:
            List of all stories
        """
        return self.fetch_stories()
