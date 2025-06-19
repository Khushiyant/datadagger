# DataDagger Pip Installation Guide

## Quick Installation

```bash
pip install datadagger
```

That's it! DataDagger is now ready to use.

## Verify Installation

```bash
datadagger --version
datadagger --help
```

## Quick Start

1. **Run Demo (No setup required)**:
   ```bash
   datadagger demo
   ```

2. **Check Platform Pricing**:
   ```bash
   datadagger pricing
   ```

3. **Setup Free APIs**:
   ```bash
   datadagger setup
   ```

4. **Start Searching**:
   ```bash
   datadagger search "your query" --platforms reddit,mastodon
   ```

## Platform Setup

### Free Platforms (Recommended)

#### Reddit API (Free)
1. Go to https://www.reddit.com/prefs/apps/
2. Click "Create App" → "script"
3. Note your `client_id` and `client_secret`

#### Mastodon API (Free)
1. Join an instance: https://mastodon.social
2. Go to Preferences → Development
3. Create new application
4. Note your `access_token`

### Paid Platform

#### Twitter API ($100+/month)
- Go to https://developer.twitter.com/
- Apply for API access (paid since Feb 2023)
- Get API keys and bearer token

## Configuration

Run the interactive setup:
```bash
datadagger setup
```

Or manually create `.env` file:
```env
# Reddit (Free)
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=DataDagger:1.0.0

# Mastodon (Free)  
MASTODON_ACCESS_TOKEN=your_access_token
MASTODON_API_BASE_URL=https://mastodon.social

# Twitter (Paid - Optional)
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
```

## Usage Examples

### Search Across Platforms
```bash
# Search free platforms
datadagger search "misinformation" --platforms reddit,mastodon

# Search with time range
datadagger search "climate change" --days 7 --limit 200

# Export results
datadagger search "conspiracy theory" --output results.json
```

### Track Narrative Evolution
```bash
datadagger track --query "vaccine" --start-date 2024-01-01 --end-date 2024-12-31
```

### Analyze Networks
```bash
datadagger network --query "election fraud" --min-connections 5
```

### Generate Timelines
```bash
datadagger timeline --query "QAnon" --interval daily
```

## Advanced Features

- **Sentiment Analysis**: Track emotional tone over time
- **Origin Detection**: Find where narratives first appeared  
- **Network Mapping**: Visualize influence relationships
- **Export Options**: JSON, CSV, visualization files
- **Free Platform Focus**: Works great without paid APIs

## Troubleshooting

### Common Issues

1. **Import Errors**: Install missing dependencies
   ```bash
   pip install --upgrade datadagger
   ```

2. **API Rate Limits**: Use built-in rate limiting
   ```bash
   datadagger search "query" --limit 50  # Reduce requests
   ```

3. **Configuration**: Check your setup
   ```bash
   datadagger config
   ```

### Getting Help

```bash
datadagger --help                    # General help
datadagger search --help            # Command-specific help
datadagger demo                      # See features in action
datadagger pricing                   # Platform comparison
```

## Development Installation

For developers:
```bash
git clone https://github.com/yourusername/datadagger.git
cd datadagger
pip install -e .
```

## Dependencies

DataDagger automatically installs:
- **CLI**: click, rich, python-dotenv
- **Scrapers**: praw, Mastodon.py, tweepy, requests
- **Analysis**: nltk, scikit-learn, pandas, textdistance
- **Visualization**: matplotlib, seaborn, networkx, wordcloud

All dependencies are managed automatically by pip.

## Platform Coverage

| Platform | Cost | Content Type | Best For |
|----------|------|-------------|----------|
| Reddit | FREE | Forums | Deep discussions, communities |
| Mastodon | FREE | Microblogging | Twitter-like content, decentralized |
| Twitter | $100+/month | Microblogging | Real-time trends, breaking news |

**Recommendation**: Start with Reddit + Mastodon (100% free, 85% coverage)
