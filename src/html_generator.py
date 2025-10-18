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
        highlights = summary_data.get('highlights', [])
        categories = summary_data.get('categories', [])

        # Format date in Japanese
        weekday_ja = ['月', '火', '水', '木', '金', '土', '日']
        date_str = date.strftime('%Y年%m月%d日')
        weekday = weekday_ja[date.weekday()]
        formatted_date = f"{date_str}（{weekday}）"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M PST')

        # Calculate estimated reading time
        total_articles = len(highlights) + sum(len(cat.get('articles', [])) for cat in categories)
        reading_time = max(5, min(15, total_articles // 6))

        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>デイリーダイジェスト - {date.strftime('%Y-%m-%d')}</title>
    {self._get_css()}
</head>
<body>
    <header class="colorful-header">
        <h1>📰 デイリーダイジェスト</h1>
        <p class="date">{formatted_date}</p>
        <p class="meta">生成時刻: {timestamp} | 読書時間: 約{reading_time}分</p>
        <button class="dark-mode-toggle" onclick="toggleDarkMode()">🌓 ダークモード</button>
    </header>

    <nav class="icon-nav">
        <a href="#highlights">🔥 ハイライト</a>
        {self._generate_category_nav(categories)}
        <a href="archive.html">📚 アーカイブ</a>
    </nav>

    <main>
        <section id="highlights" class="category-section highlight">
            <h2>🔥 今日のハイライト</h2>
            <div class="article-grid">
                {self._generate_article_cards(highlights, is_highlight=True)}
            </div>
        </section>

        {self._generate_category_sections(categories)}
    </main>

    <footer>
        <p>📊 合計 {total_articles} 件の記事</p>
        <p>ソース: はてなブックマーク, Hacker News, Reddit</p>
        <p>AI要約: Claude Haiku 4.5 (Anthropic) | <a href="archive.html">📚 アーカイブを見る</a></p>
        <p class="disclaimer">このダイジェストはAIによって自動生成されています。</p>
    </footer>

    {self._get_javascript()}
</body>
</html>"""

        return html

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
            --bg-card: #ffffff;
            --text-primary: #212529;
            --text-secondary: #6c757d;
            --border-color: #dee2e6;
            --accent-blue: #0d6efd;
            --accent-green: #198754;
            --accent-orange: #fd7e14;
            --accent-purple: #6f42c1;
            --accent-red: #dc3545;
            --shadow: 0 2px 8px rgba(0,0,0,0.1);
            --shadow-hover: 0 4px 16px rgba(0,0,0,0.15);
        }

        body.dark-mode {
            --bg-primary: #1a1a1a;
            --bg-secondary: #2d2d2d;
            --bg-card: #2d2d2d;
            --text-primary: #e9ecef;
            --text-secondary: #adb5bd;
            --border-color: #495057;
            --shadow: 0 2px 8px rgba(0,0,0,0.3);
            --shadow-hover: 0 4px 16px rgba(0,0,0,0.4);
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
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }

        .category-section {
            margin-bottom: 3rem;
            animation: fadeIn 0.6s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .category-section h2 {
            font-size: 1.8rem;
            margin-bottom: 1.5rem;
            color: var(--text-primary);
            border-left: 5px solid var(--accent-blue);
            padding-left: 1rem;
        }

        .category-section.highlight h2 {
            border-left-color: var(--accent-red);
        }

        .article-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
        }

        .article-card {
            background: var(--bg-card);
            border: 2px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: var(--shadow);
            transition: all 0.3s;
            display: flex;
            flex-direction: column;
        }

        .article-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-hover);
            border-color: var(--accent-blue);
        }

        .article-card.highlight-card {
            border-color: var(--accent-orange);
            background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
        }

        .source-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
            color: white;
            width: fit-content;
        }

        .source-badge.hatena {
            background: linear-gradient(135deg, #00a4de 0%, #0086c3 100%);
        }

        .source-badge.hackernews {
            background: linear-gradient(135deg, #ff6600 0%, #ff4500 100%);
        }

        .source-badge.reddit {
            background: linear-gradient(135deg, #ff4500 0%, #ff3300 100%);
        }

        .source-badge.other {
            background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
        }

        .article-card h3 {
            font-size: 1.1rem;
            margin-bottom: 0.75rem;
            line-height: 1.4;
        }

        .article-card h3 a {
            color: var(--text-primary);
            text-decoration: none;
            transition: color 0.3s;
        }

        .article-card h3 a:hover {
            color: var(--accent-blue);
        }

        .summary {
            color: var(--text-secondary);
            font-size: 0.95rem;
            margin-bottom: 1rem;
            flex-grow: 1;
        }

        .card-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 0.75rem;
            border-top: 1px solid var(--border-color);
        }

        .score {
            color: var(--text-secondary);
            font-size: 0.85rem;
            font-weight: 600;
        }

        .read-more {
            color: var(--accent-blue);
            text-decoration: none;
            font-weight: 600;
            font-size: 0.85rem;
            transition: all 0.3s;
        }

        .read-more:hover {
            color: var(--accent-purple);
            transform: translateX(3px);
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

            .article-grid {
                grid-template-columns: 1fr;
            }

            .icon-nav {
                gap: 0.3rem;
                top: 136px;
            }

            .icon-nav a {
                font-size: 0.8rem;
                padding: 0.4rem 0.8rem;
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

        // Add animation on scroll
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

        document.querySelectorAll('.article-card').forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(card);
        });
    </script>"""
