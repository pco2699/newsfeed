"""
Hatena Bookmark fetcher
Fetches popular and new entries from Hatena Bookmark using RSS feeds
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
import logging
import time

logger = logging.getLogger(__name__)


class HatenaFetcher:
    """Fetches articles from Hatena Bookmark via RSS feeds"""

    POPULAR_RSS_URL = "https://b.hatena.ne.jp/hotentry.rss"
    NEW_RSS_URL = "https://b.hatena.ne.jp/entrylist.rss"

    # XML namespaces used in Hatena RSS
    NAMESPACES = {
        'rss': 'http://purl.org/rss/1.0/',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'hatena': 'http://www.hatena.ne.jp/info/xmlns#'
    }

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
        Fetch popular entries from Hatena Bookmark RSS

        Returns:
            List of article dictionaries with title, url, bookmarks, etc.
        """
        logger.info(f"Fetching {self.popular_count} popular entries from Hatena RSS...")
        try:
            response = self.session.get(self.POPULAR_RSS_URL, timeout=10)
            response.raise_for_status()
            return self._parse_rss(response.content, limit=self.popular_count)
        except Exception as e:
            logger.error(f"Error fetching Hatena popular RSS: {e}")
            return []

    def fetch_new(self) -> List[Dict[str, any]]:
        """
        Fetch new entries from Hatena Bookmark RSS

        Returns:
            List of article dictionaries with title, url, bookmarks, etc.
        """
        logger.info(f"Fetching {self.new_count} new entries from Hatena RSS...")
        try:
            response = self.session.get(self.NEW_RSS_URL, timeout=10)
            response.raise_for_status()
            return self._parse_rss(response.content, limit=self.new_count)
        except Exception as e:
            logger.error(f"Error fetching Hatena new RSS: {e}")
            return []

    def _parse_rss(self, xml_content: bytes, limit: int) -> List[Dict[str, any]]:
        """
        Parse RSS XML and extract article information

        Args:
            xml_content: RSS XML content
            limit: Maximum number of entries to return

        Returns:
            List of parsed article dictionaries
        """
        try:
            root = ET.fromstring(xml_content)
            entries = []

            # Find all items in the RSS feed
            items = root.findall('.//rss:item', self.NAMESPACES)

            for item in items[:limit]:
                try:
                    entry = self._parse_rss_item(item)
                    if entry:
                        entries.append(entry)
                except Exception as e:
                    logger.warning(f"Error parsing RSS item: {e}")
                    continue

            logger.info(f"Successfully parsed {len(entries)} Hatena entries from RSS")
            return entries

        except Exception as e:
            logger.error(f"Error parsing RSS XML: {e}")
            return []

    def _parse_rss_item(self, item) -> Optional[Dict[str, any]]:
        """
        Parse individual RSS item element

        Args:
            item: ElementTree item element

        Returns:
            Dictionary with article data or None if parsing fails
        """
        try:
            ns = self.NAMESPACES

            # Get title (required)
            title_elem = item.find('rss:title', ns)
            if title_elem is None or not title_elem.text:
                return None
            title = title_elem.text

            # Get URL (required)
            link_elem = item.find('rss:link', ns)
            if link_elem is None or not link_elem.text:
                return None
            url = link_elem.text

            # Get bookmark count
            bookmarks = 0
            bookmark_elem = item.find('hatena:bookmarkcount', ns)
            if bookmark_elem is not None and bookmark_elem.text:
                try:
                    bookmarks = int(bookmark_elem.text)
                except ValueError:
                    bookmarks = 0

            # Get category (first subject tag)
            category = ''
            subject_elem = item.find('dc:subject', ns)
            if subject_elem is not None and subject_elem.text:
                category = subject_elem.text

            # Get description
            description = ''
            desc_elem = item.find('rss:description', ns)
            if desc_elem is not None and desc_elem.text:
                description = desc_elem.text

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
            logger.warning(f"Error parsing RSS item element: {e}")
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
