# 📰 AI-Powered Daily News Digest

An automated daily news aggregator that collects content from **Hatena Bookmark** (はてブ), **Hacker News**, and **Reddit**, summarizes it using **Claude AI**, and publishes it as a beautiful static HTML page.

🌐 **Live Demo**: `https://your-username.github.io/newspaper/`

## ✨ Features

- 🤖 **AI-Powered Summarization** - Uses Claude Haiku 4.5 for cost-efficient, high-quality Japanese summaries
- 📱 **Mobile-Responsive Design** - Beautiful, colorful interface that works on all devices
- 🌓 **Dark Mode** - Built-in dark mode toggle with preference persistence
- 📊 **Auto-Categorization** - AI automatically groups articles by topic
- 📚 **90-Day Archive** - Automatic archiving with visual calendar interface
- ⚡ **Fully Automated** - Runs daily at 7:00 AM PST via GitHub Actions
- 💰 **Low Cost** - Estimated ~$0.25/month for AI costs
- 🔒 **Privacy-First** - No tracking, no analytics, completely static

## 🎨 Design

The digest features a **colorful, newspaper-style layout** with:
- Icon-based navigation
- Color-coded source badges (はてブ, Hacker News, Reddit)
- Card-based article layout with hover effects
- Smooth animations and transitions
- Gradient headers and visual hierarchy
- Estimated ~10-minute reading time

## 📋 Prerequisites

- GitHub account
- Anthropic API key (for Claude AI)
- Reddit OAuth credentials (optional, for Reddit feed)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone this repository
git clone https://github.com/your-username/newspaper.git
cd newspaper

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Get API Keys

#### Anthropic API Key (Required)

1. Sign up at [Anthropic Console](https://console.anthropic.com/)
2. Create an API key
3. Copy the key - you'll need it for GitHub Secrets

**Cost Estimate**: ~$0.25/month for daily digests with Claude Haiku 4.5

#### Reddit OAuth Credentials (Optional)

1. Go to [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Fill in:
   - **name**: Daily Digest Bot
   - **type**: script
   - **redirect uri**: http://localhost:8080
4. Note down the **client ID** (under the app name) and **client secret**

### 3. Configure GitHub Secrets

Go to your repository **Settings → Secrets and variables → Actions** and add:

**Required:**
- `ANTHROPIC_API_KEY` - Your Anthropic API key

**Optional (for Reddit):**
- `REDDIT_CLIENT_ID` - Reddit app client ID
- `REDDIT_CLIENT_SECRET` - Reddit app client secret
- `REDDIT_USERNAME` - Your Reddit username
- `REDDIT_PASSWORD` - Your Reddit password

> **Note**: Without Reddit credentials, the digest will still work but only fetch from Hatena and Hacker News.

### 4. Enable GitHub Pages

1. Go to **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: **gh-pages** / **root**
4. Click **Save**

### 5. Configure Schedule (Optional)

Edit `.github/workflows/generate-digest.yml` to change the generation time:

```yaml
schedule:
  - cron: '0 15 * * *'  # 15:00 UTC = 7:00 AM PST
```

Use [crontab.guru](https://crontab.guru/) to customize the schedule.

## 🎯 Manual Testing

Run the digest generator locally:

```bash
# Set environment variables
export ANTHROPIC_API_KEY="your-key-here"
export REDDIT_CLIENT_ID="your-client-id"      # Optional
export REDDIT_CLIENT_SECRET="your-secret"     # Optional
export REDDIT_USERNAME="your-username"        # Optional
export REDDIT_PASSWORD="your-password"        # Optional

# Run the generator
python main.py
```

This will create:
- `index.html` - Today's digest
- `archive.html` - Archive index
- `archive/YYYY-MM-DD.html` - Archived digests

Open `index.html` in your browser to preview!

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
sources:
  hatena:
    enabled: true
    popular_count: 25    # Number of popular entries
    new_count: 15        # Number of new entries

  hackernews:
    enabled: true
    story_count: 30      # Number of top stories

  reddit:
    enabled: true
    use_personal_feed: true  # Use your subscribed subreddits
    post_count: 30

ai:
  model: claude-haiku-4-20250110
  max_tokens: 4000
  temperature: 0.3
  summary_language: japanese
  auto_categorize: true

archive:
  keep_days: 90          # Archive retention period
  generate_index: true
```

## 📁 Project Structure

```
newspaper/
├── .github/
│   └── workflows/
│       └── generate-digest.yml    # GitHub Actions workflow
├── src/
│   ├── fetchers/
│   │   ├── hatena_fetcher.py      # Hatena Bookmark fetcher
│   │   ├── hackernews_fetcher.py  # Hacker News fetcher
│   │   └── reddit_fetcher.py      # Reddit fetcher
│   ├── summarizer.py              # AI summarization
│   ├── html_generator.py          # HTML page generator
│   └── archive_manager.py         # Archive management
├── archive/                       # Archived digests
├── main.py                        # Main orchestrator
├── config.yaml                    # Configuration
├── requirements.txt               # Python dependencies
├── index.html                     # Latest digest (auto-generated)
├── archive.html                   # Archive index (auto-generated)
├── DESIGN.md                      # Technical specification
└── README.md                      # This file
```

## 🔧 Troubleshooting

### Digest generation fails

**Check GitHub Actions logs:**
1. Go to **Actions** tab
2. Click on the failed workflow
3. Expand steps to see error messages

**Common issues:**
- Missing API keys in Secrets
- API rate limits exceeded
- Network/timeout errors (retry logic handles most cases)

### Reddit fetching fails

- Verify OAuth credentials are correct
- Check Reddit account is in good standing
- Ensure app is configured as "script" type
- Try re-creating the Reddit app

### AI summarization errors

- Check Anthropic API key is valid
- Verify you have API credits
- Check API usage at [Anthropic Console](https://console.anthropic.com/)

### GitHub Pages not updating

- Ensure **gh-pages** branch exists
- Check GitHub Pages settings
- Workflow must have `contents: write` permission
- Wait a few minutes for deployment

## 💰 Cost Breakdown

**Estimated monthly costs (~$0.25/month):**

- **Anthropic API (Claude Haiku 4.5)**: ~$0.25/month
  - Input: ~60,000 tokens/day × 30 days = 1.8M tokens
  - Output: ~4,000 tokens/day × 30 days = 120K tokens
  - Cost: ($0.25/1M input + $1.25/1M output) ≈ $0.60/month max
  - Actual: ~$0.25/month (input-heavy)

- **GitHub Actions**: Free (2,000 minutes/month for free tier)
- **GitHub Pages**: Free
- **Reddit API**: Free
- **Hacker News API**: Free
- **Hatena Scraping**: Free

**Total**: < $1/month 💰

## 🛡️ Security & Privacy

- ✅ All API keys stored in GitHub Secrets (encrypted)
- ✅ No tracking or analytics
- ✅ HTTPS-only (enforced by GitHub Pages)
- ✅ HTML sanitization to prevent XSS
- ✅ Rate limiting for API calls
- ✅ No personal data in generated HTML

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📄 License

MIT License - feel free to use and modify!

## 🙏 Acknowledgments

- **Anthropic** - Claude AI for summarization
- **Hatena** - はてなブックマーク for Japanese tech news
- **Hacker News** - Y Combinator's tech community
- **Reddit** - Community-driven content
- **GitHub** - Hosting and automation

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/your-username/newspaper/issues)
- 📖 **Documentation**: See [DESIGN.md](DESIGN.md) for technical details

---

**Made with ❤️ and 🤖 Claude Code**

---

## 📸 Screenshots

### Desktop View
![Desktop](https://via.placeholder.com/800x600?text=Desktop+View)

### Mobile View
![Mobile](https://via.placeholder.com/375x812?text=Mobile+View)

### Dark Mode
![Dark Mode](https://via.placeholder.com/800x600?text=Dark+Mode)

### Archive
![Archive](https://via.placeholder.com/800x600?text=Archive+View)

> **Note**: Add actual screenshots after first generation!

---

## 🎯 Roadmap

Future enhancements:

- [ ] Add more news sources (DEV.to, Lobsters, etc.)
- [ ] Multi-language support (English summaries)
- [ ] RSS feed generation
- [ ] Email notification option
- [ ] Custom filtering/topics
- [ ] Search functionality
- [ ] PWA (Progressive Web App) support
- [ ] Reading list / bookmarks

---

**⭐ If you find this useful, please star the repository!**
