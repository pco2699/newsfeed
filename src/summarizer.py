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
        return f"""あなたは日本語でニュースダイジェストを作成するAIアシスタントです。以下の{count}件の記事を分析し、ソース別（はてブ、Hacker News、Reddit）に分けて要約記事を作成してください。

**重要な指示:**
1. **ソース別に分割**: はてブ、Hacker News、Redditの3つのセクションに分けて要約を作成してください
2. **各セクションの構成**:
   - 各ソースごとに300-500文字程度の段落形式の要約
   - そのソースの主要なトピックやトレンドを説明
   - 記事へのリンクを自然に埋め込む（例: 「[記事タイトル](URL)では...」）
3. **全体サマリー**: 冒頭に全ソースを通しての今日の注目点を2-3段落（200-300文字）で記述
4. **英語コンテンツの翻訳**: 英語の記事タイトルや内容は自然な日本語に翻訳してください
5. **中立的なトーン**: 客観的で情報的なトーンを保ち、分析的な視点を加えてください
6. **リンクの挿入**: Markdown形式 `[タイトル](URL)` で必ず記事リンクを含めてください

**出力形式:**
JSON形式で以下の構造で出力してください:

```json
{{
  "title": "今日のダイジェストのタイトル（20文字以内）",
  "overall_summary": "全体的な今日のトレンドや注目点（200-300文字、Markdown形式）",
  "source_summaries": [
    {{
      "source": "はてブ",
      "icon": "📑",
      "summary": "はてブからの記事の要約（300-500文字、リンク付きMarkdown形式）",
      "article_count": 記事数
    }},
    {{
      "source": "Hacker News",
      "icon": "🔶",
      "summary": "Hacker Newsからの記事の要約（300-500文字、リンク付きMarkdown形式）",
      "article_count": 記事数
    }},
    {{
      "source": "Reddit",
      "icon": "🤖",
      "summary": "Redditからの記事の要約（300-500文字、リンク付きMarkdown形式）",
      "article_count": 記事数
    }}
  ],
  "key_topics": [
    {{
      "topic": "トピック名",
      "icon": "適切な絵文字"
    }}
  ],
  "total_articles": {count}
}}
```

**記事リスト:**
{article_list}

必ずJSON形式で出力してください。各ソースのsummaryフィールドには、記事へのリンクを含む段落形式の日本語要約を書いてください。"""

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
            if 'overall_summary' not in result or 'source_summaries' not in result:
                logger.warning("Missing required fields in response")
                return self._create_fallback_summary(original_articles)

            if 'title' not in result:
                result['title'] = '今日のテックニュースダイジェスト'

            if 'key_topics' not in result:
                result['key_topics'] = []

            if 'total_articles' not in result:
                result['total_articles'] = len(original_articles)

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

        # Group by source
        by_source = {}
        for article in sorted_articles:
            source = article.get('source', 'その他')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(article)

        # Create overall summary
        overall_summary = f"今日は全体で{len(articles)}件の記事を収集しました。\n\n主なトピックは、テクノロジー、AI、プログラミングなどです。"

        # Create source summaries
        source_summaries = []
        source_icons = {
            'はてブ': '📑',
            'Hacker News': '🔶',
            'Reddit': '🤖'
        }

        for source, source_articles in by_source.items():
            summary_parts = []
            for i, article in enumerate(source_articles[:10], 1):
                title = article.get('title', '')
                url = article.get('url', '')
                summary_parts.append(f"[{title}]({url})")
                if i < len(source_articles[:10]):
                    summary_parts.append("、")

            summary_text = f"{source}からは{len(source_articles)}件の記事があります。主な記事: " + "".join(summary_parts)

            source_summaries.append({
                'source': source,
                'icon': source_icons.get(source, '📰'),
                'summary': summary_text,
                'article_count': len(source_articles)
            })

        return {
            'title': '今日のテックニュースダイジェスト',
            'overall_summary': overall_summary,
            'source_summaries': source_summaries,
            'key_topics': [
                {'topic': 'テクノロジー', 'icon': '💻'},
                {'topic': 'ニュース', 'icon': '📰'}
            ],
            'total_articles': len(articles)
        }

    def _get_source_icon(self, source: str) -> str:
        """Get icon emoji for source"""
        icons = {
            'はてブ': '📑',
            'Hacker News': '🔶',
            'Reddit': '🤖'
        }
        return icons.get(source, '📰')
