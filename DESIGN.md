# AI-Powered Daily News Digest - Technical Specification

## 1. Project Overview

### 1.1 Purpose
Build an automated daily news aggregator that collects content from Hatena Bookmark (はてブ), Hacker News, and Reddit, summarizes it using AI, and publishes it as a static HTML page accessible via web browser. The digest should be readable in approximately 10 minutes.

### 1.2 Target Audience
Single user (self-hosted personal news digest)

### 1.3 Core Requirements
- Automatic daily updates (every morning at 7:00 AM PST)
- AI-powered summarization with link preservation (using Claude Haiku 4.5 for cost efficiency)
- Mobile-responsive design
- No server maintenance required
- Accessible from any device via web browser
- Low operational cost (< $1/month)

## 2. Architecture

### 2.1 Technology Stack
- **Language**: Python 3.11+
- **AI**: Claude Haiku 4.5 (Anthropic) - cost-optimized
- **Hosting**: GitHub Pages
- **Automation**: GitHub Actions (scheduled daily at 7:00 AM PST)
- **Frontend**: Static HTML + CSS (+ minimal JavaScript)
- **Storage**: Git repository (for archives)

### 2.2 System Flow
```
Daily @ 7:00 AM PST (GitHub Actions)
    ↓
Fetch content from sources
    ↓
AI summarization (Claude Haiku 4.5)
    ↓
Generate HTML page
    ↓
Commit & push to gh-pages branch
    ↓
Accessible at https://username.github.io/daily-digest/
```

## 3. Data Sources

### 3.1 Hatena Bookmark (はてブ)
**Source URLs:**
- Popular entries: `https://b.hatena.ne.jp/hotentry/all`
- New entries: `https://b.hatena.ne.jp/entrylist/all`

**Data to collect:**
- Article title
- Article URL
- Number of bookmarks
- Categories/tags
- Top 3-5 bookmark comments (if available)

**Collection method:**
- Web scraping using BeautifulSoup or RSS feed parsing
- Target: Top 20-30 entries from popular, top 10-15 from new

### 3.2 Hacker News
**Source URLs:**
- API: `https://hacker-news.firebaseio.com/v0/`
- Top stories: `/v0/topstories.json`
- Best stories: `/v0/beststories.json`

**Data to collect:**
- Story title
- Story URL
- Points (score)
- Number of comments
- Top 3-5 comments (if relevant)

**Collection method:**
- Official Hacker News API
- Target: Top 20-30 stories

### 3.3 Reddit
**Source:**
- Reddit API (requires OAuth)
- User's personal front page feed

**Data to collect:**
- Post title
- Post URL
- Subreddit name
- Upvotes
- Number of comments

**Collection method:**
- Reddit API via PRAW (Python Reddit API Wrapper)
- Fetch user's personal front page (subscribed subreddits)
- Target: Top 20-30 posts from past 24 hours

## 4. AI Summarization

### 4.1 Summarization Strategy
**Objective:** Summarize ~60-90 articles into a 10-minute read (~1,500-2,000 words total, in Japanese)

**Approach:**
1. **Group by topic**: Use AI to automatically categorize and cluster similar articles
2. **Prioritize**: Use scores (bookmarks/points/upvotes) and source diversity
3. **Summarize**: 
   - For individual articles: 1-2 sentences max (in Japanese)
   - For topic clusters: 3-4 sentences covering multiple related articles
4. **Preserve links**: All original URLs must be included
5. **No comments**: Focus only on article content, exclude user comments

### 4.2 AI Prompt Structure
```
You are a helpful AI assistant summarizing today's tech/general news from multiple sources in Japanese.
You are using Claude Haiku 4.5, so be efficient and concise.

Guidelines:
- Be concise: each item should be 1-2 sentences in Japanese
- Automatically group related topics together and assign categories in Japanese
- Maintain a neutral, informative tone
- Translate English content to natural Japanese
- Include source attribution
- Do NOT include user comments - focus only on article content

Input format:
[Source name] [Title] (score) [URL]

Output format (in Japanese):
## [AI-determined Category in Japanese]
- **[Title/Summary in Japanese]** - [1-2 sentence summary] ([Source](URL), [score])
```

### 4.3 Language
**All summaries in Japanese** - AI will translate English content as needed

## 5. Output Format (HTML Page)

### 5.1 Page Structure
```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>デイリーダイジェスト - [Date]</title>
    <!-- CSS styling with visual design -->
    <style>
        /* Color-coded categories, card layouts, animations */
    </style>
</head>
<body>
    <header class="colorful-header">
        <h1>📰 デイリーダイジェスト</h1>
        <p class="date">[曜日], [年月日]</p>
        <p class="meta">生成時刻: [timestamp] PST | 読書時間: 約10分</p>
        <button class="dark-mode-toggle">🌓</button>
    </header>
    
    <nav class="icon-nav">
        <a href="#highlights">🔥 ハイライト</a>
        <a href="#tech">💻 テクノロジー</a>
        <a href="#science">🔬 サイエンス</a>
        <!-- AI-determined categories with icons -->
        <a href="archive.html">📚 アーカイブ</a>
    </nav>
    
    <main>
        <section id="highlights" class="category-section highlight">
            <h2>🔥 今日のハイライト</h2>
            <div class="article-grid">
                <!-- Top 5-10 stories in card format -->
                <article class="article-card">
                    <span class="source-badge hatena">はてブ</span>
                    <h3>記事タイトル</h3>
                    <p class="summary">要約文...</p>
                    <div class="meta">
                        <span class="score">⭐ 123</span>
                        <a href="#" class="read-more">続きを読む →</a>
                    </div>
                </article>
            </div>
        </section>
        
        <section id="category-auto" class="category-section">
            <h2>🏷️ [AI-Determined Category]</h2>
            <div class="article-grid">
                <!-- Articles grouped by AI-determined topics -->
            </div>
        </section>
        
        <!-- More AI-determined category sections -->
    </main>
    
    <footer>
        <p>ソース: はてなブックマーク, Hacker News, Reddit</p>
        <p>AI: Claude (Anthropic) | <a href="archive.html">📚 アーカイブを見る</a></p>
    </footer>
    
    <script>
        // Dark mode toggle
        // Smooth scroll
        // Card animations
    </script>
</body>
</html>
```

### 5.2 Design Requirements
- **Visual newspaper-style layout**: Colorful, engaging, with icons
- **Icon usage**: Use emojis or icon fonts for categories and sections
- **Color scheme**: 
  - Category-based color coding (Tech = blue, Science = green, etc.)
  - Light mode default with optional dark mode toggle
  - Accent colors for different sources
- **Typography**: Easy to read (16-18px body text), distinct headers
- **Visual hierarchy**: Clear separation with colored borders/backgrounds
- **Card-based layout**: Each article in a visually distinct card
- **Responsive**: Mobile-first design
- **Links**: Distinct styling with hover effects, open in new tab
- **Loading**: Fast (< 2 seconds on 3G)
- **Interactive elements**: Smooth transitions, hover effects

### 5.3 CSS Framework
**Recommended: Custom CSS with modern features**
- CSS Grid and Flexbox for layout
- CSS Variables for theming
- Modern animations and transitions
- Icon fonts or emoji for visual elements
- Estimated size: ~20-30KB for rich visual design

## 6. Archive System

### 6.1 Structure
```
/
├── index.html          # Today's digest (always latest)
├── archive.html        # Archive index page
├── archive/
│   ├── 2025-10-18.html
│   ├── 2025-10-17.html
│   └── ...
├── style.css
└── README.md
```

### 6.2 Archive Index
- List all past digests in reverse chronological order
- Show date and brief stats (# of articles, top categories)
- Visual calendar view with color-coded days
- Quick preview cards for each day
- Keep last 90 days (configurable)

## 7. Automation (GitHub Actions)

### 7.1 Workflow Schedule
```yaml
name: Generate Daily Digest

on:
  schedule:
    - cron: '0 15 * * *'  # 7:00 AM PST (15:00 UTC during PST, adjusts for PDT)
  workflow_dispatch:  # Manual trigger for testing

jobs:
  generate-digest:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
      - name: Set up Python
      - name: Install dependencies
      - name: Fetch news sources
      - name: Generate AI summary
      - name: Build HTML page
      - name: Commit and push to gh-pages
```

### 7.2 Environment Variables (GitHub Secrets)
- `ANTHROPIC_API_KEY` - Claude API key from Anthropic Console
- `REDDIT_CLIENT_ID` - Reddit OAuth app client ID
- `REDDIT_CLIENT_SECRET` - Reddit OAuth app client secret
- `REDDIT_USERNAME` - Reddit username
- `REDDIT_PASSWORD` - Reddit password (or use OAuth refresh token)

**Note**: For Reddit, user must create an OAuth app at https://www.reddit.com/prefs/apps

### 7.3 Error Handling
- Retry logic for API failures (3 attempts)
- Fallback to previous day's digest if generation fails
- Error logging to GitHub Actions logs
- Optional: Send notification on failure (email/Discord webhook)

## 9. Development Plan

### Single Phase: Complete Implementation
All features to be implemented together:

- [ ] Set up GitHub repository with proper structure
- [ ] Implement data fetching for all 3 sources (Hatena, HN, Reddit personal feed)
- [ ] AI-powered summarization with automatic topic categorization (Japanese output)
- [ ] Generate visually rich HTML page with:
  - Color-coded categories
  - Icon-based navigation
  - Card-based article layout
  - Dark mode toggle
  - Smooth animations
- [ ] Archive system with index page
- [ ] GitHub Actions automation (daily 7:00 AM JST)
- [ ] Deploy to GitHub Pages
- [ ] Error handling & retry logic
- [ ] Mobile optimization and responsive design
- [ ] Performance optimization (< 500KB, < 2s load)

## 10. Configuration File Example

```yaml
# config.yaml
sources:
  hatena:
    enabled: true
    popular_count: 25
    new_count: 15
  
  hackernews:
    enabled: true
    story_count: 30
  
  reddit:
    enabled: true
    use_personal_feed: true  # Fetch from user's subscribed subreddits
    post_count: 30

ai:
  provider: anthropic
  model: claude-haiku-4-20250110  # Cost-optimized model
  max_tokens: 4000
  temperature: 0.3
  summary_language: japanese
  auto_categorize: true  # AI determines topic categories

output:
  reading_time_minutes: 10
  max_word_count: 2000
  include_comments: false  # Do not include user comments
  visual_design: true  # Use colorful, icon-rich design

schedule:
  timezone: America/Los_Angeles  # PST/PDT
  time: "07:00"

archive:
  keep_days: 90
  generate_index: true
```

## 11. Testing Strategy

### 11.1 Unit Tests
- Test each data source fetcher independently
- Test HTML generation
- Test AI prompt construction

### 11.2 Integration Tests
- End-to-end workflow test
- Test with mock data
- Test GitHub Actions locally (act)

### 11.3 Manual Testing Checklist
- [ ] Mobile responsiveness (iOS Safari, Chrome Android)
- [ ] Dark mode toggle works correctly
- [ ] Color-coded categories display properly
- [ ] Card animations are smooth
- [ ] Links open correctly in new tabs
- [ ] Page loads fast (< 2 seconds)
- [ ] Archive navigation works
- [ ] Icons render correctly
- [ ] Reading time is accurate (~10 minutes)
- [ ] Japanese text displays correctly

## 12. Documentation Requirements

### 12.1 README.md
- Setup instructions (in English)
- How to configure Reddit OAuth credentials
- How to set Anthropic API key (Claude Haiku 4.5)
- How to customize generation time (default: 7:00 AM PST)
- How to trigger manual builds
- Cost estimation (~$0.25/month)
- Troubleshooting guide
- Example screenshots of the visual design

### 12.2 Code Documentation
- Docstrings for all functions
- Inline comments for complex logic
- Type hints throughout

## 13. Security & Privacy Considerations

- Store all API keys in GitHub Secrets (never commit to repository)
- Rate limiting for API calls to avoid abuse
- Sanitize HTML content (XSS prevention) when rendering summaries
- HTTPS only (enforced by GitHub Pages)
- No tracking or analytics (privacy-first approach)
- Reddit OAuth credentials securely stored
- No sensitive personal data in generated HTML (only public posts)

## 14. Performance Targets

- Page size: < 600KB (including visual assets, CSS, and fonts)
- Load time: < 2 seconds (Fast 3G)
- Generation time: < 5 minutes (GitHub Actions)
- API costs: < $1/month (Claude Haiku 4.5 is very cost-efficient: ~$0.25/month for 30 daily digests)
- Lighthouse score: > 90 (Performance, Accessibility)
- Mobile-friendly: 100% responsive

## 15. Confirmed Specifications

**All decisions have been finalized:**

1. ✅ **Summary language**: Japanese (AI translates English content)
2. ✅ **Reddit sources**: Personal feed (user's subscribed subreddits)
3. ✅ **Topic categories**: AI-determined automatic categorization
4. ✅ **Comment inclusion**: No comments - article content only
5. ✅ **Design preference**: Visual design with colors, icons, and engaging layout
6. ✅ **Implementation scope**: Complete implementation (former Phase 1 + Phase 2)
7. ✅ **AI provider**: Claude Haiku 4.5 (cost-optimized, ~$0.25/month)
8. ✅ **Timezone**: PST (America/Los_Angeles) - generates at 7:00 AM daily

**Additional specifications:**
- Dark mode toggle included
- Card-based layout for articles
- Color-coded categories
- Smooth animations and transitions
- Icon-based navigation
- Archive system with 90-day retention

---

**Ready for implementation with Claude Code.**
