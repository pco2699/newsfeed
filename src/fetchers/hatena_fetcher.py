"""
Hatena Bookmark fetcher
Fetches popular and new entries from Hatena Bookmark
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
import time

logger = logging.getLogger(__name__)


class HatenaFetcher:
    """Fetches articles from Hatena Bookmark"""

    POPULAR_URL = "https://b.hatena.ne.jp/hotentry/all"
    NEW_URL = "https://b.hatena.ne.jp/entrylist/all"

    def __init__(self, popular_count: int = 25, new_count: int = 15):
        """
        Initialize Hatena fetcher

        Args:
            popular_count: Number of popular entries to fetch
            new_count: Number of new entries to fetch
        """
        self.popular_count = popular_count
        self.new_count = new_count
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_popular(self) -> List[Dict[str, any]]:
        """
        Fetch popular entries from Hatena Bookmark

        Returns:
            List of article dictionaries with title, url, bookmarks, etc.
        """
        logger.info(f"Fetching {self.popular_count} popular entries from Hatena...")
        try:
            response = self.session.get(self.POPULAR_URL, timeout=10)
            response.raise_for_status()
            return self._parse_entries(response.text, limit=self.popular_count)
        except Exception as e:
            logger.error(f"Error fetching Hatena popular entries: {e}")
            return []

    def fetch_new(self) -> List[Dict[str, any]]:
        """
        Fetch new entries from Hatena Bookmark

        Returns:
            List of article dictionaries with title, url, bookmarks, etc.
        """
        logger.info(f"Fetching {self.new_count} new entries from Hatena...")
        try:
            response = self.session.get(self.NEW_URL, timeout=10)
            response.raise_for_status()
            return self._parse_entries(response.text, limit=self.new_count)
        except Exception as e:
            logger.error(f"Error fetching Hatena new entries: {e}")
            return []

    def _parse_entries(self, html: str, limit: int) -> List[Dict[str, any]]:
        """
        Parse HTML and extract article information

        Args:
            html: HTML content
            limit: Maximum number of entries to return

        Returns:
            List of parsed article dictionaries
        """
        soup = BeautifulSoup(html, 'lxml')
        entries = []

        # Find all article entries
        articles = soup.find_all('article', class_='entrylist-contents', limit=limit)

        for article in articles:
            try:
                entry = self._parse_article(article)
                if entry:
                    entries.append(entry)
            except Exception as e:
                logger.warning(f"Error parsing Hatena article: {e}")
                continue

        logger.info(f"Successfully parsed {len(entries)} Hatena entries")
        return entries

    def _parse_article(self, article) -> Optional[Dict[str, any]]:
        """
        Parse individual article element

        Args:
            article: BeautifulSoup article element

        Returns:
            Dictionary with article data or None if parsing fails
        """
        try:
            # Get title and URL
            title_elem = article.find('a', class_='js-keyboard-openable')
            if not title_elem:
                return None

            title = title_elem.get_text(strip=True)
            url = title_elem.get('href', '')

            # Get bookmark count
            bookmark_elem = article.find('span', class_='entrylist-contents-users')
            bookmarks = 0
            if bookmark_elem:
                bookmark_text = bookmark_elem.get_text(strip=True)
                try:
                    bookmarks = int(bookmark_text.replace(',', '').replace('users', ''))
                except ValueError:
                    bookmarks = 0

            # Get category/tag
            category_elem = article.find('a', class_='entrylist-contents-category')
            category = category_elem.get_text(strip=True) if category_elem else ''

            # Get description if available
            description_elem = article.find('p', class_='entrylist-contents-description')
            description = description_elem.get_text(strip=True) if description_elem else ''

            return {
                'source': 'はてブ',
                'title': title,
                'url': url,
                'score': bookmarks,
                'category': category,
                'description': description,
                'score_label': f'{bookmarks} users'
            }

        except Exception as e:
            logger.warning(f"Error parsing article element: {e}")
            return None

    def fetch_all(self) -> List[Dict[str, any]]:
        """
        Fetch both popular and new entries

        Returns:
            Combined list of all entries
        """
        all_entries = []

        # Fetch popular entries
        popular = self.fetch_popular()
        all_entries.extend(popular)

        # Small delay between requests
        time.sleep(1)

        # Fetch new entries
        new = self.fetch_new()
        all_entries.extend(new)

        # Remove duplicates based on URL
        seen_urls = set()
        unique_entries = []
        for entry in all_entries:
            if entry['url'] not in seen_urls:
                seen_urls.add(entry['url'])
                unique_entries.append(entry)

        logger.info(f"Total unique Hatena entries: {len(unique_entries)}")
        return unique_entries
