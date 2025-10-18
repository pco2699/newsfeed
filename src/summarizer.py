"""
AI Summarizer using Claude Haiku 4.5
Categorizes and summarizes articles in Japanese
"""

import anthropic
import os
import logging
from typing import List, Dict, Any
import json

logger = logging.getLogger(__name__)


class AISummarizer:
    """Summarizes and categorizes articles using Claude AI"""

    def __init__(
        self,
        model: str = "claude-haiku-4-20250110",
        max_tokens: int = 4000,
        temperature: float = 0.3
    ):
        """
        Initialize AI summarizer

        Args:
            model: Claude model to use
            max_tokens: Maximum tokens for response
            temperature: Temperature for generation
        """
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

        # Initialize Anthropic client
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = anthropic.Anthropic(api_key=api_key)
        logger.info(f"AI Summarizer initialized with model: {model}")

    def summarize_articles(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Summarize and categorize articles

        Args:
            articles: List of article dictionaries from all sources

        Returns:
            Dictionary with categorized summaries and highlights
        """
        logger.info(f"Summarizing {len(articles)} articles...")

        # Prepare article data for the prompt
        article_list = self._format_articles_for_prompt(articles)

        # Create the prompt
        prompt = self._create_summary_prompt(article_list, len(articles))

        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Parse the response
            summary_text = response.content[0].text
            result = self._parse_summary_response(summary_text, articles)

            logger.info(f"Successfully generated summary with {len(result.get('categories', []))} categories")
            return result

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            # Return a basic fallback structure
            return self._create_fallback_summary(articles)

    def _format_articles_for_prompt(self, articles: List[Dict[str, Any]]) -> str:
        """
        Format articles for the AI prompt

        Args:
            articles: List of article dictionaries

        Returns:
            Formatted string of articles
        """
        lines = []
        for i, article in enumerate(articles, 1):
            source = article.get('source', 'Unknown')
            title = article.get('title', 'No title')
            url = article.get('url', '')
            score = article.get('score', 0)
            score_label = article.get('score_label', f'{score}')

            lines.append(f"{i}. [{source}] {title} ({score_label}) - {url}")

        return "\n".join(lines)

    def _create_summary_prompt(self, article_list: str, count: int) -> str:
        """
        Create the prompt for Claude

        Args:
            article_list: Formatted article list
            count: Number of articles

        Returns:
            Complete prompt string
        """
        return f"""あなたは日本語でニュースダイジェストを作成するAIアシスタントです。以下の{count}件の記事を分析し、トピックごとに分類して、日本語で簡潔に要約してください。

**重要な指示:**
1. **カテゴリの自動決定**: 記事の内容に基づいて、適切な日本語のカテゴリ名を自動的に作成してください（例: テクノロジー、AI・機械学習、プログラミング、セキュリティ、ビジネス、サイエンス、など）
2. **簡潔な要約**: 各記事は1-2文で簡潔に要約してください
3. **中立的なトーン**: 客観的で情報的なトーンを保ってください
4. **英語コンテンツの翻訳**: 英語の記事は自然な日本語に翻訳してください
5. **ソースの明記**: 各記事のソース（はてブ、Hacker News、Reddit）を含めてください
6. **ハイライト**: 最も重要/人気のある5-10件の記事を「ハイライト」として選んでください
7. **コメントは含めない**: 記事の内容のみに焦点を当ててください

**出力形式:**
JSON形式で以下の構造で出力してください:

```json
{{
  "highlights": [
    {{
      "title": "日本語のタイトル",
      "summary": "1-2文の要約",
      "source": "ソース名",
      "url": "元のURL",
      "score": スコア,
      "score_label": "スコアラベル",
      "category": "カテゴリ名"
    }}
  ],
  "categories": [
    {{
      "name": "カテゴリ名（日本語）",
      "icon": "適切な絵文字",
      "articles": [
        {{
          "title": "日本語のタイトル",
          "summary": "1-2文の要約",
          "source": "ソース名",
          "url": "元のURL",
          "score": スコア,
          "score_label": "スコアラベル"
        }}
      ]
    }}
  ]
}}
```

**記事リスト:**
{article_list}

必ずJSON形式で出力してください。"""

    def _parse_summary_response(
        self,
        response_text: str,
        original_articles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Parse Claude's response into structured data

        Args:
            response_text: Response from Claude
            original_articles: Original article data

        Returns:
            Structured summary dictionary
        """
        try:
            # Try to extract JSON from response
            # Claude might wrap JSON in markdown code blocks
            response_text = response_text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            # Parse JSON
            result = json.loads(response_text)

            # Validate structure
            if 'highlights' not in result:
                result['highlights'] = []
            if 'categories' not in result:
                result['categories'] = []

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {e}")
            logger.debug(f"Response text: {response_text[:500]}")
            return self._create_fallback_summary(original_articles)

    def _create_fallback_summary(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a basic fallback summary if AI fails

        Args:
            articles: Original articles

        Returns:
            Basic summary structure
        """
        logger.warning("Creating fallback summary")

        # Sort by score
        sorted_articles = sorted(articles, key=lambda x: x.get('score', 0), reverse=True)

        # Create highlights from top articles
        highlights = []
        for article in sorted_articles[:10]:
            highlights.append({
                'title': article.get('title', ''),
                'summary': article.get('description', article.get('title', ''))[:200],
                'source': article.get('source', ''),
                'url': article.get('url', ''),
                'score': article.get('score', 0),
                'score_label': article.get('score_label', ''),
                'category': 'その他'
            })

        # Group by source as categories
        categories = {}
        for article in sorted_articles:
            source = article.get('source', 'その他')
            if source not in categories:
                categories[source] = {
                    'name': source,
                    'icon': self._get_source_icon(source),
                    'articles': []
                }

            categories[source]['articles'].append({
                'title': article.get('title', ''),
                'summary': article.get('description', article.get('title', ''))[:200],
                'source': source,
                'url': article.get('url', ''),
                'score': article.get('score', 0),
                'score_label': article.get('score_label', '')
            })

        return {
            'highlights': highlights,
            'categories': list(categories.values())
        }

    def _get_source_icon(self, source: str) -> str:
        """Get icon emoji for source"""
        icons = {
            'はてブ': '📑',
            'Hacker News': '🔶',
            'Reddit': '🤖'
        }
        return icons.get(source, '📰')
