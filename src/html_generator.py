"""
HTML Generator
Creates beautiful, colorful HTML pages with the digest content
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
import html as html_module

logger = logging.getLogger(__name__)


class HTMLGenerator:
    """Generates static HTML pages for the digest"""

    def __init__(self):
        """Initialize HTML generator"""
        pass

    def generate_digest_page(
        self,
        summary_data: Dict[str, Any],
        date: datetime,
        output_path: str
    ) -> None:
        """
        Generate the daily digest HTML page

        Args:
            summary_data: Summarized and categorized article data
            date: Date of the digest
            output_path: Path to save the HTML file
        """
        logger.info(f"Generating HTML digest for {date.strftime('%Y-%m-%d')}...")

        # Build HTML content
        html_content = self._build_html(summary_data, date)

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"HTML digest saved to {output_path}")

    def _build_html(self, summary_data: Dict[str, Any], date: datetime) -> str:
        """
        Build complete HTML document

        Args:
            summary_data: Summary data
            date: Digest date

        Returns:
            Complete HTML string
        """
        title = summary_data.get('title', '今日のテックニュースダイジェスト')
        overall_summary = summary_data.get('overall_summary', '')
        source_summaries = summary_data.get('source_summaries', [])
        key_topics = summary_data.get('key_topics', [])
        total_articles = summary_data.get('total_articles', 0)

        # Format date in Japanese
        weekday_ja = ['月', '火', '水', '木', '金', '土', '日']
        date_str = date.strftime('%Y年%m月%d日')
        weekday = weekday_ja[date.weekday()]
        formatted_date = f"{date_str}（{weekday}）"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M PST')

        # Calculate reading time based on total character count (Japanese: ~600 chars/min)
        total_chars = len(overall_summary) + sum(len(s.get('summary', '')) for s in source_summaries)
        reading_time = max(3, (total_chars // 600) + 1)

        # Convert markdown to HTML
        html_overall_summary = self._markdown_to_html(overall_summary)

        # Generate key topics badges
        topics_html = self._generate_topics_badges(key_topics)

        # Generate source sections
        source_sections_html = self._generate_source_sections(source_summaries)

        # Get list of sources
        sources_list = [s.get('source', '') for s in source_summaries]
        sources_html = ', '.join(sources_list) if sources_list else 'Various sources'

        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - {date.strftime('%Y-%m-%d')}</title>
    {self._get_css()}
</head>
<body>
    <header class="colorful-header">
        <h1>📰 {title}</h1>
        <p class="date">{formatted_date}</p>
        <p class="meta">生成時刻: {timestamp} | 読書時間: 約{reading_time}分</p>
        <button class="dark-mode-toggle" onclick="toggleDarkMode()">🌓 ダークモード</button>
    </header>

    <nav class="icon-nav">
        <a href="#overall">📝 全体サマリー</a>
        {self._generate_source_nav(source_summaries)}
        <a href="archive.html">📚 アーカイブ</a>
    </nav>

    <main>
        <section id="topics" class="topics-section">
            {topics_html}
        </section>

        <article id="overall" class="summary-article overall-summary">
            <h2 class="section-title">📝 今日の全体サマリー</h2>
            {html_overall_summary}
        </article>

        {source_sections_html}
    </main>

    <footer>
        <p>📊 分析記事数: {total_articles}件</p>
        <p>ソース: {sources_html}</p>
        <p>AI要約: Claude Haiku 4.5 (Anthropic) | <a href="archive.html">📚 アーカイブを見る</a></p>
        <p class="disclaimer">このダイジェストはAIによって自動生成されています。</p>
    </footer>

    {self._get_javascript()}
</body>
</html>"""

        return html

    def _markdown_to_html(self, markdown_text: str) -> str:
        """
        Convert simple markdown to HTML (links and paragraphs)

        Args:
            markdown_text: Markdown text

        Returns:
            HTML string
        """
        import re

        # Escape HTML first
        html_text = html_module.escape(markdown_text)

        # Convert markdown links [text](url) to HTML
        # We need to unescape the converted links
        html_text = re.sub(
            r'\[([^\]]+)\]\(([^\)]+)\)',
            r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>',
            html_text
        )

        # Convert double newlines to paragraphs
        paragraphs = html_text.split('\n\n')
        paragraphs = [f'<p>{p.strip()}</p>' for p in paragraphs if p.strip()]

        return '\n'.join(paragraphs)

    def _generate_topics_badges(self, topics: List[Dict[str, Any]]) -> str:
        """
        Generate HTML for topic badges

        Args:
            topics: List of topic dictionaries

        Returns:
            HTML string for topics
        """
        if not topics:
            return '<p class="no-topics">トピックなし</p>'

        badges = []
        for topic in topics:
            topic_name = html_module.escape(topic.get('topic', ''))
            icon = topic.get('icon', '📋')
            badges.append(f'<span class="topic-badge">{icon} {topic_name}</span>')

        return f'<div class="topics-badges">{"".join(badges)}</div>'

    def _generate_source_nav(self, source_summaries: List[Dict[str, Any]]) -> str:
        """
        Generate navigation links for source sections

        Args:
            source_summaries: List of source summary dictionaries

        Returns:
            HTML string for navigation
        """
        nav_items = []
        for source_summary in source_summaries:
            source = source_summary.get('source', '')
            icon = source_summary.get('icon', '📰')
            # Create slug for anchor
            slug = source.lower().replace(' ', '-')
            nav_items.append(f'<a href="#{slug}">{icon} {source}</a>')

        return '\n        '.join(nav_items)

    def _generate_source_sections(self, source_summaries: List[Dict[str, Any]]) -> str:
        """
        Generate HTML sections for each source

        Args:
            source_summaries: List of source summary dictionaries

        Returns:
            HTML string for source sections
        """
        sections = []

        for source_summary in source_summaries:
            source = source_summary.get('source', '')
            icon = source_summary.get('icon', '📰')
            summary = source_summary.get('summary', '')
            article_count = source_summary.get('article_count', 0)
            slug = source.lower().replace(' ', '-')

            # Convert markdown to HTML
            html_summary = self._markdown_to_html(summary)

            section = f"""
        <article id="{slug}" class="summary-article source-summary">
            <h2 class="section-title">{icon} {source} <span class="article-count">({article_count}件)</span></h2>
            {html_summary}
        </article>"""

            sections.append(section)

        return '\n'.join(sections)

    def _generate_category_nav(self, categories: List[Dict[str, Any]]) -> str:
        """Generate navigation links for categories"""
        nav_items = []
        for i, category in enumerate(categories):
            name = category.get('name', f'カテゴリ{i+1}')
            icon = category.get('icon', '📋')
            # Create slug for anchor
            slug = f"category-{i}"
            nav_items.append(f'<a href="#{slug}">{icon} {name}</a>')

        return '\n        '.join(nav_items)

    def _generate_category_sections(self, categories: List[Dict[str, Any]]) -> str:
        """Generate HTML for all category sections"""
        sections = []

        for i, category in enumerate(categories):
            name = category.get('name', f'カテゴリ{i+1}')
            icon = category.get('icon', '📋')
            articles = category.get('articles', [])
            slug = f"category-{i}"

            if not articles:
                continue

            section = f"""
        <section id="{slug}" class="category-section">
            <h2>{icon} {name}</h2>
            <div class="article-grid">
                {self._generate_article_cards(articles)}
            </div>
        </section>"""

            sections.append(section)

        return '\n'.join(sections)

    def _generate_article_cards(
        self,
        articles: List[Dict[str, Any]],
        is_highlight: bool = False
    ) -> str:
        """Generate HTML cards for articles"""
        cards = []

        for article in articles:
            title = html_module.escape(article.get('title', ''))
            summary = html_module.escape(article.get('summary', ''))
            source = article.get('source', '')
            url = article.get('url', '#')
            score = article.get('score', 0)
            score_label = html_module.escape(article.get('score_label', str(score)))

            # Determine source badge class
            source_class = self._get_source_class(source)

            card_class = 'article-card highlight-card' if is_highlight else 'article-card'

            card = f"""
                <article class="{card_class}">
                    <span class="source-badge {source_class}">{source}</span>
                    <h3><a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a></h3>
                    <p class="summary">{summary}</p>
                    <div class="card-meta">
                        <span class="score">⭐ {score_label}</span>
                        <a href="{url}" class="read-more" target="_blank" rel="noopener noreferrer">続きを読む →</a>
                    </div>
                </article>"""

            cards.append(card)

        return '\n                '.join(cards)

    def _get_source_class(self, source: str) -> str:
        """Get CSS class for source badge"""
        source_map = {
            'はてブ': 'hatena',
            'Hacker News': 'hackernews',
            'Reddit': 'reddit'
        }
        return source_map.get(source, 'other')

    def _get_css(self) -> str:
        """Get embedded CSS styles"""
        return """    <style>
        :root {
            --bg-primary: #ffffff;
            --bg-secondary: #f8f9fa;
            --bg-article: #ffffff;
            --text-primary: #212529;
            --text-secondary: #6c757d;
            --text-link: #0d6efd;
            --text-link-hover: #0a58ca;
            --border-color: #dee2e6;
            --accent-blue: #0d6efd;
            --accent-purple: #6f42c1;
            --shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        body.dark-mode {
            --bg-primary: #1a1a1a;
            --bg-secondary: #2d2d2d;
            --bg-article: #252525;
            --text-primary: #e9ecef;
            --text-secondary: #adb5bd;
            --text-link: #4dabf7;
            --text-link-hover: #74c0fc;
            --border-color: #495057;
            --shadow: 0 2px 8px rgba(0,0,0,0.3);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Hiragino Sans", "Hiragino Kaku Gothic ProN", "Yu Gothic", YuGothic, Meiryo, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.7;
            font-size: 16px;
            transition: background-color 0.3s, color 0.3s;
        }

        .colorful-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 1rem;
            text-align: center;
            box-shadow: var(--shadow);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .colorful-header h1 {
            font-size: 2rem;
            margin-bottom: 0.5rem;
            font-weight: 700;
        }

        .colorful-header .date {
            font-size: 1.2rem;
            margin-bottom: 0.3rem;
            opacity: 0.95;
        }

        .colorful-header .meta {
            font-size: 0.9rem;
            opacity: 0.85;
        }

        .dark-mode-toggle {
            margin-top: 1rem;
            padding: 0.5rem 1rem;
            background: rgba(255,255,255,0.2);
            border: 2px solid rgba(255,255,255,0.3);
            color: white;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.3s;
        }

        .dark-mode-toggle:hover {
            background: rgba(255,255,255,0.3);
            transform: scale(1.05);
        }

        .icon-nav {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 0.5rem;
            padding: 1rem;
            background: var(--bg-secondary);
            border-bottom: 2px solid var(--border-color);
            position: sticky;
            top: 152px;
            z-index: 99;
        }

        .icon-nav a {
            padding: 0.5rem 1rem;
            background: var(--bg-card);
            color: var(--text-primary);
            text-decoration: none;
            border-radius: 20px;
            border: 2px solid var(--border-color);
            transition: all 0.3s;
            font-size: 0.9rem;
            font-weight: 500;
        }

        .icon-nav a:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow);
            border-color: var(--accent-blue);
        }

        main {
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .topics-section {
            margin-bottom: 2rem;
            animation: fadeIn 0.6s ease-in;
        }

        .topics-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            justify-content: center;
        }

        .topic-badge {
            display: inline-block;
            padding: 0.5rem 1rem;
            background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
            color: white;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            box-shadow: var(--shadow);
            transition: transform 0.3s;
        }

        .topic-badge:hover {
            transform: translateY(-2px);
        }

        .summary-article {
            background: var(--bg-article);
            border-radius: 12px;
            padding: 3rem 2.5rem;
            box-shadow: var(--shadow);
            animation: fadeIn 0.8s ease-in;
            line-height: 2;
            font-size: 1.05rem;
            margin-bottom: 2rem;
        }

        .summary-article.overall-summary {
            border-left: 4px solid var(--accent-purple);
        }

        .summary-article.source-summary {
            border-left: 4px solid var(--accent-blue);
        }

        .section-title {
            color: var(--text-primary);
            font-size: 1.5rem;
            margin-bottom: 1.5rem;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid var(--border-color);
        }

        .article-count {
            font-size: 1rem;
            color: var(--text-secondary);
            font-weight: normal;
        }

        .summary-article p {
            margin-bottom: 1.5rem;
            color: var(--text-primary);
            text-align: justify;
        }

        .summary-article p:last-child {
            margin-bottom: 0;
        }

        .summary-article a {
            color: var(--text-link);
            text-decoration: none;
            border-bottom: 1px solid var(--text-link);
            transition: all 0.3s;
            font-weight: 500;
        }

        .summary-article a:hover {
            color: var(--text-link-hover);
            border-bottom-color: var(--text-link-hover);
            background: rgba(13, 110, 253, 0.05);
        }

        body.dark-mode .summary-article a:hover {
            background: rgba(77, 171, 247, 0.1);
        }

        footer {
            background: var(--bg-secondary);
            border-top: 2px solid var(--border-color);
            padding: 2rem 1rem;
            text-align: center;
            color: var(--text-secondary);
            font-size: 0.9rem;
        }

        footer p {
            margin-bottom: 0.5rem;
        }

        footer a {
            color: var(--accent-blue);
            text-decoration: none;
        }

        footer a:hover {
            text-decoration: underline;
        }

        .disclaimer {
            font-size: 0.8rem;
            margin-top: 1rem;
            opacity: 0.7;
        }

        @media (max-width: 768px) {
            .colorful-header h1 {
                font-size: 1.5rem;
            }

            .summary-article {
                padding: 2rem 1.5rem;
                font-size: 1rem;
                line-height: 1.8;
            }

            .icon-nav {
                gap: 0.3rem;
                top: 136px;
            }

            .icon-nav a {
                font-size: 0.8rem;
                padding: 0.4rem 0.8rem;
            }

            main {
                padding: 1rem 0.5rem;
            }
        }
    </style>"""

    def _get_javascript(self) -> str:
        """Get embedded JavaScript"""
        return """    <script>
        // Dark mode toggle
        function toggleDarkMode() {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDark ? 'enabled' : 'disabled');
        }

        // Load dark mode preference
        if (localStorage.getItem('darkMode') === 'enabled') {
            document.body.classList.add('dark-mode');
        }

        // Smooth scroll for navigation
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    const offset = 170; // Account for sticky header
                    const targetPosition = target.offsetTop - offset;
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            });
        });

        // Add fade-in animation on scroll for summary articles
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);

        document.querySelectorAll('.summary-article').forEach(article => {
            article.style.opacity = '0';
            article.style.transform = 'translateY(20px)';
            article.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
            observer.observe(article);
        });
    </script>"""
