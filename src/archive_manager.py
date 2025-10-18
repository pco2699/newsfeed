"""
Archive Manager
Manages digest archives and generates archive index page
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict
import glob

logger = logging.getLogger(__name__)


class ArchiveManager:
    """Manages archive of past digests"""

    def __init__(self, archive_dir: str = "archive", keep_days: int = 90):
        """
        Initialize archive manager

        Args:
            archive_dir: Directory to store archives
            keep_days: Number of days to keep archives
        """
        self.archive_dir = archive_dir
        self.keep_days = keep_days

        # Create archive directory if it doesn't exist
        os.makedirs(archive_dir, exist_ok=True)

    def save_to_archive(self, html_content: str, date: datetime) -> str:
        """
        Save digest HTML to archive

        Args:
            html_content: HTML content to save
            date: Date of the digest

        Returns:
            Path to the archived file
        """
        filename = f"{date.strftime('%Y-%m-%d')}.html"
        filepath = os.path.join(self.archive_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"Saved digest to archive: {filepath}")
        return filepath

    def cleanup_old_archives(self) -> None:
        """Remove archives older than keep_days"""
        cutoff_date = datetime.now() - timedelta(days=self.keep_days)
        logger.info(f"Cleaning up archives older than {cutoff_date.strftime('%Y-%m-%d')}")

        pattern = os.path.join(self.archive_dir, "*.html")
        removed_count = 0

        for filepath in glob.glob(pattern):
            filename = os.path.basename(filepath)

            # Skip if not a date-formatted file
            if not filename.startswith('20'):  # Simple check for year 20XX
                continue

            try:
                # Extract date from filename (YYYY-MM-DD.html)
                date_str = filename.replace('.html', '')
                file_date = datetime.strptime(date_str, '%Y-%m-%d')

                if file_date < cutoff_date:
                    os.remove(filepath)
                    removed_count += 1
                    logger.info(f"Removed old archive: {filepath}")

            except (ValueError, OSError) as e:
                logger.warning(f"Error processing archive file {filepath}: {e}")

        logger.info(f"Cleanup complete. Removed {removed_count} old archives")

    def get_archive_list(self) -> List[Dict[str, str]]:
        """
        Get list of all archives

        Returns:
            List of dictionaries with archive information
        """
        pattern = os.path.join(self.archive_dir, "*.html")
        archives = []

        for filepath in glob.glob(pattern):
            filename = os.path.basename(filepath)

            # Skip if not a date-formatted file
            if not filename.startswith('20'):
                continue

            try:
                # Extract date from filename
                date_str = filename.replace('.html', '')
                file_date = datetime.strptime(date_str, '%Y-%m-%d')

                # Get file size
                file_size = os.path.getsize(filepath)
                size_kb = file_size / 1024

                archives.append({
                    'date': file_date,
                    'date_str': date_str,
                    'filename': filename,
                    'filepath': filepath,
                    'size_kb': round(size_kb, 1)
                })

            except (ValueError, OSError) as e:
                logger.warning(f"Error processing archive file {filepath}: {e}")

        # Sort by date, most recent first
        archives.sort(key=lambda x: x['date'], reverse=True)
        return archives

    def generate_archive_index(self, output_path: str = "archive.html") -> None:
        """
        Generate archive index HTML page

        Args:
            output_path: Path to save the archive index
        """
        logger.info("Generating archive index page...")

        archives = self.get_archive_list()

        # Build HTML
        html = self._build_archive_html(archives)

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        logger.info(f"Archive index saved to {output_path}")

    def _build_archive_html(self, archives: List[Dict[str, str]]) -> str:
        """
        Build archive index HTML

        Args:
            archives: List of archive information

        Returns:
            Complete HTML string
        """
        # Group archives by month
        archives_by_month = {}
        for archive in archives:
            month_key = archive['date'].strftime('%Y年%m月')
            if month_key not in archives_by_month:
                archives_by_month[month_key] = []
            archives_by_month[month_key].append(archive)

        # Generate archive items HTML
        archive_sections = []
        for month, month_archives in archives_by_month.items():
            items = []
            for archive in month_archives:
                date = archive['date']
                weekday_ja = ['月', '火', '水', '木', '金', '土', '日']
                weekday = weekday_ja[date.weekday()]
                date_display = f"{date.strftime('%m月%d日')}（{weekday}）"

                item = f"""
                    <div class="archive-item">
                        <a href="{self.archive_dir}/{archive['filename']}">
                            <div class="archive-date">
                                <span class="day">{date.day}</span>
                                <span class="month">{date.strftime('%m月')}</span>
                            </div>
                            <div class="archive-info">
                                <h3>{archive['date_str']} ({weekday})</h3>
                                <p class="archive-meta">{archive['size_kb']} KB</p>
                            </div>
                        </a>
                    </div>"""
                items.append(item)

            section = f"""
        <section class="month-section">
            <h2>📅 {month}</h2>
            <div class="archive-grid">
                {''.join(items)}
            </div>
        </section>"""
            archive_sections.append(section)

        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>アーカイブ - デイリーダイジェスト</title>
    {self._get_archive_css()}
</head>
<body>
    <header class="colorful-header">
        <h1>📚 アーカイブ</h1>
        <p class="subtitle">過去のデイリーダイジェスト</p>
        <a href="index.html" class="back-link">← 今日のダイジェストに戻る</a>
    </header>

    <main>
        <div class="archive-stats">
            <div class="stat-card">
                <span class="stat-number">{len(archives)}</span>
                <span class="stat-label">件のダイジェスト</span>
            </div>
            <div class="stat-card">
                <span class="stat-number">{self.keep_days}</span>
                <span class="stat-label">日間保存</span>
            </div>
        </div>

        {''.join(archive_sections)}
    </main>

    <footer>
        <p><a href="index.html">今日のダイジェストに戻る</a></p>
        <p class="disclaimer">アーカイブは{self.keep_days}日間保存されます。</p>
    </footer>

    {self._get_archive_javascript()}
</body>
</html>"""

        return html

    def _get_archive_css(self) -> str:
        """Get CSS for archive page"""
        return """    <style>
        :root {
            --bg-primary: #ffffff;
            --bg-secondary: #f8f9fa;
            --bg-card: #ffffff;
            --text-primary: #212529;
            --text-secondary: #6c757d;
            --border-color: #dee2e6;
            --accent-blue: #0d6efd;
            --accent-purple: #6f42c1;
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
            transition: background-color 0.3s, color 0.3s;
        }

        .colorful-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 1rem;
            text-align: center;
            box-shadow: var(--shadow);
        }

        .colorful-header h1 {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }

        .subtitle {
            font-size: 1.1rem;
            margin-bottom: 1rem;
            opacity: 0.9;
        }

        .back-link {
            display: inline-block;
            margin-top: 1rem;
            padding: 0.5rem 1rem;
            background: rgba(255,255,255,0.2);
            color: white;
            text-decoration: none;
            border-radius: 20px;
            border: 2px solid rgba(255,255,255,0.3);
            transition: all 0.3s;
        }

        .back-link:hover {
            background: rgba(255,255,255,0.3);
            transform: scale(1.05);
        }

        main {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }

        .archive-stats {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-bottom: 3rem;
        }

        .stat-card {
            background: var(--bg-card);
            border: 2px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem 2rem;
            text-align: center;
            box-shadow: var(--shadow);
            display: flex;
            flex-direction: column;
        }

        .stat-number {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--accent-blue);
        }

        .stat-label {
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin-top: 0.5rem;
        }

        .month-section {
            margin-bottom: 3rem;
        }

        .month-section h2 {
            font-size: 1.5rem;
            margin-bottom: 1.5rem;
            color: var(--text-primary);
            border-left: 5px solid var(--accent-purple);
            padding-left: 1rem;
        }

        .archive-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1rem;
        }

        .archive-item {
            background: var(--bg-card);
            border: 2px solid var(--border-color);
            border-radius: 12px;
            overflow: hidden;
            transition: all 0.3s;
            box-shadow: var(--shadow);
        }

        .archive-item:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-hover);
            border-color: var(--accent-blue);
        }

        .archive-item a {
            display: flex;
            align-items: center;
            padding: 1rem;
            text-decoration: none;
            color: var(--text-primary);
        }

        .archive-date {
            background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
            color: white;
            border-radius: 8px;
            padding: 0.75rem;
            margin-right: 1rem;
            text-align: center;
            min-width: 60px;
        }

        .archive-date .day {
            display: block;
            font-size: 1.8rem;
            font-weight: 700;
            line-height: 1;
        }

        .archive-date .month {
            display: block;
            font-size: 0.8rem;
            margin-top: 0.25rem;
            opacity: 0.9;
        }

        .archive-info h3 {
            font-size: 1rem;
            margin-bottom: 0.25rem;
        }

        .archive-meta {
            font-size: 0.8rem;
            color: var(--text-secondary);
        }

        footer {
            background: var(--bg-secondary);
            border-top: 2px solid var(--border-color);
            padding: 2rem 1rem;
            text-align: center;
            color: var(--text-secondary);
            margin-top: 3rem;
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
            margin-top: 0.5rem;
            opacity: 0.7;
        }

        @media (max-width: 768px) {
            .archive-grid {
                grid-template-columns: 1fr;
            }

            .archive-stats {
                flex-direction: column;
                gap: 1rem;
            }
        }
    </style>"""

    def _get_archive_javascript(self) -> str:
        """Get JavaScript for archive page"""
        return """    <script>
        // Dark mode support (sync with main page)
        if (localStorage.getItem('darkMode') === 'enabled') {
            document.body.classList.add('dark-mode');
        }
    </script>"""
