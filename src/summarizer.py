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
        return f"""あなたは日本語でニュースダイジェストを作成するAIアシスタントです。以下の{count}件の記事を分析し、今日のテック業界の動向について約1000文字の日本語の要約記事を作成してください。

**重要な指示:**
1. **文章形式**: 箇条書きではなく、読みやすい段落形式の文章で書いてください
2. **構成**:
   - 冒頭に全体的なトレンドや注目点を述べる（2-3段落）
   - 主要なトピックごとに段落を分けて詳しく解説（5-7段落）
   - 締めくくりに今日の重要ポイントをまとめる（1-2段落）
3. **リンクの挿入**: 記事に言及する際は、必ず元記事へのリンクを埋め込んでください
   - 例: 「[Reactの新機能](https://example.com)が発表され...」
   - 各段落で関連する記事へのリンクを自然に含めてください
4. **英語コンテンツの翻訳**: 英語の記事タイトルや内容は自然な日本語に翻訳してください
5. **中立的なトーン**: 客観的で情報的なトーンを保ち、分析的な視点を加えてください
6. **トピックの関連付け**: 複数の記事に共通するテーマやトレンドがあれば、それらを関連付けて説明してください
7. **文字数**: 約1000文字（900-1200文字程度）を目安にしてください

**出力形式:**
JSON形式で以下の構造で出力してください:

```json
{{
  "summary": "Markdown形式の要約記事（約1000文字、リンク付き）",
  "title": "今日のダイジェストのタイトル（20文字以内）",
  "key_topics": [
    {{
      "topic": "トピック名",
      "icon": "適切な絵文字"
    }}
  ],
  "article_count": {count},
  "sources_used": ["使用したソース名のリスト"]
}}
```

**記事リスト:**
{article_list}

必ずJSON形式で出力してください。summaryフィールドには、記事へのリンクを含む約1000文字の日本語の要約記事を書いてください。"""

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

            # Validate structure for new format
            if 'summary' not in result:
                logger.warning("Missing 'summary' field in response")
                return self._create_fallback_summary(original_articles)

            if 'title' not in result:
                result['title'] = '今日のテックニュースダイジェスト'

            if 'key_topics' not in result:
                result['key_topics'] = []

            if 'article_count' not in result:
                result['article_count'] = len(original_articles)

            if 'sources_used' not in result:
                result['sources_used'] = list(set(a.get('source', '') for a in original_articles))

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

        # Create a simple summary with links
        summary_parts = ["今日のテックニュースをお届けします。\n\n"]

        for i, article in enumerate(sorted_articles[:15], 1):
            title = article.get('title', '')
            url = article.get('url', '')
            source = article.get('source', '')
            summary_parts.append(f"{i}. [{title}]({url}) ({source})\n\n")

        summary_text = "".join(summary_parts)

        # Get unique sources
        sources = list(set(a.get('source', '') for a in articles))

        return {
            'summary': summary_text,
            'title': '今日のテックニュースダイジェスト',
            'key_topics': [
                {'topic': 'テクノロジー', 'icon': '💻'},
                {'topic': 'ニュース', 'icon': '📰'}
            ],
            'article_count': len(articles),
            'sources_used': sources
        }

    def _get_source_icon(self, source: str) -> str:
        """Get icon emoji for source"""
        icons = {
            'はてブ': '📑',
            'Hacker News': '🔶',
            'Reddit': '🤖'
        }
        return icons.get(source, '📰')
