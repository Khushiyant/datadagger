# DataDagger - Influence Archaeology OSINT Tool

DataDagger is a command-line OSINT tool for mapping how ideas, narratives, and information spread through digital communities over time. It helps security researchers and analysts understand information flow patterns and identify potential threats.

## Important API Changes (2023)

⚠️ **Twitter API Update**: As of February 2023, Twitter no longer offers free API access. Basic tier starts at $100/month.

**Current Platform Support:**
- ✅ **Reddit** - Free API access available
- ⚠️ **Twitter** - Paid API required ($100+/month)
- 🆕 **Mastodon** - Free alternative to Twitter
- 🔮 **Future**: Planning support for Truth Social, Telegram, and other platforms

**Alternatives to Twitter:**
1. **Mastodon API** - Free, decentralized social network
2. **Web scraping** - Use with caution and respect robots.txt
3. **Academic access** - Some researchers may qualify for special access

## Features

- **Narrative Tracking**: Trace how specific ideas, memes, or narratives originated and evolved
- **Influence Mapping**: Map which accounts first pushed certain narratives
- **Cross-Platform Analysis**: Shows how information flows between different platforms
- **Timeline Visualization**: Create timeline visualizations showing idea evolution
- **Network Analysis**: Maps social networks of influence relationships
- **Content Evolution**: Track how stories change as they spread

## Quick Install

```bash
pip install datadagger
```

That's it! Skip to [Quick Start](#quick-start) if you want to try it immediately.

## Manual Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your environment variables (see `.env.example`)

## Quick Start

```bash
# Install DataDagger
pip install datadagger

# Try the demo (no setup required)
datadagger demo

# Check platform pricing and options
datadagger pricing

# Setup free APIs  
datadagger setup

# Search across free platforms
datadagger search "your topic" --platforms reddit,mastodon
```

## Usage

### Basic Commands

```bash
# Search for a narrative across free platforms
datadagger search "birds aren't real" --platforms reddit,mastodon --days 30

# Track narrative evolution (Reddit + Mastodon)  
datadagger track --query "covid lab leak" --start-date 2020-01-01 --end-date 2023-01-01

# Analyze influence networks
datadagger network --hashtag "#climatechange" --depth 3

# Generate timeline visualization
datadagger timeline --narrative "flat earth" --output timeline.html

# Export data for analysis
datadagger export --query "misinformation" --format csv --output data.csv
```

### Advanced Features

```bash
# Sentiment analysis over time
datadagger sentiment --query "vaccine" --platform mastodon --timeline

# Find patient zero of a narrative
datadagger origin --query "specific conspiracy theory" --threshold 0.8

# Cross-platform correlation analysis
datadagger correlate --query1 "narrative A" --query2 "narrative B"

# Use Twitter (if you have paid access)
datadagger search "breaking news" --platforms twitter --limit 100
```

## Configuration

Copy `.env.example` to `.env` and configure your API keys:

### Free Platforms (Recommended)

```bash
# Reddit API (Free)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret

# Mastodon API (Free) 
MASTODON_INSTANCE_URL=https://mastodon.social
MASTODON_ACCESS_TOKEN=your_token_here  # Optional for public data
```

### Paid Platforms

```bash  
# Twitter API (Paid - $100+/month since Feb 2023)
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
```

### API Cost Breakdown (as of 2025)

| Platform | Cost | Features | Recommendation |
|----------|------|----------|----------------|
| **Reddit** | FREE | Full API access | ✅ **Start here** |
| **Mastodon** | FREE | Decentralized, Twitter-like | ✅ **Great alternative** |
| **Twitter** | $100+/month | Official Twitter data | ⚠️ **Only if budget allows** |

### Getting API Keys

1. **Reddit (FREE)**: 
   - Go to https://www.reddit.com/prefs/apps/
   - Create a "script" application
   - Copy client ID and secret

2. **Mastodon (FREE)**:
   - Choose an instance (e.g., mastodon.social)
   - Create account → Preferences → Development
   - Create new application

3. **Twitter (PAID)**:
   - Go to https://developer.twitter.com/
   - Apply for API access
   - Choose Basic plan ($100/month) or higher

## Legal and Ethical Use

This tool is designed for:
- Security research and threat intelligence
- Academic research on information diffusion
- Journalism and fact-checking
- Understanding misinformation patterns

**Important**: Only use this tool on publicly available data and in compliance with platform terms of service and applicable laws.

## License

MIT License - See LICENSE file for details.
