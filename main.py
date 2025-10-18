#!/usr/bin/env python3
"""
Daily News Digest Generator - Main Entry Point
Orchestrates the entire digest generation process
"""

import os
import sys
import logging
import yaml
import time
from datetime import datetime
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fetchers import HatenaFetcher, HackerNewsFetcher, RedditFetcher
from summarizer import AISummarizer
from html_generator import HTMLGenerator
from archive_manager import ArchiveManager


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('digest_generation.log')
    ]
)
logger = logging.getLogger(__name__)


class DigestGenerator:
    """Main orchestrator for digest generation"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize digest generator

        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.max_retries = 3
        self.retry_delay = 5  # seconds

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise

    def fetch_articles_with_retry(self) -> List[Dict[str, Any]]:
        """
        Fetch articles from all sources with retry logic

        Returns:
            Combined list of articles from all sources
        """
        all_articles = []

        # Fetch from Hatena Bookmark
        if self.config['sources']['hatena']['enabled']:
            articles = self._retry_operation(
                self._fetch_hatena,
                "Hatena Bookmark"
            )
            all_articles.extend(articles)

        # Fetch from Hacker News
        if self.config['sources']['hackernews']['enabled']:
            articles = self._retry_operation(
                self._fetch_hackernews,
                "Hacker News"
            )
            all_articles.extend(articles)

        # Fetch from Reddit
        if self.config['sources']['reddit']['enabled']:
            articles = self._retry_operation(
                self._fetch_reddit,
                "Reddit"
            )
            all_articles.extend(articles)

        logger.info(f"Total articles fetched: {len(all_articles)}")
        return all_articles

    def _fetch_hatena(self) -> List[Dict[str, Any]]:
        """Fetch articles from Hatena Bookmark"""
        fetcher = HatenaFetcher(
            popular_count=self.config['sources']['hatena']['popular_count'],
            new_count=self.config['sources']['hatena']['new_count']
        )
        return fetcher.fetch_all()

    def _fetch_hackernews(self) -> List[Dict[str, Any]]:
        """Fetch articles from Hacker News"""
        fetcher = HackerNewsFetcher(
            story_count=self.config['sources']['hackernews']['story_count']
        )
        return fetcher.fetch_all()

    def _fetch_reddit(self) -> List[Dict[str, Any]]:
        """Fetch articles from Reddit"""
        fetcher = RedditFetcher(
            post_count=self.config['sources']['reddit']['post_count'],
            use_personal_feed=self.config['sources']['reddit']['use_personal_feed']
        )
        return fetcher.fetch_all()

    def _retry_operation(self, operation, operation_name: str) -> List[Dict[str, Any]]:
        """
        Retry an operation with exponential backoff

        Args:
            operation: Function to execute
            operation_name: Name for logging

        Returns:
            Result from operation or empty list on failure
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Attempting {operation_name} (attempt {attempt}/{self.max_retries})")
                result = operation()
                logger.info(f"{operation_name} succeeded")
                return result
            except Exception as e:
                logger.error(f"{operation_name} failed (attempt {attempt}/{self.max_retries}): {e}")
                if attempt < self.max_retries:
                    delay = self.retry_delay * (2 ** (attempt - 1))  # Exponential backoff
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"{operation_name} failed after {self.max_retries} attempts")

        return []

    def summarize_with_ai(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Summarize articles with AI, with retry logic

        Args:
            articles: List of articles to summarize

        Returns:
            Summary data
        """
        def _summarize():
            summarizer = AISummarizer(
                model=self.config['ai']['model'],
                max_tokens=self.config['ai']['max_tokens'],
                temperature=self.config['ai']['temperature']
            )
            return summarizer.summarize_articles(articles)

        result = self._retry_operation(_summarize, "AI Summarization")

        # If retry failed, create fallback
        if not result:
            logger.warning("Creating fallback summary after AI failure")
            summarizer = AISummarizer()
            result = summarizer._create_fallback_summary(articles)

        return result

    def generate_html(
        self,
        summary_data: Dict[str, Any],
        date: datetime,
        output_path: str
    ) -> str:
        """
        Generate HTML digest

        Args:
            summary_data: Summarized article data
            date: Date of digest
            output_path: Path to save HTML

        Returns:
            Generated HTML content
        """
        logger.info("Generating HTML digest...")
        generator = HTMLGenerator()
        generator.generate_digest_page(summary_data, date, output_path)

        # Read generated content
        with open(output_path, 'r', encoding='utf-8') as f:
            return f.read()

    def update_archives(self, html_content: str, date: datetime) -> None:
        """
        Update archive system

        Args:
            html_content: HTML content to archive
            date: Date of digest
        """
        logger.info("Updating archives...")
        manager = ArchiveManager(
            archive_dir=self.config.get('archive', {}).get('dir', 'archive'),
            keep_days=self.config['archive']['keep_days']
        )

        # Save to archive
        manager.save_to_archive(html_content, date)

        # Cleanup old archives
        manager.cleanup_old_archives()

        # Generate archive index
        if self.config['archive']['generate_index']:
            manager.generate_archive_index()

    def generate(self) -> bool:
        """
        Main generation process

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("=" * 60)
            logger.info("Starting Daily Digest Generation")
            logger.info("=" * 60)

            start_time = time.time()
            date = datetime.now()

            # Step 1: Fetch articles
            logger.info("\n[1/4] Fetching articles from sources...")
            articles = self.fetch_articles_with_retry()

            if not articles:
                logger.error("No articles fetched. Aborting.")
                return False

            # Step 2: Summarize with AI
            logger.info(f"\n[2/4] Summarizing {len(articles)} articles with AI...")
            summary_data = self.summarize_with_ai(articles)

            # Step 3: Generate HTML
            logger.info("\n[3/4] Generating HTML digest...")
            html_content = self.generate_html(summary_data, date, "index.html")

            # Step 4: Update archives
            logger.info("\n[4/4] Updating archives...")
            self.update_archives(html_content, date)

            # Success
            elapsed = time.time() - start_time
            logger.info("\n" + "=" * 60)
            logger.info(f"✅ Digest generation completed successfully!")
            logger.info(f"⏱️  Time elapsed: {elapsed:.2f} seconds")
            logger.info(f"📊 Articles processed: {len(articles)}")
            logger.info(f"📝 Output: index.html")
            logger.info("=" * 60)

            return True

        except Exception as e:
            logger.error(f"Fatal error during digest generation: {e}", exc_info=True)
            return False


def main():
    """Main entry point"""
    try:
        # Check for required environment variables
        required_vars = ['ANTHROPIC_API_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            logger.error("Please set them before running the script.")
            sys.exit(1)

        # Check for optional Reddit credentials
        reddit_vars = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'REDDIT_USERNAME', 'REDDIT_PASSWORD']
        missing_reddit = [var for var in reddit_vars if not os.getenv(var)]

        if missing_reddit:
            logger.warning(f"Missing Reddit credentials: {', '.join(missing_reddit)}")
            logger.warning("Reddit fetching will be skipped unless credentials are provided.")

        # Generate digest
        generator = DigestGenerator()
        success = generator.generate()

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        logger.info("\nGeneration interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
