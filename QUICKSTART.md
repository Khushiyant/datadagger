# DataDagger Quick Start Guide

## 🚀 Installation

1. **Clone and set up the project:**
   ```bash
   cd datadagger
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Or install manually:**
   ```bash
   pip3 install -r requirements.txt
   cp .env.example .env
   chmod +x datadagger.py
   ```

## 🔧 Configuration

1. **Check your configuration:**
   ```bash
   ./datadagger.py config
   ```

2. **Get API Keys (FREE options available):**
   - **Reddit (FREE):** https://www.reddit.com/prefs/apps/
     - You need: `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`
   - **Mastodon (FREE):** https://mastodon.social → Preferences → Development  
     - You need: `MASTODON_INSTANCE_URL` (and optionally `MASTODON_ACCESS_TOKEN`)
   - **Twitter (PAID - $100+/month):** https://developer.twitter.com/
     - You need: `TWITTER_BEARER_TOKEN` (only if you have paid access)

3. **Edit your .env file:**
   ```bash
   nano .env
   # Add your API keys
   ```

## 🎭 Try the Demo (No API Keys Required)

```bash
# Basic demo
./datadagger.py demo

# Full demo with timeline and network analysis
./datadagger.py demo --show-timeline --show-network

# Try different narratives
./datadagger.py demo --query flat_earth --show-timeline
```

## 🔍 Real Usage Examples

Once you have API keys configured:

```bash
# Search for a narrative (free platforms)
./datadagger.py search "birds aren't real" --platforms reddit,mastodon --days 7 --limit 50

# Search specific platforms  
./datadagger.py search "#climatechange" --platforms mastodon --days 30

# Track narrative evolution over time
./datadagger.py track --query "covid lab leak" --start-date 2020-01-01 --end-date 2023-01-01

# Export results
./datadagger.py search "vaccine conspiracy" --output results.json

# If you have Twitter paid access ($100+/month)
./datadagger.py search "breaking news" --platforms twitter --limit 100
```

## 📊 Available Commands

- `demo` - Run interactive demo with sample data
- `config` - Check API key configuration
- `search` - Search for narratives across platforms
- `track` - Track narrative evolution over time
- `network` - Analyze influence networks (coming soon)
- `timeline` - Generate timeline visualizations (coming soon)
- `sentiment` - Analyze sentiment trends (coming soon)
- `origin` - Find narrative origins (coming soon)
- `correlate` - Correlate different narratives (coming soon)
- `export` - Export data in various formats (coming soon)

## 🛡️ Legal and Ethical Use

**This tool is designed for:**
- Security research and threat intelligence
- Academic research on information diffusion
- Journalism and fact-checking
- Understanding misinformation patterns

**Important:** Only use on publicly available data and comply with platform terms of service and applicable laws.

## 🐛 Troubleshooting

1. **ImportError or ModuleNotFoundError:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **API Authentication Errors:**
   ```bash
   ./datadagger.py config  # Check your API keys
   ```

3. **No results found:**
   - Check your date ranges
   - Verify API keys are valid
   - Try broader search terms

## 📖 More Information

- See `README.md` for detailed documentation
- Run `./datadagger.py --help` for full command list
- Run `./datadagger.py COMMAND --help` for command-specific help
